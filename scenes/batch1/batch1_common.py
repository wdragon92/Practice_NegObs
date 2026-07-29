# -*- coding: utf-8 -*-
"""
batch1_common.py — shared layer used only by NegObs batch1 (12 scenes)
(ctx2 realism correction)

Purpose: collect the realism helpers that only batch1 scenes use.
       **scene_common.py must never be modified here** (avoids file-ownership
       conflicts with the main 21-scene team). Anything worth sharing later
       gets promoted into scene_common once the leads agree.

Contents:
  [1] build_bollard_v51 — bollard per the Act on Promotion of Transportation
      Convenience for the Mobility Impaired, enforcement rule table 2
      (h0.90, dia 0.12 + white reflective band near the top + 0.3 m tactile
      paving at the front). The 1.5 m spacing is guaranteed by the caller
      (scene PARAMS).
      - The existing sc.build_bollard is **not replaced** (main scenes keep
        using it).
  [2] bollard_v51_aabbs — AABB list for verifying the above bollard
      (shadow / burial checks).
  [3] det_rng / jit_yaw / jit_pos / jit_tint — deterministic jitter seeded by
      a coordinate hash (v5.1 §3 layout irregularity, §4 material tint
      jitter). Same coordinate -> always the same value, so the scene does not
      shift between reruns and re-renders.

Basis: Docs/surveys/batch1_geophysics_realism_survey.md §4, §6
       Docs/audit_v4/user_feedback_v5_1.md global conventions §2, §3, §4

Coordinates: Z-up, metres. No function needs Isaac (pure computation) — except
build_* which needs pxr.
"""

import math
import random as _random

import scene_common as sc


# ===========================================================================
# [0] Bollard v5.1 spec constants (enforcement rule, table 2)
#     height 0.8~1.0 m / diameter 0.1~0.2 m / spacing around 1.5 m / bright
#     reflective band / 0.3 m tactile paving at the front. Values below take
#     the midpoint of each band.
# ===========================================================================
BOLLARD_V51 = dict(
    radius=0.06,          # dia 0.12 (near the spec's 0.10~0.20 lower bound — stainless practice)
    height=0.90,          # middle of the spec's 0.80~1.00
    band_z0=0.78,         # reflective band, bottom edge (upper part of the post)
    band_z1=0.86,         # reflective band, top edge
    band_proud=0.002,     # body radius + 2 mm (band juts out slightly)
    tactile_depth=0.30,   # tactile pad depth (toward the front) — the spec's "0.3 m at front"
    tactile_width=0.40,   # pad width (lateral)
    spacing=1.5,          # spacing around 1.5 m (upheld by the caller's layout)
)

# Default material colours (used only when the scene passes no mtl)
_BODY_RGB = (0.78, 0.80, 0.83)      # brushed stainless
_BAND_RGB = (0.88, 0.88, 0.86)      # bright white reflective band — small area, so allowed
_TACT_RGB = (0.80, 0.66, 0.14)      # tactile paving yellow — fallback only, if texture absent
# [W2 · ground_kit §12.5-3] Tactile paving was authored as a FLAT constant
# colour, so the 36 statutory dots cast no shading at all and the batch1 pads
# read as 0.003 % of frame (55 px) — "breaks the convention AND is invisible".
# The `tactile_yellow_diff/nor` pair has been registered in `scene_common.TEX`
# all along and was simply never bound. Wire it here; the role name stays
# `tactile` / the files stay `tactile_yellow_*` because ground_kit and the
# vegetation agent both address them by that name.
#   texture [measured — assets/veg_manifest_w2.json]: 1024 px, 36 dots (6x6),
#   pitch 50.0 mm, first-column centre 26.4 mm, linear albedo 0.4504
#   (under the 0.55 clamp of ground_kit §12.5-4, so no extra tint is applied).
#   [W2-C · B7 approved 2026-07-29] Dot diameter 38.1 -> **25 mm nominal**
#   (area-equivalent 25.7 measured). The spec table fixes count / pitch /
#   height only; 38.1 was 1.5~1.7x the common 22~25 mm base and pushed the
#   dot-area share to 45.9 %, working AGAINST §12.5-4's luminance-step goal.
#   Now 20.8 %. Source constant lives in the generator, not here:
#   `assets/scene01/download_scene01_assets.py::TACTILE_DOT_D_MM`.
#   Geometry (relief height 6 mm) is untouched either way.
_TACT_TILE_M = 0.30                 # one statutory pad = 0.30 x 0.30 m
_TACT_ROUGH = 0.70


def tactile_mtl(stage, path, scale_m=None):
    """Tactile-paving material for batch1 call sites.

    Thin alias over `scene_common.tactile_pbr` so there is exactly ONE place
    that decides how tactile paving is shaded. Path token stays `...Tactile`,
    which `_look_spec` maps to class `paint` (inviolable: OmniPBR, no MDL
    promotion, no detail normal, bevel 0).
    """
    return sc.tactile_pbr(stage, path,
                          _TACT_TILE_M if scale_m is None else scale_m,
                          roughness=_TACT_ROUGH)


def _norm_front(front_dir):
    """Normalize front_dir to an axis-aligned unit vector. (+-1,0)/(0,+-1) is
    expected, but an arbitrary vector is snapped to its dominant axis (the
    tactile pad is an axis-aligned box)."""
    fx, fy = float(front_dir[0]), float(front_dir[1])
    if abs(fx) >= abs(fy):
        return (1.0 if fx >= 0.0 else -1.0), 0.0
    return 0.0, (1.0 if fy >= 0.0 else -1.0)


def build_bollard_v51(stage, prefix, cx, cy, base_z, yaw_todo_none=None,
                      mtl_body=None, mtl_band=None, mtl_tactile=None,
                      front_dir=(1.0, 0.0), radius=None, height=None,
                      tactile=True, band=True, spec=None):
    """[v5.1 spec] One functional-furniture bollard.

      prefix       : prim group path (/Body, /Band, /Tactile created under it)
      cx, cy       : centre coordinates in plan
      base_z       : z of the mounting surface (underside of the post)
      yaw_todo_none: reserved (meaningless for a cylinder of revolution). Kept
                     as a positional arg for call-site readability.
      mtl_body/band/tactile : if None, default materials are created under prefix
      front_dir    : the **front** direction the tactile pad faces.
                     (+-1,0) or (0,+-1). At a sidewalk-roadway boundary, point
                     it at the **sidewalk side** (pedestrian guidance).
      radius/height: if None, the BOLLARD_V51 spec values
      tactile/band : individual toggles (scenes turn them off when a grazing
                     view risks occlusion)
      spec         : optional dict overriding BOLLARD_V51

    Returns: dict(body=..., band=..., tactile=...) of prims (None if absent).
    """
    from pxr import UsdGeom

    S = dict(BOLLARD_V51)
    if spec:
        S.update(spec)
    r = float(S["radius"] if radius is None else radius)
    h = float(S["height"] if height is None else height)
    cx, cy, base_z = float(cx), float(cy), float(base_z)

    UsdGeom.Xform.Define(stage, prefix)

    if mtl_body is None:
        mtl_body = sc.make_pbr(stage, prefix + "/MtlBody",
                               diffuse_color=_BODY_RGB,
                               metallic=0.85, roughness_const=0.34)
    if mtl_band is None and band:
        mtl_band = sc.make_pbr(stage, prefix + "/MtlBand",
                               diffuse_color=_BAND_RGB,
                               metallic=0.0, roughness_const=0.30)
    if mtl_tactile is None and tactile:
        mtl_tactile = tactile_mtl(stage, prefix + "/MtlTactile")

    out = dict(body=None, band=None, tactile=None)

    # -- body: cylinder of r and h, underside at base_z --
    out["body"] = sc.add_cylinder(stage, prefix + "/Body",
                                  (cx, cy, base_z + h / 2.0), r, h,
                                  mtl_body, collider=True)

    # -- upper reflective band: z base_z+0.78 .. +0.86 (upper part at h0.9), r+2 mm --
    if band:
        z0 = base_z + float(S["band_z0"]) * (h / 0.90)
        z1 = base_z + float(S["band_z1"]) * (h / 0.90)
        out["band"] = sc.add_cylinder(stage, prefix + "/Band",
                                      (cx, cy, (z0 + z1) / 2.0),
                                      r + float(S["band_proud"]), z1 - z0,
                                      mtl_band)

    # -- front tactile pad (depth 0.3 x width 0.4), flush against the body front --
    if tactile:
        fx, fy = _norm_front(front_dir)
        d, w = float(S["tactile_depth"]), float(S["tactile_width"])
        n0 = r                     # near edge: body surface (flush)
        n1 = r + d                 # far edge
        if fx != 0.0:
            x0, x1 = cx + fx * n0, cx + fx * n1
            y0, y1 = cy - w / 2.0, cy + w / 2.0
        else:
            x0, x1 = cx - w / 2.0, cx + w / 2.0
            y0, y1 = cy + fy * n0, cy + fy * n1
        out["tactile"] = sc.build_tactile(stage, prefix + "/Tactile",
                                          min(x0, x1), max(x0, x1),
                                          min(y0, y1), max(y0, y1),
                                          mtl_tactile, z=base_z)
    return out


def bollard_v51_aabbs(name, cx, cy, base_z=0.0, front_dir=(1.0, 0.0),
                      radius=None, height=None, tactile=True, spec=None):
    """AABB list for verification -> [(name, xa, xb, ya, yb, z_top), ...].
    Follows the 5-tuple convention that a scene's dressing_aabbs()/dresscheck()
    can consume as-is. The tactile pad uses z_top = base_z + 0.004
    (effectively flush)."""
    S = dict(BOLLARD_V51)
    if spec:
        S.update(spec)
    r = float(S["radius"] if radius is None else radius)
    h = float(S["height"] if height is None else height)
    rb = r + float(S["band_proud"])
    cx, cy, base_z = float(cx), float(cy), float(base_z)
    out = [(name, cx - rb, cx + rb, cy - rb, cy + rb, base_z + h)]
    if tactile:
        fx, fy = _norm_front(front_dir)
        d, w = float(S["tactile_depth"]), float(S["tactile_width"])
        if fx != 0.0:
            xs = sorted((cx + fx * r, cx + fx * (r + d)))
            ys = (cy - w / 2.0, cy + w / 2.0)
        else:
            xs = (cx - w / 2.0, cx + w / 2.0)
            ys = sorted((cy + fy * r, cy + fy * (r + d)))
        out.append((name + "_Tac", xs[0], xs[1], ys[0], ys[1],
                    base_z + 0.004))
    return out


def bollard_line(x0, y0, x1, y1, spacing=None, include_end=True):
    """Bollard centre coordinates evenly dividing the segment (x0,y0)->(x1,y1)
    as **closely as possible** to `spacing` (default 1.5 m). Actual spacing =
    length/(n-1), i.e. around 1.5 m.
    Returns: [(x, y), ...] (n >= 2)."""
    sp = float(BOLLARD_V51["spacing"] if spacing is None else spacing)
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(round(L / sp)) + 1)
    pts = []
    m = n if include_end else n - 1
    for i in range(m):
        t = i / float(n - 1)
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return pts


# ===========================================================================
# [3] Deterministic jitter (v5.1 §3 layout irregularity, §4 tint jitter)
#     Seeded by a hash of the coordinates (+ tag) -> rerunning the same scene
#     any number of times yields identical results. Uses the same hash
#     constants as build_tree(v2) to keep the style consistent.
# ===========================================================================
def det_rng(*keys):
    """Build a deterministic random.Random from a list of coordinate/string keys."""
    seed = 0x9E3779B9
    for k in keys:
        if isinstance(k, str):
            hk = 0
            for ch in k:
                hk = (hk * 131 + ord(ch)) & 0xFFFFFFFF
        else:
            hk = int(round(float(k) * 100.0)) & 0xFFFFFFFF
        seed = (seed * 73856093) ^ (hk * 19349663)
        seed &= 0xFFFFFFFF
    return _random.Random(seed)


def jit_yaw(cx, cy, tag="", lo=3.0, hi=8.0, base=0.0):
    """Yaw jitter (degrees) to break up axis-parallel placement.
    |delta| in [lo, hi], random sign."""
    r = det_rng(cx, cy, tag, "yaw")
    d = r.uniform(lo, hi) * (1.0 if r.random() < 0.5 else -1.0)
    return float(base) + d


def jit_pos(cx, cy, tag="", amp=0.20):
    """Positional jitter to break up even spacing.
    Returns (dx, dy) with |d| <= amp (isotropic)."""
    r = det_rng(cx, cy, tag, "pos")
    a = r.uniform(0.0, 2.0 * math.pi)
    m = amp * math.sqrt(r.uniform(0.15, 1.0))
    return m * math.cos(a), m * math.sin(a)


def jit_scalar(cx, cy, tag="", lo=-1.0, hi=1.0):
    """Arbitrary scalar jitter (lengths, angles, etc.)."""
    return det_rng(cx, cy, tag, "sc").uniform(float(lo), float(hi))


def jit_tint(rgb, cx, cy, tag="", amp=0.05, cap=None):
    """Per-instance tint jitter of +-amp (default 5%).
    A shared brightness factor of 1+-amp plus a per-channel +-amp/2 makes the
    colours diverge subtly.
    cap: per-channel upper bound. **Default None** — this function is also used
      for make_pbr's `tint` (a texture multiplier, usually 0.8~1.0), so
      clamping unconditionally at 0.8 would wash the colour out. Pass
      cap=0.80 explicitly only when jittering **diffuse_color (albedo)**, to
      honour v5.1 §4 "no new large areas of pure white (>0.8)"."""
    r = det_rng(cx, cy, tag, "tint")
    g = 1.0 + r.uniform(-amp, amp)
    out = []
    for c in rgb:
        v = float(c) * g * (1.0 + r.uniform(-amp / 2.0, amp / 2.0))
        v = max(0.0, v)
        if cap is not None:
            v = min(float(cap), v)
        out.append(v)
    return tuple(out)
