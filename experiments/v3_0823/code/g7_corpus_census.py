#!/usr/bin/env python3
"""G7 repair — corpus-level census + the s12-artefact gate over the WHOLE corrected
corpus (2832 frames), not just the re-labelled ones."""
import json, os, collections
REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
BASE = os.path.join(REPO, "experiments/dayrun_0820/dataset_manifest_v2_full.json")
CORR = os.path.join(REPO, "experiments/v3_0823/dataset_manifest_v2corr.json")
CORA = os.path.join(REPO, "experiments/v3_0823/dataset_manifest_v2corr_roundown.json")
SPLIT = json.load(open(os.path.join(REPO, "experiments/dayrun_0820/split_v2_full.json")))
SPLIT_OF = {s: k for k, v in SPLIT.items() for s in v}
TIERS = ["V", "E", "H", "H_weak", "none_in_fov", "off"]


def census(p):
    M = json.load(open(p))
    by_split = collections.defaultdict(collections.Counter)
    tot = collections.Counter()
    for f in M["frames"]:
        by_split[SPLIT_OF.get(f["scene_id"], "?")][f["tier"]] += 1
        tot[f["tier"]] += 1
    return by_split, tot, M


def gate(p, name):
    M = json.load(open(p))
    bad = [f for f in M["frames"] if f["tier"] == "H" and
           (f["raw_vis"]["int_px"] > 0 or f["raw_vis"]["edge_visible"] > 0
            or f["raw_vis"].get("int_px_fallback", 0) > 0)]
    print(f"  GATE {name}: strict-H frames with visible hazard pixels = {len(bad)}"
          f"   (of {sum(1 for f in M['frames'] if f['tier']=='H')} strict-H frames)")
    for f in bad[:10]:
        print("    ", f["frame_id"], f["raw_vis"]["int_px"], f["raw_vis"]["edge_visible"],
              f["raw_vis"].get("int_px_fallback"))
    return len(bad)


print("### corpus tier census (2832 frames, split_v2_full)\n")
hdr = f"{'split':6s} {'source':10s} " + " ".join(f"{t:>12s}" for t in TIERS)
print(hdr); print("-" * len(hdr))
bB, tB, _ = census(BASE)
bC, tC, _ = census(CORR)
bA, tA, _ = census(CORA)
for sp in ("train", "val", "test", "hold", "?"):
    if not (bB[sp] or bC[sp]):
        continue
    for tag, b in (("BEFORE", bB), ("AFTER-B", bC), ("AFTER-A", bA)):
        print(f"{sp:6s} {tag:10s} " + " ".join(f"{b[sp][t]:12d}" for t in TIERS))
    print()
print(f"{'TOTAL':6s} {'BEFORE':10s} " + " ".join(f"{tB[t]:12d}" for t in TIERS))
print(f"{'TOTAL':6s} {'AFTER-B':10s} " + " ".join(f"{tC[t]:12d}" for t in TIERS))
print(f"{'TOTAL':6s} {'AFTER-A':10s} " + " ".join(f"{tA[t]:12d}" for t in TIERS))

print("\n### s12-artefact gate over the corrected corpus")
gate(BASE, "BEFORE (frozen v2_full)")
gate(CORR, "AFTER  variant B (canonical)")
gate(CORA, "AFTER  variant A (round-own)")

print("\n### strict-H census by scene (on-arm), BEFORE vs AFTER-B")
def hcount(p):
    M = json.load(open(p)); c = collections.Counter()
    for f in M["frames"]:
        if f["tier"] == "H":
            c[(SPLIT_OF.get(f["scene_id"], "?"), f["scene_id"])] += 1
    return c
hb, hc = hcount(BASE), hcount(CORR)
for k in sorted(set(hb) | set(hc)):
    mark = "  <-- CHANGED" if hb[k] != hc[k] else ""
    print(f"  {k[0]:6s} {k[1]:8s} H {hb[k]:3d} -> {hc[k]:3d}{mark}")
