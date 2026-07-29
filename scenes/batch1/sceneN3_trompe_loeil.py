# -*- coding: utf-8 -*-
"""
sceneN3_trompe_loeil.py — NegObs synthetic scene 23: painted floor stairs (Isaac Sim 4.5)

Type    : N3 hard negative — anamorphic trompe-l'oeil · **GT = "no drop" in every pixel**
Spec    : Docs/nanobanana_batch1_geometry_map.md §A sceneN3_trompe_loeil
Look ref: look_refs/n3_trompe_loeil.jpg (pedestrian mall + anamorphic painting of a descending stair)
Shared  : scene_common.py (add_box / dressing·lighting harness) · scene14 illusion-scene precedent

Hazard (counter-example): a "descending stair well" is painted on the paving in the
           middle of a pedestrian mall. The geometry is entirely planar (1 mm thick
           paint sheets) — there is **no drop anywhere**.
           The strongest contrast pair with the T1 campus stairs (positive).
Cues     : ① the paving joints run straight through the painted area (a real opening would break them)
           ② the fake "dark areas" are paint, so their roughness matches the paving and the specular stays
           ③ no real cast shadow — conversely **the real streetlight pole shadow crosses the painting**
           ④ leaving the design viewpoint (a single point) collapses the perspective (off_axis shot)

── Anamorphic construction (core maths) ─────────────────────────────────
Virtual object = **a sunken stair well**: near rim x=0 (z=0) → floor z=-Dp (length floor_len) →
n steps rising in +X → far rim z=0 (at x=x_f). From the design viewpoint E=(eye_x, 0, eye_h),
every point P=(xv, yv, z) of the virtual surface is projected onto the ground z=0:
      s(z) = eye_h / (eye_h - z)              (0 < s <= 1)
      Q_x  = eye_x + s * (xv - eye_x) ,  Q_y = s * yv
The near and far rims have z=0 → s=1 → they map onto themselves ⇒ **the painted footprint fills
the stair-well opening [0, x_f] × [-W/2, W/2]** exactly (no gaps, no overlaps).
Both side walls (yv=±W/2) project outside |Q_y| = s*W/2, as trapezoidal wall bands.
The band order (tread/riser/wall) is **monotone** because s and xv increase together — no overlap.
Bands projecting to Q_x <= 0 are hidden behind the near rim (grazing occlusion) and are therefore
not drawn: this reproduces the physics of a low viewpoint (h 0.9) not seeing the lower part of
the stair well.

Defaults (eye (-2, 0.9) · n 13 · riser 0.15 · tread 0.30 · floor 2.4 · W 3.0):
      footprint 6.30 × 3.00 m (matches the ~3×6 m reference) · visible steps 10/13
      per-step perspective reduction factor k ≈ 0.75~0.87 (spec band k≈0.88)
The design viewpoint is the same eye as grid_views preset_h0.9_d2 — the illusion holds in a
standard preset and collapses toward d5/d10/h1.8 (intended data diversity).
Spec deviation: the spec placed the design viewpoint at (x=-5, h=0.9), but it was **moved to
(x=-2, h=0.9)**. Reason — from a low viewpoint the lower part of the stair well is hidden by the
near rim (grazing occlusion), leaving no surface to paint.
Visible steps and reduction factors for the same virtual stair at different design viewpoints:
      eye_x  -2.0 → 10/13 steps, k 0.750~0.867   ← adopted (matches spec k≈0.88)
      eye_x  -3.0 →  8/13 steps, k 0.750~0.846
      eye_x  -5.0 →  6/13 steps, k 0.483~0.818   (sparse painted content · k out of band)
      eye_x -10.0 →  4/13 steps, k 0.177~0.778
Keeping x=-5 would require unrealistically shallow riser/tread (riser around 5 cm), so moving to
d2 was chosen while preserving the property "one of the standard h0.9 presets".
────────────────────────────────────────────────────────────────────────

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN3_trompe_loeil.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneN3_trompe_loeil.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneN3_trompe_loeil.py
Geometry/dressing check:  NEGOBS_GEOCHECK=1 python3 sceneN3_trompe_loeil.py (no Isaac needed)

Coordinates: Z-up, m, travel axis +X, painting (fake drop edge) starts at x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - the standard 7 keys.
#     No drop exists here, so hazard_stairs is redefined as the **feature (painting) toggle**.
# ===========================================================================
SCENE_CONFIG = {
    # False -> painting removed, a pure flat mall (control). The only exception among geometry toggles.
    "hazard_stairs":      True,
    "cue_railing":        False,  # a painting has no railing - key reserved only
    "cue_tactile":        False,  # not conventional here - key reserved only
    "cue_material_break": True,   # True -> the painting tint contrasts clearly with the paving
                                  # False -> close to the paving tone (weakened-illusion control)
    "cue_nosing":         True,   # a bright nosing line at the front of each tread (painted nosing)
    "cue_sign":           False,  # [optional] not implemented - key reserved only
    "cue_scene_dressing": True,   # streetlight (real-shadow cue)·planters·benches·bollards·buildings
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- virtual stair well (the object the painting depicts) + design viewpoint ---
    illusion=dict(eye_x=-2.0, eye_h=0.9,         # the single design viewpoint (= preset_h0.9_d2)
                  nsteps=13, riser=0.15, tread=0.30,
                  floor_len=2.4,                  # floor length before the first riser
                  width=3.0,                      # opening width (painting footprint width)
                  x_rim=0.0),                     # near rim = painting start x
    # --- paint layer z convention (proud) ---
    #   paint 0.001 < block joint 0.0015 < border line 0.002 < paving joint 0.003
    #   (every layer at least 0.5 mm apart - no coplanar Z-fighting)
    paint=dict(z=0.001, border_z=0.002, border_w=0.06,
               border=True, nosing_w=0.035),
    # --- "stone block joints" inside the painting [v2] : reproduces the reference block coursing ---
    #   tread_frac : block boundaries on the treads and floor (fraction of half width, +-0 is centre)
    #   wall_frac  : side-wall course joints (fraction from inner boundary 0 to opening boundary 1)
    blocks=dict(enable=True, z=0.0015, w=0.020,
                tread_frac=(-0.42, 0.02, 0.46), wall_frac=(0.45,)),
    # --- paving ---
    plaza=dict(x0=-60.0, x1=100.0, y0=-60.0, y1=60.0, z_top=0.0, thick=0.6),

    # ═══ [W2 ground_kit] P1 plaza_granite — spec §5.1 row N3 ═══════════════
    #  two scene-specific prescriptions: (1) **joints run through the painting**, strengthening the cue
    #  (2) **manholes stay outside the painting** (`x <= −1.6`).
    #  (1) is already enforced by the scene (`build_joints()` 1.2 m grid, x −12…24 passes through
    #  the painting x 0…6.3) -> **kit joints 0** (`pave.joint=None`). If the kit laid a
    #  1.8/6.0 grid on the same surface that would be a D6 double grid, and above all the joints
    #  here are a **discriminative cue**, so their period must not wobble.
    #  (2) is guaranteed structurally by cutting the region stock at `x_rim − 1.6`. On top of that,
    #  the B12 invariants `_inv_n3_painting` (surface-element AABB ∩ painting rectangle = ∅) and
    #  `_inv_hidden_illusion` (0 tactile paving · no high-contrast crossing lines) lock it twice.
    #  * the d2 near window (x −1.436…0) is **occupied by the painting** - that is this scene.
    #    So d2's B1 (surface elements >=1) falls short by construction, and that is correct.
    ground=dict(
        region=(-12.0, -4.0, -1.6, 4.0),
        manholes=[(-2.00, 1.00), (-6.00, -1.00)],
        #  patches cover the d5·d10 near windows (W1). |y| <= 0.4 keeps them inside the frame half-width.
        patches=[(-3.80, 0.20), (-8.80, -0.20)],
        gullies=[(-5.00, 3.40), (-10.00, -3.40)],
    ),
    band=dict(y=5.0, width=0.8, proud=0.002, embed=0.06),   # granite edge band
    joint=dict(x0=-12.0, x1=24.0, y0=-7.2, y1=7.2, step=1.2,
               width=0.028, proud=0.003, embed=0.06),        # paving joint grid
    # --- props ---
    #   streetlight: sun az 205 deg -> shadow az 25 deg = (+0.906,+0.423),
    #   length = 4.6/tan(49.79 deg) = 3.90 m -> shadow tip (4.13, -0.95) = inside the painting.
    lamp=dict(cx=0.6, cy=-2.6, pole_r=0.07, pole_h=4.6,
              head=(0.55, 0.22, 0.14)),
    planters=[dict(name="A", cx=-4.5, cy=3.6), dict(name="B", cx=9.0, cy=-3.8),
              dict(name="C", cx=14.0, cy=3.4), dict(name="D", cx=18.5, cy=-3.6)],
    planter=dict(size=2.6, curb_h=0.42, curb_t=0.22, cap_over=0.05,
                 cap_h=0.05, grass_h=0.38),
    # benches - all anchored beside a planter (tree). A stood in open ground (-3.0,-3.4) in ctx2
    #   -> moved 0.3 m to the right of planter A. yaw/position use the v5.1 §3 deterministic jitter.
    benches=[dict(name="A", cx=-2.0, cy=3.5, yaw=0.0),      # 0.3 m beside planter A
             dict(name="B", cx=6.5, cy=-3.6, yaw=0.0),      # 0.3 m beside planter B
             dict(name="C", cx=10.5, cy=3.6, yaw=0.0),      # 1.3 m in front of planter C
             dict(name="D", cx=16.0, cy=3.5, yaw=0.0)],     # 0.2 m beside planter C
    # ── bollards [v5.1 §2 · ctx2] ─────────────────────────────────────────
    #   old: 2 posts at (−6, +-1.4) h0.75 - right beside the walk axis (the painting centreline),
    #   they could enter the design viewpoint's view, and had no spec, spacing, reflective band or dot paving.
    #   new: one row across the **pedestrian-only street entrance of the mall** (x=−6). Spec h0.90·φ0.12·
    #   spacing 1.5 m. The central 4.8 m is left open as a **fire-engine access lane** (the Building
    #   Act sets a 4 m minimum width for firefighting zones) - real pedestrian-street practice.
    #   * painting preserved: every bollard is at |y| >= 2.4 · x = −6 -> outside the painting
    #     footprint (x 0..6.30 · |y| <= 1.50) and **outside the forward view** of the design eye (E=−2.0).
    #     (they sit −X behind the design viewpoint, so they can never appear in the design_eye shot.)
    bollard_rows=[dict(name="N", x=-6.0, y0=2.4, y1=8.4),
                  dict(name="S", x=-6.0, y0=-2.4, y1=-8.4)],
    bollard=dict(r=0.06, h=0.90, spacing=1.5, front=(-1.0, 0.0)),
    # ── mall context [v2] : shopfront band (awning + shop window + fascia sign band) ──
    #   a podium wall is added to the ground floor of buildings L/R, with bays arrayed across its front.
    #   the podium (y 9.55~10.05, z 0~3.6) **fully encloses** the ground-floor windows of
    #   build_building (y 9.98~10.01, z 0.60~2.40), so no coplanar Z-fighting occurs.
    #   podium_embed 0.05 = the podium is pushed into the shell, **removing coplanar contact**.
    #   podium_h 3.45 < the 2nd-floor window sill 3.60 -> no top-face contact with the windows either.
    shop=dict(x0=-10.0, x1=30.0, bay=4.0, gap=0.55,
              podium_t=0.50, podium_h=3.45, podium_embed=0.05,
              glass_z0=0.45, glass_z1=2.50, glass_t=0.10, glass_proud=0.05,
              awn_z=2.66, awn_proj=1.30, awn_t=0.12,
              fascia_z0=2.78, fascia_z1=3.36, fascia_t=0.18, fascia_proud=0.10),
    shop_facades=[dict(name="L", y=10.0, dir=-1.0),
                  dict(name="R", y=-10.0, dir=1.0)],
    # freestanding sign (1 info sign) - mall usage guidance. Faces -X (square to the approach camera).
    #   GT convention: only **info** signs, never a "drop warning" (no mislabelling).
    entry_sign=dict(x=7.5, y=4.6, yaw=180.0, w=0.8, h=0.8,
                    pole_h=2.2, pole_r=0.045),
    buildings=dict(
        # retail facades on both sides of the mall + vista block ahead (+X)
        L=dict(x0=-14.0, x1=34.0, y0=10.0, y1=20.0, h=9.0, floors=3,
               axis="y", facade_y=10.0, face_dir=-1.0),
        R=dict(x0=-14.0, x1=34.0, y0=-20.0, y1=-10.0, h=9.0, floors=3,
               axis="y", facade_y=-10.0, face_dir=1.0),
        F=dict(x0=42.0, x1=52.0, y0=-18.0, y1=18.0, h=14.0, floors=4,
               axis="x", facade_x=42.0, face_dir=-1.0),
    ),
    window=dict(w=1.4, h=1.8, inset=0.15, col_step=3.0, margin=2.0),

    material=dict(
        scale=dict(stone_flag=1.2, band_dark=1.0, grass=1.4, plaza_light=1.80),
        grass_tint=(0.55, 0.68, 0.42),
        # ══ paint tints [v2 palette correction · 2026-07-27] ═════════════
        #   why v1 was dropped: it used near-zero-saturation neutral greys (0.40/0.385/0.355 family),
        #     so the render read as a "grey striped abstract pattern" (the user pointed this out).
        #   basis for the correction: reading look_refs/n3_trompe_loeil.jpg —
        #     (1) treads are **warm beige / tan stone** (the warm tone of chalk pastel)
        #     (2) the dark risers and floor are not neutral grey either but **warm brown shade**
        #     (3) the side walls are stone block coursing (warm mid-tone + dark joints)
        #     (4) the painting's outline is a cream chalk border
        #   sRGB perceptual rule: dark areas stay in the 0.02~0.09 band but **keep their hue**
        #     (R:G:B ~ 1.00:0.79:0.59 warm ratio - saturated darks).
        #   every paint keeps roughness = paint_rough (same as the paving) - the "material trap" stays.
        paint_rough=0.55,
        tread_tint=(0.520, 0.450, 0.340),      # warm stone tread (tan beige)
        riser_tint_a=(0.055, 0.043, 0.032),    # warm brown darks, 2 tones (alternating)
        riser_tint_b=(0.088, 0.070, 0.053),
        floor_tint=(0.040, 0.031, 0.023),      # stair well floor (deepest · warm dark)
        wall_tint=(0.240, 0.200, 0.150),       # stone block side wall (warm mid-tone)
        nosing_tint=(0.640, 0.565, 0.440),     # painted nosing (light warm stone)
        border_tint=(0.760, 0.710, 0.600),     # cream chalk line around the painting
        block_tint=(0.130, 0.104, 0.078),      # stone block joint (warm dark hairline)
        # paving reference tone mixed in when contrast is weakened (cue_material_break=False) - warm-matched
        flat_ref=(0.340, 0.315, 0.275),
        flat_mix=0.55,
        joint_color=(0.030, 0.030, 0.032), joint_rough=0.7,
        lamp_color=(0.42, 0.43, 0.45), lamp_metallic=0.6, lamp_rough=0.45,
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        # ─ bollard v5.1 fittings: white reflective band on top (0.08 m² each - not a large area) +
        #   dot tactile paving in front (yellow). The body stays dark grey, as is mall practice.
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        parapet_color=(0.90, 0.90, 0.87), parapet_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        wall_face_tint=(0.86, 0.86, 0.85),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # ── mall context (shopfronts) ──
        podium_tint=(0.90, 0.87, 0.82),
        shopglass_color=(0.055, 0.070, 0.085), shopglass_rough=0.10,
        awning_a=(0.34, 0.10, 0.09), awning_b=(0.10, 0.22, 0.17),
        awning_rough=0.85,
        fascia_a=(0.20, 0.17, 0.14), fascia_b=(0.14, 0.16, 0.21),
        fascia_rough=0.60,
        sign_color=(0.30, 0.30, 0.32), sign_rough=0.50,
    ),

    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET: kept at the default 171.5. Rationale:
    #     sun world az ~ 33.5 + 171.5 = 205 deg -> real shadow az = 25 deg (+X,+Y).
    #     the "fake shading" of the painting assumes the riser faces turned toward the camera
    #     (i.e. facing -X) are dark, which **conflicts** with the real sun (205 deg = WSW).
    #     that conflict is not a defect but a trompe-l'oeil cue - the painting cannot cast its own
    #     shadow, while the real streetlight/planter shadows pass straight over it.
    #     Re-sweepable in the GUI with the [ ] keys (15 deg step). ───
    SUN_AZ_OFFSET=171.5,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN3")

ASSET_ROLES = ["stone_flag", "band_dark", "plaza_light", "grass", "brick_red",
               "sign_info", "hdri", "mdl"]


# ===========================================================================
# [C2] anamorphic projection - pure maths (no stage needed, shared with the SMOKE report)
# ===========================================================================
def project_bands(il):
    """Bands obtained by projecting the visible surfaces of the virtual sunken stair well onto the ground (z=0).

    il: the PARAMS["illusion"] dict.
    returns: [dict(kind, idx, xa, xb, ha, hb, sa, sb, depth_frac), ...]
      kind : "floor" | "riser" | "tread"  (near→far order, xa < xb monotone)
      xa,xb: projected ground x (near/far) ha,hb: half-width |Qy| bounds there
      sa,sb: projection factor s           depth_frac: 0(deepest)~1(rim) depth ratio
    Bands that fold to Q_x<=0 (hidden by the near rim) are dropped, and a straddling band is
    cut at x=0 by linear interpolation — for both riser and tread, s (and therefore the
    half-width) is linear in Q.
    """
    ex, h = float(il["eye_x"]), float(il["eye_h"])
    n = int(il["nsteps"])
    r, t = float(il["riser"]), float(il["tread"])
    Lf, W = float(il["floor_len"]), float(il["width"])
    x_rim = float(il["x_rim"])
    Dp = n * r                                   # stair well depth
    hw = W / 2.0

    def s_of(z):
        return h / (h - z)

    def qx(xv, z):
        return ex + s_of(z) * (xv - ex)

    raw = []
    # (1) floor slab (z=-Dp, x_rim .. x_rim+Lf)
    raw.append(("floor", 0, x_rim, x_rim + Lf, -Dp, -Dp))
    # (2) step i: riser (vertical face) -> tread (horizontal face)
    for i in range(1, n + 1):
        xi = x_rim + Lf + (i - 1) * t
        zb = -Dp + (i - 1) * r
        zt = -Dp + i * r
        raw.append(("riser", i, xi, xi, zb, zt))
        raw.append(("tread", i, xi, xi + t, zt, zt))

    bands = []
    for kind, idx, xva, xvb, za, zb in raw:
        sa, sb = s_of(za), s_of(zb)
        xa, xb = qx(xva, za), qx(xvb, zb)
        ha, hb = sa * hw, sb * hw
        if xb <= x_rim + 1e-9:                   # fully occluded - not drawn
            continue
        if xa < x_rim:                           # straddling band -> cut at x_rim
            u = (x_rim - xa) / (xb - xa)
            ha = ha + (hb - ha) * u
            sa = sa + (sb - sa) * u
            xa = x_rim
        bands.append(dict(kind=kind, idx=idx, xa=xa, xb=xb, ha=ha, hb=hb,
                          sa=sa, sb=sb,
                          depth_frac=(sa + sb) / 2.0))
    return bands


def illusion_summary(il):
    """Summary for SMOKE and docs: footprint · visible step count · per-step reduction factor k."""
    b = project_bands(il)
    x_f = float(il["x_rim"]) + float(il["floor_len"]) \
        + int(il["nsteps"]) * float(il["tread"])
    steps = sorted({d["idx"] for d in b if d["kind"] in ("riser", "tread")})
    dep = []
    for i in steps:
        seg = [d for d in b if d["idx"] == i and d["kind"] in ("riser", "tread")]
        dep.append((i, max(d["xb"] for d in seg) - min(d["xa"] for d in seg)))
    ks = [dep[j][1] / dep[j + 1][1] for j in range(len(dep) - 1)
          if dep[j + 1][1] > 1e-9]
    return dict(bands=b, x_f=x_f, steps=steps, depths=dep,
                k_min=(min(ks) if ks else 0.0), k_max=(max(ks) if ks else 0.0))


# ===========================================================================
# [C3] local builders - the painted stairs (not shared yet: this scene only)
# ===========================================================================
def _paint_quad(stage, path, corners_xy, z, mtl):
    """One planar quad (trapezoid) parallel to the ground. corners_xy is in
    counter-clockwise (CCW) order seen from +Z — normal +Z. Adjacent bands only share
    an edge and never overlap, so no coplanar Z-fighting occurs."""
    from pxr import UsdGeom, UsdShade, Gf
    mesh = UsdGeom.Mesh.Define(stage, path)
    pts = [Gf.Vec3f(float(x), float(y), float(z)) for x, y in corners_xy]
    mesh.CreatePointsAttr(pts)
    mesh.CreateFaceVertexCountsAttr([len(pts)])
    mesh.CreateFaceVertexIndicesAttr(list(range(len(pts))))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mesh.CreateExtentAttr([Gf.Vec3f(min(xs), min(ys), float(z)),
                           Gf.Vec3f(max(xs), max(ys), float(z))])
    # TfToken values are given as plain strings (removes the dependence on token constant names).
    mesh.CreateSubdivisionSchemeAttr("none")     # keep the polygon as is (no subdivision)
    mesh.CreateDoubleSidedAttr(True)             # guard against back-face culling accidents
    mesh.CreateNormalsAttr([Gf.Vec3f(0.0, 0.0, 1.0)] * len(pts))
    mesh.SetNormalsInterpolation("vertex")
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mtl)
    return mesh


def _block_joints(stage, prefix, tag, xa, xb, ha, hb, hw, bk, mtl, inner):
    """Hairlines for the "stone block joints" inside the painting (reproducing the block coursing of the reference).

    With inner=True it lays the block boundaries of the treads and floor (longitudinal
    hairlines at tread_frac of the half width); the side-wall course joints (at wall_frac
    between the inner boundary and the opening boundary) are always laid as well.
    The lines follow the same trapezoidal perspective as the band (half width varying
    ha→hb), so the projection is not broken. z sits 0.5 mm above the paint (0.001) = no Z-fighting.
    """
    z = float(bk["z"])
    w = float(bk["w"]) / 2.0
    n = 0
    if inner:
        for k, f in enumerate(bk["tread_frac"]):
            ya, yb = f * ha, f * hb
            _paint_quad(stage, f"{prefix}/BlkT_{tag}_{k}",
                        [(xa, ya - w), (xb, yb - w), (xb, yb + w), (xa, ya + w)],
                        z, mtl)
            n += 1
    for k, t in enumerate(bk["wall_frac"]):
        for sgn, sd in ((1.0, "N"), (-1.0, "S")):
            ya = sgn * (ha + t * (hw - ha))
            yb = sgn * (hb + t * (hw - hb))
            _paint_quad(stage, f"{prefix}/BlkW{sd}_{tag}_{k}",
                        [(xa, ya - w), (xb, yb - w), (xb, yb + w), (xa, ya + w)],
                        z, mtl)
            n += 1
    return n


def paint_fake_stairs(stage, prefix, il, pa, mtl_of, nosing=True,
                      blocks=None, block_mtl=None):
    """Lays the anamorphic "descending stair" paint array on the ground at z=pa["z"].

    il      : PARAMS["illusion"],  pa: PARAMS["paint"]
    mtl_of  : (kind, idx, depth_frac) -> UsdShade.Material callback
              kind ∈ {"floor","riser","tread","wall","nosing","border"}
    nosing  : if True, cuts pa["nosing_w"] off the front of each tread and paints it in the nosing colour.
    blocks  : PARAMS["blocks"] (adds stone block joint hairlines when enabled), block_mtl required.
    A band = the inner trapezoid (floor/riser/tread) + the left and right side-wall trapezoids, 3 quads.
    Their union covers the opening footprint [x_rim, x_f] × [-W/2, W/2] with no gaps.
    """
    z = float(pa["z"])
    hw = float(il["width"]) / 2.0
    bands = project_bands(il)
    n_prim = 0
    use_blk = bool(blocks and blocks.get("enable") and block_mtl is not None)
    for bi, b in enumerate(bands):
        segs = [(b["xa"], b["xb"], b["ha"], b["hb"], b["kind"])]
        if nosing and b["kind"] == "tread":
            w = min(float(pa["nosing_w"]), (b["xb"] - b["xa"]) * 0.5)
            if w > 1e-4:
                xm = b["xa"] + w
                u = (xm - b["xa"]) / max(b["xb"] - b["xa"], 1e-9)
                hm = b["ha"] + (b["hb"] - b["ha"]) * u
                segs = [(b["xa"], xm, b["ha"], hm, "nosing"),
                        (xm, b["xb"], hm, b["hb"], "tread")]
        for si, (xa, xb, ha, hb, kind) in enumerate(segs):
            tag = f"{bi:02d}_{si}"
            mtl = mtl_of(kind, b["idx"], b["depth_frac"])
            # inner side (stair faces)
            _paint_quad(stage, f"{prefix}/Band_{tag}",
                        [(xa, -ha), (xb, -hb), (xb, hb), (xa, ha)], z, mtl)
            n_prim += 1
            # left/right side-wall trapezoids (inner boundary ~ opening boundary)
            wmtl = mtl_of("wall", b["idx"], b["depth_frac"])
            _paint_quad(stage, f"{prefix}/WallS_{tag}",
                        [(xa, -hw), (xb, -hw), (xb, -hb), (xa, -ha)], z, wmtl)
            _paint_quad(stage, f"{prefix}/WallN_{tag}",
                        [(xa, ha), (xb, hb), (xb, hw), (xa, hw)], z, wmtl)
            n_prim += 2
            if use_blk:
                n_prim += _block_joints(
                    stage, prefix, tag, xa, xb, ha, hb, hw, blocks, block_mtl,
                    inner=(kind in ("tread", "nosing", "floor")))
    return bands, n_prim


# ===========================================================================
# [C4] geometry self-verification report (printed at the SMOKE early exit)
# ===========================================================================
def _geometry_report():
    il = PARAMS["illusion"]
    s = illusion_summary(il)
    pa = PARAMS["paint"]
    Dp = il["nsteps"] * il["riser"]
    D = il["x_rim"] - il["eye_x"]
    i0 = min(s["steps"]) if s["steps"] else 0
    z_seen = -Dp + (i0 - 1) * il["riser"]        # deepest visible face = the perceived drop
    print("-" * 68)
    print("[기하] sceneN3 아나모픽 자기검증")
    print(f"  설계 시점 E=({il['eye_x']:.2f}, 0, {il['eye_h']:.2f})  "
          f"근접 림 x={il['x_rim']:.2f} → D={D:.2f} m")
    print(f"  그레이징 폐색: 림 시선 기울기 h/D = {il['eye_h'] / D:.3f} vs "
          f"계단 상승 기울기 riser/tread = {il['riser'] / il['tread']:.3f} "
          f"→ 첫 가시 단 {i0} (하부 {i0 - 1}단+바닥은 림에 가림)")
    print(f"  지각 낙차(림에서 최심 가시면) = {-z_seen:.2f} m · "
          f"유효성 = 가시 단 {len(s['steps'])} ≥ 3 → "
          f"{'OK' if len(s['steps']) >= 3 else 'FAIL(그릴 면 부족 — floor_len/riser 재조정)'}")
    print(f"  가상 계단정: {il['nsteps']}단 riser {il['riser']:.2f} / "
          f"tread {il['tread']:.2f} · 깊이 {Dp:.2f} · 바닥 {il['floor_len']:.2f} "
          f"· 폭 {il['width']:.2f}")
    print(f"  그림 풋프린트: x [{il['x_rim']:.2f}, {s['x_f']:.2f}] "
          f"({s['x_f'] - il['x_rim']:.2f} m) × 폭 {il['width']:.2f} m "
          f"— 페인트 proud {pa['z']:.4f} m (≤0.001 규약)")
    print(f"  가시 단: {len(s['steps'])}/{il['nsteps']} "
          f"(단 {min(s['steps'])}~{max(s['steps'])}, 하부는 근접 림에 폐색)")
    print(f"  단당 원근 축소 계수 k = {s['k_min']:.3f} ~ {s['k_max']:.3f} "
          f"(사양 k≈0.88 대역)")
    print(f"  {'밴드':>10s} {'x_near':>8s} {'x_far':>8s} {'깊이':>7s} "
          f"{'반폭_n':>7s} {'반폭_f':>7s}")
    for b in s["bands"]:
        print(f"  {b['kind'] + str(b['idx']):>10s} {b['xa']:8.3f} {b['xb']:8.3f} "
              f"{b['xb'] - b['xa']:7.3f} {b['ha']:7.3f} {b['hb']:7.3f}")
    # band monotonicity = proof of no overlap
    xs = [(b["xa"], b["xb"]) for b in s["bands"]]
    mono = all(abs(xs[i][1] - xs[i + 1][0]) < 1e-9 for i in range(len(xs) - 1))
    print(f"  밴드 인접성(겹침·틈 0): {'OK' if mono else 'FAIL'} · "
          f"총 {len(s['bands'])} 밴드 × 3매(내측+측벽 2)")
    jt = PARAMS["joint"]
    print(f"  줄눈: 격자 {jt['step']:.2f} m · proud {jt['proud']:.3f} "
          f"(페인트 {pa['z']:.3f} 위 {jt['proud'] - pa['z']:.3f} m) → "
          "그림 영역 관통 OK")
    lp = PARAMS["lamp"]
    az = math.radians(25.0)
    L = lp["pole_h"] / math.tan(math.radians(PARAMS["light"]["noon_sun_elev"]))
    tx = lp["cx"] + L * math.cos(az)
    ty = lp["cy"] + L * math.sin(az)
    print(f"  실그림자 단서: 가로등({lp['cx']:.2f},{lp['cy']:.2f}) h{lp['pole_h']:.1f} "
          f"→ 그림자 길이 {L:.2f} m, 끝점 ({tx:.2f},{ty:.2f}) "
          f"{'= 그림 내부 OK' if (0 <= tx <= s['x_f'] and abs(ty) <= il['width'] / 2) else '(그림 밖 — 재배치 검토)'}")
    mp = PARAMS["material"]
    bk = PARAMS["blocks"]
    print("  팔레트 v2(웜 스톤): tread %s / riser %s·%s / floor %s / wall %s"
          % (mp["tread_tint"], mp["riser_tint_a"], mp["riser_tint_b"],
             mp["floor_tint"], mp["wall_tint"]))
    print("             nosing %s / border %s / block %s  "
          "(암부 0.02~0.09 · R:G:B 웜 비율 유지)"
          % (mp["nosing_tint"], mp["border_tint"], mp["block_tint"]))
    print("  석재 블록 줄눈: enable=%s · z %.4f(페인트 %.4f 위 %.4f) · 폭 %.3f · "
          "디딤면 %d선 / 측벽 %d선"
          % (bk["enable"], bk["z"], pa["z"], bk["z"] - pa["z"], bk["w"],
             len(bk["tread_frac"]), len(bk["wall_frac"])))
    print("  [GT] 전 픽셀 '낙차 없음' — 전 기하 평면, 개구/수직면 없음")
    print("-" * 68)


def ground_plans():
    """[W2 ground_kit] Ground plan — scene assembly and the CPU check use the same function."""
    g = PARAMS["ground"]
    gp = gk.plan_ground(
        "plaza_granite", region=tuple(g["region"]),
        z=float(PARAMS["plaza"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=(),                       # hard negative - 0 drop edges
        dists=(2, 5, 10), scene="sceneN3",
        tactile=(),                     # §12.4 - OFF, it clashes with the hidden-illusion identity
        sites=dict(manhole=[tuple(p) for p in g["manholes"]],
                   gully=[tuple(p) for p in g["gullies"]],
                   patch=[tuple(p) for p in g["patches"]]),
        overrides=dict(pave=dict(joint=None)),
        seed=23)
    return [("plaza", gp)]


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene shots."""
    views = sc.grid_views(0.0)
    il = PARAMS["illusion"]
    # design_eye: the single anamorphic design viewpoint - the only place the illusion holds
    views["design_eye"] = dict(eye=[il["eye_x"], 0.0, il["eye_h"]],
                               tgt=[3.5, 0.0, 0.0])
    # off_axis: side view - the perspective collapses and it shows as a "flat painting" (cue (4))
    views["off_axis"] = dict(eye=[1.5, -6.5, 1.7], tgt=[3.2, 0.0, 0.0])
    # joint_cross: low near view - joints run through the painting (cue (1)) · specular (cue (2))
    views["joint_cross"] = dict(eye=[-0.7, 0.0, 0.35], tgt=[4.5, 0.0, 0.02])
    # beauty_overview: oblique high angle - mall context + the painting laid out
    views["beauty_overview"] = dict(eye=[-5.0, -5.5, 3.4], tgt=[3.5, 0.0, 0.0])
    return views


# ===========================================================================
# [C5] dressing check (no Isaac needed) - NEGOBS_GEOCHECK=1 python3 sceneN3_trompe_loeil.py
#   (1) camera burial : is every view's eye outside the new solid AABBs (0.35 margin)?
#   (2) painting occlusion : do the new solids intrude into the camera-to-painting corridor?
# ===========================================================================
def placements():
    """[v5.1 §3] Deterministic jittered placement. Shared by the builder and the check.
    Returns (benches[(name,x,y,yaw)], planters[(name,x,y)], bollards[(name,x,y)])."""
    bl = []
    for b in PARAMS["benches"]:
        dx, dy = bc.jit_pos(b["cx"], b["cy"], "benchN3", amp=0.18)
        yaw = bc.jit_yaw(b["cx"], b["cy"], "benchN3", lo=3.0, hi=8.0,
                         base=b["yaw"])
        bl.append((b["name"], b["cx"] + dx, b["cy"] + dy, yaw))
    pl = []
    for p in PARAMS["planters"]:
        dx, dy = bc.jit_pos(p["cx"], p["cy"], "plN3", amp=0.15)
        pl.append((p["name"], p["cx"] + dx, p["cy"] + dy))
    bo = []
    sp = PARAMS["bollard"]["spacing"]
    for row in PARAMS["bollard_rows"]:
        pts = bc.bollard_line(row["x"], row["y0"], row["x"], row["y1"],
                              spacing=sp)
        for i, (bx, by) in enumerate(pts):
            bo.append((f"{row['name']}{i}", bx, by))
    return bl, pl, bo


def dressing_aabbs():
    """(name, xa, xb, ya, yb, z_top) of the **solid** context dressing. The paint is flush."""
    out = []
    _benches, _planters, _bollards = placements()
    sp = PARAMS["shop"]
    for fd in PARAMS["shop_facades"]:
        fy, dr = float(fd["y"]), float(fd["dir"])
        y_in = fy + dr * (sp["podium_t"] - sp["podium_embed"])   # podium front face
        y_aw = fy + dr * (sp["podium_t"] - sp["podium_embed"] + sp["awn_proj"])
        out.append((f"Shop_{fd['name']}", sp["x0"], sp["x1"],
                    min(fy, y_aw), max(fy, y_aw), sp["podium_h"]))
        out.append((f"ShopFace_{fd['name']}", sp["x0"], sp["x1"],
                    min(fy, y_in), max(fy, y_in), sp["podium_h"]))
    pl = PARAMS["planter"]
    ph = pl["size"] / 2.0
    top_tree = pl["grass_h"] + 2.2 + 0.85 + 0.24
    for name, px, py in _planters:
        out.append((f"Planter_{name}", px - ph, px + ph,
                    py - ph, py + ph, top_tree))
    # bench 1.8x0.4xh0.45 - half extents (0.92, 0.32) as an upper bound for yaw jitter <=8 deg
    for name, bx, by, _yaw in _benches:
        out.append((f"Bench_{name}", bx - 0.92, bx + 0.92,
                    by - 0.32, by + 0.32, 0.45))
    bo = PARAMS["bollard"]
    for name, bx, by in _bollards:
        out.extend(bc.bollard_v51_aabbs(f"Bollard_{name}", bx, by, 0.0,
                                        front_dir=bo["front"],
                                        radius=bo["r"], height=bo["h"]))
    lp = PARAMS["lamp"]                     # pole/head kept separate (avoids an over-large bound)
    out.append(("LampPole", lp["cx"] - lp["pole_r"], lp["cx"] + lp["pole_r"],
                lp["cy"] - lp["pole_r"], lp["cy"] + lp["pole_r"],
                lp["pole_h"]))
    es = PARAMS["entry_sign"]
    out.append(("EntrySign", es["x"] - es["w"] / 2.0, es["x"] + es["w"] / 2.0,
                es["y"] - 0.1, es["y"] + 0.1, es["pole_h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))
    return out


def dresscheck():
    """※ Known, accepted exception: in beauty_overview·off_axis the **existing streetlight
    pole** (r 0.07, x 0.6 / y −2.6) grazes 3~5 % of the painting samples. That streetlight
    is the very light geometry behind cue ③ (a real shadow crossing the painting), so it
    cannot be moved, and a 14 cm pole crossing a 6.30×3.00 m painting is a thin line that
    does not hinder reading the feature. **New context dressing must be 0 in every view.**
    """
    il = PARAMS["illusion"]
    s = illusion_summary(il)
    hw = il["width"] / 2.0
    pc = [(px, py) for px in (il["x_rim"], s["x_f"]) for py in (-hw, hw)]
    boxes = dressing_aabbs()
    views = build_views()
    print("-" * 68)
    print("sceneN3 드레싱 검산 (그림 풋프린트 x[%.2f, %.2f] × y±%.2f)"
          % (il["x_rim"], s["x_f"], hw))
    m, hit, worst = 0.35, 0, (None, 1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        for nm, xa, xb, ya, yb, zt in boxes:
            if (xa - m <= ex_ <= xb + m and ya - m <= ey_ <= yb + m
                    and -m <= ez_ <= zt + m):
                print("  %-20s ★카메라 매몰★ %s" % (vn, nm))
                hit += 1
            d = max(xa - ex_, ex_ - xb, ya - ey_, ey_ - yb, 0.0)
            if d < worst[1]:
                worst = ("%s vs %s" % (vn, nm), d)
    print("  ① 카메라 매몰: %s (최근접 수평 %s = %.2f m)"
          % ("0건 합격" if hit == 0 else "%d건 불합격" % hit, worst[0], worst[1]))

    # (2) sight-blocking test - sample the painting footprint on a 13x7 grid and decide, by the
    #    slab method, whether the eye->sample segment pierces a dressing AABB (shrunk by 0.01).
    def seg_hits_box(p0, p1, bmin, bmax):
        tmin, tmax = 0.0, 1.0
        for i in range(3):
            d = p1[i] - p0[i]
            if abs(d) < 1e-12:
                if p0[i] < bmin[i] or p0[i] > bmax[i]:
                    return False
                continue
            t1 = (bmin[i] - p0[i]) / d
            t2 = (bmax[i] - p0[i]) / d
            if t1 > t2:
                t1, t2 = t2, t1
            tmin, tmax = max(tmin, t1), min(tmax, t2)
            if tmin > tmax:
                return False
        return True

    def in_frame(eye, tgt, p, hfov=60.0, vfov=36.0):
        fx, fy, fz = (tgt[0] - eye[0], tgt[1] - eye[1], tgt[2] - eye[2])
        fn = math.sqrt(fx * fx + fy * fy + fz * fz)
        fx, fy, fz = fx / fn, fy / fn, fz / fn
        rx, ry = fy, -fx
        rn = math.hypot(rx, ry)
        if rn < 1e-9:
            return False
        rx, ry = rx / rn, ry / rn
        ux, uy, uz = ry * fz, -rx * fz, rx * fy - ry * fx
        dx, dy, dz = p[0] - eye[0], p[1] - eye[1], p[2] - eye[2]
        fw = dx * fx + dy * fy + dz * fz
        if fw <= 1e-6:
            return False
        ah = math.degrees(math.atan2(abs(dx * rx + dy * ry), fw))
        av = math.degrees(math.atan2(abs(dx * ux + dy * uy + dz * uz), fw))
        return ah < hfov / 2.0 and av < vfov / 2.0

    pts = [(il["x_rim"] + (s["x_f"] - il["x_rim"]) * i / 12.0,
            -hw + 2.0 * hw * j / 6.0, 0.0)
           for i in range(13) for j in range(7)]
    bad = 0
    for vn, v in sorted(views.items()):
        eye = tuple(float(c) for c in v["eye"])
        vis = [p for p in pts if in_frame(eye, v["tgt"], p)]
        if not vis:
            continue
        for nm, xa, xb, ya, yb, zt in boxes:
            bmin = (xa + 0.01, ya + 0.01, 0.01)
            bmax = (xb - 0.01, yb - 0.01, zt - 0.01)
            if bmax[0] <= bmin[0] or bmax[1] <= bmin[1] or bmax[2] <= bmin[2]:
                continue
            n_hit = sum(1 for p in vis if seg_hits_box(eye, p, bmin, bmax))
            if n_hit:
                print("  %-20s ★그림 시선 차단★ %s (%d/%d 프레임내 샘플)"
                      % (vn, nm, n_hit, len(vis)))
                bad += 1
    print("  ② 그림 시선 차단(프레임 내 샘플 한정): %s"
          % ("0건 합격" if bad == 0 else "%d건 검토" % bad))
    print("-" * 68)


def geocheck():
    _geometry_report()
    dresscheck()


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. design_eye / h0.9_d2 — 그림이 '하강 계단정'으로 읽히는가(착시 성립·특색)
 2. joint_cross          — 포장 줄눈이 그림을 끊김 없이 관통하는가(단서 ①)
 3. 암부 스펙큘러        — 라이저 암부에 포장과 같은 반사가 남는가(단서 ②)
 4. 실그림자             — 가로등 기둥 그림자가 그림 위를 지나가는가(단서 ③)
 5. off_axis             — 시점 이탈 시 원근이 붕괴하는가(단서 ④)
 6. GT 불변식            — 전 기하 평면·개구 없음·Z파이팅/부유 없는가
 7. 그림 ON vs OFF       — hazard_stairs False 시 순수 평지 몰
 8. 팔레트 v2 [1순위]    — 그림이 **웜 베이지·황갈 석재 분필화**로 읽히는가
                            (무채색 회색 줄무늬면 실패 — v1 폐기 사유).
                            석재 블록 줄눈이 트레드·측벽에 보이는가
 9. 몰 맥락             — 차양·쇼윈도·사인 밴드·벤치·화분·안내 사인으로
                            "보행자 몰"이 렌더만으로 읽히는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene23")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene23"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["plaza"] = PBR(
            f"{ROOT}/Looks/Plaza", sc.tex_path("stone_flag", "diff"),
            sc.tex_path("stone_flag", "nor"), sc.tex_path("stone_flag", "rough"),
            sca["stone_flag"])
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["light_stone"] = PBR(
            f"{ROOT}/Looks/LightStone", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"),
            sc.tex_path("plaza_light", "rough"), sca["plaza_light"],
            tint=(0.72, 0.72, 0.72))                     # [T1 T-1] x0.72
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            2.0, tint=mp["wall_face_tint"])
        M["joint"] = PBR(f"{ROOT}/Looks/Joint",
                         diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], metallic=0.0)
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        metallic=mp["lamp_metallic"],
                        roughness_const=mp["lamp_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots actually shade.
        M["tactile"] = bc.tactile_mtl(stage, f"{ROOT}/Looks/Tactile")
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        # ─ stone block joints inside the painting ─
        M["block"] = PBR(f"{ROOT}/Looks/Block", diffuse_color=mp["block_tint"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        # ─ mall context (shopfronts) ─
        M["podium"] = PBR(
            f"{ROOT}/Looks/Podium", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"),
            sc.tex_path("plaza_light", "rough"), 1.4, tint=mp["podium_tint"])
        M["shopglass"] = PBR(f"{ROOT}/Looks/ShopGlass",
                             diffuse_color=mp["shopglass_color"],
                             roughness_const=mp["shopglass_rough"], metallic=0.0)
        M["awning_a"] = PBR(f"{ROOT}/Looks/AwningA",
                            diffuse_color=mp["awning_a"],
                            roughness_const=mp["awning_rough"])
        M["awning_b"] = PBR(f"{ROOT}/Looks/AwningB",
                            diffuse_color=mp["awning_b"],
                            roughness_const=mp["awning_rough"])
        M["fascia_a"] = PBR(f"{ROOT}/Looks/FasciaA",
                            diffuse_color=mp["fascia_a"],
                            roughness_const=mp["fascia_rough"])
        M["fascia_b"] = PBR(f"{ROOT}/Looks/FasciaB",
                            diffuse_color=mp["fascia_b"],
                            roughness_const=mp["fascia_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        # Korean info sign panel - uv_mode (mesh st 1:1 fit, build_sign only)
        M["sign_panel"] = PBR(f"{ROOT}/Looks/SignPanel",
                              sc.tex_path("sign_info", "diff"), uv_mode=True,
                              roughness_const=0.45)
        return M

    # -------------------------------------------------------------------
    # paint material factory - caches and reuses tints darkened with depth.
    #   every paint uses roughness = paint_rough (same as the paving) - the "material trap".
    # -------------------------------------------------------------------
    def make_paint_mtl_of():
        cache = {}
        base = dict(floor=mp["floor_tint"], tread=mp["tread_tint"],
                    wall=mp["wall_tint"], nosing=mp["nosing_tint"],
                    border=mp["border_tint"],
                    riser_a=mp["riser_tint_a"], riser_b=mp["riser_tint_b"])
        plaza_ref = tuple(mp["flat_ref"])       # mean paving tone (for weakened contrast · warm)
        # depth attenuation floor: risers must stay in the 0.04~0.08 band, so they attenuate shallowly
        lo = dict(floor=1.0, tread=0.55, wall=0.45, riser=0.80,
                  nosing=0.70, border=1.0)

        def mtl_of(kind, idx, depth_frac):
            key_kind = kind
            tint = base.get(kind)
            if kind == "riser":
                key_kind = "riser_a" if idx % 2 == 0 else "riser_b"
                tint = base[key_kind]
            f = lo.get("riser" if kind == "riser" else kind, 1.0)
            k = f + (1.0 - f) * max(0.0, min(1.0, float(depth_frac)))
            col = tuple(c * k for c in tint)
            if not cfg["cue_material_break"]:
                m = float(mp["flat_mix"])
                col = tuple(c * (1.0 - m) + p * m
                            for c, p in zip(col, plaza_ref))
            ck = tuple(round(c, 4) for c in col)
            if ck not in cache:
                path = f"{ROOT}/Looks/Paint/{key_kind}_{len(cache):02d}"
                cache[ck] = PBR(path, diffuse_color=ck,
                                roughness_const=mp["paint_rough"],
                                metallic=0.0)
            return cache[ck]

        return mtl_of, cache

    # -------------------------------------------------------------------
    # paving - a large flagstone slab + granite edge band (no opening -> no splitting needed)
    # -------------------------------------------------------------------
    def build_plaza(M):
        pz = PARAMS["plaza"]
        cz = pz["z_top"] - pz["thick"] / 2.0
        # [W2-0 · P-A] the plaza top face is what ground_kit decorates -> displacement skin OFF.
        #   it must be registered **before the BOX call** (`add_box` decides on the spot).
        #   this scene is especially sensitive - every paint layer is proud by only 0.001~0.003, so
        #   turning the skin on (+6.5~16.5 mm) would **bury the painting itself** `[spec §1.1]`.
        sc.skin_exclude(f"{ROOT}/Plaza")
        BOX(f"{ROOT}/Plaza",
            ((pz["x0"] + pz["x1"]) / 2.0, (pz["y0"] + pz["y1"]) / 2.0, cz),
            (pz["x1"] - pz["x0"], pz["y1"] - pz["y0"], pz["thick"]),
            M["plaza"], col=True)
        bd = PARAMS["band"]
        z_top = pz["z_top"] + bd["proud"]
        z_bot = pz["z_top"] - bd["embed"]
        jt = PARAMS["joint"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Band_{tag}",
                ((jt["x0"] + jt["x1"]) / 2.0, sgn * bd["y"],
                 (z_top + z_bot) / 2.0),
                (jt["x1"] - jt["x0"], bd["width"], z_top - z_bot), M["band"])

    # -------------------------------------------------------------------
    # paving joints - a grid. They **run through the painting area** unbroken (cue (1)).
    #   proud 0.003 above the paint (z=0.001) -> 2 mm clearance, no Z-fighting.
    # -------------------------------------------------------------------
    def build_joints(M):
        jt = PARAMS["joint"]
        pz = PARAMS["plaza"]
        z_top = pz["z_top"] + jt["proud"]
        z_bot = pz["z_top"] - jt["embed"]
        zc, hz = (z_top + z_bot) / 2.0, z_top - z_bot
        Lx = jt["x1"] - jt["x0"]
        Ly = jt["y1"] - jt["y0"]
        n_x = int(round(Lx / jt["step"])) + 1
        n_y = int(round(Ly / jt["step"])) + 1
        for i in range(n_x):                     # cross joints (constant x)
            x = jt["x0"] + i * jt["step"]
            BOX(f"{ROOT}/JointX_{i}", (x, (jt["y0"] + jt["y1"]) / 2.0, zc),
                (jt["width"], Ly, hz), M["joint"])
        for j in range(n_y):                     # longitudinal joints (constant y)
            y = jt["y0"] + j * jt["step"]
            BOX(f"{ROOT}/JointY_{j}", ((jt["x0"] + jt["x1"]) / 2.0, y, zc),
                (Lx, jt["width"], hz), M["joint"])

    # -------------------------------------------------------------------
    # painting - the anamorphic paint array + border line
    # -------------------------------------------------------------------
    def build_painting(M):
        il = PARAMS["illusion"]
        pa = PARAMS["paint"]
        mtl_of, cache = make_paint_mtl_of()
        bands, n_prim = paint_fake_stairs(stage, f"{ROOT}/Paint", il, pa,
                                          mtl_of, nosing=cfg["cue_nosing"],
                                          blocks=PARAMS["blocks"],
                                          block_mtl=M["block"])
        s = illusion_summary(il)
        print(f"[그림] 밴드 {len(bands)} · 페인트 프림 {n_prim} · "
              f"재질 {len(cache)} · 풋프린트 x[{il['x_rim']:.2f},{s['x_f']:.2f}] "
              f"× {il['width']:.2f} m · 가시 단 {len(s['steps'])}/{il['nsteps']}")
        if not pa["border"]:
            return
        # white border line (painting boundary - the chalk edging in the reference)
        bmtl = mtl_of("border", 0, 1.0)
        hw = il["width"] / 2.0
        w = pa["border_w"]
        z = pa["border_z"]
        x0, x1 = il["x_rim"], s["x_f"]
        rects = [("W", x0 - w / 2.0, 0.0, w, 2 * hw + w),
                 ("E", x1 + w / 2.0, 0.0, w, 2 * hw + w),
                 ("S", (x0 + x1) / 2.0, -hw - w / 2.0, x1 - x0, w),
                 ("N", (x0 + x1) / 2.0, hw + w / 2.0, x1 - x0, w)]
        for tag, cx, cy, sx, sy in rects:
            _paint_quad(stage, f"{ROOT}/Paint/Border_{tag}",
                        [(cx - sx / 2.0, cy - sy / 2.0),
                         (cx + sx / 2.0, cy - sy / 2.0),
                         (cx + sx / 2.0, cy + sy / 2.0),
                         (cx - sx / 2.0, cy + sy / 2.0)], z, bmtl)

    # -------------------------------------------------------------------
    # [W2] ground_kit - P1 plaza_granite. Placed **outside the painting** only (x <= −1.6).
    #   0 drop edges -> GT-E1′/GT-E2 are vacuously true. The verdict rests on the two B12
    #   invariants (`_inv_n3_painting` surface elements ∩ painting = ∅ · `_inv_hidden_illusion`).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["joint"], crack=M["joint"], patch=M["light_stone"],
                  patch_cut=M["curb"], manhole=M["lamp"], gully=M["lamp"],
                  gutter=M["curb"], weed=M["grass"], tactile=M["tactile"],
                  stain_dirt=M["joint"], stain_water=M["joint"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneN3 P1 · 프림 {res['prims']} · 산포 "
              f"{res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # dressing - streetlight (real-shadow cue)·planters·benches·bollards·retail buildings
    # -------------------------------------------------------------------
    def build_dressing(M):
        lp = PARAMS["lamp"]
        CYL(f"{ROOT}/Lamp/Pole", (lp["cx"], lp["cy"], lp["pole_h"] / 2.0),
            lp["pole_r"], lp["pole_h"], M["lamp"], col=True)
        hd = lp["head"]
        BOX(f"{ROOT}/Lamp/Head",
            (lp["cx"] + hd[0] / 2.0 - lp["pole_r"], lp["cy"],
             lp["pole_h"] + hd[2] / 2.0), hd, M["lamp"])
        _benches, _planters, _bollards = placements()
        pl = PARAMS["planter"]
        for name, px, py in _planters:
            sc.build_planter(
                stage, f"{ROOT}/Planter_{name}", px, py,
                0.0, M["curb"], M["grass"],
                tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        for name, bx, by, byaw in _benches:
            sc.build_bench(stage, f"{ROOT}/Bench_{name}", bx, by, 0.0,
                           M["wood"], yaw=byaw)
        # bollards [v5.1 §2] - one row across the mall entrance (central 4.8 m left open as a fire lane)
        bo = PARAMS["bollard"]
        for name, bx, by in _bollards:
            # [W2 §12.4] this scene has **no tactile paving** - for the 4 hidden-illusion
            #   scenes (14·20·21·N3) "no permanent high-contrast cue" is the identity, and
            #   N3 is not in the §12.4 list of "4 scenes that keep bollards throughout".
            #   `ground_kit._inv_hidden_illusion` also blocks tactile paving in this
            #   scene via B12 -> the scene's own fittings follow the same ruling.
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{name}", bx, by, 0.0,
                                 None, M["bollard"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["r"], height=bo["h"],
                                 tactile=False)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_shopfronts(M)
        es = PARAMS["entry_sign"]
        sc.build_sign(stage, f"{ROOT}/EntrySign", es["x"], es["y"], 0.0,
                      es["yaw"], M["sign_panel"], w=es["w"], h=es["h"],
                      pole_h=es["pole_h"], pole_r=es["pole_r"],
                      pole_mtl=M["lamp"], back_mtl=M["sign"])

    # -------------------------------------------------------------------
    # shopfront band - the key context that makes "pedestrian mall" readable from the render alone.
    #   podium (ground-floor wall) + per-bay shop window · awning · fascia band. All at |y| >= 8.25,
    #   so unrelated to occluding the painting (|y| <= 1.5) or burying a camera [shopcheck()].
    #   shadows: sun az 205 -> shadow bearing 25 deg (+X,+Y). The L (y=+10) awning shadow goes
    #   toward +Y, and the R (y=−10) awning shadow reaches only from y −8.25 to about −6.8 ->
    #   neither touches the painting area (|y| <= 1.5).
    # -------------------------------------------------------------------
    def build_shopfronts(M):
        sp = PARAMS["shop"]
        nbay = max(1, int(round((sp["x1"] - sp["x0"]) / sp["bay"])))
        bw = sp["bay"] - sp["gap"]
        for fd in PARAMS["shop_facades"]:
            fy, dr = float(fd["y"]), float(fd["dir"])
            base = f"{ROOT}/Shop_{fd['name']}"
            # podium (ground-floor wall) - fully encloses the ground-floor windows (avoids Z-fighting).
            #   pushed into the shell by podium_embed, which also removes back-face coplanarity.
            py = fy + dr * (sp["podium_t"] / 2.0 - sp["podium_embed"])
            BOX(f"{base}/Podium",
                ((sp["x0"] + sp["x1"]) / 2.0, py, sp["podium_h"] / 2.0),
                (sp["x1"] - sp["x0"], sp["podium_t"], sp["podium_h"]),
                M["podium"], col=True)
            face = fy + dr * (sp["podium_t"] - sp["podium_embed"])   # front y
            for i in range(nbay):
                xc = sp["x0"] + (i + 0.5) * sp["bay"]
                BOX(f"{base}/Glass_{i}",
                    (xc, face + dr * (sp["glass_proud"] - sp["glass_t"] / 2.0),
                     (sp["glass_z0"] + sp["glass_z1"]) / 2.0),
                    (bw, sp["glass_t"], sp["glass_z1"] - sp["glass_z0"]),
                    M["shopglass"])
                BOX(f"{base}/Awning_{i}",
                    (xc, face + dr * sp["awn_proj"] / 2.0, sp["awn_z"]),
                    (bw, sp["awn_proj"], sp["awn_t"]),
                    M["awning_a"] if i % 2 == 0 else M["awning_b"])
                BOX(f"{base}/Fascia_{i}",
                    (xc, face + dr * (sp["fascia_proud"] - sp["fascia_t"] / 2.0),
                     (sp["fascia_z0"] + sp["fascia_z1"]) / 2.0),
                    (bw, sp["fascia_t"], sp["fascia_z1"] - sp["fascia_z0"]),
                    M["fascia_a"] if i % 2 == 0 else M["fascia_b"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_plaza(M)
    if cfg["hazard_stairs"]:
        build_painting(M)
    build_joints(M)                              # runs over the painting - built after it
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)                          # [W2] ground elements (outside the painting only)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        _geometry_report()
        print(f"[SMOKE] sceneN3 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["design_eye"]
    look_from(_v0["eye"], _v0["tgt"])

    pt_spp = int(PARAMS["render"]["pt_total_spp"])

    def set_render_mode(mode):
        if mode == "PathTracing":
            settings.set("/rtx/pathtracing/spp", 1)
            settings.set("/rtx/pathtracing/totalSpp", pt_spp)
            settings.set("/rtx/pathtracing/optixDenoiser/enabled", True)
            settings.set("/rtx/pathtracing/maxBounces",
                         int(PARAMS["render"]["pt_max_bounces"]))
            settings.set("/rtx/rendermode", "PathTracing")
        else:
            settings.set("/rtx/rendermode", "RaytracedLighting")

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        out_dir = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    def on_key(event, *args):
        if event.type != carb.input.KeyboardEventType.KEY_PRESS:
            return True
        if event.input == K.P:
            cur = settings.get("/rtx/rendermode")
            if cur == "PathTracing":
                set_render_mode("RaytracedLighting")
                print("[렌더] RTX Real-Time (이동용)")
            else:
                set_render_mode("PathTracing")
                print(f"[렌더] PathTracing (totalSpp={pt_spp})")
        elif event.input == K.C:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN3_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        return True

    keyboard_sub = input_iface.subscribe_to_keyboard_events(
        appwindow.get_keyboard(), on_key)

    print("=" * 64)
    print(BANNER)
    print("-" * 64)
    print("※ 키가 안 먹으면 Isaac Sim 창을 한 번 클릭해서 포커스를 줘!")
    print("=" * 64)

    while simulation_app.is_running():
        simulation_app.update()

    input_iface.unsubscribe_to_keyboard_events(
        appwindow.get_keyboard(), keyboard_sub)
    simulation_app.close()


if __name__ == "__main__":
    if os.environ.get("NEGOBS_GEOCHECK", "0") == "1":
        geocheck()                     # anamorphic and dressing checks without booting Isaac
    else:
        main()
