#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build dataset/ROUNDS.json and Docs/reorg_0827/dataset_moves.tsv.

Input  : the survey's per-round plan TSV (round, group, role, action, size, ...)
         and a `du -sb` snapshot for the real sizes.
Output : dataset/ROUNDS.json   {round: relative path of its NEW parent}
         Docs/reorg_0827/dataset_moves.tsv  round, old_path, new_path, action, size_bytes

Grouping rules — master plan D1 (they override the survey's own tree):
  * groups are FLAT: the survey's `v3_library/w1_B` etc. collapse to `v3_library`
  * `v2_relabel_shadow` (the 8 g7fix shadow trees) moves as one unit with `v2_corpus`
  * action=archive           -> `_archive/<group>`
  * action=delete_candidate  -> `_archive/_delete_candidates`   (moved, never deleted)
  * `scene_dev_2607`         -> `_archive/scene_dev_2607`       (all 11 are archive)
  * `260824_handson`         -> `misc`
  * the 3 pilots             -> `_archive/pilots`   (this rule wins over the
                                action column: 260816_dataall is an empty pilot dir)
Round NAMES never change; only the parent does.
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET = os.path.join(REPO, "dataset")
OUTDIR = os.path.join(REPO, "Docs", "reorg_0827")

PILOTS = {"260815_datapilot", "260815_datapilot_aug", "260816_dataall"}
MISC = {"260824_handson": "misc"}
LIVE_GROUPS = ["v2_corpus", "v2_probes", "cueoff", "v3_scene_build",
               "v3_library", "v3_test_ext", "v3_aux", "misc"]


def new_parent(round_name, group, action):
    """Relative path (under dataset/) of the round's new parent directory."""
    if round_name in PILOTS:
        return "_archive/pilots"
    if round_name in MISC:
        return MISC[round_name]
    base = group.split("/")[0]
    if base == "v2_relabel_shadow":
        base = "v2_corpus"
    if base == "scene_dev_2607":
        return "_archive/scene_dev_2607"
    if action == "delete_candidate":
        return "_archive/_delete_candidates"
    if action == "archive":
        return "_archive/" + base
    if action == "keep":
        return base
    raise SystemExit("unknown action %r for %s" % (action, round_name))


def main(plan_tsv, du_tsv):
    sizes = {}
    with open(du_tsv, encoding="utf-8") as fh:
        for line in fh:
            b, name = line.rstrip("\n").split("\t", 1)
            sizes[name.rstrip("/")] = int(b)

    rows, seen = [], set()
    with open(plan_tsv, encoding="utf-8") as fh:
        header = next(fh).rstrip("\n").split("\t")
        ir, ig, ia = header.index("round"), header.index("group"), header.index("action")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= ia or not f[ir].strip():
                continue
            name, group, action = f[ir].strip(), f[ig].strip(), f[ia].strip()
            if name in seen:
                raise SystemExit("duplicate round in plan: " + name)
            seen.add(name)
            parent = new_parent(name, group, action)
            rows.append(dict(round=name, group=group, action=action, parent=parent,
                             old=os.path.join("dataset", name),
                             new=os.path.join("dataset", parent, name),
                             size=sizes.get(name, -1)))

    # ---- validation --------------------------------------------------------
    errs = []
    if len(rows) != 196:
        errs.append("expected 196 rounds, got %d" % len(rows))
    for r in rows:
        if not os.path.isdir(os.path.join(REPO, r["old"])):
            errs.append("old_path missing on disk: " + r["old"])
        if r["size"] < 0:
            errs.append("no measured size for " + r["round"])
    newpaths = [r["new"] for r in rows]
    if len(set(newpaths)) != len(newpaths):
        errs.append("duplicate new_path")
    parents = sorted({r["parent"] for r in rows})
    allowed = set(LIVE_GROUPS) | {
        "_archive/" + g for g in
        ("v2_probes", "v3_scene_build", "v3_library", "v3_aux",
         "scene_dev_2607", "pilots", "_delete_candidates")}
    bad = [p for p in parents if p not in allowed]
    if bad:
        errs.append("unexpected group(s): " + ", ".join(bad))
    tops = sorted({p.split("/")[0] for p in parents})
    if len(tops) != 9:
        errs.append("dataset/ top level would have %d entries, expected 9: %s"
                    % (len(tops), tops))
    on_disk = sorted(e for e in os.listdir(DATASET)
                     if os.path.isdir(os.path.join(DATASET, e)))
    if len(on_disk) == 196 and sorted(seen) != on_disk:
        errs.append("plan rounds != dataset/ dirs (flat layout expected here)")
    if errs:
        for e in errs:
            print("FAIL " + e, file=sys.stderr)
        raise SystemExit(1)

    # ---- write -------------------------------------------------------------
    index = {r["round"]: r["parent"] for r in rows}
    os.makedirs(OUTDIR, exist_ok=True)
    p = os.path.join(DATASET, "ROUNDS.json")
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, p)

    t = os.path.join(OUTDIR, "dataset_moves.tsv")
    tmp = t + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("round\told_path\tnew_path\taction\tsize_bytes\n")
        for r in sorted(rows, key=lambda x: (x["parent"], x["round"])):
            fh.write("%s\t%s\t%s\t%s\t%d\n"
                     % (r["round"], r["old"], r["new"], r["action"], r["size"]))
    os.replace(tmp, t)

    # ---- report ------------------------------------------------------------
    print("rounds: %d   ROUNDS.json: %s   moves: %s" % (len(rows), p, t))
    print("%-28s %5s %14s" % ("group", "n", "bytes"))
    tot = 0
    for g in sorted(parents):
        sel = [r for r in rows if r["parent"] == g]
        b = sum(r["size"] for r in sel)
        tot += b
        print("%-28s %5d %14d  (%6.2f GiB)" % (g, len(sel), b, b / 1073741824))
    print("%-28s %5d %14d  (%6.2f GiB)" % ("TOTAL", len(rows), tot, tot / 1073741824))
    for a in ("keep", "archive", "delete_candidate"):
        sel = [r for r in rows if r["action"] == a]
        print("action %-17s %5d %14d" % (a, len(sel), sum(r["size"] for r in sel)))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_rounds_map.py <plan.tsv> <du_sb.tsv>")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
