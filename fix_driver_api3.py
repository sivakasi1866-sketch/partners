import re

with open("src/components/driver/DriverDashboard.tsx", "r") as f:
    content = f.read()

# Completely rewrite handleNextStop
new_next_stop = """  const handleNextStop = async () => {
    if (!activeTrip) return;
    setIsLoading(true);
    try {
      const route = routes.find(r => r.id === activeTrip.routeId);
      if (!route) return;
      const nextIndex = activeTrip.nextStopIndex;
      if (nextIndex < route.stops.length) {
        const nextStopData = route.stops[nextIndex];
        await api.updateGPS({ 
            tripId: activeTrip.id, 
            driverId: currentUser.id, 
            latitude: nextStopData.latitude, 
            longitude: nextStopData.longitude, 
            timestamp: new Date().toISOString() 
        });
      } else {
        await handleStopTrip();
      }
      await onRefreshData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };"""

content = re.sub(
    r"  const handleNextStop = async \(\) => \{.*?^\s*  \};" ,
    new_next_stop,
    content,
    flags=re.DOTALL | re.MULTILINE
)

with open("src/components/driver/DriverDashboard.tsx", "w") as f:
    f.write(content)

print("DriverDashboard API calls fixed round 3")
