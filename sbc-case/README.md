# SBC cases and extrusion mount

Cases for the single-board computers that run a BREAD, and a plate that holds one on 2020 aluminium
extrusion. The controller stands beside the Loaf, cabled to it, as on G1 and G2.

The cases are [SBC Case Builder](https://github.com/hominoids/SBC_Case_Builder)'s `shell` design, generated
from board data in [SBC Model Framework](https://github.com/hominoids/SBC_Model_Framework). Both are pinned
in `../scadman.toml` and used unmodified. This folder adds two things:

- **A GPIO window in the lid roof.** Jumpers to the Loaf plug in with the lid on. Case Builder's own
  `gpio_opening = "open"` cuts only the side wall, leaving the roof closed over the header.
- **A case that comes off its mount closed.** Four countersunk M2.5 screws close the case on their own, up
  through the floor into the lid's heat-set inserts. Two ears on the bottom, one past each short end, take an
  M3 screw each down into an insert in the mount.
- **An extrusion mount.** A plate under the case and its ears. Two M5 screws into T-nuts hold it on the extrusion, which runs
  across the board's short side, under the middle of the hole pattern.

Status (2026-11): designed and checked for the Pi 4B, 3A+ and Zero 2 W. The Pi 4B case was printed and fitted
to a real board: everything fit except the bottom standoffs, which stood too tall and printed poorly (fixed
since, below). The 3A+ and Zero 2 W are not printed yet; SBC Model Framework marks all three boards "yellow,
unverified", so each first print is a fit test (`print/README.md`).

## What is here

| Path | What |
|---|---|
| `sbc_case.scad` | The parts: `part = "lid"`, `"bottom"`, `"mount"`, `"coupon"`, `"assembly"`. Includes Case Builder, switches its own view off, and places its parts |
| `boards.json` | Case Builder settings per board: shell, roof vents on the 4B and 3A+ (solid roof on the Zero 2 W), M2.5 heat-set inserts in the lid standoffs, countersunk M2.5 clearance through the bottom |
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
  standoff's wall intact; nothing hangs over the window up to the standoff collars' height; a roof strip
  separates the window from the vents; each standoff has room for an M2.5 x 4.0 insert; the header-side wall is
  whole along its length.
- **Bottom**: watertight, one solid; the header-side wall is whole, floor to rim; each standoff leaves 1.6 mm
  for the board and has a 1.2 mm wall round its hole; an M2.5 screw passes the floor and standoff at every board
  hole, and its
  countersunk head (ISO 7046-1, dk 4.7) goes into the floor; the case screw's reach into the lid insert is
  2.5 mm to the insert's length; an M3 passes each ear, the ear is whole around it, and the M3 head clears the
  case's end wall.
- **Mount**: watertight, one solid, two through-holes (the T-nut screws); an M3 x 5.7 insert fits under each
  ear, in a blind pocket; the M5 shank and head fit, the head below the plate's top face; where the extrusion
  bears, the underside is solid.
- **Coupon**: every rung has room for the insert's length.

## Design decisions

- **Case Builder unmodified.** BREAD's changes are made around its parts (`case_top()`, `case_bottom()`),
  not in its files, so an upstream update is a pin bump in `../scadman.toml`.
- **scadman does not fetch git submodules**, so SBC Model Framework is its own pin, at the commit Case
  Builder's submodule records. Case Builder's `./SBC_Model_Framework/...` includes still resolve, through
  `OPENSCADPATH`.
- **Bottom standoffs: Case Builder's `custom` size, lowered for the real board.** All in `boards.json`, no
  code. Case Builder's `m2.5` and `m2.5+` sizes fix the pillar at 4 mm across, which round the 2.83 mm hole
  is a 0.6 mm wall; it printed poorly on the 4B. `custom` takes `bottom_standoff_diameter` (5.5, round: about
  a 1.3 mm wall, inside the 6 mm pad round each mounting hole on Raspberry Pi's 4B drawing) and
  `bottom_standoff_hole_size` (2.83, `m2.5+`'s clearance hole; Case Builder's `m2.5` is exactly the screw's
  2.5 major diameter, which the screw-path check fails). Its countersink is then 6.16 wide and 1.32 deep
  (103°, Case Builder's `2 x hole + 0.5` and `0.465 x hole`), so a 90° M2.5 head bottoms on the hole's edge
  about 0.4 below the floor. SBC Model Framework models the boards 1.0 thick (`pcb_z`), and Case Builder stops
  the pillars under that. The Pi 4B's board measures 1.4; the four `bottom_*_adjust` values drop the pillars
  0.6, leaving 1.6 for it: 0.2 of allowance, chosen at the bench. The 3A+ and Zero 2 W get the same drop,
  unmeasured.
- **A member between the GPIO window and the vents.** Case Builder's vent slots ran into the window, which
  left each vent bar held at one end only, a 2 mm comb tooth with its tip free at the window. A 3 mm roof
  strip (`sc_member_w`) now closes the slots short of the window, so each bar is held at both ends.
- **The window cuts through the standoff collars.** It used to reach 1 mm into the lid, which left 3 mm of
  Case Builder's 10 mm standoff collar hanging over the opening as printed (19.3 mm² facing down on the 4B).
  It now runs the collar's full height (`top_standoff_support_height`).
- **Wall openings run out to the rim.** Case Builder's port openings and the indents around them stop short of
  the rim, which left the wall curling over each port as printed: thin lips at the rim of each lid (4.2 mm² on
  the 4B, 17.0 mm² on the 3A+, including a 0.5 mm thick sliver over the 3A+ HDMI port) and a bridge over the
  SD-card slot in the 4B and 3A+ bottoms (28.4 mm²). `sc_open_to_rim()` sweeps every void in the side walls
  straight out to the rim at its own width: through openings through the whole wall, indents at their own
  depth. It samples each wall inside its material, never the air beside it; sampling the air removed the
  walls whole, which the bottom's header-wall check now catches. Downward-facing area off the bed is now 0.0 mm² on every lid and
  bottom (`../slice-case/design/synth/tools/overhang.py <stl> +z`). partspec has no overhang check yet
  (heibench/partspec#455), so nothing in `spec.py` holds this.
- **The GPIO window keeps a 0.5 mm ring around each lid standoff**, following the standoff's hex. On the
  header side the hex flat plus the ring ends at x = 7.0, where the pin field starts. A round keep-out of the
  same size covered the outer 0.46 mm of the pin field; the gpio-window check failed on it.
- **The case comes off its mount closed.** The case screws used to pass through the mount, so taking the case
  off the mount opened it. Now the case screws are countersunk M2.5 into Case Builder's countersunk floor
  holes (`bottom_standoff_type`, pinned in `boards.json`), and the case fastens to the mount by two ears with
  an M3 screw each, undone from above. The ears are 4 mm thick at floor level and centred on each end; where
  each meets its end wall, the wall is solid on all three boards, so no opening is narrowed.
- **Screw stack.** The lid's inserts start at the top standoff face, which Case Builder puts at the board's top
  face as modelled (`bottom_height` above the case floor), and a countersunk head ends at the floor's
  underside, so a screw of length l reaches `l - bottom_height` into the insert. The model takes the longest
  stock length that reaches 2.5 mm without passing the pocket: M2.5 x 12 on the 4B and 3A+ (`bottom_height`
  9), M2.5 x 10 on the Zero 2 W (7), 3 mm into the insert as modelled, less however far the head sits below the
  floor (Case Builder's countersink is 72°, ISO 7046 heads are 90°). The real board's thickness does not change this,
  because the insert's position is fixed in the lid.
- **Ear inserts are slice-case's.** M3 x 5.7 heat-set inserts in a 4.0 x 6.7 pocket: the pocket slice-case's
  printed case already uses.
- **Extrusion across the short side.** The extrusion runs along y, under the middle of the hole pattern, so
  the T-nut screws sit between the case screws and the ears sit well clear of the 20 mm face.
- **Solid roof on the Zero 2 W.** Its pin field ends 0.4 mm from the board edge, so the window leaves almost
  no roof beside the wall, and Case Builder's hex roof pattern (which covers the whole roof) then cut the
  header-side wall into posts. The Zero runs cool at control loads; its roof keeps only the window. The
  header-wall check fails on the hex pattern.
- **GPIO access is for jumpers.** The two header-side standoffs are 52 mm apart (4B, 3A+): a 40-pin IDC
  connector's body is longer than that and cannot reach the header with the lid on.

## Not yet verified

- Board models: Case Builder's openings and standoffs follow SBC Model Framework's data, which upstream marks
  unverified for all three boards. It models the board as 1.0 mm thick; the bottom standoffs leave 1.6, a 1.4 mm
  board measured on the 4B only plus 0.2.
- M2.5 insert hole: 3.7 mm is a starting value from an unofficial source; the coupon decides it.
- Print fit on the 3A+ and Zero 2 W, and the 4B's reprinted bottom.
