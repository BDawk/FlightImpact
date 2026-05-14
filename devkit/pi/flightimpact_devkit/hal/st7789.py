"""ST7789 LCD HAL — drives the dev kit's 1.69" 240x280 rounded panel.

Hardware: Waveshare 1.69" LCD Module (or any ST7789V3-based 240x280 panel
with the same pinout).

The panel is a 240x320 ST7789V3 internally; the visible window is offset
(0, 20) to skip the unused 20 rows above and below. The driver bakes this
in, so callers just send 240x280 frames.

Wiring (see docs/screen_setup.md):
    VCC → 3.3 V    GND → GND
    DIN → GPIO 10  CLK → GPIO 11   CS  → GPIO 8 (SPI0 CE0)
    DC  → GPIO 25  RST → GPIO 27   BL  → GPIO 18 (PWM)
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

from flightimpact_devkit.config import ScreenConfig

if TYPE_CHECKING:
    from PIL.Image import Image

logger = logging.getLogger(__name__)


# ST7789 command opcodes — only the ones we actually use.
_NOP = 0x00
_SWRESET = 0x01
_SLPOUT = 0x11
_NORON = 0x13
_INVON = 0x21  # Required on most 240x280 panels — colors are inverted otherwise
_DISPON = 0x29
_CASET = 0x2A
_RASET = 0x2B
_RAMWR = 0x2C
_MADCTL = 0x36
_COLMOD = 0x3A


class ST7789Display:
    """SPI driver for the ST7789V3 240x280 panel.

    Synchronous SPI/GPIO under the hood; the public API is async to match
    the rest of the HAL layer. Blocking work runs in the default executor.
    """

    def __init__(self, config: ScreenConfig):
        self._config = config
        self._spi = None  # spidev.SpiDev
        self._dc = None  # gpiozero.DigitalOutputDevice
        self._rst = None  # gpiozero.DigitalOutputDevice
        self._bl = None  # gpiozero.PWMOutputDevice
        self._open = False

    @property
    def width(self) -> int:
        return self._config.width

    @property
    def height(self) -> int:
        return self._config.height

    async def open(self) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._open_blocking)

    def _open_blocking(self) -> None:
        # Lazy-import so the module imports cleanly on non-Pi machines.
        import spidev
        from gpiozero import DigitalOutputDevice, PWMOutputDevice

        cfg = self._config

        self._spi = spidev.SpiDev()
        self._spi.open(cfg.spi_bus, cfg.spi_device)
        self._spi.max_speed_hz = cfg.spi_hz
        self._spi.mode = 0  # CPOL=0, CPHA=0 — standard for ST7789

        self._dc = DigitalOutputDevice(cfg.dc_pin, initial_value=False)
        self._rst = DigitalOutputDevice(cfg.rst_pin, initial_value=True)
        self._bl = PWMOutputDevice(cfg.bl_pin, initial_value=0.0, frequency=1000)

        self._reset()
        self._init_panel()
        self._bl.value = max(0.0, min(1.0, cfg.backlight))
        self._open = True
        logger.info(
            "ST7789 initialized: %dx%d, SPI %d MHz, backlight %.0f%%",
            cfg.width, cfg.height, cfg.spi_hz // 1_000_000, cfg.backlight * 100,
        )

    def _reset(self) -> None:
        self._rst.on()
        time.sleep(0.01)
        self._rst.off()
        time.sleep(0.01)
        self._rst.on()
        time.sleep(0.12)  # ST7789 datasheet: 120 ms after hardware reset

    def _write_cmd(self, cmd: int, *data: int) -> None:
        self._dc.off()
        self._spi.writebytes([cmd])
        if data:
            self._dc.on()
            self._spi.writebytes(list(data))

    def _init_panel(self) -> None:
        self._write_cmd(_SWRESET)
        time.sleep(0.15)
        self._write_cmd(_SLPOUT)
        time.sleep(0.12)

        # Memory data access control. 0x00 = standard orientation, RGB.
        # Flip bits here if you mount the panel rotated. The smoke test
        # `--rotate` flag rotates the bitmap before push instead — slower
        # but doesn't require re-flashing.
        self._write_cmd(_MADCTL, 0x00)

        # 16-bit RGB565 color.
        self._write_cmd(_COLMOD, 0x05)

        # ST7789V3 240x280 panels ship with inverted colors. Required.
        self._write_cmd(_INVON)
        self._write_cmd(_NORON)
        time.sleep(0.01)
        self._write_cmd(_DISPON)
        time.sleep(0.1)

    def _set_window(self, x0: int, y0: int, x1: int, y1: int) -> None:
        col_off = self._config.col_offset
        row_off = self._config.row_offset
        x0 += col_off
        x1 += col_off
        y0 += row_off
        y1 += row_off
        self._write_cmd(_CASET, x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)
        self._write_cmd(_RASET, y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)
        self._write_cmd(_RAMWR)

    async def show(self, frame: "Image") -> None:
        """Push a PIL Image to the panel. Must be exactly width x height RGB."""
        if not self._open:
            raise RuntimeError("Display not opened")
        if frame.size != (self._config.width, self._config.height):
            raise ValueError(
                f"Frame is {frame.size}, expected ({self._config.width}, {self._config.height})"
            )
        if frame.mode != "RGB":
            frame = frame.convert("RGB")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._push_blocking, frame)

    def _push_blocking(self, frame: "Image") -> None:
        # PIL → RGB565 little-endian byte buffer (the format ST7789 wants).
        import numpy as np
        pixels = np.asarray(frame, dtype=np.uint16)  # H x W x 3
        r = (pixels[..., 0] >> 3) & 0x1F
        g = (pixels[..., 1] >> 2) & 0x3F
        b = (pixels[..., 2] >> 3) & 0x1F
        rgb565 = (r << 11) | (g << 5) | b
        # Big-endian — ST7789 expects high byte first.
        buf = rgb565.astype(">u2").tobytes()

        self._set_window(0, 0, self._config.width - 1, self._config.height - 1)
        self._dc.on()
        # SPI driver max is 4096 bytes per writebytes2 call on some kernels.
        # Chunk to be safe.
        CHUNK = 4096
        for i in range(0, len(buf), CHUNK):
            self._spi.writebytes2(buf[i:i + CHUNK])

    async def set_backlight(self, level: float) -> None:
        level = max(0.0, min(1.0, level))
        if self._bl is not None:
            self._bl.value = level

    async def close(self) -> None:
        if not self._open:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._close_blocking)

    def _close_blocking(self) -> None:
        try:
            if self._bl is not None:
                self._bl.value = 0.0
                self._bl.close()
            if self._dc is not None:
                self._dc.close()
            if self._rst is not None:
                self._rst.close()
            if self._spi is not None:
                self._spi.close()
        finally:
            self._open = False


class MockDisplay:
    """No-op display for development without hardware.

    If `snapshot_dir` is set (via ScreenConfig or FLIGHTIMPACT_SCREEN_SNAPSHOT_DIR
    env var), every shown frame is written as PNG. Lets you design screens on
    a laptop and review them as image files.
    """

    def __init__(self, config: ScreenConfig):
        self._config = config
        snapshot_dir = (
            os.environ.get("FLIGHTIMPACT_SCREEN_SNAPSHOT_DIR")
            or config.snapshot_dir
            or ""
        )
        self._snapshot_dir = Path(snapshot_dir) if snapshot_dir else None
        self._frame_idx = 0
        self._backlight = config.backlight

    @property
    def width(self) -> int:
        return self._config.width

    @property
    def height(self) -> int:
        return self._config.height

    async def open(self) -> None:
        if self._snapshot_dir is not None:
            self._snapshot_dir.mkdir(parents=True, exist_ok=True)
            logger.info("MockDisplay snapshots: %s", self._snapshot_dir)

    async def close(self) -> None:
        return None

    async def show(self, frame: "Image") -> None:
        if self._snapshot_dir is not None:
            path = self._snapshot_dir / f"frame_{self._frame_idx:06d}.png"
            frame.save(path)
        self._frame_idx += 1

    async def set_backlight(self, level: float) -> None:
        self._backlight = max(0.0, min(1.0, level))


def is_panel_present(config: ScreenConfig) -> bool:
    """Best-effort check that the SPI bus is available. Returns False on
    systems without spidev or with SPI disabled in /boot/firmware/config.txt."""
    spi_path = Path(f"/dev/spidev{config.spi_bus}.{config.spi_device}")
    if not spi_path.exists():
        return False
    try:
        import spidev  # noqa: F401
        import gpiozero  # noqa: F401
    except ImportError:
        return False
    return True
