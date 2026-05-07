import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { TimelinePoint } from '../types';

interface Props {
  points: TimelinePoint[];
  p95: number;
}

/* eslint-disable @typescript-eslint/no-explicit-any */
function LatencyTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload as TimelinePoint;
  return (
    <div className="rounded border border-line bg-base/95 px-3 py-2 font-mono text-[11px] shadow-panel">
      <div className="text-faint">request #{p.index}</div>
      <div className="text-signal">{p.latency_ms.toFixed(2)} ms</div>
      <div className={p.label === 'pass' ? 'text-pass' : 'text-fail'}>
        {p.label.toUpperCase()} · p={p.probability.toFixed(2)}
      </div>
    </div>
  );
}

export function LatencyChart({ points, p95 }: Props) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between">
        <p className="eyebrow">Inference latency</p>
        <p className="font-mono text-[11px] text-faint">last {points.length} requests</p>
      </div>

      <div className="mt-3 h-[220px]">
        {points.length === 0 ? (
          <Empty />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
              <CartesianGrid stroke="#1E2D49" strokeDasharray="2 4" vertical={false} />
              <XAxis
                dataKey="index"
                tick={{ fill: '#5C6B85', fontSize: 11, fontFamily: 'IBM Plex Mono' }}
                tickLine={false}
                axisLine={{ stroke: '#1E2D49' }}
                minTickGap={28}
              />
              <YAxis
                tick={{ fill: '#5C6B85', fontSize: 11, fontFamily: 'IBM Plex Mono' }}
                tickLine={false}
                axisLine={{ stroke: '#1E2D49' }}
                width={44}
                unit="ms"
              />
              <Tooltip content={<LatencyTooltip />} cursor={{ stroke: '#34D6C3', strokeOpacity: 0.25 }} />
              {p95 > 0 && (
                <ReferenceLine
                  y={p95}
                  stroke="#E0A23C"
                  strokeDasharray="4 4"
                  label={{
                    value: `P95 ${p95.toFixed(1)}ms`,
                    position: 'insideTopRight',
                    fill: '#E0A23C',
                    fontSize: 10,
                    fontFamily: 'IBM Plex Mono',
                  }}
                />
              )}
              <Line
                type="monotone"
                dataKey="latency_ms"
                stroke="#34D6C3"
                strokeWidth={1.8}
                dot={false}
                activeDot={{ r: 3, fill: '#34D6C3' }}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

function Empty() {
  return (
    <div className="flex h-full items-center justify-center text-center">
      <p className="font-mono text-xs text-faint">
        No traffic yet — generate predictions to plot serving latency.
      </p>
    </div>
  );
}
