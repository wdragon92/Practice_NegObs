#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w2_yolo.py -- the PAPER'S OWN weights on the W1 warehouse frames.

WEIGHTS (read-only, never copied):
    Baseline_NegObs/src/negativeobstacleavoidandance/bot_camera/model/best.pt
    ultralytics yolov8n, nc=1, names={0:'negative_obstacle'} -- AGPL-3.0, run in place.

INPUT PIPELINE -- `bot_camera/bot_camera/clean_yolo.py::_process_image`, verbatim:
    frame  = bgr8 image                                     (cv_bridge -> here cv2.imread)
    verts  = ROIProcessor.create_trapezium_vertices(w, h)   TOP .20 W / BOTTOM .80 W / H .7 H
    cv2.polylines(frame, [verts], True, (0,255,0), 2)       <- the node DRAWS ON THE FRAME
    mask   = cv2.fillPoly(zeros(h,w), [verts], 255)
    roi    = cv2.bitwise_and(frame, frame, mask=mask)       <- YOLO sees the MASKED frame
    results= self.model(roi)                                <- ultralytics predict defaults
    keep a detection only if its box CENTRE is inside the trapezium (pointPolygonTest >= 0)

Three arms, one image load each:
    roi        node-exact: green ROI outline drawn, then masked          (PRIMARY)
    roi_nopoly masked but no outline drawn  (what gazebo_wh_0824 ran; isolates the outline)
    full       unmasked frame                                           (fairness control)

Boxes are predicted once at a low floor (conf 0.05) and the operating thresholds
{0.10, 0.25, 0.50} are applied at READ time, so a "silent" frame and a "just under the
bar" frame stay distinguishable.  0.25 is ultralytics' own predict default, i.e. exactly
what `self.model(image)` uses in the node.
"""
from __future__ import annotations

import argparse, hashlib, json, os, platform, sys, time
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "/home/vislab/Desktop/work_sy/Baseline_NegObs"
WEIGHTS = os.path.join(BASE, "src/negativeobstacleavoidandance/bot_camera/model/best.pt")

FLOOR = 0.05                                   # [방법] predict-time floor, thresholded later
TAUS = [0.10, 0.25, 0.50]                      # [도구기본값 0.25 + 2]
IMGSZ = 640                                    # [문헌] the weights' own train imgsz
MAX_DET = 300                                  # [도구기본값]
ROI_TOP_W, ROI_BOT_W, ROI_H = 0.20, 0.80, 0.7  # [문헌] clean_yolo.py ROIConfig
ARMS = ("roi", "roi_nopoly", "full")

os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/claude-1000/ultra_cfg_vth")


def sha256f(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def trapezium(w, h):
    top_w, bot_w, roi_h = ROI_TOP_W * w, ROI_BOT_W * w, ROI_H * h
    x1, y1 = int((w - top_w) // 2), int(h - roi_h)
    x2, y2 = int((w + top_w) // 2), int(h - roi_h)
    x3, y3 = int((w - bot_w) // 2), int(h)
    x4, y4 = int((w + bot_w) // 2), int(h)
    return np.array([[x1, y1], [x2, y2], [x4, y4], [x3, y3]], dtype=np.int32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="0")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "runs", "yolo_paper"))
    a = ap.parse_args()

    import cv2, torch, ultralytics
    from ultralytics import YOLO

    man = json.load(open(os.path.join(HERE, "capture_manifest.json")))
    frames = man["frames"][: a.limit] if a.limit else man["frames"]
    os.makedirs(a.out, exist_ok=True)

    m = YOLO(WEIGHTS)
    print(f"[w2yolo] weights sha256 {sha256f(WEIGHTS)[:16]}  names={m.names}  "
          f"frames={len(frames)}  device={a.device}", flush=True)

    W, Hh = frames[0]["resolution"]
    verts = trapezium(W, Hh)
    mask = np.zeros((Hh, W), np.uint8)
    cv2.fillPoly(mask, [verts], 255)

    det = {}
    t0 = time.time()
    nbox = {k: 0 for k in ARMS}
    for k, fr in enumerate(frames):
        img = cv2.imread(os.path.join(HERE, fr["rgb"]), cv2.IMREAD_COLOR)   # BGR, as cv_bridge
        drawn = img.copy()
        cv2.polylines(drawn, [verts], True, (0, 255, 0), 2)                 # node draws first
        srcs = dict(roi=cv2.bitwise_and(drawn, drawn, mask=mask),
                    roi_nopoly=cv2.bitwise_and(img, img, mask=mask),
                    full=img)
        rec = {}
        for arm in ARMS:
            r = m.predict(source=srcs[arm], imgsz=IMGSZ, conf=FLOOR, device=a.device,
                          save=False, verbose=False, max_det=MAX_DET)[0]
            b = r.boxes
            rows = []
            if b is not None and len(b):
                conf = b.conf.cpu().numpy()
                xyxy = b.xyxy.cpu().numpy()
                for i in conf.argsort()[::-1]:
                    x0, y0, x1_, y1_ = (round(float(v), 1) for v in xyxy[i])
                    cx, cy = (x0 + x1_) / 2.0, (y0 + y1_) / 2.0
                    in_roi = bool(cv2.pointPolygonTest(verts, (int(cx), int(cy)), False) >= 0)
                    rows.append([round(float(conf[i]), 4), x0, y0, x1_, y1_, int(in_roi)])
            rec[arm] = rows
            nbox[arm] += len(rows)
        det[fr["world"] + "/" + fr["pose_id"]] = rec
        if (k + 1) % 200 == 0:
            print(f"  [{k+1}/{len(frames)}] {time.time()-t0:.0f}s", flush=True)

    json.dump(dict(schema="conf,x0,y0,x1,y1,in_roi", frames=det),
              open(os.path.join(a.out, "detections.json"), "w"), separators=(",", ":"))
    run = dict(weights=WEIGHTS, weights_sha256=sha256f(WEIGHTS),
               weights_license="AGPL-3.0 (ultralytics) -- run in place, never copied",
               names={int(k): v for k, v in m.names.items()},
               n_frames=len(frames), arms=list(ARMS), device=a.device, imgsz=IMGSZ,
               pred_conf_floor=FLOOR, taus=TAUS, max_det=MAX_DET,
               roi=dict(top_w=ROI_TOP_W, bottom_w=ROI_BOT_W, height=ROI_H,
                        verts=verts.tolist(), polylines_drawn_in_arm="roi"),
               ultralytics=ultralytics.__version__, torch=torch.__version__,
               cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0)
               if torch.cuda.is_available() else None,
               python=platform.python_version(), wall_s=round(time.time() - t0, 1),
               boxes_at_floor=nbox, created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(run, open(os.path.join(a.out, "run.json"), "w"), indent=1)
    print(f"[w2yolo] done {len(frames)} frames in {time.time()-t0:.0f}s  "
          f"boxes@floor {nbox}")


if __name__ == "__main__":
    sys.exit(main())
