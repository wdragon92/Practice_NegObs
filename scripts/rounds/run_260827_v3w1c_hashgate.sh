#!/bin/bash
# =============================================================================
# run_260827_v3w1c_hashgate.sh — `keep_dressing` 이식 15건 기본값-무변경 렌더
#                                D82 ② 의 증명 조건
#
# 이식된 정본 씬을 **기본 설정**(A 레시피 `{"hazard_stairs": true}`)으로
# 씬당 1컷 찍는다.  대조군(BEFORE)은 재렌더하지 않는다 — 이식 이전 코드로
# 08-19 에 실제로 찍힌 정본 라운드 `260819_main_on` 이 그것이다.
# 판정은 `experiments/v3_0823/code/w1c_hashgate.py` (기하 대응 기준, D79 ②).
#
#   시드 20260819 · 조건 L0 (sceneC1 은 L4, 코퍼스와 같은 선언 치환) · --cams 1
#   → 컷 이름과 포즈가 코퍼스의 `L0__s20260819__0000` 과 동일하다.
#
# 라운드 `260827_v3w1c_hashgate` **하나만** 쓴다(VG-12).
# =============================================================================
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w1c_hashgate.log"
MARKDIR="$LOGDIR/w1c_hashgate_markers"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=14400
LOCK_RC=201
STAMP=260827_v3w1c_hashgate
SEED=20260819

SCENES="scene02 scene03 scene06 scene08 scene10 scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3"
[ $# -gt 0 ] && [ "$1" != "--dry-run" ] && SCENES="$(echo "$1" | tr ',' ' ')"
DRY=0; for a in "$@"; do [ "$a" = "--dry-run" ] && DRY=1; done

mkdir -p "$LOGDIR" "$MARKDIR"
PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'
say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

SPLITMAP=$(bash -c "$PRE
python3 - <<'PY'
import sys; sys.path.insert(0, '$REPO')
import variation_kit as vk
for s in sorted(vk.AZ_LEDGER):
    print(s, vk.split_of(s))
PY") || { echo "[fatal] split map" >&2; exit 3; }
split_of() { echo "$SPLITMAP" | awk -v s="$1" '$1==s{print $2}'; }
cond_of()  { case "$1" in sceneC1) echo "L4" ;; *) echo "L0" ;; esac; }

NOK=0; NFAIL=0; NSKIP=0
say "=== hash-gate 렌더 (기본 설정 · 씬당 1컷) ==="
for s in $SCENES; do
  split=$(split_of "$s")
  mark="$MARKDIR/${s}.done"
  outdir="$REPO/dataset/${STAMP}/${split}/${s}"
  cond=$(cond_of "$s")
  if [ -f "$mark" ]; then say "  [skip] $s"; NSKIP=$((NSKIP+1)); continue; fi
  if [ "$DRY" = "1" ]; then say "  [dry] $s split=$split cond=$cond -> $outdir"; continue; fi
  say "  [run]  $s split=$split cond=$cond seed=$SEED cfg={\"hazard_stairs\": true}"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=0
export NEGOBS_SCENE_CONFIG='{\"hazard_stairs\": true}'
mkdir -p '$outdir'
python3 scripts/run_data_render.py --run '$STAMP' --scenes '$s' \
        --conds '$cond' --cams 1 --seed $SEED --no-resume" >> "$LOG" 2>&1
  rc=$?
  if [ "$rc" = "$LOCK_RC" ]; then say "  [LOCK] $s"; NFAIL=$((NFAIL+1)); continue; fi
  n=$(ls "$outdir"/*.png 2>/dev/null | wc -l)
  if [ "$n" != "1" ] || [ ! -f "$outdir/heightmap.npy" ]; then
    say "  [FAIL] $s — png=$n heightmap=$( [ -f "$outdir/heightmap.npy" ] && echo yes || echo no ) rc=$rc"
    NFAIL=$((NFAIL+1)); continue
  fi
  : > "$mark"; NOK=$((NOK+1)); say "  [ok]   $s"
done
say "=== hash-gate 렌더 종료: ok=$NOK skip=$NSKIP fail=$NFAIL ==="
[ "$NFAIL" = "0" ] || exit 1
exit 0
