import re

with open('backend/app/tests/test_agent8_regression.py', 'r') as f:
    code = f.read()

# Fix the fixture
code = code.replace(
    'yield',
    'db.trips = []\n    db.telemetry = []\n    db.system_logs = []\n    yield'
)

# Fix the driverId in gps updates
code = code.replace(
    '"tripId": trip_id, "latitude"',
    '"tripId": trip_id, "driverId": "dummy", "latitude"'
)
code = code.replace(
    '"tripId": "dummy", "latitude"',
    '"tripId": "dummy", "driverId": "dummy", "latitude"'
)

with open('backend/app/tests/test_agent8_regression.py', 'w') as f:
    f.write(code)

