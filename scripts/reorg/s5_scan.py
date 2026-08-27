#!/usr/bin/env python3
"""S5 helper: exhaustive literal-string scan over the repo with os.walk.

`grep` in this shell is ugrep with --ignore-files, so it silently skips the
gitignored trees (dataset/, look_check/, *.log, venv_yolo/ ...).  Every count
S5 reports must come from this script instead.

Usage:
    python3 scripts/reorg/s5_scan.py PATTERN [PATTERN ...] [--exts .md,.py]
        [--exclude PREFIX ...] [--files-only] [--all-ext]
Prints one line per (file, pattern, count) plus a summary.
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEXT_EXTS = {
    ".md", ".py", ".sh", ".json", ".txt", ".html", ".csv", ".tsv", ".yaml",
    ".yml", ".cfg", ".ini", ".log", ".usda", ".bash", ".gitignore", ".weekend_note",
}
SKIP_DIRS = {".git", "__pycache__", "venv_yolo", ".venv", "node_modules"}
MAX_BYTES = 256 * 1024 * 1024


def iter_files(root, exts, excludes):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
        if any(rel_dir == e.rstrip("/") or rel_dir.startswith(e.rstrip("/") + os.sep)
               for e in excludes):
            dirnames[:] = []
            continue
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            if os.path.islink(p):
                continue
            if exts is not None:
                ext = os.path.splitext(fn)[1]
                if ext not in exts and fn not in (".gitignore",):
                    continue
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("patterns", nargs="+")
    ap.add_argument("--exts", default=None,
                    help="comma-separated extensions; default = the text set")
    ap.add_argument("--all-ext", action="store_true", help="read every file")
    ap.add_argument("--exclude", nargs="*", default=[],
                    help="repo-relative dir prefixes to skip")
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--files-only", action="store_true")
    args = ap.parse_args()

    if args.all_ext:
        exts = None
    elif args.exts:
        exts = {e if e.startswith(".") else "." + e for e in args.exts.split(",")}
    else:
        exts = TEXT_EXTS

    pats = [p.encode() for p in args.patterns]
    totals = {p: 0 for p in args.patterns}
    files = {p: 0 for p in args.patterns}
    n_files = 0
    for p in iter_files(args.root, exts, args.exclude):
        try:
            with open(p, "rb") as fh:
                blob = fh.read()
        except OSError:
            continue
        n_files += 1
        rel = os.path.relpath(p, args.root)
        for pat, raw in zip(args.patterns, pats):
            c = blob.count(raw)
            if c:
                totals[pat] += c
                files[pat] += 1
                if args.files_only:
                    print(f"{rel}\t{pat}")
                else:
                    print(f"{rel}\t{pat}\t{c}")
    print(f"# scanned {n_files} files", file=sys.stderr)
    for pat in args.patterns:
        print(f"# TOTAL\t{pat}\tfiles={files[pat]}\tocc={totals[pat]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
