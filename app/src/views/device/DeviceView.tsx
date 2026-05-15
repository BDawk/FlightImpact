import { Panel } from "@/components/Panel";
import { useTelemetry } from "@/lib/store";
import { CameraPanel } from "@/views/console/CameraPanel";
import { RadarPanel } from "@/views/console/RadarPanel";

function fmtUptime(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${sec}s`;
  return `${sec}s`;
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

export function DeviceView() {
  const status = useTelemetry((s) => s.status);

  const cpuKind: DotKind  = (status?.cpu_percent ?? 0) > 85 ? "warn" : "ok";
  const memKind: DotKind  = (status?.memory_percent ?? 0) > 85 ? "warn" : "ok";
  const tempKind: DotKind = (status?.temperature_c ?? 0) > 75 ? "warn" : "ok";

  return (
    <div className="bg-grid">
      <div className="mx-auto max-w-6xl p-3 lg:p-4">
        <div className="grid gap-3 lg:grid-cols-3">

          {/* Left — live camera + radar (2/3 width) */}
          <div className="space-y-3 lg:col-span-2">
            <CameraPanel />
            <RadarPanel />
          </div>

          {/* Right — system info panels (1/3 width) */}
          <div className="space-y-3">

            <Panel title="System" subtitle="Raspberry Pi 5">
              <KVList rows={[
                ["Camera",  status?.camera_connected ? `${status.camera_fps?.toFixed(0) ?? "—"} fps` : "Not detected", status?.camera_connected ? "ok" : "bad"],
                ["Radar",   status?.radar_connected  ? "Connected" : "Not detected",  status?.radar_connected  ? "ok" : "bad"],
                ["Trigger", status?.uno_connected    ? "Connected" : "Not present",   status?.uno_connected    ? "ok" : "off"],
                ["CPU",     `${status?.cpu_percent?.toFixed(0) ?? "—"}%`,  cpuKind],
                ["Memory",  `${status?.memory_percent?.toFixed(0) ?? "—"}%`, memKind],
                ["Temp",    status?.temperature_c != null ? `${status.temperature_c.toFixed(1)} °C` : "—", tempKind],
                ["Uptime",  status ? fmtUptime(status.uptime_s) : "—", "ok"],
              ]} />
            </Panel>

            <Panel title="Network">
              <KVList rows={[
                ["Mode", status?.ap_mode ? "Access point" : "Wi-Fi client", "ok"],
                ["SSID", status?.wifi_ssid ?? "—", "ok"],
                ["IP",   status?.ip_address ?? "—", "ok"],
              ]} />
            </Panel>

            <Panel title="Diagnostics">
              <KVList rows={[
                ["API",       ":8000",              "ok"],
                ["WebSocket", "/ws",                "ok"],
                ["Log level", "info",               "ok"],
                ["Storage",   "/var/lib/flightimpact", "ok"],
              ]} />
            </Panel>

          </div>
        </div>
      </div>
    </div>
  );
}
