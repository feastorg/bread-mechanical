"""Per-footprint courtyard (or Fab) bbox on a Loaf PCB, relative to slot 1 bus origin.
Frame: u = x - x_slot1 (KiCad x), a = y_slot - y (so +a = toward bus pin 1).
Usage: git show <rev>:hardware/BREAD_Loaf.kicad_pcb | python3 -I loafkeepout.py"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from loafparse_lib import parse, kids, kid, rot

pcb = parse(sys.stdin.read())
fps = []
for fp in kids(pcb, 'footprint'):
    at = kid(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    ref = next((p[2] for p in kids(fp, 'property') if p[1] == 'Reference'), None) or \
        next((t[2] for t in kids(fp, 'fp_text') if t[1] == 'reference'), '?')
    fps.append((ref, fp[1], kid(fp, 'layer')[1], fx, fy, fr, fp))
bus = sorted([f for f in fps if 'BREAD' in f[1] and '10' in f[1] and 'Pin' in f[1] and 'RA' not in f[1]], key=lambda f: f[3])
x0, y0 = bus[0][3], bus[0][4]
xs, ys = [], []
for g in pcb:
    if isinstance(g, list) and g and g[0] in ('gr_line', 'gr_rect', 'gr_arc'):
        L = kid(g, 'layer')
        if L and L[1] == 'Edge.Cuts':
            for k in ('start', 'end', 'mid'):
                p = kid(g, k)
                if p: xs.append(float(p[1])); ys.append(float(p[2]))
print(f"slots u: {[round(f[3]-x0,3) for f in bus]}  outline u {min(xs)-x0:.3f}..{max(xs)-x0:.3f}  a {y0-max(ys):.3f}..{y0-min(ys):.3f}")
for ref, lib, layer, fx, fy, fr, fp in fps:
    pts = []
    for layname in ('F.CrtYd', 'B.CrtYd', 'F.Fab', 'B.Fab'):
        for ln in kids(fp, 'fp_line') + kids(fp, 'fp_rect') + kids(fp, 'fp_arc') + kids(fp, 'fp_circle'):
            if kid(ln, 'layer')[1] == layname:
                for k in ('start', 'end', 'mid', 'center'):
                    p = kid(ln, k)
                    if p:
                        dx, dy = rot(float(p[1]), float(p[2]), fr); pts.append((fx+dx, fy+dy))
        if pts: src = layname; break
    if not pts: continue
    us = [p[0]-x0 for p in pts]; as_ = [y0-p[1] for p in pts]
    print(f"{ref:5s} {layer:5s} {src:7s} u {min(us):8.2f}..{max(us):8.2f}  a {min(as_):7.2f}..{max(as_):7.2f}  {lib}")
