#!/usr/bin/env bash
# capture_run.sh -- drive capture_plan.md §5 steps 1-2 for one world.
#   usage:  ./capture_run.sh gz_drop3 [n_frames]
# Launches bumperbot_description gazebo.launch.py with our world (route A of
# STAGE_A_INVENTORY §4), waits for the /gzcam/* Image topics, grabs frames, tears down.
# NOTE: no `set -u` -- ROS's setup.bash dereferences unset vars and would abort the script.
GZ=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
GZW=$GZ/worlds
W=${1:?world stem, e.g. gz_drop3}
N=${2:-3}
LOG=$GZ/logs
mkdir -p "$LOG" "$GZ/frames/$W"

source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh >/dev/null 2>&1
export DISPLAY=${DISPLAY:-:1}

cleanup() {
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

# wait for all 9 camera namespaces to appear (max 90 s)
for i in $(seq 1 45); do
  sleep 2
  NS=$(ros2 topic list 2>/dev/null | grep -c '^/gzcam/.*image_raw')
  [ "${NS:-0}" -ge 9 ] && break
done
echo "[capture_run] $W: $NS gzcam image topics live after $((i*2))s"
[ "${NS:-0}" -lt 1 ] && { echo "[capture_run] FATAL no topics for $W"; exit 2; }

sleep 5   # let the renderer settle before grab_frames' own --settle window
python3 "$GZ/tools/grab_frames.py" --tag "${W}_cap" --outdir "$GZ/frames/$W" -n "$N" \
    >> "$LOG/grab_$W.log" 2>&1
RC=$?
echo "[capture_run] $W: grab_frames rc=$RC  png=$(ls "$GZ/frames/$W"/*.png 2>/dev/null | wc -l)"
exit $RC
