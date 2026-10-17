"""Downward-facing area in print orientation.  python3 -I overhang.py <binary.stl> <+z|-z>
'+z' prints with the model's z up (bed at zmin); '-z' flips (bed at zmax).  Reports facets steeper than
45 deg past vertical (normal_z < -cos45) that are not on the bed, grouped by height above the bed and
by xy bbox, so a bridge can be told from a cantilever by reading where it is."""
import struct, sys, math
p, d = sys.argv[1], sys.argv[2]
b = open(p, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]
s = 1 if d == '+z' else -1
tris = []
for i in range(n):
    v = struct.unpack_from('<12f', b, 84 + 50 * i)
    pts = [(v[3], v[4], s * v[5]), (v[6], v[7], s * v[8]), (v[9], v[10], s * v[11])]
    tris.append(pts if s == 1 else [pts[0], pts[2], pts[1]])  # a mirror reverses winding
z0 = min(c[2] for t in tris for c in t)
groups = {}
for a, bb, c in tris:
    ux, uy, uz = bb[0]-a[0], bb[1]-a[1], bb[2]-a[2]; vx, vy, vz = c[0]-a[0], c[1]-a[1], c[2]-a[2]
    nx, ny, nz = uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx
    ln = math.sqrt(nx*nx+ny*ny+nz*nz)
    if ln == 0: continue
    if nz / ln < -math.cos(math.radians(45)):
        h = min(a[2], bb[2], c[2]) - z0
        if h < 0.01: continue
        k = round(h, 2)
        g = groups.setdefault(k, [0.0, [1e9, -1e9, 1e9, -1e9]])
        g[0] += ln / 2
        for q in (a, bb, c):
            g[1][0] = min(g[1][0], q[0]); g[1][1] = max(g[1][1], q[0]); g[1][2] = min(g[1][2], q[1]); g[1][3] = max(g[1][3], q[1])
print(f'{p.split("/")[-1]} print {d}: {sum(g[0] for g in groups.values()):.1f} mm2 downward-facing off the bed')
for k in sorted(groups):
    a, bb = groups[k]
    print(f'  h {k:6.2f}  {a:8.1f} mm2  x[{bb[0]:.2f},{bb[1]:.2f}] y[{bb[2]:.2f},{bb[3]:.2f}]')
