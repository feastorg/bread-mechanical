#!/usr/bin/env bash
# Break backplane.scad one value at a time and check that the named probe fails. Restores the file after each.
# Prints KILLED (target among the failures), SURVIVED, or BROKEN (anchor not found exactly once / file unchanged).
# Run from this directory: bash mutate.sh <scratch dir>
set -u
S="$1"; F=backplane.scad
cp "$F" "$S/backplane.orig.scad"; H0=$(sha1sum "$F" | cut -c1-12)
ALL="probe_loaf probe_above clash_rlht clash_nano clash_nano_t14 clash_nano_t18 clash_nucl_l"
run() {
    local name="$1" from="$2" to="$3" target="$4"
    python3 -I -c "
import sys; p, a, b = sys.argv[1:4]; s = open(p).read(); n = s.count(a)
sys.exit(f'anchor x{n}') if n != 1 else open(p, 'w').write(s.replace(a, b))" "$F" "$from" "$to" \
        || { echo "BROKEN   $name (anchor)"; return; }
    [ "$(sha1sum "$F" | cut -c1-12)" = "$H0" ] && { echo "BROKEN   $name (unchanged)"; cp "$S/backplane.orig.scad" "$F"; return; }
    local T=""; for t in $ALL; do T="$T spec.py:$t"; done
    partspec check $T --out "$S/mut" > "$S/mut.txt" 2>&1
    local failed=""
    for t in $ALL; do
        grep -q '"verdict": "pass"' "$S/mut/spec-$t/report.json" 2>/dev/null || failed="$failed $t"
    done
    cp "$S/backplane.orig.scad" "$F"
    case " $failed " in *" $target "*) echo "KILLED   $name -> failing:$failed";; *) echo "SURVIVED $name -> failing:${failed:- none}";; esac
}
run "plate 5.0, into the case tongue" "plate_t = 4.0;" "plate_t = 5.0;" clash_rlht
run "towers 7.2 tall" "tower_top_E = 6.7; " "tower_top_E = 7.2; " clash_rlht
run "towers 2 off in A (T3)" "towers = [-56.4, 56.4, 101.4];" "towers = [-56.4, 56.4, 99.4];" clash_rlht
run "fin 0.3 into the socket" "fin_N = [1.42, 5.42];" "fin_N = [1.12, 5.42];" clash_rlht
run "guide 1 wider than the case window" "ret_A1 = 14.9;" "ret_A1 = 15.9;" clash_rlht
run "no tail cutouts" "tail_clear = 0.5;" "tail_clear = -3;" probe_loaf
run "header window closed on -N" "hdr_N0 = -1.77;" "hdr_N0 = 1.0;" probe_loaf
run "rails 7.0 tall" "rail_t = 6.0;" "rail_t = 7.0;" probe_above
run "bosses 7.0 tall" "boss_t = 6.4;" "boss_t = 7.0;" probe_above
echo "restored $F $(sha1sum "$F" | cut -c1-12) (was $H0)"
