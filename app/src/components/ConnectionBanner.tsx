import { useTelemetry } from "@/lib/store";

export function ConnectionBanner() {
  const { connected, status } = useTelemetry();

  // All clear — show nothing
  if (connected && status?.camera_connected && status?.radar_connected) {
    return null;
  }

  // WebSocket is down — can't reach the device at all
  if (!connected) {
    return (
      <Banner kind="bad">
        <span className="font-medium">Device unreachable</span>
        <span className="text-signal-bad/70"> · attempting to reconnect to flightimpact.local…</span>
      </Banner>
    );
  }

  // Connected but some hardware is missing
  const issues: string[] = [];
  if (!status?.camera_connected) issues.push("camera not detected");
  if (!status?.radar_connected) issues.push("radar not detected");

  return (
    <Banner kind="warn">
      <span className="font-medium">Degraded</span>
      <span className="text-signal-warn/70"> · {issues.join(", ")}</span>
    </Banner>
  );
}

function Banner({ kind, children }: { kind: "bad" | "warn"; children: React.ReactNode }) {
  const colors =
    kind === "bad"
      ? "border-signal-bad/30 bg-signal-bad/10 text-signal-bad"
      : "border-signal-warn/30 bg-signal-warn/10 text-signal-warn";

  return (
    <div className={`border-b px-4 py-1.5 text-center text-xs ${colors}`}>
      {children}
    </div>
  );
}
