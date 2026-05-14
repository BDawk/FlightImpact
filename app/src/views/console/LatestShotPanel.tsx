import { useEffect, useState } from "react";
import { Panel } from "@/components/Panel";
import { MetricTile } from "@/components/MetricTile";
import { useTelemetry } from "@/lib/store";
import { api } from "@/lib/transport/rest";
import type { Shot } from "@/lib/types";

export function LatestShotPanel() {
  const recent = useTelemetry((s) => s.recentShots);
  const [latest, setLatest] = useState<Shot | null>(null);

  useEffect(() => {
    if (recent[0]) setLatest(recent[0]);
  }, [recent]);

  useEffect(() => {
    api.listShots(1).then((s) => s[0] && setLatest(s[0])).catch(() => {});
  }, []);

  const m = latest?.metrics;
  const hasData = !!m;

  return (
    <Panel
      title="latest shot"
      subtitle={
        latest
          ? `${new Date(latest.captured_at).toLocaleTimeString(undefined, { hour12: false })}${latest.club ? " · " + latest.club : ""}`
          : "—"
      }
      bodyClassName="space-y-2"
    >
      <div className="grid grid-cols-2 gap-2">
        <MetricTile label="ball mph" value={m?.ball_speed_mph} confidence={m?.confidence?.ball_speed} size="lg" />
        <MetricTile label="club mph" value={m?.club_speed_mph} confidence={m?.confidence?.club_speed} size="lg" />
      </div>
      <div className="grid grid-cols-3 gap-2">
        <MetricTile label="launch" value={m?.launch_angle_deg} unit="°" size="sm" />
        <MetricTile label="smash"  value={m?.smash_factor} size="sm" precision={2} />
        <MetricTile label="spin"   value={m?.spin_rate_rpm} unit="rpm" size="sm" />
        <MetricTile label="carry"  value={m?.carry_yards} unit="yd" size="sm" />
        <MetricTile label="apex"   value={m?.apex_yards} unit="yd" size="sm" />
        <MetricTile label="hang"   value={m?.flight_time_s} unit="s" size="sm" precision={1} />
      </div>
      {!hasData && (
        <div className="cap text-center py-2 !text-ink-dim">
          no shots captured yet
        </div>
      )}
    </Panel>
  );
}
