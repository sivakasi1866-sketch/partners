import re

with open('backend/app/api/auth.py', 'r') as f:
    content = f.read()

# Replace LoginRequest
replacement_model = """class LoginRequest(BaseModel):
    identifier: str
    password: str"""
content = re.sub(r'class LoginRequest\(BaseModel\):\n    email: str = None\n    roll_number: str = None\n    password: str', replacement_model, content)

# Replace login logic
replacement_logic = """@router.post("/login")
def login(req: LoginRequest):
    db = get_db()
    
    identifier = req.identifier
    if not identifier:
        raise HTTPException(status_code=400, detail="Missing login identifier")
        
    # Find user by studentId, staffId, or email (for admins/drivers only)
    user = next((u for u in db.users if 
                 u.get("studentId") == identifier or 
                 u.get("staffId") == identifier or 
                 (u.get("email") == identifier and u.get("role") not in ["student", "staff"])), None)
                 
    if not user:
        if hasattr(db, 'drivers'):
            user = next((d for d in db.drivers if d.get("email") == identifier or d.get("staffId") == identifier), None)
            
    if not user:
        raise HTTPException(status_code=401, detail="Unable to sign in. Please check your User ID and password and try again.")
        
    if user.get("status") == "inactive":
        raise HTTPException(status_code=403, detail="User account is inactive")
        
    hashed_password = user.get("passwordHash")
    if not hashed_password:
        # Fallback for old records without passwordHash
        if req.password != "password123":
            raise HTTPException(status_code=401, detail="Unable to sign in. Please check your User ID and password and try again.")
    else:
        if not verify_password(req.password, hashed_password):
            raise HTTPException(status_code=401, detail="Unable to sign in. Please check your User ID and password and try again.")
            
    access_token = create_access_token(subject=user["id"], role=user.get("role", "student"))
    
    # Return user without password hash
    safe_user = user.copy()
    safe_user.pop("passwordHash", None)
    
    return {"access_token": access_token, "token_type": "bearer", "user": safe_user}"""

content = re.sub(r'@router\.post\("/login"\)\ndef login.*?return \{"access_token": access_token, "token_type": "bearer", "user": safe_user\}', replacement_logic, content, flags=re.DOTALL)

with open('backend/app/api/auth.py', 'w') as f:
    f.write(content)
