#!/usr/bin/env bash
# GT-125 physics-value pilot: 3 scenes with NEGOBS_PHYS_V1=1 (A/B vs latest baselines)
# + hard-negative data extension for r_pb over the data role (N1,N2,N3 into 260815_datapilot).
set -euo pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
R=260815_w4_physpilot
run_scene () {
  local d="$1" p="$2"
  echo "=== [physpilot] $d ==="
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_PHYS_V1=1 NEGOBS_CAPTURE_DIR="look_check/$d/$R" \
      python "$p" 2>&1 | grep -E "캡처 .*FAIL|Traceback|룩v1" || true
  python3 scripts/stamp_round.py "look_check/$d/$R" "$R" "$d" || true
}
run_scene scene13 scenes/main/scene13_apartment_parking_entry.py
run_scene scene16 scenes/main/scene16_canopy_shadow.py
run_scene scene03 scenes/main/scene03_riverbank.py
echo "=== [physpilot] done ==="
# --- hard-negative data extension (same run id => r_pb over drop+nondrop) ---
python scripts/run_data_render.py --run 260815_datapilot --scenes sceneN1,sceneN2,sceneN3 \
  --conds L0,L2,L7 --cams 8 --seed 20260815 2>&1 | tail -8
python3 scripts/sensor_augment.py --in dataset/260815_datapilot --out dataset/260815_datapilot_aug --seed 3 2>&1 | tail -2
python3 scripts/shortcut_audit.py --data dataset/260815_datapilot 2>&1 | tail -8
echo "=== [physpilot+dataext] done ==="
