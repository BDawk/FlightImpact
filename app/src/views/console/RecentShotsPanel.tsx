import { Panel } from "@/components/Panel";
import { useTelemetry } from "@/lib/store";

export function RecentShotsPanel() {
  const shots = useTelemetry((s) => s.recentShots);

  if (shots.length === 0) {
    return (
      <Panel title="recent shots">
        <div className="cap text-center py-3 !text-ink-dim">empty buffer</div>
      </Panel>
    );
  }

  return (
    <Panel title="recent shots" subtitle={`${shots.length} in buffer`} bodyClassName="!p-0">
      <table className="w-full table-fixed">
        <thead>
          <tr className="cap border-b border-line-soft">
            <th className="w-10 px-3 py-2 text-left">#</th>
            <th className="px-3 py-2 text-left">time</th>
            <th className="px-3 py-2 text-right">ball</th>
            <th className="px-3 py-2 text-right">launch</th>
            <th className="px-3 py-2 text-right">spin</th>
            <th className="px-3 py-2 text-right">carry</th>
          </tr>
        </thead>
        <tbody className="divide-y-hair">
          {shots.slice(0, 8).map((s, i) => (
            <tr key={s.id} className="text-sm">
              <td className="px-3 py-2 lcd text-ink-dim">{shots.length - i}</td>
              <td className="px-3 py-2 lcd text-ink-muted text-xs">
                {new Date(s.captured_at).toLocaleTimeString(undefined, { hour12: false })}
              </td>
              <td className="px-3 py-2 lcd text-right text-ink">
                {s.metrics.ball_speed_mph?.toFixed(1) ?? "—"}
              </td>
              <td className="px-3 py-2 lcd text-right text-ink-muted">
                {s.metrics.launch_angle_deg?.toFixed(1) ?? "—"}
              </td>
              <td className="px-3 py-2 lcd text-right text-ink-muted">
                {s.metrics.spin_rate_rpm?.toFixed(0) ?? "—"}
              </td>
              <td className="px-3 py-2 lcd text-right text-brand">
                {s.metrics.carry_yards?.toFixed(0) ?? "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}
