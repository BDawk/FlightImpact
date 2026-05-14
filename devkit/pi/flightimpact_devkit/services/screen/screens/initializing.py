"""Initializing screen — service health checklist with a progress bar."""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import (
    cap_text,
    new_canvas,
    progress_bar,
)
from flightimpact_devkit.services.screen.state import ScreenState


_CHECK_ROWS = [
    ("storage", "Storage opened"),
    ("camera", "Camera attached"),
    ("radar", "Radar warming up"),
    ("api", "API server"),
    ("calibration", "Calibration check"),
]


def _draw_check(d: ImageDraw.ImageDraw, xy: tuple[int, int]) -> None:
    x, y = xy
    d.line((x, y + 5, x + 4, y + 9), fill=t.MINT, width=2)
    d.line((x + 4, y + 9, x + 10, y + 1), fill=t.MINT, width=2)


def _draw_spinner(d: ImageDraw.ImageDraw, xy: tuple[int, int], frame: int) -> None:
    """Three-quarter circle that rotates — simplest representation of a spinner
    on a single render frame. Phase is `frame % 12` for a 12-step cycle."""
    x, y = xy
    r = 6
    start = (frame * 30) % 360
    d.arc((x - r, y - r, x + r, y + r), start=start, end=start + 240,
          fill=t.TEXT_FAINT, width=2)


def _draw_pending(d: ImageDraw.ImageDraw, xy: tuple[int, int]) -> None:
    x, y = xy
    r = 6
    d.ellipse((x - r, y - r, x + r, y + r), outline=t.TEXT_FAINT, width=2)


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    cap_text(d, (t.PAD, t.PAD), "Starting Up")
    d.text((t.PAD, t.PAD + 14), "Initializing", fill=t.TEXT, font=t.font_h3())

    svc = state.services
    statuses = {
        "storage": svc.storage_ok,
        "camera": svc.camera_ok,
        "radar": svc.radar_ok,
        "api": svc.api_ok,
        "calibration": False,  # placeholder until calibration check is wired up
    }

    # Service rows.
    row_y = t.PAD + 56
    row_gap = 22
    for key, label in _CHECK_ROWS:
        ok = statuses.get(key)
        marker_x = t.PAD + 5
        text_x = t.PAD + 24
        if ok:
            _draw_check(d, (marker_x, row_y))
            text_color = t.TEXT
        elif ok is None:
            _draw_pending(d, (marker_x + 5, row_y + 5))
            text_color = (t.TEXT_FAINT[0], t.TEXT_FAINT[1], t.TEXT_FAINT[2])
        else:  # in-progress
            _draw_spinner(d, (marker_x + 5, row_y + 5), state.frame_counter)
            text_color = t.TEXT
        d.text((text_x, row_y - 2), label, fill=text_color, font=t.font_body())
        row_y += row_gap

    # Progress bar pinned to the bottom — matches the mockup.
    progress_bar(
        d,
        (t.PAD, t.HEIGHT - 22, t.WIDTH - t.PAD, t.HEIGHT - 19),
        state.boot_progress,
    )

    return img
