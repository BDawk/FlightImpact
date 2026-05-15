"""Pair screen - AP onboarding with SSID/IP and a stylized QR placeholder."""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import cap_text, new_canvas, status_bar, text_centered
from flightimpact_devkit.services.screen.state import ScreenState


def _draw_qr(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    draw.rounded_rectangle((x, y, x + size, y + size), radius=8, fill=(255, 255, 255))
    pad = 8
    cell = (size - 2 * pad) // 11
    gx = x + pad
    gy = y + pad

    def fill_cell(cx: int, cy: int) -> None:
        draw.rectangle(
            (
                gx + cx * cell,
                gy + cy * cell,
                gx + (cx + 1) * cell - 1,
                gy + (cy + 1) * cell - 1,
            ),
            fill=(0, 0, 0),
        )

    # Finder patterns.
    for ox, oy in ((0, 0), (8, 0), (0, 8)):
        for dx in range(3):
            for dy in range(3):
                fill_cell(ox + dx, oy + dy)

    # Deterministic filler pattern (not a real QR encode, but visually close).
    points = [
        (4, 1), (6, 2), (4, 4), (5, 4), (7, 4),
        (4, 6), (6, 5), (8, 6), (4, 8), (6, 9),
        (10, 5), (5, 7), (7, 8), (9, 9), (10, 10), (3, 10),
    ]
    for cx, cy in points:
        fill_cell(cx, cy)


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    status_bar(d, battery_pct=state.battery_pct, clock="", right_text="AP")

    cap_text(d, (t.PAD, t.PAD + 20), "Connect To Start")
    d.text((t.PAD, t.PAD + 36), "Pair your phone", fill=t.TEXT, font=t.font_h3())

    qr_size = 118
    qr_x = (t.WIDTH - qr_size) // 2
    qr_y = t.PAD + 62
    _draw_qr(d, qr_x, qr_y, qr_size)

    text_centered(d, f"SSID  {state.pair.ssid}", t.font_small(), y=208, fill=t.TEXT)
    text_centered(d, state.pair.ip, t.font_small(), y=226, fill=t.TEXT_FAINT)

    return img
