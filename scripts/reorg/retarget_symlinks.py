#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S2 step 4 -- repoint the absolute symlinks that the dataset/ regroup broke.

Two populations, both created before the reorg with an *absolute* target under
`<REPO>/dataset/<round>/...`:

  * 2,855 links inside the 8 `260820_boost_*_g7fix{,M}` shadow trees, which
    are now at `dataset/v2_corpus/...`;
  * 2,832 image links in `experiments/dayrun_0820/yolo_ds/images/`.

Both are rewritten to a RELATIVE target computed from the link's own directory,
so the repo can be moved or copied without breaking 5,687 links again.

Method: readlink -> map `dataset/<round>` to `dataset/<group>/<round>` through
dataset/ROUNDS.json -> assert the new absolute target exists -> os.path.relpath
from the link's directory -> write a temp link beside it and os.replace() it
onto the old one (atomic; the link count never dips).

Nothing is deleted and no link is created: the population is exactly the set of
links that already existed, so `find . -type l | wc -l` is invariant.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DS = os.path.join(REPO, "dataset")
LOG = os.path.join(REPO, "Docs", "reorg_0827", "symlink_retarget.tsv")


def load_index():
    with open(os.path.join(DS, "ROUNDS.json"), encoding="utf-8") as fh:
        return json.load(fh)


def map_target(t, index):
    """Old absolute dataset target -> new absolute target, or None if n/a."""
    pre = DS + os.sep
    if not t.startswith(pre):
        return None
    rest = t[len(pre):]
    head, _, tail = rest.partition("/")
    grp = index.get(head)
    if grp is None:
        return None
    return os.path.join(DS, grp, head, tail) if tail else os.path.join(DS, grp, head)


def iter_links(roots):
    for root in roots:
        for dirpath, dirs, files in os.walk(os.path.join(REPO, root)):
            dirs[:] = sorted(d for d in dirs
                             if not os.path.islink(os.path.join(dirpath, d)))
            for n in sorted(files + [d for d in os.listdir(dirpath)
                                     if os.path.islink(os.path.join(dirpath, d))]):
                p = os.path.join(dirpath, n)
                if os.path.islink(p):
                    yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roots", default="dataset,experiments/dayrun_0820/yolo_ds")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    index = load_index()
    roots = [r for r in a.roots.split(",") if r]

    seen, changed, already, skipped, bad = set(), 0, 0, 0, []
    rows = []
    for p in iter_links(roots):
        if p in seen:
            continue
        seen.add(p)
        t = os.readlink(p)
        if not t.startswith("/"):
            already += 1
            continue
        new_abs = map_target(t, index)
        if new_abs is None:
            skipped += 1
            continue
        if not os.path.exists(new_abs):
            bad.append((os.path.relpath(p, REPO), t, new_abs))
            continue
        newrel = os.path.relpath(new_abs, os.path.dirname(p))
        rows.append((os.path.relpath(p, REPO), t, newrel,
                     os.path.relpath(new_abs, REPO)))
        if a.apply:
            tmp = p + ".relink.tmp"
            if os.path.islink(tmp) or os.path.exists(tmp):
                os.remove(tmp)
            os.symlink(newrel, tmp)
            os.replace(tmp, p)
            if os.path.realpath(p) != os.path.realpath(new_abs):
                raise SystemExit("[relink] post-check failed for %s" % p)
        changed += 1

    if bad:
        for r in bad[:10]:
            print("[relink] TARGET MISSING %s -> %s (mapped %s)" % r, file=sys.stderr)
        raise SystemExit("[relink] %d links map to a non-existent target" % len(bad))

    if a.apply:
        with open(LOG, "w", encoding="utf-8") as fh:
            fh.write("link\told_target\tnew_target_relative\tnew_target_repo_relative\n")
            for r in sorted(rows):
                fh.write("%s\t%s\t%s\t%s\n" % r)
        print("[relink] log: %s" % LOG)
    print("[relink] mode        : %s" % ("APPLY" if a.apply else "DRY-RUN"))
    print("[relink] links seen  : %d" % len(seen))
    print("[relink] retargeted  : %d" % changed)
    print("[relink] already rel : %d" % already)
    print("[relink] not a dataset round target: %d" % skipped)
    import collections
    per = collections.Counter("/".join(r[0].split("/")[:3]) for r in rows)
    for k, v in per.most_common(12):
        print("           %6d  %s" % (v, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
