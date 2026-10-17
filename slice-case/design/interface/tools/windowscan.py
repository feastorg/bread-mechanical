"""List top-side (F.Cu) footprints whose courtyard/fab bbox intersects the bus-window strip:
x in [0, XMAX] from the bus (left) edge, |y - y_bus| <= HALF.  Usage: windowscan.py XMAX HALF pcb..."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from loafparse_lib import parse, kids, kid, rot
XMAX, HALF = float(sys.argv[1]), float(sys.argv[2])
for path in sys.argv[3:]:
    pcb = parse(open(path).read())
    xs = []
    for g in pcb:
        if isinstance(g, list) and g and g[0] in ('gr_line', 'gr_rect', 'gr_arc'):
            L = kid(g, 'layer')
            if L and L[1] == 'Edge.Cuts':
                for k in ('start', 'end', 'mid'):
                    p = kid(g, k)
                    if p: xs.append(float(p[1]))
    ox = min(xs); yb = None; hits = []
    fps = kids(pcb, 'footprint')
    for fp in fps:
        if 'PinSocket_1x10' in fp[1] and 'Horizontal' in fp[1]:
            at = kid(fp, 'at'); fr = float(at[3]) if len(at) > 3 else 0
            ys = [float(at[2]) + rot(float(kid(p, 'at')[1]), float(kid(p, 'at')[2]), fr)[1] for p in kids(fp, 'pad')]
            yb = sum(ys)/len(ys)
    for fp in fps:
        if kid(fp, 'layer')[1] != 'F.Cu' or 'PinSocket_1x10' in fp[1]: continue
        at = kid(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0
        pts = []
        for lay in ('F.CrtYd', 'F.Fab'):
            for ln in kids(fp, 'fp_line') + kids(fp, 'fp_rect') + kids(fp, 'fp_circle') + kids(fp, 'fp_arc') + kids(fp, 'fp_poly'):
                if kid(ln, 'layer')[1] != lay: continue
                for k in ('start', 'end', 'mid', 'center'):
                    p = kid(ln, k)
                    if p: dx, dy = rot(float(p[1]), float(p[2]), fr); pts.append((fx+dx, fy+dy))
            if pts: break
        if not pts: continue
        x0 = min(p[0] for p in pts) - ox; y0 = min(p[1] for p in pts) - yb; y1 = max(p[1] for p in pts) - yb
        if x0 <= XMAX and y1 >= -HALF and y0 <= HALF:
            ref = next((p[2] for p in kids(fp, 'property') if p[1] == 'Reference'), '?')
            hits.append(f"{ref}({fp[1].split(':')[-1][:28]} x0={x0:.2f} y{y0:+.1f}..{y1:+.1f})")
    print(path.split('/')[4], len(hits), '; '.join(hits))
