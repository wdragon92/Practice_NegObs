#!/usr/bin/env bash
# GT-129 회귀 수리 검증 라운드 — 5씬 (s03·s05·s06·s10·s15)
#
#   s04 는 사용자 지시로 GT-129 에서 제외됐다(최애 씬 수정 보류) — 렌더하지 않는다.
#
# 규약: GPU 배타(flock -o) · 직렬 · PT-fast · 룩 v1 ON.
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

TAG="260817_w4_regfix"
echo "########## GT-129 검증 라운드 ${TAG} ##########"
date

render() {   # $1 씬경로  $2 씬키
  local scene="$1" key="$2" t0 t1 n
  t0=$(date +%s)
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_CAPTURE_DIR="look_check/${key}/${TAG}" \
    python "${scene}" > "/tmp/negobs_${TAG}_${key}.log" 2>&1
  t1=$(date +%s)
  n=$(ls "look_check/${key}/${TAG}"/pt_*.png 2>/dev/null | wc -l)
  printf "%-10s %3d컷  %4ds\n" "${key}" "${n}" "$((t1-t0))"
  python3 scripts/stamp_round.py "look_check/${key}/${TAG}" "${TAG}" "${key}" || true
}

render scenes/main/scene03_riverbank.py                scene03
render scenes/main/scene05_amphitheater.py             scene05
render scenes/main/scene06_overpass_spiral.py          scene06
render scenes/main/scene10_park_deck_switchback.py     scene10
render scenes/main/scene15_alley_labyrinth.py          scene15

echo "=== ${TAG} 렌더+스탬프 완료 ==="
date
