import httpx
import sys

def test_login(identifier, password, expected_role):
    try:
        r = httpx.post("http://localhost:3001/api/auth/login", json={"identifier": identifier, "password": password})
        if r.status_code == 200:
            data = r.json()
            role = data['user']['role']
            print(f"[{expected_role.upper()}] login '{identifier}': SUCCESS -> Role: {role}")
            if role != expected_role:
                print(f"  -> WARNING: Expected {expected_role} but got {role}")
        else:
            print(f"[{expected_role.upper()}] login '{identifier}': FAILED -> {r.status_code} {r.text}")
    except Exception as e:
        print(f"[{expected_role.upper()}] login '{identifier}': ERROR -> {e}")

print("Testing logins...")
test_login("admin@example.com", "password123", "admin")
test_login("driver1@example.com", "password123", "driver")
test_login("STU12345", "password123", "student")
test_login("student1@example.com", "password123", "student")
test_login("EMP98765", "password123", "staff")
test_login("staff1@example.com", "password123", "staff")
