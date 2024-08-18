import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Dusche')

# Parameter all in mm
einlass_durchmesser = 245
einlass_höhe = 200

siphon = Cylinder("Siphon", einlass_durchmesser, 20)

show(siphon, name=siphon.name)


export('Dusche', "Siphon")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
