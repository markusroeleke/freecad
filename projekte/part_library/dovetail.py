import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Flat,
    Box,
    move,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)

# ---------------------------------------------------------------------------
# Internal profile helper
# ---------------------------------------------------------------------------


def _dovetail_face(
    rail_width: float,
    neck_width: float,
    rail_height: float,
    base_thickness: float,
) -> Part.Shape:
    """Return a planar Part.Face of the dovetail cross-section in the XZ plane (y=0).

    Polygon vertices (listed CCW when viewed from +Y, closed):
        A  (-rail_width/2,  0,  0)              bottom-left of base rectangle
        B  (+rail_width/2,  0,  0)              bottom-right of base rectangle
        C  (+rail_width/2,  0,  base_thickness) right junction: base → trapezoid
        D  (+neck_width/2,  0,  rail_height)    top-right (narrowest, neck)
        E  (-neck_width/2,  0,  rail_height)    top-left  (narrowest, neck)
        F  (-rail_width/2,  0,  base_thickness) left junction: base → trapezoid
        A  (close)
    """
    hw = rail_width / 2.0
    hn = neck_width / 2.0
    bt = base_thickness
    rh = rail_height

    A = Vector(-hw, 0.0, 0.0)
    B = Vector(hw, 0.0, 0.0)
    C = Vector(hw, 0.0, bt)
    D = Vector(hn, 0.0, rh)
    E = Vector(-hn, 0.0, rh)
    F = Vector(-hw, 0.0, bt)

    flat = Flat([A, B, C, D, E, F, A])
    return flat.face


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------


class DovetailRail:
    """Parametric dovetail rail, extruded along the Y axis.

    The rail is centred on X=0, resting on the Z=0 plane, running from
    Y=0 to Y=rail_length.

    Parameters
    ----------
    rail_length : float
        Length of the rail along Y (mm).
    rail_width : float
        Total width of the rail base in X (mm).
    rail_height : float
        Total height of the rail in Z (mm).
    dovetail_angle : float
        Nominal angle of the dovetail sides from vertical (degrees).
        At 45° the overhang equals the rise, requiring no support.
        Note: the actual geometry is governed by neck_width and rail_height;
        this parameter is stored for documentation / derived-parameter use.
    neck_width : float
        Narrowest width at the top of the dovetail in X (mm).
    base_thickness : float
        Thickness of the flat base rectangle below the trapezoidal protrusion (mm).
    """

    def __init__(
        self,
        rail_length: float = 80.0,
        rail_width: float = 20.0,
        rail_height: float = 10.0,
        dovetail_angle: float = 45.0,
        neck_width: float = 8.0,
        base_thickness: float = 3.0,
    ):
        self.rail_length = rail_length
        self.rail_width = rail_width
        self.rail_height = rail_height
        self.dovetail_angle = dovetail_angle
        self.neck_width = neck_width
        self.base_thickness = base_thickness

        self.solid = self._build()

    def _build(self) -> Part.Shape:
        face = _dovetail_face(
            rail_width=self.rail_width,
            neck_width=self.neck_width,
            rail_height=self.rail_height,
            base_thickness=self.base_thickness,
        )
        return face.extrude(Vector(0.0, self.rail_length, 0.0))


class DovetailSlider:
    """Parametric dovetail slider: a rectangular block with a clearance-expanded
    dovetail void cut through it along Y.

    The slider is centred on X=0, placed at Y=0..slider_length, Z=0..rail_height+wall.

    Parameters
    ----------
    rail_width : float
        Total rail base width in X (mm) — must match the mating rail.
    rail_height : float
        Total rail height in Z (mm) — must match the mating rail.
    dovetail_angle : float
        Nominal dovetail angle (stored for reference; geometry uses neck_width).
    neck_width : float
        Narrowest neck width of the mating rail (mm).
    base_thickness : float
        Base rectangle height of the mating rail (mm).
    clearance : float
        Per-face clearance added to every non-base face of the void profile (mm).
        neck_width and rail_width are each expanded by 2*clearance;
        rail_height is expanded by clearance.
    slider_length : float
        Length of the slider block along Y (mm).  Should be <= rail_length.
    wall : float
        Minimum material wall around the void in X and above in Z (mm).
    """

    def __init__(
        self,
        rail_width: float = 20.0,
        rail_height: float = 10.0,
        dovetail_angle: float = 45.0,
        neck_width: float = 8.0,
        base_thickness: float = 3.0,
        clearance: float = 0.25,
        slider_length: float = 40.0,
        wall: float = 3.0,
    ):
        self.rail_width = rail_width
        self.rail_height = rail_height
        self.dovetail_angle = dovetail_angle
        self.neck_width = neck_width
        self.base_thickness = base_thickness
        self.clearance = clearance
        self.slider_length = slider_length
        self.wall = wall

        self.solid = self._build()

    def _build(self) -> Part.Shape:
        c = self.clearance
        w = self.wall
        rw = self.rail_width
        rh = self.rail_height
        sl = self.slider_length

        # Outer block centred on X=0
        block = Box(
            Vector(-(rw / 2.0 + w), 0.0, 0.0),
            Vector((rw / 2.0 + w), sl, rh + w),
        ).solid

        # Clearance void: every non-base dimension expanded by clearance
        #   rail_width  → rail_width  + 2*clearance  (one clearance per X side)
        #   neck_width  → neck_width  + 2*clearance
        #   rail_height → rail_height + clearance     (clearance at the top face)
        #   base_thickness unchanged  (the flat base floor stays at the same Z)
        void_face = _dovetail_face(
            rail_width=rw + 2.0 * c,
            neck_width=self.neck_width + 2.0 * c,
            rail_height=rh + c,
            base_thickness=self.base_thickness,
        )
        void_solid = void_face.extrude(Vector(0.0, sl, 0.0))

        return block.cut(void_solid)


class DovetailJoint:
    """Complete dovetail rail + slider pair, pre-positioned for visual preview.

    The slider is translated so its centre sits halfway along the rail in Y.

    Attributes
    ----------
    rail   : DovetailRail
        Rail solid at its natural position (Y=0..rail_length, X centred, Z=0).
    slider : DovetailSlider
        Slider solid translated to the mid-point of the rail.
    solid  : Part.Shape
        Both solids fused into a single preview shape.
    """

    def __init__(
        self,
        rail_length: float = 80.0,
        rail_width: float = 20.0,
        rail_height: float = 10.0,
        dovetail_angle: float = 45.0,
        neck_width: float = 8.0,
        clearance: float = 0.25,
        base_thickness: float = 3.0,
        slider_length: float = 40.0,
        wall: float = 3.0,
    ):
        self.rail = DovetailRail(
            rail_length=rail_length,
            rail_width=rail_width,
            rail_height=rail_height,
            dovetail_angle=dovetail_angle,
            neck_width=neck_width,
            base_thickness=base_thickness,
        )

        self.slider = DovetailSlider(
            rail_width=rail_width,
            rail_height=rail_height,
            dovetail_angle=dovetail_angle,
            neck_width=neck_width,
            base_thickness=base_thickness,
            clearance=clearance,
            slider_length=slider_length,
            wall=wall,
        )

        # Slide the slider to the midpoint of the rail along Y
        y_offset = (rail_length - slider_length) / 2.0
        self.slider.solid = move(self.slider.solid, Vector(0.0, y_offset, 0.0))

        self.solid = fuse_all([self.rail.solid, self.slider.solid])


if __name__ == "__main__":
    new_doc("DovetailDemo")
    dj = DovetailJoint()
    show_solid(dj.rail.solid, color=(0.8, 0.5, 0.2), name="Rail")
    show_solid(dj.slider.solid, color=(0.3, 0.6, 0.9), name="Slider")
    fit_view()
