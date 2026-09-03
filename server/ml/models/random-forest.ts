import { MLFeatureVector } from '../types';
import { DecisionTreeRegressor } from './decision-tree';

export class RandomForestRegressor {
  public numTrees: number;
  public maxDepth: number;
  public maxFeaturesRatio: number;
  public trees: DecisionTreeRegressor[] = [];
  public featureImportances: number[] = [];

  constructor(numTrees: number = 25, maxDepth: number = 9, maxFeaturesRatio: number = 0.6) {
    this.numTrees = numTrees;
    this.maxDepth = maxDepth;
    this.maxFeaturesRatio = maxFeaturesRatio;
  }

  public fit(trainSet: MLFeatureVector[]): void {
    const numSamples = trainSet.length;
    const numFeatures = trainSet[0].features.length;
    this.trees = [];
    this.featureImportances = new Array(numFeatures).fill(0);

    const X = trainSet.map((s) => s.features);
    const y = trainSet.map((s) => s.target);

    for (let t = 0; t < this.numTrees; t++) {
      // Bootstrap sampling with replacement
      const bootIndices: number[] = [];
      for (let i = 0; i < numSamples; i++) {
        bootIndices.push(Math.floor(Math.random() * numSamples));
      }

      const bootX = bootIndices.map((i) => X[i]);
      const bootY = bootIndices.map((i) => y[i]);

      const tree = new DecisionTreeRegressor(this.maxDepth, 5, 2, this.maxFeaturesRatio);
      tree.fit(bootX, bootY);
      this.trees.push(tree);

      // Accumulate feature importances
      for (let f = 0; f < numFeatures; f++) {
        this.featureImportances[f] += tree.featureImportances[f] || 0;
      }
    }

    // Normalize
    const sumImp = this.featureImportances.reduce((a, b) => a + b, 0);
    if (sumImp > 0) {
      this.featureImportances = this.featureImportances.map((v) => v / sumImp);
    }
  }

  public predict(features: number[]): number {
    if (this.trees.length === 0) return 0;
    let sum = 0;
    for (const tree of this.trees) {
      sum += tree.predictRow(features);
    }
    return Math.max(0.2, sum / this.trees.length);
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
