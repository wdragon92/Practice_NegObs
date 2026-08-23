#!/usr/bin/env bash
# w1b_pipeline.sh — W1 B팔 착지 후 CPU 파이프라인 전체 (재현용 드라이버).
#
# 순서가 곧 의존성이다. W1-D와 같은 이유로 **계기 정렬(1)이 라벨링(2)보다
# 먼저**여야 한다 — 다만 B는 on팔이라 계기 짝이 구off가 아니라 **코퍼스 A팔**이다
# (w1b_fuse.py 헤더). 계기가 어긋나면 중심 게이트 VG-01이 "레버의 효과"가 아니라
# "계기 차이"를 측정하게 된다.
set -eu
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
C="$REPO/experiments/v3_0823/code"
cd "$REPO"

echo "=== 0. B팔 설정 재확인 (§6.6 표 대조 — 렌더한 것과 같은 파일인지) ==="
python3 "$C/w1b_configs.py"

echo "=== 1. 계기 정렬 (코퍼스 A팔이 융합을 쓰는 씬에만 B 융합 사이드카) ==="
python3 "$C/w1b_fuse.py" --write

echo "=== 2. 라벨링 (A 재라벨 + B 라벨 · 같은 드라이버·같은 z_off) ==="
python3 "$C/w1b_label.py" --workers 8 "${W1B_FORCE:+--force}"

echo "=== 3. 착지 검사 (회계 · **VG-01** · VG-08 per-cut · VG-10 · VG-datum) ==="
python3 "$C/w1b_verify.py"

echo "=== 4. 키별 |r| 재계산 (B팔 실측 착지 반영) ==="
python3 "$C/w1b_rimpact.py"

echo "W1B_PIPELINE_DONE"
