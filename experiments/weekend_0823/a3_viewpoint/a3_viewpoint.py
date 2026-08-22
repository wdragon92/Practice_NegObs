#!/usr/bin/env python3
"""WEEKEND 0823 / CPU-2 -- 3a/3b viewpoint stratification of the H-tier twin delta.

Question (WEEKEND_BRIEF_0823 §6.5, ruling #4 material): DIAG_V2 §2.2 reports the H-tier
twin delta in band 3a [5,8) m as RGB -0.031 +-0.054 (s42 CI [-0.127,+0.017], contains 0)
against +0.293 in band 3b [8,12).  Is that ~0 UNIFORM over viewpoints, or is it the average
of a viewpoint-dependent mixture (e.g. concentrated at low camera height h~0.3, or in one
scene / one occluder type)?

Definitions are NOT redefined here.  3a / 3b are the two far distance bands of grid
PROVISIONAL-GRID-V1 as fixed by `experiments/nightrun_0820/narrative/diag_v2/DIAG_V2.md`
sec 0.6 / sec 2.2: band 3a = [5,8) m, band 3b = [8,12) m, cell index = band*5 + sector.
The twin delta is the same statistic as DIAG_V2 sec 2:
    delta_b = max p over GT-positive cells of band b on the hazard-ON frame
            - max p over the SAME cells on its pose-matched hazard-OFF twin.

Inputs (all frozen, read-only):
  experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/eval_test/per_frame.csv
  experiments/dayrun_0820/runs/v2/{...}/twin/twin_pairs.csv          (kept flag + delta_score)
  experiments/dayrun_0820/dataset_manifest_v2_full.json              (cam d / h_rel, raw_vis)
  experiments/dayrun_0820/split_v2_full.json
Outputs (this directory only): a3_viewpoint_numbers.json, a3_strata.csv, a3_viewpoint.png

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" python a3_viewpoint.py
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

sys.dont_write_bytecode = True

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
BN = ["1", "2", "3a", "3b"]
CELLS = [f"{s}{b}" for b in BN for s in SECT]
N_CELLS = 20
MIN_N = 5          # brief: refuse to over-read strata with n < 5
BOOT_N = 8         # only bootstrap a stratum at n >= 8


def band_mask(b):
    m = np.zeros(N_CELLS, bool)
    m[b * 5:(b + 1) * 5] = True
    return m


BMASK = [band_mask(b) for b in range(4)]


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

# --------------------------------------------------------------------------- #
# stratifier definitions -- fixed BEFORE looking at any delta (pre-registered)
# --------------------------------------------------------------------------- #
# h bins: the project's three judging viewpoints (scripts/make_review_gallery.py:
#   "robot eye h0.3 / human eye h0.9 / high h1.8"), cut midway between them.
H_BINS = [(0.25, 0.60, "h_lo (robot ~0.3)"),
          (0.60, 1.20, "h_mid (~0.9)"),
          (1.20, 1.91, "h_hi (~1.8)")]
# d bins: the standoff axis DIAG_V2 sec 0.3 already established as the working range axis.
D_BINS = [(0.0, 7.0, "d<7"), (7.0, 9.0, "d 7-9"), (9.0, 99.0, "d>=9")]
# finer d cut used INSIDE band 3a, whose frames all sit at d < 7.6
D_BINS_3A = [(0.0, 5.5, "d<5.5"), (5.5, 6.8, "d 5.5-6.8"), (6.8, 99.0, "d>=6.8")]
# occluder type -- see sec 2 of the .md: only two scenes carry test H frames, so
# occluder type is PERFECTLY CONFOUNDED with scene id.  Recorded, not resolved.
OCCLUDER = {"scene14": "tread/landing self-occlusion (perspective terrace illusion)",
            "scene15": "lateral wall + 25deg bend (corridor occlusion)"}


def hbin(h):
    for lo, hi, lab in H_BINS:
        if lo <= h < hi:
            return lab
    return "h_out"


def dbin(d, bins=D_BINS):
    for lo, hi, lab in bins:
        if lo <= d < hi:
            return lab
    return "d_out"


# --------------------------------------------------------------------------- #
# build the per-pair table: 96 H pairs x 9 runs
# --------------------------------------------------------------------------- #
def build_rows():
    """rows[(model,seed)] = list of dicts, one per kept H twin pair."""
    out = {}
    for m in MODELS:
        for s in SEEDS:
            pairs = []
            with open(os.path.join(RUNS, f"{m}_s{s}/twin/twin_pairs.csv")) as fh:
                for r in csv.DictReader(fh):
                    if r["kept"] == "True" and r["tier"] == "H":
                        ds = r["delta_score"]
                        pairs.append((r["scene_id"], r["cut"],
                                      float(ds) if ds not in ("", "nan") else np.nan))
            rows = []
            for sc, cut, ds_ref in pairs:
                fid_on, fid_off = f"on/{sc}/{cut}", f"off/{sc}/{cut}"
                on, off = PF[(m, s)].get(fid_on), PF[(m, s)].get(fid_off)
                if on is None or off is None:
                    continue
                man = FRAMES[fid_on]
                cam = man["cam"]
                pos = on["g"] > 0.5
                rec = dict(scene=sc, cut=cut, cond=man["cond"], round=man["round"],
                           d=cam["d"], h=cam["h_rel"], yaw=cam["yaw"], pitch=cam["pitch"],
                           hfov=cam["hfov"], ground_z=cam["ground_z"],
                           edge_projected=man["raw_vis"].get("edge_projected", -1),
                           hbin=hbin(cam["h_rel"]), dbin=dbin(cam["d"]),
                           dbin3a=dbin(cam["d"], D_BINS_3A),
                           occluder=OCCLUDER.get(sc, "?"),
                           n_gt=int(pos.sum()), ds_ref=ds_ref)
                rec["all"] = float(on["p"][pos].max() - off["p"][pos].max()) if pos.any() else np.nan
                for b, bname in zip((2, 3), ("3a", "3b")):
                    msk = pos & BMASK[b]
                    rec[f"d_{bname}"] = (float(on["p"][msk].max() - off["p"][msk].max())
                                         if msk.any() else np.nan)
                    rec[f"on_{bname}"] = float(on["p"][msk].max()) if msk.any() else np.nan
                    rec[f"off_{bname}"] = float(off["p"][msk].max()) if msk.any() else np.nan
                    # band-restricted frame recall: any GT cell of the band over tau
                    rec[f"rec_{bname}"] = (float(on["p"][msk].max() >= TAU) if msk.any() else np.nan)
                    rec[f"recoff_{bname}"] = (float(off["p"][msk].max() >= TAU) if msk.any() else np.nan)
                    rec[f"ncell_{bname}"] = int(msk.sum())
                rows.append(rec)
            out[(m, s)] = rows
    return out


ROWS = build_rows()


def sanity():
    """Reproduce DIAG_V2 sec 2.2 headline numbers -- proves this is the published statistic, split."""
    rep = {}
    for m in MODELS:
        for band in ("3a", "3b", "all"):
            key = f"d_{band}" if band != "all" else "all"
            vals = []
            for s in SEEDS:
                v = np.array([r[key] for r in ROWS[(m, s)]], float)
                v = v[np.isfinite(v)]
                vals.append(float(v.mean()))
            rep[f"{m}_{band}"] = dict(seeds=vals, mean=float(np.mean(vals)),
                                      half_range=float((max(vals) - min(vals)) / 2),
                                      n=int(np.isfinite(np.array([r[key] for r in ROWS[(m, 42)]],
                                                                 float)).sum()))
    # also reproduce delta_score column
    dev = []
    for m in MODELS:
        for s in SEEDS:
            for r in ROWS[(m, s)]:
                if np.isfinite(r["ds_ref"]) and np.isfinite(r["all"]):
                    dev.append(abs(r["all"] - r["ds_ref"]))
    rep["max_abs_dev_vs_twin_pairs_csv"] = float(max(dev)) if dev else float("nan")
    return rep


# --------------------------------------------------------------------------- #
# stratum aggregation
# --------------------------------------------------------------------------- #
def agg(model, key, sel, boot=True):
    """3-seed aggregate of column `key` over pairs passing predicate `sel`.

    Returns dict with per-seed means, 3-seed mean, half-range, n (pairs with a finite value,
    identical across seeds because pairing + GT are seed-independent), and the s42 percentile
    bootstrap CI when n >= BOOT_N.
    """
    per_seed, n = [], None
    for s in SEEDS:
        v = np.array([r[key] for r in ROWS[(model, s)] if sel(r)], float)
        v = v[np.isfinite(v)]
        n = int(v.size) if n is None else n
        per_seed.append(float(v.mean()) if v.size else float("nan"))
    out = dict(n=int(n or 0), seeds=per_seed,
               mean=float(np.nanmean(per_seed)) if n else float("nan"),
               half_range=float((np.nanmax(per_seed) - np.nanmin(per_seed)) / 2) if n else float("nan"))
    if boot and n and n >= BOOT_N:
        v42 = np.array([r[key] for r in ROWS[(model, 42)] if sel(r)], float)
        v42 = v42[np.isfinite(v42)]
        ci = BS.bootstrap_ci(lambda idx, v=v42: {"mean": float(v[idx].mean())},
                             len(v42), n_boot=10000, seed=42)["mean"]
        out["s42_point"], out["s42_lo"], out["s42_hi"] = ci["point"], ci["lo"], ci["hi"]
        out["s42_excludes_zero"] = bool(ci["lo"] > 0 or ci["hi"] < 0)
    return out


# --------------------------------------------------------------------------- #
# Spearman with permutation p (no scipy) -- same code path as diag_v1/diag_v2
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


def spearman(a, b, n_perm=20000, seed=42):
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
# main
# --------------------------------------------------------------------------- #
def main():
    REP = dict(
        purpose="CPU-2 / WEEKEND_BRIEF_0823 sec 6.5 -- viewpoint stratification of the H-tier "
                "twin delta in bands 3a/3b (definitions per diag_v2/DIAG_V2.md sec 0.6, 2.2)",
        tau=TAU, models=list(MODELS), seeds=list(SEEDS),
        h_bins=[list(b) for b in H_BINS], d_bins=[list(b) for b in D_BINS],
        d_bins_3a=[list(b) for b in D_BINS_3A], occluder_map=OCCLUDER,
        min_n_to_read=MIN_N, min_n_to_bootstrap=BOOT_N,
        sanity=sanity())

    # ---------- 0. the frame census, per stratum ---------------------------- #
    base = ROWS[("rgb", 42)]
    REP["census"] = dict(
        n_H_pairs=len(base),
        by_scene={sc: sum(r["scene"] == sc for r in base) for sc in sorted(OCCLUDER)},
        n_with_3a_gt=sum(np.isfinite(r["d_3a"]) for r in base),
        n_with_3b_gt=sum(np.isfinite(r["d_3b"]) for r in base),
        d_range_3a=[float(min(r["d"] for r in base if np.isfinite(r["d_3a"]))),
                    float(max(r["d"] for r in base if np.isfinite(r["d_3a"])))],
        d_range_3b=[float(min(r["d"] for r in base if np.isfinite(r["d_3b"]))),
                    float(max(r["d"] for r in base if np.isfinite(r["d_3b"])))],
        h_range_3a=[float(min(r["h"] for r in base if np.isfinite(r["d_3a"]))),
                    float(max(r["h"] for r in base if np.isfinite(r["d_3a"])))],
        h_range_3b=[float(min(r["h"] for r in base if np.isfinite(r["d_3b"]))),
                    float(max(r["h"] for r in base if np.isfinite(r["d_3b"])))],
    )
    # h x d contingency of the 3a subset and the full H set
    def contingency(pred):
        t = {}
        for hb in [b[2] for b in H_BINS]:
            for db in [b[2] for b in D_BINS]:
                t[f"{hb} | {db}"] = sum(1 for r in base if pred(r) and r["hbin"] == hb
                                        and r["dbin"] == db)
        return t
    REP["census"]["hxd_all_H"] = contingency(lambda r: True)
    REP["census"]["hxd_3a_subset"] = contingency(lambda r: np.isfinite(r["d_3a"]))
    REP["census"]["by_scene_3a"] = {sc: sum(r["scene"] == sc and np.isfinite(r["d_3a"])
                                            for r in base) for sc in sorted(OCCLUDER)}
    REP["census"]["by_cond_3a"] = {}
    for c in sorted({r["cond"] for r in base}):
        REP["census"]["by_cond_3a"][c] = sum(r["cond"] == c and np.isfinite(r["d_3a"]) for r in base)

    # ---------- 1. strata tables -------------------------------------------- #
    strata = {}

    def add(name, sel, note=""):
        entry = dict(note=note)
        for m in MODELS:
            for band in ("3a", "3b"):
                entry[f"{m}_delta_{band}"] = agg(m, f"d_{band}", sel)
                entry[f"{m}_recall_{band}"] = agg(m, f"rec_{band}", sel, boot=False)
                entry[f"{m}_recalloff_{band}"] = agg(m, f"recoff_{band}", sel, boot=False)
                entry[f"{m}_pon_{band}"] = agg(m, f"on_{band}", sel, boot=False)
                entry[f"{m}_poff_{band}"] = agg(m, f"off_{band}", sel, boot=False)
        strata[name] = entry

    add("ALL H", lambda r: True, "reproduces DIAG_V2 sec 2.2")
    for sc in sorted(OCCLUDER):
        add(f"scene={sc}", lambda r, sc=sc: r["scene"] == sc, OCCLUDER[sc])
    for lo, hi, lab in H_BINS:
        add(f"h:{lab}", lambda r, lo=lo, hi=hi: lo <= r["h"] < hi)
    for lo, hi, lab in D_BINS:
        add(f"d:{lab}", lambda r, lo=lo, hi=hi: lo <= r["d"] < hi)
    for lo, hi, lab in D_BINS_3A:
        add(f"d3a:{lab}", lambda r, lo=lo, hi=hi: lo <= r["d"] < hi)
    # h x d joint (only cells that exist)
    for _, _, hl in H_BINS:
        for _, _, dl in D_BINS:
            n = sum(1 for r in base if r["hbin"] == hl and r["dbin"] == dl)
            if n:
                add(f"hxd:{hl} | {dl}",
                    lambda r, hl=hl, dl=dl: r["hbin"] == hl and r["dbin"] == dl)
    # scene x h
    for sc in sorted(OCCLUDER):
        for _, _, hl in H_BINS:
            n = sum(1 for r in base if r["scene"] == sc and r["hbin"] == hl)
            if n:
                add(f"scene x h:{sc} | {hl}",
                    lambda r, sc=sc, hl=hl: r["scene"] == sc and r["hbin"] == hl)
    # light condition
    for c in sorted({r["cond"] for r in base}):
        add(f"cond:{c}", lambda r, c=c: r["cond"] == c)
    # render round
    for rd in sorted({r["round"] for r in base}):
        add(f"round:{rd}", lambda r, rd=rd: r["round"] == rd)
    REP["strata"] = strata

    # ---------- 2. continuous tests: does delta_3a move with h or d? -------- #
    cont = {}
    sub = [r for r in base if np.isfinite(r["d_3a"])]
    for m in MODELS:
        for s in SEEDS:
            rr = [r for r in ROWS[(m, s)] if np.isfinite(r["d_3a"])]
            for var in ("h", "d", "pitch", "edge_projected"):
                x = np.array([r[var] for r in rr], float)
                y = np.array([r["d_3a"] for r in rr], float)
                rho, p = spearman(x, y)
                cont[f"{m}_s{s}_delta3a_vs_{var}"] = dict(rho=rho, p_perm=p, n=len(rr))
            # same for 3b
            rr2 = [r for r in ROWS[(m, s)] if np.isfinite(r["d_3b"])]
            for var in ("h", "d"):
                x = np.array([r[var] for r in rr2], float)
                y = np.array([r["d_3b"] for r in rr2], float)
                rho, p = spearman(x, y)
                cont[f"{m}_s{s}_delta3b_vs_{var}"] = dict(rho=rho, p_perm=p, n=len(rr2))
    REP["continuous"] = cont
    REP["continuous_seed_summary"] = {}
    for m in MODELS:
        for band in ("3a", "3b"):
            for var in ("h", "d"):
                k = f"{m}_delta{band}_vs_{var}"
                v = [cont[f"{m}_s{s}_delta{band}_vs_{var}"]["rho"] for s in SEEDS
                     if f"{m}_s{s}_delta{band}_vs_{var}" in cont]
                if v:
                    REP["continuous_seed_summary"][k] = dict(
                        rhos=v, mean=float(np.mean(v)),
                        sign_agreement=bool(all(np.sign(x) == np.sign(v[0]) for x in v)))

    # ---------- 2b. CAMERA-POSE CLUSTERING --------------------------------- #
    # The 96 H pairs are 32 unique camera poses x 3 light conditions; the 33 band-3a pairs
    # are 11 poses x 3 conditions.  A frame-level bootstrap therefore treats light replicates
    # of ONE viewpoint as independent samples and understates the CI.  Everything below is
    # recomputed with the camera pose as the sampling unit.
    def pose_key(r):
        return (r["scene"], r["round"], round(r["d"], 3), round(r["h"], 3))

    clus = {}
    for band in ("3a", "3b"):
        for m in MODELS:
            per_seed_pose = {}
            for s in SEEDS:
                acc = {}
                for r in ROWS[(m, s)]:
                    v = r[f"d_{band}"]
                    if np.isfinite(v):
                        acc.setdefault(pose_key(r), []).append(v)
                per_seed_pose[s] = {k: float(np.mean(v)) for k, v in acc.items()}
            keys = sorted(per_seed_pose[42])
            pm = np.array([np.mean([per_seed_pose[s][k] for s in SEEDS]) for k in keys])
            # cluster bootstrap over poses, s42
            v42 = np.array([per_seed_pose[42][k] for k in keys])
            ci = BS.bootstrap_ci(lambda idx, v=v42: {"mean": float(v[idx].mean())},
                                 len(v42), n_boot=10000, seed=42)["mean"]
            # leave-one-pose-out jackknife on the 3-seed pose means
            jk = [float(np.delete(pm, i).mean()) for i in range(len(pm))]
            worst = int(np.argmax(np.abs(pm - pm.mean())))
            clus[f"{m}_{band}"] = dict(
                n_poses=len(keys), n_frames=int(len(keys) * 3),
                pose_mean_3seed=float(pm.mean()),
                pose_median_3seed=float(np.median(pm)),
                s42_cluster_point=ci["point"], s42_cluster_lo=ci["lo"], s42_cluster_hi=ci["hi"],
                s42_cluster_excludes_zero=bool(ci["lo"] > 0 or ci["hi"] < 0),
                jackknife_min=float(min(jk)), jackknife_max=float(max(jk)),
                most_influential_pose=dict(
                    scene=keys[worst][0], round=keys[worst][1], d=keys[worst][2],
                    h=keys[worst][3], pose_delta_3seed=float(pm[worst]),
                    mean_without_it=float(np.delete(pm, worst).mean())),
                poses=[dict(scene=k[0], round=k[1], d=k[2], h=k[3],
                            delta_3seed=float(np.mean([per_seed_pose[s][k] for s in SEEDS])),
                            per_seed=[per_seed_pose[s][k] for s in SEEDS]) for k in keys])
            # sign vote over poses
            clus[f"{m}_{band}"]["poses_positive"] = int((pm > 0).sum())
            clus[f"{m}_{band}"]["poses_negative"] = int((pm < 0).sum())
    REP["pose_clusters"] = clus

    # scene-restricted cluster estimates (the de-confounding cut)
    sc_clus = {}
    for sc in sorted(OCCLUDER):
        for band in ("3a", "3b"):
            for m in MODELS:
                acc = {}
                for s in SEEDS:
                    for r in ROWS[(m, s)]:
                        if r["scene"] != sc:
                            continue
                        v = r[f"d_{band}"]
                        if np.isfinite(v):
                            acc.setdefault((pose_key(r), s), []).append(v)
                keys = sorted({k for (k, s) in acc})
                if not keys:
                    continue
                pm = np.array([np.mean([np.mean(acc[(k, s)]) for s in SEEDS]) for k in keys])
                sc_clus[f"{sc}_{m}_{band}"] = dict(
                    n_poses=len(keys), pose_mean_3seed=float(pm.mean()),
                    pose_median_3seed=float(np.median(pm)),
                    poses_positive=int((pm > 0).sum()), poses_negative=int((pm < 0).sum()))
    REP["pose_clusters_by_scene"] = sc_clus

    # cluster CIs for the strata that carry the ruling (pose = sampling unit)
    def cluster_stratum(m, band, sel):
        per_seed_pose = {}
        for s in SEEDS:
            acc = {}
            for r in ROWS[(m, s)]:
                if not sel(r):
                    continue
                v = r[f"d_{band}"]
                if np.isfinite(v):
                    acc.setdefault(pose_key(r), []).append(v)
            per_seed_pose[s] = {k: float(np.mean(v)) for k, v in acc.items()}
        keys = sorted(per_seed_pose[42])
        if not keys:
            return None
        pm = np.array([np.mean([per_seed_pose[s][k] for s in SEEDS]) for k in keys])
        v42 = np.array([per_seed_pose[42][k] for k in keys])
        out = dict(n_poses=len(keys), n_frames=int(3 * len(keys)),
                   pose_mean_3seed=float(pm.mean()), pose_median_3seed=float(np.median(pm)),
                   poses_positive=int((pm > 0).sum()), poses_negative=int((pm < 0).sum()),
                   per_seed_pose_mean=[float(np.mean([per_seed_pose[s][k] for k in keys]))
                                       for s in SEEDS])
        if len(keys) >= 4:
            ci = BS.bootstrap_ci(lambda idx, v=v42: {"mean": float(v[idx].mean())},
                                 len(v42), n_boot=10000, seed=42)["mean"]
            out.update(s42_cluster_point=ci["point"], s42_cluster_lo=ci["lo"],
                       s42_cluster_hi=ci["hi"],
                       s42_cluster_excludes_zero=bool(ci["lo"] > 0 or ci["hi"] < 0))
        return out

    ruling = {}
    sels = {"ALL H": lambda r: True,
            "scene14": lambda r: r["scene"] == "scene14",
            "scene15": lambda r: r["scene"] == "scene15",
            "h_lo": lambda r: r["hbin"].startswith("h_lo"),
            "h_mid": lambda r: r["hbin"].startswith("h_mid"),
            "h_hi": lambda r: r["hbin"].startswith("h_hi"),
            "d<7": lambda r: r["d"] < 7.0,
            "d 7-9": lambda r: 7.0 <= r["d"] < 9.0,
            "d>=9": lambda r: r["d"] >= 9.0,
            "scene14 & h_lo": lambda r: r["scene"] == "scene14" and r["hbin"].startswith("h_lo"),
            "scene15 & h_lo": lambda r: r["scene"] == "scene15" and r["hbin"].startswith("h_lo"),
            "scene14 & h_mid": lambda r: r["scene"] == "scene14" and r["hbin"].startswith("h_mid"),
            "scene15 & h_mid": lambda r: r["scene"] == "scene15" and r["hbin"].startswith("h_mid")}
    for nm, sel in sels.items():
        for m in MODELS:
            for band in ("3a", "3b"):
                v = cluster_stratum(m, band, sel)
                if v:
                    ruling[f"{nm} | {m} | {band}"] = v
    REP["ruling_strata_cluster"] = ruling

    # ---------- 2c. control: is band 3a null for the OTHER tiers too? ------- #
    # If V/E frames also show Delta ~ 0 in band 3a, the null is a property of the band
    # (a grid/geometry artefact).  If only H is null there, the null is a property of
    # OCCLUSION at short standoff -- which is what the paper's H claim is about.
    tier_ctl = {}
    for m in MODELS:
        for tier in ("V", "E", "H"):
            for band in ("3a", "3b"):
                per_seed = []
                n = 0
                for s in SEEDS:
                    v = []
                    with open(os.path.join(RUNS, f"{m}_s{s}/twin/twin_pairs.csv")) as fh:
                        for r in csv.DictReader(fh):
                            if r["kept"] != "True" or r["tier"] != tier:
                                continue
                            on = PF[(m, s)].get(f"on/{r['scene_id']}/{r['cut']}")
                            off = PF[(m, s)].get(f"off/{r['scene_id']}/{r['cut']}")
                            if on is None or off is None:
                                continue
                            msk = (on["g"] > 0.5) & BMASK[2 if band == "3a" else 3]
                            if msk.any():
                                v.append(float(on["p"][msk].max() - off["p"][msk].max()))
                    n = len(v)
                    per_seed.append(float(np.mean(v)) if v else float("nan"))
                tier_ctl[f"{m}_{tier}_{band}"] = dict(
                    n=n, seeds=per_seed, mean=float(np.nanmean(per_seed)),
                    half_range=float((np.nanmax(per_seed) - np.nanmin(per_seed)) / 2))
    REP["tier_control"] = tier_ctl

    # ---------- 3. per-pair dump ------------------------------------------- #
    with open(os.path.join(OUT, "a3_strata.csv"), "w", newline="") as fh:
        cols = ["model", "seed", "scene", "occluder", "cut", "cond", "round", "d", "h",
                "pitch", "yaw", "hfov", "edge_projected", "hbin", "dbin", "dbin3a", "n_gt",
                "ncell_3a", "ncell_3b", "d_3a", "d_3b", "on_3a", "off_3a", "on_3b", "off_3b",
                "rec_3a", "rec_3b", "delta_all"]
        w = csv.writer(fh)
        w.writerow(cols)
        for m in MODELS:
            for s in SEEDS:
                for r in ROWS[(m, s)]:
                    w.writerow([m, s, r["scene"], r["occluder"], r["cut"], r["cond"], r["round"],
                                r["d"], r["h"], r["pitch"], r["yaw"], r["hfov"],
                                r["edge_projected"], r["hbin"], r["dbin"], r["dbin3a"], r["n_gt"],
                                r["ncell_3a"], r["ncell_3b"],
                                r["d_3a"], r["d_3b"], r["on_3a"], r["off_3a"],
                                r["on_3b"], r["off_3b"], r["rec_3a"], r["rec_3b"], r["all"]])

    with open(os.path.join(OUT, "a3_viewpoint_numbers.json"), "w") as fh:
        json.dump(REP, fh, indent=1, default=float)

    plot(REP, base)
    return REP


MCOL = {"rgb": "#d1762f", "depth": "#3d7f9e", "b2": "#6a8f3d"}


def plot(REP, base):
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6))

    # (a) delta_3a per stratum, RGB
    ax = axes[0]
    names = ["ALL H", "scene=scene14", "scene=scene15",
             "h:h_lo (robot ~0.3)", "h:h_mid (~0.9)", "h:h_hi (~1.8)",
             "d3a:d<5.5", "d3a:d 5.5-6.8", "d3a:d>=6.8"]
    y = np.arange(len(names))[::-1]
    for m in MODELS:
        xs, ys, ns = [], [], []
        for i, nm in enumerate(names):
            e = REP["strata"].get(nm, {}).get(f"{m}_delta_3a")
            if e and e["n"]:
                xs.append(e["mean"]); ys.append(y[i]); ns.append(e["n"])
        ax.scatter(xs, ys, color=MCOL[m], s=[max(14, 5 * n) for n in ns], label=m,
                   alpha=.85, zorder=3)
    for i, nm in enumerate(names):
        e = REP["strata"].get(nm, {}).get("rgb_delta_3a")
        if e and e["n"]:
            ax.annotate(f"n={e['n']}", (0.86, y[i]), fontsize=7, color="#666",
                        xycoords=("axes fraction", "data"), va="center")
    ax.axvline(0, color="#999", lw=1)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("H-tier twin $\\Delta$, band 3a [5,8) m (3-seed mean)", fontsize=9)
    ax.set_title("(a) band 3a $\\Delta$ by stratum", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x", alpha=.25)

    # (b) same for 3b
    ax = axes[1]
    for m in MODELS:
        xs, ys, ns = [], [], []
        for i, nm in enumerate(names):
            e = REP["strata"].get(nm, {}).get(f"{m}_delta_3b")
            if e and e["n"]:
                xs.append(e["mean"]); ys.append(y[i]); ns.append(e["n"])
        ax.scatter(xs, ys, color=MCOL[m], s=[max(14, 3 * n) for n in ns], alpha=.85, zorder=3)
    for i, nm in enumerate(names):
        e = REP["strata"].get(nm, {}).get("rgb_delta_3b")
        if e and e["n"]:
            ax.annotate(f"n={e['n']}", (0.86, y[i]), fontsize=7, color="#666",
                        xycoords=("axes fraction", "data"), va="center")
    ax.axvline(0, color="#999", lw=1)
    ax.set_yticks(y); ax.set_yticklabels([])
    ax.set_xlabel("H-tier twin $\\Delta$, band 3b [8,12) m (3-seed mean)", fontsize=9)
    ax.set_title("(b) band 3b $\\Delta$ by stratum", fontsize=10)
    ax.grid(axis="x", alpha=.25)

    # (c) scatter delta_3a vs h, RGB s42/43/44 pooled
    ax = axes[2]
    for m in MODELS:
        for s in SEEDS:
            rr = [r for r in ROWS[(m, s)] if np.isfinite(r["d_3a"])]
            ax.scatter([r["h"] for r in rr], [r["d_3a"] for r in rr], s=14,
                       color=MCOL[m], alpha=.45,
                       label=m if s == 42 else None)
    ax.axhline(0, color="#999", lw=1)
    for lo, hi, lab in H_BINS[:-1]:
        ax.axvline(hi, color="#bbb", ls=":", lw=1)
    ax.set_xlabel("camera height above ground $h_{rel}$ (m)", fontsize=9)
    ax.set_ylabel("per-pair twin $\\Delta$, band 3a", fontsize=9)
    ax.set_title("(c) is 3a $\\Delta\\approx0$ a low-$h$ effect?  (33 pairs x 3 seeds)", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=.25)

    fig.suptitle("CPU-2 -- H-tier twin $\\Delta$ stratified by viewpoint (h x d), scene and "
                 "occluder type; bands per DIAG_V2 sec 2.2", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(os.path.join(OUT, "a3_viewpoint.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    R = main()
    print(json.dumps(R["sanity"], indent=1, default=float))
    print(json.dumps(R["census"], indent=1, default=float))
