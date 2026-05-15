"""Capture screen - shown while a shot is actively being recorded/processed."""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import new_canvas, text_centered
from flightimpact_devkit.services.screen.state import ScreenState


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img, "RGBA")

    # Subtle radial glow behind the capture animation.
    cx, cy = t.WIDTH // 2, 124
    for r in range(70, 8, -8):
        alpha = max(0, 150 - r)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(10, 42, 31, alpha))

    # Two pulse rings driven by frame counter.
    phase = state.frame_counter % 24
    for offset in (0, 8):
        p = ((phase + offset) % 24) / 24.0
        radius = int(20 + p * 52)
        alpha = int((1.0 - p) * 180)
        d.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=(t.MINT[0], t.MINT[1], t.MINT[2], alpha),
            width=2,
        )

    # Center target reticle.
    d.ellipse((cx - 15, cy - 15, cx + 15, cy + 15), outline=t.MINT, width=3)
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=t.TEXT)

    text_centered(d, "Capturing", t.font_h2(), y=198, fill=t.MINT)
    text_centered(d, "RADAR · CAM", t.font_cap(), y=230, fill=t.TEXT_FAINT)

    return img
