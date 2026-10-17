> The STLs build into `../1-coupons/` (`../build.sh`). Run the regenerate commands below from `print/src/`. The `work/` and `renders/` outputs named below are not tracked.

# Slice case: calibration coupons v2

> 2026-10-11 (evening): four coupons added for the sliding front panel (then
> fixed: smooth detent bump, round slot ends, legend engraved), in
> "Front panel coupons" below. The first six are unchanged and were not
> re-exported: a rebuild of `insert_ladder`, `spigot_ladder`, `hole_plate` and
> `ear_ladder` from today's source is byte-identical to the STLs here.
> `stack_tray` / `stack_lid` rebuild differently, because their corner is now a
> tower (tray) and the lid has a 0.8 edge chamfer; the boss, pocket, spigot and
> counterbore they test are unchanged, so the existing pair stays.

These coupons set the four numbers the first test print left open: the
heat-set insert pocket, the lid spigot, the ear hole, and the full stack. Each
coupon is small, prints flat with no supports, and carries engraved labels
(DejaVu Sans Bold, 4.5 mm, 0.6 deep).

`coupons.scad` includes `design/synth/case.scad` and uses its parameters and
modules (`boss_d`, `insert_depth`, `spigot_recess`, `relief_d`, `head_d`,
`head_depth`, `floor_t`, `roof_t`, `xtear`, `pad_d`, `bed_chamfer`, `facets`).
Only the value under test changes per rung. The stack pair is cut out of the
real `tray()` and `lid()` with `intersection()`, as in `../print.scad`.

Every STL is already in print orientation, with the bed face at z = 0. Load
them as they are.

## Files

| File | What it is | Bed face | Size x/y/z (mm) |
|---|---|---|---|
| `insert_ladder.stl` | 6 tray bosses (Ø9) on a 1.6 roof plate. Each has the Ø5.0 x 1.0 spigot recess, an insert pocket of the rung Ø x 6.7, and a Ø3.2 relief through the floor | roof | 78.0 x 19.0 x 10.8 |
| `spigot_ladder.stl` | 6 lid bosses (Ø9, 4.83 tall) on a 1.6 floor plate. Each has a 2.0 tall spigot of the rung OD and bore, a Ø3.4 boss bore and a Ø6.0 x 3.2 head counterbore | outer face | 78.0 x 23.0 x 6.83 |
| `hole_plate.stl` | 1.6 thick printed stand-in for the slice board, with 6 Ø5.0 holes at the spigot ladder pitch (13). Hole bed edges have a 0.4 chamfer | either face | 78.0 x 18.0 x 1.6 |
| `ear_ladder.stl` | Tray ear pad (4.7 + 0.3 seat disc, 5.0 along the hole) with 4 teardrops at ret_N, plus an 18 mm roof strip. Printed exactly as the tray prints it: roof down, teardrop tip up | roof | 18.3 x 44.0 x 15.4 |
| `stack_tray.stl` | Real tray corner around hole E74.1/A-45: roof, -A wall, Ø9 boss, Ø5.0 x 1.0 recess, Ø4.0 x 6.7 pocket, Ø3.2 relief. Engraved "V2" | roof | 15.3 x 17.3 x 27.6 |
| `stack_lid.stl` | Matching real lid corner: plate, Ø9 boss, Ø4.7 spigot with the new Ø3.2 spigot bore, Ø3.4 boss bore, Ø6.0 x 3.2 counterbore. Engraved "V2" | outer face | 15.3 x 17.3 x 6.83 |

Sizes are from `partspec measure` (`work/measure-*.json`). Renders are in
`renders/`, five per coupon (iso, front, top, right, plus one section).

## Rungs

Rungs read left to right as you face the labels.

**a) `insert_ladder`**: pocket Ø, at 6.7 deep (`insert_hole_d`, `insert_depth`)

| Rung | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Label / pocket Ø | 3.8 | 3.9 | 4.0 | 4.1 | 4.2 | 4.3 |
| Boss wall | 2.60 | 2.55 | 2.50 | 2.45 | 2.40 | 2.35 |

4.0 is the vendor hole (D3) and the current `case.scad` default. 4.2 is CNC
Kitchen's as-printed figure for M3 in PLA (see Insert).

**b) `spigot_ladder`**: spigot OD / spigot bore (`spigot_d`, `spigot_bore_d`)

| Rung (hole-plate number) | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Label, top line: OD | 4.6 | **4.7** | 4.8 | 4.9 | 4.7 | 4.7 |
| Label, bottom line: bore | 3.2 | **3.2** | 3.2 | 3.2 | 3.3 | 3.4 |
| Wall (OD - bore) / 2 | 0.70 | **0.75** | 0.80 | 0.85 | 0.70 | 0.65 |
| Radial play in Ø5.0 | 0.20 | **0.15** | 0.10 | 0.05 | 0.15 | 0.15 |

Rung 2 is the new `case.scad` default. Rung 6 is the old one.

**c) `ear_ladder`**: teardrop Ø (`ear_hole_d`)

| Rung | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Label / teardrop Ø | 3.4 | 3.6 | **3.8** | 4.0 |
| M3 float, round side ((Ø - 3.0) / 2) | 0.2 | 0.3 | **0.4** | 0.5 |

3.8 is slot interface v1.1 (`retention.case_ear.hole_d`). `ear_hole_d` is an
interface value, not a case policy value. To change it, change
`slot-interface-v1.1.json` and re-run `tools/resolve.py`. Do not change it
only in `case.scad`.

**d) `stack_tray` + `stack_lid`**: no rungs. This is the real geometry at the
current defaults: insert pocket Ø4.0 x 6.7, spigot Ø4.7 / bore Ø3.2.

## Insert

**Requirement:** an M3 brass heat-set insert, knurled, for thermoplastics.
It must fit a Ø9 PETG boss (wall ≥ 2.3 around the hole), at most 5.7 long
(the pocket is 6.7 deep in the case, and a backplane boss is assumed
similar). It must take an M3 clamp screw at the torque an M3x10 socket head
needs, and must be sold by more than one vendor to one published geometry.

**Candidate:** M3 x 5.7, OD 4.6, hole Ø4.0, the "M3 standard" class.

- CNC Kitchen "M3 Standard, M3 x 5.7": L 5.7, D1 4.6, centre tip D2 3.9, hole
  D3 4.0, minimum wall W 1.6. Price about €0.10 each in packs of 100
  (https://www.3djake.com/cnc-kitchen/threaded-inserts-m3-standard).
- ruthex RX-M3x5.7: the same row (4.6 / 3.9 / 4.0 / 5.7 / 1.6) and the same
  dimension table. €8.99 per 100
  (https://www.ruthex.de/en/products/ruthex-gewindeeinsatz-m3-100-stuck-rx-m3x5-7-messing-gewindebuchsen).
- Generic: search-result listings from Albany County Fasteners, Partsbuilt
  and Accu also give Ø4.0 for M3 OD 4.6 inserts. I read these as search
  snippets and did not open the pages. Generic 4.6 OD inserts are
  interchangeable here when the length is ≤ 5.7.

Against this boss: the wall around a Ø4.0 hole is 2.5, against the vendor's
1.6 minimum. 5.7 + 1.0 = 6.7, which is the pocket depth.

**Alternates:**

| Alternate | Geometry (vendor table) | Effect on this design |
|---|---|---|
| M3 short (CNC Kitchen) | L 3.0, OD 4.6, hole 4.0 | Same pocket Ø. Half the thread engagement. Use only where depth is short, such as a thin backplane wall: set `insert_depth` 4.0 |
| M3 "Voron" (ruthex/CNC Kitchen) | L 4.0, OD 5.0, hole 4.4, W 1.3 | Pocket Ø4.4, boss wall 2.3. Needs `insert_hole_d` 4.4, `insert_depth` 5.0 and a separate ladder |
| Generic "M3 x 5 x OD4" (AliExpress/Amazon kits) | No published hole size. OD varies by seller | Not recommended as the reference part, because the geometry is not fixed |

**Pocket:** Ø4.0 (vendor D3), straight and not tapered. 6.7 deep, which is
insert + 1.0: CNC Kitchen says "A blind hole should be slightly deeper than
the length of the insert (approx. 1 mm)". There is no lead-in chamfer:
"Normally, no chamfer is required at the hole edge"
(https://www.cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts). The
existing Ø5.0 x 1.0 spigot recess above the pocket mouth already gives the
iron tip a guide.

Printed holes come out small, and on one printer CNC Kitchen measured "every
hole about 0.25 mm smaller than designed". For as-printed PLA, "4.2 mm in CAD
is the sweet spot" for M3 (CORE One L, PolySonic PLA)
(https://www.cnckitchen.com/blog/are-our-heat-set-insert-datasheets-wrong).
That is the reason for the ladder: the CAD diameter for PETG on your printer
and nozzle comes from rung a, not from the datasheet.

## Print settings

- PETG.
- 0.4 nozzle with 0.2 layers, or 0.6 nozzle with 0.3 layers.
- 100 % infill, per the BREADS solid-infill spec.
- No supports and no brim. Bed edges have a 0.4 elephant's-foot chamfer.
- Downward-facing area, from `../../design/synth/tools/overhang.py`
  (`work/overhang.txt`):
  - `spigot_ladder`: 114.8 mm² at z 3.2. These are the six Ø3.4-6.0
    counterbore ceilings, about 19 mm² each, bridged as in the lid. There is
    also 4.7 mm² at z 4.83, the 0.1-wide step from the Ø3.4 boss bore into
    the Ø3.2 spigot bore.
  - `stack_lid`: the same, for one hole: 19.1 + 1.0 mm².
  - `ear_ladder`: 1.4 mm² slices on the 0.3 proud seat-disc lower edges, plus
    0.1 mm² at each teardrop tip (the 0.02 flat).
  - `insert_ladder`, `hole_plate` and `stack_tray`: none.
- Sliced and checked: see Slicing results.

## Slicing results

PrusaSlicer 2.9.6 (flatpak, CLI), bundled PrusaResearch presets:

- 0.4: `Original Prusa MK4S 0.4 nozzle`, `0.20mm STRUCTURAL @MK4S 0.4`,
  `Prusament PETG @MK4S`.
- 0.6: `Original Prusa MK4S 0.6 nozzle`, `0.32mm STRUCTURAL @MK4S 0.6` with
  `--layer-height 0.3`, `Prusament PETG @MK4S 0.6`. There is no bundled
  0.30 mm MK4S 0.6 print preset.
- Overrides on both: `--fill-density 100% --fill-pattern rectilinear
  --no-support-material --no-binary-gcode`. The MK4S presets default to
  binary gcode. The default infill pattern refuses 100 %.

Perimeter generator: Arachne, 2 perimeters. Extrusion width: 0.45 at 0.4, 0.68
at 0.6. First layer: 0.2 at both. The gcode is in `work/gcode/`, and the
command is in `tools/slice.sh`.

| Coupon | 0.4 / 0.20: time, PETG | 0.6 / 0.30: time, PETG |
|---|---|---|
| `insert_ladder` | 29m 29s, 6.49 g | 14m 7s, 6.45 g |
| `spigot_ladder` | 19m 43s, 4.45 g | 10m 52s, 4.55 g |
| `hole_plate` | 9m 16s, 2.62 g | 5m 58s, 2.79 g |
| `ear_ladder` | 18m 36s, 5.04 g | 12m 39s, 5.13 g |
| `stack_tray` | 18m 10s, 3.15 g | 14m 2s, 3.10 g |
| `stack_lid` | 4m 24s, 0.73 g | 2m 25s, 0.75 g |
| All six | 1h 39m 38s, 22.48 g | 1h 0m 3s, 22.77 g |

Times are the gcode's `estimated printing time (normal mode)`. Weights are
`filament used [g]`.

**How the thin features were checked.** `tools/gcheck.py` reads each gcode,
including the G2/G3 arcs that the presets' `arc_fitting = emit_center`
emits. It places the STL frame on the bed by matching bounding-box centres,
then, in every layer of each feature's z range, collects the extrusion
segments whose midpoints fall inside the feature's region. For each layer it
reports the paths by `;TYPE` and the extrusion width, recovered from E per
mm with PrusaSlicer's flow model. The output is
`work/gcode/thin-features.txt`, and the regions are in `tools/specs.py`.

| Feature | 0.4 / 0.20 | 0.6 / 0.30 |
|---|---|---|
| Spigot wall, 3.2 bores (0.70-0.85), all ladder rungs and `stack_lid` | 2 loops per layer, 0.36-0.45 wide, all 10 layers | 1 loop per layer, 0.68-0.87 wide, all 7 layers |
| Spigot wall, old 4.7/3.4 (0.65) | 1 loop, 0.64-0.66 wide | 1 loop, 0.63-0.67 wide |
| Insert boss walls (2.35-2.6), all rungs and `stack_tray` | 3-4 perimeter paths per layer plus solid infill, every layer | 3-4 perimeter paths per layer (0.57-0.87 wide), every layer |
| Teardrop tips (ear ladder) | The hole centreline stays open to z 13.0 / 13.2 / 13.2 / 13.4 for Ø3.4 / 3.6 / 3.8 / 4.0. The tips are 12.80 / 12.95 / 13.09 / 13.23, and the round tops would close at 12.10-12.40 | Open to 13.1 / 13.1 / 13.4 / 13.4 |
| Engraved labels (all) | Letter-outline perimeters in every groove layer (z 1.2, 1.4, 1.6) | Letter-outline perimeters in both groove layers (z 1.4, 1.7). Layer 1.1 is solid under the groove, as designed |
| Hole-plate holes | 1-2 perimeters per layer | 1 perimeter per layer from z 0.5. On the first layer the hole sits inside the 0.4 chamfer and was not separately checked |

No feature is dropped at either nozzle, so no parameter changes are needed for
0.6. In every rung the spigot is one full-width 0.6 loop, so the 0.75 wall
prints solid but is still one line thick. That is the limit of a Ø5.0 board
hole, as covered in the spigot decision.

PrusaSlicer printed one warning, for `hole_plate` at 0.6: "Detected missing
Voronoi vertex, input polygons will be rotated back and forth". That is an
Arachne retry; the slice completed and its holes and labels check as above.

## How to read each coupon and what it sets

**a) `insert_ladder` sets `insert_hole_d`.**
1. With the iron 10-20 °C above your PETG print temperature (CNC Kitchen),
   try each pocket. Pick the smallest rung where the insert
   pre-seats in the mouth by hand "with a bit of resistance", goes in square
   to flush with the recess floor, and leaves no bulge or crack in the boss
   wall.
2. Then drive an M3 into that insert and torque it firmly. It must not spin
   or pull out.
3. Calipers on the printed pockets give your printer's hole shrink. Record it.

Set `insert_hole_d` to the winning rung's label value. Do the same in the
backplane part.

**b) `spigot_ladder` + `hole_plate` set `spigot_d` and `spigot_bore_d`.**
1. Calipers on each spigot OD. Record it.
2. Test one spigot at a time, on the real slice board's Ø5.0 holes first, then
   on the printed plate. The winning OD is the largest that drops in by hand
   without force and seats the board flat on the boss face.
3. An M3 must pass each bore. A 3.2 bore that binds or self-threads means you
   should take 3.3, or ream it with a 3.2 drill.
4. Push each spigot sideways with a finger after the board is on. Note any
   rung that cracks.

The ladder tests local fit only. Hole-to-hole span errors (the printed lid
shrinking over the 60 x 90 hole pattern, plus ±0.075 hole position on the PCB)
need the full lid on a real board. Leave at least 0.1 radial play on top of
what the coupon shows.

**c) `ear_ladder` sets the interface `ear_hole_d` (in `slot-interface-v1.1.json`).**
1. The tip prints clean and the round part is round.
2. An M3 passes each hole. Pick the smallest that an M3 passes freely with
   ≥ 0.3 float each way. The tower guide sets slice position, so the screw
   only clamps.

**d) `stack_tray` + `stack_lid` confirm the current defaults together.**
1. Install an insert in `stack_tray`.
2. Stack tray, real slice board, `stack_lid`, with the spigot through the board
   hole.
3. Drive an M3x10 from the lid face. It pulls tight with no gap at the boss
   faces, the screw head sits below the lid face, and the spigot tip does not
   touch the insert (designed margin 0.6).

## Front panel coupons (2026-10-11)

All from `coupons.scad`, cut from the real `tray()` / `panel()` or built from
case values. Downward-facing area from `design/synth/tools/overhang.py`.

| File | What it is | Bed face | Size x/y/z (mm) | Overhang |
|---|---|---|---|---|
| `slide_tray.stl` | Both far corners of the tray, top 4.6: V grooves, groove mouths and the detent notches. The -A corner is moved 64.4 toward +A, so the opening is 16 wide | roof | 15.4 x 40.2 x 4.6 | 23.0 mm² |
| `slide_panel.stl` | Both corners of the blank panel, moved the same way: roof strip with V tongues, spring fingers with round-ended slots, bumps, fascia corners | roof strip | 14.2 x 37.9 x 29.6 | 4.3 mm² |
| `legend_strip.stl` | A -24.5..7.5 of the Slice_RLHT panel (the RELAY 2 block), legend engraved 0.6 | roof strip | 4.0 x 32.0 x 15.9 | 58.0 mm² |
| `tilt_jig.stl` | The packed neighbour's lid face: the lid's plan and outer chamfer from E 45 to the far face, 1.6 thick, carried 0.8 (slot pitch 30.4 less the 29.6 case) above the roof on two spacer strips, with lips outside both side walls | plate face | 34.4 x 109.2 x 6.4 | 0 |

**e) `slide_tray` + `slide_panel` check the V-groove clearance (0.2) and the
detent.** Slide the panel coupon into the tray coupon from the far end.
- It runs without force and does not rock in A or N. If it binds, raise
  `pan_gap` in `case.scad`; if it rocks, lower it.
- At the end of travel each bump rides over its groove wall (0.80 overlap in A,
  taken by the finger) and drops into its notch: a click. Shut, the pair stays
  together shaken roof down. `bump` and `bump_ax` in `case.scad` set it.
- Check the finger roots after 20 cycles: no whitening at the round slot ends.
- Print the pair at every nozzle you use: 0.2 is a third of a 0.6 line.

**f) `legend_strip` checks the legend.** Strokes: DejaVu Sans Condensed Bold
3.0, grown 0.2, so no stroke is under 0.8 (`spec.py` `probe_legend_thin`),
engraved 0.6. Read it at arm's length in room light, at each nozzle.

**g) `tilt_jig` answers CRITIQUE.md §0: can a packed slice be re-terminated in
place?** Take the panel off a Slice_RLHT case, set the jig on the roof with its
plate edge flush with the far face, and try each MKDS screw with a 3 mm flat
blade passing under the plate edge (about 36° from the screw axis). Record
whether the blade seats and turns a full turn, and whether it cams out. Pulling
the slice (2 ear screws) is the accepted fallback either way.

## Checklist

- [ ] e: slide and click at each nozzle; record bind, rock, click, holds, and
      the finger roots after 20 cycles.
- [ ] f: legibility at each nozzle.
- [ ] g: MKDS drive under the jig: pass or fail, and the angle used.
- [ ] Print all six at 0.4/0.2, and again at 0.6/0.3 if both nozzles will
      be used. Keep them separate and mark the nozzle on each.
- [ ] a: record each pocket Ø, the winning rung, and torque pass or fail.
      Then set `insert_hole_d`.
- [ ] b: record each spigot OD, the fit on the real board for each rung, any
      M3 bind in the 3.2/3.3 bores, and any cracks. Then set `spigot_d` and
      `spigot_bore_d`.
- [ ] c: record tip quality and the M3 float for each rung. If 3.8 is wrong,
      raise it as an interface change.
- [ ] d: stack test pass or fail, flush head, no gap.
- [ ] After changing a default: run the `spec.py` checks and
      `python3 -I tools/mutate.py` from `design/synth/`, then regenerate this
      set.

## Regenerating

From this directory:

```
partspec check coupons_spec.py:<target> --out work/check
partspec measure coupons_spec.py:<target> --out <target>.stl
partspec render coupons_spec.py:<target> --out work/render/<target> --section yz:<x>
```

Targets: `insert_ladder`, `spigot_ladder`, `hole_plate`, `ear_ladder`,
`stack_tray`, `stack_lid`, `slide_tray`, `slide_panel`, `legend_strip`,
`tilt_jig`. Each one checks that the part is watertight, is
one solid, and has nothing below z = 0. The section planes used were yz:0
(insert), yz:13 (spigot), yz:9 (ear, through the pad) and yz:74.1 (stack). The
labels need the DejaVu Sans Bold font on the machine that runs OpenSCAD.

## Running the slicer

`tools/slice.sh` runs the PrusaSlicer flatpak (`flatpak run`; set
`FLATPAK_RUN` to use a wrapper instead).

The bundled MK4S presets resolve only when the printer model is installed in
the slicer's datadir. If it is not, `--printer-profile` falls back silently to
another printer: one trial produced gcode for `Creality CR-10 SMART` with
`E3D PC-ABS`.

`tools/slice.sh` therefore passes `--datadir "$PRUSA_DATADIR"`: a directory
holding a copy of the bundled `vendor/PrusaResearch.ini` (plus `.idx` and the
`PrusaResearch/` folder). Run it as
`PRUSA_DATADIR=<dir> tools/slice.sh <stl-dir> <out-dir> <name>...`.
The datadir also holds a two-line `PrusaSlicer.ini`:

```
[vendor:PrusaResearch]
model:MK4S = 0.4;0.6
```

Every gcode here was checked for `printer_settings_id`,
`filament_settings_id` and `print_settings_id`. Pipe the slicer's output (as
`| cat > log`): with stdout redirected straight to a file, the run is cut off
mid-slice with exit 0 and no gcode.
