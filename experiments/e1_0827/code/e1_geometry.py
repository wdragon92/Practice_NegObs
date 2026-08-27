# -*- coding: utf-8 -*-
"""e1_geometry.py -- route (a): edge instances from the scene heightmap, and the
visible interior region.

Brief v6 §2 rule 1, spelled out as the five stages this module runs:

  1. WALKABLE   -- which grid cells are a surface you could stand on. The
                   heightmap is an AABB ENVELOPE (e1_const.HM_SOURCE_NOTE), so a
                   railing top, a parapet and a roof are all "surfaces" in it.
                   A cell is walkable when enough of its WALK_FOOT_R_M footprint
                   sits within WALK_FLAT_TOL_M of its own height.
  2. REACHABLE  -- flood fill from the cell the camera is standing on, stepping
                   only between 4-neighbours whose height differs by at most
                   MAX_TRAVERSE_STEP_M. This is what keeps a 6 m building roof
                   (also flat, also a 6 m drop) out of the edge population while
                   keeping every stair tread in it.
  3. DROP       -- drop(c) = z(c) - min{z(n) : |n-c| <= R_RUN_M}. Rule 1's
                   "falls at least DROP_MIN_M within the run distance".
  4. BREAK      -- an edge cell also needs a LOCAL fall: some 4-neighbour lower
                   by BREAK_LOCAL_FALL_M. Without it a long smooth ramp that
                   descends 0.3 m over R_RUN_M is a break line, which it is not.
  5. INSTANCES  -- 8-connected components of the edge cells, ordered into a
                   polyline, projected, cut into visible runs.

The interior is the same rule read downward: pixels of the RENDERED depth whose
world point sits DROP_MIN_M or more below the lip height of the instance they
belong to. "Belong to" = nearest instance in the horizontal plane (a Voronoi
split, so no association radius has to be invented).

Two consequences are reported, not hidden:
  * a descending stair produces ONE INSTANCE PER NOSING, not one per stair --
    every riser is a walkable surface that falls >= 0.3 m within R_RUN_M. That
    is the literal reading of rule 1 (❓B-2).
  * where the AABB envelope spans a floor opening, route (a) sees NO drop at
    all, however obvious the pit is in the RGB (❓B-1).
"""

import numpy as np
import scipy.ndimage as ndi
from scipy.spatial import cKDTree

import e1_const as C
import e1_visibility as V


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _disc(radius_cells):
    r = int(radius_cells)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (xx * xx + yy * yy) <= r * r


def _window(radius_cells, shape=None):
    """Neighbourhood implementing 'within R_RUN_M' -- see EDGE_WINDOW_SHAPE."""
    r = int(radius_cells)
    shape = shape or C.EDGE_WINDOW_SHAPE
    if shape == "disc":
        return _disc(r)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    if shape == "chebyshev":
        return np.ones((2 * r + 1, 2 * r + 1), dtype=bool)
    if shape == "cross":
        return (xx == 0) | (yy == 0)
    raise ValueError("[e1] unknown EDGE_WINDOW_SHAPE %r" % shape)


def _cells(metres, step):
    return max(1, int(round(metres / step)))


def walkable_mask(hm):
    """Stage 1. Flat-enough surface, judged inside a WALK_FOOT_R_M footprint."""
    step = hm.step
    foot = _disc(_cells(C.WALK_FOOT_R_M, step))
    z = hm.z
    fin = np.isfinite(z)
    zf = np.where(fin, z, 0.0)
    tol = C.WALK_FLAT_TOL_M
    # fraction of footprint cells within tol of this cell's own height:
    # counted by comparing the local min/max of a tol-band indicator.
    hi = ndi.maximum_filter(np.where(fin, z, -np.inf), footprint=foot, mode="nearest")
    lo = ndi.minimum_filter(np.where(fin, z, np.inf), footprint=foot, mode="nearest")
    flat = fin & (hi - lo <= tol)
    # a lip cell is never "flat" (its footprint spans the drop), so add the
    # support test: enough of the footprint shares this cell's height.
    n_foot = float(foot.sum())
    near = np.zeros_like(z)
    for dy, dx in zip(*np.nonzero(foot)):
        oy, ox = dy - foot.shape[0] // 2, dx - foot.shape[1] // 2
        shifted = np.roll(np.roll(zf, -oy, axis=0), -ox, axis=1)
        vmask = np.roll(np.roll(fin, -oy, axis=0), -ox, axis=1)
        near += (vmask & (np.abs(shifted - zf) <= tol)).astype(np.float64)
    support = near / n_foot
    return fin & (flat | (support >= C.WALK_SUPPORT_FRAC)), support


def reachable_mask(hm, walk, start_xy, ground_z=None):
    """Stage 2. Flood fill over `walk` from the surface the camera stands on,
    allowed to step at most MAX_TRAVERSE_STEP_M between 4-neighbours.

    MEASURED CAVEAT: in this corpus the camera routinely sits OUTSIDE the
    heightmap footprint (scene02 cut 0: eye x = -8.62 against x_range
    [-2.0, 14.0]) -- the grid covers the scene, not the approach. Clamping the
    camera cell to the grid edge and anchoring there put scene02's anchor on a
    29-cell strip of ground walled off by a 2.84 m step, and route (a) then
    reported 0 edge cells for a scene whose ground level holds 83,925 walkable
    cells. Hence REACH_ANCHOR_MODE, with both rules kept and measured
    side by side rather than one quietly replacing the other.
    """
    z = hm.z
    ny, nx = z.shape
    ix0 = int(round((start_xy[0] - hm.x0) / hm.step))
    iy0 = int(round((start_xy[1] - hm.y0) / hm.step))
    ix = int(np.clip(ix0, 0, nx - 1))
    iy = int(np.clip(iy0, 0, ny - 1))
    note = "" if (ix, iy) == (ix0, iy0) else "camera outside heightmap"
    if walk.sum() == 0:
        return np.zeros_like(walk), "no walkable cell in scene"

    at_ground = walk
    if ground_z is not None:
        near = walk & (np.abs(z - float(ground_z)) <= C.MAX_TRAVERSE_STEP_M)
        if near.any():
            at_ground = near
        else:
            note = (note + "; no walkable cell within MAX_TRAVERSE_STEP_M "
                           "of cam.ground_z").strip("; ")

    if C.REACH_ANCHOR_MODE == "largest_ground_component":
        # the ground the robot is on = the biggest connected ground-level
        # surface in the scene, not whatever cell the grid edge happens to hold.
        lab, n = ndi.label(at_ground)
        if n == 0:
            return np.zeros_like(walk), (note + "; no ground component").strip("; ")
        sizes = ndi.sum(at_ground, lab, index=np.arange(1, n + 1))
        big = int(np.argmax(sizes)) + 1
        ys, xs = np.nonzero(lab == big)
        iy, ix = int(ys[0]), int(xs[0])
        note = (note + "; anchor=largest ground component (%d cells)"
                % int(sizes[big - 1])).strip("; ")
    else:
        if not at_ground[iy, ix] or note:
            wy, wx = np.nonzero(at_ground)
            k = int(np.argmin((wy - iy) ** 2 + (wx - ix) ** 2))
            iy, ix = int(wy[k]), int(wx[k])
            note = (note + "; anchor=nearest ground cell to clamped camera"
                    ).strip("; ")

    out = np.zeros_like(walk)
    out[iy, ix] = True
    stack = [(iy, ix)]
    maxstep = C.MAX_TRAVERSE_STEP_M
    while stack:
        y, x = stack.pop()
        z0 = z[y, x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny_, nx_ = y + dy, x + dx
            if not (0 <= ny_ < ny and 0 <= nx_ < nx):
                continue
            if out[ny_, nx_] or not walk[ny_, nx_]:
                continue
            if abs(z[ny_, nx_] - z0) <= maxstep:
                out[ny_, nx_] = True
                stack.append((ny_, nx_))
    return out, note


def drop_map(hm):
    """Stage 3. z(c) - min z inside the R_RUN_M disc."""
    zf = np.where(np.isfinite(hm.z), hm.z, np.inf)
    win = _window(_cells(C.R_RUN_M, hm.step))
    lo = ndi.minimum_filter(zf, footprint=win, mode="nearest")
    return np.where(np.isfinite(hm.z), hm.z - lo, np.nan)


def local_fall(hm):
    """Stage 4. Largest one-cell 4-neighbour fall at each cell."""
    z = np.where(np.isfinite(hm.z), hm.z, np.nan)
    out = np.full(z.shape, -np.inf)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(z, -dy, axis=0), -dx, axis=1)
        out = np.fmax(out, z - nb)
    return out


def edge_cells(hm, camera_xy, ground_z=None):
    """Stages 1-4 combined -> boolean edge-cell mask + the stage counters."""
    walk, support = walkable_mask(hm)
    reach, why = reachable_mask(hm, walk, camera_xy, ground_z)
    drop = drop_map(hm)
    fall = local_fall(hm)
    mask = (reach & np.isfinite(drop) & (drop >= C.DROP_MIN_M)
            & (fall >= C.BREAK_LOCAL_FALL_M))
    diag = {"n_finite_cells": int(np.isfinite(hm.z).sum()),
            "n_walkable": int(walk.sum()), "n_reachable": int(reach.sum()),
            "n_drop_ge_thr": int(np.nansum(drop >= C.DROP_MIN_M)),
            "n_edge_cells": int(mask.sum()), "reach_note": why}
    return mask, drop, diag


# --------------------------------------------------------------------------- #
# instances
# --------------------------------------------------------------------------- #
def _order_component(pts_xy):
    """Deterministic ordering of one component's cells into a chain.

    Start at the extreme point along the component's first principal axis, then
    walk greedy-nearest-unvisited. Exact for a straight or gently curved break
    line; a self-touching component is ordered but not guaranteed optimal
    (documented as a stub in reports/P0_CODE_SKELETON.md).
    """
    P = np.asarray(pts_xy, dtype=np.float64)
    if len(P) <= 2:
        return np.arange(len(P))
    Q = P - P.mean(axis=0)
    _, _, Vt = np.linalg.svd(Q, full_matrices=False)
    t = Q @ Vt[0]
    start = int(np.argmin(t))
    order = [start]
    left = set(range(len(P))) - {start}
    cur = start
    while left:
        idx = np.fromiter(left, dtype=np.int64)
        d = ((P[idx] - P[cur]) ** 2).sum(axis=1)
        nxt = int(idx[np.argmin(d)])
        order.append(nxt)
        left.discard(nxt)
        cur = nxt
    return np.asarray(order)


def instances(hm, mask):
    """8-connected components of the edge mask, length-filtered, each returned
    as ordered 3D points."""
    lab, n = ndi.label(mask, structure=np.ones((3, 3), dtype=int))
    min_cells = _cells(C.MIN_INSTANCE_LEN_M, hm.step)
    out = []
    for k in range(1, n + 1):
        iy, ix = np.nonzero(lab == k)
        if iy.size < min_cells:
            continue
        x, y = hm.xy_of(ix, iy)
        z = hm.z[iy, ix]
        order = _order_component(np.stack([x, y], axis=1))
        pts = np.stack([x[order], y[order], z[order]], axis=1)
        out.append(pts)
    # deterministic instance order: by the first point, then length
    nd = C.SORT_KEY_DECIMALS
    out.sort(key=lambda p: (round(float(p[0, 0]), nd), round(float(p[0, 1]), nd),
                           -len(p)))
    return out, {"n_components": int(n), "n_kept": len(out), "min_cells": min_cells}


def rdp(points, tol):
    """Douglas-Peucker on a 2D pixel run (storage compaction only)."""
    P = np.asarray(points, dtype=np.float64)
    if len(P) < 3:
        return P
    a, b = P[0], P[-1]
    ab = b - a
    n = np.hypot(*ab)
    if n < 1e-9:
        d = np.hypot(*(P - a).T)
    else:
        d = np.abs(np.cross(np.broadcast_to(ab, P.shape), P - a)) / n
    i = int(np.argmax(d))
    if d[i] <= tol:
        return np.stack([a, b])
    left = rdp(P[:i + 1], tol)
    right = rdp(P[i:], tol)
    return np.concatenate([left[:-1], right], axis=0)


def visible_runs(vis, tol_px):
    """Contiguous runs of visible points -> simplified pixel polylines."""
    vmask = vis["visible"]
    runs, cur = [], []
    for i, ok in enumerate(vmask):
        if ok:
            cur.append([float(vis["px"][i]), float(vis["py"][i])])
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [[[float(a), float(b)] for a, b in rdp(r, tol_px)] for r in runs]


# --------------------------------------------------------------------------- #
# interior
# --------------------------------------------------------------------------- #
def interior_masks(cam, depth, inst_pts, lip_z, owner_ok=None):
    """Visible interior pixels per instance.

    A rendered-depth pixel is interior for instance k when
        z_world <= lip_z[k] - DROP_MIN_M
    and k is the horizontally nearest instance. Being a pixel OF THE RENDERED
    DEPTH is the visibility test -- it is by construction what the camera sees.
    """
    pts, valid = cam.unproject(depth, stride=1)
    H, W = valid.shape
    if not inst_pts:
        return [], {"n_valid_px": int(valid.sum())}
    allowed = list(range(len(inst_pts)))
    if C.INT_ASSIGN_INFRAME_ONLY and owner_ok is not None:
        allowed = [i for i in allowed if owner_ok[i]]
    if not allowed:
        return [np.zeros(valid.shape, dtype=bool) for _ in inst_pts], \
               {"n_valid_px": int(valid.sum()), "n_below_global_lip": 0,
                "n_allowed_owners": 0}
    zmax_lip = max(lip_z[i] for i in allowed)
    cand = valid & (pts[..., 2] <= zmax_lip - C.DROP_MIN_M)
    diag = {"n_valid_px": int(valid.sum()), "n_below_global_lip": int(cand.sum()),
            "n_allowed_owners": len(allowed)}
    ys, xs = np.nonzero(cand)
    out = [np.zeros((H, W), dtype=bool) for _ in inst_pts]
    if ys.size == 0:
        return out, diag
    P = pts[ys, xs]
    tree_xy = np.concatenate([inst_pts[i][:, :2] for i in allowed], axis=0)
    owner = np.concatenate([np.full(len(inst_pts[i]), i) for i in allowed])
    _, nn = cKDTree(tree_xy).query(P[:, :2], k=1)
    own = owner[nn]
    for i in allowed:
        sel = (own == i) & (P[:, 2] <= lip_z[i] - C.DROP_MIN_M)
        if sel.any():
            out[i][ys[sel], xs[sel]] = True
    return out, diag


def mask_stats(m):
    if not m.any():
        return {"int_area_px": 0, "int_h_px": 0, "int_w_px": 0}
    ys, xs = np.nonzero(m)
    return {"int_area_px": int(m.sum()),
            "int_h_px": int(ys.max() - ys.min() + 1),
            "int_w_px": int(xs.max() - xs.min() + 1)}


# --------------------------------------------------------------------------- #
# top level for one frame
# --------------------------------------------------------------------------- #
def route_a(cam, hm, depth, ids, id_table, classifier, has_sidecar,
            ground_z=None):
    """Route (a) end to end for ONE frame.

    Returns (kept, dropped, diag) where `kept` is a list of per-instance dicts
    ready for the §5 record and `dropped` records the in-frame instances that
    contributed nothing visible (kept out of edges[] so the §5 tier derivation
    still matches §2 rule 2, but never thrown away silently).
    """
    mask, drop, dg = edge_cells(hm, (cam.eye[0], cam.eye[1]), ground_z)
    inst, dg2 = instances(hm, mask)
    dg.update(dg2)

    vis_all = [V.visibility_of(cam, p, depth) for p in inst]
    lip_z = [float(np.median(p[:, 2])) for p in inst]
    owner_ok = [bool(v["in_frame"].any()) for v in vis_all]
    masks, dg3 = (interior_masks(cam, depth, inst, lip_z, owner_ok) if inst
                  else ([], {}))
    dg.update(dg3)

    kept, dropped = [], []
    for i, pts in enumerate(inst):
        vis = vis_all[i]
        occ, odiag = V.occluder_of(vis, ids, id_table, classifier, has_sidecar)
        st = mask_stats(masks[i]) if masks else {"int_area_px": 0, "int_h_px": 0,
                                                 "int_w_px": 0}
        n_vis = int(vis["visible"].sum())
        item = {"pts_3d": pts, "vis": vis, "occluder": occ, "diag": odiag,
                "int": st, "int_mask": masks[i] if masks else None,
                "lip_z": lip_z[i], "n_visible": n_vis,
                "runs": visible_runs(vis, C.RDP_TOL_PX)}
        if n_vis > 0 or st["int_area_px"] > 0:
            kept.append(item)
        elif odiag["n_in_frame"] > 0:
            dropped.append(item)
    dg["n_instances_kept"] = len(kept)
    dg["n_instances_blocked_only"] = len(dropped)
    return kept, dropped, dg


def dist_stats(cam, pts, vis):
    """Camera -> instance distance over its VISIBLE points (§5 dist_m)."""
    sel = vis["visible"]
    P = np.asarray(pts)[sel] if sel.any() else np.asarray(pts)[vis["in_frame"]]
    if len(P) == 0:
        return {"min": None, "median": None}
    d = np.linalg.norm(P - cam.eye, axis=1)
    return {"min": float(d.min()), "median": float(np.median(d))}
