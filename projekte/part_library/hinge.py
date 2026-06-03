import sys
from pathlib import Path
lib_path = Path(__file__).parent.parent

sys.path.insert(0,lib_path)
for p in sys.path:
    print(p)

import FreeCAD, Part
from FreeCAD import Vector
import math

from freecad_lib import (
    Box,
    Cylinder,
    Polygon,
    Polyhedron,
    move,
    rotate,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)

# ---------------------------------------------------------------------------
# Default parameters (all dimensions in mm)
# ---------------------------------------------------------------------------

DEFAULT_PARAMS = dict(
    leaf_width=30,
    leaf_length=40,
    leaf_thickness=3,
    barrel_diameter=8,
    barrel_inner_d=3,
    knuckle_count=3,
    pin_clearance=0.25,
    knuckle_gap=0.3,
    hole_diameter=3.5,
    hole_margin=5.0,
    holes_per_leaf=2,
)

# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _build_leaf(knuckle_indices, p):
    """Build one hinge leaf and return its solid.

    Coordinate convention
    ---------------------
    * Barrel axis = Z.  Full barrel height = leaf_width.
    * Leaf plate: x in [-leaf_width/2 .. leaf_width/2],
                  y in [-leaf_length .. 0],
                  z in [0 .. leaf_thickness]
    * Knuckle cylinders are centred on (x=0, y=0) and rise along +Z.
    * Bore runs from z=-eps to z=leaf_width+eps for clean booleans.
    """
    leaf_width = p["leaf_width"]
    leaf_length = p["leaf_length"]
    leaf_thickness = p["leaf_thickness"]
    barrel_diameter = p["barrel_diameter"]
    barrel_inner_d = p["barrel_inner_d"]
    knuckle_count = p["knuckle_count"]
    pin_clearance = p["pin_clearance"]
    knuckle_gap = p["knuckle_gap"]
    hole_diameter = p["hole_diameter"]
    hole_margin = p["hole_margin"]
    holes_per_leaf = p["holes_per_leaf"]

    knuckle_height = (leaf_width - (knuckle_count - 1) * knuckle_gap) / knuckle_count

    # --- leaf plate --------------------------------------------------------
    plate = Box(
        Vector(-leaf_width / 2, -leaf_length, 0),
        Vector(leaf_width / 2, 0, leaf_thickness),
    ).solid

    # --- knuckle cylinders for this leaf -----------------------------------
    parts = [plate]
    for i in knuckle_indices:
        z_start = i * (knuckle_height + knuckle_gap)
        knuckle = Cylinder(
            f"knuckle_{i}",
            barrel_diameter,
            knuckle_height,
            position=Vector(0, 0, z_start),
        ).solid
        parts.append(knuckle)

    body = fuse_all(parts)

    # --- pin bore through the full knuckle stack ---------------------------
    # Extend slightly beyond [0, leaf_width] for clean boolean subtraction.
    eps = 1.0
    bore = Cylinder(
        "bore",
        barrel_inner_d + 2 * pin_clearance,
        leaf_width + 2 * eps,
        position=Vector(0, 0, -eps),
    ).solid
    body = body.cut(bore)

    # --- mounting holes (drilled through leaf_thickness along Z) -----------
    hole_depth = leaf_thickness + 2 * eps  # oversized for clean cut
    if holes_per_leaf == 1:
        y_positions = [-(leaf_length / 2)]
    else:
        y_start = -(leaf_length - hole_margin)
        y_end = -hole_margin
        step = (y_end - y_start) / (holes_per_leaf - 1)
        y_positions = [y_start + j * step for j in range(holes_per_leaf)]

    for y in y_positions:
        hole = Cylinder(
            "mhole",
            hole_diameter,
            hole_depth,
            position=Vector(0, y, -eps),
        ).solid
        body = body.cut(hole)

    return body


# ---------------------------------------------------------------------------
# Public classes
# ---------------------------------------------------------------------------


class HingeLeafA:
    """Hinge leaf that owns knuckle indices 0, 2, 4, …"""

    def __init__(self, **params):
        p = {**DEFAULT_PARAMS, **params}
        indices = list(range(0, p["knuckle_count"], 2))
        self.solid = _build_leaf(indices, p)


class HingeLeafB:
    """Hinge leaf that owns knuckle indices 1, 3, 5, …"""

    def __init__(self, **params):
        p = {**DEFAULT_PARAMS, **params}
        indices = list(range(1, p["knuckle_count"], 2))
        self.solid = _build_leaf(indices, p)


class HingePin:
    """Simple cylindrical pin that slides through the assembled barrel.

    diameter = barrel_inner_d  (pin fits in bore with pin_clearance gap per side)
    height   = barrel_height   (= leaf_width of the hinge)
    """

    def __init__(self, barrel_inner_d, barrel_height, pin_clearance=0.25):
        self.solid = Cylinder(
            "pin",
            barrel_inner_d,
            barrel_height,
            position=Vector(0, 0, 0),
        ).solid


class Hinge:
    """Complete barrel/pin hinge assembly.

    Attributes
    ----------
    leaf_a : HingeLeafA
    leaf_b : HingeLeafB
    pin    : HingePin
    solid  : fused visualisation solid (all three parts combined)
    """

    def __init__(self, **params):
        p = {**DEFAULT_PARAMS, **params}
        self.leaf_a = HingeLeafA(**params)
        self.leaf_b = HingeLeafB(**params)
        self.pin = HingePin(p["barrel_inner_d"], p["leaf_width"], p["pin_clearance"])
        self.solid = fuse_all([self.leaf_a.solid, self.leaf_b.solid, self.pin.solid])


# ---------------------------------------------------------------------------
# Demo entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    new_doc("HingeDemo")
    h = Hinge()
    show_solid(h.leaf_a.solid, color=(0.8, 0.5, 0.2), name="LeafA")
    show_solid(h.leaf_b.solid, color=(0.2, 0.5, 0.8), name="LeafB")
    show_solid(h.pin.solid, color=(0.8, 0.8, 0.8), name="Pin")
    fit_view()
