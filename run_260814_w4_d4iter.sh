#!/usr/bin/env bash
# 260814_w4_d4iter — GT-116 D4 광량 반복(패널 28000) 단독 재렌더
set -euo pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
    NEGOBS_PT_TOTAL_SPP=256 \
    NEGOBS_CAPTURE_DIR="look_check/sceneD4/260814_w4_d4iter" \
    python scenes/batch1/sceneD4_subway_platform.py 2>&1 | grep -E "캡처|룩v1" || true
python3 scripts/stamp_round.py look_check/sceneD4/260814_w4_d4iter 260814_w4_d4iter sceneD4 || true
