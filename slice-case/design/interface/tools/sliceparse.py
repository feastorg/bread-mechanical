"""Slice bus geometry: python3 -I sliceparse.py <BREAD_Slice.kicad_pcb>
Prints outline (KiCad coords, y down), bus socket pins, Fab body extent, holes,
all relative to the outline min corner, plus the body overhang past the nearest edge."""
import sys, math, re
sys.path.insert(0, __import__('os').path.dirname(__file__))
from loafparse_lib import parse, kids, kid, rot  # noqa

pcb = parse(open(sys.argv[1]).read())
xs, ys = [], []
for g in pcb:
    if isinstance(g, list) and g and g[0] in ('gr_line', 'gr_rect', 'gr_arc'):
        L = kid(g, 'layer')
        if L and L[1] == 'Edge.Cuts':
            for k in ('start', 'end', 'mid'):
                p = kid(g, k)
                if p: xs.append(float(p[1])); ys.append(float(p[2]))
ox, oy, X, Y = min(xs), min(ys), max(xs), max(ys)
print(f"outline {X-ox:.3f} x {Y-oy:.3f}")
for fp in kids(pcb, 'footprint'):
    lib = fp[1]
    at = kid(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    layer = kid(fp, 'layer')[1]
    if 'PinSocket_1x10' in lib or 'PinHeader_1x10' in lib:
        pins = []
        for pad in kids(fp, 'pad'):
            pat = kid(pad, 'at'); dx, dy = rot(float(pat[1]), float(pat[2]), fr)
            pins.append((fx+dx-ox, fy+dy-oy))
        bx, by = [], []
        for ln in kids(fp, 'fp_line') + kids(fp, 'fp_rect'):
            if kid(ln, 'layer')[1].endswith('Fab'):
                for k in ('start', 'end'):
                    p = kid(ln, k); dx, dy = rot(float(p[1]), float(p[2]), fr)
                    bx.append(fx+dx-ox); by.append(fy+dy-oy)
        cx = sum(p[0] for p in pins)/len(pins); cy = sum(p[1] for p in pins)/len(pins)
        print(f"{lib} {layer} rot {fr}: pin centroid ({cx:.3f},{cy:.3f}) -> from bottom edge {Y-oy-cy:.3f}")
        print(f"   Fab body x {min(bx):.3f}..{max(bx):.3f}  y {min(by):.3f}..{max(by):.3f}  (x<0 = past left edge by {-min(bx):.3f})")
    for pad in kids(fp, 'pad'):
        if pad[2] == 'np_thru_hole' or ('Mount' in lib and pad[2] == 'thru_hole'):
            pat = kid(pad, 'at'); dx, dy = rot(float(pat[1]), float(pat[2]), fr)
            d = kid(pad, 'drill')
            if d and float(d[1]) >= 2.5:
                print(f"   hole d{d[1]} at ({fx+dx-ox:.3f},{fy+dy-oy:.3f}) [{lib}]")
