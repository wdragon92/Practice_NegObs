#!/usr/bin/env bash
# infer_run_v3.sh -- v3-A re-run of the GAZEBO_TRACK zero-shot read-out (DIAGNOSTIC / NARRATIVE).
#
# Same recipe as infer_run.sh, three deltas and nothing else:
#   1. checkpoints  experiments/v3_0823/runs/v3a/rgb_s{42,43,44}/best.pt   (v2 had 6 models;
#      v3-A wave trained the rgb family only, so there is NO v3 b2 counterpart -- 216, not 432)
#   2. outputs      out_v3/  (a NEW tree; out/ is never touched)
#   3. NO factory swap: all three v3-A ckpts are resnet34-unet-aux / 20 cells, so the frozen
#      infer_photo.py loads them directly (verified: encoder_from_config -> "resnet34").
# Everything frozen in GAZEBO_TRACK.md §4 is reused UNCHANGED: same 9 views, same _000 frame,
# same --grid gridspec_v1.json --fit squash --tau 0.5, same per-view height/pitch/hfov from the
# capture manifests, CPU only (CUDA_VISIBLE_DEVICES="" -> no GPU lock needed).
GZ=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
CK=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a
CODE=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code
PY=${PY:-/home/vislab/miniconda3/envs/env_seg/bin/python}
OVR=${OVR:-/tmp/claude-1000/-home-vislab-Desktop-work-sy/112dc8d6-e4e7-45cb-99a3-8bde8b5d3036/scratchpad/gz_overlays_v3}
mkdir -p "$GZ/out_v3/json" "$OVR" "$GZ/logs"

JOBS=$GZ/logs/infer_jobs_v3.txt
: > "$JOBS"
for W in gz_drop3 gz_drop3_ctrl gz_drop4 gz_drop4_ctrl gz_drop1 gz_drop1_ctrl gz_drop2 gz_drop2_ctrl; do
  for V in extra_h0.3_d1.2 preset_h0.3_d2 preset_h0.3_d5 preset_h0.3_d10 \
           preset_h0.9_d2 preset_h0.9_d5 preset_h0.9_d10 rs_h0.125_d2 rs_h0.125_d5; do
    case $V in
      *h0.9*)   H=0.9;   P=-10; F=60 ;;
      *h0.125*) H=0.125; P=-15; F=69 ;;
      *)        H=0.3;   P=-10; F=60 ;;
    esac
    IMG=$GZ/frames/$W/${W}_cap_${V}_000.png
    [ -f "$IMG" ] || { echo "[skip] $IMG" >&2; continue; }
    for M in rgb_s42 rgb_s43 rgb_s44; do
      echo "$IMG|$CK/$M/best.pt|$OVR/${M}__${W}__${V}.png|$GZ/out_v3/json/${M}__${W}__${V}.json|$H|$P|$F"
    done
  done
done >> "$JOBS"
echo "[infer_run_v3] $(wc -l < "$JOBS" ) jobs staged" >&2

run_one() {
  IFS='|' read -r IMG CKPT OUT JSON H P F <<< "$1"
  [ -s "$JSON" ] && return 0                       # resumable
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 \
  "$PY" "$CODE/infer_photo.py" --image "$IMG" --ckpt "$CKPT" \
      --grid "$CODE/labeling/gridspec_v1.json" --out "$OUT" --json "$JSON" \
      --height "$H" --pitch "$P" --hfov "$F" --fit squash --tau 0.5 >/dev/null 2>&1 \
    || echo "[FAIL] $JSON" >&2
}
export -f run_one
export CODE GZ PY

cd "$CODE" || exit 1
xargs -a "$JOBS" -d '\n' -P "${PAR:-6}" -I{} bash -c 'run_one "$@"' _ {}
echo "[infer_run_v3] json written: $(ls "$GZ/out_v3/json"/*.json 2>/dev/null | wc -l)"
