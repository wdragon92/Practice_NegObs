#!/usr/bin/env python3
"""NIGHTRUN 0820 -- B1 (depth-decline hypothesis) + B2 (diagnostics v2, same axes as diag_v1).

Reads only frozen dayrun_0820 v2 artefacts (9 runs = 3 models x 3 seeds, grid
PROVISIONAL-GRID-V1 = 20 cells, band edges [0,2,5,8,12]).  Writes ONLY into this
directory.  CPU only, env_seg, no scipy (Spearman implemented in-file, same code
path as diag_v1.py).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" python diag_v2.py
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

sys.dont_write_bytecode = True          # never drop __pycache__ into read-only trees

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DR = os.path.join(REPO, "experiments/dayrun_0820")
RUNS = os.path.join(DR, "runs/v2")
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code"))
import bootstrap as BS  # noqa: E402

TAU = 0.5
MODELS = ("rgb", "depth", "b2")
SEEDS = (42, 43, 44)
SECT = ["A", "B", "C", "D", "E"]
BN = ["1", "2", "3a", "3b"]                       # band names, gridspec_v1
BEDGE = [0.0, 2.0, 5.0, 8.0, 12.0]
BLAB = {"1": "[0,2)", "2": "[2,5)", "3a": "[5,8)", "3b": "[8,12)"}
CELLS = [f"{s}{b}" for b in BN for s in SECT]     # index = band*5 + sector
N_CELLS = 20
N_PERM = 200000
REPORT: dict = {}
os.makedirs(OUT, exist_ok=True)


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


MANIFEST = json.load(open(os.path.join(DR, "dataset_manifest_v2_full.json")))
SPLIT = json.load(open(os.path.join(DR, "split_v2_full.json")))
FRAMES = {f["frame_id"]: f for f in MANIFEST["frames"]}
PF = {(m, s): read_per_frame(os.path.join(RUNS, f"{m}_s{s}/eval_test/per_frame.csv"))
      for m in MODELS for s in SEEDS}


def band_mask(b):
    """boolean(20,) selecting the 5 cells of band index b (0..3)."""
    m = np.zeros(N_CELLS, bool)
    m[b * 5:(b + 1) * 5] = True
    return m


BMASK = [band_mask(b) for b in range(4)]


# --------------------------------------------------------------------------- #
# own Spearman (average ranks, permutation p) -- byte-identical logic to diag_v1
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
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a - a.mean(), b - b.mean()
    den = math.sqrt(float((a * a).sum()) * float((b * b).sum()))
    return float((a * b).sum() / den) if den > 0 else float("nan")


def spearman(a, b, n_perm=N_PERM, seed=42):
    ra, rb = rankdata(a), rankdata(b)
    rho = pearson(ra, rb)
    if not np.isfinite(rho):
        return rho, float("nan")
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_perm):
        if abs(pearson(rng.permutation(ra), rb)) >= abs(rho) - 1e-12:
            hits += 1
    return rho, (hits + 1) / (n_perm + 1)


# --------------------------------------------------------------------------- #
# B1 -- per-band recall on test, split by evidence tier
# --------------------------------------------------------------------------- #
def band_recall(rows, tiers, bidx, dfilter=None):
    """(frame recall, cell recall, n frames w/ GT in band, n GT cells) restricted to `bidx`."""
    m = BMASK[bidx]
    nf = nf_hit = nc = nc_hit = 0
    for fid, r in rows.items():
        if r["tier"] not in tiers:
            continue
        if dfilter is not None and not dfilter(fid):
            continue
        pos = (r["g"] > 0.5) & m
        if not pos.any():
            continue
        nf += 1
        nc += int(pos.sum())
        nc_hit += int((r["p"][pos] >= TAU).sum())
        nf_hit += int((r["p"][pos] >= TAU).any())
    return (nf_hit / nf if nf else float("nan"),
            nc_hit / nc if nc else float("nan"), nf, nc)


def frame_recall_all(rows, tiers, dfilter=None):
    """Unrestricted frame recall (any GT cell fires) -- the SEED_TABLE statistic."""
    n = hit = 0
    for fid, r in rows.items():
        if r["tier"] not in tiers:
            continue
        if dfilter is not None and not dfilter(fid):
            continue
        pos = r["g"] > 0.5
        n += 1
        hit += int(bool(pos.any() and (r["p"][pos] >= TAU).any()))
    return (hit / n if n else float("nan")), n


def b1():
    out = {"tau": TAU, "bands": BN, "band_edges_m": BEDGE}

    # --- (a) structure of the v2 test set: where the GT of each tier lives ----
    rows0 = PF[("rgb", 42)]
    struct = {}
    for tier in ("V", "E", "H", "H_weak"):
        sub = {k: v for k, v in rows0.items() if v["tier"] == tier}
        G = np.array([v["g"] for v in sub.values()])
        d = np.array([FRAMES[k]["cam"]["d"] for k in sub])
        rounds = {}
        for k in sub:
            rounds[FRAMES[k]["round"]] = rounds.get(FRAMES[k]["round"], 0) + 1
        struct[tier] = dict(
            n_frames=len(sub),
            frames_with_gt_in_band={BN[b]: int((G[:, b * 5:(b + 1) * 5].sum(1) > 0).sum())
                                    for b in range(4)},
            gt_cells_in_band={BN[b]: int(G[:, b * 5:(b + 1) * 5].sum()) for b in range(4)},
            cam_d=dict(mean=float(d.mean()), median=float(np.median(d)),
                       min=float(d.min()), max=float(d.max())),
            by_round=rounds)
    out["test_tier_structure"] = struct

    # --- (b) per-band frame/cell recall, per model x seed, per tier -----------
    per = {}
    for m in MODELS:
        for s in SEEDS:
            rows = PF[(m, s)]
            rec = {}
            for tier_key, tiers in (("H", ("H",)), ("V", ("V",)), ("E", ("E",)),
                                    ("H+H_weak", ("H", "H_weak")), ("all_on", ("V", "E", "H", "H_weak"))):
                rec[tier_key] = {}
                for b, bname in enumerate(BN):
                    fr, cr, nf, nc = band_recall(rows, tiers, b)
                    rec[tier_key][bname] = dict(frame_recall=fr, cell_recall=cr,
                                                n_frames=nf, n_gt_cells=nc)
                fa, nfa = frame_recall_all(rows, tiers)
                rec[tier_key]["_unrestricted"] = dict(frame_recall=fa, n_frames=nfa)
            # --- (c) H split by render round / camera standoff ---------------
            main = lambda fid: FRAMES[fid]["round"] == "260819_main_on"          # noqa: E731
            boost = lambda fid: FRAMES[fid]["round"] != "260819_main_on"          # noqa: E731
            rec["H_by_round"] = {}
            for lbl, filt in (("main_21", main), ("boost_75", boost)):
                fa, nfa = frame_recall_all(rows, ("H",), filt)
                rec["H_by_round"][lbl] = dict(frame_recall=fa, n_frames=nfa)
                for b, bname in enumerate(BN):
                    fr, cr, nf, nc = band_recall(rows, ("H",), b, filt)
                    rec["H_by_round"][lbl][bname] = dict(frame_recall=fr, cell_recall=cr,
                                                         n_frames=nf, n_gt_cells=nc)
            rec["H_by_camd"] = {}
            for lbl, lo, hi in (("d<7", 0.0, 7.0), ("7<=d<9", 7.0, 9.0), ("d>=9", 9.0, 99.0)):
                filt = (lambda fid, lo=lo, hi=hi: lo <= FRAMES[fid]["cam"]["d"] < hi)
                fa, nfa = frame_recall_all(rows, ("H",), filt)
                rec["H_by_camd"][lbl] = dict(frame_recall=fa, n_frames=nfa)
            # --- (c2) WITHIN-FRAME 3a vs 3b on the 33 H frames carrying GT in both --
            both = [r for fid, r in rows.items()
                    if r["tier"] == "H" and ((r["g"] > .5) & BMASK[2]).any()
                    and ((r["g"] > .5) & BMASK[3]).any()]
            paired = {}
            for b, bname in (("2", "3a"), ("3", "3b")):
                bi = int(b)
                hit = sum(int((r["p"][(r["g"] > .5) & BMASK[bi]] >= TAU).any()) for r in both)
                cells = sum(int(((r["g"] > .5) & BMASK[bi]).sum()) for r in both)
                chit = sum(int((r["p"][(r["g"] > .5) & BMASK[bi]] >= TAU).sum()) for r in both)
                paired[bname] = dict(frame_recall=hit / len(both) if both else float("nan"),
                                     cell_recall=chit / cells if cells else float("nan"),
                                     n_frames=len(both), n_gt_cells=cells)
            paired["delta_3b_minus_3a_frame"] = paired["3b"]["frame_recall"] - paired["3a"]["frame_recall"]
            paired["delta_3b_minus_3a_cell"] = paired["3b"]["cell_recall"] - paired["3a"]["cell_recall"]
            rec["H_paired_3a_3b"] = paired
            per[f"{m}_s{s}"] = rec
    out["per_run"] = per

    # --- (d) seed means / ranges --------------------------------------------
    def agg(getter):
        r = {}
        for m in MODELS:
            v = [getter(per[f"{m}_s{s}"]) for s in SEEDS]
            v = [x for x in v if x is not None and np.isfinite(x)]
            r[m] = dict(mean=float(np.mean(v)) if v else float("nan"),
                        half_range=(float((max(v) - min(v)) / 2) if v else float("nan")),
                        seeds=[float(x) for x in v])
        return r

    mean = {}
    for tier_key in ("H", "V", "E", "all_on"):
        mean[tier_key] = {}
        for bname in BN:
            mean[tier_key][bname] = dict(
                frame_recall=agg(lambda d, t=tier_key, b=bname: d[t][b]["frame_recall"]),
                cell_recall=agg(lambda d, t=tier_key, b=bname: d[t][b]["cell_recall"]))
        mean[tier_key]["_unrestricted"] = agg(
            lambda d, t=tier_key: d[t]["_unrestricted"]["frame_recall"])
    mean["H_by_round"] = {lbl: agg(lambda d, l=lbl: d["H_by_round"][l]["frame_recall"])
                          for lbl in ("main_21", "boost_75")}
    mean["H_by_camd"] = {lbl: agg(lambda d, l=lbl: d["H_by_camd"][l]["frame_recall"])
                         for lbl in ("d<7", "7<=d<9", "d>=9")}
    mean["H_by_camd_n"] = {lbl: per["rgb_s42"]["H_by_camd"][lbl]["n_frames"]
                           for lbl in ("d<7", "7<=d<9", "d>=9")}
    mean["H_paired_3a_3b"] = {
        k: agg(lambda d, kk=k: (d["H_paired_3a_3b"][kk] if kk.startswith("delta")
                                else d["H_paired_3a_3b"][kk]["frame_recall"]))
        for k in ("3a", "3b", "delta_3b_minus_3a_frame")}
    mean["H_paired_3a_3b_cell"] = {
        k: agg(lambda d, kk=k: (d["H_paired_3a_3b"][kk] if kk.startswith("delta")
                                else d["H_paired_3a_3b"][kk]["cell_recall"]))
        for k in ("3a", "3b", "delta_3b_minus_3a_cell")}
    out["seed_mean"] = mean

    # --- (e) the hypothesis statistic: 3b - 3a slope on H, per model ----------
    slope = {}
    for m in MODELS:
        fr = [per[f"{m}_s{s}"]["H"]["3b"]["frame_recall"] - per[f"{m}_s{s}"]["H"]["3a"]["frame_recall"]
              for s in SEEDS]
        cr = [per[f"{m}_s{s}"]["H"]["3b"]["cell_recall"] - per[f"{m}_s{s}"]["H"]["3a"]["cell_recall"]
              for s in SEEDS]
        frv = [per[f"{m}_s{s}"]["V"]["3b"]["frame_recall"] - per[f"{m}_s{s}"]["V"]["2"]["frame_recall"]
               for s in SEEDS]
        crv = [per[f"{m}_s{s}"]["V"]["3b"]["cell_recall"] - per[f"{m}_s{s}"]["V"]["2"]["cell_recall"]
               for s in SEEDS]
        slope[m] = dict(H_frame_3b_minus_3a=dict(mean=float(np.mean(fr)), seeds=fr),
                        H_cell_3b_minus_3a=dict(mean=float(np.mean(cr)), seeds=cr),
                        V_frame_3b_minus_b2=dict(mean=float(np.mean(frv)), seeds=frv),
                        V_cell_3b_minus_b2=dict(mean=float(np.mean(crv)), seeds=crv))
    out["range_slope"] = slope

    REPORT["b1"] = out
    plot_b1(out)
    return out


# --------------------------------------------------------------------------- #
# B2 (i) -- per-cell train prior vs off-arm FA geography
# --------------------------------------------------------------------------- #
def diag1():
    train = set(SPLIT["train"])
    prior_n = np.zeros(N_CELLS)
    n_tr = 0
    for f in MANIFEST["frames"]:
        if f["scene_id"] in train and f["toggle_state"] == "on":
            prior_n += np.asarray(f["polar_gt"], float)
            n_tr += 1
    prior = prior_n / n_tr

    fa, fa_noC2, per_scene, n_off = {}, {}, {}, None
    for m in MODELS:
        for s in SEEDS:
            rows = [r for r in PF[(m, s)].values() if r["toggle"] == "off"]
            n_off = len(rows)
            key = f"{m}_s{s}"
            fa[key] = np.mean([(r["p"] >= TAU).astype(float) for r in rows], axis=0)
            keep = [r for r in rows if r["scene_id"] != "sceneC2"]
            fa_noC2[key] = np.mean([(r["p"] >= TAU).astype(float) for r in keep], axis=0)
            per_scene[key] = {}
            for sc in sorted({r["scene_id"] for r in rows}):
                sub = [r for r in rows if r["scene_id"] == sc]
                fired = np.array([(r["p"] >= TAU) for r in sub])
                per_scene[key][sc] = dict(n_frames=len(sub),
                                          frame_fa=float(fired.any(axis=1).mean()),
                                          n_cell_fires=int(fired.sum()))
            tot = sum(v["n_cell_fires"] for v in per_scene[key].values())
            for v in per_scene[key].values():
                v["share_of_cell_fires"] = (v["n_cell_fires"] / tot) if tot else 0.0

    corr = {}
    for m in MODELS:
        for s in SEEDS:
            key = f"{m}_s{s}"
            rho, p = spearman(prior, fa[key])
            rho2, p2 = spearman(prior, fa_noC2[key])
            corr[key] = dict(rho=rho, p_perm=p, pearson=pearson(prior, fa[key]),
                             rho_no_sceneC2=rho2, p_perm_no_sceneC2=p2,
                             ols_slope=float(np.polyfit(prior, fa[key], 1)[0]),
                             ols_intercept=float(np.polyfit(prior, fa[key], 1)[1]))
    corr_mean = {m: dict(rho_mean=float(np.mean([corr[f"{m}_s{s}"]["rho"] for s in SEEDS])),
                         rho_seeds=[corr[f"{m}_s{s}"]["rho"] for s in SEEDS],
                         rho_no_C2_mean=float(np.mean([corr[f"{m}_s{s}"]["rho_no_sceneC2"]
                                                       for s in SEEDS])))
                 for m in MODELS}

    fa_mean = {m: np.mean([fa[f"{m}_s{s}"] for s in SEEDS], axis=0) for m in MODELS}
    corr_of_mean = {m: dict(rho=spearman(prior, fa_mean[m], n_perm=N_PERM)[0]) for m in MODELS}

    REPORT["diag1"] = dict(
        n_train_on=n_tr, n_train_scenes=len(train), n_test_off=n_off,
        prior=prior.tolist(),
        fa={k: v.tolist() for k, v in fa.items()},
        fa_no_sceneC2={k: v.tolist() for k, v in fa_noC2.items()},
        fa_seed_mean={m: v.tolist() for m, v in fa_mean.items()},
        band_prior={BN[b]: float(prior[b * 5:(b + 1) * 5].mean()) for b in range(4)},
        band_fa_seed_mean={m: {BN[b]: float(fa_mean[m][b * 5:(b + 1) * 5].mean())
                               for b in range(4)} for m in MODELS},
        corr=corr, corr_seed_mean=corr_mean, corr_of_seed_mean_fa=corr_of_mean,
        per_scene_off=per_scene,
        config_train_positive_rate_oversampled=json.load(
            open(os.path.join(RUNS, "rgb_s42/config.json")))["train_positive_rate"])
    plot_diag1(prior, fa_mean, corr_mean, fa)
    return REPORT["diag1"]


# --------------------------------------------------------------------------- #
# B2 (ii) -- twin delta by band (4 bands), per model x seed, 10k paired bootstrap
# --------------------------------------------------------------------------- #
def diag2():
    out = {}
    for m in MODELS:
        for s in SEEDS:
            key = f"{m}_s{s}"
            pairs = []
            with open(os.path.join(RUNS, f"{m}_s{s}/twin/twin_pairs.csv")) as fh:
                for r in csv.DictReader(fh):
                    if r["kept"] == "True":
                        ds = r["delta_score"]
                        pairs.append((r["scene_id"], r["cut"], r["tier"],
                                      float(ds) if ds not in ("", "nan") else np.nan))
            rows = []
            for sc, cut, tier, ds_ref in pairs:
                on = PF[(m, s)].get(f"on/{sc}/{cut}")
                off = PF[(m, s)].get(f"off/{sc}/{cut}")
                if on is None or off is None:
                    continue
                pos = on["g"] > 0.5
                rec = dict(scene=sc, cut=cut, tier=tier, ds_ref=ds_ref, n_gt=int(pos.sum()))
                rec["all"] = (float(on["p"][pos].max() - off["p"][pos].max())
                              if pos.any() else np.nan)
                rec["on_all"] = float(on["p"][pos].max()) if pos.any() else np.nan
                rec["off_all"] = float(off["p"][pos].max()) if pos.any() else np.nan
                rec["argmax_band"] = (int(np.argmax(np.where(pos, on["p"], -1)) // 5)
                                      if pos.any() else -1)
                for b, bname in enumerate(BN):
                    msk = pos & BMASK[b]
                    rec[f"b{bname}"] = (float(on["p"][msk].max() - off["p"][msk].max())
                                        if msk.any() else np.nan)
                    rec[f"on_b{bname}"] = float(on["p"][msk].max()) if msk.any() else np.nan
                    rec[f"off_b{bname}"] = float(off["p"][msk].max()) if msk.any() else np.nan
                    rec[f"n_b{bname}"] = int(msk.sum())
                rows.append(rec)
            d = np.array([r["all"] - r["ds_ref"] for r in rows if np.isfinite(r["ds_ref"])])
            sanity = float(np.abs(d).max()) if d.size else float("nan")

            res = {}
            for kkey, lbl in ([("all", "all bands")] + [(f"b{b}", f"band{b}") for b in BN]):
                for tier_sel, tsfx in ((None, ""), ("H", "_H")):
                    sel = [r for r in rows if tier_sel is None or r["tier"] == tier_sel]
                    v = np.array([r[kkey] for r in sel], float)
                    ok = np.isfinite(v)
                    vv = v[ok]
                    name = lbl + tsfx
                    if vv.size == 0:
                        res[name] = dict(n=0)
                        continue
                    ci = BS.bootstrap_ci(lambda idx, vv=vv: {"mean": float(vv[idx].mean())},
                                         len(vv), n_boot=10000, seed=42)["mean"]
                    on_v = np.array([r[f"on_{kkey}"] for r in sel], float)[ok]
                    off_v = np.array([r[f"off_{kkey}"] for r in sel], float)[ok]
                    res[name] = dict(
                        n=int(vv.size), n_pairs_kept=len(sel),
                        mean=ci["point"], lo=ci["lo"], hi=ci["hi"],
                        excludes_zero=bool(ci["lo"] > 0 or ci["hi"] < 0),
                        median=float(np.median(vv)), frac_pos=float((vv > 0).mean()),
                        mean_on=float(on_v.mean()), mean_off=float(off_v.mean()),
                        n_gt_cells=int(sum(r[f"n_{kkey}"] for r in sel) if kkey != "all"
                                       else sum(r["n_gt"] for r in sel)))
            amb = [r["argmax_band"] for r in rows if r["argmax_band"] >= 0]
            out[key] = dict(bands=res, sanity_max_abs_dev=sanity,
                            argmax_band_share={BN[b]: float(np.mean(np.array(amb) == b))
                                               for b in range(4)})
    # seed means of the point estimates
    smean = {}
    for m in MODELS:
        smean[m] = {}
        for lbl in out[f"{m}_s42"]["bands"]:
            v = [out[f"{m}_s{s}"]["bands"][lbl].get("mean", np.nan) for s in SEEDS]
            v = [x for x in v if np.isfinite(x)]
            smean[m][lbl] = dict(mean=float(np.mean(v)) if v else float("nan"),
                                 half_range=float((max(v) - min(v)) / 2) if v else float("nan"),
                                 seeds=v,
                                 n=out[f"{m}_s42"]["bands"][lbl].get("n", 0))
    REPORT["diag2"] = dict(per_run=out, seed_mean=smean)
    plot_diag2(out, smean)
    return REPORT["diag2"]


# --------------------------------------------------------------------------- #
# B2 (iii) -- false-alarm scene decomposition
# --------------------------------------------------------------------------- #
V1_SCENE = {  # diag_v1 numbers, 168 off frames, 24/scene, s42 only
    "rgb": {"sceneC2": (0.875, 0.478), "sceneN3": (0.708, 0.391), "scene05": (0.208, 0.079),
            "scene18": (0.125, 0.051), "scene07": (0.0, 0.0), "scene14": (0.0, 0.0),
            "scene15": (0.0, 0.0)},
    "depth": {"sceneC2": (0.500, 0.680), "sceneN3": (0.250, 0.120), "scene05": (0.0, 0.0),
              "scene18": (0.375, 0.200), "scene07": (0.0, 0.0), "scene14": (0.0, 0.0),
              "scene15": (0.0, 0.0)},
}


def diag3():
    ps = REPORT["diag1"]["per_scene_off"]
    scenes = sorted(ps["rgb_s42"].keys())
    out = {"scenes": scenes, "per_model_seed_mean": {}, "per_run": ps, "v1_reference": V1_SCENE}
    for m in MODELS:
        rec = {}
        for sc in scenes:
            ff = [ps[f"{m}_s{s}"][sc]["frame_fa"] for s in SEEDS]
            cf = [ps[f"{m}_s{s}"][sc]["n_cell_fires"] for s in SEEDS]
            sh = [ps[f"{m}_s{s}"][sc]["share_of_cell_fires"] for s in SEEDS]
            nfr = ps[f"{m}_s42"][sc]["n_frames"]
            rec[sc] = dict(n_off_frames=nfr,
                           frame_fa_mean=float(np.mean(ff)), frame_fa_seeds=ff,
                           frame_fa_half_range=float((max(ff) - min(ff)) / 2),
                           cell_fires_mean=float(np.mean(cf)), cell_fires_seeds=cf,
                           share_of_cell_fires_mean=float(np.mean(sh)),
                           share_of_cell_fires_seeds=sh,
                           # frame-count-normalised share: what the share would be if every
                           # scene contributed the same number of off frames
                           fires_per_frame=float(np.mean(cf)) / nfr)
        tot_pf = sum(rec[sc]["fires_per_frame"] for sc in scenes)
        for sc in scenes:
            rec[sc]["share_rate_normalised"] = (rec[sc]["fires_per_frame"] / tot_pf) if tot_pf else 0.0
        # overall off-arm frame FA (all 408 frames), per seed
        overall = []
        for s in SEEDS:
            rows = [r for r in PF[(m, s)].values() if r["toggle"] == "off"]
            fired = np.array([(r["p"] >= TAU) for r in rows])
            overall.append(float(fired.any(axis=1).mean()))
        rec["_overall"] = dict(frame_fa_mean=float(np.mean(overall)), frame_fa_seeds=overall,
                               n_off_frames=len(rows))
        # off-arm FA split by render round: are the NEW off frames the new FA source?
        by_round = {}
        for rnd_lbl, keep in (("main_168", lambda fid: FRAMES[fid]["round"] == "260819_main_off"),
                              ("boost_240", lambda fid: FRAMES[fid]["round"] != "260819_main_off")):
            ff, cf, nfr = [], [], None
            for s in SEEDS:
                sub = [(fid, r) for fid, r in PF[(m, s)].items()
                       if r["toggle"] == "off" and keep(fid)]
                fired = np.array([(r["p"] >= TAU) for _, r in sub])
                nfr = len(sub)
                ff.append(float(fired.any(axis=1).mean()))
                cf.append(int(fired.sum()))
            by_round[rnd_lbl] = dict(n_off_frames=nfr, frame_fa_mean=float(np.mean(ff)),
                                     frame_fa_seeds=ff, cell_fires_mean=float(np.mean(cf)))
        rec["_by_round"] = by_round
        out["per_model_seed_mean"][m] = rec
    REPORT["diag3"] = out
    plot_diag3(out)
    return out


# --------------------------------------------------------------------------- #
# plots -- same palette / idiom as diag_v1
# --------------------------------------------------------------------------- #
BG, FG, GRID = "#ffffff", "#1a1a1a", "#d8d8d8"
CMAP = LinearSegmentedColormap.from_list(
    "negobs", ["#f7f7f4", "#cfe0e8", "#7fb3c8", "#3d7f9e", "#1f4c63"])
CMAP_W = LinearSegmentedColormap.from_list(
    "negobs_w", ["#f7f7f4", "#f2ddc4", "#e8b06a", "#d1762f", "#8f3d10"])
MCOL = {"rgb": "#d1762f", "depth": "#3d7f9e", "b2": "#6a8f3d"}


def _grid_ax(ax, M, title, cmap, vmax, fmt="{:.3f}"):
    """20-cell heat map, 4 bands (rows, far at top) x 5 sectors."""
    im = ax.imshow(M.reshape(4, 5)[::-1], cmap=cmap, vmin=0, vmax=vmax, aspect="auto")
    ax.set_xticks(range(5)); ax.set_xticklabels(SECT, fontsize=9)
    ax.set_yticks(range(4))
    ax.set_yticklabels([f"band{b}\n{BLAB[b]}m" for b in BN[::-1]], fontsize=8)
    for r in range(4):
        b = 3 - r
        for s in range(5):
            v = M[b * 5 + s]
            ax.text(s, r, fmt.format(v), ha="center", va="center", fontsize=9,
                    color="#ffffff" if v > 0.55 * vmax else FG)
    ax.set_title(title, fontsize=10, color=FG, pad=8)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    return im


def plot_b1(out):
    fig, axg = plt.subplots(2, 2, figsize=(12.6, 8.2), facecolor=BG)
    axes = [axg[0, 0], axg[0, 1], axg[1, 0], axg[1, 1]]
    sm = out["seed_mean"]

    def series(tier, key, model):
        return [sm[tier][b][key][model]["mean"] for b in BN], \
               [sm[tier][b][key][model]["half_range"] for b in BN]

    for ax, tier, keep, ttl in (
            (axes[0], "H", ["3a", "3b"],
             "H tier — no drop pixels, context only\n(96 frames; GT exists ONLY in 3a/3b)"),
            (axes[1], "V", ["1", "2", "3a", "3b"],
             "V tier — drop surface visible\n(180 frames)")):
        idx = [BN.index(b) for b in keep]
        xs = np.arange(len(keep))
        for m in MODELS:
            mu, hr = series(tier, "frame_recall", m)
            mu = [mu[i] for i in idx]; hr = [hr[i] for i in idx]
            ax.errorbar(xs, mu, yerr=hr, color=MCOL[m], marker="o", lw=2.0, capsize=4,
                        label=f"{m.upper()} (3 seeds, ±range/2)")
            for x, v in zip(xs, mu):
                if np.isfinite(v):
                    ax.annotate(f"{v:.3f}", (x, v), fontsize=8, color=MCOL[m],
                                xytext=(4, 5), textcoords="offset points")
        ax.set_xticks(xs)
        ax.set_xticklabels([f"band{b}\n{BLAB[b]} m" for b in keep], fontsize=9)
        ax.set_ylim(-0.03, 1.05)
        ax.set_ylabel("band-restricted frame recall (τ=0.5)", fontsize=9)
        ax.set_title(ttl, fontsize=10)
        ax.grid(color=GRID, lw=.6)
        ax.legend(fontsize=8, frameon=False, loc="upper left")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)

    # --- panel 3: the decisive axis -- camera standoff --------------------------
    ax = axes[2]
    dl = ["d<7", "7<=d<9", "d>=9"]
    nn = sm["H_by_camd_n"]
    xs = np.arange(3)
    for m in MODELS:
        mu = [sm["H_by_camd"][l][m]["mean"] for l in dl]
        hr = [sm["H_by_camd"][l][m]["half_range"] for l in dl]
        ax.errorbar(xs, mu, yerr=hr, color=MCOL[m], marker="o", lw=2.2, capsize=4,
                    label=f"{m.upper()} (3 seeds, ±range/2)")
        for x, v in zip(xs, mu):
            ax.annotate(f"{v:.3f}", (x, v), fontsize=8.5, color=MCOL[m],
                        xytext=(5, 6), textcoords="offset points")
    ax.annotate("Depth = 0.000 on ALL THREE seeds", (2, 0.0), fontsize=8.5, color="#3d7f9e",
                xytext=(-140, 42), textcoords="offset points",
                arrowprops=dict(arrowstyle="->", color="#3d7f9e", lw=1.1))
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{l} m\nn={nn[l]}" for l in dl], fontsize=9)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("camera standoff `cam.d` to the hazard anchor", fontsize=9)
    ax.set_ylabel("H frame recall (unrestricted, τ=0.5)", fontsize=9)
    ax.set_title("H recall vs RANGE — the decisive axis\n"
                 "Depth's missing-floor cue dies past 9 m; RGB's context does not", fontsize=10)
    ax.grid(color=GRID, lw=.6)
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    # --- panel 4: composition, against the v1 anchors on the identical 21 frames --
    ax = axes[3]
    labs = ["main_21  (= v1's test H set,\nbyte-identical frames)  d̄=6.6 m",
            "boost_75  (new far H)\nd̄=9.1 m"]
    xs = np.arange(2)
    w = 0.26
    for k, m in enumerate(MODELS):
        mu = [sm["H_by_round"][l][m]["mean"] for l in ("main_21", "boost_75")]
        hr = [sm["H_by_round"][l][m]["half_range"] for l in ("main_21", "boost_75")]
        ax.bar(xs + (k - 1) * w, mu, w, color=MCOL[m], label=f"{m.upper()} v2", zorder=2)
        ax.errorbar(xs + (k - 1) * w, mu, yerr=hr, fmt="none", ecolor=FG, elinewidth=1.1,
                    capsize=3, zorder=3)
        for x, v, h in zip(xs + (k - 1) * w, mu, hr):
            ax.text(x, v + h + 0.035, f"{v:.2f}", ha="center", fontsize=8, color=FG)
    for v1v, col, nm in ((0.3333, "#d1762f", "v1 RGB"), (0.7143, "#3d7f9e", "v1 Depth")):
        ax.plot([-0.45, 0.45], [v1v] * 2, color=col, ls=":", lw=2.2, zorder=5)
        ax.text(0.0, v1v + 0.02, f"{nm} s42 (v1 recipe) = {v1v:.3f}", fontsize=8, color=col,
                ha="center", zorder=6,
                bbox=dict(fc="#ffffff", ec="none", alpha=0.88, pad=1.4))
    ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=8.5)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("H frame recall (unrestricted, τ=0.5)", fontsize=9)
    ax.set_title("The 0.714 → 0.438 Depth decline is COMPOSITION\n"
                 "on v1's own 21 H frames v2-Depth scores 0.857, not 0.714", fontsize=10)
    ax.grid(axis="y", color=GRID, lw=.6, zorder=0)
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    fig.suptitle("B1 — depth-decline hypothesis: per-band and per-range recall on v2 test "
                 "(grid V1, 20 cells, τ=0.5, 3 seeds)", fontsize=11.5, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    fig.savefig(os.path.join(OUT, "b1_band_recall_tiers.png"), dpi=160, facecolor=BG)
    plt.close(fig)


def plot_diag1(prior, fa_mean, corr_mean, fa):
    fig, axes = plt.subplots(1, 4, figsize=(16.5, 4.3), facecolor=BG)
    _grid_ax(axes[0], prior,
             "① TRAIN prior P(cell=1)\n%d on-arm train frames, 19 scenes" % REPORT["diag1"]["n_train_on"],
             CMAP, max(prior.max(), 1e-6))
    vmax = max(fa_mean["rgb"].max(), fa_mean["depth"].max(), 1e-6)
    _grid_ax(axes[1], fa_mean["rgb"],
             "RGB — off-arm FIRING rate, 3-seed mean\n408 test off frames, τ=0.5 · ρ̄ = %+.3f"
             % corr_mean["rgb"]["rho_mean"], CMAP_W, vmax)
    _grid_ax(axes[2], fa_mean["depth"],
             "Depth — off-arm FIRING rate, 3-seed mean\nsame colour scale as RGB · ρ̄ = %+.3f"
             % corr_mean["depth"]["rho_mean"], CMAP_W, vmax)
    ax = axes[3]
    ax.set_facecolor(BG)
    for m, mk in (("rgb", "o"), ("depth", "s"), ("b2", "^")):
        ax.scatter(prior, fa_mean[m], s=44, c=MCOL[m], marker=mk, alpha=.85, edgecolor="none",
                   label=f"{m.upper()}  ρ̄={corr_mean[m]['rho_mean']:+.3f}")
    for i, c in enumerate(CELLS):
        ax.annotate(c, (prior[i], fa_mean["rgb"][i]), fontsize=6.5, color="#8f3d10",
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("train positive rate", fontsize=9)
    ax.set_ylabel("off-arm firing rate (τ=0.5)", fontsize=9)
    ax.set_title("prior vs false-alarm, per cell\n(Spearman, 20 cells; ρ̄ = mean of 3 per-seed ρ)",
                 fontsize=10)
    ax.grid(color=GRID, lw=.6)
    ax.legend(fontsize=8, frameon=False)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag1_prior_vs_fa_v2.png"), dpi=160, facecolor=BG)
    plt.close(fig)

    # companion: the 9 rho values as a strip, v1 anchor drawn in
    fig, ax = plt.subplots(figsize=(8.4, 4.0), facecolor=BG)
    for k, m in enumerate(MODELS):
        ys = [REPORT["diag1"]["corr"][f"{m}_s{s}"]["rho"] for s in SEEDS]
        xsj = [k + (i - 1) * 0.22 for i in range(3)]
        ax.scatter(xsj, ys, s=78, c=MCOL[m], zorder=3)
        for x, s, y in zip(xsj, SEEDS, ys):
            ax.annotate(f"s{s}\n{y:+.3f}", (x, y), fontsize=8, color=FG, ha="center",
                        xytext=(0, 10), textcoords="offset points")
        ax.plot([k - .34, k + .34], [np.mean(ys)] * 2, color=FG, lw=2.4, zorder=4)
        ax.annotate(f"ρ̄ = {np.mean(ys):+.3f}", (k, np.mean(ys)), fontsize=9, color=FG,
                    ha="center", xytext=(0, -17), textcoords="offset points", weight="bold")
    ax.axhline(0.9626, color="#8f3d10", ls="--", lw=1.5,
               label="v1 anchor: RGB s42, 15 cells, ρ = +0.963")
    ax.set_xticks(range(3)); ax.set_xticklabels([m.upper() for m in MODELS], fontsize=10)
    ax.set_xlim(-.55, 2.55); ax.set_ylim(0.30, 1.10)
    ax.set_ylabel("Spearman ρ (train prior ↔ off-arm FA rate), 20 cells", fontsize=9)
    ax.set_title("① v2: prior–FA coupling per model × seed (black bar = model mean)\n"
                 "bias-init + the 8 m split did NOT break the coupling", fontsize=10)
    ax.grid(axis="y", color=GRID, lw=.6)
    ax.legend(fontsize=8.5, frameon=False, loc="lower right")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag1_rho_by_seed.png"), dpi=160, facecolor=BG)
    plt.close(fig)


def plot_diag2(out, smean):
    fig, axs = plt.subplots(1, 2, figsize=(15.4, 4.8), facecolor=BG,
                            gridspec_kw=dict(width_ratios=[1.25, 1.0]))
    _plot_diag2_panel(axs[0], out, smean, "", "all 366 kept pairs")
    _plot_diag2_panel(axs[1], out, smean, "_H", "H tier only — 96 kept pairs")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag2_twin_delta_bands_v2.png"), dpi=160, facecolor=BG)
    plt.close(fig)


def _plot_diag2_panel(ax, out, smean, sfx, subtitle):
    keys = [f"band{b}{sfx}" for b in BN] + [f"all bands{sfx}"]
    labels = [f"band{b}\n{BLAB[b]} m" for b in BN] + ["all\nbands"]
    if sfx:                       # H tier carries GT only in 3a / 3b
        keep = [i for i, q in enumerate(keys)
                if smean["rgb"][q]["n"] > 0 and np.isfinite(smean["rgb"][q]["mean"])]
        keys = [keys[i] for i in keep]
        labels = [labels[i] for i in keep]
    xs = np.arange(len(keys))
    w = 0.26
    for k, m in enumerate(MODELS):
        mu = [smean[m][q]["mean"] for q in keys]
        hr = [smean[m][q]["half_range"] for q in keys]
        # 95 % CI of the s42 run, drawn as a light whisker behind the seed range
        lo = [out[f"{m}_s42"]["bands"][q].get("lo", np.nan) for q in keys]
        hi = [out[f"{m}_s42"]["bands"][q].get("hi", np.nan) for q in keys]
        pos = xs + (k - 1) * w
        ax.bar(pos, mu, w * 0.92, color=MCOL[m], label=f"{m.upper()} (3-seed mean)", zorder=2)
        ax.errorbar(pos, [out[f"{m}_s42"]["bands"][q].get("mean", np.nan) for q in keys],
                    yerr=np.abs(np.vstack([
                        np.array([out[f"{m}_s42"]["bands"][q].get("mean", np.nan) for q in keys]) - np.array(lo),
                        np.array(hi) - np.array([out[f"{m}_s42"]["bands"][q].get("mean", np.nan) for q in keys])])),
                    fmt="none", ecolor="#999999", elinewidth=1.0, capsize=3, zorder=3)
        ax.errorbar(pos, mu, yerr=hr, fmt="none", ecolor=FG, elinewidth=1.4, capsize=4, zorder=4)
        for x, v, h in zip(pos, mu, hr):
            if np.isfinite(v):
                ax.text(x, max(v + h, 0) + .022, f"{v:.3f}", ha="center", fontsize=7.5, color=FG)
    ax.axhline(0, color=FG, lw=.9)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("twin Δ (on − off, max p over GT cells of that band)", fontsize=9)
    ax.set_title("② Twin Δ by distance band — v2 grid V1, 3 seeds · %s\n"
                 "black bar = seed range/2 · grey whisker = s42 10 000× paired bootstrap 95 %% CI"
                 % subtitle, fontsize=10)
    ax.grid(axis="y", color=GRID, lw=.6, zorder=0)
    ax.legend(fontsize=8.5, frameon=False)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def plot_diag3(out):
    scenes = out["scenes"]
    order = ["sceneC2", "sceneN3", "scene05", "scene07", "scene14", "scene15", "scene18"]
    order = [s for s in order if s in scenes]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.2), facecolor=BG)
    xs = np.arange(len(order))
    w = 0.26
    ax = axes[0]
    for k, m in enumerate(MODELS):
        mu = [out["per_model_seed_mean"][m][s]["frame_fa_mean"] for s in order]
        hr = [out["per_model_seed_mean"][m][s]["frame_fa_half_range"] for s in order]
        ax.bar(xs + (k - 1) * w, mu, w * .92, color=MCOL[m], label=m.upper(), zorder=2)
        ax.errorbar(xs + (k - 1) * w, mu, yerr=hr, fmt="none", ecolor=FG, elinewidth=1.1,
                    capsize=3, zorder=3)
    for s_i, s in enumerate(order):
        if s in V1_SCENE["rgb"]:
            ax.plot([s_i - .42, s_i + .42], [V1_SCENE["rgb"][s][0]] * 2, color="#8f3d10",
                    ls="--", lw=1.3, zorder=5)
    ax.plot([], [], color="#8f3d10", ls="--", lw=1.3, label="v1 RGB s42 frame FA")
    ax.set_xticks(xs); ax.set_xticklabels(order, fontsize=8.5, rotation=20)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("off-arm frame FA rate (τ=0.5)", fontsize=9)
    ax.set_title("③ Where the false alarms live — per test scene, 3-seed mean", fontsize=10)
    ax.grid(axis="y", color=GRID, lw=.6, zorder=0)
    ax.legend(fontsize=8, frameon=False)

    ax = axes[1]
    for k, m in enumerate(MODELS):
        mu = [100 * out["per_model_seed_mean"][m][s]["share_of_cell_fires_mean"] for s in order]
        ax.bar(xs + (k - 1) * w, mu, w * .92, color=MCOL[m], label=m.upper(), zorder=2)
        for x, v in zip(xs + (k - 1) * w, mu):
            if v > 1:
                ax.text(x, v + 1.0, f"{v:.0f}", ha="center", fontsize=7.5, color=FG)
    for s_i, s in enumerate(order):
        if s in V1_SCENE["rgb"]:
            ax.plot([s_i - .42, s_i + .42], [100 * V1_SCENE["rgb"][s][1]] * 2, color="#8f3d10",
                    ls="--", lw=1.3, zorder=5)
    ax.plot([], [], color="#8f3d10", ls="--", lw=1.3, label="v1 RGB s42 share")
    ax.set_xticks(xs); ax.set_xticklabels(order, fontsize=8.5, rotation=20)
    ax.set_ylabel("share of all off-arm CELL fires (%)", fontsize=9)
    ax.set_title("③ Concentration of cell-level false alarms\n"
                 "(C2/N3 carry 24 off frames each, the other five 72 each)", fontsize=10)
    ax.grid(axis="y", color=GRID, lw=.6, zorder=0)
    ax.legend(fontsize=8, frameon=False)
    for a in axes:
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "diag3_fa_scene_decomp_v2.png"), dpi=160, facecolor=BG)
    plt.close(fig)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print("B1 ...", flush=True); b1()
    print("B2(i) ...", flush=True); diag1()
    print("B2(ii) ...", flush=True); diag2()
    print("B2(iii) ...", flush=True); diag3()
    with open(os.path.join(OUT, "diag_v2_numbers.json"), "w") as fh:
        json.dump(REPORT, fh, indent=1)
    print("DONE ->", OUT)
