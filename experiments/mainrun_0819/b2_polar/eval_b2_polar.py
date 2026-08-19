"""Evaluate a SegFormer-B2 polar checkpoint. Thin wrapper over ../code/eval_polar.py.

NOT in the original dry-run brief — added because ../code/eval_polar.py:39 does
`model_factory.build(input_mode, encoder_weights=None)` and then load_state_dict(), so pointing
it at a B2 best.pt would build a resnet34 U-Net and blow up on the key mismatch. Same one-line
hook swap as train_b2_polar.py; every flag, metric, bootstrap CI and output file is unchanged.

  CUDA_VISIBLE_DEVICES="" PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 \
    python eval_b2_polar.py --ckpt RUNDIR/best.pt --manifest ../dataset_manifest_v1.json \
      --split ../split_v1.json --input rgb --out EVALDIR

--route mirrors train_b2_polar.py; use the same value the run's config.json records in b2_route.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, os.pardir, "code"))
for _p in (CODE, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import eval_polar  # noqa: E402
from train_b2_polar import _FactoryProxy  # noqa: E402


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    route = None
    if "--route" in argv:
        i = argv.index("--route")
        route = argv[i + 1]
        del argv[i:i + 2]
        route = None if route == "auto" else route
    eval_polar.model_factory = _FactoryProxy(route)
    print(f"[b2] eval model_factory -> b2_model_factory (route={route or 'auto'})")
    return eval_polar.main(argv)


if __name__ == "__main__":
    sys.exit(main())
