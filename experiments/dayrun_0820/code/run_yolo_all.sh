#!/bin/bash
# YOLO track: 3 seeds train -> predict(test,val) -> det2cell -> eval, under flock.
set -u -o pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820
PY=venv_yolo/bin/python
EPY=/home/vislab/miniconda3/envs/env_seg/bin/python
export PYTHONNOUSERSITE=1
L=/tmp/negobs_gpu.lock
for S in 42 43 44; do
  if [ ! -f runs/yolo_s$S/weights/best.pt ]; then
    flock -o -w 3600 -E 201 "$L" $PY code/yolo/train_yolo.py --mode train --seed $S --device 0 || { echo "[yolo] train s$S FAILED"; exit 1; }
  else
    echo "[yolo] train s$S skipped (best.pt exists)"
  fi
  for SUB in test val; do
    if [ ! -d runs/yolo_s$S/pred_$SUB/labels ]; then
      flock -o -w 3600 -E 201 "$L" $PY code/yolo/train_yolo.py --mode predict --seed $S --device 0 --subset $SUB --pred-conf 0.05 || exit 1
    else
      echo "[yolo] predict s$S $SUB skipped"
    fi
    $PY code/yolo/det2cell.py --pred-labels runs/yolo_s$S/pred_$SUB/labels --split split_v2_full.json --subset $SUB --manifest dataset_manifest_v2_full.json --grid ../mainrun_0819/code/labeling/gridspec_v1.json --conf 0.05 --out runs/yolo_s$S/cells_$SUB || exit 1
  done
  $EPY ../mainrun_0819/code/eval_polar.py --per-frame-a runs/yolo_s$S/cells_test/per_frame.csv --grid ../mainrun_0819/code/labeling/gridspec_v1.json --out runs/yolo_s$S/eval_test --tau-op 0.25 --tau-sweep 0.1,0.25,0.5 || exit 1
  echo "[yolo] seed $S complete"
done
echo "[yolo] all seeds done"
