"""FastAPI gateway — REST + WebSocket interface for the dev kit."""

from flightimpact_devkit.services.api.app import create_app

__all__ = ["create_app"]
