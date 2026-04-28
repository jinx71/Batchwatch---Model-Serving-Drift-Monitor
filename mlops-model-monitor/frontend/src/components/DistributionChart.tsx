import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { TimelineBucket } from '../types';

interface Props {
  buckets: TimelineBucket[];
}

/* eslint-disable @typescript-eslint/no-explicit-any */
function DistTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const b = payload[0].payload as TimelineBucket;
  return (
    <div className="rounded border border-line bg-base/95 px-3 py-2 font-mono text-[11px] shadow-panel">
      <div className="text-faint">requests {b.bucket}</div>
      <div className="text-pass">pass {b.passed}</div>
      <div className="text-fail">fail {b.failed}</div>
      <div className="text-muted">rate {(b.pass_rate * 100).toFixed(0)}%</div>
    </div>
  );
}

export function DistributionChart({ buckets }: Props) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between">
        <p className="eyebrow">Outcome by recent batch</p>
        <p className="font-mono text-[11px] text-faint">
          <span className="text-pass">pass</span> / <span className="text-fail">fail</span>
        </p>
      </div>

      <div className="mt-3 h-[220px]">
        {buckets.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center">
            <p className="font-mono text-xs text-faint">
              No traffic yet — a drift burst shows up here as failing batches.
            </p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={buckets} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
              <CartesianGrid stroke="#1E2D49" strokeDasharray="2 4" vertical={false} />
              <XAxis
                dataKey="bucket"
                tick={{ fill: '#5C6B85', fontSize: 10, fontFamily: 'IBM Plex Mono' }}
                tickLine={false}
                axisLine={{ stroke: '#1E2D49' }}
                minTickGap={4}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: '#5C6B85', fontSize: 11, fontFamily: 'IBM Plex Mono' }}
                tickLine={false}
                axisLine={{ stroke: '#1E2D49' }}
                width={44}
              />
              <Tooltip content={<DistTooltip />} cursor={{ fill: 'rgba(52,214,195,0.06)' }} />
              <Bar dataKey="passed" stackId="o" fill="#46C28A" isAnimationActive={false} />
              <Bar
                dataKey="failed"
                stackId="o"
                fill="#E5564E"
                radius={[2, 2, 0, 0]}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
