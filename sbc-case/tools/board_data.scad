// SPDX-License-Identifier: GPL-3.0-or-later
// Echoes, as one JSON line, the board data and Case Builder heights that spec.py places its regions with:
// mounting holes and GPIO pin field from SBC Model Framework, and Case Builder's own case dimensions.
// (str() of a numeric list is already JSON.)
include <../sbc_case.scad>
part = "none";

echo(str("BOARD_DATA", "{\"holes\":", sc_holes, ",\"gpio_x\":", sc_gx, ",\"gpio_y\":", sc_gy,
    ",\"depth\":", depth, ",\"case_z\":", case_z, ",\"floorthick\":", floorthick,
    ",\"bottom_height\":", bottom_height, ",\"case_x\":", sc_x, ",\"case_y\":", sc_y,
    ",\"ex\":", sc_ex, ",\"bolts\":", sc_bolts, "}"));
