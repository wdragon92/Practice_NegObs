"""Twin on/off analysis -- does the SAME camera pose lose its hazard score once the hazard is gone?

Pairs the two arms' per_frame.csv rows by (scene_id, cut file), keeps only pairs whose manifest
camera pose is identical, and reports the on-minus-off drop in predicted hazard probability.
Same pose + same scene + hazard removed => the drop is context-causality evidence, not a pose effect.

    delta_score   = max(p over the ON frame's GT-positive cells)_on - max(p over the SAME cells)_off
    delta_frame   = max(p over ALL cells)_on - max(p over ALL cells)_off
    delta band b  = same as delta_score but restricted to the GT-positive cells of band b
                    (v2: the bands come from --grid, so 3 rows on V0 and 4 on V1)

Reported per evidence tier (V/E/H/all), per band, and per band x H-tier, each with a paired
percentile-bootstrap CI over pairs (one shared resample index, bootstrap.py).

POSE FILTER: `ground_z` is in the default key set on purpose -- it is the only cam field that ever
differs between the arms (183/792 pairs here; D15/D17: the toggle moved the camera's own ground
plane, so absolute height ground_z+h_rel differs while d/h_rel/yaw/pitch match). Pass
`--pose-keys d,h_rel,yaw,pitch` for the brief's four-key filter, which excludes nothing.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bootstrap as BS  # noqa: E402
import gridspec  # noqa: E402
from eval_polar import read_per_frame  # noqa: E402  (same CSV contract as the writer)

POSE_KEYS, TIERS = "d,h_rel,yaw,pitch,ground_z", ("V", "E", "H")
BASE_FIELDS = ["scene_id", "cut", "tier", "kept", "mismatch", "n_gt_pos", "max_on_gt", "max_off_gt",
               "delta_score", "max_on_all", "max_off_all", "delta_frame"]
NAN = float("nan")


def by_cut(d, arm):
    """{(scene_id, cut file) -> row index} over one arm's rows; frame_id = '<arm>/<scene>/<file>'."""
    return {tuple(f.split("/", 2)[1:]): i for i, f in enumerate(d["frame_id"])
            if f.split("/", 2)[0] == arm}


def build_pairs(don, doff, manifest, keys, tol, grid):
    with open(manifest) as fh:
        cams = {tuple(r["frame_id"].split("/", 2)): r["cam"] for r in json.load(fh)["frames"]}
    band_of = np.asarray(grid.band_of)
    ion, ioff = by_cut(don, "on"), by_cut(doff, "off")
    rows = []
    for k in sorted(set(ion) & set(ioff)):
        a, b = cams.get(("on",) + k), cams.get(("off",) + k)
        bad = (["not-in-manifest"] if a is None or b is None else
               [q for q in keys if abs(float(a[q]) - float(b[q])) > tol])
        pos = don["gt"][ion[k]] > 0.5
        p_on, p_off = don["probs"][ion[k]], doff["probs"][ioff[k]]
        r = dict(scene_id=k[0], cut=k[1], tier=str(don["tier"][ion[k]]), kept=(not bad),
                 mismatch="|".join(bad), n_gt_pos=int(pos.sum()),
                 max_on_gt=float(p_on[pos].max()) if pos.any() else NAN,
                 max_off_gt=float(p_off[pos].max()) if pos.any() else NAN,
                 max_on_all=float(p_on.max()), max_off_all=float(p_off.max()))
        for bi in range(grid.n_bands):
            m = pos & (band_of == bi)
            r[f"max_on_b{bi + 1}"] = float(p_on[m].max()) if m.any() else NAN
            r[f"max_off_b{bi + 1}"] = float(p_off[m].max()) if m.any() else NAN
            r[f"delta_b{bi + 1}"] = r[f"max_on_b{bi + 1}"] - r[f"max_off_b{bi + 1}"]
        rows.append(dict(r, delta_score=r["max_on_gt"] - r["max_off_gt"],
                         delta_frame=r["max_on_all"] - r["max_off_all"]))
    return rows


def _mean(v):
    v = np.asarray(v, float)
    return float(np.nanmean(v)) if v.size and np.isfinite(v).any() else NAN


def delta_ci(kept, grid, n_boot, seed):
    """Paired percentile bootstrap over PAIRS -- one shared resample index (bootstrap.py).

    Keys: score_<tier|all>, frame_<tier|all>, band<i>_all, band<i>_H."""
    if not kept:
        return {}
    tier = np.array([r["tier"] for r in kept])
    nb = grid.n_bands
    on_cols = ["max_on_gt", "max_on_all"] + [f"max_on_b{b + 1}" for b in range(nb)]
    off_cols = ["max_off_gt", "max_off_all"] + [f"max_off_b{b + 1}" for b in range(nb)]

    def stat(names):
        M = np.array([[r[n] for n in names] for r in kept], float)

        def f(idx):
            t, m = tier[idx], M[idx]
            out = {f"{lbl}_{g}": _mean(m[:, c] if g == "all" else m[t == g, c])
                   for lbl, c in (("score", 0), ("frame", 1)) for g in TIERS + ("all",)}
            for b in range(nb):
                out[f"band{b + 1}_all"] = _mean(m[:, 2 + b])
                out[f"band{b + 1}_H"] = _mean(m[t == "H", 2 + b])
            return out
        return f
    return BS.paired_diff_ci(stat(on_cols), stat(off_cols), len(kept), n_boot, seed)


def _f(v, nd=4):
    return "n/a" if v is None or not np.isfinite(v) else f"{v:.{nd}f}"


def _ci(ci, k):
    c = ci.get(k)
    if not c:
        return "n/a"
    star = " *" if c.get("excludes_zero") else ""
    return f"{_f(c['diff'])} [{_f(c['lo'])}, {_f(c['hi'])}]{star}"


def write_md(path, rows, ci, a, grid):
    kept = [r for r in rows if r["kept"]]
    gt = [r for r in kept if r["n_gt_pos"] > 0]
    L = ["# TWIN_ANALYSIS — on/off paired context-causality", "",
         f"on: `{a.per_frame_on}` · off: `{a.per_frame_off}` · manifest: `{a.manifest}`",
         f"grid: **{grid.version}** ({grid.n_bands} bands x {grid.n_sectors} sectors)",
         f"pose keys: `{a.pose_keys}` · tol {a.tol:g} · paired bootstrap {a.n_boot}x seed {a.seed}",
         "", f"pairs found **{len(rows)}** · pose-matched (kept) **{len(kept)}** · excluded "
         f"**{len(rows) - len(kept)}** · kept pairs carrying >=1 GT cell **{len(gt)}** "
         f"(delta_score > 0 in {sum(r['delta_score'] > 0 for r in gt)}/{len(gt)})", "",
         "`*` marks a CI excluding 0.", "",
         "## 1. Mean delta by tier (paired bootstrap 95% CI)", "",
         "| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |",
         "|---|---|---|---|"]
    L += [f"| {t} | {len(kept) if t == 'all' else sum(r['tier'] == t for r in kept)} | "
          f"{_ci(ci, f'score_{t}')} | {_ci(ci, f'frame_{t}')} |" for t in TIERS + ("all",)]
    L += ["", "> delta_score is n/a where no kept pair of that tier has a GT-positive cell; "
          "`all` covers every kept pair, including tiers off/H_weak/none_in_fov.", "",
          "## 2. Mean delta by distance band (GT-positive cells of that band only)", "",
          "| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |",
          "|---|---|---|---|---|"]
    for b in range(grid.n_bands):
        col, hcol = f"max_on_b{b + 1}", "tier"
        n_any = sum(1 for r in kept if np.isfinite(r[col]))
        n_h = sum(1 for r in kept if np.isfinite(r[col]) and r[hcol] == "H")
        lo, hi = grid.band_range(b)
        L.append(f"| {grid.band_names[b]} [{lo:g},{hi:g}) m | {n_any} | "
                 f"{_ci(ci, f'band{b + 1}_all')} | {n_h} | {_ci(ci, f'band{b + 1}_H')} |")
    L += ["", "> A band row answers 'is the model's firing in this band caused by the drop, or "
          "is it a distance prior?' — a near-zero delta with a high recall in the same band is "
          "the prior signature.", "",
          "## 3. Per-scene pairs and mean delta", "",
          "| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |",
          "|---|---|---|---|---|---|"]
    for s in sorted({r["scene_id"] for r in rows}):
        g = [r for r in rows if r["scene_id"] == s]
        k = [r for r in g if r["kept"]]
        L.append(f"| {s} | {len(k)} | {len(g) - len(k)} | {len(k) / len(g):.2f} | "
                 f"{_f(_mean([r['delta_score'] for r in k]))} | {_f(_mean([r['delta_frame'] for r in k]))} |")
    L += ["", f"per-pair rows: `{os.path.join(a.out, 'twin_pairs.csv')}` "
          "(`kept`/`mismatch` carry the pose-filter verdict).", ""]
    with open(path, "w") as fh:
        fh.write("\n".join(L))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--per-frame-on", required=True, help="eval_polar per_frame.csv, on-arm rows")
    p.add_argument("--per-frame-off", required=True, help="same checkpoint, off-arm rows")
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pose-keys", default=POSE_KEYS)
    p.add_argument("--tol", type=float, default=1e-6)
    p.add_argument("--n-boot", type=int, default=BS.N_BOOT)
    p.add_argument("--seed", type=int, default=BS.SEED)
    gridspec.add_grid_arg(p)
    a = p.parse_args(argv)
    grid = gridspec.from_args(a)
    os.makedirs(a.out, exist_ok=True)

    rows = build_pairs(read_per_frame(a.per_frame_on, grid), read_per_frame(a.per_frame_off, grid),
                       a.manifest, a.pose_keys.split(","), a.tol, grid)
    if not rows:
        sys.exit("[twin] no (scene, cut) pair shared by the two CSVs -- wrong arms?")
    kept = [r for r in rows if r["kept"]]
    ci = delta_ci(kept, grid, a.n_boot, a.seed)
    fields = BASE_FIELDS + [f"{k}{b + 1}" for b in range(grid.n_bands)
                            for k in ("max_on_b", "max_off_b", "delta_b")]
    with open(os.path.join(a.out, "twin_pairs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        w.writerows(rows)
    write_md(os.path.join(a.out, "twin_analysis.md"), rows, ci, a, grid)
    d, h = ci.get("score_all", {}), ci.get("score_H", {})
    print(f"[twin] pairs={len(rows)} kept={len(kept)} excluded={len(rows) - len(kept)} "
          f"bands={grid.n_bands} | mean delta_score={_f(d.get('diff'))} "
          f"[{_f(d.get('lo'))}, {_f(d.get('hi'))}] | H-tier delta={_f(h.get('diff'))} "
          f"[{_f(h.get('lo'))}, {_f(h.get('hi'))}] -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
