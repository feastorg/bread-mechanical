// Check only: a cased slice (tray, lid, panel, board and bus socket) in every slot, intersected with the
// backplane part. The case takes its -D parameters from resolved/<slice>.json (spec.py); the backplane uses
// its file defaults, which spec.py checks against slot-interface-v1.1.json.
include <../synth/case.scad>
use <backplane.scad>
seat_gap = 0.02;               // ear pads sit on the tower tops at seat_E: lift the case off the contact
for (k = [0 : 3]) intersection() {
    backplane();
    // slot frame (E, A, N) -> backplane frame (u = k * pitch - N, A, E)
    multmatrix([[0, 0, -1, k * 30.4], [0, 1, 0, 0], [1, 0, 0, seat_gap]]) {
        tray(); lid(); panel(stop_gap); board_ghost();
        box(socket_E, [-socket_A, socket_A], socket_N);
    }
}
