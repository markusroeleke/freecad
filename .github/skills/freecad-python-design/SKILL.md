---
name: freecad-python-design
description: "Use when: creating new 3D designs with Python for FreeCAD, designing parametric models, building mechanical parts with standard components (screws, nuts, holes), exporting STL files. Includes templates for document setup, shape creation, boolean operations, and hardware component integration."
---

# FreeCAD Python 3D Design Workflow

## Overview
This skill provides a structured workflow for creating parametric 3D designs in FreeCAD using Python. It leverages the custom `freecad_lib` library for DIN/ISO-compliant components, shape primitives, and boolean operations.

## Quick Start Template

```python
import FreeCAD, Part
from FreeCAD import Vector
from freecad_lib import *

# 1. Create and configure document
new_doc('ProjectName')

# 2. Define parameters (all in mm)
width = 100
height = 50
thickness = 10

# 3. Create base shape
body = Box(Vector(-width/2, 0, 0), Vector(width/2, height, thickness)).solid

# 4. Apply boolean operations
hole = Cylinder("hole", 10, thickness, Vector(0, 25, 0))
body = body.cut(hole.solid)

# 5. Display result
show(Box(Vector(-width/2, 0, 0), Vector(width/2, height, thickness)), name="body")

# 6. Export STL
export('ProjectName', "body")

# 7. Render viewport
FreeCADGui.activeDocument().activeView().viewIsometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
```

## Core Components

### 1. Document Management

**Create Document:**
```python
new_doc('DocumentName')
FreeCADGui.runCommand('Std_DrawStyle', 6)  # shaded wireframe (optional)
```

**Fit View & Display:**
```python
fit_view()  # Isometric + auto-fit
# OR manually:
FreeCADGui.activeDocument().activeView().viewIsometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
```

**Export to STL:**
```python
export('DocumentName', 'ObjectName')  # Creates stl/ObjectName.stl
```

### 2. Coordinate System & Vectors

All coordinates in **millimeters (mm)**. Using mnemonic naming:

| Axis | X (length) | Y (breadth) | Z (height) |
|------|----------|----------|---------|
| West/East | **w** (X-) | - | - |
| Center | **c** | **m** (Y0) | **g** (Z0) |
| East | **e** (X+) | - | - |
| South | - | **s** (Y-) | - |
| North | - | **n** (Y+) | - |
| Down | - | - | **d** (Z-) |
| Up | - | - | **u** (Z+) |

Example: `Vector(w, s, d) → Vector(-50, -30, 0)` = southwest, ground level

### 3. Primitive Shapes

#### **Box** - Rectangular solid with optional rounded corners
```python
# Syntax: Box(Vector_WestSouthDown, Vector_EastNorthUp, [rounded_corner_joints])
box = Box(Vector(-width/2, 0, 0), Vector(width/2, height, thickness))

# With rounded corners (specify one corner radius, auto-applies to all 4)
box = Box(
    Vector(-width/2, 0, 0), 
    Vector(width/2, height, thickness),
    [Vector(5, 5, 0)]  # 5mm radius on all corners
)

# Access properties:
box.w, box.e  # west/east X positions
box.s, box.n  # south/north Y positions
box.d, box.u  # down/up Z positions
box.c, box.m, box.g  # center points
box.l, box.b, box.h  # length, breadth, height
box.solid  # the Part.Solid object
```

#### **Cylinder** - Circular symmetric shape
```python
# Syntax: Cylinder(name, diameter, height, position, normal_direction)
cylinder = Cylinder("cyl", 10, 50, Vector(0, 25, 0), Vector(0, 0, 1))

# Properties:
cylinder.diameter
cylinder.height
cylinder.solid
```

#### **Polygon** - Base 2D shape (circle or regular polygon)
```python
# Circle:
circle = Polygon(center=Vector(0, 0, 0), radius=5, normal=Vector(0, 0, 1))

# Regular polygon:
hexagon = Polygon(
    center=Vector(0, 0, 0), 
    radius=10, 
    normal=Vector(0, 0, 1), 
    sides=6,  # hexagon
    twist=0
)

# Properties:
polygon.face  # Part.Face object
polygon.wire  # Part.Wire object
```

#### **Polyhedron** - 3D solid lofted between two polygons
```python
poly1 = Polygon(Vector(0, 0, 0), 5, Vector(0, 0, 1))
poly2 = Polygon(Vector(0, 0, 50), 5, Vector(0, 0, 1))
polyhedron = Polyhedron(poly1, poly2)
polyhedron.solid
```

#### **Quader** - Convenience box centered at origin
```python
quader = Quader(name="box", length=100, width=80, height=50, position=Vector(0, 0, 0))
```

### 4. Hardware Components (DIN/ISO Standard)

#### **Nut** - Hexagonal nut with clearance
```python
nut = Nut(
    name="nut_m5",
    size="M5",  # M1 to M10 supported
    position=Vector(0, 0, 0),
    normal=Vector(0, 0, 1),
    screw_type="normal"  # or "slide" for sliding nuts
)

# Available sizes: M1, M1.2, M1.4, M1.6, M1.7, M2, M2.3, M2.5, M2.6, M3, M3.5, M4, M5, M6, M7, M8, M10
# screw_type "normal": full clearance around nut
# screw_type "slide": additional rectangular clearance for nut insertion
```

#### **Screw** - Bolt head + thread with clearance
```python
screw = Screw(
    name="screw_m5",
    size="M5",
    thread_length=20,
    position=Vector(0, 0, 0),
    normal=Vector(0, 0, 1),
    tolerance_class="m"  # f: fine, m: medium, c: coarse, v: very coarse
)

# Available sizes: M1.4, M1.6, M2, M2.5, M3, M3.5, M4, M5, M6, M8, M10
```

#### **SolidText** - 3D embossed text
```python
text = SolidText(
    text="MyText",
    position=Vector(0, 0, 0),
    height=5,  # extrusion depth (mm)
    txt_height=6,  # font size
    spacing=0.5,
    font="TC_LaserSans.TTF"  # available in fonts/ folder
)
```

### 5. Boolean Operations

```python
# Union (add parts together)
body = body.fuse(other_part.solid)

# Subtraction (cut holes, remove volume)
body = body.cut(hole.solid)

# Intersection (keep only overlapping volume)
body = body.common(overlap.solid)
```

### 6. Visualization & Display

#### **show()** - Display shape with transparency and color
```python
show(
    part=body,
    transparancy=50,  # 0-100 (0=opaque, 100=transparent)
    color=(0.5, 0.5, 0.5),  # RGB tuple (0-1 range)
    name="body"
)

# Common colors:
# Red: (1, 0, 0)
# Green: (0, 1, 0)
# Blue: (0, 0, 1)
# Yellow: (1, 1, 0)
# Gray: (0.5, 0.5, 0.5)
# Gold: (247/255, 197/255, 79/255)
```

#### **Clearance Variables**
Predefined clearance vectors for tolerance levels:
```python
clearance = {
    "very_loose": Vector(1.5, 1.5, 1.5),
    "loose": Vector(1, 1, 1),
    "middle": Vector(0.6, 0.6, 0.6),
    "tight": Vector(0.2, 0.2, 0.2)
}
```

### 7. Tolerances

#### **GeneralTolerances** - DIN ISO 2768 lookup
```python
tolerances = GeneralTolerances()

# Get tolerance for a dimension:
# get_tolerance(length, tolerance_class)
tolerance_value = tolerances.get_tolerance(50, "m")  # 50mm, medium tolerance

# Tolerance classes: "f" (fine), "m" (medium), "c" (coarse), "v" (very coarse)
# Returns absolute tolerance in mm based on dimension range
```

## Design Patterns

### Pattern 1: Base + Features
```python
# Start with simple base
body = Box(Vector(-50, -50, 0), Vector(50, 50, 10)).solid

# Add details
hole1 = Cylinder("hole1", 5, 10, Vector(-25, -25, 0))
body = body.cut(hole1.solid)

hole2 = Cylinder("hole2", 5, 10, Vector(25, 25, 0))
body = body.cut(hole2.solid)
```

### Pattern 2: Parametric Design
```python
# Define all dimensions as parameters at the top
WIDTH = 100
HEIGHT = 80
THICKNESS = 10
CORNER_RADIUS = 5

# Use parameters throughout
box = Box(
    Vector(-WIDTH/2, 0, 0), 
    Vector(WIDTH/2, HEIGHT, THICKNESS),
    [Vector(CORNER_RADIUS, CORNER_RADIUS, 0)]
)
```

### Pattern 3: Clearance for Assembly
```python
# Create actual part
part = Cylinder("bolt", 5, 20)

# Add generous clearance for assembly
clearance = Cylinder("clearance", 5.5, 22, Vector(0, 0, -1))
assembly_space = assembly_space.fuse(clearance.solid)
```

## Common Tasks

### Draw a rectangular box with a hole
```python
new_doc('BoxWithHole')

# Box dimensions
box = Box(Vector(-50, -30, 0), Vector(50, 30, 10))
body = box.solid

# Create hole (5mm diameter, full height)
hole = Cylinder("hole", 5, 10, Vector(0, 0, 0))
body = body.cut(hole.solid)

show(box, name="body")
```

### Create a mounting bracket
```python
new_doc('Bracket')

# Main body
body = Box(Vector(0, 0, 0), Vector(80, 20, 60)).solid

# Mounting holes (M4 clearance: ~4.5mm)
for y in [5, 15]:
    for z in [10, 50]:
        hole = Cylinder("hole", 4.5, 20, Vector(-5, y, z), Vector(1, 0, 0))
        body = body.cut(hole.solid)

# Reduce weight (optional internal cutout)
cutout = Box(Vector(5, 2, 20), Vector(75, 18, 40))
body = body.cut(cutout.solid)

show(Box(Vector(0, 0, 0), Vector(80, 20, 60)), name="bracket")
export('Bracket', 'bracket')
```

### Add text label
```python
label = SolidText(
    text="v1.0",
    position=Vector(-10, -15, 9),
    height=2,
    txt_height=5,
    font="TC_LaserSans.TTF"
)
body = body.fuse(label.solid)
```

## Workflow Checklist

- [ ] Import FreeCAD, Part, Vector, freecad_lib
- [ ] Create document with `new_doc('Name')`
- [ ] Define all dimensions as top-level parameters
- [ ] Create base shape (Box, Cylinder, or Polyhedron)
- [ ] Apply features (holes, cutouts, details) using boolean cut/fuse
- [ ] Add hardware components (Nut, Screw) if needed
- [ ] Add text labels if needed
- [ ] Test with `show()` to verify appearance
- [ ] Adjust transparency/color if needed
- [ ] Export to STL with `export(doc, obj)`
- [ ] Fit view for final rendering

## File Organization

```
projekte/
├── freecad_lib.py          # Shared library (import this)
├── YourProject.py          # Your design file
└── stl/                     # Export destination
    └── YourProject.stl
fonts/
└── TC_LaserSans.TTF        # Available fonts
```

## Tips & Best Practices

1. **Parameterize everything**: Put all dimensions at the top of the file for easy tweaking
2. **Use meaningful names**: Cylinder names like "hole_mounting_1" are clearer than "cyl"
3. **Test intermediate steps**: Show each major feature to verify it looks correct
4. **Built-in clearances**: Nut/Screw classes automatically include DIN-compliant clearances
5. **Cardinal directions**: Use w/e/s/n/d/u mnemonics for readable coordinate expressions
6. **Boolean operation order**: Apply cuts last to prevent floating geometry
7. **Export early and often**: Verify STL output matches your expectations before final assembly
8. **Color coding**: Use different colors for different functional areas (red=cutting surfaces, blue=mounting, etc.)

## Reference: Available DIN Components

**Nut Sizes** (M1 to M10): All include automatic clearance calculation
**Screw Sizes** (M1.4 to M10): Head + thread with tolerance classes
**Tolerance Classes**: f (±0.05-2.5mm), m (±0.10-3mm), c (±0.20-5mm), v (±0.35-12mm)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Shape not visible | Check that `show()` is called; verify Vector() coordinates are reasonable |
| Boolean cut produces wrong result | Ensure cutting shape extends fully through volume (use 1.5x height) |
| Export file empty | Verify document name matches string in `export(doc, obj)` |
| Font not found | Check font path: `/Users/Markus/Documents/Projekte/FreeCAD/fonts/` |
| Part not centered | Use negative/positive Vectors correctly: `Vector(-W/2, 0, 0)` to `Vector(W/2, H, D)` |
