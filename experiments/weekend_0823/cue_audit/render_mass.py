#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_mass.py — REAL-RENDER pixel mass per CUE-OFF arm pair (A2 instrument).

Replaces the AABB silhouette upper bounds of `pixel_mass.py` (PREREG sec.3) with a
measurement taken on the RENDERED frames, per scene, per band-stem, per frame, at
BOTH thresholds the corpus uses:

    >= 8/255   (sensitive; above the 2/255 renderer-noise band F7 identified)
    >= 32/255  (F7 canonical)

Frame populations reported separately, because the pre-registration judges on
paired strict-H frames only (PREREG sec.4.2):

    all       every rendered cut of the band            (n = 24)
    H_A       cuts that are strict-H in arm A           (lineage label set)
    paired    cuts that are strict-H in BOTH arms       (the judged population)

Also emits the G0 noise floor (arm A vs the canonical lineage `_on` round: same
geometry, different render call) so every ratio below can be read against it.

Output: RENDER_MASS.csv (per-frame) + RENDER_MASS_SUMMARY.csv (per pair) and a
console table.  CPU only, read-only on the dataset.
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
DS = os.path.join(REPO, "dataset")
AUDIT = os.path.join(REPO, "experiments/weekend_0823/cue_audit")

# (scene, split dir under the round, band stem, canonical lineage round)
UNITS = [
    ("scene12", "test",  "260823_cueoff",  "260820_boost_e"),
    ("scene17", "train", "260823_cueoff",  "260820_boost_h"),
    ("scene20", "train", "260823_cueoff",  "260820_boost_e2"),
    ("scene12", "test",  "260823_cueoff2", "260820_boost_e2"),
]
ARMS = ("B1", "B2", "P", "C")
THRS = (8, 32)


def load(p):
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def tiers(stem, arm, scene, lset="lineage"):
    """{basename: tier_strict} for the arm's own ON frames."""
    p = os.path.join(AUDIT, "labels", f"{lset}__{stem}_{arm}__{scene}.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p))
    out = {}
    for fid, rec in d["frames"].items():
        if not fid.startswith("on/"):
            continue
        out[os.path.basename(fid)] = rec.get("tier_strict")
    return out


def per_frame_diff(dir_a, dir_b):
    """{basename: {thr: npix}} plus the frame pixel count."""
    out, npx = {}, None
    for a in sorted(glob.glob(os.path.join(dir_a, "*.png"))):
        b = os.path.join(dir_b, os.path.basename(a))
        if not os.path.exists(b):
            continue
        d = np.abs(load(a) - load(b)).max(axis=2)
        npx = d.size
        out[os.path.basename(a)] = {t: int((d >= t).sum()) for t in THRS}
    return out, npx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(AUDIT, "RENDER_MASS.csv"))
    ap.add_argument("--summary", default=os.path.join(AUDIT, "RENDER_MASS_SUMMARY.csv"))
    ap.add_argument("--extra-round", default="",
                    help="comma list of extra round stems to fold in, e.g. 260823_cueoff_s20fix")
    a = ap.parse_args()

    units = list(UNITS)
    for extra in [s for s in a.extra_round.split(",") if s]:
        # discover scene/split from the arm-A round on disk
        for d in sorted(glob.glob(os.path.join(round_dir_or_flat(f"{extra}_A"), "*", "scene*"))):
            sc = os.path.basename(d)
            sub = os.path.basename(os.path.dirname(d))
            units.append((sc, sub, extra, ""))

    rows, summ = [], []
    for scene, sub, stem, lineage in units:
        base_a = os.path.join(round_dir_or_flat(f"{stem}_A"), sub, scene)
        if not os.path.isdir(base_a):
            print(f"[skip] {stem} {scene}: no arm A")
            continue
        tA = tiers(stem, "A", scene)
        for arm in ARMS:
            dir_b = os.path.join(round_dir_or_flat(f"{stem}_{arm}"), sub, scene)
            if not os.path.isdir(dir_b):
                continue
            pf, npx = per_frame_diff(base_a, dir_b)
            if not pf:
                continue
            tB = tiers(stem, arm, scene)
            for fn, cnt in sorted(pf.items()):
                rows.append(dict(scene=scene, stem=stem, pair=f"A_vs_{arm}", frame=fn,
                                 tier_A=tA.get(fn, "?"), tier_B=tB.get(fn, "?"),
                                 px_ge8=cnt[8], px_ge32=cnt[32], n_px=npx,
                                 pct_ge8=round(100.0 * cnt[8] / npx, 4),
                                 pct_ge32=round(100.0 * cnt[32] / npx, 4)))
            pops = {
                "all": list(pf),
                "H_A": [f for f in pf if tA.get(f) == "H"],
                "paired": [f for f in pf if tA.get(f) == "H" and tB.get(f) == "H"],
            }
            for pop, fl in pops.items():
                if not fl:
                    summ.append(dict(scene=scene, stem=stem, pair=f"A_vs_{arm}",
                                     pop=pop, n=0, px_ge8=0, px_ge32=0,
                                     pct_ge8=0.0, pct_ge32=0.0))
                    continue
                m8 = float(np.mean([pf[f][8] for f in fl]))
                m32 = float(np.mean([pf[f][32] for f in fl]))
                summ.append(dict(scene=scene, stem=stem, pair=f"A_vs_{arm}", pop=pop,
                                 n=len(fl), px_ge8=round(m8, 1), px_ge32=round(m32, 1),
                                 pct_ge8=round(100.0 * m8 / npx, 4),
                                 pct_ge32=round(100.0 * m32 / npx, 4)))
        # ---- G0 noise floor: arm A vs the canonical lineage `on` round
        if lineage:
            hit = [d for d in glob.glob(os.path.join(
                round_dir_or_flat(lineage + "_on"), "*", scene))
                   if os.path.isdir(d)]
            if hit:
                pf, npx = per_frame_diff(base_a, hit[0])
                if pf:
                    for pop, fl in (("all", list(pf)),
                                    ("H_A", [f for f in pf if tA.get(f) == "H"])):
                        if not fl:
                            continue
                        m8 = float(np.mean([pf[f][8] for f in fl]))
                        m32 = float(np.mean([pf[f][32] for f in fl]))
                        summ.append(dict(scene=scene, stem=stem, pair="A_vs_LINEAGE_ON",
                                         pop=pop, n=len(fl),
                                         px_ge8=round(m8, 1), px_ge32=round(m32, 1),
                                         pct_ge8=round(100.0 * m8 / npx, 4),
                                         pct_ge32=round(100.0 * m32 / npx, 4)))

    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(a.summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0]))
        w.writeheader()
        w.writerows(summ)

    cur = None
    for r in summ:
        k = (r["scene"], r["stem"])
        if k != cur:
            cur = k
            print(f"\n=== {r['scene']} · {r['stem']} ===")
            print(f"{'pair':18s} {'pop':7s} {'n':>3s} {'px>=8':>10s} {'%':>7s} "
                  f"{'px>=32':>10s} {'%':>7s}")
        print(f"{r['pair']:18s} {r['pop']:7s} {r['n']:3d} {r['px_ge8']:10.0f} "
              f"{r['pct_ge8']:7.3f} {r['px_ge32']:10.0f} {r['pct_ge32']:7.3f}")
    print(f"\n-> {a.out}\n-> {a.summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
