import io
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
import openpyxl

from backend.app.services.database import get_db
from backend.app.api.deps import require_role
from backend.app.core.security import get_password_hash

router = APIRouter()

def save_mock_db(db):
    with open("server/data/mock_db.json", "w") as f:
        json.dump({
            "users": db.users,
            "drivers": db.drivers,
            "buses": db.buses,
            "routes": db.routes,
            "systemLogs": db.system_logs,
            "notifications": db.notifications
        }, f, indent=2)

class ImportCommitRequest(BaseModel):
    entity_type: str
    rows: List[Dict]

TEMPLATES = {
    "students": ["name", "email", "department"],
    "staff": ["name", "email", "department"],
    "drivers": ["name", "email", "phone", "driverLicense", "assignedBusId", "assignedRouteId"],
    "buses": ["busNumber"],
    "routes": ["name"],
    "stops": ["routeId", "stopName", "latitude", "longitude"]
}

@router.get("/templates")
def get_templates(current_user: Dict = Depends(require_role(["admin"]))):
    return {"templates": TEMPLATES}

@router.post("/validate")
async def validate_import(
    entity_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: Dict = Depends(require_role(["admin"]))
):
    if not file.filename.endswith(('.xlsx')):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
        
    if entity_type not in TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type. Supported: {list(TEMPLATES.keys())}")
        
    contents = await file.read()
    
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Limit is 5MB.")
        
    try:
        wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not read workbook")
        
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise HTTPException(status_code=400, detail="Empty workbook")
        
    headers = [str(h).strip() if h else "" for h in rows[0]]
    expected_headers = TEMPLATES[entity_type]
    
    # check required headers
    missing = [h for h in expected_headers if h not in headers and h not in ['department', 'phone', 'driverLicense', 'assignedBusId', 'assignedRouteId']]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")
        
    db = get_db()
    
    valid_rows = []
    invalid_rows = []
    duplicate_rows = []
    warnings = []
    
    seen_emails = set(u.get('email') for u in db.users if u.get('email'))
    seen_bus_numbers = set(b.get('busNumber') for b in db.buses if b.get('busNumber'))
    seen_route_names = set(r.get('name') for r in db.routes if r.get('name'))
    
    file_emails = set()
    file_buses = set()
    file_routes = set()
    
    def get_val(row, header_name):
        try:
            idx = headers.index(header_name)
            val = row[idx]
            if val is not None:
                return str(val).strip()
            return None
        except ValueError:
            return None

    for i, row in enumerate(rows[1:], start=2):
        is_valid = True
        errors = []
        parsed = {}
        
        # Parse based on entity
        if entity_type in ['students', 'staff', 'drivers']:
            name = get_val(row, "name")
            email = get_val(row, "email")
            if email: email = email.lower()
            
            if not name or not email:
                is_valid = False
                errors.append("Name and email are required")
            elif email in seen_emails:
                is_valid = False
                errors.append("Duplicate email already exists in system")
            elif email in file_emails:
                is_valid = False
                errors.append("Duplicate email in file")
            else:
                file_emails.add(email)
                parsed['name'] = name
                parsed['email'] = email
                
                if entity_type == 'students' or entity_type == 'staff':
                    dept = get_val(row, 'department')
                    if dept: parsed['department'] = dept
                
                if entity_type == 'drivers':
                    phone = get_val(row, 'phone')
                    if phone: parsed['phone'] = phone
                    dl = get_val(row, 'driverLicense')
                    if dl: parsed['driverLicense'] = dl
                    
                    b_id = get_val(row, 'assignedBusId')
                    r_id = get_val(row, 'assignedRouteId')
                    if b_id:
                        if not any(b.get('id') == b_id for b in db.buses):
                            is_valid = False
                            errors.append(f"Bus {b_id} does not exist")
                        else:
                            parsed['assignedBusId'] = b_id
                    if r_id:
                        if not any(r.get('id') == r_id for r in db.routes):
                            is_valid = False
                            errors.append(f"Route {r_id} does not exist")
                        else:
                            parsed['assignedRouteId'] = r_id
                            
        elif entity_type == 'buses':
            b_num = get_val(row, "busNumber")
            if not b_num:
                is_valid = False
                errors.append("busNumber is required")
            elif b_num in seen_bus_numbers:
                is_valid = False
                errors.append(f"Bus number {b_num} already exists in system")
            elif b_num in file_buses:
                is_valid = False
                errors.append(f"Duplicate bus number {b_num} in file")
            else:
                file_buses.add(b_num)
                parsed['busNumber'] = b_num
                
        elif entity_type == 'routes':
            r_name = get_val(row, "name")
            if not r_name:
                is_valid = False
                errors.append("name is required")
            elif r_name in seen_route_names:
                is_valid = False
                errors.append(f"Route name {r_name} already exists in system")
            elif r_name in file_routes:
                is_valid = False
                errors.append(f"Duplicate route name {r_name} in file")
            else:
                file_routes.add(r_name)
                parsed['name'] = r_name
                
        elif entity_type == 'stops':
            r_id = get_val(row, "routeId")
            s_name = get_val(row, "stopName")
            lat = get_val(row, "latitude")
            lon = get_val(row, "longitude")
            
            if not r_id or not s_name or lat is None or lon is None:
                is_valid = False
                errors.append("routeId, stopName, latitude, and longitude are required")
            elif not any(r.get('id') == r_id for r in db.routes):
                is_valid = False
                errors.append(f"Route {r_id} does not exist")
            else:
                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    if not (-90 <= lat_f <= 90 and -180 <= lon_f <= 180):
                        raise ValueError()
                    parsed['routeId'] = r_id
                    parsed['stopName'] = s_name
                    parsed['latitude'] = lat_f
                    parsed['longitude'] = lon_f
                except ValueError:
                    is_valid = False
                    errors.append("latitude and longitude must be valid coordinates")

        if is_valid:
            valid_rows.append({"row_num": i, "data": parsed})
        else:
            invalid_rows.append({"row_num": i, "errors": errors, "data": parsed if parsed else {get_val(row, h) for h in headers}})

    return {
        "total_rows": len(rows) - 1,
        "valid_rows": len(valid_rows),
        "invalid_rows": len(invalid_rows),
        "duplicate_rows": 0,
        "imported_rows": 0,
        "skipped_rows": 0,
        "errors": [err for row in invalid_rows for err in row['errors']],
        "warnings": warnings,
        "preview_valid": valid_rows
    }


@router.post("/commit")
def commit_import(req: ImportCommitRequest, current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    imported = 0
    errors = []
    
    for row in req.rows:
        data = row.get("data", {})
        try:
            if req.entity_type in ['students', 'staff', 'drivers']:
                # Role assignment
                if req.entity_type == 'students': role = 'student'
                elif req.entity_type == 'staff': role = 'staff'
                elif req.entity_type == 'drivers': role = 'driver'
                
                # Check email duplicate again
                if any(u.get('email') == data.get('email') for u in db.users):
                    errors.append(f"Email {data.get('email')} already exists, skipped")
                    continue
                    
                user_id = f"usr-{role}-{int(time.time()*1000)}-{imported}"
                new_user = {
                    "id": user_id,
                    "name": data.get("name"),
                    "email": data.get("email"),
                    "role": role,
                    "status": "active",
                    "passwordHash": get_password_hash("password123"), # Default password
                    "createdAt": datetime.utcnow().isoformat() + "Z"
                }
                
                if data.get('department'):
                    new_user['department'] = data.get('department')
                    
                if role == 'driver':
                    if data.get('phone'): new_user['phone'] = data.get('phone')
                    if data.get('driverLicense'): new_user['driverLicense'] = data.get('driverLicense')
                    if data.get('assignedBusId'): new_user['assignedBusId'] = data.get('assignedBusId')
                    if data.get('assignedRouteId'): new_user['assignedRouteId'] = data.get('assignedRouteId')
                    
                    driver_entry = new_user.copy()
                    driver_entry["experienceYears"] = 0
                    driver_entry["rating"] = 5.0
                    db.drivers.append(driver_entry)
                    
                db.users.append(new_user)
                imported += 1
                
            elif req.entity_type == 'buses':
                b_num = data.get('busNumber')
                if any(b.get('busNumber') == b_num for b in db.buses):
                    errors.append(f"Bus {b_num} already exists, skipped")
                    continue
                
                bus_id = f"bus-{int(time.time()*1000)}-{imported}"
                db.buses.append({
                    "id": bus_id,
                    "busNumber": b_num,
                    "status": "idle"
                })
                imported += 1
                
            elif req.entity_type == 'routes':
                r_name = data.get('name')
                if any(r.get('name') == r_name for r in db.routes):
                    errors.append(f"Route {r_name} already exists, skipped")
                    continue
                    
                route_id = f"route-{int(time.time()*1000)}-{imported}"
                db.routes.append({
                    "id": route_id,
                    "name": r_name,
                    "stops": []
                })
                imported += 1
                
            elif req.entity_type == 'stops':
                r_id = data.get('routeId')
                route = next((r for r in db.routes if r.get('id') == r_id), None)
                if not route:
                    errors.append(f"Route {r_id} not found, skipped")
                    continue
                    
                stop_id = f"stop-{int(time.time()*1000)}-{imported}"
                if 'stops' not in route:
                    route['stops'] = []
                    
                route['stops'].append({
                    "id": stop_id,
                    "name": data.get('stopName'),
                    "latitude": data.get('latitude'),
                    "longitude": data.get('longitude')
                })
                imported += 1
                
        except Exception as e:
            errors.append(f"Failed to import row: {str(e)}")
            
    # Save the updated DB
    save_mock_db(db)
    
    # Audit log
    db.system_logs.append({
        "id": f"log-{int(time.time()*1000)}",
        "level": "INFO",
        "message": f"Bulk import completed for {req.entity_type}. Imported {imported} rows.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actorRole": current_user.get('role'),
        "actorId": current_user.get('id')
    })
    save_mock_db(db)
    
    return {
        "total_rows": len(req.rows),
        "valid_rows": len(req.rows),
        "invalid_rows": 0,
        "duplicate_rows": 0,
        "imported_rows": imported,
        "skipped_rows": len(req.rows) - imported,
        "errors": errors,
        "warnings": []
    }
