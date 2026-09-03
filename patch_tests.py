import re

for file in ["backend/app/tests/test_api.py", "backend/app/tests/test_users.py"]:
    with open(file, "r") as f:
        content = f.read()
        
    old_driver = '{"id": "driver-1", "role": "driver", "name": "Driver 1", "email": "driver1@example.com", "passwordHash": hashed}'
    new_driver = '{"id": "driver-1", "role": "driver", "name": "Driver 1", "email": "driver1@example.com", "passwordHash": hashed, "assignedBusId": "bus-1", "assignedRouteId": "route-1"}'
    content = content.replace(old_driver, new_driver)
    
    # test_users also has db.drivers
    old_db_driver = '{"id": "driver-1", "name": "Driver 1", "email": "driver1@example.com"}'
    new_db_driver = '{"id": "driver-1", "name": "Driver 1", "email": "driver1@example.com", "assignedBusId": "bus-1", "assignedRouteId": "route-1"}'
    content = content.replace(old_db_driver, new_db_driver)
    
    with open(file, "w") as f:
        f.write(content)
