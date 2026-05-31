import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from src.freecad_lib import *
from src.freecad_lib import SolidText

# create new document
new_doc("Halter")

# Parameter all in mm
extrusion = 15
wandung = 2
innen_höhe_oben = 14.5
innen_breite = 14.5
innen_länge = 133
innen_höhe_unten = 8

# berechnete Werte
außen_länge = wandung + innen_länge + innen_höhe_unten
außen_breite = wandung * 2 + innen_breite


body = Box(
    Vector(-außen_breite / 2, -außen_länge / 2, 0),
    Vector(außen_breite / 2, außen_länge / 2, extrusion),
)

innen_unten = Box(
    Vector(body.w + wandung, body.s, 0),
    Vector(body.e - wandung, body.s + innen_höhe_unten, extrusion),
)
body.solid = body.solid.cut(innen_unten.solid)


innen_oben = Box(
    Vector(body.w + wandung, body.n - wandung - innen_höhe_oben, 0),
    Vector(body.e - wandung, body.n - wandung, extrusion),
)
body.solid = body.solid.cut(innen_oben.solid)


innen_oben_freischnitt = Box(
    Vector(body.w + wandung * 2.5, body.n - wandung * 2 - innen_höhe_oben, 0),
    Vector(body.e - wandung, body.n - wandung, extrusion),
)
body.solid = body.solid.cut(innen_oben_freischnitt.solid)

innen_mitte = Box(
    Vector(body.w, body.s + innen_höhe_unten + wandung, 0),
    Vector(body.e - wandung, body.n - wandung * 2 - innen_höhe_oben, extrusion),
)
body.solid = body.solid.cut(innen_mitte.solid)

show(body, name="Topfdeckelhalter")
# show(innen_unten, name="innen_unten")
# show(innen_oben, name="innen_oben")
# show(innen_oben_freischnitt, name="innen_oben_freischnitt")
# show(innen_mitte, name="innen_mitte")

export("Halter", "Topfdeckelhalter")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
