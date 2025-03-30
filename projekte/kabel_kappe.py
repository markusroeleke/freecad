import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Kappe')

# Parameter all in mm
außen_tiefe = 15
außen_höhe = 83
außen_breite = 83
wandung = 2
innen_breite = 29

adapter = Box(Vector(-außen_breite/2, -außen_höhe/2, 0),
              Vector(außen_breite/2, außen_höhe/2, außen_tiefe))

innen = Box(Vector(adapter.w+wandung*2, adapter.s, adapter.d+wandung),
            Vector(adapter.e-wandung*2, adapter.n-wandung*2, adapter.u))
adapter.solid = adapter.solid.cut(innen.solid)
show(adapter, name="Kappe")
#show(innen, name="innen")


export('Kappe', "Kappe")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
