"""Write the feature specs for gcheck.py, one JSON per coupon, from the rung tables in coupons.scad."""
import json, math, sys

out = sys.argv[1]
ins = [3.8, 3.9, 4.0, 4.1, 4.2, 4.3]
spg = [[4.6, 3.2], [4.7, 3.2], [4.8, 3.2], [4.9, 3.2], [4.7, 3.3], [4.7, 3.4]]
ear = [3.4, 3.6, 3.8, 4.0]
LZ = (1.0, 1.75)          # label groove layers: plate top 1.6, groove 0.6 deep
ring = lambda n, c, r0, r1, z, **k: dict(name=n, shape='ring', c=c, r=[r0, r1], z=z, **k)
rect = lambda n, cx, cy, hx, hy, z, **k: dict(name=n, shape='rect', x=[cx - hx, cx + hx], y=[cy - hy, cy + hy], z=z, **k)
S = {
    'insert_ladder': [ring(f'boss wall d{d}', [13 * i, 0], d / 2 - 0.05, 4.55, [3.1, 9.8]) for i, d in enumerate(ins)]
    + [rect(f'label {d}', 13 * i, -8.5, 4.6, 2.5, LZ) for i, d in enumerate(ins)],
    'spigot_ladder': [ring(f'spigot {o}/{b} wall {(o - b) / 2:.2f}', [13 * i, 0], b / 2 - 0.05, o / 2 + 0.05, [4.83, 6.83]) for i, (o, b) in enumerate(spg)]
    + [rect(f'label {o}', 13 * i, -8.0, 4.6, 2.5, LZ) for i, (o, b) in enumerate(spg)]
    + [rect(f'label {b}', 13 * i, -13.5, 3.8, 2.0, LZ) for i, (o, b) in enumerate(spg)],
    'hole_plate': [ring(f'hole {i + 1}', [13 * i, 0], 2.45, 3.3, [0, 1.6]) for i in range(6)]
    + [rect(f'label {i + 1}', 13 * i, -8.0, 2.5, 2.5, LZ) for i in range(6)],
    # material on the hole centreline inside the pad: the first layer with extrusion there is where the hole closes
    'ear_ladder': [rect(f'teardrop d{d} (tip z {10.4 + d / 2 * math.sqrt(2):.2f}, round top z {10.4 + d / 2:.2f})', 9.35, -11 * i, 2.15, 0.25, [10.4, 15.0], all=True) for i, d in enumerate(ear)]
    + [rect(f'label {d}', 18.35, -11 * i, 4.6, 2.5, LZ) for i, d in enumerate(ear)],
    'stack_lid': [ring('spigot 4.7/3.2 wall 0.75', [74.1, -45.0], 1.55, 2.40, [4.83, 6.83]), rect('label V2', 68.3, -39.0, 3.6, 2.2, LZ)],
    'stack_tray': [ring('boss wall around d4.0 pocket', [74.1, 45.0], 1.95, 4.55, [15.5, 22.1]), rect('label V2', 68.3, 39.0, 3.6, 2.2, LZ)],
}
for k, v in S.items():
    json.dump(v, open(f'{out}/{k}.json', 'w'))
