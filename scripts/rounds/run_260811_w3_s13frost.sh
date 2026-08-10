#!/bin/bash
# GT-73 frosted 파일럿 A/B — s13 유리 31프림 (기하 불변, R-2 재질 전용)
#   arm a = 현행 (OmniPBR enable_opacity 0.35 — 배경 선명)
#   arm b = frosted 안 (OmniGlass: 경계 차폐 23 frosting 0.35 · 무관 8 클리어 0.0)
#   같은 HEAD·같은 플래그, 유리 env 2개만 차이 — 같은 prim A/B (§2.3)
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
n=scene13; REL=main/scene13_apartment_parking_entry
declare -A ARM_ENV=( [a]="" [b]="NEGOBS_GLASS_FROST=1 NEGOBS_GLASS_MDL=glass" )
for arm in a b; do
  ROUND=260811_w3_s13frost_${arm}; LOG=look_check/logs/${ROUND}.log
  mkdir -p look_check/logs; touch $LOG
  out=look_check/${n}/${ROUND}; mkdir -p $out
  python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out \
      NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
      ${ARM_ENV[$arm]} \
      python scenes/${REL}.py >> $LOG 2>&1
  cuts=$(ls $out/*.png 2>/dev/null | wc -l)
  echo "$n $arm $cuts $?" | tee -a $LOG
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
  echo "[$ROUND] done" | tee -a $LOG
done
