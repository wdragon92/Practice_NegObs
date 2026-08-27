#!/bin/bash
# =============================================================================
# run_ctrl_dressing.sh — C2 track (OVERNIGHT_BRIEF_0820 §4 C2, DECISIONS D25)
#
#   The appearance-preserving OFF arm of sceneC2 and sceneN3, and nothing else.
#   2 scenes x 3 lighting conditions x 8 cameras x ONE arm = 48 cuts, into the
#   NEW round `dataset/v2_probes/260820_ctrloff/`. No existing round is written to.
#
# WHY THE SEED IS 20260819 AND MUST STAY THERE
#   Every derived stream comes from `var_seed(scene, stream, idx, base)`
#   (variation_kit.py:121-137), so cut i of scene s under condition c draws the
#   SAME d/h_rel/y/yaw/pitch/roll/hfov as the 260819 main round. Together with
#   the scene patch (which leaves the ground under the camera untouched — see
#   README §"the datum argument") that makes every cut of this round the exact
#   twin of the SAME FILENAME in `dataset/v2_corpus/260819_main_on/`. A different seed
#   would produce a valid render that pairs with nothing.
#
# CONDITIONS — inherited verbatim from scripts/rounds/run_260819_main.sh:21-60,
#   re-verified against `vk.condition_allowed(scene, cond, role=data)` at this
#   HEAD (2026-08-21):
#     sceneC2  L0 REFUSED (season-locked autumn 35-45 deg; L0 = 49.83)
#              L5 REFUSED (same ledger; L5 = 19.08)
#              -> base invocation renders L7 only, second invocation adds L2,L3
#                 (the declared substitution — the refusal stays on the record,
#                  spec B6: the driver never substitutes silently)
#     sceneN3  L0,L5,L7 all legal, no substitution.
#   Result: 24 cuts per scene, the same 24 filenames as the main round.
#
# ARM
#   `{"hazard_stairs": false, "keep_dressing": true}` for both scenes
#   (render_configs/ beside this script). `keep_dressing` is the D25 opt-in key:
#   absent/false leaves both pre-existing arms byte-identical; true is legal only
#   with the hazard off and the scene fails loudly otherwise (module-scope guard
#   in each scene file).
#
# SIDECARS  NEGOBS_DATA_SIDECARS=1 — depth + heightmap, exactly as the main round.
#           The heightmap is what the hash gate reads.
#
# RESUME    Safe to re-run: scene-level and cut-level resume are both automatic
#           (run_data_render.py:165-169 / :449-455).
#
# usage
#   bash experiments/nightrun_0820/ctrl_dressing/run_ctrl_dressing.sh            # render
#   bash .../run_ctrl_dressing.sh --dry-run                                      # plan only
#   bash .../run_ctrl_dressing.sh --scenes sceneN3                               # one scene
#   bash .../run_ctrl_dressing.sh --no-gate                                      # skip the closing gate
# Log: experiments/nightrun_0820/ctrl_dressing/logs/render.log
# Exit 0 only if every invocation exited 0 AND the closing hash gate passed.
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
HERE="$REPO/experiments/nightrun_0820/ctrl_dressing"
CFG="$HERE/render_configs"
LOGDIR="$HERE/logs"
LOG="$LOGDIR/render.log"
LOCK=/tmp/negobs_gpu.lock
RUN=260820_ctrloff
SEED=20260819
CAMS=8
LOCK_WAIT=3600
LOCK_RC=201

SCENES="sceneC2,sceneN3"
DRY=0
GATE=1

while [ $# -gt 0 ]; do
  case "$1" in
    --scenes)  SCENES="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --no-gate) GATE=0; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$LOGDIR"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

conds_base() { echo "L0,L5,L7"; }                 # identical to the main round
conds_sub()  { case "$1" in sceneC2) echo "L2,L3" ;; *) echo "" ;; esac; }

scene_file() {
  case "$1" in
    sceneC2) echo "$REPO/scenes/batch1/sceneC2_leaf_stairs.py" ;;
    sceneN3) echo "$REPO/scenes/batch1/sceneN3_trompe_loeil.py" ;;
    *) echo "" ;;
  esac
}

# --- preflight (CPU, no lock) -----------------------------------------------
# 1. the opt-in patch is present in the scene file
# 2. the arm config says exactly what this round is
# 3. the scene parses and the guard accepts the config (NEGOBS_SMOKE, pre-boot)
preflight() {
  local rc=0 scene f cfgfile
  IFS=',' read -r -a ARR <<< "$SCENES"
  for scene in "${ARR[@]}"; do
    f=$(scene_file "$scene"); cfgfile="$CFG/${scene}_ctrloff.json"
    if [ ! -f "$f" ]; then say "  [preflight FAIL] no scene file for $scene"; rc=1; continue; fi
    if ! grep -q "KEEP_DRESSING" "$f"; then
      say "  [preflight FAIL] $scene: the keep_dressing patch is not in $f"; rc=1; continue
    fi
    if [ ! -f "$cfgfile" ]; then say "  [preflight FAIL] missing $cfgfile"; rc=1; continue; fi
    if ! python3 -c "import json,sys; c=json.load(open('$cfgfile')); sys.exit(0 if c.get('keep_dressing') is True and c.get('hazard_stairs') is False else 1)"; then
      say "  [preflight FAIL] $cfgfile is not {hazard_stairs:false, keep_dressing:true}"; rc=1; continue
    fi
    out=$(bash -c "$PRE
cd $(dirname "$f")
NEGOBS_SMOKE=1 NEGOBS_SCENE_CONFIG=\$(cat '$cfgfile') python3 $(basename "$f") 2>&1")
    if [ $? != 0 ]; then
      say "  [preflight FAIL] $scene smoke gate rc!=0:"; printf '%s\n' "$out" | tee -a "$LOG"; rc=1
    elif ! printf '%s' "$out" | grep -q "keep_dressing.*ON"; then
      say "  [preflight FAIL] $scene smoke gate did not report keep_dressing ON"; rc=1
    else
      say "  [preflight ok]   $scene: patch present · config valid · smoke gate 0 · keep_dressing ON"
    fi
  done
  return $rc
}

# --- did the SCENE SUBPROCESS succeed? (run_260819_main.sh:186-206) ----------
scene_ok() {
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

SPLITMAP=$(bash -c "$PRE
python3 - <<'PY'
import sys; sys.path.insert(0, '$REPO')
import variation_kit as vk
for s in ('sceneC2', 'sceneN3'):
    print(s, vk.split_of(s))
PY") || { echo "[fatal] could not compute the split map" >&2; exit 3; }
split_of() { echo "$SPLITMAP" | awk -v s="$1" '$1==s{print $2}'; }

FAILS=""
NFAIL=0
render() {                       # render <scene> <conds> <label>
  local scene="$1" conds="$2" label="$3"
  local cfgfile="$CFG/${scene}_ctrloff.json"
  local split; split=$(split_of "$scene")
  local outdir
  outdir="$(negobs_round_or_flat "${RUN}")/${split}/${scene}"

  if [ "$DRY" = "1" ]; then
    say "  [dry] $scene $label conds=$conds cfg=$(cat "$cfgfile") -> dataset/${RUN}/${split}/${scene}"
    return
  fi

  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SCENE_CONFIG=\$(cat '$cfgfile')
mkdir -p '$outdir'
python3 scripts/run_data_render.py --run '$RUN' --scenes '$scene' \
        --conds '$conds' --cams $CAMS --seed $SEED
rc=\$?
# inside the render shell, while NEGOBS_* is still set (stamp_round.py:39-40)
python3 scripts/stamp_round.py --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  local rc=$?

  if [ "$rc" = "0" ]; then
    local why; why=$(scene_ok "$RUN" "$scene" "$conds")
    if [ $? = 0 ]; then
      say "  [ok]   $scene $label conds=$conds — $why"
    else
      say "  [FAIL] $scene $label conds=$conds — $why"
      FAILS="${FAILS}\n  ${scene} ${label}: ${why}"; NFAIL=$((NFAIL+1))
    fi
  elif [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $scene $label — no GPU lock within ${LOCK_WAIT}s, skipped"
    FAILS="${FAILS}\n  ${scene} ${label}: LOCK-TIMEOUT (rc 201)"; NFAIL=$((NFAIL+1))
  else
    say "  [FAIL] $scene $label rc=$rc"
    FAILS="${FAILS}\n  ${scene} ${label}: rc=$rc"; NFAIL=$((NFAIL+1))
  fi
}

# =============================================================================
T0=$(date +%s)
say "================================================================"
say "run_ctrl_dressing.sh start — run:$RUN scenes:[$SCENES] cams:$CAMS seed:$SEED"
say "  arm: {\"hazard_stairs\": false, \"keep_dressing\": true} (D25) · sidecars:ON"
say "  git $(git -C "$REPO" rev-parse --short HEAD) $(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
say "================================================================"

if ! preflight; then
  say "PREFLIGHT FAILED — nothing rendered, no GPU taken."
  exit 4
fi
if [ ! -f "$HERE/baseline_frozen_rounds.json" ]; then
  say "[warn] no immutability baseline — run: python3 $HERE/hash_gate.py snapshot"
fi

IFS=',' read -r -a SCENE_ARR <<< "$SCENES"
N=${#SCENE_ARR[@]}
i=0
for scene in "${SCENE_ARR[@]}"; do
  i=$((i+1))
  say "[SCENE $i/$N $scene]"
  render "$scene" "$(conds_base "$scene")" "base"
  sub=$(conds_sub "$scene")
  if [ -n "$sub" ]; then
    say "[SCENE $i/$N $scene] declared substitution for the refused pair(s): $sub"
    render "$scene" "$sub" "sub"
  fi
done

T1=$(date +%s)
say "================================================================"
say "run_ctrl_dressing.sh render done in $(( (T1-T0)/60 )) min"
RUN_DIR="$(negobs_round_or_flat "${RUN}")"
say "  dataset/${RUN}: $(find "$RUN_DIR" -name '*.png' 2>/dev/null | wc -l) png · $(find "$RUN_DIR" -name '*.depth.npy' 2>/dev/null | wc -l) depth · $(find "$RUN_DIR" -name 'heightmap.npy' 2>/dev/null | wc -l) heightmap"

GRC=0
if [ "$DRY" = "0" ] && [ "$GATE" = "1" ] && [ "$NFAIL" = "0" ]; then
  say "[gate] python3 $HERE/hash_gate.py verify"
  python3 "$HERE/hash_gate.py" verify --ctrl-round "$RUN" 2>&1 | tee -a "$LOG"
  GRC=${PIPESTATUS[0]}
fi

if [ "$NFAIL" = "0" ] && [ "$GRC" = "0" ]; then
  if [ "$DRY" = "1" ]; then say "DRY RUN — nothing rendered"
  elif [ "$GATE" = "1" ]; then say "OK — every invocation exited 0 and the hash gate passed"
  else say "OK — every invocation exited 0 (hash gate skipped, --no-gate)"; fi
  say "next: bash $HERE/run_ctrl_eval.sh"
  say "================================================================"
  exit 0
else
  [ "$NFAIL" != "0" ] && { say "FAIL SUMMARY: $NFAIL invocation(s) did not exit 0:"; printf '%b\n' "$FAILS" | tee -a "$LOG"; }
  [ "$GRC" != "0" ] && say "FAIL: the hash gate did not pass — do NOT evaluate"
  say "  re-run this script unchanged to resume — completed cuts are no-ops"
  say "================================================================"
  exit 1
fi
