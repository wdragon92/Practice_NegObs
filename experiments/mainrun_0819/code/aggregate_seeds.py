"""Aggregate the 3-seed recipe-v2 runs into one mean±range markdown table.

Layout it expects (what run_queue_v2.sh writes):

    <root>/<model>_s<seed>/config.json          training record (best epoch, sel score, grid)
    <root>/<model>_s<seed>/eval_test/metrics.json
    <root>/<model>_s<seed>/twin/twin_pairs.csv  (optional -> twin delta columns)

"mean ± range" = mean over the seeds ± half the (max−min) spread, with the raw per-seed values
kept in an appendix table. The spread across 3 seeds is a range, NOT a confidence interval —
the per-run bootstrap CIs in each METRICS_SECTION.md are the statistical uncertainty.

  python aggregate_seeds.py --root ../runs/v2 --models rgb,depth,b2 --seeds 42,43,44 \
      --out ../runs/v2/SEED_TABLE.md
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gridspec  # noqa: E402

BASE_KEYS = ["frame_recall_H", "frame_recall_E", "frame_recall_V", "frame_det_rate",
             "frame_fa_off", "cell_fpr_off", "cell_f1", "cell_recall", "cell_precision"]


def band_keys(grid):
    return ([f"band{b + 1}_cell_recall" for b in range(grid.n_bands)]
            + [f"band{b + 1}_cell_fpr_off" for b in range(grid.n_bands)])


def _mean(v):
    v = [x for x in v if x is not None and math.isfinite(x)]
    return sum(v) / len(v) if v else float("nan")


def _fmt_mr(vals, nd=3):
    """mean ± half-range over the seeds; 'n/a' if nothing finite."""
    v = [x for x in vals if x is not None and math.isfinite(x)]
    if not v:
        return "n/a"
    m = sum(v) / len(v)
    if len(v) == 1:
        return f"{m:.{nd}f}"
    return f"{m:.{nd}f} ± {(max(v) - min(v)) / 2:.{nd}f}"


def twin_deltas(path):
    """(mean delta_score over kept pairs, mean over kept H pairs) from twin_pairs.csv."""
    if not os.path.exists(path):
        return float("nan"), float("nan")
    allv, hv = [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            if str(r.get("kept")).lower() not in ("true", "1"):
                continue
            try:
                d = float(r["delta_score"])
            except (KeyError, TypeError, ValueError):
                continue
            if not math.isfinite(d):
                continue
            allv.append(d)
            if r.get("tier") == "H":
                hv.append(d)
    return _mean(allv), _mean(hv)


def collect(root, model, seed, evaldir, twindir):
    run = os.path.join(root, f"{model}_s{seed}")
    mj = os.path.join(run, evaldir, "metrics.json")
    rec = dict(model=model, seed=seed, run=run, ok=os.path.exists(mj))
    if not rec["ok"]:
        return rec
    with open(mj) as f:
        M = json.load(f)
    rec["point"] = M["point"]["op"]
    rec["tau_star"] = M.get("tau_star")
    rec["point_star"] = M["point"].get("star", {})
    rec["counts"] = M.get("counts", {})
    rec["grid"] = M.get("grid", {})
    cfg = os.path.join(run, "config.json")
    if os.path.exists(cfg):
        with open(cfg) as f:
            c = json.load(f)
        rec["cfg"] = {k: c.get(k) for k in ("best_epoch", "best_sel_score", "best_val_f1",
                                            "best_val_h_recall", "stop_reason", "lr", "n_cells",
                                            "grid_version", "hflip", "oversample_h", "bias_init",
                                            "selection_fallback_to_f1")}
    rec["twin_all"], rec["twin_H"] = twin_deltas(os.path.join(run, twindir, "twin_pairs.csv"))
    return rec


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, help="dir holding <model>_s<seed> run dirs")
    p.add_argument("--models", default="rgb,depth,b2")
    p.add_argument("--seeds", default="42,43,44")
    p.add_argument("--eval-subdir", default="eval_test")
    p.add_argument("--twin-subdir", default="twin")
    p.add_argument("--out", required=True)
    p.add_argument("--title", default="Recipe v2 — 3-seed summary")
    gridspec.add_grid_arg(p)
    a = p.parse_args(argv)
    grid = gridspec.from_args(a)
    models = [m for m in a.models.split(",") if m]
    seeds = [int(s) for s in a.seeds.split(",") if s]
    keys = BASE_KEYS + band_keys(grid)

    R = {m: [collect(a.root, m, s, a.eval_subdir, a.twin_subdir) for s in seeds] for m in models}
    missing = [f"{r['model']}_s{r['seed']}" for m in models for r in R[m] if not r["ok"]]

    L = [f"# {a.title}", "",
         f"root `{a.root}` · models {models} · seeds {seeds} · grid **{grid.version}** "
         f"({grid.n_cells} cells)",
         "", "`mean ± range/2` over seeds. The spread is seed variability, **not** a confidence "
         "interval — per-run bootstrap CIs live in each run's `METRICS_SECTION.md`.", ""]
    if missing:
        L += [f"> **MISSING runs (not aggregated): {', '.join(missing)}**", ""]

    L += ["## 1. Headline table (tau_op = 0.5)", "",
          "| model | n seeds | " + " | ".join(keys) + " |", "|" + "---|" * (len(keys) + 2)]
    for m in models:
        got = [r for r in R[m] if r["ok"]]
        L.append(f"| {m} | {len(got)} | "
                 + " | ".join(_fmt_mr([r["point"].get(k) for r in got]) for k in keys) + " |")
    L += ["", "## 2. Twin on−off delta (kept pose-matched pairs) + tau*", "",
          "| model | n seeds | twin delta (all) | twin delta (H tier) | tau* | best epoch |",
          "|---|---|---|---|---|---|"]
    for m in models:
        got = [r for r in R[m] if r["ok"]]
        L.append(f"| {m} | {len(got)} | {_fmt_mr([r['twin_all'] for r in got])} | "
                 f"{_fmt_mr([r['twin_H'] for r in got])} | "
                 f"{_fmt_mr([r.get('tau_star') for r in got], 2)} | "
                 f"{_fmt_mr([(r.get('cfg') or {}).get('best_epoch') for r in got], 1)} |")

    L += ["", "## 3. Per-seed detail", "",
          "| model | seed | " + " | ".join(BASE_KEYS)
          + " | twin all | twin H | tau* | best ep | sel | stop |",
          "|" + "---|" * (len(BASE_KEYS) + 8)]
    for m in models:
        for r in R[m]:
            if not r["ok"]:
                L.append(f"| {m} | {r['seed']} | "
                         + " | ".join(["MISSING"] * (len(BASE_KEYS) + 6)) + " |")
                continue
            c = r.get("cfg") or {}
            L.append(f"| {m} | {r['seed']} | "
                     + " | ".join(_fmt_mr([r["point"].get(k)]) for k in BASE_KEYS)
                     + f" | {_fmt_mr([r['twin_all']])} | {_fmt_mr([r['twin_H']])} "
                     f"| {r.get('tau_star')} | {c.get('best_epoch')} "
                     f"| {_fmt_mr([c.get('best_sel_score')])} | {c.get('stop_reason')} |")

    fb = [f"{m}_s{r['seed']}" for m in models for r in R[m]
          if r["ok"] and (r.get("cfg") or {}).get("selection_fallback_to_f1")]
    if fb:
        L += ["", f"> **Selection fell back to val cell-F1 (val had no H frame) in: "
                  f"{', '.join(fb)}** — those checkpoints were chosen blind to H recall.", ""]
    L.append("")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        f.write("\n".join(L))
    print(f"[aggregate] {sum(len([r for r in R[m] if r['ok']]) for m in models)}/"
          f"{len(models) * len(seeds)} runs -> {a.out}"
          + (f"  MISSING: {missing}" if missing else ""))
    return 0 if not missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
