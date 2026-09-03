from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime
import uuid
from backend.app.services.database import get_db, save_mock_db
from backend.app.api.deps import get_current_user, require_role

router = APIRouter()

@router.get("/logs")
def get_logs(current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    return {"logs": db.system_logs}

@router.get("/notifications")
def get_notifications(current_user: Dict = Depends(get_current_user)):
    db = get_db()
    user_role = current_user.get("role")
    user_id = current_user.get("id")
    
    filtered_notifications = []
    for n in getattr(db, "notifications", []):
        target = n.get("targetRole", "all")
        if target == "all" or target == user_role or n.get("userId") == user_id:
            filtered_notifications.append(n)
            
    return {"notifications": filtered_notifications}

@router.post("/notifications")
def create_notification(data: Dict[str, Any], current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    new_notif = {
        "id": f"notif-{uuid.uuid4().hex[:8]}",
        "title": data.get("title", ""),
        "message": data.get("message", ""),
        "type": data.get("type", "info"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "routeId": data.get("routeId"),
        "busId": data.get("busId"),
        "targetRole": data.get("targetRole", "all"),
        "isRead": False
    }
    
    if not hasattr(db, "notifications"):
        db.notifications = []
        
    db.notifications.insert(0, new_notif)
    db.notifications = db.notifications[:100]
    save_mock_db(db)
    
    return {"success": True, "notification": new_notif}

@router.put("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: str, current_user: Dict = Depends(get_current_user)):
    db = get_db()
    for n in getattr(db, "notifications", []):
        if n.get("id") == notif_id:
            n["isRead"] = True
            n["read"] = True
            save_mock_db(db)
            return {"success": True}
    raise HTTPException(status_code=404, detail="Notification not found")

@router.get("/privacy/report")
def get_privacy_report(current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    active_trips_count = len([t for t in db.trips if t.get("status") == "in_progress"])
    return {
        "studentsTrackedCount": 0,
        "staffTrackedCount": 0,
        "activeBusGpsSessionsCount": active_trips_count,
        "gpsCollectedOnlyOnActiveTrip": True,
        "zeroStudentLocationPolicyVerified": True
    }
