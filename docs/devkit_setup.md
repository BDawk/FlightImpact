# Dev kit setup

This guide walks through standing up a full FlightImpact dev kit from a fresh
Raspberry Pi 5. End state: you fire a trigger from the app, the device captures
a clip + radar samples, and metrics show up in the app within a second.

## What you need

**Hardware**
- Raspberry Pi 5 (4 GB or 8 GB)
- 32 GB+ A2-rated microSD card
- Official Pi 5 27W USB-C PD power supply
- USB camera (the IFWATER 12MP IMX577 / 25° lens or equivalent)
- HB100 Doppler radar module
- Two-stage op-amp board (LM358 or TL072) — see `hardware/breadboard/`
- USB sound card *or* MCP3008-on-SPI ADC for sampling the HB100 IF
- Elegoo Uno R3 (for trigger output and LED strobe driving — Phase 1.5+)
- A laptop or phone for the app

**Software on the Pi**
- Raspberry Pi OS Bookworm (64-bit, "Lite" is fine — no desktop needed)
- Python 3.11 or newer (Bookworm ships 3.11)
- Node.js 20+ (only needed if building the app on the Pi; usually you build on
  your laptop and `scp` the `dist/` folder over)

## First-boot setup

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Required system packages
sudo apt install -y python3-venv python3-pip git \
                    libopencv-dev v4l-utils \
                    avahi-daemon network-manager
```

## Pull the code

```bash
sudo mkdir -p /opt/flightimpact
sudo chown $USER:$USER /opt/flightimpact
cd /opt
git clone <your-repo-url> flightimpact
cd flightimpact
```

## Set up the Pi as a Wi-Fi access point

So you can connect from your phone anywhere, no router needed:

```bash
sudo ./devkit/pi/scripts/setup_ap_mode.sh "FlightImpact-Dev" "myStrongPass"
sudo ./devkit/pi/scripts/setup_mdns.sh flightimpact
```

After this:
- A new Wi-Fi network "FlightImpact-Dev" appears
- Connecting your phone gets you an IP on `192.168.4.0/24`
- The Pi is reachable at `flightimpact.local`

## Install and start the API service

```bash
sudo ./devkit/pi/scripts/install_services.sh /opt/flightimpact
```

This script:
1. Creates a `flightimpact` system user
2. Sets up `/var/lib/flightimpact/` (database + clips) and `/var/log/flightimpact/`
3. Creates a venv at `/opt/flightimpact/venv` and installs `core/` and `devkit/pi/`
4. Installs and enables the `flightimpact-api` systemd unit

Verify it's running:

```bash
systemctl status flightimpact-api
journalctl -u flightimpact-api -f
```

You should see lines like `Camera service started`, `Radar service started`,
`Storage opened`, and `Uvicorn running on http://0.0.0.0:8000`.

If no camera / radar is connected, the service falls back to mock sources and
still starts cleanly — useful for app development without the rig set up.

## Build and serve the app

On your laptop (where Node is installed):

```bash
cd app
npm install
npm run build
```

Then either:

**Option A — serve via Python on the Pi** (no Node needed on the Pi):

```bash
# On your laptop, after building:
scp -r dist/* pi@flightimpact.local:/opt/flightimpact/app/dist/

# On the Pi:
cd /opt/flightimpact/app/dist
python3 -m http.server 5173 --bind 0.0.0.0
```

**Option B — dev mode on your laptop, talking to the Pi**:

```bash
# In app/.env.local:
VITE_API_HOST=http://flightimpact.local:8000

npm run dev
# Open http://localhost:5173
```

## Open the app on your phone

1. Connect your phone to the `FlightImpact-Dev` Wi-Fi
2. Open Safari/Chrome and go to `http://flightimpact.local:5173`
3. Tap "Add to Home Screen" — it installs as a PWA and looks like an app

You should see a green Online pill in the header. The status row shows
camera + radar connection state. Hit the **Test shot** button to fire a manual
trigger and verify the round-trip works.

## Calibrate

See [`calibration.md`](calibration.md). Short version:

1. Print a 9x6 checkerboard and tape it to a flat surface
2. From the Settings tab → Calibration → "Start camera calibration", capture
   ~15 frames of the board at varied angles
3. Set up the radar at the firing position, point it down-range, and hit
   "Calibrate radar zero" — this learns the cosine angle correction

## Wiring up the Uno (optional Phase 1.5)

The Uno provides a hardware trigger output and an LED strobe driver. Wire it:

| Uno pin | Function | Connect to |
|---------|----------|------------|
| D8      | 5 V trigger pulse | Camera GPIO trigger or strobe FET |
| D9      | Strobe PWM (5 V) | LED array gate driver |
| GND     | Common ground | Strobe ground, camera ground |
| USB     | Power + data | Pi USB port |

Flash `devkit/firmware/uno/uno.ino` from the Arduino IDE. The Pi will
auto-detect the Uno on `/dev/ttyACM0` once the radar service supports it
(Phase 1.5).
