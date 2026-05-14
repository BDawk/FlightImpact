import { useEffect } from "react";
import { useTelemetry, wsSend } from "@/lib/store";
import { WSCommand } from "@/lib/types";

export function LiveCamera() {
  const liveFrame = useTelemetry((s) => s.liveFrame);
  const status = useTelemetry((s) => s.status);

  useEffect(() => {
    wsSend(WSCommand.SUBSCRIBE_LIVE_FRAME);
    return () => wsSend(WSCommand.UNSUBSCRIBE_LIVE_FRAME);
  }, []);

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-md border border-line bg-black">
      {liveFrame ? (
        <img
          src={`data:image/jpeg;base64,${liveFrame.jpeg_b64}`}
          alt="Live camera"
          className="h-full w-full object-contain"
        />
      ) : (
        <div className="flex h-full items-center justify-center text-sm text-ink-dim">
          waiting for camera frames…
        </div>
      )}

      {/* Top-left source label */}
      <div className="pointer-events-none absolute left-2 top-2 rounded bg-black/60 px-1.5 py-0.5 text-[10px] uppercase tracking-cap text-ink-muted">
        cam0&nbsp;·&nbsp;{liveFrame ? `${liveFrame.width}x${liveFrame.height}` : "—"}
      </div>

      {/* Top-right live indicator + fps */}
      <div className="pointer-events-none absolute right-2 top-2 flex items-center gap-1.5 rounded bg-black/60 px-1.5 py-0.5 text-[10px] uppercase tracking-cap text-ink-muted">
        <span className={`dot ${liveFrame ? "dot-ok" : "dot-off"}`} />
        live&nbsp;{status?.camera_fps != null ? `${status.camera_fps.toFixed(0)} fps` : ""}
      </div>

      {/* Bottom-right timestamp */}
      {liveFrame && (
        <div className="pointer-events-none absolute bottom-2 right-2 lcd rounded bg-black/60 px-1.5 py-0.5 text-[10px] text-ink-muted">
          {new Date(liveFrame.timestamp).toLocaleTimeString(undefined, { hour12: false })}
        </div>
      )}

      {/* Faint scanlines for instrument feel */}
      <div className="pointer-events-none absolute inset-0 scanlines mix-blend-overlay" />
    </div>
  );
}
