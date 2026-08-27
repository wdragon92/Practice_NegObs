#!/usr/bin/env bash
# 자율 런 마감 라운드 — 전 33씬 allview (GT-119~126 + 2차 반복분 육안 검증용)
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs
bash scripts/rounds/run_p2_all33.sh 260816_w4_final33 on
# post: round stamps
for d in look_check/*/260816_w4_final33_on; do
  key=$(basename "$(dirname "$d")")
  python3 scripts/stamp_round.py "$d" 260816_w4_final33_on "$key" || true
done
echo "=== final33 render+stamp done ==="
