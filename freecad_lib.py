import FreeCAD, Part, FreeCADGui
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
    def __init__(self, vWSD, vENU, joints=[]):

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
        self, text, position=Vector(0, 0, 0), height=-1, txt_height=6, spacing=0.5
    ):
        self.position = position
        self.height = height
        self.txt_height = txt_height
        self.text = text
        font = "tc_lasersans.ttf"
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
        self, name, size: NUT_SIZES, position=Vector(0, 0, 0), normal=Vector(0, 0, 1)
    ):
        self.name = name
        self.position = position
        self.normal = normal

        # AF = radius * sqrt(3)
        self.nut_height = NUT_MAP[size]["H"]
        self.nut_across_sides = NUT_MAP[size]["AF"]
        self.nut_radius = NUT_MAP[size]["AF"] / math.sqrt(3)

        self.draw()

    def draw(self):

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
