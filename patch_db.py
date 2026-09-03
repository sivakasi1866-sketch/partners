import json
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("password123")

with open("server/data/mock_db.json", "r") as f:
    db = json.load(f)

for user in db.get("users", []):
    user["passwordHash"] = hashed

for driver in db.get("drivers", []):
    driver["passwordHash"] = hashed

with open("server/data/mock_db.json", "w") as f:
    json.dump(db, f, indent=2)

print("DB patched!")
