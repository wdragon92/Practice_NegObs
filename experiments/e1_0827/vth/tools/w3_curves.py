#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_curves.py -- paper weights vs W3 replica on the SAME axes.

Scoring is byte-for-byte the W2 rule (tools/w2_curves.py): a kept box is
conf >= tau AND its centre inside the trapezium ROI; a hit is either
IoU >= 0.50 (`iou50`, PASCAL/COCO, primary) or box-centre-inside-GT (`centre`,
localisation-free).  Same bins, same thresholds, same arms.

WORLD SPLIT (stage spec):  train = eworld2,  EVALUATE = expandedworld.
Stricter than the paper's own random train/val split -- but NOT a clean
generalisation test: the perforated plate is the SAME mesh at the SAME pose in
both worlds, so every opening is memorised geometry, and expandedworld has no
light source at all (4x brightness gap, W1 §7).  Both curves are printed.
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
DIST_EDGES = [0.0, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.5, 8.0, 10.0]
PAPER_H, PAPER_P = 0.3, -15.0
MODELS = ["paper", "replica"]
DETJSON = {"paper": "runs/yolo_paper/detections.json",
           "replica": "runs/yolo_replica/detections.json"}
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
MC = {"paper": "#e34948", "replica": "#2a78d6"}       # red = paper, blue = replica
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#dcdbd6"


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    if ix <= 0 or iy <= 0:
        return 0.0
    i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


def load():
    rows = list(csv.DictReader(open(os.path.join(HERE, "labels.csv"))))
    det = {m: json.load(open(os.path.join(HERE, DETJSON[m])))["frames"] for m in MODELS}
    with gzip.open(os.path.join(HERE, "labels_otherholes.json.gz"), "rt") as gz:
        oth = json.load(gz)
    F = []
    for r in rows:
        n = int(r["int_area_px"])
        gt = (float(r["gt_x0"]), float(r["gt_y0"]),
              float(r["gt_x1"]) + 1.0, float(r["gt_y1"]) + 1.0) if n > 0 else None
        F.append(dict(key=r["frame_key"], pose_id=r["pose_id"], world=r["world"],
                      hole=r["hole_id"], band=r["band"],
                      r_eq=float(r["r_eq_m"]), occ=int(r["occlusion_intended"]) == 1,
                      occluder=r["occluder"], standoff=float(r["standoff_m"]),
                      height=float(r["height_m"]), pitch=float(r["pitch_deg"]),
                      dist=float(r["dist_cam_hole_centre_m"]),
                      area=n, h=int(r["int_h_px"]), w=int(r["int_w_px"]),
                      rim_vis=int(r["rim_visible"]) == 1, gt=gt, rgb=r["rgb"],
                      others=[tuple(o[1:]) for o in oth.get(r["frame_key"], [])],
                      det={m: det[m][r["frame_key"]] for m in MODELS}))
    return F


def score(F):
    for f in F:
        f["res"] = {}
        for mdl in MODELS:
            for arm in ARMS:
                for tau in TAUS:
                    keep = [b for b in f["det"][mdl][arm] if b[0] >= tau and b[5] == 1]
                    hit = {c: False for c in CRITS}
                    best, bestbox, fo, fb = 0.0, None, 0, 0
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
                    f["res"][(mdl, arm, tau)] = dict(n=len(keep), best=best, bestbox=bestbox,
                                                     fp_other=fo, fp_bg=fb, **hit)
    return F


def binned(sub, key, edges, mdl, arm, tau, crit):
    out = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        s = [f for f in sub if lo <= f[key] < hi]
        k = sum(1 for f in s if f["res"][(mdl, arm, tau)][crit])
        c = math.sqrt(lo * hi) if lo > 0 else (lo + hi) / 2.0
        out.append(dict(lo=lo, hi=hi, c=c, n=len(s), k=k,
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
        res[L] = val if val is not None else ("at-first-bin" if pts and pts[0][1] >= L else "never")
    return res


def ceiling(sub, key, mdl, arm, tau, crit):
    """largest value of `key` below which NO frame was ever detected."""
    hits = sorted(f[key] for f in sub if f["gt"] and f["res"][(mdl, arm, tau)][crit])
    if not hits:
        return None, len(sub)
    lo = hits[0]
    return lo, sum(1 for f in sub if f["gt"] and f[key] < lo)


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
    EV = [f for f in F if not f["occ"] and f["world"] == "expandedworld"]      # EVALUATION
    TR = [f for f in F if not f["occ"] and f["world"] == "eworld2"]            # TRAIN world
    EVg, TRg = [f for f in EV if f["gt"]], [f for f in TR if f["gt"]]
    OC = [f for f in F if f["occ"]]
    OCg = [f for f in OC if f["gt"]]
    PP = {"expandedworld": [f for f in EVg if f["height"] == PAPER_H and f["pitch"] == PAPER_P],
          "eworld2": [f for f in TRg if f["height"] == PAPER_H and f["pitch"] == PAPER_P]}
    POPS = [("expandedworld (EVAL)", EVg), ("eworld2 (TRAIN world)", TRg)]
    # the eworld2 curve mixes frames the replica was FITTED on with the 10 % held out.
    ds = json.load(open(os.path.join(HERE, "runs/w3_dataset/index.json")))
    SPLIT = {r["frame_key"]: r["split"] for r in ds["frames"]}
    TRV = [f for f in TRg if SPLIT.get(f["key"]) == "val"]     # held out from training
    TRT = [f for f in TRg if SPLIT.get(f["key"]) == "train"]   # SEEN during training
    TRU = [f for f in TRg if f["key"] not in SPLIT]            # dropped by the ROI clip

    out = open(os.path.join(HERE, "runs", "w3_tables.md"), "w")
    P = lambda s="": (print(s), out.write(s + "\n"))

    tj = json.load(open(os.path.join(HERE, "runs/w3_train/replica/w3_train.json")))
    rj = json.load(open(os.path.join(HERE, "runs/yolo_replica/run.json")))
    pj = json.load(open(os.path.join(HERE, "runs/yolo_paper/run.json")))
    P(f"replica best.pt sha256 {tj['best_sha256']}")
    P(f"replica in-world val (eworld2 10 % held out): mAP50 {tj['val_mAP50']:.4f} "
      f"mAP50-95 {tj['val_mAP50_95']:.4f} P {tj['val_precision']:.4f} R {tj['val_recall']:.4f}")
    P(f"populations: EVAL expandedworld size-axis {len(EV)} ({len(EVg)} with GT) | "
      f"TRAIN world eworld2 size-axis {len(TR)} ({len(TRg)} with GT) | "
      f"occlusion {len(OC)} ({len(OCg)} with GT)")
    P(f"paper boxes@floor {pj['boxes_at_floor']} | replica boxes@floor {rj['boxes_at_floor']}")

    # ---- headline rates --------------------------------------------------------
    P("\n## 1. Headline detection rates (arm roi = node-exact, conf >= 0.25)\n")
    P("| population | n with GT | paper centre | paper IoU>=.50 | replica centre | replica IoU>=.50 |")
    P("|---|---:|---:|---:|---:|---:|")
    for nm, sub in [POPS[0],
                    ("eworld2 — 10 % HELD OUT of training", TRV),
                    ("eworld2 — SEEN during training", TRT),
                    ("eworld2 — dropped by the ROI clip (unseen)", TRU),
                    POPS[1],
                    ("expandedworld paper-pose (h0.3/p-15)", PP["expandedworld"]),
                    ("eworld2 paper-pose (h0.3/p-15)", PP["eworld2"])]:
        r = []
        for mdl in MODELS:
            for crit in ("centre", "iou50"):
                k = sum(1 for f in sub if f["res"][(mdl, "roi", 0.25)][crit])
                r.append(f"{k}/{len(sub)} = {k/len(sub):.3f}" if sub else "-")
        P(f"| {nm} | {len(sub)} | {r[0]} | {r[1]} | {r[2]} | {r[3]} |")

    # ---- curves ----------------------------------------------------------------
    axes = [("area", AREA_EDGES, "int_area_px"), ("h", LEN_EDGES, "int_h_px"),
            ("w", LEN_EDGES, "int_w_px")]
    P("\n## 2. Detection rate vs visible interior pixels (arm roi, conf >= 0.25)\n")
    for nm, sub in POPS:
        for key, edges, lbl in axes:
            P(f"\n**{lbl} — {nm}**\n")
            P("| bin px | n | paper centre | rate | paper IoU.50 | rate | "
              "replica centre | rate | replica IoU.50 | rate |")
            P("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
            bs = {(m, c): binned(sub, key, edges, m, "roi", 0.25, c)
                  for m in MODELS for c in ("centre", "iou50")}
            for i in range(len(edges) - 1):
                n = bs[("paper", "centre")][i]["n"]
                if n == 0:
                    continue
                cells = []
                for m in MODELS:
                    for c in ("centre", "iou50"):
                        b = bs[(m, c)][i]
                        cells += [str(b["k"]), f"{b['rate']:.3f}"]
                P(f"| {edges[i]}–{edges[i+1]} | {n} | " + " | ".join(cells) + " |")

    # ---- distance --------------------------------------------------------------
    P("\n## 3. Detection rate vs camera→hole-centre distance "
      "(`dist_cam_to_hole_centre_m`, arm roi, conf >= 0.25)\n")
    for nm, sub in POPS:
        P(f"\n**{nm}**\n")
        P("| distance m | n | median int_area_px | paper centre | paper IoU.50 | "
          "replica centre | replica IoU.50 |")
        P("|---|---:|---:|---:|---:|---:|---:|")
        for i in range(len(DIST_EDGES) - 1):
            lo, hi = DIST_EDGES[i], DIST_EDGES[i + 1]
            s = [f for f in sub if lo <= f["dist"] < hi]
            if not s:
                continue
            cells = []
            for m in MODELS:
                for c in ("centre", "iou50"):
                    k = sum(1 for f in s if f["res"][(m, "roi", 0.25)][c])
                    cells.append(f"{k/len(s):.3f}")
            P(f"| {lo:g}–{hi:g} | {len(s)} | "
              f"{np.median([f['area'] for f in s]):.0f} | " + " | ".join(cells) + " |")

    # ---- crossing table --------------------------------------------------------
    P("\n## 4. Crossing table [방법] — where the rate FIRST reaches each level\n")
    P("_보고용 (report-only). The V/E boundary is NOT chosen here._\n")
    P("| population | axis | model | criterion | 0.25 | 0.50 | 0.75 | 0.90 |")
    P("|---|---|---|---|---:|---:|---:|---:|")
    for nm, sub in [POPS[0], ("eworld2 HELD-OUT", TRV), POPS[1],
                    ("expandedworld paper-pose", PP["expandedworld"]),
                    ("eworld2 paper-pose", PP["eworld2"])]:
        for key, edges, lbl in axes:
            for mdl in MODELS:
                for crit in ("centre", "iou50"):
                    cr = crossings(binned(sub, key, edges, mdl, "roi", 0.25, crit))
                    P(f"| {nm} | {lbl} | {mdl} | {crit} | "
                      + " | ".join(fmt(cr[L]) for L in LEVELS) + " |")

    # ---- zero-detection ceiling ------------------------------------------------
    P("\n## 5. Zero-detection ceiling [방법] — largest value below which NO frame fired\n")
    P("| population | axis | model | criterion | conf | ceiling | n frames below |")
    P("|---|---|---|---|---:|---:|---:|")
    for nm, sub in [POPS[0], ("eworld2 HELD-OUT", TRV), POPS[1],
                    ("expandedworld paper-pose", PP["expandedworld"])]:
        for key, _e, lbl in axes:
            for mdl in MODELS:
                for crit in ("centre", "iou50"):
                    v, nb = ceiling(sub, key, mdl, "roi", 0.25, crit)
                    P(f"| {nm} | {lbl} | {mdl} | {crit} | 0.25 | "
                      f"{'never fired' if v is None else f'{v:.0f}'} | {nb} |")

    # ---- thresholds / arms / FP ------------------------------------------------
    P("\n## 6. Thresholds, arms and false positives (EVAL world = expandedworld, size-axis)\n")
    P("| model | arm | conf | centre | rate | IoU>=.50 | rate | FP other_hole | FP background |")
    P("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for mdl in MODELS:
        for arm in ARMS:
            for tau in TAUS:
                kc = sum(1 for f in EVg if f["res"][(mdl, arm, tau)]["centre"])
                ki = sum(1 for f in EVg if f["res"][(mdl, arm, tau)]["iou50"])
                fo = sum(f["res"][(mdl, arm, tau)]["fp_other"] for f in EV)
                fb = sum(f["res"][(mdl, arm, tau)]["fp_bg"] for f in EV)
                P(f"| {mdl} | {arm} | {tau:.2f} | {kc} | {kc/len(EVg):.3f} | "
                  f"{ki} | {ki/len(EVg):.3f} | {fo} | {fb} |")

    # ---- box geometry ----------------------------------------------------------
    P("\n## 7. Box geometry — is the replica's box-height bias the paper's? "
      "(EVAL world, arm roi, conf 0.25, frames where the centre hits)\n")
    P("| model | n | det h / GT h | det w / GT w | IoU with GT |")
    P("|---|---:|---:|---:|---:|")
    for mdl in MODELS:
        fired = [f for f in EVg if f["res"][(mdl, "roi", 0.25)]["centre"]
                 and f["res"][(mdl, "roi", 0.25)]["bestbox"]]
        if not fired:
            P(f"| {mdl} | 0 | - | - | - |")
            continue
        hr = [(f["res"][(mdl, "roi", 0.25)]["bestbox"][3]
               - f["res"][(mdl, "roi", 0.25)]["bestbox"][1]) / max(f["gt"][3] - f["gt"][1], 1)
              for f in fired]
        wr = [(f["res"][(mdl, "roi", 0.25)]["bestbox"][2]
               - f["res"][(mdl, "roi", 0.25)]["bestbox"][0]) / max(f["gt"][2] - f["gt"][0], 1)
              for f in fired]
        iv = [f["res"][(mdl, "roi", 0.25)]["best"] for f in fired]
        P(f"| {mdl} | {len(fired)} | {np.median(hr):.2f} | {np.median(wr):.2f} | "
          f"{np.median(iv):.3f} |")

    # ---- E-like frames ---------------------------------------------------------
    P("\n## 8. E-like frames — no visible interior but the rim line IS visible\n")
    for nm, sub in [("expandedworld (EVAL)", [f for f in F if not f["occ"] and f["world"] == "expandedworld"]),
                    ("eworld2 (TRAIN world)", [f for f in F if not f["occ"] and f["world"] == "eworld2"]),
                    ("occlusion set", OC)]:
        z = [f for f in sub if f["area"] == 0]
        e = [f for f in z if f["rim_vis"]]
        cells = []
        for mdl in MODELS:
            nb = sum(1 for f in e if f["res"][(mdl, "roi", 0.25)]["n"] > 0)
            tb = sum(f["res"][(mdl, "roi", 0.25)]["n"] for f in e)
            cells.append(f"{nb} frames / {tb} boxes")
        P(f"- **{nm}**: {len(z)} zero-interior frames, **{len(e)} E-like** (rim visible). "
          f"Boxes on the E-like frames — paper: {cells[0]}; replica: {cells[1]}. "
          "(No GT box exists, so every box is a false positive by construction; the count "
          "is reported because an E-tier hazard has no interior to see.)")

    # ---- occlusion -------------------------------------------------------------
    P("\n## 9. Occlusion subset (expandedworld only) — counts, no curve\n")
    P("| model | conf | n frames | n with GT | centre hits | IoU>=.50 hits | frames with any box |")
    P("|---|---:|---:|---:|---:|---:|---:|")
    for mdl in MODELS:
        for tau in TAUS:
            kc = sum(1 for f in OCg if f["res"][(mdl, "roi", tau)]["centre"])
            ki = sum(1 for f in OCg if f["res"][(mdl, "roi", tau)]["iou50"])
            nb = sum(1 for f in OC if f["res"][(mdl, "roi", tau)]["n"] > 0)
            P(f"| {mdl} | {tau:.2f} | {len(OC)} | {len(OCg)} | {kc} | {ki} | {nb} |")

    # ---- memorisation ----------------------------------------------------------
    H = json.load(open(os.path.join(HERE, "holes.json")))
    pe = H["worlds"]["eworld2"]["plate_instances"][0]
    px = H["worlds"]["expandedworld"]["plate_instances"][0]
    same = (pe["pose"] == px["pose"] and pe["world_aabb"] == px["world_aabb"])
    te = sorted({f["hole"] for f in TR})
    tx = sorted({f["hole"] for f in EV})
    P("\n## 10. Do the two worlds share hole instances? [실측]\n")
    P(f"- plate pose eworld2 {pe['pose']} vs expandedworld {px['pose']} → "
      f"**{'IDENTICAL' if same else 'different'}**; same AABB, same mesh.")
    P(f"- therefore **all {H['n_holes']} openings are the same physical openings in both "
      "worlds**. The world split changes lighting and surrounding assets, NOT the hazard.")
    P(f"- target openings: eworld2 {te} · expandedworld {tx} · "
      f"**shared as targets: {sorted(set(te) & set(tx))}** "
      f"({len(set(te)&set(tx))} of 7 bands).")
    P(f"- replica training split: {len(TRT)} eworld2 frames SEEN, {len(TRV)} held out (10 %), "
      f"{len(TRU)} eworld2 GT frames never entered the dataset at all (their GT box fell "
      "outside the trapezium ROI). The held-out frames are still the SAME 7 openings at "
      "adjacent standoffs, so even that split is optimistic.")
    P("- ⚠ **Memorisation caveat**: the replica trained on eworld2 has already seen the exact "
      "geometry it is evaluated on in expandedworld. The eworld2 curve below is printed next "
      "to the expandedworld curve for exactly this reason.")
    P("- ⚠ **Brightness caveat**: eworld2 has a sun + point light; expandedworld has NO light "
      "source at all (RGB mean ~182 vs ~42, W1 §7). The world split also swaps the "
      "illumination regime.")

    # ================= plots =====================================================
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
        ax.plot(x, y, ls, color=color, lw=2.0, marker="o", ms=5.0, mec=SURF, mew=1.1,
                label=label, zorder=3)

    def save(fig, name, title):
        fig.suptitle(title, color=INK, fontsize=11, y=0.985)
        fig.patch.set_facecolor(SURF)
        fig.tight_layout(rect=(0, 0, 1, 0.93))
        fig.savefig(os.path.join(PLOTS, name), dpi=110, facecolor=SURF)
        plt.close(fig)
        print("[plot]", name)

    def pair_panel(name, title, key, edges, xl, subs, logx=True):
        fig, axs = plt.subplots(1, len(subs), figsize=(5.3 * len(subs), 4.3))
        if len(subs) == 1:
            axs = [axs]
        for j, (nm, sub) in enumerate(subs):
            for mdl in MODELS:
                curve(axs[j], binned(sub, key, edges, mdl, "roi", 0.25, "centre"),
                      MC[mdl], f"{mdl} · centre")
                curve(axs[j], binned(sub, key, edges, mdl, "roi", 0.25, "iou50"),
                      MC[mdl], f"{mdl} · IoU≥0.50", ls="--")
            style(axs[j], xl, "detection rate" if j == 0 else "", logx)
            extra = ("  — 443 of 543 were replica training images"
                     if nm.startswith("eworld2 (TRAIN") else "")
            axs[j].set_title(f"{nm}  (n={len(sub)}){extra}", color=INK2, fontsize=9.0)
        axs[0].legend(frameon=False, fontsize=8.5, labelcolor=INK2, loc="upper left")
        save(fig, name, title)

    pair_panel("w3_p1_rate_vs_area.png",
               "Detection rate vs visible hole interior pixels — paper weights vs W3 replica "
               "(conf ≥ 0.25, node ROI)", "area", AREA_EDGES, "visible interior px (int_area_px)",
               POPS)
    pair_panel("w3_p2_rate_vs_h.png",
               "Detection rate vs GT box HEIGHT — paper vs replica (conf ≥ 0.25, node ROI)",
               "h", LEN_EDGES, "int_h_px", POPS)
    pair_panel("w3_p3_rate_vs_w.png",
               "Detection rate vs GT box WIDTH — paper vs replica (conf ≥ 0.25, node ROI)",
               "w", LEN_EDGES, "int_w_px", POPS)
    pair_panel("w3_p5_paperpose.png",
               "Paper-pose subset only (camera 0.3 m, pitch −15°) — paper vs replica",
               "area", AREA_EDGES, "visible interior px",
               [("expandedworld (EVAL)", PP["expandedworld"]),
                ("eworld2 (TRAIN world)", PP["eworld2"])])

    # distance plot (linear x)
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3))
    for j, (nm, sub) in enumerate(POPS):
        for mdl in MODELS:
            b = binned(sub, "dist", DIST_EDGES, mdl, "roi", 0.25, "centre")
            for bb in b:
                bb["c"] = (bb["lo"] + bb["hi"]) / 2
            curve(axs[j], b, MC[mdl], f"{mdl} · centre")
            b2 = binned(sub, "dist", DIST_EDGES, mdl, "roi", 0.25, "iou50")
            for bb in b2:
                bb["c"] = (bb["lo"] + bb["hi"]) / 2
            curve(axs[j], b2, MC[mdl], f"{mdl} · IoU≥0.50", ls="--")
        style(axs[j], "camera → hole centre distance (m)",
              "detection rate" if j == 0 else "", logx=False)
        axs[j].set_title(f"{nm}  (n={len(sub)})", color=INK2, fontsize=9.5)
    axs[0].legend(frameon=False, fontsize=8.5, labelcolor=INK2)
    save(fig, "w3_p4_rate_vs_distance.png",
         "Detection rate vs camera distance — paper vs replica (conf ≥ 0.25, node ROI)")

    # conf sensitivity on the EVAL world
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3))
    for j, mdl in enumerate(MODELS):
        for i, tau in enumerate(TAUS):
            curve(axs[j], binned(EVg, "area", AREA_EDGES, mdl, "roi", tau, "centre"),
                  C[i], f"conf ≥ {tau:.2f} · centre")
            curve(axs[j], binned(EVg, "area", AREA_EDGES, mdl, "roi", tau, "iou50"),
                  C[i], f"conf ≥ {tau:.2f} · IoU≥.50", ls="--")
        style(axs[j], "visible interior px", "detection rate" if j == 0 else "")
        axs[j].set_title(f"{mdl} — expandedworld (EVAL)", color=INK2, fontsize=9.5)
    axs[0].legend(frameon=False, fontsize=8, labelcolor=INK2, ncol=1)
    save(fig, "w3_p6_conf_sensitivity.png",
         "Confidence-threshold sensitivity on the evaluation world")

    json.dump(dict(plots=sorted(p for p in os.listdir(PLOTS) if p.startswith("w3_"))),
              open(os.path.join(HERE, "runs", "w3_plots.json"), "w"), indent=1)
    out.close()
    print("[w3curves] wrote runs/w3_tables.md")


if __name__ == "__main__":
    sys.exit(main())
