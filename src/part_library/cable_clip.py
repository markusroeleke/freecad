import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Box,
    Cylinder,
    Tube,
    Polygon,
    Polyhedron,
    move,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)

# ---------------------------------------------------------------------------
# Default parameters (all dimensions in mm)
# ---------------------------------------------------------------------------

DEFAULT = dict(
    cable_diameter=8.0,
    cable_clearance=0.3,
    wall_thickness=2.5,
    base_thickness=3.0,
    mount_margin=5.0,
    hole_diameter=3.5,
    num_holes=2,
)


# ---------------------------------------------------------------------------
# CableClip
# ---------------------------------------------------------------------------


class CableClip:
    """Parametric 3D-printable cable saddle clamp.

    Coordinate convention
    ---------------------
    Base plate : centred at x=0, y in [0..base_length], z in [0..base_thickness].
    Saddle body: same x/y extents, z in [base_thickness..base_thickness+saddle_height].
    Cable axis : runs along X through the centre of the groove.
    Groove     : semicircular channel (half-cylinder void) cut from the top of the
                 saddle, opening upward so the cable snaps in from above.

    Parameters
    ----------
    cable_diameter  : outer diameter of cable / tube to hold (mm)
    cable_clearance : extra radial clearance around cable in groove (mm)
    wall_thickness  : wall thickness of saddle body around cable (mm)
    base_thickness  : thickness of the flat foot plate (mm)
    mount_margin    : extra width on each side of the saddle for mounting holes (mm)
    hole_diameter   : mounting hole diameter (mm)
    num_holes       : 1 (centre hole only) or 2 (one on each side)
    """

    def __init__(
        self,
        cable_diameter: float = DEFAULT["cable_diameter"],
        cable_clearance: float = DEFAULT["cable_clearance"],
        wall_thickness: float = DEFAULT["wall_thickness"],
        base_thickness: float = DEFAULT["base_thickness"],
        mount_margin: float = DEFAULT["mount_margin"],
        hole_diameter: float = DEFAULT["hole_diameter"],
        num_holes: int = DEFAULT["num_holes"],
    ):
        self.cable_diameter = cable_diameter
        self.cable_clearance = cable_clearance
        self.wall_thickness = wall_thickness
        self.base_thickness = base_thickness
        self.mount_margin = mount_margin
        self.hole_diameter = hole_diameter
        self.num_holes = num_holes

        # Derived dimensions
        self.cable_r = cable_diameter / 2.0 + cable_clearance
        # saddle height: enough to wrap halfway around cable + outer wall
        self.saddle_height = self.cable_r + wall_thickness
        # base length equals the cable zone width (Y direction)
        self.base_length = cable_diameter + 2.0 * wall_thickness
        # base width adds mounting margins on both sides of the saddle
        self.base_width = self.base_length + 2.0 * mount_margin

        self.solid = self._build()

    # ------------------------------------------------------------------
    # Internal build
    # ------------------------------------------------------------------

    def _build(self):
        wt = self.wall_thickness
        bt = self.base_thickness
        bl = self.base_length
        bw = self.base_width
        sh = self.saddle_height
        cr = self.cable_r

        # --- 1. Base plate -------------------------------------------------
        # x: [-bw/2 .. bw/2], y: [0 .. bl], z: [0 .. bt]
        base = Box(
            Vector(-bw / 2.0, 0.0, 0.0),
            Vector(bw / 2.0, bl, bt),
        ).solid

        # --- 2. Saddle body ------------------------------------------------
        # x: [-bl/2 .. bl/2], y: [0 .. bl], z: [bt .. bt+sh]
        # The saddle is as wide as the cable zone (base_length), centred on X.
        saddle = Box(
            Vector(-bl / 2.0, 0.0, bt),
            Vector(bl / 2.0, bl, bt + sh),
        ).solid

        # --- 3. Cable groove -------................................................
        # Cylinder running along X, centred at (0, bl/2, bt + wt + cr).
        # Radius = cable_r.  Length is wider than the saddle to ensure a clean cut.
        groove_extra = bw  # extend well past the saddle in both X directions
        groove_len = bl + 2.0 * groove_extra
        groove_x_start = -groove_len / 2.0

        groove_cyl = Cylinder(
            name="groove",
            diameter=2.0 * cr,
            height=groove_len,
            position=Vector(groove_x_start, bl / 2.0, bt + wt + cr),
            normal=Vector(1, 0, 0),
        ).solid

        # --- 4. Mounting holes ---------------------------------------------
        # Through the base plate (along Z), centred in Y at bl/2.
        # num_holes==1 -> single hole at x=0
        # num_holes==2 -> holes at x = +/- (bl/2 + mount_margin/2)
        hole_len = bt + 2.0  # extend through base + a little past both faces
        hole_z_start = -1.0  # start slightly below base bottom

        hole_positions = []
        if self.num_holes == 1:
            hole_positions.append(0.0)
        else:
            x_off = bl / 2.0 + self.mount_margin / 2.0
            hole_positions = [-x_off, x_off]

        holes = []
        for hx in hole_positions:
            h = Cylinder(
                name="hole",
                diameter=self.hole_diameter,
                height=hole_len,
                position=Vector(hx, bl / 2.0, hole_z_start),
                normal=Vector(0, 0, 1),
            ).solid
            holes.append(h)

        # --- 5. Boolean operations -----------------------------------------
        # Fuse base + saddle, then cut groove and holes.
        body = fuse_all([base, saddle])
        cutters = [groove_cyl] + holes
        result = cut_all(body, cutters)

        return result


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    new_doc("CableClipDemo")
    cc = CableClip()
    show_solid(cc.solid, color=(0.3, 0.6, 0.9), name="CableClip")
    fit_view()
