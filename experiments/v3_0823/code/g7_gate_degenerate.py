#!/usr/bin/env python3
"""G7 gate, substantive form — "no s12-class artefact left".

Why the naive form is not enough.  `labeler.tier_of` DEFINES strict-H as
`int_px == 0 and edge_visible == 0`, so "count strict-H frames whose hazard
contributes pixels" is 0 by construction inside any single label set -- it was 0
in the defective set too.  What made scene12's H a lie was not an inconsistency
inside the label file; it was that the file's footprint was a 50-cell splinter,
so there was nothing for a pixel to land in.

The gate that actually bites therefore re-measures the FOOTPRINT of every
scene-arm that still carries a strict-H frame with the OTHER instrument
(depth fusion, computed in memory -- nothing is written), and asks whether the
instrument in use is under-measuring the way scene12's was.

  ratio = fused_footprint_cells / used_footprint_cells
  FLAG if the used instrument finds < 10 % of what the other one finds
        AND the other one finds a non-trivial footprint (>= 500 cells)
  (scene12 before repair: 50 vs 33605 = 0.15 %.)

Then, for the frames the repair touched, the corrected tier is re-derived under
BOTH corrected references (variant A round-own, variant B corpus-reference) and
any frame that is strict-H under one and not the other is reported.
"""
import json, os, sys, collections
import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
LAB = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LAB)
from labeler import load_heightmap, scene_dirs                       # noqa: E402
from fuse_heightmap import fuse_scene_arm                            # noqa: E402

HZ = 0.3
CORR = os.path.join(REPO, "experiments/v3_0823/dataset_manifest_v2corr.json")
CORA = os.path.join(REPO, "experiments/v3_0823/dataset_manifest_v2corr_roundown.json")


def fp_cells(on, off):
    void = ~np.isfinite(on) | ~np.isfinite(off)
    d = np.where(void, np.nan, off - on)
    return int(((~void) & (d >= HZ)).sum())


def main():
    M = json.load(open(CORR))
    # every (round, scene) that still carries a strict-H frame
    need = sorted({(f["round"], f["scene_id"]) for f in M["frames"] if f["tier"] == "H"})
    print(f"strict-H frames live in {len(need)} (round, scene) pairs\n")
    hdr = (f"{'round':22s} {'scene':8s} {'H':>4s} {'used inst':10s} {'used cells':>10s} "
           f"{'fused cells':>11s} {'ratio':>8s}  verdict")
    print(hdr); print("-" * len(hdr))
    cache, flags = {}, []
    for rnd, sc in need:
        arm = "on" if rnd.endswith("_on") else "off"
        off_round = rnd[:-3] + "_off" if arm == "on" else rnd
        don = scene_dirs(os.path.join(REPO, "dataset", rnd))[sc]
        dof = scene_dirs(os.path.join(REPO, "dataset", off_round))[sc]
        hm_on, _, src_on = load_heightmap(don)
        hm_off, _, src_off = load_heightmap(dof)
        used = fp_cells(hm_on, hm_off)
        for d in (don, dof):
            if d not in cache:
                cache[d] = fuse_scene_arm(d)[0].astype(np.float64)
        fused = fp_cells(cache[don], cache[dof])
        nH = sum(1 for f in M["frames"] if f["round"] == rnd and f["scene_id"] == sc
                 and f["tier"] == "H")
        ratio = (used / fused) if fused else float("inf")
        bad = (fused >= 500) and (ratio < 0.10)
        if bad:
            flags.append((rnd, sc, used, fused, ratio))
        print(f"{rnd:22s} {sc:8s} {nH:4d} {src_on+'/'+src_off:10s} {used:10d} {fused:11d} "
              f"{ratio:8.3f}  {'**FLAG**' if bad else 'ok'}")
    print(f"\nG7 degenerate-footprint FLAGS among strict-H scene-arms: {len(flags)}")

    print("\n### cross-reference re-derivation on the 240 repaired frames")
    A = {f["frame_id"]: f for f in json.load(open(CORA))["frames"]}
    dis = [(f["frame_id"], f["tier"], A[f["frame_id"]]["tier"]) for f in M["frames"]
           if f.get("label_source", "original") != "original"
           and (f["tier"] == "H") != (A[f["frame_id"]]["tier"] == "H")]
    print(f"  frames strict-H under one corrected reference but not the other: {len(dis)}")
    for d in dis[:10]:
        print("   ", d)


if __name__ == "__main__":
    main()
