# -*- coding: utf-8 -*-
"""simple_edge.py -- the SIMPLE labeler.

One job, stated the way the owner stated it:

    "From the surface I am standing on, find where the negative-obstacle danger
     starts, and draw it as ONE clean solid line. The visible drop surface is
     ONE clean unified segmentation mask."

Per frame it produces exactly two things and nothing else:

    1. danger rim  -- ordered polylines, drawn SOLID cyan where the rim is
                      actually visible and DOTTED cyan where an occluder (hedge,
                      parapet, bollard, railing) stands in front of it
    2. drop mask   -- one binary mask of the surfaces you would land on

It is deliberately self-contained. It REUSES the verified loaders and camera
model (e1_data, e1_camera) and the constant table (e1_const), and it imports
NOTHING from the complex instance machinery (labeler.py, e1_geometry,
e1_visibility, e1_schema). Every number it uses is registered in e1_const.

WHERE THE NUMBERS COME FROM (the standing rule: never invent a threshold --
take a published criterion, else derive one from measurement, else refuse to
decide and record 정할 수 없음):

    walkable level   RAMP_MAX_SLOPE = 1/12, the pedestrian ramp maximum of
                     장애인·노인·임산부 등의 편의증진 보장에 관한 법률 시행규칙
                     별표1.  ONE slope number: at or under it a surface is
                     something you walk on, over it is a face you fall against.
    landing          LANDING_MIN_M = 1.20 m, the 계단참 유효너비 of 건축물의
                     피난·방화구조 등의 기준에 관한 규칙 제15조 제1항.  A level
                     plateau that wide is a landing; anything narrower is a
                     tread (the same corpus survey puts 디딤판 at >= 0.28 m, so
                     a tread can never reach 1.20 m).
    drop threshold   DROP_MIN_M = 0.30 m [문헌·기존 확정], unchanged.
    run              R_RUN_M = 1.0 m [기존값], unchanged; sensitivity 0.5/1.0/2.0.
    occlusion margin NOT a constant.  Measured per frame as the
                     OCCL_MARGIN_PCTL-th percentile of |rendered depth - depth
                     of the plane z = ground_z| over my_surface, printed and
                     stored in meta.occlusion_margin_m.
    drawing          RDP_TOL_PX and the colours are [방법·표시전용]: they change
                     the picture only.  The stored polyline is the pixel-exact
                     projected rim, and no polyline is ever dropped for being
                     short -- the length distribution is reported instead.

Definitions (the whole spec)
----------------------------
ground_z
    variation.json -> cuts[i].cam.ground_z : the height of the surface the
    camera stands on.

walkable level
    a heightmap cell whose gradient to its 4-neighbours is at or under
    RAMP_MAX_SLOPE.  MEASURED CAVEAT, printed per frame: this corpus stores the
    heightmap on a 0.05 m grid with heights quantised to 0.05 m, so the finest
    gradient it can express between neighbours is 1.0 -- against that grid the
    1/12 criterion resolves to "level to within the grid", and a true 1/12 ramp
    would appear as level runs separated by single-cell steps.  The same
    criterion was first tried on depth-derived per-pixel normals and MEASURED
    UNFIT: on pixels the heightmap says are perfectly flat, |n_z| >= cos(atan
    (1/12)) passes only 49.5% (scene09), 69.8% (scene18), 90.0% (scene01),
    because float16 depth over a one-pixel baseline is quantisation noise at
    that angle.  The heightmap is the same source the drop test already trusts.

my_surface
    visible pixels whose back-projected XY lands on the walkable-level region
    that contains the camera's foot -- or, when the camera stands off the grid
    (it does in four of the six review frames), the walkable region nearest the
    foot in horizontal distance.  There is NO height tolerance any more: levels
    separate themselves, because the face between them is not walkable-level
    and so belongs to neither region.

danger rim
    the cells of that region which touch its boundary and have, within R_RUN_M,
    a heightmap cell at least DROP_MIN_M below ground_z.  Traced into ordered
    chains on the grid and projected into the image.  A projected rim point is
    VISIBLE when the rendered depth at its pixel is not nearer than the rim
    point itself by more than the measured occlusion margin, and HIDDEN when it
    is -- something stands in front.  Hidden rim is real danger you cannot see;
    it is drawn dotted and measured separately, never dropped.

drop mask, "v2_surfaces"  (the running definition)
    THE SURFACES YOU WOULD FALL ONTO OR INTO -- not "everything lower than
    0.3 m", which is what v1 painted and which the owner rejected for painting
    the air (on scene18 it painted the beach AND the whole sea to the horizon).

    (a) descent footprint, on the heightmap.  Seeds = cells below
        ground_z - DROP_MIN_M within R_RUN_M of a rim cell.  Flood outward
        (FOOTPRINT_CONN-connected) over cells below that line, and stop at
          (i)  cells that rise back up -- the far wall of a trench, the far bank
               of a canal.  Its FACE is painted by rule (b); its top is not.
          (ii) a SECOND descent.  Once the fill reaches a LANDING -- a
               walkable-level region wide enough to contain a disc of diameter
               LANDING_MIN_M -- it may not continue into cells more than
               DROP_MIN_M below that landing.  This is what keeps the sea out
               once the landing is the beach, and the far bank out once the
               landing is the promenade.
        A stair tread is far too narrow to be a landing, so a whole flight
        paints down to its bottom landing.  A trench bottom IS a landing and
        the far wall rises, so the fill stops there.

    (b) faces.  The mask lives on VISIBLE pixels, so it is the union of
          (1) visible pixels below the drop line whose back-projected XY falls
              inside the descent footprint -- treads, landing floor, trench
              bottom, lower yard; and
          (2) visible pixels below standing height whose XY is NOT walkable
              level (the complement of the one slope criterion -- no second
              number) and which are image-connected THROUGH SUCH PIXELS ONLY to
              (1) or to the visible rim: risers, trench and hole walls, the dock
              face.  Flooding over face pixels only is what stops a far building
              facade from joining in.
        The union is ONE mask.  No EDGE_BRIDGE_PX is involved: the riser face is
        image-adjacent to the rim it hangs from, so the two connect naturally.

drop mask, "v1_below"  (kept only for comparison, behind --mask v1)
    visible depth pixels whose 3D point is <= ground_z - DROP_MIN_M, keeping
    only the image-space components that touch the visible rim dilated by
    EDGE_BRIDGE_PX. This is the REJECTED definition; it is retained so both can
    be regenerated side by side.

tier_hint
    V   the drop mask is non-empty
    E   a visible rim, but nothing paintable
    H   a rim exists but every metre of it is hidden behind an occluder
    NEG no rim at all in this frame

CLI
---
    python3 simple_edge.py --scan-consts
    python3 simple_edge.py --frame ROUND:SCENE:L0:0000
    python3 simple_edge.py --batch                       # mask v2 (default)
    python3 simple_edge.py --batch --mask v1
    python3 simple_edge.py --batch --contact-sheet
    python3 simple_edge.py --compare-sheet               # v1 left / v2 right
"""

import argparse
import ast
import json
import math
import os
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e1_const as C          # noqa: E402
import e1_camera as CAM       # noqa: E402
import e1_data as D           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CYCLE = os.path.abspath(os.path.join(HERE, ".."))

MASK_V1 = "v1_below"
MASK_V2 = "v2_surfaces"
MASK_CHOICES = {"v1": MASK_V1, "v2": MASK_V2, MASK_V1: MASK_V1, MASK_V2: MASK_V2}
OUT_SUFFIX = {MASK_V1: "_simple", MASK_V2: "_simple_v2"}
NO_SEG = "seg 없음"
UNDET = "정할 수 없음"
T_STAIR, T_DROP, T_HOLE = "계단형", "절벽·단차형", "구멍·참호형"
TYPE_RGB = {}          # filled after e1_const is imported (see below)


def _type_rgb(t):
    return {T_STAIR: C.EDGE_RGB_STAIR, T_DROP: C.EDGE_RGB_DROPOFF,
            T_HOLE: C.EDGE_RGB_HOLE}.get(t, C.EDGE_RGB_UNKNOWN)


def out_dirs(mask_version):
    sub = OUT_SUFFIX[mask_version]
    return (os.path.join(CYCLE, "overlays", sub),
            os.path.join(CYCLE, "annotations", sub))


# The review frames. Rounds by NAME (variation_kit.round_dir); dataset paths are
# never spelled here. FRAMES is the 2x3 sheet, row-major; FRAMES_EXTRA carries
# the hidden-rim case that does not fit in a 2x3 grid.
FRAMES = [
    ("260819_main_on", "scene01", "L0", "0000"),
    ("260819_main_on", "scene18", "L0", "0000"),
    ("260819_main_on", "scene09", "L0", "0000"),
    ("260819_main_on", "scene03", "L0", "0000"),
    ("260819_main_on", "sceneD2", "L0", "0000"),
    ("260819_main_on", "sceneD1", "L0", "0000"),
]
FRAMES_EXTRA = [
    ("260824_v3w3_extbase_A", "sceneH1", "L0", "0000"),
]

NB8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
NB4 = ((-1, 0), (0, -1), (0, 1), (1, 0))
CONN8 = np.ones((3, 3), dtype=int)
CONN4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=int)


# --------------------------------------------------------------------------- #
# small array helpers
# --------------------------------------------------------------------------- #
def _shift(a, dy, dx, fill):
    """a[y+dy, x+dx] with out-of-array filled by `fill` (no wraparound)."""
    out = np.full_like(a, fill)
    ys_src = slice(max(dy, 0), a.shape[0] + min(dy, 0))
    xs_src = slice(max(dx, 0), a.shape[1] + min(dx, 0))
    ys_dst = slice(max(-dy, 0), a.shape[0] + min(-dy, 0))
    xs_dst = slice(max(-dx, 0), a.shape[1] + min(-dx, 0))
    out[ys_dst, xs_dst] = a[ys_src, xs_src]
    return out


def _disc(radius_m, step_m):
    r = max(int(round(radius_m / step_m)), 1)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (yy * yy + xx * xx) <= r * r


def _rdp(pts, tol):
    """Ramer-Douglas-Peucker on an ordered (N,2) float array. DRAWING ONLY."""
    pts = np.asarray(pts, dtype=np.float64)
    n = len(pts)
    if n < 3:
        return pts.copy()
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        seg = b - a
        L = math.hypot(seg[0], seg[1])
        rel = pts[i + 1:j] - a
        if L > 0:
            d = np.abs(rel[:, 0] * seg[1] - rel[:, 1] * seg[0]) / L
        else:
            d = np.hypot(rel[:, 0], rel[:, 1])
        k = int(np.argmax(d))
        if d[k] > tol:
            m = i + 1 + k
            keep[m] = True
            stack.append((i, m))
            stack.append((m, j))
    return pts[keep]


def _trace_component(coords):
    """Order one 8-connected cell component into a single chain.

    Double BFS: farthest cell A from an arbitrary start, then the path from A to
    the cell farthest from A. Side spurs are dropped, which is exactly what "one
    clean line" asks for. Ties always break on the smallest (row, col), so two
    runs give the identical chain.
    """
    idx = {(int(a), int(b)) for a, b in coords}

    def bfs(src):
        dist = {src: 0}
        parent = {src: None}
        queue = [src]
        head = 0
        while head < len(queue):
            cur = queue[head]
            head += 1
            cy, cx = cur
            for dy, dx in NB8:
                nxt = (cy + dy, cx + dx)
                if nxt in idx and nxt not in dist:
                    dist[nxt] = dist[cur] + 1
                    parent[nxt] = cur
                    queue.append(nxt)
        far = max(dist, key=lambda p: (dist[p], -p[0], -p[1]))
        return far, parent

    start = min(idx)
    a, _ = bfs(start)
    b, parent = bfs(a)
    chain = []
    node = b
    while node is not None:
        chain.append(node)
        node = parent[node]
    chain.reverse()
    return chain


def _polyline_len(pts):
    if len(pts) < 2:
        return 0.0
    p = np.asarray(pts, dtype=np.float64)
    return float(np.hypot(*(p[1:] - p[:-1]).T).sum())


def _raster(shape, runs):
    """Boolean image with every run's segments drawn 1 px wide."""
    out = np.zeros(shape, dtype=bool)
    H, W = shape
    for pts in runs:
        p = np.asarray(pts, dtype=np.float64)
        for i in range(len(p) - 1):
            a, b = p[i], p[i + 1]
            n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
            t = np.linspace(0.0, 1.0, n)
            xs = np.round(a[0] + (b[0] - a[0]) * t).astype(np.int64)
            ys = np.round(a[1] + (b[1] - a[1]) * t).astype(np.int64)
            ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
            out[ys[ok], xs[ok]] = True
    return out


# --------------------------------------------------------------------------- #
# the heightmap side: walkable level, the region under my feet, the rim
# --------------------------------------------------------------------------- #
def walkable_cells(hm):
    """Cells whose local gradient is at or under the 1/12 ramp maximum.

    Missing neighbours (grid border, nodata) impose no constraint -- a cell is
    not called a face just because the map ends next to it.
    """
    z = hm.z
    fin = np.isfinite(z)
    grad = np.zeros(z.shape, dtype=np.float64)
    for dy, dx in NB4:
        nb = _shift(z, dy, dx, np.nan)
        d = np.abs(nb - z) / hm.step
        grad = np.maximum(grad, np.where(np.isfinite(d), d, 0.0))
    return fin & (grad <= C.RAMP_MAX_SLOPE)


def foot_region(hm, walk, eye_xy, ground_z):
    """The walkable-level region the camera is standing on.

    Literally 'the region containing the camera's foot' whenever the foot is on
    the grid. In this corpus the camera routinely stands OUTSIDE the heightmap
    footprint (four of the six review frames), so the fallback is the region
    whose nearest cell is closest to the foot in horizontal distance -- the same
    thing, continued off the grid, with no threshold to invent.
    """
    lab, n = ndimage.label(walk, structure=CONN4)
    info = {"walk_regions": int(n), "foot_on_grid": False,
            "foot_region_dist_m": None, "foot_region_z_m": None,
            "ground_z_unmatched": False}
    if n == 0:
        return np.zeros(walk.shape, dtype=bool), info
    # A candidate region must sit at the height the renderer RECORDED for this
    # cut. cam.ground_z is data, not a guess, and a surface a whole hazard drop
    # away from it is by this project's own definition a different level -- so
    # the test reuses DROP_MIN_M and invents no tolerance of its own.
    at_level = np.abs(hm.z - ground_z) < C.DROP_MIN_M
    hits = np.bincount(lab[walk & at_level].ravel(), minlength=n + 1)
    hits[0] = 0
    ix = int(round((eye_xy[0] - hm.x0) / hm.step))
    iy = int(round((eye_xy[1] - hm.y0) / hm.step))
    if (0 <= ix < hm.nx and 0 <= iy < hm.ny and walk[iy, ix]
            and hits[lab[iy, ix]] > 0):
        info["foot_on_grid"] = True
        info["foot_region_dist_m"] = 0.0
        k = int(lab[iy, ix])
    else:
        gx, gy = hm.xy_of(np.arange(hm.nx)[None, :], np.arange(hm.ny)[:, None])
        dist = np.hypot(gx - eye_xy[0], gy - eye_xy[1])
        dmin = np.asarray(ndimage.minimum(dist, lab, index=np.arange(1, n + 1)))
        gated = np.where(hits[1:] > 0, dmin, np.inf)
        if np.isfinite(gated).any():
            k = int(np.argmin(gated)) + 1
        else:
            # MEASURED CONFLICT, reported not hidden: no cell of the heightmap
            # lies within a hazard drop of the ground_z the renderer recorded.
            # Cause on sceneH1: the camera stands 3.48 m OUTSIDE the grid, so
            # cam.ground_z (0.998 m) describes ground the map does not cover,
            # while the nearest mapped surface sits at 0.620 m. Falling back to
            # the nearest walkable region keeps the frame labelled; the 0.378 m
            # disagreement is recorded in meta.ground_z_mismatch_m.
            info["ground_z_unmatched"] = True
            k = int(np.argmin(dmin)) + 1
        info["foot_region_dist_m"] = float(dmin[k - 1])
    sel = lab == k
    info["foot_region_z_m"] = float(np.median(hm.z[sel]))
    return sel, info


def rim_cells(hm, region, ground_z):
    """Region cells on its boundary that fall DROP_MIN_M within R_RUN_M when you
    walk OUTWARD from them.

    The direction matters. Asking only whether some cell within R_RUN_M is low
    enough (a disc minimum) marks the ground beside every debris block that
    happens to sit within a metre of a trench: measured on sceneD2, that read
    423 rim cells in 49 chains, most of them a ring around a piece of rubble.
    Walking outward along the local boundary normal -- the same construction the
    image-space labeler used -- is what the spec says and leaves only real rim.

    Returns (rim mask, {cell -> its outward profile}) so the profile is computed
    once and reused to type the edge.
    """
    outside = np.zeros(region.shape, dtype=bool)
    for dy, dx in NB4:
        outside |= ~_shift(region, dy, dx, False)
    bnd = region & outside
    keep = np.zeros(region.shape, dtype=bool)
    prof = {}
    for iy, ix in map(tuple, np.argwhere(bnd)):
        pr = outward_profile(hm, [(iy, ix)], region, ground_z)
        if pr is None:
            continue
        prof[(iy, ix)] = pr
        if pr["cum_descent_m"] >= C.DROP_MIN_M:
            keep[iy, ix] = True
    return keep, prof


def landing_cells(hm, walk):
    """Walkable-level regions wide enough to hold a disc of LANDING_MIN_M.

    That is the code's 계단참 유효너비 read as an extent: a plateau you could
    stand on and stop. A stair tread (<= 0.32 m deep) cannot contain such a
    disc; a floor, beach or yard contains it many times over.
    """
    lab, n = ndimage.label(walk, structure=CONN4)
    if n == 0:
        return np.zeros(walk.shape, dtype=bool)
    edt = ndimage.distance_transform_edt(walk) * hm.step
    widest = np.asarray(ndimage.maximum(edt, lab, index=np.arange(1, n + 1)))
    ok = np.concatenate(([False], widest >= C.LANDING_MIN_M * 0.5))
    return ok[lab]


def outward_profile(hm, cells, region, ground_z):
    """Height profile beyond a rim cell, outward along the local rim normal.

    The outward direction is the mean unit step, in world XY, from the cell to
    its 4-neighbours that are NOT in my region -- the same construction the
    image-space labeler used, moved onto the grid. Returns, per cell, the size
    of the FIRST descending step, how many separate descending steps the run
    contains, and the cumulative fall inside R_RUN_M. All three are read
    straight off the heightmap; nothing is fitted.
    """
    n = max(int(round(C.R_RUN_M / hm.step)), 1)
    ks = (np.arange(n) + 1) * hm.step
    firsts, cums, nsteps = [], [], []
    for iy, ix in cells:
        vx = vy = 0.0
        cnt = 0
        for dy, dx in NB4:
            jy, jx = iy + dy, ix + dx
            out = not (0 <= jy < hm.ny and 0 <= jx < hm.nx) or not region[jy, jx]
            if out:
                d = math.hypot(dx, dy)
                vx += dx / d
                vy += dy / d
                cnt += 1
        if not cnt or (vx == 0 and vy == 0):
            continue
        d = math.hypot(vx, vy)
        vx, vy = vx / d, vy / d
        x0, y0 = hm.xy_of(ix, iy)
        z = np.concatenate(([hm.z[iy, ix]],
                            hm.sample(x0 + vx * ks, y0 + vy * ks)))
        if not np.isfinite(z[0]):
            continue
        # Nodata is a hole in the AABB probe, not the end of the ground, so the
        # non-finite samples are DROPPED and the walk continues. Measured need:
        # scene18 carries a one-cell nodata seam (321 cells) exactly along the
        # promenade's seaward edge, and truncating at the first hole skipped all
        # 704 boundary cells, which turned the headline frame into NEG.
        z = z[np.isfinite(z)]
        if len(z) < len(NB4) // 2:
            continue
        drop = z[:-1] - z[1:]
        steps, cur = [], 0.0
        for v in drop:
            if v > 0:
                cur += v
            elif cur > 0:
                steps.append(cur)
                cur = 0.0
        if cur > 0:
            steps.append(cur)
        firsts.append(steps[0] if steps else 0.0)
        nsteps.append(len(steps))
        cums.append(float(z[0] - z.min()))
    if not firsts:
        return None
    return {"first_step_m": float(np.median(firsts)),
            "cum_descent_m": float(np.median(cums)),
            "n_steps": float(np.median(nsteps)),
            "n_cells_profiled": len(firsts)}


def classify_edge(prof, enclosed):
    """Edge type from the ground profile beyond it. Sourced criteria only.

    구멍·참호형  the lower ground reached is ENCLOSED -- every cell bounding its
                 descent footprint is within R_RUN_M of my own level, and the
                 footprint never runs off the grid. Most specific, so first.
    절벽·단차형  the first step is itself at least DROP_MIN_M (0.30 m
                 [문헌·기존 확정]): one fall, already a hazard.
    계단형       the first step is under RISER_MAX_M (0.20 m, 주택건설기준 등에
                 관한 규정 제16조 제1항 옥외계단 단높이) AND the fall reaches
                 DROP_MIN_M inside R_RUN_M over two or more steps.
    정할 수 없음 anything else -- a ramp-like descent, or a profile the AABB
                 heightmap does not resolve. Not forced into a class.
    """
    if prof is None:
        return UNDET
    if enclosed:
        return T_HOLE
    if prof["first_step_m"] >= C.DROP_MIN_M:
        return T_DROP
    if (prof["first_step_m"] < C.RISER_MAX_M
            and prof["cum_descent_m"] >= C.DROP_MIN_M
            and prof["n_steps"] >= len(NB4) // 2):
        return T_STAIR
    return UNDET


def descent_footprint(hm, ground_z, seeds, land):
    """Where you would end up if you went over the rim.

    Flood over cells below ground_z - DROP_MIN_M. Each cell carries `land_z`,
    the height of the most recent landing on the way to it (-inf until the first
    landing). A step into a cell more than DROP_MIN_M below its land_z is a
    SECOND DESCENT and is refused; a cell that is not below the drop line is a
    wall and is refused.

    Implemented as a monotone label-correcting relaxation over the whole grid:
    every cell keeps the LOWEST land_z any admissible path can deliver, which is
    the most permissive, so the footprint is exactly 'some admissible path
    reaches here'. It converges to the unique least fixed point, so the answer
    does not depend on visiting order and two runs agree bit for bit.
    """
    z = hm.z
    below = np.isfinite(z) & (z <= ground_z - C.DROP_MIN_M)
    info = {"seed_cells": 0, "footprint_cells": 0, "landing_cells_in_footprint": 0,
            "first_landing_z_m": None, "lowest_landing_z_m": None,
            "stopped_wall_cells": 0, "stopped_second_descent_cells": 0,
            "below_cells_total": int(below.sum())}
    seeds = seeds & below
    info["seed_cells"] = int(seeds.sum())
    if not seeds.any():
        return np.zeros(z.shape, dtype=bool), info

    best = np.where(seeds, np.where(land, z, -np.inf), np.inf)
    nbrs = NB4 if C.FOOTPRINT_CONN == len(NB4) else NB8
    while True:
        cur = best
        for dy, dx in nbrs:
            cand = _shift(cur, -dy, -dx, np.inf)
            with np.errstate(invalid="ignore"):
                allow = below & (z >= cand - C.DROP_MIN_M)
            newlz = np.where(land, z, cand)
            cur = np.where(allow & (newlz < cur), newlz, cur)
        if np.array_equal(cur, best, equal_nan=True):
            break
        best = cur
    foot = below & (best < np.inf)
    info["footprint_cells"] = int(foot.sum())
    lf = foot & land
    info["landing_cells_in_footprint"] = int(lf.sum())
    if lf.any():
        info["first_landing_z_m"] = float(np.max(z[lf]))
        info["lowest_landing_z_m"] = float(np.min(z[lf]))
    grown = np.zeros(z.shape, dtype=bool)
    for dy, dx in nbrs:
        grown |= _shift(foot, dy, dx, False)
    rim = grown & ~foot
    info["stopped_wall_cells"] = int((rim & ~below).sum())
    info["stopped_second_descent_cells"] = int((rim & below).sum())
    return foot, info


# --------------------------------------------------------------------------- #
# the image side: occlusion margin, rim projection
# --------------------------------------------------------------------------- #
def plane_depth(cam, ground_z):
    """z-depth at which each pixel ray meets the plane z = ground_z (NaN above
    the horizon). Same ray convention as CameraModel.unproject."""
    un = (np.arange(cam.W) + 0.5 - cam.cx) / cam.fx
    vn = (np.arange(cam.H) + 0.5 - cam.cy) / cam.fy
    UN, VN = np.meshgrid(un, vn)
    dirs = UN[..., None] * cam.r + VN[..., None] * (-cam.u) + cam.f
    dz = dirs[..., 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (ground_z - cam.eye[2]) / dz
    return np.where(np.isfinite(t) & (t > 0), t, np.nan)


def occlusion_margin(pz, zcell, surf):
    """How far the rendered surface may sit from the geometry before the
    difference means 'something is standing in front of it'.

    MEASURED, not chosen: the OCCL_MARGIN_PCTL-th percentile of
    |z_backprojected - z of the heightmap cell it lands on| over my_surface.
    That is exactly the error the occlusion test faces -- how far the RENDER
    disagrees with the HEIGHTMAP the rim came from -- and it is measured as a
    HEIGHT because height is the well-conditioned quantity: read along the ray
    the same residual explodes near the horizon (measured on scene03: 1.33 m,
    against 0.001-0.006 m on frames without a grazing horizon), which would have
    made the test meaningless there. Each rim point converts this height
    tolerance into its own depth tolerance through its own ray geometry.

    Returns (margin_height_m, n_samples), or (None, 0) when the frame offers
    nothing to measure on -- the caller then records 정할 수 없음.
    """
    res = np.abs(pz - zcell)
    m = surf & np.isfinite(res)
    if not m.any():
        return None, 0
    return float(np.percentile(res[m], C.OCCL_MARGIN_PCTL)), int(m.sum())


def rim_chains(hm, rim, cam, depth, ground_z, margin, idseg, idtable):
    """Project the rim cells into the image and split them into visible and
    hidden runs.

    Returns (chains, raster_visible, totals). Each chain records the pixel-exact
    projected path, a per-point visibility flag, the two lengths and, when an
    idseg sidecar exists, which prims are standing in front of the hidden part.
    """
    # How much depth error a rim point carries. Two data-derived terms, no
    # chosen number: it is known only to within HALF A HEIGHTMAP CELL
    # horizontally (HM_STEP_SOURCE -- step is READ per scene, 0.05 m here) and
    # to within the MEASURED render-vs-heightmap residual vertically. Both are
    # height/position errors, and the depth error they cause depends on how
    # grazing the ray is: a ray that meets the ground at a shallow angle turns a
    # centimetre of position into decimetres of depth. The conversion factor is
    # the ray's own zc / |P_z - eye_z|. Ignoring it was measured to mark half of
    # scene01's plainly visible plaza lip as "hidden".
    unc = None if margin is None else (hm.step * 0.5 + margin)
    tols = []
    chains, vis_runs, hid_runs = [], [], []
    tot = {"rim_cells": int(rim.sum()), "occlusion_tol_m": None,
           "undecided_len_px": 0.0, "visible_len_px": 0.0,
           "hidden_len_px": 0.0, "offscreen_pts": 0, "undecided_pts": 0}
    if not rim.any():
        return chains, np.zeros(depth.shape, dtype=bool), tot
    lab, n = ndimage.label(rim, structure=CONN8)
    order = []
    for k in range(1, n + 1):
        left = set(map(tuple, np.argwhere(lab == k).tolist()))
        parts = []
        while len(left) >= len(NB4) // 2:
            ch = _trace_component(np.asarray(sorted(left)))
            parts.append(ch)
            left -= set(ch)
        for cells in parts:
            iy = np.asarray([c[0] for c in cells], dtype=np.int64)
            ix = np.asarray([c[1] for c in cells], dtype=np.int64)
            wx, wy = hm.xy_of(ix, iy)
            P = np.stack([wx, wy, hm.z[iy, ix]], axis=-1)
            px, py, zc, inb = cam.project(P)
            # -2 off frame, -1 undecided, 0 hidden, 1 visible
            state = np.full(len(cells), -2, dtype=np.int64)
            if unc is None:
                state[inb] = -1
                tot["undecided_pts"] += int(inb.sum())
            else:
                # position uncertainty -> depth tolerance along THIS ray
                rise = np.abs(P[:, 2] - cam.eye[2])
                with np.errstate(divide="ignore", invalid="ignore"):
                    tol = unc * zc / rise
                usable = inb & np.isfinite(tol)
                dr = cam.depth_at(depth, px, py)
                seen = np.isfinite(dr) & (dr >= zc - tol)
                state[usable & seen] = 1
                state[usable & ~seen] = 0
                tot["undecided_pts"] += int((inb & ~usable).sum())
                if usable.any():
                    tols.extend(tol[usable].tolist())
            tot["offscreen_pts"] += int((~inb).sum())
            pts = [[float(a), float(b)] for a, b in zip(px, py)]
            ch = {"px": [[round(a, C.JSON_DECIMALS), round(b, C.JSON_DECIMALS)]
                         for a, b in pts],
                  "visible": [int(s) for s in state],
                  "visible_len_px": 0.0, "hidden_len_px": 0.0,
                  "undecided_len_px": 0.0,
                  "edge_type": UNDET, "profile": None,
                  "occluder_prims": NO_SEG if idseg is None else [],
                  "_cells": cells}
            occ = set()

            def _flush(run, cls):
                if cls is None or len(run) < len(NB4) // 2:
                    return
                L = _polyline_len(run)
                if cls == 1:
                    vis_runs.append(run)
                    ch["visible_len_px"] += L
                elif cls == 0:
                    hid_runs.append(run)
                    ch["hidden_len_px"] += L
                elif cls == -1:
                    ch["undecided_len_px"] += L

            run, cls = [], None
            for i, st in enumerate(state):
                if st != cls:
                    _flush(run, cls)
                    run, cls = [pts[i]], st
                else:
                    run.append(pts[i])
                if st == 0 and idseg is not None:
                    xi = int(min(max(round(px[i] - 0.5), 0), cam.W - 1))
                    yi = int(min(max(round(py[i] - 0.5), 0), cam.H - 1))
                    occ.add(int(idseg[yi, xi]))
            _flush(run, cls)
            if idseg is not None:
                ch["occluder_prims"] = sorted({idtable.get(i, "id %d" % i) for i in occ})
            ch["visible_len_px"] = round(ch["visible_len_px"], C.JSON_DECIMALS)
            ch["hidden_len_px"] = round(ch["hidden_len_px"], C.JSON_DECIMALS)
            ch["undecided_len_px"] = round(ch["undecided_len_px"], C.JSON_DECIMALS)
            tot["undecided_len_px"] = (tot.get("undecided_len_px", 0.0)
                                       + ch["undecided_len_px"])
            tot["visible_len_px"] += ch["visible_len_px"]
            tot["hidden_len_px"] += ch["hidden_len_px"]
            order.append((-(ch["visible_len_px"] + ch["hidden_len_px"]),
                          ch["px"][0], ch))
    order.sort(key=lambda t: (t[0], t[1]))
    chains = [t[2] for t in order]
    tot["visible_len_px"] = round(tot["visible_len_px"], C.JSON_DECIMALS)
    tot["hidden_len_px"] = round(tot["hidden_len_px"], C.JSON_DECIMALS)
    tot["occlusion_tol_m"] = float(np.median(tols)) if tols else None
    tot["n_chains"] = len(chains)
    return chains, _raster(depth.shape, vis_runs), tot


def runs_of(chain, want):
    """The drawable runs of one visibility class, simplified for DRAWING ONLY."""
    out, run = [], []
    for p, s in zip(chain["px"], chain["visible"]):
        if s == want:
            run.append(p)
        else:
            if len(run) >= len(NB4) // 2:
                out.append(_rdp(run, C.RDP_TOL_PX).tolist())
            run = []
    if len(run) >= len(NB4) // 2:
        out.append(_rdp(run, C.RDP_TOL_PX).tolist())
    return out


# --------------------------------------------------------------------------- #
# the labeler
# --------------------------------------------------------------------------- #
def resolve_frame(sdir, tier, idx):
    """The cut whose file is <tier>__<seed>__<idx>.png -- the seed differs per
    round, so it is matched, never spelled."""
    hits = sorted(c["file"] for c in D.list_cuts(sdir)
                  if c["file"].startswith(tier + "__") and
                  c["file"].endswith("__" + idx + ".png"))
    if not hits:
        raise KeyError("[simple] no %s cut %s in %s" % (tier, idx, sdir))
    return hits[0]


def label_frame(round_name, scene_id, tier, idx, edge_bridge_px=None,
                mask_version=None):
    """Everything for one frame. Returns (record, drop mask, rim raster, rgb)."""
    bridge = C.EDGE_BRIDGE_PX if edge_bridge_px is None else int(edge_bridge_px)
    mv = MASK_CHOICES[mask_version or C.MASK_VERSION_DEFAULT]
    sdir = D.scene_dir(round_name, scene_id)
    fname = resolve_frame(sdir, tier, idx)
    cut = D.find_cut(sdir, fname)
    assets = D.frame_assets(sdir, cut)
    if not (assets["has_depth"] and assets["has_heightmap"]):
        raise RuntimeError("[simple] %s/%s/%s lacks depth or heightmap"
                           % (round_name, scene_id, fname))

    depth = D.load_depth(assets["depth_path"])
    hm = CAM.HeightMap.load(sdir)
    cam = CAM.CameraModel(cut["cam"], width=depth.shape[1], height=depth.shape[0])
    ground_z = float(cut["cam"]["ground_z"])
    drop_line_z = ground_z - C.DROP_MIN_M
    idseg, idtable = D.load_idseg(assets["idseg_path"])

    # -- 1. walkable level, my region, the rim ---------------------------- #
    hm_dz = None
    for _dy, _dx in NB4:
        _d = np.abs(_shift(hm.z, _dy, _dx, np.nan) - hm.z)
        _d = _d[np.isfinite(_d) & (_d > 0)]
        if _d.size:
            hm_dz = float(_d.min()) if hm_dz is None else min(hm_dz, float(_d.min()))
    walk = walkable_cells(hm)
    region, reg_info = foot_region(hm, walk, cam.eye, ground_z)
    # Every heightmap test runs against the height the MAP gives my own region,
    # not the one recorded beside the camera. The two agree to under a
    # millimetre on five of the six review frames; where they do not (sceneH1,
    # 0.378 m, camera 3.48 m off the grid) the map has to win, because the rim,
    # the drop line and the footprint are all read off the map.
    cam_ground_z = ground_z
    if reg_info["foot_region_z_m"] is not None:
        ground_z = reg_info["foot_region_z_m"]
    drop_line_z = ground_z - C.DROP_MIN_M
    rim, rim_prof = rim_cells(hm, region, ground_z)
    land = landing_cells(hm, walk)

    pts, valid = cam.unproject(depth, stride=1)
    valid = valid & (depth <= C.DEPTH_MAX_M)
    pz = pts[..., 2]
    cx_i = np.round((pts[..., 0] - hm.x0) / hm.step)
    cy_i = np.round((pts[..., 1] - hm.y0) / hm.step)
    on_grid = valid & (cx_i >= 0) & (cx_i < hm.nx) & (cy_i >= 0) & (cy_i < hm.ny)
    gy, gx = np.nonzero(on_grid)
    gi = cx_i[gy, gx].astype(np.int64)
    gj = cy_i[gy, gx].astype(np.int64)

    def by_cell(grid):
        out = np.zeros(depth.shape, dtype=bool)
        out[gy, gx] = grid[gj, gi]
        return out

    # A pixel whose XY lands on a cell of my region but which SHOWS something a
    # whole hazard drop away is not my surface: the AABB heightmap does not dig
    # out every opening (HM_SOURCE_NOTE), and on sceneD2 192,733 pixels of a pit
    # floor at z = -2.99 m mapped onto yard cells. The consistency test uses the
    # sanctioned DROP_MIN_M -- the project's own definition of "a different
    # level" -- not a new tolerance of its own.
    surf = by_cell(region) & (np.abs(pz - ground_z) < C.DROP_MIN_M)
    surf_area = int(surf.sum())

    # -- 2. the measured occlusion margin --------------------------------- #
    zcell = np.full(depth.shape, np.nan)
    zcell[gy, gx] = hm.z[gj, gi]
    # The residual is measured on every visible pixel that lands on MAPPED,
    # walkable ground and agrees with the map to within a hazard drop -- not
    # only on my own region. Reason, measured: on sceneH1 the camera stands
    # 3.48 m outside the grid, my_surface is 0 px, and restricting the
    # measurement to it left the whole frame unclassifiable. The consistency
    # gate is DROP_MIN_M, the same sanctioned number used everywhere else, and
    # it is what keeps an unmapped pit floor (sceneD2, 192,733 px at z=-2.99 m
    # sitting on yard cells) out of the statistic.
    margin, margin_n = occlusion_margin(pz, zcell, surf)
    margin_set = "my_surface"
    if margin is None:
        # my_surface can be empty: on sceneH1 the camera stands 3.48 m outside
        # the grid and only 8.2% of its visible pixels land on the map at all,
        # none of them on walkable ground. Rather than give the frame up, the
        # residual is then measured on every visible pixel that lands on MAPPED
        # ground and agrees with the map to within a hazard drop -- the same
        # DROP_MIN_M gate used everywhere else -- and the substitution is
        # recorded in meta.occlusion_margin_measured_on, not hidden.
        margin, margin_n = occlusion_margin(
            pz, zcell, np.isfinite(zcell) & valid
            & (np.abs(pz - zcell) < C.DROP_MIN_M))
        margin_set = "mapped_ground" if margin is not None else UNDET

    # -- 3. project the rim, split visible / hidden ----------------------- #
    chains, rim_vis, rim_tot = rim_chains(hm, rim, cam, depth, ground_z, margin,
                                          idseg, idtable)

    # -- 4. the drop mask -------------------------------------------------- #
    below = valid & (pz <= drop_line_z)
    drop = np.zeros(depth.shape, dtype=bool)
    v2 = None
    gap_px = None
    if rim_vis.any() and below.any():
        gap_px = float(ndimage.distance_transform_edt(~below)[rim_vis].min())

    if mv == MASK_V1:
        if rim_vis.any() and below.any():
            near = ndimage.binary_dilation(rim_vis, np.ones((3, 3), dtype=bool),
                                           iterations=bridge)
            lab_d, _ = ndimage.label(below, structure=CONN8)
            touched = np.unique(lab_d[near & below])
            touched = touched[touched > 0]
            if touched.size:
                drop = np.isin(lab_d, touched)
    else:
        run_disc = _disc(C.R_RUN_M, hm.step)
        seeds = ndimage.binary_dilation(rim, run_disc)
        foot, v2 = descent_footprint(hm, ground_z, seeds, land)
        # ---- edge type, per chain, from the ground profile beyond it ------ #
        flab, fn = ndimage.label(foot, structure=CONN4)
        near_mine = ndimage.binary_dilation(region, run_disc)
        border = np.zeros(foot.shape, dtype=bool)
        border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
        enclosed_comp = np.zeros(fn + 1, dtype=bool)
        for c in range(1, fn + 1):
            F = flab == c
            ring = np.zeros(foot.shape, dtype=bool)
            for dy, dx in NB4:
                ring |= _shift(F, dy, dx, False)
            ring &= ~F
            enclosed_comp[c] = bool(not (F & border).any() and ring.any()
                                    and bool((ring & ~near_mine).sum() == 0))
        for ch in chains:
            cmask = np.zeros(foot.shape, dtype=bool)
            for iy, ix in ch["_cells"]:
                cmask[iy, ix] = True
            lbl = flab[ndimage.binary_dilation(cmask, run_disc) & foot]
            lbl = lbl[lbl > 0]
            enc = False
            if lbl.size:
                enc = bool(enclosed_comp[int(np.bincount(lbl).argmax())])
            prof = outward_profile(hm, ch["_cells"], region, ground_z)
            ch["profile"] = (None if prof is None
                             else _round_floats(prof, C.JSON_DECIMALS))
            ch["enclosed"] = enc
            ch["edge_type"] = classify_edge(prof, enc)
        on_foot = below & by_cell(foot)
        faces = np.zeros(depth.shape, dtype=bool)
        steep = valid & (pz <= ground_z) & by_cell(~walk)
        anchor = on_foot | rim_vis
        if steep.any() and anchor.any():
            touch = ndimage.binary_dilation(anchor,
                                            np.ones((3, 3), dtype=bool)) & steep
            lab_s, _ = ndimage.label(steep, structure=CONN8)
            hit = np.unique(lab_s[touch])
            hit = hit[hit > 0]
            if hit.size:
                faces = np.isin(lab_s, hit)
        drop = on_foot | faces
        v2["mask_footprint_px"] = int(on_foot.sum())
        v2["mask_face_px"] = int(faces.sum())
        v2["mask_face_only_px"] = int((faces & ~on_foot).sum())
        v2["footprint_area_m2"] = v2["footprint_cells"] * hm.step * hm.step
        v2["below_px_not_painted"] = int((below & ~drop).sum())
    mask_area = int(drop.sum())

    # -- 5. numbers -------------------------------------------------------- #
    min_dist = None
    if rim.any():
        ry, rx = np.nonzero(rim)
        wx, wy = hm.xy_of(rx, ry)
        min_dist = float(np.min(np.hypot(wx - cam.eye[0], wy - cam.eye[1])))
    vis_len, hid_len = rim_tot["visible_len_px"], rim_tot["hidden_len_px"]
    h_hint = bool(hid_len > 0 and vis_len == 0)
    und_len = round(rim_tot.get("undecided_len_px", 0.0), C.JSON_DECIMALS)
    if mask_area > 0:
        tier_hint = "V"
    elif vis_len > 0:
        tier_hint = "E"
    elif hid_len > 0:
        tier_hint = "H"
    elif rim_tot["rim_cells"] > 0:
        # a rim is there; whether it can be seen could not be decided
        tier_hint = UNDET
    else:
        tier_hint = "NEG"

    for ch in chains:
        ch.pop("_cells", None)
    dp = C.JSON_DECIMALS
    lens = sorted(round(c["visible_len_px"] + c["hidden_len_px"], dp)
                  for c in chains)
    meta = {
        "round": round_name, "scene": scene_id, "file": fname,
        "split": os.path.basename(os.path.dirname(sdir)),
        "rgb_path": D.rel_to_repo(assets["rgb_path"]),
        "depth_path": D.rel_to_repo(assets["depth_path"]),
        "ground_z_m": round(ground_z, dp),
        "cam_ground_z_m": round(cam_ground_z, dp),
        "ground_z_mismatch_m": round(abs(ground_z - cam_ground_z), dp),
        "ground_z_unmatched": reg_info["ground_z_unmatched"],
        "drop_line_z_m": round(drop_line_z, dp),
        "hm_step_m": round(hm.step, dp),
        "hm_min_nonzero_dz_m": (None if hm_dz is None else round(hm_dz, dp)),
        "walk_cells": int(walk.sum()),
        "walk_regions": reg_info["walk_regions"],
        "foot_on_grid": reg_info["foot_on_grid"],
        "foot_region_dist_m": (None if reg_info["foot_region_dist_m"] is None
                               else round(reg_info["foot_region_dist_m"], dp)),
        "foot_region_z_m": (None if reg_info["foot_region_z_m"] is None
                            else round(reg_info["foot_region_z_m"], dp)),
        "region_cells": int(region.sum()),
        "surface_area_px": surf_area,
        "occlusion_margin_m": ("정할 수 없음" if margin is None
                               else round(margin, dp)),
        "occlusion_margin_n_px": margin_n,
        "occlusion_margin_measured_on": margin_set,
        "occlusion_margin_pctl": C.OCCL_MARGIN_PCTL,
        "occlusion_tol_m": (UNDET if rim_tot["occlusion_tol_m"] is None
                            else round(rim_tot["occlusion_tol_m"], dp)),
        "rim_cells": rim_tot["rim_cells"],
        "n_chains": rim_tot.get("n_chains", 0),
        "chain_len_px_sorted": lens,
        "rim_pts_offscreen": rim_tot["offscreen_pts"],
        "rim_pts_undecided": rim_tot["undecided_pts"],
        "idseg": (NO_SEG if idseg is None else D.rel_to_repo(assets["idseg_path"])),
        "n_below_px_total": int(below.sum()),
        "edge_to_below_gap_px": (None if gap_px is None else round(gap_px, dp)),
        "edge_bridge_px": (bridge if mv == MASK_V1 else None),
        "rdp_tol_px_display_only": C.RDP_TOL_PX,
        "const_fingerprint": C.fingerprint(),
    }
    if v2 is not None:
        meta["descent"] = v2
    rec = {
        "frame": "%s__%s__%s" % (round_name, scene_id, fname[:-len(".png")]),
        "mask_version": mv,
        "edges": chains,
        "edge_len_px": round(vis_len, dp),
        "hidden_len_px": round(hid_len, dp),
        "undecided_len_px": und_len,
        "mask_area_px": mask_area,
        "min_edge_dist_m": None if min_dist is None else round(min_dist, dp),
        "tier_hint": tier_hint,
        "h_hint": h_hint,
        "meta": meta,
    }
    return rec, drop, rim_vis, assets["rgb_path"]


# --------------------------------------------------------------------------- #
# drawing
# --------------------------------------------------------------------------- #
def _font(size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(C.SIMPLE_FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def _dashes(run, dash, gap):
    """Split a polyline into dash-length pieces separated by gap-length holes."""
    out, cur, carry, drawing = [], [], 0.0, True
    p = np.asarray(run, dtype=np.float64)
    if len(p) < 2:
        return out
    cur = [tuple(p[0])]
    for i in range(len(p) - 1):
        a, b = p[i], p[i + 1]
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        t0 = 0.0
        while seg - t0 > 0:
            want = (dash if drawing else gap) - carry
            if t0 + want >= seg:
                carry += seg - t0
                if drawing:
                    cur.append((float(b[0]), float(b[1])))
                break
            t0 += want
            f = t0 / seg
            q = (float(a[0] + (b[0] - a[0]) * f), float(a[1] + (b[1] - a[1]) * f))
            if drawing:
                cur.append(q)
                out.append(cur)
                cur = []
            else:
                cur = [q]
            drawing = not drawing
            carry = 0.0
    if drawing and len(cur) >= len(NB4) // 2:
        out.append(cur)
    return out


def blend(rgb_path, drop):
    """RGB + translucent magenta mask + a thin dark-magenta outline."""
    from PIL import Image
    img = Image.open(rgb_path).convert("RGB")
    arr = np.asarray(img).astype(np.float64)
    if drop.any():
        fill = np.asarray(C.SIMPLE_MASK_RGB, dtype=np.float64)
        a = C.SIMPLE_MASK_ALPHA
        arr[drop] = arr[drop] * (1.0 - a) + fill * a
        er = ndimage.binary_erosion(drop, np.ones((3, 3), dtype=bool))
        arr[drop & ~er] = np.asarray(C.SIMPLE_MASK_OUTLINE_RGB, dtype=np.float64)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def render_overlay(rgb_path, rec, drop, tile_w=None, caption=True):
    """RGB + magenta drop mask + cyan rim (solid where visible, dotted where
    hidden) + one caption. Nothing else goes on this image.

    `tile_w` re-renders at that width: the mask is blended at full resolution
    and resampled, then the rim is STROKED AT THE TILE SCALE, so a 3 px line is
    still 3 px on the contact sheet instead of a downscaled ghost.
    """
    from PIL import Image, ImageDraw
    img = blend(rgb_path, drop)
    scale = 1.0
    if tile_w and tile_w != img.width:
        scale = tile_w / float(img.width)
        img = img.resize((tile_w, int(round(img.height * scale))), Image.LANCZOS)
    dr = ImageDraw.Draw(img)

    def stroke(run, colour, width):
        if len(run) >= len(NB4) // 2:
            dr.line([(p[0] * scale, p[1] * scale) for p in run],
                    fill=tuple(colour), width=width, joint="curve")

    for ch in rec["edges"]:
        col = _type_rgb(ch["edge_type"])
        for run in runs_of(ch, 0):
            for d in _dashes(run, C.SIMPLE_HIDDEN_DASH_PX, C.SIMPLE_HIDDEN_GAP_PX):
                stroke(d, C.SIMPLE_EDGE_HALO_RGB,
                       C.SIMPLE_HIDDEN_LINE_PX + C.SIMPLE_EDGE_HALO_PX * 2)
                stroke(d, col, C.SIMPLE_HIDDEN_LINE_PX)
        for run in runs_of(ch, -1):
            for d in _dashes(run, C.SIMPLE_HIDDEN_DASH_PX, C.SIMPLE_HIDDEN_GAP_PX):
                stroke(d, C.SIMPLE_EDGE_HALO_RGB,
                       C.SIMPLE_HIDDEN_LINE_PX + C.SIMPLE_EDGE_HALO_PX * 2)
                stroke(d, C.EDGE_RGB_UNKNOWN, C.SIMPLE_HIDDEN_LINE_PX)
        for run in runs_of(ch, 1):
            stroke(run, C.SIMPLE_EDGE_HALO_RGB,
                   C.OVERLAY_LINE_PX + C.SIMPLE_EDGE_HALO_PX * 2)
            stroke(run, col, C.OVERLAY_LINE_PX)
    if not caption:
        return img

    dist = rec["min_edge_dist_m"]
    cap = ("%s   rim %.0f px vis / %.0f px hidden   mask %d px   dist %s m   [%s]"
           % (rec["meta"]["scene"], rec["edge_len_px"], rec["hidden_len_px"],
              rec["mask_area_px"],
              ("--" if dist is None else "%.2f" % dist), rec["tier_hint"]))
    px = max(int(round(C.SIMPLE_CAPTION_PX * scale)), C.SHEET_LABEL_PX // 2)
    fnt = _font(px)
    W, H = img.size
    band = px * 2
    dr.rectangle([0, H - band, W, H], fill=(0, 0, 0))
    dr.text((px // 2, H - band + px // 3), cap, font=fnt, fill=(255, 255, 255))
    return img


def draw_overlay(rgb_path, rec, drop, out_png):
    render_overlay(rgb_path, rec, drop).save(out_png)
    return out_png


def draw_legend(dr, x0, y0, w, h, fnt):
    """4 type swatches + the dotted-line note, on one strip."""
    items = [(T_STAIR, C.EDGE_RGB_STAIR), (T_DROP, C.EDGE_RGB_DROPOFF),
             (T_HOLE, C.EDGE_RGB_HOLE), (UNDET, C.EDGE_RGB_UNKNOWN)]
    pad = h // 4
    sw = h // 2
    x = x0 + pad
    ymid = y0 + h // 2
    for name, col in items:
        dr.rectangle([x, ymid - sw // 2, x + sw * 2, ymid + sw // 2],
                     fill=tuple(col), outline=(0, 0, 0))
        x += sw * 2 + pad
        dr.text((x, ymid - sw // 2), name, font=fnt, fill=(255, 255, 255))
        x += int(dr.textlength(name, font=fnt)) + sw
    for k in range(x, min(x + sw * 2, x0 + w), sw // 2):
        dr.line([k, ymid, k + sw // 4, ymid], fill=(255, 255, 255),
                width=C.SIMPLE_HIDDEN_LINE_PX)
    dr.text((x + sw * 2 + pad, ymid - sw // 2), "점선 = 가려짐 (hidden rim)",
            font=fnt, fill=(255, 255, 255))
    dr.text((x0 + pad, y0 + h - pad - sw // 2),
            "마스크 = 자홍색 (내려앉을 면)", font=fnt,
            fill=tuple(C.SIMPLE_MASK_RGB))


def grid_sheet(records, out_jpg, cols, rows, label_px=None, tile_w=None):
    """A cols x rows grid of overlays, scene name above each, legend below."""
    from PIL import Image, ImageDraw
    tw = tile_w or C.SHEET_TILE_W_PX
    lab = label_px or C.SHEET_V2_LABEL_PX
    fnt = _font(lab)
    lab_h = lab * 2
    leg_h = lab * 3
    tiles = [(render_overlay(r["_rgb"], r, r["_drop"], tile_w=tw), r)
             for r in records]
    th = max(t.height for t, _ in tiles)
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab_h) + leg_h),
                      tuple(C.SHEET_BG_RGB))
    dr = ImageDraw.Draw(sheet)
    for i, (t, rec) in enumerate(tiles):
        cx, cy = i % cols, i // cols
        x0, y0 = cx * tw, cy * (th + lab_h)
        dr.text((x0 + lab // 3, y0 + lab // 3),
                "%s   [%s]   mask %d px" % (rec["meta"]["scene"],
                                            rec["tier_hint"], rec["mask_area_px"]),
                font=fnt, fill=(255, 255, 255))
        sheet.paste(t, (x0, y0 + lab_h))
    draw_legend(dr, 0, rows * (th + lab_h), cols * tw, leg_h, fnt)
    sheet.save(out_jpg, quality=C.SHEET_JPEG_QUALITY, optimize=True)
    return out_jpg


def _crop_at(img, cxy, side):
    W, H = img.size
    x = int(min(max(cxy[0] - side // 2, 0), max(W - side, 0)))
    y = int(min(max(cxy[1] - side // 2, 0), max(H - side, 0)))
    return img.crop((x, y, min(x + side, W), min(y + side, H)))


def near_rim_pixel(rim_vis):
    """The visible rim pixel nearest the camera: largest row, then smallest
    column. Deterministic, and on a trench rim it is the near corner."""
    ys, xs = np.nonzero(rim_vis)
    if ys.size == 0:
        return None
    y = int(ys.max())
    return (int(xs[ys == y].min()), y)


def compare_sheet(out_jpg, bridge, crop_scene="sceneD2"):
    """v1 (left) vs v2 (right) for the six frames, plus a 1:1 crop of the
    sceneD2 near rim: the PREVIOUS shipped overlay (still on disk under
    overlays/_simple/) beside the new one, so the line's move onto the rim
    corner can be read at full resolution. Evidence only -- writes no label.
    """
    from PIL import Image, ImageDraw
    tw = C.SHEET_TILE_W_PX
    fnt = _font(C.SHEET_V2_LABEL_PX)
    lab_h = C.SHEET_V2_LABEL_PX * 2
    rows, crops = [], []
    for spec in FRAMES:
        r1, d1, k1, rgb = label_frame(*spec, edge_bridge_px=bridge,
                                      mask_version=MASK_V1)
        r2, d2, k2, _ = label_frame(*spec, mask_version=MASK_V2)
        rows.append((r1, d1, r2, d2, rgb))
        if spec[1] == crop_scene:
            p = near_rim_pixel(k2)
            old = os.path.join(CYCLE, "overlays", "_simple",
                               r2["frame"] + ".overlay.png")
            if p is not None:
                if os.path.exists(old):
                    crops.append((_crop_at(Image.open(old).convert("RGB"), p,
                                           C.CROP_ZOOM_PX),
                                  "%s BEFORE (shipped v1 overlay)" % crop_scene))
                crops.append((_crop_at(render_overlay(rgb, r2, d2, caption=False),
                                       p, C.CROP_ZOOM_PX),
                              "%s AFTER  rim px (%d,%d)" % (crop_scene, p[0], p[1])))
    tiles = [(render_overlay(rgb, r1, d1, tile_w=tw),
              render_overlay(rgb, r2, d2, tile_w=tw), r1, r2)
             for (r1, d1, r2, d2, rgb) in rows]
    th = max(max(a.height, b.height) for a, b, _, _ in tiles)
    crop_h = (max(c.height for c, _ in crops) + lab_h) if crops else 0
    sheet = Image.new("RGB", (tw * 2, len(tiles) * (th + lab_h) + crop_h),
                      tuple(C.SHEET_BG_RGB))
    dr = ImageDraw.Draw(sheet)
    for i, (a, b, r1, r2) in enumerate(tiles):
        y0 = i * (th + lab_h)
        dr.text((C.SHEET_V2_LABEL_PX // 3, y0 + C.SHEET_V2_LABEL_PX // 3),
                "%s   v1 %d px   ->   v2 %d px"
                % (r2["meta"]["scene"], r1["mask_area_px"], r2["mask_area_px"]),
                font=fnt, fill=(255, 255, 255))
        sheet.paste(a, (0, y0 + lab_h))
        sheet.paste(b, (tw, y0 + lab_h))
    x = 0
    for img, name in crops:
        y0 = len(tiles) * (th + lab_h)
        dr.text((x + C.SHEET_V2_LABEL_PX // 3, y0 + C.SHEET_V2_LABEL_PX // 3),
                name, font=fnt, fill=(255, 255, 255))
        sheet.paste(img, (x, y0 + lab_h))
        x += img.width
    sheet.save(out_jpg, quality=C.SHEET_JPEG_QUALITY, optimize=True)
    return out_jpg


# --------------------------------------------------------------------------- #
# io
# --------------------------------------------------------------------------- #
def _round_floats(o, dp):
    if isinstance(o, float):
        return round(o, dp)
    if isinstance(o, dict):
        return {k: _round_floats(v, dp) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round_floats(v, dp) for v in o]
    return o


def dump_json(rec, path):
    body = {k: v for k, v in rec.items() if not k.startswith("_")}
    txt = json.dumps(_round_floats(body, C.JSON_DECIMALS),
                     sort_keys=C.CONSTANTS["JSON_SORT_KEYS"][0],
                     ensure_ascii=False, indent=C.JSON_DECIMALS // 2) + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(txt)
    return txt.encode("utf-8")


def run_one(round_name, scene_id, tier, idx, mask_version=None, quiet=False):
    from PIL import Image
    mv = MASK_CHOICES[mask_version or C.MASK_VERSION_DEFAULT]
    ovdir, andir = out_dirs(mv)
    os.makedirs(ovdir, exist_ok=True)
    os.makedirs(andir, exist_ok=True)
    rec, drop, rim_vis, rgb_path = label_frame(round_name, scene_id, tier, idx,
                                               mask_version=mv)
    stem = rec["frame"]
    dump_json(rec, os.path.join(andir, stem + ".simple_edge.json"))
    mp = os.path.join(ovdir, stem + ".dropmask.png")
    Image.fromarray((drop.astype(np.uint8) * 255)).save(mp)
    op = draw_overlay(rgb_path, rec, drop, os.path.join(ovdir, stem + ".overlay.png"))
    rec["_overlay"], rec["_mask"] = op, mp
    rec["_rgb"], rec["_drop"] = rgb_path, drop
    m = rec["meta"]
    if not quiet:
        print("[simple] %-46s gz=%+.3f  walk=%6d cells in %d region(s), mine=%6d "
              "(foot %s)  surf=%7d px  rim=%4d cells -> %d chain(s)  "
              "vis %6.0f px / hidden %6.0f px  mask=%7d px  dist=%s  [%s]%s"
              % (stem, m["ground_z_m"], m["walk_cells"], m["walk_regions"],
                 m["region_cells"],
                 ("on grid" if m["foot_on_grid"]
                  else (UNDET if m["foot_region_dist_m"] is None
                        else "%.2f m off grid" % m["foot_region_dist_m"])),
                 m["surface_area_px"], m["rim_cells"],
                 m["n_chains"], rec["edge_len_px"], rec["hidden_len_px"],
                 rec["mask_area_px"],
                 ("--" if rec["min_edge_dist_m"] is None
                  else "%.2f m" % rec["min_edge_dist_m"]), rec["tier_hint"],
                 "  H_hint" if rec["h_hint"] else ""))
        print("         occlusion: measured height residual p%d on %d %s px "
              "= %s m -> median depth tolerance %s m (with half a %.2f m "
              "heightmap cell, converted per ray)"
              % (m["occlusion_margin_pctl"], m["occlusion_margin_n_px"],
                 m["occlusion_margin_measured_on"], m["occlusion_margin_m"],
                 m["occlusion_tol_m"], m["hm_step_m"]))
        for ch in rec["edges"]:
            pr = ch["profile"]
            if ch["visible_len_px"] + ch["hidden_len_px"] <= 0:
                continue
            print("         edge %-12s len %6.0f px (vis %5.0f / hid %5.0f)  "
                  "first step %s m, %s step(s), falls %s m in R_RUN, enclosed=%s"
                  % (ch["edge_type"], ch["visible_len_px"] + ch["hidden_len_px"],
                     ch["visible_len_px"], ch["hidden_len_px"],
                     "--" if pr is None else "%.2f" % pr["first_step_m"],
                     "--" if pr is None else "%.0f" % pr["n_steps"],
                     "--" if pr is None else "%.2f" % pr["cum_descent_m"],
                     ch["enclosed"]))
        occ = sorted({p for c in rec["edges"] if c["occluder_prims"] != NO_SEG
                      for p in c["occluder_prims"]})
        if rec["hidden_len_px"] > 0:
            print("         hidden rim occluded by: %s"
                  % (", ".join(occ) if occ else NO_SEG))
        if "descent" in m:
            d = m["descent"]
            print("         descent: footprint %d cells (%.1f m2) from %d seed "
                  "cell(s); landings %d cells, first landing z=%s m, lowest %s m;"
                  " stopped by wall %d / second descent %d"
                  % (d["footprint_cells"], d["footprint_area_m2"], d["seed_cells"],
                     d["landing_cells_in_footprint"],
                     ("--" if d["first_landing_z_m"] is None
                      else "%.2f" % d["first_landing_z_m"]),
                     ("--" if d["lowest_landing_z_m"] is None
                      else "%.2f" % d["lowest_landing_z_m"]),
                     d["stopped_wall_cells"], d["stopped_second_descent_cells"]))
            print("         mask = footprint %d px + faces %d px (%d face-only); "
                  "below-drop px NOT painted %d of %d"
                  % (d["mask_footprint_px"], d["mask_face_px"],
                     d["mask_face_only_px"], d["below_px_not_painted"],
                     m["n_below_px_total"]))
    return rec


def r_run_sensitivity():
    """R_RUN_M is a carried constant, so it is measured rather than argued."""
    print("[simple] R_RUN_M sensitivity -- rim cells / visible px / mask px")
    keep = C.R_RUN_M
    print("   %-46s %s" % ("frame", "  ".join("%22s" % ("R_RUN_M=%.1f" % v)
                                              for v in C.CONSTANTS["R_RUN_M"][3])))
    try:
        for spec in FRAMES + FRAMES_EXTRA:
            row = []
            for v in C.CONSTANTS["R_RUN_M"][3]:
                C.R_RUN_M = v
                rec, _, _, _ = label_frame(*spec)
                row.append("%6d %7.0f %8d" % (rec["meta"]["rim_cells"],
                                              rec["edge_len_px"],
                                              rec["mask_area_px"]))
            print("   %-46s %s" % ("%s/%s" % (spec[0], spec[1]), "  ".join(row)))
    finally:
        C.R_RUN_M = keep
    return 0


# --------------------------------------------------------------------------- #
def scan_consts():
    """e1_selftest --scan-consts globs e1_*.py only, and that module may not be
    edited, so simple_edge.py scans itself under the identical rule."""
    path = os.path.join(HERE, "simple_edge.py")
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    bad = [(n.lineno, n.value) for n in ast.walk(tree)
           if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
           and not isinstance(n.value, bool)
           and n.value not in C.STRUCTURAL_OK and -n.value not in C.STRUCTURAL_OK]
    print("[simple] unledgered numeric literals in simple_edge.py: %d" % len(bad))
    for ln, v in bad:
        print("   ! simple_edge.py:%d  %r" % (ln, v))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="the simple negative-obstacle labeler")
    ap.add_argument("--frame", help="ROUND:SCENE:TIER:IDX")
    ap.add_argument("--batch", action="store_true", help="the six review frames")
    ap.add_argument("--extra", action="store_true", help="also the hidden-rim frame")
    ap.add_argument("--mask", choices=("v1", "v2"), default=None,
                    help="drop-mask definition; default %s" % C.MASK_VERSION_DEFAULT)
    ap.add_argument("--contact-sheet", action="store_true")
    ap.add_argument("--compare-sheet", action="store_true",
                    help="v1 vs v2 evidence sheet (writes no label)")
    ap.add_argument("--compare-bridge", type=int, default=None)
    ap.add_argument("--scan-consts", action="store_true")
    ap.add_argument("--r-run-sweep", action="store_true")
    a = ap.parse_args(argv)
    mv = MASK_CHOICES[a.mask or C.MASK_VERSION_DEFAULT]

    if a.scan_consts:
        return scan_consts()
    if a.r_run_sweep:
        return r_run_sensitivity()
    if a.compare_sheet:
        ovdir, _ = out_dirs(MASK_V2)
        os.makedirs(ovdir, exist_ok=True)
        b = C.EDGE_BRIDGE_PX if a.compare_bridge is None else a.compare_bridge
        out = compare_sheet(os.path.join(ovdir, "sheet_v1_vs_v2.jpg"), b)
        print("[simple] comparison sheet %s  (%.2f MB, v1 column at "
              "EDGE_BRIDGE_PX=%d)"
              % (out, os.path.getsize(out) / float(C.BYTES_PER_MB), b))
        return 0

    recs, extra = [], []
    if a.frame:
        recs.append(run_one(*a.frame.split(":"), mask_version=mv))
    if a.batch:
        for spec in FRAMES:
            recs.append(run_one(*spec, mask_version=mv))
    if a.extra:
        for spec in FRAMES_EXTRA:
            extra.append(run_one(*spec, mask_version=mv))
    if a.contact_sheet:
        if not recs:
            raise SystemExit("[simple] --contact-sheet needs --batch")
        ovdir, _ = out_dirs(mv)
        name = "sheet_v2.jpg" if mv == MASK_V2 else "contact_sheet.jpg"
        budget = C.SHEET_V2_MAX_MB if mv == MASK_V2 else C.SHEET_MAX_MB
        out = grid_sheet(recs, os.path.join(ovdir, name), 3, 2)
        mb = os.path.getsize(out) / float(C.BYTES_PER_MB)
        print("[simple] contact sheet %s  (%.2f MB, budget %.1f MB, %s)"
              % (out, mb, budget, "OK" if mb <= budget else "OVER BUDGET"))
        if extra:
            hid = [r for r in recs if r["meta"]["scene"] == "scene03"] + extra
            out2 = grid_sheet(hid, os.path.join(ovdir, "sheet_v2_hidden.jpg"),
                              len(hid), 1)
            print("[simple] hidden-rim sheet %s  (%.2f MB)"
                  % (out2, os.path.getsize(out2) / float(C.BYTES_PER_MB)))
    if not (a.frame or a.batch or a.extra):
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
