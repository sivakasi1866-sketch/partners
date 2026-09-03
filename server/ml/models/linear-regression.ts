import { MLFeatureVector } from '../types';
import { FeatureScaler } from '../feature-pipeline';

/**
 * Ridge Linear Regression (L2-Regularized)
 * Optimized via Mini-batch Gradient Descent with Momentum & Learning Rate Decay
 */
export class RidgeLinearRegression {
  public weights: number[] = [];
  public bias: number = 0;
  public lambda: number; // L2 Regularization coefficient
  public learningRate: number;
  public epochs: number;
  public batchSize: number;

  constructor(lambda: number = 0.05, learningRate: number = 0.01, epochs: number = 300, batchSize: number = 64) {
    this.lambda = lambda;
    this.learningRate = learningRate;
    this.epochs = epochs;
    this.batchSize = batchSize;
  }

  public fit(trainSet: MLFeatureVector[], scaler: FeatureScaler): void {
    const numSamples = trainSet.length;
    const numFeatures = trainSet[0].features.length;

    // Standardize input features using the fitted scaler
    const X = trainSet.map((s) => scaler.transformVector(s.features));
    const y = trainSet.map((s) => s.target);

    // Initialize weights & momentum
    this.weights = new Array(numFeatures).fill(0);
    this.bias = y.reduce((a, b) => a + b, 0) / numSamples;

    const velocityW = new Array(numFeatures).fill(0);
    let velocityB = 0;
    const momentum = 0.9;

    let lr = this.learningRate;

    for (let epoch = 0; epoch < this.epochs; epoch++) {
      // Shuffle indices for mini-batch SGD
      const indices = Array.from({ length: numSamples }, (_, i) => i);
      for (let i = numSamples - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [indices[i], indices[j]] = [indices[j], indices[i]];
      }

      for (let b = 0; b < numSamples; b += this.batchSize) {
        const batchEnd = Math.min(b + this.batchSize, numSamples);
        const batchLen = batchEnd - b;

        const gradW = new Array(numFeatures).fill(0);
        let gradB = 0;

        for (let idx = b; idx < batchEnd; idx++) {
          const sampleIdx = indices[idx];
          const xi = X[sampleIdx];
          const yi = y[sampleIdx];

          // Compute prediction
          let pred = this.bias;
          for (let j = 0; j < numFeatures; j++) {
            pred += this.weights[j] * xi[j];
          }

          const error = pred - yi;
          gradB += error;
          for (let j = 0; j < numFeatures; j++) {
            gradW[j] += error * xi[j];
          }
        }

        // Apply average gradient + L2 penalty
        gradB /= batchLen;
        velocityB = momentum * velocityB + (1 - momentum) * gradB;
        this.bias -= lr * velocityB;

        for (let j = 0; j < numFeatures; j++) {
          const regGrad = (gradW[j] / batchLen) + this.lambda * this.weights[j];
          velocityW[j] = momentum * velocityW[j] + (1 - momentum) * regGrad;
          this.weights[j] -= lr * velocityW[j];
        }
      }

      // Learning rate annealing
      lr *= 0.995;
    }
  }

  public predict(features: number[], scaler: FeatureScaler): number {
    const scaled = scaler.transformVector(features);
    let pred = this.bias;
    for (let j = 0; j < this.weights.length; j++) {
      pred += this.weights[j] * scaled[j];
    }
    return Math.max(0.2, pred);
  }

  public evaluate(testSet: MLFeatureVector[], scaler: FeatureScaler): {
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
      const pred = this.predict(sample.features, scaler);
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
