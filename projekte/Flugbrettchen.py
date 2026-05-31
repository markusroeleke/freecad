import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from src.freecad_lib import *
from src.freecad_lib import SolidText

# create new document
new_doc("Beute")

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

# Parameter all in mm
außen_breite = 160
außen_höhe = 20
außen_tiefe = 80

flugbrettchen = Box(
    Vector(-außen_breite / 2, -außen_tiefe / 2, 0),
    Vector(außen_breite / 2, außen_tiefe / 2, außen_höhe),
)
flugbrettchen.solid = flugbrettchen.solid.makeChamfer(
    außen_höhe - 2, außen_tiefe - 5, [flugbrettchen.solid.Edge4]
)

# unterlegscheibe
u_durchmesser = 18
u_dicke = 2.8
u_distanz = 120
offset1 = Vector(
    flugbrettchen.c - u_distanz / 2, flugbrettchen.n - u_dicke, flugbrettchen.d
)

u_scheibe_slide1 = Box(
    Vector(-u_durchmesser / 2, -u_dicke / 2, 0) + offset1,
    Vector(u_durchmesser / 2, u_dicke / 2, u_durchmesser + 1) + offset1,
)
# show(u_scheibe_slide1, name="u_scheibe_slide1")
flugbrettchen.solid = flugbrettchen.solid.cut(u_scheibe_slide1.solid)

offset2 = Vector(
    flugbrettchen.c + u_distanz / 2, flugbrettchen.n - u_dicke, flugbrettchen.d
)

u_scheibe_slide2 = Box(
    Vector(-u_durchmesser / 2, -u_dicke / 2, 0) + offset2,
    Vector(u_durchmesser / 2, u_dicke / 2, u_durchmesser + 1) + offset2,
)
# show(u_scheibe_slide2, name="u_scheibe_slide2")
flugbrettchen.solid = flugbrettchen.solid.cut(u_scheibe_slide2.solid)

show(flugbrettchen, name="flugbrettchen")
export("Beute", "flugbrettchen")

# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
