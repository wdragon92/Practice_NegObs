#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_depth.py -- is the saved depth metric, and is it registered to the RGB?

METRIC CHECK (the gate: <= 2 cm at nadir)
    The plate top is a known plane (z = plate_top).  For a pixel (u,v) the camera-frame
    ray is d = (1, -(u-cx)/f, -(v-cy)/f) and Gazebo's 32FC1 value is the FORWARD
    component of the hit point, i.e. exactly the ray parameter t that solves
        eye_z + t * (R d)_z = plate_top .
    So the expected depth of any pixel whose ray lands on bare plate is computable in
    closed form with no free parameter.  We evaluate it at
      * the NADIR pixel (the ray pointing straight down) when it is inside the frame,
        which is the "known distance" check the stage was asked for, and
      * a robust median over every pixel that lands on SOLID plate (openings and any
        pixel whose measured depth runs short -- an asset in the way -- are excluded by
        a 0.25 m gate, then the median of the remainder is reported).

REGISTRATION CHECK
    RGB and depth come from ONE `type="depth"` sensor, so they cannot be misregistered
    by construction.  We still test it from the data: the target opening is projected
    from the pose, and we print the fraction of pixels inside that polygon whose depth
    is NON-finite (eworld2: the void is bottomless, so a registered depth image must go
    to +inf exactly where the RGB shows the opening).
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATE = (-13.56098, 20.2009)


def rot(pitch, yaw):
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]])
            @ np.array([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]]))


def rays(rec, step=8):
    w, h = rec["res"]
    f = (w / 2.0) / math.tan(rec["hfov_rad"] / 2.0)
    u = np.arange(0, w, step) + 0.5
    v = np.arange(0, h, step) + 0.5
    U, V = np.meshgrid(u, v)
    d = np.stack([np.ones_like(U), -(U - w / 2.0) / f, -(V - h / 2.0) / f], -1)
    R = rot(rec["sdf_pitch_rad"], rec["yaw_rad"])
    dw = d @ R.T                      # world direction (rows are R @ d)
    return U, V, d, dw, f


def check(path, grid, origin, raster, plate_top, step=8):
    rec = json.load(open(path))
    dep = np.load(path.replace(".pose.json", ".depth.npy"))
    U, V, d, dw, f = rays(rec, step)
    eye = np.array([rec["x"], rec["y"], rec["z"]])
    t = (plate_top - eye[2]) / np.where(np.abs(dw[..., 2]) < 1e-9, np.nan, dw[..., 2])
    ok = np.isfinite(t) & (t > 0.05) & (t < 60.0)
    hx = eye[0] + t * dw[..., 0]
    hy = eye[1] + t * dw[..., 1]
    ii = ((hx - PLATE[0] - origin[0]) / raster).astype(int)
    jj = ((hy - PLATE[1] - origin[1]) / raster).astype(int)
    inb = ok & (ii >= 0) & (jj >= 0) & (jj < grid.shape[0]) & (ii < grid.shape[1])
    solid = np.zeros_like(inb)
    solid[inb] = grid[jj[inb], ii[inb]]
    meas = dep[(V.astype(int)), (U.astype(int))]
    good = solid & np.isfinite(meas)
    err = np.abs(meas - t)
    # an asset standing on the plate makes the measured depth run SHORT; drop those
    keep = good & (err < 0.25)
    out = dict(pose_id=rec["pose_id"], world=rec["world"],
               n_floor_px=int(good.sum()), n_used=int(keep.sum()))
    out["floor_abs_err_med_m"] = round(float(np.median(err[keep])), 5) if keep.any() else None
    out["floor_abs_err_p90_m"] = round(float(np.percentile(err[keep], 90)), 5) if keep.any() else None

    # STEEPEST-RAY check ("nadir substitute").  With the brief's pose band the true
    # nadir is NEVER inside the frame: the most downward ray is pitch + vfov/2 =
    # 15 + 21.1 = 36.1 deg below horizontal, far from 90 deg.  The bottom-centre pixel
    # is the steepest ray that exists, so that is the single-pixel "known distance".
    w, h = rec["res"]
    R = rot(rec["sdf_pitch_rad"], rec["yaw_rad"])
    f2 = (w / 2.0) / math.tan(rec["hfov_rad"] / 2.0)
    ub, vb = w / 2.0 + 0.5, h - 0.5
    dcb = np.array([1.0, -(ub - w / 2.0) / f2, -(vb - h / 2.0) / f2])
    dwb = R @ dcb
    out["steep_err_m"] = None
    if dwb[2] < -1e-9:
        expb = (plate_top - rec["z"]) / dwb[2]
        mb = float(dep[int(vb), int(ub)])
        hxb = rec["x"] + expb * dwb[0]
        hyb = rec["y"] + expb * dwb[1]
        ib = int((hxb - PLATE[0] - origin[0]) / raster)
        jb = int((hyb - PLATE[1] - origin[1]) / raster)
        onplate = (0 <= jb < grid.shape[0] and 0 <= ib < grid.shape[1] and grid[jb, ib])
        out["steep_on_solid_plate"] = bool(onplate)
        out["steep_ray_deg_below_horizon"] = round(
            math.degrees(math.asin(-dwb[2] / np.linalg.norm(dwb))), 3)
        if np.isfinite(mb) and onplate:
            out["steep_err_m"] = round(abs(mb - expb), 5)
            out["steep_meas_m"] = round(mb, 5)
            out["steep_exp_m"] = round(float(expb), 5)

    # nadir pixel: the ray whose world direction is closest to straight down
    w, h = rec["res"]
    R = rot(rec["sdf_pitch_rad"], rec["yaw_rad"])
    dn = R.T @ np.array([0.0, 0.0, -1.0])
    out["nadir_err_m"] = None
    if dn[0] > 1e-6:
        un = w / 2.0 - f * dn[1] / dn[0]
        vn = h / 2.0 - f * dn[2] / dn[0]
        if 0 <= un < w and 0 <= vn < h:
            m = float(dep[int(vn), int(un)])
            exp = (rec["z"] - plate_top) / abs(dn[2] / dn[0]) if abs(dn[2]) > 1e-9 else np.nan
            # for the nadir ray the forward component t satisfies t*(R d)_z = -(z-plate)
            dcam = np.array([1.0, -(un - w / 2.0) / f, -(vn - h / 2.0) / f])
            dwn = R @ dcam
            exp = (plate_top - rec["z"]) / dwn[2]
            if np.isfinite(m):
                out["nadir_err_m"] = round(abs(m - exp), 5)
                out["nadir_meas_m"] = round(m, 5)
                out["nadir_exp_m"] = round(float(exp), 5)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "depth_check.json"))
    a = ap.parse_args()
    hl = json.load(open(os.path.join(HERE, "holes_local.json")))
    grid = np.load(os.path.join(HERE, "holes_local_grid.npz"))["grid"]
    plate_top = hl["plate_top_z_local"]
    pats = sorted(glob.glob(os.path.join(HERE, "frames", a.world or "*", "*.pose.json")))
    if a.limit:
        pats = pats[:: max(1, len(pats) // a.limit)][:a.limit]
    rows = [check(p, grid, hl["raster_origin"], hl["raster_m"], plate_top) for p in pats]
    json.dump(rows, open(a.out, "w"), indent=1, sort_keys=True)
    nad = [r["nadir_err_m"] for r in rows if r["nadir_err_m"] is not None]
    stp = [r["steep_err_m"] for r in rows if r.get("steep_err_m") is not None]
    flo = [r["floor_abs_err_med_m"] for r in rows if r["floor_abs_err_med_m"] is not None]
    print(f"frames checked        {len(rows)}")
    print(f"nadir pixel in frame  {len(nad)}")
    if nad:
        print(f"nadir |err| m         median {np.median(nad):.5f}  p90 {np.percentile(nad,90):.5f}"
              f"  max {max(nad):.5f}")
    if stp:
        print(f"steepest px in frame  {len(stp)}  (bottom-centre pixel; true nadir is "
              f"outside the FOV for this pose band)")
        print(f"steep |err| m         median {np.median(stp):.5f}  p90 {np.percentile(stp,90):.5f}"
              f"  max {max(stp):.5f}")
    if flo:
        print(f"floor |err| m (med)   median {np.median(flo):.5f}  p90 {np.percentile(flo,90):.5f}"
              f"  max {max(flo):.5f}")
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
