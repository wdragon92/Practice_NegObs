#!/bin/bash
# =============================================================================
# Judge-freeze proof round — lighting/camera implementation (D1/D2)
#   usage: bash scripts/rounds/run_260730_lcfreeze.sh {pre|post}
#
# Renders a fixed judge subset twice — once before the lighting/camera
# implementation lands and once after — on a **byte-identical render arm** to
# the standing round `260730_w2d_fix`.  `regression_check.py` v2.1 then compares
# pre -> post: the implementation is only accepted if the judge channel moves by
# nothing but the PT noise floor (see `Docs/reports/lighting_spikes_v1.md` §1.2,
# which measured that floor at 0.08-3.42 LSB with every decision metric at 0).
#
# The subset is the 3 scenes the mini data-run uses (one per measured azimuth
# class: S / A' / B') plus scene04 as a plain C'-class control.
# GPU exclusive, sequential, single instance.
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ARM="${1:?give the arm: pre | post}"
case "$ARM" in pre|post) ;; *) echo "arm must be pre|post"; exit 9;; esac

ROUND=260730_lcfreeze_${ARM}
LOG=look_check/logs/${ROUND}.log
TIMES=look_check/logs/${ROUND}_times.tsv
mkdir -p look_check/logs
: > $LOG
printf "scene\tsec\tcuts\texit\n" > $TIMES

# stem:subdir
SUBSET="sceneN1_shadow_band:batch1 sceneN4_downhill_ramp:batch1 \
scene02_underpass:main scene04_parktrail:main"

for spec in $SUBSET; do
  s=${spec%%:*}; sub=${spec##*:}
  n=${s%%_*}
  out=look_check/${n}/${ROUND}
  mkdir -p $out
  # Identical arm to 260730_w2d_fix. Nothing else may be set: role/variation env
  # would trip the judge gate by design.
  export NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out
  export NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1
  export NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0
  t0=$(date +%s.%N)
  python scenes/${sub}/$s.py >> $LOG 2>&1
  rc=$?
  t1=$(date +%s.%N)
  dt=$(echo "$t1 - $t0" | bc)
  cuts=$(ls $out/*.png 2>/dev/null | wc -l)
  printf "%s\t%.1f\t%d\t%d\n" "$n" "$dt" "$cuts" "$rc" | tee -a $TIMES
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
done
echo "[$ROUND] done" | tee -a $LOG
