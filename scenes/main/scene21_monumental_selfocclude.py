# -*- coding: utf-8 -*-
"""
scene21_monumental_selfocclude.py — NegObs synthetic scene 21: government office grand stair (Isaac Sim 4.5)

Type    : T2 monumental entrance grand stair (multi-step self-occlusion)
Spec    : Docs/multi_scene_brief_v3.md §D scene21_monumental_selfocclude + director's addendum
Shared  : scene_common.py (build_railing_line/build_nosing) · scene02 skeleton

Hazard  : Walking forward from the upper terrace (in front of the office facade), the lower 12
          of the grand stair's 18 steps fold behind the top nosing and vanish (multi-step
          self-occlusion). Only the descending railing line and the top 1~2 nosings remain, so
          the 2.7 m drop is hidden. The fittings (railing·nosing·tactile) are complete but
          powerless in a grazing view.
Goal    : Assemble the upper terrace (marble) + a 4-column facade hint + 18 steps + stone
          parapets on both sides + 2 central stainless railing lines + the lower grand plaza +
          2 flagpoles.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene21_monumental_selfocclude.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene21_monumental_selfocclude.py
Smoke (geometry self-verification before boot · early exit):
    NEGOBS_SMOKE=1 python scene21_monumental_selfocclude.py

Coordinates: Z-up, m, travel axis +X (terrace -> descent), drop start x=0. The facade is at -X (behind the top).

Marble (terrace·stair·columns·facade): the scene_common.TEX `marble_light` role (real material).
The lower grand plaza uses `plaza_light`, as in the brief.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - 7 keys. A fully fitted type -> cue_railing/nosing/tactile default True.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> the stair becomes a z=0 flat (only geometry toggle)
    "cue_railing":        True,    # 2 central stainless railing lines (y +-1.3)
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality - default OFF (ablation path kept)    # tactile warning strip at the top approach
    "cue_material_break": True,    # stair marble vs lower plaza plaza_light+band
    "cue_sign":           True,    # [v5 shared layer] 1 sign_info (plaza information)
    "cue_scene_dressing": True,    # column facade·flagpoles·distant buildings
    "cue_nosing":         True,    # [new] nosing strip on every step
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- Grand stair, 18 steps (riser 0.15 -> drop 2.7, tread 0.32 run 5.76, width 8 y +-4) ---
    stairs=dict(x0=0.0, riser=0.15, tread=0.32, nsteps=18,
                y0=-4.0, y1=4.0, z_top=0.0, base_z=-3.2),
    # --- Ground (audit v4 B1: there was no ground prim at all, so the terrace·parapets·buildings
    #     all floated and the terrace flank was an infinite fall). Top face -2.75 = just below the
    #     lower grand plaza top (-2.70) -> a 0.05 m step around the plaza keeps walking continuous.
    ground=dict(cx=14.0, cy=0.0, size_x=110.0, size_y=90.0, z_top=-2.75,
                thick=1.2),
    # --- Stone parapets on both sides (tilted box, width 0.5, top = stair line +0.85) ---
    #     [audit v4 B2] The y band is moved **inside** the stair width (+-3.5..+-4.0) and the
    #     thickness 0.5 -> 1.6. Previously a tilted girder floated in mid-air outside the width (+-4).
    #     Thickness 1.6 -> the underside is z=-0.60 at the top (x=0), 0.45 m below the tread (-0.15),
    #     and -3.30 at the bottom (x=5.76), below the stair base (-3.2) -> grounded over the whole span.
    #     Effective stair width 8 -> 7 m. The drop·step dimensions (hazard geometry) are unchanged.
    #     [v5 verdict applied · critical] The parapet outer face was **exactly coplanar** with the
    #     stair flank (y=+-4.0), so at 200 % crop in oblique a comb of white/stone alternating at the
    #     step pitch (coplanar Z-fighting) ran along the whole bottom of the parapet. out_off pushes
    #     the outer face out by 2 cm (y +-4.02), fixing the depth order. The inner boundary
    #     (y +-3.5)·top face (+0.85)·thickness (1.6) are unchanged, so the grounding·effective stair
    #     width checks (B2) still hold.
    parapet=dict(width=0.5, over=0.85, thick=1.6, out_off=0.02),
    # --- 2 central stainless railing lines (y +-1.3) ---
    railing=dict(ys=(-1.3, 1.3), rail_h=0.9),

    # ═══ [W2-D ground_kit] P1 plaza_granite - spec §5.1 row scene21 ═════════
    #  Row prescription: "axis water staining · plinth soiling · manholes
    #  **2, to the side, off the central axis**"; manhole (-4.0, +-1.0).
    #  ★ Tactile **OFF** (§12.4 identity conflict — hidden illusion). B12
    #    `_inv_hidden_illusion` enforces it for scene21.
    #  ★ The "axis water staining" is carried by a `wear_lane` centred on
    #    y = 0: it is the one element the row explicitly wants **on** the axis,
    #    and unlike the manholes it is a flat 0.6 mm tone band, not an object,
    #    so v5.1 §21 ("remove objects from the central axis") is not violated.
    #  ★ B1 stays 0 at d5 by construction: with the manholes held off-axis at
    #    |y| = 1.0 the disc edge (1.0 + 0.324) is outside the d5 near-window
    #    frame half width (0.577 m at X = 1.0). The identity rule wins over the
    #    frame-fill soft gate; the near window is filled by repair patches.
    gkit=dict(
        region=(-12.0, -4.0, -0.5, 4.0),
        manholes=[(-4.0, 1.0), (-4.0, -1.0)],   # avoids the central axis (v5.1 §21)
        gullies=[(-2.0, -3.6), (-7.0, 3.6)],
        patches=[(-1.25, 0.55), (-3.70, -0.60)],
        axis_stain=((-12.0, 0.0), (-0.85, 0.0)),
    ),
    # --- Upper terrace (marble) : thick 0.5 -> 3.7, making it a stone plinth (base -3.7,
    #     buried 0.95 m below the ground -2.75). Top face z=0 (hazard geometry) unchanged. ---
    #     [v5 verdict applied] x0 −12.0 -> −15.2 : plinth extended to match the facade's move west below.
    #     Top face z=0 · x1=0 (the hazard geometry boundary) unchanged.
    terrace=dict(x0=-15.2, x1=0.0, y0=-9.0, y1=9.0, z_top=0.0, thick=3.7),
    # --- Facade hint: 4 columns (r0.4 h7) + lintel beam + rear facade wall (dark windows) ---
    #     [v5 verdict applied · critical] The entire d10 preset column crushed to black in the
    #     colonnade shadow (foreground mean RGB (23,26,28)). The cause is not the colonnade but the
    #     **8.5 m full-width facade wall** behind it: under the noon sun (elev 49.79 deg, shadow
    #     azimuth 25 deg) a shadow of height h reaches 0.766·h along +X, so the wall (x −10.9, h 8.5)
    #     cast a shadow covering x −10.9..−4.39 wholesale, and the foregrounds of d10 eye (x −10) ·
    #     d5 eye (x −5) both fall entirely inside it.
    #     · Moving the preset origin is impossible - the grid defines eye_x = −d as the distance to
    #       the drop edge (x=0), so a +4 shift would put the d2 eye at x=+2 (inside the stair
    #       solid). So **the shadow source itself is pulled back and the sun bearing is turned**.
    #     · col_x −10.0 -> −13.2 / wall_x −11.2 -> −14.4 (moved 3.2 m west)
    #     · SUN_AZ_OFFSET 171.5 -> 206.5 (shadow azimuth 25 deg -> 60 deg)
    #     -> wall shadow reach x = −14.1 + 0.845·8.5·cos60 deg = −10.51,
    #       colonnade −13.2 + 0.845·7·cos60 deg = −10.24, both behind the bottom of the d10 frame
    #       (x=−9.42 at h0.3, −8.27 at h0.9) -> the foreground crush disappears.
    facade=dict(col_r=0.4, col_h=7.0, col_x=-13.2, col_ys=(-6.0, -2.0, 2.0, 6.0),
                lintel_h=0.8, wall_x=-14.4, wall_t=0.6, wall_h=8.5,
                win_w=1.4, win_h=2.6, win_ys=(-6.0, -2.0, 2.0, 6.0)),
    # --- Lower grand plaza (plaza_light + band_dark) ---
    lower=dict(x1=34.0, y0=-16.0, y1=16.0, z_top=-2.7, thick=0.5),
    # --- 2 flagpoles (slender cylinder h8) ---
    flagpole=dict(r=0.08, h=8.0, xs=(-2.0,), ys=(-7.0, 7.0)),
    # --- 3 distant buildings (horizon closure). base_z=-2.75 = ground top face (if unset the
    #     shell only comes down to z=-1.0 and the whole thing floats - audit v4 B3) ---
    buildings=dict(
        B=dict(x0=36.0, x1=42.0, y0=-14.0, y1=14.0, h=14.0, floors=6,
               axis="x", facade_x=36.0, face_dir=-1.0, base_z=-2.75),
        C=dict(x0=20.0, x1=44.0, y0=18.0, y1=24.0, h=11.0, floors=4,
               axis="y", facade_y=18.0, face_dir=-1.0, base_z=-2.75),
        D=dict(x0=44.0, x1=52.0, y0=-20.0, y1=20.0, h=18.0, floors=6,
               axis="x", facade_x=44.0, face_dir=-1.0, base_z=-2.75),
    ),
    # --- Context dressing (cue_scene_dressing) : "memorial park·city hall grand stair" ---
    # [v5.1 realism] Feedback: "dignity - **remove objects from the central axis**. Dignity comes
    #   from symmetry and emptiness." The old layout stacked (1) the memorial sculpture (x 16, shaft 9 m),
    #   (2) the middle 2 poles of the flagpole row (y +-1.8) and (3) a bollard at (7.5, 0.0) on the
    #   axis (y=0), blocking the preset (+X) vanishing point outright. All three move off the axis.
    #   (1) Memorial -> moved off-axis to the side (24.0, −12.0) + shaft shrunk 9.0 -> 6.5.
    #      (Inside the lower plaza x1 34 · y +-16. 4.00 m from the bench (20,−12),
    #       6.08 m from the streetlight (18,−13), 5.22 m from the flagpole row (19,−10.5))
    monument=dict(x=24.0, y=-12.0, base=3.0, base_h=0.9, shaft=0.9,
                  shaft_h=6.5),
    #   (2) Flagpoles -> 1 row of 6 crossing the axis (y −9..9) -> **2 symmetric side rows**.
    #      y = +-10.5 · x = 10.0 / 14.5 / 19.0 (3 per side). The axis y=0 is left completely empty.
    flagpoles_lower=dict(r=0.08, h=9.0, ys=(-10.5, 10.5),
                         xs=(10.0, 14.5, 19.0)),
    #   (3) Bollards -> the axis-crossing row at the stair foot (x 7.5, y −7..7, spacing 3.5, y=0 included)
    #      is dropped. Per the §2 statutory placement, 1 row at the **north entry of the lower plaza**
    #      (where the service road meets it): y 14.5 · x 8.0..17.0 spacing 1.5 (7 posts) + 0.3 m dot
    #      tactile paving in front of the pedestrian approach face (south). From the grid eyes
    #      (x −2/−5/−10, y 0) the bearing is 37~55 deg, outside the FOV (+-30 deg), and even from oblique(−4,−9) it is 28 m off.
    bollards_lower=dict(y=14.5, xs=(8.0, 9.5, 11.0, 12.5, 14.0, 15.5, 17.0),
                        block=dict(x0=7.7, x1=17.3, y0=14.2, y1=14.5)),
    #   (4) The 4 terrace bollards - deleted as decorative placement with no §2 basis (vehicle entry point).
    benches_lower=[(20.0, -12.0, 90.0), (20.0, 12.0, -90.0),
                   (26.0, -6.0, 180.0), (26.0, 6.0, 180.0),
                   (12.0, -13.0, 0.0), (12.0, 13.0, 0.0)],
    streetlights=[(6.6, -5.2), (6.6, 5.2), (18.0, -13.0), (18.0, 13.0)],
    streetlight=dict(pole_h=5.5, pole_r=0.09, arm_len=0.9, arm_r=0.05,
                     head=0.28),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    tactile=dict(ahead=0.4, proud=0.004),
    # [v5 shared layer] Korean sign - (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   Info(−3.2, −5.4): plaza information board on the upper terrace (x −15.2..0, y +-9, z 0).
    #     3.49 m to the nearest point (0, −4) of the stair top edge (x=0, width y +-4),
    #     3.60 m from the terrace south end (y=−9) - meets the >=0.5 m clearance from hazard geometry.
    #     1.98 m from the flagpole (x −2.0, y −7.0), 2.27 m from the terrace bollard (−1.0, −6.0).
    #   Camera check (grid gy=0, eye x −2/−5/−10, FOV +-30 deg):
    #     −2 -> behind · −5 -> −71.6 deg outside · −10 -> −38.5 deg outside
    #     crown_graze(−3,0) behind · railing_line(−2,1.3) behind ·
    #     oblique(−4,−9) 32.5 deg outside · facade_front(9,0) 23.9 deg (13.3 m distant)
    #     -> 0 occlusion of the self-occlusion judgment area (stair top·railing line).
    signs=[("Info", "sign_info", -3.2, -5.4, 0.0, 180.0, 1.0, 0.75)],

    material=dict(
        scale=dict(marble_light=1.2, plaza_light=1.80, granite_dark=1.0,
                   band_dark=0.5, brick_red=2.0, tactile=0.3, grass=1.4),
        grass_tint=(0.55, 0.68, 0.42),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        window_color=(0.05, 0.07, 0.10), window_rough=0.10,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # [v5.1 §4] parapet 0.90 -> 0.72 (no large pure-white areas)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        pole_color=(0.80, 0.82, 0.85), pole_metallic=0.9, pole_rough=0.30,
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
    # [v5 verdict applied] 171.5 -> 206.5. Shadow horizontal azimuth = atan2(cosφ, −sinφ),
    #   φ = SUN_AZ_OFFSET + 123.5 (= noon_dome_rot −110 + hdri_sun_rotz_offset
    #   233.5). Old value φ=295 deg -> shadow azimuth 25 deg (almost +X, the facade shadow spread
    #   across the terrace); new value φ=330 deg -> 60 deg, halving the shadow's x component.
    #   The dome and DistantLight turn together on the same rot, so HDRI sun consistency is kept.
    #   The −X-facing distant buildings (B·D) lose illuminance (cos component 0.585 -> 0.323), but
    #   silhouette·grounding readability is unaffected, and the −Y-facing building C and the south parapet get brighter.
    SUN_AZ_OFFSET=206.5,

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
# [C] Paths + texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene21")
ASSET_ROLES = ["marble_light", "plaza_light", "granite_dark", "band_dark",
               "brick_red", "tactile", "grass",
               "sign_info", "hdri", "mdl"]              # [v5] sign_info


# ===========================================================================
# [C2] Smoke - geometry self-verification before boot (early exit)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stairs"]
    print("=" * 64)
    print("scene21_monumental_selfocclude — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 64)
    n = st["nsteps"]
    drop = n * st["riser"]
    run = n * st["tread"]
    print(f"  대계단: {n}단 × riser {st['riser']} = 낙차 {drop:.2f} m, "
          f"run {run:.2f} m, 폭 {st['y1']-st['y0']:.1f}")
    # Self-occlusion approximation: how many lower steps fold below the sight line at the top nosing (conceptual)
    print(f"  자기폐색 특색: 상부 테라스 grazing 시 하부 ~12단 소실, "
          f"상단 1~2 단코+난간 하강선 잔존")
    print(f"  파사드: 기둥 {len(PARAMS['facade']['col_ys'])}주 "
          f"(r{PARAMS['facade']['col_r']} h{PARAMS['facade']['col_h']}) + 인방 + 창 다크")
    print(f"  중앙 난간 2선 y={PARAMS['railing']['ys']}, "
          f"파라펫 폭 {PARAMS['parapet']['width']} 상면+{PARAMS['parapet']['over']}")
    print(f"  낙차 검증: {drop:.2f} ≥ 0.3 m → {'OK' if drop >= 0.3 else 'FAIL'}")
    # ── Ground·plinth z ladder (audit v4 T1/T2/B2 fix check) ──
    gr = PARAMS["ground"]
    te = PARAMS["terrace"]
    lo = PARAMS["lower"]
    pa = PARAMS["parapet"]
    ang = math.atan2(drop, run)
    pz0 = st["z_top"] + pa["over"]                    # parapet top face (x=0)
    pb0 = pz0 - pa["thick"] * math.cos(ang)           # parapet underside (x=0)
    pb1 = pb0 - drop                                  # parapet underside (x=run)
    print("  [z 위계]  지반 상면 %.2f / 하부광장 상면 %.2f / 테라스 저면 %.2f"
          % (gr["z_top"], lo["z_top"], te["z_top"] - te["thick"]))
    print("    테라스 기단 매입: %.2f m (저면이 지반 상면 아래) → %s"
          % (gr["z_top"] - (te["z_top"] - te["thick"]),
             "OK" if te["z_top"] - te["thick"] < gr["z_top"] else "FAIL"))
    print("    광장 둘레 단차: %.2f m (지반↔하부광장) → %s"
          % (lo["z_top"] - gr["z_top"],
             "OK" if abs(lo["z_top"] - gr["z_top"]) <= 0.2 else "FAIL"))
    print("    파라펫 y대역 [%.2f,%.2f] (외면 +%.2f 돌출 — 계단 측면 Z파이팅 회피)"
          " ⊂ 계단 폭 [%.1f,%.1f] → %s"
          % (st["y1"] - pa["width"], st["y1"] + pa.get("out_off", 0.0),
             pa.get("out_off", 0.0), st["y0"], st["y1"],
             "OK" if pa["width"] <= (st["y1"] - st["y0"]) / 2.0 else "FAIL"))
    print("    파라펫 밑면 x=0: %.2f (1단 디딤면 %.2f 아래) / x=run: %.2f "
          "(계단 저면 %.2f 아래) → %s"
          % (pb0, -st["riser"], pb1, st["base_z"],
             "OK" if (pb0 < -st["riser"] and pb1 < st["base_z"]) else "FAIL"))
    print("=" * 64)


# ===========================================================================
# [D] Camera presets - 2 central railing lines -> keep gy=0 (symmetry)
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)
    # crown_graze: walking from the terrace - the lower 12 steps self-occlude, only nosings·railing remain
    views["crown_graze"] = dict(eye=[-3.0, 0.0, 0.9], tgt=[7.0, 0.0, -0.4])
    # facade_front: looking up at the facade·columns from the lower plaza (confirms the stair is real)
    views["facade_front"] = dict(eye=[9.0, 0.0, -2.0], tgt=[-9.0, 0.0, 3.0])
    # oblique: oblique high angle
    views["oblique"] = dict(eye=[-4.0, -9.0, 3.5], tgt=[5.0, 0.0, -2.0])
    # railing_line: descending exposure along the railing line
    views["railing_line"] = dict(eye=[-2.0, 1.3, 1.5], tgt=[6.0, 1.3, -1.5])
    return views


# ===========================================================================
# [E] Main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. crown_graze / h0.3 — 하부 12단 자기폐색, 상단 단코·난간 하강선만 잔존하는가
 2. facade_front       — 하부에서 기둥 4주·인방·창 다크(관공서 힌트) 식별
 3. railing_line       — 중앙 스테인리스 난간 2선 하강선
 4. oblique            — 18단·양측 파라펫 실체
 5. 재질/단서          — 대리석·단코·점자·밴드·Z파이팅·부유 없는가
 6. [v4] 지반·테라스 기단·파라펫 계단 위 안착·축선 조형물/깃대 열
 7. [v5] 공통 레이어 — 상단 점자띠 + sign_info(−3.2, −5.4) 판독"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

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
    UsdGeom.Xform.Define(stage, "/World/Scene21")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene21"

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
        M["marble"] = PBR(
            f"{ROOT}/Looks/Marble", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"), sc.tex_path("marble_light", "rough"),
            sca["marble_light"])
        M["plaza"] = PBR(
            f"{ROOT}/Looks/Plaza", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["granite"] = PBR(
            f"{ROOT}/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["window"] = PBR(f"{ROOT}/Looks/Window",
                          diffuse_color=mp["window_color"],
                          roughness_const=mp["window_rough"], metallic=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [v5.1 §2/§4] Materials for the statutory bollard - 3 body variants (tint jitter +-5%) + reflective band.
        #   The band is small in area, so high luminance is allowed (unrelated to the large pure-white ban).
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"bollard_{_i}"] = PBR(
                f"{ROOT}/Looks/Bollard_{_i}",
                diffuse_color=tuple(min(c * _f, 1.0) for c in mp["rail_color"]),
                metallic=mp["rail_metallic"],
                roughness_const=mp["rail_rough"] * (1.0 + 0.05 * (_i - 1)))
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=(0.86, 0.86, 0.84),
                                roughness_const=0.35)
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # Upper terrace + lower grand plaza
    # -------------------------------------------------------------------
    def build_plazas(M):
        # [audit v4 T1] Ground - this single box resolves A3 (infinite fall at the terrace flank)·A4 (void
        # under the free edge of the lower plaza)·B1·B4 at once. Top face -2.75 (0.05 lower than the
        # lower plaza's -2.70 -> the plaza is 0.05 proud, a negligible walking step).
        gr = PARAMS["ground"]
        BOX(f"{ROOT}/Ground",
            (gr["cx"], gr["cy"], gr["z_top"] - gr["thick"] / 2.0),
            (gr["size_x"], gr["size_y"], gr["thick"]), M["grass"], col=True)
        te = PARAMS["terrace"]
        # [W2-0 · P-A] The marble terrace is the ground_kit stage — register
        #   the skin exclusion before BOX (add_box tests it inline).
        sc.skin_exclude(f"{ROOT}/Terrace")
        BOX(f"{ROOT}/Terrace",
            ((te["x0"] + te["x1"]) / 2.0, (te["y0"] + te["y1"]) / 2.0,
             te["z_top"] - te["thick"] / 2.0),
            (te["x1"] - te["x0"], te["y1"] - te["y0"], te["thick"]),
            M["marble"], col=True)
        lo = PARAMS["lower"]
        st = PARAMS["stairs"]
        x0 = st["x0"] + st["nsteps"] * st["tread"]
        BOX(f"{ROOT}/LowerPlaza",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["plaza"] if cfg["cue_material_break"] else M["marble"], col=True)
        for k, xb in enumerate((x0 + 1.0, x0 + 2.0)):
            BOX(f"{ROOT}/LowerBand_{k}",
                (xb, (lo["y0"] + lo["y1"]) / 2.0, lo["z_top"] - 0.02),
                (0.4, lo["y1"] - lo["y0"], 0.06), M["band"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P1 plaza_granite (spec §5.1 row scene21)
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        st = PARAMS["stairs"]
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]),
            z=float(PARAMS["terrace"]["z_top"]), gy=0.0,
            origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene21", tactile=(),
            overrides=dict(extras=(("wear_lane", dict(width=0.90)),)),
            extras_args=dict(wear_lane=dict(centerline=tuple(g["axis_stain"]))),
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[tuple(v) for v in g["gullies"]],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=21)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["band"], crack=M["band"], patch=M["marble"],
                  patch_cut=M["band"], manhole=M["band"], gully=M["band"],
                  gutter=M["band"], gutter_cover=M["band"],
                  trench=M["band"], trench_frame=M["band"],
                  marking=M["band"], weed=M["grass"], wear=M["granite"],
                  stain_dirt=M["granite"], stain_water=M["granite"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene21 P1 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Grand stair, 18 steps (marble)
    # -------------------------------------------------------------------
    def build_stairs(M):
        st = PARAMS["stairs"]
        stair_mtl = M["marble"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    def build_flat_fill(M):
        st = PARAMS["stairs"]
        x1 = st["x0"] + st["nsteps"] * st["tread"]
        BOX(f"{ROOT}/FlatStairs",
            ((st["x0"] + x1) / 2.0, 0.0, st["z_top"] - 0.25),
            (x1 - st["x0"], st["y1"] - st["y0"], 0.5), M["marble"], col=True)

    # -------------------------------------------------------------------
    # Stone parapets on both sides (tilted box, top = stair line +0.85)
    # -------------------------------------------------------------------
    def build_parapets(M):
        st = PARAMS["stairs"]
        pa = PARAMS["parapet"]
        run = st["nsteps"] * st["tread"]
        drop = st["nsteps"] * st["riser"]
        z0 = st["z_top"] + pa["over"]
        # [audit v4 B2] Laid on the 0.5 m band **inside** the stair width (previously: mid-air outside it).
        # [v5 verdict applied] Only the outer face goes out by out_off (2 cm) - clearing the coplanar
        #   Z-fighting (comb pattern) with the stair flank (y=+-4.0). The inner boundary stays +-3.5.
        off = pa.get("out_off", 0.0)
        for tag, y0, y1 in (("N", st["y1"] - pa["width"], st["y1"] + off),
                            ("S", st["y0"] - off, st["y0"] + pa["width"])):
            sc.build_slope(stage, f"{ROOT}/Parapet_{tag}", st["x0"], z0,
                           run, drop, y0, y1, pa["thick"], M["parapet"],
                           collider=True)

    # -------------------------------------------------------------------
    # Facade hint - 4 columns + lintel beam + rear wall (dark windows)
    # -------------------------------------------------------------------
    def build_facade(M):
        fa = PARAMS["facade"]
        # rear facade wall
        BOX(f"{ROOT}/FacadeWall",
            (fa["wall_x"], 0.0, fa["wall_h"] / 2.0),
            (fa["wall_t"], PARAMS["terrace"]["y1"] - PARAMS["terrace"]["y0"],
             fa["wall_h"]), M["marble"], col=True)
        # dark windows (slightly proud of the wall front)
        gx = fa["wall_x"] + fa["wall_t"] / 2.0 + 0.02
        for j, y in enumerate(fa["win_ys"]):
            BOX(f"{ROOT}/FacadeWin_{j}", (gx, y, 4.0),
                (0.05, fa["win_w"], fa["win_h"]), M["window"])
        # 4 columns
        for j, y in enumerate(fa["col_ys"]):
            CYL(f"{ROOT}/Column_{j}", (fa["col_x"], y, fa["col_h"] / 2.0),
                fa["col_r"], fa["col_h"], M["marble"], col=True)
        # lintel beam (cross beam on the column tops)
        BOX(f"{ROOT}/Lintel",
            (fa["col_x"], 0.0, fa["col_h"] + fa["lintel_h"] / 2.0),
            (fa["col_r"] * 2.5,
             PARAMS["terrace"]["y1"] - PARAMS["terrace"]["y0"] - 2.0,
             fa["lintel_h"]), M["marble"], col=True)

    # -------------------------------------------------------------------
    # Dressing - 2 flagpoles + 2 distant buildings
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[v5.1 §2] One statutory bollard - height 0.90 m · diameter 0.15 m (r 0.075) +
        a white reflective band on top (width 0.09). Basis: Enforcement Rule of the Act on
        Promotion of Mobility Convenience for the Mobility Impaired, Table 2 (height 0.8~1.0 ·
        diameter 0.1~0.2 · spacing around 1.5 m · a bright reflective band).
        The old sc.build_bollard defaults (r 0.06 · h 0.75) fall below the statutory minimum, so
        the dimensions are stated here (scene_common is not modified). The body material uses a
        per-instance tint jitter (bollard_0..2) to remove the 'identical copy' impression."""
        h, r = 0.90, 0.075
        sc.build_bollard(stage, f"{prefix}/Post", cx, cy, bz,
                         mtl=M[f"bollard_{k % 3}"], radius=r, height=h)
        sc.add_cylinder(stage, f"{prefix}/Band", (cx, cy, bz + h - 0.14),
                        r * 1.05, 0.09, M["bollard_band"])

    def build_dressing(M):
        fp = PARAMS["flagpole"]
        x = fp["xs"][0]
        for j, y in enumerate(fp["ys"]):
            CYL(f"{ROOT}/Flagpole_{j}", (x, y, fp["h"] / 2.0),
                fp["r"], fp["h"], M["pole"], col=True)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        lz = PARAMS["lower"]["z_top"]                 # -2.70 (lower plaza top face)
        # [v5.1] Memorial sculpture - off-axis to the side (24, −12). The axis (y=0) is left empty.
        mo = PARAMS["monument"]
        BOX(f"{ROOT}/Monument_Base",
            (mo["x"], mo["y"], lz + mo["base_h"] / 2.0),
            (mo["base"], mo["base"], mo["base_h"]), M["marble"], col=True)
        BOX(f"{ROOT}/Monument_Shaft",
            (mo["x"], mo["y"], lz + mo["base_h"] + mo["shaft_h"] / 2.0),
            (mo["shaft"], mo["shaft"], mo["shaft_h"]), M["marble"], col=True)
        # [v5.1] 6 flagpoles - 1 axis-crossing row -> **2 symmetric side rows** (y +-10.5 x 3 poles)
        fl = PARAMS["flagpoles_lower"]
        for j, y in enumerate(fl["ys"]):
            for i, x in enumerate(fl["xs"]):
                CYL(f"{ROOT}/FlagpoleLow_{j}_{i}", (x, y, lz + fl["h"] / 2.0),
                    fl["r"], fl["h"], M["pole"], col=True)
        # [v5.1 §2] 1 row of statutory bollards at the lower plaza north entry + 0.3 m dot tactile paving
        bl = PARAMS["bollards_lower"]
        for j, bx in enumerate(bl["xs"]):
            build_bollard_std(M, f"{ROOT}/BollardLow_{j}", bx, bl["y"], lz,
                              k=j)
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=lz,
                             proud=PARAMS["tactile"]["proud"])
        # [v5.1] The 4 terrace bollards are deleted (decorative placement with no §2 basis)
        for j, (bx, by, yaw) in enumerate(PARAMS["benches_lower"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{j}", bx, by, lz,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for j, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{j}"
            CYL(f"{base}/Pole", (lx, ly, lz + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["pole"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly,
                     lz + sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, lz + sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_signs():
        """[v5 shared layer] Korean signs (sc.build_sign). For the coordinate·camera checks see
        the PARAMS['signs'] comment. The hazard geometry (grand stair) transform is unchanged."""
        back = PBR(f"{ROOT}/Looks/SignBack", diffuse_color=(0.16, 0.17, 0.18),
                   metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = PBR(f"{ROOT}/Looks/Sign{tag}",
                        diff=sc.tex_path(key, "diff"), uv_mode=True,
                        roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    # -------------------------------------------------------------------
    # cue - 2 central railing lines / nosing / top tactile strip (default True)
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        run = st["nsteps"] * st["tread"]
        drop = st["nsteps"] * st["riser"]

        def stair_ground(x):
            if x <= st["x0"]:
                return 0.0
            if x >= st["x0"] + run:
                return -drop
            idx = min(int((x - st["x0"]) / st["tread"]), st["nsteps"] - 1)
            return -st["riser"] * (idx + 1)

        if cfg["cue_railing"]:
            for k, y in enumerate(PARAMS["railing"]["ys"]):
                sc.build_railing_line(
                    stage, f"{ROOT}/Rail_{k}", y, st["x0"] - 0.5, st["x0"],
                    run, drop, stair_ground, M["rail"],
                    rail_h=PARAMS["railing"]["rail_h"])
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"], z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"],
                             z=0.0, proud=tc["proud"])

    # ── Scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_plazas(M)
    if cfg["hazard_stairs"]:
        build_stairs(M)
        build_parapets(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_facade(M)
        build_dressing(M)
    build_ground_kit(M)             # [W2-D] ground elements - after the dressing (scatter order convention)
    if cfg.get("cue_sign"):
        build_signs()               # [v5 shared layer]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["oblique"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene21_{ts}.png")
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
