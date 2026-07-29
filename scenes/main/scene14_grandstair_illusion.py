# -*- coding: utf-8 -*-
"""
scene14_grandstair_illusion.py - NegObs synthetic scene 14: illusory monumental stair (Isaac Sim 4.5)

Type    : T14 Potemkin-style illusory grand stair (40 steps, 3 landings, tapered widening)
Spec    : Docs/multi_scene_brief_v3.md §D scene14_grandstair_illusion + director addendum
Shared  : scene_common.py (build_straight_stairs width_pairs) · scene02 skeleton

Hazard  : Walking forward from the small upper viewing plaza, only the landings of the 40-step
          stair are visible and it is misread as a flat terrace. In reality a 6.0 m drop hides
          between the landings. The perspective illusion of the width opening from upper y+-3 to
          lower y+-5 strengthens the concealment.
Goal    : Assemble the small upper plaza (granite) + 40 steps (3 landings, continuous width_pairs)
          + sloped side parapets + the lower grand plaza (fountain hint) + 2 distant buildings.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene14_grandstair_illusion.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene14_grandstair_illusion.py
Smoke (pre-boot geometry self-verification, early exit):
    NEGOBS_SMOKE=1 python scene14_grandstair_illusion.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0. Total drop 6.0 m.

Marble: the scene_common.TEX `marble_light` role (real material).
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
# [A] SCENE_CONFIG - 7 keys. Only hazard_stairs toggles the hazard geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> stairs/landings become z=0 flat (the one geometry-toggle exception)
    "cue_railing":        False,   # A monumental stair is open-sided - True -> pipe rail on top of the side parapets
    # [v5 shared layer] Urban-practice scenes (01/02/05/13/14/16/20/21) default cue_tactile to True.
    #   The old comment's 'not customary' is void after the v5 setting was clarified (plaza grand stair in front of a city hall / cultural centre) -
    #   tactile paving at the entry of a public-building grand stair is standard domestic practice. Real geometry is generated.
    "cue_tactile":        False,  # [v5.2 user] Tactile paving is rare in reality - default OFF (the ablation path is kept)    # top entry warning tactile band (x −0.4..0, stair upper width)
    "cue_material_break": True,    # False -> the upper and lower plazas become marble too (the boundary is absorbed)
    "cue_sign":           True,    # [v5 shared layer] 1 sign_info (plaza information)
    "cue_scene_dressing": True,    # street lamps · parapet kerb · fountain hint · distant buildings
    "cue_nosing":         False,   # [new] True -> nosing band on every step
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- Grand stair: 40 steps, riser 0.15 (drop 6.0), tread 0.34, 3 landings (depth 2.4) ---
    stairs=dict(x0=0.0, riser=0.15, tread=0.34, nsteps=40, z_top=0.0,
                base_z=-6.7, seg_len=10, landing_depth=2.4,
                w_top=3.0, w_bot=5.0),            # half width: upper y+-3 -> lower y+-5
    landings=(10, 20, 30),                        # landing insertion points (after step n)
    # --- Upper viewing plaza (marble stair head, marble instead of granite) ---
    upper=dict(x0=-9.0, x1=0.0, y0=-8.0, y1=8.0, z_top=0.0, thick=0.5),
    # --- Large upper plaza (director D-14 r3(1)): 20m in -X behind the terrace x y+-20, plaza_light.
    #     So the stair reads as a structure joining two levels (isolation removed). 3 boxes leaving a terrace hole.
    upper_big=dict(x0=-29.0, x1=0.0, y0=-20.0, y1=20.0, z_top=0.0, thick=0.5),

    # ═══ [W2-D ground_kit] P1 plaza_granite - spec §5.1 scene14 row ═══════════
    #  Row prescription: "marble_light module 600 is already correct -> joints
    #  only; stair-head transverse trench; 2 gullies (v1.1); marble water
    #  staining that follows the joints; manhole (-8.7, +1.2)".
    #  Tactile is **OFF** here: §12.4 puts 14 in the hidden-illusion group
    #  (identity conflict). Gate B12 `_inv_hidden_illusion` enforces it, so a
    #  tactile band cannot be introduced by accident from this file.
    #
    #  ★ Trench centre -2.55 -> **-2.59** (this file's correction of the C-1'
    #    figure). C-1' derives the centre from a **0.30 m wide** trench (near
    #    lip -2.40, drow = 16.05 rows @1080 >= 16 at d10). The builder frames
    #    the cover: `build_trench_drain` adds `trench_frame_w` 0.040 on each
    #    side, so the real near lip of a trench centred at -2.55 is -2.36 and
    #    drow(-2.36, 10) = **15.70 < 16 = FAIL** [computed].  Centre -2.59 puts the
    #    frame lip back on -2.40 exactly (16.05 rows). This is the same class
    #    of correction scene13 applied to its entry trench (0.35 -> 0.52).
    #  ★ Gullies: row says `|y| = stair width/2 - 0.40`; `stairs.w_top` is the
    #    half width, so |y| = 3.00 - 0.40 = 2.60 (read from PARAMS, §7.4).
    ground=dict(
        region=(-12.0, -4.0, -0.5, 4.0),      # terrace + west plaza corridor
        trench_x=-2.59,                       # C-1' re-derived on the frame lip
        gully_x=-0.95,                        # stair-head point gullies (C-1')
        gully_inset=0.40,                     # |y| = w_top - inset
        manholes=[(-8.7, 1.2), (-4.5, -1.5)],
        # Near-window (W1) fillers. §2.2: a flat 2 mm repair patch carries the
        # d2/d5 window far better than a manhole disc does (scene15 pilot: a
        # disc at 56 % screen width is near-field monopoly, a patch at 87 % is
        # not, because it is a tone change and not an object).
        patches=[(-1.20, 0.00), (-3.70, 0.60)],
    ),
    streetlight=dict(pole_h=5.0, pole_r=0.06, arm_len=1.0, arm_r=0.04,
                     head=0.25, xs=(-6.0, -14.0, -22.0), ys=(-6.0, 6.0)),
    # --- Lower grand plaza (plaza_lower + band_dark bands) + fountain hint ---
    #     x1 40->75 : ground laid out to the foot of the distant buildings, fixing the 5 m float [B-14-1 critical]
    lower=dict(x1=75.0, y0=-20.0, y1=20.0, z_top=-6.0, thick=0.5),
    # --- Sloped grass banks either side of the stair (director D-14 r3(2)): outside the parapet y+-5.2..+-20, upper->lower ---
    #     thick 0.5->3.0 : fixes the thin plate that appeared to hang in mid air (solid slope massif)
    #     run_ext 3.2   : hides the lower end face (the slope cut wedge) under the lower plaza
    side_slope=dict(y_out=20.0, thick=3.0, run_ext=3.2),
    fountain=dict(cx=30.0, cy=0.0, r_out=3.0, r_in=2.4, h=0.4,
                  nozzles=5, nozzle_r=0.06, nozzle_h=0.5),
    # --- Side parapets (width 0.5) ---
    #     thick 0.4->1.6 : embedded into the stepped shoulder (build_shoulder) over the whole run to remove the float
    #     [v5.1] cap_t : slab thickness of the sloped top haunch (oblique solid) - see the bite check in the
    #       build_parapets docstring (vertical equivalent 1.530 > required 0.43+0.03).
    parapet=dict(width=0.5, z0=0.35, thick=1.6, cap_t=1.4),
    # --- Shoulder outside the stair (replaces the old soffit) - see build_shoulder ---
    shoulder=dict(y_out=5.2, offset=0.03, lap=0.05),
    # --- 5 distant buildings (horizon closure, on the lower plaza - grounded via base_z) ---
    buildings=dict(
        B=dict(x0=42.0, x1=48.0, y0=-14.0, y1=14.0, h=12.0, floors=5,
               axis="x", facade_x=42.0, face_dir=-1.0, base_z=-6.0),
        C=dict(x0=30.0, x1=40.0, y0=13.0, y1=19.0, h=10.0, floors=4,
               axis="y", facade_y=13.0, face_dir=-1.0, base_z=-6.0),
        F=dict(x0=30.0, x1=40.0, y0=-19.0, y1=-13.0, h=9.0, floors=3,
               axis="y", facade_y=-13.0, face_dir=1.0, base_z=-6.0),
        D=dict(x0=56.0, x1=70.0, y0=-19.0, y1=-6.0, h=22.0, floors=7,
               axis="x", facade_x=56.0, face_dir=-1.0, base_z=-6.0),
        E=dict(x0=56.0, x1=70.0, y0=4.0, y1=19.0, h=18.0, floors=6,
               axis="x", facade_x=56.0, face_dir=-1.0, base_z=-6.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    # --- Context dressing (instant read as a monumental plaza) - all combinations of existing builders, owned by cue_scene_dressing ---
    dressing=dict(
        # lower grand plaza (z −6.0)
        trees_low=((24.0, 7.0), (24.0, -7.0), (24.0, 13.0), (24.0, -13.0),
                   (33.0, 10.0), (33.0, -10.0)),
        planters_low=((25.5, 4.0), (25.5, -4.0), (34.5, 4.0), (34.5, -4.0)),
        benches_low=((22.5, 5.0), (22.5, -5.0), (22.5, 10.0), (22.5, -10.0),
                     (22.5, 15.0), (22.5, -15.0)),
        # [v5.1 §2] Bollards - old: 13 units at x 21.6, y −12..12 at 2.0 m even spacing
        #   ((1) an evenly spaced decorative row, (2) **the y=0 unit sits on the stair axis**). Replaced with a compliant layout:
        #   spacing 1.5 m · 10 units symmetric about an empty axis (y=0) = the vehicle barrier line
        #   in front of the stair entry (§2 permitted position). Height/diameter/reflective band: see build_bollard_std.
        #   Dot tactile paving is **deliberately omitted** in this scene - putting an untoggleable yellow
        #   warning band at the stair foot (x 21.6) would mix a permanent cue into this scene's
        #   concealment illusion of 'only the landings show, so it looks flat' (violates cue_tactile toggle integrity).
        bollard_x=21.6,
        bollard_ys=(-6.75, -5.25, -3.75, -2.25, -0.75,
                    0.75, 2.25, 3.75, 5.25, 6.75),
        # [v6 review §3-2] 4 flagpoles - the old x 24.5 · y +-6/+-10 intruded into the foreground of
        #   beauty_overview (eye 28,−14,4 -> tgt 6,0,−2.5, sight-line azimuth 147.5 deg) for **3 rounds
        #   running**. Back-calculation: (24.5,−10) is 5.31 m horizontally from the camera at an azimuth
        #   difference of −16.3 deg (dead centre of the +-30 deg FOV, right of screen), and the flagpole top
        #   z 3.0 sits just below the eye level 4.0, so it ran vertically through the frame and the black flag hid the stair face.
        #   (24.5,−6) is also at the frame boundary, 8.73 m · −33.9 deg.
        #   The review's alternative "move the eye +Y 1.5 m" is **counterproductive** - with eye y −14->−12.5
        #   the azimuth difference of (24.5,−10) goes −16.3 deg -> −5.9 deg, i.e. even closer to centre. So
        #   **relocating the flagpoles** is chosen: flanking the fountain (30, 0, r_out 3.0) at
        #   x 30.0 · y +-7 / +-12 - a flagpole row on the fountain terrace of a monumental plaza (real practice).
        #   Camera check (FOV +-30 deg, vertical half +-18 deg):
        #     beauty_overview : −73.5 deg / −102.5 deg / −63.0 deg / −61.9 deg  = all outside
        #     lower_lookup (eye 26,0 -> tgt 8,0, azimuth 180 deg) : +-119.7 deg / +-108.4 deg, outside
        #     side_reveal (azimuth 42.5 deg) : −13.9 deg (37.6 m) · −7.6 deg (40.2 m), distance only,
        #                               the 2 −Y units are outside at −35.6 deg / −44.2 deg
        #     terrace_read (azimuth 0 deg)   : +-11.6 deg / +-19.4 deg, 34.7~36 m distance (elevation 3.5 deg)
        #     grid preset (eye x −2..−10) : about +-12.3 deg, 32.8 m distance - no effect on the illusion
        #   Clearances : fountain rim 4.0 m · street tree (33,+-10) 3.61 m · planter (34.5,+-4) 5.41 m
        flags=((30.0, 7.0), (30.0, -7.0), (30.0, 12.0), (30.0, -12.0)),
        # upper plaza (z 0)
        trees_up=((-20.0, 14.0), (-20.0, -14.0), (-26.0, 14.0), (-26.0, -14.0)),
        benches_up=((-12.0, 5.0), (-12.0, -5.0), (-20.0, 5.0), (-20.0, -5.0)),
        # [v5.1] Axis cleared - the old (−15.0, 0.0) sat on the centre axis of the upper plaza, so from
        #   lower_lookup (eye 26,0,−5.2) the top of the shaft (z 9.8, elevation 20.1 deg) rose above the
        #   stair ridge line (elevation 11.3 deg) and **blocked the axial vanishing point**.
        #   Moved to the side (y −6.5) - 1.0 m inside hedge S (y −10.5..−9.0), and
        #   3.35 m clear of the benches (−12,−5)/(−20,−5).
        monument=(-15.0, -6.5),
        hedges=(("N", -29.0, 9.0, -9.0, 10.5), ("S", -29.0, -10.5, -9.0, -9.0),
                ("W", -29.0, -9.0, -27.5, 9.0)),
        curb_gap=2.5,                     # half width of the central opening in the upper kerb [A-14-5]
    ),
    # [v5 shared layer] Tactile paving - 0.4 m before the stair top edge (x=0), upper width y +-3.
    #   On the marble terrace (x −9..0, z 0). The hazard geometry (stairs, landings) transform is unchanged.
    tactile=dict(ahead=0.4, proud=0.004),
    # [v5 shared layer] Korean sign - (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   Info(−6.5, −4.2): plaza information plate on the upper marble terrace (x −9..0, y +-8).
    #     6.61 m to the nearest point of the stair top edge (0, −3) - meets the >=0.5 m clearance.
    #     2.0 m east of the upper kerb (x −9.0..−8.5), 1.80 m from the street lamp (−6.0, −6.0).
    #   Camera check (grid gy=0, eye x −2/−5/−10, FOV +-30 deg):
    #     −2/−5 -> behind, −10 -> −50.2 deg (outside the frame)
    #     terrace_read(−4,0) behind · side_reveal(−3,−11) 74.7 deg, outside
    #     lower_lookup(26,0) 7.4 deg (32.8 m distance, behind the stair massif) ·
    #     beauty_overview(28,−14) 16.6 deg (35.9 m distance) -> 0 near-field occlusion
    signs=[("Info", "sign_info", -6.5, -4.2, 0.0, 180.0, 1.0, 0.75)],

    material=dict(
        scale=dict(marble_light=1.2, granite_dark=1.0, plaza_lower=0.7,
                   band_dark=0.5, brick_red=2.0, plaza_light=1.80, grass=1.4,
                   tactile=0.3),                      # [v5 shared layer]
        grass_tint=(0.55, 0.68, 0.42),
        # B-14-5: fixes the high-brightness clustering across the frame - facade 0.56->0.30, parapet 0.90->0.62
        bldg_color=(0.30, 0.30, 0.33), bldg_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.62, 0.62, 0.60), parapet_rough=0.6,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        water_color=(0.05, 0.10, 0.11), water_rough=0.06,
        wood_color=(0.20, 0.14, 0.09),
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
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
# [C] paths + texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene14")
ASSET_ROLES = ["marble_light", "granite_dark", "plaza_lower", "band_dark",
               "brick_red", "plaza_light", "grass",
               "tactile", "sign_info",                # [v5 shared layer]
               "hdri", "mdl"]


# ===========================================================================
# [C2] Widening (width_pairs) - linear interpolation of the half width of every step i(1..n) (continuous across landings)
# ===========================================================================
def _half_width(i, n, w_top, w_bot):
    """Half width of step i (1-based). Linear from i=1->w_top to i=n->w_bot."""
    if n <= 1:
        return w_top
    return w_top + (w_bot - w_top) * (i - 1) / (n - 1)


# ===========================================================================
# [C3] Smoke - pre-boot geometry self-verification (early exit)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stairs"]
    print("=" * 64)
    print("scene14_grandstair_illusion — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 64)
    n = st["nsteps"]
    drop = n * st["riser"]
    run = n * st["tread"]
    nland = len(PARAMS["landings"])
    total_x = run + nland * st["landing_depth"]
    print(f"  계단: {n}단 × riser {st['riser']} = 낙차 {drop:.2f} m")
    print(f"  run(디딤) {run:.2f} + 참 {nland}×{st['landing_depth']} "
          f"= 총 X {total_x:.2f} m")
    print(f"  폭 점증(반폭): 상부 {st['w_top']} → 하부 {st['w_bot']}")
    for i in (1, 10, 20, 30, 40):
        hw = _half_width(i, n, st["w_top"], st["w_bot"])
        print(f"    단 {i:2d}: 반폭 {hw:.3f}  (y ±{hw:.3f}, 전폭 {2*hw:.2f})")
    print(f"  낙차 검증: {drop:.2f} ≥ 0.3 m → {'OK' if drop >= 0.3 else 'FAIL'}")
    # ── level z table (director D-14 r3(4)) ──
    ub = PARAMS["upper_big"]
    lo = PARAMS["lower"]
    z_bot = lo["z_top"] - 0.3
    print("  [레벨 z 표]")
    rows = [
        ("상부 광장(대형) plaza_light", f"x[{ub['x0']},{ub['x1']}] y±{ub['y1']}",
         ub["z_top"]),
        ("상부 테라스(계단머리) marble", "x[-9,0] y±8", PARAMS["upper"]["z_top"]),
        ("계단 상단", "x=0", st["z_top"]),
        ("계단 하단(40단)", f"x={total_x:.2f}", st["z_top"] - drop),
        ("계단 밖 어깨면(단별)", "|y| hw..5.2", "디딤면 -0.03"),
        ("측면 경사 잔디 사면", "y±5.2..±20", "0.0→-6.0"),
        ("하부 대광장 plaza_lower", f"x[..{lo['x1']}] y±{lo['y1']}", lo["z_top"]),
        ("기단 매시프 바닥", "상부 풋프린트", z_bot),
    ]
    for name, ext, z in rows:
        zs = z if isinstance(z, str) else f"{z:+.2f}"
        print(f"    {name:28s} {ext:22s} top z={zs}")
    print("=" * 64)


# ===========================================================================
# [D] camera presets
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)                    # preset_h0.9_d5 = the illusion check point
    # terrace_read: from above, only the landings show so it reads as a flat terrace (h0.9, slight high angle)
    views["terrace_read"] = dict(eye=[-4.0, 0.0, 0.9], tgt=[6.0, 0.0, 0.1])
    # side_reveal: oblique from the side - exposes the real drop
    views["side_reveal"] = dict(eye=[-3.0, -11.0, 3.5], tgt=[9.0, 0.0, -3.0])
    # lower_lookup: looking up at the stair from the lower grand plaza
    views["lower_lookup"] = dict(eye=[26.0, 0.0, -5.2], tgt=[8.0, 0.0, -2.0])
    # beauty_overview: high angle from the lower plaza corner (director D-14(3), d~18/h4 - mise-en-scene band
    #   exception). The full width of 40 steps + 3 landings + the upper terrace in one frame.
    views["beauty_overview"] = dict(eye=[28.0, -14.0, 4.0], tgt=[6.0, 0.0, -2.5])
    return views


# ===========================================================================
# [E] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. terrace_read / preset_h0.9_d5 — 참만 보여 평탄 테라스로 읽히는가 (은폐 착시)
 2. h0.3·d5~10                    — 낙차 6.0이 grazing 에서 완전 소실되는가
 3. side_reveal                   — 측면에서 40단·참 3개 실체 확인
 4. lower_lookup                  — 하부 대광장·분수 힌트·건물 지평
 5. 재질                          — 폭 점증 tapered 연속·Z파이팅·부유 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene14")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene14"

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
        M["marble"] = PBR(
            f"{ROOT}/Looks/Marble", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"), sc.tex_path("marble_light", "rough"),
            sca["marble_light"])
        M["granite"] = PBR(
            f"{ROOT}/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["plaza_lower"] = PBR(
            f"{ROOT}/Looks/PlazaLower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), sca["plaza_lower"])
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["plaza_light"] = PBR(
            f"{ROOT}/Looks/PlazaLight", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["bldg"] = PBR(f"{ROOT}/Looks/Bldg", diffuse_color=mp["bldg_color"],
                        roughness_const=mp["bldg_rough"], metallic=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [v5.1 §2/§4] Materials for the compliant bollards - 3 body variants (tint jitter +-5%) + reflective band.
        #   The reflective band is small in area, so high luminance is allowed (unrelated to the ban on large pure-white areas).
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"bollard_{_i}"] = PBR(
                f"{ROOT}/Looks/Bollard_{_i}",
                diffuse_color=tuple(min(c * _f, 1.0) for c in mp["rail_color"]),
                metallic=mp["rail_metallic"],
                roughness_const=mp["rail_rough"] * (1.0 + 0.05 * (_i - 1)))
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=(0.86, 0.86, 0.84),
                                roughness_const=0.35)
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        # dressing trees (dark constant colour, 0.02~0.06 convention)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=0.85)
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=1.0, specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=1.0, specular_level=0.0)
        # [v5 shared layer] dot tactile paving (yellow) - diff+nor only (no rough)
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"), None,
                           mp["scale"].get("tactile", 0.3))
        return M

    # -------------------------------------------------------------------
    # Grand stair - 40 steps split into 4 sections by 3 landings. width_pairs keeps the widening continuous across each landing.
    # -------------------------------------------------------------------
    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        n = st["nsteps"]
        wt, wb = st["w_top"], st["w_bot"]
        landings = list(PARAMS["landings"])
        # Section bounds (global step index): [0,10,20,30,40] -> 4 sections of 10 steps each
        bounds = [0] + landings + [n]
        x_cur = st["x0"]
        z_cur = st["z_top"]
        for si in range(len(bounds) - 1):
            i0, i1 = bounds[si], bounds[si + 1]     # global steps [i0+1 .. i1]
            wp = []
            for gi in range(i0 + 1, i1 + 1):
                hw = _half_width(gi, n, wt, wb)
                wp.append((-hw, hw))
            sc.build_straight_stairs(
                stage, f"{ROOT}/Stairs_{si}", x_cur, -wt, wt,
                st["riser"], st["tread"], i1 - i0, st["base_z"], stair_mtl,
                z_top=z_cur, collider=True, width_pairs=wp)
            x_cur += (i1 - i0) * st["tread"]
            z_cur -= (i1 - i0) * st["riser"]
            # Insert a landing (none after the last section)
            if si < len(bounds) - 2:
                hw = _half_width(i1, n, wt, wb)      # landing width = step width at that point
                xa, xb = x_cur, x_cur + st["landing_depth"]
                BOX(f"{ROOT}/Landing_{si}",
                    ((xa + xb) / 2.0, 0.0, (z_cur + st["base_z"]) / 2.0),
                    (xb - xa, 2 * hw, z_cur - st["base_z"]), stair_mtl, col=True)
                x_cur = xb

    def _profile():
        """Stair profile: lists (kind, x_a, x_b, representative z, global step index) per section.
        With kind='step', z is that step's tread; with 'land' it is the landing top face. It uses the
        same accumulation as build_stairs, so it reproduces exactly the same coordinates as the stair body."""
        st = PARAMS["stairs"]
        n = st["nsteps"]
        bounds = [0] + list(PARAMS["landings"]) + [n]
        rows = []
        x_cur, z_cur = st["x0"], st["z_top"]
        for si in range(len(bounds) - 1):
            i0, i1 = bounds[si], bounds[si + 1]
            for gi in range(i0 + 1, i1 + 1):
                xa = x_cur + (gi - i0 - 1) * st["tread"]
                z = z_cur - (gi - i0) * st["riser"]
                rows.append(("step", xa, xa + st["tread"], z, gi))
            x_cur += (i1 - i0) * st["tread"]
            z_cur -= (i1 - i0) * st["riser"]
            if si < len(bounds) - 2:
                rows.append(("land", x_cur, x_cur + st["landing_depth"],
                             z_cur, i1))
                x_cur += st["landing_depth"]
        return rows

    def build_shoulder(M):
        """**Shoulder massif** outside the stair - replaces the old `build_soffit` (a single sloped slab).

        [audit A-14-1/2/3 critical] The old soffit top face was a **single plane** z = −0.3 − 0.2885x.
        It crossed the section-1 stair line (z = −0.441x) at x = 1.967, so from x>1.967 the soffit
        rose above the stair and buried the last 4~5 steps of section 1 (+0.219 @x=3.4); section 2
        had 1 step buried from x>8.905. Conversely at the landing ends (x=5.8/11.6/17.4) it sat
        0.47/0.65/0.82 m below the stair, creating a full-length longitudinal trench outside the stair width (|y| hw..5.2).
        (Audit D5 recommended 'splitting into 4 sheets by section', but a sloped slab leaves a wedge
         cavity with an open flank at each section joint because of the rotateY cut face -> the method below was adopted.)

        New structure: **2 axis-aligned boxes per step** (the +-Y side bands) are laid over the same x
        range as the stair, with their top face set to that step's tread −offset(0.03). The landing sections are identical.
          · stair edge -> shoulder level difference = a uniform 0.03 m throughout (old: a 0.13~0.82 m trench)
          · stair burial 0 (there is no point at which the shoulder can rise above the stair, by construction)
          · only vertical boxes are used, so no cut wedge cavity occurs
          · the first level difference from the upper terrace (z 0) down to shoulder step 1 (−0.18) is 0.18 < the 0.2 criterion
        The stair/landing (hazard geometry) transform is **unchanged** - the illusion (terrace_read) is preserved."""
        st = PARAMS["stairs"]
        sh = PARAMS["shoulder"]
        n, yb = st["nsteps"], sh["y_out"]
        off, lap = sh["offset"], sh["lap"]
        for k, (kind, xa, xb, z, gi) in enumerate(_profile()):
            hw = _half_width(gi, n, st["w_top"], st["w_bot"])
            y_in = max(hw - lap, 0.0)              # bite lap under the stair
            top = z - off
            for tag, y0, y1 in (("N", y_in, yb), ("S", -yb, -y_in)):
                BOX(f"{ROOT}/Shoulder_{kind}{k}_{tag}",
                    ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                     (top + st["base_z"]) / 2.0),
                    (xb - xa, y1 - y0, top - st["base_z"]),
                    M["marble"], col=True)

    def build_side_slopes(M):
        """Sloped grass banks either side of the stair (director D-14 r3(2)): from outside the shoulder
        (y+-5.2) to the site edge (y+-20), sloping from the upper plaza (z0) to the lower plaza (-6.0). Removes the stair's isolation.
        A thick 3.0 solid + run_ext hides the lower cut face under the lower plaza."""
        st = PARAMS["stairs"]
        ss = PARAMS["side_slope"]
        total_x = st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        drop = st["nsteps"] * st["riser"]
        run = total_x + ss["run_ext"]
        drop_ext = drop * run / total_x           # extend the lower end while keeping the pitch
        yb = PARAMS["shoulder"]["y_out"]          # 5.2 (outside the shoulder / parapet)
        for tag, y0, y1 in (("N", yb, ss["y_out"]), ("S", -ss["y_out"], -yb)):
            sc.build_slope(stage, f"{ROOT}/SideSlope_{tag}", st["x0"], -0.05,
                           run, drop_ext, y0, y1, ss["thick"], M["grass"],
                           margin=0.0, collider=True)

    def build_flat_fill(stair_mtl):
        """hazard_stairs=False control: flattens the stair footprint to z=0."""
        st = PARAMS["stairs"]
        x1 = st["x0"] + st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        BOX(f"{ROOT}/FlatStairs",
            ((st["x0"] + x1) / 2.0, 0.0, st["z_top"] - 0.25),
            (x1 - st["x0"], 2 * st["w_bot"], 0.5), stair_mtl, col=True)

    # -------------------------------------------------------------------
    # Upper viewing plaza (granite) + lower grand plaza (plaza_lower + bands)
    # -------------------------------------------------------------------
    def build_plazas(M):
        up = PARAMS["upper"]
        ub = PARAMS["upper_big"]
        lo = PARAMS["lower"]
        z_bot = lo["z_top"] - 0.3                   # plinth floor (slightly below the lower plaza)
        pl_bot = ub["z_top"] - ub["thick"]          # underside of the upper slab = plinth top (-0.5)
        # ── Whole-plinth massif for the upper level (director D-14(1)(2)): the large upper plaza + terrace footprint,
        #    filled solid down to z_bot (marble side walls) - removes the float of the upper level.
        BOX(f"{ROOT}/UpperPlinth",
            ((ub["x0"] + ub["x1"]) / 2.0, (ub["y0"] + ub["y1"]) / 2.0,
             (z_bot + pl_bot) / 2.0),
            (ub["x1"] - ub["x0"], ub["y1"] - ub["y0"], pl_bot - z_bot),
            M["marble"], col=True)
        # ── Large upper plaza (plaza_light) - 3 boxes leaving the terrace hole (x up.x0..0, y up.y0..y1)
        #    empty (the terrace fills it, no coplanar overlap).
        cz = ub["z_top"] - ub["thick"] / 2.0
        # [W2-0 · P-A] Register the ground_kit stages **before** the BOX calls —
        #   `add_box` evaluates `_skin_wanted` on the spot, so a later call is
        #   too late. Without this the flush kit elements (joint tone plates
        #   +0.6 mm, manhole +-10 mm, trench cover -2 mm) are swallowed by the
        #   displacement skin, whose crown is +6.5..16.5 mm [spec §1.1].
        sc.skin_exclude(f"{ROOT}/UpperPlazaW", f"{ROOT}/UpperPlazaS",
                        f"{ROOT}/UpperPlazaN", f"{ROOT}/UpperPlaza")
        BOX(f"{ROOT}/UpperPlazaW",              # west: x0..up.x0, full width
            ((ub["x0"] + up["x0"]) / 2.0, (ub["y0"] + ub["y1"]) / 2.0, cz),
            (up["x0"] - ub["x0"], ub["y1"] - ub["y0"], ub["thick"]),
            M["plaza_light"], col=True)
        BOX(f"{ROOT}/UpperPlazaS",              # south: up.x0..0, y0..up.y0
            ((up["x0"] + ub["x1"]) / 2.0, (ub["y0"] + up["y0"]) / 2.0, cz),
            (ub["x1"] - up["x0"], up["y0"] - ub["y0"], ub["thick"]),
            M["plaza_light"], col=True)
        BOX(f"{ROOT}/UpperPlazaN",              # north: up.x0..0, up.y1..y1
            ((up["x0"] + ub["x1"]) / 2.0, (up["y1"] + ub["y1"]) / 2.0, cz),
            (ub["x1"] - up["x0"], ub["y1"] - up["y1"], ub["thick"]),
            M["plaza_light"], col=True)
        # ── Marble terrace (stair head) - fills the hole
        BOX(f"{ROOT}/UpperPlaza",
            ((up["x0"] + up["x1"]) / 2.0, (up["y0"] + up["y1"]) / 2.0,
             up["z_top"] - up["thick"] / 2.0),
            (up["x1"] - up["x0"], up["y1"] - up["y0"], up["thick"]),
            M["marble"], col=True)
        # lower grand plaza
        st = PARAMS["stairs"]
        x0 = st["x0"] + st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        BOX(f"{ROOT}/LowerPlaza",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["plaza_lower"], col=True)
        # 2 charcoal bands (emphasise the plaza boundary at the stair foot)
        for k, xb in enumerate((x0 + 1.0, x0 + 2.0)):
            BOX(f"{ROOT}/LowerBand_{k}",
                (xb, (lo["y0"] + lo["y1"]) / 2.0, lo["z_top"] - 0.02),
                (0.4, lo["y1"] - lo["y0"], 0.06), M["band"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P1 plaza_granite (spec §5.1 scene14 row)
    #   Drop edge = stair head x=0 (PARAMS["stairs"]["x0"], §7.4 single source).
    #   The x=0 contraction joint is dropped automatically by
    #   `_edge_guard_ticks` (GT-E2). Tactile stays empty: scene14 is a
    #   hidden-illusion scene, gate B12 refuses a tactile element here.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["ground"]
        st = PARAMS["stairs"]
        wy = float(st["w_top"]) - float(g["gully_inset"])      # 3.00-0.40=2.60
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]), z=float(st["z_top"]),
            gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene14", tactile=(),
            overrides=dict(infra=dict(manhole=2, gully=2, trench=1)),
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[(float(g["gully_x"]), -wy),
                              (float(g["gully_x"]), wy)],
                       trench=[(float(g["trench_x"]),
                                -float(st["w_top"]), float(st["w_top"]))],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=14)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # Dark cast-iron / charcoal bindings. Defect D5 (w2_pilot §7) is that
        # B9 gates a *declared* albedo while the scene binds whatever it likes —
        # so bind band_dark/granite_dark, never marble, to the metal parts.
        M2.update(joint=M["band"], crack=M["band"], patch=M["marble"],
                  patch_cut=M["band"], manhole=M["band"], gully=M["band"],
                  trench=M["band"], trench_frame=M["band"],
                  gutter=M["band"], gutter_cover=M["band"],
                  marking=M["band"], weed=M["grass"],
                  stain_dirt=M["granite"], stain_water=M["granite"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene14 P1 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Side sloped parapets (build_slope, width 0.5, marble) - both sides of the stair
    # -------------------------------------------------------------------
    def _rake_segments():
        """[v5.1] The **polyline** of the parapet top haunch - alternating section (rake) / landing (level).
        Returns: (kind, x_a, x_b, z_a, z_b). The end z of a rake equals the z of the next landing
        exactly, and the landing z equals the start z of the next rake, so **the joints have 0 level difference**.
        z is the **nosing line** at that x (the line joining the front edges of the riser tops)."""
        st = PARAMS["stairs"]
        n = st["nsteps"]
        bounds = [0] + list(PARAMS["landings"]) + [n]
        out = []
        x_cur, z_cur = st["x0"], st["z_top"]
        for si in range(len(bounds) - 1):
            nst = bounds[si + 1] - bounds[si]
            xa, za = x_cur, z_cur
            x_cur += nst * st["tread"]
            z_cur -= nst * st["riser"]
            out.append(("rake", xa, x_cur, za, z_cur))
            if si < len(bounds) - 2:
                xa = x_cur
                x_cur += st["landing_depth"]
                out.append(("land", xa, x_cur, z_cur, z_cur))
        return out

    def build_parapets(M):
        """Side parapets - [v5.1 realism] **stepped balustrade -> sloped solid top haunch**.

        Feedback: "stairs are good. Remove the stepping (stepped parapet) of the white railings on both sides."
        The old implementation followed the shoulder profile exactly, so the top face made a
        **stair-shaped silhouette** of 40 steps + 3 landings (two white saw-tooth lines flanking the
        grand stair). The side wall (haunch) of a real monumental stair is not stepped but a polyline of
        **straight rakes per section, level only at the landings**. It is rebuilt in two layers:

          (1) Body - per-step boxes (old structure kept). But the top face is lowered to be **level**
             with the shoulder (z − offset) so it disappears from the silhouette completely.
             (The 86 shoulder boxes can stay - the shoulder itself is floor outside the stair
              and makes no upper silhouette.)
          (2) Haunch - a `sc.build_slope` oblique slab per section + a level box over each landing.
             Top face = nosing line + rail_h(0.95). z is continuous at the joints -> **an oblique line with 0 level difference**.

        Check that the haunch always sits on the body (0 gap):
          · rake thickness cap_t=1.4 (vertical equivalent 1.4/cos(23.83 deg) = 1.530)
          · the nosing line is at most riser(0.15) above that step's tread -> the haunch underside is at most
            z_step + 0.15 + 0.95 − 1.530 = z_step − 0.430
          · body top face = z_step − offset = z_step − 0.03
          -> the underside is always at least 0.40 m **below** the body top face -> bite over the whole run.
        Effective railing height (relative to the shoulder) = 0.95 ~ 1.10 m - the guarding performance is better than the old one too.
        The stair/landing (hazard geometry) transform is unchanged.

        ── [v6 review §3-1] Sealing the wedge slits at the joints ──────────────────────────
        The v6 RT observed a dark triangular slit 3~6 px wide at each of the 3 landings (left x~310/740/935,
        right symmetric) in a 400 % crop of `lower_lookup`. **The cause is not the '+-Y jog from the
        widening (3.0->5.0)' that the review assumed** - the parapet band y is (w_bot+0.05, +width),
        constant over the whole run, so there is no Y jog at all.

        The real cause is that the end face of the `sc.build_slope` oblique slab is **perpendicular to the
        slope**. The top face length is hypot(run,drop) + margin, so the end face has its top edge
        protruding downhill by margin/2 and, going down through the thickness cap_t, it **retreats
        uphill by cap_t·sin(ang)**. That is, the downhill end of the rake thins into a triangular wedge
        close to height rail_h:
          ang = atan(0.15/0.34) = 23.830 deg, sin = 0.4042, cos = 0.9147
          end face bottom x = x_b + margin/2·cos − cap_t·sin
                      = x_b + 0.027 − 0.566 = x_b − 0.538
        The landing haunch box starts at x_b (a vertical end face), so under the end face the range
        x ∈ [x_b−0.538, x_b] is **empty** (below it there is only the body top face ~ z_step−0.03 -> a
        triangular cavity up to 0.9 m high). The fixlog's "joint delta z = 0.0" check only looked at the
        top face z, so it could not catch this in-plane gap.

        Seal (review fix (1)) - extend the landing haunch box uphill by lap:
          lap = cap_t·sin(ang) + 0.15 = 0.566 + 0.15 = 0.716 m  (> the 0.538 needed)
        The extension keeps the landing top face height (z_a + rail_h), and at the same x the rake top
        face is z_a + rail_h + (x_a − x)·tan(ang), i.e. **always higher** -> the extension is completely
        buried inside the oblique slab and makes no silhouette. The burial condition also holds:
          the extension top face must be above the rake underside (top face − 1.530), so
          lap·tan(ang) = 0.716 x 0.4419 = 0.316 < 1.530  ✓
        The +-Y faces of the extension are exactly coplanar with, share the normal of and use the same
        material as the +-Y faces of the oblique slab, so even with Z-fighting the shading difference is 0.

        The opposite joint (landing -> rake) has no gap in the first place, because the uphill end of the
        rake digs cap_t·sin + margin/2·cos = 0.594 m into the landing box.

        The same defect exists at both ends of the polyline and is sealed together:
          · Head end (x=0, upper terrace) - the v6 [remaining] item "white triangular mass at the lower
            end of the left/right haunches in terrace_read" is this wedge. Replaced with a newel box.
          · Toe end (bottom of the stair) - replaced with a vertical end-cap box.
        Both are at |y| >= 5.05, outside the stair width (w_bot 5.0) -> hazard geometry and illusion unchanged."""
        st = PARAMS["stairs"]
        pa = PARAMS["parapet"]
        sh = PARAMS["shoulder"]
        yb = st["w_bot"] + 0.05                     # 5.05 - just outside the maximum lower width
        rail_h = pa["z0"] + 0.6                     # 0.95 m (effective height above the nosing line)
        bands = (("N", yb, yb + pa["width"]),
                 ("S", -yb - pa["width"], -yb))
        # [v6] setback of the oblique slab end face (perpendicular to the slope) + margin = plan overlap lap
        _ang = math.atan2(st["riser"], st["tread"])
        lap = pa["cap_t"] * math.sin(_ang) + 0.15   # 0.716 m
        # (1) Body - top face level with the shoulder (old: +rail_h -> stair silhouette)
        for k, (kind, xa, xb, z, gi) in enumerate(_profile()):
            top = z - sh["offset"]
            for tag, y0, y1 in bands:
                BOX(f"{ROOT}/Parapet_{kind}{k}_{tag}",
                    ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                     (top + st["base_z"]) / 2.0),
                    (xb - xa, y1 - y0, top - st["base_z"]),
                    M["parapet"], col=True)
        # (2) Top haunch - oblique (sections) + horizontal (landings), 0 level difference at the joints · plan overlap lap
        segs = _rake_segments()
        for j, (kind, xa, xb, za, zb) in enumerate(segs):
            for tag, y0, y1 in bands:
                if kind == "rake":
                    sc.build_slope(
                        stage, f"{ROOT}/ParapetHaunch_{j}_{tag}",
                        xa, za + rail_h, xb - xa, za - zb, y0, y1,
                        pa["cap_t"], M["parapet"], margin=0.06,
                        collider=True)
                else:
                    # [v6] Extend uphill by lap -> fills the triangular cavity under the end
                    #      face of the preceding oblique slab (the extension is buried inside the oblique slab).
                    x_a2 = xa - lap
                    top = za + rail_h
                    BOX(f"{ROOT}/ParapetHaunch_{j}_{tag}",
                        ((x_a2 + xb) / 2.0, (y0 + y1) / 2.0,
                         (top + st["base_z"]) / 2.0),
                        (xb - x_a2, y1 - y0, top - st["base_z"]),
                        M["parapet"], col=True)
        # [v6] Seal the wedges at both ends of the polyline - head newel + toe end cap
        x_head, z_head = segs[0][1], segs[0][3]          # (0.0, z_top)
        x_toe, z_toe = segs[-1][2], segs[-1][4]          # lowest nosing end
        for tag, y0, y1 in bands:
            # Head newel: a lap x width x rail_h solid on the upper terrace (z_top).
            #   Its top face matches the top of the oblique slab (z_head + rail_h) exactly -> continuous shoulder.
            top_h = z_head + rail_h
            bot_h = st["z_top"] - 0.30                    # embedded into the terrace slab
            BOX(f"{ROOT}/ParapetNewel_{tag}",
                ((x_head - lap / 2.0), (y0 + y1) / 2.0, (top_h + bot_h) / 2.0),
                (lap, y1 - y0, top_h - bot_h), M["parapet"], col=True)
            # Toe end cap: closes the end of the lowest oblique slab with a vertical face.
            top_t = z_toe + rail_h
            BOX(f"{ROOT}/ParapetEndCap_{tag}",
                ((x_toe - lap / 2.0), (y0 + y1) / 2.0,
                 (top_t + st["base_z"]) / 2.0),
                (lap, y1 - y0, top_t - st["base_z"]), M["parapet"], col=True)

    # -------------------------------------------------------------------
    # Dressing - 2 street lamps + parapet kerb (behind the upper plaza) + fountain hint + distant buildings
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[v5.1 §2] 1 compliant bollard - height 0.90 m · diameter 0.15 m (r 0.075) +
        a white reflective band on top (width 0.09). Basis: Enforcement Rule of the Act on Promotion
        of Mobility Convenience for the Mobility Impaired, Table 2 (height 0.8~1.0 · diameter 0.1~0.2 ·
        spacing about 1.5 m · bright reflective band).
        The old sc.build_bollard defaults (r 0.06 · h 0.75) fall below the statutory minimum, so the
        dimensions are stated explicitly here (scene_common is not modified). The body material uses a
        per-instance tint jitter (bollard_0..2) to remove the 'identical clones' impression."""
        h, r = 0.90, 0.075
        sc.build_bollard(stage, f"{prefix}/Post", cx, cy, bz,
                         mtl=M[f"bollard_{k % 3}"], radius=r, height=h)
        sc.add_cylinder(stage, f"{prefix}/Band", (cx, cy, bz + h - 0.14),
                        r * 1.05, 0.09, M["bollard_band"])

    def build_dressing(M):
        """Context dressing - the read word is "monumental plaza". All combinations of existing builders/primitives.
        The old inventory was a single fountain on a 40x40 lower plaza, which scored emptiness 5/5."""
        dr = PARAMS["dressing"]
        z_lo = PARAMS["lower"]["z_top"]                # -6.0 (lower plaza top face)
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        # Street lamps 3x2 (upper plaza) - the extended xs create the plaza axis
        sl = PARAMS["streetlight"]
        for jx, x in enumerate(sl["xs"]):
            for j, y in enumerate(sl["ys"]):
                base = f"{ROOT}/Streetlight_{jx}_{j}"
                CYL(f"{base}/Pole", (x, y, sl["pole_h"] / 2.0),
                    sl["pole_r"], sl["pole_h"], M["pole"], col=True)
                for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                    ax = x + sgn * sl["arm_len"] / 2.0
                    CYL(f"{base}/Arm_{tag}", (ax, y, sl["pole_h"] - 0.1),
                        sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                    hx = x + sgn * sl["arm_len"]
                    BOX(f"{base}/Head_{tag}", (hx, y, sl["pole_h"] - 0.15),
                        (sl["head"], sl["head"], 0.12), M["lamp"])
        # Parapet kerb behind the upper plaza - 2 boxes leaving a central opening of 2*curb_gap [A-14-5]
        #   The old structure was width 0.5 x height 0.5 blocking the full y −8..8, so entering the terrace
        #   meant stepping over a 0.5 m kerb.
        up = PARAMS["upper"]
        g = dr["curb_gap"]
        for tag, y0, y1 in (("S", up["y0"], -g), ("N", g, up["y1"])):
            BOX(f"{ROOT}/UpperCurb_{tag}",
                (up["x0"] + 0.25, (y0 + y1) / 2.0, 0.25),
                (0.5, y1 - y0, 0.5), M["parapet"], col=True)
        # Fountain: 2-tier basin + shallow water + nozzles (softens the old 'paddling pool') [B-14-4]
        fo = PARAMS["fountain"]
        CYL(f"{ROOT}/FountainRingO", (fo["cx"], fo["cy"], z_lo + fo["h"] / 2.0),
            fo["r_out"], fo["h"], M["parapet"], col=True)
        CYL(f"{ROOT}/FountainRingM",
            (fo["cx"], fo["cy"], z_lo + fo["h"] * 0.75),
            fo["r_in"] + 0.35, fo["h"] * 1.5, M["parapet"], col=True)
        CYL(f"{ROOT}/FountainWater",
            (fo["cx"], fo["cy"], z_lo + fo["h"] / 2.0 + 0.01),
            fo["r_in"], fo["h"] + 0.02, M["water"])
        for k in range(fo["nozzles"]):
            a = 2.0 * math.pi * k / fo["nozzles"]
            CYL(f"{ROOT}/FountainNozzle_{k}",
                (fo["cx"] + 1.4 * math.cos(a), fo["cy"] + 1.4 * math.sin(a),
                 z_lo + fo["h"] + fo["nozzle_h"] / 2.0),
                fo["nozzle_r"], fo["nozzle_h"], M["parapet"])
        # ── Lower grand plaza: street trees · planters · benches · bollards · flagpoles ──
        for k, (cx, cy) in enumerate(dr["trees_low"]):
            sc.build_tree(stage, f"{ROOT}/TreeLow_{k}", cx, cy, z_lo, *tree_mtls)
        for k, (cx, cy) in enumerate(dr["planters_low"]):
            sc.build_planter(stage, f"{ROOT}/PlanterLow_{k}", cx, cy, z_lo,
                             M["parapet"], M["grass"], size=3.0)
        for k, (cx, cy) in enumerate(dr["benches_low"]):
            sc.build_bench(stage, f"{ROOT}/BenchLow_{k}", cx, cy, z_lo,
                           M["parapet"], yaw=90.0)
        for k, by in enumerate(dr["bollard_ys"]):      # [v5.1 §2] compliant bollards
            build_bollard_std(M, f"{ROOT}/BollardLow_{k}",
                              dr["bollard_x"], by, z_lo, k=k)
        for k, (cx, cy) in enumerate(dr["flags"]):
            CYL(f"{ROOT}/FlagPole_{k}", (cx, cy, z_lo + 4.5), 0.09, 9.0,
                M["rail"], col=True)
            BOX(f"{ROOT}/Flag_{k}", (cx + 0.02, cy + 0.6, z_lo + 8.2),
                (0.03, 1.2, 0.8), M["band"])
        # ── Upper plaza: monument + hedge border + street trees and benches ──
        mx, my = dr["monument"]
        BOX(f"{ROOT}/MonumentBase", (mx, my, 0.4), (3.0, 3.0, 0.8),
            M["marble"], col=True)
        BOX(f"{ROOT}/MonumentShaft", (mx, my, 3.8), (1.6, 1.6, 6.0),
            M["marble"], col=True)
        for tag, x0, y0, x1, y1 in dr["hedges"]:
            sc.build_hedge(stage, f"{ROOT}/Hedge_{tag}", x0, y0, x1, y1, 0.9)
        for k, (cx, cy) in enumerate(dr["trees_up"]):
            sc.build_tree(stage, f"{ROOT}/TreeUp_{k}", cx, cy, 0.0, *tree_mtls)
        for k, (cx, cy) in enumerate(dr["benches_up"]):
            sc.build_bench(stage, f"{ROOT}/BenchUp_{k}", cx, cy, 0.0,
                           M["parapet"], yaw=90.0)
        # 5 distant buildings (horizon closure) - grounded on the lower plaza via bd["base_z"]=-6.0 [B-14-1]
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["bldg"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # -------------------------------------------------------------------
    # cues - nosing / railing (OFF by default)
    # -------------------------------------------------------------------
    def build_signs():
        """[v5 shared layer] Korean sign (sc.build_sign). For the coordinate and camera checks see the
        PARAMS['signs'] comment. The hazard geometry (stairs, landings) transform is unchanged."""
        back = PBR(f"{ROOT}/Looks/SignBack", diffuse_color=(0.16, 0.17, 0.18),
                   metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = PBR(f"{ROOT}/Looks/Sign{tag}",
                        diff=sc.tex_path(key, "diff"), uv_mode=True,
                        roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_cues(M):
        st = PARAMS["stairs"]
        # [v5 shared layer] Tactile paving - the path that was only reserved becomes real geometry.
        #   ahead(0.4) m in front of the top edge (x=0), a band of the stair upper width (y +-w_top).
        #   Proud 4 mm above the marble terrace top face (z=0) - the stair transform is unchanged.
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             -st["w_top"], st["w_top"], M["tactile"],
                             z=st["z_top"], proud=tc["proud"])
        if cfg["cue_nosing"]:
            # Approximate nosing band ignoring the landings (based on a continuous 40 steps - representative marking)
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], -st["w_top"], st["w_top"],
                st["riser"], st["tread"], st["nsteps"], z_top=st["z_top"])
        if cfg["cue_railing"]:
            pa = PARAMS["parapet"]
            sh = PARAMS["shoulder"]
            run = st["nsteps"] * st["tread"] \
                + len(PARAMS["landings"]) * st["landing_depth"]
            drop = st["nsteps"] * st["riser"]
            segs = _rake_segments()
            rail_h = pa["z0"] + 0.6

            def para_ground(x):
                """[v5.1] Haunch top face (= nosing line + rail_h) - the landing surface for the rail posts.
                Instead of the old stepped top face it interpolates the rake/level polyline directly."""
                for kind, xa, xb, za, zb in segs:
                    if x < xb:
                        t = 0.0 if xb <= xa else (max(x, xa) - xa) / (xb - xa)
                        return za + (zb - za) * t + rail_h
                return segs[-1][4] + rail_h

            for sgn in (1.0, -1.0):
                sc.build_railing_line(
                    stage, f"{ROOT}/Rail_{'N' if sgn > 0 else 'S'}",
                    sgn * (st["w_bot"] + 0.3), st["x0"] - 0.5, st["x0"],
                    run, drop, para_ground, M["rail"], rail_h=0.9)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["marble"]
    if not cfg["cue_material_break"]:
        # Material boundary removed: the plazas are marble too (code path - plazas are separate, so only the stair is kept)
        stair_mtl = M["marble"]

    build_plazas(M)
    if cfg["hazard_stairs"]:
        build_shoulder(M)           # shoulder massif outside the stair (old soffit) - before the stair
        build_side_slopes(M)        # sloped grass banks either side of the stair (isolation removed)
        build_stairs(stair_mtl)
        build_parapets(M)
        build_cues(M)
    else:
        build_flat_fill(stair_mtl)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)             # [W2-D] ground elements - after the dressing (scatter order convention)
    if cfg["cue_sign"]:
        build_signs()               # [v5 shared layer]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene14_{ts}.png")
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
