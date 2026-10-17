// Front panel: the one per-slice printed part (REQUIREMENTS.md L2). Included by case.scad, so every number is
// case.scad's; the per-slice data comes in by -D from tools/resolve.py:
//   panel_notches  from the board file: an open-bottom fascia notch for each part that leaves the far face
//   panel_name / panel_headers / panel_labels  names from legends/<slice>.yaml (MOCK), A positions from the pads
// Parts: roof strip (the roof over the terminals) with a V tongue on each edge that slides in the tower grooves;
// a spring finger on each edge, cut free by a slot and printed flat, whose bump clicks into the groove notch;
// the fascia (case outline, R5.3 corners), full height at the corners and open below fas_N0 between the towers
// for the wires; a pull ridge along its top edge; the legend on its face. Slides out along +E.

panel_name = "";
panel_headers = [];   // [[A0, A1, text]]: header text centred over a rule from A0 to A1
panel_labels = [];    // [[A, text]]: vertical pin label centred on A, 3 characters or fewer
panel_notches = [];   // [[A0, A1, N_top]]: N_top 99 = full height (clamped to the roof underside)
panel_out = 0;        // panel pulled out along +E (scenes)
fas_N0 = 6.0;         // fascia lower edge between the towers: wire slot below (RLHT wire tops ~N 3.4, estimate)
brow = [1.5, 1.0];    // pull ridge along the fascia top edge: +E projection, N height
lg_font = "DejaVu Sans Condensed:style=Bold";
lg_size = 3.0;        // header and pin labels; cap height 3.24 with the grow (measured on the SVG export)
name_size = 4.0;      // slice name, on the -A corner
lg_grow = 0.2;        // every glyph grown 0.2 all round, so its thinnest stroke is >= stroke_min (spec.py)
lg_rule = 0.8;        // rule stroke
lg_gap = 0.4;
lg_relief = -0.6;     // > 0 raised, < 0 engraved, 0 = blank face
stroke_min = 0.8;     // REQUIREMENTS.md L4; spec.py passes it
probe_shift = 0.15;   // probes (spec.py)
probe_dir = [0, 1, 0];
probe_pull = 3.0;

hdr_top = case_N[1] - brow[1] - 0.3;
hdr_base = hdr_top - 3.3;
rule_N = [hdr_base - lg_gap - lg_rule, hdr_base - lg_gap];
lab_top = rule_N[0] - lg_gap;
name_A = (open_A[0] + case_A[0] + r_far) / 2;           // middle of the -A corner's flat face
name_N = (case_N[0] + c_lid + case_N[1] - c_roof) / 2;

module lg_text(t, size, h, v) offset(r = lg_grow, $fn = 16) text(t, size = size, font = lg_font, halign = h, valign = v);
// legend in the fascia face plane: x = A, y = N, seen from +E (reads left to right toward +A)
module legend2d() {
    for (h = panel_headers) {
        translate([(h[0] + h[1]) / 2, hdr_base]) lg_text(h[2], lg_size, "center", "baseline");
        translate([h[0], rule_N[0]]) square([h[1] - h[0], lg_rule]);
    }
    for (l = panel_labels) translate([l[0], lab_top]) rotate(90) lg_text(l[1], lg_size, "right", "center");
    if (panel_name != "") translate([name_A, name_N]) rotate(90) lg_text(panel_name, name_size, "center", "center");
}
module legend3d() if (lg_relief != 0)
    along_E(lg_relief > 0 ? fas_E1 - eps : fas_E1 + lg_relief, lg_relief > 0 ? fas_E1 + lg_relief : fas_E1 + 1) legend2d();
// the flat, readable part of the fascia face: inside the plan corners and chamfers, not the slot, notches or ridge
module face2d() difference() {
    translate([case_A[0] + r_far, case_N[0] + c_lid]) square([case_A[1] - case_A[0] - 2 * r_far, case_N[1] - c_roof - case_N[0] - c_lid]);
    translate([open_A[0], case_N[0] - 1]) square([open_A[1] - open_A[0], fas_N0 - case_N[0] + 1]);
    for (n = panel_notches) translate([n[0], case_N[0] - 1]) square([n[1] - n[0], min(n[2], roof_in) - case_N[0] + 1]);
    translate([open_A[0] + 2, case_N[1] - brow[1]]) square([open_A[1] - open_A[0] - 4, brow[1] + 1]);
}

// Strip, tongues and fascia are one intersection of the case outline (shell) with a mask, so every outer face,
// the roof-flush top included, comes from one operand: no coplanar seam where the strip meets the fascia.
module strip_mask2d() {   // the strip and its V tongues, open upward: the top face is the shell's
    translate([pA(-1) + 1, pN0]) square([pA(1) - pA(-1) - 2, pN1 - pN0 + 0.7]);
    // the upper flank runs on past the top, so the shell's top face crosses it rather than meeting a vertex
    for (s = [-1, 1]) polygon([[pA(s) - s * 3, pN0], [pA(s), pN0], [apexA(s), pNm], [pA(s) - s * 0.7, pN1 + 0.7], [pA(s) - s * 3, pN1 + 0.7]]);
}
module body() intersection() {
    shell(case_N[0], case_N[1], c_lid, c_roof, pan_E0 - 1, fas_E1);
    union() {
        along_E(pan_E0, case_E1 + 0.5) strip_mask2d();
        difference() {
            box([case_E1, fas_E1 + 1], [-500, 500], [case_N[0] - 1, case_N[1] + 1]);
            box([case_E1 - 1, fas_E1 + 2], open_A, [case_N[0] - 2, fas_N0]);   // wire slot, open at the bottom
        }
    }
}
module panel(out = 0, with_bump = true) translate([out, 0, 0]) difference() {
    union() {
        body();
        if (with_bump) for (s = [-1, 1]) bump3d(s);
        box([fas_E1 - eps, fas_E1 + brow[0]], [open_A[0] + 2, open_A[1] - 2], [case_N[1] - brow[1], case_N[1]]);
        if (lg_relief > 0) legend3d();
    }
    for (s = [-1, 1]) let(f0 = pA(s) - s * finger_t, f1 = f0 - s * finger_slot)
        hull() {                       // round end at the finger root
            box([pan_E0 - 1, pan_E0 + finger_L - finger_slot / 2], [min(f0, f1), max(f0, f1)], [pN0 - 1, pN1 + 1]);
            zcyl(pan_E0 + finger_L - finger_slot / 2, (f0 + f1) / 2, pN0 - 1, pN1 + 1, finger_slot);
        }
    // full height stops 0.01 under the strip, so the cut never shares the strip's underside
    for (n = panel_notches) box([case_E1 - 1, fas_E1 + brow[0] + 1], [n[0], n[1]], [case_N[0] - 1, min(n[2], roof_in - 0.01)]);
    if (lg_relief < 0) legend3d();
}

// ---- legend probes (spec.py): each must be empty -----------------------------------------------------
// strokes thinner than stroke_min: what an opening of radius stroke_min / 2 removes, less the corner slivers any
// opening shaves off (eroded 0.2). Finds strokes from 0.4 to stroke_min wide.
module legend_thin() linear_extrude(1) offset(r = -0.2, $fn = 24) difference() {
    legend2d();
    offset(r = stroke_min / 2 - 0.005, $fn = 24) offset(r = -(stroke_min / 2 - 0.005), $fn = 24) legend2d();
}
// legend outside the readable face, with 0.3 margin
module legend_off_face() difference() {
    along_E(fas_E1 - 0.5, fas_E1 + 1) legend2d();
    along_E(fas_E1 - 1, fas_E1 + 2) offset(delta = -0.3) face2d();
}
