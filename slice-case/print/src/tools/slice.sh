#!/usr/bin/env bash
# usage: slice.sh <stl-dir> <out-dir> <name>...   slices <stl-dir>/<name>.stl at 0.4/0.20 and 0.6/0.30
set -u
S=${PRUSA_DATADIR:?set PRUSA_DATADIR to a datadir holding vendor/PrusaResearch.ini and the two-line PrusaSlicer.ini (see README)}
read -r -a RUN <<< "${FLATPAK_RUN:-flatpak run}"   # override if flatpak needs a wrapper on your host
src=$1; out=$2; shift 2
mkdir -p "$out"
for n in "$@"; do
  for nz in 04 06; do
    if [ $nz = 04 ]; then
      P=(--printer-profile "Original Prusa MK4S 0.4 nozzle" --print-profile "0.20mm STRUCTURAL @MK4S 0.4" --material-profile "Prusament PETG @MK4S")
    else
      P=(--printer-profile "Original Prusa MK4S 0.6 nozzle" --print-profile "0.32mm STRUCTURAL @MK4S 0.6" --material-profile "Prusament PETG @MK4S 0.6" --layer-height 0.3)
    fi
    timeout 900 "${RUN[@]}" com.prusa3d.PrusaSlicer --datadir "$S" --loglevel 2 "${P[@]}" \
      --fill-density 100% --fill-pattern rectilinear --no-support-material --no-binary-gcode \
      --export-gcode --output "$out/${n}_n$nz.gcode" "$src/$n.stl" 2>&1 | cat > "$out/${n}_n$nz.log"
    echo "$n n$nz rc=${PIPESTATUS[0]} $(grep -c 'Slicing result exported' "$out/${n}_n$nz.log")"
  done
done
