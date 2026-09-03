from backend.app.services.database import get_db
db = get_db()
print("Users:", [{"id": u.get("id"), "email": u.get("email"), "studentId": u.get("studentId"), "staffId": u.get("staffId")} for u in db.users])
