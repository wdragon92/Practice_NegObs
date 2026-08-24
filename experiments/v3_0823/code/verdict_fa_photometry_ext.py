#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_fa_photometry_ext.py — V-3 이행 · step 1
test-ext 4팔(A/B/C/D) 1,152프레임의 **(프레임, 칸) 광도 + 단서-프림 귀속** 원장.

`code/fa_cell_photometry.py`(test-core 816프레임)의 **직계 이식**이다.
투영 수식·구조텐서 선질량·저역통과 규약을 **한 줄도 바꾸지 않았다** — 바뀐 것은
무대(test-core → test-ext)와, test-ext 에서만 가능한 **한 계측기의 추가**뿐이다.

추가 계측기 (test-core 에는 없었다)
-----------------------------------
test-ext 4팔은 전 컷에 `.idseg.npz`(인스턴스 세그 + prim 경로 사전)가 붙어 있다.
`code/cue_extent_audit.py:Attributor`(VG-09 키별 r 원장과 **같은 귀속기**)로
프림 → 단서키를 매기고, **칸 단위로 단서 픽셀을 센다**. 그 결과 test-core 에서
`[수동]` 2씬 오버레이였던 **장식형이 test-ext 에서는 `[기계]`가 된다**.
  · install = R,Ta,N,Sg,V,Bo,De,Cm  (설치 부재)      → 장식형 기계 보강
  · ground  = T,Mh,Tg,Jt,Dr,Rm,Gk   (지면 문양·재질) → 대리선형 기계 보강
  · shadow  = Sh                     (그림자 캐스터)  → 조명형   기계 보강
**계측기가 test-core 와 다르므로 두 무대의 장식형 수치를 나란히 놓지 않는다.**

DS·픽셀 격자 주의: `labeler.unproject` 는 `dep[::4,::4]` 로 성글게 뜬다. RGB 는
원본 그대로 `INTER_AREA` 저역통과(에일리어싱 가짜 엣지 차단), idseg 는 **라벨이라
평균낼 수 없으므로** `[::4,::4]` 최근접 — unproject 격자와 정확히 같은 화소다.

출력: experiments/v3_0823/cell_photometry_textext.csv
      (4팔 × 288프레임 × 20칸 = 23,040행 · 키 = (arm, frame_id, cell))
CPU 전용 · 재렌더 0 · GPU 0 · git 무접촉.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code/labeling"))
sys.path.insert(0, os.path.join(V3, "code"))
import labeler as L                                     # noqa: E402
import cue_extent_audit as CEA                          # noqa: E402  (main-guarded)

GRIDSPEC = os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")
MANIFESTS = [("AC", os.path.join(V3, "dataset_manifest_v3_textext.json")),
             ("BD", os.path.join(V3, "dataset_manifest_v3_textext_bd.json"))]
ATTRIB = os.path.join(V3, "logs/cue_extent_attrib.json")
OUTCSV = os.path.join(V3, "cell_photometry_textext.csv")

# ---- [복사: fa_cell_photometry.py L42-46] 상수 한 줄도 바꾸지 않는다 ----------
DS = 4                      # depth/image downsample, same factor labeler.py uses
GROUND_BAND_M = 0.30        # |height above local ground| accepted as "ground"
COH_MIN = 0.55              # structure-tensor coherence
HORIZ_MAX_DEG = 35.0        # line orientation within this of image-horizontal

# 단서키 3군 (KEYNAME = cue_extent_audit.py:101-107)
K_INSTALL = ("R", "Ta", "N", "Sg", "V", "Bo", "De", "Cm")
K_GROUND = ("T", "Mh", "Tg", "Jt", "Dr", "Rm", "Gk")
K_SHADOW = ("Sh",)

GRID = json.load(open(GRIDSPEC))
NS, NB = GRID["n_sectors"], GRID["n_bands"]
CELL_IDS = [f"{s}{b}" for b in GRID["band_names"] for s in GRID["sector_names"]]

_G = {}


def cell_of_pixels(dep, cam):
    """[복사: fa_cell_photometry.py L54-68] (칸 인덱스, 지면고, 유효) — 라벨러와 동일."""
    P, good = L.unproject(dep, [0.0, 0.0, 0.0], cam, DS)   # eye=origin -> 카메라 상대
    dx, dy, dz = P[..., 0], P[..., 1], P[..., 2]
    yaw = math.radians(cam["yaw"])
    cy, sy = math.cos(yaw), math.sin(yaw)
    xc, yc = dx * cy + dy * sy, -dx * sy + dy * cy
    az = np.degrees(np.arctan2(yc, xc))
    rng = np.hypot(xc, yc)
    asc = np.asarray(GRID["sector_edges_deg"][::-1])
    k = np.searchsorted(asc, az, side="right") - 1
    b = np.searchsorted(np.asarray(GRID["band_edges_m"]), rng, side="right") - 1
    ok = good & (k >= 0) & (k < NS) & (b >= 0) & (b < NB)
    cell = np.where(ok, b * NS + (NS - 1 - k), -1)
    return cell, dz + cam["h_rel"], good


def line_structure(lum):
    """[복사: fa_cell_photometry.py L71-100] 구조텐서 선질량."""
    import cv2
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    gmag = np.hypot(gx, gy)
    k = (5, 5)
    jxx = cv2.boxFilter(gx * gx, -1, k)
    jyy = cv2.boxFilter(gy * gy, -1, k)
    jxy = cv2.boxFilter(gx * gy, -1, k)
    tr = jxx + jyy
    det = jxx * jyy - jxy * jxy
    disc = np.sqrt(np.maximum(tr * tr - 4.0 * det, 0.0))
    coh = np.where(tr > 1e-6, disc / np.maximum(tr, 1e-6), 0.0)
    theta_g = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)
    line_ang = np.degrees(np.abs(np.arctan2(np.cos(theta_g), -np.sin(theta_g))))
    line_ang = np.minimum(line_ang, 180.0 - line_ang)
    strong = gmag > max(8.0, float(np.percentile(gmag, 90)))
    return strong & (coh > COH_MIN) & (line_ang < HORIZ_MAX_DEG), gmag


def _init(attrib):
    _G["att"] = CEA.Attributor(attrib)


def cue_key_image(idseg_path, scene):
    """idseg → 화소별 단서키 코드 (0 = 단서 아님). VG-09 귀속기 그대로."""
    z = np.load(idseg_path, allow_pickle=True)
    a = z["idseg"][::DS, ::DS]
    lab = json.loads(str(z["idToLabels"]))
    att = _G["att"]
    ids = np.unique(a)
    keys = {}
    lut = {}
    for i in ids:
        p = lab.get(str(int(i)))
        if p is None:
            continue
        k = att.key_of(scene, p)
        if k:
            lut[int(i)] = k
            keys.setdefault(k, []).append(int(i))
    return a, lut, keys


def one(args):
    arm, fid, rec = args
    import cv2
    cam = rec["cam"]
    dep = np.load(rec["depth"]).astype(np.float64)
    img = cv2.imread(rec["rgb"], cv2.IMREAD_COLOR)          # BGR uint8
    if img is None:
        return []
    h, w = img.shape[0] // DS, img.shape[1] // DS
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    lum = (0.114 * img[..., 0] + 0.587 * img[..., 1] +
           0.299 * img[..., 2]).astype(np.float32)
    line_mask, gmag = line_structure(lum)

    cell, hgt, good = cell_of_pixels(dep, cam)

    seg_path = rec["rgb"].replace(".png", ".idseg.npz")
    seg = key_img = None
    if os.path.exists(seg_path):
        a, lut, _ = cue_key_image(seg_path, rec["scene_id"])
        key_img = np.zeros(a.shape, dtype=object)
        seg = a
        keymap = lut

    n0 = min(cell.shape[0], lum.shape[0])
    n1 = min(cell.shape[1], lum.shape[1])
    cell, hgt, good = cell[:n0, :n1], hgt[:n0, :n1], good[:n0, :n1]
    lum, gmag, line_mask = lum[:n0, :n1], gmag[:n0, :n1], line_mask[:n0, :n1]
    if seg is not None:
        seg = seg[:n0, :n1]

    ground = good & (np.abs(hgt) < GROUND_BAND_M)
    fr_g = lum[ground & (cell >= 0)]
    frame_lum_med = float(np.median(fr_g)) if fr_g.size else float("nan")
    fr_all = lum[good]
    frame_lum_med_all = float(np.median(fr_all)) if fr_all.size else float("nan")

    rows = []
    for ci, cid in enumerate(CELL_IDS):
        m = cell == ci
        n = int(m.sum())
        mg = m & ground
        ng = int(mg.sum())
        if n:
            v = lum[m]
            r = dict(lum_mean=float(v.mean()), lum_median=float(np.median(v)),
                     lum_p10=float(np.percentile(v, 10)), lum_std=float(v.std()),
                     line_frac=float(line_mask[m].mean()),
                     grad_p90=float(np.percentile(gmag[m], 90)))
        else:
            r = dict(lum_mean=float("nan"), lum_median=float("nan"),
                     lum_p10=float("nan"), lum_std=float("nan"),
                     line_frac=float("nan"), grad_p90=float("nan"))
        if ng:
            r["lum_median_ground"] = float(np.median(lum[mg]))
            r["line_frac_ground"] = float(line_mask[mg].mean())
        else:
            r["lum_median_ground"] = float("nan")
            r["line_frac_ground"] = float("nan")

        kc = {}
        if seg is not None and n:
            ids, cnt = np.unique(seg[m], return_counts=True)
            for i, c in zip(ids, cnt):
                k = keymap.get(int(i))
                if k:
                    kc[k] = kc.get(k, 0) + int(c)
        rows.append(dict(
            arm=arm, frame_id=fid, scene_id=rec["scene_id"],
            band_round=rec.get("band_round", ""), toggle_state=rec["toggle_state"],
            tier=rec.get("tier", ""), cell=cid, cell_idx=ci,
            n_px=n, n_px_ground=ng,
            frame_lum_median=round(frame_lum_med, 4),
            frame_lum_median_all=round(frame_lum_med_all, 4),
            **{k: (round(x, 4) if x == x else "") for k, x in r.items()},
            cue_px_install=sum(kc.get(k, 0) for k in K_INSTALL),
            cue_px_ground=sum(kc.get(k, 0) for k in K_GROUND),
            cue_px_shadow=sum(kc.get(k, 0) for k in K_SHADOW),
            cue_keys="|".join(f"{k}:{v}" for k, v in sorted(kc.items())),
        ))
    return rows


def main():
    attrib = json.load(open(ATTRIB, encoding="utf-8"))
    tasks = []
    for _pair, mp in MANIFESTS:
        man = json.load(open(mp, encoding="utf-8"))
        for f in man["frames"]:
            arm = f["round"].rsplit("_", 1)[-1]
            assert arm in "ABCD" and len(arm) == 1, f["round"]
            tasks.append((arm, f["frame_id"], f))
    print(f"frames {len(tasks)}  (arms "
          f"{ {a: sum(1 for t in tasks if t[0] == a) for a in 'ABCD'} })", flush=True)

    out = []
    with Pool(12, initializer=_init, initargs=(attrib,)) as p:
        for i, rows in enumerate(p.imap_unordered(one, tasks, chunksize=4)):
            out.extend(rows)
            if (i + 1) % 200 == 0:
                print(f"  {i+1}/{len(tasks)}", flush=True)

    out.sort(key=lambda r: (r["arm"], r["frame_id"], r["cell_idx"]))
    with open(OUTCSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows -> {OUTCSV}")

    # 무상 검산: D팔(전 cue OFF · 위험 OFF)은 설치-단서 픽셀이 사실상 0이어야 한다.
    for a in "ABCD":
        sel = [r for r in out if r["arm"] == a]
        print(f"  arm {a}: cells {len(sel)} | install px "
              f"{sum(r['cue_px_install'] for r in sel):>9,} | ground "
              f"{sum(r['cue_px_ground'] for r in sel):>9,} | shadow "
              f"{sum(r['cue_px_shadow'] for r in sel):>8,} | unseen "
              f"{sum(1 for r in sel if r['n_px'] == 0):>5,}")


if __name__ == "__main__":
    sys.exit(main())
