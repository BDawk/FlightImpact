"""Status screen - subsystem health details."""

from __future__ import annotations

from PIL import Image, ImageDraw

from flightimpact_devkit.services.screen import tokens as t
from flightimpact_devkit.services.screen.renderer import cap_text, new_canvas, status_bar
from flightimpact_devkit.services.screen.state import ScreenState


def _row(
    d: ImageDraw.ImageDraw,
    *,
    y: int,
    label: str,
    value: str,
    color: tuple[int, int, int],
) -> None:
    d.ellipse((t.PAD, y + 3, t.PAD + 8, y + 11), fill=color)
    d.text((t.PAD + 14, y), label, fill=t.TEXT, font=t.font_body())
    vw = d.textlength(value, font=t.font_small())
    d.text((t.WIDTH - t.PAD - vw, y + 1), value, fill=t.TEXT_FAINT, font=t.font_small())


def render(state: ScreenState) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)

    status_bar(d, battery_pct=state.battery_pct, clock=state.clock_hhmm, right_text="OK")

    cap_text(d, (t.PAD, t.PAD + 20), "Connection")
    d.text((t.PAD, t.PAD + 36), "System health", fill=t.TEXT, font=t.font_h3())

    svc = state.services
    rows = [
        ("Camera", f"{svc.camera_resolution or '—'} · {svc.camera_fps or 0}fps" if svc.camera_ok else "Not detected", t.MINT if svc.camera_ok else t.RED),
        ("Radar", f"{svc.radar_db:.0f} dB" if svc.radar_ok and svc.radar_db is not None else ("Connected" if svc.radar_ok else "Not detected"), t.MINT if svc.radar_ok else t.RED),
        ("API", f":{svc.api_port}", t.MINT if svc.api_ok else t.RED),
        ("Uno", "Connected" if svc.uno_ok else "Absent", t.MINT if svc.uno_ok else t.AMBER),
        ("Storage", f"{svc.storage_free_gb:.1f} GB free" if svc.storage_ok and svc.storage_free_gb is not None else ("Ready" if svc.storage_ok else "Not ready"), t.MINT if svc.storage_ok else t.RED),
    ]

    y = t.PAD + 70
    for label, value, color in rows:
        _row(d, y=y, label=label, value=value, color=color)
        y += 26

    d.text((t.PAD, t.HEIGHT - 20), "flightimpact.local", fill=t.TEXT_FAINT, font=t.font_small())

    return img
