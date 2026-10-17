"""partspec targets for the print-oriented case STLs. Parameters come from design/synth/resolved/<slice>.json
(tools/resolve.py), passed to OpenSCAD exactly as design/synth/spec.py does; print.scad only orients the real
case geometry.

Contract per print part: watertight, one solid, and nothing below the bed plane z = 0.

Trays come in USB groups: the tray is general except for the Nano USB port, which sits at each board's own Nano.
Every S Nano slice resolves to one of two port positions (resolved params usb_ports), so one tray per group:
  s_tray_nano-a  port at E 36.7 (Nano USB at board x 27.6)   built from Slice_TEMP_NANO_S2L-r2
  s_tray_nano-b  port at E 29.1 (Nano USB at board x 20.0)   built from Slice_RLHT
`python3 -I groups.py` lists which slices use which (and checks they resolve to identical tray parameters).
The lid is the same for every S slice. The panel is the one per-slice part; it prints roof strip down."""
import json
import os

from partspec import Part, openscad, region

HERE = os.path.dirname(os.path.abspath(__file__))
SYNTH = os.path.join(HERE, '..', '..', 'design', 'synth')
BACKEND = os.environ.get('CASE_BACKEND', 'Manifold') or None
GROUPS = {'nano-a': 'Slice_TEMP_NANO_S2L-r2', 'nano-b': 'Slice_RLHT'}
BLANK = dict(panel_name='', panel_headers=[], panel_labels=[], panel_notches=[])


def _part(name, slice_name, print_part, one_solid=True, **extra):
    r = json.load(open(os.path.join(SYNTH, 'resolved', slice_name + '.json')))
    params = dict(r['params'], board_t=r['probe']['board_t'], print_part=print_part)
    params.update({k: v for k, v in r['panel'].items() if k != 'source'})
    params.update(extra)
    p = Part(name, openscad(os.path.join(HERE, 'print.scad'), backend=BACKEND, **params))
    p.watertight()
    if one_solid:
        p.solid_count(1)
    p.keep_out(region.box(min=(-200, -200, -50), max=(200, 200, 0)), shell=0.05, id='below-bed')
    return p


def s_tray_nano_a(): return _part('s_tray_nano-a', GROUPS['nano-a'], 'tray_print')
def s_tray_nano_b(): return _part('s_tray_nano-b', GROUPS['nano-b'], 'tray_print')
def s_lid(): return _part('s_lid', GROUPS['nano-a'], 'lid_print')
def panel_rlht(): return _part('panel_rlht', 'Slice_RLHT', 'panel_print')
def panel_aqph(): return _part('panel_aqph', 'Slice_AQPH', 'panel_print')
def panel_blank(): return _part('panel_blank', GROUPS['nano-a'], 'panel_print', **BLANK)
def usb_plug(): return _part('usb_plug', GROUPS['nano-a'], 'usb_plug_print')   # same plug for every Nano port
