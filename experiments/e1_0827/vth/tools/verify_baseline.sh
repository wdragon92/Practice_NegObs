#!/usr/bin/env bash
# verify_baseline.sh -- the baseline clone must be untouched, start and end of the stage.
# Two checks: (a) the 6-file table published in P0_BASELINE_DIFF.md, (b) a full census of
# every file in the clone against the snapshot this stage took before it started.
B=/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance
V=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/e1_0827/vth
echo "== P0 table (worlds + hole model) =="
cd "$B/bumperbot_description" || exit 2
declare -A EXP=(
 [worlds/eworld2.world]=9cb2a2c028cfaace
 [worlds/expandedworld.world]=2a1956d3ea564a4f
 [worlds/smallest_world.world]=5c88e743b07eb8f6
 [worlds/eworld.world]=dc8b7a19f9895a72
 [models/large_holed_floor/model.sdf]=c2751bac52bcd5dd
 [models/large_holed_floor/meshes/large_holed_floor.stl]=ab75bc68feb3adae
)
BAD=0
for f in "${!EXP[@]}"; do
  got=$(sha256sum "$f" | cut -c1-16)
  if [ "$got" = "${EXP[$f]}" ]; then echo "  OK   $f  $got"
  else echo "  FAIL $f  got $got want ${EXP[$f]}"; BAD=$((BAD+1)); fi
done
echo "== full census vs stage-start snapshot =="
cd "$B" || exit 2
find . -type f -print0 | sort -z | xargs -0 sha256sum > "$V/logs/BASELINE_SHA256_END.txt"
N=$(diff <(sort "$V/logs/BASELINE_SHA256_START.txt") <(sort "$V/logs/BASELINE_SHA256_END.txt") | grep -c '^[<>]')
echo "  files: $(wc -l < "$V/logs/BASELINE_SHA256_END.txt")   differing entries: $N"
echo "== git (read-only) =="
echo "  HEAD $(git rev-parse --short HEAD)"
git status --porcelain | sed 's/^/  /'
[ $BAD -eq 0 ] && [ "$N" -eq 0 ] && echo "BASELINE UNCHANGED" || echo "BASELINE CHANGED"
