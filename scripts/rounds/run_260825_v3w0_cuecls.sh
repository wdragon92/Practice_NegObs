#!/bin/bash
# =============================================================================
# run_260825_v3w0_cuecls.sh — W0 구조물/장식 분류 프로브 (RENDER_PLAN_V3 §4.2 · §6.1 VG-CLS)
#
# 무엇을 찍나
# -----------
# (씬 × cue_*) 39쌍을 hazard=ON 아래에서 cue ON(A팔) / cue OFF(Bx팔)로 찍는다.
# 판정은 CPU에서 heightmap.npy · heightmap_meta(n_prims) · 라벨러 cells_raw ·
# cam.ground_z 로 내린다 (experiments/v3_0823/code/w0_classify.py).
#
#   구조물  = cue 제거가 낙차 기하를 바꾼다  → 토글 금지 목록 → B팔 레버 불가
#   장식    = 기하 불변                       → B팔 레버로 확정
#
# 라운드 이름 (RENDER_PLAN_V3 §4.3 · VG-12)
# ------------------------------------------
#   260825_v3w0_cuecls_A       cue 전부 ON      (19 씬 = 39쌍의 씬 합집합)
#   260825_v3w0_cuecls_Brail   cue_railing        = false  (9 씬)
#   260825_v3w0_cuecls_Bnose   cue_nosing         = false  (5 씬)
#   260825_v3w0_cuecls_Btact   cue_tactile        = false  (2 씬)
#   260825_v3w0_cuecls_Bmatl   cue_material_break = false  (4 씬)
#   260825_v3w0_cuecls_Bdress  cue_scene_dressing = false  (19 씬)
#
# 왜 Bx 팔이 5개인가: 한 씬이 최대 5개의 cue 쌍에 등장하므로 (scene, cue)마다
# 서로 다른 출력 트리가 필요하다. cue별로 라운드를 나누면 각 라운드 안에서
# 씬 이름이 유일해져 D23의 덮어쓰기 사고가 구조적으로 불가능해진다.
#
# 컷 회계
# -------
# 계획 §4.2는 39쌍 × 2팔 × 4캠 = 312컷을 예산했다. 그러나 A팔 레시피는
# (hazard ON + cue 전부 ON) 하나뿐이라 **같은 씬의 A는 쌍마다 동일**하다
# (heightmap은 씬 프로세스당 1회 산출 — 계획 §4.2 (ㄱ)). 따라서 A는 씬당 1회만
# 찍는다: A 19씬 × 4캠 = 76컷 + Bx 39쌍 × 4캠 = 156컷 = **232컷** (예산 내).
#
# 조건 · 시드
# -----------
# L0 × 4캠 (계획 §4.2). sceneC1은 L0가 계절 잠금으로 거부되므로 L4로 치환한다
# (run_260819_main.sh:151-164 · run_260820_boost.sh:189-196의 기존 치환표).
# 시드 20260819 = 260819_main과 동일 → W0의 A팔 컷은 코퍼스 A팔(base 밴드,
# cam 0-3)의 트윈이 되고, 그 자체가 무료 교차검증이 된다.
#
# 사이드카
# --------
# NEGOBS_DATA_SIDECARS=1 필수 — heightmap.npy 없이는 VG-CLS 판정이 불가능하다.
# NEGOBS_SEG_SIDECAR은 켜지 않는다: 계획은 세그 사이드카를 §12-5 k 판정과
# VG-06(모서리 소속)의 전제로만 요구하며 W0/VG-CLS는 이를 쓰지 않는다.
#
# 재진입 안전
# -----------
# 유닛((round, scene)) 단위 DONE 마커: experiments/v3_0823/logs/w0_markers/.
# 마커는 출력물을 실제로 검사한 뒤에만 찍는다 — Isaac은 실패해도 exit 0을
# 내는 일이 있으므로 종료코드를 신뢰하지 않는다(PNG 4장 · heightmap · n_prims>0
# · cuts ok=true · Bx는 SCENE_CONFIG 오버라이드 적용 로그까지 확인).
#
# 사용법
#   tmux new -s w0cls
#   bash scripts/rounds/run_260825_v3w0_cuecls.sh --dry-run
#   bash scripts/rounds/run_260825_v3w0_cuecls.sh
#   bash scripts/rounds/run_260825_v3w0_cuecls.sh --arms A          # A팔만
#   bash scripts/rounds/run_260825_v3w0_cuecls.sh --arms Brail,Bnose
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
CFG="$REPO/experiments/mainrun_0819/render_configs"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w0_cuecls_render.log"
MARKDIR="$LOGDIR/w0_markers"
LOCK=/tmp/negobs_gpu.lock
SEED="${SEED_OVERRIDE:-20260819}"
CAMS=4
LOCK_WAIT=7200
LOCK_RC=201
STAMP=260825_v3w0_cuecls

# --- 39 pairs: <scene> <cue key> <arm tag> ----------------------------------
# 출처: experiments/v3_0823/render_plan_v3.json .classification_probe.pairs
PAIRS="
scene01 cue_railing Brail
scene02 cue_railing Brail
scene06 cue_railing Brail
scene08 cue_railing Brail
scene10 cue_railing Brail
scene16 cue_railing Brail
scene21 cue_railing Brail
sceneC1 cue_railing Brail
sceneC4 cue_railing Brail
scene02 cue_nosing Bnose
scene16 cue_nosing Bnose
scene21 cue_nosing Bnose
sceneC1 cue_nosing Bnose
sceneD1 cue_nosing Bnose
sceneC1 cue_tactile Btact
sceneC4 cue_tactile Btact
scene06 cue_material_break Bmatl
sceneN1 cue_material_break Bmatl
sceneN2 cue_material_break Bmatl
sceneN5 cue_material_break Bmatl
scene01 cue_scene_dressing Bdress
scene02 cue_scene_dressing Bdress
scene03 cue_scene_dressing Bdress
scene04 cue_scene_dressing Bdress
scene06 cue_scene_dressing Bdress
scene08 cue_scene_dressing Bdress
scene09 cue_scene_dressing Bdress
scene10 cue_scene_dressing Bdress
scene16 cue_scene_dressing Bdress
scene21 cue_scene_dressing Bdress
sceneC1 cue_scene_dressing Bdress
sceneC4 cue_scene_dressing Bdress
sceneD1 cue_scene_dressing Bdress
sceneD2 cue_scene_dressing Bdress
sceneD3 cue_scene_dressing Bdress
sceneN1 cue_scene_dressing Bdress
sceneN2 cue_scene_dressing Bdress
sceneN4 cue_scene_dressing Bdress
sceneN5 cue_scene_dressing Bdress
"

ARMS_SEL="A Brail Bnose Btact Bmatl Bdress"
SCENES_OVERRIDE=""
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --arms)   ARMS_SEL="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --scenes) SCENES_OVERRIDE="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$LOGDIR" "$MARKDIR"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# --- VG-12: 라운드명 허용목록 -----------------------------------------------
guard_run_name() {
  case "$1" in
    ${STAMP}_A|${STAMP}_Brail|${STAMP}_Bnose|${STAMP}_Btact|${STAMP}_Bmatl|${STAMP}_Bdress) return 0 ;;
    *) echo "[fatal] refusing run stamp '$1' — this script only writes dataset/${STAMP}_{A,Brail,Bnose,Btact,Bmatl,Bdress}" >&2
       exit 4 ;;
  esac
}

# --- 조건: 기존 치환표 (sceneC1은 L0 계절 잠금) -----------------------------
cond_of() {
  case "$1" in
    sceneC1) echo "L4" ;;
    *)       echo "L0" ;;
  esac
}

cue_of_arm() {
  case "$1" in
    Brail)  echo "cue_railing" ;;
    Bnose)  echo "cue_nosing" ;;
    Btact)  echo "cue_tactile" ;;
    Bmatl)  echo "cue_material_break" ;;
    Bdress) echo "cue_scene_dressing" ;;
    *) echo "" ;;
  esac
}

SPLITMAP=$(bash -c "$PRE
python3 - <<'PY'
import sys; sys.path.insert(0, '$REPO')
import variation_kit as vk
for s in sorted(vk.AZ_LEDGER):
    print(s, vk.split_of(s))
PY") || { echo "[fatal] could not compute the split map" >&2; exit 3; }
split_of() { echo "$SPLITMAP" | awk -v s="$1" '$1==s{print $2}'; }

# --- 출력 검사: exit code가 아니라 산출물을 본다 (Isaac은 실패해도 0을 낸다) --
verify_unit() {                  # verify_unit <run> <scene> <cond> <cue|->
  python3 - "$REPO" "$1" "$2" "$3" "$4" <<'PY'
import json, os, sys, glob
repo, run, scene, cond, cue = sys.argv[1:6]
mf = os.path.join(repo, "dataset", run, "manifest.json")
try:
    rec = json.load(open(mf, encoding="utf-8"))["scenes"][scene]
except Exception as e:
    print(f"manifest/scene record unreadable: {type(e).__name__}"); sys.exit(1)
d = os.path.join(repo, rec["out"])
pngs = sorted(glob.glob(os.path.join(d, f"{cond}__*.png")))
if len(pngs) != 4:
    print(f"PNG count {len(pngs)} != 4 in {rec['out']}"); sys.exit(1)
for p in pngs:
    if os.path.getsize(p) < 10000:
        print(f"PNG too small: {os.path.basename(p)}"); sys.exit(1)
hm  = os.path.join(d, "heightmap.npy")
hmm = os.path.join(d, "heightmap_meta.json")
if not (os.path.exists(hm) and os.path.exists(hmm)):
    print("heightmap sidecar missing"); sys.exit(1)
meta = json.load(open(hmm, encoding="utf-8"))
# C1-probe lesson: an illegal prim name yields silent empty SdfPaths, so the
# AABB prefilter sees (almost) nothing and the scene "renders" as an empty stage.
if int(meta.get("n_prims") or 0) < 50:
    print(f"n_prims={meta.get('n_prims')} — scene load looks EMPTY (C1-probe lesson)"); sys.exit(1)
if int(meta.get("n_finite") or 0) < 100:
    print(f"heightmap n_finite={meta.get('n_finite')} — no measured ground"); sys.exit(1)
ac = meta.get("arm_config") or ""
if cue != "-" and f'"{cue}": false' not in ac.replace("False", "false"):
    print(f"arm_config does not carry {cue}=false: {ac!r}"); sys.exit(1)
if cue == "-" and any(k in ac for k in ("cue_",)):
    print(f"A arm config carries a cue key: {ac!r}"); sys.exit(1)
var = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
cu = var["cuts"]; cu = list(cu.values()) if isinstance(cu, dict) else cu
mine = [c for c in cu if c.get("cond") == cond]
nok = sum(1 for c in mine if c.get("ok"))
if nok != 4:
    print(f"variation.json: {nok}/4 ok cuts for {cond}"); sys.exit(1)
gz = {round(float(c["cam"]["ground_z"]), 6) for c in mine}
print(f"4 cuts · n_prims={meta['n_prims']} · hm {meta['n_finite']}/{meta['n_total']} "
      f"· ground_z {sorted(gz)} · {rec.get('sec_per_cut')} s/cut")
PY
}

FAILS=""; NFAIL=0; NOK=0; NSKIP=0
render_unit() {                  # render_unit <arm> <scene> <cue|->
  local arm="$1" scene="$2" cue="$3"
  local run="${STAMP}_${arm}"
  guard_run_name "$run"
  local cond; cond=$(cond_of "$scene")
  local split; split=$(split_of "$scene")
  local mark="$MARKDIR/${run}__${scene}.done"
  local base; base=$(cat "$CFG/${scene}_on.json")
  local cfgjson="$base"
  if [ "$cue" != "-" ]; then
    cfgjson=$(python3 -c "
import json,sys
d=json.loads(sys.argv[1]); d[sys.argv[2]]=False
print(json.dumps(d))" "$base" "$cue")
  fi
  local outdir="$REPO/dataset/${run}/${split}/${scene}"

  if [ -f "$mark" ]; then
    say "  [skip] $run $scene ($cue) — DONE marker present"
    NSKIP=$((NSKIP+1)); return
  fi
  if [ -z "$split" ]; then
    say "  [FAIL] $scene: not in vk.AZ_LEDGER"
    FAILS="${FAILS}\n  ${run} ${scene} ${cue}: unknown scene"; NFAIL=$((NFAIL+1)); return
  fi
  if [ "$DRY" = "1" ]; then
    say "  [dry] $run $scene cond=$cond cfg=$cfgjson -> dataset/${run}/${split}/${scene}"
    return
  fi

  say "  [run]  $run $scene cond=$cond cfg=$cfgjson"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SCENE_CONFIG='$cfgjson'
mkdir -p '$outdir'
python3 scripts/run_data_render.py --run '$run' --scenes '$scene' \
        --conds '$cond' --cams $CAMS --seed $SEED
rc=\$?
python3 scripts/stamp_round.py --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  local rc=$?

  if [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $run $scene — no GPU lock within ${LOCK_WAIT}s"
    FAILS="${FAILS}\n  ${run} ${scene} ${cue}: LOCK-TIMEOUT"; NFAIL=$((NFAIL+1)); return
  fi
  local why; why=$(verify_unit "$run" "$scene" "$cond" "$cue"); local vrc=$?
  if [ "$vrc" = "0" ]; then
    printf '%s\n' "$(date '+%F %T') rc=$rc cond=$cond cfg=$cfgjson  $why" > "$mark"
    say "  [ok]   $run $scene ($cue) rc=$rc — $why"
    NOK=$((NOK+1))
  else
    say "  [FAIL] $run $scene ($cue) rc=$rc — $why"
    FAILS="${FAILS}\n  ${run} ${scene} ${cue}: ${why}"; NFAIL=$((NFAIL+1))
  fi
}

want_arm() { case " $ARMS_SEL " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }
want_scene() {
  [ -z "$SCENES_OVERRIDE" ] && return 0
  case " $SCENES_OVERRIDE " in *" $1 "*) return 0 ;; *) return 1 ;; esac
}

T0=$(date +%s)
say "================================================================"
say "run_260825_v3w0_cuecls.sh start — arms:[$ARMS_SEL] cams:$CAMS seed:$SEED sidecars:depth+heightmap"
say "  W0 분류 프로브 (VG-CLS) · 39쌍 · A 19씬 + Bx 39유닛 = 232컷 (예산 312)"
say "================================================================"

# --- A팔: 39쌍의 씬 합집합, 씬당 1회 ---------------------------------------
if want_arm A; then
  say "--- arm A (cue 전부 ON) ---"
  for s in $(printf '%s\n' "$PAIRS" | awk 'NF{print $1}' | sort -u); do
    want_scene "$s" || continue
    render_unit A "$s" "-"
  done
fi

# --- Bx팔 ------------------------------------------------------------------
for arm in Brail Bnose Btact Bmatl Bdress; do
  want_arm "$arm" || continue
  cue=$(cue_of_arm "$arm")
  say "--- arm $arm ($cue = false) ---"
  for s in $(printf '%s\n' "$PAIRS" | awk -v a="$arm" 'NF && $3==a {print $1}'); do
    want_scene "$s" || continue
    render_unit "$arm" "$s" "$cue"
  done
done

DT=$(( $(date +%s) - T0 ))
say "================================================================"
say "run_260825_v3w0_cuecls.sh done — ok=$NOK skip=$NSKIP fail=$NFAIL · wall $((DT/60))m $((DT%60))s"
if [ "$NFAIL" != "0" ]; then
  printf 'FAILURES:%b\n' "$FAILS" | tee -a "$LOG"
  exit 1
fi
say "ALL_OK"
exit 0
