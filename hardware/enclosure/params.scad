// FlightImpact enclosure - central parameter file.
// All dimensions in mm.

/* PRINT + GLOBAL TOLERANCE */
$fn = 64;
PRINT_LAYER_H    = 0.2;
PRINT_NOZZLE     = 0.4;
WALL_T           = 2.4;
FLOOR_T          = 2.4;
LID_T            = 2.4;
M3_CLEAR         = 3.4;
M25_CLEAR        = 2.7;
CL_TIGHT         = 0.15;
CL_NORMAL        = 0.30;
CL_LOOSE         = 0.50;

/* RASPBERRY PI 5 */
PI_W             = 85.0;
PI_D             = 56.0;
PI_PCB_T         = 1.6;
PI_HOLE_DX       = 58.0;
PI_HOLE_DY       = 49.0;
PI_STANDOFF_H    = 5.2;
PI_TOP_CLR       = 14.0;

// M2.5 heat-set insert geometry (typical 3.5-4.0mm OD inserts)
PI_BOSS_OD           = 7.2;
PI_INSERT_OD         = 3.9;
PI_INSERT_DEPTH      = 4.8;
PI_INSERT_BOTTOM_WEB = 1.4;

/* BATTERY - single-cell LiPo pack */
BAT_W            = 110.0;
BAT_D            = 65.0;
BAT_H            = 12.0;
BAT_LEAD_LEN     = 60.0;
BAT_BAY_CL       = 1.5;

/* USB CHARGE/DISCHARGE BOARD */
USB_W            = 55.0;
USB_D            = 30.0;
USB_H            = 12.0;
USB_HOLE_DX      = 49.0;
USB_HOLE_DY      = 24.0;

/* STATUS LED / BUTTON */
LED_BEZEL_OD     = 8.5;
LED_NUT_OD       = 11.0;
LED_BODY_LEN     = 18.0;
BTN_HOLE_OD      = 12.5;
BTN_NUT_OD       = 15.0;
BTN_BODY_LEN     = 22.0;

/* SCREEN MODULE - Waveshare 1.69" ST7789V3 (tunable with calipers) */
SCREEN_ACTIVE_W      = 30.6;
SCREEN_ACTIVE_H      = 36.8;
SCREEN_WINDOW_CL     = 0.8;
SCREEN_WINDOW_W      = SCREEN_ACTIVE_W + SCREEN_WINDOW_CL;
SCREEN_WINDOW_H      = SCREEN_ACTIVE_H + SCREEN_WINDOW_CL;
SCREEN_MODULE_W      = 37.5;
SCREEN_MODULE_H      = 41.0;
SCREEN_MODULE_T      = 6.0;
SCREEN_POCKET_CLR    = 0.6;
SCREEN_POCKET_DEPTH  = 2.0;
SCREEN_CLAMP_W       = 4.0;
SCREEN_CLAMP_T       = 2.0;
SCREEN_CLAMP_DROP    = 4.0;

/* PISUGAR 3 PLUS (Pi 5 HAT) - envelope + externalized interface */
PISUGAR_W            = 88.0;
PISUGAR_D            = 58.0;
PISUGAR_H            = 11.5;
PISUGAR_SIDE_CLR     = 2.0;
PISUGAR_BTN_HOLE_D   = 5.2;   // for printed button plungers
PISUGAR_BTN_GUIDE_OD = 7.0;
PISUGAR_BTN_GUIDE_ID = 5.4;
PISUGAR_BTN_Z1       = 23.0;
PISUGAR_BTN_Z2       = 33.0;
PISUGAR_BTN_Y        = -8.0;

/* EXTERNAL CHARGING PORT (panel-mount USB-C breakout) */
CHARGE_PORT_W        = 10.2;
CHARGE_PORT_H        = 4.2;
CHARGE_PORT_X        = 34.0;
CHARGE_PORT_Z        = 14.0;

/* SIDE LID FASTENING */
LID_SCREW_D          = M3_CLEAR;
LID_SCREW_HEAD_D     = 6.6;
LID_SCREW_HEAD_H     = 2.2;
LID_BOSS_OD          = 8.0;
LID_BOSS_LEN         = 9.0;
LID_SCREW_PILOT_D    = 2.7;
LID_SCREW_EDGE_Y     = 11.0;
LID_SCREW_EDGE_Z     = 10.0;

/* OVERALL ENCLOSURE - horizontal rounded rectangle */
PI_GAP_ABOVE_BAT = 3.0;
COMP_GAP_X       = 14.0;
BAY_SIDE_CLR     = 6.0;
INSIDE_W         = BAT_W + PI_W + COMP_GAP_X + 2 * BAY_SIDE_CLR;
INSIDE_D         = max(BAT_D, PI_D) + 2 * BAY_SIDE_CLR;
INSIDE_H         = FLOOR_T + max(BAT_H + 6.0, PI_STANDOFF_H + PI_PCB_T + PI_TOP_CLR + 4.0);
BASE_W           = INSIDE_W + 2 * WALL_T;
BASE_D           = INSIDE_D + 2 * WALL_T;
BASE_H           = INSIDE_H;
BASE_R           = 11.0;
BASE_TAPER       = 0.0;  // kept for backward compatibility with preview script

BAT_CENTER_X     = -(PI_W/2 + COMP_GAP_X/2);
PI_CENTER_X      =  (BAT_W/2 + COMP_GAP_X/2);
BAT_CENTER_Y     = 0.0;
PI_CENTER_Y      = 0.0;
SCREEN_CENTER_X  = BAT_CENTER_X;
SCREEN_CENTER_Y  = 0.0;

/* FRONT/REAR FEATURE POSITIONS (X from center, Z from floor) */
FRONT_USBC_X     = -18.0;
FRONT_USBC_Z     =  13.0;
FRONT_USBA_X     =  18.0;
FRONT_USBA_Z     =  13.0;
FRONT_LED_X      = -34.0;
FRONT_LED_Z      =  30.0;
FRONT_BTN_X      =  34.0;
FRONT_BTN_Z      =  30.0;

/* SIDE LID */
LID_BORDER       = 8.0;
LID_CL           = CL_NORMAL;

/* VENTILATION */
VENT_SLOT_W      = 2.2;
VENT_SLOT_LEN    = 14.0;
VENT_SLOTS_N     = 14;
VENT_SLOT_PITCH  = 5.5;
VENT_BASE_Z      = 6.0;

/* DOCK INTERFACE (optional; legacy compatibility) */
ENABLE_DOCK      = false;
DOCK_RAIL_LEN    = BASE_W - 24.0;
DOCK_RAIL_GAP    = 50.0;
DOCK_RAIL_W      = 8.0;
DOCK_RAIL_H      = 4.0;
DOCK_RAIL_HEAD   = 12.0;
DOCK_RAIL_FILLET = 0.6;
DOCK_LATCH_W     = 14.0;
DOCK_LATCH_H     = 3.0;
DOCK_CABLE_OD    = 8.0;
DOCK_CL          = CL_NORMAL;
