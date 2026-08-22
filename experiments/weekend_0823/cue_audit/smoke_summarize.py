#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""smoke_summarize.py — turn the arm-C 1-cut smoke renders into SMOKE_CUEOFF.json,
the artifact gate G1 reads.

The smoke asks exactly two questions, and they are the two that a 1-cut render
can actually answer:

  1. does the ported arm C assemble and render at all?          (rc, cuts, sec)
  2. did the hazard-only surgery MOVE THE CAMERA GROUND DATUM?  (ground_z_delta)

(2) is the whole reason the smoke exists.  `variation_kit.sample_camera` is a
pure function of (scene, idx, seed), so cut idx 0 of a `--cams 1` run IS cut
idx 0 of the `--cams 8` lineage run -- the smoke's cut 0000 and the shipped
corpus's cut 0000 are the same camera draw, and their `cam.ground_z` may
therefore be compared directly.  A non-zero delta is the D17/D30 failure mode
(sceneC2's off arm moved 0.130 -> 0.0163 m and lost every twin pair).

A third read comes free and is recorded: the arm-C heightmap's z_min.  If the
`_solid_at` oracle patch in the scene12 copy had failed, the flat arm's sidecar
would still carry the ON-arm stair profile (z_min ~ -2.40 instead of ~ 0).
"""
import argparse
import glob
import json
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
AUDIT = os.path.join(REPO, "experiments/weekend_0823/cue_audit")
SMOKE = os.path.join(AUDIT, "smoke")
OUT = os.path.join(AUDIT, "SMOKE_CUEOFF.json")

# scene -> the lineage on-arm round whose cut 0000 is the SAME camera draw
LINEAGE_ON = {"scene12": "260820_boost_e_on",
              "scene17": "260820_boost_h_on",
              "scene20": "260820_boost_e2_on"}


def canonical_cut0(scene):
    p = glob.glob(os.path.join(REPO, "dataset", LINEAGE_ON[scene], "*", scene,
                               "variation.json"))
    if not p:
        return None
    v = json.load(open(p[0]))
    cu = v["cuts"]
    cuts = list(cu.values() if isinstance(cu, dict) else cu)
    for c in cuts:
        if c["file"].endswith("0000.png") and c["file"].startswith("L0__"):
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", dest="show", action="store_true")
    a = ap.parse_args()
    rec = {}
    for scene in sorted(LINEAGE_ON):
        d = os.path.join(SMOKE, scene)
        r = dict(dir=os.path.relpath(d, REPO) if os.path.isdir(d) else None,
                 rc=None, cuts=0, sec=None, ground_z=None,
                 ground_z_canonical=None, ground_z_delta=None,
                 eye=None, eye_canonical=None, hm_z_min=None, hm_z_max=None,
                 arm_config=None)
        vp = os.path.join(d, "variation.json")
        if os.path.isfile(vp):
            v = json.load(open(vp))
            cu = v["cuts"]
            cuts = list(cu.values() if isinstance(cu, dict) else cu)
            oks = [c for c in cuts if c.get("ok")]
            r["rc"] = 0 if oks else 1
            r["cuts"] = len(oks)
            r["sec"] = v.get("sec")
            if oks:
                c0 = oks[0]
                r["ground_z"] = c0["cam"]["ground_z"]
                r["eye"] = c0["cam"]["eye"]
                cc = canonical_cut0(scene)
                if cc and cc["file"] == c0["file"]:
                    r["ground_z_canonical"] = cc["cam"]["ground_z"]
                    r["eye_canonical"] = cc["cam"]["eye"]
                    r["ground_z_delta"] = round(
                        float(c0["cam"]["ground_z"]) - float(cc["cam"]["ground_z"]), 8)
                elif cc:
                    r["note"] = (f"smoke cut {c0['file']} != canonical cut "
                                 f"{cc['file']} -- cannot compare")
        hm = os.path.join(d, "heightmap_meta.json")
        if os.path.isfile(hm):
            m = json.load(open(hm))
            r["hm_z_min"], r["hm_z_max"] = m.get("z_min"), m.get("z_max")
            r["arm_config"] = m.get("arm_config")
        rec[scene] = r
    json.dump(dict(what="CUE-OFF arm-C 1-frame smoke", out=OUT, scenes=rec),
              open(OUT, "w"), indent=1)
    if a.show:
        print(f"\n=== SMOKE_CUEOFF (arm C, 1 cut, cond L0) ===")
        for sc, r in rec.items():
            if r["rc"] is None:
                print(f"  {sc}: NOT RUN")
                continue
            dz = r["ground_z_delta"]
            verdict = ("DATUM OK" if dz is not None and abs(dz) < 1e-6 else
                       f"DATUM MOVED {dz:+.6f} m -- STOP" if dz is not None else
                       "no canonical reference")
            print(f"  {sc}: rc={r['rc']} cuts={r['cuts']} sec={r['sec']} · "
                  f"ground_z {r['ground_z']} vs canonical {r['ground_z_canonical']} "
                  f"-> {verdict}")
            print(f"        heightmap z [{r['hm_z_min']}, {r['hm_z_max']}] "
                  f"· cfg {r['arm_config']}")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
