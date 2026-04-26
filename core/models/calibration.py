"""Calibration data — camera intrinsics and radar tuning parameters."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CameraCalibration(BaseModel):
    """Camera intrinsic + extrinsic calibration.

    Intrinsics from a checkerboard routine (OpenCV calibrateCamera).
    Extrinsics describe where the camera sits relative to the ball
    (the world coordinate origin is the static ball position).
    """

    calibrated_at: datetime = Field(default_factory=datetime.utcnow)

    # Intrinsics
    fx: float
    fy: float
    cx: float
    cy: float
    distortion: list[float] = Field(default_factory=list)  # [k1, k2, p1, p2, k3]

    # Resolution this calibration applies to
    width: int
    height: int

    # Extrinsics — camera pose relative to ball (mm, degrees)
    distance_from_ball_mm: Optional[float] = None
    height_above_ball_mm: Optional[float] = None
    side_offset_mm: Optional[float] = None
    yaw_deg: Optional[float] = None
    pitch_deg: Optional[float] = None

    # mm per pixel at the ball plane — convenient derived value
    mm_per_pixel: Optional[float] = None


class RadarCalibration(BaseModel):
    """HB100 tuning + range gate parameters."""

    calibrated_at: datetime = Field(default_factory=datetime.utcnow)

    sample_rate_hz: int = 20000
    fft_size: int = 1024
    window: str = "hann"  # hann / hamming / blackman

    # Range gate — only accept Doppler peaks within this frequency band
    min_freq_hz: float = 200.0   # ~6 mph
    max_freq_hz: float = 6000.0  # ~180 mph

    # SNR threshold for peak acceptance
    min_snr_db: float = 10.0

    # The Doppler equation coefficient for a 10.525 GHz radar at 0° angle:
    # speed_mps = freq_hz * (c / (2 * f_radar)) ≈ freq_hz * 0.01425
    # mph = mps * 2.23694
    # This is overridable per-installation if cosine angle correction is needed.
    speed_per_hz_mph: float = 0.03187
