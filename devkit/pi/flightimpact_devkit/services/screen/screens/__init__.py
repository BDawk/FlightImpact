"""Per-mode screen renderers.

Each module exports a single `render(state) -> Image` function. The screen
service picks one based on `state.mode`.

To add a new screen:
  1. Add a `ScreenMode` value in `state.py`.
  2. Create a new `screens/<name>.py` with a `render` function.
  3. Register it in `screens/__init__.py:RENDERERS`.
  4. Drive the mode transition from the service or an API event.
"""

from __future__ import annotations

from typing import Callable

from PIL import Image

from flightimpact_devkit.services.screen.state import ScreenMode, ScreenState
from flightimpact_devkit.services.screen.screens import (
    boot,
    capture,
    home,
    initializing,
    low_battery,
    pair,
    pre_shot,
    result,
    sensor_offline,
    status,
)


Renderer = Callable[[ScreenState], Image.Image]


RENDERERS: dict[ScreenMode, Renderer] = {
    ScreenMode.BOOT: boot.render,
    ScreenMode.INITIALIZING: initializing.render,
    ScreenMode.PAIR: pair.render,
    ScreenMode.HOME: home.render,
    ScreenMode.STATUS: status.render,
    ScreenMode.PRE_SHOT: pre_shot.render,
    ScreenMode.CAPTURE: capture.render,
    ScreenMode.RESULT: result.render,
    ScreenMode.LOW_BATTERY: low_battery.render,
    ScreenMode.SENSOR_OFFLINE: sensor_offline.render,
}


def render(state: ScreenState) -> Image.Image:
    renderer = RENDERERS.get(state.mode)
    if renderer is None:
        # Unimplemented mode — fall back to home for now.
        renderer = home.render
    return renderer(state)
