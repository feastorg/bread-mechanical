#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Build every print STL from source into print/1-coupons/ and print/2-cases/ (STLs are not tracked).
# Needs scadman (dependencies synced: `scadman sync` at the repo root), partspec and OpenSCAD with the
# Manifold backend. Run from anywhere: bash sbc-case/build.sh
set -eu
P=$(cd "$(dirname "$0")" && pwd)
# Case Builder's sources contain import() calls (for its accessories), so partspec will not write an STL
# where the model could be reading one: each part is built into a fresh empty directory, then moved.
T=$(mktemp -d "${TMPDIR:-/tmp}/sbc-case-build.XXXXXX")
trap 'rm -rf -- "$T"' EXIT
build() {   # <out dir> <target>[=<file name>]...
    local sub=$1 out=$P/print/$1; shift
    mkdir -p "$out"
    for e in "$@"; do
        local t=${e%%=*} f=${e#*=} d
        d=$(mktemp -d "$T/part.XXXXXX")
        (cd "$P" && partspec measure "spec.py:$t" --out "$d/" > /dev/null)
        mv "$d/sbc_case.stl" "$out/$f.stl"
        echo "print/$sub/$f.stl"
    done
}
build 1-coupons coupon=insert_coupon
build 2-cases lid_rpi4b=rpi4b_lid bottom_rpi4b=rpi4b_bottom mount_rpi4b=rpi4b_mount_2020 \
    lid_rpi3a=rpi3a+_lid bottom_rpi3a=rpi3a+_bottom mount_rpi3a=rpi3a+_mount_2020 \
    lid_rpizero2w=rpizero2w_lid bottom_rpizero2w=rpizero2w_bottom mount_rpizero2w=rpizero2w_mount_2020
