# Architecture

FlightImpact splits cleanly into three layers: **algorithm core**, **device-side
services**, and **client app**. The core ships in both the dev kit and (eventually)
the production unit; the device services wrap the core in hardware-specific glue;
the app talks to the device over a versioned API contract.

## Repository layout in one paragraph

`core/` holds the reusable algorithms (radar DSP, ball detection, tracking,
spin extraction, ballistics), Pydantic data models, and the API contract.
`app/` is the React PWA — same code on phone, tablet, desktop browser. `devkit/`
contains everything that's specific to the dev-kit hardware: Pi 5 services
(`devkit/pi/`), Uno R3 firmware (`devkit/firmware/uno/`), and the Pi-only setup
scripts and systemd units. Hardware schematics and BOMs live in `hardware/`.
The dev kit imports from core; core never imports from the dev kit.

## Data flow — from photons to phone

1. The **HB100** emits a 10.525 GHz CW signal. Reflections from the clubhead
   and ball mix down to an audio-frequency IF signal proportional to radial
   velocity. The two-stage LM358 / TL072 amplifier brings this from microvolts
   to a clean line-level signal the Pi (or Uno) can sample.

2. The **camera** runs at 1080p120 in MJPEG, dumping frames to a userspace ring
   buffer in the camera service. The ring is sized to hold ~2 seconds of
   history so we have pre-impact frames available the moment a trigger fires.

3. The **radar service** continuously runs FFT on incoming sample blocks,
   extracts the dominant Doppler peak, and watches for a peak above the
   trigger threshold. When the clubhead approach pushes the speed estimate
   above ~30 mph (configurable), it fires a trigger callback.

4. The **processor service** receives the trigger, waits the post-trigger
   window for the ball to fly through frame, snapshots both the camera ring
   buffer and the radar sample buffer, and runs the analysis pipeline.

5. The pipeline runs ball detection → ball tracking → club detection →
   spin extraction → sensor fusion → ballistics simulation, producing a
   `ShotMetrics` object with per-metric confidence values.

6. Results are persisted to SQLite and pushed to all connected clients via
   the WebSocket as `ShotUpdated` messages. The same socket carries device
   status heartbeats, optional live camera previews, and optional radar
   spectrum frames for the dev waterfall view.

## Why this split

Three forces drove the structure:

**Hardware will change.** Production units will not use a USB camera or a
breadboard radar. By keeping algorithms in `core/` and hardware glue in
`devkit/pi/hal/`, the production firmware can implement the same `CameraSource`
and `RadarSource` protocols and reuse every line of algorithm code.

**The app should not know which device it's talking to.** Dev kit and
production unit speak the same versioned REST + WebSocket contract. Same PWA
build can target either.

**Iteration speed during development.** Python on the Pi means the entire
CV/DSP stack runs in one process with no marshaling — OpenCV, NumPy, SciPy,
Pydantic all native. When something is too slow, profile and selectively port
hot paths to C++ via pybind11 — don't rewrite the world up front.

## Connectivity model

The Pi runs in either of two modes, switchable at runtime:

- **AP mode (default)**: Pi creates its own Wi-Fi hotspot. Phone connects
  directly with no router involved. This is what you use at the range, in the
  backyard, anywhere with no infrastructure.
- **Client mode**: Pi joins an existing Wi-Fi network. Used at home for OTA
  updates and (later) cloud sync.

Both modes serve the app at `http://flightimpact.local:8000` via mDNS, so you
never type IP addresses.

## Versioning

The API contract is versioned in `core/api_contract/__init__.py`. Bumping
`API_VERSION` is a breaking-change signal for clients. The TypeScript types in
`app/src/lib/types.ts` are kept in sync by hand for now; the future plan is to
generate them from FastAPI's OpenAPI spec at build time.
