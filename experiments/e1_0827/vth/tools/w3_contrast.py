#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_contrast.py -- is the hole DARKER or BRIGHTER than the floor, per world?

The contact sheet shows the polarity flipping between the two worlds.  Measure it:
for every size-axis frame with a GT box, mean grey INSIDE the GT box vs mean grey
in the surrounding ring (the box grown 2x, minus the box).  Sign of the difference
is the cue polarity the detector is asked to key on.
"""
from __future__ import annotations
import csv, json, os, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "labels.csv")))
            if int(r["occlusion_intended"]) == 0 and int(r["int_area_px"]) >= 500]
    acc = {}
    for r in rows:
        g = cv2.imread(os.path.join(HERE, r["rgb"]), cv2.IMREAD_GRAYSCALE)
        x0, y0 = int(float(r["gt_x0"])), int(float(r["gt_y0"]))
        x1, y1 = int(float(r["gt_x1"])) + 1, int(float(r["gt_y1"])) + 1
        w, h = x1 - x0, y1 - y0
        X0, Y0 = max(x0 - w // 2, 0), max(y0 - h // 2, 0)
        X1, Y1 = min(x1 + w // 2, g.shape[1]), min(y1 + h // 2, g.shape[0])
        inner = g[y0:y1, x0:x1]
        outer = g[Y0:Y1, X0:X1].astype(np.int32).sum() - inner.astype(np.int32).sum()
        nout = (Y1 - Y0) * (X1 - X0) - inner.size
        if inner.size < 10 or nout < 10:
            continue
        acc.setdefault(r["world"], []).append(
            (float(inner.mean()), outer / nout, float(g.mean())))
    out = {}
    for w, v in acc.items():
        a = np.array(v)
        out[w] = dict(n=len(v), hole_grey=round(float(np.median(a[:, 0])), 1),
                      ring_grey=round(float(np.median(a[:, 1])), 1),
                      frame_grey=round(float(np.median(a[:, 2])), 1),
                      contrast_hole_minus_ring=round(float(np.median(a[:, 0] - a[:, 1])), 1),
                      frac_hole_darker=round(float((a[:, 0] < a[:, 1]).mean()), 3))
    json.dump(out, open(os.path.join(HERE, "runs", "w3_contrast.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
