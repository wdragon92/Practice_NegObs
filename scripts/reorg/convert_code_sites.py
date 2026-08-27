#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 -- convert the flat `dataset/<round>` CODE sites to the round helper.

The 0827 reorg regrouped `dataset/<round>` into `dataset/<group>/<round>`.
S2's string rewrite fixed every path that was spelled out in full. What it
could not fix is a path BUILT from a variable:

    os.path.join(REPO, "dataset", run, "*", scene, "variation.json")
    os.path.join(DS, f"{stem}_{arm}", split, scene)

A name-keyed rewriter cannot see those, and after the move they resolve to a
directory that does not exist -- `glob()` returns `[]`, `isdir()` returns
False, and the caller reports "0 frames" or "MISSING" instead of failing.
That silent-empty failure is the whole risk of this reorg (survey B ss6.3 R3).

What this script does, per file, is a surgical text edit -- NOT a reformat:

    os.path.join(<ROOT>, "dataset", <expr>, ...)  ->  os.path.join(round_dir_or_flat(<expr>), ...)
    os.path.join(<DSCONST>,          <expr>, ...)  ->  os.path.join(round_dir_or_flat(<expr>), ...)
    os.path.isdir(round_dir_or_flat(<expr>))       ->  has_round(<expr>)

Only the span from the opening paren through the round argument is replaced;
everything after it (including line breaks) is kept verbatim, with the
continuation lines re-indented by the length delta so the call still lines up.

`round_dir_or_flat` and not `round_dir`: every one of these sites already has
its own "this round is absent" branch (a MISSING row, a `[skip]`, a `None`
return the caller checks). Keeping that branch preserves behaviour for a round
that genuinely does not exist, while an EXISTING round is now found wherever it
lives. Sites where a missing round is a bug get `round_dir` by hand instead.

usage
  python3 scripts/reorg/convert_code_sites.py --dry-run     # counts, writes nothing
  python3 scripts/reorg/convert_code_sites.py --apply       # edits + .s3.bak per file
"""
from __future__ import annotations

import argparse
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# file -> the name of its dataset-ROOT constant, or None when the site spells
# the root as `<REPO>, "dataset"`.  ("REPO" means the two-element form.)
TARGETS = {
    "experiments/nightrun_0820/ctrl_dressing/hash_gate.py": "REPO",
    "experiments/weekend_0823/cue_audit/gates_cueoff.py": "REPO",
    "experiments/weekend_0823/cue_audit/render_mass.py": "DS",
    "experiments/weekend_0823/cue_audit/g2_adjudicate.py": "DS",
    "experiments/weekend_0823/cue_audit/smoke_summarize.py": "REPO",
    "experiments/weekend_0823/cue_audit/pixel_mass.py": "REPO",
    "experiments/weekend_0823/rt_response/code/f7b_noisefloor.py": "DS",
    "experiments/weekend_0823/c2_rootcause/c2_audit.py": "REPO",
    "experiments/v3_0823/code/w1b_verify.py": "REPO",
    "experiments/v3_0823/code/w1b2_segfill.py": "REPO",
    "experiments/v3_0823/code/w1b2_repro_control.py": "REPO",
    "experiments/v3_0823/code/g7_gate_degenerate.py": "REPO",
    "experiments/v3_0823/code/g7_make_shadow.py": "DS",
    "experiments/v3_0823/code/g7_variantB.py": "DS",
    "experiments/v3_0823/code/g7_pairing_audit.py": "DS",
    "experiments/v3_0823/code/g7_scan_all_boost.py": "REPO",
    "experiments/v3_0823/code/w1d_fuse.py": "REPO",
    "experiments/v3_0823/code/w1d_verify.py": "REPO",
    "experiments/v3_0823/code/w1d_readjudicate.py": "REPO",
    "experiments/v3_0823/code/w1c_datum.py": "REPO",
    "experiments/v3_0823/code/w1c_verify.py": "REPO",
    "experiments/v3_0823/code/w1c_hashgate.py": "REPO",
    "experiments/v3_0823/code/w1c_labeler_boundary.py": "REPO",
    "experiments/v3_0823/code/w1b_fuse.py": "REPO",
    "experiments/v3_0823/code/w1b_label.py": "REPO",
    "experiments/v3_0823/code/w1b_rimpact.py": "REPO",
    "experiments/v3_0823/code/w2_gpu_account.py": "REPO",
    "experiments/v3_0823/code/w3_gpu_account.py": "REPO",
    "experiments/v3_0823/code/w3_manifest.py": "REPO",
    "experiments/v3_0823/code/w3_verify.py": "REPO",
    "experiments/v3_0823/code/w0_classify.py": "REPO",
    "experiments/v3_0823/code/build_corpus_v3.py": "DATA",
    "experiments/v3_0823/code/cue_extent_audit.py": "DATA",
}

CALL = "os.path.join("

# --------------------------------------------------------------------------- #
# import block injected into every converted file, after its REPO constant
# --------------------------------------------------------------------------- #
IMPORT_TMPL = (
    "\n"
    "# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is\n"
    "# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.\n"
    "{pre}"
    "sys.path.insert(0, {repo})                              # noqa: E402\n"
    "from variation_kit import {names}   # noqa: E402\n")

REPO_LITERAL = '"/home/vislab/Desktop/work_sy/Practice_NegObs"'
A_PLAIN = "REPO = " + REPO_LITERAL + "\n"
A_UP4 = ("REPO = os.path.dirname(os.path.dirname(os.path.dirname(\n"
         "    os.path.dirname(os.path.abspath(__file__)))))\n")
UP4 = ("os.path.dirname(os.path.dirname(os.path.dirname(\n"
       "    os.path.dirname(os.path.abspath(__file__)))))")

# rel -> (anchor the block goes AFTER, extra names, extra lines before sys.path,
#         expression that evaluates to the repo root)
IMPORTS = {}
for rel in [
    "experiments/weekend_0823/cue_audit/render_mass.py",
    "experiments/weekend_0823/cue_audit/g2_adjudicate.py",
    "experiments/weekend_0823/cue_audit/smoke_summarize.py",
    "experiments/weekend_0823/cue_audit/pixel_mass.py",
    "experiments/weekend_0823/c2_rootcause/c2_audit.py",
    "experiments/v3_0823/code/w1b_verify.py",
    "experiments/v3_0823/code/w1b2_segfill.py",
    "experiments/v3_0823/code/g7_gate_degenerate.py",
    "experiments/v3_0823/code/g7_make_shadow.py",
    "experiments/v3_0823/code/g7_variantB.py",
    "experiments/v3_0823/code/g7_pairing_audit.py",
    "experiments/v3_0823/code/g7_scan_all_boost.py",
    "experiments/v3_0823/code/w1d_fuse.py",
    "experiments/v3_0823/code/w1d_verify.py",
    "experiments/v3_0823/code/w1d_readjudicate.py",
    "experiments/v3_0823/code/w1c_datum.py",
    "experiments/v3_0823/code/w1c_verify.py",
    "experiments/v3_0823/code/w1c_labeler_boundary.py",
    "experiments/v3_0823/code/w1b_fuse.py",
    "experiments/v3_0823/code/w1b_label.py",
    "experiments/v3_0823/code/w1b_rimpact.py",
    "experiments/v3_0823/code/w0_classify.py",
    "experiments/v3_0823/code/build_corpus_v3.py",
    "experiments/v3_0823/code/cue_extent_audit.py",
]:
    IMPORTS[rel] = (A_PLAIN, "round_dir_or_flat", "", "REPO")
for rel in ["experiments/v3_0823/code/w2_gpu_account.py",
            "experiments/v3_0823/code/w3_gpu_account.py",
            "experiments/v3_0823/code/w1c_hashgate.py",
            "experiments/v3_0823/code/w3_manifest.py"]:
    IMPORTS[rel] = (A_UP4, "round_dir_or_flat", "", "REPO")
IMPORTS["experiments/v3_0823/code/w3_verify.py"] = (
    "REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))\n",
    "round_dir_or_flat", "", "REPO")
IMPORTS["experiments/nightrun_0820/ctrl_dressing/hash_gate.py"] = (
    'REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))\n',
    "round_dir_or_flat, rounds_matching", "", "REPO")
IMPORTS["experiments/weekend_0823/cue_audit/gates_cueoff.py"] = (
    A_PLAIN, "round_dir_or_flat, rounds_matching", "", "REPO")
IMPORTS["experiments/v3_0823/code/w1b2_repro_control.py"] = (
    A_PLAIN, "has_round, round_dir_or_flat", "import sys\n", "REPO")
IMPORTS["experiments/weekend_0823/rt_response/code/f7b_noisefloor.py"] = (
    'REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))\n',
    "round_dir_or_flat", "import sys\n", "REPO")
IMPORTS["experiments/weekend_0823/redteam/r4_pixdiff.py"] = (
    "import numpy as np\nfrom PIL import Image\n",
    "DATASET_ROOT, round_dir_or_flat", "", UP4)
IMPORTS["experiments/v3_0823/code/h12_gates.py"] = (
    "import numpy as np\n", "round_dir_or_flat", "", UP4)


# --------------------------------------------------------------------------- #
# sites the parser deliberately does not touch (prefix globs, f-string paths,
# a hardcoded absolute root, a helper that takes the root as an argument)
# --------------------------------------------------------------------------- #
# Cosmetic re-wraps AFTER the conversion: `round_dir_or_flat(x)` is shorter
# than `os.path.join(<root>, "dataset", x`, so a call that used to be split
# over two lines collapses onto one that is now over 99 columns. Same code,
# re-wrapped. (Applied last; they match only the converted text.)
POST_RULES = [
    ("experiments/v3_0823/code/w2_gpu_account.py",
     '        for vp in sorted(glob.glob(os.path.join(round_dir_or_flat(st), "*", "*", "variation.json"))):',
     '        for vp in sorted(glob.glob(os.path.join(\n'
     '                round_dir_or_flat(st), "*", "*", "variation.json"))):', 1),
    ("experiments/v3_0823/code/w3_gpu_account.py",
     '        for vp in sorted(glob.glob(os.path.join(round_dir_or_flat(st), "*", "*", "variation.json"))):',
     '        for vp in sorted(glob.glob(os.path.join(\n'
     '                round_dir_or_flat(st), "*", "*", "variation.json"))):', 1),
    ("experiments/weekend_0823/cue_audit/render_mass.py",
     '            hit = [d for d in glob.glob(os.path.join(round_dir_or_flat(lineage + "_on"), "*", scene))\n'
     '                   if os.path.isdir(d)]',
     '            hit = [d for d in glob.glob(os.path.join(\n'
     '                round_dir_or_flat(lineage + "_on"), "*", scene))\n'
     '                   if os.path.isdir(d)]', 1),
]

HAND_RULES = [
    # (rel, old, new, expected count)
    ("experiments/nightrun_0820/ctrl_dressing/hash_gate.py",
     '    os.path.basename(p) for p in glob.glob(os.path.join(REPO, "dataset", "260820_boost_*")))',
     '    os.path.basename(p) for p in rounds_matching("260820_boost_"))', 1),
    ("experiments/weekend_0823/cue_audit/gates_cueoff.py",
     '    for d in sorted(glob.glob(os.path.join(REPO, "dataset", prefix + "*"))):',
     '    for d in sorted(rounds_matching(prefix)):', 1),
    ("experiments/weekend_0823/c2_rootcause/c2_audit.py",
     '        for p in glob.glob(os.path.join(REPO, f"dataset/{arm}/*/*/heightmap_meta.json")):',
     '        for p in glob.glob(os.path.join(round_dir_or_flat(arm),\n'
     '                                        "*", "*", "heightmap_meta.json")):', 1),
    ("experiments/weekend_0823/redteam/r4_pixdiff.py",
     'DS = "/home/vislab/Desktop/work_sy/Practice_NegObs/dataset"',
     'DS = DATASET_ROOT                 # 0827: no hardcoded absolute root', 1),
    ("experiments/weekend_0823/redteam/r4_pixdiff.py",
     '        base_a = f"{DS}/260823_cueoff_A/{sub}/{sc}"',
     '        base_a = os.path.join(round_dir_or_flat("260823_cueoff_A"), sub, sc)', 1),
    ("experiments/weekend_0823/redteam/r4_pixdiff.py",
     '            ("A  vs lineage_on ", base_a, f"{DS}/{band}_on"),',
     '            ("A  vs lineage_on ", base_a, round_dir_or_flat(f"{band}_on")),', 1),
    ("experiments/weekend_0823/redteam/r4_pixdiff.py",
     '             f"{DS}/{band}_off"),',
     '             round_dir_or_flat(f"{band}_off")),', 1),
    # cue_extent_audit's registry scan globs by PATTERN, not by prefix, and one
    # of the three passes the pattern in a variable -- which the parser could
    # not see, so it wrongly turned it into a round lookup. All three go to
    # rounds_matching(), which matches the round NAME with fnmatch.
    ("experiments/v3_0823/code/cue_extent_audit.py",
     "from variation_kit import round_dir_or_flat   # noqa: E402",
     "from variation_kit import round_dir_or_flat, rounds_matching   # noqa: E402", 1),
    ("experiments/v3_0823/code/cue_extent_audit.py",
     '            for d in sorted(glob.glob(os.path.join(DATA, pat))):',
     '            for d in rounds_matching(pat):', 1),
    ("experiments/v3_0823/code/cue_extent_audit.py",
     '        for d in sorted(glob.glob(os.path.join(DATA, "*reg_[ABCD]"))):',
     '        for d in rounds_matching("*reg_[ABCD]"):', 1),
    ("experiments/v3_0823/code/cue_extent_audit.py",
     '        for d in sorted(glob.glob(os.path.join(DATA, "*_v3p5_*"))):',
     '        for d in rounds_matching("*_v3p5_*"):', 1),
    ("experiments/v3_0823/code/h12_gates.py",
     'def arm_dir(root, stamp, arm, split, scene):\n'
     '    return os.path.join(root, f"{stamp}_{arm}", split, scene)',
     'def arm_dir(root, stamp, arm, split, scene):\n'
     '    # 0827: `root` is the dataset ROOT, which did not move; the round\n'
     '    # inside it may be flat or grouped, so it is resolved by NAME.\n'
     '    return os.path.join(round_dir_or_flat(f"{stamp}_{arm}", root),\n'
     '                        split, scene)', 1),
]



def _split_args(text, open_idx):
    """Arg spans of the call whose '(' is at `open_idx`. -> (args, close_idx).

    args = [(start, end)] character spans, depth-0 comma separated. Quote- and
    bracket-aware; f-strings are just strings here, which is all we need.
    """
    i = open_idx + 1
    depth = 0
    args, start = [], i
    quote = None
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if text.startswith(quote, i):
                i += len(quote)
                quote = None
                continue
            i += 1
            continue
        if c in "\"'":
            quote = text[i:i + 3] if text[i:i + 3] in ('"""', "'''") else c
            i += len(quote)
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                args.append((start, i))
                return args, i
            depth -= 1
        elif c == "," and depth == 0:
            args.append((start, i))
            start = i + 1
        i += 1
    raise ValueError("unterminated call at %d" % open_idx)


def _reindent(block, delta):
    """Shift the leading whitespace of every line but the first by `delta`."""
    if delta == 0:
        return block
    out = [block.split("\n")[0]]
    for line in block.split("\n")[1:]:
        stripped = line.lstrip(" ")
        ind = len(line) - len(stripped)
        out.append(" " * max(0, ind + delta) + stripped)
    return "\n".join(out)


def convert(text, root_const):
    """-> (new_text, n_sites). One pass, left to right, longest call first."""
    n = 0
    i = 0
    out = []
    while True:
        j = text.find(CALL, i)
        if j < 0:
            out.append(text[i:])
            break
        open_idx = j + len(CALL) - 1
        try:
            args, close_idx = _split_args(text, open_idx)
        except ValueError:
            out.append(text[i:j + len(CALL)])
            i = j + len(CALL)
            continue
        exprs = [text[a:b].strip() for a, b in args]
        rnd_idx = None
        if root_const == "REPO":
            if len(exprs) >= 3 and exprs[0] == "REPO" and exprs[1] == '"dataset"':
                rnd_idx = 2
        elif len(exprs) >= 2 and exprs[0] == root_const:
            rnd_idx = 1
        if (rnd_idx is None or not exprs[rnd_idx]
                or "*" in exprs[rnd_idx] or exprs[rnd_idx] == "pat"):
            # "*" in the round argument means this is a PREFIX GLOB
            # (`glob(<root>/<prefix>*)`), not one round. Those need
            # rounds_matching() and are in HAND_RULES, not here.
            out.append(text[i:j + len(CALL)])
            i = j + len(CALL)
            continue
        expr = " ".join(exprs[rnd_idx].split())
        new_call = "round_dir_or_flat(%s)" % expr
        out.append(text[i:j])
        if rnd_idx == len(exprs) - 1:
            # nothing after the round: the whole join() collapses
            old_span = text[j:close_idx + 1]
            out.append(_reindent(new_call, len(new_call) - len(old_span)))
            i = close_idx + 1
        else:
            end = args[rnd_idx][1]                 # index of the following comma
            old_span = text[j:end]
            new_span = CALL + new_call
            out.append(_reindent(new_span, len(new_span) - len(old_span)))
            i = end
        n += 1
    new = "".join(out)
    # os.path.isdir(round_dir_or_flat(x)) is exactly has_round(x), and says so.
    n_isdir = 0
    marker = "os.path.isdir(round_dir_or_flat("
    while True:
        k = new.find(marker)
        if k < 0:
            break
        inner = k + len("os.path.isdir(")
        args, close_inner = _split_args(new, inner + len("round_dir_or_flat") )
        expr = new[args[0][0]:args[0][1]].strip()
        # the outer isdir( ... ) closes one char after the inner call
        assert new[close_inner + 1] == ")", new[close_inner - 20:close_inner + 5]
        new = new[:k] + "has_round(%s)" % expr + new[close_inner + 2:]
        n_isdir += 1
    return new, n, n_isdir


def apply_rules(rules, texts, log, key="hand"):
    for rel, old, new, want in rules:
        t = texts.get(rel)
        if t is None:
            t = io.open(os.path.join(REPO, rel), encoding="utf-8", newline="").read()
        n = t.count(old)
        assert n == want, "%s: hand rule matched %d times, want %d\n%s" % (
            rel, n, want, old[:120])
        texts[rel] = t.replace(old, new, want)
        log.setdefault(rel, {}).setdefault(key, 0)
        log[rel][key] += want


def inject_imports(texts, log):
    for rel, (anch, names, pre, repo_expr) in sorted(IMPORTS.items()):
        t = texts.get(rel)
        if t is None:
            t = io.open(os.path.join(REPO, rel), encoding="utf-8", newline="").read()
        assert t.count(anch) == 1, "%s: anchor x%d" % (rel, t.count(anch))
        blk = IMPORT_TMPL.format(pre=pre, names=names, repo=repo_expr)
        texts[rel] = t.replace(anch, anch + blk, 1)
        log.setdefault(rel, {})["import"] = names


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)

    texts, log = {}, {}
    tot = tot_isdir = 0
    for rel, root_const in sorted(TARGETS.items()):
        p = os.path.join(REPO, rel)
        src = io.open(p, encoding="utf-8", newline="").read()
        new, n, n_isdir = convert(src, root_const)
        if n:
            texts[rel] = new
            log[rel] = dict(auto=n, isdir=n_isdir)
            tot += n
            tot_isdir += n_isdir

    apply_rules(HAND_RULES, texts, log)
    inject_imports(texts, log)
    apply_rules(POST_RULES, texts, log, "rewrap")

    hand = sum(v.get("hand", 0) for v in log.values())
    for rel in sorted(log):
        v = log[rel]
        print("  auto %2d  hand %d  isdir %d  import[%s]  %s" % (
            v.get("auto", 0), v.get("hand", 0), v.get("isdir", 0),
            v.get("import", "-"), rel))
    print("\n%d files · %d auto sites (%d isdir) · %d hand sites · %d import blocks"
          % (len(log), tot, tot_isdir, hand, len(IMPORTS)))

    if a.apply:
        for rel, new in sorted(texts.items()):
            p = os.path.join(REPO, rel)
            src = io.open(p, encoding="utf-8", newline="").read()
            io.open(p + ".s3.bak", "w", encoding="utf-8", newline="").write(src)
            tmp = p + ".s3tmp"
            io.open(tmp, "w", encoding="utf-8", newline="").write(new)
            os.replace(tmp, p)
        print("applied to %d files (.s3.bak kept)" % len(texts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
