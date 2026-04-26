"""Ball detection — find the ball in a frame.

Strategy: background subtraction against a learned static background, blob
detection on the difference image, filter by size and circularity.

Implementation lands in Phase 2 (camera service). Interface is defined now
so the processor can be wired up.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BallDetection:
    """A single ball detection in a single frame."""

    frame_index: int
    x: float  # pixel coordinates of the ball center
    y: float
    radius: float  # pixels
    confidence: float  # 0..1


def detect_ball(frame, background) -> Optional[BallDetection]:
    """Detect the ball in a frame against a static background. STUB."""
    raise NotImplementedError("Ball detection lands in Phase 2")
