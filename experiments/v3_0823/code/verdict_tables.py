#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_tables.py — 계기판 ①·③ 의 **v3-A 쪽 표** + L1 측방 (CPU 전용)

`v2_textext_tables.py` 를 **라이브러리로 그대로 재사용**한다 — 계기판의 정의
(트윈-조건부 recall · Δp · FA_C/FA_D · 섹터 질량)를 v3 쪽에서 다시 구현하면
두 표가 다른 코드로 계산되어 A/B 가 성립하지 않는다. 바뀌는 것은 입력 경로뿐이다.

  eval_v3a_textext/<run>/per_frame.csv       (A,C) 패스 — on=A · off=C
  eval_v3a_textext/<run>/bd/per_frame.csv    (B,D) 패스 — on=B · off=D

**FA-정합 문턱은 v3 런의 D팔 덤프에서 다시 잡는다** (PREREG §2.1 등록 절차:
정확분위에서 목표 이하 최대 달성률 · 기준 팔 = D팔). v2 의 τ 를 물려쓰지 않는다.

**보정 병기 (PREREG §2.1)**: `--calibrate` 는 런별 T 로 확률을 변환한 뒤 같은 표를
다시 만든다. temperature 는 **강단조**이므로 (a) τ_op 0.5 (b) 분위로 잡는 FA-정합
8지점 — 두 곳 모두에서 **선택되는 칸·프레임 집합이 불변**이고, 따라서 recall·FA 는
원본과 수치 동일해야 한다. 그 항등이 실제로 성립하는지 스크립트가 검산한다.

**평가에 무시 마스크는 닿지 않는다** (§5.2 3단 · §6-3): 본 스크립트는 v3_masks 를
import 하지 않는다.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "mainrun_0819", "code"))

import gridspec                      # noqa: E402
import v2_textext_tables as T2       # noqa: E402  — 계기판 정의의 단일 정본

V3A_RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
V3A_AUX = ["rgb_s42_aux"]


def _patch(evdir, runs, aux):
    """모듈 전역만 갈아끼운다 — 계산 코드는 한 줄도 다르지 않다."""
    T2.EV = evdir
    T2.RUNS = list(runs) + list(aux)
    T2.ARMS = {"v3a_rgb": list(runs), "v3a_rgb_aux_isolated": list(aux)}
    # v3-A 에는 공표 τ* 가 없다. 등록 운용점 τ_op 0.5 를 그 자리에 둔다(참고 행).
    T2.TAU_STAR = {r: 0.5 for r in T2.RUNS}


def _apply_T(evdir, runs, Ts, outdir):
    """런별 temperature 로 per_frame.csv 의 확률만 변환해 별도 트리에 쓴다."""
    import csv
    os.makedirs(outdir, exist_ok=True)
    for r in runs:
        T = Ts[r]
        for sub in ("", "bd"):
            src = os.path.join(evdir, r, sub, "per_frame.csv")
            dst = os.path.join(outdir, r, sub, "per_frame.csv")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src) as f:
                rd = csv.DictReader(f)
                fn = list(rd.fieldnames or [])
                rows = list(rd)
            pcols = [c for c in fn if c.startswith("p_")]
            with open(dst, "w", newline="") as f:
                wr = csv.DictWriter(f, fieldnames=fn)
                wr.writeheader()
                for row in rows:
                    for c in pcols:
                        p = float(row[c])
                        p = min(max(p, 1e-6), 1 - 1e-6)
                        z = np.log(p / (1 - p)) / T
                        row[c] = f"{1.0 / (1.0 + np.exp(-z)):.6f}"
                    wr.writerow(row)
    return outdir


def build(evdir, runs, aux, tag):
    _patch(evdir, runs, aux)
    grid = gridspec.load("gridspec_v1.json")
    per_run = {}
    for r in T2.RUNS:
        p = os.path.join(evdir, r, "per_frame.csv")
        if not os.path.isfile(p):
            print(f"  [miss] {r}")
            continue
        per_run[r] = T2.run_tables(r, grid)
        c = per_run[r]["counts"]
        print(f"  [{tag}] {r}: A {c['n_A']} · haz {c['n_haz_A']} · paired-H {c['paired_H']} "
              f"{c['paired_H_by_scene']} · C/D GT+ {c['C_gt_positive_cells']}/"
              f"{c['D_gt_positive_cells']}")
    # 팔별 3시드 집계 — v2 모듈의 summary 조립을 그대로 쓴다
    summary = {}
    for arm, rr in T2.ARMS.items():
        rs = [per_run[x] for x in rr if x in per_run]
        if not rs:
            continue
        summary[arm] = _summarise(rs, grid)
    return dict(tag=tag, eval_dir=evdir, per_run=per_run, summary=summary,
                frame_targets=T2.FRAME_TARGETS, cell_targets=T2.CELL_TARGETS,
                fa_reference_arm="D", pair="(A,C)")


def _summarise(rs, grid):
    """v2_textext_tables.main() 의 집계 블록과 **같은 필드**를 만든다."""
    agg = T2.agg
    n_ops = len(rs[0]["ops"])
    rows = []
    for i in range(n_ops):
        o0 = rs[0]["ops"][i]
        e = dict(name=o0["name"], axis=o0["axis"], target=o0["target"],
                 tau=agg([r["ops"][i]["tau"] for r in rs]),
                 achieved=agg([r["ops"][i].get("achieved") for r in rs]))
        for lbl, path in (("pooled", ("dash1", "pooled_pairedH")),
                          ("hidden", ("dash1", "hidden_H3_pairedH")),
                          ("allhaz", ("dash1", "all_haz"))):
            for m in ("frame_recall", "frame_recall_twin",
                      "cell_recall", "cell_recall_twin"):
                e[f"{lbl}_{m}"] = agg([r["ops"][i][path[0]][path[1]][m] for r in rs])
        for m, path in (("FA_C_frame", ("FA_C", "frame_fa")),
                        ("FA_C_cell", ("FA_C", "cell_fpr")),
                        ("FA_D_frame", ("FA_D", "frame_fa")),
                        ("FA_D_cell", ("FA_D", "cell_fpr"))):
            e[m] = agg([r["ops"][i]["dash3"][path[0]][path[1]] for r in rs])
        e["FA_diff_frame"] = agg([r["ops"][i]["dash3"]["diff_frame"] for r in rs])
        e["FA_diff_cell"] = agg([r["ops"][i]["dash3"]["diff_cell"] for r in rs])
        for g in ("ncue", "hscenes", "lat"):
            for a2 in ("FA_C", "FA_D"):
                e[f"{g}_{a2}_frame"] = agg(
                    [r["ops"][i]["dash3"]["group"][g][a2]["frame_fa"] for r in rs])
                e[f"{g}_{a2}_cell"] = agg(
                    [r["ops"][i]["dash3"]["group"][g][a2]["cell_fpr"] for r in rs])
        e["by_scene"] = {}
        for s in sorted(rs[0]["ops"][i]["dash3"]["by_scene"]):
            e["by_scene"][s] = dict(
                FA_C_frame=agg([r["ops"][i]["dash3"]["by_scene"][s]["FA_C"]["frame_fa"]
                                for r in rs]),
                FA_C_cell=agg([r["ops"][i]["dash3"]["by_scene"][s]["FA_C"]["cell_fpr"]
                               for r in rs]),
                FA_D_frame=agg([r["ops"][i]["dash3"]["by_scene"][s]["FA_D"]["frame_fa"]
                                for r in rs]),
                FA_D_cell=agg([r["ops"][i]["dash3"]["by_scene"][s]["FA_D"]["cell_fpr"]
                               for r in rs]))
        e["dash1_by_scene"] = {}
        for s in sorted(rs[0]["ops"][i]["dash1"]["by_scene"]):
            e["dash1_by_scene"][s] = dict(
                frame_recall=agg([r["ops"][i]["dash1"]["by_scene"][s]["frame_recall"]
                                  for r in rs]),
                frame_recall_twin=agg([r["ops"][i]["dash1"]["by_scene"][s]["frame_recall_twin"]
                                       for r in rs]),
                cell_recall=agg([r["ops"][i]["dash1"]["by_scene"][s]["cell_recall"]
                                 for r in rs]),
                cell_recall_twin=agg([r["ops"][i]["dash1"]["by_scene"][s]["cell_recall_twin"]
                                      for r in rs]),
                n=rs[0]["ops"][i]["dash1"]["by_scene"][s]["n_frames"])
        e["l1"] = {}
        for s in grid.sector_names:
            for w in ("fire_A", "fire_C", "fire_D"):
                e["l1"][f"{w}_{s}_frame"] = agg(
                    [r["ops"][i]["l1"][w][s]["frame_rate"] for r in rs])
                e["l1"][f"{w}_{s}_share"] = agg(
                    [r["ops"][i]["l1"][w][s]["cell_share"] for r in rs])
            e["l1"][f"fire_A_{s}_ncells"] = agg(
                [r["ops"][i]["l1"]["fire_A"][s]["n_cells"] for r in rs])
        e["l1"]["fire_A_total"] = agg([r["ops"][i]["l1"]["fire_A"]["_total_cells"] for r in rs])
        rows.append(e)
    out = dict(runs=[r["run"] for r in rs], ops=rows)
    for lbl, src in (("hidden_dp", "hidden_dp"), ("pool_dp", "pool_dp")):
        block = {}
        get = (lambda r: r["hidden_dp"]["pairedH"]) if lbl == "hidden_dp" else (lambda r: r["pool_dp"])
        for m in ("mean", "p50", "mean_abs", "frac_abs_le_05", "frac_gt0", "min", "max"):
            block[f"delta_score_{m}"] = agg([get(r)["delta_score"].get(m) for r in rs])
        block["per_run"] = {r["run"]: get(r)["delta_score"] for r in rs}
        out[lbl] = block
    out["l1_hazard_gt"] = rs[0]["l1_hazard_gt"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-dir", default=os.path.join(V3, "eval_v3a_textext"))
    ap.add_argument("--out", default=os.path.join(V3, "v3a_textext_tables.json"))
    ap.add_argument("--calib", default=os.path.join(V3, "logs", "verdict_calibration.json"))
    a = ap.parse_args(argv)

    print("[raw]")
    raw = build(a.eval_dir, V3A_RUNS, V3A_AUX, "raw")

    cal = None
    if os.path.isfile(a.calib):
        Ts = {k: v["T"] for k, v in json.load(open(a.calib, encoding="utf-8"))["runs"].items()}
        tmp = os.path.join(V3, "logs", "verdict_cal_pf")
        _apply_T(a.eval_dir, V3A_RUNS + V3A_AUX, Ts, tmp)
        print("[calibrated]")
        cal = build(tmp, V3A_RUNS, V3A_AUX, "calibrated")
        cal["temperatures"] = Ts

    # ---- 항등 검산: temperature 는 강단조 ⇒ 8지점의 선택 집합 불변 ----------
    ident = {"checked": 0, "max_abs_diff": 0.0, "fields": [], "mismatch": []}
    if cal is not None:
        for arm in raw["summary"]:
            for i, ro in enumerate(raw["summary"][arm]["ops"]):
                co = cal["summary"][arm]["ops"][i]
                for f in ("pooled_frame_recall_twin", "pooled_cell_recall_twin",
                          "pooled_frame_recall", "pooled_cell_recall",
                          "FA_C_frame", "FA_C_cell", "FA_D_frame", "FA_D_cell",
                          "FA_diff_frame", "FA_diff_cell",
                          "hidden_frame_recall_twin", "hidden_cell_recall_twin"):
                    x, y = ro[f]["mean"], co[f]["mean"]
                    if not (np.isfinite(x) and np.isfinite(y)):
                        continue
                    ident["checked"] += 1
                    d = abs(x - y)
                    if d > ident["max_abs_diff"]:
                        ident["max_abs_diff"] = float(d)
                    if d > 1e-12:
                        ident["mismatch"].append(dict(arm=arm, op=ro["name"], field=f,
                                                      raw=x, cal=y, diff=float(d)))
        ident["fields"] = ["recall/FA at tau_op and all 8 FA-matched points"]
    print(f"[identity] {ident['checked']} 값 대조 · max|Δ| = {ident['max_abs_diff']:.3e} · "
          f"불일치 {len(ident['mismatch'])}")

    doc = dict(doc="v3-A on test-ext — 계기판 ①/③ + L1 (PREREG §2 · 계산 코드 = v2_textext_tables)",
               raw=raw, calibrated=cal, calibration_identity=ident,
               note=("temperature 는 강단조 변환이므로 τ_op 0.5 와 분위 기반 FA-정합 8지점에서 "
                     "선택되는 칸·프레임 집합이 불변이다. 위 검산이 그 항등을 실측으로 확인한다. "
                     "보정이 실제로 바꾸는 것은 확률값 자체(Δp · ECE · 신뢰도 곡선)뿐이다."))
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
