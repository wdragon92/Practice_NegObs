#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4: physically regroup `look_check/` (survey C §1.4 / master plan D3).

Four move classes, all `os.rename` inside `look_check/` (one filesystem, gitignored
tree — git records none of this, which is why every row is logged):

  1. free rounds     `<scene>/<round>`        -> `_archive/<wave>/<scene>/<round>`
  2. review galleries `_review/<round>`       -> `_review/<w3|w4>/<round>`
  3. the W2 gallery  `_review_w2/`            -> `_review/w2/`
  4. render journals  root `*.log`, `spike_results.json` -> `logs/`

NO back-compat symlinks are created inside a scene root: a symlink carries a fresh
mtime and would re-break `ls -t <scene>/*/ | head -1` latest-round discovery
(`look_check/README.md` §1, symlink policy constraint 1).

Refuses to move any round in the code-derived pinned set (`lookcheck_pins.py`).
`--dry-run` (default) prints the plan; `--apply` performs it.
"""
from __future__ import annotations
import argparse
import csv
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LC = os.path.join(ROOT, "look_check")
TSV_DEFAULT = ("/tmp/claude-1000/-home-vislab-Desktop-work-sy/"
               "15df50ca-11be-4545-a9e5-5c8c56211ca8/scratchpad/lookcheck_rounds.tsv")
LOG = os.path.join(ROOT, "Docs", "reorg_0827", "lookcheck_moves.tsv")
WAVES = ("w2", "w2d", "w3", "w3fix")


def du_sb(paths):
    """{path: bytes} via `du -sb`, batched."""
    out = {}
    for i in range(0, len(paths), 200):
        chunk = paths[i:i + 200]
        r = subprocess.run(["du", "-sb"] + chunk, capture_output=True, text=True)
        for ln in r.stdout.splitlines():
            n, p = ln.split("\t", 1)
            out[p] = int(n)
    return out


def pinned_set():
    r = subprocess.run([sys.executable, os.path.join(HERE, "lookcheck_pins.py"), "--tsv"],
                       capture_output=True, text=True, check=True)
    return {tuple(ln.split("\t")[:2]) for ln in r.stdout.strip().split("\n")[1:]}


def plan_rounds(tsv):
    rows = list(csv.DictReader(open(tsv, encoding="utf-8"), delimiter="\t"))
    pins = pinned_set()
    plan, errs = [], []
    for r in rows:
        loc = r["proposed_location"]
        if "look_check/_archive/" not in loc:
            continue
        wave = loc.split("look_check/_archive/", 1)[1].split("/")[0]
        if wave not in WAVES:
            errs.append(f"unknown wave {wave!r} for {r['scene']}/{r['round']}")
            continue
        key = (r["scene"], r["round"])
        if key in pins:
            errs.append(f"PINNED BY CODE, refusing to archive: {key}")
            continue
        old = os.path.join(LC, r["scene"], r["round"])
        new = os.path.join(LC, "_archive", wave, r["scene"], r["round"])
        if not os.path.isdir(old):
            errs.append(f"source missing: {old}")
            continue
        if os.path.exists(new):
            errs.append(f"destination exists: {new}")
            continue
        plan.append(dict(old=old, new=new, wave=wave, kind="round",
                         reason=f"free round ({r['wave']}, role={r['role']}, "
                                f"cited_by={r['cited_total']}) - not pinned by "
                                f"valset.py / regr-chain / BoR stamp / anchor"))
    return plan, errs


def plan_reviews():
    plan, errs = [], []
    for d in sorted(glob.glob(os.path.join(LC, "_review", "*"))):
        if not os.path.isdir(d) or os.path.islink(d):
            continue
        name = os.path.basename(d)
        if name in ("w2", "w3", "w4"):
            continue
        if "_w3_" in name:
            wave = "w3"
        elif "_w4_" in name:
            wave = "w4"
        else:
            errs.append(f"_review: cannot classify wave for {name}")
            continue
        new = os.path.join(LC, "_review", wave, name)
        if os.path.exists(new):
            errs.append(f"destination exists: {new}")
            continue
        plan.append(dict(old=d, new=new, wave=wave, kind="review",
                         reason="review gallery grouped by wave"))
    return plan, errs


def plan_review_w2():
    src = os.path.join(LC, "_review_w2")
    if not os.path.isdir(src):
        return [], []
    dst = os.path.join(LC, "_review", "w2")
    if os.path.exists(dst):
        return [], [f"destination exists: {dst}"]
    return [dict(old=src, new=dst, wave="w2", kind="review_w2",
                 reason="_review_w2/ folded into _review/w2/")], []


def plan_logs():
    plan, errs = [], []
    dst_dir = os.path.join(LC, "logs")
    for p in sorted(glob.glob(os.path.join(LC, "*.log"))
                    + glob.glob(os.path.join(LC, "spike_results.json"))):
        if os.path.islink(p) or not os.path.isfile(p):
            continue
        new = os.path.join(dst_dir, os.path.basename(p))
        if os.path.exists(new):
            errs.append(f"destination exists: {new}")
            continue
        plan.append(dict(old=p, new=new, wave="-", kind="log",
                         reason="render journal moved out of the look_check root"))
    return plan, errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", default=TSV_DEFAULT)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    plan, errs = [], []
    for f in (lambda: plan_rounds(a.tsv), plan_reviews, plan_review_w2, plan_logs):
        p, e = f()
        plan += p
        errs += e
    if errs:
        print("REFUSING - %d problem(s):" % len(errs))
        for e in errs:
            print("  " + e)
        sys.exit(1)

    sizes = du_sb([p["old"] for p in plan])
    by_kind = {}
    for p in plan:
        p["size"] = sizes.get(p["old"], 0)
        k = by_kind.setdefault(p["kind"], [0, 0])
        k[0] += 1
        k[1] += p["size"]
    for k, (n, b) in sorted(by_kind.items()):
        print(f"{k:<12} {n:5d} entries {b/2**30:8.2f} GiB")
    print(f"{'TOTAL':<12} {len(plan):5d} entries "
          f"{sum(p['size'] for p in plan)/2**30:8.2f} GiB")
    if not a.apply:
        print("\n(dry run - nothing moved; pass --apply)")
        return

    for p in plan:
        os.makedirs(os.path.dirname(p["new"]), exist_ok=True)
        os.rename(p["old"], p["new"])
    with open(LOG, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["old", "new", "wave", "kind", "size_bytes", "reason"])
        for p in plan:
            w.writerow([os.path.relpath(p["old"], ROOT), os.path.relpath(p["new"], ROOT),
                        p["wave"], p["kind"], p["size"], p["reason"]])
    print(f"\nMOVED {len(plan)} entries; log -> {os.path.relpath(LOG, ROOT)}")
    bad = [p for p in plan if os.path.exists(p["old"]) or not os.path.exists(p["new"])]
    print("post-check:", "OK" if not bad else f"FAIL {len(bad)}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
