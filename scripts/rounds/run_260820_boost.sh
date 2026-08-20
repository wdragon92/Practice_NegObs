#!/bin/bash
# =============================================================================
# run_260820_boost.sh — the 08-20 ADDITIVE E/H boost render (Phase 2 of
# DAYRUN_BRIEF_0820, mechanised by DECISIONS.md D19 (1)(2)(3))
#
# Same machine, same driver, same conditions, same arms as
# `run_260819_main.sh`. Exactly two things differ:
#
#   1. seed 20260820 (not 20260819) — a fresh camera draw, so the boost cuts are
#      NEW frames and not a re-render of last night's;
#   2. NEGOBS_CAM_BAND_OVERRIDE biases the (d, h) band the data channel draws
#      from, per D19 (1):
#         H-boost  d LogU[6, 12] · h U[0.25, 1.0]   far + LOW  = max occlusion
#         E-boost  d LogU[6, 12] · h U[1.2, 1.9]    far + HIGH = rim still visible
#      pitch / yaw / roll / hfov / yoff distributions are UNCHANGED (D19 (1)),
#      and the override draws from its own rng stream, so cut i keeps exactly
#      the yaw/pitch/roll/hfov the unbiased sampler gave it.
#
# ADDITIVE — READ THIS BEFORE EDITING
# -----------------------------------
# The output trees are dataset/260820_boost_{h,e}_{on,off}/ — the arm MUST be in the
# run name: both arms share seed-identical camera filenames, so a shared dir would
# have the second arm silently overwrite the first (bug found 08-20 16:45, D23).
# The collided first attempt (260820_boost_h / _e, off-arm survivors) is left on
# disk untouched and superseded by these four rounds.
# NOTHING here writes into `dataset/260819_main_on|off/`. Last night's corpus is
# frozen evidence (it is the "before" half of the v1 -> v2 development story,
# Phase 3 of the brief) and a boost cut landing in it would be indistinguishable
# from a main cut afterwards. `guard_run_name` below refuses any run stamp that
# is not `260820_boost_*`.
#
# BOTH ARMS
# ---------
# on and off, as in D2: the twin structure is what measures false alarms, and
# `var_seed(scene, stream, idx, base)` makes cut i of a scene the same camera in
# both arms. The camband override is a pure function of (scene, idx, seed) too,
# so the boost arms stay exact twins.
#
# CONDITIONS — identical to 260819_main
# -------------------------------------
# Base L0,L5,L7, plus the five declared substitutions for the pairs the ledger
# refuses. Repeated verbatim from `run_260819_main.sh:151-164` so the boost cuts
# are drawn from the same lighting population as the corpus they extend:
#   sceneC1  C1xL0 refused (winter)      -> + L4
#   sceneC2  C2xL0, C2xL5 refused (autumn) -> + L2,L3
#   scene15  s15xL5 refused (|Dz| >= 37) -> + L4
#   sceneN1  N1xL5 refused (|Dz| >= 37)  -> + L3
# Each scene therefore still gets exactly 3 valid conditions x 8 cameras
# = 24 cuts per arm.
#
# CAM-2 SCENES AND THE E BAND — expect a distance-only boost
# ----------------------------------------------------------
# scene02, scene15, sceneD4, scene11 carry a STRUCTURAL h <= 1.20 ceiling
# (`variation_kit.py:592-595`). The E band [1.2, 1.9] does not intersect it, so
# on those scenes the driver prints
#     [camband] <scene>: CAM-2 CEILING WINS ... boost is DISTANCE-ONLY
# and falls back to h U[0.25, 1.20] while keeping d LogU[6, 12]. That is
# deliberate — the cap is geometry, not a preference. **scene15 is on the
# brief's E risk list and IS a CAM-2 scene**: its E boost will be far-camera
# only. The end-of-run summary re-prints every such line.
#
# THE `train/ val/ test/` DIRECTORY IS NOT THE ANALYSIS SPLIT
# -----------------------------------------------------------
# The driver files frames under `vk.split_of(scene)` (the legacy AZ-ledger
# split) — that is where 260819_main put them too, e.g. scene14 sits in
# `dataset/260819_main_on/train/scene14` even though `split_v1.json` forces
# scene14 into **test**. The analysis split is `split_v1.json` and nothing
# else. Boost frames inherit their scene's split automatically because they
# inherit their scene; do not "fix" the directory.
#
# SIDECARS
# --------
# NEGOBS_DATA_SIDECARS=1, exactly as 260819_main: `<cut>.depth.npy` per cut and
# `heightmap.npy` + `heightmap_meta.json` per scene. The Phase 1 labeller needs
# both, and a boost round without them cannot be labelled.
#
# RESUME
# ------
# Safe to re-run at any point, same two automatic levels as 260819_main
# (scene/condition via `done_conds`, cut via the PNG+depth existence check).
# A completed scene costs one Isaac boot and no renders.
#
# USAGE
# -----
#   # 1. fill H_SCENES / E_SCENES below, then:
#   bash scripts/rounds/run_260820_boost.sh --dry-run     # print the plan only
#   bash scripts/rounds/run_260820_boost.sh               # both boosts, both arms
#   bash scripts/rounds/run_260820_boost.sh --boosts h    # H only
#   bash scripts/rounds/run_260820_boost.sh --boosts e --scenes scene05,scene07
#   bash scripts/rounds/run_260820_boost.sh --arms on     # one arm only
# Log: experiments/dayrun_0820/logs/boost_render.log (appended, timestamped).
# Exit 0 only if every invocation exited 0.
#
# The GPU probe that validated the band override (do NOT confuse it with a run):
#   NEGOBS_DATA_SIDECARS=1 NEGOBS_CAM_BAND_OVERRIDE='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}' \
#   python3 scripts/run_data_render.py --run 260820_probe_h --scenes scene14 \
#           --conds L0 --cams 2 --seed 20260820
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
# Arm configs are REUSED from last night rather than copied: they are a
# per-file grep of each scene's real hazard key (30x hazard_stairs, N1
# hazard_shadow_band, N2 hazard_asphalt_patch, N5 hazard_flush_grating) and a
# second copy is a second thing to drift. A file of the same name under
# CFG_OVR wins, so today can override one scene without touching 08-19.
CFG="$REPO/experiments/mainrun_0819/render_configs"
CFG_OVR="$REPO/experiments/dayrun_0820/render_configs"
LOGDIR="$REPO/experiments/dayrun_0820/logs"
LOG="$LOGDIR/boost_render.log"
LOCK=/tmp/negobs_gpu.lock
SEED="${SEED_OVERRIDE:-20260820}"
CAMS=8
LOCK_WAIT=3600
LOCK_RC=201

# -----------------------------------------------------------------------------
# THE TWO SCENE LISTS — the orchestrator fills these.
# -----------------------------------------------------------------------------
# Comma-separated, no spaces. Leave a list empty to skip that boost entirely.
#
# H_SCENES: scenes that can put an occluder between the camera and the drop, so
#   a far+low camera yields H (hazard contributes no pixels). Brief Phase 2:
#   test s14 + s15, plus the train scenes that already hold H.
# E_SCENES: scenes whose rim stays visible from far+high, so the frame is E
#   (rim only). Brief Phase 2: test {05,07,15,18} + s14, plus train risk scenes
#   chosen from the Phase 1 sparse-cell table. CAP THIS LIST to fit the ~2 h
#   render budget — see the wall-time table in the DAYRUN report.
H_SCENES="scene14,scene15,scene09,scene17"
E_SCENES="scene05,scene07,scene14,scene15,scene18,sceneC4,scene20,sceneC1,scene09,scene17,scene03,scene04,scene12,scene08"
E2_SCENES="scene05,scene03,scene04,scene20,scene12,scene18,sceneC4,scene07"

# D19 (1) bands. Only the keys present are overridden; every absent key keeps
# its CAM_DIST value. Do not widen these without a DECISIONS entry.
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'

BOOSTS="h e"
ARMS="on off"
SCENES_OVERRIDE=""
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --boosts) BOOSTS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --scenes) SCENES_OVERRIDE="$2"; shift 2 ;;
    --arms)   ARMS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$LOGDIR" "$CFG_OVR"

# --- the shell preamble every render subshell repeats -----------------------
# (run_260819_main.sh:140-144; PYTHONNOUSERSITE=1 is mandatory on this box)
PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# --- HOLD scenes are not usable ---------------------------------------------
# Brief 보고·가드레일: "HOLD 씬 사용 금지". `split_v1.json` holds scene11,
# scene13, scene19, sceneD4 out of every split; rendering a boost into them
# would produce frames the labeller then has to throw away.
HOLD_SCENES="scene11 scene13 scene19 sceneD4"
is_hold() {
  case " $HOLD_SCENES " in *" $1 "*) return 0 ;; *) return 1 ;; esac
}

# --- additive guard ---------------------------------------------------------
# The one mistake this script must make impossible.
guard_run_name() {
  case "$1" in
    260820_boost_h_on|260820_boost_h_off|260820_boost_e_on|260820_boost_e_off|260820_boost_e2_on|260820_boost_e2_off) return 0 ;;
    *) echo "[fatal] refusing run stamp '$1' — this script only ever writes" >&2
       echo "        dataset/260820_boost_h and dataset/260820_boost_e." >&2
       exit 4 ;;
  esac
}

# --- conditions: identical table to run_260819_main.sh:151-164 --------------
conds_base() {
  case "$1" in
    *) echo "L0,L5,L7" ;;
  esac
}
conds_sub() {
  case "$1" in
    sceneC1) echo "L4" ;;
    sceneC2) echo "L2,L3" ;;
    scene15) echo "L4" ;;
    sceneN1) echo "L3" ;;
    *)       echo "" ;;
  esac
}

# --- band for a boost -------------------------------------------------------
band_of() {
  if [ "$1" = "e2" ]; then echo '{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'; return; fi
  case "$1" in
    h) echo "$BAND_H" ;;
    e) echo "$BAND_E" ;;
    *) echo "[fatal] unknown boost '$1' (expected h or e)" >&2; exit 2 ;;
  esac
}
scenes_of() {
  if [ "$1" = "e2" ]; then echo "$E2_SCENES"; return; fi
  if [ -n "$SCENES_OVERRIDE" ]; then echo "$SCENES_OVERRIDE"; return; fi
  case "$1" in
    h) echo "$H_SCENES" ;;
    e) echo "$E_SCENES" ;;
  esac
}

# --- split map, so --capture-env lands beside the frames of THIS scene ------
# Boost frames inherit the split of their scene (brief Phase 2: "분리는 씬
# 단위이므로 신규 프레임은 소속 씬의 분할을 상속"), which is automatic — the
# driver derives the split from `vk.split_of` itself. This map is only so the
# stamp lands in the right directory.
SPLITMAP=$(bash -c "$PRE
python3 - <<'PY'
import sys; sys.path.insert(0, '$REPO')
import variation_kit as vk
for s in sorted(vk.AZ_LEDGER):
    print(s, vk.split_of(s))
PY") || { echo "[fatal] could not compute the split map" >&2; exit 3; }
split_of() { echo "$SPLITMAP" | awk -v s="$1" '$1==s{print $2}'; }

# --- did the SCENE SUBPROCESS succeed? (run_260819_main.sh:186-206) ---------
scene_ok() {                     # scene_ok <run> <scene> <conds>
  python3 - "$REPO/dataset/$1/manifest.json" "$2" "$3" <<'PY'
import json, sys
mf_path, scene, conds = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
try:
    mf = json.load(open(mf_path, encoding="utf-8"))
except Exception as e:
    print(f"manifest unreadable: {e}"); sys.exit(1)
rec = mf.get("scenes", {}).get(scene)
if not rec:
    print("no manifest record"); sys.exit(1)
if rec.get("exit") != 0:
    print(f"subprocess exit {rec.get('exit')}"); sys.exit(1)
if not rec.get("cuts"):
    print("0 cuts"); sys.exit(1)
missing = [c for c in conds if c not in (rec.get("done_conds") or [])]
if missing:
    print(f"conditions not marked done: {missing}"); sys.exit(1)
print(f"exit 0 · {rec['cuts']} cuts · {rec.get('sec_per_cut')} s/cut")
PY
}

# --- one flocked invocation -------------------------------------------------
# rc: 0 ok · 201 lock timeout · anything else = the driver itself failed.
FAILS=""
NFAIL=0
render() {                       # render <boost> <scene> <arm> <conds> <label>
  local boost="$1" scene="$2" arm="$3" conds="$4" label="$5"
  local run="260820_boost_${boost}_${arm}"
  guard_run_name "$run"
  local band; band=$(band_of "$boost")
  local cfgfile="$CFG_OVR/${scene}_${arm}.json"
  [ -f "$cfgfile" ] || cfgfile="$CFG/${scene}_${arm}.json"
  local split; split=$(split_of "$scene")
  local outdir="$REPO/dataset/${run}/${split}/${scene}"

  if [ ! -f "$cfgfile" ]; then
    say "  [FAIL] $scene $arm: missing config ${scene}_${arm}.json in $CFG_OVR or $CFG"
    FAILS="${FAILS}\n  ${boost} ${scene} ${arm} ${label}: missing config"; NFAIL=$((NFAIL+1))
    return
  fi
  if [ -z "$split" ]; then
    say "  [FAIL] $scene: not in vk.AZ_LEDGER — no split"
    FAILS="${FAILS}\n  ${boost} ${scene} ${arm} ${label}: unknown scene"; NFAIL=$((NFAIL+1))
    return
  fi
  if is_hold "$scene"; then
    say "  [FAIL] $scene is a HOLD scene — the brief forbids using it"
    FAILS="${FAILS}\n  ${boost} ${scene} ${arm} ${label}: HOLD scene, refused"; NFAIL=$((NFAIL+1))
    return
  fi
  if [ "$DRY" = "1" ]; then
    say "  [dry] $boost $scene $arm $label conds=$conds cfg=$(cat "$cfgfile") band=$band -> dataset/${run}/${split}/${scene}"
    return
  fi

  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_CAM_BAND_OVERRIDE='$band'
export NEGOBS_SCENE_CONFIG=\$(cat '$cfgfile')
mkdir -p '$outdir'
python3 scripts/run_data_render.py --run '$run' --scenes '$scene' \
        --conds '$conds' --cams $CAMS --seed $SEED
rc=\$?
# inside the render shell, while NEGOBS_* is still set — this is what records
# NEGOBS_CAM_BAND_OVERRIDE beside the frames (stamp_round.py:61 ENV_PREFIXES)
python3 scripts/stamp_round.py --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  local rc=$?

  if [ "$rc" = "0" ]; then
    local why; why=$(scene_ok "$run" "$scene" "$conds")
    if [ $? = 0 ]; then
      say "  [ok]   $boost $scene $arm $label conds=$conds — $why"
    else
      say "  [FAIL] $boost $scene $arm $label conds=$conds — $why"
      FAILS="${FAILS}\n  ${boost} ${scene} ${arm} ${label}: ${why}"; NFAIL=$((NFAIL+1))
    fi
  elif [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $boost $scene $arm $label — no GPU lock within ${LOCK_WAIT}s, skipped"
    FAILS="${FAILS}\n  ${boost} ${scene} ${arm} ${label}: LOCK-TIMEOUT (rc 201)"; NFAIL=$((NFAIL+1))
  else
    say "  [FAIL] $boost $scene $arm $label rc=$rc"
    FAILS="${FAILS}\n  ${boost} ${scene} ${arm} ${label}: rc=$rc"; NFAIL=$((NFAIL+1))
  fi
}

# =============================================================================
if [ -z "$SCENES_OVERRIDE" ] && [ -z "$H_SCENES" ] && [ -z "$E_SCENES" ]; then
  echo "[fatal] H_SCENES and E_SCENES are both empty — fill them at the top of" >&2
  echo "        $0 (or pass --scenes)." >&2
  exit 2
fi

LOG_MARK=$(wc -l < "$LOG" 2>/dev/null || echo 0)
T0=$(date +%s)
say "================================================================"
say "run_260820_boost.sh start — boosts:[$BOOSTS] arms:[$ARMS] cams:$CAMS seed:$SEED sidecars:ON"
say "  ADDITIVE: writes dataset/260820_boost_{h,e} only; 260819_main_* untouched"
say "  H band $BAND_H  scenes: ${H_SCENES:-<none>}"
say "  E band $BAND_E  scenes: ${E_SCENES:-<none>}"
say "  git $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null) $(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)"
say "================================================================"

for boost in $BOOSTS; do
  list=$(scenes_of "$boost")
  if [ -z "$list" ]; then
    say "[BOOST $boost] scene list empty — skipped"
    continue
  fi
  IFS=',' read -r -a SCENE_ARR <<< "$list"
  N=${#SCENE_ARR[@]}
  NARM=$(echo "$ARMS" | wc -w)
  say "[BOOST $boost] $N scene(s) x $NARM arm(s) x 24 cuts = $((N*NARM*24)) cuts -> dataset/260820_boost_${boost}"
  i=0
  for scene in "${SCENE_ARR[@]}"; do
    i=$((i+1))
    for arm in $ARMS; do
      say "[$boost SCENE $i/$N $scene arm=$arm]"
      render "$boost" "$scene" "$arm" "$(conds_base "$scene")" "base"
      sub=$(conds_sub "$scene")
      if [ -n "$sub" ]; then
        say "[$boost SCENE $i/$N $scene arm=$arm] declared substitution for the refused pair(s): $sub"
        render "$boost" "$scene" "$arm" "$sub" "sub"
      fi
    done
  done
done

T1=$(date +%s)
say "================================================================"
say "run_260820_boost.sh done in $(( (T1-T0)/60 )) min"
for boost in $BOOSTS; do
  d="$REPO/dataset/260820_boost_${boost}"
  say "  dataset/260820_boost_${boost}: $(find "$d" -name '*.png' 2>/dev/null | wc -l) png · $(find "$d" -name '*.depth.npy' 2>/dev/null | wc -l) depth · $(find "$d" -name 'heightmap.npy' 2>/dev/null | wc -l) heightmap"
done
# Surface every scene where the CAM-2 ceiling beat the requested band, so a
# distance-only boost is never discovered later by reading variation.json.
CEIL=$(tail -n +"$((LOG_MARK+1))" "$LOG" 2>/dev/null | grep -o '\[camband\] scene[0-9A-Z]*: CAM-2 CEILING WINS' | sort -u)
if [ -n "$CEIL" ]; then
  say "  CAM-2 ceiling beat the requested h band on:"
  printf '%s\n' "$CEIL" | sed 's/^/    /' | tee -a "$LOG"
  say "    (those scenes got the distance bias only — expected, see header)"
fi
if [ "$NFAIL" = "0" ]; then
  say "FAIL SUMMARY: none — every invocation exited 0"
  say "next: python3 scripts/check_data_run.py 260820_boost_h ; ... 260820_boost_e"
  say "      then re-label with the Phase 1 pipeline and rebuild manifest v2"
  say "================================================================"
  exit 0
else
  say "FAIL SUMMARY: $NFAIL invocation(s) did not exit 0:"
  printf '%b\n' "$FAILS" | tee -a "$LOG"
  say "  re-run this script unchanged to resume — completed scenes are no-ops"
  say "================================================================"
  exit 1
fi
