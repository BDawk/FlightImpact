"""ST7789 smoke test — verify wiring before any UI runs.

Cycles through solid colors, alignment markers, and a gradient. Watch the
panel and check:
  - colors are correct (red is red, blue is blue — not swapped)
  - the image fills the panel with no offset
  - the gradient is smooth (no banding = good SPI signal integrity)

Run on the Pi:

    sudo python -m flightimpact_devkit.scripts.test_screen
    sudo python -m flightimpact_devkit.scripts.test_screen --rotate 180
    sudo python -m flightimpact_devkit.scripts.test_screen --spi-hz 24000000
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from dataclasses import replace

from PIL import Image, ImageDraw, ImageFont

from flightimpact_devkit.config import ScreenConfig
from flightimpact_devkit.hal.st7789 import ST7789Display, is_panel_present


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def _rotate(img: Image.Image, deg: int) -> Image.Image:
    if deg == 0:
        return img
    return img.rotate(deg, resample=Image.BICUBIC, expand=False)


async def _show_solid(disp: ST7789Display, rgb: tuple[int, int, int], rotate: int) -> None:
    img = Image.new("RGB", (disp.width, disp.height), rgb)
    await disp.show(_rotate(img, rotate))


async def _show_corners(disp: ST7789Display, rotate: int) -> None:
    img = Image.new("RGB", (disp.width, disp.height), (0, 0, 0))
    d = ImageDraw.Draw(img)
    s = 70
    w, h = disp.width, disp.height
    d.rectangle((0, 0, s, s), fill=(255, 0, 0))         # red — top-left
    d.rectangle((w - s, 0, w, s), fill=(0, 255, 0))     # green — top-right
    d.rectangle((0, h - s, s, h), fill=(0, 0, 255))     # blue — bottom-left
    d.rectangle((w - s, h - s, w, h), fill=(255, 255, 255))  # white — bottom-right
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    d.text((w // 2 - 36, h // 2 - 10), "ALIGN", fill=(200, 200, 200), font=font)
    await disp.show(_rotate(img, rotate))


async def _show_gradient(disp: ST7789Display, rotate: int) -> None:
    img = Image.new("RGB", (disp.width, disp.height))
    px = img.load()
    for y in range(disp.height):
        for x in range(disp.width):
            r = int(255 * x / max(1, disp.width - 1))
            g = int(255 * y / max(1, disp.height - 1))
            b = 255 - r
            px[x, y] = (r, g, b)
    await disp.show(_rotate(img, rotate))


async def main() -> int:
    parser = argparse.ArgumentParser(description="ST7789 smoke test")
    parser.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270])
    parser.add_argument("--spi-hz", type=int, default=None)
    parser.add_argument("--backlight", type=float, default=0.9)
    parser.add_argument("--hold", type=float, default=1.2, help="Seconds per slide")
    args = parser.parse_args()

    cfg = ScreenConfig(backlight=args.backlight)
    if args.spi_hz:
        cfg = replace(cfg, spi_hz=args.spi_hz)

    if not is_panel_present(cfg):
        logger.error(
            "No SPI device at /dev/spidev%d.%d — enable SPI with `sudo raspi-config "
            "nonint do_spi 0` and reboot.",
            cfg.spi_bus, cfg.spi_device,
        )
        return 1

    disp = ST7789Display(cfg)
    await disp.open()
    try:
        slides = [
            ("red",      lambda: _show_solid(disp, (255, 0, 0), args.rotate)),
            ("green",    lambda: _show_solid(disp, (0, 255, 0), args.rotate)),
            ("blue",     lambda: _show_solid(disp, (0, 0, 255), args.rotate)),
            ("white",    lambda: _show_solid(disp, (255, 255, 255), args.rotate)),
            ("black",    lambda: _show_solid(disp, (0, 0, 0), args.rotate)),
            ("corners",  lambda: _show_corners(disp, args.rotate)),
            ("gradient", lambda: _show_gradient(disp, args.rotate)),
        ]
        for name, fn in slides:
            logger.info("→ %s", name)
            await fn()
            await asyncio.sleep(args.hold)
        logger.info("Smoke test passed. If anything looked wrong, see docs/screen_setup.md.")
    finally:
        await disp.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
