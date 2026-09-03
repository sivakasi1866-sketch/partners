import { RawTripTelemetrySample, FeatureDefinition, MLFeatureVector } from './types';
import { TrafficLevel } from '../../src/types';

/**
 * Standard Scaler for Feature Normalization (Z-score: (x - mean) / std)
 */
export class FeatureScaler {
  public means: number[] = [];
  public stds: number[] = [];

  constructor(means?: number[], stds?: number[]) {
    if (means && stds) {
      this.means = means;
      this.stds = stds;
    }
  }

  public fit(matrix: number[][]): void {
    const numFeatures = matrix[0].length;
    const numSamples = matrix.length;

    this.means = new Array(numFeatures).fill(0);
    this.stds = new Array(numFeatures).fill(0);

    for (let j = 0; j < numFeatures; j++) {
      let sum = 0;
      for (let i = 0; i < numSamples; i++) {
        sum += matrix[i][j];
      }
      this.means[j] = sum / numSamples;

      let sumSqDiff = 0;
      for (let i = 0; i < numSamples; i++) {
        sumSqDiff += Math.pow(matrix[i][j] - this.means[j], 2);
      }
      const variance = sumSqDiff / Math.max(1, numSamples - 1);
      this.stds[j] = Math.sqrt(variance) || 1e-6; // Guard against division by zero
    }
  }

  public transformVector(vector: number[]): number[] {
    return vector.map((val, idx) => {
      const mean = this.means[idx] ?? 0;
      const std = this.stds[idx] || 1;
      return (val - mean) / std;
    });
  }

  public transformMatrix(matrix: number[][]): number[][] {
    return matrix.map((row) => this.transformVector(row));
  }
}

/**
 * FEATURE DEFINITIONS REPOSITORY
 */
export const ML_FEATURE_DEFINITIONS: FeatureDefinition[] = [
  {
    name: 'distance_to_stop_km',
    index: 0,
    type: 'continuous',
    description: 'Direct geodesic & road network distance to target arrival stop in km',
    source: 'GPS Telemetry & Campus GIS Waypoints',
    leakageRisk: 'NONE'
  },
  {
    name: 'stops_remaining_count',
    index: 1,
    type: 'discrete',
    description: 'Number of intermediate stop waypoints remaining before target stop',
    source: 'Route Schema & Active Stop Index',
    leakageRisk: 'NONE'
  },
  {
    name: 'current_speed_kmh',
    index: 2,
    type: 'continuous',
    description: 'Current instantaneous speed of the transit shuttle in km/h',
    source: 'Driver Mobile Telematics',
    leakageRisk: 'NONE'
  },
  {
    name: 'speed_to_limit_ratio',
    index: 3,
    type: 'continuous',
    description: 'Ratio of current vehicle speed relative to campus speed limit (25 km/h)',
    source: 'Derived: current_speed / 25.0',
    leakageRisk: 'NONE'
  },
  {
    name: 'traffic_level_encoded',
    index: 4,
    type: 'categorical',
    description: 'Ordinal road congestion factor (0=low, 1=moderate, 2=heavy, 3=gridlock)',
    source: 'Driver Console & Campus Traffic Sensors',
    leakageRisk: 'NONE'
  },
  {
    name: 'traffic_multiplier',
    index: 5,
    type: 'continuous',
    description: 'Continuous impedance multiplier on segment kinematics (1.0 to 2.4)',
    source: 'Derived Traffic Mapping',
    leakageRisk: 'NONE'
  },
  {
    name: 'passenger_count',
    index: 6,
    type: 'discrete',
    description: 'Live onboard passenger occupancy headcount',
    source: 'Driver Passenger Counter',
    leakageRisk: 'NONE'
  },
  {
    name: 'passenger_load_ratio',
    index: 7,
    type: 'continuous',
    description: 'Occupancy load factor relative to bus maximum seating capacity',
    source: 'Derived: passenger_count / capacity',
    leakageRisk: 'NONE'
  },
  {
    name: 'dwell_time_estimate_min',
    index: 8,
    type: 'continuous',
    description: 'Estimated cumulative passenger boarding and alighting dwell time across intermediate stops',
    source: 'Derived: stops_remaining * (0.35 + 0.015 * passengers)',
    leakageRisk: 'NONE'
  },
  {
    name: 'hour_of_day',
    index: 9,
    type: 'discrete',
    description: 'Hour component of observation timestamp (0-23 UTC)',
    source: 'Telemetry Timestamp',
    leakageRisk: 'NONE'
  },
  {
    name: 'minute_of_hour',
    index: 10,
    type: 'discrete',
    description: 'Minute component of observation timestamp (0-59 UTC)',
    source: 'Telemetry Timestamp',
    leakageRisk: 'NONE'
  },
  {
    name: 'time_of_day_normalized',
    index: 11,
    type: 'continuous',
    description: 'Fractional time of day representing diurnal cycle [0.0 - 1.0]',
    source: 'Derived: (hour * 60 + minute) / 1440',
    leakageRisk: 'NONE'
  },
  {
    name: 'is_peak_hour',
    index: 12,
    type: 'binary',
    description: 'Indicator for university class bell transitions (08:00-09:30, 12:30-14:00, 16:30-18:30)',
    source: 'Institutional Academic Schedule',
    leakageRisk: 'NONE'
  },
  {
    name: 'day_of_week',
    index: 13,
    type: 'discrete',
    description: 'Day of the week (0=Sunday, 1=Monday ... 6=Saturday)',
    source: 'Telemetry Timestamp',
    leakageRisk: 'NONE'
  },
  {
    name: 'is_weekend',
    index: 14,
    type: 'binary',
    description: 'Binary flag for Saturday or Sunday transit schedules (1=weekend, 0=weekday)',
    source: 'Derived Calendar',
    leakageRisk: 'NONE'
  },
  {
    name: 'weather_encoded',
    index: 15,
    type: 'categorical',
    description: 'Weather condition code (0=clear, 1=fog, 2=rain)',
    source: 'Campus Weather Station',
    leakageRisk: 'NONE'
  },
  {
    name: 'weather_multiplier',
    index: 16,
    type: 'continuous',
    description: 'Traction and visibility speed dampening factor (1.0 to 1.25)',
    source: 'Derived Weather Surface Coefficient',
    leakageRisk: 'NONE'
  },
  {
    name: 'route_category_encoded',
    index: 17,
    type: 'categorical',
    description: 'Route profile category (0=hostel_shuttle, 1=campus_express, 2=city_commuter, 3=night_owl)',
    source: 'Route Metadata',
    leakageRisk: 'NONE'
  },
  {
    name: 'trip_elapsed_minutes',
    index: 18,
    type: 'continuous',
    description: 'Total active minutes elapsed since bus departed origin terminal',
    source: 'Trip Active Runtime Telemetry',
    leakageRisk: 'NONE'
  },
  {
    name: 'trip_progress_ratio',
    index: 19,
    type: 'continuous',
    description: 'Ratio of total route distance completed [0.0 to 1.0]',
    source: 'Derived: distance_covered / total_route_km',
    leakageRisk: 'NONE'
  }
];

/**
 * Transforms raw telemetry or runtime query state into the clean 20-dimensional feature vector
 */
export function extractFeatureVector(sample: {
  distanceToStopKm: number;
  stopsRemainingCount: number;
  currentSpeedKmH: number;
  trafficLevel: TrafficLevel | string;
  passengerCount: number;
  busCapacity: number;
  hourOfDay: number;
  minuteOfHour: number;
  dayOfWeek: number;
  isWeekend: number;
  weatherCondition: 'clear' | 'rain' | 'fog' | string;
  routeCategory: string;
  tripElapsedMinutes: number;
  tripProgressRatio: number;
}): number[] {
  const distKm = Math.max(0.01, sample.distanceToStopKm || 0.1);
  const stopsRem = Math.max(0, sample.stopsRemainingCount || 1);
  const speed = Math.max(5, Math.min(60, sample.currentSpeedKmH || 24));
  const speedRatio = speed / 25.0;

  // Traffic encoding
  let trafficCode = 1; // moderate
  let trafficMult = 1.25;
  const tLevel = String(sample.trafficLevel || '').toLowerCase();
  if (tLevel === 'low') {
    trafficCode = 0;
    trafficMult = 1.0;
  } else if (tLevel === 'moderate') {
    trafficCode = 1;
    trafficMult = 1.25;
  } else if (tLevel === 'heavy') {
    trafficCode = 2;
    trafficMult = 1.65;
  } else if (tLevel === 'gridlock') {
    trafficCode = 3;
    trafficMult = 2.4;
  }

  const passCount = Math.max(0, sample.passengerCount || 15);
  const capacity = Math.max(20, sample.busCapacity || 45);
  const loadRatio = Math.min(1.5, passCount / capacity);

  // Dwell time estimation
  const dwellEstimate = stopsRem * (0.35 + 0.015 * passCount);

  const hour = Math.max(0, Math.min(23, sample.hourOfDay || 12));
  const minute = Math.max(0, Math.min(59, sample.minuteOfHour || 0));
  const timeNorm = (hour * 60 + minute) / 1440.0;

  // Peak hour
  const timeVal = hour + minute / 60.0;
  let isPeak = 0;
  if (sample.isWeekend !== 1) {
    if ((timeVal >= 8.0 && timeVal <= 9.5) || (timeVal >= 12.5 && timeVal <= 14.0) || (timeVal >= 16.5 && timeVal <= 18.5)) {
      isPeak = 1;
    }
  }

  const dow = Math.max(0, Math.min(6, sample.dayOfWeek ?? 1));
  const isWknd = sample.isWeekend === 1 ? 1 : 0;

  // Weather encoding
  let weatherCode = 0;
  let weatherMult = 1.0;
  const wCond = String(sample.weatherCondition || '').toLowerCase();
  if (wCond === 'fog') {
    weatherCode = 1;
    weatherMult = 1.15;
  } else if (wCond === 'rain') {
    weatherCode = 2;
    weatherMult = 1.25;
  }

  // Route category
  let routeCatCode = 1;
  const rCat = String(sample.routeCategory || '').toLowerCase();
  if (rCat === 'hostel_shuttle') routeCatCode = 0;
  else if (rCat === 'campus_express') routeCatCode = 1;
  else if (rCat === 'city_commuter') routeCatCode = 2;
  else if (rCat === 'night_owl') routeCatCode = 3;

  const elapsed = Math.max(0, sample.tripElapsedMinutes || 5);
  const progress = Math.max(0, Math.min(1.0, sample.tripProgressRatio || 0.3));

  return [
    distKm,             // 0: distance_to_stop_km
    stopsRem,           // 1: stops_remaining_count
    speed,              // 2: current_speed_kmh
    speedRatio,         // 3: speed_to_limit_ratio
    trafficCode,        // 4: traffic_level_encoded
    trafficMult,        // 5: traffic_multiplier
    passCount,          // 6: passenger_count
    loadRatio,          // 7: passenger_load_ratio
    dwellEstimate,      // 8: dwell_time_estimate_min
    hour,               // 9: hour_of_day
    minute,             // 10: minute_of_hour
    timeNorm,           // 11: time_of_day_normalized
    isPeak,             // 12: is_peak_hour
    dow,                // 13: day_of_week
    isWknd,             // 14: is_weekend
    weatherCode,        // 15: weather_encoded
    weatherMult,        // 16: weather_multiplier
    routeCatCode,       // 17: route_category_encoded
    elapsed,            // 18: trip_elapsed_minutes
    progress            // 19: trip_progress_ratio
  ];
}

/**
 * Data Cleaning & Preprocessing Routine
 */
export function preprocessRawDataset(rawSamples: RawTripTelemetrySample[]): {
  cleanedVectors: MLFeatureVector[];
  report: {
    totalInputRecords: number;
    validRecordsRetained: number;
    recordsRemovedCount: number;
    removalReasons: Record<string, number>;
  };
} {
  const cleaned: MLFeatureVector[] = [];
  const removalReasons: Record<string, number> = {
    'Invalid Target Travel Time (<= 0 min)': 0,
    'Negative or Zero Distance': 0,
    'Unrealistic Vehicle Speed (> 80 km/h or < 0)': 0,
    'Corrupt/Missing GPS Coordinates': 0,
    'Outlier Travel Duration (> 120 min for campus)': 0
  };

  for (const s of rawSamples) {
    if (!s.actualRemainingTravelTimeMin || s.actualRemainingTravelTimeMin <= 0) {
      removalReasons['Invalid Target Travel Time (<= 0 min)']++;
      continue;
    }
    if (s.actualRemainingTravelTimeMin > 120) {
      removalReasons['Outlier Travel Duration (> 120 min for campus)']++;
      continue;
    }
    if (s.distanceToStopKm <= 0) {
      removalReasons['Negative or Zero Distance']++;
      continue;
    }
    if (s.currentSpeedKmH < 0 || s.currentSpeedKmH > 80) {
      removalReasons['Unrealistic Vehicle Speed (> 80 km/h or < 0)']++;
      continue;
    }
    if (isNaN(s.currentLat) || isNaN(s.currentLng) || Math.abs(s.currentLat) > 90 || Math.abs(s.currentLng) > 180) {
      removalReasons['Corrupt/Missing GPS Coordinates']++;
      continue;
    }

    const featureArray = extractFeatureVector({
      distanceToStopKm: s.distanceToStopKm,
      stopsRemainingCount: s.stopsRemainingCount,
      currentSpeedKmH: s.currentSpeedKmH,
      trafficLevel: s.trafficLevel,
      passengerCount: s.passengerCount,
      busCapacity: s.busCapacity,
      hourOfDay: s.hourOfDay,
      minuteOfHour: s.minuteOfHour,
      dayOfWeek: s.dayOfWeek,
      isWeekend: s.isWeekend,
      weatherCondition: s.weatherCondition,
      routeCategory: s.routeCategory,
      tripElapsedMinutes: s.tripElapsedMinutes,
      tripProgressRatio: s.tripProgressRatio
    });

    cleaned.push({
      sampleId: s.sampleId,
      tripId: s.tripId,
      routeNumber: s.routeNumber,
      timestamp: s.timestamp,
      features: featureArray,
      target: s.actualRemainingTravelTimeMin
    });
  }

  const totalRemoved = Object.values(removalReasons).reduce((a, b) => a + b, 0);

  return {
    cleanedVectors: cleaned,
    report: {
      totalInputRecords: rawSamples.length,
      validRecordsRetained: cleaned.length,
      recordsRemovedCount: totalRemoved,
      removalReasons
    }
  };
}
