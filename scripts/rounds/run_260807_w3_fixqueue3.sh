#!/bin/bash
# =============================================================================
# 08-07 검수 답변 라운드 — 4씬 PT (round = 260807_w3_fixqueue3)
#   근거: ledger GT-90~93 선신고 (08-07 사용자 답변 — s16 확폭·스케일업 /
#         s03 곡선 접속교 롤백 / s06 계단 접속 개방 / s11 철물 감량)
#   재질 팔: LOOK_V1=1 · DETAIL_SCALE=2 · ROUGH_GAIN=0 (fixqueue2 팔 동일)
#   baseline: 03/06/11/16 전부 = 260806_w3_fixqueue2
#   사용법: bash run_260807_w3_fixqueue3.sh [scene03 scene16 ...]  (무인자 = 4씬 전부)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260807_w3_fixqueue3
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs
touch $LOG

declare -A SCENES=(
  [scene03]=main/scene03_riverbank
  [scene06]=main/scene06_overpass_spiral
  [scene11]=main/scene11_footbridge_stairs
  [scene16]=main/scene16_canopy_shadow
)
ORDER=(scene03 scene06 scene11 scene16)
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
