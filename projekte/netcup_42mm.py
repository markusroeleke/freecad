"""
Netcup für hydroponische Systeme - 44mm Loch
Aufgebaut in 3 Schritten: Flansch → Becher → Drainagelöcher
"""

import FreeCAD, Part, FreeCADGui, Mesh
from FreeCAD import Vector
import math

# Create new document
doc_name = "NetCup44"
FreeCAD.newDocument(doc_name)
FreeCAD.Gui.runCommand("Std_DrawStyle", 6)

from src.freecad_lib import *

# ================================
# Parameter
# ================================

# Abmessungen (alle in mm)
bottom_outer_dia = 42  # Außen unten (passt in 44mm Loch)
top_outer_dia = 35  # Außen oben (konisch verjüngt)
inner_wall_thickness = 1  # Wanddicke
height = 50  # Höhe Becher

# Flansch
flange_outer_dia = 52  # 52mm (21mm + 5mm = 26mm Radius)
flange_inner_hole_dia = bottom_outer_dia  # 42mm Innenloch
flange_height = 3  # 3mm Dicke
flange_bottom_inner_dia = (
    bottom_outer_dia - 2 * inner_wall_thickness
)  # 40mm - hier sitzt Flansch innen auf

# Drainagelöcher
drainage_hole_dia = 12
num_drainage_holes = 8
drain_height = 8

# ===================================================================
# SCHRITT 1: FLANSCH MIT INNENLOCH
# ===================================================================
print("SCHRITT 1: Flansch erstellen...")

flange_outer_radius = flange_outer_dia / 2  # 26mm
flange_inner_hole_radius = flange_inner_hole_dia / 2  # 24mm
flange_bottom_inner_radius = flange_bottom_inner_dia / 2  # 20mm

# Flansch als Ring: Großer Zylinder minus kleiner Zylinder
flange_outer_cyl = Part.makeCylinder(
    flange_outer_radius, flange_height, Vector(0, 0, -flange_height), Vector(0, 0, 1)
)

# Innenloch des Flansches
flange_hole_cyl = Part.makeCylinder(
    flange_inner_hole_radius,
    flange_height + 2,
    Vector(0, 0, -flange_height - 1),
    Vector(0, 0, 1),
)

# Flansch-Ring
flansch = flange_outer_cyl.cut(flange_hole_cyl)

# ===================================================================
# SCHRITT 2: KONISCHER HAUPTKÖRPER
# ===================================================================
print("SCHRITT 2: Konischer Becher erstellen...")

bottom_outer_radius = bottom_outer_dia / 2  # 21mm
top_outer_radius = top_outer_dia / 2  # 17.5mm
bottom_inner_radius = flange_bottom_inner_dia / 2  # 20mm
top_inner_radius = top_outer_dia / 2 - inner_wall_thickness  # 16.5mm
top_inner_radius_hole = top_outer_dia / 4  # 15mm - hier sitzt obere Platte innen auf
# Außenkegel
outer_cone = Part.makeCone(
    bottom_outer_radius, top_outer_radius, height, Vector(0, 0, 0), Vector(0, 0, 1)
)

# Innenkegel (Hohlraum)
inner_cone = Part.makeCone(
    bottom_inner_radius,
    top_inner_radius,
    height - inner_wall_thickness,
    Vector(0, 0, 0),
    Vector(0, 0, 1),
)

# Hohler Kegel
becher = outer_cone.cut(inner_cone)

# Boden des Bechers (fester Boden mit 1mm Dicke)
bottom_plate_outer = Part.makeCylinder(
    bottom_outer_radius, inner_wall_thickness, Vector(0, 0, 0), Vector(0, 0, 1)
)

bottom_plate_inner = Part.makeCylinder(
    bottom_inner_radius, inner_wall_thickness, Vector(0, 0, 0), Vector(0, 0, 1)
)

# Boden zusammensetzen (Ring am äußeren Rand)
bottom_ring = bottom_plate_outer.cut(bottom_plate_inner)
becher = becher.fuse(bottom_ring)

upper_plate_inner = Part.makeCylinder(
    top_inner_radius_hole,
    inner_wall_thickness,
    Vector(0, 0, height - inner_wall_thickness),
    Vector(0, 0, 1),
)
becher = becher.cut(upper_plate_inner)
# Flansch und Becher zusammensetzen
netcup_body = becher.fuse(flansch)


# ===================================================================
# SCHRITT 3: DRAINAGELÖCHER
# ===================================================================
print("SCHRITT 3: Drainagelöcher bohren...")

drainage_radius = drainage_hole_dia / 2
hole_radius_from_center = (bottom_outer_radius + bottom_inner_radius) / 2

for i in range(num_drainage_holes):
    angle = (360 / num_drainage_holes) * i
    rad = math.radians(angle)

    x = hole_radius_from_center * math.cos(rad)
    y = hole_radius_from_center * math.sin(rad)
    z = drain_height

    drill_hole = Part.makeCylinder(
        drainage_radius, height - drain_height + 2, Vector(x, y, z), Vector(0, 0, 1)
    )
    netcup_body = netcup_body.cut(drill_hole)

# ===================================================================
# ANZEIGEN UND SPEICHERN
# ===================================================================
print("")
print("✓ NetCup fertig!")
print(f"  Flansch: {flange_outer_dia}mm ⌀ mit {flange_inner_hole_dia}mm Innenloch")
print(
    f"  Becher: {bottom_outer_dia}mm ⌀ unten, {top_outer_dia}mm ⌀ oben, {height}mm hoch"
)
print(f"  Drainagelöcher: {num_drainage_holes}x {drainage_hole_dia}mm ⌀")
print("")

netcup_feature = Part.show(netcup_body, "NetCup44")
netcup_feature.ViewObject.Transparency = 30
netcup_feature.ViewObject.ShapeColor = (0.8, 0.8, 0.8)

FreeCADGui.activeDocument().activeView().viewIsometric()
FreeCADGui.SendMsgToActiveView("ViewFit")

Mesh.export(
    [FreeCAD.getDocument(doc_name).getObject("NetCup44")],
    f"/Users/Markus/Documents/Projekte/FreeCAD/stl/NetCup44.stl",
)
print("✓ STL exportiert: stl/NetCup44.stl")
