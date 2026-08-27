#!/bin/bash
# =============================================================================
# run_ctrl_eval.sh — label -> manifest -> RGB v2 3-seed eval -> twin -> 병기 table
#   for the C2 dressing control (OVERNIGHT_BRIEF_0820 §4 C2, DECISIONS D25).
#
# THE GATE COMES FIRST. The brief's C2 entry says evaluation may start only
# after "on-arm hash unchanged + camera poses byte-identical" has passed, so
# step 0 runs `hash_gate.py verify` and aborts on anything but exit 0.
#
# What it produces, all under experiments/nightrun_0820/ctrl_dressing/:
#   labels_ctrl.json      labeler v2 output for the pair (on = 260819_main_on,
#                         off = 260820_ctrloff), sceneC2 + sceneN3 only
#   manifest_ctrl.json    the fixed manifest contract over those 96 frames
#   split_ctrl.json       both scenes in `test` (they are test scenes in
#                         split_v2_full.json, so the checkpoints never saw them)
#   eval_new_s{42,43,44}  eval_polar on the NEW pair            (GPU, one lock hold each)
#   eval_old_s{42,43,44}  the same metrics recomputed on the FROZEN v2 eval rows,
#                         restricted to these two scenes        (CPU, --per-frame-a,
#                         so no checkpoint is re-run and no frozen file is touched)
#   twin_{new,old}_s*     twin_analysis, --tol 0.15 (D20) on both
#   CTRL_TABLE.md         the side-by-side table + ctrl_numbers.json
#
# WHY --per-frame-a FOR THE OLD ARM
#   The old off arm's probabilities already exist in
#   experiments/dayrun_0820/runs/v2/rgb_s*/eval_test/per_frame.csv (the frozen v2
#   test evaluation). Re-inferring them would risk a different result for the
#   same frames; filtering the frozen CSV to the two scenes and feeding it back
#   through `eval_polar --per-frame-a` reuses the published numbers and still
#   gives the same metric bundle + CIs, on CPU.
#
# usage
#   bash experiments/nightrun_0820/ctrl_dressing/run_ctrl_eval.sh
#   bash .../run_ctrl_eval.sh --seeds 42            # one seed
#   bash .../run_ctrl_eval.sh --skip-gate           # ONLY for debugging; never for a result
# =============================================================================
set -u -o pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
HERE="$REPO/experiments/nightrun_0820/ctrl_dressing"
CODE="$REPO/experiments/mainrun_0819/code"
V2="$REPO/experiments/dayrun_0820/runs/v2"
FROZEN_MANIFEST="$REPO/experiments/dayrun_0820/dataset_manifest_v2_full.json"
GRID=gridspec_v1.json
ON_ROUND="$REPO/dataset/v2_corpus/260819_main_on"
CTRL_ROUND="$REPO/dataset/v2_probes/260820_ctrloff"
SCENES=sceneC2,sceneN3
TAU=0.5
TOL=0.15                      # D20 twin pairing tolerance, kept identical on both arms
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=3600
LOG="$HERE/logs/eval.log"

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
CPU="env CUDA_VISIBLE_DEVICES= PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"

SEEDS="42 43 44"
GATE=1
while [ $# -gt 0 ]; do
  case "$1" in
    --seeds)     SEEDS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --skip-gate) GATE=0; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$HERE/logs"
say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }
FAILED=""
step() {   # step LABEL COMMAND...
  local label="$1"; shift
  say "[cpu]  $label"
  if ! bash -c "$*" >>"$LOG" 2>&1; then say "[FAIL] $label — see $LOG"; FAILED="$FAILED $label"; return 1; fi
}
gpu_step() {  # gpu_step LABEL COMMAND...   (one flock hold, 201 = lock busy, 202 = GPU full)
  local label="$1"; shift
  say "[lock] $label"
  flock -o -w "$LOCK_WAIT" -E 201 "$LOCK" nice -n 5 bash -c "$*" >>"$LOG" 2>&1
  local rc=$?
  case $rc in
    0)   say "[ok]   $label"; return 0 ;;
    201) say "[busy] $label — no GPU lock in ${LOCK_WAIT}s"; FAILED="$FAILED $label(lock)"; return 201 ;;
    202) say "[full] $label — <6 GB free on the GPU"; FAILED="$FAILED $label(gpu-full)"; return 202 ;;
    *)   say "[FAIL] $label exited $rc — see $LOG"; FAILED="$FAILED $label"; return "$rc" ;;
  esac
}

say "================================================================"
say "run_ctrl_eval.sh start — seeds:[$SEEDS] tau:$TAU tol:$TOL grid:$GRID"
say "================================================================"

# --- 0. gate -----------------------------------------------------------------
if [ "$GATE" = "1" ]; then
  say "[gate] hash_gate.py verify"
  if ! python3 "$HERE/hash_gate.py" verify --ctrl-round 260820_ctrloff 2>&1 | tee -a "$LOG"; then
    say "GATE FAILED — evaluation refused (brief §4 C2: '게이트 통과 후에만 평가')"
    exit 3
  fi
fi

# --- 1. label the pair -------------------------------------------------------
# labeler.scene_dirs keys by sceneID and IGNORES the split subdirectory, so the
# two rounds may lay their scenes out differently (they do: C2 sits under val/,
# N3 under train/). --scenes keeps the on round's other 31 scenes out.
if [ ! -f "$HERE/labels_ctrl.json" ]; then
  step "labeler (on=260819_main_on, off=260820_ctrloff, $SCENES)" \
    "$CPU $CODE/labeling/labeler.py --on-round '$ON_ROUND' --off-round '$CTRL_ROUND' \
       --scenes $SCENES --grid $CODE/labeling/$GRID --out '$HERE/labels_ctrl.json' --workers 2"
else
  say "[skip] labels_ctrl.json exists"
fi

# --- 2. manifest + split -----------------------------------------------------
if [ ! -f "$HERE/manifest_ctrl.json" ]; then
  step "build_manifest" \
    "$CPU $CODE/labeling/build_manifest.py --labels '$HERE/labels_ctrl.json' \
       --on-round '$ON_ROUND' --off-round '$CTRL_ROUND' --out '$HERE/manifest_ctrl.json'"
else
  say "[skip] manifest_ctrl.json exists"
fi
cat > "$HERE/split_ctrl.json" <<'JSON'
{
 "train": [],
 "val": [],
 "test": ["sceneC2", "sceneN3"],
 "hold": [],
 "note": "ctrl_dressing only. Both scenes are test scenes in split_v2_full.json, so the RGB v2 checkpoints never trained on them; this file just tells eval_polar which subset to walk."
}
JSON

# --- 2b. freeze the ON arm ---------------------------------------------------
# The labeler derives the on arm's GT from z_off - z_on, so a new off arm means a
# freshly derived on-arm GT. sync_on_arm.py prints every difference and then
# restores the published values, so the old and the new off arm are measured
# against the SAME on arm (brief rule 2: labels frozen).
step "sync_on_arm (report + freeze the ON-arm labels)" \
  "$CPU '$HERE/sync_on_arm.py' --manifest '$HERE/manifest_ctrl.json' --frozen '$FROZEN_MANIFEST'"

# --- 3. per-seed evaluation --------------------------------------------------
for S in $SEEDS; do
  CK="$V2/rgb_s$S/best.pt"
  FROZEN_PF="$V2/rgb_s$S/eval_test/per_frame.csv"
  NEW="$HERE/eval_new_s$S"; OLD="$HERE/eval_old_s$S"
  [ -f "$CK" ] || { say "[FAIL] missing checkpoint $CK"; FAILED="$FAILED ckpt_s$S"; continue; }

  # 3a NEW pair — the only GPU step in this script
  if [ ! -f "$NEW/metrics.json" ]; then
    gpu_step "eval_new s$S" \
      "$PY $CODE/eval_polar.py --manifest '$HERE/manifest_ctrl.json' --split '$HERE/split_ctrl.json' \
         --subset test --input rgb --ckpt '$CK' --out '$NEW' --tau-op $TAU --tau-star $TAU \
         --tau-sweep 0.3,0.5,0.7 --grid $CODE/labeling/$GRID" || continue
  else
    say "[skip] eval_new s$S exists"
  fi
  step "split_per_frame new s$S" \
    "$CPU $CODE/split_per_frame.py --per-frame '$NEW/per_frame.csv' --out-dir '$NEW'"
  step "twin new s$S" \
    "$CPU $CODE/twin_analysis.py --per-frame-on '$NEW/per_frame_on.csv' \
       --per-frame-off '$NEW/per_frame_off.csv' --manifest '$HERE/manifest_ctrl.json' \
       --out '$HERE/twin_new_s$S' --tol $TOL --grid $CODE/labeling/$GRID"

  # 3b OLD pair — reuse the frozen rows, filtered to the two scenes (CPU only)
  [ -f "$FROZEN_PF" ] || { say "[FAIL] missing frozen per_frame $FROZEN_PF"; FAILED="$FAILED frozen_s$S"; continue; }
  mkdir -p "$OLD"
  step "filter frozen per_frame s$S" \
    "$CPU - <<PY
import csv
keep = {'sceneC2', 'sceneN3'}
with open('$FROZEN_PF') as f:
    rd = csv.DictReader(f); rows = [r for r in rd if r['scene_id'] in keep]; fn = rd.fieldnames
with open('$OLD/per_frame_src.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fn); w.writeheader(); w.writerows(rows)
print(f'[filter] {len(rows)} rows -> $OLD/per_frame_src.csv')
PY"
  if [ ! -f "$OLD/metrics.json" ]; then
    step "eval_old s$S (--per-frame-a, CPU)" \
      "$CPU $CODE/eval_polar.py --per-frame-a '$OLD/per_frame_src.csv' --out '$OLD' \
         --tau-op $TAU --tau-star $TAU --tau-sweep 0.3,0.5,0.7 --grid $CODE/labeling/$GRID"
  else
    say "[skip] eval_old s$S exists"
  fi
  step "split_per_frame old s$S" \
    "$CPU $CODE/split_per_frame.py --per-frame '$OLD/per_frame.csv' --out-dir '$OLD'"
  step "twin old s$S" \
    "$CPU $CODE/twin_analysis.py --per-frame-on '$OLD/per_frame_on.csv' \
       --per-frame-off '$OLD/per_frame_off.csv' --manifest '$FROZEN_MANIFEST' \
       --out '$HERE/twin_old_s$S' --tol $TOL --grid $CODE/labeling/$GRID"
done

# --- 4. the 병기 table -------------------------------------------------------
step "ctrl_table" "$CPU $HERE/ctrl_table.py --root '$HERE' --tau $TAU \
  --seeds $(echo "$SEEDS" | tr ' ' ',')"

say "================================================================"
if [ -z "$FAILED" ]; then
  say "run_ctrl_eval.sh done — every step exited 0"
  say "  table: $HERE/CTRL_TABLE.md"
  exit 0
fi
say "run_ctrl_eval.sh finished with failures:$FAILED"
say "  partial outputs are kept; re-run to resume (completed steps are skipped)"
exit 1
