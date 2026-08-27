#!/bin/bash
# =============================================================================
# run_260826_v3a_segfill.sh — **A팔 ID 마스크 백필** (C-2 선행요건)
#                             DECISIONS **D75 ④** · W1B_REPORT **§9 C-2 · §10 W1B-3**
#
# 문제
# ----
# v3가 재활용하는 **코퍼스 A팔 816컷**(`260819_main_on` + `260820_boost_{h,e,e2}_on`,
# 낙차 18씬 × 밴드)에 `.idseg.npz`가 **하나도 없다**. A팔은 세그 사이드카 도입
# 이전 세대라 PNG·depth·heightmap만 있다. 그런데 **VG-03**(C팔 cue 픽셀 집합 =
# A와 동일) · **VG-06**(모서리 소속, A팔 H 프레임) · **VG-11**(k 고정)이 전부
# *A팔 마스크*를 전제한다 ⇒ C 웨이브 게이트를 열 수 없다.
#
# 방법 — 재렌더하되 **PNG는 버리고 사이드카만 취한다**
# ----------------------------------------------------
#   1. A팔과 **같은 씬·같은 시드·같은 밴드·같은 조건·같은 레시피**로 다시 찍는다.
#      다른 것은 `NEGOBS_SEG_SIDECAR=1 NEGOBS_SEG_STRICT=1` 하나뿐이다.
#   2. 씬 프로세스마다 재렌더 PNG를 정본 A 프레임과 **sha256 대조**한다.
#   3. **전 컷 바이트 동일**이면 그 씬의 `.idseg.npz`만 정본 프레임 옆에 설치한다
#      (PNG·depth는 폐기). **하나라도 다르면 설치하지 않고 격리**한다 —
#      정본 픽셀을 조용히 갈아치우는 일은 없다.
#   설치·격리는 이 러너가 아니라 `code/w1b2_segfill.py`가 한다(검사와 설치의 분리).
#
# 왜 바이트 동일을 기대하나 · 왜 그래도 재는가
# --------------------------------------------
# W0_CUECLS §1의 부수 검증이 A팔 재현성을 이미 한 번 실증했다
# (`heightmap.npy` sha256 **19/19 씬** 정본과 동일 · 포즈 7키 + `cam.eye`
#  **19/19 씬 · 4/4 컷 차 0.0**). 그러나 그것은 **기하**의 재현성이고, PNG는
# PathTracing 누적 상태에 달렸다. `NEGOBS_SEG_STRICT=1`은 컷마다
# `rep.orchestrator.step()`을 한 번 더 부르므로 **후속 컷의 누적 상태를 건드릴 수
# 있다.** 그래서 기대하지 않고 **잰다** — 이것이 이 웨이브의 판정 그 자체다.
#
# 라운드 이름 — 정본 A 트리는 **한 바이트도 건드리지 않는다** (VG-12)
# --------------------------------------------------------------------
#   260826_v3a_segfill      base (seed 20260819) 18씬 × 24 = 432컷
#   260826_v3a_segfill_h    H    (seed 20260820)  2씬 × 24 =  48컷
#   260826_v3a_segfill_e    E    (seed 20260820)  9씬 × 24 = 216컷
#   260826_v3a_segfill_e2   E2   (seed 20260821)  5씬 × 24 = 120컷
#   합 **816컷 = 계획 §1.2 표의 A팔 재활용 프레임 총량**.
#   이 트리는 검사·설치가 끝나면 폐기 가능한 **스크래치**다.
#
# 레시피 = A팔 그대로: `experiments/mainrun_0819/render_configs/{scene}_on.json`
#          (= `{"hazard_*": true}` 하나뿐 — cue 키가 아예 없다)
#
# 알려진 세그 함정 둘 (W1B_REPORT §5.2 · §8.4-1)
# ----------------------------------------------
#   · **조건 경계 stale 마스크** — strict 경로에서도 남는 결정론적 1컷 결함.
#     이 러너는 stale을 유닛 실패로 본다(같은 판정자). 조건 경계에서 재발하면
#     `w1b2_segfill.py`가 컷 단위로 집계해 인쇄한다.
#   · **`마스크 > 포즈`는 stale의 반대** — 인스턴스 ID가 평가마다 재번호되기
#     때문이며, 프림 경로로 정규화하면 무해하다(VG-03을 해시로 구현하면 안 된다).
#
# 사용
#   tmux new -s w1b2
#   bash scripts/rounds/run_260826_v3a_segfill.sh --dry-run
#   bash scripts/rounds/run_260826_v3a_segfill.sh              # smoke -> batch
#   python3 experiments/v3_0823/code/w1b2_segfill.py --install
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
CFG="$REPO/experiments/mainrun_0819/render_configs"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/segfill_render.log"
MARKDIR="$LOGDIR/segfill_markers"
LOCK=/tmp/negobs_gpu.lock
CAMS=8
LOCK_WAIT=14400
LOCK_RC=201
STAMP=260826_v3a_segfill
SEG_STRICT="${NEGOBS_SEG_STRICT_OVERRIDE:-1}"
STRICT_ABORT="${SEGFILL_STRICT_ABORT:-1}"

# --- 밴드 표 (render_plan_v3.json .bands · run_260820_boost.sh:135-136,203) ---
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'
BAND_E2='{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'

# --- 씬 × 밴드 -----------------------------------------------------------
# D팔 목록에서 (a) 무낙차 4씬(B팔 없음) (b) D74 스킵 3씬을 뺀 것.
S_BASE="scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3"
S_H="scene09 scene17"
S_E="scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 sceneC4"
S_E2="scene03 scene04 scene12 scene20 sceneC4"
# 정본 A 라운드 (대조 대상 — 이 러너는 읽지도 쓰지도 않는다. w1b2_segfill.py가 쓴다)
A_BASE=260819_main_on; A_H=260820_boost_h_on; A_E=260820_boost_e_on; A_E2=260820_boost_e2_on

BANDS_SEL="base h e e2"
SCENES_OVERRIDE=""
PHASE="all"
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --bands)  BANDS_SEL="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --scenes) SCENES_OVERRIDE="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --phase)  PHASE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --no-strict-abort) STRICT_ABORT=0; shift ;;
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
    ${STAMP}|${STAMP}_h|${STAMP}_e|${STAMP}_e2|${STAMP}_smoke) return 0 ;;
    *) echo "[fatal] refusing run stamp '$1' — this script only writes dataset/${STAMP}{,_h,_e,_e2,_smoke}" >&2
       exit 4 ;;
  esac
}

run_of_band()  { case "$1" in base) echo "$STAMP" ;; *) echo "${STAMP}_$1" ;; esac; }
seed_of_band() { case "$1" in base) echo 20260819 ;; h|e) echo 20260820 ;; e2) echo 20260821 ;; esac; }
band_of()      { case "$1" in base) echo "" ;; h) echo "$BAND_H" ;; e) echo "$BAND_E" ;; e2) echo "$BAND_E2" ;; esac; }
scenes_of_band() { case "$1" in base) echo "$S_BASE" ;; h) echo "$S_H" ;; e) echo "$S_E" ;; e2) echo "$S_E2" ;; esac; }

# --- 조건: run_260819_main.sh:151-164 표 그대로 ------------------------------
conds_base() { echo "L0,L5,L7"; }
conds_sub()  { case "$1" in sceneC1) echo "L4" ;; sceneN1) echo "L3" ;; *) echo "" ;; esac; }
cond_smoke() { case "$1" in sceneC1) echo "L4" ;; *) echo "L0" ;; esac; }

SPLITMAP=$(bash -c "$PRE
python3 - <<'PY'
import sys; sys.path.insert(0, '$REPO')
import variation_kit as vk
for s in sorted(vk.AZ_LEDGER):
    print(s, vk.split_of(s))
PY") || { echo "[fatal] could not compute the split map" >&2; exit 3; }
split_of() { echo "$SPLITMAP" | awk -v s="$1" '$1==s{print $2}'; }

# --- 출력 검사: exit code가 아니라 산출물을 본다 -----------------------------
# D팔 판정자와 다른 점 둘:
#   · arm_config는 `hazard_* : true` + **그 씬의 레버만** false 여야 한다.
#     금지 cue가 false로 새어 들어가면 그건 계획 위반이므로 유닛을 죽인다.
#   · idseg stale은 경고가 아니라 **실패**다 (D74 ④ strict 의무).
verify_unit() {                  # verify_unit <run> <scene> <n_expect> <cfgfile>
  python3 - "$REPO" "$1" "$2" "$3" "$4" <<'PY'
import json, os, sys, glob, hashlib
repo, run, scene, nexp, cfgp = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
CUES = ("cue_railing", "cue_tactile", "cue_nosing", "cue_material_break",
        "cue_sign", "cue_scene_dressing")
want = json.load(open(cfgp, encoding="utf-8"))
sys.path.insert(0, repo)                     # 0827: grouped dataset/
from variation_kit import round_dir_or_flat
mf = os.path.join(round_dir_or_flat(run), "manifest.json")
try:
    rec = json.load(open(mf, encoding="utf-8"))["scenes"][scene]
except Exception as e:
    print(f"manifest/scene record unreadable: {type(e).__name__}"); sys.exit(1)
d = os.path.join(repo, rec["out"])
pngs = sorted(glob.glob(os.path.join(d, "*.png")))
if len(pngs) != nexp:
    print(f"PNG count {len(pngs)} != {nexp} in {rec['out']}"); sys.exit(1)
small = [os.path.basename(p) for p in pngs if os.path.getsize(p) < 10000]
if small:
    print(f"PNG too small: {small[:3]}"); sys.exit(1)
dep = glob.glob(os.path.join(d, "*.depth.npy"))
seg = glob.glob(os.path.join(d, "*.idseg.npz"))
if len(dep) != nexp:
    print(f"depth sidecar {len(dep)}/{nexp}"); sys.exit(1)
if len(seg) != nexp:                      # VG-08
    print(f"idseg sidecar {len(seg)}/{nexp} — VG-08 fails"); sys.exit(1)
hm  = os.path.join(d, "heightmap.npy")
hmm = os.path.join(d, "heightmap_meta.json")
if not (os.path.exists(hm) and os.path.exists(hmm)):
    print("heightmap sidecar missing"); sys.exit(1)
meta = json.load(open(hmm, encoding="utf-8"))
# C1-probe lesson: an illegal prim name yields silent empty SdfPaths, so the
# AABB prefilter sees (almost) nothing and the scene "renders" as an empty stage.
# The B arm keeps the hazard AND every forbidden cue, so it is the RICHEST of the
# four arms — a legitimate B unit can never be as thin as a D unit.  We still use
# the D-arm floor (5) because the empty-stage signature is different in kind:
# (near-)zero prims AND no measured ground AND a flat image.
if int(meta.get("n_prims") or 0) < 5:
    print(f"n_prims={meta.get('n_prims')} — scene load looks EMPTY (C1-probe lesson)"); sys.exit(1)
if int(meta.get("n_finite") or 0) < 1000:
    print(f"heightmap n_finite={meta.get('n_finite')} — no measured ground"); sys.exit(1)
try:                                   # flat image = empty stage
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(pngs[0]).convert("RGB"), dtype=np.float32)
    if float(a.std()) < 1.0:
        print(f"RGB std {a.std():.3f} — image is flat, stage looks EMPTY"); sys.exit(1)
except ImportError:
    pass
# ---- arm_config == the B recipe for THIS scene ------------------------------
ac_raw = meta.get("arm_config") or ""
try:
    ac = json.loads(ac_raw.replace("False", "false").replace("True", "true")
                    .replace("'", '"'))
except Exception:
    print(f"arm_config unparseable: {ac_raw!r}"); sys.exit(1)
if ac != want:
    print(f"arm_config {ac} != A(on) recipe {want}"); sys.exit(1)
if not any(k.startswith("hazard_") and v is True for k, v in ac.items()):
    print(f"arm_config has no hazard_*=true — this is not an A arm: {ac}"); sys.exit(1)
# The A arm names NO cue key at all: every cue must stay at its scene default.
leaked = [k for k in CUES if k in ac]
if leaked:
    print(f"A recipe must name no cue_* key, found: {leaked}"); sys.exit(1)
var = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
cu = var["cuts"]; cu = list(cu.values()) if isinstance(cu, dict) else cu
nok = sum(1 for c in cu if c.get("ok"))
if nok != nexp:
    print(f"variation.json: {nok}/{nexp} ok cuts"); sys.exit(1)
nseg = sum(1 for c in cu if c.get("idseg"))
# --- ID mask stale-frame detector (D73 (1) / D74 (4): STRICT is mandatory) ----
nid = sorted({c.get("idseg_n_ids") for c in cu if c.get("idseg_n_ids") is not None})
fetch = sorted({c.get("idseg_fetch") for c in cu if c.get("idseg_fetch")})
hs = set()
for c in cu:
    p = os.path.join(d, os.path.splitext(c["file"])[0] + ".idseg.npz")
    if os.path.isfile(p):
        hs.add(hashlib.sha256(open(p, "rb").read()).hexdigest())
stale = nexp > 1 and len(hs) == 1
if stale:
    print(f"IDSEG-STALE despite NEGOBS_SEG_STRICT=1 — {len(hs)} unique mask over "
          f"{nexp} cuts, n_ids={nid}, fetch={fetch}")
    sys.exit(1)
if "t0" in fetch:
    print(f"idseg_fetch contains 't0' (fast path) — strict was not honoured: {fetch}")
    sys.exit(1)
conds = sorted({c.get("cond") for c in cu})
gz = sorted({round(float(c["cam"]["ground_z"]), 6) for c in cu})
print(f"{nok} cuts · conds {conds} · n_prims={meta['n_prims']} · "
      f"hm {meta['n_finite']}/{meta['n_total']} · idseg {nseg}/{nexp} "
      f"{len(hs)}uniq/{len(nid)}n_ids/{fetch} · ground_z {gz[:3]} · "
      f"cfg {sorted(k for k,v in want.items() if v is False)} · {rec.get('sec_per_cut')} s/cut")
PY
}

FAILS=""; NFAIL=0; NOK=0; NSKIP=0; NCUTS=0; ABORT=0
render_unit() {                  # render_unit <band> <scene> <mode: smoke|batch>
  local band="$1" scene="$2" mode="$3"
  local run seed camband cfgfile split
  if [ "$mode" = "smoke" ]; then run="${STAMP}_smoke"; else run=$(run_of_band "$band"); fi
  guard_run_name "$run"
  seed=$(seed_of_band "$band")
  camband=$(band_of "$band")
  cfgfile="$CFG/${scene}_on.json"
  split=$(split_of "$scene")
  local mark="$MARKDIR/${run}__${scene}.done"
  local outdir
  outdir="$(negobs_round_or_flat "${run}")/${split}/${scene}"
  local cams conds sub nexp
  if [ "$mode" = "smoke" ]; then
    cams=1; conds=$(cond_smoke "$scene"); sub=""; nexp=1
  else
    cams=$CAMS; conds=$(conds_base "$scene"); sub=$(conds_sub "$scene"); nexp=24
  fi

  if [ -f "$mark" ]; then
    say "  [skip] $run $scene — DONE marker present"
    NSKIP=$((NSKIP+1)); return
  fi
  if [ -z "$split" ]; then
    say "  [FAIL] $scene: not in vk.AZ_LEDGER"
    FAILS="${FAILS}\n  ${run} ${scene}: unknown scene"; NFAIL=$((NFAIL+1)); return
  fi
  if [ ! -f "$cfgfile" ]; then
    say "  [FAIL] $scene: missing A(on) config $cfgfile"
    FAILS="${FAILS}\n  ${run} ${scene}: no A(on) config"; NFAIL=$((NFAIL+1)); return
  fi
  if [ "$DRY" = "1" ]; then
    say "  [dry] $run $scene seed=$seed cams=$cams conds=$conds sub=${sub:-none} band=${camband:-none} cfg=$(cat "$cfgfile") -> dataset/${run}/${split}/${scene}"
    return
  fi

  local rc=0
  one_call() {                   # one_call <conds>
    flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=1
export NEGOBS_SEG_STRICT=$SEG_STRICT
export NEGOBS_SCENE_CONFIG=\$(cat '$cfgfile')
${camband:+export NEGOBS_CAM_BAND_OVERRIDE='$camband'}
mkdir -p '$outdir'
python3 scripts/run_data_render.py --run '$run' --scenes '$scene' \
        --conds '$1' --cams $cams --seed $seed --no-resume
rc=\$?
python3 scripts/stamp_round.py --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  }

  say "  [run]  $run $scene seed=$seed cams=$cams conds=$conds${sub:+ (+sub $sub)} band=${camband:-none} cfg=$(cat "$cfgfile")"
  one_call "$conds"; rc=$?
  if [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $run $scene — no GPU lock within ${LOCK_WAIT}s"
    FAILS="${FAILS}\n  ${run} ${scene}: LOCK-TIMEOUT"; NFAIL=$((NFAIL+1)); return
  fi
  if [ -n "$sub" ]; then
    say "  [run]  $run $scene — declared substitution for the refused condition(s): $sub"
    one_call "$sub"; rc=$?
    if [ "$rc" = "$LOCK_RC" ]; then
      say "  [LOCK] $run $scene (sub) — no GPU lock within ${LOCK_WAIT}s"
      FAILS="${FAILS}\n  ${run} ${scene}: LOCK-TIMEOUT (sub)"; NFAIL=$((NFAIL+1)); return
    fi
  fi

  local why; why=$(verify_unit "$run" "$scene" "$nexp" "$cfgfile"); local vrc=$?
  if [ "$vrc" = "0" ]; then
    printf '%s\n' "$(date '+%F %T') rc=$rc band=$band seed=$seed conds=$conds${sub:+,$sub} cfg=$(cat "$cfgfile")  $why" > "$mark"
    say "  [ok]   $run $scene rc=$rc — $why"
    NOK=$((NOK+1)); NCUTS=$((NCUTS+nexp))
  else
    say "  [FAIL] $run $scene rc=$rc — $why"
    FAILS="${FAILS}\n  ${run} ${scene}: ${why}"; NFAIL=$((NFAIL+1))
    case "$why" in
      *IDSEG-STALE*|*"strict was not honoured"*)
        if [ "$STRICT_ABORT" = "1" ]; then
          say "  [ABORT] per-cut ID 마스크가 strict 경로에서도 stale — D74 ④ 의무 위반."
          say "          웨이브를 중단한다. (해제: --no-strict-abort)"
          ABORT=1
        fi ;;
    esac
  fi
}

want_band()  { case " $BANDS_SEL " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }
want_scene() {
  [ -z "$SCENES_OVERRIDE" ] && return 0
  case " $SCENES_OVERRIDE " in *" $1 "*) return 0 ;; *) return 1 ;; esac
}

T0=$(date +%s)
say "================================================================"
say "run_260826_v3a_segfill.sh start — phase:$PHASE bands:[$BANDS_SEL] cams:$CAMS sidecars:depth+heightmap+idseg(strict=$SEG_STRICT)"
say "  A팔 세그 백필 · 18씬 · base 432 + H 48 + E 216 + E2 120 = 816컷 (스크래치 트리)"
say "  recipe = A팔 그대로 ({hazard_*: true}) · 다른 것은 SEG_SIDECAR/SEG_STRICT 뿐"
say "  정본 대조 대상: $A_BASE · $A_H · $A_E · $A_E2 (설치는 w1b2_segfill.py)"
say "================================================================"

# --- 스모크: 씬 프로세스마다 1컷 --------------------------------------------
if [ "$PHASE" = "smoke" ] || [ "$PHASE" = "all" ]; then
  say "--- phase smoke (씬당 1컷, dataset/${STAMP}_smoke) ---"
  for s in $S_BASE; do
    want_scene "$s" || continue
    render_unit base "$s" smoke
    [ "$ABORT" = "1" ] && break
  done
  if [ "$NFAIL" != "0" ]; then
    say "[stop] 스모크에서 $NFAIL 씬 실패 — 배치를 시작하지 않는다"
    printf 'FAILURES:%b\n' "$FAILS" | tee -a "$LOG"
    exit 1
  fi
fi

# --- 배치 -------------------------------------------------------------------
if [ "$PHASE" = "batch" ] || [ "$PHASE" = "all" ]; then
  for band in base h e e2; do
    want_band "$band" || continue
    [ "$ABORT" = "1" ] && break
    say "--- band $band -> dataset/$(run_of_band "$band") (seed $(seed_of_band "$band") · camband $(band_of "$band" | sed 's/^$/none/')) ---"
    for s in $(scenes_of_band "$band"); do
      want_scene "$s" || continue
      render_unit "$band" "$s" batch
      [ "$ABORT" = "1" ] && break
    done
  done
fi

DT=$(( $(date +%s) - T0 ))
say "================================================================"
say "run_260826_v3a_segfill.sh done — ok=$NOK skip=$NSKIP fail=$NFAIL cuts=$NCUTS · wall $((DT/60))m $((DT%60))s"
say "  (예산 816컷 · 정본 A 트리는 한 바이트도 건드리지 않는다)"
for r in "$STAMP" "${STAMP}_h" "${STAMP}_e" "${STAMP}_e2" "${STAMP}_smoke"; do
  d="$(negobs_round_or_flat "$r")"
  [ -d "$d" ] || continue
  say "  dataset/$r: $(find "$d" -name '*.png' | wc -l) png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name 'heightmap.npy' | wc -l) heightmap"
done
if [ "$ABORT" = "1" ]; then
  say "WAVE_ABORTED_SEG_STALE"
  printf 'FAILURES:%b\n' "$FAILS" | tee -a "$LOG"
  exit 3
fi
if [ "$NFAIL" != "0" ]; then
  printf 'FAILURES:%b\n' "$FAILS" | tee -a "$LOG"
  exit 1
fi
say "ALL_OK"
exit 0
