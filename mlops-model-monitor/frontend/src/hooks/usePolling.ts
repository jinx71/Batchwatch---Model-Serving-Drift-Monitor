import { useEffect, useRef } from 'react';

// Runs `callback` immediately, then every `intervalMs` while `enabled`.
// The latest callback is kept in a ref so changing it doesn't reset the timer.
export function usePolling(
  callback: () => void | Promise<void>,
  intervalMs: number,
  enabled = true,
): void {
  const saved = useRef(callback);

  useEffect(() => {
    saved.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    const tick = () => {
      if (active) void saved.current();
    };
    tick();
    const id = window.setInterval(tick, intervalMs);
    return () => {
      active = false;
      window.clearInterval(id);
    };
  }, [intervalMs, enabled]);
}
