with open('src/App.tsx', 'r') as f:
    content = f.read()

old_users = """
  useEffect(() => {
    const loadedUsers = api.allAvailableUsers;
    if (loadedUsers && loadedUsers.length > 0) {
      setUsers(loadedUsers);
      if (!isAuthenticated) {
        const student = loadedUsers.find(u => u.role === 'student') || loadedUsers[0];
        setCurrentUser(student);
      }
    }
    fetchFullState();
    const interval = setInterval(fetchFullState, 15000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);
"""

new_users = """
  useEffect(() => {
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
  }, [isAuthenticated]);
"""

content = content.replace(old_users.strip(), new_users.strip())
with open('src/App.tsx', 'w') as f:
    f.write(content)
