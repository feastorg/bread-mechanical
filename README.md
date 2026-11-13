# bread-mechanical

3D-printed and mechanical parts for BREADS-compatible hardware: Slice cases, Loaf backplane mounts, and related hardware.

## Contents

- `nano.scad` — Arduino Nano mechanical model
- `slice_case.scad` — Slice enclosure design
- `slice-case/` — Parametric, data-driven Slice case and Loaf_x004 backplane part, with checks and print guide
- `sbc-case/` — Cases and a 2020 extrusion mount for the single-board computers that run a BREAD (Raspberry Pi
  4B, 3A+, Zero 2 W), built on SBC Case Builder, with checks and print guide. `GPL-3.0-or-later` only

## Dependencies

`sbc-case/` uses OpenSCAD libraries pinned with [scadman](https://github.com/CameronBrooks11/scadman) in
`scadman.toml` / `scadman.lock`. Run `scadman sync` once in a checkout; `scadman env` prints the
`OPENSCADPATH` to use.

## License

`GPL-3.0-or-later OR CERN-OHL-S-2.0`, at your choice, unless a file's own
SPDX header names a narrower licence. See [LICENSING.md](./LICENSING.md);
`LICENSES/` holds both texts.
