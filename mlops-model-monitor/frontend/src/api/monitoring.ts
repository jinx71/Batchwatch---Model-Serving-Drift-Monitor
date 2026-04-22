import { client } from './client';
import type {
  ApiResponse,
  DriftReport,
  Metrics,
  ModelInfo,
  PredictionResult,
  SimulateResult,
  Timeline,
} from '../types';

// Each helper unwraps the { success, data, message } envelope to data.
export async function getModel(): Promise<ModelInfo> {
  const res = await client.get<ApiResponse<ModelInfo>>('/api/monitoring/model');
  return res.data.data;
}

export async function getMetrics(): Promise<Metrics> {
  const res = await client.get<ApiResponse<Metrics>>('/api/monitoring/metrics');
  return res.data.data;
}

export async function getTimeline(limit = 120, buckets = 12): Promise<Timeline> {
  const res = await client.get<ApiResponse<Timeline>>('/api/monitoring/timeline', {
    params: { limit, buckets },
  });
  return res.data.data;
}

export async function getDrift(window = 200): Promise<DriftReport> {
  const res = await client.get<ApiResponse<DriftReport>>('/api/monitoring/drift', {
    params: { window },
  });
  return res.data.data;
}

export async function predict(
  features: Record<string, number>,
): Promise<PredictionResult> {
  const res = await client.post<ApiResponse<PredictionResult>>('/api/predict', features);
  return res.data.data;
}

export async function simulate(count: number, drift: boolean): Promise<SimulateResult> {
  const res = await client.post<ApiResponse<SimulateResult>>('/api/simulate', {
    count,
    drift,
  });
  return res.data.data;
}

export async function clearLogs(): Promise<void> {
  await client.delete('/api/monitoring/logs');
}
