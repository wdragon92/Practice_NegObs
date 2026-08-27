#!/bin/bash
# =============================================================================
# GT-63 헤지 실자산 전환 라운드 — 전경 전정 밴드 8씬 PT (round = 260805_w3_hedgeswap)
#   근거: 08-05 사용자 지시(GT-62 방식 확산) — ledger GT-63 선신고 참조
#   재질 팔: 260805_w3_doctrine 과 동일 (LOOK_V1=1 · DETAIL_SCALE=2 · ROUGH_GAIN=0)
#   사용법: bash run_260805_w3_hedgeswap.sh [scene02 sceneN1 ...]  (무인자 = 8씬 전부)
#   scene02 는 지하도 암부로 total_spp 256 (scripts/rounds/run_p2_all33.sh 규약)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260805_w3_hedgeswap
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs
touch $LOG

declare -A SCENES=(
  [scene02]=main/scene02_underpass
  [scene05]=main/scene05_amphitheater
  [scene14]=main/scene14_grandstair_illusion
  [scene15]=main/scene15_alley_labyrinth
  [scene16]=main/scene16_canopy_shadow
  [scene20]=main/scene20_diagonal_oblique
  [sceneN1]=batch1/sceneN1_shadow_band
  [sceneN2]=batch1/sceneN2_asphalt_patch
)
ORDER=(scene16 scene02 scene05 scene14 scene15 scene20 sceneN1 sceneN2)
KEYS=("${@:-${ORDER[@]}}")

for n in "${KEYS[@]}"; do
  rel=${SCENES[$n]}
  if [ -z "$rel" ]; then echo "[$ROUND] unknown scene $n" | tee -a $LOG; continue; fi
  out=look_check/${n}/${ROUND}
  mkdir -p $out
  spp=""
  [ "$n" = "scene02" ] && spp=256
  python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
  t0=$(date +%s.%N)
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out \
      NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
      ${spp:+NEGOBS_PT_TOTAL_SPP=$spp} \
      python scenes/${rel}.py >> $LOG 2>&1
  rc=$?
  t1=$(date +%s.%N)
  dt=$(echo "$t1 - $t0" | bc)
  cuts=$(ls $out/*.png 2>/dev/null | wc -l)
  printf "%s\t%.1f\t%d\t%d\n" "$n" "$dt" "$cuts" "$rc" | tee -a $LOG
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
done
echo "[$ROUND] done (${KEYS[*]})" | tee -a $LOG
