#!/usr/bin/env bash
# w0_label.sh — W0 프로브 6개 라운드를 정본 라벨러로 라벨링한다 (CPU only).
#
# 낙차 발자국(footprint v2)은 트윈 높이맵 차분이므로 z_off가 필요하다.
# W0의 두 팔은 모두 hazard=ON이라 자기 안에 z_off가 없다 → 정본 off 라운드
# `260819_main_off`(base 밴드, 같은 시드 20260819)를 z_off로 쓴다.
# 그러면 A팔과 Bx팔의 `cells_raw`는 **같은 반사실면**에 대해 계산되므로
# 두 값의 차이는 오직 그 팔의 높이맵 차이에서만 온다 = VG-CLS가 묻는 그 양.
#
# 그리드는 v2 코퍼스와 같은 20칸 `gridspec_v1.json` (D19 세분).
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
LAB="$REPO/experiments/mainrun_0819/code/labeling/labeler.py"
GRID="$REPO/experiments/mainrun_0819/code/labeling/gridspec_v1.json"
OFF="$REPO/dataset/v2_corpus/260819_main_off"
OUT="$REPO/experiments/v3_0823/annotations"
LOG="$REPO/experiments/v3_0823/logs/w0_label.log"
mkdir -p "$OUT"

A_SCENES=scene01,scene02,scene03,scene04,scene06,scene08,scene09,scene10,scene16,scene21,sceneC1,sceneC4,sceneD1,sceneD2,sceneD3,sceneN1,sceneN2,sceneN4,sceneN5
declare -A SC=(
  [A]="$A_SCENES"
  [Brail]="scene01,scene02,scene06,scene08,scene10,scene16,scene21,sceneC1,sceneC4"
  [Bnose]="scene02,scene16,scene21,sceneC1,sceneD1"
  [Btact]="sceneC1,sceneC4"
  [Bmatl]="scene06,sceneN1,sceneN2,sceneN5"
  [Bdress]="$A_SCENES"
)

for arm in A Brail Bnose Btact Bmatl Bdress; do
  out="$OUT/w0_${arm}.json"
  want=$(printf '%s' "${SC[$arm]}" | tr ',' '\n' | grep -c .)
  have=$(ls -d "$(negobs_round_or_flat "260825_v3w0_cuecls_${arm}")"/*/*/ 2>/dev/null | wc -l)
  # 부분 렌더를 라벨링해 캐시로 굳히지 않는다 — 그 파일이 나중에 skip되면
  # 판정이 조용히 표본 부족 위에 서게 된다.
  if [ "$have" != "$want" ]; then
    echo "[hold] $arm — 렌더 $have/$want 씬만 존재, 라벨링 보류"; continue
  fi
  if [ -f "$out" ] && [ "${W0_FORCE:-0}" != "1" ]; then
    echo "[skip] $arm — $out exists"; continue
  fi
  echo "=== labeling $arm ($want 씬: ${SC[$arm]})"
  python3 "$LAB" --on-round "$(negobs_round "260825_v3w0_cuecls_${arm}")" \
      --off-round "$OFF" --grid "$GRID" --out "$out" \
      --scenes "${SC[$arm]}" --workers 8 2>&1 | tee -a "$LOG"
done
echo "W0_LABEL_DONE"
