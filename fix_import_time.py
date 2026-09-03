with open('backend/app/api/trips.py', 'r') as f:
    code = f.read()

code = "import time\n" + code

with open('backend/app/api/trips.py', 'w') as f:
    f.write(code)
