# FlightImpact

A custom golf launch monitor combining computer vision (high-speed camera) with Doppler radar (HB100), targeting within 5% accuracy of industry standard launch monitors.

## Repository layout

```
flightimpact/
├── core/        Reusable algorithms, models, and API contract — ships in production
├── app/         Progressive Web App — runs on phone, tablet, desktop browser
├── devkit/      Dev kit code — Pi 5 services, Uno firmware, breadboard config
├── hardware/    Schematics, BOMs, 3D-printable mounts (currently dev kit only)
└── docs/        Architecture, setup, calibration, API reference
```

The rule: **`core/` and `app/` never import from `devkit/`.** When the production
hardware is ready, a new top-level folder will be created (`production/`) that also
imports from `core/`. The dev kit becomes one of multiple frontends to the same
algorithm core.

## Quick start (dev kit)

See [`docs/devkit_setup.md`](docs/devkit_setup.md) for the full guide. TL;DR:

```bash
# On the Raspberry Pi 5
cd devkit/pi
pip install -e ".[dev]"
python -m flightimpact_devkit.api

# In a separate terminal — build and serve the app
cd app
npm install
npm run dev
```

Then open `http://flightimpact.local:5173` from any device on the same network.

## Architecture

See [`docs/architecture.md`](docs/architecture.md).
