import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Box,
    Cylinder,
    move,
    rotate,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)


class JHook:
    """Wall-mounted J-hook built entirely from Box and Cylinder CSG.

    Parameters
    ----------
    base_width : float
        Width (X) of the mounting base plate in mm.
    base_height : float
        Height (Z) of the mounting base plate in mm.
    base_thickness : float
        Depth (Y) of the mounting base plate in mm.
    stem_height : float
        Height of the vertical stem above the base plate in mm.
    arm_length : float
        Length of the horizontal hook arm in mm.
    arm_angle : float
        Upward tilt of the arm in degrees.
    profile_w : float
        Width (X) of the stem / arm cross-section in mm.
    profile_d : float
        Depth (Y) of the stem / arm cross-section in mm.
    tip_drop : float
        Downward drop of the tip box at the arm end in mm.
    hole_diameter : float
        Diameter of the mounting holes in mm.
    holes_per_base : int
        Number of mounting holes in the base plate.
    hole_margin : float
        Distance from the top and bottom edges of the base plate to the first
        and last hole centres in mm.
    """

    def __init__(
        self,
        base_width=30,
        base_height=40,
        base_thickness=4,
        stem_height=50,
        arm_length=40,
        arm_angle=10,
        profile_w=8,
        profile_d=8,
        tip_drop=10,
        hole_diameter=4.5,
        holes_per_base=2,
        hole_margin=8,
    ):
        self.base_width = base_width
        self.base_height = base_height
        self.base_thickness = base_thickness
        self.stem_height = stem_height
        self.arm_length = arm_length
        self.arm_angle = arm_angle
        self.profile_w = profile_w
        self.profile_d = profile_d
        self.tip_drop = tip_drop
        self.hole_diameter = hole_diameter
        self.holes_per_base = holes_per_base
        self.hole_margin = hole_margin

        self.solid = self._build()

    # ------------------------------------------------------------------

    def _build(self):
        bw = self.base_width
        bh = self.base_height
        bt = self.base_thickness
        sh = self.stem_height
        al = self.arm_length
        aa = self.arm_angle
        pw = self.profile_w
        pd = self.profile_d
        td = self.tip_drop
        hd = self.hole_diameter
        hpb = self.holes_per_base
        hm = self.hole_margin

        # 1. Base plate
        base = Box(Vector(-bw / 2, 0, 0), Vector(bw / 2, bt, bh))

        # 2. Vertical stem above base plate
        stem = Box(Vector(-pw / 2, 0, bh), Vector(pw / 2, pd, bh + sh))

        # 3. Arm — build at local origin then move and tilt
        #    Before rotation: x=[-pw/2..pw/2], y=[0..al], z=[0..pd]
        #    After move: base of arm sits at z = bh + sh
        #    Rotate arm_angle upward around X axis at that base level.
        arm_local = Box(Vector(-pw / 2, 0, 0), Vector(pw / 2, al, pd))
        arm_moved = move(arm_local.solid, Vector(0, 0, bh + sh))
        arm_solid = rotate(
            arm_moved,
            aa,
            Vector(1, 0, 0),
            Vector(0, 0, bh + sh),
        )

        # 4. Tip drop — small box hanging down from the arm end
        #    The arm end (y = al, z = 0 in local arm space) after rotation:
        aa_rad = math.radians(aa)
        y_arm_end = al * math.cos(aa_rad)
        z_arm_end = bh + sh + al * math.sin(aa_rad)

        tip_local = Box(Vector(-pw / 2, 0, -td), Vector(pw / 2, pd, 0))
        tip_solid = move(tip_local.solid, Vector(0, y_arm_end, z_arm_end))

        # Fuse all positive geometry
        body = fuse_all([base.solid, stem.solid, arm_solid, tip_solid])

        # 5. Mounting holes — cylinders through base plate along Y axis
        if hpb == 1:
            hole_z_positions = [bh / 2]
        else:
            step = (bh - 2 * hm) / (hpb - 1)
            hole_z_positions = [hm + i * step for i in range(hpb)]

        holes = [
            Cylinder("hole", hd, bt + 2, Vector(0, -1, z), Vector(0, 1, 0)).solid
            for z in hole_z_positions
        ]

        return cut_all(body, holes)


class SHook:
    """Free-hanging S-hook built entirely from Box CSG.

    One end hooks onto a wall rail / rod; the other end holds items.

    Parameters
    ----------
    total_height : float
        Full height of the central bar in mm.
    arm_length : float
        Horizontal reach of each hook arm in mm.
    profile_w : float
        Width (X) of all cross-sections in mm.
    profile_d : float
        Depth (Y) of all cross-sections in mm.
    tip_drop : float
        Height of the tip box at each arm end in mm.
    """

    def __init__(
        self,
        total_height=80,
        arm_length=30,
        profile_w=8,
        profile_d=8,
        tip_drop=10,
    ):
        self.total_height = total_height
        self.arm_length = arm_length
        self.profile_w = profile_w
        self.profile_d = profile_d
        self.tip_drop = tip_drop

        self.solid = self._build()

    # ------------------------------------------------------------------

    def _build(self):
        th = self.total_height
        al = self.arm_length
        pw = self.profile_w
        pd = self.profile_d
        td = self.tip_drop

        # Central vertical bar
        bar = Box(Vector(-pw / 2, 0, 0), Vector(pw / 2, pd, th))

        # Upper hook — arm extends in +Y at the top of the bar,
        # tip drops downward from the arm end.
        upper_arm = Box(Vector(-pw / 2, 0, th - pd), Vector(pw / 2, al, th))
        upper_tip = Box(
            Vector(-pw / 2, al - pd, th - pd - td), Vector(pw / 2, al, th - pd)
        )

        # Lower hook — arm extends in -Y at the bottom of the bar,
        # tip rises upward from the arm end (mirror of upper).
        lower_arm = Box(Vector(-pw / 2, -al, 0), Vector(pw / 2, 0, pd))
        lower_tip = Box(Vector(-pw / 2, -al, pd), Vector(pw / 2, -al + pd, pd + td))

        return fuse_all(
            [
                bar.solid,
                upper_arm.solid,
                upper_tip.solid,
                lower_arm.solid,
                lower_tip.solid,
            ]
        )


if __name__ == "__main__":
    new_doc("HookDemo")
    jh = JHook()
    sh = SHook()
    show_solid(jh.solid, color=(0.8, 0.3, 0.2), name="JHook")
    show_solid(move(sh.solid, Vector(80, 0, 0)), color=(0.2, 0.5, 0.8), name="SHook")
    fit_view()
