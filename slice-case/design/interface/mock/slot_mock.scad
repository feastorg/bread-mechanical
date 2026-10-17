// Visual mock of slot-interface-v1 (numbers copied from slot-interface-v1.json).
// World: X = u (loaf KiCad x from slot 1 bus), Y = A, Z = E. N = -(X - u_k).
pitch = 30.4; env = [-7.9, 22.1]; seatE = 6.70;
show = "all"; // all | backplane | cases
rev = "r3";   // r3 | gen1 (loaf outline only)
outline_u = rev == "r3" ? [-22.614, 98.6] : [-18.9, 102.3];

function nx(k, n) = k * pitch - n;            // world X of slot k at normal N=n
module nbox(k, N, A, E) {                      // box from N/A/E ranges in slot k
    translate([nx(k, N[1]), A[0], E[0]]) cube([N[1] - N[0], A[1] - A[0], E[1] - E[0]]);
}

module loaf() color("green") translate([outline_u[0], -24.98, -1.6]) cube([outline_u[1] - outline_u[0], 50.0, 1.6]);

module backplane() color("orange") {
    for (k = [0:3]) {
        nbox(k, [1.42, 5.42], [-14.9, 14.9], [0, 15]);                 // fin
        for (s = [-1, 1]) nbox(k, [-1.0, 5.42], s > 0 ? [12.9, 14.9] : [-14.9, -12.9], [0, 15]); // returns
        for (a = [-20, 20]) translate([k * pitch, a, 0]) cylinder(d = 8, h = 6.4, $fn = 32);       // PCB bosses
        for (a = [-56.4, 56.4, 101.4]) translate([nx(k, 11.5), a, -0]) difference() {             // towers
            cylinder(d = 10, h = seatE, $fn = 40);
            translate([0, 0, seatE - 6.5]) cylinder(d = 4.0, h = 7, $fn = 24);
        }
    }
    // rails outside the loaf in A, tying the towers (E 0..4)
    for (a = [[-61.4, -25.5], [25.5, 106.4]]) translate([-16.5, a[0], 0]) cube([91.2 + 16.5 - 6.5 + 10, a[1] - a[0], 4]);
}

module case_env(k, f) {   // simplified case envelope: body + ears, socket nose omitted
    alo = -52.4; ahi = f == "L" ? 97.4 : 52.4; far = f == "L" ? 100 : 70;
    color(f == "L" ? "steelblue" : "lightblue", 0.6) difference() {
        nbox(k, env, [alo, ahi], [seatE + 0.3, 9.10 - 3.6 + far + 3.6 + 2.4]);
        nbox(k, [-1.1, 5.92], [-15.4, 15.4], [0, 15.5]);   // bus window
    }
    color("red") for (a = [-56.4, f == "L" ? 101.4 : 56.4]) difference() {
        hull() { translate([nx(k, 11.5), a, seatE]) cylinder(d = 9, h = 5, $fn = 32);
                 translate([nx(k, 11.5) - 4.5, a > 0 ? ahi - 1 : alo, seatE]) cube([9, 1, 5]); }
        translate([nx(k, 11.5), a, 0]) cylinder(d = 3.4, h = 20, $fn = 24);
    }
}

if (show != "cases") { loaf(); backplane(); }
if (show != "backplane") { case_env(1, "S"); case_env(2, "L"); }
