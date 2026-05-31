"""STL file reader -- supports both ASCII and binary formats.

Returns a ``MeshData`` object with numpy arrays for:
- unique vertex positions
- per-triangle vertex indices
- per-triangle outward unit normals

No external dependencies beyond ``numpy`` (bundled with FreeCAD).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Data container
# ---------------------------------------------------------------------------


@dataclass
class MeshData:
    """Raw triangle mesh loaded from an STL file."""

    vertices: np.ndarray  # (N, 3) float64 - unique vertex positions in mm
    faces: np.ndarray  # (M, 3) int64   - per-triangle vertex indices
    face_normals: np.ndarray  # (M, 3) float64 - outward unit normals
    source_path: str = ""

    # ------------------------------------------------------------------
    @property
    def n_vertices(self) -> int:
        return len(self.vertices)

    @property
    def n_faces(self) -> int:
        return len(self.faces)

    @property
    def bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return ``(min_xyz, max_xyz)`` as ``(3,)`` float64 arrays."""
        return self.vertices.min(axis=0), self.vertices.max(axis=0)

    @property
    def size(self) -> np.ndarray:
        """Bounding-box dimensions ``[dx, dy, dz]`` in mm."""
        lo, hi = self.bounding_box
        return hi - lo

    @property
    def face_centers(self) -> np.ndarray:
        """``(M, 3)`` centroid of each triangle."""
        return self.vertices[self.faces].mean(axis=1)

    @property
    def volume_estimate(self) -> float:
        """Signed volume via the divergence theorem (absolute value returned)."""
        v0 = self.vertices[self.faces[:, 0]]
        v1 = self.vertices[self.faces[:, 1]]
        v2 = self.vertices[self.faces[:, 2]]
        signed = np.einsum("ij,ij->i", v0, np.cross(v1, v2)) / 6.0
        return float(np.abs(signed.sum()))


# ---------------------------------------------------------------------------
# Reader
# ---------------------------------------------------------------------------


class STLReader:
    """Read ASCII or binary STL files into a :class:`MeshData` object."""

    _BINARY_HEADER_BYTES = 80
    _BINARY_TRIANGLE_BYTES = 50  # 12 (normal) + 36 (3 x vertex) + 2 (attr)
    _VERTEX_ROUND_DECIMALS = 6  # snap vertices to 1 nm grid

    @classmethod
    def read(cls, path: str | Path) -> MeshData:
        """Auto-detect format and read the file."""
        path = str(path)
        if cls._is_ascii(path):
            return cls._read_ascii(path)
        return cls._read_binary(path)

    # ------------------------------------------------------------------
    # Format detection
    # ------------------------------------------------------------------

    @classmethod
    def _is_ascii(cls, path: str) -> bool:
        """Return True when the file looks like an ASCII STL."""
        with open(path, "rb") as fh:
            header = fh.read(cls._BINARY_HEADER_BYTES)
        try:
            text = header.decode("ascii", errors="ignore").strip().lower()
            return text.startswith("solid")
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Binary reader
    # ------------------------------------------------------------------

    @classmethod
    def _read_binary(cls, path: str) -> MeshData:
        with open(path, "rb") as fh:
            fh.read(cls._BINARY_HEADER_BYTES)  # skip header
            (n_tri,) = struct.unpack("<I", fh.read(4))
            dtype = np.dtype(
                [
                    ("normal", "<3f4"),
                    ("v0", "<3f4"),
                    ("v1", "<3f4"),
                    ("v2", "<3f4"),
                    ("attr", "<u2"),
                ]
            )
            raw = np.frombuffer(
                fh.read(n_tri * cls._BINARY_TRIANGLE_BYTES), dtype=dtype
            )

        # Stack all vertex positions: shape (3*n_tri, 3)
        # Order: all v0 rows, then all v1 rows, then all v2 rows
        all_pts = np.vstack(
            [
                raw["v0"].astype(np.float64),
                raw["v1"].astype(np.float64),
                raw["v2"].astype(np.float64),
            ]
        )

        unique_verts, inv = np.unique(
            np.round(all_pts, cls._VERTEX_ROUND_DECIMALS),
            axis=0,
            return_inverse=True,
        )
        # Reconstruct face index array: (n_tri, 3) with columns [v0_idx, v1_idx, v2_idx]
        faces = np.column_stack(
            [
                inv[:n_tri],
                inv[n_tri : 2 * n_tri],
                inv[2 * n_tri :],
            ]
        )

        return MeshData(
            vertices=unique_verts,
            faces=faces,
            face_normals=cls._recompute_normals(unique_verts, faces),
            source_path=path,
        )

    # ------------------------------------------------------------------
    # ASCII reader
    # ------------------------------------------------------------------

    @classmethod
    def _read_ascii(cls, path: str) -> MeshData:
        tri_verts: list = []
        cur_verts: list = []

        with open(path, "r", errors="ignore") as fh:
            for line in fh:
                tokens = line.split()
                if not tokens:
                    continue
                kw = tokens[0].lower()
                if kw == "vertex" and len(tokens) >= 4:
                    cur_verts.append([float(t) for t in tokens[1:4]])
                elif kw == "endfacet":
                    if len(cur_verts) == 3:
                        tri_verts.append(cur_verts)
                    cur_verts = []

        if not tri_verts:
            raise ValueError(f"No triangles found in ASCII STL: {path!r}")

        tris = np.array(tri_verts, dtype=np.float64)  # (M, 3, 3)
        n_tri = len(tris)
        all_pts = tris.reshape(-1, 3)  # (3M, 3): t0v0, t0v1, t0v2, t1v0, ...

        unique_verts, inv = np.unique(
            np.round(all_pts, cls._VERTEX_ROUND_DECIMALS),
            axis=0,
            return_inverse=True,
        )
        faces = inv.reshape(n_tri, 3)

        return MeshData(
            vertices=unique_verts,
            faces=faces,
            face_normals=cls._recompute_normals(unique_verts, faces),
            source_path=path,
        )

    # ------------------------------------------------------------------
    # Normal computation
    # ------------------------------------------------------------------

    @staticmethod
    def _recompute_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Compute per-face outward unit normals from vertex positions."""
        v0 = vertices[faces[:, 0]]
        v1 = vertices[faces[:, 1]]
        v2 = vertices[faces[:, 2]]
        cross = np.cross(v1 - v0, v2 - v0)
        lengths = np.linalg.norm(cross, axis=1, keepdims=True)
        lengths = np.where(lengths < 1e-12, 1.0, lengths)  # avoid division by zero
        return cross / lengths
