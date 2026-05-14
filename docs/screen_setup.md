# Dev kit screen — Waveshare 1.69" ST7789V3 LCD

The dev kit has an on-device screen so you can read shot results without
pulling out your phone. The panel is a Waveshare 1.69" rounded-corner IPS
(240 × 280, ST7789V3), driven over SPI from the Pi.

The mockups in [`devkit/screen-mockups/index.html`](../devkit/screen-mockups/index.html)
are rendered at native resolution and show every state the screen can be in.

## Pinout — Pi 5 ↔ ST7789V3

Labels vary between breakouts. The columns below list the most common
variants — match whatever's silkscreened on your panel to the same row.

| Panel labels                            | Pi GPIO | Pi physical pin | Notes |
|-----------------------------------------|---------|-----------------|-------|
| VCC                                     | 3.3 V   | 1               | Don't use 5 V — the panel is 3.3 V only |
| GND                                     | GND     | 6               |       |
| **SDA** / DIN / MOSI / SDI / SI         | GPIO 10 | 19              | SPI0 MOSI. "SDA" here means serial data — these panels are SPI, not I²C |
| **SCL** / SCK / CLK / SCLK              | GPIO 11 | 23              | SPI0 SCLK |
| **RES** / RST / RESET                   | GPIO 27 | 13              | Reset |
| **DC**  / A0 / D/C                      | GPIO 25 | 22              | Data / command select |
| **CS**  / CE / SS                       | GPIO 8  | 24              | SPI0 CE0. Some 7-pin boards omit this — see note below |
| **BLK** / BL / LED / LITE               | GPIO 18 | 12              | Backlight, hardware PWM for dimming |

If your board only exposes 7 pins (no CS broken out), CS is hardwired low
on the PCB. Don't wire anything to Pi GPIO 8 in that case — the driver
works either way because the panel always thinks it's selected.

The pin choices avoid the rest of the dev kit: I²C (GPIO 2/3) is free for
future sensors, UART (GPIO 14/15) is free, GPIO 4 stays free for 1-Wire
temperature probes, and the audio HAT (if you add one) still has its
expected pins. The 9V op-amp board has its own battery — no Pi pins touched.

## Enable SPI

On Pi OS Bookworm, SPI is off by default. One-time setup:

```bash
sudo raspi-config nonint do_spi 0   # enables SPI without the curses UI
sudo reboot
```

After reboot, confirm:

```bash
ls /dev/spidev0.*        # expect /dev/spidev0.0 and /dev/spidev0.1
```

The screen driver uses `spidev0.0` (CE0).

## Python dependencies

The driver uses `spidev` for SPI and `gpiozero` (with the `lgpio` backend
that ships on Pi 5) for the DC / RST / BL pins, plus Pillow for rendering.

```bash
cd /opt/flightimpact
source venv/bin/activate
pip install spidev gpiozero lgpio Pillow
```

`lgpio` is what makes this work on Pi 5 — `RPi.GPIO` does NOT work on Pi 5.

## Smoke test

Once wired, run the smoke test to confirm the panel is alive before any UI
code touches it. The user needs to be in the `gpio` and `spi` groups (default
on Pi OS — `groups` to check). Run from the venv, no sudo:

```bash
cd /opt/flightimpact && source venv/bin/activate
python -m flightimpact_devkit.scripts.test_screen
```

If you need sudo for any reason (e.g. groups not set up yet), call the venv's
Python directly so the package is on the path:

```bash
sudo /opt/flightimpact/venv/bin/python -m flightimpact_devkit.scripts.test_screen
```

You should see, in order, ~1 second each:

1. Solid red, green, blue (sanity check for color order)
2. White, then black
3. Four 70-px corner squares — confirms orientation and that the rounded
   corner mask isn't clipping content
4. A diagonal gradient — confirms full 16-bit color depth

If you see colors but they're swapped (red where blue should be), the BGR
flag is wrong — pass `--bgr` to the test script. If the image is rotated
90°, pass `--rotate 90`.

## Common wiring problems

- **Nothing on screen, backlight is on.** SPI almost certainly isn't enabled
  (`ls /dev/spidev0.*` shows nothing). Re-run `raspi-config` and reboot.
- **Nothing on screen, backlight off.** BL wire not connected — the panel
  defaults to BL off. Connect BL to GPIO 18 (or any 3.3 V rail for a quick test).
- **Garbled / shifted image with visible offset on the left.** This is the
  classic 1.69" symptom — the driver is set to the 240×240 variant. The
  HAL handles this with column/row offsets of (0, 20); make sure you're on
  the latest `hal/st7789.py`.
- **Tearing / partial frames.** Drop `spi_hz` in the config from 40 MHz
  to 24 MHz. Most Pi 5 setups are fine at 40 MHz, but long jumper wires
  start to fail above ~30 MHz.

## Integrating with the API service

The screen service is wired into the same lifespan as camera and radar in
[`services/api/app.py`](../devkit/pi/flightimpact_devkit/services/api/app.py).
If no SPI panel is detected, it falls back to a `MockDisplay` that just
discards frames — so dev work on a laptop without hardware still runs cleanly.

To watch what's being drawn without a screen connected, set
`FLIGHTIMPACT_SCREEN_SNAPSHOT_DIR=/tmp/screen` and the mock display writes
each frame as a PNG. Useful for designing new screens.
