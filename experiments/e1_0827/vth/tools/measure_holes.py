#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""measure_holes.py -- rasterise large_holed_floor.stl and measure every opening.

Method (same 1 cm raster idea as gazebo_wh_0824/tools/project_hole.py, generalised
from "the one opening we approach" to "every opening in the plate"):

  1. read the binary STL, keep the UP-FACING triangles that sit on the plate's top
     surface (|nz| ~ 1, z within TOP_EPS of the mesh's max z);
  2. rasterise them into a boolean occupancy grid at RASTER_M (1 cm);
  3. the plate outline = solid cells; an OPENING = a 4-connected component of empty
     cells that does not touch the grid border (border-connected empties are the
     outside of the plate, not a hole);
  4. report each opening's footprint bbox, area, equivalent radius and rectangularity.

Everything is in the STL's own (model-local) frame; world placement is applied by
apply_pose() using the <pose> the .world file gives the plate model.

usage:  python3 measure_holes.py [--out holes.json]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys

import numpy as np

STL = ("/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/"
       "bumperbot_description/models/large_holed_floor/meshes/large_holed_floor.stl")

RASTER_M = 0.01        # [기존값] gazebo_wh_0824 used a 1 cm raster for the same plate
TOP_EPS = 0.002        # [방법] a triangle belongs to the top face if its max z is within
                       #        2 mm of the mesh's global max z
UP_NZ = 0.90           # [방법] |nz| >= 0.90 counts as up/down-facing
MIN_HOLE_CELLS = 25    # [방법] 25 cells = 25 cm^2 -- below this an "opening" is raster
                       #        noise at a mesh seam, not a hole a robot can fall into


def read_stl(path):
    with open(path, "rb") as f:
        blob = f.read()
    n = struct.unpack("<I", blob[80:84])[0]
    exp = 84 + 50 * n
    if exp != len(blob):
        raise SystemExit(f"[fatal] not a binary STL of {n} tris ({exp} != {len(blob)})")
    rec = np.frombuffer(blob, dtype=np.dtype([("n", "<3f4"), ("v", "<3,3f4"),
                                              ("attr", "<u2")]), count=n, offset=84)
    return np.array(rec["n"], float), np.array(rec["v"], float)


def raster_top(nrm, tri):
    zmax = tri[:, :, 2].max()
    up = (np.abs(nrm[:, 2]) >= UP_NZ) & (tri[:, :, 2].max(axis=1) >= zmax - TOP_EPS)
    top = tri[up]
    x0, y0 = top[:, :, 0].min(), top[:, :, 1].min()
    x1, y1 = top[:, :, 0].max(), top[:, :, 1].max()
    nx = int(math.ceil((x1 - x0) / RASTER_M)) + 1
    ny = int(math.ceil((y1 - y0) / RASTER_M)) + 1
    grid = np.zeros((ny, nx), bool)
    # scan-convert every triangle (barycentric sign test on cell centres)
    for t in top:
        ax, ay = t[0, 0], t[0, 1]
        bx, by = t[1, 0], t[1, 1]
        cx, cy = t[2, 0], t[2, 1]
        i0 = max(0, int((min(ax, bx, cx) - x0) / RASTER_M) - 1)
        i1 = min(nx - 1, int((max(ax, bx, cx) - x0) / RASTER_M) + 1)
        j0 = max(0, int((min(ay, by, cy) - y0) / RASTER_M) - 1)
        j1 = min(ny - 1, int((max(ay, by, cy) - y0) / RASTER_M) + 1)
        if i1 < i0 or j1 < j0:
            continue
        gx = x0 + (np.arange(i0, i1 + 1) + 0.5) * RASTER_M
        gy = y0 + (np.arange(j0, j1 + 1) + 0.5) * RASTER_M
        GX, GY = np.meshgrid(gx, gy)
        d1 = (GX - bx) * (ay - by) - (ax - bx) * (GY - by)
        d2 = (GX - cx) * (by - cy) - (bx - cx) * (GY - cy)
        d3 = (GX - ax) * (cy - ay) - (cx - ax) * (GY - ay)
        neg = (d1 < 0) | (d2 < 0) | (d3 < 0)
        pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
        grid[j0:j1 + 1, i0:i1 + 1] |= ~(neg & pos)
    return grid, (x0, y0), zmax, float(tri[:, :, 2].min())


def label4(mask):
    """4-connected labelling of True cells; returns int labels (0 = background)."""
    lab = np.zeros(mask.shape, np.int32)
    cur = 0
    H, W = mask.shape
    for sj in range(H):
        for si in range(W):
            if not mask[sj, si] or lab[sj, si]:
                continue
            cur += 1
            stack = [(sj, si)]
            lab[sj, si] = cur
            while stack:
                j, i = stack.pop()
                for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    y, x = j + dj, i + di
                    if 0 <= y < H and 0 <= x < W and mask[y, x] and not lab[y, x]:
                        lab[y, x] = cur
                        stack.append((y, x))
    return lab, cur


def outline_cells(mask):
    """cells of `mask` whose 4-neighbourhood leaves `mask` -> footprint polygon seed"""
    m = mask
    e = np.zeros_like(m)
    e[1:, :] |= m[:-1, :]
    e[:-1, :] |= m[1:, :]
    e[:, 1:] |= m[:, :-1]
    e[:, :-1] |= m[:, 1:]
    return m & ~(e & np.roll(e, 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "holes_local.json"))
    a = ap.parse_args()

    nrm, tri = read_stl(STL)
    grid, (x0, y0), zmax, zmin = raster_top(nrm, tri)
    ny, nx = grid.shape
    print(f"[stl] {len(tri)} triangles   z range [{zmin:.4f}, {zmax:.4f}]  "
          f"thickness {zmax - zmin:.4f} m")
    print(f"[raster] {nx} x {ny} cells @ {RASTER_M} m   solid {grid.sum()} cells "
          f"= {grid.sum() * RASTER_M**2:.2f} m^2")
    print(f"[raster] origin (x0,y0) = ({x0:.4f}, {y0:.4f})  local bbox "
          f"x [{x0:.3f}, {x0 + nx * RASTER_M:.3f}]  y [{y0:.3f}, {y0 + ny * RASTER_M:.3f}]")

    empty = ~grid
    lab, n = label4(empty)
    print(f"[label] {n} empty components")
    border = set(lab[0, :].tolist()) | set(lab[-1, :].tolist()) | \
        set(lab[:, 0].tolist()) | set(lab[:, -1].tolist())
    border.discard(0)

    holes = []
    for k in range(1, n + 1):
        if k in border:
            continue
        m = lab == k
        cells = int(m.sum())
        if cells < MIN_HOLE_CELLS:
            continue
        js, is_ = np.nonzero(m)
        i0, i1 = int(is_.min()), int(is_.max())
        j0, j1 = int(js.min()), int(js.max())
        bx0 = x0 + i0 * RASTER_M
        bx1 = x0 + (i1 + 1) * RASTER_M
        by0 = y0 + j0 * RASTER_M
        by1 = y0 + (j1 + 1) * RASTER_M
        area = cells * RASTER_M ** 2
        w = bx1 - bx0
        h = by1 - by0
        holes.append(dict(
            cells=cells, area_m2=round(area, 5),
            local_bbox=[round(bx0, 4), round(by0, 4), round(bx1, 4), round(by1, 4)],
            w_m=round(w, 4), h_m=round(h, 4),
            r_eq_m=round(math.sqrt(area / math.pi), 4),
            rect_fill=round(area / (w * h), 4),
            centroid_local=[round(x0 + (is_.mean() + 0.5) * RASTER_M, 4),
                            round(y0 + (js.mean() + 0.5) * RASTER_M, 4)]))
    holes.sort(key=lambda d: -d["area_m2"])
    for i, hh in enumerate(holes):
        hh["hole_id"] = f"H{i:02d}"

    out = dict(stl=STL, raster_m=RASTER_M, top_eps_m=TOP_EPS, up_nz=UP_NZ,
               min_hole_cells=MIN_HOLE_CELLS,
               plate_top_z_local=round(float(zmax), 5),
               plate_bottom_z_local=round(float(zmin), 5),
               plate_thickness_m=round(float(zmax - zmin), 5),
               raster_origin=[round(float(x0), 5), round(float(y0), 5)],
               raster_shape=[int(ny), int(nx)],
               plate_area_m2=round(float(grid.sum()) * RASTER_M ** 2, 4),
               n_holes=len(holes), holes=holes)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    np.savez_compressed(a.out.replace(".json", "_grid.npz"), grid=grid)

    print(f"\n{'id':4s} {'area m2':>8s} {'w x h m':>16s} {'r_eq m':>7s} {'rect':>5s}  "
          f"centroid_local")
    for hh in holes:
        print(f"{hh['hole_id']:4s} {hh['area_m2']:8.4f} "
              f"{hh['w_m']:7.3f} x {hh['h_m']:6.3f} {hh['r_eq_m']:7.3f} "
              f"{hh['rect_fill']:5.2f}  ({hh['centroid_local'][0]:8.3f},"
              f" {hh['centroid_local'][1]:8.3f})")
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
