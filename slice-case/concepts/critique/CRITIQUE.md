# Critique of the front-cover and form concepts

> The concept explorations, writeups and renders this review cites are not in this repository. It is kept as the record of why the case uses the sliding panel and its three grafts (section 2).

Reviewed 2026-10-11 against `concepts/REQUIREMENTS.md`, each concept's `WRITEUP.md`, its renders (all the best renders were opened, plus the detent, section and packed views), its STLs and its source. Nothing in `design/` or `print/` was changed.

## Recommendation

**Front: the sliding panel (pencil box), with three changes taken from the other concepts.** **Form: option C's full-height end flanges, with option A's 1.0 roof chamfer and the shared changes.** But first, one decision has to go back to the user, because it decides whether the front cover can do its main job (F2, below).

Three of the four front concepts are the same design. Sliding panel, snap bezel and wildcard are all a per-slice L-shaped part (a roof strip plus a front plate) that pulls straight out along +E. They differ only in how the part is held in place and in how much of the far end it covers. So the real choice is "L-panel sliding along E" against "hinged flap", and then which retention to use. The sliding panel has the strongest retention of the three: V-grooves in solid corner towers hold the panel in N over its whole travel, and the spring finger is printed flat, so it flexes along the layers. The flap is the only design with no loose part, but it changes the general tray and lid the most, and its snap-in pivots rely on the tray walls bending across the layer lines.

## 0. The finding that gates every concept: F2 with neighbours packed

All four write-ups found that the screws can only be reached packed with a tilted driver. I checked how they got their different angles:

- **The disagreement comes from the terminal-height input, not from the cover design.** A 2D ray model (shaft r 1.5, screw at E 73.1, neighbour lid corner at E 79.4 / N 22.7) gives:
  - 28.2° with head N 7.73. That is wildcard's estimate: "10 tall, head 1 below", from no datasheet.
  - 36.5° with head N 11.63. That is the sliding panel's figure, taken from the KiCad STEP.

  The command was run in this review. The KiCad 10 STEP model `TerminalBlock_Phoenix_MKDS-1,5-6-5.08_1x06_P5.08mm_Horizontal.step` (flatpak Packages3D) has its z levels topping out at 13.6 (screw) and 13.8 (housing) above the board, so the 36° figures from sliding panel, snap bezel and flip cover rest on the better input. **Wildcard's "28° is the best a neighbour allows" is an artefact of a height about 4 mm low. Its advantage #5 ("a front-only bezel keeps that edge") is also wrong.** Every concept cuts the roof over the screws: the snap bezel from E 69.5, the sliding panel from E 68.0, and the flip cover with an undercut to E 77.2.
- **36° on a slotted screw is very unlikely to work.** A flat blade tilted 36° only seats while the slot lies in the tilt plane. Every quarter turn it ends up across the plane and cams out. This is reasoning, not a test.
- **The path is also blocked by the upper neighbour's wires.** `sliding-panel/renders/rlht_access_sec.png` and `flip-cover/renders/rlht_section_driver.png` both show the driver shaft passing through the +N slice's wires where they leave its face. The flip-cover render `rlht_packed_iso.png` shows the same thing in 3D.
- **What follows from this.** Packed, an opened cover exposes only things that face +N (screws, JST, headers), and the next lid sits 0.8 mm above them. So unless the tilted driver works, opening the cover packed achieves nothing. Re-terminating then means pulling a slice: either this one or the +N neighbour, 2 ear screws each.

**What I need from the user, before any cover is printed: "If a 3 mm blade cannot drive an MKDS screw at about 36° under a plate 0.8 mm above the roof, do we accept 'pull the slice (2 ear screws) to re-terminate'?"**
- Settle it on the bench: measure the MKDS head height on the RLHT in hand, then try the 36° drive.
- The recommendation below does not depend on the answer. Every concept needs the roof opening, which leaves the screws open from above once the slice is pulled. The answer only changes how much F4 (opening it packed) is worth.

## 1. Front concepts

### Scores (1 = poor, 5 = good)

| Concept | Requirements | Simplicity | Robustness | Usability | Printability | Sum |
|---|---|---|---|---|---|---|
| Sliding panel | 4 | 4 | 4 | 3 | 4 | **19** |
| Snap bezel | 4 | 3 | 3 | 3 | 3 | 16 |
| Wildcard (label is the cover) | 4 | 3 | 2 | 3 | 3 | 15 |
| Flip cover | 3 | 2 | 2 | 3 | 3 | 13 |

F2 is "partly" for all four and L3 is a mock for all four, so neither changes the ranking.

### Sliding panel: recommended base

What holds up:
- **Overhang numbers reproduce.** I re-ran `overhang.py`: tray 71.2 mm², against 58.3 for the shipped `print/2-cases/s_tray.stl`; RLHT panel 112.7. These match the write-up.
- **The geometry is sound.** The V-grooves run in solid towers that replace the free-standing far bosses. The roof opening is set by the fleet survey (E 68.0, |A| ≤ 40.2) and leaves no hits across 32 S boards.
- **The detent is the best of the four for FDM.** The finger lies in the roof strip, which is printed on the bed, so it flexes in A, along the layers. The estimated strain is 1.1 %, and there is none at rest.
- **The motion is the only one that gets past a mated BNC** (`aqph_closed_iso.png`).

What only shows up in use:
- **The panel is loose while it is off.** The 11-12 mm pull also needs clear air in front of the fascia, and wires hanging down from the slice above block it. `rlht_packed_front.png` shows the wires of each slice draped across the fascia below.
- **The fascia covers only N 6.0..21.9.** Below it, the lid-side raw ends and the lid bosses stay visible: grey cylinders at both lower corners in `rlht_front.png` and `aqph_closed_iso.png`. G1 is only half addressed.
- **The legend is engraved 0.8 mm strokes, 0.6 deep, on a vertical face.** On a 0.6 nozzle an 0.8 mm gap is narrower than two extrusion widths (about 1.2), so the slicer may bridge it or leave it unfilled (estimate). It needs a coupon.
- **`rlht_detent_sec.png` is cropped too tight to judge.** It shows only a V tip in a groove; no finger or notch is visible. `rlht_detent_top.png` and the partspec section carry the detent claim instead.

### Snap bezel

What holds up:
- **It gives the best G1 coverage.** The plate covers the whole open end, including the lid side and corner bosses (`png/rlht_packed.png`, `rlht_closed.png`).
- **The spring strips are in-plane,** like the sliding panel's finger.
- Tray overhang reproduces at 57.8 mm².

What only shows up in use:
- **It has the most small features on the per-slice part.** Two 0.8 slits (marginal on a 0.6 nozzle), two 2 mm tabs under the board edge, two grips and two bumps. The write-up's own figure is ±33 % retention force per ±0.1 mm of print error.
- **The grips stick out to E 89.4, right beside the ear-driver path.** The path is at A ±56.4 and the grip faces at |A| ≤ 52.3. The driver handle must stay beyond the grips, so the shaft must be at least 78 mm, against 68 today (write-up). A packed row of bezels also forms a continuous wall of grips 0.8 apart in N, so they can only be pulled by gripping in A.
- **It cannot be lifted off over the wires.** Its plate is full height with a letterbox, so it hangs on the wires after release ("lift it toward +N once clear").
- **Its claim that the board contradicts itself is not established.** It says J5 is labelled RELAY 2 but carries `/Relay1/` nets. The root schematic names the two relay sheet instances `Relay` (`BREAD_Slice.kicad_sch:10233`) and `Relay1` (`:9895`). That is KiCad's default name for a second instance, not a relay number, so the nets prove nothing either way.

### Wildcard (the label is the cover)

The idea is right, and it is what all the L-panels already are: the label is the cover. What sets it apart is the retention, and that is its weak point.

What only shows up in use:
- **The split pegs print standing up, so they flex across the layers.** The card prints face down, so the Ø3 split pegs stand along print Z (`renders/rlht_card_print.png`). Each half is 1.1 thick after a 0.8 slit (`wildcard_lib.scad:20,78`), and bending puts its stress across the layer lines.
- **The detent depends on 0.1 of interference,** a Ø3.5 bump in a Ø3.3 hole, which is inside normal FDM hole error. It may grip hard or not at all.
- **The way to open it levers the pegs.** You hook the card's lower edge (there is no pull tab), which bends both pegs across their layers.
- **It also changes the general lid** (a 2 mm front lip), and its F2 advantage is the height artefact in §0.
- **Text printed face-down is its real gain,** and so is the colour change at layer 4 for a two-colour legend. But on a 0.6 nozzle, first-layer squish tends to close 0.8 recesses (estimate).
- **Its renders overstate one-colour legibility.** `rlht_front.png` and `rlht_closed_packed.png` show the legend in black on a light card. In one colour it reads by shadow only.

### Flip cover

What holds up:
- **It is the only captive design,** with no loose part.
- Its F5 sweep (N −2.78..22.03) and its legend alignment check out. In `renders/rlht_front.png` every pin label sits on its pin centre.

What only shows up in use:
- **It changes the general parts the most.** The walls are lengthened to E 83.4, with pivot holes, lead-in ramps, dimples and stop blocks. The roof gets an undercut, and the lid gets a 1.4 chamfer. The lid overhang goes from 80.7 to 154.7 mm²; I re-ran `overhang.py` and it reproduces.
- **The snap pivots load the walls across the layers.** The pins are 1.4 long (`flip.scad:28`), so fitting the flap spreads each 2.0 wall about 1.4 at N 5.6, 14.7 below the roof. As a cantilever from the roof, ε ≈ 3tδ/2L² ≈ 1.9 % (rough estimate). The tray prints roof down, so that strain runs across the layer lines at the roof-wall junction.
- **The detent loads the wall whenever the flap is open.** Its bump stays 0.25 into the wall (write-up), which invites creep.
- **It has functional gaps.**
  - On AQPH it opens only 10-20° before it meets the BNC.
  - A slice with screws and a pass-through connector in the same span cannot be opened.
  - On RLHT it rests on the wires at about 75°, and on a bench it falls shut.
  - Its wire slot is the lowest, at N 5.6. That leaves 1.1 mm over an estimated Ø4 ferrule collar centred 3.75 above the board (STEP z levels 2.5-5.0). This is the most likely of the four to pinch insulation.
- **Its renders overstate the legend's contrast.** They show dark raised text on a light flap. The header row "ESTOP RLY2 ESTOP RLY1" also runs together, with "RLY2" sitting over the left block's IN/NO.

### Shared to all four (not a differentiator)

- **Legend capacity is the same everywhere:** at most 3 characters per pin at 5.08 pitch, and only a group label at 2.54 pitch. The legend data source has to provide short names.
- **The legend sits where the upper neighbour's wires hang.** With wires dressed downward, every slice's legend is covered (`sliding-panel/renders/rlht_packed_front.png`).
- **Every concept leaves the tray open over the terminals without its cover,** so each slice needs its panel printed, even if blank.

## 2. The graft I recommend for the front

Start from `concepts/sliding-panel/`: the towers with V-grooves, the L-panel, the in-plane finger detent, the pull ridge and the open-bottom wire slot. Then change three things:

1. **From the snap bezel: run the fascia down to the lid face (N −7.7), at the corners only (|A| 40.2..52.3).** This hides the lid-side wall ends and bosses (G1). The slot between the towers stays open at the bottom, so it still comes off over wires and the BNC, and F5/F6 limits are unchanged (|A| ≤ 52.3, N within −7.9..22.1). Leave out the 10 mm grips and the under-board tabs.
2. **From the flip cover and wildcard: lay the legend out as a horizontal group header with a rule over each block, vertical pin labels of 3 characters or fewer on the pad centres, and the slice name at one end.** Decide raised against engraved with a coupon at 0.4 and 0.6. I would expect raised 0.8 strokes to print more reliably on a 0.6 nozzle (estimate).
3. **From form option A/C: give the fascia the R5.3 far plan corners,** so it follows the case outline.

Before production, print three coupons:
- a tower corner with a panel corner, to test the 0.2 V-groove clearance and the finger click at 0.4 and 0.6;
- a legend strip;
- the MKDS tilt test from §0.

Extending to L boards: the same rules carry over. The panel is about 150 long, the towers come from the A −45 / +90 holes, and the deflection is an estimate of about 0.15 mm under 5 N. AOEM's SMA connectors get notches like the BNC.

## 3. Form options (G1-G3)

| Option | G1 | G2 | G3 | Printability | Cost | Sum |
|---|---|---|---|---|---|---|
| A: refined box, lugs | 4 | 5 | 4 | 5 | 4 | 22 |
| B: flared shoulders | 4 | 2 | 4 | 4 | 2 | 16 |
| C: full-height end flanges | 5 | 4 | 4 | 4 | 4 | **21** (preferred for G1) |

Sources:
- Overhang, re-run here: A 31.2, B 35.4, C 33.1 mm², against 58.3 for the baseline tray.
- Volume (`form-options/volumes.txt`): A +5.7 %, B +13.8 %, C +7.1 %.
- G3 is the same port in all three, so it scores the same.

What holds up and what doesn't:
- **C does not break the slot interface.** It is the one I suspected. `slot-interface-v1.1.json` limits the ear to N 6.5..16.5, but the note on that limit (`N_range_max_note`) says it covers the pad land only. The flanges start at `case_E0 = seat_E + face_gap` (`case.scad:87`), and only the Ø9 pad reaches E 6.7, so C is compliant.
- **C's thin-roof-edge risk at the far end disappears under the recommended fascia.** The 2.0 chamfer is separable; use A's 1.0.
- **A, seen from the top, is still a small rectangle at each corner** (`png/rlht_A_solo_top.png`). It is lower risk, but the ears still read as tabs. C's flanges and the bus wall read as one end panel, which is what G1 asks for ("ears that read as part of the case"). The extra cost is 0.4 cm³ (about 0.5 g, estimate).
- **B: reject.** The flare hides the ear screw in a tunnel with 0.6 radial clearance, so only a straight hex key fits. It is the heaviest of the three.
- **The bosses tied to the walls and the towers of the sliding panel are the same rule.** Apply the tie to the bus-end bosses, and the towers at the far end.
- **The USB port is a real conflict between G3 and L2.** A per-board port puts RLHT and THRM_31856 at E 29.12 and the other 28 Nano boards at E about 36.7. Two points matter:
  - The window is already per-board data today: `mcu_windows` in `params_Slice_RLHT.scad` is E 19.7..46.1, the worst case. So per-board ports add no new mechanism.
  - Only the port position varies, and it is generated.

  I recommend (a), per board, as G3 states it. Use the `both` height (13.35 × 18.4) until the RLHT Nano mount is measured. Fall back to (b), one 20.96-wide port, only if one S tray is a hard requirement.

## 4. Claims corrected in this review

| Claim | Concept | Correction | Evidence |
|---|---|---|---|
| Min driver tilt 28.2° | wildcard | About 36° with the KiCad model's heights; 28.2° comes from a head height about 4 mm lower | ray model above; STEP z levels 13.6 / 13.8 |
| A front-only bezel keeps the roof edge | wildcard | Every concept cuts the roof over the screws | `snap-bezel/bezel.scad` `acc_E0 = 69.5` |
| J5 RELAY 2 vs `/Relay1/` is a board contradiction | snap bezel | Not established: `Relay1` is a sheet-instance name | `BREAD_Slice.kicad_sch:9895, 10233` |
| One-colour legend readable (renders) | wildcard, flip, snap-bezel packed view | Those renders colour the text; only the sliding panel's render is truly one-colour | `rlht_front.png` in each |
| Detent shown | sliding panel | `rlht_detent_sec.png` is cropped too tight to show the finger | the PNG |

## Files

- `concepts/critique/CRITIQUE.md` (this file)
- The renders reviewed are under `concepts/{sliding-panel/renders, snap-bezel/png, flip-cover/renders, wildcard/renders, form-options/png}/`.
