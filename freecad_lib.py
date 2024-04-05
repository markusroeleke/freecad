

import FreeCAD, Part
from FreeCAD import Vector
from typing import List
import functools

# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)


class Flat:
    def __init__(self, vertices: List[Vector], joints: List[Vector] = [], normal = Vector(0, 0, 0)):
        self.v = vertices
        #print(vertices)
        #print(joints)

        self.joints = joints
        self.normal = normal

        bc = 0.55228474983079 #bezier curve coefficient (https://spencermortensen.com/articles/bezier-circle/)
        edges = []
        if len(self.joints) < len(self.v):
            for k in range (len(self.joints), len(self.v)) :
                self.joints.append(Vector(0, 0, 0))
        if self.v[0] == self.v[-1]:
            vector = self.v[-1] - self.v[-2]
            vertexC = self.v[-1] + (self.joints[-1].dot(vector) /vector.Length *vector.normalize () )
            vertexD = vertexC + (bc * (self.v[-1] -vertexC))
        for k in range (1, len(self.v)):
            vector = self.v[k] -self.v[k-1]
            vertexB = self.v[k-1] + (self.joints[k-1].dot(vector) /vector.Length *vector.normalize () )
            vertexA = vertexB + (bc * (self.v[k-1] - vertexB))
            if not self.joints[k-1].isEqual(Vector(0, 0, 0), 0):
                curve = Part.BezierCurve()
                curve.setPoles([vertexC, vertexD, vertexA, vertexB])
                edges.append(curve.toShape())
            vertexC = self.v[k] + (self.joints[k].dot(vector)/vector.Length * vector.normalize ())
            if not vertexB.isEqual(vertexC, 0) :
                edges.append(Part.LineSegment(vertexB, vertexC).toShape())
            vertexD = vertexC + (bc * (self.v[k] -vertexC))
        #print(edges)
        self.wire = Part.Wire(edges)
        #print(self.wire)
        self.face = Part.Face(self.wire)
        if self.normal.isEqual(Vector(0, 0, 0), 0):
            self.normal = self.face.normalAt(0, 0)

# Vectors (v) : (x), (y), (2)
class Box:
    def __init__ (self, vWSD, vENU, joints=[]):
        
        self.vWSD = vWSD
        self.vENU = vENU
        self.joints = joints
        if len(self.joints) == 1:
            self.joints.append(Vector(-self.joints[0].x, self.joints[0].y, 0))
            self.joints.append(Vector(-self.joints[0].x,-self.joints[0].y, 0))
            self.joints.append(Vector( self.joints[0].x,-self.joints[0].y, 0))
        if len(self.joints) == 4:
            self.joints.append(self.joints[0])
        self.vESD = Vector(self.vENU.x, self.vWSD.y, self.vWSD.z)
        self.vEND = Vector(self.vENU.x, self.vENU.y, self.vWSD.z)
        self.vWND = Vector(self.vWSD.x, self.vENU.y, self.vWSD.z)
        self.vWNU = Vector(self.vWSD.x, self.vENU.y, self.vENU.z)
        self.vWSU = Vector(self.vWSD.x, self.vWSD.y, self.vENU.z)
        self.vESU = Vector(self.vENU.x, self.vWSD.y, self.vENU.z)
        self.w = self.vWSD.x
        self.e = self.vENU.x
        self.s = self.vWSD.y
        self.n = self.vENU.y
        self.d = self.vWSD.z
        self.u = self.vENU.z
        self.c = (self.vWSD.x + self.vENU.x)/2
        self.m = (self.vWSD.y + self.vENU.y)/2
        self.g = (self.vWSD.z + self.vENU.z)/2
        self.l = abs(self.vENU.x - self.vWSD.x)
        self.b = abs(self.vENU.y - self.vWSD.y)
        self.h = abs(self.vENU.z - self.vWSD.z)
        self.vCMG = Vector(self.c, self.m, self.g)

        # create edges
        flat = Flat([self.vWSD, self.vESD, self.vEND, self.vWND, self.vWSD], self.joints)
        self.solid = flat.face.extrude(Vector(0, 0, self.vENU.z-self.vWSD.z))

class Polygon:
    def __init__ (self, center:Vector, radius, normal, sides=1, twist=0):
        self.center = center
        self.radius = radius
        self.normal = normal
        self.sides = sides 
        self.twist = twist


        circle = Part.Circle(self.center, self. normal, self.radius)
        circle.rotate(FreeCAD.Placement(self.center, self.normal, self.twist)) 
        self.v = [self.center + (circle.XAxis *self.radius)]
        self.j = []
        self.wire = Part.Wire(circle.toShape())
        if self.sides > 1:
            self.v = circle.discretize(Number = self.sides +1)
            self.wire = Flat(self.v).wire
        for k in self.v:
            self.j.append(Vector (0, 0, 0))
        self.face = Part.Face(self.wire)

class Polyhedron:
    def __init__ (self, polygon1:Polygon, polygon2:Polygon):
        self.polygon1 = polygon1
        self.polygon2 = polygon2
        self.h = polygon2.center.z - polygon1.center.z
        self.wire1 = polygon1.wire
        self.wire2 = polygon2.wire
        self.solid = Part.makeLoft([self.wire1, self.wire2], True, True)

class SolidText:
    def __init__(self, text, position=Vector(0,0,0), height=-1, txt_height=6, spacing = 0.5):
        self.position = position
        self.height = height
        self.txt_height = txt_height
        self.text = text
        font = "tc_lasersans.ttf"
        fontdir = "/Users/Markus/Documents/Projekte/FreeCAD/fonts/"
        wire_lists = Part.makeWireString(text, fontdir, font, self.txt_height, spacing)
        self.faces = [Part.Face(wire) for wires in wire_lists for wire in wires]
        #print(self.faces)
        #self.face = fusePartList([fusePartList() for c in self.wire_lists])
        def fusePartList(l):
            return functools.reduce(lambda a,b : a.fuse(b), l)
        self.solids = [face.extrude(Vector(0, 0, self.height)) for face in self.faces]
        self.solid = fusePartList(self.solids)
        self.solid.Placement = FreeCAD.Placement(self.position, FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))