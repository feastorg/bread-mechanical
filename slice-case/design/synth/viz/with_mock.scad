// Visual-only composite: this case on slot `slot_k` of the interface designer's mock backplane.
// Not a deliverable; the case never includes backplane code.
include <../case.scad>
use <../../interface/mock/slot_mock.scad>
slot_k = 1;
viz_pitch = 30.4;
// slot frame (E, A, N) -> mock frame (u = k*pitch - N, A, E)
multmatrix([[0, 0, -1, slot_k * viz_pitch], [0, 1, 0, 0], [1, 0, 0, 0]]) { tray(); lid(); board_ghost(); }
backplane();
loaf();
