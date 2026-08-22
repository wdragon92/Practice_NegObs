#!/usr/bin/env python3
"""Quantify the gz_drop3 occlusion-leak check (capture_plan.md §4).

`cmp` answers byte-identical / not.  A renderer is allowed to be non-deterministic, so a
byte difference alone does not prove a geometry leak.  This adds the discriminator: the
SAME-world frame-to-frame noise floor (frame 000 vs 001 of one camera in one world) is
measured first, and the hazard-vs-ctrl difference is read against it.

    python3 tools/leak_check.py [world_stem]     default gz_drop3
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWS = ["extra_h0.3_d1.2", "preset_h0.3_d2", "preset_h0.3_d5", "preset_h0.3_d10",
         "preset_h0.9_d2", "preset_h0.9_d5", "preset_h0.9_d10",
         "rs_h0.125_d2", "rs_h0.125_d5"]


def load(w, v, i=0):
    p = os.path.join(HERE, "frames", w, f"{w}_cap_{v}_{i:03d}.png")
    return np.asarray(Image.open(p)).astype(np.int16)


def stats(a, b):
    d = np.abs(a - b)
    m = d.max(axis=2)
    return dict(maxabs=int(d.max()), npx=int((m > 0).sum()), npx8=int((m > 8).sum()),
                frac=float((m > 0).mean()))


def main():
    w = sys.argv[1] if len(sys.argv) > 1 else "gz_drop3"
    print(f"{'view':<20} {'H-vs-C maxΔ':>11} {'#px>0':>10} {'#px>8':>9} "
          f"{'noise maxΔ':>10} {'noise#px>0':>11}  verdict")
    for v in VIEWS:
        h, c = load(w, v), load(f"{w}_ctrl", v)
        s = stats(h, c)
        n = stats(h, load(w, v, 1))            # same world, next frame = noise floor
        if s["npx"] == 0:
            verd = "identical"
        elif s["npx8"] <= n["npx8"] and s["maxabs"] <= max(n["maxabs"], 8):
            verd = "within noise floor"
        else:
            verd = "LEAK SUSPECT"
        print(f"{v:<20} {s['maxabs']:>11} {s['npx']:>10} {s['npx8']:>9} "
              f"{n['maxabs']:>10} {n['npx']:>11}  {verd}")


if __name__ == "__main__":
    main()
