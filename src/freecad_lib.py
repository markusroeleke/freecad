import FreeCAD, Part, FreeCADGui, Mesh
from FreeCAD import Vector
from typing import List
import functools
import math
from typing import Literal

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)


def new_doc(doc_name):

    FreeCAD.newDocument(doc_name)
    FreeCADGui.runCommand("Std_DrawStyle", 6)  # shaded wireframe


def fit_view():

    FreeCADGui.activeDocument().activeView().viewIsometric()
    FreeCADGui.SendMsgToActiveView("ViewFit")


def show(part, transparancy=50, color=(0.5, 0.5, 0.5), name="body"):

    bodyFeature = Part.show(part.solid, name)
    bodyFeature.ViewObject.Transparency = transparancy
    bodyFeature.ViewObject.ShapeColor = color

    return bodyFeature


def show_solid(solid, transparancy=50, color=(0.5, 0.5, 0.5), name="body"):
    """Like show(), but accepts a raw Part.Shape solid directly.

    Useful after boolean operations (body.cut / body.fuse) which return a plain
    Part solid rather than a freecad_lib object with a .solid attribute.
    """
    bodyFeature = Part.show(solid, name)
    bodyFeature.ViewObject.Transparency = transparancy
    bodyFeature.ViewObject.ShapeColor = color
    return bodyFeature


def export(doc, obj):
    Mesh.export(
        [FreeCAD.getDocument(doc).getObject(obj)],
        f"/Users/Markus/Documents/Projekte/FreeCAD/stl/{obj}.stl",
    )


############################################################################################################
# DIN / ISO size konstants

NUT_MAP = {
    "M1": {"H": 0.8, "AF": 2.5},
    "M1.2": {"H": 1, "AF": 3},
    "M1.4": {"H": 1.2, "AF": 3},
    "M1.6": {"H": 1.3, "AF": 3.2},
    "M1.7": {"H": 1.4, "AF": 3.5},
    "M2": {"H": 1.6, "AF": 4},
    "M2.3": {"H": 1.8, "AF": 4.5},
    "M2.5": {"H": 2, "AF": 5},
    "M2.6": {"H": 2, "AF": 5},
    "M3": {"H": 2.4, "AF": 5.5},
    "M3.5": {"H": 2.8, "AF": 6},
    "M4": {"H": 3.2, "AF": 7},
    "M5": {"H": 4, "AF": 8},
    "M6": {"H": 5, "AF": 10},
    "M7": {"H": 5.5, "AF": 11},
    "M8": {"H": 6.5, "AF": 13},
    "M10": {"H": 8, "AF": 17},
}

NUT_SIZES = Literal[
    "M1",
    "M1.2",
    "M1.4",
    "M1.6",
    "M1.7",
    "M2",
    "M2.3",
    "M2.5",
    "M2.6",
    "M3",
    "M3.5",
    "M4",
    "M5",
    "M6",
    "M7",
    "M8",
    "M10",
]

SCREW_MAP = {
    "M1.4": {"dK": 2.6, "d": 1.4, "k": 1.3},
    "M1.6": {"dK": 3, "d": 1.6, "k": 1.5},
    "M2": {"dK": 3.8, "d": 2, "k": 1.5},
    "M2.5": {"dK": 4.5, "d": 2.5, "k": 2},
    "M3": {"dK": 5.5, "d": 3, "k": 2.5},
    "M4": {"dK": 7, "d": 4, "k": 3},
    "M5": {"dK": 8.5, "d": 5, "k": 4},
    "M6": {"dK": 10, "d": 6, "k": 5},
    "M8": {"dK": 13, "d": 8, "k": 6},
    "M10": {"dK": 16, "d": 10, "k": 8},
}
SCREW_SIZES = Literal[
    "M1.4",
    "M1.6",
    "M2",
    "M2.5",
    "M3",
    "M3.5",
    "M4",
    "M5",
    "M6",
    "M8",
    "M10",
]

# DIN 7991 / ISO 10642 flat-head (countersunk) socket-cap screws
COUNTERSINK_MAP = {
    "M2": {"dK": 3.8, "d": 2.4, "k": 1.3},
    "M2.5": {"dK": 4.7, "d": 2.9, "k": 1.6},
    "M3": {"dK": 5.6, "d": 3.4, "k": 1.7},
    "M4": {"dK": 7.5, "d": 4.5, "k": 2.3},
    "M5": {"dK": 9.4, "d": 5.5, "k": 2.8},
    "M6": {"dK": 11.0, "d": 6.6, "k": 3.3},
    "M8": {"dK": 15.0, "d": 9.0, "k": 4.4},
    "M10": {"dK": 18.0, "d": 11.0, "k": 5.5},
}

# Standard deep-groove ball bearings (bore mm, OD mm, width mm)
BEARING_MAP = {
    "608": {"bore": 8, "OD": 22, "width": 7},
    "624": {"bore": 4, "OD": 13, "width": 5},
    "625": {"bore": 5, "OD": 16, "width": 5},
    "626": {"bore": 6, "OD": 19, "width": 6},
    "688": {"bore": 8, "OD": 16, "width": 4},
    "6200": {"bore": 10, "OD": 30, "width": 9},
    "6201": {"bore": 12, "OD": 32, "width": 10},
    "6202": {"bore": 15, "OD": 35, "width": 11},
    "6203": {"bore": 17, "OD": 40, "width": 12},
    "6204": {"bore": 20, "OD": 47, "width": 14},
}

# Heat-set threaded brass inserts (Ruthex / CNC Kitchen standard pocket sizes)
HEAT_SET_INSERT_MAP = {
    "M2": {"pocket_d": 3.6, "pocket_l": 3.4},
    "M3": {"pocket_d": 4.7, "pocket_l": 6.0},
    "M4": {"pocket_d": 5.7, "pocket_l": 8.5},
    "M5": {"pocket_d": 7.0, "pocket_l": 10.0},
}

# Neodymium disc / cylinder magnets (diameter x height in mm)
MAGNET_SIZES = {
    "5x1": {"D": 5, "H": 1},
    "5x2": {"D": 5, "H": 2},
    "6x2": {"D": 6, "H": 2},
    "8x2": {"D": 8, "H": 2},
    "10x2": {"D": 10, "H": 2},
    "10x3": {"D": 10, "H": 3},
    "12x2": {"D": 12, "H": 2},
    "12x3": {"D": 12, "H": 3},
    "20x3": {"D": 20, "H": 3},
}


class GeneralTolerances:
    #                         0.5_to_3  3_to_6  6_to_30  30_to_120  120_to_400  400_to_1000  1000_to_2000  2000_to_4000  4000_to_8000
    # f (fein) 	siehe unten   ± 0.05   ± 0.05   ± 0.10    ± 0.15      ± 0.2       ± 0.3         ± 0.5            -             -
    # m (mittel)              ± 0.10   ± 0.10   ± 0.20    ± 0.30      ± 0.5       ± 0.8         ± 1.2            ± 2            ± 3
    # c (grob)                ± 0.20   ± 0.30   ± 0.50    ± 0.80      ± 1.2       ± 2.0         ± 3.0            ± 4            ± 5
    # v (sehr grob)                    ± 0.50   ± 1.00    ± 1.50      ± 2.5       ± 4.0         ± 6.0            ± 8            ± 12
    def __init__(self) -> None:
        self.TOLERANCES = {
            "0.5_to_3": {
                "f": 0.05,
                "m": 0.10,
                "c": 0.20,
                "v": 0.35,
            },
            "3_to_6": {
                "f": 0.05,
                "m": 0.10,
                "c": 0.30,
                "v": 0.50,
            },
            "6_to_30": {
                "f": 0.10,
                "m": 0.20,
                "c": 0.50,
                "v": 1.00,
            },
            "30_to_120": {
                "f": 0.15,
                "m": 0.30,
                "c": 0.80,
                "v": 1.50,
            },
            "120_to_400": {
                "f": 0.2,
                "m": 0.5,
                "c": 1.2,
                "v": 2.5,
            },
            "400_to_1000": {
                "f": 0.3,
                "m": 0.8,
                "c": 2.0,
                "v": 4.0,
            },
            "1000_to_2000": {
                "f": 0.5,
                "m": 1.2,
                "c": 3.0,
                "v": 6.0,
            },
            "2000_to_4000": {
                "f": 2.0,
                "m": 2.0,
                "c": 4.0,
                "v": 8.0,
            },
            "4000_to_8000": {
                "f": 2.5,
                "m": 3.0,
                "c": 5.0,
                "v": 12.0,
            },
        }

    def get_tolerance(self, length, tolerance_class: Literal["f", "m", "c", "v"] = "m"):

        # get absolut value
        length = abs(length)
        # get tolerance, depending on value
        if length <= 3:
            tolerance = self.TOLERANCES["0.5_to_3"][tolerance_class]
        elif 3 < length <= 6:
            tolerance = self.TOLERANCES["3_to_6"][tolerance_class]

        elif 6 < length <= 30:
            tolerance = self.TOLERANCES["6_to_30"][tolerance_class]

        elif 30 < length <= 120:
            tolerance = self.TOLERANCES["30_to_120"][tolerance_class]

        elif 120 < length <= 400:
            tolerance = self.TOLERANCES["120_to_400"][tolerance_class]

        elif 400 < length <= 1000:
            tolerance = self.TOLERANCES["400_to_1000"][tolerance_class]

        elif 1000 < length <= 2000:
            tolerance = self.TOLERANCES["1000_to_2000"][tolerance_class]

        elif 2000 < length <= 4000:
            tolerance = self.TOLERANCES["2000_to_4000"][tolerance_class]

        elif 4000 < length:
            tolerance = self.TOLERANCES["4000_to_8000"][tolerance_class]
        return tolerance


###############################################################################
# classes


class Flat:
    def __init__(
        self, vertices: List[Vector], joints: List[Vector] = [], normal=Vector(0, 0, 0)
    ):
        self.v = vertices
        # print(vertices)
        # print(joints)

        self.joints = joints
        self.normal = normal
        self.draw()

    def draw(self):
        bc = 0.55228474983079  # bezier curve coefficient (https://spencermortensen.com/articles/bezier-circle/)
        edges = []
        if len(self.joints) < len(self.v):
            for k in range(len(self.joints), len(self.v)):
                self.joints.append(Vector(0, 0, 0))
        if self.v[0] == self.v[-1]:
            vector = self.v[-1] - self.v[-2]
            vertexC = self.v[-1] + (
                self.joints[-1].dot(vector) / vector.Length * vector.normalize()
            )
            vertexD = vertexC + (bc * (self.v[-1] - vertexC))
        for k in range(1, len(self.v)):
            vector = self.v[k] - self.v[k - 1]
            vertexB = self.v[k - 1] + (
                self.joints[k - 1].dot(vector) / vector.Length * vector.normalize()
            )
            vertexA = vertexB + (bc * (self.v[k - 1] - vertexB))
            if not self.joints[k - 1].isEqual(Vector(0, 0, 0), 0):
                curve = Part.BezierCurve()
                curve.setPoles([vertexC, vertexD, vertexA, vertexB])
                edges.append(curve.toShape())
            vertexC = self.v[k] + (
                self.joints[k].dot(vector) / vector.Length * vector.normalize()
            )
            if not vertexB.isEqual(vertexC, 0):
                edges.append(Part.LineSegment(vertexB, vertexC).toShape())
            vertexD = vertexC + (bc * (self.v[k] - vertexC))
        # print(edges)
        self.wire = Part.Wire(edges)
        # print(self.wire)
        self.face = Part.Face(self.wire)
        if self.normal.isEqual(Vector(0, 0, 0), 0):
            self.normal = self.face.normalAt(0, 0)


# Vectors (v) : (x), (y), (2)
class Box:
    def __init__(self, vWSD: Vector, vENU: Vector, joints=[]):

        self.vWSD = vWSD
        self.vENU = vENU
        self.joints = joints
        if len(self.joints) == 1:
            self.joints.append(Vector(-self.joints[0].x, self.joints[0].y, 0))
            self.joints.append(Vector(-self.joints[0].x, -self.joints[0].y, 0))
            self.joints.append(Vector(self.joints[0].x, -self.joints[0].y, 0))
        if len(self.joints) == 4:
            self.joints.append(self.joints[0])
        self.vESD = Vector(self.vENU.x, self.vWSD.y, self.vWSD.z)
        self.vEND = Vector(self.vENU.x, self.vENU.y, self.vWSD.z)
        self.vWND = Vector(self.vWSD.x, self.vENU.y, self.vWSD.z)
        self.vWNU = Vector(self.vWSD.x, self.vENU.y, self.vENU.z)
        self.vWSU = Vector(self.vWSD.x, self.vWSD.y, self.vENU.z)
        self.vESU = Vector(self.vENU.x, self.vWSD.y, self.vENU.z)
        self.w = self.vWSD.x
        self.e = self.vENU.x
        self.s = self.vWSD.y
        self.n = self.vENU.y
        self.d = self.vWSD.z
        self.u = self.vENU.z
        self.c = (self.vWSD.x + self.vENU.x) / 2
        self.m = (self.vWSD.y + self.vENU.y) / 2
        self.g = (self.vWSD.z + self.vENU.z) / 2
        self.l = abs(self.vENU.x - self.vWSD.x)
        self.b = abs(self.vENU.y - self.vWSD.y)
        self.h = abs(self.vENU.z - self.vWSD.z)
        self.vCMG = Vector(self.c, self.m, self.g)

        # create edges
        flat = Flat(
            [self.vWSD, self.vESD, self.vEND, self.vWND, self.vWSD], self.joints
        )
        self.solid = flat.face.extrude(Vector(0, 0, self.vENU.z - self.vWSD.z))


class Polygon:
    def __init__(self, center: Vector, radius, normal, sides=1, twist=0):
        self.center = center
        self.radius = radius
        self.normal = normal
        self.sides = sides
        self.twist = twist

        circle = Part.Circle(self.center, self.normal, self.radius)
        circle.rotate(FreeCAD.Placement(self.center, self.normal, self.twist))
        self.v = [self.center + (circle.XAxis * self.radius)]
        self.j = []
        self.wire = Part.Wire(circle.toShape())
        if self.sides > 1:
            self.v = circle.discretize(Number=self.sides + 1)
            self.wire = Flat(self.v).wire
        for k in self.v:
            self.j.append(Vector(0, 0, 0))
        self.face = Part.Face(self.wire)


class Polyhedron:
    def __init__(self, polygon1: Polygon, polygon2: Polygon):
        self.polygon1 = polygon1
        self.polygon2 = polygon2
        self.h = polygon2.center.z - polygon1.center.z
        self.wire1 = polygon1.wire
        self.wire2 = polygon2.wire
        self.solid = Part.makeLoft([self.wire1, self.wire2], True, True)


class SolidText:
    def __init__(
        self,
        text,
        position=Vector(0, 0, 0),
        height=-1,
        txt_height=6,
        spacing=0.5,
        font="TC_LaserSans.TTF",
    ):
        self.position = position
        self.height = height
        self.txt_height = txt_height
        self.text = text
        fontdir = "/Users/Markus/Documents/Projekte/FreeCAD/fonts/"
        wire_lists = Part.makeWireString(text, fontdir, font, self.txt_height, spacing)
        self.faces = [Part.Face(wire) for wires in wire_lists for wire in wires]

        # print(self.faces)
        # self.face = fusePartList([fusePartList() for c in self.wire_lists])
        def fusePartList(l):
            return functools.reduce(lambda a, b: a.fuse(b), l)

        self.solids = [face.extrude(Vector(0, 0, self.height)) for face in self.faces]
        self.solid = fusePartList(self.solids)
        self.solid.Placement = FreeCAD.Placement(
            self.position, FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0)
        )


class Quader(Box):
    def __init__(self, name, length, width, height, position=Vector(0, 0, 0)) -> None:
        self.length = length
        self.width = width
        self.height = height
        self.position = position
        self.name = name

        # draw the box
        Box.__init__(
            self,
            Vector(-width / 2, -length / 2, 0),
            Vector(width / 2, length / 2, height),
        )


class Cylinder(Polyhedron):
    def __init__(
        self,
        name,
        diameter,
        height,
        position=Vector(0, 0, 0),
        normal=Vector(0, 0, 1),
    ):
        self.name = name
        self.height = height
        self.diameter = diameter
        polygon1 = Polygon(position, diameter / 2, normal, sides=1)
        polygon2 = Polygon(
            position + self.height * normal,
            diameter / 2,
            normal,
            sides=1,
        )
        Polyhedron.__init__(self, polygon1, polygon2)


class Nut(Polyhedron):
    def __init__(
        self,
        name,
        size: NUT_SIZES,
        position=Vector(0, 0, 0),
        normal=Vector(0, 0, 1),
        screw_type: Literal["normal", "slide"] = "normal",
    ):
        self.name = name
        self.position = position
        self.normal = normal

        # AF = radius * sqrt(3)
        self.nut_height = NUT_MAP[size]["H"]
        self.nut_across_sides = NUT_MAP[size]["AF"]
        self.nut_radius = NUT_MAP[size]["AF"] / math.sqrt(3)

        self.draw(screw_type)

    def draw(self, screw_type):

        polygon1 = Polygon(
            self.position,
            self.nut_radius,
            self.normal,
            sides=6,
        )
        polygon2 = Polygon(
            self.position + self.nut_height * self.normal,
            self.nut_radius,
            self.normal,
            sides=6,
        )
        self.body = Polyhedron(polygon1, polygon2)
        self.solid = self.body.solid
        clearance_height = self.nut_height * 10
        tolerances = GeneralTolerances()
        clearance_radius = self.nut_radius + tolerances.get_tolerance(
            self.nut_radius, "c"
        )

        if screw_type == "normal":
            polygon1 = Polygon(
                self.position,
                clearance_radius,
                self.normal,
                sides=6,
            )
            polygon2 = Polygon(
                self.position + clearance_height * self.normal,
                clearance_radius,
                self.normal,
                sides=6,
            )
            self.clearance = Polyhedron(polygon1, polygon2)
            self.solid = self.solid.fuse(self.clearance.solid)
        elif screw_type == "slide":

            # slide clearance

            slide_clearance_width = self.nut_across_sides + tolerances.get_tolerance(
                self.nut_across_sides, "c"
            )
            slide_clearance_height = self.nut_height + tolerances.get_tolerance(
                self.nut_height, "v"
            )

            polygon1 = Polygon(
                self.position,
                clearance_radius,
                self.normal,
                sides=6,
            )
            polygon2 = Polygon(
                self.position + slide_clearance_height * self.normal,
                clearance_radius,
                self.normal,
                sides=6,
            )
            self.head_clearance = Polyhedron(polygon1, polygon2)
            self.solid = self.solid.fuse(self.head_clearance.solid)

            if self.normal == Vector(0, 0, 1):
                vec1 = Vector(0, -slide_clearance_width / 2, 0)
                vec2 = Vector(
                    clearance_height, slide_clearance_width / 2, slide_clearance_height
                )
            elif self.normal == Vector(0, 1, 0):
                vec1 = Vector(-slide_clearance_width / 2, 0, 0)
                vec2 = Vector(
                    slide_clearance_width / 2, slide_clearance_height, -clearance_height
                )
            elif self.normal == Vector(1, 0, 0):
                vec1 = Vector(0, -slide_clearance_width / 2, 0)
                vec2 = Vector(
                    slide_clearance_height, slide_clearance_width / 2, -clearance_height
                )
            self.slide_clearance = Box(
                vec1 + self.position,
                vec2 + self.position,
            )
            self.solid = self.solid.fuse(self.slide_clearance.solid)


class Screw(Polyhedron):
    def __init__(
        self,
        name,
        size: SCREW_SIZES,
        thread_length,
        position=Vector(0, 0, 0),
        normal=Vector(0, 0, 1),
        tolerance_class="m",
    ):
        self.name = name
        self.position = position
        self.normal = normal

        self.head_diameter = SCREW_MAP[size]["dK"]
        self.head_height = SCREW_MAP[size]["k"]
        self.thread_length = thread_length
        self.thread_diameter = SCREW_MAP[size]["d"]

        tolerances = GeneralTolerances()

        self.clearance_head_diameter = self.head_diameter + tolerances.get_tolerance(
            self.head_diameter, "v"
        )
        self.clearance_head_height = self.head_height * 10
        self.clearance_thread_length = self.thread_length + tolerances.get_tolerance(
            self.thread_length, "v"
        )
        self.clearance_thread_diameter = (
            self.thread_diameter + tolerances.get_tolerance(self.thread_diameter, "v")
        )

        polygon1 = Polygon(self.position, self.clearance_head_diameter / 2, self.normal)
        polygon2 = Polygon(
            self.position + self.clearance_head_height * self.normal,
            self.clearance_head_diameter / 2,
            self.normal,
        )
        polygon3 = Polygon(
            self.position + self.clearance_head_height * self.normal,
            self.clearance_thread_diameter / 2,
            self.normal,
        )

        polygon4 = Polygon(
            self.position - self.clearance_thread_length * self.normal,
            self.clearance_thread_diameter / 2,
            self.normal,
        )
        self.head_clearance = Polyhedron(polygon1, polygon2)
        self.thread_clearance = Polyhedron(polygon3, polygon4)

        self.solid = self.head_clearance.solid.fuse(self.thread_clearance.solid)


###############################################################################
# Transformation Functions


def move(solid, vector: Vector):
    """Translate/move a solid by a vector offset. Returns a new solid."""
    result = solid.copy()
    result.translate(vector)
    return result


def translate(solid, vector: Vector):
    """Alias for move(). Translate a solid by a vector offset. Returns a new solid."""
    return move(solid, vector)


def rotate(
    solid,
    angle_deg: float,
    axis: Vector = Vector(0, 0, 1),
    center: Vector = Vector(0, 0, 0),
):
    """Rotate a solid around *axis* by *angle_deg* degrees around *center*. Returns a new solid."""
    result = solid.copy()
    result.rotate(center, axis, angle_deg)
    return result


def mirror(
    solid,
    plane_normal: Vector = Vector(1, 0, 0),
    plane_origin: Vector = Vector(0, 0, 0),
):
    """Mirror a solid across a plane defined by *plane_origin* and *plane_normal*. Returns a new solid."""
    return solid.mirror(plane_origin, plane_normal)


def mirror_x(solid, x: float = 0):
    """Mirror a solid across the YZ plane at x=*x*. Returns a new solid."""
    return solid.mirror(Vector(x, 0, 0), Vector(1, 0, 0))


def mirror_y(solid, y: float = 0):
    """Mirror a solid across the XZ plane at y=*y*. Returns a new solid."""
    return solid.mirror(Vector(0, y, 0), Vector(0, 1, 0))


def mirror_z(solid, z: float = 0):
    """Mirror a solid across the XY plane at z=*z*. Returns a new solid."""
    return solid.mirror(Vector(0, 0, z), Vector(0, 0, 1))


def scale(solid, factor: float):
    """Scale a solid uniformly from the origin by *factor*. Returns a new solid."""
    mat = FreeCAD.Matrix()
    mat.scale(factor, factor, factor)
    return solid.transformGeometry(mat)


###############################################################################
# Boolean Utilities


def fuse_all(solids):
    """Fuse a list of solids into one combined solid."""
    return functools.reduce(lambda a, b: a.fuse(b), solids)


def cut_all(base, cutters):
    """Cut every solid in *cutters* from *base*. Returns one solid."""
    return functools.reduce(lambda a, b: a.cut(b), [base] + list(cutters))


###############################################################################
# Pattern / Array Utilities


def array_linear(solid, direction: Vector, count: int, spacing: float):
    """Create a linear array of *count* copies of *solid*, spaced *spacing* mm apart
    along *direction*. The original (i=0) is included. Returns one fused solid."""
    copies = [solid]
    unit = direction.normalize()
    for i in range(1, count):
        copy = solid.copy()
        copy.translate(unit * (spacing * i))
        copies.append(copy)
    return fuse_all(copies)


def array_polar(
    solid, count: int, axis: Vector = Vector(0, 0, 1), center: Vector = Vector(0, 0, 0)
):
    """Create a polar/circular array of *count* copies of *solid* evenly distributed
    around *axis* passing through *center*. The original (angle=0) is included.
    Returns one fused solid."""
    copies = [solid]
    angle_step = 360.0 / count
    for i in range(1, count):
        copy = solid.copy()
        copy.rotate(center, axis, angle_step * i)
        copies.append(copy)
    return fuse_all(copies)


###############################################################################
# Additional Shape Classes


class Sphere:
    """Sphere primitive.

    Args:
        radius:   sphere radius in mm.
        position: center of the sphere.
    """

    def __init__(self, radius: float, position: Vector = Vector(0, 0, 0)):
        self.radius = radius
        self.position = position
        self.solid = Part.makeSphere(radius, position)


class Cone:
    """Cone or truncated cone.

    Args:
        name:     identifier string.
        radius1:  base radius at *position* (mm).
        radius2:  top radius at position + height * normal (mm); use 0 for a sharp tip.
        height:   height along *normal* (mm).
        position: base center point.
        normal:   axis direction (default Z+).
    """

    def __init__(
        self,
        name: str,
        radius1: float,
        radius2: float,
        height: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
    ):
        self.name = name
        self.radius1 = radius1
        self.radius2 = radius2
        self.height = height
        self.position = position
        self.normal = normal
        self.solid = Part.makeCone(radius1, radius2, height, position, normal)


class Torus:
    """Torus (donut) shape.

    Args:
        radius_major: distance from torus center to the center of the tube (mm).
        radius_minor: radius of the tube cross-section (mm).
        position:     center of the torus.
        normal:       axis direction (default Z+).
    """

    def __init__(
        self,
        radius_major: float,
        radius_minor: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
    ):
        self.radius_major = radius_major
        self.radius_minor = radius_minor
        self.position = position
        self.normal = normal
        self.solid = Part.makeTorus(radius_major, radius_minor, position, normal)


class Bullet:
    """Cylinder with a hemispherical cap on one end.

    The flat base is at *position*; the rounded tip points along *normal*.
    If *height* <= *radius* the shape degenerates to a hemisphere only.

    Args:
        name:     identifier string.
        diameter: diameter of both the cylinder and the hemisphere (mm).
        height:   total length from flat base to tip of hemisphere (mm).
        position: center of the flat base circle.
        normal:   axis direction (default Z+).
    """

    def __init__(
        self,
        name: str,
        diameter: float,
        height: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
    ):
        self.name = name
        self.diameter = diameter
        self.height = height
        self.radius = diameter / 2
        self.position = position
        self.normal = normal

        r = self.radius
        cyl_height = max(0.0, height - r)
        hemi_pos = position + cyl_height * normal
        # angle1=0 → angle2=90 gives the upper hemisphere along *normal*
        hemi = Part.makeSphere(r, hemi_pos, normal, 0, 90, 360)
        if cyl_height > 0:
            cyl = Part.makeCylinder(r, cyl_height, position, normal)
            self.solid = cyl.fuse(hemi)
        else:
            self.solid = hemi


class Tube:
    """Hollow cylinder (pipe / tube).

    Args:
        name:            identifier string.
        outer_diameter:  outer diameter (mm).
        wall_thickness:  wall thickness (mm); inner diameter = outer - 2 * wall.
        height:          length of the tube (mm).
        position:        center of the bottom face.
        normal:          axis direction (default Z+).
    """

    def __init__(
        self,
        name: str,
        outer_diameter: float,
        wall_thickness: float,
        height: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
    ):
        self.name = name
        self.outer_diameter = outer_diameter
        self.wall_thickness = wall_thickness
        self.inner_diameter = outer_diameter - 2 * wall_thickness
        self.height = height
        self.position = position
        self.normal = normal
        outer = Part.makeCylinder(outer_diameter / 2, height, position, normal)
        inner = Part.makeCylinder(self.inner_diameter / 2, height, position, normal)
        self.solid = outer.cut(inner)


class Wedge:
    """Triangular prism (wedge).

    The isoceles triangle base lies in the XZ plane at *position* and is
    extruded along the Y axis by *width*.

    Args:
        name:     identifier string.
        length:   base length of the triangle (X direction, mm).
        width:    extrusion depth (Y direction, mm).
        height:   height of the triangle / wedge (Z direction, mm).
        position: lower-left corner of the triangle (West, South, Down).
    """

    def __init__(
        self,
        name: str,
        length: float,
        width: float,
        height: float,
        position: Vector = Vector(0, 0, 0),
    ):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.position = position
        px, py, pz = position.x, position.y, position.z
        v1 = Vector(px, py, pz)
        v2 = Vector(px + length, py, pz)
        v3 = Vector(px + length / 2, py, pz + height)
        flat = Flat([v1, v2, v3, v1])
        self.solid = flat.face.extrude(Vector(0, width, 0))


class Ellipsoid:
    """Ellipsoid (axis-aligned scaled sphere).

    A unit sphere is scaled non-uniformly to form an ellipsoid with
    semi-axes *rx*, *ry*, *rz*.

    Args:
        rx:       semi-axis along X (mm).
        ry:       semi-axis along Y (mm).
        rz:       semi-axis along Z (mm).
        position: center of the ellipsoid.
    """

    def __init__(
        self,
        rx: float,
        ry: float,
        rz: float,
        position: Vector = Vector(0, 0, 0),
    ):
        self.rx = rx
        self.ry = ry
        self.rz = rz
        self.position = position
        sphere = Part.makeSphere(1.0)
        mat = FreeCAD.Matrix()
        mat.scale(rx, ry, rz)
        self.solid = sphere.transformGeometry(mat)
        if not position.isEqual(Vector(0, 0, 0), 1e-7):
            self.solid.translate(position)


###############################################################################
# 3D-Print Utility Shapes


class Capsule:
    """Cylinder with hemispherical caps on both ends (pill / capsule shape).

    Total height includes both half-spheres, so the cylindrical section has
    length = height - diameter.  If height <= diameter the result is a full
    sphere.

    Args:
        name:     identifier string.
        diameter: diameter of the capsule (mm).
        height:   total height from bottom pole to top pole (mm).
        position: center of the bottom hemisphere pole (z=0 of the capsule).
        normal:   axis direction (default Z+).
    """

    def __init__(
        self,
        name: str,
        diameter: float,
        height: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
    ):
        self.name = name
        self.diameter = diameter
        r = diameter / 2
        self.height = max(height, diameter)
        self.position = position
        self.normal = normal

        cyl_length = self.height - 2 * r
        bottom_center = position + r * normal
        top_center = position + (self.height - r) * normal

        bottom_hemi = Part.makeSphere(r, bottom_center, normal, -90, 0, 360)
        top_hemi = Part.makeSphere(r, top_center, normal, 0, 90, 360)

        if cyl_length > 1e-6:
            cyl = Part.makeCylinder(r, cyl_length, bottom_center, normal)
            self.solid = bottom_hemi.fuse(cyl).fuse(top_hemi)
        else:
            self.solid = Part.makeSphere(r, bottom_center)


class Slot:
    """Elongated hole / oblong slot (rounded-rectangle profile extruded along normal).

    Creates two semicircular end caps connected by a rectangular body.  The
    slot is centered at *position* and extends along *direction*.

    Args:
        name:      identifier string.
        length:    overall length including the two end semicircles (mm).
        width:     slot width = end circle diameter (mm).  Must be <= length.
        depth:     extrusion depth along *normal* (mm).
        position:  center of the slot profile on the face.
        normal:    extrusion direction (default Z+).
        direction: elongation direction in the face plane (default X+).
    """

    def __init__(
        self,
        name: str,
        length: float,
        width: float,
        depth: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
        direction: Vector = Vector(1, 0, 0),
    ):
        self.name = name
        self.length = length
        self.width = width
        self.depth = depth
        self.position = position
        self.normal = normal

        r = width / 2
        center_dist = max(0.0, length - width)
        dir_unit = direction.normalize()

        c1 = position - dir_unit * (center_dist / 2)
        c2 = position + dir_unit * (center_dist / 2)

        cyl1 = Part.makeCylinder(r, depth, c1, normal)

        if center_dist > 1e-6:
            cyl2 = Part.makeCylinder(r, depth, c2, normal)
            # width direction: perpendicular to both normal and dir_unit
            perp = normal.cross(dir_unit).normalize()
            p1 = c1 + perp * r
            p2 = c2 + perp * r
            p3 = c2 - perp * r
            p4 = c1 - perp * r
            # use Flat so the face is guaranteed planar
            rect_face = Flat([p1, p2, p3, p4, p1]).face
            rect_solid = rect_face.extrude(normal * depth)
            self.solid = cyl1.fuse(cyl2).fuse(rect_solid)
        else:
            self.solid = cyl1


class CountersinkHole:
    """Through-hole with a conical chamfered entry for flat-head (countersunk) screws.

    The cone opens at *position* (flush with the top face) and tapers down to
    *hole_diameter*.  The remaining *depth* continues as a plain cylinder.
    Use ``COUNTERSINK_MAP`` for standard DIN 7991 / ISO 10642 dimensions.

    Args:
        name:                  identifier.
        hole_diameter:         core hole / clearance diameter (mm).
        countersink_diameter:  outer diameter of the cone opening (mm).
        depth:                 depth of the plain cylinder section below the cone (mm).
        position:              center of the top face (cone entry).
        normal:                direction going INTO the material (default Z+).
        angle:                 countersink half-angle in degrees (default 45 → 90° included angle).

    Example (M3 countersink)::

        cs = CountersinkHole("cs_m3",
                             hole_diameter=COUNTERSINK_MAP["M3"]["d"],
                             countersink_diameter=COUNTERSINK_MAP["M3"]["dK"],
                             depth=10)
        body = body.cut(cs.solid)
    """

    def __init__(
        self,
        name: str,
        hole_diameter: float,
        countersink_diameter: float,
        depth: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
        angle: float = 45.0,
    ):
        self.name = name
        cs_depth = (
            (countersink_diameter - hole_diameter) / 2 / math.tan(math.radians(angle))
        )
        cone = Part.makeCone(
            countersink_diameter / 2, hole_diameter / 2, cs_depth, position, normal
        )
        cyl_pos = position + cs_depth * normal
        cyl = Part.makeCylinder(hole_diameter / 2, depth, cyl_pos, normal)
        self.solid = cone.fuse(cyl)


class CounterboreHole:
    """Through-hole with a flat-bottomed cylindrical recess (counterbore) for socket-head cap screws.

    Args:
        name:          identifier.
        hole_diameter: core hole / clearance diameter (mm).
        bore_diameter: counterbore diameter — use screw head diameter + clearance (mm).
        bore_depth:    depth of the wide recess — use screw head height + clearance (mm).
        total_depth:   total hole depth (mm).  Must be >= bore_depth.
        position:      center of the top face.
        normal:        direction going INTO the material (default Z+).

    Example (M5 socket-head screw, head dK=8.5mm, head height k=4mm)::

        cb = CounterboreHole("cb_m5",
                             hole_diameter=5.5,
                             bore_diameter=9.0,
                             bore_depth=5.0,
                             total_depth=20)
        body = body.cut(cb.solid)
    """

    def __init__(
        self,
        name: str,
        hole_diameter: float,
        bore_diameter: float,
        bore_depth: float,
        total_depth: float,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
    ):
        self.name = name
        bore = Part.makeCylinder(bore_diameter / 2, bore_depth, position, normal)
        cyl_pos = position + bore_depth * normal
        cyl = Part.makeCylinder(
            hole_diameter / 2, total_depth - bore_depth, cyl_pos, normal
        )
        self.solid = bore.fuse(cyl)


class NutTrap:
    """Blind hexagonal pocket to capture a DIN nut inside a 3D-printed part.

    The pocket is sized with a coarse tolerance so the nut slides in but
    cannot rotate.  Cut this solid from your part body.

    Args:
        name:        identifier.
        size:        nut size string (same keys as NUT_MAP, e.g. ``"M3"``).
        position:    center of the pocket opening on the face.
        normal:      direction going INTO the material (default Z+).
        extra_depth: additional depth beyond the nut height (mm), e.g. for a thin
                     layer of plastic that holds the nut in place.

    Example::

        trap = NutTrap("nut_trap", "M3", Vector(0, 0, 0))
        body = body.cut(trap.solid)
    """

    def __init__(
        self,
        name: str,
        size: NUT_SIZES,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
        extra_depth: float = 0.0,
    ):
        self.name = name
        tolerances = GeneralTolerances()
        nut_height = NUT_MAP[size]["H"]
        nut_radius = NUT_MAP[size]["AF"] / math.sqrt(3)
        pocket_radius = nut_radius + tolerances.get_tolerance(nut_radius, "c")
        pocket_depth = (
            nut_height + tolerances.get_tolerance(nut_height, "c") + extra_depth
        )
        p1 = Polygon(position, pocket_radius, normal, sides=6)
        p2 = Polygon(position + pocket_depth * normal, pocket_radius, normal, sides=6)
        self.solid = Polyhedron(p1, p2).solid


class HeatSetInsert:
    """Cylindrical pocket for a heat-set threaded brass insert (Ruthex / CNC Kitchen standard).

    Heat-set inserts are pressed in with a soldering iron.  Cut this pocket
    from your part body.  The pocket diameter is slightly larger than the
    insert OD so the knurling bites into the plastic when heated.

    Sizes in ``HEAT_SET_INSERT_MAP``: M2, M3, M4, M5.

    Args:
        name:     identifier.
        size:     ``"M2"``, ``"M3"``, ``"M4"``, or ``"M5"``.
        position: center of the pocket opening.
        normal:   direction going INTO the material (default Z+).

    Example::

        ins = HeatSetInsert("hs_m3", "M3", Vector(0, 0, 10), Vector(0, 0, -1))
        body = body.cut(ins.solid)
    """

    def __init__(
        self,
        name: str,
        size: str,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
    ):
        self.name = name
        pd = HEAT_SET_INSERT_MAP[size]["pocket_d"]
        pl = HEAT_SET_INSERT_MAP[size]["pocket_l"]
        self.solid = Part.makeCylinder(pd / 2, pl, position, normal)


class BearingPocket:
    """Cylindrical press-fit pocket for a standard deep-groove ball bearing.

    Cut this from your part body.  Add a separate shaft hole for the bore.
    Standard bearing types are in ``BEARING_MAP``.

    Args:
        name:         identifier.
        bearing_type: bearing designation string, e.g. ``"608"``, ``"625"``.
        position:     center of the pocket opening face.
        normal:       direction going INTO the part (default Z+).
        tolerance:    DIN ISO 2768 class for the pocket diameter.
                      ``"f"`` (fine, press-fit) is the default for bearings.

    Properties:
        bore:            bearing bore diameter (mm).
        outer_diameter:  bearing outer diameter (mm).
        bearing_width:   bearing width / depth of pocket (mm).

    Example::

        pocket = BearingPocket("bp608", "608", Vector(0, 0, 0))
        body = body.cut(pocket.solid)
        # shaft hole
        shaft = Cylinder("shaft", pocket.bore, 30, Vector(0, 0, 0))
        body = body.cut(shaft.solid)
    """

    def __init__(
        self,
        name: str,
        bearing_type: str,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
        tolerance: str = "f",
    ):
        self.name = name
        b = BEARING_MAP[bearing_type]
        self.bore = b["bore"]
        self.outer_diameter = b["OD"]
        self.bearing_width = b["width"]
        tolerances = GeneralTolerances()
        pocket_r = b["OD"] / 2 + tolerances.get_tolerance(b["OD"] / 2, tolerance)
        self.solid = Part.makeCylinder(pocket_r, b["width"], position, normal)


class MagnetPocket:
    """Blind cylindrical recess sized for a standard neodymium disc magnet.

    Cut this from your part body.  Standard sizes are in ``MAGNET_SIZES``.

    Args:
        name:         identifier.
        magnet_size:  size key string, e.g. ``"10x2"`` (diameter x height in mm).
        position:     center of the pocket opening face.
        normal:       direction going INTO the material (default Z+).
        clearance:    radial AND depth clearance in mm added to the magnet dimensions
                      (default 0.2 mm — snug fit; use 0.3 for easy insertion).

    Example::

        mag = MagnetPocket("mag", "10x2", Vector(0, 0, 0))
        body = body.cut(mag.solid)
    """

    def __init__(
        self,
        name: str,
        magnet_size: str,
        position: Vector = Vector(0, 0, 0),
        normal: Vector = Vector(0, 0, 1),
        clearance: float = 0.2,
    ):
        self.name = name
        m = MAGNET_SIZES[magnet_size]
        pocket_r = m["D"] / 2 + clearance
        pocket_depth = m["H"] + clearance
        self.solid = Part.makeCylinder(pocket_r, pocket_depth, position, normal)
