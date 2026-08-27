#!/bin/bash
# =============================================================================
# run_260819_main.sh — the 08-19 overnight main data render (D2 of DECISIONS.md)
#
#   33 scenes x 3 lighting conditions x 8 random cameras x 2 hazard arms
#   = 792 cuts per arm, 1584 cuts total, seed 20260819 in BOTH arms.
#
# Why paired arms. `seed 20260819` drives every derived stream through
# `var_seed(scene, stream, idx, base)` (variation_kit.py:121-137), so cut i of
# scene s under condition c is the SAME camera pose and the SAME d_az draw in
# the hazard-on and the hazard-off arm. That is what makes this a twin dataset
# and the declared remedy for P(drop | railing) = 0.944
# (lighting_camera_variation_spec_v1.md:742).
#
# ORDER: scene-major, arm-inner. One `flock` acquisition per (scene, arm), so
# the user's own GPU work never waits more than one scene
# (run_260817_w4_regfix.sh:8-13). `-w 3600` then skip; `-E 201` is the
# lock-timeout exit code.
#
# -----------------------------------------------------------------------------
# CONDITIONS — base L0,L5,L7, and the 5 declared substitutions
# -----------------------------------------------------------------------------
# `check_data_run.py:134-153` needs a pair of sun-bearing conditions >= 0.3 net
# EV apart or check 1 fails "no comparable pair". Net EV of the sun-bearing
# conditions is L0 0.000 / L1 0.013 / L2 0.047 / L3 0.090 / L4 0.195 / L5 0.352,
# so **L5 is mandatory**; L7 (sunless) supplies the other half of check 1.
#
# The ledger refuses 5 (scene, condition) pairs out of the 99. The driver prints
# each refusal and renders nothing for it — it never substitutes silently (spec
# B6, run_data_render.py:73-83). So, exactly as run_260730_data_mini.sh:35-38
# did, each refusal is answered by a SECOND, explicitly declared invocation with
# the same --run stamp, and the refusal stays on the record.
#
#   scene   refused pair          reason (verified via --plan at this HEAD)
#   ------  --------------------  -------------------------------------------
#   sceneC1 C1 x L0               season-locked winter (elev 0-32); L0 = 49.83
#   sceneC2 C2 x L0, C2 x L5      season-locked autumn (elev 35-45); L0 49.83,
#                                 L5 19.08
#   scene15 s15 x L5              L5 needs |Dz| >= 37.0; s15 allows 20 (class A')
#   sceneN1 N1 x L5               L5 needs |Dz| >= 37.0; N1 allows 0 (class S)
#
#   scene    base renders   substitute   why this substitute
#   -------  -------------  -----------  ------------------------------------
#   sceneC1  L5, L7         + L4         legal set is {L4,L5,L6,L7}; L4 is the
#                                        only sun-bearing one left
#   sceneC2  L7             + L2, L3     legal set is {L2,L3,L6,L7}; both
#                                        sun-bearing ones are taken, no 0.3 EV
#                                        pair is reachable for C2 at all
#   scene15  L0, L7         + L4         legal set is {L0..L4,L6,L7}; L4 is the
#                                        darkest legal sun-bearing = closest in
#                                        role to the L5 it replaces
#   sceneN1  L0, L7         + L3         legal set is {L0..L3,L6,L7}; L3 is the
#                                        darkest legal sun-bearing (the 260730
#                                        mini used L1 here; L3 is chosen because
#                                        it maximises the net-EV separation from
#                                        L0, which is the axis L5 was serving)
#
#   Every scene therefore still gets exactly 3 valid conditions x 8 cameras.
#   All four substitutes were checked legal with
#   `vk.condition_allowed(scene, cond, role=data)` at this HEAD.
#
# -----------------------------------------------------------------------------
# ARMS
# -----------------------------------------------------------------------------
# The hazard key is NOT uniform (SPEC_EXTRACTED.md (d), re-verified per file):
# 30 scenes use "hazard_stairs", sceneN1 "hazard_shadow_band", sceneN2
# "hazard_asphalt_patch", sceneN5 "hazard_flush_grating". `_deep_update` merges
# and silently ignores an unknown key, so one blanket '{"hazard_stairs":false}'
# would leave 3 scenes with the hazard still on and nothing would say so.
# Hence one config file per (scene, arm) under
# experiments/mainrun_0819/render_configs/, generated from a per-file grep.
#
# Output trees: dataset/v2_corpus/260819_main_on/ and dataset/v2_corpus/260819_main_off/. They MUST
# differ — the split/scene/filename path is identical in both arms
# (run_data_render.py:171,430) and a shared --run stamp would overwrite.
#
# -----------------------------------------------------------------------------
# SIDECARS
# -----------------------------------------------------------------------------
# NEGOBS_DATA_SIDECARS=1 turns on the opt-in depth + heightmap patch (D4/D5):
#   <cut>.depth.npy      float16 (1080,1920) metres, distance_to_image_plane,
#                        +inf = no hit. NOT a .png — check_data_run.py:256-261
#                        fails a round on any orphan PNG.
#   heightmap.npy        (321,321) float32, z[y_idx,x_idx], x in [-2,14],
#                        y in [-8,8], step 0.05, NaN = no hit, once per scene.
#   heightmap_meta.json  the grid constants + which hazard arm produced it.
# With the variable unset the driver is byte-identical to its pre-patch self.
#
# -----------------------------------------------------------------------------
# RESUME
# -----------------------------------------------------------------------------
# Safe to re-run at any point. Two independent levels, both automatic:
#   scene/condition  run_data_render.py:165-169 — a scene whose requested
#                    conditions are all in `done_conds` is skipped outright.
#   cut              run_data_render.py:449-455 — a cut whose PNG exists, whose
#                    previous record said ok, and (with sidecars on) whose
#                    .depth.npy exists, is skipped.
# So a completed scene costs one Isaac boot and no renders; a completed arm
# costs 33 no-ops. Nothing is ever re-rendered into a different file.
#
# -----------------------------------------------------------------------------
# USAGE
# -----------------------------------------------------------------------------
#   bash scripts/rounds/run_260819_main.sh                 # everything
#   bash scripts/rounds/run_260819_main.sh --arms on       # one arm only
#   bash scripts/rounds/run_260819_main.sh --scenes scene04,scene16
#   bash scripts/rounds/run_260819_main.sh --dry-run       # print the plan only
# Log: experiments/mainrun_0819/logs/render.log (appended, timestamped).
# Exit 0 only if every invocation exited 0.
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
CFG="$REPO/experiments/mainrun_0819/render_configs"
LOGDIR="$REPO/experiments/mainrun_0819/logs"
LOG="$LOGDIR/render.log"
LOCK=/tmp/negobs_gpu.lock
SEED=20260819
CAMS=8
LOCK_WAIT=3600
LOCK_RC=201

SCENES="scene01,scene02,scene03,scene04,scene05,scene06,scene07,scene08,scene09,scene10,scene11,scene12,scene13,scene14,scene15,scene16,scene17,scene18,scene19,scene20,scene21,sceneC1,sceneC2,sceneC4,sceneD1,sceneD2,sceneD3,sceneD4,sceneN1,sceneN2,sceneN3,sceneN4,sceneN5"
ARMS="on off"
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --scenes)  SCENES="$2"; shift 2 ;;
    --arms)    ARMS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$LOGDIR"

# --- the shell preamble every render subshell repeats -----------------------
# (run_260817_w4_regfix.sh:15-19; PYTHONNOUSERSITE=1 is mandatory on this box)
PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# scene -> its 3 valid conditions, as two invocations where the ledger refuses.
#   BASE_<scene>  : the conditions handed to the first invocation
#   SUB_<scene>   : the declared substitution, "" when there is none
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

# --- split map, so --capture-env lands beside the frames of THIS scene ------
# `stamp_round.py --capture-env <dir>` must run INSIDE the render shell: that is
# the only place NEGOBS_SCENE_CONFIG (= which arm this directory is) still
# exists (stamp_round.py:18-22, the "X2 구멍" of the 8c814db queue). The scene
# directory, not the run root, because the arm's config differs per scene.
SPLITMAP=$(bash -c "$PRE
python3 - <<'PY'
import sys; sys.path.insert(0, '$REPO')
import variation_kit as vk
for s in sorted(vk.AZ_LEDGER):
    print(s, vk.split_of(s))
PY") || { echo "[fatal] could not compute the split map" >&2; exit 3; }
split_of() { echo "$SPLITMAP" | awk -v s="$1" '$1==s{print $2}'; }

# --- did the SCENE SUBPROCESS succeed? --------------------------------------
# `drive()` returns 0 whatever the per-scene subprocess did — the subprocess's
# return code is only recorded in the manifest (run_data_render.py:199-203).
# So the driver's own exit code cannot be the failure signal; the manifest is.
# Checked: exit 0, at least one cut, and every requested condition landed in
# `done_conds` (which is what scene-level resume reads back).
scene_ok() {                     # scene_ok <run> <scene> <conds>
  python3 - "$(negobs_round_or_flat "$1")/manifest.json" "$2" "$3" <<'PY'
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
render() {                       # render <scene> <arm> <conds> <label>
  local scene="$1" arm="$2" conds="$3" label="$4"
  local run="260819_main_${arm}"
  local cfgfile="$CFG/${scene}_${arm}.json"
  local split; split=$(split_of "$scene")
  local outdir
  outdir="$(negobs_round_or_flat "${run}")/${split}/${scene}"

  if [ ! -f "$cfgfile" ]; then
    say "  [FAIL] $scene $arm: missing config $cfgfile"
    FAILS="${FAILS}\n  ${scene} ${arm} ${label}: missing config"; NFAIL=$((NFAIL+1))
    return
  fi
  if [ "$DRY" = "1" ]; then
    say "  [dry] $scene $arm $label conds=$conds cfg=$(cat "$cfgfile") -> dataset/${run}/${split}/${scene}"
    return
  fi

  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SCENE_CONFIG=\$(cat '$cfgfile')
mkdir -p '$outdir'
python3 scripts/run_data_render.py --run '$run' --scenes '$scene' \
        --conds '$conds' --cams $CAMS --seed $SEED
rc=\$?
# inside the render shell, while NEGOBS_* is still set (stamp_round.py:39-40)
python3 scripts/stamp_round.py --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  local rc=$?

  if [ "$rc" = "0" ]; then
    local why; why=$(scene_ok "$run" "$scene" "$conds")
    if [ $? = 0 ]; then
      say "  [ok]   $scene $arm $label conds=$conds — $why"
    else
      say "  [FAIL] $scene $arm $label conds=$conds — $why"
      FAILS="${FAILS}\n  ${scene} ${arm} ${label}: ${why}"; NFAIL=$((NFAIL+1))
    fi
  elif [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $scene $arm $label — no GPU lock within ${LOCK_WAIT}s, skipped"
    FAILS="${FAILS}\n  ${scene} ${arm} ${label}: LOCK-TIMEOUT (rc 201)"; NFAIL=$((NFAIL+1))
  else
    say "  [FAIL] $scene $arm $label rc=$rc"
    FAILS="${FAILS}\n  ${scene} ${arm} ${label}: rc=$rc"; NFAIL=$((NFAIL+1))
  fi
}

# =============================================================================
T0=$(date +%s)
say "================================================================"
say "run_260819_main.sh start — arms:[$ARMS] cams:$CAMS seed:$SEED sidecars:ON"
say "  git $(git -C "$REPO" rev-parse --short HEAD) $(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
say "================================================================"

IFS=',' read -r -a SCENE_ARR <<< "$SCENES"
N=${#SCENE_ARR[@]}
i=0
for scene in "${SCENE_ARR[@]}"; do
  i=$((i+1))
  for arm in $ARMS; do
    say "[SCENE $i/$N $scene arm=$arm]"
    render "$scene" "$arm" "$(conds_base "$scene")" "base"
    sub=$(conds_sub "$scene")
    if [ -n "$sub" ]; then
      say "[SCENE $i/$N $scene arm=$arm] declared substitution for the refused pair(s): $sub"
      render "$scene" "$arm" "$sub" "sub"
    fi
  done
done

T1=$(date +%s)
say "================================================================"
say "run_260819_main.sh done in $(( (T1-T0)/60 )) min"
for arm in $ARMS; do
  d="$(negobs_round_or_flat "260819_main_${arm}")"
  say "  dataset/260819_main_${arm}: $(find "$d" -name '*.png' 2>/dev/null | wc -l) png · $(find "$d" -name '*.depth.npy' 2>/dev/null | wc -l) depth · $(find "$d" -name 'heightmap.npy' 2>/dev/null | wc -l) heightmap"
done
if [ "$NFAIL" = "0" ]; then
  say "FAIL SUMMARY: none — every invocation exited 0"
  say "next: python3 scripts/check_data_run.py 260819_main_on ; ... 260819_main_off"
  say "================================================================"
  exit 0
else
  say "FAIL SUMMARY: $NFAIL invocation(s) did not exit 0:"
  printf '%b\n' "$FAILS" | tee -a "$LOG"
  say "  re-run this script unchanged to resume — completed scenes are no-ops"
  say "================================================================"
  exit 1
fi
