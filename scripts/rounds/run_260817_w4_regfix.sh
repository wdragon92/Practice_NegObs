#!/usr/bin/env bash
# GT-129 회귀 수리 검증 라운드 — 5씬 (s03·s05·s06·s10·s15)
#
#   s04 는 사용자 지시로 GT-129 에서 제외됐다(최애 씬 수정 보류) — 렌더하지 않는다.
#
# 규약: GPU 배타·직렬 · PT-fast · 룩 v1 ON.
#
# **락은 씬 단위로 잡는다**(2026-08-16). 라운드 전체를 한 번에 잠그면 20~30분을
# 점유하는데, 사용자 작업은 `flock -w 55` 로 55초만 기다리고 exit 201 로 죽는다
# (실측: 00:18 env_seg 작업이 락 보유 중이었다). 씬마다 잡았다 놓으면 사용자 작업이
# 씬 사이 틈에 들어올 수 있다. 락을 60분 못 잡으면 그 씬은 건너뛰고 기록만 남긴다.
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

TAG="260817_w4_regfix"
SKIPPED=""
echo "########## GT-129 검증 라운드 ${TAG} (씬 단위 락) ##########"
date

render() {   # $1 씬경로  $2 씬키
  local scene="$1" key="$2" t0 t1 n rc
  t0=$(date +%s)
  # -w 3600: 사용자 작업이 길면 최대 1시간 대기 후 포기(건너뜀). nice 로 우선순위 양보.
  flock -o -w 3600 -E 201 /tmp/negobs_gpu.lock \
    nice -n 5 env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_CAPTURE_DIR="look_check/${key}/${TAG}" \
    python "${scene}" > "/tmp/negobs_${TAG}_${key}.log" 2>&1
  rc=$?
  t1=$(date +%s)
  if [ "$rc" = "201" ]; then
    echo "${key}: 락 획득 실패(1시간) — 건너뜀"; SKIPPED="${SKIPPED} ${key}"; return
  fi
  n=$(ls "look_check/${key}/${TAG}"/pt_*.png 2>/dev/null | wc -l)
  printf "%-10s %3d컷  %4ds  rc=%s\n" "${key}" "${n}" "$((t1-t0))" "${rc}"
  python3 scripts/stamp_round.py "look_check/${key}/${TAG}" "${TAG}" "${key}" || true
}

render scenes/main/scene03_riverbank.py                scene03
render scenes/main/scene05_amphitheater.py             scene05
render scenes/main/scene06_overpass_spiral.py          scene06
render scenes/main/scene10_park_deck_switchback.py     scene10
render scenes/main/scene15_alley_labyrinth.py          scene15

echo "건너뛴 씬:${SKIPPED:- 없음}"
echo "=== ${TAG} 렌더+스탬프 완료 ==="
date
