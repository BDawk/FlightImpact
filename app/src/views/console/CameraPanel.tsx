import { Panel } from "@/components/Panel";
import { useTelemetry } from "@/lib/store";
import { LiveCamera } from "./LiveCamera";

export function CameraPanel() {
  const status = useTelemetry((s) => s.status);
  return (
    <Panel
      title="live camera"
      subtitle={
        status?.camera_connected ? "USB cam · capturing" : "no signal"
      }
      bodyClassName="p-3"
    >
      <LiveCamera />
    </Panel>
  );
}
