with open('src/App.tsx', 'r') as f:
    content = f.read()

# Fix users init
old_users = """
  useEffect(() => {
    fetchUsers();
    fetchFullState();
    const interval = setInterval(fetchFullState, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await api.getUsers();
      if (res.success && res.users) {
        setUsers(res.users);
        if (!isAuthenticated) {
            const student = res.users.find(u => u.role === 'student');
            if (student) setCurrentUser(student);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };
"""

new_users = """
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
content = content.replace(old_users.strip(), new_users.strip())

# Fix fetch responses
old_fetch = """
      if (bRes.success) setBuses(bRes.buses || []);
      if (dRes.success) setDrivers(dRes.drivers || []);
      if (rRes.success) setRoutes(rRes.routes || []);
      if (tRes.success) setActiveTrips(tRes.trips || []);
      if (nRes.success) setNotifications(nRes.notifications || []);
"""
new_fetch = """
      if (bRes.buses) setBuses(bRes.buses);
      if (dRes.drivers) setDrivers(dRes.drivers);
      if (rRes.routes) setRoutes(rRes.routes);
      // NOTE: getActiveTrips returns { activeTrips: Trip[] }
      if (tRes.activeTrips) setActiveTrips(tRes.activeTrips);
      if (nRes.notifications) setNotifications(nRes.notifications);
"""
content = content.replace(old_fetch.strip(), new_fetch.strip())

with open('src/App.tsx', 'w') as f:
    f.write(content)
