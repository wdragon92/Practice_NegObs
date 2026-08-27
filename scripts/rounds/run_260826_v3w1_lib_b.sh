#!/bin/bash
# =============================================================================
# run_260826_v3w1_lib_b.sh — W1 B팔 렌더 (RENDER_PLAN_V3 §1.2 · §4.4.4)
#                            as amended by W1D_REPORT §6.6 / DECISIONS D72 ③ · D74 ④⑤
#
# 무엇을 찍나
# -----------
# 기존 라이브러리 씬의 **B팔** = `{"hazard_*": true, <허락된 cue_* 전부>: false}`
# = **최대 제거**(계획 §1.2 팔별 조달 규칙). 레버 집합은 씬마다 다르고,
# `experiments/v3_0823/render_configs_v3/{scene}_B.json`이 그 정본이다
# (생성기 `experiments/v3_0823/code/w1b_configs.py`, §6.6 표와 기계 대조).
#
# 왜 "재질전이 하나"가 아니라 최대 제거인가 (계획 §4.4.4)
# --------------------------------------------------------
# 초안은 B팔 레버를 `cue_material_break` 하나로 잡았다. 팔 수준 φ는 0.005였다.
# 그런데 **키별 r**을 내면 R 0.565 · Ta 0.559 · N 0.560 · Sg 0.562 · V 0.561 —
# 여섯 키 중 다섯이 퇴화한다. 난간이 A·B·C 세 팔에 다 남고 D에만 없으면 그
# 난간은 여전히 "위험의 표지"이기 때문이다. 최대 제거가 이것을 없앤다.
#
# 레버 = ON·배선 − 금지 (W1D_REPORT §6.6 · w1d_readjudication 15쌍)
# ------------------------------------------------------------------
# 금지 15쌍은 재판정에서 **구조물 또는 판정불가**로 남은 (씬, cue)다. 그 cue는
# 설정에 아예 넣지 않는다 = 기본값 ON으로 남는다. 이것이 "끌 수 없다"의 기록이다.
#
# 안 찍는 것 (D74 ⑤)
# -------------------
#   scene03(72컷) · scene04(72컷) · scene10(24컷) = **168컷 스킵**.
#   세 씬은 레버가 하나도 없어 B팔 설정이 `{hazard: true}` = A팔과 **바이트 동일**이
#   된다. 같은 프레임을 두 번 넣는 것은 자료가 아니라 학습 이중 가중이다.
#   세 씬은 부분 2×2(A/C/D)로 간다.
#   무낙차 4씬(N1·N2·N4·N5)은 on팔이 이미 C팔이라 A/B가 성립하지 않는다(계획 §1.1).
#
# 라운드 이름 (§4.3 · VG-12 · D74 계획이탈 1)
# --------------------------------------------
#   260826_v3w1_lib_B       base 밴드 (seed 20260819 = 260819_main과 짝)
#   260826_v3w1_lib_B_h     H 밴드    (seed 20260820 = 260820_boost_h와 짝)
#   260826_v3w1_lib_B_e     E 밴드    (seed 20260820 = 260820_boost_e와 짝)
#   260826_v3w1_lib_B_e2    E2 밴드   (seed 20260821 = 260820_boost_e2와 짝)
#   260826_v3w1_lib_B_smoke 씬 프로세스별 1컷 스모크
# H와 E는 시드가 같아(20260820) 컷 파일명이 글자 그대로 같다. 한 트리에 넣으면
# D23의 덮어쓰기 사고가 재발한다. 그래서 밴드마다 트리를 나눈다 — D팔과 같은 구조.
#
# 컷 회계
# -------
#   base 15씬 × 24 = 360 · H 2씬 × 24 = 48 · E 7씬 × 24 = 168 · E2 3씬 × 24 = 72
#   = **648컷** (= 계획 §1.2 표의 B팔 816컷 − D74 스킵 168컷)
#   계획 표의 "합(프레임) 792"는 scene06 보류(24컷)를 뺀 값이다. D72 ③이 보류를
#   해제했으므로 분모는 816이고, 거기서 168을 뺀 648이 본 라운드의 예산이다.
#
# 사이드카
# --------
# NEGOBS_DATA_SIDECARS=1 (depth + heightmap) + NEGOBS_SEG_SIDECAR=1 +
# **NEGOBS_SEG_STRICT=1 (의무 · D74 ④)**. B팔은 단서가 남아 있는 팔이라
# per-cut ID 마스크가 VG-06(모서리 소속)·VG-08의 전제다. D73 ①이 확정한
# `idseg_fetch="t0"` stale 결함은 이 웨이브에서 **허용되지 않는다** — 다컷 씬의
# 첫 유닛에서 stale이 잡히면 웨이브 전체를 중단한다(--strict-abort 기본 켜짐).
#
# GPU 락 / 재진입 — 마커는 유닛 단위, 렌더는 `--no-resume`
# --------------------------------------------------------
# flock은 씬 프로세스 단위. 유닛((round, scene)) DONE 마커:
# experiments/v3_0823/logs/w1b_markers/. 마커는 **산출물을 검사한 뒤에만** 찍는다
# (Isaac은 실패해도 exit 0을 낸다).
#
# `run_data_render.py`의 `--resume`는 **기본 켜짐**이고, 그 씬의 `done_conds`가
# 매니페스트에 다 있으면 `[skip] <scene> — all N conditions already done`으로
# 통째로 건너뛴다. 그런데 본 스크립트가 어떤 유닛을 다시 찍는다는 것은
# **마커가 없다 = 직전 시도가 검사를 통과하지 못했다**는 뜻이다. 그 상태에서
# 재개하면 결함이 그대로 남는다.
#
# 실측(2026-08-23): `scene20` base가 첫 컷 깊이 누락(23/24)으로 실패했는데,
# 같은 명령을 다시 돌리자 `[skip] scene20 — all 3 conditions already done`이
# 뜨고 **아무것도 다시 찍히지 않았다**(같은 실패가 그대로 재보고됐다). 그래서
# 렌더 호출에 `--no-resume`을 못 박는다. 유닛 하나는 24컷·2분 안쪽이라
# 부분 진행을 버리는 비용이 사실상 없다.
#
# 사용
#   tmux new -s w1b
#   bash scripts/rounds/run_260826_v3w1_lib_b.sh --dry-run
#   bash scripts/rounds/run_260826_v3w1_lib_b.sh --phase smoke
#   bash scripts/rounds/run_260826_v3w1_lib_b.sh --phase batch
#   bash scripts/rounds/run_260826_v3w1_lib_b.sh              # smoke -> batch
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
CFG="$REPO/experiments/v3_0823/render_configs_v3"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w1b_render.log"
MARKDIR="$LOGDIR/w1b_markers"
LOCK=/tmp/negobs_gpu.lock
CAMS=8
LOCK_WAIT=14400
LOCK_RC=201
STAMP=260826_v3w1_lib_B
SEG_STRICT="${NEGOBS_SEG_STRICT_OVERRIDE:-1}"
STRICT_ABORT="${W1B_STRICT_ABORT:-1}"

# --- 밴드 표 (render_plan_v3.json .bands · run_260820_boost.sh:135-136,203) ---
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'
BAND_E2='{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'

# --- 씬 × 밴드 -----------------------------------------------------------
# D팔 목록에서 (a) 무낙차 4씬(B팔 없음) (b) D74 스킵 3씬을 뺀 것.
S_BASE="scene01 scene02 scene06 scene08 scene09 scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3"
S_H="scene09 scene17"
S_E="scene08 scene09 scene12 scene17 scene20 sceneC1 sceneC4"
S_E2="scene12 scene20 sceneC4"
SKIPPED_D74="scene03 scene04 scene10"      # 168컷 — 회계에 명시적으로 인쇄한다

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
    print(f"arm_config {ac} != B recipe {want}"); sys.exit(1)
if not any(k.startswith("hazard_") and v is True for k, v in ac.items()):
    print(f"arm_config has no hazard_*=true — this is not a B arm: {ac}"); sys.exit(1)
leaked = [k for k in CUES if k in ac and ac[k] is False and k not in want]
if leaked:
    print(f"forbidden cue turned off: {leaked}"); sys.exit(1)
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
  cfgfile="$CFG/${scene}_B.json"
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
    say "  [FAIL] $scene: missing B config $cfgfile"
    FAILS="${FAILS}\n  ${run} ${scene}: no B config"; NFAIL=$((NFAIL+1)); return
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

  say "  [run]  $run $scene seed=$seed cams=$cams conds=$conds${sub:+ (+sub $sub)} band=${camband:-none} levers=$(python3 -c "import json,sys;print(','.join(sorted(k.replace('cue_','') for k,v in json.load(open('$cfgfile')).items() if v is False)))")"
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
say "run_260826_v3w1_lib_b.sh start — phase:$PHASE bands:[$BANDS_SEL] cams:$CAMS sidecars:depth+heightmap+idseg(strict=$SEG_STRICT)"
say "  W1 B팔 · 기존 15씬 · base 360 + H 48 + E 168 + E2 72 = 648컷"
say "  recipe {hazard_*: true, <레버>: false} = 최대 제거 (계획 §1.2·§4.4.4 · W1D §6.6)"
say "  D74 ⑤ 스킵: $SKIPPED_D74 = 168컷 (레버 0 → B ≡ A 바이트 동일)"
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
say "run_260826_v3w1_lib_b.sh done — ok=$NOK skip=$NSKIP fail=$NFAIL cuts=$NCUTS · wall $((DT/60))m $((DT%60))s"
say "  (계획 대비: 렌더 예산 648컷 · D74 스킵 168컷 · 계획 표 원안 816컷)"
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
