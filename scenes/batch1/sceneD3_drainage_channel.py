# -*- coding: utf-8 -*-
"""
sceneD3_drainage_channel.py - NegObs synthetic scene 30: urban concrete roadside
                              channel (Isaac Sim 4.5)

Type     : D3 non-stair drop (class extension - a roadside longitudinal open channel)
Spec     : Docs/nanobanana_batch1_geometry_map.md §C sceneD3_drainage_channel
           Docs/multi_scene_brief_v3.md §A regression-prevention checklist
Shared   : scene_common.py · skeleton convention scene16_canopy_shadow.py
           asphalt constant-colour pattern scene17_ramp_pair_hangang.py
Look ref : look_refs/d3_drainage_channel.jpg

Hazard   : beside a suburban asphalt roadway an **unguarded dry concrete channel**
           (trapezoid: top width 1.0 · depth 0.8 · bottom width 0.5) **runs
           parallel to the camera travel axis (+X)**. The pedestrian walks over the
           covered (slab-lidded) stretch and meets the open channel at x=0. Under
           grazing from the longitudinal viewpoint the opening shrinks to a thin
           band 1.0 m wide, and dry grass on the verge side overhangs the edge, so
           **the drop boundary disappears**. The road-side concrete lip is flush
           with the road surface, so there is no level-difference cue either.
Goal     : assemble the roadway (centre dashes · edge line) + the channel (2 sloped
           inner walls · bed slab · lip · grass overhang · bed leaves) + a distant
           box culvert + fence, houses and trees.
GT       : **drop 0.8 m positive over the channel area** (no drop on any other pixel).
           Basis = run-off-road ditch/culvert fatalities (the strongest evidence in
           scenario survey v1). The **urban counterpart** of the natural ditch (S2)
           in look check v1.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD3_drainage_channel.py

Auto capture (headless):   NEGOBS_CAPTURE=1 python sceneD3_drainage_channel.py
Smoke early exit:          NEGOBS_SMOKE=1  python sceneD3_drainage_channel.py

Coordinates: Z-up, m, travel axis +X.
  ※ convention adjustment: this scene's drop boundary is a **longitudinal line
    parallel to +X** (y=±0.50), so "drop start edge = x=0" cannot be applied to the
    longitudinal axis as it stands. Instead the layout makes **the cover slab end
    at x=0 and the open channel start there** (x<0 = walkable cover / x≥0 =
    opening), preserving the meaning of the convention (the drop begins ahead at
    x=0). Channel centre line y=0 → grid_views(gy=0.0) is itself the longitudinal
    viewpoint.

────────────────────────────────────────────────────────────────────────────
Geometry core - deriving the sloped inner walls of the trapezoidal section (_oriented_box rotX)
  Section: top width 2·0.50, bottom width 2·0.25, depth 0.80 → inner wall setback 0.25
        wall tilt (from vertical) = atan2(0.25, 0.80) = 17.354°  (matches the spec's ~17°)
  rotX(θ) in _oriented_box maps the local axes as follows (row-vector convention):
        local +Y → world (y,z) = ( cosθ,  sinθ)      … plate thickness direction (normal)
        local +Z → world (y,z) = (−sinθ,  cosθ)      … plate length direction (slope direction)
  +Y wall: its inner face must run from (0.50, 0) above to (0.25, −0.80) below, so
        the up-slope unit vector is u = (+sinφ, +cosφ), φ=17.354°.
        Satisfying local +Z = u requires −sinθ = +sinφ ⇒ **θ = −φ** (mind the sign:
        using +φ gives an inverted trapezoid with top and bottom widths swapped —
        confirmed by numeric check).
        Then local +Y = (cosφ, −sinφ) = the outward normal n (away from the channel, downward) ✓
        Relative to the inner-face mid-point (0.375, −0.40)
          center = mid + (t/2)·n − (ext/2)·u − (0, edge_sink)
        length L = hypot(0.25,0.80)·1.10 = 0.9220 (the extension ext goes **downward only**)
        check: top inner face (0.5000, −0.0040) / at z=−0.80 the inner face is y=0.2513 /
              bottom outer face y=0.3109 < invert half-width 0.60 (sealed) /
              top outer face y=0.5859 > verge start 0.50 (hides the top strip)
  −Y wall: θ=+17.354°, center_y sign flipped (symmetric). center_z is the same.
  The top edge of the opening sinks by edge_sink=0.004 → it **avoids being coplanar**
  with the verge/lip top faces (z=0/+0.002) (the no-Z-fighting convention).

────────────────────────────────────────────────────────────────────────────
[v6 context dressing] answers the audit v4 note about "barrenness" — so the place reads
as a suburban residential road.
  **The channel geometry (opening y −0.50..+0.50 · overhang · cover slab · lip ·
    culvert) was not touched by a single line.** Every new element sits either
    outside the verge (y ≥ 4.2), across the road (y ≤ −8.05) or in the distance (x ≥ 52).
  (1) 4 utility poles (x 13·33·53·73, y=+4.20) + 3 wires (per-span 2-segment sag
      approximation). y=+4.2 is 3.7 m clear of the opening edge (y=0.5) — in the
      longitudinal view it always stands **outside the opening line, to the left**,
      and an extended sight-line ray cast checks zero occlusion of the opening (§check).
      Given the sun azimuth the shadows reach **only toward +Y (the fence side)** and
      never touch the channel.
  (2) one concrete driveway patch — **across the road** (y −13.65..−8.05,
      x 12.5..16.5), running up to the house A facade. 7.4 m clear of the channel (y ≥ −0.65).
  (3) 1 mailbox + 1 wheelie bin (litter bin) — on the shoulders either side of the
      driveway (y ≈ −8.6).
  (4) distance reinforced: house C (across the road, x 56..68) · house E (beyond the
      fence, x 52..62) · 3 trees · **a treeline of 5 segments (x 74..76.4)** — the
      'huge white wall' (the ridge) that blocked the horizon in the r5 render is
      broken up by the treeline, and the ridge is given aerial-perspective colour
      (darker when nearer: 0.135 → 0.175 → 0.215).
  (5) GT unchanged: every new element is an upright or thin plate above ground —
      no new opening and no new drop.
────────────────────────────────────────────────────────────────────────────

Opening-split convention (lesson 5 — the bug where the surrounding ground covers the
cavity has recurred 3 times):
  the ground plates are split into 4 along y so that **no plate covers** the opening
  band (y −0.50..+0.50, x≥0): [far shoulder | roadway | lip] · opening · [verge | back yard]
  x<0 is deliberately covered by the cover slab (= the source of walking continuity,
  the drop-start point).
────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - the standard 7 keys + 1 scene-specific key (grass_overhang)
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # the scene's drop geometry = **the open roadside channel**.
                                   # False -> the opening is filled to a flat z=0 (geometry toggle)
    "cue_railing":        False,   # **being unguarded is the identity** - True adds one pipe
                                   # railing line on the verge side (code path implemented)
    "cue_tactile":        False,   # not customary on a roadside channel (code path only)
    "cue_material_break": True,    # concrete lip and channel vs asphalt road contrast
                                   # False -> the lip is asphalt too (cue removed)
    "cue_nosing":         False,   # stairs only - unused (key reserved only)
    "cue_sign":           False,   # [optional] not implemented - key reserved only
    "cue_scene_dressing": True,    # fence, houses, trees and distant scenery together
    # ─ scene-specific toggle: False -> no grass overhang = the fully exposed edge twin ─
    "grass_overhang":     True,
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- channel section / extent ---
    ch=dict(x_open=0.0, x_end=38.0, x_back=-22.0,
            top_half=0.50, bot_half=0.25, depth=0.80,
            wall_t=0.18, wall_ext=1.10, edge_sink=0.004,
            invert_half=0.60, invert_t=0.25),
    # --- cover slab : x −22..0, top +0.004 (walking surface, drop-start edge) ---
    #  * [W2 §5.7 D3] the joint owner **moves to ground_kit.** The spec prescribes
    #    "deepen the joints - current **+1 mm proud -> 3 mm recessed**". The old code laid a dark
    #    thin plate proud +0.001 as a "stand-in for a recess", but at a grazing angle (h0.3) a ridge
    #    and a recess shade the opposite way. The kit's `build_joint_grid` keeps the nominal recess
    #    −0.003 in the ledger (`recess_nominal`) and lifts the surface to `surface_top_z`
    #    (+0.6 mm), avoiding **burial in the solid slab** (pilot #2 defect).
    #    the pitch (2.5 m) and width (0.04) are inherited as-is, so the scene rhythm is unchanged.
    #    `joint_proud` is no longer used (kept only to preserve the ledger).
    cover=dict(y0=-0.65, y1=0.66, top=0.004, thick=0.20,
               joint_step=2.5, joint_w=0.04, joint_proud=0.001),

    # ═══ [W2 ground_kit] P17 verge_rural - spec §5.7 row D3 ═════════════════
    #  * this is a **natural scene** (`natural=True`). `plan_ground` enforces in code that urban
    #    infrastructure (manhole · gully · L-type gutter · lane paint · tactile paving · bollard) is **zero**.
    #    D3's **U-channel identity** (cover slab + trapezoidal open channel + culvert) stays exactly
    #    as the scene geometry has it, and ground_kit never touches it - zero section changes.
    #  * there are two surfaces, so there are two plans (one plan = one z):
    #     (1) `cover` cover slab top z=+0.004 - this is where the h0.3 near window sits.
    #        deepened joints · repair patches · cracks · **a silt band on the cover** · edge weeds.
    #     (2) `road`  asphalt roadway z=0.0 - **roadway patches/cracks** · soil deposits · shoulder weeds.
    gkit=dict(
        cover_x0=-12.0,
        cover_patches=[(-1.20, 0.00), (-3.80, 0.00), (-8.80, 0.00)],
        #  the roadway - kept to y <= −1.10, clear of the channel lip (y=−0.65) and the edge line (y=−0.95 +-0.05).
        road_region=(-12.0, -8.00, 2.0, -1.10),
    ),
    # --- road-side concrete lip (flush with the road surface, width 0.15) ---
    lip=dict(y0=-0.65, y1=-0.50, top=0.002, x0=-0.30, base_z=-1.60),
    # --- asphalt roadway ---
    # x1 96 : the ground has to reach the distant ridge (x 77..94), otherwise a void opens at its end
    road=dict(y0=-8.20, y1=-0.65, x0=-22.0, x1=96.0, top=0.0, thick=1.60),
    dash=dict(y=-4.40, w=0.15, length=3.0, period=8.0, proud=0.002),
    edge_line=dict(y=-0.95, w=0.10, proud=0.002),
    # --- verge (dry grass) / back yard / far shoulder ---
    verge=dict(y0=0.50, y1=6.40, top=0.0, thick=1.60),
    # site width y −42..+20 (brief §A-4: no void at the site edge)
    yard=dict(y0=6.40, y1=20.0, top=0.0, thick=1.60),
    farside=dict(y0=-42.0, y1=-8.20, top=0.0, thick=1.60),
    # the buried stretch of the channel line past the culvert (x > headwall) - the only place the opening band is covered.
    #   lid = a **thin cover** (thickness 0.05) passing over the dark recess (CulvertDark):
    #   making it thicker would overlap the dark box in volume and give coplanar Z-fighting head-on at the opening.
    #   main = normal thickness after that. The cavity under the lid is sealed by headwall · lip · verge · main.
    beyond=dict(y0=-0.65, y1=0.50, top=0.0, thick=1.60,
                lid_x0=38.40, lid_x1=44.20, lid_t=0.05),

    # --- grass overhang : low build_hedge strips laid across the opening edge ---
    overhang=dict(count=12, seed=3001, x0=0.4, x_span=36.0,
                  len_lo=2.9, len_hi=3.1, over_lo=0.0, over_hi=0.05,
                  out_lo=0.32, out_hi=0.55, h_lo=0.05, h_hi=0.08),  # r2: almost no projection over the opening, a continuous low grass lip instead
    # --- fallen leaves on the channel bed (plate + scatter) ---
    bed_leaf=dict(patches=6, seed=3002, y_half=0.22, thick=0.05,
                  sink=0.025, len_lo=0.9, len_hi=2.4, x0=1.0, x_span=34.0,
                  scatter=160, scale=(0.06, 0.045, 0.008),
                  jitter=(0.75, 1.30), lift=0.006),

    # --- box culvert (distant horizon anchor + dark recess) ---
    culvert=dict(x0=38.0, x1=38.6, y_half=0.72, z_top=0.08, z_bot=-1.05,
                 op_half=0.45, op_top=-0.10, sill_top=-0.79,
                 dark_x1=44.0, dark_half=0.48, dark_top=-0.06),

    # --- cue (default OFF - being unguarded is the identity) ---
    rail=dict(y=0.72, x0=0.0, x1=38.0, rail_h=0.90, post_r=0.024,
              rail_r=0.030, rail_mid_r=0.018, rail_mid_drop=0.42,
              spacing=1.60),
    tactile=dict(depth=0.30, proud=0.004),

    # --- dressing / horizon closure ---
    fence=dict(y=6.40, t=0.12, h=1.75, x0=-22.0, x1=96.0,
               cap_h=0.08, cap_over=0.04),
    trees=[dict(cx=-6.0, cy=9.0), dict(cx=5.0, cy=8.4),
           dict(cx=16.0, cy=10.0), dict(cx=28.0, cy=8.6),
           dict(cx=44.0, cy=9.4), dict(cx=58.0, cy=8.2),
           dict(cx=22.0, cy=-11.0), dict(cx=52.0, cy=-12.5)],
    houses=dict(
        A=dict(x0=8.0, x1=20.0, y0=-19.0, y1=-13.5, h=4.2, floors=1,
               axis="y", facade_y=-13.5, face_dir=1.0),
        B=dict(x0=32.0, x1=44.0, y0=-19.0, y1=-13.5, h=4.2, floors=1,
               axis="y", facade_y=-13.5, face_dir=1.0),
        # [v6-(4)] distant house row reinforced. C = the third house across the road (residential rhythm),
        #        E = the house behind the fence (verge-side distance - showing above the fence top 1.83).
        C=dict(x0=56.0, x1=68.0, y0=-19.0, y1=-13.5, h=4.2, floors=1,
               axis="y", facade_y=-13.5, face_dir=1.0),
        E=dict(x0=52.0, x1=62.0, y0=13.6, y1=19.5, h=4.0, floors=1,
               axis="y", facade_y=13.6, face_dir=-1.0),
    ),
    window=dict(w=1.2, h=1.3, inset=0.15, col_step=3.0, margin=2.0),
    back_hedge=dict(cy=12.6, sy=1.4, length=26.0),
    back_hedges=[dict(cx=-8.0), dict(cx=18.0), dict(cx=44.0), dict(cx=68.0)],
    # distant vista block (+X horizon): 2 ridge boxes. cy/sy stay inside the site y −42..+20.
    # [v6-(4)] aerial-perspective colour added - clears the 'white wall' of the r5 render (darker when nearer).
    ridge=[dict(cx=80.0, cy=-8.0, h=6.0, sy=56.0, t=6.0,
                color=(0.155, 0.175, 0.150)),
           dict(cx=90.0, cy=-8.0, h=9.0, sy=56.0, t=8.0,
                color=(0.205, 0.220, 0.235))],
    # [v6-(4)] treeline - x 74..76.4 in front of the ridge (x>=77). Varied heights avoid coplanar top faces.
    #   y stays inside the site (−42..+20). base_z −0.05 (avoids being coplanar with the ground top face).
    treeline=dict(x0=74.0, x1=76.4, span=13.0, base_z=-0.05,
                  cys=(-30.0, -18.0, -6.0, 6.0, 13.2),
                  hs=(3.4, 2.9, 3.8, 3.1, 3.5),
                  tint=(0.150, 0.205, 0.120)),

    # ─── [v6] context dressing (channel geometry unchanged - all at y>=4.2 / y<=−8.05 / x>=52) ───
    # (1) utility poles + wires. y=+4.20 is 3.70 m from the opening edge (0.50) and
    #    2.20 m from the fence (6.40) - mid verge. Span 20 m, sag 0.35 (2-segment mid-point approximation).
    poles=[13.0, 33.0, 53.0, 73.0],
    pole=dict(y=4.20, r=0.115, h=8.50, arm_len=1.80, arm_t=0.10, arm_h=0.09,
              wire_r=0.016, wire_z=7.620, wire_dy=(-0.75, 0.0, 0.75),
              sag=0.35, stub_x=-12.0, stub_z=7.30),
    # (2) house driveway - across the road. y1 −8.05 overlaps the road surface (y0 −8.20) by 0.15 to
    #    avoid coplanarity (top +0.002 proud); y0 −13.65 is buried 0.15 under the house A shell.
    driveway=dict(x0=12.5, x1=16.5, y0=-13.65, y1=-8.05, top=0.002,
                  thick=0.20),
    # (3) mailbox · wheelie bin (shoulders either side of the driveway)
    mailbox=dict(cx=17.4, cy=-8.55, post_r=0.05, post_h=1.05,
                 w=0.34, d=0.24, h=0.26),
    binbox=dict(cx=11.4, cy=-8.60, w=0.58, d=0.72, h=1.02, lid_t=0.06),
    # (4) 3 more distant trees (on the yard / farside ground)
    trees_v6=[dict(cx=66.0, cy=15.5), dict(cx=34.0, cy=16.5),
              dict(cx=64.0, cy=-22.0)],

    material=dict(
        scale=dict(concrete_wall=1.6, concrete_floor=1.2, grass=1.4,
                   leaf_ground=0.8, wood_dark=1.0, brick_red=2.0),
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.85,  # scene17 constant
        paint_color=(0.72, 0.72, 0.68), paint_rough=0.60,
        wall_tint=(0.55, 0.53, 0.50),        # weathered darkening of the channel inner walls (texture multiplier)
        lip_tint=(0.82, 0.81, 0.78),         # lip and cover slab (light concrete)
        dry_grass_tint=(0.62, 0.58, 0.34),   # dry grass verge
        leaf_tex_tint=(0.95, 0.72, 0.48),
        leaf_tints=((0.30, 0.14, 0.05), (0.38, 0.20, 0.06),
                    (0.25, 0.10, 0.04), (0.42, 0.28, 0.10)),
        leaf_rough=0.90,
        # dark constant inside the culvert - sRGB gamma rule (dark colours in the 0.02~0.06 band)
        dark_color=(0.030, 0.030, 0.032), dark_rough=0.95,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.86, 0.85, 0.82), parapet_rough=0.60,
        ridge_color=(0.26, 0.28, 0.26),          # (fallback - the per-ridge color wins)
        # --- [v6] dressing constant colours ---
        pole_color=(0.30, 0.27, 0.23), pole_rough=0.88,   # weathered timber utility pole
        wire_color=(0.045, 0.045, 0.048), wire_rough=0.60,
        mailbox_color=(0.38, 0.40, 0.42), mailbox_metallic=0.25,
        mailbox_rough=0.45,
        bin_color=(0.055, 0.075, 0.050), bin_rough=0.70,  # dark-green wheelie bin (dark-colour convention)
        bin_lid_color=(0.42, 0.38, 0.06), bin_lid_rough=0.65,
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
    # ─── SUN_AZ_OFFSET rationale (redefined per scene): world sun az ~ 33.5+201.5 = **235 deg**
    #     -> shadow az = 55 deg (**55 deg oblique** to the channel's long axis +X - satisfies the spec's
    #       "oblique to the long axis". At 90 deg (perpendicular) one wall is all direct sun and the
    #       other all shade - monotonous; at 0/180 deg (axial) both walls are equal and no partial shading forms).
    #     quantitative check (elev 49.79 -> 0.8455 m of horizontal shadow per 1 m of depth):
    #       at a depth of 0.80 m the shadow of the road-side top edge (y=−0.50) lands at
    #       y = −0.50 + 0.8455·sin55°·0.80 = **+0.054**
    #       => road-side inner wall = fully shaded / bed y<0.054 shaded, y>0.054 in direct sun /
    #          verge-side inner wall = direct sun.  The inside of the opening reads as **partial shade**
    #          rather than a single black, which is what makes the grazing concealment (the scene trait) work.
    #     the sun is also behind the camera (which looks +X), so road surface and verge are front-lit.
    #     [v6 shadow check of the new elements] shadow displacement (per height h) = (+0.485h, +0.6925h)
    #       - **toward +Y (the fence side)**, so shadows of new elements placed at y > 0.5 move
    #       further away from the channel. Even the largest displacement, from the utility pole
    #       (y=4.20, h=8.50), is y = 4.20 + 5.89 = +10.09 (back yard beyond the fence at 6.40) -> **zero reach into the opening**.
    #       props across the road (mailbox · bin y~−8.6, h<=1.05) get delta y <= +0.73 ->
    #       y <= −7.87, so they stay at the shoulder / road edge (7.2 m short of the opening).
    #       the driveway is a flat patch and casts no shadow. => the channel's partial-shade profile is unchanged. ───
    SUN_AZ_OFFSET=201.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD3")

ASSET_ROLES = ["concrete_wall", "concrete_floor", "grass", "leaf_ground",
               "wood_dark", "brick_red", "hdri", "mdl"]


# ===========================================================================
# [D] camera presets: grid_views (gy=0.0 = the channel centre line) + 4 mise-en-scene cuts
#     putting gy on the channel centre line makes every grid preset a **longitudinal view**.
# ===========================================================================
def ground_plans():
    """[W2 ground_kit] two ground plans - the scene assembly and the CPU numeric check use the same function.

    (1) `cover` : the cover slab (walking surface) - it holds the drop-start edge x=0.
    (2) `road`  : the asphalt roadway - no drop ahead (`edges=()`).
    """
    g = PARAMS["gkit"]
    cv, ch = PARAMS["cover"], PARAMS["ch"]
    cover = gk.plan_ground(
        "verge_rural",
        region=(float(g["cover_x0"]), float(cv["y0"]),
                float(ch["x_open"]), float(cv["y1"])),
        z=float(cv["top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("channel_open", float(ch["x_open"]))],
        dists=(2, 5, 10), scene="sceneD3",
        tactile=(),                     # §12.4 - not applicable (rural roadside)
        sites=dict(patch=[tuple(p) for p in g["cover_patches"]]),
        #  pitch and width inherited from the scene, only the recess deepened to −3 mm (§5.7).
        overrides=dict(pave=dict(joint="contraction",
                                 step_x=float(cv["joint_step"]),
                                 groove_w=float(cv["joint_w"]),
                                 recess=-0.003)),
        seed=301)
    road = gk.plan_ground(
        "verge_rural", region=tuple(g["road_region"]),
        z=float(PARAMS["road"]["top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=(),                       # no drop ahead on the roadway
        dists=(2, 5, 10), scene="sceneD3",
        tactile=(),
        #  asphalt has no contraction joints -> zero joints.
        overrides=dict(pave=dict(joint=None)),
        seed=302)
    return [("cover", cover), ("road", road)]


def build_views():
    views = sc.grid_views(0.0)                 # h{0.3,0.9,1.8}×d{2,5,10}, +X
    # verge_walk: walking along the verge, approaching the channel obliquely - does the overhang cover the edge
    views["verge_walk"] = dict(eye=[-6.0, 1.70, 1.60], tgt=[6.0, 0.35, -0.20])
    # grazing_low: low longitudinal grazing view - the extreme where the opening shrinks to a thin band
    views["grazing_low"] = dict(eye=[-4.0, 0.12, 0.35], tgt=[9.0, 0.05, -0.05])
    # oblique_cross: 30 deg oblique approach from the road side (the mise-en-scene oblique cut)
    views["oblique_cross"] = dict(eye=[-3.0, -5.20, 1.50],
                                  tgt=[6.0, 0.55, -0.35])
    # channel_reveal: close high angle - checks the trapezoidal section, partial shading and bed leaves
    views["channel_reveal"] = dict(eye=[1.20, 2.60, 1.90],
                                   tgt=[10.0, 0.00, -0.60])
    # culvert_far: checks the distant culvert mouth (dark recess)
    views["culvert_far"] = dict(eye=[30.0, 1.10, 1.55], tgt=[40.0, 0.0, -0.40])
    return views


# ===========================================================================
# [D2] camera numeric check (v6 context dressing) - pure maths, printed under SMOKE.
#   Isaac default camera (focal 18.14756 / aperture 20.955) -> hFOV 60 deg,
#   1920x1080 -> vFOV 36 deg. Half-angles 30 deg/18 deg.
#   (1) camera vs new-prim near collision  (2) **channel occlusion = 0** (extended sight-line ray cast)
# ===========================================================================
HFOV_HALF = 30.0
VFOV_HALF = 18.0


def _cam_angles(view, p):
    """(yaw_rel°, elev_rel°, dist, in_frame) - exact transform relative to the camera optical axis."""
    ex, ey, ez = view["eye"]
    tx, ty, tz = view["tgt"]
    fx, fy, fz = tx - ex, ty - ey, tz - ez
    yaw = math.atan2(fy, fx)
    pitch = math.atan2(fz, math.hypot(fx, fy))
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    u = dx * math.cos(yaw) + dy * math.sin(yaw)
    v = -dx * math.sin(yaw) + dy * math.cos(yaw)
    u2 = u * math.cos(pitch) + dz * math.sin(pitch)
    w2 = -u * math.sin(pitch) + dz * math.cos(pitch)
    yaw_r = math.degrees(math.atan2(v, u2))
    elev_r = math.degrees(math.atan2(w2, math.hypot(u2, v)))
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    inf = (u2 > 0.0 and abs(yaw_r) <= HFOV_HALF and abs(elev_r) <= VFOV_HALF)
    return yaw_r, elev_r, dist, inf


def _channel_hit(eye, p, t_max=60.0, step=0.02):
    """Extend the eye→p sight line **beyond** p and decide whether it passes through the
    channel view band (cover · lip · opening · overhang included: |y| ≤ 0.66,
    x ∈ [x_back, x_end], z ≥ −depth).
    If it does, return (x, y) = that prim hides channel pixels. Otherwise None."""
    ex, ey, ez = eye
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    ch = PARAMS["ch"]
    t = 1.0
    while t <= t_max:
        x = ex + dx * t
        y = ey + dy * t
        z = ez + dz * t
        if (abs(y) <= 0.66 and ch["x_back"] <= x <= ch["x_end"]
                and -ch["depth"] <= z <= 0.30):
            return (x, y)
        t += step
    return None


def pole_xs():
    """[v5.1 §3] deterministic x ±0.5 m jitter on the utility poles. Distribution poles
    never land on an exact 20 m pitch because of terrain and site conditions - the
    span sag is computed by build_utility_line at the real span mid-point, so it
    stays consistent after the jitter.
    y (+4.20, mid verge) is unchanged - it preserves the 3.70 m opening clearance invariant."""
    return [x + bc.jit_scalar(x, PARAMS["pole"]["y"], "poleD3", -0.5, 0.5)
            for x in PARAMS["poles"]]


def back_hedge_xs():
    """[v5.1 §3] cx ±1.0 m jitter on the 4 background hedge stretches (relaxes the even 26 m pitch)."""
    return [h["cx"] + bc.jit_scalar(h["cx"], 0.0, "bhD3", -1.0, 1.0)
            for h in PARAMS["back_hedges"]]


def _dressing_probes():
    """Points to check: (name, (x,y,z)) - representative extreme points of the new v6 dressing."""
    P = []
    pl = PARAMS["pole"]
    for x in pole_xs():
        P.append((f"전신주x{x:.1f}·상단", (x, pl["y"], pl["h"])))
        P.append((f"전신주x{x:.1f}·중단", (x, pl["y"], pl["h"] * 0.5)))
        P.append((f"전신주x{x:.1f}·기부", (x, pl["y"], 0.3)))
        P.append((f"완목x{x:.1f}·단부",
                  (x, pl["y"] + pl["arm_len"] / 2.0, pl["wire_z"])))
    dw = PARAMS["driveway"]
    for tag, (x, y) in (("근각", (dw["x0"], dw["y1"])),
                        ("원각", (dw["x1"], dw["y0"]))):
        P.append((f"진입로·{tag}", (x, y, dw["top"])))
    mb = PARAMS["mailbox"]
    P.append(("우편함", (mb["cx"], mb["cy"], mb["post_h"] + mb["h"] / 2.0)))
    bn = PARAMS["binbox"]
    P.append(("수거함", (bn["cx"], bn["cy"], bn["h"] / 2.0)))
    for key in ("C", "E"):
        hs = PARAMS["houses"][key]
        P.append((f"주택{key}·근각", (hs["x0"], hs["facade_y"], hs["h"])))
    tl = PARAMS["treeline"]
    for i, (cy, h) in enumerate(zip(tl["cys"], tl["hs"])):
        P.append((f"수림대_{i}", (tl["x0"], cy, tl["base_z"] + h)))
    for t in PARAMS["trees_v6"]:
        P.append((f"수목({t['cx']:g},{t['cy']:g})", (t["cx"], t["cy"], 2.8)))
    return P


def _dressing_report():
    views = build_views()
    probes = _dressing_probes()
    print("-" * 64)
    print("[검산] v6 맥락 드레싱 × 카메라 (hFOV 60° / vFOV 36°)")
    worst = worst_in = None
    for vn, vw in views.items():
        for nm, p in probes:
            _, _, dist, inf = _cam_angles(vw, p)
            if worst is None or dist < worst[0]:
                worst = (dist, vn, nm)
            if inf and (worst_in is None or dist < worst_in[0]):
                worst_in = (dist, vn, nm)
    print(f"  ① 최근접(전체)     = {worst[0]:.2f} m ({worst[1]} ↔ {worst[2]})")
    print(f"    최근접(프레임 내) = {worst_in[0]:.2f} m "
          f"({worst_in[1]} ↔ {worst_in[2]}) → "
          f"{'OK' if worst_in[0] >= 1.0 else 'FAIL(<1.0)'}")
    warn = []
    for vn, vw in views.items():
        for nm, p in probes:
            if not _cam_angles(vw, p)[3]:
                continue
            hit = _channel_hit(vw["eye"], p)
            if hit is not None:
                warn.append((vn, nm, hit))
    if warn:
        for vn, nm, hit in warn:
            print(f"  ② [FAIL] {vn}: {nm} → 측구 시야대 (x={hit[0]:.1f}, "
                  f"y={hit[1]:+.2f}) 가림")
    else:
        print("  ② 측구 시야대(|y|≤0.66, x −22..38) 가림 프림 **0** → OK "
              "(연장 시선 레이캐스트, 전 뷰 × 전 프림)")
    for vn in ("verge_walk", "grazing_low", "oblique_cross", "channel_reveal",
               "culvert_far", "preset_h0.9_d5"):
        vw = views.get(vn)
        if vw is None:
            continue
        names = [nm for nm, p in probes if _cam_angles(vw, p)[3]]
        print(f"  ③ {vn:15s} 프레임 내 {len(names):2d}종: "
              f"{', '.join(names[:5])}{' …' if len(names) > 5 else ''}")
    # (4) channel invariants · ground boundary margins
    ch = PARAMS["ch"]
    pl = PARAMS["pole"]
    dw = PARAMS["driveway"]
    mb, bn = PARAMS["mailbox"], PARAMS["binbox"]
    rd, vg, yd, fs = (PARAMS["road"], PARAMS["verge"], PARAMS["yard"],
                      PARAMS["farside"])
    print(f"  ④ 개구 에지 y=±{ch['top_half']:.2f} · 오버행/립 대역 |y|≤0.66")
    print(f"    전신주 y {pl['y']:+.2f} (버지 {vg['y0']:+.2f}..{vg['y1']:+.2f} 안, "
          f"개구에서 {pl['y'] - ch['top_half']:.2f} m) → "
          f"{'OK' if vg['y0'] < pl['y'] < vg['y1'] else 'FAIL'}")
    print(f"    진입로 y [{dw['y0']:+.2f},{dw['y1']:+.2f}] : 노면 y0 "
          f"{rd['y0']:+.2f} 위로 {rd['y0'] - dw['y1']:+.3f} 겹침(동일평면 회피) · "
          f"개구까지 {abs(dw['y1']) - 0.66:.2f} m → "
          f"{'OK' if dw['y1'] < -0.66 else 'FAIL'}")
    print(f"    우편함 y {mb['cy'] + mb['w'] / 2.0:+.2f} / 수거함 y "
          f"{bn['cy'] + bn['d'] / 2.0:+.2f} (둘 다 갓길 y<{rd['y0']:+.2f}) → "
          f"{'OK' if mb['cy'] + mb['w'] / 2 < rd['y0'] and bn['cy'] + bn['d'] / 2 < rd['y0'] else 'FAIL'}")
    tl = PARAMS["treeline"]
    ty0 = min(tl["cys"]) - tl["span"] / 2.0
    ty1 = max(tl["cys"]) + tl["span"] / 2.0
    print(f"    수림대 y [{ty0:+.1f},{ty1:+.1f}] vs 대지 [{fs['y0']:+.1f},"
          f"{yd['y1']:+.1f}] → {'OK(부유 없음)' if ty0 >= fs['y0'] and ty1 <= yd['y1'] else 'FAIL'}"
          f" · 높이 {tl['hs']} (상면 동일평면 없음)")
    hE = PARAMS["houses"]["E"]
    print(f"    주택E y [{hE['y0']:+.1f},{hE['y1']:+.1f}] + 파라펫 0.1 vs 뒷마당 "
          f"{yd['y1']:+.1f} → {'OK' if hE['y1'] + 0.1 <= yd['y1'] else 'FAIL'}")
    print("-" * 64)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3·h0.9 종주      — 측구 개구가 가는 띠로 축소·소실되는가(그레이징 은닉)
 2. verge_walk          — 마른 잔디 오버행이 근측 에지를 덮는가(특색)
 3. channel_reveal      — 사다리꼴 단면(1.0/0.8/0.5)·부분 음영·바닥 낙엽
 4. 립·노면             — 콘크리트 립이 노면과 flush(단차 단서 부재)인가
 5. 개구 분할           — 지면 평판이 개구를 덮지 않는가 / x<0 복개만 덮는가
 6. culvert_far         — 컬버트 입구가 암색 후퇴로 읽히는가(완전 흑 금지)
 7. grass_overhang OFF  — 측구 기하 트랜스폼 완전 불변(대응쌍)
 8. [v6] 맥락 판독      — 전신주·전선/진입로/우편함·수거함/원경 주택열·수림대로
                          '교외 주택가 도로변'이 읽히는가
 9. [v6] 측구 시야      — 신규 요소가 전 뷰에서 개구·오버행을 전혀 안 가리는가
10. [v6] 지평           — 능선이 백색 벽이 아니라 수림대+대기원근 층위로 읽히는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene30")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene30"

    ch = PARAMS["ch"]
    # wall tilt (from vertical) - derived from the trapezoidal section
    TILT = math.degrees(math.atan2(ch["top_half"] - ch["bot_half"],
                                   ch["depth"]))
    SLOPE_LEN = math.hypot(ch["top_half"] - ch["bot_half"], ch["depth"])

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

        def tex(role, path, scale, **kw):
            return PBR(path, sc.tex_path(role, "diff"),
                       sc.tex_path(role, "nor"), sc.tex_path(role, "rough"),
                       scale, **kw)

        M = {}
        M["chwall"] = tex("concrete_wall", f"{ROOT}/Looks/ChWall",
                          sca["concrete_wall"], tint=mp["wall_tint"])
        M["conc"] = tex("concrete_floor", f"{ROOT}/Looks/Conc",
                        sca["concrete_floor"], tint=mp["lip_tint"])
        M["grass"] = tex("grass", f"{ROOT}/Looks/Grass", sca["grass"],
                         tint=mp["dry_grass_tint"])
        M["leafbed"] = tex("leaf_ground", f"{ROOT}/Looks/LeafBed",
                           sca["leaf_ground"], tint=mp["leaf_tex_tint"])
        M["wood"] = tex("wood_dark", f"{ROOT}/Looks/WoodTex", sca["wood_dark"])
        M["brick"] = tex("brick_red", f"{ROOT}/Looks/Brick", sca["brick_red"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        M["dark"] = PBR(f"{ROOT}/Looks/Dark", diffuse_color=mp["dark_color"],
                        roughness_const=mp["dark_rough"], metallic=0.0,
                        specular_level=0.0)
        for i, c in enumerate(mp["leaf_tints"]):
            M[f"leaf_{i}"] = PBR(f"{ROOT}/Looks/Leaf_{i}", diffuse_color=c,
                                 roughness_const=mp["leaf_rough"],
                                 metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["woodc"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                         roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # [v6-(4)] each ridge gets its own aerial-perspective colour (fallback = ridge_color)
        for i, r in enumerate(PARAMS["ridge"]):
            M[f"ridge_{i}"] = PBR(
                f"{ROOT}/Looks/Ridge_{i}",
                diffuse_color=r.get("color", mp["ridge_color"]),
                roughness_const=0.95, specular_level=0.0)
        # --- [v6] dressing materials ---
        tl = PARAMS["treeline"]
        M["treeline"] = tex("grass", f"{ROOT}/Looks/Treeline", sca["grass"],
                            tint=tl["tint"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        roughness_const=mp["pole_rough"], metallic=0.0)
        M["wire"] = PBR(f"{ROOT}/Looks/Wire", diffuse_color=mp["wire_color"],
                        roughness_const=mp["wire_rough"], metallic=0.0)
        M["mailbox"] = PBR(f"{ROOT}/Looks/Mailbox",
                           diffuse_color=mp["mailbox_color"],
                           metallic=mp["mailbox_metallic"],
                           roughness_const=mp["mailbox_rough"])
        M["bin"] = PBR(f"{ROOT}/Looks/Bin", diffuse_color=mp["bin_color"],
                       roughness_const=mp["bin_rough"], metallic=0.0)
        M["bin_lid"] = PBR(f"{ROOT}/Looks/BinLid",
                           diffuse_color=mp["bin_lid_color"],
                           roughness_const=mp["bin_lid_rough"], metallic=0.0)
        return M

    # -------------------------------------------------------------------
    # cylinder between two points (wire) - scene15 convention. A Z-axis cylinder aligned by yaw/pitch.
    # -------------------------------------------------------------------
    def _wire(path, a, b, r, mtl):
        from pxr import UsdGeom, UsdShade, Gf
        ax, ay, az = a
        bx, by, bz = b
        dx, dy, dz = bx - ax, by - ay, bz - az
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        cyl = UsdGeom.Cylinder.Define(stage, path)
        cyl.CreateRadiusAttr(float(r))
        cyl.CreateHeightAttr(float(L))
        cyl.CreateAxisAttr(UsdGeom.Tokens.z)
        xf = UsdGeom.Xformable(cyl)
        xf.AddTranslateOp().Set(Gf.Vec3d((ax + bx) / 2.0, (ay + by) / 2.0,
                                         (az + bz) / 2.0))
        xf.AddRotateZOp().Set(float(math.degrees(math.atan2(dy, dx))))
        xf.AddRotateYOp().Set(
            float(math.degrees(math.atan2(math.hypot(dx, dy), dz))))
        if mtl is not None:
            UsdShade.MaterialBindingAPI.Apply(cyl.GetPrim()).Bind(mtl)
        return cyl

    # -------------------------------------------------------------------
    # ground - **split along y so that no plate covers the opening band (y +-0.50, x>=0)** (lesson 5)
    #   [far shoulder | roadway | lip] · opening · [verge | back yard]
    # -------------------------------------------------------------------
    def build_ground(M):
        rd = PARAMS["road"]
        lp = PARAMS["lip"]
        vg = PARAMS["verge"]
        yd = PARAMS["yard"]
        fs = PARAMS["farside"]
        by = PARAMS["beyond"]
        cv = PARAMS["culvert"]
        x0, x1 = rd["x0"], rd["x1"]

        def plate(name, y0, y1, top, thick, mtl, xa=None, xb=None):
            xa = x0 if xa is None else xa
            xb = x1 if xb is None else xb
            BOX(f"{ROOT}/{name}", ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                                   top - thick / 2.0),
                (xb - xa, y1 - y0, thick), mtl, col=True)

        # [W2-0 · P-A] the roadway is a decoration target of ground_kit -> displacement skin OFF.
        #   it has to be registered **before plate() is called** (`add_box` decides on the spot).
        sc.skin_exclude(f"{ROOT}/Road")
        # roadway (asphalt) + far shoulder + verge + back yard
        plate("Road", rd["y0"], rd["y1"], rd["top"], rd["thick"], M["asphalt"])
        plate("FarSide", fs["y0"], fs["y1"], fs["top"], fs["thick"], M["grass"])
        plate("Verge", vg["y0"], vg["y1"], vg["top"], vg["thick"], M["grass"])
        plate("Yard", yd["y0"], yd["y1"], yd["top"], yd["thick"], M["grass"])
        # road-side lip (flush with the road, proud 0.002) - x spans the open stretch + 0.30 under the cover
        lip_mtl = M["conc"] if cfg["cue_material_break"] else M["asphalt"]
        plate("Lip", lp["y0"], lp["y1"], lp["top"], lp["top"] - lp["base_z"],
              lip_mtl, xa=lp["x0"], xb=cv["x1"])
        # buried stretch past the culvert - the only +X plate that covers the opening band (lid + main body).
        # with hazard_stairs=False (the flat control) FlatFill fills the whole opening line, so
        # building it here would make the top faces coplanar (Z-fighting) -> hazard geometry only.
        if cfg["hazard_stairs"]:
            plate("BeyondLid", by["y0"], by["y1"], by["top"], by["lid_t"],
                  M["grass"], xa=by["lid_x0"], xb=by["lid_x1"])
            plate("BeyondMain", by["y0"], by["y1"], by["top"], by["thick"],
                  M["grass"], xa=by["lid_x1"], xb=x1)

    def build_cover(M):
        """Cover slab (x −22..0) - the source of walking continuity and the drop-start edge.

        [W2 §5.7] **the joints are not made here** - ground_kit lays them again as a
        −3 mm recess (`build_ground_kit`). Leaving the old code's +1 mm proud thin
        plate would put two grids on the same surface (pilot defect D6).
        """
        cvr = PARAMS["cover"]
        # [W2-0 · P-A] the cover slab top face is ground_kit's stage -> skin OFF.
        sc.skin_exclude(f"{ROOT}/CoverSlab")
        BOX(f"{ROOT}/CoverSlab",
            ((ch["x_back"] + ch["x_open"]) / 2.0,
             (cvr["y0"] + cvr["y1"]) / 2.0, cvr["top"] - cvr["thick"] / 2.0),
            (ch["x_open"] - ch["x_back"], cvr["y1"] - cvr["y0"],
             cvr["thick"]), M["conc"], col=True)
        # (the joints moved to ground_kit `build_joint_grid` - see the docstring above)

    # -------------------------------------------------------------------
    # channel - 2 sloped inner walls (_oriented_box rotX) + bed slab
    # -------------------------------------------------------------------
    def build_channel(M):
        ph = math.radians(TILT)               # φ (wall tilt from vertical)
        t = ch["wall_t"]
        mid_y = (ch["top_half"] + ch["bot_half"]) / 2.0     # 0.375
        uy, uz = math.sin(ph), math.cos(ph)   # u: up-slope unit vector
        ny, nz = math.cos(ph), -math.sin(ph)  # n: outward normal (local +Y, θ=−φ)
        ext = SLOPE_LEN * (ch["wall_ext"] - 1.0)   # the extension (downwards only)
        cy = mid_y + (t / 2.0) * ny - 0.5 * ext * uy
        cz = -ch["depth"] / 2.0 + (t / 2.0) * nz - 0.5 * ext * uz
        cz -= ch["edge_sink"]                 # top edge sinks (avoids coplanarity)
        xa, xb = ch["x_back"], ch["x_end"] + 0.30      # buried 0.30 into the headwall
        cx = (xa + xb) / 2.0
        for tag, sgn in (("N", 1.0), ("S", -1.0)):
            sc._oriented_box(
                stage, f"{ROOT}/ChWall_{tag}",
                (cx, sgn * cy, cz),
                (xb - xa, t, SLOPE_LEN * ch["wall_ext"]), M["chwall"],
                collider=True, rotx=-sgn * TILT)
        # bed slab (invert) - carries the wall bottoms and seals. Exposed width between the walls is 2·bot_half.
        BOX(f"{ROOT}/ChInvert",
            (cx, 0.0, -ch["depth"] - ch["invert_t"] / 2.0),
            (xb - xa, 2.0 * ch["invert_half"], ch["invert_t"]),
            M["chwall"], col=True)
        # rear cap of the covered stretch (blocks distant light leaks)
        BOX(f"{ROOT}/ChBackCap",
            (ch["x_back"] - 0.15, 0.0, -ch["depth"] / 2.0),
            (0.30, 2.0 * ch["invert_half"], ch["depth"] + 0.4), M["dark"])
        print(f"[기하] 측구 상폭 {2 * ch['top_half']:.2f} 하폭 "
              f"{2 * ch['bot_half']:.2f} 깊이 {ch['depth']:.2f} · "
              f"내벽 기울기 {TILT:.3f}° · 사면장 {SLOPE_LEN:.4f} m")

    def build_road_paint(M):
        """White centre dashes + edge line on the road side (paint boxes, proud 0.002)."""
        rd = PARAMS["road"]
        ds = PARAMS["dash"]
        n = 0
        x = rd["x0"] + 1.0
        while x + ds["length"] <= rd["x1"]:
            BOX(f"{ROOT}/Dash_{n}",
                (x + ds["length"] / 2.0, ds["y"], ds["proud"] - 0.01),
                (ds["length"], ds["w"], 0.02), M["paint"])
            x += ds["period"]
            n += 1
        el = PARAMS["edge_line"]
        BOX(f"{ROOT}/EdgeLine",
            ((rd["x0"] + rd["x1"]) / 2.0, el["y"], el["proud"] - 0.01),
            (rd["x1"] - rd["x0"], el["w"], 0.02), M["paint"])

    # -------------------------------------------------------------------
    # grass overhang - low build_hedge strips straddling the opening edge (y=+0.50)
    # -------------------------------------------------------------------
    def build_overhang(M):
        ov = PARAMS["overhang"]
        rng = random.Random(int(ov["seed"]))
        step = ov["x_span"] / float(ov["count"])
        for i in range(int(ov["count"])):
            xa = ov["x0"] + i * step   # r4: jitter removed - a continuous grass lip with no gaps (fixes the broken-plank look)
            xb = xa + rng.uniform(ov["len_lo"], ov["len_hi"])
            y_in = ch["top_half"] - rng.uniform(ov["over_lo"], ov["over_hi"])
            y_out = ch["top_half"] + rng.uniform(ov["out_lo"], ov["out_hi"])
            h = rng.uniform(ov["h_lo"], ov["h_hi"])
            sc.build_hedge(stage, f"{ROOT}/Overhang_{i}", xa, y_in, xb, y_out,
                           h, mtl=M["grass"], base_z=-0.04)  # r1: sunk into the verge surface (fixes floating)

    # -------------------------------------------------------------------
    # fallen leaves on the channel bed - patch plates + scattered ellipsoids (fixed seed)
    # -------------------------------------------------------------------
    def build_bed_leaf(M):
        bl = PARAMS["bed_leaf"]
        rng = random.Random(int(bl["seed"]))
        z_top = -ch["depth"] + bl["sink"]      # 2.5 cm above the bed slab top face
        step = bl["x_span"] / float(bl["patches"])
        for i in range(int(bl["patches"])):
            xa = bl["x0"] + i * step + rng.uniform(0.0, step * 0.5)
            xb = xa + rng.uniform(bl["len_lo"], bl["len_hi"])
            BOX(f"{ROOT}/BedLeaf_{i}",
                ((xa + xb) / 2.0, rng.uniform(-0.05, 0.05),
                 z_top - bl["thick"] / 2.0),
                (xb - xa, 2.0 * bl["y_half"], bl["thick"]), M["leafbed"])
        UsdGeom.Xform.Define(stage, f"{ROOT}/BedLeaves")
        mats = [M[f"leaf_{i}"] for i in range(len(mp["leaf_tints"]))]
        sx, sy, sz = bl["scale"]
        jlo, jhi = bl["jitter"]
        for i in range(int(bl["scatter"])):
            x = rng.uniform(ch["x_open"] + 0.3, ch["x_end"] - 0.5)
            y = rng.uniform(-ch["bot_half"] + 0.03, ch["bot_half"] - 0.03)
            j = rng.uniform(jlo, jhi)
            a, b = sx * j, sy * j
            if rng.random() < 0.5:
                a, b = b, a
            sc.add_sphere(stage, f"{ROOT}/BedLeaves/Leaf_{i}",
                          (x, y, -ch["depth"] + bl["lift"]), (a, b, sz * j),
                          mats[rng.randrange(len(mats))])

    # -------------------------------------------------------------------
    # box culvert mouth - the opening split into 4 (lesson 5) + dark recess
    # -------------------------------------------------------------------
    def build_culvert(M):
        cv = PARAMS["culvert"]
        cx = (cv["x0"] + cv["x1"]) / 2.0
        lx = cv["x1"] - cv["x0"]
        # (1) left (2) right (outside the opening y +-op_half, full height)
        for tag, ya, yb in (("N", cv["op_half"], cv["y_half"]),
                            ("S", -cv["y_half"], -cv["op_half"])):
            BOX(f"{ROOT}/Culvert_{tag}",
                (cx, (ya + yb) / 2.0, (cv["z_top"] + cv["z_bot"]) / 2.0),
                (lx, yb - ya, cv["z_top"] - cv["z_bot"]), M["conc"], col=True)
        # (3) lintel (from the opening top to the headwall crown)
        BOX(f"{ROOT}/Culvert_Top",
            (cx, 0.0, (cv["op_top"] + cv["z_top"]) / 2.0),
            (lx, 2.0 * cv["op_half"], cv["z_top"] - cv["op_top"]),
            M["conc"], col=True)
        # (4) lower sill (1 cm above the invert -> avoids coplanarity + stages an entry step)
        BOX(f"{ROOT}/Culvert_Sill",
            (cx, 0.0, (cv["z_bot"] + cv["sill_top"]) / 2.0),
            (lx, 2.0 * cv["op_half"], cv["sill_top"] - cv["z_bot"]),
            M["conc"], col=True)
        # dark recess (the darkness behind the opening) - never pure black: constant 0.030 + light through the opening
        BOX(f"{ROOT}/CulvertDark",
            ((cv["x1"] + cv["dark_x1"]) / 2.0, 0.0,
             (cv["z_bot"] + cv["dark_top"]) / 2.0),
            (cv["dark_x1"] - cv["x1"], 2.0 * cv["dark_half"],
             cv["dark_top"] - cv["z_bot"]), M["dark"])

    # -------------------------------------------------------------------
    # cues (cue) - default OFF
    # -------------------------------------------------------------------
    def build_cues(M):
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]
            sc.build_railing_line(
                stage, f"{ROOT}/Rail", rl["y"], rl["x0"], rl["x0"],
                rl["x1"] - rl["x0"], 0.0, lambda x: 0.0, M["rail"],
                rail_h=rl["rail_h"], post_r=rl["post_r"],
                spacing=rl["spacing"], rail_r=rl["rail_r"],
                rail_mid_r=rl["rail_mid_r"],
                rail_mid_drop=rl["rail_mid_drop"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile",
                             ch["x_open"] - tc["depth"], ch["x_open"],
                             -ch["top_half"], ch["top_half"], M["conc"],
                             z=PARAMS["cover"]["top"], proud=tc["proud"])

    # -------------------------------------------------------------------
    # dressing + horizon closure
    # -------------------------------------------------------------------
    def build_dressing(M):
        fc = PARAMS["fence"]
        BOX(f"{ROOT}/Fence",
            ((fc["x0"] + fc["x1"]) / 2.0, fc["y"], fc["h"] / 2.0),
            (fc["x1"] - fc["x0"], fc["t"], fc["h"]), M["wood"], col=True)
        BOX(f"{ROOT}/FenceCap",
            ((fc["x0"] + fc["x1"]) / 2.0, fc["y"], fc["h"] + fc["cap_h"] / 2.0),
            (fc["x1"] - fc["x0"], fc["t"] + 2 * fc["cap_over"], fc["cap_h"]),
            M["wood"])
        for i, t in enumerate(PARAMS["trees"] + PARAMS["trees_v6"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", t["cx"], t["cy"], 0.0,
                          M["woodc"], M["canopy_a"], M["canopy_b"])
        for key, bd in PARAMS["houses"].items():
            sc.build_building(stage, f"{ROOT}/House_{key}", bd, M["brick"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_utility_line(M)
        build_driveway(M)
        build_kerb_props(M)

    # -------------------------------------------------------------------
    # [v6-(1)] 4 utility poles + 3 wires - verge y=+4.20 (3.70 m from the opening edge).
    #   the shadows run only toward +Y (the fence side), so the channel's partial-shade profile is unaffected.
    #   each span is approximated by a mid-point sag (2-segment polyline) - a droop silhouette without curved prims.
    # -------------------------------------------------------------------
    def build_utility_line(M):
        pl = PARAMS["pole"]
        xs = pole_xs()                          # v5.1 §3 even-spacing jitter
        for i, x in enumerate(xs):
            base = f"{ROOT}/Pole_{i}"
            CYL(f"{base}/Shaft", (x, pl["y"], pl["h"] / 2.0),
                pl["r"], pl["h"], M["pole"], col=True)
            # crossarm - its top face touches the underside of the wires (wire_z − wire_r)
            arm_top = pl["wire_z"] - pl["wire_r"]
            BOX(f"{base}/Arm", (x, pl["y"], arm_top - pl["arm_h"] / 2.0),
                (pl["arm_t"], pl["arm_len"], pl["arm_h"]), M["pole"])
        # wires: the spans (pole->pole) + a stub on the far side (terminating behind every camera)
        spans = [(pl["stub_x"], xs[0], pl["stub_z"], pl["wire_z"])]
        spans += [(xs[k], xs[k + 1], pl["wire_z"], pl["wire_z"])
                  for k in range(len(xs) - 1)]
        for s, (xa, xb, za, zb) in enumerate(spans):
            xm = (xa + xb) / 2.0
            zm = (za + zb) / 2.0 - pl["sag"]
            for w, dy in enumerate(pl["wire_dy"]):
                y = pl["y"] + dy
                _wire(f"{ROOT}/Wire_{s}_{w}a", (xa, y, za), (xm, y, zm),
                      pl["wire_r"], M["wire"])
                _wire(f"{ROOT}/Wire_{s}_{w}b", (xm, y, zm), (xb, y, zb),
                      pl["wire_r"], M["wire"])

    # -------------------------------------------------------------------
    # [v6-(2)] house driveway - **across the road** (7.4 m from the channel). Overlaps the road by 0.15
    #   + top proud 0.002 -> avoids coplanar Z-fighting. Buried 0.15 under the house A shell.
    # -------------------------------------------------------------------
    def build_driveway(M):
        dw = PARAMS["driveway"]
        BOX(f"{ROOT}/Driveway",
            ((dw["x0"] + dw["x1"]) / 2.0, (dw["y0"] + dw["y1"]) / 2.0,
             dw["top"] - dw["thick"] / 2.0),
            (dw["x1"] - dw["x0"], dw["y1"] - dw["y0"], dw["thick"]),
            M["conc"], col=True)

    # -------------------------------------------------------------------
    # [v6-(3)] mailbox · wheelie bin - shoulders either side of the driveway (y ~ −8.6, across the road).
    # -------------------------------------------------------------------
    def build_kerb_props(M):
        mb = PARAMS["mailbox"]
        CYL(f"{ROOT}/Mailbox/Post", (mb["cx"], mb["cy"], mb["post_h"] / 2.0),
            mb["post_r"], mb["post_h"], M["mailbox"], col=True)
        BOX(f"{ROOT}/Mailbox/Box",
            (mb["cx"], mb["cy"], mb["post_h"] + mb["h"] / 2.0),
            (mb["d"], mb["w"], mb["h"]), M["mailbox"])
        bn = PARAMS["binbox"]
        BOX(f"{ROOT}/Bin/Body", (bn["cx"], bn["cy"], bn["h"] / 2.0),
            (bn["w"], bn["d"], bn["h"]), M["bin"], col=True)
        BOX(f"{ROOT}/Bin/Lid", (bn["cx"], bn["cy"], bn["h"] + bn["lid_t"] / 2.0),
            (bn["w"] + 0.02, bn["d"] + 0.02, bn["lid_t"]), M["bin_lid"])

    # -------------------------------------------------------------------
    # [W2] ground_kit - P17 verge_rural (**natural scene**). Two plans: the cover slab
    #   and the roadway. Zero urban infrastructure is enforced in code by `plan_ground` (§3.4).
    #   the U-channel identity geometry (channel section, culvert, lip) is not touched at all.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["dark"], crack=M["dark"], patch=M["conc"],
                  patch_cut=M["dark"], weed=M["grass"],
                  stain_dirt=M["leafbed"])
        total = 0
        for tag, gp in ground_plans():
            if tag == "road":
                M2 = dict(M2)
                M2.update(patch=M["asphalt"], patch_cut=M["paint"])
            res = gk.apply_ground(kit, f"{ROOT}/GKit/{tag.capitalize()}", gp, M2,
                                  skin_exclude=sc.skin_exclude,
                                  scatter=sc.scatter_debris)
            total += res["prims"]
            print(f"[ground_kit] sceneD3 P17/{tag} · 프림 {res['prims']} · "
                  f"δmax {res['gt_delta_max']:.4f} · "
                  f"unit_cell {res['unit_cell']}")
        return total

    def build_horizon(M):
        bh = PARAMS["back_hedge"]
        # [v5.1 §3·§4] even 26 m spacing -> +-1.0 m jitter + +-5% tint jitter per stretch.
        #   (4 identical materials in a row = a 'cloned wall' look. Real hedges differ in green
        #    from stretch to stretch through species and upkeep.)
        for i, hx in enumerate(back_hedge_xs()):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           hx - bh["length"] / 2.0,
                           bh["cy"] - bh["sy"] / 2.0,
                           hx + bh["length"] / 2.0,
                           bh["cy"] + bh["sy"] / 2.0, 1.9, base_z=0.0,
                           tint=bc.jit_tint((0.35, 0.45, 0.28), hx, 0.0,
                                            "bhTintD3", amp=0.05))
        for i, r in enumerate(PARAMS["ridge"]):
            BOX(f"{ROOT}/Ridge_{i}", (r["cx"], r["cy"], r["h"] / 2.0),
                (r["t"], r["sy"], r["h"]), M[f"ridge_{i}"], col=True)
        # [v6-(4)] treeline - breaks the cut line in front of the ridge with canopy silhouettes (clears the white wall).
        tl = PARAMS["treeline"]
        for i, (cy, h) in enumerate(zip(tl["cys"], tl["hs"])):
            sc.build_hedge(stage, f"{ROOT}/TreeLine_{i}",
                           tl["x0"], cy - tl["span"] / 2.0,
                           tl["x1"], cy + tl["span"] / 2.0, h,
                           mtl=M["treeline"], base_z=tl["base_z"])

    def build_flat_fill(M):
        """hazard_stairs=False control : the opening is filled, flat z=0 throughout."""
        by = PARAMS["beyond"]
        # [W2-0 · P-A] cover-surface elements are placed in the control too -> skin OFF.
        sc.skin_exclude(f"{ROOT}/FlatFill")
        rd = PARAMS["road"]
        BOX(f"{ROOT}/FlatFill",
            ((rd["x0"] + rd["x1"]) / 2.0, (by["y0"] + by["y1"]) / 2.0,
             by["top"] - by["thick"] / 2.0),
            (rd["x1"] - rd["x0"], by["y1"] - by["y0"], by["thick"]),
            M["grass"], col=True)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_ground(M)
    build_road_paint(M)
    if cfg["hazard_stairs"]:
        build_cover(M)
        build_channel(M)
        build_bed_leaf(M)
        if cfg["grass_overhang"]:
            build_overhang(M)
        build_culvert(M)
        build_cues(M)
    else:
        build_flat_fill(M)

    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements - after the dressing (scatter convention)
    build_horizon(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        if cfg["cue_scene_dressing"]:
            _dressing_report()
        print(f"[SMOKE] sceneD3 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["verge_walk"]
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
        sc.capture_pipeline(simulation_app, views, out_dir,
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD3_{ts}.png")
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
    main()
