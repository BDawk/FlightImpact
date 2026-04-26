import { create } from "zustand";
import { telemetrySocket } from "@/lib/transport/socket";
import type {
  DeviceStatus,
  LiveFrame,
  RadarSpectrum,
  Shot,
  TelemetryMessage,
} from "@/lib/types";

interface TelemetryState {
  connected: boolean;
  status: DeviceStatus | null;
  liveFrame: LiveFrame | null;
  spectrum: RadarSpectrum | null;
  recentShots: Shot[];
  start: () => void;
  stop: () => void;
}

export const useTelemetry = create<TelemetryState>((set, get) => {
  let started = false;

  const handleMessage = (msg: TelemetryMessage) => {
    switch (msg.type) {
      case "device_status":
        set({ status: msg });
        break;
      case "live_frame":
        set({ liveFrame: msg });
        break;
      case "radar_spectrum":
        set({ spectrum: msg });
        break;
      case "shot_updated": {
        const existing = get().recentShots;
        const idx = existing.findIndex((s) => s.id === msg.shot.id);
        if (idx >= 0) {
          const next = [...existing];
          next[idx] = msg.shot;
          set({ recentShots: next });
        } else {
          set({ recentShots: [msg.shot, ...existing].slice(0, 50) });
        }
        break;
      }
      default:
        break;
    }
  };

  return {
    connected: false,
    status: null,
    liveFrame: null,
    spectrum: null,
    recentShots: [],
    start() {
      if (started) return;
      started = true;
      telemetrySocket.onMessage(handleMessage);
      telemetrySocket.onConnectionChange((connected) => set({ connected }));
      telemetrySocket.start();
    },
    stop() {
      telemetrySocket.stop();
      started = false;
    },
  };
});

export const wsSend = (cmd: string) => telemetrySocket.send(cmd);
