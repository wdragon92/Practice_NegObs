#!/usr/bin/env bash
# rescore_v2corr.sh — P-2 follow-up (DZ §12-1): rescore the 9 published v2 checkpoints on the
# G7-corrected GT manifest (canonical B).
#
# Replicates the PUBLISHED eval invocation from mainrun_0819/code/run_queue_v2.sh verbatim,
# changing ONLY:
#   --manifest  dayrun_0820/dataset_manifest_v2_full.json -> v3_0823/dataset_manifest_v2corr.json
#   --tau-star  auto (val re-fit) -> the FROZEN per-run published value (mandate: do not re-fit)
# Everything else identical: same split_v2_full.json, --subset test, --tau-op 0.5,
# --tau-sweep 0.3,0.5,0.7, --n-boot 10000, --grid gridspec_v1.json, same eval entry point
# (eval_polar.py for rgb/depth, b2_polar/eval_b2_polar.py for b2).
#
# Resume-safe: a checkpoint whose eval_v2corr/<name>/metrics.json already exists is skipped.
# Markers: eval_v2corr/<name>/DONE per checkpoint, eval_v2corr/ALL_DONE at the end.
set -u -o pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
MAIN=$REPO/experiments/mainrun_0819
DAY=$REPO/experiments/dayrun_0820
V3=$REPO/experiments/v3_0823
CODE=$MAIN/code
MANIFEST=$V3/dataset_manifest_v2corr.json
SPLIT=$DAY/split_v2_full.json
RUNS=$DAY/runs/v2
OUT=$V3/eval_v2corr
GRID=gridspec_v1.json
NBOOT=10000
LOCK=/tmp/negobs_gpu.lock

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
PY_B2="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 $PYBIN"

mkdir -p "$OUT" "$OUT/logs"
QLOG=$OUT/logs/rescore.log
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$QLOG"; }

# name:input:tau_star  (tau_star = the FROZEN published value from
#   dayrun_0820/runs/v2/<name>/eval_test/metrics.json)
JOBS="rgb_s42:rgb:0.63 rgb_s43:rgb:0.71 rgb_s44:rgb:0.31 \
depth_s42:depth:0.36 depth_s43:depth:0.21 depth_s44:depth:0.6 \
b2_s42:rgb:0.45 b2_s43:rgb:0.45 b2_s44:rgb:0.45"

say "=== rescore_v2corr start ==="
say "manifest=$MANIFEST split=$SPLIT out=$OUT grid=$GRID nboot=$NBOOT tau_op=0.5"
FAILED=""

for J in $JOBS; do
  NAME=${J%%:*}; REST=${J#*:}; INPUT=${REST%%:*}; TAUSTAR=${REST##*:}
  EV=$OUT/$NAME
  LOG=$OUT/logs/$NAME.log
  mkdir -p "$EV"
  if [ -f "$EV/metrics.json" ]; then
    say "[skip] $NAME: metrics.json already present"
    touch "$EV/DONE"; continue
  fi
  case "$NAME" in
    b2_*) EVAL="$PY_B2 $MAIN/b2_polar/eval_b2_polar.py --input $INPUT --route auto" ;;
    *)    EVAL="$PY $CODE/eval_polar.py --input $INPUT" ;;
  esac
  CMD="$EVAL --manifest '$MANIFEST' --split '$SPLIT' --subset test --ckpt '$RUNS/$NAME/best.pt' \
--out '$EV' --tau-op 0.5 --tau-star $TAUSTAR --tau-sweep 0.3,0.5,0.7 --n-boot $NBOOT --grid $GRID"
  say "[lock] eval $NAME (input=$INPUT tau*=$TAUSTAR)"
  echo "CMD: $CMD" >>"$LOG"
  if flock -o -w 3600 -E 201 "$LOCK" nice -n 5 bash -c "$CMD" >>"$LOG" 2>&1; then
    say "[ok]   $NAME"
    tail -n 2 "$LOG" | sed 's/^/        /' | tee -a "$QLOG"
    touch "$EV/DONE"
  else
    rc=$?
    say "[FAIL] $NAME exited $rc -- see $LOG"
    FAILED="$FAILED $NAME"
  fi
done

# ---- CPU post-step: on/off halves of each per_frame.csv (same tool as the published queue) ----
for J in $JOBS; do
  NAME=${J%%:*}; EV=$OUT/$NAME
  if [ -f "$EV/per_frame.csv" ] && [ ! -f "$EV/per_frame_off.csv" ]; then
    env CUDA_VISIBLE_DEVICES="" $PY $CODE/split_per_frame.py --per-frame "$EV/per_frame.csv" \
        --out-dir "$EV" >>"$OUT/logs/$NAME.log" 2>&1 || FAILED="$FAILED $NAME:split_pf"
  fi
done

say "=== rescore_v2corr done ==="
if [ -n "$FAILED" ]; then say "FAILED:$FAILED"; echo "FAILED:$FAILED" > "$OUT/ALL_DONE"; exit 1; fi
date +%s > "$OUT/ALL_DONE"
say "ALL_DONE written"
