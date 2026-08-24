#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amodal5_infer.py — aux 아모달 헤드의 **픽셀 마스크 출력 추출 + 프레임별 통계** (GPU 짧게).

    PYTHONNOUSERSITE=1 flock -o /tmp/negobs_gpu.lock \
      python3 experiments/v3_0823/code/amodal5_infer.py [--device cuda] [--force]

두 체크포인트를 **같은 프레임 · 같은 전처리**로 통과시킨다.
    v2gen  experiments/dayrun_0820/runs/v2/rgb_s42_aux/best.pt   (v2 세대 · 격리 없음)
    v3gen  experiments/v3_0823/runs/v3a/rgb_s42_aux/best.pt      (v3-A 격리 aux 런)

[격리·진단] 두 런 모두 **훼손된 학습**이다 (v2: 타깃 57.8% 거짓 공백 · v3: A팔 648/2,598
프레임만 마스크). 여기서 나오는 어떤 수도 PREREG A/B 판정에 쓰지 않는다.

전처리는 `polar_dataset.PolarGridDataset._load_x` 와 **바이트 동일**:
    RGB -> 512x512 BILINEAR squash -> /255 -> ImageNet 정규화.
따라서 마스크 출력도 512x512 squash 공간이고, GT 아모달 PNG(960x540)도 훈련 때와 같은
`load_aux_mask` 규칙(NEAREST -> >127)으로 512로 맞춘다.

프레임별로 계산하는 것
    (a) 마스크 품질 : IoU@0.5 · 덮음(recall)@0.5 · 정밀도@0.5 · GT 안 평균확률
    (b) 질량 배치   : GT 아모달 영역(R1) / 경계 링 24px(R2) / 좌우거울 대조(R_mir) /
                      가림물 몸체 근사(R_occ, 깊이 연결성) / 그 외(R3) 의 질량·면적·밀도
    (d) 마스크->칸  : 20칸 지면 쐐기를 512 공간에 래스터화해 쐐기 안 평균확률 = 파생 칸 점수.
                      같은 forward 의 직접 칸 헤드 확률과 나란히 저장한다 (세대 교차 없음).

산출 -> experiments/v3_0823/amodal5/records.npz  (+ index.json · panel_masks.npz)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch
from PIL import Image, ImageDraw

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
OUTD = os.path.join(V3, "amodal5")
MAINCODE = os.path.join(ROOT, "experiments/mainrun_0819/code")
sys.path.insert(0, MAINCODE)
sys.path.insert(0, os.path.join(MAINCODE, "labeling"))

import model_factory                                        # noqa: E402
import labeler as L                                         # noqa: E402
from polar_dataset import IMAGENET_MEAN, IMAGENET_STD       # noqa: E402

CKPTS = dict(v2gen=os.path.join(DAY, "runs/v2/rgb_s42_aux/best.pt"),
             v3gen=os.path.join(V3, "runs/v3a/rgb_s42_aux/best.pt"))
S = 512                                    # img_size (두 config 모두 512)
GRIDPATH = os.path.join(MAINCODE, "labeling/gridspec_v1.json")
GSPEC = json.load(open(GRIDPATH))
CELLS = [f"{s}{b}" for b in GSPEC["band_names"] for s in GSPEC["sector_names"]]
NS, NB = GSPEC["n_sectors"], GSPEC["n_bands"]
ASC = GSPEC["sector_edges_deg"][::-1]
BND = GSPEC["band_edges_m"]
assert len(CELLS) == 20 and GSPEC["version"] == "PROVISIONAL-GRID-V1"

RING_PX = 24                               # 경계 링 폭 (512 공간)
NEIGH_PX = 96                              # 가림물 몸체 근사의 탐색 반경
OCC_TOL_M = 1.5                            # 깊이 유사 허용폭


# ------------------------------------------------------------------ 기하 (복사)
def cam_of(rgb_path):
    sdir, fn = os.path.dirname(rgb_path), os.path.basename(rgb_path)
    cuts = json.load(open(os.path.join(sdir, "variation.json")))["cuts"]
    cuts = list(cuts.values()) if isinstance(cuts, dict) else cuts
    return next(c["cam"] for c in cuts if c["file"] == fn)


def wedge_px(cell, cam, n=36):
    """[복사: verdict_panel_detvsours.py L134-154] 지면 쐐기 -> 이미지 다각형."""
    i = CELLS.index(cell)
    b, si = i // NS, i % NS
    k = NS - 1 - si
    a0, a1 = math.radians(ASC[k]), math.radians(ASC[k + 1])
    r0, r1 = BND[b], BND[b + 1]
    eye = np.asarray(cam["eye"], dtype=np.float64)
    yaw = math.radians(cam["yaw"])
    cy, sy = math.cos(yaw), math.sin(yaw)
    ring = ([(r1, a) for a in np.linspace(a0, a1, n)] +
            [(r0, a) for a in np.linspace(a1, a0, n)])
    pts = []
    for r, a in ring:
        xc, yc = r * math.cos(a), r * math.sin(a)
        pts.append([eye[0] + xc * cy - yc * sy, eye[1] + xc * sy + yc * cy,
                    float(cam["ground_z"])])
    px, py, zc, inb = L.project(np.asarray(pts), eye, cam)
    return px, py, zc > 0.05


def cellmap_of(cam):
    """512x512 int8 칸 지도 (-1 = 어느 칸도 아님). 먼 밴드부터 그려 가까운 밴드가 덮는다."""
    im = Image.new("L", (S, S), 255)                 # 255 = 어느 칸도 아님
    dr = ImageDraw.Draw(im)
    valid = np.zeros(20, bool)
    sx, sy = S / L.W_IMG, S / L.H_IMG
    for i in range(19, -1, -1):
        px, py, front = wedge_px(CELLS[i], cam)
        if not front.all():
            continue
        X, Y = px * sx, py * sy
        if X.max() < 0 or X.min() > S or Y.max() < 0 or Y.min() > S:
            continue
        valid[i] = True
        dr.polygon([(float(x), float(y)) for x, y in zip(X, Y)], fill=i)
    a = np.asarray(im, np.uint8)
    return np.where(a < 20, a.astype(np.int16), -1).astype(np.int8), valid


# ------------------------------------------------------------------ 마스크 유틸
def load_gt(path):
    """[규칙 동일: polar_dataset.load_aux_mask] 960x540 PNG -> 512x512 bool."""
    im = Image.open(path).convert("L").resize((S, S), Image.NEAREST)
    return np.asarray(im, np.uint8) > 127


def dilate(m, r):
    from scipy import ndimage
    return ndimage.binary_dilation(m, structure=np.ones((3, 3), bool), iterations=int(r))


def load_depth512(path):
    d = np.load(path).astype(np.float32)
    if d.ndim == 3:
        d = d[..., 0]
    return np.asarray(Image.fromarray(d, mode="F").resize((S, S), Image.NEAREST), np.float32)


def occluder_proxy(gt, depth):
    """가림물 몸체 **근사**: GT 아모달 영역 안에서 실제로 그려진 표면과 깊이가 비슷하고
    (±1.5 m) 공간적으로 이어진 화소들 중 GT 밖 · GT 로부터 96px 안. 정의는 문서에 인쇄한다."""
    from scipy import ndimage
    dv = depth[gt]
    dv = dv[np.isfinite(dv)]
    if dv.size == 0:
        return np.zeros_like(gt)
    band = np.isfinite(depth) & (np.abs(depth - float(np.median(dv))) <= OCC_TOL_M)
    lab, n = ndimage.label(band)
    keep = np.unique(lab[gt & (lab > 0)])
    if keep.size == 0:
        return np.zeros_like(gt)
    comp = np.isin(lab, keep)
    return comp & dilate(gt, NEIGH_PX) & ~gt


# ------------------------------------------------------------------ 모델
def load_model(path, device):
    ck = torch.load(path, map_location="cpu", weights_only=False)
    cfg = ck.get("config", {}) or {}
    enc = model_factory.encoder_from_config(cfg)
    m = model_factory.build("rgb", encoder_weights=None, classes=int(cfg.get("n_cells", 20)),
                            use_mask_head=True, encoder_name=enc)
    m.load_state_dict(ck["state_dict"] if "state_dict" in ck else ck)
    m.eval().to(device)
    return m, cfg, ck.get("epoch")


def prep(rgb):
    a = np.asarray(Image.open(rgb).convert("RGB").resize((S, S), Image.BILINEAR),
                   np.float32) / 255.0
    a = (a - np.array(IMAGENET_MEAN, np.float32)) / np.array(IMAGENET_STD, np.float32)
    return torch.from_numpy(np.ascontiguousarray(a.transpose(2, 0, 1)))


# ------------------------------------------------------------------ 본체
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="스모크용 — 앞 N장만")
    a = ap.parse_args()
    out_npz = os.path.join(OUTD, "records.npz")
    if a.limit:
        out_npz = os.path.join(OUTD, "records_smoke.npz")
    if os.path.exists(out_npz) and not a.force:
        print(f"  이미 있음 (resume-safe): {out_npz}  — 다시 하려면 --force")
        return 0

    doc = json.load(open(os.path.join(OUTD, "frames.json")))
    rows = [r for r in doc["frames"] if not r["dup"]]
    if a.limit:
        rows = rows[:a.limit]
    print(f"[in] 유니크 프레임 {len(rows)}장 · 아모달 GT "
          f"{sum(1 for r in rows if r['gt_mask'])}장")

    dev = torch.device(a.device if (a.device != "cuda" or torch.cuda.is_available()) else "cpu")
    models, metas = {}, {}
    for g, p in CKPTS.items():
        models[g], cfg, ep = load_model(p, dev)
        metas[g] = dict(ckpt=p, epoch=ep, encoder=cfg.get("encoder"),
                        aux_masks_found=cfg.get("aux_masks_found"),
                        aux_masks_missing_as_empty=cfg.get("aux_masks_missing_as_empty"),
                        n_train=cfg.get("n_train"), aux_lambda=cfg.get("aux_lambda"),
                        img_size=cfg.get("img_size"), best_epoch=ep,
                        sel_epoch_cfg=cfg.get("best_epoch"))
        assert int(cfg.get("img_size", S)) == S, cfg.get("img_size")
    print(f"[dev] {dev}  ·  체크포인트 2개 적재")
    for g, m in metas.items():
        print(f"   {g:6s} ep{m['best_epoch']} · aux 마스크 {m['aux_masks_found']} found / "
              f"{m['aux_masks_missing_as_empty']} missing-as-empty of {m['n_train']}")

    G = list(CKPTS)
    n = len(rows)
    R = {g: dict(p=np.zeros((n, 20), np.float32), q=np.full((n, 20), np.nan, np.float32),
                 qsum=np.zeros((n, 20), np.float32),
                 mass_tot=np.zeros(n), mass_in=np.zeros(n), mass_ring=np.zeros(n),
                 mass_mir=np.zeros(n), mass_occ=np.zeros(n),
                 mass_wedge=np.zeros(n), pmax_in=np.zeros(n), pmax_all=np.zeros(n),
                 inter50=np.zeros(n), pred50=np.zeros(n),
                 inter20=np.zeros(n)) for g in G}
    A = dict(a_gt=np.zeros(n), a_ring=np.zeros(n), a_mir=np.zeros(n), a_occ=np.zeros(n),
             a_wedge=np.zeros(n), a_cell=np.zeros((n, 20)), cell_valid=np.zeros((n, 20), bool))
    panel_masks = {}
    t0 = time.time()

    for b0 in range(0, n, a.batch):
        chunk = rows[b0:b0 + a.batch]
        x = torch.stack([prep(r["rgb"]) for r in chunk]).to(dev)
        with torch.no_grad():
            outs = {}
            for g in G:
                lo, mk = models[g](x)
                outs[g] = (torch.sigmoid(lo).cpu().numpy(),
                           torch.sigmoid(mk[:, 0]).cpu().numpy())
        for j, r in enumerate(chunk):
            i = b0 + j
            cm, valid = cellmap_of(cam_of(r["rgb"]))
            A["cell_valid"][i] = valid
            for c in range(20):
                A["a_cell"][i, c] = float((cm == c).sum())
            wedge = cm >= 0
            A["a_wedge"][i] = float(wedge.sum())
            gt = load_gt(r["gt_mask"]) if r["gt_mask"] else None
            if gt is not None and gt.any():
                ring = dilate(gt, RING_PX) & ~gt
                mir = np.fliplr(gt) & ~gt
                occ = occluder_proxy(gt, load_depth512(r["depth"]))
                A["a_gt"][i], A["a_ring"][i] = float(gt.sum()), float(ring.sum())
                A["a_mir"][i], A["a_occ"][i] = float(mir.sum()), float(occ.sum())
            else:
                ring = mir = occ = None
            for g in G:
                pc, mp = outs[g][0][j], outs[g][1][j].astype(np.float64)
                R[g]["p"][i] = pc
                R[g]["mass_tot"][i] = mp.sum()
                R[g]["pmax_all"][i] = mp.max()
                R[g]["pred50"][i] = float((mp >= .5).sum())
                R[g]["mass_wedge"][i] = mp[wedge].sum() if wedge.any() else 0.0
                for c in range(20):
                    s = cm == c
                    if s.any():
                        R[g]["q"][i, c] = mp[s].mean()
                        R[g]["qsum"][i, c] = mp[s].sum()
                if gt is not None and gt.any():
                    R[g]["mass_in"][i] = mp[gt].sum()
                    R[g]["pmax_in"][i] = mp[gt].max()
                    R[g]["inter50"][i] = float(((mp >= .5) & gt).sum())
                    R[g]["inter20"][i] = float(((mp >= .2) & gt).sum())
                    R[g]["mass_ring"][i] = mp[ring].sum() if ring.any() else 0.0
                    R[g]["mass_mir"][i] = mp[mir].sum() if mir.any() else 0.0
                    R[g]["mass_occ"][i] = mp[occ].sum() if occ.any() else 0.0
                if r["group"] == "panel":
                    panel_masks[f"{g}|{r['frame_id']}"] = outs[g][1][j].astype(np.float16)
        if (b0 // a.batch) % 12 == 0:
            print(f"   {b0 + len(chunk):4d}/{n}  ({time.time() - t0:.0f}s)")

    save = {f"{g}__{k}": v for g in G for k, v in R[g].items()}
    save.update(A)
    np.savez_compressed(out_npz, **save)
    np.savez_compressed(os.path.join(OUTD, "panel_masks.npz"), **panel_masks)
    idx = dict(meta=dict(created=time.strftime("%Y-%m-%dT%H:%M:%S"), device=str(dev),
                         img_size=S, ring_px=RING_PX, neigh_px=NEIGH_PX,
                         occ_tol_m=OCC_TOL_M, cells=CELLS, gens=G, ckpt_meta=metas,
                         wall_sec=round(time.time() - t0, 1),
                         isolated_from_ab=True),
               rows=[{k: r[k] for k in ("group", "gen", "frame_id", "scene", "tier", "arm",
                                        "gt_mask_px", "key")}
                     | dict(polar_gt=r["polar_gt"], has_gt=bool(r["gt_mask"]),
                            band_round=r.get("band_round"), cond=r.get("cond"),
                            file=r.get("file"), twin_of=r.get("twin_of"), cf_of=r.get("cf_of"))
                     for r in rows])
    json.dump(idx, open(os.path.join(OUTD, "index.json"), "w"), indent=1)
    print(f"\n[done] {n}프레임 × 2체크포인트  {time.time() - t0:.1f}s -> {out_npz}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
