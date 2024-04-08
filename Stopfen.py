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
diameter = 22
height = 12

cylinder = Polyhedron(Polygon(Vector(0, 0, 0), diameter/2, Vector(0,0,1)), 
                     Polygon(Vector(0, 0, height), diameter/2, Vector(0,0,1))
                )
cylinderBody = cylinder.solid

holeDiameter = 4.5
holeHeight = 11
cylinderHole = Polyhedron(Polygon(Vector(0, 0, 0), holeDiameter/2, Vector(0,0,1)), 
                     Polygon(Vector(0, 0, holeHeight), holeDiameter/2, Vector(0,0,1))
                )
cylinderBody = cylinderBody.cut(cylinderHole.solid)
cylinderBody = cylinderBody.makeFillet(9, [cylinderBody.Edge3])
cylinderBody = cylinderBody.makeFillet(2, [cylinderBody.Edge8])

bodyFeature = Part.show(cylinderBody, 'cylinderBody')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (0/255.0, 0x8C/255.0, 0x4A/255.0)

# export 
import Mesh

for obj in ["cylinderBody"]:
    Mesh.export([FreeCAD.getDocument("Cylinder").getObject(obj)], 
                f"/Users/Markus/Documents/Projekte/FreeCAD/stl/{obj}.stl")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
