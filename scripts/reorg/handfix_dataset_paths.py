#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S2 hand pass -- the `dataset/<token>` forms a name-keyed rewriter cannot see.

`rewrite_dataset_paths.py` keys on the 196 round NAMES, so it cannot touch a
brace expansion or a glob (`dataset/260819_main_{on,off}`,
`dataset/2607xx_*`, `dataset/260820_boost_<band>_<arm>_g7fix`). Those are listed
in reference_inventory.md §6.3 R2 as hand-rewrite cases, **each only after
checking that its expansion does not cross a group boundary** -- inserting one
group is only correct if every round the pattern can expand to landed in that
same group. The `expands_to` field of every rule below records the rounds that
were checked, and `--check-groups` re-derives them from dataset/ROUNDS.json and
refuses to run if any rule spans two groups.

The edit is literally the same edit the automatic pass makes: insert `<group>/`
after `dataset/`. So `rewrite_dataset_paths.py --inverse-check` (whose inverse
strips `dataset/<group>/` generically) still reproduces every `.pre0827.bak`
byte-for-byte afterwards, and this tool's own `--inverse-check` proves the same
for the files the automatic pass never touched.

DELIBERATELY NOT REWRITTEN (recorded in Docs/reorg_0827/handfix_skipped.tsv):
  * shell/py variables (`dataset/${run}`, `dataset/$r`) -- S3 converts these to
    `variation_kit.round_dir()` / `negobs_round`; a string edit cannot fix them.
  * doc placeholders (`dataset/<run>`, `dataset/<round>`, `dataset/<split>`) --
    one documented convention, S5's job, not 30 separate edits.
  * rounds that have no directory (`dataset/260819_dataall_on`,
    `dataset/260826_v3a_segfill_smoke`, `dataset/260820_boost_e2`) -- §6.3 R9
    says leave them, do not invent a group.
  * `experiments/v3_0823/ACCOUNTING.md:82`, which quotes the sealed
    PREREG_CUEOFF.md verbatim; the quote must keep matching the sealed bytes.
    The new location is recorded in PREREG_CUEOFF_PATHMAP_0827.md instead.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTDIR = os.path.join(REPO, "Docs", "reorg_0827")
BAK_SUFFIX = ".pre0827.bak"
REPORT = os.path.join(OUTDIR, "handfix_apply.tsv")

# file, old literal, group to insert, glob(s) whose expansion was group-checked
RULES = [
    # --- v2_corpus: the 8 boost/main render rounds and their 8 g7fix shadows --
    ("experiments/dayrun_0820/narrative/diag_v1/diag_v1.py",
     "dataset/260819_main_{arm}", "v2_corpus", "260819_main_*"),
    ("experiments/dayrun_0820/narrative/diag_v1/diag_v1.py",
     "dataset/260819_main_{a}", "v2_corpus", "260819_main_*"),
    ("experiments/v3_0823/redteam/RT_LEDGER_A.md",
     "dataset/260819_main_{on,off}", "v2_corpus", "260819_main_*"),
    ("experiments/weekend_0823/c2_rootcause/C2_ROOTCAUSE.md",
     "dataset/260819_main_{on,off}", "v2_corpus", "260819_main_*"),
    ("experiments/weekend_0823/redteam/REDTEAM_0823.md",
     "dataset/260819_main_{on,off}", "v2_corpus", "260819_main_*"),
    ("experiments/weekend_0823/rt_response/README.md",
     "dataset/260819_main_{on,off}", "v2_corpus", "260819_main_*"),
    ("experiments/v3_0823/G7_RELABEL.md",
     "dataset/260820_boost_<band>_<arm>", "v2_corpus", "260820_boost_?*_*"),
    ("experiments/v3_0823/G7_RELABEL.md",
     "dataset/260820_boost_*_{on,off}", "v2_corpus", "260820_boost_*_on"),
    ("experiments/v3_0823/G7_RELABEL.md",
     "dataset/260820_boost_<band>_on_g7fix{,M}", "v2_corpus", "260820_boost_*_on_g7fix*"),
    ("experiments/v3_0823/G7_RELABEL.md",
     "dataset/260820_boost_<band>_off_g7fix{,M}", "v2_corpus", "260820_boost_*_off_g7fix*"),
    ("experiments/v3_0823/code/g7_make_shadow.py",
     "dataset/260820_boost_<band>_<arm>_g7fix", "v2_corpus", "260820_boost_*_g7fix"),
    ("experiments/v3_0823/code/g7_variantB.py",
     "dataset/260820_boost_<band>_<arm>_g7fixM", "v2_corpus", "260820_boost_*_g7fixM"),
    ("experiments/v3_0823/code/g7_build_v2corr.py",
     "dataset/260820_boost_e_{{on,off}}_g7fix", "v2_corpus", "260820_boost_e_*_g7fix*"),
    ("experiments/v3_0823/code/g7_build_v2corr.py",
     "dataset/260820_boost_e2_{{on,off}}_g7fix", "v2_corpus", "260820_boost_e2_*_g7fix*"),
    ("experiments/v3_0823/dataset_manifest_v2corr.json",
     "dataset/260820_boost_e_{on,off}_g7fixM", "v2_corpus", "260820_boost_e_*_g7fixM"),
    ("experiments/v3_0823/dataset_manifest_v2corr.json",
     "dataset/260820_boost_e2_{on,off}_g7fixM", "v2_corpus", "260820_boost_e2_*_g7fixM"),
    ("experiments/v3_0823/dataset_manifest_v2corr_roundown.json",
     "dataset/260820_boost_e_{on,off}_g7fix", "v2_corpus", "260820_boost_e_*_g7fix"),
    ("experiments/v3_0823/dataset_manifest_v2corr_roundown.json",
     "dataset/260820_boost_e2_{on,off}_g7fix", "v2_corpus", "260820_boost_e2_*_g7fix"),
    ("scripts/rounds/run_260820_boost.sh",
     "dataset/260820_boost_{h,e}_{on,off}", "v2_corpus", "260820_boost_?_on|260820_boost_?_off"),
    # --- v2_probes -----------------------------------------------------------
    ("experiments/probe_holes_0820/run_probe.sh",
     "dataset/260821_probe_{on,off}", "v2_probes", "260821_probe_*"),
    # --- cueoff --------------------------------------------------------------
    ("experiments/weekend_0823/cue_audit/run_cueoff.sh",
     "dataset/260823_cueoff{,2,3,_s20fix}_{A,B1,B2,P,C}", "cueoff", "260823_cueoff*"),
    ("experiments/weekend_0823/cue_audit/CUEOFF_RESULT_v2.md",
     "dataset/260823_cueoff_s20fix_{A,B1,B2,P,C}", "cueoff", "260823_cueoff_s20fix_*"),
    ("experiments/v3_0823/panels/PANELS_V3.md",
     "dataset/260823_cueoff*_{A,B1,B2,C,P}", "cueoff", "260823_cueoff*"),
    ("submission_0830/panels/PANELS.md",
     "dataset/260823_cueoff*_{A,B1,B2,C,P}", "cueoff", "260823_cueoff*"),
    # --- v3_library / v3_test_ext / v3_aux -----------------------------------
    ("experiments/v3_0823/W2_H67_REPORT.md",
     "dataset/260824_v3w2_h67{base,h,h2}_{A,B,C,D}", "v3_library",
     "260824_v3w2_h67base_*|260824_v3w2_h67h_*|260824_v3w2_h67h2_*"),
    ("experiments/v3_0823/W3_REPORT.md",
     "dataset/260824_v3w3_extbase_{A,B,C,D}", "v3_test_ext", "260824_v3w3_extbase_*"),
    ("experiments/v3_0823/W3_REPORT.md",
     "dataset/260824_v3w3_exth_{A,B,C,D}", "v3_test_ext", "260824_v3w3_exth_*"),
    ("experiments/v3_0823/W3_REPORT.md",
     "dataset/260824_v3w3_extlat_{A,B,C,D}", "v3_test_ext", "260824_v3w3_extlat_*"),
    ("experiments/v3_0823/W3_REPORT.md",
     "dataset/260824_v3w3_extb2_{A,B,C,D}", "v3_test_ext", "260824_v3w3_extb2_*"),
    ("experiments/v3_0823/W0_CUECLS.md",
     "dataset/260825_v3w0_cuecls_*", "v3_aux", "260825_v3w0_cuecls_*"),
    # --- _archive ------------------------------------------------------------
    ("experiments/v3_0823/REG_AUDIT.md",
     "dataset/260823_v3p5_h67reg_{A,C}", "_archive/v3_scene_build",
     "260823_v3p5_h67reg_A|260823_v3p5_h67reg_C"),
    ("experiments/mainrun_0819/PATHS.md",
     "dataset/2607xx_*", "_archive/scene_dev_2607", "2607*"),
]


def check_groups(index):
    """Every round a rule's glob can expand to must live in the rule's group."""
    bad = []
    for rel, old, group, globs in RULES:
        hits = set()
        for g in globs.split("|"):
            hits |= {n for n in index if fnmatch.fnmatchcase(n, g)}
        if not hits:
            bad.append("%s: glob %r matches no round" % (rel, globs))
            continue
        other = sorted({index[n] for n in hits} - {group})
        if other:
            bad.append("%s: %r spans groups %s (rule says %s); rounds=%s"
                       % (rel, old, other, group, sorted(hits)[:6]))
    return bad


def apply_rules(apply_changes):
    with open(os.path.join(REPO, "dataset", "ROUNDS.json"), encoding="utf-8") as fh:
        index = json.load(fh)
    bad = check_groups(index)
    if bad:
        for b in bad:
            print("[handfix] GROUP BOUNDARY " + b, file=sys.stderr)
        raise SystemExit("[handfix] %d rule(s) cross a group boundary" % len(bad))

    per_file = {}
    for rel, old, group, globs in RULES:
        per_file.setdefault(rel, []).append((old, group, globs))

    rows, tot, files = [], 0, 0
    for rel in sorted(per_file):
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            raise SystemExit("[handfix] missing file: %s" % rel)
        blob = open(p, "rb").read()
        orig = blob
        n_file = 0
        # longest literal first, so a rule can never eat a longer sibling
        for old, group, globs in sorted(per_file[rel], key=lambda r: -len(r[0])):
            new = "dataset/" + group + "/" + old[len("dataset/"):]
            n = blob.count(old.encode())
            if n == 0:
                raise SystemExit("[handfix] rule never matched: %s  %r" % (rel, old))
            blob = blob.replace(old.encode(), new.encode())
            rows.append((rel, old, new, str(n)))
            n_file += n
        tot += n_file
        files += 1
        if apply_changes and blob != orig:
            bak = p + BAK_SUFFIX
            if not os.path.exists(bak):          # pre-move baseline, keep the first
                with open(bak, "wb") as fh:
                    fh.write(orig)
            tmp = p + ".handfix.tmp"
            with open(tmp, "wb") as fh:
                fh.write(blob)
            os.replace(tmp, p)

    if apply_changes:
        tmp = REPORT + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("file\told\tnew\tn\n")
            for r in rows:
                fh.write("\t".join(r) + "\n")
        os.replace(tmp, REPORT)
    print("[handfix] mode          : %s" % ("APPLY" if apply_changes else "DRY-RUN"))
    print("[handfix] rules         : %d over %d files" % (len(RULES), files))
    print("[handfix] substitutions : %d" % tot)
    for r in rows:
        print("   %3s  %s\n        %s -> %s" % (r[3], r[0], r[1], r[2]))
    return 0


def inverse_check():
    """inverse(handfixed file) must reproduce its pre-move .pre0827.bak."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rw", os.path.join(REPO, "scripts", "reorg", "rewrite_dataset_paths.py"))
    rw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rw)
    inv = rw.build_inverse_pattern(rw.load_map())
    files = sorted({r for r, _, _, _ in RULES})
    ok = bad = nobak = 0
    for rel in files:
        p = os.path.join(REPO, rel)
        bak = p + BAK_SUFFIX
        if not os.path.exists(bak):
            nobak += 1
            print("    NO BACKUP " + rel)
            continue
        back = inv.sub(b"dataset/", open(p, "rb").read())
        if back == open(bak, "rb").read():
            ok += 1
        else:
            bad += 1
            print("    MISMATCH  " + rel)
    print("[handfix] files            : %d" % len(files))
    print("[handfix] inverse-identical: %d   mismatched: %d   no backup: %d"
          % (ok, bad, nobak))
    good = (bad == 0 and nobak == 0 and ok == len(files))
    print("HANDFIX-INVERSE-CHECK " + ("PASS" if good else "FAIL"))
    return 0 if good else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--inverse-check", action="store_true")
    a = ap.parse_args()
    if a.inverse_check:
        return inverse_check()
    return apply_rules(a.apply)


if __name__ == "__main__":
    sys.exit(main())
