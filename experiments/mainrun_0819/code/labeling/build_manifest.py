#!/usr/bin/env python3
"""Merge a labeler output (labels_v*.json) + per-scene variation.json into the
fixed manifest contract.

Provenance (gt_source / tier_source / gate_policy / n_cells) is READ BACK from the
labels file rather than re-declared here: the labeler is the only component that
knows which gridspec produced these labels, so a V1 label file cannot be stamped
with the V0 provenance by a manifest step that never saw the grid (D19, DAYRUN
Phase 1).  The imported constants remain as the fallback for a pre-D19 label file.
"""
import argparse, datetime, json, os, sys
from labeler import (scene_dirs, GT_SOURCE, TIER_SOURCE, FOOTPRINT_VERSION,
                     GATE_POLICY, n_cells)

CAM_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov", "ground_z")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--on-round", required=True)
    ap.add_argument("--off-round", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    lab = json.load(open(a.labels))
    lmeta = lab.get("meta") or {}
    GT_SRC = lab.get("gt_source") or lmeta.get("gt_source") or GT_SOURCE
    TIER_SRC = lmeta.get("tier_source") or TIER_SOURCE
    NCELL = lmeta.get("n_cells") or n_cells(lab["grid"])
    dirs = {"on": scene_dirs(a.on_round), "off": scene_dirs(a.off_round)}
    rounds = {"on": os.path.basename(os.path.abspath(a.on_round)),
              "off": os.path.basename(os.path.abspath(a.off_round))}

    recs, seeds, skips = {}, set(), []
    for arm, sd in dirs.items():
        for scene, d in sd.items():
            v = json.load(open(os.path.join(d, "variation.json")))
            seeds.add(v.get("seed"))
            cu = v["cuts"]
            for c in (cu.values() if isinstance(cu, dict) else cu):
                recs[f"{arm}/{scene}/{c['file']}"] = (arm, scene, d, c)

    frames, wrong_len = [], []
    for fid, f in sorted(lab["frames"].items()):
        if fid not in recs:
            skips.append(f"{fid}: no variation.json record"); continue
        if len(f["polar_gt"]) != NCELL:      # a label vector of the wrong grid
            wrong_len.append(fid); continue
        arm, scene, d, c = recs[fid]
        if not c.get("ok", True):
            skips.append(f"{fid}: ok=false"); continue
        rgb = os.path.join(d, c["file"])
        dep = os.path.join(d, c.get("depth") or os.path.splitext(c["file"])[0] + ".depth.npy")
        frames.append(dict(
            frame_id=fid, scene_id=scene, round=rounds[arm], toggle_state=arm,
            rgb=os.path.abspath(rgb),
            depth=os.path.abspath(dep) if os.path.isfile(dep) else None,
            polar_gt=f["polar_gt"],
            # D14: training GT is the gated one above; the pre-gate wedge result
            # and the cells the gate removed ride along untouched.
            polar_gt_pregate=f.get("polar_gt_pregate", f["polar_gt"]),
            gate_excluded=f.get("gate_excluded", dict(cells=[], n=0)),
            raw_vis=f["raw_vis"],
            tier=f["tier_strict"], tier_source=TIER_SRC, gt_source=GT_SRC,
            cam={k: c["cam"].get(k) for k in CAM_KEYS},
            cond=c.get("cond"), notes=""))
    for fid in sorted(recs):
        if fid not in lab["frames"]:
            skips.append(f"{fid}: no label record")

    if wrong_len:
        raise SystemExit(f"[manifest] {len(wrong_len)} frame(s) carry a polar_gt of "
                         f"length != {NCELL} (grid {lab['grid']['version']}); the "
                         f"labels file mixes gridspecs. First: {wrong_len[:3]}")

    man = dict(meta=dict(
        created=datetime.datetime.now().isoformat(timespec="seconds"),
        grid_version=lab["grid"]["version"], n_cells=NCELL,
        gt_source=GT_SRC, tier_source=TIER_SRC,
        footprint=lab.get("footprint", FOOTPRINT_VERSION),
        gate_policy=lmeta.get("gate_policy", GATE_POLICY),
        rounds=rounds, seed=(sorted(x for x in seeds if x is not None) or [None])[0],
        cam_convention_source=lab.get("cam_convention_source"),
        tau_strict=lab.get("tau_strict"), n_skipped=len(skips)), frames=frames)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(man, open(a.out, "w"), indent=1)
    for s in skips:
        print(f"[manifest] SKIP {s}", file=sys.stderr)
    print(f"[manifest] {len(frames)} frames, {len(skips)} skipped -> {a.out}")


if __name__ == "__main__":
    main()
