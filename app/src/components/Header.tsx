import { Logo } from "./Logo";
import { useTelemetry } from "@/lib/store";
import { StatusPill } from "./StatusPill";

export function Header() {
  const { connected, status } = useTelemetry();

  return (
    <header className="pt-safe sticky top-0 z-20 border-b border-line bg-bg/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-2.5">
        <div className="flex items-center gap-3">
          <Logo size={28} />
          <div className="leading-none">
            <div className="font-display text-base font-medium tracking-tight text-ink">
              FlightImpact
            </div>
            <div className="cap mt-0.5">Devkit&nbsp;·&nbsp;#001</div>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <StatusPill
            kind={connected ? "ok" : "bad"}
            label={connected ? "link" : "offline"}
          />
          {connected && (
            <>
              <StatusPill
                kind={status?.camera_connected ? "ok" : "off"}
                label="cam"
                value={status?.camera_connected && status.camera_fps ? `${status.camera_fps.toFixed(0)}` : undefined}
              />
              <StatusPill
                kind={status?.radar_connected ? "ok" : "off"}
                label="radar"
              />
              <StatusPill
                kind={(status?.cpu_percent ?? 0) > 85 ? "warn" : "ok"}
                label="cpu"
                value={status ? `${status.cpu_percent.toFixed(0)}%` : undefined}
              />
            </>
          )}
        </div>
      </div>
    </header>
  );
}
