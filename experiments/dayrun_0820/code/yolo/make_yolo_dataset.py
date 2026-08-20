#!/usr/bin/env python3
"""Build an ultralytics detection dataset from the amodal boxes (Phase 5.2/5.3).

    <out>/images/{train,val,test}/<arm>__<scene>__<file>.png   SYMLINK -> round PNG
    <out>/labels/{train,val,test}/<arm>__<scene>__<file>.txt   YOLO txt
    <out>/data.yaml
    <out>/build_report.json

CONTRACT
  * images are SYMLINKS, never copies -- the 1584 round PNGs stay the single
    source of truth and the dataset dir costs kilobytes.  ultralytics resolves
    the `/images/` -> `/labels/` path substitution on the symlink path, so the
    layout above is the one it expects.
  * one class: 0 = hazard_opening.
  * one box per kept footprint component, taken from that component's amodal
    mask bbox (amodal_masks.py wrote them normalised into bboxes.json).  Because
    the boxes are normalised they are resolution-free: the mask is 960x540, the
    linked image is 1920x1080, and the same numbers are correct for both.
  * OFF-arm frames are included with an EMPTY label file -- ultralytics reads
    that as a background image, which is the whole point of the twin arm (the
    false-alarm measurement needs the detector to have seen hazard-free twins).
  * on-arm frames whose amodal mask is empty (tier `none_in_fov`: the hazard
    exists in the scene but projects outside the frame) are ALSO background.
  * split membership is by SCENE, read from the split json (D19 split v2).
    Scenes under `hold` -- and any scene the split file does not mention -- are
    excluded and reported, never silently dropped into train.

Run with PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CLASS_ID, CLASS_NAME, DAYRUN, split_frame_id  # noqa: E402

SUBSETS = ("train", "val", "test")


def label_lines(boxes):
    return [f"{CLASS_ID} {b['xc']:.6f} {b['yc']:.6f} {b['w']:.6f} {b['h']:.6f}" for b in boxes]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bboxes", default=os.path.join(DAYRUN, "annotations", "amodal",
                                                     "bboxes.json"))
    ap.add_argument("--split", default=os.path.join(DAYRUN, "split_v2.json"))
    ap.add_argument("--out", default=os.path.join(DAYRUN, "yolo_ds"))
    ap.add_argument("--subsets", default=",".join(SUBSETS))
    ap.add_argument("--copy", action="store_true", help="copy images instead of symlinking")
    ap.add_argument("--dry-run", action="store_true", help="count everything, write nothing")
    a = ap.parse_args(argv)

    doc = json.load(open(a.bboxes))
    meta, frames = doc["meta"], doc["frames"]
    split = json.load(open(a.split))
    subsets = [s for s in a.subsets.split(",") if s]
    scene2sub = {}
    for sub, scenes in split.items():
        for sc in scenes:
            scene2sub[sc] = sub

    rep = dict(created=time.strftime("%Y-%m-%dT%H:%M:%S"), bboxes=os.path.abspath(a.bboxes),
               split=os.path.abspath(a.split), out=os.path.abspath(a.out),
               grid_version=meta.get("grid_version"), clip_grid=meta.get("clip_grid"),
               mask_wh=meta.get("mask_wh"), link="copy" if a.copy else "symlink",
               subsets={}, excluded={}, missing_rgb=[], warnings=[])

    plan = {s: [] for s in subsets}
    for fid, v in sorted(frames.items()):
        arm, scene, _ = split_frame_id(fid)
        sub = scene2sub.get(scene)
        if sub is None:
            rep["excluded"].setdefault("not-in-split", {}).setdefault(scene, 0)
            rep["excluded"]["not-in-split"][scene] += 1
            continue
        if sub not in subsets:
            rep["excluded"].setdefault(sub, {}).setdefault(scene, 0)
            rep["excluded"][sub][scene] += 1
            continue
        if not os.path.isfile(v["rgb"]):
            rep["missing_rgb"].append(fid)
            continue
        plan[sub].append((fid, v))

    for sub in subsets:
        idir = os.path.join(a.out, "images", sub)
        ldir = os.path.join(a.out, "labels", sub)
        if not a.dry_run:
            os.makedirs(idir, exist_ok=True)
            os.makedirs(ldir, exist_ok=True)
        n_on = n_bg = n_box = 0
        tiers = {}
        for fid, v in plan[sub]:
            stem = v["stem"]
            lines = label_lines(v["boxes"])
            n_box += len(lines)
            n_on += (v["toggle"] == "on")
            n_bg += (len(lines) == 0)
            tiers[v.get("tier") or "?"] = tiers.get(v.get("tier") or "?", 0) + 1
            if a.dry_run:
                continue
            ip = os.path.join(idir, stem + ".png")
            if os.path.islink(ip) or os.path.exists(ip):
                os.remove(ip)
            if a.copy:
                import shutil
                shutil.copy2(v["rgb"], ip)
            else:
                os.symlink(os.path.abspath(v["rgb"]), ip)
            with open(os.path.join(ldir, stem + ".txt"), "w") as f:
                f.write("\n".join(lines) + ("\n" if lines else ""))
        rep["subsets"][sub] = dict(frames=len(plan[sub]), on=n_on, off=len(plan[sub]) - n_on,
                                   boxes=n_box, background_frames=n_bg,
                                   scenes=sorted({split_frame_id(f)[1] for f, _ in plan[sub]}),
                                   tiers=dict(sorted(tiers.items())))

    yaml = ["# ultralytics dataset -- DAYRUN 0820 Phase 5 (PROVISIONAL-GRID-V1 track)",
            f"# built {rep['created']} from {os.path.basename(a.bboxes)} + "
            f"{os.path.basename(a.split)}",
            "# images are symlinks to the round PNGs; labels are amodal per-component boxes",
            f"path: {os.path.abspath(a.out)}"]
    for s in subsets:
        yaml.append(f"{s}: images/{s}")
    yaml += ["", "names:", f"  {CLASS_ID}: {CLASS_NAME}", ""]
    if not a.dry_run:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "data.yaml"), "w") as f:
            f.write("\n".join(yaml))
        with open(os.path.join(a.out, "build_report.json"), "w") as f:
            json.dump(rep, f, indent=1)

    print(f"[dataset] {a.out}" + ("  (DRY RUN, nothing written)" if a.dry_run else ""))
    print(f"  {'subset':6s} {'frames':>7s} {'on':>5s} {'off':>5s} {'boxes':>6s} "
          f"{'bg':>5s} {'scenes':>6s}  tiers")
    for s in subsets:
        r = rep["subsets"].get(s)
        if not r:
            continue
        print(f"  {s:6s} {r['frames']:7d} {r['on']:5d} {r['off']:5d} {r['boxes']:6d} "
              f"{r['background_frames']:5d} {len(r['scenes']):6d}  "
              + " ".join(f"{k}={v}" for k, v in r["tiers"].items()))
    for k, v in rep["excluded"].items():
        print(f"  excluded[{k}]: {sum(v.values())} frames over {len(v)} scenes {sorted(v)}")
    if rep["missing_rgb"]:
        print(f"  WARN {len(rep['missing_rgb'])} frames have no RGB on disk", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
