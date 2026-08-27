#!/bin/bash
# v8 PT — 진출 7씬 (judge_v8_rt)
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
LOG=look_check/logs/v8_pt7.log
: > $LOG
LIST="scene05_amphitheater scene06_overpass_spiral scene07_temple_stone_path \
scene10_park_deck_switchback scene11_footbridge_stairs scene12_riverside_deck \
scene17_ramp_pair_hangang"
for s in $LIST; do
  n=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/${n}/v8_pt \
    python scenes/main/$s.py >> $LOG 2>&1
  echo "$s PT_EXIT=$? FILES=$(ls look_check/${n}/v8_pt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "v8 PT7 완료" | tee -a $LOG
