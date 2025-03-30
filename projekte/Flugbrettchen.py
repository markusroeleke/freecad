import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Beute')

# Parameter all in mm
außen_breite = 150
außen_höhe = 10
außen_tiefe = 80

flugbrettchen = Box(Vector(-außen_tiefe/2, -außen_breite/2, 0),
                    Vector( außen_tiefe/2,  außen_breite/2, außen_höhe))

show(flugbrettchen, name="flugbrettchen")


export('Beute', "flugbrettchen")

# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
