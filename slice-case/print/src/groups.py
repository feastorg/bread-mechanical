"""Which slices each case STL serves. Usage: python3 -I groups.py

Groups the resolved slices by the parameters the tray and the lid are built from (resolved params; the panel data
and the board probe are not inputs to either, and floor_reliefs only cut the lid), and names the group each print_spec.py STL was built from."""
import glob, json, os

SYNTH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'design', 'synth')
BUILT = {'s_tray_nano-a': 'Slice_TEMP_NANO_S2L-r2', 's_tray_nano-b': 'Slice_RLHT'}
LID_KEYS = ('board_E', 'board_A', 'board_r', 'holes', 'tongue_A', 'tongue_E_min', 'floor_reliefs')

trays, lids = {}, {}
for f in sorted(glob.glob(os.path.join(SYNTH, 'resolved', '*.json'))):
    r = json.load(open(f))
    p = r['params']
    trays.setdefault(json.dumps({k: v for k, v in p.items() if k != 'floor_reliefs'}, sort_keys=True), []).append(r['slice'])
    lids.setdefault(json.dumps({k: p[k] for k in LID_KEYS}, sort_keys=True), []).append(r['slice'])
for key, names in trays.items():
    stl = [s for s, n in BUILT.items() if n in names]
    port = json.loads(key)['usb_ports']
    print(f"tray {stl[0] if stl else '(no STL)':14s} usb_ports {port}: {len(names)} slices: {' '.join(names)}")
for key, names in lids.items():
    print(f"lid  {'s_lid' if 'Slice_TEMP_NANO_S2L-r2' in names else '(no STL)':14s} {len(names)} slices: {' '.join(names)}")
