#!/usr/bin/env python3
"""YOLOv8n train / predict wrapper for the DAYRUN 0820 Phase 5 track.

Thin on purpose: every hyper-parameter the brief fixed is a default here and
nothing else is touched, so the three seed runs differ ONLY in `seed`.

    model    yolov8n.pt (COCO pretrained, vendored at venv_yolo/weights/)
    imgsz    512          epochs 60          batch 16
    seed     --seed       deterministic=True
    run dir  experiments/dayrun_0820/runs/yolo_s<seed>/

MODES
    train    (default) fine-tune and leave weights/best.pt in the run dir
    predict  run a trained best.pt over a dataset subset with save_txt=True
             save_conf=True at a LOW conf floor, so det2cell.py can sweep the
             threshold upward afterwards.  Predicting at conf=0.25 and then
             "sweeping" 0.1 would silently be a no-op -- the detections below
             the predict-time floor no longer exist.
    sanity   2-image CPU fit (epochs 1, imgsz 128) that proves data.yaml, the
             symlinks, the label files and the ultralytics install all line up.
             Writes into a throwaway dir and deletes it unless --keep.

MUST be run with the track's own interpreter:
    experiments/dayrun_0820/venv_yolo/bin/python
and with PYTHONNOUSERSITE=1.  While the render owns the GPU, also export
CUDA_VISIBLE_DEVICES="" and pass --device cpu.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DAYRUN  # noqa: E402

WEIGHTS = os.path.join(DAYRUN, "venv_yolo", "weights", "yolov8n.pt")
RUNS = os.path.join(DAYRUN, "runs")
DATA = os.path.join(DAYRUN, "yolo_ds", "data.yaml")

os.environ.setdefault("YOLO_CONFIG_DIR", os.path.join(DAYRUN, "venv_yolo", "ultralytics_cfg"))


def _yolo():
    from ultralytics import YOLO
    return YOLO


def do_train(a):
    YOLO = _yolo()
    m = YOLO(a.model)
    m.train(data=a.data, imgsz=a.imgsz, epochs=a.epochs, batch=a.batch, seed=a.seed,
            deterministic=True, project=a.project, name=a.name, exist_ok=a.exist_ok,
            device=a.device, workers=a.workers, patience=a.patience, val=True,
            plots=a.plots, verbose=True)
    print(f"[train_yolo] done -> {os.path.join(a.project, a.name, 'weights', 'best.pt')}")
    return 0


def do_predict(a):
    YOLO = _yolo()
    src = a.source or os.path.join(DAYRUN, "yolo_ds", "images", a.subset)
    run = os.path.join(a.project, a.name)          # the training run this predicts FROM
    w = a.weights or os.path.join(run, "weights", "best.pt")
    if not os.path.isfile(w):
        raise SystemExit(f"[fatal] no weights at {w}")
    name = a.pred_name or f"pred_{a.subset}"
    m = YOLO(w)
    m.predict(source=src, imgsz=a.imgsz, conf=a.pred_conf, device=a.device,
              save=False, save_txt=True, save_conf=True, stream=False, verbose=False,
              project=run, name=name, exist_ok=True, max_det=a.max_det)
    out = os.path.join(run, name, "labels")
    n = len([f for f in os.listdir(out) if f.endswith(".txt")]) if os.path.isdir(out) else 0
    print(f"[train_yolo] predict conf>={a.pred_conf} -> {out}  ({n} images with detections)")
    return 0


def do_sanity(a):
    """2 images, 1 epoch, imgsz 128, CPU. Proves the pipeline end to end."""
    import glob
    import json
    YOLO = _yolo()
    ds = os.path.dirname(a.data)
    tmp = a.sanity_dir or os.path.join(DAYRUN, "runs", "_sanity_tmp")
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    # one image WITH boxes and one background image, so both label paths are exercised
    pos = neg = None
    for lp in sorted(glob.glob(os.path.join(ds, "labels", "train", "*.txt"))):
        n = sum(1 for ln in open(lp) if ln.strip())
        if n and pos is None:
            pos = lp
        elif not n and neg is None:
            neg = lp
        if pos and neg:
            break
    if not (pos and neg):
        raise SystemExit(f"[fatal] sanity needs one boxed and one background label in {ds}")
    for sub in ("train", "val"):
        os.makedirs(os.path.join(tmp, "images", sub), exist_ok=True)
        os.makedirs(os.path.join(tmp, "labels", sub), exist_ok=True)
        for lp in (pos, neg):
            stem = os.path.splitext(os.path.basename(lp))[0]
            ip = os.path.join(ds, "images", "train", stem + ".png")
            os.symlink(os.path.realpath(ip), os.path.join(tmp, "images", sub, stem + ".png"))
            shutil.copy2(lp, os.path.join(tmp, "labels", sub, stem + ".txt"))
    with open(os.path.join(tmp, "data.yaml"), "w") as f:
        f.write(f"path: {tmp}\ntrain: images/train\nval: images/val\n\nnames:\n  0: hazard_opening\n")
    print(f"[sanity] 2 images ({os.path.basename(pos)} = boxed, "
          f"{os.path.basename(neg)} = background) -> {tmp}")
    t0 = time.time()
    m = YOLO(a.model)
    r = m.train(data=os.path.join(tmp, "data.yaml"), imgsz=128, epochs=1, batch=2,
                seed=a.seed, deterministic=True, project=tmp, name="fit", exist_ok=True,
                device="cpu", workers=0, val=True, plots=False, verbose=False)
    rd = os.path.join(tmp, "fit")
    best = os.path.join(rd, "weights", "best.pt")
    res = getattr(r, "results_dict", {}) or {}
    print(f"[sanity] PASS epochs=1 imgsz=128 batch=2 device=cpu  {time.time() - t0:.1f}s  "
          f"best.pt={os.path.isfile(best)} ({os.path.getsize(best) if os.path.isfile(best) else 0} B)  "
          f"metrics={json.dumps({k: round(float(v), 5) for k, v in res.items()})}")
    if a.keep:
        print(f"[sanity] kept {tmp}")
    else:
        shutil.rmtree(tmp)
        print(f"[sanity] throwaway run dir deleted: {tmp}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["train", "predict", "sanity"], default="train")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--data", default=DATA)
    ap.add_argument("--model", default=WEIGHTS)
    ap.add_argument("--imgsz", type=int, default=512)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--patience", type=int, default=15)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--device", default="0", help="'0' for the 4090, 'cpu' while the render runs")
    ap.add_argument("--project", default=RUNS)
    ap.add_argument("--name", default=None, help="default yolo_s<seed>")
    ap.add_argument("--exist-ok", action="store_true")
    ap.add_argument("--plots", action="store_true", default=True)
    # predict
    ap.add_argument("--subset", default="test")
    ap.add_argument("--source", default=None)
    ap.add_argument("--weights", default=None)
    ap.add_argument("--pred-conf", type=float, default=0.05,
                    help="predict-time floor; keep BELOW the lowest det2cell sweep threshold")
    ap.add_argument("--pred-name", default=None)
    ap.add_argument("--max-det", type=int, default=300)
    # sanity
    ap.add_argument("--sanity-dir", default=None)
    ap.add_argument("--keep", action="store_true", help="sanity: keep the throwaway run dir")
    a = ap.parse_args(argv)
    a.name = a.name or f"yolo_s{a.seed}"
    if a.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    print(f"[train_yolo] mode={a.mode} seed={a.seed} model={a.model} data={a.data} "
          f"device={a.device} -> {os.path.join(a.project, a.name)}")
    return dict(train=do_train, predict=do_predict, sanity=do_sanity)[a.mode](a)


if __name__ == "__main__":
    sys.exit(main())
