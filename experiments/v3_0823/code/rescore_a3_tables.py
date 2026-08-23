#!/usr/bin/env python3
"""A-3 appendix analysis — published (old GT) vs G7-corrected GT, 6 appendix-encoder runs.

Same metric bundle / gates / FA-matched rules as code/rescore_tables.py (canonical 9).
Read-only over:
  experiments/weekend_0823/newmodels/runs/<run>/eval_test/{metrics.json,per_frame.csv}
  experiments/v3_0823/eval_v2corr/<run>/{metrics.json,per_frame.csv}
Writes ONE file: experiments/v3_0823/eval_v2corr/rescore_a3_tables.json
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rescore_tables import (COR, TARGETS, index, load_pf, max_off_any, mean_hr,  # noqa: E402
                            metrics, recall_at, tau_for_fa_exact, tau_for_fa_grid)

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
NM = os.path.join(REPO, "experiments/weekend_0823/newmodels/runs")
DAY = os.path.join(REPO, "experiments/dayrun_0820")
V3 = os.path.join(REPO, "experiments/v3_0823")
ENCS = ("resnet50", "tu-convnext_tiny")
SEEDS = (42, 43, 44)
RUNS = [f"{e}_s{s}" for e in ENCS for s in SEEDS]
KEYS = ["cell_f1", "cell_recall", "cell_precision", "frame_det_rate", "frame_recall_V",
        "frame_recall_E", "frame_recall_H", "frame_recall_H_weak", "frame_fa_off", "cell_fpr_off"]


def main():
    split = json.load(open(os.path.join(DAY, "split_v2_full.json")))
    test = set(split["test"])
    MA = json.load(open(os.path.join(DAY, "dataset_manifest_v2_full.json")))
    hazA = {f["frame_id"] for f in MA["frames"]
            if f["scene_id"] in test and f["toggle_state"] == "on"
            and any(v > 0.5 for v in f["polar_gt"])}

    res = {"runs": {}, "gates": {"p_max_abs_diff": {}, "frameid_match": {}, "H_row_identical": {}}}
    for run in RUNS:
        pubpf = load_pf(os.path.join(NM, run, "eval_test/per_frame.csv"))
        corpf = load_pf(os.path.join(COR, run, "per_frame.csv"))
        ip, ic = index(pubpf), index(corpf)
        res["gates"]["frameid_match"][run] = (set(ip) == set(ic))
        res["gates"]["p_max_abs_diff"][run] = max(
            float(np.abs(ip[k]["p"] - ic[k]["p"]).max()) for k in ip)
        pubm = json.load(open(os.path.join(NM, run, "eval_test/metrics.json")))["point"]["op"]
        corm = json.load(open(os.path.join(COR, run, "metrics.json")))["point"]["op"]
        res["gates"]["H_row_identical"][run] = {
            "frame_recall_H_pub": pubm["frame_recall_H"], "frame_recall_H_cor": corm["frame_recall_H"],
            "cell_recall_H_pub": pubm["cell_recall_H"], "cell_recall_H_cor": corm["cell_recall_H"],
            "identical": (abs(pubm["frame_recall_H"] - corm["frame_recall_H"]) < 1e-12
                          and abs(pubm["cell_recall_H"] - corm["cell_recall_H"]) < 1e-12)}
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
        res["runs"][run] = {"published": metrics(pubpf), "corrected": metrics(corpf),
                            "corrected_at_old_denom": metrics(corpf, restrict_ids=hazA),
                            "fa_matched": fam}

    agg = {}
    for m in ENCS:
        e = {}
        for tag in ("published", "corrected", "corrected_at_old_denom"):
            e[tag] = {}
            for k in KEYS:
                mu, hr, sd = mean_hr([res["runs"][f"{m}_s{s}"][tag].get(k) for s in SEEDS])
                e[tag][k] = {"mean": mu, "half_range": hr, "sigma": sd,
                             "per_seed": [res["runs"][f"{m}_s{s}"][tag].get(k) for s in SEEDS]}
        e["delta"] = {}
        for k in KEYS:
            dm = e["corrected"][k]["mean"] - e["published"][k]["mean"]
            sg = e["corrected"][k]["sigma"]
            e["delta"][k] = {"delta_mean": dm, "sigma_corrected": sg,
                             "exceeds_sigma": bool(np.isfinite(dm) and np.isfinite(sg)
                                                   and abs(dm) > sg)}
        e["fa_matched"] = {}
        for tag in ("published", "corrected"):
            e["fa_matched"][tag] = {}
            for rule in ("exact", "grid"):
                e["fa_matched"][tag][rule] = {}
                for tgt in TARGETS:
                    cells = [res["runs"][f"{m}_s{s}"]["fa_matched"][tag][str(tgt)][rule]
                             for s in SEEDS]
                    if any(c is None for c in cells):
                        e["fa_matched"][tag][rule][str(tgt)] = None
                        continue
                    e["fa_matched"][tag][rule][str(tgt)] = {
                        kk: dict(zip(("mean", "half_range", "sigma"),
                                     mean_hr([c[kk] for c in cells])),
                                 per_seed=[c[kk] for c in cells])
                        for kk in ("H", "E", "V", "FA", "tau")}
        agg[m] = e
    res["by_model"] = agg

    out = os.path.join(COR, "rescore_a3_tables.json")
    json.dump(res, open(out, "w"), indent=1, default=str)
    print("wrote", out)

    print("\n== GATES ==")
    print("p max|Δ|:", {k: f"{v:.2e}" for k, v in res["gates"]["p_max_abs_diff"].items()})
    print("H row identical:", {k: v["identical"] for k, v in res["gates"]["H_row_identical"].items()})
    print("\n== PER-RUN published -> corrected ==")
    for run in RUNS:
        p, c, o = (res["runs"][run][t] for t in
                   ("published", "corrected", "corrected_at_old_denom"))
        f = lambda d, k: ("  nan" if not np.isfinite(d.get(k, np.nan)) else f"{d[k]:.3f}")  # noqa: E731
        print(f"{run:22s} f1 {f(p,'cell_f1')}->{f(c,'cell_f1')} det {f(p,'frame_det_rate')}->"
              f"{f(c,'frame_det_rate')} V {f(p,'frame_recall_V')}->{f(c,'frame_recall_V')} "
              f"E {f(p,'frame_recall_E')}->{f(c,'frame_recall_E')} H {f(p,'frame_recall_H')}->"
              f"{f(c,'frame_recall_H')} Hw {f(p,'frame_recall_H_weak')}->{f(c,'frame_recall_H_weak')} "
              f"FA {f(p,'frame_fa_off')}->{f(c,'frame_fa_off')} prec {f(p,'cell_precision')}->"
              f"{f(c,'cell_precision')} | @327: det {f(o,'frame_det_rate')} V {f(o,'frame_recall_V')} "
              f"E {f(o,'frame_recall_E')} H {f(o,'frame_recall_H')}")
    print("\n== DELTA (model mean), * = |Δ| > sigma_corrected ==")
    for m in ENCS:
        for k in KEYS:
            d = agg[m]["delta"][k]
            if not np.isfinite(d["delta_mean"]):
                continue
            print(f"  {m:18s} {k:22s} pub {agg[m]['published'][k]['mean']:+.4f} -> "
                  f"cor {agg[m]['corrected'][k]['mean']:+.4f}  Δ {d['delta_mean']:+.4f} "
                  f"σ {d['sigma_corrected']:.4f} {'*' if d['exceeds_sigma'] else ''}")
    print("\n== FA-matched (exact) H / V, published -> corrected ==")
    for tgt in TARGETS:
        for m in ENCS:
            p = agg[m]["fa_matched"]["published"]["exact"][str(tgt)]
            c = agg[m]["fa_matched"]["corrected"]["exact"][str(tgt)]
            print(f"  FA {tgt:.3f} {m:18s} achFA {c['FA']['mean']:.3f} | "
                  f"H {p['H']['mean']:.3f}->{c['H']['mean']:.3f} (±{c['H']['half_range']:.3f}) | "
                  f"V {p['V']['mean']:.3f}->{c['V']['mean']:.3f} | "
                  f"E {p['E']['mean']:.3f}->{c['E']['mean']:.3f}")


if __name__ == "__main__":
    main()
