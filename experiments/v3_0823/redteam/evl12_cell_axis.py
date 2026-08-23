#!/usr/bin/env python3
"""EVL-12 residual: FA-matched comparison on the CELL axis (cell_fpr_off)
alongside the published FRAME axis (frame_fa_off).  CPU, read-only."""
import csv, json, os, sys
import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
NEW = os.path.join(ROOT, "experiments/v3_0823/eval_v2corr")          # corrected GT (canonical)
OLD = os.path.join(ROOT, "experiments/dayrun_0820/runs/v2")          # old GT (published)
MODELS = ["rgb", "depth", "b2"]
SEEDS = [42, 43, 44]
FRAME_TARGETS = [0.359, 0.200, 0.100, 0.050]


def load_run(base, model, seed, corrected):
    d = os.path.join(base, f"{model}_s{seed}") if corrected else \
        os.path.join(base, f"{model}_s{seed}", "eval_test")
    rows = {}
    for tag in ("on", "off"):
        with open(os.path.join(d, f"per_frame_{tag}.csv")) as f:
            rows[tag] = list(csv.DictReader(f))
    cells = [c[2:] for c in rows["on"][0] if c.startswith("p_")]
    out = {}
    for tag in ("on", "off"):
        R = rows[tag]
        out[tag] = dict(
            frame_id=[r["frame_id"] for r in R],
            tier=np.array([r["tier"] for r in R]),
            prob=np.array([[float(r["p_" + c]) for c in cells] for r in R]),
            gt=np.array([[float(r["g_" + c]) for c in cells] for r in R]) > 0.5,
        )
    out["cells"] = cells
    return out


def tau_for_rate(vals, target):
    """Largest achievable rate <= target, using empirical order statistics.
    Fire rule is `x >= tau` (same as eval_polar/bundle and f1_fa_matched)."""
    s = np.sort(np.asarray(vals).ravel())[::-1]
    n = s.size
    k = int(np.floor(target * n))
    if k <= 0:
        return float(np.nextafter(s[0], np.inf))
    if k >= n:
        return float(np.nextafter(s[-1], -np.inf))
    return float(np.nextafter(s[k], np.inf))


def measure(run, tau):
    on, off = run["on"], run["off"]
    pon, gon = on["prob"] >= tau, on["gt"]
    poff = off["prob"] >= tau
    haz = gon.any(1)
    m = {}
    m["frame_fa_off"] = float(poff.any(1).mean())
    m["cell_fpr_off"] = float(poff.mean())            # off arm GT is all-zero (verified)
    fired = poff.any(1)
    m["cells_per_fa_frame"] = float(poff[fired].sum() / max(fired.sum(), 1))
    for t in ("V", "E", "H"):
        s = haz & (on["tier"] == t)
        det = (pon & gon).any(1)
        m[f"frame_recall_{t}"] = float(det[s].mean()) if s.sum() else float("nan")
        m[f"cell_recall_{t}"] = float((pon[s] & gon[s]).sum() / max(gon[s].sum(), 1))
    return m


def sweep(base, corrected, cell_targets=None):
    runs = {(m, s): load_run(base, m, s, corrected) for m in MODELS for s in SEEDS}
    # sanity
    r0 = runs[("rgb", 42)]
    assert r0["off"]["gt"].sum() == 0, "off arm GT not all-zero"
    out = {"frame": {}, "cell": {}, "published": {}, "n": {}}
    out["n"] = dict(n_on=len(r0["on"]["frame_id"]), n_off=len(r0["off"]["frame_id"]),
                    n_cells=len(r0["cells"]),
                    tier=dict(zip(*[list(x) for x in np.unique(r0["on"]["tier"], return_counts=True)])))
    out["n"]["tier"] = {k: int(v) for k, v in out["n"]["tier"].items()}

    # published tau=0.5 point
    for m in MODELS:
        vals = [measure(runs[(m, s)], 0.5) for s in SEEDS]
        out["published"][m] = {k: [v[k] for v in vals] for k in vals[0]}

    # ---- frame axis ----
    for tgt in FRAME_TARGETS:
        out["frame"][tgt] = {}
        for m in MODELS:
            per = []
            for s in SEEDS:
                r = runs[(m, s)]
                tau = tau_for_rate(r["off"]["prob"].max(1), tgt)
                mm = measure(r, tau); mm["tau"] = tau
                per.append(mm)
            out["frame"][tgt][m] = per

    # ---- cell axis ----
    if cell_targets is None:
        # anchor = RGB published cell_fpr_off at tau=0.5, scaled by the frame-axis schedule
        anchor = float(np.mean(out["published"]["rgb"]["cell_fpr_off"]))
        cell_targets = [round(anchor * (t / FRAME_TARGETS[0]), 6) for t in FRAME_TARGETS]
    out["cell_targets"] = cell_targets
    for tgt in cell_targets:
        out["cell"][tgt] = {}
        for m in MODELS:
            per = []
            for s in SEEDS:
                r = runs[(m, s)]
                tau = tau_for_rate(r["off"]["prob"], tgt)
                mm = measure(r, tau); mm["tau"] = tau
                per.append(mm)
            out["cell"][tgt][m] = per
    return out


def agg(per, key):
    v = np.array([p[key] for p in per], float)
    return float(np.nanmean(v)), float((np.nanmax(v) - np.nanmin(v)) / 2)


if __name__ == "__main__":
    res = {}
    res["new"] = sweep(NEW, True)
    # old GT: reuse the SAME cell targets so the two GTs are compared on one axis
    res["old"] = sweep(OLD, False, cell_targets=res["new"]["cell_targets"])
    json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else "evl12.json", "w"), indent=1)

    for gt in ("new", "old"):
        R = res[gt]
        print("=" * 78)
        print(f"### GT = {'CORRECTED (v2corr)' if gt=='new' else 'OLD (published)'}   {R['n']}")
        print("-- published tau=0.5 --")
        for m in MODELS:
            p = R["published"][m]
            print("  %-6s frame_fa %.4f  cell_fpr %.4f  cells/FAframe %.2f  frameH %.3f  cellH %.3f" % (
                m, np.mean(p["frame_fa_off"]), np.mean(p["cell_fpr_off"]),
                np.mean(p["cells_per_fa_frame"]), np.mean(p["frame_recall_H"]),
                np.mean(p["cell_recall_H"])))
        print("-- FRAME axis (match frame_fa_off) --")
        for tgt in FRAME_TARGETS:
            row = []
            for m in MODELS:
                mu, hr = agg(R["frame"][tgt][m], "frame_recall_H")
                fa, _ = agg(R["frame"][tgt][m], "frame_fa_off")
                cf, _ = agg(R["frame"][tgt][m], "cell_fpr_off")
                row.append("%s H %.3f±%.3f (FA %.3f, cellFPR %.4f)" % (m, mu, hr, fa, cf))
            print("  tgt %.3f | %s" % (tgt, " | ".join(row)))
        print("-- CELL axis (match cell_fpr_off) --")
        for tgt in R["cell_targets"]:
            row = []
            for m in MODELS:
                mu, hr = agg(R["cell"][tgt][m], "cell_recall_H")
                cf, _ = agg(R["cell"][tgt][m], "cell_fpr_off")
                ff, _ = agg(R["cell"][tgt][m], "frame_fa_off")
                row.append("%s cH %.3f±%.3f (cellFPR %.4f, frameFA %.3f)" % (m, mu, hr, cf, ff))
            print("  tgt %.4f | %s" % (tgt, " | ".join(row)))
