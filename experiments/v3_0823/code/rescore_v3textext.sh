#!/usr/bin/env bash
# rescore_v3textext.sh — ACCOUNTING §2-8: zero-shot rescore of the 9 frozen recipe-v2
# checkpoints on the W3 test-ext stage (D87 / W3_REPORT §9).
#
# Replicates the published eval invocation (mainrun_0819/code/run_queue_v2.sh) verbatim,
# changing ONLY the manifest/split (-> v3 test-ext) and keeping the FROZEN per-run tau*
# (mandate §9: 재적합 금지 — the JOBS string carries the published values).
#
# TWO passes per checkpoint, because the dashboards need three arms:
#   pass 1 (AC): dataset_manifest_v3_textext.json     on=A  off=C  -> dashboard (1) + FA_C
#   pass 2 (BD): dataset_manifest_v3_textext_bd.json  on=B  off=D  -> FA_D (dashboard (3))
# Dashboard (2) (CUE-OFF dose-response) is NOT run here — it needs trained v3 arms.
#
# Resume-safe: a pass whose metrics.json already exists is skipped. Per-invocation flock.
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
RUNS=$DAY/runs/v2
OUT=$V3/eval_v3textext
GRID=gridspec_v1.json
NBOOT=10000
LOCK=/tmp/negobs_gpu.lock

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
PY_B2="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 $PYBIN"

mkdir -p "$OUT" "$OUT/logs"
QLOG=$OUT/logs/rescore.log
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$QLOG"; }

# name:input:tau_star  (tau_star = FROZEN published value, dayrun_0820/runs/v2/<n>/eval_test)
JOBS="rgb_s42:rgb:0.63 rgb_s43:rgb:0.71 rgb_s44:rgb:0.31 \
depth_s42:depth:0.36 depth_s43:depth:0.21 depth_s44:depth:0.6 \
b2_s42:rgb:0.45 b2_s43:rgb:0.45 b2_s44:rgb:0.45"

say "=== rescore_v3textext start ==="
say "AC man=$MAN_AC  BD man=$MAN_BD  out=$OUT grid=$GRID nboot=$NBOOT tau_op=0.5"
FAILED=""

for J in $JOBS; do
  NAME=${J%%:*}; REST=${J#*:}; INPUT=${REST%%:*}; TAUSTAR=${REST##*:}
  case "$NAME" in
    b2_*) EVAL="$PY_B2 $MAIN/b2_polar/eval_b2_polar.py --input $INPUT --route auto" ;;
    *)    EVAL="$PY $CODE/eval_polar.py --input $INPUT" ;;
  esac
  for PASS in ac bd; do
    if [ "$PASS" = ac ]; then EV=$OUT/$NAME;    MAN=$MAN_AC; SPL=$SPL_AC
    else                      EV=$OUT/$NAME/bd; MAN=$MAN_BD; SPL=$SPL_BD; fi
    LOG=$OUT/logs/${NAME}_${PASS}.log
    mkdir -p "$EV"
    if [ -f "$EV/metrics.json" ]; then
      say "[skip] $NAME/$PASS: metrics.json present"; touch "$EV/DONE"; continue
    fi
    CMD="$EVAL --manifest '$MAN' --split '$SPL' --subset test --ckpt '$RUNS/$NAME/best.pt' \
--out '$EV' --tau-op 0.5 --tau-star $TAUSTAR --tau-sweep 0.3,0.5,0.7 --n-boot $NBOOT --grid $GRID"
    say "[lock] eval $NAME/$PASS (input=$INPUT tau*=$TAUSTAR)"
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

# ---- CPU post-step: on/off halves of each per_frame.csv (same tool as the published queue) ----
for J in $JOBS; do
  NAME=${J%%:*}
  for EV in "$OUT/$NAME" "$OUT/$NAME/bd"; do
    if [ -f "$EV/per_frame.csv" ] && [ ! -f "$EV/per_frame_off.csv" ]; then
      env CUDA_VISIBLE_DEVICES="" $PY $CODE/split_per_frame.py --per-frame "$EV/per_frame.csv" \
          --out-dir "$EV" >>"$OUT/logs/${NAME}_post.log" 2>&1 || FAILED="$FAILED $NAME:split_pf"
    fi
  done
done

say "=== rescore_v3textext done ==="
if [ -n "$FAILED" ]; then say "FAILED:$FAILED"; echo "FAILED:$FAILED" > "$OUT/ALL_DONE"; exit 1; fi
date +%s > "$OUT/ALL_DONE"
say "ALL_DONE written"
