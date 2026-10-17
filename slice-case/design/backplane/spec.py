"""partspec contract for the backplane part (backplane.scad) and its loose stand feet.

Interface values come from design/synth/slot-interface-v1.1.json and are passed as -D. The clash check uses
backplane.scad's file defaults (OpenSCAD `use` takes no -D), so every clash target first checks those against the JSON.
World: x = u, y = A, z = E. Prints on its E = 0 face."""
import json
import os
import re

from partspec import Part, openscad, region

HERE = os.path.dirname(os.path.abspath(__file__))
SYNTH = os.path.join(HERE, '..', 'synth')
IFACE = json.load(open(os.path.join(SYNTH, 'slot-interface-v1.1.json')))
BACKEND = os.environ.get('CASE_BACKEND', 'Manifold') or None
SEAT = IFACE['seat']['seat_E']
AL = IFACE['alignment']
RET = IFACE['retention']
B2L = IFACE['backplane_to_loaf_pcb']
PARAMS = dict(
    pitch=IFACE['pitch'], slots=IFACE['slots_per_loaf_x004'], tower_top_E=SEAT, tower_N=RET['point_N'],
    towers=list(RET['towers'].values()), tower_d=RET['backplane_tower']['footprint_d_max'],
    fin_N=AL['fin_N'], ret_inner_A=AL['returns_A'][0], ret_A1=AL['returns_A'][1], ret_N0=AL['returns_N'][0],
    guide_E=AL['guide_top_E'], outline_u=[B2L['outline_u']['union'][0], B2L['outline_u']['union'][1]],
    tails=[[k['u'][0], k['u'][1], k['A'][0], k['A'][1]] for k in B2L['loaf_top_keepouts_E_max_3.3'][1:]],
)


def _src(part, **extra):
    return openscad(os.path.join(HERE, 'backplane.scad'), backend=BACKEND, **dict(PARAMS, part=part, **extra))


def _bed(p):
    p.watertight()
    p.solid_count(1)
    p.keep_out(region.box(min=(-300, -300, -50), max=(300, 300, 0)), shell=0.05, id='below-bed')
    return p


def backplane() -> Part:
    p = _bed(Part('backplane', _src('backplane')))
    p.envelope(max=(130, 170, IFACE['alignment']['guide_top_E'] + 0.01), id='fits-mk3-bed')
    return p


def stand_foot() -> Part:
    return _bed(Part('stand_foot', _src('stand_foot')))


def probe_loaf() -> Part:
    """Backplane vs the loaf's top-side THT tails (E 3.3) and bus header plastic (E 2.54)."""
    p = Part('probe-loaf', _src('probe_loaf'))
    p.empty()
    return p


def probe_above() -> Part:
    """Nothing above seat_E - 0.3 except the tower tops and the guides (interface seat.backplane_faces)."""
    p = Part('probe-above', _src('probe_above'))
    p.empty()
    return p


def _defaults_match():
    """backplane.scad defaults == the JSON values: clash.scad builds the backplane from its defaults."""
    src = open(os.path.join(HERE, 'backplane.scad')).read()
    for k, v in PARAMS.items():
        m = re.search(rf'^{k} = (.+?);', src, re.M)
        assert m and json.loads(m.group(1)) == v, f'backplane.scad {k} = {m and m.group(1)}, slot interface {v}'


def _clash(name, board_t=None):
    _defaults_match()
    r = json.load(open(os.path.join(SYNTH, 'resolved', name + '.json')))
    params = dict(r['params'], part='clash', board_t=board_t or r['probe']['board_t'])
    params.update({k: v for k, v in r['panel'].items() if k != 'source'})
    p = Part(f'clash-{name}' + (f'-t{board_t}' if board_t else ''),
             openscad(os.path.join(HERE, 'clash.scad'), backend=BACKEND, **params))
    p.empty()
    return p


def clash_rlht() -> Part: return _clash('Slice_RLHT')
def clash_nano() -> Part: return _clash('Slice_TEMP_NANO_S2L-r2')
def clash_nano_t14() -> Part: return _clash('Slice_TEMP_NANO_S2L-r2', 1.4)
def clash_nano_t18() -> Part: return _clash('Slice_TEMP_NANO_S2L-r2', 1.8)
def clash_nucl_l() -> Part: return _clash('Slice_TEMP_NUCL_L4L-r1')


def viz_rlht() -> Part:
    """Render only: four Slice_RLHT cases on the backplane."""
    r = json.load(open(os.path.join(SYNTH, 'resolved', 'Slice_RLHT.json')))
    params = dict(r['params'], part='viz', board_t=r['probe']['board_t'])
    params.update({k: v for k, v in r['panel'].items() if k != 'source'})
    return Part('viz-rlht', openscad(os.path.join(HERE, 'viz.scad'), backend=BACKEND, **params))
