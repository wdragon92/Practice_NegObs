#!/bin/bash
# ============================================================================
# 나노바나나 배치1 SMOKE 직렬 검증 — sceneN1~N5 / C1·C2·C4 / D1~D4 (12씬)
#   NEGOBS_SMOKE=1 = 부팅+조립 후 조기종료 (렌더 없음, 런타임 조립 오류 검출)
#   실행: bash run_smoke_batch1.sh   (씬당 ~1-2분, 총 ~20분)
#   로그: look_check/smoke_batch1.log
# ============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
export PYTHONUNBUFFERED=1
LOG=look_check/logs/smoke_batch1.log
: > $LOG

PASS=0; FAIL=0; FAILED=""
for s in sceneN1_shadow_band sceneN2_asphalt_patch sceneN3_trompe_loeil \
         sceneN4_downhill_ramp sceneN5_flush_grating \
         sceneC1_snow_stairs sceneC2_leaf_stairs sceneC4_wet_stairs \
         sceneD1_loading_dock sceneD2_floor_opening sceneD3_drainage_channel \
         sceneD4_subway_platform; do
  echo "== SMOKE $s ==" | tee -a $LOG
  NEGOBS_SMOKE=1 timeout 300 python $s.py >> $LOG 2>&1
  code=$?
  if [ $code -eq 0 ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); FAILED="$FAILED $s($code)"; fi
  echo "$s SMOKE_EXIT=$code" | tee -a $LOG
done
echo "SMOKE 완료: PASS=$PASS FAIL=$FAIL${FAILED:+ — 실패:$FAILED}" | tee -a $LOG
