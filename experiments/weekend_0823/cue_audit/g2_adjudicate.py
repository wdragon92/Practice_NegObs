#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g2_adjudicate.py — individual adjudication of every G2 breach (D49-2, R4 F4/V1).

D44 examined ONE of the eight `heightmap.npy differs` failures and generalised.
This script examines all eight, at three scopes, and refuses to generalise:

  1. CELL LOCALISATION   which (x, y) cells of the heightmap differ, their |dz|,
                         and their bounding box in world coordinates.
  2. HAZARD-SCOPE TEST   do any differing cells fall inside the DROP FOOTPRINT
                         (twin difference z_off - z_on >= 0.3 m, the definition
                         `labeling/labeler.py` cuts polar_gt out of)?  A change
                         outside the footprint is a PROP CELL; a change inside is
                         a HAZARD CELL and voids the pair under PREREG sec.4.5-2.
  3. SCORESHEET TEST     the criterion the pre-registration actually names:
                         per-frame `polar_gt` byte identity between the two arms,
                         plus the footprint `cells_raw` each arm's labels used.
                         Different scoresheets => the paired recall comparison is
                         not a paired comparison.

Output: G2_ADJUDICATION.csv + a console/markdown table.  Read-only, CPU only.
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
DS = os.path.join(REPO, "dataset")
AUDIT = os.path.join(REPO, "experiments/weekend_0823/cue_audit")
LABELS = os.path.join(AUDIT, "labels")

# stem -> scene -> (split, lineage off round for the drop footprint)
UNITS = [
    ("260823_cueoff",  "scene12", "test",  "260820_boost_e_off"),
    ("260823_cueoff",  "scene17", "train", "260820_boost_h_off"),
    ("260823_cueoff",  "scene20", "train", "260820_boost_e2_off"),
    ("260823_cueoff2", "scene12", "test",  "260820_boost_e2_off"),
    ("260823_cueoff_s20fix", "scene20", "train", "260820_boost_e2_off"),
]
ARMS = ("B1", "B2", "P")
DROP_TAU = 0.30          # labeler.py footprint threshold
# camera strip half-width (PREREG sec.6): y in [-0.9, 0.9]; x in [-d_max, -d_min]
STRIP_Y = 0.9
STRIP_X = {"scene12": (-12.0, -4.0), "scene17": (-12.0, -6.0),
           "scene20": (-9.0, -4.0)}


def hm(stem, arm, scene, split):
    d = os.path.join(round_dir_or_flat(f"{stem}_{arm}"), split, scene)
    p, m = os.path.join(d, "heightmap.npy"), os.path.join(d, "heightmap_meta.json")
    if not (os.path.isfile(p) and os.path.isfile(m)):
        return None, None
    return np.load(p), json.load(open(m))


def hm_lineage(rnd, scene):
    for d in glob.glob(os.path.join(round_dir_or_flat(rnd), "*", scene)):
        p, m = os.path.join(d, "heightmap.npy"), os.path.join(d, "heightmap_meta.json")
        if os.path.isfile(p) and os.path.isfile(m):
            return np.load(p), json.load(open(m))
    return None, None


def labels(lset, stem, arm, scene):
    p = os.path.join(LABELS, f"{lset}__{stem}_{arm}__{scene}.json")
    return json.load(open(p)) if os.path.isfile(p) else None


def world_xy(meta, iy, ix):
    return meta["x0"] + ix * meta["step"], meta["y0"] + iy * meta["step"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(AUDIT, "G2_ADJUDICATION.csv"))
    a = ap.parse_args()
    rows = []
    for stem, scene, split, off_rnd in UNITS:
        za, ma = hm(stem, "A", scene, split)
        if za is None:
            continue
        zoff, moff = hm_lineage(off_rnd, scene)
        foot = None
        if zoff is not None and zoff.shape == za.shape:
            with np.errstate(invalid="ignore"):
                foot = (zoff - za) >= DROP_TAU          # the DROP FOOTPRINT
        sx = STRIP_X.get(scene, (-12.0, -4.0))
        for arm in ARMS:
            zb, mb = hm(stem, arm, scene, split)
            if zb is None:
                continue
            same_bytes = (za.tobytes() == zb.tobytes())
            with np.errstate(invalid="ignore"):
                d = np.abs(np.nan_to_num(za, nan=-999.0) - np.nan_to_num(zb, nan=-999.0))
            mask = d > 0
            n = int(mask.sum())
            rec = dict(stem=stem, scene=scene, pair=f"{arm}_vs_A",
                       hm_bytes_identical=same_bytes, n_cells_diff=n,
                       pct_cells=round(100.0 * n / d.size, 4))
            if n:
                iy, ix = np.nonzero(mask)
                xs = ma["x0"] + ix * ma["step"]
                ys = ma["y0"] + iy * ma["step"]
                rec.update(
                    x_min=round(float(xs.min()), 3), x_max=round(float(xs.max()), 3),
                    y_min=round(float(ys.min()), 3), y_max=round(float(ys.max()), 3),
                    dz_max=round(float(d[mask].max()), 4),
                    dz_median=round(float(np.median(d[mask])), 4))
                if foot is not None:
                    inside = int((mask & foot).sum())
                    rec["cells_in_drop_footprint"] = inside
                    rec["footprint_cells_total"] = int(foot.sum())
                    rec["classification"] = ("HAZARD-CELL" if inside else "PROP-CELL")
                else:
                    rec["cells_in_drop_footprint"] = None
                    rec["classification"] = "PROP-CELL?(no off heightmap)"
                in_strip = int((mask & (np.abs(ma["y0"] + iy * 0 + ys) <= STRIP_Y)
                                & (xs >= sx[0]) & (xs <= sx[1])).sum()) \
                    if False else int(((np.abs(ys) <= STRIP_Y) &
                                       (xs >= sx[0]) & (xs <= sx[1])).sum())
                rec["cells_in_camera_strip"] = in_strip
            else:
                rec.update(x_min=None, x_max=None, y_min=None, y_max=None,
                           dz_max=0.0, dz_median=0.0, cells_in_drop_footprint=0,
                           footprint_cells_total=int(foot.sum()) if foot is not None else None,
                           classification="IDENTICAL", cells_in_camera_strip=0)
            # ---- scoresheet test (the criterion PREREG sec.4.5-2 actually names)
            for lset in ("lineage", "twin"):
                la, lb = labels(lset, stem, "A", scene), labels(lset, stem, arm, scene)
                if la is None or lb is None:
                    rec[f"{lset}_gt_frames_differ"] = None
                    rec[f"{lset}_cellsraw_A"] = rec[f"{lset}_cellsraw_B"] = None
                    continue
                dif = nfr = 0
                sa = sb = 0
                for fid, fa in la["frames"].items():
                    if f"/{scene}/" not in fid or not fid.startswith("on/"):
                        continue
                    fb = lb["frames"].get(fid)
                    if fb is None:
                        continue
                    nfr += 1
                    sa += sum(fa["polar_gt"])
                    sb += sum(fb["polar_gt"])
                    if fa["polar_gt"] != fb["polar_gt"]:
                        dif += 1
                rec[f"{lset}_gt_frames_differ"] = f"{dif}/{nfr}"
                rec[f"{lset}_gtcells_per_frame_A"] = round(sa / nfr, 3) if nfr else None
                rec[f"{lset}_gtcells_per_frame_B"] = round(sb / nfr, 3) if nfr else None
                fa_ = [s for s in la.get("scene_footprint", []) if s.get("arm") == "on"]
                fb_ = [s for s in lb.get("scene_footprint", []) if s.get("arm") == "on"]
                rec[f"{lset}_cellsraw_A"] = fa_[0]["cells_raw"] if fa_ else None
                rec[f"{lset}_cellsraw_B"] = fb_[0]["cells_raw"] if fb_ else None
            rows.append(rec)

    keys = sorted({k for r in rows for k in r})
    order = ["stem", "scene", "pair", "hm_bytes_identical", "n_cells_diff", "pct_cells",
             "x_min", "x_max", "y_min", "y_max", "dz_max", "dz_median",
             "cells_in_drop_footprint", "footprint_cells_total", "cells_in_camera_strip",
             "classification"] + [k for k in keys if k.startswith(("lineage_", "twin_"))]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=order)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in order})

    print(f"{'stem':16s} {'scene':8s} {'pair':8s} {'cells':>6s} {'dzmax':>7s} "
          f"{'x range':>16s} {'y range':>16s} {'inFP':>5s} {'strip':>5s} {'class':12s} "
          f"{'lin gtdiff':>11s} {'lin A/B cells':>15s}")
    for r in rows:
        print(f"{r['stem']:16s} {r['scene']:8s} {r['pair']:8s} {r['n_cells_diff']:6d} "
              f"{r['dz_max']:7.3f} "
              f"[{str(r['x_min']):>6},{str(r['x_max']):>6}] "
              f"[{str(r['y_min']):>6},{str(r['y_max']):>6}] "
              f"{str(r['cells_in_drop_footprint']):>5} {str(r['cells_in_camera_strip']):>5} "
              f"{r['classification']:12s} {str(r.get('lineage_gt_frames_differ')):>11} "
              f"{str(r.get('lineage_gtcells_per_frame_A'))}/{str(r.get('lineage_gtcells_per_frame_B')):>7}"
              f"  raw {r.get('lineage_cellsraw_A')}/{r.get('lineage_cellsraw_B')}")
    print(f"\n-> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
