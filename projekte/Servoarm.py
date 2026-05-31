import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from src.freecad_lib import *
from src.freecad_lib import SolidText

# create new document
new_doc("Servohalter")

# Parameter all in mm
arm1_länge = 75
arm1_loch_abstand = 65
loch_durchmesser = 4.5
arm_höhe = 5
arm_breite = 9.5

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

arm1 = Box(
    Vector(-arm1_länge / 2, -arm_breite / 2, 0),
    Vector(arm1_länge / 2, arm_breite / 2, arm_höhe),
)
# [Vector(5,5,0)])


#

loch1 = Polyhedron(
    Polygon(
        Vector(arm1.e - loch_durchmesser, arm1.m, arm1.d),
        loch_durchmesser / 2,
        Vector(0, 0, 1),
    ),
    Polygon(
        Vector(arm1.e - loch_durchmesser, arm1.m, arm1.u),
        loch_durchmesser / 2,
        Vector(0, 0, 1),
    ),
)
arm1.solid = arm1.solid.cut(loch1.solid)


loch2 = Polyhedron(
    Polygon(
        Vector(arm1.w + loch_durchmesser, arm1.m, arm1.d),
        loch_durchmesser / 2,
        Vector(0, 0, 1),
    ),
    Polygon(
        Vector(arm1.w + loch_durchmesser, arm1.m, arm1.u),
        loch_durchmesser / 2,
        Vector(0, 0, 1),
    ),
)
arm1.solid = arm1.solid.cut(loch2.solid)

loch_durchmesser = 2
loch3 = Polyhedron(
    Polygon(Vector(arm1.w + 15, arm1.m, arm1.d), loch_durchmesser / 2, Vector(0, 0, 1)),
    Polygon(Vector(arm1.w + 15, arm1.m, arm1.u), loch_durchmesser / 2, Vector(0, 0, 1)),
)
arm1.solid = arm1.solid.cut(loch3.solid)
loch4 = Polyhedron(
    Polygon(
        Vector(arm1.w + 15 + 6, arm1.m, arm1.d), loch_durchmesser / 2, Vector(0, 0, 1)
    ),
    Polygon(
        Vector(arm1.w + 15 + 6, arm1.m, arm1.u), loch_durchmesser / 2, Vector(0, 0, 1)
    ),
)
arm1.solid = arm1.solid.cut(loch4.solid)
loch5 = Polyhedron(
    Polygon(
        Vector(arm1.w + 15 + 15.5, arm1.m, arm1.d),
        loch_durchmesser / 2,
        Vector(0, 0, 1),
    ),
    Polygon(
        Vector(arm1.w + 15 + 15.5, arm1.m, arm1.u),
        loch_durchmesser / 2,
        Vector(0, 0, 1),
    ),
)
arm1.solid = arm1.solid.cut(loch5.solid)

loch0 = Box(Vector(arm1.w, arm1.s, 0), Vector(arm1.w + 10, arm1.n, arm_höhe))
arm1.solid = arm1.solid.cut(loch0.solid)

# show(loch0, name="loch3")
show(arm1, name="arm1")


export("Servohalter", "arm1")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
