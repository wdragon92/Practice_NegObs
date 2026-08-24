#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_calib.py — PREREG §2.1 "공통 보정 규약" 의 집행 (CPU 전용)

  · 학습 후 **val 에서 temperature T 자동 탐색** (런별)
  · 동반 보고: 신뢰도 곡선(reliability) · **ECE** · **선택적 발화 곡선**
    (coverage 격자 **{100, 75, 50, 25} %** — PREREG §2.1 [해소: P-22])

**마스크 사거리 (§5.2 · §6-3)**: 무시 마스크는 훈련 손실·선택식에만 닿는다.
보정은 평가에 먹이는 값이므로 **정본 = 마스크 미적용 val 전 칸**이고,
마스크 적용본은 **민감도 대조로만** 병기한다. 평가 코드 경로는 건드리지 않는다.

입력 : runs/v3a/<run>/val_probs_best.npy  (선택 에폭 · 데이터셋 순서)
       dataset_manifest_v3_seg3.json + split_v3_seg3.json (val GT · 같은 순서)
산출 : logs/verdict_calibration.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")
sys.path.insert(0, os.path.join(REPO, "experiments", "mainrun_0819", "code"))
sys.path.insert(0, HERE)

RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
AUX = ["rgb_s42_aux"]
EPS = 1e-6
COVERAGE = [1.00, 0.75, 0.50, 0.25]        # PREREG §2.1 (P-22)
N_BINS = 15


def logit(p):
    p = np.clip(np.asarray(p, np.float64), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def nll(z, y, T):
    p = np.clip(sigmoid(z / T), EPS, 1 - EPS)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


def fit_T(z, y):
    """등록 문면 '자동 탐색' — 로그 격자 조밀 스캔 + 황금분할 정련 (NLL 최소)."""
    grid = np.exp(np.linspace(np.log(0.05), np.log(20.0), 400))
    vals = [nll(z, y, t) for t in grid]
    i = int(np.argmin(vals))
    lo = grid[max(i - 1, 0)]
    hi = grid[min(i + 1, len(grid) - 1)]
    gr = (np.sqrt(5) - 1) / 2
    a, b = lo, hi
    for _ in range(80):
        c, d = b - gr * (b - a), a + gr * (b - a)
        if nll(z, y, c) < nll(z, y, d):
            b = d
        else:
            a = c
    T = float((a + b) / 2)
    return T, float(nll(z, y, T)), float(nll(z, y, 1.0))


def ece(p, y, n_bins=N_BINS):
    """등폭 구간 ECE + 신뢰도 곡선 데이터 (칸 단위 이진)."""
    p = np.asarray(p, np.float64).ravel()
    y = np.asarray(y, np.float64).ravel()
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1], right=False), 0, n_bins - 1)
    rows, e, mce = [], 0.0, 0.0
    for b in range(n_bins):
        m = idx == b
        n = int(m.sum())
        if n == 0:
            rows.append(dict(bin=b, lo=float(edges[b]), hi=float(edges[b + 1]),
                             n=0, conf=None, freq=None, gap=None))
            continue
        conf = float(p[m].mean()); freq = float(y[m].mean())
        gap = abs(conf - freq)
        e += n / len(p) * gap
        mce = max(mce, gap)
        rows.append(dict(bin=b, lo=float(edges[b]), hi=float(edges[b + 1]),
                         n=n, conf=conf, freq=freq, gap=float(conf - freq)))
    return float(e), float(mce), rows


def brier(p, y):
    return float(((np.asarray(p, np.float64) - np.asarray(y, np.float64)) ** 2).mean())


def selective_curve(P, G, tau=0.5, coverages=COVERAGE, haz=None):
    """선택적 발화 곡선 — '모르겠다' 의 값.

    프레임 신뢰도 = max_c |p_c − τ| (결정경계로부터의 거리).
    coverage γ = 신뢰도 상위 γ 프레임만 남기고 나머지는 **기권**.
    남은 부분집합에서 칸 F1 · 프레임 검출률(양성 프레임) · 프레임 FA(음성 프레임).
    """
    P = np.asarray(P, np.float64); G = np.asarray(G, np.float64) > 0.5
    conf = np.abs(P - tau).max(1)
    order = np.argsort(-conf)
    n = len(P)
    out = []
    for g in coverages:
        k = max(int(round(g * n)), 1)
        sel = order[:k]
        p, gt = P[sel], G[sel]
        fire = p >= tau
        tp = int((fire & gt).sum()); fp = int((fire & ~gt).sum()); fn = int((~fire & gt).sum())
        f1 = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) else float("nan")
        pos_fr = gt.any(1)
        det = float((fire & gt).any(1)[pos_fr].mean()) if pos_fr.any() else float("nan")
        neg_fr = ~pos_fr
        fa = float(fire.any(1)[neg_fr].mean()) if neg_fr.any() else float("nan")
        row = dict(coverage=g, n_kept=k, cell_f1=f1, frame_det_pos=det, frame_fa_neg=fa,
                   n_pos_frames=int(pos_fr.sum()), n_neg_frames=int(neg_fr.sum()),
                   conf_threshold=float(conf[order[k - 1]]))
        if haz is not None:
            h = np.asarray(haz)[sel]
            hm = h & gt.any(1)
            row["frame_recall_H"] = (float((fire & gt).any(1)[hm].mean())
                                     if hm.any() else float("nan"))
            row["n_H_frames"] = int(hm.sum())
        out.append(row)
    return out


def main():
    import gridspec
    import polar_dataset_v3 as PD3

    man = os.path.join(V3, "dataset_manifest_v3_seg3.json")
    spl = os.path.join(V3, "split_v3_seg3.json")
    grid = gridspec.load("gridspec_v1.json")
    ds = PD3.PolarGridDatasetV3(man, spl, "val", "rgb", grid=grid)
    G = ds.gt_matrix()                       # [N,20] — 데이터셋 순서
    IGN = ds.ignore_matrix().astype(bool)
    tiers = np.array([str(r.get("tier") or "none") for r in ds.items])
    arms = np.array([str(r.get("arm") or "none") for r in ds.items])
    print(f"[val] n={len(G)} cells={G.shape[1]} · mask 칸 {int(IGN.sum())} "
          f"({IGN.mean() * 100:.2f} %) · strict-H {int((tiers == 'H').sum())}")

    doc = dict(doc="verdict_calibration — PREREG §2.1 공통 보정 규약",
               procedure=("val 확률(선택 에폭 덤프)에 temperature T 를 자동 탐색 "
                          "(NLL 최소 · 로그격자 400 + 황금분할 80회). "
                          "정본 = 마스크 미적용 val 전 칸 (§5.2 3단 사거리: 마스크는 "
                          "훈련 손실·선택식에만; 보정은 평가에 먹이는 값이므로 미적용). "
                          "마스크 적용본은 민감도 대조로만 병기."),
               n_bins=N_BINS, coverage_grid=COVERAGE,
               val=dict(n_frames=int(len(G)), n_cells=int(G.size),
                        n_masked_cells=int(IGN.sum()),
                        n_strict_H=int((tiers == "H").sum()),
                        manifest=os.path.basename(man), split=os.path.basename(spl)),
               runs={})

    for run in RUNS + AUX:
        p = os.path.join(V3, "runs", "v3a", run, "val_probs_best.npy")
        if not os.path.isfile(p):
            print(f"  [miss] {run}"); continue
        P = np.load(p).astype(np.float64)
        assert P.shape == G.shape, f"{run}: {P.shape} vs {G.shape}"
        z = logit(P)
        # 정본 — 마스크 미적용
        T, nll_T, nll_1 = fit_T(z.ravel(), G.ravel())
        Pc = sigmoid(z / T)
        e0, m0, rel0 = ece(P, G)
        e1, m1, rel1 = ece(Pc, G)
        # 민감도 — 마스크 적용
        keep = ~IGN.ravel()
        Tm, nllm_T, nllm_1 = fit_T(z.ravel()[keep], G.ravel()[keep])

        haz = (tiers == "H")
        sel_raw = selective_curve(P, G, 0.5, haz=haz)
        sel_cal = selective_curve(Pc, G, 0.5, haz=haz)

        doc["runs"][run] = dict(
            isolated=(run in AUX),
            T=T, T_masked_sensitivity=Tm,
            nll_raw=nll_1, nll_cal=nll_T, nll_gain=nll_1 - nll_T,
            ece_raw=e0, ece_cal=e1, mce_raw=m0, mce_cal=m1,
            brier_raw=brier(P, G), brier_cal=brier(Pc, G),
            reliability_raw=rel0, reliability_cal=rel1,
            selective_raw=sel_raw, selective_cal=sel_cal,
            mean_p_raw=float(P.mean()), mean_p_cal=float(Pc.mean()),
            base_rate=float(G.mean()),
            fire_rate_raw=float((P >= 0.5).mean()), fire_rate_cal=float((Pc >= 0.5).mean()),
            n_A=int((arms == "A").sum()), n_D=int((arms == "D").sum()),
        )
        print(f"  [{run}] T={T:.4f} (masked {Tm:.4f}) · ECE {e0:.4f} -> {e1:.4f} · "
              f"NLL {nll_1:.4f} -> {nll_T:.4f} · fire {(P >= .5).mean():.4f} -> "
              f"{(Pc >= .5).mean():.4f}")

    out = os.path.join(V3, "logs", "verdict_calibration.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[out] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
