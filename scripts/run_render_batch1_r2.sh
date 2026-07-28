#!/bin/bash
# ============================================================================
# 나노바나나 배치1 r2 부분 재렌더 — r1 판정 수정분만
#   수정: C1 감광(dome 1200·눈 0.75) / C2 낙엽 산포 축소·감채 / C4 경면 완화
#         D2 부스러기 감광·흙무지 후퇴 / D3 오버행 저고·매입 / D4 발광 12000
#   ① RT: C1·C2·C4·D2·D3 → look_check/<id>/r2
#   ② PT: D4(발광 재판정)·D2(개구 암부) → look_check/<id>/r2_pt
#   실행: bash run_render_batch1_r2.sh
# ============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
if pgrep -f "python scene" > /dev/null; then
  echo "[가드] 다른 씬 렌더 프로세스 감지 — 중단"; exit 8
fi
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
export PYTHONUNBUFFERED=1
LOG=look_check/logs/render_batch1_r2.log
: > $LOG

echo "== [1/2] RT 재캡처 5씬 ==" | tee -a $LOG
for s in sceneC1_snow_stairs sceneC2_leaf_stairs sceneC4_wet_stairs \
         sceneD2_floor_opening sceneD3_drainage_channel; do
  id=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/${id}/r2 \
    timeout 900 python $s.py >> $LOG 2>&1
  echo "$s RT_EXIT=$? FILES=$(ls look_check/${id}/r2 2>/dev/null | wc -l)" | tee -a $LOG
done

echo "== [2/2] PT 재판정 2씬 ==" | tee -a $LOG
for s in sceneD4_subway_platform sceneD2_floor_opening; do
  id=${s%%_*}
  w=600; [ "$id" = "sceneD4" ] && w=900
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_WARMUP=$w \
    NEGOBS_CAPTURE_DIR=look_check/${id}/r2_pt \
    timeout 2400 python $s.py >> $LOG 2>&1
  echo "$s PT_EXIT=$? FILES=$(ls look_check/${id}/r2_pt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "batch1 r2 완료" | tee -a $LOG
