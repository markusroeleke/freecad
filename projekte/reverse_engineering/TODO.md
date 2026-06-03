# Reverse Engineering – Todo & Research

## Goal
Read an STL file, analyse its triangle mesh to recognise geometric primitives
(Box, Cylinder, Cone, …), and generate a standalone Python file that recreates
the same shape using `freecad_lib` primitives.  When a shape cannot be fully
parameterised, fall back to a direct mesh-import code block.

---

## Research Summary

### What STL gives us
STL stores only a triangle mesh: vertex positions (float32, mm) and one outward-
pointing normal per triangle.  There is no topology, no feature tree, no sketch
history.

### Approach: Feature-detection pipeline

```
STL file
  └─ STLReader          → MeshData (vertices, faces, face-normals as numpy arrays)
       └─ MeshAnalyzer  → PlaneFeature list + CylinderFeature list
            └─ PrimitiveFitter → FitResult (BoxPrimitive, CylinderPrimitive, …)
                 └─ CodeGenerator → Python file (freecad_lib code + mesh fallback)
```

#### 1 – Normal clustering (MeshAnalyzer)
- Group triangles whose face normals are within a configurable angle tolerance
  (default 5 °).
- Each cluster represents a *candidate flat region* (or part of a cylinder side).

#### 2 – Planar region detection
- For each normal cluster: verify all vertices lie within `plane_tol` mm of the
  plane `n · x = d`.
- Compute region area, centre, and axis-alignment flag.

#### 3 – Box detection
- Require 6 axis-aligned planar regions forming 3 opposite-normal pairs.
- Extract `x_min/max`, `y_min/max`, `z_min/max` directly from vertex coordinates.

#### 4 – Cylinder detection
- Find faces whose normals are *perpendicular* to a candidate axis (|n · axis| < ε).
- Verify the in-plane normals *span > 180 °* (distinguishes a cylinder from a flat wall).
- Fit the 2D cylinder centre via least-squares: each face defines a line through
  its centre in the direction of its in-plane normal; the cylinder axis is the
  common intersection.
- Determine **convexity**: if face normals point *away* from the centre → outer
  surface (add); if they point *toward* the centre → inner surface (cut / hole).

#### 5 – Code generation
- For each recognised primitive: emit `freecad_lib` constructor call.
- Apply `body.cut(hole)` for each concave (inward-facing) cylinder.
- Include a commented-out `mesh_import()` fallback for exact reproduction.

### Limitations (MVP)
| Shape | Status |
|---|---|
| Axis-aligned boxes | ✅ Implemented |
| Vertical cylinders (Z-axis) | ✅ Implemented |
| X/Y-axis cylinders | ✅ Implemented |
| Angled / rotated primitives | 🔲 Phase 2 |
| Cones, Spheres, Tori | 🔲 Phase 2 |
| Fillet / chamfer detection | 🔲 Phase 2 |
| Multi-body assemblies | 🔲 Phase 3 |
| ML-based feature recognition | 🔲 Phase 3 |

---

## Implementation Tasks

- [x] **01** Research & design pipeline
- [x] **02** `stl_reader.py`  -- ASCII + binary STL -> `MeshData` (numpy)
- [x] **03** `mesh_analyzer.py` -- normal clustering, plane & cylinder detection
- [x] **04** `primitive_fitter.py` -- `MeshData` -> `FitResult` (structured primitives)
- [x] **05** `code_generator.py` -- `FitResult` -> `.py` file using `freecad_lib`
- [x] **06** `reverse_engineer.py` -- single entry-point function
- [x] **07** `test_reverse_engineer.py` -- 23 tests (stdlib only, all passing)
- [x] **08** Cylinder sub-clustering: radius-histogram splits multiple shells per axis
- [ ] **09** Support Cone, Sphere primitives (Phase 2)
- [ ] **10** Handle non-axis-aligned rotations (Phase 2)
- [ ] **11** Multi-body: detect connected components, nested booleans (Phase 3)

### Known Issues (MVP)
| Issue | Impact | Fix planned |
|---|---|---|
| X/Y edge arcs at part boundaries sometimes fire as false positive cylinders | Extra fuse() calls | 08 sub-clustering (improved arc filter needed) |
| Box detection fails when outer flat faces are fragmented by curved cut boundaries | Falls back to bounding-box | improved plane grouping (Phase 2) |
| All shapes: parametric code is **approximate**; use `mesh_import()` for **exact** output | Expected by design | -- |

---

## File Layout

```
src/reverse_engineering/
    TODO.md               ← this file
    stl_reader.py         ← binary + ASCII STL parser  (no external deps)
    mesh_analyzer.py      ← normal clustering, PlaneFeature, CylinderFeature
    primitive_fitter.py   ← BoxPrimitive, CylinderPrimitive, FitResult
    code_generator.py     ← FitResult → Python source code string
    reverse_engineer.py   ← public API:  reverse_engineer(stl, output_py)
```

## Dependencies
- `numpy` — bundled with FreeCAD; required for all math
- `struct` — stdlib; used in binary STL parsing
- No `scipy`, no `sklearn`, no external packages required

## Usage Example

```python
from src.reverse_engineering.reverse_engineer import reverse_engineer

reverse_engineer(
    stl_path  = r"stl/Topfdeckelhalter.stl",
    output_py = r"projekte/Topfdeckelhalter_RE.py",
)
```

The generated file can be opened directly inside FreeCAD Python console or run
as a macro.
