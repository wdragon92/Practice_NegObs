#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 -- import every module this stage edited, on a bare interpreter.

`python3 scripts/reorg/import_check.py [--all]`

Default: the 35 python files S3 converted. `--all` widens to every `*.py`
under `experiments/` and `scripts/`, which is how the pre-existing
Isaac/torch-only modules were classified.

WARNING, and the reason this file exists rather than a throwaway one-liner:
a few of these modules do their work at MODULE level and REWRITE their
artifact as a side effect of being imported. An import sweep is therefore not
read-only. The artifacts listed in SIDE_EFFECT_FILES are read into memory
first and written back byte-for-byte afterwards; `--all` additionally sha1s
the whole tree and refuses to finish quietly if anything else moved.

Each module is imported in its own subprocess so one SystemExit or one missing
GPU library cannot end the sweep. The exception TYPE is recorded, not hidden:
`ModuleNotFoundError: torch` is a fact about this machine, not a defect.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Artifacts that get REWRITTEN (or created) merely by importing the module that
# produces them. Measured, not guessed: a sha1 sweep of the tree before and
# after a full `--all` run. The first two are enough for the default (edited
# files only) sweep; the rest are only reachable through `--all`.
SIDE_EFFECT_FILES = [
    "experiments/v3_0823/w1b_rimpact.json",
    "experiments/weekend_0823/rt_response/f7b_noisefloor.json",
    "Docs/archive/audit_v4/scene_overview_v4.png",
    "experiments/nightrun_0820/tau_curves/roc_Hrecall_vs_FA.png",
    "experiments/nightrun_0820/tau_curves/scatter_Hrecall_vs_FA.png",
    "experiments/nightrun_0820/tau_curves/tau_curve_b2.png",
    "experiments/nightrun_0820/tau_curves/tau_curve_depth.png",
    "experiments/nightrun_0820/tau_curves/tau_curve_rgb.png",
    "experiments/nightrun_0820/tau_curves/tau_best.json",
    "experiments/nightrun_0820/tau_curves/tau_curves.csv",
    "experiments/dayrun_0820/annotations/labels_v1_full.json",
    "experiments/dayrun_0820/dataset_manifest_v2_full.json",
    "experiments/v3_0823/panels/cell_axis_flip.png",
    "experiments/v3_0823/panels/fa_family_exemplars.png",
    "experiments/v3_0823/panels/fusion_headroom.png",
    "experiments/v3_0823/panels/rescore_delta.png",
    "experiments/weekend_0823/newmodels/fa_matched.json",
    "experiments/weekend_0823/newmodels/FA_MATCHED.md",
    "experiments/weekend_0823/rt_response/APPEND_METRICS.md",
    "experiments/weekend_0823/rt_response/APPEND_RESULTS_DRAFT.md",
    "experiments/weekend_0823/rt_response/f1_fa_matched.json",
    "experiments/weekend_0823/rt_response/F1_FA_MATCHED.md",
    "experiments/weekend_0823/rt_response/f7_hpair_pixdiff.json",
    "experiments/weekend_0823/rt_response/F7_HPAIR_PIXDIFF.md",
    "experiments/weekend_0823/rt_response/figs/f1_curve_data.json",
    "experiments/weekend_0823/rt_response/figs/fig_f1_recall_vs_fa.pdf",
    "experiments/weekend_0823/rt_response/figs/fig_f1_recall_vs_fa.png",
    "experiments/weekend_0823/rt_response/panels/h_diff_contact_sheet.png",
    "experiments/weekend_0823/rt_response/panels/h_diff_scene14_max.png",
    "experiments/weekend_0823/rt_response/panels/h_diff_scene14_median.png",
    "experiments/weekend_0823/rt_response/panels/h_diff_scene14_min.png",
    "experiments/weekend_0823/rt_response/panels/h_diff_scene15_max.png",
    "experiments/weekend_0823/rt_response/panels/h_diff_scene15_median.png",
    "experiments/weekend_0823/rt_response/panels/h_diff_scene15_min.png",
    "experiments/weekend_0823/v2s/annotations/labels_v2s.json",
    "experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json",
    "submission_0830/panels/gazebo_drop1ctrl_rgb-s42_arm.png",
    "submission_0830/panels/gazebo_drop1_rgb-s42_arm.png",
    # created from nothing by an --all sweep; absent -> deleted again
    "hazgate.json",
    "prims2.json",
]

CHILD = r'''
import importlib.util, os, sys
path = sys.argv[1]
os.chdir(sys.argv[2])
spec = importlib.util.spec_from_file_location("_mod_under_test", path)
m = importlib.util.module_from_spec(spec)
sys.modules["_mod_under_test"] = m
sys.argv = [path]
try:
    spec.loader.exec_module(m)
except SystemExit as e:
    print("SYSTEMEXIT:%s" % (e.code,))
    raise SystemExit(0)
except BaseException as e:
    print("EXC:%s:%s" % (type(e).__name__, str(e).replace(chr(10), " ")[:120]))
    raise SystemExit(0)
print("OK")
'''

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv_yolo", "yolo_ds"}


EDITS_TSV = "Docs/reorg_0827/S3_edits.tsv"


def edited_files():
    """The python files S3 converted, read from the stage's own edit ledger."""
    out = []
    with open(os.path.join(REPO, EDITS_TSV), encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            parts = line.rstrip("\n").split("\t")
            if i == 0 or len(parts) < 2:
                continue
            if parts[1] == "py":
                out.append(parts[0])
    out.append("variation_kit.py")
    return sorted(set(out))


def all_files():
    out = []
    for base in ("experiments", "scripts"):
        for dp, dn, fns in os.walk(os.path.join(REPO, base)):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            out += [os.path.relpath(os.path.join(dp, f), REPO)
                    for f in fns if f.endswith(".py")]
    return sorted(out)


def tree_sha():
    h = {}
    for dp, dn, fns in os.walk(REPO):
        dn[:] = [d for d in dn if d not in SKIP_DIRS | {"dataset", "look_check"}]
        for f in sorted(fns):
            p = os.path.join(dp, f)
            if os.path.islink(p):
                continue
            try:
                with open(p, "rb") as fh:
                    h[os.path.relpath(p, REPO)] = hashlib.sha1(fh.read()).hexdigest()
            except OSError:
                pass
    return h


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--timeout", type=int, default=180)
    a = ap.parse_args(argv)

    saved = {}                       # rel -> bytes, or None when it did not exist
    for rel in SIDE_EFFECT_FILES:
        p = os.path.join(REPO, rel)
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                saved[rel] = fh.read()
        else:
            saved[rel] = None

    before = tree_sha() if a.all else None
    files = all_files() if a.all else edited_files()
    rows, kinds = [], collections.Counter()
    for rel in files:
        try:
            r = subprocess.run([sys.executable, "-c", CHILD,
                                os.path.join(REPO, rel), REPO],
                               capture_output=True, text=True, timeout=a.timeout,
                               env={**os.environ, "PYTHONNOUSERSITE": "1"})
            out = (r.stdout or "").strip().split("\n")[-1] if r.stdout.strip() \
                else "NOOUT:" + ((r.stderr or "").strip().split("\n")[-1][:120] or "?")
        except subprocess.TimeoutExpired:
            out = "TIMEOUT"
        rows.append((rel, out))
        kinds[out.split(":")[0]] += 1

    restored = []
    for rel, blob in saved.items():
        p = os.path.join(REPO, rel)
        now = None
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                now = fh.read()
        if now == blob:
            continue
        if blob is None:                      # the sweep created it -- remove it
            os.remove(p)
            restored.append(rel + " (removed)")
            continue
        tmp = p + ".imptmp"
        with open(tmp, "wb") as fh:
            fh.write(blob)
        os.replace(tmp, p)
        with open(p, "rb") as fh:
            assert fh.read() == blob, rel
        restored.append(rel)

    for rel, out in rows:
        if out != "OK":
            print("  %-8s %s" % (out.split(":")[1] if ":" in out else out, rel))
    print("\n%d modules · %s" % (len(rows), " · ".join(
        "%s %d" % (k, v) for k, v in sorted(kinds.items()))))
    if restored:
        print("restored after import side effects: " + ", ".join(restored))

    rc = 0
    if a.all:
        after = tree_sha()
        moved = sorted(k for k in set(before) | set(after)
                       if before.get(k) != after.get(k))
        if moved:
            print("\n!! %d files changed content during the sweep:" % len(moved))
            for m in moved[:40]:
                print("   " + m)
            rc = 1
    if not a.all:
        bad = [r for r in rows if r[1] != "OK"]
        rc = 1 if bad else 0
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
