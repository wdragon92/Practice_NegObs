#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w2_curves.py -- detection rate vs visible hole pixels. Tables + plots, no smoothing.

GT        the bbox of the visible hole INTERIOR mask (labels.csv). A frame has a GT box
          iff int_area_px > 0.
KEPT BOX  conf >= tau AND the box CENTRE inside the trapezium ROI (clean_yolo.py step 4),
          applied to every arm so the arms differ only in what the network was shown.

THREE MATCH CRITERIA -- reported side by side, because they answer different questions
and on this data they disagree by an order of magnitude:
  iou50   IoU >= 0.50                      [문헌 PASCAL VOC / COCO convention]  PRIMARY
  iou25   IoU >= 0.25                      [방법] sensitivity
  centre  the box centre falls inside the GT box   [방법] "did it point at the hole at
          all", localisation-free.  Needed because this detector's boxes run tall (they
          are dragged up to the ROI mask edge), which fails IoU 0.5 on frames where the
          hole is unmistakably found -- see the box-geometry table.

FALSE POS a kept box matching no GT under `centre`. Split into `other_hole` (IoU >= 0.5
          with the projected footprint of one of the other 269 openings -- a REAL negative
          obstacle the frame happens to contain) and `background`.
RATE      hits / frames-with-GT in the bin. Bins with n = 0 print empty; nothing is
          interpolated or smoothed across a gap.
"""
from __future__ import annotations

import csv, gzip, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOTS = os.path.join(HERE, "plots")

TAUS = [0.10, 0.25, 0.50]
ARMS = ["roi", "roi_nopoly", "full"]
CRITS = ["iou50", "iou25", "centre"]
LEVELS = [0.25, 0.50, 0.75, 0.90]

AREA_EDGES = [1, 10, 32, 100, 316, 1000, 3162, 10000, 31623, 100000, 500000]
LEN_EDGES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1281]
SIZE_GROUPS = [("large", 0.35, 9.0), ("medium", 0.18, 0.35), ("small", 0.0, 0.18)]
ROI_TOP_Y = 216          # trapezium top edge for 1280x720
# [실측] the paper's own robot: bumperbot.urdf.xacro base_footprint->base_link z=0.033,
# base_link->camera_link z=0.092 => camera 0.125 m above the walking surface, rpy pitch
# 0.261 rad = 14.95 deg nose-down.  The nearest point of the brief's pose grid is
# height 0.3 m, pitch -15 deg -- the tilt matches to 0.05 deg, the height is 2.4x too high.
PAPER_H, PAPER_P = 0.3, -15.0
PAPER_CAM_H_M, PAPER_CAM_TILT_DEG = 0.125, 14.95

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#dcdbd6"


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    if ix <= 0 or iy <= 0:
        return 0.0
    i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


def size_group(r):
    for n, lo, hi in SIZE_GROUPS:
        if lo <= r < hi:
            return n
    return "small"


def load():
    rows = list(csv.DictReader(open(os.path.join(HERE, "labels.csv"))))
    det = json.load(open(os.path.join(HERE, "runs/yolo_paper/detections.json")))["frames"]
    with gzip.open(os.path.join(HERE, "labels_otherholes.json.gz"), "rt") as gz:
        oth = json.load(gz)
    F = []
    for r in rows:
        n = int(r["int_area_px"])
        gt = (float(r["gt_x0"]), float(r["gt_y0"]),
              float(r["gt_x1"]) + 1.0, float(r["gt_y1"]) + 1.0) if n > 0 else None
        F.append(dict(key=r["frame_key"], pose_id=r["pose_id"], world=r["world"],
                      hole=r["hole_id"], band=r["band"], r_eq=float(r["r_eq_m"]),
                      grp=size_group(float(r["r_eq_m"])),
                      occ=int(r["occlusion_intended"]) == 1,
                      occluder=r["occluder"], standoff=float(r["standoff_m"]),
                      height=float(r["height_m"]), pitch=float(r["pitch_deg"]),
                      dist=float(r["dist_cam_hole_centre_m"]),
                      near_rim=float(r["dist_near_rim_m"]),
                      area=n, h=int(r["int_h_px"]), w=int(r["int_w_px"]),
                      foot=int(r["foot_area_px"]),
                      occ_frac=float(r["occ_frac_asset"]) if r["occ_frac_asset"] else float("nan"),
                      rim_vis=int(r["rim_visible"]) == 1, gt=gt, rgb=r["rgb"],
                      others=[tuple(o[1:]) for o in oth.get(r["frame_key"], [])],
                      det=det[r["frame_key"]]))
    return F


def score(F):
    for f in F:
        f["res"] = {}
        for arm in ARMS:
            for tau in TAUS:
                keep = [b for b in f["det"][arm] if b[0] >= tau and b[5] == 1]
                hit = {c: False for c in CRITS}
                best, bestbox = 0.0, None
                fo = fb = 0
                for b in keep:
                    bb = (b[1], b[2], b[3], b[4])
                    v = iou(bb, f["gt"]) if f["gt"] else 0.0
                    if v > best:
                        best, bestbox = v, bb
                    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
                    inside = bool(f["gt"] and f["gt"][0] <= cx <= f["gt"][2]
                                  and f["gt"][1] <= cy <= f["gt"][3])
                    if v >= 0.50:
                        hit["iou50"] = True
                    if v >= 0.25:
                        hit["iou25"] = True
                    if inside:
                        hit["centre"] = True
                    if not inside and v < 0.25:
                        if any(iou(bb, o) >= 0.5 for o in f["others"]):
                            fo += 1
                        else:
                            fb += 1
                f["res"][(arm, tau)] = dict(n=len(keep), best=best, bestbox=bestbox,
                                            fp_other=fo, fp_bg=fb, **hit)
    return F


def binned(sub, key, edges, arm, tau, crit):
    out = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        s = [f for f in sub if lo <= f[key] < hi]
        k = sum(1 for f in s if f["res"][(arm, tau)][crit])
        out.append(dict(lo=lo, hi=hi, c=math.sqrt(lo * hi), n=len(s), k=k,
                        rate=(k / len(s)) if s else None))
    return out


def binned_vals(sub, key, vals, arm, tau, crit):
    out = []
    for v in vals:
        s = [f for f in sub if f[key] == v]
        k = sum(1 for f in s if f["res"][(arm, tau)][crit])
        out.append(dict(lo=v, hi=v, c=v, n=len(s), k=k,
                        rate=(k / len(s)) if s else None))
    return out


def crossings(bins, log=True):
    pts = [(b["c"], b["rate"]) for b in bins if b["n"] > 0]
    res = {}
    for L in LEVELS:
        val = None
        for i in range(1, len(pts)):
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            if y0 < L <= y1:
                a0 = math.log10(x0) if log else x0
                a1 = math.log10(x1) if log else x1
                t = (L - y0) / (y1 - y0)
                val = 10 ** (a0 + t * (a1 - a0)) if log else a0 + t * (a1 - a0)
                break
        if val is None:
            val = ("at-first-bin" if pts and pts[0][1] >= L else "never")
        res[L] = val
    return res


def fmt(v):
    if v is None:
        return "-"
    if isinstance(v, str):
        return v
    return f"{v:.0f}" if v >= 100 else f"{v:.2f}"


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(PLOTS, exist_ok=True)
    F = score(load())
    main_all = [f for f in F if not f["occ"]]
    main_gt = [f for f in main_all if f["gt"]]
    occ_all = [f for f in F if f["occ"]]
    occ_gt = [f for f in occ_all if f["gt"]]
    sos = sorted({f["standoff"] for f in main_all})
    bands = ["L1", "L2", "M1", "M2", "S1", "S2", "T1"]

    out = open(os.path.join(HERE, "runs", "w2_tables.md"), "w")
    P = lambda s="": (print(s), out.write(s + "\n"))

    P(f"populations: all {len(F)} | size-axis (occlusion_intended=false) {len(main_all)}, "
      f"with a GT box {len(main_gt)} | occlusion set {len(occ_all)}, with a GT box {len(occ_gt)}")

    # ---- 1. label distribution ------------------------------------------------
    P("\n## 1. Visible interior pixels vs standoff (size-axis population)\n")
    P("| standoff m | n | min | p25 | median | p75 | max | int_area_px = 0 |")
    P("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for s in sos:
        a = np.array([f["area"] for f in main_all if f["standoff"] == s], float)
        P(f"| {s:g} | {len(a)} | {a.min():.0f} | {np.percentile(a,25):.0f} | {np.median(a):.0f} | "
          f"{np.percentile(a,75):.0f} | {a.max():.0f} | {int((a==0).sum())} |")

    P("\n**median int_area_px by size band x standoff** (blank = no frame)\n")
    P("| band | r_eq m | " + " | ".join(f"{s:g} m" for s in sos) + " |")
    P("|---|---:|" + "---:|" * len(sos))
    for b in bands:
        sb = [f for f in main_all if f["band"] == b]
        if not sb:
            continue
        cs = [(f"{np.median([f['area'] for f in sb if f['standoff']==s]):.0f}"
               if any(f["standoff"] == s for f in sb) else "") for s in sos]
        P(f"| {b} | {np.median([f['r_eq'] for f in sb]):.3f} | " + " | ".join(cs) + " |")

    z = [f for f in F if f["area"] == 0]
    zr = [f for f in z if f["rim_vis"]]
    P(f"\n**E-like frames** — int_area_px == 0 while the rim line IS visible: **{len(zr)}** "
      f"of {len(z)} zero-interior frames (size-axis {sum(1 for f in zr if not f['occ'])}, "
      f"occlusion {sum(1 for f in zr if f['occ'])}).\n")
    P("| world | band | n int=0 | n rim_visible |")
    P("|---|---|---:|---:|")
    for k in sorted({(f["world"], f["band"]) for f in z}):
        s = [f for f in z if (f["world"], f["band"]) == k]
        P(f"| {k[0]} | {k[1]} | {len(s)} | {sum(1 for f in s if f['rim_vis'])} |")

    # ---- 2. the localisation problem ------------------------------------------
    P("\n## 2. Why two criteria — the detector's boxes run tall\n")
    fired = [f for f in main_gt if f["res"][("roi", 0.25)]["centre"]]
    hr, wr, topd = [], [], []
    for f in fired:
        b = f["res"][("roi", 0.25)]["bestbox"]
        if not b:
            continue
        g = f["gt"]
        hr.append((b[3] - b[1]) / max(g[3] - g[1], 1))
        wr.append((b[2] - b[0]) / max(g[2] - g[0], 1))
        topd.append(b[1] - ROI_TOP_Y)
    P(f"On the {len(fired)} size-axis frames where a kept box's centre lands inside the GT box "
      f"(arm roi, tau 0.25):\n")
    P("| quantity | median | p10 | p90 |")
    P("|---|---:|---:|---:|")
    P(f"| det box height / GT height | {np.median(hr):.2f} | {np.percentile(hr,10):.2f} | {np.percentile(hr,90):.2f} |")
    P(f"| det box width / GT width | {np.median(wr):.2f} | {np.percentile(wr,10):.2f} | {np.percentile(wr,90):.2f} |")
    P(f"| det box top − ROI top edge (px) | {np.median(topd):.0f} | {np.percentile(topd,10):.0f} | {np.percentile(topd,90):.0f} |")
    P(f"| IoU with GT | {np.median([f['res'][('roi',0.25)]['best'] for f in fired]):.3f} | "
      f"{np.percentile([f['res'][('roi',0.25)]['best'] for f in fired],10):.3f} | "
      f"{np.percentile([f['res'][('roi',0.25)]['best'] for f in fired],90):.3f} |")
    near = sum(1 for t in topd if abs(t) <= 12)
    P(f"\n{near} of {len(topd)} of those boxes start within 12 px of the ROI mask's top edge "
      f"(y = {ROI_TOP_Y}) — the box is dragged up to the black mask boundary. That is why the "
      "IoU-0.50 rate and the centre rate differ by ~5x below.")

    # ---- 3. curves -------------------------------------------------------------
    axes = [("area", AREA_EDGES, True, "int_area_px"),
            ("h", LEN_EDGES, True, "int_h_px"),
            ("w", LEN_EDGES, True, "int_w_px")]
    P("\n## 3. Detection rate vs visible pixels — arm `roi` (node-exact)\n")
    for key, edges, lg, nm in axes:
        for tau in TAUS:
            P(f"\n**{nm} · conf ≥ {tau:.2f}**\n")
            P("| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |")
            P("|---|---:|---:|---:|---:|---:|")
            b5 = binned(main_gt, key, edges, "roi", tau, "iou50")
            bc = binned(main_gt, key, edges, "roi", tau, "centre")
            for x, y in zip(b5, bc):
                r5 = "" if x["rate"] is None else f"{x['rate']:.3f}"
                rc_ = "" if y["rate"] is None else f"{y['rate']:.3f}"
                P(f"| {x['lo']:g}–{x['hi']:g} | {x['n']} | {x['k']} | {r5} | {y['k']} | {rc_} |")
    for tau in TAUS:
        P(f"\n**standoff m · conf ≥ {tau:.2f}**\n")
        P("| standoff m | n frames | IoU≥0.50 | rate | centre-hit | rate |")
        P("|---:|---:|---:|---:|---:|---:|")
        b5 = binned_vals(main_gt, "standoff", sos, "roi", tau, "iou50")
        bc = binned_vals(main_gt, "standoff", sos, "roi", tau, "centre")
        for x, y in zip(b5, bc):
            P(f"| {x['lo']:g} | {x['n']} | {x['k']} | {x['rate']:.3f} | {y['k']} | {y['rate']:.3f} |")

    P("\n### stratified by physical hole size (conf ≥ 0.25, arm roi, centre-hit / IoU≥0.50)\n")
    P("| int_area_px bin | " + " | ".join(f"{g}" for g, _, _ in SIZE_GROUPS) + " |")
    P("|---|" + "---|" * len(SIZE_GROUPS))
    pc = {g: binned([f for f in main_gt if f["grp"] == g], "area", AREA_EDGES, "roi", 0.25, "centre")
          for g, _, _ in SIZE_GROUPS}
    p5 = {g: binned([f for f in main_gt if f["grp"] == g], "area", AREA_EDGES, "roi", 0.25, "iou50")
          for g, _, _ in SIZE_GROUPS}
    for i in range(len(AREA_EDGES) - 1):
        cs = []
        for g, _, _ in SIZE_GROUPS:
            b, b2 = pc[g][i], p5[g][i]
            cs.append(f"n={b['n']} {b['rate']:.2f} / {b2['rate']:.2f}" if b["n"] else "–")
        P(f"| {AREA_EDGES[i]:g}–{AREA_EDGES[i+1]:g} | " + " | ".join(cs) + " |")

    P("\n### stratified by world (conf ≥ 0.25, arm roi, centre-hit / IoU≥0.50)\n")
    P("| int_area_px bin | eworld2 | expandedworld |")
    P("|---|---|---|")
    for i in range(len(AREA_EDGES) - 1):
        cs = []
        for w in ("eworld2", "expandedworld"):
            s = [f for f in main_gt if f["world"] == w]
            b = binned(s, "area", AREA_EDGES, "roi", 0.25, "centre")[i]
            b2 = binned(s, "area", AREA_EDGES, "roi", 0.25, "iou50")[i]
            cs.append(f"n={b['n']} {b['rate']:.2f} / {b2['rate']:.2f}" if b["n"] else "–")
        P(f"| {AREA_EDGES[i]:g}–{AREA_EDGES[i+1]:g} | " + " | ".join(cs) + " |")

    P("\n### centre-hit rate by size band and standoff (conf ≥ 0.25, arm roi)\n")
    P("| band | " + " | ".join(f"{s:g} m" for s in sos) + " |")
    P("|---|" + "---:|" * len(sos))
    for b in bands:
        sb = [f for f in main_gt if f["band"] == b]
        if not sb:
            continue
        cs = []
        for s in sos:
            g = [f for f in sb if f["standoff"] == s]
            cs.append(f"{sum(1 for f in g if f['res'][('roi',0.25)]['centre'])/len(g):.2f}" if g else "")
        P(f"| {b} | " + " | ".join(cs) + " |")

    # ---- 3b. pose dependence and the paper-pose subset --------------------------
    P("\n### centre-hit rate by camera height x pitch (conf ≥ 0.25, arm roi) — n in brackets\n")
    P("| height above walking surface | pitch −15° | pitch −5° | pitch +5° |")
    P("|---:|---:|---:|---:|")
    for hh in sorted({f["height"] for f in main_gt}):
        cs = []
        for pp in (-15.0, -5.0, 5.0):
            s = [f for f in main_gt if f["height"] == hh and f["pitch"] == pp]
            cs.append(f"{sum(1 for f in s if f['res'][('roi',0.25)]['centre'])/len(s):.3f} ({len(s)})"
                      if s else "–")
        P(f"| {hh:g} m | " + " | ".join(cs) + " |")
    P(f"\nThe paper's own camera sits **{PAPER_CAM_H_M:.3f} m** above the walking surface at "
      f"**{PAPER_CAM_TILT_DEG:.2f}°** nose-down (bumperbot.urdf.xacro, [실측]). The closest "
      f"point of the brief's pose grid is height {PAPER_H:g} m / pitch {PAPER_P:g}° — the tilt "
      "matches to 0.05°, the height is 2.4x too high. Rate falls off hard with camera height, "
      "so the aggregate rate above is dominated by poses this detector was never trained for.")

    pp_sub = [f for f in main_gt if f["height"] == PAPER_H and f["pitch"] == PAPER_P]
    P(f"\n### PAPER-POSE SUBSET — height {PAPER_H:g} m, pitch {PAPER_P:g}° "
      f"({len(pp_sub)} frames with a GT box)\n")
    P("This is the subset whose camera geometry is closest to the paper's own robot; read the "
      "detection limit here, not off the pooled curve.\n")
    P("| int_area_px bin | n | centre-hit | rate | IoU≥0.50 | rate | eworld2 rate | expandedworld rate |")
    P("|---|---:|---:|---:|---:|---:|---:|---:|")
    bc = binned(pp_sub, "area", AREA_EDGES, "roi", 0.25, "centre")
    b5 = binned(pp_sub, "area", AREA_EDGES, "roi", 0.25, "iou50")
    be = binned([f for f in pp_sub if f["world"] == "eworld2"], "area", AREA_EDGES, "roi", 0.25, "centre")
    bx = binned([f for f in pp_sub if f["world"] == "expandedworld"], "area", AREA_EDGES, "roi", 0.25, "centre")
    for i in range(len(AREA_EDGES) - 1):
        if bc[i]["n"] == 0:
            continue
        e = "" if be[i]["rate"] is None else f"{be[i]['rate']:.3f} (n={be[i]['n']})"
        x = "" if bx[i]["rate"] is None else f"{bx[i]['rate']:.3f} (n={bx[i]['n']})"
        P(f"| {AREA_EDGES[i]:g}–{AREA_EDGES[i+1]:g} | {bc[i]['n']} | {bc[i]['k']} | "
          f"{bc[i]['rate']:.3f} | {b5[i]['k']} | {b5[i]['rate']:.3f} | {e} | {x} |")
    P("\n| standoff m | n | centre-hit | rate | IoU≥0.50 | rate | median int_area_px |")
    P("|---:|---:|---:|---:|---:|---:|---:|")
    for s in sos:
        g = [f for f in pp_sub if f["standoff"] == s]
        if not g:
            continue
        kc = sum(1 for f in g if f["res"][("roi", 0.25)]["centre"])
        k5 = sum(1 for f in g if f["res"][("roi", 0.25)]["iou50"])
        P(f"| {s:g} | {len(g)} | {kc} | {kc/len(g):.3f} | {k5} | {k5/len(g):.3f} | "
          f"{np.median([f['area'] for f in g]):.0f} |")

    # ---- 3c. the zero-detection ceiling ----------------------------------------
    P("\n### Zero-detection ceiling [방법] — the largest value below which NO frame was ever detected\n")
    P("| population | axis | criterion | conf | ceiling | n frames below it |")
    P("|---|---|---|---:|---:|---:|")
    for pname, pop in (("all size-axis", main_gt), (f"paper-pose (h {PAPER_H:g}, p {PAPER_P:g})", pp_sub)):
        for ax, nm in (("area", "int_area_px"), ("h", "int_h_px"), ("w", "int_w_px")):
            for crit in ("centre", "iou50"):
                for tau in (0.10, 0.25):
                    hits = [f[ax] for f in pop if f["res"][("roi", tau)][crit]]
                    if not hits:
                        P(f"| {pname} | {nm} | {crit} | {tau:.2f} | never detected | {len(pop)} |")
                        continue
                    mn = min(hits)
                    P(f"| {pname} | {nm} | {crit} | {tau:.2f} | {mn} | "
                      f"{sum(1 for f in pop if f[ax] < mn)} |")

    # ---- 4. crossings ----------------------------------------------------------
    P("\n## 4. Crossing table [방법] — where the rate first reaches each level (arm roi)\n")
    P("_Report-only. The boundary is NOT chosen here._\n")
    P("| axis | criterion | conf | 0.25 | 0.50 | 0.75 | 0.90 |")
    P("|---|---|---:|---:|---:|---:|---:|")
    for key, edges, lg, nm in axes:
        for crit in ("centre", "iou50"):
            for tau in TAUS:
                cr = crossings(binned(main_gt, key, edges, "roi", tau, crit), log=lg)
                P(f"| {nm} | {crit} | {tau:.2f} | " + " | ".join(fmt(cr[L]) for L in LEVELS) + " |")
    for key, edges, lg, nm in axes:
        for crit in ("centre", "iou50"):
            cr = crossings(binned(pp_sub, key, edges, "roi", 0.25, crit), log=lg)
            P(f"| {nm} · PAPER-POSE | {crit} | 0.25 | " + " | ".join(fmt(cr[L]) for L in LEVELS) + " |")
    P("\n_The standoff axis runs downhill (rate falls with distance) so an upward-crossing "
      "value is meaningless for it; read it off the standoff table in §3._")

    # ---- 5. arms, thresholds, false positives ---------------------------------
    P("\n## 5. Arms, thresholds and false positives (size-axis population)\n")
    P("| arm | conf | detected IoU≥0.50 | rate | detected centre | rate | mean best IoU | FP other_hole | FP background |")
    P("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for arm in ARMS:
        for tau in TAUS:
            k5 = sum(1 for f in main_gt if f["res"][(arm, tau)]["iou50"])
            kc = sum(1 for f in main_gt if f["res"][(arm, tau)]["centre"])
            bi = np.mean([f["res"][(arm, tau)]["best"] for f in main_gt])
            fo = sum(f["res"][(arm, tau)]["fp_other"] for f in main_all)
            fb = sum(f["res"][(arm, tau)]["fp_bg"] for f in main_all)
            P(f"| {arm} | {tau:.2f} | {k5} | {k5/len(main_gt):.3f} | {kc} | {kc/len(main_gt):.3f} | "
              f"{bi:.3f} | {fo} | {fb} |")

    P("\n**Frames with NO GT box** (int_area_px == 0): every kept box is a false positive\n")
    P("| population | arm | conf | n frames | frames with ≥1 box | other_hole boxes | background boxes |")
    P("|---|---|---:|---:|---:|---:|---:|")
    for nm2, pop in (("size-axis", [f for f in main_all if not f["gt"]]),
                     ("occlusion", [f for f in occ_all if not f["gt"]])):
        for arm in ARMS:
            for tau in TAUS:
                nf = sum(1 for f in pop if f["res"][(arm, tau)]["n"])
                fo = sum(f["res"][(arm, tau)]["fp_other"] for f in pop)
                fb = sum(f["res"][(arm, tau)]["fp_bg"] for f in pop)
                P(f"| {nm2} | {arm} | {tau:.2f} | {len(pop)} | {nf} | {fo} | {fb} |")

    # ---- 6. occlusion ----------------------------------------------------------
    P("\n## 6. Occlusion subset (occlusion_intended = true, expandedworld only)\n")
    P(f"{len(occ_all)} frames, {len(occ_gt)} with any visible interior. `occ_frac` = the share "
      "of the opening's analytic footprint whose ray is stopped ABOVE the walking surface by a "
      "real asset, measured from the depth image (0.000 on all 1135 size-axis frames).\n")
    P("| occ_frac bin | n frames | n with GT | median int_area_px | centre-hit | IoU≥0.50 |")
    P("|---|---:|---:|---:|---:|---:|")
    for lo, hi in [(0.0, 0.01), (0.01, 0.5), (0.5, 0.9), (0.9, 0.999), (0.999, 1.0001)]:
        s = [f for f in occ_all if lo <= f["occ_frac"] < hi]
        if not s:
            continue
        g = [f for f in s if f["gt"]]
        kc = sum(1 for f in g if f["res"][("roi", 0.25)]["centre"])
        k5 = sum(1 for f in g if f["res"][("roi", 0.25)]["iou50"])
        P(f"| {lo:g}–{min(hi,1.0):g} | {len(s)} | {len(g)} | {np.median([f['area'] for f in s]):.0f} | "
          + (f"{kc} ({kc/len(g):.3f}) | {k5} ({k5/len(g):.3f}) |" if g else "– | – |"))
    P("\n| occluder asset | n frames | n with GT | centre-hit (conf ≥ 0.25) |")
    P("|---|---:|---:|---:|")
    byoc = {}
    for f in occ_all:
        byoc.setdefault(f["occluder"] or "(none)", []).append(f)
    for oc, s in sorted(byoc.items(), key=lambda kv: -len(kv[1])):
        g = [f for f in s if f["gt"]]
        P(f"| {oc} | {len(s)} | {len(g)} | "
          f"{sum(1 for f in g if f['res'][('roi',0.25)]['centre'])} |")

    # ---- plots -----------------------------------------------------------------
    def style(ax, xl, yl, logx=True):
        ax.set_facecolor(SURF)
        ax.set_xlabel(xl, color=INK2, fontsize=9)
        ax.set_ylabel(yl, color=INK2, fontsize=9)
        ax.set_ylim(-0.03, 1.03)
        if logx:
            ax.set_xscale("log")
        ax.grid(True, color=GRID, lw=0.7)
        ax.set_axisbelow(True)
        for s in ax.spines.values():
            s.set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=8)

    def curve(ax, bins, color, label, ls="-"):
        x = [b["c"] for b in bins if b["n"]]
        y = [b["rate"] for b in bins if b["n"]]
        ax.plot(x, y, ls, color=color, lw=2.0, marker="o", ms=5.5, mec=SURF, mew=1.2,
                label=label, zorder=3)

    def save(fig, name, title):
        fig.suptitle(title, color=INK, fontsize=11, y=0.985)
        fig.patch.set_facecolor(SURF)
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig(os.path.join(PLOTS, name), dpi=110, facecolor=SURF)
        plt.close(fig)
        print("[plot]", name)

    plots = []

    def two_panel(name, title, mk, xl, logx=True):
        fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3))
        for j, crit in enumerate(("centre", "iou50")):
            for i, tau in enumerate(TAUS):
                curve(axs[j], mk(crit, tau), C[i], f"conf ≥ {tau:.2f}")
            style(axs[j], xl, "detection rate" if j == 0 else "", logx)
            axs[j].set_title("centre-hit (localisation-free)" if crit == "centre"
                             else "IoU >= 0.50 (PASCAL/COCO)",
                             color=INK2, fontsize=9.5)
        axs[0].legend(frameon=False, fontsize=9, labelcolor=INK2)
        save(fig, name, title)

    two_panel("p1_rate_vs_area.png",
              "Detection rate vs visible hole pixels — paper weights, node ROI",
              lambda c, t: binned(main_gt, "area", AREA_EDGES, "roi", t, c),
              "visible hole interior  [px]")
    plots.append("p1_rate_vs_area.png — rate vs int_area_px, 3 conf thresholds x 2 match criteria")

    two_panel("p2_rate_vs_h.png", "Detection rate vs GT box height",
              lambda c, t: binned(main_gt, "h", LEN_EDGES, "roi", t, c), "int_h_px  [px]")
    plots.append("p2_rate_vs_h.png — rate vs int_h_px")
    two_panel("p3_rate_vs_w.png", "Detection rate vs GT box width",
              lambda c, t: binned(main_gt, "w", LEN_EDGES, "roi", t, c), "int_w_px  [px]")
    plots.append("p3_rate_vs_w.png — rate vs int_w_px")
    two_panel("p4_rate_vs_standoff.png", "Detection rate vs camera standoff to the near rim",
              lambda c, t: binned_vals(main_gt, "standoff", sos, "roi", t, c),
              "standoff  [m]", logx=False)
    plots.append("p4_rate_vs_standoff.png — rate vs standoff")

    # stratified
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3))
    for i, (g, _, _) in enumerate(SIZE_GROUPS):
        curve(axs[0], binned([f for f in main_gt if f["grp"] == g], "area", AREA_EDGES,
                             "roi", 0.25, "centre"), C[i], f"{g} hole")
        curve(axs[1], binned_vals([f for f in main_gt if f["grp"] == g], "standoff", sos,
                                  "roi", 0.25, "centre"), C[i], f"{g} hole")
    style(axs[0], "visible hole interior  [px]", "centre-hit rate  (conf ≥ 0.25)")
    style(axs[1], "standoff  [m]", "", logx=False)
    axs[0].legend(frameon=False, fontsize=9, labelcolor=INK2)
    save(fig, "p5_bysize.png", "Stratified by physical hole size (equivalent radius)")
    plots.append("p5_bysize.png — rate vs area and vs standoff, split small/medium/large")

    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3))
    for i, w in enumerate(("eworld2", "expandedworld")):
        s = [f for f in main_gt if f["world"] == w]
        curve(axs[0], binned(s, "area", AREA_EDGES, "roi", 0.25, "centre"), C[i], w)
        curve(axs[1], binned_vals(s, "standoff", sos, "roi", 0.25, "centre"), C[i], w)
    style(axs[0], "visible hole interior  [px]", "centre-hit rate  (conf ≥ 0.25)")
    style(axs[1], "standoff  [m]", "", logx=False)
    axs[0].legend(frameon=False, fontsize=9, labelcolor=INK2)
    save(fig, "p6_byworld.png", "Stratified by world — note the 4x brightness gap (W1 §7)")
    plots.append("p6_byworld.png — rate vs area and vs standoff, split by world")

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for i, arm in enumerate(ARMS):
        curve(ax, binned(main_gt, "area", AREA_EDGES, arm, 0.25, "centre"), C[i], arm)
    style(ax, "visible hole interior  [px]", "centre-hit rate  (conf ≥ 0.25)")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2)
    save(fig, "p7_byarm.png", "What the network is shown: node ROI vs mask-without-outline vs full frame")
    plots.append("p7_byarm.png — rate vs int_area_px for the three input arms")

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for i, (g, _, _) in enumerate(SIZE_GROUPS):
        s = [f for f in main_all if f["grp"] == g]
        ax.scatter([f["standoff"] + (i - 1) * 0.07 for f in s], [max(f["area"], 0.5) for f in s],
                   s=11, color=C[i], alpha=0.55, edgecolors="none", label=f"{g} hole", zorder=3)
    style(ax, "standoff to the near rim  [m]", "visible hole interior  [px]", logx=False)
    ax.set_yscale("log")
    ax.set_ylim(0.3, 1e6)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2)
    save(fig, "p8_area_vs_standoff.png",
         "The measurement itself: visible interior pixels vs standoff (0 px drawn at 0.5)")
    plots.append("p8_area_vs_standoff.png — int_area_px vs standoff scatter (label distribution)")

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    xs, ys, ys2, ns = [], [], [], []
    for lo, hi in [(0.0, 0.01), (0.01, 0.5), (0.5, 0.9), (0.9, 1.0001)]:
        s = [f for f in occ_all if lo <= f["occ_frac"] < hi and f["gt"]]
        if not s:
            continue
        xs.append(len(xs))
        ns.append(len(s))
        ys.append(sum(1 for f in s if f["res"][("roi", 0.25)]["centre"]) / len(s))
        ys2.append(sum(1 for f in s if f["res"][("roi", 0.25)]["iou50"]) / len(s))
        ax.set_xticks(xs)
    ax.bar([x - 0.18 for x in xs], ys, width=0.34, color=C[0], label="centre-hit", zorder=3)
    ax.bar([x + 0.18 for x in xs], ys2, width=0.34, color=C[1], label="IoU ≥ 0.50", zorder=3)
    for x, n in zip(xs, ns):
        ax.text(x, 0.94, f"n={n}", ha="center", color=INK2, fontsize=8)
    if max(ys + ys2) == 0:
        ax.text(np.mean(xs), 0.45, "not one detection in any bin",
                ha="center", color=INK2, fontsize=11)
    ax.set_xticks(xs)
    ax.set_xticklabels(["0–0.01", "0.01–0.5", "0.5–0.9", "0.9–1.0"][:len(xs)])
    style(ax, "occluded fraction of the opening's footprint", "detection rate  (conf ≥ 0.25)", logx=False)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2)
    save(fig, "p9_occlusion.png", "Occlusion subset — detection vs how much of the opening an asset hides")
    plots.append("p9_occlusion.png — occlusion subset, rate vs occluded fraction")

    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3))
    for i, w in enumerate(("eworld2", "expandedworld")):
        s_ = [f for f in pp_sub if f["world"] == w]
        curve(axs[0], binned(s_, "area", AREA_EDGES, "roi", 0.25, "centre"), C[i], w)
        curve(axs[1], binned_vals(s_, "standoff", sos, "roi", 0.25, "centre"), C[i], w)
    curve(axs[0], binned(pp_sub, "area", AREA_EDGES, "roi", 0.25, "iou50"), C[2], "both, IoU≥0.50", "--")
    curve(axs[1], binned_vals(pp_sub, "standoff", sos, "roi", 0.25, "iou50"), C[2], "both, IoU≥0.50", "--")
    style(axs[0], "visible hole interior  [px]", "detection rate  (conf ≥ 0.25)")
    style(axs[1], "standoff  [m]", "", logx=False)
    axs[0].legend(frameon=False, fontsize=9, labelcolor=INK2)
    save(fig, "p10_paperpose.png",
         "PAPER-POSE subset: camera 0.3 m up, 15° down — closest to the paper's own robot")
    plots.append("p10_paperpose.png — the paper-pose subset, rate vs area and vs standoff, by world")

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    hs = sorted({f["height"] for f in main_gt})
    for i, pp_ in enumerate((-15.0, -5.0, 5.0)):
        ys, xs2 = [], []
        for hh in hs:
            s_ = [f for f in main_gt if f["height"] == hh and f["pitch"] == pp_]
            if s_:
                xs2.append(hh)
                ys.append(sum(1 for f in s_ if f["res"][("roi", 0.25)]["centre"]) / len(s_))
        ax.plot(xs2, ys, color=C[i], lw=2.0, marker="o", ms=6, mec=SURF, mew=1.2,
                label=f"pitch {pp_:+.0f}°", zorder=3)
    style(ax, "camera height above the walking surface  [m]", "centre-hit rate  (conf ≥ 0.25)", logx=False)
    ax.axvline(PAPER_CAM_H_M, color=INK2, lw=1.2, ls=":")
    ax.text(PAPER_CAM_H_M + 0.03, 0.92, "paper's own camera 0.125 m", color=INK2, fontsize=8)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2)
    save(fig, "p11_pose_dependence.png", "The detector is pose-bound: rate vs camera height and pitch")
    plots.append("p11_pose_dependence.png — centre-hit rate vs camera height, by pitch")

    json.dump(plots, open(os.path.join(HERE, "runs", "w2_plots.json"), "w"), indent=1)
    out.close()
    print("[w2curves] tables -> runs/w2_tables.md ; plots ->", PLOTS)


if __name__ == "__main__":
    sys.exit(main())
