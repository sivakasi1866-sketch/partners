import re
import os

with open('backend/app/api/trips.py', 'r') as f:
    code = f.read()

# 1. Add haversine function and math import
if 'import math' not in code:
    code = code.replace('import time', 'import time\nimport math')

haversine_func = """
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
"""

if 'def haversine' not in code:
    code = code.replace('router = APIRouter()\n', 'router = APIRouter()\n' + haversine_func + '\n')

# 2. Fix start trip validation
validation_checks = """
    if bus.get("status") in ["maintenance", "inactive", "out_of_service"]:
        raise HTTPException(status_code=400, detail="Bus is not available for a trip")

    active_driver_trip = next((t for t in db.trips if t.get("driverId") == driver["id"] and t.get("status") == "in_progress"), None)
    if active_driver_trip:
        raise HTTPException(status_code=400, detail="Driver already has an active trip")
        
    active_bus_trip = next((t for t in db.trips if t.get("busId") == req.busId and t.get("status") == "in_progress"), None)
    if active_bus_trip:
        raise HTTPException(status_code=400, detail="Bus already has an active trip")
"""
if 'active_driver_trip =' not in code:
    code = code.replace(
        'if not bus or not route:\n        raise HTTPException(status_code=404, detail="Bus or Route not found")',
        'if not bus or not route:\n        raise HTTPException(status_code=404, detail="Bus or Route not found")\n' + validation_checks
    )

# 3. Add Haversine stop detection in update_gps
stop_detection = """
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
                        import backend.app.services.database
                        backend.app.services.database.save_mock_db(db)
            except Exception as e:
                print("Error calculating haversine:", e)
"""
if '# Haversine stop detection' not in code:
    code = code.replace(
        'trip["lastLocationUpdateTime"] = incoming_timestamp\n        \n        # Distance approximation',
        'trip["lastLocationUpdateTime"] = incoming_timestamp\n' + stop_detection + '\n        # Distance approximation'
    )

with open('backend/app/api/trips.py', 'w') as f:
    f.write(code)

print("Patch applied")
