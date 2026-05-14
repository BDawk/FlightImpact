import { useTelemetry } from "@/lib/store";

function fmtUptime(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (h > 0) return `${h}h${m.toString().padStart(2, "0")}m`;
  return `${m}m${(Math.floor(s) % 60).toString().padStart(2, "0")}s`;
}

export function TelemetryStrip() {
  const status = useTelemetry((s) => s.status);
  return (
    <div className="panel grid grid-cols-2 gap-x-4 gap-y-2 px-4 py-2.5 text-xs sm:grid-cols-4 lg:grid-cols-7">
      <Cell label="cpu"    value={status ? `${status.cpu_percent.toFixed(0)}` : "—"} unit="%" />
      <Cell label="mem"    value={status ? `${status.memory_percent.toFixed(0)}` : "—"} unit="%" />
      <Cell label="temp"   value={status?.temperature_c != null ? status.temperature_c.toFixed(1) : "—"} unit="°C" />
      <Cell label="fps"    value={status?.camera_fps != null ? status.camera_fps.toFixed(0) : "—"} />
      <Cell label="uptime" value={status ? fmtUptime(status.uptime_s) : "—"} />
      <Cell label="ssid"   value={status?.wifi_ssid ?? "—"} small />
      <Cell label="ip"     value={status?.ip_address ?? "—"} small />
    </div>
  );
}

function Cell({ label, value, unit, small }: { label: string; value: string; unit?: string; small?: boolean }) {
  return (
    <div className="flex items-center gap-2 overflow-hidden">
      <span className="cap shrink-0">{label}</span>
      <span className={small ? "lcd truncate text-xs text-ink" : "lcd text-ink"}>
        {value}
        {unit && <span className="ml-0.5 text-ink-dim text-[10px]">{unit}</span>}
      </span>
    </div>
  );
}
