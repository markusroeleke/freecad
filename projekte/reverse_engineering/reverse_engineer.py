"""Public entry point for the reverse-engineering pipeline.

Usage
-----
From a Python script or FreeCAD macro::

    from src.reverse_engineering.reverse_engineer import reverse_engineer

    reverse_engineer(
        stl_path  = r"stl/Topfdeckelhalter.stl",
        output_py = r"projekte/Topfdeckelhalter_RE.py",
        verbose   = True,
    )

The function:
1. Reads the STL file with :class:`STLReader`.
2. Fits geometric primitives with :class:`PrimitiveFitter`.
3. Generates a ``freecad_lib`` Python script with :class:`CodeGenerator`.
4. Writes the script to *output_py* (or prints it when *output_py* is ``None``).
5. Returns the :class:`FitResult` so callers can inspect what was detected.

All paths are resolved relative to the *current working directory* unless
absolute paths are supplied.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Make sibling modules importable whether this file is run directly or imported
# ---------------------------------------------------------------------------
_DIR = Path(__file__).parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from stl_reader import STLReader, MeshData
from primitive_fitter import PrimitiveFitter, FitResult
from code_generator import CodeGenerator

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def reverse_engineer(
    stl_path: str | Path,
    output_py: Optional[str | Path] = None,
    *,
    verbose: bool = True,
) -> FitResult:
    """Reverse-engineer an STL file into a ``freecad_lib`` Python script.

    Parameters
    ----------
    stl_path:
        Path to the input ``.stl`` file.
    output_py:
        Destination ``.py`` file.  Pass ``None`` to print to stdout instead.
    verbose:
        When ``True``, print a summary of what was detected.

    Returns
    -------
    FitResult
        Structured description of all detected primitives.
    """
    stl_path = Path(stl_path)
    if not stl_path.exists():
        raise FileNotFoundError(f"STL file not found: {stl_path}")

    # -- Step 1: load mesh ----------------------------------------------------
    if verbose:
        print(f"[RE] Reading  {stl_path}")
    mesh = STLReader.read(stl_path)
    if verbose:
        lo, hi = mesh.bounding_box
        sz = hi - lo
        print(
            f"[RE] Mesh     {mesh.n_faces:,} triangles, {mesh.n_vertices:,} vertices\n"
            f"[RE] Size     {sz[0]:.2f} x {sz[1]:.2f} x {sz[2]:.2f} mm"
        )

    # -- Step 2: fit primitives -----------------------------------------------
    if verbose:
        print("[RE] Fitting primitives ...")
    result = PrimitiveFitter().fit(mesh)

    if verbose:
        print(result.summary())

    # -- Step 3: generate code ------------------------------------------------
    code = CodeGenerator().generate(result, stl_abs_path=str(stl_path.resolve()))

    # -- Step 4: write / print ------------------------------------------------
    if output_py is None:
        print("\n" + "-" * 60 + "\n")
        print(code)
    else:
        output_py = Path(output_py)
        output_py.parent.mkdir(parents=True, exist_ok=True)
        output_py.write_text(code, encoding="utf-8")
        if verbose:
            print(f"[RE] Written  {output_py.resolve()}")

    return result


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------


def _cli() -> None:
    """Minimal command-line interface: ``python reverse_engineer.py input.stl [output.py]``"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Reverse-engineer an STL into a freecad_lib Python script."
    )
    parser.add_argument("stl", help="Input STL file")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output Python file (default: print to stdout)",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    reverse_engineer(args.stl, args.output, verbose=not args.quiet)


if __name__ == "__main__":
    _cli()
