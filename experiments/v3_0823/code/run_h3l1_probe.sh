#!/bin/bash
# =============================================================================
# run_h3l1_probe.sh — sceneH3 / sceneL1 (**test-ext**) 스모크 + 4팔 프로브
#                     RENDER_PLAN_V3 §2.1·§2.3 · §3.1–3.2 · WP-5 Wave A 3차 빌더 런
#
# 무엇을 찍나
#   [smoke] 씬당 1프레임 (L0 · cams 1 · hazard ON) — 프림 위생·SdfPath·사이드카 확인
#   [probe] 씬당 **4팔 × 16컷**(L0 8 + L5 8 = **8포즈**). test-ext 는 A·B·C·D 완비가
#           의무다(§3.1). **유효 표본은 컷 수가 아니라 포즈 수**이고 두 조건이 포즈를
#           공유하므로 CAMS 가 곧 포즈 수다(SCENE_TEXT_BUILD §9.3 실측 교훈) ⇒ CAMS=8.
#             A = hazard ON · 단서 전부 ON            (기준 팔)
#             B = hazard ON · **cue_* 최대 제거**      (§1.2 B팔 레버)
#             C = hazard OFF · keep_dressing ON       (계기판 ① 의 반사실 짝)
#             D = hazard OFF · cue_* 전부 OFF          (순수 씬-연합 게이지)
#   [near]  A·C 근거리 4컷 — sceneH3 는 **비-H 대조**(퇴화 아님을 실렌더로 확인),
#           sceneL1 은 근거리에서 섹터 분포가 어떻게 이동하는지의 대조군.
#
# **밴드는 씬마다 다르다** (계획 §2.1 / §2.3)
#   sceneH3  H    = {"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}   (D19 (1) · bands.H)
#   sceneL1  LAT  = {"d_min":3,"d_max":10,"h_min":0.4,"h_max":1.4}    (§2.3 측방 밴드)
#   NEAR         = {"d_min":1.5,"d_max":4.5,"h_min":0.6,"h_max":1.8}
#
# 사이드카 NEGOBS_DATA_SIDECARS=1 (depth + heightmap) · NEGOBS_SEG_SIDECAR=1 (ID 마스크)
#        + **NEGOBS_SEG_STRICT=1** — 다컷 라운드에서 `t0` 빠른 경로는 첫 컷 마스크를
#          그대로 복제한다(SCENE_H67_BUILD §7 실측: 8컷 `.idseg.npz` 가 바이트 동일).
#          VG-06 과 DZ §12-5 의 단서 임계 k 는 둘 다 **컷별** 마스크를 요구하므로 필수다.
#
# 규율
#   · flock -o /tmp/negobs_gpu.lock 로 GPU 직렬화 (수리 웨이브 w1b2 와 공유 — 라운드를
#     8–16컷으로 잘게 끊어 상대 웨이브를 굶기지 않는다)
#   · unset PYTHONPATH VIRTUAL_ENV · conda env_isaaclab · PYTHONNOUSERSITE=1 (이 머신 필수)
#   · 라운드 스탬프는 `h67_probe.py` 의 허용목록이 렌더 전에 강제한다 (VG-12)
#   · 정본 씬·kit·드라이버 파일은 한 바이트도 고치지 않는다
#
# 사용
#   bash experiments/v3_0823/code/run_h3l1_probe.sh smoke
#   CAMS=8 bash experiments/v3_0823/code/run_h3l1_probe.sh probe
#   bash experiments/v3_0823/code/run_h3l1_probe.sh near
#   CAMS=8 bash experiments/v3_0823/code/run_h3l1_probe.sh rev sceneH3   # 개정 후 한 씬만
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/h3l1_probe.log"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=14400
LOCK_RC=201
SEED=20260823
SPLIT=test                       # sceneH3·L1 은 test-ext → `vk.split_of` 가 test 를 준다
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_LAT='{"d_min":3,"d_max":10,"h_min":0.4,"h_max":1.4}'
BAND_NEAR='{"d_min":1.5,"d_max":4.5,"h_min":0.6,"h_max":1.8}'
CONDS="${CONDS:-L0,L5}"
CAMS="${CAMS:-8}"                 # = **포즈 수**. × conds 수 = 팔당 컷 수

band_for() {   # band_for <scene>
  [ "$1" = "sceneL1" ] && echo "$BAND_LAT" || echo "$BAND_H"
}

# ── 팔 레시피 ────────────────────────────────────────────────────────────────
#   B·D 는 그 씬이 실제로 가진 13키만 끈다
#   (H3 은 cue_convex_mirror, L1 은 cue_delineator 를 16번째 키로 갖는다).
CFG_A='{"hazard_stairs": true}'
CFG_C='{"hazard_stairs": false, "keep_dressing": true}'
H3_OFF='"cue_railing": false, "cue_convex_mirror": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false'
L1_OFF='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false, "cue_delineator": false'

cfg_for() {   # cfg_for <scene> <arm>
  local s="$1" arm="$2" off
  [ "$s" = "sceneL1" ] && off="$L1_OFF" || off="$H3_OFF"
  case "$arm" in
    A) echo "$CFG_A" ;;
    B) echo "{\"hazard_stairs\": true, $off}" ;;
    C) echo "$CFG_C" ;;
    D) echo "{\"hazard_stairs\": false, $off}" ;;
  esac
}

MODE="${1:-smoke}"
ONLY="${2:-}"

mkdir -p "$LOGDIR"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# render <scene> <run> <conds> <cams> <config-json> <band-json|"">
render() {
  local scene="$1" run="$2" conds="$3" cams="$4" cfg="$5" band="$6"
  local want=$(( cams * $(awk -F, '{print NF}' <<<"$conds") ))
  say "  [render] $scene run=$run conds=$conds cams=$cams (want $want cuts)"
  say "           cfg=$cfg"
  say "           band=$band"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=1
export NEGOBS_SEG_STRICT=1
python3 experiments/v3_0823/code/h67_probe.py \
        --scene '$scene' --run '$run' --conds '$conds' --cams $cams \
        --seed $SEED --config '$cfg' --band '$band'" >> "$LOG" 2>&1
  local rc=$?
  if [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $scene $run — ${LOCK_WAIT}s 안에 GPU 락 못 얻음"
    return 1
  fi
  # rc 만으로 판정하지 않는다. Isaac 의 `fastShutdown` 경로는 씬이 예외로 죽어도
  #   종료코드 0 을 돌려주는 일이 있다(SCENE_H67_BUILD §6.2 실측). **산출물이 판정한다.**
  local d; d="$(negobs_round_or_flat "$run")/$SPLIT/$scene"
  local n_png n_dep n_seg n_hm
  n_png=$(find "$d" -name '*.png' 2>/dev/null | wc -l)
  n_dep=$(find "$d" -name '*.depth.npy' 2>/dev/null | wc -l)
  n_seg=$(find "$d" -name '*.idseg.npz' 2>/dev/null | wc -l)
  n_hm=$(find "$d" -name 'heightmap.npy' 2>/dev/null | wc -l)
  if [ "$n_png" -ge "$want" ] && [ "$n_dep" -ge "$want" ] \
     && [ "$n_seg" -ge "$want" ] && [ "$n_hm" -ge 1 ]; then
    say "  [ok]   $scene $run rc=$rc · png $n_png · depth $n_dep · idseg $n_seg · hm $n_hm"
    return 0
  fi
  say "  [FAIL] $scene $run rc=$rc · png $n_png/$want · depth $n_dep · idseg $n_seg · hm $n_hm"
  return 1
}

SCENES="sceneH3 sceneL1"
[ -n "$ONLY" ] && SCENES="$ONLY"

T0=$(date +%s)
say "================================================================"
say "run_h3l1_probe.sh start — mode=$MODE scenes=[$SCENES] seed=$SEED cams=$CAMS"
say "================================================================"

FAILS=0
case "$MODE" in
  smoke)
    for s in $SCENES; do
      render "$s" 260823_v3p5_h3l1smoke_A L0 1 "$CFG_A" "" || FAILS=$((FAILS+1))
    done
    ;;
  regsmoke)
    # D82 ⓐ·ⓓ 설치-규정 감사 수정 후 1프레임 위생 확인
    for s in $SCENES; do
      render "$s" 260823_v3p5_h3l1regsmoke_A L0 1 "$CFG_A" "" || FAILS=$((FAILS+1))
    done
    ;;
  probe|rev|reg)
    STAMP=260823_v3p5_h3l1probe
    [ "$MODE" = "rev" ] && STAMP=260823_v3p5_h3l1rev
    # D82 ⓐ·ⓓ 설치-규정 감사 수정 후 **확정 4팔 라운드**.
    #   `…rev_*` 는 감사를 발동시킨 증거로 보존한다(덮어쓰지 않는다).
    [ "$MODE" = "reg" ] && STAMP=260823_v3p5_h3l1reg
    for s in $SCENES; do
      for arm in A B C D; do
        render "$s" "${STAMP}_$arm" "$CONDS" "$CAMS" \
               "$(cfg_for "$s" "$arm")" "$(band_for "$s")" || FAILS=$((FAILS+1))
      done
    done
    ;;
  near)
    for s in $SCENES; do
      for arm in A C; do
        render "$s" "260823_v3p5_h3l1near_$arm" L0 4 \
               "$(cfg_for "$s" "$arm")" "$BAND_NEAR" || FAILS=$((FAILS+1))
      done
    done
    ;;
  *) say "[fatal] unknown mode '$MODE' (smoke|probe|rev|near|regsmoke|reg)"; exit 2 ;;
esac

T1=$(date +%s)
say "----------------------------------------------------------------"
for r in 260823_v3p5_h3l1smoke_A \
         260823_v3p5_h3l1probe_A 260823_v3p5_h3l1probe_B \
         260823_v3p5_h3l1probe_C 260823_v3p5_h3l1probe_D \
         260823_v3p5_h3l1near_A 260823_v3p5_h3l1near_C \
         260823_v3p5_h3l1rev_A 260823_v3p5_h3l1rev_B \
         260823_v3p5_h3l1rev_C 260823_v3p5_h3l1rev_D \
         260823_v3p5_h3l1regsmoke_A \
         260823_v3p5_h3l1reg_A 260823_v3p5_h3l1reg_B \
         260823_v3p5_h3l1reg_C 260823_v3p5_h3l1reg_D; do
  d="$(negobs_round_or_flat "$r")"
  [ -d "$d" ] || continue
  say "  dataset/$r: $(find "$d" -name '*.png' | wc -l) png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name 'heightmap.npy' | wc -l) heightmap"
done
say "run_h3l1_probe.sh done in $(( (T1-T0)/60 )) min · 실패 $FAILS"
say "================================================================"
exit $((FAILS > 0))
