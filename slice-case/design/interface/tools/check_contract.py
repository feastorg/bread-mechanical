"""Self-consistency checks of slot-interface-v1.json. Prints PASS/FAIL per check with the numbers."""
import json, sys
c = json.load(open(sys.argv[1]))
fails = 0
def chk(name, ok, detail):
    global fails
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")

n0, n1 = c['slot_envelope_N']
chk('thickness', n1 - n0 <= c['case_max_thickness_N'] + 1e-9, f"{n1-n0:.2f} <= {c['case_max_thickness_N']}")
chk('gap', c['pitch'] - (n1 - n0) >= c['min_gap_between_cases'] - 1e-9, f"{c['pitch']-(n1-n0):.2f}")
g = c['alignment']
for nm, rng in (('fin', g['fin_N']), ('returns', g['returns_N']), ('window', c['bus_edge_zone']['case_bus_window']['N']),
                ('tongue', c['bus_edge_zone']['case_tongue']['N'])):
    chk(f'{nm} inside slot N envelope', n0 <= rng[0] and rng[1] <= n1, f"{rng} in {[n0, n1]}")
r = c['retention']; ear = r['case_ear']
chk('ear inside slot N envelope', n0 <= ear['N_range_max'][0] and ear['N_range_max'][1] <= n1, f"{ear['N_range_max']}")
td = r['backplane_tower']['footprint_d_max']
chk('tower inside slot N envelope', n0 <= r['point_N'] - td/2 and r['point_N'] + td/2 <= n1, f"N {r['point_N']-td/2}..{r['point_N']+td/2}")
# guide clears socket body and header plastic
sb = c['slice_side_datums']['socket_body']
chk('fin clears socket +N face', g['fin_inner_face_N'] > sb['N'][1], f"{g['fin_inner_face_N']} > {sb['N'][1]}")
chk('returns clear socket ends', g['returns_inner_A'] > sb['A'][1], f"{g['returns_inner_A']} > {sb['A'][1]}")
chk('returns above board top', g['returns_N'][0] > c['slice_side_datums']['board_top_N'], f"{g['returns_N'][0]} > {c['slice_side_datums']['board_top_N']}")
w = c['bus_edge_zone']['case_bus_window']
chk('window contains guide A', w['A'][1] >= g['returns_A'][1] + 0.4, f"{w['A'][1]} vs {g['returns_A'][1]}")
chk('window contains guide N', w['N'][0] <= g['returns_N'][0] and w['N'][1] >= g['fin_N'][1] + 0.4, f"{w['N']} vs {g['returns_N'][0]}..{g['fin_N'][1]}")
chk('window contains guide E', w['E'][1] >= g['guide_top_E'] + 0.4, f"{w['E'][1]} vs {g['guide_top_E']}")
# E stack
s = c['slice_side_datums']; L = c['loaf_side_datums']; se = c['seat']['seat_E']
chk('socket mouth above header plastic', s['socket_mouth_E'] >= L['header_plastic_top_E'], f"float {s['socket_mouth_E']-L['header_plastic_top_E']:.2f}")
chk('pin engagement', L['header_pin_tip_E'] - s['socket_mouth_E'] >= 5.0, f"{L['header_pin_tip_E']-s['socket_mouth_E']:.2f}")
chk('guide before pins', g['guide_top_E'] - s['socket_mouth_E'] > L['header_pin_tip_E'] - s['socket_mouth_E'] + 3, f"guided {g['guide_top_E']-L['header_pin_tip_E']:.2f}")
chk('pin row E = seat + 6.0', abs(s['pin_row_E'] - (se + 6.0)) < 1e-6, f"{s['pin_row_E']}")
chk('mouth E = pin row - 10.03', abs(s['socket_mouth_E'] - (s['pin_row_E'] - 10.03)) < 1e-6, f"{s['socket_mouth_E']}")
chk('bus edge E = pin row - 3.6', abs(s['bus_edge_E'] - (s['pin_row_E'] - 3.6)) < 1e-6, f"{s['bus_edge_E']}")
chk('tongue tip clears loaf top tails (3.3)', c['bus_edge_zone']['case_tongue']['E_min'] - 3.3 >= 1.0, f"{c['bus_edge_zone']['case_tongue']['E_min']-3.3:.2f}")
# driver access vs case body ends
dd = 7.0
for f, pts in r['points_A'].items():
    lo, hi = ear['body_end_A'][f]
    for a in pts:
        clear = (lo - (a + dd/2)) if a < lo else ((a - dd/2) - hi)
        chk(f'driver clear {f} A={a}', clear >= 0.3, f"{clear:.2f}")
    fe = c['formats'][f]['bus_A_extent']
    chk(f'{f} case wall room', fe[0] - lo >= 2.0 and hi - fe[1] >= 2.0, f"{fe[0]-lo:.2f}/{hi-fe[1]:.2f} for wall+clearance")
# unused towers under other formats' case bodies must sit below the case face (rule seat+0.3)
allpts = sorted({a for p in r['points_A'].values() for a in p})
for f in r['points_A']:
    lo, hi = ear['body_end_A'][f]
    under = [a for a in allpts if lo - td/2 < a < hi + td/2 and a not in r['points_A'][f]]
    print(f"INFO  towers under the {f} case body (case face must be >= seat_E+0.3 there): {under}")
# loaf holes vs guide/tongue
chk('hole bosses clear returns', 20 - 4 >= g['returns_A'][1] + 0.5, f"boss A from 16.0 vs returns to {g['returns_A'][1]}")
print('fails', fails)
sys.exit(1 if fails else 0)
