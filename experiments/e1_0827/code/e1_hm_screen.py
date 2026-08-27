# -*- coding: utf-8 -*-
"""e1_hm_screen.py -- REPORT-ONLY screening: does a scene's heightmap contain a
hazard-like break line AT ALL?

Camera-free on purpose. It runs only stages 1, 3 and 4 of route (a)
(walkable / drop / local break) over every scene's `heightmap.npy`; there is no
frame, no projection, no visibility test, no record and no label. That keeps it
outside the Phase 0 "smoke on at most 3 frames" limit (brief §3-P3) while still
answering the question ❓B-1 needs answering: which scenes are invisible to
route (a) because the AABB envelope filled their opening in.

    python3 e1_hm_screen.py --round 260819_main_on
"""

import argparse
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e1_camera as CAM      # noqa: E402
import e1_const as C         # noqa: E402
import e1_data as D          # noqa: E402
import e1_geometry as G      # noqa: E402


def screen(round_name):
    root = D.round_dir(round_name)
    rows = []
    for split in ("train", "val", "test"):
        for sdir in sorted(glob.glob(os.path.join(root, split, "*"))):
            if not os.path.exists(os.path.join(sdir, "heightmap.npy")):
                continue
            hm = CAM.HeightMap.load(sdir)
            walk, _ = G.walkable_mask(hm)
            drop = G.drop_map(hm)
            fall = G.local_fall(hm)
            brk = (walk & np.isfinite(drop) & (drop >= C.DROP_MIN_M)
                   & (fall >= C.BREAK_LOCAL_FALL_M))
            rows.append({
                "scene": os.path.basename(sdir), "split": split,
                "break_cells": int(brk.sum()),
                "z_min": float(np.nanmin(hm.z)), "z_max": float(np.nanmax(hm.z)),
                "n_depth": len(glob.glob(os.path.join(sdir, "*.depth.npy"))),
                "n_idseg": len(glob.glob(os.path.join(sdir, "*.idseg.npz"))),
            })
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    a = ap.parse_args(argv)
    rows = screen(a.round)
    print("%-10s %-5s %11s %8s %8s %6s %6s"
          % ("scene", "split", "break_cells", "z_min", "z_max", "depth", "idseg"))
    for r in rows:
        print("%-10s %-5s %11d %8.3f %8.3f %6d %6d"
              % (r["scene"], r["split"], r["break_cells"], r["z_min"], r["z_max"],
                 r["n_depth"], r["n_idseg"]))
    zero = [r["scene"] for r in rows if r["break_cells"] == 0]
    print("scenes with 0 break cells: %d / %d  %s" % (len(zero), len(rows), zero))
    print("NOTE: a nonzero count does NOT mean route (a) will see a hazard -- the "
          "cells may sit on roofs/planters unreachable from the ground. Run "
          "e1_run.py on a frame for that.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
