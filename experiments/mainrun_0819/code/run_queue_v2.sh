#!/usr/bin/env bash
# run_queue_v2.sh — recipe-v2 retraining queue: 9 runs, strictly sequential, one GPU lock hold
# per run (train + its evals inside the same hold; CPU-only post-steps outside it).
#
#   bash run_queue_v2.sh <manifest.json> <split_v2.json> [outdir] [gridspec] [seeds] [models]
#   bash run_queue_v2.sh ../dataset_manifest_v2.json ../split_v2.json ../runs/v2 gridspec_v1.json
#
# Order: rgb x {42,43,44}, depth x {42,43,44} (train_polar.py, lr 3e-4), then
#        b2  x {42,43,44} (b2_polar/train_b2_polar.py, lr 6e-5).
# Each run: train -> test eval (tau_op .5 + tau* fitted on val) -> per_frame on/off split ->
#           twin analysis (CPU) -> qualitative panels (CPU).
# ABORT-SAFE: a run whose best.pt AND eval_test/metrics.json already exist is skipped; the CPU
# post-steps are likewise skipped when their outputs exist. Re-running the script resumes.
# Recipe v2 flags are identical for all three models (table-fairness): --hflip on --oversample-h 4
# --bias-init prior --grid <spec>. Only lr and the factory differ.
set -u -o pipefail

MANIFEST="${1:?usage: run_queue_v2.sh <manifest.json> <split.json> [outdir] [grid] [seeds] [models]}"
SPLIT="${2:?usage: run_queue_v2.sh <manifest.json> <split.json> [outdir] [grid] [seeds] [models]}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
W="$(cd "$HERE/.." && pwd)"
OUT="${3:-$W/runs/v2}"
GRID="${4:-gridspec_v1.json}"
SEEDS="${5:-42 43 44}"
MODELS="${6:-rgb depth b2}"

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
PY_B2="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 $PYBIN"
LOCK="${GPU_LOCK:-/tmp/negobs_gpu.lock}"   # override only for a CPU self-test of this script
LOCK_WAIT="${LOCK_WAIT:-3600}"     # seconds to wait for the GPU lock before giving up on a try
LOCK_TRIES="${LOCK_TRIES:-48}"     # x LOCK_WAIT  -> ~48 h ceiling, then the queue stops
EPOCHS="${EPOCHS:-150}"
PATIENCE="${PATIENCE:-15}"
BATCH="${BATCH:-8}"
LR_UNET="${LR_UNET:-3e-4}"
LR_B2="${LR_B2:-6e-5}"
OVERSAMPLE_H="${OVERSAMPLE_H:-4}"
NBOOT="${NBOOT:-10000}"
COMMON_TRAIN="--max-epochs $EPOCHS --patience $PATIENCE --batch $BATCH --hflip on \
--oversample-h $OVERSAMPLE_H --bias-init prior --grid $GRID"

mkdir -p "$OUT" "$OUT/logs"
QLOG="$OUT/logs/queue.log"
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$QLOG"; }

say "=== run_queue_v2 start ==="
say "manifest=$MANIFEST split=$SPLIT out=$OUT grid=$GRID"
say "models='$MODELS' seeds='$SEEDS' epochs=$EPOCHS patience=$PATIENCE batch=$BATCH \
lr_unet=$LR_UNET lr_b2=$LR_B2 oversample_h=$OVERSAMPLE_H"
"$PYBIN" "$HERE/gridspec.py" "$GRID" 2>&1 | tee -a "$QLOG" || { say "[fatal] bad --grid $GRID"; exit 2; }

FAILED=""

# gpu_step LABEL LOGFILE COMMAND...   -- one flock hold for the whole COMMAND string
gpu_step () {
  local label="$1" log="$2"; shift 2
  local cmd="$*" try=0 rc=0
  while : ; do
    try=$((try + 1))
    say "[lock] $label (try $try/$LOCK_TRIES, wait ${LOCK_WAIT}s)"
    flock -o -w "$LOCK_WAIT" -E 201 "$LOCK" nice -n 5 bash -c "$cmd" >>"$log" 2>&1
    rc=$?
    case $rc in
      0)   say "[ok]   $label"; return 0 ;;
      201) if [ "$try" -ge "$LOCK_TRIES" ]; then say "[busy] $label gave up after $try tries"; return 201; fi
           say "[busy] GPU lock held by someone else -- retrying"; sleep 5 ;;
      202) say "[full] $label: <6 GB free on the GPU (exit 202) -- retrying later"; sleep 120
           if [ "$try" -ge "$LOCK_TRIES" ]; then return 202; fi ;;
      *)   say "[FAIL] $label exited $rc -- see $log"; return "$rc" ;;
    esac
  done
}

cpu_step () {  # cpu_step LABEL LOGFILE COMMAND...   (no GPU lock: these are numpy/matplotlib only)
  local label="$1" log="$2"; shift 2
  say "[cpu]  $label"
  if ! env CUDA_VISIBLE_DEVICES="" bash -c "$*" >>"$log" 2>&1; then
    say "[FAIL] $label -- see $log"; return 1
  fi
  return 0
}

for MODEL in $MODELS; do
  for SEED in $SEEDS; do
    RUN="$OUT/${MODEL}_s${SEED}"
    EV="$RUN/eval_test"
    LOG="$OUT/logs/${MODEL}_s${SEED}.log"
    mkdir -p "$RUN"
    say "--- ${MODEL} seed ${SEED} -> $RUN ---"

    case "$MODEL" in
      rgb)   TRAIN="$PY $HERE/train_polar.py --input rgb   --lr $LR_UNET"
             EVAL="$PY $HERE/eval_polar.py --input rgb" ;;
      depth) TRAIN="$PY $HERE/train_polar.py --input depth --lr $LR_UNET"
             EVAL="$PY $HERE/eval_polar.py --input depth" ;;
      b2)    TRAIN="$PY_B2 $W/b2_polar/train_b2_polar.py --input rgb --lr $LR_B2"
             EVAL="$PY_B2 $W/b2_polar/eval_b2_polar.py --input rgb" ;;
      *)     say "[skip] unknown model '$MODEL'"; continue ;;
    esac

    if [ -f "$RUN/best.pt" ] && [ -f "$EV/metrics.json" ]; then
      say "[skip] ${MODEL}_s${SEED}: best.pt + eval_test/metrics.json already present"
    else
      CMD="$TRAIN --manifest '$MANIFEST' --split '$SPLIT' --out '$RUN' --seed $SEED $COMMON_TRAIN"
      if [ -f "$RUN/best.pt" ]; then
        say "[resume] best.pt exists, eval missing -> skipping the training step"
      else
        gpu_step "train ${MODEL}_s${SEED}" "$LOG" "$CMD" || { FAILED="$FAILED ${MODEL}_s${SEED}:train"; continue; }
      fi
      ECMD="$EVAL --manifest '$MANIFEST' --split '$SPLIT' --subset test --ckpt '$RUN/best.pt' \
--out '$EV' --tau-op 0.5 --tau-star auto --tau-sweep 0.3,0.5,0.7 --n-boot $NBOOT --grid $GRID"
      gpu_step "eval ${MODEL}_s${SEED}" "$LOG" "$ECMD" || { FAILED="$FAILED ${MODEL}_s${SEED}:eval"; continue; }
    fi

    # ---- CPU post-steps (no GPU lock) --------------------------------------
    if [ ! -f "$EV/per_frame_off.csv" ]; then
      cpu_step "per_frame on/off split ${MODEL}_s${SEED}" "$LOG" \
        "$PY $HERE/split_per_frame.py --per-frame '$EV/per_frame.csv' --out-dir '$EV'" \
        || FAILED="$FAILED ${MODEL}_s${SEED}:split_pf"
    fi
    if [ ! -f "$RUN/twin/twin_analysis.md" ]; then
      cpu_step "twin ${MODEL}_s${SEED}" "$LOG" \
        "$PY $HERE/twin_analysis.py --per-frame-on '$EV/per_frame_on.csv' \
--per-frame-off '$EV/per_frame_off.csv' --manifest '$MANIFEST' --out '$RUN/twin' \
--n-boot $NBOOT --grid $GRID --tol 0.15" || FAILED="$FAILED ${MODEL}_s${SEED}:twin"
    fi
    if [ ! -d "$RUN/viz" ]; then
      cpu_step "viz ${MODEL}_s${SEED}" "$LOG" \
        "$PY $HERE/make_viz.py --per-frame '$EV/per_frame.csv' --manifest '$MANIFEST' \
--out '$RUN/viz' --n 4 --grid $GRID" || FAILED="$FAILED ${MODEL}_s${SEED}:viz"
    fi
    tail -n 3 "$LOG" | sed 's/^/        /' | tee -a "$QLOG"
  done
done

# ---- paired RGB vs depth comparison at seed 42 (same frames, shared resample index) ----------
CMP="$OUT/compare_rgb_depth_s42"
if [ -f "$OUT/rgb_s42/eval_test/per_frame.csv" ] && [ -f "$OUT/depth_s42/eval_test/per_frame.csv" ] \
   && [ ! -f "$CMP/metrics.json" ]; then
  cpu_step "paired rgb-depth compare (s42)" "$OUT/logs/compare.log" \
    "$PY $HERE/eval_polar.py --per-frame-a '$OUT/rgb_s42/eval_test/per_frame.csv' \
--compare '$OUT/depth_s42/eval_test/per_frame.csv' --out '$CMP' --tau-star 0.5 \
--n-boot $NBOOT --grid $GRID" || FAILED="$FAILED compare"
fi

SEEDMD="$OUT/SEED_TABLE.md"
cpu_step "aggregate seeds" "$OUT/logs/aggregate.log" \
  "$PY $HERE/aggregate_seeds.py --root '$OUT' --models $(echo $MODELS | tr ' ' ',') \
--seeds $(echo $SEEDS | tr ' ' ',') --out '$SEEDMD' --grid $GRID" || FAILED="$FAILED aggregate"

say "=== run_queue_v2 done ==="
if [ -n "$FAILED" ]; then say "FAILED steps:$FAILED"; exit 1; fi
say "table -> $SEEDMD"
