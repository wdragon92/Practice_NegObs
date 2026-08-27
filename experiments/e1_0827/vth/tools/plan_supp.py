#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plan_supp.py -- fill the one size band the main plan lost.

In eworld2 the M2 candidate nearest the warehouse centre (H45) turned out to sit beside
aws_robomaker_warehouse_ShelfF_01_001: every approach pose had the shelf on the sight
line, so the band produced 0 usable frames (65 poses logged as sightline_blocked_by).
This supplement re-picks that band with two extra rules -- the opening itself must not
lie inside a blocker footprint, and the candidate must actually yield poses -- and emits
`plan_supp.json` for a separate set of world copies (eworld2_s00...).
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vth_plan as V

HERE = V.HERE


def main():
    band = sys.argv[1] if len(sys.argv) > 1 else "M2"
    world = sys.argv[2] if len(sys.argv) > 2 else "eworld2"
    hl = json.load(open(os.path.join(HERE, "holes_local.json")))
    grid = np.load(os.path.join(HERE, "holes_local_grid.npz"))["grid"]
    sc = V.Scene(world, hl["holes"], grid, hl["raster_origin"], hl["raster_m"],
                 hl["plate_top_z_local"])
    lo, hi = next((l, h) for lab, l, h in V.SIZE_BANDS if lab == band)
    taken = {t["hole_id"] for t in
             json.load(open(os.path.join(HERE, "holes.json")))["worlds"][world]["targets"]}
    cands = [h for h in sc.holes if lo <= h["area_m2"] <= hi and h["hole_id"] not in taken]
    cands.sort(key=lambda h: math.hypot(*h["centre"]))
    for h in cands:
        # NEW rule 1: the opening must not be inside a blocker footprint
        c = h["centre"]
        if any(b["world_aabb"][0] - 0.3 <= c[0] <= b["world_aabb"][2] + 0.3
               and b["world_aabb"][1] - 0.3 <= c[1] <= b["world_aabb"][3] + 0.3
               for b in sc.blockers):
            continue
        scored = sorted(((V.dir_score(sc, h, dv), dn) for dn, dv in V.DIRS.items()),
                        reverse=True)
        dirs = [dn for s_, dn in scored if s_ >= len(V.STANDOFFS) - 1]
        if not dirs:
            continue
        t = dict(h); t["band"] = band; t["dirs"] = dirs[:1]
        kept, skipped = V.build_poses(sc, [t])
        # NEW rule 2: the candidate has to actually produce frames
        if len(kept) < 40:
            continue
        json.dump(kept, open(os.path.join(HERE, "plan_supp.json"), "w"),
                  indent=1, sort_keys=True)
        print(f"{world} {band}: {h['hole_id']} area {h['area_m2']:.3f} m^2 "
              f"({h['w_m']:.2f} x {h['h_m']:.2f}) at ({c[0]:.2f},{c[1]:.2f}) "
              f"dir {t['dirs'][0]} -> {len(kept)} poses, {len(skipped)} skipped")
        return 0
    print(f"no usable {band} candidate in {world}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
