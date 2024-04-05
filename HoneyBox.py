import FreeCAD, Part
from FreeCAD import Vector
from typing import List

# create new document
doc_name = 'HoneyBox'
FreeCAD.newDocument(doc_name)
FreeCAD.Gui.runCommand('Std_DrawStyle',6) #shaded wireframe

from freecad_lib import *
from freecad_lib import SolidText

clearance = {"very_loose":  Vector(1.5, 1.5, 1.5),
             "loose":       Vector(1, 1, 1),
             "middle":      Vector(0.6, 0.6, 0.6),
             "tight":       Vector(0.2, 0.2, 0.2)
             }

yellow = (247/255, 197/255, 79/255)
brown = (123/255, 83/255, 60/255)
# draw honey glas
glas_radius = 82/2
glas_height = 97
lid_hight = 15

def draw_honey_glas(glas_radius, glas_height, lid_hight, position):
    p = position
    glas = Polyhedron(Polygon(p+Vector(0, 0, 0), glas_radius, Vector(0,1,0)), 
                        Polygon(p+Vector(0,glas_height-lid_hight, 0), glas_radius, Vector(0,1,0)))
    honeyGlasFeature = Part.show(glas.solid, 'HoneyGlas')
    #honeyGlasFeature.ViewObject.Transparency = 5
    honeyGlasFeature.ViewObject.ShapeColor = (255/255,195/255,11/255)

    lid = Polyhedron(Polygon(p+Vector(0, glas_height-lid_hight, 0), glas_radius, Vector(0,1,0)), 
                        Polygon(p+Vector(0,glas_height, 0), glas_radius, Vector(0,1,0)))
    honeyGlasLidFeature = Part.show(lid.solid, 'HoneyGlasLid')
    #honeyGlasLidFeature.ViewObject.Transparency = 5
    honeyGlasLidFeature.ViewObject.ShapeColor = (204/255.0,119/255.0,34/255)



# Parameter all in mm
wall_thikness = 10
overlap = 25
lidThickness = 10

boxHight = 130 + lidThickness
boxWidth = boxHight + overlap
boxLength = boxWidth+overlap
outerBody = Box(Vector(-boxLength/2, -boxWidth/2, 0), 
                Vector(boxLength/2, boxWidth/2, boxHight), [Vector(15,15,0)])
body = outerBody.solid

# inner clearance

innerClearance = Box(outerBody.vWSD + Vector(wall_thikness+overlap, wall_thikness, wall_thikness), 
                     outerBody.vENU + Vector(-wall_thikness, -wall_thikness, 0), [Vector(15,15,0)])

body = body.cut(innerClearance.solid)

# adding mounting holes
moutingHole_diameter = 5.5

for pos in [Vector(innerClearance.w+wall_thikness*3, innerClearance.n-wall_thikness*3, 0), 
            Vector(innerClearance.w+wall_thikness*3, innerClearance.s+wall_thikness*3, 0), 
            Vector(innerClearance.e-wall_thikness*3, innerClearance.n-wall_thikness*3, 0), 
            Vector(innerClearance.e-wall_thikness*3, innerClearance.s+wall_thikness*3, 0)]:
    moutingHole = Polyhedron(Polygon(Vector(0, 0, 0) + pos, moutingHole_diameter/2, Vector(0,0,1)), 
                            Polygon(Vector(0, 0, wall_thikness)+pos, moutingHole_diameter/2, Vector(0,0,1))
                    )
    body = body.cut(moutingHole.solid)
# lid and lid clearance
lidHeight = innerClearance.b
lidWidth = innerClearance.l+overlap


lidClearance = Box(Vector(-lidWidth/2, -lidHeight/2 , innerClearance.u - lidThickness), 
                     Vector(lidWidth/2, lidHeight/2, innerClearance.u), [Vector(15,15,0)])

body = body.cut(lidClearance.solid)


# honey box lid
lid = Box(Vector(-lidWidth/2 , -lidHeight/2 , innerClearance.u - lidThickness) + clearance['loose']/2, 
          Vector(lidWidth/2, lidHeight/2, innerClearance.u) - clearance['loose']/2, [Vector(15,15,0)])
lidBody = lid.solid
#lidBody = lidBody.makeFillet(2, lidBody.Edges)

lidHoleHeight = lidHeight - 20
lidHoleWidth = 5
for x in range(-40, 60, 20):
    lidHole = Box(Vector(-lidHoleWidth/2 + x, -lidHoleHeight/2, lid.d ), 
                  Vector(lidHoleWidth/2 + x, lidHoleHeight/2 , lid.u), [Vector(2,2,0)])
    lidBody = lidBody.cut(lidHole.solid)

# adding lid hook
hook_width = 20.5
hook_hight = 36
hook_plate_thicknes = 1.5
hanger_thickness = 3
hanger_hight = 27
hole_thickness = Vector(hanger_thickness/2, 0, hanger_thickness/2)
hook_position = Vector(lid.w + overlap/2 , lid.m, lid.d)

hook_plate = Box(Vector(-hook_width/2, -hook_hight/2, 0) + hook_position, 
           Vector(hook_width/2, hook_hight/2 , -hook_plate_thicknes) + hook_position)
hanger = Box(Vector(-hook_width/2, -hanger_thickness/2, 0) + hook_position, 
             Vector(hook_width/2, hanger_thickness/2 , -hanger_hight) + hook_position, [Vector(1,1,1)])
hangerHole = Box(Vector(-hook_width/2, -hanger_thickness/2, 0) + hook_position +  Vector(hanger_thickness/2, 0, hanger_thickness/2), 
             Vector(hook_width/2, hanger_thickness/2 , -hanger_hight) + hook_position -  Vector(hanger_thickness/2, 0, -hanger_thickness/2))
hookBody = hook_plate.solid
hookBody= hookBody.fuse(hanger.solid)
hookBody = hookBody.cut(hangerHole.solid)

# adding hock clearance
hookClearance = Box(Vector(-overlap/2, -hook_hight/2-clearance['very_loose'].y, 0) + hook_position, 
                    Vector(overlap/2, hook_hight/2+clearance['very_loose'].y, -hook_plate_thicknes-clearance['very_loose'].z) + hook_position)
hangerClearance = Box(Vector(-overlap/2, -hanger_thickness, 0) + hook_position, 
                      Vector(overlap/2, hanger_thickness , -hanger_hight-clearance['very_loose'].z) + hook_position)
hookClearanceBody = hookClearance.solid.fuse(hangerClearance.solid)
body = body.cut(hookClearanceBody)
lidBody = lidBody.cut(hookClearanceBody)
# adding hinge hole

hinge_diameter = 4.1
hinge_distance = 10
hingeHole = Polyhedron(Polygon(Vector(lid.e-lid.h, -boxWidth, lid.g), hinge_diameter/2, Vector(0,1,0)), 
                       Polygon(Vector(lid.e-lid.h, boxWidth, lid.g), hinge_diameter/2, Vector(0,1,0))
                   )
hinge_diameter = 4.5
hingeHoleLid = Polyhedron(Polygon(Vector(lid.e-lid.h, -boxWidth, lid.g), hinge_diameter/2, Vector(0,1,0)), 
                       Polygon(Vector(lid.e-lid.h, boxWidth, lid.g), hinge_diameter/2, Vector(0,1,0))
                   )
body = body.cut(hingeHole.solid)
lidBody = lidBody.cut(hingeHoleLid.solid)


# lock
lock_width = 73
lock_height = 58
lock_depth = 13
lock_distance = 6.5
z_offset = hook_plate.d - lock_distance

lock_clearance_west = hook_plate.c - lock_depth/2
lock_clearance_east = innerClearance.w - 2
lockClearance = Box(Vector(lock_clearance_west, -lock_height/2 - clearance['loose'].y, outerBody.d), 
                    Vector(lock_clearance_east,  lock_height/2 + clearance['loose'].y, lidClearance.u))

x_offset = lockClearance.w  + lock_depth/2 
lock = Box(Vector(-lock_depth/2 +x_offset, -lock_height/2 , z_offset - lock_width), 
           Vector(lock_depth/2+x_offset, lock_height/2 , z_offset), [Vector(2,2,2)])

# add lock cable clearance
cableClearanceWidth = 5
cableClearanceHorizontal = Box(Vector(outerBody.w, -cableClearanceWidth/2 , 0), 
                    Vector( lockClearance.w, cableClearanceWidth/2 , cableClearanceWidth))
cableClearanceVertical = Box(Vector(lockClearance.c-cableClearanceWidth/2, outerBody.n , 0), 
                             Vector( lockClearance.c+cableClearanceWidth/2, outerBody.s , cableClearanceWidth))
body = body.cut(lockClearance.solid).cut(cableClearanceHorizontal.solid).cut(cableClearanceVertical.solid)


# rivet hole in hook and lid
rivet_hole_diameter = 4.4
for y in [12.5, -12.5]:
    rivetHole1 = Polyhedron(Polygon(Vector(hook_plate.c, hook_plate.m+y, lid.u), rivet_hole_diameter/2, Vector(0,0,1)), 
                           Polygon(Vector(hook_plate.c, hook_plate.m+y, hook_plate.d), rivet_hole_diameter/2, Vector(0,0,1)))
    lidBody = lidBody.cut(rivetHole1.solid)

    rivetHole3 = Polyhedron(Polygon(Vector(hook_plate.c, hook_plate.m+y, lid.u), rivet_hole_diameter, Vector(0,0,1)), 
                           Polygon(Vector(hook_plate.c, hook_plate.m+y, lid.u-rivet_hole_diameter), rivet_hole_diameter, Vector(0,0,1)))
    lidBody = lidBody.cut(rivetHole3.solid)
    hookBody = hookBody.cut(rivetHole1.solid)
    rivetHole2 = Polyhedron(Polygon(Vector(hook_plate.c, hook_plate.m+y, hook_plate.d), rivet_hole_diameter, Vector(0,0,1)), 
                           Polygon(Vector(hook_plate.c, hook_plate.m+y, lockClearance.u), rivet_hole_diameter, Vector(0,0,1)))
    
    body = body.cut(rivetHole2.solid)
    
# M4 Holes for hook
screw_hole_diameter = 4.5
for y, z in [(36.5/2, -6.5), (-36.5/2, -6.5), (0, -36)]:
    screwHole = Polyhedron(Polygon(Vector(outerBody.w , lock.m+y, lock.u+z), screw_hole_diameter/2, Vector(1,0,0)), 
                           Polygon(Vector(lockClearance.w , lock.m+y, lock.u+z), screw_hole_diameter/2, Vector(1,0,0)))
    body = body.cut(screwHole.solid)
    screwHole = Polyhedron(Polygon(Vector(outerBody.w , lock.m+y, lock.u+z), screw_hole_diameter, Vector(1,0,0)), 
                           Polygon(Vector(outerBody.w + screw_hole_diameter, lock.m+y, lock.u+z), screw_hole_diameter, Vector(1,0,0)))
    body = body.cut(screwHole.solid)

# bodyFeature = Part.show(screwHole.solid, 'screwHole')
# bodyFeature.ViewObject.Transparency = 50
# bodyFeature.ViewObject.ShapeColor = (0,1,1)

bodyFeature = Part.show(lock.solid, 'Lock')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (1,1,1)

# show bframe
bodyFeature = Part.show(body, 'HoneyBoxBody')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = brown

bodyFeature = Part.show(lidBody, 'HoneyBoxLid')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = yellow

bodyFeature = Part.show(hookBody, 'Hook')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (0.50,0.40,0.80)

#draw_honey_glas(glas_radius, glas_height, lid_hight, Vector(innerClearance.c,innerClearance.s,innerClearance.g-lidClearance.h/2))

# draw coin box body
offset = Vector(-boxLength, 0, 0)
coinBox = Box(Vector(-boxLength/2, -boxWidth/2, 0) + offset, 
              Vector(boxLength/2, boxWidth/2, boxHight) + offset,
              [Vector(15,15,0)]
              )
coinBoxBody = coinBox.solid

# inner clearance
coinBoxInnerClearance = Box(coinBox.vWSD + Vector(wall_thikness, wall_thikness, wall_thikness), 
                            coinBox.vENU + Vector(-wall_thikness, -wall_thikness, 0),
                            [Vector(15,15,0)]
                            )
coinBoxBody = coinBoxBody.cut(coinBoxInnerClearance.solid)

coinBoxLid = Box(coinBoxInnerClearance.vWSU + clearance['loose']/2 + Vector(0, 0, -lidThickness), 
                 coinBoxInnerClearance.vENU - clearance['loose']/2, [Vector(15,15,0)])
coinBoxLidBody = coinBoxLid.solid
#coinBoxLidBody = coinBoxLidBody.makeFillet(2, coinBoxLidBody.Edges)

#coinBoxSouthClearance = Box(coinBox.vWSD + Vector(wall_thikness*2, wall_thikness, wall_thikness), 
                            #coinBox.vESU + Vector(-wall_thikness*2, -wall_thikness, 0))
#coinBoxBody = coinBoxBody.cut(coinBoxSouthClearance.solid)

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)

# coin acceptor
ca_dim = Vector(40, 110, 120)
ca_offset = Vector(40, 0, 0)
ca_pos = Vector(coinBoxLid.c, coinBoxLid.m, coinBoxLid.u) + ca_offset
ca = Box(Vector(-ca_dim.x/2, -ca_dim.y/2, 0) + ca_pos,
         Vector(ca_dim.x/2, ca_dim.y/2, -ca_dim.z) + ca_pos)
caBody = ca.solid

cap_dim = Vector(65, 123, 6)
cap = Box(Vector(-cap_dim.x/2, -cap_dim.y/2, cap_dim.z) + ca_pos,
          Vector(cap_dim.x/2, cap_dim.y/2, 0) + ca_pos)
capBody = cap.solid
capBody = capBody.makeFillet(2, [ capBody.Edge3, capBody.Edge6, capBody.Edge9, capBody.Edge11])

pcb_dim = Vector(60, 31, 2)
pcb_offset = Vector(-40, 20, 0)
pcb_pos = Vector(coinBoxLid.c, coinBoxLid.m, coinBoxLid.d) + pcb_offset
pcb = Box(Vector(-pcb_dim.x/2, -pcb_dim.y/2, -pcb_dim.z) + pcb_pos,
          Vector(pcb_dim.x/2, pcb_dim.y/2, 0) + pcb_pos)
pcbBody = pcb.solid

pcbDisplay_dim = Vector(30, 20, lidThickness)
pcbDisplay_offset = Vector(0, 0, 0)
pcbDisplay_pos = Vector(pcb.c, pcb.m, pcb.u) + pcbDisplay_offset
pcbDisplayClearance = Box(Vector(-pcbDisplay_dim.x/2, -pcbDisplay_dim.y/2, pcbDisplay_dim.z) + pcbDisplay_pos,
                           Vector(pcbDisplay_dim.x/2, pcbDisplay_dim.y/2, 0) + pcbDisplay_pos)
pcbDisplayClearanceBody = pcbDisplayClearance.solid
# cut out cleance over 
coinBoxLidBody = coinBoxLidBody.cut(pcbDisplayClearanceBody)
coinBoxLidBody = coinBoxLidBody.makeFillet(lidThickness-3, [ coinBoxLidBody.Edge25, 
                                                          coinBoxLidBody.Edge26, 
                                                          coinBoxLidBody.Edge27, 
                                                          coinBoxLidBody.Edge28])


# 73 mm x 50 mm x 18,5 mm
relais_dim = Vector(50, 73, 18.5)
relais_offset = Vector(-40, 0, 0)
relais_pos = Vector(coinBoxInnerClearance.c, coinBoxInnerClearance.m, coinBoxInnerClearance.d) + relais_offset
relais = Box(Vector(-relais_dim.x/2, -relais_dim.y/2, relais_dim.z) + relais_pos,
          Vector(relais_dim.x/2, relais_dim.y/2, 0) + relais_pos)
relaisBody = relais.solid

honigText = SolidText("Honig 7€", Vector(pcbDisplayClearance.w-20, coinBoxLid.n - 25, coinBoxLid.u))
coinBoxLidBody = coinBoxLidBody.cut(honigText.solid)

#txtFeature = Part.show(honigText.solid, 'HonigText')

bodyFeature = Part.show(coinBoxBody, 'CoinBoxBody')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = brown

bodyFeature = Part.show(coinBoxLidBody, 'CoinBoxLid')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = yellow

bodyFeature = Part.show(caBody, 'CoinAcceptor')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (1,1,1)

bodyFeature = Part.show(capBody, 'CoinAcceptorPlate')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (0xc0/255,0xc0/255,0xc0/255)

bodyFeature = Part.show(pcbBody, 'CoinBoxPcb')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (0/255.0, 0x8C/255.0, 0x4A/255.0)

bodyFeature = Part.show(relaisBody, 'CoinBoxRelais')
bodyFeature.ViewObject.Transparency = 50
bodyFeature.ViewObject.ShapeColor = (0/255.0, 0x8C/255.0, 0x4A/255.0)

# export 
import Mesh

for obj in ["HoneyBoxBody", "HoneyBoxLid", "CoinBoxBody"]:
    Mesh.export([FreeCAD.getDocument("HoneyBox").getObject(obj)], 
                f"/Users/Markus/Documents/Projekte/FreeCAD/stl/{obj}.stl")

# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")