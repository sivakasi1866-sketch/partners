import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.database import get_db, save_mock_db
import json

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
    db.telemetry = []
    
    # We need a trip for driver-1
    trip_id = "trip-gps-1"
    db.trips.append({
        "id": trip_id,
        "busId": "bus-1",
        "driverId": "driver-1",
        "routeId": "route-1",
        "status": "in_progress",
        "gpsActive": True,
        "currentLatitude": 0,
        "currentLongitude": 0
    })
    
    db.buses[0]["status"] = "in_service"
    
    save_mock_db(db)
    yield
    # We just run one test at a time or we can reset, let's let the DB reload in real app, here we reload in fixture.

def test_1_student_gps_rejected():
    headers = get_headers("student1@example.com")
    resp = client.post("/api/trips/update-gps", json={
        "tripId": "trip-gps-1",
        "driverId": "student-1",
        "latitude": 40.0,
        "longitude": -73.0,
        "timestamp": "2023-01-01T00:00:00Z"
    }, headers=headers)
    assert resp.status_code == 403

def test_2_staff_gps_rejected():
    headers = get_headers("staff1@example.com")
    resp = client.post("/api/trips/update-gps", json={
        "tripId": "trip-gps-1",
        "driverId": "staff-1",
        "latitude": 40.0,
        "longitude": -73.0,
        "timestamp": "2023-01-01T00:00:00Z"
    }, headers=headers)
    assert resp.status_code == 403

def test_3_wrong_driver_rejected():
    # driver-3 tries to update driver-1's trip
    db = get_db()
    headers = get_headers("driver2@example.com")
    resp = client.post("/api/trips/update-gps", json={
        "tripId": "trip-gps-1",
        "driverId": "driver-2",
        "latitude": 40.0,
        "longitude": -73.0,
        "timestamp": "2023-01-01T00:00:00Z"
    }, headers=headers)
    assert resp.status_code == 403

def test_4_invalid_coordinates_rejected():
    headers = get_headers("driver1@example.com")
    resp = client.post("/api/trips/update-gps", json={
        "tripId": "trip-gps-1",
        "driverId": "driver-1",
        "latitude": 100.0, # invalid
        "longitude": -73.0,
        "timestamp": "2023-01-01T00:00:00Z"
    }, headers=headers)
    assert resp.status_code == 422
    
    resp2 = client.post("/api/trips/update-gps", json={
        "tripId": "trip-gps-1",
        "driverId": "driver-1",
        "latitude": 40.0,
        "longitude": 190.0, # invalid
        "timestamp": "2023-01-01T00:00:00Z"
    }, headers=headers)
    assert resp2.status_code == 422

def test_5_active_driver_gps_accepted():
    headers = get_headers("driver1@example.com")
    resp = client.post("/api/trips/update-gps", json={
        "tripId": "trip-gps-1",
        "driverId": "driver-1",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timestamp": "2023-01-01T00:00:00Z",
        "speedKmH": 30.0
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["success"] == True
    
    db = get_db()
    assert len(db.telemetry) == 1
    assert db.telemetry[0]["latitude"] == 40.7128
    assert db.telemetry[0]["speed_kmh"] == 30.0

def test_6_duplicate_telemetry_protected():
    headers = get_headers("driver1@example.com")
    payload = {
        "tripId": "trip-gps-1",
        "driverId": "driver-1",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timestamp": "2023-01-01T00:00:00Z",
        "speedKmH": 30.0
    }
    client.post("/api/trips/update-gps", json=payload, headers=headers)
    
    resp2 = client.post("/api/trips/update-gps", json=payload, headers=headers)
    assert resp2.status_code == 200
    
    db = get_db()
    # Should only be 1 in telemetry, duplicate was ignored
    assert len(db.telemetry) == 1

def test_7_post_stop_gps_rejected():
    headers = get_headers("driver1@example.com")
    
    # stop the trip
    r_stop = client.post("/api/trips/stop", json={"tripId": "trip-gps-1", "driverId": "driver-1"}, headers=headers)
    assert r_stop.status_code == 200
    
    # send gps
    payload = {
        "tripId": "trip-gps-1",
        "driverId": "driver-1",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timestamp": "2023-01-01T00:01:00Z"
    }
    resp = client.post("/api/trips/update-gps", json=payload, headers=headers)
    assert resp.status_code == 403
    assert "strictly forbidden" in resp.json()["detail"]

