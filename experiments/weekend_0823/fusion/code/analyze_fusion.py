#!/usr/bin/env python3
"""GPU-3 / WEEKEND_BRIEF_0823 §6.4 — aggregate the fused row and decompose the marginal gain.

Reads (all already written; nothing here runs a model):
  experiments/weekend_0823/fusion/s<S>/fused_or/eval_test/metrics.json      fused row, tau 0.5 == OR rule
  experiments/weekend_0823/fusion/s<S>/fused_max/eval_test/metrics.json     raw-max sensitivity
  experiments/weekend_0823/fusion/s<S>/{fused_or,fused_max}/twin/twin_pairs.csv
  experiments/weekend_0823/fusion/s<S>/compare_fused_vs_rgb/metrics.json    paired bootstrap fused-rgb
  experiments/dayrun_0820/runs/v2/rgb_s<S>/eval_test/metrics.json           RGB-alone reference row
  experiments/dayrun_0820/runs/v2/rgb_s<S>/twin/twin_analysis.md            RGB-alone twin delta
  experiments/dayrun_0820/runs/yolo_s<S>/eval_test/metrics.json             YOLO-alone reference row
  the two source per_frame.csv files                                        cell-level attribution

Writes experiments/weekend_0823/fusion/FUSION_NUMBERS.json — every number quoted in
FUSION_ROW.md comes from this file.

Run with PYTHONNOUSERSITE=1 in env_seg. CPU only.
"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
import gridspec  # noqa: E402
from eval_polar import read_per_frame  # noqa: E402
from make_fused import TAU_U, TAU_Y, load_pair  # noqa: E402

FUS = os.path.join(ROOT, "experiments/weekend_0823/fusion")
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
SEEDS = [42, 43, 44]
KEYS = ["frame_recall_V", "frame_recall_E", "frame_recall_H", "frame_det_rate", "frame_fa_off",
        "cell_fpr_off", "cell_f1", "cell_recall", "cell_precision",
        "band1_cell_recall", "band2_cell_recall", "band3_cell_recall", "band4_cell_recall",
        "band1_cell_fpr_off", "band2_cell_fpr_off", "band3_cell_fpr_off", "band4_cell_fpr_off",
        "cell_recall_V", "cell_recall_E", "cell_recall_H"]


def mr(vals):
    """mean +- range/2 over seeds, the SEED_TABLE convention."""
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)], float)
    if not v.size:
        return dict(mean=None, half_range=None, n=0, vals=list(vals))
    return dict(mean=float(v.mean()), half_range=float((v.max() - v.min()) / 2), n=int(v.size),
                vals=[float(x) for x in v])


def jload(p):
    with open(p) as f:
        return json.load(f)


def twin_from_md(path):
    """mean twin delta_score for 'all' and 'H' out of a twin_analysis.md section 1 table."""
    out = {}
    with open(path) as f:
        for line in f:
            m = re.match(r"\|\s*(V|E|H|all)\s*\|\s*\d+\s*\|\s*([-\d.]+|n/a)\s*\[", line)
            if m:
                out[m.group(1)] = None if m.group(2) == "n/a" else float(m.group(2))
    return out


def twin_from_pairs(path):
    """Same statistic as twin_analysis section 1, recomputed from the per-pair CSV (point only)."""
    import csv
    rows = [r for r in csv.DictReader(open(path)) if r["kept"] == "True"]
    out = {}
    for g in ("V", "E", "H", "all"):
        sel = rows if g == "all" else [r for r in rows if r["tier"] == g]
        v = np.array([float(r["delta_score"]) for r in sel if r["delta_score"] not in ("", "nan")],
                     float)
        out[g] = float(np.nanmean(v)) if v.size and np.isfinite(v).any() else None
    return out


def attribution(grid):
    """Where do the cells that ONLY the detector fires actually land? Per seed."""
    band_of = np.asarray(grid.band_of)
    per_seed = {}
    for s in SEEDS:
        du, dy, _, _ = load_pair(s, grid=grid)
        pu, py, gt = du["probs"], dy["probs"], du["gt"] > 0.5
        tier, tog = du["tier"], du["toggle"]
        fu, fy = pu >= TAU_U, py >= TAU_Y
        new = fy & ~fu                                     # cells the union adds over RGB alone
        on, off = tog == "on", tog == "off"
        haz = on & gt.any(1)
        det_u = (fu & gt).any(1)
        det_f = ((fu | fy) & gt).any(1)
        rescued = det_f & ~det_u                           # frames flipped miss -> hit
        d = dict(
            n_new_cells=int(new.sum()),
            n_new_tp=int((new & gt).sum()), n_new_fp=int((new & ~gt).sum()),
            n_new_on=int(new[on].sum()), n_new_off=int(new[off].sum()),
            new_by_band={f"band{b+1}": int(new[:, band_of == b].sum()) for b in range(grid.n_bands)},
            new_tp_by_band={f"band{b+1}": int((new & gt)[:, band_of == b].sum())
                            for b in range(grid.n_bands)},
            yolo_fired_by_band={f"band{b+1}": int(fy[:, band_of == b].sum())
                                for b in range(grid.n_bands)},
            unet_fired_by_band={f"band{b+1}": int(fu[:, band_of == b].sum())
                                for b in range(grid.n_bands)},
            n_frames_with_new_cell=int(new.any(1).sum()),
            n_rescued_frames=int(rescued[haz].sum()),
            rescued_by_tier={t: int((rescued & haz & (tier == t)).sum()) for t in ("V", "E", "H")},
            n_haz_by_tier={t: int((haz & (tier == t)).sum()) for t in ("V", "E", "H")},
            n_new_off_frames=int(new[off].any(1).sum()),
            n_fa_frames_added=int((((fu | fy)[off].any(1)) & ~(fu[off].any(1))).sum()),
            n_off_frames=int(off.sum()),
        )
        per_seed[s] = d
    return per_seed


def main():
    grid = gridspec.load("gridspec_v1.json")
    rows = {}
    for name, pat in (("fused_or", os.path.join(FUS, "s{s}/fused_or/eval_test/metrics.json")),
                      ("fused_max", os.path.join(FUS, "s{s}/fused_max/eval_test/metrics.json")),
                      ("rgb", os.path.join(DAY, "runs/v2/rgb_s{s}/eval_test/metrics.json")),
                      ("yolo", os.path.join(DAY, "runs/yolo_s{s}/eval_test/metrics.json"))):
        per_seed = {s: jload(pat.format(s=s))["point"]["op"] for s in SEEDS}
        rows[name] = dict(per_seed={s: {k: per_seed[s].get(k) for k in KEYS} for s in SEEDS},
                          agg={k: mr([per_seed[s].get(k) for s in SEEDS]) for k in KEYS})

    twins = {}
    for name, pat in (("fused_or", os.path.join(FUS, "s{s}/fused_or/twin/twin_pairs.csv")),
                      ("fused_max", os.path.join(FUS, "s{s}/fused_max/twin/twin_pairs.csv")),
                      ("rgb", os.path.join(DAY, "runs/v2/rgb_s{s}/twin/twin_pairs.csv"))):
        ps = {s: twin_from_pairs(pat.format(s=s)) for s in SEEDS}
        twins[name] = dict(per_seed=ps,
                           agg={g: mr([ps[s][g] for s in SEEDS]) for g in ("V", "E", "H", "all")})

    # paired bootstrap, fused - rgb, on the 816 common test frames (frame-iid resample; the
    # scene-cluster caveat of weekend_0823/rt_response/F5 applies to any CI in this block)
    paired = {}
    for s in SEEDS:
        cmp_ = jload(os.path.join(FUS, f"s{s}/compare_fused_vs_rgb/metrics.json"))["compare"]
        paired[s] = {k: cmp_["diff"][k] for k in KEYS if k in cmp_["diff"]}
        paired[s]["_n_common"] = cmp_["n_common"]

    out = dict(
        rule=dict(fire="p_unet >= 0.50 OR p_yolo >= 0.25", tau_unet=TAU_U, tau_yolo=TAU_Y,
                  headline_csv="fused_or (phi-rescaled YOLO axis; tau 0.5 reproduces the OR rule)",
                  sensitivity_csv="fused_max (raw max(p_unet, p_yolo)); twin delta only"),
        counts=jload(os.path.join(FUS, "FUSION_PROVENANCE.json")),
        rows=rows, twin=twins, paired_fused_minus_rgb=paired,
        attribution=attribution(grid),
        seed_table_reference=dict(
            note="from experiments/dayrun_0820/runs/v2/SEED_TABLE.md sections 1/2/4",
            rgb=dict(frame_recall_V=0.796, frame_recall_E=0.556, frame_recall_H=0.688,
                     frame_det_rate=0.730, frame_fa_off=0.359, cell_f1=0.450,
                     twin_all=0.314, twin_H=0.285),
            yolo=dict(frame_recall_V=0.150, frame_recall_E=0.000, frame_recall_H=0.000,
                      frame_det_rate=0.083, frame_fa_off=0.024, cell_f1=0.026)))
    with open(os.path.join(FUS, "FUSION_NUMBERS.json"), "w") as f:
        json.dump(out, f, indent=2)

    def row(name, r):
        a = r["agg"]
        return (f"{name:10s} V {a['frame_recall_V']['mean']:.3f}+-{a['frame_recall_V']['half_range']:.3f}"
                f"  E {a['frame_recall_E']['mean']:.3f}+-{a['frame_recall_E']['half_range']:.3f}"
                f"  H {a['frame_recall_H']['mean']:.3f}+-{a['frame_recall_H']['half_range']:.3f}"
                f"  det {a['frame_det_rate']['mean']:.3f}"
                f"  FA {a['frame_fa_off']['mean']:.3f}+-{a['frame_fa_off']['half_range']:.3f}"
                f"  F1 {a['cell_f1']['mean']:.3f}+-{a['cell_f1']['half_range']:.3f}")
    for n in ("rgb", "yolo", "fused_or", "fused_max"):
        print(row(n, rows[n]))
    for n in ("rgb", "fused_or"):
        a = twins[n]["agg"]
        print(f"{n:10s} twin all {a['all']['mean']:.4f}+-{a['all']['half_range']:.4f} "
              f" H {a['H']['mean']:.4f}+-{a['H']['half_range']:.4f}")
    for s in SEEDS:
        d = out["attribution"][s]
        print(f"s{s}: new_cells={d['n_new_cells']} (tp {d['n_new_tp']} / fp {d['n_new_fp']}) "
              f"band={d['new_by_band']} rescued_frames={d['n_rescued_frames']} "
              f"{d['rescued_by_tier']} fa_frames_added={d['n_fa_frames_added']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
