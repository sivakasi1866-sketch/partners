import re

with open('src/services/api.ts', 'r') as f:
    content = f.read()

# Update login to take identifier instead of email
content = content.replace('async login(email: string, password: string = "password123")', 'async login(roll_number: string, password: string = "password123")')
content = content.replace('body: JSON.stringify({ email, password })', 'body: JSON.stringify({ roll_number, password })')

with open('src/services/api.ts', 'w') as f:
    f.write(content)
