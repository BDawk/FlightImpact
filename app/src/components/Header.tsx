import { useState } from "react";
import { Logo } from "./Logo";
import { useTelemetry } from "@/lib/store";
import { SettingsModal } from "./SettingsModal";

export function Header() {
  const { connected, status } = useTelemetry();
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <>
      <header className="pt-safe sticky top-0 z-20 border-b border-line bg-bg/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-2.5">
          {/* Left — logo + wordmark */}
          <div className="flex items-center gap-3">
            <Logo size={28} />
            <div className="leading-none">
              <div className="font-display text-base font-medium tracking-tight text-ink">
                FlightImpact
              </div>
              <div className="cap mt-0.5 !text-ink-dim">Development Kit</div>
            </div>
          </div>

          {/* Right — connection status + settings */}
          <div className="flex items-center gap-2">
            <ConnectionPill connected={connected} />

            <button
              onClick={() => setSettingsOpen(true)}
              aria-label="Open settings"
              className="flex h-7 w-7 items-center justify-center rounded-md text-ink-muted transition-colors hover:bg-bg-panel hover:text-ink"
            >
              <GearIcon />
            </button>
          </div>
        </div>
      </header>

      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </>
  );
}

function ConnectionPill({ connected }: { connected: boolean }) {
  return (
    <div
      className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
        connected
          ? "border-signal-ok/30 bg-signal-ok/10 text-signal-ok"
          : "border-signal-bad/30 bg-signal-bad/10 text-signal-bad"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          connected ? "bg-signal-ok animate-pulse" : "bg-signal-bad"
        }`}
      />
      {connected ? "Connected" : "Offline"}
    </div>
  );
}

function GearIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="8" cy="8" r="2.5" />
      <path d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M2.93 2.93l1.06 1.06M12.01 12.01l1.06 1.06M2.93 13.07l1.06-1.06M12.01 3.99l1.06-1.06" />
    </svg>
  );
}
