export type UserRole = 'admin' | 'driver' | 'student' | 'staff';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  studentId?: string;
  staffId?: string;
  department?: string;
  driverLicense?: string;
  assignedRouteId?: string;
  assignedBusId?: string;
  favoriteStopIds?: string[];
  phone?: string;
}

export type BusStatus = 'in_service' | 'idle' | 'maintenance' | 'out_of_service';

export interface Bus {
  id: string;
  busNumber: string;
  plateNumber: string;
  model: string;
  capacity: number;
  currentOccupancy: number;
  status: BusStatus;
  assignedDriverId?: string;
  currentRouteId?: string;
  fuelLevel: number; // percentage 0-100
  lastInspectionDate: string;
  year: number;
  features: string[];
}

export type DriverStatus = 'on_duty' | 'off_duty' | 'on_trip' | 'break';

export interface Driver {
  id: string;
  name: string;
  phone: string;
  licenseNumber: string;
  experienceYears: number;
  rating: number;
  status: DriverStatus;
  assignedBusId?: string;
  assignedRouteId?: string;
  activeTripId?: string;
  photoUrl?: string;
}

export interface RouteStop {
  id: string;
  stopName: string;
  code: string;
  latitude: number;
  longitude: number;
  sequence: number;
  scheduledArrivalDeltaMin: number; // minutes from trip start
  landmark: string;
  isCampusGate?: boolean;
  isHostel?: boolean;
  isAcademicBlock?: boolean;
}

export type RouteCategory = 'campus_express' | 'hostel_shuttle' | 'city_commuter' | 'night_owl';

export interface Route {
  id: string;
  routeNumber: string;
  name: string;
  description: string;
  color: string;
  origin: string;
  destination: string;
  estimatedDurationMin: number;
  totalDistanceKm: number;
  stops: RouteStop[];
  pathCoordinates: [number, number][]; // [lat, lng] array
  category: RouteCategory;
  frequencyMinutes: number;
  operatingHours: string;
  isActive: boolean;
}

export type TripStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
export type TrafficLevel = 'low' | 'moderate' | 'heavy' | 'gridlock';

export interface Trip {
  id: string;
  busId: string;
  busNumber: string;
  driverId: string;
  driverName: string;
  routeId: string;
  routeName: string;
  routeNumber: string;
  status: TripStatus;
  startTime?: string;
  endTime?: string;
  currentLatitude?: number;
  currentLongitude?: number;
  speedKmH?: number;
  heading?: number;
  accuracy?: number | null;
  currentStopIndex: number;
  nextStopIndex: number;
  delayMinutes: number;
  trafficLevel: TrafficLevel;
  lastLocationUpdateTime?: string;
  distanceCoveredKm: number;
  passengerCount: number;
  delayReason?: string;
  gpsActive: boolean;
}

export interface StopETA {
  stopId: string;
  stopName: string;
  stopCode: string;
  sequence: number;
  latitude: number;
  longitude: number;
  scheduledArrivalTime: string;
  predictedArrivalTime: string;
  etaMinutes: number;
  confidenceScore: number; // 0 to 100
  distanceRemainingKm: number;
  trafficDelayMin: number;
  weatherImpactMin: number;
  status: 'passed' | 'approaching' | 'next' | 'scheduled';
  aiExplanation?: string;
}

export interface GPSUpdatePayload {
  tripId: string;
  driverId: string;
  latitude: number;
  longitude: number;
  speedKmH?: number;
  heading?: number;
  accuracy?: number | null;
  timestamp: string;
  accuracyMeters?: number;
}

export type NotificationType = 'info' | 'warning' | 'alert' | 'success';

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  timestamp: string;
  routeId?: string;
  busId?: string;
  targetRole?: UserRole | 'all';
  read?: boolean;
  isRead?: boolean;
}

export type Notification = NotificationItem;

export interface SystemLog {
  id: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'AUDIT' | 'PRIVACY';
  message: string;
  timestamp: string;
  actorRole: string;
  actorId?: string;
  metadata?: Record<string, any>;
}

export interface MLPredictionModelStats {
  modelName: string;
  version: string;
  meanAbsoluteErrorMin: number;
  accuracyScore: number;
  totalPredictionsToday: number;
  activeFeatures: string[];
  trafficCondition: TrafficLevel;
  weatherCondition: string;
  lastTrainedDate: string;
}

export interface PrivacyReport {
  studentsTrackedCount: number; // Always 0
  staffTrackedCount: number;    // Always 0
  activeBusGpsSessionsCount: number;
  gpsCollectedOnlyOnActiveTrip: boolean;
  zeroStudentLocationPolicyVerified: boolean;
  lastAuditTimestamp: string;
  complianceStatus: '100% COMPLIANT' | 'NON_COMPLIANT';
}

export interface RealBusTelemetryRecord {
  id: string;
  trip_id: string;
  bus_id: string;
  route_id: string;
  driver_id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  speed_kmh: number | null;
  gps_accuracy_m: number | null;
  heading: number | null;
  trip_status: string;
}

export interface RealStopEventRecord {
  id: string;
  trip_id: string;
  route_id: string;
  stop_id: string;
  event_type: 'ARRIVAL' | 'DEPARTURE';
  timestamp: string;
}
