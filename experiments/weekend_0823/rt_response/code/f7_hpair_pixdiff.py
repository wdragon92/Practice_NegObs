"""F7 — STRICT-H TWIN PIXEL-DIFFERENCE AUDIT (D35 / R1-F7).

strict-H is a GEOMETRIC definition: `int_px == 0 and edge_vis == 0`, i.e. the hazard
prism re-projects to zero pixels.  It does not forbid the hazard from changing the
image through shadow, ambient occlusion, GI bounce, terrain-mesh seams or
sub-threshold silhouettes.  This script measures what is actually left.

For each of the 96 test strict-H twin pairs (all pose-exact, verified here):
    d(x,y) = max_c | on_c(x,y) - off_c(x,y) |     on the native 1920x1080 RGB
and reports the count / fraction of pixels above 2/255, where those pixels sit
relative to (a) the GT-positive polar wedges projected to the image, (b) the amodal
hazard silhouette (the prism projected ignoring occlusion), (c) the whole 20-cell
grid footprint, and how the residual correlates with each RGB run's twin delta.

Outputs: f7_hpair_pixdiff.json, F7_HPAIR_PIXDIFF.md, panels/*.png
"""
import json
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code/labeling"))
import labeler as LB  # noqa: E402  (canonical camera model — imported, never re-derived)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_rt import MODELS, SEEDS, load_twin  # noqa: E402

MANIFEST = os.path.join(REPO, "experiments/dayrun_0820/dataset_manifest_v2_full.json")
SPLIT = os.path.join(REPO, "experiments/dayrun_0820/split_v2_full.json")
GRID = os.path.join(REPO, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")
AMODAL_DIR = os.path.join(REPO, "experiments/dayrun_0820/annotations/amodal")
BBOX = os.path.join(AMODAL_DIR, "bboxes.json")

# The brief asked for ~2/255.  f7b_noisefloor.py shows that level is DOMINATED by
# path-tracer / denoiser nondeterminism (sceneN3's geometrically-identical render pair
# flips 44 % of pixels at >= 2/255), so every statistic is reported at three levels and
# the >= 32/255 level is the one that carries scene content (N3 floor: 50 px).
THRESH = 2
THRESH_HI = [8, 32]
LEVELS = [2, 8, 32]
W, H = LB.W_IMG, LB.H_IMG
ARC = 25
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov", "ground_z")

grid = json.load(open(GRID))
M = json.load(open(MANIFEST))
by_id = {f["frame_id"]: f for f in M["frames"]}
test_scenes = set(json.load(open(SPLIT))["test"])
bb = json.load(open(BBOX))["frames"]

pairs = [f for f in M["frames"] if f["tier"] == "H" and f["scene_id"] in test_scenes]
pairs.sort(key=lambda f: f["frame_id"])
assert len(pairs) == 96, len(pairs)


# ----------------------------------------------------------------- wedge rasteriser
def wedge_mask(cells, cam):
    """Binary 1080x1920 mask of the ground wedges of `cells`, projected with the
    frame's own camera (labeler.project / labeler.cam_basis).  Eye at the origin of
    its own ground frame (common.synth_eye convention): eye=(0,0,h_rel), ground z=0."""
    eye = np.array([0.0, 0.0, float(cam["h_rel"])])
    yaw = float(cam["yaw"])
    camd = {"yaw": yaw, "pitch": float(cam["pitch"]), "roll": float(cam["roll"]),
            "hfov": float(cam["hfov"])}
    asc = np.asarray(grid["sector_edges_deg"], float)[::-1]
    ns = grid["n_sectors"]
    edges = np.asarray(grid["band_edges_m"], float)
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    drew = 0
    for c in cells:
        b, s = c // ns, c % ns
        az_lo, az_hi = asc[ns - 1 - s], asc[ns - s]
        az = np.radians(np.linspace(az_lo, az_hi, ARC) + yaw)   # camera az -> world az
        r_lo, r_hi = max(edges[b], 0.10), edges[b + 1]
        ring = np.concatenate([
            np.stack([r_hi * np.cos(az), r_hi * np.sin(az)], 1),
            np.stack([r_lo * np.cos(az[::-1]), r_lo * np.sin(az[::-1])], 1)])
        pts = np.concatenate([ring, np.zeros((len(ring), 1))], 1)
        px, py, zc, _ = LB.project(pts, eye, camd)
        ok = zc > 0.05
        if ok.sum() < 3:
            continue
        poly = [(float(x), float(y)) for x, y in zip(px[ok], py[ok])]
        dr.polygon(poly, fill=255)
        drew += 1
    return np.asarray(img) > 0, drew


def amodal_mask(frame_id):
    rec = bb.get(frame_id, {})
    name = rec.get("mask")
    if not name:
        return np.zeros((H, W), bool)
    p = os.path.join(AMODAL_DIR, name)
    if not os.path.exists(p):
        return np.zeros((H, W), bool)
    m = Image.open(p).convert("L").resize((W, H), Image.NEAREST)
    return np.asarray(m) > 0


# ----------------------------------------------------------------- main loop
per_pair = []
for i, f in enumerate(pairs):
    off_id = f["frame_id"].replace("on/", "off/", 1)
    g = by_id[off_id]
    assert all(abs(float(f["cam"][k]) - float(g["cam"][k])) <= 1e-6 for k in POSE_KEYS), f["frame_id"]
    a = np.asarray(Image.open(f["rgb"]).convert("RGB"), np.int16)
    b = np.asarray(Image.open(g["rgb"]).convert("RGB"), np.int16)
    assert a.shape == (H, W, 3), a.shape
    d = np.abs(a - b).max(axis=2)                # per-pixel max-channel absolute diff
    mask = d >= THRESH
    n = int(mask.sum())
    gt_cells = [c for c, v in enumerate(f["polar_gt"]) if v]
    wm_gt, n_drawn = wedge_mask(gt_cells, f["cam"])
    wm_all, _ = wedge_mask(range(grid["n_bands"] * grid["n_sectors"]), f["cam"])
    am = amodal_mask(f["frame_id"])
    tot = W * H
    rec = {
        "frame_id": f["frame_id"], "scene_id": f["scene_id"], "cond": f["cond"],
        "cam_d": f["cam"]["d"], "cam_h_rel": f["cam"]["h_rel"],
        "n_gt_cells": len(gt_cells), "n_wedges_drawn": n_drawn,
        "n_diff_px": n, "frac_diff": n / tot,
        "max_diff": int(d.max()), "mean_diff_over_changed": float(d[mask].mean()) if n else 0.0,
        "sum_abs_diff": int(d.sum()),
        **{f"n_diff_px_ge{t}": int((d >= t).sum()) for t in THRESH_HI},
        "n_px_gt_wedge": int(wm_gt.sum()), "n_px_amodal": int(am.sum()),
        "n_diff_in_gt_wedge": int((mask & wm_gt).sum()),
        "n_diff_in_grid": int((mask & wm_all).sum()),
        "n_diff_in_amodal": int((mask & am).sum()),
        "frac_diff_in_gt_wedge": float((mask & wm_gt).sum() / n) if n else float("nan"),
        "frac_diff_in_grid": float((mask & wm_all).sum() / n) if n else float("nan"),
        "frac_diff_in_amodal": float((mask & am).sum() / n) if n else float("nan"),
        "amodal_coverage_by_diff": float((mask & am).sum() / am.sum()) if am.sum() else float("nan"),
        "gt_wedge_coverage_by_diff": float((mask & wm_gt).sum() / wm_gt.sum()) if wm_gt.sum() else float("nan"),
    }
    # the same spatial accounting at every level, so the noise-dominated level 2 can be
    # replaced by the content-carrying level 32 without re-reading the corpus
    for lv in LEVELS:
        mk = d >= lv
        nk = int(mk.sum())
        rec[f"L{lv}"] = {
            "n_diff_px": nk, "frac_diff": nk / tot,
            "n_in_gt_wedge": int((mk & wm_gt).sum()),
            "n_in_grid": int((mk & wm_all).sum()),
            "n_in_amodal": int((mk & am).sum()),
            "frac_in_gt_wedge": float((mk & wm_gt).sum() / nk) if nk else float("nan"),
            "frac_in_grid": float((mk & wm_all).sum() / nk) if nk else float("nan"),
            "frac_in_amodal": float((mk & am).sum() / nk) if nk else float("nan"),
            "amodal_coverage": float((mk & am).sum() / am.sum()) if am.sum() else float("nan"),
            "gt_wedge_coverage": float((mk & wm_gt).sum() / wm_gt.sum()) if wm_gt.sum() else float("nan"),
        }
    # vertical position of the residual, relative to the image and to the GT wedge
    if n:
        ys, xs = np.nonzero(mask)
        rec["diff_row_median"] = float(np.median(ys))
        rec["diff_row_p10"] = float(np.percentile(ys, 10))
        rec["diff_row_p90"] = float(np.percentile(ys, 90))
        if wm_gt.sum():
            wy, _wx = np.nonzero(wm_gt)
            rec["gt_wedge_row_median"] = float(np.median(wy))
    per_pair.append(rec)
    if (i + 1) % 24 == 0:
        print(f"  ... {i+1}/96", flush=True)

# ----------------------------------------------------------------- aggregation
def agg(sel):
    if not sel:
        return {}
    fr = np.array([r["frac_diff"] for r in sel])
    npx = np.array([r["n_diff_px"] for r in sel], float)
    return {
        "n_pairs": len(sel),
        "n_pairs_zero_diff": int(sum(1 for r in sel if r["n_diff_px"] == 0)),
        "n_pairs_lt_100px": int(sum(1 for r in sel if r["n_diff_px"] < 100)),
        "frac_diff_mean": float(fr.mean()), "frac_diff_median": float(np.median(fr)),
        "frac_diff_min": float(fr.min()), "frac_diff_max": float(fr.max()),
        "n_diff_px_median": float(np.median(npx)),
        "n_diff_px_min": float(npx.min()), "n_diff_px_max": float(npx.max()),
        "max_diff_median": float(np.median([r["max_diff"] for r in sel])),
        "mean_diff_over_changed_median": float(np.median([r["mean_diff_over_changed"] for r in sel])),
        "n_diff_px_ge8_median": float(np.median([r["n_diff_px_ge8"] for r in sel])),
        "n_diff_px_ge32_median": float(np.median([r["n_diff_px_ge32"] for r in sel])),
        "frac_diff_in_gt_wedge_mean": float(np.nanmean([r["frac_diff_in_gt_wedge"] for r in sel])),
        "frac_diff_in_grid_mean": float(np.nanmean([r["frac_diff_in_grid"] for r in sel])),
        "frac_diff_in_amodal_mean": float(np.nanmean([r["frac_diff_in_amodal"] for r in sel])),
        "amodal_coverage_by_diff_mean": float(np.nanmean([r["amodal_coverage_by_diff"] for r in sel])),
        "gt_wedge_coverage_by_diff_mean": float(np.nanmean([r["gt_wedge_coverage_by_diff"] for r in sel])),
        "gt_wedge_px_median": float(np.median([r["n_px_gt_wedge"] for r in sel])),
        "amodal_px_median": float(np.median([r["n_px_amodal"] for r in sel])),
        "levels": {str(lv): {
            "n_diff_px_median": float(np.median([r[f"L{lv}"]["n_diff_px"] for r in sel])),
            "n_diff_px_p10": float(np.percentile([r[f"L{lv}"]["n_diff_px"] for r in sel], 10)),
            "n_diff_px_p90": float(np.percentile([r[f"L{lv}"]["n_diff_px"] for r in sel], 90)),
            "n_diff_px_min": float(np.min([r[f"L{lv}"]["n_diff_px"] for r in sel])),
            "frac_diff_median": float(np.median([r[f"L{lv}"]["frac_diff"] for r in sel])),
            "frac_in_gt_wedge_mean": float(np.nanmean([r[f"L{lv}"]["frac_in_gt_wedge"] for r in sel])),
            "frac_in_grid_mean": float(np.nanmean([r[f"L{lv}"]["frac_in_grid"] for r in sel])),
            "frac_in_amodal_mean": float(np.nanmean([r[f"L{lv}"]["frac_in_amodal"] for r in sel])),
            "amodal_coverage_mean": float(np.nanmean([r[f"L{lv}"]["amodal_coverage"] for r in sel])),
            "gt_wedge_coverage_mean": float(np.nanmean([r[f"L{lv}"]["gt_wedge_coverage"] for r in sel])),
        } for lv in LEVELS},
    }


res = {"threshold_255": THRESH, "provenance": {
    "rgb": "dataset_manifest_v2_full.json frames[*].rgb (native 1920x1080 PNG, both arms)",
    "pairing": "frame_id on/-> off/, all 96 verified pose-exact to 1e-6 on "
               "(d,h_rel,yaw,pitch,roll,hfov,ground_z)",
    "camera_model": "experiments/mainrun_0819/code/labeling/labeler.py (imported)",
    "grid": "gridspec_v1.json, eye=(0,0,h_rel) ground z=0 (common.synth_eye convention)",
    "amodal": "annotations/amodal/<stem>.png, 960x540 nearest-upsampled to 1920x1080",
    "diff": "d = max_c |on_c - off_c|, changed pixel = d >= 2",
}, "all": agg(per_pair),
    "by_scene": {sc: agg([r for r in per_pair if r["scene_id"] == sc])
                 for sc in ("scene14", "scene15")},
    "by_scene_cond": {}, "per_pair": per_pair}

for sc in ("scene14", "scene15"):
    for cond in sorted({r["cond"] for r in per_pair if r["scene_id"] == sc}):
        res["by_scene_cond"][f"{sc}/{cond}"] = agg(
            [r for r in per_pair if r["scene_id"] == sc and r["cond"] == cond])

# ---- consistency gate + residual-vs-delta coupling ------------------------------
diffmap = {r["frame_id"]: r for r in per_pair}
res["coupling"] = {}
for m in MODELS:
    for s in SEEDS:
        run = f"{m}_s{s}"
        tw = [t for t in load_twin(run) if t["kept"] and t["tier"] == "H"]
        # twin_pairs.csv keys on (scene_id, cut) -> rebuild the on-arm frame_id
        rows = []
        for t in tw:
            fid = f"on/{t['scene_id']}/{t['cut']}"
            if fid in diffmap:
                rows.append((diffmap[fid], t))
        if not rows:
            continue
        x = np.array([np.log10(max(r["L32"]["n_diff_px"], 1)) for r, _ in rows])
        y = np.array([t["delta_score"] for _, t in rows])
        def spearman(u, v):
            ru = np.argsort(np.argsort(u)).astype(float)
            rv = np.argsort(np.argsort(v)).astype(float)
            ru -= ru.mean(); rv -= rv.mean()
            den = math.sqrt((ru ** 2).sum() * (rv ** 2).sum())
            return float((ru * rv).sum() / den) if den else float("nan")
        entry = {"n": len(rows), "spearman_logL32px_vs_delta": spearman(x, y)}
        for sc in ("scene14", "scene15"):
            sub = [(r, t) for r, t in rows if r["scene_id"] == sc]
            if len(sub) > 2:
                entry[f"spearman_{sc}"] = spearman(
                    np.array([np.log10(max(r["L32"]["n_diff_px"], 1)) for r, _ in sub]),
                    np.array([t["delta_score"] for _, t in sub]))
        # consistency gate: a pair with no residual at all must have delta 0
        for lv, name in ((2, "L2"), (32, "L32")):
            zero = [(r, t) for r, t in rows if r[f"L{lv}"]["n_diff_px"] == 0]
            entry[f"n_zero_diff_pairs_{name}"] = len(zero)
            entry[f"max_abs_delta_on_zero_diff_{name}"] = (
                float(max(abs(t["delta_score"]) for _, t in zero)) if zero else None)
        # mean delta on the quietest vs loudest residual tercile (within scene14)
        s14 = sorted([(r, t) for r, t in rows if r["scene_id"] == "scene14"],
                     key=lambda rt: rt[0]["L32"]["n_diff_px"])
        if len(s14) >= 9:
            k = len(s14) // 3
            entry["s14_delta_mean_quiet_tercile"] = float(np.mean([t["delta_score"] for _, t in s14[:k]]))
            entry["s14_delta_mean_loud_tercile"] = float(np.mean([t["delta_score"] for _, t in s14[-k:]]))
        res["coupling"][run] = entry

json.dump(res, open(os.path.join(OUT, "f7_hpair_pixdiff.json"), "w"), indent=1)
print("[f7] json written")
