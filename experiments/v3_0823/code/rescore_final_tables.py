#!/usr/bin/env python3
"""Final-rows analysis — YOLO x3 (tau_op 0.25, det2cell adapter) + rgb_s42_aux (tau_op 0.5).

Same gates / decomposition as code/rescore_tables.py, but tau is per-arm.
Read-only.  -> experiments/v3_0823/eval_v2corr/rescore_final_tables.json
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rescore_tables import COR, index, load_pf, mean_hr  # noqa: E402

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DAY = os.path.join(REPO, "experiments/dayrun_0820")
ARMS = {  # run -> (published per_frame.csv, published metrics.json, tau_op)
    "yolo_s42": (f"{DAY}/runs/yolo_s42/eval_test/per_frame.csv",
                 f"{DAY}/runs/yolo_s42/eval_test/metrics.json", 0.25),
    "yolo_s43": (f"{DAY}/runs/yolo_s43/eval_test/per_frame.csv",
                 f"{DAY}/runs/yolo_s43/eval_test/metrics.json", 0.25),
    "yolo_s44": (f"{DAY}/runs/yolo_s44/eval_test/per_frame.csv",
                 f"{DAY}/runs/yolo_s44/eval_test/metrics.json", 0.25),
    "rgb_s42_aux": (f"{DAY}/runs/v2/rgb_s42_aux/eval_test/per_frame.csv",
                    f"{DAY}/runs/v2/rgb_s42_aux/eval_test/metrics.json", 0.5),
}
GROUPS = {"yolov8n": ["yolo_s42", "yolo_s43", "yolo_s44"], "rgb_s42_aux": ["rgb_s42_aux"]}
KEYS = ["cell_f1", "cell_recall", "cell_precision", "frame_det_rate", "frame_recall_V",
        "frame_recall_E", "frame_recall_H", "frame_recall_H_weak", "frame_fa_off", "cell_fpr_off"]


def metrics(rows, tau, restrict_ids=None):
    on = [r for r in rows if r["toggle"] == "on"]
    off = [r for r in rows if r["toggle"] == "off"]
    haz = [r for r in on if r["g"].any()]
    if restrict_ids is not None:
        haz = [r for r in haz if r["frame_id"] in restrict_ids]
    out = {}
    P = np.array([r["p"] for r in rows]) >= tau
    G = np.array([r["g"] for r in rows])
    tp = float((P & G).sum()); fp = float((P & ~G).sum()); fn = float((~P & G).sum())
    out["cell_f1"] = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")
    out["cell_recall"] = tp / (tp + fn) if (tp + fn) else float("nan")
    out["cell_precision"] = tp / (tp + fp) if (tp + fp) else float("nan")
    det = [bool(((r["p"] >= tau) & r["g"]).any()) for r in haz]
    out["frame_det_rate"] = float(np.mean(det)) if det else float("nan")
    out["n_hazard_frames"] = len(haz)
    for t in ("V", "E", "H", "H_weak"):
        s = [r for r in haz if r["tier"] == t]
        out[f"n_{t}"] = len(s)
        out[f"frame_recall_{t}"] = float(np.mean(
            [bool(((r["p"] >= tau) & r["g"]).any()) for r in s])) if s else float("nan")
        if s:
            pos = np.array([r["g"] for r in s]); pr = np.array([r["p"] for r in s]) >= tau
            out[f"cell_recall_{t}"] = float((pr & pos).sum() / pos.sum()) if pos.sum() else float("nan")
        else:
            out[f"cell_recall_{t}"] = float("nan")
    Po = np.array([r["p"] for r in off]) >= tau
    Go = np.array([r["g"] for r in off])
    out["frame_fa_off"] = float(Po.any(1).mean())
    out["cell_fpr_off"] = float((Po & ~Go).sum() / (~Go).sum())
    out["n_off"] = len(off)
    out["n_pos_cells"] = int(G.sum())
    return out


def main():
    split = json.load(open(os.path.join(DAY, "split_v2_full.json")))
    test = set(split["test"])
    MA = json.load(open(os.path.join(DAY, "dataset_manifest_v2_full.json")))
    hazA = {f["frame_id"] for f in MA["frames"]
            if f["scene_id"] in test and f["toggle_state"] == "on"
            and any(v > 0.5 for v in f["polar_gt"])}

    res = {"runs": {}, "gates": {"p_max_abs_diff": {}, "frameid_match": {},
                                 "H_row_identical": {}, "tau_op": {}}}
    for run, (ppf, pmj, tau) in ARMS.items():
        pub, cor = load_pf(ppf), load_pf(os.path.join(COR, run, "per_frame.csv"))
        ip, ic = index(pub), index(cor)
        res["gates"]["frameid_match"][run] = (set(ip) == set(ic))
        res["gates"]["p_max_abs_diff"][run] = max(
            float(np.abs(ip[k]["p"] - ic[k]["p"]).max()) for k in ip)
        res["gates"]["tau_op"][run] = {
            "published": json.load(open(pmj))["tau_op"],
            "corrected": json.load(open(os.path.join(COR, run, "metrics.json")))["tau_op"]}
        mp, mc = metrics(pub, tau), metrics(cor, tau)
        res["gates"]["H_row_identical"][run] = {
            "frame_recall_H_pub": mp["frame_recall_H"], "frame_recall_H_cor": mc["frame_recall_H"],
            "cell_recall_H_pub": mp["cell_recall_H"], "cell_recall_H_cor": mc["cell_recall_H"],
            "identical": all(abs(mp[k] - mc[k]) < 1e-12 or (np.isnan(mp[k]) and np.isnan(mc[k]))
                             for k in ("frame_recall_H", "cell_recall_H"))}
        res["runs"][run] = {"tau_op": tau, "published": mp, "corrected": mc,
                            "corrected_at_old_denom": metrics(cor, tau, restrict_ids=hazA)}

    res["by_group"] = {}
    for g, runs in GROUPS.items():
        e = {}
        for tag in ("published", "corrected", "corrected_at_old_denom"):
            e[tag] = {}
            for k in KEYS:
                vals = [res["runs"][r][tag].get(k) for r in runs]
                mu, hr, sd = mean_hr(vals)
                e[tag][k] = {"mean": mu, "half_range": hr, "sigma": sd, "per_seed": vals}
        e["delta"] = {}
        for k in KEYS:
            dm = e["corrected"][k]["mean"] - e["published"][k]["mean"]
            sg = e["corrected"][k]["sigma"]
            e["delta"][k] = {"delta_mean": dm, "sigma_corrected": sg,
                             "exceeds_sigma": bool(np.isfinite(dm) and np.isfinite(sg)
                                                   and sg > 0 and abs(dm) > sg),
                             "n_runs": len(runs)}
        res["by_group"][g] = e

    p = os.path.join(COR, "rescore_final_tables.json")
    json.dump(res, open(p, "w"), indent=1, default=str)
    print("wrote", p)
    print("\n== GATES ==")
    print("p max|Δ|:", {k: f"{v:.2e}" for k, v in res["gates"]["p_max_abs_diff"].items()})
    print("tau_op   :", {k: (v["published"], v["corrected"]) for k, v in res["gates"]["tau_op"].items()})
    print("H row identical:", {k: v["identical"] for k, v in res["gates"]["H_row_identical"].items()})
    print("\n== PER-RUN published -> corrected ==")
    for run in ARMS:
        p_, c_, o_ = (res["runs"][run][t] for t in
                      ("published", "corrected", "corrected_at_old_denom"))
        f = lambda d, k: ("  nan" if not np.isfinite(d.get(k, np.nan)) else f"{d[k]:.4f}")  # noqa: E731
        print(f"{run:12s} τ{res['runs'][run]['tau_op']} f1 {f(p_,'cell_f1')}->{f(c_,'cell_f1')} "
              f"det {f(p_,'frame_det_rate')}->{f(c_,'frame_det_rate')} "
              f"V {f(p_,'frame_recall_V')}->{f(c_,'frame_recall_V')} "
              f"E {f(p_,'frame_recall_E')}->{f(c_,'frame_recall_E')} "
              f"H {f(p_,'frame_recall_H')}->{f(c_,'frame_recall_H')} "
              f"Hw {f(p_,'frame_recall_H_weak')}->{f(c_,'frame_recall_H_weak')} "
              f"FA {f(p_,'frame_fa_off')}->{f(c_,'frame_fa_off')} "
              f"prec {f(p_,'cell_precision')}->{f(c_,'cell_precision')}")
        print(f"{'':12s}   @327: det {f(o_,'frame_det_rate')} V {f(o_,'frame_recall_V')} "
              f"E {f(o_,'frame_recall_E')} H {f(o_,'frame_recall_H')} "
              f"Hw {f(o_,'frame_recall_H_weak')} (nV {o_['n_V']} nHw {o_['n_H_weak']})")
    print("\n== DELTA (group mean), * = |Δ| > sigma_corrected ==")
    for g in GROUPS:
        for k in KEYS:
            d = res["by_group"][g]["delta"][k]
            if not np.isfinite(d["delta_mean"]):
                continue
            sg = d["sigma_corrected"]
            r = abs(d["delta_mean"]) / sg if sg > 0 else float("nan")
            print(f"  {g:12s} {k:22s} pub {res['by_group'][g]['published'][k]['mean']:+.4f} -> "
                  f"cor {res['by_group'][g]['corrected'][k]['mean']:+.4f}  Δ {d['delta_mean']:+.4f} "
                  f"σ {sg:.4f} ratio {r:.2f} {'*' if d['exceeds_sigma'] else ''}")


if __name__ == "__main__":
    main()
