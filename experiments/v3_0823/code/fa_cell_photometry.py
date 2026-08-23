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
COH_MIN = 0.55              # structure-tensor coherence above which a pixel is
                            # "on a line" rather than on isotropic texture
HORIZ_MAX_DEG = 35.0        # line orientation within this of image-horizontal
                            # (a ground-crossing line reads as near-horizontal)

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


def line_structure(lum):
    """Structure-tensor line mass.

    A drop edge and its surrogates (slab joint, paint stripe, material seam) are
    *coherent oriented* structure; grass / gravel / render noise is isotropic
    texture with equally large raw gradients.  Plain |Sobel| cannot tell them
    apart -- on these renders it flags >50 % of every cell.  Coherence
    (l1-l2)/(l1+l2) of the smoothed structure tensor does.

    Returns (line_mask, gmag) where line_mask is "strong AND coherent AND
    near-image-horizontal", i.e. a candidate ground-crossing line pixel.
    """
    import cv2
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    gmag = np.hypot(gx, gy)
    k = (5, 5)
    jxx = cv2.boxFilter(gx * gx, -1, k)
    jyy = cv2.boxFilter(gy * gy, -1, k)
    jxy = cv2.boxFilter(gx * gy, -1, k)
    tr = jxx + jyy
    det = jxx * jyy - jxy * jxy
    disc = np.sqrt(np.maximum(tr * tr - 4.0 * det, 0.0))
    coh = np.where(tr > 1e-6, disc / np.maximum(tr, 1e-6), 0.0)
    # dominant gradient orientation; the LINE runs perpendicular to it
    theta_g = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)          # grad dir
    line_ang = np.degrees(np.abs(np.arctan2(np.cos(theta_g), -np.sin(theta_g))))
    line_ang = np.minimum(line_ang, 180.0 - line_ang)          # 0 = horizontal
    strong = gmag > max(8.0, float(np.percentile(gmag, 90)))
    return strong & (coh > COH_MIN) & (line_ang < HORIZ_MAX_DEG), gmag


def one(args):
    fid, rec = args
    cam = rec["cam"]
    dep = np.load(rec["depth"]).astype(np.float64)
    import cv2
    img = cv2.imread(rec["rgb"], cv2.IMREAD_COLOR)          # BGR uint8
    if img is None:
        return []
    # INTER_AREA (proper low-pass) -- strided subsampling aliases the render's
    # high-frequency ground texture into fake "edges".
    h, w = img.shape[0] // DS, img.shape[1] // DS
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    lum = (0.114 * img[..., 0] + 0.587 * img[..., 1] + 0.299 * img[..., 2]).astype(np.float32)
    line_mask, gmag = line_structure(lum)

    cell, hgt, good = cell_of_pixels(dep, cam)
    if cell.shape != lum.shape:                             # defensive crop
        ch = min(cell.shape[0], lum.shape[0]); cw = min(cell.shape[1], lum.shape[1])
        cell, hgt, good = cell[:ch, :cw], hgt[:ch, :cw], good[:ch, :cw]
        lum, gmag = lum[:ch, :cw], gmag[:ch, :cw]
        line_mask = line_mask[:ch, :cw]

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
            r = dict(lum_mean=float(v.mean()), lum_median=float(np.median(v)),
                     lum_p10=float(np.percentile(v, 10)), lum_std=float(v.std()),
                     line_frac=float(line_mask[m].mean()),
                     grad_p90=float(np.percentile(gmag[m], 90)))
        else:
            r = dict(lum_mean=float("nan"), lum_median=float("nan"),
                     lum_p10=float("nan"), lum_std=float("nan"),
                     line_frac=float("nan"), grad_p90=float("nan"))
        if ng:
            r["lum_median_ground"] = float(np.median(lum[mg]))
            r["line_frac_ground"] = float(line_mask[mg].mean())
        else:
            r["lum_median_ground"] = float("nan")
            r["line_frac_ground"] = float("nan")
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
