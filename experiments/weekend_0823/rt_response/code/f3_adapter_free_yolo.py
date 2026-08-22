"""F3 — ADAPTER-FREE YOLO DETECTION METRIC (D35 / R1-F3).

Question the ground-projection adapter cannot answer: does the trained detector put
ANY box near a hidden hazard at all?

For every hazard-ON test frame we ask, purely in image space:
    "is there a stored detection whose IoU with ANY amodal GT box exceeds t?"
for t in {0, 0.1, 0.3}, plus a centre-in-box variant.  No polar grid, no ground
projection, no det2cell.

Inputs (all frozen, read-only):
  experiments/dayrun_0820/runs/yolo_s{42,43,44}/pred_test/labels/<stem>.txt
      ultralytics save_txt+save_conf format: cls xc yc w h conf   (normalised)
      NOTE: a frame with no stored detection has NO file -> counts as zero boxes.
  experiments/dayrun_0820/annotations/amodal/bboxes.json   (amodal GT boxes)
  experiments/dayrun_0820/runs/yolo_s42/eval_test/per_frame.csv  (test frame list + tier)

Outputs: f3_adapter_free_yolo.json, F3_ADAPTER_FREE_YOLO.md
"""
import csv
import json
import os
import numpy as np
from common_rt import SEEDS, mean_hr, halfrange

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
YOLO = os.path.join(REPO, "experiments/dayrun_0820/runs")
BBOX = os.path.join(REPO, "experiments/dayrun_0820/annotations/amodal/bboxes.json")
TAU_CONFS = [0.25, 0.05]          # 0.25 = the adapter's operating point; 0.05 = every stored box
IOU_TS = [0.0, 0.1, 0.3]
TIERS = ["V", "E", "H", "H_weak", "none_in_fov"]

bb = json.load(open(BBOX))["frames"]
# test frame list + tier, taken from the YOLO row's own per_frame dump
ref = list(csv.DictReader(open(os.path.join(YOLO, "yolo_s42/eval_test/per_frame.csv"))))
frames = [(r["frame_id"], r["scene_id"], r["tier"]) for r in ref]


def stem_of(frame_id):
    return bb[frame_id]["stem"]


def xywh_to_xyxy(b):
    xc, yc, w, h = b
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
    for line in open(p):
        t = line.split()
        if len(t) < 5:
            continue
        xc, yc, w, h = (float(x) for x in t[1:5])
        conf = float(t[5]) if len(t) >= 6 else 1.0
        out.append((xywh_to_xyxy((xc, yc, w, h)), conf))
    return out


res = {"provenance": {
    "detections": "experiments/dayrun_0820/runs/yolo_s{42,43,44}/pred_test/labels/*.txt "
                  "(ultralytics save_txt/save_conf, normalised xywh+conf; frames with no "
                  "stored detection have no file and count as zero boxes)",
    "amodal_gt": "experiments/dayrun_0820/annotations/amodal/bboxes.json "
                 "(prism silhouette, occlusion ignored, per-component boxes)",
    "frame_list": "experiments/dayrun_0820/runs/yolo_s42/eval_test/per_frame.csv (816 test rows)",
    "note": "no ground projection, no polar grid, no det2cell — image space only",
}, "seeds": {}, "mean": {}, "per_scene_H": {}}

detail = {}
for seed in SEEDS:
    e = {}
    for tc in TAU_CONFS:
        per_tier = {t: {"n": 0, "n_gt_boxed": 0, "any_det": 0,
                        **{f"iou>{t2}": 0 for t2 in IOU_TS}, "centre_in_gt": 0,
                        "best_iou_sum": 0.0, "n_det_sum": 0} for t in TIERS}
        for fid, scene, tier in frames:
            if tier not in TIERS:
                continue
            rec = bb[fid]
            gts = [xywh_to_xyxy((b["xc"], b["yc"], b["w"], b["h"])) for b in rec["boxes"]]
            dets = [d for d in load_dets(seed, rec["stem"]) if d[1] >= tc]
            pt = per_tier[tier]
            pt["n"] += 1
            pt["n_det_sum"] += len(dets)
            if gts:
                pt["n_gt_boxed"] += 1
            if dets:
                pt["any_det"] += 1
            best = 0.0
            hit_centre = False
            for db, _c in dets:
                cx, cy = (db[0] + db[2]) / 2, (db[1] + db[3]) / 2
                for g in gts:
                    best = max(best, iou(db, g))
                    if g[0] <= cx <= g[2] and g[1] <= cy <= g[3]:
                        hit_centre = True
            pt["best_iou_sum"] += best
            if hit_centre:
                pt["centre_in_gt"] += 1
            for t2 in IOU_TS:
                if best > t2:
                    pt[f"iou>{t2}"] += 1
        # rates
        out = {}
        for t, pt in per_tier.items():
            n = pt["n"] or 1
            out[t] = {"n": pt["n"], "n_with_gt_box": pt["n_gt_boxed"],
                      "any_detection_rate": pt["any_det"] / n,
                      "mean_boxes_per_frame": pt["n_det_sum"] / n,
                      "mean_best_iou": pt["best_iou_sum"] / n,
                      "centre_in_gt_rate": pt["centre_in_gt"] / n,
                      **{f"rate_iou>{t2}": pt[f"iou>{t2}"] / n for t2 in IOU_TS},
                      **{f"count_iou>{t2}": pt[f"iou>{t2}"] for t2 in IOU_TS}}
        e[str(tc)] = out
    res["seeds"][str(seed)] = e

for tc in TAU_CONFS:
    res["mean"][str(tc)] = {}
    for t in TIERS:
        keys = ["any_detection_rate", "mean_boxes_per_frame", "mean_best_iou",
                "centre_in_gt_rate"] + [f"rate_iou>{x}" for x in IOU_TS]
        res["mean"][str(tc)][t] = {
            k: {"mean": mean_hr([res["seeds"][str(s)][str(tc)][t][k] for s in SEEDS]),
                "half_range": halfrange([res["seeds"][str(s)][str(tc)][t][k] for s in SEEDS]),
                "per_seed": [res["seeds"][str(s)][str(tc)][t][k] for s in SEEDS]}
            for k in keys}
        res["mean"][str(tc)][t]["n"] = res["seeds"]["42"][str(tc)][t]["n"]

# --- control A: how big are the amodal GT boxes?  IoU>0 against a facade-sized box is cheap ---
res["gt_box_geometry"] = {}
for t in TIERS:
    areas, uni = [], []
    for fid, _s, tier in frames:
        if tier != t:
            continue
        bs = bb[fid]["boxes"]
        if not bs:
            continue
        areas.append(max(b["w"] * b["h"] for b in bs))
        # union area fraction, approximated by the max box (boxes rarely overlap-free); report both
        uni.append(sum(b["w"] * b["h"] for b in bs))
    res["gt_box_geometry"][t] = {
        "n_frames_with_box": len(areas),
        "mean_largest_box_area_frac": float(np.mean(areas)) if areas else float("nan"),
        "median_largest_box_area_frac": float(np.median(areas)) if areas else float("nan"),
        "mean_summed_box_area_frac": float(np.mean(uni)) if uni else float("nan"),
    }

# --- control B: hazard-blind baseline.  Score the OFF twin's detections against the ON
#     frame's amodal GT boxes.  Same scene, same cut, same dressing, hazard removed. ---
res["hazard_blind_control"] = {}
for tc in TAU_CONFS:
    res["hazard_blind_control"][str(tc)] = {}
    for seed in SEEDS:
        per_tier = {}
        for t in ("V", "E", "H"):
            n = 0
            on_hit = {f"iou>{x}": 0 for x in IOU_TS}
            off_hit = {f"iou>{x}": 0 for x in IOU_TS}
            cond_hit = {f"iou>{x}": 0 for x in IOU_TS}
            anyd = 0
            for fid, _s, tier in frames:
                if tier != t:
                    continue
                off_fid = fid.replace("on/", "off/", 1)
                if off_fid not in bb:
                    continue
                n += 1
                gts = [xywh_to_xyxy((b["xc"], b["yc"], b["w"], b["h"])) for b in bb[fid]["boxes"]]
                don = [d for d in load_dets(seed, bb[fid]["stem"]) if d[1] >= tc]
                dof = [d for d in load_dets(seed, bb[off_fid]["stem"]) if d[1] >= tc]
                if dof:
                    anyd += 1
                b_on = max([iou(db, g) for db, _ in don for g in gts] or [0.0])
                b_off = max([iou(db, g) for db, _ in dof for g in gts] or [0.0])
                for x in IOU_TS:
                    if b_on > x:
                        on_hit[f"iou>{x}"] += 1
                    if b_off > x:
                        off_hit[f"iou>{x}"] += 1
                    if b_on > x and not b_off > x:
                        cond_hit[f"iou>{x}"] += 1
            per_tier[t] = {
                "n": n, "off_any_detection_rate": anyd / n if n else float("nan"),
                **{f"on_rate_{k}": v / n for k, v in on_hit.items()},
                **{f"off_rate_{k}": v / n for k, v in off_hit.items()},
                **{f"twin_conditional_{k}": v / n for k, v in cond_hit.items()}}
        res["hazard_blind_control"][str(tc)][str(seed)] = per_tier
    res["hazard_blind_control"][str(tc)]["mean"] = {
        t: {k: {"mean": mean_hr([res["hazard_blind_control"][str(tc)][str(s)][t][k] for s in SEEDS]),
                "half_range": halfrange([res["hazard_blind_control"][str(tc)][str(s)][t][k] for s in SEEDS]),
                "per_seed": [res["hazard_blind_control"][str(tc)][str(s)][t][k] for s in SEEDS]}
            for k in ("off_any_detection_rate", "on_rate_iou>0.0", "off_rate_iou>0.0",
                      "twin_conditional_iou>0.0", "on_rate_iou>0.1", "off_rate_iou>0.1",
                      "twin_conditional_iou>0.1")}
        for t in ("V", "E", "H")}

# H per scene, at the adapter's conf
for seed in SEEDS:
    res["per_scene_H"][str(seed)] = {}
    for sc in ("scene14", "scene15"):
        sel = [(fid, s, t) for fid, s, t in frames if t == "H" and s == sc]
        n = len(sel)
        hits = {f"iou>{t2}": 0 for t2 in IOU_TS}
        anyd = 0
        for fid, _s, _t in sel:
            rec = bb[fid]
            gts = [xywh_to_xyxy((b["xc"], b["yc"], b["w"], b["h"])) for b in rec["boxes"]]
            dets = [d for d in load_dets(seed, rec["stem"]) if d[1] >= 0.25]
            if dets:
                anyd += 1
            best = max([iou(db, g) for db, _ in dets for g in gts] or [0.0])
            for t2 in IOU_TS:
                if best > t2:
                    hits[f"iou>{t2}"] += 1
        res["per_scene_H"][str(seed)][sc] = {
            "n": n, "any_detection_rate": anyd / n,
            **{f"rate_{k}": v / n for k, v in hits.items()}}

json.dump(res, open(os.path.join(OUT, "f3_adapter_free_yolo.json"), "w"), indent=1)


def f(x, nd=3):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


L = []
L.append("# F3 — Adapter-free YOLO detection metric (RED-TEAM RESPONSE, D35 / R1-F3)\n")
L.append("Generated by `rt_response/code/f3_adapter_free_yolo.py` · CPU · read-only.\n")
L.append("**Why.** The published YOLO row reads E/H recall = 0.000, and the draft called that a "
         "property of *the detection paradigm*.  R1-F3 showed the 0 is produced by our "
         "bottom-edge ground-projection adapter: feeding the amodal GT boxes themselves in as "
         "conf-1.0 detections also yields E = H = 0.000 (`METRICS_NOTES_yolo.md` §3).  This file "
         "removes the adapter entirely and asks the detector question directly in image space.\n")
L.append("**Metric.** A hazard-ON frame is an *image-space hit* iff some stored detection "
         "(conf ≥ τ_conf) has IoU > t with some amodal GT box of that frame.  Frames with no "
         "stored detection file count as zero boxes.  Detector: yolov8n, seeds 42/43/44, the "
         "same frozen `pred_test` dumps that fed the published row.\n")

for tc in TAU_CONFS:
    tag = "τ_conf = 0.25 (the adapter's operating point)" if tc == 0.25 else \
          "τ_conf = 0.05 (every box the predictor stored)"
    L.append(f"\n## {tag}\n")
    L.append("| tier | n | frames with amodal GT box | any detection | IoU > 0 | IoU > 0.1 | "
             "IoU > 0.3 | detection centre inside a GT box | mean best IoU |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for t in TIERS:
        c = res["mean"][str(tc)][t]
        ngt = res["seeds"]["42"][str(tc)][t]["n_with_gt_box"]
        L.append("| **%s** | %d | %d | %s ±%s | **%s ±%s** | %s | %s | %s | %s |" % (
            t, c["n"], ngt,
            f(c["any_detection_rate"]["mean"]), f(c["any_detection_rate"]["half_range"]),
            f(c["rate_iou>0.0"]["mean"]), f(c["rate_iou>0.0"]["half_range"]),
            f(c["rate_iou>0.1"]["mean"]), f(c["rate_iou>0.3"]["mean"]),
            f(c["centre_in_gt_rate"]["mean"]), f(c["mean_best_iou"]["mean"])))

L.append("\n## Control A — how large is the target the detector has to hit?\n")
L.append("An IoU > 0 hit against a facade-sized amodal box is cheap, so the box geometry has to be "
         "printed next to the rate.  Areas are fractions of the image.\n")
L.append("| tier | frames with a box | mean largest-box area | median largest-box area | mean summed box area |")
L.append("|---|---|---|---|---|")
for t in TIERS:
    g = res["gt_box_geometry"][t]
    L.append("| %s | %d | %s | %s | %s |" % (
        t, g["n_frames_with_box"], f(g["mean_largest_box_area_frac"]),
        f(g["median_largest_box_area_frac"]), f(g["mean_summed_box_area_frac"])))

L.append("\n## Control B — hazard-blind baseline (the off twin's detections vs the on frame's GT boxes)\n")
L.append("Same scene, same camera cut, same dressing, hazard geometry deleted.  Any hit here is a box "
         "the detector would have produced **without** the hazard, so it bounds how much of the on-arm "
         "rate is hazard-conditional.  3-seed mean, at both confidence levels.\n")
for tc in TAU_CONFS:
    L.append(f"\n**τ_conf = {tc}**\n")
    L.append("| tier | n | on-arm IoU>0 | off-twin IoU>0 (hazard-blind) | on − off | "
             "**twin-conditional IoU>0** (on hit ∧ off miss, same cut) |")
    L.append("|---|---|---|---|---|---|")
    for t in ("V", "E", "H"):
        c = res["hazard_blind_control"][str(tc)]["mean"][t]
        on = c["on_rate_iou>0.0"]["mean"]
        off = c["off_rate_iou>0.0"]["mean"]
        cond = c["twin_conditional_iou>0.0"]
        ps = "/".join(f(x) for x in cond["per_seed"])
        L.append("| %s | %d | %s | %s | %+.3f | **%s ±%s** (%s) |" % (
            t, res["hazard_blind_control"][str(tc)]["42"][t]["n"], f(on), f(off), on - off,
            f(cond["mean"]), f(cond["half_range"]), ps))

L.append("\n## Per-seed detail (τ_conf = 0.25)\n")
L.append("| seed | tier | n | any det | IoU>0 | IoU>0.1 | IoU>0.3 | centre-in-GT |")
L.append("|---|---|---|---|---|---|---|---|")
for s in SEEDS:
    for t in TIERS:
        c = res["seeds"][str(s)]["0.25"][t]
        L.append("| %d | %s | %d | %s | %s | %s | %s | %s |" % (
            s, t, c["n"], f(c["any_detection_rate"]), f(c["rate_iou>0.0"]),
            f(c["rate_iou>0.1"]), f(c["rate_iou>0.3"]), f(c["centre_in_gt_rate"])))

L.append("\n## H tier by scene (τ_conf = 0.25)\n")
L.append("| seed | scene | n | any det | IoU>0 | IoU>0.1 | IoU>0.3 |")
L.append("|---|---|---|---|---|---|---|")
for s in SEEDS:
    for sc in ("scene14", "scene15"):
        c = res["per_scene_H"][str(s)][sc]
        L.append("| %d | %s | %d | %s | %s | %s | %s |" % (
            s, sc, c["n"], f(c["any_detection_rate"]), f(c["rate_iou>0.0"]),
            f(c["rate_iou>0.1"]), f(c["rate_iou>0.3"])))

open(os.path.join(OUT, "F3_ADAPTER_FREE_YOLO.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
