import pytest
import io
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.database import get_db
import openpyxl

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    db = get_db()
    from backend.app.core.security import get_password_hash
    hashed = get_password_hash("password123")
    db.users = [
        {"id": "admin-1", "role": "admin", "name": "Admin", "email": "admin@example.com", "passwordHash": hashed},
        {"id": "student-1", "role": "student", "name": "Student", "email": "student@example.com", "passwordHash": hashed}
    ]
    db.drivers = []
    db.buses = [{"id": "bus-1", "busNumber": "100"}]
    db.routes = [{"id": "route-1", "name": "Main Route"}]
    db.system_logs = []
    yield

def get_token(email: str):
    response = client.post("/api/auth/login", json={"identifier": email, "password": "password123"})
    return response.json()["access_token"]

def get_headers(email: str):
    return {"Authorization": f"Bearer {get_token(email)}"}

def create_excel(headers, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.read()

def test_unauthorized_upload():
    content = create_excel(["name", "email", "department"], [("Alice", "alice@test.com", "CS")])
    headers = get_headers("student@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "students"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 403

def test_admin_upload_students():
    content = create_excel(["name", "email", "department"], [("Alice", "alice@test.com", "CS"), ("Bob", "bob@test.com", "Math")])
    headers = get_headers("admin@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "students"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["total_rows"] == 2
    assert res_data["valid_rows"] == 2
    assert len(res_data["preview_valid"]) == 2

def test_duplicate_email():
    content = create_excel(["name", "email", "department"], [("Admin", "admin@example.com", "CS")])
    headers = get_headers("admin@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "students"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["invalid_rows"] == 1

def test_missing_required_column():
    content = create_excel(["name", "department"], [("Alice", "CS")])
    headers = get_headers("admin@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "students"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 400

def test_invalid_driver_assignment():
    content = create_excel(["name", "email", "assignedBusId"], [("Driver1", "d1@test.com", "bus-999")])
    headers = get_headers("admin@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "drivers"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["invalid_rows"] == 1
    assert "bus-999 does not exist" in res_data["errors"][0]

def test_commit_import():
    headers = get_headers("admin@example.com")
    data = {
        "entity_type": "students",
        "rows": [
            {"data": {"name": "Alice", "email": "alice2@test.com", "department": "CS"}}
        ]
    }
    response = client.post("/api/import/commit", json=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["imported_rows"] == 1
    
    # check db
    db = get_db()
    assert any(u["email"] == "alice2@test.com" for u in db.users)
    assert any(log["level"] == "INFO" and "Bulk import completed" in log["message"] for log in db.system_logs)

def test_import_stops_invalid_route():
    content = create_excel(["routeId", "stopName", "latitude", "longitude"], [("route-99", "Stop 1", 10, 10)])
    headers = get_headers("admin@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "stops"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["invalid_rows"] == 1

def test_import_stops_invalid_coords():
    content = create_excel(["routeId", "stopName", "latitude", "longitude"], [("route-1", "Stop 1", 999, 10)])
    headers = get_headers("admin@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "stops"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["invalid_rows"] == 1

def test_import_stops_valid():
    content = create_excel(["routeId", "stopName", "latitude", "longitude"], [("route-1", "Stop 1", 10.5, 20.5)])
    headers = get_headers("admin@example.com")
    files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"entity_type": "stops"}
    response = client.post("/api/import/validate", files=files, data=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["valid_rows"] == 1
    
    commit_data = {
        "entity_type": "stops",
        "rows": res_data["preview_valid"]
    }
    commit_response = client.post("/api/import/commit", json=commit_data, headers=headers)
    assert commit_response.status_code == 200
    
    db = get_db()
    route = next(r for r in db.routes if r["id"] == "route-1")
    assert len(route["stops"]) == 1
    assert route["stops"][0]["name"] == "Stop 1"

