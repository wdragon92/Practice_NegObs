#!/bin/bash
# 감사 v4 구현(5팀) 반영 후 유지 씬 15종 SMOKE + RT 확인 렌더
#   출력: look_check/sceneNN/v5_rt  ·  로그: look_check/v5_keep_rt.log
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
LOG=look_check/v5_keep_rt.log
: > $LOG

KEEP="scene01_campus_stairs scene02_underpass scene03_riverbank scene04_parktrail \
scene05_amphitheater scene09_ghat_riverfront scene13_helical_parkingramp \
scene14_grandstair_illusion scene15_alley_labyrinth scene16_canopy_shadow \
scene17_ramp_pair_hangang scene18_wavy_artstair scene19_fan_winder \
scene20_diagonal_oblique scene21_monumental_selfocclude"

for s in $KEEP; do
  n=${s%%_*}
  # v2 세트(01~05)는 SMOKE 규약 도입 전 — 미지원 씬은 SMOKE 생략, RT 직행
  if grep -q "NEGOBS_SMOKE" $s.py; then
    NEGOBS_SMOKE=1 python $s.py >> $LOG 2>&1
    SM=$?
    if [ $SM -ne 0 ]; then
      echo "$s SMOKE_EXIT=$SM RT=SKIP" | tee -a $LOG
      continue
    fi
  else
    echo "$s SMOKE=N/A(v2)" | tee -a $LOG
  fi
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/${n}/v5_rt \
    python $s.py >> $LOG 2>&1
  echo "$s SMOKE_OK RT_EXIT=$? FILES=$(ls look_check/${n}/v5_rt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "v5 keep RT 완료" | tee -a $LOG
