#!/bin/bash
# =============================================================================
# run_w3_label.sh — W3 test-ext **본렌더**의 라벨 + 게이트 배터리 (CPU 전용)
#
# 라벨 4회 × 밴드라운드 4개 = **16회**
#   (A,C) — 기준 쌍. A팔 tier·발자국·VG-datum 의 원천이고 **계기판 ① 의 쌍 규약**.
#   (B,D) — B팔 tier. `paired-H` = A·B 가 **둘 다** strict-H 인 프레임.
#   (C,A) — 역쌍. C팔의 프레임 단위 `polar_gt` 행 = **C팔 올-음성의 반증 경로**.
#   (D,B) — 역쌍. D팔 동상.
#   ※ 역쌍을 **N-cue 씬뿐 아니라 6씬 전부**에 돌린다. 계획 §1.0(사실 판정)과
#     PREREG §7.2 AC-INSTR-1(C팔 GT = 사양 상수 = 전 칸 음성)은 H·측방 씬의
#     C·D 팔에도 그대로 걸리는 주장이고, 정순 2회만으로는 그 주장이 **반증
#     불가능**하기 때문이다(h12_gates 의 ALLNEG 은 ncue 씬에서만 자동 호출되므로
#     나머지는 `w3_extra_gates.py` 가 같은 함수로 집계한다).
#
# 밴드라운드 (렌더가 밴드마다 별도 디렉터리를 쓴다 — REG_AUDIT §8.4 (b))
#   extbase : 6씬 · 기본 CAM_DIST
#   exth    : H1·H2·H3 · bands.H
#   extlat  : L1 · bands.LAT
#   extb2   : N9·N11 · base 2차 draw (시드 20260824)
#
# 사용
#   bash experiments/v3_0823/code/run_w3_label.sh            # 전체
#   bash experiments/v3_0823/code/run_w3_label.sh exth       # 한 밴드라운드만
# =============================================================================
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
LAB="$REPO/experiments/mainrun_0819/code/labeling"
ANN="$REPO/experiments/v3_0823/annotations"
OUT="$REPO/experiments/v3_0823"
LOG="$REPO/experiments/v3_0823/logs/w3_label.log"
D="$REPO/dataset"

ONLY="${1:-}"
mkdir -p "$ANN"
export PYTHONNOUSERSITE=1
unset PYTHONPATH VIRTUAL_ENV

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

label() {  # label <on-round> <off-round> <scenes> <out>
  if [ -s "$4" ]; then say "  [skip] $(basename "$4") — 존재"; return 0; fi
  ( cd "$LAB" && $PY labeler.py --on-round "$D/$1" --off-round "$D/$2" \
        --grid gridspec_v1.json --scenes "$3" --out "$4" --workers 4 ) \
    >> "$LOG" 2>&1 \
    && say "  [ok] $(basename "$4")" || { say "  [FAIL] $(basename "$4")"; return 1; }
}

# round <tag> <stamp> <scenes>
round() {
  local tag="$1" stamp="$2" scenes="$3"
  [ -n "$ONLY" ] && [ "$ONLY" != "$tag" ] && return 0
  say "════════ $tag · $stamp · [$scenes] ════════"
  label "${stamp}_A" "${stamp}_C" "$scenes" "$ANN/w3_${tag}_ac_labels.json"
  label "${stamp}_B" "${stamp}_D" "$scenes" "$ANN/w3_${tag}_bd_labels.json"
  label "${stamp}_C" "${stamp}_A" "$scenes" "$ANN/w3_${tag}_ca_labels.json"
  label "${stamp}_D" "${stamp}_B" "$scenes" "$ANN/w3_${tag}_db_labels.json"

  say "──── h12_gates ($tag) ────"
  ( cd "$REPO" && $PY experiments/v3_0823/code/h12_gates.py \
      --root dataset --stamp "$stamp" --split test --scenes "$scenes" \
      --labels-ac "$ANN/w3_${tag}_ac_labels.json" \
      --labels-bd "$ANN/w3_${tag}_bd_labels.json" \
      --labels-ca "$ANN/w3_${tag}_ca_labels.json" \
      --labels-db "$ANN/w3_${tag}_db_labels.json" \
      --walk-z 0.0 \
      --out "$OUT/w3_gates_${tag}.json" ) 2>&1 | tee -a "$LOG"

  # 수율 판정문은 **은닉 낙차 씬(H 계열)에만** 의미가 있다. 측방 씬(L1)과
  #   무낙차 N-cue 씬(N9·N11)에서는 무의미하다 — SCENE_TEXT_BUILD §12 가 L1 에서
  #   이미 확인했고 `run_n911_label.sh` 는 아예 돌리지 않는다.
  if [ -n "${4:-}" ]; then
    say "──── strict-H 수율 ($tag · 밴드 $4) ────"
    ( cd "$REPO" && $PY experiments/v3_0823/code/h67_yield.py \
        --labels "$ANN/w3_${tag}_ac_labels.json" \
        --on "dataset/${stamp}_A" --off "dataset/${stamp}_C" \
        --band "$4" --split ext ) 2>&1 | tee -a "$LOG"
  fi
}

say "################ W3 라벨·게이트 배터리 시작 ################"
round base   260824_v3w3_extbase sceneH1,sceneH2,sceneH3,sceneL1,sceneN9,sceneN11 base
round h      260824_v3w3_exth    sceneH1,sceneH2,sceneH3                          H
round lat    260824_v3w3_extlat  sceneL1                                          ""
round b2     260824_v3w3_extb2   sceneN9,sceneN11                                 ""

say "──── W3 종합 (ALLNEG 전 팔 · (C,D) 광학차 · 모집단 회계) ────"
( cd "$REPO" && $PY experiments/v3_0823/code/w3_extra_gates.py \
    --out "$OUT/w3_extra_gates.json" ) 2>&1 | tee -a "$LOG"

# §2-8 재채점 훅의 **입력 파일**만 만든다 — 재채점은 돌리지 않는다(별도 트랙).
say "──── test-ext 매니페스트 · 분할 (ACCOUNTING §2-8 입력) ────"
( cd "$REPO" && $PY experiments/v3_0823/code/w3_manifest.py --pair ac ) 2>&1 | tee -a "$LOG"

say "──── GPU 시간 회계 ────"
( cd "$REPO" && $PY experiments/v3_0823/code/w3_gpu_account.py \
    --out "$OUT/w3_gpu_account.json" ) 2>&1 | tee -a "$LOG"
say "################ 끝 ################"
