import { useTelemetry } from "@/lib/store";

export function ConnectionBanner() {
  const { connected, status } = useTelemetry();
  if (connected && status?.camera_connected && status?.radar_connected) {
    return null;
  }
  if (!connected) {
    return (
      <div className="border-b border-signal-bad/30 bg-signal-bad/10 px-4 py-1.5 text-center text-xs text-signal-bad">
        <span className="cap !text-signal-bad">link down</span>
        &nbsp;reconnecting to flightimpact.local…
      </div>
    );
  }
  const issues: string[] = [];
  if (!status?.camera_connected) issues.push("camera");
  if (!status?.radar_connected) issues.push("radar");
  return (
    <div className="border-b border-signal-warn/30 bg-signal-warn/10 px-4 py-1.5 text-center text-xs text-signal-warn">
      <span className="cap !text-signal-warn">degraded</span>
      &nbsp;{issues.join(" + ")} not connected
    </div>
  );
}
