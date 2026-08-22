#!/usr/bin/env bash
# V2S TEST TRACK -- step 1 of PROJECT_STATE_0823 12.6: relabel the WHOLE merged corpus
# on gridspec_v2s.json (10 sectors x 4 bands = 40 cells), then merge.
#
#   bash relabel_v2s.sh
#
# Isolation (PS 12.6 "격리 규칙"): every output of this script lives under
# experiments/weekend_0823/v2s/.  Nothing under experiments/dayrun_0820/ or
# experiments/mainrun_0819/ is written, and nothing under dataset/ is touched --
# the four rendered round PAIRS are reused byte-for-byte, exactly as the V1
# merged corpus (dayrun_0820/code/merge_corpus.py) built them.
#
# The four pairs are the same four the V1 corpus is made of:
#   main     260819_main_on     / 260819_main_off      1584 frames (bare frame ids)
#   boost_h  260820_boost_h_on  / 260820_boost_h_off    192 frames (id + '::boost_h')
#   boost_e  260820_boost_e_on  / 260820_boost_e_off    672 frames (id + '::boost_e')
#   boost_e2 260820_boost_e2_on / 260820_boost_e2_off   384 frames (id + '::boost_e2')
#                                                      ----
#                                                      2832
set -euo pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LAB=$REPO/experiments/mainrun_0819/code/labeling
V2S=$REPO/experiments/weekend_0823/v2s
GRID=$LAB/gridspec_v2s.json
WORKERS="${WORKERS:-8}"

source /home/vislab/miniconda3/etc/profile.d/conda.sh
conda activate env_seg
export PYTHONNOUSERSITE=1
export CUDA_VISIBLE_DEVICES=""          # CPU ONLY -- the GPU belongs to the night queue

mkdir -p "$V2S/annotations" "$V2S/logs"

echo "=== [0/3] gridspec + synth suite on every gridspec (V0 / V1 / V2S) ==="
python "$REPO/experiments/mainrun_0819/code/gridspec.py" "$GRID"
python "$LAB/synth_test.py" | tail -5

label_pair () {           # label_pair <tag> <on-round> <off-round>
  local tag="$1" on="$2" off="$3"
  echo "=== [1/3] relabel $tag on gridspec_v2s ==="
  python "$LAB/labeler.py" \
    --on-round  "$REPO/dataset/$on" \
    --off-round "$REPO/dataset/$off" \
    --grid "$GRID" --workers "$WORKERS" \
    --out "$V2S/annotations/labels_v2s_$tag.json"
  echo "=== [2/3] manifest $tag ==="
  python "$LAB/build_manifest.py" \
    --labels "$V2S/annotations/labels_v2s_$tag.json" \
    --on-round  "$REPO/dataset/$on" \
    --off-round "$REPO/dataset/$off" \
    --out "$V2S/manifest_v2s_$tag.json"
}

label_pair main     260819_main_on     260819_main_off
label_pair boost_h  260820_boost_h_on  260820_boost_h_off
label_pair boost_e  260820_boost_e_on  260820_boost_e_off
label_pair boost_e2 260820_boost_e2_on 260820_boost_e2_off

echo "=== [3/3] merge the four pairs (merge_corpus.py PATTERN, V2S variant) ==="
python "$V2S/code/merge_corpus_v2s.py"

echo "=== done -> $V2S/annotations/labels_v2s.json + $V2S/dataset_manifest_v2s_full.json ==="
