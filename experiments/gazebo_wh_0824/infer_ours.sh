#!/usr/bin/env bash
# infer_ours.sh -- our frozen cell-probability models, ZERO-SHOT, on the same frames.
#
# Same recipe as weekend_0823/gazebo/infer_run{,_v3}.sh: frozen infer_photo.py, frozen
# gridspec_v1, --fit squash --tau 0.5, and the per-view height/pitch/hfov taken from the
# CAPTURE MANIFEST (measured, not assumed -- the cameras are static models so the pose is
# exact).  Two checkpoints only, as briefed:
#     v2   experiments/dayrun_0820/runs/v2/rgb_s42/best.pt
#     v3a  experiments/v3_0823/runs/v3a/rgb_s42/best.pt
# CPU only -> no GPU lock is taken.  Separate shell from the capture shell: the ONLY
# interface between them is the PNG files (ISOLATION.md).
GZ=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/gazebo_wh_0824
CODE=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code
PY=${PY:-/home/vislab/miniconda3/envs/env_seg/bin/python}
OVR=${OVR:-/tmp/claude-1000/-home-vislab-Desktop-work-sy/112dc8d6-e4e7-45cb-99a3-8bde8b5d3036/scratchpad/wh_overlays}
declare -A CK=(
  [v2_rgb_s42]=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt
  [v3a_rgb_s42]=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s42/best.pt
)
mkdir -p "$GZ/out/ours/json" "$OVR" "$GZ/logs"

JOBS=$GZ/logs/infer_jobs_ours.txt
: > "$JOBS"
H=0.125; P=-14.954; F=69.001          # manifest values, identical for all 8 approach views
for W in wh0 wh_e wh_h wh_hc; do
  for V in rs_d0.5 rs_d0.7 rs_d0.9 rs_d1.1 rs_d1.5 rs_d2 rs_d2.6 rs_d3.4; do
    IMG=$GZ/frames/$W/${W}_cap_${V}_000.png
    [ -f "$IMG" ] || { echo "[skip] $IMG" >&2; continue; }
    for M in "${!CK[@]}"; do
      echo "$IMG|${CK[$M]}|$OVR/${M}__${W}__${V}.png|$GZ/out/ours/json/${M}__${W}__${V}.json|$H|$P|$F"
    done
  done
done >> "$JOBS"
echo "[infer_ours] $(wc -l < "$JOBS") jobs staged" >&2

run_one() {
  IFS='|' read -r IMG CKPT OUT JSON H P F <<< "$1"
  [ -s "$JSON" ] && return 0
  CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONNOUSERSITE=1 \
  "$PY" "$CODE/infer_photo.py" --image "$IMG" --ckpt "$CKPT" \
      --grid "$CODE/labeling/gridspec_v1.json" --out "$OUT" --json "$JSON" \
      --height "$H" --pitch "$P" --hfov "$F" --fit squash --tau 0.5 >/dev/null 2>&1 \
    || echo "[FAIL] $JSON" >&2
}
export -f run_one
export CODE GZ PY

cd "$CODE" || exit 1
xargs -a "$JOBS" -d '\n' -P "${PAR:-6}" -I{} bash -c 'run_one "$@"' _ {}
echo "[infer_ours] json written: $(ls "$GZ/out/ours/json"/*.json 2>/dev/null | wc -l)"
