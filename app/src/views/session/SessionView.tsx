import { useEffect, useState } from "react";
import { MetricTile } from "@/components/MetricTile";
import { api } from "@/lib/transport/rest";
import { useTelemetry } from "@/lib/store";
import type { Shot } from "@/lib/types";

export function SessionView() {
  const recent = useTelemetry((s) => s.recentShots);
  const [busy, setBusy] = useState(false);
  const [latest, setLatest] = useState<Shot | null>(null);

  useEffect(() => {
    if (recent[0]) setLatest(recent[0]);
  }, [recent]);

  useEffect(() => {
    api.listShots(1).then((shots) => {
      if (shots[0]) setLatest(shots[0]);
    }).catch(() => {});
  }, []);

  const fireTest = async () => {
    setBusy(true);
    try {
      await api.triggerTestShot();
    } catch (e) {
      console.error(e);
    } finally {
      setBusy(false);
    }
  };

  const m = latest?.metrics;

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-wide text-ink-dim">Last shot</div>
          <div className="mt-0.5 flex items-baseline gap-2">
            <span className="text-sm text-ink-muted">
              {latest ? new Date(latest.captured_at).toLocaleTimeString() : "No shots yet"}
            </span>
            {latest?.club && <span className="text-xs text-ink-dim">{latest.club}</span>}
          </div>
        </div>
        <button
          onClick={fireTest}
          disabled={busy}
          className="rounded-lg bg-brand px-3 py-1.5 text-sm font-medium text-white transition hover:bg-brand-glow disabled:opacity-50"
        >
          {busy ? "Triggering…" : "Test shot"}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MetricTile
          label="Ball speed"
          value={m?.ball_speed_mph}
          unit="mph"
          confidence={m?.confidence?.ball_speed}
        />
        <MetricTile
          label="Club speed"
          value={m?.club_speed_mph}
          unit="mph"
          confidence={m?.confidence?.club_speed}
        />
        <MetricTile
          label="Launch"
          value={m?.launch_angle_deg}
          unit="°"
          confidence={m?.confidence?.launch_angle}
        />
        <MetricTile
          label="Smash"
          value={m?.smash_factor}
          confidence={m?.confidence?.smash_factor}
        />
        <MetricTile
          label="Spin"
          value={m?.spin_rate_rpm}
          unit="rpm"
          confidence={m?.confidence?.spin_rate}
        />
        <MetricTile label="Carry" value={m?.carry_yards} unit="yd" />
      </div>

      {recent.length > 1 && (
        <div className="space-y-2 pt-2">
          <div className="text-xs uppercase tracking-wide text-ink-dim">This session</div>
          <ul className="divide-y divide-line rounded-xl border border-line bg-bg-elev">
            {recent.slice(1, 11).map((s) => (
              <li key={s.id} className="flex items-center justify-between px-3 py-2 text-sm">
                <span className="text-ink-muted tabular">
                  {s.metrics.ball_speed_mph?.toFixed(1) ?? "—"} mph
                </span>
                <span className="text-xs text-ink-dim">
                  {new Date(s.captured_at).toLocaleTimeString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
