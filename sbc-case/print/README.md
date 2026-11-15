# What to print

PETG, as for the slice case (`../../slice-case/print/README.md`): 0.4 nozzle, 0.20 layers, no supports. Every
STL is in print orientation with its bed face at z = 0: load it without rotating. `bash ../build.sh` builds
every STL below from source.

## 1. Coupon: `1-coupons/`

| File | What to do with it | Records |
|---|---|---|
| `insert_coupon.stl` | Seven hex bosses, the same size as the lid's top standoffs, with pockets of 3.4 to 4.0 mm (engraved in front of each). Press an M2.5 x 4.0 heat-set insert into each. Take the smallest pocket where the insert goes in square, sits flush, and does not spin under an M2.5. | Insert hole Ø |

`boards.json` starts at 3.7 (`top_standoff_insert_dia`), an unverified figure. Set it to the coupon's
answer before printing a case.

## 2. Then a case: `2-cases/`

| File | For |
|---|---|
| `<board>_lid.stl` | Lid, printed roof down. Vents, and the window over the GPIO header |
| `<board>_bottom.stl` | Bottom, printed floor down, with an ear at each short end |
| `<board>_mount_2020.stl` | Extrusion mount, printed underside down |

`<board>` is `rpi4b`, `rpi3a+` or `rpizero2w`. Print the Pi 4B and Pi 3A+ first.

## Hardware, per case

- 4 M2.5 x 4.0 heat-set inserts (CNC Kitchen "M2.5 standard" class), one in each lid standoff.
- 4 M2.5 countersunk screws (ISO 7046-1 or ISO 14581), up through the floor and the board into the inserts:
  M2.5 x 12 for the 4B and 3A+, M2.5 x 10 for the Zero 2 W. They close the case with or without the mount.

With the mount, add:

- 2 M3 x 5.7 heat-set inserts (as slice-case's), one in each pocket on the mount's top face.
- 2 M3 x 8 or x 10 socket head screws (ISO 4762), down through the ears into those inserts. Undo these two
  and the closed case lifts off.
- 2 M5 socket head screws (ISO 4762) and 2 M5 drop-in T-nuts for 2020. The head sits in a 5 mm recess, leaving
  3 mm of plate under it, so an M5 x 8 puts about 5 mm into the T-nut. Check that against your T-nuts.
  Screw the mount to the extrusion before the case goes on: these heads are under the case.

## Fit test (first print of each board)

Case Builder builds the openings and standoffs from SBC Model Framework's board data, which upstream marks
unverified for all three boards, and which models the board as 1.0 mm thick. Record for each board:

1. The board sits on all four bottom standoffs without rocking.
2. Every port lines up with its opening: USB, HDMI, power, audio, Ethernet (4B), SD card.
3. The lid closes onto the bottom with the board in place, with no gap at the seam, and does not press on any
   component.
4. Dupont jumpers plug onto every pin of the 40-pin header through the roof window, including the end pins
   on both rows.
5. The four countersunk screws pull the lid down, and their heads sit flush with or below the floor, so the
   case sits flat on the mount.
6. The mount sits flat on the extrusion, and both M5 heads sit below its top face.
7. The two M3 ear screws hold the case down on the mount without rocking, and undoing them lifts the closed
   case off.
