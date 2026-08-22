#!/usr/bin/env bash
# GPU-3 / WEEKEND_BRIEF_0823 §6.4 — evaluate the fused row. CPU ONLY (no GPU lock needed:
# every input is a stored per_frame.csv and eval_polar with --per-frame-a runs no model).
#
# Flags are copied verbatim from the main table's own runs so the fused row is table-comparable:
#   eval_polar : --grid gridspec_v1.json --tau-op 0.5 --tau-star 0.5 --n-boot 10000 (seed 42)
#   twin       : --grid gridspec_v1.json --manifest dataset_manifest_v2_full.json --tol 0.15
#                --pose-keys d,h_rel,yaw,pitch,ground_z (default) --n-boot 10000
# (source of those flags: experiments/dayrun_0820/code/run_aux.sh and the header of
#  experiments/dayrun_0820/runs/v2/rgb_s42/twin/twin_analysis.md)
#
# tau_star is pinned to 0.5 rather than 'auto': 'auto' would refit on a val forward pass, which a
# --per-frame-a run cannot do, and the fused row's operating point is fixed by construction.
set -euo pipefail

ROOT=/home/vislab/Desktop/work_sy/Practice_NegObs
MAIN=$ROOT/experiments/mainrun_0819/code
DAY=$ROOT/experiments/dayrun_0820
FUS=$ROOT/experiments/weekend_0823/fusion
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES= \
/home/vislab/miniconda3/envs/env_seg/bin/python"
GRID=gridspec_v1.json
MANIFEST=$DAY/dataset_manifest_v2_full.json
NBOOT=10000

for S in 42 43 44; do
  for TAG in fused_or fused_max; do
    D=$FUS/s$S/$TAG
    echo "=== seed $S / $TAG ==="
    $PY $MAIN/eval_polar.py --per-frame-a "$D/per_frame.csv" --out "$D/eval_test" \
        --tau-op 0.5 --tau-star 0.5 --tau-sweep 0.3,0.5,0.7 --n-boot $NBOOT --grid $GRID
    $PY $MAIN/split_per_frame.py --per-frame "$D/eval_test/per_frame.csv" --out-dir "$D/eval_test"
    $PY $MAIN/twin_analysis.py --per-frame-on "$D/eval_test/per_frame_on.csv" \
        --per-frame-off "$D/eval_test/per_frame_off.csv" --manifest "$MANIFEST" \
        --out "$D/twin" --n-boot $NBOOT --grid $GRID --tol 0.15
  done
done
echo "=== done ==="
