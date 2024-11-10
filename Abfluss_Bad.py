import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Dusche')

# Parameter all in mm
sieb_durchmesser = 85.5
sieb_höhe = 1

sieb = Cylinder("sieb", sieb_durchmesser, sieb_höhe)


loch_durchmesser = 4
for x_offset in range(-84, 84, loch_durchmesser*2):
    for y_offset in range(-84, 84, loch_durchmesser*2):
        
        distance = math.sqrt(x_offset**2 + y_offset**2)
        
        # check ob loch innerhalb kreis liegt
        if distance < (sieb_durchmesser/2-loch_durchmesser):

            loch = Cylinder("loch", loch_durchmesser, sieb_höhe, Vector(x_offset, y_offset))
            #print(x_offset, y_offset, distance)
            #show(loch, name=loch.name)
            sieb.solid = sieb.solid.cut(loch.solid)

handle_durchmesser = 16
handle = Cylinder("handle", handle_durchmesser, sieb_höhe+5)
sieb.solid = sieb.solid.fuse(handle.solid)
show(sieb, name=sieb.name)


export('Dusche', "sieb")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
