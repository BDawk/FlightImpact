import { useTelemetry } from "@/lib/store";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine } from "recharts";

export function SpectrumChart() {
  const spectrum = useTelemetry((s) => s.spectrum);
  if (!spectrum) {
    return (
      <div className="flex h-40 items-center justify-center rounded-xl border border-line bg-bg-elev text-sm text-ink-dim">
        Waiting for radar samples…
      </div>
    );
  }

  const data = spectrum.freq_hz
    .map((f, i) => ({ f, m: spectrum.magnitudes_db[i] }))
    .filter((d) => d.f >= 100 && d.f <= 8000);

  return (
    <div className="rounded-xl border border-line bg-bg-elev p-2">
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data}>
          <XAxis
            dataKey="f"
            type="number"
            domain={[0, 8000]}
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`}
          />
          <YAxis
            domain={[-80, 0]}
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            width={28}
          />
          {spectrum.peak_freq_hz && (
            <ReferenceLine x={spectrum.peak_freq_hz} stroke="#1ec98c" strokeDasharray="3 3" />
          )}
          <Line type="monotone" dataKey="m" stroke="#94a3b8" dot={false} strokeWidth={1} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
