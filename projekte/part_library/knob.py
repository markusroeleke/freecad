import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Cylinder,
    Polygon,
    Polyhedron,
    NutTrap,
    HeatSetInsert,
    array_polar,
    move,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
    HEAT_SET_INSERT_MAP,
    NUT_MAP,
)


class Knob:
    """Knurled thumb-screw knob with vertical rib grooves and a central insert pocket.

    The body is a cylinder whose outer surface is interrupted by evenly-spaced
    vertical rectangular grooves (simulated knurling).  The top outer edge
    carries a 45-degree chamfer.  A threaded insert pocket (heat-set or nut
    trap) is sunk into the top face along the central axis.

    Parameters
    ----------
    diameter : float
        Outer diameter of the knob body (mm).
    height : float
        Total height (mm).
    rib_count : int
        Number of vertical rib grooves around the circumference.
    rib_height : float
        Height of the ribbed zone, centred vertically (mm).
    rib_depth : float
        How deep each rib groove is cut into the surface (mm).
    insert_type : {"heat_set", "nut_trap"}
        Type of insert pocket in the centre.
    insert_size : str
        Thread size key, e.g. "M3", "M4", "M5".
    top_chamfer : float
        45-degree bevel size on the top outer edge (mm).
    """

    def __init__(
        self,
        diameter: float = 30.0,
        height: float = 15.0,
        rib_count: int = 18,
        rib_height: float = 8.0,
        rib_depth: float = 1.2,
        insert_type: str = "heat_set",
        insert_size: str = "M4",
        top_chamfer: float = 1.5,
    ):
        self.diameter = diameter
        self.height = height
        self.rib_count = rib_count
        self.rib_height = rib_height
        self.rib_depth = rib_depth
        self.insert_type = insert_type
        self.insert_size = insert_size
        self.top_chamfer = top_chamfer

        self.solid = self._build()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _top_chamfer_cutter(self, r: float, h: float, tc: float) -> Part.Shape:
        """Return an annular solid that cuts a 45-degree bevel on the top outer edge.

        The cutter occupies the ring between the inner chamfer cone and the
        outer cylindrical surface, from z = h-tc to z = h.  Subtracting it from
        the body removes only the outer corner, leaving a clean slanted edge.
        """
        outer_cyl = Part.makeCylinder(r, tc, Vector(0, 0, h - tc))
        inner_cone = Part.makeCone(r, r - tc, tc, Vector(0, 0, h - tc))
        return outer_cyl.cut(inner_cone)

    def _groove_cutter(self, r: float, rib_z: float) -> Part.Shape:
        """Return a single rectangular groove cutter Box positioned at angle 0 (along +X).

        The box straddles the cylinder surface so it cuts rib_depth / 2 into the
        body.  array_polar() distributes rib_count copies around the Z axis.
        """
        return Part.makeBox(
            self.rib_depth + 2,  # radial extent (spans surface)
            2.0,  # tangential width (mm)
            self.rib_height + 2,  # slightly taller than rib zone
            Vector(r - self.rib_depth / 2, -1.0, rib_z),
        )

    def _insert_pocket(self, h: float) -> Part.Shape:
        """Return the insert pocket solid (to be subtracted from the body).

        The pocket opens at the top face (z = h) and descends toward z = 0.
        """
        if self.insert_type == "heat_set":
            return HeatSetInsert(
                "insert",
                self.insert_size,
                position=Vector(0, 0, h),
                normal=Vector(0, 0, -1),
            ).solid
        else:
            return NutTrap(
                "insert",
                self.insert_size,
                position=Vector(0, 0, h),
                normal=Vector(0, 0, -1),
            ).solid

    def _build(self) -> Part.Shape:
        r = self.diameter / 2
        h = self.height
        tc = self.top_chamfer

        # 1. Main cylindrical body
        body = Part.makeCylinder(r, h)

        # 2. Top outer chamfer
        if tc > 0:
            body = body.cut(self._top_chamfer_cutter(r, h, tc))

        # 3. Rib grooves — one Box cutter arrayed rib_count times around Z
        rib_z = (h - self.rib_height) / 2
        groove = self._groove_cutter(r, rib_z)
        body = body.cut(array_polar(groove, self.rib_count))

        # 4. Central insert pocket from the top face
        body = body.cut(self._insert_pocket(h))

        return body


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    new_doc("KnobDemo")
    k1 = Knob(insert_type="heat_set", insert_size="M4")
    k2 = Knob(
        diameter=25, height=12, rib_count=14, insert_type="nut_trap", insert_size="M4"
    )
    show_solid(k1.solid, color=(0.6, 0.2, 0.8), name="KnobHeatSet")
    show_solid(
        move(k2.solid, Vector(40, 0, 0)), color=(0.3, 0.7, 0.5), name="KnobNutTrap"
    )
    fit_view()
