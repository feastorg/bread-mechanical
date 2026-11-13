---
# front matter added by import
---

# bread-mechanical

3D-printed and mechanical parts for BREADS-compatible hardware: Slice enclosures,
Loaf backplane mounts, and related hardware.

> **Work in progress.** This repository is early-stage. The designs here are
> functional but not yet fully documented. Check back as the project matures.

## Contents

| File | Description |
|---|---|
| `slice_case.scad` | Parametric enclosure for BREADS-compatible Slice modules |
| `slice-case/` | Parametric, data-driven Slice case and Loaf_x004 backplane part, with checks and print guide |
| `nano.scad` | Arduino Nano mechanical reference model |

## Usage

Files are designed in [OpenSCAD](https://openscad.org/). Open any `.scad` file
directly in OpenSCAD to render and export to STL for printing.

## License

`GPL-3.0-or-later OR CERN-OHL-S-2.0`, at your choice, unless a file's own
SPDX header names a narrower licence. See
[LICENSING.md](https://github.com/feastorg/bread-mechanical/blob/main/LICENSING.md).
