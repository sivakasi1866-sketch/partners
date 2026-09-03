import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.database import get_db

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
    db.drivers = [{"id": "driver-1", "assignedBusId": "bus-driver", "assignedRouteId": "route-driver"}]
    db.buses = [{"id": "bus-1", "busNumber": "100"}, {"id": "bus-driver", "busNumber": "200"}]
    db.routes = [{"id": "route-1", "name": "Main Route"}, {"id": "route-driver", "name": "Driver Route"}]
    db.trips = [{"id": "trip-1", "busId": "bus-1", "routeId": "route-1"}]
    yield

def get_headers(email: str):
    response = client.post("/api/auth/login", json={"identifier": email, "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_list_buses():
    response = client.get("/api/buses", headers=get_headers("student@example.com"))
    assert response.status_code == 200
    assert len(response.json()["buses"]) == 2

def test_create_bus_admin():
    response = client.post("/api/buses", json={"busNumber": "999"}, headers=get_headers("admin@example.com"))
    assert response.status_code == 200
    assert response.json()["bus"]["busNumber"] == "999"

def test_create_bus_duplicate():
    response = client.post("/api/buses", json={"busNumber": "100"}, headers=get_headers("admin@example.com"))
    assert response.status_code == 400
    
def test_create_bus_student():
    response = client.post("/api/buses", json={"busNumber": "999"}, headers=get_headers("student@example.com"))
    assert response.status_code == 403

def test_delete_bus_in_use():
    response = client.delete("/api/buses/bus-1", headers=get_headers("admin@example.com"))
    assert response.status_code == 400 # Referenced by trips
    
def test_delete_bus_assigned():
    response = client.delete("/api/buses/bus-driver", headers=get_headers("admin@example.com"))
    assert response.status_code == 400 # Assigned to driver

def test_create_route_admin():
    response = client.post("/api/routes", json={"name": "New Route"}, headers=get_headers("admin@example.com"))
    assert response.status_code == 200
    assert response.json()["route"]["name"] == "New Route"

def test_create_stop():
    stop_data = {"name": "Test Stop", "latitude": 10.5, "longitude": 20.5}
    response = client.post("/api/routes/route-1/stops", json=stop_data, headers=get_headers("admin@example.com"))
    assert response.status_code == 200
    stop = response.json()["stop"]
    assert stop["name"] == "Test Stop"
    assert "id" in stop

def test_create_stop_invalid_coords():
    stop_data = {"name": "Test Stop", "latitude": 900.5, "longitude": 20.5}
    response = client.post("/api/routes/route-1/stops", json=stop_data, headers=get_headers("admin@example.com"))
    assert response.status_code == 400
