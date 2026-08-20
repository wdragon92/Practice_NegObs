"""Qualitative panels: RGB frame + GT grid + predicted-probability grid (n_bands x n_sectors).

Picks --n detected-H, --n missed-H and --n off-frame false alarms from a per_frame.csv.
Grid is drawn FAR band on top .. NEAR band at the bottom, columns = sector names left-to-right;
row labels carry the band's metric range, so a V0 (3-row) and a V1 (4-row) panel are self-
describing. Everything comes from the gridspec (--grid), nothing is hard-coded.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gridspec  # noqa: E402
from eval_polar import read_per_frame  # noqa: E402


def _grid(ax, vals, title, tau, binary, g):
    """vals is a flat n_cells vector in cell_index order (band*n_sectors + sector)."""
    m = np.asarray(vals, float).reshape(g.n_bands, g.n_sectors)[::-1]   # far band on top
    ax.imshow(m, vmin=0, vmax=1, cmap="magma", aspect="auto")
    ax.set_title(title, fontsize=9)
    ax.set_xticks(range(g.n_sectors), list(g.sector_names), fontsize=8)
    ax.set_yticks(range(g.n_bands), [g.band_label(b) for b in range(g.n_bands)][::-1], fontsize=7)
    for r in range(g.n_bands):
        for c in range(g.n_sectors):
            v = m[r, c]
            txt = f"{int(v)}" if binary else f"{v:.2f}"
            ax.text(c, r, txt, ha="center", va="center", fontsize=8,
                    color="white" if v < 0.6 else "black",
                    fontweight="bold" if (v >= tau and not binary) or (binary and v > 0.5) else "normal")


def panel(rec_rgb, probs, gt, meta, out_png, tau, g):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2),
                             gridspec_kw=dict(width_ratios=[1.5, 1, 1]))
    try:
        axes[0].imshow(Image.open(rec_rgb).convert("RGB"))
    except Exception as e:
        axes[0].text(0.5, 0.5, f"image unreadable\n{e}", ha="center", va="center", fontsize=8)
    axes[0].set_axis_off()
    axes[0].set_title(os.path.basename(rec_rgb), fontsize=8)
    _grid(axes[1], gt, f"GT ({g.version})", tau, True, g)
    _grid(axes[2], probs, f"pred prob (tau={tau})", tau, False, g)
    fig.suptitle(meta, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_png, dpi=110)
    plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--per-frame", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--tau", type=float, default=0.5)
    p.add_argument("--tier", default="H")
    gridspec.add_grid_arg(p)
    a = p.parse_args(argv)
    g = gridspec.from_args(a)
    os.makedirs(a.out, exist_ok=True)

    d = read_per_frame(a.per_frame, g)
    with open(a.manifest) as f:
        rgb = {str(r["frame_id"]): r["rgb"] for r in json.load(f)["frames"]}
    P, G = d["probs"], d["gt"] > 0.5
    pred = P >= a.tau
    on = d["toggle"] == "on"
    sel_t = on & (d["tier"] == a.tier) & G.any(1)
    maxp_gt = np.where(G.any(1), np.where(G, P, -1).max(1), -1.0)

    hit = [i for i in np.where(sel_t & (pred & G).any(1))[0]]
    hit.sort(key=lambda i: -maxp_gt[i])
    miss = [i for i in np.where(sel_t & ~(pred & G).any(1))[0]]
    miss.sort(key=lambda i: maxp_gt[i])
    off = [i for i in np.where((d["toggle"] == "off") & pred.any(1))[0]]
    off.sort(key=lambda i: -P[i].max())

    made = 0
    for tag, idxs in (("hit" + a.tier, hit), ("miss" + a.tier, miss), ("fa_off", off)):
        if not idxs:
            print(f"[viz] no candidates for {tag}")
        for r, i in enumerate(idxs[: a.n], 1):
            fid = d["frame_id"][i]
            meta = (f"[{tag}] {fid} · scene {d['scene_id'][i]} · tier {d['tier'][i]} · "
                    f"toggle {d['toggle'][i]} · max p {P[i].max():.3f}")
            out = os.path.join(a.out, f"{tag}_{r:02d}_{fid.replace('/', '__')}.png")
            panel(rgb.get(fid, ""), P[i], d["gt"][i], meta, out, a.tau, g)
            made += 1
    print(f"[viz] wrote {made} panels ({g.n_bands}x{g.n_sectors} grid, {g.version}) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
