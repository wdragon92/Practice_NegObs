#!/bin/bash
# OVERNIGHT_BRIEF_0820 §2 GPU queue: poll every 10 min; require TWO CONSECUTIVE
# checks with (a) lock obtainable and (b) no user compute process, then exit 0.
# Exit 3 at the 05:00 deadline (GPU track abandoned, resume package to morning).
STREAK=0
while :; do
  H=$(date +%H); M=$(date +%M)
  if [ "$H" = "05" ] || [ "$H" = "06" ]; then echo "[gpu_watch] 05:00 deadline reached"; exit 3; fi
  USERPROC=$(pgrep -f "clean_yolo" | head -1)
  LOCKOK=0
  flock -n /tmp/negobs_gpu.lock -c true 2>/dev/null && LOCKOK=1
  if [ -z "$USERPROC" ] && [ "$LOCKOK" = "1" ]; then
    STREAK=$((STREAK+1))
    echo "[gpu_watch] $(date +%H:%M) free check streak=$STREAK"
    [ "$STREAK" -ge 2 ] && { echo "[gpu_watch] GPU FREE (2 consecutive) at $(date +%H:%M)"; exit 0; }
  else
    STREAK=0
    echo "[gpu_watch] $(date +%H:%M) busy (user=$USERPROC lock_ok=$LOCKOK)"
  fi
  sleep 600
done
