#!/usr/bin/env python3
"""DAYRUN 0820 Phase 3 -- diagnostics 1/2/3 on the mainrun_0819 V0 (15-cell) artefacts.

Read-only w.r.t. everything outside experiments/dayrun_0820/narrative/diag_v1/.
CPU only, no scipy (Spearman implemented here).
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
MR = os.path.join(REPO, "experiments/mainrun_0819")
OUT = os.path.join(REPO, "experiments/dayrun_0820/narrative/diag_v1")
sys.path.insert(0, os.path.join(MR, "code"))
import bootstrap as BS  # noqa: E402

TAU = 0.5
SECT = ["A", "B", "C", "D", "E"]
CELLS = [f"{s}{b}" for b in (1, 2, 3) for s in SECT]        # index = band*5 + sector
BANDS = {1: (0.0, 2.0), 2: (2.0, 5.0), 3: (5.0, 12.0)}
os.makedirs(OUT, exist_ok=True)
REPORT: dict = {}


# --------------------------------------------------------------------------- #
# loaders
# --------------------------------------------------------------------------- #
def read_per_frame(path):
    rows = {}
    with open(path) as fh:
        for r in csv.DictReader(fh):
            rows[r["frame_id"]] = dict(
                scene_id=r["scene_id"], tier=r["tier"], toggle=r["toggle_state"],
                p=np.array([float(r[f"p_{c}"]) for c in CELLS]),
                g=np.array([float(r[f"g_{c}"]) for c in CELLS]))
    return rows


MANIFEST = json.load(open(os.path.join(MR, "dataset_manifest_v1.json")))
SPLIT = json.load(open(os.path.join(MR, "split_v1.json")))
LABELS = json.load(open(os.path.join(MR, "annotations/labels_v0.json")))
PF = {a: read_per_frame(os.path.join(MR, f"runs/{a}_s42/eval_test/per_frame.csv"))
      for a in ("rgb", "depth")}
FRAMES = {f["frame_id"]: f for f in MANIFEST["frames"]}


# --------------------------------------------------------------------------- #
# own Spearman (rank correlation with average ranks for ties) + permutation p
# --------------------------------------------------------------------------- #
def rankdata(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), float)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0        # average rank, 1-based
        i = j + 1
    return ranks


def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a - a.mean(), b - b.mean()
    den = math.sqrt(float((a * a).sum()) * float((b * b).sum()))
    return float((a * b).sum() / den) if den > 0 else float("nan")


def spearman(a, b, n_perm=200000, seed=42):
    ra, rb = rankdata(a), rankdata(b)
    rho = pearson(ra, rb)
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_perm):
        if abs(pearson(rng.permutation(ra), rb)) >= abs(rho) - 1e-12:
            hits += 1
    return rho, (hits + 1) / (n_perm + 1)


# --------------------------------------------------------------------------- #
# DIAG (1)
# --------------------------------------------------------------------------- #
def diag1():
    train = set(SPLIT["train"])
    prior_n = np.zeros(15)
    n_tr = 0
    for f in MANIFEST["frames"]:
        if f["scene_id"] in train and f["toggle_state"] == "on":
            prior_n += np.asarray(f["polar_gt"], float)
            n_tr += 1
    prior = prior_n / n_tr

    fa, n_off = {}, None
    for arm in ("rgb", "depth"):
        rows = [r for r in PF[arm].values() if r["toggle"] == "off"]
        n_off = len(rows)
        fa[arm] = np.mean([(r["p"] >= TAU).astype(float) for r in rows], axis=0)

    # robustness: drop sceneC2 (it supplies most of the off-arm firing) and redo
    fa_noC2, per_scene = {}, {}
    for arm in ("rgb", "depth"):
        rows = [r for r in PF[arm].values() if r["toggle"] == "off"]
        keep = [r for r in rows if r["scene_id"] != "sceneC2"]
        fa_noC2[arm] = np.mean([(r["p"] >= TAU).astype(float) for r in keep], axis=0)
        per_scene[arm] = {}
        for sc in sorted({r["scene_id"] for r in rows}):
            sub = [r for r in rows if r["scene_id"] == sc]
            fired = np.array([(r["p"] >= TAU) for r in sub])
            per_scene[arm][sc] = dict(n_frames=len(sub),
                                      frame_fa=float(fired.any(axis=1).mean()),
                                      n_cell_fires=int(fired.sum()))
        tot = sum(v["n_cell_fires"] for v in per_scene[arm].values())
        for v in per_scene[arm].values():
            v["share_of_cell_fires"] = (v["n_cell_fires"] / tot) if tot else 0.0

    corr = {}
    for arm in ("rgb", "depth"):
        rho, p = spearman(prior, fa[arm])
        rho2, p2 = spearman(prior, fa_noC2[arm])
        corr[arm] = dict(rho=rho, p_perm=p, pearson=pearson(prior, fa[arm]),
                         rho_no_sceneC2=rho2, p_perm_no_sceneC2=p2)

    REPORT["diag1"] = dict(
        n_train_on=n_tr, n_test_off=n_off,
        prior=prior.tolist(), fa_rgb=fa["rgb"].tolist(), fa_depth=fa["depth"].tolist(),
        fa_rgb_no_sceneC2=fa_noC2["rgb"].tolist(), fa_depth_no_sceneC2=fa_noC2["depth"].tolist(),
        band_prior={b: float(prior[(b - 1) * 5:b * 5].mean()) for b in (1, 2, 3)},
        band_fa={a: {b: float(fa[a][(b - 1) * 5:b * 5].mean()) for b in (1, 2, 3)}
                 for a in ("rgb", "depth")},
        band_fa_no_sceneC2={a: {b: float(fa_noC2[a][(b - 1) * 5:b * 5].mean()) for b in (1, 2, 3)}
                            for a in ("rgb", "depth")},
        per_scene_off=per_scene, corr=corr)
    plot_diag1(prior, fa, corr)
    return prior, fa, corr


# --------------------------------------------------------------------------- #
# DIAG (2)
# --------------------------------------------------------------------------- #
def diag2():
    out = {}
    for arm in ("rgb", "depth"):
        pairs = []
        with open(os.path.join(MR, f"runs/{arm}_s42/twin/twin_pairs.csv")) as fh:
            for r in csv.DictReader(fh):
                if r["kept"] == "True":
                    pairs.append((r["scene_id"], r["cut"], r["tier"],
                                  float(r["delta_score"]) if r["delta_score"] not in ("", "nan") else np.nan))
        rows = []
        for sc, cut, tier, ds_ref in pairs:
            on, off = PF[arm].get(f"on/{sc}/{cut}"), PF[arm].get(f"off/{sc}/{cut}")
            if on is None or off is None:
                continue
            pos = on["g"] > 0.5
            rec = dict(scene=sc, cut=cut, tier=tier, ds_ref=ds_ref, n_gt=int(pos.sum()))
            rec["all"] = (float(on["p"][pos].max() - off["p"][pos].max())
                          if pos.any() else np.nan)
            rec["on_all"] = float(on["p"][pos].max()) if pos.any() else np.nan
            rec["off_all"] = float(off["p"][pos].max()) if pos.any() else np.nan
            rec["argmax_band"] = (int(np.argmax(np.where(pos, on["p"], -1)) // 5 + 1)
                                  if pos.any() else 0)
            for b in (1, 2, 3):
                m = pos.copy()
                m[:(b - 1) * 5] = False
                m[b * 5:] = False
                rec[f"b{b}"] = (float(on["p"][m].max() - off["p"][m].max())
                                if m.any() else np.nan)
                rec[f"on_b{b}"] = float(on["p"][m].max()) if m.any() else np.nan
                rec[f"off_b{b}"] = float(off["p"][m].max()) if m.any() else np.nan
                rec[f"n_b{b}"] = int(m.sum())
            rows.append(rec)
        # sanity: recomputed 'all' must reproduce twin_pairs.csv delta_score
        d = np.array([r["all"] - r["ds_ref"] for r in rows if np.isfinite(r["ds_ref"])])
        sanity = float(np.abs(d).max()) if d.size else float("nan")

        res = {}
        for key, lbl in [("all", "all bands")] + [(f"b{b}", f"band{b}") for b in (1, 2, 3)]:
            v = np.array([r[key] for r in rows], float)
            ok = np.isfinite(v)
            vv = v[ok]
            if vv.size == 0:
                res[lbl] = dict(n=0)
                continue
            ci = BS.bootstrap_ci(lambda idx, vv=vv: {"mean": float(vv[idx].mean())},
                                 len(vv), n_boot=10000, seed=42)["mean"]
            on_v = np.array([r[f"on_{key}"] for r in rows], float)[ok]
            off_v = np.array([r[f"off_{key}"] for r in rows], float)[ok]
            res[lbl] = dict(n=int(vv.size), n_pairs_kept=len(rows),
                            mean=ci["point"], lo=ci["lo"], hi=ci["hi"],
                            excludes_zero=bool(ci["lo"] > 0 or ci["hi"] < 0),
                            median=float(np.median(vv)),
                            frac_pos=float((vv > 0).mean()),
                            mean_on=float(on_v.mean()), mean_off=float(off_v.mean()),
                            n_gt_cells=int(sum(r[f"n_{key}"] for r in rows) if key != "all"
                                           else sum(r["n_gt"] for r in rows)))
        amb = [r["argmax_band"] for r in rows if r["argmax_band"]]
        out[arm] = dict(bands=res, sanity_max_abs_dev=sanity,
                        argmax_band_share={b: float(np.mean(np.array(amb) == b)) for b in (1, 2, 3)})
    REPORT["diag2"] = out
    plot_diag2(out)
    return out


# --------------------------------------------------------------------------- #
# DIAG (3) -- sceneC2
# --------------------------------------------------------------------------- #
def load_hm(arm):
    d = os.path.join(REPO, f"dataset/v2_corpus/260819_main_{arm}/val/sceneC2")
    z = np.load(os.path.join(d, "heightmap.npy"))
    m = json.load(open(os.path.join(d, "heightmap_meta.json")))
    return z, m


def polar_cells(XX, YY, eye, yaw):
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    dx, dy = XX - eye[0], YY - eye[1]
    xc, yc = dx * cy + dy * sy, -dx * sy + dy * cy
    az = np.degrees(np.arctan2(yc, xc))
    rng = np.hypot(xc, yc)
    asc = np.asarray([-31.1, -18.66, -6.22, 6.22, 18.66, 31.1])
    k = np.searchsorted(asc, az, side="right") - 1
    b = np.searchsorted(np.asarray([0.0, 2.0, 5.0, 12.0]), rng, side="right") - 1
    ok = (k >= 0) & (k < 5) & (b >= 0) & (b < 3)
    return np.where(ok, b * 5 + (4 - k), -1)


def local_drop(z, step, win_m=1.0):
    """z(p) - min z inside a square window of half-width win_m (the labeler's step-gate scale)."""
    r = int(round(win_m / step))
    zz = np.where(np.isfinite(z), z, np.inf)
    mn = zz.copy()
    for sh in range(1, r + 1):                     # separable min-filter, 4 shifts per radius
        mn[:, sh:] = np.minimum(mn[:, sh:], zz[:, :-sh])
        mn[:, :-sh] = np.minimum(mn[:, :-sh], zz[:, sh:])
    zz2 = mn.copy()
    for sh in range(1, r + 1):
        mn[sh:, :] = np.minimum(mn[sh:, :], zz2[:-sh, :])
        mn[:-sh, :] = np.minimum(mn[:-sh, :], zz2[sh:, :])
    return np.where(np.isfinite(z), z - mn, np.nan)


def diag3():
    var = {a: json.load(open(os.path.join(
        REPO, f"dataset/v2_corpus/260819_main_{a}/val/sceneC2/variation.json"))) for a in ("on", "off")}
    cuts = {a: {c["file"]: c for c in var[a]["cuts"]} for a in ("on", "off")}

    off_rows = {k: v for k, v in PF["rgb"].items() if v["scene_id"] == "sceneC2"
                and v["toggle"] == "off"}
    files = sorted(k.split("/")[-1] for k in off_rows)
    P = np.array([off_rows[f"off/sceneC2/{f}"]["p"] for f in files])
    fired = P >= TAU

    cell_tab = [dict(cell=CELLS[i], n_fire=int(fired[:, i].sum()),
                     mean_p=float(P[:, i].mean()), max_p=float(P[:, i].max()),
                     mean_p_fired=(float(P[fired[:, i], i].mean()) if fired[:, i].any() else float("nan")))
                for i in range(15)]

    # (c) twin pose mismatch cause
    keys = ("d", "h_rel", "yaw", "pitch", "ground_z", "roll", "hfov")
    dev = {k: [] for k in keys}
    gz = []
    for f in files:
        a, b = FRAMES[f"on/sceneC2/{f}"]["cam"], FRAMES[f"off/sceneC2/{f}"]["cam"]
        for k in keys:
            dev[k].append(abs(float(a[k]) - float(b[k])))
        gz.append((float(a["ground_z"]), float(b["ground_z"])))
    mism = {k: dict(max_abs=float(np.max(dev[k])), n_gt_tol=int((np.array(dev[k]) > 1e-6).sum()))
            for k in keys}

    # (b) height-map cross-check over the fired wedges
    z_off, m_off = load_hm("off")
    z_on, m_on = load_hm("on")
    x = m_off["x0"] + np.arange(m_off["nx"]) * m_off["step"]
    y = m_off["y0"] + np.arange(m_off["ny"]) * m_off["step"]
    XX, YY = np.meshgrid(x, y)
    st = m_off["step"]
    drop_off, drop_on = local_drop(z_off, st), local_drop(z_on, st)
    GROUND_MAX = 0.30            # exclude vegetation / props: keep ground-like samples only

    per_frame, union_mask = [], np.zeros_like(z_off, bool)
    for f in files:
        eye = np.asarray(cuts["off"][f]["cam"]["eye"], float)
        yaw = float(cuts["off"][f]["cam"]["yaw"])
        cell = polar_cells(XX, YY, eye, yaw)
        fi = [i for i in range(15) if fired[files.index(f), i]]
        msk = np.isin(cell, fi) & np.isfinite(z_off)
        union_mask |= msk
        gl = msk & (z_off <= GROUND_MAX)
        per_frame.append(dict(
            cut=f, cond=cuts["off"][f]["cond"], n_fired=len(fi),
            fired_cells=[CELLS[i] for i in fi],
            max_p=float(P[files.index(f)].max()),
            n_grid=int(msk.sum()),
            off_z_min=float(np.nanmin(z_off[msk])) if msk.any() else np.nan,
            off_z_max=float(np.nanmax(z_off[msk])) if msk.any() else np.nan,
            off_max_drop_ground=float(np.nanmax(drop_off[gl])) if gl.any() else np.nan,
            off_max_drop_all=float(np.nanmax(drop_off[msk])) if msk.any() else np.nan,
            on_max_drop_all=float(np.nanmax(drop_on[msk])) if msk.any() else np.nan,
            on_off_z_diff_max=float(np.nanmax(z_off[msk] - z_on[msk])) if msk.any() else np.nan))

    gl_u = union_mask & (z_off <= GROUND_MAX)
    above = union_mask & (z_off > GROUND_MAX)                # positive obstacles, not drops
    eye_dz = [float(np.asarray(cuts["on"][f]["cam"]["eye"])[2]
                    - np.asarray(cuts["off"][f]["cam"]["eye"])[2]) for f in files]
    summary = dict(
        n_off_frames=len(files), conds=sorted({c["cond"] for c in var["off"]["cuts"]}),
        union_grid_cells=int(union_mask.sum()),
        union_off_max_drop_ground=float(np.nanmax(drop_off[gl_u])),
        union_off_max_drop_all=float(np.nanmax(drop_off[union_mask])),
        union_off_z_span=[float(np.nanmin(z_off[union_mask])), float(np.nanmax(z_off[union_mask]))],
        union_off_ground_z_span=[float(np.nanmin(z_off[gl_u])), float(np.nanmax(z_off[gl_u]))],
        union_on_max_drop_all=float(np.nanmax(drop_on[union_mask])),
        union_on_off_diff_max=float(np.nanmax(z_off[union_mask] - z_on[union_mask])),
        hm_off_z_min=float(np.nanmin(z_off)), hm_off_z_max=float(np.nanmax(z_off)),
        hm_on_z_min=float(np.nanmin(z_on)), hm_on_z_max=float(np.nanmax(z_on)),
        frac_off_frames_firing=float((fired.any(axis=1)).mean()),
        mean_cells_fired=float(fired.sum(axis=1).mean()),
        frac_grid_above_ground_max=float(above.sum() / union_mask.sum()),
        above_z_max=float(np.nanmax(z_off[above])) if above.any() else float("nan"),
        eye_z_delta_on_minus_off=[min(eye_dz), max(eye_dz)],
        ground_max_used=GROUND_MAX)

    REPORT["diag3"] = dict(cells=cell_tab, per_frame=per_frame, summary=summary,
                           twin_mismatch=mism,
                           ground_z_on_off=[dict(cut=f, on=a, off=b) for f, (a, b) in zip(files, gz)],
                           arm_config=dict(on=m_on["arm_config"], off=m_off["arm_config"]))
    plot_diag3(P, fired, cell_tab, files)

    # centre-line ground profile of the FA panel frame, both arms
    panel = "L2__s20260819__0005.png"
    eye = np.asarray(cuts["off"][panel]["cam"]["eye"], float)
    yaw = float(cuts["off"][panel]["cam"]["yaw"])
    rr = np.arange(0.0, 12.0, 0.05)
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    px, py = eye[0] + rr * cy, eye[1] + rr * sy
    ix = np.clip(np.round((px - m_off["x0"]) / st).astype(int), 0, m_off["nx"] - 1)
    iy = np.clip(np.round((py - m_off["y0"]) / st).astype(int), 0, m_off["ny"] - 1)
    plot_diag3_profile(rr, z_off[iy, ix], z_on[iy, ix], panel,
                       float(P[files.index(panel)].max()))
    REPORT["diag3"]["profile_panel"] = dict(
        cut=panel, off_z_at_2m=float(z_off[iy, ix][rr.searchsorted(2.0)]),
        off_z_at_8m=float(z_off[iy, ix][rr.searchsorted(8.0)]),
        on_z_at_8m=float(z_on[iy, ix][rr.searchsorted(8.0)]))
    return REPORT["diag3"]


# --------------------------------------------------------------------------- #
# plots
# --------------------------------------------------------------------------- #
BG, FG, GRID = "#ffffff", "#1a1a1a", "#d8d8d8"
CMAP = LinearSegmentedColormap.from_list(
    "negobs", ["#f7f7f4", "#cfe0e8", "#7fb3c8", "#3d7f9e", "#1f4c63"])
CMAP_W = LinearSegmentedColormap.from_list(
    "negobs_w", ["#f7f7f4", "#f2ddc4", "#e8b06a", "#d1762f", "#8f3d10"])


def _grid_ax(ax, M, title, cmap, vmax, fmt="{:.3f}"):
    im = ax.imshow(M.reshape(3, 5), cmap=cmap, vmin=0, vmax=vmax, aspect="auto")
    ax.set_xticks(range(5)); ax.set_xticklabels(SECT, fontsize=9)
    ax.set_yticks(range(3))
    ax.set_yticklabels(["band1\n[0,2)m", "band2\n[2,5)m", "band3\n[5,12)m"], fontsize=8)
    for b in range(3):
        for s in range(5):
            v = M[b * 5 + s]
            ax.text(s, b, fmt.format(v), ha="center", va="center", fontsize=9,
                    color="#ffffff" if v > 0.55 * vmax else FG)
    ax.set_title(title, fontsize=10, color=FG, pad=8)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    return im


def plot_diag1(prior, fa, corr):
    fig, axes = plt.subplots(1, 4, figsize=(15.5, 3.5), facecolor=BG)
    _grid_ax(axes[0], prior, "① TRAIN prior  P(cell=1)\n480 on-arm train frames, 20 scenes",
             CMAP, max(prior.max(), 1e-6))
    _grid_ax(axes[1], fa["rgb"],
             f"RGB s42 — off-arm FIRING rate (all FA)\n168 test off frames, τ=0.5 · ρ vs prior = {corr['rgb']['rho']:+.3f}",
             CMAP_W, max(fa["rgb"].max(), 1e-6))
    _grid_ax(axes[2], fa["depth"],
             f"Depth s42 — off-arm FIRING rate (all FA)\nsame colour scale as RGB · ρ vs prior = {corr['depth']['rho']:+.3f}",
             CMAP_W, max(fa["rgb"].max(), 1e-6))
    ax = axes[3]
    ax.set_facecolor(BG)
    for arm, c, mk in (("rgb", "#d1762f", "o"), ("depth", "#3d7f9e", "s")):
        ax.scatter(prior, fa[arm], s=42, c=c, marker=mk, alpha=.85, edgecolor="none",
                   label=f"{arm.upper()}  ρ={corr[arm]['rho']:+.3f}")
    for i, c in enumerate(CELLS):
        ax.annotate(c, (prior[i], fa["rgb"][i]), fontsize=7, color="#8f3d10",
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("train positive rate", fontsize=9)
    ax.set_ylabel("off-arm firing rate (τ=0.5)", fontsize=9)
    ax.set_title("prior vs false-alarm, per cell\n(Spearman, 15 cells)", fontsize=10)
    ax.grid(color=GRID, lw=.6)
    ax.legend(fontsize=8, frameon=False)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag1_prior_vs_fa.png"), dpi=160, facecolor=BG)
    plt.close(fig)


def plot_diag2(out):
    fig, ax = plt.subplots(figsize=(8.2, 4.2), facecolor=BG)
    labels = ["band1\n[0,2)m", "band2\n[2,5)m", "band3\n[5,12)m", "all bands"]
    keys = ["band1", "band2", "band3", "all bands"]
    xs = np.arange(4)
    for k, (arm, c) in enumerate((("rgb", "#d1762f"), ("depth", "#3d7f9e"))):
        m = [out[arm]["bands"][q].get("mean", np.nan) for q in keys]
        lo = [out[arm]["bands"][q].get("lo", np.nan) for q in keys]
        hi = [out[arm]["bands"][q].get("hi", np.nan) for q in keys]
        off = (k - .5) * .34
        err = np.abs(np.vstack([np.array(m) - np.array(lo), np.array(hi) - np.array(m)]))
        ax.bar(xs + off, m, .32, color=c, label=f"{arm.upper()} U-Net s42", zorder=2)
        ax.errorbar(xs + off, m, yerr=err, fmt="none", ecolor=FG, elinewidth=1.2,
                    capsize=4, zorder=3)
        for xi, mi, hj in zip(xs + off, m, hi):
            if np.isfinite(mi):
                ax.text(xi, hj + .015, f"{mi:.3f}", ha="center", fontsize=8, color=FG)
    ax.axhline(0, color=FG, lw=.9)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("twin Δ score  (on − off, max p over GT cells of that band)", fontsize=9)
    ax.set_title("② Twin Δ decomposed by distance band — 10 000× paired bootstrap, 95 % CI",
                 fontsize=10)
    ax.grid(axis="y", color=GRID, lw=.6, zorder=0)
    ax.legend(fontsize=9, frameon=False)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag2_twin_delta_bands.png"), dpi=160, facecolor=BG)
    plt.close(fig)


def plot_diag3(P, fired, cell_tab, files):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.6), facecolor=BG)
    fr = np.array([c["n_fire"] for c in cell_tab], float) / len(files)
    mp = np.array([c["mean_p"] for c in cell_tab], float)
    _grid_ax(axes[0], fr, "③ sceneC2 OFF arm — firing rate\n24 frames, RGB s42, τ=0.5",
             CMAP_W, 1.0, "{:.2f}")
    _grid_ax(axes[1], mp, "sceneC2 OFF arm — mean predicted p\n(GT = all-zero: every fire is a FA)",
             CMAP_W, 1.0, "{:.2f}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag3_sceneC2_offarm_cells.png"), dpi=160, facecolor=BG)
    plt.close(fig)


def plot_diag3_profile(rr, z_off, z_on, cut, maxp):
    fig, ax = plt.subplots(figsize=(8.6, 3.6), facecolor=BG)
    ax.plot(rr, z_on, color="#8f3d10", lw=2.0, label="hazard ON  (14-step stone stair, drop 2.24 m)")
    ax.plot(rr, z_off, color="#3d7f9e", lw=2.0, label="hazard OFF (flat slab + leaf scatter)")
    ax.axhspan(-0.30, 0.0, color="#e8b06a", alpha=.18, zorder=0)
    ax.text(11.6, -0.15, "0.30 m hazard depth", ha="right", va="center", fontsize=8, color="#8f3d10")
    for b in (2.0, 5.0):
        ax.axvline(b, color=GRID, lw=1.0, ls="--")
    ax.text(1.0, 0.9, "band1", fontsize=8, color="#777"); ax.text(3.3, 0.9, "band2", fontsize=8, color="#777")
    ax.text(8.2, 0.9, "band3  ← where the model fires", fontsize=8, color="#8f3d10")
    ax.set_xlabel("range along the camera's forward axis (m)", fontsize=9)
    ax.set_ylabel("ground height z (m)", fontsize=9)
    ax.set_title(f"③ sceneC2 centre-line ground profile — panel {cut} (OFF arm, max p = {maxp:.3f})",
                 fontsize=10)
    ax.annotate("OFF arm is flat to 16 mm over the whole fired region\n"
                "(max local drop in a 1.0 m window = 0.016 m = 5.5 % of the 0.30 m threshold)",
                xy=(8.5, 0.02), xytext=(6.2, 0.62), fontsize=8, color="#3d7f9e",
                arrowprops=dict(arrowstyle="->", color="#3d7f9e", lw=1.0))
    ax.set_ylim(-2.6, 1.2)
    ax.grid(color=GRID, lw=.6)
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag3_sceneC2_profile.png"), dpi=160, facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    diag1(); diag2(); diag3()
    with open(os.path.join(OUT, "diag_v1_numbers.json"), "w") as fh:
        json.dump(REPORT, fh, indent=1)
    print(json.dumps({k: REPORT[k] for k in ("diag1",)}, indent=1)[:1500])
    print("DONE")
