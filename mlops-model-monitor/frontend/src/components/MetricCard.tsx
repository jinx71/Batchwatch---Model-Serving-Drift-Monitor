interface Props {
  label: string;
  value: string;
  unit?: string;
  sub?: string;
  tone?: 'signal' | 'pass' | 'warn' | 'fail';
}

const TONE: Record<NonNullable<Props['tone']>, string> = {
  signal: 'text-signal',
  pass: 'text-pass',
  warn: 'text-warn',
  fail: 'text-fail',
};

export function MetricCard({ label, value, unit, sub, tone = 'signal' }: Props) {
  return (
    <div className="panel p-4">
      <p className="eyebrow">{label}</p>
      <div className="mt-3 flex items-baseline gap-1.5">
        <span className={`font-mono text-3xl font-medium tabular-nums ${TONE[tone]}`}>
          {value}
        </span>
        {unit && <span className="font-mono text-sm text-faint">{unit}</span>}
      </div>
      {sub && <p className="mt-1 font-mono text-[11px] text-faint">{sub}</p>}
    </div>
  );
}
