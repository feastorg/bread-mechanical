// Slice case: one-sided clamshell (tray + lid) with a sliding front panel.
// World frame = slot frame of slot-interface-v1.1: X = E (away from the loaf), Y = A (pin 1 +),
// Z = N (slice top/THT side +). Origin B = centre of the slice bus pin row.
//
// TRAY  = THT-side shell: roof, walls, bus wall with the guide window, full-height end flanges with the
//         retention ears, 4 insert bosses (bus pair tied to the walls, far pair inside two corner towers).
//         The roof is open over the terminal zone between the towers. Prints roof-down.
// LID   = SMT-side plate: 4 bosses with locating spigots, socket tongue, screw counterbores. Prints outer face down.
// PANEL = the one per-slice part (panel.scad): roof strip with V tongues that slide in the tower grooves, a
//         spring-finger detent, and the front fascia that carries the legend. Prints roof strip down.
// The tray references the board TOP face (the socket's datum). The lid clamps the board from below and floats
// with board thickness; rim_gap absorbs it. 4 x M3x10 go in from the lid face, into heat-set inserts. No nuts.
//
// Driven by -D only: format values from tools/resolve.py (formats.yaml), interface values from
// slot-interface-v1.1.json, modifiers and panel data from the slice's own data. Defaults below are an S fallback.

part = "assembly";

// ---- format (resolved; -D) ----------------------------------------------------------------
board_E = [9.10, 79.10];
board_A = [-50.0, 50.0];
board_r = 5.0;                 // board plan corner radius (formats.yaml corner_r)
holes = [[14.1, -45.0], [74.1, -45.0], [14.1, 45.0], [74.1, 45.0]];
ret_A = [-56.4, 56.4];
usb_ports = [["-A", 36.7, 13.35, -0.12, 18.28, 1.5]];   // [side, E centre, width, N0, N1, corner r] (resolve.py, from
                                                        // the board's own MCU USB and formats.yaml mcu_access)

// ---- interface v1.1 (-D) --------------------------------------------------------------------
env_N = [-7.9, 22.1];
seat_E = 6.70;
face_gap = 0.3;
board_top_N = -1.27;
tongue_A = 12.7;
tongue_E_min = 4.67;
win_A = 15.4;
win_N = [-1.1, 5.92];
win_E_max = 15.5;
ret_N = 11.5;
ear_t = 5.0;
ear_hole_d = 3.8;
pad_d = 9.0;
socket_A = 12.7;
socket_N = [-1.27, 1.27];
socket_E = [2.67, 11.24];

// ---- policy (case-owned) --------------------------------------------------------------------
case_N = [-7.7, 21.9];         // nominal 29.6 thick with a 1.6 board; a 1.8 board moves the lid to -7.9
board_t_nom = 1.6;
board_t = 1.6;                 // actual board (assembly / probes only): the lid follows it
wall = 2.0;
roof_t = 1.6;
floor_t = 1.6;
board_clear = 0.3;
boss_d = 9.0;                  // 2.5 wall around a d4.0 insert hole; inside the d10.5 hole courtyard
insert_hole_d = 4.0;           // M3 x 5.7 x OD4.6 heat-set insert (CNC Kitchen / ruthex class): vendor hole D3 4.0;
                               // printed holes shrink, so set from print/1-coupons insert ladder
insert_depth = 6.7;            // insert 5.7 + 1.0 (CNC Kitchen: blind hole ~1 mm deeper than the insert)
relief_d = 3.2;
screw_clear_d = 3.4;
head_d = 6.0;                  // ISO 4762 M3 dk 5.5 + 0.5
head_depth = 3.2;              // k 3.0 + 0.2
spigot_d = 4.7;                // in the board's d5.0 hole: 0.15 radial play (JLC NPTH -0.08 dia, +-0.075 position)
spigot_bore_d = 3.2;           // ISO 273 fine clearance for M3, through the spigot only: wall 0.75
spigot_above = 0.4;            // spigot tip above the board top
spigot_recess = 1.0;           // insert seat above the board top: a proud insert has 0.6 before it meets the spigot
rim_gap = 0.4;                 // >= 0.15 left at a 1.4 board; clamp load goes through the board
win_clear = 0.1;
bed_chamfer = 0.4;             // elephant's foot relief on bed faces (socket tongue, coupons)
eps = 0.01;
facets = 48;
// form: full-height end flanges, roof perimeter chamfer
r_far = 5.3;                   // far plan corners: board R5 + board_clear, on the outline that includes the fascia
r_bus = 1.0;                   // bus-end plan corners (behind the flanges)
c_roof = 1.0;                  // 45 deg roof perimeter chamfer (a bed edge: chamfer, not a fillet)
c_part = 1.0;                  // tray wall chamfer at the parting line: with rim_gap it reads as a groove
c_lid = 0.8;                   // lid outer (bed) edge chamfer
tie_gap = 0.2;                 // boss ties stop this far above the board top: only the boss face clamps
r_ear = 1.5;                   // flange plan rounds on the outer vertical edges
r_flange = 3.0;                // flange corners at the lid end
// front: sliding panel in V-grooved corner towers; fascia to the lid face, R5.3 corners
front_inset = 11.1;            // roof opening and towers start this far in from the board's far edge: S E 68.0 clears
                               // every S courtyard that reaches |A| > 40.2 (sliding-panel data/corner_survey.txt)
open_clear = 0.3;              // opening edge = far boss face (boss_d / 2) + 0.3: A +-40.2 on S
tower_gap = 0.3;               // towers stop this far above the board top
fas_t = 2.0;                   // fascia thickness along E
pan_gap = 0.2;                 // sliding clearance per side, V tongue in groove (print/1-coupons slide coupon)

// ---- modifiers (slot frame after resolve; default none) --------------------------------------
floor_reliefs = [];   // [[E0, E1, A0, A1, depth]]  depth < 0 = through window
edge_notches = [];    // [[side, u0, u1, N0, N1]]   side "-A"/"+A": u = E; "far": u = A
roof_windows = [];    // [[E0, E1, A0, A1]]

// ---- board probe inputs (from the board's .kicad_pcb; probes only) ----------------------------
pb_outline_E = [9.1, 79.1];
pb_outline_A = [-50.0, 50.0];
pb_corner_r = 5.0;
pb_holes = [];
pb_crt_top = [];      // [E0, E1, A0, A1] (to the roof) or [E0, E1, A0, A1, z0, z1] (z above the top copper)
pb_crt_bot = [];
pb_clear = 0.2;

// ---- derived ----------------------------------------------------------------------------------
lid_dz = -(board_t - board_t_nom);
board_bot_nom = board_top_N - board_t_nom;
case_E0 = seat_E + face_gap;
bus_wall_in = board_E[0] - board_clear;
case_E1 = board_E[1] + board_clear;
fas_E1 = case_E1 + fas_t;
case_A = [board_A[0] - board_clear - wall, board_A[1] + board_clear + wall];
roof_in = case_N[1] - roof_t;
floor_in = case_N[0] + floor_t;
rim_N = floor_in + rim_gap;
spigot_top = board_top_N + spigot_above;
insert_top = board_top_N + spigot_recess;
drv_E0 = seat_E + ear_t;       // slot interface retention.driver_access starts at the ear back face
mid_E = (board_E[0] + board_E[1]) / 2;
far_holes = [for (h = holes) if (h[0] > mid_E) h];
open_E0 = board_E[1] - front_inset;
open_A = [min([for (h = far_holes) h[1]]) + boss_d / 2 + open_clear, max([for (h = far_holes) h[1]]) - boss_d / 2 - open_clear];

module box(E, A, N) translate([E[0], A[0], N[0]]) cube([E[1] - E[0], A[1] - A[0], N[1] - N[0]]);
// box with its bed face (N max if top, else N min) chamfered bed_chamfer x 45 deg on the E/A edges
module bedbox(E, A, N, top) hull() {
    c = bed_chamfer;
    box(E, A, top ? [N[0], N[1] - c] : [N[0] + c, N[1]]);
    box([E[0] + c, E[1] - c], [A[0] + c, A[1] - c], N);
}
module zcyl(e, a, n0, n1, d) translate([e, a, n0]) cylinder(d = d, h = n1 - n0, $fn = facets);
module xcyl(e0, e1, a, n, d) translate([e0, a, n]) rotate([0, 90, 0]) cylinder(d = d, h = e1 - e0, $fn = facets);
// hole along E, teardrop point toward -N (up when the tray prints roof-down)
module xtear(e0, e1, a, n, d) translate([e0, a, n]) rotate([0, 90, 0]) linear_extrude(e1 - e0)
    hull() { circle(d = d, $fn = facets); translate([d / 2 * sqrt(2) - 0.01, 0]) square(0.02, center = true); }
// 2D profile in the (A, N) plane extruded along E from e0 to e1
module along_E(e0, e1) translate([e0, 0, 0]) rotate([90, 0, 90]) linear_extrude(e1 - e0) children();

// ---- outline ----------------------------------------------------------------------------------
// plan (E, A) of the whole closed case, fascia included: one rounded rectangle, far corners r_far
module plan2d() hull() {
    for (a = [case_A[0] + r_far, case_A[1] - r_far]) translate([fas_E1 - r_far, a]) circle(r = r_far, $fn = 64);
    for (a = [case_A[0] + r_bus, case_A[1] - r_bus]) translate([case_E0 + r_bus, a]) circle(r = r_bus, $fn = 32);
}
// the plan as a prism n0..n1 with 45 deg chamfers c0 (at n0) and c1 (at n1), cut to E e0..e1
module shell(n0, n1, c0, c1, e0, e1) intersection() {
    hull() {
        translate([0, 0, n0]) linear_extrude(c0 + 0.01) offset(r = -c0) plan2d();
        translate([0, 0, n0 + c0]) linear_extrude(n1 - n0 - c0 - c1) plan2d();
        translate([0, 0, n1 - c1 - 0.01]) linear_extrude(c1 + 0.01) offset(r = -c1) plan2d();
    }
    box([e0, e1], [-500, 500], [n0 - 1, n1 + 1]);
}
// inside of the tray: the board outline + board_clear, open at the far end between the towers
module cavity2d() {
    hull() for (e = [board_E[0] + board_r, board_E[1] - board_r], a = [board_A[0] + board_r, board_A[1] - board_r])
        translate([e, a]) circle(r = board_r + board_clear, $fn = 64);
    translate([open_E0, open_A[0]]) square([fas_E1 + 5 - open_E0, open_A[1] - open_A[0]]);
    // the corner arcs are tangent to the far cut plane (case_E1): run the cavity straight out from 1.0 before it,
    // or the corner below the towers ends in a knife edge
    let(r = board_r + board_clear, de = r - 1.0, da = sqrt(r * r - de * de))
        translate([case_E1 - 1.0, board_A[0] + board_r - da]) square([fas_E1 + 5 - case_E1 + 1.0, board_A[1] - board_A[0] - 2 * board_r + 2 * da]);
}

// ---- tray -------------------------------------------------------------------------------------
// The tray's inside. Left solid in it (so no solid shares a face with the walls):
//   ties:   each bus-end boss fused to its wall corner over the hole's corner quadrant (inside the board's R5
//           corner, i.e. inside the d10.5 hole courtyard; 0 top-side courtyard hits over 35 boards,
//           form-options fleetcheck.txt), from tie_gap above the board top to the roof;
//   towers: the far corners outside the opening, around the far bosses, from tower_gap above the board top:
//           they carry the panel grooves.
module cavity3d() difference() {
    translate([0, 0, rim_N - 1]) linear_extrude(roof_in - rim_N + 1) cavity2d();
    for (h = holes) if (h[0] < mid_E)
        translate([0, 0, board_top_N + tie_gap]) linear_extrude(roof_in - board_top_N + 1) let(s = h[1] > 0 ? 1 : -1)
            translate([h[0] - 20, s > 0 ? h[1] - 0.3 : h[1] - 20]) square([20.3, 20.3]);
    translate([0, 0, board_top_N + tower_gap]) linear_extrude(roof_in - board_top_N + 1) difference() {
        translate([open_E0, -500]) square([fas_E1 + 10 - open_E0, 1000]);
        translate([open_E0 - 1, open_A[0]]) square([fas_E1 + 12 - open_E0, open_A[1] - open_A[0]]);
    }
}
// ---- panel tongue and detent, shared by the tray grooves and the panel (s = -1 / +1: the -A / +A tower) ----
pN0 = roof_in; pN1 = case_N[1]; pNm = (pN0 + pN1) / 2;
pv = roof_t / 2;                       // V tongue depth: 45 deg faces
function pA(s) = s > 0 ? open_A[1] - pan_gap : open_A[0] + pan_gap;   // panel strip edge
function apexA(s) = pA(s) + s * pv;
pan_E0 = open_E0 + pan_gap;            // panel strip -E end, closed
travel = case_E1 - pan_E0;             // the strip leaves the grooves after this pull
finger_t = 1.5; finger_L = 10.0; finger_slot = 0.8;   // detent finger in the strip, cut free by a slot
bump = 0.7;                            // bump height on the V apex: 0.42 interference out of the notch
bump_E = pan_E0 + 2.0;
module tongue2d(s) polygon([[pA(s) - s * 3, pN0], [pA(s), pN0], [apexA(s), pNm], [pA(s), pN1], [pA(s) - s * 3, pN1]]);
bump_ax = [1.0, 1.0, 0.45];            // detent bump: an ellipsoid, semi-axes E / A (inside the apex) / N; tip bump past the apex
module bump3d(s, g = 0) translate([bump_E, apexA(s) - s * bump_ax[1], pNm])
    scale([bump_ax[0] + g, bump_ax[1] + bump + g, bump_ax[2] + g]) sphere(r = 1, $fn = 64);
module groove(s) {
    // the V only (beyond the opening edge), from 0.3 ahead of the towers: a small lead-in at the mouth
    along_E(open_E0 - 0.3, case_E1 + 1) intersection() {
        offset(delta = pan_gap) tongue2d(s);
        translate([s > 0 ? open_A[1] - 0.1 : open_A[0] - 10 + 0.1, pN0 - 5]) square([10, 10]);
    }
    bump3d(s, 0.1 + pan_gap);          // detent notch: the bump sits here with 0.1 + pan_gap to spare, no preload
}

module usb_port(p) let(a0 = p[0] == "-A" ? case_A[0] - 1 : case_A[1] - wall - 1)
    translate([0, a0, 0]) rotate([-90, 0, 0]) linear_extrude(wall + 2)
        translate([p[1], -(p[3] + p[4]) / 2]) offset(r = p[5], $fn = 24) square([p[2] - 2 * p[5], p[4] - p[3] - 2 * p[5]], center = true);

// USB plug (separate part, -A ports): a cover on the outer wall face plus two snap arms through the port at its
// E edges, clear of a Nano receptacle that sits inside the port (nano-b: its face is 0.17 in from the outer face)
plug_gap = 0.15;               // arm to port edge
plug_fl = 1.2;                 // cover thickness
plug_margin = 1.5;             // cover past the port edge
arm_t = 0.7;                   // snap arm thickness along E; flexes toward the port centre
arm_h = 6.0;                   // snap arm length along N
plug_lip = 0.4;                // hook: overlaps the inner wall face by plug_lip - plug_gap
module plug_cover2d(p, o) translate([p[1], -(p[3] + p[4]) / 2]) offset(r = p[5] + plug_margin + o, $fn = 24)
    square([p[2] - 2 * p[5], p[4] - p[3] - 2 * p[5]], center = true);
module along_A(a_lo, a_hi) translate([0, a_lo, 0]) rotate([-90, 0, 0]) linear_extrude(a_hi - a_lo) children();
module usb_plug(p) let(c = p[1], n = (p[3] + p[4]) / 2, a0 = case_A[0], a1 = case_A[0] + wall) {
    hull() {                                                   // cover, bed-edge chamfer on its outer face
        along_A(a0 - plug_fl, a0 - plug_fl + bed_chamfer) plug_cover2d(p, -bed_chamfer);
        along_A(a0 - plug_fl + bed_chamfer, a0) plug_cover2d(p, 0);
    }
    for (s = [-1, 1]) let(eo = c + s * (p[2] / 2 - plug_gap), ei = eo - s * arm_t) {
        box([min(eo, ei), max(eo, ei)], [a0 - eps, a1 + 0.2 + plug_lip], [n - arm_h / 2, n + arm_h / 2]);
        translate([0, 0, n - arm_h / 2]) linear_extrude(arm_h)     // hook: square catch, 45 deg lead-in
            polygon([[eo - s * 0.1, a1 + 0.05], [eo + s * plug_lip, a1 + 0.05], [eo + s * plug_lip, a1 + 0.2], [eo - s * 0.1, a1 + 0.2 + plug_lip]]);
    }
}

// full-height end flange with the ear, in the (|A|, N) plane on the side of a; roof corner chamfered
module flange2d(a) {
    aa = abs(a); r = pad_d / 2; A1 = a > 0 ? case_A[1] : -case_A[0]; N0 = case_N[0]; N1 = case_N[1];
    hull() {
        translate([A1 + 0.2, N0]) offset(r = r_flange, $fn = 32) offset(delta = -r_flange) square([aa + r - A1 - 0.2, N1 - N0 - 4]);
        translate([A1 + 0.2, N1 - 4]) square([aa + r - A1 - 0.2, 4 - c_roof]);
        translate([A1 + 0.2, N1 - c_roof]) square([aa + r - c_roof - A1 - 0.2, c_roof]);
        translate([A1 - wall, rim_N]) square([wall + 0.2, N1 - rim_N]);
    }
}
module flange(a) mirror([0, a > 0 ? 0 : 1, 0]) intersection() {
    translate([case_E0, 0, 0]) rotate([90, 0, 90]) linear_extrude(drv_E0 - case_E0) flange2d(a);
    translate([0, 0, case_N[0] - 1]) linear_extrude(case_N[1] - case_N[0] + 2) hull() {
        translate([case_E0 - 1, 0]) square([drv_E0 - case_E0 + 1, 1]);
        for (e = [case_E0 + r_ear, drv_E0 - r_ear]) translate([e, abs(a) + pad_d / 2 - r_ear]) circle(r = r_ear, $fn = 24);
    }
}

module tray() difference() {
    union() {
        difference() {
            shell(rim_N, case_N[1], c_part, c_roof, case_E0, case_E1);
            cavity3d();
        }
        for (h = holes) zcyl(h[0], h[1], board_top_N, roof_in + eps, boss_d);
        for (a = ret_A) {
            flange(a);
            xcyl(seat_E, case_E0 + eps, a, ret_N, pad_d);
        }
    }
    box([case_E0 - 1, win_E_max], [-win_A - win_clear, win_A + win_clear], [rim_N - 1, win_N[1] + win_clear]);
    box([case_E0 - 1, case_E1 + 1], [case_A[0] - 0.2, case_A[1] + 0.2], [case_N[0] - 1, rim_N]);   // the lid's zone
    for (a = ret_A) xtear(seat_E - 1, drv_E0 + 1, a, ret_N, ear_hole_d);
    for (h = holes) {
        zcyl(h[0], h[1], board_top_N - 1, insert_top, spigot_d + 0.3);
        zcyl(h[0], h[1], insert_top - eps, insert_top + insert_depth, insert_hole_d);
        zcyl(h[0], h[1], insert_top + insert_depth - eps, insert_top + insert_depth + 4, relief_d);
    }
    box([open_E0, case_E1 + 1], open_A, [roof_in - 1, case_N[1] + 1]);   // roof opening over the terminals
    for (s = [-1, 1]) groove(s);
    for (w = roof_windows) box([w[0], w[1]], [w[2], w[3]], [roof_in - 1, case_N[1] + 1]);
    for (n = edge_notches) notch(n);
    for (p = usb_ports) usb_port(p);
}

module notch(n) {
    if (n[0] == "-A") box([n[1], n[2]], [case_A[0] - 1, case_A[0] + wall + 1], [n[3], n[4]]);
    if (n[0] == "+A") box([n[1], n[2]], [case_A[1] - wall - 1, case_A[1] + 1], [n[3], n[4]]);
    if (n[0] == "far") box([case_E1 - wall - 1, case_E1 + 1], [n[1], n[2]], [n[3], n[4]]);
}

// ---- lid --------------------------------------------------------------------------------------
module lid_nominal() difference() {
    union() {
        shell(case_N[0], floor_in, c_lid, 0, case_E0, case_E1);
        for (h = holes) {
            zcyl(h[0], h[1], case_N[0], board_bot_nom, boss_d);
            zcyl(h[0], h[1], board_bot_nom - eps, spigot_top, spigot_d);
        }
        bedbox([tongue_E_min, bus_wall_in], [-tongue_A, tongue_A], [case_N[0], board_top_N], false);
    }
    for (h = holes) {
        zcyl(h[0], h[1], case_N[0] - 1, board_bot_nom, screw_clear_d);
        zcyl(h[0], h[1], board_bot_nom - eps, spigot_top + 1, spigot_bore_d);
        zcyl(h[0], h[1], case_N[0] - 1, case_N[0] + head_depth, head_d);
    }
    for (r = floor_reliefs) box([r[0], r[1]], [r[2], r[3]], [r[4] < 0 ? case_N[0] - 1 : floor_in - r[4], floor_in + 1]);
}
module lid() translate([0, 0, lid_dz]) lid_nominal();

include <panel.scad>

// ---- board ghost and probes -------------------------------------------------------------------
module rrect2d(E, A, r) hull() for (e = [E[0] + r, E[1] - r], a = [A[0] + r, A[1] - r]) translate([e, a]) circle(r = max(r, 0.01), $fn = 48);
module board_probe() {
    difference() {
        translate([0, 0, board_top_N - board_t + 0.02]) linear_extrude(board_t - 0.04)
            offset(r = pb_clear) rrect2d(pb_outline_E, pb_outline_A, pb_corner_r);
        for (h = pb_holes) zcyl(h[0], h[1], board_top_N - board_t - 1, board_top_N + 1, h[2]);
    }
    box(socket_E, [-socket_A, socket_A], [socket_N[0] + 0.02, socket_N[1]]);
    for (c = pb_crt_top) box([c[0], c[1]], [c[2], c[3]],
        len(c) > 4 ? [board_top_N + max(c[4], 0.02), board_top_N + c[5]] : [board_top_N + 0.02, roof_in - 0.02]);
    for (c = pb_crt_bot) box([c[0], c[1]], [c[2], c[3]], [floor_in + lid_dz + 0.02, board_top_N - board_t - 0.02]);
}
module board_ghost() color("green") difference() {
    translate([0, 0, board_top_N - board_t]) linear_extrude(board_t) rrect2d(board_E, board_A, board_r);
    for (h = holes) zcyl(h[0], h[1], board_top_N - board_t - 1, board_top_N + 1, 5.0);
}
module below_seat_allowed() {
    box([tongue_E_min - 0.05, case_E0 + 1], [-tongue_A - 0.05, tongue_A + 0.05], [env_N[0] - 1, board_top_N + 0.05]);
    for (a = ret_A) xcyl(seat_E - 0.05, case_E0 + 1, a, ret_N, pad_d + 0.1);
}

// print orientation, bed face at z = 0
module tray_bed() translate([0, 0, case_N[1]]) rotate([180, 0, 0]) children();            // roof down
module lid_bed() translate([0, 0, -(case_N[0] + lid_dz)]) children();                      // outer face down
module panel_bed() translate([0, 0, case_N[1]]) rotate([180, 0, 0]) children();           // roof strip down
module plug_bed() rotate([90, 0, 0]) translate([0, -(case_A[0] - plug_fl), 0]) children(); // cover face down

if (part == "tray") tray();
if (part == "lid") lid();
if (part == "panel") panel(panel_out);
if (part == "tray_print") tray_bed() tray();
if (part == "lid_print") lid_bed() lid();
if (part == "panel_print") panel_bed() panel();
// checks place the panel stop_gap short of its stop (fascia on the tray's far face): a face contact would fuse
// the parts in a union and leave a zero-volume sheet in an intersection probe
stop_gap = 0.02;
if (part == "assembly") { tray(); lid(); panel(panel_out + stop_gap); }
if (part == "assembly_board") { tray(); lid(); panel(panel_out); board_ghost(); }
if (part == "exploded") { tray(); translate([0, 0, -6]) board_ghost(); translate([0, 0, -14]) lid(); panel(travel + 6); }
if (part == "probe_board") intersection() { union() { tray(); lid(); panel(stop_gap); } board_probe(); }
if (part == "probe_board_only") board_probe();
if (part == "probe_parts") intersection() { tray(); translate([0, 0, 0.15]) lid(); }
if (part == "probe_below_seat") intersection() {
    union() { tray(); lid(); }
    difference() { box([-20, case_E0 - 0.02], [-200, 200], [-50, 50]); below_seat_allowed(); }
}
// panel probes (spec.py): see panel.scad
if (part == "panel_swept") for (o = [0 : 2 : travel + 2]) panel(o);
if (part == "probe_panel_closed") intersection() { tray(); panel(stop_gap); }
if (part == "probe_panel_lid") intersection() { lid(); panel(stop_gap); }
if (part == "probe_panel_slide") intersection() { tray(); for (o = [stop_gap : 1 : travel + 1]) panel(o, with_bump = false); }
if (part == "probe_panel_shift") intersection() { tray();
    for (d = [[0, probe_shift, 0], [0, -probe_shift, 0], [0, 0, probe_shift], [0, 0, -probe_shift]]) translate(d) panel(stop_gap, with_bump = false); }
if (part == "probe_panel_locate") intersection() { tray(); translate(probe_dir * probe_shift) panel(stop_gap, with_bump = false); }
if (part == "probe_detent") intersection() { tray(); panel(probe_pull); box([0, 200], [0, 200], [-50, 50]); }
if (part == "probe_legend_thin") legend_thin();
if (part == "probe_legend_off_face") legend_off_face();
// USB plug probes (spec.py): seated 0.02 off the outer face, against the board; pulled 0.3, its hooks must catch
if (part == "usb_plug") for (p = usb_ports) usb_plug(p);
if (part == "probe_plug_tray") intersection() { tray(); translate([0, -0.02, 0]) for (p = usb_ports) usb_plug(p); }
if (part == "probe_plug_board") intersection() { for (p = usb_ports) usb_plug(p); board_probe(); }
if (part == "probe_plug_pulled") for (p = usb_ports) intersection() {   // only overlap reaching 0.1 past the port edge
    tray(); translate([0, -0.3, 0]) usb_plug(p);
    difference() { box([-200, 200], [-200, 200], [-50, 50]); box([p[1] - p[2] / 2 - 0.1, p[1] + p[2] / 2 + 0.1], [-200, 200], [-50, 50]); }
}
