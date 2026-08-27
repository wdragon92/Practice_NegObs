# -*- coding: utf-8 -*-
"""e1_selftest.py -- the three checks the skeleton has to pass on its own.

    python3 e1_selftest.py --scan-consts
        Walks every e1_*.py except e1_const.py and reports every numeric literal
        that is not in e1_const.STRUCTURAL_OK. Brief §3-P1: "기록 없이 쓰인 상수
        0건" is a gate condition, and this is how it is measured rather than
        asserted.

    python3 e1_selftest.py --schema
        Round-trips a synthetic record through the validator, the canonical JSON
        dump and the csv mirror, and checks the §5 tier_now derivation on all
        four cases (empty / external occluder / self only / unresolved).

    python3 e1_selftest.py --ledger
        Cross-checks e1_const.CONSTANTS against CONST_LEDGER.md in both
        directions: no constant missing from the ledger, no stale name in it.

    python3 e1_selftest.py --determinism --frame round:scene:frame.png
        Labels the same frame twice into two directories and compares the
        canonical json BYTE BY BYTE (brief §4 Phase 1 통과수치).
"""

import argparse
import ast
import filecmp
import glob
import hashlib
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e1_const as C          # noqa: E402
import e1_schema as S          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------- #
def scan_consts():
    bad = []
    for path in sorted(glob.glob(os.path.join(HERE, "e1_*.py"))):
        if os.path.basename(path) == "e1_const.py":
            continue
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src, path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                    and not isinstance(node.value, bool):
                v = node.value
                if v in C.STRUCTURAL_OK or -v in C.STRUCTURAL_OK:
                    continue
                bad.append((os.path.basename(path), node.lineno, v))
    print("[selftest] unledgered numeric literals: %d" % len(bad))
    for f, ln, v in bad:
        print("   ! %s:%d  %r" % (f, ln, v))
    return 0 if not bad else 1


# --------------------------------------------------------------------------- #
def schema_check():
    fails = []

    def mk(occ_flag, frac=None):
        return S.EdgeRecord(edge_id="e00", pts_3d=[[0.0, 0.0, 0.0]],
                            occluder=S.Occluder(flag=occ_flag, prim="p",
                                                occl_frac=frac))

    cases = [([], "NEG"),
             ([mk(True, 0.5)], "H_cand"),
             ([mk(False, 0.0)], "VE_raw"),
             ([mk(None)], "VE_raw")]
    for edges, want in cases:
        got = S.derive_tier_now(edges)
        if got != want:
            fails.append("tier_now: wanted %s got %s" % (want, got))

    rec = S.FrameRecord(frame_id="f", pose_id="p", scene_id="s", world_id="s",
                        domain="stair", rgb_path="r.png", depth_path="d.npy",
                        tier_now="VE_raw", edges=[mk(False, 0.0)])
    fails += ["validator: %s" % p for p in S.validate(rec)]

    bad = S.FrameRecord(frame_id="", pose_id="p", scene_id="s", world_id="s",
                        domain="nope", rgb_path="r", depth_path="d",
                        tier_now="V", tier_final="E")
    if len(S.validate(bad)) < 4:
        fails.append("validator did not catch the deliberately bad record")

    with tempfile.TemporaryDirectory() as td:
        b1 = S.dump_json([rec], os.path.join(td, "a.json"))
        b2 = S.dump_json([rec], os.path.join(td, "b.json"))
        if b1 != b2:
            fails.append("json dump is not stable within a process")
        S.dump_csv([rec, S.FrameRecord(frame_id="g", pose_id="p", scene_id="s",
                                       world_id="s", domain="stair",
                                       rgb_path="r", depth_path="d",
                                       tier_now="NEG")],
                   os.path.join(td, "a.csv"))
        rows = open(os.path.join(td, "a.csv"), encoding="utf-8").read().splitlines()
        if len(rows) != 3:
            fails.append("csv mirror: wanted header + 2 rows, got %d" % len(rows))

    print("[selftest] schema failures: %d" % len(fails))
    for f in fails:
        print("   !", f)
    return 0 if not fails else 1


# --------------------------------------------------------------------------- #
def ledger_check():
    """Every key of e1_const.CONSTANTS must appear in CONST_LEDGER.md, and the
    ledger must not name a constant the code does not have.

    This is the mechanical half of "기록 없이 쓰인 상수 0건": --scan-consts proves
    no constant hides in the code, this proves none hides from the ledger.
    """
    path = os.path.abspath(os.path.join(HERE, "..", "CONST_LEDGER.md"))
    if not os.path.exists(path):
        print("[selftest] CONST_LEDGER.md missing at %s" % path)
        return 1
    text = open(path, encoding="utf-8").read()
    missing = [k for k in C.CONSTANTS if k not in text]
    named = set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", text))
    extra = sorted(n for n in named if n not in C.CONSTANTS
                   and n not in {"CONST_LEDGER", "PYTHONNOUSERSITE", "NEG",
                                 "VE_RAW", "STRUCTURAL_OK", "CONSTANTS"})
    print("[selftest] ledger: %d constants, missing from CONST_LEDGER.md: %d, "
          "named there but absent from code: %d"
          % (len(C.CONSTANTS), len(missing), len(extra)))
    for k in missing:
        print("   ! missing:", k)
    for k in extra:
        print("   ! stale:", k)
    return 0 if not (missing or extra) else 1


# --------------------------------------------------------------------------- #
def determinism(spec):
    import e1_label_frame as LF
    import e1_visibility as V
    rnd, scene, frame = spec.split(":")
    # ONE output directory for both runs: the mask output location is an INPUT
    # to the run (it is echoed into int_mask_path), so varying it would make the
    # test fail for a reason that has nothing to do with determinism.
    td = tempfile.mkdtemp(prefix="e1_det_")
    outs = []
    for i in range(2):
        rec, _ = LF.label_frame(rnd, scene, frame, td,
                                classifier=V.PrimClassifier.load())
        p = os.path.join(td, "run%d.json" % i)
        S.dump_json([rec], p)
        outs.append(p)
    same = filecmp.cmp(outs[0], outs[1], shallow=False)
    h = [hashlib.sha256(open(p, "rb").read()).hexdigest()[:C.SHA_PREFIX_LEN] for p in outs]
    print("[selftest] determinism %s : byte-identical=%s  sha16=%s / %s"
          % (spec, same, h[0], h[1]))
    return 0 if same else 1


# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-consts", action="store_true")
    ap.add_argument("--schema", action="store_true")
    ap.add_argument("--ledger", action="store_true")
    ap.add_argument("--determinism", action="store_true")
    ap.add_argument("--frame", help="round:scene:frame.png for --determinism")
    a = ap.parse_args(argv)
    rc = 0
    if a.scan_consts:
        rc |= scan_consts()
    if a.schema:
        rc |= schema_check()
    if a.ledger:
        rc |= ledger_check()
    if a.determinism:
        if not a.frame:
            raise SystemExit("[e1] --determinism needs --frame")
        rc |= determinism(a.frame)
    if not (a.scan_consts or a.schema or a.ledger or a.determinism):
        rc |= scan_consts()
        rc |= schema_check()
        rc |= ledger_check()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
