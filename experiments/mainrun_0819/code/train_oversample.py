"""RESERVE — DO NOT RUN TONIGHT unless the strict-H recall in the first table is unusable.

Identical to train_polar.py except that frames with tier=="H" are drawn --oversample-strict-h times
more often, via a WeightedRandomSampler over the train subset (epoch length is kept equal to the
un-oversampled train set so that "epoch" stays comparable across arms).

  python train_oversample.py --input rgb --oversample-strict-h 4 ... (same flags as train_polar)

Reserve status: only the import + sampler self-check below has been executed.
"""
from __future__ import annotations

import os
import sys

import torch
from torch.utils.data import WeightedRandomSampler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import train_polar  # noqa: E402


def build_argparser():
    p = train_polar.build_argparser(desc=__doc__)
    p.add_argument("--oversample-strict-h", type=float, default=4.0,
                   help="weight multiplier for tier=='H' train frames (1.0 == off)")
    return p


def make_sampler(ds, args):
    k = float(getattr(args, "oversample_strict_h", 1.0))
    if k <= 1.0:
        return None
    w = [k if (r.get("tier") == "H") else 1.0 for r in ds.items]
    n_h = sum(1 for x in w if x > 1.0)
    print(f"[oversample] tier-H frames {n_h}/{len(w)} weighted x{k}")
    return WeightedRandomSampler(torch.as_tensor(w, dtype=torch.double), num_samples=len(w),
                                 replacement=True)


def main(argv=None):
    train_polar.make_sampler = make_sampler       # hook swap; train_polar calls it by module lookup
    return train_polar.main(argv, parser=build_argparser())


if __name__ == "__main__":
    sys.exit(main())
