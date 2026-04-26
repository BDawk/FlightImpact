import { useState } from "react";
import { LiveCamera } from "./LiveCamera";
import { RadarWaterfall } from "./RadarWaterfall";
import { SpectrumChart } from "./SpectrumChart";
import { api } from "@/lib/transport/rest";

export function DevView() {
  const [busy, setBusy] = useState(false);
  const [showWaterfall, setShowWaterfall] = useState(true);

  const fire = async () => {
    setBusy(true);
    try {
      await api.triggerTestShot();
    } catch (e) {
      console.error(e);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-4">
      <header className="flex items-center justify-between">
        <h1 className="text-base font-semibold text-ink">Dev panel</h1>
        <button
          onClick={fire}
          disabled={busy}
          className="rounded-lg bg-brand px-3 py-1.5 text-sm font-medium text-white transition hover:bg-brand-glow disabled:opacity-50"
        >
          {busy ? "Triggering…" : "Manual trigger"}
        </button>
      </header>

      <section className="space-y-2">
        <div className="text-xs uppercase tracking-wide text-ink-dim">Live camera</div>
        <LiveCamera />
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="text-xs uppercase tracking-wide text-ink-dim">Radar Doppler</div>
          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => setShowWaterfall(true)}
              className={`rounded px-2 py-0.5 ${showWaterfall ? "bg-bg-panel text-ink" : "text-ink-dim"}`}
            >
              Waterfall
            </button>
            <button
              onClick={() => setShowWaterfall(false)}
              className={`rounded px-2 py-0.5 ${!showWaterfall ? "bg-bg-panel text-ink" : "text-ink-dim"}`}
            >
              Spectrum
            </button>
          </div>
        </div>
        {showWaterfall ? <RadarWaterfall /> : <SpectrumChart />}
      </section>

      <section className="rounded-xl border border-line bg-bg-elev p-3 text-xs text-ink-muted">
        <div className="mb-1 text-ink-dim">Tip</div>
        Subscribe-on-mount means these streams only run while the dev tab is
        open — the device doesn't waste bandwidth pushing frames the rest of
        the time.
      </section>
    </div>
  );
}
