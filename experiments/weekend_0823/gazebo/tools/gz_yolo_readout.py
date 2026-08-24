#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gz_yolo_readout.py — detection-side readout of the frozen Gazebo track.

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= python3 tools/gz_yolo_readout.py

Mirrors `tools/collect_csv.py`'s population discipline exactly:
  * headline = the SEVEN negobs presets only (`rs_h0.125_*` kept in the CSV, out of
    every headline number -- GAZEBO_TRACK.md sec.6);
  * one frame per view (`_000`), because the renderer is deterministic
    (GAZEBO_TRACK.md sec.7-6).  `_001/_002` are still scored, as a gate.
  * tau_conf 0.25 -- the frozen detector operating point (runs/yolo_s*/eval_test/
    metrics.json -> tau_op), applied to boxes predicted at a 0.05 floor.

THE DROP'S TRUE IMAGE REGION -- projected, not eyeballed
    Every world is a rectangular prism cut into a flat deck and both the prism and
    the camera pose are literals in `make_worlds.py`, so the region a detector
    *should* box is computable to the pixel.  We reproduce the DAYRUN detection
    ground truth convention (`code/yolo/amodal_masks.py`): the AMODAL silhouette
    of the hazard PRISM [z_on, z_off] over the footprint, occlusion ignored --
    which is why the H world (gz_drop3, hazard 0 visible px) still has a region.
    Projection is `infer_photo.project` (== `labeler.project` algebra), the very
    function the seg arm used on these same frames.

    Two variants are reported for every world:
      R_wedge  footprint clipped to the labelled polar wedge (range < 12 m,
               |az| < 31.1 deg) -- the conservative one, and the domain the
               20-cell readout lives in.  HEADLINE.
      R_full   unclipped footprint (amodal_masks.py's default).  For gz_drop2 the
               hazard is the whole sunken level out to x = 120 m, so R_full is a
               huge band and any box under the lip line "overlaps" it -- reported
               as the permissive bound, never as the headline.

OUTPUT (all under out_yolo/, nothing else is touched)
    boxes.csv        one row per box (all seeds, all 216 frames, floor 0.05)
    frames.csv       one row per frame x seed
    readout.json     every table in this file, machine-readable
    READOUT_YOLO.txt the printed tables
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
GZ = os.path.join(ROOT, "experiments/weekend_0823/gazebo")
CODE = os.path.join(ROOT, "experiments/mainrun_0819/code")
OUT = os.path.join(GZ, "out_yolo")
sys.path.insert(0, CODE)
sys.path.insert(0, os.path.join(CODE, "labeling"))
from labeler import cam_basis                                     # noqa: E402

GRID = json.load(open(os.path.join(CODE, "labeling/gridspec_v1.json")))
assert GRID["version"] == "PROVISIONAL-GRID-V1"
NS, NB = GRID["n_sectors"], GRID["n_bands"]
BND = GRID["band_edges_m"]
ASC = GRID["sector_edges_deg"][::-1]                # ascending
CELLS = [f"{s}{b}" for b in GRID["band_names"] for s in GRID["sector_names"]]

TAU = 0.25                                          # detector operating point (frozen)
TAU_SEG = 0.5                                       # seg operating point (frozen)
SEEDS = (42, 43, 44)

# ---------------------------------------------------------------- world geometry (make_worlds.py)
X_LIP = 12.0
PRISM = {                                           # x0, x1, |y|, z_on (floor), z_off (deck)
    "gz_drop1": dict(x0=X_LIP, x1=20.0, hy=1.10, z_on=-0.72, z_off=0.0, tier="V",
                     what="계단식 피트 (4×0.18 m = 0.72 m), 개구 8.0 × 2.2 m"),
    "gz_drop2": dict(x0=X_LIP, x1=120.0, hy=8.0, z_on=-0.80, z_off=0.0, tier="V",
                     what="수직 단차 0.80 m — 아래 층이 x=120까지 이어짐"),
    "gz_drop3": dict(x0=X_LIP, x1=15.0, hy=0.90, z_on=-0.72, z_off=0.0, tier="H",
                     what="0.72 m 피트, 앞의 0.61 m 화단벽이 완전 차폐(위험 0 px)"),
    "gz_drop4": dict(x0=X_LIP, x1=12.25, hy=0.50, z_on=-0.70, z_off=0.0, tier="E",
                     what="0.25 × 1.00 m 트렌치, 0.70 m — 테두리만 보임(d=10에서 E)"),
}
TIER_OF_VIEW = {                                    # gz_drop4 is E only at d = 10 (README sec.8.5)
    "gz_drop4": lambda v: "E" if v.endswith("_d10") else "V",
}

# ---------------------------------------------------------------- camera presets (make_worlds.py)
def build_views():
    vs = {}
    for h in (0.3, 0.9):
        for d in (2, 5, 10):
            vs[f"preset_h{h}_d{d}"] = dict(cam_x=X_LIP - d, h=h, pitch=-10.0, hfov=60.0,
                                           W=1920, H=1080, fam="negobs", d=float(d))
    vs["extra_h0.3_d1.2"] = dict(cam_x=X_LIP - 1.2, h=0.3, pitch=-10.0, hfov=60.0,
                                 W=1920, H=1080, fam="negobs", d=1.2)
    for d in (2, 5):
        vs[f"rs_h0.125_d{d}"] = dict(cam_x=X_LIP - d, h=0.125, pitch=-15.0, hfov=69.0,
                                     W=1280, H=720, fam="rs", d=float(d))
    return vs


VIEWS = build_views()
NEG7 = [v for v, m in VIEWS.items() if m["fam"] == "negobs"]        # the headline population
assert len(NEG7) == 7
VIEW_ORDER = ["extra_h0.3_d1.2", "preset_h0.3_d2", "preset_h0.3_d5", "preset_h0.3_d10",
              "preset_h0.9_d2", "preset_h0.9_d5", "preset_h0.9_d10",
              "rs_h0.125_d2", "rs_h0.125_d5"]
WORLDS = ["gz_drop1", "gz_drop1_ctrl", "gz_drop2", "gz_drop2_ctrl",
          "gz_drop3", "gz_drop3_ctrl", "gz_drop4", "gz_drop4_ctrl"]
HAZ = [w for w in WORLDS if not w.endswith("_ctrl")]


def project(pts, height, pitch_deg, hfov_deg, W, H):
    """[copy: infer_photo.project] eye at (0,0,height), yaw = roll = 0."""
    r, u, f = cam_basis(0.0, pitch_deg, 0.0)
    fx = (W * 0.5) / math.tan(math.radians(hfov_deg) * 0.5)
    rel = np.asarray(pts, np.float64) - np.array([0.0, 0.0, float(height)])
    zc, xc, yc = rel @ f, rel @ r, rel @ (-u)
    z = np.where(zc > 0.05, zc, np.nan)
    return W * 0.5 + fx * xc / z, H * 0.5 + fx * yc / z, zc


def cell_of(x, y):
    """[copy: labeler.polar_cells] eye at origin, yaw 0 -> cell index (-1 outside)."""
    az = np.degrees(np.arctan2(y, x))
    rng = np.hypot(x, y)
    k = np.searchsorted(np.asarray(ASC), az, side="right") - 1
    b = np.searchsorted(np.asarray(BND), rng, side="right") - 1
    ok = (k >= 0) & (k < NS) & (b >= 0) & (b < NB)
    return np.where(ok, b * NS + (NS - 1 - k), -1), rng


def _boxdilate(m, r):
    """binary dilation by a (2r+1) square, integral-image, numpy only."""
    if r <= 0:
        return m
    H, W = m.shape
    p = np.zeros((H + 2 * r + 1, W + 2 * r + 1), np.int32)
    p[r + 1:r + 1 + H, r + 1:r + 1 + W] = m
    c = p.cumsum(0).cumsum(1)
    s = (c[2 * r + 1:, 2 * r + 1:] - c[:-2 * r - 1, 2 * r + 1:]
         - c[2 * r + 1:, :-2 * r - 1] + c[:-2 * r - 1, :-2 * r - 1])
    return s[:H, :W] > 0


STEP = 0.05                                          # heightmap step the labeler uses
NZ = 14                                              # z samples through the prism


def region(world, view, clip_wedge):
    """-> dict(mask, bbox, n_px, gt_cells) for the hazard prism of `world` seen from `view`."""
    g = PRISM[world.replace("_ctrl", "")]
    v = VIEWS[view]
    W, H = v["W"], v["H"]
    step = STEP if (g["x1"] - g["x0"]) < 30 else 0.20
    xs = np.arange(g["x0"], g["x1"] + 1e-9, step) - v["cam_x"]       # eye-local x
    ys = np.arange(-g["hy"], g["hy"] + 1e-9, step)
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    XX, YY = XX.ravel(), YY.ravel()
    cid, rng = cell_of(XX, YY)
    if clip_wedge:
        keep = cid >= 0
        XX, YY, cid = XX[keep], YY[keep], cid[keep]
    gt_cells = sorted(set(int(c) for c in cid if c >= 0))
    mask = np.zeros((H, W), bool)
    if XX.size:
        zs = np.linspace(g["z_on"], g["z_off"], NZ)
        P = np.stack([np.repeat(XX, NZ), np.repeat(YY, NZ), np.tile(zs, XX.size)], 1)
        px, py, zc = project(P, v["h"], v["pitch"], v["hfov"], W, H)
        fx = (W * 0.5) / math.tan(math.radians(v["hfov"]) * 0.5)
        ok = np.isfinite(px) & np.isfinite(py) & (zc > 0.05)
        px, py, zc = px[ok], py[ok], zc[ok]
        rad = np.clip(np.ceil(fx * step / np.maximum(zc, 1e-6)), 1, 48).astype(int)
        rad = 1 << np.ceil(np.log2(np.maximum(rad, 1))).astype(int)      # power-of-two buckets
        ix, iy = np.round(px).astype(int), np.round(py).astype(int)
        inb = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        for r in np.unique(rad):
            s = inb & (rad == r)
            if not s.any():
                continue
            m = np.zeros((H, W), bool)
            m[iy[s], ix[s]] = True
            mask |= _boxdilate(m, int(r))
    ys_, xs_ = np.nonzero(mask)
    bbox = (int(xs_.min()), int(ys_.min()), int(xs_.max()) + 1, int(ys_.max()) + 1) \
        if mask.any() else None
    return dict(mask=mask, bbox=bbox, n_px=int(mask.sum()), gt_cells=gt_cells)


# ---------------------------------------------------------------- det2cell rule (frozen)
def box_cells(b, v):
    """[frozen rule: code/yolo/det2cell.py] bottom-edge 3 points -> claimed cells."""
    W, H, fx = v["W"], v["H"], (v["W"] * 0.5) / math.tan(math.radians(v["hfov"]) * 0.5)
    r, u, f = cam_basis(0.0, v["pitch"], 0.0)
    x0, x1 = (b["cx"] - b["w"] / 2) * W, (b["cx"] + b["w"] / 2) * W
    yb = (b["cy"] + b["h"] / 2) * H
    out = set()
    for uu in (x0, x1, 0.5 * (x0 + x1)):
        xn, yn = (uu - W / 2) / fx, (yb - H / 2) / fx
        d = xn * r + yn * (-u) + f
        if d[2] >= 0:
            continue
        t = (0.0 - v["h"]) / d[2]
        if t <= 0:
            continue
        P = np.array([0.0, 0.0, v["h"]]) + t * d
        c, _ = cell_of(np.array([P[0]]), np.array([P[1]]))
        if c[0] >= 0:
            out.add(int(c[0]))
    return out


# ---------------------------------------------------------------- load predictions
def load_preds():
    rows = []
    for s in SEEDS:
        jdir = os.path.join(OUT, "pred", f"yolo_s{s}", "json")
        for fn in sorted(os.listdir(jdir)):
            if fn.endswith(".json"):
                rows.append(json.load(open(os.path.join(jdir, fn))))
    return rows


def load_seg(dirpath, models):
    """-> {(model, world, view): probs(20,)} from the frozen infer_photo dumps."""
    out = {}
    for fn in sorted(os.listdir(dirpath)):
        if not fn.endswith(".json"):
            continue
        m, w, v = fn[:-5].split("__")
        if m not in models:
            continue
        d = json.load(open(os.path.join(dirpath, fn)))
        assert d["cell_ids"] == CELLS, fn
        out[(m, w, v)] = np.asarray(d["probs"], float)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    preds = load_preds()
    assert len(preds) == 3 * 216, len(preds)

    # ---------- regions (world x view, hazard worlds only) --------------------
    REG = {}
    for w in HAZ:
        for v in VIEW_ORDER:
            REG[(w, v, "wedge")] = region(w, v, True)
            REG[(w, v, "full")] = region(w, v, False)

    # ---------- per-box / per-frame scoring -----------------------------------
    brows, frows = [], []
    for p in preds:
        w, v, idx, s = p["world"], p["view"], p["idx"], p["seed"]
        hz = not w.endswith("_ctrl")
        base = w.replace("_ctrl", "")
        vm = VIEWS[v]
        rw = REG[(base, v, "wedge")] if hz else None
        rf = REG[(base, v, "full")] if hz else None
        gtc = set(rw["gt_cells"]) if hz else set()
        keep = [b for b in p["boxes"] if b["conf"] >= TAU]
        claimed = set()
        nhit_w = nhit_f = ncen_w = 0
        for b in keep:
            bx = (int(round(b["x0"])), int(round(b["y0"])),
                  int(round(b["x1"])), int(round(b["y1"])))
            ov_w = ov_f = cen_w = 0
            iou_w = 0.0
            if hz:
                for tag, R, store in (("wedge", rw, "w"), ("full", rf, "f")):
                    sub = R["mask"][max(bx[1], 0):bx[3], max(bx[0], 0):bx[2]]
                    hit = int(sub.any()) if sub.size else 0
                    if store == "w":
                        ov_w = hit
                        cx, cy = int((bx[0] + bx[2]) / 2), int((bx[1] + bx[3]) / 2)
                        cen_w = int(0 <= cy < vm["H"] and 0 <= cx < vm["W"]
                                    and bool(R["mask"][cy, cx]))
                        inter = int(sub.sum()) if sub.size else 0
                        area_b = max(1, (bx[2] - bx[0]) * (bx[3] - bx[1]))
                        iou_w = inter / (area_b + R["n_px"] - inter) if R["n_px"] else 0.0
                    else:
                        ov_f = hit
            claimed |= box_cells(b, vm)
            nhit_w += ov_w
            nhit_f += ov_f
            ncen_w += cen_w
            brows.append(dict(seed=s, world=w, view=v, idx=idx, hazard=int(hz),
                              conf=round(b["conf"], 5),
                              x0=bx[0], y0=bx[1], x1=bx[2], y1=bx[3],
                              area_pct=round(100.0 * b["w"] * b["h"], 3),
                              overlap_wedge=ov_w, center_in_wedge=cen_w,
                              iou_wedge=round(iou_w, 5), overlap_full=ov_f))
        frows.append(dict(seed=s, world=w, view=v, idx=idx, hazard=int(hz),
                          fam=vm["fam"],
                          n_floor=p["n_boxes_floor"], n_tau=len(keep),
                          max_conf=round(max([b["conf"] for b in p["boxes"]], default=0.0), 5),
                          any_box=int(bool(keep)),
                          hit_wedge=int(nhit_w > 0), center_wedge=int(ncen_w > 0),
                          hit_full=int(nhit_f > 0),
                          cell_hit=int(bool(claimed & gtc)) if hz else 0,
                          n_claimed=len(claimed),
                          n_gt_cells=len(gtc)))

    with open(os.path.join(OUT, "boxes.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(brows[0].keys()) if brows else ["seed"])
        wr.writeheader()
        wr.writerows(brows)
    with open(os.path.join(OUT, "frames.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(frows[0].keys()))
        wr.writeheader()
        wr.writerows(frows)

    F = {(r["seed"], r["world"], r["view"], r["idx"]): r for r in frows}

    # ---------- determinism gate: _000 vs _001/_002 ---------------------------
    diff = [k for k in F if k[3] == "000"
            and any(F[(k[0], k[1], k[2], j)]["n_tau"] != F[k]["n_tau"] for j in ("001", "002"))]
    gate_det = f"{len(diff)} view가 반복 프레임에서 상자 수 불일치 (기대 0)"

    P7 = [(w, v) for w in WORLDS for v in NEG7]
    L = []                                            # printed lines

    def pr(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.append(s)

    def rate(sel, key):
        n = len(sel)
        return (sum(F[k][key] for k in sel) / n) if n else float("nan"), n

    pr("=" * 108)
    pr("GAZEBO x YOLO (frozen, tau_conf 0.25) — 검출측 판독   [진단·서술용]")
    pr("=" * 108)
    pr(f"[gate] 반복프레임 결정성: {gate_det}")
    pr(f"[gate] 모집단 = negobs 프리셋 {len(NEG7)}개 x _000  ·  rs_h0.125 2뷰는 CSV에만 (sec.6 규정)")
    pr("")

    # ---------- 1. per world x seed -----------------------------------------
    pr("1. 월드 x 시드 — 상자 수 / 발화 프레임 / 정답영역 정합 (7뷰 x _000 = 월드당 7프레임)")
    pr("-" * 108)
    pr(f"{'world':16s} {'티어':>4s} {'seed':>5s} {'상자(τ.25)':>10s} {'상자(floor.05)':>13s} "
       f"{'발화프레임':>9s} {'영역겹침':>9s} {'중심적중':>9s} {'칸정합':>7s} {'maxconf':>8s}")
    T1 = {}
    for w in WORLDS:
        base = w.replace("_ctrl", "")
        tier = PRISM[base]["tier"] if not w.endswith("_ctrl") else "ctrl"
        for s in SEEDS:
            sel = [(s, w, v, "000") for v in NEG7]
            nb = sum(F[k]["n_tau"] for k in sel)
            nfl = sum(F[k]["n_floor"] for k in sel)
            fa, n = rate(sel, "any_box")
            hw, _ = rate(sel, "hit_wedge")
            cw, _ = rate(sel, "center_wedge")
            ch, _ = rate(sel, "cell_hit")
            mc = max(F[k]["max_conf"] for k in sel)
            T1[(w, s)] = dict(n_box=nb, n_floor=nfl, any=fa, hit=hw, center=cw,
                              cell=ch, maxconf=mc, n=n)
            pr(f"{w:16s} {tier:>4s} {s:>5d} {nb:>10d} {nfl:>13d} "
               f"{fa:>9.3f} {hw:>9.3f} {cw:>9.3f} {ch:>7.3f} {mc:>8.3f}")
    pr("")

    # ---------- 2. hazard vs ctrl twin --------------------------------------
    pr("2. 하자드 vs 대조군 트윈 (3시드 pooled, 월드당 7뷰 x 3시드 = 21프레임)")
    pr("-" * 108)
    pr(f"{'pair':22s} {'HAZ 발화':>9s} {'CTL 발화(=FA)':>13s} {'HAZ 영역겹침':>12s} "
       f"{'HAZ 중심적중':>12s} {'HAZ 칸정합':>10s} {'HAZ 상자':>8s} {'CTL 상자':>8s}")
    T2 = {}
    for base in HAZ:
        selh = [(s, base, v, "000") for s in SEEDS for v in NEG7]
        selc = [(s, base + "_ctrl", v, "000") for s in SEEDS for v in NEG7]
        h_any, nh = rate(selh, "any_box")
        c_any, nc = rate(selc, "any_box")
        h_hit, _ = rate(selh, "hit_wedge")
        h_cen, _ = rate(selh, "center_wedge")
        h_cell, _ = rate(selh, "cell_hit")
        nbh = sum(F[k]["n_tau"] for k in selh)
        nbc = sum(F[k]["n_tau"] for k in selc)
        T2[base] = dict(haz_fire=h_any, ctl_fire=c_any, haz_hit=h_hit, haz_center=h_cen,
                        haz_cell=h_cell, n_haz_box=nbh, n_ctl_box=nbc, n=nh)
        pr(f"{base + ' / ctrl':22s} {h_any:>9.3f} {c_any:>13.3f} {h_hit:>12.3f} "
           f"{h_cen:>12.3f} {h_cell:>10.3f} {nbh:>8d} {nbc:>8d}")
    allh = [(s, w, v, "000") for s in SEEDS for w in HAZ for v in NEG7]
    allc = [(s, w + "_ctrl", v, "000") for s in SEEDS for w in HAZ for v in NEG7]
    ah, _ = rate(allh, "any_box")
    ac, _ = rate(allc, "any_box")
    ahh, _ = rate(allh, "hit_wedge")
    ahc, _ = rate(allh, "center_wedge")
    acell, _ = rate(allh, "cell_hit")
    pr(f"{'전체 (84 vs 84)':22s} {ah:>9.3f} {ac:>13.3f} {ahh:>12.3f} {ahc:>12.3f} "
       f"{acell:>10.3f} {sum(F[k]['n_tau'] for k in allh):>8d} "
       f"{sum(F[k]['n_tau'] for k in allc):>8d}")
    pr("")

    # ---------- 3. tier verdict ---------------------------------------------
    pr("3. 티어별 판정 (하자드 팔 · 3시드 pooled)")
    pr("-" * 108)
    pr(f"{'티어':>5s} {'월드/뷰':34s} {'n':>4s} {'발화':>7s} {'영역겹침':>9s} "
       f"{'중심적중':>9s} {'칸정합':>7s} {'maxconf':>8s}")
    TIERSEL = {
        "V": [(w, v) for w in ("gz_drop1", "gz_drop2") for v in NEG7]
             + [("gz_drop4", v) for v in NEG7 if not v.endswith("_d10")],
        "E": [("gz_drop4", v) for v in NEG7 if v.endswith("_d10")],
        "H": [("gz_drop3", v) for v in NEG7],
    }
    T3 = {}
    for t, wv in TIERSEL.items():
        sel = [(s, w, v, "000") for s in SEEDS for (w, v) in wv]
        f_, n = rate(sel, "any_box")
        h_, _ = rate(sel, "hit_wedge")
        c_, _ = rate(sel, "center_wedge")
        cc, _ = rate(sel, "cell_hit")
        mc = max(F[k]["max_conf"] for k in sel)
        lab = {"V": "drop1+drop2 7뷰, drop4 d≠10 5뷰", "E": "drop4 d=10 2뷰",
               "H": "drop3 7뷰"}[t]
        T3[t] = dict(fire=f_, hit=h_, center=c_, cell=cc, n=n, maxconf=mc)
        pr(f"{t:>5s} {lab:34s} {n:>4d} {f_:>7.3f} {h_:>9.3f} {c_:>9.3f} {cc:>7.3f} {mc:>8.3f}")
    pr("")

    # ---------- 4. seg side (frozen dumps) -----------------------------------
    SEG = {}
    SEG.update({("v2_" + k[0], k[1], k[2]): v for k, v in
                load_seg(os.path.join(GZ, "out", "json"),
                         {f"{m}_s{s}" for m in ("rgb", "b2") for s in SEEDS}).items()})
    SEG.update({("v3a_" + k[0], k[1], k[2]): v for k, v in
                load_seg(os.path.join(GZ, "out_v3", "json"),
                         {f"rgb_s{s}" for s in SEEDS}).items()})
    FAMS = [("v2 rgb", ["v2_rgb_s%d" % s for s in SEEDS]),
            ("v2 b2", ["v2_b2_s%d" % s for s in SEEDS]),
            ("v3-A rgb", ["v3a_rgb_s%d" % s for s in SEEDS])]

    def seg_rates(models, worlds, views):
        fire = hit = n = 0
        for m in models:
            for w in worlds:
                for v in views:
                    p = SEG[(m, w, v)]
                    n += 1
                    fire += int((p >= TAU_SEG).any())
                    gt = REG[(w.replace("_ctrl", ""), v, "wedge")]["gt_cells"]
                    if not w.endswith("_ctrl") and gt:
                        hit += int((p[gt] >= TAU_SEG).any())
        return (fire / n if n else float("nan")), (hit / n if n else float("nan")), n

    pr("4. 두 계통 합산표 — 발화율 vs 정답영역 정합률 (하자드 팔 · 3시드 pooled · 7뷰)")
    pr("-" * 108)
    pr(f"{'계통':12s} {'대상':28s} {'n':>4s} {'발화율':>8s} {'정답영역 정합률':>16s} "
       f"{'대조군 발화(FA)':>15s} {'(영상영역 정합)':>15s}")
    T4 = []
    for t, wv in (("V", TIERSEL["V"]), ("E", TIERSEL["E"]), ("H", TIERSEL["H"])):
        for lab, ms in FAMS:
            ws = sorted({w for w, _ in wv})
            vs = sorted({v for _, v in wv})
            wv_set = set(wv)
            fire = hit = n = 0
            for m in ms:
                for (w, v) in wv:
                    p = SEG[(m, w, v)]
                    n += 1
                    fire += int((p >= TAU_SEG).any())
                    gt = REG[(w, v, "wedge")]["gt_cells"]
                    hit += int(bool(gt) and (p[gt] >= TAU_SEG).any())
            fa = fan = 0
            for m in ms:
                for (w, v) in wv:
                    p = SEG[(m, w + "_ctrl", v)]
                    fan += 1
                    fa += int((p >= TAU_SEG).any())
            row = dict(tier=t, family=lab, n=n, fire=fire / n, hit=hit / n, fa=fa / fan)
            T4.append(row)
            pr(f"{lab:12s} {t + ' 티어 ' + ','.join(sorted({w for w, _ in wv})):28s} {n:>4d} "
               f"{fire / n:>8.3f} {hit / n:>16.3f} {fa / fan:>15.3f} {'—':>15s}")
        sel = [(s, w, v, "000") for s in SEEDS for (w, v) in wv]
        selc = [(s, w + "_ctrl", v, "000") for s in SEEDS for (w, v) in wv]
        f_, n = rate(sel, "any_box")
        cc, _ = rate(sel, "cell_hit")
        cw, _ = rate(sel, "center_wedge")
        fa_, _ = rate(selc, "any_box")
        T4.append(dict(tier=t, family="YOLO(검출)", n=n, fire=f_, hit=cc,
                       hit_img=cw, fa=fa_))
        pr(f"{'YOLO(검출)':12s} {t + ' 티어 ' + ','.join(sorted({w for w, _ in wv})):28s} "
           f"{n:>4d} {f_:>8.3f} {cc:>16.3f} {fa_:>15.3f} {cw:>15.3f}")
        pr("")

    # ---------- 5. region provenance -----------------------------------------
    pr("5. 낙차 영역(투영) — 하자드 월드 x 7뷰, R_wedge / R_full 픽셀 수 · GT 칸 수")
    pr("-" * 108)
    pr(f"{'world':10s} {'view':18s} {'R_wedge px':>11s} {'R_full px':>11s} "
       f"{'화면비%':>8s} {'GT칸':>5s} {'bbox(wedge)':>26s}")
    T5 = []
    for w in HAZ:
        for v in VIEW_ORDER:
            rw, rf = REG[(w, v, "wedge")], REG[(w, v, "full")]
            vm = VIEWS[v]
            pct = 100.0 * rw["n_px"] / (vm["W"] * vm["H"])
            T5.append(dict(world=w, view=v, wedge_px=rw["n_px"], full_px=rf["n_px"],
                           pct=pct, gt_cells=len(rw["gt_cells"]), bbox=rw["bbox"]))
            if vm["fam"] == "negobs":
                pr(f"{w:10s} {v:18s} {rw['n_px']:>11d} {rf['n_px']:>11d} {pct:>8.2f} "
                   f"{len(rw['gt_cells']):>5d} {str(rw['bbox']):>26s}")
    pr("")

    # ---------- 6. every box, listed -----------------------------------------
    pr("6. τ 0.25 이상 상자 전량 (216 x 3 시드 = 648 프레임에서)")
    pr("-" * 108)
    if brows:
        pr(f"{'seed':>5s} {'world':16s} {'view':18s} {'idx':>4s} {'conf':>6s} "
           f"{'box(px)':>28s} {'면적%':>7s} {'영역겹침':>8s} {'중심':>5s} {'IoU':>6s}")
        for b in sorted(brows, key=lambda r: (-r["conf"], r["world"], r["view"])):
            pr(f"{b['seed']:>5d} {b['world']:16s} {b['view']:18s} {b['idx']:>4s} "
               f"{b['conf']:>6.3f} "
               f"{('(%d,%d)-(%d,%d)' % (b['x0'], b['y0'], b['x1'], b['y1'])):>28s} "
               f"{b['area_pct']:>7.1f} "
               f"{b['overlap_wedge']:>8d} {b['center_in_wedge']:>5d} {b['iou_wedge']:>6.3f}")
    else:
        pr("  (상자 0건)")
    pr("")

    # ---------- 6b. twin-identity: does the same box survive hazard removal? --
    pr("6b. 트윈 동형 검사 — 같은 시드·같은 뷰에서 하자드 팔 상자가 대조군에도 나오는가")
    pr("-" * 108)
    pr(f"{'seed':>5s} {'world':10s} {'view':18s} {'HAZ conf':>9s} {'CTL conf':>9s} "
       f"{'Δconf':>7s} {'상자 IoU(HAZ↔CTL)':>18s}")
    BB = {}
    for b in brows:
        BB.setdefault((b["seed"], b["world"], b["view"], b["idx"]), []).append(b)
    T6b = []
    for base in HAZ:
        for v in VIEW_ORDER:
            for s in SEEDS:
                hb = BB.get((s, base, v, "000"), [])
                cb = BB.get((s, base + "_ctrl", v, "000"), [])
                if not (hb or cb):
                    continue
                h0 = max(hb, key=lambda r: r["conf"]) if hb else None
                c0 = max(cb, key=lambda r: r["conf"]) if cb else None
                iou = float("nan")
                if h0 and c0:
                    ix0, iy0 = max(h0["x0"], c0["x0"]), max(h0["y0"], c0["y0"])
                    ix1, iy1 = min(h0["x1"], c0["x1"]), min(h0["y1"], c0["y1"])
                    inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
                    ah = (h0["x1"] - h0["x0"]) * (h0["y1"] - h0["y0"])
                    ac = (c0["x1"] - c0["x0"]) * (c0["y1"] - c0["y0"])
                    iou = inter / (ah + ac - inter) if (ah + ac - inter) else 0.0
                T6b.append(dict(seed=s, world=base, view=v,
                                haz=h0["conf"] if h0 else None,
                                ctl=c0["conf"] if c0 else None, iou=iou))
                hs = ("%.3f" % h0["conf"]) if h0 else "—"
                cs = ("%.3f" % c0["conf"]) if c0 else "—"
                dc = (h0["conf"] - c0["conf"]) if (h0 and c0) else float("nan")
                pr(f"{s:>5d} {base:10s} {v:18s} {hs:>9s} {cs:>9s} {dc:>7.3f} {iou:>18.3f}")
    pr("")

    # ---------- 7. sub-threshold diagnostic ----------------------------------
    pr("7. 문턱 아래까지 본다 — 하자드 팔 max conf 분포 (7뷰 x 3시드 = 21, floor 0.05)")
    pr("-" * 108)
    pr(f"{'world':16s} {'≥0.25':>7s} {'≥0.10':>7s} {'≥0.05':>7s} {'평균 maxconf':>13s} "
       f"{'최대':>7s}")
    T7 = {}
    for w in WORLDS:
        sel = [(s, w, v, "000") for s in SEEDS for v in NEG7]
        mc = np.array([F[k]["max_conf"] for k in sel])
        T7[w] = dict(ge25=float((mc >= .25).mean()), ge10=float((mc >= .10).mean()),
                     ge05=float((mc >= .05).mean()), mean=float(mc.mean()),
                     max=float(mc.max()))
        pr(f"{w:16s} {(mc >= .25).mean():>7.3f} {(mc >= .10).mean():>7.3f} "
           f"{(mc >= .05).mean():>7.3f} {mc.mean():>13.3f} {mc.max():>7.3f}")
    pr("")

    # ---------- 8. box size — Gazebo vs the detector's own in-domain habit ----
    pr("8. 상자 크기 — Gazebo 상자가 이상하게 큰 것인가? (in-domain Isaac test와 대조)")
    pr("-" * 108)
    IND = os.path.join(ROOT, "experiments/dayrun_0820")
    pr(f"{'set':28s} {'n(τ0.25)':>9s} {'면적% 중앙값':>13s} {'평균':>7s} {'p90':>7s} {'최대':>7s}")
    T8 = []
    for s in SEEDS:
        d = os.path.join(IND, f"runs/yolo_s{s}/pred_test/labels")
        a = []
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".txt"):
                continue
            for ln in open(os.path.join(d, fn)):
                p_ = ln.split()
                if len(p_) == 6 and float(p_[5]) >= TAU:
                    a.append(100.0 * float(p_[3]) * float(p_[4]))
        a = np.array(a)
        T8.append(dict(set=f"Isaac test (in-domain) s{s}", n=len(a),
                       med=float(np.median(a)), mean=float(a.mean()),
                       p90=float(np.percentile(a, 90)), max=float(a.max())))
        pr(f"{'Isaac test (in-domain) s' + str(s):28s} {len(a):>9d} {np.median(a):>13.2f} "
           f"{a.mean():>7.2f} {np.percentile(a, 90):>7.2f} {a.max():>7.2f}")
    ga = np.array([b["area_pct"] for b in brows if b["idx"] == "000"])
    if ga.size:
        T8.append(dict(set="Gazebo 216 (τ0.25, _000)", n=int(ga.size),
                       med=float(np.median(ga)), mean=float(ga.mean()),
                       p90=float(np.percentile(ga, 90)), max=float(ga.max())))
        pr(f"{'Gazebo (τ0.25, _000)':28s} {ga.size:>9d} {np.median(ga):>13.2f} "
           f"{ga.mean():>7.2f} {np.percentile(ga, 90):>7.2f} {ga.max():>7.2f}")
    pr("")

    json.dump(dict(tau=TAU, tau_seg=TAU_SEG, seeds=list(SEEDS), n_frames=len(preds),
                   twin_boxes=T6b, box_area=T8,
                   gate_determinism=gate_det,
                   per_world_seed={f"{w}|{s}": v for (w, s), v in T1.items()},
                   twin={k: v for k, v in T2.items()},
                   tier=T3, combined=T4, regions=T5, subthreshold=T7,
                   n_boxes_tau=len(brows)),
              open(os.path.join(OUT, "readout.json"), "w"), indent=1)
    open(os.path.join(OUT, "READOUT_YOLO.txt"), "w").write("\n".join(L) + "\n")
    print(f"\n[done] {OUT}/READOUT_YOLO.txt · readout.json · boxes.csv · frames.csv")


if __name__ == "__main__":
    main()
