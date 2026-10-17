// Visual only: the backplane with a cased slice in every slot (case params by -D, as clash.scad).
include <../synth/case.scad>
use <backplane.scad>
backplane();
for (k = [0 : 3]) multmatrix([[0, 0, -1, k * 30.4], [0, 1, 0, 0], [1, 0, 0, 0]]) { tray(); lid(); panel(stop_gap); }
