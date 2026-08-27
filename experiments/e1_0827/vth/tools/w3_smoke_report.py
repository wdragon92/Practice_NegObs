#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_smoke_report.py -- score the stair smoke boxes against the corpus drop mask.

Report-only transfer note.  The stair corpus's own `*.dropmask.png` (the owner's
own label, overlays/_simple/) is used purely to say whether a box landed ON a
drop or somewhere else.  No threshold, no rate, no boundary.
"""
from __future__ import annotations
import json, os, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OV = "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/e1_0827/overlays/_simple"
MASK = {"scene01": "260819_main_on__scene01__L0__s20260819__0000.dropmask.png",
        "scene03": "260819_main_on__scene03__L0__s20260819__0000.dropmask.png",
        "scene09": "260819_main_on__scene09__L0__s20260819__0000.dropmask.png",
        "scene18": "260819_main_on__scene18__L0__s20260819__0000.dropmask.png",
        "scene18_L5": "260819_main_on__scene18__L5__s20260819__0003.dropmask.png"}
TAU = 0.25


def main():
    S = {t: json.load(open(os.path.join(HERE, "runs", f"w3_smoke_{t}.json")))
         for t in ("paper", "replica")}
    rows, tiles = [], []
    for name in MASK:
        m = cv2.imread(os.path.join(OV, MASK[name]), cv2.IMREAD_GRAYSCALE)
        drop_px = int((m > 0).sum())
        img = cv2.imread(S["paper"]["frames"][name]["path"], cv2.IMREAD_COLOR)
        ov = img.copy()
        ov[m > 0] = (0.55 * np.array([60, 220, 60]) + 0.45 * ov[m > 0]).astype(np.uint8)
        rec = dict(scene=name, drop_px=drop_px)
        for tag, col in (("paper", (40, 40, 235)), ("replica", (235, 120, 40))):
            bx = [b for b in S[tag]["frames"][name]["boxes"] if b[0] >= TAU]
            on = 0
            for b in bx:
                cx, cy = int((b[1] + b[3]) / 2), int((b[2] + b[4]) / 2)
                hit = bool(0 <= cy < m.shape[0] and 0 <= cx < m.shape[1] and m[cy, cx] > 0)
                on += hit
                cv2.rectangle(ov, (int(b[1]), int(b[2])), (int(b[3]), int(b[4])), col, 3)
                cv2.putText(ov, f"{tag} {b[0]:.2f}{' ON-DROP' if hit else ''}",
                            (int(b[1]), max(int(b[2]) - 8, 16)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, col, 2, cv2.LINE_AA)
            rec[tag + "_boxes"] = len(bx)
            rec[tag + "_on_drop"] = on
            rec[tag + "_max_conf"] = S[tag]["frames"][name]["max_conf"]
        rows.append(rec)
        t = cv2.resize(ov, (640, 360))
        cv2.rectangle(t, (0, 0), (640, 26), (24, 24, 24), -1)
        cv2.putText(t, f"{name}  drop {drop_px/ (m.size):.1%} of frame", (7, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(t)
    while len(tiles) % 3:
        tiles.append(np.full_like(tiles[0], 24))
    sheet = np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)])
    hdr = np.full((40, sheet.shape[1], 3), 20, np.uint8)
    cv2.putText(hdr, "W3 transfer note - stair smoke frames.  GREEN tint = corpus drop mask "
                     "  RED = paper weights  ORANGE = W3 replica  (conf >= 0.25)",
                (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    p = os.path.join(HERE, "VTH_smoke.jpg")
    cv2.imwrite(p, np.vstack([hdr, sheet]), [cv2.IMWRITE_JPEG_QUALITY, 82])
    json.dump(rows, open(os.path.join(HERE, "runs", "w3_smoke_scored.json"), "w"), indent=1)
    print("| scene | drop px | paper boxes | on drop | paper max conf | "
          "replica boxes | on drop | replica max conf |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"| {r['scene']} | {r['drop_px']} | {r['paper_boxes']} | {r['paper_on_drop']} | "
              f"{r['paper_max_conf']:.3f} | {r['replica_boxes']} | {r['replica_on_drop']} | "
              f"{r['replica_max_conf']:.3f} |")
    print("wrote", p, os.path.getsize(p) // 1024, "KiB")


if __name__ == "__main__":
    sys.exit(main())
