import type { DriftReport, ModelInfo } from '../types';
import { StatusLamp } from './StatusLamp';

interface Props {
  model: ModelInfo | null;
  drift: DriftReport | null;
  lastUpdated: Date | null;
  paused: boolean;
  onTogglePause: () => void;
  onRefresh: () => void;
}

function driftLamp(drift: DriftReport | null) {
  if (!drift || drift.status === 'insufficient_data') {
    return <StatusLamp tone="idle" label="Awaiting data" />;
  }
  if (drift.dataset_drift) {
    return <StatusLamp tone="fail" label="Drift detected" pulse />;
  }
  return <StatusLamp tone="pass" label="Stable" />;
}

export function Header({
  model,
  drift,
  lastUpdated,
  paused,
  onTogglePause,
  onRefresh,
}: Props) {
  return (
    <header className="border-b border-line bg-surface/60 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="h-7 w-1.5 rounded-full bg-signal shadow-[0_0_12px_2px_rgba(52,214,195,0.55)]" />
          <div>
            <h1 className="font-mono text-lg font-semibold tracking-[0.2em] text-ink">
              BATCHWATCH
            </h1>
            <p className="text-xs text-muted">Model serving &amp; drift monitor</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          {model && (
            <div className="flex items-center gap-3">
              <StatusLamp tone="pass" label="Model live" />
              <span className="font-mono text-xs text-muted">
                {model.model_name}{' '}
                <span className="text-faint">v{model.version}</span>
                <span className="text-faint"> · AUC {model.metrics.roc_auc}</span>
              </span>
            </div>
          )}

          <div className="h-5 w-px bg-line" aria-hidden />

          {driftLamp(drift)}

          <div className="flex items-center gap-2">
            <span className="hidden font-mono text-[11px] text-faint sm:inline">
              {lastUpdated
                ? `synced ${lastUpdated.toLocaleTimeString()}`
                : 'connecting…'}
            </span>
            <button
              onClick={onTogglePause}
              className="rounded border border-line px-2.5 py-1 font-mono text-[11px] uppercase tracking-wider text-muted transition-colors hover:border-signal/50 hover:text-ink"
            >
              {paused ? 'Resume' : 'Pause'}
            </button>
            <button
              onClick={onRefresh}
              className="rounded border border-line px-2.5 py-1 font-mono text-[11px] uppercase tracking-wider text-muted transition-colors hover:border-signal/50 hover:text-ink"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
