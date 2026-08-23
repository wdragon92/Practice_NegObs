#!/usr/bin/env bash
# w1b2_pipeline.sh — W1-B2 착지 후 CPU 파이프라인 (재현용 드라이버).
#
# `w1b_pipeline.sh`와 **같은 코드·같은 순서**다. 다른 것은 `W1B_ARM=B2` 하나 —
# 그러면 fuse/label/verify가 `260826_v3w1_lib_B2*` 트리를 읽고 `w1b2_*`로 쓴다
# (12씬만; 나머지 3씬 scene01·scene06·sceneD2는 T가 이미 B 레버였으므로
#  착지한 B 라운드를 그대로 쓴다).
#
# 순서가 곧 의존성이다 — 계기 정렬(1)이 라벨링(2)보다 먼저여야 중심 게이트가
# "레버의 효과"가 아니라 "계기 차이"를 재는 사고를 피한다.
set -eu
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
C="$REPO/experiments/v3_0823/code"
cd "$REPO"
export W1B_ARM=B2

echo "=== 0. B2 설정 재확인 (hazgate_full 파생 · 재질 재바인딩 AST 검사) ==="
python3 "$C/w1b2_configs.py"

echo "=== 1. 계기 정렬 (코퍼스 A팔이 융합을 쓰는 씬에만 B2 융합 사이드카) ==="
python3 "$C/w1b_fuse.py" --write

echo "=== 2. 라벨링 (A 재라벨 + B2 라벨 · 같은 드라이버·z_off = D팔) ==="
python3 "$C/w1b_label.py" --workers 8 "${W1B_FORCE:+--force}"

echo "=== 3. 게이트 배터리 (회계 · VG-01 · VG-08 per-cut · VG-10 · VG-datum) ==="
python3 "$C/w1b_verify.py"

echo "=== 4. 키별 |r| 재계산 (B2 실측 반영 · 전 6키) ==="
python3 "$C/w1b_rimpact.py" --b2

echo "W1B2_PIPELINE_DONE"
