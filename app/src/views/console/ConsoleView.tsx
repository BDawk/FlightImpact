import { TelemetryStrip } from "@/components/TelemetryStrip";
import { CameraPanel } from "./CameraPanel";
import { RadarPanel } from "./RadarPanel";
import { ControlsPanel } from "./ControlsPanel";
import { LatestShotPanel } from "./LatestShotPanel";
import { RecentShotsPanel } from "./RecentShotsPanel";

export function ConsoleView() {
  return (
    <div className="bg-grid">
      <div className="mx-auto max-w-6xl space-y-3 p-3 lg:p-4">
        <TelemetryStrip />

        {/* Two-column layout on lg+; stacked below */}
        <div className="grid gap-3 lg:grid-cols-3">
          <div className="space-y-3 lg:col-span-2">
            <CameraPanel />
            <RadarPanel />
            <RecentShotsPanel />
          </div>
          <div className="space-y-3 lg:col-span-1">
            <ControlsPanel />
            <LatestShotPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
