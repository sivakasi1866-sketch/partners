import re

with open('backend/app/tests/test_agent8_regression.py', 'r') as f:
    code = f.read()

code = code.replace(
    '"tripId": trip_id,\n            "latitude"',
    '"tripId": trip_id, "driverId": "dummy",\n            "latitude"'
)

code = code.replace(
    '"tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:00Z"',
    '"tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:00Z", "accuracyMeters": 10.0'
)

code = code.replace(
    '"tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:05Z"',
    '"tripId": trip_id, "driverId": "dummy", "latitude": stop2["latitude"], "longitude": stop2["longitude"], "timestamp": "2023-01-01T00:01:05Z", "accuracyMeters": 10.0'
)


with open('backend/app/tests/test_agent8_regression.py', 'w') as f:
    f.write(code)
