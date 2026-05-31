import FreeCAD, Part
from FreeCAD import Vector
from typing import List
import copy

from src.freecad_lib import *

# create new document
new_doc("Varovap")

# Parameter all in mm
länge = 80
breite = 72
höhe = 6

platte = Box(Vector(-länge / 2, -breite / 2, 0), Vector(länge / 2, breite / 2, höhe))

länge = 32
breite = 7
aussparung = Box(
    Vector(-länge / 2, platte.n - breite, 0), Vector(länge / 2, platte.n, höhe)
)
platte.solid = platte.solid.cut(aussparung.solid)

platte_unten = copy.copy(platte)
platte_oben = copy.copy(platte)

# löcher für M4 schrauben
# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)
loch_durchmesser = 4.1
abstand = 5
for x_offset, y_offset in [
    (platte.w + abstand, platte.n - abstand),
    (platte.e - abstand, platte.n - abstand),
    (platte.w + abstand, platte.m),
    (platte.e - abstand, platte.m),
    (platte.w + abstand, platte.s + abstand),
    (platte.e - abstand, platte.s + abstand),
]:
    # platte unten und oben
    loch = Cylinder("loch", loch_durchmesser, höhe, Vector(x_offset, y_offset, 0))
    platte_unten.solid = platte_unten.solid.cut(loch.solid)
    platte_oben.solid = platte_oben.solid.cut(loch.solid)

    # platte unten löcher
    mutter = Nut("mutter", "M4", Vector(x_offset, y_offset, 4), Vector(0, 0, -1))
    platte_unten.solid = platte_unten.solid.cut(mutter.solid)

    # platte oben
    senkung = Polyhedron(
        Polygon(
            Vector(x_offset, y_offset, platte.u - 2.5),
            loch_durchmesser / 2,
            Vector(0, 0, 1),
        ),
        Polygon(
            Vector(x_offset, y_offset, platte.u), loch_durchmesser, Vector(0, 0, 1)
        ),
    )
    platte_oben.solid = platte_oben.solid.cut(senkung.solid)
# platte unten M3 löcher

schraube1 = Screw(
    "schraube", "M3", 10, Vector(platte_unten.c + 11, platte_unten.m - 15.5, 3)
)
schraube2 = Screw(
    "schraube", "M3", 10, Vector(platte_unten.c - 11, platte_unten.m - 15.5, 3)
)
schraube3 = Screw(
    "schraube", "M3", 10, Vector(platte_unten.c, platte_unten.m + 15.5, 3)
)

# show(schraube1, name="schraube1")
# show(schraube2, name="schraube2")
# show(schraube3, name="schraube3")

platte_unten.solid = platte_unten.solid.cut(schraube1.head_clearance.solid)
platte_unten.solid = platte_unten.solid.cut(schraube2.head_clearance.solid)
platte_unten.solid = platte_unten.solid.cut(schraube3.head_clearance.solid)
platte_unten.solid = platte_unten.solid.cut(schraube1.thread_clearance.solid)
platte_unten.solid = platte_unten.solid.cut(schraube2.thread_clearance.solid)
platte_unten.solid = platte_unten.solid.cut(schraube3.thread_clearance.solid)

show(platte_unten, name="platte_unten")
show(platte_oben, name="platte_oben")

# export
export("Varovap", "platte_unten")
export("Varovap", "platte_oben")

# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
