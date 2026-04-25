import { useCallback, useEffect, useState } from 'react';
import {
  clearLogs,
  getDrift,
  getMetrics,
  getModel,
  getTimeline,
  predict,
  simulate,
} from './api/monitoring';
import { usePolling } from './hooks/usePolling';
import type { DriftReport, Metrics, ModelInfo, Timeline } from './types';
import { DistributionChart } from './components/DistributionChart';
import { DriftPanel } from './components/DriftPanel';
import { Header } from './components/Header';
import { LatencyChart } from './components/LatencyChart';
import { MetricCard } from './components/MetricCard';
import { PredictForm } from './components/PredictForm';
import { SimulatePanel } from './components/SimulatePanel';

const POLL_MS = 4000;

function passRateTone(rate: number): 'pass' | 'warn' | 'fail' {
  if (rate >= 0.6) return 'pass';
  if (rate >= 0.3) return 'warn';
  return 'fail';
}

export default function App() {
  const [model, setModel] = useState<ModelInfo | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [drift, setDrift] = useState<DriftReport | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [paused, setPaused] = useState(false);
  const [connError, setConnError] = useState(false);

  const refreshAll = useCallback(async () => {
    try {
      const [m, t, d] = await Promise.all([getMetrics(), getTimeline(), getDrift()]);
      setMetrics(m);
      setTimeline(t);
      setDrift(d);
      setLastUpdated(new Date());
      setConnError(false);
    } catch {
      setConnError(true);
    }
  }, []);

  useEffect(() => {
    getModel()
      .then(setModel)
      .catch(() => setConnError(true));
  }, []);

  usePolling(refreshAll, POLL_MS, !paused);

  const handleSimulate = useCallback(
    async (count: number, withDrift: boolean) => {
      const res = await simulate(count, withDrift);
      await refreshAll();
      return res;
    },
    [refreshAll],
  );

  const handleClear = useCallback(async () => {
    await clearLogs();
    await refreshAll();
  }, [refreshAll]);

  const handlePredict = useCallback(
    async (features: Record<string, number>) => {
      const res = await predict(features);
      await refreshAll();
      return res;
    },
    [refreshAll],
  );

  const passRate = metrics?.pass_rate ?? 0;

  return (
    <div className="min-h-screen">
      <Header
        model={model}
        drift={drift}
        lastUpdated={lastUpdated}
        paused={paused}
        onTogglePause={() => setPaused((p) => !p)}
        onRefresh={() => void refreshAll()}
      />

      <main className="mx-auto max-w-7xl space-y-5 px-6 py-6">
        {connError && (
          <div className="rounded-md border border-fail/40 bg-fail/10 px-4 py-3 font-mono text-xs text-fail">
            Can't reach the API. Start the backend (uvicorn on :8000) or set VITE_API_URL,
            then refresh.
          </div>
        )}

        <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <MetricCard
            label="Predictions served"
            value={metrics ? metrics.total.toLocaleString() : '—'}
            sub={
              metrics
                ? `${metrics.passed.toLocaleString()} pass · ${metrics.failed.toLocaleString()} fail`
                : undefined
            }
          />
          <MetricCard
            label="Avg latency"
            value={metrics ? metrics.avg_latency_ms.toFixed(2) : '—'}
            unit="ms"
            sub={metrics ? `p50 ${metrics.p50_latency_ms.toFixed(2)} ms` : undefined}
          />
          <MetricCard
            label="P95 latency"
            value={metrics ? metrics.p95_latency_ms.toFixed(2) : '—'}
            unit="ms"
            tone="warn"
          />
          <MetricCard
            label="Pass rate"
            value={metrics ? (passRate * 100).toFixed(1) : '—'}
            unit="%"
            tone={metrics ? passRateTone(passRate) : 'signal'}
            sub={drift?.dataset_drift ? 'drift active' : undefined}
          />
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <LatencyChart
            points={timeline?.points ?? []}
            p95={metrics?.p95_latency_ms ?? 0}
          />
          <DistributionChart buckets={timeline?.buckets ?? []} />
        </section>

        <DriftPanel drift={drift} />

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <SimulatePanel simulate={handleSimulate} clearLog={handleClear} />
          <PredictForm model={model} predict={handlePredict} />
        </section>

        <footer className="pt-2 pb-6 text-center">
          <p className="font-mono text-[11px] text-faint">
            BATCHWATCH · FastAPI + scikit-learn serving · PSI / KS drift monitoring ·
            polling every {POLL_MS / 1000}s
          </p>
        </footer>
      </main>
    </div>
  );
}
