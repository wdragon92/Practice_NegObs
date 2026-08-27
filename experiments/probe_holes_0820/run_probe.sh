#!/bin/bash
# =============================================================================
# run_probe.sh — C1 hole-type ZERO-SHOT probe, end to end, one command.
#
#   OVERNIGHT_BRIEF_0820_v1.md §4 C1 · switch RUN_HOLE_PROBE = YES
#
# THE ONE COMMAND
# ---------------
#   bash experiments/probe_holes_0820/run_probe.sh
#
# That runs, in order:
#   render   3 probe scenes x 2 arms x conds L0,L5,L7 x 8 cams
#            -> dataset/v2_probes/260821_probe_on/  and  dataset/v2_probes/260821_probe_off/
#            = 72 cuts per arm, 144 frames, sidecars ON (depth + heightmap)
#   label    labeler.py on the round PAIR with gridspec_v1 (5 sectors x 4 bands)
#            -> annotations/labels_probe.json, then build_manifest.py
#            -> dataset_manifest_probe.json, then a one-subset split
#   eval     9 FROZEN v2 checkpoints (rgb/depth/b2 x seeds 42/43/44), zero shot,
#            + twin analysis + 4 representative panels per checkpoint
#            -> eval/<model>_s<seed>/ and PROBE_TABLE.md
#
# Other entry points:
#   bash run_probe.sh --dry-run          plan + budget + every command, run none
#   bash run_probe.sh --phase render     just the render (needs the GPU lock)
#   bash run_probe.sh --phase label      just label -> manifest -> split (CPU)
#   bash run_probe.sh --phase eval       just the 9 zero-shot evals
#   bash run_probe.sh --scenes probeH1   one scene (both arms)
#   bash run_probe.sh --arms on          one arm
#   PROBE_CPU_EVAL=1 bash run_probe.sh --phase eval     force the evals to CPU
#
# NOTHING HERE TRAINS. Not one line. The nine checkpoints are opened read-only
# (brief C1: "훈련 편입 절대 금지 — 평가 전용").
#
# ISOLATION — the guarantees this script is written to keep
# ---------------------------------------------------------
#  * writes only `dataset/v2_probes/260821_probe_{on,off}/` and this experiment directory;
#    `guard_run_name` refuses any other run stamp, and `PROBE_ONLY` refuses any
#    scene whose name does not start with `probe`;
#  * the corpus AZ-ledger split is proven unchanged by `probe_driver.install()`'s
#    SPLIT_GUARD on every invocation, in every subprocess;
#  * frames land under `dataset/<run>/probe/<scene>/` — a fourth split name, so
#    a probe frame can never be mistaken for corpus train/val/test;
#  * `mainrun_0819/` and `dayrun_0820/` are read-only inputs here.
#
# TWIN PROTOCOL (brief C1 "트윈 규약 엄수: hazard on/off, seed·카메라 포즈 바이트 동일")
# ---------------------------------------------------------------------------
# Both arms use the SAME seed (20260822), so `vk.var_seed(scene,"cam",i,seed)`
# gives cut i of a scene byte-identical camera parameters in both arms. The
# scenes are built so the hazard toggle cannot move `ground_z` under any camera
# (`probe_common.twin_audit`, checked pre-boot in both arms), so the eye position
# is identical too — no D20-style 0.15 m pairing tolerance is needed here, and
# the twin step asserts that by running with `--tol 0.0`.
#
# GPU
# ---
# Every GPU step goes through `flock /tmp/negobs_gpu.lock` (absolute rule 5).
# rc 201 = the lock was busy for the whole wait; the script records it and moves
# on rather than queueing forever. The user's robot baseline is never touched.
#
# BUDGET (measured, not assumed)
# ------------------------------
# `probe_driver.py --plan` prints 5.4 min/arm from the SP-3 constants, which
# exclude sidecars. The honest figure is the measured one from the 08-19/08-20
# sidecar rounds: 3.3 s/cut (light scene, scene15) to 7.5 s/cut (heavy scene,
# scene09), wall time including the boot. These probes are light (~40 prims), so
# 144 cuts x ~3.5-4.5 s ~= 9-11 min of GPU, call it 12-20 min with the six boots
# and the lock waits. Compare: brief §5 estimated "C1 렌더 30-60분".
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
W="$REPO/experiments/probe_holes_0820"
CFG="$W/render_configs"
LOGDIR="$W/logs"
LOG="$LOGDIR/probe.log"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT="${LOCK_WAIT:-3600}"
LOCK_RC=201

SEED="${SEED:-20260822}"
CAMS="${CAMS:-8}"
CONDS="${CONDS:-L0,L5,L7}"
RUN_ON=260821_probe_on
RUN_OFF=260821_probe_off
GRID=gridspec_v1.json

SCENES="probeH1 probeH2 probeH3"
ARMS="on off"
PHASE=all
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --scenes)  SCENES="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --arms)    ARMS="$(echo "$2" | tr ',' ' ')"; shift 2 ;;
    --conds)   CONDS="$2"; shift 2 ;;
    --phase)   PHASE="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '1,70p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$LOGDIR" "$W/annotations" "$W/eval"

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# --- guards -----------------------------------------------------------------
guard_run_name() {
  case "$1" in
    260821_probe_on|260821_probe_off) return 0 ;;
    *) echo "[fatal] refusing run stamp '$1' — this script only ever writes" >&2
       echo "        dataset/v2_probes/260821_probe_{on,off}." >&2; exit 4 ;;
  esac
}
PROBE_ONLY() {
  case "$1" in
    probe*) return 0 ;;
    *) echo "[fatal] '$1' is not a probe scene. This script may not render a" >&2
       echo "        corpus scene: the corpus is frozen (absolute rule 2)." >&2
       exit 4 ;;
  esac
}

# --- the render shell preamble (run_260819_main.sh:140-144) -----------------
PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

# The eval half lives in env_seg (torch), not env_isaaclab.
PYBIN=/home/vislab/miniconda3/envs/env_seg/bin/python
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 $PYBIN"

FAILS=""
NFAIL=0
fail() { FAILS="${FAILS}\n  $*"; NFAIL=$((NFAIL+1)); }

# ============================================================================
# PHASE 1 — render
# ============================================================================
render_one() {                      # render_one <scene> <arm>
  local scene="$1" arm="$2"
  PROBE_ONLY "$scene"
  local run; [ "$arm" = "on" ] && run="$RUN_ON" || run="$RUN_OFF"
  guard_run_name "$run"
  local cfgfile="$CFG/${scene}_${arm}.json"
  local outdir
  outdir="$(negobs_round_or_flat "${run}")/probe/${scene}"

  if [ ! -f "$cfgfile" ]; then
    say "  [FAIL] $scene $arm: missing $cfgfile"; fail "$scene $arm: missing config"; return
  fi
  if [ "$DRY" = "1" ]; then
    say "  [dry] $scene $arm conds=$CONDS cfg=$(cat "$cfgfile") -> dataset/${run}/probe/${scene}"
    return
  fi

  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SCENE_CONFIG=\$(cat '$cfgfile')
mkdir -p '$outdir'
python3 '$W/probe_driver.py' --run '$run' --scenes '$scene' \
        --conds '$CONDS' --cams $CAMS --seed $SEED
rc=\$?
python3 scripts/stamp_round.py --capture-env '$outdir' || true
exit \$rc" >> "$LOG" 2>&1
  local rc=$?

  if [ "$rc" = "0" ]; then
    local why; why=$(scene_ok "$run" "$scene" "$CONDS")
    if [ $? = 0 ]; then say "  [ok]   $scene $arm — $why"
    else say "  [FAIL] $scene $arm — $why"; fail "$scene $arm: $why"; fi
  elif [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $scene $arm — no GPU lock within ${LOCK_WAIT}s, skipped"
    fail "$scene $arm: LOCK-TIMEOUT (rc 201)"
  else
    say "  [FAIL] $scene $arm rc=$rc"; fail "$scene $arm: rc=$rc"
  fi
}

scene_ok() {                        # scene_ok <run> <scene> <conds>
  python3 - "$(negobs_round_or_flat "$1")/manifest.json" "$2" "$3" <<'PY'
import json, sys
mf_path, scene, conds = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
try:
    mf = json.load(open(mf_path, encoding="utf-8"))
except Exception as e:
    print(f"manifest unreadable: {e}"); sys.exit(1)
rec = mf.get("scenes", {}).get(scene)
if not rec: print("no manifest record"); sys.exit(1)
if rec.get("exit") != 0: print(f"subprocess exit {rec.get('exit')}"); sys.exit(1)
if not rec.get("cuts"): print("0 cuts"); sys.exit(1)
missing = [c for c in conds if c not in (rec.get("done_conds") or [])]
if missing: print(f"conditions not marked done: {missing}"); sys.exit(1)
print(f"exit 0 · {rec['cuts']} cuts · {rec.get('sec_per_cut')} s/cut")
PY
}

phase_render() {
  say "--- PHASE render: scenes[$SCENES] arms[$ARMS] conds $CONDS cams $CAMS seed $SEED"
  bash -c "$PRE
python3 '$W/probe_driver.py' --plan --run '$RUN_ON' --scenes '$(echo $SCENES | tr ' ' ',')' \
        --conds '$CONDS' --cams $CAMS --seed $SEED" 2>&1 | tee -a "$LOG"
  for scene in $SCENES; do
    for arm in $ARMS; do
      say "[render $scene arm=$arm]"
      render_one "$scene" "$arm"
    done
  done
  [ "$DRY" = "1" ] && return 0
  for run in "$RUN_ON" "$RUN_OFF"; do
    d="$(negobs_round_or_flat "$run")"
    say "  dataset/$run: $(find "$d" -name '*.png' 2>/dev/null | wc -l) png · \
$(find "$d" -name '*.depth.npy' 2>/dev/null | wc -l) depth · \
$(find "$d" -name 'heightmap.npy' 2>/dev/null | wc -l) heightmap"
  done
  # Through the shim, not directly: check_data_run's check 2 is the azimuth
  # ledger conformance test and it calls vk.ledger() on every scene it sees.
  bash -c "$PRE
python3 '$W/probe_driver.py' --check-run $RUN_ON
python3 '$W/probe_driver.py' --check-run $RUN_OFF" \
    >> "$LOG" 2>&1 || say "  [note] check_data_run reported findings — see $LOG"
}

# ============================================================================
# PHASE 2 — label -> manifest -> split   (CPU, env_seg)
# ============================================================================
phase_label() {
  local L="$W/annotations/labels_probe.json"
  local M="$W/dataset_manifest_probe.json"
  local S="$W/split_probe.json"
  local LAB="$REPO/experiments/mainrun_0819/code/labeling"
  local ON_DIR OFF_DIR                # 0827: rounds are grouped
  ON_DIR="$(negobs_round_or_flat "$RUN_ON")"
  OFF_DIR="$(negobs_round_or_flat "$RUN_OFF")"
  say "--- PHASE label: gridspec_v1 on the round pair"
  local c1="cd '$LAB' && $PY labeler.py --on-round '$ON_DIR' \
--off-round '$OFF_DIR' --grid $GRID --out '$L' --workers 6"
  local c2="cd '$LAB' && $PY build_manifest.py --labels '$L' \
--on-round '$ON_DIR' --off-round '$OFF_DIR' --out '$M'"
  local c3="$PY '$W/eval_probe.py' --step split --manifest '$M' --split '$S'"
  if [ "$DRY" = "1" ]; then
    say "  [dry] $c1"; say "  [dry] $c2"; say "  [dry] $c3"; return 0
  fi
  for c in "$c1" "$c2" "$c3"; do
    say "  [cpu] ${c:0:110}..."
    bash -c "$c" >> "$LOG" 2>&1 || { say "  [FAIL] $c"; fail "label: ${c:0:60}"; return 1; }
  done
  $PY "$W/eval_probe.py" --step tiers --manifest "$M" --out "$W/TIER_TABLE.md" \
      --grid "$LAB/$GRID" 2>&1 | tee -a "$LOG"
}

# ============================================================================
# PHASE 3 — zero-shot eval of the 9 frozen v2 checkpoints
# ============================================================================
phase_eval() {
  local M="$W/dataset_manifest_probe.json"
  local S="$W/split_probe.json"
  say "--- PHASE eval: 9 frozen v2 checkpoints, zero shot, NOTHING TRAINS"
  local args=(--step eval --manifest "$M" --split "$S" --out "$W/eval"
              --table "$W/PROBE_TABLE.md" --grid "$GRID" --log "$LOG")
  [ "$DRY" = "1" ] && args+=(--dry-run)
  [ "${PROBE_CPU_EVAL:-0}" = "1" ] && args+=(--cpu)
  $PY "$W/eval_probe.py" "${args[@]}" 2>&1 | tee -a "$LOG"
  return ${PIPESTATUS[0]}
}

# ============================================================================
T0=$(date +%s)
say "================================================================"
say "run_probe.sh start — phase=$PHASE dry=$DRY seed=$SEED"
say "  git $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null) \
$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)"
say "  EVALUATION ONLY — no probe frame may enter training (brief C1)"
say "================================================================"

case "$PHASE" in
  render) phase_render ;;
  label)  phase_label ;;
  eval)   phase_eval || fail "eval phase" ;;
  all)    phase_render
          if [ "$NFAIL" = "0" ] || [ "$DRY" = "1" ]; then
            phase_label && { phase_eval || fail "eval phase"; }
          else
            say "  [skip] render had $NFAIL failure(s) — not labelling a partial round"
          fi ;;
  *) echo "unknown --phase '$PHASE' (render|label|eval|all)" >&2; exit 2 ;;
esac

T1=$(date +%s)
say "================================================================"
say "run_probe.sh done in $(( (T1-T0)/60 )) min"
if [ "$NFAIL" = "0" ]; then
  say "FAIL SUMMARY: none"
  say "  tiers -> $W/TIER_TABLE.md"
  say "  table -> $W/PROBE_TABLE.md"
  say "================================================================"
  exit 0
else
  say "FAIL SUMMARY: $NFAIL step(s) failed:"
  printf '%b\n' "$FAILS" | tee -a "$LOG"
  say "  re-run this script unchanged to resume — completed work is a no-op"
  say "================================================================"
  exit 1
fi
