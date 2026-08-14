#!/bin/bash
# 배치1 r3 — C1(감광+PT 판정 전환)·D3(오버행 잔디 립) 재렌더만
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
if pgrep -f "python scene" > /dev/null; then
  echo "[가드] 다른 씬 렌더 프로세스 감지 — 중단"; exit 8
fi
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
export PYTHONUNBUFFERED=1
LOG=look_check/logs/render_batch1_r3.log
: > $LOG

NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/sceneD3/r3 \
  timeout 900 python sceneD3_drainage_channel.py >> $LOG 2>&1
echo "sceneD3 RT_EXIT=$? FILES=$(ls look_check/sceneD3/r3 2>/dev/null | wc -l)" | tee -a $LOG

NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/sceneC1/r3 \
  timeout 900 python sceneC1_snow_stairs.py >> $LOG 2>&1
echo "sceneC1 RT_EXIT=$? FILES=$(ls look_check/sceneC1/r3 2>/dev/null | wc -l)" | tee -a $LOG

NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_WARMUP=600 \
  NEGOBS_VIEWS="approach,grazing_top,lower_lookback,preset_h0.9_d5" \
  NEGOBS_CAPTURE_DIR=look_check/sceneC1/r3_pt \
  timeout 2400 python sceneC1_snow_stairs.py >> $LOG 2>&1
echo "sceneC1 PT_EXIT=$? FILES=$(ls look_check/sceneC1/r3_pt 2>/dev/null | wc -l)" | tee -a $LOG
echo "batch1 r3 완료" | tee -a $LOG
