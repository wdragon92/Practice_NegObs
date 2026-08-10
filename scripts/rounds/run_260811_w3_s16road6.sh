#!/bin/bash
# GT-103 s16 대공사 — 왕복 6차로+중분대(22.2 m)·통로 z_top −3.00(유효고 2.65)·계단 20단
#   동측 전이(계단 30.20→36.60·walk 40·건물 C 42)·x0 종단 포스트. baseline 260806_w3_fixqueue2
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
n=scene16; REL=main/scene16_canopy_shadow
ROUND=260811_w3_s16road6; LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs; touch $LOG
out=look_check/${n}/${ROUND}; mkdir -p $out
python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out \
    NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
    NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
    python scenes/${REL}.py >> $LOG 2>&1
cuts=$(ls $out/*.png 2>/dev/null | wc -l)
echo "$n $cuts $?" | tee -a $LOG
python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
echo "[$ROUND] done" | tee -a $LOG
