import re

with open('backend/app/tests/test_agent8_regression.py', 'r') as f:
    code = f.read()

# Fix the test 5
code = re.sub(
    r'r_gps = r_gps = client.post\("/api/trips/update-gps", json=\{\n\s*"tripId": trip_id,\n\s*"latitude": stop1\["latitude"\],\n\s*"longitude": stop1\["longitude"\],\n\s*"timestamp": "2023-01-01T00:00:00Z"\n\s*\}, headers=headers\)',
    'r_gps1 = client.post("/api/trips/update-gps", json={"tripId": trip_id, "driverId": "dummy", "latitude": stop1["latitude"], "longitude": stop1["longitude"], "timestamp": "2023-01-01T00:00:00Z"}, headers=headers)',
    code
)

code = re.sub(
    r'r_gps = client.post\("/api/trips/update-gps", json=\{\n\s*"tripId": trip_id,\n\s*"latitude": stop2\["latitude"\],\n\s*"longitude": stop2\["longitude"\],\n\s*"timestamp": "2023-01-01T00:01:00Z"\n\s*\}, headers=headers\)',
    'r_gps2 = client.post("/api/trips/update-gps", json={"tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:00Z"}, headers=headers)',
    code
)

code = code.replace("assert r_gps.status_code == 200", "assert r_gps1.status_code == 200")

# Fix test 6
code = code.replace(
    'r_gps = client.post("/api/trips/update-gps", json={',
    'r_gps1 = client.post("/api/trips/update-gps", json={'
)
code = code.replace(
    'r_gps1 = client.post("/api/trips/update-gps", json={\n            "tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:05Z"',
    'r_gps2 = client.post("/api/trips/update-gps", json={\n            "tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:05Z"'
)

with open('backend/app/tests/test_agent8_regression.py', 'w') as f:
    f.write(code)

