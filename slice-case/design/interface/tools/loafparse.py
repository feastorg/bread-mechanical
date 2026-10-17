"""Parse a Loaf .kicad_pcb (stdin) and print outline, footprints, NPTH/mounting holes.
Usage: git -C <repo> show <rev>:hardware/BREAD_Loaf.kicad_pcb | python3 -I loafparse.py
"""
import sys, math, re

def tokenize(s):
    for m in re.finditer(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s):
        yield m.group(0)

def parse(s):
    stack = [[]]
    for t in tokenize(s):
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t.strip('"') if t.startswith('"') else t)
    return stack[0][0]

def kids(n, name):
    return [c for c in n if isinstance(c, list) and c and c[0] == name]

def kid(n, name):
    k = kids(n, name); return k[0] if k else None

def rot(x, y, deg):
    # KiCad: positive angle rotates CCW on screen (y down) -> use -deg in math frame
    a = math.radians(-deg)
    return x*math.cos(a) - y*math.sin(a), x*math.sin(a) + y*math.cos(a)

pcb = parse(sys.stdin.read())
# outline from Edge.Cuts
xs, ys = [], []
for g in pcb:
    if isinstance(g, list) and g and g[0] in ('gr_line', 'gr_rect', 'gr_arc'):
        L = kid(g, 'layer')
        if L and L[1] == 'Edge.Cuts':
            for k in ('start', 'end', 'mid'):
                p = kid(g, k)
                if p: xs.append(float(p[1])); ys.append(float(p[2]))
print(f"outline x {min(xs):.3f}..{max(xs):.3f} ({max(xs)-min(xs):.3f})  y {min(ys):.3f}..{max(ys):.3f} ({max(ys)-min(ys):.3f})")
ox, oy = min(xs), min(ys)
for fp in kids(pcb, 'footprint'):
    lib = fp[1]
    at = kid(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    ref = '?'
    for p in kids(fp, 'property'):
        if p[1] == 'Reference': ref = p[2]
    for t in kids(fp, 'fp_text'):
        if t[1] == 'reference': ref = t[2]
    layer = kid(fp, 'layer')[1]
    print(f"{ref:5s} {lib:60s} at ({fx-ox:8.3f},{fy-oy:8.3f}) rel-outline  rot {fr:6.1f} {layer}")
    pins = []
    for pad in kids(fp, 'pad'):
        pt = pad[2]; pat = kid(pad, 'at'); px, py = float(pat[1]), float(pat[2])
        dx, dy = rot(px, py, fr)
        drill = kid(pad, 'drill'); d = drill[1] if drill and len(drill) > 1 else '-'
        ax, ay = fx+dx-ox, fy+dy-oy
        if pt == 'np_thru_hole' or 'Mount' in lib or 'Hole' in lib:
            print(f"      pad {pad[1]!s:3s} {pt:13s} drill {d}  at ({ax:8.3f},{ay:8.3f})  local ({px},{py})")
        else:
            pins.append((ax, ay))
    if pins and ('10' in lib):
        cx = sum(p[0] for p in pins)/len(pins); cy = sum(p[1] for p in pins)/len(pins)
        print(f"      {len(pins)} pins, centroid ({cx:8.3f},{cy:8.3f}); x span {min(p[0] for p in pins):.3f}..{max(p[0] for p in pins):.3f} y span {min(p[1] for p in pins):.3f}..{max(p[1] for p in pins):.3f}")
