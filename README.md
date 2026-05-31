# FreeCAD Python Design Library

A Python-first workflow for designing **3D-printable parts** inside FreeCAD.
Write parametric models as plain Python scripts — no GUI required — and export
directly to STL.

---

## Project structure

```
FreeCAD/
├── src/
│   ├── freecad_lib.py          # Core library: primitives, transforms, hardware data
│   └── part_library/           # Reusable parametric parts
│       ├── __init__.py
│       ├── hinge.py
│       ├── snap_fit.py
│       ├── living_hinge.py
│       ├── cable_clip.py
│       ├── standoff.py
│       ├── wall_bracket.py
│       ├── hook.py
│       ├── knob.py
│       ├── box_lid.py
│       └── dovetail.py
├── projekte/                   # Individual design scripts
│   ├── HoneyBox.py
│   ├── Schirmhalter.py
│   └── ...
├── fonts/                      # TTF fonts for SolidText
├── stl/                        # Exported STL files
└── pics/                       # Reference images
```

---

## Quick start

Open a design script inside FreeCAD's built-in Python console or run it via
**Macro → Execute Macro**. All scripts import from `src.freecad_lib`:

```python
import FreeCAD, Part
from FreeCAD import Vector
from src.freecad_lib import *

new_doc("MyPart")

# Build geometry
body = Box(Vector(-25, -15, 0), Vector(25, 15, 10)).solid
hole = Cylinder("hole", 5, 10, Vector(0, 0, 0))
body = body.cut(hole.solid)

# Display and export
show_solid(body, color=(0.3, 0.6, 0.9), name="MyPart")
export("MyPart", "MyPart")
fit_view()
```

---

## `src/freecad_lib.py` — core library

### Coordinate conventions

All coordinates are in **millimetres**. The mnemonic naming for box corners uses
compass directions:

| Shorthand | Axis | Direction |
|-----------|------|-----------|
| `w` | X | West (−) |
| `e` | X | East (+) |
| `s` | Y | South (−) |
| `n` | Y | North (+) |
| `d` | Z | Down (−) |
| `u` | Z | Up (+) |
| `c`, `m`, `g` | X, Y, Z | Centre |

### Primitive shapes

| Class | Key parameters | Description |
|-------|---------------|-------------|
| `Box(vWSD, vENU, joints=[])` | two corner Vectors, optional rounded corners | Rectangular solid; `.solid`, `.w/.e/.s/.n/.d/.u`, `.c/.m/.g`, `.l/.b/.h` |
| `Quader(name, length, width, height, position)` | dimensions + origin | Convenience box centred at XY origin |
| `Cylinder(name, diameter, height, position, normal)` | — | Circular cylinder |
| `Polygon(center, radius, normal, sides, twist)` | `sides=1` → circle | 2D face (circle or regular polygon) |
| `Polyhedron(polygon1, polygon2)` | two `Polygon` faces | Lofted 3D solid between two profiles |
| `Sphere(radius, position)` | — | Full sphere |
| `Cone(name, r1, r2, height, position, normal)` | `r2=0` → sharp tip | Cone or truncated cone |
| `Torus(r_major, r_minor, position, normal)` | — | Donut shape |
| `Bullet(name, diameter, height, position, normal)` | — | Cylinder + hemispherical tip |
| `Tube(name, outer_d, wall, height, position, normal)` | — | Hollow cylinder / pipe |
| `Wedge(name, length, width, height, position)` | — | Triangular prism |
| `Ellipsoid(rx, ry, rz, position)` | — | Axis-aligned scaled sphere |
| `Capsule(name, diameter, height, position, normal)` | — | Pill / stadium shape |
| `Slot(name, length, width, depth, position, normal, direction)` | — | Elongated hole |
| `SolidText(text, position, height, txt_height, spacing, font)` | — | Extruded 3D text |

### Transformations  *(all return a new solid, never modify in place)*

```python
move(solid, Vector(10, 0, 0))          # translate
translate(solid, vector)               # alias for move
rotate(solid, 45)                      # 45° around Z
rotate(solid, 90, Vector(1,0,0))       # 90° around X
mirror_x(solid, x=0)                   # mirror across YZ plane
mirror_y(solid, y=0)
mirror_z(solid, z=0)
mirror(solid, plane_normal, plane_origin)
scale(solid, 1.5)                      # uniform scale
```

### Boolean helpers

```python
fuse_all([s1, s2, s3])                 # union of a list
cut_all(base, [hole1, hole2])          # cut a list from a base
```

### Pattern utilities

```python
array_linear(solid, Vector(1,0,0), count=4, spacing=20)   # linear array
array_polar(solid, count=6)                               # circular array around Z
```

### Hardware data & 3D-print features

| Class / Map | Purpose |
|-------------|---------|
| `Nut(name, size, position, normal, screw_type)` | Hex nut + clearance pocket |
| `Screw(name, size, thread_length, ...)` | Bolt-head + thread clearance |
| `CountersinkHole(name, hole_d, cs_d, depth, ...)` | Flat-head screw recess |
| `CounterboreHole(name, hole_d, bore_d, bore_depth, total_depth, ...)` | Socket-head recess |
| `NutTrap(name, size, position, normal, extra_depth)` | Blind hex nut pocket |
| `HeatSetInsert(name, size, position, normal)` | Ruthex/CNC-Kitchen insert pocket |
| `BearingPocket(name, bearing_type, position, normal, tolerance)` | Press-fit bearing seat |
| `MagnetPocket(name, magnet_size, position, normal, clearance)` | Neodymium disc magnet recess |
| `NUT_MAP`, `SCREW_MAP` | M1–M10 DIN dimensions |
| `COUNTERSINK_MAP` | DIN 7991 head dimensions M2–M10 |
| `BEARING_MAP` | 608, 624, 625 … 6204 bore / OD / width |
| `HEAT_SET_INSERT_MAP` | Pocket sizes for M2–M5 |
| `MAGNET_SIZES` | Standard neodymium disc sizes 5×1 … 20×3 mm |
| `GeneralTolerances` | DIN ISO 2768 lookup (`"f"` / `"m"` / `"c"` / `"v"`) |

### Display & export

```python
show(part_obj, transparancy=50, color=(0.5,0.5,0.5), name="body")
show_solid(raw_solid, ...)   # same but takes a Part.Shape directly
export("DocName", "ObjectName")
new_doc("DocName")
fit_view()
```

---

## `src/part_library/` — reusable parametric parts

Import everything in one line:

```python
from src.part_library import *
```

Every class follows the same convention: constructor accepts only dimension
parameters, exposes a `.solid` attribute, and has a runnable
`if __name__ == "__main__":` demo block.

### Available parts

| Module | Classes | Description |
|--------|---------|-------------|
| `hinge.py` | `HingeLeafA`, `HingeLeafB`, `HingePin`, `Hinge` | Barrel/pin hinge — two printable halves + removable pin |
| `snap_fit.py` | `SnapHook`, `SnapReceptor`, `SnapFit` | Cantilever snap-fit clip (male + female) |
| `living_hinge.py` | `LivingHinge` | Single-print flexible hinge strip with stress-relief notches |
| `cable_clip.py` | `CableClip` | Cable/tube saddle clamp |
| `standoff.py` | `Standoff` | PCB standoff / spacer (round or hex, optional flange) |
| `wall_bracket.py` | `WallBracket` | L-bracket / shelf bracket with optional triangular gusset |
| `hook.py` | `JHook`, `SHook` | Wall hooks (J-profile and S-profile) |
| `knob.py` | `Knob` | Knurled thumb-screw knob (heat-set insert or nut trap) |
| `box_lid.py` | `BoxLid`, `EnclosureBox` | Snap-fit rectangular enclosure lid + matching box body |
| `dovetail.py` | `DovetailRail`, `DovetailSlider`, `DovetailJoint` | Dovetail rail + slider for tool-less assembly |

### Usage examples

```python
from src.freecad_lib import new_doc, show_solid, fit_view, move
from src.part_library import (
    Hinge, Standoff, DovetailJoint, BoxLid, EnclosureBox,
    CableClip, WallBracket, Knob, JHook,
)

new_doc("Demo")

# Barrel hinge — print LeafA and LeafB separately
h = Hinge(leaf_width=30, barrel_diameter=8, knuckle_count=3)
show_solid(h.leaf_a.solid, color=(0.8, 0.5, 0.2), name="HingeLeafA")
show_solid(h.leaf_b.solid, color=(0.3, 0.6, 0.9), name="HingeLeafB")

# M3 PCB standoff, hex body, 12 mm tall, with base flange
s = Standoff(inner_diameter=3.2, height=12, shape="hex", base_flange=10)
show_solid(move(s.solid, Vector(40, 0, 0)), name="Standoff")

# Dovetail rail + slider
dj = DovetailJoint(rail_length=80, clearance=0.25)
show_solid(dj.rail.solid,   color=(0.8, 0.5, 0.2), name="Rail")
show_solid(dj.slider.solid, color=(0.3, 0.6, 0.9), name="Slider")

# Cable clip for 8 mm cable
cc = CableClip(cable_diameter=8, wall_thickness=2.5)
show_solid(move(cc.solid, Vector(80, 0, 0)), name="CableClip")

fit_view()
```

---

## Adding a new project

1. Create `projekte/MyPart.py`.
2. Import and call `new_doc("MyPart")` at the top.
3. Define all dimensions as named constants near the top of the file.
4. Build geometry using `freecad_lib` primitives and booleans.
5. Call `show_solid(body, name="MyPart")` and `export("MyPart", "MyPart")`.
6. Run inside FreeCAD via **Macro → Execute Macro**.

---

## FDM printing tips encoded in the library

- **Hinge**: barrel axis printed horizontally → round bore without support.
- **Living hinge**: layer lines must run **perpendicular to the bend axis**; print flat with the hinge web horizontal.
- **Snap-fit**: arm parallel to the print bed for maximum flexural strength.
- **Dovetail**: 45° angle = support-free overhang on any FDM printer.
- **Standoff**: printed vertically for best bore roundness.
- All press-fit / clearance dimensions use DIN ISO 2768 tolerance classes (`"f"` fine, `"m"` medium, `"c"` coarse, `"v"` very coarse).
