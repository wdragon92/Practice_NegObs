#!/bin/bash
# =============================================================================
# S13 캐노피·난간 보수 라운드 — scene13 단독 PT (round = 260805_w3_s13fix)
#   근거: gallery_fix_plan_v1.md §3 사용자 답변 (08-05) — 난간 수리 + U-5 캐노피
#   재질 팔: 260805_w3_doctrine 과 동일 (LOOK_V1=1 · DETAIL_SCALE=2 · ROUGH_GAIN=0)
#   baseline (회귀): 260731_w3_full (fix plan §2)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260805_w3_s13fix
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs
: > $LOG

s=scene13_apartment_parking_entry
n=scene13
out=look_check/${n}/${ROUND}
mkdir -p $out
export NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out
export NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1
export NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0
python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
t0=$(date +%s.%N)
python scenes/main/$s.py >> $LOG 2>&1
rc=$?
t1=$(date +%s.%N)
dt=$(echo "$t1 - $t0" | bc)
cuts=$(ls $out/*.png 2>/dev/null | wc -l)
printf "%s\t%.1f\t%d\t%d\n" "$n" "$dt" "$cuts" "$rc" | tee -a $LOG
python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
echo "[$ROUND] done (exit=$rc cuts=$cuts)" | tee -a $LOG
