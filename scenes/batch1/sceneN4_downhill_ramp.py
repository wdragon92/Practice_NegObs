# -*- coding: utf-8 -*-
"""
sceneN4_downhill_ramp.py - NegObs synthetic scene 24: downhill gentle ramp (Isaac Sim 4.5)

Type    : N4 hard negative - a walkable gentle slope (5%) · **GT = "no drop" on every pixel**
Spec    : Docs/nanobanana_batch1_geometry_map.md §A sceneN4_downhill_ramp
Look ref: look_refs/n4_ramp.jpg (a 4 m wide straight road between concrete retaining walls)
Shared  : scene_common.py (build_slope / add_box / dressing and lighting harness)

Hazard (counter-example): a composition where the road surface disappears downward out of view
          and the two retaining walls converge invites the false positive "end of road = drop".
          But the real geometry is a 5% (1:20) gentle slope - drivable and walkable, and there is
          **no drop anywhere**. It is the counter-example of the S1 (roadside departure) branch
          and the standalone version of T21 (ramp-vs-stair contrast pair).
Goal    : Entry flat (x<0) -> 5% slope over 30 m (drop 1.5) -> flat landing -> horizon closed by
          distant ground, trees and buildings. Concrete retaining walls on both sides (1.6 m above
          the road) follow the slope.

GT rule  : No drop (0 on every pixel). **The site descends at 5% together with the road** so that no
          level difference appears behind the walls (they are not retaining walls but free-standing
          guard walls on a slope).
          -> No real vertical drop exists anywhere in the frame. The mise-en-scene shots are also
          framed only from inside the corridor so they do not break this invariant.

────────────────────────────────────────────────────────────────────────────
[v6 context dressing] Answers the "emptiness" finding of audit v4 - make it read as "where am I".
  (1) Road material correction: the concrete_floor texture is warm (ochre) and read as a dirt track
     in the r1 render -> apply road_tint (0.80,0.86,0.94) to cool it to neutral grey concrete.
     (Texture mean R:G:B ~ 1:0.89:0.74 -> a fully neutralising tint would be (0.74,0.83,1.00).
      Real concrete looks natural slightly warm, so only 70% is corrected = residual ratio 1:0.96:0.87)
     + transverse expansion joints (4 m spacing, width 0.06, proud 0.001) confirm it as a 'paved ramp'.
  (2) 1 guardrail line on top of each wall - build_railing_line, follows the slope + extends over the
     flat landing. Fills the empty upper area (bare sky/wall face) and confirms it as a walkway.
  (3) 3 street lamps - placed **only on the -Y (south) grass**. Given the sun azimuth the shadows fall
     only toward −Y, so new shadows on the road are **0** (§check). The arms reach out over the
     corridor, giving the urban rhythm of 'roadway/sidewalk lighting'.
  (4) 3 plates on the wall face (south side = the sunlit face) + 1 information sign at the entry (Korean texture).
  (5) Entry bollards 2 -> 4 (2 rows) - rhythm at the pedestrian entry.
  (6) 2 distant low-rise buildings (L1·L2) - h5.0/4.2 roofs laid in front of the existing distant
     building F (h12) to form skyline tiers. Placed by calculation at x·y that keep them inside the
     corridor view angle (small |y|) and unoccluded by the walls.
  (7) GT invariant: every new element is an object standing on the ground - no new vertical drop, opening or level difference.
────────────────────────────────────────────────────────────────────────────

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN4_downhill_ramp.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneN4_downhill_ramp.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneN4_downhill_ramp.py

Coordinates: Z-up, m, travel axis +X, slope start (crest) = x=0.
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
# [A] SCENE_CONFIG - standard 7 keys.
#     The scene has no drop, so the hazard_stairs key is redefined as the **signature-element (slope) toggle**.
# ===========================================================================
SCENE_CONFIG = {
    # False -> remove the slope, z=0 flat throughout (retaining wall height constant). The one geometry-toggle exception.
    "hazard_stairs":      True,
    # The retaining wall itself is the guard - if True, add a 'single continuous pipe' (no posts) on top of the wall.
    # [v6] When the context dressing is on, the proper guardrail (posts + top/mid rails) already stands at the
    #      same y·z, so the cue rail is skipped to avoid duplication (coaxial cylinders = Z-fighting).
    #      -> the cue rail only appears in pure-geometry shots with cue_scene_dressing=False.
    "cue_railing":        False,
    "cue_tactile":        False,  # not customary - code path reserved only
    "cue_material_break": True,   # True -> asphalt on the entry flat vs concrete on the slope
                                  # False -> concrete throughout (the slope-start boundary disappears)
    "cue_nosing":         False,  # [optional] no stairs - key reserved only
    "cue_sign":           False,  # [optional] not implemented - key reserved only
    "cue_scene_dressing": True,   # bollards and distant trees/hedges/buildings together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- Slope: run 30 · drop 1.5 -> 5.0% (1:20). Crest x=0, landing x=30 ---
    ramp=dict(x0=0.0, run=30.0, drop=1.5, y0=-2.0, y1=2.0, thick=0.6),
    # --- Entry flat (x<0): the start section for walking continuity (lesson 9) ---
    approach=dict(x0=-14.0, x1=0.02, z_top=0.0, thick=0.6),
    # --- Flat landing + lower plain (slope end z=-1.5) ---
    landing=dict(x0=29.98, x1=60.0, z_top=-1.5, thick=0.6),
    # --- Retaining wall (guard wall): wall_h above the road, thickness t, inner face y=+-y_in ---
    wall=dict(y_in=2.0, thick=0.35, wall_h=1.6, depth=3.2, x_end=45.0),
    # --- Site: grass outside the corridor. **Descends 5% exactly like the road** (0 level difference behind the wall) ---
    ground=dict(half_y=60.0, x_w=-60.0, x_e=130.0, thick=1.0),
    # --- Distance (horizon closure) ---
    far=dict(hedge_x=72.0, hedge_h=1.8, hedge_len=30.0,
             hedge_cys=(-30.0, 0.0, 30.0),
             tree_x=80.0, tree_cys=(-16.0, 0.0, 16.0),
             ridge=dict(x0=100.0, x1=118.0, y0=-60.0, y1=60.0, h=6.0)),
    buildings=dict(
        # Blocks the frontal (+X) vista - facade on the -X plane. Top face z = -1.5+12 = 10.5
        # -> +5.8 deg from the camera (h0.9, x-5) (above the horizon) -> sky exposure verified as blocked.
        F=dict(x0=90.0, x1=98.0, y0=-16.0, y1=16.0, h=12.0, floors=4,
               axis="x", facade_x=90.0, face_dir=-1.0, base_z=-1.5),
        # [v6-(6)] 2 low-rise roofs - a skyline tier beyond the landing.
        #   Because of the occlusion wedge made by the retaining wall (h1.6, x_end 45), anything at large |y|
        #   is fully hidden: the sight line must be above the wall top at the x where it crosses y=+-2.0.
        #   L1 (y 4..10, x 62..70): the sight line crosses y=2 at x~30.5 -> wall top there is
        #     z=0.1, sight line z=2.45 -> not occluded (check OK).
        #   L2 (y −12..−5, x 56..64): crosses y=−2 at x~21.8, wall top 0.51,
        #     sight line z=1.82 -> not occluded.
        #   Both sit in front of F (top 10.5), the distant sky closure, so they open no gap of sky.
        L1=dict(x0=62.0, x1=70.0, y0=4.0, y1=10.0, h=5.0, floors=2,
                axis="x", facade_x=62.0, face_dir=-1.0, base_z=-1.5),
        L2=dict(x0=56.0, x1=64.0, y0=-12.0, y1=-5.0, h=4.2, floors=1,
                axis="x", facade_x=56.0, face_dir=-1.0, base_z=-1.5),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    # --- Props ---
    # ── Bollards [v6-(5) -> v5.1 §2 · ctx2] 2 rows at the ramp entry (x<0 flat) ──────────
    #   Old: y=+-1.55 (spacing 3.10 m) · h0.75 · no reflective band / dot tactile paving.
    #   New: spec h0.90·φ0.12 + white reflective band on top + 0.3 m dot tactile paving on the
    #   front face (−X = the pedestrian approach side). **Re-spaced to about 1.5 m**: y=+-0.80
    #     · bollard<->bollard 1.60 m  · bollard<->wall inner face (y=+-2.0) 1.20 m
    #     Both are in the "about 1.5 m" band, and the largest opening 1.60 m < car width (1.8 m),
    #     so it also works as a vehicle barrier.
    #   * Signature-preservation check (_dressing_report measured, hFOV60/vFOV36):
    #     −0.9 row |yaw| = 37.1 deg (h0.3_d2) / 34.6 deg (h0.9_d2) / 31.3 deg (h1.8_d2)
    #       -> all outside the 30 deg frame half-angle. h1.8_d2 has only 1.3 deg of horizontal margin, but
    #         at el −36.4 deg it is **well outside the 18 deg vertical half-angle**, so it is doubly safe.
    #         h0.9_d2 is still 32.2 deg > 30 deg after subtracting the silhouette half-angle (0.06/1.43 = 2.4 deg).
    #     The −3.6 row is at |yaw| ~ 150 deg at d2 = behind the camera.
    #     Even from ramp_head (eye −1.0) it is off screen at |yaw| 79.5 deg.
    #     The dot tactile plates are further out (|yaw| 43.9~52.0 deg) -> no interference with the judged elements.
    #     They only enter the frame at d5·d10, and the ray-cast occlusion of the vanishing line (x >= 20) is
    #     0 cases · nearest in frame 1.67 m, so the check passes.
    #   * The central 1.6 m is completely empty, so the walk axis and the judging sight line are untouched.
    bollards=[dict(cx=-0.9, cy=-0.80), dict(cx=-0.9, cy=0.80),
              dict(cx=-3.6, cy=-0.80), dict(cx=-3.6, cy=0.80)],
    bollard=dict(r=0.06, h=0.90, front=(-1.0, 0.0)),

    # --- [v6-(2)] Guardrail on top of the retaining wall (both sides, follows the road slope) ---
    #   Ground function = wall top z = road_z(x) + wall_h. The flat landing section (x 30..44.9) is a
    #   local parallel extension (post rhythm 2.75 kept, duplicate post at x=30 avoided).
    guard=dict(rail_h=0.95, post_r=0.022, rail_r=0.028, rail_mid_r=0.016,
               rail_mid_drop=0.42, spacing=2.75, x_land_end=44.9),
    # --- [v6-(3)] 3 street lamps: on the -Y (south) grass. Shadows go only to −Y -> 0 effect on the road ---
    streetlight=dict(pole_h=4.6, pole_r=0.07, arm_len=1.30, arm_r=0.04,
                     head=0.24, y=-2.90),
    streetlights=[4.0, 15.0, 26.0],
    # --- [v6-(4)] Wall plates (south inner face = the sunlit face). proud toward +Y from y=−2.0 ---
    wall_plates=[dict(x=9.0), dict(x=18.0), dict(x=27.0)],
    wall_plate=dict(w=0.55, h=0.38, t=0.03, z_off=1.05,
                    face_w=0.42, face_h=0.26, face_t=0.012),
    # --- [v6-(4)] 1 entry information sign (Korean texture, faces -X) ---
    #   With yaw=180 the plate width (w) spreads along the **Y axis**: y 1.13..1.91
    #   -> 0.09 clear of the wall inner face (y=2.0) (no penetration), stays within the road (|y|<2).
    #   x=−4.2: d2·d5·ramp_head·beauty are behind/outside the FOV; at d10 it is frontal at yaw 14.7 deg.
    entry_sign=dict(x=-4.2, y=1.52, yaw=180.0, pole_h=2.30, pole_r=0.045,
                    w=0.78, h=0.78),
    # --- [v6-(1)] Road expansion-joint transverse lines (flat plates proud 0.001, follow the slope) ---
    joints=dict(x0=4.0, x1=44.0, step=4.0, w=0.06, proud=0.001),

    # ═══ [W2 ground_kit] P8 ramp_road - spec §5.8 N4 row ════════════════════
    #  Prescription: L-shaped gutters 300 on both sides (y=+-1.85) · gully · 2 edge lines ·
    #        individual cracks (breaks the texture repeat) · low-point patch · tyre/dirt stains · weeds.
    #  * **Placed only on the flat entry section (x −14…0).** `plan_ground` builds the whole plan
    #    at a single z (`z_fn` is not consumed yet) while this scene's road
    #    descends 5 % for x>0 - a z=0 element laid on the slope would float
    #    0.30 m at x=6 `[computed - road_z(6) = −0.30]`. Elements on the slope section are
    #    handled by the expansion-joint transverse lines the scene already has (they follow the slope).
    #  * The "ramp_crest" in `edges` is **not a GT drop but a grade change point**.
    #    This scene is a hard negative (drop 0 on every pixel). There are only two reasons to
    #    declare the crest an edge: (1) to pull surface elements 0.8 m clear ahead of the crest and
    #    prevent silhouette contamination (§6.2 GT-E1′), and (2) to keep the beyond-the-crest
    #    visibility judgement (`beyond_grade`) in the plan.
    #    Grade = drop/run = 1.5/30 = 0.050 -> compared with the ray slope h/d,
    #    d2(0.150)·d5(0.060) visible · **d10(0.030) hidden** `[computed]`.
    gkit=dict(
        region=(-14.0, -2.0, 0.0, 2.0),
        #  3 patches = 1 each for the d2/d5/d10 near window (W1). The corridor half width is only
        #  0.46 m at X=0.8 m, so |y| <= 0.4 is needed to stay in frame `[computed]`.
        patches=[(-1.20, 0.00), (-3.80, 0.30), (-8.80, -0.30)],
        #  Gully - 1 just before the crest (blocks inflow onto the slope) + 1 at the entry.
        #  `lid=True` fixed (no-open-hole convention); it is flush so the GT-E1′ clearance is 0 ✔.
        gullies=[(-1.20, -1.70), (-7.00, 1.70)],
        #  2 edge lines - the length is derived by the plan from the corridor (max 6.0 m).
        edge_lines=[(-11.0, -1.60, 0.0), (-11.0, 1.60, 0.0)],
        tactile_depth=0.60, tactile_setback=0.30,
        tactile_row_x=-3.6,             # first bollard row on the pedestrian approach side (−X)
    ),

    material=dict(
        scale=dict(concrete_floor=0.9, concrete_wall=1.2, grass=1.4),
        grass_tint=(0.55, 0.68, 0.42),
        wall_tint=(0.92, 0.92, 0.90),                 # bright exposed concrete
        # [v6-(1)] Road cooling tint - removes the warm (ochre) cast of concrete_floor. Fixes the dirt-track misread.
        road_tint=(0.80, 0.86, 0.94),
        joint_color=(0.055, 0.055, 0.058),            # joints (within the dark sRGB convention)
        joint_rough=0.92,
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.85,
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        # ─ Bollard v5.1 fittings: white reflective band on top (0.08 m² each) + dot tactile paving in front ─
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        parapet_color=(0.90, 0.90, 0.87), parapet_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        brick_tint=(0.80, 0.80, 0.82),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [v6] dressing constant colours
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        sign_color=(0.045, 0.085, 0.19), sign_rough=0.55,   # sign navy background
        sign_face=(0.58, 0.59, 0.56),                       # plate face (lettering area)
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
    # ─── SUN_AZ_OFFSET: 171.5 (default) -> **81.5**. Rationale:
    #     sun world az ~ 33.5 + offset = 115 deg (shadow az = az−180 = 295 deg).
    #     shadow vector ~ (cos295, sin295) = (+0.42, −0.91), length =
    #     wall_h/tan(elev 49.79°) = 1.6/1.181 = 1.355 m
    #     -> the +Y wall shadow covers the road only from y=2.0 to y=0.77, a width of 1.23 m
    #        (31% of the 4.0 road width - meets the requirement of "an azimuth where the two wall
    #         shadows do not fully cover the road"). The other 69% stays in direct light -> road texture and slope shading kept.
    #     [v6 new-element shadow check] shadow displacement (per height h) = (+0.3577h, −0.7675h).
    #       · Street lamps (y=−2.90, h<=4.60): pole shadow y <= −2.90 -> **outside the road (|y|<=2.0)**.
    #         The arm end/head (y=−1.60, h=4.45~4.50) also gives y = −1.60−3.42 = −5.02 ->
    #         off the road.  => new road shadow area **0** (no effect on the vanishing-line section).
    #       · Entry sign (y=+1.52, plate top z 2.25): shadow y = 1.52−1.73 = −0.21,
    #         x −4.2 -> −3.4. Of that, y 0.77..1.52 is already in the wall shadow band -> the net gain is
    #         only a thin 0.98-wide strip on the **entry flat (x<0)** - no effect on the slope section.
    #       · Guardrail (pipe r0.028, on the wall top): 1~2 solid lines of shadow ~0.03 m wide
    #         fall inside the existing wall shadow band (y 0.77..2.0).
    #       · Wall plates (proud 0.03): projected only onto their own wall face, never reaching the road.
    #     Re-sweepable in the GUI with the [ ] keys (15 deg step). ───
    SUN_AZ_OFFSET=81.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN4")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "grass", "brick_red",
               "sign_info", "hdri", "mdl"]


# ===========================================================================
# [C1] Road longitudinal profile - aligns the landing z of dressing elements to the road/site.
#      (The site descends on the same profile, so the grass z outside the wall uses the same function)
# ===========================================================================
def tactile_band_rect():
    """[W2 §12.5 (2)] **Continuous dot tactile band** in front of the bollard row (x0, y0, x1, y1).

    The front is −X (the pedestrian approach side), so the band sits setback away from the bollard
    front face toward −X and runs for depth. There are 2 rows, but the statutory subject is the
    single **row the pedestrian meets first** (x = tactile_row_x) - the (scene, site) registration
    in §12.4 is likewise a single "bollard" site. The coordinates are derived from PARAMS (§7.4).
    """
    g, bo = PARAMS["gkit"], PARAMS["bollard"]
    ys = [b["cy"] for b in PARAMS["bollards"]
          if abs(b["cx"] - g["tactile_row_x"]) < 1e-6]
    sb, dp, r = g["tactile_setback"], g["tactile_depth"], bo["r"]
    x_face = float(g["tactile_row_x"]) - r
    return (x_face - sb - dp, min(ys) - 0.20, x_face - sb, max(ys) + 0.20)


def ground_plans():
    """[W2 ground_kit] Ground plan - the scene assembly and the CPU check use the same function."""
    g = PARAMS["gkit"]
    rp = PARAMS["ramp"]
    grade = float(rp["drop"]) / float(rp["run"])
    gp = gk.plan_ground(
        "ramp_road", region=tuple(g["region"]),
        z=float(PARAMS["approach"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("ramp_crest", float(rp["x0"]), dict(beyond_grade=grade))],
        dists=(2, 5, 10), scene="sceneN4",
        tactile=("bollard",) if SCENE_CONFIG["cue_scene_dressing"] else (),
        sites=dict(gully=[tuple(p) for p in g["gullies"]],
                   patch=[tuple(p) for p in g["patches"]],
                   marking=[tuple(m) for m in g["edge_lines"]],
                   tactile=dict(bollard=tactile_band_rect())),
        #  The 6 gully sites are based on the full 30 m ramp length. On the 14 m entry flat
        #  2 units at 22 m spacing is the cap `[spec 20~25 m each]`.
        overrides=dict(infra=dict(gully=2, gutter_L=2,
                                  marking=("line", "line")),
                       surface=(("patch", 3), ("crack", 6),
                                ("stain", ("tire", "dirt")), ("weed", 4))),
        seed=24)
    return [("approach", gp)]


def road_z(x, drop):
    rp = PARAMS["ramp"]
    if x <= rp["x0"]:
        return 0.0
    if x >= rp["x0"] + rp["run"]:
        return -drop
    return -drop * (x - rp["x0"]) / rp["run"]


# ===========================================================================
# [C2] Geometry self-verification report (pure maths - printed on the SMOKE early exit)
# ===========================================================================
def _geometry_report():
    rp = PARAMS["ramp"]
    ap = PARAMS["approach"]
    ld = PARAMS["landing"]
    wl = PARAMS["wall"]
    grade = rp["drop"] / rp["run"]
    ang = math.degrees(math.atan2(rp["drop"], rp["run"]))
    print("-" * 64)
    print("[기하] sceneN4 자기검증")
    print(f"  경사: run {rp['run']:.1f} · drop {rp['drop']:.2f} → "
          f"{grade * 100:.1f}% ({ang:.2f}°)  폭 {rp['y1'] - rp['y0']:.1f} m")
    print(f"  보행 연속성: 진입 [{ap['x0']:.1f},{ap['x1']:.2f}] z=0 → "
          f"경사 [0,{rp['run']:.1f}] z 0→{-rp['drop']:.2f} → "
          f"착지 [{ld['x0']:.2f},{ld['x1']:.1f}] z={ld['z_top']:.2f}")
    print(f"    이음 겹침: 진입/경사 {ap['x1'] - rp['x0']:+.3f} m, "
          f"경사/착지 {rp['x0'] + rp['run'] - ld['x0']:+.3f} m "
          f"(쐐기 틈 방지 ≥0.02 · 상면이 서로 교차 발산 → Z-파이팅 없음)")
    # Wall top (follows the road) - handled by a single build_slope, with no stepped segment approximation
    print(f"  옹벽: 내면 y=±{wl['y_in']:.2f} 두께 {wl['thick']:.2f} · "
          f"상단 = 노면 +{wl['wall_h']:.2f} 일정 (build_slope 1개 = 계단식 근사 불요)")
    print(f"    상단 z: x=0 {wl['wall_h']:+.2f} → x={rp['run']:.0f} "
          f"{wl['wall_h'] - rp['drop']:+.2f} · 하단 z {-wl['depth'] + wl['wall_h']:+.2f}"
          f" (노면 아래 {wl['depth'] - wl['wall_h']:.2f} m 매입 → 부유 없음)")
    # Sight-line check: is the road vanishing line below the horizon + horizon closure
    print("  [시선 검산] 카메라 h=0.9 · 노면 소실선 = atan(-grade) = "
          f"{-math.degrees(math.atan(grade)):+.2f}° → 지평선(0°) 아래 OK")
    bd = PARAMS["buildings"]["F"]
    btop = bd["base_z"] + bd["h"]
    for ex in (-2.0, -5.0, -10.0):
        h = 0.9
        a_end = math.degrees(math.atan2(ld["z_top"] - h, ld["x1"] - ex))
        a_bld = math.degrees(math.atan2(btop - h, bd["x0"] - ex))
        print(f"    eye x={ex:6.1f}: 착지끝 {a_end:+.2f}° / 원경건물 상단 "
              f"{a_bld:+.2f}° → 하늘 노출 {'차단 OK' if a_bld > 0 else 'FAIL'}")
    print("  [GT] 전 픽셀 '낙차 없음' — 대지도 노면과 동일 5% 하강, "
          "옹벽 뒤 단차 0, 개구 없음")
    print("-" * 64)


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene shots (all inside the corridor)."""
    views = sc.grid_views(0.0)
    # ramp_head: just before the crest - the false-positive composition where the road vanishes downward (signature)
    views["ramp_head"] = dict(eye=[-1.0, 0.0, 0.9], tgt=[12.0, 0.0, -0.5])
    # wall_run: mid-slope, the composition where one wall's shadow covers part of the road
    views["wall_run"] = dict(eye=[6.0, -1.2, 0.6], tgt=[26.0, 0.6, -1.2])
    # landing_lookback: looking back from the landing - continuous as an uphill (proof it is walkable)
    views["landing_lookback"] = dict(eye=[33.0, 0.0, 0.9], tgt=[16.0, 0.0, 0.1])
    # beauty_overview: oblique high angle (above the corridor interior) - the impression of the slope unfolding
    views["beauty_overview"] = dict(eye=[-6.0, -1.7, 3.0], tgt=[16.0, 0.4, -1.0])
    return views


# ===========================================================================
# [D2] Camera check (v6 context dressing) - pure maths. Printed on SMOKE.
#   Isaac default camera: focal 18.14756 / horiz aperture 20.955 -> hFOV 60.0 deg,
#   1920x1080 -> vFOV = 2·atan(tan30 deg·9/16) = 36.0 deg. Half-angles 30 deg / 18 deg.
#   Judgement: (1) in every view, does a new prim avoid a near collision with the camera (<0.6 m)
#         (2) if it enters the frame, does it avoid occluding the road vanishing line (low centre angle)
# ===========================================================================
HFOV_HALF = 30.0
VFOV_HALF = 18.0


def _cam_angles(view, p):
    """(yaw_rel deg, elev_rel deg, dist, in_frame) - exact transform relative to the camera optical axis."""
    ex, ey, ez = view["eye"]
    tx, ty, tz = view["tgt"]
    fx, fy, fz = tx - ex, ty - ey, tz - ez
    yaw = math.atan2(fy, fx)
    pitch = math.atan2(fz, math.hypot(fx, fy))
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    u = dx * math.cos(yaw) + dy * math.sin(yaw)
    v = -dx * math.sin(yaw) + dy * math.cos(yaw)          # camera left +
    u2 = u * math.cos(pitch) + dz * math.sin(pitch)
    w2 = -u * math.sin(pitch) + dz * math.cos(pitch)
    yaw_r = math.degrees(math.atan2(v, u2))
    elev_r = math.degrees(math.atan2(w2, math.hypot(u2, v)))
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    inf = (u2 > 0.0 and abs(yaw_r) <= HFOV_HALF and abs(elev_r) <= VFOV_HALF)
    return yaw_r, elev_r, dist, inf


def _road_hit(eye, p, drop, t_max=40.0, step=0.02):
    """Extend the eye->p sight line past p (t>1) and return the (x,y) where it meets the road top face.
    Road = |y| <= 2.0, x in [approach.x0, landing.x1], z = road_z(x).
    None if there is no hit. (A hit means the prim occludes the road pixel at that point.)"""
    ap, ld = PARAMS["approach"], PARAMS["landing"]
    rp = PARAMS["ramp"]
    ex, ey, ez = eye
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    t = 1.0
    prev = None
    while t <= t_max:
        x = ex + dx * t
        y = ey + dy * t
        z = ez + dz * t
        on = (abs(y) <= rp["y1"]) and (ap["x0"] <= x <= ld["x1"])
        cur = (z - road_z(x, drop)) if on else None
        if cur is not None and prev is not None and prev > 0.0 >= cur:
            return (x, y)
        prev = cur
        t += step
    return None


def streetlight_xs():
    """[v5.1 §3] Deterministic +-0.3 m jitter on the street lamp x - removes the 11 m even-spacing look.
    y(=−2.90) is **fixed**: it must not break the lighting-check premise that the shadows run only
    to −Y and contribute 0 to the road, nor the functional condition that the arm (+Y 1.30) reaches over the corridor."""
    return [x + bc.jit_scalar(x, PARAMS["streetlight"]["y"], "slN4",
                              -0.30, 0.30)
            for x in PARAMS["streetlights"]]


def wall_plate_xs():
    """[v5.1 §3] Wall plate x jitter +-0.25 m (relaxes the 9 m even spacing)."""
    return [d["x"] + bc.jit_scalar(d["x"], 0.0, "wpN4", -0.25, 0.25)
            for d in PARAMS["wall_plates"]]


def _dressing_probes(drop):
    """Check points: (name, (x,y,z)). Only the representative extreme points of the new dressing."""
    P = []
    sl = PARAMS["streetlight"]
    for x in streetlight_xs():
        gz = road_z(x, drop)
        P.append((f"가로등x{x:.1f}·헤드", (x + 0.0, sl["y"] + sl["arm_len"],
                                        gz + sl["pole_h"] - 0.15)))
        P.append((f"가로등x{x:.1f}·기부", (x, sl["y"], gz + 0.3)))
    es = PARAMS["entry_sign"]
    P.append(("진입사인·판", (es["x"], es["y"],
                             es["pole_h"] - es["h"] / 2.0 - 0.05)))
    wp = PARAMS["wall_plate"]
    for x in wall_plate_xs():
        P.append((f"옹벽판x{x:.1f}", (x, -PARAMS["wall"]["y_in"] + 0.02,
                                      road_z(x, drop) + wp["z_off"])))
    bo = PARAMS["bollard"]
    for b in PARAMS["bollards"]:
        P.append((f"볼라드({b['cx']:+.1f},{b['cy']:+.1f})",
                  (b["cx"], b["cy"], bo["h"] / 2.0)))
        # **The corner nearest the camera** of the front dot tactile plate (axial far end x lateral outer end)
        fx, fy = bo["front"]
        P.append((f"점형블록({b['cx']:+.1f},{b['cy']:+.1f})",
                  (b["cx"] + fx * (bo["r"] + 0.30),
                   b["cy"] + fy * (bo["r"] + 0.30)
                   + (0.20 if fx != 0.0 else 0.0)
                   * (1.0 if b["cy"] >= 0.0 else -1.0), 0.004)))
    g = PARAMS["guard"]
    yg = PARAMS["wall"]["y_in"] + PARAMS["wall"]["thick"] / 2.0
    for sgn, tag in ((1.0, "N"), (-1.0, "S")):
        for x in (-14.0, -6.0, -2.0, 0.0, 15.0, 30.0, 40.0):
            P.append((f"가드레일{tag}x{x:g}",
                      (x, sgn * yg,
                       road_z(x, drop) + PARAMS["wall"]["wall_h"] + g["rail_h"])))
    for key in ("L1", "L2"):
        bd = PARAMS["buildings"][key]
        P.append((f"원경{key}·근각",
                  (bd["x0"], bd["y0"] if abs(bd["y0"]) < abs(bd["y1"])
                   else bd["y1"], -drop + bd["h"])))
    return P


def _dressing_report(drop):
    views = build_views()
    probes = _dressing_probes(drop)
    print("-" * 64)
    print("[검산] v6 맥락 드레싱 × 카메라 (hFOV 60° / vFOV 36°)")
    # (1) near collision with the camera
    worst = None
    worst_in = None
    for vn, vw in views.items():
        for nm, p in probes:
            _, _, dist, inf = _cam_angles(vw, p)
            if worst is None or dist < worst[0]:
                worst = (dist, vn, nm)
            if inf and (worst_in is None or dist < worst_in[0]):
                worst_in = (dist, vn, nm)
    print(f"  ① 최근접(전체)   = {worst[0]:.2f} m ({worst[1]} ↔ {worst[2]}) "
          f"— 프레임 밖이면 시각 영향 없음")
    ok = worst_in[0] >= 1.0
    print(f"    최근접(프레임 내) = {worst_in[0]:.2f} m "
          f"({worst_in[1]} ↔ {worst_in[2]}) → "
          f"{'OK(근접 점유 없음)' if ok else 'FAIL(<1.0)'}")
    # (2) Occlusion of the signature (road vanishing line) - **exact test**: for prims inside the frame, extend
    #    the eye->prim sight line past the prim and ray-cast whether it lands on the road (|y|<=2, x −14..60).
    #    Warn if the hit x_h is in the vanishing-line section (x >= 20, i.e. lower slope to landing transition).
    #    (Approximate, based on prim representative points - an extreme-point sample, not the full silhouette)
    warn = []
    for vn, vw in views.items():
        for nm, p in probes:
            yw, el, dist, inf = _cam_angles(vw, p)
            if not inf:
                continue
            hit = _road_hit(vw["eye"], p, drop)
            if hit is not None and hit[0] >= 20.0:
                warn.append((vn, nm, hit))
    if warn:
        for vn, nm, hit in warn:
            print(f"  ② [경고] {vn}: {nm} → 노면 (x={hit[0]:.1f}, "
                  f"y={hit[1]:+.2f}) 가림 — 소실선 구간(x≥20) 침범")
    else:
        print("  ② 소실선 구간(x≥20) 노면 가림 프림 없음 → OK "
              "(연장 시선 레이캐스트 판정)")
    # (3) Per-view summary of new prims in frame for the main mise-en-scene views
    for vn in ("ramp_head", "wall_run", "beauty_overview",
               "landing_lookback", "preset_h0.9_d5"):
        vw = views.get(vn)
        if vw is None:
            continue
        names = [nm for nm, p in probes if _cam_angles(vw, p)[3]]
        print(f"  ③ {vn:18s} 프레임 내 {len(names):2d}종: "
              f"{', '.join(names[:6])}{' …' if len(names) > 6 else ''}")
    # (4) Geometric margin (penetration / floating) check
    wl = PARAMS["wall"]
    es = PARAMS["entry_sign"]
    sl = PARAMS["streetlight"]
    g = PARAMS["guard"]
    sy1 = es["y"] + es["w"] / 2.0                   # yaw180 -> plate width along the Y axis
    print(f"  ④ 진입사인 판 y [{es['y'] - es['w'] / 2.0:+.2f}, {sy1:+.2f}] vs "
          f"옹벽 내면 {wl['y_in']:+.2f} → 여유 {wl['y_in'] - sy1:+.3f} m "
          f"{'OK' if sy1 < wl['y_in'] else 'FAIL(관통)'}")
    hy = sl["y"] + sl["arm_len"]
    print(f"    가로등 헤드 y {hy:+.2f} (노면 |y|≤{PARAMS['ramp']['y1']:.2f} 안) "
          f"· 지주 y {sl['y']:+.2f} (옹벽 외면 "
          f"{-(wl['y_in'] + wl['thick']):+.2f} 밖 = 잔디) → "
          f"{'OK' if abs(hy) < PARAMS['ramp']['y1'] and abs(sl['y']) > wl['y_in'] + wl['thick'] else 'FAIL'}")
    ygr = wl["y_in"] + wl["thick"] / 2.0
    print(f"    가드레일 y ±{ygr:.3f} = 옹벽 두께 중앙(±{wl['y_in']:.2f}.."
          f"±{wl['y_in'] + wl['thick']:.2f}) → 천단 착지 OK · 포스트 높이 "
          f"{g['rail_h']:.2f} m")
    print("-" * 64)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. ramp_head / h0.9   — 노면이 아래로 사라지는데 실제로는 5% 완경사인가(특색)
 2. wall_run           — 편측 옹벽 그림자가 노면을 '일부만' 덮는가(태양 az 115°)
 3. 지평 폐쇄          — 경사 끝 너머 하늘 틈 없이 착지·원경 지면/건물로 닫히는가
 4. landing_lookback   — 진입→경사→착지 노면이 끊김 없이 이어지는가(보행 연속성)
 5. GT 불변식          — 프레임 어디에도 수직 낙차/개구/옹벽 뒤 단차가 없는가
 6. 경사 ON vs OFF     — hazard_stairs False 시 전 구간 평지, 옹벽 높이 일정
 7. [v6] 노면 재질     — 콘크리트 회색으로 읽히는가(흙길 오독 해소) · 횡줄눈
 8. [v6] 맥락 판독     — 가드레일·가로등·안내판/사인·볼라드 2열·원경 저층지붕
                         으로 '지하차도 진입 보행 램프'가 읽히는가
 9. [v6] 신규 그림자   — 가로등 그림자가 노면에 전혀 안 떨어지는가(-Y 배치)"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
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
    UsdGeom.Xform.Define(stage, "/World/Scene24")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene24"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # Slope toggle: if OFF, drop=0 (flat throughout) - only the geometry transform changes.
    DROP = PARAMS["ramp"]["drop"] if cfg["hazard_stairs"] else 0.0

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        # [v6-(1)] road_tint cools the warm (ochre) cast of concrete_floor to a neutral grey
        #        - the reason it read as a "dirt track" in the r1 render. Geometry and scale unchanged.
        M["road"] = PBR(
            f"{ROOT}/Looks/Road", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"],
            tint=mp["road_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["wall_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            2.0, tint=mp["brick_tint"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = PBR(f"{ROOT}/Looks/GKitIron",
                            diffuse_color=(0.10, 0.10, 0.105),
                            metallic=0.55, roughness_const=0.55)
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
        M["tactile"] = bc.tactile_mtl(stage, f"{ROOT}/Looks/Tactile")
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        # --- [v6] dressing materials ---
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        M["sign_face"] = PBR(f"{ROOT}/Looks/SignFace",
                             diffuse_color=mp["sign_face"],
                             roughness_const=mp["sign_rough"])
        # Korean information sign panel - uv_mode (1:1 match to the mesh st, build_sign only)
        M["sign_panel"] = PBR(f"{ROOT}/Looks/SignPanel",
                              sc.tex_path("sign_info", "diff"), uv_mode=True,
                              roughness_const=0.45)
        M["joint"] = PBR(f"{ROOT}/Looks/Joint", diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], specular_level=0.0)
        # [W2 fix batch F1] Ground-class decal materials for the kit.
        #   Binding kit crack / stain / wear elements to the scene's joint-sealant
        #   (`paint` class), steel (`metal`) or kerb constants is what rendered them
        #   as flat texture-less ribbons and mats: those classes are excluded from
        #   `_CONST_MDL_CLASSES` **by design** (a constant colour is physically right
        #   for paint and metal), so a *ground* prim bound to one gets no texture at
        #   all. `GKitCrack` / `GKitStain` classify as concrete, so they are promoted
        #   to a real ground texture with the intended albedo preserved.
        M["gk_crack"] = PBR(f"{ROOT}/Looks/GKitCrack",
                            diffuse_color=(0.055, 0.055, 0.056),
                            roughness_const=0.92)
        M["gk_stain"] = PBR(f"{ROOT}/Looks/GKitStain",
                            diffuse_color=(0.20, 0.20, 0.195),
                            roughness_const=0.86)
        return M

    # -------------------------------------------------------------------
    # Site - grass outside the corridor. Descends on the same slope as the road (0 level difference behind the wall = GT invariant)
    #   3 sections: upper flat / slope face (south·north) / lower plain. The joints have 0.02 overlap and the top
    #   faces diverge across each other, so no coplanar Z-fighting occurs.
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        rp = PARAMS["ramp"]
        wl = PARAMS["wall"]
        y_out = wl["y_in"] + wl["thick"]              # 2.35
        th = g["thick"]
        run = rp["run"]
        # (1) upper flat (x_w .. 0.02), full width
        BOX(f"{ROOT}/Land_Upper",
            ((g["x_w"] + 0.02) / 2.0, 0.0, -th / 2.0),
            (0.02 - g["x_w"], 2.0 * g["half_y"], th), M["grass"], col=True)
        # (2) sloped site (0 .. run) - 2 sheets south and north, outside the corridor (+-y_out)
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            ya = sgn * y_out
            yb = sgn * g["half_y"]
            sc.build_slope(stage, f"{ROOT}/Land_Slope_{tag}", rp["x0"], 0.0,
                           run, DROP, min(ya, yb), max(ya, yb), th, M["grass"],
                           margin=0.0, collider=True)
        # (3) lower plain (run-0.02 .. x_e), full width
        BOX(f"{ROOT}/Land_Lower",
            ((run - 0.02 + g["x_e"]) / 2.0, 0.0, -DROP - th / 2.0),
            (g["x_e"] - run + 0.02, 2.0 * g["half_y"], th), M["grass"],
            col=True)

    # -------------------------------------------------------------------
    # Road - entry flat + 5% slope + flat landing (continuous walking surface)
    # -------------------------------------------------------------------
    def build_road(M):
        rp = PARAMS["ramp"]
        ap = PARAMS["approach"]
        ld = PARAMS["landing"]
        appr_mtl = M["asphalt"] if cfg["cue_material_break"] else M["road"]
        # [W2-0 · P-A] The entry flat is the stage for ground_kit -> displacement skin OFF.
        #   It must be registered **before the BOX call** (`add_box` decides on the spot).
        sc.skin_exclude(f"{ROOT}/Road_Approach")
        # entry flat
        BOX(f"{ROOT}/Road_Approach",
            ((ap["x0"] + ap["x1"]) / 2.0, 0.0, ap["z_top"] - ap["thick"] / 2.0),
            (ap["x1"] - ap["x0"], rp["y1"] - rp["y0"], ap["thick"]),
            appr_mtl, col=True)
        # slope body
        sc.build_slope(stage, f"{ROOT}/Road_Slope", rp["x0"], 0.0, rp["run"],
                       DROP, rp["y0"], rp["y1"], rp["thick"], M["road"],
                       margin=0.0, collider=True)
        # flat landing
        BOX(f"{ROOT}/Road_Landing",
            ((ld["x0"] + ld["x1"]) / 2.0, 0.0, -DROP - ld["thick"] / 2.0),
            (ld["x1"] - ld["x0"], rp["y1"] - rp["y0"], ld["thick"]),
            M["road"], col=True)

    # -------------------------------------------------------------------
    # [W2] ground_kit - P8 ramp_road. **Entry flat only** (the slope section cannot be covered
    #   by a single-z plan - see the PARAMS["gkit"] comment).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["joint"], crack=M["gk_crack"], patch=M["asphalt"],
                  patch_cut=M["gk_crack"], gully=M["gk_iron"], gutter=M["wall"],
                  marking=M["parapet"], weed=M["grass"], tactile=M["tactile"],
                  stain_tire=M["gk_stain"], stain_dirt=M["gk_stain"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneN4 P8 · 프림 {res['prims']} · 산포 "
              f"{res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Retaining wall - the top follows the road exactly (1 build_slope). The entry and landing sections are flat wall.
    #   No stepped segment approximation is used, so wedge gaps (lesson 4) are ruled out at source.
    # -------------------------------------------------------------------
    def build_walls(M):
        rp = PARAMS["ramp"]
        ap = PARAMS["approach"]
        wl = PARAMS["wall"]
        y_in, t = wl["y_in"], wl["thick"]
        hh, dep = wl["wall_h"], wl["depth"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            ya = sgn * y_in
            yb = sgn * (y_in + t)
            y0, y1 = min(ya, yb), max(ya, yb)
            yc = (y0 + y1) / 2.0
            # entry section flat wall (top z=hh) - 0.02 overlap with the sloped wall
            BOX(f"{ROOT}/Wall_Appr_{tag}",
                ((ap["x0"] + ap["x1"]) / 2.0, yc, hh - dep / 2.0),
                (ap["x1"] - ap["x0"], t, dep), M["wall"], col=True)
            # slope section - the top face runs (0,hh)->(run, hh-DROP)
            sc.build_slope(stage, f"{ROOT}/Wall_Slope_{tag}", rp["x0"], hh,
                           rp["run"], DROP, y0, y1, dep, M["wall"],
                           margin=0.0, collider=True)
            # landing section flat wall (top z=hh-DROP)
            BOX(f"{ROOT}/Wall_Land_{tag}",
                ((rp["run"] - 0.02 + wl["x_end"]) / 2.0, yc,
                 hh - DROP - dep / 2.0),
                (wl["x_end"] - rp["run"] + 0.02, t, dep), M["wall"], col=True)

            # [realism v1] Retaining wall detail - weep holes · expansion/contraction joints · coping.
            # Survey finding: all 51 retaining walls in this scene were **plain blank walls**. A real retaining wall
            # has φ100 weep holes about every 4m (Road Design Guide vol.3, part 8-7), a cantilever wall is
            # broken by an expansion joint every 15~20m, and contraction joint grooves go in at 9m or less
            # spacing. These repeated division lines are what let the wall face read at scale.
            # No GT effect: they are wall-face fittings, so they do not change the ground z(x,y).
            if sc.LOOK_GEO:            # weep holes / expansion joints = new prims (geometry)
                try:
                    import infra_kit as ik
                    kit = ik.Kit(
                        box=lambda pth, c, sz, m=None, col=False: sc.add_box(
                            stage, pth, c, sz, m, collider=col),
                        cyl=lambda pth, c, r, h, m=None, rotY=0.0, rotX=0.0,                             col=False: sc.add_cylinder(
                                stage, pth, c, r, h, m, rotY=rotY),
                        stage=stage)
                    ik.build_retaining_wall_details(
                        kit, f"{ROOT}/WallDet_{tag}",
                        ap["x0"], wl["x_end"], ya, 0.0, hh,
                        M["wall"], axis="x", normal_sign=-sgn,
                        wall_t=t, wall_type="cantilever", coping=False)
                except Exception as e:
                    print(f"[룩v1][경고] 옹벽 상세 실패 {tag}: {e}")

    # -------------------------------------------------------------------
    # cue - pipe rail on top of the retaining wall (optional)
    # -------------------------------------------------------------------
    def build_cues(M):
        if not cfg["cue_railing"]:
            return
        # [v6] Same y·z as the dressing guardrail (posts + 2 rails), so avoid the coaxial duplicate.
        if cfg["cue_scene_dressing"]:
            print("[cue] cue_railing 생략 — 드레싱 가드레일이 이미 동일 선상에 "
                  "있음(동축 실린더 Z-파이팅 회피)")
            return
        rp = PARAMS["ramp"]
        wl = PARAMS["wall"]
        yc = wl["y_in"] + wl["thick"] / 2.0
        n = 12
        seg = rp["run"] / n
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            for i in range(n):
                xa = rp["x0"] + i * seg
                zc = wl["wall_h"] - DROP * (i + 0.5) / n + 0.45
                CYL(f"{ROOT}/Rail_{tag}/Seg_{i}", (xa + seg / 2.0, sgn * yc, zc),
                    0.03, seg * 1.02, M["rail"], rotY=90.0)

    # -------------------------------------------------------------------
    # [v6-(2)] Guardrail on top of the retaining wall - follows the road slope (entry flat + 5% slope)
    #   ground_fn of build_railing_line = wall top z = road_z(x) + wall_h.
    #   The flat landing section (x 30..44.9) is a local parallel extension (post rhythm 2.75 kept).
    #   The post bases land on the wall crown, so nothing floats or is buried.
    # -------------------------------------------------------------------
    def build_guard(M):
        rp = PARAMS["ramp"]
        wl = PARAMS["wall"]
        ap = PARAMS["approach"]
        g = PARAMS["guard"]
        yg = wl["y_in"] + wl["thick"] / 2.0            # centre of the wall thickness
        top_of_wall = lambda x: road_z(x, DROP) + wl["wall_h"]   # noqa: E731
        z_land = wl["wall_h"] - DROP                   # crown z of the landing section
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            y = sgn * yg
            sc.build_railing_line(
                stage, f"{ROOT}/Guard_{tag}", y, ap["x0"], rp["x0"],
                rp["run"], DROP, top_of_wall, M["rail"],
                rail_h=g["rail_h"], post_r=g["post_r"], spacing=g["spacing"],
                rail_r=g["rail_r"], rail_mid_r=g["rail_mid_r"],
                rail_mid_drop=g["rail_mid_drop"])
            # Landing flat extension: 2 rails (top·mid) + posts (2.75 rhythm, no duplicate at x=30)
            xa, xb = rp["x0"] + rp["run"], g["x_land_end"]
            if xb - xa > 0.1:
                for nm, r, zo in (("Top", g["rail_r"], 0.0),
                                  ("Mid", g["rail_mid_r"], g["rail_mid_drop"])):
                    CYL(f"{ROOT}/GuardLand_{tag}/Rail{nm}",
                        ((xa + xb) / 2.0, y, z_land + g["rail_h"] - zo),
                        r, xb - xa, M["rail"], rotY=90.0)
                xp = xa + g["spacing"]
                k = 0
                while xp <= xb - 0.2:
                    CYL(f"{ROOT}/GuardLand_{tag}/Post_{k}",
                        (xp, y, z_land + g["rail_h"] / 2.0),
                        g["post_r"], g["rail_h"], M["rail"])
                    xp += g["spacing"]
                    k += 1

    # -------------------------------------------------------------------
    # [v6-(3)] 3 street lamps - **on the -Y grass only**. Shadows run only to −Y -> 0 effect on the road.
    #   The poles stand behind the wall (crown = road+1.6) and the arms reach out over the corridor.
    # -------------------------------------------------------------------
    def build_streetlights(M):
        sl = PARAMS["streetlight"]
        for i, x in enumerate(streetlight_xs()):    # v5.1 §3 even-spacing jitter
            gz = road_z(x, DROP)                       # grass = same profile as the road
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (x, sl["y"], gz + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["pole"], col=True)
            ay = sl["y"] + sl["arm_len"] / 2.0          # the arm goes +Y (corridor side) only
            CYL(f"{base}/Arm", (x, ay, gz + sl["pole_h"] - 0.10),
                sl["arm_r"], sl["arm_len"], M["pole"], rotX=90.0)
            BOX(f"{base}/Head",
                (x, sl["y"] + sl["arm_len"], gz + sl["pole_h"] - 0.15),
                (sl["head"], sl["head"], 0.12), M["lamp"])

    # -------------------------------------------------------------------
    # [v6-(4)] 3 wall plates - the south (-Y) inner face is the sunlit face, so they read.
    #   proud toward +Y from the inner face y=-y_in. Backing plate + face plate, 2 boxes (scene02 pattern).
    # -------------------------------------------------------------------
    def build_wall_plates(M):
        wl = PARAMS["wall"]
        wp = PARAMS["wall_plate"]
        y_face = -wl["y_in"]                           # south wall inner face
        for i, x in enumerate(wall_plate_xs()):     # v5.1 §3 even-spacing jitter
            zc = road_z(x, DROP) + wp["z_off"]
            yb = y_face + wp["t"] / 2.0                # backing plate centre
            BOX(f"{ROOT}/WallPlate_{i}/Back", (x, yb, zc),
                (wp["w"], wp["t"], wp["h"]), M["sign"])
            BOX(f"{ROOT}/WallPlate_{i}/Face",
                (x, y_face + wp["t"] + wp["face_t"] / 2.0, zc),
                (wp["face_w"], wp["face_t"], wp["face_h"]), M["sign_face"])

    # -------------------------------------------------------------------
    # [v6-(4)] 1 entry information sign - Korean texture panel (sign_info). Faces -X.
    #   Per the GT convention only an **information (info)** sign is used, never a 'drop warning' (mislabelling banned).
    # -------------------------------------------------------------------
    def build_entry_sign(M):
        es = PARAMS["entry_sign"]
        sc.build_sign(stage, f"{ROOT}/EntrySign", es["x"], es["y"], 0.0,
                      es["yaw"], M["sign_panel"], w=es["w"], h=es["h"],
                      pole_h=es["pole_h"], pole_r=es["pole_r"],
                      pole_mtl=M["pole"], back_mtl=M["sign"])

    # -------------------------------------------------------------------
    # [v6-(1)] Road expansion-joint transverse lines - thin dark bands following the slope.
    #   Box thickness 0.02, top face at local road +0.001. Over the 0.06 joint width the slope deviation is
    #   0.05·0.06 = 0.003 m < half thickness 0.01 -> no penetration or floating (avoids Z-fighting).
    # -------------------------------------------------------------------
    def build_joints(M):
        jt = PARAMS["joints"]
        rp = PARAMS["ramp"]
        n = 0
        x = jt["x0"]
        while x <= jt["x1"] + 1e-6:
            zc = road_z(x, DROP) + jt["proud"] - 0.01
            # Width 0.04 narrower than the road - so no third coplanar face is created at the road flanks
            # (y=+-2.0, where it meets the wall inner face).
            BOX(f"{ROOT}/RoadJoint_{n}", (x, 0.0, zc),
                (jt["w"], rp["y1"] - rp["y0"] - 0.04, 0.02), M["joint"])
            x += jt["step"]
            n += 1

    # -------------------------------------------------------------------
    # Dressing - bollards + horizon closure by the distance (hedges · trees · ridge · buildings)
    # -------------------------------------------------------------------
    def build_dressing(M):
        # Bollards [v5.1 §2] - 2 rows at the ramp entry, spec h0.90 · spacing about 1.5 m,
        #   white reflective band on top + 0.3 m dot tactile paving on the front (−X approach side).
        bo = PARAMS["bollard"]
        for i, bd in enumerate(PARAMS["bollards"]):
            # [W2 §12.5 (2)] The per-unit small plate is replaced by ground_kit's **continuous 0.60 m band**
            #   (a 0.12 m² plate per unit cannot be read). Of the 2 rows, placing it only in front of the
            #   row on the pedestrian approach side is the statutory intent (§12.4 registers 1 site).
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bd["cx"],
                                 bd["cy"], 0.0, None, M["bollard"],
                                 M["bollard_band"], M["tactile"],
                                 front_dir=bo["front"], radius=bo["r"],
                                 height=bo["h"], tactile=False)
        build_guard(M)
        build_streetlights(M)
        build_wall_plates(M)
        build_entry_sign(M)
        build_joints(M)
        fa = PARAMS["far"]
        for i, cy in enumerate(fa["hedge_cys"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fa["hedge_x"], cy - fa["hedge_len"] / 2.0,
                           fa["hedge_x"] + 1.2, cy + fa["hedge_len"] / 2.0,
                           fa["hedge_h"], base_z=-DROP)
        for i, cy in enumerate(fa["tree_cys"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", fa["tree_x"], cy,
                          -DROP, M["wood"], M["canopy_a"], M["canopy_b"])
        rg = fa["ridge"]
        BOX(f"{ROOT}/FarRidge",
            ((rg["x0"] + rg["x1"]) / 2.0, (rg["y0"] + rg["y1"]) / 2.0,
             -DROP + rg["h"] / 2.0),
            (rg["x1"] - rg["x0"], rg["y1"] - rg["y0"], rg["h"]), M["grass"])
        for key, bd in PARAMS["buildings"].items():
            bd = dict(bd)
            bd["base_z"] = -DROP
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    build_road(M)
    build_walls(M)
    build_cues(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements - after the dressing (scatter order convention)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        _geometry_report()
        if cfg["cue_scene_dressing"]:
            _dressing_report(DROP)
        print(f"[SMOKE] sceneN4 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN4_{ts}.png")
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
