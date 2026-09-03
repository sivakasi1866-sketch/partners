from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from backend.app.services.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.api.deps import get_current_user
from backend.app.core.config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    identifier: str
    password: str

class SwitchRoleRequest(BaseModel):
    userId: str
    role: str

@router.post("/login")
def login(req: LoginRequest):
    db = get_db()
    
    identifier = req.identifier
    if not identifier:
        raise HTTPException(status_code=400, detail="Missing login identifier")
        
    # Find user by studentId, staffId, or email
    user = next((u for u in db.users if 
                 u.get("studentId") == identifier or 
                 u.get("staffId") == identifier or 
                 u.get("email") == identifier), None)
                 
    if not user:
        if hasattr(db, 'drivers'):
            user = next((d for d in db.drivers if d.get("email") == identifier or d.get("staffId") == identifier), None)
            
    if not user:
        raise HTTPException(status_code=401, detail="Unable to sign in. Please check your User ID and password and try again.")
        
    if user.get("status") == "inactive":
        raise HTTPException(status_code=403, detail="User account is inactive")
        
    hashed_password = user.get("passwordHash")
    if not hashed_password:
        # Fallback for old records without passwordHash
        if req.password != "password123":
            raise HTTPException(status_code=401, detail="Unable to sign in. Please check your User ID and password and try again.")
    else:
        if not verify_password(req.password, hashed_password):
            raise HTTPException(status_code=401, detail="Unable to sign in. Please check your User ID and password and try again.")
            
    access_token = create_access_token(subject=user["id"], role=user.get("role", "student"))
    
    # Return user without password hash
    safe_user = user.copy()
    safe_user.pop("passwordHash", None)
    
    return {"access_token": access_token, "token_type": "bearer", "user": safe_user}

@router.get("/me")
def get_me(current_user: Dict = Depends(get_current_user)):
    db = get_db()
    # Mask password hashes in the list
    safe_users = []
    for u in db.users:
        su = u.copy()
        su.pop("passwordHash", None)
        safe_users.append(su)
        
    return {"user": current_user, "allAvailableUsers": safe_users}

@router.post("/switch-role")
def switch_role(req: SwitchRoleRequest):
    # This is purely for development/demo switching as requested
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=403, detail="Persona switching is disabled in production")
        
    db = get_db()
    target_user = next((u for u in db.users if u.get("id") == req.userId), None)
    if not target_user:
        if hasattr(db, 'drivers'):
            target_user = next((d for d in db.drivers if d.get("id") == req.userId), None)
            
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    access_token = create_access_token(subject=target_user["id"], role=target_user.get("role", "student"))
    safe_user = target_user.copy()
    safe_user.pop("passwordHash", None)
    return {"success": True, "access_token": access_token, "user": safe_user}

