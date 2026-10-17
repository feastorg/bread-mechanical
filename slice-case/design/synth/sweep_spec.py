"""Every resolved slice through the default case (plus its modifiers and panel data): board probe, assembly, panel.
Targets: sweep_spec.py:p_<i> (probe_board), a_<i> (assembly), n_<i> (panel); i follows sorted resolved/*.json."""
import glob
import os

import spec

NAMES = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(spec.HERE, 'resolved', '*.json')))
for _i, _n in enumerate(NAMES):
    globals()[f'p_{_i}'] = (lambda n=_n: spec.probe_board(n))
    globals()[f'a_{_i}'] = (lambda n=_n: spec.assembly(n))
    globals()[f'n_{_i}'] = (lambda n=_n: spec.panel(n))
