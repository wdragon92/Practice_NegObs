#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_smoke.py -- transfer sanity note ONLY (stage spec item 3).

Runs one detector over the 5 stair-scene smoke frames the owner already saw
(experiments/e1_0827/overlays/_simple/*.overlay.png sources) and prints how many
boxes it produces.  There is no warehouse GT here and no stair GT in the paper's
class space, so this is a COUNT, not a detection rate.  Same node pipeline
(trapezium ROI, drawn outline, centre-in-ROI keep rule) at the frames' own
1920x1080, so the ROI scales with the image.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = "/home/vislab/Desktop/work_sy/Practice_NegObs/dataset/v2_corpus/260819_main_on"
FRAMES = [("scene01", f"{CORPUS}/val/scene01/L0__s20260819__0000.png"),
          ("scene03", f"{CORPUS}/train/scene03/L0__s20260819__0000.png"),
          ("scene09", f"{CORPUS}/train/scene09/L0__s20260819__0000.png"),
          ("scene18", f"{CORPUS}/test/scene18/L0__s20260819__0000.png"),
          ("scene18_L5", f"{CORPUS}/test/scene18/L5__s20260819__0003.png")]
TAUS = [0.10, 0.25, 0.50]
FLOOR, IMGSZ = 0.05, 640
os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/claude-1000/ultra_cfg_vth")


def sha256f(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def trap(w, h):
    tw, bw, rh = 0.20 * w, 0.80 * w, 0.7 * h
    return np.array([[int((w - tw) // 2), int(h - rh)], [int((w + tw) // 2), int(h - rh)],
                     [int((w + bw) // 2), int(h)], [int((w - bw) // 2), int(h)]], np.int32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--device", default="0")
    a = ap.parse_args()
    import cv2
    from ultralytics import YOLO
    m = YOLO(a.weights)
    out = {}
    for name, path in FRAMES:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        h, w = img.shape[:2]
        verts = trap(w, h)
        mask = np.zeros((h, w), np.uint8)
        cv2.fillPoly(mask, [verts], 255)
        drawn = img.copy()
        cv2.polylines(drawn, [verts], True, (0, 255, 0), 2)
        roi = cv2.bitwise_and(drawn, drawn, mask=mask)
        r = m.predict(source=roi, imgsz=IMGSZ, conf=FLOOR, device=a.device,
                      save=False, verbose=False)[0]
        rows = []
        if r.boxes is not None and len(r.boxes):
            cf = r.boxes.conf.cpu().numpy()
            xy = r.boxes.xyxy.cpu().numpy()
            for i in cf.argsort()[::-1]:
                x0, y0, x1, y1 = (round(float(v), 1) for v in xy[i])
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                if cv2.pointPolygonTest(verts, (int(cx), int(cy)), False) < 0:
                    continue
                rows.append([round(float(cf[i]), 4), x0, y0, x1, y1, 1])
        out[name] = dict(path=path, resolution=[w, h], boxes=rows,
                         n={f"{t:.2f}": sum(1 for b in rows if b[0] >= t) for t in TAUS},
                         max_conf=(max(b[0] for b in rows) if rows else 0.0))
        print(f"  {a.tag:8s} {name:11s} boxes(conf>=.10/.25/.50) = "
              f"{out[name]['n']['0.10']}/{out[name]['n']['0.25']}/{out[name]['n']['0.50']}"
              f"   max conf {out[name]['max_conf']:.3f}")
    p = os.path.join(HERE, "runs", f"w3_smoke_{a.tag}.json")
    json.dump(dict(tag=a.tag, weights=a.weights, weights_sha256=sha256f(a.weights),
                   names={int(k): v for k, v in m.names.items()},
                   conf_floor=FLOOR, imgsz=IMGSZ, frames=out), open(p, "w"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    sys.exit(main())
