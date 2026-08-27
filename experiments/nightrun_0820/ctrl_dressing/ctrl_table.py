#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ctrl_table.py — the side-by-side (병기) table: OLD off arm vs NEW dressing-preserving off arm.

Reads what `run_ctrl_eval.sh` produced and writes `CTRL_TABLE.md` + `ctrl_numbers.json`.
Nothing here re-runs a model; every number comes from a per_frame.csv or a twin_pairs.csv.

  per scene x arm x seed
    frames                 off-arm frames evaluated
    FA_frame               fraction of off frames with >= 1 cell at p >= tau (GT is all-zero on
                           every off frame by construction, so this is a pure false-alarm rate)
    cells/frame            mean number of fired cells
    mean max p             mean over off frames of max_cell p   (confidence, not just rate)
    twin d_frame           mean (max p over ALL cells)_on - (same)_off over pose-matched pairs
    twin d_score           same but restricted to the ON frame's GT-positive cells (n/a where the
                           ON arm carries no GT-positive cell -- sceneN3 is a hard negative)
    pairs                  kept / total

  QC
    on-arm reproduction    max |p_new - p_frozen| over the ON rows the two evals share. The new
                           round re-infers the SAME on-arm PNGs, so this must be ~1e-6; anything
                           larger means the two evals did not see the same frames.

usage: python3 ctrl_table.py --root <ctrl_dressing dir> [--tau 0.5] [--seeds 42,43,44]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics as st

SCENES = ("sceneC2", "sceneN3")


def read_per_frame(path):
    rows = []
    with open(path) as f:
        rd = csv.DictReader(f)
        cells = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        for r in rd:
            rows.append(dict(frame_id=r["frame_id"], scene=r["scene_id"], tier=r["tier"],
                             arm=r["toggle_state"],
                             p=[float(r[f"p_{c}"]) for c in cells],
                             g=[float(r[f"g_{c}"]) for c in cells]))
    return rows


def arm_stats(rows, scene, arm, tau):
    sel = [r for r in rows if r["scene"] == scene and r["arm"] == arm]
    if not sel:
        return None
    fired = [sum(1 for v in r["p"] if v >= tau) for r in sel]
    return dict(n=len(sel),
                fa_frame=sum(1 for k in fired if k) / len(sel),
                cells_per_frame=sum(fired) / len(sel),
                mean_max_p=sum(max(r["p"]) for r in sel) / len(sel),
                recall_frame=(sum(1 for r in sel
                                  if any(v >= tau and gg > 0.5 for v, gg in zip(r["p"], r["g"])))
                              / max(1, sum(1 for r in sel if any(gg > 0.5 for gg in r["g"]))))
                if any(any(gg > 0.5 for gg in r["g"]) for r in sel) else None)


def twin_stats(path, scene):
    if not os.path.isfile(path):
        return None
    kept, tot, df, ds = [], 0, [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["scene_id"] != scene:
                continue
            tot += 1
            if r["kept"].lower() in ("true", "1"):
                kept.append(r)
                for key, acc in (("delta_frame", df), ("delta_score", ds)):
                    try:
                        v = float(r[key])
                    except (TypeError, ValueError):
                        continue
                    if v == v:                       # not NaN
                        acc.append(v)
    return dict(pairs_total=tot, pairs_kept=len(kept),
                d_frame=(sum(df) / len(df)) if df else None, n_frame=len(df),
                d_score=(sum(ds) / len(ds)) if ds else None, n_score=len(ds))


def mr(vals, fmt="{:.3f}"):
    """mean ± half-range over seeds, the SEED_TABLE convention."""
    vals = [v for v in vals if v is not None]
    if not vals:
        return "n/a"
    if len(vals) == 1:
        return fmt.format(vals[0])
    return f"{fmt.format(st.mean(vals))} ±{fmt.format((max(vals) - min(vals)) / 2)}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--tau", type=float, default=0.5)
    ap.add_argument("--seeds", default="42,43,44")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    seeds = [s.strip() for s in a.seeds.split(",") if s.strip()]
    R = a.root
    data = {"tau": a.tau, "seeds": seeds, "scenes": {}, "qc": {}}

    for scene in SCENES:
        data["scenes"][scene] = {}
        for arm_tag in ("old", "new"):
            per = {}
            for s in seeds:
                pf = os.path.join(R, f"eval_{arm_tag}_s{s}", "per_frame.csv")
                tw = os.path.join(R, f"twin_{arm_tag}_s{s}", "twin_pairs.csv")
                if not os.path.isfile(pf):
                    continue
                rows = read_per_frame(pf)
                per[s] = dict(off=arm_stats(rows, scene, "off", a.tau),
                              on=arm_stats(rows, scene, "on", a.tau),
                              twin=twin_stats(tw, scene))
            data["scenes"][scene][arm_tag] = per

    # QC: the new round re-infers the same ON-arm PNGs the frozen eval used.
    for s in seeds:
        pnew = os.path.join(R, f"eval_new_s{s}", "per_frame.csv")
        pold = os.path.join(R, f"eval_old_s{s}", "per_frame.csv")
        if not (os.path.isfile(pnew) and os.path.isfile(pold)):
            continue
        A = {r["frame_id"]: r["p"] for r in read_per_frame(pnew) if r["arm"] == "on"}
        B = {r["frame_id"]: r["p"] for r in read_per_frame(pold) if r["arm"] == "on"}
        common = sorted(set(A) & set(B))
        dev = max((abs(x - y) for f in common for x, y in zip(A[f], B[f])), default=None)
        data["qc"][s] = dict(on_rows_common=len(common), max_abs_dp=dev)

    L = ["# CTRL_TABLE — dressing-preserving OFF arm vs the original OFF arm", "",
         f"tau = {a.tau} · seeds {', '.join(seeds)} · grid PROVISIONAL-GRID-V1 (20 cells) · "
         "RGB recipe v2 checkpoints", "",
         "**old off** = `dataset/v2_corpus/260819_main_off` (the toggle also deleted the leaf mound, the "
         "railing and, in N3, the mural) · **new off** = `dataset/v2_probes/260820_ctrloff` "
         "(`keep_dressing`: hazard geometry only). Both are paired against the SAME on arm, "
         "`dataset/v2_corpus/260819_main_on`. Every off frame carries an all-zero GT, so `FA_frame` is a "
         "pure false-alarm rate.", "",
         "## 1. Off-arm response (per seed, then mean ±half-range)", "",
         "| scene | arm | seed | frames | FA_frame | cells/frame | mean max p |",
         "|---|---|---|---|---|---|---|"]
    for scene in SCENES:
        for arm_tag in ("old", "new"):
            per = data["scenes"][scene][arm_tag]
            for s in seeds:
                d = (per.get(s) or {}).get("off")
                if not d:
                    L.append(f"| {scene} | {arm_tag} | {s} | — | — | — | — |")
                    continue
                L.append(f"| {scene} | {arm_tag} | {s} | {d['n']} | {d['fa_frame']:.3f} | "
                         f"{d['cells_per_frame']:.2f} | {d['mean_max_p']:.3f} |")
            got = [(per.get(s) or {}).get("off") for s in seeds]
            got = [g for g in got if g]
            if got:
                L.append(f"| **{scene}** | **{arm_tag}** | **3 seeds** | {got[0]['n']} | "
                         f"**{mr([g['fa_frame'] for g in got])}** | "
                         f"{mr([g['cells_per_frame'] for g in got], '{:.2f}')} | "
                         f"{mr([g['mean_max_p'] for g in got])} |")
    L += ["", "## 2. Twin delta, old vs new off arm (pose-matched pairs, tol 0.15 m)", "",
          "| scene | arm | seed | pairs kept/total | d_frame | d_score |",
          "|---|---|---|---|---|---|"]
    for scene in SCENES:
        for arm_tag in ("old", "new"):
            per = data["scenes"][scene][arm_tag]
            for s in seeds:
                t = (per.get(s) or {}).get("twin")
                if not t:
                    L.append(f"| {scene} | {arm_tag} | {s} | — | — | — |")
                    continue
                L.append(f"| {scene} | {arm_tag} | {s} | {t['pairs_kept']}/{t['pairs_total']} | "
                         + (f"{t['d_frame']:.3f} |" if t["d_frame"] is not None else "n/a |")
                         + (f" {t['d_score']:.3f} |" if t["d_score"] is not None
                            else " n/a (no GT-positive cell on the on arm) |"))
            got = [(per.get(s) or {}).get("twin") for s in seeds]
            got = [g for g in got if g]
            if got:
                L.append(f"| **{scene}** | **{arm_tag}** | **3 seeds** | "
                         f"{got[0]['pairs_kept']}/{got[0]['pairs_total']} | "
                         f"**{mr([g['d_frame'] for g in got])}** | "
                         f"{mr([g['d_score'] for g in got])} |")
    L += ["", "## 3. QC", "",
          "| seed | shared on-arm rows | max abs dp (new eval vs frozen eval) |", "|---|---|---|"]
    for s in seeds:
        q = data["qc"].get(s)
        if not q:
            L.append(f"| {s} | — | — |")
            continue
        dp = "—" if q["max_abs_dp"] is None else f"{q['max_abs_dp']:.2e}"
        L.append(f"| {s} | {q['on_rows_common']} | {dp} |")
    L += ["", "> The on-arm rows are the same PNGs in both evaluations; a max |dp| above ~1e-5 "
          "means the two runs did not see the same frames and the comparison is void.", "",
          "## 4. How to read this", "",
          "The old off arm removes the hazard AND the scene's dressing; the new one removes the "
          "hazard only. `FA_frame(new) ~ FA_frame(old)` says the firing never depended on the "
          "dressing; `FA_frame(new) > FA_frame(old)` says the dressing is what the model fires "
          "on (the shortcut reading of DIAG_V1 §3); `FA_frame(new) < FA_frame(old)` would be "
          "the surprise and needs its own investigation before it is quoted. For sceneN3 the new "
          "off arm is structurally identical to the on arm, so its twin d_frame is a NULL "
          "control: a value near 0 is the expected result and a large one is a measurement "
          "artefact, not a finding.", ""]
    out = a.out or os.path.join(R, "CTRL_TABLE.md")
    with open(out, "w") as f:
        f.write("\n".join(L))
    with open(os.path.join(R, "ctrl_numbers.json"), "w") as f:
        json.dump(data, f, indent=1)
    print(f"[ctrl_table] -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
