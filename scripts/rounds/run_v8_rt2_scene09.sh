#!/bin/bash
# [v8 Y1] scene09 단독 RT 재렌더 — 지붕 셰이딩 수정 검증 (look_check/scene09/v8_rt2)
# PT 배치와 GPU 를 공유하므로 `python scenes` 프로세스가 사라질 때까지 대기 후 실행.
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
LOG=look_check/v8_rt2_scene09.log
: > $LOG
echo "[대기] PT 배치 종료 대기 중 ..." | tee -a $LOG
for i in $(seq 1 720); do            # 최대 2시간 (10s × 720)
  if ! pgrep -f "python scenes/main" >/dev/null 2>&1; then
    echo "[대기] GPU 해제 확인 (${i}회 폴링)" | tee -a $LOG
    sleep 20                          # 셧다운 여유
    break
  fi
  sleep 10
done
if pgrep -f "python scenes/main" >/dev/null 2>&1; then
  echo "[중단] PT 배치가 아직 살아 있음 — 렌더 취소" | tee -a $LOG
  exit 3
fi
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt \
  NEGOBS_CAPTURE_DIR=look_check/scene09/v8_rt2 \
  python scenes/main/scene09_ghat_riverfront.py >> $LOG 2>&1
echo "scene09 RT2 EXIT=$? FILES=$(ls look_check/scene09/v8_rt2 2>/dev/null | wc -l)" | tee -a $LOG
