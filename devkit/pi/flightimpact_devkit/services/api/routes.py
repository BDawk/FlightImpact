"""REST routes for the dev kit API."""

from __future__ import annotations

import logging
import time
from typing import Optional
from uuid import UUID

import psutil
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from core.api_contract import API_VERSION
from core.models import DeviceStatus, Shot

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

    app.include_router(router)
