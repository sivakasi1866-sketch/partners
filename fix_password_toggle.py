import re

with open('src/components/Login.tsx', 'r') as f:
    content = f.read()

# Replace lucide-react imports
content = content.replace(
    "import { ShieldCheck, Bus, KeyRound, Mail } from 'lucide-react';",
    "import { ShieldCheck, Bus, KeyRound, Mail, Eye, EyeOff } from 'lucide-react';"
)

# Insert showPassword state
state_insertion = """  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);"""
content = content.replace(
    "  const [password, setPassword] = useState('');\n  const [isLoading, setIsLoading] = useState(false);",
    state_insertion
)

# Replace password input field
old_password_field = """                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="block w-full rounded-md border-0 py-2.5 pl-10 text-slate-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                />"""

new_password_field = """                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="block w-full rounded-md border-0 py-2.5 pl-10 pr-10 text-slate-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-500 focus:outline-none"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" aria-hidden="true" />
                  ) : (
                    <Eye className="h-5 w-5" aria-hidden="true" />
                  )}
                </button>"""

content = content.replace(old_password_field, new_password_field)

with open('src/components/Login.tsx', 'w') as f:
    f.write(content)
