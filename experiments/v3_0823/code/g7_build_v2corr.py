#!/usr/bin/env python3
"""G7 repair, step 5 — the corrected-GT manifest + corrected merged label file.

MAPPING RULE (one sentence): a frame is re-pointed at the corrected label iff its
(boost band, scene) is one of the five pairs whose heightmap the boost round left
un-fused -- boost_e x {scene07, scene08, scene12} and boost_e2 x {scene07,
scene12} -- and every other frame in the corpus keeps the frozen 08-20 label,
byte for byte.

Nothing frozen is read-modify-written: this reads
  experiments/dayrun_0820/dataset_manifest_v2_full.json   (base, untouched)
  experiments/dayrun_0820/annotations/labels_v1_full.json (base, untouched)
  experiments/v3_0823/annotations/labels_boost_{e,e2}_g7fix{,M}.json  (corrected)
and writes NEW files under experiments/v3_0823/.

Frame-level provenance: every frame carries `label_source`
("original" | "g7fix-B" | "g7fix-A"), and every corrected frame additionally
carries `tier_before` and `g7_note`.  rgb/depth keep pointing at the FROZEN
render paths -- only the GT changed, not a pixel.
"""
import json, os, sys, collections

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DAY = os.path.join(REPO, "experiments/dayrun_0820")
V3 = os.path.join(REPO, "experiments/v3_0823")
AFFECTED = {("boost_e", "scene07"), ("boost_e", "scene08"), ("boost_e", "scene12"),
            ("boost_e2", "scene07"), ("boost_e2", "scene12")}
SUFFIX_OF_ROUND = {"260820_boost_e_on": "boost_e", "260820_boost_e_off": "boost_e",
                   "260820_boost_e2_on": "boost_e2", "260820_boost_e2_off": "boost_e2",
                   "260820_boost_h_on": "boost_h", "260820_boost_h_off": "boost_h",
                   "260819_main_on": "main", "260819_main_off": "main"}
GT_KEYS = ("polar_gt", "polar_gt_pregate", "gate_excluded", "raw_vis")


def load_corrected(variant):
    """{(band, 'arm/scene/file'): label-dict} for the corrected label sets."""
    out = {}
    for band in ("e", "e2"):
        p = os.path.join(V3, f"annotations/labels_boost_{band}_g7fix{variant}.json")
        L = json.load(open(p))
        for k, v in L["frames"].items():
            out[(f"boost_{band}", k)] = v
    return out


def build(variant, tag, out_manifest, out_labels):
    M = json.load(open(os.path.join(DAY, "dataset_manifest_v2_full.json")))
    L = json.load(open(os.path.join(DAY, "annotations/labels_v1_full.json")))
    corr = load_corrected(variant)
    n_corr = 0
    mig = collections.Counter()
    frames = []
    for f in M["frames"]:
        f = dict(f)
        band = SUFFIX_OF_ROUND[f["round"]]
        key = (band, f["scene_id"])
        base_id = f["frame_id"].split("::")[0]
        c = corr.get((band, base_id)) if key in AFFECTED else None
        if c is None:
            f["label_source"] = "original"
        else:
            mig[(band, f["scene_id"], f["tier"], c["tier_strict"])] += 1
            f["tier_before"] = f["tier"]
            for k in GT_KEYS:
                f[k] = c[k]
            f["tier"] = c["tier_strict"]
            f["label_source"] = tag
            f["g7_note"] = ("relabelled against the re-fused heightmap; "
                            "pixels unchanged (G7 / D42 / D50)")
            n_corr += 1
        frames.append(f)

    lab = dict(L)
    lab_frames = dict(L["frames"])
    for (band, k), v in corr.items():
        scene = k.split("/")[1]
        if (band, scene) not in AFFECTED:
            continue
        lab_frames[k + "::" + band] = v
    lab["frames"] = lab_frames
    # scene_footprint: replace the affected rows, keep the rest
    sfp = []
    for r in L.get("scene_footprint", []):
        if (r.get("round_tag"), r["scene"]) in AFFECTED:
            continue
        sfp.append(r)
    for band in ("e", "e2"):
        S = json.load(open(os.path.join(V3, f"annotations/labels_boost_{band}_g7fix{variant}.json")))
        for r in S["scene_footprint"]:
            if (f"boost_{band}", r["scene"]) in AFFECTED:
                r = dict(r); r["round_tag"] = f"boost_{band}"; r["label_source"] = tag
                sfp.append(r)
    lab["scene_footprint"] = sfp

    meta = dict(M["meta"])
    meta.update(
        created="2026-08-23", corrects="experiments/dayrun_0820/dataset_manifest_v2_full.json",
        defect="G7 — the 260820_boost_* rounds never ran fuse_heightmap.py "
               "(DECISIONS.md D42/D50; cue_audit/CUEOFF_RESULT_v2.md §3)",
        g7_variant=tag,
        g7_mapping_rule="frames whose (band, scene) is in "
                        "{boost_e x (scene07, scene08, scene12), boost_e2 x (scene07, scene12)} "
                        "carry the corrected label; every other frame is the frozen 08-20 label, "
                        "byte-identical",
        g7_affected_frames=n_corr,
        g7_label_sets=[f"experiments/v3_0823/annotations/labels_boost_e_g7fix{variant}.json",
                       f"experiments/v3_0823/annotations/labels_boost_e2_g7fix{variant}.json"],
        g7_shadow_render_trees=[f"dataset/260820_boost_e_{{on,off}}_g7fix{variant}",
                                f"dataset/260820_boost_e2_{{on,off}}_g7fix{variant}"],
        note=meta.get("note", "") + " | G7-corrected labels for 5 (band, scene) pairs")
    json.dump(dict(meta=meta, frames=frames), open(out_manifest, "w"))
    lab["meta"] = dict(lab.get("meta", {})); lab["meta"].update(
        g7_variant=tag, g7_mapping_rule=meta["g7_mapping_rule"])
    json.dump(lab, open(out_labels, "w"))
    print(f"[{tag}] {len(frames)} frames, {n_corr} corrected -> {os.path.relpath(out_manifest, REPO)}")
    for (band, sc, a, b), n in sorted(mig.items()):
        if a != b:
            print(f"    {band:9s} {sc:8s} {a:12s} -> {b:12s} {n}")
    return mig


if __name__ == "__main__":
    build("M", "g7fix-B", os.path.join(V3, "dataset_manifest_v2corr.json"),
          os.path.join(V3, "annotations/labels_v1_full_g7fix.json"))
    build("", "g7fix-A", os.path.join(V3, "dataset_manifest_v2corr_roundown.json"),
          os.path.join(V3, "annotations/labels_v1_full_g7fix_roundown.json"))
