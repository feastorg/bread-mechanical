// Calibration coupons v2 for the slice case. Every rung uses case.scad's own parameters and modules
// (boss_d, insert_depth, spigot_recess, relief_d, head_d, head_depth, floor_t, roof_t, ear/pad/teardrop,
// bed_chamfer, facets); only the value under test changes per rung. The stack pair is cut from the
// real tray() and lid() with intersection(), as in ../print.scad.
// All parts are in print orientation with the bed face at z = 0. Case parameters come in via -D
// (resolved/<slice>.json), as spec.py passes them.
include <../../design/synth/case.scad>

part = "none";            // keep case.scad's own dispatch silent
coupon = "none";

// ---- rungs (README.md table mirrors these) ---------------------------------------------------------
insert_rungs = [3.8, 3.9, 4.0, 4.1, 4.2, 4.3];                      // pocket d, depth insert_depth
spigot_rungs = [[4.6, 3.2], [4.7, 3.2], [4.8, 3.2], [4.9, 3.2], [4.7, 3.3], [4.7, 3.4]];   // [OD, bore]
board_hole_d = 5.0;                                                 // slice MountingHole_5mm (NPTH)
ear_rungs = [3.4, 3.6, 3.8, 4.0];                                   // teardrop d

pitch = 13;               // rung spacing, ladders a and b
txt_h = 4.5;              // label cap size: strokes ~0.7 at DejaVu Sans Bold, one 0.6-nozzle line
txt_depth = 0.6;          // engraving depth: 3 layers at 0.2, 2 at 0.3
font = "DejaVu Sans:style=Bold";
coupon_hole = 2;          // stack pair: holes[2] = [74.1, -45.0] for S (as ../print.scad)
coupon_half = 10;

module label(s, x, y, size = txt_h, ztop) translate([x, y, ztop - txt_depth])
    linear_extrude(txt_depth + 1) text(s, size = size, font = font, halign = "center", valign = "center");
function fmt(v) = str(floor(v + 1e-6), ".", round((v - floor(v + 1e-6)) * 10));

// ---- a) insert-pocket ladder: tray boss, pocket mouth up (the tray prints roof-down) -------------------
// z 0..roof_t is the roof; the boss carries 1.5 solid below the pocket, the pocket (insert_depth) and the
// d(spigot_d + 0.3) x spigot_recess spigot recess at the top, exactly as tray() stacks them.
ins_floor = 1.5;
ins_top = roof_t + ins_floor + insert_depth + spigot_recess;
module insert_ladder() {
    n = len(insert_rungs);
    x1 = (n - 1) * pitch;
    difference() {
        union() {
            bedbox([-pitch / 2, x1 + pitch / 2], [-13, boss_d / 2 + 1.5], [0, roof_t], false);
            for (i = [0 : n - 1]) zcyl(i * pitch, 0, roof_t - eps, ins_top, boss_d);
        }
        for (i = [0 : n - 1]) {
            d = insert_rungs[i];
            zcyl(i * pitch, 0, ins_top - spigot_recess, ins_top + 1, spigot_d + 0.3);
            zcyl(i * pitch, 0, ins_top - spigot_recess - insert_depth, ins_top - spigot_recess + eps, d);
            zcyl(i * pitch, 0, -1, ins_top - spigot_recess - insert_depth + eps, relief_d);
            label(fmt(d), i * pitch, -8.5, ztop = roof_t);
        }
    }
}

// ---- b) spigot ladder: lid boss + spigot, outer face down (as the lid prints) ---------------------------
sp_boss_top = board_bot_nom - case_N[0];         // 4.83: boss face the board sits on
sp_top = spigot_top - case_N[0];                 // 6.83: spigot tip
module spigot_ladder() {
    n = len(spigot_rungs);
    x1 = (n - 1) * pitch;
    difference() {
        union() {
            bedbox([-pitch / 2, x1 + pitch / 2], [-17, boss_d / 2 + 1.5], [0, floor_t], false);
            for (i = [0 : n - 1]) {
                zcyl(i * pitch, 0, floor_t - eps, sp_boss_top, boss_d);
                zcyl(i * pitch, 0, sp_boss_top - eps, sp_top, spigot_rungs[i][0]);
            }
        }
        for (i = [0 : n - 1]) {
            r = spigot_rungs[i];
            zcyl(i * pitch, 0, -1, sp_boss_top, screw_clear_d);
            zcyl(i * pitch, 0, sp_boss_top - eps, sp_top + 1, r[1]);
            zcyl(i * pitch, 0, -1, head_depth, head_d);
            label(fmt(r[0]), i * pitch, -8.0, ztop = floor_t);
            label(fmt(r[1]), i * pitch, -13.5, size = 3.5, ztop = floor_t);
        }
    }
}

// printed stand-in for the slice board: board-thick plate, d5.0 holes at the ladder pitch
plate_t = board_t_nom;
module hole_plate() {
    n = len(spigot_rungs);
    x1 = (n - 1) * pitch;
    c = bed_chamfer;
    difference() {
        bedbox([-pitch / 2, x1 + pitch / 2], [-12, boss_d / 2 + 1.5], [0, plate_t], false);
        for (i = [0 : n - 1]) {
            zcyl(i * pitch, 0, -1, plate_t + 1, board_hole_d);
            // elephant's-foot relief on the hole's bed edge, as bedbox does on outer edges
            translate([i * pitch, 0, -eps]) cylinder(d1 = board_hole_d + 2 * c, d2 = board_hole_d, h = c, $fn = facets);
            label(str(i + 1), i * pitch, -8.0, ztop = plate_t);
        }
    }
}

// ---- c) ear teardrop ladder: tray ear pad + roof strip, built in the case frame, printed as the tray ----
ear_pitch = 11;
ear_strip = 18;           // roof strip depth along E: room for the labels beside the pad
module ear_ladder_case() {
    n = len(ear_rungs);
    a1 = (n - 1) * ear_pitch;
    difference() {
        union() {
            bedbox([case_E0, seat_E + ear_t], [-pad_d / 2 - 1, a1 + pad_d / 2 + 1], [ret_N - pad_d / 2 - 0.5, case_N[1]], true);
            bedbox([case_E0, case_E0 + ear_strip], [-pad_d / 2 - 1, a1 + pad_d / 2 + 1], [roof_in, case_N[1]], true);
            for (i = [0 : n - 1]) xcyl(seat_E, case_E0 + eps, i * ear_pitch, ret_N, pad_d);
        }
        for (i = [0 : n - 1]) xtear(seat_E - 1, seat_E + ear_t + 1, i * ear_pitch, ret_N, ear_rungs[i]);
    }
}
module ear_ladder() {
    n = len(ear_rungs);
    difference() {
        tray_bed() ear_ladder_case();
        // labels on the roof strip's top face in print (z = roof_t), beside the pad
        for (i = [0 : n - 1]) label(fmt(ear_rungs[i]), (seat_E + ear_t + case_E0 + ear_strip) / 2, -i * ear_pitch, ztop = roof_t);
    }
}

// ---- d) stack pair: real tray / lid corner around holes[coupon_hole] ------------------------------------
// (tray_bed / lid_bed / panel_bed: print orientation, from case.scad)
module coupon_box() {
    h = holes[coupon_hole];
    box([h[0] - coupon_half, h[0] + coupon_half], [h[1] - coupon_half, h[1] + coupon_half], [-100, 100]);
}

if (coupon == "insert_ladder") insert_ladder();
if (coupon == "spigot_ladder") spigot_ladder();
if (coupon == "hole_plate") hole_plate();
if (coupon == "ear_ladder") ear_ladder();
// "V2" engraved on a free corner of the roof (tray) / plate (lid), away from the boss and wall
stack_mark = [holes[coupon_hole][0] - 5.8, holes[coupon_hole][1] + 6];
if (coupon == "stack_tray") difference() {
    tray_bed() intersection() { tray(); coupon_box(); }
    label("V2", stack_mark[0], -stack_mark[1], size = 3.5, ztop = roof_t);
}
if (coupon == "stack_lid") difference() {
    lid_bed() intersection() { lid(); coupon_box(); }
    label("V2", stack_mark[0], stack_mark[1], size = 3.5, ztop = floor_t);
}

// ---- e) slide pair: both tower corners and both panel corners, cut from the real tray() and panel() ----------
// The case's opening is 80.4 wide; here the -A half moves toward +A so the coupon opening is slide_w wide. Each
// half is the real geometry: V groove and detent notch in the tower; strip corner with the finger, its
// round-ended slot and the bump. The panel is the blank one, roof strip down as the panel prints.
slide_w = 16;
slide_mid = open_A[1] - slide_w / 2;                    // the halves meet on this plane
slide_shift = open_A[1] - open_A[0] - slide_w;
module two_halves(E, N) {
    intersection() { children(); box(E, [slide_mid, 300], N); }
    translate([0, slide_shift, 0]) intersection() { children(); box(E, [-300, slide_mid - slide_shift], N); }
}
if (coupon == "slide_tray")                             // the towers' top 4.6 (grooves and notches), roof down
    tray_bed() two_halves([open_E0 - 4, case_E1 + 1], [case_N[1] - 4.6, case_N[1] + 1]) tray();
if (coupon == "slide_panel")                            // roof strip down, as the panel prints
    panel_bed() two_halves([pan_E0 - 1, fas_E1 + 1], [case_N[0] - 1, case_N[1] + 1]) panel();

// ---- f) legend strip: the RELAY 2 block of the real RLHT panel, engraved -------------------------------------
legend_A = [-24.5, 7.5];
module legend_box() box([case_E1 - 1, fas_E1 + 1], legend_A, [fas_N0 - 1, case_N[1] + 1]);
if (coupon == "legend_strip") panel_bed() intersection() { panel(); legend_box(); }

// ---- g) tilt jig: the packed neighbour's lid face, pitch - case thickness (0.8) above this case's roof ---------
// Sits on a real case with its panel off. Plate = the lid's own plan and outer chamfer, far half only (the
// driver only meets the lid's far edge); two spacer strips on the roof, clear of the opening; side lips locate it.
slot_pitch = 30.4;                                      // slot-interface-v1.1 pitch (-D from coupons_spec.py)
jig_E = [45, case_E1];
jig_n0 = case_N[1] + slot_pitch - (case_N[1] - case_N[0]);   // the neighbour's lid face: N 22.7
module tilt_jig_use() {
    shell(jig_n0, jig_n0 + floor_t, c_lid, 0, jig_E[0], jig_E[1]);
    for (e = [jig_E[0] + 1, open_E0 - 7]) box([e, e + 6], [case_A[0] + 3, case_A[1] - 3], [case_N[1], jig_n0 + 0.5]);
    for (s = [-1, 1]) let(a = s > 0 ? case_A[1] : case_A[0]) {
        box([jig_E[0] + 1, open_E0 - 1], s > 0 ? [a - 1.5, a + 2.3] : [a - 2.3, a + 1.5], [jig_n0 + 0.5, jig_n0 + floor_t]);
        box([jig_E[0] + 1, open_E0 - 1], s > 0 ? [a + 0.3, a + 2.3] : [a - 2.3, a - 0.3], [case_N[1] - 4, jig_n0 + floor_t]);
    }
}
if (coupon == "tilt_jig") translate([0, 0, jig_n0 + floor_t]) rotate([180, 0, 0]) tilt_jig_use();   // plate face down
