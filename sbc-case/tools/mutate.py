# SPDX-License-Identifier: GPL-3.0-or-later
"""Mutation sweep over sbc_case.scad and boards.json: each mutation must redden its target check.
Usage: python3 -I tools/mutate.py [name filter]   (run from anywhere; restores each file after each mutation)
Runs every spec.py target per mutation. Prints BROKEN when a mutation did not apply (pattern count != 1, or the
file hash unchanged after writing), otherwise every (part, check) newly failing for it.
Reports go to a fresh temporary directory under $TMPDIR.
"""
import ast
import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = open(os.path.join(HERE, 'spec.py')).read()
NAMES = ast.literal_eval(SPEC.split("for n in ", 1)[1].split("]", 1)[0].strip().rstrip(')') + ')')
TARGETS = [f'spec.py:{n}' for n in NAMES]
S, B = 'sbc_case.scad', 'boards.json'
MUTS = [
    # lid
    (S, 'gpio window gone', 'cube([sc_gx[1] - sc_gx[0] + 2 * sc_gpio_margin,', 'cube([0.01,', 'gpio-window'),
    (S, 'window cuts the standoffs', 'sc_standoff_ring = 0.5;', 'sc_standoff_ring = -1.5;', 'standoff-wall'),
    (S, 'round keep-out over the pin field', 'rotate([0, 0, 30])\n                        cylinder(d = (top_standoff_diameter + 2 * sc_standoff_ring) * 2 / sqrt(3), h = case_z + 1, $fn = 6);',
     'cylinder(d = top_standoff_diameter * 2 / sqrt(3) + 2 * sc_standoff_ring, h = case_z + 1, $fn = 64);', 'gpio-window'),
    (B, 'insert pocket shorter than the insert', '"top_standoff_insert_height": "4.5",\n            "bottom_standoff_size": "m2.5+"\n        },\n        "rpi3a+"',
     '"top_standoff_insert_height": "3.5",\n            "bottom_standoff_size": "m2.5+"\n        },\n        "rpi3a+"', 'insert-pocket'),
    (B, 'hex roof pattern back on the Zero', '"top_cover_pattern": "solid"', '"top_cover_pattern": "hex_5mm"',
     'header-wall'),
    # bottom
    (B, 'bottom hole size-for-size', '"bottom_standoff_size": "m2.5+"\n        },\n        "rpi3a+"',
     '"bottom_standoff_size": "m2.5"\n        },\n        "rpi3a+"', 'screw-path'),
    # mount
    (S, 'head counterbore shallow', 'cylinder(d = sc_head_d + sc_head_clear, h = sc_cb + 1, $fn = 32);',
     'cylinder(d = sc_head_d + sc_head_clear, h = sc_cb, $fn = 32);', 'head-pocket'),
    (S, 'head counterbore deep (screw too short)', 'sc_cb = sc_plate_t - sc_shank;', 'sc_cb = sc_plate_t - sc_shank + 1;', 'head-seat'),
    (S, 'case screw hole undersize', 'cylinder(d = sc_screw_clear_d, h = sc_plate_t + sc_key_h + 2, $fn = 32);',
     'cylinder(d = 2.0, h = sc_plate_t + sc_key_h + 2, $fn = 32);', 'screw@'),
    (S, 'T-nut screw hole undersize', 'cylinder(d = sc_bolt_clear_d, h = sc_plate_t + sc_key_h + 2, $fn = 32);',
     'cylinder(d = 3, h = sc_plate_t + sc_key_h + 2, $fn = 32);', 'bolt-'),
    (S, 'T-nut screw head recess shallow', 'translate([b[0], b[1], -sc_bolt_head_k]) cylinder',
     'translate([b[0], b[1], -sc_bolt_head_k + 1]) cylinder', 'bolt-head'),
    (S, 'head pocket onto the extrusion face', 'cylinder(d = sc_head_d + sc_head_clear, h = sc_cb + 1, $fn = 32);',
     'cylinder(d = 60, h = sc_cb + 1, $fn = 32);', 'extrusion-face'),
    # coupon
    (S, 'coupon pockets shallow', 'translate([i * sc_coupon_pitch, 0, boss_h - top_standoff_insert_height])',
     'translate([i * sc_coupon_pitch, 0, boss_h - 2])', 'pocket-'),
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
orig = {f: open(os.path.join(HERE, f)).read() for f in (S, B)}
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
    for f in (S, B):
        open(os.path.join(HERE, f), 'w').write(orig[f])
        assert sha(open(os.path.join(HERE, f)).read()) == h0[f]
    print('restored', ' '.join(f'{f} {h0[f][:12]}' for f in (S, B)))
