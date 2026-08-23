#!/usr/bin/env python3
"""
CPU-2 / FA CENSUS  --  step 4: dose-response check for the two *measurable*
families (조명형 / 대리선형), with the dominant confound held fixed.

The family counts in step 3 are shares of the FA set.  They cannot say whether a
family *causes* firing, because band (range) explains most of the variance and
band correlates with everything.  This script asks the counterfactual-shaped
question the census CAN answer from on-disk data:

    among cells that are equally at risk AND in the same distance band,
    does the FA rate rise with cell darkness / with cell line content?

If 조명형 and 대리선형 are real drivers, the rate must rise monotonically across
deciles WITHIN a band.  If they are only correlated with range, the within-band
curves go flat.  Output: experiments/v3_0823/logs/fa_dose_response.json
"""
import csv
import json
import os
import sys
from collections import defaultdict

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OUT = os.path.join(ROOT, "experiments/v3_0823")
CELLS = [c + b for b in ("1", "2", "3a", "3b") for c in "ABCDE"]
NRUN = 9


def main():
    # --corr: G7-corrected GT (정본 B).  Photometry is GT-independent and is
    # shared by both modes; only the at-risk universe and the events change.
    corr = "--corr" in sys.argv
    tag = "_v2corr" if corr else ""
    photo = {(r["frame_id"], r["cell"]): r
             for r in csv.DictReader(open(os.path.join(OUT, "cell_photometry.csv")))}
    pf = (os.path.join(OUT, "eval_v2corr/rgb_s42/per_frame.csv") if corr else
          os.path.join(ROOT, "experiments/dayrun_0820/runs/v2/rgb_s42/"
                             "eval_test/per_frame.csv"))
    rows = list(csv.DictReader(open(pf)))

    fa = defaultdict(int)
    for e in csv.DictReader(open(os.path.join(OUT, f"fa_events{tag}.csv"))):
        fa[(e["frame_id"], e["cell"])] += 1

    # at-risk universe: one record per (frame, cell) with 9 trials each
    uni = []
    for r in rows:
        strat = "OFF" if r["toggle_state"] == "off" else "ON_NEG"
        for c in CELLS:
            if strat == "ON_NEG" and int(r["g_" + c]) != 0:
                continue
            ph = photo.get((r["frame_id"], c), {})
            if not ph or int(ph["n_px"]) == 0:
                continue                      # cell not visible: no photometry
            fl = float(ph["frame_lum_median_all"]) if ph["frame_lum_median_all"] else 0.0
            if fl <= 0 or not ph["lum_median"] or not ph["line_frac"]:
                continue
            lr = float(ph["lum_median"]) / fl
            uni.append(dict(strat=strat, scene=r["scene_id"], band=c[1:],
                            lum_ratio=lr,
                            # |log| deviation from the frame's own median: the
                            # "optical change mass" reading -- either tail counts
                            lum_dev=abs(np.log(max(lr, 1e-6))),
                            lum_sd=float(ph["lum_std"]) if ph["lum_std"] else 0.0,
                            line_frac=float(ph["line_frac"]),
                            hits=fa.get((r["frame_id"], c), 0)))

    def curve(sel, var, nq=5, reverse=False):
        v = np.array([u[var] for u in sel])
        if len(v) < 50:
            return None
        qs = np.unique(np.quantile(v, np.linspace(0, 1, nq + 1)))
        if len(qs) < 3:
            return None
        idx = np.clip(np.searchsorted(qs, v, side="right") - 1, 0, len(qs) - 2)
        out = []
        for b in range(len(qs) - 1):
            m = idx == b
            n = int(m.sum())
            h = sum(u["hits"] for u, k in zip(sel, m) if k)
            out.append(dict(q=b + 1, lo=round(float(qs[b]), 4), hi=round(float(qs[b + 1]), 4),
                            n_cells=n, trials=n * NRUN, hits=h,
                            fa_rate=round(h / (n * NRUN), 5) if n else 0.0))
        if reverse:
            out = out[::-1]
        return out

    res = {"note": "fa_rate = FA events / (at-risk cells x 9 runs). "
                   "Deciles are quintiles of the variable within the listed slice.",
           "n_universe": len(uni)}
    for strat in ("OFF", "ON_NEG"):
        S = [u for u in uni if u["strat"] == strat]
        res[strat] = {}
        for var, rev in (("lum_ratio", True), ("lum_dev", False),
                         ("lum_sd", False), ("line_frac", False)):
            res[strat][var] = {"ALL": curve(S, var, reverse=rev)}
            for band in ("2", "3a", "3b"):
                res[strat][var][f"band{band}"] = curve(
                    [u for u in S if u["band"] == band], var, reverse=rev)
            for sc in ("scene15", "sceneN3", "scene05", "scene07"):
                res[strat][var][f"{sc}|band3b"] = curve(
                    [u for u in S if u["scene"] == sc and u["band"] == "3b"],
                    var, reverse=rev)

    # ------------------------------------------------------------------ #
    # Grid-locked vs content-locked test.
    #
    # A scene feature (a paint band, a joint, a railing) sits at a FIXED WORLD
    # position.  As the camera backs away, that feature's camera-range grows with
    # cam_d, so the band it occupies moves OUTWARD -- equivalently, if you plot
    # the fired band's midpoint against cam_d for a content-driven FA you get a
    # slope near +1 only if the feature is behind the camera origin; for a
    # feature at fixed distance AHEAD of the lip the fired band midpoint tracks
    # cam_d with slope ~ -1 as the viewpoint recedes past it.  Either way a
    # content-locked FA MOVES.  A range-prior FA does not: it stays at the same
    # camera-relative band no matter how far back the camera goes -> slope ~ 0.
    # ------------------------------------------------------------------ #
    MID = {"1": 1.0, "2": 3.5, "3a": 6.5, "3b": 10.0}
    raw = list(csv.DictReader(open(os.path.join(OUT, f"fa_events{tag}_raw.csv"))))
    lock = {}
    for sc in sorted({r["scene_id"] for r in raw}):
        S = [r for r in raw if r["scene_id"] == sc and r["stratum"] == "OFF"]
        if len(S) < 30:
            continue
        ds = sorted(float(r["cam_d"]) for r in S)
        q1, q2 = ds[len(ds) // 3], ds[2 * len(ds) // 3]
        grp = [[], [], []]
        for r in S:
            d = float(r["cam_d"])
            grp[0 if d <= q1 else (1 if d <= q2 else 2)].append(
                (d, MID[r["band"]]))
        cells = [dict(mean_cam_d=float(np.mean([x[0] for x in g])),
                      mean_band_mid=float(np.mean([x[1] for x in g])), n=len(g))
                 for g in grp if g]
        slope = ((cells[-1]["mean_band_mid"] - cells[0]["mean_band_mid"]) /
                 (cells[-1]["mean_cam_d"] - cells[0]["mean_cam_d"])) \
            if len(cells) > 1 and cells[-1]["mean_cam_d"] != cells[0]["mean_cam_d"] else None
        lock[sc] = dict(n=len(S), tertiles=cells, slope=slope)
    res["grid_locked_test"] = dict(
        note="OFF stratum. slope = d(mean fired band midpoint) / d(cam_d) across "
             "cam_d tertiles. ~0 => FA locked to the GRID (pure range prior); "
             "|slope| ~ 1 => FA tracks a fixed scene feature.",
        scenes=lock)

    json.dump(res, open(os.path.join(OUT, f"logs/fa_dose_response{tag}.json"), "w"), indent=2)

    print("===== GRID-LOCKED vs CONTENT-LOCKED (OFF) =====")
    for sc, v in lock.items():
        t = "  ".join(f"d{c['mean_cam_d']:5.2f}->band{c['mean_band_mid']:5.2f}"
                      for c in v["tertiles"])
        print(f"  {sc:9s} n={v['n']:4d}  {t}   slope={v['slope']:+.3f}")
    print()

    for strat in ("OFF", "ON_NEG"):
        print(f"===== {strat} =====")
        for var, lab in (("lum_ratio", "DARKEST->BRIGHTEST (조명형)"),
                         ("lum_dev", "LOW->HIGH |log| deviation from frame median"),
                         ("lum_sd", "LOW->HIGH within-cell luminance spread"),
                         ("line_frac", "LOWEST->HIGHEST line content (대리선형)")):
            print(f"  -- {var}  [{lab}]")
            for slc, cur in res[strat][var].items():
                if cur is None:
                    continue
                print(f"     {slc:18s} " + "  ".join(
                    f"Q{c['q']}:{c['fa_rate']:.4f}(n{c['n_cells']})" for c in cur))
    print(f"\n-> logs/fa_dose_response{tag}.json")


if __name__ == "__main__":
    main()
