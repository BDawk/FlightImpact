"""Low-battery warning screen.

Surfaces when `battery_pct` drops below the warning threshold. Mirrors
mockup #12 — a large amber battery glyph, the percentage, and an estimate
of how much capture time is left.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import (
    cap_text,
    new_canvas,
    status_bar,
    text_centered,
)
from flightimpact_devkit.services.screen.state import ScreenState


def _draw_battery_glyph(d: ImageDraw.ImageDraw, *, pct: int, cx: int, cy: int) -> None:
    """Big amber battery icon with a fill bar proportional to `pct`."""
    body_w, body_h = 100, 48
    x0 = cx - body_w // 2
    y0 = cy - body_h // 2
    d.rounded_rectangle((x0, y0, x0 + body_w, y0 + body_h), radius=6,
                        outline=t.AMBER, width=2)
    # Battery cap on the right.
    cap_w, cap_h = 6, 16
    d.rounded_rectangle(
        (x0 + body_w + 2, cy - cap_h // 2,
         x0 + body_w + 2 + cap_w, cy + cap_h // 2),
        radius=2, fill=t.AMBER,
    )
    # Filled portion — clamp to a small minimum so a near-empty cell is still visible.
    pad = 4
    fill_max = body_w - 2 * pad
    fill_w = max(8, int(fill_max * max(0, min(100, pct)) / 100))
    d.rectangle((x0 + pad, y0 + pad, x0 + pad + fill_w, y0 + body_h - pad),
                fill=t.AMBER)
    # Percent text overlaid in dark on the amber bar.
    pct_text = f"{pct}%"
    tw = d.textlength(pct_text, font=t.font_h3())
    d.text((cx - tw / 2, cy - 11), pct_text, fill=t.BG, font=t.font_h3())


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    pct = state.battery_pct if state.battery_pct is not None else 0

    status_bar(
        d,
        battery_pct=pct,
        clock=state.clock_hhmm or "",
        right_text="low battery",
    )

    # Title block.
    cap_text(d, (t.PAD, t.PAD + 20), "low battery", fill=t.RED)
    d.text((t.PAD, t.PAD + 36), f"{pct}% remaining",
           fill=t.TEXT, font=t.font_h3())

    # Big battery glyph in the middle.
    _draw_battery_glyph(d, pct=pct, cx=t.WIDTH // 2, cy=148)

    # Time-remaining hint. If we don't have an estimate, fall back to copy
    # that matches the mockup without pretending to know the number.
    if state.battery_minutes_remaining is not None:
        minutes_text = f"about {state.battery_minutes_remaining} min of capture left"
    else:
        minutes_text = "limited capture time remaining"
    text_centered(d, minutes_text, t.font_small(),
                  y=t.HEIGHT - 56, fill=t.TEXT_DIM)
    text_centered(d, "connect a USB-C charger to top up", t.font_small(),
                  y=t.HEIGHT - 38, fill=t.TEXT_FAINT)

    return img
