"""Print the spec.py contract targets (not the render-only ones). Usage: partspec check $(python3 -I tools/targets.py)"""
CASE = ['tray', 'lid', 'assembly', 'probe_board', 'probe_board_only', 'probe_parts', 'probe_below_seat']
PANEL = ['panel', 'panel_swept', 'probe_panel_closed', 'probe_panel_lid', 'probe_panel_slide', 'probe_panel_shift',
         'probe_panel_locate_A', 'probe_panel_locate_N', 'probe_detent', 'probe_legend_thin', 'probe_legend_off_face']
T = [f'spec.py:{k}_{f}' for k in ('nano', 'nucl', 'dcmt', 'rlht', 'aqph') for f in CASE]
T += [f'spec.py:{k}_{f}' for k in ('rlht', 'aqph') for f in PANEL]
T += ['spec.py:nano_panel_blank', 'spec.py:nano_assembly_nominal', 'spec.py:nano_assembly_tmax']
print(' '.join(T))
