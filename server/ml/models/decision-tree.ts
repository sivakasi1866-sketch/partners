import { MLFeatureVector, DecisionTreeNodeJSON } from '../types';

export interface TreeNode {
  isLeaf: boolean;
  value?: number;
  featureIndex?: number;
  threshold?: number;
  left?: TreeNode;
  right?: TreeNode;
  samples: number;
  varianceReduction?: number;
}

export class DecisionTreeRegressor {
  public root: TreeNode | null = null;
  public maxDepth: number;
  public minSamplesSplit: number;
  public minSamplesLeaf: number;
  public maxFeaturesRatio: number; // For Random Forest subspace sampling (1.0 = all features)
  public featureImportances: number[] = [];

  constructor(
    maxDepth: number = 8,
    minSamplesSplit: number = 6,
    minSamplesLeaf: number = 3,
    maxFeaturesRatio: number = 1.0
  ) {
    this.maxDepth = maxDepth;
    this.minSamplesSplit = minSamplesSplit;
    this.minSamplesLeaf = minSamplesLeaf;
    this.maxFeaturesRatio = maxFeaturesRatio;
  }

  public fit(X: number[][], y: number[]): void {
    const numFeatures = X[0].length;
    this.featureImportances = new Array(numFeatures).fill(0);
    this.root = this.buildTree(X, y, 0);

    // Normalize feature importances
    const sumImp = this.featureImportances.reduce((a, b) => a + b, 0);
    if (sumImp > 0) {
      this.featureImportances = this.featureImportances.map((v) => v / sumImp);
    }
  }

  private buildTree(X: number[][], y: number[], depth: number): TreeNode {
    const numSamples = y.length;
    const numFeatures = X[0].length;

    // Calculate node mean value
    const meanValue = y.reduce((a, b) => a + b, 0) / numSamples;

    // Stopping criteria
    if (depth >= this.maxDepth || numSamples < this.minSamplesSplit || this.calculateVariance(y) < 1e-5) {
      return { isLeaf: true, value: meanValue, samples: numSamples };
    }

    // Subsample features if maxFeaturesRatio < 1.0 (for Random Forests)
    let featureIndices = Array.from({ length: numFeatures }, (_, i) => i);
    if (this.maxFeaturesRatio < 1.0) {
      const numSubset = Math.max(1, Math.floor(numFeatures * this.maxFeaturesRatio));
      featureIndices.sort(() => Math.random() - 0.5);
      featureIndices = featureIndices.slice(0, numSubset);
    }

    let bestVarRed = -1;
    let bestFeature = -1;
    let bestThreshold = 0;
    let bestLeftIndices: number[] = [];
    let bestRightIndices: number[] = [];

    const parentVar = this.calculateVariance(y);

    for (const featIdx of featureIndices) {
      // Find candidate thresholds (quantiles / distinct values)
      const values = X.map((row) => row[featIdx]);
      const uniqueValues = Array.from(new Set(values)).sort((a, b) => a - b);

      if (uniqueValues.length <= 1) continue;

      // Sample up to 20 candidate split points
      const step = Math.max(1, Math.floor(uniqueValues.length / 20));
      for (let k = 0; k < uniqueValues.length - 1; k += step) {
        const threshold = (uniqueValues[k] + uniqueValues[k + 1]) / 2;

        const leftIdxs: number[] = [];
        const rightIdxs: number[] = [];

        for (let i = 0; i < numSamples; i++) {
          if (X[i][featIdx] <= threshold) leftIdxs.push(i);
          else rightIdxs.push(i);
        }

        if (leftIdxs.length < this.minSamplesLeaf || rightIdxs.length < this.minSamplesLeaf) {
          continue;
        }

        const leftY = leftIdxs.map((i) => y[i]);
        const rightY = rightIdxs.map((i) => y[i]);

        const leftVar = this.calculateVariance(leftY);
        const rightVar = this.calculateVariance(rightY);

        const varRed = parentVar - ((leftIdxs.length / numSamples) * leftVar + (rightIdxs.length / numSamples) * rightVar);

        if (varRed > bestVarRed) {
          bestVarRed = varRed;
          bestFeature = featIdx;
          bestThreshold = threshold;
          bestLeftIndices = leftIdxs;
          bestRightIndices = rightIdxs;
        }
      }
    }

    if (bestVarRed <= 0 || bestLeftIndices.length === 0 || bestRightIndices.length === 0) {
      return { isLeaf: true, value: meanValue, samples: numSamples };
    }

    // Accumulate feature importance
    this.featureImportances[bestFeature] += bestVarRed * numSamples;

    const leftX = bestLeftIndices.map((i) => X[i]);
    const leftY = bestLeftIndices.map((i) => y[i]);
    const rightX = bestRightIndices.map((i) => X[i]);
    const rightY = bestRightIndices.map((i) => y[i]);

    return {
      isLeaf: false,
      featureIndex: bestFeature,
      threshold: bestThreshold,
      samples: numSamples,
      varianceReduction: bestVarRed,
      left: this.buildTree(leftX, leftY, depth + 1),
      right: this.buildTree(rightX, rightY, depth + 1)
    };
  }

  private calculateVariance(y: number[]): number {
    if (y.length <= 1) return 0;
    const mean = y.reduce((a, b) => a + b, 0) / y.length;
    let sumSq = 0;
    for (const val of y) sumSq += Math.pow(val - mean, 2);
    return sumSq / y.length;
  }

  public predictRow(features: number[], node: TreeNode | null = this.root): number {
    if (!node) return 0;
    if (node.isLeaf || node.featureIndex === undefined || node.threshold === undefined) {
      return node.value ?? 0;
    }

    if (features[node.featureIndex] <= node.threshold) {
      return this.predictRow(features, node.left || null);
    } else {
      return this.predictRow(features, node.right || null);
    }
  }

  public toJSON(node: TreeNode | null = this.root): DecisionTreeNodeJSON {
    if (!node) return { isLeaf: true, value: 0 };
    if (node.isLeaf) {
      return { isLeaf: true, value: parseFloat((node.value || 0).toFixed(4)), samples: node.samples };
    }
    return {
      isLeaf: false,
      featureIndex: node.featureIndex,
      threshold: parseFloat((node.threshold || 0).toFixed(4)),
      samples: node.samples,
      varianceReduction: parseFloat((node.varianceReduction || 0).toFixed(4)),
      left: this.toJSON(node.left || null),
      right: this.toJSON(node.right || null)
    };
  }

  public static fromJSON(json: DecisionTreeNodeJSON): TreeNode {
    if (json.isLeaf) {
      return { isLeaf: true, value: json.value, samples: json.samples || 1 };
    }
    return {
      isLeaf: false,
      featureIndex: json.featureIndex,
      threshold: json.threshold,
      samples: json.samples || 1,
      varianceReduction: json.varianceReduction,
      left: json.left ? DecisionTreeRegressor.fromJSON(json.left) : undefined,
      right: json.right ? DecisionTreeRegressor.fromJSON(json.right) : undefined
    };
  }
}
