"""partspec targets for the v2 calibration coupons (coupons.scad). Case parameters come from
design/synth/resolved/<slice>.json, passed to OpenSCAD as design/synth/spec.py passes them.

Contract per coupon: watertight, one solid, and nothing below the bed plane z = 0."""
import json
import os

from partspec import Part, openscad, region

HERE = os.path.dirname(os.path.abspath(__file__))
SYNTH = os.path.join(HERE, '..', '..', 'design', 'synth')
BACKEND = os.environ.get('CASE_BACKEND', 'Manifold') or None
NANO = 'Slice_TEMP_NANO_S2L-r2'
IFACE = json.load(open(os.path.join(SYNTH, 'slot-interface-v1.1.json')))
BLANK = dict(panel_name='', panel_headers=[], panel_labels=[], panel_notches=[])


def _part(name, coupon, slice_name=NANO, **extra):
    r = json.load(open(os.path.join(SYNTH, 'resolved', slice_name + '.json')))
    params = dict(r['params'], board_t=r['probe']['board_t'], coupon=coupon)
    params.update({k: v for k, v in r['panel'].items() if k != 'source'})
    params.update(extra)
    p = Part(name, openscad(os.path.join(HERE, 'coupons.scad'), backend=BACKEND, **params))
    p.watertight()
    p.solid_count(1)
    p.keep_out(region.box(min=(-200, -200, -50), max=(200, 200, 0)), shell=0.05, id='below-bed')
    return p


def insert_ladder(): return _part('insert_ladder', 'insert_ladder')
def spigot_ladder(): return _part('spigot_ladder', 'spigot_ladder')
def hole_plate(): return _part('hole_plate', 'hole_plate')
def ear_ladder(): return _part('ear_ladder', 'ear_ladder')
def stack_tray(): return _part('stack_tray', 'stack_tray')
def stack_lid(): return _part('stack_lid', 'stack_lid')


# front panel coupons
def slide_tray(): return _part('slide_tray', 'slide_tray')
def slide_panel(): return _part('slide_panel', 'slide_panel', **BLANK)
def legend_strip(): return _part('legend_strip', 'legend_strip', 'Slice_RLHT')

def tilt_jig(): return _part('tilt_jig', 'tilt_jig', slot_pitch=IFACE['pitch'])
