# Bill of materials — dev kit

Total target: ~$200–$300 in parts, plus the camera you already have.

## Compute

| Item | Qty | Notes |
|------|-----|-------|
| Raspberry Pi 5 (4 GB) | 1 | 8 GB if you want headroom |
| Pi 5 active cooler | 1 | Required — Pi 5 throttles fast under sustained load |
| 27W USB-C PD power supply | 1 | The official Pi 5 supply, no substitutes |
| 32 GB A2 microSD | 1 | A2 rating matters — random IOPS during clip writes |
| Elegoo Uno R3 | 1 | Already on hand; trigger + strobe driver |

## Sensing

| Item | Qty | Notes |
|------|-----|-------|
| HB100 module | 1 | $5–10 on Amazon / AliExpress |
| Camera (IFWATER 12MP IMX577 25° lens) | 1 | Already on hand |
| USB sound card (CM108-based) | 1 | Cheapest path to ADC for HB100 IF |

Future upgrade for production sensing: global-shutter sensor (Arducam AR0234
1200P or similar) — see `docs/architecture.md` for why.

## HB100 amplifier circuit

| Item | Qty | Notes |
|------|-----|-------|
| LM358 dual op-amp DIP-8 | 1 | First stage |
| TL072 dual op-amp DIP-8 | 1 | Second stage (lower noise than LM358 here) |
| Resistors 1%: 10k, 100k, 1M | ~10 each | Gain-setting + biasing |
| Capacitors: 1µF, 10µF (electrolytic), 100nF (ceramic) | ~5 each | DC blocking + decoupling |
| 9V battery + clip | 1 | Cleaner than Pi 5V rail for analog front-end |
| Breadboard (full size, 830 tie-points) | 1 | |
| Jumper wire kit | 1 | M-M, M-F |

See `breadboard/` for the schematic and breadboard layout.

## Mounting + alignment

| Item | Qty | Notes |
|------|-----|-------|
| Mini ball-head tripod (camera) | 1 | For repeatable camera positioning |
| Adjustable mount (HB100) | 1 | Doesn't need to be precise — angle calibration handles offset |
| Hitting mat (small turf square) | 1 | Reference position for the ball |
| Alignment laser (optional) | 1 | Cheap line laser makes setup repeatable |

## Cables

| Item | Qty | Notes |
|------|-----|-------|
| USB-A to USB-A 2 m | 1 | Camera to Pi |
| USB-A to USB-B | 1 | Uno to Pi |
| 3.5mm TRS shielded | 1 | HB100 amp output to USB sound card line-in |
