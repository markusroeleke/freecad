"""Code generator: converts a :class:`FitResult` into a runnable Python file.

The generated script:

1. Imports FreeCAD + ``freecad_lib``.
2. Opens a new document named after the original STL file.
3. **Parametric section** -- emits ``Box`` / ``Cylinder`` calls for every detected
   primitive, combining them with ``.fuse()`` and ``.cut()`` as appropriate.
4. **Mesh fallback section** -- always includes a commented-out ``mesh_import()``
   helper that reproduces the exact STL shape in case the parametric
   reconstruction is not accurate enough.
5. Calls ``show_solid()`` and ``fit_view()`` for immediate visual feedback.

Usage::

    from code_generator import CodeGenerator
    code = CodeGenerator().generate(fit_result)
    with open("output.py", "w") as fh:
        fh.write(code)
"""

from __future__ import annotations

import textwrap
from datetime import date
from pathlib import Path
from typing import List

from primitive_fitter import BoxPrimitive, CylinderPrimitive, FitResult


class CodeGenerator:
    """Generates a ``freecad_lib`` Python script from a :class:`FitResult`."""

    # Relative import path to freecad_lib (adjust if running from a different CWD)
    FREECAD_LIB_IMPORT = "src.freecad_lib"

    def generate(self, result: FitResult, stl_abs_path: str = "") -> str:
        """Return the full generated Python source as a string."""
        stem = Path(result.source_path).stem if result.source_path else "shape"
        doc_name = stem + "_RE"
        stl_path_str = stl_abs_path or result.source_path or "path/to/original.stl"

        lines: List[str] = []

        # ------------------------------------------------------------------
        # Module docstring / header comment
        # ------------------------------------------------------------------
        # Forward slashes avoid invalid escape sequence warnings (e.g. \d on Windows paths)
        safe_source = (result.source_path or stl_path_str).replace("\\", "/")
        lines += [
            f'"""Reverse-engineered design.',
            f"",
            f"Source      : {safe_source}",
            f"Generated   : {date.today().isoformat()}",
            f"Confidence  : {result.confidence:.0%}  "
            f"({result.confidence:.0%} of mesh faces covered by detected primitives)",
            f"",
            f"NOTE: This is an APPROXIMATE parametric reconstruction.",
            f"      For an exact copy use the mesh_import() helper at the bottom.",
            f'"""',
            "",
        ]

        # ------------------------------------------------------------------
        # Imports
        # ------------------------------------------------------------------
        lines += [
            "import FreeCAD, Part, Mesh as _FcMesh",
            "from FreeCAD import Vector",
            "import sys, os as _os",
            "",
            "# Ensure freecad_lib is importable",
            "_here = _os.path.dirname(_os.path.abspath(__file__))",
            "for _p in (_here,",
            "           _os.path.join(_here, '..', '..'),",
            "           _os.path.join(_here, '..')):",
            "    if _p not in sys.path:",
            "        sys.path.insert(0, _p)",
            "",
            f"from {self.FREECAD_LIB_IMPORT} import *",
            "",
        ]

        # ------------------------------------------------------------------
        # Document setup
        # ------------------------------------------------------------------
        lines += [
            "# --- Document ---",
            f"new_doc({doc_name!r})",
            "",
        ]

        # ------------------------------------------------------------------
        # Parametric reconstruction
        # ------------------------------------------------------------------
        lines += [
            "# " + "=" * 60,
            "# Parametric reconstruction",
            f"# Bounding box: "
            f"{result.bounding_box.length:.2f} x "
            f"{result.bounding_box.breadth:.2f} x "
            f"{result.bounding_box.height:.2f} mm",
            "# " + "=" * 60,
            "",
        ]

        bb = result.bounding_box

        if result.box_bodies:
            # Use the detected box
            b = result.box_bodies[0]
            lines += [
                f"# Detected box body",
                f"body = Box(",
                f"    Vector({b.x_min}, {b.y_min}, {b.z_min}),",
                f"    Vector({b.x_max}, {b.y_max}, {b.z_max}),",
                f").solid",
                "",
            ]
        else:
            # Bounding-box fallback
            lines += [
                "# No box detected -- using bounding box as body",
                f"body = Box(",
                f"    Vector({bb.x_min}, {bb.y_min}, {bb.z_min}),",
                f"    Vector({bb.x_max}, {bb.y_max}, {bb.z_max}),",
                f").solid",
                "",
            ]

        # Cylinders: first ADD (convex), then CUT (concave holes)
        add_cyls = [c for c in result.cylinders if not c.is_cut]
        cut_cyls = [c for c in result.cylinders if c.is_cut]

        for i, cyl in enumerate(add_cyls):
            vname = f"_cyl_add_{i}"
            lines += self._cylinder_lines(vname, cyl)
            lines.append(f"body = body.fuse({vname})")
            lines.append("")

        for i, cyl in enumerate(cut_cyls):
            vname = f"_cyl_cut_{i}"
            lines += self._cylinder_lines(vname, cyl, comment="hole")
            lines.append(f"body = body.cut({vname})")
            lines.append("")

        # ------------------------------------------------------------------
        # Display & export
        # ------------------------------------------------------------------
        lines += [
            "# --- Display ---",
            f"show_solid(body, name={stem!r}, color=(0.5, 0.5, 0.5))",
            "fit_view()",
            "",
        ]

        # ------------------------------------------------------------------
        # Mesh-import fallback (always included, commented out by default)
        # ------------------------------------------------------------------
        lines += [
            "# " + "=" * 60,
            "# Exact mesh reproduction (uncomment to use)",
            "# " + "=" * 60,
            "",
            "def mesh_import(stl_path: str):",
            '    """Load the original STL as an exact FreeCAD solid."""',
            "    m = _FcMesh.Mesh(stl_path)",
            "    shape = Part.Shape()",
            "    shape.makeShapeFromMesh(m.Topology, 0.05)",
            "    return Part.makeSolid(shape)",
            "",
            f"# exact_body = mesh_import(r{stl_path_str.replace(chr(92), '/')!r})",
            f"# show_solid(exact_body, name={stem + '_exact'!r})",
            "",
        ]

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cylinder_lines(
        vname: str,
        cyl: CylinderPrimitive,
        comment: str = "",
    ) -> List[str]:
        """Return source lines that construct one cylinder solid.

        Cylinder(name, diameter, height, position=Vector(0,0,0), normal=Vector(0,0,1))
        """
        ax = cyl.axis
        comment_str = f"  # {comment}" if comment else ""
        pos = f"Vector({cyl.center_x}, {cyl.center_y}, {cyl.center_z})"
        if ax != (0.0, 0.0, 1.0):
            normal_line = f"    Vector({ax[0]}, {ax[1]}, {ax[2]}),   # axis"
            return [
                f"{vname} = Cylinder({comment_str}",
                f"    {vname!r}, {cyl.diameter}, {cyl.height},",
                f"    {pos},",
                f"    {normal_line}",
                f").solid",
            ]
        return [
            f"{vname} = Cylinder({comment_str}",
            f"    {vname!r}, {cyl.diameter}, {cyl.height},",
            f"    {pos},",
            f").solid",
        ]
