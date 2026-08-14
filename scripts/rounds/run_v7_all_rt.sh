#!/bin/bash
# v7 전 씬 라운드 (v5/v5.1 반영 + 나무 v2 일괄): SMOKE(지원 씬) → RT
#   출력 look_check/sceneNN/v7_rt · 로그 look_check/v7_all_rt.log
#   ※ 신규 파일명 기준 (구 helical/towerstone 등은 archive_v3)
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
LOG=look_check/v7_all_rt.log
: > $LOG

ALL="scene01_campus_stairs scene02_underpass scene03_riverbank scene04_parktrail \
scene05_amphitheater scene06_overpass_spiral scene07_temple_stone_path \
scene08_sunken_plaza scene09_ghat_riverfront scene10_park_deck_switchback \
scene11_footbridge_stairs scene12_riverside_deck scene13_apartment_parking_entry \
scene14_grandstair_illusion scene15_alley_labyrinth scene16_canopy_shadow \
scene17_ramp_pair_hangang scene18_wavy_artstair scene19_fan_winder \
scene20_diagonal_oblique scene21_monumental_selfocclude"

for s in $ALL; do
  n=${s%%_*}
  if grep -q "NEGOBS_SMOKE" scenes/main/$s.py; then
    NEGOBS_SMOKE=1 python scenes/main/$s.py >> $LOG 2>&1
    SM=$?
    if [ $SM -ne 0 ]; then
      echo "$s SMOKE_EXIT=$SM RT=SKIP" | tee -a $LOG
      continue
    fi
  else
    echo "$s SMOKE=N/A(v2)" | tee -a $LOG
  fi
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/${n}/v7_rt \
    python scenes/main/$s.py >> $LOG 2>&1
  echo "$s SMOKE_OK RT_EXIT=$? FILES=$(ls look_check/${n}/v7_rt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "v7 all RT 완료" | tee -a $LOG
