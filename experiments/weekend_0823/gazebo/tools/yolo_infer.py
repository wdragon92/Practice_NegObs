#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yolo_infer.py — frozen YOLOv8n (3 seeds) over the 216 frozen Gazebo frames.

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      experiments/dayrun_0820/venv_yolo/bin/python tools/yolo_infer.py

WHAT
    The detection-side twin of `infer_run.sh`.  Same 216 PNGs, same frozen
    weights the DAYRUN track trained (`runs/yolo_s{42,43,44}/weights/best.pt`),
    same imgsz (512) and same predict-time floor (conf 0.05) the frozen
    `run_yolo_all.sh` used, so the operating point tau_conf 0.25 is applied at
    READ time exactly as `det2cell.py --conf` does it upstream.  Predicting at
    0.25 directly would delete the sub-threshold boxes and make the "is it
    silence or is it just under the bar?" question unanswerable.

OUTPUT (new tree; nothing under out/ or out_v3/ is touched)
    out_yolo/pred/yolo_s<seed>/labels/<world>__<view>__<idx>.txt
        frozen ultralytics txt grammar: `class cx cy w h conf` (normalised).
        Written ONLY when the frame has >= 1 box above the floor -- byte-grammar
        identical to runs/yolo_s*/pred_test/labels, so panel_f's reader works.
    out_yolo/pred/yolo_s<seed>/json/<world>__<view>__<idx>.json
        written for EVERY frame including the empty ones (216/216), because the
        false-alarm and detection-rate denominators must count silence.
    out_yolo/pred/yolo_s<seed>/run.json   provenance + wall clock

CPU only by default.  GPU is optional and not needed: 648 forwards at imgsz 512.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
GZ = os.path.join(ROOT, "experiments/weekend_0823/gazebo")
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
FRAMES = os.path.join(GZ, "frames")
OUT = os.path.join(GZ, "out_yolo", "pred")

WORLDS = ["gz_drop1", "gz_drop1_ctrl", "gz_drop2", "gz_drop2_ctrl",
          "gz_drop3", "gz_drop3_ctrl", "gz_drop4", "gz_drop4_ctrl"]
SEEDS = (42, 43, 44)
IMGSZ = 512
FLOOR = 0.05          # predict-time floor (frozen run_yolo_all.sh value)
TAU = 0.25            # frozen operating point, applied at read time
MAX_DET = 300

os.environ.setdefault("YOLO_CONFIG_DIR", os.path.join(DAY, "venv_yolo", "ultralytics_cfg"))


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]


def frame_list():
    """-> [(world, view, idx, path)] sorted, from the frozen manifests."""
    out = []
    for w in WORLDS:
        man = json.load(open(os.path.join(FRAMES, w, f"{w}_cap_manifest.json")))
        for fr in man["frames"]:
            fn = fr["file"]
            stem = fn[:-4]
            idx = stem[-3:]
            assert stem.startswith(f"{w}_cap_") and idx.isdigit(), stem
            view = stem[len(w) + 5:-4]
            p = os.path.join(FRAMES, w, fn)
            if not os.path.isfile(p):
                raise SystemExit(f"[fatal] missing frame {p}")
            out.append((w, view, idx, p, fr["w"], fr["h"]))
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seeds", default=",".join(str(s) for s in SEEDS))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    if a.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    from ultralytics import YOLO
    import torch
    import ultralytics

    frames = frame_list()
    print(f"[yolo_infer] {len(frames)} frames x {len(a.seeds.split(','))} seeds  "
          f"device={a.device}  imgsz={IMGSZ}  floor={FLOOR}  (tau_op {TAU} applied at read)")

    for seed in [int(s) for s in a.seeds.split(",")]:
        w = os.path.join(DAY, f"runs/yolo_s{seed}/weights/best.pt")
        if not os.path.isfile(w):
            raise SystemExit(f"[fatal] no weights: {w}")
        rd = os.path.join(OUT, f"yolo_s{seed}")
        ldir, jdir = os.path.join(rd, "labels"), os.path.join(rd, "json")
        os.makedirs(ldir, exist_ok=True)
        os.makedirs(jdir, exist_ok=True)
        done = len([f for f in os.listdir(jdir) if f.endswith(".json")])
        if done == len(frames) and not a.force:
            print(f"[yolo_infer] seed {seed}: {done}/{len(frames)} json present — skip "
                  f"(--force to redo)")
            continue
        m = YOLO(w)
        names = m.names
        t0 = time.time()
        nbox_floor = nbox_tau = nframe_tau = 0
        for (world, view, idx, path, iw, ih) in frames:
            stem = f"{world}__{view}__{idx}"
            r = m.predict(source=path, imgsz=IMGSZ, conf=FLOOR, device=a.device,
                          save=False, save_txt=False, verbose=False, max_det=MAX_DET)[0]
            b = r.boxes
            n = 0 if b is None else len(b)
            rows = []
            if n:
                xywhn = b.xywhn.cpu().numpy()
                conf = b.conf.cpu().numpy()
                cls = b.cls.cpu().numpy().astype(int)
                xyxy = b.xyxy.cpu().numpy()          # pixels, in ORIGINAL frame resolution
                order = conf.argsort()[::-1]
                for i in order:
                    rows.append(dict(cls=int(cls[i]),
                                     cx=float(xywhn[i][0]), cy=float(xywhn[i][1]),
                                     w=float(xywhn[i][2]), h=float(xywhn[i][3]),
                                     conf=float(conf[i]),
                                     x0=float(xyxy[i][0]), y0=float(xyxy[i][1]),
                                     x1=float(xyxy[i][2]), y1=float(xyxy[i][3])))
            keep = [d for d in rows if d["conf"] >= TAU]
            nbox_floor += len(rows)
            nbox_tau += len(keep)
            nframe_tau += 1 if keep else 0
            if rows:                                  # frozen txt grammar, floor-level
                with open(os.path.join(ldir, stem + ".txt"), "w") as f:
                    for d in rows:
                        f.write(f"{d['cls']} {d['cx']:.6f} {d['cy']:.6f} "
                                f"{d['w']:.6f} {d['h']:.6f} {d['conf']:.6f}\n")
            elif os.path.exists(os.path.join(ldir, stem + ".txt")):
                os.remove(os.path.join(ldir, stem + ".txt"))
            json.dump(dict(frame=os.path.relpath(path, ROOT), world=world, view=view,
                           idx=idx, img_w=iw, img_h=ih, seed=seed, imgsz=IMGSZ,
                           pred_conf_floor=FLOOR, tau_op=TAU, class_names=names,
                           n_boxes_floor=len(rows), n_boxes_tau=len(keep), boxes=rows),
                      open(os.path.join(jdir, stem + ".json"), "w"), indent=1)
        dt = time.time() - t0
        json.dump(dict(seed=seed, weights=os.path.relpath(w, ROOT),
                       weights_sha256_16=sha16(w), n_frames=len(frames),
                       device=a.device, imgsz=IMGSZ, pred_conf_floor=FLOOR, tau_op=TAU,
                       max_det=MAX_DET, ultralytics=ultralytics.__version__,
                       torch=torch.__version__, python=platform.python_version(),
                       wall_s=round(dt, 1), created=time.strftime("%Y-%m-%dT%H:%M:%S"),
                       n_boxes_floor=nbox_floor, n_boxes_tau=nbox_tau,
                       n_frames_with_box_tau=nframe_tau),
                  open(os.path.join(rd, "run.json"), "w"), indent=1)
        print(f"[yolo_infer] seed {seed}: {len(frames)} frames in {dt:.1f}s  "
              f"boxes(floor {FLOOR}) {nbox_floor}  boxes(tau {TAU}) {nbox_tau}  "
              f"frames-with-box(tau) {nframe_tau}/{len(frames)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
