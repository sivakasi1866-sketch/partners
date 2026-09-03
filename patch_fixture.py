import re

with open('backend/app/tests/test_agent8_regression.py', 'r') as f:
    code = f.read()

# Replace the entire fixture
fixture_pattern = re.compile(r'@pytest.fixture.*?yield.*?orig_system_logs\)', re.DOTALL)

new_fixture = """@pytest.fixture(autouse=True)
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
            
    yield
    
    db.trips = json.loads(orig_trips)
    db.buses = json.loads(orig_buses)
    db.drivers = json.loads(orig_drivers)
    db.users = json.loads(orig_users)
    db.routes = json.loads(orig_routes)
    db.telemetry = json.loads(orig_telemetry)
    db.system_logs = json.loads(orig_system_logs)
"""

code = fixture_pattern.sub(new_fixture, code)

with open('backend/app/tests/test_agent8_regression.py', 'w') as f:
    f.write(code)
