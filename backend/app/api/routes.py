import time
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from backend.app.services.database import get_db, save_mock_db
from backend.app.api.deps import require_role, get_current_user

router = APIRouter()

@router.get("")
def get_routes():
    db = get_db()
    return {"routes": db.routes}

@router.get("/{route_id}")
def get_route(route_id: str):
    db = get_db()
    route = next((r for r in db.routes if r.get("id") == route_id), None)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return {"route": route}

@router.post("")
def create_route(route: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    route_name = route.get("name")
    if not route_name:
        raise HTTPException(status_code=400, detail="Route name is required")
        
    if any(r.get("name") == route_name for r in db.routes):
        raise HTTPException(status_code=400, detail="Route with this name already exists")
        
    route["id"] = f"route-{int(time.time()*1000)}"
    if "stops" not in route:
        route["stops"] = []
        
    db.routes.append(route)
    save_mock_db(db)
    return {"success": True, "route": route}

@router.patch("/{route_id}")
def update_route(route_id: str, route_data: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    route = next((r for r in db.routes if r.get("id") == route_id), None)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    new_route_name = route_data.get("name")
    if new_route_name and new_route_name != route.get("name"):
        if any(r.get("name") == new_route_name for r in db.routes):
            raise HTTPException(status_code=400, detail="Route with this name already exists")
            
    # Protect stops from being wiped out by a naive patch
    if "stops" in route_data:
        # Actually, let's allow updating stops if they pass validation
        pass
        
    route.update(route_data)
    save_mock_db(db)
    return {"success": True, "route": route}

@router.delete("/{route_id}")
def delete_route(route_id: str, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    # Check if route is referenced by trips
    if any(t.get("routeId") == route_id for t in db.trips):
        raise HTTPException(status_code=400, detail="Cannot delete route referenced by historical trips. Please deactivate it instead.")
        
    # Check if route is referenced by assignments
    if any(d.get("assignedRouteId") == route_id for d in db.drivers):
        raise HTTPException(status_code=400, detail="Cannot delete route assigned to a driver.")
        
    route_idx = next((i for i, r in enumerate(db.routes) if r.get("id") == route_id), -1)
    if route_idx == -1:
        raise HTTPException(status_code=404, detail="Route not found")
        
    removed = db.routes.pop(route_idx)
    save_mock_db(db)
    return {"success": True, "removedRoute": removed}


# --- STOPS ---

@router.get("/{route_id}/stops")
def get_stops(route_id: str):
    db = get_db()
    route = next((r for r in db.routes if r.get("id") == route_id), None)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return {"stops": route.get("stops", [])}

@router.post("/{route_id}/stops")
def create_stop(route_id: str, stop: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    route = next((r for r in db.routes if r.get("id") == route_id), None)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    if "name" not in stop or "latitude" not in stop or "longitude" not in stop:
        raise HTTPException(status_code=400, detail="Stop name, latitude, and longitude are required")
        
    lat = stop["latitude"]
    lon = stop["longitude"]
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid coordinates")
        
    if "stops" not in route:
        route["stops"] = []
        
    stop["id"] = f"stop-{int(time.time()*1000)}-{len(route['stops'])}"
    
    # Handle sequence
    if "sequence" not in stop:
        stop["sequence"] = len(route["stops"]) + 1
        
    route["stops"].append(stop)
    # Sort stops by sequence
    route["stops"] = sorted(route["stops"], key=lambda s: s.get("sequence", 999))
    
    save_mock_db(db)
    return {"success": True, "stop": stop}

@router.patch("/{route_id}/stops/{stop_id}")
def update_stop(route_id: str, stop_id: str, stop_data: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    route = next((r for r in db.routes if r.get("id") == route_id), None)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    stops = route.get("stops", [])
    stop = next((s for s in stops if s.get("id") == stop_id), None)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
        
    if "latitude" in stop_data or "longitude" in stop_data:
        lat = stop_data.get("latitude", stop["latitude"])
        lon = stop_data.get("longitude", stop["longitude"])
        try:
            lat = float(lat)
            lon = float(lon)
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid coordinates")
            
    stop.update(stop_data)
    
    if "sequence" in stop_data:
        route["stops"] = sorted(route["stops"], key=lambda s: s.get("sequence", 999))
        
    save_mock_db(db)
    return {"success": True, "stop": stop}

@router.delete("/{route_id}/stops/{stop_id}")
def delete_stop(route_id: str, stop_id: str, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    route = next((r for r in db.routes if r.get("id") == route_id), None)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    stops = route.get("stops", [])
    stop_idx = next((i for i, s in enumerate(stops) if s.get("id") == stop_id), -1)
    if stop_idx == -1:
        raise HTTPException(status_code=404, detail="Stop not found")
        
    removed = stops.pop(stop_idx)
    save_mock_db(db)
    return {"success": True, "removedStop": removed}

