#!/usr/bin/env python3
"""Merge the mainrun pair + boost pairs into one corpus (manifest + labels).

frame_id uniqueness: boost rounds share filenames across h/e lists (same seed,
same scene) — D24. The file TOKEN gains '::<round>' so parsers that
split('/', 2) still get [arm, scene, file-with-suffix] and twin pairing keys
(scene, file-token) stay distinct per round while on/off of the SAME round pair
up (both carry the same suffix).  Main-pair frames keep their bare ids (all
downstream mainrun artifacts remain valid).
"""
import json, sys

OUT_M = "experiments/dayrun_0820/dataset_manifest_v2_full.json"
OUT_L = "experiments/dayrun_0820/annotations/labels_v1_full.json"
PAIRS = [  # (manifest, labels, suffix or None)
    ("experiments/dayrun_0820/dataset_manifest_v2.json",
     "experiments/dayrun_0820/annotations/labels_v1.json", None),
    ("experiments/dayrun_0820/manifest_boost_h.json",
     "experiments/dayrun_0820/annotations/labels_boost_h.json", "boost_h"),
    ("experiments/dayrun_0820/manifest_boost_e.json",
     "experiments/dayrun_0820/annotations/labels_boost_e.json", "boost_e"),
    ("experiments/dayrun_0820/manifest_boost_e2.json",
     "experiments/dayrun_0820/annotations/labels_boost_e2.json", "boost_e2"),
]

frames, lab_frames, lab_scene_fp = [], {}, []
grid = None
for mp, lp, suf in PAIRS:
    M = json.load(open(mp)); L = json.load(open(lp))
    grid = grid or L.get("grid")
    for f in M["frames"]:
        if suf:
            f = dict(f); f["frame_id"] = f["frame_id"] + "::" + suf
        frames.append(f)
    for k, v in L["frames"].items():
        lab_frames[k + ("::" + suf if suf else "")] = v
    for s in L.get("scene_footprint", []):
        s = dict(s); s["round_tag"] = suf or "main"; lab_scene_fp.append(s)

ids = [f["frame_id"] for f in frames]
assert len(ids) == len(set(ids)), f"dup frame_ids: {len(ids)-len(set(ids))}"
base_meta = json.load(open(PAIRS[0][0]))["meta"]
meta = dict(base_meta)  # inherit every key gates/consumers expect (tier_source, rounds, ...)
meta.update(created="2026-08-20", grid_version="PROVISIONAL-GRID-V1", n_cells=20,
            gt_source="derived-heightmapdiff-gridv1-PROVISIONAL",
            note="mainrun pair + boost_h/e/e2 pairs; boost file tokens ::<round> (D24)")
json.dump({"meta": meta, "frames": frames}, open(OUT_M, "w"))
json.dump({"grid": grid, "meta": meta, "frames": lab_frames,
           "scene_footprint": lab_scene_fp}, open(OUT_L, "w"))
on = sum(1 for f in frames if f["toggle_state"] == "on")
print(f"[merge] {len(frames)} frames (on {on} / off {len(frames)-on}) -> {OUT_M}")
