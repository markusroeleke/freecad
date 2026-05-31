# Part Library – Technical Specifications (FDM 3D Printing)

Research document for TODO step 01.  
All dimensions in **mm**. CSG notes use `freecad_lib` primitives (`Box`, `Cylinder`, `Tube`,
`Polygon`/`Polyhedron`, `Wedge`, `Cone`). Boolean ops: `fuse` = union, `cut` = subtract.

---

## A. Barrel / Pin Hinge

### Description / Purpose
Two symmetric knuckle leaves joined by a cylindrical barrel that consists of
interleaved barrel segments. A removable pin (rod) runs through all segments along the
hinge axis. Produces a full 180 ° rotation joint that can be disassembled.  
Typical use: box lids, enclosures, access panels, tool cases.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Wall thickness (leaf body) | ≥ 2.0 mm (≥ 3 × extrusion width) |
| Barrel wall thickness | ≥ 1.6 mm; print as solid (100 % infill cylinder shell) |
| Overhang | Print hinge axis **horizontal**; barrel overhangs ≤ 45 ° — no supports needed when diameter ≤ 12 mm |
| Pin clearance | 0.2–0.3 mm diametral clearance between pin OD and barrel bore |
| Segment interleave clearance | 0.2–0.3 mm axial gap between adjacent knuckles |
| Leaf-to-leaf clearance | 0.1–0.2 mm gap on mating faces so leaves can rotate freely |
| Print orientation | Hinge axis lies flat (Z axis = perpendicular to hinge axis) |
| Min segments | ≥ 3 (2 on one leaf, 1 on other) for stability |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `leaf_w` | 30 | Leaf width (perpendicular to hinge axis), mm |
| `leaf_h` | 40 | Leaf height (along hinge axis), mm |
| `leaf_t` | 3 | Leaf plate thickness, mm |
| `barrel_d` | 8 | Barrel outer diameter, mm |
| `pin_d` | 3 | Pin (rod) diameter, mm |
| `n_knuckles` | 3 | Total number of knuckle segments (odd = one leaf gets (n+1)/2) |
| `knuckle_gap` | 0.25 | Axial clearance between adjacent knuckle faces, mm |
| `leaf_gap` | 0.15 | Face clearance between the two leaves, mm |
| `hole_d` | 3.2 | Fastener hole diameter in each leaf, mm |
| `hole_margin` | 5 | Distance from hole centre to leaf edge, mm |
| `n_holes` | 2 | Number of fastener holes per leaf |

### CSG Construction Notes

```
LEAF_A (solid):
  base  = Box( [0, 0, 0] → [leaf_t, leaf_w, leaf_h] )
  knuckle_i (for each of leaf_A's segments):
      cyl = Cylinder(d=barrel_d, h=knuckle_h_i, pos on hinge axis)
      base = base.fuse(cyl)
  bore = Cylinder(d=pin_d + 2*clearance, h=leaf_h, aligned on barrel axis)
  base = base.cut(bore)
  for each hole: base = base.cut( Cylinder(d=hole_d, h=leaf_t) )

LEAF_B  ← mirror of LEAF_A, shifted by leaf_gap along Z, staggered knuckles

PIN:
  pin = Cylinder(d=pin_d, h=leaf_h + 2)   # 1 mm proud each end
  (printed separately; drop in after assembly)
```

**Assembly:** Interleave LEAF_A and LEAF_B knuckles along the axis, then slide PIN in.

---

## B. Cantilever Snap-Fit Clip

### Description / Purpose
A single elastic beam (arm) that bends as the mating part is pushed in, then springs
back to lock behind a retention ledge. The **male** part carries the hook; the **female**
part carries the receptor slot/ledge. Designed for tool-less assembly/disassembly.  
Typical use: enclosure lids, battery covers, panel-mount clips.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Arm wall thickness | 1.0–2.0 mm; thinner = lower insertion force |
| Overhang (hook tip) | Print arm along XY so hook face is ≤ 45 ° slope; or use chamfer on hook tip |
| Arm orientation | Print arm **parallel to bed** so layer lines run along the bending axis (maximises bending strength) |
| Clearance hook–slot | 0.2–0.3 mm per side for loose fit; 0.05–0.1 mm for press-fit |
| Max strain (PLA) | Keep max fibre strain ε ≤ 2 % → arm deflection δ ≤ L²·t / (3·h²) |
| Return angle | 45 ° lead-in chamfer on hook nose; 90 ° retention face for positive lock |
| Min arm length | ≥ 10 × arm thickness for adequate flex |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `arm_l` | 15 | Clip arm (beam) length, mm |
| `arm_w` | 8 | Arm width, mm |
| `arm_t` | 1.5 | Arm thickness (controls spring rate), mm |
| `hook_h` | 1.5 | Hook protrusion height (engagement depth), mm |
| `hook_lead` | 45 | Lead-in chamfer angle on hook nose, ° |
| `base_t` | 3 | Rigid base plate thickness, mm |
| `base_w` | 12 | Base plate width, mm |
| `base_l` | 10 | Base plate length, mm |
| `slot_clearance` | 0.25 | Lateral clearance between hook and slot walls, mm |
| `slot_depth` | 2 | Depth of female receptor slot, mm |

### CSG Construction Notes

```
MALE:
  base  = Box( [0,0,0] → [base_l, base_w, base_t] )
  arm   = Box( [0, (base_w-arm_w)/2, base_t] → [arm_l, arm_w, base_t+arm_t] )
  base  = base.fuse(arm)
  hook_prism = Polyhedron(
      bottom = Polygon(rect, at arm tip, z=base_t+arm_t),
      top    = Polygon(rect chamfered, at z=base_t+arm_t+hook_h)
  )
  base = base.fuse(hook_prism)

FEMALE (receptor):
  body = Box( [0,0,0] → [slot_depth*2, base_w+2*slot_clearance, base_t+arm_t+hook_h+1] )
  slot = Box( [slot_depth, slot_clearance, 0] → [slot_depth+hook_h, ...] )
  body = body.cut(slot)
  ledge undercut at top of slot to capture hook
```

---

## C. Living Hinge Strip

### Description / Purpose
A thin, continuous flexible web connecting two rigid panels, printed in a single piece.
The hinge flexes repeatedly through bending of the thin web. Relies on the anisotropic
layer structure of FDM: layer lines **perpendicular to the bend axis** give maximum
flex life.  
Typical use: flip-top boxes, cable tidies, compliant mechanisms.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Web thickness | 0.4–0.8 mm (1–2 layer heights for PETG/TPU; 0.6 mm recommended for PLA) |
| Web width (along hinge axis) | 2–8 mm; wider = stiffer; ≥ 3 mm for reliability |
| Print orientation | **Mandatory**: hinge axis parallel to X, layer lines run Y → bending stress is inter-layer (avoid delamination) |
| Material | PETG or TPU preferred; PLA cracks after ~50 cycles at 0.6 mm; nylon lasts thousands |
| Rigid panel thickness | ≥ 3 × web_t (stiff relative to hinge) |
| Taper / fillet | Add 0.5 mm fillet at web-to-panel transition to reduce stress concentration |
| Bend radius | Min bend radius ≈ 5 × web_t; do not over-constrain motion |
| Infill panels | 40–100 % for panels; 100 % for hinge web region |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `panel_w` | 60 | Panel width (X axis, along hinge), mm |
| `panel_l` | 40 | Panel length (Y axis, away from hinge), mm |
| `panel_t` | 3 | Panel thickness (Z), mm |
| `hinge_w` | 4 | Hinge web width (Y, between panels), mm |
| `hinge_t` | 0.6 | Hinge web thickness (Z), mm |
| `fillet_r` | 0.5 | Fillet radius at web-to-panel junction, mm |
| `n_hinges` | 1 | Number of parallel hinge webs (use 2 for heavy panels) |
| `hinge_gap` | 3 | Gap between parallel hinge webs (if n_hinges > 1), mm |

### CSG Construction Notes

```
PANEL_LEFT  = Box( [-panel_w/2 - hinge_w/2,  0, 0] → [-hinge_w/2, panel_l, panel_t] )
PANEL_RIGHT = Box( [ hinge_w/2, 0, 0] → [panel_w/2 + hinge_w/2, panel_l, panel_t] )

HINGE_WEB   = Box( [-hinge_w/2, 0, (panel_t - hinge_t)/2] → [hinge_w/2, panel_l, (panel_t + hinge_t)/2] )
             # web sits at mid-height of panel so neutral axis is centred

body = PANEL_LEFT.fuse(HINGE_WEB).fuse(PANEL_RIGHT)

# Fillet: apply edge fillet of fillet_r to the 4 vertical edges where
#         HINGE_WEB meets each panel (Part.Shape.makeFillet)
```

**Note:** For `n_hinges > 1`, repeat `HINGE_WEB` objects with Y offset `hinge_gap` and
remove the material between them from the panel undersides.

---

## D. Cable / Wire Saddle Clamp

### Description / Purpose
A round-bottomed U-shaped saddle that captures one or more cables. A flat foot with
screw holes allows bolting to a surface. The saddle may be open-top (single-part snap-in)
or use a separate top cap. Strain relief for wiring in enclosures, cable routing on panels.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Wall thickness (saddle) | ≥ 2 mm around cable bore |
| Saddle overhang | Print with saddle opening facing **up** (U faces up); no supports for ≤ 180 ° arc |
| Cable clearance | +0.3 mm on cable radius for easy insertion; +0.1 mm for snug grip |
| Foot thickness | ≥ 3 mm; countersink or clearance hole for M3/M4 screw |
| Snap opening | If single-part: add 0.5 × cable_d gap in saddle wall (squeeze to insert) |
| Outer wall vs cable | Min 1.5 mm of material around cable bore |
| Layer orientation | Print standing upright (foot on bed); saddle arches away from bed |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `cable_d` | 6 | Cable outer diameter, mm |
| `wall_t` | 2.5 | Saddle wall thickness, mm |
| `foot_t` | 3 | Foot plate thickness, mm |
| `foot_l` | 30 | Foot plate length (along cable axis), mm |
| `foot_w` | 20 | Foot plate width (perpendicular to cable), mm |
| `hole_d` | 3.4 | Fastener clearance hole diameter (M3 = 3.4), mm |
| `hole_offset` | 7 | Hole centre to foot edge, mm |
| `saddle_h` | 10 | Height of saddle above foot, mm |
| `n_cables` | 1 | Number of parallel cable channels |
| `cable_spacing` | 12 | Centre-to-centre spacing for multi-cable variant, mm |

### CSG Construction Notes

```
FOOT = Box( [-foot_l/2, -foot_w/2, 0] → [foot_l/2, foot_w/2, foot_t] )
      .cut( Cylinder(d=hole_d, h=foot_t, pos=[ ±hole_offset, 0, 0]) )   # × 2 holes

outer_r = cable_d/2 + wall_t
inner_r = cable_d/2 + 0.3   # clearance

SADDLE_OUTER = Cylinder(d=2*outer_r, h=foot_l, pos=[0,0,foot_t], vertical=False)
               clipped to upper half (intersect with Box above saddle centre line)
SADDLE_BORE  = Cylinder(d=2*inner_r, h=foot_l+2, pos same, vertical=False)

saddle_solid = SADDLE_OUTER.cut(SADDLE_BORE)
body = FOOT.fuse(saddle_solid)

# For snap-open variant: cut a thin slot (0.5 mm wide) from top of saddle down
# to cable centre line on one side
```

---

## E. PCB Standoff / Spacer

### Description / Purpose
A short pillar that lifts a PCB above a mounting surface, providing electrical clearance
and airflow. Central through-hole for an M-series screw; hex or round outer profile for
gripper or press-fit into a hex pocket.  
Variants: hollow for screw pass-through; blind-bore for self-tapping screw; closed-top
for plain spacer.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Wall thickness | ≥ 1.2 mm (≥ 2 × extrusion width) around bore |
| Hex flat-to-flat | Across-flats (AF) ≥ screw head OD + 2 mm (use DIN 934 NUT_MAP as reference) |
| Central bore | Drill after print or use 0.1–0.2 mm undersize bore + heat-set insert |
| Bore clearance | +0.2 mm on bolt diameter for clearance fit; −0.1 mm for self-tap grip |
| Print orientation | Axis **vertical** (Z); hex flat base on bed → best bore circularity |
| Overhang | None (solid pillar); top chamfer 45 ° to avoid drooping on bore entry |
| Layer adhesion | Print at 100 % infill for compressive load paths |
| Height tolerance | FDM ±0.2 mm height; use washers to fine-tune PCB height |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `height` | 10 | Standoff height, mm |
| `screw_size` | "M3" | Screw designation (drives OD from NUT_MAP), string |
| `bore_d` | 3.2 | Central bore diameter (clearance for M3), mm |
| `outer_d` | 6 | Outer diameter (round) **or** AF size (hex), mm |
| `profile` | "hex" | `"hex"` or `"round"` |
| `top_style` | "through" | `"through"`, `"blind"`, or `"closed"` |
| `blind_depth` | 6 | Depth of blind bore (if top_style = "blind"), mm |
| `chamfer` | 0.5 | Entry chamfer on bore openings, mm |
| `base_flange_d` | 0 | Optional flange diameter at base (0 = none), mm |
| `base_flange_t` | 1.5 | Flange thickness if base_flange_d > 0, mm |

### CSG Construction Notes

```
if profile == "hex":
    BODY = Polyhedron(
        Polygon(center=[0,0,0],       radius=outer_d/2, sides=6),
        Polygon(center=[0,0,height],  radius=outer_d/2, sides=6)
    )
else:
    BODY = Cylinder(d=outer_d, h=height)

if top_style == "through":
    BORE = Cylinder(d=bore_d, h=height + 1)
elif top_style == "blind":
    BORE = Cylinder(d=bore_d, h=blind_depth)  # from bottom only
else:
    BORE = None   # closed spacer / plain standoff

if BORE:
    BODY = BODY.cut(BORE)
    # add entry chamfer: cut a Cone(r1=bore_d/2+chamfer, r2=bore_d/2, h=chamfer)
    #   at both open ends

if base_flange_d > 0:
    FLANGE = Cylinder(d=base_flange_d, h=base_flange_t)
    BODY = BODY.fuse(FLANGE)
```

---

## F. L-Bracket / Shelf Wall Bracket

### Description / Purpose
Two perpendicular plates (vertical wall plate + horizontal shelf plate) meeting at 90 °,
optionally reinforced with a triangular gusset. Bolt holes in both plates for wall fixing
and shelf attachment.  
Typical use: shelf supports, sensor mounts, cable tray brackets.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Plate thickness | ≥ 3 mm for light duty; ≥ 4–5 mm for shelf loads > 2 kg |
| Gusset | Always add for load-bearing; gusset t ≥ plate_t; 45 ° triangle |
| Overhang | Print with long axis vertical (wall plate vertical on bed, shelf plate horizontal → horizontal plate overhangs 90 °) — **use support or tilt 45 °** |
| Preferred orientation | Print bracket standing on wall plate edge so both plates are near-vertical; gusset on bed. No supports needed. |
| Corner fillet | ≥ 2 mm fillet on inner corner to avoid stress concentration |
| Hole pattern | Use 4 mm clearance holes (M3 = 3.4, M4 = 4.5) on grid |
| Hole margin | ≥ 2 × hole_d from plate edge |
| Infill | ≥ 40 % for structural, 100 % for gusset area |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `wall_l` | 60 | Wall plate length (vertical), mm |
| `shelf_l` | 60 | Shelf plate length (horizontal), mm |
| `plate_w` | 40 | Width of both plates (into the wall), mm |
| `plate_t` | 4 | Plate thickness, mm |
| `gusset` | True | Include diagonal gusset, bool |
| `gusset_t` | 4 | Gusset thickness, mm |
| `fillet_r` | 2 | Inner corner fillet radius, mm |
| `hole_d` | 4.5 | Fastener clearance hole diameter (M4), mm |
| `hole_rows_wall` | 2 | Number of hole rows on wall plate |
| `hole_rows_shelf` | 2 | Number of hole rows on shelf plate |
| `hole_spacing` | 20 | Centre-to-centre hole spacing, mm |

### CSG Construction Notes

```
WALL_PLATE  = Box( [0, 0, 0] → [plate_t, plate_w, wall_l] )
SHELF_PLATE = Box( [plate_t, 0, 0] → [plate_t + shelf_l, plate_w, plate_t] )
body = WALL_PLATE.fuse(SHELF_PLATE)

if gusset:
    # Right triangle in XZ plane, extruded along Y
    GUSSET = Wedge(length=shelf_l, width=plate_w, height=wall_l - plate_t)
    GUSSET positioned at corner, cut to triangle shape
    body = body.fuse(GUSSET)

# Inner fillet: makeFillet on the two Z-axis edges at X=plate_t

# Holes in wall plate (Cylinders along X axis)
for row in wall_hole_positions:
    body = body.cut( Cylinder(d=hole_d, h=plate_t, along_X) )

# Holes in shelf plate (Cylinders along Z axis)
for row in shelf_hole_positions:
    body = body.cut( Cylinder(d=hole_d, h=plate_t, along_Z) )
```

---

## G. J-Hook and S-Hook Wall Hooks

### Description / Purpose
**J-hook:** One-sided hook screwed or press-fit to a wall; open jaw at top accepts a
rod, cable, or bag loop.  
**S-hook:** Double-sided curved hook with one loop engaging a rail/rod and one open
jaw for hanging loads. Can be a single print or two J-hooks fused back-to-back.  
Typical use: tool storage, cable hangers, coat hooks, workshop organiser rails.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Cross-section thickness | ≥ 4 mm in the load-bearing direction; round cross-section → 5 mm dia |
| Overhang (hook arc) | Print hook arc in XY plane; all overhangs ≤ 45 °. If hook jaw gap is top, no support needed |
| Hook opening gap | ≥ rod_d + 1.0 mm to allow insertion with hand |
| Wall thickness (tube hook) | ≥ 1.6 mm for hollow hook; solid preferred for hooks ≤ 8 mm dia |
| Base plate | ≥ 3 mm thick; ≥ 2 screw holes for anti-rotation |
| Print orientation | J-hook: back plate flat on bed, hook curves upward. S-hook: mid-plane on bed |
| Layer direction | Main load is tensile along hook arc → layers perpendicular to load = weakest; orient so bending load is across layers |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `hook_d` | 6 | Hook wire/bar cross-section diameter, mm |
| `jaw_d` | 20 | Inner jaw diameter (loop inside radius × 2), mm |
| `jaw_gap` | 10 | Opening width of jaw, mm |
| `hook_h` | 40 | Total hook height above base, mm |
| `hook_style` | "J" | `"J"` or `"S"` |
| `base_t` | 4 | Back-plate thickness (J-hook), mm |
| `base_w` | 30 | Back-plate width, mm |
| `base_h` | 40 | Back-plate height, mm |
| `hole_d` | 4.5 | Screw hole diameter in back plate, mm |
| `n_holes` | 2 | Number of screw holes |
| `press_fit_d` | 0 | Press-fit peg diameter (0 = screw mount), mm |

### CSG Construction Notes

```
J-HOOK:
  BASE = Box( [0,0,0] → [base_t, base_w, base_h] )
         .cut( Cylinder × n_holes for screw holes )

  STEM = Cylinder(d=hook_d, h=hook_h - jaw_d/2, pos at top of base, vertical)

  ARC  = Torus(major=jaw_d/2 + hook_d/2, minor=hook_d/2)
         trimmed to 180 ° semicircle (intersect with half-space Box)
         positioned so open jaw faces up

  body = BASE.fuse(STEM).fuse(ARC)

S-HOOK:
  upper_J = (as above, mirrored)
  lower_J = J without base, rotated 180 ° about Z
  body = upper_J.fuse(lower_J)
  (no base plate on S-hook; both ends are open jaws)
```

---

## H. Knurled Thumb-Screw Knob

### Description / Purpose
A large-diameter cylindrical or dome-shaped knob that provides a grippable surface for
finger-tightening. Central axial pocket accepts either a **heat-set insert** (M3–M8) or
a **hex nut trap** (DIN 934). Knurl pattern on outer surface adds grip.  
Typical use: adjustment knobs, fixture clamps, lens rings, panel controls.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Knob diameter | ≥ 20 mm for M3; ≥ 25 mm for M5+ for usable torque |
| Wall around insert | ≥ 2.5 mm between bore wall and knob OD |
| Insert pocket depth | = insert length + 0.5 mm; heat-set bore = insert OD − 0.1 mm (interference fit before pressing) |
| Nut trap | Hex AF + 0.2 mm; depth = nut height + 0.3 mm; closed bottom for nut retention |
| Knurl pattern | 0.8–1.2 mm triangular axial ribs, 0.5 mm depth, 60 ° helix angle; or straight axial flutes |
| Print orientation | Axis **vertical** (Z axis); base on bed — no supports, best bore roundness |
| Top dome | Optional hemisphere on top for aesthetics; add 1 mm above main cylinder |
| Infill | 40–60 % for hand loads; 100 % for high-torque applications |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `knob_d` | 25 | Knob outer diameter (before knurl), mm |
| `knob_h` | 18 | Knob overall height, mm |
| `screw_size` | "M4" | Thread size, drives insert/nut pocket geometry |
| `insert_type` | "heat_set" | `"heat_set"` or `"nut_trap"` |
| `insert_d` | 5.6 | Insert outer diameter (heat-set M4 = 5.6), mm |
| `insert_h` | 6 | Insert / nut pocket depth, mm |
| `bore_d` | 4.2 | Through-bore or clearance hole diameter, mm |
| `top_style` | "flat" | `"flat"`, `"dome"`, or `"countersink"` |
| `knurl_ribs` | 20 | Number of knurl ribs around circumference |
| `knurl_depth` | 0.5 | Knurl rib depth (radial), mm |
| `knurl_h` | 12 | Height of knurled section, mm |

### CSG Construction Notes

```
BODY = Cylinder(d=knob_d, h=knob_h)

# Knurl: for each of n ribs:
#   RIB = Wedge or Polyhedron(triangular cross-section, h=knurl_h)
#         rotated i × 360°/knurl_ribs about Z axis, placed at OD surface
#   BODY = BODY.fuse(RIB)
# (Alternatively: use Polygon(sides=knurl_ribs, radius=knob_d/2+knurl_depth) extruded
#  to form a star prism, fuse to base cylinder bottom half)

if top_style == "dome":
    DOME = Sphere(radius=knob_d/2) clipped to upper hemisphere
    DOME shifted to Z = knob_h
    BODY = BODY.fuse(DOME)

# Insert pocket (from bottom):
if insert_type == "heat_set":
    POCKET = Cylinder(d=insert_d, h=insert_h)
else:  # nut_trap
    nut = NUT_MAP[screw_size]
    POCKET = Polyhedron(hex, AF=nut["AF"]+0.2, h=nut["H"]+0.3)

BODY = BODY.cut(POCKET)

# Optional through-bore above insert:
THRU = Cylinder(d=bore_d, h=knob_h - insert_h, pos at Z=insert_h)
BODY = BODY.cut(THRU)
```

---

## I. Snap-Fit Rectangular Enclosure Lid

### Description / Purpose
A flat panel lid that snaps onto a matching rectangular box. Snap tabs (cantilever arms
ending in hooks) project from all four sides and engage ledges moulded into the box
walls. Provides tool-less open/close for electronics enclosures, project boxes, sensor
housings.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Lid panel thickness | ≥ 1.6 mm; 2 mm recommended |
| Tab arm thickness | 1.0–1.5 mm for PLA; 0.8–1.2 mm for PETG |
| Tab arm length | 6–12 mm for adequate flex at small deflection |
| Engagement depth | 0.8–1.5 mm (hook protrusion beyond box wall) |
| Clearance lid-to-box | 0.15–0.25 mm per side for side walls |
| Tab clearance in slot | 0.2 mm per side |
| Overhang | Print lid flat on bed; all tab arms print horizontally (no supports if hook ≤ 45 °) |
| Corner tabs | Place at least 1 tab per side; 2 per long side for lids > 80 mm |
| Box ledge | Recess cut into box inner wall: ledge_d = hook_h + 0.2 mm |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `lid_l` | 100 | Lid outer length, mm |
| `lid_w` | 60 | Lid outer width, mm |
| `lid_t` | 2 | Lid panel thickness, mm |
| `skirt_h` | 6 | Downward skirt / lip height, mm |
| `skirt_t` | 1.5 | Skirt wall thickness, mm |
| `tab_l` | 8 | Snap tab arm length, mm |
| `tab_w` | 8 | Tab arm width, mm |
| `tab_arm_t` | 1.2 | Tab arm thickness (flex element), mm |
| `hook_h` | 1.2 | Hook protrusion (engagement depth), mm |
| `hook_lead` | 45 | Lead-in angle on hook, ° |
| `side_clearance` | 0.2 | Clearance between lid skirt and box outer wall, mm |
| `tabs_long` | 2 | Number of tabs on each long side |
| `tabs_short` | 1 | Number of tabs on each short side |

### CSG Construction Notes

```
PANEL = Box( [0,0,0] → [lid_l, lid_w, lid_t] )

SKIRT (4 walls, inset by side_clearance from panel edge):
  front = Box( [side_clearance, side_clearance, -skirt_h] → [lid_l - side_clearance, side_clearance + skirt_t, 0] )
  back  = mirror of front
  left  = Box( similar, along X )
  right = mirror
  PANEL = PANEL.fuse(front).fuse(back).fuse(left).fuse(right)

TABS (for each tab position on each side):
  ARM  = Box( [x0, skirt_outer_face, -tab_l - lid_t] → [x0+tab_w, skirt_outer_face+tab_arm_t, -lid_t] )
  HOOK = Polyhedron(trapezoidal cross-section at arm tip, hook_h protrusion outward)
  PANEL = PANEL.fuse(ARM).fuse(HOOK)

# Tab slots in skirt (so arm can flex inward):
for each tab: PANEL = PANEL.cut( slot Box around tab arm + clearance )
```

---

## J. Dovetail Rail + Slider Joint

### Description / Purpose
A linear sliding joint where the rail has a trapezoidal (dovetail) cross-section and the
slider has a matching female channel. The geometry prevents pull-out perpendicular to
the rail axis while allowing free sliding along it. Tool-less, print-in-place or
print-separate assembly.  
Typical use: drawer runners, adjustable mounts, camera rail accessories, modular
furniture connections.

### FDM Design Rules
| Rule | Guideline |
|---|---|
| Dovetail angle | 45–60 ° included half-angle (60 ° = more retention; 45 ° = easier print) |
| Clearance (print-separate) | 0.2–0.3 mm per mating face; 0.4 mm for loose sliding fit |
| Wall around dovetail | ≥ 2 mm on slider outer cheeks |
| Overhang | At 45 ° dovetail angle, faces print at exactly 45 ° — marginal without support; 30 ° angle is support-free. **60 ° requires support or bridging**. |
| Print orientation | Rail: cross-section in XY, length along Z (vertical print gives best face finish). OR flat on bed for long rails (dovetail faces are then vertical walls — good). |
| Print-in-place gap | ≥ 0.4 mm clearance; print at 0.2 mm layer height for accuracy |
| Lock / stop | Add optional end-stop tab or set-screw hole to retain slider position |
| Infill | ≥ 30 % for rail (wear surface); 100 % for thin slider walls |

### Parametric Dimensions

| Name | Default | Description |
|---|---|---|
| `rail_l` | 80 | Rail length, mm |
| `rail_w` | 20 | Rail total width at base, mm |
| `rail_h` | 8 | Rail height (Z), mm |
| `dove_w_top` | 10 | Dovetail top width (narrow end of trapezoid), mm |
| `dove_w_base` | 14 | Dovetail base width (wide end), mm |
| `dove_h` | 5 | Dovetail protrusion height, mm |
| `dove_angle` | 45 | Half-angle of dovetail walls, ° |
| `slider_l` | 30 | Slider length, mm |
| `slider_h` | 8 | Slider body height, mm |
| `slider_wall_t` | 3 | Slider outer cheek wall thickness, mm |
| `clearance` | 0.25 | Per-face sliding clearance, mm |
| `stop_tab` | False | Add retention end-stop tab to rail, bool |

### CSG Construction Notes

```
RAIL_BASE = Box( [-rail_w/2, 0, 0] → [rail_w/2, rail_l, rail_h - dove_h] )

DOVE_PRISM = Polyhedron(
    bottom = Polygon(trapezoid, w=dove_w_base, at Z=rail_h - dove_h),
    top    = Polygon(trapezoid, w=dove_w_top,  at Z=rail_h)
)  # trapezoidal prism, extruded along Y for rail_l

RAIL = RAIL_BASE.fuse(DOVE_PRISM)

if stop_tab:
    TAB = Box at one end of rail, protruding into slider channel path

# SLIDER CHANNEL (female, with clearance):
dove_w_top_c  = dove_w_top  + 2 * clearance
dove_w_base_c = dove_w_base + 2 * clearance
dove_h_c      = dove_h      + clearance

SLIDER_BLANK = Box( [-rail_w/2 - slider_wall_t, 0, 0]
                  → [ rail_w/2 + slider_wall_t, slider_l, slider_h] )

CHANNEL = Polyhedron(
    bottom = Polygon(trapezoid, w=dove_w_base_c, at Z=slider_h - dove_h_c),
    top    = Polygon(trapezoid, w=dove_w_top_c,  at Z=slider_h + clearance)
)  # cut upward through slider

SLIDER = SLIDER_BLANK.cut(CHANNEL)
```

**Assembly note:** Slide SLIDER onto RAIL from one open end along Y axis.

---

*Document generated: 2026-05-31 — Part Library research step 01.*
