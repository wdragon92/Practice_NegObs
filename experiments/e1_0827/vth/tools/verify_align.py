#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_align.py -- are RGB and depth the SAME pixels?

In eworld2 nothing exists under the plate, so every ray that enters an opening leaves
the scene: depth = +inf and RGB = the flat <background> colour.  Those two masks are
produced by two different code paths inside Gazebo, so their agreement is a direct
RGB<->depth co-registration measurement (not an assumption about the sensor model).

    void  = ~isfinite(depth)
    bg    = every RGB channel within TOL of the modal colour inside `void`
    -> IoU(void, bg), and the centroid offset in pixels.

A registered pair gives IoU ~ 1 and an offset of a fraction of a pixel; a one-pixel
shift between the two images would show up immediately in the offset.
"""
from __future__ import annotations

import argparse
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 6          # [방법] per-channel tolerance around the modal void colour, 0-255


def one(pj):
    r = json.load(open(pj))
    d = os.path.dirname(pj)
    dep = np.load(os.path.join(d, r["depth_file"]))
    from PIL import Image
    rgb = np.asarray(Image.open(os.path.join(d, r["rgb_file"])).convert("RGB"), np.int16)
    void = ~np.isfinite(dep)
    if void.sum() < 500:
        return None
    med = np.median(rgb[void], axis=0)
    bg = (np.abs(rgb - med) <= TOL).all(axis=2)
    inter = (void & bg).sum()
    union = (void | bg).sum()
    ys, xs = np.nonzero(void)
    ys2, xs2 = np.nonzero(bg)
    return dict(pose_id=r["pose_id"], world=r["world"],
                void_px=int(void.sum()), bg_px=int(bg.sum()),
                iou=round(float(inter / union), 5),
                void_colour=[int(v) for v in med],
                dx_px=round(float(xs2.mean() - xs.mean()), 3),
                dy_px=round(float(ys2.mean() - ys.mean()), 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="eworld2")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--out", default=os.path.join(HERE, "align_check.json"))
    a = ap.parse_args()
    fs = sorted(glob.glob(os.path.join(HERE, "frames", a.world, "*.pose.json")))
    if a.limit and len(fs) > a.limit:
        fs = fs[:: len(fs) // a.limit][:a.limit]
    rows = [x for x in (one(p) for p in fs) if x]
    json.dump(rows, open(a.out, "w"), indent=1, sort_keys=True)
    if not rows:
        print("no frame had enough void pixels")
        return
    iou = np.array([r["iou"] for r in rows])
    dx = np.array([r["dx_px"] for r in rows])
    dy = np.array([r["dy_px"] for r in rows])
    print(f"frames with void>=500 px  {len(rows)} / {len(fs)}")
    print(f"IoU(void, background RGB) median {np.median(iou):.4f}  min {iou.min():.4f}")
    print(f"centroid offset px        dx median {np.median(dx):+.3f}  dy median {np.median(dy):+.3f}"
          f"   |dx|max {np.abs(dx).max():.3f}  |dy|max {np.abs(dy).max():.3f}")
    print(f"void colour (modal RGB)   {rows[0]['void_colour']}")
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
