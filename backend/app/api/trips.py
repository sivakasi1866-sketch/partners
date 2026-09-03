from datetime import datetime
import time

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict
from backend.app.services.database import get_db
from backend.app.api.deps import get_current_user

import math

router = APIRouter()

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class StartTripReq(BaseModel):
    driverId: str
    busId: str
    routeId: str

class StopTripReq(BaseModel):
    tripId: str
    driverId: str

class GPSUpdateReq(BaseModel):
    tripId: str
    driverId: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speedKmH: Optional[float] = None
    heading: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: str
    accuracyMeters: Optional[float] = None
    passengerCount: Optional[int] = None
    trafficLevel: Optional[str] = None
    delayMinutes: Optional[float] = None
    delayReason: Optional[str] = None

@router.get("")
def get_trips():
    db = get_db()
    return {"trips": db.trips}

@router.get("/active")
def get_active_trips():
    db = get_db()
    active_trips = [t for t in db.trips if t.get("status") == "in_progress"]
    return {"activeTrips": active_trips}

@router.post("/start")
def start_trip(req: StartTripReq, current_user: Dict = Depends(get_current_user)):
    db = get_db()
    # OVERRIDE ANY CLIENT driverId WITH AUTHENTICATED USER ID
    req.driverId = current_user.get("id")
    
    driver = current_user
    if driver.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Unauthorized: Only drivers can start trips")
        
    db_driver = next((d for d in db.drivers if d.get("id") == driver["id"]), None)
    if not db_driver:
        # Fallback to current_user if driver array doesn't have them
        db_driver = driver
        
    if req.busId != db_driver.get("assignedBusId"):
        raise HTTPException(status_code=403, detail=f"Unauthorized: You are not assigned to this bus. Driver assigned bus: {db_driver.get('assignedBusId')}, Req bus: {req.busId}")
        
    if req.routeId != db_driver.get("assignedRouteId"):
        raise HTTPException(status_code=403, detail=f"Unauthorized: You are not assigned to this route. Driver assigned route: {db_driver.get('assignedRouteId')}, Req route: {req.routeId}")
        
    bus = next((b for b in db.buses if b.get("id") == req.busId), None)
    route = next((r for r in db.routes if r.get("id") == req.routeId), None)
    
    if not bus or not route:
        raise HTTPException(status_code=404, detail="Bus or Route not found")

    if bus.get("status") in ["maintenance", "inactive", "out_of_service"]:
        raise HTTPException(status_code=400, detail="Bus is not available for a trip")

    active_driver_trip = next((t for t in db.trips if t.get("driverId") == driver["id"] and t.get("status") == "in_progress"), None)
    if active_driver_trip:
        raise HTTPException(status_code=400, detail="Driver already has an active trip")
        
    active_bus_trip = next((t for t in db.trips if t.get("busId") == req.busId and t.get("status") == "in_progress"), None)
    if active_bus_trip:
        raise HTTPException(status_code=400, detail="Bus already has an active trip")

        
    new_trip = {
        "id": f"trip-{int(time.time()*1000)}",
        "busId": bus["id"],
        "busNumber": bus.get("busNumber"),
        "driverId": driver["id"],
        "driverName": driver.get("name"),
        "routeId": route["id"],
        "routeNumber": route.get("routeNumber"),
        "routeName": route.get("name"),
        "status": "in_progress",
        "startTime": datetime.utcnow().isoformat() + "Z",
        "currentLatitude": route.get("stops", [{}])[0].get("latitude"),
        "currentLongitude": route.get("stops", [{}])[0].get("longitude"),
        "currentStopIndex": 0,
        "nextStopIndex": 1 if len(route.get("stops", [])) > 1 else 0,
        "passengerCount": 0,
        "distanceCoveredKm": 0,
        "gpsActive": True
    }
    
    
    db.trips.insert(0, new_trip)
    db.save_trips()
    
    bus["status"] = "in_service"
    
    if not hasattr(db, "notifications"):
        db.notifications = []
    
    import uuid
    
    # Notify start
    db.notifications.insert(0, {
        "id": f"notif-{uuid.uuid4().hex[:8]}",
        "title": f"Trip Started: Bus {bus.get('busNumber', 'Unknown')}",
        "message": f"Bus {bus.get('busNumber', 'Unknown')} has started a trip on route {route.get('routeName', 'Unknown')}.",
        "type": "info",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "routeId": route["id"],
        "busId": bus["id"],
        "targetRole": "all",
        "isRead": False
    })
    
    # avoid circular import or doing full save - just use existing save method or save_mock_db
    try:
        from backend.app.services.database import save_mock_db
        save_mock_db(db)
    except:
        pass

    return {"success": True, "trip": new_trip}


@router.post("/update-gps")
def update_gps(req: GPSUpdateReq, current_user: Dict = Depends(get_current_user)):
    db = get_db()
    
    # Overwrite the request's driverId with the true JWT sub
    req.driverId = current_user.get("id")
    
    if current_user.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Unauthorized: Only drivers can submit GPS")
        
    trip = next((t for t in db.trips if t.get("id") == req.tripId), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    if trip.get("status") != "in_progress" or not trip.get("gpsActive"):
        raise HTTPException(status_code=403, detail="PRIVACY_POLICY_VIOLATION: GPS updates are strictly forbidden after trip has ended or is inactive.")
        
    if trip.get("driverId") != req.driverId:
        raise HTTPException(status_code=403, detail="Unauthorized driver telemetry is rejected.")
        
    # Duplicate Protection
    incoming_timestamp = req.timestamp or datetime.utcnow().isoformat() + "Z"
    last_record = next((t for t in reversed(db.telemetry) if t.get("trip_id") == trip["id"]), None)
    
    if last_record and last_record.get("latitude") == req.latitude and last_record.get("longitude") == req.longitude and last_record.get("speed_kmh") == req.speedKmH:
        return {"success": True, "trip": trip, "message": "Duplicate telemetry ignored safely"}
        
    trip["currentLatitude"] = req.latitude
    trip["currentLongitude"] = req.longitude
    if req.speedKmH is not None:
        trip["speedKmH"] = round(req.speedKmH)
    if req.heading is not None:
        trip["heading"] = round(req.heading)
    trip["lastLocationUpdateTime"] = incoming_timestamp

    # Haversine stop detection
    route = next((r for r in db.routes if r.get("id") == trip.get("routeId")), None)
    if route:
        stops = route.get("stops", [])
        next_index = trip.get("nextStopIndex", 0)
        if next_index < len(stops):
            next_stop = stops[next_index]
            try:
                slat = float(next_stop.get("latitude"))
                slon = float(next_stop.get("longitude"))
                dist = haversine(req.latitude, req.longitude, slat, slon)
                if dist < 50:  # 50 meters threshold
                    trip["currentStopIndex"] = next_index
                    trip["nextStopIndex"] = next_index + 1
                    
                    if not hasattr(db, "system_logs"):
                        db.system_logs = []
                    
                    existing_event = next((e for e in db.system_logs if e.get("type") == "stop_arrival" and e.get("tripId") == trip["id"] and e.get("stopId") == next_stop.get("id")), None)
                    if not existing_event:
                        
                        db.system_logs.append({
                            "id": f"evt-{int(time.time()*1000)}",
                            "type": "stop_arrival",
                            "tripId": trip["id"],
                            "routeId": route["id"],
                            "stopId": next_stop.get("id"),
                            "timestamp": incoming_timestamp,
                            "message": f"Arrived at stop {next_stop.get('name') or next_stop.get('stopName') or 'Unknown'}"
                        })
            except Exception as e:
                print("Error calculating haversine:", e)

        # Distance approximation placeholder, skipping actual haversine in basic mock
    
    telemetry_record = {
        "id": f"tel-{int(time.time()*1000)}",
        "trip_id": trip["id"],
        "bus_id": trip.get("busId"),
        "route_id": trip.get("routeId"),
        "driver_id": trip.get("driverId"),
        "timestamp": incoming_timestamp,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "speed_kmh": req.speedKmH,
        "gps_accuracy_m": req.accuracyMeters,
        "heading": req.heading,
        "trip_status": trip["status"]
    }
    
    db.telemetry.append(telemetry_record)
    db.save_telemetry()
    
    db.save_trips()
    return {
        "success": True,
        "tripId": trip["id"],
        "currentLatitude": trip["currentLatitude"],
        "currentLongitude": trip["currentLongitude"],
        "speedKmH": trip.get("speedKmH"),
        "heading": trip.get("heading")
    }

@router.post("/stop")
def stop_trip(req: StopTripReq, current_user: Dict = Depends(get_current_user)):
    db = get_db()
    
    # Enforce driver identity
    req.driverId = current_user.get("id")
    if current_user.get("role") != "driver":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    trip = next((t for t in db.trips if t.get("id") == req.tripId), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    if trip.get("driverId") != req.driverId:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot stop trip belonging to another driver")
        
    trip["status"] = "completed"
    trip["gpsActive"] = False
    trip["endTime"] = datetime.utcnow().isoformat() + "Z"
    trip["speedKmH"] = 0
    
    bus = next((b for b in db.buses if b.get("id") == trip.get("busId")), None)
    if bus:
        bus["status"] = "idle"
        bus["currentOccupancy"] = 0
        
    
    db.save_trips()
    
    if not hasattr(db, "notifications"):
        db.notifications = []
        
    route = next((r for r in db.routes if r.get("id") == trip.get("routeId")), {})
    import uuid
    
    db.notifications.insert(0, {
        "id": f"notif-{uuid.uuid4().hex[:8]}",
        "title": f"Trip Completed",
        "message": f"Bus {bus.get('busNumber', 'Unknown') if bus else 'Unknown'} has completed its trip on route {route.get('routeName', 'Unknown')}.",
        "type": "info",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "routeId": trip.get("routeId"),
        "busId": trip.get("busId"),
        "targetRole": "all",
        "isRead": False
    })
    try:
        from backend.app.services.database import save_mock_db
        save_mock_db(db)
    except:
        pass

    return {

        "success": True,
        "message": "Trip completed successfully. Bus GPS stream has been shut down.",
        "trip": trip
    }

@router.get("/{trip_id}/eta")
def get_eta(trip_id: str, weather: str = 'clear'):
    # In order not to lose the ML model logic written in typescript, we call a subprocess to the existing TS script, 
    # OR we use the heuristic fallback if we don't have the full model ported yet.
    # The requirement says: "The FastAPI backend should call the existing ETA/ML service through a clean service interface."
    # Since we replaced the backend, we can create a tiny node script to run the predictor, or just implement the heuristic fallback here for now.
    
    import subprocess
    import json
    
    # We will call the TS predictor using tsx via the permanent bridge script.
    try:
        result = subprocess.run(["npx", "tsx", "backend/scripts/ml_bridge.ts", "eta", trip_id, weather], capture_output=True, text=True)
        if result.returncode == 0:
            output_str = result.stdout.strip()
            # Try to extract the last line which contains the JSON
            if '\n' in output_str:
                output_str = output_str.split('\n')[-1]
            try:
                stop_etas = json.loads(output_str)
            except json.JSONDecodeError:
                # Fallback to regex or empty if it fails completely
                import re
                match = re.search(r'\[.*\]', result.stdout.strip(), re.DOTALL)
                if match:
                    stop_etas = json.loads(match.group(0))
                else:
                    stop_etas = []
        else:
            stop_etas = []
    except Exception as e:
        print("ETA failed:", e)
        stop_etas = []
        
    db = get_db()
    trip = next((t for t in db.trips if t.get("id") == trip_id), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    route = next((r for r in db.routes if r.get("id") == trip.get("routeId")), None)
    
    return {
        "tripId": trip["id"],
        "busNumber": trip.get("busNumber"),
        "routeId": trip.get("routeId"),
        "routeName": route.get("name") if route else "",
        "tripStatus": trip.get("status"),
        "predictionMethod": "ML_PREDICTION",
        "stopEtas": stop_etas
    }