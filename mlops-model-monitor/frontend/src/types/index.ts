// Shared response envelope returned by every endpoint.
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface FeatureSchema {
  name: string;
  unit: string;
  set_point: number;
}

export interface ModelInfo {
  model_name: string;
  model_type: string;
  version: string;
  trained_at: string;
  n_train: number;
  n_test: number;
  train_pass_rate: number;
  metrics: { accuracy: number; f1: number; roc_auc: number };
  features: FeatureSchema[];
  classes: Record<string, string>;
}

export interface Metrics {
  total: number;
  passed: number;
  failed: number;
  pass_rate: number;
  avg_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  sources: Record<string, number>;
}

export interface TimelinePoint {
  index: number;
  created_at: string;
  latency_ms: number;
  prediction: number;
  label: 'pass' | 'fail';
  probability: number;
  source: string;
}

export interface TimelineBucket {
  bucket: string;
  passed: number;
  failed: number;
  pass_rate: number;
}

export interface Timeline {
  points: TimelinePoint[];
  buckets: TimelineBucket[];
}

export interface FeatureDrift {
  feature: string;
  ks_statistic: number;
  ks_pvalue: number;
  psi: number;
  drifted: boolean;
  reference_mean: number;
  current_mean: number;
}

export interface DriftReport {
  status: 'ok' | 'insufficient_data';
  sample_size: number;
  min_sample?: number;
  psi_threshold?: number;
  pvalue_threshold?: number;
  n_drifted: number;
  drift_share: number;
  dataset_drift: boolean;
  features: FeatureDrift[];
}

export interface PredictionResult {
  prediction: number;
  label: 'pass' | 'fail';
  probability: number;
  latency_ms: number;
}

export interface SimulateResult {
  count: number;
  drift_injected: boolean;
  pass_rate: number;
  avg_latency_ms: number;
}
