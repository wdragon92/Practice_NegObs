#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""readout.py -- every number in WAREHOUSE_VARIANT.md, computed in one place.

Populations
    approach views  8 (rs_d0.5 .. rs_d3.4).  `overview` is diagnostic and excluded.
    frame per view  `_000` only (the renderer is deterministic: _000 == _001 == _002,
                    verified by md5 in §1 of the doc).

Regions (projected analytically -- see project_hole.py; nothing is hand-annotated)
    opening    the 0.80 x 0.80 m cut in the floor plate, at plate top z = 0.1243
    void       the part of the opening still OPEN in that world:
                 wh0/wh_h/wh_hc -> the whole opening
                 wh_e           -> only x in [-3.66, -3.48] (the pallet covers the rest)
    roi        clean_yolo.py's trapezium (TOP 0.20 W, BOTTOM 0.80 W, HEIGHT 0.7 H)

Detector columns (tau 0.25 = ultralytics' predict default, i.e. what `self.model(img)` uses)
    fire        >=1 box
    hit         >=1 box overlapping `void`
    centre      >=1 box whose centre is inside `void`
    node        >=1 box passing clean_yolo.py's own obstacle gate: centre inside the
                trapezium AND conf > 0.65.  (Its other branch needs the aligned depth
                image, which static Gazebo cameras do not publish -- stated in the doc.)
    D_box       ground distance the node would have published for the best box, obtained
                by inverting the paper's own pinhole model on the box BOTTOM edge
                (clean_yolo._generate_3d_points samples depth along y2):
                    D = h / tan(pitch + atan((v - cy) / f)),  h 0.125, f 931.18, cy 360
                compare with D_true = standoff (the near rim).

Ours columns (frozen cell-probability models, tau 0.5)
    fire        max cell p >= 0.5
    gt_hit      max p over the GT cells >= 0.5
    p_gt        max p over the GT cells
    GT cells    gridspec_v1 wedges any footprint sample of `void` falls into,
                decided by labeler.polar_cells -- the corpus' own wedge test.

Outputs
    out/readout.csv        64 rows = 4 worlds x 8 approach views x 2 YOLO arms, the
                           YOLO columns plus `ours_<model>_{max_p,fire,p_gt,gt_hit,
                           top_cell}` for both models (arm-independent, hence repeated).
    out/readout_ours.csv   64 rows = 2 models x 4 worlds x 8 views, ours only, long form.
    out/readout.json       rows / yolo / ours / geo.
    stdout                 the markdown tables that go into WAREHOUSE_VARIANT.md.
"""
from __future__ import annotations

import csv
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tools"))
import project_hole as P                                            # noqa: E402
from yolo_paper import trapezium, poly_fill_mask, point_in_poly     # noqa: E402

# The wedge test is NOT re-derived here: gt_cells() calls the very function that
# produced every training label, experiments/mainrun_0819/code/labeling/labeler.py.
REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
LABELING = os.path.join(REPO, "experiments", "mainrun_0819", "code", "labeling")
sys.path.insert(0, LABELING)
import labeler as L                                                 # noqa: E402

WORLDS = ["wh0", "wh_e", "wh_h", "wh_hc"]
TIER = {"wh0": "V", "wh_e": "E", "wh_h": "H", "wh_hc": "H-ctrl"}
TIERFULL = {"wh0": "V (as published)", "wh_e": "E (edge-only)",
            "wh_h": "H (hidden)", "wh_hc": "H-ctrl (no hazard)"}
TAU, GATE = 0.25, 0.65
TAU_OURS = 0.5
MODELS = ["v2_rgb_s42", "v3a_rgb_s42"]

# wh_e's pallet covers the far 0.62 m; this is what is left open.
E_VOID_X0 = P.HOLE_X0 + 0.62
GRID_PATH = os.path.join(LABELING, "gridspec_v1.json")
GRID = json.load(open(GRID_PATH))
SEC_EDGES = GRID["sector_edges_deg"]
BAND_EDGES = GRID["band_edges_m"]
CELL_IDS = [f"{s}{b}" for b in GRID["band_names"] for s in GRID["sector_names"]]

# the paper's own intrinsics (clean_yolo.py CameraConfig)
F_PAPER, CY_PAPER = 931.1829833984375, 360.0
PITCH_TRUE = 0.261          # the URDF mount, which is what actually rendered the frame
EYE_H = 0.125


def void_corners(world):
    x0 = E_VOID_X0 if world == "wh_e" else P.HOLE_X0
    return np.array([[x0, P.HOLE_Y0, P.FLOOR_TOP_Z], [P.HOLE_X1, P.HOLE_Y0, P.FLOOR_TOP_Z],
                     [P.HOLE_X1, P.HOLE_Y1, P.FLOOR_TOP_Z], [x0, P.HOLE_Y1, P.FLOOR_TOP_Z]])


def gt_cells(world, cam):
    """gridspec_v1 cells the still-OPEN void footprint falls into, from this camera.

    Sampling: a 33x33 lattice over the void rectangle on the plate top surface.
    Wedge test: `labeler.polar_cells` -- the same function, the same gridspec and the
    same "any footprint sample in wedge" rule that produced every training label, so
    the GT here is generated the way the corpus GT was, not re-derived.  The camera
    pose comes from the capture manifest (static camera models -> exact), not from a
    constant.

    For `wh_hc` (the no-hazard twin) the same rectangle is returned: there is no
    hazard there, so those cells are the WOULD-BE hole cells and p_gt on them reads
    as a false-alarm probability at the location a hole would occupy.
    """
    x0 = E_VOID_X0 if world == "wh_e" else P.HOLE_X0
    xs = np.linspace(x0, P.HOLE_X1, 33)
    ys = np.linspace(P.HOLE_Y0, P.HOLE_Y1, 33)
    XX, YY = np.meshgrid(xs, ys)
    idx, _ = L.polar_cells(XX.ravel(), YY.ravel(),
                           (cam["eye"][0], cam["eye"][1]),
                           math.degrees(cam["yaw_rad"]), GRID)
    hit = sorted({int(i) for i in idx.tolist() if i >= 0})
    return [CELL_IDS[i] for i in hit]


def box_distance(v_bottom):
    """Invert the paper's pinhole model on a box bottom edge -> ground distance (m)."""
    dep = PITCH_TRUE + math.atan((v_bottom - CY_PAPER) / F_PAPER)
    return float("inf") if dep <= 1e-4 else EYE_H / math.tan(dep)


def geometry():
    man = json.load(open(os.path.join(HERE, "frames", "wh0", "wh0_cap_manifest.json")))
    cams = {v: c for v, c in man["cameras"].items() if c["family"] == "approach"}
    views = sorted(cams, key=lambda v: cams[v]["standoff"])
    g = {}
    for v in views:
        c = cams[v]
        w, h = c["res"]
        roi = poly_fill_mask(trapezium(w, h), w, h)
        per = {}
        for wd in WORLDS:
            q, _ = P.project(void_corners(wd), c["eye"], c["pitch_rad"], c["yaw_rad"],
                             c["hfov_rad"], w, h)
            m = P.poly_mask(q, w, h)
            per[wd] = dict(mask=m, px=int(m.sum()), roi_px=int((m & roi).sum()),
                           gt=gt_cells(wd, c))
        g[v] = dict(cam=c, res=(w, h), roi=roi, per=per, standoff=c["standoff"])
    return views, g


def yolo_rows(views, g):
    rows = []
    for p in sorted(glob.glob(os.path.join(HERE, "out/yolo_paper/json/*.json"))):
        r = json.load(open(p))
        if r["view"] not in g or r["idx"] != "000":
            continue
        gv = g[r["view"]]
        W, H = gv["res"]
        m = gv["per"][r["world"]]["mask"]
        poly = np.array(r["roi_poly"])
        for arm in ("roi", "full"):
            A = r["arms"][arm]
            keep = [b for b in A["boxes"] if b["conf"] >= TAU]
            hit = centre = node = 0
            dbox = None
            for b in sorted(keep, key=lambda b: -b["conf"]):
                x0, y0 = int(max(0, b["x0"])), int(max(0, b["y0"]))
                x1, y1 = int(min(W, b["x1"])), int(min(H, b["y1"]))
                if x1 > x0 and y1 > y0 and m[y0:y1, x0:x1].any():
                    hit = 1
                    if dbox is None:
                        dbox = box_distance(b["y1"])
                cx, cy = int(b["cx"]), int(b["cy"])
                if 0 <= cy < H and 0 <= cx < W and m[cy, cx]:
                    centre = 1
                if b["conf"] > GATE and point_in_poly((cx, cy), poly):
                    node = 1
            if dbox is None and keep:
                dbox = box_distance(max(keep, key=lambda b: b["conf"])["y1"])
            rows.append(dict(world=r["world"], tier=TIER[r["world"]], view=r["view"],
                             standoff=gv["standoff"], arm=arm,
                             void_px=gv["per"][r["world"]]["px"],
                             void_roi_px=gv["per"][r["world"]]["roi_px"],
                             n_floor=A["n_floor"], n_tau=len(keep),
                             maxconf=round(max([b["conf"] for b in A["boxes"]], default=0.0), 3),
                             fire=int(bool(keep)), hit=hit, centre=centre, node=node,
                             d_box=None if dbox is None else round(dbox, 2),
                             d_true=gv["standoff"]))
    return rows


def ours_rows(views, g):
    rows = []
    for mdl in MODELS:
        for wd in WORLDS:
            for v in views:
                p = os.path.join(HERE, "out/ours/json", f"{mdl}__{wd}__{v}.json")
                if not os.path.exists(p):
                    continue
                d = json.load(open(p))
                pr = dict(zip(d["cell_ids"], d["probs"]))
                gt = g[v]["per"][wd]["gt"]
                pg = max([pr[c] for c in gt if c in pr], default=0.0)
                rows.append(dict(model=mdl, world=wd, tier=TIER[wd], view=v,
                                 standoff=g[v]["standoff"], gt_cells=",".join(gt),
                                 n_gt=len(gt), max_p=round(max(pr.values()), 3),
                                 p_gt=round(pg, 3),
                                 fire=int(max(pr.values()) >= TAU_OURS),
                                 gt_hit=int(pg >= TAU_OURS),
                                 top_cell=max(pr, key=pr.get)))
    return rows


def merged_rows(yr, orr):
    """One row per (world, approach view, YOLO arm) -- the 64-row shape out/readout.csv
    has always had -- carrying the YOLO columns unchanged PLUS both models' zero-shot
    columns for that world+view.  The `ours` numbers do not depend on the YOLO arm
    (they are read from one frame), so they are repeated on the `roi` and `full` rows
    by construction; that repetition is what keeps the file one flat table.
    A missing per-model json is a KeyError here, never a blank cell.
    """
    by = {(r["model"], r["world"], r["view"]): r for r in orr}
    out = []
    for r in yr:
        row = dict(r)
        base = by[(MODELS[0], r["world"], r["view"])]
        row["gt_cells"] = base["gt_cells"]
        row["n_gt"] = base["n_gt"]
        for mdl in MODELS:
            o = by[(mdl, r["world"], r["view"])]
            row[f"ours_{mdl}_max_p"] = o["max_p"]
            row[f"ours_{mdl}_fire"] = o["fire"]
            row[f"ours_{mdl}_p_gt"] = o["p_gt"]
            row[f"ours_{mdl}_gt_hit"] = o["gt_hit"]
            row[f"ours_{mdl}_top_cell"] = o["top_cell"]
        out.append(row)
    return out


def frac(rs, k):
    return sum(r[k] for r in rs) / (len(rs) or 1)


def main():
    views, g = geometry()
    yr, orr = yolo_rows(views, g), ours_rows(views, g)
    mr = merged_rows(yr, orr)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for name, rs in (("readout.csv", mr), ("readout_ours.csv", orr)):
        with open(os.path.join(HERE, "out", name), "w", newline="") as f:
            wtr = csv.DictWriter(f, fieldnames=list(rs[0].keys()))
            wtr.writeheader()
            wtr.writerows(rs)

    print("## G1 geometry per view (visible void, per world)\n")
    print("| view | standoff | wh0/wh_h/wh_hc opening px | wh_e visible void px | "
          "opening px inside the node's ROI | GT cells (wh0) |")
    print("|---|---|---|---|---|---|")
    for v in views:
        gv = g[v]
        print(f"| `{v}` | {gv['standoff']:.1f} m | {gv['per']['wh0']['px']:,} | "
              f"{gv['per']['wh_e']['px']:,} | {gv['per']['wh0']['roi_px']:,} | "
              f"{' '.join(gv['per']['wh0']['gt'])} |")

    for arm, lab in (("roi", "Y1 the node's real path (trapezium-masked input)"),
                     ("full", "Y2 unmasked frame (fairness control)")):
        print(f"\n## {lab}\n")
        print("| world | tier | views | boxes tau0.25 | boxes floor0.05 | fire | "
              "void-overlap | centre-in-void | node gate | max conf |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for wd in WORLDS:
            rs = [r for r in yr if r["world"] == wd and r["arm"] == arm]
            print(f"| `{wd}` | {TIERFULL[wd]} | {len(rs)} | {sum(r['n_tau'] for r in rs)} | "
                  f"{sum(r['n_floor'] for r in rs)} | {frac(rs,'fire'):.3f} | "
                  f"{frac(rs,'hit'):.3f} | {frac(rs,'centre'):.3f} | {frac(rs,'node'):.3f} | "
                  f"{max(r['maxconf'] for r in rs):.3f} |")

    print("\n## Y3 per-view, arm=roi (the node's own path)\n")
    print("| view | standoff | " + " | ".join(f"`{w}`" for w in WORLDS) + " |")
    print("|---|---|" + "---|" * len(WORLDS))
    for v in views:
        cells = []
        for wd in WORLDS:
            r = next(r for r in yr if r["world"] == wd and r["view"] == v and r["arm"] == "roi")
            tag = f"{r['n_tau']}box conf {r['maxconf']:.2f}" if r["n_tau"] else "silent"
            if r["hit"]:
                tag += " HIT"
            if r["node"]:
                tag += " GATE"
            cells.append(tag)
        print(f"| `{v}` | {g[v]['standoff']:.1f} m | " + " | ".join(cells) + " |")

    print("\n## Y4 where the node would have put the obstacle (arm=roi, best box)\n")
    print("| view | true near-rim distance | wh0 D_box | error | wh_e D_box | error |")
    print("|---|---|---|---|---|---|")
    for v in views:
        a = next(r for r in yr if r["world"] == "wh0" and r["view"] == v and r["arm"] == "roi")
        b = next(r for r in yr if r["world"] == "wh_e" and r["view"] == v and r["arm"] == "roi")
        f = lambda r: ("-", "-") if r["d_box"] is None else \
            (f"{r['d_box']:.2f} m", f"{r['d_box'] - r['d_true']:+.2f} m")
        av, ae = f(a)
        bv, be = f(b)
        print(f"| `{v}` | {a['d_true']:.2f} m | {av} | {ae} | {bv} | {be} |")

    print("\n## O1 ours, zero-shot (tau 0.5, gridspec_v1)\n")
    print("| model | world | tier | views | fire | GT-cell hit | mean max-p | mean p(GT) |")
    print("|---|---|---|---|---|---|---|---|")
    for mdl in MODELS:
        for wd in WORLDS:
            rs = [r for r in orr if r["model"] == mdl and r["world"] == wd]
            if not rs:
                continue
            print(f"| `{mdl}` | `{wd}` | {TIERFULL[wd]} | {len(rs)} | {frac(rs,'fire'):.3f} | "
                  f"{frac(rs,'gt_hit'):.3f} | "
                  f"{np.mean([r['max_p'] for r in rs]):.3f} | "
                  f"{np.mean([r['p_gt'] for r in rs]):.3f} |")

    print("\n## O2 ours per view, p(GT cells)\n")
    print("| model | view | " + " | ".join(f"`{w}`" for w in WORLDS) + " |")
    print("|---|---|" + "---|" * len(WORLDS))
    for mdl in MODELS:
        for v in views:
            cells = []
            for wd in WORLDS:
                r = next((r for r in orr if r["model"] == mdl and r["world"] == wd
                          and r["view"] == v), None)
                cells.append("-" if r is None else f"{r['p_gt']:.2f}")
            print(f"| `{mdl}` | `{v}` | " + " | ".join(cells) + " |")

    json.dump(dict(rows=mr, yolo=yr, ours=orr,
                   geo={v: {wd: {k: g[v]["per"][wd][k] for k in ("px", "roi_px", "gt")}
                            for wd in WORLDS} | {"standoff": g[v]["standoff"]}
                        for v in views}),
              open(os.path.join(HERE, "out", "readout.json"), "w"), indent=1)
    print(f"\nwrote out/readout.csv ({len(mr)} rows), out/readout_ours.csv "
          f"({len(orr)} rows), out/readout.json")


if __name__ == "__main__":
    main()
