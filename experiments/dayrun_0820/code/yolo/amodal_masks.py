#!/usr/bin/env python3
"""Amodal hazard masks (DAYRUN_BRIEF_0820 Phase 5.1 / 5.2).

WHAT
    For every hazard-ON frame, project the POST-GATE heightmap footprint through
    that frame's camera **ignoring occlusion**, and rasterise it to a binary mask.
    "Amodal" = the mask is the image region the hazard occupies whether or not
    anything stands in front of it, so an H-tier frame (zero visible hazard
    pixels, by definition) still gets a non-empty mask.  Off-arm frames carry no
    hazard: no PNG is written and their box list is empty (YOLO background).

GEOMETRY -- all of it imported from the labeler, none of it re-derived here
    footprint : LB.load_heightmap + LB.align_to + (z_off - z_on >= hazard_depth)
                + LB.connected_components + LB.step_gate   == labeler.label_scene
                Cross-checked per frame against the labels json's
                `footprint.cells_kept`, which the labeler wrote for that frame.
    camera    : LB.project (CAM_CONVENTION.md sec.3/sec.6)
    grid      : gridspec_v1.json (only used for --clip-grid and for provenance)

WHAT IS PROJECTED -- the hazard PRISM, not a surface
    A footprint cell (x, y) says "the walkable surface used to be at z_off and is
    now at z_on, a fall of >= 0.30 m".  The hazard therefore occupies the vertical
    prism [z_on, z_off] over the footprint region, and its image silhouette is
    what a detector should box.  The prism's surface is sampled as

        top    : (x, y, z_off) for every footprint cell   -- the opening at
                 walkable level (hence the class name `hazard_opening`)
        bottom : (x, y, z_on)  for every footprint cell   -- the drop floor,
                 i.e. exactly the surface the renderer drew and the labeler
                 counted as `int_px`
        sides  : (x, y, z) for BOUNDARY cells only, z stepping by the heightmap
                 step (0.05 m) from z_on to z_off -- the walls.  Interior columns
                 are inside the prism and cannot contribute to a silhouette, so
                 sampling the perimeter is exact and keeps the point count at
                 O(area + perimeter x depth).

RASTERISATION -- depth-adaptive point splat, numpy only
    Each sample is splatted as a filled square whose radius is the size that ONE
    heightmap cell subtends at that sample's depth:

        r_px = ceil(f_px_out * grid_step / z_cam)      (clipped to [1, 64])

    so the splats of neighbouring cells always touch and the mask has no interior
    holes -- this is a cheap stand-in for rasterising each 5 cm lattice quad.
    Radii are bucketed to the next power of two (>= the exact radius, < 2x it, so
    over-coverage is at most one heightmap cell ~ 0.05-0.10 m in world terms) and
    each bucket is scattered then dilated by an exact-radius separable binary
    dilation (O(log r) zero-filled OR-shifts, restricted to that bucket's
    bounding box).  No morphological close is needed: the splat radius already
    closes the lattice, and a close would also bridge genuinely separate
    components.

OUTPUT
    annotations/amodal/<arm>__<scene>__<file>.png    uint8, 0 / 255, 960x540
    annotations/amodal/bboxes.json                   per-frame normalised boxes
                                                     (one per kept component) --
                                                     the contract read by
                                                     make_yolo_dataset.py

NOT CLIPPED TO THE POLAR GRID by default: the brief says "project the post-gate
footprint", and the footprint of a cliff-type scene legitimately runs past the
grid's 12 m outer radius.  `--clip-grid` restricts it to the labelled wedge; the
choice is recorded in bboxes.json meta.

CPU only.  Run with PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="".
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (CLASS_NAME, DAYRUN, LB, cuts_of, load_grid, scene_dir_of,  # noqa: E402
                    split_frame_id, stem_of, twin_round_dir)

R_MAX = 64
"""Splat radius cap in output pixels.  r = f_px_out * 0.05 / z, so 64 px at
960-wide is reached at z ~ 0.62 m -- nearer than any footprint sample the
sampler can produce (standoff >= 1.2 m).  The cap only bounds pathological
frames; it is reported if it ever binds."""

OUT_W, OUT_H = 960, 540


# --------------------------------------------------------------------------- #
# binary morphology (numpy only)
# --------------------------------------------------------------------------- #
def _shift(a, dy, dx):
    """Zero-filled shift (never wraps, unlike np.roll)."""
    out = np.zeros_like(a)
    h, w = a.shape
    ys_src = slice(max(0, -dy), h - max(0, dy))
    ys_dst = slice(max(0, dy), h - max(0, -dy))
    xs_src = slice(max(0, -dx), w - max(0, dx))
    xs_dst = slice(max(0, dx), w - max(0, -dx))
    out[ys_dst, xs_dst] = a[ys_src, xs_src]
    return out


def dilate_square(m, r):
    """Exact binary dilation by the square [-r, r]^2, in O(log r) OR-shifts.

    Invariant: `out` is always the dilation of `m` by a CONTIGUOUS square of
    radius c.  OR-ing it with a +/-d shift extends that to radius c + d provided
    d <= 2c + 1 (otherwise a gap of unset rows would open), so d doubles each
    round and the loop lands exactly on r.
    """
    r = int(r)
    if r <= 0:
        return m
    out, c = m, 0
    while c < r:
        d = min(2 * c + 1, r - c)
        out = out | _shift(out, 0, d) | _shift(out, 0, -d)
        out = out | _shift(out, d, 0) | _shift(out, -d, 0)
        c += d
    return out


def boundary4(m):
    """Footprint cells with a 4-neighbour outside the mask (map edge counts)."""
    inner = m.copy()
    inner[1:, :] &= m[:-1, :]
    inner[:-1, :] &= m[1:, :]
    inner[:, 1:] &= m[:, :-1]
    inner[:, :-1] &= m[:, 1:]
    inner[0, :] = inner[-1, :] = False
    inner[:, 0] = inner[:, -1] = False
    return m & ~inner


# --------------------------------------------------------------------------- #
# scene geometry (twin heightmaps) -- mirrors labeler.label_scene's prologue
# --------------------------------------------------------------------------- #
class SceneGeom:
    def __init__(self, on_dir, off_dir):
        hm, geo, self.hm_src = LB.load_heightmap(on_dir)
        if os.path.abspath(off_dir) == os.path.abspath(on_dir):
            hm_off, self.hm_src_off = hm, self.hm_src
        else:
            hmo, geo_o, self.hm_src_off = LB.load_heightmap(off_dir)
            hm_off = LB.align_to(hmo, geo_o, geo, hm.shape)
        self.hm, self.hm_off, self.geo = hm, hm_off, geo
        x0, y0, self.st = geo
        ny, nx = hm.shape
        self.XX, self.YY = np.meshgrid(x0 + np.arange(nx) * self.st,
                                       y0 + np.arange(ny) * self.st)
        self.void_any = ~np.isfinite(hm) | ~np.isfinite(hm_off)
        self.diff = np.where(self.void_any, np.nan, hm_off - hm)

    def raw_footprint(self, hz):
        fp_raw = (~self.void_any) & (self.diff >= hz)
        comp, n = LB.connected_components(fp_raw)
        return fp_raw, comp, n


def prism_points(g, m, max_levels=400):
    """Surface samples of the hazard prism over mask `m`.  See module docstring."""
    st = g.st
    x, y = g.XX[m], g.YY[m]
    z0, z1 = g.hm[m], g.hm_off[m]
    chunks = [np.stack([x, y, z0], 1), np.stack([x, y, z1], 1)]
    b = boundary4(m)
    if b.any():
        xb, yb = g.XX[b], g.YY[b]
        zb0, zb1 = g.hm[b], g.hm_off[b]
        span = float(np.nanmax(zb1 - zb0))
        k = int(min(max_levels, math.ceil(span / st)))
        if k > 1:
            t = np.arange(1, k)[None, :] * st
            Z = zb0[:, None] + t
            v = Z < zb1[:, None]
            if v.any():
                chunks.append(np.stack([np.repeat(xb, k - 1)[v.ravel()],
                                        np.repeat(yb, k - 1)[v.ravel()],
                                        Z.ravel()[v.ravel()]], 1))
    return np.concatenate(chunks, 0)


def rasterize(px, py, zc, fx_out, step_m, shape=(OUT_H, OUT_W), r_max=R_MAX):
    """Depth-adaptive splat of projected samples -> binary mask + splat stats."""
    h, w = shape
    ok = np.isfinite(zc) & (zc > 0.05) & np.isfinite(px) & np.isfinite(py)
    px, py, zc = px[ok], py[ok], zc[ok]
    out = np.zeros((h + 2 * (r_max + 1), w + 2 * (r_max + 1)), bool)
    st = dict(n_samples=int(ok.sum()), n_in_canvas=0, r_max_used=0, r_capped=0)
    if px.size == 0:
        return out[r_max + 1:r_max + 1 + h, r_max + 1:r_max + 1 + w], st
    r = np.ceil(fx_out * step_m / zc)
    st["r_capped"] = int((r > r_max).sum())
    r = np.clip(r, 1, r_max).astype(np.int64)
    rc = np.clip(1 << np.ceil(np.log2(r)).astype(np.int64), 1, r_max)  # power-of-2 bucket
    pad = r_max + 1
    ix = np.rint(px).astype(np.int64) + pad
    iy = np.rint(py).astype(np.int64) + pad
    keep = (ix >= 0) & (ix < out.shape[1]) & (iy >= 0) & (iy < out.shape[0])
    st["n_in_canvas"] = int(keep.sum())
    for c in np.unique(rc[keep]):
        s = keep & (rc == c)
        yy, xx = iy[s], ix[s]
        y0, y1 = max(int(yy.min()) - c, 0), min(int(yy.max()) + c + 1, out.shape[0])
        x0, x1 = max(int(xx.min()) - c, 0), min(int(xx.max()) + c + 1, out.shape[1])
        sub = np.zeros((y1 - y0, x1 - x0), bool)
        sub[np.clip(yy - y0, 0, y1 - y0 - 1), np.clip(xx - x0, 0, x1 - x0 - 1)] = True
        out[y0:y1, x0:x1] |= dilate_square(sub, int(c))
        st["r_max_used"] = max(st["r_max_used"], int(c))
    return out[pad:pad + h, pad:pad + w], st


# --------------------------------------------------------------------------- #
# per-frame
# --------------------------------------------------------------------------- #
def frame_masks(g, fp_raw, comp, n_comp, cam, hz, spec=None, clip_grid=False,
                out_wh=(OUT_W, OUT_H), r_max=R_MAX):
    """-> (full mask, [(component id, sub mask)], step-gate stats, splat stats)."""
    eye = np.asarray(cam["eye"], float)
    ox, oy = LB._outward(g.XX, g.YY, eye)
    fp, gstat = LB.step_gate(fp_raw, comp, n_comp, g.void_any, g.hm, ox, oy, g.st, hz)
    if clip_grid and spec is not None:
        cell, _ = LB.polar_cells(g.XX, g.YY, eye, cam["yaw"], spec)
        fp = fp & (cell >= 0)
    w_out, h_out = out_wh
    sx, sy = w_out / LB.W_IMG, h_out / LB.H_IMG
    fx_out = LB.focal_px(cam["hfov"]) * sx
    full = np.zeros((h_out, w_out), bool)
    parts, splat = [], dict(n_samples=0, n_in_canvas=0, r_max_used=0, r_capped=0)
    ids = np.unique(comp[fp])
    for cid in ids[ids > 0]:
        m = fp & (comp == cid)
        if not m.any():
            continue
        pts = prism_points(g, m)
        px, py, zc, _ = LB.project(pts, eye, cam)
        sub, s = rasterize(px * sx, py * sy, zc, fx_out, g.st, (h_out, w_out), r_max)
        for k in ("n_samples", "n_in_canvas", "r_capped"):
            splat[k] += s[k]
        splat["r_max_used"] = max(splat["r_max_used"], s["r_max_used"])
        if sub.any():
            parts.append((int(cid), sub))
            full |= sub
    return full, parts, gstat, splat, fp


def boxes_from_parts(parts, w_out, h_out, min_box_px):
    """Per-component mask bbox -> normalised YOLO box (xc, yc, w, h)."""
    out = []
    for cid, sub in parts:
        ys, xs = np.nonzero(sub)
        x0, x1 = int(xs.min()), int(xs.max()) + 1
        y0, y1 = int(ys.min()), int(ys.max()) + 1
        if (x1 - x0) < min_box_px or (y1 - y0) < min_box_px:
            continue
        out.append(dict(comp=cid,
                        xc=round((x0 + x1) / 2.0 / w_out, 6),
                        yc=round((y0 + y1) / 2.0 / h_out, 6),
                        w=round((x1 - x0) / w_out, 6),
                        h=round((y1 - y0) / h_out, 6),
                        px=[x0, y0, x1, y1], area_px=int(sub.sum())))
    return out


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def group_frames(frames):
    """{(arm, scene): [frame, ...]} preserving manifest order."""
    g = {}
    for f in frames:
        arm, scene, _ = split_frame_id(f["frame_id"])
        # D24: one group per (arm, scene, round) -- merged corpus mixes rounds per
        # scene and each round has its own dir/variation.json/heightmaps.
        g.setdefault((arm, scene, f.get("round", "")), []).append(f)
    return g


def run_scene(task):
    (arm, scene, _round), fr, args, hz, spec = task
    t0 = time.time()
    res, warn = {}, []
    if arm != "on":
        for f in fr:
            res[f["frame_id"]] = dict(stem=stem_of(f["frame_id"]), mask=None, boxes=[],
                                      mask_px=0, tier=f.get("tier"), toggle=arm,
                                      scene_id=f["scene_id"], rgb=f["rgb"])
        return res, warn, 0.0
    sdir = scene_dir_of(fr[0])
    off_round = twin_round_dir(fr[0], args["meta"])
    off_dirs = LB.scene_dirs(off_round)
    if scene not in off_dirs:
        warn.append(f"{arm}/{scene}: no off-arm twin under {off_round} -> SKIPPED "
                    f"(footprint v2 needs z_off)")
        return {}, warn, 0.0
    g = SceneGeom(sdir, off_dirs[scene])
    fp_raw, comp, n_comp = g.raw_footprint(hz)
    cuts = cuts_of(sdir)
    labels = args["labels"]
    for f in fr:
        fid = f["frame_id"]
        _, _, fn = split_frame_id(fid)
        cut = cuts.get(fn)
        if cut is None:
            warn.append(f"{fid}: not in variation.json -> SKIPPED")
            continue
        cam = cut["cam"]
        full, parts, gstat, splat, fp = frame_masks(
            g, fp_raw, comp, n_comp, cam, hz, spec, args["clip_grid"],
            (args["w"], args["h"]), args["r_max"])
        lab = labels.get(fid) if labels else None
        if lab is not None and not args["clip_grid"]:
            want = int(lab["footprint"]["cells_kept"])
            got = int(fp.sum())
            if want != got:
                warn.append(f"{fid}: post-gate footprint {got} cells != labels "
                            f"cells_kept {want}")
        boxes = boxes_from_parts(parts, args["w"], args["h"], args["min_box_px"])
        stem = stem_of(fid)
        png = None
        if full.any() and not args["dry_run"]:
            png = stem + ".png"
            Image.fromarray((full.astype(np.uint8) * 255), "L").save(
                os.path.join(args["out"], png), optimize=True)
        elif full.any():
            png = stem + ".png"
        res[fid] = dict(stem=stem, mask=png, boxes=boxes, mask_px=int(full.sum()),
                        tier=f.get("tier"), toggle=arm, scene_id=f["scene_id"],
                        rgb=f["rgb"], comps_kept=int(gstat["comps_kept"]),
                        fp_cells=int(fp.sum()), splat=splat)
    return res, warn, time.time() - t0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--labels", default=None,
                    help="labels_v*.json -- used for the per-frame cells_kept cross-check")
    ap.add_argument("--out", default=os.path.join(DAYRUN, "annotations", "amodal"))
    ap.add_argument("--grid", default=None)
    ap.add_argument("--scenes", default="", help="comma list, default all")
    ap.add_argument("--width", type=int, default=OUT_W)
    ap.add_argument("--min-box-px", type=int, default=3,
                    help="drop boxes thinner than this many OUTPUT pixels")
    ap.add_argument("--clip-grid", action="store_true",
                    help="restrict the footprint to the polar grid wedge before projecting")
    ap.add_argument("--r-max", type=int, default=R_MAX)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="compute everything, write nothing")
    ap.add_argument("--selftest", action="store_true", help="run the 3-frame self-test and exit")
    a = ap.parse_args(argv)

    grid, spec, gpath = load_grid(a.grid)
    hz = float(spec["hazard_depth_m"])
    man = json.load(open(a.manifest))
    meta, frames = man.get("meta", {}), man["frames"]
    if a.scenes:
        keep = set(a.scenes.split(","))
        frames = [f for f in frames if f["scene_id"] in keep]
    labels = {}
    if a.labels:
        labels = json.load(open(a.labels)).get("frames", {})

    if a.selftest:
        return selftest(a, meta, frames, labels, spec, hz, grid, gpath)

    os.makedirs(a.out, exist_ok=True)
    args = dict(meta=meta, labels=labels, out=a.out, clip_grid=a.clip_grid,
                w=a.width, h=int(round(a.width * LB.H_IMG / LB.W_IMG)),
                min_box_px=a.min_box_px, r_max=a.r_max, dry_run=a.dry_run)
    tasks = [(k, v, args, hz, spec) for k, v in sorted(group_frames(frames).items())]
    t0 = time.time()
    if a.workers > 1:
        import multiprocessing as mp
        with mp.Pool(a.workers) as p:
            out = p.map(run_scene, tasks, chunksize=1)
    else:
        out = [run_scene(t) for t in tasks]

    res, warns = {}, []
    for r, w, _ in out:
        res.update(r)
        warns += w
    n_on = sum(1 for v in res.values() if v["toggle"] == "on")
    n_mask = sum(1 for v in res.values() if v["mask_px"] > 0)
    n_box = sum(len(v["boxes"]) for v in res.values())
    empty_on = sorted(k for k, v in res.items() if v["toggle"] == "on" and v["mask_px"] == 0)
    doc = dict(meta=dict(created=time.strftime("%Y-%m-%dT%H:%M:%S"),
                         manifest=os.path.abspath(a.manifest),
                         labels=os.path.abspath(a.labels) if a.labels else None,
                         grid=gpath, grid_version=grid.version, hazard_depth_m=hz,
                         mask_wh=[args["w"], args["h"]],
                         source_wh=[LB.W_IMG, LB.H_IMG],
                         class_id=0, class_name=CLASS_NAME,
                         clip_grid=bool(a.clip_grid), min_box_px=a.min_box_px,
                         r_max=a.r_max,
                         method=("prism silhouette (top z_off + bottom z_on + boundary walls) "
                                 "splatted with a depth-adaptive square of radius "
                                 "ceil(f_px_out*0.05/z), power-of-two bucketed, exact separable "
                                 "binary dilation; occlusion ignored"),
                         geometry_source="experiments/mainrun_0819/code/labeling/labeler.py",
                         counts=dict(frames=len(res), on=n_on, off=len(res) - n_on,
                                     masks_written=n_mask, boxes=n_box,
                                     on_frames_empty=len(empty_on)),
                         on_frames_empty=empty_on[:40], warnings=warns),
              frames=res)
    if not a.dry_run:
        with open(os.path.join(a.out, "bboxes.json"), "w") as f:
            json.dump(doc, f, indent=1)
    print(f"[amodal] frames={len(res)} on={n_on} off={len(res) - n_on} "
          f"masks={n_mask} boxes={n_box} empty_on={len(empty_on)} "
          f"warn={len(warns)} in {time.time() - t0:.1f}s -> {a.out}"
          + (" (DRY RUN, nothing written)" if a.dry_run else ""))
    for w in warns[:10]:
        print("  WARN", w, file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #
# self-test
# --------------------------------------------------------------------------- #
SELFTEST_FRAMES = ["on/scene04/L0__s20260819__0001.png",   # V  -- drop directly visible
                   "on/scene14/L0__s20260819__0000.png",   # H  -- zero visible hazard pixels
                   "on/scene18/L0__s20260819__0002.png"]   # E  -- rim only
"""Overridable with --scenes; these three are the brief's named cases plus one
E-tier control.  Chosen from dataset_manifest_v2.json (tier field)."""


def visible_hit_mask(g, fp, cam, dep):
    """The labeler's `int_px` test, reproduced by calling LB.unproject: reprojected
    pixels that land inside the footprint AND >= INTERIOR_MARGIN_M below the
    counterfactual walkable surface.  This is the ground truth for "the drop area
    the camera can actually see", at the labeler's DS=4 lattice."""
    eye = np.asarray(cam["eye"], float)
    P, good = LB.unproject(dep, eye, cam, LB.DS)
    x0, y0, st = g.geo
    ny, nx = g.hm.shape
    gx = np.rint((np.where(good, P[..., 0], x0) - x0) / st).astype(np.int64)
    gy = np.rint((np.where(good, P[..., 1], y0) - y0) / st).astype(np.int64)
    inb = good & (gx >= 0) & (gx < nx) & (gy >= 0) & (gy < ny)
    gxc, gyc = np.clip(gx, 0, nx - 1), np.clip(gy, 0, ny - 1)
    zo = g.hm_off[gyc, gxc]
    on_fp = inb & fp[gyc, gxc]
    fb = on_fp & ~np.isfinite(zo) & (P[..., 2] <= float(cam["ground_z"]) - LB.INTERIOR_MARGIN_M)
    return (on_fp & np.isfinite(zo) & (P[..., 2] <= zo - LB.INTERIOR_MARGIN_M)) | fb


def selftest(a, meta, frames, labels, spec, hz, grid, gpath):
    byid = {f["frame_id"]: f for f in frames}
    want = [f for f in SELFTEST_FRAMES if f in byid]
    if len(want) < 3:
        print(f"[selftest] FAIL: only {len(want)}/3 self-test frames present in the manifest",
              file=sys.stderr)
        return 2
    w_out = a.width
    h_out = int(round(w_out * LB.H_IMG / LB.W_IMG))
    rows, ok_all = [], True
    for fid in want:
        f = byid[fid]
        _, scene, fn = split_frame_id(fid)
        sdir = scene_dir_of(f)
        off = LB.scene_dirs(twin_round_dir(f, meta))[scene]
        g = SceneGeom(sdir, off)
        fp_raw, comp, n_comp = g.raw_footprint(hz)
        cam = cuts_of(sdir)[fn]["cam"]
        full, parts, gstat, splat, fp = frame_masks(g, fp_raw, comp, n_comp, cam, hz,
                                                    spec, a.clip_grid, (w_out, h_out), a.r_max)
        dep = np.load(f["depth"]).astype(np.float64)
        vis = visible_hit_mask(g, fp, cam, dep)                     # (270, 480) at DS=4
        # visible pixels -> output-mask coordinates (DS=4 lattice of a 1920x1080 image)
        vy, vx = np.nonzero(vis)
        my = np.clip(((vy * LB.DS + 0.5) * h_out / LB.H_IMG).astype(int), 0, h_out - 1)
        mx = np.clip(((vx * LB.DS + 0.5) * w_out / LB.W_IMG).astype(int), 0, w_out - 1)
        cov = float(full[my, mx].mean()) if vy.size else float("nan")

        # occlusion probe: footprint samples whose rendered depth is NEARER than
        # the sample itself -> the mask is continuing behind something.
        pts = prism_points(g, fp)
        px, py, zc, inb = LB.project(pts, eye=np.asarray(cam["eye"], float), cam=cam)
        s = inb & (zc > 0.05)
        d = dep[np.clip(py[s].astype(int), 0, LB.H_IMG - 1),
                np.clip(px[s].astype(int), 0, LB.W_IMG - 1)]
        occ = int((np.isfinite(d) & (d < zc[s] - LB.RIM_TOL_M)).sum())
        n_in = int(s.sum())

        lab = labels.get(fid, {})
        int_px = (lab.get("raw_vis") or {}).get("int_px")
        cells_kept = (lab.get("footprint") or {}).get("cells_kept")
        checks = []
        checks.append(("mask non-empty", bool(full.any())))
        checks.append(("boxes >= 1", len(boxes_from_parts(parts, w_out, h_out,
                                                          a.min_box_px)) >= 1))
        if cells_kept is not None and not a.clip_grid:
            checks.append((f"post-gate cells == labels ({cells_kept})",
                           int(fp.sum()) == int(cells_kept)))
        if f["tier"] == "V":
            checks.append((f"covers visible drop area (cov={cov:.3f} >= 0.90)",
                           np.isfinite(cov) and cov >= 0.90))
            checks.append((f"continues behind occluder (occluded samples={occ} > 0)", occ > 0))
        if f["tier"] == "H":
            checks.append((f"zero visible hazard pixels (labeler int_px={int_px})",
                           int_px == 0 and int(vis.sum()) == 0))
            checks.append(("non-empty mask despite zero visible pixels", bool(full.any())))
        if f["tier"] == "E":
            checks.append(("rim-only frame still masked", bool(full.any())))
        good = all(v for _, v in checks)
        ok_all &= good
        rows.append((fid, f["tier"], int(full.sum()), len(parts), int(vis.sum()), cov,
                     occ, n_in, checks, good))

    print(f"[selftest] grid={grid.version} ({gpath})  mask {w_out}x{h_out}")
    print(f"{'frame':46s} {'tier':5s} {'mask_px':>8s} {'comp':>4s} {'vis_px':>7s} "
          f"{'cov':>6s} {'occl':>7s} {'proj':>8s}  verdict")
    for fid, tier, mpx, nc, vpx, cov, occ, n_in, checks, good in rows:
        print(f"{fid:46s} {tier:5s} {mpx:8d} {nc:4d} {vpx:7d} "
              f"{cov if np.isfinite(cov) else float('nan'):6.3f} {occ:7d} {n_in:8d}  "
              f"{'PASS' if good else 'FAIL'}")
        for name, v in checks:
            print(f"    [{'ok' if v else 'XX'}] {name}")
    print(f"[selftest] {'ALL PASS' if ok_all else 'FAILURES PRESENT'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
