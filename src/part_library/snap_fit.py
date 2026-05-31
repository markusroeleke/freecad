import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Box,
    Cylinder,
    Polygon,
    Polyhedron,
    Flat,
    move,
    rotate,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)

# ---------------------------------------------------------------------------
# FDM design rules
# ---------------------------------------------------------------------------

_MIN_ARM_THICKNESS = 1.5  # mm – flexural strength requires min printed wall


# ---------------------------------------------------------------------------
# Default parameters (all dimensions in mm)
# ---------------------------------------------------------------------------

DEFAULT = dict(
    base_width=20,
    base_length=20,
    base_thickness=4,
    arm_width=10,
    arm_length=25,
    arm_thickness=2,
    hook_height=2.5,
    hook_lead_angle=30,
    hook_retention_angle=80,
    receptor_wall=3,
    receptor_depth=20,
    clearance=0.25,
    hole_diameter=3.5,
)


# ---------------------------------------------------------------------------
# SnapHook  (male part)
# ---------------------------------------------------------------------------


class SnapHook:
    """
    Male (hook) part of a cantilever snap-fit clip.

    Coordinate convention
    ---------------------
    Base plate : XY plane, z = 0 → base_thickness, centred in X,
                 y = -base_length → 0.
    Arm        : x ∈ [-arm_width/2, arm_width/2],
                 y = 0 → arm_length,
                 z = base_thickness → base_thickness + arm_thickness.
                 Printed parallel to the bed for maximum flexural strength.
    Hook       : Triangular prism on top of the arm tip (+Z direction).
                 - Ramp face  (snap-in / lead-in, faces +Y) :
                       angled at hook_lead_angle from horizontal (~30°).
                 - Retention face (faces −Y, resists withdrawal) :
                       angled at hook_retention_angle from horizontal (~80°).
    """

    def __init__(
        self,
        base_width=DEFAULT["base_width"],
        base_length=DEFAULT["base_length"],
        base_thickness=DEFAULT["base_thickness"],
        arm_width=DEFAULT["arm_width"],
        arm_length=DEFAULT["arm_length"],
        arm_thickness=DEFAULT["arm_thickness"],
        hook_height=DEFAULT["hook_height"],
        hook_lead_angle=DEFAULT["hook_lead_angle"],
        hook_retention_angle=DEFAULT["hook_retention_angle"],
        hole_diameter=DEFAULT["hole_diameter"],
    ):
        # FDM rule: arm must be at least 1.5 mm thick for sufficient flex
        arm_thickness = max(arm_thickness, _MIN_ARM_THICKNESS)

        self.base_width = base_width
        self.base_length = base_length
        self.base_thickness = base_thickness
        self.arm_width = arm_width
        self.arm_length = arm_length
        self.arm_thickness = arm_thickness
        self.hook_height = hook_height
        self.hook_lead_angle = hook_lead_angle
        self.hook_retention_angle = hook_retention_angle
        self.hole_diameter = hole_diameter

        self.solid = self._build()

    def _build(self):
        bw = self.base_width
        bl = self.base_length
        bt = self.base_thickness
        aw = self.arm_width
        al = self.arm_length
        at = self.arm_thickness
        hh = self.hook_height
        hla = math.radians(self.hook_lead_angle)
        hra = math.radians(self.hook_retention_angle)
        hd = self.hole_diameter

        # ---- base plate --------------------------------------------------
        # centred in X, recessed behind arm root (y = -base_length → 0)
        base = Box(
            Vector(-bw / 2, -bl, 0),
            Vector(bw / 2, 0, bt),
        ).solid

        # optional bolt hole through the base plate (centred, Z-axis bore)
        if hd > 0:
            eps = 1.0
            bore = Cylinder(
                "hole",
                hd,
                bt + 2 * eps,
                position=Vector(0, -bl / 2, -eps),
            ).solid
            base = base.cut(bore)

        # ---- cantilever arm ----------------------------------------------
        # printed parallel to XY bed; arm extends in +Y from the base edge
        arm = Box(
            Vector(-aw / 2, 0, bt),
            Vector(aw / 2, al, bt + at),
        ).solid

        # ---- hook (triangular prism) -------------------------------------
        # Cross-section in the YZ plane drawn at x = −arm_width/2,
        # then extruded arm_width in the +X direction.
        #
        #   z = bt+at+hh         *  ← apex
        #                       /|
        #     ramp (lead-in)   / |  retention wall (steep)
        #                     /  |
        #   z = bt+at  ______/___*__ ← arm top surface
        #               back   tip-y  front (y = arm_length)
        #
        # Horizontal footprints along Y:
        #   dy_ramp      = hh / tan(lead_angle)       [gradual, e.g. 4.3 mm]
        #   dy_retention = hh / tan(retention_angle)  [steep,   e.g. 0.4 mm]
        #
        # Insertion direction is +Y, so the ramp faces +Y (snap-in side)
        # and the retention wall faces −Y (lock-in side).
        dy_ramp = hh / math.tan(hla)
        dy_ret = hh / math.tan(hra)

        x0 = -aw / 2
        z0 = bt + at

        v_front = Vector(x0, al, z0)  # ramp base (arm tip)
        v_apex = Vector(x0, al - dy_ramp, z0 + hh)  # hook apex
        v_back = Vector(x0, al - dy_ramp - dy_ret, z0)  # retention base

        # closed triangle profile → Flat creates a planar face in YZ
        hook_profile = Flat([v_front, v_apex, v_back, v_front])
        hook_solid = hook_profile.face.extrude(Vector(aw, 0, 0))

        # ---- combine all parts -------------------------------------------
        return fuse_all([base, arm, hook_solid])


# ---------------------------------------------------------------------------
# SnapReceptor  (female part)
# ---------------------------------------------------------------------------


class SnapReceptor:
    """
    Female (receptor) part of a cantilever snap-fit clip.

    A solid rectangular box with a rectangular through-slot cut along the Y
    axis.  The arm + hook assembly inserts from the −Y face of the receptor.

    Slot dimensions (sized to clear arm cross-section + hook protrusion):
        slot_width  = arm_width  + 2 × clearance
        slot_height = arm_thickness + hook_height + 2 × clearance

    The slot is centred in X and sits above the bottom wall, leaving walls of
    thickness receptor_wall on all six sides of the outer box.
    """

    def __init__(
        self,
        arm_width=DEFAULT["arm_width"],
        arm_thickness=DEFAULT["arm_thickness"],
        hook_height=DEFAULT["hook_height"],
        receptor_wall=DEFAULT["receptor_wall"],
        receptor_depth=DEFAULT["receptor_depth"],
        clearance=DEFAULT["clearance"],
    ):
        arm_thickness = max(arm_thickness, _MIN_ARM_THICKNESS)

        self.arm_width = arm_width
        self.arm_thickness = arm_thickness
        self.hook_height = hook_height
        self.receptor_wall = receptor_wall
        self.receptor_depth = receptor_depth
        self.clearance = clearance

        self.solid = self._build()

    def _build(self):
        aw = self.arm_width
        at = self.arm_thickness
        hh = self.hook_height
        rw = self.receptor_wall
        rd = self.receptor_depth
        cl = self.clearance

        # rectangular window that accepts the arm + hook with clearance
        slot_w = aw + 2 * cl
        slot_h = at + hh + 2 * cl

        # outer box: walls of rw on every side
        outer_w = slot_w + 2 * rw
        outer_h = slot_h + 2 * rw

        # outer box centred in X, y = 0 → receptor_depth, z = 0 → outer_h
        outer = Box(
            Vector(-outer_w / 2, 0, 0),
            Vector(outer_w / 2, rd, outer_h),
        ).solid

        # through-slot centred in X, full Y depth (eps for clean booleans)
        eps = 1.0
        slot = Box(
            Vector(-slot_w / 2, -eps, rw),
            Vector(slot_w / 2, rd + eps, rw + slot_h),
        ).solid

        return outer.cut(slot)


# ---------------------------------------------------------------------------
# SnapFit  (assembly / preview helper)
# ---------------------------------------------------------------------------


class SnapFit:
    """
    Convenience assembly: instantiates both hook and receptor and places them
    side-by-side in the scene for visual inspection.

    Attributes
    ----------
    hook     : SnapHook instance (male part)
    receptor : SnapReceptor instance (female part)
    solid    : fused compound of both parts positioned side-by-side
    """

    def __init__(
        self,
        base_width=DEFAULT["base_width"],
        base_length=DEFAULT["base_length"],
        base_thickness=DEFAULT["base_thickness"],
        arm_width=DEFAULT["arm_width"],
        arm_length=DEFAULT["arm_length"],
        arm_thickness=DEFAULT["arm_thickness"],
        hook_height=DEFAULT["hook_height"],
        hook_lead_angle=DEFAULT["hook_lead_angle"],
        hook_retention_angle=DEFAULT["hook_retention_angle"],
        receptor_wall=DEFAULT["receptor_wall"],
        receptor_depth=DEFAULT["receptor_depth"],
        clearance=DEFAULT["clearance"],
        hole_diameter=DEFAULT["hole_diameter"],
    ):
        arm_thickness = max(arm_thickness, _MIN_ARM_THICKNESS)

        self.hook = SnapHook(
            base_width=base_width,
            base_length=base_length,
            base_thickness=base_thickness,
            arm_width=arm_width,
            arm_length=arm_length,
            arm_thickness=arm_thickness,
            hook_height=hook_height,
            hook_lead_angle=hook_lead_angle,
            hook_retention_angle=hook_retention_angle,
            hole_diameter=hole_diameter,
        )

        self.receptor = SnapReceptor(
            arm_width=arm_width,
            arm_thickness=arm_thickness,
            hook_height=hook_height,
            receptor_wall=receptor_wall,
            receptor_depth=receptor_depth,
            clearance=clearance,
        )

        # place receptor to the right (+X) of the hook for side-by-side preview
        slot_w = arm_width + 2 * clearance
        outer_w = slot_w + 2 * receptor_wall
        gap = 5.0
        x_offset = base_width / 2 + gap + outer_w / 2
        receptor_placed = move(self.receptor.solid, Vector(x_offset, 0, 0))

        self.solid = fuse_all([self.hook.solid, receptor_placed])


# ---------------------------------------------------------------------------
# Demo entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    new_doc("SnapFitDemo")
    sf = SnapFit()
    show_solid(sf.hook.solid, color=(0.8, 0.4, 0.1), name="Hook")
    show_solid(sf.receptor.solid, color=(0.2, 0.6, 0.4), name="Receptor")
    fit_view()
