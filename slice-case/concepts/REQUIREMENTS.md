# Slice case: front cover, label and form — requirements (draft for review)

Status: draft, 2026-10-11. Nothing gets designed until this is agreed.

## What is fixed already

- The case is general: tray (THT side) + lid (SMT side), one default per board
  format, data-driven, with per-slice modifiers only where a board really differs.
  Nothing slice-specific is moulded into the tray or lid.
- Slot interface v1.1 (`design/synth/slot-interface-v1.1.json`):
  - case thickness 29.6 inside the slot envelope;
  - ears at the bus edge, seat face and holes fixed;
  - bus window and tongue.
- M3 heat-set inserts in the tray, M3 screws through the lid, no nuts.
- Prints without supports in PETG on 0.4 and 0.6 nozzles.
- The stand never touches the case; the backplane part does not either, beyond the ears and guide.

## Front edge (the far end, opposite the backplane)

Most S slices bring field wiring out here: screw terminal blocks (Phoenix MKDS
and MPT, 4Ucon, TE 282834) along the far edge, plus a few other connectors
(USB-A on USBP, BNC on the AQ* slices, SMA on AOEM, which is an L board).

| # | Requirement | Source |
|---|---|---|
| F1 | Wires stay connected and pass through the front edge with the case fully closed. | User, 2026-10-11 |
| F2 | Reaching the terminal screws (tighten, re-terminate) needs only the front cover removed or opened. The case stays assembled: no lid screws, and the slice stays on the backplane. | User, 2026-10-11 |
| F3 | The cover cannot fall out or open by itself when the slice hangs vertically, or when it is knocked or vibrates. | User (retaining bump) |
| F4 | It opens and closes by hand, with no tools, and with neighbouring slices packed at 30.4 pitch. | Derived: the slot pitch |
| F5 | Nothing moves outside the slot envelope, open or closed. | Slot interface |
| F6 | The ear-screw driver paths (Ø7 along E, from the far side) stay clear, with the cover on. | Slot interface v1.1 |
| F7 | The front opening is sized from the format, with a default covering where terminal blocks sit on S boards. A slice with connectors deeper or elsewhere gets a modifier, not a bigger default. | Data-driven rule |
| F8 | Connectors that are not screw terminals (USB-A, BNC, JST, headers) are still reachable or pass through. | Fleet survey |

## Label

| # | Requirement | Source |
|---|---|---|
| L1 | It shows the slice name and a per-terminal legend lined up with the terminals (e.g. HTR1+ / HTR1-, TC1, 12V). | User, 2026-10-11 |
| L2 | The label is the only per-slice printed part, so the case stays general. Swapping a label means reprinting only it. | User |
| L3 | The legend is generated from slice data, never typed into CAD by hand. | Data-driven rule |
| L4 | It is readable at arm's length when printed in one colour at 0.4 and 0.6 (stroke width at least about 0.8). It also prints blank, for hand labelling. | Print constraint |

Open question for L3: where does the legend data live? Today `slice.yaml`
`hardware.connectors` has only ref/type/purpose, and the per-pin names exist only
in the schematics. Options: extend `slice.yaml` (a schema change across the
slices, fixed at source), or read pin names from the schematic net labels.

## Form

| # | Requirement | Source |
|---|---|---|
| G1 | It looks like a finished product: rounded plan corners, chamfered outer edges, ears that read as part of the case, and a visible, intentional parting line. | User feedback on the current case |
| G2 | Every form choice is justified by looks, handling or strength. No vents or light pipes. | User |
| G3 | The USB port is sized for the plug, not the worst case, at each board's real Nano position. The height depends on how the Nano is mounted, which is still being measured. | User |

## How the concepts will be judged

Each concept gets a render on a real S board, and a short write-up of how it meets
F1–F8 and L1–L4, part count, print time and filament (estimates), how it feels to
use, and its risks.

Candidate directions to explore (not decided):
- a sliding roof panel;
- a snap-on front bezel;
- a clip-in label card plus a separate access flap;
- a hinged flip cover (living hinge or pin).

Out of scope: the backplane part, the stand, L-format specifics beyond noting
how a concept extends to L.
