import FreeCAD, Part
from FreeCAD import Vector
from typing import List

# create new document
doc_name = 'Cylinder'
FreeCAD.newDocument(doc_name)
FreeCAD.Gui.runCommand('Std_DrawStyle',6) #shaded wireframe

from freecad_lib import *
from freecad_lib import SolidText

# Parameter all in mm
breite = 80
tiefe = 30
höhe = 30

box = Box(Vector(-breite/2, 0 , 0), Vector(breite/2, tiefe, höhe))
body = box.solid

breite = 40
tiefe = 100
höhe = 30

box = Box(Vector(-breite/2, 0, 0), Vector(breite/2, tiefe, höhe))
body = body.fuse(box.solid)

breite = 80
tiefe = 20
höhe = 30

box = Box(Vector(-breite/2, 0, 10), Vector(breite/2, tiefe, höhe))
body = body.cut(box.solid)

hole = Cylinder("zylinder", 30, höhe, Vector(0, 80, 0))
#show(hole, name=hole.name)

box.solid = body.cut(hole.solid)
show(box, name="body")


# export 
# import Mesh

# for obj in ["halter"]:
#     Mesh.export([FreeCAD.getDocument("Cylinder").getObject(obj)], 
#                 f"/Users/Markus/Documents/Projekte/FreeCAD/stl/{obj}.stl")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
