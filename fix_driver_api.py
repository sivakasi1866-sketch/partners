import os

with open("src/components/driver/DriverDashboard.tsx", "r") as f:
    content = f.read()

# Fix startTrip
content = content.replace(
    "await api.startTrip({\\n        routeId: selectedRouteId,\\n        busId: selectedBusId\\n      });",
    "await api.startTrip(currentUser.id, selectedBusId, selectedRouteId);"
)

# Fix stopTrip
content = content.replace(
    "await api.completeTrip(activeTrip.id);",
    "await api.stopTrip(activeTrip.id, currentUser.id);"
)

# Fix updateTripProgress
content = content.replace(
    "await api.updateTripProgress(activeTrip.id, nextIndex, nextIndex < route.stops.length - 1 ? nextIndex + 1 : nextIndex);",
    "await api.updateGPS({ tripId: activeTrip.id, driverId: currentUser.id, currentLatitude: activeTrip.currentLatitude, currentLongitude: activeTrip.currentLongitude, currentStopIndex: nextIndex, nextStopIndex: nextIndex < route.stops.length - 1 ? nextIndex + 1 : nextIndex });"
)

with open("src/components/driver/DriverDashboard.tsx", "w") as f:
    f.write(content)

print("DriverDashboard API calls fixed")
