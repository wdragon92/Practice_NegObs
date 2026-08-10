#!/bin/bash
# GT-100(s06 서측 접합 수평 시작 베이) + GT-96 2판(s11 동측 존치 레그 스왑 east_N)
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
declare -A R=( [scene06]=260811_w3_s06weld [scene11]=260811_w3_s11flip )
declare -A REL=( [scene06]=main/scene06_overpass_spiral [scene11]=main/scene11_footbridge_stairs )
for n in scene06 scene11; do
  ROUND=${R[$n]}; LOG=look_check/logs/${ROUND}.log
  mkdir -p look_check/logs; touch $LOG
  out=look_check/${n}/${ROUND}; mkdir -p $out
  python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out \
      NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
      python scenes/${REL[$n]}.py >> $LOG 2>&1
  cuts=$(ls $out/*.png 2>/dev/null | wc -l)
  echo "$n $cuts $?" | tee -a $LOG
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
  echo "[$ROUND] done" | tee -a $LOG
done
