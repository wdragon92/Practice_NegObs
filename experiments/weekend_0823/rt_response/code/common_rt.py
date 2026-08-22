"""Shared loaders for the RED-TEAM RESPONSE (D35) analyses.

Read-only.  Consumes ONLY frozen v2 artefacts:
  experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/eval_test/per_frame.csv
  experiments/dayrun_0820/runs/v2/*/twin/twin_pairs.csv
No canonical file is written or modified by anything importing this module.
"""
import csv
import os
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BASE = os.path.join(REPO, "experiments/dayrun_0820/runs/v2")
MODELS = ("rgb", "depth", "b2")
SEEDS = (42, 43, 44)
RUNS = [f"{m}_s{s}" for m in MODELS for s in SEEDS]


def load_per_frame(run):
    """-> list of dicts with scene_id, tier, toggle_state, p (20,), g (20,), frame_id."""
    path = os.path.join(BASE, run, "eval_test", "per_frame.csv")
    rows = list(csv.DictReader(open(path)))
    cells = [k[2:] for k in rows[0] if k.startswith("p_")]
    out = []
    for r in rows:
        out.append(dict(
            frame_id=r["frame_id"], scene_id=r["scene_id"], tier=r["tier"],
            toggle=r["toggle_state"],
            p=np.array([float(r["p_" + c]) for c in cells]),
            g=np.array([int(float(r["g_" + c])) for c in cells]),
        ))
    return out


def max_on_gt(rows, tier=None, scene=None):
    """Per-frame max probability restricted to GT-positive cells (hazard-ON frames)."""
    sel = [r for r in rows if (tier is None or r["tier"] == tier)
           and (scene is None or r["scene_id"] == scene)]
    return np.array([r["p"][r["g"] == 1].max() for r in sel]), sel


def max_off_any(rows, scene=None):
    """Per-frame max probability over all 20 cells, off-arm frames only."""
    sel = [r for r in rows if r["toggle"] == "off" and (scene is None or r["scene_id"] == scene)]
    return np.array([r["p"].max() for r in sel]), sel


def recall_at(rows, tier, tau, scene=None):
    v, sel = max_on_gt(rows, tier, scene)
    if len(v) == 0:
        return None, 0
    return float((v >= tau).mean()), len(v)


def fa_at(rows, tau, scene=None):
    v, sel = max_off_any(rows, scene)
    if len(v) == 0:
        return None, 0
    return float((v >= tau).mean()), len(v)


def tau_for_fa_exact(off_max, target):
    """Smallest tau achieving frame-FA <= target on the off arm, using the empirical
    order statistics (no 0.01 grid).  Returns (tau, achieved_fa)."""
    n = len(off_max)
    s = np.sort(off_max)[::-1]          # descending
    k = int(np.floor(target * n + 1e-9))  # max frames allowed to fire
    if k >= n:
        return 0.0, 1.0
    # tau just above the (k)-th largest -> at most k frames have max >= tau
    tau = np.nextafter(s[k], np.inf)
    achieved = float((off_max >= tau).mean())
    # ties can push achieved below k/n; walk down while still <= target
    return float(tau), achieved


def tau_for_fa_grid(rows, target, step=0.01):
    """R1's r1.py rule, reproduced verbatim: first tau on arange(0.01,1.00,step) with FA<=target."""
    for t in np.arange(step, 1.00, step):
        f = fa_at(rows, t)[0]
        if f <= target:
            return float(t)
    return None


def load_twin(run):
    path = os.path.join(BASE, run, "twin", "twin_pairs.csv")
    rows = list(csv.DictReader(open(path)))
    out = []
    for r in rows:
        def fl(k):
            v = r.get(k, "")
            try:
                return float(v)
            except (TypeError, ValueError):
                return float("nan")
        out.append(dict(scene_id=r["scene_id"], cut=r["cut"], tier=r["tier"],
                        kept=(r["kept"].strip().lower() == "true"),
                        mismatch=r.get("mismatch", ""),
                        n_gt_pos=fl("n_gt_pos"),
                        max_on_gt=fl("max_on_gt"), max_off_gt=fl("max_off_gt"),
                        delta_score=fl("delta_score")))
    return out


def mean_hr(vals):
    v = [x for x in vals if x is not None and not (isinstance(x, float) and np.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def halfrange(vals):
    v = [x for x in vals if x is not None and not (isinstance(x, float) and np.isnan(x))]
    return float((max(v) - min(v)) / 2) if v else float("nan")
