#!/usr/bin/env bash
# rescore_final_rows.sh — closes the last 구 GT rows (§6.4 items 1-2):
#   (a) YOLO 3런  (yolo_s{42,43,44})   — det2cell adapter path
#   (b) rgb_s42_aux                     — standard eval_polar path
#
# (a) YOLO — the published path is NOT a forward pass. run_yolo_all.sh does
#       train -> predict(dump txt labels) -> det2cell.py -> eval_polar --per-frame-a
#     The detections are already frozen on disk (runs/yolo_s*/pred_test/labels), and the
#     MANIFEST enters only at the det2cell step (GT g_* columns + cam poses for the ground
#     projection). So the corrected-GT rescore re-runs det2cell + eval_polar ONLY, is
#     CPU-only, and touches no detector weights.  cam.* is byte-identical between the two
#     manifests, so p_* must come out unchanged — that is the gate.
#     Published invocation replicated verbatim from code/run_yolo_all.sh:20-23 except
#     --manifest.  tau_op = 0.25 (verified: runs/yolo_s42/eval_test/metrics.json).
#     NOTE the published YOLO steps deliberately take NO GPU lock (they are numpy-only);
#     we replicate that, which is also the polite thing to do next to the scene builder.
#
# (b) rgb_s42_aux — resnet34+aux ckpt, GPU forward pass, so this one DOES take the lock.
#     Published invocation from code/run_aux.sh:148-149 except --manifest and --tau-star
#     (auto -> the frozen published value 0.43; no re-fitting, same rule as §0/§7).
#
# Resume-safe; markers: eval_v2corr/<run>/DONE, eval_v2corr/FINAL_DONE.
set -u -o pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
MAIN=$REPO/experiments/mainrun_0819
DAY=$REPO/experiments/dayrun_0820
V3=$REPO/experiments/v3_0823
CODE=$MAIN/code
MANIFEST=$V3/dataset_manifest_v2corr.json
SPLIT=$DAY/split_v2_full.json
GRIDFILE=$MAIN/code/labeling/gridspec_v1.json
OUT=$V3/eval_v2corr
LOCK=/tmp/negobs_gpu.lock

YPY=$DAY/venv_yolo/bin/python                              # ultralytics venv (det2cell)
PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"

mkdir -p "$OUT" "$OUT/logs"
QLOG=$OUT/logs/rescore_final.log
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$QLOG"; }

say "=== rescore_final_rows start ==="
FAILED=""

# ---------------------------------------------------------------- (a) YOLO x3
for S in 42 43 44; do
  RUN=yolo_s$S
  EV=$OUT/$RUN
  LOG=$OUT/logs/$RUN.log
  W=$DAY/runs/$RUN/weights/best.pt
  P=$DAY/runs/$RUN/pred_test/labels
  if [ -f "$EV/metrics.json" ]; then say "[skip] $RUN already done"; touch "$EV/DONE"; continue; fi
  if [ ! -f "$W" ]; then
    say "[MISSING] $RUN: $W absent (AGPL untrack policy?) -- NOT retraining"
    FAILED="$FAILED $RUN:no-weights"; continue
  fi
  if [ ! -d "$P" ]; then
    say "[MISSING] $RUN: frozen predictions $P absent -- would need a GPU predict pass; stopping this run"
    FAILED="$FAILED $RUN:no-preds"; continue
  fi
  mkdir -p "$EV/cells_test"
  say "[cpu]  det2cell $RUN (corrected manifest)"
  if ! env PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= "$YPY" "$DAY/code/yolo/det2cell.py" \
        --pred-labels "$P" --split "$SPLIT" --subset test --manifest "$MANIFEST" \
        --grid "$GRIDFILE" --conf 0.05 --out "$EV/cells_test" >>"$LOG" 2>&1; then
    say "[FAIL] det2cell $RUN -- see $LOG"; FAILED="$FAILED $RUN:det2cell"; continue
  fi
  say "[cpu]  eval $RUN (tau_op 0.25)"
  if ! env PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= $PYBIN "$CODE/eval_polar.py" \
        --per-frame-a "$EV/cells_test/per_frame.csv" --grid "$GRIDFILE" --out "$EV" \
        --tau-op 0.25 --tau-sweep 0.1,0.25,0.5 >>"$LOG" 2>&1; then
    say "[FAIL] eval $RUN -- see $LOG"; FAILED="$FAILED $RUN:eval"; continue
  fi
  tail -n 1 "$LOG" | sed 's/^/        /' | tee -a "$QLOG"
  touch "$EV/DONE"; say "[ok]   $RUN"
done

# ---------------------------------------------------------------- (b) rgb_s42_aux
RUN=rgb_s42_aux
EV=$OUT/$RUN
LOG=$OUT/logs/$RUN.log
CK=$DAY/runs/v2/$RUN/best.pt
if [ -f "$EV/metrics.json" ]; then
  say "[skip] $RUN already done"; touch "$EV/DONE"
elif [ ! -f "$CK" ]; then
  say "[MISSING] $RUN: $CK absent -- NOT retraining"; FAILED="$FAILED $RUN:no-weights"
else
  mkdir -p "$EV"
  CMD="$PY $CODE/eval_polar.py --input rgb --manifest '$MANIFEST' --split '$SPLIT' --subset test \
--ckpt '$CK' --out '$EV' --tau-op 0.5 --tau-star 0.43 --tau-sweep 0.3,0.5,0.7 --n-boot 10000 \
--grid gridspec_v1.json"
  echo "CMD: $CMD" >>"$LOG"
  try=0
  while : ; do
    try=$((try + 1))
    say "[lock] eval $RUN (tau*=0.43 · try $try/24)"
    flock -o -w 600 -E 201 "$LOCK" nice -n 5 bash -c "$CMD" >>"$LOG" 2>&1
    rc=$?
    case $rc in
      0)   say "[ok]   $RUN"; tail -n 2 "$LOG" | sed 's/^/        /' | tee -a "$QLOG"
           touch "$EV/DONE"; break ;;
      201) if [ "$try" -ge 24 ]; then say "[busy] $RUN gave up"; FAILED="$FAILED $RUN:busy"; break; fi
           say "[busy] GPU lock held elsewhere -- retrying"; sleep 20 ;;
      202) if [ "$try" -ge 24 ]; then say "[full] $RUN gave up"; FAILED="$FAILED $RUN:vram"; break; fi
           say "[full] <6 GB free -- backing off 60 s"; sleep 60 ;;
      *)   say "[FAIL] $RUN exited $rc -- see $LOG"; FAILED="$FAILED $RUN:rc$rc"; break ;;
    esac
  done
fi

say "=== rescore_final_rows done ==="
if [ -n "$FAILED" ]; then say "FAILED:$FAILED"; echo "FAILED:$FAILED" > "$OUT/FINAL_DONE"; exit 1; fi
date +%s > "$OUT/FINAL_DONE"
say "FINAL_DONE written"
