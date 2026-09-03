import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.database import get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    db = get_db()
    # Ensure they have passwordHash
    from backend.app.core.security import get_password_hash
    hashed = get_password_hash("password123")
    
    db.users = [
        {"id": "admin-1", "role": "admin", "name": "Admin", "email": "admin@example.com", "passwordHash": hashed},
        {"id": "driver-1", "role": "driver", "name": "Driver 1", "email": "driver1@example.com", "passwordHash": hashed, "assignedBusId": "bus-1", "assignedRouteId": "route-1"},
        {"id": "driver-2", "role": "driver", "name": "Driver 2", "email": "driver2@example.com", "passwordHash": hashed},
        {"id": "student-1", "role": "student", "name": "Student 1", "email": "student1@example.com", "passwordHash": hashed},
        {"id": "staff-1", "role": "staff", "name": "Staff 1", "email": "staff1@example.com", "passwordHash": hashed}
    ]
    db.buses = [{"id": "bus-1", "busNumber": "101", "status": "idle"}]
    db.routes = [{"id": "route-1", "name": "Route 1", "stops": [{"id": "stop-1", "latitude": 10, "longitude": 10}]}]
    db.trips = []
    db.drivers = []
    db.telemetry = []
    yield

def get_token(email: str):
    response = client.post("/api/auth/login", json={"identifier": email, "password": "password123"})
    return response.json()["access_token"]

def get_headers(email: str):
    return {"Authorization": f"Bearer {get_token(email)}"}

def test_1_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_2_auth_login():
    response = client.post("/api/auth/login", json={"identifier": "student1@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    response = client.post("/api/auth/login", json={"identifier": "student1@example.com", "password": "wrong"})
    assert response.status_code == 401

def test_3_buses():
    response = client.get("/api/buses")
    assert response.status_code == 200

def test_6_trip_start():
    headers = get_headers("driver1@example.com")
    response = client.post("/api/trips/start", json={
        "driverId": "driver-1", 
        "busId": "bus-1",
        "routeId": "route-1"
    }, headers=headers)
    assert response.status_code == 200
    trip = response.json()["trip"]
    assert trip["status"] == "in_progress"

def test_7_trip_stop():
    headers = get_headers("driver1@example.com")
    start_resp = client.post("/api/trips/start", json={
        "driverId": "driver-1",
        "busId": "bus-1",
        "routeId": "route-1"
    }, headers=headers)
    trip_id = start_resp.json()["trip"]["id"]
    
    stop_resp = client.post("/api/trips/stop", json={
        "tripId": trip_id,
        "driverId": "driver-1"
    }, headers=headers)
    assert stop_resp.status_code == 200
    assert stop_resp.json()["trip"]["status"] == "completed"

def test_9_telemetry_authorization():
    driver_headers = get_headers("driver1@example.com")
    response = client.get("/api/telemetry/export", headers=driver_headers)
    assert response.status_code == 403
    
    admin_headers = get_headers("admin@example.com")
    response = client.get("/api/telemetry/export", headers=admin_headers)
    assert response.status_code == 200

def test_10_post_stop_gps_rejection():
    headers = get_headers("driver1@example.com")
    start_resp = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = start_resp.json()["trip"]["id"]
    
    client.post("/api/trips/stop", json={"tripId": trip_id, "driverId": "driver-1"}, headers=headers)
    
    gps_resp = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "driver-1", "latitude": 10.0, "longitude": 10.0, "timestamp": "2026-08-31T00:00:00Z"
    }, headers=headers)
    assert gps_resp.status_code == 403

def test_11_telemetry_persistence():
    headers = get_headers("driver1@example.com")
    start_resp = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = start_resp.json()["trip"]["id"]
    
    gps_resp = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "driver-1", "latitude": 10.5, "longitude": 10.5, "timestamp": "2026-08-31T00:00:00Z"
    }, headers=headers)
    assert gps_resp.status_code == 200

def test_12_telemetry_export():
    admin_headers = get_headers("admin@example.com")
    response = client.get("/api/telemetry/export", headers=admin_headers)
    assert response.status_code == 200

def test_14_student_gps_rejection():
    headers = get_headers("student1@example.com")
    start_resp = client.post("/api/trips/start", json={"driverId": "student-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    assert start_resp.status_code == 403

def test_15_staff_gps_rejection():
    headers = get_headers("staff1@example.com")
    start_resp = client.post("/api/trips/start", json={"driverId": "staff-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    assert start_resp.status_code == 403

def test_16_wrong_driver_rejection():
    headers = get_headers("driver1@example.com")
    start_resp = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = start_resp.json()["trip"]["id"]
    
    headers2 = get_headers("driver2@example.com")
    gps_resp = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "driver-2", "latitude": 10.0, "longitude": 10.0, "timestamp": "2026-08-31T00:00:00Z"
    }, headers=headers2)
    assert gps_resp.status_code == 403

def test_18_driver_trip_assignment_enforced():
    # Setup Driver 2 with different assignment
    db = get_db()
    from backend.app.core.security import get_password_hash
    hashed = get_password_hash("password123")
    
    # Assign Driver 2 to something else
    for u in db.users:
        if u["id"] == "driver-2":
            u["assignedBusId"] = "bus-2"
            u["assignedRouteId"] = "route-2"
    
    # Try starting bus-1 with driver-2
    headers = get_headers("driver2@example.com")
    start_resp = client.post("/api/trips/start", json={
        "driverId": "driver-2",
        "busId": "bus-1",
        "routeId": "route-1"
    }, headers=headers)
    assert start_resp.status_code == 403
    assert "not assigned" in start_resp.json()["detail"].lower()
