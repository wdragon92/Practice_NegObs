#!/usr/bin/env bash
# run_v3a_train.sh — v3-A 학습 웨이브 러너 (본 3시드 + 격리 aux 1런, 순차)
#
#   PREREG_V3.md (FROZEN sha256 05f41322…) §1.1 · §5.x 집행.
#   본 A/B = rgb_s42 / rgb_s43 / rgb_s44   (aux OFF · §5.6)
#   격리    = rgb_s42_aux                   (aux ON · 본 판정 비혼입 · D82 결재 3)
#
#   GPU 락: flock -o /tmp/negobs_gpu.lock  (런마다 획득 — 다른 트랙과 공유)
#   재개 안전: 런 디렉터리에 DONE + best.pt + metrics.csv 가 다 있으면 건너뛴다.
#             TRAINING_FAILED 마커가 있으면 재시도하지 않는다(§6-16 — 조용한 재시도 금지).
set -u

ROOT=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823
CODE=$ROOT/code
RUNS=$ROOT/runs/v3a
LOGS=$ROOT/logs/v3a
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
LOCK=/tmp/negobs_gpu.lock
MAN=$ROOT/dataset_manifest_v3_seg3.json
SPL=$ROOT/split_v3_seg3.json
AUXDIR=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/annotations/amodal
AUXMAP=$ROOT/aux_stem_map_v3.json

mkdir -p "$RUNS" "$LOGS"

run_one () {
  local name=$1; shift
  local out=$RUNS/$name
  if [ -f "$out/DONE" ] && [ -f "$out/best.pt" ] && [ -f "$out/metrics.csv" ]; then
    echo "[skip] $name — DONE + best.pt + metrics.csv 존재 (재개 안전)"; return 0
  fi
  if [ -f "$out/TRAINING_FAILED" ]; then
    echo "[skip] $name — TRAINING_FAILED 마커 (§6-16: 조용한 재시도 금지)"; return 0
  fi
  mkdir -p "$out"
  echo "=== [$(date +%H:%M:%S)] START $name ==="
  flock -o "$LOCK" nice -n 5 \
    env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 \
    "$PY" "$CODE/train_v3.py" \
      --manifest "$MAN" --split "$SPL" --input rgb \
      --grid gridspec_v1.json --out "$out" \
      "$@" 2>&1 | tee "$LOGS/$name.log"
  local rc=${PIPESTATUS[0]}
  echo "=== [$(date +%H:%M:%S)] END $name rc=$rc ==="
  return 0
}

echo "###############################################################"
echo "# v3-A TRAINING WAVE  $(date)"
echo "#  corpus : $(basename "$MAN") / $(basename "$SPL")"
echo "#  runs   : rgb_s42 rgb_s43 rgb_s44 (본) + rgb_s42_aux (격리)"
echo "###############################################################"

run_one rgb_s42 --seed 42
run_one rgb_s43 --seed 43
run_one rgb_s44 --seed 44
run_one rgb_s42_aux --seed 42 --aux-mask-dir "$AUXDIR" --aux-stem-map "$AUXMAP" --isolated

echo "### WAVE COMPLETE $(date) ###"
for r in rgb_s42 rgb_s43 rgb_s44 rgb_s42_aux; do
  if [ -f "$RUNS/$r/DONE" ]; then echo "  $r: $(cat "$RUNS/$r/DONE" | tr -d '\n ')"
  elif [ -f "$RUNS/$r/TRAINING_FAILED" ]; then echo "  $r: TRAINING_FAILED"
  else echo "  $r: (없음)"; fi
done
touch "$ROOT/markers/v3a_wave.done"
