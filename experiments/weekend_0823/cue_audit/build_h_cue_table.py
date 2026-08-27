#!/usr/bin/env python3
"""
CPU-1 / WEEKEND_BRIEF_0823 §6.1 — strict-H frame cue audit.

Purpose (one line): enumerate every strict-H frame in the merged corpus and record,
per frame, which of the 13 drop-off cues are still visible in that frame.

Inputs (read-only, all canonical files untouched):
  labels   experiments/dayrun_0820/annotations/labels_v1_full.json   (tier_strict)
  manifest experiments/dayrun_0820/dataset_manifest_v2_full.json     (camera, round, cond)
  split    experiments/dayrun_0820/split_v2_full.json
  cues     Docs/reports/raw_260816/cue_matrix_result.json            (13 cues x 9 presets)
  poses    dataset/<group>/<round>/<split>/<scene>/variation.json    (full eye incl. y)
           (0827 reorg: a round sits one purpose group below `dataset/`.  Resolve it by
            NAME — `dataset/ROUNDS.json` / `variation_kit.round_dir(name)` — not by path.)

Output: h_cue_table.csv in this directory.

Method grades (see PREREGISTRATION.md §4):
  M1  geometric projection from scene coordinates + this frame's camera
  M2  matrix per-preset occlusion list, mapped through this frame's (h, d)
  M2+cond  M2 refined by this frame's lighting condition (physics: no sun disc -> no cast shadow)
  M3  scene-level fallback (flagged)
"""
import json, csv, math, os, sys

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OUT = os.path.join(ROOT, "experiments/weekend_0823/cue_audit")

CUES = ["edge_line_contrast", "texture_change_across_edge", "shadow_line",
        "far_side_visible_depth", "nosing_strip", "tactile_paving",
        "railing_or_guard", "curb_or_upstand", "vegetation_edge",
        "water_surface", "signage_or_marking", "specular_change",
        "geometry_silhouette"]

# brief §6.1 names these as load-bearing
LOADBEARING = ["railing_or_guard", "tactile_paving", "nosing_strip", "shadow_line",
               "far_side_visible_depth", "signage_or_marking", "vegetation_edge"]

# cue families (see H_CUE_AUDIT.md §3.3)
FAM = {
    "direct_depth": ["far_side_visible_depth", "water_surface", "geometry_silhouette"],
    "edge_surface": ["edge_line_contrast", "texture_change_across_edge", "shadow_line",
                     "curb_or_upstand", "specular_change"],
    "installed":    ["railing_or_guard", "tactile_paving", "nosing_strip",
                     "signage_or_marking"],
    "context_veg":  ["vegetation_edge"],
}

# raw-json scene key -> corpus scene_id
SCENEKEY = {
    "scene09": "scene09", "scene12_riverside_deck": "scene12",
    "scene14_grandstair_illusion": "scene14", "scene15_alley_labyrinth": "scene15",
    "scene17_ramp_pair_hangang": "scene17", "scene20_diagonal_oblique": "scene20",
}

# occluder identity, read from the scene .py files + the matrix drop_summary (see H_CUE_AUDIT.md §2)
OCCLUDER = {
    "scene09": ("self_occlusion_crest", "terrace lip / 36-step flight self-occluded below the lip"),
    "scene12": ("self_occlusion_deck_edge", "cantilever deck edge; 7.5 m riprap+water band hidden under the open guard"),
    "scene14": ("self_occlusion_crest", "marble terrace crest; 40-step flight self-occludes (Potemkin identity)"),
    "scene15": ("self_occlusion_crest+side_walls", "upper alley floor end + flanking house walls; 2.21 m behind the 25 deg bend has no cue by design"),
    "scene17": ("self_occlusion_crest", "levee crest at x=0; grazing ray skips bank/stairs/terrace"),
    "scene20": ("self_occlusion_crest", "mesa lip on the 30 deg diagonal; flight self-occluded at every preset"),
}

PRESET_H = [0.3, 0.9, 1.8]
PRESET_D = [2.0, 5.0, 10.0]


def bucket_h(h):
    # midpoints 0.6 / 1.35
    return 0.3 if h < 0.6 else (0.9 if h < 1.35 else 1.8)


def bucket_d(d):
    # log midpoints sqrt(2*5)=3.162, sqrt(5*10)=7.071
    return 2.0 if d < 3.1623 else (5.0 if d < 7.0711 else 10.0)


def preset_name(h, d):
    hs = {0.3: "h0.3", 0.9: "h0.9", 1.8: "h1.8"}[h]
    ds = {2.0: "d2", 5.0: "d5", 10.0: "d10"}[d]
    return hs + "_" + ds


def load_cue_matrix():
    p = os.path.join(ROOT, "Docs/reports/raw_260816/cue_matrix_result.json")
    scenes = json.load(open(p))["result"]["scenes"]
    out = {}
    for s in scenes:
        if s["scene"] not in SCENEKEY:
            continue
        sid = SCENEKEY[s["scene"]]
        rec = {}
        for c in s["cues"]:
            rec[c["cue"]] = dict(present=bool(c["present"]), strength=c["strength"],
                                 occ=set(c["occluded_or_weak_at"]))
        out[sid] = dict(cues=rec, undercued=s["undercued"],
                        single_cue_risk=s["single_cue_risk"],
                        drop_type=s["drop_type"])
    return out


def load_variation_index(rgb_paths):
    """dir(variation.json) -> {filename: cut}"""
    idx = {}
    for p in rgb_paths:
        d = os.path.dirname(p)
        if d in idx:
            continue
        vp = os.path.join(d, "variation.json")
        if not os.path.exists(vp):
            idx[d] = None
            continue
        v = json.load(open(vp))
        idx[d] = {c["file"]: c for c in v["cuts"]}
        idx[d]["__gy__"] = v.get("gy", 0.0)
    return idx


# ---------------------------------------------------------------- M1 geometry
def in_frame(eye, yaw_deg, pitch_deg, hfov_deg, pt, aspect=1920.0 / 1080.0):
    """Approximate frustum test. Roll ignored, azimuth/elevation treated separably
    (exact at pitch=0; the H frames sit at pitch -8..-14 deg, so the corner error is
    a few degrees). Returns True if pt is inside the FOV and in front of the camera."""
    dx, dy, dz = pt[0] - eye[0], pt[1] - eye[1], pt[2] - eye[2]
    horiz = math.hypot(dx, dy)
    if horiz < 1e-6:
        return False
    az = math.degrees(math.atan2(dy, dx))
    daz = (az - yaw_deg + 180.0) % 360.0 - 180.0
    if abs(daz) > 90.0:
        return False
    hh = hfov_deg / 2.0
    vfov = 2.0 * math.degrees(math.atan(math.tan(math.radians(hh)) / aspect))
    el = math.degrees(math.atan2(dz, horiz))
    dele = el - pitch_deg
    return abs(daz) <= hh and abs(dele) <= vfov / 2.0


def scene12_rail_in_frame(cut):
    """scene12 river-side guard: PARAMS['rail'] y=1.15, post_h=1.10, rails at z=1.10/0.55,
    spanning the deck x0=-18.0 .. x1=0.0 (scene file lines 265, 346, 1922-1933).
    True if any sampled rail point falls inside the frustum."""
    cam = cut["cam"]
    eye = cam["eye"]
    for i in range(181):                      # x = -18 .. 0 step 0.1
        x = -18.0 + 0.1 * i
        for z in (1.10, 0.55, 0.0):
            if in_frame(eye, cam["yaw"], cam["pitch"], cam["hfov"], (x, 1.15, z)):
                return True
    return False


def main():
    labels = json.load(open(os.path.join(
        ROOT, "experiments/dayrun_0820/annotations/labels_v1_full.json")))["frames"]
    manifest = json.load(open(os.path.join(
        ROOT, "experiments/dayrun_0820/dataset_manifest_v2_full.json")))["frames"]
    mf = {f["frame_id"]: f for f in manifest}
    split = json.load(open(os.path.join(ROOT, "experiments/dayrun_0820/split_v2_full.json")))
    where = {}
    for k, v in split.items():
        for s in v:
            where[s] = k
    mat = load_cue_matrix()

    H = sorted([k for k, v in labels.items() if v.get("tier_strict") == "H"])
    vidx = load_variation_index([mf[k]["rgb"] for k in H])

    band_of = ["1"] * 5 + ["2"] * 5 + ["3a"] * 5 + ["3b"] * 5
    rows = []
    for fid in H:
        m = mf[fid]
        lab = labels[fid]
        sid = m["scene_id"]
        cam = m["cam"]
        hb, db = bucket_h(cam["h_rel"]), bucket_d(cam["d"])
        pre = preset_name(hb, db)
        cond = m["cond"]
        smat = mat[sid]["cues"]

        d = os.path.dirname(m["rgb"])
        cut = (vidx.get(d) or {}).get(os.path.basename(m["rgb"]))

        flags, methods, strengths = {}, {}, {}
        for c in CUES:
            rec = smat.get(c, dict(present=False, strength="absent", occ=set()))
            if not rec["present"]:
                flags[c], methods[c] = 0, "M2"
                strengths[c] = "-"
                continue
            vis = 0 if pre in rec["occ"] else 1
            meth = "M2"
            # ---- refinement 1: no sun disc -> no cast shadow line (L6/L7 overcast)
            if c == "shadow_line" and cond in ("L6", "L7"):
                vis, meth = 0, "M2+cond"
            # ---- refinement 2: scene12 guard, per-frame geometric projection
            if c == "railing_or_guard" and sid == "scene12" and cut is not None:
                vis = 1 if scene12_rail_in_frame(cut) else 0
                meth = "M1"
            flags[c], methods[c] = vis, meth
            strengths[c] = rec["strength"][0].upper() if vis else "-"

        n_all = sum(flags.values())
        n_lb = sum(flags[c] for c in LOADBEARING)
        n_strong = sum(1 for c in CUES if flags[c] and
                       smat.get(c, {}).get("strength") == "strong")
        fam_counts = {k: sum(flags[c] for c in v) for k, v in FAM.items()}

        gt = lab["polar_gt"]
        pos = [i for i, g in enumerate(gt) if g]
        bands = sorted({band_of[i] for i in pos}, key=lambda b: ["1", "2", "3a", "3b"].index(b))

        rows.append(dict(
            frame_id=fid, scene=sid, split=where.get(sid, "?"), round=m["round"], cond=cond,
            cam_d=round(cam["d"], 3), cam_h=round(cam["h_rel"], 3), cam_yaw=round(cam["yaw"], 2),
            cam_pitch=round(cam["pitch"], 2), cam_hfov=round(cam["hfov"], 2),
            cam_y=round(cut["cam"]["eye"][1], 3) if cut else "",
            preset=pre, preset_h=hb, preset_d=db,
            occluder_class=OCCLUDER[sid][0], occluder_detail=OCCLUDER[sid][1],
            **{("cue_" + c): flags[c] for c in CUES},
            **{("m_" + c): methods[c] for c in CUES},
            cue_count=n_all, cue_count_loadbearing=n_lb, cue_count_strong=n_strong,
            fam_direct_depth=fam_counts["direct_depth"],
            fam_edge_surface=fam_counts["edge_surface"],
            fam_installed=fam_counts["installed"],
            fam_context_veg=fam_counts["context_veg"],
            cls=("bare-H" if n_all == 0 else "cued-H"),
            cue_list="|".join(c for c in CUES if flags[c]),
            n_pos_cells=len(pos), gt_bands="+".join(bands),
            scene_level_fallback=0,
        ))

    fields = list(rows[0].keys())
    with open(os.path.join(OUT, "h_cue_table.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("wrote", os.path.join(OUT, "h_cue_table.csv"), len(rows), "rows")

    # console summary
    import collections
    print("\n-- per scene --")
    for s in sorted({r["scene"] for r in rows}):
        rr = [r for r in rows if r["scene"] == s]
        print("%-9s n=%-4d split=%-6s bare=%-3d cued=%-3d  presets=%s"
              % (s, len(rr), rr[0]["split"],
                 sum(1 for r in rr if r["cls"] == "bare-H"),
                 sum(1 for r in rr if r["cls"] == "cued-H"),
                 dict(collections.Counter(r["preset"] for r in rr))))
    print("\n-- cue_count histogram --")
    print(dict(sorted(collections.Counter(r["cue_count"] for r in rows).items())))
    print("\n-- per cue, n frames visible (of %d) --" % len(rows))
    for c in CUES:
        print("  %-28s %4d" % (c, sum(r["cue_" + c] for r in rows)))


if __name__ == "__main__":
    main()
