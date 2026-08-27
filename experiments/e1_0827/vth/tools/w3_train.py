#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_train.py -- the paper's recipe, retrained on our eworld2 frames.

[문헌] Esuga-Mopah et al. 2026 recipe: YOLOv8n, COCO-pretrained, 100 epochs,
batch 16, imgsz 640, DEFAULT ultralytics augmentation, ONE class.
Everything else is left at the ultralytics default on purpose -- the point of
this stage is a replica, not a better detector.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sys, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETRAINED = "/home/vislab/Desktop/Desktop_Arrangement/workspace/isaac/isaacsim_test/yolov8n.pt"
EPOCHS, BATCH, IMGSZ, SEED = 100, 16, 640, 0
os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/claude-1000/ultra_cfg_vth")


def sha256f(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "runs/w3_dataset/data.yaml"))
    ap.add_argument("--project", default=os.path.join(HERE, "runs/w3_train"))
    ap.add_argument("--name", default="replica")
    ap.add_argument("--device", default="0")
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    a = ap.parse_args()

    import torch, ultralytics
    from ultralytics import YOLO
    from ultralytics.utils import SETTINGS
    SETTINGS.update({"sync": False})

    t0 = time.time()
    m = YOLO(PRETRAINED)
    r = m.train(data=a.data, epochs=a.epochs, batch=BATCH, imgsz=IMGSZ, seed=SEED,
                device=a.device, project=a.project, name=a.name, exist_ok=True,
                pretrained=True, val=True, plots=True, deterministic=True, verbose=True)
    wall = time.time() - t0
    sd = os.path.join(a.project, a.name)
    best = os.path.join(sd, "weights", "best.pt")
    last = os.path.join(sd, "weights", "last.pt")
    mv = YOLO(best).val(data=a.data, imgsz=IMGSZ, device=a.device, split="val",
                        project=a.project, name=a.name + "_val", exist_ok=True, plots=False)
    cfg = dict(recipe="[문헌] YOLOv8n COCO-pretrained, 100 ep, batch 16, default aug, nc=1",
               pretrained=PRETRAINED, pretrained_sha256=sha256f(PRETRAINED),
               epochs_requested=a.epochs,
               epochs_run=int(getattr(r, "epoch", a.epochs) or a.epochs) if r else a.epochs,
               batch=BATCH, imgsz=IMGSZ, seed=SEED, optimizer="auto (ultralytics default)",
               augmentation="ultralytics defaults (mosaic 1.0, hsv, scale .5, fliplr .5)",
               best=best, best_sha256=sha256f(best), last_sha256=sha256f(last),
               val_mAP50=float(mv.box.map50), val_mAP50_95=float(mv.box.map),
               val_precision=float(mv.box.mp), val_recall=float(mv.box.mr),
               ultralytics=ultralytics.__version__, torch=torch.__version__,
               cuda=torch.version.cuda,
               gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
               python=platform.python_version(), wall_s=round(wall, 1),
               created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(cfg, open(os.path.join(sd, "w3_train.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in cfg.items() if k != "pretrained_sha256"},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
