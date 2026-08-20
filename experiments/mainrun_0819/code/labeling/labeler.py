#!/usr/bin/env python3
"""Derive polar GT (D3/D5/D10) + V/E/H tiers (D6) for every cut of both toggle arms.

GT source : per-scene TWIN heightmap DIFF (footprint v2, D10) --
            footprint_raw = {z_off(x,y) - z_on(x,y) >= hazard_depth}, i.e. the
            hazard-off arm is the counterfactual walkable surface, so a scene
            that simply SLOPES away from the camera produces no footprint at all.
            A near-boundary STEP gate then drops components that fall gradually
            (ramps) and keeps the ones that fall >= hazard_depth within
            STEP_RUN_M of the lip (stairs, vertical drops).  What survives is
            projected into the camera-frame polar grid (`--grid`, default
            gridspec_v0.json; gridspec_v1.json = the D19 20-cell refinement).
Tier source: depth reprojection (int_px, referenced to z_off) + near-edge
            polyline visibility.
D14        : the gated footprint remains the training GT (`polar_gt`), and the
            same wedge test is run a second time on the RAW pre-gate footprint
            (`polar_gt_pregate` + `gate_excluded`) so that nothing the step gate
            removes is lost -- reverting the gate is a field swap, not a redo.

Camera convention is taken VERBATIM from the render driver
(`variation_kit.dir_of` + `variation_kit.look_at_rows`, quoted in cam_basis()).
"""
import argparse, json, math, os, re, sys
import numpy as np

W_IMG, H_IMG = 1920, 1080

# --------------------------------------------------------------------------- #
# CONSTANTS -- single source of truth.  Rationales are DECISIONS.md D10/D11;
# nothing below may be re-spelled as a literal further down the file.
# --------------------------------------------------------------------------- #
INTERIOR_MARGIN_M = 0.15
"""D11(1) interior margin. A reprojected pixel counts as drop INTERIOR only when
it sits >= 0.15 m below the counterfactual walkable surface z_off (v2; was
cam.ground_z in v0).  0.15 m is above the corpus ground-displacement ceiling
(ground_kit delta_max measured 0.113 m, scene02 log) and below half the 0.3 m
hazard threshold -- the midpoint that separates ground texture / displacement
noise from a genuine interior surface."""

RIM_TOL_M = 0.35
"""D11(2) rim depth tolerance. A projected lip point counts as directly seen when
the rendered depth agrees within 0.35 m.  Absorbs f16 depth quantisation
(~0.016 m at <= 16 m) + the 5 cm heightmap grid times local slope + the 3x3
window sampling of a 1-px-wide lip; empirically stable (0.175 detected on the
real probe).  PROVISIONAL: at the 0.3 m minimum drop it can confuse lip with
floor, so it is a morning sensitivity-sweep candidate."""

LIP_MAX_PTS = 200
"""D11(3) lip sample budget. 200 points is ~1:1 with the 5 cm grid along a ~10 m
lip and holds the measured 0.24 s/frame whole-stack cost."""

STEP_RUN_M = 1.0
"""D10 step-gate run length. Horizontal distance, measured outward from the lip
along the toward-camera normal, inside which z_on must fall by the hazard depth
for a footprint component to count as a step.  Stairs (0.15-0.18 m risers) clear
it within ~2-3 treads; a ramp reaching -1.0 m over 8 m never does."""

LIP_WALL_TOP_M = 0.3
"""Lip filter (v0, unchanged): the lip's walkable side must not stand more than
this above the cut's approach_z -- higher means a wall top, not a drop lip."""

LIP_MIN_PROJ = 8
"""Minimum lip points landing in frame before edge_ratio is reported at all."""

DS = 4                 # depth downsample factor for int_px
TAU_INT = (1, 50, 200)
TAU_EDGE = (0.02, 0.05, 0.10)
TAU_INT_DEF, TAU_EDGE_DEF = 50, 0.05   # taus used for tier_strict
HM_DEFAULT = dict(x0=-2.0, y0=-8.0, step=0.05)

GT_SOURCE_FMT = "derived-heightmapdiff-{grid}-PROVISIONAL"
GT_SOURCE = GT_SOURCE_FMT.format(grid="gridv0")
"""Legacy constant = the v0 string, kept so an importer that never sees a
gridspec still gets the historical value.  Everything that HAS a gridspec must
call `gt_source_of(grid)` instead: the grid identity belongs in the provenance
string, so a V1 run is not silently stamped `gridv0` (D19 / DAYRUN Phase 1)."""
FOOTPRINT_VERSION = "v2-diff-stepgate"
TIER_SOURCE = "derived-depth-v0-strict"
GATE_POLICY = "train-on-gated; pregate preserved per D14"
"""D14(2) gate policy.  The training GT (`polar_gt`) stays the GATED footprint, but
the same wedge test is ALSO run on the raw pre-gate footprint and kept alongside
(`polar_gt_pregate` + `gate_excluded`).  A morning decision to revert the step
gate is then a field swap, not a re-derivation."""
CAM_SRC = ("CAM_CONVENTION.md sec.2/sec.6 == variation_kit.dir_of + look_at_rows "
           "(driver code, HEAD 8c814db); VERIFIED on 260819_patchprobe_on/scene04, "
           "median |z_recon - ground_z| = 0.0001 m")


# --------------------------------------------------------------------------- #
# camera
# --------------------------------------------------------------------------- #
def cam_basis(yaw, pitch, roll):
    """World-frame (right, up, forward) unit vectors, mirroring the driver:

        dir_of(y,p)   = (cos p cos y, cos p sin y, sin p)          # forward
        right         = normalize(cross(fwd, +Z)) = (f_y, -f_x, 0)
        up            = cross(right, fwd)
        roll          : r2 = r*cos+u*sin ; u2 = -r*sin+u*cos

    Image +x follows `right`, image +y (row index) follows `-up`.
    """
    y, p, rl = math.radians(yaw), math.radians(pitch), math.radians(roll)
    f = np.array([math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), math.sin(p)])
    r = np.array([f[1], -f[0], 0.0])
    r /= (np.linalg.norm(r) or 1.0)
    u = np.cross(r, f)
    cr, sr = math.cos(rl), math.sin(rl)
    return r * cr + u * sr, -r * sr + u * cr, f


def focal_px(hfov_deg):
    return (W_IMG * 0.5) / math.tan(math.radians(hfov_deg) * 0.5)


def unproject(dep, eye, cam, step=1):
    """z-depth image (distance_to_image_plane) -> world points (H',W',3)."""
    r, u, f = cam_basis(cam["yaw"], cam["pitch"], cam["roll"])
    fx = focal_px(cam["hfov"])
    d = np.asarray(dep, dtype=np.float64)[::step, ::step]
    un = (np.arange(0, W_IMG, step) + 0.5 - W_IMG * 0.5) / fx
    vn = (np.arange(0, H_IMG, step) + 0.5 - H_IMG * 0.5) / fx
    UN, VN = np.meshgrid(un[:d.shape[1]], vn[:d.shape[0]])
    dirs = UN[..., None] * r + VN[..., None] * (-u) + f      # z-component == 1
    return np.asarray(eye) + d[..., None] * dirs, np.isfinite(d) & (d > 0.01) & (d < 300.0)


def project(pts, eye, cam):
    """World points (N,3) -> (px, py, z_cam, in_frame)."""
    r, u, f = cam_basis(cam["yaw"], cam["pitch"], cam["roll"])
    fx = focal_px(cam["hfov"])
    rel = np.asarray(pts, dtype=np.float64) - np.asarray(eye)
    zc, xc, yc = rel @ f, rel @ r, rel @ (-u)
    front = zc > 0.05
    z = np.where(front, zc, 1.0)
    px = W_IMG * 0.5 + fx * xc / z
    py = H_IMG * 0.5 + fx * yc / z
    inb = front & (px >= 0) & (px < W_IMG) & (py >= 0) & (py < H_IMG)
    return px, py, zc, inb


# --------------------------------------------------------------------------- #
# polar grid
# --------------------------------------------------------------------------- #
def n_cells(grid):
    """Cells in this gridspec.  The ONLY place the count is computed."""
    return int(grid["n_bands"]) * int(grid["n_sectors"])


def grid_slug(grid):
    """`PROVISIONAL-GRID-V1` -> `gridv1` (provenance-string fragment).

    The V0 spelling is load-bearing: `gt_source_of(gridspec_v0)` must reproduce the
    historical `derived-heightmapdiff-gridv0-PROVISIONAL` byte for byte, or every
    mainrun_0819 artefact stops matching its own labels.
    """
    v = str(grid.get("version", "")).upper()
    m = re.search(r"GRID-?(V[0-9A-Z]+)", v)
    return "grid" + (m.group(1).lower() if m else
                     re.sub(r"[^a-z0-9]+", "", v.lower()) or "unknown")


def gt_source_of(grid):
    """Provenance string for labels derived on `grid`.  Carries the grid identity
    so a V1 label file can never be mistaken for a V0 one downstream."""
    return GT_SOURCE_FMT.format(grid=grid_slug(grid))


def polar_cells(XX, YY, eye, yaw, grid):
    """Cell index per grid point (-1 = outside every wedge), plus az/range.

    Band and sector counts come from `grid` alone -- no cell count is spelled as
    a literal anywhere in this stack, so V0 (3x5=15) and V1 (4x5=20) are the same
    code path with a different json.
    """
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    dx, dy = XX - eye[0], YY - eye[1]
    xc, yc = dx * cy + dy * sy, -dx * sy + dy * cy      # rotate by -yaw about Z
    az = np.degrees(np.arctan2(yc, xc))
    rng = np.hypot(xc, yc)
    asc = np.asarray(grid["sector_edges_deg"][::-1])
    k = np.searchsorted(asc, az, side="right") - 1
    b = np.searchsorted(np.asarray(grid["band_edges_m"]), rng, side="right") - 1
    ns, nb = grid["n_sectors"], grid["n_bands"]
    ok = (k >= 0) & (k < ns) & (b >= 0) & (b < nb)
    return np.where(ok, b * ns + (ns - 1 - k), -1), rng


def _adj4(mask, other):
    """mask & (any 4-neighbour in `other`)."""
    a = np.zeros_like(other)
    a[1:, :] |= other[:-1, :]; a[:-1, :] |= other[1:, :]
    a[:, 1:] |= other[:, :-1]; a[:, :-1] |= other[:, 1:]
    return mask & a


# --------------------------------------------------------------------------- #
# heightmaps (twin pair)
# --------------------------------------------------------------------------- #
def load_heightmap(sdir):
    """(z grid, (x0, y0, step), source) for one scene-arm.

    A `heightmap_fused.npy` sidecar, when present, WINS over `heightmap.npy`.
    The AABB map is a single top-down ray per cell, so a hazard under a roof,
    deck or canopy is measured as the structure top on BOTH arms and the D10
    twin difference vanishes; `fuse_heightmap.py` re-measures those scenes from
    the per-cut depth sidecars on the identical lattice.  The choice is made per
    scene-arm and reported as `hm_source` -- nothing else in this file changes,
    the twin diff and the step gate simply operate on whichever map loads.
    """
    fp = os.path.join(sdir, "heightmap_fused.npy")
    fused = os.path.isfile(fp)
    base = "heightmap_fused" if fused else "heightmap"
    hm = np.load(os.path.join(sdir, base + ".npy")).astype(np.float64)
    mp = os.path.join(sdir, base + "_meta.json")
    meta = json.load(open(mp)) if os.path.isfile(mp) else {}
    return hm, (float(meta.get("x0", HM_DEFAULT["x0"])),
                float(meta.get("y0", HM_DEFAULT["y0"])),
                float(meta.get("step", HM_DEFAULT["step"]))), \
        ("fused" if fused else "aabb")


def align_to(hm_src, geo_src, geo_dst, shape_dst):
    """Nearest-cell resample of one arm's heightmap onto the other arm's grid.

    A no-op whenever the two sidecars share (x0, y0, step, shape) -- which is the
    normal case, both arms being sampled by the same driver code.  Cells with no
    source cell become NaN, i.e. void, i.e. excluded from the footprint.
    """
    if geo_src == geo_dst and hm_src.shape == tuple(shape_dst):
        return hm_src
    (x0s, y0s, sts), (x0d, y0d, std) = geo_src, geo_dst
    ny, nx = shape_dst
    gx = np.rint((x0d + np.arange(nx) * std - x0s) / sts).astype(np.int64)
    gy = np.rint((y0d + np.arange(ny) * std - y0s) / sts).astype(np.int64)
    kx, ky = (gx >= 0) & (gx < hm_src.shape[1]), (gy >= 0) & (gy < hm_src.shape[0])
    out = np.full(shape_dst, np.nan)
    out[np.ix_(ky, kx)] = hm_src[np.ix_(gy[ky], gx[kx])]
    return out


try:                                                     # optional fast path
    from scipy.ndimage import label as _scipy_label
except Exception:                                        # pragma: no cover
    _scipy_label = None
_CC4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def connected_components(mask):
    """4-connected component ids (0 = background) + count."""
    if not mask.any():
        return np.zeros(mask.shape, np.int32), 0
    if _scipy_label is not None:
        lab, n = _scipy_label(mask, structure=_CC4)
        return lab.astype(np.int32), int(n)
    lab = np.zeros(mask.shape, np.int32)                 # pragma: no cover
    par = [0]

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a

    ny, nx = mask.shape
    for y in range(ny):
        for x in range(nx):
            if not mask[y, x]:
                continue
            up = lab[y - 1, x] if y else 0
            lf = lab[y, x - 1] if x else 0
            if up and lf:
                lab[y, x] = min(up, lf)
                ra, rb = find(up), find(lf)
                if ra != rb:
                    par[max(ra, rb)] = min(ra, rb)
            elif up or lf:
                lab[y, x] = up or lf
            else:
                par.append(len(par)); lab[y, x] = len(par) - 1
    roots = np.array([find(i) for i in range(len(par))])
    uniq = {r: i + 1 for i, r in enumerate(sorted(set(roots[1:])))}
    remap = np.array([0] + [uniq[roots[i]] for i in range(1, len(par))], np.int32)
    return remap[lab], len(uniq)


def _outward(XX, YY, eye):
    """Unit cell step toward the camera (the walkable side of a near lip)."""
    dx, dy = eye[0] - XX, eye[1] - YY
    n = np.hypot(dx, dy); n[n == 0] = 1.0
    return np.rint(dx / n).astype(np.int32), np.rint(dy / n).astype(np.int32)


def _near_boundary(seed, fp, void, ox, oy):
    """Cells of `seed` whose toward-camera 4-neighbour is walkable ground.

    Returns (iy, ix, jy, jx): i = the footprint (far) side, j = the walkable
    (near) side.  `seed` selects which footprint cells are considered (the lip
    extractor narrows it to the polar grid); "walkable" is always judged against
    the FULL footprint, so a neighbour that is footprint-but-out-of-grid is not
    mistaken for standing ground.
    """
    iy, ix = np.nonzero(seed)
    if iy.size == 0:
        return (np.zeros(0, np.int64),) * 4
    jy, jx = iy + oy[iy, ix], ix + ox[iy, ix]
    ny, nx = fp.shape
    m = (jy >= 0) & (jy < ny) & (jx >= 0) & (jx < nx)
    iy, ix, jy, jx = iy[m], ix[m], jy[m], jx[m]
    m = (~fp[jy, jx]) & (~void[jy, jx])
    return iy[m], ix[m], jy[m], jx[m]


def step_gate(fp, comp, n_raw, void, hm_on, ox, oy, st, hz):
    """D10 near-boundary STEP gate, applied per connected component.

    For every near-boundary cell we walk the inward ray (away from the camera,
    into the component) out to STEP_RUN_M of horizontal distance -- 20 cells on
    the 5 cm grid for an axis-aligned normal, 14 for a diagonal one -- and take
    the largest fall of z_on below the walkable-side height.  A component is kept
    when ANY of its boundary cells sees a fall of at least `hz` inside that run:
    stairs and vertical drops qualify, a gradual ramp never does.

    Returns (kept mask, stats dict).  `comps_no_boundary` is the diagnostic that
    separates "failed the step test" from "the camera never saw a near rim of
    this component at all" (component walled in by void or by the map edge).
    """
    stat = dict(comps_raw=n_raw, comps_kept=0, comps_no_boundary=0,
                boundary_cells=0, boundary_pass=0)
    if n_raw == 0:
        return np.zeros_like(fp), stat
    iy, ix, jy, jx = _near_boundary(fp, fp, void, ox, oy)
    stat["boundary_cells"] = int(iy.size)
    if iy.size == 0:
        stat["comps_no_boundary"] = n_raw
        return np.zeros_like(fp), stat
    sy, sx = oy[iy, ix], ox[iy, ix]
    run = st * np.hypot(sx, sy)                       # metres per ray step
    nmax = np.floor(np.where(run > 0, STEP_RUN_M / np.maximum(run, 1e-9), 0) - 1).astype(int)
    zw = hm_on[jy, jx]                                # walkable-side height
    ny, nx = fp.shape
    best = np.full(iy.shape, -np.inf)
    for t in range(int(max(nmax.max(), 0)) + 1):
        ry, rx = iy - sy * t, ix - sx * t
        ok = (t <= nmax) & (ry >= 0) & (ry < ny) & (rx >= 0) & (rx < nx)
        z = hm_on[np.clip(ry, 0, ny - 1), np.clip(rx, 0, nx - 1)]
        best = np.maximum(best, np.where(ok & np.isfinite(z), zw - z, -np.inf))
    stat["boundary_pass"] = int((best >= hz).sum())
    seen = np.unique(comp[iy, ix])
    stat["comps_no_boundary"] = int(n_raw - seen[seen > 0].size)
    keep = np.unique(comp[iy, ix][best >= hz])
    keep = keep[keep > 0]
    stat["comps_kept"] = int(keep.size)
    if keep.size == 0:
        return np.zeros_like(fp), stat
    return np.isin(comp, keep), stat


def edge_points(fp, void, hm, XX, YY, eye, cell, approach_z, ox, oy):
    """Near-boundary (drop-lip) points: footprint cells whose neighbour toward
    the camera is walkable ground.  The emitted point is the LIP -- XY midway
    between the two cells, Z of the walkable side -- because that is the part of
    the edge a camera can actually see (a vertical drop's floor never is).

    Two filters keep this meaningful on real scenes, where the footprint can be
    the entire far half of the map: the lip must lie INSIDE the polar grid (that
    is the edge the label is about), and its walkable side must not sit above
    standing ground + LIP_WALL_TOP_M (that is a wall top, not a drop lip).
    """
    iy, ix, jy, jx = _near_boundary(fp & (cell >= 0), fp, void, ox, oy)
    if iy.size == 0:
        return np.zeros((0, 3))
    m = hm[jy, jx] <= approach_z + LIP_WALL_TOP_M
    iy, ix, jy, jx = iy[m], ix[m], jy[m], jx[m]
    if iy.size == 0:
        return np.zeros((0, 3))
    if iy.size > LIP_MAX_PTS:
        sel = np.linspace(0, iy.size - 1, LIP_MAX_PTS).astype(int)
        iy, ix, jy, jx = iy[sel], ix[sel], jy[sel], jx[sel]
    return np.stack([0.5 * (XX[iy, ix] + XX[jy, jx]),
                     0.5 * (YY[iy, ix] + YY[jy, jx]), hm[jy, jx]], axis=1)


# --------------------------------------------------------------------------- #
# tier
# --------------------------------------------------------------------------- #
def tier_of(int_px, edge_vis, edge_ratio, ti, te, any_pos):
    if not any_pos:
        return "none_in_fov"          # hazard outside the grid -- NOT hidden
    if int_px == 0 and edge_vis == 0:
        return "H"
    if int_px >= ti:
        return "V"
    if edge_ratio is not None and edge_ratio >= te:
        return "E"
    return "H_weak"


# --------------------------------------------------------------------------- #
# per scene-arm
# --------------------------------------------------------------------------- #
def scene_dirs(round_dir):
    out = {}
    for split in sorted(os.listdir(round_dir)):
        sp = os.path.join(round_dir, split)
        if not os.path.isdir(sp):
            continue
        for sc in sorted(os.listdir(sp)):
            d = os.path.join(sp, sc)
            if os.path.isfile(os.path.join(d, "variation.json")):
                out[sc] = d                      # keyed by sceneID, split ignored
    return out


def label_scene(arm, scene, sdir, off_dir, grid):
    var = json.load(open(os.path.join(sdir, "variation.json")))
    hm, geo, hm_src = load_heightmap(sdir)
    same = os.path.abspath(off_dir) == os.path.abspath(sdir)
    if same:
        hm_off, hm_src_off = hm, hm_src
    else:
        hmo, geo_o, hm_src_off = load_heightmap(off_dir)
        hm_off = align_to(hmo, geo_o, geo, hm.shape)
    x0, y0, st = geo
    ny, nx = hm.shape
    XX, YY = np.meshgrid(x0 + np.arange(nx) * st, y0 + np.arange(ny) * st)
    void, void_off = ~np.isfinite(hm), ~np.isfinite(hm_off)
    void_any = void | void_off
    hz = float(grid["hazard_depth_m"])
    ncell = n_cells(grid)

    # ---- footprint v2: twin heightmap difference (D10) ----------------------
    diff = np.where(void_any, np.nan, hm_off - hm)
    fp_raw = (~void_any) & (diff >= hz)
    cells_raw = int(fp_raw.sum())
    comp_raw, n_comp_raw = connected_components(fp_raw)
    max_diff = float(np.nanmax(diff)) if np.isfinite(diff).any() else float("nan")
    warn = []
    if not same and hm_off.shape != hm.shape:
        warn.append(f"{arm}/{scene}: off-arm heightmap resampled "
                    f"{hm_off.shape} onto {hm.shape}")

    cuts = var["cuts"]
    if isinstance(cuts, dict):
        cuts = list(cuts.values())
    frames = {}
    kept_cells, kept_comps, no_bnd, excl_gt = [], [], [], []
    for c in cuts:
        cam, fn = c["cam"], c["file"]
        eye = np.asarray(cam["eye"], dtype=np.float64)
        az_z = float(cam["ground_z"])                  # reference only (v2 uses z_off)
        ox, oy = _outward(XX, YY, eye)
        fp, gstat = step_gate(fp_raw, comp_raw, n_comp_raw, void_any, hm, ox, oy, st, hz)
        kept_comps.append(gstat["comps_kept"]); kept_cells.append(int(fp.sum()))
        no_bnd.append(gstat["comps_no_boundary"])
        cell, _ = polar_cells(XX, YY, eye, cam["yaw"], grid)

        fc = cell[fp]
        cnt = np.bincount(fc[fc >= 0], minlength=ncell)
        dsum = np.bincount(fc[fc >= 0], weights=diff[fp][fc >= 0], minlength=ncell)
        mean_drop = np.where(cnt > 0, dsum / np.maximum(cnt, 1), 0.0)
        gt = (cnt > 0).astype(int)

        # ---- D14: the SAME wedge test on the RAW (pre-gate) footprint --------
        # Training GT above is unchanged; this second pass only records what the
        # step gate removed, so a morning reversal is a field swap.  fp is a
        # subset of fp_raw by construction, hence gt <= gt_pre cell-wise.
        fcr = cell[fp_raw]
        cnt_pre = np.bincount(fcr[fcr >= 0], minlength=ncell)
        gt_pre = (cnt_pre > 0).astype(int)
        excl_cells = [i for i in range(ncell) if gt_pre[i] and not gt[i]]
        excl_gt.append(len(excl_cells))

        vs = dict(void_total=int(void.sum()),
                  void_frac=round(float(void.mean()), 6),
                  void_in_grid=int((void & (cell >= 0)).sum()),
                  void_adj_walkable=int(_adj4(void_any, np.isfinite(hm) & ~fp).sum()),
                  void_off_total=int(void_off.sum()),
                  void_off_frac=round(float(void_off.mean()), 6),
                  void_off_in_grid=int((void_off & (cell >= 0)).sum()),
                  void_either_total=int(void_any.sum()),
                  void_either_in_grid=int((void_any & (cell >= 0)).sum()))

        dep_p = os.path.join(sdir, c.get("depth") or os.path.splitext(fn)[0] + ".depth.npy")
        rv = dict(int_px=None, int_px_fallback=0, edge_ratio=None, edge_projected=0,
                  edge_visible=0, cell_int_px=[0] * ncell)
        if os.path.isfile(dep_p):
            dep = np.load(dep_p).astype(np.float64)
            if dep.shape != (H_IMG, W_IMG):
                warn.append(f"{arm}/{scene}/{fn}: depth shape {dep.shape}")
            P, good = unproject(dep, eye, cam, DS)
            # sky pixels carry +inf depth -> neutralise before the integer cast
            gx = np.rint((np.where(good, P[..., 0], x0) - x0) / st).astype(np.int64)
            gy = np.rint((np.where(good, P[..., 1], y0) - y0) / st).astype(np.int64)
            inb = good & (gx >= 0) & (gx < nx) & (gy >= 0) & (gy < ny)
            gxc, gyc = np.clip(gx, 0, nx - 1), np.clip(gy, 0, ny - 1)
            # interior = inside the footprint AND below the counterfactual
            # walkable surface z_off at that cell (v2).  Where z_off is void the
            # cut's own approach_z carries the margin instead -- counted apart.
            zo = hm_off[gyc, gxc]
            on_fp = inb & fp[gyc, gxc]
            hit_fb = on_fp & ~np.isfinite(zo) & (P[..., 2] <= az_z - INTERIOR_MARGIN_M)
            hit = (on_fp & np.isfinite(zo) & (P[..., 2] <= zo - INTERIOR_MARGIN_M)) | hit_fb
            hc = cell[gyc, gxc][hit]
            rv["int_px"] = int(hit.sum())
            rv["int_px_fallback"] = int(hit_fb.sum())
            rv["cell_int_px"] = np.bincount(hc[hc >= 0], minlength=ncell).astype(int).tolist()

            E = edge_points(fp, void_any, hm, XX, YY, eye, cell, az_z, ox, oy)
            if E.shape[0]:
                px, py, zc, ok = project(E, eye, cam)
                rv["edge_projected"] = int(ok.sum())
                if ok.any():
                    qy, qx, qz = py[ok].astype(int), px[ok].astype(int), zc[ok]
                    # 3x3 window: the lip is a 1-px-thin feature, so tolerate the
                    # sub-pixel round-off rather than call it occluded.
                    err = np.full(qz.shape, np.inf)
                    for oy_ in (-1, 0, 1):
                        for ox_ in (-1, 0, 1):
                            s = dep[np.clip(qy + oy_, 0, H_IMG - 1),
                                    np.clip(qx + ox_, 0, W_IMG - 1)]
                            e = np.where(np.isfinite(s) & (s > 0), np.abs(s - qz), np.inf)
                            err = np.minimum(err, e)
                    rv["edge_visible"] = int((err <= RIM_TOL_M).sum())
            if rv["edge_projected"] >= LIP_MIN_PROJ:
                rv["edge_ratio"] = round(rv["edge_visible"] / rv["edge_projected"], 4)

        any_pos = bool(gt.any())
        if arm == "off":
            t_strict, tmat = "off", {f"i{a}_e{b}": "off" for a in TAU_INT for b in TAU_EDGE}
        elif rv["int_px"] is None:
            t_strict, tmat = "no_depth", {f"i{a}_e{b}": "no_depth" for a in TAU_INT for b in TAU_EDGE}
        else:
            t_strict = tier_of(rv["int_px"], rv["edge_visible"], rv["edge_ratio"],
                               TAU_INT_DEF, TAU_EDGE_DEF, any_pos)
            tmat = {f"i{a}_e{b}": tier_of(rv["int_px"], rv["edge_visible"],
                                          rv["edge_ratio"], a, b, any_pos)
                    for a in TAU_INT for b in TAU_EDGE}

        frames[f"{arm}/{scene}/{fn}"] = dict(
            polar_gt=gt.tolist(), cell_counts=cnt.astype(int).tolist(),
            polar_gt_pregate=gt_pre.tolist(),
            gate_excluded=dict(cells=excl_cells, n=len(excl_cells)),
            cell_mean_drop=[round(float(v), 4) for v in mean_drop],
            raw_vis=rv, tier_strict=t_strict, tier_matrix=tmat,
            approach_z=round(az_z, 4), void_stats=vs,
            footprint=dict(version=FOOTPRINT_VERSION, cells_raw=cells_raw,
                           cells_kept=kept_cells[-1],
                           hm_cells_excluded=cells_raw - kept_cells[-1],
                           max_diff=round(max_diff, 4) if np.isfinite(max_diff) else None,
                           **gstat))
    summary = dict(scene=scene, arm=arm,
                   # which heightmap instrument this row was measured with
                   hm_source=hm_src, hm_source_off=hm_src_off,
                   void_total=int(void.sum()), void_frac=round(float(void.mean()), 6),
                   void_off_total=int(void_off.sum()),
                   void_off_frac=round(float(void_off.mean()), 6),
                   footprint_version=FOOTPRINT_VERSION,
                   cells_raw=cells_raw,
                   cells_kept_max=max(kept_cells) if kept_cells else 0,
                   cells_kept_min=min(kept_cells) if kept_cells else 0,
                   # D14 scene-level exclusion ledger.  "hm cells" = heightmap
                   # cells; raw is camera-independent, kept/excluded vary per cut
                   # because the step gate reads the camera-facing near boundary.
                   hm_cells_raw=cells_raw,
                   hm_cells_excluded_min=cells_raw - (max(kept_cells) if kept_cells else 0),
                   hm_cells_excluded_max=cells_raw - (min(kept_cells) if kept_cells else 0),
                   n_frames_gate_excluded=sum(1 for n in excl_gt if n > 0),
                   gt_cells_excluded_sum=int(sum(excl_gt)),
                   comps_raw=n_comp_raw,
                   comps_kept_max=max(kept_comps) if kept_comps else 0,
                   comps_kept_min=min(kept_comps) if kept_comps else 0,
                   comps_no_boundary_max=max(no_bnd) if no_bnd else 0,
                   max_diff=round(max_diff, 4) if np.isfinite(max_diff) else None,
                   n_cuts=len(cuts))
    return frames, summary, warn


def _worker(t):
    arm, scene, sdir, off_dir, gpath = t
    try:
        return label_scene(arm, scene, sdir, off_dir, json.load(open(gpath)))
    except Exception as e:                                   # keep the run alive
        return {}, dict(scene=scene, arm=arm, error=f"{type(e).__name__}: {e}"), \
            [f"{arm}/{scene}: FAILED {type(e).__name__}: {e}"]


def check_twins(on, off):
    """Twin pairing: identical filename across arms must be the same pose."""
    bad = []
    for sc in sorted(set(on) & set(off)):
        cs = {}
        for arm, d in (("on", on[sc]), ("off", off[sc])):
            v = json.load(open(os.path.join(d, "variation.json")))
            cu = v["cuts"]
            cs[arm] = {c["file"]: c["cam"] for c in (cu.values() if isinstance(cu, dict) else cu)}
        for fn in sorted(set(cs["on"]) & set(cs["off"])):
            a, b = cs["on"][fn], cs["off"][fn]
            if any(abs(float(a[k]) - float(b[k])) > 1e-6
                   for k in ("yaw", "pitch", "roll", "hfov", "d", "h_rel")) or \
               any(abs(float(a["eye"][i]) - float(b["eye"][i])) > 1e-6 for i in range(3)):
                bad.append(f"{sc}/{fn}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--on-round", required=True)
    ap.add_argument("--off-round", required=True)
    ap.add_argument("--grid", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "gridspec_v0.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--scenes", default="")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args()

    grid = json.load(open(a.grid))
    keep = set(x for x in a.scenes.split(",") if x)
    on, off = scene_dirs(a.on_round), scene_dirs(a.off_round)
    if keep:
        on = {k: v for k, v in on.items() if k in keep}
        off = {k: v for k, v in off.items() if k in keep}
    bad = check_twins(on, off)
    if bad:
        print(f"[labeler] WARN twin-pose mismatch on {len(bad)} cuts: {bad[:5]}", file=sys.stderr)

    # footprint v2 needs BOTH arms of a scene; an on-arm scene whose off twin has
    # not rendered yet is skipped loudly rather than labelled against a guess.
    orphan = sorted(set(on) - set(off))
    tasks = [("on", s, d, off[s], a.grid) for s, d in sorted(on.items()) if s in off] + \
            [("off", s, d, d, a.grid) for s, d in sorted(off.items())]
    if a.workers > 1:
        import multiprocessing as mp
        with mp.Pool(a.workers) as p:
            res = p.map(_worker, tasks, chunksize=1)
    else:
        res = [_worker(t) for t in tasks]

    warns = [f"twin-mismatch {b}" for b in bad] + \
            [f"{s}: on-arm scene has no off-arm twin -> SKIPPED (footprint v2 "
             f"needs z_off)" for s in orphan]
    frames, sv = {}, []
    for fr, s, w in res:
        frames.update(fr); sv.append(s); warns += w
    if orphan:
        print(f"[labeler] WARN {len(orphan)} on-arm scenes skipped (no off twin): "
              f"{orphan[:5]}", file=sys.stderr)
    gt_src = gt_source_of(grid)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(dict(grid=grid, cam_convention_source=CAM_SRC,
                   meta=dict(gt_source=gt_src, tier_source=TIER_SOURCE,
                             footprint=FOOTPRINT_VERSION,
                             n_cells=n_cells(grid),
                             interior_margin_m=INTERIOR_MARGIN_M,
                             rim_tol_m=RIM_TOL_M, lip_max_pts=LIP_MAX_PTS,
                             step_run_m=STEP_RUN_M, gate_policy=GATE_POLICY),
                   gt_source=gt_src, footprint=FOOTPRINT_VERSION,
                   tau_strict=dict(tau_int=TAU_INT_DEF, tau_edge=TAU_EDGE_DEF),
                   scene_void=sv, scene_footprint=sv, warnings=warns, frames=frames),
              open(a.out, "w"), indent=1)
    print(f"[labeler] {len(frames)} frames -> {a.out} ({len(warns)} warnings)")


if __name__ == "__main__":
    main()
