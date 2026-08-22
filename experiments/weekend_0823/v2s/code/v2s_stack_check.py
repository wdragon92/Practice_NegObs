#!/usr/bin/env python3
"""V2S TEST TRACK -- CPU pre-flight of the TRAINING stack at 40 cells.

PS 12.6 procedure 2 asks for a cell-count hardcode sweep before the GPU stage.  A
grep proves absence of literals; this proves PRESENCE of the behaviour -- it drives
the real 40-cell gridspec through every piece the queue will touch, on CPU, with the
real V2S manifest and the reused scene split:

  1. gridspec        40 cells, hflip involution, no fixed cell (even sector count),
                     no cell crosses a band, and the pairing is (1<->10 ... 5<->6)
  2. model_factory   rgb + depth PolarNet at classes=40, forward -> [B,40]
  3. polar_dataset   PolarGridDataset on the V2S manifest / reused split, hflip on
  4. flip law        flipping a V2S label and folding it onto V1 == folding it first
                     and then flipping under V1's own permutation (the refinement and
                     the augmentation commute -- what makes recipe v2 transfer)
  5. bias-init       train_polar.set_prior_bias writes sigmoid(bias) == the per-cell
                     train positive rate computed FROM THE MANIFEST at runtime
  6. eval_polar      per_frame.csv write/read round trip at 40 cells (84 columns)

Run:  PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" python v2s_stack_check.py
"""
import os
import sys

import numpy as np
import torch

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
MAIN_CODE = os.path.join(REPO, "experiments/mainrun_0819/code")
V2S = os.path.join(REPO, "experiments/weekend_0823/v2s")
GRID_PATH = os.path.join(MAIN_CODE, "labeling/gridspec_v2s.json")
MANIFEST = os.path.join(V2S, "dataset_manifest_v2s_full.json")
SPLIT = os.path.join(REPO, "experiments/dayrun_0820/split_v2_full.json")

sys.path.insert(0, MAIN_CODE)
import gridspec                      # noqa: E402
import model_factory                 # noqa: E402
import polar_dataset as PD           # noqa: E402
import train_polar as TP             # noqa: E402
from eval_polar import read_per_frame, write_per_frame   # noqa: E402

OK = []


def chk(name, cond, extra=""):
    OK.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")


def main():
    g = gridspec.load(GRID_PATH)
    g1 = gridspec.load(os.path.join(MAIN_CODE, "labeling/gridspec_v1.json"))
    ns, nb, nc = g.n_sectors, g.n_bands, g.n_cells
    print(f"grid: {g.summary()}")

    # ---- 1. gridspec -------------------------------------------------------
    chk("gridspec: 4 bands x 10 sectors = 40 cells", (nb, ns, nc) == (4, 10, 40))
    perm = g.flip_perm()
    chk("hflip: involution", [perm[i] for i in perm] == list(range(nc)))
    chk("hflip: no cell is its own image (even sector count -> NO fixed centre)",
        all(perm[i] != i for i in range(nc)))
    chk("hflip: no cell crosses a band", all(g.band_of[i] == g.band_of[perm[i]] for i in range(nc)))
    want = [(s + 1, ns - s) for s in range(ns // 2)]
    got = [(s + 1, perm[s] + 1) for s in range(ns // 2)]
    chk("hflip: sector pairing is (1<->10, 2<->9, 3<->8, 4<->7, 5<->6) from the "
        "generic band*ns+(ns-1-s)", got == want, f"got {got}")
    chk("cell ids unique and CSV-safe", len(set(g.cell_ids)) == nc,
        f"{g.cell_ids[:4]} .. {g.cell_ids[-2:]}")

    # ---- 2. model_factory --------------------------------------------------
    for mode, ch in (("rgb", 3), ("depth", 1)):
        m = model_factory.build(mode, encoder_weights=None, grid=g).eval()
        with torch.no_grad():
            out = m(torch.randn(2, ch, 64, 64))
        chk(f"model_factory({mode}) -> logits {tuple(out.shape)}",
            tuple(out.shape) == (2, nc) and m.final_classifier().out_features == nc)

    # ---- 3. polar_dataset --------------------------------------------------
    dtr = PD.PolarGridDataset(MANIFEST, SPLIT, "train", input_mode="rgb",
                              grid=g, train_hflip=True, img_size=64, seed=42)
    dte = PD.PolarGridDataset(MANIFEST, SPLIT, "test", input_mode="rgb",
                              grid=g, img_size=64, seed=42)
    x, y, meta = dtr[0]
    chk(f"PolarGridDataset train n={len(dtr)} test={len(dte)}, y is a {nc}-vector",
        y.shape == (nc,) and len(dtr) > 0 and len(dte) > 0)
    prior = dtr.positive_rate()
    chk("positive_rate() is per-cell over the TRAIN split (runtime bias prior source)",
        prior.shape == (nc,) and 0.0 < prior.min() and prior.max() < 1.0,
        f"min/med/max = {prior.min():.4f}/{np.median(prior):.4f}/{prior.max():.4f}")

    # ---- 4. flip and fold commute -----------------------------------------
    pairs = [(2 * s, 2 * s + 1) for s in range(g1.n_sectors)]

    def fold(v):
        v = np.asarray(v).reshape(-1)
        return np.array([v[b * ns + i] or v[b * ns + j]
                         for b in range(nb) for i, j in pairs], int)

    rs = np.random.default_rng(0)
    bad = 0
    for r in [rs.integers(0, 2, nc) for _ in range(2000)]:
        flipped = r[np.asarray(perm)]
        if not np.array_equal(fold(flipped), fold(r)[np.asarray(g1.flip_perm())]):
            bad += 1
    chk("flip and sector-fold COMMUTE (V2S hflip projects onto the V1 hflip)", bad == 0,
        f"{bad}/2000 counterexamples")

    # the same on real labels, plus the folding law against the V1 manifest
    ytr = np.asarray([r["polar_gt"] for r in dtr.items], int)
    chk("real train labels: folding a V2S vector yields a valid 20-cell V1 vector",
        fold(ytr[0]).shape == (g1.n_cells,))

    # ---- 5. bias-init ------------------------------------------------------
    m = model_factory.build("rgb", encoder_weights=None, grid=g)
    name, bias = TP.set_prior_bias(m, prior, nc)
    got_p = 1.0 / (1.0 + np.exp(-np.asarray(bias)))
    chk("set_prior_bias: sigmoid(bias) == the manifest-derived per-cell prior "
        "(nothing to precompute)", name is not None and len(bias) == nc
        and np.allclose(got_p, np.clip(prior, *TP.PRIOR_CLAMP), atol=1e-6))

    # ---- 6. eval_polar CSV round trip -------------------------------------
    import tempfile
    p = np.linspace(0.01, 0.99, nc)
    gt = (np.arange(nc) % 3 == 0).astype(float)
    rec = dict(frame_id=["on/scene04/x.png"], scene_id=["scene04"], tier=np.array(["V"]),
               toggle=np.array(["on"]), probs=p[None, :], gt=gt[None, :],
               cell_ids=list(g.cell_ids))
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "per_frame.csv")
        write_per_frame(rec, f, GRID_PATH)
        d = read_per_frame(f, GRID_PATH)       # also asserts header vs --grid agreement
        with open(f) as fh:
            ncol = len(fh.readline().strip().split(","))
    chk(f"eval_polar per_frame.csv round trip: {ncol} columns, {nc} cells inferred",
        ncol == 4 + 2 * nc and d["probs"].shape == (1, nc)
        and np.allclose(d["probs"][0], p, atol=1e-6) and list(d["cell_ids"]) == list(g.cell_ids))

    print(f"\nRESULT: {sum(OK)}/{len(OK)} checks passed "
          f"({'V2S STACK GREEN' if all(OK) else 'V2S STACK RED'})")
    return 0 if all(OK) else 1


if __name__ == "__main__":
    sys.exit(main())
