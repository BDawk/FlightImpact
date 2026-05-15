import { useEffect, useRef } from "react";
import { Panel } from "./Panel";
import { Button } from "./Button";
import type { ReactNode } from "react";

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
}

export function SettingsModal({ open, onClose }: SettingsModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  // Close on Escape
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  // Lock body scroll
  useEffect(() => {
    if (open) document.body.style.overflow = "hidden";
    else document.body.style.overflow = "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-start justify-center bg-bg/70 backdrop-blur-sm pt-16 px-4 pb-4 overflow-y-auto"
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <div className="w-full max-w-lg space-y-3 animate-in">
        {/* Modal header */}
        <div className="flex items-center justify-between px-1">
          <h2 className="font-display text-lg font-medium text-ink tracking-tight">Settings</h2>
          <button
            onClick={onClose}
            className="flex h-7 w-7 items-center justify-center rounded-md text-ink-muted hover:text-ink hover:bg-bg-panel transition-colors"
            aria-label="Close settings"
          >
            <CloseIcon />
          </button>
        </div>

        <CalibrationPanel />
        <AppPanel />
        <DangerPanel />

        <div className="cap text-center !text-ink-faint pb-2">
          FlightImpact Development Kit · v0.1.0
        </div>
      </div>
    </div>
  );
}

function CalibrationPanel() {
  return (
    <Panel
      title="Calibration"
      actions={
        <>
          <Button variant="secondary" size="sm">Camera…</Button>
          <Button variant="secondary" size="sm">Radar zero</Button>
        </>
      }
    >
      <p className="text-sm text-ink-muted leading-relaxed">
        Run camera intrinsics with a checkerboard target before first capture.
        Radar zero calibrates the cosine angle between the radar boresight and ball flight path.
      </p>
    </Panel>
  );
}

function AppPanel() {
  return (
    <Panel title="App">
      <div className="space-y-3">
        <Row label="Theme">
          <div className="flex gap-1">
            <Button variant="primary" size="sm">Dark</Button>
            <Button variant="secondary" size="sm" disabled>Light</Button>
          </div>
        </Row>
        <Row label="Units">
          <div className="flex gap-1">
            <Button variant="primary" size="sm">Yards</Button>
            <Button variant="secondary" size="sm">Meters</Button>
          </div>
        </Row>
        <Row label="Shot buffer">
          <span className="lcd text-sm text-ink">50 shots</span>
        </Row>
      </div>
    </Panel>
  );
}

function DangerPanel() {
  return (
    <Panel title="Danger Zone" className="border-signal-bad/30">
      <div className="space-y-3">
        <Row label="Restart API service">
          <Button variant="danger" size="sm">Restart</Button>
        </Row>
        <Row label="Clear all shot data">
          <Button variant="danger" size="sm">Erase all</Button>
        </Row>
        <Row label="Reboot device">
          <Button variant="danger" size="sm">Reboot</Button>
        </Row>
      </div>
    </Panel>
  );
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="cap">{label}</span>
      <div>{children}</div>
    </div>
  );
}

function CloseIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <path d="M2 2l10 10M12 2L2 12" />
    </svg>
  );
}
