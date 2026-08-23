#!/usr/bin/env python3
"""F3 adapter-free YOLO spot-check, re-stratified under the G7-corrected GT.

Metric is IDENTICAL to weekend_0823/rt_response/code/f3_adapter_free_yolo.py (D35 / R1-F3):
a hazard-ON frame is an image-space hit iff some stored detection (conf >= tau_conf) has
IoU > t with some amodal GT box of that frame.  Nothing about the detector, the stored
detections, or the amodal boxes changes here -- ONLY the tier each frame is filed under.

The original takes the tier column from runs/yolo_s42/eval_test/per_frame.csv (old GT);
this run takes it from eval_v2corr/yolo_s42/per_frame.csv (corrected GT) and reports both
so the delta is explicit.  CPU, read-only.  -> eval_v2corr/f3_adapterfree_v2corr.json
"""
import csv
import json
import os

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
YOLO = os.path.join(REPO, "experiments/dayrun_0820/runs")
COR = os.path.join(REPO, "experiments/v3_0823/eval_v2corr")
BBOX = os.path.join(REPO, "experiments/dayrun_0820/annotations/amodal/bboxes.json")
SEEDS = (42, 43, 44)
TAU_CONFS = [0.25, 0.05]
IOU_TS = [0.0, 0.1, 0.3]
TIERS = ["V", "E", "H", "H_weak", "none_in_fov"]

bb = json.load(open(BBOX))["frames"]


def tiers_from(path):
    return {r["frame_id"]: r["tier"] for r in csv.DictReader(open(path))}


def xywh_to_xyxy(b):
    """b is either a 4-tuple or the amodal record's dict form {xc,yc,w,h}."""
    xc, yc, w, h = (b["xc"], b["yc"], b["w"], b["h"]) if isinstance(b, dict) else b
    return np.array([xc - w / 2, yc - h / 2, xc + w / 2, yc + h / 2])


def iou(a, b):
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def load_dets(seed, stem):
    p = os.path.join(YOLO, f"yolo_s{seed}", "pred_test", "labels", stem + ".txt")
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p):
        f = ln.split()
        if len(f) >= 6:
            out.append((xywh_to_xyxy([float(x) for x in f[1:5]]), float(f[5])))
    return out


def run(tier_of, frame_ids):
    """-> {tau_conf: {tier: {metric: 3-seed mean/half-range}}}"""
    res = {}
    for tc in TAU_CONFS:
        per_seed = {t: {k: [] for k in ("n", "n_gtbox", "any_det", "iou0", "iou01", "iou03",
                                        "centre_in", "best_iou")} for t in TIERS}
        for seed in SEEDS:
            acc = {t: {"n": 0, "gt": 0, "det": 0, "hit": {q: 0 for q in IOU_TS},
                       "centre": 0, "bi": 0.0} for t in TIERS}
            for fid in frame_ids:
                t = tier_of.get(fid)
                if t not in TIERS:
                    continue
                rec = bb.get(fid)
                if rec is None:
                    continue
                acc[t]["n"] += 1
                gts = [xywh_to_xyxy(b) for b in rec.get("boxes", [])]
                if gts:
                    acc[t]["gt"] += 1
                dets = [d for d in load_dets(seed, rec["stem"]) if d[1] >= tc]
                if dets:
                    acc[t]["det"] += 1
                # identical inner loop to f3_adapter_free_yolo.py:108-115
                best, centre = 0.0, False
                for db, _c in dets:
                    cx, cy = (db[0] + db[2]) / 2, (db[1] + db[3]) / 2
                    for g in gts:
                        best = max(best, iou(db, g))
                        if g[0] <= cx <= g[2] and g[1] <= cy <= g[3]:
                            centre = True
                for q in IOU_TS:
                    if best > q:
                        acc[t]["hit"][q] += 1
                acc[t]["centre"] += int(centre)
                acc[t]["bi"] += best
            for t in TIERS:
                a = acc[t]
                n = max(a["n"], 1)
                per_seed[t]["n"].append(a["n"])
                per_seed[t]["n_gtbox"].append(a["gt"])
                per_seed[t]["any_det"].append(a["det"] / n)
                per_seed[t]["iou0"].append(a["hit"][0.0] / n)
                per_seed[t]["iou01"].append(a["hit"][0.1] / n)
                per_seed[t]["iou03"].append(a["hit"][0.3] / n)
                per_seed[t]["centre_in"].append(a["centre"] / n)
                per_seed[t]["best_iou"].append(a["bi"] / n)
        res[str(tc)] = {t: {k: {"mean": float(np.mean(v)),
                                "half_range": float((max(v) - min(v)) / 2),
                                "per_seed": v}
                            for k, v in per_seed[t].items()} for t in TIERS}
    return res


def main():
    pub_pf = os.path.join(YOLO, "yolo_s42/eval_test/per_frame.csv")
    cor_pf = os.path.join(COR, "yolo_s42/per_frame.csv")
    tp, tc_ = tiers_from(pub_pf), tiers_from(cor_pf)
    assert set(tp) == set(tc_), "frame_id sets differ"
    fids = list(tp)
    out = {"provenance": {
        "detections": "experiments/dayrun_0820/runs/yolo_s{42,43,44}/pred_test/labels/*.txt (frozen)",
        "amodal_gt": "experiments/dayrun_0820/annotations/amodal/bboxes.json (frozen)",
        "tiers_published": os.path.relpath(pub_pf, REPO),
        "tiers_corrected": os.path.relpath(cor_pf, REPO),
        "metric": "image-space hit = some stored det (conf>=tau_conf) with IoU > t "
                  "against some amodal GT box of the frame (f3_adapter_free_yolo.py rule)"},
        "tier_migration": {}}
    mig = {}
    for f in fids:
        if tp[f] != tc_[f]:
            mig[f"{tp[f]}->{tc_[f]}"] = mig.get(f"{tp[f]}->{tc_[f]}", 0) + 1
    out["tier_migration"] = mig
    out["published"] = run(tp, fids)
    out["corrected"] = run(tc_, fids)
    p = os.path.join(COR, "f3_adapterfree_v2corr.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p, "| tier migration:", mig)
    for tc in TAU_CONFS:
        print(f"\n== tau_conf {tc} ==")
        print(f"{'tier':12s} {'n pub->cor':>12s} {'any_det':>16s} {'IoU>0':>16s} {'meanIoU':>16s}")
        for t in TIERS:
            P = out["published"][str(tc)][t]
            C = out["corrected"][str(tc)][t]
            print(f"{t:12s} {P['n']['mean']:5.0f}->{C['n']['mean']:5.0f}   "
                  f"{P['any_det']['mean']:6.3f}->{C['any_det']['mean']:6.3f}   "
                  f"{P['iou0']['mean']:6.3f}->{C['iou0']['mean']:6.3f} "
                  f"(±{C['iou0']['half_range']:.3f})  "
                  f"{P['best_iou']['mean']:6.3f}->{C['best_iou']['mean']:6.3f}")


if __name__ == "__main__":
    main()
