# Part Library – Build Todo List

## Goal
Parametric 3D-printable part library (`src/part_library/`) built on top of `freecad_lib`.
Each part is a standalone Python module whose top-level class accepts **only dimension
parameters** and returns a `.solid` ready to cut/fuse/show/export.

---

## Todo

- [x] **01** Research & spec all parts — decide API for each module (sub-agent)
- [x] **02** `hinge.py` — Parametric barrel / pin hinge (two halves + pin hole)
- [x] **03** `snap_fit.py` — Cantilever snap-fit clip (male hook + female receptor)
- [x] **04** `living_hinge.py` — Single-print flexible living hinge strip
- [x] **05** `cable_clip.py` — Round cable / wire clip (bolt-on saddle clamp)
- [x] **06** `standoff.py` — PCB standoff / spacer with or without thread pocket
- [x] **07** `wall_bracket.py` — L-bracket / shelf bracket (parametric wall mount)
- [x] **08** `hook.py` — Wall hook (J-hook and S-hook variants)
- [x] **09** `knob.py` — Knurled thumb-screw knob for M3–M8 inserts
- [x] **10** `box_lid.py` — Snap-fit or friction-fit rectangular enclosure lid
- [x] **11** `dovetail.py` — Dovetail rail + slider (tool-less assembly joint)
- [x] **12** `__init__.py` — Re-export everything from one import

---

## Status log

| Step | File | Status | Notes |
|------|------|--------|-------|
| 01 | research.md (intermediate) | ✅ Done | specs + CSG notes for A–J |
| 02 | hinge.py | ✅ Done | HingeLeafA/B + HingePin + Hinge |
| 03 | snap_fit.py | ✅ Done | SnapHook + SnapReceptor + SnapFit |
| 04 | living_hinge.py | ✅ Done | LivingHinge with stress-relief notches |
| 05 | cable_clip.py | ✅ Done | CableClip |
| 06 | standoff.py | ✅ Done | Standoff (round/hex, flange, chamfer) |
| 07 | wall_bracket.py | ✅ Done | WallBracket with gusset |
| 08 | hook.py | ✅ Done | JHook + SHook |
| 09 | knob.py | ✅ Done | Knob (heat-set or nut-trap insert) |
| 10 | box_lid.py | ✅ Done | BoxLid + EnclosureBox |
| 11 | dovetail.py | ✅ Done | DovetailRail + DovetailSlider + DovetailJoint |
| 12 | __init__.py | ✅ Done | Single-import re-export |
