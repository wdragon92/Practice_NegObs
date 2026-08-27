"""F7b — CALIBRATION FOR THE H-PAIR PIXEL DIFF (D35 / R1-F7).

The raw |on - off| number for a strict-H pair is meaningless without two references:

  (1) RENDERER NOISE FLOOR.  sceneN3's `keep_dressing` off arm is *geometrically
      identical* to its on arm (`ctrl_dressing/CTRL_TABLE.md`: max |Δheightmap| =
      0.000000 m, NaN pattern equal).  Any pixel difference between those two
      renders is path-tracer / denoiser nondeterminism, not scene content.

  (2) HAZARD-ONLY DIFF.  sceneC2's `keep_dressing` off arm removes the hazard
      geometry and nothing else.  Its diff is what "delete the drop, keep the
      dressing" costs in pixels.

Both are compared against the ordinary main-round on/off diff of the same scenes,
which — like scene14's and scene15's — deletes the hazard AND everything the
scene builder puts inside the `hazard_stairs` branch.

Outputs: f7b_noisefloor.json (consumed by the F7 report)
"""
import json
import os
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
import sys
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DS = os.path.join(REPO, "dataset")
MANIFEST = os.path.join(REPO, "experiments/dayrun_0820/dataset_manifest_v2_full.json")
THRESH = 2
THRESH_HI = [8, 32]

M = json.load(open(MANIFEST))
by_id = {f["frame_id"]: f for f in M["frames"]}
ctrl = json.load(open(os.path.join(round_dir_or_flat("260820_ctrloff"), "manifest.json")))


def diff_stats(pa, pb):
    a = np.asarray(Image.open(pa).convert("RGB"), np.int16)
    b = np.asarray(Image.open(pb).convert("RGB"), np.int16)
    d = np.abs(a - b).max(axis=2)
    m = d >= THRESH
    n = int(m.sum())
    tot = d.size
    return {"n_diff_px": n, "frac_diff": n / tot, "max_diff": int(d.max()),
            "mean_diff_over_changed": float(d[m].mean()) if n else 0.0,
            **{f"n_diff_px_ge{t}": int((d >= t).sum()) for t in THRESH_HI}}


def summarise(rows, name):
    if not rows:
        return None
    k = lambda key: np.array([r[key] for r in rows], float)  # noqa: E731
    return {"name": name, "n_pairs": len(rows),
            "frac_diff_median": float(np.median(k("frac_diff"))),
            "frac_diff_mean": float(np.mean(k("frac_diff"))),
            "frac_diff_max": float(np.max(k("frac_diff"))),
            "n_diff_px_median": float(np.median(k("n_diff_px"))),
            "n_diff_px_ge8_median": float(np.median(k("n_diff_px_ge8"))),
            "n_diff_px_ge32_median": float(np.median(k("n_diff_px_ge32"))),
            "mean_diff_over_changed_median": float(np.median(k("mean_diff_over_changed"))),
            "max_diff_median": float(np.median(k("max_diff")))}


# ctrloff manifest -> map (scene, cut) -> path
ctrl_path = {}
for fr in ctrl.get("frames", ctrl if isinstance(ctrl, list) else []):
    if isinstance(fr, dict) and "rgb" in fr:
        p = fr["rgb"]
        sc = fr.get("scene_id") or os.path.basename(os.path.dirname(p))
        ctrl_path[(sc, os.path.basename(p))] = p
if not ctrl_path:                      # fall back to a directory walk
    for root, _d, files in os.walk(round_dir_or_flat("260820_ctrloff")):
        for fn in files:
            if fn.endswith(".png"):
                ctrl_path[(os.path.basename(root), fn)] = os.path.join(root, fn)

res = {"threshold_255": THRESH, "groups": {}, "provenance": {
    "noise_floor": "dataset/v2_corpus/260819_main_on/sceneN3 vs dataset/v2_probes/260820_ctrloff/sceneN3 "
                   "(keep_dressing; heightmap max|Δ| = 0.000000 m per ctrl_dressing/CTRL_TABLE.md)",
    "hazard_only": "dataset/v2_corpus/260819_main_on/sceneC2 vs dataset/v2_probes/260820_ctrloff/sceneC2 (keep_dressing)",
    "full_toggle": "dataset/v2_corpus/260819_main_on/<scene> vs dataset/v2_corpus/260819_main_off/<scene> "
                   "(the ordinary corpus twin: hazard geometry AND everything else inside "
                   "the scene builder's hazard_stairs branch)",
}}

for sc, label in (("sceneN3", "noise_floor__N3_on_vs_keepdressing_off"),
                  ("sceneC2", "hazard_only__C2_on_vs_keepdressing_off")):
    rows = []
    for (s, cut), p in sorted(ctrl_path.items()):
        if s != sc:
            continue
        on = by_id.get(f"on/{sc}/{cut}")
        if on is None or not os.path.exists(on["rgb"]):
            continue
        rows.append(diff_stats(on["rgb"], p))
    res["groups"][label] = summarise(rows, label)

for sc in ("sceneN3", "sceneC2", "scene14", "scene15"):
    rows = []
    for f in M["frames"]:
        if f["scene_id"] != sc or f["toggle_state"] != "on":
            continue
        g = by_id.get(f["frame_id"].replace("on/", "off/", 1))
        if g is None or "260819_main" not in f["rgb"]:
            continue
        if not (os.path.exists(f["rgb"]) and os.path.exists(g["rgb"])):
            continue
        rows.append(diff_stats(f["rgb"], g["rgb"]))
    res["groups"][f"full_toggle__{sc}_main_round"] = summarise(rows, f"full_toggle__{sc}")

# scene14/15: does the diff depend on the hazard being inside the grid?
for sc in ("scene14", "scene15"):
    for tier in ("H", "none_in_fov", "V"):
        rows = []
        for f in M["frames"]:
            if f["scene_id"] != sc or f["tier"] != tier:
                continue
            g = by_id.get(f["frame_id"].replace("on/", "off/", 1))
            if g is None or not (os.path.exists(f["rgb"]) and os.path.exists(g["rgb"])):
                continue
            rows.append(diff_stats(f["rgb"], g["rgb"]))
        if rows:
            res["groups"][f"tiercheck__{sc}__{tier}"] = summarise(rows, f"{sc}/{tier}")

json.dump(res, open(os.path.join(OUT, "f7b_noisefloor.json"), "w"), indent=1)
for k, v in res["groups"].items():
    if v:
        print(f"{k:46} n={v['n_pairs']:4d}  frac_diff med={v['frac_diff_median']:.5f}  "
              f"px>=8 med={v['n_diff_px_ge8_median']:9.0f}  px>=32 med={v['n_diff_px_ge32_median']:9.0f}  "
              f"meanmag={v['mean_diff_over_changed_median']:6.2f}")
