#!/bin/bash
# ============================================================================
# 배치1 맥락 라운드(ctx1) 검증 체인 — 씬 위치: scenes/batch1/
#   ① SMOKE 12씬 직렬 (실패 시 렌더 중단)
#   ② RT 전 12씬 → look_check/<id>/ctx1
#   ③ PT: D4(실내 판정) 전 뷰 + C1·C4(overcast, RT 평면광 보완) 서브셋
#      → look_check/<id>/ctx1_pt
#   로그: look_check/logs/batch1_ctx1.log
# ============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs/scenes/batch1 || exit 9
if pgrep -f "python scene" > /dev/null; then
  echo "[가드] 다른 씬 렌더 프로세스 감지 — 중단"; exit 8
fi
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
export PYTHONUNBUFFERED=1
LOG=../../look_check/logs/batch1_ctx1.log
: > $LOG

SCENES="sceneN1_shadow_band sceneN2_asphalt_patch sceneN3_trompe_loeil \
        sceneN4_downhill_ramp sceneN5_flush_grating \
        sceneC1_snow_stairs sceneC2_leaf_stairs sceneC4_wet_stairs \
        sceneD1_loading_dock sceneD2_floor_opening sceneD3_drainage_channel \
        sceneD4_subway_platform"

echo "== [1/3] SMOKE 12씬 ==" | tee -a $LOG
FAIL=0
for s in $SCENES; do
  NEGOBS_SMOKE=1 timeout 300 python $s.py >> $LOG 2>&1
  code=$?
  echo "$s SMOKE_EXIT=$code" | tee -a $LOG
  [ $code -ne 0 ] && FAIL=$((FAIL+1))
done
if [ $FAIL -ne 0 ]; then echo "SMOKE 실패 $FAIL건 — 렌더 중단" | tee -a $LOG; exit 7; fi

echo "== [2/3] RT 12씬 ==" | tee -a $LOG
for s in $SCENES; do
  id=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=../../look_check/${id}/ctx1 \
    timeout 900 python $s.py >> $LOG 2>&1
  echo "$s RT_EXIT=$? FILES=$(ls ../../look_check/${id}/ctx1 2>/dev/null | wc -l)" | tee -a $LOG
done

echo "== [3/3] PT 판정 ==" | tee -a $LOG
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_WARMUP=900 \
  NEGOBS_CAPTURE_DIR=../../look_check/sceneD4/ctx1_pt \
  timeout 2400 python sceneD4_subway_platform.py >> $LOG 2>&1
echo "sceneD4 PT_EXIT=$? FILES=$(ls ../../look_check/sceneD4/ctx1_pt 2>/dev/null | wc -l)" | tee -a $LOG
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_WARMUP=600 \
  NEGOBS_VIEWS="approach,grazing_top,lower_lookback" \
  NEGOBS_CAPTURE_DIR=../../look_check/sceneC1/ctx1_pt \
  timeout 2400 python sceneC1_snow_stairs.py >> $LOG 2>&1
echo "sceneC1 PT_EXIT=$? FILES=$(ls ../../look_check/sceneC1/ctx1_pt 2>/dev/null | wc -l)" | tee -a $LOG
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_WARMUP=600 \
  NEGOBS_VIEWS="approach,grazing_mirror,film_closeup" \
  NEGOBS_CAPTURE_DIR=../../look_check/sceneC4/ctx1_pt \
  timeout 2400 python sceneC4_wet_stairs.py >> $LOG 2>&1
echo "sceneC4 PT_EXIT=$? FILES=$(ls ../../look_check/sceneC4/ctx1_pt 2>/dev/null | wc -l)" | tee -a $LOG
echo "batch1 ctx1 완료" | tee -a $LOG
