#!/bin/bash
# =============================================================================
# run_n911_label.sh — sceneN9 / sceneN11 (**test-ext · N-cue**) 4팔 프로브의
#                     **라벨 + 게이트 배터리** (CPU 전용)
#
# 라벨 **4회** — H 씬(2회)·측방 씬(2회)과 다르다.
#   (A,C) — 기준 쌍. A팔 tier·발자국·VG-datum(A,C) 의 원천.
#   (B,D) — B팔 tier. (단서 OFF 팔의 GT)
#   **(C,A)** — 역쌍. C팔에 A팔보다 0.30 m 낮은 칸이 있는가 = VG-02 (ii) 의 프레임 판본.
#   **(D,B)** — 역쌍. D팔 동상.
#   ⇒ N-cue 씬의 판정은 *"**네 팔 전부** GT 올-음성"* 이므로 C·D 팔도 프레임 단위
#     `polar_gt` 행을 가져야 한다. 정순 2회만 돌리면 C·D 는 tier `off` 로만 남고
#     프레임 단위 반증이 불가능하다.
#
# 게이트
#   h12_gates.py (N-cue 모드 · `PRIMS[scene]["ncue"]=True` 가 전환)
#     VG-01/02/08/void/datum/10  — 공통
#     VG-06                      — **측정만** (가림체도 낙차 구조물도 없다)
#     (a) ALL-NEG  전 팔 · 전 프레임 GT 올-음성 + **`cells_raw` = 0** (D78 사각과 분리)
#     (a) 격자깊이 팔별 heightmap 최저점 회계 (쌍짓기에 의존하지 않는 반증 경로)
#     (b) 단서 픽셀 클래스별 분포 (DZ §12-5 k 게이트의 데이터 원천 · 임계 판정 없음)
#     (c) **(C,D) 광학차** — 단서 ON↔OFF · 계기판 ③ 용량-반응 입력
#
#   ※ `h67_yield.py` 는 **돌리지 않는다.** 그 스크립트의 판정문(strict-H 수율)은
#     낙차가 없는 씬에 대해 무의미하다(sceneL1 에서 이미 확인 — SCENE_TEXT_BUILD §12).
#
# 사용
#   bash experiments/v3_0823/code/run_n911_label.sh                     # probe · 두 씬
#   bash experiments/v3_0823/code/run_n911_label.sh 260823_v3p5_n911rev rev
#   bash experiments/v3_0823/code/run_n911_label.sh 260823_v3p5_n911b2  b2
#   인자: <stamp> <tag> [scenes]
# =============================================================================
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
LAB="$REPO/experiments/mainrun_0819/code/labeling"
ANN="$REPO/experiments/v3_0823/annotations"
D="$REPO/dataset"

S="${1:-260823_v3p5_n911probe}"
TAG="${2:-r0}"
SCENES="${3:-sceneN9,sceneN11}"

mkdir -p "$ANN"
export PYTHONNOUSERSITE=1
unset PYTHONPATH VIRTUAL_ENV

label() {  # label <on-round> <off-round> <out>
  ( cd "$LAB" && $PY labeler.py --on-round "$D/$1" --off-round "$D/$2" \
        --grid gridspec_v1.json --scenes "$SCENES" --out "$3" --workers 4 )
}

echo "=== (A,C) 라벨 · $S ==========================================="
label "${S}_A" "${S}_C" "$ANN/n911_${TAG}_ac_labels.json"
echo "=== (B,D) 라벨 · $S ==========================================="
label "${S}_B" "${S}_D" "$ANN/n911_${TAG}_bd_labels.json"
echo "=== (C,A) 역쌍 라벨 · $S ======================================"
label "${S}_C" "${S}_A" "$ANN/n911_${TAG}_ca_labels.json"
echo "=== (D,B) 역쌍 라벨 · $S ======================================"
label "${S}_D" "${S}_B" "$ANN/n911_${TAG}_db_labels.json"

cd "$REPO"
echo
echo "=== N-cue 게이트 배터리 (ALL-NEG · 격자깊이 · 단서 픽셀 · (C,D) 광학차) ==="
$PY experiments/v3_0823/code/h12_gates.py \
    --root dataset --stamp "$S" --split test --scenes "$SCENES" \
    --labels-ac "$ANN/n911_${TAG}_ac_labels.json" \
    --labels-bd "$ANN/n911_${TAG}_bd_labels.json" \
    --labels-ca "$ANN/n911_${TAG}_ca_labels.json" \
    --labels-db "$ANN/n911_${TAG}_db_labels.json" \
    --walk-z 0.0 \
    --out "$REPO/experiments/v3_0823/n911_gates_${TAG}.json"
