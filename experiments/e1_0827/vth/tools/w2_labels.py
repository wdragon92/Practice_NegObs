#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w2_labels.py -- analytic ground truth: how many pixels of the hole's INTERIOR are visible?

No hand annotation.  Every number comes from the rendered depth image plus the exact
camera pose plus the 1 cm footprint raster of the plate mesh.

DEFINITION USED (warehouse redefinition of "interior", VTH_CONST W1-4)
    A pixel belongs to the visible hole interior when
      (a) its sight ray crosses the z = plate_top plane INSIDE the target opening's
          exact 1 cm footprint (ray -> plane intersection; this is the unoccluded,
          purely geometric footprint), AND
      (b) what the ray actually hit is below the walking surface:
          depth == +inf (the ray left the scene through the opening)  OR
          the back-projected 3D point has z < plate_top - INT_Z_MARGIN.
    (a) alone is the analytic footprint area (`foot_area_px`); (a) and (b) together are
    the visible interior (`int_area_px`).  Their ratio gives `occluded_frac` for free.

    Rationale for testing xy at the plane rather than at the hit point: the plate is
    0.124 m thick, so 18-82 % of interior rays land on the vertical CUT FACE, whose xy
    lies exactly ON the footprint boundary -- a 1 cm raster lookup there is a coin flip.
    The plane crossing is where the ray ENTERS the opening and is numerically stable.
    Verified equivalent on near frames (see W2_PAPERWEIGHTS.md).

PROJECTION (verified to 0.05 mm in W1)
    R = Rz(yaw) @ Ry(sdf_pitch);  p_cam = R^T (p_world - eye)
    f = (W/2)/tan(hfov/2);  u = W/2 - f*p_cam.y/p_cam.x;  v = H/2 - f*p_cam.z/p_cam.x
    Gazebo depth = p_cam.x, so the ray parameter IS the stored depth.
"""
from __future__ import annotations

import argparse, csv, gzip, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INT_Z_MARGIN = 0.01      # [방법] "below the plate top" margin, metres
RIM_RING_PX = 2          # [방법] rim ring half-thickness in pixels (+-2 px)
RIM_TOL_M = 0.05         # [방법] |measured - plate-plane expected| tolerance for "rim visible"
MIN_OTHER_BOX_PX = 4     # [방법] a non-target opening is listed only if its projected bbox >= 4 px^2


def rot(pitch, yaw):
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]])
            @ np.array([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]]))


def hole_polygon(hole, n_circle=32):
    """World-frame footprint polygon at plate top. Targets carry the measured one."""
    if hole.get("footprint_polygon_world"):
        return np.asarray(hole["footprint_polygon_world"], float)
    b = hole["world_bbox"]
    if hole.get("shape") == "circle":
        cx, cy = 0.5 * (b[0] + b[2]), 0.5 * (b[1] + b[3])
        r = 0.25 * ((b[2] - b[0]) + (b[3] - b[1]))
        a = np.linspace(0, 2 * np.pi, n_circle, endpoint=False)
        return np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1)
    return np.array([[b[0], b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]]], float)


def project(pts_xyz, eye, R, f, W, H):
    """world points -> (u, v, depth). depth<=0 means behind the camera."""
    q = (pts_xyz - eye) @ R          # R^T (p-eye) == (p-eye) @ R
    d = q[:, 0]
    safe = np.where(np.abs(d) < 1e-9, 1e-9, d)
    u = W / 2.0 - f * q[:, 1] / safe
    v = H / 2.0 - f * q[:, 2] / safe
    return u, v, d


def seg_dist_xy(p, a, b):
    ab = b - a
    t = np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-12), 0.0, 1.0)
    return np.linalg.norm(p - (a + t * ab)), a + t * ab


def near_rim(poly, eye_xy):
    best, bp = 1e9, poly[0]
    n = len(poly)
    for i in range(n):
        d, q = seg_dist_xy(eye_xy, poly[i], poly[(i + 1) % n])
        if d < best:
            best, bp = d, q
    return best, bp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--n-masks", type=int, default=12)
    a = ap.parse_args()

    import cv2

    man = json.load(open(os.path.join(HERE, "capture_manifest.json")))
    H = json.load(open(os.path.join(HERE, "holes.json")))
    loc = json.load(open(os.path.join(HERE, "holes_local.json")))
    grid = np.load(os.path.join(HERE, "holes_local_grid.npz"))["grid"]   # True = SOLID plate
    plate_xy = np.asarray(H["plate_pose_xy"], float)
    top = float(H["plate_top_z"])
    raster = float(loc["raster_m"])
    org = np.asarray(loc["raster_origin"], float)

    holes = {h["hole_id"]: h for h in H["holes"]}
    # targets carry the measured polygon; merge it in
    for w, wv in H["worlds"].items():
        for t in wv["targets"]:
            holes[t["hole_id"]].setdefault("footprint_polygon_world", t["footprint_polygon_world"])

    # ---- per-target: exact opening sub-raster inside its own bbox -------------------
    sub = {}
    for hid, h in holes.items():
        b = h["world_bbox"]
        i0 = int(math.floor((b[0] - plate_xy[0] - org[0]) / raster))
        j0 = int(math.floor((b[1] - plate_xy[1] - org[1]) / raster))
        i1 = int(math.ceil((b[2] - plate_xy[0] - org[0]) / raster))
        j1 = int(math.ceil((b[3] - plate_xy[1] - org[1]) / raster))
        s = ~grid[j0:j1, i0:i1]                      # True = opening
        sub[hid] = (i0, j0, s)
    # sanity: the bbox crop must contain exactly the opening's own cells
    bad = [hid for hid, (i0, j0, s) in sub.items() if abs(int(s.sum()) - holes[hid]["cells"]) > 2]
    print(f"[w2] footprint sub-raster check: {len(sub)} openings, "
          f"{len(bad)} whose bbox crop != measured cell count {bad[:5]}")

    polys = {hid: hole_polygon(h) for hid, h in holes.items()}
    poly3 = {hid: np.column_stack([p, np.full(len(p), top)]) for hid, p in polys.items()}

    frames = man["frames"]
    if a.limit:
        frames = frames[:a.limit]
    W, Hh = man["frames"][0]["resolution"]
    f = (W / 2.0) / math.tan(man["frames"][0]["hfov_rad"] / 2.0)
    U, V = np.meshgrid(np.arange(W, dtype=np.float32) + 0.5,
                       np.arange(Hh, dtype=np.float32) + 0.5)
    dcam = np.stack([np.ones_like(U), -(U - W / 2.0) / f, -(V - Hh / 2.0) / f], -1).astype(np.float32)

    rows, others = [], {}
    mask_ids = set()
    t0 = time.time()
    mdir = os.path.join(HERE, "runs", "masks")
    os.makedirs(mdir, exist_ok=True)

    for k, fr in enumerate(frames):
        c = fr["camera"]
        eye = np.array([c["x"], c["y"], c["z"]], float)
        R = rot(c["sdf_pitch_rad"], c["yaw_rad"])
        dep = np.load(os.path.join(HERE, fr["depth"]))
        dw = dcam @ R.T.astype(np.float32)                     # world ray directions

        dz = dw[..., 2]
        tp = (top - eye[2]) / np.where(np.abs(dz) < 1e-9, np.nan, dz)
        desc = (dz < -1e-9) & np.isfinite(tp) & (tp > 0)
        hx = eye[0] + tp * dw[..., 0]
        hy = eye[1] + tp * dw[..., 1]

        hid = fr["hole_id"]
        i0, j0, s = sub[hid]
        ii = np.floor((hx - plate_xy[0] - org[0]) / raster).astype(np.int32) - i0
        jj = np.floor((hy - plate_xy[1] - org[1]) / raster).astype(np.int32) - j0
        inb = desc & (ii >= 0) & (jj >= 0) & (ii < s.shape[1]) & (jj < s.shape[0])
        through = np.zeros_like(inb)
        through[inb] = s[jj[inb], ii[inb]]

        finite = np.isfinite(dep)
        pz = eye[2] + np.where(finite, dep, 0.0) * dz
        below = (~finite) | (pz < top - INT_Z_MARGIN)
        interior = through & below

        foot_px = int(through.sum())
        int_px = int(interior.sum())
        void_px = int((interior & ~finite).sum())
        # why a footprint pixel is NOT interior -- two very different causes:
        #   asset  : the ray was stopped ABOVE the walking surface -> a real occluder
        #   graze  : it hit the far cut face within INT_Z_MARGIN of the top (shallow ray)
        occ_px = int((through & finite & (pz > top + INT_Z_MARGIN)).sum())
        graze_px = foot_px - int_px - occ_px

        if int_px:
            ys, xs = np.nonzero(interior)
            gx0, gx1, gy0, gy1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
            int_w, int_h = gx1 - gx0 + 1, gy1 - gy0 + 1
        else:
            gx0 = gx1 = gy0 = gy1 = -1
            int_w = int_h = 0

        # ---- rim ring: is the opening's outline on the floor visible? --------------
        pu, pv, pd = project(poly3[hid], eye, R, f, W, Hh)
        rim_in = bool((pd > 0).all() and pu.max() > 0 and pu.min() < W
                      and pv.max() > 0 and pv.min() < Hh)
        rim_vis, rim_px_n = False, 0
        rb = [-1, -1, -1, -1]
        if (pd > 0).all():
            rb = [int(np.floor(pu.min())), int(np.floor(pv.min())),
                  int(np.ceil(pu.max())), int(np.ceil(pv.max()))]
            ring = np.zeros((Hh, W), np.uint8)
            cv2.polylines(ring, [np.round(np.stack([pu, pv], 1)).astype(np.int32)],
                          True, 1, thickness=2 * RIM_RING_PX + 1)
            rm = ring.astype(bool) & ~through
            rim_px_n = int(rm.sum())
            if rim_px_n:
                exp = tp[rm]
                meas = dep[rm]
                ok = np.isfinite(meas) & np.isfinite(exp)
                rim_vis = bool(np.any(np.abs(meas[ok] - exp[ok]) <= RIM_TOL_M)) if ok.any() else False

        nd, npt = near_rim(polys[hid], eye[:2])
        d3 = float(math.hypot(nd, eye[2] - top))

        # ---- every OTHER opening whose footprint projects into this frame ----------
        ol = []
        for oid, p3 in poly3.items():
            if oid == hid:
                continue
            ou, ov, od = project(p3, eye, R, f, W, Hh)
            if not (od > 0).all():
                continue
            x0, x1 = ou.min(), ou.max()
            y0, y1 = ov.min(), ov.max()
            if x1 < 0 or y1 < 0 or x0 > W or y0 > Hh:
                continue
            if (min(x1, W) - max(x0, 0)) * (min(y1, Hh) - max(y0, 0)) < MIN_OTHER_BOX_PX:
                continue
            ol.append([oid, round(float(x0), 1), round(float(y0), 1),
                       round(float(x1), 1), round(float(y1), 1)])
        fkey = fr["world"] + "/" + fr["pose_id"]
        others[fkey] = ol

        rows.append(dict(
            frame_key=fkey, pose_id=fr["pose_id"], world=fr["world"], hole_id=hid, band=fr["hole_band"],
            shape=fr["hole_shape"], hole_area_m2=fr["hole_area_m2"], r_eq_m=fr["hole_r_eq_m"],
            occlusion_intended=int(bool(fr["occlusion_intended"])),
            occluder=fr["occluder"] or "", approach=fr["approach"],
            standoff_m=fr["standoff_m"], height_m=fr["height_m"], pitch_deg=fr["pitch_deg"],
            dist_cam_hole_centre_m=fr["dist_cam_to_hole_centre_m"],
            dist_near_rim_m=round(d3, 4), dist_near_rim_xy_m=round(float(nd), 4),
            int_area_px=int_px, int_w_px=int_w, int_h_px=int_h,
            gt_x0=gx0, gt_y0=gy0, gt_x1=gx1, gt_y1=gy1,
            foot_area_px=foot_px, occ_above_px=occ_px, graze_px=graze_px,
            occluded_frac=round(1.0 - int_px / foot_px, 4) if foot_px else "",
            occ_frac_asset=round(occ_px / foot_px, 4) if foot_px else "",
            void_frac=round(void_px / int_px, 4) if int_px else "",
            rim_bbox_x0=rb[0], rim_bbox_y0=rb[1], rim_bbox_x1=rb[2], rim_bbox_y1=rb[3],
            rim_ring_px=rim_px_n, rim_in_frame=int(rim_in), rim_visible=int(rim_vis),
            n_other_holes=len(ol),
            rgb=fr["rgb"], depth=fr["depth"],
        ))

        if len(mask_ids) < a.n_masks and int_px > 200 and (k % 97 == 0 or len(mask_ids) < 3):
            mp = os.path.join(mdir, fr["world"] + "__" + fr["pose_id"] + ".mask.png")
            img = cv2.imread(os.path.join(HERE, fr["rgb"]))
            ov = img.copy()
            ov[through & ~interior] = (0, 128, 255)      # analytic footprint, not interior
            ov[interior] = (0, 0, 255)                   # visible interior
            out = cv2.addWeighted(img, 0.55, ov, 0.45, 0)
            cv2.rectangle(out, (gx0, gy0), (gx1, gy1), (0, 255, 0), 2)
            cv2.imwrite(mp, cv2.resize(out, (640, 360)))
            mask_ids.add(fr["pose_id"])

        if (k + 1) % 200 == 0:
            print(f"  [{k+1}/{len(frames)}] {time.time()-t0:.0f}s", flush=True)

    cols = list(rows[0].keys())
    with open(os.path.join(HERE, "labels.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with gzip.open(os.path.join(HERE, "labels_otherholes.json.gz"), "wt") as gz:
        json.dump(others, gz, separators=(",", ":"))
    print(f"[w2] labels.csv rows={len(rows)}  frames={len(frames)}  "
          f"masks={len(mask_ids)}  wall={time.time()-t0:.0f}s")


if __name__ == "__main__":
    sys.exit(main())
