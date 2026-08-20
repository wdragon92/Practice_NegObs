"""RETIRED (0820, recipe v2) — the oversampler now lives in train_polar.py.

Strict-H oversampling was folded into the main trainer as `--oversample-h K` (train_polar.
make_sampler + train_polar.is_strict_h), so all three models share one code path and one config
record. This file stays only as a compatibility shim for the old flag name:

    python train_oversample.py --oversample-strict-h 4 ...   ==   python train_polar.py --oversample-h 4 ...

Difference vs the 0819 prototype: "strict-H" is now tier=='H' AND the hazard-ON arm AND >=1
GT-positive cell (make_split's own rule), not tier=='H' alone.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import train_polar  # noqa: E402


def build_argparser():
    p = train_polar.build_argparser(desc=__doc__)
    p.add_argument("--oversample-strict-h", type=float, default=4.0,
                   help="DEPRECATED alias of train_polar --oversample-h (1.0 == off)")
    return p


def make_sampler(ds, args):
    """Kept as an importable name; delegates to the folded-in implementation."""
    return train_polar.make_sampler(ds, args)


def main(argv=None):
    parser = build_argparser()
    args = parser.parse_args(argv)
    k = float(args.oversample_strict_h)
    if k > 1.0 and float(args.oversample_h) <= 1.0:   # honour the legacy flag
        argv = list(sys.argv[1:] if argv is None else argv) + ["--oversample-h", str(k)]
        print(f"[oversample] --oversample-strict-h {k:g} -> --oversample-h {k:g} (shim)")
    return train_polar.main(argv, parser=build_argparser())


if __name__ == "__main__":
    sys.exit(main())
