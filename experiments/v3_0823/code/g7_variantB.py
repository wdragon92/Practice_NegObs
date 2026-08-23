#!/usr/bin/env python3
"""G7 repair, sensitivity variant B — re-label the affected boost scenes against
the MAIN round's fused heightmap instead of a fusion of the boost round's own
cameras.

Why the variant exists.  A fused heightmap is a measurement of SCENE GEOMETRY,
not of a camera: it only differs between rounds because the pooled views differ.
The AABB map is byte-identical between 260819_main and 260820_boost_* (proved in
g7_pairing_audit.py), so the two rounds render the same ground.  The boost
cameras are band-biased (e: far+high, e2: near+low), so their pooled coverage is
thinner than the main round's -- scene12 ON is 27.7 % covered in `e2` against
74.8 % in `main`.  Variant B therefore asks the D50 question with the most
complete reference available inside this corpus, and variant A (the primary,
each round fused from its own depth) asks it self-containedly.

Tree:  dataset/260820_boost_<band>_<arm>_g7fixM/<split>/<scene>/  -- affected
scenes only, every entry a symlink, the fused sidecar pointing at the MAIN
round's file.  Nothing is copied and nothing frozen is written.
"""
import os, sys, json

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DS = os.path.join(REPO, "dataset")
# per-arm pairing, identical to the main round (fuse_heightmap.py docstring)
PAIRING = {"scene07": ("fused", "fused"),
           "scene08": ("aabb", "fused"),
           "scene12": ("fused", "fused")}
AFFECTED = {"e": ["scene07", "scene08", "scene12"], "e2": ["scene07", "scene12"]}


def sdir(round_name, scene):
    for split in sorted(os.listdir(os.path.join(DS, round_name))):
        d = os.path.join(DS, round_name, split, scene)
        if os.path.isfile(os.path.join(d, "variation.json")):
            return d, split
    return None, None


def build(band):
    for arm, ai in (("on", 0), ("off", 1)):
        src_round = f"260820_boost_{band}_{arm}"
        dst_round = src_round + "_g7fixM"
        main_round = f"260819_main_{arm}"
        for sc in AFFECTED[band]:
            s, split = sdir(src_round, sc)
            out = os.path.join(DS, dst_round, split, sc)
            os.makedirs(out, exist_ok=True)
            for f in sorted(os.listdir(s)):
                q = os.path.join(out, f)
                if not (os.path.exists(q) or os.path.islink(q)):
                    os.symlink(os.path.join(s, f), q)
            if PAIRING[sc][ai] == "fused":
                m, _ = sdir(main_round, sc)
                for b in ("heightmap_fused.npy", "heightmap_fused_meta.json"):
                    p, q = os.path.join(m, b), os.path.join(out, b)
                    if not os.path.isfile(p):
                        sys.exit(f"[variantB] FATAL main round lacks {p}")
                    if not (os.path.exists(q) or os.path.islink(q)):
                        os.symlink(p, q)
            print(f"[variantB] {dst_round}/{split}/{sc}  hm={PAIRING[sc][ai]}")


if __name__ == "__main__":
    for b in ("e", "e2"):
        build(b)
