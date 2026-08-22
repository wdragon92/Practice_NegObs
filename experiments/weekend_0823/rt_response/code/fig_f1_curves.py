"""Figure — H (and E, V) frame recall vs off-arm frame false-alarm rate, full sweep.

The published table reads RGB's H recall at FA 0.359 and Depth's at FA 0.042 in the
same column.  This figure puts every operating point of every run on one axis so the
comparison is read at matched FA.

Palette: slots 1-3 of the dataviz reference palette (blue / orange / aqua), used
unchanged.  That triple is the documented all-pairs-validated subset in both modes
(worst-pair CVD dE 9.2 light, normal-vision 24.0), so no re-stepping is applied.
Series are also direct-labelled, so identity is never colour-alone.

Writes figs/fig_f1_recall_vs_fa.png and .pdf
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
curves = json.load(open(os.path.join(OUT, "figs", "f1_curve_data.json")))
matched = json.load(open(os.path.join(OUT, "f1_fa_matched.json")))

MODELS = ["rgb", "depth", "b2"]
LABEL = {"rgb": "RGB U-Net", "depth": "Depth U-Net", "b2": "SegFormer-B2"}
COLOR = {"rgb": "#2a78d6", "depth": "#eb6834", "b2": "#1baf7a"}
SEEDS = [42, 43, 44]
TIERS = [("H", "strict-H  (n = 96)"), ("E", "E  (n = 45)"), ("V", "V  (n = 180)")]
TARGETS = [0.05, 0.10, 0.20, 0.359]

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8b8a85"
SURFACE = "#ffffff"
GRID = "#e6e5e1"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.edgecolor": GRID, "axes.linewidth": 0.8,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

FA_GRID = np.linspace(0.0, 1.0, 501)


def mean_curve(model, tier):
    """Seed-mean recall on a common FA axis (each seed's curve is a step function of tau;
    both FA and recall are monotone in tau, so interpolation in FA is well defined)."""
    ys = []
    for s in SEEDS:
        c = curves[f"{model}_s{s}"]
        fa = np.asarray(c["FA"])
        rec = np.asarray(c[tier])
        o = np.argsort(fa)
        ys.append(np.interp(FA_GRID, fa[o], rec[o]))
    return np.mean(ys, axis=0), np.min(ys, axis=0), np.max(ys, axis=0)


fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.7), sharey=True)
for ax, (tier, title) in zip(axes, TIERS):
    ax.set_title(title, fontsize=9.5, color=INK, pad=8, loc="left")
    ax.grid(True, color=GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for m in MODELS:
        mu, lo, hi = mean_curve(m, tier)
        ax.fill_between(FA_GRID, lo, hi, color=COLOR[m], alpha=0.13, linewidth=0, zorder=2)
        ax.plot(FA_GRID, mu, color=COLOR[m], linewidth=2.0, zorder=4,
                solid_capstyle="round")
    if tier == "H":
        for t in TARGETS:
            ax.axvline(t, color=MUTED, linewidth=0.7, linestyle=(0, (2, 3)), zorder=1)
        for m in MODELS:
            xs = [matched["model_mean"][m]["exact"][str(t)]["FA"]["mean"] for t in TARGETS]
            ys = [matched["model_mean"][m]["exact"][str(t)]["H"]["mean"] for t in TARGETS]
            ax.plot(xs, ys, "o", color=COLOR[m], markersize=5.2, zorder=6,
                    markeredgecolor=SURFACE, markeredgewidth=1.4)
        ax.text(0.985, 0.035, "dashed guides = matched-FA targets\n0.05 · 0.10 · 0.20 · 0.359",
                transform=ax.transAxes, fontsize=7.2, color=MUTED, ha="right", va="bottom",
                linespacing=1.4)
    # the published tau = 0.5 points, hollow, on every panel
    for m in MODELS:
        p = matched["model_mean"][m]["tau_op_0.5"]
        ax.plot([p["FA"]["mean"]], [p[tier]["mean"]], marker="D", markersize=6.0,
                markerfacecolor=SURFACE, markeredgecolor=COLOR[m], markeredgewidth=1.6,
                zorder=7)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("off-arm frame false-alarm rate", fontsize=8.5, color=INK2)

axes[0].set_ylabel("frame recall", fontsize=8.5, color=INK2)

# direct labels on the H panel
ax = axes[0]
# direct labels sit beside each curve at the FA = 0.10 reporting point, where the
# three are maximally separated; a surface-coloured box keeps them off the guides
for m, yoff in (("depth", 0.045), ("rgb", -0.030), ("b2", -0.045)):
    mu, _lo, _hi = mean_curve(m, "H")
    y = mu[np.searchsorted(FA_GRID, 0.10)] + yoff
    ax.text(0.155, y, LABEL[m], color=COLOR[m], fontsize=8.2, fontweight="bold",
            ha="left", va="center", zorder=8,
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.2))

handles = [Line2D([], [], color=COLOR[m], linewidth=2.0, label=LABEL[m]) for m in MODELS]
handles += [
    Line2D([], [], color=MUTED, marker="o", linestyle="none", markersize=5.2,
           label="matched-FA point (3-seed mean)"),
    Line2D([], [], color=MUTED, marker="D", linestyle="none", markersize=6.0,
           markerfacecolor=SURFACE, markeredgewidth=1.6,
           label="published operating point, τ = 0.5"),
    Line2D([], [], color=MUTED, linewidth=6, alpha=0.25,
           label="seed min–max envelope (n = 3)"),
]
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=8,
           labelcolor=INK2, bbox_to_anchor=(0.5, -0.075), handlelength=1.8,
           columnspacing=1.8)

fig.suptitle("Recall against false alarms — the H-tier ordering is an operating-point artefact",
             fontsize=11, color=INK, x=0.008, ha="left", y=1.015)
fig.text(0.008, 0.945,
         "Frozen recipe-v2 runs, 816 test frames.  Diamonds are the numbers printed in the main "
         "table: RGB reads its H recall at FA 0.359, Depth at FA 0.042.",
         fontsize=8, color=INK2, ha="left")
fig.tight_layout(rect=(0, 0.02, 1, 0.90))
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, "figs", f"fig_f1_recall_vs_fa.{ext}"),
                dpi=200, bbox_inches="tight")
print("wrote figs/fig_f1_recall_vs_fa.png/.pdf")
