#!/bin/bash
# =============================================================================
# run_h67_probe.sh — sceneH6 / sceneH7 스모크 + H밴드 프로브 (P-5, RENDER_PLAN_V3 §3.5)
#
# 무엇을 찍나
#   [smoke] 씬당 1프레임 (L0 · cams 1 · hazard ON) — 프림 위생·SdfPath·사이드카 확인
#   [probe] 씬당 H밴드 8컷 × 2팔 (A = hazard ON / C = hazard OFF·단서 유지)
#           라벨러가 요구하는 **양팔**이 갖춰져야 footprint v2(z_off − z_on)가 성립한다.
#
# 밴드   H = {"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}  (D19 (1) · 계획 bands.H)
# 사이드카 NEGOBS_DATA_SIDECARS=1 (depth + heightmap) · NEGOBS_SEG_SIDECAR=1 (ID 마스크)
#
# 규율
#   · flock -o /tmp/negobs_gpu.lock 로 GPU 직렬화 (다른 웨이브가 잡고 있으면 큐잉)
#   · unset PYTHONPATH VIRTUAL_ENV · conda env_isaaclab · PYTHONNOUSERSITE=1 (이 머신 필수)
#   · 라운드 스탬프는 `h67_probe.py` 의 허용목록이 렌더 전에 강제한다 (VG-12)
#   · 정본 씬·kit 파일은 한 바이트도 고치지 않는다
#
# 사용
#   bash experiments/v3_0823/code/run_h67_probe.sh smoke
#   bash experiments/v3_0823/code/run_h67_probe.sh probe
#   bash experiments/v3_0823/code/run_h67_probe.sh probe sceneH6      # 한 씬만
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/h67_probe.log"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=7200
LOCK_RC=201
SEED=20260823
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'

MODE="${1:-smoke}"
ONLY="${2:-}"

mkdir -p "$LOGDIR"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# render <scene> <run> <cams> <config-json> <band-json|""> [extra-flags]
render() {
  local scene="$1" run="$2" cams="$3" cfg="$4" band="$5" extra="${6:-}"
  say "  [render] $scene run=$run cams=$cams cfg=$cfg band=${band:-default}"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=1
python3 experiments/v3_0823/code/h67_probe.py \
        --scene '$scene' --run '$run' --conds L0 --cams $cams \
        --seed $SEED --config '$cfg' --band '$band' $extra" >> "$LOG" 2>&1
  local rc=$?
  if [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $scene $run — ${LOCK_WAIT}s 안에 GPU 락 못 얻음"
    return 1
  fi
  # rc 만으로 판정하지 않는다. Isaac 의 `fastShutdown` 경로는 씬이 예외로 죽어도
  #   프로세스 종료코드를 0 으로 돌려주는 일이 있다(설계 시 실측: sceneH6 의
  #   ground_kit U2 게이트 위반이 rc=0 으로 보고됐다). **산출물이 판정한다.**
  local d="$REPO/dataset/$run/val/$scene"
  local n_png n_dep n_seg n_hm
  n_png=$(find "$d" -name '*.png' 2>/dev/null | wc -l)
  n_dep=$(find "$d" -name '*.depth.npy' 2>/dev/null | wc -l)
  n_seg=$(find "$d" -name '*.idseg.npz' 2>/dev/null | wc -l)
  n_hm=$(find "$d" -name 'heightmap.npy' 2>/dev/null | wc -l)
  if [ "$n_png" -ge "$cams" ] && [ "$n_dep" -ge "$cams" ] \
     && [ "$n_seg" -ge "$cams" ] && [ "$n_hm" -ge 1 ]; then
    say "  [ok]   $scene $run rc=$rc · png $n_png · depth $n_dep · idseg $n_seg · hm $n_hm"
    return 0
  fi
  say "  [FAIL] $scene $run rc=$rc · png $n_png/$cams · depth $n_dep · idseg $n_seg · hm $n_hm"
  return 1
}

SCENES="sceneH6 sceneH7"
[ -n "$ONLY" ] && SCENES="$ONLY"

T0=$(date +%s)
say "================================================================"
say "run_h67_probe.sh start — mode=$MODE scenes=[$SCENES] seed=$SEED"
say "================================================================"

FAILS=0
case "$MODE" in
  smoke)
    for s in $SCENES; do
      render "$s" 260823_v3p5_h67smoke_A 1 '{"hazard_stairs": true}' "" || FAILS=$((FAILS+1))
    done
    ;;
  probe)
    for s in $SCENES; do
      render "$s" 260823_v3p5_h67probe_A 8 '{"hazard_stairs": true}' "$BAND_H" || FAILS=$((FAILS+1))
      render "$s" 260823_v3p5_h67probe_C 8 '{"hazard_stairs": false, "keep_dressing": true}' "$BAND_H" || FAILS=$((FAILS+1))
    done
    ;;
  segstrict)
    # ID 마스크 stale-frame 결함 검증용 A팔 재렌더 (`--seg-strict`).
    #   기하·시드·밴드가 probe 와 **완전히 같으므로** 라벨은 probe_C 와 짝지어 그대로 쓴다.
    for s in $SCENES; do
      render "$s" 260823_v3p5_h67rev_A 8 '{"hazard_stairs": true}' "$BAND_H" "--seg-strict" \
        || FAILS=$((FAILS+1))
    done
    ;;
  rev)
    # 씬 기하 개정 후 재프로브 (§3.5 톱업 규칙과 같은 자리, 씬당 상한 2회)
    for s in $SCENES; do
      render "$s" 260823_v3p5_h67rev_A 8 '{"hazard_stairs": true}' "$BAND_H" || FAILS=$((FAILS+1))
      render "$s" 260823_v3p5_h67rev_C 8 '{"hazard_stairs": false, "keep_dressing": true}' "$BAND_H" || FAILS=$((FAILS+1))
    done
    ;;
  *) say "[fatal] unknown mode '$MODE' (smoke|probe|segstrict|rev)"; exit 2 ;;
esac

T1=$(date +%s)
say "----------------------------------------------------------------"
for r in 260823_v3p5_h67smoke_A 260823_v3p5_h67probe_A 260823_v3p5_h67probe_C \
         260823_v3p5_h67rev_A 260823_v3p5_h67rev_C; do
  d="$REPO/dataset/$r"
  [ -d "$d" ] || continue
  say "  dataset/$r: $(find "$d" -name '*.png' | wc -l) png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name 'heightmap.npy' | wc -l) heightmap"
done
say "run_h67_probe.sh done in $(( (T1-T0)/60 )) min · 실패 $FAILS"
say "================================================================"
exit $((FAILS > 0))
