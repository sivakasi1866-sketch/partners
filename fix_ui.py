import re

with open('src/components/Login.tsx', 'r') as f:
    content = f.read()

# 1. Update icon imports: replace Mail with IdCard
content = content.replace("Mail,", "IdCard,")
content = content.replace("Mail ", "IdCard ")

# 2. Update Label
content = content.replace(">Email Address<", ">Roll Number<")

# 3. Update Input field
content = content.replace('placeholder="admin@elite.edu"', 'placeholder="Enter your roll number"')
content = content.replace('<Mail className="h-5 w-5 text-gray-400" />', '<IdCard className="h-5 w-5 text-gray-400" />')

# Let's change the name and id of the input to rollNumber (the state variable we will use)
# Wait, actually let's use `identifier` for the state variable.

with open('src/components/Login.tsx', 'w') as f:
    f.write(content)
