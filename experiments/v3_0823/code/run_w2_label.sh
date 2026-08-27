#!/bin/bash
# =============================================================================
# run_w2_label.sh — W2-lite (sceneH6·H7) 본렌더의 라벨 + 게이트 배터리 (CPU 전용)
#
# **이 씬들은 훈련 씬이다.** 산출 라벨은 v3 train/val 코퍼스로 들어가므로 W3(평가 전용)
# 과 달리 *"val strict-H ≥ 30"* (계획 §3.5) 이 함께 걸린다 — `w2_val_yield.py` 가 그 판정을 낸다.
#
# 라벨 4회 × 밴드라운드 3개 = **12회**
#   (A,C) 기준 쌍 · (B,D) B팔 tier(paired-H) · (C,A)/(D,B) 역쌍 = C·D 올-음성 반증 경로
#   ※ 역쌍을 두 씬 모두에 돌리는 이유는 W3 와 같다 — 정순 2회만으로는 AC-INSTR-1 의
#     "C팔 GT = 사양 상수" 주장이 **반증 불가능**해진다.
#
# 밴드라운드 (밴드마다 별도 디렉터리 — REG_AUDIT §8.4 (b))
#   h67base : H6·H7 · 기본 CAM_DIST
#   h67h    : H6·H7 · bands.H
#   h67h2   : H6    · bands.H 2차 draw (시드 20260824)
#
# 사용
#   bash experiments/v3_0823/code/run_w2_label.sh          # 전체
#   bash experiments/v3_0823/code/run_w2_label.sh h        # 한 밴드라운드만
# =============================================================================
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
LAB="$REPO/experiments/mainrun_0819/code/labeling"
ANN="$REPO/experiments/v3_0823/annotations"
OUT="$REPO/experiments/v3_0823"
LOG="$REPO/experiments/v3_0823/logs/w2_label.log"
D="$REPO/dataset"

ONLY="${1:-}"
mkdir -p "$ANN"
export PYTHONNOUSERSITE=1
unset PYTHONPATH VIRTUAL_ENV

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

label() {  # label <on-round> <off-round> <scenes> <out>
  if [ -s "$4" ]; then say "  [skip] $(basename "$4") — 존재"; return 0; fi
  local _on _off                      # 0827: rounds are grouped
  _on="$(negobs_round "$1")"  || return 1
  _off="$(negobs_round "$2")" || return 1
  ( cd "$LAB" && $PY labeler.py --on-round "$_on" --off-round "$_off" \
        --grid gridspec_v1.json --scenes "$3" --out "$4" --workers 4 ) \
    >> "$LOG" 2>&1 \
    && say "  [ok] $(basename "$4")" || { say "  [FAIL] $(basename "$4")"; return 1; }
}

# round <tag> <stamp> <scenes> <yield-band>
round() {
  local tag="$1" stamp="$2" scenes="$3" band="$4"
  [ -n "$ONLY" ] && [ "$ONLY" != "$tag" ] && return 0
  say "════════ $tag · $stamp · [$scenes] ════════"
  label "${stamp}_A" "${stamp}_C" "$scenes" "$ANN/w2_${tag}_ac_labels.json"
  label "${stamp}_B" "${stamp}_D" "$scenes" "$ANN/w2_${tag}_bd_labels.json"
  label "${stamp}_C" "${stamp}_A" "$scenes" "$ANN/w2_${tag}_ca_labels.json"
  label "${stamp}_D" "${stamp}_B" "$scenes" "$ANN/w2_${tag}_db_labels.json"

  say "──── h12_gates ($tag · split=val) ────"
  ( cd "$REPO" && $PY experiments/v3_0823/code/h12_gates.py \
      --root dataset --stamp "$stamp" --split val --scenes "$scenes" \
      --labels-ac "$ANN/w2_${tag}_ac_labels.json" \
      --labels-bd "$ANN/w2_${tag}_bd_labels.json" \
      --labels-ca "$ANN/w2_${tag}_ca_labels.json" \
      --labels-db "$ANN/w2_${tag}_db_labels.json" \
      --walk-z 0.0 \
      --out "$OUT/w2_gates_${tag}.json" ) 2>&1 | tee -a "$LOG"

  say "──── strict-H 수율 ($tag · 밴드 $band · val 모형 H 0.60/base 0.20) ────"
  ( cd "$REPO" && $PY experiments/v3_0823/code/h67_yield.py \
      --labels "$ANN/w2_${tag}_ac_labels.json" \
      --on "$(negobs_round "${stamp}_A")" --off "$(negobs_round "${stamp}_C")" \
      --band "$band" --split val ) 2>&1 | tee -a "$LOG"
}

say "################ W2-lite 라벨·게이트 배터리 시작 ################"
round base 260824_v3w2_h67base sceneH6,sceneH7 base
round h    260824_v3w2_h67h    sceneH6,sceneH7 H
round h2   260824_v3w2_h67h2   sceneH6         H

say "──── val strict-H ≥ 30 회계 (계획 §3.5) ────"
( cd "$REPO" && $PY experiments/v3_0823/code/w2_val_yield.py \
    --out "$OUT/w2_val_yield.json" ) 2>&1 | tee -a "$LOG"
say "################ 끝 ################"
