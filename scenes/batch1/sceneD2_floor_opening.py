# -*- coding: utf-8 -*-
"""
sceneD2_floor_opening.py - NegObs synthetic scene 29: construction-site floor opening (Isaac Sim 4.5)

Type     : D2 non-stair drop - an unguarded opening in a frame-stage floor slab (drop 3.0 m)
Spec     : Docs/nanobanana_batch1_geometry_map.md §C sceneD2_floor_opening
Look ref : look_refs/d2_floor_opening.jpg
Shared   : scene_common.py (verified API helpers) · scene16_canopy_shadow.py (standard template)

Hazard   : in the middle of a frame-stage floor (concrete slab, form-marked walls) a 1.5x2.0 m
           unguarded opening is cut through, and below it is the basement (z −3.0). The inside of the
           opening reads only as a "black rectangle" under backlight and self-occlusion - with no
           cue of running nosings as a stair would have, only the RGB context (rebar stubs, debris
           ring, perspective of the formwork wall faces) announces that the drop exists.
Note     : the **strongest "black rectangle" confusion pair** with sceneN2 (fresh asphalt patch, GT negative).
           Opening dimensions 1.5x2.0 [fixed] - the condition for the confusion pair to hold.
Goal     : assemble the slab (split into 4 boxes) + basement (floor, formwork walls) + rebar stubs +
           crushed debris scatter + 2 formwork walls / south column openings (light source), and
           adjudicate by render (render only).

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD2_floor_opening.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneD2_floor_opening.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneD2_floor_opening.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0 (west lip of the opening).
"""

import os
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. The key stays hazard_stairs rather than hazard_opening
#     (shared library convention: the single exception for a geometry toggle).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> the opening is filled with slab, giving flat z=0 (control)
    "cue_railing":        False,  # temporary opening safety railing - OFF by default (**unguarded is the point**)
    "cue_tactile":        False,  # not applicable (construction site) - key reserved only
    "cue_material_break": True,   # False -> the basement gets the same material as the slab (contrast removed)
    "cue_nosing":         False,  # yellow warning paint around the opening - OFF by default (unguarded)
    "cue_sign":           False,  # [optional] not implemented - key reserved only
    "cue_scene_dressing": True,   # formwork panels · spoil piles · outside earth mounds · distant ridge
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # Frame-stage floor slab (= ground level). South and west are nearly flush with the outside earth
    # (walking continuity); east and north are closed off by formwork walls -> horizon blocked.
    deck=dict(x_w=-9.0, x_e=8.45, y_s=-6.5, y_n=6.5, z_top=0.0, thick=0.25),

    # * Unguarded opening: 2.0 m along the travel axis x 1.5 m wide. Its west lip is the drop start edge x=0.
    #   [fixed] the condition for the confusion pair with sceneN2 (4x5 m asphalt patch).
    opening=dict(x0=0.0, x1=2.0, y0=-0.75, y1=0.75),

    # Formwork downstand hung under the opening (charred dark) - makes the area right below the lip
    # reliably dark. Its inner face is set 0.01 outside the opening to avoid coplanarity.
    #   z_top -0.24 = bites 0.01 into the slab underside (-0.25) -> avoids horizontal coplanarity.
    skirt=dict(inset=0.01, thick=0.35, z_top=-0.24, z_bot=-0.55),

    # Basement (below the opening). Generously wider than the opening so light through it lands on the
    # floor -> the bounce lights the east wall (the face the camera sees past the opening) = "dark but not 0".
    lower=dict(x0=-5.0, x1=7.0, y0=-4.5, y1=4.5,
               z_floor=-3.0, floor_t=0.5, wall_t=0.35, z_ceil=-0.20),

    # Formwork walls (east, north) - storey height 3.2, used to close the horizon.
    #   The outer wall faces sit **strictly inside** the deck edges (east 8.30<8.45,
    #   north 6.45<6.50), and the east and north walls get different z ranges to remove corner coplanarity.
    walls=dict(t=0.30, n_t=0.28, h=3.2, x_face=8.0, y_face=6.15,
               e_y0=-6.05, e_y1=6.45, n_x0=-8.65, n_x1=8.15,
               n_h_delta=0.06, n_base=-0.12, base=-0.09),

    # South column openings (colonnade) - a light source where outside earth and sky show between the columns
    colonnade=dict(y_c=-6.2, size=0.45, h=3.2,
                   xs=[-6.5, -3.5, -0.5, 2.5, 5.5]),

    # Rebar stubs: 6 straight (vertical) + 2 bent (_oriented_box approximation) + 1 hook
    rebar=dict(r=0.006, h=0.36, z_c=0.13,
               straight=[(-0.20, -0.55), (-0.20, 0.60), (0.70, -0.95),
                         (1.55, 0.96), (2.20, -0.30), (2.22, 0.62)],
               bent=[(0.05, -0.98, 32.0, 18.0), (2.32, 0.05, 27.0, -64.0)],
               bent_len=0.42, bent_t=0.013,
               # hook: placed to pierce the top of the straight stub at (-0.20,-0.55) (no floating)
               hook=dict(cx=-0.20, cy=-0.42, z=0.293, lx=0.30, t=0.013,
                         yaw=90.0)),

    # ═══ [W2 ground_kit] P15 slab_construction - spec §5.8 D2 row ═══════════
    #  Prescription: **wear remnants** of the opening marking paint (20-30 % yellow left) · ink snap
    #  lines (partial runs) · cold joints · efflorescence stains · 8-15 footprints.
    #  Basis: Occupational Safety and Health Standards Rules §43 requires "marking that it is an
    #  opening", and in reality that is **floor paint**, not a sign, and it is more than half worn away by traffic after the pour.
    #  * GT-V (§6.3): **no element whatsoever** may overhang the opening (x 0…2 · y +-0.75).
    #    The region far end is cut at the opening's west lip (x=0) and the opening is passed through
    #    `voids` so that `plan_ground` asserts on every element AABB x opening intersection.
    #  * The opening marking paint is a **U shape** of **2 longitudinal lines (y=+-1.05) + 1 transverse
    #    line (x=-3.00)**. The 2 longitudinal lines are inset 0.15 m from the west lip because of GT-E1′
    #    (paint proud 0.003 x EDGE_K 40 = 0.12 m required `[computed]`).
    #  * [2026-07-30, after kit defect F1 was fixed] the W2-D round had **deferred** the transverse
    #    band - `ground_kit._ik_marking` laid element AABBs along +X ignoring yaw, so a transverse
    #    band was misjudged as "an element crossing the opening" and tripped B8/B6.
    #    Now that F1 is fixed, **those two gates are clean**
    #    `[measured - reproducing the x=-0.225 placement in front of the west lip, B6 and B8 pass and only B7
    #     remains]`. What is left is not a misjudgement but a genuine rule:
    #      GT-E2 - a full-width transverse line just in front of the lip merges with the lip under GRAZE.
    #      At x=-0.225, delta = 19.7/3.1/0.8 rows@1080 (32/32/16 required) `[measured]`.
    #      To pass the d10 E band (7-22 m) the near end must stand back **2.60 m from the lip**
    #      `[computed]`.
    #    -> the band is therefore placed at the west end of the 2 longitudinal lines (x=-3.00), closing
    #      the painted zone into a **U that opens toward the opening**. That matches the real wear order
    #      (the lip side wears first) and §5.8's "20-30 % yellow left" prescription exactly, and it is legal in every cut
    #      (d2 and d5 are outside the E band, d10 has delta 21.0 >= 16 `[measured]`).
    #      A layout wrapping the lip would need a **GT-E2-x listing** (EXPECTED_FP) like tactile paving,
    #      and that is the GRAZE adjudicator's remit - a supervisor agenda item.
    gkit=dict(
        region=(-9.0, -6.0, 0.0, 6.0),
        #  Opening marking paint remnants - (x0, y0, yaw, length). Inset 0.15 from the west lip.
        #  The third line is a yaw 90 deg transverse band: centred at x=-3.00, y -1.125…+1.125 (covering out to
        #  the outer edge of the 2 longitudinal 0.15-wide lines so the corners interlock).
        mark_lines=[(-3.00, -1.05, 0.0, 2.85), (-3.00, 1.05, 0.0, 2.85),
                    (-3.00, -1.125, 90.0, 2.25)],
        #  Footprint trail - traces of walking toward the opening (never across it).
        foot_path=[(-7.0, -0.90), (-1.2, -0.30)],
        foot_n=12,
    ),

    # Crushed concrete debris scatter (fixed seed)
    debris=dict(seed=2907, count=46, perim_ratio=0.6,
                x0=-2.2, x1=4.2, y0=-2.6, y1=2.6,
                ring_lo=0.03, ring_hi=0.55,
                s_lo=0.030, s_hi=0.130, sink=0.35),

    # cue (OFF by default - being unguarded is this scene's hazard essence)
    nosing=dict(width=0.15, proud=0.002, color=(0.85, 0.72, 0.10)),
    opening_rail=dict(rail_h=0.95, post_r=0.025, rail_r=0.022,
                      mid_h=0.48, offset=0.45),

    # Outside ground (earth) - only a 0.05 level difference from the slab -> secures walking continuity (lesson 9)
    #   overlap: the 4 ground boxes are pushed 6 cm inside the building footprint to remove vertical
    #   coplanarity with the slab sides (front/back butt joint -> Z-fighting).
    ground=dict(z_top=-0.05, thick=1.0, half=60.0, overlap=0.06),
    dressing=dict(
        # 3 formwork panels (leaned against the north wall)
        panels=[dict(cx=3.0), dict(cx=4.4), dict(cx=5.8)],
        panel=dict(w=1.15, t=0.055, h=2.35, y_c=6.10, tilt=12.0),
        # 2 spoil / gravel piles
        piles=[dict(cx=6.1, cy=-4.6, sx=1.7, sy=1.15, sz=0.42),
               dict(cx=-6.8, cy=4.1, sx=1.2, sy=0.9, sz=0.30)],
        # 2 outside earth mounds + distant ridge (closes the -Y horizon)
        #   v2 (context dressing): r2 verdict "the right mound reads as a smooth pebble, out of place" ->
        #   made **low and wide + split into 3 lobes** to become a spoil pile. Peak ~ gz-sink+sz.
        #   (e.g. -0.05-0.55+1.45 = 0.85 m high x 18 m wide = a spoil profile)
        mounds=[dict(cx=-16.0, cy=-26.0, sink=0.55,
                     lobes=[(0.0, 0.0, 9.0, 5.2, 1.45),
                            (7.5, 2.4, 5.6, 3.4, 1.05),
                            (-7.0, -1.8, 6.2, 3.6, 0.95)]),
                dict(cx=15.0, cy=-33.0, sink=0.60,
                     lobes=[(0.0, 0.0, 10.5, 5.8, 1.50),
                            (-8.0, 2.0, 6.0, 3.6, 1.10),
                            (8.5, -1.5, 5.4, 3.2, 0.95)])],
        ridge=dict(cy=-52.0, half_x=58.0, t=8.0, h=8.5),
    ),

    # ─── context dressing v2 (2026-07-27, fixing the barren look) ────────────────────────────
    #   Purpose: make "this is a frame-stage construction site" legible. Every element belongs to cue_scene_dressing.
    #   * Unchanged: opening (1.5x2.0) · rebar stubs · debris scatter · slab 4-way split · skirt · basement.
    #   * Placement principles (numeric checks in the build_site_dressing docstring):
    #     (1) grid_views(gy=0) cameras -> opening sight wedge half-width |y| <= 0.75·(x+10)/10.
    #        Every new solid sits **outside** that wedge (clearance 1.6 m or more).
    #     (2) the opening itself **stays unguarded** - the safety fence keeps 3.9 m or more from it and
    #        is placed as a **single straight row** (north side) that does not surround the opening.
    #     (3) the distant crane only works at a bearing that grazes the south end of the east wall (x 8.15, h 3.2) -
    #        sight-line clearance confirmed by coordinate check (see comments).
    site=dict(
        # Rebar bundle (laid down). Low profile (<=0.20 m), so it blocks no sight line.
        rebar_bundles=[dict(tag="A", cx=-3.40, cy=3.90, yaw=4.0, L=5.0,
                            rows=3, per_row=4),
                       dict(tag="B", cx=3.20, cy=-3.40, yaw=-7.0, L=4.2,
                            rows=2, per_row=5)],
        bundle=dict(r=0.010, batten_w=0.16, batten_h=0.085, batten_d=0.45,
                    strap_t=0.012),
        # Cement bag pallets
        bagpallets=[dict(tag="A", cx=-3.60, cy=-3.60, yaw=12.0, layers=4),
                    dict(tag="B", cx=4.60, cy=3.40, yaw=-8.0, layers=3)],
        bagpallet=dict(pw=1.20, pd=1.00, pt=0.14, bw=0.52, bd=0.34, bh=0.11,
                       seed=6203),
        # 3 movable safety fences (single north row - **the opening staying unguarded is the point**)
        fences=[dict(cx=-1.00, cy=4.60), dict(cx=1.10, cy=4.60),
                dict(cx=3.20, cy=4.60)],
        fence=dict(w=2.00, h=1.90, post_r=0.024, rail_r=0.018, bar_r=0.008,
                   n_bar=7, foot_d=0.62, foot_w=0.10, foot_h=0.06),
        # Cable reel · tool boxes
        reel=dict(cx=-5.40, cy=2.40, flange_r=0.46, flange_t=0.05,
                  coil_r=0.40, coil_w=0.42),
        toolboxes=[dict(cx=-4.85, cy=1.70, yaw=15.0, w=0.72, d=0.40, h=0.36),
                   dict(cx=-5.95, cy=3.15, yaw=-22.0, w=0.55, d=0.34, h=0.30)],
        # Column safety-slogan panels (textless colour fields) - colonnade indices 3 (x 2.5) and 4 (x 5.5)
        placards=[dict(col=3, z=1.58), dict(col=4, z=1.66)],
        placard=dict(w=0.42, h=0.56, t=0.04, band_h=0.14, proud=0.010),
        # Distant tower crane (assembly of thin boxes, distance ~110 m)
        #   cy=-40: a bearing that clears both the east wall's south end (y -6.05) and the column
        #   (x 5.5, y -6.425..-5.975) with margin (numbers in the build_site_dressing docstring).
        #   Apex 15.4 m at 110 m -> elevation 7.5 deg < frame top limit 8.0 deg.
        crane=dict(cx=100.0, cy=-40.0, base_z=-1.20,
                   mast_w=1.15, mast_top=14.20,
                   apex_w=1.60, apex_top=15.40,
                   jib_len=28.0, jib_w=0.85, jib_h=1.15, jib_z0=13.40,
                   cjib_len=11.0, cjib_w=0.95, cjib_h=1.00, cjib_z0=13.50,
                   cw_w=1.60, cw_d=2.40, cw_h=1.80,
                   hook_dy=-14.0, hook_w=0.46, hook_h=0.85, hook_z0=6.60,
                   rope_w=0.07),
        # Distant ground pad - closes the view so it cannot escape past the existing ground (half 60).
        #   Top face -0.06 = 1 cm below the existing ground (-0.05) -> zero coplanarity in the overlap.
        farpad=dict(x0=45.0, x1=420.0, y0=-260.0, y1=260.0,
                    z_top=-0.06, thick=1.0),
    ),

    material=dict(
        scale=dict(concrete_floor=1.2, concrete_wall=2.0,
                   dirt_park=3.0, gravel=0.9),
        slab_tint=(0.88, 0.86, 0.82),       # cement dust tint (light grey-white)
        lower_wall_tint=(0.58, 0.58, 0.57),  # basement formwork - lower saturation and value
        lower_floor_tint=(0.52, 0.51, 0.49),
        wall_tint=(0.92, 0.91, 0.89),        # above-ground formwork wall (bright)
        # Charred formwork under the opening - sRGB dark band 0.02-0.06 [lesson 1]
        skirt_color=(0.042, 0.042, 0.045), skirt_rough=0.95,
        rebar_color=(0.25, 0.12, 0.08), rebar_metallic=0.8, rebar_rough=0.6,
        debris_colors=[(0.30, 0.29, 0.27), (0.24, 0.23, 0.22),   # r1: 0.55 is perceived as white -> darkened
                       (0.18, 0.175, 0.17)],
        debris_rough=0.95,
        panel_color=(0.46, 0.38, 0.27), panel_rough=0.88,   # plywood formwork
        rail_color=(0.80, 0.60, 0.10), rail_metallic=0.6, rail_rough=0.5,
        # ── context dressing v2 ── (props keep to the 0.18-0.35 mid-tone convention. The 0.02-0.09 dark
        #    band is only for things that are 'actually black', like the opening skirt and the cable coil.)
        bag_color=(0.52, 0.49, 0.43), bag_rough=0.92,       # cement bag (paper)
        fence_color=(0.50, 0.51, 0.53), fence_metallic=0.60,
        fence_rough=0.38,
        cable_color=(0.055, 0.055, 0.060), cable_rough=0.85,  # cable coil (dark)
        tool_color=(0.34, 0.12, 0.09), tool_metallic=0.20, tool_rough=0.55,
        placard_color=(0.68, 0.68, 0.65), placard_rough=0.60,
        placard_band=(0.09, 0.34, 0.18),                    # safety slogan colour band (green)
        crane_color=(0.40, 0.38, 0.33), crane_metallic=0.25,
        crane_rough=0.70,
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
    # ─── basis for SUN_AZ_OFFSET (redefined per scene - brief v3 §A-7) ───
    #   Sun mapping world az ~ 33.5 + offset = 185.5  ->  shadow az = az-180 = 5.5 deg
    #   (1) shadows fall almost due +X (sun behind the camera) -> the slab top face, rebar stubs and
    #      debris are crisp under frontal light, and the opening reads relatively blacker.
    #   (2) direct light through the opening (x 0..2) drifts 3.0/tan(49.79 deg) = 2.53 m horizontally
    #      while falling 3.0 m, landing on the basement floor at x 2.53..4.53.
    #      The bounce off that light pool illuminates the basement east wall (x=7.0), and that wall face is
    #      exactly the region (z -1.6..-0.8) visible past the opening from the h0.9/d4-5 walking eye.
    #      -> geometrically guarantees the **"dark but not fully 0"** goal (spec §C).
    #   (3) the slight +5.5 deg yaw puts the light pool and shadows a touch off-axis, avoiding a flat look.
    #   The [ ] keys (dome_rotation_step 15 deg) allow a further GUI sweep.
    SUN_AZ_OFFSET=152.0,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def fence_placements():
    """[v5.1 §3] 3 movable safety fences - breaks up the even 2.1 m spacing and axis-parallel look.
    Position +-0.18 m · yaw +-3~8 deg (deterministic from a coordinate hash). Temporary fences on a real
    site are not lined up exactly. * The 3.9 m clearance from the opening (which stays unguarded) is
    overwhelmingly larger than the jitter width (0.18), so the 'unguarded opening' feature is unchanged."""
    out = []
    for i, fd in enumerate(PARAMS["site"]["fences"]):
        dx, dy = bc.jit_pos(fd["cx"], fd["cy"], "fenceD2", amp=0.18)
        yaw = bc.jit_yaw(fd["cx"], fd["cy"], "fenceD2", lo=3.0, hi=8.0)
        out.append((i, fd["cx"] + dx, fd["cy"] + dy, yaw))
    return out


def formpanel_xs():
    """[v5.1 §3] x +-0.16 m jitter for the 3 formwork panels leaned against the north wall."""
    return [pd["cx"] + bc.jit_scalar(pd["cx"], 0.0, "panelD2", -0.16, 0.16)
            for pd in PARAMS["dressing"]["panels"]]


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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD2")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "dirt_park", "gravel",
               "hdri", "mdl"]


def ground_plans():
    """[W2 ground_kit] ground plan - the scene assembly and the CPU check use the same function."""
    g = PARAMS["gkit"]
    op = PARAMS["opening"]
    gp = gk.plan_ground(
        "slab_construction", region=tuple(g["region"]),
        z=float(PARAMS["deck"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("opening_lip", float(op["x0"]))],
        voids=((float(op["x0"]), float(op["y0"]),
                float(op["x1"]), float(op["y1"])),),
        dists=(2, 5, 10), scene="sceneD2",
        tactile=(),                     # §12.4 - not applicable (construction site)
        sites=dict(marking=[tuple(m) for m in g["mark_lines"]]),
        overrides=dict(infra=dict(marking=("line", "line", "line")),
                       extras=(("footprints",
                                dict(n=int(g["foot_n"]),
                                     path_pts=[tuple(p)
                                               for p in g["foot_path"]])),)),
        seed=29)
    return [("slab", gp)]


def build_views():
    """Camera presets: grid_views(gy=0.0, orthogonal approach head-on to the opening) + 4 mise-en-scene cuts.

    Spec §C cameras: 'walking approach 4 m · h0.9' -> grid_views d5/h0.9 and the
    mise-en-scene approach (d4·h0.9) both align to that axis.
    """
    views = sc.grid_views(0.0)
    # approach: the eye the spec calls for - a pedestrian facing the opening from 4 m away
    views["approach"] = dict(eye=[-4.0, 0.0, 0.9], tgt=[1.2, 0.0, -0.35])
    # brink: looking down from just in front of the lip - basement floor light pool and formwork wall exposed
    views["brink"] = dict(eye=[-1.0, 0.0, 1.60], tgt=[1.6, 0.15, -2.30])
    # graze: low eye - the concealment framing where the opening flattens into a thin black band (maximum hazard)
    views["graze"] = dict(eye=[-6.0, -0.25, 0.35], tgt=[2.5, 0.05, 0.02])
    # beauty_overview: oblique high angle - opening, rebar and formwork wall corner read together
    views["beauty_overview"] = dict(eye=[-5.2, -5.0, 3.4], tgt=[1.2, 0.4, -0.9])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach/preset_h0.9_d5 — 1.5×2.0 개구가 '검은 사각형'으로 읽히는가(특색)
 2. brink                   — 개구 내부가 어둡되 **완전 0이 아닌가**(PT 8바운스로 판정)
 3. graze (h0.35)           — 저시점에서 개구가 납작해지며 은닉되는가
 4. 철근·부스러기           — 립 주변 스터브 6+2+1본·부스러기 링이 낙차 단서로 작동
 5. 보행 연속성             — 슬래브↔외부 흙 단차 0.05, 개구 우회 가능
 6. Z-파이팅/부유           — 스커트 내면 물림 0.01, 스터브 하단 매입, 거푸집 패널 접지"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene29")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene29"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def OBOX(path, center, size, mtl=None, rotz=0.0, rotx=0.0):
        return sc._oriented_box(stage, path, center, size, mtl,
                                rotz=rotz, rotx=rotx)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def SPH(path, center, scale3, mtl=None):
        return sc.add_sphere(stage, path, center, scale3, mtl)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["slab"] = PBR(
            f"{ROOT}/Looks/Slab", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["slab_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint"])
        M["lower_wall"] = PBR(
            f"{ROOT}/Looks/LowerWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["lower_wall_tint"])
        M["lower_floor"] = PBR(
            f"{ROOT}/Looks/LowerFloor", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["lower_floor_tint"])
        M["dirt"] = PBR(
            f"{ROOT}/Looks/Dirt", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            sca["dirt_park"])
        M["gravel"] = PBR(
            f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"])
        M["skirt"] = PBR(f"{ROOT}/Looks/Skirt",
                         diffuse_color=mp["skirt_color"],
                         roughness_const=mp["skirt_rough"], metallic=0.0)
        M["rebar"] = PBR(f"{ROOT}/Looks/Rebar",
                         diffuse_color=mp["rebar_color"],
                         metallic=mp["rebar_metallic"],
                         roughness_const=mp["rebar_rough"])
        for i, c in enumerate(mp["debris_colors"]):
            M[f"debris{i}"] = PBR(f"{ROOT}/Looks/Debris_{i}",
                                  diffuse_color=c,
                                  roughness_const=mp["debris_rough"])
        M["panel"] = PBR(f"{ROOT}/Looks/Panel",
                         diffuse_color=mp["panel_color"],
                         roughness_const=mp["panel_rough"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=PARAMS["nosing"]["color"],
                          roughness_const=0.75)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # ── context dressing v2 materials ──
        M["bag"] = PBR(f"{ROOT}/Looks/Bag", diffuse_color=mp["bag_color"],
                       roughness_const=mp["bag_rough"])
        M["fence"] = PBR(f"{ROOT}/Looks/Fence", diffuse_color=mp["fence_color"],
                         metallic=mp["fence_metallic"],
                         roughness_const=mp["fence_rough"])
        M["cable"] = PBR(f"{ROOT}/Looks/Cable", diffuse_color=mp["cable_color"],
                         roughness_const=mp["cable_rough"])
        M["tool"] = PBR(f"{ROOT}/Looks/Tool", diffuse_color=mp["tool_color"],
                        metallic=mp["tool_metallic"],
                        roughness_const=mp["tool_rough"])
        M["placard"] = PBR(f"{ROOT}/Looks/Placard",
                           diffuse_color=mp["placard_color"],
                           roughness_const=mp["placard_rough"])
        M["placard_band"] = PBR(f"{ROOT}/Looks/PlacardBand",
                                diffuse_color=mp["placard_band"],
                                roughness_const=mp["placard_rough"])
        M["crane"] = PBR(f"{ROOT}/Looks/Crane", diffuse_color=mp["crane_color"],
                         metallic=mp["crane_metallic"],
                         roughness_const=mp["crane_rough"])
        return M

    # -------------------------------------------------------------------
    # Outside ground (earth) - 4 boxes with the building footprint left empty (does not cover the basement cavity)
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        d = PARAMS["deck"]
        H = g["half"]
        th = g["thick"]
        cz = g["z_top"] - th / 2.0
        ov = g["overlap"]
        # Boundary pushed ov inside the building footprint (the ground top face -0.05 is above the slab
        # underside -0.25, so the overlapping part is hidden behind the slab)
        xw, xe = d["x_w"] + ov, d["x_e"] - ov
        ys, yn = d["y_s"] + ov, d["y_n"] - ov
        BOX(f"{ROOT}/Ground_W", ((-H + xw) / 2.0, 0.0, cz),
            (xw + H, 2.0 * H, th), M["dirt"], col=True)
        BOX(f"{ROOT}/Ground_E", ((xe + H) / 2.0, 0.0, cz),
            (H - xe, 2.0 * H, th), M["dirt"], col=True)
        BOX(f"{ROOT}/Ground_S", ((xw + xe) / 2.0, (-H + ys) / 2.0, cz),
            (xe - xw, ys + H, th), M["dirt"], col=True)
        BOX(f"{ROOT}/Ground_N", ((xw + xe) / 2.0, (yn + H) / 2.0, cz),
            (xe - xw, H - yn, th), M["dirt"], col=True)

    # -------------------------------------------------------------------
    # Slab - **split into 4 boxes around the opening** (brief v3 §A-3 / lesson 5)
    #   No box covers the cavity (the opening).
    # -------------------------------------------------------------------
    def build_slab(M):
        d = PARAMS["deck"]
        op = PARAMS["opening"]
        th = d["thick"]
        # [W2-0 · P-A] the whole 4-way slab split is what ground_kit decorates ->
        #   displacement skin OFF (registered **before the BOX call**). Otherwise the cold joints (engraved
        #   tone), paint remnants (+3 mm) and footprints (+0.6 mm) all vanish under the skin.
        sc.skin_exclude(f"{ROOT}/Slab_W", f"{ROOT}/Slab_E",
                        f"{ROOT}/Slab_S", f"{ROOT}/Slab_N",
                        f"{ROOT}/Slab_Fill")
        cz = d["z_top"] - th / 2.0
        xw, xe, ys, yn = d["x_w"], d["x_e"], d["y_s"], d["y_n"]
        ox0, ox1, oy0, oy1 = op["x0"], op["x1"], op["y0"], op["y1"]
        # (1) west: x_w..opening west lip, full width
        BOX(f"{ROOT}/Slab_W", ((xw + ox0) / 2.0, (ys + yn) / 2.0, cz),
            (ox0 - xw, yn - ys, th), M["slab"], col=True)
        # (2) east: opening east lip..x_e, full width
        BOX(f"{ROOT}/Slab_E", ((ox1 + xe) / 2.0, (ys + yn) / 2.0, cz),
            (xe - ox1, yn - ys, th), M["slab"], col=True)
        # (3) south: opening x range, y_s..opening south lip
        BOX(f"{ROOT}/Slab_S", ((ox0 + ox1) / 2.0, (ys + oy0) / 2.0, cz),
            (ox1 - ox0, oy0 - ys, th), M["slab"], col=True)
        # (4) north: opening x range, opening north lip..y_n
        BOX(f"{ROOT}/Slab_N", ((ox0 + ox1) / 2.0, (oy1 + yn) / 2.0, cz),
            (ox1 - ox0, yn - oy1, th), M["slab"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False control: the opening is filled with slab (no drop on any pixel)."""
        d = PARAMS["deck"]
        op = PARAMS["opening"]
        th = d["thick"]
        BOX(f"{ROOT}/Slab_Fill",
            ((op["x0"] + op["x1"]) / 2.0, (op["y0"] + op["y1"]) / 2.0,
             d["z_top"] - th / 2.0),
            (op["x1"] - op["x0"], op["y1"] - op["y0"], th), M["slab"], col=True)

    # -------------------------------------------------------------------
    # Formwork skirt under the opening - secures a dark zone right below the lip (dark constant colour 0.042)
    #   Its inner face is set **outward** from the opening by inset (0.01) so it is never coplanar with
    #   the slab opening reveal (no Z-fighting, brief §A-8).
    # -------------------------------------------------------------------
    def build_skirt(M):
        op = PARAMS["opening"]
        sk = PARAMS["skirt"]
        ins, t = sk["inset"], sk["thick"]
        z0, z1 = sk["z_bot"], sk["z_top"]
        cz, hz = (z0 + z1) / 2.0, z1 - z0
        xa, xb = op["x0"] - ins, op["x1"] + ins       # skirt inner face
        ya, yb = op["y0"] - ins, op["y1"] + ins
        # e (0.02) makes W/E and S/N overlap **strictly inward** at the corners
        # -> removes the coplanar butt faces of the 4-box frame corners.
        e = 0.02
        BOX(f"{ROOT}/Skirt_W", (xa - t / 2.0, (ya + yb) / 2.0, cz),
            (t, yb - ya + 2.0 * e, hz), M["skirt"])
        BOX(f"{ROOT}/Skirt_E", (xb + t / 2.0, (ya + yb) / 2.0, cz),
            (t, yb - ya + 2.0 * e, hz), M["skirt"])
        # S/N pull z 2 mm inward to remove top/bottom coplanarity in the corner overlaps
        BOX(f"{ROOT}/Skirt_S", ((xa + xb) / 2.0, ya - t / 2.0, cz),
            (xb - xa + 2.0 * (t + e), t, hz - 0.004), M["skirt"])
        BOX(f"{ROOT}/Skirt_N", ((xa + xb) / 2.0, yb + t / 2.0, cz),
            (xb - xa + 2.0 * (t + e), t, hz - 0.004), M["skirt"])

    # -------------------------------------------------------------------
    # Basement - floor (z -3.0) + 4 formwork walls. The slab (z -0.25) doubles as the ceiling.
    #   Wall tops at -0.20 overlap the slab underside (-0.25) by 0.05 -> no gap.
    # -------------------------------------------------------------------
    def build_lower(M):
        lw = PARAMS["lower"]
        t = lw["wall_t"]
        x0, x1, y0, y1 = lw["x0"], lw["x1"], lw["y0"], lw["y1"]
        zf, ft = lw["z_floor"], lw["floor_t"]
        # Floor plate: 0.05 larger than the wall outline -> avoids coplanarity with the outer wall faces
        BOX(f"{ROOT}/Lower_Floor",
            ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zf - ft / 2.0),
            (x1 - x0 + 2.0 * t + 0.10, y1 - y0 + 2.0 * t + 0.10, ft),
            M["lower_floor"], col=True)
        # Wall bottoms are dropped 0.10 below the floor plate top to avoid horizontal coplanarity (butt joint)
        zwb = zf - 0.10
        czw = (zwb + lw["z_ceil"]) / 2.0
        hzw = lw["z_ceil"] - zwb
        # Corners: W/E overrun in y and S/N in x by the wall thickness + 0.02 so they overlap
        # (removes the coplanar butt faces of the 4-box frame corners)
        e = 0.02
        BOX(f"{ROOT}/Lower_Wall_W", (x0 - t / 2.0, (y0 + y1) / 2.0, czw),
            (t, y1 - y0 + 2.0 * t, hzw), M["lower_wall"], col=True)
        BOX(f"{ROOT}/Lower_Wall_E", (x1 + t / 2.0, (y0 + y1) / 2.0, czw),
            (t, y1 - y0 + 2.0 * t, hzw), M["lower_wall"], col=True)
        ts = t - e                                   # S/N thickness (outer face 0.02 inward)
        # S/N also pull z 2 cm inward to remove top/bottom coplanarity in the corner overlaps
        BOX(f"{ROOT}/Lower_Wall_S", ((x0 + x1) / 2.0, y0 - ts / 2.0, czw),
            (x1 - x0 + 2.0 * ts, ts, hzw - 0.04), M["lower_wall"], col=True)
        BOX(f"{ROOT}/Lower_Wall_N", ((x0 + x1) / 2.0, y1 + ts / 2.0, czw),
            (x1 - x0 + 2.0 * ts, ts, hzw - 0.04), M["lower_wall"], col=True)

    # -------------------------------------------------------------------
    # 2 above-ground formwork walls (east, north) + south column openings (light source)
    # -------------------------------------------------------------------
    def build_upper_walls(M):
        w = PARAMS["walls"]
        t, h = w["t"], w["h"]
        xf, yf = w["x_face"], w["y_face"]
        # East wall - closes the horizon head-on along the main camera axis (+X) (brief §A-4)
        ey0, ey1 = w["e_y0"], w["e_y1"]
        BOX(f"{ROOT}/Wall_E", (xf + t / 2.0, (ey0 + ey1) / 2.0,
                               (w["base"] + h) / 2.0),
            (t, ey1 - ey0, h - w["base"]), M["wall"], col=True)
        # North wall - overlaps the east wall in x but with a different z range to remove corner coplanarity
        nx0, nx1 = w["n_x0"], w["n_x1"]
        hn, tn = h - w["n_h_delta"], w["n_t"]
        BOX(f"{ROOT}/Wall_N", ((nx0 + nx1) / 2.0, yf + tn / 2.0,
                               (w["n_base"] + hn) / 2.0),
            (nx1 - nx0, tn, hn - w["n_base"]), M["wall"], col=True)
        # South colonnade - the gaps expose outside earth and sky = a light source preventing an indoor dark zone
        co = PARAMS["colonnade"]
        s = co["size"]
        for i, cx in enumerate(co["xs"]):
            BOX(f"{ROOT}/Column_{i}", (cx, co["y_c"], (w["base"] + co["h"]) / 2.0),
                (s, s, co["h"] - w["base"]), M["wall"], col=True)

    # -------------------------------------------------------------------
    # Rebar stubs - 6 straight + 2 bent (_oriented_box) + 1 hook
    # -------------------------------------------------------------------
    def build_rebar(M):
        rb = PARAMS["rebar"]
        for i, (cx, cy) in enumerate(rb["straight"]):
            CYL(f"{ROOT}/Rebar_{i}", (cx, cy, rb["z_c"]), rb["r"], rb["h"],
                M["rebar"])
        L, t = rb["bent_len"], rb["bent_t"]
        for i, (cx, cy, tilt, yaw) in enumerate(rb["bent"]):
            # Local Z = rebar axis. rotx tilts it and rotz gives the bearing.
            # Vertical length after tilting = L*cos(tilt) -> centre z chosen so the bottom is embedded in the slab.
            zc = L * math.cos(math.radians(tilt)) / 2.0 - 0.055
            OBOX(f"{ROOT}/RebarBent_{i}", (cx, cy, zc), (t, t, L),
                 M["rebar"], rotz=yaw, rotx=tilt)
        hk = rb["hook"]
        OBOX(f"{ROOT}/RebarHook", (hk["cx"], hk["cy"], hk["z"]),
             (hk["lx"], hk["t"], hk["t"]), M["rebar"], rotz=hk["yaw"])

    # -------------------------------------------------------------------
    # Crushed concrete debris - fixed-seed random (reproducibility). No placement inside the opening
    #   (prevents fragments floating over the cavity). 60 % is concentrated in a ring around the lip to form a 'debris rim'.
    # -------------------------------------------------------------------
    def build_debris(M):
        db = PARAMS["debris"]
        op = PARAMS["opening"]
        rng = random.Random(db["seed"])
        mats = [M[f"debris{i}"] for i in range(len(mp["debris_colors"]))]
        n_mat = len(mats)
        placed = 0
        guard = 0
        while placed < db["count"] and guard < db["count"] * 20:
            guard += 1
            if rng.random() < db["perim_ratio"]:
                off = rng.uniform(db["ring_lo"], db["ring_hi"])
                side = rng.randrange(4)
                if side == 0:                      # outside the west lip
                    px = op["x0"] - off
                    py = rng.uniform(op["y0"] - 0.5, op["y1"] + 0.5)
                elif side == 1:                    # outside the east lip
                    px = op["x1"] + off
                    py = rng.uniform(op["y0"] - 0.5, op["y1"] + 0.5)
                elif side == 2:                    # outside the south lip
                    px = rng.uniform(op["x0"] - 0.5, op["x1"] + 0.5)
                    py = op["y0"] - off
                else:                              # outside the north lip
                    px = rng.uniform(op["x0"] - 0.5, op["x1"] + 0.5)
                    py = op["y1"] + off
            else:
                px = rng.uniform(db["x0"], db["x1"])
                py = rng.uniform(db["y0"], db["y1"])
            # No placement inside the opening (over the cavity) - prevents floating fragments
            if (op["x0"] - 0.02 < px < op["x1"] + 0.02
                    and op["y0"] - 0.02 < py < op["y1"] + 0.02):
                continue
            s = rng.uniform(db["s_lo"], db["s_hi"])
            mtl = mats[placed % n_mat]
            sink = db["sink"]
            if placed % 3 == 2:
                # Flattened ellipsoid: radius rz, centre z = rz*(1-2·sink) -> bottom buried
                rz = s * 0.38
                SPH(f"{ROOT}/Debris_{placed}",
                    (px, py, rz * (1.0 - 2.0 * sink)),
                    (s * 0.6, s * 0.5, rz), mtl)
            else:
                # Box: height hz, centre z = hz*(0.5-sink) -> bottom at -hz·sink (buried)
                hz = s * rng.uniform(0.4, 0.8)
                OBOX(f"{ROOT}/Debris_{placed}",
                     (px, py, hz * (0.5 - sink)),
                     (s, s * rng.uniform(0.55, 1.0), hz),
                     mtl, rotz=rng.uniform(0.0, 90.0))
            placed += 1
        return placed

    # -------------------------------------------------------------------
    # cue - warning paint / temporary railing (OFF by default: being unguarded is this scene's hazard essence)
    # -------------------------------------------------------------------
    def build_cues(M):
        op = PARAMS["opening"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            w, pr = ns["width"], ns["proud"]
            t = 0.01
            cz = pr - t / 2.0
            xa, xb, ya, yb = op["x0"], op["x1"], op["y0"], op["y1"]
            BOX(f"{ROOT}/Nosing_W", (xa - w / 2.0, (ya + yb) / 2.0, cz),
                (w, yb - ya, t), M["nosing"])
            BOX(f"{ROOT}/Nosing_E", (xb + w / 2.0, (ya + yb) / 2.0, cz),
                (w, yb - ya, t), M["nosing"])
            BOX(f"{ROOT}/Nosing_S", ((xa + xb) / 2.0, ya - w / 2.0, cz),
                (xb - xa + 2.0 * w, w, t), M["nosing"])
            BOX(f"{ROOT}/Nosing_N", ((xa + xb) / 2.0, yb + w / 2.0, cz),
                (xb - xa + 2.0 * w, w, t), M["nosing"])
        if cfg["cue_railing"]:
            rr = PARAMS["opening_rail"]
            o = rr["offset"]
            xa, xb = op["x0"] - o, op["x1"] + o
            ya, yb = op["y0"] - o, op["y1"] + o
            corners = [(xa, ya), (xb, ya), (xb, yb), (xa, yb)]
            for i, (cx, cy) in enumerate(corners):
                CYL(f"{ROOT}/OpenRail_Post_{i}",
                    (cx, cy, rr["rail_h"] / 2.0 - 0.05),
                    rr["post_r"], rr["rail_h"] + 0.10, M["rail"])
            for i in range(4):
                ax, ay = corners[i]
                bx, by = corners[(i + 1) % 4]
                mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
                length = math.hypot(bx - ax, by - ay)
                horiz = abs(by - ay) < 1e-9
                for tag, zc in (("Top", rr["rail_h"]), ("Mid", rr["mid_h"])):
                    if horiz:
                        CYL(f"{ROOT}/OpenRail_{tag}_{i}", (mx, my, zc),
                            rr["rail_r"], length, M["rail"], rotY=90.0)
                    else:
                        CYL(f"{ROOT}/OpenRail_{tag}_{i}", (mx, my, zc),
                            rr["rail_r"], length, M["rail"], rotX=90.0)

    # -------------------------------------------------------------------
    # Dressing - formwork panels · spoil piles · outside earth mounds · distant ridge
    # -------------------------------------------------------------------
    def build_dressing(M):
        dr = PARAMS["dressing"]
        pn = dr["panel"]
        tilt = pn["tilt"]
        # Tilted panel: vertical half-height = (h/2)*cos(tilt) -> the bottom sits on the slab (z=0).
        # The y centre is set inside the north wall (6.10) so either the top or the bottom must bite into the wall.
        zc = pn["h"] * math.cos(math.radians(tilt)) / 2.0 - 0.03
        for i, px in enumerate(formpanel_xs()):      # v5.1 §3 even-spacing jitter
            OBOX(f"{ROOT}/FormPanel_{i}", (px, pn["y_c"], zc),
                 (pn["w"], pn["t"], pn["h"]), M["panel"], rotx=tilt)
        for i, pl in enumerate(dr["piles"]):
            # The bottom bites only 0.06 below the slab top face (0) - embedded shallowly relative to sz so it
            # does not pierce the slab (0.25 thick) and poke through the basement ceiling.
            SPH(f"{ROOT}/Pile_{i}", (pl["cx"], pl["cy"], pl["sz"] - 0.06),
                (pl["sx"], pl["sy"], pl["sz"]), M["gravel"])
        gz = PARAMS["ground"]["z_top"]
        # Outside earth mounds - v2: split into 3 lobes and flattened (sink buries the bottom in the ground,
        #   breaking the 'smooth pebble' silhouette). Peak = gz - sink + sz.
        for i, mo in enumerate(dr["mounds"]):
            for j, (dx, dy, sx, sy, sz) in enumerate(mo["lobes"]):
                SPH(f"{ROOT}/Mound_{i}_{j}",
                    (mo["cx"] + dx, mo["cy"] + dy, gz - mo["sink"]),
                    (sx, sy, sz), M["dirt"])
        rg = dr["ridge"]
        BOX(f"{ROOT}/Ridge_S", (0.0, rg["cy"], gz + rg["h"] / 2.0 - 0.5),
            (2.0 * rg["half_x"], rg["t"], rg["h"]), M["dirt"])

    # -------------------------------------------------------------------
    # Context dressing v2 - material piles (rebar bundle, cement bags) · movable safety fences ·
    #                  cable reel / tool boxes · column slogan panels · distant tower crane
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2] ground_kit - P15 slab_construction. Respects both the opening (GT-V) and the west lip
    #   (GT-E1′). Adjudication is done by B8 (zero opening intersection) and B6 (edge standoff).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["skirt"], crack=M["skirt"],
                  marking=M["nosing"],           # yellow opening marking paint
                  stain_efflorescence=M["panel"], stain_dirt=M["dirt"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneD2 P15 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_site_dressing(M):
        """Frame-stage construction-site context elements. **Opening, rebar stubs, debris and slab split unchanged.**

        ── Camera checks (all views, basis of the coordinate calculations) ─────────────────────────────
        grid_views(gy=0) hfov 60 deg (half tan 0.577) · pitch −10 deg · 16:9 -> vfov 36 deg.
        [opening sight wedge] the sight lines from camera (−d,0) to the opening (x 0..2, |y| <= 0.75) satisfy
          |y| <= 0.75·(px+d)/(d+1) at x=px  (d=10 is the widest).
          Nearest new solid = tool box (−4.85, 1.70) -> wedge limit 0.39 ->
          **clearance 1.31 m**. All the rest are 3 m or more. -> zero occlusion of the opening.
        [4 mise-en-scene cuts]
          approach(−4,0,0.9->1.2,0,−0.35): every new solid is either behind the camera or
            51 deg+ off the view axis (hfov half 30 deg) -> out of frame.
          brink(−1,0,1.6->1.6,0.15,−2.3): a downward cut directly over the opening. Nothing new within 3 m.
          graze(−6,−0.25,0.35->2.5,0.05,0.02): reel 77 deg · tools 59 deg · bag pallet 56 deg
            -> all out of frame. **The low-eye concealment framing is unchanged.**
          beauty_overview(−5.2,−5,3.4->1.2,0.4,−0.9): bag pallet A enters at 26 deg off the view axis
            (lower left of frame), but the sight line toward the opening's near lip is at z=2.40 m there,
            far above the pallet's total height 0.55 m -> **zero occlusion** (it acts as a foreground prop only).
        [distant tower crane - grazing the south end of the east wall]
          Crane at (100, −40), mast top 14.2 / apex 15.4.
          · Sight angle: bearing 21.8 deg from eye(−10,0) < hfov half 30 deg -> in frame.
          · East wall (x 8.15, y −6.05..6.45, h 3.2) clearance check: the mast bearing line reaches
            y = −40·18.15/110 = −6.60 < −6.05 at x=8.15 -> **passes outside the wall's south end**
            (clearance 0.55 m).
          · Colonnade columns (x 2.5·5.5, y −6.425..−5.975) check:
            y=−4.55 at x=2.5, y=−5.64 at x=5.5 -> both north of the columns -> no occlusion.
          · Elevation check: apex 15.4 m at ~110 m -> elevation 7.5 deg < frame top limit
            (pitch −10 + vfov half 18 = +8.0 deg) -> **in frame all the way to the apex**.
          · **Visible view = grid h*_d10 (the widest cut)**. In d5/d2 and graze it is hidden behind the
            east wall (elevation 9.9 deg/12.7 deg) - an intended outcome (close cuts should have the
            opening as their subject, so a distant prop is better kept out).
        [distant ground pad] closes the void beyond the existing ground half 60 m (the crane is at 100 m).
          Its top face −0.06 is below the existing ground −0.05, so the overlap is coplanar-free.
        """
        st = PARAMS["site"]
        cnt = dict(rebar=0, bag=0, fence=0, tool=0, placard=0, crane=0)

        # ── (0) distant ground pad ──
        fp = st["farpad"]
        BOX(f"{ROOT}/FarPad",
            ((fp["x0"] + fp["x1"]) / 2.0, (fp["y0"] + fp["y1"]) / 2.0,
             fp["z_top"] - fp["thick"] / 2.0),
            (fp["x1"] - fp["x0"], fp["y1"] - fp["y0"], fp["thick"]), M["dirt"])

        # ── (1) rebar bundle (laid down) - 2 bearers + rows x per_row bars + 2 binding bands ──
        bu = st["bundle"]
        for rb in st["rebar_bundles"]:
            tag, cx, cy, yaw, L = rb["tag"], rb["cx"], rb["cy"], rb["yaw"], rb["L"]
            a = math.radians(yaw)
            ca, sa = math.cos(a), math.sin(a)

            def put(dx, dy, _cx=cx, _cy=cy, _ca=ca, _sa=sa):
                return (_cx + dx * _ca - dy * _sa, _cy + dx * _sa + dy * _ca)

            for k, dx in enumerate((-L / 2.0 + 0.55, L / 2.0 - 0.55)):
                bx, by = put(dx, 0.0)
                OBOX(f"{ROOT}/Batten_{tag}_{k}",
                     (bx, by, bu["batten_h"] / 2.0 - 0.01),
                     (bu["batten_w"], bu["batten_d"], bu["batten_h"]),
                     M["panel"], rotz=yaw)
            r = bu["r"]
            for row in range(int(rb["rows"])):
                zc = bu["batten_h"] + r + row * (1.85 * r)
                off = (row % 2) * r          # half-pitch offset per layer (stacking stability)
                for j in range(int(rb["per_row"])):
                    dy = (j - (rb["per_row"] - 1) / 2.0) * (2.2 * r) + off
                    px, py = put(0.0, dy)
                    # add_cylinder cannot take rotz, so bars that need a bearing are made
                    # with _oriented_box (at D20 gauge the round/square section difference is invisible).
                    OBOX(f"{ROOT}/RebarBar_{tag}_{row}_{j}", (px, py, zc),
                         (L, 2.0 * r, 2.0 * r), M["rebar"], rotz=yaw)
                    cnt["rebar"] += 1
            # 2 binding bands (thin straps wrapping the bar bundle)
            hz = bu["batten_h"] + 2.0 * r * int(rb["rows"]) + 0.02
            wy = rb["per_row"] * 2.2 * r + 0.05
            for k, dx in enumerate((-L / 4.0, L / 4.0)):
                bx, by = put(dx, 0.0)
                OBOX(f"{ROOT}/Strap_{tag}_{k}", (bx, by, hz / 2.0),
                     (bu["strap_t"], wy, hz), M["rail"], rotz=yaw)

        # ── (2) cement bag pallets ──
        bp = st["bagpallet"]
        brng = random.Random(bp["seed"])
        for pd_ in st["bagpallets"]:
            tag, cx, cy, yaw = pd_["tag"], pd_["cx"], pd_["cy"], pd_["yaw"]
            a = math.radians(yaw)
            ca, sa = math.cos(a), math.sin(a)

            def put2(dx, dy, _cx=cx, _cy=cy, _ca=ca, _sa=sa):
                return (_cx + dx * _ca - dy * _sa, _cy + dx * _sa + dy * _ca)

            OBOX(f"{ROOT}/BagPallet_{tag}", (cx, cy, bp["pt"] / 2.0 - 0.01),
                 (bp["pw"], bp["pd"], bp["pt"]), M["panel"], rotz=yaw)
            for lay in range(int(pd_["layers"])):
                for q in range(4):
                    dx = (0.5 - (q % 2)) * (bp["bw"] * 0.52)
                    dy = (0.5 - (q // 2)) * (bp["bd"] * 1.02)
                    if lay % 2:                      # alternating stack
                        dx, dy = dy * 0.9, dx * 1.1
                    px, py = put2(dx, dy)
                    OBOX(f"{ROOT}/Bag_{tag}_{lay}_{q}",
                         (px, py, bp["pt"] + bp["bh"] * (lay + 0.5)),
                         (bp["bw"], bp["bd"], bp["bh"]), M["bag"],
                         rotz=yaw + (90.0 if lay % 2 else 0.0)
                         + brng.uniform(-4.0, 4.0))
                    cnt["bag"] += 1

        # ── (3) movable safety fences (single north row - 3.85 m or more from the opening) ──
        fc = st["fence"]
        for i, cx, cy, fyaw in fence_placements():   # v5.1 §3 position/yaw jitter
            w, h = fc["w"], fc["h"]
            grp = sc.build_rot_group(stage, f"{ROOT}/Fence_{i}", (cx, cy),
                                     fyaw)
            for s, sx in enumerate((-w / 2.0, w / 2.0)):
                CYL(f"{grp}/P{s}", (cx + sx, cy, h / 2.0 - 0.01),
                    fc["post_r"], h, M["fence"])
                BOX(f"{grp}/F{s}",
                    (cx + sx, cy, fc["foot_h"] / 2.0 - 0.012),
                    (fc["foot_w"], fc["foot_d"], fc["foot_h"]), M["fence"])
            z_lo, z_hi = 0.22, h - 0.06
            for s, zc in enumerate((z_lo, z_hi)):
                CYL(f"{grp}/R{s}", (cx, cy, zc), fc["rail_r"], w,
                    M["fence"], rotY=90.0)
            nb = int(fc["n_bar"])
            for j in range(nb):
                bx = cx - w / 2.0 + w * (j + 1) / (nb + 1)
                CYL(f"{grp}/B{j}", (bx, cy, (z_lo + z_hi) / 2.0),
                    fc["bar_r"], z_hi - z_lo, M["fence"])
            cnt["fence"] += 1

        # ── (4) cable reel · tool boxes ──
        rl = st["reel"]
        for s, sy in enumerate((-1.0, 1.0)):
            CYL(f"{ROOT}/Reel_F{s}",
                (rl["cx"], rl["cy"] + sy * (rl["coil_w"] + rl["flange_t"]) / 2.0,
                 rl["flange_r"]),
                rl["flange_r"], rl["flange_t"], M["panel"], rotX=90.0)
        CYL(f"{ROOT}/Reel_Coil", (rl["cx"], rl["cy"], rl["flange_r"]),
            rl["coil_r"], rl["coil_w"] + 0.01, M["cable"], rotX=90.0)
        for i, tb in enumerate(st["toolboxes"]):
            OBOX(f"{ROOT}/ToolBox_{i}",
                 (tb["cx"], tb["cy"], tb["h"] / 2.0 - 0.01),
                 (tb["w"], tb["d"], tb["h"]), M["tool"], rotz=tb["yaw"])
            cnt["tool"] += 1

        # ── (5) column safety-slogan panels (textless colour fields) ──
        co = PARAMS["colonnade"]
        pc = st["placard"]
        y_face = co["y_c"] + co["size"] / 2.0        # column north face (camera side)
        for i, pl in enumerate(st["placards"]):
            cxp = co["xs"][int(pl["col"])]
            BOX(f"{ROOT}/Placard_{i}", (cxp, y_face + 0.010, pl["z"]),
                (pc["w"], pc["t"], pc["h"]), M["placard"])
            BOX(f"{ROOT}/Placard_{i}_B", (cxp, y_face + 0.035,
                                          pl["z"] + pc["h"] / 2.0
                                          - pc["band_h"] / 2.0),
                (pc["w"], 0.030, pc["band_h"]), M["placard_band"])
            cnt["placard"] += 1

        # ── (6) distant tower crane (assembly of thin boxes) ──
        cr = st["crane"]
        cx, cy = cr["cx"], cr["cy"]
        BOX(f"{ROOT}/Crane_Mast",
            (cx, cy, (cr["base_z"] + cr["mast_top"]) / 2.0),
            (cr["mast_w"], cr["mast_w"], cr["mast_top"] - cr["base_z"]),
            M["crane"])
        BOX(f"{ROOT}/Crane_Apex",
            (cx, cy, (cr["mast_top"] - 0.40 + cr["apex_top"]) / 2.0),
            (cr["apex_w"], cr["apex_w"],
             cr["apex_top"] - cr["mast_top"] + 0.40), M["crane"])
        jl = cr["jib_len"] + 0.6
        BOX(f"{ROOT}/Crane_Jib",
            (cx, cy + 0.30 - jl / 2.0, cr["jib_z0"] + cr["jib_h"] / 2.0),
            (cr["jib_w"], jl, cr["jib_h"]), M["crane"])
        cl = cr["cjib_len"] + 0.6
        BOX(f"{ROOT}/Crane_CJib",
            (cx, cy - 0.30 + cl / 2.0, cr["cjib_z0"] + cr["cjib_h"] / 2.0),
            (cr["cjib_w"], cl, cr["cjib_h"]), M["crane"])
        BOX(f"{ROOT}/Crane_CW",
            (cx, cy + cr["cjib_len"] - 1.40,
             cr["cjib_z0"] + 0.90 - cr["cw_h"] / 2.0),
            (cr["cw_w"], cr["cw_d"], cr["cw_h"]), M["crane"])
        hz0 = cr["hook_z0"]
        BOX(f"{ROOT}/Crane_Hook",
            (cx, cy + cr["hook_dy"], hz0 + cr["hook_h"] / 2.0),
            (cr["hook_w"], cr["hook_w"], cr["hook_h"]), M["crane"])
        BOX(f"{ROOT}/Crane_Rope",
            (cx, cy + cr["hook_dy"],
             (hz0 + cr["hook_h"] - 0.05 + cr["jib_z0"] + 0.05) / 2.0),
            (cr["rope_w"], cr["rope_w"],
             cr["jib_z0"] + 0.05 - (hz0 + cr["hook_h"] - 0.05)), M["crane"])
        cnt["crane"] = 7
        return cnt

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if not cfg["cue_material_break"]:
        # Contrast-removed control: the basement gets the same material as the slab
        M["lower_wall"] = M["slab"]
        M["lower_floor"] = M["slab"]

    build_ground(M)
    build_upper_walls(M)
    if cfg["hazard_stairs"]:
        build_slab(M)
        build_skirt(M)
        build_lower(M)
        build_rebar(M)
        n_debris = build_debris(M)
        build_cues(M)
    else:
        build_slab(M)
        build_flat_fill(M)
        n_debris = build_debris(M)
    site_cnt = None
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        site_cnt = build_site_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements - after the dressing (scatter convention)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # Geometry self-check printout (numbers confirmed before rendering - for supervisor re-checking)
    op, lw = PARAMS["opening"], PARAMS["lower"]
    drop = PARAMS["deck"]["z_top"] - lw["z_floor"]
    beam = drop / math.tan(math.radians(PARAMS["light"]["noon_sun_elev"]))
    print(f"[기하] 개구 {op['x1'] - op['x0']:.2f}(진행축) × "
          f"{op['y1'] - op['y0']:.2f}(폭) m · 낙차 {drop:.2f} m · "
          f"부스러기 {n_debris}개")
    print(f"[조명] 개구 통과광 수평 이동 {beam:.2f} m → 지하 바닥 착지 "
          f"x {op['x0'] + beam:.2f}..{op['x1'] + beam:.2f} "
          f"(지하 동벽 x={lw['x1']:.1f} 까지 여유 "
          f"{lw['x1'] - (op['x1'] + beam):.2f} m)")

    if site_cnt is not None:
        # Context dressing self-check - opening sight wedge clearance · crane sight-line clearance
        st = PARAMS["site"]
        props = ([(f"철근{b['tag']}", b["cx"], b["cy"]) for b in st["rebar_bundles"]]
                 + [(f"포대{b['tag']}", b["cx"], b["cy"])
                    for b in st["bagpallets"]]
                 + [(f"펜스{i}", fx, fy)
                    for i, fx, fy, _fy in fence_placements()]
                 + [("릴", st["reel"]["cx"], st["reel"]["cy"])]
                 + [(f"공구{i}", t["cx"], t["cy"])
                    for i, t in enumerate(st["toolboxes"])])
        worst = None
        for nm, px, py in props:
            wedge = 0.75 * max(px + 10.0, 0.0) / 10.0     # d10 camera maximum width
            margin = abs(py) - wedge
            if worst is None or margin < worst[1]:
                worst = (nm, margin)
        cr = st["crane"]
        w = PARAMS["walls"]
        y_at_wall = cr["cy"] * (w["x_face"] + w["t"] / 2.0 - (-10.0)) \
            / (cr["cx"] + 10.0)
        elev = math.degrees(math.atan2(cr["apex_top"] - 0.9, cr["cx"] + 10.0))
        print(f"[드레싱] 철근봉 {site_cnt['rebar']} · 포대 {site_cnt['bag']} · "
              f"펜스 {site_cnt['fence']}매 · 공구 {site_cnt['tool']} · "
              f"표어 {site_cnt['placard']} · 크레인 {site_cnt['crane']}프림 "
              f"+ 원경 패드")
        print(f"[검산] 개구 시선 웨지 최소 여유 = {worst[0]} {worst[1]:.2f} m "
              f"(>0 이면 개구 가림 0)")
        print(f"[검산] 크레인 방위선이 동벽면(x={w['x_face']:.2f})을 지나는 y = "
              f"{y_at_wall:.2f} (동벽 남단 {w['e_y0']:.2f} 밖이어야 가시) · "
              f"정점 앙각 {elev:.1f}° (프레임 상한 8.0°)")

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneD2 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["beauty_overview"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD2_{ts}.png")
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
