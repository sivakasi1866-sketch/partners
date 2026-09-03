import os
import glob

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # DB user objects need email not identifier for seeding
    content = content.replace('"identifier": "student1@example.com", "passwordHash"', '"email": "student1@example.com", "passwordHash"')
    content = content.replace('"identifier": "student1@example.com", "passwordHash": hashed, "status": "active"', '"email": "student1@example.com", "passwordHash": hashed, "status": "active"')
    
    with open(filepath, 'w') as f:
        f.write(content)

test_files = glob.glob('backend/app/tests/test_*.py')
for tf in test_files:
    fix_file(tf)
    print(f"Fixed {tf}")
