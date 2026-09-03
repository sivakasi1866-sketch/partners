sed -i 's/"email": "student1@example.com"/"identifier": "student1@example.com"/g' backend/app/tests/test_api.py
sed -i 's/email": "alice2@test.com"/identifier": "alice2@test.com"/g' backend/app/tests/test_import.py
sed -i 's/"email": "new.student@example.com"/"identifier": "new.student@example.com"/g' backend/app/tests/test_users.py
sed -i 's/"email": "student1@example.com"/"identifier": "student1@example.com"/g' backend/app/tests/test_users.py
