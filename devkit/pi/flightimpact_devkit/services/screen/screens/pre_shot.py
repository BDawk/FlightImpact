"""Pre-shot screen - ball placement guide and armed state."""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import new_canvas, status_bar, text_centered
from flightimpact_devkit.services.screen.state import ScreenState


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    status_bar(
        d,
        battery_pct=state.battery_pct,
        clock=state.clock_hhmm,
        right_text=f"S{state.session_id:02d}" if state.session_id > 0 else "",
    )

    cx, cy = t.WIDTH // 2, 128
    outer_r = 70
    inner_r = 46

    d.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r), outline=t.GRID, width=1)
    d.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r), outline=t.GRID, width=1)
    d.line((cx, cy - outer_r, cx, cy + outer_r), fill=t.GRID, width=1)
    d.line((cx - outer_r, cy, cx + outer_r, cy), fill=t.GRID, width=1)

    blink_on = (state.frame_counter // 12) % 2 == 0
    ring_color = t.MINT if blink_on else t.TEXT_DIM
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=t.TEXT, outline=ring_color, width=2)

    text_centered(d, "Place ball", t.font_h3(), y=208, fill=t.TEXT)
    text_centered(d, "auto-detect armed", t.font_small(), y=232, fill=t.TEXT_FAINT)

    return img
