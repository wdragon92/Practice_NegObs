#!/bin/bash
# =============================================================================
# W3 P03 pilot — scene03 crest paving (GT-46 · GT-47).  round = 260731_w3_p03
#   look_check/README.md §2 naming: <yymmdd>_<wave>_<purpose>
#   Judge arm, identical to the frozen channel and to this scene's
#   baseline-of-record `260731_w3_s03`:
#     LOOK_V1=1 (= MTL 1 · GEO 1) · DETAIL_SCALE=2 · DETAIL_ROUGH_GAIN=0 · PT_FAST=1
#   Full preset set (16 cuts), so the A/B against 260731_w3_s03 is cut-for-cut.
#   GPU only · single instance · run inside `flock -w 7200 /tmp/negobs_gpu.lock`.
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260731_w3_p03
OUT=look_check/scene03/${ROUND}
LOG=look_check/logs/${ROUND}.log
mkdir -p "$OUT" look_check/logs

export NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$OUT
export NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1
export NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0

# K-micro item 10: capture the env INSIDE the render shell, so the stamp is
# reproducible whichever shell stamps it later (`env_source` names the origin).
python3 scripts/stamp_round.py --capture-env "$OUT" >> "$LOG" 2>&1

t0=$(date +%s.%N)
python scenes/main/scene03_riverbank.py >> "$LOG" 2>&1
rc=$?
t1=$(date +%s.%N)
cuts=$(ls "$OUT"/*.png 2>/dev/null | wc -l)
printf "[%s] rc=%d cuts=%d %.1fs\n" "$ROUND" "$rc" "$cuts" "$(echo "$t1 - $t0" | bc)"

python3 scripts/stamp_round.py "$OUT" "$ROUND" scene03 \
  --baseline-of-record \
  --compared-against look_check/scene03/260731_w3_s03 \
  --note "P03 · GT-46/GT-47 crest paving. Compared cut-for-cut against 260731_w3_s03 (the S03 round, the previous baseline-of-record for scene03). 10 lanes share this worktree; only dirty_paths_mine is loaded into this render." \
  >> "$LOG" 2>&1
tail -3 "$LOG"
exit $rc
