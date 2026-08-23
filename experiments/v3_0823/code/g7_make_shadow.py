#!/usr/bin/env python3
"""G7 repair, step 1 — build SHADOW render trees for the boost rounds.

The defect (G7 / D42 / D50): the 08-20 `boost_*` rounds never ran
`fuse_heightmap.py`, so every boost scene-arm was labelled off the top-down AABB
heightmap.  On the scenes the main round had to fuse (scene02/07/08/12/16) the
AABB map is demonstrably wrong, and the twin diff collapses to an empty or
splinter footprint.

`fuse_heightmap.py` writes its sidecar INTO the scene directory and
`labeler.load_heightmap` reads it from there, so repairing the boost rounds
without touching the frozen corpus needs a parallel tree.  This builds one:

    dataset/260820_boost_<band>_<arm>_g7fix/<split>/<scene>/

Every entry of the original scene directory becomes a SYMLINK (pixels, depth
sidecars, variation.json, heightmap.npy, heightmap_meta.json, .negobs_env.json).
Nothing under the original round is created, modified or removed.  The fused
sidecars written in step 2 are the only real files in the shadow tree.
"""
import os, sys, json

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DS = os.path.join(REPO, "dataset")
SUFFIX = "_g7fix"


def build(round_name):
    src = os.path.join(DS, round_name)
    dst = os.path.join(DS, round_name + SUFFIX)
    if not os.path.isdir(src):
        sys.exit(f"[shadow] FATAL missing round {src}")
    n_dir = n_link = 0
    os.makedirs(dst, exist_ok=True)
    # round-level manifest.json -> symlink
    for e in sorted(os.listdir(src)):
        p = os.path.join(src, e)
        if os.path.isfile(p):
            q = os.path.join(dst, e)
            if not os.path.islink(q):
                os.symlink(p, q); n_link += 1
            continue
        for sc in sorted(os.listdir(p)):                    # <split>/<scene>
            sdir = os.path.join(p, sc)
            if not os.path.isfile(os.path.join(sdir, "variation.json")):
                continue
            out = os.path.join(dst, e, sc)
            os.makedirs(out, exist_ok=True); n_dir += 1
            for f in sorted(os.listdir(sdir)):
                q = os.path.join(out, f)
                if os.path.exists(q) or os.path.islink(q):
                    continue
                os.symlink(os.path.join(sdir, f), q); n_link += 1
    return dst, n_dir, n_link


if __name__ == "__main__":
    rounds = sys.argv[1:] or [
        "260820_boost_e_on", "260820_boost_e_off",
        "260820_boost_e2_on", "260820_boost_e2_off",
    ]
    for r in rounds:
        d, nd, nl = build(r)
        print(f"[shadow] {r:24s} -> {os.path.relpath(d, REPO)}  {nd} scene-dirs  {nl} symlinks")
