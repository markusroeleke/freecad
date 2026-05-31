import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from src.freecad_lib import *
from src.freecad_lib import SolidText

# create new document
new_doc("Dusche")

# Parameter all in mm
sieb_durchmesser = 86
sieb_höhe = 2

sieb = Cylinder("sieb", sieb_durchmesser, sieb_höhe)


loch_durchmesser = 5
start_offset = int(sieb_durchmesser)
for x_offset in range(-start_offset, start_offset, loch_durchmesser * 2):
    for y_offset in range(-start_offset, start_offset, loch_durchmesser * 2):

        distance = math.sqrt(x_offset**2 + y_offset**2)

        # check ob loch innerhalb kreis liegt
        if distance < (sieb_durchmesser / 2 - loch_durchmesser):

            loch = Cylinder(
                "loch", loch_durchmesser, sieb_höhe, Vector(x_offset, y_offset)
            )
            # print(x_offset, y_offset, distance)
            # show(loch, name=loch.name)
            sieb.solid = sieb.solid.cut(loch.solid)

handle_durchmesser = 16
handle = Cylinder("handle", handle_durchmesser, sieb_höhe + 5)
sieb.solid = sieb.solid.fuse(handle.solid)
show(sieb, name=sieb.name)


export("Dusche", "sieb")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
