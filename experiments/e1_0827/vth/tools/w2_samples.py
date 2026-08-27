#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w2_samples.py -- 8 frames across the detection transition, GT (green) vs paper model (red).

One opening (H00, the 0.97 m circle) in eworld2, at the paper-pose camera geometry
(0.3 m up, 15 deg down), walked out from 0.5 m to 8 m.  The visible interior falls from
1.4e5 px to 68 px and the detector goes from confident to silent.
"""
from __future__ import annotations
import csv, json, os, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAU = 0.25
TILE = (640, 360)
GREEN, RED, YEL, WHITE = (60, 220, 60), (40, 40, 235), (0, 200, 235), (255, 255, 255)


def trap(w, h):
    tw, bw, rh = 0.20 * w, 0.80 * w, 0.7 * h
    return np.array([[int((w - tw) // 2), int(h - rh)], [int((w + tw) // 2), int(h - rh)],
                     [int((w + bw) // 2), int(h)], [int((w - bw) // 2), int(h)]], np.int32)


def main():
    L = {r["frame_key"]: r for r in csv.DictReader(open(os.path.join(HERE, "labels.csv")))}
    D = json.load(open(os.path.join(HERE, "runs/yolo_paper/detections.json")))["frames"]
    picks = [f"eworld2/H00_xp_d{d}_h03_pm15" for d in
             ("05", "07", "10", "15", "20", "30", "40", "60")]
    picks = [p for p in picks if p in L]
    print("tiles:", len(picks))
    sx, sy = TILE[0] / 1280.0, TILE[1] / 720.0
    tiles = []
    for k in picks:
        r = L[k]
        img = cv2.imread(os.path.join(HERE, r["rgb"]))
        cv2.polylines(img, [trap(1280, 720)], True, (90, 90, 90), 2)
        t = cv2.resize(img, TILE)
        gx0, gy0 = int(float(r["gt_x0"]) * sx), int(float(r["gt_y0"]) * sy)
        gx1, gy1 = int(float(r["gt_x1"]) * sx), int(float(r["gt_y1"]) * sy)
        if int(r["int_area_px"]) > 0:
            cv2.rectangle(t, (gx0, gy0), (gx1, gy1), GREEN, 2)
        best, on_hole = None, False
        gt = (float(r["gt_x0"]), float(r["gt_y0"]), float(r["gt_x1"]), float(r["gt_y1"]))
        for b in D[k]["roi"]:
            if b[0] < TAU or b[5] != 1:
                continue
            cv2.rectangle(t, (int(b[1] * sx), int(b[2] * sy)),
                          (int(b[3] * sx), int(b[4] * sy)), RED, 2)
            cx, cy = (b[1] + b[3]) / 2, (b[2] + b[4]) / 2
            if int(r["int_area_px"]) > 0 and gt[0] <= cx <= gt[2] and gt[1] <= cy <= gt[3]:
                on_hole = True
            if best is None:
                best = b[0]
        # caption bar
        cv2.rectangle(t, (0, 0), (TILE[0], 46), (24, 24, 24), -1)
        cv2.putText(t, f"standoff {float(r['standoff_m']):.1f} m   interior "
                       f"{int(r['int_area_px'])} px  ({r['int_w_px']}x{r['int_h_px']})",
                    (7, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.44, WHITE, 1, cv2.LINE_AA)
        if best is None:
            cap, col = "paper model: no box at all", YEL
        elif on_hole:
            cap, col = "paper model: conf %.2f  ON the hole" % best, GREEN
        else:
            cap, col = "paper model: conf %.2f  but NOT on the hole" % best, RED
        cv2.putText(t, cap, (7, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.44, col, 1, cv2.LINE_AA)
        tiles.append(t)
    rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
    sheet = np.vstack(rows)
    hdr = np.full((44, sheet.shape[1], 3), 20, np.uint8)
    cv2.putText(hdr, "W2 - paper weights (best.pt) on eworld2 H00 (0.97 m circle), camera 0.3 m up / 15 deg down."
                     "   GREEN = measured visible-interior GT   RED = paper model box (conf >= 0.25)   grey = node ROI",
                (10, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1, cv2.LINE_AA)
    out = np.vstack([hdr, sheet])
    p = os.path.join(HERE, "W2_samples.jpg")
    cv2.imwrite(p, out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print("wrote", p, out.shape, os.path.getsize(p) // 1024, "KiB")


if __name__ == "__main__":
    sys.exit(main())
