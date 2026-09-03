import { Bus, Driver, Route, Trip, NotificationItem, SystemLog, User } from '../src/types';
import fs from 'fs';
import path from 'path';

const DATA_DIR = path.join(process.cwd(), 'server', 'data');
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Mock educational institution coordinates: "Elite Institute of Technology & Science"
// Centered around lat: 12.9716, lng: 77.5946 (or customizable campus grid)
export const CAMPUS_CENTER = { lat: 12.9716, lng: 77.5946 };

export class MockDatabase {
  realTelemetry: any[] = [];
  realStopEvents: any[] = [];

  constructor() {
    const telemetryPath = path.join(DATA_DIR, 'telemetry.json');
    const stopEventsPath = path.join(DATA_DIR, 'stop_events.json');
    if (fs.existsSync(telemetryPath)) {
      try {
        this.realTelemetry = JSON.parse(fs.readFileSync(telemetryPath, 'utf8'));
      } catch (e) { console.error('Failed to load telemetry', e); }
    }
    const tripsPath = path.join(DATA_DIR, 'trips.json');
    if (fs.existsSync(tripsPath)) {
      try {
        this.trips = JSON.parse(fs.readFileSync(tripsPath, 'utf8'));
      } catch (e) { console.error('Failed to load trips', e); }
    }
    if (fs.existsSync(stopEventsPath)) {
      try {
        this.realStopEvents = JSON.parse(fs.readFileSync(stopEventsPath, 'utf8'));
      } catch (e) { console.error('Failed to load stop events', e); }
    }
  }

  persistTrips() {
    fs.writeFileSync(path.join(DATA_DIR, 'trips.json'), JSON.stringify(this.trips, null, 2));
  }

  saveTelemetry(record: any) {
    this.realTelemetry.push(record);
    fs.writeFileSync(path.join(DATA_DIR, 'telemetry.json'), JSON.stringify(this.realTelemetry, null, 2));
  }

  saveStopEvent(record: any) {
    this.realStopEvents.push(record);
    fs.writeFileSync(path.join(DATA_DIR, 'stop_events.json'), JSON.stringify(this.realStopEvents, null, 2));
  }
  users: User[] = [
    {
      id: 'usr-admin-1',
      name: 'Dr. Arthur Vance',
      email: 'transport.director@elite.edu',
      role: 'admin',
      department: 'Campus Transport Operations & Safety'
    },
    {
      id: 'usr-driver-1',
      name: 'Robert Jenkins',
      email: 'robert.j@elite.edu',
      role: 'driver',
      phone: '+1 (555) 234-8901',
      driverLicense: 'DL-98234-COM',
      assignedBusId: 'bus-101',
      assignedRouteId: 'route-1'
    },
    {
      id: 'usr-driver-2',
      name: 'Marcus Henderson',
      email: 'marcus.h@elite.edu',
      role: 'driver',
      phone: '+1 (555) 345-6789',
      driverLicense: 'DL-77412-COM',
      assignedBusId: 'bus-102',
      assignedRouteId: 'route-2'
    },
    {
      id: 'usr-driver-3',
      name: 'Elena Rostova',
      email: 'elena.r@elite.edu',
      role: 'driver',
      phone: '+1 (555) 456-7890',
      driverLicense: 'DL-55219-COM',
      assignedBusId: 'bus-103',
      assignedRouteId: 'route-3'
    },
    {
      id: 'usr-student-1',
      name: 'Sophia Patel',
      email: 'sophia.patel@student.elite.edu',
      role: 'student',
      studentId: 'ST-2024-8841',
      department: 'Computer Science & AI',
      favoriteStopIds: ['stop-1-3', 'stop-1-5']
    },
    {
      id: 'usr-staff-1',
      name: 'Prof. Katherine Hayes',
      email: 'k.hayes@faculty.elite.edu',
      role: 'staff',
      staffId: 'FAC-4019',
      department: 'Department of Electrical Engineering',
      favoriteStopIds: ['stop-2-2', 'stop-2-5']
    }
  ];

  buses: Bus[] = [
    {
      id: 'bus-101',
      busNumber: 'BUS-01',
      plateNumber: 'ELT-BUS-101',
      model: 'Volvo 9400 B8R City Shuttle',
      capacity: 45,
      currentOccupancy: 28,
      status: 'in_service',
      assignedDriverId: 'usr-driver-1',
      currentRouteId: 'route-1',
      fuelLevel: 84,
      lastInspectionDate: '2026-08-15',
      year: 2024,
      features: ['Air Conditioned', 'Wheelchair Ramp', 'Wi-Fi 6', 'Security Cameras', 'USB Charging']
    },
    {
      id: 'bus-102',
      busNumber: 'BUS-02',
      plateNumber: 'ELT-BUS-102',
      model: 'Scania Metrolink HD',
      capacity: 50,
      currentOccupancy: 18,
      status: 'in_service',
      assignedDriverId: 'usr-driver-2',
      currentRouteId: 'route-2',
      fuelLevel: 72,
      lastInspectionDate: '2026-08-10',
      year: 2023,
      features: ['Air Conditioned', 'Wi-Fi 6', 'GPS Telematics', 'PA System']
    },
    {
      id: 'bus-103',
      busNumber: 'BUS-03',
      plateNumber: 'ELT-BUS-103',
      model: 'BYD K9 Electric Campus Shuttle',
      capacity: 40,
      currentOccupancy: 34,
      status: 'in_service',
      assignedDriverId: 'usr-driver-3',
      currentRouteId: 'route-3',
      fuelLevel: 91,
      lastInspectionDate: '2026-08-20',
      year: 2025,
      features: ['100% Electric (Zero Emission)', 'Air Conditioned', 'Low Floor Access', 'USB Charging']
    },
    {
      id: 'bus-104',
      busNumber: 'BUS-04',
      plateNumber: 'ELT-BUS-104',
      model: 'Tata Marcopolo Starbus Ultra',
      capacity: 35,
      currentOccupancy: 0,
      status: 'idle',
      fuelLevel: 60,
      lastInspectionDate: '2026-08-01',
      year: 2023,
      features: ['Standard Seating', 'CCTV']
    },
    {
      id: 'bus-105',
      busNumber: 'BUS-05',
      plateNumber: 'ELT-BUS-105',
      model: 'Volvo 9400 B8R City Shuttle',
      capacity: 45,
      currentOccupancy: 0,
      status: 'maintenance',
      fuelLevel: 45,
      lastInspectionDate: '2026-07-28',
      year: 2022,
      features: ['Under Brake Inspection']
    }
  ];

  drivers: Driver[] = [
    {
      id: 'usr-driver-1',
      name: 'Robert Jenkins',
      phone: '+1 (555) 234-8901',
      licenseNumber: 'DL-98234-COM',
      experienceYears: 8,
      rating: 4.9,
      status: 'on_trip',
      assignedBusId: 'bus-101',
      assignedRouteId: 'route-1',
      activeTripId: 'trip-101'
    },
    {
      id: 'usr-driver-2',
      name: 'Marcus Henderson',
      phone: '+1 (555) 345-6789',
      licenseNumber: 'DL-77412-COM',
      experienceYears: 12,
      rating: 4.8,
      status: 'on_trip',
      assignedBusId: 'bus-102',
      assignedRouteId: 'route-2',
      activeTripId: 'trip-102'
    },
    {
      id: 'usr-driver-3',
      name: 'Elena Rostova',
      phone: '+1 (555) 456-7890',
      licenseNumber: 'DL-55219-COM',
      experienceYears: 6,
      rating: 4.95,
      status: 'on_trip',
      assignedBusId: 'bus-103',
      assignedRouteId: 'route-3',
      activeTripId: 'trip-103'
    },
    {
      id: 'usr-driver-4',
      name: 'Devon Lee',
      phone: '+1 (555) 567-8901',
      licenseNumber: 'DL-33410-COM',
      experienceYears: 4,
      rating: 4.7,
      status: 'on_duty',
      assignedBusId: 'bus-104'
    }
  ];

  routes: Route[] = [
    {
      id: 'route-1',
      routeNumber: 'R-01',
      name: 'North Hostel to Science & Tech Quad',
      description: 'Primary residential express connecting North Dorms, Dining Hall, Central Library, and Science Complex.',
      color: '#3b82f6', // Blue
      origin: 'North Hostel Complex (Block A-D)',
      destination: 'Advanced Technology & Robotics Center',
      estimatedDurationMin: 22,
      totalDistanceKm: 7.4,
      category: 'hostel_shuttle',
      frequencyMinutes: 10,
      operatingHours: '06:30 AM - 10:30 PM',
      isActive: true,
      stops: [
        { id: 'stop-1-1', stopName: 'North Hostel Terminal (Gate 4)', code: 'NHT-01', latitude: 12.9850, longitude: 77.5850, sequence: 1, scheduledArrivalDeltaMin: 0, landmark: 'Opposite Student Dining Hall 3', isHostel: true },
        { id: 'stop-1-2', stopName: 'Olympic Sports Pavilion', code: 'OSP-02', latitude: 12.9800, longitude: 77.5890, sequence: 2, scheduledArrivalDeltaMin: 5, landmark: 'Aquatic Center & Track' },
        { id: 'stop-1-3', stopName: 'University Central Library', code: 'UCL-03', latitude: 12.9740, longitude: 77.5920, sequence: 3, scheduledArrivalDeltaMin: 10, landmark: 'Main Library Plaza East', isAcademicBlock: true },
        { id: 'stop-1-4', stopName: 'Administration & Student Center', code: 'ASC-04', latitude: 12.9700, longitude: 77.5950, sequence: 4, scheduledArrivalDeltaMin: 15, landmark: 'Clock Tower Circle' },
        { id: 'stop-1-5', stopName: 'Science & Engineering Quad', code: 'SEQ-05', latitude: 12.9650, longitude: 77.5990, sequence: 5, scheduledArrivalDeltaMin: 19, landmark: 'Newton Hall Front Courtyard', isAcademicBlock: true },
        { id: 'stop-1-6', stopName: 'Adv. Technology & Robotics Center', code: 'ATC-06', latitude: 12.9600, longitude: 77.6030, sequence: 6, scheduledArrivalDeltaMin: 22, landmark: 'Innovation Hub Gate', isAcademicBlock: true }
      ],
      pathCoordinates: [
        [12.9850, 77.5850],
        [12.9830, 77.5865],
        [12.9800, 77.5890],
        [12.9770, 77.5905],
        [12.9740, 77.5920],
        [12.9715, 77.5938],
        [12.9700, 77.5950],
        [12.9675, 77.5970],
        [12.9650, 77.5990],
        [12.9620, 77.6010],
        [12.9600, 77.6030]
      ]
    },
    {
      id: 'route-2',
      routeNumber: 'R-02',
      name: 'Metro Link & Faculty Express',
      description: 'Rapid transit route between Campus Main Gate, City Metro Station, Management School, and Faculty Residences.',
      color: '#10b981', // Emerald Green
      origin: 'University Metro Station Plaza',
      destination: 'Faculty Residential Enclave',
      estimatedDurationMin: 28,
      totalDistanceKm: 9.8,
      category: 'campus_express',
      frequencyMinutes: 15,
      operatingHours: '06:00 AM - 11:00 PM',
      isActive: true,
      stops: [
        { id: 'stop-2-1', stopName: 'University Metro Transit Center', code: 'MTC-01', latitude: 12.9550, longitude: 77.5800, sequence: 1, scheduledArrivalDeltaMin: 0, landmark: 'Metro Exit Gate 2 & Campus Shuttle Bay' },
        { id: 'stop-2-2', stopName: 'Main Campus Grand Arch (Gate 1)', code: 'MCG-02', latitude: 12.9620, longitude: 77.5870, sequence: 2, scheduledArrivalDeltaMin: 7, landmark: 'Visitor Center & Security', isCampusGate: true },
        { id: 'stop-2-3', stopName: 'School of Business & Economics', code: 'SBE-03', latitude: 12.9690, longitude: 77.5910, sequence: 3, scheduledArrivalDeltaMin: 14, landmark: 'Executive Auditorium', isAcademicBlock: true },
        { id: 'stop-2-4', stopName: 'University Medical & Health Clinic', code: 'UMC-04', latitude: 12.9720, longitude: 77.5980, sequence: 4, scheduledArrivalDeltaMin: 20, landmark: 'Emergency Wing Entrance' },
        { id: 'stop-2-5', stopName: 'Faculty Residential Enclave', code: 'FRE-05', latitude: 12.9780, longitude: 77.6050, sequence: 5, scheduledArrivalDeltaMin: 28, landmark: 'Clubhouse Roundabout' }
      ],
      pathCoordinates: [
        [12.9550, 77.5800],
        [12.9580, 77.5830],
        [12.9620, 77.5870],
        [12.9660, 77.5890],
        [12.9690, 77.5910],
        [12.9710, 77.5945],
        [12.9720, 77.5980],
        [12.9750, 77.6015],
        [12.9780, 77.6050]
      ]
    },
    {
      id: 'route-3',
      routeNumber: 'R-03',
      name: 'South Campus & Research Park Loop',
      description: 'Electric shuttle looping South Dormitories, Bio-Sciences Wing, Artificial Intelligence Center, and Food Street.',
      color: '#8b5cf6', // Violet
      origin: 'South Lake Hostel Complex',
      destination: 'AI & Data Science Institute',
      estimatedDurationMin: 18,
      totalDistanceKm: 6.2,
      category: 'campus_express',
      frequencyMinutes: 12,
      operatingHours: '07:00 AM - 10:00 PM',
      isActive: true,
      stops: [
        { id: 'stop-3-1', stopName: 'South Lake Hostels (Block G-K)', code: 'SLH-01', latitude: 12.9620, longitude: 77.6100, sequence: 1, scheduledArrivalDeltaMin: 0, landmark: 'Lakeside Walkway', isHostel: true },
        { id: 'stop-3-2', stopName: 'Student Activity & Food Pavilion', code: 'SFP-02', latitude: 12.9660, longitude: 77.6050, sequence: 2, scheduledArrivalDeltaMin: 5, landmark: 'Food Court & Bookstore' },
        { id: 'stop-3-3', stopName: 'Bio-Sciences & Chem Research Lab', code: 'BCR-03', latitude: 12.9700, longitude: 77.6020, sequence: 3, scheduledArrivalDeltaMin: 10, landmark: 'Franklin Laboratory', isAcademicBlock: true },
        { id: 'stop-3-4', stopName: 'AI & Data Science Institute', code: 'AID-04', latitude: 12.9750, longitude: 77.5980, sequence: 4, scheduledArrivalDeltaMin: 18, landmark: 'Turing Hall Main Entrance', isAcademicBlock: true }
      ],
      pathCoordinates: [
        [12.9620, 77.6100],
        [12.9640, 77.6075],
        [12.9660, 77.6050],
        [12.9680, 77.6035],
        [12.9700, 77.6020],
        [12.9725, 77.6000],
        [12.9750, 77.5980]
      ]
    }
  ];

  trips: Trip[] = [
    {
      id: 'trip-101',
      busId: 'bus-101',
      busNumber: 'BUS-01',
      driverId: 'usr-driver-1',
      driverName: 'Robert Jenkins',
      routeId: 'route-1',
      routeName: 'North Hostel to Science & Tech Quad',
      routeNumber: 'R-01',
      status: 'in_progress',
      startTime: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
      currentLatitude: 12.9740,
      currentLongitude: 77.5920,
      speedKmH: 26,
      heading: 145,
      currentStopIndex: 2,
      nextStopIndex: 3,
      delayMinutes: 2,
      trafficLevel: 'moderate',
      lastLocationUpdateTime: new Date().toISOString(),
      distanceCoveredKm: 3.8,
      passengerCount: 28,
      delayReason: 'Moderate queue at Library crosswalk',
      gpsActive: true
    },
    {
      id: 'trip-102',
      busId: 'bus-102',
      busNumber: 'BUS-02',
      driverId: 'usr-driver-2',
      driverName: 'Marcus Henderson',
      routeId: 'route-2',
      routeName: 'Metro Link & Faculty Express',
      routeNumber: 'R-02',
      status: 'in_progress',
      startTime: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
      currentLatitude: 12.9620,
      currentLongitude: 77.5870,
      speedKmH: 32,
      heading: 45,
      currentStopIndex: 1,
      nextStopIndex: 2,
      delayMinutes: 0,
      trafficLevel: 'low',
      lastLocationUpdateTime: new Date().toISOString(),
      distanceCoveredKm: 2.1,
      passengerCount: 18,
      gpsActive: true
    },
    {
      id: 'trip-103',
      busId: 'bus-103',
      busNumber: 'BUS-03',
      driverId: 'usr-driver-3',
      driverName: 'Elena Rostova',
      routeId: 'route-3',
      routeName: 'South Campus & Research Park Loop',
      routeNumber: 'R-03',
      status: 'in_progress',
      startTime: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
      currentLatitude: 12.9660,
      currentLongitude: 77.6050,
      speedKmH: 22,
      heading: 310,
      currentStopIndex: 1,
      nextStopIndex: 2,
      delayMinutes: 1,
      trafficLevel: 'low',
      lastLocationUpdateTime: new Date().toISOString(),
      distanceCoveredKm: 1.4,
      passengerCount: 34,
      gpsActive: true
    }
  ];

  notifications: NotificationItem[] = [
    {
      id: 'notif-1',
      title: 'Bus 01 Approaching Library',
      message: 'Bus 01 is 2 minutes away from University Central Library.',
      type: 'info',
      timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
      routeId: 'route-1',
      busId: 'bus-101',
      targetRole: 'all',
      isRead: false
    },
    {
      id: 'notif-2',
      title: 'Gate 2 Roadwork Advisory',
      message: 'Minor congestion near Gate 2 roundabout. Metro Express R-02 running with estimated 2-min delay buffer.',
      type: 'warning',
      timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
      routeId: 'route-2',
      targetRole: 'all',
      isRead: true
    },
    {
      id: 'notif-3',
      title: 'Privacy Protocol Check: 100% Compliant',
      message: 'System audit verified: Zero student or staff location data collected. GPS tracking strictly bound to active driver bus sessions.',
      type: 'success',
      timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      targetRole: 'admin',
      isRead: true
    }
  ];

  systemLogs: SystemLog[] = [
    {
      id: 'log-1',
      level: 'PRIVACY',
      message: 'Privacy Audit: Confirmed 0 student devices tracked. Client GPS collection disabled on Student & Staff views.',
      timestamp: new Date(Date.now() - 120 * 60 * 1000).toISOString(),
      actorRole: 'SYSTEM_AUDITOR'
    },
    {
      id: 'log-2',
      level: 'AUDIT',
      message: 'Driver Robert Jenkins started Trip trip-101 on Bus BUS-01 (Route R-01). Bus GPS stream initialized.',
      timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
      actorRole: 'driver',
      actorId: 'usr-driver-1'
    },
    {
      id: 'log-3',
      level: 'INFO',
      message: 'ML ETA Model recalculated predictions for 15 campus stops. Mean Absolute Error: 0.82 mins.',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      actorRole: 'ML_PIPELINE'
    }
  ];

  addLog(level: 'INFO' | 'WARN' | 'ERROR' | 'AUDIT' | 'PRIVACY', message: string, actorRole: string, actorId?: string, metadata?: any) {
    const log: SystemLog = {
      id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      level,
      message,
      timestamp: new Date().toISOString(),
      actorRole,
      actorId,
      metadata
    };
    this.systemLogs.unshift(log);
    if (this.systemLogs.length > 200) {
      this.systemLogs.pop();
    }
    return log;
  }
}

export const db = new MockDatabase();
