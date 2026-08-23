#!/usr/bin/env python3
"""V2_RESCORE analysis — published (old GT) vs G7-corrected GT, on test-core (816 frames).

Read-only over:
  experiments/dayrun_0820/runs/v2/<run>/eval_test/{metrics.json,per_frame.csv,twin/twin_pairs.csv}
  experiments/v3_0823/eval_v2corr/<run>/{metrics.json,per_frame.csv,twin/twin_pairs.csv}
  experiments/dayrun_0820/{dataset_manifest_v2_full.json,split_v2_full.json}
  experiments/v3_0823/dataset_manifest_v2corr.json
  experiments/v3_0823/code/hazgate.json
Writes ONE file: experiments/v3_0823/eval_v2corr/rescore_tables.json
"""
import csv
import json
import os
import re

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DAY = os.path.join(REPO, "experiments/dayrun_0820")
V3 = os.path.join(REPO, "experiments/v3_0823")
PUB = os.path.join(DAY, "runs/v2")
COR = os.path.join(V3, "eval_v2corr")
MODELS = ("rgb", "depth", "b2")
SEEDS = (42, 43, 44)
RUNS = [f"{m}_s{s}" for m in MODELS for s in SEEDS]
TARGETS = [0.359, 0.20, 0.10, 0.05]
TAU = 0.5
CUE = ["cue_railing", "cue_tactile", "cue_nosing", "cue_material_break", "cue_sign",
       "cue_scene_dressing"]


# ------------------------------------------------------------------ loaders
def load_pf(path):
    rows = list(csv.DictReader(open(path)))
    cells = [k[2:] for k in rows[0] if k.startswith("p_")]
    return [dict(frame_id=r["frame_id"], scene_id=r["scene_id"], tier=r["tier"],
                 toggle=r["toggle_state"],
                 p=np.array([float(r["p_" + c]) for c in cells]),
                 g=np.array([float(r["g_" + c]) for c in cells]) > 0.5) for r in rows]


def index(rows):
    return {r["frame_id"]: r for r in rows}


def mean_hr(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    return (float(np.mean(v)), float((max(v) - min(v)) / 2), float(np.std(v, ddof=1))) if v \
        else (float("nan"),) * 3


# ------------------------------------------------------------------ metric bundle
def metrics(rows, restrict_ids=None):
    """All headline metrics at TAU. restrict_ids limits the HAZARD (on-arm) population only;
    the off arm (FA) is always the full 408 — the off arm is untouched by the G7 repair."""
    on = [r for r in rows if r["toggle"] == "on"]
    off = [r for r in rows if r["toggle"] == "off"]
    haz = [r for r in on if r["g"].any()]
    if restrict_ids is not None:
        haz = [r for r in haz if r["frame_id"] in restrict_ids]
    out = {}
    P = np.array([r["p"] for r in rows]) >= TAU
    G = np.array([r["g"] for r in rows])
    tp = float((P & G).sum()); fp = float((P & ~G).sum()); fn = float((~P & G).sum())
    out["cell_f1"] = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")
    out["cell_recall"] = tp / (tp + fn) if (tp + fn) else float("nan")
    out["cell_precision"] = tp / (tp + fp) if (tp + fp) else float("nan")
    det = [bool(((r["p"] >= TAU) & r["g"]).any()) for r in haz]
    out["frame_det_rate"] = float(np.mean(det)) if det else float("nan")
    out["n_hazard_frames"] = len(haz)
    for t in ("V", "E", "H", "H_weak"):
        s = [r for r in haz if r["tier"] == t]
        out[f"frame_recall_{t}"] = float(np.mean(
            [bool(((r["p"] >= TAU) & r["g"]).any()) for r in s])) if s else float("nan")
        out[f"n_{t}"] = len(s)
        pos = np.array([r["g"] for r in s]); pr = np.array([r["p"] for r in s]) >= TAU if s else None
        out[f"cell_recall_{t}"] = float((pr & pos).sum() / pos.sum()) if s and pos.sum() else float("nan")
    Po = np.array([r["p"] for r in off]) >= TAU
    Go = np.array([r["g"] for r in off])
    out["frame_fa_off"] = float(Po.any(1).mean())
    out["cell_fpr_off"] = float((Po & ~Go).sum() / (~Go).sum())
    out["n_off"] = len(off)
    out["n_pos_cells"] = int(G.sum())
    return out


# ------------------------------------------------------------------ FA-matched
def max_on_gt(rows, tier):
    s = [r for r in rows if r["tier"] == tier and r["toggle"] == "on" and r["g"].any()]
    return np.array([r["p"][r["g"]].max() for r in s])


def max_off_any(rows, scenes=None):
    s = [r for r in rows if r["toggle"] == "off" and (scenes is None or r["scene_id"] in scenes)]
    return np.array([r["p"].max() for r in s])


def tau_for_fa_exact(off_max, target):
    n = len(off_max)
    srt = np.sort(off_max)[::-1]
    k = int(np.floor(target * n + 1e-9))
    if k >= n:
        return 0.0, 1.0
    tau = float(np.nextafter(srt[k], np.inf))
    return tau, float((off_max >= tau).mean())


def tau_for_fa_grid(off_max, target, step=0.01):
    for t in np.arange(step, 1.00, step):
        if float((off_max >= t).mean()) <= target:
            return float(t)
    return None


def recall_at(rows, tier, tau):
    v = max_on_gt(rows, tier)
    return float((v >= tau).mean()) if len(v) else None


# ------------------------------------------------------------------ scene classification
def classify_scenes():
    h = json.load(open(os.path.join(V3, "code/hazgate.json")))
    lib = {k: v for k, v in h.items() if k.split("::")[0] in ("main", "batch1")}
    prim, sec, detail = {}, {}, {}
    for k, e in lib.items():
        base = k.split("::")[1]
        sid = base.split("_")[0] if base.split("_")[0].startswith("scene") else base[:-3]
        wired = {c: e["cue"][c] for c in CUE if e["cue"].get(c)}
        st = {c: ("HZ" if r["all_hazard_gated"] else ("hz?" if r["any"] else "free"))
              for c, r in wired.items()}
        onk = {c: v for c, v in st.items() if e["defaults"].get(c) is True}
        prim[sid] = "C" if all(v == "free" for v in st.values()) else "D"
        sec[sid] = "C" if (onk and all(v == "free" for v in onk.values())) else "D"
        detail[sid] = {"all_wired": st, "default_on": onk}
    return prim, sec, detail


# ------------------------------------------------------------------ main
def main():
    split = json.load(open(os.path.join(DAY, "split_v2_full.json")))
    test = set(split["test"])
    MA = json.load(open(os.path.join(DAY, "dataset_manifest_v2_full.json")))
    MB = json.load(open(os.path.join(V3, "dataset_manifest_v2corr.json")))
    res = {}

    # ---- 0. GT census + old/new hazard populations -----------------------------
    def census(M):
        c, ids, npos = {}, set(), 0
        for f in M["frames"]:
            if f["scene_id"] not in test:
                continue
            pos = sum(1 for v in f["polar_gt"] if v > 0.5)
            npos += pos
            if f["toggle_state"] == "on":
                c[f["tier"]] = c.get(f["tier"], 0) + 1
                if pos > 0:
                    ids.add(f["frame_id"])
        return c, ids, npos
    cA, hazA, nposA = census(MA)
    cB, hazB, nposB = census(MB)
    res["census"] = {"old": cA, "corrected": cB,
                     "n_hazard_old": len(hazA), "n_hazard_corrected": len(hazB),
                     "n_pos_cells_old": nposA, "n_pos_cells_corrected": nposB,
                     "old_haz_subset_of_new": hazA <= hazB,
                     "entering_frames": sorted(hazB - hazA),
                     "leaving_frames": sorted(hazA - hazB)}
    tiA = {f["frame_id"]: f["tier"] for f in MA["frames"] if f["scene_id"] in test}
    tiB = {f["frame_id"]: f["tier"] for f in MB["frames"] if f["scene_id"] in test}
    mig = {}
    for k in tiA:
        if tiA[k] != tiB[k]:
            mig[f"{tiA[k]}->{tiB[k]}"] = mig.get(f"{tiA[k]}->{tiB[k]}", 0) + 1
    res["census"]["tier_migration_test"] = mig
    res["census"]["entering_scenes"] = sorted({i.split("/")[1] for i in (hazB - hazA)})

    # ---- 1. per-run tables -----------------------------------------------------
    res["runs"] = {}
    gate = {"p_max_abs_diff": {}, "frameid_match": {}, "H_row_identical": {}}
    for run in RUNS:
        pubpf = load_pf(os.path.join(PUB, run, "eval_test/per_frame.csv"))
        corpf = load_pf(os.path.join(COR, run, "per_frame.csv"))
        ip, ic = index(pubpf), index(corpf)
        gate["frameid_match"][run] = (set(ip) == set(ic))
        d = max(float(np.abs(ip[k]["p"] - ic[k]["p"]).max()) for k in ip)
        gate["p_max_abs_diff"][run] = d
        mp = metrics(pubpf)
        mc = metrics(corpf)
        mc327 = metrics(corpf, restrict_ids=hazA)
        pubm = json.load(open(os.path.join(PUB, run, "eval_test/metrics.json")))["point"]["op"]
        corm = json.load(open(os.path.join(COR, run, "metrics.json")))["point"]["op"]
        gate["H_row_identical"][run] = {
            "frame_recall_H_pub": pubm["frame_recall_H"], "frame_recall_H_cor": corm["frame_recall_H"],
            "cell_recall_H_pub": pubm["cell_recall_H"], "cell_recall_H_cor": corm["cell_recall_H"],
            "identical": (abs(pubm["frame_recall_H"] - corm["frame_recall_H"]) < 1e-12
                          and abs(pubm["cell_recall_H"] - corm["cell_recall_H"]) < 1e-12)}
        # ---- FA-matched on corrected GT (and on published GT, for the delta) ----
        fam = {}
        for tag, rows in (("published", pubpf), ("corrected", corpf)):
            om = max_off_any(rows)
            e = {}
            for tgt in TARGETS:
                te, fae = tau_for_fa_exact(om, tgt)
                tg = tau_for_fa_grid(om, tgt)
                e[str(tgt)] = {
                    "exact": {"tau": te, "FA": fae, "H": recall_at(rows, "H", te),
                              "E": recall_at(rows, "E", te), "V": recall_at(rows, "V", te)},
                    "grid": (None if tg is None else
                             {"tau": tg, "FA": float((om >= tg).mean()),
                              "H": recall_at(rows, "H", tg), "E": recall_at(rows, "E", tg),
                              "V": recall_at(rows, "V", tg)})}
            fam[tag] = e
        res["runs"][run] = {"published": mp, "corrected": mc, "corrected_at_old_denom": mc327,
                            "published_metrics_json": pubm, "corrected_metrics_json": corm,
                            "fa_matched": fam}

    res["gates"] = gate

    # ---- 2. off-arm FA heterogeneity (C-like / D-like) -------------------------
    prim, sec, detail = classify_scenes()
    tc = {s: {"primary": prim.get(s), "secondary": sec.get(s), "detail": detail.get(s)}
          for s in sorted(test)}
    res["scene_class"] = {"test_core": tc,
                          "library_C_primary": sorted([s for s, v in prim.items() if v == "C"]),
                          "library_D_primary": sorted([s for s, v in prim.items() if v == "D"])}
    fa_split = {}
    for run in RUNS:
        corpf = load_pf(os.path.join(COR, run, "per_frame.csv"))
        e = {}
        for rule, mp_ in (("primary", prim), ("secondary", sec)):
            Cs = {s for s in test if mp_.get(s) == "C"}
            Ds = {s for s in test if mp_.get(s) == "D"}
            oc, od = max_off_any(corpf, Cs), max_off_any(corpf, Ds)
            e[rule] = {"C_scenes": sorted(Cs), "D_scenes": sorted(Ds),
                       "n_off_C": len(oc), "n_off_D": len(od),
                       "fa_C": float((oc >= TAU).mean()), "fa_D": float((od >= TAU).mean())}
        e["per_scene"] = {}
        for s in sorted(test):
            v = max_off_any(corpf, {s})
            e["per_scene"][s] = {"n_off": len(v), "fa": float((v >= TAU).mean())}
        fa_split[run] = e
    res["fa_split"] = fa_split

    # ---- 3. twin restratification ---------------------------------------------
    def load_twin(path):
        rows = list(csv.DictReader(open(path)))
        out = []
        for r in rows:
            def fl(k):
                try:
                    return float(r.get(k, ""))
                except (TypeError, ValueError):
                    return float("nan")
            out.append(dict(scene_id=r["scene_id"], cut=r["cut"], tier=r["tier"],
                            kept=r["kept"].strip().lower() == "true", n_gt_pos=fl("n_gt_pos"),
                            max_on_gt=fl("max_on_gt"), max_off_gt=fl("max_off_gt"),
                            delta_score=fl("delta_score")))
        return out
    twin = {}
    for run in RUNS:
        pth_c = os.path.join(COR, run, "twin/twin_pairs.csv")
        pth_p = os.path.join(PUB, run, "twin/twin_pairs.csv")
        e = {}
        for tag, pth in (("published", pth_p), ("corrected", pth_c)):
            if not os.path.exists(pth):
                e[tag] = None
                continue
            rows = load_twin(pth)
            kept = [r for r in rows if r["kept"]]
            b = {"n_pairs": len(rows), "n_kept": len(kept),
                 "delta_all": float(np.nanmean([r["delta_score"] for r in kept]))}
            for t in ("V", "E", "H", "H_weak"):
                s = [r for r in kept if r["tier"] == t]
                b[f"n_{t}"] = len(s)
                b[f"delta_{t}"] = float(np.nanmean([r["delta_score"] for r in s])) if s else None
                # twin-conditional recall (F2 rule)
                sv = [r for r in s if np.isfinite(r["max_on_gt"])]
                b[f"tc_recall_{t}"] = float(np.mean(
                    [(r["max_on_gt"] >= TAU) and (r["max_off_gt"] < TAU) for r in sv])) if sv else None
                b[f"plain_recall_{t}"] = float(np.mean(
                    [r["max_on_gt"] >= TAU for r in sv])) if sv else None
            # H by scene
            b["H_by_scene"] = {}
            for sc in sorted({r["scene_id"] for r in kept if r["tier"] == "H"}):
                s = [r for r in kept if r["tier"] == "H" and r["scene_id"] == sc]
                b["H_by_scene"][sc] = {
                    "n": len(s), "delta": float(np.nanmean([r["delta_score"] for r in s])),
                    "plain": float(np.mean([r["max_on_gt"] >= TAU for r in s])),
                    "tc": float(np.mean([(r["max_on_gt"] >= TAU) and (r["max_off_gt"] < TAU)
                                         for r in s]))}
            e[tag] = b
        twin[run] = e
    res["twin"] = twin

    # ---- 4. model-level aggregation + sigma ------------------------------------
    KEYS = ["cell_f1", "cell_recall", "cell_precision", "frame_det_rate", "frame_recall_V",
            "frame_recall_E", "frame_recall_H", "frame_recall_H_weak", "frame_fa_off",
            "cell_fpr_off"]
    agg = {}
    for m in MODELS:
        e = {}
        for tag in ("published", "corrected", "corrected_at_old_denom"):
            e[tag] = {}
            for k in KEYS:
                vals = [res["runs"][f"{m}_s{s}"][tag].get(k) for s in SEEDS]
                mu, hr, sd = mean_hr(vals)
                e[tag][k] = {"mean": mu, "half_range": hr, "sigma": sd, "per_seed": vals}
        e["delta"] = {}
        for k in KEYS:
            dm = e["corrected"][k]["mean"] - e["published"][k]["mean"]
            sg = e["corrected"][k]["sigma"]
            e["delta"][k] = {"delta_mean": dm, "sigma_corrected": sg,
                             "exceeds_sigma": bool(np.isfinite(dm) and np.isfinite(sg) and abs(dm) > sg),
                             "per_seed_delta": [res["runs"][f"{m}_s{s}"]["corrected"].get(k)
                                                - res["runs"][f"{m}_s{s}"]["published"].get(k)
                                                if np.isfinite(res["runs"][f"{m}_s{s}"]["corrected"].get(k, np.nan))
                                                and np.isfinite(res["runs"][f"{m}_s{s}"]["published"].get(k, np.nan))
                                                else None for s in SEEDS]}
        # FA-matched aggregation
        e["fa_matched"] = {}
        for tag in ("published", "corrected"):
            e["fa_matched"][tag] = {}
            for tgt in TARGETS:
                for rule in ("exact", "grid"):
                    cells = [res["runs"][f"{m}_s{s}"]["fa_matched"][tag][str(tgt)][rule]
                             for s in SEEDS]
                    if any(c is None for c in cells):
                        e["fa_matched"][tag].setdefault(rule, {})[str(tgt)] = None
                        continue
                    e["fa_matched"][tag].setdefault(rule, {})[str(tgt)] = {
                        kk: dict(zip(("mean", "half_range", "sigma"),
                                     mean_hr([c[kk] for c in cells])), per_seed=[c[kk] for c in cells])
                        for kk in ("H", "E", "V", "FA", "tau")}
        # FA split aggregation
        e["fa_split"] = {}
        for rule in ("primary", "secondary"):
            for kk in ("fa_C", "fa_D"):
                vals = [fa_split[f"{m}_s{s}"][rule][kk] for s in SEEDS]
                mu, hr, sd = mean_hr(vals)
                e["fa_split"].setdefault(rule, {})[kk] = {
                    "mean": mu, "half_range": hr, "sigma": sd, "per_seed": vals}
        # twin aggregation
        e["twin"] = {}
        for tag in ("published", "corrected"):
            for kk in ["delta_all", "delta_V", "delta_E", "delta_H", "tc_recall_H", "tc_recall_V",
                       "tc_recall_E", "plain_recall_H", "n_H", "n_V", "n_E", "n_kept"]:
                vals = [twin[f"{m}_s{s}"][tag][kk] if twin[f"{m}_s{s}"][tag] else None
                        for s in SEEDS]
                vals = [v for v in vals]
                mu, hr, sd = mean_hr([v for v in vals if v is not None])
                e["twin"].setdefault(tag, {})[kk] = {"mean": mu, "half_range": hr, "sigma": sd,
                                                     "per_seed": vals}
        agg[m] = e
    res["by_model"] = agg

    out = os.path.join(COR, "rescore_tables.json")
    json.dump(res, open(out, "w"), indent=1, default=str)
    print("wrote", out)

    # ---- console summary --------------------------------------------------------
    print("\n== GATES ==")
    print("p max|Δ| per run:", {k: f"{v:.2e}" for k, v in gate["p_max_abs_diff"].items()})
    print("H row identical:", {k: v["identical"] for k, v in gate["H_row_identical"].items()})
    print("\n== CENSUS ==", json.dumps(res["census"]["old"]), "->",
          json.dumps(res["census"]["corrected"]))
    print("haz", res["census"]["n_hazard_old"], "->", res["census"]["n_hazard_corrected"],
          "| old subset of new:", res["census"]["old_haz_subset_of_new"],
          "| entering scenes:", res["census"]["entering_scenes"],
          "| migration:", res["census"]["tier_migration_test"])
    print("\n== DELTA (model mean, corrected - published), * = |Δ| > sigma_corrected ==")
    for m in MODELS:
        for k in KEYS:
            d = agg[m]["delta"][k]
            if not np.isfinite(d["delta_mean"]):
                continue
            print(f"  {m:6s} {k:22s} pub {agg[m]['published'][k]['mean']:+.4f} "
                  f"-> cor {agg[m]['corrected'][k]['mean']:+.4f}  Δ {d['delta_mean']:+.4f} "
                  f"σ {d['sigma_corrected']:.4f} {'*' if d['exceeds_sigma'] else ''}")
    print("\n== FA-matched (exact) corrected: model mean H ==")
    for tgt in TARGETS:
        row = []
        for m in MODELS:
            c = agg[m]["fa_matched"]["corrected"]["exact"][str(tgt)]
            p = agg[m]["fa_matched"]["published"]["exact"][str(tgt)]
            row.append(f"{m} {p['H']['mean']:.3f}->{c['H']['mean']:.3f}")
        dd = (agg["depth"]["fa_matched"]["corrected"]["exact"][str(tgt)]["H"]["mean"]
              - agg["rgb"]["fa_matched"]["corrected"]["exact"][str(tgt)]["H"]["mean"])
        print(f"  FA {tgt:.3f}: " + " | ".join(row) + f"   Δ(D-R)_cor {dd:+.3f}")
    print("\n== FA split (primary C/D) ==")
    for m in MODELS:
        p = agg[m]["fa_split"]["primary"]
        s = agg[m]["fa_split"]["secondary"]
        print(f"  {m:6s} primary  C {p['fa_C']['mean']:.3f} D {p['fa_D']['mean']:.3f} | "
              f"secondary C {s['fa_C']['mean']:.3f} D {s['fa_D']['mean']:.3f}")
    print("\n== TWIN (corrected vs published) ==")
    for m in MODELS:
        t = agg[m]["twin"]
        print(f"  {m:6s} all {t['published']['delta_all']['mean']:.3f}->{t['corrected']['delta_all']['mean']:.3f}"
              f" | H {t['published']['delta_H']['mean']:.3f}->{t['corrected']['delta_H']['mean']:.3f}"
              f" (n_H {t['published']['n_H']['mean']:.0f}->{t['corrected']['n_H']['mean']:.0f})"
              f" | V {t['published']['delta_V']['mean']:.3f}->{t['corrected']['delta_V']['mean']:.3f}"
              f" (n_V {t['published']['n_V']['mean']:.0f}->{t['corrected']['n_V']['mean']:.0f})")


if __name__ == "__main__":
    main()
