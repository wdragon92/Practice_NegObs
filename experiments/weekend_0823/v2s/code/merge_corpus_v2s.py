#!/usr/bin/env python3
"""V2S variant of experiments/dayrun_0820/code/merge_corpus.py -- SAME PATTERN, new paths.

The original is left untouched (PS 12.6 isolation rule); this file only swaps the
four input pairs for their gridspec_v2s relabels, writes into
experiments/weekend_0823/v2s/, and stamps the V2S grid identity in `meta`.

frame_id uniqueness (unchanged, D24): boost rounds share filenames across the h/e
lists (same seed, same scene), so the file TOKEN gains '::<round>'.  Parsers that
split('/', 2) still get [arm, scene, file-with-suffix]; twin pairing keys
(scene, file-token) stay distinct per round while on/off of the SAME round pair up.
Main-pair frames keep their bare ids -- which is also what makes the V1<->V2S
invariant gate a straight key-by-key comparison against labels_v1_full.json.

Provenance is READ BACK from the labels the labeler wrote (n_cells / grid_version /
gt_source), never re-declared as a literal: a mismatch between the labels and this
file is a failure, not something to paper over.
"""
import json
import os

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V2S = os.path.join(REPO, "experiments/weekend_0823/v2s")

OUT_M = os.path.join(V2S, "dataset_manifest_v2s_full.json")
OUT_L = os.path.join(V2S, "annotations/labels_v2s.json")
PAIRS = [  # (manifest, labels, suffix or None) -- the four rounds of the V1 corpus
    (f"{V2S}/manifest_v2s_main.json",     f"{V2S}/annotations/labels_v2s_main.json",     None),
    (f"{V2S}/manifest_v2s_boost_h.json",  f"{V2S}/annotations/labels_v2s_boost_h.json",  "boost_h"),
    (f"{V2S}/manifest_v2s_boost_e.json",  f"{V2S}/annotations/labels_v2s_boost_e.json",  "boost_e"),
    (f"{V2S}/manifest_v2s_boost_e2.json", f"{V2S}/annotations/labels_v2s_boost_e2.json", "boost_e2"),
]

frames, lab_frames, lab_scene_fp = [], {}, []
grid = None
for mp, lp, suf in PAIRS:
    M = json.load(open(mp))
    L = json.load(open(lp))
    if grid is None:
        grid = L.get("grid")
    elif L.get("grid") != grid:
        raise SystemExit(f"[merge] {lp} was labelled on a DIFFERENT gridspec than the first pair")
    for f in M["frames"]:
        if suf:
            f = dict(f)
            f["frame_id"] = f["frame_id"] + "::" + suf
        frames.append(f)
    for k, v in L["frames"].items():
        lab_frames[k + ("::" + suf if suf else "")] = v
    for s in L.get("scene_footprint", []):
        s = dict(s)
        s["round_tag"] = suf or "main"
        lab_scene_fp.append(s)

ids = [f["frame_id"] for f in frames]
assert len(ids) == len(set(ids)), f"dup frame_ids: {len(ids) - len(set(ids))}"
n_cells = int(grid["n_bands"]) * int(grid["n_sectors"])
assert grid["version"] == "PROVISIONAL-GRID-V2S" and n_cells == 40, grid["version"]
bad = [f["frame_id"] for f in frames if len(f["polar_gt"]) != n_cells]
assert not bad, f"{len(bad)} frame(s) carry a polar_gt of length != {n_cells}: {bad[:3]}"

base_meta = json.load(open(PAIRS[0][0]))["meta"]
meta = dict(base_meta)  # inherit every key gates/consumers expect (tier_source, rounds, ...)
meta.update(created="2026-08-23", grid_version=grid["version"], n_cells=n_cells,
            gt_source=base_meta["gt_source"],
            note="V2S TEST TRACK (PS 12.6): mainrun pair + boost_h/e/e2 pairs relabelled on "
                 "gridspec_v2s.json (10 sectors x 4 bands = 40 cells); boost file tokens "
                 "'::<round>' (D24). Frame set and frame ids are identical to "
                 "dayrun_0820/dataset_manifest_v2_full.json -- only polar_gt widens 20 -> 40.")
json.dump({"meta": meta, "frames": frames}, open(OUT_M, "w"))
json.dump({"grid": grid, "meta": meta, "frames": lab_frames,
           "scene_footprint": lab_scene_fp}, open(OUT_L, "w"))
on = sum(1 for f in frames if f["toggle_state"] == "on")
print(f"[merge] {len(frames)} frames (on {on} / off {len(frames) - on}) "
      f"x {n_cells} cells -> {OUT_M}")
print(f"[merge] labels -> {OUT_L}")
