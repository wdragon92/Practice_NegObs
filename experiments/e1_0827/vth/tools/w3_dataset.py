#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_dataset.py -- build the YOLO training set for the W3 replica.

RECIPE (the paper's, replicated):
  * images  = the EXACT input the paper's node feeds its network
              (clean_yolo.py::_process_image, same as W2 arm `roi`):
                  draw the green trapezium outline on the BGR frame, then
                  bitwise_and it with the filled trapezium mask.
              Resize to 640 is ultralytics' own letterbox at train time
              (imgsz=640, the weights' own train setting) -- not done here.
  * labels  = ONE class, the TARGET opening's visible-interior bbox from
              labels.csv (`int_area_px > 0`), clipped to the trapezium.
  * split   = eworld2 only; 10 % of frames held out for checkpoint selection.

Non-target openings in the same frame are NOT labelled (W1 hand-off note 4 /
the stage spec: "GT box = interior bbox").  That is a documented limitation:
median other-opening projection is 18 px^2 / 0.9 px tall, but ~1.5 per frame
exceed 400 px^2, and the replica is therefore trained to call those background.
"""
from __future__ import annotations
import argparse, csv, json, os, random, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROI_TOP_W, ROI_BOT_W, ROI_H = 0.20, 0.80, 0.7   # [문헌] clean_yolo.py ROIConfig
TRAIN_WORLD = "eworld2"                          # [방법] stage spec: world split
VAL_FRAC = 0.10                                  # [방법]
SPLIT_SEED = 0                                   # [방법]
MIN_CLIPPED_PX = 20                              # [방법] drop slivers left by the ROI clip
CLASS_NAMES = ["hole"]                           # [방법] one class


def trapezium(w, h):
    top_w, bot_w, roi_h = ROI_TOP_W * w, ROI_BOT_W * w, ROI_H * h
    x1, y1 = int((w - top_w) // 2), int(h - roi_h)
    x2, y2 = int((w + top_w) // 2), int(h - roi_h)
    x3, y3 = int((w - bot_w) // 2), int(h)
    x4, y4 = int((w + bot_w) // 2), int(h)
    return np.array([[x1, y1], [x2, y2], [x4, y4], [x3, y3]], dtype=np.int32)


def clip_to_trapezium(box, verts, W, H):
    """bbox of (box AND trapezium).  Exact: the trapezium's row extent is widest
    at its bottom row, so over any y-range the union of row extents is the extent
    at the largest y in that range."""
    x0, y0, x1, y1 = box
    ytop, ybot = float(verts[0][1]), float(verts[2][1])
    xl_top, xr_top = float(verts[0][0]), float(verts[1][0])
    xl_bot, xr_bot = float(verts[3][0]), float(verts[2][0])
    y0 = max(y0, ytop); y1 = min(y1, ybot)
    if y1 <= y0:
        return None
    t = (y1 - ytop) / (ybot - ytop)          # widest row inside the clipped range
    xl = xl_top + t * (xl_bot - xl_top)
    xr = xr_top + t * (xr_bot - xr_top)
    x0 = max(x0, xl); x1 = min(x1, xr)
    if x1 <= x0:
        return None
    return (x0, y0, x1, y1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "runs", "w3_dataset"))
    a = ap.parse_args()
    import cv2

    rows = list(csv.DictReader(open(os.path.join(HERE, "labels.csv"))))
    man = json.load(open(os.path.join(HERE, "capture_manifest.json")))
    W, H = man["frames"][0]["resolution"]
    verts = trapezium(W, H)
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [verts], 255)

    cand = [r for r in rows
            if r["world"] == TRAIN_WORLD
            and int(r["occlusion_intended"]) == 0
            and int(r["int_area_px"]) > 0]
    kept, drop_clip = [], 0
    for r in cand:
        box = (float(r["gt_x0"]), float(r["gt_y0"]),
               float(r["gt_x1"]) + 1.0, float(r["gt_y1"]) + 1.0)
        cb = clip_to_trapezium(box, verts, W, H)
        if cb is None or (cb[2] - cb[0]) < 2 or (cb[3] - cb[1]) < 2 \
           or (cb[2] - cb[0]) * (cb[3] - cb[1]) < MIN_CLIPPED_PX:
            drop_clip += 1
            continue
        kept.append((r, cb))

    rnd = random.Random(SPLIT_SEED)
    idx = list(range(len(kept)))
    rnd.shuffle(idx)
    nval = max(1, int(round(VAL_FRAC * len(kept))))
    valset = set(idx[:nval])

    for sp in ("train", "val"):
        for sub in ("images", "labels"):
            d = os.path.join(a.out, sub, sp)
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d, exist_ok=True)

    counts = {"train": 0, "val": 0}
    index = []
    for i, (r, cb) in enumerate(kept):
        sp = "val" if i in valset else "train"
        img = cv2.imread(os.path.join(HERE, r["rgb"]), cv2.IMREAD_COLOR)
        drawn = img.copy()
        cv2.polylines(drawn, [verts], True, (0, 255, 0), 2)     # node draws first
        roi = cv2.bitwise_and(drawn, drawn, mask=mask)
        stem = r["pose_id"]
        cv2.imwrite(os.path.join(a.out, "images", sp, stem + ".png"), roi,
                    [cv2.IMWRITE_PNG_COMPRESSION, 3])
        cx = (cb[0] + cb[2]) / 2 / W
        cy = (cb[1] + cb[3]) / 2 / H
        bw = (cb[2] - cb[0]) / W
        bh = (cb[3] - cb[1]) / H
        with open(os.path.join(a.out, "labels", sp, stem + ".txt"), "w") as fh:
            fh.write(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
        counts[sp] += 1
        index.append(dict(frame_key=r["frame_key"], split=sp, hole=r["hole_id"],
                          band=r["band"], standoff=float(r["standoff_m"]),
                          height=float(r["height_m"]), pitch=float(r["pitch_deg"]),
                          int_area_px=int(r["int_area_px"]),
                          gt=[round(v, 1) for v in cb]))

    yml = os.path.join(a.out, "data.yaml")
    with open(yml, "w") as fh:
        fh.write(f"path: {a.out}\ntrain: images/train\nval: images/val\n"
                 f"nc: {len(CLASS_NAMES)}\nnames: {CLASS_NAMES}\n")
    meta = dict(train_world=TRAIN_WORLD, candidates=len(cand),
                dropped_by_roi_clip=drop_clip, kept=len(kept),
                n_train=counts["train"], n_val=counts["val"],
                val_frac=VAL_FRAC, split_seed=SPLIT_SEED,
                min_clipped_px=MIN_CLIPPED_PX, resolution=[W, H],
                roi_verts=verts.tolist(), classes=CLASS_NAMES,
                label_source="labels.csv gt_x0..gt_y1 (visible interior bbox), "
                             "clipped to the trapezium ROI",
                other_openings_labelled=False)
    json.dump(dict(meta=meta, frames=index),
              open(os.path.join(a.out, "index.json"), "w"), indent=1)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    sys.exit(main())
