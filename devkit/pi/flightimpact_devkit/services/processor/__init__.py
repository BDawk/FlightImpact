"""Processor service — orchestrates shot capture from trigger to stored metrics.

When a trigger fires:
  1. Snapshot the camera ring buffer (we already have pre-trigger frames)
  2. Wait for post-trigger window so we have ball flight frames too
  3. Snapshot the radar samples
  4. Hand both off to the analysis pipeline (core.algorithms)
  5. Persist the shot + push ShotUpdated telemetry to subscribers

For Phase 1 this just persists a Shot stub with the trigger speed from radar
and a placeholder metrics object. Phase 2 wires in real ball detection.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Callable
from uuid import uuid4

from core.models import Shot, ShotMetrics, ShotStatus
from flightimpact_devkit.config import TriggerConfig
from flightimpact_devkit.services.camera import CameraService
from flightimpact_devkit.services.radar import RadarService
from flightimpact_devkit.storage import Storage

logger = logging.getLogger(__name__)


class ProcessorService:
    def __init__(
        self,
        camera: CameraService,
        radar: RadarService,
        storage: Storage,
        trigger_config: TriggerConfig,
    ):
        self._camera = camera
        self._radar = radar
        self._storage = storage
        self._trigger_config = trigger_config
        self._subscribers: list[Callable[[Shot], None]] = []

    def subscribe_shot_updates(self, fn: Callable[[Shot], None]) -> Callable[[], None]:
        self._subscribers.append(fn)
        return lambda: self._subscribers.remove(fn)

    async def start(self) -> None:
        # Wire the radar trigger to our handler
        self._radar.set_trigger_callback(self._on_trigger)
        logger.info("Processor service started")

    def _on_trigger(self, speed_mph: float) -> None:
        # Called from the radar sample loop — schedule async handler
        asyncio.create_task(self._handle_shot(speed_mph))

    async def _handle_shot(self, trigger_speed_mph: float) -> None:
        shot = Shot(
            id=uuid4(),
            status=ShotStatus.CAPTURING,
            metrics=ShotMetrics(),
        )
        logger.info("Shot %s triggered at %.1f mph", shot.id, trigger_speed_mph)
        await self._publish(shot)

        # Wait for the post-trigger window to elapse so we capture ball flight
        await asyncio.sleep(self._trigger_config.post_trigger_ms / 1000.0)

        # Snapshot sensor data
        frames = self._camera.snapshot_buffer()
        radar_samples = self._radar.snapshot_samples()

        shot.status = ShotStatus.PROCESSING
        await self._publish(shot)

        # Phase 1: just record the trigger speed as ball speed (it's actually
        # club speed but we don't have full ball-tracking yet — this gets
        # replaced in Phase 2 with proper camera-derived measurement)
        shot.metrics.ball_speed_mph = trigger_speed_mph
        shot.metrics.confidence = {"ball_speed": 0.3}  # low — radar-only estimate
        shot.status = ShotStatus.COMPLETE

        # Persist
        await self._storage.save_shot(shot)
        # TODO Phase 2: write the clip + radar samples to disk and update paths

        logger.info("Shot %s complete: %d frames, %d samples",
                    shot.id, len(frames), len(radar_samples))
        await self._publish(shot)

    async def trigger_test_shot(self) -> Shot:
        """Manually trigger a shot — used by /api/v1/test/trigger."""
        speed = 100.0  # placeholder for manual triggers
        shot_id = uuid4()
        shot = Shot(id=shot_id, status=ShotStatus.CAPTURING)
        await self._publish(shot)
        # Run through the same handler
        asyncio.create_task(self._handle_shot(speed))
        return shot

    async def _publish(self, shot: Shot) -> None:
        for fn in list(self._subscribers):
            try:
                fn(shot)
            except Exception:
                logger.exception("Shot subscriber raised; dropping")
