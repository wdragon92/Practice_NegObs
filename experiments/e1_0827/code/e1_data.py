# -*- coding: utf-8 -*-
"""e1_data.py -- locating and loading a rendered frame. No labelling logic.

Round directories are resolved BY NAME through `variation_kit.round_dir()`
(which raises on a missing or ambiguous name) -- dataset paths are never spelled
by hand, because the 2026-08-27 tidy-up moved every round one folder deeper
while keeping its name.
"""

import glob
import json
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _vk():
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    import variation_kit                      # driver-side path index only
    return variation_kit


def round_dir(name):
    return _vk().round_dir(name)


def scene_dir(round_name, scene_id):
    """<round>/<split>/<scene_id>, found by search -- the split is not ours to
    assume, and a scene that lives in two splits is an error, not a coin flip."""
    root = round_dir(round_name)
    hits = [d for d in glob.glob(os.path.join(root, "*", scene_id))
            if os.path.isdir(d)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise FileNotFoundError("[e1] scene %r not under round %r (%s)"
                                % (scene_id, round_name, root))
    raise RuntimeError("[e1] scene %r is in %d splits of %r: %s"
                       % (scene_id, len(hits), round_name, ", ".join(hits)))


def load_variation(sdir):
    with open(os.path.join(sdir, "variation.json"), encoding="utf-8") as fh:
        return json.load(fh)


def list_cuts(sdir):
    return load_variation(sdir).get("cuts", [])


def find_cut(sdir, frame_name):
    for c in list_cuts(sdir):
        if c.get("file") == frame_name:
            return c
    raise KeyError("[e1] cut %r not in %s/variation.json" % (frame_name, sdir))


def frame_assets(sdir, cut):
    """Absolute paths for one cut + which sidecars actually exist."""
    png = os.path.join(sdir, cut["file"])
    dep = os.path.join(sdir, cut.get("depth") or
                       cut["file"].replace(".png", ".depth.npy"))
    seg = os.path.join(sdir, cut["file"].replace(".png", ".idseg.npz"))
    return {
        "rgb_path": png, "depth_path": dep, "idseg_path": seg,
        "has_rgb": os.path.exists(png), "has_depth": os.path.exists(dep),
        "has_idseg": os.path.exists(seg),
        "has_heightmap": os.path.exists(os.path.join(sdir, "heightmap.npy")),
    }


def load_depth(path):
    """float16 on disk -> float64; inf (sky) is preserved and dropped by the
    validity test in e1_camera, never silently replaced."""
    return np.load(path).astype(np.float64)


def load_idseg(path):
    """(id image (H,W) uint16, {id -> prim path}) or (None, None) when absent."""
    if not os.path.exists(path):
        return None, None
    z = np.load(path, allow_pickle=False)
    ids = z["idseg"]
    raw = z["idToLabels"]
    table = json.loads(str(raw.item()) if getattr(raw, "shape", ()) == () else str(raw))
    return ids, {int(k): v for k, v in table.items() if str(k).lstrip("-").isdigit()}


def rel_to_repo(path):
    """Repo-relative path -- what goes into a record, so the manifest does not
    hard-code this machine."""
    return os.path.relpath(os.path.abspath(path), REPO)
