#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_driver.py — the render driver for the three hole probes.

It is a **shim around `scripts/run_data_render.py`**, not a copy of it. Every
line of render logic — camera sampler, condition switching, rejection filters,
sidecars, resume, manifest — is the corpus driver's, untouched. This file only
teaches that driver about three scenes it has no way to know about, and it does
so **at runtime, in this process only**.

WHY A SHIM AND NOT TWO SMALL EDITS TO THE REPO
==============================================
Two things stand between `run_data_render.py` and a probe scene, and they are
not equally dangerous.

(1) DISCOVERY — cheap, and would have been fine to edit.
    `run_data_render.scene_files()` globs `scenes/{main,batch1}/scene*.py` and
    keys each file by `basename.split("_")[0]`. It is NOT recursive and the
    glob is `scene*`, so files named `probe*.py` under `scenes/probe/` are
    invisible to it no matter where they sit. (Verified: the function has no
    env override and no other call site.) A one-line edit would fix it.

(2) THE LEDGER — NOT cheap. This is the real blocker, and it is a trap.
    `vk.ledger(scene)` raises `SystemExit` for any scene absent from
    `vk.AZ_LEDGER`, so the probe scenes must be in it. But `vk.split_map()`
    computes the train/val/test split by **shuffling `sorted(AZ_LEDGER)` with a
    fixed seed and slicing**:

        scenes = sorted(AZ_LEDGER)
        random.Random(var_seed("__all__","split",0,base)).shuffle(scenes)
        n_tr = round(0.70*n); n_va = round(0.15*n)      # variation_kit.py:831

    Adding three names to the table at SOURCE level therefore re-shuffles all
    33 corpus scenes. Measured, not guessed:

        >>> base = vk.split_map(0)                 # the frozen 33
        >>> vk.AZ_LEDGER.update(3 probe rows); vk._SPLIT_CACHE.clear()
        >>> [s for s in base if base[s] != vk.split_map(0)[s]]
        19 scenes move: scene01, scene02, scene05, scene06, scene09, scene10,
        scene12, scene16, scene17, scene18, scene19, scene20, scene21,
        sceneC1, sceneC2, sceneD1, sceneN1, sceneN2, sceneN5

    That is 19 of 33 corpus scenes changing the `<split>/` directory any future
    corpus render files them under, and it would also break
    `variation_kit._selfcheck`'s `chk("33 scenes", len(AZ_LEDGER) == 33)`.
    Absolute rules 1, 2 and 4 of OVERNIGHT_BRIEF_0820 forbid exactly this. An
    exploratory probe track (the FIRST thing on §5's discard list) may not put a
    scratch on the frozen corpus's provenance.

    So the ledger rows are injected here, AFTER `vk.split_map(0)` has already
    been called once and its result cached in `vk._SPLIT_CACHE[0]`. The cache
    hit means the 33 corpus scenes keep byte-identical splits, and the probe
    rows are then written into that cached dict with the split `"probe"` — a
    fourth value that no corpus tool asks for and that keeps probe frames in
    `dataset/<group>/<run>/probe/<scene>/`, visibly apart from `train/ val/ test/`
    (0827 reorg: rounds sit one purpose group below `dataset/`; resolve a round by
    NAME via `dataset/ROUNDS.json` or `variation_kit.round_dir(name)`, never by path).
    `SPLIT_GUARD` below re-verifies the 33 after the injection and aborts if any
    moved.

WHICH LEDGER CLASS, AND ON WHAT AUTHORITY
=========================================
`vk.AZ_LEDGER` is a MEASURED table (SP-2, 693 cuts). Nothing measured these
three scenes, so the honest move is to borrow the row of the closest measured
scene and say so — which is what `LEDGER_BASIS` records in the row itself.

    class C'  (daz_judge = DAZ_SAMPLER_MAX = 35 deg, label_shadow = False,
               az_free = False, c_bound = False  ->  daz_data = 35 deg)

borrowed from **sceneD2 floor_opening** — an outdoor concrete opening in flat
paving under the same noon rig, which the SP-2 sweep measured at +-35 deg with
no criterion-B firing at any arm (`variation_kit.py:157-159` calls it out by
name). The three probes reuse sceneD2's light dict verbatim
(`probe_common.probe_light`), which is what makes the borrowing defensible
rather than convenient.

The alternatives were considered and rejected: `_AZ_FREE` (sceneC1/C4/D4) is for
sunless or sealed-indoor scenes and these are outdoor with a sun; `label_shadow`
(sceneN1) is for a scene whose LABEL is a shadow band, and here the label is a
hole in a heightmap.

Consequence for the round, computed:  L0, L5 and L7 are ALL admissible on all
three probes (`vk.condition_allowed` returns (True, "")), because C' gives
daz_data 35 deg and L5's forced-off-noon minimum of 37.0 deg is covered by
`DAZ_DATA_EXTRAP = 60` (granted to any scene that is neither label_shadow nor
c_bound). **No condition substitution is needed** — unlike sceneC1/C2/N1/
scene15 in the corpus rounds.

USAGE
=====
    python3 probe_driver.py --plan --scenes probeH1,probeH2,probeH3 \
            --conds L0,L5,L7 --cams 8 --seed 20260822
    python3 probe_driver.py --run 260821_probe_on --scenes probeH1 ...

`run_probe.sh` is the intended entry point; this file is what it calls.
"""
from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCENE_DIR = os.path.join(REPO, "scenes", "probe")
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))   # for `import run_data_render`

import variation_kit as vk                                        # noqa: E402

PROBE_SPLIT = "probe"
PROBE_SCENES = ("probeH1", "probeH2", "probeH3")
LEDGER_BASIS = ("borrowed from sceneD2 floor_opening (C', +-35 deg with no "
                "criterion-B firing, SP-2); same rig, same outdoor concrete "
                "opening class. NOT independently measured — probe track, "
                "evaluation only.")


def install():
    """Inject the probe scenes into `variation_kit` and `run_data_render`.

    Idempotent, and safe to call in both the driver process and the per-scene
    subprocess. Returns the `run_data_render` module, patched.
    """
    # --- 1. freeze the corpus split BEFORE the ledger grows -----------------
    frozen = dict(vk.split_map(0))            # populates vk._SPLIT_CACHE[0]
    if len(frozen) != 33:
        raise SystemExit(f"[probe] expected 33 corpus scenes in the ledger, "
                         f"found {len(frozen)} — refusing to touch it")

    # --- 2. add the probe rows ---------------------------------------------
    for s in PROBE_SCENES:
        if s in vk.AZ_LEDGER:
            continue
        vk.AZ_LEDGER[s] = vk._ledger_row(
            s, "C'", vk.DAZ_SAMPLER_MAX, False, LEDGER_BASIS)

    # --- 3. give them a split of their own, in the ALREADY-CACHED map -------
    cached = vk._SPLIT_CACHE[0]
    for s in PROBE_SCENES:
        cached[s] = PROBE_SPLIT

    # --- 4. SPLIT_GUARD: prove the corpus did not move ----------------------
    moved = [s for s, v in frozen.items() if vk.split_of(s) != v]
    if moved:
        raise SystemExit(
            f"[probe] SPLIT GUARD TRIPPED — {len(moved)} corpus scene(s) "
            f"changed split after the probe injection: {sorted(moved)}. This "
            f"must never happen; the whole point of caching the map first is "
            f"that it cannot. Abort and report.")

    # --- 5. teach the driver where the probe scene files are ---------------
    import run_data_render as rdr                                 # noqa: E402
    found = {}
    for f in sorted(glob.glob(os.path.join(SCENE_DIR, "probe*.py"))):
        b = os.path.basename(f)
        if b.startswith("probe_common"):
            continue
        found[b.split("_")[0]] = (f, "probe")
    missing = [s for s in PROBE_SCENES if s not in found]
    if missing:
        raise SystemExit(f"[probe] no scene file for {missing} under "
                         f"{SCENE_DIR} (expected <key>_<name>.py)")
    rdr.SCENE_FILES.update(found)
    rdr.ALL_SCENES = list(PROBE_SCENES)

    # --- 6. re-entry point for the per-scene subprocess ---------------------
    # `run_data_render.drive` spawns `[sys.executable, os.path.abspath(__file__),
    # "--scene-proc", ...]` reading the MODULE-level `__file__` of
    # `run_data_render`. Pointing it at this file makes each scene subprocess
    # come back through `install()` before it calls `vk.ledger` / `vk.split_of`
    # — which it does, in `scene_proc` and `_write_scene_json`. Without this the
    # subprocess would die with "scene 'probeH1' is not in the SP-2 azimuth
    # ledger". `rdr.REPO` was computed at import time from the real path, so
    # rebinding `__file__` afterwards changes nothing else.
    rdr.__file__ = os.path.abspath(__file__)
    return rdr


def _depoison(run, tag):
    """Withdraw `done_conds` from any scene in `run` that produced ZERO cuts.

    `run_data_render.drive` advances a scene's `done_conds` whenever the scene
    SUBPROCESS returned 0 (`run_data_render.py:202`). That is a sound test for a
    corpus scene but not for a crashing one: an Isaac scene process exits 0 even
    when assembly raised, because the app's shutdown path reaches `os._exit(0)`
    regardless. The first probe attempt therefore recorded

        "probeH1": {"exit": 0, "cuts": 0, "done_conds": ["L0","L5","L7"]}

    and every later invocation answered `[skip] probeH1 — all 1 conditions
    already done` and rendered nothing. The round was **unrecoverable by
    re-running**, which is precisely what run_probe.sh promises it is — the
    banner even says "re-run this script unchanged to resume".

    A scene that produced no cuts has done no work and may not claim a
    condition. Rewriting only that one field leaves every genuinely-rendered
    scene byte-identical, keeps the shared corpus driver unmodified, and is what
    makes the probe's resume mean what it says. Called on the way IN (to clear
    poison an earlier attempt left) and on the way OUT (so a failure never
    poisons the next attempt).
    """
    mf_path = os.path.join(vk.data_root(run), "manifest.json")
    if not os.path.isfile(mf_path):
        return
    try:
        with open(mf_path, encoding="utf-8") as fh:
            mf = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"[probe] [warn] manifest unreadable ({tag}): {e}")
        return
    cleared = []
    for s, rec in (mf.get("scenes") or {}).items():
        if not rec.get("cuts") and rec.get("done_conds"):
            cleared.append(f"{s} {rec['done_conds']}")
            rec["done_conds"] = []
    if not cleared:
        return
    tmp = mf_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(mf, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, mf_path)
    print(f"[probe] resume de-poisoned ({tag}) in {run}: withdrew done_conds "
          f"from {len(cleared)} zero-cut scene(s) — {', '.join(cleared)}. "
          f"They will be retried instead of skipped.")


def _run_arg(argv, flag="--run"):
    """The value of `flag` in `argv`, supporting both `--run X` and `--run=X`."""
    for i, a in enumerate(argv):
        if a == flag and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(flag + "="):
            return a.split("=", 1)[1]
    return None


def _check_run(run="260730_data_mini"):
    """`scripts/check_data_run.py` on a probe round, with an EMPTY-ROUND guard.

    check_data_run assumes a round has at least one cut — its check 3 ends in

        nr = min(c["stage1"]["nearest_solid"] for c in cuts)   # :222

    which raises `ValueError: min() arg is an empty sequence` when every scene
    failed to render. That is what happened on the first probe attempt, and the
    traceback was actively harmful: it buried the REAL failure (a scene-assembly
    error 60 lines higher up) under a second, meaningless one, and it made the
    checker look like the broken component.

    A round with no cuts is a RENDER failure, not a checker failure. Say so in
    one line, name where the real traceback is, and return non-zero without a
    traceback of our own. `check_data_run.py` is a corpus script shared with the
    frozen rounds and is not modified for the probe's benefit.
    """
    import check_data_run                                       # noqa: E402
    root = vk.data_root(run)
    mf = os.path.join(root, "manifest.json")
    if not os.path.isfile(mf):
        print(f"[probe] [FAIL] check-run {run}: no manifest at {mf} — the "
              f"render never got as far as writing one. Nothing to check.")
        return 1

    n_cuts = 0
    for p in sorted(glob.glob(os.path.join(root, "*", "*", "variation.json"))):
        try:
            with open(p, encoding="utf-8") as fh:
                n_cuts += len(json.load(fh).get("cuts") or [])
        except (OSError, ValueError) as e:
            print(f"[probe] [warn] unreadable {p}: {e}")
    if n_cuts == 0:
        print(f"[probe] [FAIL] check-run {run}: 0 cuts on disk across "
              f"{len(glob.glob(os.path.join(root, '*', '*')))} scene dir(s). "
              f"The render produced nothing, so there is nothing to check — "
              f"this is NOT a checker finding. Read the render traceback "
              f"higher up in logs/probe.log (the first '[py stderr]' block).")
        return 1

    try:
        return check_data_run.main(run)
    except ValueError as e:
        # A partially-rendered round can still starve an aggregate the checker
        # takes over all cuts. Same verdict, same reason: fix the render.
        print(f"[probe] [FAIL] check-run {run}: check_data_run raised "
              f"{type(e).__name__}: {e} on a {n_cuts}-cut round — the round is "
              f"partial or degenerate. Treat it as a render failure, not a "
              f"checker bug.")
        return 1


def main(argv):
    rdr = install()
    if argv and argv[0] == "--scene-proc":
        return rdr.scene_proc(*argv[1:])
    if argv and argv[0] == "--check-run":
        # `scripts/check_data_run.py` also calls `vk.ledger(scene)` (its check 2
        # is the azimuth-ledger conformance test), so the round checker has to
        # come through the same shim or it exits with "not in the SP-2 azimuth
        # ledger" on the first probe scene.
        return _check_run(*argv[1:])
    if not any(a.startswith("--scenes") for a in argv):
        argv = list(argv) + ["--scenes", ",".join(PROBE_SCENES)]
    print(f"[probe] ledger rows injected: {list(PROBE_SCENES)} "
          f"(class C', daz_data {vk.ledger('probeH1')['daz_data']:.0f} deg) · "
          f"split '{PROBE_SPLIT}' · corpus split UNCHANGED (33 scenes verified)")
    run = _run_arg(argv)
    if run:
        _depoison(run, "pre")
    try:
        return rdr.main(argv)
    finally:
        if run:
            _depoison(run, "post")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
