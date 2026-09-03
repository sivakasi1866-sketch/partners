import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.database import get_db, save_mock_db

client = TestClient(app)

def get_headers(email: str):
    response = client.post("/api/auth/login", json={"identifier": email, "password": "password123"})
    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}

@pytest.fixture(autouse=True)
def run_around_tests():
    db = get_db()
    with open("server/data/mock_db.json.bak", "r") as f:
        data = json.load(f)
    
    db.users = data.get("users", [])
    db.buses = data.get("buses", [])
    db.routes = data.get("routes", [])
    db.drivers = data.get("drivers", [])
    db.trips = []
    
    from backend.app.core.security import get_password_hash
    pass_hash = get_password_hash("password123")
    
    db.users.append({"id": "driver-inactive", "email": "driverinactive@example.com", "role": "driver", "name": "Driver Inactive", "passwordHash": pass_hash, "status": "inactive"})
    db.drivers.append({"id": "driver-inactive", "email": "driverinactive@example.com", "role": "driver", "name": "Driver Inactive", "status": "inactive"})
    
    db.users.append({"id": "driver-3", "email": "driver3@example.com", "role": "driver", "name": "Driver 3", "passwordHash": pass_hash, "status": "active"})
    db.drivers.append({"id": "driver-3", "email": "driver3@example.com", "role": "driver", "name": "Driver 3", "status": "active"})
    
    db.buses.append({"id": "bus-maintenance", "busNumber": "999", "status": "maintenance"})
    db.buses.append({"id": "bus-inactive", "busNumber": "998", "status": "inactive"})
    db.buses.append({"id": "bus-2", "busNumber": "102", "status": "idle"})
    
    db.routes.append({"id": "route-inactive", "name": "Inactive", "status": "inactive", "stops": []})

    save_mock_db(db)
    
    yield
    
    # Restore disk
    with open("server/data/mock_db.json.bak", "r") as f:
        data = json.load(f)
    with open("server/data/mock_db.json", "w") as f:
        json.dump(data, f, indent=2)

def test_1_admin_creates_assignment():
    admin_headers = get_headers("admin@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-3", "busId": "bus-2", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] == True

def test_2_student_cannot_create_assignment():
    headers = get_headers("student1@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-3", "busId": "bus-2", "routeId": "route-1"
    }, headers=headers)
    assert resp.status_code == 403

def test_3_staff_cannot_create_assignment():
    headers = get_headers("staff1@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-3", "busId": "bus-2", "routeId": "route-1"
    }, headers=headers)
    assert resp.status_code == 403

def test_4_driver_cannot_create_assignment():
    headers = get_headers("driver1@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-3", "busId": "bus-2", "routeId": "route-1"
    }, headers=headers)
    assert resp.status_code == 403

def test_5_invalid_driver_rejected():
    admin_headers = get_headers("admin@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-unknown", "busId": "bus-2", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 400

def test_6_student_used_as_driver_rejected():
    admin_headers = get_headers("admin@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "usr-student-1", "busId": "bus-2", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 400

def test_8_inactive_driver_rejected():
    admin_headers = get_headers("admin@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-inactive", "busId": "bus-2", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 400
    assert "not active" in resp.json()["detail"]

def test_10_maintenance_bus_rejected():
    admin_headers = get_headers("admin@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-3", "busId": "bus-maintenance", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 400
    assert "not available" in resp.json()["detail"]

def test_13_inactive_route_rejected():
    admin_headers = get_headers("admin@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-3", "busId": "bus-2", "routeId": "route-inactive"
    }, headers=admin_headers)
    assert resp.status_code == 400
    assert "inactive" in resp.json()["detail"]

def test_15_duplicate_bus_assignment_rejected():
    admin_headers = get_headers("admin@example.com")
    # In pristine db, driver-1 is assigned to bus-1
    resp = client.post("/api/assignments", json={
        "driverId": "driver-3", "busId": "bus-1", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 400
    assert "already assigned to another driver" in resp.json()["detail"]

def test_17_reassignment_works_safely():
    admin_headers = get_headers("admin@example.com")
    resp = client.delete("/api/assignments/driver-1", headers=admin_headers)
    assert resp.status_code == 200
    
    resp = client.post("/api/assignments", json={
        "driverId": "driver-1", "busId": "bus-2", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 200

def test_19_active_trip_blocks_reassignment():
    driver_headers = get_headers("driver1@example.com")
    r_start = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=driver_headers)
    assert r_start.status_code == 200
    
    admin_headers = get_headers("admin@example.com")
    resp = client.post("/api/assignments", json={
        "driverId": "driver-1", "busId": "bus-2", "routeId": "route-1"
    }, headers=admin_headers)
    assert resp.status_code == 400
    assert "active trip" in resp.json()["detail"]
    
    resp2 = client.delete("/api/assignments/driver-1", headers=admin_headers)
    assert resp2.status_code == 400
    assert "active trip" in resp2.json()["detail"]

def test_22_driver_sees_only_own_assignment():
    driver_headers = get_headers("driver1@example.com")
    resp = client.get("/api/assignments", headers=driver_headers)
    assert resp.status_code == 200
    assignments = resp.json()["assignments"]
    assert len(assignments) == 1
    assert assignments[0]["driverId"] == "driver-1"

def test_23_admin_sees_all_assignments():
    admin_headers = get_headers("admin@example.com")
    resp = client.get("/api/assignments", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()["assignments"]) >= 1

def test_26_gps_privacy_remains_intact():
    student_headers = get_headers("student1@example.com")
    resp = client.post("/api/trips/update-gps", json={
        "tripId": "dummy", "latitude": 0, "longitude": 0, "timestamp": "2023-01-01T00:00:00Z"
    }, headers=student_headers)
    assert resp.status_code in [403, 422]

