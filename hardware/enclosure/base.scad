// FlightImpact - base chassis (horizontal rounded rectangle).
//
// Coordinate system:
//   X = long axis (left/right)
//   Y = depth axis (front/back), +Y is front panel
//   Z = vertical, Z=0 at print bed
//
// Internal layout is side-by-side:
//   left bay  = LiPo battery
//   right bay = Raspberry Pi 5 on M2.5 insert standoffs
//
// One side face is opened as a removable lid window for service access.

include <params.scad>;
use <dock.scad>;

// ---------- 2D rounded rectangle ----------
module _rrect(w, d, r = BASE_R) {
    offset(r = r) offset(r = -r)
        square([w, d], center = true);
}

module _outer_shell() {
    linear_extrude(height = BASE_H)
        _rrect(BASE_W, BASE_D, BASE_R);
}

module _inner_cavity() {
    translate([0, 0, FLOOR_T])
        linear_extrude(height = BASE_H - FLOOR_T + 0.1)
            offset(delta = -WALL_T)
                _rrect(BASE_W, BASE_D, BASE_R);
}

// ---------- Front-panel cutouts ----------
CUT_DEPTH = WALL_T + 2.0;

module _front_panel_cutouts() {
    front_y = BASE_D / 2 + 0.1;

    translate([FRONT_LED_X, front_y, FRONT_LED_Z])
        rotate([90, 0, 0])
            cylinder(d = LED_BEZEL_OD + 2 * CL_TIGHT, h = CUT_DEPTH);

    translate([FRONT_BTN_X, front_y, FRONT_BTN_Z])
        rotate([90, 0, 0])
            cylinder(d = BTN_HOLE_OD + 2 * CL_TIGHT, h = CUT_DEPTH);

    translate([FRONT_USBC_X, front_y - CUT_DEPTH/2 + 0.1, FRONT_USBC_Z])
        cube([9.5, CUT_DEPTH, 3.8], center = true);

    translate([FRONT_USBA_X, front_y - CUT_DEPTH/2 + 0.1, FRONT_USBA_Z])
        cube([13.8, CUT_DEPTH, 6.7], center = true);

    for (i = [0:VENT_SLOTS_N - 1]) {
        x = -((VENT_SLOTS_N - 1) * VENT_SLOT_PITCH) / 2 + i * VENT_SLOT_PITCH;
        translate([x, front_y - CUT_DEPTH/2 + 0.1, VENT_BASE_Z + VENT_SLOT_LEN/2])
            cube([VENT_SLOT_W, CUT_DEPTH, VENT_SLOT_LEN], center = true);
    }
}

module _rear_panel_cutouts() {
    rear_y = -BASE_D / 2 - 0.1;
    // Pi 5 rear I/O window, centered on the Pi bay.
    translate([PI_CENTER_X, rear_y + CUT_DEPTH/2 - 0.1, FLOOR_T + 11])
        cube([44, CUT_DEPTH, 18], center = true);

    for (i = [0:VENT_SLOTS_N - 1]) {
        x = -((VENT_SLOTS_N - 1) * VENT_SLOT_PITCH) / 2 + i * VENT_SLOT_PITCH;
        translate([x + PI_CENTER_X, rear_y + CUT_DEPTH/2 - 0.1, BASE_H - 10 - VENT_SLOT_LEN/2])
            cube([VENT_SLOT_W, CUT_DEPTH, VENT_SLOT_LEN], center = true);
    }
}

module _top_screen_cutouts() {
    top_z = BASE_H + 0.1;
    // Visible window through top surface.
    translate([SCREEN_CENTER_X, SCREEN_CENTER_Y, top_z])
        cylinder(h = WALL_T + 0.6, d = 0.1); // anchor for transform preview stability
    translate([SCREEN_CENTER_X, SCREEN_CENTER_Y, BASE_H - WALL_T - 0.2])
        cube([SCREEN_WINDOW_W, SCREEN_WINDOW_H, WALL_T + 1.0], center = true);

    // Pocket for the display PCB/module body from the inside top.
    translate([SCREEN_CENTER_X, SCREEN_CENTER_Y, BASE_H - SCREEN_POCKET_DEPTH])
        cube([
            SCREEN_MODULE_W + SCREEN_POCKET_CLR,
            SCREEN_MODULE_H + SCREEN_POCKET_CLR,
            SCREEN_MODULE_T + 0.2
        ], center = true);
}

module _right_side_interface_cutouts() {
    side_x = BASE_W / 2 + 0.1;

    // External PiSugar button access holes (two function buttons).
    for (zv = [PISUGAR_BTN_Z1, PISUGAR_BTN_Z2])
        translate([side_x, PI_CENTER_Y + PISUGAR_BTN_Y, zv])
            rotate([0, 90, 0])
                cylinder(d = PISUGAR_BTN_HOLE_D, h = WALL_T + 2.0);

    // External charging USB-C window (front-right wall).
    front_y = BASE_D / 2 + 0.1;
    translate([CHARGE_PORT_X, front_y - CUT_DEPTH/2 + 0.1, CHARGE_PORT_Z])
        cube([CHARGE_PORT_W, CUT_DEPTH, CHARGE_PORT_H], center = true);
}

module _side_lid_window() {
    lid_w = BASE_D - 2 * LID_BORDER;
    lid_h = BASE_H - FLOOR_T - 2 * LID_BORDER;
    translate([-BASE_W/2 - 0.1, 0, FLOOR_T + LID_BORDER + lid_h/2])
        cube([WALL_T + 1.2, lid_w, lid_h], center = true);
}

module _side_lid_bosses() {
    y_span = BASE_D / 2 - LID_SCREW_EDGE_Y;
    z0 = FLOOR_T + LID_SCREW_EDGE_Z;
    z1 = BASE_H - LID_SCREW_EDGE_Z;
    x0 = -BASE_W / 2 + WALL_T + 0.6;

    for (yy = [-y_span, y_span], zz = [z0, z1])
        translate([x0, yy, zz])
            rotate([0, 90, 0])
                difference() {
                    cylinder(d = LID_BOSS_OD, h = LID_BOSS_LEN);
                    translate([0, 0, -0.05])
                        cylinder(d = LID_SCREW_PILOT_D, h = LID_BOSS_LEN + 0.1);
                }
}

module _feet_recesses() {
    foot_d = 12.5;
    foot_h = 1.2;
    inset = 12;
    for (sx = [-1, 1], sy = [-1, 1])
        translate([sx * (BASE_W/2 - inset), sy * (BASE_D/2 - inset), -0.01])
            cylinder(d = foot_d, h = foot_h);
}

module _battery_retainers() {
    rx = BAT_W / 2 + BAT_BAY_CL;
    ry = BAT_D / 2 + BAT_BAY_CL;
    h = 4.0;
    w = 3.0;

    for (sx = [-1, 1], sy = [-1, 1])
        translate([
            BAT_CENTER_X + sx * (rx - w/2),
            BAT_CENTER_Y + sy * (ry - w/2),
            FLOOR_T,
        ])
            cube([w, w, h], center = true);
}

module _screen_clamps() {
    // Printed clamp tabs that lightly retain the screen PCB from inside.
    y0 = SCREEN_CENTER_Y + (SCREEN_MODULE_H + SCREEN_POCKET_CLR)/2 - SCREEN_CLAMP_W/2;
    y1 = SCREEN_CENTER_Y - (SCREEN_MODULE_H + SCREEN_POCKET_CLR)/2 + SCREEN_CLAMP_W/2;
    x0 = SCREEN_CENTER_X + (SCREEN_MODULE_W + SCREEN_POCKET_CLR)/2 - SCREEN_CLAMP_W/2;
    x1 = SCREEN_CENTER_X - (SCREEN_MODULE_W + SCREEN_POCKET_CLR)/2 + SCREEN_CLAMP_W/2;
    zc = BASE_H - SCREEN_POCKET_DEPTH - SCREEN_CLAMP_DROP/2;

    for (xx = [x0, x1], yy = [y0, y1])
        translate([xx, yy, zc])
            cube([SCREEN_CLAMP_W, SCREEN_CLAMP_W, SCREEN_CLAMP_DROP], center = true);
}

module _pi_insert_boss() {
    difference() {
        cylinder(d = PI_BOSS_OD, h = PI_STANDOFF_H);
        // Heat-set insert cavity from top face.
        translate([0, 0, PI_STANDOFF_H - PI_INSERT_DEPTH])
            cylinder(d = PI_INSERT_OD, h = PI_INSERT_DEPTH + 0.05);
        // Keep a narrow pilot below insert to avoid elephant-foot bulge.
        translate([0, 0, -0.05])
            cylinder(d = 2.2, h = PI_STANDOFF_H - PI_INSERT_DEPTH + PI_INSERT_BOTTOM_WEB);
    }
}

module _pi_mounts() {
    z0 = FLOOR_T;
    for (sx = [-1, 1], sy = [-1, 1]) {
        x = PI_CENTER_X + sx * PI_HOLE_DX / 2;
        y = PI_CENTER_Y + sy * PI_HOLE_DY / 2;
        // Pedestal from floor to board plane.
        translate([x, y, z0])
            cylinder(d = PI_BOSS_OD + 1.2, h = 1.2);
        // Insert boss at board plane.
        translate([x, y, z0 + 1.2])
            _pi_insert_boss();
    }
}

module _usb_posts() {
    post_h = 6.0;
    post_od = 6.0;
    usb_center_x = (BAT_CENTER_X + PI_CENTER_X) / 2;
    usb_center_y = BASE_D/2 - WALL_T - USB_D/2 - 7;

    for (sx = [-1, 1], sy = [-1, 1]) {
        x = usb_center_x + sx * USB_HOLE_DX / 2;
        y = usb_center_y + sy * USB_HOLE_DY / 2;
        translate([x, y, FLOOR_T])
            difference() {
                cylinder(d = post_od, h = post_h);
                translate([0, 0, -0.05]) cylinder(d = M25_CLEAR, h = post_h + 0.1);
            }
    }
}

module _pisugar_button_guides() {
    side_x = BASE_W/2 - WALL_T - 2.0;
    for (zv = [PISUGAR_BTN_Z1, PISUGAR_BTN_Z2])
        translate([side_x, PI_CENTER_Y + PISUGAR_BTN_Y, zv])
            rotate([0, 90, 0])
                difference() {
                    cylinder(d = PISUGAR_BTN_GUIDE_OD, h = 6.0);
                    translate([0, 0, -0.05])
                        cylinder(d = PISUGAR_BTN_GUIDE_ID, h = 6.1);
                }
}

// ============================================================================
//  Main base
// ============================================================================
module base_chassis() {
    union() {
        difference() {
            union() {
                _outer_shell();
                if (ENABLE_DOCK)
                    translate([0, 0, BASE_H]) rotate([0, 0, 90]) dock_male();
            }
            _inner_cavity();
            _front_panel_cutouts();
            _rear_panel_cutouts();
            _top_screen_cutouts();
            _right_side_interface_cutouts();
            _side_lid_window();
            _feet_recesses();
        }

        _battery_retainers();
        _pi_mounts();
        _usb_posts();
        _screen_clamps();
        _pisugar_button_guides();
        _side_lid_bosses();
    }
}

// ---------- Render ----------
base_chassis();
