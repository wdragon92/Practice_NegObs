#!/usr/bin/env bash
# p4_repro.sh — P-4 재현 검증 GPU 트랙 (ACCOUNTING §2-7).
#
# 신선택식이 출하와 **다른 에폭**을 고른 런만 대상으로:
#   ① 원 훈련을 그대로 재현(같은 시드·같은 구 GT 매니페스트)하며 대상 에폭 ckpt 를 물질화
#   ② 재현 검산: 재훈련 metrics.csv 가 보관본과 일치하는가 (일치 안 하면 그 자체가 결과)
#   ③ 그 에폭 ckpt 를 test-core **교정 GT** 로 채점 (rescore_v2corr.sh 호출과 동일 규약)
#
# 재개 안전: 각 단계 DONE 마커. flock -o /tmp/negobs_gpu.lock 로 GPU 홀드.
set -u -o pipefail

R=/home/vislab/Desktop/work_sy/Practice_NegObs
MAIN=$R/experiments/mainrun_0819
DAY=$R/experiments/dayrun_0820
V3=$R/experiments/v3_0823
CODE=$MAIN/code
MAN_OLD=$DAY/dataset_manifest_v2_full.json      # 훈련 = 원 조건 그대로
MAN_COR=$V3/dataset_manifest_v2corr.json        # 채점 = 교정 GT
SPLIT=$DAY/split_v2_full.json
GRID=gridspec_v1.json
NBOOT=10000
LOCK=/tmp/negobs_gpu.lock
OUT=$V3/reselect
LOGD=$OUT/logs

PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"
PY_B2="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 $PYBIN"
WRAP=$V3/code/p4_retrain_epoch.py

mkdir -p "$OUT" "$LOGD"
QLOG=$LOGD/p4_repro.log
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$QLOG"; }

# run:which:input:lr:old_epoch:new_epoch:tau_star_published
JOBS="${JOBS:-rgb_s42:polar:rgb:3e-4:9:10:0.63 \
b2_s42:b2:rgb:6e-5:8:1:0.45 \
b2_s44:b2:rgb:6e-5:8:13:0.45}"

COMMON="--max-epochs 150 --patience 15 --batch 8 --hflip on --oversample-h 4 \
--bias-init prior --grid $GRID"

say "=== p4_repro start ==="
FAILED=""

for J in $JOBS; do
  IFS=: read -r NAME WHICH INPUT LR EPOLD EPNEW TAUSTAR <<<"$J"
  RUN=$OUT/${NAME}_repro
  mkdir -p "$RUN"
  LOG=$LOGD/${NAME}.log

  # ---------------------------------------------------------------- ① 재훈련
  if [ -f "$RUN/TRAIN_DONE" ]; then
    say "[skip] $NAME train (TRAIN_DONE)"
  else
    case "$WHICH" in
      b2) TCMD="$PY_B2 $WRAP --which b2    --keep $EPOLD,$EPNEW -- --input $INPUT --lr $LR" ;;
      *)  TCMD="$PY    $WRAP --which polar --keep $EPOLD,$EPNEW -- --input $INPUT --lr $LR" ;;
    esac
    CMD="$TCMD --manifest '$MAN_OLD' --split '$SPLIT' --out '$RUN' --seed ${NAME##*_s} $COMMON"
    say "[lock] retrain $NAME (keep ep $EPOLD,$EPNEW)"
    echo "CMD: $CMD" >>"$LOG"
    if flock -o -w 7200 -E 201 "$LOCK" nice -n 5 bash -c "$CMD" >>"$LOG" 2>&1; then
      touch "$RUN/TRAIN_DONE"; say "[ok]   retrain $NAME"
    else
      rc=$?; say "[FAIL] retrain $NAME rc=$rc"; FAILED="$FAILED $NAME:train"; continue
    fi
  fi

  # ------------------------------------------------- ② 재현 검산 (CPU, 락 불필요)
  env CUDA_VISIBLE_DEVICES="" $PY - "$DAY/runs/v2/$NAME/metrics.csv" "$RUN/metrics.csv" \
      "$RUN/REPRO_CHECK.json" <<'PYEOF' >>"$LOG" 2>&1 || FAILED="$FAILED $NAME:reprocheck"
import csv, json, sys
a, b, out = sys.argv[1], sys.argv[2], sys.argv[3]
A = list(csv.DictReader(open(a))); B = list(csv.DictReader(open(b)))
cols = ["val_loss","val_f1","val_recall","val_fpr","val_h_recall","sel_score","train_loss"]
n = min(len(A), len(B)); worst = {c: 0.0 for c in cols}; first_bad = None
for i in range(n):
    for c in cols:
        d = abs(float(A[i][c]) - float(B[i][c]))
        if d > worst[c]: worst[c] = d
        if d > 1e-6 and first_bad is None: first_bad = {"epoch": A[i]["epoch"], "col": c, "d": d}
res = {"n_epochs_archived": len(A), "n_epochs_repro": len(B), "n_compared": n,
       "max_abs_diff": worst, "first_divergence": first_bad,
       "identical": (len(A) == len(B) and first_bad is None)}
json.dump(res, open(out, "w"), indent=1)
print("[repro-check]", json.dumps(res))
PYEOF

  # ------------------------------------------------ ③ 교정 GT test-core 채점
  for EP in $EPOLD $EPNEW; do
    CK=$RUN/ep${EP}.pt
    EV=$OUT/eval/${NAME}_ep${EP}
    [ -f "$EV/metrics.json" ] && { say "[skip] eval $NAME ep$EP"; touch "$EV/DONE"; continue; }
    [ -f "$CK" ] || { say "[FAIL] missing $CK"; FAILED="$FAILED $NAME:ep$EP"; continue; }
    mkdir -p "$EV"
    case "$WHICH" in
      b2) EVAL="$PY_B2 $MAIN/b2_polar/eval_b2_polar.py --input $INPUT --route auto" ;;
      *)  EVAL="$PY $CODE/eval_polar.py --input $INPUT" ;;
    esac
    ECMD="$EVAL --manifest '$MAN_COR' --split '$SPLIT' --subset test --ckpt '$CK' \
--out '$EV' --tau-op 0.5 --tau-star $TAUSTAR --tau-sweep 0.3,0.5,0.7 --n-boot $NBOOT --grid $GRID"
    say "[lock] eval $NAME ep$EP (corrected GT)"
    echo "CMD: $ECMD" >>"$LOG"
    if flock -o -w 7200 -E 201 "$LOCK" nice -n 5 bash -c "$ECMD" >>"$LOG" 2>&1; then
      env CUDA_VISIBLE_DEVICES="" $PY $CODE/split_per_frame.py --per-frame "$EV/per_frame.csv" \
          --out-dir "$EV" >>"$LOG" 2>&1 || true
      touch "$EV/DONE"; say "[ok]   eval $NAME ep$EP"
    else
      rc=$?; say "[FAIL] eval $NAME ep$EP rc=$rc"; FAILED="$FAILED $NAME:eval$EP"
    fi
  done
done

say "=== p4_repro done ==="
if [ -n "$FAILED" ]; then say "FAILED:$FAILED"; echo "FAILED:$FAILED" >"$OUT/ALL_DONE"; exit 1; fi
date +%s >"$OUT/ALL_DONE"; say "ALL_DONE"
