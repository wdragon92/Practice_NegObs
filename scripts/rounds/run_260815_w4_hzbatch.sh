#!/usr/bin/env bash
# 260815_w4_hzbatch — GT-119(hazard 6건)·121·122·123 검증 렌더 13씬
set -euo pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
R=260815_w4_hzbatch
run_scene () {
  local d="$1" p="$2"
  echo "=== [hzbatch] $d ==="
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_CAPTURE_DIR="look_check/$d/$R" \
      python "$p" 2>&1 | grep -E "캡처 .*FAIL|Traceback|GT-120|GT-119" || true
  python3 scripts/stamp_round.py "look_check/$d/$R" "$R" "$d" || true
}
run_scene scene02 scenes/main/scene02_underpass.py
run_scene scene03 scenes/main/scene03_riverbank.py
run_scene scene08 scenes/main/scene08_sunken_plaza.py
run_scene scene10 scenes/main/scene10_park_deck_switchback.py
run_scene scene15 scenes/main/scene15_alley_labyrinth.py
run_scene scene16 scenes/main/scene16_canopy_shadow.py
run_scene scene17 scenes/main/scene17_ramp_pair_hangang.py
run_scene scene21 scenes/main/scene21_monumental_selfocclude.py
run_scene sceneC1 scenes/batch1/sceneC1_snow_stairs.py
run_scene sceneD4 scenes/batch1/sceneD4_subway_platform.py
run_scene sceneN1 scenes/batch1/sceneN1_shadow_band.py
run_scene sceneN2 scenes/batch1/sceneN2_asphalt_patch.py
run_scene sceneN3 scenes/batch1/sceneN3_trompe_loeil.py
echo "=== [hzbatch] done ==="
