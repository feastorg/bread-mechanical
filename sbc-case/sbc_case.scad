// SPDX-License-Identifier: GPL-3.0-or-later
//
// SBC cases for BREAD controllers (#5): SBC Case Builder's shell case, with
//   - a window in the lid roof over the GPIO header, so jumpers to the Loaf
//     plug in with the lid on (Case Builder's gpio_opening = "open" cuts the
//     side wall only), and
//   - an extrusion mount: a plate under the case that the case's own four
//     M2.5 screws pass through, held on the extrusion by two screws into
//     T-nuts. The extrusion runs along y, under the middle of the hole pattern.
//
// Case Builder and SBC Model Framework are pinned in ../scadman.toml; run with
// OPENSCADPATH=$(scadman env). Case Builder's settings come in as -D (or
// -p boards.json -P <board>); Case Builder's own view is switched off and this
// file places its parts.
//
// Frames. Model: board coordinates in x and y, case outer floor at z = 0 (Case
// Builder's). part = "lid", "bottom", "mount" and "coupon" are in print
// orientation, bed face at z = 0: the lid is turned over (y -> depth - y,
// z -> case_z - z), the mount is lifted by its thickness.

include <SBC_Case_Builder/sbc_case_builder.scad>
view = "none";

part = "lid";   // lid | bottom | mount | coupon | assembly

// ---- lid: GPIO window ----------------------------------------------------------------------
sc_pitch = 2.54;            // 0.1 in header pitch
sc_gpio_margin = 1;         // clearance around the pin field, each side
sc_standoff_ring = 0.5;     // material the window leaves around each top standoff

// ---- mount ---------------------------------------------------------------------------------
sc_plate_t = 8;
sc_head_clear = 0.5;        // diametral clearance on counterbores
// Extrusion: 20-series (2020) defaults, M5 into a drop-in T-nut.
sc_profile = 20;            // face width
sc_bolt_clear_d = 5.5;      // ISO 273 fine, M5
sc_bolt_head_d = 8.5;       // ISO 4762 M5 dk
sc_bolt_head_k = 5;         // ISO 4762 M5 k
sc_bolt_spacing = undef;    // centre to centre along the extrusion; undef: up to 30, as the plate allows
sc_key = false;             // locating key into the slot
sc_slot_w = 6;              // 20-series slot opening
sc_key_h = 1.5;
// Case screws: M2.5 socket head (ISO 4762) from under the plate into the lid's inserts.
sc_screw_len = 16;
sc_screw_clear_d = 2.7;     // ISO 273 fine, M2.5
sc_head_d = 4.5;            // ISO 4762 M2.5 dk
sc_head_k = 2.5;            // ISO 4762 M2.5 k
sc_engagement = 3.5;        // thread into the lid insert, from the standoff face

// ---- coupon: M2.5 insert pockets -----------------------------------------------------------
sc_coupon_rungs = [3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0];
sc_coupon_pitch = 14;

// ---- board data (SBC Model Framework) ------------------------------------------------------
function sc_entry(m) = sbc_data[search([m], sbc_data)[0]];
function sc_comp(e, c) = [for (i = [2 : 11 : len(e) - 1]) if (e[i] == c) [e[i + 3], e[i + 4], e[i + 8], e[i + 7]]][0];

sc_e = sc_entry(sbc_model);
sc_hdr = sc_comp(sc_e, "gpio");
sc_holes = [for (i = [2 : 11 : len(sc_e) - 1]) if (sc_e[i] == "pcbhole") [sc_e[i + 3], sc_e[i + 4]]];
assert(case_design == "shell", "sbc_case.scad places shell cases only");
assert(pcb_loc_x == 0 && pcb_loc_y == 0, "the board must sit at Case Builder's origin");
assert(len(sc_holes) == 4, str(sbc_model, ": expected 4 mounting holes, found ", len(sc_holes)));
assert(!is_undef(sc_hdr), str(sbc_model, " has no gpio entry in SBC Model Framework"));
assert(sc_hdr[3] == [0, 0, 0], str(sbc_model, ": rotated GPIO headers are not handled"));

// Header pin field, model frame.
sc_gx = [sc_hdr[0], sc_hdr[0] + sc_hdr[2][0] * sc_pitch];
sc_gy = [sc_hdr[1], sc_hdr[1] + sc_hdr[2][1] * sc_pitch];

// Case outline, model frame (Case Builder: board at the origin, side and wall plus gap around it).
sc_x = [-(sidethick + gap), width - (sidethick + gap)];
sc_y = [-(wallthick + gap), depth - (wallthick + gap)];

// Mount layout.
sc_hx = [for (h = sc_holes) h[0]];
sc_hy = [for (h = sc_holes) h[1]];
sc_ex = (min(sc_hx) + max(sc_hx)) / 2;
sc_ey = (min(sc_hy) + max(sc_hy)) / 2;
sc_spacing = is_undef(sc_bolt_spacing)
    ? min(30, (sc_y[1] - sc_y[0]) - (sc_bolt_head_d + sc_head_clear) - 2 * 2) : sc_bolt_spacing;
sc_bolts = [[sc_ex, sc_ey - sc_spacing / 2], [sc_ex, sc_ey + sc_spacing / 2]];
// Screw stack: the lid's insert starts at the top standoff face, which Case Builder puts at
// bottom_height (the board's top face as modelled). The screw's shank left in the plate is
// what remains of its length; the counterbore takes the rest of the plate.
sc_shank = sc_screw_len - (bottom_height + sc_engagement);
sc_cb = sc_plate_t - sc_shank;

if (part == "mount" || part == "assembly") {
    assert(sc_engagement <= top_standoff_insert_height, "screw reaches past the insert pocket");
    assert(sc_cb >= sc_head_k, str("M2.5x", sc_screw_len, " too long for a ", sc_plate_t, " plate: counterbore ", sc_cb));
    assert(sc_shank >= 1.5, str("M2.5x", sc_screw_len, " too short: ", sc_shank, " mm left in the plate"));
    assert(sc_plate_t - sc_bolt_head_k >= 2, "plate too thin under the T-nut screw heads");
    for (h = sc_holes) assert(abs(h[0] - sc_ex) - (sc_head_d + sc_head_clear) / 2 >= sc_profile / 2,
        str(sbc_model, ": M2.5 head at x ", h[0], " lands on the extrusion face"));
    for (b = sc_bolts) assert(b[1] - (sc_bolt_head_d + sc_head_clear) / 2 >= sc_y[0]
                              && b[1] + (sc_bolt_head_d + sc_head_clear) / 2 <= sc_y[1],
        str(sbc_model, ": bolt spacing ", sc_spacing, " puts a T-nut screw head outside the plate"));
    echo(str("mount: plate ", sc_x[1] - sc_x[0], " x ", sc_y[1] - sc_y[0], " x ", sc_plate_t,
             ", case screws M2.5x", sc_screw_len, " (counterbore ", sc_cb, ")",
             ", T-nut screws at x ", sc_ex, ", y ", sc_bolts[0][1], " / ", sc_bolts[1][1]));
}

// ---- parts, model frame --------------------------------------------------------------------
module sc_lid() {
    difference() {
        case_top(case_design);
        difference() {
            translate([sc_gx[0] - sc_gpio_margin, sc_gy[0] - sc_gpio_margin, case_z - floorthick - 1])
                cube([sc_gx[1] - sc_gx[0] + 2 * sc_gpio_margin, sc_gy[1] - sc_gy[0] + 2 * sc_gpio_margin, floorthick + 2]);
            for (h = sc_holes)
                translate([h[0], h[1], 0])
                    // Case Builder's hex pillar: top_standoff_diameter across flats, a flat facing +-x
                    // (standoff.scad: rotate 30, $fn = 6). The ring follows the hex, so on the header side it
                    // stops at the flat plus sc_standoff_ring.
                    rotate([0, 0, 30])
                        cylinder(d = (top_standoff_diameter + 2 * sc_standoff_ring) * 2 / sqrt(3), h = case_z + 1, $fn = 6);
        }
    }
}

module sc_rounded(x, y, r, h) hull()
    for (px = [x[0] + r, x[1] - r], py = [y[0] + r, y[1] - r]) translate([px, py, 0]) cylinder(r = r, h = h, $fn = 48);

module sc_mount() {
    difference() {
        union() {
            translate([0, 0, -sc_plate_t]) sc_rounded(sc_x, sc_y, corner_fillet, sc_plate_t);
            if (sc_key)
                translate([sc_ex - sc_slot_w / 2 + 0.2, sc_y[0], -sc_plate_t - sc_key_h])
                    cube([sc_slot_w - 0.4, sc_y[1] - sc_y[0], sc_key_h]);
        }
        for (h = sc_holes) {
            translate([h[0], h[1], -sc_plate_t - sc_key_h - 1])
                cylinder(d = sc_screw_clear_d, h = sc_plate_t + sc_key_h + 2, $fn = 32);
            translate([h[0], h[1], -sc_plate_t - 1]) cylinder(d = sc_head_d + sc_head_clear, h = sc_cb + 1, $fn = 32);
        }
        for (b = sc_bolts) {
            translate([b[0], b[1], -sc_plate_t - sc_key_h - 1])
                cylinder(d = sc_bolt_clear_d, h = sc_plate_t + sc_key_h + 2, $fn = 32);
            translate([b[0], b[1], -sc_bolt_head_k]) cylinder(d = sc_bolt_head_d + sc_head_clear, h = sc_bolt_head_k + 1, $fn = 48);
        }
    }
}

// Insert-pocket ladder: one hex boss per rung, the same diameter and pocket depth as the lid's
// top standoffs, standing on a base plate with the rung engraved in front of it (4.5 mm text, as
// slice-case's coupons).
// One decimal place, so 4.0 reads "4.0" (as slice-case's coupons).
function sc_fmt(v) = str(floor(v + 1e-6), ".", round((v - floor(v + 1e-6)) * 10));

module sc_coupon() {
    n = len(sc_coupon_rungs);
    boss_h = top_standoff_insert_height + 1.5;
    difference() {
        union() {
            translate([-sc_coupon_pitch / 2, -12, 0]) cube([n * sc_coupon_pitch, 17, 1.5]);
            for (i = [0 : n - 1]) translate([i * sc_coupon_pitch, 0, 0])
                cylinder(d = top_standoff_diameter / cos(30), h = boss_h, $fn = 6);
        }
        for (i = [0 : n - 1]) {
            translate([i * sc_coupon_pitch, 0, boss_h - top_standoff_insert_height])
                cylinder(d = sc_coupon_rungs[i], h = top_standoff_insert_height + 1, $fn = 48);
            translate([i * sc_coupon_pitch, -8, 1.5 - 0.6]) linear_extrude(1)
                text(sc_fmt(sc_coupon_rungs[i]), size = 4.5, font = "DejaVu Sans:style=Bold", halign = "center", valign = "center");
        }
    }
}

// ---- dispatch ------------------------------------------------------------------------------
if (part == "lid") translate([0, depth, case_z]) rotate([180, 0, 0]) sc_lid();
if (part == "bottom") case_bottom(case_design);
if (part == "mount") translate([0, 0, sc_plate_t]) sc_mount();
if (part == "coupon") sc_coupon();
if (part == "assembly") {
    color("dimgrey") sc_mount();
    color("grey") case_bottom(case_design);
    translate([pcb_loc_x, pcb_loc_y, bottom_height - pcb_z + pcb_loc_z]) sbc(sbc_model);
    color("silver", 0.6) sc_lid();
}
