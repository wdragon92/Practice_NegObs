#!/bin/bash
# Fast re-arm: user is about to kill the baseline. 2-min polls, 2-consecutive rule.
STREAK=0
while :; do
  USERPROC=$(pgrep -f "clean_yolo" | head -1)
  LOCKOK=0; flock -n /tmp/negobs_gpu.lock -c true 2>/dev/null && LOCKOK=1
  if [ -z "$USERPROC" ] && [ "$LOCKOK" = "1" ]; then
    STREAK=$((STREAK+1))
    [ "$STREAK" -ge 2 ] && { echo "[gpu_watch_fast] FREE at $(date +%H:%M:%S)"; exit 0; }
  else STREAK=0; fi
  sleep 120
done
