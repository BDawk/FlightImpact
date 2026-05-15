import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/Button";
import { Panel } from "@/components/Panel";
import { useTelemetry } from "@/lib/store";
import { api } from "@/lib/transport/rest";
import type { ScreenStateSnapshot } from "@/lib/types";

const MODES = ["pair", "home", "status", "pre_shot", "capture", "result"] as const;

export function ScreenDebugPanel() {
  const live = useTelemetry((s) => s.screenState);
  const [screen, setScreen] = useState<ScreenStateSnapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [battery, setBattery] = useState(87);
  const [session, setSession] = useState(3);
  const [boot, setBoot] = useState(1);
  const [macroRunning, setMacroRunning] = useState<string | null>(null);
  const macroRunIdRef = useRef(0);

  useEffect(() => {
    api.getScreenState().then((s) => {
      setScreen(s);
      setBattery(s.battery_pct ?? 87);
      setSession(s.session_id || 1);
      setBoot(s.boot_progress);
    }).catch((e: unknown) => {
      setError(e instanceof Error ? e.message : "Failed to fetch screen state");
    });
  }, []);

  useEffect(() => {
    // Bump run id on unmount so pending timers self-cancel.
    return () => {
      macroRunIdRef.current += 1;
    };
  }, []);

  const apply = async (fn: () => Promise<ScreenStateSnapshot>) => {
    setBusy(true);
    setError(null);
    try {
      const next = await fn();
      setScreen(next);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Screen update failed");
    } finally {
      setBusy(false);
    }
  };

  const applyContext = async () => {
    await apply(() => api.applyScreenScenario({
      battery_pct: battery,
      session_id: session,
      boot_progress: boot,
    }));
  };

  const applyResultDemo = async () => {
    await apply(() => api.applyScreenScenario({
      mode: "result",
      session_id: session,
      battery_pct: battery,
      shot: {
        shot_id: 14,
        ball_speed_mph: 152,
        carry_yd: 241,
        launch_deg: 12.4,
        spin_rpm: 2580,
        smash_factor: 1.49,
        apex_yd: 32,
        hang_s: 6.1,
        side_yd: -4.2,
        quality: "good",
      },
    }));
  };

  const runMacro = async (
    name: string,
    steps: Array<{ waitMs: number; payload: Parameters<typeof api.applyScreenScenario>[0] }>,
    options?: { repeat?: boolean },
  ) => {
    if (macroRunning) return;
    const runId = macroRunIdRef.current + 1;
    macroRunIdRef.current = runId;
    setMacroRunning(name);
    setError(null);

    try {
      do {
        for (const step of steps) {
          await new Promise((resolve) => setTimeout(resolve, step.waitMs));
          if (runId !== macroRunIdRef.current) return;
          const next = await api.applyScreenScenario(step.payload);
          setScreen(next);
        }
      } while (options?.repeat && runId == macroRunIdRef.current);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scenario macro failed");
    } finally {
      setMacroRunning(null);
    }
  };

  const stopMacro = () => {
    macroRunIdRef.current += 1;
    setMacroRunning(null);
  };

  const runBootMacro = async () => {
    await runMacro("Boot", [
      { waitMs: 0, payload: { mode: "boot", boot_progress: 0, battery_pct: battery, session_id: session } },
      { waitMs: 550, payload: { mode: "initializing", boot_progress: 0.2 } },
      { waitMs: 650, payload: { boot_progress: 0.55 } },
      { waitMs: 650, payload: { boot_progress: 0.85 } },
      { waitMs: 550, payload: { boot_progress: 1, mode: "home" } },
    ]);
  };

  const runPairMacro = async () => {
    await runMacro("Pairing", [
      { waitMs: 0, payload: { mode: "pair", battery_pct: battery, session_id: session } },
      { waitMs: 1400, payload: { mode: "pair", clock_hhmm: "AP" } },
      { waitMs: 1200, payload: { mode: "home", clock_hhmm: "" } },
      { waitMs: 900, payload: { mode: "status" } },
      { waitMs: 900, payload: { mode: "home" } },
    ]);
  };

  const runShotMacro = async () => {
    await runMacro("Shot", [
      { waitMs: 0, payload: { mode: "pre_shot", battery_pct: battery, session_id: session } },
      { waitMs: 900, payload: { mode: "capture" } },
      {
        waitMs: 1400,
        payload: {
          mode: "result",
          shot: {
            shot_id: 15,
            ball_speed_mph: 158,
            carry_yd: 253,
            launch_deg: 13.1,
            spin_rpm: 2440,
            smash_factor: 1.51,
            apex_yd: 34,
            hang_s: 6.3,
            side_yd: -2.1,
            quality: "good",
          },
        },
      },
      { waitMs: 1800, payload: { mode: "pre_shot" } },
    ]);
  };

  const runDemoLoopMacro = async () => {
    await runMacro(
      "Demo Loop",
      [
        { waitMs: 0, payload: { mode: "boot", boot_progress: 0.0, battery_pct: battery, session_id: session } },
        { waitMs: 500, payload: { mode: "initializing", boot_progress: 0.2 } },
        { waitMs: 550, payload: { boot_progress: 0.55 } },
        { waitMs: 550, payload: { boot_progress: 0.9 } },
        { waitMs: 500, payload: { mode: "pair", boot_progress: 1.0 } },
        { waitMs: 1400, payload: { mode: "status" } },
        { waitMs: 1000, payload: { mode: "home" } },
        { waitMs: 900, payload: { mode: "pre_shot" } },
        { waitMs: 900, payload: { mode: "capture" } },
        {
          waitMs: 1400,
          payload: {
            mode: "result",
            shot: {
              shot_id: 16,
              ball_speed_mph: 160,
              carry_yd: 257,
              launch_deg: 12.9,
              spin_rpm: 2385,
              smash_factor: 1.52,
              apex_yd: 35,
              hang_s: 6.4,
              side_yd: -1.3,
              quality: "good",
            },
          },
        },
        { waitMs: 1800, payload: { mode: "home" } },
      ],
      { repeat: true },
    );
  };

  return (
    <Panel title="Screen Debug" subtitle="Live scenario control" bodyClassName="space-y-3">
      <div className="rounded-md border border-line bg-bg-input px-2.5 py-2 text-xs text-ink-dim">
        <div className="flex items-center justify-between">
          <span className="cap">mode</span>
          <span className="lcd text-ink">{screen?.mode ?? live?.mode ?? "—"}</span>
        </div>
        <div className="mt-1 flex items-center justify-between">
          <span className="cap">telemetry</span>
          <span className="text-ink-muted">{live ? "streaming" : "idle"}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-1.5">
        {MODES.map((mode) => (
          <Button
            key={mode}
            size="sm"
            variant={screen?.mode === mode ? "primary" : "secondary"}
            disabled={busy}
            onClick={() => apply(() => api.setScreenMode(mode))}
          >
            {mode}
          </Button>
        ))}
      </div>

      <div className="space-y-2 rounded-md border border-line bg-bg-input p-2.5">
        <label className="block">
          <span className="cap">battery %</span>
          <input
            type="number"
            min={1}
            max={100}
            value={battery}
            onChange={(e) => setBattery(Number(e.target.value))}
            className="mt-1 w-full rounded-md border border-line bg-bg px-2 py-1.5 text-sm"
          />
        </label>
        <label className="block">
          <span className="cap">session id</span>
          <input
            type="number"
            min={0}
            value={session}
            onChange={(e) => setSession(Number(e.target.value))}
            className="mt-1 w-full rounded-md border border-line bg-bg px-2 py-1.5 text-sm"
          />
        </label>
        <label className="block">
          <span className="cap">boot progress ({Math.round(boot * 100)}%)</span>
          <input
            type="range"
            min={0}
            max={100}
            value={Math.round(boot * 100)}
            onChange={(e) => setBoot(Number(e.target.value) / 100)}
            className="mt-1 w-full accent-brand"
          />
        </label>
      </div>

      <div className="grid grid-cols-2 gap-1.5">
        <Button size="sm" disabled={busy} onClick={applyContext}>Apply Context</Button>
        <Button size="sm" variant="primary" disabled={busy} onClick={applyResultDemo}>Demo Result</Button>
      </div>

      <div className="space-y-1.5 rounded-md border border-line bg-bg-input p-2.5">
        <div className="cap">Scenario Macros</div>
        <div className="grid grid-cols-3 gap-1.5">
          <Button size="sm" disabled={busy || !!macroRunning} onClick={runBootMacro}>Boot</Button>
          <Button size="sm" disabled={busy || !!macroRunning} onClick={runPairMacro}>Pairing</Button>
          <Button size="sm" disabled={busy || !!macroRunning} onClick={runShotMacro}>Shot Flow</Button>
        </div>
        <Button
          size="sm"
          variant="primary"
          className="w-full"
          disabled={busy || !!macroRunning}
          onClick={runDemoLoopMacro}
        >
          Demo Loop
        </Button>
        <div className="flex items-center justify-between text-xs">
          <span className="text-ink-dim">{macroRunning ? `Running: ${macroRunning}` : "Idle"}</span>
          <Button size="sm" variant="danger" disabled={!macroRunning} onClick={stopMacro}>Stop</Button>
        </div>
      </div>

      {error && <div className="text-xs text-signal-bad">{error}</div>}
    </Panel>
  );
}
