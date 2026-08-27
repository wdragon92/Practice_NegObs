#!/usr/bin/env bash
# finalize.sh -- everything that runs once the frames are on disk.
set -e
V=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/e1_0827/vth
cd "$V"
echo "===== manifest + SHA256SUMS ====="
python3 tools/build_manifest.py
echo; echo "===== depth is metric (all frames) ====="
python3 tools/verify_depth.py
echo; echo "===== RGB<->depth registration (eworld2) ====="
python3 tools/verify_align.py --world eworld2 --limit 200
echo; echo "===== world copies vs source ====="
python3 tools/verify_copies.py
echo; echo "===== contact sheet ====="
python3 tools/contact_sheet.py
echo; echo "===== baseline integrity (end of stage) ====="
tools/verify_baseline.sh
echo; echo "===== report ====="
python3 tools/write_report.py
echo; echo "===== stage numbers ====="
python3 tools/w1_stats.py
