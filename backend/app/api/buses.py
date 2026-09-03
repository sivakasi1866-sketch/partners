import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from backend.app.services.database import get_db, save_mock_db
from backend.app.api.deps import require_role, get_current_user

router = APIRouter()

@router.get("")
def get_buses():
    # Everyone authenticated can read buses
    db = get_db()
    return {"buses": db.buses}

@router.get("/{bus_id}")
def get_bus(bus_id: str):
    db = get_db()
    bus = next((b for b in db.buses if b.get("id") == bus_id), None)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return {"bus": bus}

@router.post("")
def create_bus(bus: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    bus_number = bus.get("busNumber")
    if not bus_number:
        raise HTTPException(status_code=400, detail="busNumber is required")
        
    if any(b.get("busNumber") == bus_number for b in db.buses):
        raise HTTPException(status_code=400, detail="Bus with this number already exists")
        
    bus["id"] = f"bus-{int(time.time()*1000)}"
    if "status" not in bus:
        bus["status"] = "idle"
        
    db.buses.append(bus)
    save_mock_db(db)
    return {"success": True, "bus": bus}

@router.patch("/{bus_id}")
def update_bus(bus_id: str, bus_data: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    bus = next((b for b in db.buses if b.get("id") == bus_id), None)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
        
    new_bus_number = bus_data.get("busNumber")
    if new_bus_number and new_bus_number != bus.get("busNumber"):
        if any(b.get("busNumber") == new_bus_number for b in db.buses):
            raise HTTPException(status_code=400, detail="Bus with this number already exists")
            
    bus.update(bus_data)
    save_mock_db(db)
    return {"success": True, "bus": bus}

@router.put("/{bus_id}")
def update_bus_put(bus_id: str, bus_data: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    return update_bus(bus_id, bus_data, current_user)

@router.delete("/{bus_id}")
def delete_bus(bus_id: str, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    # Check if bus is referenced by trips
    if any(t.get("busId") == bus_id for t in db.trips):
        raise HTTPException(status_code=400, detail="Cannot delete bus referenced by historical trips. Please deactivate it instead.")
        
    # Check if bus is referenced by assignments
    if any(d.get("assignedBusId") == bus_id for d in db.drivers):
        raise HTTPException(status_code=400, detail="Cannot delete bus assigned to a driver.")
        
    bus_idx = next((i for i, b in enumerate(db.buses) if b.get("id") == bus_id), -1)
    if bus_idx == -1:
        raise HTTPException(status_code=404, detail="Bus not found")
        
    removed = db.buses.pop(bus_idx)
    save_mock_db(db)
    return {"success": True, "removedBus": removed}
