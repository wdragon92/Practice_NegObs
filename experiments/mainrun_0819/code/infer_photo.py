#!/usr/bin/env python3
"""Real-world pilot inference: one phone photo -> polar hazard-cell probabilities + overlay PNG.

DAYRUN 0820 Phase 7.  **PROVISIONAL, sim-trained.**  The network never saw a real photograph and
the camera pose is *assumed*, not measured, so every number this tool prints is a pilot signal,
not a measurement.  That is why the assumptions are burned into the output image as a watermark.

What it does
    photo --(EXIF-aware rotate)--> letterbox 512x512 (gray pad) --> ImageNet norm
          --> model_factory U-Net(resnet34)+aux head sized by --grid --> sigmoid
          --> overlay.png = [ photo + translucent ground-wedge projection ] | [ n_bands x n_sectors
              probability grid, make_viz._grid style ]

Camera assumptions (all overridable, all watermarked)
    height  --height   1.65 m eye height above a FLAT ground plane
    pitch   --pitch    0 deg (level camera); negative = looking down
    hfov    --hfov     auto -> EXIF FocalLengthIn35mmFilm if present, else 69 deg
    roll/yaw           0 (the wedge fan is drawn straight ahead)
The projection uses the labeler's own camera convention (`labeling/labeler.py::cam_basis`), so a
wedge drawn here is the same wedge the GT labeler would have used for that pose.

KNOWN train/infer mismatch: `polar_dataset.py` SQUASHES to 512x512 (aspect not preserved); this
tool letterboxes by default because a phone photo's aspect is arbitrary.  `--fit squash`
reproduces the training geometry exactly; the tool prints which one it used.

Run with PYTHONNOUSERSITE=1 (this machine's ~/.local shadows env_seg).  CPU is fine
(CUDA_VISIBLE_DEVICES="" to stay off a busy GPU).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                       # noqa: E402
import numpy as np                                    # noqa: E402
import torch                                          # noqa: E402
from matplotlib.patches import Polygon                 # noqa: E402
from PIL import Image, ImageOps                        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "labeling"))
import gridspec                                        # noqa: E402
import model_factory                                   # noqa: E402
from labeler import cam_basis                          # noqa: E402  (camera convention, verbatim)
from make_viz import _grid                             # noqa: E402  (grid panel style, reused)
from polar_dataset import IMAGENET_MEAN, IMAGENET_STD, IMG_SIZE  # noqa: E402

PAD_RGB = (128, 128, 128)          # mid-gray letterbox pad
DEFAULT_HEIGHT_M = 1.65            # brief: assumed eye height
DEFAULT_HFOV_DEG = 69.0            # brief: fallback horizontal FOV when EXIF is silent
DEFAULT_PITCH_DEG = 0.0
SENSOR_W_MM, SENSOR_H_MM = 36.0, 24.0   # 35 mm-equivalent frame (landscape / portrait)
ARC_SAMPLES = 13                   # points per wedge arc (straight chords look wrong up close)


# --------------------------------------------------------------------------- photo io / EXIF
def read_photo(path):
    """EXIF-aware upright RGB image + the few EXIF fields we can actually use."""
    im = Image.open(path)
    ex = {}
    try:
        raw = im.getexif()
        if raw:
            ex["make"] = str(raw.get(271, "") or "").strip()
            ex["model"] = str(raw.get(272, "") or "").strip()
            ex["orientation"] = raw.get(274)
            sub = {}
            try:
                sub = dict(raw.get_ifd(0x8769) or {})
            except Exception:
                sub = {}
            for tag, name in ((41989, "f35"), (37386, "focal_mm")):
                v = sub.get(tag, raw.get(tag))
                if v is not None:
                    try:
                        ex[name] = float(v)
                    except (TypeError, ValueError):
                        pass
    except Exception as e:                    # a corrupt EXIF block must not kill the run
        ex["exif_error"] = repr(e)
    try:
        im = ImageOps.exif_transpose(im)      # apply orientation, then forget it
    except Exception:
        pass
    return im.convert("RGB"), ex


def resolve_hfov(hfov_arg, exif, w, h):
    """-> (hfov_deg, short source tag for the watermark). Degrades to the 69 deg default."""
    if hfov_arg not in (None, "", "auto"):
        try:
            v = float(hfov_arg)
        except ValueError:
            raise SystemExit(f"[fatal] --hfov must be a number or 'auto', got {hfov_arg!r}")
        if not 5.0 < v < 175.0:
            raise SystemExit(f"[fatal] --hfov {v} deg is not a plausible horizontal FOV")
        return v, "cli"
    f35 = exif.get("f35")
    if f35 and f35 > 0:
        # 35 mm equivalence is defined on the 36x24 frame: the HORIZONTAL side is 36 mm in
        # landscape and 24 mm in portrait (the photo is already EXIF-uprighted here).
        side = SENSOR_W_MM if w >= h else SENSOR_H_MM
        hfov = 2.0 * math.degrees(math.atan(side / (2.0 * f35)))
        return hfov, f"EXIF f35={f35:g}mm"
    return DEFAULT_HFOV_DEG, "default,no EXIF"


# --------------------------------------------------------------------------- preprocessing
def letterbox(img, size=IMG_SIZE, pad=PAD_RGB):
    w, h = img.size
    s = min(size / w, size / h)
    nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
    canvas = Image.new("RGB", (size, size), pad)
    canvas.paste(img.resize((nw, nh), Image.BILINEAR), ((size - nw) // 2, (size - nh) // 2))
    return canvas


def to_tensor(img512):
    a = np.asarray(img512, np.float32) / 255.0
    a = (a - np.array(IMAGENET_MEAN, np.float32)) / np.array(IMAGENET_STD, np.float32)
    return torch.from_numpy(np.ascontiguousarray(a.transpose(2, 0, 1)))[None]


# --------------------------------------------------------------------------- model
def ckpt_n_cells(ck):
    """Cell count a checkpoint was trained on, from whichever field carries it."""
    if not isinstance(ck, dict):
        return None
    for probe in (ck, ck.get("config") or {}):
        if isinstance(probe, dict) and probe.get("n_cells") is not None:
            return int(probe["n_cells"])
    sd = ck.get("state_dict", ck)
    for k, v in (sd.items() if isinstance(sd, dict) else ()):
        if k.endswith("classification_head.3.weight") and hasattr(v, "shape"):
            return int(v.shape[0])            # [n_cells, 512] final Linear
    return None


def load_model(ckpt_path, grid):
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    n = ckpt_n_cells(ck)
    if n is not None and n != grid.n_cells:
        raise SystemExit(
            f"[fatal] checkpoint {os.path.basename(ckpt_path)} was trained on {n} cells but "
            f"--grid says {grid.n_cells} ({grid.version}) -- wrong --grid or wrong --ckpt")
    model = model_factory.build("rgb", encoder_weights=None, classes=grid.n_cells)
    model.load_state_dict(ck["state_dict"] if isinstance(ck, dict) and "state_dict" in ck else ck)
    model.eval()
    return model, (ck.get("config", {}) if isinstance(ck, dict) else {})


# --------------------------------------------------------------------------- ground geometry
def project(pts, height, pitch_deg, hfov_deg, W, H):
    """World points (N,3), eye at (0,0,height), yaw=roll=0 -> (px, py, z_cam).

    Same algebra as `labeler.project`, but parameterised on the photo's own W/H instead of the
    simulator's fixed 1920x1080."""
    r, u, f = cam_basis(0.0, pitch_deg, 0.0)
    fx = (W * 0.5) / math.tan(math.radians(hfov_deg) * 0.5)
    rel = np.asarray(pts, np.float64) - np.array([0.0, 0.0, float(height)])
    zc, xc, yc = rel @ f, rel @ r, rel @ (-u)
    z = np.where(zc > 0.05, zc, np.nan)
    return W * 0.5 + fx * xc / z, H * 0.5 + fx * yc / z, zc


R_MIN_M = 0.10                     # innermost radius drawn (r=0 is the point under the eye)


def wedge_polygons(grid, height, pitch_deg, hfov_deg, W, H):
    """One image-space polygon per cell (None when too little of the wedge is in front).

    Sector s is image-left-to-right (s=0 == 'A' == largest azimuth), exactly as
    `labeler.polar_cells` assigns it: cell = band*n_sectors + (n_sectors-1-k) with k the
    ASCENDING azimuth index.  Vertices behind the image plane are dropped rather than killing
    the whole wedge; a polygon that keeps < 3 vertices is reported as unprojectable."""
    asc = np.asarray(grid.spec["sector_edges_deg"], float)[::-1]     # ascending edges
    ns = grid.n_sectors
    out = []
    for cell in range(grid.n_cells):
        b, s = grid.band_of[cell], grid.sector_of[cell]
        az = np.radians(np.linspace(asc[ns - 1 - s], asc[ns - s], ARC_SAMPLES))
        r_lo, r_hi = grid.band_range(b)
        r_lo = max(r_lo, R_MIN_M)
        ring = np.concatenate([np.stack([r_hi * np.cos(az), r_hi * np.sin(az)], 1),
                               np.stack([r_lo * np.cos(az[::-1]), r_lo * np.sin(az[::-1])], 1)])
        pts = np.concatenate([ring, np.zeros((len(ring), 1))], 1)    # ground plane z = 0
        px, py, _zc = project(pts, height, pitch_deg, hfov_deg, W, H)
        ok = np.isfinite(px) & np.isfinite(py)
        out.append(np.stack([px[ok], py[ok]], 1) if ok.sum() >= 3 else None)
    return out


def frame_coverage(polys, W, H):
    """(n_drawn_inside_frame, n_unprojectable) — how much of the fan the photo actually sees."""
    inside = sum(1 for p in polys if p is not None
                 and p[:, 0].max() > 0 and p[:, 0].min() < W
                 and p[:, 1].max() > 0 and p[:, 1].min() < H)
    return inside, sum(1 for p in polys if p is None)


# --------------------------------------------------------------------------- render
def render(photo, probs, grid, polys, tau, watermark, subtitle, out_png):
    W, H = photo.size
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.0),
                             gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axes[0]
    ax.imshow(np.asarray(photo))
    cmap = matplotlib.colormaps["magma"]
    for cell, poly in enumerate(polys):
        if poly is None:
            continue
        p = float(probs[cell])
        ax.add_patch(Polygon(poly, closed=True, facecolor=cmap(p), alpha=0.42,
                             edgecolor="white", linewidth=0.6, zorder=2))
        cx, cy = poly[:, 0].mean(), poly[:, 1].mean()
        if 0 <= cx < W and 0 <= cy < H:
            ax.text(cx, cy, f"{grid.cell_ids[cell]}\n{p:.2f}", ha="center", va="center",
                    fontsize=6.5, color="white" if p < 0.6 else "black", zorder=3,
                    fontweight="bold" if p >= tau else "normal")
    ax.set_xlim(0, W); ax.set_ylim(H, 0)
    ax.set_axis_off()
    ax.set_title(subtitle, fontsize=8)
    ax.text(0.5, 0.012, watermark, transform=ax.transAxes, ha="center", va="bottom",
            fontsize=6.6, family="monospace", color="white", zorder=4,
            bbox=dict(facecolor="black", alpha=0.6, pad=2.5, edgecolor="none"))
    _grid(axes[1], probs, f"pred prob (tau={tau}) · {grid.version}", tau, False, grid)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(out_png)) or ".", exist_ok=True)
    fig.savefig(out_png, dpi=130)
    plt.close(fig)


# --------------------------------------------------------------------------- main
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--image", required=True, help="photo (jpg/png); EXIF orientation is applied")
    p.add_argument("--ckpt", required=True, help="RGB polar checkpoint, e.g. runs/rgb_s42/best.pt")
    p.add_argument("--out", required=True, help="overlay PNG to write")
    p.add_argument("--height", type=float, default=DEFAULT_HEIGHT_M,
                   help=f"assumed eye height above flat ground, m (default {DEFAULT_HEIGHT_M})")
    p.add_argument("--hfov", default="auto",
                   help=f"'auto' = EXIF FocalLengthIn35mmFilm else {DEFAULT_HFOV_DEG:g} deg, "
                        f"or a number in degrees")
    p.add_argument("--pitch", type=float, default=DEFAULT_PITCH_DEG,
                   help="assumed camera pitch, deg (negative = looking down; default 0)")
    p.add_argument("--tau", type=float, default=0.5, help="display threshold (default 0.5)")
    p.add_argument("--fit", choices=("letterbox", "squash"), default="letterbox",
                   help="letterbox (default, aspect-preserving, gray pad) or squash "
                        "(reproduces the training-time geometry of polar_dataset.py)")
    p.add_argument("--json", default=None, help="optional: also dump probabilities to this json")
    gridspec.add_grid_arg(p)
    a = p.parse_args(argv)

    grid = gridspec.from_args(a)
    photo, exif = read_photo(a.image)
    W, H = photo.size
    hfov, hfov_src = resolve_hfov(a.hfov, exif, W, H)

    x = to_tensor(letterbox(photo) if a.fit == "letterbox"
                  else photo.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR))
    model, cfg = load_model(a.ckpt, grid)
    with torch.no_grad():
        probs = torch.sigmoid(model(x))[0].numpy().astype(np.float64)
    if not np.isfinite(probs).all():
        raise SystemExit("[fatal] non-finite probabilities -- refusing to write an overlay")

    watermark = (f"PROVISIONAL sim-trained | assumed h={a.height:.2f}m "
                 f"hfov={hfov:.1f}deg({hfov_src}) pitch={a.pitch:+.1f}deg | "
                 f"grid {grid.version}")
    cam_note = (f"{exif.get('make','')} {exif.get('model','')}".strip() or "camera unknown")
    polys = wedge_polygons(grid, a.height, a.pitch, hfov, W, H)
    n_in, n_bad = frame_coverage(polys, W, H)
    subtitle = (f"{os.path.basename(a.image)} · {W}x{H} · {cam_note} · fit={a.fit}"
                + ("" if a.fit == "squash" else " (training used SQUASH -- see --fit)")
                + f"\n{n_in}/{grid.n_cells} wedges fall inside the frame at the assumed pose"
                + (f", {n_bad} unprojectable" if n_bad else "")
                + ("  -- near bands sit below the frame for a LEVEL camera; try --pitch -15"
                   if n_in < grid.n_cells else ""))
    render(photo, probs, grid, polys, a.tau, watermark, subtitle, a.out)

    order = np.argsort(-probs)
    top = ", ".join(f"{grid.cell_ids[i]}={probs[i]:.3f}" for i in order[:5])
    print(f"[infer_photo] {grid.summary()}")
    print(f"[infer_photo] image {a.image} {W}x{H} · fit={a.fit} · hfov={hfov:.2f}deg ({hfov_src}) "
          f"· h={a.height:.2f}m · pitch={a.pitch:+.2f}deg")
    print(f"[infer_photo] ckpt {a.ckpt} (trained n_cells={cfg.get('n_cells', 'unknown')}, "
          f"input={cfg.get('input', 'rgb')})")
    print(f"[infer_photo] top cells: {top}")
    print(f"[infer_photo] fired (p>={a.tau}): "
          f"{[grid.cell_ids[i] for i in range(grid.n_cells) if probs[i] >= a.tau] or 'none'}")
    print(f"[infer_photo] max_prob={probs.max():.6f} mean_prob={probs.mean():.6f} "
          f"finite={bool(np.isfinite(probs).all())}")
    print(f"[infer_photo] wrote {a.out}")
    if a.json:
        with open(a.json, "w") as f:
            json.dump(dict(image=os.path.abspath(a.image), ckpt=os.path.abspath(a.ckpt),
                           grid=grid.version, grid_path=grid.path, fit=a.fit, tau=a.tau,
                           height_m=a.height, pitch_deg=a.pitch, hfov_deg=hfov,
                           hfov_source=hfov_src, exif=exif, watermark=watermark,
                           cell_ids=list(grid.cell_ids),
                           probs=[round(float(v), 6) for v in probs]), f, indent=1)
        print(f"[infer_photo] wrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
