#!/usr/bin/env bash
# GT-127 micro-octave pilot: 3 scenes, NEGOBS_MICRO_V1=1 (A/B vs final33 baselines)
set -euo pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
R=260816_w4_micropilot
run_scene () {
  local d="$1" p="$2"
  echo "=== [micropilot] $d ==="
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_MICRO_V1=1 NEGOBS_CAPTURE_DIR="look_check/$d/$R" \
      python "$p" 2>&1 | grep -E "캡처 .*FAIL|Traceback|룩v1" || true
  python3 scripts/stamp_round.py "look_check/$d/$R" "$R" "$d" || true
}
run_scene scene13 scenes/main/scene13_apartment_parking_entry.py
run_scene scene16 scenes/main/scene16_canopy_shadow.py
run_scene scene03 scenes/main/scene03_riverbank.py
echo "=== [micropilot] done ==="
