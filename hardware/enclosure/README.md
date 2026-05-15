# Enclosure (Second Pass)

This enclosure is now a horizontal rounded-rectangle chassis with:

- Side-by-side internal bays for battery + Pi 5 stack
- Pi 5 mounting on M2.5 heat-set insert bosses
- Top screen window + pocket + retention clamps
- PiSugar external interface holes (two button channels)
- External USB-C charging window
- Removable side service lid with 4x M3 screws

## Files

- `params.scad`: all tunable dimensions
- `base.scad`: main body
- `lid.scad`: removable service lid (print separately)
- `dock.scad`: legacy docking rail interface (disabled by default)

## Critical Tune-First Parameters

These are intentionally parameterized because exact modules vary by vendor revision:

- Screen:
  - `SCREEN_ACTIVE_W`, `SCREEN_ACTIVE_H`
  - `SCREEN_MODULE_W`, `SCREEN_MODULE_H`, `SCREEN_MODULE_T`
  - `SCREEN_POCKET_CLR`
- PiSugar button alignment:
  - `PISUGAR_BTN_Y`, `PISUGAR_BTN_Z1`, `PISUGAR_BTN_Z2`
  - `PISUGAR_BTN_HOLE_D`, `PISUGAR_BTN_GUIDE_ID`
- External charging breakout:
  - `CHARGE_PORT_W`, `CHARGE_PORT_H`, `CHARGE_PORT_X`, `CHARGE_PORT_Z`

## Pi Mounting / Inserts

Pi bosses are sized for M2.5 heat-set inserts:

- `PI_INSERT_OD`
- `PI_INSERT_DEPTH`
- `PI_BOSS_OD`

Recommended process:

1. Print only a small boss test coupon using your insert brand.
2. Confirm press-fit and melt depth.
3. Adjust `PI_INSERT_OD` in 0.1 mm increments as needed.

## Notes

- `ENABLE_DOCK = false` by default to keep the top surface dedicated to screen integration.
- If you need dock rails again, set `ENABLE_DOCK = true` in `params.scad`.

## Suggested Validation Workflow

1. Print a low-infill draft of `base.scad` at 0.28 mm layer height.
2. Dry-fit battery, Pi, PiSugar stack, and screen module.
3. Measure offsets and update only `params.scad`.
4. Reprint final with production wall/infill.
