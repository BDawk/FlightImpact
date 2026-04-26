# Uno R3 firmware

The Uno acts as the dev kit's hardware-timing front-end:

| Pin  | Function |
|------|----------|
| D8   | Hardware trigger output (5 V pulse, ~100 µs) — wire to camera shutter sync or strobe driver |
| D9   | LED strobe PWM output — wire to a MOSFET gate driving an LED array |
| D13  | Onboard heartbeat LED |

## Flashing

1. Open `uno.ino` in the Arduino IDE
2. Select board: **Arduino Uno**
3. Select port: the `/dev/ttyACM*` (Linux/macOS) or `COMx` (Windows) the Uno appears on
4. Click Upload

Or with `arduino-cli`:

```bash
arduino-cli compile --fqbn arduino:avr:uno uno.ino
arduino-cli upload  --fqbn arduino:avr:uno --port /dev/ttyACM0 uno.ino
```

## Testing without the Pi

Open a serial monitor at 115200 baud and try:

```
PING        -> PONG
ID          -> FLIGHTIMPACT-DEVKIT v0.1
TRIG        -> OK   (and you should see a pulse on D8)
STROBE 200  -> OK   (D9 HIGH for 200 ms)
STROBE OFF  -> OK
```

## Phase 2 plans

Replace the simple text protocol with a binary frame protocol that streams
HB100 IF samples to the Pi at 20 kHz. The header (`magic + n_samples`) is
already documented in `flightimpact_devkit/hal/hb100_radar.py::SerialRadar`.
