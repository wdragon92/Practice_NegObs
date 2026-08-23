#!/bin/bash
# =============================================================================
# run_260826_v3w1_lib_d.sh — W1 D팔 렌더 (RENDER_PLAN_V3 §1.2 · §4.2 · §4.3)
#                            as amended by W0_CUECLS §8 / DECISIONS D72 ②
#
# 무엇을 찍나
# -----------
# 기존 22씬의 **D팔** = `{"hazard_*": false, "cue_*": false}` (6키 전부).
# 계획 §1.2의 D팔 레시피 그대로. B팔·C팔은 이 스크립트가 건드리지 않는다.
#
# 왜 D를 먼저 찍는가 (D72 ②)
# ---------------------------
# W0의 VG-CLS는 39쌍 중 16쌍을 판정불가로 남겼다. 원인은 참조로 쓴 구off
# `260819_main_off`가 **cue-비대칭**이라는 것(위험결속 단서만 지우고 자유결속
# 단서는 남긴다). D팔은 cue-대칭 off팔이므로 D를 z_off로 두면 그 16쌍이
# **추가 GPU 0 · CPU 6초**로 닫힌다. D팔 레시피는 VG-CLS 결과에 전혀 의존하지
# 않으므로 지금 찍을 수 있다.
#
# 라운드 이름 (§4.3 · VG-12)
# ---------------------------
#   260826_v3w1_lib_D       base 밴드 (seed 20260819 = 260819_main과 짝)
#   260826_v3w1_lib_D_h     H 밴드    (seed 20260820 = 260820_boost_h와 짝)
#   260826_v3w1_lib_D_e     E 밴드    (seed 20260820 = 260820_boost_e와 짝)
#   260826_v3w1_lib_D_e2    E2 밴드   (seed 20260821 = 260820_boost_e2와 짝)
#   260826_v3w1_lib_D_smoke 씬 프로세스별 1컷 스모크
#
# 계획 §4.3 표는 D팔에 라운드 스탬프를 **하나만** 적어 두었으나, H와 E는
# 시드가 같아(20260820) 컷 파일명이 글자 그대로 같다. 한 트리에 넣으면 D23이
# 남긴 그 덮어쓰기 사고가 그대로 재발한다. 그래서 밴드마다 트리를 나눈다 —
# 팔 접미사 `D`는 모든 스탬프에 남아 있으므로 VG-12 문면을 지킨다.
#
# 컷 회계
# -------
#   base 22씬 × 24 = 528 · H 2씬 × 24 = 48 · E 9씬 × 24 = 216 · E2 5씬 × 24 = 120
#   = **912컷** (= 계획 §1.2 표의 D팔 "합(프레임) 912")
# 계획 §1.2의 "신규 컷 816 (+96 구off 재활용)"에서 재활용분 96컷(s02 24 + s03 72)도
# 신규로 찍는다. 사유는 아래 두 줄:
#   · s02 — VG-04 **불통과**(`cue_scene_dressing` 결속 `hz?`). 계획 §1.4가
#           "통과 실패 시 96컷을 신규로 찍으면 그만"이라 한 그 경로다.
#   · s03 — VG-04 통과(재활용 적격)이지만, s03 `cue_scene_dressing`은 W0의
#           **판정불가 16쌍 중 하나**다. 그 재판정의 참조를 구off로 되돌리면
#           재판정 자체가 무의미해진다. 또한 D팔을 한 세대로 균질화해 두는 편이
#           ACCOUNTING §4.1 "비균질 세대" 재발을 막는다. 실측 부수 효과로
#           s03의 D 높이맵 sha256 = 구off와 같은지가 VG-04의 **실증**이 된다.
#
# 사이드카
# --------
# NEGOBS_DATA_SIDECARS=1 (depth + heightmap) **및** NEGOBS_SEG_SIDECAR=1.
# W0와 다른 점이 여기다 — W1은 생산 프레임이라 `.idseg.npz`가 §12-5 k 판정과
# VG-06(모서리 소속)의 전제다(계획 §6.3 · VG-08).
#
# NEGOBS_SEG_STRICT=1 — ID 마스크 stale-frame 결함 우회 (D73 ① · h67build
# SCENE_H67_BUILD.md §7). `_seg_fetch`의 사다리 첫 단 `t0`는 추가 tick이 0회라
# 애노테이터를 다시 평가시키지 않는다. 그래서 **다컷 씬 프로세스에서 전 컷의
# `.idseg.npz`가 바이트 동일**해진다(깊이는 정상 갱신). 본 라운드에서도 실측으로
# 확인했다 — scene01·02·03·04에서 6컷의 idseg 해시가 1종, depth 해시는 6종,
# `idseg_n_ids`는 24컷 전부 상수. P-5 스모크가 1컷이라 못 잡은 결함이다.
# 실측 비용은 잡음 안(5.101→5.225 · 5.689→5.050 s/컷).
# 끄려면 `NEGOBS_SEG_STRICT_OVERRIDE=0`.
#
# **이미 마커가 찍힌 6씬(scene01·02·03·04·06·08)은 재렌더하지 않는다** — D팔은
# 단서도 위험도 없어 세그가 W1-D의 어떤 게이트에도 하중을 걸지 않는다
# (§12-5 k는 자명하게 0, VG-06은 A팔 H 프레임에 적용). 대신 그 6씬의 stale을
# 보고서에 명시한다.
#
# GPU 락
# ------
# flock은 **씬 프로세스 단위로** 잡고 놓는다. 씬 빌더(h67build)가 프로세스
# 사이에 끼어들 수 있어야 하기 때문이다. 라운드 전체를 한 번에 잡지 않는다.
#
# 재진입 안전
# -----------
# 유닛((round, scene)) DONE 마커: experiments/v3_0823/logs/w1d_markers/.
# 마커는 산출물을 실제로 검사한 뒤에만 찍는다(Isaac은 실패해도 exit 0을 낸다).
#
# 사용법
#   tmux new -s w1d
#   bash scripts/rounds/run_260826_v3w1_lib_d.sh --dry-run
#   bash scripts/rounds/run_260826_v3w1_lib_d.sh --phase smoke
#   bash scripts/rounds/run_260826_v3w1_lib_d.sh --phase batch
#   bash scripts/rounds/run_260826_v3w1_lib_d.sh              # smoke -> batch
#   bash scripts/rounds/run_260826_v3w1_lib_d.sh --bands base,e
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
CFG="$REPO/experiments/v3_0823/render_configs_v3"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w1d_render.log"
MARKDIR="$LOGDIR/w1d_markers"
LOCK=/tmp/negobs_gpu.lock
CAMS=8
LOCK_WAIT=14400
LOCK_RC=201
STAMP=260826_v3w1_lib_D
SEG_STRICT="${NEGOBS_SEG_STRICT_OVERRIDE:-1}"

# --- 밴드 표 (render_plan_v3.json .bands · run_260820_boost.sh:135-136,203) ---
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'
BAND_E2='{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'

# --- 씬 × 밴드 (render_plan_v3.json .scenes[origin=existing].bands) ----------
S_BASE="scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3 sceneN1 sceneN2 sceneN4 sceneN5"
S_H="scene09 scene17"
S_E="scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 sceneC4"
S_E2="scene03 scene04 scene12 scene20 sceneC4"

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
conds_sub()  { case "$1" in sceneC1) echo "L4" ;; sceneN1) echo "L3" ;; *) echo "" ;; esac; }
# 스모크는 실제로 통과하는 조건 하나만 쓴다 (sceneC1의 L0는 계절 잠금으로 거부됨)
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
verify_unit() {                  # verify_unit <run> <scene> <n_expect> [strict]
  python3 - "$REPO" "$1" "$2" "$3" "${4:-0}" <<'PY'
import json, os, sys, glob, hashlib
repo, run, scene, nexp = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
strict = sys.argv[5] == "1"
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
#
# THE D-ARM THRESHOLD IS NOT THE W0 THRESHOLD. W0's floor was n_prims >= 50
# (its emptiest unit was sceneN2/Bdress at 60). The D arm removes the hazard AND
# all six cue keys at once, so a legitimately stripped scene can be far smaller —
# the 1-cut smoke measured scene02 at 28 prims and scene08 at 49 with a fully
# measured heightmap (103,041/103,041 finite) and a normal RGB render. Keeping
# the 50 floor would have quarantined two sound scenes. The empty-stage signature
# is different in kind: (near-)zero prims AND no measured ground AND a flat image.
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
ac = (meta.get("arm_config") or "").replace("False", "false").replace("True", "true")
for k in ("cue_railing", "cue_tactile", "cue_nosing", "cue_material_break",
          "cue_sign", "cue_scene_dressing"):
    if f'"{k}": false' not in ac:
        print(f"arm_config missing {k}=false: {ac!r}"); sys.exit(1)
if '"hazard_' not in ac or ac.count("true") > 0:
    print(f"arm_config is not an all-false D recipe: {ac!r}"); sys.exit(1)
var = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
cu = var["cuts"]; cu = list(cu.values()) if isinstance(cu, dict) else cu
nok = sum(1 for c in cu if c.get("ok"))
if nok != nexp:
    print(f"variation.json: {nok}/{nexp} ok cuts"); sys.exit(1)
nseg = sum(1 for c in cu if c.get("idseg"))
# --- ID mask stale-frame detector (D73 (1) / SCENE_H67_BUILD.md §7.6-2) -------
# `idseg_n_ids` is already in variation.json: constant across every cut of a
# multi-cut process == the annotator was never re-evaluated.  Free to check.
nid = sorted({c.get("idseg_n_ids") for c in cu if c.get("idseg_n_ids") is not None})
fetch = sorted({c.get("idseg_fetch") for c in cu if c.get("idseg_fetch")})
stale = (nexp > 1 and len(nid) == 1)
if stale:                                   # confirm on bytes before calling it
    hs = set()
    for c in cu[:6]:
        p = os.path.join(d, os.path.splitext(c["file"])[0] + ".idseg.npz")
        if os.path.isfile(p):
            hs.add(hashlib.sha256(open(p, "rb").read()).hexdigest())
    stale = len(hs) == 1 and len(cu) > 1
if stale and strict:
    print(f"idseg STALE despite NEGOBS_SEG_STRICT=1 — n_ids={nid} fetch={fetch}")
    sys.exit(1)
conds = sorted({c.get("cond") for c in cu})
gz = sorted({round(float(c["cam"]["ground_z"]), 6) for c in cu})
print(f"{nok} cuts · conds {conds} · n_prims={meta['n_prims']} · "
      f"hm {meta['n_finite']}/{meta['n_total']} · idseg {nseg}/{nexp} "
      f"{'STALE' if stale else 'fresh'}({len(nid)} n_ids/{fetch}) · "
      f"ground_z {gz[:3]} · {rec.get('sec_per_cut')} s/cut")
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
  cfgfile="$CFG/${scene}_D.json"
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
    say "  [FAIL] $scene: missing D config $cfgfile"
    FAILS="${FAILS}\n  ${run} ${scene}: no D config"; NFAIL=$((NFAIL+1)); return
  fi
  if [ "$DRY" = "1" ]; then
    say "  [dry] $run $scene seed=$seed cams=$cams conds=$conds sub=${sub:-none} band=${camband:-none} cfg=$(cat "$cfgfile") -> dataset/${run}/${split}/${scene}"
    return
  fi

  # --- 한 번의 flock = 한 씬 프로세스. 여러 조건 인보케이션이면 각각 따로 잡는다.
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
        --conds '$1' --cams $cams --seed $seed
rc=\$?
python3 scripts/stamp_round.py --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  }

  say "  [run]  $run $scene seed=$seed cams=$cams conds=$conds${sub:+ (+sub $sub)} band=${camband:-none}"
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

  local why; why=$(verify_unit "$run" "$scene" "$nexp" "$SEG_STRICT"); local vrc=$?
  if [ "$vrc" = "0" ]; then
    printf '%s\n' "$(date '+%F %T') rc=$rc band=$band seed=$seed conds=$conds${sub:+,$sub} cfg=$(cat "$cfgfile")  $why" > "$mark"
    say "  [ok]   $run $scene rc=$rc — $why"
    NOK=$((NOK+1)); NCUTS=$((NCUTS+nexp))
  else
    say "  [FAIL] $run $scene rc=$rc — $why"
    FAILS="${FAILS}\n  ${run} ${scene}: ${why}"; NFAIL=$((NFAIL+1))
  fi
}

want_band()  { case " $BANDS_SEL " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }
want_scene() {
  [ -z "$SCENES_OVERRIDE" ] && return 0
  case " $SCENES_OVERRIDE " in *" $1 "*) return 0 ;; *) return 1 ;; esac
}

T0=$(date +%s)
say "================================================================"
say "run_260826_v3w1_lib_d.sh start — phase:$PHASE bands:[$BANDS_SEL] cams:$CAMS sidecars:depth+heightmap+idseg"
say "  W1 D팔 · 기존 22씬 · base 528 + H 48 + E 216 + E2 120 = 912컷"
say "  recipe {hazard_*: false, cue_* x6: false} (계획 §1.2) · GPU lock per scene process"
say "================================================================"

# --- 스모크: 씬 프로세스마다 1컷 --------------------------------------------
if [ "$PHASE" = "smoke" ] || [ "$PHASE" = "all" ]; then
  say "--- phase smoke (씬당 1컷, dataset/${STAMP}_smoke) ---"
  for s in $S_BASE; do
    want_scene "$s" || continue
    render_unit base "$s" smoke
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
    say "--- band $band -> dataset/$(run_of_band "$band") (seed $(seed_of_band "$band") · camband $(band_of "$band" | sed 's/^$/none/')) ---"
    for s in $(scenes_of_band "$band"); do
      want_scene "$s" || continue
      render_unit "$band" "$s" batch
    done
  done
fi

DT=$(( $(date +%s) - T0 ))
say "================================================================"
say "run_260826_v3w1_lib_d.sh done — ok=$NOK skip=$NSKIP fail=$NFAIL cuts=$NCUTS · wall $((DT/60))m $((DT%60))s"
for r in "$STAMP" "${STAMP}_h" "${STAMP}_e" "${STAMP}_e2" "${STAMP}_smoke"; do
  d="$REPO/dataset/$r"
  [ -d "$d" ] || continue
  say "  dataset/$r: $(find "$d" -name '*.png' | wc -l) png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name 'heightmap.npy' | wc -l) heightmap"
done
if [ "$NFAIL" != "0" ]; then
  printf 'FAILURES:%b\n' "$FAILS" | tee -a "$LOG"
  exit 1
fi
say "ALL_OK"
exit 0
