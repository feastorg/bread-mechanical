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
  * ISO 4762 socket heads, typed from the standard: M2.5 dk 4.5, k 2.5; M5 dk 8.5, k 5.0.
  * Heat-set insert, M2.5 x 4.0: length 4.0 from Prusa's CNC Kitchen insert set listing
    (prusa3d.com/product/heat-set-inserts-set-xxl-760-pcs); hole 3.7 is an unverified aggregator figure
    (funkfinger.github.io/binkey-data/parts/cnc-kitchen-heat-set-inserts-universal), which is why the coupon
    exists. The pocket check below asserts room for the insert's length at a diameter below every rung.
  * 2020 extrusion face 20 mm: the profile's name.
  * Screw stack (the counterbore floor): derived below from the screw length, Case Builder's board-top height
    (echoed by the model as bottom_height) and the thread engagement; stated in the comment where it is used.
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
M5 = iso_metric_thread.coarse(5).nominal
ISO4762 = {'M2.5': {'dk': 4.5, 'k': 2.5}, 'M5': {'dk': 8.5, 'k': 5.0}}   # typed from ISO 4762
INSERT_LEN = Referenced(4.0, {'standard': 'Prusa CNC Kitchen heat-set insert set listing',
                              'subject': 'M2.5 x 4.0 heat-set insert', 'field': 'length'})
PITCH = 2.54
PROFILE = 20                        # 2020 face

# The mount's own design inputs, as sbc_case.scad declares them (change-detectors, not references).
PLATE_T = 8
SCREW_LEN = 16
ENGAGEMENT = 3.5


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
    # The case screw's path: an M2.5 passes the floor and the bottom standoff at every board hole.
    for hx, hy in d['holes']:
        p.keep_out(region.cylinder(d=M25, h=d['bottom_height'] + 0.2, at=(hx, hy, -0.1), axis='z'),
                   shell=0.4, id=f'screw-path@{hx},{hy}')
    return p


# ---- mount (print frame: model z + plate_t) -------------------------------------------------------------------
def _mount(board):
    d = board_data(board)
    p = _solid(Part(f'mount-{board}', _src(board, 'mount')))
    p.genus(6)                                   # four case screws, two T-nut screws: through-holes only
    # Screw stack. The insert starts at the top standoff face, at the board top as modelled (bottom_height above
    # the case floor); an M2.5 x SCREW_LEN reaching ENGAGEMENT into it leaves SCREW_LEN - bottom_height -
    # ENGAGEMENT of shank in the plate, so the head seats that far below the plate top.
    seat = PLATE_T - (SCREW_LEN - d['bottom_height'] - ENGAGEMENT)
    hd, hk = ISO4762['M2.5']['dk'], ISO4762['M2.5']['k']
    assert seat >= hk, f'{board}: M2.5x{SCREW_LEN} head ({hk}) does not fit a {seat} counterbore'
    for hx, hy in d['holes']:
        p.keep_out(region.cylinder(d=M25, h=PLATE_T + 0.2, at=(hx, hy, -0.1), axis='z'), shell=0.4,
                   id=f'screw@{hx},{hy}')
        p.keep_out(region.cylinder(d=hd, h=seat + 0.1, at=(hx, hy, -0.1), axis='z'), shell=0.4,
                   id=f'head-pocket@{hx},{hy}')
        # Material the head bears on, just above the seat, between the clearance hole and the head's rim.
        p.keep_in(region.box(min=(hx - 0.3, hy + 1.6, seat + 0.1), max=(hx + 0.3, hy + 2.1, seat + 0.6)),
                  shell=0.3, id=f'head-seat@{hx},{hy}')
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
