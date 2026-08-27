#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_infer.py -- run ONE weights file over every W1 frame, exactly like w2_yolo.py.

Same three arms, same ROI trapezium, same predict-time conf floor 0.05, same
centre-in-ROI keep rule, same output schema -- so runs/yolo_paper/detections.json
and runs/yolo_replica/detections.json are directly comparable.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sys, time
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOOR, IMGSZ, MAX_DET = 0.05, 640, 300
TAUS = [0.10, 0.25, 0.50]
ROI_TOP_W, ROI_BOT_W, ROI_H = 0.20, 0.80, 0.7
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
    ap.add_argument("--weights", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="0")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    import cv2, torch, ultralytics
    from ultralytics import YOLO

    man = json.load(open(os.path.join(HERE, "capture_manifest.json")))
    frames = man["frames"][: a.limit] if a.limit else man["frames"]
    os.makedirs(a.out, exist_ok=True)
    m = YOLO(a.weights)
    print(f"[w3infer] {os.path.basename(a.weights)} sha {sha256f(a.weights)[:16]} "
          f"names={m.names} frames={len(frames)}", flush=True)

    W, Hh = frames[0]["resolution"]
    verts = trapezium(W, Hh)
    mask = np.zeros((Hh, W), np.uint8)
    cv2.fillPoly(mask, [verts], 255)

    det, nbox, t0 = {}, {k: 0 for k in ARMS}, time.time()
    for k, fr in enumerate(frames):
        img = cv2.imread(os.path.join(HERE, fr["rgb"]), cv2.IMREAD_COLOR)
        drawn = img.copy()
        cv2.polylines(drawn, [verts], True, (0, 255, 0), 2)
        srcs = dict(roi=cv2.bitwise_and(drawn, drawn, mask=mask),
                    roi_nopoly=cv2.bitwise_and(img, img, mask=mask), full=img)
        rec = {}
        for arm in ARMS:
            r = m.predict(source=srcs[arm], imgsz=IMGSZ, conf=FLOOR, device=a.device,
                          save=False, verbose=False, max_det=MAX_DET)[0]
            b, rows = r.boxes, []
            if b is not None and len(b):
                conf, xyxy = b.conf.cpu().numpy(), b.xyxy.cpu().numpy()
                for i in conf.argsort()[::-1]:
                    x0, y0, x1_, y1_ = (round(float(v), 1) for v in xyxy[i])
                    cx, cy = (x0 + x1_) / 2.0, (y0 + y1_) / 2.0
                    in_roi = bool(cv2.pointPolygonTest(verts, (int(cx), int(cy)), False) >= 0)
                    rows.append([round(float(conf[i]), 4), x0, y0, x1_, y1_, int(in_roi)])
            rec[arm] = rows
            nbox[arm] += len(rows)
        det[fr["world"] + "/" + fr["pose_id"]] = rec
        if (k + 1) % 400 == 0:
            print(f"  [{k+1}/{len(frames)}] {time.time()-t0:.0f}s", flush=True)

    json.dump(dict(schema="conf,x0,y0,x1,y1,in_roi", frames=det),
              open(os.path.join(a.out, "detections.json"), "w"), separators=(",", ":"))
    json.dump(dict(weights=a.weights, weights_sha256=sha256f(a.weights),
                   names={int(k): v for k, v in m.names.items()}, n_frames=len(frames),
                   arms=list(ARMS), device=a.device, imgsz=IMGSZ, pred_conf_floor=FLOOR,
                   taus=TAUS, max_det=MAX_DET,
                   roi=dict(top_w=ROI_TOP_W, bottom_w=ROI_BOT_W, height=ROI_H,
                            verts=verts.tolist(), polylines_drawn_in_arm="roi"),
                   ultralytics=ultralytics.__version__, torch=torch.__version__,
                   cuda=torch.version.cuda, python=platform.python_version(),
                   gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                   wall_s=round(time.time() - t0, 1), boxes_at_floor=nbox,
                   created=time.strftime("%Y-%m-%dT%H:%M:%S")),
              open(os.path.join(a.out, "run.json"), "w"), indent=1)
    print(f"[w3infer] done {len(frames)} in {time.time()-t0:.0f}s boxes@floor {nbox}")


if __name__ == "__main__":
    sys.exit(main())
