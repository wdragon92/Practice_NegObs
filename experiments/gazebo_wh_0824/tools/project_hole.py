#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""project_hole.py -- the TRUE DROP REGION, computed, not hand-drawn.

The hazard is a rectangle of the paper's floor plate that has been cut away:

    x in [-4.280, -3.480]   y in [-1.370, -0.570]   at z = 0.1243

Every camera pose is exact (static camera models in the world file), and Gazebo's
pinhole model is exact, so the region a drop-detection box MUST overlap can be
PROJECTED rather than annotated.  This module returns, per view:

    quad   the 4 corners of the opening projected into the image (float px)
    bbox   the axis-aligned bounding box of that quad, clipped to the frame
    mask   a boolean HxW rasterisation of the quad (used for pixel-level overlap)

Camera convention (Gazebo Classic / SDF): the sensor looks along its local +X,
local +Z is up, local +Y is left.  With R = Rz(yaw) Ry(pitch) Rx(roll),
    p_cam = R^T (p_world - eye)
    u = cx + f * (-p_cam.y / p_cam.x)
    v = cy + f * (-p_cam.z / p_cam.x)
    f  = (W/2) / tan(hfov/2)      (square pixels; Gazebo derives vfov from aspect)

Sanity: for the d1.2 view this puts the near rim at v ~ 212 and the far rim at
v ~ 172 in a 1280x720 frame, matching the hand calculation in WAREHOUSE_VARIANT.md §2.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from make_wh_worlds import HOLE_X0, HOLE_X1, HOLE_Y0, HOLE_Y1, FLOOR_TOP_Z  # noqa: E402

CORNERS = np.array([
    [HOLE_X0, HOLE_Y0, FLOOR_TOP_Z],
    [HOLE_X1, HOLE_Y0, FLOOR_TOP_Z],
    [HOLE_X1, HOLE_Y1, FLOOR_TOP_Z],
    [HOLE_X0, HOLE_Y1, FLOOR_TOP_Z],
], dtype=float)


def rot(roll, pitch, yaw):
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    return Rz @ Ry @ Rx


def project(points, eye, pitch, yaw, hfov, w, h, roll=0.0):
    R = rot(roll, pitch, yaw)
    pc = (np.asarray(points, float) - np.asarray(eye, float)) @ R      # == R^T (p-eye)
    f = (w / 2.0) / math.tan(hfov / 2.0)
    fwd = pc[:, 0]
    ok = fwd > 1e-6
    u = np.full(len(pc), np.nan)
    v = np.full(len(pc), np.nan)
    u[ok] = w / 2.0 + f * (-pc[ok, 1] / fwd[ok])
    v[ok] = h / 2.0 + f * (-pc[ok, 2] / fwd[ok])
    return np.stack([u, v], 1), ok


def poly_mask(quad, w, h):
    """Rasterise a convex quad (float px) into a boolean HxW mask."""
    m = np.zeros((h, w), bool)
    q = np.asarray(quad, float)
    if not np.isfinite(q).all():
        return m
    x0 = max(0, int(np.floor(q[:, 0].min())))
    x1 = min(w - 1, int(np.ceil(q[:, 0].max())))
    y0 = max(0, int(np.floor(q[:, 1].min())))
    y1 = min(h - 1, int(np.ceil(q[:, 1].max())))
    if x1 < x0 or y1 < y0:
        return m
    gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
    # orientation-free half-plane test: a point is inside a convex polygon iff the
    # edge cross-products never change sign.  (Avoids having to know the winding,
    # which flips between views because yaw = pi mirrors the image.)
    neg = np.zeros(gx.shape, bool)
    pos = np.zeros(gx.shape, bool)
    n = len(q)
    for i in range(n):
        ax, ay = q[i]
        bx, by = q[(i + 1) % n]
        d = (gx - ax) * (by - ay) - (bx - ax) * (gy - ay)
        neg |= d < 0
        pos |= d > 0
    m[y0:y1 + 1, x0:x1 + 1] = ~(neg & pos)
    return m


CORNERS_BOT = CORNERS.copy()
CORNERS_BOT[:, 2] = 0.0                 # underside of the 0.1243 m plate


def region_for_view(cam):
    """cam: manifest camera dict -> the projected drop region.

    `strict` is the opening at the plate's TOP surface -- the pixels that are
    literally missing floor.  `loose` additionally covers the cut face of the plate
    (the same rectangle at z = 0), i.e. every pixel a human would circle as "the
    hole", including its visible inner wall.  Both are reported; the read-out uses
    `strict` for overlap and reports `loose` alongside as a cross-check.
    """
    w, h = cam["res"]
    quad, ok = project(CORNERS, cam["eye"], cam["pitch_rad"], cam["yaw_rad"],
                       cam["hfov_rad"], w, h)
    quad_b, _ = project(CORNERS_BOT, cam["eye"], cam["pitch_rad"], cam["yaw_rad"],
                        cam["hfov_rad"], w, h)
    m_strict = poly_mask(quad, w, h)
    m_loose = m_strict | poly_mask(quad_b, w, h)
    # fill the band between top and bottom quads (the cut face) by convex hull rows
    ys, xs = np.nonzero(m_loose)
    out = dict(quad=quad.tolist(), quad_bottom=quad_b.tolist(),
               n_visible_corners=int(ok.sum()), res=[w, h])
    for tag, m in (("strict", m_strict), ("loose", m_loose)):
        yy, xx = np.nonzero(m)
        out[tag] = dict(
            area_px=int(m.sum()),
            bbox=None if not len(xx) else
            [float(xx.min()), float(yy.min()), float(xx.max() + 1), float(yy.max() + 1)])
    # PRIMARY = strict: the pixels where the floor is literally missing.  `loose` is a
    # generous envelope that also contains the projected underside of the plate; some of
    # those pixels are occluded by the near rim, so loose is only ever used as a
    # "we were not strict enough to matter" cross-check.
    out["bbox"] = out["strict"]["bbox"]
    out["area_px"] = out["strict"]["area_px"]
    return out


def masks_for_view(cam):
    w, h = cam["res"]
    quad, _ = project(CORNERS, cam["eye"], cam["pitch_rad"], cam["yaw_rad"],
                      cam["hfov_rad"], w, h)
    quad_b, _ = project(CORNERS_BOT, cam["eye"], cam["pitch_rad"], cam["yaw_rad"],
                        cam["hfov_rad"], w, h)
    ms = poly_mask(quad, w, h)
    return ms, ms | poly_mask(quad_b, w, h)


def load(world, frames_root=None):
    frames_root = frames_root or os.path.join(HERE, "frames")
    man = json.load(open(os.path.join(frames_root, world, f"{world}_cap_manifest.json")))
    return {v: region_for_view(c) for v, c in man["cameras"].items()}


def main():
    world = sys.argv[1] if len(sys.argv) > 1 else "wh0"
    out = load(world)
    print(f"{'view':12s} {'corners':>7s} {'area_px':>9s}  bbox")
    for v in sorted(out):
        r = out[v]
        bb = "-" if r["bbox"] is None else \
            "[%4d %4d %4d %4d]" % tuple(int(x) for x in r["bbox"])
        print(f"{v:12s} {r['n_visible_corners']:7d} {r['area_px']:9d}  {bb}")
    json.dump(out, open(os.path.join(HERE, "out", f"drop_region_{world}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
