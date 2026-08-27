#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yolo_paper.py -- the PAPER'S OWN detector on the paper's own warehouse, offline.

WEIGHTS (read-only, never copied into a git-tracked path; AGPL-3.0, see run.json)
    Baseline_NegObs/src/negativeobstacleavoidandance/bot_camera/model/best.pt
    ultralytics 8.3.6 / yolov8n.yaml / nc=1 / names={0: 'negative_obstacle'}
    trained 2024-12-15, imgsz 640, 100 epochs, val mAP50 0.935.

INFERENCE PATH -- reproduces `bot_camera/bot_camera/clean_yolo.py` step for step:

    1. build the trapezium ROI  (ROIConfig: TOP 0.20 W, BOTTOM 0.80 W, HEIGHT 0.7 H)
    2. `roi_image = cv2.bitwise_and(frame, frame, mask=mask)`   <- YOLO sees the MASKED frame
    3. `results = self.model(image)`                            <- ultralytics defaults
    4. keep a detection only if its box CENTRE is inside the trapezium
       (`cv2.pointPolygonTest(...) < 0: continue`)
    5. call it an OBSTACLE if `has_depth_drop(profile, conf)` -- which is
       `depth jump > 0.015 m  OR  conf > 0.65`

We do not have the aligned depth image for these static cameras, so step 5 is
reported in its conf-only branch (`gate_conf065`) and that is stated in the doc.
Steps 1-4 are exact.  Arms:

    roi   masked exactly like the node   (the node's real operating condition)
    full  unmasked frame                 (fairness control: is the mask the reason?)

Predictions are made at a low floor (conf 0.05) and the operating point tau = 0.25
(ultralytics' own predict default, which `self.model(image)` uses) is applied at READ
time, so "silent" and "just under the bar" stay distinguishable.

Run in the baseline's own venv:
    source Baseline_NegObs/setup_env.sh && python3 tools/yolo_paper.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

BASE = "/home/vislab/Desktop/work_sy/Baseline_NegObs"
WEIGHTS = os.path.join(
    BASE, "src/negativeobstacleavoidandance/bot_camera/model/best.pt")
WORLDS = ["wh0", "wh_e", "wh_h", "wh_hc"]
FLOOR = 0.05          # predict-time floor
TAU = 0.25            # ultralytics predict default == what clean_yolo.py's model(img) uses
GATE_CONF = 0.65      # clean_yolo.py DetectionConfig.CONFIDENCE_THRESHOLD
IMGSZ = 640           # the weights' own train_args imgsz
MAX_DET = 300
ROI_TOP_W, ROI_BOT_W, ROI_H = 0.20, 0.80, 0.7      # clean_yolo.py ROIConfig, verbatim

os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/claude-1000/ultra_cfg_wh")


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]


def trapezium(w, h):
    """clean_yolo.py ROIProcessor.create_trapezium_vertices, verbatim."""
    top_w = ROI_TOP_W * w
    bot_w = ROI_BOT_W * w
    roi_h = ROI_H * h
    x1, y1 = int((w - top_w) // 2), int(h - roi_h)
    x2, y2 = int((w + top_w) // 2), int(h - roi_h)
    x3, y3 = int((w - bot_w) // 2), int(h)
    x4, y4 = int((w + bot_w) // 2), int(h)
    return np.array([[x1, y1], [x2, y2], [x4, y4], [x3, y3]], dtype=np.int32)


def point_in_poly(pt, poly):
    """cv2.pointPolygonTest(..., False) >= 0, without needing cv2."""
    x, y = pt
    neg = pos = False
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        d = (x - ax) * (by - ay) - (bx - ax) * (y - ay)
        if d < 0:
            neg = True
        elif d > 0:
            pos = True
    return not (neg and pos)


def poly_fill_mask(poly, w, h):
    ys, xs = np.mgrid[0:h, 0:w]
    neg = np.zeros((h, w), bool)
    pos = np.zeros((h, w), bool)
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        d = (xs - ax) * (by - ay) - (bx - ax) * (ys - ay)
        neg |= d < 0
        pos |= d > 0
    return ~(neg & pos)


def frame_list(views=None):
    out = []
    for wname in WORLDS:
        man = json.load(open(os.path.join(HERE, "frames", wname,
                                          f"{wname}_cap_manifest.json")))
        for fr in man["frames"]:
            fn = fr["file"]
            stem = fn[:-4]
            idx = stem[-3:]
            view = stem[len(wname) + 5:-4]
            if views and view not in views:
                continue
            out.append((wname, view, idx, os.path.join(HERE, "frames", wname, fn),
                        fr["w"], fr["h"]))
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--outdir", default=os.path.join(HERE, "out", "yolo_paper"))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    if a.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    from PIL import Image
    from ultralytics import YOLO
    import torch
    import ultralytics

    frames = frame_list()
    os.makedirs(a.outdir, exist_ok=True)
    jdir = os.path.join(a.outdir, "json")
    os.makedirs(jdir, exist_ok=True)

    m = YOLO(WEIGHTS)
    names = m.names
    print(f"[yolo_paper] weights={WEIGHTS}\n[yolo_paper] names={names}  "
          f"frames={len(frames)}  imgsz={IMGSZ}  floor={FLOOR}  tau={TAU}")

    t0 = time.time()
    stats = dict(roi=dict(nbox=0, nframe=0), full=dict(nbox=0, nframe=0))
    for (world, view, idx, path, iw, ih) in frames:
        stem = f"{world}__{view}__{idx}"
        jp = os.path.join(jdir, stem + ".json")
        if os.path.exists(jp) and not a.force:
            continue
        img = np.asarray(Image.open(path).convert("RGB"))
        h, w = img.shape[:2]
        poly = trapezium(w, h)
        mask = poly_fill_mask(poly, w, h)
        roi_img = img * mask[:, :, None]                    # == cv2.bitwise_and(frame,frame,mask)
        rec = dict(frame=os.path.relpath(path, HERE), world=world, view=view, idx=idx,
                   img_w=iw, img_h=ih, imgsz=IMGSZ, pred_conf_floor=FLOOR, tau_op=TAU,
                   gate_conf=GATE_CONF, class_names=names,
                   roi_poly=poly.tolist(), arms={})
        for arm, src in (("roi", roi_img), ("full", img)):
            # ultralytics wants BGR when handed a numpy array
            r = m.predict(source=src[:, :, ::-1], imgsz=IMGSZ, conf=FLOOR,
                          device=a.device, save=False, verbose=False, max_det=MAX_DET)[0]
            b = r.boxes
            rows = []
            if b is not None and len(b):
                conf = b.conf.cpu().numpy()
                cls = b.cls.cpu().numpy().astype(int)
                xyxy = b.xyxy.cpu().numpy()
                for i in conf.argsort()[::-1]:
                    x0, y0, x1_, y1_ = (float(v) for v in xyxy[i])
                    cx, cy = (x0 + x1_) / 2.0, (y0 + y1_) / 2.0
                    rows.append(dict(cls=int(cls[i]), conf=float(conf[i]),
                                     x0=x0, y0=y0, x1=x1_, y1=y1_,
                                     cx=cx, cy=cy,
                                     in_roi=bool(point_in_poly((int(cx), int(cy)), poly))))
            keep = [d for d in rows if d["conf"] >= TAU]
            node = [d for d in keep if d["in_roi"] and d["conf"] > GATE_CONF]
            rec["arms"][arm] = dict(n_floor=len(rows), n_tau=len(keep),
                                    n_node_gate=len(node), boxes=rows)
            stats[arm]["nbox"] += len(keep)
            stats[arm]["nframe"] += 1 if keep else 0
        json.dump(rec, open(jp, "w"), indent=1)
    dt = time.time() - t0

    run = dict(weights=WEIGHTS, weights_sha256_16=sha16(WEIGHTS),
               weights_license="AGPL-3.0 (ultralytics) -- run in place, never copied",
               names=names, n_frames=len(frames), device=a.device, imgsz=IMGSZ,
               pred_conf_floor=FLOOR, tau_op=TAU, gate_conf=GATE_CONF, max_det=MAX_DET,
               roi=dict(top_w=ROI_TOP_W, bottom_w=ROI_BOT_W, height=ROI_H),
               ultralytics=ultralytics.__version__, torch=torch.__version__,
               python=platform.python_version(), wall_s=round(dt, 1),
               created=time.strftime("%Y-%m-%dT%H:%M:%S"), stats=stats)
    json.dump(run, open(os.path.join(a.outdir, "run.json"), "w"), indent=1)
    print(f"[yolo_paper] {len(frames)} frames in {dt:.1f}s  "
          f"roi: boxes(tau) {stats['roi']['nbox']} frames {stats['roi']['nframe']}  |  "
          f"full: boxes(tau) {stats['full']['nbox']} frames {stats['full']['nframe']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
