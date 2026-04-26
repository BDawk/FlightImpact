import { useTelemetry } from "@/lib/store";

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
    <div className="mx-auto max-w-2xl space-y-4 p-4">
      <section>
        <h2 className="mb-2 text-xs uppercase tracking-wide text-ink-dim">Device</h2>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 rounded-xl border border-line bg-bg-elev p-4 text-sm">
          <Row k="Camera" v={status?.camera_connected ? `${status.camera_fps?.toFixed(0) ?? "—"} fps` : "Off"} />
          <Row k="Radar" v={status?.radar_connected ? "Connected" : "Off"} />
          <Row k="Uno" v={status?.uno_connected ? "Connected" : "Off"} />
          <Row k="CPU" v={`${status?.cpu_percent?.toFixed(0) ?? "—"}%`} />
          <Row k="Memory" v={`${status?.memory_percent?.toFixed(0) ?? "—"}%`} />
          <Row
            k="Temp"
            v={status?.temperature_c != null ? `${status.temperature_c.toFixed(1)}°C` : "—"}
          />
          <Row k="Uptime" v={status ? fmtUptime(status.uptime_s) : "—"} />
        </dl>
      </section>

      <section>
        <h2 className="mb-2 text-xs uppercase tracking-wide text-ink-dim">Network</h2>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 rounded-xl border border-line bg-bg-elev p-4 text-sm">
          <Row k="Mode" v={status?.ap_mode ? "Hotspot" : "Wi-Fi client"} />
          <Row k="SSID" v={status?.wifi_ssid ?? "—"} />
          <Row k="IP" v={status?.ip_address ?? "—"} />
        </dl>
      </section>

      <section>
        <h2 className="mb-2 text-xs uppercase tracking-wide text-ink-dim">About</h2>
        <div className="rounded-xl border border-line bg-bg-elev p-4 text-sm text-ink-muted">
          FlightImpact dev kit • v0.1.0
        </div>
      </section>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <>
      <dt className="text-ink-dim">{k}</dt>
      <dd className="text-right text-ink tabular">{v}</dd>
    </>
  );
}
