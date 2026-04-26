"""Main entry point — run with `python -m flightimpact_devkit.services.api`."""

from __future__ import annotations

import logging
import sys

import uvicorn

from flightimpact_devkit.config import load_config
from flightimpact_devkit.services.api.app import create_app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = load_config()
    app = create_app(config)
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
    sys.exit(0)
