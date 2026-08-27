# -*- coding: utf-8 -*-
"""e1_visibility.py -- "is this 3D point visible, and if not, WHAT stopped it?"

Visibility (brief §2 rule 1): a world point is VISIBLE when its projected
z-depth agrees with the rendered depth image within VIS_TOL_M
([임시-결재대기], sensitivity 0.05 / 0.15 / 0.35 m in the ledger).

Blocking (brief §2 rule 3) is the part that must not be guessed:

  * self-occlusion by ground / stair / hazard geometry -- the BRINK -- is the
    DEFINITION of E and is NOT an occluder. Getting this backwards dumps every
    E frame into H_cand (the exact failure that killed the old labeller).
  * an EXTERNAL prim (guardrail, shrub, street furniture) makes the frame
    H_cand.

Telling the two apart needs a prim-id sidecar. This corpus ships one for part of
the population (`*.idseg.npz`: `idseg` (H,W) uint16 + `idToLabels` id -> USD prim
path). When a frame has no sidecar, or the blocking prim matches no APPROVED
rule, the answer is `flag = None` and the frame goes on an unresolved list. It is
never guessed, and `prim_class_rules.json` ships EMPTY for exactly that reason
(❓B-4).
"""

import json
import os
import re
from collections import Counter

import numpy as np

import e1_const as C

RULES_PATH = os.path.join(os.path.dirname(__file__), "prim_class_rules.json")

SELF = "self"          # ground / stair / hazard geometry -> not an occluder (E)
EXTERNAL = "external"  # guardrail, shrub, furniture ...  -> H_cand
UNKNOWN = "unknown"    # not classifiable without 결재


class PrimClassifier:
    """prim path -> {self, external, unknown}, driven by an approved rule file.

    Rule file shape:
        {"approved_by": "...", "rules": [{"pattern": "<regex>", "class": "self"}, ...]}

    Ships with `rules: []`. With no rules, EVERY blocking prim is `unknown`,
    which is the honest state before 결재 -- and it is visible in the output
    (occluder.flag stays null, the frame lands on the unresolved list) rather
    than hidden behind a plausible default.
    """

    def __init__(self, rules=None, approved_by=""):
        self.rules = rules or []
        self.approved_by = approved_by
        self._compiled = [(re.compile(r["pattern"]), r["class"]) for r in self.rules]

    @classmethod
    def load(cls, path=RULES_PATH):
        if not os.path.exists(path):
            return cls([], "")
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        return cls(doc.get("rules", []), doc.get("approved_by", ""))

    @property
    def is_empty(self):
        return not self._compiled

    def classify(self, prim_path):
        for rx, cls in self._compiled:
            if rx.search(prim_path or ""):
                return cls
        return UNKNOWN


def visibility_of(cam, pts3d, depth):
    """Per point: in_frame / visible / blocked / no_surface, plus pixel coords.

    `no_surface` = the rendered depth at that pixel is FARTHER than the point
    (or is sky). Nothing occludes it; the point simply is not on any rendered
    surface there -- a sub-pixel sliver of geometry, or a heightmap cell that
    the AABB envelope invented. Counted separately so it can never be mistaken
    for an occlusion.
    """
    px, py, zc, inb = cam.project(pts3d)
    d = cam.depth_at(depth, px, py)
    tol = C.VIS_TOL_M
    finite = np.isfinite(d)
    diff = np.where(finite, d - zc, np.nan)          # >0 : rendered surface is farther
    visible = inb & finite & (np.abs(diff) <= tol)
    blocked = inb & finite & (diff < -tol)
    no_surface = inb & (~finite | (diff > tol))
    return {"px": px, "py": py, "z_cam": zc, "in_frame": inb, "depth": d,
            "visible": visible, "blocked": blocked, "no_surface": no_surface}


def occluder_of(vis, ids, id_table, classifier, has_sidecar):
    """Turn the blocked points of ONE edge instance into the §5 `occluder` dict.

    Returns (occluder_dict, diagnostics). `flag`:
        True   at least one blocked point is an approved EXTERNAL prim
        False  points are blocked, but every blocker is approved SELF geometry
               (or nothing is blocked at all)
        None   unresolved -- no sidecar, or at least one blocker is `unknown`
    """
    n_in = int(vis["in_frame"].sum())
    n_blocked = int(vis["blocked"].sum())
    diag = {"n_in_frame": n_in, "n_visible": int(vis["visible"].sum()),
            "n_blocked": n_blocked, "n_no_surface": int(vis["no_surface"].sum()),
            "blocked_frac_total": (n_blocked / n_in) if n_in else None,
            "blocker_prims": {}}

    if n_in == 0:
        return {"flag": False, "prim": "none", "occl_frac": 0.0}, diag
    if n_blocked == 0:
        return {"flag": False, "prim": "none", "occl_frac": 0.0}, diag
    if not has_sidecar:
        diag["unresolved_reason"] = "no-seg-sidecar"
        return {"flag": None, "prim": "no-seg-sidecar", "occl_frac": None}, diag

    sel = vis["blocked"]
    xi = np.clip(np.round(vis["px"][sel] - 0.5).astype(np.int64), 0, ids.shape[1] - 1)
    yi = np.clip(np.round(vis["py"][sel] - 0.5).astype(np.int64), 0, ids.shape[0] - 1)
    prim_ids = ids[yi, xi]
    counts = Counter(int(v) for v in prim_ids)
    paths = {i: (id_table or {}).get(i, "id:%d" % i) for i in counts}
    diag["blocker_prims"] = {paths[i]: n for i, n in counts.most_common()}

    classes = {i: classifier.classify(paths[i]) for i in counts}
    n_ext = sum(n for i, n in counts.items() if classes[i] == EXTERNAL)
    n_unk = sum(n for i, n in counts.items() if classes[i] == UNKNOWN)

    if n_unk:
        diag["unresolved_reason"] = "unclassified-prim"
        top_unk = max((n, paths[i]) for i, n in counts.items()
                      if classes[i] == UNKNOWN)[1]
        return {"flag": None, "prim": top_unk, "occl_frac": None}, diag

    if n_ext:
        top_ext = max((n, paths[i]) for i, n in counts.items()
                      if classes[i] == EXTERNAL)[1]
        return {"flag": True, "prim": top_ext, "occl_frac": n_ext / n_in}, diag

    return {"flag": False, "prim": "self-geometry", "occl_frac": 0.0}, diag
