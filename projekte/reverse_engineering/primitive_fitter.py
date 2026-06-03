"""High-level primitive fitting.

Converts low-level :class:`PlaneFeature` / :class:`CylinderFeature` objects
(from :class:`MeshAnalyzer`) into structured, code-generator-ready primitives:

- :class:`BoxPrimitive`      -- axis-aligned rectangular cuboid
- :class:`CylinderPrimitive` -- vertical or horizontal cylinder (add or cut)
- :class:`FitResult`         -- all primitives + coverage confidence

The fitting strategy:
1. Search for 6 axis-aligned planar regions that form 3 opposite-normal pairs.
   When found, derive a ``BoxPrimitive`` from the vertex extents of each face group.
2. Wrap each detected ``CylinderFeature`` into a ``CylinderPrimitive``.
   Mark it as a *cut* when the surface is concave (inward-facing normals).
3. Always include a bounding-box fallback so the code generator can emit *something*
   even for shapes that cannot be fully parametrised.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from stl_reader import MeshData
from mesh_analyzer import MeshAnalyzer, CylinderFeature, PlaneFeature

# ---------------------------------------------------------------------------
# Primitive descriptions
# ---------------------------------------------------------------------------


@dataclass
class BoxPrimitive:
    """Axis-aligned rectangular cuboid."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

    @property
    def length(self) -> float:
        return round(self.x_max - self.x_min, 3)

    @property
    def breadth(self) -> float:
        return round(self.y_max - self.y_min, 3)

    @property
    def height(self) -> float:
        return round(self.z_max - self.z_min, 3)

    @property
    def center(self) -> Tuple[float, float, float]:
        return (
            round((self.x_min + self.x_max) / 2, 3),
            round((self.y_min + self.y_max) / 2, 3),
            round((self.z_min + self.z_max) / 2, 3),
        )

    def __str__(self) -> str:
        return (
            f"Box  [{self.x_min:.2f}, {self.y_min:.2f}, {self.z_min:.2f}] "
            f"-> [{self.x_max:.2f}, {self.y_max:.2f}, {self.z_max:.2f}]  "
            f"({self.length:.2f} x {self.breadth:.2f} x {self.height:.2f} mm)"
        )


@dataclass
class CylinderPrimitive:
    """Cylinder -- outer body (add) or hole (cut)."""

    center_x: float
    center_y: float
    center_z: float
    diameter: float
    height: float
    axis: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    is_cut: bool = False  # True -> subtract from main body

    @property
    def radius(self) -> float:
        return self.diameter / 2.0

    def __str__(self) -> str:
        op = "CUT " if self.is_cut else "ADD "
        return (
            f"{op}Cylinder  o{self.diameter:.2f} mm x h{self.height:.2f} mm "
            f"@ ({self.center_x:.2f}, {self.center_y:.2f}, {self.center_z:.2f})"
        )


@dataclass
class FitResult:
    """All primitives recognised in the mesh, plus coverage statistics."""

    source_path: str

    # Overall bounding box (always present)
    bounding_box: BoxPrimitive

    # Detected parametric shapes
    box_bodies: List[BoxPrimitive] = field(default_factory=list)
    cylinders: List[CylinderPrimitive] = field(default_factory=list)

    # 0-1: fraction of mesh faces covered by at least one detected primitive
    confidence: float = 0.0

    @property
    def has_parametric_body(self) -> bool:
        return bool(self.box_bodies or self.cylinders)

    def summary(self) -> str:
        lines = [
            f"Source      : {self.source_path}",
            f"Bounding box: {self.bounding_box}",
            f"Confidence  : {self.confidence:.0%}",
        ]
        for b in self.box_bodies:
            lines.append(f"  {b}")
        for c in self.cylinders:
            lines.append(f"  {c}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fitter
# ---------------------------------------------------------------------------


class PrimitiveFitter:
    """Analyse a :class:`MeshData` and return a :class:`FitResult`."""

    # Normal-to-axis alignment: |n[i] +/- 1| must be < this to be "axis-aligned"
    AXIS_TOL: float = 0.09

    def fit(self, mesh: MeshData) -> FitResult:
        analyzer = MeshAnalyzer(mesh)

        lo, hi = mesh.bounding_box
        bb = BoxPrimitive(
            x_min=_r(lo[0]),
            x_max=_r(hi[0]),
            y_min=_r(lo[1]),
            y_max=_r(hi[1]),
            z_min=_r(lo[2]),
            z_max=_r(hi[2]),
        )

        planes = analyzer.detect_planar_regions()
        raw_cyls = analyzer.detect_cylinders()

        box_bodies = self._fit_boxes(planes)
        cylinders = self._fit_cylinders(raw_cyls, bb)

        # Coverage: union of all face indices claimed by detectors
        covered: set = set()
        for p in planes:
            covered.update(p.face_indices)
        for c in raw_cyls:
            covered.update(c.face_indices)
        confidence = len(covered) / max(1, mesh.n_faces)

        return FitResult(
            source_path=mesh.source_path,
            bounding_box=bb,
            box_bodies=box_bodies,
            cylinders=cylinders,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Box fitting
    # ------------------------------------------------------------------

    def _fit_boxes(self, planes: List[PlaneFeature]) -> List[BoxPrimitive]:
        # Keep only axis-aligned planes
        ax = [p for p in planes if p.is_axis_aligned]
        if len(ax) < 6:
            return []

        # Bucket by normal direction
        px: List[PlaneFeature] = []  # +X normal
        nx: List[PlaneFeature] = []  # -X
        py: List[PlaneFeature] = []
        ny: List[PlaneFeature] = []
        pz: List[PlaneFeature] = []
        nz: List[PlaneFeature] = []

        for p in ax:
            n = p.normal
            if abs(float(n[0]) - 1.0) < self.AXIS_TOL:
                px.append(p)
            elif abs(float(n[0]) + 1.0) < self.AXIS_TOL:
                nx.append(p)
            elif abs(float(n[1]) - 1.0) < self.AXIS_TOL:
                py.append(p)
            elif abs(float(n[1]) + 1.0) < self.AXIS_TOL:
                ny.append(p)
            elif abs(float(n[2]) - 1.0) < self.AXIS_TOL:
                pz.append(p)
            elif abs(float(n[2]) + 1.0) < self.AXIS_TOL:
                nz.append(p)

        if not (px and nx and py and ny and pz and nz):
            return []

        # For each direction use the OUTERMOST vertex coordinate across all planes
        # in that bucket.  This makes the detection robust when the STL
        # contains many near-axis-aligned planes (e.g. curved-cut boundaries).
        x_max = max(float(p.vertices[:, 0].max()) for p in px)
        x_min = min(float(p.vertices[:, 0].min()) for p in nx)
        y_max = max(float(p.vertices[:, 1].max()) for p in py)
        y_min = min(float(p.vertices[:, 1].min()) for p in ny)
        z_max = max(float(p.vertices[:, 2].max()) for p in pz)
        z_min = min(float(p.vertices[:, 2].min()) for p in nz)

        # Reject inverted / degenerate boxes -- these arise when the algorithm
        # mistakes internal hole faces (whose normals are reversed) for outer faces.
        if x_max <= x_min or y_max <= y_min or z_max <= z_min:
            return []

        return [
            BoxPrimitive(
                x_min=_r(x_min),
                x_max=_r(x_max),
                y_min=_r(y_min),
                y_max=_r(y_max),
                z_min=_r(z_min),
                z_max=_r(z_max),
            )
        ]

    # ------------------------------------------------------------------
    # Cylinder fitting
    # ------------------------------------------------------------------

    def _fit_cylinders(
        self,
        raw: List[CylinderFeature],
        bb: BoxPrimitive,
    ) -> List[CylinderPrimitive]:
        result: List[CylinderPrimitive] = []
        axis_to_bb_extent = {
            (0.0, 0.0, 1.0): bb.height,
            (1.0, 0.0, 0.0): bb.length,
            (0.0, 1.0, 0.0): bb.breadth,
        }
        max_bb_dim = max(bb.length, bb.breadth, bb.height)

        for c in raw:
            cx, cy, cz = float(c.center[0]), float(c.center[1]), float(c.center[2])

            # --- False-positive filter ---
            # A real through-hole or boss spans >= 40 % of the bounding-box
            # extent along the cylinder axis.  Shorter cylinders are edge artefacts.
            ax_key = (
                round(float(c.axis[0])),
                round(float(c.axis[1])),
                round(float(c.axis[2])),
            )
            bb_extent_along_axis = axis_to_bb_extent.get(ax_key, 0.0)  # type: ignore[arg-type]
            if bb_extent_along_axis > 0 and c.height < bb_extent_along_axis * 0.4:
                continue

            # Reject cylinders wider than the bounding box (physically impossible)
            if c.radius * 2.0 > max_bb_dim * 1.1:
                continue

            # A concave (inward-facing) cylinder that sits within the bounding box
            # is most likely a through-hole or pocket -> mark as cut.
            inside_bb = (
                bb.x_min <= cx <= bb.x_max
                and bb.y_min <= cy <= bb.y_max
                and bb.z_min <= cz <= bb.z_max
            )
            is_cut = inside_bb and not c.is_convex

            ax = tuple(_r(float(v)) for v in c.axis)

            result.append(
                CylinderPrimitive(
                    center_x=_r(cx),
                    center_y=_r(cy),
                    center_z=_r(cz),
                    diameter=_r(c.radius * 2.0),
                    height=_r(c.height),
                    axis=ax,  # type: ignore[arg-type]
                    is_cut=is_cut,
                )
            )

        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _r(v: float, decimals: int = 3) -> float:
    """Round to *decimals* significant decimal places."""
    return round(v, decimals)
