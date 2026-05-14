"""Shared rendering primitives for screens.

Each `Screen` returns a 240x280 RGB PIL Image. This module collects the
drawing helpers — rounded rectangles, tile rows, status pills, status-bar
strip — so screens stay declarative.
"""

from __future__ import annotations

from typing import Iterable

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t


def new_canvas(bg: tuple[int, int, int] = t.BG) -> Image.Image:
    """A fresh 240x280 RGB canvas at the configured background color."""
    return Image.new("RGB", (t.WIDTH, t.HEIGHT), bg)


def rounded_tile(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int] = t.SURFACE,
    radius: int = t.RESULT_TILE_RADIUS,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def cap_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: tuple[int, int, int] = t.TEXT_FAINT,
) -> None:
    """Small caps tag — letter-spaced uppercase, matches the `.cap` class."""
    spaced = " ".join(text.upper())
    draw.text(xy, spaced, fill=fill, font=t.font_cap())


def tile(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    value: str,
    *,
    unit: str = "",
    fill: tuple[int, int, int] = t.SURFACE,
    value_color: tuple[int, int, int] = t.TEXT,
) -> None:
    """A labeled value tile — the building block of the result / trajectory grids."""
    rounded_tile(draw, box, fill=fill)
    x0, y0, _x1, _y1 = box
    cap_text(draw, (x0 + 10, y0 + 8), label)
    draw.text(
        (x0 + 10, y0 + 20),
        value,
        fill=value_color,
        font=t.font_tile_value(),
    )
    if unit:
        # Width of `value` so we can place the unit after it.
        v_w = draw.textlength(value, font=t.font_tile_value())
        draw.text(
            (x0 + 10 + v_w + 3, y0 + 30),
            unit,
            fill=t.TEXT_FAINT,
            font=t.font_tile_label(),
        )


def status_dot(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    color: tuple[int, int, int],
    *,
    radius: int = 4,
) -> None:
    x, y = xy
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def progress_bar(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fraction: float,
    *,
    bg: tuple[int, int, int] = t.SURFACE,
    fg: tuple[int, int, int] = t.MINT,
) -> None:
    x0, y0, x1, y1 = box
    rounded_tile(draw, box, fill=bg, radius=(y1 - y0) // 2)
    width = x1 - x0
    fill_w = int(width * max(0.0, min(1.0, fraction)))
    if fill_w > 0:
        draw.rounded_rectangle(
            (x0, y0, x0 + fill_w, y1),
            fill=fg,
            radius=(y1 - y0) // 2,
        )


def text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    *,
    y: int,
    fill: tuple[int, int, int] = t.TEXT,
    x_center: int = t.WIDTH // 2,
) -> None:
    w = draw.textlength(text, font=font)
    draw.text((x_center - w / 2, y), text, fill=fill, font=font)


def status_bar(
    draw: ImageDraw.ImageDraw,
    *,
    battery_pct: int | None = None,
    clock: str = "",
    right_text: str = "",
    y: int = 10,
) -> None:
    """Top status strip — matches `.sb` in the mockups."""
    if battery_pct is not None:
        # Battery icon at (16, y) then percentage to its right.
        bx, by = t.PAD, y
        draw.rectangle((bx, by, bx + 14, by + 8), outline=t.TEXT, width=1)
        draw.rectangle((bx + 15, by + 2, bx + 17, by + 6), fill=t.TEXT)
        # Fill based on percentage.
        fw = int(12 * (battery_pct / 100))
        draw.rectangle((bx + 1, by + 1, bx + 1 + fw, by + 7), fill=t.MINT)
        draw.text(
            (bx + 22, by - 2),
            f"{battery_pct}%",
            fill=t.TEXT_FAINT,
            font=t.font_cap(),
        )
    if clock:
        text_centered(draw, clock, t.font_cap(), y=y, fill=t.TEXT_FAINT)
    if right_text:
        w = draw.textlength(right_text, font=t.font_cap())
        draw.text(
            (t.WIDTH - t.PAD - w, y),
            right_text,
            fill=t.TEXT_FAINT,
            font=t.font_cap(),
        )


def horizontal_tile_row(
    draw: ImageDraw.ImageDraw,
    *,
    y: int,
    tiles: Iterable[tuple[str, str, str]],
    height: int = 50,
) -> None:
    """Render a row of equally-sized tiles. Each tile is (label, value, unit)."""
    items = list(tiles)
    n = len(items)
    gap = t.RESULT_TILE_GAP
    avail = t.WIDTH - 2 * t.PAD - gap * (n - 1)
    w = avail // n
    for i, (label, value, unit) in enumerate(items):
        x = t.PAD + i * (w + gap)
        tile(draw, (x, y, x + w, y + height), label, value, unit=unit)
