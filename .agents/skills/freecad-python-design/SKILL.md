---
name: freecad-python-design
description: "Use when: creating new 3D designs with Python for FreeCAD, designing parametric models, building mechanical parts with standard components (screws, nuts, holes), exporting STL files. Also use for snap-fit clips, living hinges, dovetail joints, cable clips, wall brackets, hooks, knobs, standoffs, and enclosure lids available in the part_library. Includes templates for document setup, shape creation, boolean operations, hardware component integration, and ready-made parametric building blocks."
---

# FreeCAD Python 3D Design Workflow

## Overview
This skill provides a structured workflow for creating parametric 3D designs in FreeCAD using Python. It leverages the custom `freecad_lib` library for DIN/ISO-compliant components, shape primitives, and boolean operations.

## Quick Start Template

```python
import FreeCAD, Part
from FreeCAD import Vector
from freecad_lib import *
# Optional: parametric building blocks
# from src.part_library import BoxLid, EnclosureBox, Hinge, SnapHook, SnapReceptor, LivingHinge, CableClip, Standoff, WallBracket, JHook, SHook, Knob, DovetailRail, DovetailSlider

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

#### **Flat** - Custom 2D profile from a list of vertices
```python
# Flat takes a closed list of Vectors (last == first) and an optional
# list of rounding radii (joints) at each vertex, then builds a planar
# face ready for extrusion.
#
# Use Flat when you need an irregular or non-standard 2D cross-section
# that Box / Polygon cannot express.

# Triangle (no rounding):
triangle = Flat(
    vertices=[Vector(0, 0, 0), Vector(50, 0, 0), Vector(25, 40, 0), Vector(0, 0, 0)]
)
wedge_solid = triangle.face.extrude(Vector(0, 0, 10))

# L-profile with optional rounded corners:
l_verts = [
    Vector(0, 0, 0), Vector(40, 0, 0), Vector(40, 10, 0),
    Vector(10, 10, 0), Vector(10, 30, 0), Vector(0, 30, 0),
    Vector(0, 0, 0)
]
l_profile = Flat(vertices=l_verts)
l_solid = l_profile.face.extrude(Vector(0, 0, 5))

# Properties:
flat.wire    # Part.Wire
flat.face    # Part.Face (ready to .extrude())
flat.normal  # auto-computed face normal
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

#### **Sphere** - Ball primitive
```python
sphere = Sphere(radius=20, position=Vector(0, 0, 0))
sphere.solid
```

#### **Cone** - Cone or truncated cone
```python
# Sharp cone (radius2=0)
cone = Cone("tip", radius1=15, radius2=0, height=40, position=Vector(0, 0, 0), normal=Vector(0, 0, 1))

# Truncated cone (frustum)
frustum = Cone("frustum", radius1=20, radius2=10, height=30)

# Properties:
cone.radius1, cone.radius2, cone.height
cone.solid
```

#### **Torus** - Donut / ring shape
```python
torus = Torus(radius_major=30, radius_minor=8, position=Vector(0, 0, 0), normal=Vector(0, 0, 1))
torus.solid
```

#### **Bullet** - Cylinder with hemispherical tip
```python
# Total height includes the hemisphere radius at the top
bullet = Bullet("proj", diameter=10, height=30, position=Vector(0, 0, 0), normal=Vector(0, 0, 1))
# → cylinder from z=0..25 plus hemisphere of r=5 at z=25..30
bullet.solid
```

#### **Tube** - Hollow cylinder (pipe)
```python
tube = Tube("pipe", outer_diameter=20, wall_thickness=2, height=50, position=Vector(0, 0, 0))
tube.inner_diameter  # = outer_diameter - 2 * wall_thickness
tube.solid
```

#### **Wedge** - Triangular prism
```python
# Isosceles triangle in XZ plane, extruded along Y
wedge = Wedge("ramp", length=40, width=20, height=15, position=Vector(0, 0, 0))
wedge.solid
```

#### **Ellipsoid** - Scaled sphere
```python
# Semi-axes rx (X), ry (Y), rz (Z)
egg = Ellipsoid(rx=15, ry=15, rz=25, position=Vector(0, 0, 0))
egg.solid
```

#### **Capsule** - Cylinder with hemispherical caps on both ends (pill shape)
```python
# height must be >= diameter; cylindrical section = height - diameter
capsule = Capsule("pill", diameter=10, height=30, position=Vector(0, 0, 0), normal=Vector(0, 0, 1))
capsule.solid
```

#### **Slot** - Elongated hole / oblong (rounded rectangle extruded)
```python
# Centered at position, elongated along direction, extruded depth along normal
slot = Slot("slot", length=20, width=6, depth=10,
            position=Vector(0, 0, 0), normal=Vector(0, 0, 1), direction=Vector(1, 0, 0))
body = body.cut(slot.solid)
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

### 5. 3D-Print Specific Features

#### **CountersinkHole** - Cone entry for flat-head (DIN 7991) screws
```python
# Look up standard dimensions from COUNTERSINK_MAP:
# COUNTERSINK_MAP["M3"] = {"dK": 5.6, "d": 3.4, "k": 1.7}
cs = CountersinkHole(
    name="cs_m3",
    hole_diameter=COUNTERSINK_MAP["M3"]["d"],     # 3.4 mm clearance hole
    countersink_diameter=COUNTERSINK_MAP["M3"]["dK"],  # 5.6 mm head cone
    depth=10,                                     # through-hole depth below cone
    position=Vector(0, 0, 10),
    normal=Vector(0, 0, -1),   # going down into the part
)
body = body.cut(cs.solid)

# Custom angle (default 45° half-angle = 90° included):
cs = CountersinkHole("cs", 3.4, 6.0, 8, angle=45)
```

#### **CounterboreHole** - Flat-bottomed recess for socket-head cap screws
```python
# M5 ISO 4762 socket head: dK=8.5mm, k(head height)=4mm
cb = CounterboreHole(
    name="cb_m5",
    hole_diameter=5.5,    # thread clearance hole
    bore_diameter=9.0,    # head diameter + clearance
    bore_depth=5.0,       # head height + clearance
    total_depth=20,
    position=Vector(0, 0, 0),
)
body = body.cut(cb.solid)
```

#### **NutTrap** - Blind hex pocket to capture a DIN nut
```python
# Very common in 3D printing: pocket in the side of a part traps a standard nut
trap = NutTrap("trap_m3", "M3", position=Vector(0, 0, 5), normal=Vector(0, 1, 0))
body = body.cut(trap.solid)

# extra_depth=1.0: adds 1mm buffer above nut (thin plastic membrane)
trap = NutTrap("trap_m3", "M3", extra_depth=1.0)
```

#### **HeatSetInsert** - Pocket for heat-set threaded brass inserts
```python
# Ruthex / CNC Kitchen standard dimensions (HEAT_SET_INSERT_MAP)
hs = HeatSetInsert("hs_m3", "M3", position=Vector(0, 0, 10), normal=Vector(0, 0, -1))
body = body.cut(hs.solid)

# Available: M2, M3, M4, M5
# HEAT_SET_INSERT_MAP["M3"] = {"pocket_d": 4.7, "pocket_l": 6.0}
```

#### **BearingPocket** - Press-fit pocket for standard ball bearings
```python
# BEARING_MAP keys: "608", "624", "625", "626", "688", "6200", "6201", "6202", "6203", "6204"
pocket = BearingPocket("bp608", "608", position=Vector(0, 0, 0), tolerance="f")
body = body.cut(pocket.solid)

# Add shaft hole separately:
shaft = Cylinder("shaft", pocket.bore, 30, Vector(0, 0, 0))
body = body.cut(shaft.solid)

# Properties:
pocket.bore            # = 8 mm (for 608)
pocket.outer_diameter  # = 22 mm
pocket.bearing_width   # = 7 mm (= pocket depth)
```

#### **MagnetPocket** - Blind recess for a neodymium disc magnet
```python
# MAGNET_SIZES keys: "5x1", "5x2", "6x2", "8x2", "10x2", "10x3", "12x2", "12x3", "20x3"
mag = MagnetPocket("mag", "10x2", position=Vector(20, 0, 0), clearance=0.2)
body = body.cut(mag.solid)
```

### 6. Boolean Operations

```python
# Union (add parts together)
body = body.fuse(other_part.solid)

# Subtraction (cut holes, remove volume)
body = body.cut(hole.solid)

# Intersection (keep only overlapping volume)
body = body.common(overlap.solid)

# Fuse a list of solids in one call
body = fuse_all([part1, part2, part3])

# Cut multiple shapes from a base in one call
body = cut_all(base, [hole1, hole2, slot])
```

### 6. Transformations

#### **move / translate** - Shift a solid
```python
moved = move(solid, Vector(10, 0, 0))      # shift 10 mm in X
moved = translate(solid, Vector(0, 5, 0))  # alias
```

#### **rotate** - Rotate a solid
```python
# rotate(solid, angle_deg, axis, center)
rotated = rotate(solid, 45)                                  # 45° around Z at origin
rotated = rotate(solid, 90, Vector(1, 0, 0))                 # 90° around X
rotated = rotate(solid, 30, Vector(0, 0, 1), Vector(5, 5, 0))  # 30° around Z at (5,5,0)
```

#### **mirror** - Mirror a solid
```python
mirrored   = mirror(solid, plane_normal=Vector(1, 0, 0), plane_origin=Vector(0, 0, 0))
mirrored_x = mirror_x(solid, x=0)   # mirror across YZ plane at x=0
mirrored_y = mirror_y(solid, y=10)  # mirror across XZ plane at y=10
mirrored_z = mirror_z(solid, z=5)   # mirror across XY plane at z=5
```

#### **scale** - Uniform scaling from origin
```python
bigger = scale(solid, 1.5)   # 150 %
smaller = scale(solid, 0.5)  # 50 %
```

### 7. Pattern / Array Utilities

#### **array_linear** - Linear (rectangular) pattern
```python
# array_linear(solid, direction, count, spacing)
row = array_linear(hole.solid, Vector(1, 0, 0), count=5, spacing=20)
# → 5 copies along X, 20 mm apart (original at i=0 included)
body = body.cut(row)
```

#### **array_polar** - Circular / polar pattern
```python
# array_polar(solid, count, axis, center)
ring = array_polar(hole.solid, count=6, axis=Vector(0, 0, 1), center=Vector(0, 0, 0))
# → 6 copies evenly distributed at 60° intervals
body = body.cut(ring)
```

### 8. Visualization & Display

#### **show()** - Display a freecad_lib object
```python
show(
    part=box_obj,       # must be a freecad_lib object with .solid attribute
    transparancy=50,    # 0-100 (0=opaque, 100=transparent)
    color=(0.5, 0.5, 0.5),  # RGB tuple (0-1 range)
    name="body"
)
```

#### **show_solid()** - Display a raw Part solid
```python
# Use this after boolean operations (body.cut / body.fuse return a raw solid)
show_solid(body, transparancy=0, color=(0.2, 0.6, 0.8), name="part")

# Common colors:
# Red: (1, 0, 0)   Green: (0, 1, 0)   Blue: (0, 0, 1)
# Yellow: (1, 1, 0)   Gray: (0.5, 0.5, 0.5)   Gold: (247/255, 197/255, 79/255)
```

### 9. Tolerances

#### **GeneralTolerances** - DIN ISO 2768 lookup
```python
tolerances = GeneralTolerances()

# Get tolerance for a dimension:
# get_tolerance(length, tolerance_class)
tolerance_value = tolerances.get_tolerance(50, "m")  # 50mm, medium tolerance

# Tolerance classes: "f" (fine), "m" (medium), "c" (coarse), "v" (very coarse)
# Returns absolute tolerance in mm based on dimension range
```

---

## Part Library (`src/part_library/`)

Ready-made parametric 3D-printable building blocks built on top of `freecad_lib`. Import with:

```python
from src.part_library import (
    Hinge, HingeLeafA, HingeLeafB, HingePin,
    SnapFit, SnapHook, SnapReceptor,
    LivingHinge,
    CableClip,
    Standoff,
    WallBracket,
    JHook, SHook,
    Knob,
    BoxLid, EnclosureBox,
    DovetailJoint, DovetailRail, DovetailSlider,
)
```

Each class exposes a `.solid` attribute and a set of keyword parameters with sensible defaults. All dimensions are in **mm**.

### Hinge — Parametric 3D-printable barrel hinge
```python
from src.part_library import Hinge, HingeLeafA, HingeLeafB, HingePin

# Full assembly (two leaves + pin)
hinge = Hinge(
    leaf_width=30,       # barrel axis length
    leaf_length=40,      # leaf plate depth
    leaf_thickness=3,    # leaf plate thickness
    barrel_diameter=8,   # knuckle outer diameter
    barrel_inner_d=3,    # pin bore diameter
    knuckle_count=3,     # number of knuckle segments
    pin_clearance=0.25,  # radial gap between pin and bore
    knuckle_gap=0.3,     # axial gap between knuckles
    hole_diameter=3.5,   # mounting holes in each leaf
    holes_per_leaf=2,
)
hinge.leaf_a.solid  # first leaf Part.Shape
hinge.leaf_b.solid  # second leaf Part.Shape
hinge.pin.solid     # pin Part.Shape

# Or use individual components:
leaf_a = HingeLeafA(leaf_width=30, leaf_length=40, ...)
leaf_b = HingeLeafB(leaf_width=30, leaf_length=40, ...)
pin    = HingePin(barrel_inner_d=3, leaf_width=30)
```

### SnapHook / SnapReceptor — Cantilever snap-fit clip
```python
from src.part_library import SnapHook, SnapReceptor, SnapFit

# Male (hook) part — cantilever arm with a wedge tip
hook = SnapHook(
    base_width=20,
    base_length=20,
    base_thickness=4,
    arm_width=10,
    arm_length=25,
    arm_thickness=2,
    hook_height=2.5,
    hook_lead_angle=30,       # ramp angle for snap-in (~30°)
    hook_retention_angle=80,  # near-vertical face for retention
    hole_diameter=3.5,
)
hook.solid

# Female (receptor) part — rectangular block with a through-slot
receptor = SnapReceptor(
    arm_width=10,
    arm_thickness=2,
    hook_height=2.5,
    receptor_wall=3,
    receptor_depth=20,
    clearance=0.25,
)
receptor.solid

# Preview assembly (hook + receptor positioned together)
assembly = SnapFit(hook=hook, receptor=receptor)
assembly.solid  # fused preview
```

### LivingHinge — Thin flexible web between two rigid panels
```python
from src.part_library import LivingHinge

hinge = LivingHinge(
    panel_width=40,       # X dim of each rigid side panel
    panel_length=60,      # Y dim
    panel_thickness=3,    # Z thickness of rigid panels
    hinge_width=20,       # Y span of the flex web (≤ panel_length)
    hinge_length=8,       # X span of the flex web
    hinge_thickness=0.6,  # FDM minimum ≈ 0.6 mm (1-2 layers)
    num_notches=5,        # stress-relief semicircular notches
    notch_radius=2.0,
)
hinge.solid               # complete panel
hinge.left_panel_solid
hinge.hinge_solid
hinge.right_panel_solid
# PRINT ORIENTATION: layer lines must run along X (perpendicular to bend axis Y)
```

### CableClip — Saddle clamp for cables or tubes
```python
from src.part_library import CableClip

clip = CableClip(
    cable_diameter=8.0,    # outer diameter of cable/tube
    cable_clearance=0.3,   # extra radial clearance
    wall_thickness=2.5,    # wall around the cable groove
    base_thickness=3.0,    # foot plate thickness
    mount_margin=5.0,      # extra width on each side for holes
    hole_diameter=3.5,     # mounting screw hole diameter
    num_holes=2,           # 1 (centre) or 2 (left+right)
)
clip.solid
```

### Standoff — PCB spacer / pillar
```python
from src.part_library import Standoff

standoff = Standoff(
    outer_diameter=8.0,   # body outer diameter (or circumscribed circle for hex)
    inner_diameter=3.2,   # bore for M3 screw
    height=10.0,
    shape="round",        # "round" or "hex"
    chamfer=0.5,          # lead-in chamfer radius at bore entries
    base_flange=0,        # outer diameter of base flange disc (0 = none)
)
standoff.solid
```

### WallBracket — L-shaped shelf bracket with gusset
```python
from src.part_library import WallBracket

bracket = WallBracket(
    wall_plate_width=40,
    wall_plate_height=60,
    plate_thickness=4,
    shelf_plate_width=40,
    shelf_plate_depth=50,
    gusset=True,           # triangular reinforcement at inner corner
    hole_diameter=4.5,
    holes_per_wall=3,
    holes_per_shelf=2,
    hole_margin=8,
)
bracket.solid
```

### JHook / SHook — Wall-mounted hooks
```python
from src.part_library import JHook, SHook

# J-hook: mounts to wall, arm extends horizontally, tip curves down
jhook = JHook(
    base_width=30,
    base_height=40,
    base_thickness=4,
    stem_height=50,
    arm_length=40,
    arm_angle=10,       # upward tilt of arm (degrees)
    profile_w=8,
    profile_d=8,
    tip_drop=10,
    hole_diameter=4.5,
    holes_per_base=2,
    hole_margin=8,
)
jhook.solid

# S-hook: free-hanging, hooks onto a rail; both ends have opposing curves
shook = SHook(
    total_height=80,
    arm_length=30,
    profile_w=8,
    profile_d=8,
    tip_drop=10,
)
shook.solid
```

### Knob — Knurled thumb-screw knob
```python
from src.part_library import Knob

knob = Knob(
    diameter=30.0,          # outer diameter
    height=15.0,
    rib_count=18,           # number of vertical grip grooves
    rib_height=8.0,         # height of the ribbed zone
    rib_depth=1.2,          # groove depth
    insert_type="heat_set", # "heat_set" or "nut_trap"
    insert_size="M4",
    top_chamfer=1.5,        # 45-degree bevel on top outer edge
)
knob.solid
```

### BoxLid / EnclosureBox — Snap-fit enclosure
```python
from src.part_library import BoxLid, EnclosureBox

# Lid with snap tabs
lid = BoxLid(
    lid_length=100.0,
    lid_width=70.0,
    panel_thickness=2.0,
    skirt_height=6.0,
    skirt_thickness=1.8,
    snap_height=1.5,
    snap_count=2,         # tabs per long side
    snap_lead_angle=30,   # ramp angle for easy snap-in
    clearance=0.2,
)
lid.solid

# Matching open-top box body
box = EnclosureBox(
    inner_length=100.0,
    inner_width=70.0,
    inner_height=50.0,
    wall=2.5,
)
box.solid
```

### DovetailRail / DovetailSlider / DovetailJoint — Sliding dovetail joint
```python
from src.part_library import DovetailRail, DovetailSlider, DovetailJoint

# Female rail (the groove, cut into a base part)
rail = DovetailRail(
    rail_length=80,
    rail_width=14,        # total rail base width
    rail_height=8,        # total height of the trapezoidal protrusion
    neck_width=8,         # narrow width at top of dovetail
    base_thickness=2,     # flat base below the trapezoid
)
rail.solid

# Male slider (the protruding tongue that rides in the rail)
slider = DovetailSlider(
    slider_length=30,
    rail_width=14,
    rail_height=8,
    neck_width=8,
    base_thickness=2,
    clearance=0.2,        # radial gap for smooth sliding
)
slider.solid

# Preview assembly (rail + slider positioned together)
joint = DovetailJoint(rail=rail, slider=slider)
joint.solid
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

### Pattern 4: Symmetry with Mirror
```python
# Design one half, mirror it, fuse
half = Box(Vector(0, 0, 0), Vector(50, 30, 10)).solid
slot = Cylinder("slot", 5, 10, Vector(25, 5, 0))
half = half.cut(slot.solid)

# Mirror across YZ plane and fuse both halves
full = half.fuse(mirror_x(half))
```

### Pattern 5: Polar / Circular Patterns
```python
# 6 mounting holes on a bolt circle (Lochkreis)
hole = Cylinder("hole", 3.5, 10, Vector(30, 0, 0))   # offset from center
holes = array_polar(hole.solid, count=6)               # 60° steps
body = body.cut(holes)
```

### Pattern 6: Linear Array / Grid
```python
# 3×4 grid of pins
pin = Cylinder("pin", 2, 5, Vector(0, 0, 10))
row = array_linear(pin.solid, Vector(1, 0, 0), count=3, spacing=10)
grid = array_linear(row, Vector(0, 1, 0), count=4, spacing=10)
body = body.fuse(grid)
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
src/
├── freecad_lib.py          # Core library — primitives, transforms, hardware
└── part_library/           # Ready-made parametric building blocks
    ├── __init__.py         # Import all components from here
    ├── hinge.py            # Barrel hinge (Hinge, HingeLeafA/B, HingePin)
    ├── snap_fit.py         # Snap-fit clips (SnapHook, SnapReceptor, SnapFit)
    ├── living_hinge.py     # Flexible living hinge panel (LivingHinge)
    ├── cable_clip.py       # Cable saddle clamp (CableClip)
    ├── standoff.py         # PCB standoff / spacer (Standoff)
    ├── wall_bracket.py     # L-shaped wall bracket (WallBracket)
    ├── hook.py             # Wall hooks (JHook, SHook)
    ├── knob.py             # Knurled thumb knob (Knob)
    ├── box_lid.py          # Snap-fit enclosure (BoxLid, EnclosureBox)
    └── dovetail.py         # Sliding dovetail joint (DovetailRail, DovetailSlider, DovetailJoint)
projekte/
└── YourProject.py          # Your design file
stl/
└── YourProject.stl         # STL export destination
fonts/
└── TC_LaserSans.TTF        # Available fonts for SolidText
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
9. **Transformations return new solids**: `move`, `rotate`, `mirror`, `scale` never modify the original — always assign the result
10. **Patterns produce fused solids**: `array_linear` / `array_polar` return one ready-to-use solid (or cut shape)

## Reference: Available DIN Components

**Nut Sizes** (M1 to M10): All include automatic clearance calculation
**Screw Sizes** (M1.4 to M10): Head + thread with tolerance classes
**Tolerance Classes**: f (±0.05-2.5mm), m (±0.10-3mm), c (±0.20-5mm), v (±0.35-12mm)

## Reference: Part Library Quick-Picks

| Need | Class | Module |
|------|-------|--------|
| Barrel hinge | `Hinge` / `HingeLeafA` + `HingeLeafB` + `HingePin` | `hinge.py` |
| Snap-fit clip | `SnapHook` + `SnapReceptor` | `snap_fit.py` |
| Flexible living hinge | `LivingHinge` | `living_hinge.py` |
| Cable / tube clamp | `CableClip` | `cable_clip.py` |
| PCB spacer pillar | `Standoff` | `standoff.py` |
| Shelf / wall bracket | `WallBracket` | `wall_bracket.py` |
| Wall-mounted J-hook | `JHook` | `hook.py` |
| Free-hanging S-hook | `SHook` | `hook.py` |
| Thumb-screw knob | `Knob` | `knob.py` |
| Box + snap lid | `BoxLid` + `EnclosureBox` | `box_lid.py` |
| Sliding dovetail | `DovetailRail` + `DovetailSlider` | `dovetail.py` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Shape not visible | Check that `show()` is called; verify Vector() coordinates are reasonable |
| Boolean cut produces wrong result | Ensure cutting shape extends fully through volume (use 1.5x height) |
| Export file empty | Verify document name matches string in `export(doc, obj)` |
| Font not found | Verify font path in `SolidText`; fonts are in the workspace `fonts/` directory |
| Part library import fails | Ensure the workspace root is on `sys.path`; `src/part_library/` is imported via `from src.part_library import ...` |
| Part not centered | Use negative/positive Vectors correctly: `Vector(-W/2, 0, 0)` to `Vector(W/2, H, D)` |
