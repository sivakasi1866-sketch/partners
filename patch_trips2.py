with open('backend/app/api/trips.py', 'r') as f:
    content = f.read()

old_check = """
    if req.busId != db_driver.get("assignedBusId"):
        raise HTTPException(status_code=403, detail="Unauthorized: You are not assigned to this bus")
        
    if req.routeId != db_driver.get("assignedRouteId"):
        raise HTTPException(status_code=403, detail="Unauthorized: You are not assigned to this route")
"""

new_check = """
    if req.busId != db_driver.get("assignedBusId"):
        raise HTTPException(status_code=403, detail=f"Unauthorized: You are not assigned to this bus. Driver assigned bus: {db_driver.get('assignedBusId')}, Req bus: {req.busId}")
        
    if req.routeId != db_driver.get("assignedRouteId"):
        raise HTTPException(status_code=403, detail=f"Unauthorized: You are not assigned to this route. Driver assigned route: {db_driver.get('assignedRouteId')}, Req route: {req.routeId}")
"""

content = content.replace(old_check, new_check)

with open('backend/app/api/trips.py', 'w') as f:
    f.write(content)
