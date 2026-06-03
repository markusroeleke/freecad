import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc("honeybot")

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

# Parameter all in mm
base_width = 150  # x
base_length = 150  # y
base_hight = 20  # z
wall_thickness = 4

# honey box lid
base = Box(
    vWSD=Vector(-base_width / 2, -base_length / 2, 0),
    vENU=Vector(
        base_width / 2,
        base_length / 2,
        base_hight,
    ),
    joints=[Vector(15, 15, 0)],
)


show(base, name="base")
export("honeybot", "base")

# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
