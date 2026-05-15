"""Telemetry — the live messages streamed over the WebSocket.

These are the messages the device pushes to the app in real time:
device status heartbeats, live camera frames (or thumbnails), radar
spectrum snapshots for the dev waterfall view, and shot events.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from core.models.shot import Shot


class TelemetryType(str, Enum):
    DEVICE_STATUS = "device_status"
    LIVE_FRAME = "live_frame"
    RADAR_SPECTRUM = "radar_spectrum"
    SCREEN_STATE = "screen_state"
    SHOT_TRIGGERED = "shot_triggered"
    SHOT_UPDATED = "shot_updated"
    LOG = "log"


class DeviceStatus(BaseModel):
    type: Literal[TelemetryType.DEVICE_STATUS] = TelemetryType.DEVICE_STATUS
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    camera_connected: bool
    camera_fps: Optional[float] = None
    radar_connected: bool
    uno_connected: bool

    cpu_percent: float
    memory_percent: float
    temperature_c: Optional[float] = None
    uptime_s: float

    # Network info — useful for the connection panel
    ap_mode: bool
    wifi_ssid: Optional[str] = None
    ip_address: Optional[str] = None


class LiveFrame(BaseModel):
    """A downsampled JPEG preview frame for the live camera view.

    The full-resolution frames stay on the Pi (in the ring buffer) — only
    these previews are pushed to the app, to keep bandwidth reasonable.
    """

    type: Literal[TelemetryType.LIVE_FRAME] = TelemetryType.LIVE_FRAME
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    width: int
    height: int
    jpeg_b64: str  # base64-encoded JPEG bytes


class RadarSpectrum(BaseModel):
    """A single FFT frame for the dev-mode waterfall display.

    Contains the magnitudes (in dB) for each frequency bin, plus the
    detected peak if any.
    """

    type: Literal[TelemetryType.RADAR_SPECTRUM] = TelemetryType.RADAR_SPECTRUM
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    freq_hz: list[float]
    magnitudes_db: list[float]
    peak_freq_hz: Optional[float] = None
    peak_speed_mph: Optional[float] = None


class ScreenStateUpdated(BaseModel):
    """Screen mode/state snapshot from the on-device renderer service."""

    type: Literal[TelemetryType.SCREEN_STATE] = TelemetryType.SCREEN_STATE
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    mode: str
    boot_progress: float
    session_id: int
    battery_pct: Optional[int] = None
    clock_hhmm: str = ""

    storage_ok: bool
    camera_ok: bool
    radar_ok: bool
    api_ok: bool
    uno_ok: bool

    current_shot_id: Optional[int] = None
    current_ball_speed_mph: Optional[float] = None
    current_quality: Optional[str] = None


class ShotTriggered(BaseModel):
    type: Literal[TelemetryType.SHOT_TRIGGERED] = TelemetryType.SHOT_TRIGGERED
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    shot_id: str


class ShotUpdated(BaseModel):
    type: Literal[TelemetryType.SHOT_UPDATED] = TelemetryType.SHOT_UPDATED
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    shot: Shot


class LogMessage(BaseModel):
    """Server-side log entry streamed to the dev panel."""

    type: Literal[TelemetryType.LOG] = TelemetryType.LOG
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str  # info / warning / error
    source: str  # service name
    message: str


TelemetryMessage = Union[
    DeviceStatus,
    LiveFrame,
    RadarSpectrum,
    ScreenStateUpdated,
    ShotTriggered,
    ShotUpdated,
    LogMessage,
]
