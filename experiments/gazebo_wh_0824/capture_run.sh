#!/usr/bin/env bash
# capture_run.sh -- one warehouse-variant world: launch, wait for cameras, grab, tear down.
#   usage:  ./capture_run.sh wh0 [n_frames]
# Route (A) of weekend_0823/gazebo/STAGE_A_INVENTORY.md §4: the baseline's own
# gazebo.launch.py with an ABSOLUTE, extension-less world_name.  That launch file
# SetEnvironmentVariable's GAZEBO_MODEL_PATH to the baseline's models dir, which is
# exactly what our worlds need (they keep every `model://aws_robomaker_*` URI).
# Baseline_NegObs is READ-ONLY: we only launch from it.
# NOTE: no `set -u` -- ROS's setup.bash dereferences unset vars and would abort.
GZ=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/gazebo_wh_0824
GZW=$GZ/worlds
W=${1:?world stem, e.g. wh0}
N=${2:-3}
LOG=$GZ/logs
NCAM=${NCAM:-8}
mkdir -p "$LOG" "$GZ/frames/$W"

source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh >/dev/null 2>&1
export DISPLAY=${DISPLAY:-:1}

cleanup() {
  [ -n "${GUIKILL:-}" ] && kill "$GUIKILL" 2>/dev/null
  [ -n "${SIMPID:-}" ] && kill -INT -"$SIMPID" 2>/dev/null
  sleep 3
  pkill -f gzclient >/dev/null 2>&1
  pkill -f gzserver >/dev/null 2>&1
  pkill -f spawn_entity >/dev/null 2>&1
  pkill -f robot_state_publisher >/dev/null 2>&1
  sleep 2
}
trap cleanup EXIT

# stale processes from a previous world would keep publishing the old topics
pkill -f gzserver >/dev/null 2>&1; pkill -f gzclient >/dev/null 2>&1; sleep 2
ros2 daemon stop >/dev/null 2>&1

setsid ros2 launch bumperbot_description gazebo.launch.py \
    world_name:="$GZW/$W" > "$LOG/sim_$W.log" 2>&1 &
SIMPID=$!
sleep 1
SIMPID=$(ps -o pgid= -p $SIMPID 2>/dev/null | tr -d ' ')

# --- GUI suppression (owner is at the machine; no viewer window may pop up) ---
# bumperbot_description/gazebo.launch.py includes gzclient.launch.py unconditionally and
# exposes no gui:= argument, so the only lever is to kill the viewer as soon as it appears.
# gzSERVER does the sensor rendering, so frames are unaffected (weekend track, proven).
# Reaper runs for 40 s because gzclient is started by the launch system, not by us, and can
# come up several seconds after gzserver.
( for _ in $(seq 1 80); do pkill -f gzclient >/dev/null 2>&1; sleep 0.5; done ) &
GUIKILL=$!

for i in $(seq 1 60); do
  sleep 2
  NS=$(ros2 topic list 2>/dev/null | grep -c '^/gzcam/.*image_raw')
  [ "${NS:-0}" -ge "$NCAM" ] && break
done
echo "[capture_run] $W: $NS gzcam image topics live after $((i*2))s"
[ "${NS:-0}" -lt 1 ] && { echo "[capture_run] FATAL no topics for $W"; exit 2; }

sleep 6   # let the renderer settle before grab_frames' own --settle window
python3 "$GZ/tools/grab_frames.py" --tag "${W}_cap" --outdir "$GZ/frames/$W" -n "$N" \
    >> "$LOG/grab_$W.log" 2>&1
RC=$?
echo "[capture_run] $W: grab_frames rc=$RC  png=$(ls "$GZ/frames/$W"/*.png 2>/dev/null | wc -l)"
exit $RC
