#!/bin/bash
# =============================================================================
# run_h3l1_label.sh — sceneH3 / sceneL1 (test-ext) 4팔 프로브의 **라벨 + 게이트** (CPU 전용)
#
# 라벨 3회
#   (A,C) — 기준 쌍. A팔 tier·발자국·VG-datum(A,C) 의 원천이고, **계기판 ① 의 쌍 규약**이다.
#   (B,D) — B팔 tier. `paired-H` = A·B 가 **둘 다** strict-H 인 프레임(사전등록 §4.2 정의).
#   near  — 근거리 대조. sceneH3 은 퇴화(전 프레임 H)가 아님을, sceneL1 은 근거리 섹터
#           이동을 확인한다.
#
# 게이트 2종
#   h67_yield.py --split ext : strict-H 수율 대 계획 §3.2 가정(0.50) · VG-datum/10/08/void
#        ※ **sceneL1 에 대한 수율 판정문은 무의미하다** — 측방 씬은 은닉 씬이 아니고
#          계획 §3.2 표의 paired-H 열이 "—" 다. 그 씬의 판정은 아래 섹터 게이트다.
#   h12_gates.py             : VG-01 · VG-02 · VG-06 · VG-07 · paired-H + **섹터 분포**
#
# 사용
#   bash experiments/v3_0823/code/run_h3l1_label.sh                       # probe·near, 두 씬
#   bash experiments/v3_0823/code/run_h3l1_label.sh 260823_v3p5_h3l1rev \
#        260823_v3p5_h3l1near rev sceneH3                                 # 개정 후 한 씬만
#   인자: <probe-stamp> <near-stamp> <tag> <scenes>
# =============================================================================
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
LAB="$REPO/experiments/mainrun_0819/code/labeling"
ANN="$REPO/experiments/v3_0823/annotations"
D="$REPO/dataset"

S="${1:-260823_v3p5_h3l1probe}"
N="${2:-260823_v3p5_h3l1near}"
TAG="${3:-r0}"
SCENES="${4:-sceneH3,sceneL1}"

mkdir -p "$ANN"
export PYTHONNOUSERSITE=1
unset PYTHONPATH VIRTUAL_ENV

label() {  # label <on-round> <off-round> <out>
  ( cd "$LAB" && $PY labeler.py --on-round "$D/$1" --off-round "$D/$2" \
        --grid gridspec_v1.json --scenes "$SCENES" --out "$3" --workers 4 )
}

echo "=== (A,C) 라벨 · $S ==========================================="
label "${S}_A" "${S}_C" "$ANN/h3l1_${TAG}_ac_labels.json"
echo "=== (B,D) 라벨 · $S ==========================================="
label "${S}_B" "${S}_D" "$ANN/h3l1_${TAG}_bd_labels.json"
if [ -d "$D/${N}_A" ]; then
  echo "=== near (A,C) 라벨 · $N ======================================"
  label "${N}_A" "${N}_C" "$ANN/h3l1_${TAG}_near_labels.json"
fi

cd "$REPO"
echo
echo "=== strict-H 수율 (test-ext 모형 0.50) ========================"
echo "    ※ sceneL1(측방)의 판정문은 무시한다 — 아래 섹터 게이트가 판정층이다."
$PY experiments/v3_0823/code/h67_yield.py \
    --labels "$ANN/h3l1_${TAG}_ac_labels.json" \
    --on "dataset/${S}_A" --off "dataset/${S}_C" --band H --split ext
if [ -f "$ANN/h3l1_${TAG}_near_labels.json" ]; then
  echo
  echo "=== 근거리 대조 (비-H 가 실제로 나오는가) ====================="
  $PY experiments/v3_0823/code/h67_yield.py \
      --labels "$ANN/h3l1_${TAG}_near_labels.json" \
      --on "dataset/${N}_A" --off "dataset/${N}_C" --band base --split ext
fi
echo
echo "=== 4팔 게이트 (VG-01/02/06/07 · paired-H · 섹터 분포) ========"
$PY experiments/v3_0823/code/h12_gates.py \
    --root dataset --stamp "$S" --split test --scenes "$SCENES" \
    --labels-ac "$ANN/h3l1_${TAG}_ac_labels.json" \
    --labels-bd "$ANN/h3l1_${TAG}_bd_labels.json" \
    --out "$REPO/experiments/v3_0823/h3l1_gates_${TAG}.json"
if [ -f "$ANN/h3l1_${TAG}_near_labels.json" ]; then
  echo
  echo "=== 근거리 라운드 섹터 대조 (sceneL1) ========================="
  $PY experiments/v3_0823/code/h12_gates.py \
      --root dataset --stamp "$N" --split test --scenes sceneL1 \
      --labels-ac "$ANN/h3l1_${TAG}_near_labels.json" \
      --out "$REPO/experiments/v3_0823/h3l1_gates_${TAG}_near.json" || true
fi
