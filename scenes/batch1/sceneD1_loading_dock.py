# -*- coding: utf-8 -*-
"""
sceneD1_loading_dock.py — NegObs synthetic scene 33: loading dock U-shaped platform edge (Isaac Sim 4.5)

Type    : D1 non-stair drop - logistics loading platform dock edge (drop 1.2 m)
Spec    : Docs/nanobanana_batch1_geometry_map.md §D sceneD1_loading_dock
Look ref: look_refs/d1_loading_dock.jpg (v3, on-platform viewpoint - main composition)
          look_refs/d1_loading_dock_v2_overview.jpg (exterior high angle - dimension reference)
Shared  : scene_common.py (verified API helpers) · scene16_canopy_shadow.py (standard template)

Hazard  : Walking on the platform, a **yellow·black diagonal warning paint band crosses the
          view**, and the truck apron floor beyond it (z −1.2) is completely hidden at grazing
          angles. The paint band induces the misreading "the floor continues" rather than "it
          ends here" - a case where the drop's only visual cue is **flat paint**. The U-shaped
          recessed bay (width 6 x depth 4) bends the edge line through 90 deg twice, breaking
          the straight-edge assumption (a single vanishing line).
Goal    : Assemble the platform slab (U-shaped bay cut - split into 3 boxes) + apron + the
          bay's 3 wall faces + warning paint band + dock bumpers + shutter door wall·bollards,
          and judge it by render (render only).

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD1_loading_dock.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneD1_loading_dock.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneD1_loading_dock.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0 (the platform's main dock edge).
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
# [A] SCENE_CONFIG - standard 7 keys
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> bay·dock edge filled in for a z=0 flat (control)
    "cue_railing":        False,  # Safety railing around the bay - default OFF (unguarded is the reality)
    "cue_tactile":        False,  # not applicable (industrial loading dock) - key reserved only
    "cue_material_break": True,   # False -> the apron is concrete too (removes the material contrast)
    "cue_nosing":         True,   # * yellow·black 45 deg warning paint band - the core cue of this scene
    "cue_sign":           False,  # [optional] not implemented - key reserved only
    "cue_scene_dressing": True,   # shutter door wall·warehouse wall·bollards·end parapets
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # Platform deck (top slab). Top face z=0, thickness 0.20. Main dock edge = x 0 (drop start edge).
    deck=dict(x_w=-16.0, x_e=0.0, y_s=-14.0, y_n=14.0, z_top=0.0, thick=0.20),

    # * U-shaped recessed bay: width 6.0(y) x depth 4.0(x). Opens toward +X so a truck backs in.
    #   The edge line is the U of (0,−14)->(0,−3)->(−4,−3)->(−4,+3)->(0,+3)->(0,+14).
    bay=dict(x0=-4.0, x1=0.0, y0=-3.0, y1=3.0),

    # Platform mass (dock-edge wall). Set back from the deck by setback so the deck lip
    # projects 3 cm -> (1) removes the vertical coplanar face (Z-fighting) (2) makes a shadow line under the lip.
    mass=dict(z_bot=-1.35, z_top=-0.19, setback=0.03),

    # Truck apron (lower yard). Top face z −1.2 -> drop 1.2 m [GT].
    apron=dict(z_top=-1.2, thick=0.6, half=40.0),

    # Warning paint band (width 0.35). Continuous black base strip + alternating yellow 45 deg plates.
    #   The AABB of a 45 deg rotated rectangle is ((L+w)/√2)² -> setting L = W·√2 − w makes it
    #   exactly inscribed in the band width W -> **zero floating geometry sticking out over the void**.
    #   lip_inset: the black base strip is pulled back 3 mm **on the drop-side edge only**, removing the
    #   coplanar face (Z-fighting) with the deck's vertical cut. The yellow plates sit on a 45 deg face,
    #   so leaving them as plain rectangles is safe - they are not parallel to the deck face.
    band=dict(width=0.35, pitch=0.38, stripe_w=0.15,
              base_proud=0.0015, base_t=0.010, lip_inset=0.003,
              stripe_proud=0.0035, stripe_t=0.006,
              seed=3301, drop_ratio=0.10, y_end=13.7),

    # Dock bumpers (black rubber). Fixed to the top of the wall face, spacing 1.2 m.
    bumper=dict(w=0.30, proud=0.15, h=0.60, z_top=-0.30, spacing=1.2),

    # ── 2 bollards (bay corner protection, yellow) [v5.1 §2 · ctx2] ───────
    #   Position kept: the bay corner is a real collision-risk point where trucks back in, so it
    #   matches the "only at vehicle-entry risk points" convention exactly (director's verdict).
    #   Dimensions are already within spec (φ0.18 ∈ 0.10~0.20 · h0.95 ∈ 0.80~1.00) -> kept.
    #   Added: **white reflective band on top** (night visibility on a loading dock - also matches industrial practice).
    #   * Dot tactile paving **not installed**: the Mobility Impaired Act Table 2 governs sidewalks
    #     (pedestrian ways) and this is a vehicle loading yard. Besides, the yellow tiles clash in
    #     colour·position with the deck's **warning paint band** (yellow-black 45 deg) and pollute the judgment element -> tactile=False.
    #   * The body stays yellow (v5.1 §2 "function·practice based" - the standard colour of an industrial bollard).
    bollards=[dict(cx=-0.75, cy=-3.9), dict(cx=-0.75, cy=3.9)],
    bollard=dict(radius=0.09, height=0.95, base_z=-0.04, tactile=False),

    # Platform end parapets (+-Y) - removing the unguarded drop away from the dock edge confines the GT to the bay·main edge
    parapet=dict(t=0.30, h=0.90, base_z=-0.05, outer_inset=0.02),

    # ═══ [W2 ground_kit] P14 yard_industrial - spec §5.8 row D1 ════════════
    #  This scene has **two surfaces**, so the plan is split in two as well (one plan = one z).
    #   (1) Deck (z=0) - **this is where the h0.3 preset's near window is** (gy=−4.0 corridor).
    #      joint grid 6.0x4.5 · forklift tyre marks · hydraulic oil stains · dirt ingress ·
    #      2 repair patches (d2·d5 windows).
    #   (2) Yard (apron z=−1.2) - "linear trench in front of the dock (6.0 m from the lip)" ·
    #      2 backing guide solid lines · 1 stop line · yard joint grid.
    #      At h0.3 it hides beyond the warning band, but it is the stage for the h0.9/h1.8 and
    #      mise-en-scene shots (this scene's first judgment point is "the apron hides beyond the band").
    #  * Tactile paving **not installed**: the Mobility Impaired Act Table 2 governs pedestrian ways
    #    and this is a vehicle loading yard (p ~ 0, §12.4 "out of scope"). Besides, the yellow tiles
    #    clash in colour·position with the deck's yellow-black warning band and pollute the judgment element.
    #    `TACTILE_OFF_REASON["sceneD1"]` records the same reason in the code.
    #  * The yellow-black warning band is **left as is** - ground_kit does not touch it.
    gkit=dict(
        #  Deck south side (camera corridor gy=−4.0). Taken so as to **avoid** the U-shaped bay
        #  (y −3…3), which satisfies GT-V (no element over an opening) structurally.
        deck_region=(-12.0, -13.0, 0.0, -3.0),
        deck_patches=[(-1.10, -4.00), (-3.80, -4.20)],
        #  Yard - the apron including the bay mouth. +X from the lip (x=0).
        yard_region=(0.5, -13.0, 16.0, 13.0),
        yard_trench_x=6.0,              # "6.0 m from the lip" [F]
        #  2 backing guide solid lines (bracketing the 6.0 bay width from both sides) + 1 stop line.
        yard_lines=[(2.0, -2.50, 0.0), (2.0, 2.50, 0.0), (10.0, 0.0, 90.0)],
    ),

    # Background: shutter door wall (+X horizon closure) + warehouse wall (-X, behind the platform)
    shutter=dict(x0=22.0, t=1.4, y_half=30.0, z_top=7.0,
                 door_w=3.6, door_h=4.2, door_embed=0.03, door_proud=0.10,
                 door_ys=[-12.0, -4.0, 4.0, 12.0],
                 rib_w=0.05, rib_proud=0.02, rib_step=0.30),
    #   x1 −15.6: pulled 0.4 inside the deck's west end (−16) so the wall front is not coplanar
    #   with the west faces of the deck/mass (a 3-face butt -> Z-fighting).
    warehouse=dict(x1=-15.6, t=1.4, y_half=20.0, z_top=6.0),

    # ─── Context dressing v2 (2026-07-27, curing the emptiness) ────────────
    #   Purpose: make "this is a logistics warehouse loading dock" readable at a glance. Every element
    #   belongs to cue_scene_dressing. The drop geometry (deck·bay·apron)·warning paint·bumpers are **wholly unchanged**.
    #   * Placement principle (for the camera check see the build_yard_dressing docstring):
    #     (1) No solid whatsoever is placed on the deck's **edge approach path (x −10..0 x y −5..−3)**
    #        (paint is flush, so it is allowed - it actually helps read the walkway).
    #     (2) The only solids that enter the view of the 3 judgment shots (edge_graze / edge_walk /
    #        bay_corner) are **beyond the edge line (x>0, apron)** or **north of the bay (y>6.5)**.
    #     (3) The far field (containers·warehouse blocks·light masts) is all x>6 -> it cannot block
    #        any sight line on the deck (being outside the apron hiding limit x=8.2 it stays visible in grazing).
    yard=dict(
        # 3 timber pallet stacks. cx,cy=stack centre, yaw=bearing (deg)
        stacks=[dict(tag="N1", cx=-2.55, cy=7.80, yaw=7.0, n_pallet=3, n_box=3),
                dict(tag="N2", cx=-5.60, cy=10.20, yaw=-14.0,
                     n_pallet=2, n_box=2),
                # S1: a **low stack** (total height 0.48) that only clips the lower right of grid d10
                dict(tag="S1", cx=-3.60, cy=-7.40, yaw=21.0,
                     n_pallet=1, n_box=1)],
        pallet=dict(w=1.20, d=1.00, h=0.145, top_t=0.030, bot_t=0.022,
                    string_w=0.10, string_h=0.090),
        carton=dict(w=0.54, d=0.44, h=0.34, seed=5107),
        # Forklift traffic paint (worn yellow) - 2 pairs of longitudinal aisles + 1 pair of cross aisles.
        #   Wear is staged with dash/gap + seeded dropout. All flush (proud <= 0.0019).
        lane=dict(w=0.11, t=0.010, proud_main=0.0012, proud_cross=0.0019,
                  dash=1.30, gap=0.55, seed=4407, drop=0.13,
                  main_ys=(-4.60, -7.10), north_ys=(4.30, 6.50),
                  x0=-15.0, x1=-0.90,
                  cross_xs=(-11.0, -13.2), cy0=-7.10, cy1=6.50),
        # Dock number sign plate (beside the shutter door, textless colour field)
        docksign=dict(w=0.70, h=0.90, z_c=2.85, off=0.62, t=0.05,
                      fw=0.40, fh=0.46),
        # Wall-mounted exterior lamp box (daytime, so no emission - shape·shadow only)
        lamp=dict(w=0.34, d=0.30, h=0.24, lens_t=0.035,
                  shutter_ys=(-9.0, 0.0, 9.0), shutter_z=5.30,
                  wh_ys=(-7.0, 5.0), wh_z=4.40),
        # Containers on the apron (far-field silhouette - outside the hiding limit x=8.2)
        container=dict(L=12.19, W=2.44, H=2.59, gap=0.06),
        #   * Every container's **near end (min x) >= 8.91** - outside the edge_graze apron hiding
        #     limit of 8.23 m (note C2 below has its long axis along x, so its near end is cx−L/2)
        containers=[dict(cx=12.60, cy=-16.0, yaw=90.0, tier=1, tone=0),
                    dict(cx=16.00, cy=13.5, yaw=90.0, tier=2, tone=1),
                    dict(cx=15.00, cy=-30.0, yaw=0.0, tier=1, tone=2)],
        # Yard light masts (silhouettes rising above the shutter wall z_top 7.0)
        masts=[dict(cx=7.40, cy=-21.0), dict(cx=8.20, cy=18.0)],
        mast=dict(r=0.10, h=8.0, head_w=0.90, head_d=0.45, head_h=0.20),
        # 2 distant warehouse blocks - silhouettes showing only their tops over the shutter wall (z 7.0)
        sheds=[dict(x0=25.0, x1=38.0, y0=-33.0, y1=-8.0, z_top=10.6, tone=0),
               dict(x0=26.5, x1=39.5, y0=6.0, y1=31.0, z_top=9.4, tone=1)],
        shed=dict(z_bot=-1.60, band_h=0.50, band_proud=0.12,
                  vent_w=0.90, vent_h=0.70, vent_n=3),
    ),

    # Railing around the bay (only when cue_railing=True)
    bay_rail=dict(rail_h=1.05, post_r=0.030, rail_r=0.025, mid_h=0.52,
                  offset=0.35, spacing=1.5),

    material=dict(
        scale=dict(concrete_floor=1.4, concrete_wall=2.2, wood_dark=0.55),
        deck_tint=(0.86, 0.85, 0.83),        # broom-finished concrete (light grey)
        wall_tint=(0.80, 0.79, 0.77),        # dock-edge wall (slightly darker)
        # Constant asphalt colour - same convention as scene11/17
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.90,
        # Warning paint: black sits in the sRGB dark band 0.02~0.06 [lesson 1]
        band_black=(0.045, 0.045, 0.047), band_black_rough=0.88,
        #   3 yellow grades (new->mid->worn) - wear is staged by lowering saturation·brightness
        band_yellow=[(0.85, 0.72, 0.10), (0.70, 0.60, 0.14),
                     (0.52, 0.46, 0.20)],
        band_yellow_w=[0.45, 0.35, 0.20],
        band_yellow_rough=[0.75, 0.85, 0.92],
        # black rubber bumper
        rubber_color=(0.035, 0.035, 0.037), rubber_rough=0.90,
        bollard_color=(0.72, 0.60, 0.08), bollard_metallic=0.1,
        bollard_rough=0.65,
        # Top reflective band (white, 0.11 m² each - small area, so the v5.1 §4 large-area ban does not apply)
        bollard_band_color=(0.88, 0.88, 0.86),
        shutter_color=(0.44, 0.45, 0.47), shutter_metallic=0.30,
        shutter_rough=0.48,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # ── Context dressing v2 ── (props keep the mid-tone 0.18~0.35 convention - lesson (2)
        #    "grey debris at 0.55 is perceived as white". The dark band 0.02~0.09 is for openings·rubber only.)
        pallet_tint=(1.00, 0.94, 0.86),          # wood_dark(~0.18) x -> timber pallet
        pallet_rough=0.90,
        carton_colors=[(0.32, 0.25, 0.16), (0.27, 0.21, 0.14),
                       (0.35, 0.29, 0.20)],
        carton_rough=0.93,
        sign_face=(0.72, 0.72, 0.69), sign_field=(0.055, 0.055, 0.060),
        sign_rough=0.60,
        lamp_body=(0.20, 0.21, 0.22), lamp_metallic=0.40, lamp_rough=0.50,
        lamp_lens=(0.56, 0.56, 0.53), lamp_lens_rough=0.22,
        container_colors=[(0.34, 0.15, 0.11), (0.13, 0.26, 0.32),
                          (0.30, 0.31, 0.29)],
        container_metallic=0.35, container_rough=0.62,
        container_door_mul=0.82,                 # door end = body x 0.82 (shading difference)
        shed_colors=[(0.42, 0.43, 0.45), (0.38, 0.40, 0.42)],
        shed_band=(0.52, 0.53, 0.54),
        shed_metallic=0.25, shed_rough=0.55,
        galv_color=(0.46, 0.47, 0.48), galv_metallic=0.55, galv_rough=0.45,
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
    # ─── Rationale for SUN_AZ_OFFSET (redefined per scene - brief v3 §A-7) ───
    #   Sun mapping world az ~ 33.5 + offset = 205  ->  shadow az = az−180 = 25 deg
    #   (the default 171.5 is adopted as is, but the rationale below confirms it is optimal here)
    #   (1) The sun is behind the camera (-X side) -> the platform deck is frontlit and the **yellow·black
    #      contrast of the warning paint band reads at its maximum** (the band is this scene's only cue).
    #   (2) Shadows lean 25 deg toward +X. The main dock edge (x=0, height 1.2 m) casts a
    #      **dark band** 1.2/tan(49.79 deg) = 1.02 m wide onto the apron,
    #      darkening the near apron beyond the band -> the hiding effect is reinforced.
    #   (3) Inside the bay: the back wall (x=−4) throws a +X component (0.92 m) and the south wall (y=−3)
    #      a +Y component (0.43 m), so **the lower part of the bay floor darkens in an L shape** -
    #      the bearing at which the recess reads as 'a deeper hole'.
    #   The [ ] keys (dome_rotation_step 15 deg) allow a further GUI sweep.
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
# [C] Path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD1")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "wood_dark", "hdri", "mdl"]

# grid_views baseline: the y at which the camera stands on the deck clear of the bay (y +-3). At −4.0
#   · the camera is always over Deck_S (y −14..−3) -> nothing is placed in mid-air
#   · even at d2 the bay corner (0,−3) is 26.6 deg off the view axis -> inside the hfov 60 deg frame
GRID_GY = -4.0


def ground_plans():
    """[W2 ground_kit] 2 ground plans - the scene assembly and the CPU check use the same function.

    (1) `deck`  : platform top slab z=0 (h0.3 near window)
    (2) `yard`  : truck apron z=−1.2 (trench·backing guide lines·stop line)
    """
    g = PARAMS["gkit"]
    d, by, ap = PARAMS["deck"], PARAMS["bay"], PARAMS["apron"]
    void_bay = (float(by["x0"]), float(by["y0"]),
                float(by["x1"]), float(by["y1"]))
    deck = gk.plan_ground(
        "yard_industrial", region=tuple(g["deck_region"]),
        z=float(d["z_top"]), gy=GRID_GY, origin=(0.0, 0.0, 0.0),
        edges=[("dock_lip", float(by["x1"]))],
        voids=(void_bay,),
        dists=(2, 5, 10), scene="sceneD1",
        tactile=(),                     # §12.4 - out of scope (industrial yard)
        sites=dict(patch=[tuple(p) for p in g["deck_patches"]]),
        #  No trench or paint is put on the deck (the yard plan handles those). Instead 2 repair
        #  patches secure surface elements for the near window.
        overrides=dict(infra=dict(trench=0, marking=()),
                       surface=(("patch", 2),
                                ("stain", ("tire", "oil", "dirt")))),
        seed=331)
    yard = gk.plan_ground(
        "yard_industrial", region=tuple(g["yard_region"]),
        z=float(ap["z_top"]), gy=GRID_GY, origin=(0.0, 0.0, 0.0),
        edges=(),                       # no drop in front of the apron
        dists=(2, 5, 10), scene="sceneD1",
        tactile=(),
        sites=dict(trench=[(float(g["yard_trench_x"]),
                            float(g["yard_region"][1]),
                            float(g["yard_region"][3]))],
                   marking=[tuple(m) for m in g["yard_lines"]]),
        overrides=dict(infra=dict(trench=1,
                                  marking=("line", "line", "line"))),
        seed=332)
    return [("deck", deck), ("yard", yard)]


def build_views():
    """Camera presets: grid_views(gy=−4.0, **orthogonal approach to the edge**) + 4 mise-en-scene shots.

    Spec §D cameras: h0.9 walk along the platform + orthogonal approach + bay corner mise-en-scene.
    Judgment point = in edge_graze the apron floor is completely hidden beyond the warning band.
    """
    views = sc.grid_views(GRID_GY)
    # edge_approach: a pedestrian approaching the dock edge head-on (h0.9) - the band crosses the view
    views["edge_approach"] = dict(eye=[-4.0, -4.0, 0.9],
                                  tgt=[1.0, -3.4, -0.40])
    # edge_walk: walking parallel to the edge - the band converges on the vanishing point, the U-bend shows
    views["edge_walk"] = dict(eye=[-1.25, -9.0, 0.9], tgt=[-0.75, 0.5, 0.30])
    # edge_graze: low-eye grazing - the apron hides beyond the band (reproduces the v3 reference)
    #   eye z 0.35 · 2.4 m to the edge -> hiding limit x = 1.2·2.4/0.35 = 8.2 m
    views["edge_graze"] = dict(eye=[-2.4, -5.2, 0.35], tgt=[1.6, -3.0, 0.05])
    # bay_corner: bay corner mise-en-scene - the 90 deg bend in the paint + bumper row + recess depth
    views["bay_corner"] = dict(eye=[-1.10, -5.0, 1.55], tgt=[-2.8, -0.6, -0.85])
    # beauty_overview: oblique high angle - the whole U
    views["beauty_overview"] = dict(eye=[-9.0, -9.5, 3.8], tgt=[-1.5, 0.0, -0.7])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. edge_graze (h0.35)  — **에이프런이 경고 밴드 너머로 완전 은닉**되는가(판정 1순위)
 2. edge_walk           — 밴드가 종주 소실선으로 수렴 + ㄷ자 90° 꺾임 판독
 3. bay_corner          — 도색 코너 연결·범퍼 열·만입 깊이 1.2 m 인지
 4. grid preset h0.9_d5 — 엣지 직교 접근에서 낙차 경계가 화면을 횡단
 5. 도색 밴드           — 황 박판이 밴드(0.35) 안에 내접, 공동 위 부유 없음
 6. 보행 연속성         — 데크가 베이를 우회 가능(y±3 바깥), 단부 파라펫으로 폐쇄
 7. Z-파이팅            — 데크 립 setback 0.03, 밴드 proud 0.0015/0.0035 층 분리"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene33")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene33"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def OBOX(path, center, size, mtl=None, rotz=0.0, rotx=0.0):
        return sc._oriented_box(stage, path, center, size, mtl,
                                rotz=rotz, rotx=rotx)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def RECT(path, x0, y0, x1, y1, z_c, hz, mtl=None, col=False):
        """A plan rectangle (x0..x1, y0..y1) -> a box converted to centre·size."""
        return BOX(path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z_c),
                   (x1 - x0, y1 - y0, hz), mtl, col=col)

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["deck"] = PBR(
            f"{ROOT}/Looks/Deck", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["deck_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["band_black"] = PBR(f"{ROOT}/Looks/BandBlack",
                              diffuse_color=mp["band_black"],
                              roughness_const=mp["band_black_rough"])
        for i, c in enumerate(mp["band_yellow"]):
            M[f"band_y{i}"] = PBR(
                f"{ROOT}/Looks/BandYellow_{i}", diffuse_color=c,
                roughness_const=mp["band_yellow_rough"][i])
        # [W2 fix batch F1] Ground-class decal materials for the kit — see the
        #   `scripts/const_color_audit.py` rule: a *ground* prim may not carry a
        #   texture-less constant. paint / metal / water / misc are excluded from
        #   `_CONST_MDL_CLASSES` by design, so binding a kit crack or stain to one
        #   left it as a dead flat ribbon.
        M["gk_crack"] = PBR(f"{ROOT}/Looks/GKitCrack",
                            diffuse_color=(0.055, 0.055, 0.056),
                            roughness_const=0.92)
        M["gk_stain"] = PBR(f"{ROOT}/Looks/GKitStain",
                            diffuse_color=(0.20, 0.20, 0.195),
                            roughness_const=0.86)
        M["rubber"] = PBR(f"{ROOT}/Looks/Rubber",
                          diffuse_color=mp["rubber_color"],
                          roughness_const=mp["rubber_rough"], metallic=0.0)
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        M["shutter"] = PBR(f"{ROOT}/Looks/Shutter",
                           diffuse_color=mp["shutter_color"],
                           metallic=mp["shutter_metallic"],
                           roughness_const=mp["shutter_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # ── Context dressing v2 materials ──
        M["pallet"] = PBR(
            f"{ROOT}/Looks/Pallet", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            sca["wood_dark"], tint=mp["pallet_tint"])
        for i, c in enumerate(mp["carton_colors"]):
            M[f"carton{i}"] = PBR(f"{ROOT}/Looks/Carton_{i}",
                                  diffuse_color=c,
                                  roughness_const=mp["carton_rough"])
        M["sign_face"] = PBR(f"{ROOT}/Looks/SignFace",
                             diffuse_color=mp["sign_face"],
                             roughness_const=mp["sign_rough"])
        M["sign_field"] = PBR(f"{ROOT}/Looks/SignField",
                              diffuse_color=mp["sign_field"],
                              roughness_const=mp["sign_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_body"],
                        metallic=mp["lamp_metallic"],
                        roughness_const=mp["lamp_rough"])
        M["lens"] = PBR(f"{ROOT}/Looks/Lens", diffuse_color=mp["lamp_lens"],
                        roughness_const=mp["lamp_lens_rough"])
        k = mp["container_door_mul"]
        for i, c in enumerate(mp["container_colors"]):
            M[f"cont{i}"] = PBR(f"{ROOT}/Looks/Container_{i}",
                                diffuse_color=c,
                                metallic=mp["container_metallic"],
                                roughness_const=mp["container_rough"])
            M[f"cont{i}_d"] = PBR(
                f"{ROOT}/Looks/ContainerDoor_{i}",
                diffuse_color=tuple(v * k for v in c),
                metallic=mp["container_metallic"],
                roughness_const=mp["container_rough"])
        for i, c in enumerate(mp["shed_colors"]):
            M[f"shed{i}"] = PBR(f"{ROOT}/Looks/Shed_{i}", diffuse_color=c,
                                metallic=mp["shed_metallic"],
                                roughness_const=mp["shed_rough"])
        M["shed_band"] = PBR(f"{ROOT}/Looks/ShedBand",
                             diffuse_color=mp["shed_band"],
                             metallic=mp["shed_metallic"],
                             roughness_const=mp["shed_rough"])
        M["galv"] = PBR(f"{ROOT}/Looks/Galv", diffuse_color=mp["galv_color"],
                        metallic=mp["galv_metallic"],
                        roughness_const=mp["galv_rough"])
        return M

    # -------------------------------------------------------------------
    # Apron (lower yard) - split into 4 boxes.
    #   S/N reach under(0.30) beneath the deck to close the gap under the lip, and the
    #   centre strip (Apron_C) and the bay floor (Apron_Bay) **meet exactly** at x=0 so they
    #   join with no top-face overlap (coplanar Z-fighting).
    # -------------------------------------------------------------------
    def build_apron(M, mtl):
        ap = PARAMS["apron"]
        # [W2-0 · P-A] The apron is a kit-dressing target too (trench·backing guide lines·stop line).
        sc.skin_exclude(f"{ROOT}/Apron_S", f"{ROOT}/Apron_N",
                        f"{ROOT}/Apron_C", f"{ROOT}/Apron_Bay")
        by = PARAMS["bay"]
        ms = PARAMS["mass"]
        H, th = ap["half"], ap["thick"]
        cz = ap["z_top"] - th / 2.0
        sb = ms["setback"]
        # Bites 0.05 deeper than the bay wall faces (y +-(3+sb), x −4−sb) so it is buried inside the wall
        ye = by["y1"] + sb + 0.05
        xb = by["x0"] - sb - 0.05
        RECT(f"{ROOT}/Apron_S", -H, -H, H, -ye, cz, th, mtl, col=True)
        RECT(f"{ROOT}/Apron_N", -H, ye, H, H, cz, th, mtl, col=True)
        RECT(f"{ROOT}/Apron_C", by["x1"], -ye, H, ye, cz, th, mtl, col=True)
        RECT(f"{ROOT}/Apron_Bay", xb, -ye, by["x1"], ye, cz, th, mtl, col=True)

    # -------------------------------------------------------------------
    # Platform - **U-shaped bay cut: deck split into 3 boxes + mass into 3 boxes** (lesson 5)
    #   No box covers the bay void.
    # -------------------------------------------------------------------
    def build_platform(M):
        d = PARAMS["deck"]
        by = PARAMS["bay"]
        ms = PARAMS["mass"]
        th = d["thick"]
        czd = d["z_top"] - th / 2.0
        sb = ms["setback"]
        czm = (ms["z_bot"] + ms["z_top"]) / 2.0
        hzm = ms["z_top"] - ms["z_bot"]
        # [W2-0 · P-A] The deck top slab is a ground_kit dressing target -> displacement skin
        #   OFF (registered **before the RECT calls**). Without it the joint·patch·stain decals are
        #   buried wholesale under the skin (+6.5~16.5 mm) `[spec §1.1]`.
        sc.skin_exclude(f"{ROOT}/Deck_W", f"{ROOT}/Deck_S", f"{ROOT}/Deck_N")
        # ── Deck top slab split in 3 ──
        RECT(f"{ROOT}/Deck_W", d["x_w"], d["y_s"], by["x0"], d["y_n"],
             czd, th, M["deck"], col=True)
        RECT(f"{ROOT}/Deck_S", by["x0"], d["y_s"], d["x_e"], by["y0"],
             czd, th, M["deck"], col=True)
        RECT(f"{ROOT}/Deck_N", by["x0"], by["y1"], d["x_e"], d["y_n"],
             czd, th, M["deck"], col=True)
        # ── Mass (dock-edge wall) split in 3 - exposed faces pulled back by setback ──
        #    Mass_S/N overlap Mass_W by 0.07 to remove the internal butt face
        RECT(f"{ROOT}/Mass_W", d["x_w"], d["y_s"] + sb, by["x0"] - sb,
             d["y_n"] - sb, czm, hzm, M["wall"], col=True)
        #    The +-Y outer faces sit 0.02 inside Mass_W and the z range 0.005/0.01 inside ->
        #    removes the coplanar outer-wall and top/bottom faces at the corner overlap
        czs, hzs = czm + 0.0025, hzm - 0.015
        RECT(f"{ROOT}/Mass_S", by["x0"] - sb - 0.07, d["y_s"] + sb + 0.02,
             d["x_e"] - sb, by["y0"] - sb, czs, hzs, M["wall"], col=True)
        RECT(f"{ROOT}/Mass_N", by["x0"] - sb - 0.07, by["y1"] + sb,
             d["x_e"] - sb, d["y_n"] - sb - 0.02, czs, hzs, M["wall"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False control: bay·dock edge filled in, the whole area a z=0 flat."""
        d = PARAMS["deck"]
        ap = PARAMS["apron"]
        H = ap["half"]
        # [W2-0 · P-A] The control's flat deck is a kit-dressing target too -> skin OFF.
        sc.skin_exclude(f"{ROOT}/FlatDeck")
        RECT(f"{ROOT}/FlatDeck", d["x_w"], -H, H, H,
             d["z_top"] - 0.5, 1.0, M["deck"], col=True)

    # -------------------------------------------------------------------
    # Warning paint band - black base strip + alternating yellow 45 deg plates (wear = 3 tint grades + dropout)
    #   The U-shaped edge line is decomposed into **5 mutually non-overlapping rectangular spans**
    #   so base strips overlapping at a corner (coplanar Z-fighting) are eliminated at source.
    # -------------------------------------------------------------------
    def band_segments():
        by = PARAMS["bay"]
        bd = PARAMS["band"]
        W = bd["width"]
        ye = bd["y_end"]
        x0, x1, y0, y1 = by["x0"], by["x1"], by["y0"], by["y1"]
        # (name, x0, y0, x1, y1, long axis, drop-side edges)
        return [
            # Main dock edge, south span (starts at y −3−W so it does not overlap the bay corner paint)
            ("MainS", x1 - W, -ye, x1, y0 - W, "y", ("x1",)),
            ("MainN", x1 - W, y1 + W, x1, ye, "y", ("x1",)),
            # Top of the bay south·north walls (extended along x to include the corner square)
            #   the east end (x1=0) is a main dock edge drop face too, so it is pulled back as well
            ("BayS", x0 - W, y0 - W, x1, y0, "x", ("y1", "x1")),
            ("BayN", x0 - W, y1, x1, y1 + W, "x", ("y0", "x1")),
            # Top of the bay back wall (meets the south·north spans at y=+-3)
            ("BayBack", x0 - W, y0, x0, y1, "y", ("x1",)),
        ]

    def build_band(M):
        bd = PARAMS["band"]
        W, w = bd["width"], bd["stripe_w"]
        # Long-side length at which a 45 deg rotated rectangle is exactly inscribed in a band of width W
        L = W * math.sqrt(2.0) - w
        cz_base = bd["base_proud"] - bd["base_t"] / 2.0
        cz_st = bd["stripe_proud"] - bd["stripe_t"] / 2.0
        rng = random.Random(bd["seed"])
        yell = [M[f"band_y{i}"] for i in range(len(mp["band_yellow"]))]
        wts = mp["band_yellow_w"]
        n_stripe = 0
        ins = bd["lip_inset"]
        for name, x0, y0, x1, y1, axis, dsides in band_segments():
            bx0, by0, bx1, by1 = x0, y0, x1, y1
            for dside in dsides:
                if dside == "x1":
                    bx1 -= ins
                elif dside == "x0":
                    bx0 += ins
                elif dside == "y1":
                    by1 -= ins
                else:
                    by0 += ins
            RECT(f"{ROOT}/Band_{name}_Base", bx0, by0, bx1, by1,
                 cz_base, bd["base_t"], M["band_black"])
            if axis == "y":
                a0, a1 = y0, y1
                cc = (x0 + x1) / 2.0
            else:
                a0, a1 = x0, x1
                cc = (y0 + y1) / 2.0
            n = max(int((a1 - a0) / bd["pitch"]), 1)
            for i in range(n):
                a = a0 + (i + 0.5) * (a1 - a0) / n
                if rng.random() < bd["drop_ratio"]:
                    continue                       # paint dropout (wear)
                mtl = rng.choices(yell, weights=wts, k=1)[0]
                cx, cy = (cc, a) if axis == "y" else (a, cc)
                OBOX(f"{ROOT}/Band_{name}_S_{i}", (cx, cy, cz_st),
                     (L, w, bd["stripe_t"]), mtl, rotz=45.0)
                n_stripe += 1
        return n_stripe

    # -------------------------------------------------------------------
    # Dock bumpers - black rubber boxes fixed to the top of the wall face (spacing 1.2 m). They project
    #   further forward than the deck lip, giving rhythm to the shadow under the dock edge (reference reproduction).
    # -------------------------------------------------------------------
    def build_bumpers(M):
        bp = PARAMS["bumper"]
        by = PARAMS["bay"]
        d = PARAMS["deck"]
        sb = PARAMS["mass"]["setback"]
        cz = bp["z_top"] - bp["h"] / 2.0
        idx = [0]

        def row(face_c, a0, a1, axis, sgn):
            """axis='y': the wall face is at x=face_c and the bumper projects along sgn·x / 'x': the reverse."""
            span = a1 - a0
            n = max(int(span / bp["spacing"]), 1)
            for i in range(n):
                a = a0 + (i + 0.5) * span / n
                # 0.03 embedded into the wall face + projecting by proud
                c_off = sgn * (bp["proud"] / 2.0 - 0.015)
                if axis == "y":
                    ctr = (face_c + c_off, a, cz)
                    size = (bp["proud"] + 0.03, bp["w"], bp["h"])
                else:
                    ctr = (a, face_c + c_off, cz)
                    size = (bp["w"], bp["proud"] + 0.03, bp["h"])
                BOX(f"{ROOT}/Bumper_{idx[0]}", ctr, size, M["rubber"])
                idx[0] += 1

        # Bay back wall (x = −4−sb, projecting +X)
        row(by["x0"] - sb, by["y0"], by["y1"], "y", +1.0)
        # Bay south·north walls (y = ∓(3+sb), projecting into the bay)
        row(by["y0"] - sb, by["x0"], by["x1"], "x", +1.0)
        row(by["y1"] + sb, by["x0"], by["x1"], "x", -1.0)
        # Main dock edge (x = −sb, projecting +X) - the south·north spans outside the bay
        row(d["x_e"] - sb, d["y_s"] + 1.0, by["y0"] - 0.6, "y", +1.0)
        row(d["x_e"] - sb, by["y1"] + 0.6, d["y_n"] - 1.0, "y", +1.0)
        return idx[0]

    # -------------------------------------------------------------------
    # End parapets (+-Y) - remove the unguarded drop at the platform ends (confines the GT to the U-shaped edge)
    # -------------------------------------------------------------------
    def build_parapets(M):
        d = PARAMS["deck"]
        pp = PARAMS["parapet"]
        cz = (pp["base_z"] + pp["h"]) / 2.0
        hz = pp["h"] - pp["base_z"]
        # The dock-edge end is pulled back 0.05 and the outer (+-Y) face by outer_inset to
        # avoid a coplanar face with the deck's cut face
        xe = d["x_e"] - 0.05
        oi = pp["outer_inset"]
        RECT(f"{ROOT}/Parapet_S", d["x_w"], d["y_s"] + oi, xe,
             d["y_s"] + pp["t"], cz, hz, M["wall"], col=True)
        RECT(f"{ROOT}/Parapet_N", d["x_w"], d["y_n"] - pp["t"], xe,
             d["y_n"] - oi, cz, hz, M["wall"], col=True)

    # -------------------------------------------------------------------
    # Background dressing - shutter door wall (+X horizon closure) · warehouse wall (-X) · 2 bollards
    # -------------------------------------------------------------------
    def build_dressing(M):
        sh = PARAMS["shutter"]
        ap = PARAMS["apron"]
        zb = ap["z_top"] - 0.3
        # +X shutter door wall - closes the horizon straight down the main camera axis (brief §A-4)
        RECT(f"{ROOT}/ShutterWall", sh["x0"], -sh["y_half"],
             sh["x0"] + sh["t"], sh["y_half"],
             (zb + sh["z_top"]) / 2.0, sh["z_top"] - zb, M["wall"], col=True)
        dw, dh = sh["door_w"], sh["door_h"]
        dz0 = ap["z_top"] - 0.05          # bottom embedded 0.05 into the apron (avoids a coplanar face)
        for j, dy in enumerate(sh["door_ys"]):
            # Door panel: door_embed into the wall face (x0) + door_proud projecting
            px0 = sh["x0"] - sh["door_proud"]
            px1 = sh["x0"] + sh["door_embed"]
            RECT(f"{ROOT}/Door_{j}", px0, dy - dw / 2.0, px1, dy + dw / 2.0,
                 dz0 + dh / 2.0, dh, M["shutter"])
            # Vertical ribs (proud of the panel front)
            nr = max(int(dw / sh["rib_step"]), 1)
            for k in range(nr):
                ry = dy - dw / 2.0 + (k + 0.5) * dw / nr
                RECT(f"{ROOT}/Door_{j}_Rib_{k}",
                     px0 - sh["rib_proud"], ry - sh["rib_w"] / 2.0,
                     px0 + 0.02, ry + sh["rib_w"] / 2.0,
                     dz0 + 0.03 + (dh - 0.09) / 2.0, dh - 0.09, M["shutter"])
        # -X warehouse wall (behind the platform) - site closure
        wh = PARAMS["warehouse"]
        RECT(f"{ROOT}/Warehouse", wh["x1"] - wh["t"], -wh["y_half"],
             wh["x1"], wh["y_half"],
             (zb + wh["z_top"]) / 2.0, wh["z_top"] - zb, M["wall"], col=True)
        # 2 yellow bollards (bay corner protection) - v5.1 spec + top reflective band,
        #   dot tactile paving not installed as this is an industrial yard (see the PARAMS comment).
        bo = PARAMS["bollard"]
        for i, bd in enumerate(PARAMS["bollards"]):
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bd["cx"],
                                 bd["cy"], bo["base_z"], None, M["bollard"],
                                 M["bollard_band"], None,
                                 radius=bo["radius"], height=bo["height"],
                                 tactile=bo["tactile"])

    # -------------------------------------------------------------------
    # Context dressing v2 - pallet stacks · forklift traffic paint · dock number signs ·
    #                       wall lamps · apron containers · light masts · distant warehouse blocks
    # -------------------------------------------------------------------
    def build_ground_kit(M, yard=True):
        """[W2] ground_kit - P14 yard_industrial, **2 plans: deck + yard**.

        A single `plan_ground` is raised at one z, so z=0 (deck) and z=−1.2
        (apron) cannot be held in one call. The two plans each pass the prim
        budget (<=60) and the gates.
        """
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["band_black"], crack=M["gk_crack"],
                  patch=M["deck"], patch_cut=M["gk_crack"],
                  trench=M["galv"], trench_frame=M["rail"],
                  marking=M["sign_face"], weed=M["rubber"],
                  stain_tire=M["gk_stain"], stain_oil=M["gk_crack"],
                  stain_dirt=M["asphalt"])
        total = 0
        for tag, gp in ground_plans():
            if tag == "yard" and not yard:
                continue
            res = gk.apply_ground(kit, f"{ROOT}/GKit/{tag.capitalize()}", gp, M2,
                                  skin_exclude=sc.skin_exclude,
                                  scatter=sc.scatter_debris)
            total += res["prims"]
            print(f"[ground_kit] sceneD1 P14/{tag} · 프림 {res['prims']} · "
                  f"δmax {res['gt_delta_max']:.4f} · "
                  f"unit_cell {res['unit_cell']}")
        return total

    def build_yard_dressing(M):
        """Logistics-warehouse loading dock context elements. **Drop geometry·paint band·bumpers·apron unchanged.**

        ── Camera check (all views, basis for the coordinates) ─────────────
        View: grid_views hfov 60 deg (half tan 0.577) · pitch −10 deg · 16:9 -> vfov 36 deg.
        1) The only new solids on the deck are the 3 pallet stacks.
           N1(−2.55, 7.80) / N2(−5.60, 10.20): **beyond the bay north lip (y=3)**.
             · grid(gy=−4): frame left bound y <= −4+0.577·(x+10) -> at x=−2.55, y <= 0.30
               -> y 7.8/10.2 are **outside the frame** (0 occlusion).
             · edge_walk(eye −1.25,−9 -> tgt −0.75,0.5): 9.6 deg off axis (inside the frame) but
               **farther away** than the bay·main-edge paint (y <= 3.35), so occlusion is impossible in principle.
             · bay_corner(eye −1.10,−5.0,1.55, 27 deg down): horizontal 24.8 deg/vertical −4.3 deg ->
               above the vfov upper bound (−27+18=−9 deg) -> outside the frame.
           S1(−3.60, −7.40, total height 0.48): south staging.
             · grid d10(eye −10,−4): frame right bound y >= −4−0.577·6.4 = −7.69 -> it clips.
               The main-edge points this stack hides run from y −4+(10/6.4)(−3.4) = −9.31 ..
               to the frame right bound −9.77, i.e. **only the 0.46 m rightmost corner span** (it hides
               none of the central band·bay corner that are being judged).
             · d5/d2·edge_approach·edge_graze: off axis or behind the camera -> irrelevant.
             · beauty_overview(eye −9,−9.5,3.8): 30.4 deg off the view axis -> outside the frame border.
        2) The traffic paint is flush (proud <= 0.0019) - no effect on hiding·occlusion.
           The edge approach path (x −10..0 x y −5..−3) carries **0 solids** (paint only).
        3) The far field (containers·light masts·warehouse blocks) is all x >= 7.4 = beyond the drop.
           edge_graze(eye z 0.35, 2.4 m to the edge) hiding limit x = 1.2·2.4/0.35
           = 8.23 m -> the containers' near end min x = 8.91(C2) is **outside the hiding limit**, so
           they give far-field context without breaking the near-apron hiding.
        4) The new prim closest to a camera position (eye of any view) = stack S1(−3.60,−7.40) <->
           beauty_overview eye(−9.0,−9.5,3.8): horizontal 6.0 m·vertical 3.3 m -> not buried.
        """
        yd = PARAMS["yard"]
        sh = PARAMS["shutter"]
        ap = PARAMS["apron"]
        cnt = dict(pallet=0, carton=0, lane=0, sign=0, lamp=0,
                   container=0, mast=0, shed=0)

        # ── (1) Timber pallet stacks (approximated by stacked boxes) ──
        pl = yd["pallet"]
        ct = yd["carton"]
        ph = pl["bot_t"] + pl["string_h"] + pl["top_t"]      # actual height (no voids)
        crng = random.Random(ct["seed"])
        ncar = len(mp["carton_colors"])
        for st in yd["stacks"]:
            cx, cy, yaw = st["cx"], st["cy"], st["yaw"]
            a = math.radians(yaw)
            ca, sa = math.cos(a), math.sin(a)

            def place(dx, dy, _cx=cx, _cy=cy, _ca=ca, _sa=sa):
                return (_cx + dx * _ca - dy * _sa, _cy + dx * _sa + dy * _ca)

            tag = st["tag"]
            for i in range(int(st["n_pallet"])):
                z0 = i * ph
                OBOX(f"{ROOT}/Pallet_{tag}_{i}_Bot",
                     (cx, cy, z0 + pl["bot_t"] / 2.0),
                     (pl["w"], pl["d"], pl["bot_t"]), M["pallet"], rotz=yaw)
                for j, dx in enumerate((-(pl["w"] - pl["string_w"]) / 2.0, 0.0,
                                        (pl["w"] - pl["string_w"]) / 2.0)):
                    sx, sy = place(dx, 0.0)
                    OBOX(f"{ROOT}/Pallet_{tag}_{i}_S{j}",
                         (sx, sy, z0 + pl["bot_t"] + pl["string_h"] / 2.0),
                         (pl["string_w"], pl["d"], pl["string_h"]),
                         M["pallet"], rotz=yaw)
                OBOX(f"{ROOT}/Pallet_{tag}_{i}_Top",
                     (cx, cy, z0 + ph - pl["top_t"] / 2.0),
                     (pl["w"], pl["d"], pl["top_t"]), M["pallet"], rotz=yaw)
                cnt["pallet"] += 1
            zc0 = int(st["n_pallet"]) * ph
            for b in range(int(st["n_box"])):
                bx, by = place(crng.uniform(-0.15, 0.15),
                               crng.uniform(-0.11, 0.11))
                OBOX(f"{ROOT}/Carton_{tag}_{b}",
                     (bx, by, zc0 + ct["h"] * (b + 0.5)),
                     (ct["w"], ct["d"], ct["h"]),
                     M[f"carton{crng.randrange(ncar)}"],
                     rotz=yaw + crng.uniform(-9.0, 9.0))
                cnt["carton"] += 1

        # ── (2) Forklift traffic paint (worn yellow dashes) ──
        ln = yd["lane"]
        lrng = random.Random(ln["seed"])
        ymtl = [M["band_y1"], M["band_y2"]]
        cz_m = ln["proud_main"] - ln["t"] / 2.0
        cz_c = ln["proud_cross"] - ln["t"] / 2.0     # the crossing sits 0.7 mm higher -> 0 coplanar

        def dashed(tag, a0, a1, fixed, axis, cz):
            step = ln["dash"] + ln["gap"]
            n = max(int((a1 - a0) / step), 1)
            k = 0
            for i in range(n):
                s = a0 + i * step
                e = min(s + ln["dash"], a1)
                if e - s < 0.30 or lrng.random() < ln["drop"]:
                    continue
                mtl = ymtl[lrng.randrange(len(ymtl))]
                if axis == "x":
                    RECT(f"{ROOT}/Lane_{tag}_{k}", s, fixed - ln["w"] / 2.0,
                         e, fixed + ln["w"] / 2.0, cz, ln["t"], mtl)
                else:
                    RECT(f"{ROOT}/Lane_{tag}_{k}", fixed - ln["w"] / 2.0, s,
                         fixed + ln["w"] / 2.0, e, cz, ln["t"], mtl)
                k += 1
            cnt["lane"] += k

        for i, ly in enumerate(ln["main_ys"]):
            dashed(f"MS{i}", ln["x0"], ln["x1"], ly, "x", cz_m)
        for i, ly in enumerate(ln["north_ys"]):
            dashed(f"MN{i}", ln["x0"], ln["x1"], ly, "x", cz_m)
        for i, lx in enumerate(ln["cross_xs"]):
            dashed(f"CX{i}", ln["cy0"], ln["cy1"], lx, "y", cz_c)

        # ── (3) Dock number sign plates (beside the shutter door, textless colour field) ──
        ds = yd["docksign"]
        px1 = sh["x0"] + 0.01                     # 1 cm bite into the wall face (22.0)
        px0 = px1 - ds["t"]
        for j, dy in enumerate(sh["door_ys"]):
            sy = dy - sh["door_w"] / 2.0 - ds["off"]
            RECT(f"{ROOT}/DockSign_{j}", px0, sy - ds["w"] / 2.0,
                 px1, sy + ds["w"] / 2.0, ds["z_c"], ds["h"], M["sign_face"])
            RECT(f"{ROOT}/DockSign_{j}_F", px0 - 0.012, sy - ds["fw"] / 2.0,
                 px0 + 0.010, sy + ds["fw"] / 2.0, ds["z_c"] - 0.03,
                 ds["fh"], M["sign_field"])
            cnt["sign"] += 1

        # ── (4) Wall-mounted exterior lamp boxes (daytime - no emission) ──
        lp = yd["lamp"]
        wh = PARAMS["warehouse"]
        for j, ly in enumerate(lp["shutter_ys"]):
            bx1 = sh["x0"] + 0.02
            bx0 = bx1 - lp["d"]
            RECT(f"{ROOT}/WallLamp_S{j}", bx0, ly - lp["w"] / 2.0,
                 bx1, ly + lp["w"] / 2.0, lp["shutter_z"], lp["h"], M["lamp"])
            RECT(f"{ROOT}/WallLamp_S{j}_L", bx0 - lp["lens_t"],
                 ly - lp["w"] / 2.0 + 0.05, bx0 + 0.01,
                 ly + lp["w"] / 2.0 - 0.05, lp["shutter_z"] - 0.03,
                 lp["h"] - 0.09, M["lens"])
            cnt["lamp"] += 1
        for j, ly in enumerate(lp["wh_ys"]):
            bx0 = wh["x1"] - 0.02
            bx1 = bx0 + lp["d"]
            RECT(f"{ROOT}/WallLamp_W{j}", bx0, ly - lp["w"] / 2.0,
                 bx1, ly + lp["w"] / 2.0, lp["wh_z"], lp["h"], M["lamp"])
            RECT(f"{ROOT}/WallLamp_W{j}_L", bx1 - 0.01,
                 ly - lp["w"] / 2.0 + 0.05, bx1 + lp["lens_t"],
                 ly + lp["w"] / 2.0 - 0.05, lp["wh_z"] - 0.03,
                 lp["h"] - 0.09, M["lens"])
            cnt["lamp"] += 1

        # ── (5) Apron containers (far-field silhouette - outside the 8.2 m hiding limit) ──
        cn = yd["container"]
        for j, cd in enumerate(yd["containers"]):
            a = math.radians(cd["yaw"])
            for t in range(int(cd["tier"])):
                zb = ap["z_top"] + t * (cn["H"] - cn["gap"])
                zc = zb + cn["H"] / 2.0
                OBOX(f"{ROOT}/Container_{j}_{t}", (cd["cx"], cd["cy"], zc),
                     (cn["L"], cn["W"], cn["H"]), M[f"cont{cd['tone']}"],
                     rotz=cd["yaw"])
                # Door end: 1 cm proud of the body·1.5 cm wider·3 cm inside top and bottom -> 0 coplanar
                ex = cd["cx"] + math.cos(a) * (cn["L"] / 2.0 - 0.05)
                ey = cd["cy"] + math.sin(a) * (cn["L"] / 2.0 - 0.05)
                OBOX(f"{ROOT}/Container_{j}_{t}_D", (ex, ey, zc),
                     (0.12, cn["W"] + 0.015, cn["H"] - 0.06),
                     M[f"cont{cd['tone']}_d"], rotz=cd["yaw"])
                cnt["container"] += 1

        # ── (6) Yard light masts (silhouettes rising above the shutter wall z 7.0) ──
        ms = yd["mast"]
        for j, md in enumerate(yd["masts"]):
            zb = ap["z_top"] - 0.10                # 0.10 embedded into the apron
            CYL(f"{ROOT}/Mast_{j}", (md["cx"], md["cy"], zb + ms["h"] / 2.0),
                ms["r"], ms["h"], M["galv"])
            BOX(f"{ROOT}/Mast_{j}_Head",
                (md["cx"], md["cy"], zb + ms["h"] - ms["head_h"] / 2.0 + 0.03),
                (ms["head_w"], ms["head_d"], ms["head_h"]), M["lamp"])
            cnt["mast"] += 1

        # ── (7) Distant warehouse blocks (only the tops exposed above the shutter wall) ──
        shd = yd["shed"]
        for j, sd in enumerate(yd["sheds"]):
            z0 = shd["z_bot"]
            RECT(f"{ROOT}/Shed_{j}", sd["x0"], sd["y0"], sd["x1"], sd["y1"],
                 (z0 + sd["z_top"]) / 2.0, sd["z_top"] - z0,
                 M[f"shed{sd['tone']}"])
            p = shd["band_proud"]
            RECT(f"{ROOT}/Shed_{j}_Band", sd["x0"] - p, sd["y0"] - p,
                 sd["x1"] + p, sd["y1"] + p,
                 sd["z_top"] - shd["band_h"] / 2.0 + 0.20, shd["band_h"],
                 M["shed_band"])
            vx = (sd["x0"] + sd["x1"]) / 2.0
            nv = int(shd["vent_n"])
            for i in range(nv):
                vy = sd["y0"] + (sd["y1"] - sd["y0"]) * (i + 1) / (nv + 1)
                RECT(f"{ROOT}/Shed_{j}_V{i}",
                     vx - shd["vent_w"] / 2.0, vy - shd["vent_w"] / 2.0,
                     vx + shd["vent_w"] / 2.0, vy + shd["vent_w"] / 2.0,
                     sd["z_top"] + 0.15 + shd["vent_h"] / 2.0, shd["vent_h"],
                     M["shed_band"])
            cnt["shed"] += 1
        return cnt

    # -------------------------------------------------------------------
    # cue - safety railing around the bay (default OFF: unguarded is this scene's hazard essence)
    # -------------------------------------------------------------------
    def build_railing(M):
        by = PARAMS["bay"]
        rr = PARAMS["bay_rail"]
        o = rr["offset"]
        # U-shaped railing line: (x1,y0−o) -> (x0−o,y0−o) -> (x0−o,y1+o) -> (x1,y1+o)
        pts = [(by["x1"], by["y0"] - o), (by["x0"] - o, by["y0"] - o),
               (by["x0"] - o, by["y1"] + o), (by["x1"], by["y1"] + o)]
        nid = [0]
        for s in range(len(pts) - 1):
            ax, ay = pts[s]
            bx, by_ = pts[s + 1]
            length = math.hypot(bx - ax, by_ - ay)
            mx, my = (ax + bx) / 2.0, (ay + by_) / 2.0
            along_x = abs(by_ - ay) < 1e-9
            for tag, zc in (("Top", rr["rail_h"]), ("Mid", rr["mid_h"])):
                if along_x:
                    CYL(f"{ROOT}/BayRail_{tag}_{s}", (mx, my, zc),
                        rr["rail_r"], length, M["rail"], rotY=90.0)
                else:
                    CYL(f"{ROOT}/BayRail_{tag}_{s}", (mx, my, zc),
                        rr["rail_r"], length, M["rail"], rotX=90.0)
            npost = max(int(length / rr["spacing"]), 1)
            for i in range(npost + 1):
                t = i / float(npost)
                px, py = ax + (bx - ax) * t, ay + (by_ - ay) * t
                CYL(f"{ROOT}/BayRail_Post_{nid[0]}",
                    (px, py, rr["rail_h"] / 2.0 - 0.05),
                    rr["post_r"], rr["rail_h"] + 0.10, M["rail"])
                nid[0] += 1

    # ── Scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    # Material contrast toggle: when OFF the apron is concrete too (removes the asphalt/concrete contrast)
    apron_mtl = M["asphalt"] if cfg["cue_material_break"] else M["deck"]

    n_stripe, n_bumper = 0, 0
    if cfg["hazard_stairs"]:
        build_apron(M, apron_mtl)
        build_platform(M)
        n_bumper = build_bumpers(M)
        if cfg["cue_nosing"]:
            n_stripe = build_band(M)
        if cfg["cue_railing"]:
            build_railing(M)
        build_parapets(M)
    else:
        build_flat_fill(M)
    yard_cnt = None
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        yard_cnt = build_yard_dressing(M)
    #  [W2] Ground elements - after the dressing (scatter convention). **The deck plan runs in the
    #  control arm too** (the twins' only difference must be the drop geometry). The yard plan is at
    #  z=−1.2, so in the flat control (FlatDeck top face z=0) it would be buried and is left out.
    build_ground_kit(M, yard=bool(cfg["hazard_stairs"]))

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # Geometry self-verification print (for the director's re-check)
    by, bd, ap = PARAMS["bay"], PARAMS["band"], PARAMS["apron"]
    drop = PARAMS["deck"]["z_top"] - ap["z_top"]
    L = bd["width"] * math.sqrt(2.0) - bd["stripe_w"]
    aabb = (L + bd["stripe_w"]) / math.sqrt(2.0)
    shadow = drop / math.tan(math.radians(PARAMS["light"]["noon_sun_elev"]))
    print(f"[기하] ㄷ자 베이 폭 {by['y1'] - by['y0']:.2f}(y) × "
          f"깊이 {by['x1'] - by['x0']:.2f}(x) m · 낙차 {drop:.2f} m")
    print(f"[도색] 밴드 폭 {bd['width']:.3f} · 황 박판 {L:.3f}×"
          f"{bd['stripe_w']:.3f} @45° → AABB {aabb:.3f} m "
          f"(밴드 내접 오차 {abs(aabb - bd['width']):.2e}) · 박판 {n_stripe}개")
    print(f"[범퍼] {n_bumper}개 · [조명] 연단 그림자 폭 {shadow:.2f} m "
          f"(에이프런 근경 암대)")

    if yard_cnt is not None:
        # Context dressing self-check - the camera interference numbers for new solids on the deck
        yd = PARAMS["yard"]
        gy = GRID_GY
        lines = []
        for st in yd["stacks"]:
            # Against grid d10 (eye −10, gy): frame half width 0.577·dx, occlusion reach y@x=0
            dx = st["cx"] + 10.0
            half = 0.577 * dx
            inframe = abs(st["cy"] - gy) <= half
            y_at_edge = gy + (10.0 / dx) * (st["cy"] - gy) if dx > 1e-6 else 0.0
            lines.append(f"{st['tag']}({st['cx']:+.2f},{st['cy']:+.2f}) "
                         f"d10프레임={'IN' if inframe else 'OUT'} "
                         f"가림도달 y@x=0 {y_at_edge:+.2f}")
        graze_hide = 1.2 * 2.4 / 0.35
        cL, cW = yd["container"]["L"], yd["container"]["W"]
        cmin = min(c["cx"] - (cW if abs(c["yaw"] - 90.0) < 1e-6 else cL) / 2.0
                   for c in yd["containers"])
        print("[드레싱] 팔레트 " + str(yard_cnt["pallet"]) + "매·박스 "
              + str(yard_cnt["carton"]) + " · 통행도색 "
              + str(yard_cnt["lane"]) + "절 · 표지 " + str(yard_cnt["sign"])
              + " · 외등 " + str(yard_cnt["lamp"]) + " · 컨테이너 "
              + str(yard_cnt["container"]) + " · 조명탑 "
              + str(yard_cnt["mast"]) + " · 창고동 " + str(yard_cnt["shed"]))
        for s in lines:
            print(f"[검산] {s}")
        print(f"[검산] edge_graze 에이프런 은닉 한계 x={graze_hide:.2f} m < "
              f"컨테이너 근단 x={cmin:.2f} m → 은닉 특색 불변")

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneD1 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD1_{ts}.png")
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
