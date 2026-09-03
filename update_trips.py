import re

with open("backend/app/api/trips.py", "r") as f:
    content = f.read()

# start_trip
start_repl = """
    db.trips.insert(0, new_trip)
    db.save_trips()
    
    bus["status"] = "in_service"
    
    if not hasattr(db, "notifications"):
        db.notifications = []
    
    import uuid
    from datetime import datetime
    
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
"""
content = re.sub(
    r'db\.trips\.insert\(0, new_trip\)\s*db\.save_trips\(\)\s*bus\["status"\] = "in_service"\s*return \{"success": True, "trip": new_trip\}',
    start_repl.replace('\\', '\\\\'),
    content
)

# stop arrival
arrival_repl = """
                    if not existing_event:
                        db.system_logs.insert(0, {
                            "id": f"evt-{uuid.uuid4().hex[:8]}",
                            "type": "stop_arrival",
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "tripId": trip["id"],
                            "stopId": next_stop.get("id"),
                            "busId": trip["busId"],
                            "message": f"Arrived at stop {next_stop.get('name') or next_stop.get('stopName') or 'Unknown'}"
                        })
                        
                        # create notification
                        if not hasattr(db, "notifications"):
                            db.notifications = []
                        bus_obj = next((b for b in db.buses if b.get("id") == trip.get("busId")), {})
                        db.notifications.insert(0, {
                            "id": f"notif-{uuid.uuid4().hex[:8]}",
                            "title": f"Bus Arrived at Stop",
                            "message": f"Bus {bus_obj.get('busNumber', 'Unknown')} arrived at {next_stop.get('name') or next_stop.get('stopName') or 'Unknown'}.",
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
"""
content = re.sub(
    r'if not existing_event:\s*db\.system_logs\.insert\(0, \{\s*"id": f"evt-\{uuid\.uuid4\(\)\.hex\[:8\]\}",\s*"type": "stop_arrival",\s*"timestamp": datetime\.utcnow\(\)\.isoformat\(\) \+ "Z",\s*"tripId": trip\["id"\],\s*"stopId": next_stop\.get\("id"\),\s*"busId": trip\["busId"\],\s*"message": f"Arrived at stop \{next_stop\.get\(\'name\'\) or next_stop\.get\(\'stopName\'\) or \'Unknown\'\}"\s*\}\)',
    arrival_repl.replace('\\', '\\\\'),
    content
)

# stop trip
stop_repl = """
    db.save_trips()
    
    if not hasattr(db, "notifications"):
        db.notifications = []
        
    route = next((r for r in db.routes if r.get("id") == trip.get("routeId")), {})
    import uuid
    from datetime import datetime
    
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
"""
content = re.sub(
    r'db\.save_trips\(\)\s*return \{',
    stop_repl.replace('\\', '\\\\'),
    content
)

with open("backend/app/api/trips.py", "w") as f:
    f.write(content)

