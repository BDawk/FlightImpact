import { useTelemetry } from "@/lib/store";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine, CartesianGrid } from "recharts";

export function SpectrumChart() {
  const spectrum = useTelemetry((s) => s.spectrum);
  if (!spectrum) {
    return (
      <div className="flex h-[220px] items-center justify-center rounded-md border border-line bg-bg-input text-sm text-ink-dim">
        waiting for radar samples…
      </div>
    );
  }

  const data = spectrum.freq_hz
    .map((f, i) => ({ f, m: spectrum.magnitudes_db[i] }))
    .filter((d) => d.f >= 100 && d.f <= 8000);

  return (
    <div className="rounded-md border border-line bg-bg-input p-2">
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid stroke="#1f2a38" strokeDasharray="2 4" vertical={false} />
          <XAxis
            dataKey="f"
            type="number"
            domain={[0, 8000]}
            tick={{ fill: "#5d6a78", fontSize: 10, fontFamily: "JetBrains Mono Variable" }}
            tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`}
            stroke="#1f2a38"
          />
          <YAxis
            domain={[-80, 0]}
            tick={{ fill: "#5d6a78", fontSize: 10, fontFamily: "JetBrains Mono Variable" }}
            width={28}
            stroke="#1f2a38"
          />
          {spectrum.peak_freq_hz && (
            <ReferenceLine x={spectrum.peak_freq_hz} stroke="#34d399" strokeDasharray="3 3" />
          )}
          <Line type="monotone" dataKey="m" stroke="#8a96a3" dot={false} strokeWidth={1.2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
