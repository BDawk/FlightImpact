"""FastAPI app factory — composes services and exposes REST + WebSocket.

Lifespan management: services start on app startup and stop on shutdown.
A choice of camera/radar HAL implementations is made based on config.dev_mode
and what hardware is actually present (auto-fallback to mock).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from flightimpact_devkit.config import Config, load_config
from flightimpact_devkit.hal import CameraSource, RadarSource
from flightimpact_devkit.hal.hb100_radar import MockRadar, PiAudioRadar, SerialRadar
from flightimpact_devkit.hal.usb_camera import MockCamera, USBCamera
from flightimpact_devkit.services.api.routes import register_routes
from flightimpact_devkit.services.api.websocket import register_websocket
from flightimpact_devkit.services.camera import CameraService
from flightimpact_devkit.services.processor import ProcessorService
from flightimpact_devkit.services.radar import RadarService
from flightimpact_devkit.storage import Storage

logger = logging.getLogger(__name__)


def _select_camera(config: Config) -> CameraSource:
    """Pick a real USB camera if available, otherwise mock."""
    device = config.camera.device
    if device.startswith("/dev/video") and Path(device).exists():
        logger.info("Using USBCamera at %s", device)
        return USBCamera(config.camera)
    logger.warning("Camera device %s not found — using MockCamera", device)
    return MockCamera(config.camera)


def _select_radar(config: Config) -> RadarSource:
    """Pick the configured radar source, falling back to mock if unavailable."""
    if config.radar.use_pi_adc:
        try:
            return PiAudioRadar(config.radar)
        except Exception as e:
            logger.warning("PiAudioRadar unavailable (%s) — using MockRadar", e)
            return MockRadar(config.radar)
    if Path(config.radar.serial_port).exists():
        logger.info("Using SerialRadar at %s", config.radar.serial_port)
        return SerialRadar(config.radar)
    logger.warning("Serial radar not found — using MockRadar")
    return MockRadar(config.radar)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    config: Config = app.state.config

    # Storage
    storage = Storage(config.storage.db_path)
    await storage.open()
    app.state.storage = storage

    # Sensors
    camera_source = _select_camera(config)
    radar_source = _select_radar(config)

    camera_service = CameraService(camera_source, config.camera)
    radar_service = RadarService(radar_source, config.radar, config.trigger)
    processor_service = ProcessorService(camera_service, radar_service, storage, config.trigger)

    app.state.camera_service = camera_service
    app.state.radar_service = radar_service
    app.state.processor_service = processor_service

    await camera_service.start()
    await radar_service.start()
    await processor_service.start()

    logger.info("All services started — API ready on %s:%d", config.api.host, config.api.port)

    try:
        yield
    finally:
        logger.info("Shutting down services")
        await camera_service.stop()
        await radar_service.stop()
        await storage.close()


def create_app(config: Config | None = None) -> FastAPI:
    if config is None:
        config = load_config()

    app = FastAPI(
        title="FlightImpact Dev Kit API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.config = config

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)
    register_websocket(app)

    # Serve the built web app at / so REST + WebSocket + UI share an origin.
    # Override the location with FLIGHTIMPACT_WEBAPP_DIR if you build elsewhere.
    webapp_dir = Path(
        os.environ.get("FLIGHTIMPACT_WEBAPP_DIR", "/opt/flightimpact/app/dist")
    )
    if webapp_dir.is_dir() and (webapp_dir / "index.html").exists():
        app.mount("/", StaticFiles(directory=str(webapp_dir), html=True), name="webapp")
        logger.info("Serving web app from %s", webapp_dir)
    else:
        logger.info("Web app dist not found at %s — API only", webapp_dir)

    return app
