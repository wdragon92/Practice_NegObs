#!/usr/bin/env bash
# capture_batch.sh <batch_name>   e.g. eworld2_b00
# Headless gzserver on a world COPY, grab one RGB+depth per camera, tear down.
# gzclient is NEVER started (the owner is at the machine; no viewer window may pop up).
# NOTE: only -s libgazebo_ros_init.so is loaded.  Adding libgazebo_ros_factory.so makes
# gzserver abort with "could not create service: rcl node's context is invalid" on this
# install, and we do not spawn anything, so the factory plugin is not needed.
VTH=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/e1_0827/vth
B=${1:?batch name}
# batch names are <world>_b## (main) or <world>_s## (supplement); strip either.
W=$(printf %s "$B" | sed -E 's/_[a-z][0-9]+$//')
NCAM=$(python3 -c "import json;print(len(json.load(open('$VTH/worlds/$B.cams.json'))))")
LOG=$VTH/logs
mkdir -p "$LOG" "$VTH/frames/$W"

source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh >/dev/null 2>&1
export DISPLAY=${DISPLAY:-:1}
export GAZEBO_MODEL_PATH=/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/bumperbot_description/models:${GAZEBO_MODEL_PATH}

# Gazebo Classic often ignores SIGTERM while the render loop is busy, which leaves the
# PREVIOUS world's server alive and the next batch then grabs the wrong world (observed).
# SIGKILL, then WAIT until the process table is actually clear.
kill_gz() {
  pkill -9 -x gzserver >/dev/null 2>&1
  pkill -9 -x gzclient >/dev/null 2>&1
  for _ in $(seq 1 30); do
    pgrep -x gzserver >/dev/null 2>&1 || return 0
    sleep 1
  done
  echo "[capture] WARNING gzserver still alive after SIGKILL"
}
cleanup() { kill_gz; }
trap cleanup EXIT

kill_gz; sleep 1

T0=$(date +%s)
setsid gzserver -s libgazebo_ros_init.so "$VTH/worlds/$B.world" \
    > "$LOG/sim_$B.log" 2>&1 < /dev/null &

# The ROS 2 daemon caches the graph, so right after a fresh gzserver `ros2 topic list`
# happily reports the PREVIOUS world's camera topics and the readiness test passes on a
# server that is not up yet (RUN_GUIDE.md documents this daemon-cache trap).  Drop the
# daemon and refuse to look at the graph for MINWAIT seconds.
ros2 daemon stop >/dev/null 2>&1
sleep "${MINWAIT:-12}"

NS=0
for i in $(seq 1 90); do
  if ! pgrep -x gzserver >/dev/null 2>&1; then
    echo "[capture] $B: FATAL gzserver died -- see $LOG/sim_$B.log"; exit 3
  fi
  NS=$(ros2 topic list 2>/dev/null | grep -c '/cam/depth/image_raw$')
  [ "${NS:-0}" -ge "$NCAM" ] && break
  sleep 2
done
T1=$(date +%s)
echo "[capture] $B: $NS/$NCAM depth topics live after $((T1-T0))s"
if [ "${NS:-0}" -lt "$NCAM" ]; then
  echo "[capture] $B: FATAL only $NS topics"; exit 2
fi

# hard guard: the live server must be THIS batch's world
if ! pgrep -a -x gzserver 2>/dev/null | grep -q "$B.world"; then
  echo "[capture] $B: FATAL live gzserver is not this batch's world"; exit 5
fi

python3 "$VTH/tools/grab_vth.py" --cams "$VTH/worlds/$B.cams.json" \
    --outdir "$VTH/frames/$W" --settle "${SETTLE:-8}" --timeout 90 > "$LOG/grab_$B.log" 2>&1
RC=$?
T2=$(date +%s)
echo "[capture] $B: rc=$RC  $(grep '^\[grab_vth\]' "$LOG/grab_$B.log" | tail -1)  load=$((T1-T0))s grab=$((T2-T1))s total=$((T2-T0))s"
exit $RC
