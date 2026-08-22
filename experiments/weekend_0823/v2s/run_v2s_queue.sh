#!/usr/bin/env bash
# ============================================================================
# V2S TEST TRACK -- GPU STAGE (PS 12.6 procedure 2 + WEEKEND_BRIEF_0823 5.1 GPU-0)
#
#   bash experiments/weekend_0823/v2s/run_v2s_queue.sh          # everything
#   bash experiments/weekend_0823/v2s/run_v2s_queue.sh unet     # the 9 GPU runs only
#   bash experiments/weekend_0823/v2s/run_v2s_queue.sh yolo     # the CPU remap only
#
# PRECONDITION -- DO NOT START THIS UNTIL THE INVARIANT GATE HAS PASSED.
#   bash experiments/weekend_0823/v2s/code/relabel_v2s.sh
#   python experiments/weekend_0823/v2s/code/invariant_gate_v2s.py \
#       --v1 experiments/dayrun_0820/annotations/labels_v1_full.json \
#       --v2s experiments/weekend_0823/v2s/annotations/labels_v2s.json --label 2832
#   (any failure = HARD STOP, record the cause, roll back -- PS 12.6 procedure 1)
#
# ISOLATION: every artefact of this script lands under experiments/weekend_0823/v2s/.
# V1 labels, manifests, splits, runs and reports are read-only inputs. The V1 canon
# is not replaced until the user rules adoption (PS 12.6 채택/롤백 기준).
#
# ---------------------------------------------------------------------------
# WHY THE SPLIT IS *NOT* REGENERATED
# ---------------------------------------------------------------------------
# experiments/dayrun_0820/split_v2_full.json is reused VERBATIM. The split is a
# partition of SCENE NAMES ({"train":[...], "val":[...], "test":[...], "hold":[...]}) --
# it carries no cell, sector or band information whatsoever, and both arms of a twin
# always travel with their scene. V2S changes only how each frame's hazard footprint
# is tiled in azimuth; it moves no frame between scenes and adds/removes no frame.
# Regenerating it would risk a DIFFERENT test set, which would make the V1 vs V2S
# headline comparison apples-to-oranges -- exactly what PS 12.6's adoption criterion
# ① (headline inside the V1 seed spread) needs to exclude. Same scenes, same frames,
# same seeds: the only thing that changes is the answer sheet's angular resolution.
# (The 7 test scenes stay untouchable per PS §9.)
#
# ---------------------------------------------------------------------------
# BIAS-INIT -- NOTHING TO PRECOMPUTE  (PS 12.6 procedure 2 ⓑ)
# ---------------------------------------------------------------------------
# `--bias-init prior` is already in COMMON_TRAIN inside run_queue_v2.sh. train_polar.py
# computes the prior AT RUNTIME from the manifest it is handed:
#     prior = dtr.positive_rate()            # train_polar.py, the TRAIN split only
#     set_prior_bias(model, prior, grid.n_cells)
# so passing the V2S manifest is by itself the "V2S 셀별 양성률로 재산출" the spec asks
# for -- the 40-cell per-cell positive rates fall out of the V2S labels, and the final
# classifier's bias vector is sized from grid.n_cells. There is no precomputed prior
# file anywhere in the stack to regenerate. config.json records the vector actually
# used as `train_positive_rate` / `bias_init_values`; check them in the first run.
#
# HFLIP -- also nothing to do: gridspec.Grid.flip_perm() is the generic
# `band*ns + (ns-1-sector)`, which at ns=10 yields the pairing (1<->10, 2<->9, 3<->8,
# 4<->7, 5<->6) with NO fixed centre sector. Verified by `python gridspec.py
# labeling/gridspec_v2s.json` (involution + no cell crosses a band).
# ============================================================================
set -u -o pipefail

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
MAIN=$REPO/experiments/mainrun_0819
DAY=$REPO/experiments/dayrun_0820
V2S=$REPO/experiments/weekend_0823/v2s

MANIFEST=$V2S/dataset_manifest_v2s_full.json
SPLIT=$DAY/split_v2_full.json                 # REUSED VERBATIM -- see the note above
GRID=gridspec_v2s.json                        # resolved by gridspec.SEARCH_DIRS
OUT=$V2S/runs
SEEDS="${SEEDS:-42 43 44}"
MODELS="${MODELS:-rgb depth b2}"

STAGE="${1:-all}"
mkdir -p "$OUT" "$OUT/logs" "$V2S/logs"

if [ ! -f "$MANIFEST" ]; then
  echo "[fatal] $MANIFEST missing -- run code/relabel_v2s.sh first"; exit 2
fi

# ---------------------------------------------------------------- U-Net / B2
if [ "$STAGE" = "all" ] || [ "$STAGE" = "unet" ]; then
  echo "=== V2S: run_queue_v2.sh (rgb/depth/b2 x $SEEDS, recipe v2 unchanged) ==="
  bash "$MAIN/code/run_queue_v2.sh" \
    "$MANIFEST" \
    "$SPLIT" \
    "$OUT" \
    "$GRID" \
    "$SEEDS" \
    "$MODELS" 2>&1 | tee -a "$V2S/logs/run_v2s_queue.log"
fi

# ---------------------------------------------------------------- YOLO remap
# NO RETRAINING (PS 12.6: "YOLO는 재훈련 불필요 -- det2cell 재매핑 + 재평가만").
# The detections in dayrun_0820/runs/yolo_s*/pred_{test,val}/labels are boxes in
# image space: they know nothing about the polar grid, so the V1-trained detector's
# raw output is re-mapped through the V2S gridspec and re-scored. CPU only, no GPU
# lock needed -- nothing here touches the device.
if [ "$STAGE" = "all" ] || [ "$STAGE" = "yolo" ]; then
  YPY=$DAY/venv_yolo/bin/python                       # as in dayrun code/run_yolo_all.sh
  EPY=/home/vislab/miniconda3/envs/env_seg/bin/python
  export PYTHONNOUSERSITE=1
  export CUDA_VISIBLE_DEVICES=""
  echo "=== V2S: YOLO det2cell remap + re-eval (no retraining) ==="
  for S in $SEEDS; do
    for SUB in test val; do
      SRC=$DAY/runs/yolo_s$S/pred_$SUB/labels
      [ -d "$SRC" ] || { echo "[yolo] missing $SRC -- skipped"; continue; }
      "$YPY" "$DAY/code/yolo/det2cell.py" \
        --pred-labels "$SRC" \
        --manifest "$MANIFEST" \
        --split "$SPLIT" --subset "$SUB" \
        --grid "$MAIN/code/labeling/gridspec_v2s.json" \
        --conf 0.05 \
        --out "$OUT/yolo_s$S/cells_$SUB" || exit 1
    done
    "$EPY" "$MAIN/code/eval_polar.py" \
      --per-frame-a "$OUT/yolo_s$S/cells_test/per_frame.csv" \
      --grid "$MAIN/code/labeling/gridspec_v2s.json" \
      --out "$OUT/yolo_s$S/eval_test" \
      --tau-op 0.25 --tau-sweep 0.1,0.25,0.5 || exit 1
    echo "[yolo] seed $S remapped -> $OUT/yolo_s$S"
  done 2>&1 | tee -a "$V2S/logs/run_v2s_yolo.log"
fi

echo "=== V2S queue done -> $OUT ==="
