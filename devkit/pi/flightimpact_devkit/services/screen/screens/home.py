"""Home screen — idle / ready state.

Top status strip (battery, clock, paired count) over a radar-style icon
and a big "Ready" headline. Tapping (when input is wired) starts a session.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import (
    new_canvas,
    status_bar,
    text_centered,
)
from flightimpact_devkit.services.screen.state import ScreenState


def _draw_radar_icon(d: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    # Outer dashed ring + inner faint ring + scope crosshair + three pings.
    outer_r = 60
    d.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r),
              outline=t.GRID, width=1)
    inner_r = 46
    d.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
              outline=(t.MINT[0] // 3, t.MINT[1] // 3, t.MINT[2] // 3), width=1)
    # Stylized radar disc.
    disc_r = 22
    d.ellipse((cx - disc_r, cy - disc_r, cx + disc_r, cy + disc_r),
              outline=t.MINT, width=2)
    # Three pings inside.
    d.ellipse((cx - 10, cy - 10, cx - 6, cy - 6), fill=t.MINT)
    d.ellipse((cx + 4, cy - 6, cx + 7, cy - 3), fill=t.MINT)
    d.ellipse((cx - 4, cy + 5, cx - 1, cy + 8), fill=t.MINT)


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    paired_text = ""
    if state.services.api_ok:
        # Mockup shows "2 paired" — we use a placeholder until WS conns are tracked.
        paired_text = "2 paired"
    status_bar(
        d,
        battery_pct=state.battery_pct,
        clock=state.clock_hhmm or "",
        right_text=paired_text,
    )

    # Radar icon, then "Ready", then secondary hint.
    cx = t.WIDTH // 2
    icon_cy = 110
    _draw_radar_icon(d, cx, icon_cy)
    text_centered(d, "Ready", t.font_h2(), y=icon_cy + 64)
    text_centered(
        d, "tap to start a session", t.font_small(), y=icon_cy + 100, fill=t.TEXT_FAINT
    )

    return img
