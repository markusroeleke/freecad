"""Unit tests for the reverse-engineering pipeline.

Run from the repo root (or from src/reverse_engineering/):

    python src/reverse_engineering/test_reverse_engineer.py
    python test_reverse_engineer.py          # if CWD is src/reverse_engineering

No pytest / unittest dependency -- uses stdlib only.  Compatible with both
a stand-alone Python installation and FreeCAD's bundled interpreter.

Exit code: 0 = all passed, 1 = at least one failure.
"""

from __future__ import annotations

import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
for _p in (_HERE, _HERE.parent.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from stl_reader import STLReader, MeshData
from mesh_analyzer import MeshAnalyzer, PlaneFeature, CylinderFeature
from primitive_fitter import PrimitiveFitter, FitResult, BoxPrimitive
from code_generator import CodeGenerator
from reverse_engineer import reverse_engineer

# Root of the workspace (two levels above src/reverse_engineering/)
_REPO = _HERE.parent.parent
_STL_DIR = _REPO / "stl"

# ---------------------------------------------------------------------------
# Minimal test framework
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_SKIP = "SKIP"


class _TestResult:
    def __init__(self, name: str, status: str, detail: str = ""):
        self.name = name
        self.status = status
        self.detail = detail

    def __str__(self) -> str:
        tag = f"[{self.status}]"
        line = f"{tag:8s} {self.name}"
        if self.detail:
            line += f"\n         {self.detail}"
        return line


_results: List[_TestResult] = []


def _test(name: str):
    """Decorator: run the function and record PASS / FAIL."""

    def decorator(fn: Callable):
        try:
            fn()
            _results.append(_TestResult(name, _PASS))
        except AssertionError as exc:
            _results.append(_TestResult(name, _FAIL, str(exc)))
        except Exception:
            _results.append(_TestResult(name, _FAIL, traceback.format_exc().strip()))
        return fn

    return decorator


def _assert_close(a: float, b: float, tol: float = 0.5, msg: str = ""):
    assert (
        abs(a - b) <= tol
    ), f"{msg + ': ' if msg else ''}expected ~{b:.3f}, got {a:.3f}  (tol +/-{tol})"


def _stl(name: str) -> Path:
    p = _STL_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"STL not found: {p}")
    return p


# ---------------------------------------------------------------------------
# STLReader tests
# ---------------------------------------------------------------------------


@_test("STLReader: detect binary format")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    assert mesh.n_faces > 0, "No triangles loaded"
    assert mesh.n_vertices > 0, "No vertices loaded"


@_test("STLReader: bounding box lasche 10x10x3 mm")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    lo, hi = mesh.bounding_box
    sz = hi - lo
    _assert_close(sz[0], 10.0, 0.2, "X size")
    _assert_close(sz[1], 10.0, 0.2, "Y size")
    _assert_close(sz[2], 3.0, 0.2, "Z size")


@_test("STLReader: face normals are unit vectors")
def _():
    import numpy as np

    mesh = STLReader.read(_stl("lasche.stl"))
    lengths = np.linalg.norm(mesh.face_normals, axis=1)
    assert (abs(lengths - 1.0) < 1e-4).all(), "Normals are not unit vectors"


@_test("STLReader: face indices in valid range")
def _():
    mesh = STLReader.read(_stl("platte.stl"))
    assert mesh.faces.min() >= 0
    assert mesh.faces.max() < mesh.n_vertices


@_test("STLReader: face_centers shape")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    assert mesh.face_centers.shape == (mesh.n_faces, 3)


# ---------------------------------------------------------------------------
# MeshAnalyzer tests
# ---------------------------------------------------------------------------


@_test("MeshAnalyzer: detect_planar_regions returns list")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    planes = MeshAnalyzer(mesh).detect_planar_regions()
    assert isinstance(planes, list)
    assert len(planes) > 0, "No planar regions found"


@_test("MeshAnalyzer: lasche has top and bottom planes (Z-aligned)")
def _():
    import numpy as np

    mesh = STLReader.read(_stl("lasche.stl"))
    planes = MeshAnalyzer(mesh).detect_planar_regions()
    z_aligned = [p for p in planes if abs(abs(float(p.normal[2])) - 1.0) < 0.1]
    assert len(z_aligned) >= 2, f"Expected >=2 Z-aligned planes, got {len(z_aligned)}"


@_test("MeshAnalyzer: detect_cylinders returns list")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    cyls = MeshAnalyzer(mesh).detect_cylinders()
    assert isinstance(cyls, list)


@_test("MeshAnalyzer: cluster_by_normal covers all faces")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    clusters = MeshAnalyzer(mesh).cluster_by_normal()
    covered = sum(len(c) for c in clusters)
    assert covered == mesh.n_faces, f"Clustering covered {covered}/{mesh.n_faces} faces"


# ---------------------------------------------------------------------------
# PrimitiveFitter tests
# ---------------------------------------------------------------------------


@_test("PrimitiveFitter: FitResult has bounding_box")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    result = PrimitiveFitter().fit(mesh)
    assert result.bounding_box is not None
    assert result.bounding_box.length > 0
    assert result.bounding_box.breadth > 0
    assert result.bounding_box.height > 0


@_test("PrimitiveFitter: lasche bounding box ~10x10x3 mm")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    result = PrimitiveFitter().fit(mesh)
    bb = result.bounding_box
    _assert_close(bb.length, 10.0, 0.3, "length")
    _assert_close(bb.breadth, 10.0, 0.3, "breadth")
    _assert_close(bb.height, 3.0, 0.3, "height")


@_test("PrimitiveFitter: platte bounding box ~72x80x6 mm")
def _():
    mesh = STLReader.read(_stl("platte.stl"))
    result = PrimitiveFitter().fit(mesh)
    bb = result.bounding_box
    _assert_close(bb.length, 72.0, 0.5, "length")
    _assert_close(bb.breadth, 80.0, 0.5, "breadth")
    _assert_close(bb.height, 6.0, 0.5, "height")


@_test("PrimitiveFitter: confidence 0-1")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    result = PrimitiveFitter().fit(mesh)
    assert 0.0 <= result.confidence <= 1.0, f"confidence={result.confidence}"


@_test("PrimitiveFitter: no inverted box primitives")
def _():
    for stl_name in ["lasche.stl", "platte.stl", "Kappe_20mm.stl"]:
        try:
            mesh = STLReader.read(_stl(stl_name))
        except FileNotFoundError:
            continue
        result = PrimitiveFitter().fit(mesh)
        for b in result.box_bodies:
            assert b.length > 0, f"{stl_name}: box length <= 0"
            assert b.breadth > 0, f"{stl_name}: box breadth <= 0"
            assert b.height > 0, f"{stl_name}: box height <= 0"


@_test("PrimitiveFitter: cylinder diameters positive")
def _():
    for stl_name in ["lasche.stl", "platte.stl"]:
        try:
            mesh = STLReader.read(_stl(stl_name))
        except FileNotFoundError:
            continue
        result = PrimitiveFitter().fit(mesh)
        for c in result.cylinders:
            assert c.diameter > 0, f"{stl_name}: cylinder diameter <= 0"
            assert c.height > 0, f"{stl_name}: cylinder height <= 0"


# ---------------------------------------------------------------------------
# CodeGenerator tests
# ---------------------------------------------------------------------------


@_test("CodeGenerator: output is non-empty string")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    result = PrimitiveFitter().fit(mesh)
    code = CodeGenerator().generate(result)
    assert isinstance(code, str)
    assert len(code) > 100


@_test("CodeGenerator: output contains new_doc call")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    result = PrimitiveFitter().fit(mesh)
    code = CodeGenerator().generate(result)
    assert "new_doc(" in code


@_test("CodeGenerator: output is valid Python (compile)")
def _():
    for stl_name in ["lasche.stl", "platte.stl", "Kappe_20mm.stl"]:
        try:
            mesh = STLReader.read(_stl(stl_name))
        except FileNotFoundError:
            continue
        result = PrimitiveFitter().fit(mesh)
        code = CodeGenerator().generate(result)
        try:
            compile(code, f"<{stl_name}>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"{stl_name}: SyntaxError in generated code: {e}")


@_test("CodeGenerator: mesh_import fallback always present")
def _():
    mesh = STLReader.read(_stl("lasche.stl"))
    result = PrimitiveFitter().fit(mesh)
    code = CodeGenerator().generate(result)
    assert "mesh_import" in code, "mesh_import fallback missing"


# ---------------------------------------------------------------------------
# End-to-end / integration tests
# ---------------------------------------------------------------------------


@_test("reverse_engineer: writes output file")
def _():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "test_output.py"
        reverse_engineer(_stl("lasche.stl"), out, verbose=False)
        assert out.exists(), "Output file was not created"
        content = out.read_text(encoding="utf-8")
        assert len(content) > 100


@_test("reverse_engineer: returns FitResult")
def _():
    result = reverse_engineer(_stl("lasche.stl"), verbose=False)
    assert isinstance(result, FitResult)


@_test("reverse_engineer: raises FileNotFoundError for missing STL")
def _():
    raised = False
    try:
        reverse_engineer("does_not_exist.stl", verbose=False)
    except FileNotFoundError:
        raised = True
    assert raised, "Expected FileNotFoundError was not raised"


@_test("Integration: all STL files in stl/ run without exception")
def _():
    failures: List[str] = []
    for stl_file in sorted(_STL_DIR.glob("*.stl")):
        try:
            result = reverse_engineer(stl_file, verbose=False)
        except Exception as exc:
            failures.append(f"{stl_file.name}: {exc}")
    if failures:
        raise AssertionError(
            f"{len(failures)} STL(s) failed:\n  " + "\n  ".join(failures)
        )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def _run():
    print("=" * 60)
    print("Reverse Engineering - Unit Tests")
    print("=" * 60)

    passed = [r for r in _results if r.status == _PASS]
    failed = [r for r in _results if r.status == _FAIL]
    skipped = [r for r in _results if r.status == _SKIP]

    for r in _results:
        print(r)

    print()
    print(
        f"Results: {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped"
    )
    print("=" * 60)

    return len(failed)


if __name__ == "__main__":
    # Force UTF-8 output on Windows consoles that default to cp1252
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
    sys.exit(_run())
