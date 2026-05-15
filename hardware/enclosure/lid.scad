// FlightImpact - removable side service lid.
//
// This lid covers the side opening on the -X wall of base.scad and fastens
// with four M3 screws into internal bosses.

include <params.scad>;

module _rrect(w, h, r = 3.0) {
    offset(r = r) offset(r = -r)
        square([w, h], center = true);
}

module service_lid_flat() {
    open_w = BASE_D - 2 * LID_BORDER;
    open_h = BASE_H - FLOOR_T - 2 * LID_BORDER;

    // Printed flat part: X=opening width (base Y), Y=opening height (base Z), Z=thickness.
    panel_w = open_w + 2 * (LID_BORDER - 2.0);
    panel_h = open_h + 2 * (LID_BORDER - 2.0);

    hole_y = panel_h / 2 - (LID_SCREW_EDGE_Z - 2.0);
    hole_x = panel_w / 2 - (LID_SCREW_EDGE_Y - 2.0);

    difference() {
        union() {
            // Face plate.
            linear_extrude(height = LID_T)
                _rrect(panel_w, panel_h, r = 4.0);

            // Inner locating lip.
            translate([0, 0, LID_T])
                linear_extrude(height = 2.0)
                    _rrect(open_w - 2 * LID_CL, open_h - 2 * LID_CL, r = 2.5);
        }

        // Screw clearances + shallow countersink.
        for (sx = [-1, 1], sy = [-1, 1]) {
            translate([sx * hole_x, sy * hole_y, -0.1])
                cylinder(d = LID_SCREW_D, h = LID_T + 2.3);
            translate([sx * hole_x, sy * hole_y, LID_T - LID_SCREW_HEAD_H])
                cylinder(d = LID_SCREW_HEAD_D, h = LID_SCREW_HEAD_H + 0.2);
        }
    }
}

service_lid_flat();
