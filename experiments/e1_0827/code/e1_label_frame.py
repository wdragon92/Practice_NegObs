# -*- coding: utf-8 -*-
"""e1_label_frame.py -- one rendered frame -> one §5 record.

Order of operations (brief v6 §2 판정 순서):
    route (a) instances -> project -> visibility -> occluder test -> interior
    route (b) depth discontinuities (global parameter set)
    (a)-(b) deviation per instance
    tier_now derived by e1_schema.derive_tier_now -- §5's rule, spelled once

Nothing here decides anything. Every threshold it touches comes from
e1_const.py, and anything the code cannot resolve (an unclassified blocking
prim, a missing sidecar, a missing heightmap) is written into the record as a
null plus a note, never as a plausible default.
"""

import os

import numpy as np

import e1_camera as CAM
import e1_compare as CMP
import e1_const as C
import e1_data as D
import e1_depth_edges as B
import e1_geometry as G
import e1_schema as S
import e1_visibility as V


def _save_mask(mask, path):
    from PIL import Image
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray((np.asarray(mask, dtype=bool) * 255).astype(np.uint8),
                    mode="L").save(path)
    return path


def label_frame(round_name, scene_id, frame_name, out_dir, domain="stair",
                classifier=None, want_camera_check=False, keep_arrays=False):
    """Build the record for one frame.

    Returns (FrameRecord, extras) where `extras` carries the arrays the overlay
    and the smoke report need (only when keep_arrays).
    """
    sdir = D.scene_dir(round_name, scene_id)
    cut = D.find_cut(sdir, frame_name)
    A = D.frame_assets(sdir, cut)
    classifier = classifier or V.PrimClassifier.load()

    frame_id = "%s/%s/%s" % (round_name, scene_id, frame_name[:-len(".png")])
    pose_id = "%s#p%02d" % (scene_id, int(cut.get("idx", -1)))
    notes = {"messages": [], "diag": {}}

    if not A["has_depth"]:
        notes["messages"].append("no depth image -- route (a) visibility and "
                                 "route (b) both impossible; frame not labelled")
        rec = S.FrameRecord(frame_id=frame_id, pose_id=pose_id, scene_id=scene_id,
                            world_id=scene_id, domain=domain,
                            rgb_path=D.rel_to_repo(A["rgb_path"]),
                            depth_path="", tier_now="NEG", notes=notes)
        return rec, {"skipped": "no-depth"}
    if not A["has_heightmap"]:
        notes["messages"].append("no heightmap -- route (a) impossible; "
                                 "frame not labelled")
        rec = S.FrameRecord(frame_id=frame_id, pose_id=pose_id, scene_id=scene_id,
                            world_id=scene_id, domain=domain,
                            rgb_path=D.rel_to_repo(A["rgb_path"]),
                            depth_path=D.rel_to_repo(A["depth_path"]),
                            tier_now="NEG", notes=notes)
        return rec, {"skipped": "no-heightmap"}

    depth = D.load_depth(A["depth_path"])
    hm = CAM.HeightMap.load(sdir)
    cam = CAM.CameraModel(cut["cam"])
    if depth.shape != (cam.H, cam.W):
        notes["messages"].append("depth shape %s != (%d,%d) from IMG_H/IMG_W"
                                 % (depth.shape, cam.H, cam.W))

    ids, id_table = D.load_idseg(A["idseg_path"])
    if not A["has_idseg"]:
        notes["messages"].append("no idseg sidecar -- occluder test unresolved "
                                 "(seg 없음 list)")
    if classifier.is_empty:
        notes["messages"].append("prim_class_rules.json is empty (결재 대기) -- "
                                 "every blocking prim resolves to 'unknown'")

    cam_check = None
    if want_camera_check:
        cam_check = CAM.verify(cam, depth, hm, cut["cam"].get("ground_z"))

    kept, dropped, gdiag = G.route_a(cam, hm, depth, ids, id_table, classifier,
                                     A["has_idseg"],
                                     ground_z=cut["cam"].get("ground_z"))
    b_mask, b_comps, bdiag = B.extract(depth)
    dfield = CMP.distance_field(b_mask)

    edges = []
    for i, item in enumerate(kept):
        edge_id = "e%02d" % i
        st = item["int"]
        mask_path = None
        if st["int_area_px"] > 0:
            mask_path = D.rel_to_repo(_save_mask(
                item["int_mask"],
                os.path.join(out_dir, "masks", "%s__%s.png"
                             % (frame_id.replace("/", "__"), edge_id))))
        dev, n_used = CMP.deviation(dfield, item["vis"]["px"], item["vis"]["py"],
                                    item["vis"]["visible"], depth.shape)
        dm = G.dist_stats(cam, item["pts_3d"], item["vis"])
        edges.append(S.EdgeRecord(
            edge_id=edge_id,
            polyline_px=item["runs"],
            pts_3d=[[float(a), float(b_), float(c_)] for a, b_, c_ in item["pts_3d"]],
            dist_m=S.DistM(**dm),
            int_area_px=st["int_area_px"], int_h_px=st["int_h_px"],
            int_w_px=st["int_w_px"], int_mask_path=mask_path,
            occluder=S.Occluder(**item["occluder"]),
            src_disagree_px=S.SrcDisagreePx(**dev)))
        item["_edge_id"] = edge_id
        item["_dev_n"] = n_used

    notes["diag"] = {
        "route_a": gdiag,
        "route_b": bdiag,
        "n_edges": len(edges),
        "instance_visibility": [
            {"edge_id": it["_edge_id"], **{k: v for k, v in it["diag"].items()
                                           if k != "blocker_prims"},
             "n_dev_points": it["_dev_n"]} for it in kept],
        "blocked_only_instances": [
            {"n_in_frame": it["diag"]["n_in_frame"],
             "n_blocked": it["diag"]["n_blocked"],
             "blocker_prims": it["diag"]["blocker_prims"]} for it in dropped],
        "unresolved_occluders": sorted({
            it["occluder"]["prim"] for it in kept + dropped
            if it["occluder"]["flag"] is None}),
    }
    if cam_check:
        notes["diag"]["camera_check"] = cam_check

    rec = S.FrameRecord(
        frame_id=frame_id, pose_id=pose_id, scene_id=scene_id, world_id=scene_id,
        domain=domain, rgb_path=D.rel_to_repo(A["rgb_path"]),
        depth_path=D.rel_to_repo(A["depth_path"]),
        tier_now=S.derive_tier_now(edges), notes=notes, edges=edges)

    extras = {"cam": cam, "depth": depth, "kept": kept, "dropped": dropped,
              "b_mask": b_mask, "assets": A, "cam_check": cam_check}
    return rec, (extras if keep_arrays else {"cam_check": cam_check})
