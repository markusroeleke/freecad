import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Halter')

# Parameter all in mm
außen_tiefe = 90
außen_höhe = 20.5
außen_breite = 34
innen_höhe = 11
innen_breite = 29

adapter = Box(Vector(-außen_breite/2, -außen_höhe/2, 0),
              Vector(außen_breite/2, außen_höhe/2, außen_tiefe))

innen = Box(Vector(-innen_breite+adapter.e, -innen_höhe/2, 0),
            Vector(              adapter.e,  innen_höhe/2, außen_tiefe))
adapter.solid = adapter.solid.cut(innen.solid)
show(adapter, name="Adapter")


export('Halter', "Adapter")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
