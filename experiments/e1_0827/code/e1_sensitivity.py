# -*- coding: utf-8 -*-
"""e1_sensitivity.py -- run the SAME frames under the alternative values of one
ledgered constant and print how the counts move.

This is the "2-3 값 민감도" half of P1 made executable: the ledger says which
alternatives to try, this prints what they do. It never changes a stored label
-- it re-runs route (a) in memory and reports counts, so a sweep can be produced
at any time without touching annotations/.

    python3 e1_sensitivity.py --key R_RUN_M --list smoke_frames.txt
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e1_camera as CAM       # noqa: E402
import e1_const as C          # noqa: E402
import e1_data as D           # noqa: E402
import e1_geometry as G       # noqa: E402


def _reload_named():
    """Re-derive the module-level convenience names after CONSTANTS changed."""
    for k in list(C.CONSTANTS):
        if hasattr(C, k):
            setattr(C, k, C.value(k))


def sweep(key, specs):
    base = C.CONSTANTS[key]
    alts = base[3] or (base[0],)
    rows = []
    for val in alts:
        C.CONSTANTS[key] = (val, base[1], base[2], base[3])
        _reload_named()
        for rnd, scene, frame in specs:
            sdir = D.scene_dir(rnd, scene)
            cut = D.find_cut(sdir, frame)
            hm = CAM.HeightMap.load(sdir)
            cam = CAM.CameraModel(cut["cam"])
            mask, drop, dg = G.edge_cells(hm, (cam.eye[0], cam.eye[1]),
                                          cut["cam"].get("ground_z"))
            inst, dg2 = G.instances(hm, mask)
            lens = [len(p) * hm.step for p in inst]
            rows.append((val, scene, frame, dg["n_walkable"], dg["n_reachable"],
                         dg["n_drop_ge_thr"], dg["n_edge_cells"],
                         dg2["n_components"], dg2["n_kept"],
                         round(float(np.sum(lens)), 2)))
    C.CONSTANTS[key] = base
    _reload_named()
    return rows


def sweep_full(key, specs, out_dir):
    """Whole-pipeline sweep: re-label the frames under each alternative value and
    report what actually reaches the record. Needed for the constants that live
    downstream of route (a) (VIS_TOL_M, B_*), where an edge-cell count says
    nothing."""
    import e1_label_frame as LF
    import e1_visibility as V
    base = C.CONSTANTS[key]
    alts = base[3] or (base[0],)
    rows = []
    for val in alts:
        C.CONSTANTS[key] = (val, base[1], base[2], base[3])
        _reload_named()
        for rnd, scene, frame in specs:
            rec, _ = LF.label_frame(rnd, scene, frame, out_dir,
                                    classifier=V.PrimClassifier.load())
            devs = [e.src_disagree_px.median for e in rec.edges
                    if e.src_disagree_px.median is not None]
            rows.append((val, scene, rec.tier_now, len(rec.edges),
                         sum(e.int_area_px for e in rec.edges),
                         sum(1 for e in rec.edges if e.occluder.flag is None),
                         round(float(np.median(devs)), 3) if devs else None,
                         len(devs)))
    C.CONSTANTS[key] = base
    _reload_named()
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--list", required=True)
    ap.add_argument("--full", action="store_true",
                    help="re-label each frame instead of counting edge cells")
    ap.add_argument("--tmp", default=None, help="scratch dir for --full masks")
    a = ap.parse_args(argv)
    specs = []
    with open(a.list, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#")[0].strip()
            if line:
                specs.append(tuple(line.split(":")))
    if a.full:
        import tempfile
        td = a.tmp or tempfile.mkdtemp(prefix="e1_sens_")
        rows = sweep_full(a.key, specs, td)
        print("%-10s %-9s %-8s %6s %10s %10s %10s %6s"
              % (a.key, "scene", "tier_now", "edges", "int_px", "unresolved",
                 "dev_med", "n_dev"))
        for r in rows:
            print("%-10s %-9s %-8s %6d %10d %10d %10s %6d"
                  % (r[0], r[1], r[2], r[3], r[4], r[5],
                     "-" if r[6] is None else r[6], r[7]))
        return 0
    rows = sweep(a.key, specs)
    print("%-10s %-9s %-28s %9s %9s %9s %9s %6s %5s %9s"
          % (a.key, "scene", "frame", "walkable", "reachable", "drop>=thr",
             "edgecells", "comps", "kept", "len_m"))
    for r in rows:
        print("%-10s %-9s %-28s %9d %9d %9d %9d %6d %5d %9.2f"
              % (r[0], r[1], r[2][:C.SENS_FRAME_COL], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
