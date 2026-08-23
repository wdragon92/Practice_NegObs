#!/usr/bin/env bash
# w1d_pipeline.sh — W1 D팔 착지 후 CPU 파이프라인 전체 (재현용 드라이버).
#
# 순서가 곧 의존성이다. 특히 **계기 정렬(1)이 라벨링(2)보다 먼저**여야 한다 —
# 융합 사이드카가 없으면 scene08 계열의 낙차가 통째로 사라진 채 라벨이 굳는다.
set -eu
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
C="$REPO/experiments/v3_0823/code"
cd "$REPO"

echo "=== 1. 계기 정렬 (융합 높이맵 사이드카) ==="
python3 "$C/w1d_fuse.py" --write

echo "=== 2. 라벨링 (생산 스캔 + D를 z_off로 한 W0 재라벨링) ==="
bash "$C/w1d_label.sh"

echo "=== 3. 착지 검사 (회계 · VG-02 · VG-04 · VG-08 · VG-10 · VG-datum) ==="
python3 "$C/w1d_verify.py"

echo "=== 4. VG-CLS 재판정 (사전등록 규칙 동일 · 참조와 계기만 교체) ==="
# 4a 귀속용 중간 원장 — 참조는 그대로 두고 **계기만** 고친 것.
#    W0의 검정 2가 융합 씬에서 공허하게 '장식'을 찍던 문제의 크기를 분리한다.
python3 "$C/w0_classify.py" --hm-loader labeler \
    --out "$REPO/experiments/v3_0823/w1d_cuecls_guoff_hmfix.json"
# 4b 확정 원장 — 참조 = D팔, 계기 = 라벨러와 동일.
python3 "$C/w0_classify.py" --zoff-round 260826_v3w1_lib_D \
    --ann-prefix w1d_zoffD_ --hm-loader labeler \
    --out "$REPO/experiments/v3_0823/w1d_cuecls.json"

echo "=== 5. before/after 대조 ==="
python3 "$C/w1d_readjudicate.py"

echo "=== 6. 키별 |r| 재계산 (확정 판정 원장으로) ==="
python3 "$C/w0_rimpact.py" --cls "$REPO/experiments/v3_0823/w1d_cuecls.json"

echo "W1D_PIPELINE_DONE"
