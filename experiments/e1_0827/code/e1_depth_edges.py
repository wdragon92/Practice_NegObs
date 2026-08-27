# -*- coding: utf-8 -*-
"""e1_depth_edges.py -- route (b): edge polylines straight from the rendered
depth image, with ONE global parameter set.

Brief v6 §4 Phase 1-3 is explicit about why the parameters are global: tuning
(b) per scene to agree with (a) launders the contrast that the comparison is
supposed to measure. Every constant used here therefore comes from
`e1_const.py` and is the same for every frame, every scene and both domains.

The test: a pixel sits on a depth discontinuity when the largest 4-neighbour
depth jump satisfies

    |dd| >= max(B_ABS_JUMP_M, B_REL_JUMP * d)

-- the relative term because a 0.3 m step subtends less and less depth
difference with range, the absolute floor because the relative term alone fires
on near-field texture. The mask is thinned by the published Zhang-Suen 1984
rule (B_THIN_METHOD, no free parameter) and split into 8-connected components;
components shorter than B_MIN_COMP_PX are dropped.

This route is depth-only. It cannot know WHY a discontinuity is there, so it
also fires on object silhouettes (a lamp post against the ground). That is not a
defect to be tuned away -- it is one of the things the (a)-(b) deviation numbers
are there to expose.
"""

import numpy as np
import scipy.ndimage as ndi

import e1_const as C

_THIN_ITERS = {"n": 0}      # last thin() iteration count, for the diagnostics


def jump_mask(depth):
    """Boolean mask of depth-discontinuity pixels."""
    d = np.asarray(depth, dtype=np.float64)
    fin = np.isfinite(d) & (d > C.DEPTH_VALID_MIN_M)
    dd = np.zeros(d.shape, dtype=np.float64)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(d, -dy, axis=0), -dx, axis=1)
        nbf = np.roll(np.roll(fin, -dy, axis=0), -dx, axis=1)
        diff = np.where(fin & nbf, np.abs(d - nb), 0.0)
        dd = np.maximum(dd, diff)
    thr = np.maximum(C.B_ABS_JUMP_M, C.B_REL_JUMP * np.where(fin, d, np.inf))
    return fin & (dd >= thr)


def _neighbours(m):
    """P2..P9 of the Zhang-Suen 8-neighbourhood, clockwise from north."""
    return [np.roll(np.roll(m, dy, axis=0), dx, axis=1)
            for dy, dx in ((1, 0), (1, -1), (0, -1), (-1, -1),
                           (-1, 0), (-1, 1), (0, 1), (1, 1))]


def thin(mask):
    """Zhang-Suen 1984 parallel thinning (B_THIN_METHOD). No free parameter.

    Implemented here on purpose: the repo mandates PYTHONNOUSERSITE=1, and under
    that setting skimage is not importable on this machine (measured), so a
    library call would make the route (b) constant depend on the environment.
    """
    m = np.asarray(mask, dtype=bool).copy()
    m[0, :] = m[-1, :] = m[:, 0] = m[:, -1] = False       # border guard for roll
    it = 0
    for it in range(1, C.B_THIN_MAX_ITERS + 1):
        changed = False
        for sub in (0, 1):
            P = _neighbours(m)
            B = sum(p.astype(np.uint8) for p in P)
            seq = P + [P[0]]
            A = sum(((~seq[i]) & seq[i + 1]).astype(np.uint8) for i in range(8))
            if sub == 0:
                c1 = P[0] & P[2] & P[4]
                c2 = P[2] & P[4] & P[6]
            else:
                c1 = P[0] & P[2] & P[6]
                c2 = P[0] & P[4] & P[6]
            kill = (m & (B >= C.ZS_B_MIN) & (B <= C.ZS_B_MAX)
                    & (A == C.ZS_A_TARGET) & ~c1 & ~c2)
            if kill.any():
                m &= ~kill
                changed = True
        if not changed:
            break
    _THIN_ITERS["n"] = it
    return m


def components(mask):
    """8-connected components of the thinned mask, length-filtered."""
    lab, n = ndi.label(mask, structure=np.ones((3, 3), dtype=int))
    keep = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if ys.size < C.B_MIN_COMP_PX:
            continue
        keep.append(np.stack([xs, ys], axis=1))
    keep.sort(key=lambda p: (int(p[:, 0].min()), int(p[:, 1].min()), -len(p)))
    return keep


def extract(depth):
    """depth image -> (thinned mask, list of component pixel sets, diagnostics)."""
    raw = jump_mask(depth)
    thinned = thin(raw)
    comps = components(thinned)
    diag = {"n_jump_px": int(raw.sum()), "n_thin_px": int(thinned.sum()),
            "thin_iters": _THIN_ITERS["n"], "n_components": len(comps),
            "n_component_px": int(sum(len(c) for c in comps))}
    return thinned, comps, diag


def polylines(comps):
    """Component pixel sets -> ordered pixel polylines (same ordering routine as
    route (a), so the two routes are compared like with like)."""
    from e1_geometry import _order_component, rdp
    out = []
    for c in comps:
        order = _order_component(c.astype(np.float64))
        out.append([[float(x), float(y)] for x, y in rdp(c[order].astype(np.float64),
                                                         C.RDP_TOL_PX)])
    return out
