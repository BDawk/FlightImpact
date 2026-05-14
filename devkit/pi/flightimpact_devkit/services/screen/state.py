"""ScreenState — the dataclass passed to every screen render call.

The screen service maintains one of these and updates it from API events.
Screens read what they need; if a field is absent or None, the screen
shows the appropriate placeholder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ScreenMode(Enum):
    BOOT = "boot"
    INITIALIZING = "initializing"
    PAIR = "pair"
    HOME = "home"
    STATUS = "status"
    PRE_SHOT = "pre_shot"
    CAPTURE = "capture"
    RESULT = "result"
    TRAJECTORY = "trajectory"
    HISTORY = "history"
    CALIBRATION = "calibration"
    LOW_BATTERY = "low_battery"
    SENSOR_OFFLINE = "sensor_offline"
    SETTINGS = "settings"


@dataclass
class ServiceHealth:
    """Status row used by the Initializing and Status screens."""

    storage_ok: bool = False
    camera_ok: bool = False
    radar_ok: bool = False
    api_ok: bool = False
    uno_ok: bool = False
    camera_fps: Optional[int] = None
    camera_resolution: str = ""
    radar_db: Optional[float] = None
    storage_free_gb: Optional[float] = None
    api_port: int = 8000


@dataclass
class ShotMetrics:
    """The numbers that show up on the Result / Trajectory screens."""

    shot_id: int
    ball_speed_mph: float
    carry_yd: int
    launch_deg: float
    spin_rpm: int
    smash_factor: float
    apex_yd: int
    hang_s: float
    side_yd: float  # positive = left, negative = right
    quality: str = "good"  # good | ok | poor


@dataclass
class PairInfo:
    ssid: str = "FlightImpact-Dev"
    ip: str = "192.168.4.1"
    # QR code payload — typically a wifi: URI or http://flightimpact.local URL.
    qr_payload: str = ""


@dataclass
class ScreenState:
    mode: ScreenMode = ScreenMode.BOOT
    boot_progress: float = 0.0
    boot_version: str = "v0.1.0"
    services: ServiceHealth = field(default_factory=ServiceHealth)
    pair: PairInfo = field(default_factory=PairInfo)
    current_shot: Optional[ShotMetrics] = None
    recent_shots: list[ShotMetrics] = field(default_factory=list)
    session_id: int = 0
    battery_pct: Optional[int] = 87
    battery_minutes_remaining: Optional[int] = None
    clock_hhmm: str = ""
    calibration_frames_captured: int = 0
    calibration_frames_target: int = 15
    brightness: float = 0.85
    # Used by animated screens to advance their state per frame.
    frame_counter: int = 0
