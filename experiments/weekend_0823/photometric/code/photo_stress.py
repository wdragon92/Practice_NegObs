#!/usr/bin/env python3
"""GPU-4 / WEEKEND_BRIEF_0823 §6.6 — photometric stress of the frozen RGB U-Nets. EVAL ONLY.

WHAT THIS IS. Zero-shot lighting-robustness curves for the three frozen RGB checkpoints
`experiments/dayrun_0820/runs/v2/rgb_s{42,43,44}/best.pt`. Nothing is trained, nothing is
selected, nothing is tuned. The image is perturbed at load time, the frozen network runs, and
the standard `eval_polar` metrics are computed on the result.

WHY. Approval #5 kept the main table augmentation-free and folded lighting sensitivity in as an
evaluation-only track; the pilot-shoot package (brief §6.8, approval #6) needs prior information
on how much the sim-trained model degrades under a lighting change before anyone photographs
anything.

*** SPLIT DISCIPLINE — THE HARD RULE OF THIS FILE ***
The subset is **val** (`split_v2_full.json` -> ["scene08", "scene20", "sceneD3"], 288 frames,
144 hazard-on / 144 off). **test is never touched here.** Brief §3-1 makes the 7 test scenes
inviolable for anything but a final evaluation read; a robustness sweep is a diagnostic and
therefore belongs on val. Every number this file produces is a *val* number and must be labelled
as such wherever it is quoted.

PERTURBATIONS. Let I be the frame after the training pipeline's own resize to 512x512
(`polar_dataset.PolarGridDataset._load_x`, squash, BILINEAR), expressed as float in [0,1] by
dividing the uint8 array by 255. The perturbation is applied to I, *before* the ImageNet
normalisation, which is exactly the slot `_apply_photometric` occupies during training. All three
families are deterministic (no RNG) and identity-preserving at their neutral parameter.

  identity          P(I) = I                                             (the anchor point)

  brightness b      P(I) = clip(b * I, 0, 1)                b in {0.6, 0.8, 1.2, 1.4}
                    A linear gain in the sRGB-encoded domain. This is exactly
                    PIL.ImageEnhance.Brightness(img).enhance(b), which blends the image with a
                    black image: out = I*b + 0*(1-b). Verified against PIL in --self-check.
                    Highlights CLIP at b > 1: that is the real behaviour of a gained sensor and
                    is kept, not avoided.

  gamma g           P(I) = I ** g                            g in {0.7, 1.4}
                    Pure tone-curve change, no clipping possible on [0,1]. g < 1 lifts midtones
                    (a brighter-looking image with highlights intact), g > 1 crushes them.

  exposure ev       P(I) = lin2srgb( clip( srgb2lin(I) * 2**ev, 0, 1 ) )   ev in {-1,-0.5,+0.5,+1}
                    A stop-based exposure change applied in LINEAR light, which is what changing
                    a camera's exposure physically does — unlike `brightness`, which scales the
                    already-encoded values. The two therefore differ by the sRGB transfer curve
                    and are reported as separate families on purpose.
                      srgb2lin(c) = c/12.92                       if c <= 0.04045
                                  = ((c + 0.055)/1.055) ** 2.4    otherwise
                      lin2srgb(l) = 12.92*l                       if l <= 0.0031308
                                  = 1.055 * l**(1/2.4) - 0.055    otherwise

OUTPUT. For each (seed, variant): `runs/s<seed>/<variant>/per_frame.csv` in the exact
`eval_polar.write_per_frame` format, so `eval_polar.py --per-frame-a` scores it with the same
code path as every row of the main table.

GATE. `--self-check` (no GPU) proves phi-free identity: the perturbation functions return the
input bit-for-bit at their neutral parameter, and `brightness` matches PIL. In the run itself the
`identity` variant is compared against the checkpoint's own stored val predictions
(`runs/v2/rgb_s<seed>/eval_test/per_frame_val.csv`) — if the identity pass does not reproduce
those probabilities the whole sweep is invalid and the run aborts.

Run with PYTHONNOUSERSITE=1 in env_seg, under the GPU lock.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
MAIN = os.path.join(ROOT, "experiments/mainrun_0819/code")
sys.path.insert(0, MAIN)
import gridspec  # noqa: E402
import model_factory  # noqa: E402
from eval_polar import read_per_frame, write_per_frame  # noqa: E402
from polar_dataset import IMAGENET_MEAN, IMAGENET_STD, PolarGridDataset  # noqa: E402
from train_polar import guard_gpu_free  # noqa: E402

S_A, S_B, S_C, S_D = 0.04045, 12.92, 0.055, 1.055
L_THR = 0.0031308


def srgb2lin(c):
    return np.where(c <= S_A, c / S_B, ((c + S_C) / S_D) ** 2.4)


def lin2srgb(l):
    return np.where(l <= L_THR, l * S_B, S_D * np.power(np.maximum(l, 0.0), 1 / 2.4) - S_C)


def perturb(a, kind, p):
    """a: float32 [H,W,3] in [0,1]. Returns the perturbed array, same shape/dtype/range."""
    if kind == "identity":
        return a
    if kind == "brightness":
        return np.clip(a * p, 0.0, 1.0)
    if kind == "gamma":
        return np.power(a, p)
    if kind == "exposure":
        return np.clip(lin2srgb(np.clip(srgb2lin(a.astype(np.float64)) * (2.0 ** p), 0.0, 1.0)),
                       0.0, 1.0).astype(np.float32)
    raise ValueError(kind)


# variant name -> (family, parameter).  Order = the order they appear in the report.
VARIANTS = [("identity", "identity", 0.0)]
VARIANTS += [(f"bright_{p:g}", "brightness", p) for p in (0.6, 0.8, 1.2, 1.4)]
VARIANTS += [(f"gamma_{p:g}", "gamma", p) for p in (0.7, 1.4)]
VARIANTS += [(f"exp_{p:+g}", "exposure", p) for p in (-1.0, -0.5, 0.5, 1.0)]


class PhotoDataset(PolarGridDataset):
    """PolarGridDataset with one deterministic photometric perturbation spliced into _load_x.

    Everything else — squash resize, BILINEAR, ImageNet normalisation, label handling — is the
    parent's, unchanged, so `identity` must reproduce the training run's own val inference.
    """

    def __init__(self, *a, kind="identity", param=0.0, **kw):
        super().__init__(*a, **kw)
        self.kind, self.param = kind, float(param)

    def _load_x(self, rec, idx):
        assert self.input_mode == "rgb", "photometric stress is an RGB-arm track only"
        S = self.img_size
        img = Image.open(rec["rgb"]).convert("RGB").resize((S, S), Image.BILINEAR)
        a = np.asarray(img, np.float32) / 255.0
        a = perturb(a, self.kind, self.param)
        a = (a - np.array(IMAGENET_MEAN, np.float32)) / np.array(IMAGENET_STD, np.float32)
        return torch.from_numpy(np.ascontiguousarray(a.transpose(2, 0, 1).astype(np.float32)))


def self_check():
    rng = np.random.default_rng(0)
    a = rng.random((37, 41, 3), dtype=np.float32)
    assert np.array_equal(perturb(a, "identity", 0.0), a)
    assert np.array_equal(perturb(a, "brightness", 1.0), np.clip(a, 0, 1))
    assert np.allclose(perturb(a, "gamma", 1.0), a, atol=1e-6)
    assert np.allclose(perturb(a, "exposure", 0.0), a, atol=2e-6), \
        float(np.abs(perturb(a, "exposure", 0.0) - a).max())
    # brightness == PIL ImageEnhance.Brightness, to within uint8 quantisation
    from PIL import ImageEnhance
    u = (a * 255).astype(np.uint8)
    for b in (0.6, 0.8, 1.2, 1.4):
        ref = np.asarray(ImageEnhance.Brightness(Image.fromarray(u)).enhance(b), np.float32) / 255
        ours = perturb(u.astype(np.float32) / 255, "brightness", b)
        assert np.abs(ref - ours).max() <= 1.5 / 255, (b, float(np.abs(ref - ours).max()))
    # exposure round-trips: +1 EV then -1 EV recovers the un-clipped part
    x = np.clip(a * 0.4, 0, 1).astype(np.float32)
    assert np.allclose(perturb(perturb(x, "exposure", 1.0), "exposure", -1.0), x, atol=3e-3)
    print("[self-check] all perturbation identities hold")
    return 0


@torch.no_grad()
def run_seed(seed, args, grid, device):
    ckpt = os.path.join(ROOT, f"experiments/dayrun_0820/runs/v2/rgb_s{seed}/best.pt")
    model = model_factory.build("rgb", encoder_weights=None, classes=grid.n_cells).to(device)
    ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    if isinstance(ck, dict) and ck.get("n_cells") not in (None, grid.n_cells):
        raise SystemExit(f"[fatal] ckpt has {ck['n_cells']} cells, grid has {grid.n_cells}")
    model.load_state_dict(ck["state_dict"] if "state_dict" in ck else ck)
    model.eval()

    for name, kind, param in VARIANTS:
        out = os.path.join(args.out_root, f"s{seed}", name)
        os.makedirs(out, exist_ok=True)
        pf = os.path.join(out, "per_frame.csv")
        if os.path.exists(pf) and not args.force:
            print(f"[skip] s{seed}/{name} already present")
            continue
        ds = PhotoDataset(args.manifest, args.split, args.subset, "rgb", train_aug=False,
                          grid=grid, kind=kind, param=param)
        dl = DataLoader(ds, batch_size=args.batch, shuffle=False, num_workers=args.workers,
                        pin_memory=(device.type == "cuda"))
        fid, sid, tier, tog, P, G = [], [], [], [], [], []
        for x, y, m in dl:
            P.append(torch.sigmoid(model(x.to(device))).cpu().numpy())
            G.append(y.numpy())
            fid += list(m["frame_id"]); sid += list(m["scene_id"])
            tier += list(m["tier"]); tog += list(m["toggle_state"])
        d = dict(frame_id=fid, scene_id=sid, tier=np.array(tier), toggle=np.array(tog),
                 probs=np.concatenate(P).astype(np.float64),
                 gt=np.concatenate(G).astype(np.float64), cell_ids=list(grid.cell_ids))
        write_per_frame(d, pf, grid)
        print(f"[run ] s{seed}/{name:12s} n={len(fid)} -> {pf}")

        if name == "identity":
            ref = os.path.join(ROOT, f"experiments/dayrun_0820/runs/v2/rgb_s{seed}"
                                     "/eval_test/per_frame_val.csv")
            if os.path.exists(ref):
                r = read_per_frame(ref, grid)
                assert r["frame_id"] == d["frame_id"], "identity gate: val frame order differs"
                e = float(np.abs(r["probs"] - d["probs"]).max())
                print(f"[gate] s{seed} identity vs stored val predictions: max|dp| = {e:.2e}")
                if e > 1e-3:
                    raise SystemExit(f"[fatal] identity pass does not reproduce the frozen "
                                     f"checkpoint's stored val output (max|dp| {e:.2e}) — the "
                                     f"sweep would be measuring the harness, not the lighting")
            else:
                print(f"[warn] no stored val reference for s{seed}; identity gate skipped")
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-check", action="store_true")
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--subset", default="val", choices=["val"],
                   help="val ONLY — test is inviolable (brief §3-1); the choice list enforces it")
    p.add_argument("--manifest", default=os.path.join(ROOT, "experiments/dayrun_0820/"
                                                            "dataset_manifest_v2_full.json"))
    p.add_argument("--split", default=os.path.join(ROOT, "experiments/dayrun_0820/"
                                                         "split_v2_full.json"))
    p.add_argument("--grid", default="gridspec_v1.json")
    p.add_argument("--out-root", default=os.path.join(ROOT, "experiments/weekend_0823/"
                                                            "photometric/runs"))
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--force", action="store_true")
    a = p.parse_args(argv)
    if a.self_check:
        return self_check()
    self_check()
    grid = gridspec.load(a.grid)
    dev = torch.device(guard_gpu_free())
    if dev.type == "cuda" and not torch.cuda.is_available():
        dev = torch.device("cpu")
    print(f"[grid] {grid.summary()} · device {dev} · subset {a.subset} · "
          f"{len(VARIANTS)} variants")
    with open(os.path.join(a.out_root, "VARIANTS.json"), "w") as f:
        json.dump([dict(name=n, family=k, param=v) for n, k, v in VARIANTS], f, indent=2)
    for s in [int(x) for x in a.seeds.split(",")]:
        run_seed(s, a, grid, dev)
    return 0


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "experiments/weekend_0823/photometric/runs"), exist_ok=True)
    sys.exit(main())
