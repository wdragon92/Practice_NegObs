#!/usr/bin/env python3
"""infer_photo.py for the **b2 arm**, with zero edits to the frozen mainrun_0819 tool.

Why this exists: `code/model_factory.py` hard-codes `ENCODER = "resnet34"`, and
`infer_photo.load_model` calls it unconditionally, so `--ckpt .../b2_s4x/best.pt` dies with
`Missing key(s) in state_dict: net.encoder.conv1.weight ...`.  The b2 arm was trained through
`b2_polar/b2_model_factory.py` (MiT-B2 / SegFormer), whose `build()` has the same signature
by design ("Twin of code/model_factory.py").

So the whole fix is: swap the factory module that `infer_photo` already holds a reference to,
then hand argv straight to `infer_photo.main`.  Every other step -- squash resize, ImageNet
normalisation, gridspec, wedge projection, overlay, --json dump -- runs verbatim.

    python3 tools/infer_photo_b2.py --image ... --ckpt .../b2_s42/best.pt --grid ... [same flags]
"""
import os
import sys

CODE = "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code"
B2 = "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/b2_polar"
for p in (CODE, B2, os.path.join(CODE, "labeling")):
    if p not in sys.path:
        sys.path.insert(0, p)

import b2_model_factory  # noqa: E402
import infer_photo  # noqa: E402

infer_photo.model_factory = b2_model_factory

if __name__ == "__main__":
    raise SystemExit(infer_photo.main())
