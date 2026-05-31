import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Box,
    Cylinder,
    Wedge,
    move,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)


class WallBracket:
    """L-shaped wall / shelf bracket with optional triangular gusset.

    Coordinate convention
    ---------------------
    Wall plate  : x = [0 .. plate_thickness],                      y = [0 .. wall_plate_width],  z = [0 .. wall_plate_height]
    Shelf plate : x = [plate_thickness .. plate_thickness + shelf_plate_depth],  y = [0 .. shelf_plate_width], z = [0 .. plate_thickness]
    Gusset      : right-triangle prism in the XZ plane at the inner corner,
                  extruded along Y for the full plate width.

    Parameters
    ----------
    wall_plate_width  : Y extent of the vertical wall plate (mm)
    wall_plate_height : Z extent of the vertical wall plate (mm)
    plate_thickness   : thickness of both plates (mm)
    shelf_plate_width : Y extent of the horizontal shelf plate (mm)
    shelf_plate_depth : X extent of the shelf plate, away from the wall (mm)
    gusset            : add a triangular reinforcement at the inner corner
    hole_diameter     : diameter of mounting holes (mm)
    holes_per_wall    : number of holes in the wall plate, evenly spaced in Z
    holes_per_shelf   : number of holes in the shelf plate, evenly spaced in X
    hole_margin       : minimum distance from hole centre to plate edge (mm)
    """

    def __init__(
        self,
        wall_plate_width: float = 40,
        wall_plate_height: float = 60,
        plate_thickness: float = 4,
        shelf_plate_width: float = 40,
        shelf_plate_depth: float = 50,
        gusset: bool = True,
        hole_diameter: float = 4.5,
        holes_per_wall: int = 3,
        holes_per_shelf: int = 2,
        hole_margin: float = 8,
    ):
        self.wall_plate_width = wall_plate_width
        self.wall_plate_height = wall_plate_height
        self.plate_thickness = plate_thickness
        self.shelf_plate_width = shelf_plate_width
        self.shelf_plate_depth = shelf_plate_depth
        self.gusset = gusset
        self.hole_diameter = hole_diameter
        self.holes_per_wall = holes_per_wall
        self.holes_per_shelf = holes_per_shelf
        self.hole_margin = hole_margin

        self.solid = self._build()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evenly_spaced(self, start: float, end: float, count: int):
        """Return *count* positions evenly distributed in [start, end]."""
        if count <= 0:
            return []
        if count == 1:
            return [(start + end) / 2]
        step = (end - start) / (count - 1)
        return [start + i * step for i in range(count)]

    def _build(self):
        pt = self.plate_thickness
        wpw = self.wall_plate_width
        wph = self.wall_plate_height
        spw = self.shelf_plate_width
        spd = self.shelf_plate_depth
        hd = self.hole_diameter
        hm = self.hole_margin

        # ------------------------------------------------------------------
        # Body: wall plate + shelf plate (+ optional gusset)
        # ------------------------------------------------------------------

        # Wall plate: x=[0..pt], y=[0..wpw], z=[0..wph]
        wall_plate = Box(Vector(0, 0, 0), Vector(pt, wpw, wph)).solid

        # Shelf plate: x=[pt..pt+spd], y=[0..spw], z=[0..pt]
        shelf_plate = Box(Vector(pt, 0, 0), Vector(pt + spd, spw, pt)).solid

        body_parts = [wall_plate, shelf_plate]

        if self.gusset:
            gs = min(spd, wph) * 0.4
            gusset_width = min(wpw, spw)

            # Right-triangle prism in XZ plane:
            #   right-angle corner at (pt, *, pt)
            #   base leg along X to (pt+gs, *, pt)
            #   vertical leg along Z to (pt, *, pt+gs)
            # Extruded along +Y by gusset_width
            v1 = Vector(pt, 0, pt)
            v2 = Vector(pt + gs, 0, pt)
            v3 = Vector(pt, 0, pt + gs)
            wire = Part.makePolygon([v1, v2, v3, v1])
            face = Part.Face(wire)
            gusset_solid = face.extrude(Vector(0, gusset_width, 0))
            body_parts.append(gusset_solid)

        body = fuse_all(body_parts)

        # ------------------------------------------------------------------
        # Holes
        # ------------------------------------------------------------------
        cutters = []

        # Wall plate holes: drilled through X, centred at x=pt/2, y=wpw/2
        # evenly spaced in z within [hm .. wph-hm]
        if self.holes_per_wall > 0:
            for z in self._evenly_spaced(hm, wph - hm, self.holes_per_wall):
                cyl = Cylinder(
                    "wall_hole",
                    hd,
                    pt + 2,  # slightly oversized for clean cut
                    Vector(-1, wpw / 2, z),  # start 1 mm before face
                    Vector(1, 0, 0),  # drill along +X
                )
                cutters.append(cyl.solid)

        # Shelf plate holes: drilled through Z, centred at z=pt/2, y=spw/2
        # evenly spaced in x within [pt+hm .. pt+spd-hm]
        if self.holes_per_shelf > 0:
            for x in self._evenly_spaced(pt + hm, pt + spd - hm, self.holes_per_shelf):
                cyl = Cylinder(
                    "shelf_hole",
                    hd,
                    pt + 2,  # slightly oversized for clean cut
                    Vector(x, spw / 2, -1),  # start 1 mm below face
                    Vector(0, 0, 1),  # drill along +Z
                )
                cutters.append(cyl.solid)

        if cutters:
            body = cut_all(body, cutters)

        return body


if __name__ == "__main__":
    new_doc("WallBracketDemo")
    wb = WallBracket()
    show_solid(wb.solid, color=(0.7, 0.5, 0.3), name="Bracket")
    fit_view()
