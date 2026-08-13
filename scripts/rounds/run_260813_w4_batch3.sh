#!/bin/bash
# 08-13 배치 3 — GT-108(품질 파일럿 A: 룩 톤·입도) + GT-109~112(건물 파일럿 4씬).
#   s16tone/s11tone  GT-108 본편(틴트 분화·원경 포함) — baselines s16under/s11clean
#   s13tone          GT-108 asphalt 클래스 파급 확인(frost c 팔 env 동일) — baseline s13frost_c
#   s01k5            GT-109 강의동 — baseline 260806_w3_fixqueue2
#   n3wall           GT-110 가로벽 1층 띠 — baseline 260731_w3_full
#   s15villa         GT-111 다세대 — baseline 260806_w3_allview5
#   s21civic         GT-112 관공서 정합 — baseline 260806_w3_allview5
# 사용: flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260813_w4_batch3.sh [필터...]
#   ** -o 필수 ** (08-11 사고 — Omniverse Hub 락 fd 상속. run_260811_w3_batch2.sh 헤더 참조)
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

FILTERS=("$@")
should_run() {
  local k=$1
  [ ${#FILTERS[@]} -eq 0 ] && return 0
  for f in "${FILTERS[@]}"; do [ "$f" = "$k" ] && return 0; done
  return 1
}

run_one() {  # run_one <scene> <rel> <round> <extra env...>
  local n=$1 REL=$2 ROUND=$3; shift 3
  local LOG=look_check/logs/${ROUND}.log
  mkdir -p look_check/logs; touch "$LOG"
  local out=look_check/${n}/${ROUND}; mkdir -p "$out"
  python3 scripts/stamp_round.py --capture-env "$out" >> "$LOG" 2>&1
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR="$out" \
      NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
      "$@" \
      python scenes/${REL}.py >> "$LOG" 2>&1
  local rc=$?
  local cuts=$(ls "$out"/*.png 2>/dev/null | wc -l)
  echo "$n $ROUND cuts=$cuts rc=$rc" | tee -a "$LOG"
  python3 scripts/stamp_round.py "$out" "$ROUND" "$n" >> "$LOG" 2>&1
  echo "[$ROUND] done" | tee -a "$LOG"
}

should_run s16 && run_one scene16 main/scene16_canopy_shadow 260813_w4_s16tone
should_run s11 && run_one scene11 main/scene11_footbridge_stairs 260813_w4_s11tone
should_run s13 && run_one scene13 main/scene13_apartment_parking_entry 260813_w4_s13tone \
  NEGOBS_GLASS_FROST=1 NEGOBS_GLASS_MDL=glass
should_run s01 && run_one scene01 main/scene01_campus_stairs 260813_w4_s01k5
should_run n3  && run_one sceneN3 batch1/sceneN3_trompe_loeil 260813_w4_n3wall
should_run s15 && run_one scene15 main/scene15_alley_labyrinth 260813_w4_s15villa
should_run s21 && run_one scene21 main/scene21_monumental_selfocclude 260813_w4_s21civic
exit 0
