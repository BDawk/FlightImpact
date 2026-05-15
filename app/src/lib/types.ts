// Mirror of core/models — kept in sync by hand for now. A future improvement
// is to generate this from the OpenAPI spec the FastAPI app produces.

export type ShotStatus = "triggered" | "capturing" | "processing" | "complete" | "failed";

export interface ShotMetrics {
  ball_speed_mph: number | null;
  club_speed_mph: number | null;
  smash_factor: number | null;
  launch_angle_deg: number | null;
  launch_direction_deg: number | null;
  spin_rate_rpm: number | null;
  spin_axis_deg: number | null;
  carry_yards: number | null;
  total_distance_yards: number | null;
  apex_yards: number | null;
  flight_time_s: number | null;
  confidence: Record<string, number>;
}

export interface Shot {
  id: string;
  captured_at: string;
  session_id: string | null;
  status: ShotStatus;
  metrics: ShotMetrics;
  clip_path: string | null;
  radar_path: string | null;
  reference_metrics: ShotMetrics | null;
  reference_source: string | null;
  notes: string | null;
  club: string | null;
}

export interface DeviceStatus {
  type: "device_status";
  timestamp: string;
  camera_connected: boolean;
  camera_fps: number | null;
  radar_connected: boolean;
  uno_connected: boolean;
  cpu_percent: number;
  memory_percent: number;
  temperature_c: number | null;
  uptime_s: number;
  ap_mode: boolean;
  wifi_ssid: string | null;
  ip_address: string | null;
}

export interface LiveFrame {
  type: "live_frame";
  timestamp: string;
  width: number;
  height: number;
  jpeg_b64: string;
}

export interface RadarSpectrum {
  type: "radar_spectrum";
  timestamp: string;
  freq_hz: number[];
  magnitudes_db: number[];
  peak_freq_hz: number | null;
  peak_speed_mph: number | null;
}

export interface ScreenStateUpdated {
  type: "screen_state";
  timestamp: string;
  mode: string;
  boot_progress: number;
  session_id: number;
  battery_pct: number | null;
  clock_hhmm: string;
  storage_ok: boolean;
  camera_ok: boolean;
  radar_ok: boolean;
  api_ok: boolean;
  uno_ok: boolean;
  current_shot_id: number | null;
  current_ball_speed_mph: number | null;
  current_quality: string | null;
}

export interface ScreenShotScenario {
  shot_id: number;
  ball_speed_mph: number;
  carry_yd: number;
  launch_deg: number;
  spin_rpm: number;
  smash_factor: number;
  apex_yd?: number;
  hang_s?: number;
  side_yd?: number;
  quality?: string;
}

export interface ScreenScenarioUpdate {
  mode?: string;
  boot_progress?: number;
  battery_pct?: number;
  session_id?: number;
  clock_hhmm?: string;
  brightness?: number;
  shot?: ScreenShotScenario;
}

export interface ScreenStateSnapshot {
  mode: string;
  boot_progress: number;
  boot_version: string;
  session_id: number;
  battery_pct: number | null;
  clock_hhmm: string;
  services: {
    storage_ok: boolean;
    camera_ok: boolean;
    radar_ok: boolean;
    api_ok: boolean;
    uno_ok: boolean;
    camera_fps: number | null;
    camera_resolution: string;
    radar_db: number | null;
    storage_free_gb: number | null;
    api_port: number;
  };
  current_shot: {
    shot_id: number;
    ball_speed_mph: number;
    carry_yd: number;
    launch_deg: number;
    spin_rpm: number;
    smash_factor: number;
    apex_yd: number;
    hang_s: number;
    side_yd: number;
    quality: string;
  } | null;
}

export interface ShotTriggered {
  type: "shot_triggered";
  timestamp: string;
  shot_id: string;
}

export interface ShotUpdated {
  type: "shot_updated";
  timestamp: string;
  shot: Shot;
}

export interface LogMessage {
  type: "log";
  timestamp: string;
  level: "info" | "warning" | "error";
  source: string;
  message: string;
}

export type TelemetryMessage =
  | DeviceStatus
  | LiveFrame
  | RadarSpectrum
  | ScreenStateUpdated
  | ShotTriggered
  | ShotUpdated
  | LogMessage;

export const WSCommand = {
  SUBSCRIBE_LIVE_FRAME: "subscribe_live_frame",
  UNSUBSCRIBE_LIVE_FRAME: "unsubscribe_live_frame",
  SUBSCRIBE_RADAR_SPECTRUM: "subscribe_radar_spectrum",
  UNSUBSCRIBE_RADAR_SPECTRUM: "unsubscribe_radar_spectrum",
  SUBSCRIBE_LOGS: "subscribe_logs",
  UNSUBSCRIBE_LOGS: "unsubscribe_logs",
  SUBSCRIBE_SCREEN_STATE: "subscribe_screen_state",
  UNSUBSCRIBE_SCREEN_STATE: "unsubscribe_screen_state",
} as const;
