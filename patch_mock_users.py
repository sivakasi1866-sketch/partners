import json

with open('server/data/mock_db.json', 'r') as f:
    db = json.load(f)

for u in db['users']:
    if u['id'] == 'student-1':
        u['role'] = 'student'
        u['studentId'] = 'STU12345'
    elif u['id'] == 'staff-1':
        u['staffId'] = 'EMP98765'

with open('server/data/mock_db.json', 'w') as f:
    json.dump(db, f, indent=2)
