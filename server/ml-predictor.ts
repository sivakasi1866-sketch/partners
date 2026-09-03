import { Trip, Route, RouteStop, StopETA, TrafficLevel, MLPredictionModelStats } from '../src/types';
import { mlInferenceEngine } from './ml/inference-engine';

// Haversine distance in kilometers
export function calculateDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

export class MLEtaPredictor {
  /**
   * Predict ETA for all stops on an active trip using the trained ML model artifact
   */
  public predictTripStopETAs(
    trip: Trip,
    route: Route,
    weatherCondition: 'clear' | 'rain' | 'fog' = 'clear'
  ): StopETA[] {
    return mlInferenceEngine.predictTripStopETAs(trip, route, weatherCondition);
  }

  public getModelStats(): MLPredictionModelStats {
    return mlInferenceEngine.getModelStats();
  }
}

export const mlPredictor = new MLEtaPredictor();

