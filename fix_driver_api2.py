import re

with open("src/components/driver/DriverDashboard.tsx", "r") as f:
    content = f.read()

# Fix handleStartTrip
content = re.sub(
    r"await api\.startTrip\(\{.*?\}\);",
    "await api.startTrip(currentUser.id, selectedBusId, selectedRouteId);",
    content,
    flags=re.DOTALL
)

# Fix handleNextStop
content = re.sub(
    r"await api\.updateTripProgress\(.*?\);",
    "await api.updateGPS({ tripId: activeTrip.id, driverId: currentUser.id, latitude: activeTrip.currentLatitude, longitude: activeTrip.currentLongitude, currentStopIndex: nextIndex, nextStopIndex: nextIndex < route.stops.length - 1 ? nextIndex + 1 : nextIndex });",
    content,
    flags=re.DOTALL
)

with open("src/components/driver/DriverDashboard.tsx", "w") as f:
    f.write(content)

print("DriverDashboard API calls fixed round 2")
