#!/usr/bin/env python3
"""
CPU-2 / FA CENSUS  --  step 2: per-(frame, cell) photometry for the 816 test-core
frames.  This is the measurement substrate for the 조명형 (lighting) and the
off-arm 대리선형 (surrogate-line) family heuristics.

Method (CPU only, no model, no GPU)
-----------------------------------
Reuses the *labelling* geometry verbatim -- `labeler.unproject` and the sector /
band arithmetic of `labeler.polar_cells` -- so a pixel is assigned to exactly the
cell the GT labeller would assign its ground point to.

Key identity that removes the need for the camera world position: `polar_cells`
only ever uses `XX - eye[0]`, `YY - eye[1]`, and `unproject` returns
`eye + d * dirs`.  Therefore the camera-relative offset `d * dirs` is sufficient
and exact; the manifest's `cam` dict (which drops `eye`) is enough.
Camera height convention verified empirically: bottom-centre pixels reconstruct
to rel_z = -h_rel, i.e. `height_above_ground = rel_z + h_rel`.

Per (frame, cell) it records luminance (Rec.601 luma on sRGB 0..255) and a Sobel
"edge mass" over the cell's image region, plus the ground-restricted variants.

Output: experiments/v3_0823/cell_photometry.csv  (816 * 20 = 16320 rows)
"""
import csv
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code/labeling"))
import labeler as L  # noqa: E402

OUT = os.path.join(ROOT, "experiments/v3_0823")
MANIFEST = os.path.join(ROOT, "experiments/dayrun_0820/dataset_manifest_v2_full.json")
GRIDSPEC = os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")

DS = 4                      # depth/image downsample, same factor labeler.py uses
GROUND_BAND_M = 0.30        # |height above local ground| accepted as "ground"
EDGE_THRESH = 24.0          # Sobel |grad| (luma/px, at DS=4) counted as an edge px

GRID = json.load(open(GRIDSPEC))
NS, NB = GRID["n_sectors"], GRID["n_bands"]
CELL_IDS = [f"{s}{b}" for b in GRID["band_names"] for s in GRID["sector_names"]]


def cell_of_pixels(dep, cam):
    """(cell_idx per pixel, height_above_ground per pixel, valid mask) at DS."""
    P, good = L.unproject(dep, [0.0, 0.0, 0.0], cam, DS)   # eye=origin -> camera-relative
    dx, dy, dz = P[..., 0], P[..., 1], P[..., 2]
    yaw = math.radians(cam["yaw"])
    cy, sy = math.cos(yaw), math.sin(yaw)
    xc, yc = dx * cy + dy * sy, -dx * sy + dy * cy
    az = np.degrees(np.arctan2(yc, xc))
    rng = np.hypot(xc, yc)
    asc = np.asarray(GRID["sector_edges_deg"][::-1])
    k = np.searchsorted(asc, az, side="right") - 1
    b = np.searchsorted(np.asarray(GRID["band_edges_m"]), rng, side="right") - 1
    ok = good & (k >= 0) & (k < NS) & (b >= 0) & (b < NB)
    cell = np.where(ok, b * NS + (NS - 1 - k), -1)
    return cell, dz + cam["h_rel"], good


def one(args):
    fid, rec = args
    cam = rec["cam"]
    dep = np.load(rec["depth"]).astype(np.float64)
    import cv2
    img = cv2.imread(rec["rgb"], cv2.IMREAD_COLOR)          # BGR uint8
    if img is None:
        return []
    img = img[::DS, ::DS]
    lum = (0.114 * img[..., 0] + 0.587 * img[..., 1] + 0.299 * img[..., 2]).astype(np.float32)
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    gmag = np.hypot(gx, gy)

    cell, hgt, good = cell_of_pixels(dep, cam)
    if cell.shape != lum.shape:                             # defensive crop
        h = min(cell.shape[0], lum.shape[0]); w = min(cell.shape[1], lum.shape[1])
        cell, hgt, good = cell[:h, :w], hgt[:h, :w], good[:h, :w]
        lum, gmag = lum[:h, :w], gmag[:h, :w]

    ground = good & (np.abs(hgt) < GROUND_BAND_M)
    fr_g = lum[ground & (cell >= 0)]
    frame_lum_med = float(np.median(fr_g)) if fr_g.size else float("nan")
    fr_all = lum[good]
    frame_lum_med_all = float(np.median(fr_all)) if fr_all.size else float("nan")

    rows = []
    for ci, cid in enumerate(CELL_IDS):
        m = cell == ci
        n = int(m.sum())
        mg = m & ground
        ng = int(mg.sum())
        if n:
            v = lum[m]
            g = gmag[m]
            r = dict(lum_mean=float(v.mean()), lum_median=float(np.median(v)),
                     lum_p10=float(np.percentile(v, 10)), lum_std=float(v.std()),
                     edge_frac=float((g > EDGE_THRESH).mean()),
                     grad_p90=float(np.percentile(g, 90)))
        else:
            r = dict(lum_mean=float("nan"), lum_median=float("nan"),
                     lum_p10=float("nan"), lum_std=float("nan"),
                     edge_frac=float("nan"), grad_p90=float("nan"))
        if ng:
            vg = lum[mg]
            gg = gmag[mg]
            r["lum_median_ground"] = float(np.median(vg))
            r["edge_frac_ground"] = float((gg > EDGE_THRESH).mean())
        else:
            r["lum_median_ground"] = float("nan")
            r["edge_frac_ground"] = float("nan")
        rows.append(dict(frame_id=fid, scene_id=rec["scene_id"],
                         toggle_state=rec["toggle_state"], tier=rec.get("tier", ""),
                         cell=cid, cell_idx=ci, n_px=n, n_px_ground=ng,
                         frame_lum_median=frame_lum_med,
                         frame_lum_median_all=frame_lum_med_all,
                         **{k: (round(x, 4) if x == x else "") for k, x in r.items()}))
    return rows


def main():
    man = {f["frame_id"]: f for f in json.load(open(MANIFEST))["frames"]}
    # test-core 816 = the frame_ids present in any run's per_frame.csv
    pf = os.path.join(ROOT, "experiments/dayrun_0820/runs/v2/rgb_s42/eval_test/per_frame.csv")
    fids = [r["frame_id"] for r in csv.DictReader(open(pf))]
    assert len(fids) == 816, len(fids)
    tasks = [(f, man[f]) for f in fids]

    out = []
    with Pool(12) as p:
        for i, rows in enumerate(p.imap_unordered(one, tasks, chunksize=4)):
            out.extend(rows)
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(tasks)}", flush=True)

    out.sort(key=lambda r: (r["frame_id"], r["cell_idx"]))
    with open(os.path.join(OUT, "cell_photometry.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows -> {OUT}/cell_photometry.csv")


if __name__ == "__main__":
    sys.exit(main())
