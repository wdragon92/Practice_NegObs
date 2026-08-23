#!/usr/bin/env python3
"""G7 repair, step 4b — the scene12 case, frame by frame, plus the byte-identity
control on the scene-arms no fused sidecar was added to."""
import json, os, collections
REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OLD = os.path.join(REPO, "experiments/dayrun_0820/annotations")
NEW = os.path.join(REPO, "experiments/v3_0823/annotations")
TOUCHED = {("e", "scene07"), ("e", "scene08"), ("e", "scene12"),
           ("e2", "scene07"), ("e2", "scene12")}

print("### control — every scene-arm with NO fused sidecar must reproduce byte-identically")
tot = same = diff = 0
bad = []
for band in ("e", "e2"):
    O = json.load(open(os.path.join(OLD, f"labels_boost_{band}.json")))
    N = json.load(open(os.path.join(NEW, f"labels_boost_{band}_g7fix.json")))
    for k in O["frames"]:
        sc = k.split("/")[1]
        if (band, sc) in TOUCHED:
            continue
        tot += 1
        if json.dumps(O["frames"][k], sort_keys=True) == json.dumps(N["frames"][k], sort_keys=True):
            same += 1
        else:
            diff += 1; bad.append((band, k))
print(f"  untouched frames {tot}  identical {same}  DIFFERENT {diff}")
for b in bad[:10]:
    print("   ", b)

print("\n### scene12 — the 48 claimed strict-H frames, frame by frame")
hdr = (f"{'band':4s} {'frame':34s} {'tier b':7s} {'tier a':11s} "
       f"{'kept b':>6s} {'kept a':>6s} {'gtcells b':>9s} {'gtcells a':>9s} "
       f"{'int_px a':>8s} {'edgevis a':>9s} {'edge_ratio a':>12s} {'edgeproj a':>10s}")
print(hdr); print("-" * len(hdr))
agg = collections.Counter()
for band in ("e", "e2"):
    O = json.load(open(os.path.join(OLD, f"labels_boost_{band}.json")))
    N = json.load(open(os.path.join(NEW, f"labels_boost_{band}_g7fix.json")))
    for k in sorted(O["frames"]):
        if not k.startswith("on/scene12/"):
            continue
        o, n = O["frames"][k], N["frames"][k]
        agg[(band, o["tier_strict"], n["tier_strict"])] += 1
        print(f"{band:4s} {k.split('/')[-1]:34s} {o['tier_strict']:7s} {n['tier_strict']:11s} "
              f"{o['footprint']['cells_kept']:6d} {n['footprint']['cells_kept']:6d} "
              f"{sum(o['polar_gt']):9d} {sum(n['polar_gt']):9d} "
              f"{n['raw_vis']['int_px']:8d} {n['raw_vis']['edge_visible']:9d} "
              f"{str(n['raw_vis']['edge_ratio']):>12s} {n['raw_vis']['edge_projected']:10d}")
print("\n  aggregate:", dict(agg))
