import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *

# create new document
new_doc('Verkaufsschild')


# Parameter all in mm
length = 80
width = 9
height = 1

schild = Box(Vector(-length/2, -width/2, 0),
                  Vector( length/2,  width/2, height),
                  [Vector(1,1, 0)])
#schild.solid = schild.solid.makeFillet(1, schild.solid.Edges)

position = Vector(schild.w+1, schild.s+2, schild.u)

# Verkaufstext
text = SolidText("X-Mas #LikeABosch", position=position, height=-height, txt_height=2.5)
schild.solid = schild.solid.cut(text.solid)


show(schild, name="Schild")
show(text, name="text")

# export 
export('Verkaufsschild', "Schild")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
