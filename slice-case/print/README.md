# What to print

PETG, 100 % infill (BREADS "solid infill"), no supports, on a 0.4 nozzle (0.20
layers) or a 0.6 (0.30 layers). Every STL is in print orientation with its bed
face at z = 0: load it without rotating. Slice by hand; nothing here is sliced.
`bash build.sh` builds every STL below from source.

## 1. Coupons: `1-coupons/`

| File | What to do with it | Records |
|---|---|---|
| `insert_ladder.stl` | Press an M3 heat-set insert into each pocket (Ø3.8 to 4.3, labelled). Take the smallest that goes in square, sits flush and does not spin under an M3. | Insert hole Ø |
| `spigot_ladder.stl` + `hole_plate.stl` | Push each spigot into its numbered Ø5.0 hole, then into a real slice board's mounting hole. Pass an M3 through each bore. | Spigot OD and bore |
| `ear_ladder.stl` | Pass an M3 through each teardrop (Ø3.4 to 4.0); it should float about ±0.4. | Ear hole Ø |
| `stack_tray.stl` + `stack_lid.stl` | One case corner: insert in the tray, board on top, lid spigot through the board hole, M3x10 from the lid side. It clamps the board with no gap at the boss faces. | Whole stack works |
| `slide_tray.stl` + `slide_panel.stl` | Both front corners of the case and both corners of a blank panel (roof strip down, as the panel prints), moved together to a 16 mm wide opening. Slide the panel in from the open end: it runs free, does not rock, and the bumps on the strip edges click into the grooves at the end of travel. Print at each nozzle you use. | V-groove clearance 0.2, detent click |
| `legend_strip.stl` | The RELAY 2 block of the Slice_RLHT legend, engraved 0.6. Read it at arm's length. | Legend legibility |
| `tilt_jig.stl` | The next slice's lid face, 0.8 above the roof, as it sits when slices are packed. Take the panel off a real RLHT case, set the jig on the roof (spacers on the roof, lips outside the side walls, plate edge flush with the far face), and try to turn an MKDS screw with a 3 mm flat blade under the plate edge (about 36° from vertical). | Whether a packed slice can be re-terminated in place |

The first six are unchanged. `stack_tray` / `stack_lid` were cut from the
earlier case; the boss, pocket and spigot they test are the same now.

## 2. Then a case: `2-cases/`

| File | For |
|---|---|
| `s_tray_nano-b.stl` | S tray, USB port at E 29.1 (Nano USB at board x 20.0): Slice_RLHT, Slice_THRM_31856 |
| `s_tray_nano-a.stl` | S tray, USB port at E 36.7 (Nano USB at board x 27.6): the other 28 S Nano slices (Slice_AQ*, Slice_DCMT, Slice_TEMP_NANO_S2L-r1/r2 and the rest; `src/groups.py` lists them) |
| `s_lid.stl` | S lid, every S slice except Slice_DCMT (its lid has Nano-tail windows) |
| `panel_rlht.stl` | Front panel for Slice_RLHT, legend engraved 0.6 |
| `panel_aqph.stl` | Front panel for Slice_AQPH (open-bottom notch for the mated BNC plug) |
| `panel_blank.stl` | Blank front panel, for any S slice with nothing past its far edge; label it by hand |

The panels print roof strip down; the legend is engraved in the fascia, which
stands vertical.

Print order: the coupons, then `s_tray_nano-b` + `s_lid` + `panel_rlht` for
Slice_RLHT. Each case is three parts: the tray and lid as before, plus the
panel, the one per-slice part. The port in both trays is the soldered plus
socketed height (13.35 x 18.4) until RLHT's Nano mount is measured.

Volume, from the STLs (x 1.27 g/cm³, not sliced): tray 39.9 g, lid 16.7 g,
panel 6.0 to 6.4 g, tilt jig 9.2 g, the slide and legend coupons 0.1 to 2.9 g each.

## Hardware

- M3 x 5.7 heat-set inserts, OD 4.6, Ø4.0 vendor hole (CNC Kitchen / ruthex
  "M3 standard" class): 6 for the insert ladder, 1 for the stack pair, 4 per
  case, and the backplane's below.
- M3x10 socket head screws (ISO 4762): 1 for the stack pair, 1 for the ear
  ladder, 4 per case, plus 2 per case for the ear screws into the backplane.
- Backplane: 8 inserts in the bosses plus 2 per slot used (12 for all towers),
  and 8 M3x6 socket head screws from the loaf underside.
- For the tilt jig: a 3 mm flat-blade screwdriver and a Slice_RLHT in its case.
- The panel needs nothing: it slides into the tray and clicks. Pull it out by
  the ridge along the fascia's top edge.

## 3. Backplane: `3-backplane/`

| File | What |
|---|---|
| `backplane.stl` | The backplane part for Loaf_x004 (gen1 and r3). It sits on the loaf top: 8 M3x6 screws from the loaf underside into inserts in its 8 bosses at the bus-footprint Ø3.3 holes. Per slot: a U guide around the slice socket and 3 towers (A -56.4, +56.4, +101.4) with an insert each, for the case ear screws. 124.9 x 167.8 x 15.0: fits an MK3 bed as it loads. Prints fine on a 0.8 nozzle. |
| `stand_foot.stl` | Print 4. Loose feet: the peg goes up into the Ø4.0 holes under the outer rails, and they lift the loaf's underside parts (barrel jack, to 10.6 below the loaf) off the bench. Placeholder until a stand exists. 10 x 20 x 17. |

Volume, from the STLs (x 1.27 g/cm³, not sliced): backplane 83.5 g, foot 3.6 g each.

Fit it: inserts into the 8 bosses from the flat (bed) face, flush; then into the
towers from the top, flush with the tower top (that face is the slice's E stop,
so a proud insert lifts the slice). Set the backplane on the loaf with the guide
fins on the chain-input end's side of each header, screw the loaf on, put the
feet under, then slide a cased slice down into a slot and screw its two ears.

What it tests (slot-interface-v1.1 `measure_on_real_parts`): the socket meets the
header with about 0.13 to spare when the ears sit on the towers (seat 6.7, from
the gen-2 support); the guide catches the socket before the pins meet; the ear
holes line up with the towers.

## Everything else

| Path | What |
|---|---|
| `src/` | The `.scad` and partspec spec files these STLs come from, `groups.py` (which slices use which tray), and the detailed READMEs (`README-coupons.md`, `README-cases.md`). |
