#!/bin/bash
# =============================================================================
# GT-96 라운드 — scene11 울타리 리본 통일(1.25 단일 높이·테이퍼/빌보드 소멸)·동측 레그 1 제거
#   round = 260811_w3_s11ribbon · 근거: ledger 행 52 GT-96 선신고 (08-10~11 사용자)
#   재질 팔: fixqueue2 동일 · baseline: scene11 = 260806_w3_fixqueue2
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
ROUND=260811_w3_s11ribbon
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs; touch $LOG
n=scene11; rel=main/scene11_footbridge_stairs
out=look_check/${n}/${ROUND}; mkdir -p $out
python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
t0=$(date +%s.%N)
env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out \
    NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
    NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
    python scenes/${rel}.py >> $LOG 2>&1
rc=$?
t1=$(date +%s.%N); dt=$(echo "$t1 - $t0" | bc)
cuts=$(ls $out/*.png 2>/dev/null | wc -l)
printf "%s\t%.1f\t%d\t%d\n" "$n" "$dt" "$cuts" "$rc" | tee -a $LOG
python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
echo "[$ROUND] done" | tee -a $LOG
