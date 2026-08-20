#!/usr/bin/env python3
"""DAYRUN 0820 Phase 1 step 2 -- the MANDATORY grid-invariance gate.

V/E/H/H_weak/none_in_fov are properties of a FRAME (what the camera can see of a
drop), not of the grid we bin the drop into.  Retiling V0's band 3 [5,12) m into
V1's 3a [5,8) + 3b [8,12) therefore must not move a single frame between tiers.
Only one tier has any grid dependence at all -- `none_in_fov`, which fires when NO
cell is positive -- and V1 preserves the outer radius (12 m) and the angular
coverage exactly, so the set of ground points inside the grid is identical and
even that tier is invariant.  A mismatch here is a labeler bug, full stop.

Compares EVERY frame of ALL 33 scenes (both arms), not the 29-scene eligible view.
"""
import argparse, collections, json, sys

TIERS = ("V", "E", "H", "H_weak", "none_in_fov", "off", "no_depth")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v0", required=True)
    ap.add_argument("--v1", required=True)
    ap.add_argument("--max-list", type=int, default=10)
    a = ap.parse_args()

    L0 = json.load(open(a.v0))
    L1 = json.load(open(a.v1))
    F0, F1 = L0["frames"], L1["frames"]
    g0, g1 = L0["grid"], L1["grid"]
    ns = g1["n_sectors"]

    print(f"V0 = {g0['version']}  bands {g0['band_edges_m']}  "
          f"({g0['n_bands']}x{g0['n_sectors']} = {g0['n_bands'] * g0['n_sectors']} cells)")
    print(f"V1 = {g1['version']}  bands {g1['band_edges_m']}  "
          f"({g1['n_bands']}x{g1['n_sectors']} = {g1['n_bands'] * g1['n_sectors']} cells)")

    only0 = sorted(set(F0) - set(F1))
    only1 = sorted(set(F1) - set(F0))
    common = sorted(set(F0) & set(F1))
    print(f"\nframes: V0 {len(F0)}  V1 {len(F1)}  common {len(common)}  "
          f"V0-only {len(only0)}  V1-only {len(only1)}")
    if only0 or only1:
        print(f"  V0-only: {only0[:5]}\n  V1-only: {only1[:5]}")

    scenes = sorted({k.split("/")[1] for k in common})
    print(f"scenes covered: {len(scenes)}")

    mism, pos_mism, anypos_mism = [], [], []
    t0c, t1c = collections.Counter(), collections.Counter()
    for k in common:
        a0, a1 = F0[k], F1[k]
        t0, t1 = a0["tier_strict"], a1["tier_strict"]
        t0c[t0] += 1
        t1c[t1] += 1
        if t0 != t1:
            mism.append((k, t0, t1))
        # the containment law: V0 cell (2*ns+s) positive  <->  V1 3a or 3b positive
        p0, p1 = a0["polar_gt"], a1["polar_gt"]
        fold = [p1[b * ns + s] if b < 2 else (p1[2 * ns + s] | p1[3 * ns + s])
                for b in range(3) for s in range(ns)]
        if fold != p0:
            pos_mism.append((k, p0, p1))
        if bool(any(p0)) != bool(any(p1)):
            anypos_mism.append((k, p0, p1))

    print("\n--- TIER TOTALS (all 33 scenes, both arms) ---")
    print(f"{'tier':<14}{'V0':>7}{'V1':>7}{'delta':>7}")
    for t in TIERS:
        if t0c[t] or t1c[t]:
            print(f"{t:<14}{t0c[t]:>7}{t1c[t]:>7}{t1c[t] - t0c[t]:>7}")

    print(f"\n--- INVARIANT GATE ---")
    print(f"frame-by-frame tier_strict(V1) == tier_strict(V0) mismatches: {len(mism)}")
    print(f"any-cell-positive (drives none_in_fov) mismatches           : {len(anypos_mism)}")
    print(f"nesting-law violations (V1 folded back onto V0 != V0)       : {len(pos_mism)}")

    if mism:
        print(f"\nFIRST {min(a.max_list, len(mism))} TIER MISMATCHES:")
        for k, t0, t1 in mism[:a.max_list]:
            r0, r1 = F0[k]["raw_vis"], F1[k]["raw_vis"]
            print(f"\n  {k}\n    tier V0={t0}  V1={t1}")
            print(f"    raw_vis V0: int_px={r0['int_px']} edge_visible={r0['edge_visible']} "
                  f"edge_projected={r0['edge_projected']} edge_ratio={r0['edge_ratio']}")
            print(f"    raw_vis V1: int_px={r1['int_px']} edge_visible={r1['edge_visible']} "
                  f"edge_projected={r1['edge_projected']} edge_ratio={r1['edge_ratio']}")
            print(f"    polar_gt V0 = {F0[k]['polar_gt']}  (any={any(F0[k]['polar_gt'])})")
            print(f"    polar_gt V1 = {F1[k]['polar_gt']}  (any={any(F1[k]['polar_gt'])})")
            print(f"    cell_counts V0 band3 = {F0[k]['cell_counts'][2 * ns:3 * ns]}")
            print(f"    cell_counts V1 3a/3b = {F1[k]['cell_counts'][2 * ns:3 * ns]} / "
                  f"{F1[k]['cell_counts'][3 * ns:4 * ns]}")
    if pos_mism:
        print(f"\nFIRST {min(a.max_list, len(pos_mism))} NESTING VIOLATIONS:")
        for k, p0, p1 in pos_mism[:a.max_list]:
            print(f"  {k}\n    V0={p0}\n    V1={p1}")

    ok = not mism and not only0 and not only1
    print(f"\nVERDICT: {'IDENTICAL — PASS' if ok else 'MISMATCH — FAIL, STOP'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
