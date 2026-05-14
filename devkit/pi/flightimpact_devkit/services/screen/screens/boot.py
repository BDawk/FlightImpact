"""Boot screen — animated mint splash.

Matches the first mockup: three concentric pulse rings expanding around a
solid mint dot, wordmark + version below. The pulse animation is driven by
`state.frame_counter`; the screen service increments it every render.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import new_canvas, text_centered
from flightimpact_devkit.services.screen.state import ScreenState


# 2.4-second pulse loop at the mockup's animation duration. We get ~24 fps
# from the service so 60 frames ≈ one pulse cycle.
_PULSE_FRAMES = 60
# Three rings, evenly phase-offset.
_PHASES = (0.0, 1 / 3, 2 / 3)


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img, "RGBA")

    cx, cy = t.WIDTH // 2, 110
    max_r = 48

    for phase in _PHASES:
        # Animation goes 0 → 1; opacity peaks at 0.5 and fades to 0 at edges.
        frac = ((state.frame_counter / _PULSE_FRAMES) + phase) % 1.0
        # Match the mockup keyframes: invisible at 0%/100%, opaque around 50%,
        # invisible (scaled large) at 80%.
        if frac >= 0.8:
            continue
        scale = 0.5 + frac  # 0.5 → 1.4
        radius = int(max_r * scale)
        if frac < 0.5:
            opacity = int(255 * (frac / 0.5) * 0.7)
        else:
            opacity = int(255 * (1 - (frac - 0.5) / 0.3) * 0.7)
        opacity = max(0, min(255, opacity))
        d.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=(*t.MINT, opacity),
            width=2,
        )

    # Center dot — solid mint.
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=t.MINT)

    # Wordmark + version, matching the mockup's vertical rhythm.
    text_centered(d, "FlightImpact", t.font(20, weight="medium"), y=cy + 78)
    text_centered(d, state.boot_version, t.font_cap(), y=cy + 110, fill=t.TEXT_FAINT)

    return img
