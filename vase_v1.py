import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Wohnung')

# Parameter all in mm
vase_durchmesser = 100
vase_höhe = 100
vase_wandung = 8

vase = Cylinder("Vase_v1", 
                vase_durchmesser, 
                vase_höhe)
innen = Cylinder("innen", 
                 vase_durchmesser-vase_wandung*2, 
                 vase_höhe-vase_wandung,
                 Vector(0, 0, vase_wandung))
fuß_rundung = 10
fuß = Cylinder("fuß", 
                vase_durchmesser-fuß_rundung*2, 
                vase_wandung,
                Vector(0, 0, -vase_wandung))
vase.solid = vase.solid.cut(innen.solid)
vase.solid = vase.solid.fuse(fuß.solid)

# ecken abrunden
vase.solid = vase.solid.makeFillet(fuß_rundung*0.99, [ vase.solid.Edge1])


show(vase, name=vase.name)


export('Wohnung', "Vase_v1")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
