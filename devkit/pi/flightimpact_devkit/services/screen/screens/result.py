"""Result screen — primary metrics for the most recent shot.

Layout (matching the mockup):

    [SHOT 14]               [GOOD]
    BALL SPEED
    152  mph
    [carry][launch]
    [spin ][smash ]
                tap for trajectory
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import (
    cap_text,
    new_canvas,
    text_centered,
    tile,
)
from flightimpact_devkit.services.screen.state import ScreenState


_QUALITY_COLOR = {
    "good": t.MINT,
    "ok": t.AMBER,
    "poor": t.RED,
}


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    shot = state.current_shot
    if shot is None:
        # Empty state — defer to the home screen if there's no shot data yet.
        text_centered(d, "No shots yet", t.font_h3(), y=120, fill=t.TEXT_FAINT)
        return img

    # Header row.
    cap_text(d, (t.PAD, t.PAD + 4), f"Shot {shot.shot_id}")
    quality_color = _QUALITY_COLOR.get(shot.quality, t.TEXT_FAINT)
    quality_text = " ".join(shot.quality.upper())
    qw = d.textlength(quality_text, font=t.font_cap())
    d.text((t.WIDTH - t.PAD - qw, t.PAD + 4), quality_text,
           fill=quality_color, font=t.font_cap())

    # Primary metric — ball speed.
    cap_text(d, (t.PAD, t.PAD + 28), "Ball Speed")
    speed_text = f"{shot.ball_speed_mph:.0f}"
    d.text((t.PAD, t.PAD + 42), speed_text, fill=t.TEXT, font=t.font_h1())
    sw = d.textlength(speed_text, font=t.font_h1())
    d.text(
        (t.PAD + sw + 6, t.PAD + 76),
        "mph",
        fill=t.TEXT_FAINT,
        font=t.font(13),
    )

    # 2x2 tile grid below.
    grid_y = 124
    tile_h = 50
    gap = t.RESULT_TILE_GAP
    tile_w = (t.WIDTH - 2 * t.PAD - gap) // 2

    tiles = [
        (0, 0, "carry", f"{shot.carry_yd}", "yd"),
        (1, 0, "launch", f"{shot.launch_deg:.1f}", "°"),
        (0, 1, "spin", f"{shot.spin_rpm:,}", "rpm"),
        (1, 1, "smash", f"{shot.smash_factor:.2f}", ""),
    ]
    for col, row, label, value, unit in tiles:
        x0 = t.PAD + col * (tile_w + gap)
        y0 = grid_y + row * (tile_h + gap)
        tile(d, (x0, y0, x0 + tile_w, y0 + tile_h), label, value, unit=unit)

    # Footer hint.
    text_centered(
        d, "tap for trajectory", t.font_small(),
        y=t.HEIGHT - 24, fill=t.TEXT_FAINT,
    )

    return img
