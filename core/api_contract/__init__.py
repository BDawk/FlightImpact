"""API contract — REST + WebSocket schema definition.

This module defines the contract between any device (dev kit or production)
and any client (PWA, future native app). It generates the OpenAPI spec that
the frontend's TypeScript types are derived from.

Versioning rule: any breaking change to a message bumps API_VERSION.
"""

from __future__ import annotations

API_VERSION = "0.1.0"


# REST endpoints — the device exposes these for non-realtime data.
REST_ROUTES = {
    "GET /api/v1/status": "Current device status (also pushed via WS)",
    "GET /api/v1/shots": "List recent shots (paginated)",
    "GET /api/v1/shots/{id}": "Single shot by ID",
    "POST /api/v1/shots/{id}/notes": "Add or update notes / club for a shot",
    "POST /api/v1/shots/{id}/reference": "Log reference monitor metrics (dev kit)",
    "GET /api/v1/calibration/camera": "Current camera calibration",
    "POST /api/v1/calibration/camera": "Upload new camera calibration",
    "GET /api/v1/calibration/radar": "Current radar calibration",
    "POST /api/v1/calibration/radar": "Update radar calibration parameters",
    "POST /api/v1/test/trigger": "Manually trigger a test shot (dev kit)",
    "GET /api/v1/screen/state": "Current on-device screen state",
    "POST /api/v1/screen/mode": "Force a specific screen mode (dev mode)",
    "POST /api/v1/screen/scenario": "Apply a scenario payload to screen state (dev mode)",
    "GET /api/v1/clip/{id}": "Download raw clip for a shot (dev kit)",
}


# WebSocket — clients connect to /ws and receive TelemetryMessage frames.
WS_PATH = "/ws"


# Client-to-server messages — used to subscribe/unsubscribe to high-bandwidth
# streams. By default a client receives device_status + shot events; live frames
# and radar spectrum require explicit subscription (they are bandwidth-heavy
# and only used in the dev panel).
class WSCommand:
    SUBSCRIBE_LIVE_FRAME = "subscribe_live_frame"
    UNSUBSCRIBE_LIVE_FRAME = "unsubscribe_live_frame"
    SUBSCRIBE_RADAR_SPECTRUM = "subscribe_radar_spectrum"
    UNSUBSCRIBE_RADAR_SPECTRUM = "unsubscribe_radar_spectrum"
    SUBSCRIBE_LOGS = "subscribe_logs"
    UNSUBSCRIBE_LOGS = "unsubscribe_logs"
    SUBSCRIBE_SCREEN_STATE = "subscribe_screen_state"
    UNSUBSCRIBE_SCREEN_STATE = "unsubscribe_screen_state"
