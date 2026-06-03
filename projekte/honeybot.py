import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *

# create new document
new_doc("honeybot")

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

# Parameter all in mm
base_width = 150  # x
base_length = 150  # y
base_hight = 20  # z
wall_thickness = 5

###############################################################################
# base
###############################################################################
base = Box(
    vWSD=Vector(-base_width / 2, -base_length / 2, 0),
    vENU=Vector(
        base_width / 2,
        base_length / 2,
        base_hight,
    ),
    joints=[Vector(15, 15, 0)],
)

base_clearance = Box(
    vWSD=base.vWSD + Vector(wall_thickness, wall_thickness, wall_thickness),
    vENU=base.vENU - Vector(wall_thickness, wall_thickness, 0),
    joints=[Vector(15, 15, 0)],
)

base.solid = base.solid.cut(base_clearance.solid)


###############################################################################
# stand
###############################################################################
stand_width = 20  # x
stand_length = 50  # y
stand_hight = 5  # z
stand = Box(
    vWSD=Vector(-stand_width / 2, -stand_length, 0),
    vENU=Vector(stand_width / 2, 0, stand_hight)
)

position = Vector(0, 60, base_clearance.d)
stand.solid = stand.solid.translate(position)

show(stand, name="stand")

###############################################################################
# PCB
###############################################################################
pcb_hole_diameter = 4.1
pcb_width = 50
pcb_length = 70
pcb_hight = 1.6

pcb = Box(
    vWSD=Vector(-pcb_width / 2, -pcb_length / 2, 0),
    vENU=Vector(pcb_width / 2, pcb_length / 2, pcb_hight)
)

# add holes to pcb
hole1 = Cylinder("hole1", pcb_hole_diameter, pcb_hight + 1)
hole1_position = Vector(-pcb_width / 2 + 4, -pcb_length / 2 + 4, 0)
hole2 = Cylinder("hole2", pcb_hole_diameter, pcb_hight + 1)
hole2_position = Vector(pcb_width / 2 - 4, -pcb_length / 2 + 4, 0)
hole3 = Cylinder("hole3", pcb_hole_diameter, pcb_hight + 1)
hole3_position = Vector(-pcb_width / 2 + 4, pcb_length / 2 - 4, 0)
hole4 = Cylinder("hole4", pcb_hole_diameter, pcb_hight + 1)
hole4_position = Vector(pcb_width / 2 - 4, pcb_length / 2 - 4, 0)
hole1 = hole1.solid.translate(hole1_position)
pcb.solid = pcb.solid.cut(hole1)
hole2 = hole2.solid.translate(hole2_position)
pcb.solid = pcb.solid.cut(hole2)
hole3 = hole3.solid.translate(hole3_position)
pcb.solid = pcb.solid.cut(hole3)
hole4 = hole4.solid.translate(hole4_position)
pcb.solid = pcb.solid.cut(hole4)

pcb_position = Vector(-40, 0, base_clearance.d + stand_hight)
pcb.solid = pcb.solid.translate(pcb_position)

show(pcb, name="pcb", color=(0.8, 0.3, 0.8))



###############################################################################
# load cell
###############################################################################
load_cell_width = stand_width
load_cell_length = 120
load_cell_hight = 20

load_cell = Box(
    vWSD=Vector(-load_cell_width / 2, -load_cell_length / 2, 0),
    vENU=Vector(load_cell_width / 2, load_cell_length / 2, load_cell_hight)
)
load_cell_position = Vector(stand.n, 0, base_clearance.d + stand_hight)
load_cell.solid = load_cell.solid.translate(load_cell_position)
show(load_cell, name="load_cell", color=(0.2, 0.8, 0.8))

# combine all parts
base.solid = base.solid.fuse(stand.solid)

show(base, name="base")
export("honeybot", "base")

# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
