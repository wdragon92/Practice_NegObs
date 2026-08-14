#!/usr/bin/env bash
# 260815_w4_r4batch — GT-115 배치(수리 15씬) 시각 검증 + GT-118 turf 파일럿(s14·s21)
set -euo pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
R=260815_w4_r4batch
run_scene () {
  local d="$1" p="$2"
  echo "=== [r4batch] $d ==="
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_CAPTURE_DIR="look_check/$d/$R" \
      python "$p" 2>&1 | grep -E "룩v1|캡처 .*FAIL|Error|Traceback" || true
  python3 scripts/stamp_round.py "look_check/$d/$R" "$R" "$d" || true
}
run_scene scene05 scenes/main/scene05_amphitheater.py
run_scene scene08 scenes/main/scene08_sunken_plaza.py
run_scene scene09 scenes/main/scene09_ghat_riverfront.py
run_scene scene10 scenes/main/scene10_park_deck_switchback.py
run_scene scene12 scenes/main/scene12_riverside_deck.py
run_scene scene13 scenes/main/scene13_apartment_parking_entry.py
run_scene scene14 scenes/main/scene14_grandstair_illusion.py
run_scene scene16 scenes/main/scene16_canopy_shadow.py
run_scene scene17 scenes/main/scene17_ramp_pair_hangang.py
run_scene scene18 scenes/main/scene18_wavy_artstair.py
run_scene scene19 scenes/main/scene19_fan_winder.py
run_scene scene21 scenes/main/scene21_monumental_selfocclude.py
run_scene sceneC2 scenes/batch1/sceneC2_leaf_stairs.py
run_scene sceneC4 scenes/batch1/sceneC4_wet_stairs.py
run_scene sceneD1 scenes/batch1/sceneD1_loading_dock.py
run_scene sceneD2 scenes/batch1/sceneD2_floor_opening.py
run_scene sceneN1 scenes/batch1/sceneN1_shadow_band.py
echo "=== [r4batch] done ==="
