#!/bin/bash
# =============================================================================
# Gallery fix-plan §2 큐 라운드 — 백로그 6씬 + 헤지 밀도 파일럿 PT (round = 260806_w3_fixqueue)
#   근거: gallery_fix_plan_v1.md §2 + 08-06 사용자 지시 — ledger GT-65~71 선신고 참조
#   순서: scene01 선행 (공용 킷 build_railing_line 변경의 §2.3 1씬 선검증) → 나머지
#   재질 팔: 260805_w3_doctrine 과 동일 (LOOK_V1=1 · DETAIL_SCALE=2 · ROUGH_GAIN=0)
#   baseline (회귀): 01·06·10·12 = 260805_w3_doctrine · 05·14·16 = 260805_w3_hedgeswap
#   사용법: bash run_260806_w3_fixqueue.sh [scene01 scene10 ...]  (무인자 = 7씬 전부)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260806_w3_fixqueue
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs
touch $LOG

declare -A SCENES=(
  [scene01]=main/scene01_campus_stairs
  [scene05]=main/scene05_amphitheater
  [scene06]=main/scene06_overpass_spiral
  [scene10]=main/scene10_park_deck_switchback
  [scene12]=main/scene12_riverside_deck
  [scene14]=main/scene14_grandstair_illusion
  [scene16]=main/scene16_canopy_shadow
)
ORDER=(scene01 scene10 scene12 scene06 scene05 scene14 scene16)
KEYS=("${@:-${ORDER[@]}}")

for n in "${KEYS[@]}"; do
  rel=${SCENES[$n]}
  if [ -z "$rel" ]; then echo "[$ROUND] unknown scene $n" | tee -a $LOG; continue; fi
  out=look_check/${n}/${ROUND}
  mkdir -p $out
  python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
  t0=$(date +%s.%N)
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out \
      NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
      python scenes/${rel}.py >> $LOG 2>&1
  rc=$?
  t1=$(date +%s.%N)
  dt=$(echo "$t1 - $t0" | bc)
  cuts=$(ls $out/*.png 2>/dev/null | wc -l)
  printf "%s\t%.1f\t%d\t%d\n" "$n" "$dt" "$cuts" "$rc" | tee -a $LOG
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
done
echo "[$ROUND] done (${KEYS[*]})" | tee -a $LOG
