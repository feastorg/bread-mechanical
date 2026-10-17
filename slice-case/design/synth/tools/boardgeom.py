"""Slice board geometry in the slot frame (E, A) of slot-interface-v1.

Usage: python3 -I boardgeom.py <BREAD_Slice.kicad_pcb> [--fps]
Prints JSON: outline bbox, smallest Edge.Cuts arc radius (corner_r), holes (d >= 2.5), bus pin row, and with --fps every
footprint's courtyard (or Fab) bbox in E/A, its layer, whether it has THT pads, and its named pads [name, E, A].

Frame: E = x_s - x_pinrow + 12.70 (pin_row_E), A = y_pinrow - y_s (pin 1 toward +A).
"""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', 'interface', 'tools'))
from loafparse_lib import parse, kids, kid, rot  # noqa: E402

PIN_ROW_E = 12.70
pcb = parse(open(sys.argv[1]).read())
xs, ys, radii = [], [], []
for g in pcb:
    if isinstance(g, list) and g and g[0] in ('gr_line', 'gr_rect', 'gr_arc'):
        L = kid(g, 'layer')
        if L and L[1] == 'Edge.Cuts':
            pts3 = []
            for k in ('start', 'mid', 'end'):
                p = kid(g, k)
                if p:
                    xs.append(float(p[1])); ys.append(float(p[2])); pts3.append((float(p[1]), float(p[2])))
            if g[0] == 'gr_arc' and len(pts3) == 3:   # circumradius of start / mid / end
                (ax, ay), (bx, by), (cx, cy) = pts3
                a, b, c = math.dist(pts3[1], pts3[2]), math.dist(pts3[0], pts3[2]), math.dist(pts3[0], pts3[1])
                area2 = abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay))
                if area2 > 1e-9:
                    radii.append(a * b * c / (2 * area2))
fps = kids(pcb, 'footprint')
xp = yp = None
for fp in fps:
    if 'PinSocket_1x10' in fp[1] and 'Horizontal' in fp[1]:
        at = kid(fp, 'at'); fr = float(at[3]) if len(at) > 3 else 0.0
        pts = [rot(float(kid(p, 'at')[1]), float(kid(p, 'at')[2]), fr) for p in kids(fp, 'pad')]
        xp = float(at[1]) + sum(p[0] for p in pts) / len(pts)
        yp = float(at[2]) + sum(p[1] for p in pts) / len(pts)


def E(x): return round(x - xp + PIN_ROW_E, 3)
def A(y): return round(yp - y, 3)


out = {"board": os.path.abspath(sys.argv[1]),
       "outline_E": [E(min(xs)), E(max(xs))], "outline_A": [A(max(ys)), A(min(ys))],
       "corner_r": round(min(radii), 3) if radii else 0.0,
       "holes": [], "fps": []}
for fp in fps:
    at = kid(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    ref = next((p[2] for p in kids(fp, 'property') if len(p) > 2 and p[1] == 'Reference'), None)
    if ref is None:
        ref = next((t[2] for t in kids(fp, 'fp_text') if t[1] == 'reference'), '?')
    tht = False
    pads = []
    for pad in kids(fp, 'pad'):
        if pad[1] and kid(pad, 'at'):
            dx, dy = rot(float(kid(pad, 'at')[1]), float(kid(pad, 'at')[2]), fr)
            pads.append([pad[1], E(fx + dx), A(fy + dy)])
        if pad[2] in ('thru_hole', 'np_thru_hole'):
            tht = tht or pad[2] == 'thru_hole'
            d = kid(pad, 'drill')
            if d and len(d) > 1 and d[1] != 'oval' and float(d[1]) >= 2.5:
                dx, dy = rot(float(kid(pad, 'at')[1]), float(kid(pad, 'at')[2]), fr)
                out["holes"].append({"E": E(fx + dx), "A": A(fy + dy), "d": float(d[1]), "ref": ref})
    layer = kid(fp, 'layer')[1]
    side = 'F' if layer == 'F.Cu' else 'B'
    pts = []
    for lay in (side + '.CrtYd', side + '.Fab'):
        for ln in (kids(fp, 'fp_line') + kids(fp, 'fp_rect') + kids(fp, 'fp_circle')
                   + kids(fp, 'fp_arc') + kids(fp, 'fp_poly')):
            if kid(ln, 'layer')[1] != lay:
                continue
            if ln[0] == 'fp_circle':
                c, e = kid(ln, 'center'), kid(ln, 'end')
                r = ((float(e[1]) - float(c[1])) ** 2 + (float(e[2]) - float(c[2])) ** 2) ** 0.5
                for ox_, oy_ in ((r, 0), (-r, 0), (0, r), (0, -r)):
                    dx, dy = rot(float(c[1]) + ox_, float(c[2]) + oy_, fr); pts.append((fx + dx, fy + dy))
                continue
            for k in ('start', 'end', 'mid', 'center'):
                p = kid(ln, k)
                if p:
                    dx, dy = rot(float(p[1]), float(p[2]), fr); pts.append((fx + dx, fy + dy))
            pl = kid(ln, 'pts')
            if pl:
                for xy in kids(pl, 'xy'):
                    dx, dy = rot(float(xy[1]), float(xy[2]), fr); pts.append((fx + dx, fy + dy))
        if pts:
            break
    if not pts:
        continue
    out["fps"].append({"ref": ref, "lib": fp[1].split(':')[-1], "side": side, "tht": tht,
                       "at": [E(fx), A(fy)], "rot": fr, "pads": pads,
                       "E": [E(min(p[0] for p in pts)), E(max(p[0] for p in pts))],
                       "A": [A(max(p[1] for p in pts)), A(min(p[1] for p in pts))]})
if '--fps' not in sys.argv:
    del out["fps"]
print(json.dumps(out, indent=1))
