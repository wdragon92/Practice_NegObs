#!/usr/bin/env python3
"""Depth-fusion heightmaps (`heightmap_fused.npy`) for scenes the top-down AABB ray
cannot measure.

WHY
---
`heightmap.npy` is sampled by `variation_kit.AabbPrefilter.ground_z(top=+60)`: one
vertical ray per cell, from the sky down, first hit wins.  Any hazard that sits
UNDER a structure -- an underpass mouth, a deck, a canopy, a station roof -- is
therefore measured as the STRUCTURE TOP, identically on both toggle arms, so the
D10 twin difference is ~0 and every on-arm frame is labelled `none_in_fov`
(GATES_REPORT G2: scene02/06/07/08/11/13/19).

WHAT
----
The corpus already carries the instrument that CAN see under a roof: the per-cut
`.depth.npy` sidecars (D4).  This script unprojects every cut of one scene-arm
with the labeler's own camera math (imported, never re-spelled), pools the world
points of all 24 views, and re-bins them into the SAME 321x321 / 5 cm grid.

Per cell the surface height is a LOW percentile of the pooled z (p5), because the
thing we want is the walking / drop-floor surface and everything a camera adds on
top of it -- railings, props, people-height clutter, the wall face between the
lip and the floor -- lies ABOVE that surface, never below it.  Two guards keep the
low percentile from digging into noise:

  * stragglers: points more than STRAGGLER_M below the cell's p20 are dropped
    before p5 is taken (a handful of bad depth pixels cannot define the floor),
  * thin cells: a cell left with fewer than MIN_PTS points is NaN, i.e. void,
    i.e. excluded from the footprint exactly like an unmeasured AABB cell.

View filters, in world space, per cut: finite depth, depth < DEPTH_MAX, z at most
EYE_MARGIN above that cut's eye (a surface above the camera is roof/ceiling, not
ground -- and every cut in this corpus pitches DOWN), and XY inside the grid plus
GRID_MARGIN.  Cells with no coverage stay NaN.

The output is a SIDECAR: `heightmap_fused.npy` + `heightmap_fused_meta.json`
written NEXT TO the AABB pair, which is never touched.  `labeler.load_heightmap`
prefers the fused map when it exists and records `hm_source` per scene-arm.

PER-ARM SELECTION -- the fused map is not automatically the better one
---------------------------------------------------------------------
The two instruments fail in opposite directions, so the choice is made ARM BY ARM
(that is what "prefer the fused map if present" buys: presence is the switch).

  * the AABB ray is COMPLETE (every cell, no view shadow) but reads the first
    thing under the sky -- a roof, a deck, or a prim that the toggle only made
    INVISIBLE rather than deleted.  The second failure is why an off arm can
    still report the hazard it is supposed to have removed, which is the actual
    reason scene07/08 differenced to zero.
  * depth fusion reads exactly what the camera rendered -- no hidden prims, no
    roofs -- but only where a camera looked.  A drop's own floor right behind its
    lip is in the view shadow, so a deep bowl or a roofed trench comes back as a
    ring of far wall with a VOID interior, and the D10 step gate then finds no
    walkable near boundary and discards the component.

So: fuse the arm whose AABB is demonstrably wrong (verified by disagreement with
the rendered depth), and keep the AABB on the arm where the two agree, because
there the AABB is the same surface with none of the holes.  Measured on this
round (median |fused - aabb| over cells both instruments fill):

  scene02  on 0.003 / off 0.005   -- both agree in general, but the AABB ON reads
           the plaza deck (2.84) over the underpass mouth where the floor is
           -0.59: the disagreement IS the hazard.  fused / fused.
  scene07  on 0.004 / off 1.967   -- AABB OFF still carries the removed terrain;
           AABB ON never reaches the +4.0 terrace the cameras stand on.
           fused / fused.
  scene08  on 0.002 / off 2.400   -- AABB ON is sound and complete (the bowl is
           open to the sky); only the OFF arm is contaminated.  aabb / fused,
           which is what keeps the bowl's near rim and its step-gate boundary.

Round 2 (scene12, scene16) -- both ended on fused/fused, and BOTH mixed pairings
were rejected by the same audit, for two different reasons worth remembering:

  scene12  on 0.001 / off 0.600   -- by the agreement rule alone this is scene08
           again (sound AABB ON, contaminated AABB OFF -> aabb/fused).  It is
           not: the AABB ray passes THROUGH the river and reads the bed at
           -2.40, while a camera sees the water surface at -1.80.  Pairing
           aabb ON against fused OFF turns that 0.6 m instrument offset into
           9532 phantom footprint cells of open water.  Matching the instrument
           on both arms cancels it exactly (fused/fused: 0 such cells).
  scene16  on 0.006 (p90 2.87) / off 0.0005  -- the ON median hides the fault:
           the AABB ON is right everywhere EXCEPT over the roofed passage, where
           it reads the deck at +2.16 instead of the floor at -3.00.  Fusing ON
           is therefore mandatory.  Fusing OFF is not indicated by the median,
           but the AABB OFF reads that same deck at +2.16 over a walkway the
           toggle has filled to 0.00, so aabb OFF puts a structure top at the
           top of the diff and inflates max_diff to 4.30.  fused/fused.

A LOW percentile cannot rescue a cell the cameras never saw under a structure:
in scene16's OFF arm 532 cells (0.5 % of the grid) still hold the deck rather
than the ground beneath it.  One of them survives into the footprint and owns
the fused/fused max_diff (3.90); over the other 10324 footprint cells the drop
measures 3.022 m = 1.007x the design table.  Treat a single-cell max as what it
is -- an extremum over 100k cells -- and read the neighbouring percentile too.

`--remove` deletes a scene's sidecars again, which is how a scene that fails the
acceptance band is put back on the AABB instrument.
"""
import argparse, json, os, sys, time
import numpy as np

from labeler import unproject, HM_DEFAULT, scene_dirs, W_IMG, H_IMG

SOURCE_TAG = "depth-fusion-v1"

DEPTH_MAX_M = 40.0
"""Beyond ~40 m a z-depth pixel is sky, backdrop or HDRI proxy, never scene floor;
the polar grid itself stops at 12 m, so this only trims what could pollute."""

EYE_MARGIN_M = 0.5
"""A world point more than this ABOVE the cut's eye is not ground for that view.
Every cut pitches down (-17.7 deg .. -2.5 deg over the 7 rescue scenes), so what
lands above the eye plane is a roof underside, a wall high on the far side, or a
depth straggler.  0.5 m keeps the near ground of a low camera on a rising floor."""

GRID_MARGIN_M = 2.0
"""Pre-bin XY slack around the grid box, per the rescue brief (|x| <= 14+2,
|y| <= 8+2).  Binning clips to the grid anyway; this only saves the arithmetic."""

MIN_PTS = 5
"""Fewer surviving points than this and the cell is void.  A cell is 5x5 cm and a
1920x1080 view at DS=2 puts hundreds of samples per square metre inside 12 m, so
a cell under MIN_PTS is grazing-angle or barely-glimpsed geometry."""

P_LOW, P_REF = 5.0, 20.0
"""p5 = the reported surface; p20 = the straggler reference.  p20 is high enough
to be immune to the same outliers p5 is exposed to, low enough to still sit on
the floor rather than on the clutter above it."""

STRAGGLER_M = 0.5
"""Points more than this below the cell's p20 are discarded before p5 is taken."""

DS_DEFAULT = 2
"""Pixel stride for unprojection.  DS=2 -> 518k samples/cut, ~12M pooled per
scene-arm over 24 cuts: ~120 per grid cell, far above MIN_PTS, at a few seconds
of CPU per scene-arm."""


# --------------------------------------------------------------------------- #
def grid_geometry(sdir):
    """(x0, y0, step, ny, nx) of the scene-arm's EXISTING heightmap -- the fused
    map must land on the identical lattice or the twin diff is meaningless."""
    hm = np.load(os.path.join(sdir, "heightmap.npy"))
    mp = os.path.join(sdir, "heightmap_meta.json")
    meta = json.load(open(mp)) if os.path.isfile(mp) else {}
    return (float(meta.get("x0", HM_DEFAULT["x0"])),
            float(meta.get("y0", HM_DEFAULT["y0"])),
            float(meta.get("step", HM_DEFAULT["step"])),
            hm.shape[0], hm.shape[1]), meta


def _cell_percentile(cellf, z, nx, ny):
    """Per-cell p5 of z after the p20 straggler cut.  Returns (grid, n_pts grid).

    Sorted lexicographically by (cell, z), so every cell owns a contiguous run and
    a percentile is an index, not a sort.  The straggler cut needs a per-cell
    binary search, which is vectorised through a composite key
    (cell * 1000 + z + 500) -- monotone inside a cell AND across cells because the
    z span of this corpus is far under the 1000 m stride.
    """
    n = ny * nx
    out = np.full(n, np.nan)
    cnt_g = np.zeros(n, np.int32)
    if cellf.size == 0:
        return out.reshape(ny, nx), cnt_g.reshape(ny, nx)
    order = np.lexsort((z, cellf))
    cs, zs = cellf[order], z[order].astype(np.float64)
    uc, start = np.unique(cs, return_index=True)
    end = np.append(start[1:], cs.size)
    cnt = end - start

    i20 = start + np.floor((P_REF / 100.0) * (cnt - 1)).astype(np.int64)
    thr = zs[i20] - STRAGGLER_M
    key = cs.astype(np.float64) * 1000.0 + zs + 500.0
    kthr = uc.astype(np.float64) * 1000.0 + thr + 500.0
    new_start = np.searchsorted(key, kthr, side="left")
    new_start = np.maximum(new_start, start)                 # never leave the cell
    kept = end - new_start

    ok = kept >= MIN_PTS
    i5 = new_start[ok] + np.floor((P_LOW / 100.0) * (kept[ok] - 1)).astype(np.int64)
    out[uc[ok]] = zs[i5]
    cnt_g[uc] = kept
    return out.reshape(ny, nx), cnt_g.reshape(ny, nx)


def fuse_scene_arm(sdir, ds=DS_DEFAULT):
    """Fused heightmap + meta for one scene-arm directory."""
    t0 = time.time()
    (x0, y0, st, ny, nx), old_meta = grid_geometry(sdir)
    var = json.load(open(os.path.join(sdir, "variation.json")))
    cuts = var["cuts"]
    if isinstance(cuts, dict):
        cuts = list(cuts.values())

    xlo, xhi = x0 - GRID_MARGIN_M, x0 + (nx - 1) * st + GRID_MARGIN_M
    ylo, yhi = y0 - GRID_MARGIN_M, y0 + (ny - 1) * st + GRID_MARGIN_M
    C, Z, n_views, missing = [], [], 0, []
    for c in cuts:
        cam, fn = c["cam"], c["file"]
        dep_p = os.path.join(sdir, c.get("depth") or os.path.splitext(fn)[0] + ".depth.npy")
        if not os.path.isfile(dep_p):
            missing.append(fn); continue
        dep = np.load(dep_p).astype(np.float64)
        if dep.shape != (H_IMG, W_IMG):
            missing.append(f"{fn}:shape{dep.shape}"); continue
        eye = np.asarray(cam["eye"], dtype=np.float64)
        P, good = unproject(dep, eye, cam, ds)               # labeler's camera math
        dd = dep[::ds, ::ds]
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        m = (good & (dd < DEPTH_MAX_M) & (z <= eye[2] + EYE_MARGIN_M)
             & (x >= xlo) & (x <= xhi) & (y >= ylo) & (y <= yhi))
        if not m.any():
            n_views += 1; continue
        gx = np.rint((x[m] - x0) / st).astype(np.int64)
        gy = np.rint((y[m] - y0) / st).astype(np.int64)
        inb = (gx >= 0) & (gx < nx) & (gy >= 0) & (gy < ny)
        C.append((gy[inb] * nx + gx[inb]).astype(np.int64))
        Z.append(z[m][inb].astype(np.float64))
        n_views += 1

    cellf = np.concatenate(C) if C else np.zeros(0, np.int64)
    zz = np.concatenate(Z) if Z else np.zeros(0)
    hm, cnt = _cell_percentile(cellf, zz, nx, ny)

    fin = np.isfinite(hm)
    meta = dict(x0=x0, y0=y0, step=st, nx=int(nx), ny=int(ny),
                order="z[y_idx,x_idx]",
                x_range=[x0, x0 + (nx - 1) * st], y_range=[y0, y0 + (ny - 1) * st],
                scene=old_meta.get("scene", os.path.basename(sdir)),
                arm_config=old_meta.get("arm_config"),
                nodata="NaN", source=SOURCE_TAG, n_views=int(n_views),
                n_finite=int(fin.sum()), n_total=int(hm.size),
                z_min=round(float(np.nanmin(hm)), 4) if fin.any() else None,
                z_max=round(float(np.nanmax(hm)), 4) if fin.any() else None,
                sec=round(time.time() - t0, 2),
                fusion=dict(ds=ds, depth_max_m=DEPTH_MAX_M, eye_margin_m=EYE_MARGIN_M,
                            grid_margin_m=GRID_MARGIN_M, min_pts=MIN_PTS,
                            p_low=P_LOW, p_ref=P_REF, straggler_m=STRAGGLER_M,
                            n_points=int(cellf.size),
                            pts_per_cell_median=int(np.median(cnt[fin])) if fin.any() else 0,
                            missing_depth=missing),
                aabb_ref=dict(n_finite=old_meta.get("n_finite"),
                              z_min=old_meta.get("z_min"), z_max=old_meta.get("z_max"),
                              source=old_meta.get("source")))
    return hm, meta


def write_pair(sdir, hm, meta):
    np.save(os.path.join(sdir, "heightmap_fused.npy"), hm.astype(np.float32))
    json.dump(meta, open(os.path.join(sdir, "heightmap_fused_meta.json"), "w"), indent=1)


def remove_pair(sdir):
    n = 0
    for b in ("heightmap_fused.npy", "heightmap_fused_meta.json"):
        p = os.path.join(sdir, b)
        if os.path.isfile(p):
            os.remove(p); n += 1
    return n


def compare(hm_on, hm_off, hz, st):
    """Twin-diff summary of a fused pair, for the acceptance band (brief step 3)."""
    void = ~np.isfinite(hm_on) | ~np.isfinite(hm_off)
    diff = np.where(void, np.nan, hm_off - hm_on)
    fp = (~void) & (diff >= hz)
    out = dict(max_diff=round(float(np.nanmax(diff)), 4) if np.isfinite(diff).any() else None,
               fp_cells=int(fp.sum()),
               void_cells=int(void.sum()),
               void_frac=round(float(void.mean()), 4),
               cover_on=round(float(np.isfinite(hm_on).mean()), 4),
               cover_off=round(float(np.isfinite(hm_off).mean()), 4))
    if fp.any():                        # void right around the measured hazard
        iy, ix = np.nonzero(fp)
        pad = int(round(1.0 / st))
        sl = (slice(max(iy.min() - pad, 0), iy.max() + pad + 1),
              slice(max(ix.min() - pad, 0), ix.max() + pad + 1))
        out["hazard_bbox_cells"] = int(void[sl].size)
        out["hazard_void_frac"] = round(float(void[sl].mean()), 4)
        out["fp_mean_drop"] = round(float(np.nanmean(diff[fp])), 4)
    else:
        out["hazard_bbox_cells"] = 0
        out["hazard_void_frac"] = 1.0
        out["fp_mean_drop"] = None
    return out


def _worker(t):
    sdir, ds = t
    try:
        hm, meta = fuse_scene_arm(sdir, ds)
        write_pair(sdir, hm, meta)
        return sdir, meta, None
    except Exception as e:
        return sdir, None, f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--on-round", required=True)
    ap.add_argument("--off-round", required=True)
    ap.add_argument("--scenes", required=True, help="comma-separated sceneIDs")
    ap.add_argument("--grid", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "gridspec_v0.json"))
    ap.add_argument("--ds", type=int, default=DS_DEFAULT)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--remove", action="store_true",
                    help="delete the fused sidecars of --scenes instead of writing them")
    ap.add_argument("--json-out", default="")
    a = ap.parse_args()

    hz = float(json.load(open(a.grid))["hazard_depth_m"])
    on, off = scene_dirs(a.on_round), scene_dirs(a.off_round)
    scenes = [s for s in a.scenes.split(",") if s]

    if a.remove:
        for s in scenes:
            for d in (on.get(s), off.get(s)):
                if d:
                    print(f"[fuse] removed {remove_pair(d)} file(s) in {d}")
        return

    tasks = []
    for s in scenes:
        for arm, dd in (("on", on), ("off", off)):
            if s not in dd:
                print(f"[fuse] MISSING {arm}/{s}", file=sys.stderr); continue
            tasks.append((dd[s], a.ds))
    if a.workers > 1:
        import multiprocessing as mp
        with mp.Pool(a.workers) as p:
            res = p.map(_worker, tasks, chunksize=1)
    else:
        res = [_worker(t) for t in tasks]
    metas = {}
    for sdir, meta, err in res:
        if err:
            print(f"[fuse] FAIL {sdir}: {err}", file=sys.stderr); continue
        metas[os.path.abspath(sdir)] = meta
        print(f"[fuse] {meta['scene']:9s} {os.path.basename(os.path.dirname(os.path.dirname(sdir)))}"
              f"  views={meta['n_views']}  finite={meta['n_finite']}/{meta['n_total']}"
              f"  z=[{meta['z_min']},{meta['z_max']}]  {meta['sec']}s")

    rep = {}
    for s in scenes:
        if s not in on or s not in off:
            continue
        po, pf = os.path.join(on[s], "heightmap_fused.npy"), os.path.join(off[s], "heightmap_fused.npy")
        if not (os.path.isfile(po) and os.path.isfile(pf)):
            continue
        hm_on = np.load(po).astype(np.float64)
        hm_off = np.load(pf).astype(np.float64)
        st = float(metas.get(os.path.abspath(on[s]), {}).get("step", HM_DEFAULT["step"]))
        rep[s] = compare(hm_on, hm_off, hz, st)
        print(f"[fuse] {s}: " + "  ".join(f"{k}={v}" for k, v in rep[s].items()))
    if a.json_out:
        json.dump(rep, open(a.json_out, "w"), indent=1)


if __name__ == "__main__":
    main()
