#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_on_arm.py — keep the ON arm of the control manifest identical to the frozen one.

Why this exists. The labeler derives GT as `z_off - z_on >= 0.30` (footprint v2, D10), so
re-labelling the ON arm against a NEW off arm re-derives the ON arm's labels. For sceneC2 the
two off arms differ by ~18 mm in the fill height (0.0163 m leaf card vs -0.002 m walk slab),
which cannot move a 0.30 m threshold anywhere the drop is 2.24 m, but CAN move it by ~5 cm along
the shallow side-lawn slope, and the same 18 mm shifts the interior-pixel reference (z_off-0.15)
that decides V/E/H. A one-cell or one-tier flip would make the old/new comparison compare two
different ON arms, which is exactly the confound this whole track exists to remove.

So: the ON arm is frozen (brief rule 2). This script reports every difference it finds and then
writes the frozen values (`polar_gt`, `polar_gt_pregate`, `gate_excluded`, `tier`, `raw_vis`)
into the control manifest, leaving the OFF arm -- the thing being measured -- untouched.

  python3 sync_on_arm.py --manifest manifest_ctrl.json --frozen ../../dayrun_0820/dataset_manifest_v2_full.json
  ... --report-only          # print the diff, change nothing
Exit 0 always unless a frame is missing from the frozen manifest (then 1: the pair is not the
published on arm at all).
"""
from __future__ import annotations

import argparse
import json
import sys

FIELDS = ("polar_gt", "polar_gt_pregate", "gate_excluded", "tier", "raw_vis")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--frozen", required=True)
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()

    man = json.load(open(a.manifest))
    frozen = json.load(open(a.frozen))
    ref = {}
    for f in frozen["frames"]:
        ref[f["frame_id"]] = f
        ref.setdefault(f["frame_id"].split("::", 1)[0], f)      # D24 round token

    n_on, missing, diffs, synced = 0, [], {k: 0 for k in FIELDS}, 0
    for f in man["frames"]:
        if f.get("toggle_state") != "on":
            continue
        n_on += 1
        r = ref.get(f["frame_id"]) or ref.get(f["frame_id"].split("::", 1)[0])
        if r is None:
            missing.append(f["frame_id"])
            continue
        changed = False
        for k in FIELDS:
            if k in r and f.get(k) != r[k]:
                diffs[k] += 1
                if not a.report_only:
                    f[k] = r[k]
                    changed = True
        synced += 1 if changed else 0

    print(f"[sync_on_arm] {n_on} on-arm frames · differences vs the frozen manifest: "
          + " · ".join(f"{k} {v}" for k, v in diffs.items()))
    if missing:
        print(f"[sync_on_arm] FATAL {len(missing)} on-arm frames are not in the frozen manifest: "
              f"{missing[:5]}", file=sys.stderr)
        return 1
    if a.report_only:
        print("[sync_on_arm] report-only: nothing written")
        return 0
    man.setdefault("meta", {})["on_arm_labels"] = dict(
        source=a.frozen, note="ON-arm labels frozen: re-derivation against the control off arm "
                              "was discarded so both off arms are compared against the same "
                              "published on arm.",
        fields_synced={k: v for k, v in diffs.items() if v})
    with open(a.manifest, "w") as f:
        json.dump(man, f, indent=1)
    print(f"[sync_on_arm] {synced} on-arm frames rewritten from the frozen manifest -> {a.manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
