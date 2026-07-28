#!/usr/bin/env bash
# Phase 1 — 검증의 날 스파이크 랩 (부팅 1회로 E1~E7 전부)
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

echo "=== [P1] 스파이크 랩 시작 ==="; date
python scripts/spike_realism.py "$@"
echo "=== [P1] 종료 ==="; date
