import { TrafficLevel } from '../../src/types';

/**
 * Raw Trip Telemetry Sample for ML Training
 * Clearly identified as SYNTHETIC DEVELOPMENT TELEMETRY DATA
 */
export interface RawTripTelemetrySample {
  sampleId: string;
  tripId: string;
  routeId: string;
  routeNumber: string;
  routeCategory: string;
  busId: string;
  busCapacity: number;
  driverId: string;
  timestamp: string; // ISO 8601
  hourOfDay: number;
  minuteOfHour: number;
  dayOfWeek: number; // 0 = Sunday, 1 = Monday, ... 6 = Saturday
  isWeekend: number;
  currentLat: number;
  currentLng: number;
  currentSpeedKmH: number;
  trafficLevel: TrafficLevel;
  passengerCount: number;
  weatherCondition: 'clear' | 'rain' | 'fog';
  targetStopId: string;
  targetStopName: string;
  targetStopSequence: number;
  targetStopLat: number;
  targetStopLng: number;
  scheduledArrivalDeltaMin: number;
  distanceToStopKm: number;
  stopsRemainingCount: number;
  tripElapsedMinutes: number;
  tripProgressRatio: number;
  
  // GROUND TRUTH TARGET VARIABLE
  // Time in minutes from the sample timestamp until the bus actually arrives at targetStopId
  actualRemainingTravelTimeMin: number;
}

/**
 * Cleaned & Processed Feature Vector for Model Ingestion
 */
export interface MLFeatureVector {
  sampleId: string;
  tripId: string;
  routeNumber?: string;
  timestamp?: string;
  features: number[];
  target: number; // actualRemainingTravelTimeMin
}

/**
 * Feature Metadata Schema
 */
export interface FeatureDefinition {
  name: string;
  index: number;
  type: 'continuous' | 'discrete' | 'binary' | 'categorical';
  description: string;
  source: string;
  leakageRisk: 'NONE' | 'LOW' | 'HIGH';
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
}

/**
 * Model Evaluation Report Structure
 */
export interface ModelEvaluationResult {
  modelName: string;
  modelType: 'baseline' | 'linear_ridge' | 'decision_tree' | 'random_forest' | 'gradient_boosted_trees';
  mae: number;
  rmse: number;
  r2: number;
  medianAbsoluteError: number;
  accuracyWithin1Min: number; // percentage (0-100)
  accuracyWithin3Min: number; // percentage (0-100)
  accuracyWithin5Min: number; // percentage (0-100)
  trainingTimeMs: number;
  inferenceTimeUs: number; // micro-seconds per prediction
  hyperparameters: Record<string, any>;
}

/**
 * Decision Tree Node Schema for serialization
 */
export interface DecisionTreeNodeJSON {
  isLeaf: boolean;
  value?: number;
  featureIndex?: number;
  threshold?: number;
  left?: DecisionTreeNodeJSON;
  right?: DecisionTreeNodeJSON;
  samples?: number;
  varianceReduction?: number;
}

/**
 * Serialized Production Model Artifact
 */
export interface TrainedModelArtifact {
  metadata: {
    modelName: string;
    modelType: string;
    modelVersion: string;
    datasetType: 'SYNTHETIC_DEVELOPMENT_TELEMETRY';
    datasetVersion: string;
    splitStrategy?: string;
    trainedAt: string;
    trainTripsCount?: number;
    valTripsCount?: number;
    testTripsCount?: number;
    trainSamplesCount: number;
    valSamplesCount: number;
    testSamplesCount: number;
    featuresCount: number;
  };
  features: FeatureDefinition[];
  scaler: {
    means: number[];
    stds: number[];
  };
  evaluationMetrics: ModelEvaluationResult;
  modelPayload: {
    // For Linear Ridge
    weights?: number[];
    bias?: number;
    // For Tree / Forest / GBDT
    trees?: DecisionTreeNodeJSON[];
    treeWeights?: number[]; // For GBDT shrinkage or Forest voting
    learningRate?: number;
    initialPrediction?: number; // Base prediction for GBDT
  };
  featureImportance: {
    featureName: string;
    importanceScore: number;
  }[];
}
