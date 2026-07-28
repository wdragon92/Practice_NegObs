#!/bin/bash
# v4측 v5 렌더 종료 대기 후 배치1 r2 자동 실행 (3회 연속 무프로세스 확인 = 씬 전환 갭 오탐 방지)
clear_count=0
while [ $clear_count -lt 3 ]; do
  if pgrep -f "python scene" > /dev/null; then
    clear_count=0
  else
    clear_count=$((clear_count + 1))
  fi
  sleep 60
done
bash /home/vislab/Desktop/work_sy/Practice_NegObs/run_render_batch1_r2.sh
