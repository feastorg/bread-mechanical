# Slice case: S case parts (tray, lid, front panel)

The STLs in `../2-cases/` are the real `design/synth/case.scad` geometry (the
panel is `panel.scad`, included by it), with parameters from
`design/synth/resolved/<slice>.json` passed the way `spec.py` passes them.
`print.scad` only puts each part in print orientation. Nothing is re-modelled.

## Files

| File | Built from | Bed face | Size x/y/z (mm) |
|---|---|---|---|
| `s_tray_nano-a.stl` | Slice_TEMP_NANO_S2L-r2 (USB port at E 36.7) | roof | 72.7 x 121.8 x 29.6 |
| `s_tray_nano-b.stl` | Slice_RLHT (USB port at E 29.1) | roof | 72.7 x 121.8 x 29.6 |
| `s_lid.stl` | Slice_TEMP_NANO_S2L-r2 | outer face | 74.7 x 104.6 x 6.83 |
| `panel_rlht.stl` | Slice_RLHT, legend from `design/synth/legends/Slice_RLHT.yaml` (MOCK), engraved 0.6 | roof strip | 14.7 x 102.3 x 29.6 |
| `panel_aqph.stl` | Slice_AQPH, legend from `legends/Slice_AQPH.yaml` (MOCK), BNC notch from the board | roof strip | 14.7 x 102.3 x 29.6 |
| `panel_blank.stl` | no legend, no notches | roof strip | 14.7 x 102.3 x 29.6 |
`python3 -I groups.py` lists which slices each tray and the lid serve; a tray
group is the set of slices that resolve to identical tray parameters.

## Design

- Front: the roof is open over the terminals (E 68.0 to the far end, A ±40.2)
  between two corner towers. The panel's roof strip slides into a V groove in
  each tower (0.2 clearance). The fascia carries the engraved legend (0.6 deep),
  comes down to the lid face at the corners, and leaves the wire slot open below
  N 6.0 between the towers. A pull ridge runs along the fascia top edge.
- Detent: a spring finger along each strip edge (1.5 x 10, cut free by a 0.8
  slot that ends in a full round), printed flat so it flexes along the layers.
  A smooth ellipsoid bump ($fn 64) on its V apex clicks into a matching notch
  in the groove, 0.3 larger, so the finger is unloaded when shut. Pulled 3 mm,
  the bump overlaps the groove wall by 0.80 in A (spec band 0.45 to 0.85).
- Form: R5.3 far plan corners on one outline that runs through the fascia,
  1.0 roof chamfer, 1.0 parting-line chamfer on the tray with the 0.4 rim gap,
  0.8 lid edge chamfer, full-height end flanges carrying the ears, bus-end
  bosses tied to their wall corners.
- USB: a 13.35 x 18.4 port (R1.5 corners) centred on the board's own Nano
  USB, in place of the 26.4 x 21.8 window. Its height covers a soldered and a
  socketed Nano (`formats.yaml` `mcu_access.nano`).

## Print notes

Downward-facing area off the bed, from `design/synth/tools/overhang.py`
(`../_work/cases/panel/overhang.txt`):

- Trays: 53.7 mm² (the earlier `s_tray` was 58.3), most of it the USB port's
  print-top edge, which bridges about 10.4 mm.
- Lid: 91.7 mm² (was 80.7), most of it the four counterbore ceilings
  (76.6 mm² at z 3.2).
- Panels, roof strip down: RLHT 148.7, AQPH 42.0, blank 4.2 mm². The panel
  figures are mostly the tops of the engraved strokes in the vertical fascia.

## Checklist

**Tray and lid**: as before. The insert, spigot, boss, ear and bus window are
unchanged.
- [ ] The USB plug goes in with Slice_RLHT installed. Record the Nano mount
      (soldered or socketed) and the plug used.
- [ ] Assembled on the real board with 4 x M3x10, the rim gap is even and the
      overall thickness is 29.6 nominal, 30.0 maximum.

**Panel**
- [ ] It slides in from the far end without force, the bumps click at the end
      of travel, and it sits with the fascia flat on the tower ends.
- [ ] Shut, it does not rattle or slide out with the case held face down.
- [ ] It comes out by the pull ridge, and comes off over the wires.
- [ ] Wires leave through the slot under the fascia without pinching.
- [ ] Legend readable at arm's length (compare with the legend coupons).

## Regenerating

From this directory:

```
python3 -I ../../design/synth/tools/resolve.py Slice_TEMP_NANO_S2L-r2 Slice_RLHT Slice_AQPH
partspec check print_spec.py:<target> --out <dir>
partspec measure print_spec.py:<target> --out ../2-cases/<name>.stl
```

Targets: `s_tray_nano_a`, `s_tray_nano_b`, `s_lid`, `panel_rlht`,
`panel_aqph`, `panel_blank`. Each checks that the part is watertight, is one
solid, and has nothing below z = 0. The legend needs the DejaVu Sans Condensed
Bold font on the machine that runs OpenSCAD.
