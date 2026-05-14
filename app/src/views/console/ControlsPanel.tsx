import { useState } from "react";
import { Panel } from "@/components/Panel";
import { Button } from "@/components/Button";
import { api } from "@/lib/transport/rest";

export function ControlsPanel() {
  const [busy, setBusy] = useState(false);
  const [autoTrigger, setAutoTrigger] = useState(true);
  const [threshold, setThreshold] = useState(40);
  const [units, setUnits] = useState<"yd" | "m">("yd");

  const fire = async () => {
    setBusy(true);
    try { await api.triggerTestShot(); }
    catch (e) { console.error(e); }
    finally { setBusy(false); }
  };

  return (
    <Panel title="controls" bodyClassName="space-y-3.5">
      <Button
        variant="primary"
        size="md"
        onClick={fire}
        disabled={busy}
        className="w-full"
      >
        {busy ? "triggering…" : "Fire test shot"}
      </Button>

      <Toggle
        label="auto-trigger"
        hint="capture on Doppler peak"
        on={autoTrigger}
        onChange={setAutoTrigger}
      />

      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="cap">trigger threshold</span>
          <span className="lcd text-ink text-xs">
            -{threshold}<span className="text-ink-dim text-[10px] ml-0.5">dB</span>
          </span>
        </div>
        <input
          type="range"
          min="20"
          max="60"
          value={threshold}
          onChange={(e) => setThreshold(Number(e.target.value))}
          className="w-full accent-brand"
        />
      </div>

      <div className="space-y-1.5">
        <div className="cap">units</div>
        <div className="grid grid-cols-2 gap-1">
          <Button variant={units === "yd" ? "primary" : "secondary"} size="sm" onClick={() => setUnits("yd")}>
            yards
          </Button>
          <Button variant={units === "m" ? "primary" : "secondary"} size="sm" onClick={() => setUnits("m")}>
            meters
          </Button>
        </div>
      </div>
    </Panel>
  );
}

function Toggle({ label, hint, on, onChange }: {
  label: string; hint?: string; on: boolean; onChange: (v: boolean) => void;
}) {
  return (
    <button
      onClick={() => onChange(!on)}
      className="flex w-full items-center justify-between rounded-md border border-line bg-bg-input px-2.5 py-2 text-left transition-colors hover:border-line-strong"
    >
      <div>
        <div className="cap">{label}</div>
        {hint && <div className="mt-0.5 text-xs text-ink-dim">{hint}</div>}
      </div>
      <span
        className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${
          on ? "bg-brand" : "bg-line"
        }`}
      >
        <span
          className={`absolute top-0.5 h-4 w-4 rounded-full bg-bg shadow transition-transform ${
            on ? "translate-x-4" : "translate-x-0.5"
          }`}
        />
      </span>
    </button>
  );
}
