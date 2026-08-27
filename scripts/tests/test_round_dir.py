#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for variation_kit.round_dir() — the 0827 reorg's path helper.

Plain asserts, no test framework (nothing in this repo has one, and the helper
has to be checkable on a bare interpreter with no Isaac and no GPU):

    python3 scripts/tests/test_round_dir.py

Every layout case gets a throwaway tree under tempfile, so the tests are true
both BEFORE the dataset/ move (flat) and after it (grouped). The last test is
the one that ties them to reality: it resolves a real round in the live tree,
whatever layout the live tree currently has.
"""
from __future__ import annotations

import importlib
import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

import variation_kit as vk                                        # noqa: E402

PASS = []


def check(label, fn):
    fn()
    PASS.append(label)
    print("  ok   " + label)


def _mkround(root, *parts):
    """Create <root>/<parts...> as a round directory and return its path."""
    p = os.path.join(root, *parts)
    os.makedirs(os.path.join(p, "val", "scene01"), exist_ok=True)
    return p


def _write_index(root, mapping):
    import json
    with open(os.path.join(root, vk.ROUNDS_INDEX), "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, indent=1, sort_keys=True)


# ---------------------------------------------------------------------------
def t_flat():
    """(a) flat <root>/<name> — the pre-move layout and where new rounds land."""
    with tempfile.TemporaryDirectory() as d:
        want = _mkround(d, "260819_main_on")
        got = vk.round_dir("260819_main_on", dataset_root=d)
        assert os.path.realpath(got) == os.path.realpath(want), got


def t_grouped_via_index():
    """(b) grouped, found through ROUNDS.json."""
    with tempfile.TemporaryDirectory() as d:
        want = _mkround(d, "v2_corpus", "260819_main_on")
        _write_index(d, {"260819_main_on": "v2_corpus"})
        got = vk.round_dir("260819_main_on", dataset_root=d)
        assert os.path.realpath(got) == os.path.realpath(want), got


def t_grouped_via_glob():
    """(c) grouped, found by scanning — no index present at all."""
    with tempfile.TemporaryDirectory() as d:
        want = _mkround(d, "v3_library", "260826_v3w1_lib_B_h")
        assert not os.path.exists(os.path.join(d, vk.ROUNDS_INDEX))
        got = vk.round_dir("260826_v3w1_lib_B_h", dataset_root=d)
        assert os.path.realpath(got) == os.path.realpath(want), got


def t_archive_second_level():
    """(c) the archive tier is two levels deep and still resolves."""
    with tempfile.TemporaryDirectory() as d:
        want = _mkround(d, "_archive", "pilots", "260815_datapilot")
        got = vk.round_dir("260815_datapilot", dataset_root=d)
        assert os.path.realpath(got) == os.path.realpath(want), got


def t_stale_index_falls_through():
    """An index entry pointing at a directory that does not exist is ignored,
    not returned — round_dir must never hand back a non-existent path."""
    with tempfile.TemporaryDirectory() as d:
        want = _mkround(d, "v3_aux", "260825_v3w0_cuecls_A")
        _write_index(d, {"260825_v3w0_cuecls_A": "v3_library"})   # wrong group
        got = vk.round_dir("260825_v3w0_cuecls_A", dataset_root=d)
        assert os.path.realpath(got) == os.path.realpath(want), got
        assert os.path.isdir(got)


def t_miss_raises():
    """0 hits -> FileNotFoundError naming the round and the roots searched."""
    with tempfile.TemporaryDirectory() as d:
        _mkround(d, "v2_corpus", "260819_main_on")
        try:
            vk.round_dir("260819_main_off", dataset_root=d)
        except FileNotFoundError as exc:
            msg = str(exc)
            assert "260819_main_off" in msg, msg
            assert d in msg, msg
            assert "_archive" in msg, msg
        else:
            raise AssertionError("a missing round returned instead of raising")


def t_ambiguity_raises():
    """>1 hit -> RuntimeError listing them (the mid-move state)."""
    with tempfile.TemporaryDirectory() as d:
        _mkround(d, "260820_boost_e_on")                  # flat copy
        _mkround(d, "v2_corpus", "260820_boost_e_on")     # grouped copy
        try:
            vk.round_dir("260820_boost_e_on", dataset_root=d)
        except RuntimeError as exc:
            msg = str(exc)
            assert "260820_boost_e_on" in msg, msg
            assert msg.count("260820_boost_e_on") >= 3, msg   # name + 2 paths
        else:
            raise AssertionError("an ambiguous round returned instead of raising")


def t_symlink_alias_is_one_hit():
    """A back-compat symlink beside the real dir is the SAME dir, not an
    ambiguity — candidates are collapsed by realpath."""
    with tempfile.TemporaryDirectory() as d:
        want = _mkround(d, "v2_probes", "260821_probe_on")
        os.symlink(want, os.path.join(d, "260821_probe_on"))
        got = vk.round_dir("260821_probe_on", dataset_root=d)
        assert os.path.realpath(got) == os.path.realpath(want), got


def t_env_override():
    """NEGOBS_DATASET_ROOT relocates the whole lookup (read at import time)."""
    with tempfile.TemporaryDirectory() as d:
        want = _mkround(d, "cueoff", "260823_cueoff_A")
        old = os.environ.get("NEGOBS_DATASET_ROOT")
        os.environ["NEGOBS_DATASET_ROOT"] = d
        try:
            importlib.reload(vk)
            assert vk.DATASET_ROOT == d, vk.DATASET_ROOT
            got = vk.round_dir("260823_cueoff_A")             # no explicit root
            assert os.path.realpath(got) == os.path.realpath(want), got
            assert vk.data_root("260823_cueoff_A") == got
            assert vk.data_root("260899_brand_new") == os.path.join(
                d, "260899_brand_new")
        finally:
            if old is None:
                os.environ.pop("NEGOBS_DATASET_ROOT", None)
            else:
                os.environ["NEGOBS_DATASET_ROOT"] = old
            importlib.reload(vk)
        assert vk.DATASET_ROOT == os.path.join(vk.REPO, "dataset"), vk.DATASET_ROOT


def t_data_root_new_stamp_is_flat():
    """A stamp that does not exist yet is still created flat — this is what
    scripts/run_data_render.py:112 makedirs()."""
    with tempfile.TemporaryDirectory() as d:
        old = os.environ.get("NEGOBS_DATASET_ROOT")
        os.environ["NEGOBS_DATASET_ROOT"] = d
        try:
            importlib.reload(vk)
            assert vk.data_root("260828_v3w4_x") == os.path.join(
                d, "260828_v3w4_x")
        finally:
            if old is None:
                os.environ.pop("NEGOBS_DATASET_ROOT", None)
            else:
                os.environ["NEGOBS_DATASET_ROOT"] = old
            importlib.reload(vk)


def t_has_round():
    """has_round() — the group-aware isdir() feature switch (S3)."""
    with tempfile.TemporaryDirectory() as d:
        _mkround(d, "v3_aux", "260826_v3a_segfill")
        _write_index(d, {"260826_v3a_segfill": "v3_aux"})
        assert vk.has_round("260826_v3a_segfill", dataset_root=d)
        assert not vk.has_round("260826_v3a_never_rendered", dataset_root=d)


def t_rounds_matching_across_groups():
    """rounds_matching() — the group-aware replacement for glob(<root>/<pre>*).

    The flat glob is the idiom that fails SILENTLY after the move, so this test
    also asserts the negative control: a name that only LOOKS like the prefix
    (different stem) is not swept in, and a GROUP directory is never returned
    as if it were a round.
    """
    with tempfile.TemporaryDirectory() as d:
        _mkround(d, "v2_corpus", "260820_boost_h_on")
        _mkround(d, "v2_corpus", "260820_boost_h_off")
        _mkround(d, "_archive", "v2_probes", "260820_boost_h")
        _mkround(d, "v3_aux", "260825_v3w0_cuecls_A")
        _mkround(d, "260828_boost_z")                     # flat, not yet grouped
        _write_index(d, {"260820_boost_h_on": "v2_corpus",
                         "260820_boost_h_off": "v2_corpus",
                         "260820_boost_h": "_archive/v2_probes",
                         "260825_v3w0_cuecls_A": "v3_aux"})
        got = [os.path.basename(p) for p in vk.rounds_matching(
            "260820_boost_", dataset_root=d)]
        assert got == ["260820_boost_h", "260820_boost_h_off",
                       "260820_boost_h_on"], got
        for p in vk.rounds_matching("260820_boost_", dataset_root=d):
            assert os.path.isdir(p), p
        # a flat round that has not been grouped yet is still found
        assert [os.path.basename(p) for p in vk.rounds_matching(
            "260828_", dataset_root=d)] == ["260828_boost_z"]
        # every round, and no group directory among them
        allr = [os.path.basename(p) for p in vk.rounds_matching("", dataset_root=d)]
        assert len(allr) == 5, allr
        for g in ("v2_corpus", "v3_aux", "_archive", "v2_probes"):
            assert g not in allr, (g, allr)
        # miss is an empty list, not an exception — the caller decides
        assert vk.rounds_matching("2609", dataset_root=d) == []


def t_rounds_matching_pattern():
    """rounds_matching() with a GLOB pattern, matched on the round name only.

    `cue_extent_audit.py`'s registry scan globs `*reg_[ABCD]` and `*_v3p5_*`;
    a wildcard in the middle cannot be expressed as a prefix, and a flat glob
    would not cross the new group directory.
    """
    with tempfile.TemporaryDirectory() as d:
        _mkround(d, "_archive", "v3_scene_build", "260823_v3p5_h12reg_A")
        _mkround(d, "v3_scene_build", "260823_v3p5_h12reg2_B")
        _mkround(d, "v3_library", "260826_v3w1_lib_C")
        _write_index(d, {"260823_v3p5_h12reg_A": "_archive/v3_scene_build",
                         "260823_v3p5_h12reg2_B": "v3_scene_build",
                         "260826_v3w1_lib_C": "v3_library"})
        got = [os.path.basename(p) for p in
               vk.rounds_matching("*reg_[ABCD]", dataset_root=d)]
        assert got == ["260823_v3p5_h12reg_A"], got
        got = sorted(os.path.basename(p) for p in
                     vk.rounds_matching("*_v3p5_*", dataset_root=d))
        assert got == ["260823_v3p5_h12reg2_B", "260823_v3p5_h12reg_A"], got
        # the pattern never sees the group name
        assert vk.rounds_matching("v3_*", dataset_root=d) == []
        # a pattern that matches nothing is [], not an error
        assert vk.rounds_matching("*nope*", dataset_root=d) == []
        # no wildcard -> still a plain prefix
        assert [os.path.basename(p) for p in
                vk.rounds_matching("260826_", dataset_root=d)] == ["260826_v3w1_lib_C"]


def t_rounds_matching_live_tree():
    """Live tree: every round in ROUNDS.json is reachable by prefix, and the
    prefix sweep agrees with the index exactly."""
    import json
    idx_path = os.path.join(vk.DATASET_ROOT, vk.ROUNDS_INDEX)
    if not os.path.isfile(idx_path):
        return                                   # flat tree, nothing to compare
    with open(idx_path, encoding="utf-8") as fh:
        idx = json.load(fh)
    got = sorted(os.path.basename(p) for p in vk.rounds_matching(""))
    assert got == sorted(idx), (len(got), len(idx))


def t_live_tree():
    """The live repo, in whatever layout it is in right now."""
    got = vk.round_dir("260819_main_on")
    assert os.path.isdir(got), got
    assert os.path.basename(got) == "260819_main_on", got
    assert os.path.isdir(os.path.join(got, "val")) or os.path.isdir(
        os.path.join(got, "train")), got
    # data_root agrees with round_dir for a stamp that already exists
    assert vk.data_root("260819_main_on") == got


def main():
    print("test_round_dir.py — variation_kit.round_dir()")
    print("  DATASET_ROOT = " + vk.DATASET_ROOT)
    for name, fn in sorted(globals().items()):
        if name.startswith("t_") and callable(fn):
            check(name[2:], fn)
    print("\n%d/%d PASS" % (len(PASS), len(PASS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
