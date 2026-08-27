#!/usr/bin/env bash
# run_all.sh [batch ...] -- capture every VTH batch, one gzserver load at a time.
# Each batch takes the project GPU lock on its own so a concurrent CPU job is not blocked
# for the whole run.  A batch that comes back short is retried once with a longer settle.
VTH=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/e1_0827/vth
BATCHES=${@:-$(python3 -c "
import json,os
o=[]
for f in ('batches.json','batches_supp.json'):
    p=os.path.join('$VTH/worlds',f)
    if os.path.exists(p):
        b=json.load(open(p))
        for w in ('eworld2','expandedworld'):
            o += b.get(w, [])
print(' '.join(o))")}
T0=$(date +%s)
OK=0; BAD=""
for B in $BATCHES; do
  pkill -9 -x gzserver >/dev/null 2>&1; sleep 2
  flock -o /tmp/negobs_gpu.lock "$VTH/tools/capture_batch.sh" "$B"
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "[run_all] $B rc=$RC -- retry with SETTLE=16"
    pkill -9 -x gzserver >/dev/null 2>&1; sleep 3
    SETTLE=16 flock -o /tmp/negobs_gpu.lock "$VTH/tools/capture_batch.sh" "$B"
    RC=$?
  fi
  [ $RC -eq 0 ] && OK=$((OK+1)) || BAD="$BAD $B"
  echo "[run_all] progress: $OK ok,${BAD:- none} bad, $(( $(date +%s)-T0 ))s elapsed"
done
pkill -9 -x gzserver >/dev/null 2>&1
echo "[run_all] DONE ok=$OK bad=${BAD:-none} wall=$(( $(date +%s)-T0 ))s"
