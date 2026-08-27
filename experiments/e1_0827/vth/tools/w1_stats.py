#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1_stats.py -- the numbers W1_CAPTURE.md reports."""
from __future__ import annotations
import json, os, re, subprocess
from collections import Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
man = json.load(open(os.path.join(HERE, "capture_manifest.json")))
plan = json.load(open(os.path.join(HERE, "plan.json")))
try:
    supp = json.load(open(os.path.join(HERE, "plan_supp.json")))
except FileNotFoundError:
    supp = []
holes = json.load(open(os.path.join(HERE, "holes.json")))
F = man["frames"]

print(f"frames captured        {len(F)}")
for w, n in man["n_frames_by_world"].items():
    print(f"  {w:16s} {n}")
print(f"  occlusion_intended   {man['n_occlusion_intended']}")
print(f"planned poses          {len(plan) + len(supp)}  (main {len(plan)} + supplement {len(supp)})")
print(f"manifest == files      {len(F) == len(plan) + len(supp)}")

log = open(os.path.join(HERE, "logs", "run_all.log")).read()
ld = [int(x) for x in re.findall(r"load=(\d+)s", log)]
gr = [int(x) for x in re.findall(r"grab=(\d+)s", log)]
tot = [int(x) for x in re.findall(r"total=(\d+)s", log)]
print(f"batches OK             {log.count('rc=0')}  / {log.count('[capture]')//2}")
if tot:
    print(f"per-batch wall s       load med {sorted(ld)[len(ld)//2]}  grab med {sorted(gr)[len(gr)//2]}"
          f"  total med {sorted(tot)[len(tot)//2]}  sum {sum(tot)}")
m = re.findall(r"DONE ok=(\d+) bad=(\S+) wall=(\d+)s", log)
for a, b, c in m:
    print(f"run_all DONE           ok={a} bad={b} wall={c}s ({int(c)/60:.1f} min)")

du = subprocess.run(["du", "-sb", os.path.join(HERE, "frames")],
                    capture_output=True, text=True).stdout.split()[0]
print(f"frames on disk         {int(du)/2**30:.2f} GiB")

for w in ("eworld2", "expandedworld"):
    fw = [f for f in F if f["world"] == w]
    print(f"--- {w}: {len(fw)} frames")
    print("    standoff m :", dict(sorted(Counter(f["standoff_m"] for f in fw if not f["occlusion_intended"]).items())))
    print("    height m   :", dict(sorted(Counter(f["height_m"] for f in fw if not f["occlusion_intended"]).items())))
    print("    pitch deg  :", dict(sorted(Counter(f["pitch_deg"] for f in fw if not f["occlusion_intended"]).items())))
    print("    size band  :", dict(sorted(Counter(f["hole_band"] for f in fw if not f["occlusion_intended"]).items())))
    print("    holes      :", dict(sorted(Counter(f["hole_id"] for f in fw).items())))
    sk = Counter(s["skip"].split("@")[0].split(":")[0] for s in holes["worlds"][w]["skips"])
    print(f"    skipped {holes['worlds'][w]['n_skipped']}:", dict(sk.most_common()))
    rgb = [f["rgb_mean"] for f in fw]
    sat = [f["rgb_sat_frac"] for f in fw]
    fin = [f["depth_finite_frac"] for f in fw]
    q = lambda a, p: sorted(a)[int(p * (len(a) - 1))]
    print(f"    RGB mean   : min {min(rgb):.1f}  med {q(rgb,.5):.1f}  max {max(rgb):.1f}")
    print(f"    RGB blown-out frac (>=250 all ch): max {max(sat):.5f}")
    print(f"    depth finite frac: min {min(fin):.3f}  med {q(fin,.5):.3f}  max {max(fin):.3f}")
