#!/bin/bash
# scene19 옥상 v3 확인 렌더 (RT) — 진입 확폭 + 옥상 재프레이밍
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
LOG=look_check/scene19_r5.log
: > $LOG
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/scene19/r5 \
  python scene19_fan_winder.py >> $LOG 2>&1
echo "scene19 RT_EXIT=$? FILES=$(ls look_check/scene19/r5 2>/dev/null | wc -l)" | tee -a $LOG
