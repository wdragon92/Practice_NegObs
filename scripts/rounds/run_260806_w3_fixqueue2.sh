#!/bin/bash
# =============================================================================
# 08-06 검수 답변 라운드 — 15씬 PT (round = 260806_w3_fixqueue2)
#   근거: ledger GT-74~88 선신고 (08-06 사용자 17씬 검수) + GT-83 사실화 교정
#   재질 팔: LOOK_V1=1 · DETAIL_SCALE=2 · ROUGH_GAIN=0 (doctrine 팔 동일)
#   baseline: 01/05/06/10/14/16 = 260806_w3_fixqueue · 20 = 260805_w3_hedgeswap ·
#             03/07/08/09/11/17/19/C4 = 260731_w3_full
#   사용법: bash run_260806_w3_fixqueue2.sh [scene01 sceneC4 ...]  (무인자 = 15씬 전부)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260806_w3_fixqueue2
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs
touch $LOG

declare -A SCENES=(
  [scene01]=main/scene01_campus_stairs
  [scene03]=main/scene03_riverbank
  [scene05]=main/scene05_amphitheater
  [scene06]=main/scene06_overpass_spiral
  [scene07]=main/scene07_temple_stone_path
  [scene08]=main/scene08_sunken_plaza
  [scene09]=main/scene09_ghat_riverfront
  [scene10]=main/scene10_park_deck_switchback
  [scene11]=main/scene11_footbridge_stairs
  [scene14]=main/scene14_grandstair_illusion
  [scene16]=main/scene16_canopy_shadow
  [scene17]=main/scene17_ramp_pair_hangang
  [scene19]=main/scene19_fan_winder
  [scene20]=main/scene20_diagonal_oblique
  [sceneC4]=batch1/sceneC4_wet_stairs
)
ORDER=(scene01 scene03 scene05 scene06 scene07 scene08 scene09 scene10 scene11 scene14 scene16 scene17 scene19 scene20 sceneC4)
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
