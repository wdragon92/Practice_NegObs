#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""measure_void.py -- how deep is the void, measured from the rendered depth?

For every frame of a chosen opening: back-project the pixels whose sight line passes
through that opening's footprint, and report the world z of what the ray actually hit.
  * bottomless  -> the depth is +inf and nothing is reported
  * floored     -> the median hit z is the floor under the plate, and
                   plate_top - z is the drop depth the camera can see.
"""
from __future__ import annotations
import argparse, glob, json, math, os
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATE = (-13.56098, 20.2009)


def rot(p, y):
    cp, sp, cy, sy = math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    return (np.array([[cy, -sy, 0.], [sy, cy, 0.], [0., 0., 1.]])
            @ np.array([[cp, 0., sp], [0., 1., 0.], [-sp, 0., cp]]))


def inside_opening(hole, hx, hy):
    """True where the world point (hx,hy) is inside the opening's footprint.

    The bbox is NOT the footprint for a disc -- 1 - pi/4 = 21.5 % of a circular hole's
    bbox is bright floor, and using the bbox silently mixes floor pixels into every
    "interior" statistic (caught by an inside-saturation reading of exactly 0.212).
    """
    b = hole["world_bbox"]
    inb = (hx > b[0]) & (hx < b[2]) & (hy > b[1]) & (hy < b[3])
    if hole.get("shape") != "circle":
        return inb
    cx, cy = 0.5 * (b[0] + b[2]), 0.5 * (b[1] + b[3])
    r = 0.25 * ((b[2] - b[0]) + (b[3] - b[1]))
    return inb & (((hx - cx) ** 2 + (hy - cy) ** 2) <= r * r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", required=True)
    ap.add_argument("--hole", required=True)
    ap.add_argument("--step", type=int, default=4)
    a = ap.parse_args()
    H = json.load(open(os.path.join(HERE, "holes.json")))
    hole = next(h for h in H["holes"] if h["hole_id"] == a.hole)
    b = hole["world_bbox"]
    top = H["plate_top_z"]
    zs, ninf, nfin, nfr = [], 0, 0, 0
    for pj in sorted(glob.glob(os.path.join(HERE, "frames", a.world, f"{a.hole}_*.pose.json"))):
        r = json.load(open(pj))
        dep = np.load(pj.replace(".pose.json", ".depth.npy"))
        w, h = r["res"]
        f = (w / 2) / math.tan(r["hfov_rad"] / 2)
        R = rot(r["sdf_pitch_rad"], r["yaw_rad"])
        u = np.arange(0, w, a.step) + .5
        v = np.arange(0, h, a.step) + .5
        U, V = np.meshgrid(u, v)
        d = np.stack([np.ones_like(U), -(U - w / 2) / f, -(V - h / 2) / f], -1) @ R.T
        t = dep[V.astype(int), U.astype(int)]
        # ray through the opening's footprint at plate top?
        tp = (top - r["z"]) / np.where(np.abs(d[..., 2]) < 1e-9, np.nan, d[..., 2])
        hx = r["x"] + tp * d[..., 0]
        hy = r["y"] + tp * d[..., 1]
        thru = (tp > 0) & inside_opening(hole, hx, hy)
        if not thru.any():
            continue
        nfr += 1
        fin = thru & np.isfinite(t)
        ninf += int((thru & ~np.isfinite(t)).sum())
        nfin += int(fin.sum())
        if fin.any():
            z = r["z"] + t[fin] * d[fin][:, 2]
            zs.append(z[z < top - 0.005])          # keep only what is BELOW the plate top
    print(f"world {a.world}  opening {a.hole} ({hole['w_m']}x{hole['h_m']} m, "
          f"{hole['shape']})  centre {hole['centre']}")
    print(f"frames with the opening on a sight line : {nfr}")
    print(f"pixels through the opening: +inf {ninf}   finite {nfin}   "
          f"({100*ninf/max(1,ninf+nfin):.1f} % bottomless)")
    if zs:
        z = np.concatenate(zs)
        print(f"hit z below the plate: median {np.median(z):.4f} m  "
              f"p10 {np.percentile(z,10):.4f}  p90 {np.percentile(z,90):.4f}  (n={len(z)})")
        print(f"=> visible drop depth = plate_top {top:.4f} - z = "
              f"**{top - np.median(z):.4f} m**")
    else:
        print("no finite hit below the plate -> the opening is bottomless from every pose")


if __name__ == "__main__":
    main()
