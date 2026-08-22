#!/usr/bin/env python3
"""V2S TEST TRACK -- the MANDATORY V1 -> V2S invariance gate (PS 12.6 procedure 1,
following the V0 -> V1 precedent in experiments/dayrun_0820/P1_GRID_V1.md sec.1).

V/E/H/H_weak/none_in_fov are properties of a FRAME (what the camera can SEE of a
drop), not of the tiling we bin the drop into.  V2S bisects each V1 SECTOR while
keeping the band edges, the outer radius (12 m) and the total angular coverage
(+-31.1 deg) byte-identical, so the set of ground points inside the grid does not
move.  The only tier with any grid dependence at all -- `none_in_fov`, which fires
when NO cell is positive -- is therefore invariant too.  A mismatch here is a
labeler bug, full stop: HARD STOP, record the cause, roll back.

Three gates, all mandatory:
  (a) tier 5-category counts identical to V1, frame by frame, over the WHOLE view
  (b) any-cell-positive identical per frame (the channel that drives none_in_fov)
  (c) FOLDING LAW: for every frame and every V1 cell,
          V1_cell(b*5 + s) == V2S_cell(b*10 + 2s) OR V2S_cell(b*10 + 2s + 1)
      violations must be 0.  Run on polar_gt AND on polar_gt_pregate (D14: the
      pre-gate wedge result rides along, so the refinement must be exact there too).

Usage (run it TWICE -- the 1584 main view and the 2832 merged view):
  python invariant_gate_v2s.py --v1 <labels_v1*.json> --v2s <labels_v2s*.json>
"""
import argparse
import collections
import json
import sys

TIERS = ("V", "E", "H", "H_weak", "none_in_fov", "off", "no_depth")


def fold(p2, ns1, nb, pairs):
    """V2S vector -> the V1-indexed vector it implies (sector pair OR)."""
    return [p2[b * (2 * ns1) + pairs[s][0]] | p2[b * (2 * ns1) + pairs[s][1]]
            for b in range(nb) for s in range(ns1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1", required=True)
    ap.add_argument("--v2s", required=True)
    ap.add_argument("--label", default="", help="name of this view, for the header")
    ap.add_argument("--max-list", type=int, default=10)
    a = ap.parse_args()

    L1 = json.load(open(a.v1))
    L2 = json.load(open(a.v2s))
    F1, F2 = L1["frames"], L2["frames"]
    g1, g2 = L1["grid"], L2["grid"]
    ns1, ns2 = int(g1["n_sectors"]), int(g2["n_sectors"])
    nb = int(g1["n_bands"])

    print(f"=== INVARIANT GATE V1 -> V2S {a.label} ===")
    print(f"V1  = {g1['version']}  {g1['n_bands']}x{ns1} = {g1['n_bands'] * ns1} cells  "
          f"sectors {g1['sector_names']}  bands {g1['band_edges_m']}")
    print(f"V2S = {g2['version']}  {g2['n_bands']}x{ns2} = {g2['n_bands'] * ns2} cells  "
          f"sectors {g2['sector_names']}  bands {g2['band_edges_m']}")

    # ---- structural preconditions of the refinement -------------------------
    struct = []
    if ns2 != 2 * ns1:
        struct.append(f"n_sectors {ns2} != 2 x {ns1}")
    if [float(x) for x in g1["band_edges_m"]] != [float(x) for x in g2["band_edges_m"]]:
        struct.append("band_edges_m differ")
    if list(g1["band_names"]) != list(g2["band_names"]):
        struct.append("band_names differ")
    e1 = [float(x) for x in g1["sector_edges_deg"]]
    e2 = [float(x) for x in g2["sector_edges_deg"]]
    if e2[::2] != e1:
        struct.append(f"every other V2S sector edge must reproduce V1's: {e2[::2]} != {e1}")
    mids = [round((e1[s] + e1[s + 1]) / 2.0, 6) for s in range(ns1)]
    got_mids = [round(e2[2 * s + 1], 6) for s in range(ns1)]
    if got_mids != mids:
        struct.append(f"V2S interior edges are not the V1 midpoints: {got_mids} != {mids}")
    pairs = [(2 * s, 2 * s + 1) for s in range(ns1)]
    spec_pairs = [tuple(p) for p in (g2.get("sector_pairs") or pairs)]
    if spec_pairs != pairs:
        struct.append(f"gridspec sector_pairs {spec_pairs} != the bisection pairing {pairs}")
    # hflip permutation must fall out of the generic formula, with NO fixed centre
    perm = [b * ns2 + (ns2 - 1 - s) for b in range(nb) for s in range(ns2)]
    if any(perm[i] == i for i in range(len(perm))):
        struct.append("hflip permutation has a FIXED cell -- impossible at an even sector count")
    if [perm[i] for i in perm] != list(range(len(perm))):
        struct.append("hflip permutation is not an involution")
    print(f"\n--- structure ---")
    print(f"sector bisection pairs (0-based): {pairs}")
    print(f"hflip sector pairing (1-based)  : "
          f"{[(s + 1, ns2 - s) for s in range(ns2 // 2)]}")
    for m in struct:
        print(f"  STRUCT FAIL: {m}")
    if not struct:
        print("  structure OK: V2S is a strict angular bisection of V1")

    # ---- frame sets ---------------------------------------------------------
    only1 = sorted(set(F1) - set(F2))
    only2 = sorted(set(F2) - set(F1))
    common = sorted(set(F1) & set(F2))
    print(f"\nframes: V1 {len(F1)}  V2S {len(F2)}  common {len(common)}  "
          f"V1-only {len(only1)}  V2S-only {len(only2)}")
    if only1 or only2:
        print(f"  V1-only : {only1[:5]}\n  V2S-only: {only2[:5]}")
    print(f"scenes covered: {len({k.split('/')[1] for k in common})}")

    # ---- the three gates ----------------------------------------------------
    mism, anypos_mism, fold_mism, fold_pre_mism, len_bad = [], [], [], [], []
    t1c, t2c = collections.Counter(), collections.Counter()
    for k in common:
        d1, d2 = F1[k], F2[k]
        a1, a2 = d1["tier_strict"], d2["tier_strict"]
        t1c[a1] += 1
        t2c[a2] += 1
        if a1 != a2:
            mism.append((k, a1, a2))
        p1, p2 = d1["polar_gt"], d2["polar_gt"]
        if len(p1) != nb * ns1 or len(p2) != nb * ns2:
            len_bad.append(k)
            continue
        if bool(any(p1)) != bool(any(p2)):
            anypos_mism.append((k, p1, p2))
        if fold(p2, ns1, nb, pairs) != p1:
            fold_mism.append((k, p1, p2))
        q1 = d1.get("polar_gt_pregate", p1)
        q2 = d2.get("polar_gt_pregate", p2)
        if fold(q2, ns1, nb, pairs) != q1:
            fold_pre_mism.append((k, q1, q2))

    print("\n--- TIER TOTALS (every frame of the view, both arms) ---")
    print(f"{'tier':<14}{'V1':>7}{'V2S':>7}{'delta':>7}")
    for t in TIERS:
        if t1c[t] or t2c[t]:
            print(f"{t:<14}{t1c[t]:>7}{t2c[t]:>7}{t2c[t] - t1c[t]:>7}")
    print(f"{'frames':<14}{sum(t1c.values()):>7}{sum(t2c.values()):>7}"
          f"{sum(t2c.values()) - sum(t1c.values()):>7}")

    print("\n--- INVARIANT GATE ---")
    print(f"(a) frame-by-frame tier_strict(V2S) == tier_strict(V1) mismatches : {len(mism)}")
    print(f"(b) any-cell-positive (drives none_in_fov) mismatches             : "
          f"{len(anypos_mism)}")
    print(f"(c) FOLDING LAW violations, polar_gt   (sector pair OR != V1 cell): {len(fold_mism)}")
    print(f"(c) FOLDING LAW violations, pregate    (sector pair OR != V1 cell): "
          f"{len(fold_pre_mism)}")
    print(f"    vectors of the wrong length                                  : {len(len_bad)}")

    for title, lst in (("TIER MISMATCHES", mism), ("ANY-POS MISMATCHES", anypos_mism),
                       ("FOLDING VIOLATIONS", fold_mism),
                       ("FOLDING VIOLATIONS (pregate)", fold_pre_mism)):
        if lst:
            print(f"\nFIRST {min(a.max_list, len(lst))} {title}:")
            for row in lst[:a.max_list]:
                print(f"  {row[0]}\n    V1 ={row[1]}\n    V2S={row[2]}")

    ok = not (struct or mism or anypos_mism or fold_mism or fold_pre_mism
              or len_bad or only1 or only2)
    print(f"\nVERDICT{(' ' + a.label) if a.label else ''}: "
          f"{'IDENTICAL — PASS' if ok else 'MISMATCH — FAIL, HARD STOP'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
