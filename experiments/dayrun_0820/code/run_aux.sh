#!/usr/bin/env bash
# run_aux.sh — DAYRUN_BRIEF_0820 Phase 6: the ONE aux-pixel-loss run.
#
#   bash experiments/dayrun_0820/code/run_aux.sh              # real run (takes the GPU lock)
#   DRYRUN=1 bash experiments/dayrun_0820/code/run_aux.sh     # print every command, touch nothing
#
# RGB U-Net, seed 42, recipe v2 EXACTLY as run_queue_v2.sh ran rgb_s42 (--hflip on
# --oversample-h 4 --bias-init prior --grid gridspec_v1.json --lr 3e-4 --batch 8 --max-epochs 150
# --patience 15) plus the only new variable:
#
#       loss = BCE(cell_logits, y) + AUX_LAMBDA * BCE(mask_logits, amodal_mask)
#
# One variable, one twin: runs/v2/rgb_s42 is the same recipe without the aux term, so the last
# step is a PAIRED bootstrap of aux-minus-base on the identical test frames -> the ablation line
# (H recall, FA, twin delta) the brief asks for.
#
# Notes
#  * val loss and checkpoint selection stay CELL-ONLY by design (train_polar.py header): sel_score
#    must remain comparable with the v2 runs, so the pixel term is a train-time regulariser only.
#  * The aux masks (annotations/amodal, Phase 5 product) cover the on-arm hazard frames; every
#    off-arm frame and every on-arm 'none_in_fov' frame has NO png and is read as an empty mask,
#    which is the correct target — the negatives are what teach the head not to hallucinate.
#  * GPU discipline is the queue's: flock -o -w 3600 -E 201 on /tmp/negobs_gpu.lock, nice -n 5,
#    train + eval each inside their own hold; CPU post-steps run outside it with CUDA hidden.
#  * VRAM is a little higher than the base run: with the pixel term the U-Net DECODER activations
#    must survive to backward (without it they are freed immediately). Same 512^2/batch 8 recipe
#    still fits a 4090 with room; if it ever OOMs, do NOT quietly shrink BATCH — that breaks the
#    one-variable comparison with runs/v2/rgb_s42 and must be reported.
#  * ABORT-SAFE: any step whose output already exists is skipped, so re-running resumes.
set -u -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"          # experiments/dayrun_0820/code
W="$(cd "$HERE/.." && pwd)"                                   # experiments/dayrun_0820
MAIN="$(cd "$W/../mainrun_0819/code" && pwd)"                 # experiments/mainrun_0819/code

MANIFEST="${MANIFEST:-$W/dataset_manifest_v2_full.json}"
SPLIT="${SPLIT:-$W/split_v2_full.json}"
GRID="${GRID:-gridspec_v1.json}"
SEED="${SEED:-42}"
RUN="${RUN:-$W/runs/v2/rgb_s42_aux}"
BASE="${BASE:-$W/runs/v2/rgb_s42}"                            # the no-aux twin (ablation partner)
AUX_MASK_DIR="${AUX_MASK_DIR:-$W/annotations/amodal}"
AUX_LAMBDA="${AUX_LAMBDA:-0.5}"

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
LOCK="${GPU_LOCK:-/tmp/negobs_gpu.lock}"
LOCK_WAIT="${LOCK_WAIT:-3600}"
LOCK_TRIES="${LOCK_TRIES:-48}"
EPOCHS="${EPOCHS:-150}"
PATIENCE="${PATIENCE:-15}"
BATCH="${BATCH:-8}"
LR="${LR:-3e-4}"
OVERSAMPLE_H="${OVERSAMPLE_H:-4}"
NBOOT="${NBOOT:-10000}"
DRYRUN="${DRYRUN:-}"

EV="$RUN/eval_test"
CMP="$W/runs/v2/compare_aux_vs_base_s42"
mkdir -p "$RUN" "$W/runs/v2/logs"
LOG="$W/runs/v2/logs/rgb_s42_aux.log"
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

say "=== run_aux (phase 6) start ${DRYRUN:+[DRYRUN]} ==="
say "manifest=$MANIFEST split=$SPLIT grid=$GRID seed=$SEED lambda=$AUX_LAMBDA"
say "run=$RUN  base(twin)=$BASE  masks=$AUX_MASK_DIR"

FAILED=""

gpu_step () {   # gpu_step LABEL COMMAND...   — one flock hold for the whole COMMAND string
  local label="$1"; shift
  local cmd="$*" try=0 rc=0
  if [ -n "$DRYRUN" ]; then
    say "[dry] GPU  $label"; printf '        flock -o -w %s -E 201 %s nice -n 5 bash -c %q\n' \
      "$LOCK_WAIT" "$LOCK" "$cmd" | tee -a "$LOG"; return 0
  fi
  while : ; do
    try=$((try + 1))
    say "[lock] $label (try $try/$LOCK_TRIES, wait ${LOCK_WAIT}s)"
    flock -o -w "$LOCK_WAIT" -E 201 "$LOCK" nice -n 5 bash -c "$cmd" >>"$LOG" 2>&1
    rc=$?
    case $rc in
      0)   say "[ok]   $label"; return 0 ;;
      201) if [ "$try" -ge "$LOCK_TRIES" ]; then say "[busy] $label gave up after $try tries"; return 201; fi
           say "[busy] GPU lock held by someone else -- retrying"; sleep 5 ;;
      202) say "[full] $label: <6 GB free on the GPU (exit 202) -- retrying later"; sleep 120
           if [ "$try" -ge "$LOCK_TRIES" ]; then return 202; fi ;;
      *)   say "[FAIL] $label exited $rc -- see $LOG"; return "$rc" ;;
    esac
  done
}

cpu_step () {   # cpu_step LABEL COMMAND...    — numpy/matplotlib only, no GPU lock, CUDA hidden
  local label="$1"; shift
  if [ -n "$DRYRUN" ]; then
    say "[dry] CPU  $label"; printf '        CUDA_VISIBLE_DEVICES="" bash -c %q\n' "$*" \
      | tee -a "$LOG"; return 0
  fi
  say "[cpu]  $label"
  if ! env CUDA_VISIBLE_DEVICES="" bash -c "$*" >>"$LOG" 2>&1; then
    say "[FAIL] $label -- see $LOG"; return 1
  fi
  return 0
}

# ---- preflight (CPU): inputs exist and the mask stems actually resolve -----------------------
for f in "$MANIFEST" "$SPLIT"; do
  [ -f "$f" ] || { say "[fatal] missing $f"; exit 2; }
done
[ -d "$AUX_MASK_DIR" ] || { say "[fatal] missing aux mask dir $AUX_MASK_DIR"; exit 2; }
[ -f "$BASE/eval_test/per_frame.csv" ] || say "[warn] no $BASE/eval_test/per_frame.csv yet -> the \
paired ablation step will be skipped; run run_queue_v2.sh for rgb_s42 first"
cpu_now () {    # like cpu_step but ALWAYS runs, DRYRUN or not (read-only checks live here)
  local label="$1"; shift
  say "[cpu]  $label"
  if ! env CUDA_VISIBLE_DEVICES="" bash -c "$*" 2>&1 | tee -a "$LOG"; then
    say "[FAIL] $label"; return 1
  fi
  return 0
}

cpu_now "preflight: grid + aux mask coverage" \
  "$PY $MAIN/gridspec.py $GRID && $PY -c \"
import sys; sys.path.insert(0, '$MAIN')
from polar_dataset import PolarGridDataset
import gridspec
d = PolarGridDataset('$MANIFEST', '$SPLIT', 'train', 'rgb', grid=gridspec.load('$GRID'),
                     aux_mask_dir='$AUX_MASK_DIR')
print(f'[preflight] train={len(d)} aux masks found={d.n_aux_found} '
      f'missing-as-empty={d.n_aux_missing}')
assert d.n_aux_found > 0
\"" || { say "[fatal] preflight failed -- see $LOG"; exit 2; }

# ---- 1. train (GPU) --------------------------------------------------------------------------
TRAIN="$PY $MAIN/train_polar.py --input rgb --lr $LR \
--manifest '$MANIFEST' --split '$SPLIT' --out '$RUN' --seed $SEED \
--max-epochs $EPOCHS --patience $PATIENCE --batch $BATCH --hflip on \
--oversample-h $OVERSAMPLE_H --bias-init prior --grid $GRID \
--aux-mask-dir '$AUX_MASK_DIR' --aux-lambda $AUX_LAMBDA"

if [ -f "$RUN/best.pt" ] && [ -z "$DRYRUN" ]; then
  say "[skip] train: $RUN/best.pt already present"
else
  gpu_step "train rgb_s42_aux" "$TRAIN" || { say "[abort] training failed"; exit 1; }
fi

# ---- 2. test eval (GPU) — identical flags to the queue's eval step ---------------------------
EVAL="$PY $MAIN/eval_polar.py --input rgb --manifest '$MANIFEST' --split '$SPLIT' --subset test \
--ckpt '$RUN/best.pt' --out '$EV' --tau-op 0.5 --tau-star auto --tau-sweep 0.3,0.5,0.7 \
--n-boot $NBOOT --grid $GRID"
if [ -f "$EV/metrics.json" ] && [ -z "$DRYRUN" ]; then
  say "[skip] eval: $EV/metrics.json already present"
else
  gpu_step "eval rgb_s42_aux" "$EVAL" || { say "[abort] eval failed"; exit 1; }
fi

# ---- 3. CPU post-steps (the queue's three, same order) ---------------------------------------
if [ ! -f "$EV/per_frame_off.csv" ] || [ -n "$DRYRUN" ]; then
  cpu_step "per_frame on/off split" \
    "$PY $MAIN/split_per_frame.py --per-frame '$EV/per_frame.csv' --out-dir '$EV'" \
    || FAILED="$FAILED split_pf"
fi
if [ ! -f "$RUN/twin/twin_analysis.md" ] || [ -n "$DRYRUN" ]; then
  cpu_step "twin analysis" \
    "$PY $MAIN/twin_analysis.py --per-frame-on '$EV/per_frame_on.csv' \
--per-frame-off '$EV/per_frame_off.csv' --manifest '$MANIFEST' --out '$RUN/twin' \
--n-boot $NBOOT --grid $GRID --tol 0.15" || FAILED="$FAILED twin"
fi
if [ ! -d "$RUN/viz" ] || [ -n "$DRYRUN" ]; then
  cpu_step "qualitative panels" \
    "$PY $MAIN/make_viz.py --per-frame '$EV/per_frame.csv' --manifest '$MANIFEST' \
--out '$RUN/viz' --n 4 --grid $GRID" || FAILED="$FAILED viz"
fi

# ---- 4. the ablation line: paired aux MINUS base on the same test frames ----------------------
# --per-frame-a = aux, --compare = base  -> metrics.json["compare"]["diff"] is (aux - base) with a
# paired bootstrap CI at tau 0.5; read frame_recall_H / frame_fa_off from it for the one-liner,
# and the twin delta from each run's twin/twin_analysis.md.
if { [ ! -f "$CMP/metrics.json" ] || [ -n "$DRYRUN" ]; } \
   && { [ -f "$BASE/eval_test/per_frame.csv" ] || [ -n "$DRYRUN" ]; }; then
  cpu_step "paired ablation aux vs base (s42)" \
    "$PY $MAIN/eval_polar.py --per-frame-a '$EV/per_frame.csv' \
--compare '$BASE/eval_test/per_frame.csv' --out '$CMP' --tau-op 0.5 --tau-star 0.5 \
--n-boot $NBOOT --grid $GRID" || FAILED="$FAILED compare"
fi

say "=== run_aux done ${DRYRUN:+[DRYRUN]} ==="
if [ -n "$FAILED" ]; then say "FAILED steps:$FAILED"; exit 1; fi
say "run      -> $RUN"
say "eval     -> $EV/METRICS_SECTION.md"
say "twin     -> $RUN/twin/twin_analysis.md"
say "ablation -> $CMP/metrics.json  (compare.diff = aux - base, paired, tau 0.5)"
