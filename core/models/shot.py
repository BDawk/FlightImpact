"""Shot — a single golf swing capture with all derived metrics."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ShotStatus(str, Enum):
    """Lifecycle of a shot from trigger to fully processed."""

    TRIGGERED = "triggered"
    CAPTURING = "capturing"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class ShotMetrics(BaseModel):
    """All measurable / derivable metrics for a single shot.

    Every field is Optional because not every sensor configuration produces
    every metric. A shot with radar only will have ball_speed but not spin.
    A shot with camera only will have launch_angle but possibly noisy speed.
    """

    # Speed
    ball_speed_mph: Optional[float] = Field(None, ge=0, le=250)
    club_speed_mph: Optional[float] = Field(None, ge=0, le=200)
    smash_factor: Optional[float] = Field(None, ge=0, le=2.0)

    # Launch
    launch_angle_deg: Optional[float] = Field(None, ge=-30, le=90)
    launch_direction_deg: Optional[float] = Field(None, ge=-45, le=45)

    # Spin
    spin_rate_rpm: Optional[float] = Field(None, ge=0, le=15000)
    spin_axis_deg: Optional[float] = Field(None, ge=-90, le=90)

    # Derived flight
    carry_yards: Optional[float] = Field(None, ge=0, le=400)
    total_distance_yards: Optional[float] = Field(None, ge=0, le=450)
    apex_yards: Optional[float] = Field(None, ge=0, le=100)
    flight_time_s: Optional[float] = Field(None, ge=0, le=15)

    # Per-metric confidence (0..1) — the fusion engine fills these in
    confidence: dict[str, float] = Field(default_factory=dict)


class Shot(BaseModel):
    """A complete shot record stored in the database."""

    id: UUID = Field(default_factory=uuid4)
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[UUID] = None

    status: ShotStatus = ShotStatus.TRIGGERED
    metrics: ShotMetrics = Field(default_factory=ShotMetrics)

    # Paths to raw artifacts on disk (dev kit feature — production may stream)
    clip_path: Optional[str] = None
    radar_path: Optional[str] = None

    # Optional reference monitor entry — dev kit only, for accuracy tracking
    reference_metrics: Optional[ShotMetrics] = None
    reference_source: Optional[str] = None  # e.g. "GCQuad", "Mevo+"

    # Free-form notes from the user
    notes: Optional[str] = None
    club: Optional[str] = None  # e.g. "Driver", "7-iron"
