#!/usr/bin/env python3
"""S5 helper: byte-exact literal path rewrite across the repo (os.walk, no grep).

Reads (old, new) pairs from a TSV given with --pairs (or --pair old new,
repeatable), applies them longest-first in ONE pass per file, and appends one
row per (file, pair) to Docs/reorg_0827/docs_citation_edits.tsv.

`--check` reports what would change without writing.
Docs/reorg_0827/ is always excluded: it is this reorg's own record of the OLD
paths and must keep them.
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(REPO, "Docs", "reorg_0827", "docs_citation_edits.tsv")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s5_scan import iter_files, TEXT_EXTS  # noqa: E402

DEFAULT_EXCLUDES = ["Docs/reorg_0827"]

# Byte-sealed by the pre-registration doctrine: their sha256 is an invariant of the
# whole reorg.  A stale path inside them is fixed with a sibling *_PATHMAP_0827.md
# note, never by editing the file.
SEALED = {
    "experiments/v3_0823/PREREG_V3.md",
    "experiments/weekend_0823/cue_audit/PREREG_CUEOFF.md",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", nargs=2, action="append", default=[],
                    metavar=("OLD", "NEW"))
    ap.add_argument("--pairs", help="TSV file: old<TAB>new per line")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--boundary", action="store_true",
                    help="require a non-word char after the match")
    ap.add_argument("--left-boundary", action="store_true",
                    help="refuse a match preceded by a path/word char, x")
    ap.add_argument("--exts", default=None)
    ap.add_argument("--tag", default="", help="note column for the log")
    ap.add_argument("--no-log", action="store_true")
    args = ap.parse_args()

    pairs = list(args.pair)
    if args.pairs:
        with open(args.pairs) as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                old, new = line.split("\t")[:2]
                pairs.append([old, new])
    if not pairs:
        ap.error("no pairs given")
    pairs.sort(key=lambda p: -len(p[0]))

    exts = ({e if e.startswith(".") else "." + e for e in args.exts.split(",")}
            if args.exts else TEXT_EXTS)
    excludes = DEFAULT_EXCLUDES + list(args.exclude)

    rx = re.compile(
        (b"(?<![/A-Za-z0-9_.-])" if args.left_boundary else b"")
        + b"|".join(re.escape(o.encode()) for o, _ in pairs)
        + (b"(?![A-Za-z0-9_])" if args.boundary else b"")
    )
    table = {o.encode(): n.encode() for o, n in pairs}

    rows = []
    n_files = 0
    n_occ = 0
    for path in iter_files(REPO, exts, excludes):
        with open(path, "rb") as fh:
            blob = fh.read()
        counts = {}

        def sub(m):
            key = m.group(0)
            counts[key] = counts.get(key, 0) + 1
            return table[key]

        out = rx.sub(sub, blob)
        if out == blob:
            continue
        n_files += 1
        rel = os.path.relpath(path, REPO)
        if rel in SEALED:
            print(f"# SEALED, not written: {rel} ({sum(counts.values())} hits)",
                  file=sys.stderr)
            continue
        for key, c in sorted(counts.items()):
            n_occ += c
            rows.append((rel, key.decode(), table[key].decode(), c, args.tag))
        if not args.check:
            with open(path, "wb") as fh:
                fh.write(out)
    for r in rows:
        print("\t".join(str(x) for x in r))
    print(f"# files={n_files} occurrences={n_occ} "
          f"{'(CHECK ONLY)' if args.check else '(WRITTEN)'}", file=sys.stderr)
    if rows and not args.check and not args.no_log:
        with open(LOG, "a") as fh:
            for r in rows:
                fh.write("\t".join(str(x) for x in r) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
