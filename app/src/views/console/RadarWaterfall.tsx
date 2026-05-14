import { useEffect, useRef } from "react";
import { useTelemetry, wsSend } from "@/lib/store";
import { WSCommand } from "@/lib/types";

const HEIGHT = 220;
const WIDTH = 720;

// Mint-leaning colormap — dark blue → teal → mint → yellow on hot peaks
function magToColor(mag: number, min: number, max: number): [number, number, number] {
  const t = Math.max(0, Math.min(1, (mag - min) / (max - min)));
  if (t < 0.25) {
    const k = t / 0.25;
    return [Math.round(8 + k * 18), Math.round(14 + k * 70), Math.round(36 + k * 60)];
  } else if (t < 0.55) {
    const k = (t - 0.25) / 0.3;
    return [Math.round(26), Math.round(84 + k * 110), Math.round(96 + k * 80)];
  } else if (t < 0.85) {
    const k = (t - 0.55) / 0.3;
    return [Math.round(26 + k * 80), Math.round(194 + k * 26), Math.round(176 - k * 110)];
  }
  const k = (t - 0.85) / 0.15;
  return [Math.round(106 + k * 145), Math.round(220 - k * 30), Math.round(66 - k * 66)];
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
    const img = ctx.getImageData(0, 1, WIDTH, HEIGHT - 1);
    ctx.putImageData(img, 0, 0);

    const { magnitudes_db } = spectrum;
    const min = -80, max = 0;
    const row = ctx.createImageData(WIDTH, 1);
    const binCount = magnitudes_db.length;
    for (let x = 0; x < WIDTH; x++) {
      const idx = Math.floor((x / WIDTH) * binCount);
      const mag = magnitudes_db[idx];
      const [r, g, b] = magToColor(mag, min, max);
      const off = x * 4;
      row.data[off] = r; row.data[off + 1] = g; row.data[off + 2] = b; row.data[off + 3] = 255;
    }
    ctx.putImageData(row, 0, HEIGHT - 1);
  }, [spectrum]);

  return (
    <canvas
      ref={canvasRef}
      width={WIDTH}
      height={HEIGHT}
      className="w-full rounded-md border border-line bg-black"
    />
  );
}
