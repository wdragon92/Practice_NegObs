#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4: rewrite the text citations that point at paths the S4 move relocated.

Four transforms, applied in one pass per file, longest-first inside each class:
  `_review_w2`                    -> `_review/w2`
  `_review/<gallery>`             -> `_review/<w3|w4>/<gallery>`   (47 galleries)
  `look_check/<name>.log`         -> `look_check/logs/<name>.log`  (11 journals)
  `look_check/spike_results.json` -> `look_check/logs/spike_results.json`

Bare round / gallery / file NAMES are never touched - only path forms.
The move log `Docs/reorg_0827/lookcheck_moves.tsv` is the source of the name lists,
so this script cannot drift from what was actually moved.

Excluded by design: `Docs/reorg_0827/**` (this reorg's own record of the OLD paths),
`scripts/reorg/**` (this tooling names both forms), `look_check/INDEX.md`
(regenerated from disk by `make_lookcheck_index.py`) and `look_check/README.md`
(hand-extended in the same stage). `--apply` writes `<file>.s4.bak` next to each file.
"""
from __future__ import annotations
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MOVES = os.path.join(ROOT, "Docs", "reorg_0827", "lookcheck_moves.tsv")
LOG = os.path.join(ROOT, "Docs", "reorg_0827", "lookcheck_citation_edits.tsv")
TEXT = (".md", ".py", ".sh", ".json", ".txt", ".tsv", ".csv", ".yaml", ".yml",
        ".log", ".cfg", ".ini")
EXCLUDE_REL = ("Docs/reorg_0827", "scripts/reorg")
EXCLUDE_FILE = ("look_check/INDEX.md", "look_check/README.md")


def build_rules():
    rows = list(csv.DictReader(open(MOVES, encoding="utf-8"), delimiter="\t"))
    revs = {os.path.basename(r["old"]): r["wave"] for r in rows if r["kind"] == "review"}
    logs = [os.path.basename(r["old"]) for r in rows if r["kind"] == "log"]
    rules = []
    # 1. _review_w2 -> _review/w2   (also covers `look_check/_review_w2/...`)
    rules.append(("review_w2", re.compile(r"_review_w2(?![A-Za-z0-9_])"),
                  lambda m: "_review/w2"))
    # 2. _review/<gallery> -> _review/<wave>/<gallery>
    alt = "|".join(sorted(map(re.escape, revs), key=len, reverse=True))
    rules.append(("review_round",
                  re.compile(r"_review/(" + alt + r")(?![A-Za-z0-9_])"),
                  lambda m: f"_review/{revs[m.group(1)]}/{m.group(1)}"))
    # 3. look_check/<name>.log|spike_results.json -> look_check/logs/<same>
    alt = "|".join(sorted(map(re.escape, logs), key=len, reverse=True))
    rules.append(("root_log",
                  re.compile(r"look_check/(" + alt + r")(?![A-Za-z0-9_])"),
                  lambda m: f"look_check/logs/{m.group(1)}"))
    return rules


def walk_files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d != ".git"]
        rel = os.path.relpath(dp, ROOT)
        if any(rel == e or rel.startswith(e + os.sep) for e in EXCLUDE_REL):
            continue
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p) or not fn.endswith(TEXT):
                continue
            r = os.path.relpath(p, ROOT)
            if r in EXCLUDE_FILE or r.endswith(".s4.bak"):
                continue
            yield p, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    rules = build_rules()
    log_rows, tot = [], 0
    for p, rel in walk_files():
        try:
            src = open(p, encoding="utf-8", errors="strict").read()
        except (UnicodeDecodeError, OSError):
            continue
        out, counts = src, {}
        for name, pat, fn in rules:
            out, n = pat.subn(fn, out)
            if n:
                counts[name] = n
        if not counts:
            continue
        n_here = sum(counts.values())
        tot += n_here
        log_rows.append([rel, n_here,
                         counts.get("review_w2", 0), counts.get("review_round", 0),
                         counts.get("root_log", 0),
                         len(out.encode()) - len(src.encode())])
        print(f"{n_here:5d}  {rel}  {counts}")
        if a.apply:
            with open(p + ".s4.bak", "w", encoding="utf-8") as fh:
                fh.write(src)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(out)
    print(f"\n{len(log_rows)} files, {tot} substitutions")
    if a.apply:
        with open(LOG, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["file", "n_total", "n_review_w2", "n_review_round",
                        "n_root_log", "delta_bytes"])
            w.writerows(log_rows)
        print(f"log -> {os.path.relpath(LOG, ROOT)}")
    else:
        print("(dry run - nothing written; pass --apply)")


if __name__ == "__main__":
    main()
