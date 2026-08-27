#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_manifest.py -- one capture_manifest.json entry per frame actually on disk."""
from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ("world", "pose_id", "hole_id", "hole_area_m2", "hole_band", "approach",
          "standoff_m", "height_m", "pitch_deg", "occlusion_intended")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    holes = json.load(open(os.path.join(HERE, "holes.json")))
    HC = {h["hole_id"]: h for h in holes["holes"]}
    top = holes["plate_top_z"]
    rows, missing = [], []
    for pj in sorted(glob.glob(os.path.join(HERE, "frames", "*", "*.pose.json"))):
        r = json.load(open(pj))
        d = os.path.dirname(pj)
        rgb = os.path.join(d, r["rgb_file"])
        dep = os.path.join(d, r["depth_file"])
        if not (os.path.exists(rgb) and os.path.exists(dep)):
            missing.append(r["pose_id"])
            continue
        e = {k: r[k] for k in FIELDS}
        hh = HC[r["hole_id"]]
        b = hh["world_bbox"]
        # Unambiguous geometry, recomputed from the pose rather than trusted from the plan.
        # NOTE standoff_m means "to the near rim along the approach axis" for approach
        # poses but is only an approximation for the occlusion poses, so W2 should use
        # these two instead.
        dxy = math.hypot(r["x"] - hh["centre"][0], r["y"] - hh["centre"][1])
        e.update(
            camera=dict(x=r["x"], y=r["y"], z=r["z"], yaw_rad=r["yaw_rad"],
                        yaw_deg=round(math.degrees(r["yaw_rad"]), 3),
                        pitch_deg=r["pitch_deg"], sdf_pitch_rad=r["sdf_pitch_rad"],
                        height_above_plate_m=r["height_m"]),
            hole_centre_xy=hh["centre"], hole_bbox_world=b, hole_shape=hh["shape"],
            hole_w_m=hh["w_m"], hole_h_m=hh["h_m"], hole_r_eq_m=hh["r_eq_m"],
            dist_cam_to_hole_centre_m=round(math.hypot(dxy, r["z"] - top), 4),
            dist_cam_to_hole_centre_xy_m=round(dxy, 4),
            hfov_rad=r["hfov_rad"], hfov_deg=round(math.degrees(r["hfov_rad"]), 3),
            resolution=r["res"],
            rgb=os.path.relpath(rgb, HERE), depth=os.path.relpath(dep, HERE),
            depth_units="metres float32",
            rim_px_pred=r.get("rim_px_pred"),
            occluder=r.get("occluder"), occluder_planned=r.get("occluder_planned"),
            rgb_mean=r.get("rgb_mean"), rgb_sat_frac=r.get("rgb_sat_frac"),
            depth_finite_frac=r.get("depth_finite_frac"),
            depth_min_m=r.get("depth_min_m"), depth_max_m=r.get("depth_max_m"),
            bytes_rgb=os.path.getsize(rgb), bytes_depth=os.path.getsize(dep))
        rows.append(e)
    rows.sort(key=lambda e: (e["world"], e["pose_id"]))
    man = dict(
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        stage="W1 capture (edge_relabel_brief_v6 §7 / VTH warehouse A-track)",
        source_worlds={w: f"Baseline_NegObs/.../bumperbot_description/worlds/{w}.world"
                       for w in ("eworld2", "expandedworld")},
        plate_pose_xy=holes["plate_pose_xy"], plate_top_z=holes["plate_top_z"],
        n_frames=len(rows),
        n_frames_by_world={w: sum(1 for r in rows if r["world"] == w)
                           for w in ("eworld2", "expandedworld")},
        n_occlusion_intended=sum(1 for r in rows if r["occlusion_intended"]),
        frames=rows)
    out = os.path.join(HERE, "capture_manifest.json")
    json.dump(man, open(out, "w"), indent=1, sort_keys=True)
    print(f"frames in manifest {len(rows)}   incomplete pairs {len(missing)}")
    for w, n in man["n_frames_by_world"].items():
        print(f"  {w:16s} {n}")
    print(f"  occlusion_intended {man['n_occlusion_intended']}")
    print(f"-> {out}")

    # SHA256SUMS of every frame artefact
    sums = []
    for e in rows:
        for k in ("rgb", "depth"):
            p = os.path.join(HERE, e[k])
            sums.append(f"{sha256(p)}  {e[k]}")
    open(os.path.join(HERE, "frames", "SHA256SUMS.txt"), "w").write("\n".join(sums) + "\n")
    print(f"-> {os.path.join(HERE, 'frames', 'SHA256SUMS.txt')} ({len(sums)} files)")


if __name__ == "__main__":
    main()
