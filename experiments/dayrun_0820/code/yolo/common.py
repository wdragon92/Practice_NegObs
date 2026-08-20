"""Shared bootstrap for the YOLOv8n track (DAYRUN_BRIEF_0820 Phase 5).

The ONE job of this module is to make the labeling stack importable and to hand
every script the same camera / grid objects, so no piece of geometry is ever
re-spelled here:

    LB = experiments/mainrun_0819/code/labeling/labeler.py
         -> cam_basis, focal_px, project, unproject, polar_cells,
            load_heightmap, align_to, step_gate, connected_components, _outward
    GS = experiments/mainrun_0819/code/gridspec.py
         -> Grid (cell ids, band_of, n_cells)

Nothing in this directory may reimplement a projection, an unprojection, a
sector/band test or a heightmap footprint.  If a formula is needed, it is
imported from LB.

Run everything with PYTHONNOUSERSITE=1 and (while the render owns the GPU)
CUDA_VISIBLE_DEVICES="".
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))                     # .../dayrun_0820/code/yolo
DAYRUN = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))    # .../dayrun_0820
EXPS = os.path.abspath(os.path.join(DAYRUN, os.pardir))               # .../experiments
REPO = os.path.abspath(os.path.join(EXPS, os.pardir))                 # .../Practice_NegObs
MAINRUN_CODE = os.path.join(EXPS, "mainrun_0819", "code")
LABELING = os.path.join(MAINRUN_CODE, "labeling")

for _p in (LABELING, MAINRUN_CODE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gridspec as GS  # noqa: E402
import labeler as LB  # noqa: E402

DEFAULT_GRID = os.path.join(LABELING, "gridspec_v1.json")
"""Phase 5 is a V1 (20-cell) track by decision D19.  gridspec.py's own default is
still V0 so that pre-0820 runs reproduce -- this track overrides it explicitly."""

CLASS_NAME = "hazard_opening"
CLASS_ID = 0


def load_grid(path=None):
    """(Grid object, raw spec dict).  `LB.polar_cells` wants the raw dict, the
    training/eval stack wants the Grid; both must come from the SAME file."""
    p = GS.resolve(path or DEFAULT_GRID)
    g = GS.load(p)
    with open(p) as f:
        spec = json.load(f)
    return g, spec, p


# --------------------------------------------------------------------------- #
# frame identity
# --------------------------------------------------------------------------- #
def split_frame_id(frame_id):
    """'on/scene04/L0__s20260819__0000.png' -> ('on', 'scene04', 'L0__..._0000.png').
    D24 merged corpus: boost file tokens carry '::<round>' -- strip it here so the
    on-disk filename (bare) resolves; the round itself comes from frame['round']."""
    a, s, f = frame_id.split("/", 2)
    return a, s, f.split("::", 1)[0]


def stem_of(frame_id):
    """Flat, collision-free stem shared by the mask PNG, the symlinked image and
    the YOLO label txt: '<arm>__<scene>__<file-without-.png>[__<round>]'.
    The '::<round>' suffix (D24) survives into the stem -- boost_h and boost_e
    share bare filenames, so the stem must keep the round to stay collision-free."""
    arm, scene, fn = split_frame_id(frame_id)
    suf = ""
    if "::" in frame_id:
        suf = "__" + frame_id.split("::", 1)[1]
    return f"{arm}__{scene}__{os.path.splitext(fn)[0]}{suf}"


def scene_dir_of(frame):
    """Directory holding the frame's PNG + depth + variation.json + heightmap."""
    return os.path.dirname(frame["rgb"])


def round_dir_of(frame):
    """<dataset root>/<round>  (scene dirs live at <round>/<split>/<scene>)."""
    return os.path.dirname(os.path.dirname(scene_dir_of(frame)))


def twin_round_dir(frame, meta):
    """Absolute path of the OFF-arm round dir twinned with this frame's round.

    Preference order: the manifest's own `meta.rounds` map, then the _on/_off
    filename convention.  footprint v2 is a twin difference, so a wrong answer
    here is a wrong label -- it fails loudly rather than guessing further.
    """
    rd = round_dir_of(frame)
    root, rnd = os.path.split(rd)
    rounds = (meta or {}).get("rounds") or {}
    if rounds.get("on") == rnd and rounds.get("off"):
        return os.path.join(root, rounds["off"])
    if rnd.endswith("_on"):
        return os.path.join(root, rnd[:-3] + "_off")
    raise SystemExit(f"[fatal] cannot find the off-arm twin round for {rnd!r} "
                     f"(manifest meta.rounds={rounds})")


def cuts_of(scene_dir):
    """{file -> cut record} from a scene's variation.json.  The manifest's `cam`
    block drops `eye`, so the full camera always comes from here."""
    v = json.load(open(os.path.join(scene_dir, "variation.json")))
    cu = v["cuts"]
    cu = list(cu.values()) if isinstance(cu, dict) else cu
    return {c["file"]: c for c in cu}


# --------------------------------------------------------------------------- #
# camera helpers -- thin wrappers over LB, no new geometry
# --------------------------------------------------------------------------- #
def pixel_rays(cam, px, py):
    """Continuous pixel coords (full-res 1920x1080) -> unit-ish world ray dirs.

    Exact inverse of `LB.project` (which returns the same continuous coords):
        px = W/2 + fx * xc/zc  ->  xn = (px - W/2)/fx
        py = H/2 + fx * yc/zc  ->  yn = (py - H/2)/fx      (yc = rel . -up)
        dir = xn*right + yn*(-up) + fwd                     (dir . fwd == 1)

    NB the +0.5 that `LB.unproject` adds is a pixel-CENTRE offset for integer
    pixel indices; a bbox edge is already a continuous coordinate, so it is not
    applied here.  Round-tripping project() through pixel_rays() is exact.
    """
    r, u, f = LB.cam_basis(cam["yaw"], cam["pitch"], cam["roll"])
    fx = LB.focal_px(cam["hfov"])
    xn = (np.asarray(px, float) - LB.W_IMG * 0.5) / fx
    yn = (np.asarray(py, float) - LB.H_IMG * 0.5) / fx
    return xn[..., None] * r + yn[..., None] * (-u) + f


def ground_project(cam, eye, ground_z, px, py):
    """Ray from a pixel to the plane z = ground_z.  -> (P (N,3), hit (N,) bool).

    `hit` is False for a ray that does not point downward or that would meet the
    plane behind the camera -- the horizon and everything above it.
    """
    d = pixel_rays(cam, px, py)
    eye = np.asarray(eye, float)
    dz = d[..., 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (float(ground_z) - eye[2]) / dz
    hit = np.isfinite(t) & (dz < -1e-9) & (t > 0)
    P = eye + np.where(hit, t, 0.0)[..., None] * d
    return P, hit


def synth_eye(cam):
    """A camera whose absolute (x, y) is unknown (the manifest's `cam` block has
    no `eye`) can still be ground-projected: every quantity the cell mapping uses
    -- the ray, the plane offset (ground_z - eye_z) = -h_rel, and the azimuth /
    range of P relative to the eye -- depends only on h_rel, yaw, pitch, roll,
    hfov.  So place the eye at the origin of its own ground frame.

    Returns (eye, ground_z) usable with `ground_project` + `LB.polar_cells`.
    """
    return np.array([0.0, 0.0, float(cam["h_rel"])]), 0.0


def cells_of_points(P, eye, yaw, spec):
    """World points (N,3) -> cell ids via LB.polar_cells (-1 = outside the grid)."""
    P = np.atleast_2d(np.asarray(P, float))
    cid, rng = LB.polar_cells(P[:, 0], P[:, 1], np.asarray(eye, float), float(yaw), spec)
    return np.asarray(cid, int), np.asarray(rng, float)
