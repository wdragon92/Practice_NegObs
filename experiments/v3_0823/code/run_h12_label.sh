#!/bin/bash
# =============================================================================
# run_h12_label.sh — sceneH1 / sceneH2 (test-ext) 4팔 프로브의 **라벨 + 게이트** (CPU 전용)
#
# 라벨 3회
#   (A,C) — 기준 쌍. A팔 tier·발자국·VG-datum(A,C) 의 원천이고, **계기판 ① 의 쌍 규약**이다.
#   (B,D) — B팔 tier. `paired-H` = A·B 가 **둘 다** strict-H 인 프레임(사전등록 §4.2 정의).
#   near  — 근거리 비-H 대조. 퇴화(전 프레임 H)가 아님을 실렌더로 확인한다.
#
# 게이트 2종
#   h67_yield.py --split ext : strict-H 수율 대 계획 §3.2 가정(0.50) · VG-datum/10/08/void
#   h12_gates.py             : VG-01 · VG-02 · VG-06 · VG-07 · paired-H (4팔 전용)
#
# 사용
#   bash experiments/v3_0823/code/run_h12_label.sh                       # R0 (probe·near, 두 씬)
#   bash experiments/v3_0823/code/run_h12_label.sh 260823_v3p5_h12rev \
#        260823_v3p5_h12near rev sceneH1                                 # 개정 후 (sceneH1 만)
#   인자: <probe-stamp> <near-stamp> <tag> <scenes>
# =============================================================================
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
LAB="$REPO/experiments/mainrun_0819/code/labeling"
ANN="$REPO/experiments/v3_0823/annotations"
D="$REPO/dataset"

S="${1:-260823_v3p5_h12probe}"
N="${2:-260823_v3p5_h12near}"
TAG="${3:-r0}"
SCENES="${4:-sceneH1,sceneH2}"

mkdir -p "$ANN"
export PYTHONNOUSERSITE=1
unset PYTHONPATH VIRTUAL_ENV

label() {  # label <on-round> <off-round> <out>
  local _on _off                      # 0827: rounds are grouped
  _on="$(negobs_round "$1")"  || return 1
  _off="$(negobs_round "$2")" || return 1
  ( cd "$LAB" && $PY labeler.py --on-round "$_on" --off-round "$_off" \
        --grid gridspec_v1.json --scenes "$SCENES" --out "$3" --workers 4 )
}

echo "=== (A,C) 라벨 · $S ==========================================="
label "${S}_A" "${S}_C" "$ANN/h12_${TAG}_ac_labels.json"
echo "=== (B,D) 라벨 · $S ==========================================="
label "${S}_B" "${S}_D" "$ANN/h12_${TAG}_bd_labels.json"
if [ -d "$(negobs_round_or_flat "${N}_A")" ]; then
  echo "=== near (A,C) 라벨 · $N ======================================"
  label "${N}_A" "${N}_C" "$ANN/h12_${TAG}_near_labels.json"
fi

cd "$REPO"
echo
echo "=== strict-H 수율 (H 밴드 · test-ext 모형 0.50) ==============="
$PY experiments/v3_0823/code/h67_yield.py \
    --labels "$ANN/h12_${TAG}_ac_labels.json" \
    --on "$(negobs_round "${S}_A")" --off "$(negobs_round "${S}_C")" --band H --split ext
if [ -f "$ANN/h12_${TAG}_near_labels.json" ]; then
  echo
  echo "=== 근거리 대조 (비-H 가 실제로 나오는가) ====================="
  $PY experiments/v3_0823/code/h67_yield.py \
      --labels "$ANN/h12_${TAG}_near_labels.json" \
      --on "$(negobs_round "${N}_A")" --off "$(negobs_round "${N}_C")" --band base --split ext
fi
echo
echo "=== 4팔 게이트 (VG-01/02/06/07 · paired-H) ===================="
$PY experiments/v3_0823/code/h12_gates.py \
    --root dataset --stamp "$S" --split test --scenes "$SCENES" \
    --labels-ac "$ANN/h12_${TAG}_ac_labels.json" \
    --labels-bd "$ANN/h12_${TAG}_bd_labels.json" \
    --out "$REPO/experiments/v3_0823/h12_gates_${TAG}.json"
