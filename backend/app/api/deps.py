from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from typing import Optional, Dict

from backend.app.core.config import settings
from backend.app.services.database import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False
)

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    db = get_db()
    # Check regular users
    user = next((u for u in db.users if u.get("id") == user_id), None)
    if not user:
        # Check drivers list just in case they are separated
        if hasattr(db, 'drivers'):
            user = next((d for d in db.drivers if d.get("id") == user_id), None)
            
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker
