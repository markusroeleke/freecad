import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from src.freecad_lib import *
from src.freecad_lib import SolidText

# create new document
new_doc("Waschmaschine")

# Parameter all in mm
lasche_länge = 10
lasche_höhe = 3
lasche_breite_außen = 10

lasche_wandung = 0.75
rohr_durchmesser = 13.1

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

lasche = Box(
    Vector(-lasche_länge / 2, -lasche_breite_außen / 2, 0),
    Vector(lasche_länge / 2, lasche_breite_außen / 2, lasche_höhe),
)

z_offset = lasche.d + rohr_durchmesser / 2 + lasche_wandung
rohr = Polyhedron(
    Polygon(
        Vector(lasche.c, lasche.n, z_offset), rohr_durchmesser / 2, Vector(0, 1, 0)
    ),
    Polygon(
        Vector(lasche.c, lasche.s, z_offset), rohr_durchmesser / 2, Vector(0, 1, 0)
    ),
)

loch_durchmesser = 4.1
loch = Polyhedron(
    Polygon(
        Vector(lasche.c, lasche.m, lasche.u), loch_durchmesser / 2, Vector(0, 0, 1)
    ),
    Polygon(
        Vector(lasche.c, lasche.m, lasche.d), loch_durchmesser / 2, Vector(0, 0, 1)
    ),
)

lasche.solid = lasche.solid.cut(rohr.solid)
lasche.solid = lasche.solid.cut(loch.solid)

# show(rohr, name="rohr")
# show(loch, name="loch")
show(lasche, name="lasche")


export("Waschmaschine", "lasche")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
