#!/bin/bash
# =============================================================================
# run_cueoff.sh — the CUE-OFF intervention render (GPU-2, D31 (1) / D36)
#
# Pre-registration: PREREG_CUEOFF.md  (written and timestamped BEFORE this
# script may render a single cut; `gates_cueoff.py` G_PREREG enforces it).
#
# WHAT IT RENDERS
# ---------------
#   3 scenes x up to 5 arms x 1-2 camera bands, all from ISOLATED SCENE COPIES
#   under scenes_cueoff/ .  The canonical scenes in scenes/main/ are never
#   opened for writing by anything in this directory.
#
#     A   hazard + cues                (baseline; must reproduce the corpus, G0)
#     B2  hazard, GUARD removed        (scene12, scene20 -- scene17 has no guard)
#     B1  hazard, ALL cues removed
#     P   hazard + cues, NON-cue objects removed   (placebo, D35 / R2 sec.5.3-2)
#     C   NO hazard + cues kept        (keep_dressing port, D25/D30 lineage)
#
# WHY --scene-proc AND NOT THE NORMAL DRIVER
# ------------------------------------------
# `run_data_render.py` resolves scene files by globbing scenes/{main,batch1},
# so the normal `--run/--scenes` entry point cannot see an isolated copy, and
# teaching it to would mean editing a driver that the V2S queue is running
# RIGHT NOW.  The driver's own in-process half takes the scene FILE as its first
# argument:
#     run_data_render.py --scene-proc <file> <scene_key> <out_dir> <conds> <cams> <seed>
# so pointing it at scenes_cueoff/ is a supported call, not a hack, and it keeps
# the driver read-only.  The environment `drive()` would have set is reproduced
# verbatim below (run_data_render.py:170-187) -- if that block ever changes,
# this one has to change with it, which is why it is quoted rather than guessed.
#
# SEEDS ARE PER BAND, NOT GLOBAL
# ------------------------------
# boost_e / boost_h were seeded 20260820, boost_e2 was seeded **20260821**
# (measured in the shipped variation.json files).  Every arm of one scene-band
# shares one seed, which is the condition that matters; using each band's
# lineage seed additionally makes arm A a bit-for-bit re-render of the audited
# rows.  PREREG sec.2.1 records this deviation from the brief's "seed 20260820".
#
# RESUME
# ------
# Safe to re-run at any point.  The driver skips a cut whose PNG + depth sidecar
# already exist and whose variation record says ok (run_data_render.py:461-467),
# so a completed scene-arm costs one Isaac boot and no renders.  Nothing here
# deletes anything.
#
# GPU ETIQUETTE
# -------------
# Every invocation is `flock -o -w 3600 -E 201 /tmp/negobs_gpu.lock`, the same
# lock and the same timeout the V2S queue uses.  rc 201 = never got the lock; it
# is recorded as a FAIL and re-running is safe.  `--smoke` holds the GPU for one
# cut only (< 3 min including boot) so it can slot between V2S runs.
#
# USAGE
#   bash run_cueoff.sh --dry-run              # print the plan, render nothing
#   bash run_cueoff.sh --smoke                # 3 x 1-cut arm-C smoke  (GATE G1)
#   bash run_cueoff.sh                        # the full matrix (stages 1+2)
#   bash run_cueoff.sh --stages 1             # primary bands only
#   bash run_cueoff.sh --scenes scene17 --arms A,B1
# Log: experiments/weekend_0823/cue_audit/logs/cueoff_render.log
# Exit 0 only if every invocation exited 0.
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
AUDIT="$REPO/experiments/weekend_0823/cue_audit"
SCN="$AUDIT/scenes_cueoff"
CFG="$AUDIT/render_configs"
LOGDIR="$AUDIT/logs"
LOG="$LOGDIR/cueoff_render.log"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=3600
LOCK_RC=201
CAMS=8
CONDS=L0,L5,L7

mkdir -p "$LOGDIR"

# --- scene file map ---------------------------------------------------------
scene_file() {
  case "$1" in
    scene12) echo "$SCN/scene12_riverside_deck.py" ;;
    scene17) echo "$SCN/scene17_ramp_pair_hangang.py" ;;
    scene20) echo "$SCN/scene20_diagonal_oblique.py" ;;
    *) echo "" ;;
  esac
}

# --- camera bands (lineage, CUEOFF_CANDIDATES sec.4.2) ----------------------
BAND_E='{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}'
BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_E2='{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}'
# --- A2 / D49 repair band for scene20 -----------------------------------------
# PREREG sec.4.5-3 voids scene20 at paired-H 6 < 10.  The pre-registration itself
# names the remedy (sec.7 risk 2 -> R4 F14 -> D49 (a)): keep every arm, keep the
# seed, and re-sample the CAMERA so the same scene yields more strict-H poses.
# Lower and nearer eyes graze the mesa lip more often, which is the mechanism
# that makes a frame strict-H in this corpus (H_CUE_AUDIT sec.2.2).
# Nothing about the hypotheses, the arms or the thresholds moves.
BAND_S20FIX='{"d_min":4,"d_max":8,"h_min":0.25,"h_max":0.6}'

# --- the render matrix ------------------------------------------------------
# stage | round stem | scene | band json | seed | arms
#   stage 1 = each scene's PRIMARY lineage band  (the audit's H frames)
#   stage 2 = scene12's SECOND band (boost_e2) -- doubles scene12 H 24 -> 48
#   stage 3 = scene17's main band  (+9 H frames)  -- optional, off by default
MATRIX="
1|260823_cueoff|scene12|BAND_E|20260820|A,B2,B1,P,C
1|260823_cueoff|scene17|BAND_H|20260820|A,B1,P,C
1|260823_cueoff|scene20|BAND_E2|20260821|A,B2,B1,P,C
2|260823_cueoff2|scene12|BAND_E2|20260821|A,B2,B1,P,C
3|260823_cueoff3|scene17|NONE|20260819|A,B1,P,C
4|260823_cueoff_s20fix|scene20|BAND_S20FIX|20260821|A,B2,B1,P,C
"

STAGES="1 2"
SCENES_OVERRIDE=""
ARMS_OVERRIDE=""
DRY=0
SMOKE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --stages)  STAGES="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --cams)    CAMS="$2"; shift 2 ;;
    --scenes)  SCENES_OVERRIDE="$2"; shift 2 ;;
    --arms)    ARMS_OVERRIDE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --smoke)   SMOKE=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# --- the one mistake this script must make impossible -----------------------
guard_run_name() {
  case "$1" in
    260823_cueoff_A|260823_cueoff_B1|260823_cueoff_B2|260823_cueoff_P|260823_cueoff_C|\
    260823_cueoff2_A|260823_cueoff2_B1|260823_cueoff2_B2|260823_cueoff2_P|260823_cueoff2_C|\
    260823_cueoff3_A|260823_cueoff3_B1|260823_cueoff3_B2|260823_cueoff3_P|260823_cueoff3_C|\
    260823_cueoff_s20fix_A|260823_cueoff_s20fix_B1|260823_cueoff_s20fix_B2|\
    260823_cueoff_s20fix_P|260823_cueoff_s20fix_C)
      return 0 ;;
    *) echo "[fatal] refusing run stamp '$1' — this script only ever writes" >&2
       echo "        dataset/cueoff/260823_cueoff{,2,3,_s20fix}_{A,B1,B2,P,C}." >&2
       exit 4 ;;
  esac
}

# --- the shell preamble every render subshell repeats -----------------------
#     (run_260819_main.sh:140-144; PYTHONNOUSERSITE=1 is mandatory on this box)
PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

band_json() {
  case "$1" in
    BAND_E)  echo "$BAND_E" ;;
    BAND_H)  echo "$BAND_H" ;;
    BAND_E2) echo "$BAND_E2" ;;
    BAND_S20FIX) echo "$BAND_S20FIX" ;;
    NONE)    echo "" ;;
    *) echo "[fatal] unknown band '$1'" >&2; exit 2 ;;
  esac
}

# --- pre-flight: PREREG must exist and predate everything -------------------
if [ ! -f "$AUDIT/PREREG_CUEOFF.md" ]; then
  echo "[fatal] PREREG_CUEOFF.md is missing. A CUE-OFF render without a" >&2
  echo "        pre-registration is not an experiment. Refusing." >&2
  exit 5
fi

# --- pre-flight: lookfix derivatives (CPU, what drive() does at :226) -------
preflight_assets() {
  bash -c "$PRE
python3 - <<'PY'
import sys, os
sys.path.insert(0, '$REPO/scripts')
os.environ.setdefault('NEGOBS_RENDER_ROLE', 'data')
import run_data_render as R
print('[assets]', R.prepare_assets('$(echo $CONDS | tr ',' ' ')'.split()) or 'nothing to make')
PY" >> "$LOG" 2>&1
}

# --- the split each scene files under (driver derives it itself) ------------
SPLITMAP=$(bash -c "$PRE
python3 - <<'PY'
import sys; sys.path.insert(0, '$REPO')
import variation_kit as vk
for s in ('scene12','scene17','scene20'):
    print(s, vk.split_of(s))
PY") || { echo "[fatal] could not compute the split map" >&2; exit 3; }
split_of() { echo "$SPLITMAP" | awk -v s="$1" '$1==s{print $2}'; }

# --- did the scene subprocess actually produce the cuts? --------------------
scene_ok() {                      # scene_ok <out_dir> <expected_cuts>
  python3 - "$1" "$2" <<'PY'
import json, os, sys
d, want = sys.argv[1], int(sys.argv[2])
p = os.path.join(d, "variation.json")
try:
    v = json.load(open(p, encoding="utf-8"))
except Exception as e:
    print(f"variation.json unreadable: {e}"); sys.exit(1)
cu = v["cuts"]
cuts = list(cu.values() if isinstance(cu, dict) else cu)
n_ok = sum(1 for c in cuts if c.get("ok"))
miss = [c["file"] for c in cuts
        if not os.path.isfile(os.path.join(d, c["file"]))]
if n_ok < want:
    print(f"only {n_ok}/{want} ok cuts"); sys.exit(1)
if miss:
    print(f"{len(miss)} PNG missing e.g. {miss[:2]}"); sys.exit(1)
if not os.path.isfile(os.path.join(d, "heightmap.npy")):
    print("heightmap.npy sidecar missing"); sys.exit(1)
print(f"{n_ok} cuts · {v.get('sec_per_cut')} s/cut · seed {v.get('seed')}")
PY
}

# --- one flocked render -----------------------------------------------------
FAILS=""
NFAIL=0
render() {   # render <stem> <scene> <band_json> <seed> <arm> <cams> <conds> <out_dir>
  local stem="$1" scene="$2" band="$3" seed="$4" arm="$5" cams="$6" conds="$7" outdir="$8"
  local sfile; sfile=$(scene_file "$scene")
  local cfgfile="$CFG/${scene}_${arm}.json"
  local want; want=$(( cams * $(echo "$conds" | tr ',' ' ' | wc -w) ))

  if [ -z "$sfile" ] || [ ! -f "$sfile" ]; then
    say "  [FAIL] $scene $arm: no isolated scene copy"
    FAILS="${FAILS}\n  ${stem} ${scene} ${arm}: no scene copy"; NFAIL=$((NFAIL+1)); return
  fi
  if [ ! -f "$cfgfile" ]; then
    say "  [FAIL] $scene $arm: missing $cfgfile"
    FAILS="${FAILS}\n  ${stem} ${scene} ${arm}: missing config"; NFAIL=$((NFAIL+1)); return
  fi
  if [ "$DRY" = "1" ]; then
    say "  [dry] $stem $scene $arm seed=$seed cams=$cams conds=$conds"
    say "        cfg=$(cat "$cfgfile")"
    say "        band=${band:-<none>}  ->  ${outdir#$REPO/}"
    return
  fi

  mkdir -p "$outdir"
  # The env block below is `run_data_render.drive()` :170-187, verbatim.
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_RENDER_ROLE=data
export NEGOBS_SEED='$seed'
export NEGOBS_LIGHT_COND='$conds'
export NEGOBS_CAM_MODE=random
export NEGOBS_CAM_N='$cams'
export NEGOBS_CAPTURE=1
export NEGOBS_CAPTURE_MODE=pt
export NEGOBS_PT_FAST=1
export NEGOBS_LOOK_V1=1
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SCENE_CONFIG=\$(cat '$cfgfile')
$( [ -n "$band" ] && echo "export NEGOBS_CAM_BAND_OVERRIDE='$band'" )
python3 '$REPO/scripts/run_data_render.py' --scene-proc \
        '$sfile' '$scene' '$outdir' '$conds' '$cams' '$seed'
rc=\$?
python3 '$REPO/scripts/stamp_round.py' --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  local rc=$?

  if [ "$rc" = "0" ]; then
    local why; why=$(scene_ok "$outdir" "$want")
    if [ $? = 0 ]; then
      say "  [ok]   $stem $scene $arm — $why"
    else
      say "  [FAIL] $stem $scene $arm — $why"
      FAILS="${FAILS}\n  ${stem} ${scene} ${arm}: ${why}"; NFAIL=$((NFAIL+1))
    fi
  elif [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $stem $scene $arm — no GPU lock within ${LOCK_WAIT}s, skipped"
    FAILS="${FAILS}\n  ${stem} ${scene} ${arm}: LOCK-TIMEOUT (rc 201)"; NFAIL=$((NFAIL+1))
  else
    say "  [FAIL] $stem $scene $arm rc=$rc"
    FAILS="${FAILS}\n  ${stem} ${scene} ${arm}: rc=$rc"; NFAIL=$((NFAIL+1))
  fi
}

# =============================================================================
T0=$(date +%s)
say "================================================================"
say "run_cueoff.sh  stages='$STAGES' smoke=$SMOKE dry=$DRY"
say "prereg $(date -r "$AUDIT/PREREG_CUEOFF.md" '+%F %T')"
[ "$DRY" = "1" ] || preflight_assets

# --- SMOKE MODE: one cut of arm C per ported scene (gate G1) ----------------
if [ "$SMOKE" = "1" ]; then
  say "--- SMOKE: 1 cut, cond L0, ARM C (the only new code path) per scene ---"
  for row in $MATRIX; do
    IFS='|' read -r stage stem scene bandkey seed arms <<< "$row"
    [ "$stage" = "1" ] || continue
    [ -n "$SCENES_OVERRIDE" ] && case ",$SCENES_OVERRIDE," in *",$scene,"*) ;; *) continue ;; esac
    band=$(band_json "$bandkey")
    out="$AUDIT/smoke/$scene"
    render "$stem" "$scene" "$band" "$seed" "C" 1 "L0" "$out"
  done
  [ "$DRY" = "1" ] || bash -c "$PRE
python3 '$AUDIT/smoke_summarize.py'" >> "$LOG" 2>&1
  [ "$DRY" = "1" ] || python3 "$AUDIT/smoke_summarize.py" --print
  say "--- SMOKE done ---"
fi

# --- FULL MATRIX ------------------------------------------------------------
if [ "$SMOKE" != "1" ]; then
  for row in $MATRIX; do
    IFS='|' read -r stage stem scene bandkey seed arms <<< "$row"
    case " $STAGES " in *" $stage "*) ;; *) continue ;; esac
    [ -n "$SCENES_OVERRIDE" ] && case ",$SCENES_OVERRIDE," in *",$scene,"*) ;; *) continue ;; esac
    band=$(band_json "$bandkey")
    split=$(split_of "$scene")
    say "--- stage $stage · $stem · $scene · band ${bandkey} · seed $seed ---"
    for arm in $(echo "${ARMS_OVERRIDE:-$arms}" | tr ',' ' '); do
      case ",$arms," in *",$arm,"*) ;; *)
        say "  [skip] $scene has no arm $arm (see PREREG sec.2.2)"; continue ;; esac
      run="${stem}_${arm}"
      guard_run_name "$run"
      render "$stem" "$scene" "$band" "$seed" "$arm" "$CAMS" "$CONDS" \
             "$(negobs_round_or_flat "$run")/$split/$scene"
    done
  done
fi

DT=$(( $(date +%s) - T0 ))
say "================================================================"
if [ "$NFAIL" = "0" ]; then
  say "run_cueoff.sh COMPLETE — 0 failures · ${DT}s"
else
  say "run_cueoff.sh FAILURES ($NFAIL) · ${DT}s"
  printf '%b\n' "$FAILS" | tee -a "$LOG"
fi
say "next: python3 $AUDIT/gates_cueoff.py --stage pre"
exit $(( NFAIL > 0 ))
