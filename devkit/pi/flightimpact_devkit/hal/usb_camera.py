"""USB camera HAL implementation — V4L2 via OpenCV.

This is the dev-kit camera driver. It opens the USB camera at the configured
resolution / fps and yields (timestamp_ns, frame_bgr) tuples.

When we move to production hardware we'll write a sibling module
(e.g. mipi_camera.py) that implements the same interface.
"""

from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator

import cv2
import numpy as np

from flightimpact_devkit.config import CameraConfig


class USBCamera:
    def __init__(self, config: CameraConfig):
        self._config = config
        self._cap: cv2.VideoCapture | None = None

    async def open(self) -> None:
        loop = asyncio.get_event_loop()
        self._cap = await loop.run_in_executor(None, self._open_blocking)
        if not self._cap.isOpened():
            raise RuntimeError(f"Failed to open camera at {self._config.device}")

    def _open_blocking(self) -> cv2.VideoCapture:
        # On Linux the device path is "/dev/videoN"; cv2 wants the integer N.
        device = self._config.device
        if device.startswith("/dev/video"):
            device_idx = int(device.removeprefix("/dev/video"))
        else:
            device_idx = device  # type: ignore[assignment]

        cap = cv2.VideoCapture(device_idx, cv2.CAP_V4L2)
        # Set MJPEG fourcc BEFORE width/height/fps — required for high-rate modes
        if self._config.pixel_format == "MJPG":
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.height)
        cap.set(cv2.CAP_PROP_FPS, self._config.fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # always grab the freshest frame
        return cap

    async def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    async def frames(self) -> AsyncIterator[tuple[int, np.ndarray]]:
        if self._cap is None:
            raise RuntimeError("Camera not opened")
        loop = asyncio.get_event_loop()
        while True:
            ts_ns = time.monotonic_ns()
            ok, frame = await loop.run_in_executor(None, self._cap.read)
            if not ok:
                # Camera dropped — yield to event loop and retry
                await asyncio.sleep(0.01)
                continue
            yield ts_ns, frame

    @property
    def width(self) -> int:
        return self._config.width

    @property
    def height(self) -> int:
        return self._config.height

    @property
    def fps(self) -> float:
        return float(self._config.fps)


class MockCamera:
    """A fake camera that yields synthetic frames — used when no hardware is present.

    Generates a moving bright spot on a dark background to simulate a ball in flight.
    Useful for end-to-end testing of the pipeline without setting up the rig.
    """

    def __init__(self, config: CameraConfig):
        self._config = config
        self._frame_idx = 0

    async def open(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def frames(self) -> AsyncIterator[tuple[int, np.ndarray]]:
        while True:
            await asyncio.sleep(1.0 / self._config.fps)
            frame = np.zeros((self._config.height, self._config.width, 3), dtype=np.uint8)
            # Static "ball" + a moving "clubhead" to simulate something happening
            cv2.circle(frame, (self._config.width // 3, self._config.height // 2), 12, (240, 240, 240), -1)
            x = (self._frame_idx * 8) % self._config.width
            cv2.rectangle(frame, (x, 100), (x + 40, 140), (200, 200, 200), -1)
            self._frame_idx += 1
            yield time.monotonic_ns(), frame

    @property
    def width(self) -> int:
        return self._config.width

    @property
    def height(self) -> int:
        return self._config.height

    @property
    def fps(self) -> float:
        return float(self._config.fps)
