#!/usr/bin/env python3
"""G7 scope scan — every (boost band, scene) in the corpus, AABB footprint vs a
depth-fusion footprint computed in memory.  Answers "are the five known pairs the
whole defect, or is there a sixth?"  Nothing is written to disk."""
import json, os, sys
import numpy as np
REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code/labeling"))
from labeler import scene_dirs, load_heightmap
from fuse_heightmap import fuse_scene_arm
HZ = 0.3
MAIN_FUSED = {"scene02", "scene07", "scene08", "scene12", "scene16"}


def fp(on, off):
    v = ~np.isfinite(on) | ~np.isfinite(off)
    d = np.where(v, np.nan, off - on)
    return int(((~v) & (d >= HZ)).sum())


print(f"{'band':5s} {'scene':8s} {'aabb/aabb':>10s} {'fused/fused':>11s} {'aabbON/fusOFF':>13s} "
      f"{'cov f_on':>8s} {'cov f_off':>9s} {'missing depth':>13s}  verdict")
flags = []
for band in ("h", "e", "e2"):
    on = scene_dirs(round_dir_or_flat(f"260820_boost_{band}_on"))
    off = scene_dirs(round_dir_or_flat(f"260820_boost_{band}_off"))
    for sc in sorted(on):
        a_on = load_heightmap(on[sc])[0]
        a_off = load_heightmap(off[sc])[0]
        f_on, m_on = fuse_scene_arm(on[sc])
        f_off, m_off = fuse_scene_arm(off[sc])
        aa, ff, mix = fp(a_on, a_off), fp(f_on, f_off), fp(a_on, f_off)
        best = max(ff, mix)
        bad = best >= 500 and aa < 0.10 * best
        miss = len(m_on["fusion"]["missing_depth"]) + len(m_off["fusion"]["missing_depth"])
        if bad:
            flags.append((band, sc, aa, best))
        print(f"{band:5s} {sc:8s} {aa:10d} {ff:11d} {mix:13d} "
              f"{np.isfinite(f_on).mean():8.3f} {np.isfinite(f_off).mean():9.3f} {miss:13d}"
              f"  {'**G7 DEFECT**' if bad else ('main-fused' if sc in MAIN_FUSED else 'ok')}")
print(f"\nG7 defect pairs found by scan: {len(flags)} -> {[(b, s) for b, s, _, _ in flags]}")
