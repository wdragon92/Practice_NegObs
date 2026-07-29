# -*- coding: utf-8 -*-
"""
scene20_diagonal_oblique.py - NegObs synthetic scene 20: diagonal oblique stair (Isaac Sim 4.5)

Type    : T8 diagonal oblique (alignment assumption breaks down)
Spec    : Docs/multi_scene_brief_v3.md §D scene20_diagonal_oblique
Shared  : scene_common.py (verified API helpers) · scene01/scene02 (urban skeleton)

Hazard  : a straight stair rotated 30 deg relative to the plaza walk axis (+X). In the
          frontal presets (axis = walk axis +X, fixed) the drop boundary cuts across the
          frame diagonally - the assumption that a stair is aligned with the direction of
          travel breaks down. The horizon-closing buildings stay axis-aligned, which
          sharpens the contrast.
Goal    : assemble an upper plaza (plaza_light + bands, a scaled-down scene01 motif), a
          30 deg rot_group stair of 14 steps (width 5), the diagonal extension wedge
          (flush plaza-to-stair joint), a lower plaza (warm plaza_lower), grass fill (no
          cavity), 3 axis-aligned buildings and axis-aligned props (bollard rows, planters,
          benches, street lamps), and judge it from renders (render only).

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene20_diagonal_oblique.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene20_diagonal_oblique.py
Smoke early exit:         NEGOBS_SMOKE=1  python scene20_diagonal_oblique.py

Coordinates: Z-up, m, walk axis +X (fixed by the presets), drop start edge = x=0 before rotation.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs is a geometry toggle (False -> unified flat ground).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> remove stairs/lower plaza, whole scene flat at z=0
    "cue_railing":        True,   # Sloped rails on both sides of the stair (inside rot_group - follows the diagonal)
    "cue_tactile":        False,  # [v5.2 user] Tactile paving is rare in reality - OFF by default (ablation path kept)   # Top warning strip (inside rot_group - follows the diagonal)
    "cue_material_break": True,   # False -> unify stair/lower with the upper material (plaza_light)
    "cue_nosing":         False,  # (key reserved)
    "cue_sign":           False,  # [v5.2 user] Arbitrary warning placards removed - nothing placed (key reserved only)
    "cue_scene_dressing": True,   # Bands, axis-aligned buildings and grass in one go
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # Upper plaza (mesa): plaza_light, x -14..-4.5, y -8..8. Top face z=0, solid down to the valley.
    #   [audit v4 A2] x1 0.0 -> -4.5. If the axis-aligned plaza edge runs east past the stair
    #   top line (local x=0 = world x=-0.5774*y diagonal), the north (y>0) top steps get
    #   buried in the plaza solid and the first step height grows to as much as 0.75 m. x1=-4.5
    #   satisfies both limits at once:
    #     (1) the value at which the plaza edge stays west of the diagonal over all |y|<=8
    #        (diagonal x = -0.5774*8 = -4.619 <= -4.5 exceeds by only 0.12 m at y=8 - and that
    #         point is outside the stair width (local |y|<=2.5), pure cliff, irrelevant to walking),
    #     (2) the value at which the wedge below (local |y|<=9) still covers the remaining area
    #        with no gap (mesa points have lx<=0 => y <= -1.732x => ly = -0.5x+0.866y <= -2x <= 9).
    upper=dict(x0=-14.0, x1=-4.5, y0=-8.0, y1=8.0, z_top=0.0, base_z=-2.2),
    # Diagonal extension wedge of the upper plaza (inside rot_group - east face = stair top line)
    wedge=dict(x0=-8.0, x1=0.0, y_half=9.0, z_top=0.0, base_z=-2.2),
    # [W2-D, spec §5.1 scene20 row] Band x range -13...-5 -> **extended to -13...-0.5**.
    #   Measurement basis: the current 5 bands (-13/-11/-9/-7/-5) **hit the d10 cut only** - the
    #   near window of d5 is x -4.44...-3.0 and d2 is -1.44...0, so not one band falls inside.
    #   Restoring the -3 and -1 bands gives all three cuts a longitudinal structure line.
    #   * The old comment ("bands only over the axis-aligned plaza") pulled x1 back to -5.0 for a
    #     real reason: the mesa is the union of the axis-aligned plaza (x <= -4.5) and the 30 deg
    #     wedge, and the wedge's east boundary is the world line **x = -0.5774*y**. Leaving a
    #     full-width y+-8 band at x=-3 would leave the y > 5.196 stretch floating in mid-air.
    #     -> extend x1 as the spec says, but **clamp each band's +y end to the mesa boundary**
    #       (`y_hi = min(y_half, 1.7321*|x|)`). The -y side stays at y_half since it is inside the
    #       wedge local |ly| <= 9 [computed]. The clipped bands end in a staircase along the
    #       diagonal, which if anything strengthens this scene's theme of "axis-aligned props vs 30 deg diagonal".
    band=dict(width=0.45, spacing=2.0, proud=0.0015, x0=-13.0, x1=-0.5,
              y_half=8.0, mesa_slope=1.7320508),   # cot(30°) = 1/tan(30°)
    # Stair 14 steps x riser 0.15, tread 0.34 -> drop 2.1 m, run 4.76 m. Width 5 (y +-2.5).
    stairs=dict(x0=0.0, riser=0.15, tread=0.34, nsteps=14,
                y0=-2.5, y1=2.5, z_top=0.0, base_z=-2.6),
    # rot_group: pivot (0,0), 30 deg - rotates stair and lower plaza together (boundary stays aligned)
    rot=dict(pivot=(0.0, 0.0), deg=30.0),
    # Lower plaza (warm) - inside rot_group, continues from the stair foot (local x=4.76, z=-2.1)
    lower=dict(x0=4.76, x1=18.0, y0=-2.5, y1=2.5, z_top=-2.1, thick=0.15),
    # Lower grass base - fills the valley (no cavity). Fully solid under the rotated stair/plaza.
    valley=dict(size=100.0, z_top=-2.15, thick=1.0),

    stair_rail=dict(y=2.4, x_start=-0.4, rail_h=0.9, post_r=0.02,
                    rail_r=0.03, rail_mid_r=0.018, rail_mid_drop=0.45,
                    spacing=1.3),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004),

    # === [W2-D ground_kit] P1 plaza_granite - spec §5.1 scene20 row ========================
    #  The row's own prescription is the band extension (see `band` above);
    #  the P1 common set (6 m expansion + 1.8 m contraction joints, 1~2
    #  manholes with one in W1, repair patches, soiling decals, edge weeds)
    #  supplies the rest.
    #  ★ Tactile **OFF** (§12.4 identity conflict — hidden illusion). Gate B12
    #    `_inv_hidden_illusion` refuses a tactile element or any bright
    #    (albedo > 0.28) full-width transverse line for scene20.
    #  ★ Region x1 = **-2.0**, not -0.5. The drop edge of this scene is the
    #    30 deg diagonal x = -0.5774*y, not the line x = 0 that the kit's frame
    #    model assumes. A rectangle is only entirely on the mesa if
    #    x1 <= -0.5774*|y|max; with y = +-3.0 that is x1 <= -1.73, and -2.0
    #    keeps 0.27 m of margin at the worst corner [computed].
    #    Consequence: the d2 near window (x -1.44..0) cannot be filled by the
    #    kit at all in this scene. That is geometry, not an omission — the d2
    #    window lies beyond the diagonal for most of the frame width.
    gkit=dict(
        region=(-13.0, -3.0, -2.0, 3.0),
        manholes=[(-5.00, 1.40), (-10.00, -1.40)],
        gullies=[(-3.00, -2.60), (-8.00, 2.60)],
        patches=[(-3.70, -0.55), (-8.60, 0.30)],
    ),

    # 3 axis-aligned horizon-closing buildings (not rotated - emphasises the alignment contrast)
    #   base_z=-2.15 : top face of the valley grass. Left unset (0.0) the shell only reached down
    #   to z=-1.0 and floated 1.15 m (audit v4 B3).
    buildings=dict(
        C=dict(x0=26.0, x1=32.0, y0=-14.0, y1=14.0, h=13.0, floors=4,
               axis="x", facade_x=26.0, face_dir=-1.0, base_z=-2.15),
        D=dict(x0=-6.0, x1=20.0, y0=16.0, y1=22.0, h=11.0, floors=4,
               axis="y", facade_y=16.0, face_dir=-1.0, base_z=-2.15),
        E=dict(x0=-40.0, x1=-32.0, y0=-16.0, y1=16.0, h=16.0, floors=5,
               axis="x", facade_x=-32.0, face_dir=1.0, base_z=-2.15),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.6, margin=2.0),

    # --- Context dressing (cue_scene_dressing): "civic / university-front urban plaza" ---
    #     The contrast between axis-aligned props (bands, buildings, planter rows) and the 30 deg diagonal edge is this scene's theme.
    #     All upper props sit on the mesa (axis-aligned plaza union wedge) - see fixlog_I5 for the coordinate check.
    # [v5.1 §2] Bollards regularised - old: 5 bollards at 2.0 m spacing along x -1.2 over y -7..1
    #   plus 3 scattered = 8 total. That is a **decorative row lined up right in front of the
    #   diagonal drop edge (local x=0)**, which has no basis in §2 (vehicle entry points only) and
    #   also violates the equal-spacing convention (§3). Dropped exactly as instructed: "do not line them up along the diagonal edge itself".
    #   New: **one row** at each of the 2 actual vehicle approach points (1.5 m spacing, 1.5 m centre gap),
    #   with a 0.3 m dot-tactile strip in front of each row on the pedestrian side.
    #     (1) Top of the mesa entry ramp (x -13.6; ramp x -18..-14, width y +-2)
    #        -> **behind** (x < -10) every grid eye (x -2/-5/-10) and every mise-en-scene preset
    #     (2) Entrance to the lower plaza's diagonal corridor (rot local lx 17.0, plaza x1 18.0)
    #        -> world (14.72, 8.50). From the grid eyes that is bearing 19-27 deg, distance 18.7-26 m,
    #          i.e. background, with no interference with the judged region (diagonal drop boundary x -4.6..0).
    bollards=dict(x=-13.6, ys=(-2.25, -0.75, 0.75, 2.25),
                  block=dict(x0=-13.6, x1=-13.3, y0=-2.55, y1=2.55)),
    planters=[(-10.0, 5.5), (-10.0, -5.5), (-6.5, 6.2)],
    planter=dict(size=3.0),
    benches=[(-7.5, 6.6, 180.0), (-7.5, -6.6, 0.0),
             (-11.5, 3.0, 90.0), (-11.5, -3.0, -90.0)],
    streetlights=[(-7.0, 6.8), (-9.0, -6.8), (-12.5, 4.0)],
    streetlight=dict(pole_h=5.5, pole_r=0.07, arm_len=1.0, arm_r=0.04,
                     head=0.25),
    hedges=[(-14.0, 7.4, -9.0, 8.0), (-14.0, -8.0, -9.0, -7.4)],
    # Mesa entry ramp (west side) - "how does one get up onto this plaza" (audit v4 A5)
    access_ramp=dict(x0=-18.0, x1=-14.0, y0=-2.0, y1=2.0, thick=2.6),
    # [v5.2 user] Arbitrary warning placards removed - stair-warning sign (PARAMS['signs']) deleted.
    # Lower plaza props (rot_group local coordinates, base_z=-2.1)
    # [v5.1 §2] Old: 2 pairs at the stair foot (lx 5.6/9.0) = decorative placement lining the
    #   diagonal corridor. -> Moved to a single row at the corridor **entrance** (lx 17.0) plus a 0.3 m dot-tactile strip in front.
    lower_bollards=dict(x=17.0, ys=(-2.25, -0.75, 0.75, 2.25),
                        block=dict(x0=16.7, x1=17.0, y0=-2.55, y1=2.55)),
    lower_benches=[(12.0, -1.85, 0.0), (12.0, 1.85, 0.0)],

    material=dict(
        scale=dict(plaza_light=1.80, band_dark=0.6, plaza_lower=0.7,
                   grass=1.4, brick_red=2.0, tactile=0.3),
        lower_warm_tint=(1.06, 1.0, 0.94),
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] Parapet 0.90 -> 0.72 (no large pure-white areas)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        # For dressing (dark constant-colour albedo convention)
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
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
    SUN_AZ_OFFSET=171.5,   # Standard. Keeps the preset frontal light (inherited from scene01). Shadows fall on the
                           # diagonal drop boundary and emphasise the obliqueness (can be fine-tuned at render time).

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene20")

ASSET_ROLES = ["plaza_light", "band_dark", "plaza_lower", "grass",
               "brick_red", "tactile",
               "hdri", "mdl"]      # [v5.2 user] Arbitrary warning placards removed


def build_views():
    """Camera presets: grid_views(gy=0, walk axis +X [fixed]) + 4 mise-en-scene cuts."""
    views = sc.grid_views(0.0)               # Preset axis = walk axis +X (spec §D, fixed)
    # oblique_overview: the diagonal drop boundary cuts across the frame
    views["oblique_overview"] = dict(eye=[-8.0, -4.0, 3.2], tgt=[3.0, 1.0, -1.0])
    # walk_axis_front: head-on along the walk axis - the boundary slices the frame diagonally
    views["walk_axis_front"] = dict(eye=[-6.0, 0.0, 1.6], tgt=[4.0, 0.0, -0.8])
    # along_diagonal: looking down along the stair's diagonal axis (confirms the alignment breakdown)
    views["along_diagonal"] = dict(eye=[-3.0, -3.0, 1.5], tgt=[5.0, 1.6, -1.6])
    # low_grazing: low viewpoint - the drop is hidden above the diagonal boundary
    views["low_grazing"] = dict(eye=[-6.0, 0.0, 0.35], tgt=[4.0, 0.5, -0.3])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. oblique_overview / walk_axis_front — 30° 사교 계단·사선 낙차 경계 식별
 2. h0.3·d5~10                         — 사선 경계 위로 낙차 2.1m가 은닉되는가
 3. 정렬 대비                          — 건물은 축정렬, 계단만 30° 틀어진 대비
 4. cue ON vs OFF                      — railing/tactile(사선 따라) 토글 시 기하 불변
 5. 재질/공동                          — 하부 잔디 채움·경계 정합·Z파이팅 없는가
 6. [v4] 사선 쐐기 접합(첫 단차 전 폭 0.15)·축정렬 볼라드 열·건물 접지
 7. [v5] 공통 레이어 — 사선 점자띠 판독"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene20")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene20"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["upper"] = PBR(
            f"{ROOT}/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["lower"] = PBR(
            f"{ROOT}/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["lower_warm_tint"])
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
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [v5.1 §2/§4] Materials for the regulation bollards - 3 body variants (tint jitter +-5%) + reflective band.
        #   The band is small in area, so high luminance is allowed (unrelated to the no-large-pure-white-area rule).
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
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # Ground - valley grass (fully solid, no cavity) + upper mesa
    # -------------------------------------------------------------------
    def build_ground(M):
        v = PARAMS["valley"]
        H = v["size"] / 2.0
        BOX(f"{ROOT}/Valley", (6.0, 0.0, v["z_top"] - v["thick"] / 2.0),
            (v["size"], v["size"], v["thick"]), M["grass"], col=True)

    def build_upper(M):
        u = PARAMS["upper"]
        cx = (u["x0"] + u["x1"]) / 2.0
        cy = (u["y0"] + u["y1"]) / 2.0
        top, bot = u["z_top"], u["base_z"]
        # [W2-0 · P-A] The mesa top is the ground_kit stage.
        sc.skin_exclude(f"{ROOT}/UpperPlaza")
        BOX(f"{ROOT}/UpperPlaza", (cx, cy, (top + bot) / 2.0),
            (u["x1"] - u["x0"], u["y1"] - u["y0"], top - bot),
            M["upper"], col=True)
        # Bands (charcoal stripes running along Y, a scaled-down scene01 motif)
        if cfg["cue_scene_dressing"]:
            bd = PARAMS["band"]
            x = bd["x0"]
            i = 0
            while x <= bd["x1"] + 1e-6:
                # [W2-D] Clamp the +y end to the mesa boundary (axis-aligned plaza union 30 deg wedge).
                y_hi = min(bd["y_half"], bd["mesa_slope"] * abs(x))
                y_lo = -bd["y_half"]
                if y_hi - y_lo > 0.30:      # Skip the band if no length remains
                    BOX(f"{ROOT}/Band_{i}",
                        (x, (y_lo + y_hi) / 2.0, top + bd["proud"] - 0.003),
                        (bd["width"], y_hi - y_lo, 0.02), M["band"])
                x += bd["spacing"]
                i += 1

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P1 plaza_granite (spec §5.1 scene20 row)
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        st = PARAMS["stairs"]
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]),
            z=float(PARAMS["upper"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene20", tactile=(),
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[tuple(v) for v in g["gullies"]],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=20)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["band"], crack=M["band"], patch=M["upper"],
                  patch_cut=M["band"], manhole=M["band"], gully=M["band"],
                  gutter=M["band"], gutter_cover=M["band"],
                  trench=M["band"], trench_frame=M["band"],
                  marking=M["band"], weed=M["grass"], wear=M["curb"],
                  stain_dirt=M["curb"], stain_water=M["curb"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene20 P1 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_flat_fill(M):
        """hazard_stairs=False control: unify upper+stair+lower into flat ground at z=0."""
        sc.skin_exclude(f"{ROOT}/FlatPlaza")     # [W2-0, P-A] The twin gets the same conditions
        u = PARAMS["upper"]
        v = PARAMS["valley"]
        x0, x1 = u["x0"], 20.0
        y0, y1 = -8.0, 8.0
        BOX(f"{ROOT}/FlatPlaza", ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
            (0.0 + v["z_top"]) / 2.0), (x1 - x0, y1 - y0, 0.0 - v["z_top"]),
            M["upper"], col=True)

    # -------------------------------------------------------------------
    # Stair + lower plaza (rot_group 30 deg - boundary stays aligned) + diagonal cue
    # -------------------------------------------------------------------
    def build_diagonal(M):
        # Stair tone unified with the upper plaza_light family (the contrast with the warm lower level is lower's job).
        stair_mtl = M["upper"]
        r = PARAMS["rot"]
        grp = sc.build_rot_group(stage, f"{ROOT}/Diag", r["pivot"], r["deg"])
        # [audit v4 S1] Diagonal extension wedge of the upper plaza - being inside the rotation group,
        # its east face becomes a 30 deg diagonal edge exactly coincident with the stair top edge (local x=0).
        # It overlaps the axis-aligned plaza (x <= -4.5) to form one continuous top face (z=0), so
        #   * A1, the south wedge trench (horizontal gap up to 1.25 m, drop 2.15 m), disappears,
        #   * A2, the north top-step burial (first step up to 0.75 m), disappears -> first step 0.15 m across the full width,
        #   * B1 the tactile strip (local x -0.3..0) and B2 the south railing start (local x -0.4) sit on the ground,
        #   * the drop boundary becomes the whole 30 deg line instead of a single point at the origin, so the scene's character is reinforced.
        # In the overlap both boxes have top 0 / bottom -2.2 with identical material and world-projected
        # texture, so any Z-fighting makes no visible difference on screen.
        wg = PARAMS["wedge"]
        BOX(f"{grp}/UpperWedge",
            ((wg["x0"] + wg["x1"]) / 2.0, 0.0,
             (wg["z_top"] + wg["base_z"]) / 2.0),
            (wg["x1"] - wg["x0"], 2.0 * wg["y_half"],
             wg["z_top"] - wg["base_z"]), M["upper"], col=True)
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{grp}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        # Lower plaza (warm) - a thin slab proud of the grass. Same 30 deg group -> boundary stays aligned.
        lo = PARAMS["lower"]
        lower_mtl = M["lower"] if cfg["cue_material_break"] else M["upper"]
        BOX(f"{grp}/LowerPlaza",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"], lo["thick"]),
            lower_mtl, col=True)

        # Diagonal cue (inside rot_group - rotates along the drop diagonal)
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{grp}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
        if cfg["cue_railing"]:
            sr = PARAMS["stair_rail"]

            def stair_ground(x):
                if x <= 1e-9:
                    return 0.0
                return -st["riser"] * min(max(int(x / st["tread"]) + 1, 1),
                                          st["nsteps"])

            run = st["tread"] * st["nsteps"]
            drop = st["riser"] * st["nsteps"]
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                sc.build_railing_line(
                    stage, f"{grp}/StairRail_{tag}", sgn * sr["y"],
                    sr["x_start"], st["x0"], run, drop, stair_ground,
                    M["rail"], rail_h=sr["rail_h"], post_r=sr["post_r"],
                    spacing=sr["spacing"], rail_r=sr["rail_r"],
                    rail_mid_r=sr["rail_mid_r"],
                    rail_mid_drop=sr["rail_mid_drop"])

        # Lower plaza props (rotation-group local - aligned along the diagonal corridor)
        if cfg["cue_scene_dressing"]:
            lz = lo["z_top"]
            # [v5.1 §2] One row of regulation bollards + dot tactile at the corridor entrance (rot local coordinates)
            lb = PARAMS["lower_bollards"]
            for i, ly in enumerate(lb["ys"]):
                build_bollard_std(M, f"{grp}/LowBollard_{i}", lb["x"], ly, lz,
                                  k=i)
            if cfg["cue_tactile"]:
                bk = lb["block"]
                sc.build_tactile(stage, f"{grp}/Tactile_LowBollard",
                                 bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                                 M["tactile"], z=lz,
                                 proud=PARAMS["tactile"]["proud"])
            for i, (lx, ly, yaw) in enumerate(PARAMS["lower_benches"]):
                sc.build_bench(stage, f"{grp}/LowBench_{i}", lx, ly, lz,
                               M["wood"], yaw=yaw)

    # -------------------------------------------------------------------
    # Dressing - 3 axis-aligned buildings + axis-aligned props (bollard rows, planters, benches,
    #          street lamps, hedges) + mesa entry ramp
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[v5.1 §2] One regulation bollard - height 0.90 m · diameter 0.15 m (r 0.075) +
        white reflective band at the top (width 0.09). Basis: Enforcement Rule of the
        Act on Promotion of Mobility Convenience for the Mobility Impaired, Table 2
        (height 0.8-1.0 · diameter 0.1-0.2 · spacing around 1.5 m · bright reflective band).
        The old sc.build_bollard defaults (r 0.06 · h 0.75) fall short of the regulatory
        minimum, so the dimensions are stated explicitly here (scene_common untouched).
        The body material uses per-instance tint jitter (bollard_0..2) to remove the
        'identical clones' impression."""
        h, r = 0.90, 0.075
        sc.build_bollard(stage, f"{prefix}/Post", cx, cy, bz,
                         mtl=M[f"bollard_{k % 3}"], radius=r, height=h)
        sc.add_cylinder(stage, f"{prefix}/Band", (cx, cy, bz + h - 0.14),
                        r * 1.05, 0.09, M["bollard_band"])

    def build_dressing(M):
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # [v5.1 §2] One row of regulation bollards + dot tactile at the top of the mesa entry ramp
        bl = PARAMS["bollards"]
        for i, by in enumerate(bl["ys"]):
            build_bollard_std(M, f"{ROOT}/Bollard_{i}", bl["x"], by, 0.0, k=i)
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=0.0,
                             proud=PARAMS["tactile"]["proud"])
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (px, py) in enumerate(PARAMS["planters"]):
            sc.build_planter(stage, f"{ROOT}/Planter_{i}", px, py, 0.0,
                             M["curb"], M["grass"], tree_mtls=tree_mtls,
                             size=PARAMS["planter"]["size"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["pole"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly, sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                           0.9, base_z=0.0)
        # Mesa entry ramp (west side, grass -2.15 -> plaza 0). Negative drop = rising towards +X.
        # margin=0, so the top edge is exactly flush with the plaza west face (x=-14, z=0).
        ar = PARAMS["access_ramp"]
        vz = PARAMS["valley"]["z_top"]
        sc.build_slope(stage, f"{ROOT}/AccessRamp", ar["x0"], vz,
                       ar["x1"] - ar["x0"], vz - PARAMS["upper"]["z_top"],
                       ar["y0"], ar["y1"], ar["thick"], M["upper"],
                       margin=0.0, collider=True)

    # [v5.2 user] Arbitrary warning placards removed - build_signs() deleted.

    # -- Scene assembly --
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_upper(M)
        build_diagonal(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)             # [W2-D] Ground elements - after dressing (scatter-order convention)
    # [v5.2 user] Arbitrary warning placards removed - cue_sign placement deleted.

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene20 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["oblique_overview"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene20_{ts}.png")
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
