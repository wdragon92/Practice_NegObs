#!/bin/bash
# 유지 씬 15종 PT 파이널 (판정 반영 수정 후) — 512spp/8바운스
#   출력: look_check/sceneNN/v5_pt  ·  로그: look_check/logs/v5_keep_pt.log
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
LOG=look_check/logs/v5_keep_pt.log
: > $LOG

KEEP="scene01_campus_stairs scene02_underpass scene03_riverbank scene04_parktrail \
scene05_amphitheater scene09_ghat_riverfront scene13_helical_parkingramp \
scene14_grandstair_illusion scene15_alley_labyrinth scene16_canopy_shadow \
scene17_ramp_pair_hangang scene18_wavy_artstair scene19_fan_winder \
scene20_diagonal_oblique scene21_monumental_selfocclude"

for s in $KEEP; do
  n=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/${n}/v5_pt \
    python scenes/main/$s.py >> $LOG 2>&1
  echo "$s PT_EXIT=$? FILES=$(ls look_check/${n}/v5_pt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "v5 keep PT 완료" | tee -a $LOG
