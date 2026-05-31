import FreeCAD, Part
from FreeCAD import Vector
from typing import List

from src.freecad_lib import *
from src.freecad_lib import SolidText

# create new document
new_doc("Hydroponic")

# Parameter all in mm

# erstelle body
body_durchmesser = 50
adapter_höhe = 60
adapter = Cylinder("hydro_adapter", body_durchmesser, adapter_höhe)

# base
base_durchmesser = 100
base_höhe = 6
base = Cylinder("base", base_durchmesser, base_höhe)
adapter.solid = adapter.solid.fuse(base.solid)

# loch für Flasche
loch_durchmesser = 32
höhe_über_boden = 4
loch = Cylinder("loch", loch_durchmesser, adapter_höhe, Vector(0, 0, höhe_über_boden))
adapter.solid = adapter.solid.cut(loch.solid)

# auslauf
auslauf_länge = base_durchmesser
auslauf_breite = 8
auslauf1 = Box(
    Vector(-auslauf_länge / 2, -auslauf_breite / 2, 0),
    Vector(auslauf_länge / 2, auslauf_breite / 2, höhe_über_boden),
)
# show(auslauf1, name="auslauf1")

adapter.solid = adapter.solid.cut(auslauf1.solid)
auslauf2 = Box(
    Vector(-auslauf_breite / 2, -auslauf_länge / 2, 0),
    Vector(auslauf_breite / 2, auslauf_länge / 2, höhe_über_boden),
)
adapter.solid = adapter.solid.cut(auslauf2.solid)

# fase oben
adapter.solid = adapter.solid.makeChamfer(6, 6, [adapter.solid.Edge44])

show(adapter, name=adapter.name)
export("Hydroponic", "hydro_adapter")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
