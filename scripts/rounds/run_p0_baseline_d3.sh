#!/usr/bin/env bash
# Phase 0 — sceneD3 기준선 PT 렌더 (배치1은 RT 판정만 있어 PT가 0장)
# 백그라운드 셸 cwd 리셋 함정 회피를 위해 cd 를 포함한 스크립트 파일로 실행할 것.
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

OUT=look_check/sceneD3/p0_base_pt
echo "=== [P0] sceneD3 PT 기준선 → ${OUT} ==="
date

NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt \
NEGOBS_CAPTURE_DIR="${OUT}" \
  python scenes/batch1/sceneD3_drainage_channel.py

echo "=== 완료 ==="
date
ls -la "${OUT}" | head -25
