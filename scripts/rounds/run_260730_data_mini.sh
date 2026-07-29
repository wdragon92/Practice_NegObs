#!/bin/bash
# =============================================================================
# Mini data-run validation — lighting/camera round (run = 260730_data_mini)
#
#   3 scenes, one per MEASURED azimuth class (SP-2, spike §1.5):
#       sceneN1  S   daz 0    label IS the shadow
#       scene02  A'  daz 10 judge / 35 data
#       sceneN4  B'  daz 20 judge / 35 data
#   x 3 conditions: L0 ref + L7 overcast (sunless) + L5 low_sun (19.08 deg)
#   x 8 random cameras = 72 planned.
#
#   sceneN1 x L5 is REFUSED by design and that refusal is part of what this run
#   validates: L5 needs |Dz| >= 36.9 deg to be an honest Seoul sun (D6) and
#   sceneN1 allows 0. The 8 cuts are given to L1 cumulus instead, declared
#   explicitly here rather than substituted silently inside the driver.
#
#   Output: dataset/260730_data_mini/<split>/<scene>/ — never look_check/.
#   GPU exclusive, sequential, single instance.
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

RUN=260730_data_mini
LOG=look_check/logs/${RUN}.log
mkdir -p look_check/logs
: > $LOG

python3 scripts/run_data_render.py --run $RUN \
    --scenes sceneN1,scene02,sceneN4 --conds L0,L7,L5 --cams 8 \
    --seed 20260730 2>&1 | tee -a $LOG

# The declared substitution for the refused pair.
python3 scripts/run_data_render.py --run $RUN \
    --scenes sceneN1 --conds L1 --cams 8 \
    --seed 20260730 2>&1 | tee -a $LOG

python3 scripts/stamp_round.py dataset/${RUN} $RUN mini 2>&1 | tee -a $LOG
echo "[$RUN] done" | tee -a $LOG
