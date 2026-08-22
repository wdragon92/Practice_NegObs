#!/bin/bash
# =============================================================================
# eval_cueoff.sh — label the CUE-OFF arms, then run the FROZEN models over them
# zero-shot, then print the PRE-REGISTERED decision rule next to the result.
#
# RETRAINING IS ZERO.  Nothing here writes to runs/v2/*/best.pt; gate G6 in
# gates_cueoff.py hashes them before and after and fails if one moved.
#
# THREE PHASES
# ------------
#   1 label     labeling/labeler.py + build_manifest.py, per arm, in TWO label
#               sets (PREREG amendment A1.2):
#                 lineage  z_off = the canonical boost off round (READ-ONLY).
#                          Reproduces the GT the audit's H recall was computed
#                          against -- including scene12's declared-degenerate
#                          50-cell footprint.
#                 twin     z_off = ARM C, the same-seed same-pose hazard-off
#                          twin rendered by this very experiment.  Written only
#                          inside our own rounds; the corpus is never touched.
#   2 infer     eval_polar.py per (model, seed, arm) -> per_frame.csv
#               3 models x 3 seeds x every arm.  tau_op 0.5, tau_star pinned to
#               0.5 so no val subset is needed and nothing is fitted on test.
#   3 read out  readout_cueoff.py -- H recall by arm, the paired deltas, the
#               twin-conditional variants, and the D36 decision rule PRINTED
#               WITH THE RESULT rather than applied afterwards.
#
# USAGE
#   bash eval_cueoff.sh                      # all three phases, both label sets
#   bash eval_cueoff.sh --phases 1           # label only
#   bash eval_cueoff.sh --sets lineage       # skip the twin set
#   bash eval_cueoff.sh --models rgb --seeds 42     # a fast smoke of the chain
# Log: experiments/weekend_0823/cue_audit/logs/cueoff_eval.log
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
AUDIT="$REPO/experiments/weekend_0823/cue_audit"
CODE="$REPO/experiments/mainrun_0819/code"
LAB="$CODE/labeling"
GRID="$LAB/gridspec_v1.json"                 # 20 cells -- what runs/v2 was trained on
RUNS="$REPO/experiments/dayrun_0820/runs/v2"
LOGDIR="$AUDIT/logs"
LOG="$LOGDIR/cueoff_eval.log"
OUTDIR="$AUDIT/eval"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=3600
LOCK_RC=201

MODELS="rgb depth b2"
MAIN=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819
SEEDS="42 43 44"
PHASES="1 2 3"
SETS="lineage twin"
ARMS="A B2 B1 P C"
STEMS="260823_cueoff 260823_cueoff2"
TAU=0.5

mkdir -p "$LOGDIR" "$OUTDIR" "$AUDIT/labels" "$AUDIT/manifests"

while [ $# -gt 0 ]; do
  case "$1" in
    --phases) PHASES="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --sets)   SETS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --models) MODELS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --seeds)  SEEDS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --arms)   ARMS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --stems)  STEMS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# env_seg is the analysis env; PYTHONNOUSERSITE=1 is mandatory on this box
PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_seg
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# stem -> the canonical hazard-OFF round that supplies z_off for the `lineage` set
off_round() {
  case "$1" in
    260823_cueoff)  echo "$REPO/dataset/260820_boost_e_off" ;;   # s12 band e
    260823_cueoff2) echo "$REPO/dataset/260820_boost_e2_off" ;;  # s12 band e2, s20
    260823_cueoff3) echo "$REPO/dataset/260819_main_off" ;;
    *) echo "" ;;
  esac
}
# scene17 draws its z_off from the boost_h off round, which only that stem needs
off_round_s17() { echo "$REPO/dataset/260820_boost_h_off"; }

scenes_of_stem() {
  case "$1" in
    260823_cueoff)  echo "scene12 scene17 scene20" ;;
    260823_cueoff2) echo "scene12" ;;
    260823_cueoff3) echo "scene17" ;;
  esac
}

NFAIL=0
FAILS=""
note_fail() { NFAIL=$((NFAIL+1)); FAILS="${FAILS}\n  $*"; say "  [FAIL] $*"; }

# ---------------------------------------------------------------- phase 1
label_one() {   # label_one <set> <stem> <arm> <scene> <off_dir>
  local set="$1" stem="$2" arm="$3" scene="$4" offdir="$5"
  local on="$REPO/dataset/${stem}_${arm}"
  [ -d "$on" ] || { say "  [skip] $on absent"; return; }
  [ -d "$offdir" ] || { note_fail "$set $stem $arm $scene: off round $offdir absent"; return; }
  local lab="$AUDIT/labels/${set}__${stem}_${arm}__${scene}.json"
  local man="$AUDIT/manifests/${set}__${stem}_${arm}__${scene}.json"
  bash -c "$PRE
cd '$LAB'
python3 labeler.py --on-round '$on' --off-round '$offdir' \
        --scenes '$scene' --grid '$GRID' --out '$lab' --workers 2
python3 build_manifest.py --labels '$lab' --on-round '$on' \
        --off-round '$offdir' --out '$man'" >> "$LOG" 2>&1 \
    || note_fail "$set $stem $arm $scene: labeler/build_manifest rc=$?"
}

if case " $PHASES " in *" 1 "*) true ;; *) false ;; esac; then
  say "=== PHASE 1 · labels ==="
  for set in $SETS; do
    for stem in $STEMS; do
      for scene in $(scenes_of_stem "$stem"); do
        for arm in $ARMS; do
          if [ "$set" = "lineage" ]; then
            if [ "$scene" = "scene17" ] && [ "$stem" = "260823_cueoff" ]; then
              offdir=$(off_round_s17)
            else
              offdir=$(off_round "$stem")
            fi
          else
            # `twin`: arm C of the SAME stem is the exact-pose hazard-off twin
            offdir="$REPO/dataset/${stem}_C"
          fi
          say "  label $set $stem $arm $scene  (z_off <- ${offdir#$REPO/})"
          label_one "$set" "$stem" "$arm" "$scene" "$offdir"
        done
      done
    done
  done
fi

# ---------------------------------------------------------------- phase 2
# One split file that puts all three CUE-OFF scenes into `test`.  The split is
# scene-level (polar_dataset.py:217), and every frame in a CUE-OFF manifest is a
# CUE-OFF frame, so this selects everything without touching split_v2_full.json.
SPLIT="$AUDIT/split_cueoff.json"
cat > "$SPLIT" <<'JSON'
{"train": [], "val": [], "hold": [],
 "test": ["scene12", "scene17", "scene20"]}
JSON

infer_one() {   # infer_one <set> <stem> <arm> <scene> <model> <seed>
  local set="$1" stem="$2" arm="$3" scene="$4" model="$5" seed="$6"
  local man="$AUDIT/manifests/${set}__${stem}_${arm}__${scene}.json"
  [ -f "$man" ] || { say "  [skip] manifest $(basename "$man") absent"; return; }
  local inp="$model"; [ "$model" = "b2" ] && inp="rgb"
  local ck="$RUNS/${model}_s${seed}/best.pt"
  [ -f "$ck" ] || { note_fail "checkpoint $ck absent"; return; }
  local out="$OUTDIR/${set}/${stem}_${arm}/${scene}/${model}_s${seed}"
  [ -f "$out/per_frame.csv" ] && { say "  [skip] $out already done"; return; }
  mkdir -p "$out"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" bash -c "$PRE
cd '$CODE'
EVAL=eval_polar.py; [ '$model' = b2 ] && EVAL='$MAIN/b2_polar/eval_b2_polar.py'
python3 \$EVAL --manifest '$man' --split '$SPLIT' --subset test \
        --ckpt '$ck' --input '$inp' --grid '$GRID' \
        --tau-op $TAU --tau-star $TAU --out '$out'" >> "$LOG" 2>&1
  local rc=$?
  # rc 201 = never got the GPU lock in $LOCK_WAIT s (V2S queue held it).
  # rc 202 = train_polar.guard_gpu_free: the GPU freed the lock but not yet its
  #          memory. Both are TRANSIENT and this script is resume-safe (an
  #          existing per_frame.csv is skipped), so the fix is: re-run it.
  case "$rc" in
    0) ;;
    201) note_fail "$set $stem $arm $scene $model s$seed: LOCK-TIMEOUT (201) — re-run" ;;
    202) note_fail "$set $stem $arm $scene $model s$seed: GPU-BUSY (202, guard_gpu_free) — re-run" ;;
    *)   note_fail "$set $stem $arm $scene $model s$seed: eval rc=$rc" ;;
  esac
}

if case " $PHASES " in *" 2 "*) true ;; *) false ;; esac; then
  say "=== PHASE 2 · frozen inference (retraining 0) ==="
  say "  models='$MODELS' seeds='$SEEDS' tau_op=$TAU tau_star=$TAU (pinned, nothing fitted)"
  for set in $SETS; do
    for stem in $STEMS; do
      for scene in $(scenes_of_stem "$stem"); do
        for arm in $ARMS; do
          for model in $MODELS; do
            for seed in $SEEDS; do
              infer_one "$set" "$stem" "$arm" "$scene" "$model" "$seed"
            done
          done
        done
      done
    done
  done
fi

# ---------------------------------------------------------------- phase 3
if case " $PHASES " in *" 3 "*) true ;; *) false ;; esac; then
  say "=== PHASE 3 · readout + PRE-REGISTERED decision rule ==="
  bash -c "$PRE
python3 '$AUDIT/readout_cueoff.py' --eval-root '$OUTDIR' \
        --sets '$(echo $SETS | tr ' ' ',')' \
        --out '$AUDIT/CUEOFF_RESULT.md'" 2>&1 | tee -a "$LOG"
fi

say "================================================================"
if [ "$NFAIL" = "0" ]; then
  say "eval_cueoff.sh COMPLETE — 0 failures"
else
  say "eval_cueoff.sh FAILURES ($NFAIL)"
  printf '%b\n' "$FAILS" | tee -a "$LOG"
fi
say "gates: python3 $AUDIT/gates_cueoff.py --stage post"
exit $(( NFAIL > 0 ))
