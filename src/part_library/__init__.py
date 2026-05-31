"""
part_library — parametric 3D-printable building blocks built on top of freecad_lib.

Usage::

    from src.part_library import (
        Hinge, HingeLeafA, HingeLeafB, HingePin,
        SnapFit, SnapHook, SnapReceptor,
        LivingHinge,
        CableClip,
        Standoff,
        WallBracket,
        JHook, SHook,
        Knob,
        BoxLid, EnclosureBox,
        DovetailJoint, DovetailRail, DovetailSlider,
    )
"""

from .hinge import Hinge, HingeLeafA, HingeLeafB, HingePin
from .snap_fit import SnapFit, SnapHook, SnapReceptor
from .living_hinge import LivingHinge
from .cable_clip import CableClip
from .standoff import Standoff
from .wall_bracket import WallBracket
from .hook import JHook, SHook
from .knob import Knob
from .box_lid import BoxLid, EnclosureBox
from .dovetail import DovetailJoint, DovetailRail, DovetailSlider

__all__ = [
    "Hinge",
    "HingeLeafA",
    "HingeLeafB",
    "HingePin",
    "SnapFit",
    "SnapHook",
    "SnapReceptor",
    "LivingHinge",
    "CableClip",
    "Standoff",
    "WallBracket",
    "JHook",
    "SHook",
    "Knob",
    "BoxLid",
    "EnclosureBox",
    "DovetailJoint",
    "DovetailRail",
    "DovetailSlider",
]
