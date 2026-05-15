import { useState } from "react";
import { Panel, PanelButton } from "@/components/Panel";
import { useTelemetry } from "@/lib/store";
import { RadarWaterfall } from "./RadarWaterfall";
import { SpectrumChart } from "./SpectrumChart";

type Mode = "waterfall" | "spectrum";

export function RadarPanel() {
  const [mode, setMode] = useState<Mode>("waterfall");
  const spectrum = useTelemetry((s) => s.spectrum);
  const status = useTelemetry((s) => s.status);

  return (
    <Panel
      title="Radar"
      subtitle={status?.radar_connected ? "HB100 · 10.525 GHz" : "No signal"}
      actions={
        <>
          <PanelButton active={mode === "waterfall"} onClick={() => setMode("waterfall")}>
            Waterfall
          </PanelButton>
          <PanelButton active={mode === "spectrum"} onClick={() => setMode("spectrum")}>
            Spectrum
          </PanelButton>
        </>
      }
      bodyClassName="space-y-2"
    >
      {mode === "waterfall" ? <RadarWaterfall /> : <SpectrumChart />}

      {/* Footer readout strip */}
      <div className="flex items-center justify-between rounded-md border border-line bg-bg-input px-2.5 py-1.5 text-xs">
        <span className="cap">Peak</span>
        <span className="lcd text-ink">
          {spectrum?.peak_freq_hz ? `${spectrum.peak_freq_hz.toFixed(0)}` : "—"}
          <span className="ml-0.5 text-ink-dim text-[10px]">Hz</span>
        </span>
        <span className="cap">→ Ball speed</span>
        <span className="lcd text-brand">
          {spectrum?.peak_speed_mph != null ? spectrum.peak_speed_mph.toFixed(1) : "—"}
          <span className="ml-0.5 text-ink-dim text-[10px]">mph</span>
        </span>
      </div>
    </Panel>
  );
}
