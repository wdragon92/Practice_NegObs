#!/usr/bin/env bash
# w3_all.sh -- re-run the whole W3 chain idempotently.  Every step overwrites in place.
#   dataset ~15 s | train ~2 min (GPU) | infer ~25 s (GPU) | curves/samples/contrast a few s
# GPU steps take the project lock.  The paper-weights smoke arm needs neg_env (torch 2.5.1);
# everything else runs in vth/venv.
set -euo pipefail
V=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/e1_0827/vth
PY="env PYTHONNOUSERSITE=1 $V/venv/bin/python"
NEG="env PYTHONNOUSERSITE=1 /home/vislab/Desktop/work_sy/Baseline_NegObs/neg_env/bin/python"
PAPER_W=/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/bot_camera/model/best.pt
cd "$V"
bash tools/verify_baseline.sh | tail -3
$PY tools/w3_dataset.py
flock -o /tmp/negobs_gpu.lock $PY tools/w3_train.py 2>&1 | tail -30
flock -o /tmp/negobs_gpu.lock $PY tools/w3_infer.py \
     --weights runs/w3_train/replica/weights/best.pt --out runs/yolo_replica | tail -2
flock -o /tmp/negobs_gpu.lock $PY tools/w3_smoke.py \
     --weights runs/w3_train/replica/weights/best.pt --tag replica
flock -o /tmp/negobs_gpu.lock $NEG tools/w3_smoke.py --weights "$PAPER_W" --tag paper
$PY tools/w3_contrast.py
$PY tools/w3_smoke_report.py
$PY tools/w3_curves.py > /dev/null
$PY tools/w3_samples.py
bash tools/verify_baseline.sh | tail -3
echo "W3 chain done -- see VTH_REPORT.md, runs/w3_tables.md, plots/w3_*.png"
