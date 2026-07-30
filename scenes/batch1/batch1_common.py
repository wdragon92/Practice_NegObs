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
  [3] det_rng / jit_scalar / jit_tint — deterministic variation seeded by a
      coordinate hash (v5.1 §3, §4 material tint jitter). Same coordinate ->
      always the same value, so the scene does not shift between reruns and
      re-renders.
      **jit_yaw and jit_pos are RETIRED** in W3 CB-3 (J-3 / J-4 abolished,
      `[ruled 07-30]`, spec §1.2 / §10.1). They still exist, and are inert, so
      that the last call sites outside this work package keep importing; see
      `JIT_LEGACY_CALLS` for when they can be deleted outright.

Basis: Docs/surveys/batch1_geophysics_realism_survey.md §4, §6
       Docs/audit_v4/user_feedback_v5_1.md global conventions §2, §3, §4
       Docs/briefs/w3_execution_spec_v1.md §1.2 · §3.1 C6 · §10.1 (W3)

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

# ---------------------------------------------------------------------------
# [0b] C6 asset flip — **PREPARED, NOT ADOPTED** (spec §1.8 "prepare" posture)
#
# Spec §3.1 row C6 flips the bollard to an asset, and §4.2 puts the K2 half of
# that flip here. Four independent gates say it may not be *switched on* in
# this window, so what lands is the route and its measurements, with the
# scene-side value unchanged:
#
#   (1) spec §5.3 hard dependency edge — "K4(c) prop templates -> C6 asset swap
#       in K2". K4(c) is WINDOW 2; K2 is WINDOW 1.
#   (2) spec §3.1 C6 gate — "an A/B h0.3 crop (asset vs current) before
#       adoption". No such crop exists; CB-3's own pilots are N3 and C1.
#   (3) `Docs/audit_v4/gt_changes_w3.md` §0-1 — a change to a hazard/collision
#       box may not land before its ledger row exists. Swapping the body
#       changes `build_bollard_v51`'s collider and `bollard_v51_aabbs`, and
#       there is no GT row for it (the ledger is T5's file, not K2's).
#   (4) spec §3.1 C6 residual work — "base plate + anchor cover + impact-
#       absorbing band material" is prop-template work, i.e. K4(c) again. The
#       raw asset also has **no reflective band**, which 별표2 제7호 requires,
#       so adopting it today would be a net compliance loss for batch1.
#
# Measured through `urban_kit` (usd-core, instance proxies expanded) against
# 교통약자법 시행규칙 별표2 제7호 (h 0.80–1.00 m, dia 0.10–0.20 m) `[law]`:
#
#   bollard_01            dia 139.3 mm · bbox h 1002.8 · zmin −182.6 ·
#                         **exposed 820.2 mm at grade** · 2,564 tri · PASS
#   strt_fxd_bollard_05   dia 133.0 mm · bbox h  844.9 · zmin  −53.9 ·
#                         **exposed 791.0 mm at grade** · 2,628 tri · PASS
#   strt_fxd_bollard_03   207.1 x 297.4 x 721.3 mm — non-circular and below the
#                         height floor; the deliberate non-compliance variant
#
# **Correction to carry forward.** The procurement note reads both adopted rows
# as "both in spec". That is true of the bbox and false of the *installed*
# object: `urban_kit` places these at `z_mode="grade"` (local z = 0 is street
# grade), so the exposed height is `zmax`, not the bbox height — and
# `strt_fxd_bollard_05` then stands **791.0 mm, 9.0 mm below the 800 mm
# statutory floor**. It needs `z_lift_m >= 0.009`, which is what
# `bollard_asset_lift()` returns. `bollard_01` clears the floor unaided.
#
# For reference, the batch1 procedural bollard is dia 120 mm x h 900 mm —
# already inside the statutory band, unlike `scene_common.build_bollard`
# (dia 120 x h 750, 6.3 % below the floor, spec §3.1 C6). So this flip buys
# fidelity, not compliance, and nothing breaks by waiting for its gates.
# ---------------------------------------------------------------------------
BOLLARD_STATUTE = dict(h_min=0.80, h_max=1.00, dia_min=0.10, dia_max=0.20)

BOLLARD_ASSET = dict(
    primary="bollard_01",              # dia 139.3 · exposed 820.2 mm
    variant="strt_fxd_bollard_05",     # dia 133.0 · exposed 791.0 mm (needs the lift)
    noncompliant="strt_fxd_bollard_03",  # the measured 부적정 variant, spec §3.1 C6
)


def bollard_asset_lift(asset_id):
    """Extra z lift, in metres, that brings an asset bollard's **exposed**
    height up to the 800 mm statutory floor. 0.0 when it already clears.

    Raises `urban_kit.UrbanAssetError` if the id is unusable, so a caller that
    wires an asset can never end up silently building nothing.
    """
    import urban_kit as uk
    s = uk.spec(asset_id)
    return max(0.0, float(BOLLARD_STATUTE["h_min"]) - float(s.exposed_h))


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


def _build_bollard_asset(stage, prefix, cx, cy, base_z, asset_id,
                         front_dir, tactile, mtl_tactile, spec_over):
    """[C6, PREPARED — see the §0b block] Asset body + our own tactile pad.

    Kept out of `build_bollard_v51`'s body so the procedural path stays exactly
    the code it was before CB-3. No call site reaches this yet.
    """
    import urban_kit as uk
    from pxr import UsdGeom

    UsdGeom.Xform.Define(stage, prefix)
    uk.add_urban_asset(stage, prefix + "/Body", asset_id,
                       pos_m=(float(cx), float(cy), float(base_z)),
                       yaw_deg=0.0, z_mode="grade",
                       z_lift_m=bollard_asset_lift(asset_id),
                       instanceable=True)
    out = dict(body=stage.GetPrimAtPath(prefix + "/Body"), band=None, tactile=None)
    # The reflective band and the base plate / anchor cover are residual
    # procedural work owned by K4(c) (spec §3.1 C6). They are deliberately NOT
    # faked here: a band drawn at the procedural radius would not sit on this
    # body, and shipping the asset without one is a 별표2 제7호 miss that the
    # adoption gate has to see.
    if tactile:
        S = dict(BOLLARD_V51)
        if spec_over:
            S.update(spec_over)
        s = uk.spec(asset_id)
        r = 0.5 * max(float(s.size_m[0]), float(s.size_m[1]))
        fx, fy = _norm_front(front_dir)
        d, w = float(S["tactile_depth"]), float(S["tactile_width"])
        if fx != 0.0:
            xs = sorted((cx + fx * r, cx + fx * (r + d)))
            ys = (cy - w / 2.0, cy + w / 2.0)
        else:
            xs = (cx - w / 2.0, cx + w / 2.0)
            ys = sorted((cy + fy * r, cy + fy * (r + d)))
        if mtl_tactile is None:
            mtl_tactile = tactile_mtl(stage, prefix + "/MtlTactile")
        out["tactile"] = sc.build_tactile(stage, prefix + "/Tactile",
                                          xs[0], xs[1], ys[0], ys[1],
                                          mtl_tactile, z=float(base_z))
    return out


def build_bollard_v51(stage, prefix, cx, cy, base_z, yaw_todo_none=None,
                      mtl_body=None, mtl_band=None, mtl_tactile=None,
                      front_dir=(1.0, 0.0), radius=None, height=None,
                      tactile=True, band=True, spec=None, asset=None):
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
      asset        : **PREPARED, default off.** A `urban_kit` id
                     (`BOLLARD_ASSET["primary"]` / `["variant"]`) routes the
                     body to the procured asset instead of the cylinder. Do
                     not switch it on: the four gates in the §0b block, above,
                     all have to clear first — chiefly K4(c) and a GT row.

    Returns: dict(body=..., band=..., tactile=...) of prims (None if absent).
    """
    from pxr import UsdGeom

    if asset:
        return _build_bollard_asset(stage, prefix, cx, cy, base_z, asset,
                                    front_dir, tactile, mtl_tactile, spec)

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
                      radius=None, height=None, tactile=True, spec=None,
                      asset=None):
    """AABB list for verification -> [(name, xa, xb, ya, yb, z_top), ...].
    Follows the 5-tuple convention that a scene's dressing_aabbs()/dresscheck()
    can consume as-is. The tactile pad uses z_top = base_z + 0.004
    (effectively flush).

    `asset` mirrors `build_bollard_v51`'s prepared C6 route and must be passed
    wherever that one is, or the check would measure a body the scene no longer
    builds — the exact class of registry/geometry divergence spec §1.2 J-7 is
    about. Default off; see the §0b block."""
    S = dict(BOLLARD_V51)
    if spec:
        S.update(spec)
    r = float(S["radius"] if radius is None else radius)
    h = float(S["height"] if height is None else height)
    rb = r + float(S["band_proud"])
    if asset:
        import urban_kit as uk
        s = uk.spec(asset)
        r = 0.5 * max(float(s.size_m[0]), float(s.size_m[1]))
        rb = r
        h = float(s.exposed_h) + bollard_asset_lift(asset)
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
#
# [W3 · CB-3] **J-3 / J-4 are abolished** (`[ruled 07-30]`, spec §1.2, §10.1
#   rows 3 and 4). `jit_yaw` and `jit_pos` are now inert: they return the
#   anchor bearing and (0, 0). `jit_scalar` and `jit_tint` are NOT in the
#   abolition inventory and are untouched (§10.1 lists only :248 and :256;
#   `jit_tint` is exempt by spec §12-15).
#
#   Why the abolition had to be a **behaviour** flip and not a signature
#   default flip: every one of C-2's 24 call sites passes its amplitude
#   explicitly (`amp=0.12 .. 0.22`, `lo=3.0, hi=5.0 / 8.0`) `[measured]`, so
#   changing `lo`/`hi`/`amp` defaults alone would have changed **nothing** at
#   any call site. The defaults are flipped to zero as well, so that the
#   declared default and the actual behaviour agree.
#
#   The replacement is structural, not "delete and hope" (spec §10.1): an
#   object takes the bearing of the thing it belongs to (kerb line, planter
#   cap face, platform edge) and varies by size, model and interval — never by
#   angle. For batch1 those bearings are the axis set {0, 90, 180, 270}, which
#   is what the surviving `base=` argument already carried.
# ===========================================================================
JITTER_ABOLISHED = True          # J-3 / J-4, spec §1.2 [ruled 07-30]

# Residual `bc.jit_yaw` / `bc.jit_pos` call sites, counted per process. CB-3
# removed the 19 sites in the files it owns; the last 5 belong to other work
# packages (sceneC2 x4 -> S3/CB-2, sceneN5 x1 -> S4). This counter is what
# tells those owners the shim is still load-bearing — when a full 33-scene
# assembly reports zero, the two functions can be deleted outright.
JIT_LEGACY_CALLS = dict(jit_yaw=0, jit_pos=0)
_JIT_WARNED = set()


def _jit_retired(fn, replacement):
    """Count an inert legacy call and say so once per process."""
    JIT_LEGACY_CALLS[fn] = JIT_LEGACY_CALLS.get(fn, 0) + 1
    if fn in _JIT_WARNED:
        return
    _JIT_WARNED.add(fn)
    print("[batch1_common] `%s` is abolished (J-3/J-4, spec §1.2 [ruled 07-30]) "
          "and now returns %s. Remove the call site." % (fn, replacement))


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


def jit_yaw(cx, cy, tag="", lo=0.0, hi=0.0, base=0.0):
    """**RETIRED (J-3, spec §1.2 / §10.1 row 3) — returns `base` unchanged.**

    Was: yaw jitter of |delta| in [lo, hi] degrees with a random sign, to break
    up axis-parallel placement. The supervisor abolished it on 2026-07-30:
    decorative angular wobble is not what makes a real Korean streetscape look
    irregular, and it defeats the alignment the placement linter checks
    (LINT-7). `lo`, `hi` and `cx`/`cy`/`tag` are accepted and ignored so the
    last few call sites outside this work package keep importing cleanly.

    `base` is the bearing of the anchor the object belongs to, which is the
    replacement rule — so returning it is the correct behaviour, not a stub.
    """
    _jit_retired("jit_yaw", "the anchor bearing `base`")
    return float(base)


def jit_pos(cx, cy, tag="", amp=0.0):
    """**RETIRED (J-4, spec §1.2 / §10.1 row 4) — returns (0.0, 0.0).**

    Was: isotropic positional jitter of |d| <= `amp` metres to break up even
    spacing. Abolished with J-3: spacing irregularity in a real frame comes
    from a cause (a tree pit, a manhole, a doorway), so it belongs in the
    scene's own interval table, not in a coordinate hash. `amp` is accepted
    and ignored.

    Returning zero restores each prop to its nominal PARAMS coordinate. Every
    batch1 call site sized its amplitude to stay *inside* an existing
    clearance (sceneC1:809 "does not eat into the existing clearance (0.22 m)",
    sceneD4:646 "|y| = 7.40 +- 0.12 -> clearance kept", sceneD2:289 "3.9 m
    clearance ... overwhelmingly larger than the jitter width"), so collapsing
    the offset to zero can only widen a clearance, never narrow one.
    """
    _jit_retired("jit_pos", "(0.0, 0.0)")
    return 0.0, 0.0


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
