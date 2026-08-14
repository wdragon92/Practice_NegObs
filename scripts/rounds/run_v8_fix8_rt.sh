#!/bin/bash
# v8 — X 웨이브 반영 잔여 8씬 SMOKE+RT (look_check/sceneNN/v8_rt)
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
LOG=look_check/v8_fix8_rt.log
: > $LOG
LIST="scene05_amphitheater scene06_overpass_spiral scene07_temple_stone_path \
scene09_ghat_riverfront scene10_park_deck_switchback scene11_footbridge_stairs \
scene12_riverside_deck scene17_ramp_pair_hangang"
for s in $LIST; do
  n=${s%%_*}
  if grep -q "NEGOBS_SMOKE" scenes/main/$s.py; then
    NEGOBS_SMOKE=1 python scenes/main/$s.py >> $LOG 2>&1 || { echo "$s SMOKE_FAIL" | tee -a $LOG; continue; }
  fi
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/${n}/v8_rt \
    python scenes/main/$s.py >> $LOG 2>&1
  echo "$s RT_EXIT=$? FILES=$(ls look_check/${n}/v8_rt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "v8 fix8 RT 완료" | tee -a $LOG
