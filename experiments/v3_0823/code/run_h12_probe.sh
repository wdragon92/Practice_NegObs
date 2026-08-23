#!/bin/bash
# =============================================================================
# run_h12_probe.sh — sceneH1 / sceneH2 (**test-ext**) 스모크 + 4팔 프로브
#                    RENDER_PLAN_V3 §2.1 · §3.1–3.2 · WP-5 Wave A 2차 빌더 런
#
# 무엇을 찍나
#   [smoke] 씬당 1프레임 (L0 · cams 1 · hazard ON) — 프림 위생·SdfPath·사이드카 확인
#   [probe] 씬당 **4팔 × 8컷** (L0 4 + L5 4). test-ext 는 A·B·C·D 완비가 의무다(§3.1).
#             A = hazard ON · 단서 전부 ON            (기준 팔)
#             B = hazard ON · **cue_* 최대 제거**      (§1.2 B팔 레버)
#             C = hazard OFF · keep_dressing ON       (계기판 ① 의 반사실 짝)
#             D = hazard OFF · cue_* 전부 OFF          (순수 씬-연합 게이지)
#   [near]  A·C 근거리 4컷 — **비-H 대조**. 퇴화(전 프레임 H) 가 아님을 실렌더로 확인한다.
#
# 밴드   H    = {"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}   (D19 (1) · 계획 bands.H)
#        NEAR = {"d_min":1.5,"d_max":4.5,"h_min":0.6,"h_max":1.8} (두 씬 다 설계상 V)
# 사이드카 NEGOBS_DATA_SIDECARS=1 (depth + heightmap) · NEGOBS_SEG_SIDECAR=1 (ID 마스크)
#        + **NEGOBS_SEG_STRICT=1** — 다컷 라운드에서 `t0` 빠른 경로는 첫 컷 마스크를
#          그대로 복제한다(SCENE_H67_BUILD §7 실측: 8컷 `.idseg.npz` 가 바이트 동일).
#          VG-06 과 DZ §12-5 의 단서 임계 k 는 둘 다 **컷별** 마스크를 요구하므로 필수다.
#
# 규율
#   · flock -o /tmp/negobs_gpu.lock 로 GPU 직렬화 (웨이브 w1b 와 공유 — 예의 있게 끼어든다)
#   · unset PYTHONPATH VIRTUAL_ENV · conda env_isaaclab · PYTHONNOUSERSITE=1 (이 머신 필수)
#   · 라운드 스탬프는 `h67_probe.py` 의 허용목록이 렌더 전에 강제한다 (VG-12)
#   · 정본 씬·kit·드라이버 파일은 한 바이트도 고치지 않는다
#
# 사용
#   bash experiments/v3_0823/code/run_h12_probe.sh smoke
#   bash experiments/v3_0823/code/run_h12_probe.sh probe
#   bash experiments/v3_0823/code/run_h12_probe.sh near
#   bash experiments/v3_0823/code/run_h12_probe.sh probe sceneH1     # 한 씬만
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/h12_probe.log"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=10800
LOCK_RC=201
SEED=20260823
SPLIT=test                       # sceneH1·H2 는 test-ext → `vk.split_of` 가 test 를 준다
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_NEAR='{"d_min":1.5,"d_max":4.5,"h_min":0.6,"h_max":1.8}'
CONDS="${CONDS:-L0,L5}"
# **포즈 수 = CAMS 다** (컷 수가 아니다). 두 조건은 같은 시드·같은 카메라 인덱스를 쓰므로
#   포즈가 조건 간 동일하고, 수율의 유효 표본은 조건 수가 아니라 CAMS 로 결정된다
#   [R0 실측: 8컷 = 4포즈였다]. 개정 후 확정 라운드는 `CAMS=8` 로 돌려 8포즈를 확보한다.
CAMS="${CAMS:-4}"                 # × conds 수 = 팔당 컷 수

# ── 팔 레시피 ────────────────────────────────────────────────────────────────
#   B·D 는 그 씬이 실제로 가진 키만 끈다(H1 은 cue_delineator, H2 는 cue_planter_edge).
CFG_A='{"hazard_stairs": true}'
CFG_C='{"hazard_stairs": false, "keep_dressing": true}'
H1_OFF='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false, "cue_delineator": false'
H2_OFF='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false, "cue_planter_edge": false'

cfg_for() {   # cfg_for <scene> <arm>
  local s="$1" arm="$2" off
  [ "$s" = "sceneH1" ] && off="$H1_OFF" || off="$H2_OFF"
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
  local d="$REPO/dataset/$run/$SPLIT/$scene"
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

SCENES="sceneH1 sceneH2"
[ -n "$ONLY" ] && SCENES="$ONLY"

T0=$(date +%s)
say "================================================================"
say "run_h12_probe.sh start — mode=$MODE scenes=[$SCENES] seed=$SEED"
say "================================================================"

FAILS=0
case "$MODE" in
  smoke)
    for s in $SCENES; do
      render "$s" 260823_v3p5_h12smoke_A L0 1 "$CFG_A" "" || FAILS=$((FAILS+1))
    done
    ;;
  probe)
    for s in $SCENES; do
      for arm in A B C D; do
        render "$s" "260823_v3p5_h12probe_$arm" "$CONDS" "$CAMS" \
               "$(cfg_for "$s" "$arm")" "$BAND_H" || FAILS=$((FAILS+1))
      done
    done
    ;;
  near)
    for s in $SCENES; do
      for arm in A C; do
        render "$s" "260823_v3p5_h12near_$arm" L0 4 \
               "$(cfg_for "$s" "$arm")" "$BAND_NEAR" || FAILS=$((FAILS+1))
      done
    done
    ;;
  rev)
    # 씬 기하 개정 후 재프로브 (§7.4 톱업 규칙과 같은 자리, 씬당 상한 2회)
    for s in $SCENES; do
      for arm in A B C D; do
        render "$s" "260823_v3p5_h12rev_$arm" "$CONDS" "$CAMS" \
               "$(cfg_for "$s" "$arm")" "$BAND_H" || FAILS=$((FAILS+1))
      done
    done
    ;;
  regsmoke)
    # D82 ⓐ·ⓓ 설치-규정 감사 수정 후 1프레임 위생 확인
    for s in $SCENES; do
      render "$s" 260823_v3p5_h12regsmoke_A L0 1 "$CFG_A" "" || FAILS=$((FAILS+1))
    done
    ;;
  reg)
    # D82 ⓐ·ⓓ 설치-규정 감사 수정 후 **확정 4팔 라운드**.
    #   `…rev_*` 는 감사를 발동시킨 증거로 보존한다(덮어쓰지 않는다).
    for s in $SCENES; do
      for arm in A B C D; do
        render "$s" "260823_v3p5_h12reg_$arm" "$CONDS" "$CAMS" \
               "$(cfg_for "$s" "$arm")" "$BAND_H" || FAILS=$((FAILS+1))
      done
    done
    ;;
  *) say "[fatal] unknown mode '$MODE' (smoke|probe|near|rev|regsmoke|reg)"; exit 2 ;;
esac

T1=$(date +%s)
say "----------------------------------------------------------------"
for r in 260823_v3p5_h12smoke_A \
         260823_v3p5_h12probe_A 260823_v3p5_h12probe_B \
         260823_v3p5_h12probe_C 260823_v3p5_h12probe_D \
         260823_v3p5_h12near_A 260823_v3p5_h12near_C \
         260823_v3p5_h12rev_A 260823_v3p5_h12rev_B \
         260823_v3p5_h12rev_C 260823_v3p5_h12rev_D \
         260823_v3p5_h12regsmoke_A \
         260823_v3p5_h12reg_A 260823_v3p5_h12reg_B \
         260823_v3p5_h12reg_C 260823_v3p5_h12reg_D; do
  d="$REPO/dataset/$r"
  [ -d "$d" ] || continue
  say "  dataset/$r: $(find "$d" -name '*.png' | wc -l) png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name 'heightmap.npy' | wc -l) heightmap"
done
say "run_h12_probe.sh done in $(( (T1-T0)/60 )) min · 실패 $FAILS"
say "================================================================"
exit $((FAILS > 0))
