// FlightImpact enclosure — central parameters file
// All dimensions in millimeters. Change a value here, the whole project updates.
// Anything marked TODO_MEASURE needs calipers on the real part.

/* PRINT + GLOBAL TOLERANCE */
$fn = 64;
PRINT_LAYER_H   = 0.2;
PRINT_NOZZLE    = 0.4;
WALL_T          = 2.4;
FLOOR_T         = 2.0;
LID_T           = 2.0;
INSERT_BOSS_OD  = 5.0;
INSERT_BORE_ID  = 4.2;
M3_CLEAR        = 3.4;
M25_CLEAR       = 2.7;
CL_TIGHT        = 0.15;
CL_NORMAL       = 0.30;
CL_LOOSE        = 0.50;

/* RASPBERRY PI 5 */
PI_W            = 85.0;
PI_D            = 56.0;
PI_PCB_T        = 1.6;
PI_HOLE_DX      = 58.0;
PI_HOLE_DY      = 49.0;
PI_HOLE_INSET_X = 3.5;
PI_HOLE_INSET_Y = 3.5;
PI_STANDOFF_H   = 5.0;
PI_TOP_CLR      = 22.0;

/* BATTERY — YELUFT 10000 mAh single-cell LiPo. TODO_MEASURE all three. */
BAT_W           = 110.0;
BAT_D           = 65.0;
BAT_H           = 12.0;
BAT_LEAD_LEN    = 60.0;
BAT_BAY_CL      = 1.5;

/* USB CHARGE/DISCHARGE BOARD — TBD. Placeholder generic 30 x 55mm bay. */
USB_W           = 55.0;
USB_D           = 30.0;
USB_H           = 12.0;
USB_HOLE_DX     = 49.0;
USB_HOLE_DY     = 24.0;
USB_USBC_OFFSET = 8.0;
USB_USBA_OFFSET = 8.0;

/* STATUS LED — pre-wired panel mount. TODO_MEASURE. */
LED_BEZEL_OD    = 8.5;
LED_NUT_OD      = 11.0;
LED_BODY_LEN    = 18.0;

/* MOMENTARY BUTTON — 12mm panel mount family. TODO_MEASURE. */
BTN_HOLE_OD     = 12.5;
BTN_NUT_OD      = 15.0;
BTN_BODY_LEN    = 22.0;

/* OVERALL ENCLOSURE — tool-battery silhouette */
INSIDE_W        = max(PI_W, BAT_W) + 2 * BAT_BAY_CL;
INSIDE_D        = max(PI_D, BAT_D) + 2 * BAT_BAY_CL;
INSIDE_H        = FLOOR_T + BAT_H + 2 + PI_STANDOFF_H + PI_PCB_T + PI_TOP_CLR;
BASE_W          = INSIDE_W + 2 * WALL_T;
BASE_D          = INSIDE_D + 2 * WALL_T;
BASE_H          = INSIDE_H;
BASE_R          = 4.0;
BASE_TAPER      = 8.0;     // strong tool-battery taper on short axis

/* DOCK INTERFACE on top of base */
DOCK_RAIL_LEN   = BASE_W - 2 * BAT_BAY_CL - 2 * WALL_T;
DOCK_RAIL_GAP   = 50.0;
DOCK_RAIL_W     = 8.0;
DOCK_RAIL_H     = 4.0;
DOCK_RAIL_HEAD  = 12.0;
DOCK_RAIL_FILLET= 0.6;
DOCK_LATCH_W    = 14.0;
DOCK_LATCH_H    = 3.0;
DOCK_CABLE_OD   = 8.0;
DOCK_CL         = CL_NORMAL;

/* PANELS — front-face feature positions (X from center, Z from floor) */
FRONT_USBC_X    = -12.0;
FRONT_USBC_Z    =  12.0;
FRONT_USBA_X    =  12.0;
FRONT_USBA_Z    =  12.0;
FRONT_LED_X     = -22.0;
FRONT_LED_Z     =  28.0;
FRONT_BTN_X     =  22.0;
FRONT_BTN_Z     =  28.0;

/* VENTILATION */
VENT_SLOT_W     = 2.0;
VENT_SLOT_LEN   = 4.0;
VENT_SLOTS_N    = 8;
VENT_SLOT_PITCH = 5.0;
VENT_BASE_Z     = 4.0;
