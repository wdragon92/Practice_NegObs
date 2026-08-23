#!/bin/bash
# =============================================================================
# run_260827_v3w1_lib_b3.sh — W1-B3 (B팔 **보충 웨이브 3**) 라이브러리 렌더
#                             DECISIONS **D90 ①** (VG-09 as-built 클리어링)
#                             W1-D §6.4 세그 3차 판정 → `w1d_seg3.json`
#                             RENDER_PLAN_V3 **§1.2 · §4.5** (레버 추가 처방)
#
# 무엇을 찍나
# ----------
# 세그 3차 검정(`code/w1d_readjudicate.py --mode seg3`)이 **장식으로 확정**해
# 토글 금지에서 해제한 (씬, 단서) 쌍을 **B팔 레버에 추가**한 재렌더다.
# 레시피는 기존 B/B2 레시피의 **상위집합**(최대 제거) — 지우던 것은 그대로
# 지우고 새로 해제된 키만 더한다.
#
#   scene01  B  → B3 : + cue_railing, cue_scene_dressing
#   scene09  B2 → B3 : + cue_scene_dressing
#   scene21  B2 → B3 : + cue_railing, cue_nosing
#   sceneC1  B2 → B3 : + cue_railing, cue_scene_dressing, cue_tactile
#   sceneC4  B2 → B3 : + cue_tactile
#
# **찍지 않는 것**: scene02 V(=polar_gt 4프레임 상이 · VG-01 경성 위반) ·
# scene04 V · scene08 R · scene10 R · scene20 R · sceneC4 V 는 구조물로 남는다.
# scene03·scene10 은 B팔 자체가 없다(D74 ⑤ 부재) — 등록된 `lever_add` 집합
# 밖이므로 이 웨이브는 **건드리지 않는다**(레버 사냥 금지 · D90 ①).
#
# 라운드 이름 — 밴드별 트리 (D23 교훈 · VG-12)
# --------------------------------------------
#   260827_v3w1_lib_B3       base (seed 20260819)  5씬 × 24 = 120컷
#   260827_v3w1_lib_B3_h     H    (seed 20260820)  1씬 × 24 =  24컷
#   260827_v3w1_lib_B3_e     E    (seed 20260820)  3씬 × 24 =  72컷
#   260827_v3w1_lib_B3_e2    E2   (seed 20260821)  1씬 × 24 =  24컷
#   260827_v3w1_lib_B3_smoke 씬 프로세스별 1컷 스모크
#   합 **240컷** (기존 B/B2 프레임 수와 씬·밴드 단위로 정확히 일치).
#
# 사이드카 · 락 · 재진입
# ----------------------
#   NEGOBS_SEG_SIDECAR=1 · NEGOBS_SEG_STRICT=1 (D74 ④ 의무).
#   **Repair-1** (`run_data_render.py` 컷별 마스크 검증 + 재페치 ·
#   `code/w1c_seg_repair_note.md`)이 활성이므로 잔존 stale 은 조용한 나쁜
#   파일이 아니라 `.idseg.STALE` 마커로 남는다 — 이 러너는 그 마커와
#   `variation.json` 의 `idseg_stale` 기록을 **유닛 실패**로 센다.
#   flock `/tmp/negobs_gpu.lock` · 씬 프로세스 단위 · 유닛 DONE 마커는
#   **산출물을 실제로 검사한 뒤에만** 기록 · 렌더 호출에 `--no-resume` 못 박음.
#
# 사용
#   tmux new -s w1b3
#   bash scripts/rounds/run_260827_v3w1_lib_b3.sh --dry-run
#   bash scripts/rounds/run_260827_v3w1_lib_b3.sh --phase smoke
#   bash scripts/rounds/run_260827_v3w1_lib_b3.sh              # smoke -> batch
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
CFG="$REPO/experiments/v3_0823/render_configs_v3"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w1b3_render.log"
MARKDIR="$LOGDIR/w1b3_markers"
LOCK=/tmp/negobs_gpu.lock
CAMS=8
LOCK_WAIT=14400
LOCK_RC=201
STAMP=260827_v3w1_lib_B3
SEG_STRICT="${NEGOBS_SEG_STRICT_OVERRIDE:-1}"
STRICT_ABORT="${W1B3_STRICT_ABORT:-1}"
ABORT=0
T0=$(date +%s)

# --- 밴드 표 (render_plan_v3.json .bands · run_260820_boost.sh:135-136,203) ---
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'
BAND_E2='{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'

# --- 씬 × 밴드 (기존 B/B2 프레임의 씬·밴드 분포와 **1:1** · 매니페스트 실측) ---
S_BASE="scene01 scene09 scene21 sceneC1 sceneC4"
S_H="scene09"
S_E="scene09 sceneC1 sceneC4"
S_E2="sceneC4"
UNTOUCHED="scene02 scene06 scene08 scene12 scene16 scene17 scene20 sceneD1 sceneD2 sceneD3"  # 레시피 불변 -> B/B2 그대로
NO_B_ARM="scene03 scene04 scene10"           # D74 ⑤ 부재 · lever_add 집합 밖

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
conds_sub()  { case "$1" in sceneC1) echo "L4" ;; *) echo "" ;; esac; }
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
# B2 판정자와 다른 점 셋:
#   · arm_config 는 `hazard_* : false` 이고 **금지 cue 가 하나도 false 여서는
#     안 된다** — C팔은 단서를 전부 남기는 팔이다.  cue 가 새어 꺼지면 그건
#     C 가 아니라 D 이므로 유닛을 죽인다.
#   · `keep_dressing: true` 가 이식 15씬에서 arm_config 에 실제로 실려야 한다.
#   · Repair-1 의 `.idseg.STALE` 마커 / `idseg_stale` 레코드는 **실패**다.
#     (라운드 수준 "전 컷 동일 해시" 그물은 그대로 두되, 같은 포즈가 조건을
#      건너 반복될 때 해시가 겹치는 것은 정상이므로 — Repair-1 검증에서 실측 —
#      해시 유일성은 **포즈 유일성 대비**로 판정한다.)
verify_unit() {                  # verify_unit <run> <scene> <n_expect> <cfgfile>
  python3 - "$REPO" "$1" "$2" "$3" "$4" <<'PY'
import json, os, sys, glob, hashlib
repo, run, scene, nexp, cfgp = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
CUES = ("cue_railing", "cue_tactile", "cue_nosing", "cue_material_break",
        "cue_sign", "cue_scene_dressing")
want = json.load(open(cfgp, encoding="utf-8"))
mf = os.path.join(repo, "dataset", run, "manifest.json")
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
stale_mk = glob.glob(os.path.join(d, "*.idseg.STALE"))
if len(dep) != nexp:
    print(f"depth sidecar {len(dep)}/{nexp}"); sys.exit(1)
if stale_mk:                              # Repair-1 잔존 결함
    print(f"IDSEG-STALE markers present ({len(stale_mk)}): "
          f"{[os.path.basename(p) for p in stale_mk][:3]}"); sys.exit(1)
if len(seg) != nexp:                      # VG-08
    print(f"idseg sidecar {len(seg)}/{nexp} — VG-08 fails"); sys.exit(1)
hm  = os.path.join(d, "heightmap.npy")
hmm = os.path.join(d, "heightmap_meta.json")
if not (os.path.exists(hm) and os.path.exists(hmm)):
    print("heightmap sidecar missing"); sys.exit(1)
meta = json.load(open(hmm, encoding="utf-8"))
# C1-probe lesson: an illegal prim name yields silent empty SdfPaths, so the AABB
# prefilter sees (almost) nothing and the scene "renders" as an empty stage.
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
# ---- arm_config == the B3 recipe for THIS scene -----------------------------
ac_raw = meta.get("arm_config") or ""
try:
    ac = json.loads(ac_raw.replace("False", "false").replace("True", "true")
                    .replace("'", '"'))
except Exception:
    print(f"arm_config unparseable: {ac_raw!r}"); sys.exit(1)
if ac != want:
    print(f"arm_config {ac} != B3 recipe {want}"); sys.exit(1)
if not any(k.startswith("hazard_") and v is True for k, v in ac.items()):
    print(f"arm_config has no hazard_*=true — this is not a B arm: {ac}"); sys.exit(1)
leaked = [k for k in CUES if k in ac and ac[k] is False and k not in want]
if leaked:
    print(f"forbidden cue turned off: {leaked}"); sys.exit(1)
kept_on = [k for k in CUES if want.get(k) is False and ac.get(k) is not False]
if kept_on:
    print(f"B3 lever did not reach the scene: {kept_on}"); sys.exit(1)
var = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
cu = var["cuts"]; cu = list(cu.values()) if isinstance(cu, dict) else cu
nok = sum(1 for c in cu if c.get("ok"))
if nok != nexp:
    print(f"variation.json: {nok}/{nexp} ok cuts"); sys.exit(1)
rec_stale = [c["file"] for c in cu if c.get("idseg_stale")]
if rec_stale:
    print(f"idseg_stale recorded on {len(rec_stale)} cuts: {rec_stale[:3]}"); sys.exit(1)
nseg = sum(1 for c in cu if c.get("idseg"))
nid = sorted({c.get("idseg_n_ids") for c in cu if c.get("idseg_n_ids") is not None})
fetch = sorted({c.get("idseg_fetch") for c in cu if c.get("idseg_fetch")})
retried = sum(1 for c in cu if c.get("idseg_retry"))
# --- per-cut discriminability, judged against POSE uniqueness ----------------
#  `vk.sample_camera` ignores the condition, so `L0__000i` and `L5__000i` are
#  the SAME pose and legitimately share a mask (measured, Repair-1 validation).
#  The right predicate is therefore "unique masks >= unique poses", not
#  "unique masks == n_cuts" (W1B_REPORT §8.4 · D75 ②).
hs, poses = set(), set()
for c in cu:
    p = os.path.join(d, os.path.splitext(c["file"])[0] + ".idseg.npz")
    if os.path.isfile(p):
        hs.add(hashlib.sha256(open(p, "rb").read()).hexdigest())
    cm = c.get("cam") or {}
    poses.add((round(float(cm.get("d", 0)), 6), round(float(cm.get("h_rel", 0)), 6),
               round(float(cm.get("yaw", 0)), 6), round(float(cm.get("pitch", 0)), 6),
               round(float(cm.get("hfov", 0)), 6)))
if nexp > 1 and len(hs) < len(poses):
    print(f"per-cut seg discriminability: {len(hs)} unique masks < "
          f"{len(poses)} unique poses, n_ids={nid}, fetch={fetch}")
    sys.exit(1)
if "t0" in fetch:
    print(f"idseg_fetch contains 't0' (fast path) — strict was not honoured: {fetch}")
    sys.exit(1)
conds = sorted({c.get("cond") for c in cu})
gz = sorted({round(float(c["cam"]["ground_z"]), 6) for c in cu})
print(f"{nok} cuts · conds {conds} · n_prims={meta['n_prims']} · "
      f"hm {meta['n_finite']}/{meta['n_total']} · idseg {nseg}/{nexp} "
      f"{len(hs)}uniq/{len(poses)}pose/{len(nid)}n_ids/{fetch} · retried {retried} · "
      f"ground_z {gz[:3]} · cfg {sorted(want)} · {rec.get('sec_per_cut')} s/cut")
PY
}

FAILS=""; NFAIL=0; NOK=0; NSKIP=0; NCUTS=0
render_unit() {                  # render_unit <band> <scene> <mode: smoke|batch>
  local band="$1" scene="$2" mode="$3"
  local run seed camband cfgfile split
  if [ "$mode" = "smoke" ]; then run="${STAMP}_smoke"; else run=$(run_of_band "$band"); fi
  guard_run_name "$run"
  seed=$(seed_of_band "$band")
  camband=$(band_of "$band")
  cfgfile="$CFG/${scene}_B3.json"
  split=$(split_of "$scene")
  local mark="$MARKDIR/${run}__${scene}.done"
  local outdir="$REPO/dataset/${run}/${split}/${scene}"
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
    say "  [FAIL] $scene: missing B3 config $cfgfile (run code/w1b3_configs.py --write)"
    FAILS="${FAILS}\n  ${run} ${scene}: no B3 config"; NFAIL=$((NFAIL+1)); return
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

  say "  [run]  $run $scene seed=$seed cams=$cams conds=$conds${sub:+ (+sub $sub)} band=${camband:-none} levers=$(python3 -c "import json;print(','.join(sorted(k.replace('cue_','') for k,v in json.load(open('$cfgfile')).items() if v is False)))")"
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
  if [ "$vrc" != "0" ]; then
    say "  [FAIL] $run $scene rc=$rc — $why"
    FAILS="${FAILS}\n  ${run} ${scene}: ${why}"; NFAIL=$((NFAIL+1))
    case "$why" in
      *IDSEG-STALE*|*"strict was not honoured"*|*"idseg_stale recorded"*)
        if [ "$STRICT_ABORT" = "1" ]; then
          say "  [ABORT] 컷별 ID 마스크가 strict 경로에서도 stale — D74 ④ 의무 위반."
          say "          웨이브를 중단한다. (해제: W1B3_STRICT_ABORT=0)"
          ABORT=1
        fi ;;
    esac
    return
  fi
  printf '%s\n' "$(date '+%F %T') rc=$rc band=$band seed=$seed conds=$conds${sub:+,$sub} cfg=$(cat "$cfgfile")  $why" > "$mark"
  NOK=$((NOK+1)); NCUTS=$((NCUTS+nexp))
  say "  [ok]   $run $scene — $why"
}

# ---------------------------------------------------------------------------
say "=== W1-B3 렌더 시작 (phase=$PHASE bands='$BANDS_SEL' dry=$DRY) ==="
say "  레시피 불변(재렌더 없음): $UNTOUCHED"
say "  B팔 부재(D74 ⑤ · lever_add 밖): $NO_B_ARM"

if [ "$PHASE" = "all" ] || [ "$PHASE" = "smoke" ]; then
  say "--- 스모크 (씬 프로세스당 1컷) ---"
  SMOKE_SCENES="${SCENES_OVERRIDE:-$S_BASE}"
  for s in $SMOKE_SCENES; do render_unit base "$s" smoke; done
  if [ "$NFAIL" != "0" ] && [ "$PHASE" = "all" ]; then
    say "!!! 스모크 실패 $NFAIL 건 — 배치를 시작하지 않는다"
    printf '%b\n' "$FAILS" | tee -a "$LOG"
    exit 5
  fi
fi

if [ "$PHASE" = "all" ] || [ "$PHASE" = "batch" ]; then
  for band in $BANDS_SEL; do
    say "--- 밴드 $band (run=$(run_of_band "$band") seed=$(seed_of_band "$band")) ---"
    SC="${SCENES_OVERRIDE:-$(scenes_of_band "$band")}"
    for s in $SC; do render_unit "$band" "$s" batch; done
  done
fi

DT=$(( $(date +%s) - T0 ))
say "================================================================"
say "run_260827_v3w1_lib_b3.sh done — ok=$NOK skip=$NSKIP fail=$NFAIL cuts=$NCUTS · wall $((DT/60))m $((DT%60))s"
for r in "$STAMP" "${STAMP}_h" "${STAMP}_e" "${STAMP}_e2" "${STAMP}_smoke"; do
  d="$REPO/dataset/$r"
  [ -d "$d" ] || continue
  say "  dataset/$r: $(find "$d" -name '*.png' | wc -l) png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name '*.idseg.STALE' | wc -l) STALE · $(find "$d" -name 'heightmap.npy' | wc -l) heightmap"
done
if [ "$ABORT" = "1" ]; then
  say "WAVE_ABORTED_SEG_STALE"
  printf 'FAILURES:%b\n' "$FAILS" | tee -a "$LOG"
  exit 3
fi
if [ "$NFAIL" != "0" ]; then printf 'FAILURES:%b\n' "$FAILS" | tee -a "$LOG"; exit 1; fi
say "ALL_OK"
exit 0
