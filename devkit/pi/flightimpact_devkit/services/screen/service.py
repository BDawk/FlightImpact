"""ScreenService — runs the render loop and pushes frames to the display.

Single asyncio task. Holds the current ScreenState; mutates it in response
to API events (set_mode, update_health, on_shot, …). Renders at `target_fps`
or skips frames if the render+SPI push budget is exceeded.
"""

from __future__ import annotations

import asyncio
import logging
import time

from flightimpact_devkit.config import ScreenConfig
from flightimpact_devkit.hal import DisplaySink
from flightimpact_devkit.services.screen import screens
from flightimpact_devkit.services.screen.state import (
    ScreenMode,
    ScreenState,
    ServiceHealth,
    ShotMetrics,
)

logger = logging.getLogger(__name__)


class ScreenService:
    def __init__(self, display: DisplaySink, config: ScreenConfig):
        self._display = display
        self._config = config
        self._state = ScreenState()
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._wake = asyncio.Event()  # set when state changes — wakes the renderer

    @property
    def state(self) -> ScreenState:
        return self._state

    async def start(self) -> None:
        await self._display.open()
        self._task = asyncio.create_task(self._run(), name="screen-service")

    async def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        if self._task is not None:
            await self._task
        await self._display.close()

    # --- State mutators (called from the API or other services) ---------

    def set_mode(self, mode: ScreenMode) -> None:
        if self._state.mode != mode:
            logger.info("Screen mode → %s", mode.value)
            self._state.mode = mode
            self._wake.set()

    def update_health(self, **kwargs) -> None:
        h = self._state.services
        for k, v in kwargs.items():
            if hasattr(h, k):
                setattr(h, k, v)
        self._wake.set()

    def set_boot_progress(self, fraction: float) -> None:
        self._state.boot_progress = max(0.0, min(1.0, fraction))
        self._wake.set()

    def on_shot(self, shot: ShotMetrics) -> None:
        self._state.current_shot = shot
        self._state.recent_shots = ([shot] + self._state.recent_shots)[:10]
        self.set_mode(ScreenMode.RESULT)

    def set_brightness(self, level: float) -> None:
        self._state.brightness = max(0.0, min(1.0, level))
        # Fire and forget — backlight change doesn't need to block the caller.
        asyncio.create_task(self._display.set_backlight(self._state.brightness))

    # --- Render loop ----------------------------------------------------

    async def _run(self) -> None:
        frame_period = 1.0 / max(1, self._config.target_fps)
        next_tick = time.monotonic()

        while not self._stop.is_set():
            # Wait until either it's time for the next frame, or state changed.
            now = time.monotonic()
            sleep_for = max(0.0, next_tick - now)
            if sleep_for > 0:
                try:
                    await asyncio.wait_for(self._wake.wait(), timeout=sleep_for)
                except asyncio.TimeoutError:
                    pass

            self._wake.clear()
            if self._stop.is_set():
                break

            self._state.frame_counter += 1
            t_start = time.monotonic()
            try:
                img = screens.render(self._state)
                await self._display.show(img)
            except Exception:
                # Don't let a render bug kill the service.
                logger.exception("Screen render failed")
            elapsed = time.monotonic() - t_start

            # Schedule the next tick. If we're behind, snap to "now" so we
            # don't burn CPU trying to catch up.
            next_tick += frame_period
            if next_tick < time.monotonic() - frame_period:
                next_tick = time.monotonic() + frame_period

            if elapsed > frame_period * 1.5:
                logger.debug(
                    "Slow frame: %.1f ms (budget %.1f ms)",
                    elapsed * 1000, frame_period * 1000,
                )
