"""Ballistics — derive carry, total distance, apex from launch conditions.

Input: ball_speed, launch_angle, spin_rate, spin_axis.
Output: carry, total_distance, apex, flight_time.

Uses a simple ballistic flight model with drag and Magnus lift coefficients
appropriate for a golf ball. This is the same physics any indoor sim uses.

Implementation lands in Phase 4.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FlightResult:
    carry_yards: float
    total_distance_yards: float
    apex_yards: float
    flight_time_s: float


def simulate_flight(
    ball_speed_mph: float,
    launch_angle_deg: float,
    spin_rate_rpm: float,
    spin_axis_deg: float = 0.0,
) -> FlightResult:
    """Simple ballistic flight simulation. STUB."""
    raise NotImplementedError("Ballistics lands in Phase 4")
