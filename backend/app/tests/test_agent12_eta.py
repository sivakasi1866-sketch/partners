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
    with open("server/data/mock_db.json", "r") as f:
        data = json.load(f)
    
    db.users = data.get("users", [])
    db.buses = data.get("buses", [])
    db.routes = data.get("routes", [])
    db.drivers = data.get("drivers", [])
    db.trips = []
    db.telemetry = []
    
    trip_id = "trip-eta-1"
    db.trips.append({
        "id": trip_id,
        "busId": "bus-1",
        "driverId": "driver-1",
        "routeId": db.routes[0]["id"] if db.routes else "route-1",
        "status": "in_progress",
        "gpsActive": True,
        "currentLatitude": 40.7128,
        "currentLongitude": -74.0060,
        "speedKmH": 30,
        "currentStopIndex": 0
    })
    
    trip_completed = "trip-eta-2"
    db.trips.append({
        "id": trip_completed,
        "busId": "bus-2",
        "driverId": "driver-2",
        "routeId": db.routes[0]["id"] if db.routes else "route-1",
        "status": "completed",
        "gpsActive": False,
        "currentLatitude": 40.7128,
        "currentLongitude": -74.0060,
        "speedKmH": 0,
        "currentStopIndex": 3
    })
    
    if db.buses:
        db.buses[0]["status"] = "in_service"
    
    save_mock_db(db)
    db.save_trips()
    yield
    
def test_1_active_trip_eta():
    headers = get_headers("student1@example.com")
    resp = client.get("/api/trips/trip-eta-1/eta", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tripId"] == "trip-eta-1"
    assert "stopEtas" in data
    print("ACTIVE ETA:", data)

def test_2_completed_trip_eta():
    headers = get_headers("student1@example.com")
    resp = client.get("/api/trips/trip-eta-2/eta", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    print("COMPLETED ETA:", data)

