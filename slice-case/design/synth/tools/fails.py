"""Summarise partspec reports under a directory: every non-pass check. Usage: python3 -I tools/fails.py <out dir>"""
import glob, json, os, sys
n = bad = 0
for rep in sorted(glob.glob(os.path.join(sys.argv[1], '*', 'report.json'))):
    d = json.load(open(rep)); n += 1
    part = d['part']['id'] if isinstance(d.get('part'), dict) else os.path.basename(os.path.dirname(rep))
    f = [f"{c['id']}={c['status']}" + (f" ({c['measurement']})" if c['status'] == 'fail' and c.get('measurement') is not None else '')
         for c in d['checks'] if c['status'] != 'pass']
    if f or d['verdict'] != 'pass':
        bad += 1
        print(f"{part}: {d['verdict']} {d.get('error') or ''} {'; '.join(f)}")
print(f'{n} parts, {n - bad} pass, {bad} not pass')
