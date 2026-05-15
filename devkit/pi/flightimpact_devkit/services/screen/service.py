"""ScreenService — runs the render loop and pushes frames to the display.

Single asyncio task. Holds the current ScreenState; mutates it in response
to API events (set_mode, update_health, on_shot, …). Renders at `target_fps`
or skips frames if the render+SPI push budget is exceeded.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Callable

from core.models import Shot, ShotStatus

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
        self._subscribers: list[Callable[[ScreenState], None]] = []
        self._shot_ids: dict[str, int] = {}

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

    def subscribe_state(self, fn: Callable[[ScreenState], None]) -> Callable[[], None]:
        self._subscribers.append(fn)

        def _unsub() -> None:
            if fn in self._subscribers:
                self._subscribers.remove(fn)

        return _unsub

    def snapshot(self) -> dict:
        shot = self._state.current_shot
        return {
            "mode": self._state.mode.value,
            "boot_progress": self._state.boot_progress,
            "boot_version": self._state.boot_version,
            "session_id": self._state.session_id,
            "battery_pct": self._state.battery_pct,
            "clock_hhmm": self._state.clock_hhmm,
            "services": {
                "storage_ok": self._state.services.storage_ok,
                "camera_ok": self._state.services.camera_ok,
                "radar_ok": self._state.services.radar_ok,
                "api_ok": self._state.services.api_ok,
                "uno_ok": self._state.services.uno_ok,
                "camera_fps": self._state.services.camera_fps,
                "camera_resolution": self._state.services.camera_resolution,
                "radar_db": self._state.services.radar_db,
                "storage_free_gb": self._state.services.storage_free_gb,
                "api_port": self._state.services.api_port,
            },
            "current_shot": None if shot is None else {
                "shot_id": shot.shot_id,
                "ball_speed_mph": shot.ball_speed_mph,
                "carry_yd": shot.carry_yd,
                "launch_deg": shot.launch_deg,
                "spin_rpm": shot.spin_rpm,
                "smash_factor": shot.smash_factor,
                "apex_yd": shot.apex_yd,
                "hang_s": shot.hang_s,
                "side_yd": shot.side_yd,
                "quality": shot.quality,
            },
        }

    # --- State mutators (called from the API or other services) ---------

    def _publish_state(self) -> None:
        for fn in list(self._subscribers):
            try:
                fn(self._state)
            except Exception:
                logger.exception("Screen state subscriber raised; dropping")

    def _changed(self) -> None:
        self._wake.set()
        self._publish_state()

    def set_mode(self, mode: ScreenMode) -> None:
        if self._state.mode != mode:
            logger.info("Screen mode → %s", mode.value)
            self._state.mode = mode
            self._changed()

    def update_health(self, **kwargs) -> None:
        h = self._state.services
        changed = False
        for k, v in kwargs.items():
            if hasattr(h, k):
                if getattr(h, k) != v:
                    setattr(h, k, v)
                    changed = True
        if changed:
            self._changed()

    def update_state(self, **kwargs) -> None:
        changed = False
        for k, v in kwargs.items():
            if not hasattr(self._state, k):
                continue
            if k in {"mode", "services", "current_shot", "recent_shots", "frame_counter"}:
                continue
            if getattr(self._state, k) != v:
                setattr(self._state, k, v)
                changed = True
        if changed:
            self._changed()

    def set_boot_progress(self, fraction: float) -> None:
        bounded = max(0.0, min(1.0, fraction))
        if self._state.boot_progress != bounded:
            self._state.boot_progress = bounded
            self._changed()

    def on_shot(self, shot: ShotMetrics) -> None:
        self._state.current_shot = shot
        self._state.recent_shots = ([shot] + self._state.recent_shots)[:10]
        self._changed()
        self.set_mode(ScreenMode.RESULT)

    def on_processor_shot(self, shot: Shot) -> None:
        shot_key = str(shot.id)
        shot_id = self._shot_ids.setdefault(shot_key, len(self._shot_ids) + 1)

        if shot.status in {ShotStatus.CAPTURING, ShotStatus.PROCESSING}:
            self.set_mode(ScreenMode.CAPTURE)
            return
        if shot.status == ShotStatus.COMPLETE:
            self.on_shot(self._to_screen_shot(shot, shot_id=shot_id))
            return
        if shot.status == ShotStatus.FAILED:
            self.set_mode(ScreenMode.HOME)

    @staticmethod
    def _to_screen_shot(shot: Shot, *, shot_id: int) -> ShotMetrics:
        metrics = shot.metrics
        confidence = metrics.confidence.get("ball_speed", 0.0)
        if confidence >= 0.7:
            quality = "good"
        elif confidence >= 0.4:
            quality = "ok"
        else:
            quality = "poor"
        return ShotMetrics(
            shot_id=shot_id,
            ball_speed_mph=metrics.ball_speed_mph or 0.0,
            carry_yd=int(round(metrics.carry_yards or 0.0)),
            launch_deg=metrics.launch_angle_deg or 0.0,
            spin_rpm=int(round(metrics.spin_rate_rpm or 0.0)),
            smash_factor=metrics.smash_factor or 0.0,
            apex_yd=int(round(metrics.apex_yards or 0.0)),
            hang_s=metrics.flight_time_s or 0.0,
            side_yd=-(metrics.launch_direction_deg or 0.0),
            quality=quality,
        )

    def set_brightness(self, level: float) -> None:
        self._state.brightness = max(0.0, min(1.0, level))
        # Fire and forget — backlight change doesn't need to block the caller.
        asyncio.create_task(self._display.set_backlight(self._state.brightness))
        self._changed()

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

            current_clock = time.strftime("%H:%M")
            if self._state.clock_hhmm != current_clock:
                self._state.clock_hhmm = current_clock
                self._publish_state()

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
