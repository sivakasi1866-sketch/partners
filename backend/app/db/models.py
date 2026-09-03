from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    role = Column(String)  # admin, driver, student, staff
    department = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    driverLicense = Column(String, nullable=True)
    studentId = Column(String, nullable=True)
    staffId = Column(String, nullable=True)
    favoriteStopIds = Column(JSON, nullable=True)

class Bus(Base):
    __tablename__ = "buses"
    id = Column(String, primary_key=True, index=True)
    busNumber = Column(String)
    plateNumber = Column(String)
    model = Column(String)
    capacity = Column(Integer)
    currentOccupancy = Column(Integer, default=0)
    status = Column(String)
    assignedDriverId = Column(String, ForeignKey("users.id"), nullable=True)
    currentRouteId = Column(String, ForeignKey("routes.id"), nullable=True)
    fuelLevel = Column(Integer, nullable=True)
    lastInspectionDate = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    features = Column(JSON, nullable=True)

class Route(Base):
    __tablename__ = "routes"
    id = Column(String, primary_key=True, index=True)
    routeNumber = Column(String)
    name = Column(String)
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    estimatedDurationMin = Column(Integer, nullable=True)
    totalDistanceKm = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    frequencyMinutes = Column(Integer, nullable=True)
    operatingHours = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)
    pathCoordinates = Column(JSON, nullable=True)
    stops = relationship("Stop", back_populates="route", cascade="all, delete")

class Stop(Base):
    __tablename__ = "stops"
    id = Column(String, primary_key=True, index=True)
    route_id = Column(String, ForeignKey("routes.id", ondelete="CASCADE"))
    stopName = Column(String)
    code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    sequence = Column(Integer)
    scheduledArrivalDeltaMin = Column(Integer)
    landmark = Column(String, nullable=True)
    isHostel = Column(Boolean, default=False)
    isAcademicBlock = Column(Boolean, default=False)
    route = relationship("Route", back_populates="stops")

class Trip(Base):
    __tablename__ = "trips"
    id = Column(String, primary_key=True, index=True)
    busId = Column(String, ForeignKey("buses.id"))
    driverId = Column(String, ForeignKey("users.id"))
    routeId = Column(String, ForeignKey("routes.id"))
    status = Column(String, index=True)  # scheduled, in_progress, completed
    startTime = Column(String)
    endTime = Column(String, nullable=True)
    gpsActive = Column(Boolean, default=False)
    currentLatitude = Column(Float, nullable=True)
    currentLongitude = Column(Float, nullable=True)
    currentStopIndex = Column(Integer, default=0)
    nextStopIndex = Column(Integer, default=1)
    passengerCount = Column(Integer, default=0)
    distanceCoveredKm = Column(Float, default=0)
    speedKmH = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    lastLocationUpdateTime = Column(String, nullable=True)

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(String, primary_key=True, index=True)
    trip_id = Column(String, ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    bus_id = Column(String, ForeignKey("buses.id"))
    route_id = Column(String, ForeignKey("routes.id"))
    driver_id = Column(String, ForeignKey("users.id"))
    timestamp = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    speed_kmh = Column(Float, nullable=True)
    gps_accuracy_m = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    trip_status = Column(String)

class StopEvent(Base):
    __tablename__ = "stop_events"
    id = Column(String, primary_key=True, index=True)
    trip_id = Column(String, ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    route_id = Column(String, ForeignKey("routes.id"))
    stop_id = Column(String, ForeignKey("stops.id"))
    arrival_timestamp = Column(String, index=True)
    event_type = Column(String)

