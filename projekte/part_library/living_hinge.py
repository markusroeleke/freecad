"""
Living Hinge Panel – parametric FreeCAD/Part module
=====================================================

PRINT ORIENTATION NOTE:
    For maximum flexibility, orient the part so that **layer lines run
    parallel to the X-axis** (i.e. the slicer moves along X during each
    layer).  This places the layer interfaces perpendicular to the bend
    axis (Y), which is the weakest direction in FDM and therefore gives the
    hinge its flexibility.  A hinge_thickness of 0.6 mm (1–2 layers) is
    recommended for PLA/PETG.
"""

import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import Box, move, fuse_all, new_doc, show_solid, fit_view


class LivingHinge:
    """Parametric 3D-printable living hinge panel.

    Three coplanar sections in the XY plane at z=0:
      - left rigid panel
      - thin flexible web (the living hinge zone)
      - right rigid panel

    PRINT ORIENTATION NOTE:
        Layer lines must run along X (perpendicular to the Y bend-axis) so
        that inter-layer bonds are what flex, minimising stress concentration.
        Recommended hinge_thickness ≈ 0.6 mm (1–2 FDM layers).

    Parameters
    ----------
    panel_width : float
        X dimension of each rigid side panel (mm).
    panel_length : float
        Y dimension of each panel (mm).
    panel_thickness : float
        Z thickness of the rigid panels (mm).
    hinge_width : float
        Y span of the flexible hinge web (should equal panel_length for a
        flush edge, but can be narrower).
    hinge_length : float
        X span of the flexible web between the two panels (mm).
    hinge_thickness : float
        Z thickness of the flexible web (mm).  FDM minimum ≈ 0.6 mm.
    num_notches : int
        Number of semicircular stress-relief notches cut alternately from
        the top and bottom edges of the web.  0 = plain flat web.
    notch_radius : float
        Radius of each semicircular notch (mm).

    Attributes
    ----------
    left_panel_solid : Part.Shape
    hinge_solid : Part.Shape
    right_panel_solid : Part.Shape
    solid : Part.Shape
        All three sections fused into one combined solid.
    """

    def __init__(
        self,
        panel_width: float = 40,
        panel_length: float = 60,
        panel_thickness: float = 3,
        hinge_width: float = 20,
        hinge_length: float = 8,
        hinge_thickness: float = 0.6,
        num_notches: int = 5,
        notch_radius: float = 2.0,
    ):
        hl2 = hinge_length / 2.0

        # ── Left panel ────────────────────────────────────────────────────────
        # x = [-panel_width - hinge_length/2 .. -hinge_length/2]
        self.left_panel_solid = Box(
            Vector(-panel_width - hl2, 0, 0),
            Vector(-hl2, panel_length, panel_thickness),
        ).solid

        # ── Right panel ───────────────────────────────────────────────────────
        # x = [hinge_length/2 .. hinge_length/2 + panel_width]
        self.right_panel_solid = Box(
            Vector(hl2, 0, 0),
            Vector(hl2 + panel_width, panel_length, panel_thickness),
        ).solid

        # ── Hinge web (base slab) ─────────────────────────────────────────────
        # x = [-hinge_length/2 .. hinge_length/2], thin in Z
        web = Box(
            Vector(-hl2, 0, 0),
            Vector(hl2, hinge_width, hinge_thickness),
        ).solid

        # ── Semicircular notch cutters ────────────────────────────────────────
        # Cylinders run along Z and are positioned on the Y-edges of the web
        # so that only the half inside the web is removed, giving a clean
        # semicircular relief notch.
        if num_notches > 0:
            cutter_height = hinge_thickness + 1.0  # extend past both Z faces
            for i in range(num_notches):
                # evenly space notch centres along X within the hinge zone
                x_pos = -hl2 + (i + 1) * hinge_length / (num_notches + 1)
                # alternate: even index → bottom edge (y=0), odd → top edge
                y_center = 0.0 if (i % 2 == 0) else hinge_width
                cyl = Part.makeCylinder(
                    notch_radius,
                    cutter_height,
                    Vector(x_pos, y_center, -0.5),  # start slightly below web
                    Vector(0, 0, 1),  # axis along Z
                )
                web = web.cut(cyl)

        self.hinge_solid = web

        # ── Combined solid (convenience attribute) ────────────────────────────
        self.solid = fuse_all(
            [
                self.left_panel_solid,
                self.hinge_solid,
                self.right_panel_solid,
            ]
        )


if __name__ == "__main__":
    new_doc("LivingHingeDemo")
    lh = LivingHinge()
    show_solid(lh.left_panel_solid, color=(0.7, 0.4, 0.2), name="LeftPanel")
    show_solid(lh.hinge_solid, color=(0.9, 0.9, 0.2), name="Hinge")
    show_solid(lh.right_panel_solid, color=(0.7, 0.4, 0.2), name="RightPanel")
    fit_view()
