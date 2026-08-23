#!/bin/bash
# =============================================================================
# run_n911_probe.sh — sceneN9 / sceneN11 (**test-ext · N-cue**) 스모크 + 4팔 프로브
#                     RENDER_PLAN_V3 §2.4 · §3.1–3.2 · WP-5 Wave A **4차 빌더 런**
#                     (§8 결재 1 A안 순서의 마지막 두 씬 — 이 런으로 A안이 닫힌다)
#
# 무엇을 찍나
#   [smoke] 씬당 1프레임 (L0 · cams 1 · hazard ON) — 프림 위생·SdfPath·사이드카 확인
#   [probe] 씬당 **4팔 × 16컷**(L0 8 + L5 8 = **8포즈**). test-ext 는 A·B·C·D 완비가
#           의무다(§3.1). 유효 표본은 컷 수가 아니라 **포즈 수**이고 두 조건이 포즈를
#           공유하므로 CAMS 가 곧 포즈 수다(SCENE_TEXT_BUILD §9.3) ⇒ CAMS=8.
#   [b2]    **`base2`** — 계획 §3.2 가 N-cue 씬에 배정한 두 번째 밴드다. `base2` 는
#           별도 (d,h) 사양이 아니라 **같은 base 지지집합의 2차 draw** 이므로
#           밴드 오버라이드 없이 **시드만 바꿔** 찍는다(SEED+1). 4팔 × 8컷.
#
# **N-cue 씬의 팔 사상 — H 씬과 다르다** (계획 §1.0 "팔의 이름은 레시피, 판정은 사실")
#   무낙차 씬의 `hazard_*` 키는 낙차가 아니라 **함정을 짓는다**. 두 씬 다 그 토글이
#   만드는 표고차가 임계 0.30 m 미만이므로 **네 팔 전부 GT 올-음성**이고, 사실 수준의
#   2×2 에서는 A·C 가 둘 다 C팔(단서 有·위험 無), B·D 가 둘 다 D팔이다.
#
#     레시피 팔   hazard_*        cue_*            사실 판정   표고차
#     A           True            전부 ON          **C**       N9 0.200 / N11 0.150
#     B           True            전부 OFF         **D**       동상
#     C           False (+keep)   ON 유지          **C**       0 (반사실 채움면)
#     D           False           전부 OFF         **D**       0
#
#   ⇒ 계기판 ③(용량-반응)이 쓰는 대조는 위험 축이 아니라 **단서 축 (C,D)** 다.
#      (A,C) 광학차는 "차도가 0.20 m 내려가 있나 / 식재대가 0.15 m 파여 있나"만 재는
#      부수 로그다. 게이트 스크립트가 둘 다 인쇄한다.
#
#   **hazard_* 키 이름이 씬마다 다르다** — sceneN1/N5 선례(`hazard_shadow_band`,
#   `hazard_flush_grating`)를 따라 함정의 이름을 쓴다:
#     sceneN9   `hazard_platform_edge`   (승강장 경계 연석 0.200 m)
#     sceneN11  `hazard_planting_bed`    (연속 식재대 토양면 −0.150 m)
#
# 밴드: **두 씬 다 base 지지집합**(`CAM_DIST` 기본값 d LogU[1.2,12] · h U[0.25,1.90]).
#       밴드 오버라이드를 주지 않는다 — N-cue 씬은 은닉 밴드도 측방 밴드도 쓰지 않는다
#       (계획 §3.2 표: `base, base2`).
#
# 사이드카 NEGOBS_DATA_SIDECARS=1 (depth + heightmap) · NEGOBS_SEG_SIDECAR=1 (ID 마스크)
#        + **NEGOBS_SEG_STRICT=1** — 다컷 라운드에서 `t0` 빠른 경로는 첫 컷 마스크를
#          그대로 복제한다(SCENE_H67_BUILD §7). **§12-5 의 단서 임계 k 는 컷별 마스크를
#          요구하고, N-cue 씬에서는 그 k 게이트가 판정층이므로 절대 생략 불가**다.
#
# 규율
#   · flock -o /tmp/negobs_gpu.lock 로 GPU 직렬화 (다른 웨이브와 공유 — 라운드를
#     8–16컷으로 잘게 끊어 상대를 굶기지 않는다)
#   · unset PYTHONPATH VIRTUAL_ENV · conda env_isaaclab · PYTHONNOUSERSITE=1 (이 머신 필수)
#   · 라운드 스탬프는 `h67_probe.py` 의 허용목록이 렌더 전에 강제한다 (VG-12)
#   · 정본 씬·kit·드라이버 파일은 한 바이트도 고치지 않는다
#   · **resume-safe DONE 마커** — 이미 산출물이 완성된 (씬,라운드)는 건너뛴다
#
# 사용
#   bash experiments/v3_0823/code/run_n911_probe.sh smoke
#   CAMS=8 bash experiments/v3_0823/code/run_n911_probe.sh probe
#   CAMS=8 bash experiments/v3_0823/code/run_n911_probe.sh rev sceneN9   # 개정 후 한 씬만
#   CAMS=4 bash experiments/v3_0823/code/run_n911_probe.sh b2
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/n911_probe.log"
MARK="$REPO/experiments/v3_0823/markers"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=14400
LOCK_RC=201
SEED=20260823
SEED_B2=20260824              # `base2` = 같은 지지집합의 **2차 draw** (시드만 다르다)
SPLIT=test                    # sceneN9·N11 은 test-ext → `vk.split_of` 가 test 를 준다
CONDS="${CONDS:-L0,L5}"
CAMS="${CAMS:-8}"             # = **포즈 수**. × conds 수 = 팔당 컷 수

# ── 팔 레시피 ────────────────────────────────────────────────────────────────
#   B·D 는 그 씬이 실제로 가진 13개 cue 키를 전부 끈다.
#   (기본 OFF 키도 명시적으로 false 로 적는다 — 레시피는 선언이지 추론이 아니다.)
N9_HZ=hazard_platform_edge
N11_HZ=hazard_planting_bed
N9_OFF='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false, "cue_road_marking": false'
N11_OFF='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false, "cue_road_marking": false'

hz_for() { [ "$1" = "sceneN11" ] && echo "$N11_HZ" || echo "$N9_HZ"; }

cfg_for() {   # cfg_for <scene> <arm>
  local s="$1" arm="$2" off hz
  hz="$(hz_for "$s")"
  [ "$s" = "sceneN11" ] && off="$N11_OFF" || off="$N9_OFF"
  case "$arm" in
    A) echo "{\"$hz\": true}" ;;
    B) echo "{\"$hz\": true, $off}" ;;
    C) echo "{\"$hz\": false, \"keep_dressing\": true}" ;;
    D) echo "{\"$hz\": false, $off}" ;;
  esac
}

MODE="${1:-smoke}"
ONLY="${2:-}"

mkdir -p "$LOGDIR" "$MARK"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# render <scene> <run> <conds> <cams> <config-json> <seed>
render() {
  local scene="$1" run="$2" conds="$3" cams="$4" cfg="$5" sd="$6"
  local want=$(( cams * $(awk -F, '{print NF}' <<<"$conds") ))
  local done_mark="$MARK/${run}_${scene}.done"
  if [ -f "$done_mark" ]; then
    say "  [skip] $scene $run — DONE 마커 존재 ($done_mark)"
    return 0
  fi
  say "  [render] $scene run=$run conds=$conds cams=$cams seed=$sd (want $want cuts)"
  say "           cfg=$cfg"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=1
export NEGOBS_SEG_STRICT=1
python3 experiments/v3_0823/code/h67_probe.py \
        --scene '$scene' --run '$run' --conds '$conds' --cams $cams \
        --seed $sd --config '$cfg' --band ''" >> "$LOG" 2>&1
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
    date '+%F %T' > "$done_mark"
    return 0
  fi
  say "  [FAIL] $scene $run rc=$rc · png $n_png/$want · depth $n_dep · idseg $n_seg · hm $n_hm"
  return 1
}

SCENES="sceneN9 sceneN11"
[ -n "$ONLY" ] && SCENES="$ONLY"

T0=$(date +%s)
say "================================================================"
say "run_n911_probe.sh start — mode=$MODE scenes=[$SCENES] seed=$SEED cams=$CAMS"
say "================================================================"

FAILS=0
case "$MODE" in
  smoke)
    for s in $SCENES; do
      render "$s" 260823_v3p5_n911smoke_A L0 1 "$(cfg_for "$s" A)" $SEED \
        || FAILS=$((FAILS+1))
    done
    ;;
  probe|rev|rev2|rev3|rev4)
    STAMP=260823_v3p5_n911probe
    [ "$MODE" = "rev" ] && STAMP=260823_v3p5_n911rev
    [ "$MODE" = "rev2" ] && STAMP=260823_v3p5_n911rev2
    [ "$MODE" = "rev3" ] && STAMP=260823_v3p5_n911rev3
    [ "$MODE" = "rev4" ] && STAMP=260823_v3p5_n911rev4
    for s in $SCENES; do
      for arm in A B C D; do
        render "$s" "${STAMP}_$arm" "$CONDS" "$CAMS" "$(cfg_for "$s" "$arm")" \
               $SEED || FAILS=$((FAILS+1))
      done
    done
    ;;
  b2)
    for s in $SCENES; do
      for arm in A B C D; do
        render "$s" "260823_v3p5_n911b2_$arm" "$CONDS" "$CAMS" \
               "$(cfg_for "$s" "$arm")" $SEED_B2 || FAILS=$((FAILS+1))
      done
    done
    ;;
  *) say "[fatal] unknown mode '$MODE' (smoke|probe|rev|rev2|rev3|rev4|b2)"; exit 2 ;;
esac

T1=$(date +%s)
say "----------------------------------------------------------------"
for r in 260823_v3p5_n911smoke_A \
         260823_v3p5_n911probe_A 260823_v3p5_n911probe_B \
         260823_v3p5_n911probe_C 260823_v3p5_n911probe_D \
         260823_v3p5_n911rev_A 260823_v3p5_n911rev_B \
         260823_v3p5_n911rev_C 260823_v3p5_n911rev_D \
         260823_v3p5_n911b2_A 260823_v3p5_n911b2_B \
         260823_v3p5_n911b2_C 260823_v3p5_n911b2_D \
         260823_v3p5_n911rev2_A 260823_v3p5_n911rev2_B \
         260823_v3p5_n911rev2_C 260823_v3p5_n911rev2_D \
         260823_v3p5_n911rev3_A 260823_v3p5_n911rev3_B \
         260823_v3p5_n911rev3_C 260823_v3p5_n911rev3_D \
         260823_v3p5_n911rev4_A 260823_v3p5_n911rev4_B \
         260823_v3p5_n911rev4_C 260823_v3p5_n911rev4_D; do
  d="$REPO/dataset/$r"
  [ -d "$d" ] || continue
  say "  dataset/$r: $(find "$d" -name '*.png' | wc -l) png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name 'heightmap.npy' | wc -l) heightmap"
done
say "run_n911_probe.sh done in $(( (T1-T0)/60 )) min · 실패 $FAILS"
say "================================================================"
exit $((FAILS > 0))
