#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_calib_curves.py — 보정 동반 보고 2건 (CPU 전용)

(1) **선택적 발화 곡선** — `ab_table_shells §6.4` 등록 문면 그대로:
    *"only the most confident x % of **cells** are answered"* ⇒ **칸 단위** 기권.
    coverage 격자 {100, 75, 50, 25} % (PREREG §2.1 [해소: P-22]).
    무대 = **test-core**(교정 GT) — v2 · v3-A 양측이 다 있는 헤드라인 무대.
    열 = 칸 정밀도 · 칸 recall(기권 포함/제외 두 분모 병기) · H 프레임 recall · FA(off팔).

(2) **④-b 맨-가림 H 시험** (`§6.3`) — 맨-가림 H 의 정답은 **발화가 아니라 보정된 낮은 확률**
    (PREREG §6-4 · DZ §2.5-5). val 에서 `px_canonical6 < k(=7,000)` 인 strict-H 프레임의
    GT 양성 칸 평균 확률 vs 그 층의 경험 위험 빈도 · τ_op 발화율. 원본/보정 병기.

**단조성 항등**: 신뢰도 |p − τ| 로 매긴 순서는 temperature 변환에 불변이므로 선택적
발화 곡선의 **선택 집합이 원본과 동일**하다. 스크립트가 그 항등을 검산해 인쇄한다.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "mainrun_0819", "code"))

COVERAGE = [1.00, 0.75, 0.50, 0.25]
RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
AUX = ["rgb_s42_aux"]
TAU = 0.5
EPS = 1e-6


def load_core(base, run):
    rows = {}
    for tag in ("on", "off"):
        with open(os.path.join(base, run, f"per_frame_{tag}.csv")) as f:
            rows[tag] = list(csv.DictReader(f))
    cells = [c[2:] for c in rows["on"][0] if c.startswith("p_")]
    out = {}
    for tag in ("on", "off"):
        R = rows[tag]
        out[tag] = dict(tier=np.array([r["tier"] for r in R]),
                        prob=np.array([[float(r["p_" + c]) for c in cells] for r in R]),
                        gt=np.array([[float(r["g_" + c]) for c in cells] for r in R]) > 0.5)
    return out


def selective_cells(run, tau=TAU, coverages=COVERAGE, T=None):
    on, off = run["on"], run["off"]
    P = np.concatenate([on["prob"].ravel(), off["prob"].ravel()])
    G = np.concatenate([on["gt"].ravel(), off["gt"].ravel()])
    if T is not None:
        p = np.clip(P, EPS, 1 - EPS)
        P = 1.0 / (1.0 + np.exp(-(np.log(p / (1 - p)) / T)))
    conf = np.abs(P - tau)
    order = np.argsort(-conf, kind="stable")
    n = len(P)
    n_on_cells = on["prob"].size
    haz = on["gt"].any(1)
    hazH = haz & (on["tier"] == "H")
    n_pos_all = int(G.sum())
    out = []
    for g in coverages:
        k = max(int(round(g * n)), 1)
        keep = np.zeros(n, bool); keep[order[:k]] = True
        fire = (P >= tau) & keep
        tp = int((fire & G).sum()); fp = int((fire & ~G).sum())
        kept_pos = int((keep & G).sum())
        fn_kept = kept_pos - tp
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec_kept = tp / kept_pos if kept_pos else float("nan")
        rec_all = tp / n_pos_all if n_pos_all else float("nan")
        # H 프레임 recall: 남은 칸 중 GT 양성 칸에서 발화가 하나라도 있으면 검출
        onfire = fire[:n_on_cells].reshape(on["prob"].shape)
        det = (onfire & on["gt"]).any(1)
        hrec = float(det[hazH].mean()) if hazH.any() else float("nan")
        # FA — off팔 (GT 전음성)
        offfire = fire[n_on_cells:].reshape(off["prob"].shape)
        offkeep = keep[n_on_cells:].reshape(off["prob"].shape)
        fa_cell = float(offfire.sum() / max(offkeep.sum(), 1))
        fa_frame = float(offfire.any(1).mean())
        out.append(dict(coverage=g, n_kept_cells=k, cell_precision=prec,
                        cell_recall_kept=rec_kept, cell_recall_all=rec_all,
                        frame_recall_H=hrec, fa_cell_kept=fa_cell, fa_frame=fa_frame,
                        conf_threshold=float(conf[order[k - 1]]),
                        n_kept_pos=kept_pos, n_pos_all=n_pos_all))
    return out


def agg(v):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
    if not len(v):
        return dict(mean=None, sd=None)
    return dict(mean=float(v.mean()), sd=(float(v.std(ddof=1)) if len(v) > 1 else 0.0),
                vals=[float(x) for x in v])


def bare_h_table(Ts):
    """④-b — val 의 맨-가림 H(px_canonical6 < k) 층. 원본/보정 병기."""
    import gridspec
    import polar_dataset_v3 as PD3
    import v3_masks as VM
    grid = gridspec.load("gridspec_v1.json")
    ds = PD3.PolarGridDatasetV3(os.path.join(V3, "dataset_manifest_v3_seg3.json"),
                                os.path.join(V3, "split_v3_seg3.json"), "val", "rgb",
                                grid=grid)
    G = ds.gt_matrix() > 0.5
    tiers = np.array([str(r.get("tier") or "none") for r in ds.items])
    arms = np.array([str(r.get("arm") or "none") for r in ds.items])
    bare = np.array([bool(VM.is_bare_h(r)) if hasattr(VM, "is_bare_h") else False
                     for r in ds.items])
    if not bare.any():                       # 술어를 원장에서 직접 재현
        px = np.array([((r.get("cue") or {}).get("px_canonical6")) for r in ds.items],
                      dtype=object)
        meas = np.array([p is not None for p in px])
        pxv = np.array([(p if p is not None else -1) for p in px], float)
        bare = (tiers == "H") & meas & (pxv < VM.K_CUE_PX)
    out = dict(k=VM.K_CUE_PX, seal=getattr(VM, "K_SEAL", None), strata={})
    for lbl, sel in (("A팔 맨-가림 H", bare & (arms == "A")),
                     ("전 팔 맨-가림 H", bare),
                     ("(대조) 단서 보유 A팔 strict-H", (tiers == "H") & (arms == "A") & ~bare)):
        n_fr = int(sel.sum())
        if not n_fr:
            out["strata"][lbl] = dict(n_frames=0)
            continue
        rows = {}
        for run in RUNS + AUX:
            P = np.load(os.path.join(V3, "runs", "v3a", run, "val_probs_best.npy")).astype(float)
            pos = G[sel]
            p = P[sel]
            pc = None
            if run in Ts:
                q = np.clip(p, EPS, 1 - EPS)
                pc = 1.0 / (1.0 + np.exp(-(np.log(q / (1 - q)) / Ts[run])))
            rows[run] = dict(
                n_frames=n_fr, n_pos_cells=int(pos.sum()),
                mean_p_pos_raw=(float(p[pos].mean()) if pos.any() else None),
                mean_p_pos_cal=(float(pc[pos].mean()) if (pc is not None and pos.any()) else None),
                fire_rate_pos_at_tau=(float((p[pos] >= TAU).mean()) if pos.any() else None),
                frame_fire_rate=float((p >= TAU).any(1).mean()),
                empirical_hazard_freq=float(pos.mean()))
        out["strata"][lbl] = dict(
            n_frames=n_fr, per_run=rows,
            mean_p_pos_raw=agg([rows[r]["mean_p_pos_raw"] for r in RUNS]),
            mean_p_pos_cal=agg([rows[r]["mean_p_pos_cal"] for r in RUNS]),
            fire_rate_pos=agg([rows[r]["fire_rate_pos_at_tau"] for r in RUNS]),
            empirical_hazard_freq=rows[RUNS[0]]["empirical_hazard_freq"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(V3, "logs", "verdict_calib_curves.json"))
    a = ap.parse_args(argv)
    Ts = {k: v["T"] for k, v in
          json.load(open(os.path.join(V3, "logs", "verdict_calibration.json"),
                         encoding="utf-8"))["runs"].items()}

    sides = {}
    ident = dict(max_abs_diff=0.0, checked=0)
    for lbl, base, runs in (("v2", os.path.join(V3, "eval_v2corr"), RUNS),
                            ("v3a", os.path.join(V3, "eval_v3a_core"), RUNS),
                            ("v3a_aux_isolated", os.path.join(V3, "eval_v3a_core"), AUX)):
        per = {}
        for r in runs:
            run = load_core(base, r)
            raw = selective_cells(run)
            per[r] = dict(raw=raw)
            if lbl.startswith("v3") and r in Ts:
                cal = selective_cells(run, T=Ts[r])
                per[r]["cal"] = cal
                for x, y in zip(raw, cal):
                    for f in ("cell_precision", "cell_recall_kept", "cell_recall_all",
                              "frame_recall_H", "fa_cell_kept", "fa_frame"):
                        if np.isfinite(x[f]) and np.isfinite(y[f]):
                            ident["checked"] += 1
                            ident["max_abs_diff"] = max(ident["max_abs_diff"],
                                                        abs(x[f] - y[f]))
        summ = []
        for i, g in enumerate(COVERAGE):
            e = dict(coverage=g, n_kept_cells=per[runs[0]]["raw"][i]["n_kept_cells"])
            for f in ("cell_precision", "cell_recall_kept", "cell_recall_all",
                      "frame_recall_H", "fa_cell_kept", "fa_frame", "conf_threshold"):
                e[f] = agg([per[r]["raw"][i][f] for r in runs])
            summ.append(e)
        sides[lbl] = dict(runs=runs, per_run=per, summary=summ)
        print(f"  [{lbl}] " + " | ".join(
            f"cov{int(g*100)}% P {sides[lbl]['summary'][i]['cell_precision']['mean']:.3f} "
            f"R {sides[lbl]['summary'][i]['cell_recall_all']['mean']:.3f} "
            f"H {sides[lbl]['summary'][i]['frame_recall_H']['mean']:.3f} "
            f"FA {sides[lbl]['summary'][i]['fa_cell_kept']['mean']:.4f}"
            for i, g in enumerate(COVERAGE)))
    print(f"[identity] 선택적 발화 곡선 원본↔보정 {ident['checked']} 값 · "
          f"max|Δ| = {ident['max_abs_diff']:.3e}")

    bare = bare_h_table(Ts)
    for k, v in bare["strata"].items():
        if v.get("n_frames"):
            print(f"  [④-b] {k}: n={v['n_frames']} · mean p(양성칸) raw "
                  f"{v['mean_p_pos_raw']['mean']:.4f} → cal {v['mean_p_pos_cal']['mean']:.4f} "
                  f"· τ_op 발화율 {v['fire_rate_pos']['mean']:.4f} · 경험빈도 "
                  f"{v['empirical_hazard_freq']:.4f}")

    doc = dict(doc="보정 동반 보고 — 선택적 발화 곡선(칸 단위 · test-core) + ④-b 맨-가림 H",
               coverage_grid=COVERAGE, tau=TAU, temperatures=Ts,
               selective=sides, selective_identity=ident, bare_h=bare,
               note=("신뢰도 |p−τ| 의 순서는 temperature 에 불변이므로 곡선의 선택 집합이 "
                     "원본과 동일하다 — 위 항등 검산이 그것을 확인한다. 보정이 바꾸는 것은 "
                     "확률값(ECE·신뢰도 곡선·Δp)뿐이다."))
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
