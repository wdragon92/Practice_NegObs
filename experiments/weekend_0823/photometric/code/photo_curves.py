#!/usr/bin/env python3
"""GPU-4 / WEEKEND_BRIEF_0823 §6.6 — score the photometric sweep and draw the curve figure.

CPU only. Reads the per_frame.csv written by `photo_stress.py` for every (seed, variant) and
scores each with `eval_polar.bundle` — the SAME metric code every row of the main table uses —
at the approved operating threshold tau_op = 0.5 (approval #1).

*** All numbers here are VAL numbers (scene08, scene20, sceneD3). test is not touched. ***

Val composition (288 frames): 144 hazard-off, 144 hazard-on, of which the hazard frames carrying
>=1 GT-positive cell are the recall denominators. E and H have only a handful of frames each —
the report must label those curves as indicative, not measured.

Outputs (this directory's parent):
  PHOTO_CURVES.csv        long-form table: seed x variant x metric  (the table view the
                          accessibility rule requires next to the figure)
  PHOTO_NUMBERS.json      the same, plus 3-seed mean/range and the deltas vs identity
  photometric_stress.png  the figure: 2 rows x 3 small multiples (brightness / gamma / exposure).
                          Row A = detection rates at the fixed tau_op = 0.5 (hazard recall,
                          V recall, false-alarm rate). Row B = cell F1 at that fixed threshold
                          against cell F1 at a per-variant val-re-fitted threshold, which
                          separates "the scores shifted" from "the representation was lost".
                          Line = 3-seed mean, band = seed min-max.

Run: PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" python photo_curves.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(HERE)
RUNS = os.path.join(TRACK, "runs")
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
import gridspec  # noqa: E402
from eval_polar import bundle, counts, fit_tau_star, read_per_frame  # noqa: E402

SEEDS = (42, 43, 44)
TAU = 0.5
METRICS = ["frame_det_rate", "frame_recall_V", "frame_recall_E", "frame_recall_H",
           "frame_fa_off", "cell_fpr_off", "cell_f1", "cell_recall", "cell_precision"]

# family -> [(variant dir name, x value, x tick label)] ; x=neutral is the identity anchor
FAMILIES = {
    "brightness": ([("bright_0.6", 0.6), ("bright_0.8", 0.8), ("identity", 1.0),
                    ("bright_1.2", 1.2), ("bright_1.4", 1.4)],
                   "brightness gain  b        (clip(b·I, 0, 1))", 1.0),
    "gamma": ([("gamma_0.7", 0.7), ("identity", 1.0), ("gamma_1.4", 1.4)],
              "gamma  g        (I^g)", 1.0),
    "exposure": ([("exp_-1", -1.0), ("exp_-0.5", -0.5), ("identity", 0.0),
                  ("exp_+0.5", 0.5), ("exp_+1", 1.0)],
                 "exposure  EV     (linear-light, ±stops)", 0.0),
}

# dataviz reference palette, categorical slots 1-3 (blue / orange / aqua). This exact
# three-slot subset is the documented all-pairs-validating set (references/palette.md:
# worst pair CVD dE 9.2 light, normal-vision 24.0 light), which is what small multiples need.
C_1, C_2, C_3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, INK3 = "#0b0b0b", "#52514e", "#8a8985"
SURFACE, GRID_C = "#fcfcfb", "#e6e5e1"
# Row 1: the requested curves — frame recall (val positives) and FA (val off) vs perturbation.
ROW1 = [("frame_det_rate", "hazard recall (any tier)", C_1, "o"),
        ("frame_recall_V", "V-tier frame recall", C_2, "s"),
        ("frame_fa_off", "false alarm (off frames)", C_3, "^")]
# Row 2: the mechanism — is a sag a lost representation, or only a shifted firing rate?
ROW2 = [("f1_op", "cell F1 @ fixed tau_op = 0.5", C_1, "o"),
        ("f1_star", "cell F1 @ per-variant best tau (val re-fit, diagnostic)", C_2, "s")]


def _stagger(labels, gap):
    """Greedy vertical de-collision for right-edge direct labels: [(y, text, colour), ...]."""
    out = sorted(labels, key=lambda t: t[0])
    for i in range(1, len(out)):
        if out[i][0] - out[i - 1][0] < gap:
            out[i] = (out[i - 1][0] + gap,) + out[i][1:]
    return out


def score_all(grid):
    """Point metrics at tau_op = 0.5, plus the DIAGNOSTIC re-fit of tau on the same val set.

    The re-fit answers one question and only one: is a degradation a loss of the representation,
    or just a gain/offset shift that moved the scores past a fixed threshold? If cell F1 at the
    per-variant best tau is flat while cell F1 at 0.5 sags, the perturbation moved the scores,
    not the ranking, and a pilot-time exposure normalisation (or a per-shoot tau) recovers it.
    This tau is NEVER used for the main table — approval #1 fixes tau_op = 0.5 — and it is fitted
    on val, which is the split that is allowed to be fitted on.
    """
    out, star, comp = {}, {}, None
    for s in SEEDS:
        for v in sorted({n for f in FAMILIES.values() for n, _ in f[0]}):
            d = read_per_frame(os.path.join(RUNS, f"s{s}", v, "per_frame.csv"), grid)
            if comp is None:
                comp = counts(d)
            out[(s, v)] = bundle(d, TAU, grid=grid)
            t, f1 = fit_tau_star(d, grid)
            star[(s, v)] = dict(tau_star=t, cell_f1_at_star=f1)
    return out, star, comp


def agg(scores, v, k):
    a = np.array([scores[(s, v)][k] for s in SEEDS], float)
    a = a[np.isfinite(a)]
    if not a.size:
        return None, None
    return float(a.mean()), float((a.max() - a.min()) / 2)


def _panel(ax, xs, series, getter, neutral, ylim, label_gap, direct):
    ax.set_facecolor(SURFACE)
    ax.axvline(neutral, color=INK3, lw=1.0, ls=(0, (3, 3)), zorder=1)
    tags = []
    for key, _lbl, col, mk in series:
        mean = [getter(v, key)[0] for v in xs[1]]
        lo = [getter(v, key)[1] for v in xs[1]]
        hi = [getter(v, key)[2] for v in xs[1]]
        ax.fill_between(xs[0], lo, hi, color=col, alpha=0.11, lw=0, zorder=2)
        ax.plot(xs[0], mean, color=col, lw=2.0, marker=mk, ms=5.5, mec=SURFACE, mew=1.5,
                zorder=3, label=_lbl)
        tags.append((mean[-1], f"{mean[-1]:.2f}", col))
    if direct:
        for y, txt, col in _stagger(tags, label_gap):
            ax.annotate(txt, (xs[0][-1], y), textcoords="offset points", xytext=(10, -4),
                        color=col, fontsize=9.5, fontweight="bold", zorder=5,
                        annotation_clip=False)
    ax.set_xticks(xs[0])
    ax.set_xticklabels([f"{x:g}" for x in xs[0]], fontsize=9.5, color=INK2)
    span = max(xs[0]) - min(xs[0])
    ax.set_xlim(min(xs[0]) - span * 0.10, max(xs[0]) + span * (0.22 if direct else 0.10))
    ax.set_ylim(*ylim)
    ax.grid(axis="y", color=GRID_C, lw=0.9, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#d9d8d3")
    ax.tick_params(length=0, colors=INK2, labelsize=9.5)


def figure(scores, star, comp, path):
    fig, axes = plt.subplots(2, 3, figsize=(13.4, 8.3),
                             gridspec_kw=dict(width_ratios=[5, 3, 5], wspace=0.13, hspace=0.34))
    fig.patch.set_facecolor(SURFACE)

    def g1(v, k):
        a = [scores[(s, v)][k] for s in SEEDS]
        return float(np.mean(a)), min(a), max(a)

    def g2(v, k):
        a = [(scores[(s, v)]["cell_f1"] if k == "f1_op" else star[(s, v)]["cell_f1_at_star"])
             for s in SEEDS]
        return float(np.mean(a)), min(a), max(a)

    for j, (fam, (pts, xlabel, neutral)) in enumerate(FAMILIES.items()):
        xs = ([x for _, x in pts], [v for v, _ in pts])
        _panel(axes[0][j], xs, ROW1, g1, neutral, (0.0, 1.0), 0.075, j == 2)
        _panel(axes[1][j], xs, ROW2, g2, neutral, (0.30, 0.56), 0.020, j == 2)
        axes[1][j].set_xlabel(xlabel, fontsize=10, color=INK2, labelpad=7)
        if j:
            for r in (0, 1):
                axes[r][j].set_yticklabels([])
    for r, ticks in ((0, np.arange(0, 1.01, 0.2)), (1, np.arange(0.30, 0.561, 0.05))):
        for j in range(3):
            axes[r][j].set_yticks(ticks)
        axes[r][0].set_yticklabels([f"{t:.2f}" for t in ticks], fontsize=9.5, color=INK2)
    axes[0][0].set_ylabel("rate", fontsize=10, color=INK2)
    axes[1][0].set_ylabel("cell F1", fontsize=10, color=INK2)

    fig.text(0.055, 0.972, "Photometric stress of the frozen RGB U-Net — zero-shot, VAL only",
             ha="left", va="top", fontsize=15, color=INK, fontweight="bold")
    fig.text(0.055, 0.938,
             f"3 seeds (42/43/44), no retraining and no re-selection · line = seed mean, band = "
             f"seed min–max · dashed vertical = the unperturbed image\n"
             f"val split (scene08 / scene20 / sceneD3): {comp['n_hazard_frames']} hazard frames "
             f"(V {comp['n_V']} / E {comp['n_E']} / H {comp['n_H']}) and {comp['n_off']} "
             f"hazard-off frames — the E and H strata are far too small to read as curves",
             ha="left", va="top", fontsize=9.6, color=INK2, linespacing=1.55)
    for r, y, ttl in ((0, 0.870, "A · detection rates at the operating threshold  tau_op = 0.5"),
                      (1, 0.443, "B · shift or loss?  cell F1 at the fixed threshold vs at a "
                                 "re-fitted one — a gap that closes means the scores moved, "
                                 "not the representation")):
        fig.text(0.055, y, ttl, ha="left", va="top", fontsize=10.8, color=INK, fontweight="bold")
        h, l = axes[r][0].get_legend_handles_labels()
        leg = fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.055, y - 0.022), ncol=3,
                         frameon=False, fontsize=9.8, handlelength=1.8, columnspacing=2.0)
        for t in leg.get_texts():
            t.set_color(INK2)
        fig.add_artist(leg)
    fig.subplots_adjust(left=0.055, right=0.952, top=0.795, bottom=0.075)
    fig.savefig(path, dpi=170, facecolor=SURFACE)
    plt.close(fig)


def main():
    grid = gridspec.load("gridspec_v1.json")
    scores, star, comp = score_all(grid)

    with open(os.path.join(TRACK, "PHOTO_CURVES.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "variant", "param", "seed"] + METRICS
                   + ["tau_star_val_diag", "cell_f1_at_tau_star"])
        for fam, (pts, _, _) in FAMILIES.items():
            for v, x in pts:
                for s in SEEDS:
                    w.writerow([fam, v, x, s] + [f"{scores[(s, v)][k]:.6f}" for k in METRICS]
                               + [f"{star[(s, v)]['tau_star']:.2f}",
                                  f"{star[(s, v)]['cell_f1_at_star']:.6f}"])

    out = dict(subset="val", split=os.path.join(ROOT, "experiments/dayrun_0820/split_v2_full.json"),
               val_scenes=["scene08", "scene20", "sceneD3"], tau_op=TAU, seeds=list(SEEDS),
               counts=comp, per_seed={f"s{s}|{v}": scores[(s, v)] for (s, v) in scores},
               agg={}, delta_vs_identity={})
    for fam, (pts, _, _) in FAMILIES.items():
        for v, x in pts:
            out["agg"][v] = {k: dict(zip(("mean", "half_range"), agg(scores, v, k)))
                             for k in METRICS}
            out["agg"][v]["_param"] = x
            out["agg"][v]["_family"] = fam
            ts = np.array([star[(s, v)]["tau_star"] for s in SEEDS], float)
            f1s = np.array([star[(s, v)]["cell_f1_at_star"] for s in SEEDS], float)
            out["agg"][v]["tau_star_val_diag"] = dict(mean=float(ts.mean()),
                                                      half_range=float((ts.max() - ts.min()) / 2),
                                                      per_seed=[float(t) for t in ts])
            out["agg"][v]["cell_f1_at_tau_star"] = dict(
                mean=float(f1s.mean()), half_range=float((f1s.max() - f1s.min()) / 2))
    base = out["agg"]["identity"]
    for v, m in out["agg"].items():
        if v == "identity":
            continue
        out["delta_vs_identity"][v] = {
            k: dict(mean=m[k]["mean"] - base[k]["mean"],
                    per_seed=[scores[(s, v)][k] - scores[(s, "identity")][k] for s in SEEDS])
            for k in METRICS}
    with open(os.path.join(TRACK, "PHOTO_NUMBERS.json"), "w") as f:
        json.dump(out, f, indent=2)

    figure(scores, star, comp, os.path.join(TRACK, "photometric_stress.png"))

    print(f"val counts: {comp}")
    cols = ("frame_det_rate", "frame_recall_V", "frame_recall_E", "frame_recall_H",
            "frame_fa_off", "cell_f1")
    print(f"{'variant':12s}" + "".join(f"{k:>18s}" for k in cols) + f"{'tau*':>10s}{'F1@tau*':>10s}")
    for fam, (pts, _, _) in FAMILIES.items():
        for v, x in pts:
            row = f"{v:12s}"
            for k in cols:
                m, r = agg(scores, v, k)
                row += f"{m:>11.3f}±{r:<6.3f}"
            a = out["agg"][v]
            row += f"{a['tau_star_val_diag']['mean']:>10.2f}{a['cell_f1_at_tau_star']['mean']:>10.3f}"
            print(row)
        print()
    print("worst brightness +-40% delta (det_rate / V recall):")
    for v in ("bright_0.6", "bright_1.4"):
        print(f"  {v}: det {out['delta_vs_identity'][v]['frame_det_rate']['mean']:+.4f} "
              f"V {out['delta_vs_identity'][v]['frame_recall_V']['mean']:+.4f} "
              f"FA {out['delta_vs_identity'][v]['frame_fa_off']['mean']:+.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
