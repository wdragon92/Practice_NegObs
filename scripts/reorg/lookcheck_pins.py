#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4: re-derive the pinned look_check round set FROM CODE (not from the survey TSV).

Sources of truth, in the order the stage brief names them:
  1. `scripts/valset.py` — every (scene, round) the three corpora join under
     `look_check/<scene>/<round>` (imported, so the list comprehensions over
     `SCENES` are evaluated exactly as the checker evaluates them).
  2. `scripts/regression_check.py` `resolve_round` baseline chain — the chain in
     its module docstring AND the (longer, authoritative) chain in
     `look_check/README.md` §4. A round is pinned in every scene directory where
     it exists, because `resolve_round` is applied per scene.
  3. every `look_check/<scene>/<round>/round_stamp.json` with
     `baseline_of_record: true`.
  4. (informational) the four hard-coded anchors in
     `scripts/quality_metrics_probe.py`.

Read-only. Writes nothing; prints TSV on stdout with `--tsv`.
"""
from __future__ import annotations
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LC = os.path.join(ROOT, "look_check")


def scene_dirs():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(LC, "scene*"))
                  if os.path.isdir(p) and not os.path.islink(p))


def valset_pins():
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import valset  # noqa: E402
    pins = set()
    for corpus in (valset.HISTORY, valset.FP, valset.T3):
        for _series, scene, b, a in corpus:
            pins.add((scene, b))
            pins.add((scene, a))
    return pins


def readme_chain():
    """The `--before-round` chain from look_check/README.md §4 (longest wins)."""
    txt = open(os.path.join(LC, "README.md"), encoding="utf-8").read()
    best = []
    for m in re.finditer(r"--before-round\s+([A-Za-z0-9_,\\\s]+?)\s*\\?\n", txt):
        names = [n.strip() for n in m.group(1).replace("\\", " ").split(",") if n.strip()]
        if len(names) > len(best):
            best = names
    return best


def regrcheck_chain():
    txt = open(os.path.join(ROOT, "scripts", "regression_check.py"), encoding="utf-8").read()
    best = []
    for m in re.finditer(r"--before-round\s+([A-Za-z0-9_,]+)", txt):
        names = [n.strip() for n in m.group(1).split(",") if n.strip()]
        if len(names) > len(best):
            best = names
    return best


def chain_pins(chain, scenes):
    """resolve_round is per scene and 'first existing wins', but ANY chain member
    present in a scene dir can become the head the day the ones above it are pruned
    (README §4 says exactly that: 'kept as a safety net'). So every existing
    (scene, chain-round) pair is pinned."""
    pins = set()
    for s in scenes:
        for r in chain:
            if os.path.isdir(os.path.join(LC, s, r)):
                pins.add((s, r))
    return pins


def stamp_pins(scenes):
    pins = set()
    for s in scenes:
        for d in sorted(glob.glob(os.path.join(LC, s, "*"))):
            if not os.path.isdir(d):
                continue
            sp = os.path.join(d, "round_stamp.json")
            if not os.path.isfile(sp):
                continue
            try:
                j = json.load(open(sp, encoding="utf-8"))
            except Exception:
                continue
            if j.get("baseline_of_record") is True:
                pins.add((s, os.path.basename(d)))
    return pins


# `look_check/README.md` §3 item 2 names these four as the published measurement
# anchors: `quality_metrics_probe.py` holds its four as real string constants, the
# other three carry theirs as docstring reproduction commands. Both kinds pin the
# round - one breaks a run, the other breaks a copy-pasteable command.
ANCHOR_FILES = [os.path.join(ROOT, "scripts", n) for n in
                ("quality_metrics_probe.py", "norm_spec.py",
                 "near_ground_stats.py", "skyline.py")]


def anchor_pins():
    pins = set()
    for f in ANCHOR_FILES:
        if not os.path.isfile(f):
            continue
        txt = open(f, encoding="utf-8").read()
        pins |= {(m.group(1), m.group(2))
                 for m in re.finditer(r"(scene[A-Za-z0-9]+)/([A-Za-z0-9_]+)", txt)}
    return pins


def resolve_round(scene_dir, chain):
    for name in chain:
        d = os.path.join(scene_dir, name)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png")):
            return name, len(glob.glob(os.path.join(d, "*.png")))
    return None, 0


def main():
    scenes = scene_dirs()
    vp = valset_pins()
    rc_chain = regrcheck_chain()
    rm_chain = readme_chain()
    chain = rm_chain if len(rm_chain) >= len(rc_chain) else rc_chain
    # union of both chains, README order first
    union_chain = rm_chain + [n for n in rc_chain if n not in rm_chain]
    cp = chain_pins(union_chain, scenes)
    sp = stamp_pins(scenes)
    ap = anchor_pins()

    on_disk = {(s, os.path.basename(d))
               for s in scenes
               for d in glob.glob(os.path.join(LC, s, "*")) if os.path.isdir(d)}

    vp_d, cp_d, sp_d, ap_d = (vp & on_disk, cp & on_disk, sp & on_disk, ap & on_disk)
    pinned = vp_d | cp_d | sp_d | ap_d

    if "--tsv" in sys.argv:
        print("scene\tround\tvalset\tregr_chain\tstamp_bor\tanchor")
        for s, r in sorted(pinned):
            print(f"{s}\t{r}\t{int((s,r) in vp_d)}\t{int((s,r) in cp_d)}"
                  f"\t{int((s,r) in sp_d)}\t{int((s,r) in ap_d)}")
        return
    if "--resolve" in sys.argv:
        print("scene\tresolved_round\tn_png")
        for s in scenes:
            n, c = resolve_round(os.path.join(LC, s), union_chain)
            print(f"{s}\t{n or '(none)'}\t{c}")
        return

    print(f"scenes on disk            : {len(scenes)}")
    print(f"round dirs on disk        : {len(on_disk)}")
    print(f"README §4 chain names     : {len(rm_chain)}")
    print(f"regression_check chain    : {len(rc_chain)}")
    print(f"union chain               : {len(union_chain)}")
    print(f"valset pins  (on disk)    : {len(vp_d)}  (declared {len(vp)})")
    print(f"chain pins   (on disk)    : {len(cp_d)}")
    print(f"stamp BoR    (on disk)    : {len(sp_d)}  (found {len(sp)})")
    print(f"anchors      (on disk)    : {len(ap_d)}  (found {len(ap)})")
    print(f"PINNED union (on disk)    : {len(pinned)}")


if __name__ == "__main__":
    main()
