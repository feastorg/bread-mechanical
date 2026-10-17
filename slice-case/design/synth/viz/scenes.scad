// Visual-only scenes for renders (tools/render.sh). Not a deliverable.
include <../case.scad>
scene = "closed";       // closed | open | packed | front | flange | usb | panel_print | tray_print | lid_print | section
pitch = 30.4;           // slot pitch: packed neighbours
cut_A = 0;              // section scene: keep A >= cut_A
part = "none";

module one(out = 0, with_board = true) {
    color("#c9ced6") tray();
    color("#8f99a8") lid();
    color("#e8833a") panel(out);
    if (with_board) board_ghost();
}
if (scene == "closed") one();
if (scene == "open") one(travel + 8);
if (scene == "packed") { one(travel + 8); for (s = [-1, 1]) translate([0, 0, s * pitch]) one(); }
if (scene == "front") one();
if (scene == "flange") one();
if (scene == "usb") one();
if (scene == "panel_print") color("#e8833a") panel_bed() panel();
if (scene == "tray_print") color("#c9ced6") tray_bed() tray();
if (scene == "lid_print") color("#8f99a8") lid_bed() lid();
if (scene == "section") intersection() { one(); box([-100, 300], [cut_A, 300], [-300, 300]); }
if (scene == "detent") intersection() {    // plan section through the bump centre, from +N: finger, slot end, bump, notch
    union() { color("#c9ced6") tray(); color("#e8833a") panel(panel_out); }
    box([pan_E0 - 2, pan_E0 + finger_L + 3], [open_A[1] - 6, open_A[1] + 3], [-20, pNm]);
}
if (scene == "bump") color("#e8833a") intersection() { panel(panel_out); box([pan_E0 - 1, pan_E0 + finger_L + 3], [open_A[1] - 6, open_A[1] + 3], [pN0 - 1, pN1 + 1]); }
cut_N = 10;
if (scene == "plan_cut") intersection() { color("#c9ced6") tray(); box([-100, 300], [-300, 300], [-300, cut_N]); }   // seen from -N
