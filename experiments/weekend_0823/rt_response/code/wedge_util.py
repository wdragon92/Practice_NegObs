"""Image-space rasterisation of the polar grid and of the amodal hazard silhouette.

Uses the CANONICAL camera model (`mainrun_0819/code/labeling/labeler.py`, imported, never
re-derived) and the `common.synth_eye` convention: the manifest's `cam` block carries no
absolute eye, and none is needed — the eye sits at the origin of its own ground frame,
eye = (0, 0, h_rel), ground plane z = 0.
"""
import json
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code/labeling"))
import labeler as LB  # noqa: E402

GRID_PATH = os.path.join(REPO, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")
AMODAL_DIR = os.path.join(REPO, "experiments/dayrun_0820/annotations/amodal")
W, H = LB.W_IMG, LB.H_IMG
ARC = 25

GRID = json.load(open(GRID_PATH))
_BB = None


def bboxes():
    global _BB
    if _BB is None:
        _BB = json.load(open(os.path.join(AMODAL_DIR, "bboxes.json")))["frames"]
    return _BB


def wedge_mask(cells, cam, grid=None):
    """Binary (H, W) mask of the ground wedges of `cells` under this frame's camera."""
    grid = grid or GRID
    eye = np.array([0.0, 0.0, float(cam["h_rel"])])
    yaw = float(cam["yaw"])
    camd = {"yaw": yaw, "pitch": float(cam["pitch"]), "roll": float(cam["roll"]),
            "hfov": float(cam["hfov"])}
    asc = np.asarray(grid["sector_edges_deg"], float)[::-1]
    ns = grid["n_sectors"]
    edges = np.asarray(grid["band_edges_m"], float)
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    drew = 0
    for c in cells:
        b, s = c // ns, c % ns
        az = np.radians(np.linspace(asc[ns - 1 - s], asc[ns - s], ARC) + yaw)
        r_lo, r_hi = max(edges[b], 0.10), edges[b + 1]
        ring = np.concatenate([
            np.stack([r_hi * np.cos(az), r_hi * np.sin(az)], 1),
            np.stack([r_lo * np.cos(az[::-1]), r_lo * np.sin(az[::-1])], 1)])
        pts = np.concatenate([ring, np.zeros((len(ring), 1))], 1)
        px, py, zc, _ = LB.project(pts, eye, camd)
        ok = zc > 0.05
        if ok.sum() < 3:
            continue
        dr.polygon([(float(x), float(y)) for x, y in zip(px[ok], py[ok])], fill=255)
        drew += 1
    return np.asarray(img) > 0, drew


def amodal_mask(frame_id):
    """The prism silhouette projected ignoring occlusion — where the hazard WOULD be."""
    name = bboxes().get(frame_id, {}).get("mask")
    if not name:
        return np.zeros((H, W), bool)
    p = os.path.join(AMODAL_DIR, name)
    if not os.path.exists(p):
        return np.zeros((H, W), bool)
    return np.asarray(Image.open(p).convert("L").resize((W, H), Image.NEAREST)) > 0
