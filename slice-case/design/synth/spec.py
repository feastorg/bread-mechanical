"""partspec contract for the slice case: tray + lid + sliding front panel (case.scad, panel.scad).

Parameters come from resolved/<slice>.json (tools/resolve.py: formats.yaml + slot-interface-v1.1.json
+ slice.yaml + modifiers + legends). The board probe and the board thickness come from the slice's .kicad_pcb.
World frame = slot frame: x = E, y = A, z = N.

Limits and their homes:
  * slot-interface-v1.1.json: envelope N, thickness 30.0, seat_E, bus window, tongue, towers, ear hole d3.8,
    driver path d7.0, board thickness range.
  * ISO 261 via partspec.refs: M3 major d3.0. ISO 4762 M3 head dk 5.5, k 3.0 typed from the standard.
  * Insert: M3 x 5.7 x OD4.6 heat-set (CNC Kitchen / ruthex class). Vendor table: hole D3 4.0, min wall 1.6
    (3djake.com CNC Kitchen M3 standard listing); blind hole ~1 mm deeper than the insert (cnckitchen.com
    blog, tips-and-tricks-for-heat-set-inserts). Pocket >= 5.7 + 1.0. As-printed CAD diameter: coupon ladder.
  * Spigot bore: ISO 273 fine clearance hole for M3, d3.2 (typed from the standard).
  * Legend stroke >= 0.8: REQUIREMENTS.md L4 (one colour, readable, 0.4 and 0.6 nozzles).
  * CASE_* below mirror case.scad policy so regions can be placed: change detectors, said so.
"""
import json
import os

from partspec import Part, openscad, region
from partspec.refs import iso_metric_thread

HERE = os.path.dirname(os.path.abspath(__file__))
M3 = iso_metric_thread.coarse(3)
IFACE = json.load(open(os.path.join(HERE, 'slot-interface-v1.1.json')))
THICK_MAX = IFACE['case_max_thickness_N']
ENV_N = IFACE['slot_envelope_N']
SEAT = IFACE['seat']['seat_E']
WIN = IFACE['bus_edge_zone']['case_bus_window']
TONGUE = IFACE['bus_edge_zone']['case_tongue']
RET = IFACE['retention']
EAR_HOLE = RET['case_ear']['hole_d']
T_RANGE = IFACE['slice_side_datums']['board_thickness_range']
BOARD_TOP = IFACE['slice_side_datums']['board_top_N']
DRIVER_D, DRIVER_E0 = 7.0, 11.7                     # retention.driver_access
HEAD_DK, HEAD_K = 5.5, 3.0
SPIGOT_BORE = 3.2                                   # ISO 273 fine series, M3
INSERT_HOLE, INSERT_DEPTH = 4.0, 6.7
# USB plug envelope for the MCU access window, placed at each board's own Nano USB (resolve.py mcu_usb, from
# the .kicad_pcb): width 12.35 = USB Type-C plug overmold max (USB-IF Type-C compliance document, critical
# dimensions); height 8.9 = the taller common mini-B shell (Adafruit 1389, 34.4 x 9.2 x 8.9), above USB-C's
# 6.5 max (Amphenol Socapex USB3CFTV datasheet, citing USB-IF). Plug centre above the slice board top: 6.1
# with the Nano soldered (2.5 male-header insulator + 1.6 Nano PCB + 2.0 half a mini-B receptacle), 14.6 in
# 8.5 female headers. Typical catalogue values, not measured on a board.
PLUG_W, PLUG_H = 12.35, 8.9
PLUG_Z = (6.1 - PLUG_H / 2, 14.6 + PLUG_H / 2)

CASE_N = (-7.7, 21.9)                               # case.scad case_N (change detector)
CASE_T_NOM = 1.6
ROOF_IN = CASE_N[1] - 1.6                           # case.scad roof_in
WALL, BOARD_CLEAR, R_FAR, FAS_T, BROW = 2.0, 0.3, 5.3, 2.0, 1.5   # case.scad / panel.scad (change detectors)
FRONT_INSET, PAN_GAP, BUMP = 11.1, 0.2, 0.7         # case.scad front_inset, pan_gap, bump
FAS_N0 = 6.0                                        # panel.scad fas_N0: the wire slot's top
STROKE_MIN = 0.8                                    # REQUIREMENTS.md L4
INSERT_TOP = BOARD_TOP + 1.0                        # case.scad spigot_recess
SPIGOT_TOP = BOARD_TOP + 0.4                        # case.scad spigot_above
BACKEND = os.environ.get('CASE_BACKEND', 'Manifold') or None


def _resolved(name):
    return json.load(open(os.path.join(HERE, 'resolved', name + '.json')))


def _src(name, part, board_t=None, probe=False, blank=False, **extra):
    r = _resolved(name)
    params = dict(r['params'], part=part, board_t=board_t if board_t is not None else r['probe']['board_t'])
    params.update({k: v for k, v in r['panel'].items() if k != 'source'})
    if blank:   # the blank panel: no legend, no notches (hand labelling)
        params.update(panel_name='', panel_headers=[], panel_labels=[], panel_notches=[])
    if probe:
        params.update({k: v for k, v in r['probe'].items() if k != 'board_t'})
    params.update(extra)
    return openscad(os.path.join(HERE, 'case.scad'), backend=BACKEND, **params)


def _dims(p):
    return p['board_A'][0] - 2.3, p['board_A'][1] + 2.3, p['board_E'][1] + 0.3


def _front(p):
    """Panel geometry as case.scad derives it: opening E0 and A range, panel strip E0, travel."""
    far = [h for h in p['holes'] if h[0] > sum(p['board_E']) / 2]
    open_A = (min(h[1] for h in far) + 4.5 + 0.3, max(h[1] for h in far) - 4.5 - 0.3)
    open_E0 = p['board_E'][1] - FRONT_INSET
    pan_E0 = open_E0 + PAN_GAP
    return open_E0, open_A, pan_E0, p['board_E'][1] + BOARD_CLEAR - pan_E0


def tray(name):
    p = _resolved(name)['params']; a0, a1, e1 = _dims(p)
    t = Part(f'{name}-tray', _src(name, 'tray'))
    t.watertight(); t.solid_count(1)
    ext = (e1 - SEAT, (p['ret_A'][1] + 4.5) - (p['ret_A'][0] - 4.5), CASE_N[1] - CASE_N[0])   # full-height flanges
    t.envelope(min=tuple(v - 0.05 for v in ext), max=tuple(v + 0.05 for v in ext), id='size')
    return t


def lid(name):
    p = _resolved(name)['params']; a0, a1, e1 = _dims(p)
    l = Part(f'{name}-lid', _src(name, 'lid'))
    l.watertight(); l.solid_count(1)
    ext = (e1 - TONGUE['E_min'], a1 - a0, SPIGOT_TOP - CASE_N[0])
    l.envelope(min=tuple(v - 0.05 for v in ext), max=tuple(v + 0.05 for v in ext), id='size')
    return l


def assembly(name, board_t=None):
    r = _resolved(name); p = r['params']; a0, a1, e1 = _dims(p)
    bt = board_t if board_t is not None else r['probe']['board_t']
    dz = -(bt - CASE_T_NOM)                          # the lid follows the board underside
    tag = '' if board_t is None else f'-t{board_t}'
    s = Part(f'{name}-assembly{tag}', _src(name, 'assembly', board_t=bt))
    s.solid_count(3)
    s.envelope(max=(500, 500, THICK_MAX), id='thickness-N')
    s.keep_out(region.box(min=(-50, -100, ENV_N[1]), max=(200, 200, ENV_N[1] + 20)), shell=0.5, id='above-envelope')
    s.keep_out(region.box(min=(-50, -100, ENV_N[0] - 20), max=(200, 200, ENV_N[0])), shell=0.5, id='below-envelope')
    s.keep_out(region.box(min=(WIN['E'][0], WIN['A'][0], WIN['N'][0]), max=(WIN['E'][1], WIN['A'][1], WIN['N'][1])),
               shell=0.5, id='bus-window-empty')
    s.keep_in(region.box(min=(TONGUE['E_min'] + 0.05, TONGUE['A'][0] + 0.1, CASE_N[0] + dz + 0.5),   # above the 0.4 bed chamfer
                         max=(p['board_E'][0] - 0.35, TONGUE['A'][1] - 0.1, TONGUE['N'][1] + dz - 0.05)),
              shell=0.1, id='socket-tongue')
    n = RET['point_N']; rh = EAR_HOLE / 2
    for a in p['ret_A']:
        s.keep_out(region.cylinder(d=EAR_HOLE - 0.1, h=7.0, at=(SEAT - 1.0, a, n), axis='x'), shell=0.6, id=f'ear-hole@A{a}')
        # material just outside the hole: +A, -A, +N at r+0.2..r+0.7; -N beyond the 45 deg teardrop tip (r*1.414)
        for k, (al, ah, nl, nh) in enumerate(((rh + 0.05, rh + 0.7, -0.3, 0.3), (-rh - 0.7, -rh - 0.05, -0.3, 0.3),
                                              (-0.3, 0.3, rh + 0.05, rh + 0.7),
                                              (-0.3, 0.3, -rh * 1.414 - 0.7, -rh * 1.414 - 0.05))):
            s.keep_in(region.box(min=(SEAT + 0.3, a + al, n + nl), max=(SEAT + 4.7, a + ah, n + nh)),
                      shell=0.1, id=f'ear-hole-wall{k}@A{a}')
        s.keep_out(region.box(min=(SEAT - 1.0, a - 4.0, n - 4.0), max=(SEAT - 0.02, a + 4.0, n + 4.0)), shell=0.05,
                   id=f'pad-face-not-below-seat@A{a}')
        s.keep_in(region.box(min=(SEAT + 0.02, a + 2.5, n - 1.0), max=(SEAT + 0.28, a + 4.0, n + 1.0)), shell=0.05,
                  id=f'pad-face-at-seat@A{a}')
        s.keep_out(region.cylinder(d=DRIVER_D, h=e1 + 30 - DRIVER_E0, at=(DRIVER_E0 + 0.01, a, n), axis='x'),
                   shell=0.5, id=f'driver-path@A{a}')
    for (e, a) in p['holes']:
        s.keep_out(region.cylinder(d=INSERT_HOLE - 0.1, h=INSERT_DEPTH - 0.05, at=(e, a, INSERT_TOP), axis='z'),
                   shell=0.6, id=f'insert-pocket@{e},{a}')
        s.keep_in(region.box(min=(e + INSERT_HOLE / 2 + 0.05, a - 0.5, INSERT_TOP + 0.2),
                             max=(e + 4.4, a + 0.5, INSERT_TOP + INSERT_DEPTH - 0.2)), shell=0.1,
                  id=f'insert-wall-2.4@{e},{a}')
        # M3 major + 0.15: the d3.2 ISO 273 fine spigot bore, less 0.05 for the 48-facet polygon (0.0034 radial)
        s.keep_out(region.cylinder(d=M3.nominal + 0.15, h=INSERT_TOP - CASE_N[0] - dz + 1.0,
                                   at=(e, a, CASE_N[0] + dz - 0.5), axis='z'), shell=0.6, id=f'screw-clear@{e},{a}')
        s.keep_out(region.cylinder(d=HEAD_DK, h=HEAD_K + 0.5, at=(e, a, CASE_N[0] + dz - 0.5), axis='z'),
                   shell=0.6, id=f'head-counterbore@{e},{a}')
        s.keep_in(region.box(min=(e + SPIGOT_BORE / 2 + 0.05, a - 0.3, BOARD_TOP - bt + 0.1), max=(e + 2.3, a + 0.3, SPIGOT_TOP + dz - 0.1)),
                  shell=0.1, id=f'spigot@{e},{a}')
    # F1: the wire slot under the fascia, between the towers, stays open with the panel closed
    open_E0, open_A, _, _ = _front(p)
    # the towers are solid up to the roof beside and under the grooves; each bus-end boss is tied to its wall corner
    for k, a in enumerate(open_A):
        sa = 1 if k else -1
        lo, hi = sorted((a + sa * 0.05, a + sa * 1.5))
        s.keep_in(region.box(min=(open_E0 + 1, lo, ROOF_IN - 2.0), max=(e1 - 1, hi, ROOF_IN - 0.5)), shell=0.1, id=f'tower@A{a:+.1f}')
    for (e, a) in p['holes']:
        if e < sum(p['board_E']) / 2:
            sa = 1 if a > 0 else -1
            lo, hi = sorted((a + sa * 4.6, a + sa * 4.9))
            s.keep_in(region.box(min=(e - 1.0, lo, BOARD_TOP + 0.5), max=(e + 0.25, hi, ROOF_IN - 0.5)), shell=0.1, id=f'boss-tie@{e},{a}')
    s.keep_out(region.box(min=(e1 + 0.1, open_A[0] + 0.5, BOARD_TOP + 0.5), max=(e1 + FAS_T - 0.1, open_A[1] - 0.5, FAS_N0 - 0.2)),
               shell=0.7, id='wire-slot')
    for u in r.get('mcu_usb', []):
        assert u['dir_EA'] == [0.0, -1.0], u                 # every fleet Nano plugs in through the -A wall
        s.keep_out(region.box(min=(u['E'] - PLUG_W / 2, a0 - 1.0, BOARD_TOP + PLUG_Z[0]),
                              max=(u['E'] + PLUG_W / 2, u['A_face'], BOARD_TOP + PLUG_Z[1])),
                   shell=2.0, id=f"usb-plug@{u['ref']}")    # shell reaches the rim strip 1.65 below the plug
        # the port is plug-sized, not a window: wall material 0.8..1.5 beyond the plug envelope on both sides and above
        wa = (a0 + 0.05, a0 + WALL - 0.3)   # from just inside the outer face: the shell sees air there
        for k, (el, eh) in enumerate(((-PLUG_W / 2 - 1.5, -PLUG_W / 2 - 0.8), (PLUG_W / 2 + 0.8, PLUG_W / 2 + 1.5))):
            s.keep_in(region.box(min=(u['E'] + el, wa[0], BOARD_TOP + PLUG_Z[0] + 1.0), max=(u['E'] + eh, wa[1], BOARD_TOP + PLUG_Z[1] - 1.0)),
                      shell=0.1, id=f"usb-port-side{k}@{u['ref']}")
        s.keep_in(region.box(min=(u['E'] - PLUG_W / 2, wa[0], BOARD_TOP + PLUG_Z[1] + 0.8), max=(u['E'] + PLUG_W / 2, wa[1], ROOF_IN - 0.2)),
                  shell=0.1, id=f"usb-port-top@{u['ref']}")
    return s


def probe_board(name):
    """The board as its own .kicad_pcb draws it (outline +0.2, holes as drilled, bus socket body, every courtyard
    as a prism to the roof / lid floor, file thickness), placed by its bus datum, intersected with the case."""
    pr = Part(f'{name}-probe-board', _src(name, 'probe_board', probe=True))
    pr.empty()
    return pr


def probe_board_only(name):
    r = _resolved(name)
    pr = Part(f'{name}-probe-board-only', _src(name, 'probe_board_only', probe=True))
    oe, oa = r['probe']['pb_outline_E'], r['probe']['pb_outline_A']
    pr.envelope(min=(oe[1] - oe[0], oa[1] - oa[0], 1.5))
    return pr


def probe_parts(name):
    """Tray vs lid moved 0.15 toward the tray, at the thinnest board in the interface range."""
    pr = Part(f'{name}-probe-parts', _src(name, 'probe_parts', board_t=T_RANGE[0]))
    pr.empty()
    return pr


def probe_below_seat(name):
    pr = Part(f'{name}-probe-below-seat', _src(name, 'probe_below_seat'))
    pr.empty()
    return pr


# ---- front panel --------------------------------------------------------------------------------------------
def panel(name, blank=False):
    p = _resolved(name)['params']; a0, a1, e1 = _dims(p)
    _, _, pan_E0, _ = _front(p)
    pr = Part(f'{name}-panel' + ('-blank' if blank else ''), _src(name, 'panel', blank=blank))
    pr.watertight(); pr.solid_count(1)
    # E: strip end to the pull ridge; A: the fascia's back face, where the R5.3 plan corners have turned 3.3 in;
    # N: the corner legs reach the lid face
    ext = (e1 + FAS_T + BROW - pan_E0, (a1 - a0) - 2 * (R_FAR - (R_FAR ** 2 - (R_FAR - FAS_T) ** 2) ** 0.5), CASE_N[1] - CASE_N[0])
    pr.envelope(min=tuple(v - 0.05 for v in ext), max=tuple(v + 0.05 for v in ext), id='size')
    return pr


def panel_swept(name):
    """The panel at every 2 mm of its pull, closed to clear of the grooves: inside the slot envelope and out of
    the ear-screw driver paths the whole way (F5, F6)."""
    p = _resolved(name)['params']; a0, a1, e1 = _dims(p)
    s = Part(f'{name}-panel-swept', _src(name, 'panel_swept'))
    s.keep_out(region.box(min=(-50, -100, ENV_N[1]), max=(250, 200, ENV_N[1] + 20)), shell=0.5, id='above-envelope')
    s.keep_out(region.box(min=(-50, -100, ENV_N[0] - 20), max=(250, 200, ENV_N[0])), shell=0.5, id='below-envelope')
    for a in p['ret_A']:
        s.keep_out(region.cylinder(d=DRIVER_D, h=e1 + 40 - DRIVER_E0, at=(DRIVER_E0 + 0.01, a, RET['point_N']), axis='x'),
                   shell=4.0, id=f'driver-path@A{a}')   # the fascia edge is 0.6 outside the path
    return s


def _probe(name, part, pid, **kw):
    pr = Part(f'{name}-{pid}', _src(name, part, **kw))
    pr.empty()
    return pr


def probe_panel_closed(name):
    """Closed, bump in its notch: no contact with the tray, so the finger carries no load at rest."""
    return _probe(name, 'probe_panel_closed', 'probe-panel-closed')


def probe_panel_lid(name):
    """Fascia corner legs against the lid, at the thinnest board (the lid sits highest)."""
    return _probe(name, 'probe_panel_lid', 'probe-panel-lid', board_t=T_RANGE[0])


def probe_panel_slide(name):
    """The panel without its bumps, at every 1 mm of the pull: the tongues run free in the grooves."""
    return _probe(name, 'probe_panel_slide', 'probe-panel-slide')


def probe_panel_shift(name):
    """Panel (no bumps) moved 0.15 each way in A and N: still clear, so the V clearance is at least 0.15."""
    return _probe(name, 'probe_panel_shift', 'probe-panel-shift', probe_shift=0.15)


def _locate(name, d, pid):
    pr = Part(f'{name}-{pid}', _src(name, 'probe_panel_locate', probe_shift=0.4, probe_dir=d))
    pr.volume(min=0.01)
    return pr


def probe_panel_locate_A(name):
    """Panel moved 0.4 in +A hits the tower: the grooves locate it (clearance < 0.4)."""
    return _locate(name, [0, 1, 0], 'probe-panel-locate-A')


def probe_panel_locate_N(name):
    """Panel moved 0.4 in +N hits the groove: located in N too."""
    return _locate(name, [0, 0, 1], 'probe-panel-locate-N')


def probe_detent(name):
    """Pulled 3.0, bump past its notch: the +A bump presses into the groove wall (the finger deflection that holds
    the panel shut, F3). Bump 0.7 past the V apex against the groove apex 0.28 out: 0.42 deep at the apex, and the
    overlap reaches 0.65 along A where the bump's flanks cross the groove's (geometry; change detector)."""
    pr = Part(f'{name}-probe-detent', _src(name, 'probe_detent', probe_pull=3.0))
    pr.envelope(min=(0.3, 0.45, 0.3), max=(5.0, 0.85, 2.0), id='bump-interference')
    return pr


def probe_legend_thin(name):
    """Legend strokes narrower than 0.8 (from 0.4 up): none."""
    return _probe(name, 'probe_legend_thin', 'probe-legend-thin', stroke_min=STROKE_MIN)


def probe_legend_off_face(name):
    """Legend outside the flat fascia face (0.3 margin), on a notch, the wire slot or under the pull ridge: none."""
    return _probe(name, 'probe_legend_off_face', 'probe-legend-off-face')


SLICES = {'nano': 'Slice_TEMP_NANO_S2L-r2', 'nucl': 'Slice_TEMP_NUCL_L4L-r1', 'dcmt': 'Slice_DCMT', 'rlht': 'Slice_RLHT',
          'aqph': 'Slice_AQPH'}
CASE_FNS = (tray, lid, assembly, probe_board, probe_board_only, probe_parts, probe_below_seat)
PANEL_FNS = (panel, panel_swept, probe_panel_closed, probe_panel_lid, probe_panel_slide, probe_panel_shift,
             probe_panel_locate_A, probe_panel_locate_N, probe_detent, probe_legend_thin, probe_legend_off_face)
for _k, _n in SLICES.items():
    for _f in CASE_FNS + (PANEL_FNS if _k in ('rlht', 'aqph') else ()):
        globals()[f'{_k}_{_f.__name__}'] = (lambda f=_f, n=_n: f(n))


def nano_panel_blank():
    return panel(SLICES['nano'], blank=True)


def nano_assembly_nominal():
    """Nominal 1.6 board: change detector for the 29.6 policy thickness."""
    s = assembly(SLICES['nano'], board_t=CASE_T_NOM)
    s.envelope(min=(1, 1, 29.55), max=(500, 500, 29.65), id='nominal-29.6')
    return s


def nano_assembly_tmax():
    """Thickest board the interface allows: still inside the slot envelope."""
    return assembly(SLICES['nano'], board_t=T_RANGE[1])


# ---- render-only targets ----------------------------------------------------------------------------
def _r(key, part, **kw):
    return Part(f'{key}-{part}', _src(SLICES[key], part, **kw))


def nano_tray_print(): return _r('nano', 'tray_print')
def nano_board(): return _r('nano', 'assembly_board')
def nano_exploded(): return _r('nano', 'exploded')
def nucl_board(): return _r('nucl', 'assembly_board')
def dcmt_board(): return _r('dcmt', 'assembly_board')

