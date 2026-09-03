with open('backend/app/api/auth.py', 'r') as f:
    content = f.read()

replacement_logic = """@router.post("/login")
def login(req: LoginRequest):
    db = get_db()
    
    identifier = req.roll_number if req.roll_number else req.email
    if not identifier:
        raise HTTPException(status_code=400, detail="Missing login identifier")
        
    # Find user by email or studentId
    user = next((u for u in db.users if u.get("email") == identifier or u.get("studentId") == identifier), None)
    if not user:
        if hasattr(db, 'drivers'):
            user = next((d for d in db.drivers if d.get("email") == identifier or d.get("studentId") == identifier), None)
            
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")"""

import re
content = re.sub(r'@router.post\("/login"\)\ndef login\(req: LoginRequest\):\n    db = get_db\(\)\n        \n    # Find user by email\n    user = next\(\(u for u in db.users if u.get\("email"\) == req.email\), None\)\n    if not user:\n        if hasattr\(db, \'drivers\'\):\n            user = next\(\(d for d in db.drivers if d.get\("email"\) == req.email\), None\)\n                \n    if not user:\n        raise HTTPException\(status_code=401, detail="Incorrect credentials"\)', replacement_logic, content)

with open('backend/app/api/auth.py', 'w') as f:
    f.write(content)
