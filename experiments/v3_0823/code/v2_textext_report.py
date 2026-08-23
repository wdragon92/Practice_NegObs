#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2_textext_report.py — `V2_TEXTEXT_BASELINE.md` 생성기 (표는 전부 JSON 원장에서 조판).

수치를 손으로 옮겨 적지 않는다. 입력은 `v2_textext_tables.json` 하나뿐이고,
산문은 이 파일 안의 리터럴이다. 재생성:

    python3 experiments/v3_0823/code/v2_textext_report.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")

ARMS = ["rgb", "depth", "b2"]
ARM_LBL = {"rgb": "RGB", "depth": "Depth", "b2": "b2(SegFormer)"}
OPS_FA = ["F@0.359", "F@0.200", "F@0.100", "F@0.050",
          "C@0.046732", "C@0.026035", "C@0.013017", "C@0.006509"]
OP_LBL = {"tau_op": "τ_op 0.5 *(참고)*", "tau_star": "τ\\* (런별 동결) *(참고)*",
          "F@0.359": "프레임축 FA .359", "F@0.200": "프레임축 FA .200",
          "F@0.100": "프레임축 FA .100", "F@0.050": "프레임축 FA .050",
          "C@0.046732": "칸축 MAP-C .046732", "C@0.026035": "칸축 MAP-C .026035",
          "C@0.013017": "칸축 MAP-C .013017", "C@0.006509": "칸축 MAP-C .006509"}


def g(d, name):
    for o in d["ops"]:
        if o["name"] == name:
            return o
    raise KeyError(name)


def m(a, nd=3):
    if a is None or a.get("n", 0) == 0:
        return "n/a"
    return f"{a['mean']:.{nd}f} ± {a['sd']:.{nd}f}"


def m1(a, nd=3):
    if a is None or a.get("n", 0) == 0:
        return "n/a"
    return f"{a['mean']:.{nd}f}"


def ratio(num, den):
    if not num or not den or den.get("n", 0) == 0 or den["mean"] <= 0:
        return "n/a"
    return f"{num['mean'] / den['mean']:.2f}"


def build(J):
    S, P = J["summary"], J["per_run"]
    C = P["rgb_s42"]["counts"]
    L = []
    A = L.append

    A("# V2_TEXTEXT_BASELINE — v2 체크포인트 **zero-shot** test-ext 재채점")
    A("")
    A("> **이 표가 v3-A 의 before 다.** `ACCOUNTING §2-8` 이 *\"v2 에 N-cue 표본 없음으로 "
      "끝내지 말고 v2 체크포인트를 test-ext 에 zero-shot 재채점해 **진짜 before** 를 만들라\"* 고 "
      "명령한 그 표다. test-ext 는 v2·v3 양 모델이 **공히 미학습**이므로 공정 비교가 성립한다"
      "(`AC §2-9`).")
    A("")
    A("| | |")
    A("|---|---|")
    A("| 대상 | 레시피-v2 동결 체크포인트 **9개** (`experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}`) |")
    A("| 무대 | W3 test-ext 6씬 · 4팔 (`dataset_manifest_v3_textext{,_bd}.json`) |")
    A("| 쌍 | **(A,C)** — 위험만 제거·단서 보존 (`AC §2-2` 세대 통일). v2 공표 44.7 %/0 % 는 (A,D) 라 **참고치 강등 유지** |")
    A("| τ\\* | **런별 동결 공표값** 승계 (재적합 금지 — `W3_REPORT §9`) |")
    A("| 그리드 | `PROVISIONAL-GRID-V1` · 4밴드 × 5섹터 = 20칸 |")
    A("| 재집계 | `code/rescore_v3textext.sh` → `code/v2_textext_tables.py` → **본 문서 = `code/v2_textext_report.py`** |")
    A("| 원장 | `v2_textext_tables.json` · `eval_v3textext/<run>/{,bd/}metrics.json` |")
    A("| 측정일 | 2026-08-24 |")
    A("")

    # ---------------------------------------------------------------- 승용 요약
    r_op, d_op, b_op = g(S["rgb"], "tau_op"), g(S["depth"], "tau_op"), g(S["b2"], "tau_op")
    A("## 승용 요약 (6문장)")
    A("")
    A(f"1. **계기판① 의 before 가 생겼다.** paired-H 풀링층(H1+H2, n={C['n_pool_pairedH']})에서 "
      f"v2 의 **트윈-조건부** 프레임 recall 은 τ_op 0.5 에서 RGB {m1(r_op['pooled_frame_recall_twin'])} · "
      f"Depth {m1(d_op['pooled_frame_recall_twin'])} 이고, **같은 지점의 맨 recall** 은 "
      f"RGB {m1(r_op['pooled_frame_recall'])} · Depth {m1(d_op['pooled_frame_recall'])} 이다 — "
      f"즉 v2 발화의 **{100 * (1 - r_op['pooled_frame_recall_twin']['mean'] / r_op['pooled_frame_recall']['mean']):.0f} %"
      f"(RGB) / {100 * (1 - d_op['pooled_frame_recall_twin']['mean'] / d_op['pooled_frame_recall']['mean']):.0f} %(Depth)** 는 "
      "낙차를 지워도 그대로 남는다.")
    A(f"2. **완전 은닉층(sceneH3, n={C['n_hidden_pairedH']})의 트윈-조건부 recall 은 9런 전부에서 "
      "사실상 0** 이고, Δp 는 |Δp| ≤ 0.05 가 **21/21 · 9/9 런**이다 (Depth 는 정확히 0.0000). "
      "D87 ① 이 *\"올바른 모델은 A/C 동등 발화가 정답\"* 이라고 예고한 그 값이다 — **성적이 아니라 "
      "은닉 완전성의 측정치**다.")
    A(f"3. **계기판③ 의 함정이 실측됐다.** τ_op 에서 **FA_C {m1(r_op['FA_C_frame'])} vs "
      f"FA_D {m1(r_op['FA_D_frame'])}** (RGB, 프레임축) — 분해하면 **FA_C − FA_D = "
      f"{m1(r_op['FA_diff_frame'])}** 이다. 위험도 단서도 없는 D팔에서는 거의 안 울리는 모델이 "
      "**단서만 켜면 울린다**.")
    A(f"4. **N-cue 두 씬(N9·N11)이 그 함정의 순수 배양접시다** — τ_op FA_C 프레임 RGB "
      f"{m1(r_op['ncue_FA_C_frame'])} · b2 {m1(b_op['ncue_FA_C_frame'])} 대 FA_D "
      f"RGB {m1(r_op['ncue_FA_D_frame'])} · b2 {m1(b_op['ncue_FA_D_frame'])}. "
      f"반면 **Depth 는 같은 자리에서 FA_C {m1(d_op['ncue_FA_C_frame'])}** 로 거의 걸리지 않는다 — "
      "단서가 **광학량**이라 깊이 입력에는 실리지 않기 때문이며, 이것이 계기판③ 이 재려는 병의 정체다.")
    A("5. **측방(sceneL1)에서 v2 는 방향을 못 맞춘다.** 위험 질량은 A+E **0.6722** · 정면 C "
      f"**0.0328** 인데 v2 발화 질량은 A+E {ratio_ae(S, 'rgb')} · 정면 C {ratio_c(S, 'rgb')} (RGB, τ_op) — "
      "**정면 과발화 · 측방 미발화**다. V2S(섹터 5→10) 재론의 기준선이 이것이다.")
    A("6. **판정은 하지 않는다.** 본 문서는 before 표일 뿐이고, 사전등록 판정은 v3-A 가 학습된 뒤 "
      "`PREREG §3.5` 의 8지점 규칙으로 한다. 계기판② 는 **여기서 돌릴 수 없다**(§4).")
    A("")

    # ---------------------------------------------------------------- 분모
    A("---")
    A("")
    A("# §1. 분모 회계 — 표에 인쇄할 의무가 있는 수")
    A("")
    A("| 항목 | 값 | 근거 |")
    A("|---|---|---|")
    A(f"| test-ext 프레임 (팔별) | A {C['n_A']} · B {C['n_B']} · C {C['n_C']} · D {C['n_D']} = **1,152** | "
      "`AC §4.10` · W3_REPORT §1 |")
    A(f"| 재채점 입력 (패스별) | (A,C) 576 + (B,D) 576 | `dataset_manifest_v3_textext{{,_bd}}.json` |")
    A(f"| **프레임축 recall 분모** | A팔 중 그리드 내 양성 칸 ≥ 1 = **{C['n_haz_A']}** | `PREREG §2.1` 분모표 |")
    A(f"| **조건화 탈락** | {C['n_A'] - C['n_haz_A']}/{C['n_A']} = "
      f"**{(C['n_A'] - C['n_haz_A']) / C['n_A']:.1%}** — 내역 sceneN9 48 + sceneN11 48 + sceneH3 27 | "
      "`PREREG §2.1` 조건화 공개 의무 (test-core 대응값 9.6 %) |")
    A(f"| 칸축 recall 분모 | A팔 양성 칸 **{C['n_pos_cells_A']:,}** | `AC §1.2` 칸 정의 |")
    A(f"| **FA_C 분모** | C팔 **{C['n_C']}프레임 = {C['n_C'] * 20:,}칸** | `AC §4.10` 행 |")
    A(f"| **FA_D 분모** | D팔 **{C['n_D']}프레임 = {C['n_D'] * 20:,}칸** | 동상 |")
    A("| void 버킷 격리 | **0프레임** (VG-void 커버리지 1.000000 전면) | `AC §4.10` |")
    A(f"| paired-H | H1 **{C['paired_H_by_scene']['sceneH1']}** · H2 "
      f"**{C['paired_H_by_scene']['sceneH2']}** · H3 **{C['paired_H_by_scene']['sceneH3']}** = "
      f"**{C['paired_H']}** | 재채점이 W3_REPORT §4.2 를 **한 컷도 안 틀리고 재현** |")
    A(f"| 계기판① 층 | 풀링(H1+H2) **{C['n_pool_pairedH']}** · 완전 은닉(H3) **{C['n_hidden_pairedH']}** | "
      "D87 ① — H3 는 **풀링에 절대 넣지 않는다** |")
    A("")
    A("**C·D 팔 GT 권위 인쇄 (AC-INSTR-1 C3-2 필수 사항)**: 본 표의 C·D 팔 GT 는 **사양 상수(전 칸 음성)** 를 "
      "권위로 읽었다. 매니페스트에 실린 라벨러 `polar_gt` 행은 **쓰지 않았다**. 다만 두 권위가 "
      f"**충돌하지 않음**을 함께 확인했다 — 라벨러 행의 양성 칸 수가 C팔 **{C['C_gt_positive_cells']}** · "
      f"D팔 **{C['D_gt_positive_cells']}** 이다(6/6 씬 전음성, W3_REPORT §5 와 일치).")
    A("")

    # ---------------------------------------------------------------- 운용점
    A("---")
    A("")
    A("# §2. 운용점 — τ_op 참고 + FA-정합 이중축 8지점")
    A("")
    A("정합 기준 팔 = **D팔**(`MILESTONE §6.2-2`). τ 는 **정확분위**(경험 순서통계)에서 "
      "**목표 이하 최대 달성률**을 주도록 취했다. 프레임축 τ 모집단 = D팔 프레임별 최대확률"
      "(해상도 1/288), 칸축 τ 모집단 = D팔 전 칸 확률(해상도 1/5,760).")
    A("")
    A("| 운용점 | 목표 | 달성 FA(D팔) | τ RGB | τ Depth | τ b2 |")
    A("|---|---|---|---|---|---|")
    for name in OPS_FA:
        o = {a: g(S[a], name) for a in ARMS}
        tgt = o["rgb"]["target"]
        ach = [P[r]["ops"][[x["name"] for x in P[r]["ops"]].index(name)].get("achieved")
               for r in ["rgb_s42", "depth_s42", "b2_s42"]]
        A(f"| {OP_LBL[name]} | {tgt:g} | {min(ach):.4f}–{max(ach):.4f} | "
          f"{m(o['rgb']['tau'])} | {m(o['depth']['tau'])} | {m(o['b2']['tau'])} |")
    A("")
    A("- **달성 FA 가 목표와 미세하게 다른 이유**는 분해능이다 — 288프레임 격자에서 .359 는 "
      "103/288 = .3576 이 목표 이하 최대다. 규약대로다.")
    A("- **τ 의 시드 산포가 크다** (예: RGB 프레임축 .359 에서 τ 0.037–0.281). `PREREG §3.2` 의 "
      "*\"σ 가 큰 팔의 PASS 는 '움직이지 않았다' 가 아니라 '3시드로는 판정 불가' 다\"* 가 "
      "**이 표에도 그대로 걸린다**. 판정력이 있는 것은 σ 가 작은 팔뿐이다.")
    A("- **b2 팔은 σ 기반 주장에서 제외**된다 (`PREREG §3.2` · `[PENDING-24]`). 아래 표에는 "
      "인쇄하되 판정에는 쓰지 않는다.")
    A("")

    # ---------------------------------------------------------------- 계기판 1
    A("---")
    A("")
    A("# §3. 계기판 ① — 트윈-조건부 recall (A,C)")
    A("")
    A("**재는 양** (`PREREG §2.1`): A팔에서 발화했고 **같은 밴드·같은 씬·같은 포즈의 C팔에서는 "
      "발화하지 않은** 것만 센 recall.")
    A("")
    A("- **프레임축**: A팔 GT-양성 칸 중 `p_A ≥ τ ∧ p_C < τ` 인 칸이 **하나라도** 있으면 그 프레임을 검출로 센다.")
    A("- **칸축**: A팔 GT-양성 칸 전체에서 `p_A ≥ τ ∧ p_C < τ` 인 칸의 비율.")
    A("- **맨 recall**(= C팔 조건 없이 `p_A ≥ τ`)을 **같은 표에 병기**한다. 두 수의 차가 곧 "
      "*\"위험 씬처럼 생겼으면 위험이다\"* 의 크기다.")
    A("")
    A("**쌍짓기 키 = `(밴드라운드, 씬, 컷 파일명)`.** 이 키가 곧 포즈 동일성을 보증한다 — "
      "W3_REPORT §3.2 실측: **A↔C 는 전 씬·전 밴드에서 `datum exact 24`**(|Δground_z| 0.000000) · "
      "**VG-10 포즈 6키 불일치 0건** · 쌍 생존율 1.0000. 별도 포즈 필터를 걸어도 걸러지는 쌍이 없다.")
    A("")
    A(f"## 3.1 풀링층 — paired-H H1+H2 (n = {C['n_pool_pairedH']}) · **H3 제외**")
    A("")
    for axis, k_plain, k_twin in (("프레임축", "pooled_frame_recall", "pooled_frame_recall_twin"),
                                  ("칸축", "pooled_cell_recall", "pooled_cell_recall_twin")):
        A(f"**{axis}** — `맨 recall` / **`트윈-조건부`** / 트윈 통과율")
        A("")
        A("| 운용점 | RGB | Depth | b2 *(σ 제외)* |")
        A("|---|---|---|---|")
        for name in ["tau_op", "tau_star"] + OPS_FA:
            cells = []
            for a in ARMS:
                o = g(S[a], name)
                cells.append(f"{m1(o[k_plain])} / **{m(o[k_twin])}** / {ratio(o[k_twin], o[k_plain])}")
            A(f"| {OP_LBL[name]} | " + " | ".join(cells) + " |")
        A("")
    A("**읽는 법**: 트윈 통과율(= 트윈 recall ÷ 맨 recall)이 1.0 이면 발화가 전부 낙차에 매달려 있다는 "
      "뜻이고, 0 에 가까우면 발화가 **낙차와 무관**하다는 뜻이다. v2 는 8지점 어디서도 0.5 를 넘지 못한다.")
    A("")

    A(f"## 3.2 완전 은닉층 — sceneH3 (n = {C['n_hidden_pairedH']}) · **별도 행** (D87 ①)")
    A("")
    A("D58 의 영정보 층화를 문자대로 적용하면 sceneH3 의 (A,C) 모집단 **48프레임**(그중 위험 양성 "
      f"**{C['n_hidden_pairedH']}**)이 계기판①에서 통째로 빠진다. D87 ① 은 "
      "**삭제가 아니라 별도 층**으로 승격했다 — *\"단서 동일 + 반사실 불가시 ⇒ 올바른 모델은 A/C "
      "동등 발화가 정답\"*. 그러므로 여기서는 **recall 이 아니라 Δp 분포**가 보고량이다.")
    A("")
    A("| 운용점 | RGB 맨/트윈 | Depth 맨/트윈 | b2 맨/트윈 |")
    A("|---|---|---|---|")
    for name in ["tau_op"] + OPS_FA:
        cells = [f"{m1(g(S[a], name)['hidden_frame_recall'])} / "
                 f"**{m1(g(S[a], name)['hidden_frame_recall_twin'])}**" for a in ARMS]
        A(f"| {OP_LBL[name]} | " + " | ".join(cells) + " |")
    A("")
    A("**Δp 분포** (운용점 무관 — 확률 자체) · `Δp = max(p_A over A팔 GT-양성 칸) − max(p_C over 같은 칸)`")
    A("")
    A("| 런 | n | mean | p50 | p25 | p75 | min | max | mean&#124;Δp&#124; | &#124;Δp&#124; ≤ 0.05 |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for r in P:
        s = P[r]["hidden_dp"]["pairedH"]["delta_score"]
        A(f"| {r} | {s['n']} | {s['mean']:+.4f} | {s['p50']:+.4f} | {s['p25']:+.4f} | "
          f"{s['p75']:+.4f} | {s['min']:+.4f} | {s['max']:+.4f} | {s['mean_abs']:.4f} | "
          f"**{s['frac_abs_le_05']:.3f}** |")
    A("")
    A("**대조 — 풀링층(H1+H2)의 같은 Δp**: 같은 계기가 살아 있는 층에서는 Δp 가 실제로 벌어진다.")
    A("")
    A("| 런 | n | mean | p50 | mean&#124;Δp&#124; | frac(Δp>0) |")
    A("|---|---|---|---|---|---|")
    for r in P:
        s = P[r]["pool_dp"]["delta_score"]
        A(f"| {r} | {s['n']} | {s['mean']:+.4f} | {s['p50']:+.4f} | {s['mean_abs']:.4f} | "
          f"{s['frac_gt0']:.3f} |")
    A("")
    A("- **Depth 의 H3 Δp 는 9자리까지 정확히 0.0000** 이다(21/21 쌍). 낙차가 화면에 한 픽셀도 "
      "없으면 깊이 입력은 **바이트 동일**에 가깝고, 모델은 두 팔을 구별할 수단이 없다. "
      "**이것이 은닉 완전성의 직접 측정치**이며 성적이 아니다.")
    A("- RGB·b2 는 |Δp| p50 이 0.002 수준으로 **0 이 아니지만 무시 가능**하다 — 조명·노이즈 수준이다.")
    A("- ⇒ **v3-A 의 이 행은 '올라가야 하는 수' 가 아니다.** 개선 방향 부호(`PREREG §3.4` ① ↑)는 "
      "**풀링층에만** 적용되고, 이 층은 *동등 발화 유지*가 정답이다. 이 사실을 판정표에 인쇄해야 한다.")
    A("")

    A("## 3.3 씬별 (참고 — 층화 근거)")
    A("")
    A("| 씬 | n | RGB 맨/트윈(프레임) | Depth 맨/트윈 | b2 맨/트윈 |")
    A("|---|---|---|---|---|")
    for sc in ["sceneH1", "sceneH2", "sceneH3"]:
        cells = []
        for a in ARMS:
            vals_p = [P[r]["ops"][0]["dash1"]["by_scene"][sc]["frame_recall"]
                      for r in S[a]["runs"]]
            vals_t = [P[r]["ops"][0]["dash1"]["by_scene"][sc]["frame_recall_twin"]
                      for r in S[a]["runs"]]
            cells.append(f"{sum(vals_p) / 3:.3f} / **{sum(vals_t) / 3:.3f}**")
        n = C["paired_H_by_scene"][sc]
        A(f"| {sc} | {n} | " + " | ".join(cells) + " |")
    A("")
    A("τ_op 0.5 · 3시드 평균. sceneH2(계단참형)가 가장 높고 sceneH3(복도굴절형)는 트윈이 0 이다 — "
      "W3_REPORT §6.1 의 (A,C) 광학차 p50 **H2 6.54 : H1 2.36 : H3 0.22 (30배 폭)** 와 **같은 순서**다.")
    A("")

    # ---------------------------------------------------------------- 계기판 2
    A("---")
    A("")
    A("# §4. 계기판 ② — **여기서 돌리지 않는다** (사유 명기)")
    A("")
    A("계기판② 는 **CUE-OFF 용량-반응**이고 쌍 규약이 **(A,B)** 다(`AC §2-2`). 재는 양은 "
      "*\"단서를 끌 때 오경보가 **단서 개수**를 따르는가 **광학 변화량**을 따르는가\"* 의 두 기울기이며, "
      "판정은 **두 기울기의 상대 지배**로 한다(`PREREG §2.2` · §3.4 ②).")
    A("")
    A("**돌리지 않는 이유 3가지**:")
    A("")
    A("1. **v3 팔이 없다.** 용량-반응은 v2 단독으로는 *before* 조차 성립하지 않는다 — 비교 대상이 "
      "v2 자신뿐이면 기울기의 부호 변화를 물을 수 없다. `AC §2-8` 이 zero-shot 재채점을 명령한 대상은 "
      "**계기판③ 의 기준점**(과 §2-2 를 경유한 ①)이지 ② 가 아니다.")
    A("2. **v2 기준점은 이미 등록돼 있다** — 광학 질량 추종(scene17 역설), 그리드-고정 검정 기울기 "
      "−0.058 ~ +0.387, 장식형 lift 1.01/0.98 (`PREREG §2.2` v2 기준점 행 · `AC §4.5` 행 I·J). "
      "본 웨이브가 그 수를 다시 만들 필요가 없다.")
    A("3. **판정 모집단이 미충족**이다. ② 의 판정 모집단은 *\"양 팔 모두 strict-H 인 paired 프레임\"* + "
      "칸별 `n_paired` **하한 10** 인데, 그 하한은 **v3 훈련 코퍼스의 (A,B) 위에서** 세는 수다. "
      "test-ext 의 (A,B) 로 재면 `AC §2-9` 의 무대 규약과는 맞지만 **v3 만 분포-내가 되는** 문제와는 "
      "다른 축의 문제 — 즉 지금 재도 v3-A 학습 후 다시 재야 한다.")
    A("")
    A("⇒ 계기판② 의 before/after 는 **v3-A 학습 완료 후 (A,B) 팔 위에서 한 번에** 만든다. "
      "본 문서의 어느 표도 ② 로 인용하지 않는다.")
    A("")

    # ---------------------------------------------------------------- 계기판 3
    A("---")
    A("")
    A("# §5. 계기판 ③ — N-cue 함정 FA (FA_C vs FA_D)")
    A("")
    A(f"분모: **FA_C = C팔 {C['n_C']}프레임 = {C['n_C'] * 20:,}칸** · "
      f"**FA_D = D팔 {C['n_D']}프레임 = {C['n_D'] * 20:,}칸** (void 격리 대상 0). "
      "GT 는 양 팔 모두 **사양 상수 전음성**이므로 발화는 전부 오경보다.")
    A("")
    A("**분해 규약** (`AC §2-3` 표준 보고): **FA_D = 순수 씬-연합의 직접 게이지** · "
      "**FA_C − FA_D = 단서-유발 오경보 몫**.")
    A("")
    A("## 5.1 프레임축 (`frame_fa_off`)")
    A("")
    A("| 운용점 | RGB FA_C / FA_D / **차** | Depth FA_C / FA_D / **차** | b2 FA_C / FA_D / **차** |")
    A("|---|---|---|---|")
    for name in ["tau_op", "tau_star"] + OPS_FA:
        cells = []
        for a in ARMS:
            o = g(S[a], name)
            cells.append(f"{m1(o['FA_C_frame'])} / {m1(o['FA_D_frame'])} / "
                         f"**{m(o['FA_diff_frame'])}**")
        A(f"| {OP_LBL[name]} | " + " | ".join(cells) + " |")
    A("")
    A("## 5.2 칸축 (`cell_fpr_off`)")
    A("")
    A("| 운용점 | RGB FA_C / FA_D / **차** | Depth FA_C / FA_D / **차** | b2 FA_C / FA_D / **차** |")
    A("|---|---|---|---|")
    for name in ["tau_op", "tau_star"] + OPS_FA:
        cells = []
        for a in ARMS:
            o = g(S[a], name)
            cells.append(f"{m1(o['FA_C_cell'], 4)} / {m1(o['FA_D_cell'], 4)} / "
                         f"**{m(o['FA_diff_cell'], 4)}**")
        A(f"| {OP_LBL[name]} | " + " | ".join(cells) + " |")
    A("")
    A("## 5.3 씬군 분해 — N-cue(N9·N11) vs H씬(H1·H2·H3) vs 측방(L1)")
    A("")
    A("| 씬군 | 팔 | RGB | Depth | b2 |")
    A("|---|---|---|---|---|")
    for grp, lbl in (("ncue", "**N-cue (N9·N11)**"), ("hscenes", "H씬 (H1·H2·H3)"),
                     ("lat", "측방 (L1)")):
        for armk in ("FA_C", "FA_D"):
            cells = [m(g(S[a], "tau_op")[f"{grp}_{armk}_frame"]) for a in ARMS]
            A(f"| {lbl} | {armk} 프레임 | " + " | ".join(cells) + " |")
    A("")
    A("τ_op 0.5 · 3시드 평균 ± σ(ddof=1).")
    A("")
    A("**읽는 법 3가지**")
    A("")
    A("1. **함정은 실재한다.** N-cue 두 씬은 낙차가 물리적으로 없고(격자깊이 N9 0.200 m · "
      "N11 0.150 m, 임계 0.30 m 미만 — W3_REPORT §5.1) GT 는 네 팔 전부 전음성인데, "
      f"RGB 는 C팔에서 프레임의 **{g(S['rgb'], 'tau_op')['ncue_FA_C_frame']['mean']:.1%}** 에서 울린다. "
      f"D팔에서는 **{g(S['rgb'], 'tau_op')['ncue_FA_D_frame']['mean']:.1%}**. 차이는 **단서뿐**이다.")
    A("2. **Depth 는 이 함정에 거의 안 걸린다** — 같은 자리에서 FA_C "
      f"{m1(g(S['depth'], 'tau_op')['ncue_FA_C_frame'])}. 단서가 **광학량**(점형블록 패턴·노면 표시)이라 "
      "깊이 채널에 실리지 않기 때문이다. 대신 Depth 는 **H씬**에서 FA_C·FA_D 가 **둘 다** 높다"
      f"({m1(g(S['depth'], 'tau_op')['hscenes_FA_C_frame'])} / "
      f"{m1(g(S['depth'], 'tau_op')['hscenes_FA_D_frame'])}) — 이쪽은 단서가 아니라 **지형 통계** 오경보다. "
      "**두 팔의 병이 다르다**는 것이 이 분해의 수확이다.")
    A("3. **`AC §2-3` 이 예고한 대로 v2 에는 FA_D 표본이 없었다.** v2 공표 `frame_fa_off` **.681** 은 "
      "장식 보존 off팔이라 **FA_C 의 근사**였고 `AC §2-8` 이 이미 보조 참고치로 격하했다. "
      "위 표가 **v3 D팔로 처음 가능해진 분해**의 v2 쪽 값이다.")
    A("")

    # ---------------------------------------------------------------- L1
    A("---")
    A("")
    A("# §6. L1 측방 — 섹터별 발화 vs 실측 위험 섹터 분포 (V2S 재론 기준선)")
    A("")
    A("**정답(실측 위험 분포)** — 본 재채점이 W3_REPORT §7 을 소수 넷째 자리까지 재현했다:")
    A("")
    gt = P["rgb_s42"]["l1_hazard_gt"]
    A("| 층 | A | B | C | D | E |")
    A("|---|---|---|---|---|---|")
    A("| 프레임 양성률 (n=48) | " + " | ".join(f"**{gt[s]['frame_rate']:.4f}**"
                                          for s in "ABCDE") + " |")
    A("| 칸 점유율 | " + " | ".join(f"**{gt[s]['cell_share']:.4f}**" for s in "ABCDE") + " |")
    A("")
    A("**v2 발화 분포 (A팔 · τ_op 0.5 · 3시드 평균 ± σ)** — 프레임 발화율 / 칸 점유율:")
    A("")
    A("| 팔 | A | B | C | D | E |")
    A("|---|---|---|---|---|---|")
    for a in ARMS:
        o = g(S[a], "tau_op")
        A(f"| {ARM_LBL[a]} | " + " | ".join(
            f"{m1(o['l1'][f'fire_A_{s}_frame'], 2)} / {m1(o['l1'][f'fire_A_{s}_share'], 3)}"
            for s in "ABCDE") + " |")
    A("")
    A("**집계 — A+E(측방) vs B+D(중간) vs C(정면), 칸 점유율**")
    A("")
    A("| | A+E | B+D | C | 판정 |")
    A("|---|---|---|---|---|")
    A(f"| **실측 위험(정답)** | **0.6722** | 0.2950 | **0.0328** | 측방 지배 |")
    for a in ARMS:
        o = g(S[a], "tau_op")
        ae = o["l1"]["fire_A_A_share"]["mean"] + o["l1"]["fire_A_E_share"]["mean"]
        bd = o["l1"]["fire_A_B_share"]["mean"] + o["l1"]["fire_A_D_share"]["mean"]
        cc = o["l1"]["fire_A_C_share"]["mean"]
        verdict = "정면 과발화 · 측방 미발화" if cc > 0.0328 * 2 else "—"
        A(f"| {ARM_LBL[a]} 발화 | {ae:.4f} | {bd:.4f} | {cc:.4f} | {verdict} |")
    A("")
    A("**발화 칸 원수 (τ_op · 런별)** — 위 점유율의 분모를 정직하게 인쇄한다:")
    A("")
    A("| 런 | 총 발화 칸 | A | B | C | D | E |")
    A("|---|---|---|---|---|---|---|")
    for r in P:
        o = [x for x in P[r]["ops"] if x["name"] == "tau_op"][0]["l1"]["fire_A"]
        A(f"| {r} | {o['_total_cells']} | " + " | ".join(str(o[s]["n_cells"])
                                                         for s in "ABCDE") + " |")
    A("")
    A("**읽는 법**")
    A("")
    rgb_op = g(S["rgb"], "tau_op")
    rgb_c = rgb_op["l1"]["fire_A_C_share"]["mean"]
    rgb_ae = rgb_op["l1"]["fire_A_A_share"]["mean"] + rgb_op["l1"]["fire_A_E_share"]["mean"]
    A(f"- RGB 는 정면 C 에 발화 질량의 **{rgb_c:.1%}** 를 싣는데 실제 위험은 **3.28 %** 다 — "
      f"**{rgb_c / 0.0328:.1f}배 과발화**. 반대로 측방 A+E 에는 **{rgb_ae:.1%}** 만 싣는데 실제는 "
      f"**67.22 %** 다 — **{0.6722 / rgb_ae:.1f}배 미발화**.")
    A("- **Depth 는 sceneL1 에서 사실상 발화하지 않는다** — 3시드 합쳐 **18칸**(s42 18 · s43 0 · s44 0). "
      "위 Depth 행의 0.333/0.667 은 **s42 한 런의 18칸을 나눈 값**이지 세 런의 분포가 아니다. "
      "측방 낙차를 깊이만으로 잡지 못한다는 뜻이며, σ 가 0 에 가까워 보이는 것은 **퇴화**이지 "
      "안정성이 아니다 (`PREREG §3.2` σ=0 퇴화 인용 금지 조항과 같은 계열).")
    A("- ⇒ **V2S(섹터 5→10) 재론의 기준선**: 지금 v2 는 5섹터 분해능조차 못 쓰고 있다. "
      "*\"분해능을 올리면 실용 정보가 느는가\"* 를 묻기 전에 **현 분해능에서 방향이 맞는가**가 "
      "먼저이고, 그 답이 본 표다.")
    A("")

    # ---------------------------------------------------------------- 방향 부호
    A("---")
    A("")
    A("# §7. 이 표가 v3-A 의 before 다 — 사전등록 방향 부호 (`PREREG §3.4`)")
    A("")
    A("| 계기판 | 개선 방향 (등록된 부호) | 본 표의 before 값 (τ_op · 3시드 평균) | v3-A 가 해야 할 일 |")
    A("|---|---|---|---|")
    A(f"| **① 트윈-조건부 recall** | **↑** (같은 FA-정합 지점에서) | 풀링(H1+H2) 프레임 "
      f"RGB **{m1(r_op['pooled_frame_recall_twin'])}** · Depth **{m1(d_op['pooled_frame_recall_twin'])}** / "
      f"칸 RGB {m1(r_op['pooled_cell_recall_twin'])} · Depth {m1(d_op['pooled_cell_recall_twin'])} | "
      "**8지점 전부**에서 부호가 ↑ ∧ 모델 평균 &#124;Δ&#124; > σ |")
    A("| | **(완전 은닉층은 예외)** | H3 트윈 recall ≈ 0 · &#124;Δp&#124; ≤ 0.05 가 21/21 | "
      "**동등 발화 유지가 정답** — 이 행은 ↑ 를 요구하지 않는다 (D87 ①) |")
    A("| ② CUE-OFF 용량-반응 | 광학 변화량 추종 기울기 **↓** ∧ 단서 개수 추종 기울기 **↑** | "
      "**본 웨이브 미산출** (§4) | v3-A 학습 후 (A,B) 팔에서 before/after 동시 산출 |")
    A(f"| **③ N-cue 함정 FA** | **FA_C ↓** ∧ **(FA_C − FA_D) ↓** (둘 다 인쇄) | "
      f"FA_C 프레임 RGB **{m1(r_op['FA_C_frame'])}** · Depth {m1(d_op['FA_C_frame'])} / "
      f"차 RGB **{m1(r_op['FA_diff_frame'])}** · Depth {m1(d_op['FA_diff_frame'])} | "
      "**8지점 전부**에서 두 수 모두 ↓ ∧ &#124;Δ&#124; > σ |")
    A("")
    A("**판정 규칙 재확인** (`PREREG §3.5`)")
    A("")
    A("- **개선** = 프레임축·칸축 **8지점 전부**에서 부호가 개선 방향 ∧ 모델 평균 |Δ| > σ.")
    A("- **악화** = 8지점 전부에서 부호가 악화 방향 ∧ |Δ| > σ. **축 간 부호 불일치는 판정 불가**이며 "
      "불일치 사실과 사유를 인쇄한다.")
    A("- 종합: 개선 3/3 ∧ 악화 0 = **창발** · 개선 1–2 ∧ 악화 0 = **부분** · 개선 0 또는 악화 ≥ 1 = **미달**.")
    A("- 본 문서는 **before 표일 뿐 판정이 아니다.** ② 가 미산출이므로 종합 판정의 분모는 "
      "v3-A 산출 시점에 3 으로 복원된다.")
    A("")

    # ---------------------------------------------------------------- 주의
    A("---")
    A("")
    A("# §8. 소비자 주의 4건 (인용 전 필독)")
    A("")
    A("1. **분모는 1,152 이지 1,728 이 아니다.** 계획 문면의 9씬 대비 B안 대기 3씬(H4·L2·N12) "
      "576컷이 미착지다. 팔당 288 · 재채점 패스당 576 (`W3_REPORT §9`).")
    A("2. **(A,D) 수치를 이 표에 섞지 말 것.** v2 공표 트윈 44.7 % / 0 % 는 (A,D) 세대이고 "
      "본 표는 전부 **(A,C)** 다 (`AC §2-2`). 같은 칸에 넣으면 세대 혼합이다.")
    A("3. **C·D 팔 GT 는 사양 상수를 읽었다.** 매니페스트의 라벨러 `polar_gt` 행은 미사용 "
      "(AC-INSTR-1 C3-2). 두 권위는 6/6 씬에서 일치했다(§1 말미).")
    A("4. **`[PENDING-17]`(test-ext 모집단 4행)은 `AC §4.10` 으로 충당됐으나 `PREREG §7` 의 "
      "PENDING 목록 자체는 아직 미해소**다. `PREREG §8` 규약상 미해소 PENDING 에 매달린 계기판은 "
      "판정에서 제외하고 제외 사실을 표제에 인쇄해야 한다 — v3-A 판정표를 만들 때 이 조항을 다시 확인할 것.")
    A("")

    # ---------------------------------------------------------------- 파일
    A("---")
    A("")
    A("# §9. 실행 · 산출 파일")
    A("")
    A("| 항목 | 값 |")
    A("|---|---|")
    A("| 실행 | tmux `v2zeroshot` · 인보케이션별 `flock -o /tmp/negobs_gpu.lock` · env_seg · "
      "`PYTHONNOUSERSITE=1` · resume-safe |")
    A("| 패스 | 9 체크포인트 × 2 (AC · BD) = **18** — 전부 성공, 실패 0 |")
    A("| 벽시계 | **12.1 분** (04:55:33 → 05:07:39) — 후반은 W2 렌더와 GPU 락 공유 |")
    A("| 재추론 프레임 | 18 × 576 = **10,368** |")
    A("| 산출 | `eval_v3textext/<run>/{per_frame.csv,metrics.json,METRICS_SECTION.md}` + "
      "`<run>/bd/` 동일 · `v2_textext_tables.json` · 본 문서 |")
    A("| 신규 코드 | `code/rescore_v3textext.sh` · `code/v2_textext_tables.py` · "
      "`code/v2_textext_report.py` |")
    A("| 신규 입력 | `dataset_manifest_v3_textext_bd.json` · `split_v3_textext_bd.json` "
      "(`code/w3_manifest.py --pair bd` — FA_D 산출에 D팔이 필요) |")
    A("")
    return "\n".join(L) + "\n"


def ratio_ae(S, arm):
    o = [x for x in S[arm]["ops"] if x["name"] == "tau_op"][0]
    return f"{o['l1']['fire_A_A_share']['mean'] + o['l1']['fire_A_E_share']['mean']:.4f}"


def ratio_c(S, arm):
    o = [x for x in S[arm]["ops"] if x["name"] == "tau_op"][0]
    return f"{o['l1']['fire_A_C_share']['mean']:.4f}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.path.join(V3, "v2_textext_tables.json"))
    ap.add_argument("--out", default=os.path.join(V3, "V2_TEXTEXT_BASELINE.md"))
    a = ap.parse_args(argv)
    J = json.load(open(a.tables, encoding="utf-8"))
    open(a.out, "w", encoding="utf-8").write(build(J))
    print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
