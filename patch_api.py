with open('src/services/api.ts', 'r') as f:
    c = f.read()
c = c.replace('async login(roll_number: string, password: string = "password123")', 'async login(identifier: string, password: string = "password123")')
c = c.replace('body: JSON.stringify({ roll_number, password })', 'body: JSON.stringify({ identifier, password })')
with open('src/services/api.ts', 'w') as f:
    f.write(c)
