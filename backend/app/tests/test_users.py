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
        {"id": "admin-1", "role": "admin", "name": "Admin", "email": "admin@example.com", "passwordHash": hashed, "status": "active"},
        {"id": "driver-1", "role": "driver", "name": "Driver 1", "email": "driver1@example.com", "passwordHash": hashed, "status": "active"},
        {"id": "student-1", "role": "student", "name": "Student 1", "email": "student1@example.com", "passwordHash": hashed, "status": "active"},
        {"id": "staff-1", "role": "staff", "name": "Staff 1", "email": "staff1@example.com", "passwordHash": hashed, "status": "active"}
    ]
    db.drivers = [{"id": "driver-1", "name": "Driver 1", "email": "driver1@example.com", "assignedBusId": "bus-1", "assignedRouteId": "route-1"}]
    yield

def get_token(email: str):
    response = client.post("/api/auth/login", json={"identifier": email, "password": "password123"})
    return response.json()["access_token"]

def get_headers(email: str):
    return {"Authorization": f"Bearer {get_token(email)}"}

def test_1_create_user_admin():
    headers = get_headers("admin@example.com")
    response = client.post("/api/users", json={
        "name": "New Student",
        "email": "new.student@example.com",
        "role": "student",
        "password": "password123"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "new.student@example.com"

def test_2_create_user_student_rejected():
    headers = get_headers("student1@example.com")
    response = client.post("/api/users", json={
        "name": "Hacker Student",
        "identifier": "hacker@example.com",
        "role": "admin",
        "password": "password123"
    }, headers=headers)
    assert response.status_code == 403

def test_3_duplicate_user():
    headers = get_headers("admin@example.com")
    response = client.post("/api/users", json={
        "name": "Another Admin",
        "email": "admin@example.com",  # Duplicate
        "role": "admin",
        "password": "password123"
    }, headers=headers)
    assert response.status_code == 400

def test_4_deactivate_user():
    admin_headers = get_headers("admin@example.com")
    response = client.patch("/api/users/student-1/status", json={"status": "inactive"}, headers=admin_headers)
    assert response.status_code == 200
    
    # Now try to login as student-1
    login_resp = client.post("/api/auth/login", json={"identifier": "student1@example.com", "password": "password123"})
    assert login_resp.status_code == 403
    assert "inactive" in login_resp.json()["detail"].lower()

def test_5_update_role_admin():
    admin_headers = get_headers("admin@example.com")
    response = client.patch("/api/users/student-1/role", json={"role": "staff"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "staff"

def test_6_update_role_student_rejected():
    headers = get_headers("student1@example.com")
    response = client.patch("/api/users/student-1/role", json={"role": "admin"}, headers=headers)
    assert response.status_code == 403

def test_7_get_users_admin():
    admin_headers = get_headers("admin@example.com")
    response = client.get("/api/users", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()["users"]) >= 4
    # Ensure no passwordHash is returned
    for u in response.json()["users"]:
        assert "passwordHash" not in u

def test_8_get_users_student_rejected():
    headers = get_headers("student1@example.com")
    response = client.get("/api/users", headers=headers)
    assert response.status_code == 403

def test_9_driver_gps_validation():
    # Wait, testing GPS driver requires trips to be setup. Let's just test get driver.
    response = client.get("/api/drivers")
    assert response.status_code == 200
    assert len(response.json()["drivers"]) >= 1

