#!/bin/bash
# 08-11 갤러리 회신 배치 2 — GT-104/105/106/107 + GT-73 frosted 자연화 팔.
#   s11clean   GT-105(하강 가드 중간 가로대 소거) + GT-107 파일럿(데칼 정온)
#   s06bay14   GT-104(데크 판폭 재모듈: 에이프런 3 + 필드 12)
#   s13frost_c/d/e  GT-73 frosted 자연화 — 유백 0.90 고정 × rough 0.35/0.22/0.50
#   s16under   GT-106(포털 데크 연장·헤드월·지하보도 표지·통로 조명 5등)
# 사용: flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260811_w3_batch2.sh [필터...]
#   필터 = s11 s06 s13 s16 중 부분집합(무인자 = 전부). GT-107 은 공유 킷이므로
#   §2.3 에 따라 s11 을 먼저 단독 실행해 육안 후 나머지를 돌린다.
#   ** -o 필수 ** — 08-11 실사고: -o 없이 걸면 Isaac 부팅이 띄우는 Omniverse Hub
#   데몬이 락 fd 를 상속·보유해 렌더 종료 후에도 락이 풀리지 않는다(대기열 기아).
#   -o(--close) 는 자식 실행 전에 락 fd 를 닫아 상속을 차단한다.
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

should_run s11 && run_one scene11 main/scene11_footbridge_stairs 260811_w3_s11clean
should_run s06 && run_one scene06 main/scene06_overpass_spiral 260811_w3_s06bay14
if should_run s13; then
  run_one scene13 main/scene13_apartment_parking_entry 260811_w3_s13frost_c \
    NEGOBS_GLASS_FROST=1 NEGOBS_GLASS_MDL=glass
  run_one scene13 main/scene13_apartment_parking_entry 260811_w3_s13frost_d \
    NEGOBS_GLASS_FROST=1 NEGOBS_GLASS_MDL=glass NEGOBS_GLASS_FROST_ROUGH=0.22
  run_one scene13 main/scene13_apartment_parking_entry 260811_w3_s13frost_e \
    NEGOBS_GLASS_FROST=1 NEGOBS_GLASS_MDL=glass NEGOBS_GLASS_FROST_ROUGH=0.50
fi
should_run s16 && run_one scene16 main/scene16_canopy_shadow 260811_w3_s16under
exit 0
