"""Percentile bootstrap, written from scratch (no scipy).

The load-bearing detail for the paired case: ONE resample index per iteration, applied to BOTH
arms, so the pairing survives (resampling each arm independently is an unpaired test and gives
CIs that are too wide). See HARNESS_NOTES §7 -- no bootstrap code existed to copy.
"""
from __future__ import annotations

import numpy as np

N_BOOT = 10000
SEED = 42


def _pct(vals, alpha):
    v = np.asarray(vals, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return (float("nan"), float("nan"))
    return (float(np.percentile(v, 100 * alpha / 2)), float(np.percentile(v, 100 * (1 - alpha / 2))))


def bootstrap_ci(stat_fn, n, n_boot=N_BOOT, seed=SEED, alpha=0.05):
    """stat_fn(idx: np.ndarray[int]) -> dict[str, float]. Resamples n frames with replacement.

    Returns {key: {"point","lo","hi","n_boot","n_valid"}}.
    """
    rng = np.random.default_rng(seed)
    point = stat_fn(np.arange(n))
    draws = {k: [] for k in point}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        s = stat_fn(idx)
        for k in draws:
            draws[k].append(s.get(k, float("nan")))
    out = {}
    for k, v in draws.items():
        lo, hi = _pct(v, alpha)
        out[k] = dict(point=float(point[k]), lo=lo, hi=hi, n_boot=n_boot,
                      n_valid=int(np.isfinite(np.asarray(v, float)).sum()))
    return out


def paired_diff_ci(stat_a, stat_b, n, n_boot=N_BOOT, seed=SEED, alpha=0.05):
    """CI for stat_a - stat_b over the SAME n paired frames, sharing the resample index."""
    rng = np.random.default_rng(seed)
    pa, pb = stat_a(np.arange(n)), stat_b(np.arange(n))
    keys = [k for k in pa if k in pb]
    draws = {k: [] for k in keys}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        a, b = stat_a(idx), stat_b(idx)
        for k in keys:
            draws[k].append(a.get(k, float("nan")) - b.get(k, float("nan")))
    out = {}
    for k in keys:
        lo, hi = _pct(draws[k], alpha)
        d = float(pa[k]) - float(pb[k])
        out[k] = dict(a=float(pa[k]), b=float(pb[k]), diff=d, lo=lo, hi=hi,
                      excludes_zero=bool(np.isfinite(lo) and np.isfinite(hi) and (lo > 0 or hi < 0)),
                      n_boot=n_boot)
    return out


if __name__ == "__main__":  # sanity: CI of a mean should bracket the truth
    rng = np.random.default_rng(0)
    x = rng.normal(0.6, 0.1, 500)
    r = bootstrap_ci(lambda i: {"mean": float(x[i].mean())}, len(x), n_boot=2000)["mean"]
    print(r, "ok" if r["lo"] < 0.6 < r["hi"] else "FAIL")
