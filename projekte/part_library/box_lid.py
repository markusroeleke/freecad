import FreeCAD, Part
from FreeCAD import Vector
import math
from src.freecad_lib import (
    Box,
    Cylinder,
    move,
    fuse_all,
    cut_all,
    new_doc,
    show_solid,
    fit_view,
)

# ---------------------------------------------------------------------------
# BoxLid
# ---------------------------------------------------------------------------


class BoxLid:
    """
    Snap-fit rectangular enclosure lid.

    Coordinate convention
    ---------------------
    Top surface at z = 0.
    Panel  : x in [-lid_length/2,  lid_length/2],
             y in [-lid_width/2,   lid_width/2],
             z in [-panel_thickness, 0].
    Skirt  : hangs below the panel,
             z in [-panel_thickness - skirt_height, -panel_thickness],
             wall thickness = skirt_thickness on each side.
    Snap tabs : small triangular-ramped bumps on the outer face of the skirt,
                pointing radially outward.  Bottom face is a lead-in ramp;
                top face (flat, horizontal) provides retention.

    Snap-tab placement
    ------------------
    Long sides (±Y faces, spanning lid_length in X) : snap_count tabs each.
    Short sides (±X faces, spanning lid_width  in Y) : 1 tab each.
    """

    def __init__(
        self,
        lid_length=100.0,
        lid_width=70.0,
        panel_thickness=2.0,
        skirt_height=6.0,
        skirt_thickness=1.8,
        snap_height=1.5,
        snap_count=2,
        snap_lead_angle=30,
        clearance=0.2,
    ):
        self.lid_length = lid_length
        self.lid_width = lid_width
        self.panel_thickness = panel_thickness
        self.skirt_height = skirt_height
        self.skirt_thickness = skirt_thickness
        self.snap_height = snap_height
        self.snap_count = snap_count
        self.snap_lead_angle = snap_lead_angle
        self.clearance = clearance

        self.solid = self._build()

    # ------------------------------------------------------------------

    def _build(self):
        ll = self.lid_length
        lw = self.lid_width
        pt = self.panel_thickness
        sh = self.skirt_height
        st = self.skirt_thickness
        snap_h = self.snap_height
        sc = self.snap_count
        lead_rad = math.radians(self.snap_lead_angle)

        # ------------------------------------------------------------------
        # 1. Top panel
        # ------------------------------------------------------------------
        panel = Box(
            Vector(-ll / 2, -lw / 2, -pt),
            Vector(ll / 2, lw / 2, 0.0),
        ).solid

        # ------------------------------------------------------------------
        # 2. Skirt — hollow rectangular frame hanging below the panel
        # ------------------------------------------------------------------
        z_skirt_bot = -pt - sh
        z_skirt_top = -pt
        eps = 0.1  # epsilon for clean boolean subtractions

        skirt_outer = Box(
            Vector(-ll / 2, -lw / 2, z_skirt_bot),
            Vector(ll / 2, lw / 2, z_skirt_top),
        ).solid

        # Inner void: extend just past the skirt bottom to guarantee a clean
        # cut; do NOT extend above z_skirt_top so the panel is not nicked.
        skirt_void = Box(
            Vector(-ll / 2 + st, -lw / 2 + st, z_skirt_bot - eps),
            Vector(ll / 2 - st, lw / 2 - st, z_skirt_top),
        ).solid

        skirt = skirt_outer.cut(skirt_void)

        # Merge panel and skirt (they share the face at z = -panel_thickness)
        body = panel.fuse(skirt)

        # ------------------------------------------------------------------
        # 3. Snap tabs
        # ------------------------------------------------------------------
        # Vertical centre of every tab sits mid-height of the skirt.
        z_tab_ctr = z_skirt_bot + sh / 2.0
        z_tab_bot = z_tab_ctr - snap_h / 2.0
        z_tab_top = z_tab_ctr + snap_h / 2.0

        tab_w = 8.0  # fixed tab width (perpendicular to face normal), mm

        # Ramp height: how far up the tab face the lead-in slope reaches.
        dz_ramp = snap_h * math.tan(lead_rad)
        # Cap so the ramp never consumes more than 85 % of the tab height,
        # preserving a meaningful flat retention ledge at the top.
        dz_ramp = min(dz_ramp, (z_tab_top - z_tab_bot) * 0.85)

        all_tabs = []

        # --- Long sides: ±Y faces (each face spans lid_length in X) ---------
        # Distribute snap_count tabs evenly, with a small margin from the
        # skirt corners.
        tab_margin = tab_w / 2.0 + 2.0
        if sc <= 1:
            x_positions = [0.0]
        else:
            x_span = ll - 2.0 * tab_margin
            x_positions = [-x_span / 2.0 + i * x_span / (sc - 1) for i in range(sc)]

        for xc in x_positions:
            all_tabs.append(
                self._tab_on_y_face(
                    xc,
                    lw / 2,
                    +1,
                    tab_w,
                    snap_h,
                    z_tab_bot,
                    z_tab_top,
                    dz_ramp,
                )
            )
            all_tabs.append(
                self._tab_on_y_face(
                    xc,
                    -lw / 2,
                    -1,
                    tab_w,
                    snap_h,
                    z_tab_bot,
                    z_tab_top,
                    dz_ramp,
                )
            )

        # --- Short sides: ±X faces (each face spans lid_width in Y) ---------
        # One tab per face, centred at Y = 0.
        for x_face, sign in [(ll / 2, +1), (-ll / 2, -1)]:
            all_tabs.append(
                self._tab_on_x_face(
                    0.0,
                    x_face,
                    sign,
                    tab_w,
                    snap_h,
                    z_tab_bot,
                    z_tab_top,
                    dz_ramp,
                )
            )

        if all_tabs:
            body = fuse_all([body] + all_tabs)

        return body

    # ------------------------------------------------------------------
    # Snap-tab geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _triangular_wedge(va, vb, vc, extrude_vec):
        """
        Build a triangular prism by extruding triangle (va, vb, vc) along
        extrude_vec.  All three vertices must be coplanar (same component
        perpendicular to extrude_vec).  Returns a Part.Shape solid.
        """
        e0 = Part.LineSegment(va, vb).toShape()
        e1 = Part.LineSegment(vb, vc).toShape()
        e2 = Part.LineSegment(vc, va).toShape()
        wire = Part.Wire([e0, e1, e2])
        face = Part.Face(wire)
        return face.extrude(extrude_vec)

    def _tab_on_y_face(
        self,
        xc,
        y_face,
        sign,
        tab_w,
        snap_h,
        z_bot,
        z_top,
        dz_ramp,
    ):
        """
        Snap tab on a ±Y skirt face.

        Parameters
        ----------
        xc     : X centre of the tab.
        y_face : Y coordinate of the skirt outer face (±lw/2).
        sign   : +1 for +Y face (tab protrudes in +Y); -1 for -Y face.
        """
        y_base = y_face  # junction with skirt outer wall
        y_outer = y_face + sign * snap_h  # tab outer edge

        y_lo = min(y_base, y_outer)
        y_hi = max(y_base, y_outer)

        # Tab box
        tab_box = Box(
            Vector(xc - tab_w / 2, y_lo, z_bot),
            Vector(xc + tab_w / 2, y_hi, z_top),
        ).solid

        # Ramp wedge — cross-section is a triangle in the YZ plane,
        # extruded along X (wider than the tab to guarantee a full cut).
        #
        # Triangle (at x = x0, in the YZ plane):
        #   A = (y_base,  z_bot)           inner-bottom (at skirt face)
        #   B = (y_outer, z_bot)           outer-bottom (leading tip)
        #   C = (y_base,  z_bot+dz_ramp)  inner top of ramp
        #
        # After the cut the tab has:
        #   - a sloped bottom face rising from (y_outer, z_bot) to
        #     (y_base, z_bot+dz_ramp)  → lead-in ramp
        #   - a flat horizontal top face at z_top              → retention ledge
        cut_eps = 1.0
        x0 = xc - tab_w / 2 - cut_eps
        dx = tab_w + 2.0 * cut_eps

        va = Vector(x0, y_base, z_bot)
        vb = Vector(x0, y_outer, z_bot)
        vc = Vector(x0, y_base, z_bot + dz_ramp)

        wedge = self._triangular_wedge(va, vb, vc, Vector(dx, 0.0, 0.0))
        return tab_box.cut(wedge)

    def _tab_on_x_face(
        self,
        yc,
        x_face,
        sign,
        tab_w,
        snap_h,
        z_bot,
        z_top,
        dz_ramp,
    ):
        """
        Snap tab on a ±X skirt face.

        Parameters
        ----------
        yc     : Y centre of the tab.
        x_face : X coordinate of the skirt outer face (±ll/2).
        sign   : +1 for +X face (tab protrudes in +X); -1 for -X face.
        """
        x_base = x_face
        x_outer = x_face + sign * snap_h

        x_lo = min(x_base, x_outer)
        x_hi = max(x_base, x_outer)

        # Tab box
        tab_box = Box(
            Vector(x_lo, yc - tab_w / 2, z_bot),
            Vector(x_hi, yc + tab_w / 2, z_top),
        ).solid

        # Ramp wedge — cross-section is a triangle in the XZ plane,
        # extruded along Y.
        #
        # Triangle (at y = y0, in the XZ plane):
        #   A = (x_base,  z_bot)           inner-bottom
        #   B = (x_outer, z_bot)           outer-bottom (leading tip)
        #   C = (x_base,  z_bot+dz_ramp)  inner top of ramp
        cut_eps = 1.0
        y0 = yc - tab_w / 2 - cut_eps
        dy = tab_w + 2.0 * cut_eps

        va = Vector(x_base, y0, z_bot)
        vb = Vector(x_outer, y0, z_bot)
        vc = Vector(x_base, y0, z_bot + dz_ramp)

        wedge = self._triangular_wedge(va, vb, vc, Vector(0.0, dy, 0.0))
        return tab_box.cut(wedge)


# ---------------------------------------------------------------------------
# EnclosureBox
# ---------------------------------------------------------------------------


class EnclosureBox:
    """
    Simple open-top rectangular enclosure body for test-fitting a BoxLid.

    Origin / coordinate convention
    -------------------------------
    Top opening flush with z = 0.  Box body extends downward:
        z in [-(inner_height + wall), 0].
    Outer footprint: (inner_length + 2·wall) × (inner_width + 2·wall).
    Floor thickness  = wall.
    Side-wall thickness = wall.
    Top edge is plain (no ledge); the BoxLid snap tabs bear against the
    box top inner rim.

    The lid_interface_height parameter documents the depth of engagement
    between the lid skirt and the box interior (informational only; no
    special geometry is added).
    """

    def __init__(
        self,
        inner_length=100.0,
        inner_width=70.0,
        inner_height=50.0,
        wall=2.5,
        lid_interface_height=6,
    ):
        self.inner_length = inner_length
        self.inner_width = inner_width
        self.inner_height = inner_height
        self.wall = wall
        self.lid_interface_height = lid_interface_height

        self.solid = self._build()

    def _build(self):
        il = self.inner_length
        iw = self.inner_width
        ih = self.inner_height
        w = self.wall

        ol = il + 2.0 * w  # outer length
        ow = iw + 2.0 * w  # outer width

        eps = 0.1  # small overshoot for clean open-top cut

        # Full outer block — top face at z = 0, bottom at z = -(ih + w)
        outer = Box(
            Vector(-ol / 2, -ow / 2, -(ih + w)),
            Vector(ol / 2, ow / 2, 0.0),
        ).solid

        # Inner void — open top: void reaches z = +eps so the top face of
        # the inner area is fully removed, leaving the box open.
        # Floor: from z = -(ih + w) to z = -ih, thickness = w.
        inner_void = Box(
            Vector(-il / 2, -iw / 2, -ih),
            Vector(il / 2, iw / 2, eps),
        ).solid

        return outer.cut(inner_void)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    new_doc("BoxLidDemo")
    lid = BoxLid()
    box = EnclosureBox()
    show_solid(lid.solid, color=(0.3, 0.7, 0.9), transparancy=20, name="Lid")
    show_solid(move(box.solid, Vector(120, 0, 0)), color=(0.6, 0.6, 0.6), name="Box")
    fit_view()
