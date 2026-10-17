"""Thin-feature check on PrusaSlicer text gcode.

Usage: python3 -I gcheck.py <stl> <gcode> <feature-spec.json-string>
Places the STL frame onto the bed by matching xy bbox centres (gcode extrusions vs STL vertices),
then for each feature reports, at the layers inside its z range, the extrusion paths whose segment
midpoints fall inside its region: path count by ;TYPE, and segment widths from E per mm.
Width model (PrusaSlicer flow): area = (w - h) * h + pi * h^2 / 4; E = area * L / filament_area.
"""
import json, math, re, sys

stl, gcode, spec = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
import struct
xs, ys = [], []
raw = open(stl, 'rb').read()
n = struct.unpack_from('<I', raw, 80)[0]
if len(raw) == 84 + 50 * n:
    for i in range(n):
        v = struct.unpack_from('<12f', raw, 84 + 50 * i)
        xs += [v[3], v[6], v[9]]; ys += [v[4], v[7], v[10]]
else:
    for line in raw.decode().splitlines():
        t = line.split()
        if t and t[0] == 'vertex':
            xs.append(float(t[1])); ys.append(float(t[2]))
scx, scy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

FA = math.pi * (1.75 / 2) ** 2
segs = []          # (z, h, type, path_id, x0, y0, x1, y1, w)
x = y = 0.0; z = h = 0.0; typ = None; path = 0; extruding = False
num = re.compile(r'([XYZEFIJ])(-?[\d.]+)')


def pieces(x, y, d, arc):
    """Yield (x0, y0, x1, y1) chords for a G1 line or a G2 (cw) / G3 (ccw) arc."""
    nx, ny = d.get('X', x), d.get('Y', y)
    if not arc:
        yield x, y, nx, ny; return
    cx, cy = x + d.get('I', 0.0), y + d.get('J', 0.0)
    r = math.hypot(x - cx, y - cy)
    a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
    sweep = a1 - a0
    if arc == 2 and sweep >= 0: sweep -= 2 * math.pi
    if arc == 3 and sweep <= 0: sweep += 2 * math.pi
    k = max(2, int(abs(sweep) * r / 0.2) + 1)
    px, py = x, y
    for i in range(1, k + 1):
        a = a0 + sweep * i / k
        qx, qy = (cx + r * math.cos(a), cy + r * math.sin(a)) if i < k else (nx, ny)
        yield px, py, qx, qy
        px, py = qx, qy


for line in open(gcode):
    if line.startswith(';Z:'): z = float(line[3:]); continue
    if line.startswith(';HEIGHT:'): h = float(line[8:]); continue
    if line.startswith(';TYPE:'): typ = line[6:].strip(); path += 1; continue
    arc = 2 if line.startswith('G2 ') else 3 if line.startswith('G3 ') else 0
    if not (arc or line.startswith('G1 ') or line.startswith('G0 ')):
        continue
    code = line.split(';')[0]
    d = dict((k, float(v)) for k, v in num.findall(code))
    nx, ny = d.get('X', x), d.get('Y', y)
    e = d.get('E', 0.0)
    if e > 0 and ('X' in d or 'Y' in d) and typ not in (None, 'Custom', 'Skirt/Brim'):
        if not extruding:
            path += 1
        ch = list(pieces(x, y, d, arc))
        Ltot = sum(math.hypot(c[2] - c[0], c[3] - c[1]) for c in ch)
        if Ltot > 1e-4 and h > 0:
            area = e * FA / Ltot
            w = (area - math.pi * h * h / 4) / h + h
            for c in ch:
                segs.append((z, h, typ, path, *c, w))
        extruding = True
    else:
        if 'X' in d or 'Y' in d:
            extruding = False
    x, y = nx, ny

gx = [s[4] for s in segs] + [s[6] for s in segs]
gy = [s[5] for s in segs] + [s[7] for s in segs]
ox, oy = (min(gx) + max(gx)) / 2 - scx, (min(gy) + max(gy)) / 2 - scy
print(f'offset bed-STL x {ox:.3f} y {oy:.3f}; extrusion bbox {max(gx)-min(gx):.2f} x {max(gy)-min(gy):.2f}; STL bbox {max(xs)-min(xs):.2f} x {max(ys)-min(ys):.2f}')


def inside(f, px, py):
    if f['shape'] == 'ring':
        r = math.hypot(px - f['c'][0], py - f['c'][1])
        return f['r'][0] <= r <= f['r'][1]
    return f['x'][0] <= px <= f['x'][1] and f['y'][0] <= py <= f['y'][1]


for f in spec:
    zs = sorted({s[0] for s in segs if f['z'][0] < s[0] <= f['z'][1]})
    rows = []
    for zz in zs:
        hit = [s for s in segs if s[0] == zz and inside(f, (s[4] + s[6]) / 2 - ox, (s[5] + s[7]) / 2 - oy)]
        by = {}
        for s in hit:
            by.setdefault(s[2], set()).add(s[3])
        ws = [s[8] for s in hit if 'erimeter' in s[2]]
        L = sum(math.hypot(s[6] - s[4], s[7] - s[5]) for s in hit)
        rows.append((zz, {k: len(v) for k, v in sorted(by.items())}, (min(ws), max(ws)) if ws else None, L))
    if f.get('all'):
        filled = [r[0] for r in rows if r[1]]
        print(f"-- {f['name']}: centreline first filled at z {min(filled) if filled else None}; open layers {[r[0] for r in rows if not r[1]]}")
        continue
    pc = [sum(v for k, v in r[1].items() if 'erimeter' in k) for r in rows]
    allw = [w for r in rows if r[2] for w in r[2]]
    Ls = [r[3] for r in rows]
    print(f"-- {f['name']}: {len(zs)} layers; perimeter paths/layer {min(pc)}-{max(pc)}; "
          f"perimeter w {min(allw):.2f}-{max(allw):.2f}; extruded/layer {min(Ls):.1f}-{max(Ls):.1f} mm; "
          f"empty layers {[r[0] for r in rows if not r[1]] or 'none'}" if allw else
          f"-- {f['name']}: {len(zs)} layers; NO PERIMETER; empty layers {[r[0] for r in rows if not r[1]]}")
    continue
    pick = rows if f.get('all') else [r for i, r in enumerate(rows) if i in (0, len(rows) // 2, len(rows) - 1)]
    for zz, by, ws, L in pick:
        wtxt = f'perimeter w {ws[0]:.2f}-{ws[1]:.2f}' if ws else 'no perimeter'
        print(f'   z {zz:6.2f}: paths {by}  {wtxt}  extruded length {L:.1f} mm')
    empty = [r[0] for r in rows if not r[1]]
    print(f'   layers with no extrusion in region: {empty if empty else "none"}')
