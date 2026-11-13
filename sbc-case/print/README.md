# What to print

PETG, as for the slice case (`../../slice-case/print/README.md`): 0.4 nozzle, 0.20 layers, no supports. Every
STL is in print orientation with its bed face at z = 0: load it without rotating. `bash ../build.sh` builds
every STL below from source.

## 1. Coupon: `1-coupons/`

| File | What to do with it | Records |
|---|---|---|
| `insert_coupon.stl` | Seven hex bosses, the same size as the lid's top standoffs, with pockets of 3.4 to 4.0 mm (engraved beside each). Press an M2.5 x 4.0 heat-set insert into each. Take the smallest pocket where the insert goes in square, sits flush, and does not spin under an M2.5. | Insert hole Ø |

`boards.json` starts at 3.7 (`top_standoff_insert_dia`), an unverified figure. Set it to the coupon's
answer before printing a case.

## 2. Then a case: `2-cases/`

| File | For |
|---|---|
| `<board>_lid.stl` | Lid, printed roof down. Vents, and the window over the GPIO header |
| `<board>_bottom.stl` | Bottom, printed floor down |
| `<board>_mount_2020.stl` | Extrusion mount, printed underside down |

`<board>` is `rpi4b`, `rpi3a+` or `rpizero2w`. Print the Pi 4B and Pi 3A+ first.

## Hardware, per case with its mount

- 4 M2.5 x 4.0 heat-set inserts (CNC Kitchen "M2.5 standard" class), one in each lid standoff.
- 4 M2.5 x 16 socket head screws (ISO 4762), from under the mount, through the bottom and the board, into the
  inserts.
- 2 M5 socket head screws (ISO 4762) and 2 M5 drop-in T-nuts for 2020. The head sits in a 5 mm recess, leaving
  3 mm of plate under it, so an M5 x 8 puts about 5 mm into the T-nut. Check that against your T-nuts.
  Screw the mount to the extrusion before the case goes on: these heads are under the case.

Using the case without the mount needs shorter M2.5 screws; that length has not been worked out.

## Fit test (first print of each board)

Case Builder builds the openings and standoffs from SBC Model Framework's board data, which upstream marks
unverified for all three boards, and which models the board as 1.0 mm thick. Record for each board:

1. The board sits on all four bottom standoffs without rocking.
2. Every port lines up with its opening: USB, HDMI, power, audio, Ethernet (4B), SD card.
3. The lid closes onto the bottom with the board in place, with no gap at the seam, and does not press on any
   component.
4. Dupont jumpers plug onto every pin of the 40-pin header through the roof window, including the end pins
   on both rows.
5. With the mount: the four M2.5 x 16 screws reach the inserts and pull the lid down, and their heads sit
   below the mount's underside.
6. The mount sits flat on the extrusion, and both M5 heads sit below its top face.
