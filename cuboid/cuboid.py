#!/usr/bin/env python3
"""
3-point perspective, equidistant cubes with gap:cube = 1:5.
True hidden-line removal via 2D silhouette accumulation (shapely).
Output: plottable SVG, black lines on white, DIN landscape (A3).
"""

import sys
import math

import numpy as np
from shapely.geometry import LineString, MultiPoint, Polygon, box
from shapely.ops import unary_union

# ============================================================
# CANVAS: A1 landscape (DIN, ratio sqrt(2):1)
# ============================================================
W, H = 841.0, 594.0  # millimetres — direct pen-plotter units

# ============================================================
# SCENE GEOMETRY
# ============================================================
s = 1.0  # cube side length
g = s / 5  # gap
p = s + g  # grid period = 1.2

# Viewer at the 3D gap corner (intersection of three gap slabs)
cam_pos = np.array([0.5900, 0.8100, 0.8300])
# cam_pos = np.array([s / 2 + g / 2, s / 2 + g / 2, s / 2 + g / 2])  # (0.6, 0.6, 0.6)

# Camera orientation (yaw around world-up, pitch above horizon).
# Asymmetric yaw pushes the two horizontal VPs apart asymmetrically.
# az = math.radians(58.0)
# el = math.radians(15.0)
az = math.radians(61.592)
el = math.radians(16.129)

forward = np.array(
    [math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el)]
)
world_up = np.array([0.0, 1.0, 0.0])
right_v = np.cross(forward, world_up)
right_v /= np.linalg.norm(right_v)
up_v = np.cross(right_v, forward)

NEAR = 0.05  # near plane


def cam_coords(P):
    v = P - cam_pos
    return right_v @ v, up_v @ v, forward @ v


def project_dir(d):
    xc, yc, zc = right_v @ d, up_v @ d, forward @ d
    return None if abs(zc) < 1e-12 else (xc / zc, yc / zc)


# --- find the three vanishing points in camera-plane coords ---
vp_x_cp = project_dir(np.array([1.0, 0, 0]))
vp_y_cp = project_dir(np.array([0, 1.0, 0]))
vp_z_cp = project_dir(np.array([0, 0, 1.0]))

# Horizontal VPs: sort by camera-plane x to decide VPL / VPR
hvp = sorted([vp_x_cp, vp_z_cp], key=lambda v: v[0])
vpl_cp, vpr_cp = hvp

# --- target placements on canvas ---
# VPL_X = 0.03 * W  # VPL near left edge (≈ 12.6 mm)
# VPR_X = 0.75 * W  # VPR at 3/4 (315 mm)
# HORIZON_Y = 0.40 * H  # horizon above middle → plenty of "floor" visible too

# K = (VPR_X - VPL_X) / (vpr_cp[0] - vpl_cp[0])
# cx = VPL_X - K * vpl_cp[0]
# horizon_cp_y = (vpl_cp[1] + vpr_cp[1]) / 2
# cy = HORIZON_Y + K * horizon_cp_y


K = 138.5652
cx = 134.7516
cy = 78.7929


def to_canvas(P):
    xc, yc, zc = cam_coords(P)
    if zc < NEAR:
        return None
    return (cx + K * xc / zc, cy - K * yc / zc)


# ============================================================
# CUBE TOPOLOGY
# ============================================================
def vert(vidx):
    return np.array(
        [
            0.5 if (vidx >> 0) & 1 else -0.5,
            0.5 if (vidx >> 1) & 1 else -0.5,
            0.5 if (vidx >> 2) & 1 else -0.5,
        ]
    )


FACE_VERTS = {
    0: [1, 5, 7, 3],  # +x
    1: [4, 0, 2, 6],  # -x
    2: [3, 7, 6, 2],  # +y
    3: [0, 4, 5, 1],  # -y
    4: [5, 4, 6, 7],  # +z
    5: [0, 1, 3, 2],  # -z
}


def _build_edges():
    out = []
    for a in range(8):
        for b in range(a + 1, 8):
            diff = a ^ b
            if bin(diff).count("1") != 1:
                continue
            if diff == 1:
                fa = 2 if (a & 2) else 3
                fb = 4 if (a & 4) else 5
            elif diff == 2:
                fa = 0 if (a & 1) else 1
                fb = 4 if (a & 4) else 5
            else:
                fa = 0 if (a & 1) else 1
                fb = 2 if (a & 2) else 3
            out.append((a, b, fa, fb))
    return out


CUBE_EDGES = _build_edges()


def face_visible(c, f):
    h = s / 2
    return [
        cam_pos[0] > c[0] + h,
        cam_pos[0] < c[0] - h,
        cam_pos[1] > c[1] + h,
        cam_pos[1] < c[1] - h,
        cam_pos[2] > c[2] + h,
        cam_pos[2] < c[2] - h,
    ][f]


def cube_data(center):
    """Return (2D silhouette polygon, list of 2D edges to draw)."""
    vis = [f for f in range(6) if face_visible(center, f)]
    if not vis:
        return None, []
    pts = []
    for f in vis:
        for vi in FACE_VERTS[f]:
            p2 = to_canvas(vert(vi) * s + center)
            if p2 is None:
                return None, []
            pts.append(p2)
    if len({tuple(p) for p in pts}) < 3:
        return None, []
    sil = MultiPoint(pts).convex_hull
    if not isinstance(sil, Polygon):
        return None, []
    vis_set = set(vis)
    edges2d = []
    for a, b, fa, fb in CUBE_EDGES:
        if fa in vis_set or fb in vis_set:
            p0 = to_canvas(vert(a) * s + center)
            p1 = to_canvas(vert(b) * s + center)
            if p0 is not None and p1 is not None:
                edges2d.append((p0, p1))
    return sil, edges2d


# ============================================================
# CUBE LIST
# ============================================================
N = 11
MIN_CORNER_DIST = 1.0  # skip cubes whose nearest corner is too close
MAX_CENTER_DIST = 22.0  # cull deep background (too small to matter)

cubes = []
for i in range(-2, N):
    for j in range(-2, N):
        for k in range(-2, N):
            c = np.array([i * p, j * p, k * p])
            if forward @ (c - cam_pos) <= 0:
                continue
            h = s / 2
            near_corner = np.maximum(np.abs(cam_pos - c) - h, 0.0)
            if np.linalg.norm(near_corner) < MIN_CORNER_DIST:
                continue
            d_center = np.linalg.norm(c - cam_pos)
            if d_center > MAX_CENTER_DIST:
                continue
            cubes.append((i, j, k, c, d_center))

cubes.sort(key=lambda e: e[4])  # nearest first

# ============================================================
# HIDDEN LINE REMOVAL — accumulate 2D silhouettes, diff each edge
# ============================================================
occupied = None
canvas_poly = box(0, 0, W, H)
segments = []

for i, j, k, c, d in cubes:
    sil, edges2d = cube_data(c)
    if sil is None:
        continue
    if sil.intersection(canvas_poly).is_empty:
        continue
    for p0, p1 in edges2d:
        seg = LineString([p0, p1]).intersection(canvas_poly)
        if seg.is_empty:
            continue
        if occupied is not None:
            seg = seg.difference(occupied)
            if seg.is_empty:
                continue
        if seg.geom_type == "LineString":
            coords = list(seg.coords)
            if len(coords) >= 2:
                segments.append(coords)
        elif seg.geom_type == "MultiLineString":
            for part in seg.geoms:
                coords = list(part.coords)
                if len(coords) >= 2:
                    segments.append(coords)
    occupied = sil if occupied is None else unary_union([occupied, sil])

# ============================================================
# SVG
# ============================================================
out = sys.argv[1]
with open(out, "w") as f:
    f.write(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm">\n'
    )
    f.write('<rect width="100%" height="100%" fill="white"/>\n')
    f.write(
        '<g fill="none" stroke="black" stroke-width="0.35" '
        'stroke-linecap="round" stroke-linejoin="miter">\n'
    )
    for seg in segments:
        pts = " ".join(f"{x:.3f},{y:.3f}" for x, y in seg)
        f.write(f'  <polyline points="{pts}"/>\n')
    f.write("</g>\n</svg>\n")

# Report
print(f"Cubes rendered : {len(cubes)}")
print(f"Line segments  : {len(segments)}")
print(f"Canvas         : {W} x {H} mm")
print(f"VPL on canvas  : ({cx + K * vpl_cp[0]:7.2f}, {cy - K * vpl_cp[1]:7.2f})")
print(f"VPR on canvas  : ({cx + K * vpr_cp[0]:7.2f}, {cy - K * vpr_cp[1]:7.2f})")
print(f"VP_vert canvas : ({cx + K * vp_y_cp[0]:7.2f}, {cy - K * vp_y_cp[1]:7.2f})")
