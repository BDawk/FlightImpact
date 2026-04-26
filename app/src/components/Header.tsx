import { useTelemetry } from "@/lib/store";
import { StatusPill } from "./StatusPill";

export function Header() {
  const { connected, status } = useTelemetry();
  const cameraOk = status?.camera_connected;
  const radarOk = status?.radar_connected;

  return (
    <header className="pt-safe sticky top-0 z-10 border-b border-line bg-bg-elev/95 backdrop-blur">
      <div className="mx-auto flex max-w-2xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <svg width="22" height="22" viewBox="0 0 64 64" aria-hidden>
            <path d="M14 50 L32 14 L50 50 Z" fill="none" stroke="#1ec98c" strokeWidth="3" strokeLinejoin="round" />
            <circle cx="32" cy="40" r="4" fill="#1ec98c" />
          </svg>
          <span className="text-sm font-semibold tracking-wide text-ink">FlightImpact</span>
        </div>
        <div className="flex items-center gap-1.5">
          <StatusPill kind={connected ? "ok" : "bad"} label={connected ? "Online" : "Offline"} />
          {connected && (
            <>
              <StatusPill kind={cameraOk ? "ok" : "bad"} label="Cam" />
              <StatusPill kind={radarOk ? "ok" : "bad"} label="Radar" />
            </>
          )}
        </div>
      </div>
    </header>
  );
}
