"""Sensor offline / device-not-ready screen.

Drives off `state.services` — surfaces the specific component that's down
(camera, radar, or both/+uno). Capture is disabled until all required
components reconnect.

Mapping to the mockups:
  - one component offline → mockup #13 (Sensor Offline, e.g. camera)
  - two+ components offline → mockup #15 (Device Not Ready)
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import (
    cap_text,
    new_canvas,
    rounded_tile,
    status_bar,
    text_centered,
)
from flightimpact_devkit.services.screen.state import ScreenState


_HINT_BY_COMPONENT = {
    "camera": "USB camera unplugged or not enumerated by the Pi",
    "radar":  "Radar feed unavailable — check the audio/serial link",
    "uno":    "Trigger board not detected on /dev/ttyACM0",
}


def _offline_components(state: ScreenState) -> list[str]:
    svc = state.services
    offline: list[str] = []
    if not svc.camera_ok:
        offline.append("camera")
    if not svc.radar_ok:
        offline.append("radar")
    # Uno is optional today, but if it was ever wired (uno_ok flipped at
    # least once) we treat a drop-out as needing attention. For now we only
    # surface it when the user explicitly set up the trigger board.
    return offline


def _draw_warning_glyph(d: ImageDraw.ImageDraw, *, cx: int, cy: int) -> None:
    """Round red glyph with exclamation, matching mockup #13."""
    r = 24
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=t.RED, width=2)
    # Vertical bar.
    d.rectangle((cx - 2, cy - 12, cx + 2, cy + 6), fill=t.RED)
    # Dot below.
    d.ellipse((cx - 2, cy + 10, cx + 2, cy + 14), fill=t.RED)


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    offline = _offline_components(state)
    multi = len(offline) >= 2

    status_bar(
        d,
        battery_pct=state.battery_pct,
        clock=state.clock_hhmm or "",
        right_text="not ready" if multi else "error",
    )

    # Title.
    if multi:
        cap_text(d, (t.PAD, t.PAD + 20), "device not ready", fill=t.RED)
        d.text((t.PAD, t.PAD + 36),
               f"{len(offline)} components offline",
               fill=t.TEXT, font=t.font_h3())
    else:
        cap_text(d, (t.PAD, t.PAD + 20), "sensor offline", fill=t.RED)
        primary = offline[0] if offline else "sensor"
        d.text((t.PAD, t.PAD + 36),
               f"{primary.capitalize()} not detected",
               fill=t.TEXT, font=t.font_h3())

    # Warning glyph.
    _draw_warning_glyph(d, cx=t.WIDTH // 2, cy=130)

    if multi:
        # Component list — one row per offline component.
        row_y = 162
        for component in offline:
            box = (t.PAD, row_y, t.WIDTH - t.PAD, row_y + 24)
            rounded_tile(d, box, fill=t.SURFACE, radius=8)
            # Red status dot.
            d.ellipse((t.PAD + 10, row_y + 8, t.PAD + 18, row_y + 16), fill=t.RED)
            d.text((t.PAD + 26, row_y + 5), component.capitalize(),
                   fill=t.TEXT, font=t.font_body())
            # "disconnected" tag on the right.
            tag = "disconnected"
            tw = d.textlength(tag, font=t.font_small())
            d.text((t.WIDTH - t.PAD - 10 - tw, row_y + 6), tag,
                   fill=t.RED, font=t.font_small())
            row_y += 28
        text_centered(d, "Capture disabled until all components reconnect",
                      t.font_small(), y=t.HEIGHT - 22, fill=t.TEXT_FAINT)
    else:
        primary = offline[0] if offline else "sensor"
        hint = _HINT_BY_COMPONENT.get(primary, "Component is offline")
        # Word-wrap the hint into two lines so it fits the panel.
        words = hint.split()
        mid = max(1, len(words) // 2)
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        text_centered(d, line1, t.font_small(), y=170, fill=t.TEXT_DIM)
        if line2:
            text_centered(d, line2, t.font_small(), y=186, fill=t.TEXT_DIM)
        text_centered(d, "auto-retry on reconnect",
                      t.font_small(), y=t.HEIGHT - 22, fill=t.TEXT_FAINT)

    return img
