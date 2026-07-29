# -*- coding: utf-8 -*-
"""
sceneD4_subway_platform.py — NegObs synthetic scene 31: D4 subway platform edge
(Isaac Sim 4.5) — **the library's first fully indoor scene**

Type    : D4 non-stair drop (platform edge → track bed, drop 1.15 m)
Spec    : Docs/nanobanana_batch1_geometry_map.md §C sceneD4_subway_platform
Look ref: look_refs/d4_subway_platform.jpg
Shared  : scene_common.py (check API) · scene16_canopy_shadow.py (standard skeleton)
          · scene02_underpass.py (semi-indoor concrete) · scene06_spiral_towerstone.py
            (origin of the indoor-shadow lesson — see [Lighting convention] below)

Hazard   : the platform walking surface (z=0) breaks off over the track trough with no
           guard at all. Below the 1.15 m edge face is dark ballast, so **from a low
           (grazing) viewpoint the track trough is concealed entirely** and the platform
           reads as one floor running through to the far side. The only cues are the two
           rows of yellow tactile paving 0.3 m inside the edge, plus the edge line.
GT       : the track area (y −2.0..+2.0) is positive with a 1.15 m drop. The whole platform top = no drop.
           Basis = platform falls (scenario survey v1, national statistics).

──────────────────────────────────────────────────────────────────────────
[Lighting convention — the hardest problem in this scene. Read it.]
  This scene is a **fully sealed shell with no window or opening at all** (platform slab
  + ballast floor, 2 side walls, ceiling, 2 end walls, and the tunnel bore capped at the
  back). DomeLight / HDRI contribution is therefore **structurally 0**, and the only
  light in the scene is the 30 emissive ceiling panels.

  * **A single RT (RaytracedLighting) bounce barely picks up emissive contribution.**
    Use the RT render only to check form and layout; **brightness and shadow must always
    be judged in PathTracing with 8 bounces (PARAMS["render"]["pt_max_bounces"]=8)**.
    (scene06 lesson 7 — indoor shadow is judged under PT only)

  * Brightness tuning is the single knob PARAMS["panel"]["intensity"]. Start value 1500.
    A supervisor sweep is recommended (no file edit needed):
      NEGOBS_PARAMS_OVERRIDE='{"panel":{"intensity":400}}'  python sceneD4_...py
      ... compare 400 / 800 / 1500 / 3000 under PT.
    scene06 audit B-06-2 said "150~300 is enough for indoor legibility", but that was the
    value for a **semi-outdoor scene where the noon sun dominated the exposure**. This
    scene has no direct or sky light at all, so an order of magnitude more is expected to
    reach the same displayed brightness, hence the start at 1500 (the panels are
    luminaires themselves, so mild white clipping is acceptable).

  * Relative darkness of the track bed (design basis): the panel rows sit only above the
    platforms (y=±5.0) and **not one** is placed above the track (|y|<2). The distance to
    the panel directly above the platform walking surface is 3.35 m, while the nearest
    distance to the track surface is 6.7 m at an incidence of 48° →
    direct illuminance ratio ≈ (0.669²/45.3)/(1/11.2) ≈ 0.26. Add albedo, ballast 0.05 vs
    concrete 0.35, a factor of 7 → the displayed luminance of the track bed is a few % of
    the platform. But it is **not 0**: indirect bounce off the white tile walls and ceiling
    flows into the track trough, so under PT the sleepers and rail heads should be barely
    readable. (If it is fully black, do not raise intensity - suspect the wall albedo / bounces)
──────────────────────────────────────────────────────────────────────────

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD4_subway_platform.py

Auto capture (headless):   NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt python sceneD4_...py
      * indoor emissive-only lighting converges slowly under PT. If noise remains,
        raise NEGOBS_WARMUP=900 (+ pt_total_spp 768).
Smoke early exit:       NEGOBS_SMOKE=1  python sceneD4_subway_platform.py

Coordinates: Z-up, m. **Platform run axis = +X** (the camera travel axis), platform walking surface z=0.
        The drop starts at the edge line **y=−2.0** (near side) / **y=+2.0** (far side, symmetric).
        x=0 is the station centre datum (it is the run axis, so no hazard geometry sits at the x origin).
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. The hazard_stairs key is kept by convention instead of hazard_track
#     (the one geometry-toggle exception: False -> fill the track trough to z=0, making it flat).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> track trough filled (all z=0 flat, drop 0)
    "cue_railing":        True,   # barrier railing at the platform end (tunnel side) - the edge itself stays unguarded [fixed]
    "cue_tactile":        True,   # 2 rows of yellow tactile paving x both platforms (0.3m back from the edge)
    "cue_material_break": True,   # dark soiled fascia on the platform edge face (bright 6cm coping remains)
    "cue_nosing":         True,   # yellow platform edge line (walking surface, proud 0.002)
    "cue_sign":           False,  # [reserved] not implemented - config key only
    "cue_scene_dressing": True,   # benches·wall doors·skirting / cornice bands together
}


# ===========================================================================
# [B] PARAMS - dimension table. Mergeable via NEGOBS_PARAMS_OVERRIDE.
# ===========================================================================
PARAMS = dict(
    seed=31,                                  # fixed seed for sleeper jitter (reproducibility)

    # ── hall shell ─────────────────────────────────────────────────────
    #  x: platform run 62 m (−16..46), tunnel bore beyond it 46..56
    #  y: near platform −8..−2 / track trough −2..+2 / far platform +2..+8
    hall=dict(x0=-16.0, x1=46.0,
              plat_out=8.0,                   # outer end of the platform (wall front face)
              edge=2.0,                       # platform edge line |y| (the edge where the drop starts)
              z_walk=0.0,                     # platform walking surface
              z_base=-1.60,                   # slab underside (not visible)
              wall_in=7.98, wall_out=8.40,    # side walls (0.02 is the slab embedment)
              wall_top=3.70,
              ceil_z0=3.40, ceil_z1=3.72,
              end_t=0.42),                    # end wall thickness

    # ── track bed ─────────────────────────────────────────────────────
    #  ballast top z=−1.15 -> **the reference plane for the 1.15 m GT drop**
    track=dict(x0=-16.0, x1=55.5,
               half_w=2.05,                   # embedded 0.05 into the slab (avoids coplanarity)
               # ballast_bot drops 2 cm below the slab underside (−1.60) -
               # it is the shell's lowest face (not visible) but leaves no coplanarity at all (§8).
               ballast_top=-1.15, ballast_bot=-1.62,
               gauge=1.435,                   # standard gauge - rail centres y=+-0.7175
               sleeper_step=0.65, sleeper_len=2.60,
               sleeper_w=0.24, sleeper_h=0.16, sleeper_top=-1.06,
               jitter_x=0.03, jitter_y=0.03, jitter_z=0.012,
               rail_w=0.070, rail_h=0.15,     # rail web (rises from the sleeper top)
               head_w=0.075, head_z0=-0.925, head_z1=-0.900),

    # ── tunnel portal · bore (far closure, dark vanishing point) ────────
    portal=dict(half_w=2.40, top_z=1.58),     # end wall opening
    bore=dict(x0=46.30, x1=56.00, half_in=2.38, half_out=2.82,
              z0=-1.92, z1=1.92, cap_t=0.40),

    # ── ceiling emissive panels (the scene's only light) ────────────────
    #   2 rows above the platform centres (y=+-5.0), 4.0 m pitch, 15 per row = 30 total
    panel=dict(rows=(-5.0, 5.0), x0=-14.0, step=4.0, n=15,
               size_x=1.60, size_y=0.55, z0=3.32, z1=3.41,
               color=(0.90, 0.90, 0.86), rough=0.35,
               emis=(1.0, 1.0, 0.95), intensity=12000.0),  # r1: 1500 left the platform pitch dark -> raised 8x

    # ── cue ──────────────────────────────────────────────────────────
    #  tactile paving: 0.30 back from the edge -> row 1 |y| 2.30..2.60, row 2 2.62..2.92
    tactile=dict(offset=0.30, width=0.30, gap=0.02, proud=0.004),
    #  yellow platform edge line: 0.02..0.14 inside the edge line
    nosing=dict(color=(0.85, 0.72, 0.10), inset=0.02, width=0.12, proud=0.002),
    #  soiled fascia on the platform edge face (the top 6 cm remains bright coping)
    facade=dict(y_in=2.06, y_out=1.99, z0=-1.25, z1=-0.06),
    #  barrier railing at the platform end (tunnel side) - the hazard is that the edge has no railing [fixed]
    endrail=dict(x=45.40, rail_r=0.030, post_r=0.040,
                 top_h=1.05, mid_h=0.55, nposts=5),
    #  walking-surface joints (transverse, 3 m pitch)
    joint=dict(step=3.0, width=0.03, proud=0.001),

    # ── dressing ──────────────────────────────────────────────────────
    bench=dict(ys=(-7.40, 7.40), xs_near=(-2.0, 10.0, 22.0, 34.0),
               xs_far=(4.0, 16.0, 28.0),
               length=1.80, width=0.40, height=0.45),
    door=dict(xs=(-8.0, 6.0, 20.0, 34.0), w=1.00, t=0.05, h=2.10),
    trim=dict(skirt_z0=-0.005, skirt_z1=0.22,
              cornice_z0=3.08, cornice_z1=3.41, proud=0.02),

    # ── signage context v2 (2026-07-27, less barren - **modest**) ──────────
    #   * invariant: platform edge (|y|=2.0)·track·ballast·tactile paving·edge line·ceiling panels
    #     ·lighting parameters. Every new element goes only on the **side wall faces (|y| >= 7.958)**
    #     or **ceiling hangers (z >= 2.44)** -> zero change to walking surface, edge and track geometry.
    #   * illumination balance: the ad lightbox emission is 1/5 of the ceiling panels (12000) = 2400,
    #     within the cap (1/4=3000). With only 2 of them (area 2.86 m²) their effect on the
    #     platform / track illumination ratio is under a few % of the 30 panels (the track stays relatively dark).
    signage=dict(
        # line colour band - runs along both side walls. Placed above the doors (h 2.10)·station
        # name panels (<=2.05)·lightboxes (<=2.15) and below the cornice (3.08).
        band=dict(z0=2.30, z1=2.55, proud=0.022, embed=0.005),
        # station name panels (textless colour-field plates) - near wall x{-4,10,30} / far wall x{2,26}
        #   their x ranges do not overlap the doors x{-8,6,20,34} or the lightboxes x{16,12}.
        nameplates=[dict(x=-4.0, sgn=-1.0), dict(x=10.0, sgn=-1.0),
                    dict(x=30.0, sgn=-1.0), dict(x=2.0, sgn=1.0),
                    dict(x=26.0, sgn=1.0)],
        nameplate=dict(w=1.60, h=0.50, z_c=1.80, proud=0.030, embed=0.005,
                       bar_h=0.14, bar_w=1.10, bar_proud=0.012),
        # 2 ad lightboxes (weak emission)
        lightboxes=[dict(x=16.0, sgn=-1.0), dict(x=12.0, sgn=1.0)],
        #   face_proud > frame_proud is required so the emissive face is not buried in the frame slab
        #   (the frame is a solid box - it spans w+2·frame, so it reads as a border).
        lightbox=dict(w=2.20, h=1.30, z_c=1.50, frame=0.09,
                      face_proud=0.095, frame_proud=0.075, embed=0.005,
                      emis=(1.0, 0.96, 0.88), intensity=2400.0),
        # 4 ceiling-hung station signs - |y|=2.6 inside the edge, 0.59 m above the highest
        #   camera (z 1.85). Panel bottom 2.44 / top 3.05, hanger rod -> ceiling 3.40.
        hangers=[dict(x=0.0, sgn=-1.0), dict(x=24.0, sgn=-1.0),
                 dict(x=12.0, sgn=1.0), dict(x=36.0, sgn=1.0)],
        hanger=dict(y=2.60, w=2.20, t=0.07, z0=2.44, z1=3.05,
                    rod_r=0.022, rod_dx=0.80, ceil_z=3.42,
                    bar_h=0.16, bar_w=1.50, bar_proud=0.010),
    ),

    material=dict(
        scale=dict(concrete_floor=1.5, concrete_wall=2.0, plaster=1.2,
                   gravel=0.5, wood_dark=0.5, tactile=0.3),
        # ─ sRGB gamma convention (§A-1): "dark colours" live in 0.02~0.06.
        #   texture tints multiply, so (source albedo x tint) must land in that band.
        ballast_tint=(0.155, 0.150, 0.145),   # gravel (~0.35) x -> ~0.052 [darkened]
        sleeper_tint=(0.30, 0.28, 0.26),      # wood_dark(≈0.18) × → ≈0.052
        facade_tint=(0.14, 0.14, 0.15),       # concrete_wall(≈0.45) × → ≈0.063
        wall_tint=(0.90, 0.90, 0.88),         # white tile wall (bright - carries the indirect light)
        rail_color=(0.045, 0.042, 0.038), rail_metallic=0.55, rail_rough=0.75,
        head_color=(0.42, 0.42, 0.44), head_metallic=0.85, head_rough=0.14,
        ceil_color=(0.20, 0.20, 0.21), ceil_rough=0.85,
        trim_color=(0.055, 0.055, 0.060), trim_rough=0.70,
        tunnel_color=(0.022, 0.022, 0.026), tunnel_rough=0.95,
        joint_color=(0.045, 0.045, 0.048), joint_rough=0.90,
        door_color=(0.28, 0.30, 0.32), door_metallic=0.35, door_rough=0.45,
        bench_color=(0.22, 0.23, 0.25), bench_metallic=0.25, bench_rough=0.50,
        fence_color=(0.45, 0.46, 0.48), fence_metallic=0.70, fence_rough=0.35,
        # ── signage v2 ── (mid to high saturation for the dim interior. The dark band is unused)
        line_band=(0.72, 0.30, 0.06), line_band_rough=0.55,   # line colour (orange)
        sign_field=(0.06, 0.10, 0.24), sign_rough=0.50,       # station name panel, deep blue colour field
        sign_bar=(0.78, 0.78, 0.76),                          # white colour-field bar
        lbox_frame=(0.12, 0.12, 0.13), lbox_frame_rough=0.45,
        lbox_face=(0.85, 0.82, 0.75), lbox_face_rough=0.30,
    ),

    # ── lighting ──────────────────────────────────────────────────────
    #  fully indoors: both dome and sun are effectively disabled. The hdri is left at its
    #  default to pass check_assets and honour the setup_lighting contract (sealed shell, contribution 0).
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        lookfix=False,          # indoors - sun cap / horizon lift are meaningless (saves cv2 cost)
        dome_intensity=8.0,     # effectively cut off. The shell is sealed, so the real contribution is 0
        noon_dome_rot=0.0,
        noon_sun_enable=False,  # indoors - no direct sun (the prim is set invisible)
        noon_sun_elev=49.79,
        noon_sun_intensity=0.0, noon_sun_color=(1.0, 1.0, 1.0),
        hdri_sun_rotz_offset=0.0,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET: **departs to 0.0** from the convention default 171.5.
    #     Reason = in a fully sealed interior the sun azimuth affects nothing on screen,
    #     and it removes a residual variable that clouds exposure judgement. The [ ] sweep is moot too. ───
    SUN_AZ_OFFSET=0.0,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD4")

# ballast reuses the existing gravel + a darkening tint with no new asset (supervisor decision, map §shared-1).
ASSET_ROLES = ["concrete_floor", "concrete_wall", "plaster", "gravel",
               "wood_dark", "tactile", "hdri", "mdl"]


def build_views():
    """Camera presets: grid_views (gy=−3.6, running above the near platform) + 4 mise-en-scene shots.

    gy=−3.6 is 1.6 m inside the edge (y=−2.0) = the walking line just behind the tactile paving.
    Looking toward +X puts the edge and the track trough on the **left of the image** and the side wall on the right."""
    views = sc.grid_views(-3.6)
    # edge_graze: low viewpoint running right beside the edge - the key shot where the track trough is wholly hidden
    views["edge_graze"] = dict(eye=[-6.0, -2.55, 0.32], tgt=[9.0, -2.25, 0.02])
    # edge_approach: **perpendicular approach** to the edge (a pedestrian walking from inside the platform toward it)
    views["edge_approach"] = dict(eye=[8.0, -6.60, 1.60], tgt=[8.6, -1.20, -0.85])
    # track_reveal: reading shot where the track trough, rails and far platform read together
    views["track_reveal"] = dict(eye=[-3.0, -4.80, 1.85], tgt=[9.0, -0.60, -0.95])
    # tunnel_vista: the vanishing point of the run + the dark tunnel portal (impression of interior scale)
    views["tunnel_vista"] = dict(eye=[6.0, -3.40, 1.70], tgt=[44.0, -1.40, 0.10])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 돔 방위(실내=무의미)
[체크리스트]  ※ 밝기·암부 판정은 반드시 P(PathTracing, 8바운스)로!
 1. track_reveal   — 승강장/궤도 골/건너편 승강장 3층 구성이 읽히는가
 2. edge_graze     — 저시점에서 궤도 골이 은닉되어 "하나의 바닥"으로 읽히는가(특색)
 3. edge_approach  — 연단 직교 접근에서 1.15 m 수직면·발라스트가 드러나는가
 4. 조도 대비      — 궤도부가 승강장보다 확연히 어둡되 **완전 흑은 아닌가**
                     (침목·레일 두부가 겨우 읽혀야 정상. 아니면 panel.intensity 스윕)
 5. 패널           — 천장 패널 30장이 승강장 상부에만·궤도 상공엔 없는가
 6. cue ON vs OFF  — tactile/nosing/material_break 토글 시 위험 기하 트랜스폼 불변
 7. Z-파이팅       — 연단 파세이드·줄눈·점자블록·레일 두부 경계에 깜빡임 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene31")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    HA = PARAMS["hall"]
    TR = PARAMS["track"]
    ROOT = "/World/Scene31"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def SPAN(path, x0, x1, y0, y1, z0, z1, mtl=None, col=False):
        """AABB(x0..x1, y0..y1, z0..z1) box — readability wrapper for shell assembly."""
        return BOX(path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                   (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), mtl, col=col)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["platform"] = PBR(
            f"{ROOT}/Looks/Platform", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        # platform edge face: concrete wall texture + strong darkening tint (dust and brake-shoe soiling)
        M["facade"] = PBR(
            f"{ROOT}/Looks/Facade", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["facade_tint"])
        # ballast: gravel + a darkening tint, no new asset (supervisor decision)
        M["ballast"] = PBR(
            f"{ROOT}/Looks/Ballast", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"], tint=mp["ballast_tint"])
        M["sleeper"] = PBR(
            f"{ROOT}/Looks/Sleeper", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            sca["wood_dark"], tint=mp["sleeper_tint"])
        # white tile side walls - the main reflector for indirect light, so kept bright
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["wall_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # ── constant colours ──
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["head"] = PBR(f"{ROOT}/Looks/RailHead",
                        diffuse_color=mp["head_color"],
                        metallic=mp["head_metallic"],
                        roughness_const=mp["head_rough"])
        M["ceiling"] = PBR(f"{ROOT}/Looks/Ceiling",
                           diffuse_color=mp["ceil_color"],
                           roughness_const=mp["ceil_rough"])
        M["trim"] = PBR(f"{ROOT}/Looks/Trim", diffuse_color=mp["trim_color"],
                        roughness_const=mp["trim_rough"])
        M["tunnel"] = PBR(f"{ROOT}/Looks/Tunnel",
                          diffuse_color=mp["tunnel_color"],
                          roughness_const=mp["tunnel_rough"])
        M["joint"] = PBR(f"{ROOT}/Looks/Joint", diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=PARAMS["nosing"]["color"],
                          roughness_const=0.70)
        M["door"] = PBR(f"{ROOT}/Looks/Door", diffuse_color=mp["door_color"],
                        metallic=mp["door_metallic"],
                        roughness_const=mp["door_rough"])
        M["bench"] = PBR(f"{ROOT}/Looks/Bench", diffuse_color=mp["bench_color"],
                         metallic=mp["bench_metallic"],
                         roughness_const=mp["bench_rough"])
        M["fence"] = PBR(f"{ROOT}/Looks/Fence", diffuse_color=mp["fence_color"],
                         metallic=mp["fence_metallic"],
                         roughness_const=mp["fence_rough"])
        # ── signage v2 materials ──
        M["line_band"] = PBR(f"{ROOT}/Looks/LineBand",
                             diffuse_color=mp["line_band"],
                             roughness_const=mp["line_band_rough"])
        M["sign_field"] = PBR(f"{ROOT}/Looks/SignField",
                              diffuse_color=mp["sign_field"],
                              roughness_const=mp["sign_rough"])
        M["sign_bar"] = PBR(f"{ROOT}/Looks/SignBar",
                            diffuse_color=mp["sign_bar"],
                            roughness_const=mp["sign_rough"])
        M["lbox_frame"] = PBR(f"{ROOT}/Looks/LboxFrame",
                              diffuse_color=mp["lbox_frame"],
                              roughness_const=mp["lbox_frame_rough"])
        lb = PARAMS["signage"]["lightbox"]
        M["lbox_face"] = PBR(f"{ROOT}/Looks/LboxFace",
                             diffuse_color=mp["lbox_face"],
                             roughness_const=mp["lbox_face_rough"],
                             metallic=0.0,
                             emission_color=lb["emis"],
                             emission_intensity=lb["intensity"])
        # ceiling emissive panels - uses the emission argument of make_pbr (added to scene_common 07-27)
        pn = PARAMS["panel"]
        M["panel"] = PBR(f"{ROOT}/Looks/Panel", diffuse_color=pn["color"],
                         roughness_const=pn["rough"], metallic=0.0,
                         emission_color=pn["emis"],
                         emission_intensity=pn["intensity"])
        return M

    # -------------------------------------------------------------------
    # the 2 platform slabs - **they do not cover the track trough (|y|<2.0)** (lesson 5 observed).
    #   making near and far two fully separate boxes satisfies the opening-split convention
    #   structurally (the longitudinal reduction of the 4-box square-opening split: the end walls close the long direction).
    # -------------------------------------------------------------------
    def build_platforms(M):
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * HA["edge"]
            y_b = sgn * HA["plat_out"]
            SPAN(f"{ROOT}/Platform_{i}", HA["x0"], HA["x1"],
                 min(y_a, y_b), max(y_a, y_b),
                 HA["z_base"], HA["z_walk"], M["platform"], col=True)

    def build_joints(M):
        """Transverse joints in the walking surface — large slab panel boundaries (a scale cue)."""
        jt = PARAMS["joint"]
        w = jt["width"]
        n = int((HA["x1"] - HA["x0"]) / jt["step"]) + 1
        k = 0
        for i in range(n):
            x = HA["x0"] + jt["step"] * (i + 0.5)
            if x >= HA["x1"] - 0.1:
                break
            for j, sgn in enumerate((-1.0, 1.0)):
                y_a = sgn * HA["edge"]
                y_b = sgn * HA["plat_out"]
                SPAN(f"{ROOT}/Joint_{k}", x - w / 2.0, x + w / 2.0,
                     min(y_a, y_b), max(y_a, y_b),
                     HA["z_walk"] - 0.01, HA["z_walk"] + jt["proud"],
                     M["joint"])
                k += 1

    def build_facade(M):
        """Soiled fascia on the platform edge face (cue_material_break).
        z1=−0.06 → the top 6 cm remains as coping of the slab body (bright concrete).
        The y range is embedded 0.06 into the slab to avoid coplanar Z-fighting and
        projects only 0.01 toward the track."""
        fa = PARAMS["facade"]
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * fa["y_in"]
            y_b = sgn * fa["y_out"]
            SPAN(f"{ROOT}/Facade_{i}", HA["x0"], HA["x1"],
                 min(y_a, y_b), max(y_a, y_b), fa["z0"], fa["z1"], M["facade"])

    # -------------------------------------------------------------------
    # track bed - ballast slab + sleepers + 2 rails
    # -------------------------------------------------------------------
    def build_track(M):
        hw = TR["half_w"]
        SPAN(f"{ROOT}/Ballast", TR["x0"], TR["x1"], -hw, hw,
             TR["ballast_bot"], TR["ballast_top"], M["ballast"], col=True)

        rs = np.random.RandomState(int(PARAMS["seed"]))     # fixed seed
        step = TR["sleeper_step"]
        n = int((TR["x1"] - TR["x0"] - 0.4) / step) + 1
        sz = (TR["sleeper_w"], TR["sleeper_len"], TR["sleeper_h"])
        zc = TR["sleeper_top"] - TR["sleeper_h"] / 2.0
        for i in range(n):
            x = TR["x0"] + 0.2 + step * i + rs.uniform(-TR["jitter_x"],
                                                       TR["jitter_x"])
            y = rs.uniform(-TR["jitter_y"], TR["jitter_y"])
            z = zc + rs.uniform(-TR["jitter_z"], TR["jitter_z"])
            BOX(f"{ROOT}/Sleeper_{i}", (x, y, z), sz, M["sleeper"])

        # 2 rails: web (dark steel) + head (polished, metallic 0.85)
        rz0 = TR["sleeper_top"]
        rz1 = rz0 + TR["rail_h"]
        for i, sgn in enumerate((-1.0, 1.0)):
            yc = sgn * TR["gauge"] / 2.0
            SPAN(f"{ROOT}/Rail_{i}/Body", TR["x0"], TR["x1"],
                 yc - TR["rail_w"] / 2.0, yc + TR["rail_w"] / 2.0,
                 rz0, rz1, M["rail"])
            # the head is embedded 0.015 into the web top and projects 0.01 (avoids coplanarity)
            SPAN(f"{ROOT}/Rail_{i}/Head", TR["x0"], TR["x1"],
                 yc - TR["head_w"] / 2.0, yc + TR["head_w"] / 2.0,
                 TR["head_z0"], TR["head_z1"], M["head"])

    def build_flat_fill(M):
        """hazard_stairs=False control: the track trough is filled to z=0, making it all flat.
        (no edge fascia and no track built at all — drop 0)"""
        SPAN(f"{ROOT}/FlatFill", HA["x0"], HA["x1"],
             -TR["half_w"], TR["half_w"], HA["z_base"], HA["z_walk"],
             M["platform"], col=True)

    # -------------------------------------------------------------------
    # shell - 2 side walls · ceiling · 2 end walls (+tunnel portal) · tunnel bore
    #   the goal is a full seal: no face leaves a path for the dome light to enter.
    # -------------------------------------------------------------------
    def build_shell(M):
        # side walls (white tile). Inner face |y|=7.98 - embedded 0.02 into the slab (+-8.0).
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * HA["wall_in"]
            y_b = sgn * HA["wall_out"]
            SPAN(f"{ROOT}/SideWall_{i}", HA["x0"] - HA["end_t"],
                 HA["x1"] + HA["end_t"], min(y_a, y_b), max(y_a, y_b),
                 HA["z_base"], HA["wall_top"], M["wall"], col=True)
        # ceiling slab (covers the wall tops with 0.30 of embedment)
        SPAN(f"{ROOT}/Ceiling", HA["x0"] - HA["end_t"], HA["x1"] + HA["end_t"],
             -HA["wall_out"], HA["wall_out"], HA["ceil_z0"], HA["ceil_z1"],
             M["ceiling"])
        # end wall W (platform start end) - fully closed
        SPAN(f"{ROOT}/EndWall_W", HA["x0"] - HA["end_t"], HA["x0"] + 0.02,
             -HA["wall_out"], HA["wall_out"], HA["z_base"], HA["ceil_z1"],
             M["wall"], col=True)
        # end wall E (tunnel side) - split into 3, leaving the track opening (portal)
        po = PARAMS["portal"]
        ex0, ex1 = HA["x1"] - 0.02, HA["x1"] + HA["end_t"]
        SPAN(f"{ROOT}/EndWall_E_0", ex0, ex1, -HA["wall_out"], -po["half_w"],
             HA["z_base"], HA["ceil_z1"], M["wall"], col=True)
        SPAN(f"{ROOT}/EndWall_E_1", ex0, ex1, po["half_w"], HA["wall_out"],
             HA["z_base"], HA["ceil_z1"], M["wall"], col=True)
        SPAN(f"{ROOT}/EndWall_E_2", ex0, ex1,
             -po["half_w"] - 0.02, po["half_w"] + 0.02,
             po["top_z"], HA["ceil_z1"], M["wall"], col=True)

        # tunnel bore - sealed with 5 dark boxes (2 side walls·ceiling·floor·back cap).
        #   "dark tunnel mouth" is the target, so the material is an extremely dark constant around 0.022.
        bo = PARAMS["bore"]
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * bo["half_in"]
            y_b = sgn * bo["half_out"]
            SPAN(f"{ROOT}/Bore_Side_{i}", bo["x0"], bo["x1"],
                 min(y_a, y_b), max(y_a, y_b), bo["z0"], bo["z1"], M["tunnel"])
        SPAN(f"{ROOT}/Bore_Roof", bo["x0"], bo["x1"],
             -bo["half_out"], bo["half_out"], po["top_z"], bo["z1"],
             M["tunnel"])
        SPAN(f"{ROOT}/Bore_Floor", bo["x0"], bo["x1"],
             -bo["half_out"], bo["half_out"], bo["z0"], HA["z_base"] + 0.02,
             M["tunnel"])
        SPAN(f"{ROOT}/Bore_Cap", bo["x1"] - bo["cap_t"], bo["x1"],
             -bo["half_out"], bo["half_out"], bo["z0"], bo["z1"], M["tunnel"])

    # -------------------------------------------------------------------
    # ceiling emissive panels - only the 2 rows above the platforms. Nothing above the track, deliberately.
    # -------------------------------------------------------------------
    def build_panels(M):
        pn = PARAMS["panel"]
        k = 0
        for r, yc in enumerate(pn["rows"]):
            for i in range(int(pn["n"])):
                x = pn["x0"] + pn["step"] * i
                SPAN(f"{ROOT}/Panel_{k}",
                     x - pn["size_x"] / 2.0, x + pn["size_x"] / 2.0,
                     yc - pn["size_y"] / 2.0, yc + pn["size_y"] / 2.0,
                     pn["z0"], pn["z1"], M["panel"])
                k += 1
        print(f"[조명] 천장 발광 패널 {k}장 "
              f"(열 {len(pn['rows'])} × {pn['n']}, 간격 {pn['step']} m, "
              f"emissive_intensity={pn['intensity']}) — 궤도 상공 미배치")

    # -------------------------------------------------------------------
    # cues - tactile paving / platform edge line / barrier railing at the platform end
    # -------------------------------------------------------------------
    def build_cues(M):
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            a0 = HA["edge"] + tc["offset"]              # 2.30
            a1 = a0 + tc["width"]                       # 2.60
            b0 = a1 + tc["gap"]                         # 2.62
            b1 = b0 + tc["width"]                       # 2.92
            k = 0
            for sgn in (-1.0, 1.0):
                for (p, q) in ((a0, a1), (b0, b1)):
                    y0, y1 = sorted((sgn * p, sgn * q))
                    sc.build_tactile(stage, f"{ROOT}/Tactile_{k}",
                                     HA["x0"], HA["x1"], y0, y1, M["tactile"],
                                     z=HA["z_walk"], proud=tc["proud"])
                    k += 1
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            for i, sgn in enumerate((-1.0, 1.0)):
                p = HA["edge"] + ns["inset"]
                q = p + ns["width"]
                y0, y1 = sorted((sgn * p, sgn * q))
                SPAN(f"{ROOT}/Nosing_{i}", HA["x0"], HA["x1"], y0, y1,
                     HA["z_walk"] - 0.01, HA["z_walk"] + ns["proud"],
                     M["nosing"])
        if cfg["cue_railing"]:
            # barrier railing at the platform end (tunnel side). The hazard is that **the edge has no railing**.
            er = PARAMS["endrail"]
            k = 0
            for sgn in (-1.0, 1.0):
                ya = sgn * HA["edge"]
                yb = sgn * HA["plat_out"]
                y0, y1 = sorted((ya, yb))
                length = y1 - y0
                yc = (y0 + y1) / 2.0
                for tag, hz, rr in (("Top", er["top_h"], er["rail_r"]),
                                    ("Mid", er["mid_h"], er["rail_r"] * 0.6)):
                    CYL(f"{ROOT}/EndRail_{k}/{tag}", (er["x"], yc, hz),
                        rr, length, M["fence"], rotX=90.0)
                ph = er["top_h"]
                for j in range(int(er["nposts"])):
                    t = (j + 0.5) / float(er["nposts"])
                    CYL(f"{ROOT}/EndRail_{k}/Post_{j}",
                        (er["x"], y0 + t * length, ph / 2.0),
                        er["post_r"], ph, M["fence"])
                k += 1

    # -------------------------------------------------------------------
    # dressing - benches · wall doors · skirting / cornice bands (reinforces the context reading)
    # -------------------------------------------------------------------
    def build_dressing(M):
        bn = PARAMS["bench"]
        k = 0
        # [v5.1 §3] breaks the 12 m even spacing and the perfect axis alignment. These are fixed
        #   platform seats, so the jitter is **small**: angle within the installation tolerance (3~5 deg), position +-0.12 m
        #   (the ceiling panels, sleepers and tactile paving are exempt as industrially aligned, so unchanged).
        #   |y| = 7.40 +- 0.12 -> clearance kept from the edge (|y| 2.0) and the side wall (7.958).
        for ys, xs in ((bn["ys"][0], bn["xs_near"]), (bn["ys"][1], bn["xs_far"])):
            for x in xs:
                dx, dy = bc.jit_pos(x, ys, "benchD4", amp=0.12)
                yaw = bc.jit_yaw(x, ys, "benchD4", lo=3.0, hi=5.0)
                sc.build_bench(stage, f"{ROOT}/Bench_{k}", x + dx, ys + dy,
                               HA["z_walk"], M["bench"], length=bn["length"],
                               width=bn["width"], height=bn["height"], yaw=yaw)
                k += 1
        tm = PARAMS["trim"]
        dr = PARAMS["door"]
        k = 0
        for sgn in (-1.0, 1.0):
            wi = sgn * HA["wall_in"]
            wo = sgn * (HA["wall_in"] - tm["proud"])    # projects from the wall into the room
            y0, y1 = sorted((wi, wo))
            SPAN(f"{ROOT}/Skirt_{k}", HA["x0"], HA["x1"], y0, y1,
                 tm["skirt_z0"], tm["skirt_z1"], M["trim"])
            SPAN(f"{ROOT}/Cornice_{k}", HA["x0"], HA["x1"], y0, y1,
                 tm["cornice_z0"], tm["cornice_z1"], M["trim"])
            k += 1
        k = 0
        for sgn in (-1.0, 1.0):
            wi = sgn * HA["wall_in"]
            wo = sgn * (HA["wall_in"] - dr["t"])
            y0, y1 = sorted((wi, wo))
            for x in dr["xs"]:
                SPAN(f"{ROOT}/Door_{k}", x - dr["w"] / 2.0, x + dr["w"] / 2.0,
                     y0, y1, HA["z_walk"], HA["z_walk"] + dr["h"], M["door"])
                k += 1

    # -------------------------------------------------------------------
    # signage context v2 - line colour band · station name panels · ad lightboxes · ceiling-hung signs
    # -------------------------------------------------------------------
    def build_signage(M):
        """Platform signage. **The edge, track, tactile paving, emissive panels and lighting are all unchanged.**

        ── Camera check (a PT-judged scene, so replaced by a coordinate check) ─────────
        Eyes of all views: grid(gy −3.6) (−2/−5/−10, −3.6, 0.3~1.8) ·
          edge_graze(−6, −2.55, 0.32) · edge_approach(8, −6.60, 1.60) ·
          track_reveal(−3, −4.80, 1.85) · tunnel_vista(6, −3.40, 1.70).
        1) Wall elements (band·name panel·lightbox): max projection y = ±(7.98−0.095)
           = ±7.885. Max camera |y| = 6.60 (edge_approach) → **1.29 m clearance**,
           zero burial or interference. 5.9 m clear of the walking surface (z 0) and the edge (|y|=2.0).
        2) Ceiling-hung signs: |y| = 2.60 (0.6 m inside the edge, directly above the tactile paving 2.30~2.92),
           panel bottom z 2.44. Max camera z = 1.85 (track_reveal) →
           **vertical clearance 0.59 m**; the nearest camera, edge_graze (y −2.55, z 0.32),
           is more than 6 m away in x → burial 0.
           · FOV check: from edge_graze the x=0 sign is at elevation 19.5° > vfov half 18°
             → it leaves the top of the frame, while the x=24 sign at 4.0° → in frame (distant).
             Neither obstructs the **downward sight line to the edge line and track trough**.
           · From track_reveal the x=0 sign is 23° above the optical axis → out of frame,
             the x=24 sign 13.8° → in frame (upper). The track sight line is downward, so no interference.
        3) x-range collision check: doors x{−8,6,20,34}(±0.50) / name panels x{−4,10,30}
           near·{2,26} far (±0.80) / lightboxes x{16} near·{12} far (±1.10)
           → no overlapping ranges on the same wall face. The benches (near −2,10,22,34 /
           far 4,16,28) sit at y=±7.40, clear of the wall elements (|y| ≥ 7.905) in both z and y.
        4) Line colour band z 2.30~2.55 — above the door tops 2.10 / name panel tops 2.05 /
           lightbox tops 2.15, below the cornice bottom 3.08 → coplanarity 0.
        """
        sg = PARAMS["signage"]
        wi = HA["wall_in"]
        cnt = dict(band=0, plate=0, lbox=0, hanger=0)

        def wall_slab(path, x0, x1, sgn, z0, z1, proud, mtl, embed=0.005):
            """Thin plate fixed to the inner face of a side wall. sgn=−1 near / +1 far.
            The back is embedded into the wall by `embed`, removing coplanarity with the wall face."""
            y_a = sgn * (wi + embed)
            y_b = sgn * (wi - proud)
            SPAN(path, x0, x1, min(y_a, y_b), max(y_a, y_b), z0, z1, mtl)

        # ── (1) line colour band (runs along both side walls) ──
        bd = sg["band"]
        for i, sgn in enumerate((-1.0, 1.0)):
            wall_slab(f"{ROOT}/LineBand_{i}", HA["x0"], HA["x1"], sgn,
                      bd["z0"], bd["z1"], bd["proud"], M["line_band"],
                      bd["embed"])
            cnt["band"] += 1

        # ── (2) station name panels (textless colour-field plates) ──
        np_ = sg["nameplate"]
        for i, pl in enumerate(sg["nameplates"]):
            x, sgn = pl["x"], pl["sgn"]
            wall_slab(f"{ROOT}/NamePlate_{i}", x - np_["w"] / 2.0,
                      x + np_["w"] / 2.0, sgn,
                      np_["z_c"] - np_["h"] / 2.0, np_["z_c"] + np_["h"] / 2.0,
                      np_["proud"], M["sign_field"], np_["embed"])
            # white colour-field bar - projects a further bar_proud from the panel face (coplanarity 0)
            y_a = sgn * (wi - np_["proud"] + 0.008)
            y_b = sgn * (wi - np_["proud"] - np_["bar_proud"])
            SPAN(f"{ROOT}/NamePlate_{i}_Bar", x - np_["bar_w"] / 2.0,
                 x + np_["bar_w"] / 2.0, min(y_a, y_b), max(y_a, y_b),
                 np_["z_c"] - np_["bar_h"] / 2.0,
                 np_["z_c"] + np_["bar_h"] / 2.0, M["sign_bar"])
            cnt["plate"] += 1

        # ── (3) ad lightboxes (weak emission - 1/5 of the panels) ──
        lb = sg["lightbox"]
        for i, bx in enumerate(sg["lightboxes"]):
            x, sgn = bx["x"], bx["sgn"]
            fw, fh = lb["w"] + 2.0 * lb["frame"], lb["h"] + 2.0 * lb["frame"]
            wall_slab(f"{ROOT}/LightBox_{i}_Frame", x - fw / 2.0, x + fw / 2.0,
                      sgn, lb["z_c"] - fh / 2.0, lb["z_c"] + fh / 2.0,
                      lb["frame_proud"], M["lbox_frame"], lb["embed"])
            # emissive face: the back is embedded 0.010 into the frame slab and the front projects
            #   0.020 past the frame -> coplanarity 0, and the frame remains as a 0.09 wide border.
            y_a = sgn * (wi - lb["face_proud"])
            y_b = sgn * (wi - lb["face_proud"] + 0.030)
            SPAN(f"{ROOT}/LightBox_{i}_Face", x - lb["w"] / 2.0,
                 x + lb["w"] / 2.0, min(y_a, y_b), max(y_a, y_b),
                 lb["z_c"] - lb["h"] / 2.0, lb["z_c"] + lb["h"] / 2.0,
                 M["lbox_face"])
            cnt["lbox"] += 1

        # ── (4) ceiling-hung station signs ──
        hg = sg["hanger"]
        for i, hd in enumerate(sg["hangers"]):
            x, sgn = hd["x"], hd["sgn"]
            yc = sgn * hg["y"]
            SPAN(f"{ROOT}/HangSign_{i}", x - hg["w"] / 2.0, x + hg["w"] / 2.0,
                 yc - hg["t"] / 2.0, yc + hg["t"] / 2.0, hg["z0"], hg["z1"],
                 M["sign_field"])
            # double-sided colour-field bars (2 of them so they read from both directions)
            for s, sy in enumerate((-1.0, 1.0)):
                y_a = yc + sy * hg["t"] / 2.0 - sy * 0.008
                y_b = yc + sy * (hg["t"] / 2.0 + hg["bar_proud"])
                SPAN(f"{ROOT}/HangSign_{i}_Bar{s}", x - hg["bar_w"] / 2.0,
                     x + hg["bar_w"] / 2.0, min(y_a, y_b), max(y_a, y_b),
                     (hg["z0"] + hg["z1"]) / 2.0 - hg["bar_h"] / 2.0,
                     (hg["z0"] + hg["z1"]) / 2.0 + hg["bar_h"] / 2.0,
                     M["sign_bar"])
            for s, sx in enumerate((-hg["rod_dx"], hg["rod_dx"])):
                CYL(f"{ROOT}/HangSign_{i}_Rod{s}",
                    (x + sx, yc, (hg["z1"] - 0.03 + hg["ceil_z"]) / 2.0),
                    hg["rod_r"], hg["ceil_z"] - hg["z1"] + 0.03, M["fence"])
            cnt["hanger"] += 1
        return cnt

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ... (완전 실내 · 발광 패널 단독 조명)")
    M = setup_materials()

    build_platforms(M)
    build_joints(M)
    build_shell(M)
    if cfg["hazard_stairs"]:
        build_track(M)
        if cfg["cue_material_break"]:
            build_facade(M)
    else:
        build_flat_fill(M)
    build_panels(M)
    build_cues(M)
    sign_cnt = None
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        sign_cnt = build_signage(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])
    print("[조명] 완전 밀폐 실내 — dome/sun 기여 0. "
          "밝기·암부 판정은 PathTracing(P키, 8바운스)로만 할 것.")

    if sign_cnt is not None:
        # signage self-check (a PT scene - elements RT cannot confirm are checked by coordinates)
        sg = PARAMS["signage"]
        lb, hg = sg["lightbox"], sg["hanger"]
        eyes = [(-2.0, -3.6, 1.8), (-5.0, -3.6, 1.8), (-10.0, -3.6, 1.8),
                (-6.0, -2.55, 0.32), (8.0, -6.60, 1.60),
                (-3.0, -4.80, 1.85), (6.0, -3.40, 1.70)]
        y_wall_face = HA["wall_in"] - max(lb["frame_proud"], lb["face_proud"],
                                          sg["nameplate"]["proud"],
                                          sg["band"]["proud"])
        wall_margin = y_wall_face - max(abs(e[1]) for e in eyes)
        z_margin = hg["z0"] - max(e[2] for e in eyes)
        ratio = lb["intensity"] / PARAMS["panel"]["intensity"]
        print(f"[사이니지] 노선밴드 {sign_cnt['band']} · 역명판 "
              f"{sign_cnt['plate']} · 라이트박스 {sign_cnt['lbox']} · "
              f"천장 걸이 {sign_cnt['hanger']}")
        print(f"[검산] 벽면 요소 최전면 |y|={y_wall_face:.3f} vs 카메라 최대 "
              f"|y|={max(abs(e[1]) for e in eyes):.2f} → 여유 "
              f"{wall_margin:.2f} m · 걸이 사인 하단 z={hg['z0']:.2f} vs "
              f"카메라 최고 z={max(e[2] for e in eyes):.2f} → 여유 "
              f"{z_margin:.2f} m")
        print(f"[검산] 라이트박스 발광비 {ratio:.2f} × 패널(상한 0.25) · "
              f"연단(|y|=2.0)·궤도·점자블록·패널 좌표 불변")

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneD4 조립 완료 · SMOKE_OK prims={n} · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["track_reveal"]
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
                print("[렌더] RTX Real-Time (이동용 — 실내 발광 미반영)")
            else:
                set_render_mode("PathTracing")
                print(f"[렌더] PathTracing (totalSpp={pt_spp}, "
                      f"maxBounces={PARAMS['render']['pt_max_bounces']}) "
                      f"← 판정은 이 모드로")
        elif event.input == K.C:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD4_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[돔 방위] 오프셋 {dome_user_rot[0]:+.0f}° (실내라 영향 없음)")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[돔 방위] 오프셋 {dome_user_rot[0]:+.0f}° (실내라 영향 없음)")
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
