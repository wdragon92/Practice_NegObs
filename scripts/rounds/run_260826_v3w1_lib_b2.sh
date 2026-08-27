#!/bin/bash
# =============================================================================
# run_260826_v3w1_lib_b2.sh — W1-B2 보충 웨이브 (T레버 보충 재렌더)
#                             DECISIONS **D75 ③** · W1B_REPORT **§8.1 · §7.2**
#
# 무엇을 다시 찍나
# ----------------
# 이미 착지한 B팔 648컷 중 **12씬 576컷**을, `cue_material_break`(T) 레버를
# **추가한** 설정으로 다시 찍는다. 정본은
# `experiments/v3_0823/render_configs_v3/{scene}_B2.json`
# (생성기 `code/w1b2_configs.py` — B 설정에 T 하나만 얹고, 그 자리가 전부
#  재질 재바인딩임을 AST로 확인한 뒤에만 쓴다).
#
#   CONFIG_B2(s) = CONFIG_B(s) ∪ { "cue_material_break": false }
#
# 왜 (W1B_REPORT §8.1)
# ---------------------
# `hazgate.py`가 cue 배선을 `if` 문 조건절에서만 수집한 탓에
# `mtl = M[a] if cfg["cue_material_break"] else M[b]` 형태의 삼항 읽기 **23칸**을
# "배선無"로 오기록했다. 그 손실이 W0 프로브 → W1-D 재판정 → §6.6 레버표 →
# W1-B 레시피까지 4단계를 타고 왔고, B팔이 T를 **6씬에서만** 껐다. T가 A·B·C에
# 남고 D에만 없으면 그 재질전이는 여전히 "위험의 표지"이므로 **T키의 |r|이
# 0.3100**으로 VG-09 문턱 0.2를 넘겼다. 메우면 예측 **0.0442**.
#
# **신규 컷 0** — 같은 씬·같은 시드·같은 밴드·같은 조건을 다시 찍는 것이다
# (계획 §4.2: "최대 제거로 키를 더 얹어도 컷 수는 늘지 않는다").
#
# VG-01 안전이 "구성상"인 이유
# ----------------------------
# 추가하는 13자리가 전부 `M[a] if cfg[k] else M[b]` — **재질 재바인딩 전용**이라
# 프림이 하나도 생성·삭제되지 않는다. 계획 §1.2의 바닥 규칙이 그대로 적용된다.
# 그래도 게이트 배터리로 **실증**한다(`code/w1b2_verify.py`).
#
# 라운드 이름 — **착지한 B 라운드를 절대 덮어쓰지 않는다** (VG-12)
# -----------------------------------------------------------------
#   260826_v3w1_lib_B2       base  (seed 20260819)   12씬 × 24 = 288컷
#   260826_v3w1_lib_B2_h     H     (seed 20260820)    2씬 × 24 =  48컷
#   260826_v3w1_lib_B2_e     E     (seed 20260820)    7씬 × 24 = 168컷
#   260826_v3w1_lib_B2_e2    E2    (seed 20260821)    3씬 × 24 =  72컷
#   260826_v3w1_lib_B2_smoke 씬 프로세스별 1컷 스모크
#   합 **576컷**. 코퍼스 매니페스트는 이 12씬에 대해 B2를 가리킨다.
#   나머지 3씬(scene01·scene06·sceneD2)은 T가 이미 B 레버에 있었으므로
#   **B 라운드 그대로 쓴다** — 다시 찍지 않는다.
#
# 사이드카 · 락 · 재진입: B 러너와 동일 (NEGOBS_SEG_STRICT=1 의무 · flock ·
# 유닛 DONE 마커는 산출물을 검사한 뒤에만 · 렌더 호출에 `--no-resume` 못 박음).
#
# 사용
#   tmux new -s w1b2
#   bash scripts/rounds/run_260826_v3w1_lib_b2.sh --dry-run
#   bash scripts/rounds/run_260826_v3w1_lib_b2.sh              # smoke -> batch
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
CFG="$REPO/experiments/v3_0823/render_configs_v3"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w1b2_render.log"
MARKDIR="$LOGDIR/w1b2_markers"
LOCK=/tmp/negobs_gpu.lock
CAMS=8
LOCK_WAIT=14400
LOCK_RC=201
STAMP=260826_v3w1_lib_B2
SEG_STRICT="${NEGOBS_SEG_STRICT_OVERRIDE:-1}"
STRICT_ABORT="${W1B2_STRICT_ABORT:-1}"

# --- 밴드 표 (render_plan_v3.json .bands · run_260820_boost.sh:135-136,203) ---
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'
BAND_E2='{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'

# --- 씬 × 밴드 -----------------------------------------------------------
# D팔 목록에서 (a) 무낙차 4씬(B팔 없음) (b) D74 스킵 3씬을 뺀 것.
S_BASE="scene02 scene08 scene09 scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD3"
S_H="scene09 scene17"
S_E="scene08 scene09 scene12 scene17 scene20 sceneC1 sceneC4"
S_E2="scene12 scene20 sceneC4"
KEPT_B="scene01 scene06 sceneD2"           # T가 이미 B 레버 -> B 라운드 그대로
SKIPPED_D74="scene03 scene04 scene10"      # D74 (5) 168컷 스킵 — B2에서도 대상 아님

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
    print(f"arm_config {ac} != B2 recipe {want}"); sys.exit(1)
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
  cfgfile="$CFG/${scene}_B2.json"
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
    say "  [FAIL] $scene: missing B2 config $cfgfile"
    FAILS="${FAILS}\n  ${run} ${scene}: no B2 config"; NFAIL=$((NFAIL+1)); return
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
say "run_260826_v3w1_lib_b2.sh start — phase:$PHASE bands:[$BANDS_SEL] cams:$CAMS sidecars:depth+heightmap+idseg(strict=$SEG_STRICT)"
say "  W1-B2 T레버 보충 · 12씬 · base 288 + H 48 + E 168 + E2 72 = 576컷 (신규 컷 0)"
say "  recipe CONFIG_B2 = CONFIG_B + {cue_material_break: false} (D75 ③ · W1B §8.1)"
say "  B 그대로 쓰는 씬: $KEPT_B (T가 이미 레버) · D74 ⑤ 스킵: $SKIPPED_D74"
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
say "run_260826_v3w1_lib_b2.sh done — ok=$NOK skip=$NSKIP fail=$NFAIL cuts=$NCUTS · wall $((DT/60))m $((DT%60))s"
say "  (예산 576컷 · 착지한 B 라운드는 건드리지 않는다 — 별 트리)"
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
