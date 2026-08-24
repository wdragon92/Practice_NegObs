#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amodal5_twindelta.py — 트윈 짝의 **광학 차이** 실측 (CPU 전용 · 새 렌더 0).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      python3 experiments/v3_0823/code/amodal5_twindelta.py

(b) 트윈 대조군의 정직성 잣대다. 「낙차만 뺐다」고 말하려면 **두 컷이 실제로 얼마나 다른지**를
같이 인쇄해야 한다. 술어는 PREREG §2.1 의 `frac(|ΔI| > 8)` 을 그대로 쓴다 (회색조 · 원본 해상도).

산출 -> experiments/v3_0823/amodal5/twin_delta.json
    core_H  : test-core H 96장 · on팔 vs off팔 트윈
    ext     : test-ext sceneH1/H2/H3 · A vs C (낙차만) · A vs B (단서만)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
OUTD = os.path.join(V3, "amodal5")


def gray(p):
    return np.asarray(Image.open(p).convert("L"), np.int16)


def delta(p1, p2):
    a, b = gray(p1), gray(p2)
    if a.shape != b.shape:
        raise SystemExit(f"[fatal] 해상도 불일치 {p1} {p2}")
    dd = np.abs(a - b)
    return dict(mean_abs=round(float(dd.mean()), 4),
                frac_gt8=round(float((dd > 8).mean()), 6),
                frac_gt32=round(float((dd > 32).mean()), 6))


def main():
    out = {}
    fr = json.load(open(os.path.join(OUTD, "frames.json")))["frames"]
    by_fid = {}
    for r in fr:
        by_fid.setdefault(r["frame_id"], r)

    core = []
    for r in fr:
        if r["group"] != "core_Htwin":
            continue
        on = by_fid[r["twin_of"]]
        d = delta(on["rgb"], r["rgb"])
        # 512 squash 공간에서 GT 아모달 영역 안/밖으로 쪼갠다 — 마스크와 같은 좌표계.
        S = 512
        a = np.asarray(Image.open(on["rgb"]).convert("L").resize((S, S), Image.BILINEAR),
                       np.int16)
        b = np.asarray(Image.open(r["rgb"]).convert("L").resize((S, S), Image.BILINEAR),
                       np.int16)
        dd = np.abs(a - b)
        gt = np.asarray(Image.open(r["gt_mask"]).convert("L").resize((S, S), Image.NEAREST),
                        np.uint8) > 127
        d.update(frac_gt8_in=round(float((dd[gt] > 8).mean()), 6) if gt.any() else None,
                 frac_gt8_out=round(float((dd[~gt] > 8).mean()), 6) if (~gt).any() else None,
                 mean_abs_in=round(float(dd[gt].mean()), 4) if gt.any() else None,
                 mean_abs_out=round(float(dd[~gt].mean()), 4) if (~gt).any() else None)
        core.append(dict(on=r["twin_of"], off=r["frame_id"], **d))
    out["core_H"] = core
    v = np.array([c["frac_gt8"] for c in core])
    ma = np.array([c["mean_abs"] for c in core])
    fi = np.array([c["frac_gt8_in"] for c in core], float)
    fo = np.array([c["frac_gt8_out"] for c in core], float)
    print(f"[core_H] {len(core)}짝  frac(|ΔI|>8) 평균 {v.mean():.4f} · 중앙 "
          f"{np.median(v):.4f} · 최대 {v.max():.4f}  |  mean|ΔI| 평균 {ma.mean():.3f}")
    print(f"          zero-info(<0.001) 짝 {int((v < 0.001).sum())}/{len(core)}")
    print(f"          GT아모달 **안** frac(|ΔI|>8) 평균 {np.nanmean(fi):.4f} · "
          f"**밖** {np.nanmean(fo):.4f}  → 안/밖 비 {np.nanmean(fi) / max(np.nanmean(fo), 1e-9):.2f}")
    out["core_H_summary"] = dict(
        n=len(core), frac_gt8_mean=float(v.mean()), frac_gt8_median=float(np.median(v)),
        frac_gt8_max=float(v.max()), mean_abs_mean=float(ma.mean()),
        n_zero_info=int((v < 0.001).sum()),
        frac_gt8_in_mean=float(np.nanmean(fi)), frac_gt8_out_mean=float(np.nanmean(fo)))

    ext = []
    for r in fr:
        if r["group"] != "cueoff" or r["arm"] != "A":
            continue
        fid = r["frame_id"]
        pa = r["rgb"]
        rec = dict(frame_id=fid, scene=r["scene"])
        for other, tag in (("C", "AC"), ("B", "AB")):
            po = pa.replace("_A/", f"_{other}/")
            if not os.path.exists(po):
                rec[tag] = None
                continue
            rec[tag] = delta(pa, po)
        ext.append(rec)
    out["ext"] = ext
    import collections
    agg = collections.defaultdict(list)
    for r in ext:
        for tag in ("AC", "AB"):
            if r[tag]:
                agg[(r["scene"], tag)].append(r[tag]["frac_gt8"])
    for k in sorted(agg):
        a = np.array(agg[k])
        print(f"[ext] {k[0]:9s} {k[1]}  n={len(a):3d}  frac(|ΔI|>8) 평균 {a.mean():.4f} · "
              f"중앙 {np.median(a):.4f} · 최대 {a.max():.4f}")
    out["meta"] = dict(predicate="frac(|dI|>8) — PREREG §2.1", gray="PIL convert('L')",
                       note="A=단서有·낙차有 · B=단서OFF·낙차有 · C=단서有·낙차無")
    json.dump(out, open(os.path.join(OUTD, "twin_delta.json"), "w"), indent=1)
    print(f"\n[done] -> {os.path.join(OUTD, 'twin_delta.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
