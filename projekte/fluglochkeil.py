import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Beute')

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

# Parameter all in mm
außen_tiefe = 230
außen_höhe = 24
außen_breite = 24

aussparung_tiefe = 150
aussparung_höhe = 6
offset = Vector(0, außen_tiefe+außen_höhe, 0)
keil = Box(Vector(-außen_breite/2, -außen_tiefe/2, 0) + offset,
           Vector(außen_breite/2, außen_tiefe/2, außen_höhe)+offset)

aussparung1 = Box(Vector(keil.e-aussparung_höhe, keil.n-30-aussparung_tiefe, 0),
                  Vector(keil.e+aussparung_höhe, keil.n-30, außen_höhe), 
                [Vector(6,6,0)])
keil.solid = keil.solid.cut(aussparung1.solid)
aussparung2 = Box(Vector(keil.c, keil.s+außen_höhe, 0),
                  Vector(keil.e, keil.s, außen_höhe))
keil.solid = keil.solid.cut(aussparung2.solid)

screw = Screw("M4_Schraube", "M4", 16, 
          position=Vector(keil.w+6,aussparung2.m, aussparung2.g),
          normal=Vector(-1,0,0))
keil.solid = keil.solid.cut(screw.solid)
show(keil, name="keil_150mm")

#show(screw, name="M4_Schraube")
export('Beute', "keil_150mm")


aussparung_tiefe = 30
aussparung_höhe = 6

keil = Box(Vector(-außen_breite/2, -außen_tiefe/2, 0),
           Vector(außen_breite/2, außen_tiefe/2, außen_höhe))

aussparung1 = Box(Vector(keil.e-aussparung_höhe, keil.s+30, 0),
                 Vector(keil.e+aussparung_höhe, keil.s+30+aussparung_tiefe, außen_höhe), 
                [Vector(6,6,0)])
keil.solid = keil.solid.cut(aussparung1.solid)
aussparung2 = Box(Vector(keil.w, keil.n-außen_höhe, keil.u),
                  Vector(keil.e, keil.n, keil.g))
keil.solid = keil.solid.cut(aussparung2.solid)

screw = Screw("M4_Schraube", "M4", 16, 
          position=Vector(aussparung2.c ,aussparung2.m, aussparung2.g),
          normal=Vector(0,0,1))
nut = Nut("M4_Mutter", 
          "M4", 
          position=Vector(aussparung2.c ,aussparung2.m, 6),
          normal=Vector(0,0,-1))

loch_durchmesser = 7.5
loch = Polyhedron(Polygon(Vector(aussparung1.c ,aussparung1.m, aussparung1.g), loch_durchmesser/2, Vector(1,0,0)), 
                  Polygon(Vector(keil.w ,aussparung1.m, aussparung1.g), loch_durchmesser/2, Vector(1,0,0))
                    )
#show(loch, name="loch")
#show(nut, name="M4_Mutter")
keil.solid = keil.solid.cut(loch.solid)
keil.solid = keil.solid.cut(nut.solid)
keil.solid = keil.solid.cut(screw.solid)

show(keil, name="keil_30mm")
export('Beute', "keil_30mm")

# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
