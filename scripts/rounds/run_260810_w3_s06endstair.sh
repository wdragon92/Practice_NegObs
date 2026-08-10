#!/bin/bash
# =============================================================================
# GT-97 라운드 — scene06 타워 동측 이동(+3.0)·통로 단부 정면 접속·판정축 2.6
#   round = 260810_w3_s06endstair · 근거: ledger 행 53 GT-97 선신고 (08-10 사용자 7차)
#   재질 팔: fixqueue2 와 동일 (LOOK_V1=1 · DETAIL_SCALE=2 · ROUGH_GAIN=0 · PT_FAST)
#   baseline: scene06 = 260810_w3_s06direct(GT-95판)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260810_w3_s06endstair
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs
touch $LOG

n=scene06
rel=main/scene06_overpass_spiral
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
echo "[$ROUND] done" | tee -a $LOG
