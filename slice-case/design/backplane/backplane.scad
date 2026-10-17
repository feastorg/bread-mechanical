// Backplane part for Loaf_x004 (gen1 5b8b9b9 and r3), per slot-interface-v1.1.
// World: X = u (loaf KiCad x from the slot-1 bus origin), Y = A (pin 1 +), Z = E (away from the loaf top).
// A slot's N maps to u = k * pitch - N.
//
// A plate that sits on the loaf top, screwed to it by M3x6 from the loaf underside into heat-set inserts in
// 8 bosses at the d3.3 bus-footprint holes. Per slot: the U guide around the slice socket, and the towers
// T1/T2/T3 with an insert each for the case ear screws. Rails and ribs outside the loaf tie the towers.
// Prints on its E = 0 face, no supports. Stand: loose feet (stand_foot) peg into the 4 holes under the rails.
//
// Driven by -D from slot-interface-v1.1.json (spec.py); defaults below are the same values.

part = "backplane";

// ---- interface v1.1 (-D) ---------------------------------------------------------------------
pitch = 30.4;
slots = 4;
tower_top_E = 6.7;            // seat.seat_E. Names differ from case.scad: clash.scad -D reaches used files
tower_N = 11.5;                // retention.point_N
towers = [-56.4, 56.4, 101.4];
tower_d = 10.0;                // footprint_d_max
fin_N = [1.42, 5.42];
ret_inner_A = 12.9;
ret_A1 = 14.9;
ret_N0 = -1.0;
guide_E = 15.0;
lead_in = 1.5;
pcb_hole_A = 20.0;
outline_u = [-22.614, 102.3];  // union of gen1 and r3
outline_A = [-25.0, 25.02];
tails = [[-13.45, -11.75, -12.29, 12.27], [94.05, 95.75, -12.29, 12.27], [9.35, 21.85, -21.43, -10.68]];
                               // loaf_top_keepouts THT tails [u0, u1, A0, A1], E_max 3.3
hdr_A = 13.0;                  // bus header plastic, A +-13.0, u slot +-1.4, E_max 2.54

// ---- policy ------------------------------------------------------------------------------------
plate_t = 4.0;                 // under the case tongue (E_min 4.67)
rail_t = 6.0;                  // backplane faces stay <= seat_E - 0.3 = 6.4 (interface seat.backplane_faces)
boss_t = 6.4;
boss_d = 8.0;
insert_hole_d = 4.0;           // M3 x 5.7 heat-set; set from print/1-coupons insert ladder
insert_depth = 6.5;            // tower pocket from the top (interface: >= 6.5)
relief_d = 3.2;
rib_w = 8.0;
tail_clear = 0.5;
hdr_N0 = -1.77;                // header window on -N: socket body -1.27 less 0.5
foot_hole_d = 4.0;             // stand interface holes (future inserts), from the E = 0 face
foot_hole_h = 4.0;
foot_u = [3.7, 64.5];          // between towers; -A pair clear of the barrel-jack plug path u 9.6..21.6
foot_A = [towers[0], towers[2]];
foot = [10, 20, 14];           // u, A, height: loaf underside parts reach E -10.6
peg_d = 3.6;
peg_h = 3.0;
eps = 0.01;
facets = 48;

tower_u = [for (k = [0 : slots - 1]) k * pitch - tower_N];
rail_u = [tower_u[0] - tower_d / 2, tower_u[slots - 1] + tower_d / 2];

module box(U, A, E) translate([U[0], A[0], E[0]]) cube([U[1] - U[0], A[1] - A[0], E[1] - E[0]]);
module zcyl(u, a, e0, e1, d) translate([u, a, e0]) cylinder(d = d, h = e1 - e0, $fn = facets);

module guide(k) {
    s = k * pitch;
    difference() {
        union() {
            box([s - fin_N[1], s - fin_N[0]], [-ret_A1, ret_A1], [0, guide_E]);                       // fin
            for (m = [0, 1]) mirror([0, m, 0])
                box([s - fin_N[1], s - ret_N0], [ret_inner_A, ret_A1], [0, guide_E]);                // returns
        }
        // 45 deg lead-in on the top inner edges
        translate([s - fin_N[0], 0, guide_E]) rotate([0, 45, 0]) cube([lead_in * sqrt(2), 2 * ret_inner_A, lead_in * sqrt(2)], center = true);
        for (m = [0, 1]) mirror([0, m, 0])
            translate([s + (ret_N0 - fin_N[0]) / 2 - ret_N0, ret_inner_A, guide_E]) rotate([45, 0, 0])
                cube([fin_N[0] - ret_N0 + 2, lead_in * sqrt(2), lead_in * sqrt(2)], center = true);
    }
}

module backplane() difference() {
    union() {
        box(outline_u, outline_A, [0, plate_t]);
        for (a = towers) box(rail_u, [a - tower_d / 2, a + tower_d / 2], [0, rail_t]);
        for (u = tower_u) box([u - rib_w / 2, u + rib_w / 2], [towers[0], max(towers)], [0, rail_t]);
        for (k = [0 : slots - 1]) {
            guide(k);
            for (a = [-pcb_hole_A, pcb_hole_A]) zcyl(k * pitch, a, 0, boss_t, boss_d);
            for (a = towers) zcyl(tower_u[k], a, 0, tower_top_E, tower_d);
        }
    }
    for (k = [0 : slots - 1]) {
        box([k * pitch - fin_N[0], k * pitch - hdr_N0], [-ret_inner_A, ret_inner_A], [-1, plate_t + 1]);  // header
        for (a = [-pcb_hole_A, pcb_hole_A]) zcyl(k * pitch, a, -1, boss_t + 1, insert_hole_d);
        for (a = towers) {
            zcyl(tower_u[k], a, tower_top_E - insert_depth, tower_top_E + 1, insert_hole_d);
            zcyl(tower_u[k], a, -1, tower_top_E, relief_d);
        }
    }
    for (t = tails) box([t[0] - tail_clear, t[1] + tail_clear], [t[2] - tail_clear, t[3] + tail_clear], [-1, rail_t + 1]);
    for (u = foot_u, a = foot_A) zcyl(u, a, -1, foot_hole_h, foot_hole_d);
}

module stand_foot() {
    translate([-foot[0] / 2, -foot[1] / 2, 0]) cube(foot);
    zcyl(0, 0, foot[2] - eps, foot[2] + peg_h, peg_d);
}

// loaf top keepouts (probe): THT tails to E 3.3 and the bus header plastic
module loaf_keepouts() {
    for (t = tails) box([t[0], t[1]], [t[2], t[3]], [0, 3.3]);
    for (k = [0 : slots - 1]) box([k * pitch - 1.4, k * pitch + 1.4], [-hdr_A + 0.1, hdr_A - 0.1], [0, 2.54]);
}
// where the backplane may rise above seat_E - 0.3: the towers and the guides
module above_allowed() {
    for (k = [0 : slots - 1]) {
        for (a = towers) zcyl(tower_u[k], a, 0, tower_top_E + 0.05, tower_d + 0.1);
        box([k * pitch - fin_N[1] - 0.05, k * pitch - ret_N0 + 0.05], [-ret_A1 - 0.05, ret_A1 + 0.05], [0, guide_E + 0.05]);
    }
}

if (part == "backplane") backplane();
if (part == "stand_foot") stand_foot();
if (part == "probe_loaf") intersection() { backplane(); loaf_keepouts(); }
if (part == "probe_above") intersection() {
    backplane();
    difference() { box([-100, 200], [-100, 200], [tower_top_E - 0.3 + 0.02, 50]); above_allowed(); }
}
