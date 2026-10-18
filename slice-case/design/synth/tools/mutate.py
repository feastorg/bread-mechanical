"""Mutation sweep over case.scad and panel.scad: each mutation must redden its target check.

Usage: python3 -I tools/mutate.py [name filter]   (run from anywhere; restores each file after each mutation)
Runs every spec.py contract target (tools/targets.py) per mutation. Prints BROKEN when a mutation did not apply
(pattern count != 1, or the file hash unchanged after writing), otherwise every failing (part, check) for it.
Reports go to a fresh temporary directory under $TMPDIR.
"""
import glob, hashlib, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'tools', 'targets.py')], capture_output=True,
                         text=True, check=True).stdout.split()
C, P = 'case.scad', 'panel.scad'
MUTS = [
    # case: interface and fasteners
    (C, 'tongue narrower', 'bedbox([tongue_E_min, bus_wall_in], [-tongue_A, tongue_A]', 'bedbox([tongue_E_min, bus_wall_in], [-tongue_A + 2, tongue_A - 2]', 'socket-tongue'),
    (C, 'tongue into board edge', 'bedbox([tongue_E_min, bus_wall_in], [-tongue_A', 'bedbox([tongue_E_min, bus_wall_in + 0.5], [-tongue_A', 'probe-board'),
    (C, 'ear hole off axis', 'xtear(seat_E - 1, drv_E0 + 1, a, ret_N, ear_hole_d)', 'xtear(seat_E - 1, drv_E0 + 1, a, ret_N + 0.5, ear_hole_d)', 'ear-hole-wall'),
    (C, 'ear hole undersize', 'xtear(seat_E - 1, drv_E0 + 1, a, ret_N, ear_hole_d)', 'xtear(seat_E - 1, drv_E0 + 1, a, ret_N, ear_hole_d - 0.6)', 'ear-hole@'),
    (C, 'pad below seat', 'xcyl(seat_E, case_E0 + eps, a, ret_N, pad_d)', 'xcyl(seat_E - 0.2, case_E0 + eps, a, ret_N, pad_d)', 'pad-face-not-below-seat'),
    (C, 'flange into driver path', 'drv_E0 = seat_E + ear_t; ', 'drv_E0 = seat_E + ear_t + 2; ', 'driver-path'),
    (C, 'bus window short', '[rim_N - 1, win_N[1] + win_clear]);', '[rim_N - 1, win_N[1] - 1]);', 'bus-window-empty'),
    (C, 'insert pocket shallow', 'insert_top + insert_depth, insert_hole_d);', 'insert_top + insert_depth - 1, insert_hole_d);', 'insert-pocket'),
    (C, 'insert pocket oversize', 'insert_top + insert_depth, insert_hole_d);', 'insert_top + insert_depth, insert_hole_d + 0.6);', 'insert-wall'),
    (C, 'spigot too big for hole', 'board_bot_nom - eps, spigot_top, spigot_d);', 'board_bot_nom - eps, spigot_top, spigot_d + 0.6);', 'probe-board'),
    (C, 'spigot bore back to screw clearance', 'spigot_top + 1, spigot_bore_d);', 'spigot_top + 1, screw_clear_d);', 'spigot@'),
    (C, 'spigot bore undersize', 'spigot_top + 1, spigot_bore_d);', 'spigot_top + 1, spigot_bore_d - 0.4);', 'screw-clear'),
    (C, 'no head counterbore', 'case_N[0] + head_depth, head_d);', 'case_N[0] + head_depth, head_d - 1.5);', 'head-counterbore'),
    (C, 'roof too thick', 'case_N = [-7.7, 21.9];', 'case_N = [-7.7, 22.3];', 'above-envelope'),
    (C, 'no thickness margin', 'case_N = [-7.7, 21.9];', 'case_N = [-7.9, 21.9];', 'below-envelope'),
    (C, 'no rim gap', 'rim_N = floor_in + rim_gap;', 'rim_N = floor_in;', 'probe-parts'),
    (C, 'spigot meets insert', 'insert_top = board_top_N + spigot_recess;', 'insert_top = board_top_N + spigot_above;', 'probe-parts'),
    (C, 'cavity onto board', 'translate([e, a]) circle(r = board_r + board_clear, $fn = 64);', 'translate([e, a]) circle(r = board_r + 0.05, $fn = 64);', 'probe-board'),
    (C, 'lid ignores board thickness', 'lid_dz = -(board_t - board_t_nom);', 'lid_dz = 0;', 'probe-board'),
    (C, 'boss ties onto the board', 'tie_gap = 0.2;', 'tie_gap = -0.3;', 'probe-board'),
    # case: USB port
    (C, 'usb port removed', 'for (p = usb_ports) usb_port(p);', 'for (p = []) usb_port(p);', 'usb-plug'),
    (C, 'usb port 8 narrower', 'for (p = usb_ports) usb_port(p);', 'for (p = usb_ports) usb_port([p[0], p[1], p[2] - 8, p[3], p[4], p[5]]);', 'usb-plug'),
    (C, 'usb port back to a wide window', 'for (p = usb_ports) usb_port(p);', 'for (p = usb_ports) usb_port([p[0], p[1], p[2] + 8, p[3], p[4], p[5]]);', 'usb-port-side'),
    (C, 'usb port top 2 low', 'for (p = usb_ports) usb_port(p);', 'for (p = usb_ports) usb_port([p[0], p[1], p[2], p[3], p[4] - 2, p[5]]);', 'usb-plug'),
    (C, 'usb port 1.5 taller', 'for (p = usb_ports) usb_port(p);', 'for (p = usb_ports) usb_port([p[0], p[1], p[2], p[3], p[4] + 1.5, p[5]]);', 'usb-port-top'),
    # case: front towers and grooves
    (C, 'towers onto the board', 'tower_gap = 0.3;', 'tower_gap = -0.3;', 'probe-board'),
    (C, 'towers stop short of the roof', 'linear_extrude(roof_in - board_top_N + 1) difference() {', 'linear_extrude(roof_in - board_top_N - 1.5) difference() {', 'tower@'),
    (C, 'boss ties stop short of the roof', 'linear_extrude(roof_in - board_top_N + 1) let(', 'linear_extrude(roof_in - board_top_N - 3) let(', 'boss-tie@'),
    (C, 'no boss ties', 'translate([h[0] - 20, s > 0 ? h[1] - 0.3 : h[1] - 20]) square([20.3, 20.3]);', 'translate([h[0] - 20, s > 0 ? h[1] - 0.3 : h[1] - 20]) square([0.01, 0.01]);', 'boss-tie@'),
    (C, 'opening narrower (towers onto terminals)', 'open_clear = 0.3;', 'open_clear = 3.0;', 'probe-board'),
    (C, 'groove clearance 0.05', 'offset(delta = pan_gap) tongue2d(s);', 'offset(delta = 0.05) tongue2d(s);', 'probe-panel-shift'),
    (C, 'groove clearance 0.5 (loose)', 'offset(delta = pan_gap) tongue2d(s);', 'offset(delta = 0.5) tongue2d(s);', 'probe-panel-locate'),
    (C, 'groove blind at the far end', 'along_E(open_E0 - 0.3, case_E1 + 1) intersection() {', 'along_E(open_E0 - 0.3, case_E1 - 3) intersection() {', 'probe-panel-slide'),
    (C, 'detent notch too shallow (preload at rest)', 'bump3d(s, 0.1 + pan_gap);', 'bump3d(s, -0.2);', 'probe-panel-closed'),
    (C, 'bump 0.4', 'bump = 0.7;', 'bump = 0.4;', 'bump-interference'),
    # panel
    (P, 'no bump', 'if (with_bump) for (s = [-1, 1]) bump3d(s);', 'if (false) for (s = [-1, 1]) bump3d(s);', 'bump-interference'),
    (P, 'fascia below the lid face', 'shell(case_N[0], case_N[1], c_lid, c_roof, pan_E0 - 1, fas_E1);', 'shell(case_N[0] - 0.5, case_N[1], c_lid, c_roof, pan_E0 - 1, fas_E1);', 'below-envelope'),
    (P, 'fascia lugs into the driver path', '        body();\n', '        body(); box([case_E1, fas_E1], [case_A[0] - 3, case_A[1] + 3], [5, 15]);\n', 'driver-path'),
    (P, 'wire slot closed to 2.0', 'fas_N0 = 6.0;', 'fas_N0 = 2.0;', 'wire-slot'),
    (P, 'no notches', 'for (n = panel_notches) box(', 'for (n = []) box(', 'probe-board'),
    (P, 'notch 3 low', '[case_N[0] - 1, min(n[2], roof_in - 0.01)]);', '[case_N[0] - 1, min(n[2] - 3, roof_in - 0.01)]);', 'probe-board'),
    (P, 'legend not emboldened (thin strokes)', 'lg_grow = 0.2;', 'lg_grow = 0.0;', 'probe-legend-thin'),
    (P, 'pin labels 3 lower (into the wire slot)', 'lab_top = rule_N[0] - lg_gap;', 'lab_top = rule_N[0] - lg_gap - 3;', 'probe-legend-off-face'),
    (P, 'header under the pull ridge', 'hdr_base = hdr_top - 3.3;', 'hdr_base = hdr_top - 1.5;', 'probe-legend-off-face'),
    # USB plug
    (C, 'usb plug hooks too short to catch', 'plug_lip = 0.4;', 'plug_lip = 0.15;', 'both-hooks-catch'),
    (C, 'usb plug arms into the port edge', 'plug_gap = 0.15;', 'plug_gap = -0.1;', 'probe-plug-tray'),
    (C, 'usb plug arms onto the Nano receptacle', 'arm_t = 0.7;', 'arm_t = 3.0;', 'probe-plug-board'),
    (C, 'usb plug arms into the Nano module', 'a1 + 0.2 + plug_lip], [n - arm_h', 'a1 + 1.2 + plug_lip], [n - arm_h', 'probe-plug-board'),
]


def run():
    out = tempfile.mkdtemp(prefix='mut-', dir=os.environ.get('TMPDIR'))
    subprocess.run(['partspec', 'check', *TARGETS, '--quiet', '--out', out], cwd=HERE, capture_output=True, text=True)
    fails = []
    for rep in sorted(glob.glob(os.path.join(out, '*', 'report.json'))):
        d = json.load(open(rep))
        part = d['part']['id'] if isinstance(d.get('part'), dict) else os.path.basename(os.path.dirname(rep))
        for c in d['checks']:
            if c['status'] != 'pass':
                fails.append(f"{part}:{c['id']}={c['status']}")
        if d['verdict'] != 'pass' and not any(f.startswith(part + ':') for f in fails):
            fails.append(f"{part}:<verdict {d['verdict']}>")
    return fails


sha = lambda t: hashlib.sha256(t.encode()).hexdigest()
orig = {f: open(os.path.join(HERE, f)).read() for f in (C, P)}
h0 = {f: sha(t) for f, t in orig.items()}
base = run()
print(f'{len(TARGETS)} targets')
print('BASELINE', 'clean' if not base else base)
try:
    for f, name, old, new, target in [m for m in MUTS if all(w in m[1] for w in sys.argv[1:])]:
        path = os.path.join(HERE, f)
        n = orig[f].count(old)
        mutated = orig[f].replace(old, new)
        if n != 1 or sha(mutated) == h0[f]:
            print(f'BROKEN   {f}: {name}: pattern count {n}')
            continue
        open(path, 'w').write(mutated)
        if sha(open(path).read()) == h0[f]:
            print(f'BROKEN   {f}: {name}: file unchanged after write')
            continue
        fails = [x for x in run() if x not in base]
        hit = any(target in x for x in fails)
        print(f"{'KILLED  ' if hit else 'SURVIVED'} {f}: {name} (target {target}): {len(fails)} new failing -> {'; '.join(fails)}",
              flush=True)
        open(path, 'w').write(orig[f])
finally:
    for f in (C, P):
        open(os.path.join(HERE, f), 'w').write(orig[f])
        assert sha(open(os.path.join(HERE, f)).read()) == h0[f]
    print('restored', ' '.join(f'{f} {h0[f][:12]}' for f in (C, P)))
