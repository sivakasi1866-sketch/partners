from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from backend.app.services.database import get_db, save_mock_db
from backend.app.api.deps import get_current_user, require_role

router = APIRouter()

class AssignmentReq(BaseModel):
    driverId: str
    busId: str
    routeId: str

@router.get("/")
def get_assignments(current_user: Dict = Depends(get_current_user)):
    db = get_db()
    
    if current_user.get("role") == "driver":
        drivers = [d for d in db.drivers if d.get("id") == current_user.get("id")]
    elif current_user.get("role") in ["admin", "staff", "student"]:
        # Allow reading all assignments for operational visibility, but maybe restrict sensitive info?
        # The prompt says: "Student/Staff -> only permitted operational information"
        # Since this returns driverId, busId, routeId, it's safe operational info.
        drivers = [d for d in db.drivers if d.get("assignedBusId")]
    else:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    assignments = []
    for d in drivers:
        if d.get("assignedBusId") and d.get("assignedRouteId"):
            assignments.append({
                "driverId": d.get("id"),
                "driverName": d.get("name"),
                "busId": d.get("assignedBusId"),
                "routeId": d.get("assignedRouteId")
            })
    return {"assignments": assignments}

@router.post("/")
def create_assignment(req: AssignmentReq, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    driver = next((d for d in db.drivers if d.get("id") == req.driverId), None)
    if not driver:
        raise HTTPException(status_code=400, detail="Driver not found")
        
    user = next((u for u in db.users if u.get("id") == req.driverId), None)
    if user and user.get("status") != "active":
        raise HTTPException(status_code=400, detail="Driver is not active")
    if user and user.get("role") != "driver":
        raise HTTPException(status_code=400, detail="User is not a driver")
        
    bus = next((b for b in db.buses if b.get("id") == req.busId), None)
    if not bus:
        raise HTTPException(status_code=400, detail="Bus not found")
    if bus.get("status") in ["maintenance", "inactive", "out_of_service"]:
        raise HTTPException(status_code=400, detail="Bus is not available for assignment")
        
    route = next((r for r in db.routes if r.get("id") == req.routeId), None)
    if not route:
        raise HTTPException(status_code=400, detail="Route not found")
    # if route has status, verify it
    if route.get("status") == "inactive":
        raise HTTPException(status_code=400, detail="Route is inactive")
        
    # Check if driver has active trip
    active_driver_trip = next((t for t in db.trips if t.get("driverId") == req.driverId and t.get("status") == "in_progress"), None)
    if active_driver_trip:
        raise HTTPException(status_code=400, detail="Driver has an active trip")

    # Check if bus has active trip
    active_bus_trip = next((t for t in db.trips if t.get("busId") == req.busId and t.get("status") == "in_progress"), None)
    if active_bus_trip:
        raise HTTPException(status_code=400, detail="Bus has an active trip")
        
    # Check if bus is already assigned to someone else
    other_driver = next((d for d in db.drivers if d.get("assignedBusId") == req.busId and d.get("id") != req.driverId), None)
    if other_driver:
        raise HTTPException(status_code=400, detail="Bus is already assigned to another driver")
        
    # Prevent duplicate assignments silently overriding?
    # If the exact assignment exists, we can just return success
    if driver.get("assignedBusId") == req.busId and driver.get("assignedRouteId") == req.routeId:
        return {"success": True, "assignment": {"driverId": driver["id"], "busId": driver["assignedBusId"], "routeId": driver["assignedRouteId"]}, "message": "Assignment already exists"}

    driver["assignedBusId"] = req.busId
    driver["assignedRouteId"] = req.routeId
    
    if user:
        user["assignedBusId"] = req.busId
        user["assignedRouteId"] = req.routeId
        
    save_mock_db(db)
    
    return {"success": True, "assignment": {"driverId": driver["id"], "busId": driver["assignedBusId"], "routeId": driver["assignedRouteId"]}}

@router.delete("/{driver_id}")
def remove_assignment(driver_id: str, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    driver = next((d for d in db.drivers if d.get("id") == driver_id), None)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
        
    active_driver_trip = next((t for t in db.trips if t.get("driverId") == driver_id and t.get("status") == "in_progress"), None)
    if active_driver_trip:
        raise HTTPException(status_code=400, detail="Cannot remove assignment during active trip")

    if "assignedBusId" in driver:
        del driver["assignedBusId"]
    if "assignedRouteId" in driver:
        del driver["assignedRouteId"]
    
    user = next((u for u in db.users if u.get("id") == driver_id), None)
    if user:
        if "assignedBusId" in user:
            del user["assignedBusId"]
        if "assignedRouteId" in user:
            del user["assignedRouteId"]

    save_mock_db(db)

    return {"success": True}
