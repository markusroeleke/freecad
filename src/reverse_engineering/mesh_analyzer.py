"""Geometric analysis of a triangle mesh.

Provides two detection layers:

1. **Normal clustering** - groups triangles whose face-normals agree within an
   angle threshold.  Each cluster is a candidate planar (or cylindrical) region.

2. **Planar region detection** - verifies that every vertex in a cluster lies
   within ``plane_tol`` mm of a common plane.  Returns :class:`PlaneFeature`
   objects with normal, offset ``d``, and vertex set.

3. **Cylindrical surface detection** - for each of the three canonical axes
   (Z, X, Y) finds triangles whose normals are *perpendicular* to the axis and
   whose projected normals *span more than 180 deg* in the cross-section plane.
   Fits the cylinder centre and radius by least-squares.

No external dependencies beyond ``numpy``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

from stl_reader import MeshData

# ---------------------------------------------------------------------------
# Feature data-classes
# ---------------------------------------------------------------------------


@dataclass
class PlaneFeature:
    """An approximately planar region extracted from the mesh."""

    normal: np.ndarray  # (3,) outward unit normal
    d: float  # plane offset: normal * x = d (mm)
    vertices: np.ndarray  # (K, 3) vertices lying in this region
    face_indices: List[int]  # triangle indices that belong to this region
    area: float = 0.0  # total triangle area (mm2)

    @property
    def center(self) -> np.ndarray:
        """Centroid of the region's vertices."""
        return self.vertices.mean(axis=0)

    @property
    def is_axis_aligned(self) -> bool:
        """True when the normal is within 5 deg of +/-X, +/-Y or +/-Z."""
        return any(abs(abs(float(self.normal[i])) - 1.0) < 0.09 for i in range(3))


@dataclass
class CylinderFeature:
    """A cylindrical surface (inner or outer) detected from the mesh."""

    axis: np.ndarray  # (3,) unit vector along cylinder axis
    center: np.ndarray  # (3,) point at the *bottom* of the cylinder on the axis
    radius: float  # mm
    height: float  # mm
    face_indices: List[int]
    is_convex: bool = True  # True -> outer surface (add); False -> inner hole (cut)


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class MeshAnalyzer:
    """Detects planar and cylindrical features in a :class:`MeshData`."""

    # Normal-clustering angle tolerance (degrees)
    DEFAULT_ANGLE_TOL: float = 5.0
    # Planarity check: max allowed vertex deviation from fitted plane (mm)
    DEFAULT_PLANE_TOL: float = 0.15
    # Cylinder-axis alignment: faces whose |n * axis| < sin(this) are candidates
    CYLINDER_PERP_TOL_DEG: float = 10.0
    # Minimum arc that must be covered for something to count as a cylinder (deg)
    MIN_ARC_DEG: float = 180.0
    # Clusters smaller than this fraction of total faces are ignored
    MIN_CLUSTER_FRAC: float = 0.003

    def __init__(self, mesh: MeshData) -> None:
        self.mesh = mesh

    # ------------------------------------------------------------------
    # 1. Normal clustering
    # ------------------------------------------------------------------

    def cluster_by_normal(
        self, angle_tol_deg: float = DEFAULT_ANGLE_TOL
    ) -> List[List[int]]:
        """Return a list of face-index lists grouped by similar normal direction.

        Uses a greedy linear-scan: the first unassigned face seeds a new cluster;
        all subsequent unassigned faces within *angle_tol_deg* are added to it.
        """
        cos_tol = np.cos(np.radians(angle_tol_deg))
        normals = self.mesh.face_normals  # (M, 3)
        n_faces = normals.shape[0]
        assigned = np.zeros(n_faces, dtype=bool)
        clusters: List[List[int]] = []

        for i in range(n_faces):
            if assigned[i]:
                continue
            # Vectorised similarity check against all unassigned faces
            dots = normals @ normals[i]  # (M,)
            mask = (~assigned) & (dots > cos_tol)
            idx = np.where(mask)[0].tolist()
            for j in idx:
                assigned[j] = True
            clusters.append(idx)

        return clusters

    # ------------------------------------------------------------------
    # 2. Planar regions
    # ------------------------------------------------------------------

    def detect_planar_regions(
        self,
        angle_tol_deg: float = DEFAULT_ANGLE_TOL,
        plane_tol_mm: float = DEFAULT_PLANE_TOL,
    ) -> List[PlaneFeature]:
        """Detect approximately planar face groups."""
        clusters = self.cluster_by_normal(angle_tol_deg)
        verts = self.mesh.vertices
        faces = self.mesh.faces
        normals = self.mesh.face_normals
        min_faces = max(1, int(self.mesh.n_faces * self.MIN_CLUSTER_FRAC))

        result: List[PlaneFeature] = []

        for cluster in clusters:
            if len(cluster) < min_faces:
                continue

            face_arr = np.array(cluster, dtype=int)
            # Representative normal: mean of cluster normals
            rep_normal = normals[face_arr].mean(axis=0)
            rep_len = np.linalg.norm(rep_normal)
            if rep_len < 1e-12:
                continue
            rep_normal /= rep_len

            # Gather all unique vertices for these faces
            vert_idx = np.unique(faces[face_arr])
            region_verts = verts[vert_idx]  # (K, 3)

            # Plane offset d: normal * x = d
            d = float(np.median(region_verts @ rep_normal))

            # Planarity check
            deviations = np.abs(region_verts @ rep_normal - d)
            if deviations.max() > plane_tol_mm:
                continue

            # Triangle area
            v0 = verts[faces[face_arr, 0]]
            v1 = verts[faces[face_arr, 1]]
            v2 = verts[faces[face_arr, 2]]
            area = float(np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1).sum() / 2.0)

            result.append(
                PlaneFeature(
                    normal=rep_normal,
                    d=d,
                    vertices=region_verts,
                    face_indices=cluster,
                    area=area,
                )
            )

        return result

    # ------------------------------------------------------------------
    # 3. Cylinder detection
    # ------------------------------------------------------------------

    def detect_cylinders(
        self,
        min_arc_deg: float = MIN_ARC_DEG,
    ) -> List[CylinderFeature]:
        """Detect cylindrical surfaces by testing three canonical axes (Z, X, Y).

        Sub-clustering strategy (task 08)
        ----------------------------------
        For each axis, all perpendicular faces are first projected to 2-D and a
        global least-squares center is estimated.  Per-face radii are then
        computed from that center, and faces are grouped into *radius buckets*
        using a histogram with adaptive bin width (~ 5 % of median radius, min
        1 mm).  Each bucket that covers >= ``min_arc_deg`` of arc becomes an
        independent ``CylinderFeature`` with its own re-fitted centre and radius.
        This correctly separates, e.g., an outer boss from an inner through-hole
        that share the same axis.
        """
        results: List[CylinderFeature] = []
        sin_tol = np.sin(np.radians(self.CYLINDER_PERP_TOL_DEG))
        normals = self.mesh.face_normals  # (M, 3)
        verts = self.mesh.vertices
        faces = self.mesh.faces

        for axis_vec in [
            np.array([0.0, 0.0, 1.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
        ]:
            # -- Step 1: select perpendicular faces --------------------------
            dot_axis = np.abs(normals @ axis_vec)  # (M,)
            perp_mask = dot_axis < sin_tol
            if perp_mask.sum() < 6:
                continue

            perp_idx = np.where(perp_mask)[0]  # (k,)
            perp_n = normals[perp_idx]  # (k, 3)
            fc = self.mesh.face_centers[perp_idx]  # (k, 3)

            ref_a, ref_b = _perp_basis(axis_vec)

            n_a = perp_n @ ref_a
            n_b = perp_n @ ref_b
            c_a = fc @ ref_a
            c_b = fc @ ref_b

            n_mag = np.sqrt(n_a**2 + n_b**2)
            valid = n_mag > 0.7
            if valid.sum() < 6:
                continue

            n_a_v, n_b_v = n_a[valid], n_b[valid]
            c_a_v, c_b_v = c_a[valid], c_b[valid]
            idx_v = perp_idx[valid]
            n_mag_v = n_mag[valid]
            n_a_u = n_a_v / n_mag_v
            n_b_u = n_b_v / n_mag_v

            # -- Step 2: global LS center -------------------------------------
            A_g = np.column_stack([n_b_u, -n_a_u])
            b_g = n_b_u * c_a_v - n_a_u * c_b_v
            sol_g, _, _, _ = np.linalg.lstsq(A_g, b_g, rcond=None)
            gx, gy = float(sol_g[0]), float(sol_g[1])

            # -- Step 3: per-face radius from global center -------------------
            per_r = np.sqrt((c_a_v - gx) ** 2 + (c_b_v - gy) ** 2)  # (k_valid,)

            # -- Step 4: radius-histogram sub-clustering ----------------------
            median_r = float(np.median(per_r))
            bin_width = max(1.0, median_r * 0.08)
            r_min, r_max = per_r.min(), per_r.max()
            n_bins = max(1, int(np.ceil((r_max - r_min) / bin_width)))
            bins = np.linspace(r_min - 1e-6, r_max + 1e-6, n_bins + 1)
            bin_ids = np.digitize(per_r, bins) - 1  # 0-based

            # Merge adjacent radius bins that share a common arc into groups
            radius_groups = _merge_radius_bins(
                bin_ids,
                n_bins,
                per_r,
                bins,
                merge_gap=bin_width * 1.5,
            )

            # -- Step 5: fit one cylinder per radius group --------------------
            for group_mask in radius_groups:
                if group_mask.sum() < 4:
                    continue

                g_a_u = n_a_u[group_mask]
                g_b_u = n_b_u[group_mask]

                # Arc coverage check
                ang = np.arctan2(g_b_u, g_a_u)
                if np.degrees(_circular_span(ang)) < min_arc_deg:
                    continue

                # Re-fit centre for this sub-group
                A_s = np.column_stack([g_b_u, -g_a_u])
                b_s = g_b_u * c_a_v[group_mask] - g_a_u * c_b_v[group_mask]
                sol_s, _, _, _ = np.linalg.lstsq(A_s, b_s, rcond=None)
                sx, sy = float(sol_s[0]), float(sol_s[1])

                # Sub-group face indices back to global mesh indexing
                sub_idx = idx_v[group_mask]

                # Height from vertex extremes along axis
                sub_verts = verts[faces[sub_idx]].reshape(-1, 3)
                axis_proj = sub_verts @ axis_vec
                z_min_s = float(axis_proj.min())
                z_max_s = float(axis_proj.max())
                height_s = z_max_s - z_min_s

                center_3d = sx * ref_a + sy * ref_b + z_min_s * axis_vec

                # Refined radius: mean distance from re-fitted centre
                dr_a_s = c_a_v[group_mask] - sx
                dr_b_s = c_b_v[group_mask] - sy
                radius_s = float(np.sqrt(dr_a_s**2 + dr_b_s**2).mean())

                # Convexity
                dot_conv = (dr_a_s * g_a_u + dr_b_s * g_b_u).mean()
                is_convex = bool(dot_conv > 0)

                results.append(
                    CylinderFeature(
                        axis=axis_vec.copy(),
                        center=center_3d,
                        radius=round(radius_s, 3),
                        height=round(height_s, 3),
                        face_indices=sub_idx.tolist(),
                        is_convex=is_convex,
                    )
                )

        return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _perp_basis(axis: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return two orthonormal vectors that span the plane perpendicular to *axis*."""
    if abs(float(axis[0])) < 0.9:
        ref = np.array([1.0, 0.0, 0.0])
    else:
        ref = np.array([0.0, 1.0, 0.0])
    ref_a = ref - (ref @ axis) * axis
    ref_a /= np.linalg.norm(ref_a)
    ref_b = np.cross(axis, ref_a)
    ref_b /= np.linalg.norm(ref_b)
    return ref_a, ref_b


def _circular_span(angles: np.ndarray) -> float:
    """Return the angular arc (radians) covered by *angles* on the unit circle."""
    if len(angles) == 0:
        return 0.0
    a = np.sort(angles % (2.0 * np.pi))
    gaps = np.diff(a)
    wrap_gap = 2.0 * np.pi - (a[-1] - a[0])
    largest_gap = float(max(gaps.max() if len(gaps) else 0.0, wrap_gap))
    return float(2.0 * np.pi - largest_gap)


def _merge_radius_bins(
    bin_ids: np.ndarray,
    n_bins: int,
    per_r: np.ndarray,
    bins: np.ndarray,
    merge_gap: float = 2.0,
) -> List[np.ndarray]:
    """Group adjacent histogram bins into cylinder sub-clusters.

    Two neighbouring bins are merged when their radius gap is smaller than
    *merge_gap* mm.  Returns a list of boolean masks (one per sub-cluster)
    indexing into the input face array.

    Parameters
    ----------
    bin_ids:   Per-face bin index (0-based, shape ``(k_valid,)``).
    n_bins:    Total number of bins.
    per_r:     Per-face radius values (mm, shape ``(k_valid,)``).
    bins:      Bin edges array (``n_bins + 1`` elements).
    merge_gap: Maximum radius gap (mm) between adjacent bins to still merge them.
    """
    # Gather non-empty bins sorted by their radius
    occupied = sorted(set(int(b) for b in bin_ids))
    if not occupied:
        return []

    # Grow connected groups: merge adjacent occupied bins within merge_gap
    groups: List[List[int]] = [[occupied[0]]]
    for b in occupied[1:]:
        prev = groups[-1][-1]
        gap = float(bins[b] - bins[prev + 1])  # gap between bin edges
        if gap <= merge_gap:
            groups[-1].append(b)
        else:
            groups.append([b])

    # Build boolean mask for each group
    masks: List[np.ndarray] = []
    for group_bins in groups:
        mask = np.zeros(len(bin_ids), dtype=bool)
        for b in group_bins:
            mask |= bin_ids == b
        masks.append(mask)

    return masks
