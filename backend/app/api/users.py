from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from backend.app.services.database import get_db
from backend.app.api.deps import require_role, get_current_user
from backend.app.core.security import get_password_hash
import time
from datetime import datetime

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str
    studentId: Optional[str] = None
    staffId: Optional[str] = None
    department: Optional[str] = None
    # Driver specific
    phone: Optional[str] = None
    driverLicense: Optional[str] = None
    assignedBusId: Optional[str] = None
    assignedRouteId: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    studentId: Optional[str] = None
    staffId: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    driverLicense: Optional[str] = None

class RoleUpdate(BaseModel):
    role: str

class StatusUpdate(BaseModel):
    status: str

def safe_user(user: dict) -> dict:
    u = user.copy()
    u.pop("passwordHash", None)
    return u

@router.get("/users")
def get_users(current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    return {"users": [safe_user(u) for u in db.users]}

@router.get("/drivers")
def get_drivers():
    db = get_db()
    # We strip password hash just in case
    return {"drivers": [safe_user(d) for d in db.drivers]}

@router.get("/users/{user_id}")
def get_user(user_id: str, current_user: Dict = Depends(get_current_user)):
    db = get_db()
    if current_user.get("role") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    user = next((u for u in db.users if u.get("id") == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": safe_user(user)}

@router.post("/users")
def create_user(req: UserCreate, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    if any(u.get("email") == req.email for u in db.users):
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    if req.role not in ["student", "staff", "driver", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    user_id = f"usr-{req.role}-{int(time.time()*1000)}"
    new_user = {
        "id": user_id,
        "name": req.name,
        "email": req.email,
        "role": req.role,
        "status": "active",
        "passwordHash": get_password_hash(req.password),
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }
    if req.studentId: new_user["studentId"] = req.studentId
    if req.staffId: new_user["staffId"] = req.staffId
    if req.department:
        new_user["department"] = req.department
        
    if req.role == "driver":
        if req.phone: new_user["phone"] = req.phone
        if req.driverLicense: new_user["driverLicense"] = req.driverLicense
        if req.assignedBusId: new_user["assignedBusId"] = req.assignedBusId
        if req.assignedRouteId: new_user["assignedRouteId"] = req.assignedRouteId
        
        # Add to drivers array as well to preserve compatibility
        driver_entry = new_user.copy()
        driver_entry["experienceYears"] = 0
        driver_entry["rating"] = 5.0
        db.drivers.append(driver_entry)
        
    db.users.append(new_user)
    
    with open("server/data/mock_db.json", "w") as f:
        import json
        json.dump({"users": db.users, "drivers": db.drivers, "buses": db.buses, "routes": db.routes, "systemLogs": db.system_logs, "notifications": db.notifications}, f, indent=2)
        
    return {"success": True, "user": safe_user(new_user)}

@router.patch("/users/{user_id}")
def update_user(user_id: str, req: UserUpdate, current_user: Dict = Depends(get_current_user)):
    db = get_db()
    if current_user.get("role") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        
    user = next((u for u in db.users if u.get("id") == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check email duplicate if changed
    if req.email and req.email != user.get("email"):
        if any(u.get("email") == req.email for u in db.users):
            raise HTTPException(status_code=400, detail="Email already in use")
        user["email"] = req.email
        
    if req.name: user["name"] = req.name
    if req.studentId: user["studentId"] = req.studentId
    if req.staffId: user["staffId"] = req.staffId
    if req.department: user["department"] = req.department
    
    if user.get("role") == "driver":
        if req.phone: user["phone"] = req.phone
        if req.driverLicense: user["driverLicense"] = req.driverLicense
        # Update driver array
        driver = next((d for d in db.drivers if d.get("id") == user_id), None)
        if driver:
            if req.name: driver["name"] = req.name
            if req.email: driver["email"] = req.email
            if req.phone: driver["phone"] = req.phone
            if req.driverLicense: driver["driverLicense"] = req.driverLicense
            
    with open("server/data/mock_db.json", "w") as f:
        import json
        json.dump({"users": db.users, "drivers": db.drivers, "buses": db.buses, "routes": db.routes, "systemLogs": db.system_logs, "notifications": db.notifications}, f, indent=2)
        
    return {"success": True, "user": safe_user(user)}

@router.patch("/users/{user_id}/role")
def update_user_role(user_id: str, req: RoleUpdate, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    user = next((u for u in db.users if u.get("id") == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if req.role not in ["student", "staff", "driver", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    user["role"] = req.role
    # If they became a driver, maybe add to drivers array? For simplicity, we just update it.
    if req.role == "driver":
        existing = next((d for d in db.drivers if d.get("id") == user_id), None)
        if not existing:
            driver_entry = user.copy()
            driver_entry["experienceYears"] = 0
            driver_entry["rating"] = 5.0
            db.drivers.append(driver_entry)
            
    with open("server/data/mock_db.json", "w") as f:
        import json
        json.dump({"users": db.users, "drivers": db.drivers, "buses": db.buses, "routes": db.routes, "systemLogs": db.system_logs, "notifications": db.notifications}, f, indent=2)
        
    return {"success": True, "user": safe_user(user)}

@router.patch("/users/{user_id}/status")
def update_user_status(user_id: str, req: StatusUpdate, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    user = next((u for u in db.users if u.get("id") == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if req.status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    user["status"] = req.status
    
    # Update driver array
    driver = next((d for d in db.drivers if d.get("id") == user_id), None)
    if driver:
        driver["status"] = req.status
        
    with open("server/data/mock_db.json", "w") as f:
        import json
        json.dump({"users": db.users, "drivers": db.drivers, "buses": db.buses, "routes": db.routes, "systemLogs": db.system_logs, "notifications": db.notifications}, f, indent=2)
        
    return {"success": True, "user": safe_user(user)}

@router.delete("/users/{user_id}")
def delete_user(user_id: str, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    user_idx = next((i for i, u in enumerate(db.users) if u.get("id") == user_id), -1)
    if user_idx == -1:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = db.users[user_idx]
    
    # Check references
    if user.get("role") == "driver":
        active_trip = next((t for t in db.trips if t.get("driverId") == user_id and t.get("status") == "in_progress"), None)
        if active_trip:
            raise HTTPException(status_code=400, detail="Cannot delete driver while on an active trip")
        # Remove from drivers array
        driver_idx = next((i for i, d in enumerate(db.drivers) if d.get("id") == user_id), -1)
        if driver_idx != -1:
            db.drivers.pop(driver_idx)
    
    removed = db.users.pop(user_idx)
    
    with open("server/data/mock_db.json", "w") as f:
        import json
        json.dump({"users": db.users, "drivers": db.drivers, "buses": db.buses, "routes": db.routes, "systemLogs": getattr(db, "system_logs", []), "notifications": getattr(db, "notifications", [])}, f, indent=2)
    
    return {"success": True, "removedUser": safe_user(removed)}
