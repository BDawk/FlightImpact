import { useTelemetry } from "@/lib/store";

export function ConnectionBanner() {
  const { connected, status } = useTelemetry();
  if (connected && status?.camera_connected && status?.radar_connected) {
    return null;
  }
  if (!connected) {
    return (
      <div className="bg-signal-bad/15 border-b border-signal-bad/30 px-4 py-2 text-center text-xs text-signal-bad">
        Disconnected from device — reconnecting…
      </div>
    );
  }
  const issues: string[] = [];
  if (!status?.camera_connected) issues.push("camera");
  if (!status?.radar_connected) issues.push("radar");
  return (
    <div className="bg-signal-warn/15 border-b border-signal-warn/30 px-4 py-2 text-center text-xs text-signal-warn">
      Hardware issue: {issues.join(", ")} not connected
    </div>
  );
}
