import type { ReactNode } from "react";
import { useTelemetry } from "@/lib/store";
import { Panel } from "@/components/Panel";
import { Button } from "@/components/Button";

function fmtUptime(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${sec}s`;
  return `${sec}s`;
}

export function SettingsView() {
  const status = useTelemetry((s) => s.status);

  return (
    <div className="bg-grid">
      <div className="mx-auto max-w-3xl space-y-3 p-3 lg:p-4">
        <Panel title="device" subtitle="raspberry pi 5">
          <KVList rows={[
            ["camera", status?.camera_connected ? `${status.camera_fps?.toFixed(0) ?? "—"} fps` : "off", status?.camera_connected ? "ok" : "off"],
            ["radar",  status?.radar_connected ? "connected" : "off", status?.radar_connected ? "ok" : "off"],
            ["uno",    status?.uno_connected ? "connected" : "off", status?.uno_connected ? "ok" : "off"],
            ["cpu",    `${status?.cpu_percent?.toFixed(0) ?? "—"}%`, (status?.cpu_percent ?? 0) > 85 ? "warn" : "ok"],
            ["memory", `${status?.memory_percent?.toFixed(0) ?? "—"}%`, (status?.memory_percent ?? 0) > 85 ? "warn" : "ok"],
            ["temp",   status?.temperature_c != null ? `${status.temperature_c.toFixed(1)}°C` : "—", (status?.temperature_c ?? 0) > 75 ? "warn" : "ok"],
            ["uptime", status ? fmtUptime(status.uptime_s) : "—", "ok"],
          ]} />
        </Panel>

        <Panel title="network">
          <KVList rows={[
            ["mode",  status?.ap_mode ? "access point" : "wi-fi client", "ok"],
            ["ssid",  status?.wifi_ssid ?? "—", "ok"],
            ["ip",    status?.ip_address ?? "—", "ok"],
          ]} />
        </Panel>

        <Panel
          title="calibration"
          actions={
            <>
              <Button variant="secondary" size="sm">camera…</Button>
              <Button variant="secondary" size="sm">radar zero</Button>
            </>
          }
        >
          <p className="text-sm text-ink-muted">
            Run camera intrinsics with a checkerboard target before first capture.
            Radar zero learns the cosine angle between the radar boresight and the ball path.
          </p>
        </Panel>

        <Panel title="diagnostics">
          <KVList rows={[
            ["api",        ":8000", "ok"],
            ["ws",         "/ws · live + spectrum", "ok"],
            ["log level",  "info", "ok"],
            ["storage",    "/var/lib/flightimpact", "ok"],
          ]} />
        </Panel>

        <Panel title="danger zone" className="border-signal-bad/30">
          <div className="space-y-3">
            <Row k="restart api" v={<Button variant="danger" size="sm">systemctl restart</Button>} />
            <Row k="clear shot db" v={<Button variant="danger" size="sm">erase all</Button>} />
            <Row k="reboot pi" v={<Button variant="danger" size="sm">reboot</Button>} />
          </div>
        </Panel>

        <div className="cap text-center !text-ink-faint">FlightImpact dev kit · v0.1.0</div>
      </div>
    </div>
  );
}

type DotKind = "ok" | "warn" | "bad" | "off";

function KVList({ rows }: { rows: [string, string, DotKind][] }) {
  return (
    <dl className="divide-y-hair">
      {rows.map(([k, v, kind]) => (
        <div key={k} className="flex items-center justify-between py-2 first:pt-0 last:pb-0">
          <dt className="cap">{k}</dt>
          <dd className="flex items-center gap-2">
            <span className={`dot dot-${kind}`} />
            <span className="lcd text-ink text-sm">{v}</span>
          </dd>
        </div>
      ))}
    </dl>
  );
}

function Row({ k, v }: { k: string; v: ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="cap">{k}</span>
      <div>{v}</div>
    </div>
  );
}
