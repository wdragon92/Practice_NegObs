#!/bin/bash
# ============================================================================
# 나노바나나 배치1 r1 렌더 — RT 룩체크 12씬 + PT(실내 판정 D4·개구부 D2)
#   ① RT 전 씬 → look_check/<sceneID>/r1   (형상·특색·카메라 판정용)
#   ② PT: sceneD4(실내 발광 단독 — RT로는 판정 불가), sceneD2(개구 내부 암부)
#      → look_check/<sceneID>/r1_pt
#   실행: bash run_render_batch1_r1.sh   (RT ~2-4분/씬 + PT 2씬, 총 45~70분)
#   로그: look_check/render_batch1_r1.log
#   주의: v4 감사측 재렌더(run_finalize_v5)와 GPU 동시 사용 금지 — 시작 시 가드.
# ============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
if pgrep -f "python scene" > /dev/null; then
  echo "[가드] 다른 씬 렌더 프로세스 감지 — 중복 실행 방지를 위해 중단"; exit 8
fi
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
export PYTHONUNBUFFERED=1
LOG=look_check/render_batch1_r1.log
: > $LOG

SCENES="sceneN1_shadow_band sceneN2_asphalt_patch sceneN3_trompe_loeil \
        sceneN4_downhill_ramp sceneN5_flush_grating \
        sceneC1_snow_stairs sceneC2_leaf_stairs sceneC4_wet_stairs \
        sceneD1_loading_dock sceneD2_floor_opening sceneD3_drainage_channel \
        sceneD4_subway_platform"

echo "== [1/2] RT 룩체크 12씬 ==" | tee -a $LOG
for s in $SCENES; do
  id=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/${id}/r1 \
    timeout 900 python $s.py >> $LOG 2>&1
  echo "$s RT_EXIT=$? FILES=$(ls look_check/${id}/r1 2>/dev/null | wc -l)" | tee -a $LOG
done

echo "== [2/2] PT 판정 2씬 (실내 D4 · 개구 암부 D2) ==" | tee -a $LOG
for s in sceneD4_subway_platform sceneD2_floor_opening; do
  id=${s%%_*}
  w=600; [ "$id" = "sceneD4" ] && w=900   # 실내 발광 단독은 수렴 느림(구현 권고)
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_WARMUP=$w \
    NEGOBS_CAPTURE_DIR=look_check/${id}/r1_pt \
    timeout 2400 python $s.py >> $LOG 2>&1
  echo "$s PT_EXIT=$? FILES=$(ls look_check/${id}/r1_pt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "batch1 r1 렌더 완료" | tee -a $LOG
