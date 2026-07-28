#!/bin/bash
# v7 PT 파이널 — 진출 13씬 (judge_v7_rt_A/B)
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
LOG=look_check/v7_pt13.log
: > $LOG
LIST="scene01_campus_stairs scene02_underpass scene03_riverbank scene04_parktrail \
scene08_sunken_plaza scene13_apartment_parking_entry scene14_grandstair_illusion \
scene15_alley_labyrinth scene16_canopy_shadow scene18_wavy_artstair \
scene19_fan_winder scene20_diagonal_oblique scene21_monumental_selfocclude"
for s in $LIST; do
  n=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/${n}/v7_pt \
    python scenes/main/$s.py >> $LOG 2>&1
  echo "$s PT_EXIT=$? FILES=$(ls look_check/${n}/v7_pt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "v7 PT13 완료" | tee -a $LOG
