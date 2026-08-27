# -*- coding: utf-8 -*-
"""p0_edge_distance.py -- Phase-0 REPORT-ONLY geometry probe for pilot-scene choice.

What it measures, and nothing else:
  * "edge-candidate cells" of a scene, straight from the rendered heightmap
    sidecar: cells whose walkable surface falls by at least DROP_MIN_M inside a
    run distance of R_RUN_M (brief v6 §2 rule 1).
  * for every camera stored in that scene's `variation.json`, the 3-D distance
    from the camera eye to the NEAREST edge-candidate cell.

What it deliberately does NOT do (brief v6 §3-P3, Phase 0):
  * it writes no label record, no polyline, no mask, no tier;
  * it does not project anything into the image and runs no visibility test;
  * it adopts no threshold -- every number it prints is a distribution for §9.

Constants: imported from `e1_const.py` (the cycle's single source of truth).
This file spells no decision-affecting numeric literal of its own; the two
structural literals it does use (a 3x3 neighbourhood, and the +1 that turns a
radius in metres into a radius in cells) are documented at their use site.

No import of labeler.py, of any polar-grid code, or of any old tier logic.

usage:
  python3 experiments/e1_0827/code/p0_edge_distance.py \
      --round 260819_main_on --split val --scene scene01
  python3 experiments/e1_0827/code/p0_edge_distance.py --plan <plan.json> --out <out.json>
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import e1_const as K                      # noqa: E402  (path set above)
import variation_kit as vk                # noqa: E402  round_dir ONLY -- see below


# --------------------------------------------------------------------------- #
# heightmap -> edge-candidate cells
# --------------------------------------------------------------------------- #
def _sliding_min(z, r):
    """Minimum of `z` over a (2r+1) square window, NaN-safe, separable.

    Two 1-D passes (x then y) instead of one (2r+1)^2 stack: the square window
    is separable under `min`, and 2*(2r+1) shifts beat (2r+1)^2 by ~40x at r=20.
    NaN (the sidecar's `nodata`) is neutralised with +inf so it never wins a
    minimum, and restored afterwards only where the input itself was NaN.
    """
    a = np.where(np.isfinite(z), z, np.inf)
    for axis in (1, 0):
        acc = a.copy()
        for k in range(1, r + 1):
            acc = np.minimum(acc, np.roll(a, k, axis=axis))
            acc = np.minimum(acc, np.roll(a, -k, axis=axis))
        a = acc
    return a


def edge_cells(z, step, drop_min, r_run):
    """Boolean mask of edge-candidate cells + the two drop fields it is built from.

    edge cell  <=>  drop_R >= drop_min  AND  drop_1 > 0
      drop_R = z - min(z) over a square window of radius `r_run` metres
               ("the walkable surface falls by drop_min inside the run distance")
      drop_1 = z - min(z) over the 8-neighbourhood
               (keeps only the crest cell on the UPPER side of the break, so a
                flat tread 0.9 m back from a nosing does not also become "edge"
                unless it too has a step down beside it)

    The window is a square in cell space, i.e. a Chebyshev ball -- it reaches
    r_run*sqrt(2) diagonally. Recorded as a [방법] approximation of the disc.
    """
    r_cells = int(np.ceil(r_run / step))          # +ceil: never under-reach
    drop_R = z - _sliding_min(z, r_cells)
    drop_1 = z - _sliding_min(z, 1)               # 1 == the 8-neighbourhood
    mask = np.isfinite(z) & (drop_R >= drop_min) & (drop_1 > 0.0)
    return mask, drop_R, drop_1


def cell_xyz(mask, meta):
    """World (x, y, z) of every True cell.  `order` is z[y_idx, x_idx]."""
    iy, ix = np.nonzero(mask)
    x = meta["x0"] + ix * meta["step"]
    y = meta["y0"] + iy * meta["step"]
    return x, y, iy, ix


# --------------------------------------------------------------------------- #
# one (round, split, scene)
# --------------------------------------------------------------------------- #
def measure(scene_dir, drop_min, r_run):
    hm_p = os.path.join(scene_dir, "heightmap.npy")
    mt_p = os.path.join(scene_dir, "heightmap_meta.json")
    va_p = os.path.join(scene_dir, "variation.json")
    for p in (hm_p, mt_p, va_p):
        if not os.path.exists(p):
            return dict(ok=False, why="missing " + os.path.basename(p))

    meta = json.load(open(mt_p, encoding="utf-8"))
    z = np.load(hm_p).astype(np.float64)
    var = json.load(open(va_p, encoding="utf-8"))

    mask, drop_R, _ = edge_cells(z, float(meta["step"]), drop_min, r_run)
    n_edge = int(mask.sum())
    out = dict(ok=True, scene=meta.get("scene"), arm_config=meta.get("arm_config"),
               hm_step=float(meta["step"]), hm_shape=list(z.shape),
               n_cells_finite=int(np.isfinite(z).sum()), n_edge_cells=n_edge,
               edge_area_m2=round(n_edge * float(meta["step"]) ** 2, 4),
               max_drop_in_run_m=(round(float(np.nanmax(drop_R[np.isfinite(drop_R)])), 4)
                                  if np.isfinite(drop_R).any() else None),
               conds=var.get("conds"), split=var.get("split"), n_cuts=len(var.get("cuts", [])))
    if n_edge == 0:
        out.update(dist_min=None, dist_med=None, dist_max=None, n_cams=0,
                   note="no edge-candidate cell at this drop_min / r_run")
        return out

    ex, ey, iy, ix = cell_xyz(mask, meta)
    ez = z[iy, ix]

    d = []
    for cut in var.get("cuts", []):
        cam = cut.get("cam") or {}
        eye = cam.get("eye")
        if not eye:
            continue
        dx = ex - eye[0]
        dy = ey - eye[1]
        dz = ez - eye[2]
        d.append(float(np.sqrt(np.min(dx * dx + dy * dy + dz * dz))))
    if not d:
        out.update(dist_min=None, dist_med=None, dist_max=None, n_cams=0,
                   note="variation.json carries no cam.eye")
        return out
    a = np.asarray(d)
    out.update(n_cams=len(d),
               dist_min=round(float(a.min()), 3),
               dist_p25=round(float(np.percentile(a, 25)), 3),
               dist_med=round(float(np.median(a)), 3),
               dist_p75=round(float(np.percentile(a, 75)), 3),
               dist_max=round(float(a.max()), 3),
               dist_all=[round(v, 3) for v in d])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--round")
    ap.add_argument("--split")
    ap.add_argument("--scene")
    ap.add_argument("--plan", help="json list of {round, split, scene}")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    drop_min, r_run = K.DROP_MIN_M, K.R_RUN_M
    jobs = (json.load(open(a.plan, encoding="utf-8")) if a.plan
            else [dict(round=a.round, split=a.split, scene=a.scene)])

    res = []
    for j in jobs:
        rd = vk.round_dir(j["round"])           # NEVER spell a dataset path
        sd = os.path.join(rd, j["split"], j["scene"])
        r = measure(sd, drop_min, r_run)
        r.update(round=j["round"], split=j["split"], scene_id=j["scene"],
                 scene_dir=sd, drop_min_m=drop_min, r_run_m=r_run,
                 const_fingerprint=K.fingerprint())
        res.append(r)
        print(f'{j["scene"]:9s} {j["round"]:26s} {j["split"]:5s} '
              f'edge_cells={r.get("n_edge_cells")} '
              f'dist(min/med/max)={r.get("dist_min")}/{r.get("dist_med")}/{r.get("dist_max")} '
              f'n_cam={r.get("n_cams")}', flush=True)

    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    main()
