#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hash_gate.py — the C2 (dressing-control) admission gate. Renders NOTHING.

Three questions, one exit code (0 = every check passed, 1 = at least one failed):

  (a) IMMUTABILITY   Did the control round disturb any frozen round?
                     `snapshot` records (size, mtime_ns) for every file of the
                     protected rounds plus sha256 of a deterministic sample;
                     `verify` re-reads them.  Run `snapshot` BEFORE the render.
  (b) TWIN POSE      Is every cut of the new OFF round byte-equal in camera pose
                     to the SAME cut of the ON arm?  The whole `cam` dict of
                     `variation.json` is compared field by field, all cuts, all
                     conditions -- `ground_z` included, which is the one field
                     the old OFF arm got wrong (D20: 0.130 -> 0.0163 m, 24/24
                     cuts excluded from the twin analysis).
  (c) GEOMETRY       Did the toggle remove the hazard and ONLY the hazard?
                     Per-scene rules over the 5 cm height-map sidecar, below.

The height map is `variation_kit.AabbPrefilter.ground_z(top=60)` sampled on a
5 cm lattice (`run_data_render.py:840-882`), i.e. the top of the highest prim
AABB over each column -- NOT the analytic surface.  That is why the ON arm reads
+0.200 over the leaf-mound-B footprint (mound B's AABB top, its declared crest
z0) where the sloped leaf face is at +0.084 at x=0 (`sceneC2_leaf_stairs.py`
PARAMS['mound'] B, and DIAG_V1 §3.1).  The gate therefore asserts EQUALITY with
the ON arm over the dressing region rather than a literal +0.084, and prints the
value it found at the crest so the number can be read off the log.

usage
  python3 hash_gate.py snapshot                    # before the render (CPU, ~20 s)
  python3 hash_gate.py verify                      # after the render (CPU, ~30 s)
  python3 hash_gate.py verify --skip-immutability  # (b)+(c) only, e.g. mid-debug
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat, rounds_matching   # noqa: E402

# --------------------------------------------------------------------------- #
# what may not move
# --------------------------------------------------------------------------- #
PROTECTED = ["260819_main_on", "260819_main_off"] + sorted(
    os.path.basename(p) for p in rounds_matching("260820_boost_"))
"""Both arms of the frozen main corpus and every boost round.  The brief's rule 2
freezes `_v2_full`; the off arm is in it too, and this track re-reads the old off
arm's per-frame CSVs for the side-by-side table, so its immutability matters as
much as the on arm's."""

SAMPLE_PNG_PER_ROUND = 24
"""sha256 sample size per round.  Deterministic (`sorted(files)[::stride]`), so
two snapshots of an untouched round produce the same sample."""

CTRL_ROUND = "260820_ctrloff"
ON_ROUND = "260819_main_on"
SCENES = ("sceneC2", "sceneN3")

# --------------------------------------------------------------------------- #
# (c) per-scene geometry rules -- every constant carries its source
# --------------------------------------------------------------------------- #
HAZARD_DEPTH_M = 0.30      # gridspec_v1.json "hazard_depth_m"
STEP_RUN_M = 1.0           # labeler.py:52 STEP_RUN_M (the step-gate window)
CORRIDOR_Y = 1.62          # sceneC2 PARAMS['upper']['y_half'] -- the walk width
DROP_EDGE_X = 0.0          # sceneC2 PARAMS['stairs']['x0'] -- the old drop edge
DATUM_Y = 0.90
"""Lateral half-width the camera sampler can reach: `variation_kit.CAM_DIST`
yoff = (0.0, 0.35, -0.90, 0.90), truncated normal, so |y| <= 0.90 always
(`sample_camera` :618).  With d in [1.2, 12] the eye is always at x = -d < 0.
`ground_z(-d, y)` therefore only ever reads the strip x<0, |y|<=0.90 -- the
strip this gate requires to be byte-identical to the ON arm."""
WALK_Y = 1.20
"""Walked strip used for the flatness rows: inside the corridor but clear of the
railing line (y = 1.45 +- post radius, PARAMS['rail']['y']) and of the coping
band (|y| 1.28..1.62, PARAMS['coping']).  Those two are structures, not ground,
and the height map reads their AABB tops."""
COPING_Y_IN = 1.28         # sceneC2 PARAMS['coping']['y_in']
COPING_Y_OUT = 1.62        # sceneC2 PARAMS['coping']['y_out']
COPING_X0 = -0.25          # -PARAMS['coping']['ext'] -- the coping starts upstream of the edge


def _slope_aabb_x0(x0, z0, run, drop, thick, margin=0.0):
    """World AABB x-min of a `scene_common.build_slope` plate (:2749).

    `build_slope` authors ONE rotateY'd Cube, so its world AABB is the bound of a
    tilted box, which overhangs the analytic top-face span at both ends by the
    thickness corner.  The height map reads AABB tops, not surfaces (see the
    module docstring), so a mask written against the analytic `x0` is too narrow
    by exactly that overhang."""
    ang = math.atan2(drop, run)
    L = math.hypot(run, drop) + margin
    cx = (x0 + run / 2.0) - (thick / 2.0) * math.sin(ang)
    return cx - ((L / 2.0) * abs(math.cos(ang)) + (thick / 2.0) * abs(math.sin(ang)))


_SLOPE = 0.16 / 0.34       # PARAMS['stairs'] riser/tread -- the nosing line
_C_RUN = 0.34 * 14 + 2 * 0.25      # RUN + 2*PARAMS['coping']['ext']
COPING_AABB_X0 = _slope_aabb_x0(
    COPING_X0, -_SLOPE * COPING_X0 + 0.12, _C_RUN, _SLOPE * _C_RUN, 0.55)
"""-0.48419 m: the upstream end of `Coping_N/S`'s **world AABB**, 0.234 m upstream
of the analytic `x0 = -0.25`.

`build_stairs` builds the coping with `build_slope(cx0=-ext, cz0=+0.237647,
crun=5.26, cdrop=2.4753, thick=0.55, margin=0.0)`, i.e. a 5.813 m box tilted
25.20 deg.  Its AABB is x [-0.48419, 5.010], z_max **+0.237647** -- the top-face
corner at x=-0.25, carried 0.234 m upstream by the tilt.  Every 5 cm column whose
centre lands in that overhang therefore reads +0.23765 in the ON arm and drops to
LeafMound_A's AABB top (+0.13000) once `build_stairs` is skipped -- 39 cells at
x in {-0.45,-0.40,-0.35}, |y| in [1.30, 1.60], **all coping, no dressing**.

The coping is hazard geometry by construction: `sceneC2_leaf_stairs.py:1315`
("No `build_stairs` (stair + coping = the hazard)") and the `keep_dressing`
docstring's removal list (stair + coping + side slopes + lower ground).  The
plate's solid, as opposed to its AABB, is buried over this whole span -- it sits
below z=0 for x <= -0.375 and inside LeafMound_A's 0.15 m plate at x=-0.35..-0.325,
first clearing the leaf surface only at x ~ -0.30 `[computed]` -- so not one pixel
of the 24 cuts changes here.  Widened in x, and simultaneously **tightened in y**
to the coping's own `y_out`: a difference outside |y| <= 1.62 cannot be the coping
and must still fail."""
MOUND_B = dict(x0=-0.25, x1=1.02, y_half=1.33)
"""sceneC2 PARAMS['mound'] entry B (x0 -0.25, run 1.27, y_half 1.33): the burial
ramp whose crest is the scene's identity.  Its AABB is what the height map reads
over that footprint in BOTH arms."""
FLAT_TOL_M = 0.05
"""How far the fill may sit from the approach datum (z=0) before it stops being
"flat".  0.05 m = one height-map cell of slope tolerance, and 1/6 of the hazard
threshold."""
EQ_TOL_M = 1e-6            # "byte-equal" for float32 height maps written by the same code path


def _load_hm(sdir):
    Z = np.load(os.path.join(sdir, "heightmap.npy"))
    meta = json.load(open(os.path.join(sdir, "heightmap_meta.json")))
    return Z.astype(np.float64), meta


def _axes(meta):
    x = float(meta["x0"]) + np.arange(int(meta["nx"])) * float(meta["step"])
    y = float(meta["y0"]) + np.arange(int(meta["ny"])) * float(meta["step"])
    return x, y


def _max_local_drop(Z, x, y, win_m, corridor_y):
    """Largest z(x) - z(x + dx) over 0 < dx <= win_m, along +X, |y| <= corridor_y.

    The same quantity the labeler's step gate measures (labeler.py:312 step_gate),
    restricted to the walk corridor -- a hazard that is really gone leaves no
    window with a >= 0.30 m descent."""
    step = float(y[1] - y[0])
    k = max(1, int(round(win_m / step)))
    m = np.abs(y) <= corridor_y
    S = Z[m, :]
    worst, at = 0.0, None
    for dx in range(1, k + 1):
        d = np.where(np.isfinite(S[:, :-dx] - S[:, dx:]), S[:, :-dx] - S[:, dx:], -np.inf)
        if not np.isfinite(d).any():
            continue
        jj = np.unravel_index(int(np.argmax(d)), d.shape)
        v = float(d[jj])
        if v > worst:
            worst, at = v, (float(x[jj[1]]), float(y[m][jj[0]]), dx * step)
    return worst, at


def check_geometry_C2(on_dir, new_dir, rep):
    Zon, mon = _load_hm(on_dir)
    Znew, mnew = _load_hm(new_dir)
    for k in ("x0", "y0", "step", "nx", "ny", "order"):
        if mon[k] != mnew[k]:
            return rep.fail("C2 heightmap", f"grid meta {k} differs: {mon[k]} vs {mnew[k]}")
    x, y = _axes(mon)
    XX, YY = np.meshgrid(x, y)
    fin = np.isfinite(Zon) & np.isfinite(Znew)
    if not np.array_equal(np.isfinite(Zon), np.isfinite(Znew)):
        n = int((np.isfinite(Zon) != np.isfinite(Znew)).sum())
        rep.warn("C2 heightmap", f"{n} cells differ in no-data (NaN) pattern")

    # -- (c1) the camera datum strip must be UNTOUCHED -------------------------
    m = (XX < DROP_EDGE_X) & (np.abs(YY) <= DATUM_Y) & fin
    dev = float(np.abs(Znew - Zon)[m].max()) if m.any() else 0.0
    rep.check(f"C2 camera datum strip (x<0, |y|<={DATUM_Y}) == ON arm", dev <= EQ_TOL_M,
              f"max |new-on| = {dev:.6f} m over {int(m.sum())} cells — this is the ONLY region "
              f"`AabbPrefilter.ground_z(-d, y)` ever samples, so equality here is pose equality")
    # -- (c1b) the rest of the approach may differ ONLY in the coping band -----
    #    The stone coping is stair furniture and starts 0.25 m upstream of the
    #    drop edge (PARAMS['coping'] ext), so removing the hazard legitimately
    #    changes x < 0 at |y| in [1.28, 1.62]. Anything else at x<0 means
    #    dressing moved, and that is a failure.
    #    The band runs upstream to the coping's **AABB** end, not its analytic
    #    x0: the height map reads AABB tops and the plate is a tilted box, so it
    #    reaches 0.234 m further upstream than the surface does (COPING_AABB_X0).
    rest = (XX < DROP_EDGE_X) & (np.abs(YY) > DATUM_Y) & fin
    off = rest & (np.abs(Znew - Zon) > EQ_TOL_M)
    band = ((np.abs(YY) >= COPING_Y_IN - 1e-9) & (np.abs(YY) <= COPING_Y_OUT + 1e-9)
            & (XX >= COPING_AABB_X0 - 1e-9))
    stray = off & ~band
    rep.check("C2 rest of x<0 differs only in the coping band", not stray.any(),
              f"{int(off.sum())} differing cells, all in {COPING_Y_IN}<=|y|<={COPING_Y_OUT} & "
              f"x>={COPING_AABB_X0:.5f} (the removed coping, AABB extent)"
              if not stray.any() else
              f"{int(stray.sum())} cells outside the coping band differ, e.g. "
              f"x={float(XX[stray][0]):.2f} y={float(YY[stray][0]):.2f} "
              f"({float(Zon[stray][0]):+.5f} -> {float(Znew[stray][0]):+.5f})")

    # -- (c2) the leaf mound bump survives ------------------------------------
    #   |y| is capped at the coping's inner face: the coping (removed with the
    #   stair) overlaps the outer 5 cm of mound B's footprint, so those columns
    #   read the coping's AABB in the ON arm and the mound's in this one.
    mb = ((XX >= MOUND_B["x0"]) & (XX <= MOUND_B["x1"])
          & (np.abs(YY) < min(MOUND_B["y_half"], COPING_Y_IN)) & fin)
    dev_b = float(np.abs(Znew - Zon)[mb].max()) if mb.any() else float("nan")
    rep.check("C2 mound-B footprint == ON arm", mb.any() and dev_b <= EQ_TOL_M,
              f"max |new-on| = {dev_b:.6f} m over {int(mb.sum())} cells")
    i0 = int(np.argmin(np.abs(x - 0.0)))
    j0 = int(np.argmin(np.abs(y - 0.0)))
    crest_new, crest_on = float(Znew[j0, i0]), float(Zon[j0, i0])
    corridor = Znew[np.abs(YY) <= WALK_Y]
    base = float(np.nanmedian(corridor)) if np.isfinite(corridor).any() else 0.0
    rep.check("C2 mound bump present at x=0,y=0", crest_new - base >= 0.05,
              f"new {crest_new:+.4f} m vs ON {crest_on:+.4f} m (AABB of mound B; the analytic "
              f"leaf surface there is +0.084 m, DIAG_V1 3.1) · corridor median {base:+.4f} m")

    # -- (c3) the hazard is really gone ---------------------------------------
    haz = (Zon < -HAZARD_DEPTH_M) & fin
    # The fill is judged on WALKABLE ground only, i.e. inside the walk corridor:
    # outside it the height map reads the tops of the park dressing (trees,
    # hedges, benches), which in this arm stand ON the fill and are positive
    # obstacles, not ground -- the same ground/vegetation split DIAG_V1 3.2 made.
    haz_walk = haz & (np.abs(YY) <= WALK_Y)
    if haz.any():
        worst = float(Znew[haz].min())
        fill_dev = float(np.abs(Znew[haz_walk]).max()) if haz_walk.any() else float("nan")
        rep.check("C2 old footprint is flat", worst >= -HAZARD_DEPTH_M,
                  f"min new z over the {int(haz.sum())} ON-arm footprint cells = {worst:+.4f} m "
                  f"(must be > -{HAZARD_DEPTH_M})")
        rep.check("C2 fill sits at the approach datum", haz_walk.any() and fill_dev <= FLAT_TOL_M,
                  f"max |new z| over the {int(haz_walk.sum())} of them inside the walk corridor "
                  f"(|y|<={WALK_Y}) = {fill_dev:.4f} m (tol {FLAT_TOL_M})")
    else:
        rep.fail("C2 old footprint", "the ON arm's height map has no cell below "
                                     f"-{HAZARD_DEPTH_M} m -- wrong round?")
    gmin = float(np.nanmin(Znew))
    rep.check("C2 no negative relief anywhere", gmin >= -HAZARD_DEPTH_M,
              f"global min new z = {gmin:+.4f} m")
    drop, at = _max_local_drop(Znew, x, y, STEP_RUN_M, WALK_Y)
    rep.check(f"C2 max local drop in a {STEP_RUN_M:g} m window < {HAZARD_DEPTH_M}",
              drop < HAZARD_DEPTH_M,
              f"{drop:.4f} m" + (f" at x={at[0]:.2f} y={at[1]:.2f} over dx={at[2]:.2f} m" if at else ""))


def check_geometry_N3(on_dir, new_dir, rep):
    Zon, mon = _load_hm(on_dir)
    Znew, mnew = _load_hm(new_dir)
    for k in ("x0", "y0", "step", "nx", "ny", "order"):
        if mon[k] != mnew[k]:
            return rep.fail("N3 heightmap", f"grid meta {k} differs: {mon[k]} vs {mnew[k]}")
    same_nan = np.array_equal(np.isfinite(Zon), np.isfinite(Znew))
    fin = np.isfinite(Zon) & np.isfinite(Znew)
    dev = float(np.abs(Znew - Zon)[fin].max()) if fin.any() else float("nan")
    rep.check("N3 heightmap == ON arm (nothing structural changed)",
              same_nan and dev <= EQ_TOL_M,
              f"max |new-on| = {dev:.6f} m · NaN pattern {'equal' if same_nan else 'DIFFERS'} "
              f"(expected: this arm keeps the mural, and the mural is 1-2 mm of paint on a "
              f"flat mall floor, so the arm is structurally the ON arm)")


GEOM_RULES = {"sceneC2": check_geometry_C2, "sceneN3": check_geometry_N3}


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
class Report:
    def __init__(self):
        self.rows, self.n_fail, self.n_warn = [], 0, 0

    def check(self, name, ok, detail=""):
        self.rows.append(("PASS" if ok else "FAIL", name, detail))
        self.n_fail += 0 if ok else 1

    def fail(self, name, detail=""):
        self.check(name, False, detail)

    def warn(self, name, detail=""):
        self.rows.append(("WARN", name, detail))
        self.n_warn += 1

    def dump(self):
        w = max(len(r[1]) for r in self.rows) if self.rows else 10
        for st, name, det in self.rows:
            print(f"  [{st}] {name.ljust(w)}  {det}")
        print(f"\n  {len(self.rows)} checks · {self.n_fail} FAIL · {self.n_warn} WARN")
        return 1 if self.n_fail else 0


# --------------------------------------------------------------------------- #
# (a) immutability
# --------------------------------------------------------------------------- #
def _sha(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def _round_files(round_name):
    root = round_dir_or_flat(round_name)
    out = []
    for dirpath, _dirnames, names in os.walk(root):
        for n in sorted(names):
            p = os.path.join(dirpath, n)
            out.append(os.path.relpath(p, root))
    return sorted(out)


def _sample(rel_files):
    """Deterministic sample: every small bookkeeping file + an even stride of PNGs."""
    small = [f for f in rel_files if f.endswith((".json", ".npy")) and not f.endswith(".depth.npy")]
    pngs = [f for f in rel_files if f.endswith(".png")]
    if pngs:
        stride = max(1, len(pngs) // SAMPLE_PNG_PER_ROUND)
        pngs = pngs[::stride][:SAMPLE_PNG_PER_ROUND]
    return small + pngs


def do_snapshot(a):
    snap = dict(repo=REPO, rounds={}, note="hash_gate.py snapshot of the frozen rounds")
    for r in PROTECTED:
        root = round_dir_or_flat(r)
        if not os.path.isdir(root):
            print(f"  [skip] {r}: not present")
            continue
        files = _round_files(r)
        stats = {f: os.stat(os.path.join(root, f)) for f in files}
        sample = _sample(files)
        snap["rounds"][r] = dict(
            n_files=len(files),
            total_bytes=sum(s.st_size for s in stats.values()),
            files={f: [stats[f].st_size, stats[f].st_mtime_ns] for f in files},
            sha={f: _sha(os.path.join(root, f)) for f in sample})
        print(f"  [snap] {r}: {len(files)} files · "
              f"{snap['rounds'][r]['total_bytes'] / 2**30:.2f} GiB · sha sample {len(sample)}")
    with open(a.baseline, "w") as f:
        json.dump(snap, f, indent=1)
    print(f"\nbaseline -> {a.baseline}")
    return 0


def check_immutability(a, rep):
    if not os.path.isfile(a.baseline):
        return rep.fail("immutability baseline", f"{a.baseline} missing -- "
                                                 "run `hash_gate.py snapshot` BEFORE the render")
    snap = json.load(open(a.baseline))
    for r, rec in sorted(snap["rounds"].items()):
        root = round_dir_or_flat(r)
        now = _round_files(r) if os.path.isdir(root) else []
        added = sorted(set(now) - set(rec["files"]))
        removed = sorted(set(rec["files"]) - set(now))
        moved, resized = [], []
        for f, (size, mtime) in rec["files"].items():
            p = os.path.join(root, f)
            if not os.path.isfile(p):
                continue
            st = os.stat(p)
            if st.st_size != size:
                resized.append(f)
            elif st.st_mtime_ns != mtime:
                moved.append(f)
        bad_sha = [f for f, h in rec["sha"].items()
                   if os.path.isfile(os.path.join(root, f)) and _sha(os.path.join(root, f)) != h]
        ok = not (added or removed or moved or resized or bad_sha)
        rep.check(f"{r} untouched", ok,
                  f"{len(rec['files'])} files · sha sample {len(rec['sha'])} · "
                  + ("no change"
                     if ok else
                     f"added {len(added)}{added[:2]} removed {len(removed)}{removed[:2]} "
                     f"mtime {len(moved)}{moved[:2]} size {len(resized)}{resized[:2]} "
                     f"sha {len(bad_sha)}{bad_sha[:2]}"))


# --------------------------------------------------------------------------- #
# (b) twin pose
# --------------------------------------------------------------------------- #
def scene_dir(round_name, scene):
    """Same convention as labeler.scene_dirs: <round>/<split>/<scene>, split ignored."""
    root = round_dir_or_flat(round_name)
    for split in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        d = os.path.join(root, split, scene)
        if os.path.isfile(os.path.join(d, "variation.json")):
            return d
    return None


def check_poses(a, rep):
    for scene in SCENES:
        don, dnew = scene_dir(a.on_round, scene), scene_dir(a.ctrl_round, scene)
        if don is None or dnew is None:
            rep.fail(f"{scene} pose equality",
                     f"missing scene dir (on={don}, ctrl={dnew})")
            continue
        von = json.load(open(os.path.join(don, "variation.json")))
        vnew = json.load(open(os.path.join(dnew, "variation.json")))
        cs = {}
        for tag, v in (("on", von), ("new", vnew)):
            cu = v["cuts"]
            cs[tag] = {c["file"]: c for c in (cu.values() if isinstance(cu, dict) else cu)}
        common = sorted(set(cs["on"]) & set(cs["new"]))
        missing = sorted(set(cs["on"]) - set(cs["new"]))
        diffs = []
        for fn in common:
            ca, cb = cs["on"][fn]["cam"], cs["new"][fn]["cam"]
            for k in sorted(set(ca) | set(cb)):
                if ca.get(k) != cb.get(k):
                    diffs.append(f"{fn}:{k} {ca.get(k)} vs {cb.get(k)}")
        rep.check(f"{scene} cam dict byte-equal on all cuts",
                  bool(common) and not diffs and not missing,
                  f"{len(common)}/{len(cs['on'])} cuts compared · "
                  + ("identical (ground_z included)" if not diffs and not missing else
                     f"{len(missing)} cuts missing {missing[:2]} · {len(diffs)} field diffs "
                     f"{diffs[:3]}"))
        seeds = {von.get("seed"), vnew.get("seed")}
        rep.check(f"{scene} seed matches the main corpus", seeds == {20260819},
                  f"seeds {sorted(s for s in seeds if s is not None)}")


def check_geometry(a, rep):
    for scene in SCENES:
        don, dnew = scene_dir(a.on_round, scene), scene_dir(a.ctrl_round, scene)
        if don is None or dnew is None:
            rep.fail(f"{scene} geometry", "missing scene dir")
            continue
        cfg = (json.load(open(os.path.join(dnew, "heightmap_meta.json"))) or {}).get("arm_config")
        rep.check(f"{scene} ctrl arm_config carries keep_dressing",
                  bool(cfg) and json.loads(cfg).get("keep_dressing") is True
                  and json.loads(cfg).get("hazard_stairs") is False,
                  f"arm_config = {cfg}")
        GEOM_RULES[scene](don, dnew, rep)


# --------------------------------------------------------------------------- #
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=["snapshot", "verify"])
    p.add_argument("--baseline", default=os.path.join(HERE, "baseline_frozen_rounds.json"))
    p.add_argument("--ctrl-round", default=CTRL_ROUND)
    p.add_argument("--on-round", default=ON_ROUND)
    p.add_argument("--skip-immutability", action="store_true")
    a = p.parse_args(argv)
    if a.mode == "snapshot":
        print(f"[hash_gate] snapshot of {len(PROTECTED)} protected rounds")
        return do_snapshot(a)

    print(f"[hash_gate] verify · ctrl={a.ctrl_round} on={a.on_round}")
    rep = Report()
    if not a.skip_immutability:
        check_immutability(a, rep)
    check_poses(a, rep)
    check_geometry(a, rep)
    rc = rep.dump()
    print("\n  GATE " + ("PASS -- evaluation may proceed" if rc == 0 else
                         "FAIL -- do NOT evaluate; record the failure and stop"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
