import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *
from freecad_lib import SolidText

# create new document
new_doc('Elektrokasten')

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

# Maße für die TS 35-Schiene
TS35_WIDTH_MAX = 35.5     # X: Max Breite der Schiene in mm
TS35_WIDTH_MIN = 34.0   # X: Min Breite der Schiene in mm
TS35_HEIGHT = 2.5       # Y: Höhe der Schiene in mm
TS35_THICKNESS = 1.5    # Y: Höhe der Schiene in mm
TS35_GROOVE_HIGHT = 6   # Y: Höhe feder aussparung

SCREW_DRIVER_WIDTH  = 5.0   # x: Min Breite der Schiene in mm
SCREW_DRIVER_HEIGHT = 5.0 # y: Höhe der Schiene in mm
SCREW_DRIVER_HOLE_THINKNESS = 2.5

HOLDER_LENGTH = 31       # Z: Länge des Halters

HOLDER_HIGHT = 10       # y: Höhe des Halters
HOLDER_WIDTH = 39       # x: Breite der Schiene in mm

# 1. Hauptkörper der Halterung (zentrales Rechteck)
main_body = Box(
    Vector(-HOLDER_WIDTH / 2, -HOLDER_HIGHT/2, 0            ),  # West, South, Down
    Vector( HOLDER_WIDTH / 2,  HOLDER_HIGHT/2, HOLDER_LENGTH)  # East, North, Up
)

# 2. Linker Fuß (seitliche Verlängerung des unteren Bereichs links)
y_offset = main_body.s
ts35_body = Box(
    Vector( -TS35_WIDTH_MIN / 2, y_offset, 0),  # West, South, Down
    Vector(  TS35_WIDTH_MIN / 2, y_offset+TS35_HEIGHT,   HOLDER_LENGTH)  # East, North, Up
)
y_offset = ts35_body.n
ts35_groove = Box(
    Vector(-TS35_WIDTH_MAX / 2, y_offset,  0),  # West, South, Down
    Vector( TS35_WIDTH_MAX / 2, y_offset+TS35_THICKNESS,  HOLDER_LENGTH)  # East, North, Up
)

y_offset = ts35_groove.s
x_offset = ts35_groove.w
ts35_groove_swing = Box(
    Vector(                  x_offset, y_offset,  0),  # West, South, Down
    Vector( x_offset + TS35_THICKNESS, y_offset+TS35_GROOVE_HIGHT,  HOLDER_LENGTH)  # East, North, Up
)

screw_driver = Box(
    Vector( main_body.w - SCREW_DRIVER_WIDTH, main_body.s,  0),  # West, South, Down
    Vector( main_body.w , main_body.s+SCREW_DRIVER_HEIGHT,  HOLDER_LENGTH)  # East, North, Up
)

screw_driver_hole = Box(
    Vector( main_body.w-SCREW_DRIVER_HOLE_THINKNESS, screw_driver.s + SCREW_DRIVER_HOLE_THINKNESS,  SCREW_DRIVER_HOLE_THINKNESS),  # West, South, Down
    Vector( main_body.w, screw_driver.n,  HOLDER_LENGTH)  # East, North, Up
)
# 3. Die endgültige Halterung erstellen:
# - Hauptkörper
# - Minus den Fußaussparungen links und rechts
main_body.solid = main_body.solid.cut(ts35_body.solid)
main_body.solid = main_body.solid.cut(ts35_groove.solid)
main_body.solid = main_body.solid.cut(ts35_groove_swing.solid)
main_body.solid = main_body.solid.fuse(screw_driver.solid)
main_body.solid = main_body.solid.cut(screw_driver_hole.solid)

# ecken abrunden
main_body.solid = main_body.solid.makeFillet(1.5, [ main_body.solid.Edge9, main_body.solid.Edge59])

# Optional: Ausgabe, um die Boxen anzusehen (Placeholder, hängt von der verwendeten 3D-Bibliothek ab)
#print("Final Holder:", final_holder)



RC_BOX_HIGHT = 60.5 # X
RC_BOX_WIDTH = 43.5 # y
RC_BOX_LENGTH = 28.5 # y

RC_BOX_HOLDER_THICKNESS = 1
RC_BOX_HOLDER_HIGHT = RC_BOX_HIGHT + RC_BOX_HOLDER_THICKNESS*2 # X
RC_BOX_HOLDER_WIDTH = 4 # Y
RC_BOX_HOLDER_OVERHANG = 6

x_offset = main_body.w - RC_BOX_HOLDER_OVERHANG
rc_box_holder_body = Box(
    Vector(  x_offset,                     main_body.n, 0            ),  # West, South, Down
    Vector(  x_offset+RC_BOX_HOLDER_HIGHT, main_body.n+RC_BOX_HOLDER_WIDTH, HOLDER_LENGTH)  # East, North, Up
)
z_offset = (HOLDER_LENGTH - RC_BOX_LENGTH) / 2
x_offset += RC_BOX_HOLDER_THICKNESS
y_offset = rc_box_holder_body.s
rc_box_body = Box(
    Vector(  x_offset,              y_offset+RC_BOX_HOLDER_THICKNESS, z_offset    ),  # West, South, Down
    Vector(  x_offset+RC_BOX_HIGHT, y_offset+ RC_BOX_WIDTH+RC_BOX_HOLDER_THICKNESS, z_offset+RC_BOX_LENGTH),  # East, North, Up
   # [Vector(1,1,1)]
)



RC_BOX_SLIP_HIGHT = 10 # X
RC_BOX_SLIP_HOLE = 47
RC_BOX_SLIP_WIDTH = 53 # y

RC_BOX_BACK_WIDTH = 45 # y

x_offset = rc_box_body.c
y_offset = rc_box_body.s
rc_box_slip_body = Box(
    Vector(  x_offset-RC_BOX_SLIP_HIGHT/2, y_offset, 0    ),  # West, South, Down
    Vector(  x_offset+RC_BOX_SLIP_HIGHT/2, y_offset+RC_BOX_SLIP_WIDTH, rc_box_body.d),  # East, North, Up
    [Vector(2,2,2)]
)
rc_box_back_body = Box(
    Vector(  x_offset-RC_BOX_HOLDER_HIGHT/2, y_offset, 0    ),  # West, South, Down
    Vector(  x_offset+RC_BOX_HOLDER_HIGHT/2, y_offset+RC_BOX_BACK_WIDTH, rc_box_body.d+RC_BOX_HOLDER_THICKNESS*2),  # East, North, Up
    [Vector(2,2,2)]
)
RC_BOX_NOTCH_HIGHT = 30
rc_box_back_notch = Box(
    Vector(  x_offset-RC_BOX_NOTCH_HIGHT/2, y_offset, rc_box_body.d    ),  # West, South, Down
    Vector(  x_offset+RC_BOX_NOTCH_HIGHT/2, y_offset+RC_BOX_BACK_WIDTH, rc_box_body.d+RC_BOX_HOLDER_THICKNESS*2),  # East, North, Up
)

rc_box_holder_body.solid = rc_box_holder_body.solid.fuse(rc_box_back_body.solid)
rc_box_holder_body.solid = rc_box_holder_body.solid.cut(rc_box_back_notch.solid)
rc_box_holder_body.solid = rc_box_holder_body.solid.cut(rc_box_body.solid)
rc_box_holder_body.solid = rc_box_holder_body.solid.fuse(rc_box_slip_body.solid)
notch_diameter = 3.5
notch = Polyhedron(Polygon(Vector(rc_box_slip_body.c, rc_box_slip_body.s+RC_BOX_SLIP_HOLE, rc_box_slip_body.u), notch_diameter/2, Vector(0,0,1)), 
                   Polygon(Vector(rc_box_slip_body.c, rc_box_slip_body.s+RC_BOX_SLIP_HOLE, rc_box_slip_body.u+3), notch_diameter/2, Vector(0,0,1)))

rc_box_holder_body.solid = rc_box_holder_body.solid.fuse(notch.solid)

# ecken abrunden
rc_box_holder_body.solid = rc_box_holder_body.solid.makeFillet(1.5, 
                                                               [ rc_box_holder_body.solid.Edge97, 
                                                                rc_box_holder_body.solid.Edge108, 
                                                                rc_box_holder_body.solid.Edge37])

main_body.solid = main_body.solid.fuse(rc_box_holder_body.solid)
#show(rc_box_holder_body, name="RC_Box_holder", color=(50,50,0))
#show(rc_box_body, name="RC_Box_body", color=(0,50,0))
show(main_body, name="Tragschienenhalter", color=(111,123,0))
#show(ts35_body, name="ts35_body", color=(0,123,0))
#show(ts35_groove, name="ts35_groove", color=(0,0, 123))

export('Elektrokasten', "Tragschienenhalter")
#export('Elektrokasten', "RC_Box_holder")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")