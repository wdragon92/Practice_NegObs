#!/bin/bash
# run_newmodels.sh — D45 new-models queue: ENCODER AXIS ONLY, recipe v2, grid V1, RGB, 3 seeds.
#
#   tmux new -s newmodels 'bash experiments/weekend_0823/code/run_newmodels.sh 2>&1 \
#       | tee experiments/weekend_0823/newmodels/queue.log'
#
# 6 runs = {tu-convnext_tiny, resnet50} x {42,43,44}. Everything except --encoder is byte-identical
# to the v2 U-Net recipe (lr 3e-4, batch 8, 150 ep, patience 15, hflip on, oversample-h 4,
# bias-init prior, grid V1, n-boot 10000 = eval_polar's default) so the comparison isolates one
# variable. DLv3+ is deliberately absent: a decoder change would confound the encoder effect.
#
# ABORT-SAFE / resumable: a run with eval_test/metrics.json is skipped; a run with best.pt but no
# eval re-runs only the eval. Re-running the script resumes.
# GPU discipline (HARNESS_NOTES §1): one flock -o hold per step, nice -n 5, and 201 (lock busy) /
# 202 (<6 GB free) are RETRIED rather than silently dropping a seed.
set -u -o pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs

CODE=experiments/mainrun_0819/code
MAN=experiments/dayrun_0820/dataset_manifest_v2_full.json
SPL=experiments/dayrun_0820/split_v2_full.json
GRID=$CODE/labeling/gridspec_v1.json
BASE=experiments/weekend_0823/newmodels
OUT=$BASE/runs
PYBIN="/home/vislab/miniconda3/envs/env_seg/bin/python"
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
LOCK="${GPU_LOCK:-/tmp/negobs_gpu.lock}"
LOCK_WAIT="${LOCK_WAIT:-3600}"
LOCK_TRIES="${LOCK_TRIES:-48}"
ENCODERS="${ENCODERS:-tu-convnext_tiny resnet50}"
SEEDS="${SEEDS:-42 43 44}"
export PYTHONNOUSERSITE=1

mkdir -p "$OUT" "$BASE/logs"
rm -f "$BASE/DONE"
say () { echo "[$(date +%H:%M:%S)] $*"; }

say "=== run_newmodels start (D45 encoder axis) ==="
say "encoders='$ENCODERS' seeds='$SEEDS' grid=$GRID out=$OUT"

# --- CPU pre-flight: a bad encoder name must fail HERE, not 3600 s into the GPU lock ----------
for ENC in $ENCODERS; do
  if ! env CUDA_VISIBLE_DEVICES="" PYTHONNOUSERSITE=1 "$PYBIN" "$CODE/model_factory.py" 20 "$ENC" \
       > "$BASE/logs/preflight_${ENC//\//_}.log" 2>&1; then
    say "[fatal] encoder '$ENC' does not build on CPU -- see $BASE/logs/preflight_${ENC//\//_}.log"
    tail -n 5 "$BASE/logs/preflight_${ENC//\//_}.log"
    exit 2
  fi
  say "[preflight] $ENC OK -- $(grep -m1 'rgb ' "$BASE/logs/preflight_${ENC//\//_}.log")"
done

# gpu_step LABEL LOGFILE COMMAND...  -- one flock hold for the whole command, 201/202 retried
gpu_step () {
  local label="$1" log="$2"; shift 2
  local cmd="$*" try=0 rc=0
  while : ; do
    try=$((try + 1))
    say "[lock] $label (try $try/$LOCK_TRIES, wait ${LOCK_WAIT}s)"
    flock -o -w "$LOCK_WAIT" -E 201 "$LOCK" nice -n 5 bash -c "$cmd" 2>&1 | tee -a "$log"
    rc=${PIPESTATUS[0]}
    case $rc in
      0)   say "[ok]   $label"; return 0 ;;
      201) if [ "$try" -ge "$LOCK_TRIES" ]; then say "[busy] $label gave up after $try tries"; return 201; fi
           say "[busy] GPU lock held elsewhere -- retrying"; sleep 5 ;;
      202) if [ "$try" -ge "$LOCK_TRIES" ]; then say "[full] $label gave up after $try tries"; return 202; fi
           say "[full] $label: <6 GB free on the GPU -- retrying in 120 s"; sleep 120 ;;
      *)   say "[FAIL] $label exited $rc -- see $log"; return "$rc" ;;
    esac
  done
}

FAILED=""
for ENC in $ENCODERS; do
  for S in $SEEDS; do
    TAG="${ENC//\//_}_s$S"
    R="$OUT/$TAG"
    LOG="$BASE/logs/$TAG.log"
    mkdir -p "$R"
    if [ -f "$R/eval_test/metrics.json" ]; then say "[skip] $TAG (eval_test/metrics.json present)"; continue; fi
    say "--- $ENC seed $S -> $R ---"

    if [ -f "$R/best.pt" ]; then
      say "[resume] best.pt exists -> skipping the training step"
    else
      gpu_step "train $TAG" "$LOG" \
        "$PY $CODE/train_polar.py --manifest $MAN --split $SPL --grid $GRID --input rgb \
--seed $S --encoder $ENC --out $R --hflip on --oversample-h 4 --bias-init prior \
--lr 3e-4 --batch 8 --max-epochs 150 --patience 15" \
        || { FAILED="$FAILED $TAG:train"; continue; }
    fi
    # eval_polar rebuilds the encoder from the ckpt's config["encoder"] -- no flag needed here
    gpu_step "eval $TAG" "$LOG" \
      "$PY $CODE/eval_polar.py --manifest $MAN --split $SPL --subset test --ckpt $R/best.pt \
--input rgb --grid $GRID --tau-op 0.5 --tau-star auto --tau-sweep 0.3,0.5,0.7 --out $R/eval_test" \
      || { FAILED="$FAILED $TAG:eval"; continue; }
  done
done

say "=== run_newmodels done ==="
if [ -n "$FAILED" ]; then
  say "FAILED steps:$FAILED"
  echo "FAILED:$FAILED" > "$BASE/DONE"
  exit 1
fi
echo ALLDONE > "$BASE/DONE"
say "ALLDONE -> $BASE/DONE"
