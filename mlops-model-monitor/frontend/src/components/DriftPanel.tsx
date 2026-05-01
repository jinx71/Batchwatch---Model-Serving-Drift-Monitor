import type { DriftReport, FeatureDrift } from '../types';
import { StatusLamp } from './StatusLamp';

interface Props {
  drift: DriftReport | null;
}

// PSI rule of thumb: <0.1 stable | 0.1-0.2 minor | >0.2 significant (flagged).
function classify(psi: number, drifted: boolean) {
  if (drifted) return { tone: 'fail' as const, label: 'Drift', fill: 'bg-fail' };
  if (psi > 0.1) return { tone: 'warn' as const, label: 'Minor', fill: 'bg-warn' };
  return { tone: 'pass' as const, label: 'Stable', fill: 'bg-pass' };
}

const PSI_BAR_SCALE = 1.0; // bar fills at PSI=1.0; larger values clamp to full

function FeatureRow({ f, threshold }: { f: FeatureDrift; threshold: number }) {
  const c = classify(f.psi, f.drifted);
  const fillPct = Math.min(f.psi / PSI_BAR_SCALE, 1) * 100;
  const markerPct = (threshold / PSI_BAR_SCALE) * 100;

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-line/70 py-3 first:border-t-0">
      <div className="w-44 shrink-0">
        <div className="font-mono text-sm text-ink">{f.feature}</div>
        <div className="font-mono text-[11px] text-faint">
          ref {f.reference_mean} → now {f.current_mean}
        </div>
      </div>

      <div className="relative h-2.5 min-w-[120px] flex-1 rounded-full bg-raised">
        <div
          className={`h-full rounded-full ${c.fill} transition-[width] duration-500`}
          style={{ width: `${fillPct}%` }}
        />
        {/* drift threshold marker */}
        <div
          className="absolute top-[-3px] h-[17px] w-px bg-warn/70"
          style={{ left: `${markerPct}%` }}
          title={`PSI threshold ${threshold}`}
        />
      </div>

      <div className="flex w-[150px] shrink-0 items-center justify-between">
        <div className="font-mono text-[11px] leading-tight">
          <div className="text-ink">PSI {f.psi.toFixed(3)}</div>
          <div className="text-faint">KS p {f.ks_pvalue.toFixed(3)}</div>
        </div>
        <StatusLamp tone={c.tone} label={c.label} />
      </div>
    </div>
  );
}

export function DriftPanel({ drift }: Props) {
  const threshold = drift?.psi_threshold ?? 0.2;
  const features = drift?.features
    ? [...drift.features].sort((a, b) => b.psi - a.psi)
    : [];

  return (
    <div className="panel p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Feature drift vs training reference</p>
          <p className="mt-1 text-xs text-muted">
            Population Stability Index per input feature. The amber tick marks the{' '}
            {threshold} drift threshold; KS p-value is shown as supporting evidence.
          </p>
        </div>
        {drift && drift.status === 'ok' && (
          <div className="text-right">
            {drift.dataset_drift ? (
              <StatusLamp tone="fail" label={`${drift.n_drifted} drifted`} pulse />
            ) : (
              <StatusLamp tone="pass" label="All stable" />
            )}
            <p className="mt-1 font-mono text-[11px] text-faint">
              window {drift.sample_size}
            </p>
          </div>
        )}
      </div>

      <div className="mt-4">
        {!drift || drift.status === 'insufficient_data' ? (
          <div className="rounded-md border border-dashed border-line py-8 text-center">
            <p className="font-mono text-xs text-faint">
              Awaiting data — send at least {drift?.min_sample ?? 20} predictions to
              evaluate drift.
            </p>
          </div>
        ) : (
          features.map((f) => (
            <FeatureRow key={f.feature} f={f} threshold={threshold} />
          ))
        )}
      </div>
    </div>
  );
}
