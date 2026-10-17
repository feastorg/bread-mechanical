#!/bin/bash
# Usage: tools/render.sh <slice> <out.png> <scene> <camera> [extra openscad -D ...]
# camera: rx,ry,rz (framed with --viewall) or tx,ty,tz,rx,ry,rz,dist. Renders viz/scenes.scad with the slice's
# resolved parameters and panel data, as spec.py passes them. Full render (Manifold), Tomorrow colour scheme.
set -eu
D=$(cd "$(dirname "$0")/.." && pwd)
S=$1; O=$2; SC=$3; C=$4; shift 4
mapfile -t ARGS < <(python3 -I - "$D/resolved/$S.json" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
p = dict(r['params']); p.update({k: v for k, v in r['panel'].items() if k != 'source'}); p['board_t'] = r['probe']['board_t']
for k, v in p.items():
    print('-D'); print(f'{k}={json.dumps(v)}')
EOF
)
if [ "$(echo "$C" | tr -cd , | wc -c)" = 6 ]; then CAM="--camera=$C"; else CAM="--camera=0,0,0,$C,0 --autocenter --viewall"; fi
openscad --backend=Manifold --render -o "$O" --imgsize=1800,1000 $CAM --colorscheme=Tomorrow --projection=${PROJ:-p} \
    "${ARGS[@]}" -D "scene=\"$SC\"" "$@" "$D/viz/scenes.scad" 2>&1 | grep -E "WARNING|ERROR" || true
