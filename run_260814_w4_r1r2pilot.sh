#!/usr/bin/env bash
# 260814_w4_r1r2pilot — GT-113(R1 배선)+GT-114(R2 클래스) 파일럿 5씬 판정 렌더
# s13(asphalt macro_wl·카펫 트랙) · s16(paving/nosing/curb/metal) · s21(unit_cell
# 파일럿+테라스) · C1(snow 밴드) · D4(W7 발광·metal·조명 최악 씬 현황 기록용).
# PT-fast 전 컷. baseline = 각 씬 최신 라운드(회귀는 선언 변화 귀속 예정).
set -euo pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1

R=260814_w4_r1r2pilot
run_scene () {  # dir, scene.py
  local scdir="$1" scpy="$2"
  echo "=== [r1r2pilot] $scdir ==="
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_CAPTURE_DIR="look_check/$scdir/$R" \
      python "$scpy" 2>&1 | grep -E "룩v1|캡처|unit_cell|배선|Error|Traceback" || true
  python3 scripts/stamp_round.py "look_check/$scdir/$R" "$R" "$scdir" || true
}

run_scene scene13 scenes/main/scene13_apartment_parking_entry.py
run_scene scene16 scenes/main/scene16_canopy_shadow.py
run_scene scene21 scenes/main/scene21_monumental_selfocclude.py
run_scene sceneC1 scenes/batch1/sceneC1_snow_stairs.py
run_scene sceneD4 scenes/batch1/sceneD4_subway_platform.py
echo "=== [r1r2pilot] done ==="
