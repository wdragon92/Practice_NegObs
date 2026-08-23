#!/bin/bash
# =============================================================================
# run_260827_v3w1_lib_c.sh — W1-C (C팔 = 신off 세대) 라이브러리 렌더
#                            DECISIONS **D82 ②** (C 웨이브 게이트 해제)
#                            RENDER_PLAN_V3 **§1.2 · §1.3 · §4.2 · §4.3**
#
# 무엇을 찍나
# ----------
# 기존 22씬 중 C팔이 **신규 컷**을 갖는 18씬 **816컷**.  무낙차 4씬
# (N1·N2·N4·N5)은 on팔이 그대로 C팔이므로(계획 §1.2 `24*`) 여기 없다.
#
#   C 레시피 = {"hazard_stairs": false, "keep_dressing": true}   (이식 15씬)
#            = {"hazard_stairs": false}                          (자유 결속 3씬)
#
# 자유 결속 3씬(s01·s04·s09)에 `keep_dressing` 을 주지 않는 이유는
# CUE_COVERAGE §4-4 (1)이다 — 읽는 코드가 없는 키는 **사문**이고, 사문 키를
# 설정에 넣으면 "켰다"는 기록만 남고 그림은 안 바뀐다.  그 씬들은 결속이
# 자유라 `hazard=False` 하나로 단서가 전부 살아남는다(§2.1 결속표).
#
# 왜 C팔인가 (계획 §1.2)
# ----------------------
# C = **낙차만 없는 팔**.  단서·드레싱은 A와 같이 있고 낙차만 메워져 있다.
# (A,C)가 v3의 반사실 쌍이고, 이 쌍의 광학차가 계기판①의 영정보 층화 입력이다.
# `hazard_*=false` 만 주면 결속 `HZ`·`HZ부분` 씬에서 **단서까지 같이 지워져
# C가 D와 같아진다**(=구off).  그것을 막는 것이 `keep_dressing` 이식이다.
#
# 라운드 이름 — 밴드별 트리 (D23 교훈 · VG-12)
# --------------------------------------------
#   260827_v3w1_lib_C       base (seed 20260819)  18씬 × 24 = 432컷
#   260827_v3w1_lib_C_h     H    (seed 20260820)   2씬 × 24 =  48컷
#   260827_v3w1_lib_C_e     E    (seed 20260820)   9씬 × 24 = 216컷
#   260827_v3w1_lib_C_e2    E2   (seed 20260821)   5씬 × 24 = 120컷
#   260827_v3w1_lib_C_smoke 씬 프로세스별 1컷 스모크
#   합 **816컷**.
#
# 사이드카 · 락 · 재진입
# ----------------------
#   NEGOBS_SEG_SIDECAR=1 · NEGOBS_SEG_STRICT=1 (D74 ④ 의무).  C는 세그가
#   **하중**이다(VG-03 · VG-06 · VG-11).  **Repair-1** (`run_data_render.py`
#   의 컷별 마스크 검증 + 재페치, `code/w1c_seg_repair_note.md`)이 활성이므로
#   잔존 stale 은 조용한 나쁜 파일이 아니라 `.idseg.STALE` 마커로 남는다 —
#   이 러너는 그 마커를 **유닛 실패**로 센다.
#   flock `/tmp/negobs_gpu.lock` · 씬 프로세스 단위 · 유닛 DONE 마커는
#   **산출물을 실제로 검사한 뒤에만** 기록 · 렌더 호출에 `--no-resume` 못 박음
#   (W1B_REPORT §8.5 / C-10).
#
# 사용
#   tmux new -s w1c
#   bash scripts/rounds/run_260827_v3w1_lib_c.sh --dry-run
#   bash scripts/rounds/run_260827_v3w1_lib_c.sh              # smoke -> batch
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
CFG="$REPO/experiments/v3_0823/render_configs_v3"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w1c_render.log"
MARKDIR="$LOGDIR/w1c_markers"
LOCK=/tmp/negobs_gpu.lock
CAMS=8
LOCK_WAIT=14400
LOCK_RC=201
STAMP=260827_v3w1_lib_C
SEG_STRICT="${NEGOBS_SEG_STRICT_OVERRIDE:-1}"

# --- 밴드 표 (render_plan_v3.json .bands · run_260820_boost.sh:135-136,203) ---
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'
BAND_E2='{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'

# --- 씬 × 밴드 (계획 §1.2 표의 C열 · 신규 컷) ----------------------------
S_BASE="scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3"
S_H="scene09 scene17"
S_E="scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 sceneC4"
S_E2="scene03 scene04 scene12 scene20 sceneC4"
REUSED_N="sceneN1 sceneN2 sceneN4 sceneN5"   # on팔 재활용 = 신규 컷 0

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
# ---- arm_config == the C recipe for THIS scene ------------------------------
ac_raw = meta.get("arm_config") or ""
try:
    ac = json.loads(ac_raw.replace("False", "false").replace("True", "true")
                    .replace("'", '"'))
except Exception:
    print(f"arm_config unparseable: {ac_raw!r}"); sys.exit(1)
if ac != want:
    print(f"arm_config {ac} != C recipe {want}"); sys.exit(1)
if any(k.startswith("hazard_") and v is True for k, v in ac.items()):
    print(f"arm_config has a hazard_*=true — this is not a C arm: {ac}"); sys.exit(1)
off_cues = [k for k in CUES if ac.get(k) is False]
if off_cues:
    print(f"C arm turned a cue OFF ({off_cues}) — that is arm D, not arm C"); sys.exit(1)
if want.get("keep_dressing") and ac.get("keep_dressing") is not True:
    print(f"keep_dressing did not reach the scene: arm_config={ac}"); sys.exit(1)
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
  cfgfile="$CFG/${scene}_C.json"
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
    say "  [FAIL] $scene: missing C config $cfgfile (run code/w1c_configs.py --write)"
    FAILS="${FAILS}\n  ${run} ${scene}: no C config"; NFAIL=$((NFAIL+1)); return
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
  if [ "$vrc" != "0" ]; then
    say "  [FAIL] $run $scene — $why"
    FAILS="${FAILS}\n  ${run} ${scene}: ${why}"; NFAIL=$((NFAIL+1)); return
  fi
  : > "$mark"
  NOK=$((NOK+1)); NCUTS=$((NCUTS+nexp))
  say "  [ok]   $run $scene — $why"
}

# ---------------------------------------------------------------------------
say "=== W1-C 렌더 시작 (phase=$PHASE bands='$BANDS_SEL' dry=$DRY) ==="
say "  재활용(신규 컷 0): $REUSED_N — 계획 §1.2 C열 '24*'"

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

say "=== W1-C 렌더 종료: ok=$NOK skip=$NSKIP fail=$NFAIL cuts=$NCUTS ==="
if [ "$NFAIL" != "0" ]; then printf '%b\n' "$FAILS" | tee -a "$LOG"; exit 1; fi
exit 0
