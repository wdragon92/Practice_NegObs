"""SegFormer-B2 arm of the polar hazard-grid run. Thin wrapper over ../code/train_polar.py.

Identical to train_polar.py in every respect (CLI flags, dataset, BCEWithLogitsLoss, AdamW +
linear-decay-to-0 LambdaLR, recipe-v2 selection score `0.5*val_F1 + 0.5*val_H_frame_recall`,
--grid / --hflip / --oversample-h / --bias-init, config.json/metrics.csv/best.pt/last.pt
layout) EXCEPT:
  * the model comes from b2_model_factory.build (local MiT-B2, offline) instead of the
    resnet34-U-Net+aux-head factory;
  * --lr defaults to 6e-5 instead of 3e-4 — the transformer convention carried over from the
    segmentation campaign (HARNESS_NOTES §3: 3e-4 is the smp/U-Net figure; SegFormer runs there
    used the ~6e-5 AdamW transformer default). Override freely with --lr.
  * --route {auto,imgcls,semseg-gap} picks the B2 head route (see b2_model_factory).

VRAM / TIME (HARNESS_NOTES §5, measured RTX 4090 fp32 512^2 batch 8):
    segformer-b2 = 9.71 GB peak, 18.3 s/epoch on sidewalk 800/200 (~2x the U-Net's 9.3 s).
    That 9.71 GB is the 27.37 M semantic-segmentation variant; the default route here is the
    24.20 M classification head (no decode head), so 9.7 GB is a safe upper bound.
    Batch 8 @ 512^2 therefore fits a 24 GB 4090 ALONE with ~14 GB headroom — but it does NOT
    co-exist with a render. Hold the GPU lock; do not run this next to a Blender job.
    Epoch estimate: t_epoch ~ 2 * (N_train/99 + N_val/220) s.

Launch (the CALLER holds the GPU lock; -o is mandatory, HARNESS_NOTES §1):
  flock -o -w 55 -E 201 /tmp/negobs_gpu.lock nice -n 5 \
    env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 \
    /home/vislab/miniconda3/envs/env_seg/bin/python train_b2_polar.py --input rgb \
      --manifest ../dataset_manifest_v1.json --split ../split_v1.json --out RUNDIR
train_polar's own pre-CUDA guard (nvidia-smi free >= 6 GB, exit 202) still applies.

BRIDGE NOTE: train_polar.main() hardcodes cfg["encoder"]="resnet34-unet-aux" in the run's
config.json. We cannot reach that local dict, so this wrapper rewrites the encoder/model/route
keys in <out>/config.json after main() returns (also on exception, via finally). params_m,
n_cells and grid_version in that file are computed from the live model/grid and already correct.

CELL COUNT: train_polar calls `model_factory.build(input, classes=grid.n_cells)`, and the proxy
below forwards `classes` to b2_model_factory, so `--grid gridspec_v1.json` yields a Linear(512,20)
head with no edit here. The prior bias-init reaches it through B2PolarNet.final_classifier().
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, os.pardir, "code"))
for _p in (CODE, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import b2_model_factory  # noqa: E402
import train_polar  # noqa: E402

DEFAULT_LR = 6e-5


class _FactoryProxy:
    """Stands in for the `model_factory` module train_polar looks up by name."""

    def __init__(self, route):
        self.route = route

    def build(self, input_mode, *a, **kw):
        kw.setdefault("force_route", self.route)
        return b2_model_factory.build(input_mode, *a, **kw)


def build_argparser():
    p = train_polar.build_argparser(desc=__doc__)
    p.set_defaults(lr=DEFAULT_LR)
    p.add_argument("--route", choices=["auto", "imgcls", "semseg-gap"], default="auto",
                   help="B2 head route (default auto: imgcls, fall back to semseg-gap)")
    return p


def _fix_config(out_dir, route):
    """Overwrite the resnet34 label train_polar bakes into <out>/config.json."""
    path = os.path.join(out_dir, "config.json")
    try:
        with open(path) as f:
            cfg = json.load(f)
        cfg["encoder"] = "segformer-b2-mit"
        cfg["model_factory"] = "b2_model_factory"
        cfg["b2_route"] = route
        cfg["backbone_ckpt"] = b2_model_factory.LOCAL_MIT_B2
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)
    except FileNotFoundError:
        pass


def main(argv=None):
    parser = build_argparser()
    args = parser.parse_args(argv)                      # peek: need --out and --route
    route = None if args.route == "auto" else args.route
    train_polar.model_factory = _FactoryProxy(route)    # hook swap (train_oversample.py pattern)
    print(f"[b2] model_factory -> b2_model_factory (route={args.route}) lr={args.lr:g}")
    try:
        return train_polar.main(argv, parser=parser)
    finally:
        _fix_config(args.out, args.route)


if __name__ == "__main__":
    sys.exit(main())
