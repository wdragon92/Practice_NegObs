#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_samples.py -- 8 frames, GT green / paper red / replica blue.

The SAME opening (H00, the 0.97 m circle) at the SAME camera poses in both
worlds -- the pose_ids and the measured visible-interior pixel counts are
identical to the digit, because the perforated plate is the same mesh at the
same pose.  Only the lighting and the surrounding assets differ.  Top row =
eworld2 (training world, has a sun), bottom row = expandedworld (evaluation
world, NO light source at all).
"""
from __future__ import annotations
import csv, json, os, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAU = 0.25
TILE = (640, 360)
GREEN, RED, BLUE, YEL, WHITE = (60, 220, 60), (40, 40, 235), (235, 130, 40), (0, 200, 235), (255, 255, 255)
STANDOFFS = ("05", "10", "20", "40")


def trap(w, h):
    tw, bw, rh = 0.20 * w, 0.80 * w, 0.7 * h
    return np.array([[int((w - tw) // 2), int(h - rh)], [int((w + tw) // 2), int(h - rh)],
                     [int((w + bw) // 2), int(h)], [int((w - bw) // 2), int(h)]], np.int32)


def main():
    L = {r["frame_key"]: r for r in csv.DictReader(open(os.path.join(HERE, "labels.csv")))}
    D = {t: json.load(open(os.path.join(HERE, f"runs/yolo_{t}/detections.json")))["frames"]
         for t in ("paper", "replica")}
    sx, sy = TILE[0] / 1280.0, TILE[1] / 720.0
    rows = []
    for world in ("eworld2", "expandedworld"):
        tiles = []
        for d in STANDOFFS:
            k = f"{world}/H00_xp_d{d}_h03_pm15"
            r = L[k]
            img = cv2.imread(os.path.join(HERE, r["rgb"]))
            cv2.polylines(img, [trap(1280, 720)], True, (90, 90, 90), 2)
            t = cv2.resize(img, TILE)
            gt = (float(r["gt_x0"]), float(r["gt_y0"]), float(r["gt_x1"]), float(r["gt_y1"]))
            if int(r["int_area_px"]) > 0:
                cv2.rectangle(t, (int(gt[0] * sx), int(gt[1] * sy)),
                              (int(gt[2] * sx), int(gt[3] * sy)), GREEN, 2)
            caps = []
            for tag, col in (("paper", RED), ("replica", BLUE)):
                best, on = None, False
                for b in D[tag][k]["roi"]:
                    if b[0] < TAU or b[5] != 1:
                        continue
                    cv2.rectangle(t, (int(b[1] * sx), int(b[2] * sy)),
                                  (int(b[3] * sx), int(b[4] * sy)), col, 2)
                    cx, cy = (b[1] + b[3]) / 2, (b[2] + b[4]) / 2
                    if int(r["int_area_px"]) > 0 and gt[0] <= cx <= gt[2] and gt[1] <= cy <= gt[3]:
                        on = True
                    if best is None:
                        best = b[0]
                caps.append((tag, best, on, col))
            cv2.rectangle(t, (0, 0), (TILE[0], 62), (24, 24, 24), -1)
            cv2.putText(t, f"{world}  standoff {float(r['standoff_m']):.1f} m   interior "
                           f"{int(r['int_area_px'])} px ({r['int_w_px']}x{r['int_h_px']})",
                        (7, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.44, WHITE, 1, cv2.LINE_AA)
            for i, (tag, best, on, col) in enumerate(caps):
                s = (f"{tag}: no box" if best is None
                     else f"{tag}: {best:.2f} " + ("ON the hole" if on else "NOT on the hole"))
                cv2.putText(t, s, (7, 34 + 18 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.44,
                            (GREEN if on else (YEL if best is None else col)), 1, cv2.LINE_AA)
            tiles.append(t)
        rows.append(np.hstack(tiles))
    sheet = np.vstack(rows)
    hdr = np.full((66, sheet.shape[1], 3), 20, np.uint8)
    cv2.putText(hdr, "W3 - the SAME opening H00 (0.97 m circle) at the SAME 4 camera poses in BOTH worlds "
                     "(camera 0.3 m up / 15 deg down).  Interior pixel counts are identical to the digit.",
                (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.58, WHITE, 1, cv2.LINE_AA)
    cv2.putText(hdr, "GREEN = measured visible-interior GT    RED = paper weights    BLUE = W3 replica   "
                     "(conf >= 0.25, node ROI)    top row eworld2 (train, has sun) / bottom expandedworld (eval, NO light)",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 1, cv2.LINE_AA)
    out = np.vstack([hdr, sheet])
    p = os.path.join(HERE, "VTH_samples.jpg")
    cv2.imwrite(p, out, [cv2.IMWRITE_JPEG_QUALITY, 86])
    print("wrote", p, out.shape, os.path.getsize(p) // 1024, "KiB")


if __name__ == "__main__":
    sys.exit(main())
