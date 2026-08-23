#!/usr/bin/env bash
# rescore_twin.sh — CPU-only twin re-analysis on the G7-corrected dumps.
# Same tool + same flags as the published queue (run_queue_v2.sh), only the manifest and the
# per_frame dumps change:  --manifest -> v3_0823/dataset_manifest_v2corr.json
#                          --per-frame-{on,off} -> v3_0823/eval_v2corr/<run>/per_frame_{on,off}.csv
# No GPU: twin_analysis.py is numpy over the frozen probability dumps.
set -u -o pipefail
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
CODE=$REPO/experiments/mainrun_0819/code
V3=$REPO/experiments/v3_0823
OUT=$V3/eval_v2corr
MANIFEST=$V3/dataset_manifest_v2corr.json
PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env CUDA_VISIBLE_DEVICES= PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
for RUN in rgb_s42 rgb_s43 rgb_s44 depth_s42 depth_s43 depth_s44 b2_s42 b2_s43 b2_s44; do
  EV=$OUT/$RUN
  [ -f "$EV/twin/twin_analysis.md" ] && { echo "[skip] $RUN twin"; continue; }
  $PY $CODE/twin_analysis.py --per-frame-on "$EV/per_frame_on.csv" \
      --per-frame-off "$EV/per_frame_off.csv" --manifest "$MANIFEST" --out "$EV/twin" \
      --n-boot 10000 --grid gridspec_v1.json --tol 0.15 2>&1 | tail -1
done
touch "$OUT/TWIN_DONE"
echo "TWIN_DONE"
