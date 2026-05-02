// FlightImpact — top-of-base DOCK INTERFACE.
//
// Two parallel T-rails run along the long axis. A camera/radar/etc module
// slides onto the dock from the rear and clicks into a finger-release latch.
//
// The dock is intentionally exposed as TWO modules:
//   dock_male()    — the rails as POSITIVE geometry (added to the base shell)
//   dock_female()  — the matching slot as NEGATIVE geometry (subtracted from
//                    a module's underside)
// This guarantees the mating fit is parametrically symmetric — change a
// dimension in params.scad and both sides update together.

include <params.scad>;

// ---------- Single T-rail ----------
module _t_rail(length) {
    // rail base
    translate([-DOCK_RAIL_W/2, 0, 0])
        cube([DOCK_RAIL_W, length, DOCK_RAIL_H * 0.6]);
    // rail head (the T cap, wider at top so the slot retains it laterally)
    translate([-DOCK_RAIL_HEAD/2, 0, DOCK_RAIL_H * 0.6])
        cube([DOCK_RAIL_HEAD, length, DOCK_RAIL_H * 0.4]);
}

// ---------- Negative slot to receive a single T-rail ----------
module _t_slot(length) {
    // base channel, slightly wider for sliding fit
    translate([-(DOCK_RAIL_W + 2*DOCK_CL)/2, 0, 0])
        cube([DOCK_RAIL_W + 2*DOCK_CL, length, DOCK_RAIL_H * 0.6 + DOCK_CL]);
    // head undercut
    translate([-(DOCK_RAIL_HEAD + 2*DOCK_CL)/2, 0, DOCK_RAIL_H * 0.6 + DOCK_CL])
        cube([DOCK_RAIL_HEAD + 2*DOCK_CL, length, DOCK_RAIL_H * 0.4 + DOCK_CL]);
}

// ---------- Latch tab (positive, sits at front end of dock) ----------
module _latch_tab() {
    // a small ramp tab — module's matching pocket clicks over it
    hull() {
        translate([-DOCK_LATCH_W/2, 0, 0])
            cube([DOCK_LATCH_W, 0.5, DOCK_LATCH_H]);
        translate([-DOCK_LATCH_W/2, 5, 0])
            cube([DOCK_LATCH_W, 0.5, 0.5]);
    }
}

// ---------- Public: positive dock geometry (added to base top) ----------
// Place in PARENT coordinates so that origin = top-center of base, +Y = rear.
module dock_male() {
    // two T-rails, symmetric about Y axis
    for (sx = [-1, 1]) translate([sx * DOCK_RAIL_GAP/2, -DOCK_RAIL_LEN/2, 0])
        _t_rail(DOCK_RAIL_LEN);
    // front-edge latch tab
    translate([0, -DOCK_RAIL_LEN/2 - 0.001, 0]) _latch_tab();
    // cable pass-through stub (a small chimney that the module can route into)
    difference() {
        translate([0, -DOCK_CABLE_OD, 0])
            cylinder(d = DOCK_CABLE_OD + 4, h = 1.2);
        translate([0, -DOCK_CABLE_OD, -0.1])
            cylinder(d = DOCK_CABLE_OD, h = 2.0);
    }
}

// ---------- Public: matching female slot for a module's underside ----------
// Subtract this from the bottom of any module that should snap onto the dock.
module dock_female() {
    for (sx = [-1, 1]) translate([sx * DOCK_RAIL_GAP/2, -DOCK_RAIL_LEN/2, 0])
        _t_slot(DOCK_RAIL_LEN + DOCK_CL);
    // latch pocket
    translate([0, -DOCK_RAIL_LEN/2 - 0.5, 0])
        cube([DOCK_LATCH_W + 2*DOCK_CL, 6, DOCK_LATCH_H + DOCK_CL], center = false);
    // cable pass-through hole
    translate([0, -DOCK_CABLE_OD, -0.1])
        cylinder(d = DOCK_CABLE_OD + 2*DOCK_CL, h = 50);
}

// ---------- Self-test render ----------
// Comment this out when use<>ing the file from base.scad.
if ($preview) {
    color("DimGray") dock_male();
    color("Tomato", 0.4) translate([0, 0, 30]) dock_female();
}
