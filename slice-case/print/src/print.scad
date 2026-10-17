// Print-orientation wrapper around design/synth/case.scad. All case and panel parameters come in via -D (from
// resolved/<slice>.json, as spec.py passes them); this file only selects a part in its print orientation
// (case.scad tray_bed / lid_bed / panel_bed, bed face at z = 0; the panel prints roof strip down). No feature is re-modelled here.
include <../../design/synth/case.scad>

part = "none";            // keep case.scad's own dispatch silent
print_part = "none";

if (print_part == "tray_print") tray_bed() tray();
if (print_part == "lid_print") lid_bed() lid();
if (print_part == "panel_print") panel_bed() panel();
if (print_part == "usb_plug_print") plug_bed() usb_plug(usb_ports[0]);
