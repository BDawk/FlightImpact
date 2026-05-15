import { Panel } from "@/components/Panel";
import { useTelemetry } from "@/lib/store";
import { LiveCamera } from "./LiveCamera";

export function CameraPanel() {
  const status = useTelemetry((s) => s.status);
  const fps = status?.camera_fps;

  return (
    <Panel
      title="Camera"
      subtitle={
        status?.camera_connected
          ? `USB · ${fps ? `${fps.toFixed(0)} fps` : "connected"}`
          : "No signal"
      }
      bodyClassName="p-3"
    >
      <LiveCamera />
    </Panel>
  );
}
