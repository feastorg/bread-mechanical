"""Write slot-interface-v1.1.json: slot-interface-v1.json plus the changes the synthesis proposes.

Usage: python3 -I tools/make_iface.py   (reads ../interface/slot-interface-v1.json, writes ./slot-interface-v1.1.json)

Every change is listed in CHANGES and applied here, so the diff against v1 is this file.
"""
import copy, json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v1 = json.load(open(os.path.join(HERE, '..', 'interface', 'slot-interface-v1.json')))
v = copy.deepcopy(v1)
CHANGES = [
    "id -> slot-interface-v1.1",
    "retention: a fixed tower set (T1 -56.4, T2 +56.4, T3 +101.4) is the slot contract; a format row in the format "
    "table selects towers by id. Removes retention.points_A per format, rule_A as a rule, towers_per_slot as 'union of "
    "formats', and slice_side_datums.format_extent_A. A new format that needs a new tower position is a backplane reprint, "
    "and the format table says so by naming an unknown id.",
    "retention.case_ear.hole_d 3.4 -> 3.8, printed as a teardrop: the guide sets the slice position; the screw only "
    "clamps (M3 in 3.8 leaves +/-0.4, larger than the guide's 0.15/0.2 clearance).",
    "retention.case_ear.N_range_max describes the pad land only; a case may buttress the ear further in N inside its "
    "own slot envelope at E >= seat_E + 0.3.",
    "slice_side_datums.board_thickness -> board_thickness_range [1.4, 1.8]: board_top_N is the datum (socket sits on "
    "it); the board's underside floats with thickness, and a case must absorb that inside the envelope.",
]
v['id'] = 'slot-interface-v1.1'
v['changes_from_v1'] = CHANGES
r = v['retention']
r['towers'] = {'T1': -56.4, 'T2': 56.4, 'T3': 101.4}
r['towers_note'] = ("Every slot carries all towers, at point_N. Formats select towers by id (bread-infra format "
                    "table). Guidance for a new format: ear 6.4 beyond the board end, i.e. pick or add the tower there.")
for k in ('points_A', 'rule_A'):
    r.pop(k, None)
r['case_ear']['hole_d'] = 3.8
r['case_ear']['hole_shape'] = 'teardrop, point toward -N (up when the THT-side part prints roof-down), 45 deg'
r['case_ear'].pop('body_end_A', None)
r['case_ear']['N_range_max_note'] = 'pad land only; buttressing beyond it is allowed inside the slot envelope at E >= seat_E + 0.3'
r['backplane_tower']['towers_per_slot'] = 'all ids in retention.towers'
sd = v['slice_side_datums']
sd.pop('format_extent_A', None)
sd.pop('board_thickness', None)
sd['board_thickness_range'] = [1.4, 1.8]
sd['board_bottom_N'] = 'board_top_N - thickness (floats)'
v.pop('formats', None)
v['prose'][2] = ("Retention: two M3 screws per slice along -E, driven from the slice's far side past the case ends, into "
                 "heat-set inserts in the backplane part. The ear pads are the only E stop; the guide, not the screw, "
                 "locates the slice. Every slot carries towers T1 -56.4, T2 +56.4, T3 +101.4; each format selects two.")
v['named_exceptions_moved_to'] = 'format table exceptions list (bread-infra stand-in: synth/formats.yaml)'
json.dump(v, open(os.path.join(HERE, 'slot-interface-v1.1.json'), 'w'), indent=1)
print('wrote slot-interface-v1.1.json;', len(CHANGES), 'changes; removed top-level formats:', 'formats' in v1)
