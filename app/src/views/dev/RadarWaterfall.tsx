import { useEffect, useRef } from "react";
import { useTelemetry, wsSend } from "@/lib/store";
import { WSCommand } from "@/lib/types";

const HEIGHT = 240;
const WIDTH = 600;

function magToColor(mag: number, min: number, max: number): [number, number, number] {
  const t = Math.max(0, Math.min(1, (mag - min) / (max - min)));
  // viridis-like: dark blue -> teal -> green -> yellow
  if (t < 0.25) {
    const k = t / 0.25;
    return [Math.round(20 + k * 30), Math.round(20 + k * 80), Math.round(60 + k * 80)];
  } else if (t < 0.5) {
    const k = (t - 0.25) / 0.25;
    return [Math.round(50), Math.round(100 + k * 80), Math.round(140 + k * 60)];
  } else if (t < 0.75) {
    const k = (t - 0.5) / 0.25;
    return [Math.round(50 + k * 80), Math.round(180 + k * 50), Math.round(200 - k * 100)];
  }
  const k = (t - 0.75) / 0.25;
  return [Math.round(130 + k * 120), Math.round(230 - k * 30), Math.round(100 - k * 100)];
}

export function RadarWaterfall() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const spectrum = useTelemetry((s) => s.spectrum);

  useEffect(() => {
    wsSend(WSCommand.SUBSCRIBE_RADAR_SPECTRUM);
    return () => wsSend(WSCommand.UNSUBSCRIBE_RADAR_SPECTRUM);
  }, []);

  useEffect(() => {
    if (!spectrum || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Scroll existing image up by 1 px
    const img = ctx.getImageData(0, 1, WIDTH, HEIGHT - 1);
    ctx.putImageData(img, 0, 0);

    // Render newest spectrum at the bottom row
    const { magnitudes_db } = spectrum;
    const min = -80;
    const max = 0;
    const row = ctx.createImageData(WIDTH, 1);
    const binCount = magnitudes_db.length;
    for (let x = 0; x < WIDTH; x++) {
      const idx = Math.floor((x / WIDTH) * binCount);
      const mag = magnitudes_db[idx];
      const [r, g, b] = magToColor(mag, min, max);
      const off = x * 4;
      row.data[off] = r;
      row.data[off + 1] = g;
      row.data[off + 2] = b;
      row.data[off + 3] = 255;
    }
    ctx.putImageData(row, 0, HEIGHT - 1);
  }, [spectrum]);

  const peakSpeed = spectrum?.peak_speed_mph;
  const peakFreq = spectrum?.peak_freq_hz;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-ink-dim">
        <span>Frequency →</span>
        <span className="tabular">
          Peak: {peakFreq ? `${peakFreq.toFixed(0)} Hz` : "—"}
          {peakSpeed != null && ` (${peakSpeed.toFixed(1)} mph)`}
        </span>
      </div>
      <canvas
        ref={canvasRef}
        width={WIDTH}
        height={HEIGHT}
        className="w-full rounded-xl border border-line bg-black"
      />
    </div>
  );
}
