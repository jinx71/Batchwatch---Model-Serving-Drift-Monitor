import { useState } from 'react';
import type { SimulateResult } from '../types';

interface Props {
  simulate: (count: number, drift: boolean) => Promise<SimulateResult>;
  clearLog: () => Promise<void>;
}

const COUNTS = [50, 100, 250];

export function SimulatePanel({ simulate, clearLog }: Props) {
  const [count, setCount] = useState(100);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(drift: boolean) {
    setBusy(true);
    setError(null);
    try {
      const res = await simulate(count, drift);
      setMessage(
        `${res.count} ${drift ? 'drifted' : 'normal'} batches scored · pass rate ${(
          res.pass_rate * 100
        ).toFixed(0)}% · avg ${res.avg_latency_ms.toFixed(2)} ms`,
      );
    } catch {
      setError('Request failed — is the API running on the configured URL?');
    } finally {
      setBusy(false);
    }
  }

  async function clear() {
    setBusy(true);
    setError(null);
    try {
      await clearLog();
      setMessage('Prediction log cleared.');
    } catch {
      setError('Could not clear the log.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel p-5">
      <p className="eyebrow">Generate traffic</p>
      <p className="mt-1 text-xs text-muted">
        Feed the model synthetic batches. Drifted batches simulate a process
        excursion — watch the pass rate fall and features trip the drift threshold.
      </p>

      <div className="mt-4">
        <span className="eyebrow">Batch size</span>
        <div className="mt-2 inline-flex overflow-hidden rounded-md border border-line">
          {COUNTS.map((c) => (
            <button
              key={c}
              onClick={() => setCount(c)}
              className={`px-4 py-1.5 font-mono text-xs tabular-nums transition-colors ${
                count === c
                  ? 'bg-signal/15 text-signal'
                  : 'text-muted hover:bg-raised hover:text-ink'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button
          onClick={() => run(false)}
          disabled={busy}
          className="rounded-md bg-signal px-4 py-2 text-sm font-medium text-base transition-opacity hover:opacity-90 disabled:opacity-40"
        >
          Send normal batch
        </button>
        <button
          onClick={() => run(true)}
          disabled={busy}
          className="rounded-md border border-warn/60 px-4 py-2 text-sm font-medium text-warn transition-colors hover:bg-warn/10 disabled:opacity-40"
        >
          Send drifted batch
        </button>
        <button
          onClick={clear}
          disabled={busy}
          className="ml-auto rounded-md border border-line px-4 py-2 text-sm text-muted transition-colors hover:border-fail/50 hover:text-fail disabled:opacity-40"
        >
          Clear log
        </button>
      </div>

      {(message || error) && (
        <p
          className={`mt-4 font-mono text-[11px] ${error ? 'text-fail' : 'text-muted'}`}
        >
          {error ?? message}
        </p>
      )}
    </div>
  );
}
