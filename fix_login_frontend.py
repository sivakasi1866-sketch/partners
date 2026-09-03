import re

with open('src/components/Login.tsx', 'r') as f:
    content = f.read()

content = content.replace("const [email, setEmail] = useState('');", "const [rollNumber, setRollNumber] = useState('');")
content = content.replace("onChange={(e) => setEmail(e.target.value)}", "onChange={(e) => setRollNumber(e.target.value)}")
content = content.replace('value={email}', 'value={rollNumber}')
content = content.replace('id="email"', 'id="rollNumber"')
content = content.replace('name="email"', 'name="rollNumber"')
content = content.replace('type="email"', 'type="text"')
content = content.replace('api.login(email, password)', 'api.login(rollNumber, password)')

with open('src/components/Login.tsx', 'w') as f:
    f.write(content)
