import type { TelemetryMessage } from "@/lib/types";

type Listener = (msg: TelemetryMessage) => void;

export class TelemetrySocket {
  private ws: WebSocket | null = null;
  private listeners = new Set<Listener>();
  private connectListeners = new Set<(connected: boolean) => void>();
  private url: string;
  private reconnectMs = 1000;
  private alive = true;
  private pendingCommands: string[] = [];

  constructor(url?: string) {
    if (url) {
      this.url = url;
    } else {
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      this.url = `${proto}//${window.location.host}/ws`;
    }
  }

  start(): void {
    this.alive = true;
    this.connect();
  }

  stop(): void {
    this.alive = false;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(fn: Listener): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  onConnectionChange(fn: (connected: boolean) => void): () => void {
    this.connectListeners.add(fn);
    return () => this.connectListeners.delete(fn);
  }

  send(command: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(command);
    } else {
      // Queue and replay after reconnect
      this.pendingCommands.push(command);
    }
  }

  private connect(): void {
    try {
      this.ws = new WebSocket(this.url);
    } catch (e) {
      this.scheduleReconnect();
      return;
    }
    this.ws.onopen = () => {
      this.reconnectMs = 1000;
      this.connectListeners.forEach((fn) => fn(true));
      // Replay any pending commands (e.g. subscriptions)
      const queued = [...this.pendingCommands];
      this.pendingCommands = [];
      queued.forEach((c) => this.send(c));
    };
    this.ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as TelemetryMessage;
        this.listeners.forEach((fn) => fn(data));
      } catch (e) {
        console.warn("Bad telemetry payload", e);
      }
    };
    this.ws.onclose = () => {
      this.connectListeners.forEach((fn) => fn(false));
      this.ws = null;
      if (this.alive) this.scheduleReconnect();
    };
    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  private scheduleReconnect(): void {
    setTimeout(() => {
      if (this.alive) this.connect();
    }, this.reconnectMs);
    // Exponential backoff up to 8s
    this.reconnectMs = Math.min(this.reconnectMs * 1.6, 8000);
  }
}

export const telemetrySocket = new TelemetrySocket();
