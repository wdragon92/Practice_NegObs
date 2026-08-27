#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vth_plan.py -- pick target holes, build the camera pose grid, log every skip.

Outputs (written next to this tool's parent dir):
    holes.json            every opening in world frame, per world + the target list
    plan.json             one entry per PLANNED pose (kept or skipped, with reason)

Geometry conventions
    * Gazebo/SDF camera looks along its local +X; R = Rz(yaw) Ry(pitch) Rx(roll).
      SDF pitch is nose-DOWN positive, so sdf_pitch = -radians(pitch_deg) and a
      pitch_deg of -15 means "15 deg below horizontal" (the stair corpus convention,
      and the same sign the 08-24 warehouse manifest printed).
    * standoff is measured from the camera to the NEAR RIM of the target hole,
      along the approach axis (not to the hole centre).
    * height is ABOVE THE PLATE TOP (the walking surface), so world z = plate_top + h.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import zlib

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- constants (see VTH_CONST.md)
HFOV_RAD = 1.2043                 # [문헌] paper realsense2.urdf.xacro:104
RES = (1280, 720)                 # [문헌] same file
CLIP = (0.1, 100.0)               # [문헌] same file
PLATE_POSE = (-13.56098, 20.2009)  # [문헌] <pose> of the plate model in BOTH worlds
STANDOFFS = (0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0)   # [방법] brief §7 grid
HEIGHTS = (0.3, 0.6, 1.0, 1.5, 2.0)                              # [문헌] brief §7 band
PITCHES_DEG = (-15.0, -5.0, +5.0)                                # [문헌] brief §7 band
CAM_CLEAR_M = 0.25       # [방법] the camera must sit this far inside solid plate
ASSET_PAD_M = 0.20       # [방법] asset AABBs are inflated by this before the "inside
                         #        an asset" test (AABBs already over-cover the mesh)
CORRIDOR_HALF_W = 0.5    # [방법] half width of the approach corridor kept clear
MIN_HOLE_PX = 1          # [방법] a pose is kept only if >=1 px of the opening's top
                         #        rim quad lands inside the image
SIZE_BANDS = [           # [방법] the size ladder the curve needs; (label, lo, hi) m^2
    ("L1", 0.70, 0.80),      # 0.97 x 0.97 m
    ("L2", 0.55, 0.65),      # 0.78 x 0.73 m
    ("M1", 0.30, 0.36),      # 0.66 x 0.66 m
    ("M2", 0.19, 0.26),      # 0.50 x 0.50 m
    ("S1", 0.13, 0.17),      # 0.39 x 0.39 m
    ("S2", 0.055, 0.070),    # 0.25 x 0.25 m
    ("T1", 0.0085, 0.0105),  # 0.10 x 0.10 m
]
DIRS = {"xp": (1.0, 0.0), "xm": (-1.0, 0.0), "yp": (0.0, 1.0), "ym": (0.0, -1.0)}
N_DIRS = 1               # [방법] approach directions kept per target hole


def rot(pitch, yaw):
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    Rz = np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]])
    Ry = np.array([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]])
    return Rz @ Ry


def project(points, eye, pitch, yaw, hfov=HFOV_RAD, res=RES):
    w, h = res
    R = rot(pitch, yaw)
    pc = (np.asarray(points, float) - np.asarray(eye, float)) @ R
    f = (w / 2.0) / math.tan(hfov / 2.0)
    fwd = pc[:, 0]
    ok = fwd > 1e-6
    uv = np.full((len(pc), 2), np.nan)
    uv[ok, 0] = w / 2.0 + f * (-pc[ok, 1] / fwd[ok])
    uv[ok, 1] = h / 2.0 + f * (-pc[ok, 2] / fwd[ok])
    return uv, ok


def quad_px_area(uv, ok, res=RES):
    """approximate on-screen area of the projected rim quad, clipped to the frame."""
    if not ok.all():
        return 0.0
    w, h = res
    x0, x1 = uv[:, 0].min(), uv[:, 0].max()
    y0, y1 = uv[:, 1].min(), uv[:, 1].max()
    ix0, ix1 = max(0.0, x0), min(float(w), x1)
    iy0, iy1 = max(0.0, y0), min(float(h), y1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    # shoelace area of the full quad, scaled by how much of its bbox is on screen
    a = 0.0
    for i in range(4):
        j = (i + 1) % 4
        a += uv[i, 0] * uv[j, 1] - uv[j, 0] * uv[i, 1]
    full = abs(a) / 2.0
    bb = max((x1 - x0) * (y1 - y0), 1e-9)
    return full * ((ix1 - ix0) * (iy1 - iy0)) / bb


def seg_hits_aabb(p0, p1, box):
    """3D segment vs axis-aligned box (x0,y0,x1,y1,z_lo,z_hi); slab method."""
    lo = np.array([box[0], box[1], box[4]], float)
    hi = np.array([box[2], box[3], box[5]], float)
    d = np.asarray(p1, float) - np.asarray(p0, float)
    t0, t1 = 0.0, 1.0
    for k in range(3):
        if abs(d[k]) < 1e-12:
            if p0[k] < lo[k] or p0[k] > hi[k]:
                return False
            continue
        a = (lo[k] - p0[k]) / d[k]
        b = (hi[k] - p0[k]) / d[k]
        if a > b:
            a, b = b, a
        t0 = max(t0, a)
        t1 = min(t1, b)
        if t0 > t1:
            return False
    return True


class Scene:
    def __init__(self, world, holes_local, grid, origin, raster_m, plate_top):
        self.world = world
        self.plate_top = plate_top
        self.grid = grid
        self.origin = origin
        self.raster = raster_m
        self.assets = [a for a in json.load(open(os.path.join(HERE, f"geom_{world}.json")))
                       if a["name"] not in ("Floor", "large_holed_floor")]
        # only things that can block a low camera / a ground-level sight line
        self.blockers = [a for a in self.assets if a["z_hi"] > plate_top + 0.02]
        self.holes = []
        for hh in holes_local:
            b = hh["local_bbox"]
            self.holes.append(dict(
                hole_id=hh["hole_id"], area_m2=hh["area_m2"], w_m=hh["w_m"], h_m=hh["h_m"],
                r_eq_m=hh["r_eq_m"], rect_fill=hh["rect_fill"], cells=hh["cells"],
                world_bbox=[round(b[0] + PLATE_POSE[0], 4), round(b[1] + PLATE_POSE[1], 4),
                            round(b[2] + PLATE_POSE[0], 4), round(b[3] + PLATE_POSE[1], 4)],
                centre=[round(hh["centroid_local"][0] + PLATE_POSE[0], 4),
                        round(hh["centroid_local"][1] + PLATE_POSE[1], 4)],
                # [실측] rectangularity separates the paper's two hole families exactly:
                # a disc fills pi/4 = 0.785 of its bbox, a square fills 1.00.
                shape=_shape(hh),
                diam_m=(round(2.0 * hh["r_eq_m"], 4) if _shape(hh) == "circle" else None)))

    def solid(self, x, y):
        i = int((x - PLATE_POSE[0] - self.origin[0]) / self.raster)
        j = int((y - PLATE_POSE[1] - self.origin[1]) / self.raster)
        if not (0 <= j < self.grid.shape[0] and 0 <= i < self.grid.shape[1]):
            return False
        return bool(self.grid[j, i])

    def solid_disc(self, x, y, r=CAM_CLEAR_M):
        n = max(1, int(r / self.raster))
        for dj in range(-n, n + 1):
            for di in range(-n, n + 1):
                if di * di + dj * dj > n * n:
                    continue
                if not self.solid(x + di * self.raster, y + dj * self.raster):
                    return False
        return True

    def inside_asset(self, x, y, z):
        for a in self.assets:
            b = a["world_aabb"]
            if (b[0] - ASSET_PAD_M <= x <= b[2] + ASSET_PAD_M
                    and b[1] - ASSET_PAD_M <= y <= b[3] + ASSET_PAD_M
                    and a["z_lo"] - ASSET_PAD_M <= z <= a["z_hi"] + ASSET_PAD_M):
                return a["name"]
        return None

    def blocked_by(self, eye, tgt):
        for a in self.blockers:
            b = a["world_aabb"]
            if seg_hits_aabb(eye, tgt, (b[0], b[1], b[2], b[3], a["z_lo"], a["z_hi"])):
                return a["name"]
        return None


def _polygon(h):
    """world-frame footprint polygon of a TARGET opening.

    Only the targets carry a polygon (keeping holes.json small); the exact footprint of
    every opening is the 1 cm boolean raster `holes_local_grid.npy`.  A square/slot is its
    bbox rectangle; a disc is sampled as a 24-gon inscribed in its bbox.
    """
    b = h["world_bbox"]
    cx, cy = 0.5 * (b[0] + b[2]), 0.5 * (b[1] + b[3])
    if h["shape"] == "circle":
        r = 0.25 * ((b[2] - b[0]) + (b[3] - b[1]))
        return [[round(cx + r * math.cos(2 * math.pi * k / 24), 4),
                 round(cy + r * math.sin(2 * math.pi * k / 24), 4)] for k in range(24)]
    return [[b[0], b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]]]


def _shape(hh):
    """[실측] the paper describes two hole families (discs r 0.05-0.8 m, squares
    <= 0.8 m^2).  Rectangularity separates them exactly -- a disc fills pi/4 = 0.785 of
    its bbox, a square fills 1.00 -- once elongated cut-outs are split off by aspect
    ratio (a 0.26 x 1.07 m slot also fills ~0.70 but is neither family)."""
    ar = max(hh["w_m"], hh["h_m"]) / max(1e-9, min(hh["w_m"], hh["h_m"]))
    if ar > 1.30:
        return "slot"
    return "circle" if hh["rect_fill"] < 0.87 else "square"


def rim_quad(hole, plate_top):
    b = hole["world_bbox"]
    return np.array([[b[0], b[1], plate_top], [b[2], b[1], plate_top],
                     [b[2], b[3], plate_top], [b[0], b[3], plate_top]], float)


def near_rim_offset(hole, d):
    """distance from the hole CENTRE to the camera, given a standoff to the near rim"""
    b = hole["world_bbox"]
    half = 0.5 * (b[2] - b[0]) if d[0] else 0.5 * (b[3] - b[1])
    return half


def dir_score(sc, hole, dvec):
    """How usable is this approach direction?

    The plate is perforated all over (270 openings in 41 x 62 m), so demanding an
    unbroken corridor of solid plate rules out almost every direction and would also
    be unfaithful to the scene -- other openings ARE in frame at long range.  What
    must hold is (i) each of the 10 camera stations stands on solid plate, and
    (ii) no asset blocks the corridor between camera and hole.
    -> score = number of usable camera stations; 0 disqualifies the direction.
    """
    c = hole["centre"]
    half = near_rim_offset(hole, dvec)
    nx, ny = -dvec[1], dvec[0]
    n_ok = 0
    for d in STANDOFFS:
        px = c[0] + dvec[0] * (half + d)
        py = c[1] + dvec[1] * (half + d)
        if not sc.solid_disc(px, py):
            continue
        blocked = False
        for s in np.arange(0.2, half + d, 0.25):
            qx = c[0] + dvec[0] * s
            qy = c[1] + dvec[1] * s
            for t in (-CORRIDOR_HALF_W, 0.0, CORRIDOR_HALF_W):
                for a in sc.blockers:
                    b = a["world_aabb"]
                    if (b[0] - 0.1 <= qx + nx * t <= b[2] + 0.1
                            and b[1] - 0.1 <= qy + ny * t <= b[3] + 0.1):
                        blocked = True
                        break
                if blocked:
                    break
            if blocked:
                break
        if not blocked:
            n_ok += 1
    return n_ok


def pick_targets(sc, per_band=1):
    chosen, notes = [], []
    for label, lo, hi in SIZE_BANDS:
        cands = [h for h in sc.holes if lo <= h["area_m2"] <= hi]
        # prefer holes near the warehouse centre (that is where the paper drives)
        cands.sort(key=lambda h: math.hypot(*h["centre"]))
        got = 0
        for h in cands:
            scored = sorted(((dir_score(sc, h, dv), dn) for dn, dv in DIRS.items()),
                            reverse=True)
            dirs = [dn for sc_, dn in scored if sc_ >= len(STANDOFFS) - 1]
            if not dirs:
                continue
            h = dict(h)
            h["band"] = label
            h["dirs"] = dirs[:N_DIRS]
            h["dir_scores"] = {dn: s_ for s_, dn in scored}
            h["footprint_polygon_world"] = _polygon(h)
            chosen.append(h)
            notes.append(f"{label}: {h['hole_id']} area {h['area_m2']:.3f} m^2 at "
                         f"({h['centre'][0]:.2f},{h['centre'][1]:.2f}) dirs {h['dirs']}")
            got += 1
            if got >= per_band:
                break
        if got == 0:
            notes.append(f"{label}: NO hole with a clear {max(STANDOFFS)+0.5:.1f} m corridor")
    return chosen, notes


def build_poses(sc, targets, occlusion=False):
    kept, skipped = [], []
    for h in targets:
        for dn in h["dirs"]:
            dv = DIRS[dn]
            yaw = math.atan2(-dv[1], -dv[0])      # camera looks back toward the hole
            half = near_rim_offset(h, dv)
            quad = rim_quad(h, sc.plate_top)
            for d in STANDOFFS:
                ex = h["centre"][0] + dv[0] * (half + d)
                ey = h["centre"][1] + dv[1] * (half + d)
                for hgt in HEIGHTS:
                    ez = sc.plate_top + hgt
                    for pd in PITCHES_DEG:
                        pid = (f"{h['hole_id']}_{dn}_d{round(d*10):02d}"
                               f"_h{round(hgt*10):02d}"
                               f"_p{'m' if pd < 0 else 'p'}{round(abs(pd)):02d}")
                        rec = dict(pose_id=pid, world=sc.world, hole_id=h["hole_id"],
                                   hole_area_m2=h["area_m2"], hole_band=h["band"],
                                   approach=dn, standoff_m=d, height_m=hgt, pitch_deg=pd,
                                   x=round(ex, 4), y=round(ey, 4), z=round(ez, 4),
                                   yaw_rad=round(yaw, 6),
                                   sdf_pitch_rad=round(-math.radians(pd), 6),
                                   hfov_rad=HFOV_RAD, res=list(RES),
                                   occlusion_intended=False)
                        if not sc.solid_disc(ex, ey):
                            rec["skip"] = "camera_not_over_solid_plate"
                            skipped.append(rec)
                            continue
                        a = sc.inside_asset(ex, ey, ez)
                        if a:
                            rec["skip"] = f"camera_inside_asset:{a}"
                            skipped.append(rec)
                            continue
                        uv, ok = project(quad, (ex, ey, ez), -math.radians(pd), yaw)
                        px = quad_px_area(uv, ok)
                        rec["rim_px_pred"] = round(float(px), 1)
                        if px < MIN_HOLE_PX:
                            rec["skip"] = "hole_outside_fov"
                            skipped.append(rec)
                            continue
                        blk = sc.blocked_by((ex, ey, ez),
                                            (h["centre"][0], h["centre"][1], sc.plate_top))
                        if blk and not occlusion:
                            rec["skip"] = f"sightline_blocked_by:{blk}"
                            skipped.append(rec)
                            continue
                        rec["occluder"] = blk
                        kept.append(rec)
    return kept, skipped


def build_occlusion_poses(sc, targets):
    """expandedworld only: poses whose sight line to the hole crosses a shelf/asset."""
    kept, skipped = [], []
    for h in targets:
        quad = rim_quad(h, sc.plate_top)
        c = h["centre"]
        for a in sc.blockers:
            b = a["world_aabb"]
            ax = 0.5 * (b[0] + b[2])
            ay = 0.5 * (b[1] + b[3])
            r = math.hypot(ax - c[0], ay - c[1])
            if r < 0.8 or r > 7.0:
                continue
            ux, uy = (ax - c[0]) / r, (ay - c[1]) / r     # hole -> asset direction
            for extra in (0.6, 1.2, 2.0):
                # camera on the far side of the asset, looking back through it
                span = max(b[2] - b[0], b[3] - b[1])
                dist = r + 0.5 * span + extra
                ex, ey = c[0] + ux * dist, c[1] + uy * dist
                for hgt in (0.3, 0.6, 1.0, 1.5):
                    ez = sc.plate_top + hgt
                    for pd in (-15.0, -5.0):
                        yaw = math.atan2(c[1] - ey, c[0] - ex)
                        oid = zlib.crc32(a["name"].encode()) % 1000
                        pid = (f"{h['hole_id']}_occ{oid:03d}"
                               f"_e{round(extra*10):02d}_h{round(hgt*10):02d}"
                               f"_p{'m' if pd < 0 else 'p'}{round(abs(pd)):02d}")
                        rec = dict(pose_id=pid, world=sc.world, hole_id=h["hole_id"],
                                   hole_area_m2=h["area_m2"], hole_band=h["band"],
                                   approach="occ", standoff_m=round(dist - 0.5 * (
                                       b[2] - b[0] if abs(ux) > abs(uy) else b[3] - b[1]), 3),
                                   height_m=hgt, pitch_deg=pd,
                                   x=round(ex, 4), y=round(ey, 4), z=round(ez, 4),
                                   yaw_rad=round(yaw, 6),
                                   sdf_pitch_rad=round(-math.radians(pd), 6),
                                   hfov_rad=HFOV_RAD, res=list(RES),
                                   occlusion_intended=True, occluder_planned=a["name"])
                        if not sc.solid_disc(ex, ey):
                            rec["skip"] = "camera_not_over_solid_plate"
                            skipped.append(rec)
                            continue
                        ia = sc.inside_asset(ex, ey, ez)
                        if ia:
                            rec["skip"] = f"camera_inside_asset:{ia}"
                            skipped.append(rec)
                            continue
                        uv, ok = project(quad, (ex, ey, ez), -math.radians(pd), yaw)
                        px = quad_px_area(uv, ok)
                        rec["rim_px_pred"] = round(float(px), 1)
                        if px < MIN_HOLE_PX:
                            rec["skip"] = "hole_outside_fov"
                            skipped.append(rec)
                            continue
                        blk = sc.blocked_by((ex, ey, ez), (c[0], c[1], sc.plate_top))
                        if not blk:
                            rec["skip"] = "no_occluder_on_sightline"
                            skipped.append(rec)
                            continue
                        rec["occluder"] = blk
                        kept.append(rec)
    return kept, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-band", type=int, default=1)
    ap.add_argument("--max-occ", type=int, default=96)
    a = ap.parse_args()

    hl = json.load(open(os.path.join(HERE, "holes_local.json")))
    grid = np.load(os.path.join(HERE, "holes_local_grid.npz"))["grid"]
    plate_top = hl["plate_top_z_local"]
    out = dict(plate_pose_xy=list(PLATE_POSE), plate_top_z=plate_top,
               plate_bottom_z=hl["plate_bottom_z_local"],
               plate_thickness_m=hl["plate_thickness_m"],
               raster_m=hl["raster_m"],
               exact_footprint_raster="holes_local_grid.npz ['grid'] (1 cm boolean grid, model frame; "
                                      "origin holes_local.json:raster_origin)",
               note=("The plate mesh and its pose are IDENTICAL in both worlds, so the 270 "
                     "openings have the same world coordinates in both -- `holes` is listed "
                     "once, not per world."),
               n_holes=hl["n_holes"], holes=None, worlds={})
    plan = []
    for world in ("eworld2", "expandedworld"):
        sc = Scene(world, hl["holes"], grid, hl["raster_origin"], hl["raster_m"], plate_top)
        tg, notes = pick_targets(sc, a.per_band)
        print(f"===== {world}: {len(sc.assets)} assets ({len(sc.blockers)} above the plate)")
        for n in notes:
            print("   ", n)
        kept, skipped = build_poses(sc, tg)
        occ_k, occ_s = ([], [])
        if world == "expandedworld":
            occ_k, occ_s = build_occlusion_poses(sc, tg)
            step = max(1, len(occ_k) // a.max_occ)
            occ_k = occ_k[::step][:a.max_occ]
        print(f"    poses kept {len(kept)} (+{len(occ_k)} occlusion)  skipped {len(skipped)}")
        from collections import Counter
        for r, n in Counter(s["skip"].split("@")[0] for s in skipped).most_common():
            print(f"      skip {r:42s} {n}")
        plan += kept + occ_k
        out["worlds"][world] = dict(
            n_assets=len(sc.assets), n_blockers=len(sc.blockers),
            targets=[{k: v for k, v in t.items()} for t in tg],
            n_kept=len(kept) + len(occ_k), n_skipped=len(skipped) + len(occ_s),
            skips=[{k: s[k] for k in ("pose_id", "skip")} for s in skipped + occ_s])
        out["holes"] = sc.holes
        # plate instances + what is (or is not) under the plate, straight from the world
        srcw = os.path.join(
            "/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/"
            "bumperbot_description/worlds", world + ".world")
        allg = json.load(open(os.path.join(HERE, f"geom_{world}.json")))
        plates = [g for g in allg if g["name"] in ("Floor", "large_holed_floor")]
        floors = [g for g in allg
                  if ("Ground" in g["name"] or "ground_plane" in g["name"]
                      or "Normalfloor" in g["name"])]
        out["worlds"][world]["source_world"] = srcw
        out["worlds"][world]["plate_instances"] = [
            dict(model=g["name"], pose=g["pose"], world_aabb=g["world_aabb"],
                 top_z=g["z_hi"], bottom_z=g["z_lo"]) for g in plates]
        out["worlds"][world]["below_the_plate"] = dict(
            floor_models=[dict(model=g["name"], pose=g["pose"], top_z=g["z_hi"],
                               world_aabb=g["world_aabb"]) for g in floors],
            note=("bottomless everywhere -- no ground plane and no floor asset in this "
                  "world (model://ground_plane is commented out)" if not floors else
                  "a floor asset covers PART of the plate; outside its world_aabb the "
                  "openings are bottomless"),
            drop_depth_m_over_floor=(round(plate_top - floors[0]["z_hi"], 4)
                                     if floors else None))
    json.dump(out, open(os.path.join(HERE, "holes.json"), "w"), indent=1, sort_keys=True)
    json.dump(plan, open(os.path.join(HERE, "plan.json"), "w"), indent=1, sort_keys=True)
    print(f"\nTOTAL planned frames: {len(plan)}")
    print(f"-> {os.path.join(HERE, 'holes.json')}\n-> {os.path.join(HERE, 'plan.json')}")


if __name__ == "__main__":
    main()
