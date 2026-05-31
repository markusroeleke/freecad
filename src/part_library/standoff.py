import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Box,
    Cylinder,
    Polygon,
    Polyhedron,
    move,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)


class Standoff:
    """PCB standoff / spacer — cylindrical or hexagonal pillar with a central
    through-bore and optional entry chamfers and base flange.

    Parameters
    ----------
    outer_diameter : float
        Outer diameter of the standoff body (mm).  For shape="hex" this is the
        diameter of the circumscribed circle (vertex-to-vertex).
    inner_diameter : float
        Bore diameter for the screw clearance hole (mm).  Default 3.2 mm suits
        an M3 screw.
    height : float
        Total height of the standoff pillar (mm).
    shape : {"round", "hex"}
        Cross-section profile.
    chamfer : float
        Radius of the conical lead-in chamfer applied to both bore entries (mm).
        Set to 0 to disable.
    base_flange : float
        Outer diameter of an optional circular flange at z=0 (mm).
        ``0`` means no flange.  When > 0 a 1.5 mm tall disc is fused to the
        base of the body before the bore is cut.
    """

    FLANGE_HEIGHT = 1.5

    def __init__(
        self,
        outer_diameter: float = 8.0,
        inner_diameter: float = 3.2,
        height: float = 10.0,
        shape: str = "round",
        chamfer: float = 0.5,
        base_flange: float = 0,
    ):
        self.outer_diameter = outer_diameter
        self.inner_diameter = inner_diameter
        self.height = height
        self.shape = shape
        self.chamfer = chamfer
        self.base_flange = base_flange

        self.solid = self._build()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _outer_body(self) -> Part.Shape:
        """Return the un-bored outer body solid."""
        r = self.outer_diameter / 2
        h = self.height
        if self.shape == "hex":
            p1 = Polygon(Vector(0, 0, 0), r, Vector(0, 0, 1), sides=6)
            p2 = Polygon(Vector(0, 0, h), r, Vector(0, 0, 1), sides=6)
            return Polyhedron(p1, p2).solid
        else:
            return Part.makeCylinder(r, h, Vector(0, 0, 0), Vector(0, 0, 1))

    def _bore(self) -> Part.Shape:
        """Central through-bore, slightly oversized on both ends for clean booleans."""
        return Part.makeCylinder(
            self.inner_diameter / 2,
            self.height + 1,
            Vector(0, 0, -0.5),
            Vector(0, 0, 1),
        )

    def _chamfer_cone_bottom(self) -> Part.Shape:
        """Conical lead-in at the bottom bore entry (z=0).

        Wider end (r = inner_r + chamfer) sits at z=0; narrows to inner_r at
        z=chamfer, matching a 45-degree chamfer profile.
        """
        ir = self.inner_diameter / 2
        c = self.chamfer
        return Part.makeCone(ir + c, ir, c, Vector(0, 0, 0), Vector(0, 0, 1))

    def _chamfer_cone_top(self) -> Part.Shape:
        """Conical lead-in at the top bore entry (z=height).

        Wider end sits at z=height; narrows to inner_r at z=height-chamfer.
        """
        ir = self.inner_diameter / 2
        c = self.chamfer
        return Part.makeCone(ir + c, ir, c, Vector(0, 0, self.height), Vector(0, 0, -1))

    def _build(self) -> Part.Shape:
        body = self._outer_body()

        # Optional base flange — fuse before cutting bore so the bore pierces it too
        if self.base_flange > 0:
            flange = Part.makeCylinder(
                self.base_flange / 2,
                self.FLANGE_HEIGHT,
                Vector(0, 0, 0),
                Vector(0, 0, 1),
            )
            body = body.fuse(flange)

        cutters = [self._bore()]

        if self.chamfer > 0:
            cutters.append(self._chamfer_cone_bottom())
            cutters.append(self._chamfer_cone_top())

        return cut_all(body, cutters)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    new_doc("StandoffDemo")
    s1 = Standoff()
    s2 = Standoff(shape="hex", height=15, base_flange=12)
    show_solid(s1.solid, color=(0.6, 0.6, 0.9), name="Round")
    show_solid(move(s2.solid, Vector(20, 0, 0)), color=(0.9, 0.7, 0.3), name="Hex")
    fit_view()
