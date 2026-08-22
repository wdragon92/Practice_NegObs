#!/usr/bin/env bash
# infer_run.sh -- capture_plan.md §5 step 3, widened to 6 frozen RGB seeds and all 9 views.
# infer_photo.py is used VERBATIM (no flag added): its --json already dumps cell_ids + probs,
# so the CSV in tools/collect_csv.py is built from those JSONs -- zero change to the tool.
# Overlays are bulky and mostly unused, so they go to a scratch dir; representative panels
# are copied into out/panels/ afterwards.
GZ=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
CK=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2
CODE=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code
OVR=${OVR:-/tmp/claude-1000/-home-vislab-Desktop-work-sy/112dc8d6-e4e7-45cb-99a3-8bde8b5d3036/scratchpad/gz_overlays}
mkdir -p "$GZ/out/json" "$OVR" "$GZ/logs"

JOBS=$GZ/logs/infer_jobs.txt
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
    for M in rgb_s42 rgb_s43 rgb_s44 b2_s42 b2_s43 b2_s44; do
      echo "$IMG|$CK/$M/best.pt|$OVR/${M}__${W}__${V}.png|$GZ/out/json/${M}__${W}__${V}.json|$H|$P|$F"
    done
  done
done >> "$JOBS"
echo "[infer_run] $(wc -l < "$JOBS" ) jobs staged" >&2

run_one() {
  IFS='|' read -r IMG CKPT OUT JSON H P F <<< "$1"
  [ -s "$JSON" ] && return 0                       # resumable
  # b2_* was trained through b2_polar/b2_model_factory (MiT-B2); code/model_factory hard-codes
  # resnet34, so infer_photo cannot load it directly -- tools/infer_photo_b2.py swaps the
  # factory and re-enters infer_photo.main() unchanged.
  TOOL="$CODE/infer_photo.py"
  case "$CKPT" in */b2_s*) TOOL="$GZ/tools/infer_photo_b2.py" ;; esac
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 \
  python3 "$TOOL" --image "$IMG" --ckpt "$CKPT" \
      --grid "$CODE/labeling/gridspec_v1.json" --out "$OUT" --json "$JSON" \
      --height "$H" --pitch "$P" --hfov "$F" --fit squash --tau 0.5 >/dev/null 2>&1 \
    || echo "[FAIL] $JSON" >&2
}
export -f run_one
export CODE GZ

cd "$CODE" || exit 1
xargs -a "$JOBS" -d '\n' -P "${PAR:-6}" -I{} bash -c 'run_one "$@"' _ {}
echo "[infer_run] json written: $(ls "$GZ/out/json"/*.json 2>/dev/null | wc -l)"
