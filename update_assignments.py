import re

with open("backend/app/api/assignments.py", "r") as f:
    content = f.read()

create_repl = """
    driver["assignedRouteId"] = req.routeId
    
    # Notify driver
    if not hasattr(db, "notifications"):
        db.notifications = []
    
    import uuid
    from datetime import datetime
    
    db.notifications.insert(0, {
        "id": f"notif-{uuid.uuid4().hex[:8]}",
        "title": "New Assignment",
        "message": f"You have been assigned to Bus {bus.get('busNumber')} on Route {route.get('routeName')}.",
        "type": "info",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "routeId": req.routeId,
        "busId": req.busId,
        "targetRole": "driver",
        "userId": req.driverId,
        "isRead": False
    })
    
    try:
        from backend.app.services.database import save_mock_db
        save_mock_db(db)
    except:
        pass
        
    return {"success": True, "driver": driver}
"""
content = re.sub(
    r'driver\["assignedRouteId"\] = req\.routeId\s*return \{"success": True, "driver": driver\}',
    create_repl.replace('\\', '\\\\'),
    content
)

remove_repl = """
    driver["assignedRouteId"] = None
    
    # Notify driver
    if not hasattr(db, "notifications"):
        db.notifications = []
    
    import uuid
    from datetime import datetime
    
    db.notifications.insert(0, {
        "id": f"notif-{uuid.uuid4().hex[:8]}",
        "title": "Assignment Removed",
        "message": f"Your current bus/route assignment has been removed.",
        "type": "warning",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "targetRole": "driver",
        "userId": driver_id,
        "isRead": False
    })
    
    try:
        from backend.app.services.database import save_mock_db
        save_mock_db(db)
    except:
        pass
        
    return {"success": True, "driver": driver}
"""
content = re.sub(
    r'driver\["assignedRouteId"\] = None\s*return \{"success": True, "driver": driver\}',
    remove_repl.replace('\\', '\\\\'),
    content
)

with open("backend/app/api/assignments.py", "w") as f:
    f.write(content)
