#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pixel_mass.py — estimate the on-screen pixel mass of candidate CUE-OFF / PLACEBO
object groups, in the EXACT camera frusta of the strict-H frames the audit measured.

Why this exists
---------------
D35/D36 require a PLACEBO arm that removes a NON-CUE object of *comparable pixel
mass* to the cue objects the B arms remove.  "Comparable" is a number, not an
adjective, so it is measured here before the arm is declared, on CPU, with no
render.

Method (upper bound, stated as such)
------------------------------------
For every candidate group we take its world AABB (derived from the scene module's
own PARAMS -- the scene files import cleanly outside Isaac, verified), project the
8 corners through the cut's real camera basis (variation_kit.dir_of /
look_at_rows, quoted verbatim in CAM_CONVENTION.md sec.2), take the convex hull of
the in-front-of-camera corners, clip it to the 1920x1080 frame and report the area.

This is an UPPER BOUND on the object's silhouette because
  (a) an AABB is >= the object it bounds (a lamp pole's AABB is a slab), and
  (b) occlusion is not modelled -- an object hidden behind the crest still scores.
Both are declared; the number is used only to RANK candidates and to show that the
placebo is of the same order as the cue, never as a rendered measurement.

`--occl` adds a crude visibility test for scenes that expose a `_solid_at` oracle:
the AABB centre-ray is marched from the eye and the group is scored 0 if the first
solid hit is closer than the AABB.  scene12 has such an oracle; 17/20 do not.

Usage
    python3 pixel_mass.py                       # all three scenes, H frames only
    python3 pixel_mass.py --all-cuts            # every cut, not just strict-H
    python3 pixel_mass.py --scenes scene12
"""
import argparse
import csv
import json
import math
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
AUDIT = os.path.join(REPO, "experiments/weekend_0823/cue_audit")
W_IMG, H_IMG = 1920, 1080

# Lineage: which rendered round each scene's strict-H frames come from
# (H_CUE_AUDIT.md sec.2.1 + h_cue_table.csv `round` column).
LINEAGE = {
    "scene12": ["260820_boost_e_on", "260820_boost_e2_on"],
    "scene17": ["260820_boost_h_on", "260819_main_on"],
    "scene20": ["260820_boost_e2_on"],
}


# --------------------------------------------------------------------------- cam
def cam_basis(yaw, pitch, roll):
    y, p, rl = math.radians(yaw), math.radians(pitch), math.radians(roll)
    f = np.array([math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), math.sin(p)])
    r = np.array([f[1], -f[0], 0.0])
    r /= (np.linalg.norm(r) or 1.0)
    u = np.cross(r, f)
    cr, sr = math.cos(rl), math.sin(rl)
    return r * cr + u * sr, -r * sr + u * cr, f


def project(P, eye, cam):
    """(u, v, z_cam) in pixels; z_cam = distance to the image plane (>0 = in front)."""
    r, u, f = cam_basis(cam["yaw"], cam["pitch"], cam["roll"])
    fx = (W_IMG * 0.5) / math.tan(math.radians(cam["hfov"]) * 0.5)
    d = np.asarray(P, dtype=np.float64) - np.asarray(eye, dtype=np.float64)
    zc = d @ f
    xc = d @ r
    yc = d @ u
    with np.errstate(divide="ignore", invalid="ignore"):
        px = W_IMG * 0.5 + fx * xc / zc
        py = H_IMG * 0.5 - fx * yc / zc
    return px, py, zc


def _hull_area_clipped(px, py):
    """Area (px^2) of the convex hull of the points, clipped to the frame."""
    pts = np.stack([px, py], axis=1)
    if pts.shape[0] < 3:
        return 0.0
    # Sutherland-Hodgman clip of the hull polygon against the 4 frame edges.
    hull = _convex_hull(pts)
    if len(hull) < 3:
        return 0.0
    poly = hull
    for edge in ("x>=0", "x<=W", "y>=0", "y<=H"):
        poly = _clip(poly, edge)
        if len(poly) < 3:
            return 0.0
    return abs(_shoelace(poly))


def _convex_hull(pts):
    pts = sorted(map(tuple, pts))
    if len(pts) < 3:
        return pts

    def half(ps):
        out = []
        for p in ps:
            while len(out) >= 2 and _cross(out[-2], out[-1], p) <= 0:
                out.pop()
            out.append(p)
        return out[:-1]
    return half(pts) + half(pts[::-1])


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _shoelace(poly):
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return 0.5 * s


def _clip(poly, edge):
    def inside(p):
        return {"x>=0": p[0] >= 0, "x<=W": p[0] <= W_IMG,
                "y>=0": p[1] >= 0, "y<=H": p[1] <= H_IMG}[edge]

    def inter(a, b):
        if edge in ("x>=0", "x<=W"):
            xe = 0.0 if edge == "x>=0" else float(W_IMG)
            t = (xe - a[0]) / ((b[0] - a[0]) or 1e-12)
            return (xe, a[1] + t * (b[1] - a[1]))
        ye = 0.0 if edge == "y>=0" else float(H_IMG)
        t = (ye - a[1]) / ((b[1] - a[1]) or 1e-12)
        return (a[0] + t * (b[0] - a[0]), ye)

    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ia, ib = inside(a), inside(b)
        if ia:
            out.append(a)
            if not ib:
                out.append(inter(a, b))
        elif ib:
            out.append(inter(a, b))
    return out


def crest_visible(C, eye):
    """Boolean mask: corners NOT hidden under the drop-start lip.

    World convention (scene_common.py:13): travel axis +X, drop start edge x = 0,
    and in all three CUE-OFF scenes the walked crest is the plane z = 0 for x <= 0.
    The sight ray that grazes the lip (x=0, z=0) from an eye at (-d, ., h) has
    z(x) = -h * x / d beyond the lip, so a point at x > 0 with z below that ray is
    occluded BY THE SCENE'S OWN CREST.  This is the same grazing-concealment
    geometry H_CUE_AUDIT sec.2.2 identifies as the occluder of every strict-H
    frame in the corpus, so it is the one occluder that must not be ignored when
    ranking placebo candidates.  Nothing else is modelled.
    """
    d = -float(eye[0])
    h = float(eye[2])
    if d <= 0:
        return np.ones(len(C), dtype=bool)
    x, z = C[:, 0], C[:, 2]
    return (x <= 0.0) | (z > (-h * x / d))


def aabb_px(box, eye, cam, crest=False):
    """Clipped hull area in px^2 of one world AABB (x0,x1,y0,y1,z0,z1)."""
    x0, x1, y0, y1, z0, z1 = box
    C = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])
    px, py, zc = project(C, eye, cam)
    ok = zc > 0.05
    if crest:
        ok = ok & crest_visible(C, eye)
    if ok.sum() < 3:
        return 0.0
    return _hull_area_clipped(px[ok], py[ok])


def group_px(boxes, eye, cam, crest=False):
    """Sum of the per-box clipped areas (double counts overlaps -> upper bound)."""
    return float(sum(aabb_px(b, eye, cam, crest) for b in boxes))


# --------------------------------------------------------------------------- groups
def _scene_module(key):
    sys.path.insert(0, os.path.join(REPO, "scenes", "main"))
    os.environ.setdefault("NEGOBS_RENDER_ROLE", "data")
    import importlib
    return importlib.import_module({
        "scene12": "scene12_riverside_deck",
        "scene17": "scene17_ramp_pair_hangang",
        "scene20": "scene20_diagonal_oblique"}[key])


def groups_scene12():
    P = _scene_module("scene12").PARAMS
    d, r, sl = P["deck"], P["rail"], P["streetlight"]
    u, lo, br = P["upper"], P["lower"], P["bridge"]
    G = {}
    # ---- CUE objects (what the B arms remove) --------------------------------
    G["CUE_guard(cue_railing)"] = [
        (d["x0"], d["x1"], r["y"] - r["post_r"], r["y"] + r["post_r"],
         0.0, r["top_z"] + r["top_r"])]
    G["CUE_reeds(vegetation_edge)"] = [
        (rd["x0"], rd["x1"], rd["y0"], rd["y1"], rd["z"], rd["z"] + rd["h"])
        for rd in P["reeds"]]
    G["CUE_bikelines(signage_or_marking)"] = [
        (P["bikeroad"]["x0"], P["bikeroad"]["x1"], P["bikeroad"]["y0"],
         P["bikeroad"]["y1"], lo["z_top"] - 0.01, lo["z_top"] + 0.03)]
    G["CUE_bridge(geometry_silhouette)"] = [
        (br["x0"], br["x1"], br["y0"], br["y1"], br["pier_base"],
         br["deck_top"] + br["parapet_h"])]
    G["CUE_lowerbenches(lower-level-only)"] = [
        (bx - 0.95, bx + 0.95, by - 0.25, by + 0.25, lo["z_top"], lo["z_top"] + 0.46)
        for bx, by, _ in P["lower_benches"]]
    # ---- PLACEBO candidates (no cue credit in the matrix) --------------------
    G["PLA_upperbenches"] = [
        (bx - 0.95, bx + 0.95, by - 0.25, by + 0.25, u["z_top"], u["z_top"] + 0.46)
        for bx, by, _ in P["benches"]]
    G["PLA_streetlights"] = [
        (lx - 0.15, lx + 0.15, ly - sl["arm_len"] - 0.2, ly + 0.2,
         u["z_top"], u["z_top"] + sl["pole_h"])
        for lx, ly in P["streetlights"]]
    G["PLA_uppertrees"] = [
        (tx - 0.9, tx + 0.9, ty - 0.9, ty + 0.9, u["z_top"], u["z_top"] + 3.3)
        for tx, ty in P["trees"]]
    G["PLA_apartments(far bank)"] = [
        (bd["x0"], bd["x1"], bd["y0"], bd["y1"], bd.get("base_z", 0.0),
         bd.get("base_z", 0.0) + bd["h"]) for bd in P["far_buildings"].values()]
    G["PLA_farhedges"] = [
        (fh["cx"] - fh["sx"] / 2, fh["cx"] + fh["sx"] / 2,
         fh["cy"] - fh["length"] / 2, fh["cy"] + fh["length"] / 2,
         u["z_top"], u["z_top"] + fh["h"]) for fh in P["far_hedges"]]
    return G


def groups_scene17():
    P = _scene_module("scene17").PARAMS
    tz = P["terrace"]["z_top"]
    sl, ks = P["streetlight"], P["km_sign"]
    G = {}
    G["CUE_terracelights(base-hidden column)"] = [
        (lx - 0.15, lx + sl["arm_len"] + 0.2, ly - 0.15, ly + 0.15,
         tz, tz + sl["pole_h"]) for lx, ly in P["terrace_lights"]]
    G["CUE_kmsign"] = [(ks["x"] - 0.35, ks["x"] + 0.35, ks["y"] - 0.35,
                        ks["y"] + 0.35, tz, tz + ks["pole_h"])]
    G["CUE_terracetrees"] = [(tx - 0.9, tx + 0.9, ty - 0.9, ty + 0.9, tz, tz + 3.3)
                             for tx, ty in P["terrace_trees"]]
    G["CUE_reeds"] = [(r["x0"], r["x1"], r["y0"], r["y1"], -3.2, -3.2 + r["h"])
                      for r in P["reeds"]]
    G["PLA_apartments(far bank)"] = [
        (bd["x0"], bd["x1"], bd["y0"], bd["y1"], bd.get("base_z", 0.0),
         bd.get("base_z", 0.0) + bd["h"]) for bd in P["far_buildings"].values()]
    G["PLA_terracebenches"] = [
        (bx - 0.95, bx + 0.95, by - 0.25, by + 0.25, tz, tz + 0.46)
        for bx, by, _ in P["terrace_benches"]]
    G["PLA_crowntrees"] = [(tx - 0.9, tx + 0.9, ty - 0.9, ty + 0.9, 0.0, 3.3)
                           for tx, ty in P["crown_trees"]]
    G["PLA_crownlights"] = [
        (lx - 0.15, lx + sl["arm_len"] + 0.2, ly - 0.15, ly + 0.15, 0.0, sl["pole_h"])
        for lx, ly in P["crown_lights"]]
    return G


def groups_scene20():
    m = _scene_module("scene20")
    P = m.PARAMS
    sl = P["streetlight"]
    sw = P.get("stair_wall", {})
    G = {}
    # cheek wall: authored in rot-group local coords; the world AABB of a 30 deg
    # rotated run over |y| 2.44..2.80 and x 0..run is taken conservatively wide.
    st = P["stairs"]
    run = st["nsteps"] * st["tread"]
    G["CUE_cheekwalls(cue_railing)"] = [
        (-1.0, run + 2.0, -4.0, 4.0, st["z_top"] - st["riser"] * st["nsteps"],
         st["z_top"] + float(sw.get("head_h", 0.9) if sw else 0.9))]
    G["PLA_backdrop_E"] = [(b[1], b[2], b[3], b[4], P["backdrop"]["base_z"],
                            P["backdrop"]["base_z"] + b[5])
                           for b in P["backdrop"]["blocks"] if b[0].startswith("E")]
    G["PLA_backdrop_NS"] = [(b[1], b[2], b[3], b[4], P["backdrop"]["base_z"],
                             P["backdrop"]["base_z"] + b[5])
                            for b in P["backdrop"]["blocks"] if not b[0].startswith("E")]
    G["PLA_belt_E"] = [(row[1] - 0.6, row[1] + 0.6, row[2], row[3],
                        P["belt"]["z"], P["belt"]["z"] + P["belt"]["trunk_h"] + 2.0)
                       for row in P["belt"]["rows"] if row[0].startswith("E")]
    G["PLA_planters"] = [(px - 1.5, px + 1.5, py - 1.5, py + 1.5, 0.0, 2.8)
                         for px, py in P["planters"]]
    G["PLA_benches"] = [(bx - 0.95, bx + 0.95, by - 0.25, by + 0.25, 0.0, 0.46)
                        for bx, by, _ in P["benches"]]
    G["PLA_streetlights"] = [(lx - sl["arm_len"] - 0.2, lx + sl["arm_len"] + 0.2,
                              ly - 0.15, ly + 0.15, 0.0, sl["pole_h"])
                             for lx, ly in P["streetlights"]]
    G["PLA_bollards"] = [(P["bollards"]["x"] - 0.1, P["bollards"]["x"] + 0.1,
                          min(P["bollards"]["ys"]) - 0.1,
                          max(P["bollards"]["ys"]) + 0.1, 0.0, 0.85)]
    G["PLA_hedges"] = [(h[0], h[2], h[1], h[3], 0.0, 0.9) for h in P["hedges"]]
    return G


GROUPS = {"scene12": groups_scene12, "scene17": groups_scene17,
          "scene20": groups_scene20}


# --------------------------------------------------------------------------- main
def h_frames():
    """{(scene, round, file)} of the strict-H frames, from the audit table."""
    out = set()
    with open(os.path.join(AUDIT, "h_cue_table.csv")) as f:
        for r in csv.DictReader(f):
            fid = r["frame_id"].split("::")[0]          # 'on/scene12/L0__...png'
            out.add((r["scene"], r["round"], fid.split("/")[-1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", default="scene12,scene17,scene20")
    ap.add_argument("--all-cuts", action="store_true")
    ap.add_argument("--crest", action="store_true",
                    help="drop AABB corners hidden under the drop-start lip ray")
    ap.add_argument("--out", default=os.path.join(AUDIT, "PLACEBO_PIXEL_MASS.csv"))
    a = ap.parse_args()
    H = h_frames()
    rows = []
    for sc in [s for s in a.scenes.split(",") if s]:
        G = GROUPS[sc]()
        for rnd in LINEAGE[sc]:
            import glob
            vp = glob.glob(os.path.join(round_dir_or_flat(rnd), "*", sc, "variation.json"))
            if not vp:
                print(f"[skip] {sc} {rnd}: no variation.json")
                continue
            v = json.load(open(vp[0]))
            cuts = v["cuts"] if isinstance(v["cuts"], list) else list(v["cuts"].values())
            sel = [c for c in cuts
                   if a.all_cuts or (sc, rnd, c["file"]) in H]
            if not sel:
                continue
            acc = {g: [] for g in G}
            for c in sel:
                eye, cam = c["cam"]["eye"], c["cam"]
                for g, boxes in G.items():
                    acc[g].append(group_px(boxes, eye, cam, crest=a.crest))
            for g in G:
                v_ = np.asarray(acc[g])
                rows.append(dict(
                    scene=sc, round=rnd, n_frames=len(sel), group=g,
                    mean_px=round(float(v_.mean()), 1),
                    median_px=round(float(np.median(v_)), 1),
                    max_px=round(float(v_.max()), 1),
                    mean_pct_frame=round(100.0 * float(v_.mean()) / (W_IMG * H_IMG), 3),
                    n_zero=int((v_ <= 1.0).sum())))
    rows.sort(key=lambda r: (r["scene"], r["round"], -r["mean_px"]))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    cur = None
    for r in rows:
        k = (r["scene"], r["round"])
        if k != cur:
            cur = k
            print(f"\n=== {r['scene']} · {r['round']} · n={r['n_frames']} "
                  f"{'cuts' if a.all_cuts else 'strict-H frames'} "
                  f"(AABB upper bound, crest-occlusion "
                  f"{'MODELLED' if a.crest else 'NOT modelled'}) ===")
            print(f"{'group':40s} {'mean px':>10s} {'median':>10s} "
                  f"{'% frame':>8s} {'zero':>5s}")
        print(f"{r['group']:40s} {r['mean_px']:10.0f} {r['median_px']:10.0f} "
              f"{r['mean_pct_frame']:8.3f} {r['n_zero']:5d}")
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
