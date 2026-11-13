# SPDX-License-Identifier: GPL-3.0-or-later
"""Print every spec.py target, for `partspec check $(python3 -I tools/targets.py)` from sbc-case/."""
import ast
import os

src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'spec.py')).read()
names = ast.literal_eval(src.split('for n in ', 1)[1].split(']', 1)[0].strip().rstrip(')') + ')')
print(' '.join(f'spec.py:{n}' for n in names))
