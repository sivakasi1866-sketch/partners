import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.database import get_db

client = TestClient(app)

def get_token(email: str):
    response = client.post("/api/auth/login", json={"identifier": email, "password": "password123"})
    if response.status_code == 200:
        return response.json()["access_token"]
    return ""

def get_headers(email: str):
    return {"Authorization": f"Bearer {get_token(email)}"}

@pytest.fixture(autouse=True)
def run_around_tests():
    db = get_db()
    import json
    orig_trips = json.dumps(db.trips)
    orig_buses = json.dumps(db.buses)
    orig_drivers = json.dumps(db.drivers)
    orig_users = json.dumps(db.users)
    orig_routes = json.dumps(db.routes)
    orig_telemetry = json.dumps(db.telemetry)
    orig_system_logs = json.dumps(getattr(db, 'system_logs', []))
    
    db.trips = []
    db.telemetry = []
    db.system_logs = []
    
    db.buses.append({"id": "bus-3", "busNumber": "103", "status": "maintenance", "capacity": 40})
    db.buses.append({"id": "bus-2", "busNumber": "102", "status": "idle", "capacity": 40})
    
    pass_hash = "$2b$12$yy6z54nVBPAAyM2.Iywvs.oa2nX4l39GZ1b5FP3aRrGhOpjIgSoG."
    
    db.users.append({"id": "driver-3", "email": "driver3@example.com", "role": "driver", "name": "Driver 3", "passwordHash": pass_hash, "status": "active"})
    db.drivers.append({"id": "driver-3", "email": "driver3@example.com", "role": "driver", "name": "Driver 3", "assignedBusId": "bus-1", "assignedRouteId": "route-1"})
    
    for r in db.routes:
        if r["id"] == "route-1":
            r["stops"].append({"id": "stop-2", "name": "Stop 2", "latitude": 10.0001, "longitude": 20.0001})
            
    db.trips = []
    db.telemetry = []
    db.system_logs = []
    db.trips = []
    db.telemetry = []
    db.system_logs = []
    db.trips = []
    db.telemetry = []
    db.system_logs = []
    db.trips = []
    db.telemetry = []
    db.system_logs = []
    db.trips = []
    db.telemetry = []
    db.system_logs = []
    db.trips = []
    db.telemetry = []
    db.system_logs = []
    yield
    
    db.trips = json.loads(orig_trips)
    db.buses = json.loads(orig_buses)
    db.drivers = json.loads(orig_drivers)
    db.users = json.loads(orig_users)
    db.routes = json.loads(orig_routes)
    db.telemetry = json.loads(orig_telemetry)
    db.system_logs = json.loads(orig_system_logs)


def test_1_duplicate_trip_start():
    headers = get_headers("driver1@example.com")
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    assert r1.status_code == 200
    r2 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    assert r2.status_code == 400

def test_2_bus_conflict():
    headers = get_headers("driver1@example.com")
    # Start trip A with driver 1 on bus 1
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    assert r1.status_code == 200
    
    headers2 = get_headers("driver3@example.com") # driver-3 also assigned to bus-1
    # Another driver tries to start on the same bus 1
    r2 = client.post("/api/trips/start", json={"driverId": "driver-3", "busId": "bus-1", "routeId": "route-1"}, headers=headers2)
    assert r2.status_code == 400

def test_3_bus_maintenance():
    # Setup driver to be assigned to bus-3
    db = get_db()
    for d in db.drivers:
        if d["id"] == "driver-1":
            d["assignedBusId"] = "bus-3"
            
    headers = get_headers("driver1@example.com")
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-3", "routeId": "route-1"}, headers=headers)
    assert r1.status_code == 400

def test_4_driver_conflict():
    # Already tested in test_1 basically, but let's test driver A trying to start a different trip
    headers = get_headers("driver1@example.com")
    db = get_db()
    for d in db.drivers:
        if d["id"] == "driver-1":
            d["assignedBusId"] = "bus-1"
            
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    assert r1.status_code == 200
    
    # now let's change assignment dynamically just to test
    for d in db.drivers:
        if d["id"] == "driver-1":
            d["assignedBusId"] = "bus-2"
            
    r2 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-2", "routeId": "route-1"}, headers=headers)
    assert r2.status_code == 400

def test_5_gps_stop_detection():
    headers = get_headers("driver1@example.com")
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = r1.json()["trip"]["id"]
    
    db = get_db()
    route = next(r for r in db.routes if r["id"] == "route-1")
    stop2 = route["stops"][1]
    stop2 = route["stops"][1]
    
    r_gps1 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:00:00Z"
    }, headers=headers)
    assert r_gps1.status_code == 200
    
    r_gps2 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:00Z"
    }, headers=headers)
    assert r_gps2.status_code == 200
    
    trip = next(t for t in db.trips if t["id"] == trip_id)
    assert trip["currentStopIndex"] == 1
    assert trip["nextStopIndex"] == 2

def test_6_duplicate_stop_events():
    headers = get_headers("driver1@example.com")
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = r1.json()["trip"]["id"]
    
    db = get_db()
    route = next(r for r in db.routes if r["id"] == "route-1")
    stop2 = route["stops"][1]
    
    initial_logs_count = len(getattr(db, 'system_logs', []))
    
    r_gps1 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:00Z", "accuracyMeters": 10.0
    }, headers=headers)
    assert r_gps1.status_code == 200
    
    r_gps2 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:05Z", "accuracyMeters": 10.0
    }, headers=headers)
    assert r_gps2.status_code == 200
    
    new_logs_count = len(getattr(db, 'system_logs', []))
    assert new_logs_count == initial_logs_count + 1

def test_7_post_stop_gps():
    headers = get_headers("driver1@example.com")
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = r1.json()["trip"]["id"]
    
    client.post("/api/trips/stop", json={"tripId": trip_id, "driverId": "driver-1"}, headers=headers)
    
    r_gps = r_gps1 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": 0, "longitude": 0, "timestamp": "2023-01-01T00:01:00Z"
    }, headers=headers)
    assert r_gps.status_code == 403

def test_8_student_gps():
    headers = get_headers("student1@example.com")
    r_gps = r_gps1 = client.post("/api/trips/update-gps", json={
        "tripId": "dummy", "driverId": "dummy", "latitude": 0, "longitude": 0, "timestamp": "2023-01-01T00:01:00Z"
    }, headers=headers)
    assert r_gps.status_code == 403

def test_9_staff_gps():
    headers = get_headers("staff1@example.com")
    r_gps = r_gps1 = client.post("/api/trips/update-gps", json={
        "tripId": "dummy", "driverId": "dummy", "latitude": 0, "longitude": 0, "timestamp": "2023-01-01T00:01:00Z"
    }, headers=headers)
    assert r_gps.status_code == 403
