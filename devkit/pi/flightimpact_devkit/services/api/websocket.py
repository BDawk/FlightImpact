"""WebSocket handler — pushes telemetry messages to subscribed clients.

By default a connected client receives device_status (every 2s) and shot events.
Live frames and radar spectrum require explicit subscribe messages — they're
only useful in the dev panel and would waste bandwidth otherwise.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from core.api_contract import WSCommand
from core.models import (
    DeviceStatus,
    LiveFrame,
    RadarSpectrum,
    Shot,
    ShotUpdated,
)
from flightimpact_devkit.services.api.routes import _get_temperature_c
import psutil

logger = logging.getLogger(__name__)

_START_TIME = time.monotonic()


class WSConnection:
    """One connected client and its subscription state."""

    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.subscribe_live_frame = False
        self.subscribe_radar_spectrum = False
        self.subscribe_logs = False
        self._send_lock = asyncio.Lock()

    async def send_json(self, payload: str) -> None:
        async with self._send_lock:
            await self.ws.send_text(payload)


def register_websocket(app: FastAPI) -> None:
    connections: set[WSConnection] = set()

    # ---- Subscriber wiring (called from services on every event) -----------------
    def on_preview_frame(jpeg: bytes, w: int, h: int) -> None:
        msg = LiveFrame(width=w, height=h, jpeg_b64=base64.b64encode(jpeg).decode("ascii"))
        payload = msg.model_dump_json()
        for c in list(connections):
            if c.subscribe_live_frame:
                asyncio.create_task(_safe_send(c, payload))

    def on_spectrum(freqs, mags, peak_freq, peak_speed) -> None:
        msg = RadarSpectrum(
            freq_hz=freqs.tolist(),
            magnitudes_db=mags.tolist(),
            peak_freq_hz=peak_freq,
            peak_speed_mph=peak_speed,
        )
        payload = msg.model_dump_json()
        for c in list(connections):
            if c.subscribe_radar_spectrum:
                asyncio.create_task(_safe_send(c, payload))

    def on_shot_update(shot: Shot) -> None:
        msg = ShotUpdated(shot=shot)
        payload = msg.model_dump_json()
        for c in list(connections):
            asyncio.create_task(_safe_send(c, payload))

    async def _safe_send(c: WSConnection, payload: str) -> None:
        try:
            await c.send_json(payload)
        except Exception:
            connections.discard(c)

    # ---- Subscribe to services on first connect ---------------------------------
    services_wired = {"done": False}
    unsub_callbacks: list = []

    def _wire_services_once() -> None:
        if services_wired["done"]:
            return
        unsub_callbacks.append(app.state.camera_service.subscribe_preview(on_preview_frame))
        unsub_callbacks.append(app.state.radar_service.subscribe_spectrum(on_spectrum))
        unsub_callbacks.append(app.state.processor_service.subscribe_shot_updates(on_shot_update))
        services_wired["done"] = True

    # ---- Heartbeat task pushes DeviceStatus to all clients every 2s -------------
    async def heartbeat_loop() -> None:
        while True:
            await asyncio.sleep(2.0)
            if not connections:
                continue
            try:
                status = DeviceStatus(
                    camera_connected=app.state.camera_service.connected,
                    camera_fps=app.state.camera_service.fps,
                    radar_connected=app.state.radar_service.connected,
                    uno_connected=False,
                    cpu_percent=psutil.cpu_percent(interval=None),
                    memory_percent=psutil.virtual_memory().percent,
                    temperature_c=_get_temperature_c(),
                    uptime_s=time.monotonic() - _START_TIME,
                    ap_mode=app.state.config.network.ap_mode,
                    wifi_ssid=None,
                    ip_address=None,
                )
                payload = status.model_dump_json()
                for c in list(connections):
                    asyncio.create_task(_safe_send(c, payload))
            except Exception:
                logger.exception("Heartbeat tick failed")

    heartbeat_started = {"done": False}

    @app.websocket("/ws")
    async def ws_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        _wire_services_once()
        if not heartbeat_started["done"]:
            asyncio.create_task(heartbeat_loop())
            heartbeat_started["done"] = True

        c = WSConnection(websocket)
        connections.add(c)
        logger.info("WS client connected (total: %d)", len(connections))

        try:
            while True:
                msg = await websocket.receive_text()
                _handle_command(c, msg)
        except WebSocketDisconnect:
            pass
        except Exception:
            logger.exception("WS handler error")
        finally:
            connections.discard(c)
            logger.info("WS client disconnected (total: %d)", len(connections))

    def _handle_command(c: WSConnection, msg: str) -> None:
        cmd = msg.strip()
        if cmd == WSCommand.SUBSCRIBE_LIVE_FRAME:
            c.subscribe_live_frame = True
        elif cmd == WSCommand.UNSUBSCRIBE_LIVE_FRAME:
            c.subscribe_live_frame = False
        elif cmd == WSCommand.SUBSCRIBE_RADAR_SPECTRUM:
            c.subscribe_radar_spectrum = True
        elif cmd == WSCommand.UNSUBSCRIBE_RADAR_SPECTRUM:
            c.subscribe_radar_spectrum = False
        elif cmd == WSCommand.SUBSCRIBE_LOGS:
            c.subscribe_logs = True
        elif cmd == WSCommand.UNSUBSCRIBE_LOGS:
            c.subscribe_logs = False
        else:
            logger.warning("Unknown WS command: %s", cmd)
