import { useEffect, useState } from "react";
import { Panel } from "@/components/Panel";
import { MetricTile } from "@/components/MetricTile";
import { useTelemetry } from "@/lib/store";
import { api } from "@/lib/transport/rest";
import type { Shot } from "@/lib/types";

export function SessionView() {
  const recent = useTelemetry((s) => s.recentShots);
  const [shots, setShots] = useState<Shot[]>([]);

  useEffect(() => {
    if (recent.length) setShots(recent);
  }, [recent]);

  useEffect(() => {
    api.listShots(50).then(setShots).catch(() => {});
  }, []);

  const latest = shots[0];
  const m = latest?.metrics;

  return (
    <div className="bg-grid">
      <div className="mx-auto max-w-4xl space-y-3 p-3 lg:p-4">
        <Panel
          title="latest shot"
          subtitle={
            latest
              ? `${new Date(latest.captured_at).toLocaleString()} · ${latest.club ?? "no club"}`
              : "no shots yet"
          }
          bodyClassName="space-y-3"
        >
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            <MetricTile label="ball mph"  value={m?.ball_speed_mph} confidence={m?.confidence?.ball_speed} size="lg" />
            <MetricTile label="club mph"  value={m?.club_speed_mph} confidence={m?.confidence?.club_speed} size="lg" />
            <MetricTile label="smash"     value={m?.smash_factor} confidence={m?.confidence?.smash_factor} size="lg" precision={2} />
            <MetricTile label="carry yd"  value={m?.carry_yards} confidence={m?.confidence?.carry} size="lg" />
          </div>
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
            <MetricTile label="launch°"   value={m?.launch_angle_deg} size="sm" />
            <MetricTile label="dir°"      value={m?.launch_direction_deg} size="sm" />
            <MetricTile label="spin rpm"  value={m?.spin_rate_rpm} size="sm" />
            <MetricTile label="axis°"     value={m?.spin_axis_deg} size="sm" />
            <MetricTile label="apex yd"   value={m?.apex_yards} size="sm" />
            <MetricTile label="hang s"    value={m?.flight_time_s} size="sm" precision={1} />
          </div>
        </Panel>

        <Panel title="session log" subtitle={`${shots.length} shots`} bodyClassName="!p-0">
          {shots.length === 0 ? (
            <div className="cap p-6 text-center !text-ink-dim">no shots captured yet</div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="cap border-b border-line-soft">
                  <th className="w-12 px-3 py-2 text-left">#</th>
                  <th className="px-3 py-2 text-left">time</th>
                  <th className="px-3 py-2 text-left">club</th>
                  <th className="px-3 py-2 text-right">ball mph</th>
                  <th className="px-3 py-2 text-right">launch</th>
                  <th className="px-3 py-2 text-right">spin</th>
                  <th className="px-3 py-2 text-right">carry yd</th>
                </tr>
              </thead>
              <tbody className="divide-y-hair">
                {shots.map((s, i) => (
                  <tr key={s.id} className="text-sm">
                    <td className="px-3 py-2 lcd text-ink-dim">{shots.length - i}</td>
                    <td className="px-3 py-2 lcd text-ink-muted text-xs">
                      {new Date(s.captured_at).toLocaleTimeString(undefined, { hour12: false })}
                    </td>
                    <td className="px-3 py-2 text-ink-muted text-xs">{s.club ?? "—"}</td>
                    <td className="px-3 py-2 lcd text-right text-ink">{s.metrics.ball_speed_mph?.toFixed(1) ?? "—"}</td>
                    <td className="px-3 py-2 lcd text-right text-ink-muted">{s.metrics.launch_angle_deg?.toFixed(1) ?? "—"}</td>
                    <td className="px-3 py-2 lcd text-right text-ink-muted">{s.metrics.spin_rate_rpm?.toFixed(0) ?? "—"}</td>
                    <td className="px-3 py-2 lcd text-right text-brand">{s.metrics.carry_yards?.toFixed(0) ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>
      </div>
    </div>
  );
}
