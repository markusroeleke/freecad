import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Waschmaschine')

# Parameter all in mm
anschlag_länge = 45
anschlag_höhe = 55
anschlag_breite_außen = 55
anschlag_breite_innen = 55

anschlag_wandung = 5
tuer_durchmesser = 470

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

anschlag = Box(Vector(-anschlag_länge/2, -anschlag_breite_außen/2, 0),
               Vector( anschlag_länge/2,  anschlag_breite_außen/2,  anschlag_höhe),)

lasche = Box(Vector(anschlag.e-10, anschlag.s-90, anschlag.u-20),
             Vector(anschlag.e,    anschlag.s,    anschlag.u),)

z_offset = anschlag.d + tuer_durchmesser/2 + anschlag_wandung
tuer = Polyhedron(Polygon(Vector(anschlag.c, anschlag.n-anschlag_wandung, z_offset), tuer_durchmesser/2, Vector(0,1,0)), 
                  Polygon(Vector(anschlag.c, anschlag.s+anschlag_wandung, z_offset), tuer_durchmesser/2, Vector(0,1, 0)))

anschlag.solid = anschlag.solid.cut(tuer.solid)
anschlag.solid = anschlag.solid.fuse(lasche.solid)

#show(tuer, name="tuer")
show(anschlag, name="tuer_anschlag")


export('Waschmaschine', "tuer_anschlag")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
