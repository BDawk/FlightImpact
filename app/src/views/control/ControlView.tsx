import { useEffect, useState } from "react";
import { Panel } from "@/components/Panel";
import { Button } from "@/components/Button";
import { MetricTile } from "@/components/MetricTile";
import { useTelemetry } from "@/lib/store";
import { api } from "@/lib/transport/rest";
import type { Shot } from "@/lib/types";
import { ScreenDebugPanel } from "@/views/control/ScreenDebugPanel";

export function ControlView() {
  const recent = useTelemetry((s) => s.recentShots);
  const [shots, setShots] = useState<Shot[]>([]);

  useEffect(() => {
    if (recent.length) setShots(recent);
  }, [recent]);

  useEffect(() => {
    api.listShots(50).then(setShots).catch(() => {});
  }, []);

  const latest = shots[0] ?? null;

  return (
    <div className="bg-grid">
      <div className="mx-auto max-w-6xl p-3 lg:p-4">
        <div className="grid gap-3 lg:grid-cols-3">

          {/* Controls sidebar — right on large screens, top on mobile */}
          <div className="space-y-3 order-first lg:order-last">
            <ControlsPanel />
            <ScreenDebugPanel />
          </div>

          {/* Main — latest shot + history */}
          <div className="space-y-3 lg:col-span-2">
            <LatestShotPanel shot={latest} />
            <ShotHistoryPanel shots={shots} />
          </div>

        </div>
      </div>
    </div>
  );
}

// ── Controls ─────────────────────────────────────────────────────────────────

function ControlsPanel() {
  const [busy, setBusy] = useState(false);
  const [autoTrigger, setAutoTrigger] = useState(true);
  const [threshold, setThreshold] = useState(40);
  const [units, setUnits] = useState<"yd" | "m">("yd");

  const fire = async () => {
    setBusy(true);
    try { await api.triggerTestShot(); }
    catch (e) { console.error(e); }
    finally { setBusy(false); }
  };

  return (
    <Panel title="Controls" bodyClassName="space-y-3.5">
      <Button
        variant="primary"
        size="md"
        onClick={fire}
        disabled={busy}
        className="w-full"
      >
        {busy ? "Triggering…" : "Fire test shot"}
      </Button>

      <Toggle
        label="Auto-trigger"
        hint="Capture on Doppler peak"
        on={autoTrigger}
        onChange={setAutoTrigger}
      />

      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="cap">Trigger threshold</span>
          <span className="lcd text-ink text-xs">
            -{threshold}<span className="text-ink-dim text-[10px] ml-0.5">dB</span>
          </span>
        </div>
        <input
          type="range"
          min="20"
          max="60"
          value={threshold}
          onChange={(e) => setThreshold(Number(e.target.value))}
          className="w-full accent-brand"
        />
      </div>

      <div className="space-y-1.5">
        <div className="cap">Distance units</div>
        <div className="grid grid-cols-2 gap-1">
          <Button variant={units === "yd" ? "primary" : "secondary"} size="sm" onClick={() => setUnits("yd")}>
            Yards
          </Button>
          <Button variant={units === "m" ? "primary" : "secondary"} size="sm" onClick={() => setUnits("m")}>
            Meters
          </Button>
        </div>
      </div>
    </Panel>
  );
}

function Toggle({ label, hint, on, onChange }: {
  label: string; hint?: string; on: boolean; onChange: (v: boolean) => void;
}) {
  return (
    <button
      onClick={() => onChange(!on)}
      className="flex w-full items-center justify-between rounded-md border border-line bg-bg-input px-2.5 py-2 text-left transition-colors hover:border-line-strong"
    >
      <div>
        <div className="cap">{label}</div>
        {hint && <div className="mt-0.5 text-xs text-ink-dim">{hint}</div>}
      </div>
      <span className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${on ? "bg-brand" : "bg-line"}`}>
        <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-bg shadow transition-transform ${on ? "translate-x-4" : "translate-x-0.5"}`} />
      </span>
    </button>
  );
}

// ── Latest Shot ───────────────────────────────────────────────────────────────

function LatestShotPanel({ shot }: { shot: Shot | null }) {
  const m = shot?.metrics;

  return (
    <Panel
      title="Latest Shot"
      subtitle={
        shot
          ? `${new Date(shot.captured_at).toLocaleTimeString(undefined, { hour12: false })}${shot.club ? " · " + shot.club : ""}`
          : "No shots yet"
      }
      bodyClassName="space-y-2"
    >
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <MetricTile label="Ball Speed" value={m?.ball_speed_mph}  unit="mph" confidence={m?.confidence?.ball_speed}  size="lg" />
        <MetricTile label="Club Speed" value={m?.club_speed_mph}  unit="mph" confidence={m?.confidence?.club_speed}  size="lg" />
        <MetricTile label="Smash"      value={m?.smash_factor}               confidence={m?.confidence?.smash_factor} size="lg" precision={2} />
        <MetricTile label="Carry"      value={m?.carry_yards}     unit="yd"  confidence={m?.confidence?.carry}        size="lg" />
      </div>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        <MetricTile label="Launch"  value={m?.launch_angle_deg}     unit="°"   size="sm" />
        <MetricTile label="Dir"     value={m?.launch_direction_deg} unit="°"   size="sm" />
        <MetricTile label="Spin"    value={m?.spin_rate_rpm}         unit="rpm" size="sm" />
        <MetricTile label="Axis"    value={m?.spin_axis_deg}         unit="°"   size="sm" />
        <MetricTile label="Apex"    value={m?.apex_yards}            unit="yd"  size="sm" />
        <MetricTile label="Hang"    value={m?.flight_time_s}         unit="s"   size="sm" precision={1} />
      </div>
      {!m && (
        <div className="cap text-center py-2 !text-ink-dim">
          No shots captured yet — fire a test shot or swing to begin
        </div>
      )}
    </Panel>
  );
}

// ── Shot History ──────────────────────────────────────────────────────────────

function ShotHistoryPanel({ shots }: { shots: Shot[] }) {
  return (
    <Panel title="Shot History" subtitle={shots.length ? `${shots.length} shots` : undefined} bodyClassName="!p-0">
      {shots.length === 0 ? (
        <div className="cap p-6 text-center !text-ink-dim">No shots recorded yet</div>
      ) : (
        <table className="w-full table-fixed">
          <thead>
            <tr className="cap border-b border-line-soft">
              <th className="w-10 px-3 py-2 text-left">#</th>
              <th className="px-3 py-2 text-left">Time</th>
              <th className="hidden px-3 py-2 text-left sm:table-cell">Club</th>
              <th className="px-3 py-2 text-right">Ball mph</th>
              <th className="px-3 py-2 text-right">Launch</th>
              <th className="hidden px-3 py-2 text-right sm:table-cell">Spin</th>
              <th className="px-3 py-2 text-right">Carry yd</th>
            </tr>
          </thead>
          <tbody className="divide-y-hair">
            {shots.map((s, i) => (
              <tr key={s.id} className="text-sm transition-colors hover:bg-bg-panel/60">
                <td className="px-3 py-2 lcd text-ink-dim">{shots.length - i}</td>
                <td className="px-3 py-2 lcd text-ink-muted text-xs">
                  {new Date(s.captured_at).toLocaleTimeString(undefined, { hour12: false })}
                </td>
                <td className="hidden px-3 py-2 text-ink-muted text-xs sm:table-cell">
                  {s.club ?? "—"}
                </td>
                <td className="px-3 py-2 lcd text-right text-ink">
                  {s.metrics.ball_speed_mph?.toFixed(1) ?? "—"}
                </td>
                <td className="px-3 py-2 lcd text-right text-ink-muted">
                  {s.metrics.launch_angle_deg?.toFixed(1) ?? "—"}°
                </td>
                <td className="hidden px-3 py-2 lcd text-right text-ink-muted sm:table-cell">
                  {s.metrics.spin_rate_rpm?.toFixed(0) ?? "—"}
                </td>
                <td className="px-3 py-2 lcd text-right text-brand font-medium">
                  {s.metrics.carry_yards?.toFixed(0) ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}
