#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_copies.py -- every world copy is the paper's file plus exactly one added block."""
import glob, os, re, sys
SRC = ("/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/"
       "bumperbot_description/worlds")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B0 = "    <!-- ===== ADDED BY make_vth_worlds.py"
B1 = "    <!-- ===== END ADDED BLOCK ===== -->"
bad = []
n = 0
for p in sorted(glob.glob(os.path.join(HERE, "worlds", "*.world"))):
    stem = os.path.basename(p).rsplit("_", 1)[0]
    src = open(os.path.join(SRC, stem + ".world")).read()
    cp = open(p).read()
    i, j = cp.find(B0), cp.find(B1)
    if i < 0 or j < 0:
        bad.append((p, "no added block")); continue
    rest = cp[:i] + cp[j + len(B1):]
    if rest.replace("\n", "") != src.replace("\n", ""):
        bad.append((p, "source bytes differ outside the added block"))
    n += 1
print(f"world copies checked {n}   deviations {len(bad)}")
for p, why in bad:
    print("  ", os.path.basename(p), why)
sys.exit(1 if bad else 0)
