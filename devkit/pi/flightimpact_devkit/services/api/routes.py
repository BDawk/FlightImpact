"""REST routes for the dev kit API."""

from __future__ import annotations

import logging
import time
from typing import Any
from typing import Optional
from uuid import UUID

import psutil
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from core.api_contract import API_VERSION
from core.models import DeviceStatus, Shot
from flightimpact_devkit.services.screen.state import ScreenMode, ShotMetrics

logger = logging.getLogger(__name__)

_START_TIME = time.monotonic()


def _get_temperature_c() -> Optional[float]:
    """Pi-specific CPU temperature read. Returns None on non-Pi systems."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read().strip()) / 1000.0
    except (FileNotFoundError, PermissionError):
        return None


def register_routes(app: FastAPI) -> None:
    router = APIRouter(prefix="/api/v1")

    def _parse_mode(mode: str) -> ScreenMode:
        try:
            return ScreenMode(mode)
        except ValueError as e:
            valid = ", ".join(m.value for m in ScreenMode)
            raise HTTPException(400, f"Invalid mode '{mode}'. Valid: {valid}") from e

    @router.get("/version")
    def get_version() -> dict:
        return {"api_version": API_VERSION, "service": "flightimpact-devkit"}

    @router.get("/status", response_model=DeviceStatus)
    def get_status() -> DeviceStatus:
        camera = app.state.camera_service
        radar = app.state.radar_service
        config = app.state.config

        return DeviceStatus(
            camera_connected=camera.connected,
            camera_fps=camera.fps,
            radar_connected=radar.connected,
            uno_connected=False,  # wired up in Phase 1.5 (trigger/strobe)
            cpu_percent=psutil.cpu_percent(interval=None),
            memory_percent=psutil.virtual_memory().percent,
            temperature_c=_get_temperature_c(),
            uptime_s=time.monotonic() - _START_TIME,
            ap_mode=config.network.ap_mode,
            wifi_ssid=None,  # filled in by network module Phase 1.5
            ip_address=None,
        )

    @router.get("/shots", response_model=list[Shot])
    async def list_shots(limit: int = 50, offset: int = 0) -> list[Shot]:
        return await app.state.storage.list_shots(limit=limit, offset=offset)

    @router.get("/shots/{shot_id}", response_model=Shot)
    async def get_shot(shot_id: UUID) -> Shot:
        shot = await app.state.storage.get_shot(shot_id)
        if shot is None:
            raise HTTPException(404, "Shot not found")
        return shot

    class ShotNotesUpdate(BaseModel):
        notes: Optional[str] = None
        club: Optional[str] = None

    @router.post("/shots/{shot_id}/notes", response_model=Shot)
    async def update_shot_notes(shot_id: UUID, body: ShotNotesUpdate) -> Shot:
        shot = await app.state.storage.get_shot(shot_id)
        if shot is None:
            raise HTTPException(404, "Shot not found")
        if body.notes is not None:
            shot.notes = body.notes
        if body.club is not None:
            shot.club = body.club
        await app.state.storage.save_shot(shot)
        return shot

    @router.post("/test/trigger", response_model=Shot)
    async def manual_trigger() -> Shot:
        if not app.state.config.dev_mode:
            raise HTTPException(403, "Manual trigger is dev-mode only")
        return await app.state.processor_service.trigger_test_shot()

    class ScreenModeUpdate(BaseModel):
        mode: str

    class ScenarioShot(BaseModel):
        shot_id: int
        ball_speed_mph: float
        carry_yd: int
        launch_deg: float
        spin_rpm: int
        smash_factor: float
        apex_yd: int = 0
        hang_s: float = 0.0
        side_yd: float = 0.0
        quality: str = "good"

    class ScreenScenarioUpdate(BaseModel):
        mode: Optional[str] = None
        boot_progress: Optional[float] = None
        battery_pct: Optional[int] = None
        session_id: Optional[int] = None
        clock_hhmm: Optional[str] = None
        brightness: Optional[float] = None
        shot: Optional[ScenarioShot] = None
        # Health overrides — dev only. Let the debug panel simulate a
        # camera/radar drop-out without unplugging the hardware.
        camera_ok: Optional[bool] = None
        radar_ok: Optional[bool] = None
        uno_ok: Optional[bool] = None

    @router.get("/screen/state")
    def get_screen_state() -> dict[str, Any]:
        return app.state.screen_service.snapshot()

    @router.post("/screen/mode")
    def set_screen_mode(body: ScreenModeUpdate) -> dict[str, Any]:
        if not app.state.config.dev_mode:
            raise HTTPException(403, "Screen mode override is dev-mode only")
        mode = _parse_mode(body.mode)
        app.state.screen_service.set_mode(mode)
        return app.state.screen_service.snapshot()

    @router.post("/screen/scenario")
    def apply_screen_scenario(body: ScreenScenarioUpdate) -> dict[str, Any]:
        if not app.state.config.dev_mode:
            raise HTTPException(403, "Screen scenario API is dev-mode only")

        screen = app.state.screen_service
        if body.boot_progress is not None:
            screen.set_boot_progress(body.boot_progress)
        if body.brightness is not None:
            screen.set_brightness(body.brightness)

        update_state_payload: dict[str, Any] = {}
        if body.battery_pct is not None:
            update_state_payload["battery_pct"] = body.battery_pct
        if body.session_id is not None:
            update_state_payload["session_id"] = body.session_id
        if body.clock_hhmm is not None:
            update_state_payload["clock_hhmm"] = body.clock_hhmm
        if update_state_payload:
            screen.update_state(**update_state_payload)

        health_payload: dict[str, Any] = {}
        if body.camera_ok is not None:
            health_payload["camera_ok"] = body.camera_ok
        if body.radar_ok is not None:
            health_payload["radar_ok"] = body.radar_ok
        if body.uno_ok is not None:
            health_payload["uno_ok"] = body.uno_ok
        if health_payload:
            screen.update_health(**health_payload)

        if body.shot is not None:
            screen.on_shot(ShotMetrics(**body.shot.model_dump()))

        if body.mode is not None:
            screen.set_mode(_parse_mode(body.mode))

        return screen.snapshot()

    app.include_router(router)
