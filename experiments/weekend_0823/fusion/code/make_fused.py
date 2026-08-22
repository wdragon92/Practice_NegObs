#!/usr/bin/env python3
"""GPU-3 / WEEKEND_BRIEF_0823 §6.4 — build the YOLO-union-U-Net fused per_frame.csv.

NO RETRAINING, NO GPU. Reads two *stored* per_frame.csv files per seed and writes a third.

INPUTS (per seed S in {42,43,44}) — both on the same 816-frame v2 test set, same
PROVISIONAL-GRID-V1 20 cells, same labels, same frame order (asserted here):
  A) U-Net RGB grid probabilities
     experiments/dayrun_0820/runs/v2/rgb_s<S>/eval_test/per_frame.csv       operating tau_u = 0.50
  B) YOLOv8n det2cell output, detector confidence used as the cell probability
     experiments/dayrun_0820/runs/yolo_s<S>/cells_test/per_frame.csv        operating tau_y = 0.25

DECISION RULE (this is the definition of the fused row; brief §6.4 "cell-level OR"):

     cell c of frame f FIRES  <=>  p_unet(f,c) >= 0.50   OR   p_yolo(f,c) >= 0.25

Each source keeps its own approved operating threshold (approval #1: tau_op = 0.5 for the
U-Net rows, tau = 0.25 for the detector row). The fused row therefore introduces no new
threshold and does no test-set fitting.

HOW A SINGLE-TAU EVALUATOR IS MADE TO REPRODUCE THAT RULE EXACTLY.
`eval_polar.bundle` and `twin_analysis` take one scalar tau for the whole probability matrix,
so the per-source thresholds are folded into a strictly-increasing rescale of the YOLO score
onto the U-Net threshold scale:

     phi(q) = 2*q                        for 0 <= q <  0.25      -> [0, 0.5)
            = 0.5 + (q - 0.25) * (2/3)   for 0.25 <= q <= 1      -> [0.5, 1]

phi is continuous and strictly increasing with phi(0.25) = 0.5 and phi(1.0) = 1.0, so

     max(p_unet, phi(p_yolo)) >= 0.5   <=>   p_unet >= 0.5  OR  p_yolo >= 0.25

i.e. thresholding the fused CSV at tau = 0.5 IS the OR rule above, cell for cell, with no
approximation. phi only relabels the YOLO axis; it changes no ordering and no decision.

TWO CSVs ARE WRITTEN PER SEED because the two uses want different things:
  fused_or/per_frame.csv   p = max(p_unet, phi(p_yolo))  -> HEADLINE. All thresholded metrics
                           (V/E/H frame recall, FA, cell F1/recall/precision, per-band) are the
                           OR rule exactly. Twin delta on this CSV is on the rescaled axis.
  fused_max/per_frame.csv  p = max(p_unet, p_yolo)       -> the literal "max" of brief §6.4,
                           kept as a twin-delta sensitivity check on the raw score axis.
                           Do NOT threshold this one at 0.5: that would silently demote the
                           detector's operating point from 0.25 to 0.5.

Run with PYTHONNOUSERSITE=1 in env_seg.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
import gridspec  # noqa: E402
from eval_polar import read_per_frame, write_per_frame  # noqa: E402

TAU_U, TAU_Y = 0.50, 0.25


def phi(q):
    """Strictly-increasing rescale of the YOLO confidence onto the U-Net threshold axis."""
    q = np.asarray(q, float)
    return np.where(q < TAU_Y, q * (TAU_U / TAU_Y),
                    TAU_U + (q - TAU_Y) * ((1.0 - TAU_U) / (1.0 - TAU_Y)))


def check_phi():
    q = np.linspace(0, 1, 100001)
    p = phi(q)
    assert np.all(np.diff(p) > -1e-15), "phi is not monotone"
    assert abs(float(phi(TAU_Y))) - TAU_U < 1e-12
    assert abs(float(phi(1.0)) - 1.0) < 1e-12
    assert abs(float(phi(0.0)) - 0.0) < 1e-12
    # the equivalence the whole file rests on, checked on a dense grid
    assert np.array_equal(p >= TAU_U, q >= TAU_Y), "phi does not preserve the OR threshold"
    return True


def load_pair(seed, root=ROOT, grid=None):
    a = os.path.join(root, f"experiments/dayrun_0820/runs/v2/rgb_s{seed}/eval_test/per_frame.csv")
    b = os.path.join(root, f"experiments/dayrun_0820/runs/yolo_s{seed}/cells_test/per_frame.csv")
    du, dy = read_per_frame(a, grid), read_per_frame(b, grid)
    # the fusion is only defined if the two files describe the SAME frames in the SAME order
    assert du["frame_id"] == dy["frame_id"], "frame_id order differs between the two sources"
    assert du["cell_ids"] == dy["cell_ids"], "cell id order differs between the two sources"
    assert np.array_equal(du["gt"] > 0.5, dy["gt"] > 0.5), "GT differs between the two sources"
    assert np.array_equal(du["tier"], dy["tier"]) and np.array_equal(du["toggle"], dy["toggle"])
    return du, dy, a, b


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--grid", default="gridspec_v1.json")
    p.add_argument("--out-root", default=os.path.join(ROOT, "experiments/weekend_0823/fusion"))
    a = p.parse_args(argv)
    check_phi()
    grid = gridspec.load(a.grid)
    prov = {}
    for s in [int(x) for x in a.seeds.split(",")]:
        du, dy, pa, pb = load_pair(s, grid=grid)
        pu, py = du["probs"], dy["probs"]
        d_or = dict(du, probs=np.maximum(pu, phi(py)))
        d_mx = dict(du, probs=np.maximum(pu, py))
        for tag, d in (("fused_or", d_or), ("fused_max", d_mx)):
            o = os.path.join(a.out_root, f"s{s}", tag)
            os.makedirs(o, exist_ok=True)
            write_per_frame(d, os.path.join(o, "per_frame.csv"), grid)
        # the identity that makes the fused_or CSV legitimate, re-verified on the real data
        fired_or = (pu >= TAU_U) | (py >= TAU_Y)
        fired_csv = d_or["probs"] >= TAU_U
        assert np.array_equal(fired_or, fired_csv), f"seed {s}: fused_or CSV != OR rule"
        n_u, n_y = int((pu >= TAU_U).sum()), int((py >= TAU_Y).sum())
        n_new = int((fired_or & ~(pu >= TAU_U)).sum())
        prov[s] = dict(unet_csv=pa, yolo_csv=pb, n_frames=len(du["frame_id"]),
                       n_cells=grid.n_cells, cells_fired_unet=n_u, cells_fired_yolo=n_y,
                       cells_fired_fused=int(fired_or.sum()), cells_added_by_yolo=n_new)
        print(f"[fuse s{s}] frames={len(du['frame_id'])} unet_cells={n_u} yolo_cells={n_y} "
              f"fused={int(fired_or.sum())} added_by_yolo={n_new}")
    with open(os.path.join(a.out_root, "FUSION_PROVENANCE.json"), "w") as f:
        json.dump(dict(rule="p_unet>=0.50 OR p_yolo>=0.25", tau_u=TAU_U, tau_y=TAU_Y,
                       phi="2q for q<0.25 ; 0.5+(q-0.25)*2/3 for q>=0.25",
                       grid=grid.version, per_seed=prov), f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
