import { useEffect, useState } from "react";
import { api } from "@/lib/transport/rest";
import type { Shot } from "@/lib/types";

export function HistoryView() {
  const [shots, setShots] = useState<Shot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listShots(100)
      .then(setShots)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-ink-muted">Loading shots…</div>;
  }

  if (shots.length === 0) {
    return (
      <div className="p-8 text-center text-ink-muted">
        No shots yet. Hit a ball, or use the Test shot button on the Session tab.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-2 p-4">
      <div className="text-xs uppercase tracking-wide text-ink-dim">{shots.length} shots</div>
      <ul className="divide-y divide-line rounded-xl border border-line bg-bg-elev">
        {shots.map((s) => (
          <li key={s.id} className="grid grid-cols-[1fr_auto_auto] items-center gap-4 px-3 py-3">
            <div>
              <div className="text-sm text-ink">
                {s.metrics.ball_speed_mph?.toFixed(1) ?? "—"}{" "}
                <span className="text-xs text-ink-muted">mph</span>
              </div>
              <div className="text-xs text-ink-dim">
                {new Date(s.captured_at).toLocaleString()}
              </div>
            </div>
            <div className="text-xs text-ink-muted">{s.club ?? ""}</div>
            <div className="text-xs uppercase text-ink-dim">{s.status}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
