# SPDX-License-Identifier: GPL-3.0-or-later
"""partspec contract for the SBC cases (sbc_case.scad): lid, bottom, extrusion mount and the insert coupon.

Board settings come from boards.json, passed as -D (OpenSCAD's -p does not reach variables that sbc_case.scad
takes from Case Builder through `include`). Case Builder and SBC Model Framework resolve through the scadman
environment of this repository (../.scadman/env, `scadman sync`), which is put on OPENSCADPATH here.

Where the limits come from:
  * Board geometry (mounting holes, GPIO header position and pin count) is SBC Model Framework's data for the
    board, read from sbc_models.cfg -- the reference the parts are built against, not the parts themselves.
    Upstream marks rpi3a+, rpi4b and rpizero2w "yellow, unverified"; the printed fit test is the check on it.
  * Header pitch 2.54: 0.1 in.
  * M2.5 and M5 major diameters: ISO 261 via partspec.refs.iso_metric_thread.
  * ISO 4762 socket heads, typed from the standard: M3 dk 5.5, k 3.0; M5 dk 8.5, k 5.0. ISO 7046-1 M2.5
    countersunk head dk 4.7 (actual, max), typed from the standard.
  * Heat-set insert, M3 x 5.7 (the ear screws): slice-case's insert, length 5.7 from the same vendor table
    (3djake.com CNC Kitchen M3 standard listing); its pocket, 4.0 x 6.7, is slice-case's printed one.
  * Heat-set insert, M2.5 x 4.0: length 4.0 from Prusa's CNC Kitchen insert set listing
    (prusa3d.com/product/heat-set-inserts-set-xxl-760-pcs); hole 3.7 is an unverified aggregator figure
    (funkfinger.github.io/binkey-data/parts/cnc-kitchen-heat-set-inserts-universal), which is why the coupon
    exists. The pocket check below asserts room for the insert's length at a diameter below every rung.
  * 2020 extrusion face 20 mm: the profile's name.
  * Case screw length: the model picks it (echoed as case_screw); the check below holds its reach into the
    insert, length - bottom_height, between 2.5 and the insert's length.
World: model frame for bottom; lid and mount in print orientation as sbc_case.scad documents."""
import json
import os
import subprocess
import tempfile

from partspec import Part, Referenced, openscad, region
from partspec.refs import iso_metric_thread

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENV = os.path.join(ROOT, '.scadman', 'env')
if not os.path.isdir(os.path.join(ENV, 'SBC_Case_Builder')):
    raise RuntimeError(f'{ENV} has no SBC_Case_Builder: run `scadman sync` in {ROOT}')
os.environ['OPENSCADPATH'] = ENV + os.pathsep + os.environ.get('OPENSCADPATH', '')

BACKEND = os.environ.get('CASE_BACKEND', 'Manifold') or None
BOARDS = json.load(open(os.path.join(HERE, 'boards.json')))['parameterSets']
SRC = os.path.join(HERE, 'sbc_case.scad')

M25 = iso_metric_thread.coarse(2.5).nominal
M3 = iso_metric_thread.coarse(3).nominal
M5 = iso_metric_thread.coarse(5).nominal
ISO4762 = {'M3': {'dk': 5.5, 'k': 3.0}, 'M5': {'dk': 8.5, 'k': 5.0}}   # typed from ISO 4762
ISO7046_M25_DK = 4.7                                                   # typed from ISO 7046-1
INSERT_LEN = Referenced(4.0, {'standard': 'Prusa CNC Kitchen heat-set insert set listing',
                              'subject': 'M2.5 x 4.0 heat-set insert', 'field': 'length'})
INSERT_M3_LEN = Referenced(5.7, {'standard': '3djake.com CNC Kitchen M3 standard listing',
                                 'subject': 'M3 x 5.7 heat-set insert', 'field': 'length'})
PITCH = 2.54
PROFILE = 20                        # 2020 face

# The mount's own design inputs, as sbc_case.scad declares them (change-detectors, not references).
PLATE_T = 8
EAR_T = 4
# The real board's thickness, which the bottom standoffs stop under: 1.6, measured on a Pi 4B with calipers
# (Raspberry Pi's mechanical drawings give none; Case Builder models 1.0). The sleeve's wall, a design input: at
# least 1.2, three perimeters at 0.4.
BOARD_T = 1.6
SLEEVE_WALL = 1.2


def _value(v):
    if v in ('true', 'false'):
        return v == 'true'
    try:
        return float(v)
    except ValueError:
        return v


def _params(board, part):
    return dict({k: _value(v) for k, v in BOARDS[board].items()}, part=part)


def _src(board, part, **extra):
    return openscad(SRC, backend=BACKEND, **dict(_params(board, part), **extra))


_DATA = {}


def board_data(board):
    """Holes, header field and Case Builder's dimensions for a board, echoed by tools/board_data.scad."""
    if board not in _DATA:
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            out = os.path.join(tmp, 'board.echo')
            args = ['openscad', '-o', out]
            for k, v in _params(board, 'none').items():
                args += ['-D', f'{k}={json.dumps(v) if isinstance(v, (str, bool)) else v}']
            r = subprocess.run(args + [os.path.join(HERE, 'tools', 'board_data.scad')], capture_output=True,
                               text=True, env=os.environ)
            line = [l for l in open(out).read().splitlines() if 'BOARD_DATA' in l] if os.path.exists(out) else []
        assert line, f'tools/board_data.scad gave nothing for {board}:\n{r.stderr[-2000:]}'
        _DATA[board] = json.loads(line[0].split('BOARD_DATA', 1)[1].strip().rstrip('"').replace('\\"', '"'))
    return _DATA[board]


def _solid(p):
    p.watertight()
    p.solid_count(1)
    return p


# ---- lid (print frame: x, depth - y, case_z - z) ------------------------------------------------------------
def _lid(board):
    d = board_data(board)
    p = _solid(Part(f'lid-{board}', _src(board, 'lid')))
    tz = d['case_z']
    fy = lambda y: d['depth'] - y
    # The header's pin field, through the roof: open, so jumpers plug in with the lid on.
    gx, gy = d['gpio_x'], d['gpio_y']
    p.keep_out(region.box(min=(gx[0], fy(gy[1]), -0.1), max=(gx[1], fy(gy[0]), d['floorthick'] + 0.1)),
               shell=0.4, id='gpio-window')
    # Over the window, nothing hangs from the roof up to the standoff collars' height (Case Builder's
    # top_standoff_support_height, 4): no overhang left over the opening, outside each standoff's ring.
    ft, m = d['floorthick'], 1.0
    p.keep_out(region.box(min=(7.5, fy(gy[1] + m), ft - 0.5), max=(57.5, fy(gy[0] - m), ft + 3.9)),
               shell=0.3, id='window-no-overhang')
    # A roof strip between the window and the vents, so each vent bar is held at both ends: no slot runs into
    # the window.
    p.keep_in(region.box(min=(gx[0], fy(gy[0] - m) + 0.2, 0.2), max=(gx[1], fy(gy[0] - m) + 2.8, ft - 0.2)),
              shell=0.3, id='vent-member')
    # Each top standoff keeps its wall on the window side: the window must not cut it.
    for i, (hx, hy) in enumerate(d['holes']):
        side = 1 if hx < (gx[0] + gx[1]) / 2 else -1
        x0 = hx + side * 2.2
        p.keep_in(region.box(min=(min(x0, x0 + side * 0.6), fy(hy) - 0.4, d['floorthick'] + 0.2),
                             max=(max(x0, x0 + side * 0.6), fy(hy) + 0.4, tz - d['bottom_height'] - 0.2)),
                  shell=0.3, id=f'standoff-wall@{hx},{hy}')
        # Insert pocket: room for the insert's length from the standoff face, narrower than every coupon rung.
        p.keep_out(region.cylinder(d=3.3, h=INSERT_LEN,
                                   at=(hx, fy(hy), tz - d['bottom_height'] - INSERT_LEN), axis='z'),
                   shell=0.3, id=f'insert-pocket@{hx},{hy}')
    # The header-side wall stays whole along its length, roof to rim: no roof pattern or window cuts it.
    # (On the Zero 2 W, Case Builder's hex roof pattern and the window once left it a row of posts.)
    y0, w = fy(d['case_y'][1]), d['wallthick']
    p.keep_in(region.box(min=(d['case_x'][0] + 3, y0 + 0.3, 0.3),
                         max=(d['case_x'][1] - 3, y0 + w - 0.3, tz - d['bottom_height'] - 1.0)),
              shell=0.3, id='header-wall')
    return p


# ---- bottom (model frame) -------------------------------------------------------------------------------------
def _bottom(board):
    d = board_data(board)
    p = _solid(Part(f'bottom-{board}', _src(board, 'bottom')))
    # The case screw's path: an M2.5 passes the floor and the bottom standoff at every board hole, and its
    # countersunk head goes into the floor's underside.
    for hx, hy in d['holes']:
        p.keep_out(region.cylinder(d=M25, h=d['bottom_height'] + 0.2, at=(hx, hy, -0.1), axis='z'),
                   shell=0.4, id=f'screw-path@{hx},{hy}')
        p.keep_out(region.cylinder(d=ISO7046_M25_DK, h=0.3, at=(hx, hy, -0.1), axis='z'),
                   shell=0.4, id=f'countersink@{hx},{hy}')
        # The standoff stops under the real board, and its wall around the screw hole is printable: material
        # from the hole (Case Builder's m2.5+, 2.83) out to SLEEVE_WALL, above the base collar (4 tall) to the top.
        top = d['bottom_height'] - BOARD_T
        p.keep_out(region.cylinder(d=4.0, h=0.35, at=(hx, hy, top + 0.05), axis='z'), shell=0.3,
                   id=f'standoff-top@{hx},{hy}')
        r0 = 2.83 / 2
        p.keep_in(region.box(min=(hx + r0 + 0.2, hy - 0.3, 4.3), max=(hx + r0 + SLEEVE_WALL - 0.2, hy + 0.3, top - 0.1)),
                  shell=0.3, id=f'standoff-wall@{hx},{hy}')
    # The header-side wall has no port on any board: it stays whole, floor to rim (the rim cut keeps to openings).
    y1, w = d['case_y'][1], d['wallthick']
    p.keep_in(region.box(min=(d['case_x'][0] + 4, y1 - w + 0.1, d['floorthick'] + 0.3),
                         max=(d['case_x'][1] - 4, y1 - 0.1, d['bottom_height'] - 0.1)),
              shell=0.3, id='header-wall')
    # Its reach into the lid insert, which starts at the board top: enough thread, and inside the insert.
    reach = d['case_screw'] - d['bottom_height']
    assert 2.5 <= reach <= INSERT_LEN, f'{board}: M2.5x{d["case_screw"]} reaches {reach} into the insert'
    # The ears: an M3 passes each, there is ear around it, and the screw head clears the case's end wall.
    hd, hk = ISO4762['M3']['dk'], ISO4762['M3']['k']
    for i, (ex, ey) in enumerate(d['ears']):
        p.keep_out(region.cylinder(d=M3, h=EAR_T + 0.2, at=(ex, ey, -0.1), axis='z'), shell=0.4, id=f'ear-hole-{i}')
        p.keep_in(region.box(min=(ex - 0.3, ey + 2.2, 0.2), max=(ex + 0.3, ey + 3.0, EAR_T - 0.2)),
                  shell=0.3, id=f'ear-{i}')
        p.keep_out(region.cylinder(d=hd, h=hk, at=(ex, ey, EAR_T + 0.1), axis='z'), shell=0.4, id=f'ear-head-{i}')
    return p


# ---- mount (print frame: model z + plate_t) -------------------------------------------------------------------
def _mount(board):
    d = board_data(board)
    p = _solid(Part(f'mount-{board}', _src(board, 'mount')))
    p.genus(2)                                   # the two T-nut screws; the ear insert pockets are blind
    # The ear screws: an M3 x 5.7 insert fits each pocket, under its ear, and the pocket stays blind.
    for i, (ex, ey) in enumerate(d['ears']):
        p.keep_out(region.cylinder(d=M3 + 0.9, h=INSERT_M3_LEN, at=(ex, ey, PLATE_T - INSERT_M3_LEN + 0.1), axis='z'),
                   shell=0.3, id=f'ear-insert-{i}')
        # The pocket's floor, bed to pocket bottom (PLATE_T - 6.7, slice-case's pocket depth).
        p.keep_in(region.box(min=(ex - 0.3, ey - 0.3, 0.1), max=(ex + 0.3, ey + 0.3, PLATE_T - 6.7 - 0.1)), shell=0.2,
                  id=f'ear-insert-floor-{i}')
    # The T-nut screws: shank through, socket head recessed below the plate top (which meets the case floor).
    bd, bk = ISO4762['M5']['dk'], ISO4762['M5']['k']
    for i, (bx, by) in enumerate(d['bolts']):
        p.keep_out(region.cylinder(d=M5, h=PLATE_T + 0.2, at=(bx, by, -0.1), axis='z'), shell=0.4, id=f'bolt-{i}')
        p.keep_out(region.cylinder(d=bd, h=bk + 0.1, at=(bx, by, PLATE_T - bk), axis='z'), shell=0.4,
                   id=f'bolt-head-{i}')
    # Where the extrusion face bears, the plate's underside is solid: no case-screw head pocket lands on it.
    ex = d['ex']
    for s in (-1, 1):
        x = sorted([ex + s * (M5 / 2 + 0.6), ex + s * PROFILE / 2])
        p.keep_in(region.box(min=(x[0], d['case_y'][0] + 1, 0.1), max=(x[1], d['case_y'][1] - 1, 0.6)),
                  shell=0.3, id=f'extrusion-face-{"left" if s < 0 else "right"}')
    return p


# ---- coupon ---------------------------------------------------------------------------------------------------
def coupon() -> Part:
    p = _solid(Part('insert-coupon', _src('rpi4b', 'coupon')))
    rungs = [3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0]   # sbc_case.scad sc_coupon_rungs, printed on each boss
    top = 4.5 + 1.5
    for i, r in enumerate(rungs):
        p.keep_out(region.cylinder(d=r - 0.1, h=INSERT_LEN, at=(i * 14, 0, top - INSERT_LEN), axis='z'), shell=0.3,
                   id=f'pocket-{r}')
    return p


def lid_rpi4b() -> Part: return _lid('rpi4b')
def lid_rpi3a() -> Part: return _lid('rpi3a+')
def lid_rpizero2w() -> Part: return _lid('rpizero2w')
def bottom_rpi4b() -> Part: return _bottom('rpi4b')
def bottom_rpi3a() -> Part: return _bottom('rpi3a+')
def bottom_rpizero2w() -> Part: return _bottom('rpizero2w')
def mount_rpi4b() -> Part: return _mount('rpi4b')
def mount_rpi3a() -> Part: return _mount('rpi3a+')
def mount_rpizero2w() -> Part: return _mount('rpizero2w')

TARGETS = [f'spec.py:{n}' for n in ('lid_rpi4b', 'lid_rpi3a', 'lid_rpizero2w', 'bottom_rpi4b', 'bottom_rpi3a',
                                     'bottom_rpizero2w', 'mount_rpi4b', 'mount_rpi3a', 'mount_rpizero2w', 'coupon')]
