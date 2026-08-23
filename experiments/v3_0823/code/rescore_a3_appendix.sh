#!/usr/bin/env bash
# rescore_a3_appendix.sh — A-3 (D69): rescore the 6 APPENDIX-encoder runs on the G7-corrected GT.
#
# Runs: resnet50_s{42,43,44} · tu-convnext_tiny_s{42,43,44}
#       (weights: experiments/weekend_0823/newmodels/runs/<run>/best.pt)
#
# Replicates the published appendix invocation from weekend_0823/code/run_newmodels.sh:93-94
# verbatim, changing ONLY:
#   --manifest  dayrun_0820/dataset_manifest_v2_full.json -> v3_0823/dataset_manifest_v2corr.json
#   --tau-star  auto (val re-fit) -> the FROZEN per-run published value (no re-fitting)
# Identical otherwise: same split_v2_full.json, --subset test, --input rgb, --tau-op 0.5,
# --tau-sweep 0.3,0.5,0.7, --grid gridspec_v1.json, n-boot = eval_polar default (10000), and
# NO --encoder flag: eval_polar rebuilds the backbone from the ckpt's config["encoder"] (D45).
#
# Polite interleave (D69 A-3): the scene-builder takes the GPU in short bursts, so each
# invocation takes the lock with a bounded wait and retries on 201 (busy) / 202 (<6 GB free).
# Resume-safe: skip a run whose eval_v2corr/<run>/metrics.json already exists.
# Markers: eval_v2corr/<run>/DONE per run, eval_v2corr/A3_DONE at the end.
set -u -o pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
MAIN=$REPO/experiments/mainrun_0819
DAY=$REPO/experiments/dayrun_0820
V3=$REPO/experiments/v3_0823
NM=$REPO/experiments/weekend_0823/newmodels/runs
CODE=$MAIN/code
MANIFEST=$V3/dataset_manifest_v2corr.json
SPLIT=$DAY/split_v2_full.json
OUT=$V3/eval_v2corr
GRID=gridspec_v1.json
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=600
LOCK_TRIES=24

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"

mkdir -p "$OUT" "$OUT/logs"
QLOG=$OUT/logs/rescore_a3.log
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$QLOG"; }

# name:tau_star  (FROZEN published value from newmodels/runs/<name>/eval_test/metrics.json)
JOBS="resnet50_s42:0.72 resnet50_s43:0.36 resnet50_s44:0.58 \
tu-convnext_tiny_s42:0.31 tu-convnext_tiny_s43:0.3 tu-convnext_tiny_s44:0.33"

say "=== rescore_a3_appendix start ==="
say "manifest=$MANIFEST split=$SPLIT out=$OUT grid=$GRID tau_op=0.5 (encoder read from ckpt)"
FAILED=""

for J in $JOBS; do
  NAME=${J%%:*}; TAUSTAR=${J##*:}
  EV=$OUT/$NAME
  LOG=$OUT/logs/$NAME.log
  mkdir -p "$EV"
  if [ -f "$EV/metrics.json" ]; then
    say "[skip] $NAME: metrics.json already present"; touch "$EV/DONE"; continue
  fi
  if [ ! -f "$NM/$NAME/best.pt" ]; then
    say "[MISSING] $NAME: $NM/$NAME/best.pt not on disk -- NOT retraining (policy)"
    FAILED="$FAILED $NAME:no-weights"; continue
  fi
  CMD="$PY $CODE/eval_polar.py --manifest '$MANIFEST' --split '$SPLIT' --subset test \
--input rgb --ckpt '$NM/$NAME/best.pt' --out '$EV' --tau-op 0.5 --tau-star $TAUSTAR \
--tau-sweep 0.3,0.5,0.7 --grid $GRID"
  echo "CMD: $CMD" >>"$LOG"
  try=0
  while : ; do
    try=$((try + 1))
    say "[lock] eval $NAME (tau*=$TAUSTAR · try $try/$LOCK_TRIES)"
    flock -o -w "$LOCK_WAIT" -E 201 "$LOCK" nice -n 5 bash -c "$CMD" >>"$LOG" 2>&1
    rc=$?
    case $rc in
      0)   say "[ok]   $NAME"; tail -n 2 "$LOG" | sed 's/^/        /' | tee -a "$QLOG"
           touch "$EV/DONE"; break ;;
      201) if [ "$try" -ge "$LOCK_TRIES" ]; then say "[busy] $NAME gave up"; FAILED="$FAILED $NAME:busy"; break; fi
           say "[busy] GPU lock held elsewhere (scene builder?) -- retrying"; sleep 20 ;;
      202) if [ "$try" -ge "$LOCK_TRIES" ]; then say "[full] $NAME gave up"; FAILED="$FAILED $NAME:vram"; break; fi
           say "[full] <6 GB free -- backing off 60 s"; sleep 60 ;;
      *)   say "[FAIL] $NAME exited $rc -- see $LOG"; FAILED="$FAILED $NAME:rc$rc"; break ;;
    esac
  done
done

say "=== rescore_a3_appendix done ==="
if [ -n "$FAILED" ]; then say "FAILED:$FAILED"; echo "FAILED:$FAILED" > "$OUT/A3_DONE"; exit 1; fi
date +%s > "$OUT/A3_DONE"
say "A3_DONE written"
