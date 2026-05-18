type Tone = 'pass' | 'fail' | 'warn' | 'idle';

const TONE: Record<Tone, { dot: string; text: string; glow: string }> = {
  pass: { dot: 'bg-pass', text: 'text-pass', glow: 'shadow-[0_0_10px_2px_rgba(70,194,138,0.6)]' },
  fail: { dot: 'bg-fail', text: 'text-fail', glow: 'shadow-[0_0_10px_2px_rgba(229,86,78,0.6)]' },
  warn: { dot: 'bg-warn', text: 'text-warn', glow: 'shadow-[0_0_10px_2px_rgba(224,162,60,0.6)]' },
  idle: { dot: 'bg-faint', text: 'text-faint', glow: '' },
};

interface Props {
  tone: Tone;
  label: string;
  pulse?: boolean;
}

export function StatusLamp({ tone, label, pulse = false }: Props) {
  const t = TONE[tone];
  return (
    <span className="inline-flex items-center gap-2">
      <span
        className={`h-2 w-2 rounded-full ${t.dot} ${t.glow} ${pulse ? 'animate-lamp' : ''}`}
      />
      <span className={`font-mono text-[11px] uppercase tracking-[0.16em] ${t.text}`}>
        {label}
      </span>
    </span>
  );
}
