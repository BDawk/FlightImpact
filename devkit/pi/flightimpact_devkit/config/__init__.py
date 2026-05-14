"""Configuration loader — YAML defaults + runtime overrides."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


CONFIG_DIR = Path(__file__).parent
DEFAULT_CONFIG_PATH = CONFIG_DIR / "default.yaml"
RUNTIME_CONFIG_PATH = Path("/etc/flightimpact/config.yaml")


@dataclass
class CameraConfig:
    device: str = "/dev/video0"
    width: int = 1920
    height: int = 1080
    fps: int = 120
    pixel_format: str = "MJPG"
    buffer_seconds: float = 2.0  # ring buffer length


@dataclass
class RadarConfig:
    serial_port: str = "/dev/ttyACM0"  # Uno when used as ADC sampler
    baud_rate: int = 115200
    sample_rate_hz: int = 20000
    fft_size: int = 1024
    use_pi_adc: bool = True  # If True, sample directly via Pi GPIO/SPI ADC
    audio_device: str = "default"  # ALSA capture device name


@dataclass
class TriggerConfig:
    """How shots are triggered."""

    source: str = "radar"  # radar | manual | external
    radar_speed_threshold_mph: float = 30.0  # min club approach to trigger
    pre_trigger_ms: int = 200
    post_trigger_ms: int = 1500


@dataclass
class NetworkConfig:
    ap_mode: bool = True
    ap_ssid_prefix: str = "FlightImpact"
    ap_passphrase: str = "flightimpact"  # change in production!
    mdns_hostname: str = "flightimpact"


@dataclass
class StorageConfig:
    db_path: str = "/var/lib/flightimpact/shots.sqlite"
    clip_dir: str = "/var/lib/flightimpact/clips"
    radar_dir: str = "/var/lib/flightimpact/radar"
    keep_clips_days: int = 30


@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


@dataclass
class ScreenConfig:
    """On-device ST7789 LCD (1.69" 240x280)."""

    enabled: bool = True
    width: int = 240
    height: int = 280
    # Visible-area offsets into the 240x320 ST7789V3 driver framebuffer.
    # Don't change these unless you're using a different panel size.
    col_offset: int = 0
    row_offset: int = 20
    # SPI bus / device. /dev/spidev{bus}.{device}.
    spi_bus: int = 0
    spi_device: int = 0
    spi_hz: int = 40_000_000  # drop to 24_000_000 if you see tearing
    # GPIO pins (BCM numbering).
    dc_pin: int = 25
    rst_pin: int = 27
    bl_pin: int = 18  # hardware PWM channel
    # Render budget. The renderer will skip frames if it can't keep up.
    target_fps: int = 30
    # Initial backlight, 0.0–1.0. The brightness screen overrides at runtime.
    backlight: float = 0.85
    # If set, MockDisplay writes each frame as PNG here — useful for designing
    # screens without hardware. Overrides via env: FLIGHTIMPACT_SCREEN_SNAPSHOT_DIR.
    snapshot_dir: str = ""


@dataclass
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    radar: RadarConfig = field(default_factory=RadarConfig)
    trigger: TriggerConfig = field(default_factory=TriggerConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    api: APIConfig = field(default_factory=APIConfig)
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    dev_mode: bool = True  # enables /api/v1/test/* and verbose logging


def _merge(base: Any, override: dict) -> Any:
    """Recursively merge override dict into a dataclass instance."""
    if not override:
        return base
    for key, value in override.items():
        if hasattr(base, key):
            cur = getattr(base, key)
            if hasattr(cur, "__dataclass_fields__") and isinstance(value, dict):
                _merge(cur, value)
            else:
                setattr(base, key, value)
    return base


def load_config(path: Path | None = None) -> Config:
    """Load defaults from packaged YAML and merge runtime overrides if present."""
    cfg = Config()
    candidates = []
    if DEFAULT_CONFIG_PATH.exists():
        candidates.append(DEFAULT_CONFIG_PATH)
    if path and path.exists():
        candidates.append(path)
    elif RUNTIME_CONFIG_PATH.exists():
        candidates.append(RUNTIME_CONFIG_PATH)

    for p in candidates:
        with open(p) as f:
            data = yaml.safe_load(f) or {}
        _merge(cfg, data)
    return cfg
