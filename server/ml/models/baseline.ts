import { MLFeatureVector } from '../types';

export class KinematicSpeedDistanceBaseline {
  public predict(features: number[]): number {
    const distanceKm = features[0]; // distance_to_stop_km
    const currentSpeed = Math.max(10, features[2]); // current_speed_kmh
    // Standard baseline: (distance / speed) * 60
    return Math.max(0.5, (distanceKm / currentSpeed) * 60);
  }

  public evaluate(testSet: MLFeatureVector[]): {
    mae: number;
    rmse: number;
    r2: number;
    medianAbsoluteError: number;
    accuracyWithin1Min: number;
    accuracyWithin3Min: number;
    accuracyWithin5Min: number;
  } {
    const errors: number[] = [];
    let sumSquaredError = 0;
    let sumAbsError = 0;
    let within1Count = 0;
    let within3Count = 0;
    let within5Count = 0;

    let targetSum = 0;
    for (const sample of testSet) {
      targetSum += sample.target;
    }
    const targetMean = targetSum / testSet.length;

    let totalSumSquares = 0;

    for (const sample of testSet) {
      const pred = this.predict(sample.features);
      const err = pred - sample.target;
      const absErr = Math.abs(err);

      errors.push(absErr);
      sumAbsError += absErr;
      sumSquaredError += err * err;
      totalSumSquares += Math.pow(sample.target - targetMean, 2);

      if (absErr <= 1.0) within1Count++;
      if (absErr <= 3.0) within3Count++;
      if (absErr <= 5.0) within5Count++;
    }

    errors.sort((a, b) => a - b);
    const mid = Math.floor(errors.length / 2);
    const medianAbsoluteError = errors.length % 2 !== 0 ? errors[mid] : (errors[mid - 1] + errors[mid]) / 2;

    const n = testSet.length;
    const mae = sumAbsError / n;
    const rmse = Math.sqrt(sumSquaredError / n);
    const r2 = 1 - sumSquaredError / Math.max(1e-6, totalSumSquares);

    return {
      mae: parseFloat(mae.toFixed(4)),
      rmse: parseFloat(rmse.toFixed(4)),
      r2: parseFloat(r2.toFixed(4)),
      medianAbsoluteError: parseFloat(medianAbsoluteError.toFixed(4)),
      accuracyWithin1Min: parseFloat(((within1Count / n) * 100).toFixed(2)),
      accuracyWithin3Min: parseFloat(((within3Count / n) * 100).toFixed(2)),
      accuracyWithin5Min: parseFloat(((within5Count / n) * 100).toFixed(2))
    };
  }
}
