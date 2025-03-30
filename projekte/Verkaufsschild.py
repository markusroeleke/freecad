import FreeCAD, Part
from FreeCAD import Vector
from typing import List

# create new document
doc_name = 'Verkaufsschild'
FreeCAD.newDocument(doc_name)
FreeCAD.Gui.runCommand('Std_DrawStyle',6) #shaded wireframe

from freecad_lib import *
from freecad_lib import SolidText

# Parameter all in mm
length = 245
width = 140
height = 10

Honigschild = Box(Vector(-length/2, -width/2, 0),
                  Vector( length/2,  width/2, height),
                  [Vector(30,30, 0)])
Honigschild.solid = Honigschild.solid.makeFillet(2, Honigschild.solid.Edges)

position = Vector(Honigschild.w+10, Honigschild.c+30, Honigschild.u)

# Verkaufstext
offset = Vector(0, -30, 0)
txt_list = ["  Honig",
            "vom Imker",]
            #"bee-modern.de"]
for n, txt in enumerate(txt_list):
    text = SolidText(txt, position=position+offset*n, height=-height, txt_height=10)
    Honigschild.solid = Honigschild.solid.cut(text.solid)


show(Honigschild, name="Honigschild")


# export 
import Mesh

for obj in ["Honigschild"]:
    Mesh.export([FreeCAD.getDocument("Verkaufsschild").getObject(obj)], 
                f"/Users/Markus/Documents/Projekte/FreeCAD/stl/{obj}.stl")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
