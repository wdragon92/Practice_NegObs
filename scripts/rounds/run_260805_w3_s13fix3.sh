#!/bin/bash
# =============================================================================
# S13 gallery answer round 3 — scene13 solo PT (round = 260805_w3_s13fix3)
#   Authority: user 3rd answer 08-05 (building-form structure, glass curtain
#   walls replacing railings, GT-60) on top of GT-58/GT-59.
#   Material arms: same as 260805_w3_doctrine (LOOK_V1=1, DETAIL_SCALE=2, RG=0)
#   Regression baseline: 260805_w3_s13fix2 (round-over-round)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260805_w3_s13fix3
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
