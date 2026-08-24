#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_rollup.py — PREREG §3.5 판정 규칙의 기계 집행 (CPU 전용)

계기판별 1차 판정 ∈ {개선, 판정 불가, 악화}
  · **개선** = 프레임축·칸축 **8지점 전부**에서 부호가 개선 방향 ∧ 모델 평균 |Δ| > σ
  · **악화** = 8지점 전부에서 부호가 악화 방향 ∧ |Δ| > σ
  · **판정 불가** = 그 외 전부. **축 간 부호 불일치는 판정 불가**이며 사실과 사유를 인쇄.
  · τ_op 0.5 · τ* 는 **참고 병기 전용 · 판정 불사용** (§3.3)
  · 완전 은닉층(H3)은 계기판① 판정에 **산입하지 않는다** (§3.4 · §3.5)

σ 의 정의 = 표본표준편차 **ddof=1**, n=3 (§3.2). 판정선 σ 는 **max(σ_v2, σ_v3)** 를
정본으로 쓴다 — §3.2 가 `range/2` 를 버린 이유가 "성공 선언 쪽 편향의 수리"이므로
두 σ 중 **큰 쪽**을 문턱으로 삼는 보수적 선택이 그 취지에 맞다. 풀링 σ 는 민감도로 병기.

종합: 개선 3/3 ∧ 악화 0 = **창발** · 개선 1–2 ∧ 악화 0 = **부분** · 개선 0 또는 악화 ≥1 = **미달**
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "mainrun_0819", "code"))

import gridspec                    # noqa: E402
import v2_textext_tables as T2     # noqa: E402

JUDGE_OPS = ["F@0.359", "F@0.200", "F@0.100", "F@0.050",
             "C@0.046732", "C@0.026035", "C@0.013017", "C@0.006509"]
REF_OPS = ["tau_op", "tau_star"]
RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
AUX = ["rgb_s42_aux"]


def ops_by_name(ops):
    return {o["name"]: o for o in ops}


def cmp_series(v2ops, v3ops, field, direction):
    """한 (지표, 단위) 계열의 8지점 비교. direction ∈ {+1(↑ 개선), -1(↓ 개선)}."""
    a, b = ops_by_name(v2ops), ops_by_name(v3ops)
    rows, n_ok, n_bad = [], 0, 0
    for name in JUDGE_OPS:
        x, y = a.get(name), b.get(name)
        if x is None or y is None:
            continue
        m2, s2 = x[field]["mean"], x[field]["sd"]
        m3, s3 = y[field]["mean"], y[field]["sd"]
        if m2 is None or m3 is None or not (np.isfinite(m2) and np.isfinite(m3)):
            rows.append(dict(op=name, v2=m2, v3=m3, delta=None, note="비유한"))
            continue
        d = m3 - m2
        sig_max = max(s2 or 0.0, s3 or 0.0)
        sig_pool = float(np.sqrt(((s2 or 0.0) ** 2 + (s3 or 0.0) ** 2) / 2))
        good = (d * direction) > 0
        exceeds = abs(d) > sig_max
        rows.append(dict(op=name, v2=m2, sd_v2=s2, v3=m3, sd_v3=s3, delta=d,
                         sigma_gate=sig_max, sigma_pooled=sig_pool,
                         direction_ok=bool(good), exceeds_sigma=bool(exceeds),
                         exceeds_sigma_pooled=bool(abs(d) > sig_pool),
                         seeds_better=None))
        n_ok += bool(good and exceeds)
        n_bad += bool((not good) and exceeds and abs(d) > 0)
    signs = [r.get("direction_ok") for r in rows if r.get("delta") is not None]
    all_good = bool(signs) and all(signs)
    all_bad = bool(signs) and not any(signs)
    all_gate = all(r.get("exceeds_sigma") for r in rows if r.get("delta") is not None)
    if all_good and all_gate:
        v = "개선"
    elif all_bad and all_gate:
        v = "악화"
    else:
        v = "판정 불가"
    return dict(field=field, direction=("↑" if direction > 0 else "↓"),
                rows=rows, verdict=v,
                n_points=len(signs), n_direction_ok=int(sum(bool(s) for s in signs)),
                n_direction_ok_and_sigma=n_ok,
                sign_consistent=bool(all_good or all_bad),
                sigma_all=bool(all_gate))


def combine(parts, label):
    """한 계기판의 여러 (지표,단위) 계열을 §3.5 로 합친다."""
    vs = [p["verdict"] for p in parts]
    if all(v == "개선" for v in vs):
        v = "개선"
    elif all(v == "악화" for v in vs):
        v = "악화"
    else:
        v = "판정 불가"
    why = []
    for p in parts:
        if p["verdict"] != "개선":
            if not p["sign_consistent"]:
                why.append(f"{p['field']}: 8지점 부호 불일치 "
                           f"({p['n_direction_ok']}/{p['n_points']} 개선 방향)")
            elif not p["sigma_all"]:
                why.append(f"{p['field']}: 부호는 {'개선' if p['n_direction_ok'] else '악화'} "
                           f"방향 일치이나 |Δ| > σ 가 "
                           f"{p['n_direction_ok_and_sigma']}/{p['n_points']} 지점에서만 성립")
    return dict(dashboard=label, verdict=v, series=parts, reasons=why)


# ---------------------------------------------------------------- 경보 부담
def alarm_burden(evdir, runs, grid):
    """칸/FA프레임 — PREREG §2.1 '경보 부담 병기 의무'. 추정량 = **시드 합산**(P-08)."""
    per_op = defaultdict(lambda: dict(fire_cells=0, fire_frames=0, per_run={}))
    tau_cache = {}
    for run in runs:
        ac = T2.read_pf(os.path.join(evdir, run, "per_frame.csv"), grid)
        bd = T2.read_pf(os.path.join(evdir, run, "bd", "per_frame.csv"), grid)
        _, C_idx = T2.arm_view(ac, "off")
        _, D_idx = T2.arm_view(bd, "off")
        dfs = bd["probs"][D_idx].max(1)
        dcs = bd["probs"][D_idx].ravel()
        ops = [("tau_op", 0.5)]
        for t in T2.FRAME_TARGETS:
            ops.append((f"F@{t:.3f}", T2.tau_for_target(dfs, t)[0]))
        for t in T2.CELL_TARGETS:
            ops.append((f"C@{t:.6f}", T2.tau_for_target(dcs, t)[0]))
        for name, tau in ops:
            tau_cache.setdefault(name, []).append(tau)
            for lbl, d, idx in (("C", ac, C_idx), ("D", bd, D_idx)):
                fire = d["probs"][idx] >= tau
                k = f"{name}|{lbl}"
                per_op[k]["fire_cells"] += int(fire.sum())
                per_op[k]["fire_frames"] += int(fire.any(1).sum())
                per_op[k]["per_run"][run] = (
                    float(fire.sum() / max(fire.any(1).sum(), 1)))
    out = {}
    for k, v in per_op.items():
        pooled = v["fire_cells"] / v["fire_frames"] if v["fire_frames"] else None
        vals = list(v["per_run"].values())
        out[k] = dict(cells_per_fa_frame_pooled=pooled,
                      cells_per_fa_frame_seedmean=float(np.mean(vals)) if vals else None,
                      sd=float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                      n_fire_frames=v["fire_frames"], n_fire_cells=v["fire_cells"],
                      per_run=v["per_run"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(V3, "verdict_v3_rollup.json"))
    a = ap.parse_args(argv)
    grid = gridspec.load("gridspec_v1.json")

    V2T = json.load(open(os.path.join(V3, "v2_textext_tables.json"), encoding="utf-8"))
    V3T = json.load(open(os.path.join(V3, "v3a_textext_tables.json"), encoding="utf-8"))
    D2 = json.load(open(os.path.join(V3, "verdict_dash2.json"), encoding="utf-8"))
    CORE = json.load(open(os.path.join(V3, "verdict_core.json"), encoding="utf-8"))
    CAL = json.load(open(os.path.join(V3, "logs", "verdict_calibration.json"),
                         encoding="utf-8"))

    v2ops = V2T["summary"]["rgb"]["ops"]
    v3ops = V3T["raw"]["summary"]["v3a_rgb"]["ops"]
    auxops = V3T["raw"]["summary"]["v3a_rgb_aux_isolated"]["ops"]

    # ---------------- 계기판 ① (풀링층 · H3 산입 금지) ----------------------
    d1 = combine([
        cmp_series(v2ops, v3ops, "pooled_frame_recall_twin", +1),
        cmp_series(v2ops, v3ops, "pooled_cell_recall_twin", +1),
    ], "① 트윈-조건부 recall (A,C) · 풀링층 H1+H2 (n=51)")
    d1["hidden_stratum"] = dict(
        note=("§3.4 — 완전 은닉층(H3계)은 **부호 없음**. A/C 동등 발화가 정답이고 "
              "recall 상승을 개선으로 세면 §6-4 위반. 계기판① 판정에 산입하지 않는다."),
        n=21,
        v2=dict(frac_abs_dp_le_05=V2T["summary"]["rgb"]["hidden_dp"]["frac_abs_le_05"]["mean"],
                mean_abs_dp=V2T["summary"]["rgb"]["hidden_dp"]["delta_score_meanabs"]["mean"],
                twin_recall_by_op={o["name"]: o["hidden_frame_recall_twin"]["mean"]
                                   for o in v2ops}),
        v3_raw=dict(frac_abs_dp_le_05=V3T["raw"]["summary"]["v3a_rgb"]["hidden_dp"]
                    ["delta_score_frac_abs_le_05"]["mean"],
                    mean_abs_dp=V3T["raw"]["summary"]["v3a_rgb"]["hidden_dp"]
                    ["delta_score_mean_abs"]["mean"],
                    twin_recall_by_op={o["name"]: o["hidden_frame_recall_twin"]["mean"]
                                       for o in v3ops}),
        v3_calibrated=dict(
            frac_abs_dp_le_05=V3T["calibrated"]["summary"]["v3a_rgb"]["hidden_dp"]
            ["delta_score_frac_abs_le_05"]["mean"],
            mean_abs_dp=V3T["calibrated"]["summary"]["v3a_rgb"]["hidden_dp"]
            ["delta_score_mean_abs"]["mean"]),
        verdict_text="은닉 완전성 유지 (동등 발화) — 판정 산입 없음",
    )
    d1["reference_points_not_used_for_verdict"] = {
        n: dict(v2_frame=ops_by_name(v2ops)[n]["pooled_frame_recall_twin"]["mean"],
                v3_frame=ops_by_name(v3ops)[n]["pooled_frame_recall_twin"]["mean"],
                v2_cell=ops_by_name(v2ops)[n]["pooled_cell_recall_twin"]["mean"],
                v3_cell=ops_by_name(v3ops)[n]["pooled_cell_recall_twin"]["mean"])
        for n in REF_OPS if n in ops_by_name(v2ops) and n in ops_by_name(v3ops)}

    # --- 의무 보조 열: 트윈 통과율 (ab_table_shells §1.2) · **판정 불사용** ---
    def pass_rate(tabpath, per_run_key):
        d = json.load(open(tabpath, encoding="utf-8"))
        pr = d["per_run"] if "per_run" in d else d[per_run_key]["per_run"]
        n_ops = len(pr[RUNS[0]]["ops"])
        out = {}
        for i in range(n_ops):
            nm = pr[RUNS[0]]["ops"][i]["name"]
            fr, ce = [], []
            for r in RUNS:
                b = pr[r]["ops"][i]["dash1"]["pooled_pairedH"]
                fr.append(b["frame_recall_twin"] / b["frame_recall"]
                          if b["frame_recall"] else float("nan"))
                ce.append(b["cell_recall_twin"] / b["cell_recall"]
                          if b["cell_recall"] else float("nan"))
            out[nm] = dict(frame=dict(mean=float(np.mean(fr)),
                                      sd=float(np.std(fr, ddof=1)), vals=fr),
                           cell=dict(mean=float(np.mean(ce)),
                                     sd=float(np.std(ce, ddof=1)), vals=ce))
        return out
    pr2 = pass_rate(os.path.join(V3, "v2_textext_tables.json"), "raw")
    pr3 = pass_rate(os.path.join(V3, "v3a_textext_tables.json"), "raw")
    d1["aux_pass_through_rate"] = dict(
        definition="트윈 통과율 = 트윈-조건부 recall / 맨 recall (시드별 계산 후 3시드 평균)",
        status=("**의무 보조 열** — ab_table_shells §1.2. **판정 지표가 아니다**; 결과를 본 뒤 "
                "이 열을 판정으로 승격하면 PREREG §6-1 위반."),
        rows={n: dict(
            v2_frame=pr2[n]["frame"], v3_frame=pr3[n]["frame"],
            d_frame=pr3[n]["frame"]["mean"] - pr2[n]["frame"]["mean"],
            exceeds_frame=abs(pr3[n]["frame"]["mean"] - pr2[n]["frame"]["mean"]) >
                          max(pr2[n]["frame"]["sd"], pr3[n]["frame"]["sd"]),
            v2_cell=pr2[n]["cell"], v3_cell=pr3[n]["cell"],
            d_cell=pr3[n]["cell"]["mean"] - pr2[n]["cell"]["mean"],
            exceeds_cell=abs(pr3[n]["cell"]["mean"] - pr2[n]["cell"]["mean"]) >
                         max(pr2[n]["cell"]["sd"], pr3[n]["cell"]["sd"]))
              for n in pr2})
    d1["stratum_table"] = {n: {s: ops_by_name(v3ops)[n]["dash1_by_scene"][s]
                               for s in ops_by_name(v3ops)[n]["dash1_by_scene"]}
                           for n in ["tau_op"] + JUDGE_OPS
                           if "dash1_by_scene" in ops_by_name(v3ops)[n]}

    # ---------------- 계기판 ② -------------------------------------------
    s2 = D2["summary"]["v3a_rgb"]["ops"]
    d2 = dict(dashboard="② CUE-OFF 용량-반응 (A,B)", verdict="판정 불가",
              reasons=[("v2 쪽 팔이 **구조적으로 성립하지 않는다** — PREREG §2.2 주의 · "
                        "V2_TEXTEXT_BASELINE §4. 등록된 처분이 '**v3 단독 절대값 + 층별 "
                        "기울기**'이므로 v2→v3 델타를 8지점에서 만들 수 없고, §3.5 의 "
                        "개선/악화 술어가 적용될 대상 자체가 없다."),
                       (f"판정 모집단이 등록 하한(n_paired ≥ 10)을 통과한 단위 **4개**뿐 — "
                        f"OLS 자유도 2. 회귀 계수의 시드 σ 가 계수 자체와 같은 자릿수다."),
                       ("두 회귀변수의 공선성 r = 0.487 — 완전 교락은 아니나 n=4 에서 "
                        "분리 검정력이 없다.")],
              registered_direction="광학 변화량 기울기 ↓ ∧ 단서 개수 기울기 ↑",
              v2_reference=D2["v2_reference"], unit_static=D2["unit_static"],
              v3_slopes={e["op"]: dict(
                  tau=e["tau"]["mean"],
                  cue_slope=e["fa_frame_B|vs_cue_count|slope"],
                  cue_slope_std=e["fa_frame_B|vs_cue_count|slope_std"],
                  cue_r2=e["fa_frame_B|vs_cue_count|r2"],
                  opt_slope=e["fa_frame_B|vs_optical_mean|slope"],
                  opt_slope_std=e["fa_frame_B|vs_optical_mean|slope_std"],
                  opt_r2=e["fa_frame_B|vs_optical_mean|r2"],
                  cue_slope_cell=e["fa_cell_B|vs_cue_count|slope_std"],
                  opt_slope_cell=e["fa_cell_B|vs_optical_mean|slope_std"],
                  dominant=e["dominant_fa_frame_B"],
                  companion_n=e.get("companion_n"),
                  companion_cue_std=e.get("companion|vs_cue_count|slope_std"),
                  companion_opt_std=e.get("companion|vs_optical_mean|slope_std"))
                  for e in s2},
              stratification_5family=("**미산출** — PREREG §2.2 층화 행(FA 5가족)의 분류기는 "
                                      "v2 코퍼스 라운드의 칸 광도 원장 위에 만들어져 있고 "
                                      "test-ext 4단위에는 이식되지 않았다. 인쇄 의무 미이행 "
                                      "1건으로 §결재란에 올린다."))
    dom_all = [x for e in s2 if e["op"] in JUDGE_OPS for x in e["dominant_fa_frame_B"]]
    d2["dominant_census"] = {k: dom_all.count(k) for k in set(dom_all)}

    # ---------------- 계기판 ③ -------------------------------------------
    d3 = combine([
        cmp_series(v2ops, v3ops, "FA_C_frame", -1),
        cmp_series(v2ops, v3ops, "FA_C_cell", -1),
        cmp_series(v2ops, v3ops, "FA_diff_frame", -1),
        cmp_series(v2ops, v3ops, "FA_diff_cell", -1),
    ], "③ N-cue 함정 FA (FA_C ↓ ∧ FA_C−FA_D ↓)")
    d3["by_group"] = {}
    for g in ("ncue", "hscenes", "lat"):
        d3["by_group"][g] = {}
        for n in REF_OPS + JUDGE_OPS:
            x, y = ops_by_name(v2ops).get(n), ops_by_name(v3ops).get(n)
            if not x or not y:
                continue
            d3["by_group"][g][n] = dict(
                v2_FA_C_frame=x[f"{g}_FA_C_frame"], v3_FA_C_frame=y[f"{g}_FA_C_frame"],
                v2_FA_D_frame=x[f"{g}_FA_D_frame"], v3_FA_D_frame=y[f"{g}_FA_D_frame"],
                v2_FA_C_cell=x[f"{g}_FA_C_cell"], v3_FA_C_cell=y[f"{g}_FA_C_cell"],
                v2_FA_D_cell=x[f"{g}_FA_D_cell"], v3_FA_D_cell=y[f"{g}_FA_D_cell"])
    d3["by_scene"] = {}
    for n in ["tau_op"] + JUDGE_OPS:
        x, y = ops_by_name(v2ops).get(n), ops_by_name(v3ops).get(n)
        if not x or not y or "by_scene" not in y:
            continue
        d3["by_scene"][n] = {s: dict(
            v3_FA_C_frame=y["by_scene"][s]["FA_C_frame"],
            v3_FA_D_frame=y["by_scene"][s]["FA_D_frame"],
            v3_FA_C_cell=y["by_scene"][s]["FA_C_cell"],
            v3_FA_D_cell=y["by_scene"][s]["FA_D_cell"]) for s in y["by_scene"]}
    d3["negative_flip_caveat"] = ("§2.3 축 부호 사전 명기 — FA_C−FA_D 의 음전은 '개선' 이 "
                                  "아니라 '단서를 아예 안 본다' 는 뜻일 수 있으므로 "
                                  "**FA_C 절대값과 함께** 읽는다.")

    # ---------------- 경보 부담 ------------------------------------------
    burden = dict(
        v2=alarm_burden(os.path.join(V3, "eval_v3textext"), RUNS, grid),
        v3=alarm_burden(os.path.join(V3, "eval_v3a_textext"), RUNS, grid),
        estimator="시드 합산(pooled)이 정본 — PREREG §2.1 [해소: P-08]. 시드 평균 병기.")

    # ---------------- test-core 헤드라인 ---------------------------------
    core = {}
    for k in ("frame_recall_H", "cell_recall_H", "frame_recall_V", "cell_recall_V",
              "frame_recall_E", "cell_recall_E", "cell_f1", "cell_precision",
              "cell_recall", "frame_det_rate", "frame_fa_off", "cell_fpr_off",
              "cells_per_fa_frame", "tau"):
        core[k] = []
        for x, y in zip(CORE["v2"]["ops"], CORE["v3"]["ops"]):
            m2, s2_ = x[k]["mean"], x[k]["sd"]
            m3, s3_ = y[k]["mean"], y[k]["sd"]
            d = (m3 - m2) if (m2 is not None and m3 is not None) else None
            gate = max(s2_ or 0.0, s3_ or 0.0)
            core[k].append(dict(op=x["name"], v2=m2, sd_v2=s2_, v3=m3, sd_v3=s3_,
                                delta=d, sigma_gate=gate,
                                exceeds=(d is not None and abs(d) > gate)))
    core["cells_per_fa_frame_pooled"] = [
        dict(op=x["name"], v2=x["cells_per_fa_frame_pooled"],
             v3=y["cells_per_fa_frame_pooled"])
        for x, y in zip(CORE["v2"]["ops"], CORE["v3"]["ops"])]
    core["counts"] = dict(v2=CORE["v2"]["counts"], v3=CORE["v3"]["counts"])
    core["aux_isolated"] = {o["name"]: {k: o[k]["mean"] for k in
                                        ("frame_recall_H", "cell_recall_H", "cell_f1",
                                         "frame_fa_off", "cell_fpr_off",
                                         "cells_per_fa_frame")}
                            for o in CORE["v3_aux_isolated"]["ops"]}

    # ---------------- L1 측방 (V2S 재론 행) -------------------------------
    l1 = dict(hazard_gt=V3T["raw"]["summary"]["v3a_rgb"]["l1_hazard_gt"], ops={})
    for n in ["tau_op"] + JUDGE_OPS:
        x, y = ops_by_name(v2ops).get(n), ops_by_name(v3ops).get(n)
        if not x or not y:
            continue
        row = {}
        for s in grid.sector_names:
            row[s] = dict(v2_frame=x["l1"][f"fire_A_{s}_frame"]["mean"],
                          v2_share=x["l1"][f"fire_A_{s}_share"]["mean"],
                          v3_frame=y["l1"][f"fire_A_{s}_frame"]["mean"],
                          v3_share=y["l1"][f"fire_A_{s}_share"]["mean"])
        def sh(side, keys):
            return sum((row[s][side] or 0.0) for s in keys)
        row["_AE_v2"] = sh("v2_share", ["A", "E"]); row["_AE_v3"] = sh("v3_share", ["A", "E"])
        row["_BD_v2"] = sh("v2_share", ["B", "D"]); row["_BD_v3"] = sh("v3_share", ["B", "D"])
        row["_C_v2"] = row["C"]["v2_share"]; row["_C_v3"] = row["C"]["v3_share"]
        row["_total_cells_v3"] = y["l1"]["fire_A_total"]["mean"]
        l1["ops"][n] = row

    # ---------------- 종합 ------------------------------------------------
    dash = [d1, d2, d3]
    n_improved = sum(1 for d in dash if d["verdict"] == "개선")
    n_worse = sum(1 for d in dash if d["verdict"] == "악화")
    if n_worse >= 1 or n_improved == 0:
        overall = "미달"
    elif n_improved == 3:
        overall = "창발"
    else:
        overall = "부분"

    doc = dict(
        doc="VERDICT rollup — PREREG §3.5 기계 집행",
        prereg_sha256="05f41322e52b8e085b4d678c57dba4ee984deff3bfcea960123ae586e9fcf56a",
        judgement_points=JUDGE_OPS, reference_points=REF_OPS,
        sigma_rule="ddof=1 · 판정선 σ = max(σ_v2, σ_v3) · 풀링 σ 병기",
        dashboards=dict(d1=d1, d2=d2, d3=d3),
        overall=dict(classification=overall, n_improved=n_improved, n_worse=n_worse,
                     n_undecidable=3 - n_improved - n_worse,
                     rule="개선 3/3 ∧ 악화 0 = 창발 · 개선 1–2 ∧ 악화 0 = 부분 · "
                          "개선 0 또는 악화 ≥1 = 미달",
                     status="Claude 예비판정 — 최종 채택은 승용"),
        alarm_burden=burden, core=core, l1=l1,
        calibration={k: dict(T=v["T"], T_masked=v["T_masked_sensitivity"],
                             ece_raw=v["ece_raw"], ece_cal=v["ece_cal"],
                             nll_raw=v["nll_raw"], nll_cal=v["nll_cal"],
                             brier_raw=v["brier_raw"], brier_cal=v["brier_cal"],
                             mce_raw=v["mce_raw"], mce_cal=v["mce_cal"],
                             isolated=v["isolated"],
                             selective_raw=v["selective_raw"],
                             selective_cal=v["selective_cal"])
                     for k, v in CAL["runs"].items()},
        calibration_identity=V3T["calibration_identity"],
        aux_isolated_dash=dict(
            note="[격리·진단] — 본 A/B 판정에 혼입하지 않는다 (PREREG §5.6 · D82 ③)",
            ops={o["name"]: dict(
                pooled_frame_recall_twin=o["pooled_frame_recall_twin"],
                pooled_cell_recall_twin=o["pooled_cell_recall_twin"],
                FA_C_frame=o["FA_C_frame"], FA_C_cell=o["FA_C_cell"],
                FA_D_frame=o["FA_D_frame"], FA_D_cell=o["FA_D_cell"],
                FA_diff_frame=o["FA_diff_frame"], FA_diff_cell=o["FA_diff_cell"])
                for o in auxops}),
    )
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[verdict] ① {d1['verdict']} · ② {d2['verdict']} · ③ {d3['verdict']} "
          f"⇒ **{overall}** (개선 {n_improved} / 악화 {n_worse})")
    for d in dash:
        for r in d.get("reasons", []):
            print(f"   - {d['dashboard'][:6]} {r[:110]}")
    print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
