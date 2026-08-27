#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 -- READ-ONLY smoke of the sites that used to fail SILENTLY (survey B R3).

The 0827 regrouping's real danger was never a crash. It was a `glob()` over a
flat round path returning `[]` and the caller reporting "0 frames" or
"gate PASS on an empty set". This script loads each converted module and calls
the converted resolution for the rounds that module actually targets, then
asserts a NON-ZERO count. Nothing is written; no round is rendered.

    python3 scripts/reorg/smoke_round_sites.py

Each check prints PASS with the count it measured, SKIP with the reason, or
FAIL. Exit code 1 if anything failed or if any check returned zero.
"""
from __future__ import annotations

import glob
import importlib.util
import os
import sys
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
import variation_kit as vk                                        # noqa: E402

_LOADED = {}

# Three of the modules below do their work at MODULE level and write their
# artifact as a side effect of being imported. This script must not leave a
# mark on the tree, so those artifacts are read into memory before anything is
# loaded and written back byte-for-byte at the end. `main()` asserts the
# restore. (Measured, not guessed: a sha1 sweep of 11,852 files before and
# after a run showed exactly these two changing mtime and nothing changing
# content.)
SIDE_EFFECT_FILES = [
    "experiments/v3_0823/w1b_rimpact.json",          # w1b_rimpact.py
    "experiments/weekend_0823/rt_response/f7b_noisefloor.json",   # f7b_noisefloor.py
]
_PROTECTED = {}


def protect():
    for rel in SIDE_EFFECT_FILES:
        p = os.path.join(REPO, rel)
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                _PROTECTED[rel] = fh.read()


def restore():
    """Put the side-effect artifacts back. -> list of the ones that had moved."""
    moved = []
    for rel, blob in _PROTECTED.items():
        p = os.path.join(REPO, rel)
        with open(p, "rb") as fh:
            now = fh.read()
        if now != blob:
            tmp = p + ".smoketmp"
            with open(tmp, "wb") as fh:
                fh.write(blob)
            os.replace(tmp, p)
            moved.append(rel)
        with open(p, "rb") as fh:
            assert fh.read() == blob, rel
    return moved


def load(rel, name=None):
    """Load a module by file path (they are scripts, not a package)."""
    if rel in _LOADED:
        return _LOADED[rel]
    path = os.path.join(REPO, rel)
    name = name or ("_smoke_" + os.path.basename(rel)[:-3])
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    cwd = os.getcwd()
    os.chdir(REPO)
    try:
        spec.loader.exec_module(m)
    finally:
        os.chdir(cwd)
    _LOADED[rel] = m
    return m


RESULTS = []


class Skip(Exception):
    """Raised by a check that cannot run here; the message is the reason."""


def check(label, fn):
    """A check returns what it MEASURED. Empty/zero is a FAIL, never a pass."""
    try:
        n = fn()
    except Skip as e:
        RESULTS.append(("SKIP", label, str(e)))
        return
    except Exception:
        RESULTS.append(("FAIL", label, traceback.format_exc().strip().split("\n")[-1]))
        return
    if n:
        RESULTS.append(("PASS", label, str(n)))
    else:
        RESULTS.append(("FAIL", label, "returned 0 / empty -- SILENT EMPTY"))


# --------------------------------------------------------------------------- #
# 1. the two prefix globs (rounds_matching)
# --------------------------------------------------------------------------- #
def s_hash_gate_protected():
    m = load("experiments/nightrun_0820/ctrl_dressing/hash_gate.py")
    boost = [r for r in m.PROTECTED if r.startswith("260820_boost_")]
    assert len(m.PROTECTED) == len(boost) + 2, m.PROTECTED
    for r in boost:
        assert os.path.isdir(m._round_files.__globals__["round_dir_or_flat"](r)), r
    return "PROTECTED=%d (boost %d)" % (len(m.PROTECTED), len(boost))


def s_gates_cueoff_round_dirs():
    m = load("experiments/weekend_0823/cue_audit/gates_cueoff.py")
    d = m.round_dirs("260823_cueoff")
    scenes = sum(len(v) for v in d.values())
    return "%d (stem,arm) units · %d scene dirs" % (len(d), scenes)


# --------------------------------------------------------------------------- #
# 2. the variation.json globs -- `sdir(run, scene)` and its twins
# --------------------------------------------------------------------------- #
SDIR_SITES = [
    ("experiments/v3_0823/code/w1b_verify.py", "sdir", "260826_v3w1_lib_B", "scene01"),
    ("experiments/v3_0823/code/w1b_label.py", "sdir", "260826_v3w1_lib_B", "scene01"),
    ("experiments/v3_0823/code/w1b_fuse.py", "sdir", "260826_v3w1_lib_B", "scene01"),
    ("experiments/v3_0823/code/w1b2_segfill.py", "sdir", "260826_v3w1_lib_B", "scene01"),
    ("experiments/v3_0823/code/w1b2_repro_control.py", "sdir", "260819_main_on", "scene01"),
    ("experiments/v3_0823/code/w1c_datum.py", "sdir", "260826_v3w1_lib_B", "scene01"),
    ("experiments/v3_0823/code/w1c_verify.py", "sdir", "260826_v3w1_lib_B", "scene01"),
    ("experiments/v3_0823/code/w1d_fuse.py", "sdir", "260825_v3w0_cuecls_A", "scene01"),
    ("experiments/v3_0823/code/w1d_verify.py", "sdir", "260825_v3w0_cuecls_A", "scene01"),
    ("experiments/v3_0823/code/w1d_readjudicate.py", "_sdir", "260825_v3w0_cuecls_A", "scene01"),
    ("experiments/v3_0823/code/w0_classify.py", "scene_dir", "260825_v3w0_cuecls_A", "scene01"),
    ("experiments/v3_0823/code/w1c_labeler_boundary.py", "sdir_of", "260819_main_on", "scene01"),
]


def _sdir_check(rel, fname, run, scene):
    def fn():
        m = load(rel)
        f = getattr(m, fname, None)
        if f is None:
            raise Skip("no %s() in this module" % fname)
        d = f(run, scene)
        if not d:
            return 0
        assert os.path.isdir(d), d
        n = len(glob.glob(os.path.join(d, "*.png")))
        return "%s -> %s (%d png)" % (run, os.path.relpath(d, REPO), n)
    return fn


# --------------------------------------------------------------------------- #
# 3. the isdir feature switch, the manifest read, the arm_dir helper
# --------------------------------------------------------------------------- #
def s_repro_control_switch():
    m = load("experiments/v3_0823/code/w1b2_repro_control.py")
    w0, bs = "260825_v3w0_cuecls_A", "260826_v3w1_lib_B_smoke"
    a, b = m.has_round(w0), m.has_round(bs)
    assert a and b, (a, b)
    return "has_round(%s)=%s · has_round(%s)=%s · scenes_of=%d/%d" % (
        w0, a, bs, b, len(m.scenes_of(w0)), len(m.scenes_of(bs)))


def s_w1c_hashgate_unit_dir():
    m = load("experiments/v3_0823/code/w1c_hashgate.py")
    scenes = getattr(m, "SCENES", None) or sorted(getattr(m, "CUT_OVERRIDE", {})) \
        or ["scene01", "scene02", "scene06"]
    hits = [s for s in scenes if m.unit_dir(m.BEFORE_RUN, s)]
    assert len(hits) == len(scenes), (hits, scenes)
    return "%d/%d scenes resolve through %s manifest" % (
        len(hits), len(scenes), m.BEFORE_RUN)


def s_h12_arm_dir():
    m = load("experiments/v3_0823/code/h12_gates.py")
    d = m.arm_dir("dataset", "260823_v3p5_h12probe", "A", "test", "sceneH1")
    assert os.path.isdir(d), d
    return "%s (%d png)" % (os.path.relpath(d, REPO), len(glob.glob(d + "/*.png")))


def s_w3_extra_gates_root():
    m = load("experiments/v3_0823/code/w3_extra_gates.py")
    d = m.G.arm_dir(os.path.join(REPO, "dataset"), "260824_v3w3_extbase",
                    "A", "test", "sceneH1")
    assert os.path.isdir(d), d
    return os.path.relpath(d, REPO)


# --------------------------------------------------------------------------- #
# 4. the g7 / corpus / audit families
# --------------------------------------------------------------------------- #
def s_g7_scene_dirs():
    m = load("experiments/v3_0823/code/g7_pairing_audit.py")
    rdf = m.__dict__["round_dir_or_flat"]
    n = 0
    for r in ("260820_boost_h_on", "260820_boost_h_off", "260819_main_on"):
        d = rdf(r)
        assert os.path.isdir(d), r
        n += len(glob.glob(os.path.join(d, "*", "*", "variation.json")))
    return "%d scene dirs over 3 rounds" % n


def s_build_corpus_v3():
    m = load("experiments/v3_0823/code/build_corpus_v3.py")
    rdf = m.__dict__["round_dir_or_flat"]
    hits = glob.glob(os.path.join(rdf("260826_v3w1_lib_B"), "*", "scene01",
                                  "variation.json"))
    return "%d variation.json for 260826_v3w1_lib_B/scene01" % len(hits)


def s_cue_extent_audit():
    m = load("experiments/v3_0823/code/cue_extent_audit.py")
    rdf = m.__dict__["round_dir_or_flat"]
    n = len(glob.glob(os.path.join(rdf("260826_v3w1_lib_B"), "*", "*",
                                   "*.idseg.npz")))
    return "%d idseg sidecars in 260826_v3w1_lib_B" % n


def s_cue_extent_registry_patterns():
    """cue_extent_audit's registry scan: three fnmatch patterns, not prefixes."""
    m = load("experiments/v3_0823/code/cue_extent_audit.py")
    rm = m.__dict__["rounds_matching"]
    out = []
    for pat in ("*reg_[ABCD]", "*_v3p5_*", "*_v3w1_lib_C*"):
        hits = rm(pat)
        assert all(os.path.isdir(p) for p in hits), pat
        out.append("%s=%d" % (pat, len(hits)))
        assert hits, pat
    return " · ".join(out)


def s_render_mass():
    m = load("experiments/weekend_0823/cue_audit/render_mass.py")
    rdf = m.__dict__["round_dir_or_flat"]
    n = len(glob.glob(os.path.join(rdf("260823_cueoff_A"), "*", "scene*")))
    return "%d scene dirs in 260823_cueoff_A" % n


def s_g2_adjudicate():
    m = load("experiments/weekend_0823/cue_audit/g2_adjudicate.py")
    d = m.arm_dir("260823_cueoff", "B1", "test", "scene12") \
        if hasattr(m, "arm_dir") else None
    if d is None:
        rdf = m.__dict__["round_dir_or_flat"]
        d = os.path.join(rdf("260823_cueoff_B1"), "test", "scene12")
    assert os.path.isdir(d), d
    return "%s (%d png)" % (os.path.relpath(d, REPO), len(glob.glob(d + "/*.png")))


def s_f7b_noisefloor():
    m = load("experiments/weekend_0823/rt_response/code/f7b_noisefloor.py")
    return "260820_ctrloff manifest: %d scenes" % len(m.ctrl.get("scenes", {}))


def s_c2_audit():
    m = load("experiments/weekend_0823/c2_rootcause/c2_audit.py")
    hm = m.heightmap_meta()
    return "%d scenes with heightmap_meta over 3 arms" % len(hm)


def s_r4_pixdiff():
    m = load("experiments/weekend_0823/redteam/r4_pixdiff.py")
    rdf = m.__dict__["round_dir_or_flat"]
    n = 0
    for sc, sub, band in m.SCENES:
        a = os.path.join(rdf("260823_cueoff_A"), sub, sc)
        assert os.path.isdir(a), a
        n += len(glob.glob(os.path.join(rdf(band + "_on"), "*", sc)))
    return "3 cueoff_A scene dirs + %d lineage_on scene dirs" % n


def s_smoke_summarize():
    m = load("experiments/weekend_0823/cue_audit/smoke_summarize.py")
    hits = [s for s in m.LINEAGE_ON if m.canonical_cut0(s)]
    return "%d/%d lineage scenes resolve" % (len(hits), len(m.LINEAGE_ON))


def s_w1b_rimpact():
    m = load("experiments/v3_0823/code/w1b_rimpact.py")
    return "landed frames: %d over %d scenes" % (sum(m.landed.values()),
                                                 len(m.landed))


def s_gpu_account():
    n = 0
    for rel in ("experiments/v3_0823/code/w2_gpu_account.py",
                "experiments/v3_0823/code/w3_gpu_account.py"):
        m = load(rel)
        rdf = m.__dict__["round_dir_or_flat"]
        for st in m.STAMPS:
            n += len(glob.glob(os.path.join(rdf(st), "*", "*", "variation.json")))
    return "%d variation.json over w2+w3 stamps" % n


def s_w3_verify():
    m = load("experiments/v3_0823/code/w3_verify.py")
    rdf = m.__dict__["round_dir_or_flat"]
    d = os.path.join(rdf("260824_v3w3_extbase_A"), m.SPLIT, "sceneH1")
    assert os.path.isdir(d), d
    return "%s (%d png)" % (os.path.relpath(d, REPO), len(glob.glob(d + "/*.png")))


def s_pixel_mass():
    m = load("experiments/weekend_0823/cue_audit/pixel_mass.py")
    rdf = m.__dict__["round_dir_or_flat"]
    n = len(glob.glob(os.path.join(rdf("260823_cueoff_A"), "*", "scene12",
                                   "variation.json")))
    return "%d variation.json for cueoff_A/scene12" % n


# --------------------------------------------------------------------------- #
# 5. the shell helper, exercised the way the converted scripts call it
# --------------------------------------------------------------------------- #
def s_shell_helper():
    import subprocess
    lib = os.path.join(REPO, "scripts", "lib", "negobs_paths.sh")
    script = ('source "%s"; negobs_round 260819_main_on; '
              'negobs_round_or_flat 260826_v3w1_lib_B; '
              'negobs_round_or_flat 260899_no_such_round; '
              'negobs_round 260899_no_such_round && echo STRICT_DID_NOT_FAIL'
              % lib)
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    out = [l for l in r.stdout.strip().split("\n") if l]
    assert "STRICT_DID_NOT_FAIL" not in r.stdout, r.stdout
    assert len(out) == 3, out
    assert os.path.isdir(out[0]) and os.path.isdir(out[1]), out
    assert out[2].endswith("dataset/260899_no_such_round"), out[2]
    return "negobs_round ok · or_flat ok · strict miss returns non-zero"


def main():
    protect()
    check("hash_gate.PROTECTED (rounds_matching)", s_hash_gate_protected)
    check("gates_cueoff.round_dirs (rounds_matching)", s_gates_cueoff_round_dirs)
    for rel, fname, run, scene in SDIR_SITES:
        check("%s.%s" % (os.path.basename(rel), fname),
              _sdir_check(rel, fname, run, scene))
    check("w1b2_repro_control isdir switch", s_repro_control_switch)
    check("w1c_hashgate.unit_dir (manifest)", s_w1c_hashgate_unit_dir)
    check("h12_gates.arm_dir (--root dataset)", s_h12_arm_dir)
    check("w3_extra_gates -> G.arm_dir (abs root)", s_w3_extra_gates_root)
    check("g7 family scene_dirs", s_g7_scene_dirs)
    check("build_corpus_v3", s_build_corpus_v3)
    check("cue_extent_audit", s_cue_extent_audit)
    check("cue_extent_audit registry patterns", s_cue_extent_registry_patterns)
    check("render_mass", s_render_mass)
    check("g2_adjudicate", s_g2_adjudicate)
    check("f7b_noisefloor (DS const)", s_f7b_noisefloor)
    check("c2_audit.heightmap_meta (f-string path)", s_c2_audit)
    check("r4_pixdiff (was ABS-HARDCODED)", s_r4_pixdiff)
    check("smoke_summarize.canonical_cut0", s_smoke_summarize)
    check("w1b_rimpact module-level glob", s_w1b_rimpact)
    check("w2+w3_gpu_account", s_gpu_account)
    check("w3_verify", s_w3_verify)
    check("pixel_mass", s_pixel_mass)
    check("scripts/lib/negobs_paths.sh", s_shell_helper)

    moved = restore()
    if moved:
        print("  [restored after import side effects] " + ", ".join(moved))

    npass = sum(1 for r in RESULTS if r[0] == "PASS")
    nskip = sum(1 for r in RESULTS if r[0] == "SKIP")
    nfail = sum(1 for r in RESULTS if r[0] == "FAIL")
    for st, label, detail in RESULTS:
        print("  %-4s %-44s %s" % (st, label, detail))
    print("\n%d PASS · %d SKIP · %d FAIL" % (npass, nskip, nfail))
    return 1 if nfail else 0


if __name__ == "__main__":
    raise SystemExit(main())
