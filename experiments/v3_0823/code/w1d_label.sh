#!/usr/bin/env bash
# w1d_label.sh — W1 D팔 라벨링 + W0 재판정용 재라벨링 (CPU only).
#
# 두 묶음을 만든다. 둘 다 정본 라벨러 · 정본 그리드(gridspec_v1.json 20칸)다.
#
# (1) 생산 라벨  annotations/w1d_base.json
#     on = D팔 base 라운드 · off = 정본 구off `260819_main_off`.
#     D는 그 자체가 off팔이라 자기 안에 z_off가 없다. 여기서 나오는 발자국은
#     "구off 대비 D가 얼마나 낮은가"이고, 구off가 cue-비대칭이므로 자유결속
#     단서 자리에서 **위양성**이 난다(W0_CUECLS §3). 그래서 이 산출물은
#     프레임 스캔용이고, "D에 낙차가 남았는가"의 판정은 w1d_verify.py의
#     발자국-잔차 검사(fp_corpus ∩ 여전히 꺼진 셀)가 내린다.
#
#     **밴드 라운드(h·e·e2)는 이 스캔을 돌리지 않는다.** 그 밴드의 정본 구off는
#     "평 라운드 + g7fixM 결함 씬 3개"의 하이브리드라 완전한 트리가 없고
#     (g7fixM은 scene07/08/12만 담은 부분 트리), 평 라운드만 쓰면 scene08·s12에서
#     aabb-off ↔ fused-D의 **계기 혼합**이 되어 유령 발자국이 생긴다
#     (`fuse_heightmap.py` scene12 교훈 = 9,532칸). 밴드의 전 칸 음성 판정은
#     w1d_verify.py의 잔차 검사가 4밴드 전부에 대해 내린다.
#
# (2) 재판정 라벨  annotations/w1d_zoffD_<arm>.json
#     on = W0의 A·Bx 라운드(이미 디스크에 있음) · off = **D팔 base 라운드**.
#     D는 cue-대칭 off팔이므로 여기서 잰 Δcells_raw는 W0_CUECLS §3이 지적한
#     "참조 한쪽에만 단서가 있다"는 교락이 **구조적으로 없다**.
#     추가 GPU 0 · CPU 수 초 (D72 ②).
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LAB="$REPO/experiments/mainrun_0819/code/labeling/labeler.py"
GRID="$REPO/experiments/mainrun_0819/code/labeling/gridspec_v1.json"
OUT="$REPO/experiments/v3_0823/annotations"
LOG="$REPO/experiments/v3_0823/logs/w1d_label.log"
D_BASE=260826_v3w1_lib_D
mkdir -p "$OUT"

S_BASE="scene01,scene02,scene03,scene04,scene06,scene08,scene09,scene10,scene12,scene16,scene17,scene20,scene21,sceneC1,sceneC4,sceneD1,sceneD2,sceneD3,sceneN1,sceneN2,sceneN4,sceneN5"
S_H="scene09,scene17"
S_E="scene03,scene04,scene08,scene09,scene12,scene17,scene20,sceneC1,sceneC4"
S_E2="scene03,scene04,scene12,scene20,sceneC4"

# --- (1) 생산 라벨 ----------------------------------------------------------
label_band() {                     # label_band <band> <D run> <off run> <scenes>
  local band="$1" on="$2" off="$3" sc="$4"
  local out="$OUT/w1d_${band}.json"
  local want have
  want=$(printf '%s' "$sc" | tr ',' '\n' | grep -c .)
  have=$(ls -d "$REPO/dataset/${on}"/*/*/ 2>/dev/null | wc -l)
  if [ "$have" != "$want" ]; then
    echo "[hold] band $band — 렌더 $have/$want 씬만 존재, 라벨링 보류"; return
  fi
  if [ -f "$out" ] && [ "${W1D_FORCE:-0}" != "1" ]; then
    echo "[skip] band $band — $out exists"; return
  fi
  echo "=== labeling band $band  on=$on  off=$off  ($want 씬)"
  python3 "$LAB" --on-round "$REPO/dataset/$on" --off-round "$REPO/dataset/$off" \
      --grid "$GRID" --out "$out" --scenes "$sc" --workers 8 2>&1 | tee -a "$LOG"
}

label_band base "$D_BASE" 260819_main_off "$S_BASE"
: "밴드 라운드는 위 주석의 사유로 스캔하지 않는다 (S_H=$S_H · S_E=$S_E · S_E2=$S_E2)"

# --- (2) 재판정 라벨: W0 렌더물을 D를 z_off로 다시 라벨링 -------------------
A_SCENES=scene01,scene02,scene03,scene04,scene06,scene08,scene09,scene10,scene16,scene21,sceneC1,sceneC4,sceneD1,sceneD2,sceneD3,sceneN1,sceneN2,sceneN4,sceneN5
declare -A SC=(
  [A]="$A_SCENES"
  [Brail]="scene01,scene02,scene06,scene08,scene10,scene16,scene21,sceneC1,sceneC4"
  [Bnose]="scene02,scene16,scene21,sceneC1,sceneD1"
  [Btact]="sceneC1,sceneC4"
  [Bmatl]="scene06,sceneN1,sceneN2,sceneN5"
  [Bdress]="$A_SCENES"
)
NDBASE=$(ls -d "$REPO/dataset/${D_BASE}"/*/*/ 2>/dev/null | wc -l)
if [ "$NDBASE" != "22" ]; then
  echo "[hold] 재판정 — D팔 base 라운드가 $NDBASE/22 씬만 존재. 부분 렌더 위에서 판정하지 않는다."
  echo "W1D_LABEL_PARTIAL"; exit 0
fi
for arm in A Brail Bnose Btact Bmatl Bdress; do
  out="$OUT/w1d_zoffD_${arm}.json"
  want=$(printf '%s' "${SC[$arm]}" | tr ',' '\n' | grep -c .)
  have=$(ls -d "$REPO/dataset/260825_v3w0_cuecls_${arm}"/*/*/ 2>/dev/null | wc -l)
  if [ "$have" != "$want" ]; then
    echo "[hold] $arm — W0 렌더 $have/$want 씬만 존재, 라벨링 보류"; continue
  fi
  if [ -f "$out" ] && [ "${W1D_FORCE:-0}" != "1" ]; then
    echo "[skip] $arm — $out exists"; continue
  fi
  echo "=== relabelling W0 $arm with z_off = $D_BASE ($want 씬)"
  python3 "$LAB" --on-round "$REPO/dataset/260825_v3w0_cuecls_${arm}" \
      --off-round "$REPO/dataset/${D_BASE}" --grid "$GRID" --out "$out" \
      --scenes "${SC[$arm]}" --workers 8 2>&1 | tee -a "$LOG"
done
echo "W1D_LABEL_DONE"
