# -*- coding: utf-8 -*-
"""
scene16_canopy_shadow.py — NegObs synthetic scene 16: canopy shadow stair (Isaac Sim 4.5)

Type    : T20 canopy stair (the inverse of T3 — the upper shadow band is the danger signal)
Spec    : Docs/multi_scene_brief_v3.md §D scene16_canopy_shadow
Shared  : scene_common.py (verified API helpers) · scene02_underpass.py (urban skeleton)

Hazard   : a descending stair (14 steps) sits in the middle of a bright sidewalk, with a solid
           canopy over it. In noon light the whole stair is sunk in the canopy shadow and reads
           as a dark band — the inverse of T3 (dark below): here the **upper shadow band** that
           floats above is what signals the drop. The cue_nosing yellow strip survives inside
           the shadow at low contrast.
Goal     : assemble the bright sidewalk (plaza_lower) + descending stair (plaza_light) + canopy
           (solid roof + 4 columns) + lower passage + planters·buildings, and judge by render (render only).

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene16_canopy_shadow.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene16_canopy_shadow.py
Smoke early exit:         NEGOBS_SMOKE=1  python scene16_canopy_shadow.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk
import stair_kit as sk       # [realism v1] statutory handrail (§15(3)/(4))


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs toggles geometry (False->pit filled flat).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> pit/stairs/passage become z=0 flat (only geometry toggle)
    # [realism v1] The four stair lines (west + east exit) are now statutory
    #   **handrails** (§15(3)/(4)) - one pipe per side, no mid rail, no balusters.
    #   Both stairs are wall to wall, so §15(1)2 is met by the "wall". The pit
    #   perimeter guard is unchanged. Docs/reports/scene15_railing_fix_v1.md §8.
    "cue_railing":        True,   # one handrail per stair side + guardrail around the pit at ground level
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality - OFF by default (path kept for ablation)   # dot tactile paving: top warning strip + lower passage
    "cue_material_break": True,   # False -> stairs·passage also take the sidewalk material (plaza_lower)
    "cue_nosing":         True,   # yellow non-slip strip on every step (low contrast inside the shadow - the signature)
    "cue_sign":           True,   # [v5 shared layer] one sign_exit (underpass exit)
    "cue_scene_dressing": True,   # planters·buildings·distant vista, all together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    walk=dict(x_w=-12.0, x_e=22.0, y_s=-8.0, y_n=8.0, z_top=0.0, thick=0.5),
    # descending pit (trench): stair width 3 (y +-1.5), outer wall faces +-1.8
    pit=dict(x0=0.0, x1=4.48, y0=-1.5, y1=1.5),
    # 14 steps x riser 0.15 · tread 0.32 -> drop 2.1m, run 4.48m
    stairs=dict(x0=0.0, riser=0.15, tread=0.32, nsteps=14,
                y0=-1.5, y1=1.5, z_top=0.0, base_z=-2.6),
    # lower passage (plaza_lower), continuing +X and rising again at the east exit stair.
    passage=dict(x0=4.48, x1=14.0, z_top=-2.1, base_z=-2.6),
    # [audit v4 A1] east exit stair - there used to be a full-width blocking wall (Wall_E) at x=14,
    #   so you went down 2.1 m, walked 9.5 m and hit a dead end with no way out.
    #   A descending stair is built inside a rot_group 180 deg (pivot x=(14+18.48)/2) and maps
    #   to an ascending stair: local x=14(z=0) -> world x=18.48, local x=18.48(z=-2.1) ->
    #   world x=14.0 (flush with the passage top). This completes the scene as an "underpass".
    east_stairs=dict(x0=14.0, riser=0.15, tread=0.32, nsteps=14,
                     y0=-1.5, y1=1.5, z_top=0.0, base_z=-2.6),
    # [realism v1] `x_start` retired — it is now derived as x0 − ext_top.
    east_rail=dict(y=1.43),
    # east end of wall·trench = top of the east stair (14.0 + 14*0.32 = 18.48)
    wall=dict(thick=0.3, y_in=1.5, parapet_top=0.15, base_z=-2.6, x1=18.48),

    # canopy: covers the whole stair (x 0..4.48) + 1m past the head (x -1). Roof z=2.6, 4 columns.
    canopy=dict(x0=-1.0, x1=4.6, y0=-2.0, y1=2.0, z_roof=2.6, post_r=0.13,
                roof_t=0.14, base_z=-0.05),

    # cue
    # [audit v4 B1] perim_rail y 1.9 -> 1.65. y=1.9 sat outside the parapet (y 1.5..1.8), leaving
    #   a 15 cm gap between the post foot (z=0.15) and the sidewalk (z=0). y=1.65 is the
    #   parapet wall centreline -> the posts sit exactly on the parapet top (0.15).
    #   x1 4.48 -> 18.48 : guards the whole trench (including the east exit stair).
    perim_rail=dict(y=1.65, x0=0.0, x1=18.48, x_rear=None,
                    parapet_top=0.15, rail_h=0.9, post_r=0.03,
                    rail_r=0.03, rail_mid_r=0.018, mid_h=0.45, spacing=1.2),
    # ═══ [realism v1] Stair rail → statutory handrail (§15(3)/(4)) ══════════
    #  Old: `y=1.4, x_start=-0.5, rail_h=0.9, post_r=0.02, rail_r=0.03,
    #        rail_mid_r=0.018, rail_mid_drop=0.45, spacing=1.2` through
    #        `sc.build_railing_line`, used by **both** the west stair and the
    #        east exit stair — a full guardrail per side (top + mid rail + 43
    #        balusters + 5 posts + a second coaxial LOOK_GEO handrail with its
    #        own 5 posts) × 4 lines = 240 prims, **39.7 % of the scene**
    #        `[measured]`.
    #  Both stairs are **wall to wall**: width 3.00 = 2 × `wall.y_in` 1.50, and
    #  the walls run x 0…18.48 (`Lx = wall.x1 − pit.x0`), covering every rail
    #  span `[measured]`. So §15(1)2 is met by the "wall" and §15(3) prescribes
    #  a **handrail** - one pipe per side, no infill.
    #  **Post-mounted, not wall-bracketed**, for the same measured reason as
    #  scene02: `wall.parapet_top` = +0.15, so the 850 mm rail line runs 0.70 m
    #  above the wall top at the stair head and only meets the wall from
    #  x = 1.60 (step 5) — 36 % of this 4.48 m run would have had nothing to
    #  bracket to `[computed]`. Posts also make the statutory ≥300 mm end
    #  extensions buildable (§15(4)3).
    #  y = `wall.y_in` − 0.07 → pipe face 53 mm / post face 50 mm clear of the
    #  wall, both ≥ statutory 50 mm (§15(4)2) `[computed]`.
    stair_rail=dict(y=1.43, dia=0.034, height=0.85, post_r=0.020,
                    post_spacing=1.20, ext_top=0.30, ext_bot=0.30),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004, land_depth=0.4),
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.05, proud=0.001),

    # ═══ [W2-D ground_kit] P3 sidewalk_block - spec §5.2 scene16 row ══════════
    #  Row prescription: "edge weeds on both walk verges · 1 manhole · canopy
    #  drip staining band (eaves projection)"; manhole (-3.9, -0.8).
    #  ★ Tactile is **ON, newly installed** (§12.4, the only ON scene in this
    #    batch): 0.6 m x full width in front of the **building entrance**,
    #    i.e. deliberately at a spot with **no drop**. That is the point — this
    #    scene is what fills the cue+/label- quadrant (§12.6). Defect type
    #    applied: "obstruction/occupation" — ground_kit only leaves the space
    #    clear, the pot/bicycle that occupies it belongs to the props team.
    #  ★ Placed unconditionally, not under `cue_tactile`, following the
    #    sceneN5 pilot: a band that is unrelated to the drop cannot leak a
    #    hazard cue into a cue-OFF cut, so toggle integrity is not at stake.
    #    The scene's own stair-head / bollard tactile paths stay toggle-bound.
    #  ★ `gutter_L` is overridden to 0: an L gutter is a carriageway edge
    #    detail and this walk has grass on both sides, no roadway (§4.2).
    #  ★ The canopy eaves projection line (x = canopy.x0 = -1.0) is only 1.0 m
    #    in front of the drop; drow(-1.0, d10) = 5.65 rows @1080 against a
    #    16-row floor, so a continuous transverse drip band there is a GT-E2
    #    violation [computed]. The drip is therefore carried as **decals**
    #    (`stain` kind "drip") inside the trimmed region instead of a line.
    gkit=dict(
        region=(-12.0, -2.5, 0.0, 2.5),
        manholes=[(-3.9, -0.8)],
        gullies=[(-6.0, -2.2), (-1.5, 2.2)],
        patches=[(-1.20, 0.35), (-8.60, -0.30)],
        # entrance tactile band: 0.60 m deep, walk-corridor width
        tactile_entrance=(-6.00, -2.5, -5.40, 2.5),
        wear_lane=((-12.0, 0.0), (-0.85, 0.0)),   # desire line to the stairs
    ),

    # surrounding ground / dressing
    #   gx1 14.5 -> 19.0 : also clears the east exit stair footprint (x 14..18.48) from the grass.
    ground=dict(size=140.0, z_top=-0.03, gx0=-0.5, gx1=19.0, gy0=-1.85, gy1=1.85),
    planters=[dict(name="A", cx=-4.0, cy=4.0, base_z=0.0),
              dict(name="B", cx=8.0, cy=-4.5, base_z=0.0),
              dict(name="C", cx=12.0, cy=5.0, base_z=0.0),
              dict(name="D", cx=2.0, cy=6.5, base_z=0.0)],
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    buildings=dict(
        # blocks the distant vista (+X horizon): facade -X plane
        C=dict(x0=26.0, x1=32.0, y0=-12.0, y1=12.0, h=12.0, floors=4,
               axis="x", facade_x=26.0, face_dir=-1.0),
        # the -X horizon is closed too (only one side used to be blocked, leaving the other empty)
        D=dict(x0=-30.0, x1=-24.0, y0=-14.0, y1=14.0, h=15.0, floors=5,
               axis="x", facade_x=-24.0, face_dir=1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # --- context dressing (cue_scene_dressing) : "a downtown plaza with an underpass entrance" ---
    # entrance sign gate (portal-type sign) - spans the top of the opening
    # [v5.1 realism, critical] Feedback: "the blue sign panel floats in mid-air - why up there?"
    #   Cause: the old Gate/Beam was a box of size (2.4, 0.15, 0.45) at (x −1.2, **y 0**, z 2.55).
    #   That is, **a 2.4 m slab lying along X** hung above the middle of the opening,
    #   and with the columns at y +-2.0 the slab never physically touched them ->
    #   a floating blue panel with no structural support.
    #   Fix: the beam becomes **a real lintel joining the columns**. It spans 4.12 m in Y
    #   (= 2·(y_half + post/2), out to both column faces), is 0.22 thick in X, and its top
    #   (z 2.60) is flush with the column heads -> the portal closes.
    #   The lintel itself is the sign band mounted at the opening head (gate material = navy),
    #   so no separate floating panel. Korean wayfinding is consolidated into the one N-4
    #   sign_exit (side post-mounted, −1.6, 2.6) - no duplicate signage.
    gate=dict(x=-1.2, y_half=2.0, post=0.12, post_h=2.6,
              beam_t=0.22, beam_h=0.40, beam_top=2.60),
    # [v5.1 §2] bollards brought to code - old: 6 posts at 2.5 m x spacing on both trench sides (y +-3.2)
    #   (a **decorative row** lining the opening; unrelated to any vehicle entry, spacing off code).
    #   New: **one row at the sidewalk entry** (x 20.5) beyond the east exit stair head (x 18.48),
    #   6 posts at 1.5 m spacing with a 1.5 m central gap (wheelchair passage). Dot tactile paving
    #   runs 0.3 m across the pedestrian approach face (west, x 20.2..20.5).
    #   Camera: 21~30 m away in every preset (eye x <= −0.5, looking +X) -
    #   zero near occlusion, unrelated to the judging subject (stairs·canopy shadow, x 0..4.6).
    bollards=dict(x=20.5, ys=(-3.75, -2.25, -0.75, 0.75, 2.25, 3.75),
                  block=dict(x0=20.2, x1=20.5, y0=-4.05, y1=4.05)),
    benches=[(-5.0, 5.5, 180.0), (-5.0, -5.5, 0.0), (9.0, 5.0, 180.0)],
    streetlights=[(-3.0, 6.5), (9.0, -6.5)],
    streetlight=dict(pole_h=5.0, pole_r=0.07, arm_len=0.9, arm_r=0.04,
                     head=0.24),
    hedges=[(-12.0, 6.5, -9.0, 7.3), (14.0, -7.3, 18.0, -6.5)],
    # 2 sidewalk paving bands (indicate the plaza scale)
    walk_bands=dict(ys=(-6.0, 6.0), width=0.45, z=0.007),
    # [v5 shared layer] Korean signs - (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   Exit(−1.6, 2.6): the underpass entrance exit sign. From the trench opening (y +-1.5) it is
    #     1.10 m, from the retaining wall face (y +-1.8) 0.80 m - meets the >=0.5 m hazard clearance.
    #     0.57 m from the sign gate column (x −1.2, y +-2.0, r 0.12); from the bollard
    #     (−1.0, 3.2) 0.92 m; outside the canopy (x −1.0..4.6) on the west.
    #   Camera check (grid gy=0, eye x −2/−5/−10, FOV +-30 deg):
    #     −2 -> outside at 81.3 deg (2.63 m to the side) · −5 -> outside at 37.4 deg · −10 -> 17.2 deg (8.81 m)
    #     approach(−7,0) 25.7 deg (frame edge) · shadow_band(−5,0) outside at 37.4 deg ·
    #     under_canopy(−0.5,0) behind · beauty_overview(−7,−5) 23.6 deg at the edge
    #     -> none of them hides the judging subject (stairs·shadow) at frame centre.
    signs=[("Exit", "sign_exit", -1.6, 2.6, 0.0, 180.0, 0.9, 0.45)],

    material=dict(
        scale=dict(plaza_lower=0.7, plaza_light=1.80, grass=1.4,
                   brick_red=2.0, tactile=0.3),
        grass_tint=(0.55, 0.68, 0.42),
        roof_color=(0.72, 0.72, 0.74), roof_rough=0.55,     # light grey roof
        post_color=(0.55, 0.55, 0.58), post_metallic=0.5, post_rough=0.5,
        wall_tint=(0.85, 0.85, 0.86),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] parapet 0.90 -> 0.72 (no large pure-white areas)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # dark constant colours for dressing (albedo 0.02~0.06 convention)
        band_color=(0.05, 0.05, 0.055), band_rough=0.7,
        gate_color=(0.03, 0.05, 0.09), gate_rough=0.45,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
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
    # ─── SUN_AZ_OFFSET: the key parameter behind this scene's signature (the canopy
    #     shadow covering the stairs). Supervisor r1 C-16: 171.5->146.5. Sun mapping world az ~
    #     33.5+offset = 180 -> shadow az = az−180 = 0 -> the roof (z=2.6, noon elevation
    #     elev~49.79 deg) casts its shadow toward +X (the stair descent direction), covering the pit
    #     opening and the whole stair. Shadow-stair alignment is re-judged by the supervisor on renders.
    #     The [ ] keys (dome_rotation_step 15 deg) allow a further sweep in the GUI. ───
    SUN_AZ_OFFSET=146.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene16")

ASSET_ROLES = ["plaza_lower", "plaza_light", "grass", "tactile",
               "brick_red", "sign_exit", "hdri", "mdl"]   # [v5] sign_exit


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene cuts."""
    views = sc.grid_views(0.0)
    # approach: from the bright sidewalk toward stairs·canopy (impression of the upper shadow band)
    views["approach"] = dict(eye=[-7.0, 0.0, 1.6], tgt=[3.0, 0.0, -0.6])
    # shadow_band: low viewpoint - only the stairs read as a dark band on the bright sidewalk
    views["shadow_band"] = dict(eye=[-5.0, 0.0, 0.35], tgt=[4.0, 0.0, -0.4])
    # under_canopy: from above the stairs, looking down into the canopy shadow and lower passage
    views["under_canopy"] = dict(eye=[-0.5, 0.0, 1.7], tgt=[4.5, 0.0, -1.6])
    # beauty_overview: oblique high-angle impression
    views["beauty_overview"] = dict(eye=[-7.0, -5.0, 3.2], tgt=[3.0, 1.0, -1.0])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / beauty  — 밝은 보도·하강 계단·캐노피(지붕+기둥4) 식별
 2. shadow_band·h0.3   — 계단 전체가 캐노피 그림자로 어두운 밴드가 되는가(특색)
 3. under_canopy       — 암부 속 황색 노징이 저대비로 잔존하는가
 4. cue ON vs OFF      — nosing/railing/tactile 토글 시 기하 트랜스폼 불변
 5. 재질·태양방위      — [ ]키로 그림자가 계단을 덮는 방위 확인·Z파이팅 없는가
 6. [v4] 동측 출구 계단(x14→18.48 상승)·둘레난간 파라펫 접지·사인 게이트
 7. [v5] 공통 레이어 — 점자띠(상단·하부) + sign_exit(진입부 y +2.6) 판독"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene16")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene16"

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
        M["walk"] = PBR(
            f"{ROOT}/Looks/Walk", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"])
        M["stair"] = PBR(
            f"{ROOT}/Looks/Stair", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["wall_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["roof"] = PBR(f"{ROOT}/Looks/Roof", diffuse_color=mp["roof_color"],
                        roughness_const=mp["roof_rough"], metallic=0.0)
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [v5.1 §2/§4] materials for the code-compliant bollards - 3 body variants (tint jitter +-5%) + reflective band.
        #   The band is small in area, so high luminance is allowed (the no-large-pure-white rule does not apply).
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"bollard_{_i}"] = PBR(
                f"{ROOT}/Looks/Bollard_{_i}",
                diffuse_color=tuple(min(c * _f, 1.0) for c in mp["rail_color"]),
                metallic=mp["rail_metallic"],
                roughness_const=mp["rail_rough"] * (1.0 + 0.05 * (_i - 1)))
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=(0.86, 0.86, 0.84),
                                roughness_const=0.35)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/Band", diffuse_color=mp["band_color"],
                        roughness_const=mp["band_rough"])
        M["gate"] = PBR(f"{ROOT}/Looks/Gate", diffuse_color=mp["gate_color"],
                        roughness_const=mp["gate_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # ground - grass base (4 boxes cut around the pit footprint) : never covers the cavity
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        cz = g["z_top"] - 0.25
        th = 0.5
        H = g["size"] / 2.0
        gx0, gx1 = g["gx0"], g["gx1"]
        gy0, gy1 = g["gy0"], g["gy1"]
        BOX(f"{ROOT}/Grass_W", ((-H + gx0) / 2.0, 0.0, cz),
            (gx0 + H, g["size"], th), M["grass"])
        BOX(f"{ROOT}/Grass_E", ((gx1 + H) / 2.0, 0.0, cz),
            (H - gx1, g["size"], th), M["grass"])
        BOX(f"{ROOT}/Grass_S", ((gx0 + gx1) / 2.0, (-H + gy0) / 2.0, cz),
            (gx1 - gx0, gy0 + H, th), M["grass"])
        BOX(f"{ROOT}/Grass_N", ((gx0 + gx1) / 2.0, (gy1 + H) / 2.0, cz),
            (gx1 - gx0, H - gy1, th), M["grass"])

    # -------------------------------------------------------------------
    # ground-level sidewalk - around the trench (x 0..14, outer wall faces +-1.8): west + south·north flanks
    # -------------------------------------------------------------------
    def build_walk(M):
        w = PARAMS["walk"]
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        top, th = w["z_top"], w["thick"]
        cz = top - th / 2.0
        y_out = p["y1"] + wl["thick"]            # 1.8
        x_tr1 = wl["x1"]                          # trench east end 18.48
        # [W2-0 · P-A] Walk_W is the ground_kit stage — register the skin
        #   exclusion **before** BOX (add_box calls `_skin_wanted` inline).
        sc.skin_exclude(f"{ROOT}/Walk_W")
        # west: x_w..0, full width
        BOX(f"{ROOT}/Walk_W",
            ((w["x_w"] + p["x0"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (p["x0"] - w["x_w"], w["y_n"] - w["y_s"], th), M["walk"], col=True)
        # south: trench x span, y_s..-y_out
        BOX(f"{ROOT}/Walk_S",
            ((p["x0"] + x_tr1) / 2.0, (w["y_s"] - y_out) / 2.0, cz),
            (x_tr1 - p["x0"], (-y_out) - w["y_s"], th), M["walk"], col=True)
        # north: trench x span, +y_out..y_n
        BOX(f"{ROOT}/Walk_N",
            ((p["x0"] + x_tr1) / 2.0, (y_out + w["y_n"]) / 2.0, cz),
            (x_tr1 - p["x0"], w["y_n"] - y_out, th), M["walk"], col=True)
        # east: trench end (x18.48 = east stair head)..x_e, full width
        BOX(f"{ROOT}/Walk_E",
            ((x_tr1 + w["x_e"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (w["x_e"] - x_tr1, w["y_n"] - w["y_s"], th), M["walk"], col=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P3 sidewalk_block (spec §5.2 scene16 row)
    #   Drop edge = pit head x=0 (PARAMS["pit"]["x0"], §7.4). The pit itself is
    #   declared as a **void** so gate B8 (GT-V) refuses any element that would
    #   lay a ground plane over the opening (§6.3).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        p = PARAMS["pit"]
        gp = gk.plan_ground(
            "sidewalk_block", region=tuple(g["region"]),
            z=float(PARAMS["walk"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(p["x0"]))],
            voids=((p["x0"], p["y0"], p["x1"], p["y1"]),),
            dists=(2, 5, 10), scene="scene16",
            tactile=("entrance",),
            overrides=dict(
                infra=dict(manhole=1, gully=2, gutter_L=0),
                # "drip" added to the stain kinds = canopy eaves run-off.
                surface=(("patch", 2), ("crack", 4),
                         ("stain", ("dirt", "gum", "drip")), ("weed", 8)),
                extras=(("wear_lane", dict(width=0.90)),)),
            extras_args=dict(wear_lane=dict(centerline=tuple(g["wear_lane"]))),
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[tuple(v) for v in g["gullies"]],
                       patch=[tuple(v) for v in g["patches"]],
                       tactile=dict(entrance=tuple(g["tactile_entrance"]))),
            seed=16)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["band"], crack=M["band"], patch=M["walk"],
                  patch_cut=M["band"], manhole=M["band"], gully=M["band"],
                  gutter=M["band"], gutter_cover=M["band"],
                  trench=M["band"], trench_frame=M["band"],
                  marking=M["band"], weed=M["grass"], wear=M["wall"],
                  stain_dirt=M["wall"], stain_gum=M["band"],
                  stain_drip=M["wall"], tactile=M["tactile"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene16 P3 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_flat_fill(M):
        """hazard_stairs=False control: the trench is filled, everything flat at z=0."""
        sc.skin_exclude(f"{ROOT}/FlatWalk")      # [W2-0 · P-A] the twin gets the same conditions
        w = PARAMS["walk"]
        BOX(f"{ROOT}/FlatWalk",
            ((w["x_w"] + w["x_e"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0,
             w["z_top"] - w["thick"] / 2.0),
            (w["x_e"] - w["x_w"], w["y_n"] - w["y_s"], w["thick"]),
            M["walk"], col=True)

    # -------------------------------------------------------------------
    # walls + stairs + lower passage
    # -------------------------------------------------------------------
    def build_walls(M):
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        y_out = wl["y_in"] + wl["thick"]          # 1.8
        y_ctr = (wl["y_in"] + y_out) / 2.0
        top = wl["parapet_top"]
        bot = wl["base_z"]
        cz = (top + bot) / 2.0
        hz = top - bot
        Lx = wl["x1"] - p["x0"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Wall_{tag}",
                ((p["x0"] + wl["x1"]) / 2.0, sgn * y_ctr, cz),
                (Lx, wl["thick"], hz), M["wall"], col=True)
        # (audit v4 A1) east blocking wall Wall_E removed - the east exit stair stands there instead.

    def build_stairs(stair_mtl, passage_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        # lower passage
        pa = PARAMS["passage"]
        st = PARAMS["stairs"]
        BOX(f"{ROOT}/Passage",
            ((pa["x0"] + pa["x1"]) / 2.0, 0.0,
             (pa["z_top"] + pa["base_z"]) / 2.0),
            (pa["x1"] - pa["x0"], st["y1"] - st["y0"],
             pa["z_top"] - pa["base_z"]), passage_mtl, col=True)

    def build_east_exit(M, stair_mtl):
        """East exit stair (ascending) — the descending stair mirrored by a rot_group 180°.
        Local x0(z=0)=14.0 → world 18.48 (sidewalk top), local end (z=-2.1) → world
        14.0, flush with the passage top. Nosing·tactile·railing mirror inside the same group."""
        es = PARAMS["east_stairs"]
        run = es["tread"] * es["nsteps"]
        px = es["x0"] + run / 2.0                      # 16.24
        grp = sc.build_rot_group(stage, f"{ROOT}/EastExit", (px, 0.0), 180.0)
        sc.build_straight_stairs(
            stage, f"{grp}/Stairs", es["x0"], es["y0"], es["y1"],
            es["riser"], es["tread"], es["nsteps"], es["base_z"], stair_mtl,
            z_top=es["z_top"], collider=True)
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{grp}/Nosing", es["x0"], es["y0"], es["y1"],
                es["riser"], es["tread"], es["nsteps"], color=ns["color"],
                width=ns["width"], proud=ns["proud"], z_top=es["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{grp}/Tactile_East",
                             es["x0"] - tc["ahead"], es["x0"],
                             es["y0"], es["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
        # [realism v1] East exit stair: guardrail -> handrail (§15(3)), same
        #   rationale as the west stair (PARAMS.stair_rail). Built in the
        #   rot_group's **local** frame; the 180° flip preserves |y|, so the
        #   wall inner faces are at local y = ±1.50 exactly as in world.
        if cfg["cue_railing"]:
            er = PARAMS["east_rail"]
            sr = PARAMS["stair_rail"]

            def east_ground(x):
                if x <= es["x0"] + 1e-9:
                    return 0.0
                i = int((x - es["x0"]) / es["tread"]) + 1
                return -es["riser"] * min(max(i, 1), es["nsteps"])

            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                res = sk.build_handrail(
                    stage, f"{grp}/EastRail_{tag}", sgn * er["y"],
                    es["x0"], run, es["riser"] * es["nsteps"],
                    M["rail"], sc.add_cylinder, z_top=es["z_top"],
                    height=sr["height"], dia=sr["dia"],
                    ext_top=sr["ext_top"], ext_bot=sr["ext_bot"],
                    post_r=sr["post_r"], post_spacing=sr["post_spacing"],
                    ground_fn=east_ground, strict=False)
                for w in res["warnings"]:
                    print(f"[cue_railing] 규정 미달(동측) — {w}")

    # -------------------------------------------------------------------
    # canopy (solid roof + 4 columns) - covers the whole stair + 1m past the head
    # -------------------------------------------------------------------
    def build_canopy(M):
        cp = PARAMS["canopy"]
        sc.build_canopy(stage, f"{ROOT}/Canopy", cp["x0"], cp["x1"],
                        cp["y0"], cp["y1"], cp["z_roof"], cp["post_r"],
                        M["roof"], M["post"], roof_t=cp["roof_t"],
                        base_z=cp["base_z"])

    # -------------------------------------------------------------------
    # cues - nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_signs():
        """[v5 shared layer] Korean sign (sc.build_sign). The exit sign at the underpass entrance =
        a cue for inferring a drop from adjacent infrastructure (series (1)). Coordinate checks are in the PARAMS['signs'] comment."""
        back = sc.make_pbr(stage, f"{ROOT}/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"{ROOT}/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_cues(M, stair_mtl):
        st = PARAMS["stairs"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            pa = PARAMS["passage"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
            sc.build_tactile(stage, f"{ROOT}/Tactile_Land",
                             pa["x0"], pa["x0"] + tc["land_depth"],
                             st["y0"], st["y1"], M["tactile"],
                             z=pa["z_top"], proud=tc["proud"])
        if cfg["cue_railing"]:
            sr = PARAMS["stair_rail"]

            def stair_ground(x):
                if x <= 1e-9:
                    return 0.0
                return -st["riser"] * min(max(int(x / st["tread"]) + 1, 1),
                                          st["nsteps"])

            run = st["tread"] * st["nsteps"]
            drop = st["riser"] * st["nsteps"]
            n_hr = 0
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                res = sk.build_handrail(
                    stage, f"{ROOT}/StairRail_{tag}", sgn * sr["y"],
                    st["x0"], run, drop, M["rail"], sc.add_cylinder,
                    z_top=st["z_top"], height=sr["height"], dia=sr["dia"],
                    ext_top=sr["ext_top"], ext_bot=sr["ext_bot"],
                    post_r=sr["post_r"], post_spacing=sr["post_spacing"],
                    ground_fn=stair_ground, strict=False)
                for w in res["warnings"]:
                    print(f"[cue_railing] 규정 미달 — {w}")
                n_hr += len(res["prims"])
            print(f"[cue_railing] 계단 손잡이 2선 (φ{sr['dia'] * 1000:.0f} · "
                  f"h{sr['height'] * 1000:.0f}) · 프림 {n_hr} — 방호는 좌우 "
                  f"옹벽 + 피트 둘레 난간")
            # ground-level guardrail around the pit (south·north edges, over the stair width)
            pr = PARAMS["perim_rail"]
            base_z = pr["parapet_top"]
            top_z = base_z + pr["rail_h"]
            mid_z = base_z + pr["mid_h"]

            def hrail(prefix, const_c, a0, a1):
                mid_c = (a0 + a1) / 2.0
                length = a1 - a0
                CYL(f"{prefix}/Top", (mid_c, const_c, top_z),
                    pr["rail_r"], length, M["rail"], rotY=90.0)
                CYL(f"{prefix}/Mid", (mid_c, const_c, mid_z),
                    pr["rail_mid_r"], length, M["rail"], rotY=90.0)
                ph = top_z - base_z
                n = 0
                a = a0 + pr["spacing"] / 2.0
                while a <= a1 - pr["spacing"] / 2.0 + 1e-6:
                    CYL(f"{prefix}/Post_{n}", (a, const_c, base_z + ph / 2.0),
                        pr["post_r"], ph, M["rail"])
                    a += pr["spacing"]
                    n += 1

            hrail(f"{ROOT}/PerimRail_S", -pr["y"], pr["x0"], pr["x1"])
            hrail(f"{ROOT}/PerimRail_N", pr["y"], pr["x0"], pr["x1"])

    # -------------------------------------------------------------------
    # dressing - 2 planters + distant buildings
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[v5.1 §2] One code-compliant bollard — height 0.90 m · diameter 0.15 m (r 0.075) +
        a white reflective band on top (0.09 wide). Basis: Enforcement Rule of the Act on
        Promotion of Mobility Convenience for the Mobility Impaired, Table 2 (height 0.8~1.0 ·
        diameter 0.1~0.2 · spacing around 1.5 m · a bright reflective band).
        The old sc.build_bollard defaults (r 0.06 · h 0.75) fall short of the statutory floor,
        so the dimensions are stated here (scene_common unmodified). The body material takes a
        per-instance tint jitter (bollard_0..2) to remove the 'identical copies' impression."""
        h, r = 0.90, 0.075
        sc.build_bollard(stage, f"{prefix}/Post", cx, cy, bz,
                         mtl=M[f"bollard_{k % 3}"], radius=r, height=h)
        sc.add_cylinder(stage, f"{prefix}/Band", (cx, cy, bz + h - 0.14),
                        r * 1.05, 0.09, M["bollard_band"])

    def build_dressing(M):
        pl = PARAMS["planter"]
        for pdef in PARAMS["planters"]:
            sc.build_planter(
                stage, f"{ROOT}/Planter_{pdef['name']}", pdef["cx"], pdef["cy"],
                pdef["base_z"], M["curb"], M["grass"],
                tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"], grass_h=pl["grass_h"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # entrance sign gate - a portal sign spanning the opening head ("underpass entrance")
        # [v5.1] The beam becomes a lintel that really joins the columns (floating panel removed).
        ga = PARAMS["gate"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Gate/Post_{tag}",
                (ga["x"], sgn * ga["y_half"], ga["post_h"] / 2.0),
                (ga["post"], ga["post"], ga["post_h"]), M["gate"], col=True)
        span = 2.0 * (ga["y_half"] + ga["post"] / 2.0)     # 4.12 (outer column faces)
        BOX(f"{ROOT}/Gate/Beam",
            (ga["x"], 0.0, ga["beam_top"] - ga["beam_h"] / 2.0),
            (ga["beam_t"], span, ga["beam_h"]), M["gate"], col=True)
        # [v5.1 §2] one row of code-compliant bollards (east sidewalk entry) + 0.3 m dot tactile paving
        bl = PARAMS["bollards"]
        for i, by in enumerate(bl["ys"]):
            build_bollard_std(M, f"{ROOT}/Bollard_{i}", bl["x"], by, 0.0, k=i)
        # Dot tactile paving belongs to the 'tactile paving' cue family, so it is bound to cue_tactile
        #   (so no yellow warning strip survives outside the toggle in an OFF cut - toggle integrity).
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=0.0,
                             proud=PARAMS["tactile"]["proud"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["post"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly, sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["post"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                           0.8, base_z=0.0)
        # 2 sidewalk paving bands (indicate the plaza scale) - outside the trench at y=+-6
        w = PARAMS["walk"]
        wb = PARAMS["walk_bands"]
        for i, by in enumerate(wb["ys"]):
            BOX(f"{ROOT}/WalkBand_{i}",
                ((w["x_w"] + w["x_e"]) / 2.0, by, wb["z"] - 0.01),
                (w["x_e"] - w["x_w"], wb["width"], 0.02), M["band"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["stair"] if cfg["cue_material_break"] else M["walk"]
    # passage material: the bright sidewalk material (plaza_lower) keeps the lower tone
    passage_mtl = M["walk"]

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_walk(M)
        build_walls(M)
        build_stairs(stair_mtl, passage_mtl)
        build_east_exit(M, stair_mtl)
        build_canopy(M)
        build_cues(M, stair_mtl)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)             # [W2-D] ground elements - after the dressing (scatter order convention)
    if cfg.get("cue_sign"):
        build_signs()               # [v5 shared layer]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene16 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene16_{ts}.png")
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
