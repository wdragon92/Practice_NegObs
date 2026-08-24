# -*- coding: utf-8 -*-
"""
sceneC1_snow_stairs.py - NegObs synthetic scene 26: snow-covered stairs (Isaac Sim 4.5)

Type    : C1 condition variant - existing straight-stair geometry + a snow environment layer (core batch1 scene)
Spec    : Docs/nanobanana_batch1_geometry_map.md §B sceneC1_snow_stairs
Look ref: look_refs/c1_snow_stairs.jpg
Shared  : scene_common.py · scene16_canopy_shadow.py (standard template) ·
          scene01_campus_stairs.py (straight-stair reference form)

Hazard  : The geometry is an ordinary straight flight of 12 (riser 0.17 · tread 0.30 · width 2.5),
          yet 5cm of snow bridges the treads into an **ambiguous white slope**.
          The step edges are hinted at only by the rounded ridge line the nosing overhang
          (snow eave) makes, and the high-albedo, low-contrast overcast light smears even
          that ridge. GT follows the geometry as built - **drop positive (2.04m)** - an
          extreme case with the cue buried.
Goal    : Keeping the walking continuity of upper terrace -> stairs -> lower ground (lesson 9),
          lay the snow layer (per-tread snow boxes + approach plates + railing top strip)
          on top and judge from the render (render only).

Signature precondition [important]:
  **Low-contrast overcast light** is the precondition for this scene's signature. Under clear
  noon light, hard shadows re-create the step edges sharply and the "concealment" itself
  collapses. So the light profile is sc.OVERCAST_HDRI + lookfix=False + sunless (DistantLight
  invisible), and the lost direct light is compensated by raising dome_intensity.

Concealment control [for director sweeps]:
  thickness / chamfer in PARAMS["snow"] govern step-edge visibility (defaults 0.05 / 0.030).
  **[GT-119 ③ · 08-15] `nose_over` / `riser_cover` / `lip_recess` / `side_over` are RETIRED.**
  They built each tread's snow as a rigid slab pushed 60 mm past the riser with a set-back fin
  under it - a 51 mm cantilever over a 35 mm shadow slot, i.e. an edge that reads *sharper*
  than the bare concrete it was meant to hide (checklist item 2 defeated), and the same
  +side_over spilled white tabs over the stringers on every step. The snow front face is now
  flush with the riser plane (never proud) and the front-top edge carries a 45 deg chamfer.
  To bury the edges further than the reference, raise thickness 0.05 -> 0.09 and
  chamfer 0.030 -> 0.045; the front plane itself is not a sweep knob any more.
  The concrete stair, the tread z, the drop registry and the nosing prims are bit-unchanged.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneC1_snow_stairs.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneC1_snow_stairs.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneC1_snow_stairs.py
Self-check (CPU, no boot):NEGOBS_SELFCHECK=1 python3 sceneC1_snow_stairs.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0.
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
# [A] SCENE_CONFIG - standard 7 keys + 1 signature toggle (snow_cover).
#     Only hazard_stairs is a geometry toggle (False -> all-flat z=0 ground).
#     snow_cover is this scene's signature toggle - per spec "False -> remove snow",
#     so the snow-layer prims disappear and the bank surface drops by the snow depth
#     (the stair core geometry = GT is unchanged).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> stairs/banks/lower ground become z=0 flat (the one geometry-toggle exception)
    "cue_railing":        True,   # one-sided (+Y) pipe railing + snow strip on top
    "cue_tactile":        True,   # warning tactile paving at the top - fully buried under the snow (signature)
    "cue_material_break": True,   # False -> stairs get the same concrete tone as the approach
    "cue_nosing":         True,   # yellow anti-slip band - buried under snow, exposed only in the twin
    "cue_sign":           False,  # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,   # cleared snow piles, post and distant buildings together
    "snow_cover":         True,   # [signature] False -> remove the snow layer = twin (bare stairs)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # straight 12 steps x riser 0.17 · tread 0.30 -> drop 2.04m, run 3.60m, width 2.5
    stairs=dict(x0=0.0, riser=0.17, tread=0.30, nsteps=12,
                y0=-1.25, y1=1.25, z_top=0.0, base_z=-2.90),

    # Upper terrace (top of the embankment). Thickness 2.6 -> solid down past the lower ground floor.
    terrace=dict(x0=-60.0, x1=0.0, y0=-60.0, y1=60.0, z_top=0.0, thick=2.60),
    # Lower ground. x0 starts 0.05 behind the stair end (run) and its top face is 2mm lower
    # to avoid a coplanar face (Z-fighting) with the last step top - 5cm overlap.
    lower=dict(x_back=0.05, x1=60.0, y0=-60.0, y1=60.0, z_gap=0.002,
               thick=0.70),

    # Snow banks on both sides of the stair (embankment slope). Top plane z = lift - (riser/tread)·x
    #   = the "nosing line" (the line joining the front edges of the steps) raised by the snow depth.
    #   -> it joins the upper terrace snow face (z=+t) and the lower ground snow face (z=-2.04+t) exactly:
    #     no extra drop edge = no GT contamination, walking continuity kept (lesson 9).
    #   y_in sits 0.02 inside the stair flank (+-1.25) -> solid overlap (avoids a coplanar face).
    bank=dict(y_in_over=0.02, y_out=60.0, x_head=0.02, x_tail=0.20, thick=2.20),
    # Exposed concrete stringer on the stair flank (the only non-snow element in the reference).
    # Top face = bank face + proud(0.02) -> survives as a thin dark edge line in the snow field.
    stringer=dict(y_in=1.20, y_out=1.45, proud=0.02, x_head=0.05, x_tail=0.10,
                  thick=0.60),

    # ─── snow layer [signature parameters · GT-119 ③ re-cut] ────────────
    #  thickness   snow depth. Raising it thickens the ridge on the tread top so the
    #              edge contrast falls against the step height. Geometry-map spec 0.05. Sweep 0.05->0.09.
    #  chamfer     45 deg front-top chamfer (run = drop). **This is the edge-silhouette knob
    #              that replaces the retired `nose_over`**: it takes material *off* the razor
    #              corner instead of hanging material past the riser. Sweep 0.030->0.045.
    #              Must satisfy 0 < chamfer < thickness (a chamfer as deep as the layer would
    #              leave no front face at all).
    #  cham_thick  chamfer wedge thickness measured perpendicular to its own face. Only has to
    #              be deep enough to meet the bed under it: >= (thickness-chamfer) is plenty.
    #  front_inset how far the snow front face sits **behind** the riser plane (>=0; 0 = flush).
    #              Never negative - a positive number here is the only legal direction, and
    #              raising it exposes the buried nosing band, so leave it at 0 unless ruled.
    #  side_inset  y inset from the stair flank. Must stay inside the band
    #              0.010 <= side_inset <= bank.y_in_over (0.020): below it the snow spills over
    #              the stringer again (the white tabs), above it the snow stops short of the
    #              bank and a bare concrete sliver opens along the flank.
    #  rest_gap    the tread bed **rests this far above the tread** instead of biting into it.
    #              A flush front face plus an embedded bottom would put a snow face in the same
    #              plane as the riser (Z-fighting, checklist item 6). The gap is sealed to
    #              within 1.1 deg of horizontal by the nosing band under it, so no camera in
    #              build_views() (all >= 10 deg down) can see into it. Must exceed the nosing
    #              proud (0.001).
    #  back_bury   how far the bed's trailing edge bites into the step above (X) - the
    #              coplanar-face guard at the back, where the snow is inside solid concrete.
    #  embed_plate depth buried into the solid below on the approach plates (no visual effect).
    # ────────────────────────────────────────────────────────────────────
    snow=dict(thickness=0.05, chamfer=0.030, cham_thick=0.025,
              front_inset=0.000, side_inset=0.015, rest_gap=0.002,
              back_bury=0.010, embed_plate=0.020,
              rail_strip_w=0.08, rail_strip_t=0.05, rail_strip_lift=0.04),

    # One-sided railing (right in the reference). Stands on the bank face, same pitch as the stairs.
    rail=dict(y=1.60, x_start=-1.20, rail_h=0.90, post_r=0.022, rail_r=0.03,
              rail_mid_r=0.018, rail_mid_drop=0.45, spacing=1.20),

    #  Tactile paving - [W2 §12.4] "keep ON (current)", but **move the enforcer to ground_kit**.
    #  The current `sc.build_tactile` is a flat constant-colour plate with no dots, so the shading
    #  of the statutory 36 dots was 0 on screen (§12.5 (3)). The kit emits the spec
    #  (300 grid · dot Ø25 mm · 6 mm) as-is via `build_tactile_pair`.
    #  The position is corrected to the statutory value too: old `x −0.30…0` (touching the stair) ->
    #  **`x −0.90…−0.30`** = "0.3 m before the first step, 60 cm standard depth"
    #  `[statute Enforcement Rule of the Mobility Convenience Act, Table 1, item 2(i) · spec National Road Practice Guide 7.5]`.
    #  GT-E1′ passes only at this position too - dots 0.006 m x EDGE_K 40 = 0.24 m
    #  clearance required, statutory 0.30 m > 0.24 ✔ `[computed]`.
    tactile=dict(ahead=0.30, depth=0.60, proud=0.004),

    # ═══ [W2 ground_kit] P1 plaza_granite - spec §5.1 C1 row ════════════════
    #  * Conditional overlay: **the ground elements of this scene lie under the snow.**
    #    Snow depth 0.05 m burying the anti-slip band and the dot tactile paving is the scene's
    #    signature (§7.3 B12 `_inv_c1_snow`: new elements proud <= 0.05), so the plan is
    #    built on the terrace top face z=0. In the `snow_cover=False` twin the same
    #    elements are exposed as-is - the twin carries more information.
    #  * Cap the weed height at 0.045 (`caps.weed_h`). The default 0.12 exceeds the snow
    #    depth and would stick up above the snow, which violates B12.
    #  * The scene-specific prescription "cleared-snow traces" (wear lane · footprints) is laid
    #    separately on **the snow surface z=LIFT** - the plan is single-z so it cannot go in the same call.
    ground=dict(
        region=(-11.0, -3.0, 0.0, 3.0),
        manhole=(-2.40, 0.60),          # W2 window (d5 X=2.6 m · 21.6 % of screen width)
        gully=(-6.00, 2.40),
        patches=[(-1.20, 0.10), (-8.80, -0.20)],
        weed_h=0.045,
        #  Cleared-snow traces - wear lane 1.0 m wide at centre (spec 0.8~1.2), albedo x0.75.
        #  The x far end stops at −0.10: proud is 0.0006 so GT-E1′ only needs 0.024 m
        #  of clearance, but we still avoid a bright terminating line stuck to the edge.
        trace_lane=((-11.0, 0.0), (-0.10, 0.0)),
        trace_lane_w=1.0, trace_lane_gain=0.75,
        trace_steps=12,
        trace_path=[(-10.6, 0.30), (-0.30, 0.10)],
    ),
    # Set the nosing y 0.02 inside the stair width -> fully enclosed inside the snow slab.
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.05, proud=0.001,
                y_inset=0.02),

    # Dressing - cleared snow piles (3 squashed spheres/pile) · marker post · distant buildings
    piles=[dict(cx=-4.2, cy=3.6, s=1.0), dict(cx=-6.5, cy=-3.2, s=0.8),
           dict(cx=-2.6, cy=-5.4, s=0.9)],
    pile=dict(blobs=((0.00, 0.00, 1.30, 0.55), (0.75, 0.25, 1.05, 0.40),
                     (-0.60, -0.20, 0.95, 0.38))),
    pole=dict(cx=-3.4, cy=2.9, r=0.05, h=2.60, cap_t=0.06),
    buildings=dict(
        # Blocks the +X distant vista (plinth at the lower ground level). Facade on the -X plane.
        C=dict(x0=26.0, x1=32.0, y0=-14.0, y1=14.0, h=12.0, floors=4,
               axis="x", facade_x=26.0, face_dir=-1.0),
        # -X distance (for lower_lookback). Facade on the +X plane, plinth at terrace level.
        D=dict(x0=-46.0, x1=-40.0, y0=-14.0, y1=14.0, h=9.0, floors=3,
               axis="x", facade_x=-40.0, face_dir=1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # ═══ [context dressing v2 · 07-27] a winter residential area/campus that reads as "where am I" ═══
    #  Answers §emptiness of the audit v4 integrated plan. The stair core, snow layer and lighting
    #  parameters are left completely untouched; new prims go only on the upper terrace (x<0, top
    #  z=LIFT) and the lower ground (x>RUN, top z=LOWER_TOP+LIFT).
    #  Every element gets a **snow cap (white thin plate 0.03~0.05)** to keep the snow consistent.
    #
    #  [camera check - all 8+4 shots of build_views(), assuming FOV horizontal +-30 deg / vertical +-18 deg]
    #   grid  eye(-2/-5/-10, 0, h) +X · approach eye(-6,0,1.65) ·
    #   grazing_top eye(-2.2,0,0.35) · rail_side eye(-3.0,3.2,1.5) az -29.1° ·
    #   lower_lookback eye(7.0,0.6,1.5) az 184.3°
    #   -> each item comment below records (camera, azimuth, whether it occludes the stairs).
    #   Shared rules (1) no new solid within a 1.5 m radius of the camera eye
    #            (2) placed outside the stair azimuth band (computed per viewpoint) = signature not occluded
    #            (3) no intrusion into the walking corridor (|y|<1.6, approach x<0 / lower x>RUN)
    # ───────────────────────────────────────────────────────────────────────
    # 2 snow-covered benches - A(-1.0,-2.35) is at the right frame edge of approach
    #   (az -19.2..-32.9 deg, outside the +-11.8 deg stair band) & mid ground of lower_lookback.
    #   B(-6.9,3.9) is on the left of lower_lookback. 0.22 m clear of snow pile 0
    #   (x -5.75..-2.40) - passes self-audit.
    benches=[dict(cx=-1.0, cy=-2.35, yaw=0.0, base="upper"),
             dict(cx=-6.9, cy=3.9, yaw=0.0, base="upper")],
    bench=dict(length=1.8, width=0.50, height=0.45, back_h=0.42, cap_t=0.04),
    # 2 street lamps - long shadows under the soft direct light (elev 28 deg, light travel
    #   (-0.879,+0.477,-0.469); derived from dome_rot -110+171.5=61.5 deg · rotX 62 deg).
    #   A(-0.9,-3.10): h4.0 -> shadow end (-7.5,+0.5). **Falls entirely on the x<0 terrace,
    #   so it never touches the stair treads** = concealment condition unchanged, only more near-field snow relief.
    #   Cameras: approach head az -23.3 deg (outside the stair +-11.8 deg) · grid d5 head
    #   az -28.2 deg (outside the stair +-14 deg) · grid d10 head az -13.6 deg (outside the stair +-7.1 deg) ·
    #   rail_side az -71 deg (outside the -59..+1 deg frame) · lookback az 203.9 deg (behind the stairs).
    lamps=[dict(cx=-0.9, cy=-3.10, arm=0.9, base="upper"),
           dict(cx=-8.4, cy=3.6, arm=-0.9, base="upper")],
    lamp=dict(pole_r=0.06, pole_h=4.0, arm_r=0.035, head_l=0.34, head_w=0.22,
              head_h=0.14, cap_t=0.04),
    # 1 signpost - lower_lookback only (az 201.4 deg). Outside the frame of every frontal viewpoint.
    signpost=dict(cx=-3.2, cy=-3.4, pole_r=0.045, pole_h=2.15,
                  panel_w=0.70, panel_h=0.50, panel_t=0.06, panel_z=1.72,
                  cap_t=0.035),
    # Snow-covered hedge lines - define the site boundary (top fix for emptiness).
    #   Upper 2 rows (|y|=5.2, x -22..-4.5): cut to clear snow pile 2 (x -3.8..-1.4).
    #   Lower 2 rows (|y|=7.0, x 6.5..12.5) + 2 perpendicular rows (x 12.0..12.7) = distant garden boundary.
    #   All outside the walking corridor (|y|<1.6) · farther than the stairs so they cannot occlude.
    hedges=[dict(x0=-22.0, x1=-4.5, y0=4.85, y1=5.55, h=0.75, base="upper"),
            dict(x0=-22.0, x1=-4.5, y0=-5.55, y1=-4.85, h=0.75, base="upper"),
            dict(x0=6.5, x1=12.5, y0=6.65, y1=7.35, h=0.80, base="lower"),
            dict(x0=6.5, x1=12.5, y0=-7.35, y1=-6.65, h=0.80, base="lower"),
            dict(x0=11.4, x1=12.1, y0=7.00, y1=15.5, h=0.80, base="lower"),
            dict(x0=11.4, x1=12.1, y0=-15.5, y1=-7.00, h=0.80, base="lower")],
    # [GT-119 ③] `over=0.05` retired - the cap now insets from the hedge outline
    #   (SNOW_CAP_INSET) like every other object cap.
    hedge_cap=dict(t=0.05),
    # 4 distant low-rise houses (snow-capped roof + chimney) - horizon closure + reads as residential.
    #   The lower 3 fill the mid/far frame of approach/grazing_top (in front of building C),
    #   the upper 1 forms the background with building D on the left of lower_lookback (az 161.4 deg).
    #   None overlap each other, the hedges or the existing buildings (coordinate check done).
    houses=[dict(x0=13.0, x1=19.0, y0=9.0, y1=15.0, h=5.0, base="lower",
                 face=-1.0),
            dict(x0=15.0, x1=20.0, y0=-18.0, y1=-11.0, h=4.5, base="lower",
                 face=-1.0),
            dict(x0=20.0, x1=25.0, y0=4.5, y1=10.5, h=6.0, base="lower",
                 face=-1.0),
            dict(x0=-18.0, x1=-12.0, y0=7.0, y1=13.0, h=5.0, base="upper",
                 face=1.0)],
    house=dict(eave=0.35, roof_t=0.16, cap_t=0.06, cap_inset=0.06,
               chimney_s=0.50, chimney_h=1.10, win_w=1.0, win_h=1.4,
               win_rows=2, win_cols=3, foot=0.60),

    material=dict(
        scale=dict(concrete_floor=1.0, dirt_park=2.0, brick_red=2.0,
                   tactile=0.3),
        # Snow: high albedo, so it is not subject to the dark sRGB convention (0.02~0.06).
        snow_color=(0.72, 0.74, 0.78), snow_rough=0.95, snow_spec=0.1,
        stair_tint=(0.92, 0.92, 0.95),      # slight colour difference for cue_material_break
        dirt_tint=(0.72, 0.68, 0.62),       # bank (decomposed granite) when the snow is removed
        rail_color=(0.72, 0.74, 0.78), rail_metallic=0.8, rail_rough=0.45,
        wall_tint=(0.88, 0.88, 0.90),
        glass_color=(0.05, 0.07, 0.10), glass_rough=0.12,
        parapet_color=(0.86, 0.87, 0.88), parapet_rough=0.7,
        # ─ context dressing v2 constants (dark sRGB convention 0.02~0.09 observed) ─
        wood_color=(0.055, 0.036, 0.022), wood_rough=0.85,   # bench timber
        roof_color=(0.045, 0.042, 0.048), roof_rough=0.75,   # house roof slab
        hedge_color=(0.030, 0.048, 0.028), hedge_rough=1.0,  # evergreen hedge
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,      # lamp head (daytime)
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.50,
        sign_color=(0.045, 0.085, 0.19),                     # signpost panel (blue)
    ),

    # ─── overcast lighting profile (same as sceneC4) ────────────────────
    #  · hdri=sc.OVERCAST_HDRI : overcast sky instead of clear sky -> no sun disc.
    #  · lookfix=False         : lookfix is for "sun cap + horizon lift". It is meaningless
    #                            for a sunless HDRI (the peak-luminance pixel is not the sun),
    #                            so the original is used.
    #  · noon_sun_enable=False : auxiliary DistantLight invisible -> hard shadows removed.
    #                            (setup_lighting always reads the intensity/color keys,
    #                             so the keys themselves are kept.)
    #  · dome_intensity        : raised by as much as the 2450 of direct light lost. Relative to
    #                            the previous noon 1000, a 1500~2500 sweep is advised. Start at 2000.
    #                            Snow (albedo 0.85), so move toward 1600 if overexposed,
    #                            toward 2400 if the highlights die.
    #  · hdri_sun_rotz_offset  : meaningless without a sun -> 0.0.
    # ────────────────────────────────────────────────────────────────────
    light=dict(
        hdri=sc.OVERCAST_HDRI,
        dome_intensity=800.0,    # saturated even at r2 -> extra stop down. A sunless dome alone makes RT flat light - judge on PT
        noon_dome_rot=-110.0,
        lookfix=False,
        noon_sun_enable=True, noon_sun_elev=28.0,   # r3: fully directionless light gives no shading on the ridge lines (whiteout) -> restore relief with low-intensity soft direct light
        noon_sun_intensity=420.0, noon_sun_color=(1.0, 0.985, 0.97),
        hdri_sun_rotz_offset=0.0,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET: the profile is sunless, so shadow azimuth is meaningless. Rotating the
    #     dome in Z only changes the gentle luminance gradient of the overcast sky and the direction
    #     of distant reflections. Kept at the brief v3 §A-7 default 171.5 for harness consistency; sweepable with the [ ] keys. ───
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
# [B'] keep_dressing — the v3 arm C control, resolved ONCE at module scope
# ===========================================================================
#   Arm C = "hazard geometry removed, cue and dressing objects KEPT in their ON
#   transforms" (RENDER_PLAN_V3 §1.2). The pattern is ported from the sibling
#   `sceneC2_leaf_stairs.py:496-520`, verbatim in structure and in reasoning.
#   Every use below reads this one constant, so `grep KEEP_DRESSING` is the whole
#   audit surface, and False — the default, and the value both existing arms
#   carry — makes every guarded expression collapse to exactly the pre-patch code
#   path.
#   The contradictions are FATAL rather than silently resolved: an arm whose
#   config does not say what it means must not render 24 cuts and be discovered
#   later in a metrics table (sceneC2:503-507, same reasoning).
#   `snow_cover` is deliberately NOT constrained: it is this scene's signature
#   toggle, not its cue set, and `build_flat_fill` already carries the snow
#   through to the hazard-off arms as one flat plate.
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneC1] keep_dressing=True requires hazard_stairs=False — "
            "with the hazard ON there is nothing to keep and the arm would be "
            "an unlabelled duplicate of arm A. Fix the render config.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneC1] keep_dressing=True contradicts "
            "cue_scene_dressing=False — the dressing IS what this arm exists to "
            "preserve.")
    print("[keep_dressing] sceneC1 ON — stair·side banks·stringers·lower ground "
          "collapse into the off arm's flat plate (top z=0) with its flat snow "
          "plate on top; the +Y pipe railing is rebuilt LEVEL on it (same y "
          "1.60, same x span, same 0.90 m height) with its snow strip, the "
          "stair-head tactile band rides through `build_ground_kit` (already "
          "outside the hazard test), and piles·pole·buildings·benches·lamps·"
          "hedges·houses keep their ON transforms — their lower datum already "
          "collapses to 0 via `LOWER_TOP if cfg[\"hazard_stairs\"] else 0.0`. "
          "Step nosing is NOT rebuilt (declared limit, see `build_cues`). "
          "Camera datum (x<0, |y|<=0.90): snow top +0.050 in EVERY arm — "
          "`Snow/PlateTop` in arm A, `Snow/FlatPlate` here.")


# ===========================================================================
# [C] path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneC1")

ASSET_ROLES = ["concrete_floor", "dirt_park", "brick_red", "tactile",
               "hdri", "mdl"]


# --- derived dimensions (shared by several builders) -------------------------
def _dims():
    st = PARAMS["stairs"]
    run = st["tread"] * st["nsteps"]
    drop = st["riser"] * st["nsteps"]
    slope_k = st["riser"] / st["tread"]          # nosing-line slope (descending +X)
    lift = PARAMS["snow"]["thickness"] if SCENE_CONFIG["snow_cover"] else 0.0
    return run, drop, slope_k, lift


def _steps():
    """Per-step (xa, xb, ztop) - **the same call the concrete stair makes**.

    `build_snow` used to recompute `x0 + tread*(i-1)` on its own, which differs from
    `_stair_steps`' running sum in the last bits (step 3 ended at 0.9 for the snow and at
    0.8999999999999999 for the concrete). Sharing the derivation makes "snow front <= riser
    plane" an exact comparison instead of one that has to carry a float tolerance.
    """
    st = PARAMS["stairs"]
    return sc._stair_steps(st["x0"], st["riser"], st["tread"], st["nsteps"],
                           st["z_top"], None, None)


def _bank_top(x):
    """Top face of the side bank (= the nosing line raised by the snow depth) at x.
    The stringer face is this + `stringer.proud`. Any snow that climbs above this line
    while reaching past the stair flank surfaces as a white tab over the stringer."""
    _run, _drop, slope_k, lift = _dims()
    bk = PARAMS["bank"]
    x0 = PARAMS["stairs"]["x0"] - bk["x_head"]
    z0 = lift + slope_k * bk["x_head"]
    return z0 - slope_k * (float(x) - x0)


# ===========================================================================
# [B2] [GT-119 ③] snow-layer geometry - one pure derivation, two consumers.
#   `build_snow()` emits it and `snow_selfcheck()` measures it, so the gates are a
#   measurement of what is actually built rather than a restatement of intent.
#
#   What was wrong (audit R4 · crop pt_noon_lower_lookback.png 520,600-1320,1000):
#     (a) each tread's cap was a slab pushed `nose_over` = 60 mm past the riser, with a
#         `lip_recess`-set-back fin under it covering only the upper `riser_cover` of the
#         riser -> a 51 mm cantilever standing over a 35 mm dark slot. A cantilever + slot
#         silhouette is *sharper* than the bare nosing it was supposed to bury, which is
#         the exact opposite of checklist item 2.
#     (b) `side_over` = +10 mm put the slab 10 mm outside the stair flank (+-1.25). Over the
#         last 25 mm of that same overhang the slab top also climbed above `_bank_top(x)`
#         (the overhang runs +X while the bank falls at SLOPE_K), so each step surfaced a
#         white tab over the stringer - "regularly, on both sides, ~7 steps" in the crop.
#   The re-cut touches snow only:
#     Bed_i   flush box, front face **at** the riser plane, top at ztop + (t - chamfer)
#     Slab_i  full-depth cap, set back from the front by `chamfer`
#     Nose_i  45 deg chamfer wedge bridging the two (a rotY box via `build_slope`, always
#             `margin=0.0` so its own front corner is its maximum x)
#   and the same three-piece profile is applied at the drop start line x=0 (PlateTop /
#   BedTop / NoseTop), where the old plate hung 60 mm over the 2.04 m drop.
#   None of these prims carries a collider (snow is a look layer here) - see `build_snow`.
# ===========================================================================
def _snow_lat():
    """(y_lo, y_hi) shared by every step-snow prim: stair width less `side_inset`."""
    st = PARAMS["stairs"]
    ins = float(PARAMS["snow"]["side_inset"])
    return st["y0"] + ins, st["y1"] - ins


def _sbox(tag, xs, ys, zs, riser=None, clip=False):
    """A snow box + the two claims made about it: `riser` = the plane its front may not
    pass, `clip` = "this one is cut to the stair width" (the tab gate's population)."""
    return dict(tag=tag, form="box", x=(min(xs), max(xs)), y=(min(ys), max(ys)),
                z=(min(zs), max(zs)), riser=riser, clip=clip)


def _swedge(tag, x_front, z0, c, ys, thick, riser=None, clip=False):
    """A 45 deg `build_slope` chamfer wedge ending exactly at `x_front`, + its AABB.

    `x0` is derived as `x_front - c` and `run` as `x_front - x0`, so `x0 + run` is
    `x_front` **bit-exactly** (Sterbenz: the difference of two nearby floats is exact, and
    adding it back is correctly rounded to the original). Writing `run = c` instead would
    let the wedge end one ulp past the riser plane and make the front gate a lie.
    Profile vertices: back-top (x0,z0), front-top (x_front, z0-c), then both dropped by
    `thick` along the face normal (-sin,-cos) - so the solid's **maximum x is its
    front-top corner**, and nothing can reach past it (given `margin=0.0` at build time).
    """
    x0 = x_front - c
    run = x_front - x0
    ang = math.atan2(run, run)                  # 45 deg by construction
    return dict(tag=tag, form="wedge", x0=x0, z0=z0, run=run, drop=run,
                thick=thick, y=(min(ys), max(ys)), riser=riser, clip=clip,
                x=(x0 - thick * math.sin(ang), x0 + run),
                z=(z0 - run - thick * math.cos(ang), z0))


def snow_solids():
    """[GT-119 ③] Every prim of the stair/approach snow layer, derived once.

    Returns a list of dicts: `form` "box" (x/y/z spans) or "wedge" (build_slope args +
    the solid's AABB in x/y/z). `riser` carries the plane the solid's front must not
    pass, for the solids that sit on a step.
    """
    st, tr, lo = PARAMS["stairs"], PARAMS["terrace"], PARAMS["lower"]
    sn = PARAMS["snow"]
    run, drop, _slope_k, _lift = _dims()
    lower_top = st["z_top"] - drop - lo["z_gap"]
    t = float(sn["thickness"])
    c = float(sn["chamfer"])
    fi = float(sn["front_inset"])
    gap = float(sn["rest_gap"])
    back = float(sn["back_bury"])
    cth = float(sn["cham_thick"])
    sy0, sy1 = _snow_lat()
    ins = 0.10          # site-boundary inset of the big plates (60 m away, never in frame)
    out = []

    # (1) Upper approach plate + the drop-edge nose. The plate stops `chamfer` short and the
    #     bed/wedge pair carries the edge, so the terrace snow no longer overhangs the drop.
    xf = st["x0"] - fi
    #     The plate must end **exactly** at the chamfer start (`xf - c`), the way each
    #     tread's Slab_i does: end it any earlier and the wedge's own back face (a 45 deg
    #     plane, not a vertical one) leaves a notch in the snow surface just before the nose.
    out.append(_sbox("PlateTop", (tr["x0"] + ins, xf - c),
                     (tr["y0"] + ins, tr["y1"] - ins),
                     (tr["z_top"] - sn["embed_plate"], tr["z_top"] + t),
                     riser=xf))
    out.append(_sbox("BedTop", (xf - c - 0.012, xf), (sy0, sy1),
                     (tr["z_top"] + gap, tr["z_top"] + t - c),
                     riser=xf, clip=True))
    out.append(_swedge("NoseTop", xf, tr["z_top"] + t, c, (sy0, sy1), cth,
                       riser=xf, clip=True))

    # (2) Per-tread bed + cap + chamfer. The last step needs no special case: its nose is
    #     swallowed by the lower approach plate (which overlaps the last 50 mm, top face
    #     2 mm lower), so the chamfer there is simply not on any silhouette.
    for i, (xa, xb, ztop) in enumerate(_steps(), 1):
        xf = xb - fi
        out.append(_sbox(f"Bed_{i}", (xa - back, xf), (sy0, sy1),
                         (ztop + gap, ztop + t - c), riser=xf, clip=True))
        out.append(_sbox(f"Slab_{i}", (xa - back, xf - c), (sy0, sy1),
                         (ztop + t - c - 0.005, ztop + t), riser=xf, clip=True))
        out.append(_swedge(f"Nose_{i}", xf, ztop + t, c, (sy0, sy1), cth,
                           riser=xf, clip=True))

    # (3) Lower approach plate (50 mm overlap with the last step · top face 2 mm lower)
    out.append(_sbox("PlateBot", (run - lo["x_back"], lo["x1"] - ins),
                     (lo["y0"] + ins, lo["y1"] - ins),
                     (lower_top - sn["embed_plate"], lower_top + t)))
    return out


# --- [GT-119 ③] object snow caps --------------------------------------------
#  Audit item C: `cap()` added +0.05 on both axes with square corners, so every bench,
#  lamp, sign, hedge and chimney wore a snow lid **wider than the thing under it**. Real
#  snow recedes from an edge (it melts and shears off first where it is unsupported), so
#  the lid now insets, and any lid big enough to show a rim gets a stepped crown - the
#  cheapest chamfer there is - instead of one square 40~60 mm corner.
SNOW_CAP_INSET = 0.020          # per-side recession from the support outline
SNOW_CAP_MIN_FRAC = 0.60        # ... but a 60 mm plank still carries a ridge of snow
SNOW_CAP_CROWN_MIN = 0.30       # crown (= 1-step chamfer) only where the rim is visible
SNOW_CAP_CROWN_INSET = 0.020


def cap_span(d, inset=SNOW_CAP_INSET):
    """Snow-cap footprint over a support of width `d`: recede `inset` per side, floored at
    SNOW_CAP_MIN_FRAC of the support so thin members keep a cap instead of a hairline."""
    return max(float(d) - 2.0 * float(inset), float(d) * SNOW_CAP_MIN_FRAC)


def cap_boxes(center, support, t, inset=SNOW_CAP_INSET):
    """[GT-119 ③] Snow-cap boxes over a support of footprint `support` = (sx, sy).

    `center`/`t` keep their old meaning (centre and thickness of the cap), so the cap's
    **top face does not move**; only the outline shrinks and the rim gains a step.
    Returns [(suffix, center, size), ...] - suffix "" is the base plate.
    """
    cx, cy, cz = [float(v) for v in center]
    sx = cap_span(support[0], inset)
    sy = cap_span(support[1], inset)
    t = float(t)
    if min(sx, sy) < SNOW_CAP_CROWN_MIN:
        return [("", (cx, cy, cz), (sx, sy, t))]
    ci = SNOW_CAP_CROWN_INSET
    base_t, crown_t = t * 0.60, t * 0.55        # 0.15 t overlap -> no coplanar joint
    return [("", (cx, cy, cz - t / 2.0 + base_t / 2.0), (sx, sy, base_t)),
            ("_Crown", (cx, cy, cz + t / 2.0 - crown_t / 2.0),
             (max(sx - 2.0 * ci, sx * 0.5), max(sy - 2.0 * ci, sy * 0.5),
              crown_t))]


def object_cap_supports():
    """(name, support_sx, support_sy, inset) for every dressing snow cap - the table the
    self-check runs `cap_boxes` over. It mirrors the call sites in `build_context` /
    `build_dressing`; both read the same PARAMS, so a parameter move shows up in both."""
    bs, lm, sp = PARAMS["bench"], PARAMS["lamp"], PARAMS["signpost"]
    hs, po = PARAMS["house"], PARAMS["pole"]
    rows = [("Pole/Cap", po["r"] * 2.0, po["r"] * 2.0, SNOW_CAP_INSET)]
    for i in range(len(PARAMS["benches"])):
        rows.append((f"Bench_{i}/SnowSeat", bs["length"], bs["width"],
                     SNOW_CAP_INSET))
        rows.append((f"Bench_{i}/SnowBack", bs["length"], 0.06, SNOW_CAP_INSET))
    for i in range(len(PARAMS["lamps"])):
        rows.append((f"Lamp_{i}/SnowHead", lm["head_w"], lm["head_l"],
                     SNOW_CAP_INSET))
        rows.append((f"Lamp_{i}/SnowTop", lm["pole_r"] * 2.0, lm["pole_r"] * 2.0,
                     SNOW_CAP_INSET))
    rows.append(("SignPost/SnowPanel", sp["panel_t"], sp["panel_w"],
                 SNOW_CAP_INSET))
    for i, hd in enumerate(PARAMS["hedges"]):
        rows.append((f"Hedge_{i}_Snow", hd["x1"] - hd["x0"], hd["y1"] - hd["y0"],
                     SNOW_CAP_INSET))
    for i, hd in enumerate(PARAMS["houses"]):
        rows.append((f"House_{i}/SnowRoof",
                     (hd["x1"] - hd["x0"]) + 2.0 * hs["eave"],
                     (hd["y1"] - hd["y0"]) + 2.0 * hs["eave"], hs["cap_inset"]))
        rows.append((f"House_{i}/SnowChimney", hs["chimney_s"], hs["chimney_s"],
                     SNOW_CAP_INSET))
    return rows


def ground_plans():
    """[W2 ground_kit] Ground plan - the scene assembly and the CPU check use the same function."""
    g = PARAMS["ground"]
    st = PARAMS["stairs"]
    tc = PARAMS["tactile"]
    x_edge = float(st["x0"])
    band = (x_edge - tc["ahead"] - tc["depth"], float(st["y0"]),
            x_edge - tc["ahead"], float(st["y1"]))
    gp = gk.plan_ground(
        "plaza_granite", region=tuple(g["region"]),
        z=float(PARAMS["terrace"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("stair_top", x_edge)],
        dists=(2, 5, 10), scene="sceneC1",
        caps=dict(weed_h=float(g["weed_h"])),
        tactile=("stair_top",) if SCENE_CONFIG["cue_tactile"] else (),
        sites=dict(manhole=[tuple(g["manhole"])], gully=[tuple(g["gully"])],
                   patch=[tuple(p) for p in g["patches"]],
                   tactile=dict(stair_top=band)),
        overrides=dict(infra=dict(manhole=1, gully=1)),
        seed=26)
    return [("terrace", gp)]


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene shots."""
    views = sc.grid_views(0.0)
    # approach: walking viewpoint on the upper terrace - the white-slope impression
    views["approach"] = dict(eye=[-6.0, 0.0, 1.65], tgt=[2.0, 0.0, -0.90])
    # grazing_top: low viewpoint - do the step edges survive only as ridge lines (top signature)
    views["grazing_top"] = dict(eye=[-2.2, 0.0, 0.35], tgt=[3.6, 0.0, -0.70])
    # rail_side: oblique from the railing/stringer side - check the only surviving cue
    views["rail_side"] = dict(eye=[-3.0, 3.2, 1.50], tgt=[2.2, 0.30, -1.20])
    # lower_lookback: looking back from below - the contrast view where the step edges show best
    views["lower_lookback"] = dict(eye=[7.0, 0.60, 1.50], tgt=[-1.0, 0.0, 0.20])
    return views


# ===========================================================================
# [C3] [GT-119 ③] snow_selfcheck - R-1 drop-registry print + the snow-layer gates.
#   CPU only, no Isaac, no GPU:  NEGOBS_SELFCHECK=1 python3 sceneC1_snow_stairs.py
#   The same function arms NEGOBS_SMOKE (GT-89's pre-boot gate), so the ledger's
#   "before/after bit identity" evidence is produced by the smoke floor itself.
#
#   `_DROP_REG_FROZEN` is the **pre-GT-119 derivation**, captured from the very
#   `sc._stair_steps` call this file has always made. GT-119's invariant is that the
#   concrete stair, the tread z, the drop line and the nosing prims do not move while the
#   snow is re-cut, so the comparison is exact float identity, not a tolerance.
# ===========================================================================
_DROP_REG_FROZEN = dict(
    kind="T1 straight flight · 12 x (riser 0.170 / tread 0.300)",
    nsteps=12,
    run=3.5999999999999996,
    drop=2.04,
    top_edge_x=0.0,
    top_edge_z=0.0,
    lower_z=-2.042,
    corridor=(-1.25, 1.25),
    steps=[(0.0, 0.3, -0.17), (0.3, 0.6, -0.34), (0.6, 0.8999999999999999, -0.51),
           (0.8999999999999999, 1.2, -0.68), (1.2, 1.5, -0.8500000000000001),
           (1.5, 1.8, -1.02), (1.8, 2.1, -1.19), (2.1, 2.4, -1.3599999999999999),
           (2.4, 2.6999999999999997, -1.5299999999999998),
           (2.6999999999999997, 2.9999999999999996, -1.6999999999999997),
           (2.9999999999999996, 3.2999999999999994, -1.8699999999999997),
           (3.2999999999999994, 3.599999999999999, -2.0399999999999996)],
    nosing_x=[0.27499999999999997, 0.575, 0.8749999999999999, 1.175, 1.475,
              1.7750000000000001, 2.075, 2.375, 2.675, 2.9749999999999996,
              3.2749999999999995, 3.5749999999999993],
    nosing_z=[-0.169, -0.339, -0.509, -0.679, -0.8490000000000001,
              -1.0190000000000001, -1.189, -1.359, -1.529, -1.6989999999999998,
              -1.8689999999999998, -2.0389999999999997],
    nosing_y=(-1.23, 1.23),
)


def drop_registry():
    """Re-derive the hazard/drop registry from the geometry that is actually built.

    Nothing here is restated from a constant: the steps come from the same
    `sc._stair_steps` call `build_stairs` makes, and the nosing rows from the same
    (`xb - width/2`, `ztop + proud`) the `sc.build_nosing` loop makes. If a stair or
    nosing parameter moved, these rows move and the identity assertion is what fails.
    """
    st, ns = PARAMS["stairs"], PARAMS["nosing"]
    run, drop, _k, _lift = _dims()
    steps = _steps()
    return dict(
        kind="T1 straight flight · %d x (riser %.3f / tread %.3f)"
             % (st["nsteps"], st["riser"], st["tread"]),
        nsteps=st["nsteps"], run=run, drop=drop,
        top_edge_x=float(st["x0"]), top_edge_z=float(st["z_top"]),
        lower_z=st["z_top"] - drop - PARAMS["lower"]["z_gap"],
        corridor=(float(st["y0"]), float(st["y1"])),
        steps=[(xa, xb, zt) for (xa, xb, zt) in steps],
        nosing_x=[xb - ns["width"] / 2.0 for (_xa, xb, _zt) in steps],
        nosing_z=[zt + ns["proud"] for (_xa, _xb, zt) in steps],
        nosing_y=(st["y0"] + ns["y_inset"], st["y1"] - ns["y_inset"]),
    )


def _top_margin_vs_bank(s):
    """How far a snow solid's top face stays **below** the bank/stringer plane, worst point.

    box   : the top is flat, the bank falls with +x -> the worst point is the solid's x_hi.
    wedge : the top falls at 45 deg while the bank falls at SLOPE_K < 1, so the margin only
            grows with x -> the worst point is the back-top corner (x0, z0).
    Negative means a corner of that solid has surfaced above the bank = the white tab.
    """
    if s["form"] == "wedge":
        return _bank_top(s["x0"]) - s["z0"]
    return _bank_top(s["x"][1]) - s["z"][1]


def snow_selfcheck(verbose=True):
    """[GT-119 ③] R-1 registry identity + the snow-layer gates. Returns (ok, npass, ntot)."""
    st, sn, bk = PARAMS["stairs"], PARAMS["snow"], PARAMS["bank"]
    reg = drop_registry()
    solids = snow_solids()
    on_stair = [s for s in solids if s.get("riser") is not None]
    clipped = [s for s in solids if s.get("clip")]
    fails = []
    rows = []
    #  In the twin (`snow_cover=False`) no snow prim is built and LIFT drops to 0, so the
    #  four gates that measure the snow **against the bank/stair** have no subject. They
    #  are reported SKIP rather than evaluated - a twin run must not fail the smoke floor.
    snow_on = bool(SCENE_CONFIG["snow_cover"])

    def chk(tag, ok, msg="", skip=False):
        rows.append((tag, None if skip else bool(ok), msg))
        if not skip and not ok:
            fails.append(tag)

    # --- 1. drop registry: before/after bit identity ----------------------
    diff = [k for k in _DROP_REG_FROZEN
            if _DROP_REG_FROZEN[k] != reg.get(k)]
    chk("낙차 레지스트리 = GT-119 이전 유도값과 비트 동일 (콘크리트 계단·답면 z·"
        "노징 프림 불변)", not diff,
        "동일 필드 %d/%d" % (len(_DROP_REG_FROZEN) - len(diff),
                             len(_DROP_REG_FROZEN))
        + ("" if not diff else " · 불일치 " + ", ".join(diff)))

    # --- 2. snow front face never passes the riser plane ------------------
    fr = min((s["riser"] - s["x"][1] for s in on_stair), default=9.9)
    chk("계단 눈 전면 ≤ 라이저 평면 (구 nose_over +60mm 캔틸레버 소멸)",
        fr >= -1e-9,
        "최소 여유 %+.1f mm · 프림 %d (0.0 = flush 설계값, 허용 1 nm = ulp)"
        % (fr * 1000.0, len(on_stair)), skip=not snow_on)
    chk("front_inset ≥ 0 · 0 < chamfer < thickness",
        sn["front_inset"] >= 0.0 and 0.0 < sn["chamfer"] < sn["thickness"],
        "front_inset %.3f · chamfer %.3f < thickness %.3f"
        % (sn["front_inset"], sn["chamfer"], sn["thickness"]))

    # --- 3. y extent: inside the stair flank, still overlapping the bank ---
    ymax = max(max(abs(s["y"][0]), abs(s["y"][1])) for s in clipped)
    chk("계단 눈 y 폭 ≤ 계단 폭 − 0.010 (스트링어 위 흰 탭 소멸)",
        ymax <= st["y1"] - 0.010 + 1e-12,
        "|y|max %.4f ≤ %.4f · 프림 %d (인셋 %.0f mm)"
        % (ymax, st["y1"] - 0.010, len(clipped), sn["side_inset"] * 1000.0),
        skip=not snow_on)
    chk("눈이 뱅크 안쪽면(±%.3f)까지는 닿는다 — 측면 콘크리트 노출 0"
        % (st["y1"] - bk["y_in_over"]),
        ymax >= st["y1"] - bk["y_in_over"] - 1e-12
        and sn["side_inset"] <= bk["y_in_over"] + 1e-12,
        "겹침 %+.1f mm" % ((ymax - (st["y1"] - bk["y_in_over"])) * 1000.0),
        skip=not snow_on)

    # --- 4. no snow corner above the bank/stringer plane ------------------
    #   Only the stair-width solids can produce a tab: they are the ones that reach past
    #   the flank (+-1.235 > bank y_in 1.23). The two big approach plates are terrain, and
    #   the lower one deliberately covers the bank's run-out tail.
    tab = min(_top_margin_vs_bank(s) for s in clipped)
    worst = min(clipped, key=_top_margin_vs_bank)["tag"]
    chk("눈 상면 ≤ 뱅크/스트링어 평면 (탭 발생 기구 자체가 음수)",
        tab >= 0.0, "최소 여유 %+.1f mm @ %s" % (tab * 1000.0, worst),
        skip=not snow_on)

    # --- 5. the resting gap and what it has to clear ----------------------
    chk("rest_gap > 노징 돌출(proud) — 베드가 노징 위에 얹힌다",
        sn["rest_gap"] > PARAMS["nosing"]["proud"],
        "%.1f mm > %.1f mm" % (sn["rest_gap"] * 1000.0,
                               PARAMS["nosing"]["proud"] * 1000.0))
    #  Anything the terrace kit leaves proud under the drop-edge nose must fit inside
    #  the same gap, or it would spear through the 20 mm nose block.
    nose_x0 = st["x0"] - sn["front_inset"] - sn["chamfer"] - 0.012
    sy0, sy1 = _snow_lat()
    (_tag, gp), = ground_plans()
    under = [e for e in gp["elements"]
             if e["aabb"][3] > nose_x0 and e["aabb"][0] < st["x0"]
             and e["aabb"][4] > sy0 and e["aabb"][1] < sy1]
    worst_p = max([e["proud"] for e in under], default=0.0)
    chk("낙차선 코 밑(x %.3f…%.3f) ground_kit proud < rest_gap"
        % (nose_x0, st["x0"]),
        worst_p < sn["rest_gap"],
        "요소 %d · proud max %.1f mm < %.1f mm"
        % (len(under), worst_p * 1000.0, sn["rest_gap"] * 1000.0))

    # --- 6. object snow caps recede from their support --------------------
    over = []
    for name, sx, sy, inset in object_cap_supports():
        cx = cap_span(sx, inset) - sx
        cy = cap_span(sy, inset) - sy
        over.append((max(cx, cy), name))
    worst_c = max(over)
    chk("물체 눈 캡이 지지체보다 크지 않다 (구 +0.05 돌출 → 음의 인셋)",
        worst_c[0] < 0.0,
        "최악 %+.1f mm @ %s · 캡 %d개" % (worst_c[0] * 1000.0, worst_c[1],
                                          len(over)))

    live = [r for r in rows if r[1] is not None]
    npass = len([r for r in live if r[1]])
    if verbose:
        print("=" * 72)
        print("sceneC1 [GT-119 ③] 눈 형상 재절단 자기검산 (부팅 0 · GPU 0)")
        print("=" * 72)
        print("[1] 위험/낙차 레지스트리 — 이번 수리에서 이동 0 (재유도값)")
        print(f"    유형          {reg['kind']}")
        print(f"    단수/런/낙차  {reg['nsteps']}단 · run {reg['run']:.3f} · "
              f"drop {reg['drop']:.3f}")
        print(f"    낙차 시작선   x={reg['top_edge_x']:.3f} · z={reg['top_edge_z']:.3f}"
              f" → 하부 z={reg['lower_z']:.3f} · 회랑 |y| ≤ {reg['corridor'][1]:.2f}")
        print("    답면 상단 z   "
              + ", ".join(f"{s[2]:.3f}" for s in reg["steps"]))
        print("    노징 x 중심   "
              + ", ".join(f"{x:.3f}" for x in reg["nosing_x"]))
        print(f"    동결값 대조   {'동일' if not diff else '불일치 ' + str(diff)}"
              " (repr 수준 · 허용오차 없음)")
        print("[2] 눈층 (프림 %d · 콜라이더 0 — 눈은 룩 레이어)%s"
              % (len(solids),
                 "" if snow_on else "  ※ 트윈 팔: 미생성, 형상 게이트 SKIP"))
        print(f"    두께 {sn['thickness']:.3f} · 모따기 {sn['chamfer']:.3f}@45° · "
              f"전면 인셋 {sn['front_inset']:.3f} · 측면 인셋 "
              f"{sn['side_inset']:.3f} · 안착 간극 {sn['rest_gap']:.3f}")
        print(f"    단 코 실루엣: 수직면 {(sn['thickness'] - sn['chamfer']) * 1000:.0f}"
              f"mm + 45° 모따기 {sn['chamfer'] * 1000:.0f}mm "
              f"(구: 60mm 캔틸레버 + 35mm 그림자 슬롯)")
        print("[3] 게이트")
        for tag, ok, msg in rows:
            mark = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
            print(f"  [{mark}] {tag}" + (f" — {msg}" if msg else ""))
        # --- consequence the ruling has to see (not a gate) ---------------
        #   Snow that hides a face lying **on** the riser plane would have to be proud of
        #   that plane, which the ruling forbids - so the measurement is reported, not
        #   engineered away. `n_exp` excludes the noses the lower approach plate swallows.
        ns = PARAMS["nosing"]
        pb = [s for s in solids if s["tag"] == "PlateBot"][0]
        n_exp = sum(1 for (_xa, xb, zt) in reg["steps"]
                    if not (xb - ns["width"] >= pb["x"][0] - 1e-9
                            and zt + ns["proud"] <= pb["z"][1] + 1e-9))
        print("[4] 주의(게이트 아님) — 전면 flush 의 대가")
        print(f"    라이저 평면이 눈에 덮이지 않으므로 노징 띠 전면 "
              f"{(ns['proud'] + 0.005) * 1000:.0f}mm 가 x=xb 평면에 노출된다 "
              f"({n_exp}단 · 나머지는 하부 평판에 매몰). "
              f"상류 시점(approach·grazing_top·grid)에서는 답면 눈(베드)에 "
              f"가려 보이지 않고 lower_lookback 에서만 보인다 "
              f"(단 경사 29.5° > 각 시점 부각 11.8~22.4°).")
        print("    처분 선택지: (a) 그대로 수용 (b) 눈 전면에 0.2mm 실링 물림 "
              "(front_inset=-0.0002) (c) 이 팔에서 cue_nosing=False. "
              "— 지시가 'never proud' 이므로 기본값은 (a).")
        print("-" * 72)
        print(f"게이트 {npass}/{len(live)} PASS"
              + (f" · SKIP {len(rows) - len(live)}"
                 if len(live) != len(rows) else ""))
    return (not fails), npass, len(live)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / grid    — 상부 테라스·계단·하부 평지가 하나의 백색면으로 읽히는가
 2. grazing_top·h0.3   — 단 에지가 둥근 융기선으로만 암시되는가(특색 1순위)
 3. rail_side          — 난간·콘크리트 스트링어가 유일 단서로 잔존하는가
 4. snow_cover ON/OFF  — 눈 제거 시 계단 코어 기하(단 위치·낙차) 불변인가
 5. 조명               — 무태양 저대비인가(경질 그림자 0), 눈 과노출/흑화 없는가
 6. 재질·Z파이팅       — 눈/콘크리트 경계, 모따기 웨지, 평판 이음에 깜빡임 없는가
 7. lower_lookback     — [GT-119 ③] 단 코가 45° 모따기 능선인가(캔틸레버·그림자 슬롯 0),
                         스트링어 위 흰 탭 0인가
 8. 검산               — NEGOBS_SELFCHECK=1 python3 sceneC1_snow_stairs.py"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    # [GT-119 ③] The gate now *measures* the snow layer instead of only announcing the
    # early exit: the registry identity + the 9 snow gates are what the §2.2 smoke floor
    # runs, so a shape regression fails on a GPU-less machine.
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        _ok, _np, _nt = snow_selfcheck(verbose=True)
        sys.exit(0 if _ok else 1)
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        _ok, _np, _nt = snow_selfcheck(verbose=False)
        print("SMOKE_%s %s pre-boot gate (GT-89) gates=%d/%d"
              % ("OK" if _ok else "FAIL", os.path.basename(__file__), _np, _nt))
        if not _ok:
            snow_selfcheck(verbose=True)
            sys.exit(1)
        return
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
    UsdGeom.Xform.Define(stage, "/World/Scene26")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene26"

    RUN, DROP, SLOPE_K, LIFT = _dims()
    LOWER_TOP = PARAMS["stairs"]["z_top"] - DROP - PARAMS["lower"]["z_gap"]

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
        M["concrete"] = PBR(
            f"{ROOT}/Looks/Concrete", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        M["stair"] = PBR(
            f"{ROOT}/Looks/Stair", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"],
            tint=mp["stair_tint"])
        M["dirt"] = PBR(
            f"{ROOT}/Looks/Dirt", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            sca["dirt_park"], tint=mp["dirt_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"], tint=mp["wall_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # Snow: constant high albedo + ultra rough + low specular (geometry-map spec)
        M["snow"] = PBR(f"{ROOT}/Looks/Snow",
                        diffuse_color=mp["snow_color"],
                        roughness_const=mp["snow_rough"], metallic=0.0,
                        specular_level=mp["snow_spec"])
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = PBR(f"{ROOT}/Looks/GKitIron",
                            diffuse_color=(0.10, 0.10, 0.105),
                            metallic=0.55, roughness_const=0.55)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ context dressing v2 materials (constant colours only - no new texture dependency) ─
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["roof"] = PBR(f"{ROOT}/Looks/Roof", diffuse_color=mp["roof_color"],
                        roughness_const=mp["roof_rough"])
        # [v5.1 §4] The 4 distant houses share the same roof/wall material, which gives a
        #   'cloned block' impression -> deterministic +-5% tint jitter per house.
        #   · The roof uses diffuse_color (albedo 0.045) -> unaffected by the cap.
        #   · The wall only shifts the tint multiplier of the brick texture (the texture itself is shared).
        for _i, _hd in enumerate(PARAMS["houses"]):
            _kx, _ky = _hd["x0"], _hd["y0"]
            M[f"roof_{_i}"] = PBR(
                f"{ROOT}/Looks/Roof_{_i}",
                diffuse_color=bc.jit_tint(mp["roof_color"], _kx, _ky,
                                          "roofC1", amp=0.05),
                roughness_const=mp["roof_rough"])
            M[f"brick_{_i}"] = PBR(
                f"{ROOT}/Looks/Brick_{_i}", sc.tex_path("brick_red", "diff"),
                sc.tex_path("brick_red", "nor"),
                sc.tex_path("brick_red", "rough"), sca["brick_red"],
                tint=bc.jit_tint(mp["wall_tint"], _kx, _ky, "wallC1",
                                 amp=0.05))
        M["hedge"] = PBR(f"{ROOT}/Looks/Hedge", diffuse_color=mp["hedge_color"],
                         roughness_const=mp["hedge_rough"], specular_level=0.0)
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=0.5)
        return M

    # -------------------------------------------------------------------
    # Terrain - upper terrace / lower ground / snow banks on both sides / concrete stringers
    #   It is an embankment form with no opening (pit), so there is nothing to split into 4 boxes. Instead the three
    #   solids overlap and tile -> no plane covering a cavity and no floating edge.
    # -------------------------------------------------------------------
    def build_terrace(M):
        tr = PARAMS["terrace"]
        # [W2-0 · P-A] The terrace top face is what ground_kit decorates -> displacement skin
        #   OFF (registered **before the BOX call**). This keeps the kit elements from being
        #   swallowed by the skin (+6.5~16.5 mm) in the `snow_cover=False` twin `[spec §1.1]`.
        sc.skin_exclude(f"{ROOT}/Terrace")
        BOX(f"{ROOT}/Terrace",
            ((tr["x0"] + tr["x1"]) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
             tr["z_top"] - tr["thick"] / 2.0),
            (tr["x1"] - tr["x0"], tr["y1"] - tr["y0"], tr["thick"]),
            M["concrete"], col=True)

    def build_lower(M):
        lo = PARAMS["lower"]
        x0 = RUN - lo["x_back"]
        BOX(f"{ROOT}/LowerPlain",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             LOWER_TOP - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["concrete"], col=True)

    def build_banks(M):
        """Slopes on both sides. Top face z = LIFT − SLOPE_K·x (nosing line + snow depth)."""
        bk = PARAMS["bank"]
        st = PARAMS["stairs"]
        mtl = M["snow"] if cfg["snow_cover"] else M["dirt"]
        x0 = st["x0"] - bk["x_head"]
        z0 = LIFT + SLOPE_K * bk["x_head"]
        run = RUN + bk["x_head"] + bk["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            y_in = sgn * (st["y1"] - bk["y_in_over"])   # 2cm bite into the stair solid
            y_out = sgn * bk["y_out"]
            sc.build_slope(stage, f"{ROOT}/Bank_{tag}", x0, z0, run,
                           run * SLOPE_K, min(y_in, y_out), max(y_in, y_out),
                           bk["thick"], mtl, margin=0.0, collider=True)

    def build_stringers(M):
        """Exposed stringer on the stair flank - top face = bank face + proud."""
        sg = PARAMS["stringer"]
        st = PARAMS["stairs"]
        x0 = st["x0"] - sg["x_head"]
        z0 = LIFT + SLOPE_K * sg["x_head"] + sg["proud"]
        run = RUN + sg["x_head"] + sg["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a = sgn * sg["y_in"]
            b = sgn * sg["y_out"]
            sc.build_slope(stage, f"{ROOT}/Stringer_{tag}", x0, z0, run,
                           run * SLOPE_K, min(a, b), max(a, b), sg["thick"],
                           M["concrete"], margin=0.0, collider=True)

    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False control: z=0 flat throughout (+ a snow plate)."""
        tr = PARAMS["terrace"]
        # [W2-0 · P-A] The ground elements are laid in the control too (the only difference in the
        #   twin comparison must be the **drop geometry**) -> skin OFF on the flat plate as well.
        sc.skin_exclude(f"{ROOT}/FlatFill")
        lo = PARAMS["lower"]
        x0, x1 = tr["x0"], lo["x1"]
        BOX(f"{ROOT}/FlatFill",
            ((x0 + x1) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
             tr["z_top"] - tr["thick"] / 2.0),
            (x1 - x0, tr["y1"] - tr["y0"], tr["thick"]),
            M["concrete"], col=True)
        if cfg["snow_cover"]:
            sn = PARAMS["snow"]
            z_hi = tr["z_top"] + sn["thickness"]
            z_lo = tr["z_top"] - sn["embed_plate"]
            BOX(f"{ROOT}/Snow/FlatPlate",
                ((x0 + x1) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
                 (z_hi + z_lo) / 2.0),
                (x1 - x0, tr["y1"] - tr["y0"], z_hi - z_lo), M["snow"])

    # -------------------------------------------------------------------
    # Snow layer [signature] - emits `snow_solids()` (see [B2] for the shape and the
    #   GT-119 ③ reasoning). Nothing is computed here: the same list the self-check
    #   measures is the list that gets built.
    #   **Colliders: none.** Every box goes through BOX(col=False) and every wedge through
    #   build_slope(collider=False), which is what the pre-GT-119 layer did too - the snow
    #   is a look layer, the walked/collided surfaces are the concrete stair, the banks and
    #   the two ground plates. So this repair moves no collision extent at all.
    # -------------------------------------------------------------------
    def build_snow(M):
        sn = PARAMS["snow"]
        n_box = n_wedge = 0
        for s in snow_solids():
            path = f"{ROOT}/Snow/{s['tag']}"
            if s["form"] == "box":
                (xa, xb), (ya, yb), (za, zb) = s["x"], s["y"], s["z"]
                BOX(path, ((xa + xb) / 2.0, (ya + yb) / 2.0, (za + zb) / 2.0),
                    (xb - xa, yb - ya, zb - za), M["snow"])
                n_box += 1
            else:
                # margin=0.0 is load-bearing: the default 0.3 would extend the wedge
                # 0.15 past both ends and put the chamfer back over the riser plane.
                sc.build_slope(stage, path, s["x0"], s["z0"], s["run"], s["drop"],
                               s["y"][0], s["y"][1], s["thick"], M["snow"],
                               margin=0.0, collider=False)
                n_wedge += 1
        print(f"[눈층] 박스 {n_box} · 45° 모따기 웨지 {n_wedge} · 전면 = 라이저 평면 "
              f"−{sn['front_inset'] * 1000.0:.0f}mm · 측면 인셋 "
              f"{sn['side_inset'] * 1000.0:.0f}mm · 콜라이더 0")

    def build_rail_snow(M):
        """Snow strip on top of the railing - horizontal extension (box) + sloped part (build_slope thin plate)."""
        sn = PARAMS["snow"]
        rl = PARAMS["rail"]
        top0 = LIFT + rl["rail_h"]                     # rail centre z at x=0
        z_top = top0 + rl["rail_r"] + sn["rail_strip_lift"]
        w = sn["rail_strip_w"]
        th = sn["rail_strip_t"]
        # Horizontal part: x_start..x0+0.03 (3cm overlap with the sloped part, top face 2mm lower -> no coplanar face)
        hx1 = PARAMS["stairs"]["x0"] + 0.03
        BOX(f"{ROOT}/Snow/RailStripFlat",
            ((rl["x_start"] + hx1) / 2.0, rl["y"], z_top - 0.002 - th / 2.0),
            (hx1 - rl["x_start"], w, th), M["snow"])
        # [v3 arm C] the strip lies ON the rail, so it takes the rail's drop: in
        #   arm C `build_cues` builds the rail level (drop 0), and a strip still
        #   descending 2.04 m would leave it and bury itself in the flat plate.
        #   `z_top` is derived from LIFT + rail_h above, which is unchanged.
        #   Flag off ⇒ `DROP`, unchanged.
        sc.build_slope(stage, f"{ROOT}/Snow/RailStripSlope", 0.0, z_top,
                       RUN, (0.0 if KEEP_DRESSING else DROP),
                       rl["y"] - w / 2.0, rl["y"] + w / 2.0,
                       th, M["snow"], margin=0.0, collider=False)

    # -------------------------------------------------------------------
    # cues - nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        # [v3 arm C · DECLARED LIMIT] the nosing is one anti-slip band per TREAD,
        #   authored from `z_top` downwards at −0.17·i. In this arm the run is
        #   filled by a 2.60 m thick plate topped at 0.000, so every band below the
        #   first is inside that solid and renders 0 px. A nosing marks a step edge
        #   and this arm has no step edges, so it is skipped rather than authored
        #   invisible. The scene's other HZ-bound cue, the railing, IS kept (level,
        #   below), and `cue_tactile` was never hazard-bound — `ground_plans()`
        #   emits the stair-head band from `build_ground_kit`, which every arm
        #   calls. Flag off ⇒ the branch runs as before.
        if cfg["cue_nosing"] and not KEEP_DRESSING:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"],
                st["y0"] + ns["y_inset"], st["y1"] - ns["y_inset"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])
        # [W2 §12.4] The tactile paving is **enforced by ground_kit** (`build_ground_kit`).
        #   Laying it again here would double it up in the same place. The toggle (`cue_tactile`) is
        #   read as-is by `ground_plans()`, so the ablation path is unchanged.
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]

            def bank_ground(x):
                """Bank top face (the landing surface for the railing posts)."""
                if KEEP_DRESSING:
                    # [v3 arm C] the fill IS the ground here and it is level, so
                    #   the landing surface is the snow top LIFT everywhere —
                    #   which is exactly what this function already returns for
                    #   x <= 0 (sceneC2:941 `terrain_z`, the identical construct).
                    return LIFT
                if x <= 0.0:
                    return LIFT
                return LIFT - SLOPE_K * min(x, RUN)

            # [v3 arm C] `DROP` is what tilts the rail: `build_railing_line` lays
            #   the top/mid tubes from `run`/`drop` and uses `ground_fn` only for
            #   the post and picket feet (scene_common:2471-2489). Flattening the
            #   ground alone would leave the tube diving into the plate while its
            #   posts stood on it, so the two switches are one change: no drop, no
            #   slope. The rail keeps y 1.60, x_start −1.20, its 0.90 m height
            #   over the walking surface and its statutory picket pitch, so the
            #   (A,C) cue mask keeps its pixels.
            sc.build_railing_line(
                stage, f"{ROOT}/StairRail_P", rl["y"], rl["x_start"],
                st["x0"], RUN, (0.0 if KEEP_DRESSING else DROP), bank_ground,
                M["rail"],
                rail_h=rl["rail_h"], post_r=rl["post_r"],
                spacing=rl["spacing"], rail_r=rl["rail_r"],
                rail_mid_r=rl["rail_mid_r"],
                rail_mid_drop=rl["rail_mid_drop"])
            if cfg["snow_cover"]:
                build_rail_snow(M)

    # -------------------------------------------------------------------
    # [W2] ground_kit - P1 plaza_granite. **Split into 2 layers.**
    #   (1) Paving layer (z = terrace top 0.0): joints · manhole · gully · patches · cracks · stains ·
    #      weeds · tactile paving. It sits under 0.05 of snow, so with `snow_cover=True` it is all
    #      buried and only shows in the twin (False) - that is this scene's signature (§7.3 B12).
    #   (2) Snow surface layer (z = LIFT): **cleared-snow traces** - wear lane + footprints.
    #      The plan is single-z so it cannot go in the same call as (1); the builders are called directly
    #      (the same exception route as the "bend-group local grating" of pilot #2).
    #      GT: proud 0.0006 m - not a drop, and it also passes the B12 snow cap of 0.05.
    # -------------------------------------------------------------------
    def build_ground_kit(M, lift):
        g = PARAMS["ground"]
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["stair"], crack=M["stair"], patch=M["concrete"],
                  patch_cut=M["stair"], manhole=M["gk_iron"], gully=M["gk_iron"],
                  gutter=M["concrete"], weed=M["dirt"], tactile=M["tactile"],
                  stain_dirt=M["dirt"], stain_water=M["stair"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_trace = 0
        # With `NEGOBS_GKIT=0` (the C2 A/B OFF arm) the direct calls outside the plan must be turned off too,
        #   so that the only A/B difference stays "kit prims present or not" `[spec §7.5 A3]`.
        if cfg["snow_cover"] and gk.GKIT_ON:
            (ax, ay), (bx, by) = g["trace_lane"]
            r1 = gk.build_wear_lane(kit, f"{ROOT}/GKit/SnowTrace/Lane",
                                    ((ax, ay), (bx, by)), lift, M["concrete"],
                                    width=float(g["trace_lane_w"]),
                                    albedo_gain=float(g["trace_lane_gain"]))
            r2 = gk.build_footprints(kit, f"{ROOT}/GKit/SnowTrace/Steps",
                                     [tuple(p) for p in g["trace_path"]],
                                     lift, M["dirt"],
                                     n=int(g["trace_steps"]), seed=26)
            n_trace = r1["prim_count"] + r2["prim_count"]
        print(f"[ground_kit] sceneC1 P1 · 프림 {res['prims']} + 제설흔적 "
              f"{n_trace} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Dressing - cleared snow piles · marker post · 2 distant buildings (horizon closure §A-4)
    # -------------------------------------------------------------------
    def build_dressing(M):
        pile_mtl = M["snow"] if cfg["snow_cover"] else M["dirt"]
        # All the dressing sits on the upper terrace (x<0) - prevents floating over the bank slope.
        base_top = LIFT
        for i, pd in enumerate(PARAMS["piles"]):
            s = pd["s"]
            for j, (dx, dy, rxy, rz) in enumerate(PARAMS["pile"]["blobs"]):
                sc.add_sphere(stage, f"{ROOT}/Pile_{i}_{j}",
                              (pd["cx"] + dx * s, pd["cy"] + dy * s,
                               base_top + rz * s * 0.35),
                              (rxy * s, rxy * s * 0.8, rz * s * 0.55),
                              pile_mtl)
        po = PARAMS["pole"]
        CYL(f"{ROOT}/Pole", (po["cx"], po["cy"], base_top + po["h"] / 2.0),
            po["r"], po["h"], M["rail"], col=True)
        if cfg["snow_cover"]:
            # [GT-119 ③] was r*2.4 = 20 % wider than the post it sits on
            for _sfx, _c, _s in cap_boxes(
                    (po["cx"], po["cy"],
                     base_top + po["h"] + po["cap_t"] / 2.0 - 0.01),
                    (po["r"] * 2.0, po["r"] * 2.0), po["cap_t"]):
                BOX(f"{ROOT}/Snow/PoleCap{_sfx}", _c, _s, M["snow"])
        # Distant buildings - C(+X) is plinthed on the lower ground, D(-X) at terrace level
        # [v3 arm C] this line is ALREADY the `Z_LOW` datum switch (sceneC2:666) and
        #   it keys on the right thing: arm C renders with `hazard_stairs=False`, so
        #   it yields 0.0 = the top of `build_flat_fill`'s plate, and building C sits
        #   on the fill instead of 2.042 m under it. No `KEEP_DRESSING` term is
        #   needed or wanted here — adding one could only make the two hazard-off
        #   arms disagree about where the ground is.
        low_base = LOWER_TOP if cfg["hazard_stairs"] else 0.0
        for key, bd in PARAMS["buildings"].items():
            b = dict(bd)
            b["base_z"] = low_base if key == "C" else 0.0
            sc.build_building(stage, f"{ROOT}/Building_{key}", b,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_context(M)

    # -------------------------------------------------------------------
    # Context dressing v2 - benches · street lamps · signpost · hedges · low-rise houses
    #   Every element builds the "winter residential/campus back stair" situation. The stairs, snow layer
    #   and lighting parameters are unchanged, and every new prim stands only on a flat face (terrace z=LIFT /
    #   lower ground z=LOWER_TOP+LIFT) - nothing floats over the bank slope.
    #   The snow caps follow the snow_cover toggle -> geometry stays consistent in the twin (bare stairs) too.
    # -------------------------------------------------------------------
    def build_context(M):
        # [v3 arm C] same reading as `low_base` in `build_dressing`: already the
        #   `Z_LOW` switch, already correct for arm C (hazard_stairs=False ⇒
        #   0.0 + LIFT = the flat snow plate's top), so the benches, lamps, hedges
        #   and low-rise houses on the "lower" side ride the fill and none of them
        #   is a lower-anchor risk. Left untouched.
        low_top = (LOWER_TOP if cfg["hazard_stairs"] else 0.0) + LIFT

        def base_of(kind):
            return LIFT if kind == "upper" else low_top

        def cap(path, center, support, t, inset=SNOW_CAP_INSET):
            """Snow cap - created only when snow_cover is ON (twin consistency).

            [GT-119 ③] `support` is the footprint of the thing being capped, **not** the
            cap size: `cap_boxes` insets from it (audit item C - the old +0.05 on both
            axes made every lid overhang its own object) and adds a stepped crown where
            the rim is big enough to read.
            """
            if cfg["snow_cover"]:
                for sfx, ctr, size in cap_boxes(center, support, t, inset):
                    BOX(path + sfx, ctr, size, M["snow"])

        # (1) Bench (seat + 4 legs + back) - snow caps on the seat and the top of the back
        bs = PARAMS["bench"]
        for i, bd in enumerate(PARAMS["benches"]):
            bz = base_of(bd["base"])
            pfx = f"{ROOT}/Bench_{i}"
            # [W3 CB-3 · J-3/J-4 abolished, spec §1.2 / §10.1] Was +-0.18 m / +-3~8 deg
            #   coordinate-hash jitter. Bench 0 stands by the snow pile and the stair shoulder,
            #   bench 1 next to snow pile 0; each now sits at its nominal centre on its anchor's
            #   bearing, which RESTORES the 0.22 m clearance the jitter was trimmed to fit inside.
            #   This is a CB-3 GATE-1 pilot scene.
            sc.build_bench(stage, pfx, bd["cx"], bd["cy"], bz,
                           M["wood"], length=bs["length"], width=bs["width"],
                           height=bs["height"], yaw=bd["yaw"])
            # The child prims below are in the build_bench root Xform local frame (rotation inherited)
            back_y = -(bs["width"] / 2.0 - 0.04)
            BOX(f"{pfx}/Back", (0.0, back_y, bs["height"] + bs["back_h"] / 2.0),
                (bs["length"], 0.06, bs["back_h"]), M["wood"])
            cap(f"{pfx}/SnowSeat",
                (0.0, 0.0, bs["height"] + bs["cap_t"] / 2.0 - 0.012),
                (bs["length"], bs["width"]), bs["cap_t"])
            cap(f"{pfx}/SnowBack",
                (0.0, back_y,
                 bs["height"] + bs["back_h"] + bs["cap_t"] / 2.0 - 0.012),
                (bs["length"], 0.06), bs["cap_t"])

        # (2) Street lamp (pole + one-sided arm + head) - snow caps on the pole top and the head
        lm = PARAMS["lamp"]
        for i, ld in enumerate(PARAMS["lamps"]):
            bz = base_of(ld["base"])
            pfx = f"{ROOT}/Lamp_{i}"
            # [W3 CB-3 · J-4 abolished] Was +-0.15 m position jitter. The lamp returns to its
            #   nominal centre; the shadow still falls only on the x<0 terrace (shadow direction
            #   (−0.879,+0.477), length 8.5 m), so the concealment condition on the stair treads
            #   is unchanged — the jitter only ever moved it inside that envelope.
            cx, cy, arm = ld["cx"], ld["cy"], ld["arm"]
            CYL(f"{pfx}/Pole", (cx, cy, bz + lm["pole_h"] / 2.0),
                lm["pole_r"], lm["pole_h"], M["pole"], col=True)
            # The arm is a horizontal cylinder running +Y/−Y -> rotX 90 deg (axis Z->Y)
            CYL(f"{pfx}/Arm", (cx, cy + arm / 2.0, bz + lm["pole_h"] - 0.10),
                lm["arm_r"], abs(arm), M["pole"], rotX=90.0)
            hy = cy + arm
            BOX(f"{pfx}/Head", (cx, hy, bz + lm["pole_h"] - 0.18),
                (lm["head_w"], lm["head_l"], lm["head_h"]), M["lamp"])
            cap(f"{pfx}/SnowHead",
                (cx, hy, bz + lm["pole_h"] - 0.18 + lm["head_h"] / 2.0
                 + lm["cap_t"] / 2.0 - 0.010),
                (lm["head_w"], lm["head_l"]), lm["cap_t"])
            cap(f"{pfx}/SnowTop",
                (cx, cy, bz + lm["pole_h"] + lm["cap_t"] / 2.0 - 0.010),
                (lm["pole_r"] * 2.0, lm["pole_r"] * 2.0), lm["cap_t"])

        # (3) Signpost (information sign) - snow cap on top of the panel
        sp = PARAMS["signpost"]
        bz = base_of("upper")
        CYL(f"{ROOT}/SignPost/Pole", (sp["cx"], sp["cy"],
                                      bz + sp["pole_h"] / 2.0),
            sp["pole_r"], sp["pole_h"], M["pole"], col=True)
        BOX(f"{ROOT}/SignPost/Panel", (sp["cx"], sp["cy"], bz + sp["panel_z"]),
            (sp["panel_t"], sp["panel_w"], sp["panel_h"]), M["sign"])
        cap(f"{ROOT}/SignPost/SnowPanel",
            (sp["cx"], sp["cy"],
             bz + sp["panel_z"] + sp["panel_h"] / 2.0 + sp["cap_t"] / 2.0
             - 0.008),
            (sp["panel_t"], sp["panel_w"]), sp["cap_t"])

        # (4) Hedge lines - a top snow cap (overhang) keeps them consistent with winter
        hc = PARAMS["hedge_cap"]
        for i, hd in enumerate(PARAMS["hedges"]):
            bz = base_of(hd["base"])
            cx = (hd["x0"] + hd["x1"]) / 2.0
            cy = (hd["y0"] + hd["y1"]) / 2.0
            sx = hd["x1"] - hd["x0"]
            sy = hd["y1"] - hd["y0"]
            BOX(f"{ROOT}/Hedge_{i}", (cx, cy, bz + hd["h"] / 2.0),
                (sx, sy, hd["h"]), M["hedge"], col=True)
            cap(f"{ROOT}/Hedge_{i}_Snow",
                (cx, cy, bz + hd["h"] + hc["t"] / 2.0 - 0.015),
                (sx, sy), hc["t"])

        # (5) Distant low-rise houses - shell + eaved roof slab + snow cap + chimney + windows
        hs = PARAMS["house"]
        for i, hd in enumerate(PARAMS["houses"]):
            bz = base_of(hd["base"])
            pfx = f"{ROOT}/House_{i}"
            cx = (hd["x0"] + hd["x1"]) / 2.0
            cy = (hd["y0"] + hd["y1"]) / 2.0
            sx = hd["x1"] - hd["x0"]
            sy = hd["y1"] - hd["y0"]
            h = hd["h"]
            # Shell: extend the plinth down by foot -> prevents floating above the ground
            BOX(f"{pfx}/Shell", (cx, cy, bz + (h - hs["foot"]) / 2.0),
                (sx, sy, h + hs["foot"]), M[f"brick_{i}"], col=True)
            # Eaved roof slab (overhang) - top face z = bz+h+roof_t
            BOX(f"{pfx}/Roof", (cx, cy, bz + h + hs["roof_t"] / 2.0),
                (sx + 2.0 * hs["eave"], sy + 2.0 * hs["eave"], hs["roof_t"]),
                M[f"roof_{i}"])
            cap(f"{pfx}/SnowRoof",
                (cx, cy, bz + h + hs["roof_t"] + hs["cap_t"] / 2.0 - 0.02),
                (sx + 2.0 * hs["eave"], sy + 2.0 * hs["eave"]), hs["cap_t"],
                inset=hs["cap_inset"])
            # Chimney (one side of the roof) + snow cap
            ch = hs["chimney_s"]
            chx = cx + sx * 0.28 * hd["face"]
            chy = cy + sy * 0.22
            BOX(f"{pfx}/Chimney",
                (chx, chy, bz + h + hs["roof_t"] + hs["chimney_h"] / 2.0
                 - 0.10),
                (ch, ch, hs["chimney_h"] + 0.20), M[f"brick_{i}"])
            cap(f"{pfx}/SnowChimney",
                (chx, chy,
                 bz + h + hs["roof_t"] + hs["chimney_h"] + hs["cap_t"] / 2.0
                 - 0.02),
                (ch, ch), hs["cap_t"])
            # Windows - the face toward the camera (face=-1 -> -X facade, +1 -> +X facade)
            # Bite the window plate (thickness 0.04) 1cm into the wall to avoid a coplanar face
            gx = (hd["x0"] if hd["face"] < 0 else hd["x1"]) \
                + hd["face"] * 0.01
            for r in range(hs["win_rows"]):
                zc = bz + h * (0.30 + 0.36 * r)
                for c in range(hs["win_cols"]):
                    yc = hd["y0"] + sy * (c + 0.5) / hs["win_cols"]
                    BOX(f"{pfx}/Win_{r}_{c}", (gx, yc, zc),
                        (0.04, hs["win_w"], hs["win_h"]), M["glass"])
        print(f"[드레싱] 벤치 {len(PARAMS['benches'])} · 가로등 "
              f"{len(PARAMS['lamps'])} · 표지판 1 · 생울타리 "
              f"{len(PARAMS['hedges'])} · 저층 주택 {len(PARAMS['houses'])} "
              f"(눈 캡 {'ON' if cfg['snow_cover'] else 'OFF'})")

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["stair"] if cfg["cue_material_break"] else M["concrete"]

    if cfg["hazard_stairs"]:
        build_terrace(M)
        build_lower(M)
        build_banks(M)
        build_stringers(M)
        build_stairs(stair_mtl)
        build_cues(M)
        if cfg["snow_cover"]:
            build_snow(M)
    elif KEEP_DRESSING:
        # [v3 arm C] hazard-ONLY removal. Terrace, lower ground, the two side
        #   banks, the flank stringers and the stair itself are the drop and its
        #   supporting ground, so `build_flat_fill` replaces all five with the same
        #   single plate the plain off arm lays — including its `Snow/FlatPlate`
        #   when `snow_cover` is on, which is why the camera datum stays at the
        #   +0.050 snow top that `Snow/PlateTop` gives arm A.
        #   `build_cues` is then called exactly as the hazard branch calls it: the
        #   railing comes back level with its snow strip (two switches inside),
        #   the nosing is declared lost there. `build_snow` is NOT called — every
        #   solid it emits is a per-tread bed/cap/chamfer or the approach plate's
        #   drop-edge nose, i.e. the snow's copy of the stair.
        #   Untouched by either arm and therefore still present: the material
        #   break (`stair_mtl`, chosen above), the stair-head tactile band and the
        #   whole paving/snow-trace kit (`build_ground_kit`), and the dressing.
        build_flat_fill(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M, LIFT)            # [W2] ground elements - after the dressing (scatter convention)

    print(f"[기하] run={RUN:.2f}m drop={DROP:.2f}m slope_k={SLOPE_K:.4f} "
          f"lower_top={LOWER_TOP:.3f} snow_lift={LIFT:.3f}")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneC1 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["approach"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneC1_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[하늘 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[하늘 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
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
    main()
