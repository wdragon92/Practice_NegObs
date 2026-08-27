# -*- coding: utf-8 -*-
"""simple_edge.py -- the SIMPLE labeler.

One job, stated the way the owner stated it:

    "From the surface I am standing on, find where the negative-obstacle danger
     starts, and draw it as ONE clean solid line. The visible drop surface is
     ONE clean unified segmentation mask."

So this module produces exactly two things per frame and nothing else:

    1. danger edge   -- a short list of ordered polylines (usually one)
    2. drop mask     -- one binary mask of the visible surface below the drop

It is deliberately self-contained. It REUSES the verified loaders and camera
model (e1_data, e1_camera) and the constant table (e1_const), and it imports
NOTHING from the complex instance machinery (labeler.py, e1_geometry,
e1_visibility, e1_schema). Every number it uses is registered in e1_const.

Definitions (the whole spec)
----------------------------
ground_z
    variation.json -> cuts[i].cam.ground_z : the height of the surface the
    camera stands on.

my_surface
    image pixels whose back-projected 3D point satisfies
    |z - ground_z| <= FLAT_TOL_M (= WALK_FLAT_TOL_M), 8-connected in IMAGE
    space to the bottom-centre of the frame. That is "the surface I am standing
    on, as actually visible".

danger edge
    the boundary pixels of my_surface where, looking OUTWARD (away from
    my_surface, along the ground) within a horizontal run of R_RUN_M, the true
    ground -- the heightmap, not the depth image -- lies at least DROP_MIN_M
    below ground_z. A wall, a bench, a planter or a lawn at the same level is
    at or above ground_z there, so it is NOT an edge. Kept pixels are traced
    into ordered polylines (one per 8-connected run) and simplified with
    Ramer-Douglas-Peucker at RDP_TOL_PX, so a straight plaza lip becomes ONE
    straight segment.

visible drop surface
    visible depth pixels whose 3D point is <= ground_z - DROP_MIN_M, keeping
    only the image-space components that touch the danger edge dilated by
    EDGE_BRIDGE_PX (the dilation bridges the riser, which is neither surface
    nor drop). Empty on an E frame; that is the correct answer, not a failure.

Outward direction
-----------------
For a boundary pixel we need "beyond it, along the ground". Every pixel ray is
intersected with the plane z = ground_z (exact for flat ground, and the camera
model that does it is the numerically verified one in e1_camera). The outward
direction is the mean, over the 8-neighbours that are OUTSIDE my_surface, of
the unit world-XY step from this pixel's ground point to the neighbour's. A
boundary pixel with no usable outward direction (frame border, or every
outside neighbour above the horizon) is reported and dropped -- never guessed.

CLI
---
    python3 simple_edge.py --scan-consts
    python3 simple_edge.py --frame ROUND:SCENE:L0:0000
    python3 simple_edge.py --batch
    python3 simple_edge.py --batch --contact-sheet
"""

import argparse
import ast
import glob
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
OVERLAY_DIR = os.path.join(CYCLE, "overlays", "_simple")
ANNOT_DIR = os.path.join(CYCLE, "annotations", "_simple")

# The six frames the owner asked for. Rounds by NAME (variation_kit.round_dir);
# dataset paths are never spelled here.
FRAMES = [
    ("260819_main_on", "scene01", "L0", "0000"),
    ("260819_main_on", "scene03", "L0", "0000"),
    ("260819_main_on", "scene09", "L0", "0000"),
    ("260819_main_on", "scene18", "L0", "0000"),
    ("260824_v3w3_extbase_A", "sceneH1", "L0", "0000"),
    ("260819_main_on", "sceneD2", "L0", "0000"),
]

# 8-neighbourhood, fixed order -> the traversals below are deterministic.
NB8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


# --------------------------------------------------------------------------- #
# small array helpers
# --------------------------------------------------------------------------- #
def _shift(a, dy, dx, fill):
    """a[y+dy, x+dx] with out-of-image filled by `fill` (no wraparound)."""
    out = np.full_like(a, fill)
    ys_src = slice(max(dy, 0), a.shape[0] + min(dy, 0))
    xs_src = slice(max(dx, 0), a.shape[1] + min(dx, 0))
    ys_dst = slice(max(-dy, 0), a.shape[0] + min(-dy, 0))
    xs_dst = slice(max(-dx, 0), a.shape[1] + min(-dx, 0))
    out[ys_dst, xs_dst] = a[ys_src, xs_src]
    return out


def _ground_plane_xy(cam, ground_z):
    """Per-pixel intersection of the pixel ray with the plane z = ground_z.

    Returns (GX, GY), NaN wherever the ray does not descend to the plane in
    front of the camera (i.e. at or above the horizon).
    """
    un = (np.arange(cam.W) + 0.5 - cam.cx) / cam.fx
    vn = (np.arange(cam.H) + 0.5 - cam.cy) / cam.fy
    UN, VN = np.meshgrid(un, vn)
    dirs = UN[..., None] * cam.r + VN[..., None] * (-cam.u) + cam.f
    dz = dirs[..., 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (ground_z - cam.eye[2]) / dz
    ok = np.isfinite(t) & (t > 0)
    gx = np.where(ok, cam.eye[0] + t * dirs[..., 0], np.nan)
    gy = np.where(ok, cam.eye[1] + t * dirs[..., 1], np.nan)
    return gx, gy


def _rdp(pts, tol):
    """Ramer-Douglas-Peucker on an ordered (N,2) float array."""
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
    """Order one 8-connected pixel component into a single chain.

    Double BFS: farthest pixel A from an arbitrary start, then the shortest
    path from A to the pixel farthest from A. Side spurs are dropped, which is
    exactly what "one clean line" asks for. Ties always break on the smallest
    (y, x), so two runs give the identical chain.
    """
    idx = {(int(y), int(x)): i for i, (y, x) in enumerate(coords)}

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
    return [(x, y) for (y, x) in chain]          # (x, y) pixel order


def _chain_len_px(chain):
    if len(chain) < 2:
        return 0.0
    p = np.asarray(chain, dtype=np.float64)
    return float(np.hypot(*(p[1:] - p[:-1]).T).sum())


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


def pick_my_surface(flat):
    """8-connected component of `flat` that the camera is standing on.

    Rule, in order; the branch taken is reported per frame:
      1. the LARGEST component reaching the bottom strip of the frame
      2. else the largest component whose lowest pixel is in the bottom half
      3. else the largest component in the frame

    Why "largest reaching the bottom strip" and not "whatever sits at
    bottom-centre": on sceneD2 the camera stands at the lip of a trench that is
    already open at the bottom of the frame, so the bottom-CENTRE patch is 90%
    trench and its only flat pixels are a 5,045 px blob lying INSIDE the
    trench at ground height. Bottom-centre would elect a blob nobody can stand
    on, over the 960,320 px yard that the camera is really on and that carries
    the trench rim. The yard reaches the bottom strip at x 0..177 and
    x 1495..1919 -- off centre, but under the camera's feet. The bottom-centre
    patch is still measured and reported (`seed_centre_area_px`) so the two
    readings can be compared per frame.
    """
    H, W = flat.shape
    lab, n = ndimage.label(flat, structure=np.ones((3, 3), dtype=int))
    info = {"seed_centre_area_px": 0, "n_flat_components": int(n)}
    if n == 0:
        return np.zeros_like(flat), "none", info
    strip = max(int(round(H * C.SIMPLE_SEED_STRIP_FRAC)), 1)
    half = max(int(round(W * C.SIMPLE_SEED_HALF_W_FRAC)), 1)
    cx = W // 2
    areas = np.bincount(lab.ravel(), minlength=n + 1)
    areas[0] = 0

    patch = lab[H - strip:, max(cx - half, 0):min(cx + half, W)]
    hits = np.bincount(patch.ravel(), minlength=n + 1)
    hits[0] = 0
    if hits.max() > 0:
        info["seed_centre_area_px"] = int(areas[int(np.argmax(
            np.where(hits > 0, areas, 0)))])

    band = np.bincount(lab[H - strip:, :].ravel(), minlength=n + 1)
    band[0] = 0
    if band.max() > 0:
        k = int(np.argmax(np.where(band > 0, areas, 0)))
        return lab == k, "bottom_strip", info

    rows = np.broadcast_to(np.arange(H)[:, None], (H, W))
    ymax = np.asarray(ndimage.maximum(rows, lab, index=np.arange(1, n + 1)))
    low = np.zeros(n + 1, dtype=bool)
    low[1:] = ymax >= H * 0.5
    if low.any():
        k = int(np.argmax(np.where(low, areas, 0)))
        return lab == k, "lowest_component", info
    k = int(np.argmax(areas))
    return lab == k, "largest_component", info


def label_frame(round_name, scene_id, tier, idx, edge_bridge_px=None):
    """Everything for one frame. Returns (record, drop mask, edge mask, rgb path).

    `edge_bridge_px` overrides EDGE_BRIDGE_PX for the --bridge-sweep
    measurement only; every shipped label uses the ledger value.
    """
    bridge = C.EDGE_BRIDGE_PX if edge_bridge_px is None else int(edge_bridge_px)
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

    # -- 1. my_surface --------------------------------------------------- #
    pts, valid = cam.unproject(depth, stride=1)
    valid = valid & (depth <= C.DEPTH_MAX_M)
    pz = pts[..., 2]
    flat = valid & (np.abs(pz - ground_z) <= C.WALK_FLAT_TOL_M)
    surf, seed_branch, seed_info = pick_my_surface(flat)
    surf_area = int(surf.sum())

    # -- 2. boundary + outward direction --------------------------------- #
    gx, gy = _ground_plane_xy(cam, ground_z)
    outside = ~surf
    acc_x = np.zeros(surf.shape, dtype=np.float64)
    acc_y = np.zeros(surf.shape, dtype=np.float64)
    acc_n = np.zeros(surf.shape, dtype=np.int32)
    is_bnd = np.zeros(surf.shape, dtype=bool)
    for dy, dx in NB8:
        nb_out = _shift(outside, dy, dx, True)
        is_bnd |= nb_out
        gx2 = _shift(gx, dy, dx, np.nan)
        gy2 = _shift(gy, dy, dx, np.nan)
        vx = gx2 - gx
        vy = gy2 - gy
        nrm = np.hypot(vx, vy)
        ok = nb_out & np.isfinite(nrm) & (nrm > 0)
        acc_x += np.where(ok, vx / np.where(nrm > 0, nrm, 1.0), 0.0)
        acc_y += np.where(ok, vy / np.where(nrm > 0, nrm, 1.0), 0.0)
        acc_n += ok
    is_bnd &= surf
    dir_ok = is_bnd & (acc_n > 0) & (np.hypot(acc_x, acc_y) > 0)
    n_bnd = int(is_bnd.sum())
    n_nodir = int((is_bnd & ~dir_ok).sum())

    # -- 3. march outward over the heightmap ----------------------------- #
    by, bx = np.nonzero(dir_ok)
    edge = np.zeros(surf.shape, dtype=bool)
    beyond_min_z = np.array([], dtype=np.float64)
    if by.size:
        dvx, dvy = acc_x[by, bx], acc_y[by, bx]
        dn = np.hypot(dvx, dvy)
        dvx, dvy = dvx / dn, dvy / dn
        px0, py0 = pts[by, bx, 0], pts[by, bx, 1]
        nstep = max(int(round(C.R_RUN_M / hm.step)), 1)
        ks = (np.arange(nstep) + 1) * hm.step
        sx = px0[:, None] + dvx[:, None] * ks[None, :]
        sy = py0[:, None] + dvy[:, None] * ks[None, :]
        zs = hm.sample(sx, sy)
        fin = np.isfinite(zs)
        beyond_min_z = np.where(fin.any(axis=1),
                                np.where(fin, zs, np.inf).min(axis=1), np.nan)
        keep = np.isfinite(beyond_min_z) & (beyond_min_z <= drop_line_z)
        edge[by[keep], bx[keep]] = True
    n_edge_px = int(edge.sum())

    # -- 4. trace + simplify --------------------------------------------- #
    lab_e, n_e = ndimage.label(edge, structure=np.ones((3, 3), dtype=int))
    polys, chains, dropped_short = [], [], 0
    for k in range(1, n_e + 1):
        coords = np.argwhere(lab_e == k)
        chain = _trace_component(coords)
        L = _chain_len_px(chain)
        if L < C.MIN_EDGE_PX:
            dropped_short += 1
            continue
        simp = _rdp(np.asarray(chain, dtype=np.float64), C.RDP_TOL_PX)
        polys.append([[int(round(p[0])), int(round(p[1]))] for p in simp])
        chains.append(chain)
    order = sorted(range(len(polys)),
                   key=lambda i: (-_chain_len_px(chains[i]), polys[i][0]))
    polys = [polys[i] for i in order]
    chains = [chains[i] for i in order]
    kept_mask = np.zeros(surf.shape, dtype=bool)
    for ch in chains:
        for (x, y) in ch:
            kept_mask[y, x] = True
    edge_len_px = float(sum(_chain_len_px([tuple(p) for p in pl]) for pl in polys))

    # -- 5. visible drop surface ----------------------------------------- #
    below = valid & (pz <= drop_line_z)
    drop = np.zeros(surf.shape, dtype=bool)
    if kept_mask.any() and below.any():
        near = ndimage.binary_dilation(kept_mask, np.ones((3, 3), dtype=bool),
                                       iterations=bridge)
        lab_d, n_d = ndimage.label(below, structure=np.ones((3, 3), dtype=int))
        touched = np.unique(lab_d[near & below])
        touched = touched[touched > 0]
        if touched.size:
            drop = np.isin(lab_d, touched)
    mask_area = int(drop.sum())
    # Why is this frame E and not V? The gap, in px, from the kept edge to the
    # nearest below-the-drop pixel. EDGE_BRIDGE_PX has to cover it.
    gap_px = None
    if kept_mask.any() and below.any():
        gap_px = float(ndimage.distance_transform_edt(~below)[kept_mask].min())

    # -- 6. numbers ------------------------------------------------------- #
    min_dist = None
    if kept_mask.any():
        ky, kx = np.nonzero(kept_mask)
        r = np.hypot(pts[ky, kx, 0] - cam.eye[0], pts[ky, kx, 1] - cam.eye[1])
        min_dist = float(np.min(r))
    if mask_area > 0:
        tier_hint = "V"
    elif polys:
        tier_hint = "E"
    else:
        tier_hint = "NEG"

    dp = C.JSON_DECIMALS
    rec = {
        "frame": "%s__%s__%s" % (round_name, scene_id, fname[:-len(".png")]),
        "edges": polys,
        "edge_len_px": round(edge_len_px, dp),
        "mask_area_px": mask_area,
        "min_edge_dist_m": None if min_dist is None else round(min_dist, dp),
        "tier_hint": tier_hint,
        "meta": {
            "round": round_name, "scene": scene_id, "file": fname,
            "split": os.path.basename(os.path.dirname(sdir)),
            "rgb_path": D.rel_to_repo(assets["rgb_path"]),
            "depth_path": D.rel_to_repo(assets["depth_path"]),
            "ground_z_m": round(ground_z, dp),
            "drop_line_z_m": round(drop_line_z, dp),
            "hm_step_m": round(hm.step, dp),
            "surface_area_px": surf_area,
            "surface_seed_branch": seed_branch,
            "seed_centre_area_px": seed_info["seed_centre_area_px"],
            "n_flat_components": seed_info["n_flat_components"],
            "boundary_px": n_bnd,
            "boundary_px_no_direction": n_nodir,
            "edge_px_kept": n_edge_px,
            "n_polylines": len(polys),
            "polylines_dropped_short": dropped_short,
            "n_below_px_total": int(below.sum()),
            "edge_to_below_gap_px": (None if gap_px is None
                                     else round(gap_px, C.JSON_DECIMALS)),
            "edge_bridge_px": bridge,
            "const_fingerprint": C.fingerprint(),
        },
    }
    return rec, drop, kept_mask, assets["rgb_path"]


# --------------------------------------------------------------------------- #
# drawing
# --------------------------------------------------------------------------- #
def _font(size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(C.SIMPLE_FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def render_overlay(rgb_path, rec, drop, tile_w=None):
    """RGB + translucent red drop mask + solid orange edge + one caption.
    Nothing else goes on this image.

    `tile_w` re-renders at that width: the mask is blended at full resolution
    and resampled, then the polyline is STROKED AT THE TILE SCALE, so a 3 px
    line is still 3 px on the contact sheet instead of a downscaled ghost.
    """
    from PIL import Image, ImageDraw
    img = Image.open(rgb_path).convert("RGB")
    arr = np.asarray(img).astype(np.float64)

    if drop.any():
        fill = np.asarray(C.SIMPLE_MASK_RGB, dtype=np.float64)
        a = C.SIMPLE_MASK_ALPHA
        arr[drop] = arr[drop] * (1.0 - a) + fill * a
        er = ndimage.binary_erosion(drop, np.ones((3, 3), dtype=bool))
        arr[drop & ~er] = np.asarray(C.SIMPLE_MASK_OUTLINE_RGB, dtype=np.float64)

    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    scale = 1.0
    if tile_w and tile_w != img.width:
        scale = tile_w / float(img.width)
        img = img.resize((tile_w, int(round(img.height * scale))), Image.LANCZOS)

    dr = ImageDraw.Draw(img)
    for poly in rec["edges"]:
        if len(poly) >= 2:
            dr.line([(p[0] * scale, p[1] * scale) for p in poly],
                    fill=tuple(C.SIMPLE_EDGE_RGB), width=C.OVERLAY_LINE_PX,
                    joint="curve")

    dist = rec["min_edge_dist_m"]
    cap = "%s   edge %.0f px   mask %d px   min dist %s m   [%s]" % (
        rec["frame"], rec["edge_len_px"], rec["mask_area_px"],
        ("--" if dist is None else "%.2f" % dist), rec["tier_hint"])
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


def contact_sheet(records, out_jpg):
    """2 rows x 3 columns of the six overlays, scene name printed above each."""
    from PIL import Image, ImageDraw
    cols, rows = 3, 2
    tw = C.SHEET_TILE_W_PX
    fnt = _font(C.SHEET_LABEL_PX)
    lab_h = C.SHEET_LABEL_PX * 2
    tiles = [(render_overlay(r["_rgb"], r, r["_drop"], tile_w=tw), r)
             for r in records]
    th = max(t.height for t, _ in tiles)
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab_h)),
                      tuple(C.SHEET_BG_RGB))
    dr = ImageDraw.Draw(sheet)
    for i, (t, rec) in enumerate(tiles):
        cx, cy = i % cols, i // cols
        x0, y0 = cx * tw, cy * (th + lab_h)
        name = "%s / %s   [%s]" % (rec["meta"]["round"], rec["meta"]["scene"],
                                   rec["tier_hint"])
        dr.text((x0 + C.SHEET_LABEL_PX // 3, y0 + C.SHEET_LABEL_PX // 3), name,
                font=fnt, fill=(255, 255, 255))
        sheet.paste(t, (x0, y0 + lab_h))
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


def run_one(round_name, scene_id, tier, idx, quiet=False):
    from PIL import Image
    os.makedirs(OVERLAY_DIR, exist_ok=True)
    os.makedirs(ANNOT_DIR, exist_ok=True)
    rec, drop, kept, rgb_path = label_frame(round_name, scene_id, tier, idx)
    stem = rec["frame"]
    dump_json(rec, os.path.join(ANNOT_DIR, stem + ".simple_edge.json"))
    mp = os.path.join(OVERLAY_DIR, stem + ".dropmask.png")
    Image.fromarray((drop.astype(np.uint8) * 255)).save(mp)
    op = draw_overlay(rgb_path, rec, drop, os.path.join(OVERLAY_DIR, stem + ".overlay.png"))
    rec["_overlay"], rec["_mask"] = op, mp
    rec["_rgb"], rec["_drop"] = rgb_path, drop
    m = rec["meta"]
    if not quiet:
        print("[simple] %-42s ground_z=%+.3f  surf=%7d px (%s)  bnd=%6d "
              "(no-dir %5d)  edge=%5d px -> %d line(s) len %.0f px  "
              "mask=%7d px  min_dist=%s  %s"
              % (stem, m["ground_z_m"], m["surface_area_px"],
                 m["surface_seed_branch"], m["boundary_px"],
                 m["boundary_px_no_direction"], m["edge_px_kept"],
                 m["n_polylines"], rec["edge_len_px"], rec["mask_area_px"],
                 ("--" if rec["min_edge_dist_m"] is None
                  else "%.2f m" % rec["min_edge_dist_m"]), rec["tier_hint"]))
        if rec["tier_hint"] == "E" and m["edge_to_below_gap_px"] is not None:
            print("         E, not V: the nearest below-drop pixel is %.1f px "
                  "from the edge and EDGE_BRIDGE_PX is %d -- the riser gap "
                  "is not bridged" % (m["edge_to_below_gap_px"],
                                      m["edge_bridge_px"]))
    return rec



def bridge_sweep():
    """mask_area_px for every frame at every BRIDGE_SWEEP_PX value.

    EDGE_BRIDGE_PX is a given constant, so it is not tuned here. This only
    measures what it costs: a frame whose riser gap exceeds the dilation
    reports an empty drop mask (tier E) even though the drop floor is plainly
    visible.
    """
    print("[simple] EDGE_BRIDGE_PX sweep -- mask_area_px (running value %d)"
          % C.EDGE_BRIDGE_PX)
    print("   %-46s %8s  %s" % ("frame", "gap px",
                                "  ".join("%8d" % b for b in C.BRIDGE_SWEEP_PX)))
    for spec in FRAMES:
        row, gap = [], None
        for b in C.BRIDGE_SWEEP_PX:
            rec, _, _, _ = label_frame(*spec, edge_bridge_px=b)
            row.append(rec["mask_area_px"])
            gap = rec["meta"]["edge_to_below_gap_px"]
        print("   %-46s %8s  %s"
              % ("%s/%s" % (spec[0], spec[1]),
                 "--" if gap is None else "%.1f" % gap,
                 "  ".join("%8d" % v for v in row)))
    return 0



def diag_sheet():
    """A SECOND contact sheet showing what the drop masks look like once the
    riser gap is actually bridged.

    This is evidence, not a relabel: it writes no json and no overlay, only
    `contact_sheet_EDGE_BRIDGE_<n>px.jpg`, and the shipped labels keep the
    ledger value of EDGE_BRIDGE_PX. `n` is the smallest swept dilation at
    which every frame that HAS a danger edge also has a non-empty drop mask.
    """
    os.makedirs(OVERLAY_DIR, exist_ok=True)
    chosen, best = None, None
    for b in C.BRIDGE_SWEEP_PX:
        recs = []
        for spec in FRAMES:
            rec, drop, _, rgb = label_frame(*spec, edge_bridge_px=b)
            rec["_rgb"], rec["_drop"] = rgb, drop
            recs.append(rec)
        if all(r["mask_area_px"] > 0 for r in recs if r["edges"]):
            chosen, best = b, recs
            break
    if chosen is None:
        print("[simple] no swept EDGE_BRIDGE_PX fills every edged frame")
        return 1
    out = os.path.join(OVERLAY_DIR,
                       "contact_sheet_EDGE_BRIDGE_%dpx.jpg" % chosen)
    contact_sheet(best, out)
    mb = os.path.getsize(out) / float(C.BYTES_PER_MB)
    print("[simple] diagnostic sheet at EDGE_BRIDGE_PX=%d (ledger value %d): "
          "%s  (%.2f MB)" % (chosen, C.EDGE_BRIDGE_PX, out, mb))
    for r in best:
        print("         %-46s mask %8d px  [%s]"
              % (r["meta"]["scene"], r["mask_area_px"], r["tier_hint"]))
    return 0


# --------------------------------------------------------------------------- #
# self-check: the const scan, applied to THIS module
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


# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(description="the simple negative-obstacle labeler")
    ap.add_argument("--frame", help="ROUND:SCENE:TIER:IDX, e.g. 260819_main_on:scene01:L0:0000")
    ap.add_argument("--batch", action="store_true", help="the six review frames")
    ap.add_argument("--contact-sheet", action="store_true")
    ap.add_argument("--scan-consts", action="store_true")
    ap.add_argument("--bridge-sweep", action="store_true")
    ap.add_argument("--diag-sheet", action="store_true")
    a = ap.parse_args(argv)

    if a.scan_consts:
        return scan_consts()
    if a.bridge_sweep:
        return bridge_sweep()
    if a.diag_sheet:
        return diag_sheet()

    recs = []
    if a.frame:
        recs.append(run_one(*a.frame.split(":")))
    if a.batch:
        for spec in FRAMES:
            recs.append(run_one(*spec))
    if a.contact_sheet:
        if not recs:
            raise SystemExit("[simple] --contact-sheet needs --batch")
        out = contact_sheet(recs, os.path.join(OVERLAY_DIR, "contact_sheet.jpg"))
        mb = os.path.getsize(out) / float(C.BYTES_PER_MB)
        print("[simple] contact sheet %s  (%.2f MB, budget %.1f MB, %s)"
              % (out, mb, C.SHEET_MAX_MB,
                 "OK" if mb <= C.SHEET_MAX_MB else "OVER BUDGET"))
    if not (a.frame or a.batch or a.bridge_sweep or a.diag_sheet):
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
