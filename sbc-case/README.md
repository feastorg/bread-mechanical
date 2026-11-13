# SBC cases and extrusion mount

Cases for the single-board computers that run a BREAD, and a plate that holds one on 2020 aluminium
extrusion. The controller stands beside the Loaf, cabled to it, as on G1 and G2.

The cases are [SBC Case Builder](https://github.com/hominoids/SBC_Case_Builder)'s `shell` design, generated
from board data in [SBC Model Framework](https://github.com/hominoids/SBC_Model_Framework). Both are pinned
in `../scadman.toml` and used unmodified. This folder adds two things:

- **A GPIO window in the lid roof.** Jumpers to the Loaf plug in with the lid on. Case Builder's own
  `gpio_opening = "open"` cuts only the side wall, leaving the roof closed over the header.
- **An extrusion mount.** A plate under the case, which the case's own four M2.5 screws pass through on
  their way to the lid's heat-set inserts. Two M5 screws into T-nuts hold it on the extrusion, which runs
  across the board's short side, under the middle of the hole pattern.

Status (2026-11): designed and checked for the Pi 4B, 3A+ and Zero 2 W; not yet printed. SBC Model
Framework marks all three boards "yellow, unverified", so the first print is a fit test (`print/README.md`).

## What is here

| Path | What |
|---|---|
| `sbc_case.scad` | The parts: `part = "lid"`, `"bottom"`, `"mount"`, `"coupon"`, `"assembly"`. Includes Case Builder, switches its own view off, and places its parts |
| `boards.json` | Case Builder settings per board: shell, roof vents on the 4B and 3A+ (solid roof on the Zero 2 W), M2.5 heat-set inserts in the lid standoffs, M2.5 clearance through the bottom |
| `spec.py` | partspec checks for every part on every board, and where each limit comes from |
| `tools/board_data.scad` | Echoes the board data and case dimensions `spec.py` places its checks with |
| `tools/targets.py` | Prints every `spec.py` target |
| `tools/mutate.py` | Mutation sweep: each mutation must fail its check |
| `build.sh` | Builds every STL into `print/` |
| `print/README.md` | What to print, settings, hardware, and the fit test |

## Building

Requirements: OpenSCAD with the Manifold backend (tested on 2026.10.15), scadman, partspec (tested on
0.7.8), Python 3.

```
scadman sync              # once, at the repository root
bash sbc-case/build.sh    # STLs into sbc-case/print/1-coupons and 2-cases (not tracked)
```

Every STL is in print orientation with its bed face at z = 0.

To view a part in OpenSCAD, put the scadman environment on the path and pass the board's settings as `-D`
values. OpenSCAD's `-p boards.json` does not work here, because it does not reach variables that come in
through `include`:

```
OPENSCADPATH=$(scadman env) openscad -D 'sbc_model="rpi4b"' -D 'case_design="shell"' \
    -D 'top_standoff_insert=true' -D 'part="assembly"' sbc-case/sbc_case.scad
```

## Checks

From `sbc-case/`:

```
partspec check $(python3 -I tools/targets.py)
python3 -I tools/mutate.py    # each mutation must fail its check
```

What is checked, per board:

- **Lid**: watertight, one solid; the GPIO pin field is open through the roof; the window leaves every top
  standoff's wall intact; each standoff has room for an M2.5 x 4.0 insert; the header-side wall is whole along
  its length.
- **Bottom**: watertight, one solid; an M2.5 screw passes the floor and standoff at every board hole.
- **Mount**: watertight, one solid, six through-holes; the M2.5 shank and ISO 4762 head fit; the head seats at
  the depth the screw stack sets (below); the M5 shank and head fit, the head below the plate's top face;
  where the extrusion bears, the underside is solid.
- **Coupon**: every rung has room for the insert's length.

## Design decisions

- **Case Builder unmodified.** BREAD's changes are made around its parts (`case_top()`, `case_bottom()`),
  not in its files, so an upstream update is a pin bump in `../scadman.toml`.
- **scadman does not fetch git submodules**, so SBC Model Framework is its own pin, at the commit Case
  Builder's submodule records. Case Builder's `./SBC_Model_Framework/...` includes still resolve, through
  `OPENSCADPATH`.
- **Bottom holes are `m2.5+`.** Case Builder's `m2.5` makes the hole exactly 2.5 mm, the screw's own major
  diameter; the contract's screw-path check failed on it. `m2.5+` is Case Builder's clearance size.
- **The GPIO window keeps a 0.5 mm ring around each lid standoff**, following the standoff's hex. On the
  header side the hex flat plus the ring ends at x = 7.0, where the pin field starts. A round keep-out of the
  same size covered the outer 0.46 mm of the pin field; the gpio-window check failed on it.
- **Screw stack.** The lid's inserts start at the top standoff face, which Case Builder puts at the board's top
  face as modelled (`bottom_height` above the case floor). An M2.5 x 16 reaching 3.5 mm into the insert leaves
  `16 - bottom_height - 3.5` of shank in the 8 mm plate; the head counterbore takes the rest: 4.5 mm on the 4B
  and 3A+ (`bottom_height` 9), 2.5 mm on the Zero 2 W (7), equal to the ISO 4762 head height. The real board's
  thickness does not change this, because the insert's position is fixed in the lid.
- **Extrusion across the short side.** All three boards have their holes 58 mm apart in x, so the M2.5 heads
  sit well clear of a 20 mm face. Along the long side, the Zero's heads (23 mm apart) would sit at the
  extrusion's edge.
- **Solid roof on the Zero 2 W.** Its pin field ends 0.4 mm from the board edge, so the window leaves almost
  no roof beside the wall, and Case Builder's hex roof pattern (which covers the whole roof) then cut the
  header-side wall into posts. The Zero runs cool at control loads; its roof keeps only the window. The
  header-wall check fails on the hex pattern.
- **GPIO access is for jumpers.** The two header-side standoffs are 52 mm apart (4B, 3A+): a 40-pin IDC
  connector's body is longer than that and cannot reach the header with the lid on.

## Not yet verified

- Board models: Case Builder's openings and standoffs follow SBC Model Framework's data, which upstream marks
  unverified for all three boards. It models the board as 1.0 mm thick.
- M2.5 insert hole: 3.7 mm is a starting value from an unofficial source; the coupon decides it.
- Print fit and the screw stack on real hardware.
