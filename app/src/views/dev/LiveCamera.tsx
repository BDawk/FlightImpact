import { useEffect } from "react";
import { useTelemetry, wsSend } from "@/lib/store";
import { WSCommand } from "@/lib/types";

export function LiveCamera() {
  const liveFrame = useTelemetry((s) => s.liveFrame);

  useEffect(() => {
    wsSend(WSCommand.SUBSCRIBE_LIVE_FRAME);
    return () => wsSend(WSCommand.UNSUBSCRIBE_LIVE_FRAME);
  }, []);

  return (
    <div className="overflow-hidden rounded-xl border border-line bg-black">
      <div className="relative aspect-video">
        {liveFrame ? (
          <img
            src={`data:image/jpeg;base64,${liveFrame.jpeg_b64}`}
            alt="Live camera"
            className="h-full w-full object-contain"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-ink-dim">
            Waiting for camera frames…
          </div>
        )}
      </div>
    </div>
  );
}
