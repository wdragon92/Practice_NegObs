#!/usr/bin/env bash
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
python scripts/rtx_probe.py
