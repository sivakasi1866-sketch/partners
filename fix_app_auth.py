import re

with open('src/App.tsx', 'r') as f:
    content = f.read()

old_users_state = """  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User>(DEFAULT_INITIAL_USER);
  const [users, setUsers] = useState<User[]>([DEFAULT_INITIAL_USER]);"""

new_users_state = """  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);"""

content = content.replace(old_users_state, new_users_state)

old_init = """  useEffect(() => {
    const initUsers = async () => {
      try {
        const res = await api.getCurrentUser();
        if (res && res.allAvailableUsers) {
          setUsers(res.allAvailableUsers);
          if (!isAuthenticated) {
            const student = res.allAvailableUsers.find(u => u.role === 'student') || res.allAvailableUsers[0];
            setCurrentUser(student);
          }
        }
      } catch (e) { console.error(e); }
    };
    initUsers();
    fetchFullState();
    const interval = setInterval(fetchFullState, 15000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);"""

new_init = """  useEffect(() => {
    const initAuth = async () => {
      try {
        const res = await api.getCurrentUser();
        if (res && res.user) {
          setCurrentUser(res.user);
          setIsAuthenticated(true);
        }
      } catch (e) {
        console.error("Auth check failed:", e);
      }
    };
    initAuth();
  }, []);

  useEffect(() => {
    if (!isAuthenticated) return;
    fetchFullState();
    const interval = setInterval(fetchFullState, 15000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);"""

content = content.replace(old_init, new_init)

old_login_comp = """  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} availableUsers={users} />;
  }"""

new_login_comp = """  if (!isAuthenticated || !currentUser) {
    return <Login onLogin={handleLogin} />;
  }"""

content = content.replace(old_login_comp, new_login_comp)

content = content.replace("DEFAULT_INITIAL_USER", "DEFAULT_INITIAL_USER_UNUSED")

with open('src/App.tsx', 'w') as f:
    f.write(content)
