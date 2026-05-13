import { useMemo, useState } from 'react';
import type { ModelInfo, PredictionResult } from '../types';

interface Props {
  model: ModelInfo | null;
  predict: (features: Record<string, number>) => Promise<PredictionResult>;
}

export function PredictForm({ model, predict }: Props) {
  const defaults = useMemo(() => {
    const out: Record<string, string> = {};
    model?.features.forEach((f) => {
      out[f.name] = String(f.set_point);
    });
    return out;
  }, [model]);

  const [values, setValues] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Show entered value if present, otherwise the set-point default.
  const valueFor = (name: string) => values[name] ?? defaults[name] ?? '';

  function setField(name: string, raw: string) {
    setValues((v) => ({ ...v, [name]: raw }));
  }

  async function submit() {
    if (!model) return;
    setBusy(true);
    setError(null);
    try {
      const payload: Record<string, number> = {};
      for (const f of model.features) {
        const n = Number(valueFor(f.name));
        if (Number.isNaN(n)) {
          setError(`"${f.name}" must be a number.`);
          setBusy(false);
          return;
        }
        payload[f.name] = n;
      }
      setResult(await predict(payload));
    } catch {
      setError('Prediction failed — check the API connection.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel p-5">
      <p className="eyebrow">Score a batch</p>
      <p className="mt-1 text-xs text-muted">
        Enter in-process parameters for a single batch and run inference. Defaults
        are the validated set-points.
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3">
        {model?.features.map((f) => (
          <label key={f.name} className="block">
            <span className="font-mono text-[11px] text-faint">
              {f.name} <span className="text-line">({f.unit})</span>
            </span>
            <input
              type="number"
              step="any"
              value={valueFor(f.name)}
              onChange={(e) => setField(f.name, e.target.value)}
              className="mt-1 w-full rounded-md border border-line bg-base px-3 py-1.5 font-mono text-sm text-ink focus:border-signal/60"
            />
          </label>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={submit}
          disabled={busy || !model}
          className="rounded-md bg-signal px-4 py-2 text-sm font-medium text-base transition-opacity hover:opacity-90 disabled:opacity-40"
        >
          Score batch
        </button>
        <button
          onClick={() => {
            setValues({});
            setResult(null);
            setError(null);
          }}
          className="font-mono text-[11px] uppercase tracking-wider text-faint hover:text-muted"
        >
          Reset to set-points
        </button>
      </div>

      {error && <p className="mt-3 font-mono text-[11px] text-fail">{error}</p>}

      {result && !error && (
        <div className="mt-4 flex items-center gap-6 rounded-md border border-line bg-base/60 px-4 py-3">
          <div>
            <span className="eyebrow">Verdict</span>
            <div
              className={`font-mono text-2xl font-semibold ${
                result.label === 'pass' ? 'text-pass' : 'text-fail'
              }`}
            >
              {result.label.toUpperCase()}
            </div>
          </div>
          <div>
            <span className="eyebrow">P(pass)</span>
            <div className="font-mono text-2xl tabular-nums text-ink">
              {(result.probability * 100).toFixed(1)}%
            </div>
          </div>
          <div>
            <span className="eyebrow">Latency</span>
            <div className="font-mono text-2xl tabular-nums text-signal">
              {result.latency_ms.toFixed(2)}
              <span className="text-sm text-faint"> ms</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
