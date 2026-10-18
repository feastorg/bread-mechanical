#!/usr/bin/env bash
# Build every print STL from source into 1-coupons/, 2-cases/ and 3-backplane/ (STLs are not tracked).
# Needs partspec and OpenSCAD with the Manifold backend. Run from anywhere: bash print/build.sh
set -eu
P=$(cd "$(dirname "$0")" && pwd)
build() {   # <spec dir> <spec file> <out dir> <target>[=<file name>]...
    local dir=$1 spec=$2 sub=$3 out=$P/$3; shift 3
    mkdir -p "$out"
    for e in "$@"; do
        local t=${e%%=*} f=${e#*=}
        (cd "$dir" && partspec measure "$spec:$t" --out "$out/$f.stl" > /dev/null)
        echo "$sub/$f.stl"
    done
}
build "$P/src" coupons_spec.py 1-coupons insert_ladder spigot_ladder hole_plate ear_ladder stack_tray stack_lid \
    slide_tray slide_panel legend_strip tilt_jig
build "$P/src" print_spec.py 2-cases s_tray_nano_a=s_tray_nano-a s_tray_nano_b=s_tray_nano-b s_lid panel_rlht panel_aqph panel_blank usb_plug
build "$P/../design/backplane" spec.py 3-backplane backplane stand_foot
