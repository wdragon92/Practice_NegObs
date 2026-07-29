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
  thickness / nose_over / riser_cover in PARAMS["snow"] govern step-edge visibility.
  The defaults are the geometry-map spec values (0.05 / 0.06 / 0.50); to bury the edges further
  than the reference, raise them toward (0.09 / 0.12 / 0.85). See the PARAMS comments for detail.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneC1_snow_stairs.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneC1_snow_stairs.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneC1_snow_stairs.py

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

    # ─── snow layer [signature parameters] ──────────────────────────────
    #  thickness   snow depth. Raising it thickens the ridge on the tread top so the
    #              edge contrast falls against the step height. Geometry-map spec 0.05. Sweep 0.05->0.09.
    #  nose_over   forward nosing overhang (snow eave). Raising it covers the next step so the
    #              nosing curls round and vanishes. Geometry-map spec 0.06. Sweep 0.06->0.12.
    #  riser_cover fraction of the upper riser covered (0.5=upper half). Raising it shrinks the
    #              dark band on the riser face so the profile approaches a ramp. Sweep 0.50->0.85.
    #  lip_recess  how far the eave fin is set back from the slab front edge (rounded look).
    #  side_over   width by which the snow spills over the stair flank (doubles as coplanar avoidance).
    #  embed_*     depth buried into the solid below (Z-fighting guard, no visual effect).
    # ────────────────────────────────────────────────────────────────────
    snow=dict(thickness=0.05, nose_over=0.06, riser_cover=0.50,
              lip_recess=0.15, side_over=0.010,
              embed_step=0.010, embed_plate=0.020,
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
    hedge_cap=dict(over=0.05, t=0.05),
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


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / grid    — 상부 테라스·계단·하부 평지가 하나의 백색면으로 읽히는가
 2. grazing_top·h0.3   — 단 에지가 둥근 융기선으로만 암시되는가(특색 1순위)
 3. rail_side          — 난간·콘크리트 스트링어가 유일 단서로 잔존하는가
 4. snow_cover ON/OFF  — 눈 제거 시 계단 코어 기하(단 위치·낙차) 불변인가
 5. 조명               — 무태양 저대비인가(경질 그림자 0), 눈 과노출/흑화 없는가
 6. 재질·Z파이팅       — 눈/콘크리트 경계, 처마 핀, 평판 이음에 깜빡임 없는가"""


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
    # Snow layer [signature] - per-tread snow boxes (+eave fin) · approach plates · railing strip
    #   * The eave fin is set back from the slab front edge by lip_recess and bites 5mm upward to
    #     approximate a "rounded nosing" profile (no coplanar faces).
    #   * The upper plate only reaches x0+nose_over, becoming an eave that covers the first riser
    #     without blocking the drop space beneath it (honours the intent of regression guard §A-3).
    # -------------------------------------------------------------------
    def build_snow(M):
        sn = PARAMS["snow"]
        st = PARAMS["stairs"]
        tr = PARAMS["terrace"]
        lo = PARAMS["lower"]
        t = sn["thickness"]
        over = sn["nose_over"]
        so = sn["side_over"]
        sy0, sy1 = st["y0"] - so, st["y1"] + so
        scy = (sy0 + sy1) / 2.0
        sLy = sy1 - sy0
        fLy = sLy - 0.010                    # eave fin width (narrower than the slab)

        def _slab(tag, xa, xb, ztop, lip):
            z_hi = ztop + t
            z_lo = ztop - sn["embed_step"]
            # Bury the trailing edge 1cm into the solid ahead (previous step / upper terrace) to avoid a coplanar face at x=xa
            xa_s = xa - 0.010
            xb_s = xb + (over if lip else 0.0)
            BOX(f"{ROOT}/Snow/Slab_{tag}",
                ((xa_s + xb_s) / 2.0, scy, (z_hi + z_lo) / 2.0),
                (xb_s - xa_s, sLy, z_hi - z_lo), M["snow"])
            if lip:
                # 12mm bite - it must sit on a different plane from the next slab's trailing edge (10mm) so that
                # no coplanar face appears even in sweeps that raise the concealment (riser_cover up).
                fx0 = xb - 0.012
                fx1 = xb + over * (1.0 - sn["lip_recess"])
                fz_hi = ztop + 0.005                   # enclosed inside the slab
                fz_lo = ztop - st["riser"] * sn["riser_cover"]
                BOX(f"{ROOT}/Snow/Lip_{tag}",
                    ((fx0 + fx1) / 2.0, scy, (fz_hi + fz_lo) / 2.0),
                    (fx1 - fx0, fLy, fz_hi - fz_lo), M["snow"])

        # (1) Upper approach plate + eave at the stair top edge.
        #    0.1 inset from the site boundary - to avoid a coplanar face with the terrace box flanks
        #    (the inset edge is 60m away, so it never enters the frame).
        ins = 0.10
        z_hi = tr["z_top"] + t
        z_lo = tr["z_top"] - sn["embed_plate"]
        px0 = tr["x0"] + ins
        px1 = st["x0"] + over
        BOX(f"{ROOT}/Snow/PlateTop",
            ((px0 + px1) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
             (z_hi + z_lo) / 2.0),
            (px1 - px0, (tr["y1"] - tr["y0"]) - 2.0 * ins, z_hi - z_lo),
            M["snow"])
        lz_hi = st["z_top"] + 0.005
        lz_lo = st["z_top"] - st["riser"] * sn["riser_cover"]
        lx0 = st["x0"] - 0.012                  # different plane from the trailing edge of Slab_1 (10mm)
        lx1 = st["x0"] + over * (1.0 - sn["lip_recess"])
        BOX(f"{ROOT}/Snow/LipTop",
            ((lx0 + lx1) / 2.0, scy, (lz_hi + lz_lo) / 2.0),
            (lx1 - lx0, fLy, lz_hi - lz_lo), M["snow"])

        # (2) Per-tread snow boxes (the last step joins the lower ground, so no eave)
        for i in range(1, st["nsteps"] + 1):
            xa = st["x0"] + st["tread"] * (i - 1)
            xb = xa + st["tread"]
            ztop = st["z_top"] - st["riser"] * i
            _slab(str(i), xa, xb, ztop, lip=(i < st["nsteps"]))

        # (3) Lower approach plate (5cm overlap with the last step slab · top face 2mm lower)
        bx0 = RUN - lo["x_back"]
        bx1 = lo["x1"] - ins
        z_hi = LOWER_TOP + t
        z_lo = LOWER_TOP - sn["embed_plate"]
        BOX(f"{ROOT}/Snow/PlateBot",
            ((bx0 + bx1) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             (z_hi + z_lo) / 2.0),
            (bx1 - bx0, (lo["y1"] - lo["y0"]) - 2.0 * ins, z_hi - z_lo),
            M["snow"])

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
        sc.build_slope(stage, f"{ROOT}/Snow/RailStripSlope", 0.0, z_top,
                       RUN, DROP, rl["y"] - w / 2.0, rl["y"] + w / 2.0,
                       th, M["snow"], margin=0.0, collider=False)

    # -------------------------------------------------------------------
    # cues - nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        if cfg["cue_nosing"]:
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
                if x <= 0.0:
                    return LIFT
                return LIFT - SLOPE_K * min(x, RUN)

            sc.build_railing_line(
                stage, f"{ROOT}/StairRail_P", rl["y"], rl["x_start"],
                st["x0"], RUN, DROP, bank_ground, M["rail"],
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
                  patch_cut=M["stair"], manhole=M["rail"], gully=M["rail"],
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
            BOX(f"{ROOT}/Snow/PoleCap",
                (po["cx"], po["cy"], base_top + po["h"] + po["cap_t"] / 2.0
                 - 0.01),
                (po["r"] * 2.4, po["r"] * 2.4, po["cap_t"]), M["snow"])
        # Distant buildings - C(+X) is plinthed on the lower ground, D(-X) at terrace level
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
        low_top = (LOWER_TOP if cfg["hazard_stairs"] else 0.0) + LIFT

        def base_of(kind):
            return LIFT if kind == "upper" else low_top

        def cap(path, center, size):
            """Snow cap thin plate - created only when snow_cover is ON (twin consistency)."""
            if cfg["snow_cover"]:
                BOX(path, center, size, M["snow"])

        # (1) Bench (seat + 4 legs + back) - snow caps on the seat and the top of the back
        bs = PARAMS["bench"]
        for i, bd in enumerate(PARAMS["benches"]):
            bz = base_of(bd["base"])
            pfx = f"{ROOT}/Bench_{i}"
            # [v5.1 §3] Fixes the axis-aligned/exact-position look. Bench 0 is by the snow pile and the stair
            #   shoulder, bench 1 sits next to the snow pile 0 anchor, so the jitter is limited to 0.18
            #   and does not eat into the existing clearance (0.22 m).
            _dx, _dy = bc.jit_pos(bd["cx"], bd["cy"], "benchC1", amp=0.18)
            _yaw = bc.jit_yaw(bd["cx"], bd["cy"], "benchC1", lo=3.0, hi=8.0,
                              base=bd["yaw"])
            sc.build_bench(stage, pfx, bd["cx"] + _dx, bd["cy"] + _dy, bz,
                           M["wood"], length=bs["length"], width=bs["width"],
                           height=bs["height"], yaw=_yaw)
            # The child prims below are in the build_bench root Xform local frame (rotation inherited)
            back_y = -(bs["width"] / 2.0 - 0.04)
            BOX(f"{pfx}/Back", (0.0, back_y, bs["height"] + bs["back_h"] / 2.0),
                (bs["length"], 0.06, bs["back_h"]), M["wood"])
            cap(f"{pfx}/SnowSeat",
                (0.0, 0.0, bs["height"] + bs["cap_t"] / 2.0 - 0.012),
                (bs["length"] + 0.05, bs["width"] + 0.05, bs["cap_t"]))
            cap(f"{pfx}/SnowBack",
                (0.0, back_y,
                 bs["height"] + bs["back_h"] + bs["cap_t"] / 2.0 - 0.012),
                (bs["length"] + 0.04, 0.11, bs["cap_t"]))

        # (2) Street lamp (pole + one-sided arm + head) - snow caps on the pole top and the head
        lm = PARAMS["lamp"]
        for i, ld in enumerate(PARAMS["lamps"]):
            bz = base_of(ld["base"])
            pfx = f"{ROOT}/Lamp_{i}"
            # [v5.1 §3] Position jitter +-0.15 m. The shadow still falls only on the x<0 terrace
            #   (shadow direction (−0.879,+0.477), length 8.5 m), so the concealment condition on the
            #   stair treads is unchanged.
            _dx, _dy = bc.jit_pos(ld["cx"], ld["cy"], "lampC1", amp=0.15)
            cx, cy, arm = ld["cx"] + _dx, ld["cy"] + _dy, ld["arm"]
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
                (lm["head_w"] + 0.04, lm["head_l"] + 0.04, lm["cap_t"]))
            cap(f"{pfx}/SnowTop",
                (cx, cy, bz + lm["pole_h"] + lm["cap_t"] / 2.0 - 0.010),
                (lm["pole_r"] * 2.6, lm["pole_r"] * 2.6, lm["cap_t"]))

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
            (sp["panel_t"] + 0.05, sp["panel_w"] + 0.05, sp["cap_t"]))

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
                (sx + 2.0 * hc["over"], sy + 2.0 * hc["over"], hc["t"]))

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
                (sx + 2.0 * (hs["eave"] - hs["cap_inset"]),
                 sy + 2.0 * (hs["eave"] - hs["cap_inset"]), hs["cap_t"]))
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
                (ch + 0.06, ch + 0.06, hs["cap_t"]))
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
