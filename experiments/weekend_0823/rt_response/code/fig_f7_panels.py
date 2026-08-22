"""Figure — six representative strict-H twin pairs: hazard-ON | hazard-OFF | |on - off|.

Six pairs are chosen without cherry-picking: for each of the two test H scenes, the
pair at the minimum, the median and the maximum of the supra-noise residual
(pixels differing by >= 32/255), ranked over that scene's pairs.

The difference panel uses a SEQUENTIAL one-hue ramp (the dataviz reference palette's
blue ramp, white -> #0d366b), so "no difference" recedes into the surface and
magnitude reads monotonically.  A dashed outline marks the GT-positive polar wedges
projected into the image; a solid outline marks the amodal hazard silhouette (the
hazard prism projected ignoring occlusion) — i.e. where the hazard WOULD be.

Writes panels/h_diff_<scene>_<rank>.png (6 files) + panels/h_diff_contact_sheet.png
"""
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                       # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from PIL import Image                                  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code/labeling"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wedge_util import wedge_mask, amodal_mask          # noqa: E402  (same code the audit used)

MANIFEST = os.path.join(REPO, "experiments/dayrun_0820/dataset_manifest_v2_full.json")
res = json.load(open(os.path.join(OUT, "f7_hpair_pixdiff.json")))
M = json.load(open(MANIFEST))
by_id = {f["frame_id"]: f for f in M["frames"]}

INK, INK2, MUTED, SURFACE, GRID = "#0b0b0b", "#52514e", "#8b8a85", "#ffffff", "#e6e5e1"
BLUE_RAMP = ["#ffffff", "#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95", "#0d366b"]
CMAP = LinearSegmentedColormap.from_list("negobs_blue", BLUE_RAMP)
VMAX = 96.0            # 32/255 is the content floor; 96 saturates the ramp
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURFACE,
                     "savefig.facecolor": SURFACE})

# ---------------------------------------------------------------- pick 6 pairs
picks = []
for sc in ("scene14", "scene15"):
    rows = sorted([r for r in res["per_pair"] if r["scene_id"] == sc],
                  key=lambda r: r["L32"]["n_diff_px"])
    picks += [(sc, "min", rows[0]), (sc, "median", rows[len(rows) // 2]), (sc, "max", rows[-1])]


def load_pair(rec):
    f = by_id[rec["frame_id"]]
    g = by_id[rec["frame_id"].replace("on/", "off/", 1)]
    a = np.asarray(Image.open(f["rgb"]).convert("RGB"), np.int16)
    b = np.asarray(Image.open(g["rgb"]).convert("RGB"), np.int16)
    return f, a, b, np.abs(a - b).max(axis=2)


def outline(ax, mask, color, ls, lw):
    if mask.any():
        ax.contour(mask.astype(float), levels=[0.5], colors=[color],
                   linewidths=lw, linestyles=[ls])


def one_panel(rec, tag, path):
    f, a, b, d = load_pair(rec)
    gt_cells = [c for c, v in enumerate(f["polar_gt"]) if v]
    wm, _ = wedge_mask(gt_cells, f["cam"])
    am = amodal_mask(f["frame_id"])
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 2.62))
    for ax in axes:
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color(GRID)
    axes[0].imshow(a.astype(np.uint8))
    axes[0].set_title("hazard ON", fontsize=9, color=INK, loc="left", pad=5)
    axes[1].imshow(b.astype(np.uint8))
    axes[1].set_title("hazard OFF (twin, pose-exact)", fontsize=9, color=INK, loc="left", pad=5)
    im = axes[2].imshow(d, cmap=CMAP, vmin=0, vmax=VMAX, interpolation="nearest")
    axes[2].set_title("| on − off |  (max channel)", fontsize=9, color=INK, loc="left", pad=5)
    for ax in axes:
        outline(ax, am, "#eb6834", "-", 1.0)
        outline(ax, wm, "#0b0b0b", "--", 0.9)
    cb = fig.colorbar(im, ax=axes[2], fraction=0.032, pad=0.012)
    cb.set_label("|Δ| / 255", fontsize=7.5, color=INK2)
    cb.ax.tick_params(labelsize=7, colors=INK2)
    cb.outline.set_edgecolor(GRID)
    L = rec["L32"]
    fig.suptitle(
        f"{rec['scene_id']} · {os.path.basename(rec['frame_id'])} · {rec['cond']} · "
        f"standoff {rec['cam_d']:.2f} m — {tag} residual for this scene",
        fontsize=10, color=INK, x=0.006, ha="left", y=1.10)
    fig.text(0.006, 0.985,
             f"pixels |Δ| ≥ 32/255: {L['n_diff_px']:,} ({100*L['frac_diff']:.2f} % of frame) · "
             f"{100*L['frac_in_amodal']:.0f} % of them inside the amodal hazard silhouette (solid) · "
             f"{100*L['frac_in_gt_wedge']:.0f} % inside the GT wedges (dashed) · "
             f"renderer noise floor at this level = 50 px",
             fontsize=7.6, color=INK2, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


paths = []
for sc, tag, rec in picks:
    p = os.path.join(OUT, "panels", f"h_diff_{sc}_{tag}.png")
    one_panel(rec, tag, p)
    paths.append((sc, tag, rec, p))
    print("wrote", os.path.relpath(p, REPO))

# ---------------------------------------------------------------- contact sheet
fig, axes = plt.subplots(6, 3, figsize=(11.2, 11.6))
for row, (sc, tag, rec, _p) in enumerate(paths):
    f, a, b, d = load_pair(rec)
    gt_cells = [c for c, v in enumerate(f["polar_gt"]) if v]
    wm, _ = wedge_mask(gt_cells, f["cam"])
    am = amodal_mask(f["frame_id"])
    for col, img in enumerate((a.astype(np.uint8), b.astype(np.uint8), None)):
        ax = axes[row, col]
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color(GRID)
        if img is not None:
            ax.imshow(img)
        else:
            ax.imshow(d, cmap=CMAP, vmin=0, vmax=VMAX, interpolation="nearest")
        outline(ax, am, "#eb6834", "-", 0.8)
        outline(ax, wm, "#0b0b0b", "--", 0.7)
        if row == 0:
            ax.set_title(["hazard ON", "hazard OFF (twin)", "| on − off |"][col],
                         fontsize=9, color=INK, loc="left", pad=5)
    L = rec["L32"]
    axes[row, 0].set_ylabel(f"{sc}\n{tag}\n{L['n_diff_px']:,} px", fontsize=7.6,
                            color=INK2, rotation=0, ha="right", va="center", labelpad=26)
fig.suptitle("strict-H twin pairs: what is still visible when the hazard contributes zero pixels",
             fontsize=11.5, color=INK, x=0.006, ha="left", y=0.995)
fig.text(0.006, 0.977,
         "Six pairs = min / median / max supra-noise residual (|Δ| ≥ 32/255) within each of the two "
         "test H scenes.  Solid outline = amodal hazard silhouette; dashed = GT-positive polar wedges.",
         fontsize=8, color=INK2, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.968))
cs = os.path.join(OUT, "panels", "h_diff_contact_sheet.png")
fig.savefig(cs, dpi=130, bbox_inches="tight")
print("wrote", os.path.relpath(cs, REPO))
