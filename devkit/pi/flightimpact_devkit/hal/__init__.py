"""Hardware Abstraction Layer.

The processor and API services talk to "a camera" and "a radar" through these
interfaces. The dev kit provides USB-camera and serial-Uno implementations;
production hardware will provide MIPI-camera and integrated-radar implementations
of the same protocols.

Keeping these as Protocols (structural typing) means we don't need a base class
inheritance tree — a class just needs to implement the methods.
"""

from __future__ import annotations

from typing import AsyncIterator, Protocol

import numpy as np


class CameraSource(Protocol):
    """A source of frames. Async iterator yielding (timestamp_ns, frame_bgr)."""

    async def open(self) -> None: ...
    async def close(self) -> None: ...
    async def frames(self) -> AsyncIterator[tuple[int, np.ndarray]]: ...

    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def fps(self) -> float: ...


class RadarSource(Protocol):
    """A source of HB100 IF samples. Async iterator yielding sample blocks."""

    async def open(self) -> None: ...
    async def close(self) -> None: ...
    async def sample_blocks(self) -> AsyncIterator[np.ndarray]: ...

    @property
    def sample_rate_hz(self) -> int: ...


class TriggerSink(Protocol):
    """Optional hardware trigger output (for camera shutter / LED strobe)."""

    async def fire(self, duration_us: int = 100) -> None: ...


class DisplaySink(Protocol):
    """A frame sink for the on-device screen. Sync `show` is called from
    a single producer task; we don't queue here — the screen service is
    responsible for rate limiting and dropping stale frames."""

    async def open(self) -> None: ...
    async def close(self) -> None: ...
    async def show(self, frame: "PIL.Image.Image") -> None: ...  # noqa: F821
    async def set_backlight(self, level: float) -> None: ...

    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
