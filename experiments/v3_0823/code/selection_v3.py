#!/usr/bin/env python3
"""
selection_v3.py — P-4 체크포인트 선택식 수리: **단일 정본 구현**.

이 파일이 ACCOUNTING §4.3-3 (결함 ③ "선택지표 분모 이중 정의")의 처방이다.
분모 정의 · 게이트 · 점수식이 **전부 이 파일 한 곳에만** 존재하며,
train_polar.py / 재선택 스크립트 / v3 학습 루프는 모두 여기를 import 한다.

원본(수리 대상):
  experiments/mainrun_0819/code/train_polar.py
    :158-161  is_strict_h()        <- 정의 A (toggle_state != "off" 요구)
    :235-244  h_frame_recall()     <- 정의 B (토글 검사 없음)   ** 이중 정의 **
    :268-272  selection_score()    <- 0.5*f1 + 0.5*h_recall     ** 유도 근거 없음 **
    :413/:435 호출부 / `if sel > best` (동률 시 이른 에폭)

본 파일은 train_polar.py를 수정하지 않는다(P-4 규칙). 대체 구현이며,
채택은 P4_SELECTION.md 결재란 승인 후.
"""
from __future__ import annotations

import json
import math
from typing import Iterable, Sequence

# ---------------------------------------------------------------------------
# §A  단일 분모 정의  (결함 ③의 정본 처방)
# ---------------------------------------------------------------------------
# 등록 규칙 (ACCOUNTING §3 append 대상):
#   hazard-H 프레임  :=  tier == "H"  AND  polar_gt 에 양성 칸이 1개 이상
#
# 왜 toggle_state 절을 뺐나:
#   * v2 실측에서 두 정의는 **전 split · 두 매니페스트 모두 완전 일치**한다
#     (train 141/93 · val 6 · test 96, 발산 0건 — reselect_p4.py 가 매 실행마다 재검산).
#     즉 toggle_state 절은 v2에서 **중복 조건**이었고, 결함 ③은 잠복 결함이었다.
#   * v3 코퍼스는 팔이 4개(A/B/C/D)라 toggle_state 가 더 이상 2치가 아니다.
#     B팔(위험 O · 단서 X)은 위험을 갖고도 토글 이름이 "off" 계열로 붙을 수 있다
#     → 정의 A를 그대로 물려받으면 **v3에서 진짜 H 프레임이 분모에서 탈락**한다.
#   * C·D팔은 "전 칸 음성"이 사양(V3_DESIGN §4.1)이므로 polar_gt.any() 절 하나로
#     이미 배제된다. 따라서 최소·일반화 가능한 정의는 B다.
#
# 안전장치: 두 정의가 갈라지면 조용히 한쪽을 고르지 않고 **하드 실패**시킨다.

H_DEF_ID = "hazard_H_v3:  tier=='H' and any(polar_gt)"


# RT-B 재판정 (redteam/RT_LEDGER_B.md:340-350): 두 정의가 v2에서 일치하는 **기전**은
#   labeler.py:527-528 `if arm == "off": t_strict = "off"` — off팔 프레임의 tier가 강제로
#   "off"로 덮이므로 tier=="H" ∧ toggle_state=="off" 는 출하 라벨에서 성립 불가능하다.
#   따라서 `N-3`은 **현재 결함이 아니라 문서 정리 대상**으로 강등됐고, 진짜 위험은 §D로 이동했다.


def is_hazard_h(rec: dict) -> bool:
    """정본 정의(레코드 수준). 분모·분자 어디서든 **이 함수만** 쓴다.
    무시 마스크가 있는 코퍼스에서는 이 함수 대신 §D의 h_frame_recall_selection 을 쓴다
    (마스크는 레코드가 아니라 칸 단위이므로)."""
    return rec.get("tier") == "H" and any(int(v) for v in rec["polar_gt"])


def _is_hazard_h_legacy_A(rec: dict) -> bool:
    """train_polar.py:158-161 is_strict_h — 대조용(직접 사용 금지)."""
    return (rec.get("tier") == "H" and rec.get("toggle_state") != "off"
            and any(int(v) for v in rec["polar_gt"]))


def count_hazard_h(records: Iterable[dict], *, strict: bool = True) -> tuple[int, int]:
    """(n_H, 정의 A와의 발산 건수). strict=True면 발산 시 AssertionError."""
    recs = list(records)
    n_new = sum(1 for r in recs if is_hazard_h(r))
    n_old = sum(1 for r in recs if _is_hazard_h_legacy_A(r))
    div = n_new - n_old
    if strict and div != 0:
        raise AssertionError(
            f"[VG-denom] H 분모 이중 정의 발산 {div}건 (B={n_new} vs A={n_old}). "
            "두 정의가 갈라지는 코퍼스다 — 조용히 진행 금지, ACCOUNTING 등재 후 재개.")
    return n_new, div


# ---------------------------------------------------------------------------
# §B  게이트 VG-const — 상수출력 거부
# ---------------------------------------------------------------------------
# 통계량: **val 전 프레임(288)** 에서의 프레임별 최대확률의 분포 폭
#         spread = max_f (max_c p_fc) - min_f (max_c p_fc)
#   ASSUMPTION_LEDGER MOD-07 / FA_MATCHED.md:99-111 이 기록한 붕괴 서명과 같은 통계량이다.
#
# 왜 '위험-없는 팔'이 아니라 'val 전체'인가 — 실측이 정한다:
#   대장은 이 통계량을 test **off팔**에서 쟀다. 그 무대를 val 로 그대로 옮기면
#   **정상 모델이 게이트에 걸릴 뻔한다**: depth_s43 의 val off팔 spread = 1.418e-02
#   (임계의 1.4배)이다 — off팔은 전부 음성이라 '잘 학습된 모델일수록 출력이 균일'해지는
#   퇴화 무대이기 때문이다. 같은 체크포인트의 val 전체 spread 는 1.000 이다.
#   위험 프레임과 무위험 프레임이 **섞인** 모집단에서는 비퇴화 모델이 반드시 변해야 하므로
#   val 전체가 옳은 무대다. (실측 원장: logs/p4_reselect.json::gate)
#
# 임계값 유도 (v2 실측만 사용, 임의 상수 아님) — val 전체 기준:
#   붕괴 실측 최대   : convnext_tiny_s43  1.92e-04   (s42 6.60e-05)
#   비붕괴 실측 최소 : convnext_tiny_s44  3.478e-01  (resnet34/50/b2 0.940~1.000)
#   → 로그축 중점 sqrt(1.92e-4 * 3.478e-1) = 8.17e-03  → **1e-2 로 반올림 등재**
#   여유: 최악 붕괴의 52배 위 · 최선 분리의 35배 아래 (로그축 대칭)
VGCONST_SPREAD_MIN = 1e-2
VGCONST_STAGE = "val_all_frames"
VGCONST_SOURCE = ("experiments/weekend_0823/newmodels/FA_MATCHED.md:99-111 (test off팔 9런) + "
              "experiments/v3_0823/logs/p4_reselect.json::gate (val 무대 15런 재실측)")


def output_spread(prob_rows: Sequence[Sequence[float]]) -> float:
    """프레임별 최대확률의 (max - min). prob_rows = [프레임][칸] 확률."""
    if not prob_rows:
        return float("nan")
    per_frame_max = [max(r) for r in prob_rows]
    return float(max(per_frame_max) - min(per_frame_max))


def vgconst_pass(spread: float) -> bool:
    """True = 통과(상수출력 아님)."""
    return bool(math.isfinite(spread) and spread >= VGCONST_SPREAD_MIN)


# VG-const-p — 소급 적용 가능한 **대리 게이트** (metrics.csv 만으로 판정).
#   τ 고정 하에서 near-constant 출력은 전 칸이 τ의 한쪽에만 놓이므로
#   결정 수준에서 '전무발화'(f1=0) 또는 '전부발화'(recall=fpr=1)로 나타난다.
#   VG-const 의 필요조건이지 충분조건은 아니다 — 리포트에서 그렇게 표기할 것.
def vgconstp_pass(val_f1: float, val_recall: float, val_fpr: float, eps: float = 1e-3) -> bool:
    if val_f1 <= eps:                                   # 전무발화
        return False
    if val_recall >= 1 - eps and val_fpr >= 1 - eps:    # 전부발화
        return False
    return True


# ---------------------------------------------------------------------------
# §C  점수식
# ---------------------------------------------------------------------------
# 구식 (train_polar.py:268-272) — 대조용
def sel_score_v2(f1: float, h_recall: float | None) -> tuple[float, bool]:
    if h_recall is None or not math.isfinite(h_recall):
        return f1, True
    return 0.5 * f1 + 0.5 * h_recall, False


# 신식
#   S = (1-beta) * F1_val  +  beta * H_hat  -  lam * FA_val
#
#   H_hat = (h + a) / (n_H + 2a)              [a = 1, 라플라스]
#     n_H=6  -> H_hat in [0.125, 0.875]  ("전부 발화"의 공짜 1.0 제거)
#     n_H=30 -> H_hat in [0.031, 0.969]  (원 recall 에 실질 수렴)
#     n_H=0  -> H_hat = 0.5 (무정보) 이지만 beta=0 이라 항 자체가 사라짐
#
#   beta  = n_H / (n_H + n0),  n0 = 30       [분산 가드 = 유효표본 축소가중]
#     n_H=0  -> 0     (F1 - lam*FA 로 자동 폴백 = 구식 폴백 규칙 보존)
#     n_H=6  -> 0.1667
#     n_H=30 -> 0.5   (**구식 0.5/0.5 를 n_H=30 의 특수해로 복원**)
#     n_H→∞  -> 1
#     n0=30 은 새로 발명한 상수가 아니라 V3_DESIGN §4.3-3 의 "val strict-H >= 30 확충"
#     목표치를 '반신뢰점'으로 앵커한 것이다.
#
#   FA_val = val 전 칸의 cell false-positive rate  FP/(FP+TN)
#     이미 metrics.csv 에 val_fpr 로 매 에폭 기록됨 → 재훈련 없이 소급 적용 가능.
#     v3에서 C·D팔이 val 에 들어오면 분모의 음성 칸이 늘어 **정의 변경 없이 자동으로
#     더 민감해진다**(단일 정의 유지).
#
#   lam = 1.0  — 등록 기본값(단순 기본값임을 명시).
#     근거 ①: F1 과 FPR 은 둘 다 칸 수준 무차원 비율([0,1]) — 단위 환산 계수가 필요 없다.
#     근거 ②: v2 실측 val_fpr 범위 0.000~0.183 vs val_f1 범위 0.000~0.537
#             (metrics.csv 9런) — 같은 자릿수라 물되 압도하지 않는다.
#     근거 ③: n_H=6 에서 H 항 1스텝 = beta*(1/8) = 0.0208 이므로,
#             전형적 dFA 0.05 를 뒤집으려면 lam >= 0.42 가 필요하다. 1.0 은 그 위.
#     민감도 lam ∈ {0.5, 1, 2} · a ∈ {0.5, 1} 를 **결과를 보기 전에** 사전등록해 함께 보고.
N0_HALF_TRUST = 30.0
LAMBDA_FA = 1.0
LAPLACE_A = 1.0


def h_shrunk(h_hits: float, n_h: int, a: float = LAPLACE_A) -> float:
    return (h_hits + a) / (n_h + 2 * a)


def beta_weight(n_h: int, n0: float = N0_HALF_TRUST) -> float:
    return n_h / (n_h + n0) if n_h > 0 else 0.0


def sel_score_v3(f1: float, h_hits: float, n_h: int, fa: float,
                 lam: float = LAMBDA_FA, a: float = LAPLACE_A,
                 n0: float = N0_HALF_TRUST) -> float:
    b = beta_weight(n_h, n0)
    hh = h_shrunk(h_hits, n_h, a) if n_h > 0 else 0.0
    return (1.0 - b) * f1 + b * hh - lam * fa


FORMULA_ID = (f"S = (1-b)*val_cell_F1 + b*(h+{LAPLACE_A:g})/(n_H+{2*LAPLACE_A:g})"
              f" - {LAMBDA_FA:g}*val_cell_FPR,  b = n_H/(n_H+{N0_HALF_TRUST:g}),"
              f"  gate VG-const: val-all max-prob spread >= {VGCONST_SPREAD_MIN:g}"
              f"  (tie -> earliest epoch)")


def select_epoch(rows: Sequence[dict], score_key: str) -> dict:
    """동률 시 이른 에폭 (train_polar.py:435 `if sel > best` 와 동일 규칙)."""
    best = None
    for r in rows:
        s = r[score_key]
        if s is None or not math.isfinite(s):
            continue
        if best is None or s > best[score_key]:
            best = r
    return best


# ---------------------------------------------------------------------------
# §D  무시 마스크 규약 + FA 모집단 등록  (RT-B §5-③ 보강 처분)
# ---------------------------------------------------------------------------
# ── D-1  무시 마스크의 3단 사거리 (신설 규약) ────────────────────────────────
#   손실   : 마스크 적용            (V3_DESIGN §5.1 — B팔 H 칸은 손실 제외)
#   선택식 : **손실과 동일한 마스크 적용**   <-- 본 파일이 신설하는 규약
#   평가   : 마스크 미적용          (ACCOUNTING §2-4 — 평가 분모·recall·FA 정의 불변)
#
#   왜 선택식에도 거나: **선택식은 평가가 아니라 훈련 루프의 일부다.** val에 B팔(위험−단서)
#   H 프레임이 들어가면, 마스크 없는 선택식은 "모델이 무시하라고 배운 칸에서 발화한" 체크포인트를
#   고른다 — 지도와 선택이 정반대를 요구하는 구성이고, MOD-07이 진단한 병의 v3판 재발이다
#   (RT_LEDGER_B.md:548-553). 마스크된 칸은 **H 분자·H 분모·F1·FA 어디에도 기여하지 않는다.**
#
#   §2-4와 충돌하지 않는다: §2-4가 규율하는 것은 **평가 분모**이고, 여기서 마스크가 닿는 것은
#   **val 위에서 계산되는 훈련 루프 내부 스칼라**다. 평가 코드 경로는 손대지 않는다.
#
#   v2 소급 적용: v2에는 무시 마스크가 **존재하지 않는다**(ignore = 전부 False) → 아래 함수들은
#   마스크 없는 계산과 항등이고, 따라서 **v2 재현 검증 숫자는 이 규약에 영향받지 않는다.**
#
# ── D-2  FA 항의 모집단 등록 ─────────────────────────────────────────────────
#   RT-B §5-③(다): FA 항에 FA_C(단서 있는 무위험)를 넣으면 선택이 ④-a층 목표를 직접 최적화해
#   **계기판 ③이 자기 선택 기준을 재는 순환**이 된다 → FA 항은 **FA_D(청정 오경보) 권고**.
#   그러나 v2에는 D팔 표본이 없고(ACCOUNTING §2-3), off팔은 씬별 8C/25D 혼합이며(§4.1),
#   에폭별로 남은 통계량은 pooled `val_fpr` 하나뿐이다. 따라서 **하나의 식 · 하나의 정의**를
#   유지하되 **모집단만 코퍼스가 선언**한다(선언값은 config.json 에 각인, 표에서 절대 혼용 금지).
FA_POPULATIONS = {
    # v2: D팔이 존재하지 않음 -> pooled val 칸 (선언된 근사, 재현 검증 전용)
    "v2_all_val_cells": "val 전 칸의 FP/(FP+TN) — v2에는 D팔이 없다(ACCOUNTING §2-3·§4.1)",
    # v3: 청정 오경보만 -> D팔(무위험·무단서) 칸 한정
    "v3_D_arm_cells": "D팔(무위험·무단서) 칸 한정 FP/(FP+TN) = FA_D (RT-B §5-③(다) 권고)",
}
FA_POPULATION_DEFAULT_V2 = "v2_all_val_cells"
FA_POPULATION_DEFAULT_V3 = "v3_D_arm_cells"

# ── D-3  H 항 만개 조건 (공급 의존성 · 가정하지 않는다) ──────────────────────
#   beta = n_H/(n_H+30) 은 n_H=30 에서 0.5 가 된다. 그러나 RT-B §7-#2 실측:
#   **"val strict-H >= 30"의 공급원이 현 사양 안에 없다** — test-ext 씬은 val 로 쓸 수 없다
#   (ACCOUNTING §2-9). 따라서 본 식은 30 을 **가정하지 않고** n_H 을 매 실행 실측해 beta 를
#   만든다. 공급이 오기 전까지 beta = 6/36 = 0.1667 로 머물며, 그것이 정직한 상태다.
H_FULL_WEIGHT_CONDITION = ("H 항 만개(beta=0.5)는 **훈련측 씬**에서 공급된 "
                           "val strict-H >= 30 이 착지한 뒤에만 성립한다 "
                           "(RT_LEDGER_B.md:643-656 · P-5 렌더 계획 의존)")


def _mask_arrays(gt, ignore):
    """ignore=None 이면 전부 유효. 반환 = valid(bool, gt 와 동형)."""
    import numpy as np
    gt = np.asarray(gt)
    if ignore is None:
        return np.ones_like(gt, dtype=bool)
    ig = np.asarray(ignore, dtype=bool)
    if ig.shape != gt.shape:
        raise AssertionError(f"[VG-mask] ignore shape {ig.shape} != gt shape {gt.shape}")
    return ~ig


def cell_stats_selection(prob, gt, tau, ignore=None, fa_cells=None):
    """선택식용 칸 통계. **마스크된 칸은 어디에도 기여하지 않는다.**
    fa_cells = FA 항 모집단 불리언(칸 단위). None -> 유효 칸 전체(v2 규약)."""
    import numpy as np
    prob, gt = np.asarray(prob), np.asarray(gt)
    valid = _mask_arrays(gt, ignore)
    pred, pos = (prob >= tau), (gt > 0.5)
    tp = float((pred & pos & valid).sum())
    fp = float((pred & ~pos & valid).sum())
    fn = float((~pred & pos & valid).sum())
    f1 = 2 * tp / max(2 * tp + fp + fn, 1e-9)
    fam = valid if fa_cells is None else (valid & np.asarray(fa_cells, dtype=bool))
    fa_fp = float((pred & ~pos & fam).sum())
    fa_tn = float((~pred & ~pos & fam).sum())
    fa = fa_fp / max(fa_fp + fa_tn, 1e-9)
    return f1, fa, int(valid.sum()), int(fam.sum())


def h_frame_recall_selection(prob, gt, tier, tau, ignore=None):
    """선택식용 H 프레임 recall. 정본 분모 = tier=='H' ∧ **마스크되지 않은** 양성 칸 >= 1.
    적중 = 마스크되지 않은 양성 칸 중 하나 이상에서 발화. -> (h_hits, n_H)."""
    import numpy as np
    prob, gt = np.asarray(prob), np.asarray(gt)
    tier = np.asarray(tier)
    valid = _mask_arrays(gt, ignore)
    pos_eff = (gt > 0.5) & valid                    # 유효 양성 칸
    sel = (tier == "H") & pos_eff.any(1)            # <- 단일 분모 정의 (마스크 반영)
    n = int(sel.sum())
    if n == 0:
        return 0, 0
    hit = ((prob >= tau) & pos_eff)[sel].any(1)
    return int(hit.sum()), n


def compute_selection(prob, gt, tier, tau, *, ignore=None, fa_cells=None,
                      lam: float = LAMBDA_FA, a: float = LAPLACE_A,
                      n0: float = N0_HALF_TRUST,
                      fa_population: str = FA_POPULATION_DEFAULT_V2) -> dict:
    """**단일 진입점.** 훈련 루프는 이 함수만 호출한다.
    VG-const 게이트는 여기서 함께 판정한다(확률을 이미 갖고 있는 유일한 지점)."""
    if fa_population not in FA_POPULATIONS:
        raise AssertionError(f"[VG-fa] 미등록 FA 모집단: {fa_population}")
    f1, fa, n_valid, n_fa = cell_stats_selection(prob, gt, tau, ignore, fa_cells)
    h, n_h = h_frame_recall_selection(prob, gt, tier, tau, ignore)
    spread = output_spread([list(r) for r in prob])
    gate = vgconst_pass(spread)
    s = sel_score_v3(f1, h, n_h, fa, lam=lam, a=a, n0=n0)
    return {"S": (s if gate else float("-inf")), "S_ungated": s,
            "f1": f1, "fa": fa, "h_hits": h, "n_H": n_h,
            "beta": beta_weight(n_h, n0), "H_hat": (h_shrunk(h, n_h, a) if n_h else None),
            "spread": spread, "vgconst_pass": gate,
            "n_valid_cells": n_valid, "n_fa_cells": n_fa,
            "fa_population": fa_population, "ignore_applied": ignore is not None}


if __name__ == "__main__":
    print(json.dumps({"H_DEF_ID": H_DEF_ID, "FORMULA_ID": FORMULA_ID,
                      "VGCONST_STAGE": VGCONST_STAGE, "VGCONST_SPREAD_MIN": VGCONST_SPREAD_MIN,
                      "VGCONST_SOURCE": VGCONST_SOURCE, "FA_POPULATIONS": FA_POPULATIONS,
                      "H_FULL_WEIGHT_CONDITION": H_FULL_WEIGHT_CONDITION},
                     ensure_ascii=False, indent=2))
