"""Resolve one slice into case.scad parameters, board-probe parameters and a data report.

Usage: python3 -I tools/resolve.py <Slice_name> [...]   (writes resolved/<slice>.json)

One home per fact:
  slot-interface-v1.1.json     interface numbers (frame, envelope, seat, window, towers, ear)
  formats.yaml                 board-frame format rows, stopgap format inference, named exceptions
  <slice>/slice.yaml           format declaration (hardware.mounting.pattern), pcb.thickness
  modifiers/<slice>.yaml       stand-in for slice.yaml hardware.enclosure.modifiers (same shape)
  legends/<slice>.yaml         front-panel legend names (MOCK stand-in; the legend source is undecided)
  <slice>/hardware/BREAD_Slice.kicad_pcb   checks only: probe, hole fit, thickness; never the case
"""
import json, math, os, re, subprocess, sys
import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the folder holding the Slice_* clones; default: the folder that holds this repository
REPOS = os.environ.get('BREADS_REPOS') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
IFACE = json.load(open(os.path.join(HERE, 'slot-interface-v1.1.json')))
TABLE = yaml.safe_load(open(os.path.join(HERE, 'formats.yaml')))


def choose_format(name, slice_yaml):
    """The only place a format is decided: a named exception, else the declared pattern, else the stopgap."""
    exc = TABLE['exceptions'].get(name) or {}
    if 'format' in exc:
        return exc['format'], f"exception: {exc['reason']}"
    hw = slice_yaml['hardware']
    pat = hw['mounting']['pattern']
    for k, row in TABLE['formats'].items():
        if row['pattern'] == pat:
            return k, 'declared'
    k = TABLE['stopgap_dimensions'].get(hw['pcb']['dimensions'])
    if k is None:
        sys.exit(f"no format: pattern {pat!r}, dimensions {hw['pcb']['dimensions']!r}")
    return k, f'stopgap: pattern {pat!r} names no format; pcb.dimensions {hw["pcb"]["dimensions"]!r}'


# Known part heights above the top copper, for parts that leave through the far face (panel notch top and
# probe prism top). Anything not listed gets a full-height notch and a prism to the roof.
#   031-5431-1010 (Amphenol BNC jack, Slice_AQ*): a mated BNC plug, coupling sleeve ~d15 (estimate) on the
#   jack axis 7.35 above the board (0.58 in square body, KiCad STEP bounds) + 0.5 = 15.35.
HEIGHTS = {'03154311010': 15.35}
LABEL_MAX = 3          # characters per pin label: what fits vertically at 5.08 pitch
RULE_PAD = 2.0         # the rule runs this far past the outermost pad centre of its group


def panel_data(name, geom, params, f):
    """Per-slice front-panel data: the only per-slice part (L2). Notches come from the board file, legend names
    from legends/<slice>.yaml (MOCK), positions from the pads in the board file. A, N in the slot frame."""
    sd = IFACE['slice_side_datums']
    far = params['board_E'][1] + 0.3          # the fascia's back face: case.scad case_E1 = board edge + board_clear
    notches = []
    for fp in geom['fps']:
        if fp['side'] == 'F' and fp['E'][1] > far:
            h = HEIGHTS.get(fp['lib'])
            notches.append([round(fp['A'][0] - 0.5, 3), round(fp['A'][1] + 0.5, 3),
                            99.0 if h is None else round(sd['board_top_N'] + h, 3)])   # 99: full height (case.scad clamps)
    lpath = os.path.join(HERE, 'legends', name + '.yaml')
    out = {'panel_name': '', 'panel_headers': [], 'panel_labels': [],
           'panel_notches': notches, 'source': None}
    if not os.path.exists(lpath):
        return out
    leg = yaml.safe_load(open(lpath))
    by_ref = {fp['ref']: {p[0]: p[2] for p in fp['pads'] if p[0].isdigit()} for fp in geom['fps']}
    all_pads = {fp['ref']: [p[2] for p in fp['pads']] for fp in geom['fps']}
    for g in leg.get('groups', []):
        span = []
        for ref in g.get('refs', []):
            span += all_pads[ref]
        for l in g.get('labels', []):
            if len(str(l['text'])) > LABEL_MAX:
                sys.exit(f"{name}: label {l['text']!r} longer than {LABEL_MAX} characters")
            pads = by_ref[l['ref']]
            a = [pads[str(n)] for n in l['pads']] if 'pads' in l else list(pads.values())
            out['panel_labels'].append([round(sum(a) / len(a), 3), str(l['text'])])
            span += a
        out['panel_headers'].append([round(min(span) - RULE_PAD, 3), round(max(span) + RULE_PAD, 3), str(g['header'])])
    out['panel_name'] = str(leg.get('name', ''))
    out['source'] = 'legends/' + name + '.yaml'
    return out


def resolve(name):
    sy = yaml.safe_load(open(f'{REPOS}/{name}/slice.yaml'))
    fk, fsrc = choose_format(name, sy)
    f = TABLE['formats'][fk]
    sd = IFACE['slice_side_datums']; bez = IFACE['bus_edge_zone']; ret = IFACE['retention']
    E = lambda x: round(sd['pin_row_E'] - f['bus']['inset'] + x, 3)
    A = lambda y: round(y - f['bus']['y'], 3)
    N = lambda z: round(sd['board_top_N'] + z, 3)
    X, Y = f['board']; i = f['holes']['inset']
    holes = [[E(x), A(y)] for x in (i, X - i) for y in (i, Y - i)]

    pcb = f'{REPOS}/{name}/hardware/BREAD_Slice.kicad_pcb'
    geom = json.loads(subprocess.run([sys.executable, '-I', os.path.join(HERE, 'tools', 'boardgeom.py'), pcb, '--fps'],
                                     check=True, capture_output=True, text=True).stdout)
    t_kicad = float(re.search(r'\(general\s*\(thickness ([\d.]+)\)', open(pcb).read()).group(1))
    t_yaml = float(str(sy['hardware']['pcb']['thickness']).replace('mm', ''))
    board_holes = [h for h in geom['holes'] if h['d'] >= 4.5]

    exc = TABLE['exceptions'].get(name)
    if exc and exc.get('case') == 'none':
        sys.exit(f"{name}: named exception, no default case: {exc['reason']}")
    if exc and exc.get('holes') == 'from_board':
        holes = [[h['E'], h['A']] for h in board_holes]

    mods = ((sy['hardware'].get('enclosure') or {}).get('modifiers')) or {}
    mpath = os.path.join(HERE, 'modifiers', name + '.yaml')
    if os.path.exists(mpath):   # stand-in file has the slice.yaml shape
        mods = yaml.safe_load(open(mpath))['hardware']['enclosure']['modifiers'] or {}
    unknown = set(mods) - {'wall_notches', 'floor_reliefs', 'roof_windows'}
    if unknown:
        sys.exit(f'{name}: unknown modifier keys {sorted(unknown)}')
    side = {'bottom': '-A', 'top': '+A', 'far': 'far'}
    notches = [[side[n['wall']], *(map(E, n['along']) if n['wall'] != 'far' else map(A, n['along'])), *map(N, n['z'])]
               for n in mods.get('wall_notches', [])]
    reliefs = [[*map(E, r['x']), *map(A, r['y']), -1 if r['depth'] == 'through' else r['depth']]
               for r in mods.get('floor_reliefs', [])]
    windows = [[*map(E, w['x']), *map(A, w['y'])] for w in mods.get('roof_windows', [])]
    ff = (sy['hardware'].get('mcu') or {}).get('form_factor')
    acc = (TABLE.get('mcu_access') or {}).get(ff)
    # Nano USB receptacle from the board file (checks only): body on F.Fab at local x 3.81..11.43, front face
    # at local y 41.91, plug axis local +y. Footprint origin and rotation from boardgeom.
    usb = []
    for fp in geom['fps']:
        if fp['lib'] in ('Arduino_Nano', 'Arduino_Nano_Headers'):
            a = math.radians(-fp['rot'])
            r = lambda x, y: (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
            (dx, dy), (ux, uy) = r(7.62, 41.91), r(0.0, 1.0)
            usb.append({'ref': fp['ref'], 'lib': fp['lib'], 'E': round(fp['at'][0] + dx, 3),
                        'A_face': round(fp['at'][1] - dy, 3), 'dir_EA': [round(ux, 6), round(-uy, 6)]})
    # one plug-sized port per MCU USB, in the wall it faces: [side, E centre, width, N0, N1, corner r]
    wall_of = {(0.0, -1.0): '-A', (0.0, 1.0): '+A'}
    usb_ports = []
    if acc:
        for u in usb:
            st = acc['e_round']
            usb_ports.append([wall_of[tuple(u['dir_EA'])], round(round(u['E'] / st) * st, 3), acc['w'],
                              *map(N, acc['z']), acc['r']])

    params = {
        'board_E': [E(0), E(X)], 'board_A': [A(0), A(Y)], 'holes': holes,
        'ret_A': [ret['towers'][t] for t in f['towers']],
        'env_N': IFACE['slot_envelope_N'], 'seat_E': IFACE['seat']['seat_E'], 'board_top_N': sd['board_top_N'],
        'tongue_A': bez['case_tongue']['A'][1], 'tongue_E_min': bez['case_tongue']['E_min'],
        'win_A': bez['case_bus_window']['A'][1], 'win_N': bez['case_bus_window']['N'],
        'win_E_max': bez['case_bus_window']['E'][1],
        'ret_N': ret['point_N'], 'ear_t': ret['case_ear']['thickness_E'], 'ear_hole_d': ret['case_ear']['hole_d'],
        'socket_A': sd['socket_body']['A'][1], 'socket_N': sd['socket_body']['N'], 'socket_E': sd['socket_body']['E'],
        'edge_notches': notches, 'floor_reliefs': reliefs, 'roof_windows': windows, 'usb_ports': usb_ports,
        'board_r': f['corner_r'],
    }
    skip = lambda fp: fp['lib'].startswith('MountingHole') or 'PinSocket_1x10' in fp['lib']
    nano = lambda fp: fp['lib'] in ('Arduino_Nano', 'Arduino_Nano_Headers')
    # Top-side courtyards become prisms from the board top to the roof, except where a height is known:
    # [E0, E1, A0, A1] or [E0, E1, A0, A1, z0, z1] (z above the top copper).
    crt_top = [fp['E'] + fp['A'] + ([0.0, HEIGHTS[fp['lib']]] if fp['lib'] in HEIGHTS else [])
               for fp in geom['fps'] if fp['side'] == 'F' and not skip(fp) and not nano(fp)]
    # The Nano at F.Fab level instead of its courtyard bbox, which reaches 2.36 past the bottom edge on the
    # boards whose USB face is at the edge: module PCB 17.78 wide from A_face + 2.54 to + 45.72, to the roof;
    # USB receptacle 7.62 wide x 10.16 deep, z from a soldered Nano's receptacle bottom (4.1) to a socketed
    # one's top (16.6), from spec.py PLUG_Z less / plus half a 4.0 receptacle. Catalogue values, not measured.
    for u in usb:
        if u['dir_EA'] != [0.0, -1.0]:
            sys.exit(f"{name}: Nano USB not facing -A: {u}")
        crt_top.append([round(u['E'] - 8.89, 3), round(u['E'] + 8.89, 3), round(u['A_face'] + 2.54, 3), round(u['A_face'] + 45.72, 3)])
        crt_top.append([round(u['E'] - 3.81, 3), round(u['E'] + 3.81, 3), u['A_face'], round(u['A_face'] + 10.16, 3), 4.1, 16.6])
    probe = {
        'board_t': t_kicad,
        'pb_outline_E': geom['outline_E'], 'pb_outline_A': geom['outline_A'], 'pb_corner_r': geom['corner_r'],
        'pb_holes': [[h['E'], h['A'], h['d']] for h in geom['holes']],
        'pb_crt_top': crt_top,
        'pb_crt_bot': [fp['E'] + fp['A'] for fp in geom['fps'] if fp['side'] == 'B' and not skip(fp)],
    }
    panel = panel_data(name, geom, params, f)
    fit = []
    for (e, a) in holes:
        near = min(board_holes, key=lambda h: (h['E'] - e) ** 2 + (h['A'] - a) ** 2) if board_holes else None
        off = ((near['E'] - e) ** 2 + (near['A'] - a) ** 2) ** 0.5 if near else None
        fit.append({'case': [e, a], 'board': near and [near['E'], near['A'], near['d']], 'offset': None if off is None else round(off, 3)})
    rng = sd['board_thickness_range']
    report = {
        'format': fk, 'format_source': fsrc,
        'outline_vs_format': {'board_file_E': geom['outline_E'], 'board_file_A': geom['outline_A'],
                              'format_E': params['board_E'], 'format_A': params['board_A']},
        'thickness': {'slice_yaml': t_yaml, 'kicad_general': t_kicad, 'interface_range': rng,
                      'in_range': rng[0] <= t_kicad <= rng[1]},
        'outline_ok': all(abs(a - b) <= 0.3 for a, b in zip(geom['outline_E'] + geom['outline_A'],
                                                              params['board_E'] + params['board_A'])),
        'hole_fit': fit, 'max_hole_offset': max(99 if h['offset'] is None else h['offset'] for h in fit) if fit else None,
        'mcu': {'form_factor': ff, 'port': acc and f'formats.yaml mcu_access.{ff}'},
        'legend': panel['source'],
        'exception': exc, 'modifiers_source': 'modifiers/' + name + '.yaml' if os.path.exists(mpath) else 'slice.yaml',
    }
    out = {'slice': name, 'params': params, 'probe': probe, 'panel': panel, 'report': report, 'board_file': os.path.relpath(pcb, REPOS),
           'mcu_usb': usb}
    os.makedirs(os.path.join(HERE, 'resolved'), exist_ok=True)
    # one line per section; the report is printed, not stored
    with open(os.path.join(HERE, 'resolved', name + '.json'), 'w') as f:
        f.write('{\n' + ',\n'.join(f' {json.dumps(k)}: {json.dumps(v)}' for k, v in out.items() if k != 'report') + '\n}\n')
    return out


if __name__ == '__main__':
    for n in sys.argv[1:]:
        try:
            r = resolve(n)['report']
        except SystemExit as e:
            print('SKIP', e)
            continue
        print(f"{n:28s} {r['format']} t_yaml {r['thickness']['slice_yaml']} t_kicad {r['thickness']['kicad_general']}"
              f" outline_ok {r['outline_ok']} max_hole_off {r['max_hole_offset']} exc {bool(r['exception'])} ({r['format_source'][:8]})")
