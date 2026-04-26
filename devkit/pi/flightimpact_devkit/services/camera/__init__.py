"""Camera service — captures frames, maintains a ring buffer, emits previews.

Architecture:
  - capture loop: pulls frames from the HAL as fast as the camera produces them,
    writes them into a ring buffer (so we have ~2s of history when a trigger fires)
  - preview loop: periodically (10 fps) downsamples the latest frame and pushes
    it to subscribers as JPEG bytes
  - on trigger: snapshots the entire ring buffer and hands it to the processor

The actual ball-detection / tracking work happens in the processor service —
this one just deals with frames.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Callable, Optional

import cv2
import numpy as np

from flightimpact_devkit.config import CameraConfig
from flightimpact_devkit.hal import CameraSource

logger = logging.getLogger(__name__)


class CameraService:
    PREVIEW_FPS = 10
    PREVIEW_WIDTH = 640

    def __init__(self, source: CameraSource, config: CameraConfig):
        self._source = source
        self._config = config
        self._buffer_size = int(config.buffer_seconds * config.fps)
        self._ring: deque[tuple[int, np.ndarray]] = deque(maxlen=self._buffer_size)
        self._latest_frame: Optional[np.ndarray] = None
        self._frame_count = 0
        self._fps_estimate = 0.0
        self._last_fps_check = 0
        self._preview_subscribers: list[Callable[[bytes, int, int], None]] = []
        self._running = False

    @property
    def fps(self) -> float:
        return self._fps_estimate

    @property
    def connected(self) -> bool:
        return self._running

    def subscribe_preview(self, fn: Callable[[bytes, int, int], None]) -> Callable[[], None]:
        self._preview_subscribers.append(fn)
        return lambda: self._preview_subscribers.remove(fn)

    async def start(self) -> None:
        await self._source.open()
        self._running = True
        asyncio.create_task(self._capture_loop())
        asyncio.create_task(self._preview_loop())
        logger.info("Camera service started: %dx%d @ %dfps",
                    self._config.width, self._config.height, self._config.fps)

    async def stop(self) -> None:
        self._running = False
        await self._source.close()

    async def _capture_loop(self) -> None:
        try:
            async for ts_ns, frame in self._source.frames():
                if not self._running:
                    break
                self._ring.append((ts_ns, frame))
                self._latest_frame = frame
                self._frame_count += 1
                # FPS estimate over a 1-second sliding window
                now_ns = ts_ns
                if now_ns - self._last_fps_check > 1_000_000_000:
                    self._fps_estimate = self._frame_count
                    self._frame_count = 0
                    self._last_fps_check = now_ns
        except Exception as e:
            logger.exception("Capture loop crashed: %s", e)
            self._running = False

    async def _preview_loop(self) -> None:
        period = 1.0 / self.PREVIEW_FPS
        while self._running:
            await asyncio.sleep(period)
            if self._latest_frame is None:
                continue
            try:
                frame = self._latest_frame
                # Downsample to PREVIEW_WIDTH while preserving aspect ratio
                h, w = frame.shape[:2]
                scale = self.PREVIEW_WIDTH / w
                new_size = (self.PREVIEW_WIDTH, int(h * scale))
                small = cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)
                ok, encoded = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if not ok:
                    continue
                payload = encoded.tobytes()
                for fn in list(self._preview_subscribers):
                    try:
                        fn(payload, new_size[0], new_size[1])
                    except Exception:
                        logger.exception("Preview subscriber raised; dropping")
            except Exception:
                logger.exception("Preview loop iteration failed")

    def snapshot_buffer(self) -> list[tuple[int, np.ndarray]]:
        """Return a copy of the current ring buffer for processing."""
        return list(self._ring)
