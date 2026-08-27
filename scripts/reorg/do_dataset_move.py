#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S2 step 2 -- physically regroup dataset/<round> into dataset/<group>/<round>.

Reads Docs/reorg_0827/dataset_moves.tsv (written by build_rounds_map.py) and
os.rename()s each round.  os.rename, not shutil.move: it is atomic per round,
it keeps every inode (so the 2,855 absolute symlinks inside the g7fix shadow
trees still resolve to the same files, they just need their *targets* rewritten
afterwards), and it refuses silently-slow cross-device copies.  st_dev is
asserted equal on both sides before every single rename.

The 16 v2_corpus rounds go first, as one unit: the 8 g7fix shadow trees and the
8 rounds they shadow must never be split across a half-finished move.

Writes:
  Docs/reorg_0827/dataset_move_log.tsv   one row per rename, with mtime + st_dev
  Docs/reorg_0827/dataset_moves.tsv      rewritten with a `done` column
"""
from __future__ import annotations

import csv
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTDIR = os.path.join(REPO, "Docs", "reorg_0827")
MOVES = os.path.join(OUTDIR, "dataset_moves.tsv")
LOG = os.path.join(OUTDIR, "dataset_move_log.tsv")


def main():
    with open(MOVES, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    if len(rows) != 196:
        raise SystemExit("[move] expected 196 rows, got %d" % len(rows))

    dev = os.stat(os.path.join(REPO, "dataset")).st_dev
    # v2_corpus first, as a unit; then everything else in TSV order.
    order = ([r for r in rows if r["new_path"].startswith("dataset/v2_corpus/")] +
             [r for r in rows if not r["new_path"].startswith("dataset/v2_corpus/")])
    assert len(order) == len(rows)

    done = {}
    log = open(LOG, "w", encoding="utf-8")
    log.write("seq\tround\told_path\tnew_path\taction\tsize_bytes\tst_dev\tmtime\tresult\n")
    for i, r in enumerate(order, 1):
        old = os.path.join(REPO, r["old_path"])
        new = os.path.join(REPO, r["new_path"])
        if not os.path.isdir(old):
            raise SystemExit("[move] old_path missing: %s" % r["old_path"])
        if os.path.exists(new):
            raise SystemExit("[move] new_path already exists: %s" % r["new_path"])
        parent = os.path.dirname(new)
        os.makedirs(parent, exist_ok=True)
        st_old, st_par = os.stat(old), os.stat(parent)
        if not (st_old.st_dev == st_par.st_dev == dev):
            raise SystemExit("[move] cross-device rename refused: %s (%s -> %s)"
                             % (r["round"], st_old.st_dev, st_par.st_dev))
        mtime = st_old.st_mtime
        os.rename(old, new)
        if not os.path.isdir(new) or os.path.exists(old):
            raise SystemExit("[move] rename did not land: %s" % r["round"])
        log.write("%d\t%s\t%s\t%s\t%s\t%s\t%d\t%s\tok\n"
                  % (i, r["round"], r["old_path"], r["new_path"], r["action"],
                     r["size_bytes"], dev,
                     time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(mtime))))
        done[r["round"]] = "yes"
    log.close()

    # rewrite the plan TSV with a done column (atomic)
    tmp = MOVES + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("round\told_path\tnew_path\taction\tsize_bytes\tdone\n")
        for r in rows:
            fh.write("%s\t%s\t%s\t%s\t%s\t%s\n"
                     % (r["round"], r["old_path"], r["new_path"], r["action"],
                        r["size_bytes"], done.get(r["round"], "NO")))
    os.replace(tmp, MOVES)
    print("[move] renamed %d rounds (v2_corpus %d first)"
          % (len(done), sum(1 for r in rows
                            if r["new_path"].startswith("dataset/v2_corpus/"))))
    print("[move] log: %s" % LOG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
