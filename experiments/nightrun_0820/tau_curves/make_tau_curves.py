#!/usr/bin/env python
"""B3 -- recall/FA seed scatter + tau sweep curves (CPU only, reads frozen prob dumps).

Reads the stored per-frame probability dumps written by mainrun_0819/code/eval_polar.py
(`write_per_frame`) and re-derives, at every tau on a grid, the two frame-level headline
numbers the paper table uses:

    frame_recall_<T>  : among hazard-ON frames that carry >=1 GT-positive cell and are in
                        evidence tier T, the fraction where SOME GT-positive cell fires.
    frame_fa_off      : among hazard-OFF frames, the fraction where ANY cell fires.

Both definitions are copied verbatim from eval_polar.bundle() so the tau=0.5 column here
must reproduce the SEED_TABLE numbers exactly (that equality is asserted-by-eye in the md).

Writes nothing outside its own directory.
"""
from __future__ import annotations

import csv
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V2 = os.path.join(REPO, "experiments/dayrun_0820/runs/v2")
YOLO = os.path.join(REPO, "experiments/dayrun_0820/runs/yolo_s42/eval_test/per_frame.csv")
OUT = os.path.join(REPO, "experiments/nightrun_0820/tau_curves")

MODELS = ["rgb", "depth", "b2"]           # fixed order == categorical slot order
SEEDS = [42, 43, 44]
TIERS = ["V", "E", "H"]
TAUS = np.round(np.arange(0.05, 0.951, 0.05), 2)
TAU_OP = 0.50
TAU_YOLO = 0.25

# --- palette (dataviz skill reference instance, light mode) -------------------------
# slots 1-4 in documented order; the first three validate on the all-pairs list (scatter),
# all four on the adjacent list (lines).  Every line is also direct-labelled, which
# discharges the relief rule for the low-contrast yellow slot.
SLOT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
MODEL_C = {"rgb": SLOT[0], "depth": SLOT[1], "b2": SLOT[2]}
SERIES_C = {"V": SLOT[0], "E": SLOT[1], "H": SLOT[2], "FA": SLOT[3]}
INK, INK2, GRID = "#1a1a19", "#63625c", "#e4e3de"
YOLO_C = "#3d3c37"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 9, "axes.titlesize": 10.5, "axes.labelsize": 9,
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "legend.frameon": False, "legend.fontsize": 8,
    "savefig.dpi": 170, "savefig.bbox": "tight",
})


# --- io ----------------------------------------------------------------------------
def read_per_frame(path):
    with open(path) as f:
        rd = csv.DictReader(f)
        cells = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        tier, tog, P, G = [], [], [], []
        for r in rd:
            tier.append(r["tier"]); tog.append(r["toggle_state"])
            P.append([float(r[f"p_{c}"]) for c in cells])
            G.append([float(r[f"g_{c}"]) for c in cells])
    return dict(tier=np.array(tier), tog=np.array(tog),
                P=np.asarray(P, float), G=np.asarray(G, float), cells=cells)


def _ratio(a, b):
    return float(a) / float(b) if b > 0 else float("nan")


def curve(d):
    """frame recall per tier + off-arm frame FA at every tau on TAUS."""
    pos = d["G"] > 0.5
    on, off = d["tog"] == "on", d["tog"] == "off"
    haz = on & pos.any(1)
    sel = {t: haz & (d["tier"] == t) for t in TIERS}
    out = {t: [] for t in TIERS}
    out["FA"] = []
    for tau in TAUS:
        pred = d["P"] >= tau
        det = (pred & pos).any(1)
        for t in TIERS:
            out[t].append(_ratio(det[sel[t]].sum(), sel[t].sum()))
        out["FA"].append(_ratio(pred[off].any(1).sum(), off.sum()))
    return {k: np.asarray(v, float) for k, v in out.items()}, \
           {t: int(sel[t].sum()) for t in TIERS} | {"off": int(off.sum())}


def at(cur, tau):
    i = int(np.argmin(np.abs(TAUS - tau)))
    return {k: v[i] for k, v in cur.items()}


# --- load --------------------------------------------------------------------------
C, N = {}, {}
for m in MODELS:
    for s in SEEDS:
        p = os.path.join(V2, f"{m}_s{s}/eval_test/per_frame.csv")
        C[(m, s)], N[(m, s)] = curve(read_per_frame(p))
Y, NY = curve(read_per_frame(YOLO))

MEAN = {m: {k: np.nanmean([C[(m, s)][k] for s in SEEDS], 0) for k in ["V", "E", "H", "FA"]}
        for m in MODELS}

# argmax of the Youden-style gap (H frame recall - off-arm frame FA), on the seed mean
BEST = {}
for m in MODELS:
    j = MEAN[m]["H"] - MEAN[m]["FA"]
    i = int(np.nanargmax(j))
    per_seed = {}
    for s in SEEDS:
        js = C[(m, s)]["H"] - C[(m, s)]["FA"]
        k = int(np.nanargmax(js))
        per_seed[s] = (float(TAUS[k]), float(js[k]))
    o = at(MEAN[m], TAU_OP)
    BEST[m] = dict(tau=float(TAUS[i]), gap=float(j[i]),
                   gap_at_op=float(o["H"] - o["FA"]),
                   H_at_best=float(MEAN[m]["H"][i]), FA_at_best=float(MEAN[m]["FA"][i]),
                   H_at_op=float(o["H"]), FA_at_op=float(o["FA"]),
                   per_seed_argmax=per_seed)
jy = Y["H"] - Y["FA"]
iy = int(np.nanargmax(jy))
BEST["yolo_s42"] = dict(tau=float(TAUS[iy]), gap=float(jy[iy]),
                        H_at_best=float(Y["H"][iy]), FA_at_best=float(Y["FA"][iy]),
                        H_at_op=float(at(Y, TAU_YOLO)["H"]),
                        FA_at_op=float(at(Y, TAU_YOLO)["FA"]))


# ================================================================== fig 1: scatter
fig, ax = plt.subplots(figsize=(5.6, 4.4))
for m in MODELS:
    xs = [at(C[(m, s)], TAU_OP)["FA"] for s in SEEDS]
    ys = [at(C[(m, s)], TAU_OP)["H"] for s in SEEDS]
    ax.scatter(xs, ys, s=68, color=MODEL_C[m], edgecolor="white", linewidth=1.6,
               zorder=3, label=f"{m} (tau .5)")
    for s, x, y in zip(SEEDS, xs, ys):
        ax.annotate(f"s{s}", (x, y), textcoords="offset points", xytext=(7, -3),
                    fontsize=7.5, color=INK2)
yx, yy = at(Y, TAU_YOLO)["FA"], at(Y, TAU_YOLO)["H"]
ax.scatter([yx], [yy], s=110, marker="X", color=YOLO_C, edgecolor="white", linewidth=1.4,
           zorder=4, label="YOLO s42 (tau .25, detector baseline)")
ax.annotate("s42", (yx, yy), textcoords="offset points", xytext=(8, -3),
            fontsize=7.5, color=INK2)
ax.set_xlabel("off-arm frame false-alarm rate")
ax.set_ylabel("H-tier frame recall")
ax.set_title("H recall vs off-arm FA at the operating point\n"
             "3 models x 3 seeds, test split", loc="left", color=INK)
ax.set_xlim(left=-0.01)
ax.set_ylim(-0.03, 1.03)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.99))
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.savefig(os.path.join(OUT, "scatter_Hrecall_vs_FA.png"))
plt.close(fig)


# ================================================================== fig 2: per model
for m in MODELS:
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    for s in SEEDS:                                   # per-seed thin lines
        for k in ["V", "E", "H", "FA"]:
            ax.plot(TAUS, C[(m, s)][k], color=SERIES_C[k], lw=0.7, alpha=0.30, zorder=2)
    for k in ["V", "E", "H", "FA"]:                    # seed mean, thick
        ax.plot(TAUS, MEAN[m][k], color=SERIES_C[k], lw=2.0, zorder=3,
                ls="--" if k == "FA" else "-",
                label=f"{k} frame recall" if k != "FA" else "off-arm frame FA")
        ax.annotate(k, (TAUS[-1], MEAN[m][k][-1]), textcoords="offset points",
                    xytext=(5, -3), fontsize=8, color=SERIES_C[k], weight="bold")
    ax.axvline(TAU_OP, color=INK2, lw=1.0, ls=":", zorder=1)
    ax.annotate("tau_op .5", (TAU_OP, 1.10), fontsize=7.5, color=INK2, ha="center")
    bt = BEST[m]["tau"]
    if abs(bt - TAU_OP) > 1e-6:
        ax.axvline(bt, color=SERIES_C["H"], lw=1.0, ls=":", zorder=1)
        ax.annotate(f"argmax(H-FA) {bt:.2f}", (bt, 1.03), fontsize=7.5,
                    color=SERIES_C["H"], ha="center")
    ax.set_xlabel("tau")
    ax.set_ylabel("rate")
    ax.set_ylim(-0.03, 1.17)
    ax.set_xlim(0.0, 1.02)
    ax.set_title(f"{m}: tier frame recall and off-arm FA vs tau\n"
                 "thick = mean over seeds 42/43/44, thin = per seed",
                 loc="left", color=INK)
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.99))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(os.path.join(OUT, f"tau_curve_{m}.png"))
    plt.close(fig)


# ================================================================== fig 3: ROC-style
fig, ax = plt.subplots(figsize=(5.6, 4.4))
for m in MODELS:
    ax.plot(MEAN[m]["FA"], MEAN[m]["H"], color=MODEL_C[m], lw=2.0, zorder=3, label=m)
    i = int(np.argmin(np.abs(TAUS - TAU_OP)))
    ax.scatter([MEAN[m]["FA"][i]], [MEAN[m]["H"][i]], s=64, color=MODEL_C[m],
               edgecolor="white", linewidth=1.6, zorder=4)
    ax.annotate(f"{m} @ .5", (MEAN[m]["FA"][i], MEAN[m]["H"][i]),
                textcoords="offset points", xytext=(8, -9), fontsize=7.5, color=MODEL_C[m])
    ax.annotate("tau .05", (MEAN[m]["FA"][0], MEAN[m]["H"][0]),
                textcoords="offset points", xytext=(4, 4), fontsize=6.5, color=INK2)
i = int(np.argmin(np.abs(TAUS - TAU_YOLO)))
ax.scatter([Y["FA"][i]], [Y["H"][i]], s=110, marker="X", color=YOLO_C,
           edgecolor="white", linewidth=1.4, zorder=4, label="YOLO s42 @ .25")
ax.plot([0, 1], [0, 1], color=GRID, lw=1.0, zorder=1)
ax.set_xlabel("off-arm frame false-alarm rate")
ax.set_ylabel("H-tier frame recall")
ax.set_title("ROC-style trace, parametric in tau (0.05 -> 0.95)\n"
             "seed-mean curves; dot = tau_op 0.5", loc="left", color=INK)
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.03, 1.03)
ax.legend(loc="lower right")
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.savefig(os.path.join(OUT, "roc_Hrecall_vs_FA.png"))
plt.close(fig)


# ================================================================== numbers -> csv/json
with open(os.path.join(OUT, "tau_curves.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["model", "seed", "tau", "frame_recall_V", "frame_recall_E",
                "frame_recall_H", "frame_fa_off"])
    for m in MODELS:
        for s in SEEDS:
            for i, t in enumerate(TAUS):
                w.writerow([m, s, f"{t:.2f}"] + [f"{C[(m, s)][k][i]:.4f}"
                                                 for k in ["V", "E", "H", "FA"]])
        for i, t in enumerate(TAUS):
            w.writerow([m, "mean", f"{t:.2f}"] + [f"{MEAN[m][k][i]:.4f}"
                                                  for k in ["V", "E", "H", "FA"]])
    for i, t in enumerate(TAUS):
        w.writerow(["yolo", 42, f"{t:.2f}"] + [f"{Y[k][i]:.4f}" for k in ["V", "E", "H", "FA"]])

with open(os.path.join(OUT, "tau_best.json"), "w") as f:
    json.dump(dict(taus=[float(t) for t in TAUS], best=BEST,
                   n_frames={f"{m}_s{s}": N[(m, s)] for m in MODELS for s in SEEDS},
                   n_frames_yolo=NY), f, indent=1)

print(json.dumps(BEST, indent=1))
print("counts", N[("rgb", 42)], "yolo", NY)
for m in MODELS:
    o = at(MEAN[m], TAU_OP)
    print(m, "@0.5 mean V/E/H/FA",
          " ".join(f"{o[k]:.4f}" for k in ["V", "E", "H", "FA"]))
    for s in SEEDS:
        p = at(C[(m, s)], TAU_OP)
        print("  s%d" % s, " ".join(f"{p[k]:.4f}" for k in ["V", "E", "H", "FA"]))
print("yolo@0.25", " ".join(f"{at(Y, TAU_YOLO)[k]:.4f}" for k in ["V", "E", "H", "FA"]))
