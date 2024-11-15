import FreeCAD, Part
from FreeCAD import Vector
from typing import List


from freecad_lib import *

# create new document
new_doc('Schaltschrank')


# Parameter all in mm
# 215 x 45
innen_länge = 215
innen_breite = 45

wandung = 2.5
rand = 5

länge = innen_länge + rand*2
breite = innen_breite + rand*2
höhe = 10
Abdeckung = Box(Vector(-länge/2, -breite/2, 0),
                Vector( länge/2,  breite/2, höhe))

Falz = Box(Vector(-länge/2+rand, -breite/2+rand, höhe),
           Vector( länge/2-rand,  breite/2-rand, höhe+wandung))
Aussparung = Box(Vector(-länge/2+rand*2, -breite/2+rand*2, wandung),
                 Vector( länge/2-rand*2,  breite/2-rand*2, höhe+wandung))
Abdeckung.solid = Abdeckung.solid.fuse(Falz.solid)
Abdeckung.solid = Abdeckung.solid.cut(Aussparung.solid)

# löcher für M3 schrauben
# (1) ength  : (w)est   (X-)  (s)outh  (Y-)  (d)own   (Z-)
# (b)readth  : (c)entre (X0)  (m)iddle (YO)  (g)round (Z0)
# (h) eight  : (e)ast   (X+)  (n) orth (Y+)  (u)p     (Z+)
loch_durchmesser = 2.5
for x_offset, y_offset in [
    (Abdeckung.w+rand+loch_durchmesser/2, Abdeckung.n-rand-loch_durchmesser/2),
    (Abdeckung.c                        , Abdeckung.n-rand-loch_durchmesser/2),
    (Abdeckung.e-rand-loch_durchmesser/2, Abdeckung.n-rand-loch_durchmesser/2),
    (Abdeckung.w+rand+loch_durchmesser/2, Abdeckung.s+rand+loch_durchmesser/2),
    (Abdeckung.c                        , Abdeckung.s+rand+loch_durchmesser/2),
    (Abdeckung.e-rand-loch_durchmesser/2, Abdeckung.s+rand+loch_durchmesser/2),
]:
    loch = Cylinder("loch", loch_durchmesser, -höhe, Vector(x_offset, y_offset, höhe+wandung))
    Abdeckung.solid = Abdeckung.solid.cut(loch.solid)
    #show(loch, name=loch.name)

show(Abdeckung, name="Abdeckung")


# export 
export('Schaltschrank', "Abdeckung")
# show part
FreeCAD.Gui.activeDocument().activeView().viewIsometric()
FreeCAD.Gui.SendMsgToActiveView("ViewFit")
