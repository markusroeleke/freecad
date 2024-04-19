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

m4_side_slide = Quader("m4_side_slide", 10, 10, 10)
m4_nut = Nut("side_slide", "M4", normal=Vector(0,1,0),position=Vector(0, 0, 5))
m4_side_slide.solid = m4_side_slide.solid.cut(m4_nut.slide_clearance.solid)
m4_side_slide.solid = m4_side_slide.solid.cut(m4_nut.head_clearance.solid)


bodyFeature = Part.show(m4_side_slide.solid, 'm4_side_slide')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (0.50,0.40,0.80)


# export 
import Mesh

for obj in ["m4_side_slide"]:
    Mesh.export([FreeCAD.getDocument("Cylinder").getObject(obj)], 
                f"/Users/Markus/Documents/Projekte/FreeCAD/stl/{obj}.stl")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
