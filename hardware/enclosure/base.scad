// FlightImpact — main BASE chassis ("tool battery" silhouette).
//
// Coordinate system (right-handed, +Z up):
//   X = long axis (BASE_W)  -- "left/right"
//   Y = short axis (BASE_D) -- "front/back"; +Y is the FRONT panel
//   Z = vertical             -- Z=0 is the BOTTOM face of the chassis
//
// Construction strategy: hull() two rounded cap profiles. Bottom cap is the
// full BASE_W × BASE_D rectangle; top cap is tapered inward — strongly on the
// short axis (BASE_TAPER), mildly on the long axis (BASE_TAPER * LONG_TAPER_F).
// This gives the recognizable cordless-tool-battery silhouette while keeping
// most of the top dock surface usable.
//
// One long side is removable as a snap-fit lid (panel_lid.scad) so you can
// swap the Pi or battery without unscrewing anything.

include <params.scad>;
use <dock.scad>;

LONG_TAPER_F = 0.3;            // long-axis taper as fraction of short-axis taper

// ---------- 2D rounded rectangle (corner radius BASE_R) ----------
module _rrect(w, d, r = BASE_R) {
    offset(r = r) offset(r = -r)
        square([w, d], center = true);
}

// ---------- Outer hull: rounded frustum ----------
module _hull_outer() {
    hull() {
        // bottom cap
        linear_extrude(height = 0.01)
            _rrect(BASE_W, BASE_D);
        // top cap, tapered
        translate([0, 0, BASE_H - 0.01])
            linear_extrude(height = 0.01)
                _rrect(BASE_W - 2 * BASE_TAPER * LONG_TAPER_F,
                       BASE_D - 2 * BASE_TAPER);
    }
}

// ---------- Inner hollow: same shape, walls + floor offset inward ----------
module _hull_inner() {
    // start FLOOR_T above the bottom, run to top of base (top is open — dock
    // closes it). Walls offset inward by WALL_T from the outer profile.
    hull() {
        translate([0, 0, FLOOR_T])
            linear_extrude(height = 0.01)
                offset(delta = -WALL_T)
                    _rrect(BASE_W, BASE_D);
        translate([0, 0, BASE_H + 0.01])
            linear_extrude(height = 0.01)
                offset(delta = -WALL_T)
                    _rrect(BASE_W - 2 * BASE_TAPER * LONG_TAPER_F,
                           BASE_D - 2 * BASE_TAPER);
    }
}

// ---------- Front-panel cutouts ----------
// Front face is at Y = +BASE_D/2 (slightly less at the top due to taper).
// Cuts go in -Y direction, deep enough to clear the (tapered) wall.
CUT_DEPTH = WALL_T + BASE_TAPER + 1.0;  // deep enough at any Z to fully pierce

module _front_panel_cutouts() {
    front_y = BASE_D / 2 + 0.1;
    // LED hole
    translate([FRONT_LED_X, front_y, FRONT_LED_Z])
        rotate([90, 0, 0])
            cylinder(d = LED_BEZEL_OD + 2 * CL_TIGHT, h = CUT_DEPTH);
    // Button hole
    translate([FRONT_BTN_X, front_y, FRONT_BTN_Z])
        rotate([90, 0, 0])
            cylinder(d = BTN_HOLE_OD + 2 * CL_TIGHT, h = CUT_DEPTH);
    // USB-C charge in (~9.0 × 3.5mm jack body, slop added)
    translate([FRONT_USBC_X, front_y - CUT_DEPTH/2 + 0.1, FRONT_USBC_Z])
        cube([9.5, CUT_DEPTH, 3.8], center = true);
    // USB-A discharge out
    translate([FRONT_USBA_X, front_y - CUT_DEPTH/2 + 0.1, FRONT_USBA_Z])
        cube([13.8, CUT_DEPTH, 6.7], center = true);
    // Front ventilation grille (low intake) — bottom row
    for (i = [0:VENT_SLOTS_N - 1]) {
        x = -((VENT_SLOTS_N - 1) * VENT_SLOT_PITCH) / 2 + i * VENT_SLOT_PITCH;
        translate([x, front_y - CUT_DEPTH/2 + 0.1, VENT_BASE_Z + VENT_SLOT_LEN/2])
            cube([VENT_SLOT_W, CUT_DEPTH, VENT_SLOT_LEN], center = true);
    }
}

// ---------- Rear-panel cutouts ----------
module _rear_panel_cutouts() {
    rear_y = -BASE_D / 2 - 0.1;
    // Pi 5 connector cluster window (HDMI x2, Ethernet, 3.5mm)
    pi_floor_z = FLOOR_T + BAT_H + 2 + PI_STANDOFF_H + 1;
    translate([0, rear_y + CUT_DEPTH/2 - 0.1, pi_floor_z + 9])
        cube([44, CUT_DEPTH, 18], center = true);
    // Rear ventilation grille (high exhaust)
    for (i = [0:VENT_SLOTS_N - 1]) {
        x = -((VENT_SLOTS_N - 1) * VENT_SLOT_PITCH) / 2 + i * VENT_SLOT_PITCH;
        translate([x, rear_y + CUT_DEPTH/2 - 0.1, BASE_H - 8 - VENT_SLOT_LEN/2])
            cube([VENT_SLOT_W, CUT_DEPTH, VENT_SLOT_LEN], center = true);
    }
}

// ---------- Removable side-lid window ----------
// Cut through the +Y... wait, no, +Y is the front. Cut through the -X side
// (left long side). Use a slim border around the lid opening.
module _side_lid_window() {
    lid_inset = 6;
    lid_w = BASE_D - 2 * lid_inset;
    lid_h = BASE_H - 2 * lid_inset - FLOOR_T;
    translate([-BASE_W/2 - 0.1, 0, FLOOR_T + lid_inset + lid_h/2])
        cube([CUT_DEPTH, lid_w, lid_h], center = true);
}

// ---------- Foot recesses (bottom) ----------
module _feet_recesses() {
    foot_d = 12.5;
    foot_h = 1.2;
    inset = 12;
    for (sx = [-1, 1], sy = [-1, 1])
        translate([sx * (BASE_W/2 - inset), sy * (BASE_D/2 - inset), -0.01])
            cylinder(d = foot_d, h = foot_h);
}

// ---------- Dock placement on top of base ----------
// Top surface = Z=BASE_H. dock_male() builds rails along its local Y; we want
// rails along world X (the long axis), so rotate 90° about Z.
module _dock_on_top() {
    translate([0, 0, BASE_H])
        rotate([0, 0, 90])
            dock_male();
}

// ---------- Top closure plate (between hull top and dock) ----------
// Above _hull_inner the cavity is open. Add a thin closure plate with a hole
// for cable pass-through, so the chassis is enclosed and the dock has a real
// surface to ride on.
module _top_closure() {
    plate_t = 2.0;
    translate([0, 0, BASE_H - plate_t]) difference() {
        linear_extrude(height = plate_t)
            offset(delta = -WALL_T)
                _rrect(BASE_W - 2 * BASE_TAPER * LONG_TAPER_F,
                       BASE_D - 2 * BASE_TAPER);
        // cable pass-through (matches dock)
        translate([0, -DOCK_CABLE_OD, -0.1])
            cylinder(d = DOCK_CABLE_OD, h = plate_t + 0.2);
    }
}

// ============================================================================
//  Main base
// ============================================================================
module base_chassis() {
    difference() {
        union() {
            _hull_outer();
            _top_closure();
            _dock_on_top();
        }
        _hull_inner();
        _front_panel_cutouts();
        _rear_panel_cutouts();
        _side_lid_window();
        _feet_recesses();
    }
}

// ---------- Render ----------
base_chassis();
