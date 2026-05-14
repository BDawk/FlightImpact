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
from flightimpact_devkit.hal import CameraSource, DisplaySink, RadarSource
from flightimpact_devkit.hal.hb100_radar import MockRadar, PiAudioRadar, SerialRadar
from flightimpact_devkit.hal.st7789 import MockDisplay, ST7789Display, is_panel_present
from flightimpact_devkit.hal.usb_camera import MockCamera, USBCamera
from flightimpact_devkit.services.api.routes import register_routes
from flightimpact_devkit.services.api.websocket import register_websocket
from flightimpact_devkit.services.camera import CameraService
from flightimpact_devkit.services.processor import ProcessorService
from flightimpact_devkit.services.radar import RadarService
from flightimpact_devkit.services.screen import ScreenService
from flightimpact_devkit.services.screen.state import ScreenMode
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


def _select_display(config: Config) -> DisplaySink:
    """Pick the ST7789 panel if SPI is wired up, otherwise mock."""
    if not config.screen.enabled:
        logger.info("Screen disabled in config — using MockDisplay")
        return MockDisplay(config.screen)
    if is_panel_present(config.screen):
        logger.info("Using ST7789Display on spidev%d.%d",
                    config.screen.spi_bus, config.screen.spi_device)
        return ST7789Display(config.screen)
    logger.warning("ST7789 not detected — using MockDisplay (set FLIGHTIMPACT_"
                   "SCREEN_SNAPSHOT_DIR to capture frames as PNG)")
    return MockDisplay(config.screen)


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
    display = _select_display(config)

    camera_service = CameraService(camera_source, config.camera)
    radar_service = RadarService(radar_source, config.radar, config.trigger)
    processor_service = ProcessorService(camera_service, radar_service, storage, config.trigger)
    screen_service = ScreenService(display, config.screen)

    app.state.camera_service = camera_service
    app.state.radar_service = radar_service
    app.state.processor_service = processor_service
    app.state.screen_service = screen_service

    # Screen comes up first so the user sees the boot splash while the rest spin up.
    screen_service.set_mode(ScreenMode.BOOT)
    await screen_service.start()

    screen_service.set_mode(ScreenMode.INITIALIZING)
    screen_service.update_health(storage_ok=True)
    screen_service.set_boot_progress(0.2)

    await camera_service.start()
    screen_service.update_health(
        camera_ok=isinstance(camera_source, USBCamera),
        camera_resolution=f"{config.camera.width}x{config.camera.height}",
        camera_fps=config.camera.fps,
    )
    screen_service.set_boot_progress(0.5)

    await radar_service.start()
    screen_service.update_health(radar_ok=not isinstance(radar_source, MockRadar))
    screen_service.set_boot_progress(0.8)

    await processor_service.start()
    screen_service.update_health(api_ok=True, api_port=config.api.port)
    screen_service.set_boot_progress(1.0)
    screen_service.set_mode(ScreenMode.HOME)

    logger.info("All services started — API ready on %s:%d", config.api.host, config.api.port)

    try:
        yield
    finally:
        logger.info("Shutting down services")
        await screen_service.stop()
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
