import re

with open('src/components/Login.tsx', 'r') as f:
    content = f.read()

# Replace state variables
state_vars = """  const [rollNumber, setRollNumber] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');"""
content = re.sub(r'  const \[rollNumber, setRollNumber\] = useState\(\'\'\);\n  const \[password, setPassword\] = useState\(\'\'\);\n  const \[showPassword, setShowPassword\] = useState\(false\);\n  const \[isLoading, setIsLoading\] = useState\(false\);', state_vars, content)

# Replace handleSubmit
submit_logic = """  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    
    if (!rollNumber.trim()) {
      setErrorMsg("Please enter your roll number");
      return;
    }
    
    if (!password.trim()) {
      setErrorMsg("Please enter your password");
      return;
    }
    
    setIsLoading(true);
    try {
      const res = await api.login(rollNumber.trim(), password);
      if (res.user) {
        onLogin(res.user);
      }
    } catch (e) {
      console.error(e);
      setErrorMsg("Login failed. Please check credentials.");
    } finally {
      setIsLoading(false);
    }
  };"""

content = re.sub(r'  const handleSubmit = async \(e: React\.FormEvent\) => \{\n    e\.preventDefault\(\);\n    setIsLoading\(true\);\n    try \{\n      const res = await api\.login\(rollNumber, password\);\n      if \(res\.user\) \{\n        onLogin\(res\.user\);\n      \}\n    \} catch \(e\) \{\n      console\.error\(e\);\n      alert\("Login failed\. Please check credentials\."\);\n    \} finally \{\n      setIsLoading\(false\);\n    \}\n  \};', submit_logic, content)

# Add error message rendering
error_ui = """          <form className="space-y-6" onSubmit={handleSubmit}>
            {errorMsg && (
              <div className="p-3 rounded-md bg-red-50 text-red-600 text-sm font-medium border border-red-200">
                {errorMsg}
              </div>
            )}
            <div>"""

content = content.replace('          <form className="space-y-6" onSubmit={handleSubmit}>\n            <div>', error_ui)

with open('src/components/Login.tsx', 'w') as f:
    f.write(content)
