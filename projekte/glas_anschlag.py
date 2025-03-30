import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Servohalter')

# Parameter all in mm
anschlag_länge = 106
anschlag_höhe = 20
anschlag_breite = 95
anschlag_wandung = 2.5
# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

anschlag = Box(Vector(-anschlag_breite/2, -anschlag_länge/2, 0),
               Vector( anschlag_breite/2,  anschlag_länge/2, anschlag_höhe),)


waage = Box(Vector(anschlag.w, anschlag.s+anschlag_wandung, 0),
            Vector(anschlag.e-anschlag_wandung, anschlag.n-anschlag_wandung, 10),)

anschlag.solid = anschlag.solid.cut(waage.solid)
glas_durchmesser = 51
loch1 = Polyhedron(Polygon(Vector(anschlag.c, anschlag.m, anschlag.d), glas_durchmesser/2, Vector(0,0,1), sides=6), 
                   Polygon(Vector(anschlag.c, anschlag.m, anschlag.u), glas_durchmesser/2, Vector(0,0,1), sides=6))
anschlag.solid = anschlag.solid.cut(loch1.solid)

#show(waage, name="waage")
show(anschlag, name="anschlag")


export('Servohalter', "anschlag")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
