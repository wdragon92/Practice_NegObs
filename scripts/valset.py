#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validation corpora for `regression_check.py` - the GRAZE series definitions, in code.

**Why this file exists.** The two corpora that license every GRAZE threshold in the
project have now been reconstructed from scratch **twice**, because the only record of
them was prose plus a scratchpad driver that died with its session:

  * `graze_recalibration_v1.md` §5 recorded the per-series **counts** but not the pair
    membership, so `w2_tools_v1.md` §4.3 had to rebuild the membership and prove the
    rebuild by reproducing the published v2 outcome.
  * `cleanup_lookcheck_v1.md` §4 had to rebuild it a second time to prove the round
    deletion changed nothing, and closes with the recommendation this file implements:
    *"promote the driver to `scripts/valset.py` so the corpora stop being a scratchpad
    artefact."*

So the membership lives here, the expected outcome lives here next to it, and
`--check` turns "the corpora still reproduce" into a command instead of an errand.

The corpora
  `history`  the judged-round ladder - what the checker must keep detecting.
  `fp`       the false-positive control - rounds that changed the look but not the
             geometry, where the checker must stay quiet.
  `t3`       the two pairs T3 required v2.1 to silence (`w2_tools_v1.md` §4.2).

Reading the counts
  A "cut" is one GRAZE-eligible view present in **both** rounds of a pair. Pairs whose
  rounds are missing on disk are skipped silently - `look_check/**` is gitignored, so a
  machine that never rendered a series simply reports fewer cuts. That is why
  `--check` compares against `EXPECTED` per series and prints what is absent, rather
  than asserting a single global total.

Usage
    python3 scripts/valset.py                      # all three corpora, table + summary
    python3 scripts/valset.py --corpus fp --check  # exit 1 if the series drifts
    python3 scripts/valset.py --json out.json --jobs 8
Dependencies: `regression_check` (numpy + PIL). **GPU 0 · no writes outside --json.**
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import regression_check as rc  # noqa: E402


def _scenes():
    """Every scene directory under `look_check/` (`scene*` also matches C/D/N batch1)."""
    return sorted(os.path.basename(p)
                  for p in glob.glob(os.path.join(ROOT, "look_check", "scene*"))
                  if os.path.isdir(p))


SCENES = _scenes()


def _P(series, pairs):
    return [(series, s, b, a) for (s, b, a) in pairs]


# ---------------------------------------------------------------------------
# History set - `w2_tools_v1.md` §4.3: 94 cuts (the doc's own enumeration said 92;
# the +2 are PASS under both versions and affect no conclusion).
# ---------------------------------------------------------------------------
HISTORY = (_P("v6->v7", [(s, "v6_rt", "v7_rt") for s in SCENES]) +
           _P("v7->v8", [(s, "v7_rt", "v8_rt") for s in SCENES]))

# ---------------------------------------------------------------------------
# False-positive set - five series, `w2_tools_v1.md` §4.3 / `cleanup_lookcheck_v1.md` §4.
#
# The P4 series is the near-field fix ladder, and the round list that pins it is
# `cleanup_lookcheck_v1.md` §1.1: `sceneC2/{r2_on,balust,leaf3d,handrail,fix1}` +
# `scene05/{r2_on,shrub,facade}`. Walked as two chronological chains that is 4 + 2 = 6
# pairs x 3 GRAZE cuts = **18**, the count that report measured. (The scratchpad driver
# this file replaces guessed `sceneC2/r2` and `scene05/r3` instead - two rounds that do
# not exist - and so under-counted the series by 5.)
# ---------------------------------------------------------------------------
FP = (_P("mode", [("scene07", "v8_rt", "v8_pt"),
                  ("scene07", "scene07_ptlegacy", "scene07_ptfast"),
                  ("sceneD3", "sceneD3_ptlegacy", "sceneD3_ptfast")] +
                 [(s, "p2dark_legacy", "p2dark_fast64") for s in SCENES] +
                 [(s, "p2dark_fast64", "p2dark_fast256") for s in SCENES]) +
      _P("lookAB", [(s, f"p2g{i}_off", f"p2g{i}_on")
                    for s in SCENES for i in (1, 2, 3)] +
                   [(s, "p2rf_off", "p2rf_on") for s in SCENES] +
                   [(s, "p2ctrl_a", "p2ctrl_b") for s in SCENES] +
                   [(s, "p2det_a", "p2det_b") for s in SCENES] +
                   [(s, "p2c_a", "p2c_b") for s in SCENES] +
                   [(s, "p2mat_before", "p2mat_after") for s in SCENES]) +
      _P("ctx", [(s, "ctx1", "ctx2") for s in SCENES]) +
      _P("real", [(s, "r1_on", "r2_on") for s in SCENES]) +
      _P("P4", [("sceneC2", "r2_on", "balust"), ("sceneC2", "balust", "leaf3d"),
                ("sceneC2", "leaf3d", "handrail"), ("sceneC2", "handrail", "fix1"),
                ("scene05", "r2_on", "shrub"), ("scene05", "shrub", "facade")]))

# ---------------------------------------------------------------------------
# T3 - the two pairs v2.1 was required to silence. These are also FP members; they are
# listed separately because the requirement is per-cut, not per-series.
# ---------------------------------------------------------------------------
T3 = _P("T3", [("scene13", "v6_rt", "v7_rt"), ("scene07", "r1_on", "r2_on")])

CORPORA = {"history": HISTORY, "fp": FP, "t3": T3}

# ---------------------------------------------------------------------------
# Expected outcome under regression_check v2.1, `[measured]` and cross-checked against
# `w2_tools_v1.md` §4.4 and `cleanup_lookcheck_v1.md` §4. `cuts` is the count on a
# machine holding the full round tree; `--check` warns when the count is lower (rounds
# absent) and fails when a verdict count moves.
# ---------------------------------------------------------------------------
EXPECTED = {
    "history": dict(cuts=94, fail=1, warn=2,
                    series={"v6->v7": 68, "v7->v8": 26}),
    "fp": dict(cuts=156, fail=0, warn=0,
               series={"mode": 12, "lookAB": 42, "ctx": 44, "real": 40, "P4": 18}),
    "t3": dict(cuts=None, fail=0, warn=0, series={}),
}

# The three history firings v2.1 keeps, and which `w2_tools_v1.md` §4.4 defends as
# genuine. Identified by (scene, view) - the spec value is printed for eyeballing only.
EXPECTED_FIRINGS = {
    ("history", "scene18", "preset_h0.3_d2"): ("FAIL", 67.6),
    ("history", "scene17", "preset_h0.3_d2"): ("WARN", 10.2),
    ("history", "scene19", "preset_h0.3_d5"): ("WARN", 11.1),
}

# The two cuts that must be quiet (they fired under v2 and must not under v2.1).
EXPECTED_QUIET = [("scene13", "v6_rt", "v7_rt", "preset_h0.3_d5"),
                  ("scene07", "r1_on", "r2_on", "preset_h0.3_d2")]


# ---------------------------------------------------------------------------
def jobs_for(pairs):
    """(series, tag, scene, view, before_entry, after_entry) for every shared GRAZE cut."""
    out = []
    for series, scene, b, a in pairs:
        bd = os.path.join(ROOT, "look_check", scene, b)
        ad = os.path.join(ROOT, "look_check", scene, a)
        if not (os.path.isdir(bd) and os.path.isdir(ad)):
            continue
        B = rc.index_round(bd, ROOT)
        A = rc.index_round(ad, ROOT)
        for v in sorted(set(A) & set(B)):
            if rc.is_graze_view(v):
                out.append((series, f"{scene}:{b}->{a}", scene, v, B[v], A[v]))
    return out


def missing(pairs):
    """Pairs whose before or after round is not on disk - reported, never fatal."""
    out = []
    for series, scene, b, a in pairs:
        for r in (b, a):
            if not os.path.isdir(os.path.join(ROOT, "look_check", scene, r)):
                out.append((series, scene, r))
                break
    return out


def _run(j):
    series, tag, scene, v, bb, aa = j
    r = rc.check_view(scene, v, bb, aa)
    gz = [i for i in r["issues"] if i["code"] == "GRAZE"]
    sev = gz[0]["sev"] if gz else "PASS"
    m = r["metrics"]
    return dict(series=series, pair=tag, scene=scene, view=v, sev=sev,
                spec=m.get("gz_spec"), agree=m.get("gz_agree"),
                step_b=m.get("gz_step_b"), step_a=m.get("gz_step_a"),
                ratio=m.get("gz_step_ratio"), quiet=m.get("gz_quiet"),
                msg=gz[0]["msg"][:100] if gz else "")


def run(pairs, label, jobs=8, verbose=True):
    js = jobs_for(pairs)
    if not js:
        if verbose:
            print(f"\n=== {label}: 0 cuts on disk")
        return []
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        res = list(ex.map(_run, js, chunksize=2))
    if verbose:
        f = [r for r in res if r["sev"] == "FAIL"]
        w = [r for r in res if r["sev"] == "WARN"]
        i = [r for r in res if r["sev"] == "INFO"]
        print(f"\n=== {label}: {len(res)} GRAZE cuts · "
              f"FAIL {len(f)} · WARN {len(w)} · deferred {len(i)}")
        for r in f + w:
            print(f"  {r['sev']:<5}{r['pair']:<32}{r['view']:<22}"
                  f"spec={r['spec']} agree={r['agree']} "
                  f"step {r['step_b']}->{r['step_a']} ratio={r['ratio']}")
    return res


def check(name, res, verbose=True):
    """Compare one corpus against `EXPECTED`. Returns a list of failure strings."""
    exp = EXPECTED[name]
    bad, notes = [], []
    n_fail = sum(1 for r in res if r["sev"] == "FAIL")
    n_warn = sum(1 for r in res if r["sev"] == "WARN")
    if exp["cuts"] is not None and len(res) != exp["cuts"]:
        notes.append(f"cuts {len(res)} != {exp['cuts']} (rounds absent on this machine?)")
    for s, n in exp["series"].items():
        got = sum(1 for r in res if r["series"] == s)
        if got != n:
            notes.append(f"series {s}: {got} != {n}")
    if n_fail != exp["fail"]:
        bad.append(f"{name}: FAIL {n_fail} != {exp['fail']}")
    if n_warn != exp["warn"]:
        bad.append(f"{name}: WARN {n_warn} != {exp['warn']}")
    if name == "history":
        got = {(name, r["scene"], r["view"]): r["sev"]
               for r in res if r["sev"] in ("FAIL", "WARN")}
        for k, (sev, spec) in EXPECTED_FIRINGS.items():
            if k[0] != name:
                continue
            if got.get(k) != sev:
                bad.append(f"{name}: {k[1]} {k[2]} expected {sev} (spec {spec}), "
                           f"got {got.get(k, 'PASS')}")
        for k, sev in got.items():
            if k not in EXPECTED_FIRINGS:
                bad.append(f"{name}: unexpected {sev} at {k[1]} {k[2]}")
    if name == "t3":
        for scene, b, a, view in EXPECTED_QUIET:
            hit = [r for r in res
                   if r["scene"] == scene and r["view"] == view
                   and r["pair"] == f"{scene}:{b}->{a}"]
            if not hit:
                notes.append(f"t3: {scene} {view} not on disk")
            elif hit[0]["sev"] in ("FAIL", "WARN"):
                bad.append(f"t3: {scene} {view} must be quiet, got {hit[0]['sev']}")
    if verbose:
        for n in notes:
            print(f"  [note] {n}")
        for b in bad:
            print(f"  [FAIL] {b}")
        if not bad:
            print(f"  [ok] {name}: FAIL {n_fail} · WARN {n_warn} — matches EXPECTED")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corpus", default="all",
                    choices=("all", "history", "fp", "t3"))
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--json", help="machine-readable output path")
    ap.add_argument("--check", action="store_true",
                    help="compare against EXPECTED; exit 1 on a verdict-count change")
    ap.add_argument("--list-missing", action="store_true",
                    help="only print the pairs whose rounds are absent on disk")
    a = ap.parse_args(argv)

    names = ("history", "fp", "t3") if a.corpus == "all" else (a.corpus,)
    if a.list_missing:
        for n in names:
            miss = missing(CORPORA[n])
            print(f"{n}: {len(miss)} pair(s) with an absent round")
            for s, sc, r in miss:
                print(f"   {s:<8}{sc:<10}{r}")
        return 0

    out, bad = {}, []
    labels = dict(history="history ladder (v6->v7 + v7->v8)",
                  fp="false-positive control (5 series)",
                  t3="T3 residual WARN pairs")
    for n in names:
        out[n] = run(CORPORA[n], labels[n], a.jobs)
        if a.check:
            bad += check(n, out[n])
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f"\nJSON -> {a.json}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
