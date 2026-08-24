#!/usr/bin/env bash
# rescore_v3a_verdict.sh — VERDICT WAVE: score the v3-A checkpoints on
#   (1) the test-ext dashboard stage (AC + BD passes)  -> 계기판 ①②③
#   (2) test-core with the corrected GT (v2corr)       -> 헤드라인 표
#
# Mirrors rescore_v3textext.sh / rescore_v2corr.sh **verbatim** except for the
# checkpoint root (runs/v3a) and the per-run tau*.  v3-A has no published tau*,
# so --tau-star is left at the registered operating point 0.5 (tau_op); the
# judgement points are the FA-matched dual-axis grid recomputed downstream from
# the D-arm probability dumps (PREREG §2.1), never a re-fit tau*.
#
# EVALUATION NEVER APPLIES TRAINING MASKS (PREREG §5.2/§6-3): this script calls
# the untouched mainrun eval entry point, which has no knowledge of v3_masks.py.
#
# Resume-safe: a pass whose metrics.json exists is skipped. Per-invocation flock.
set -u -o pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
MAIN=$REPO/experiments/mainrun_0819
DAY=$REPO/experiments/dayrun_0820
V3=$REPO/experiments/v3_0823
CODE=$MAIN/code
MAN_AC=$V3/dataset_manifest_v3_textext.json
SPL_AC=$V3/split_v3_textext.json
MAN_BD=$V3/dataset_manifest_v3_textext_bd.json
SPL_BD=$V3/split_v3_textext_bd.json
MAN_CORE=$V3/dataset_manifest_v2corr.json
SPL_CORE=$DAY/split_v2_full.json
RUNS=$V3/runs/v3a
OUT_EXT=$V3/eval_v3a_textext
OUT_CORE=$V3/eval_v3a_core
GRID=gridspec_v1.json
NBOOT=10000
LOCK=/tmp/negobs_gpu.lock

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"

mkdir -p "$OUT_EXT" "$OUT_EXT/logs" "$OUT_CORE" "$OUT_CORE/logs"
QLOG=$OUT_EXT/logs/rescore.log
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$QLOG"; }

JOBS="rgb_s42 rgb_s43 rgb_s44 rgb_s42_aux"

say "=== rescore_v3a_verdict start ==="
say "ext AC=$MAN_AC  ext BD=$MAN_BD  core=$MAN_CORE  ckpt root=$RUNS"
FAILED=""

for NAME in $JOBS; do
  CK=$RUNS/$NAME/best.pt
  [ -f "$CK" ] || { say "[FAIL] missing ckpt $CK"; FAILED="$FAILED $NAME:ckpt"; continue; }
  for PASS in ac bd core; do
    case "$PASS" in
      ac)   EV=$OUT_EXT/$NAME;     MAN=$MAN_AC;   SPL=$SPL_AC ;;
      bd)   EV=$OUT_EXT/$NAME/bd;  MAN=$MAN_BD;   SPL=$SPL_BD ;;
      core) EV=$OUT_CORE/$NAME;    MAN=$MAN_CORE; SPL=$SPL_CORE ;;
    esac
    LOG=$(dirname "$EV")/logs/${NAME}_${PASS}.log
    [ "$PASS" = bd ] && LOG=$OUT_EXT/logs/${NAME}_bd.log
    mkdir -p "$EV" "$(dirname "$LOG")"
    if [ -f "$EV/metrics.json" ]; then
      say "[skip] $NAME/$PASS: metrics.json present"; touch "$EV/DONE"; continue
    fi
    CMD="$PY $CODE/eval_polar.py --input rgb --manifest '$MAN' --split '$SPL' --subset test \
--ckpt '$CK' --out '$EV' --tau-op 0.5 --tau-star 0.5 --tau-sweep 0.3,0.5,0.7 \
--n-boot $NBOOT --grid $GRID"
    say "[lock] eval $NAME/$PASS"
    echo "CMD: $CMD" >>"$LOG"
    if flock -o -w 7200 -E 201 "$LOCK" nice -n 5 bash -c "$CMD" >>"$LOG" 2>&1; then
      say "[ok]   $NAME/$PASS"
      tail -n 1 "$LOG" | sed 's/^/        /' | tee -a "$QLOG"
      touch "$EV/DONE"
    else
      rc=$?
      say "[FAIL] $NAME/$PASS exited $rc -- see $LOG"
      FAILED="$FAILED $NAME/$PASS"
    fi
  done
done

# ---- CPU post-step: on/off halves (same tool as the published queue) ----
for NAME in $JOBS; do
  for EV in "$OUT_EXT/$NAME" "$OUT_EXT/$NAME/bd" "$OUT_CORE/$NAME"; do
    if [ -f "$EV/per_frame.csv" ] && [ ! -f "$EV/per_frame_off.csv" ]; then
      env CUDA_VISIBLE_DEVICES="" $PY $CODE/split_per_frame.py --per-frame "$EV/per_frame.csv" \
          --out-dir "$EV" >>"$OUT_EXT/logs/${NAME}_post.log" 2>&1 || FAILED="$FAILED $NAME:split_pf"
    fi
  done
done

say "=== rescore_v3a_verdict done ==="
if [ -n "$FAILED" ]; then say "FAILED:$FAILED"; echo "FAILED:$FAILED" > "$OUT_EXT/ALL_DONE"; exit 1; fi
date +%s > "$OUT_EXT/ALL_DONE"; date +%s > "$OUT_CORE/ALL_DONE"
say "ALL_DONE written"
