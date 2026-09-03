import { RawTripTelemetrySample } from './types';
import { db } from '../db';
import { Route, RouteStop, TrafficLevel } from '../../src/types';
import { calculateDistanceKm } from '../ml-predictor';

/**
 * DEVELOPMENT/TRAINING DATASET GENERATOR
 *
 * Explicit Classification: SYNTHETIC DEVELOPMENT DATASET
 *
 * Generates high-fidelity physics-based campus transit telemetry across all 4 campus routes:
 * - Route 1: North Hostel to Science & Tech Quad (7.4 km, 7 stops)
 * - Route 2: Metro Link & Faculty Express (11.2 km, 8 stops)
 * - Route 3: South Campus & Research Park Loop (9.5 km, 8 stops)
 * - Route 4: West Campus Dorms to Sports Complex (5.8 km, 5 stops)
 *
 * Simulates:
 * 1. Morning, Lunch, Evening, and Off-Peak traffic rhythms.
 * 2. Weather events (Clear, Rain, Fog).
 * 3. Realistic passenger boarding/alighting distributions per stop type (Hostels, Dining, Classrooms).
 * 4. Road segment speed limits, traffic signal delays, and bus stops dwell times.
 * 5. Deterministic random seed for 100% reproducible data generation.
 */

// Simple Linear Congruential Generator (LCG) for reproducible pseudorandom numbers
class SeededRandom {
  private state: number;

  constructor(seed: number = 42) {
    this.state = seed % 2147483647;
    if (this.state <= 0) this.state += 2147483646;
  }

  public next(): number {
    this.state = (this.state * 16807) % 2147483647;
    return (this.state - 1) / 2147483646;
  }

  public nextRange(min: number, max: number): number {
    return min + this.next() * (max - min);
  }

  public nextInt(min: number, max: number): number {
    return Math.floor(this.nextRange(min, max + 1));
  }

  public nextGaussian(mean: number = 0, stdev: number = 1): number {
    let u1 = this.next();
    let u2 = this.next();
    while (u1 === 0) u1 = this.next();
    const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    return z0 * stdev + mean;
  }
}

export function generateSyntheticTransitDataset(
  numTripsPerRoute: number = 75,
  seed: number = 20260830
): {
  dataset: RawTripTelemetrySample[];
  metadata: {
    totalSamples: number;
    totalTrips: number;
    routesRepresented: string[];
    dateRangeStart: string;
    dateRangeEnd: string;
    datasetType: string;
    version: string;
  };
} {
  const rng = new SeededRandom(seed);
  const samples: RawTripTelemetrySample[] = [];

  const routes = db.routes;
  const buses = db.buses;
  const drivers = db.drivers;

  // Simulate 14 consecutive days of campus bus operations (Starting 2026-08-01)
  const baseStartDate = new Date('2026-08-01T06:30:00.000Z');
  let globalSampleIndex = 0;
  let totalTripsGenerated = 0;

  routes.forEach((route) => {
    for (let tripIdx = 0; tripIdx < numTripsPerRoute; tripIdx++) {
      totalTripsGenerated++;
      const tripId = `synth-trip-${route.routeNumber}-${tripIdx + 1}`;
      const bus = buses[tripIdx % buses.length];
      const driver = drivers[tripIdx % drivers.length];

      // Time distribution: Day 0 to 13, Hours 07:00 to 21:00
      const dayOffset = Math.floor((tripIdx / numTripsPerRoute) * 14);
      const hourOfDay = rng.nextInt(7, 20);
      const minuteOfHour = rng.nextInt(0, 59);

      const tripStartDate = new Date(baseStartDate.getTime());
      tripStartDate.setUTCDate(tripStartDate.getUTCDate() + dayOffset);
      tripStartDate.setUTCHours(hourOfDay, minuteOfHour, 0, 0);

      const dayOfWeek = tripStartDate.getUTCDay();
      const isWeekend = dayOfWeek === 0 || dayOfWeek === 6 ? 1 : 0;

      // Weather probability (75% Clear, 15% Rain, 10% Fog)
      const weatherRoll = rng.next();
      const weatherCondition: 'clear' | 'rain' | 'fog' =
        weatherRoll < 0.75 ? 'clear' : weatherRoll < 0.9 ? 'rain' : 'fog';

      const weatherSpeedFactor = weatherCondition === 'rain' ? 0.85 : weatherCondition === 'fog' ? 0.9 : 1.0;

      // Determine time of day peak traffic factor
      const timeVal = hourOfDay + minuteOfHour / 60;
      let isPeak = 0;
      let trafficLevel: TrafficLevel = 'low';

      if (!isWeekend) {
        if (timeVal >= 8.0 && timeVal <= 9.5) {
          isPeak = 1;
          trafficLevel = rng.next() < 0.7 ? 'heavy' : 'moderate';
        } else if (timeVal >= 12.5 && timeVal <= 14.0) {
          isPeak = 1;
          trafficLevel = rng.next() < 0.6 ? 'moderate' : 'heavy';
        } else if (timeVal >= 16.5 && timeVal <= 18.5) {
          isPeak = 1;
          trafficLevel = rng.next() < 0.75 ? 'heavy' : 'gridlock';
        } else {
          trafficLevel = rng.next() < 0.8 ? 'low' : 'moderate';
        }
      } else {
        trafficLevel = rng.next() < 0.85 ? 'low' : 'moderate';
      }

      const trafficSpeedFactor =
        trafficLevel === 'low' ? 1.0 :
        trafficLevel === 'moderate' ? 0.82 :
        trafficLevel === 'heavy' ? 0.60 : 0.42;

      // Passenger occupancy generation
      let basePassengers = 10;
      if (isPeak) basePassengers = Math.floor(bus.capacity * rng.nextRange(0.6, 0.95));
      else basePassengers = Math.floor(bus.capacity * rng.nextRange(0.15, 0.55));
      const passengerCount = Math.min(bus.capacity, Math.max(2, basePassengers));

      // Simulate step-by-step progress through stops to compute true ground truth arrival times
      const stops = route.stops;
      const stopArrivalTimes: number[] = []; // In minutes from trip start
      let cumulativeTimeMin = 0;

      // Stop 0 arrival is minute 0
      stopArrivalTimes.push(0);

      // Pre-compute actual travel time between stops using physics simulation + noise
      for (let s = 1; s < stops.length; s++) {
        const prevStop = stops[s - 1];
        const currentStop = stops[s];
        const distKm = calculateDistanceKm(prevStop.latitude, prevStop.longitude, currentStop.latitude, currentStop.longitude);

        // Base segment speed limit on campus (25-32 km/h)
        const segmentSpeedLimit = rng.nextRange(24, 30);
        const effectiveSpeed = Math.max(8, segmentSpeedLimit * trafficSpeedFactor * weatherSpeedFactor + rng.nextGaussian(0, 1.5));

        // Transit travel minutes: (dist / speed) * 60
        const segmentDriveMin = (distKm / effectiveSpeed) * 60;

        // Dwell time at prevStop (boarding/alighting: 0.3 to 1.2 minutes)
        const dwellTime = Math.max(0.2, (0.02 * passengerCount) + rng.nextRange(0.1, 0.4));

        cumulativeTimeMin += (segmentDriveMin + dwellTime);
        stopArrivalTimes.push(cumulativeTimeMin);
      }

      // Now generate telemetry sampling snapshots along the trip
      // We sample telemetry at 5 to 8 intermediate positions along the route
      for (let sIdx = 0; sIdx < stops.length - 1; sIdx++) {
        const originStop = stops[sIdx];
        const destStop = stops[sIdx + 1];
        const segmentDistKm = calculateDistanceKm(originStop.latitude, originStop.longitude, destStop.latitude, destStop.longitude);

        // Generate 2 observation snapshots per segment (at start and midway)
        const fractions = [0.05, 0.55];

        for (const frac of fractions) {
          globalSampleIndex++;
          const sampleId = `samp-${globalSampleIndex}`;

          // Interpolate GPS
          const currentLat = originStop.latitude + (destStop.latitude - originStop.latitude) * frac + rng.nextGaussian(0, 0.00005);
          const currentLng = originStop.longitude + (destStop.longitude - originStop.longitude) * frac + rng.nextGaussian(0, 0.00005);

          // Approximate current elapsed trip time
          const segmentStartTime = stopArrivalTimes[sIdx];
          const segmentEndTime = stopArrivalTimes[sIdx + 1];
          const currentElapsedMin = segmentStartTime + (segmentEndTime - segmentStartTime) * frac;

          // Snapshot speed
          const currentSpeedKmH = Math.max(5, Math.min(45, (segmentDistKm / ((segmentEndTime - segmentStartTime) / 60)) + rng.nextGaussian(0, 2)));

          // Calculate trip progress
          const totalRouteDistKm = route.totalDistanceKm || 7.0;
          const distCoveredEst = (sIdx + frac) * (totalRouteDistKm / stops.length);
          const tripProgressRatio = Math.min(1.0, distCoveredEst / totalRouteDistKm);

          // For every upcoming stop (from sIdx+1 to end), generate a prediction training record!
          for (let targetIdx = sIdx + 1; targetIdx < stops.length; targetIdx++) {
            const targetStop = stops[targetIdx];
            const trueTargetArrivalTimeMin = stopArrivalTimes[targetIdx];

            // TARGET VARIABLE: Remaining travel time from current observation to arrival at targetStop
            const actualRemainingTravelTimeMin = Math.max(0.1, trueTargetArrivalTimeMin - currentElapsedMin);

            // Distance from current position to target stop
            const distanceToStopKm = calculateDistanceKm(currentLat, currentLng, targetStop.latitude, targetStop.longitude);
            const stopsRemainingCount = targetIdx - sIdx;

            const sampleDate = new Date(tripStartDate.getTime() + currentElapsedMin * 60 * 1000);

            const sample: RawTripTelemetrySample = {
              sampleId: `${sampleId}-tgt-${targetStop.id}`,
              tripId,
              routeId: route.id,
              routeNumber: route.routeNumber,
              routeCategory: route.category || 'campus_express',
              busId: bus.id,
              busCapacity: bus.capacity,
              driverId: driver.id,
              timestamp: sampleDate.toISOString(),
              hourOfDay: sampleDate.getUTCHours(),
              minuteOfHour: sampleDate.getUTCMinutes(),
              dayOfWeek,
              isWeekend,
              currentLat,
              currentLng,
              currentSpeedKmH: parseFloat(currentSpeedKmH.toFixed(2)),
              trafficLevel,
              passengerCount,
              weatherCondition,
              targetStopId: targetStop.id,
              targetStopName: targetStop.stopName,
              targetStopSequence: targetStop.sequence,
              targetStopLat: targetStop.latitude,
              targetStopLng: targetStop.longitude,
              scheduledArrivalDeltaMin: targetStop.scheduledArrivalDeltaMin,
              distanceToStopKm: parseFloat(distanceToStopKm.toFixed(3)),
              stopsRemainingCount,
              tripElapsedMinutes: parseFloat(currentElapsedMin.toFixed(2)),
              tripProgressRatio: parseFloat(tripProgressRatio.toFixed(3)),
              actualRemainingTravelTimeMin: parseFloat(actualRemainingTravelTimeMin.toFixed(3))
            };

            samples.push(sample);
          }
        }
      }
    }
  });

  return {
    dataset: samples,
    metadata: {
      totalSamples: samples.length,
      totalTrips: totalTripsGenerated,
      routesRepresented: routes.map((r) => `${r.routeNumber} (${r.name})`),
      dateRangeStart: '2026-08-01T06:30:00.000Z',
      dateRangeEnd: '2026-08-14T21:30:00.000Z',
      datasetType: 'SYNTHETIC_DEVELOPMENT_TELEMETRY',
      version: '1.0.0-dev'
    }
  };
}
