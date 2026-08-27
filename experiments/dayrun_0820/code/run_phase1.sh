#!/usr/bin/env bash
# DAYRUN 0820 Phase 1 -- one command: relabel both arms on a gridspec, rebuild the
# manifest, prove the tier map is grid-invariant, write the comparison + gates.
#
#   ./run_phase1.sh                       # gridspec_v1 (20 cells) -- the default
#   ./run_phase1.sh gridspec_v0.json      # ROLLBACK: the grid change is a json swap
#
# Rounds are reused as-is; nothing under dataset/ is written.
set -euo pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LAB=$REPO/experiments/mainrun_0819/code/labeling
OUT=$REPO/experiments/dayrun_0820
GRID=$LAB/${1:-gridspec_v1.json}

source /home/vislab/miniconda3/etc/profile.d/conda.sh
conda activate env_seg
export PYTHONNOUSERSITE=1

# label file is named after the gridspec, so a rollback run cannot overwrite the
# v1 labels (and vice versa)
SLUG=$(python - "$GRID" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))["version"].lower()
print(v.split("grid-")[-1].replace("-", ""))
PY
)

mkdir -p "$OUT/annotations" "$OUT/audit_samples" "$OUT/logs"
# gates.py rewrites <manifest dir>/annotations/hold_scenes.json, so the dayrun run
# gets its OWN copy of both hold files -- mainrun_0819's originals stay untouched.
[ -f "$OUT/annotations/hold_scenes.json" ] || \
  cp "$REPO/experiments/mainrun_0819/annotations/hold_scenes.json" "$OUT/annotations/"
[ -f "$OUT/annotations/extra_holds.json" ] || \
  cp "$REPO/experiments/mainrun_0819/annotations/extra_holds.json" "$OUT/annotations/"

echo "=== [0/5] synth suite (every gridspec) ==="
python "$LAB/synth_test.py" | tail -4

echo "=== [1/5] relabel both arms on $(basename "$GRID") ==="
python "$LAB/labeler.py" \
  --on-round  "$REPO/dataset/v2_corpus/260819_main_on" \
  --off-round "$REPO/dataset/v2_corpus/260819_main_off" \
  --grid "$GRID" --workers 8 \
  --out "$OUT/annotations/labels_$SLUG.json"

echo "=== [2/5] manifest ==="
python "$LAB/build_manifest.py" \
  --labels "$OUT/annotations/labels_$SLUG.json" \
  --on-round  "$REPO/dataset/v2_corpus/260819_main_on" \
  --off-round "$REPO/dataset/v2_corpus/260819_main_off" \
  --out "$OUT/dataset_manifest_v2.json"

echo "=== [3/5] INVARIANT GATE (mandatory -- stops the run on any mismatch) ==="
python "$OUT/code/invariant_gate.py" \
  --v0 "$REPO/experiments/mainrun_0819/annotations/labels_v0.json" \
  --v1 "$OUT/annotations/labels_$SLUG.json" | tee "$OUT/logs/invariant_gate.log"

echo "=== [4/5] V0 vs V1 comparison ==="
python "$OUT/code/compare_v0_v1.py" \
  --v0 "$REPO/experiments/mainrun_0819/annotations/labels_v0.json" \
  --v1 "$OUT/annotations/labels_$SLUG.json" \
  --manifest "$OUT/dataset_manifest_v2.json" \
  --split "$REPO/experiments/mainrun_0819/split_v1.json" \
  --holds "$OUT/annotations/hold_scenes.json" \
  --out "$OUT/P1_GRID_V1.md"

echo "=== [5/5] gates + audit overlays ==="
python "$LAB/gates.py" \
  --manifest "$OUT/dataset_manifest_v2.json" \
  --labels "$OUT/annotations/labels_$SLUG.json" \
  --grid "$GRID" \
  --out "$OUT/GATES_REPORT_v1grid.md" \
  --audit-dir "$OUT/audit_samples" --n-audit 10
