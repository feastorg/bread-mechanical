"""Top-side THT pad bboxes of B.Cu footprints, frame of loafkeepout.py (u from slot1, a=+toward pin1)."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from loafparse_lib import parse, kids, kid, rot
pcb = parse(sys.stdin.read())
fps = kids(pcb, 'footprint')
def ref(fp):
    return next((p[2] for p in kids(fp, 'property') if p[1] == 'Reference'), None) or next((t[2] for t in kids(fp, 'fp_text') if t[1] == 'reference'), '?')
bus = sorted([fp for fp in fps if ('BREAD 10-Pin' in fp[1] or 'Slice_Bus' in fp[1])], key=lambda f: float(kid(f, 'at')[1]))
x0, y0 = float(kid(bus[0], 'at')[1]), float(kid(bus[0], 'at')[2])
for fp in fps:
    if kid(fp, 'layer')[1] != 'B.Cu': continue
    at = kid(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    us, as_ = [], []
    for pad in kids(fp, 'pad'):
        if pad[2] != 'thru_hole': continue
        pa = kid(pad, 'at'); dx, dy = rot(float(pa[1]), float(pa[2]), fr)
        sz = kid(pad, 'size'); r = max(float(sz[1]), float(sz[2]))/2
        u, a = fx+dx-x0, y0-(fy+dy)
        us += [u-r, u+r]; as_ += [a-r, a+r]
    if us: print(f"{ref(fp):4s} THT pads u {min(us):7.2f}..{max(us):7.2f} a {min(as_):7.2f}..{max(as_):7.2f}  {fp[1]}")
