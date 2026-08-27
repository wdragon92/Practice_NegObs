#!/usr/bin/env python3
"""S5 gate 2 — every `Docs/...` path cited anywhere in the repo must resolve.

Re-runnable and read-only.  Walks with os.walk (this shell's `grep` is ugrep with
--ignore-files and skips the gitignored trees).

The repo carries a KNOWN backlog of dangling `Docs/` citations that predates the
0827 reorg — `Docs/reports/repo_reorg_v1.md` §3 calls it the 유령 인용 대장 (ghost
citation register): reports that were planned and never written, files archived by
the 08-05 / 08-14 batches whose citers were not repointed, and so on.  Fixing that
backlog is not this reorg's job, so the gate is scoped:

    FAIL only when a broken citation points INTO a path this reorg created —
    Docs/archive/legacy/, Docs/archive/campaign_status/, Docs/campaign/.

Anything else is reported as INFO with its count, so the number can be watched but
does not gate.  `scripts/reorg/` and `Docs/reorg_0827/` are skipped: they name old
and new forms by construction.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s5_scan import iter_files, TEXT_EXTS  # noqa: E402

RX = re.compile(r"(?<![A-Za-z0-9_/.-])(Docs/[^\s`'\"|)\],<>*]+\.(?:md|json|yaml|yml|png))")
GATED = ("Docs/archive/legacy/", "Docs/archive/campaign_status/", "Docs/campaign/")
SKIP = ["Docs/reorg_0827", "scripts/reorg"]


def main():
    seen, missing = set(), {}
    for p in iter_files(REPO, TEXT_EXTS, SKIP):
        rel = os.path.relpath(p, REPO)
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for path in set(RX.findall(txt)):
            path = path.rstrip(".")
            seen.add(path)
            if not os.path.exists(os.path.join(REPO, path)):
                missing.setdefault(path, set()).add(rel)
    gated = {k: v for k, v in missing.items() if k.startswith(GATED)}
    print("distinct Docs/ paths cited: %d · broken: %d" % (len(seen), len(missing)))
    print("INFO  pre-existing dangling citations (ghost-citation backlog): %d"
          % (len(missing) - len(gated)))
    if gated:
        print("FAIL  broken citations into paths the 0827 reorg created: %d" % len(gated))
        for k, v in sorted(gated.items()):
            print("        %s  <- %s" % (k, sorted(v)[:3]))
        return 1
    print("PASS  broken citations into paths the 0827 reorg created: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
