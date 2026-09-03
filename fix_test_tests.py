import re

with open('backend/app/tests/test_agent8_regression.py', 'r') as f:
    code = f.read()

# Replace test_5
code = re.sub(
    r'def test_5_gps_stop_detection\(\):.*?def test_6_duplicate_stop_events',
    """def test_5_gps_stop_detection():
    headers = get_headers("driver1@example.com")
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = r1.json()["trip"]["id"]
    
    db = get_db()
    route = next(r for r in db.routes if r["id"] == "route-1")
    stop1 = route["stops"][0]
    stop2 = route["stops"][1]
    
    r_gps1 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop1["latitude"], "longitude": stop1["longitude"], "timestamp": "2023-01-01T00:00:00Z"
    }, headers=headers)
    assert r_gps1.status_code == 200
    
    r_gps2 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:00Z"
    }, headers=headers)
    assert r_gps2.status_code == 200
    
    trip = next(t for t in db.trips if t["id"] == trip_id)
    assert trip["currentStopIndex"] == 1
    assert trip["nextStopIndex"] == 2

def test_6_duplicate_stop_events""",
    code, flags=re.DOTALL
)

# Replace test_6
code = re.sub(
    r'def test_6_duplicate_stop_events\(\):.*?def test_7_post_stop_gps',
    """def test_6_duplicate_stop_events():
    headers = get_headers("driver1@example.com")
    r1 = client.post("/api/trips/start", json={"driverId": "driver-1", "busId": "bus-1", "routeId": "route-1"}, headers=headers)
    trip_id = r1.json()["trip"]["id"]
    
    db = get_db()
    route = next(r for r in db.routes if r["id"] == "route-1")
    stop1 = route["stops"][0]
    
    initial_logs_count = len(getattr(db, 'system_logs', []))
    
    r_gps1 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop1["latitude"], "longitude": stop1["longitude"], "timestamp": "2023-01-01T00:01:00Z", "accuracyMeters": 10.0
    }, headers=headers)
    assert r_gps1.status_code == 200
    
    r_gps2 = client.post("/api/trips/update-gps", json={
        "tripId": trip_id, "driverId": "dummy", "latitude": stop1["latitude"], "longitude": stop1["longitude"], "timestamp": "2023-01-01T00:01:05Z", "accuracyMeters": 10.0
    }, headers=headers)
    assert r_gps2.status_code == 200
    
    new_logs_count = len(getattr(db, 'system_logs', []))
    assert new_logs_count == initial_logs_count + 1

def test_7_post_stop_gps""",
    code, flags=re.DOTALL
)

with open('backend/app/tests/test_agent8_regression.py', 'w') as f:
    f.write(code)

