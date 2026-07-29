# -*- coding: utf-8 -*-
"""
scene19_fan_winder.py — NegObs synthetic scene 19: T7 fan corner stairs (winder)
(Isaac Sim 4.5)

Spec : Docs/multi_scene_brief_v3.md §D scene19_fan_winder (the only spec)
Shared library : scene_common.py (§A) — boot · make_pbr · build_arc_steps · lighting · capture
Motif reference : scene05_amphitheater.py (main skeleton · arc step tiers · cue toggles)

Type identity: the nosings are radial — no straight-line vanishing point.
  12 fan steps (r_in1.2/r_out4.0, 7.5 deg sector each, drop 1.8m) wind a 1/4 turn (90 deg)
  around a building corner. From the upper approach direction (+X), the radial nosings break
  the vanishing-point rule.

[accessibility v2] (2026-07-27, see the look_refs/scene19 study): in the old version the parapet blocked
  all 12 sectors, and the wedge between the outer arc and the sidewalk plus the pocket beside the L wall
  were open drops, so pedestrian entry was impossible. Fix: keep the parapet on sectors 2..9 only
  (opening the entry and exit) + gate posts, a corner slab (the wedge floor = an extension of the lower
  plaza), an upper threshold sliver, an edge guard retaining wall, and the L wall flush with the radial
  edges (sealing the pockets). See PARAMS["access"].

[rooftop v3] (2026-07-27, user instruction "widen the approach + rooftop scene context"):
  (1) approach widened — entry sectors 0..2 are merged into a kite landing (same top face −0.15),
    parapet sectors 3..9 → the entry opens over a 22.5 deg arc (outer arc 1.53m, was 1.05m). The remaining
    9 steps divide riser (1.8−0.15)/9 evenly, so the total drop stays 1.8. See _step_top.
  (2) rooftop reframing — the upper sidewalk (z0) = the roof terrace of a low wing, the L wall = the
    rooftop core, the lower sidewalk (−1.95) = the terrace one floor down. The ground drops −2.31→−6.0
    (road level) and the sidewalk slabs extend into the building body. Rooftop parapet (perimeter edge
    guard = a cue for inferring the plant), HVAC · vent · pipe run · rooftop door (plant cues), and roofs of
    surrounding low-rise buildings (scale anchors at or below eye height, build_building with base_z
    support). See PARAMS["roof"] and build_rooftop.

[rooftop v4] (2026-07-27, judge_v6_rt_light8 §scene19 rework — 2 re-aimed cuts failed 2 rounds running):
  The cause of both failures was **not doing the occlusion check on coordinates**. So section [C]
  (_solid_at · _frame_scan · _geom_report) is added, porting and simplifying the
  `_obstacle_boxes`/`_solid_at` sight-line test of scene08_sunken_plaza, and with NEGOBS_SMOKE=1 it
  **checks every preset on coordinates before booting** (sparse ray marching of the frame → occupancy).
  (1) roof_skyline — building E's roof was being occluded tangentially by the rooftop parapet (U_N top 1.1).
    To keep the human eye-height limit (2.0 m), instead of raising the camera **distant building E is moved
    north** (old x−28..−14·y8..22 → x6..20·y16..42, height 4.5 unchanged).
    The bearing becomes due north, where the lower terrace parapet (top −0.75) is out of the sight line,
    so building E's roof (−1.5, cap −1.0) opens up 3.0 m below eye height.
  (2) radial_nosing — the old eye(5.2,0.7) was inside the L wall and edge guard, so no tgt could avoid the
    white mass. Following the judgment's recommendation it moves **near winder_mid (above the kite
    landing)** and tgt drops to the foot of the newel, taking in all 12 steps from above. White mass 0 %.
  (3) (additional director instruction) lower_lookup — the old eye faced the parapet ring head-on, so the
    sight-line axis was blocked by `Parapet_9` 0.60 m ahead and the white mass was 54 %.
    Replaced by stepping down **onto the last step of the descent (sector 10)** and looking back up the
    fan — riser faces 47 %, white 0 %. It pairs with radial_nosing (down-view = treads).
  (4) (additional director instruction) roof_context — the rooftop planter is pushed to the west end
    (6.0,−6.8) and the depression eased so the canopy top comes inside the frame (sy +0.86).
  ※ Not fixed (structural): the whole winder corridor lies in the shadow of the L wall (top 3.5). Lighting
    adjustment is out of scope for this instruction — read the PT judgment on the premise that
    "the corridor cuts receive sky light only".

Run / capture / smoke : the same env convention as scene05 and scene06.
    NEGOBS_CAPTURE=1 / NEGOBS_SMOKE=1 / NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG

Coordinates: Z-up, m. Winder centre (the building corner newel) (0, 0). First step direction +X.
  Preset axis = the upper approach direction (looking down the descent from +X toward −X): grid_views
  mirrored about x=6 → the axis looking down at the winder from the upper sidewalk [brief §D 'preset axis'].
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
# [A] SCENE_CONFIG — 7 keys. hazard_stairs = winder descent geometry toggle (↔ flat corner).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # fan winder (False → z=0 flat corner plaza)
    "cue_railing":        True,    # handrail on top of the outer parapet (usual for public corner stairs)
    "cue_tactile":        False,   # True → warning tactile strip on the upper approach
    "cue_material_break": True,    # upper sidewalk (plaza_light) vs lower sidewalk (plaza_lower)
    "cue_nosing":         False,   # True → radial nosing anti-slip arc bands
    "cue_sign":           False,   # [reserved]
    "cue_scene_dressing": True,    # planter, buildings, grass
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    center=dict(cx=0.0, cy=0.0),
    # 12 fan steps: step i = build_arc_steps(r_in1.2/r_out4.0, i*7.5 deg..+7.5 deg, seg3,
    #   top_z=−0.15*(i+1), base −2.3) → 90 deg of total turn, drop 1.8
    # [rooftop v3] kite_n: entry sectors 0..kite_n-1 are merged into a single kite landing (top −riser).
    #   The remaining (n−kite_n) steps divide the (n·riser − riser) drop evenly → total drop stays 1.8.
    winder=dict(r_in=1.2, r_out=4.0, n=12, sector_deg=7.5, a0=0.0,
                riser=0.15, base_z=-2.3, seg=3, kite_n=3),
    # inner corner newel: Cylinder r1.1 (z −2.3..0.5)
    newel=dict(r=1.1, z_bot=-2.3, z_top=0.5),
    # building corner L wall: flush with the winder radial edges (y=0 / x=0) — seals the side drop pockets
    #   [accessibility v2] south x1 1→4·y1 −0.2→0, west x1 −0.2→0·y1 1→4
    walls=dict(z_bot=-6.0, z_top=3.5,   # [rooftop v3] extended down to ground −6.0 (rooftop core body)
               south=dict(x0=-8.0, x1=4.0, y0=-1.0, y1=0.0),
               west=dict(x0=-1.0, x1=0.0, y0=-8.0, y1=4.0)),
    # outer low parapet: per-step arc ring (r 3.82..4.05), +1.0 above each step top (arc ring)
    parapet=dict(r_in=3.82, r_out=4.05, h=1.0),
    # [accessibility v2] entry and exit opened (per the look_refs study): parapet on sectors 2..9 only.
    #   corner   = corner slab (the wedge floor between the outer arc and the straight sidewalk edge, lower plaza extension −1.95)
    #   threshold= upper threshold sliver (gap between sidewalk x=4 and the entry sector outer arc, max 0.14, z0)
    #   guard    = upper sidewalk edge retaining wall (guards the 1.95 drop above the wedge, top +1.0)
    # [rooftop v3] entry widened: open sectors 0..2 (kite landing) → parapet 3..9.
    #   threshold x0 3.86→3.70 (at 22.5 deg the outer arc retreats to x=3.70 — prevents a sliver gap;
    #   the inner band bites in as a z0 plate above the kite top face −0.15 = effective tread boundary x<=3.70),
    #   y1 1.05→1.53 (=4·sin22.5 deg). guard follows at x0 3.7·y0 1.53 (seals the junction slot).
    access=dict(parapet_first=3, parapet_last=9,
                corner=dict(x0=-1.0, y0=-1.0, x1=4.0, y1=4.0),
                threshold=dict(x0=3.70, y0=0.0, y1=1.53),
                guard=dict(x0=3.7, x1=4.0, y0=1.53, y1=4.0, h_top=1.0),
                post_r=0.05, post_h=1.15),
    # upper/lower sidewalks (material boundary cue) — solid slabs (down to ground −2.31)
    upper=dict(x0=4.0, x1=17.0, y0=-9.0, y1=4.0, top_z=0.0),
    lower=dict(x0=-9.0, x1=4.0, y0=4.0, y1=17.0, top_z=-1.95),
    # ground (grass) floor — [rooftop v3] road level −6.0 (upper sidewalk z0 = a rooftop 6m above ground)
    ground=dict(x0=-60.0, x1=60.0, y0=-60.0, y1=60.0, top_z=-6.0),

    # ═══ [W2-D ground_kit] P6 roof_membrane — spec §5.6 scene19 row ═════════
    #  19-1 urethane membrane waterproofing (green) + roll seam pitch 0.9~1.1 m, albedo **0.16~0.22**
    #       (director approved M2; the special-effects band 0.10~0.16 and the C4 props band 0.20~0.35
    #        have an empty intersection, so the spec ruled for the mid band of an aged coat) — kit ledger default 0.19.
    #  19-2 parapet turn-up + coping  -> build_rooftop (`roof.turnup_h/coping_w` above)
    #  19-3 roof drains at 2 places (10.5, -0.6) [in every F cut] · (6.0, -7.5)
    #  19-4 4 membrane repair overcoat patches · radial water marks around the drains · runoff below the parapet
    #  --   **no joint grid** — P6 has `joint=None`, so the kit cannot emit one.
    #  ★ Tactile **OFF** (§12.4): private rooftop, not a facility covered by the
    #    accessibility act. The scene keeps a `cue_tactile` path for ablation
    #    only; nothing is installed by default.
    #  ★ Frame origin: `build_views` mirrors `grid_views` about xref 5.8, so the
    #    preset grid origin is world x = 2*5.8 = **11.6** and the progression is
    #    **-X**. `plan_ground(origin=...)` wants that grid origin (the frame
    #    model puts the eye at s = -d), **not** the drop edge. The drop edge is
    #    the roof deck's west lip `upper.x0` = 4.0, i.e. s = 11.6 - 4.0 = **7.6**.
    #    dists are (2, 3.5, 5) to match `build_views` (d10 would be off-roof).
    gkit=dict(
        grid_origin_x=11.6,                    # = 2 * xref(5.8), build_views
        region_inset=0.25,                     # = roof.pp_t (inside parapets)
        drains=[(10.50, -0.60), (6.00, -7.50)],
        patches=[(12.30, -0.60), (14.30, -0.25), (9.20, -3.40), (6.80, 1.90)],
        seam_pitch=1.00,
        wear_n=5,
    ),
    # horizon-closing buildings (base_z = ground) — C high-rise + [rooftop v3] D/E low-rise (roofs at or below
    #   eye height, −2.5/−1.5 = rooftop scale anchors)
    # [rooftop v4] E relocated: from the old x−28..−14·y8..22 (north-west) the sight line grazed the **lower
    #   terrace parapets L_W/L_N (top −0.75)** and the roof (cap top −1.0) sank below that
    #   silhouette (2 rounds running with no sighting). Moving it to a due-north site (x6..20·y16..42) opens
    #   a sight line that crosses neither the upper rooftop (x4..17·y−9..4) nor the lower terrace (x−9..4·y4..17)
    #   parapets. Height 4.5 (roof −1.5) unchanged → against the 2.0 eye height it sits
    #   3.0 m below = the scale anchor holds. The facade is turned to the south face (our side).
    #   *hazard geometry (winder, parapet) unchanged; only the distant building moves.*
    buildings=dict(
        C=dict(x0=44.0, x1=54.0, y0=-16.0, y1=16.0, h=15.0, floors=5,
               axis="x", facade_x=44.0, face_dir=-1.0, base_z=-6.0),
        D=dict(x0=-30.0, x1=-16.0, y0=-20.0, y1=-6.0, h=3.5, floors=1,
               axis="x", facade_x=-16.0, face_dir=1.0, base_z=-6.0),
        E=dict(x0=6.0, x1=20.0, y0=16.0, y1=42.0, h=4.5, floors=1,
               axis="y", facade_y=16.0, face_dir=-1.0, base_z=-6.0),
    ),
    # [rooftop v3] rooftop parapet (perimeter guard) · plant props · rooftop door — build_rooftop
    roof=dict(pp_t=0.25, pp_h=1.2, pp_h_inner=1.1,
              # [W2-D §5.6 19-2] turn-up 0.30 m · coping 0.50, the middle of 0.45~0.55
              turnup_h=0.30, coping_w=0.50,
              hvac=[dict(cx=13.0, cy=-7.0), dict(cx=14.4, cy=-7.0)],
              hvac_size=(0.9, 0.35, 0.8),
              vent=dict(cx=8.0, cy=-5.5, r=0.15, h=0.8),
              pipe=dict(x0=5.0, x1=16.0, y=-8.55, r=0.06),
              door=dict(w=0.9, h=2.1),   # position = centre of the L wall south end face (x=4)
              # [rooftop v4] the rooftop planter position is promoted into PARAMS (single source for
              #   assembly and occlusion checks). The old (11,−6) was 5.9 m in front of the roof_context eye, so the
              #   canopy top was cropped at sy=1.95, outside the top of frame (v6 judgment extra observation (1)).
              #   Pushed to the west end for a 10.8 m viewing distance → sy 0.83, inside the frame.
              #   0.19 m clear of the pipe run (y −8.61..−8.49) and 0.25 m clear of the U_W parapet (x4.25).
              #   canopy_*: the measured upper bound of the tree form that scene_common.build_tree
              #   builds from a coordinate-hash RNG (trunk 2.42 + canopy) — for the occlusion AABB and frame checks.
              planter=dict(cx=6.0, cy=-6.8, size=3.0,
                           canopy_top=3.90, canopy_r=1.35)),

    material=dict(
        scale=dict(plaza_light=1.80, plaza_lower=0.8, granite_dark=1.0,
                   concrete_wall=2.0, brick_red=2.0, grass=1.4),
        lower_warm_tint=(1.06, 1.0, 0.94),
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [W2-D · spec §5.6 19-2] The near-white parapet constant is retired.
        #   scene19 is the #1 near-white offender of the whole set and this
        #   single constant is bound to every parapet, guard and gate post in
        #   the scene. Weathered concrete coping measures 0.35~0.45; 0.40 is
        #   the middle and is unambiguously not near-white.
        parapet_color=(0.40, 0.40, 0.385), parapet_rough=0.66,
        # 19-2 coating turn-up: the lower 0.30 m of the parapet's inner face takes the same colour as the deck coat.
        #   The value is the middle of the director-approved M2 band 0.16~0.22 (= ground_kit
        #   GROUND_DIMENSIONS["membrane_albedo"] 0.19), given in green.
        #   [W2 fix batch F1/B3] The bound value was **0.1405 luminance** against the
        #   0.16~0.22 band it cites - below its own declaration, which is why the
        #   membrane collapsed to a single near-black blob in building shadow
        #   (`entry_gate` mean -47, `upper_approach` -57). Rescaled to luminance 0.19,
        #   the declared mid, keeping the green hue exactly.
        coating_color=(0.155, 0.203, 0.162), coating_rough=0.72,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
        hvac_color=(0.60, 0.61, 0.62), hvac_rough=0.5,      # [rooftop v3] HVAC unit
        # r5 judgment: a dark door was buried in the dark granite wall → painted steel plate in blue-grey for contrast
        door_color=(0.28, 0.30, 0.33), door_rough=0.6,      # [rooftop v3] rooftop steel door
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


_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene19")


# ===========================================================================
# [C] geometry self-verification — point containment (_solid_at) + sight-line ray marching
#   [v6 judgment §scene19] the 2 re-aimed cuts failed on **occlusion 2 rounds running**. The cause was
#   assuming occlusion by eye alone. The scene08_sunken_plaza `_obstacle_boxes`/
#   `_solid_at` sight-line test is ported and simplified so the check runs on coordinates before rendering.
#   The single source of the coordinates is PARAMS — it reads the same values as the assembly code (no duplicate definitions).
#   Approximation: winder steps and parapet arcs are tested as **annular sectors** instead of the
#   segment boxes of build_arc_steps (they come out slightly smaller than reality by the 1.03x segment-chord
#   margin, which errs toward 'underestimating occlusion' rather than being conservative, so pass verdicts carry a safety margin).
# ===========================================================================
def _step_top(i):
    """[rooftop v3] sectors 0..kite_n-1 = the kite landing (same top face −riser).
    The remaining (n−kite_n) steps divide (total drop−riser) evenly → total drop n·riser unchanged."""
    w = PARAMS["winder"]
    kn = int(w.get("kite_n", 0))
    if kn <= 0 or i < kn:
        if kn <= 0:
            return -w["riser"] * (i + 1)
        return -w["riser"]
    rem = (w["riser"] * w["n"] - w["riser"]) / (w["n"] - kn)
    return -w["riser"] - rem * (i - kn + 1)


_BOXES_CACHE = [None]


def _solid_boxes():
    """Obstacle AABB list (name, x0,x1, y0,y1, z0,z1) — the same coordinates as the assembly code.
    Arcs (winder steps, parapet) and the cylinder (newel) are tested separately, in polar coordinates, in _solid_at."""
    if _BOXES_CACHE[0] is not None:
        return _BOXES_CACHE[0]
    up, lo, gr = PARAMS["upper"], PARAMS["lower"], PARAMS["ground"]
    ac, wl, rf = PARAMS["access"], PARAMS["walls"], PARAMS["roof"]
    base = gr["top_z"]
    t, h, hi = rf["pp_t"], rf["pp_h"], rf["pp_h_inner"]
    th, gd, co = ac["threshold"], ac["guard"], ac["corner"]
    B = [
        ("Ground", gr["x0"], gr["x1"], gr["y0"], gr["y1"], base - 1.0, base),
        ("Walk_upper", up["x0"], up["x1"], up["y0"], up["y1"], base,
         up["top_z"]),
        ("Walk_lower", lo["x0"], lo["x1"], lo["y0"], lo["y1"], base,
         lo["top_z"]),
        ("CornerSlab", co["x0"], co["x1"], co["y0"], co["y1"], base,
         lo["top_z"]),
        ("Threshold", th["x0"], up["x0"], th["y0"], th["y1"], lo["top_z"],
         up["top_z"]),
        ("EdgeGuard", gd["x0"], gd["x1"], gd["y0"], gd["y1"], lo["top_z"],
         gd["h_top"]),
    ]
    for tag in ("south", "west"):
        b = wl[tag]
        B.append((f"Wall_{tag}", b["x0"], b["x1"], b["y0"], b["y1"],
                  wl["z_bot"], wl["z_top"]))
    # 7 rooftop parapet runs (same z as pp() in build_rooftop: base−0.05 .. base+hh)
    for tag, x0, x1, y0, y1, bz, hh in (
            ("U_E", up["x1"] - t, up["x1"], up["y0"], up["y1"], up["top_z"], h),
            ("U_S", up["x0"], up["x1"] - t, up["y0"], up["y0"] + t,
             up["top_z"], h),
            ("U_W", up["x0"], up["x0"] + t, up["y0"] + t, -1.0, up["top_z"], h),
            ("U_N", up["x0"], up["x1"], up["y1"] - t, up["y1"], up["top_z"],
             hi),
            ("L_W", lo["x0"], lo["x0"] + t, lo["y0"], lo["y1"], lo["top_z"], h),
            ("L_N", lo["x0"] + t, lo["x1"], lo["y1"] - t, lo["y1"],
             lo["top_z"], h),
            ("L_E", lo["x1"] - t, lo["x1"], lo["y0"], lo["y1"] - t,
             lo["top_z"], h)):
        B.append((f"RoofPP_{tag}", x0, x1, y0, y1, bz - 0.05, bz + hh))
    # plant, rooftop door, planter (approximated including the canopy)
    hs = rf["hvac_size"]
    for i, u in enumerate(rf["hvac"]):
        B.append((f"Hvac_{i}", u["cx"] - hs[0] / 2 - 0.05,
                  u["cx"] + hs[0] / 2 + 0.05, u["cy"] - hs[1] / 2 - 0.05,
                  u["cy"] + hs[1] / 2 + 0.05, up["top_z"],
                  up["top_z"] + 0.1 + hs[2]))
    v = rf["vent"]
    B.append(("Vent", v["cx"] - v["r"], v["cx"] + v["r"] * 2.2,
              v["cy"] - v["r"], v["cy"] + v["r"], up["top_z"],
              up["top_z"] + v["h"] + v["r"]))
    p = rf["pipe"]
    B.append(("PipeRun", p["x0"], p["x1"], p["y"] - p["r"], p["y"] + p["r"],
              up["top_z"] + 0.02, up["top_z"] + 0.02 + 2 * p["r"]))
    d, ws = rf["door"], wl["south"]
    B.append(("CoreDoor", ws["x1"], ws["x1"] + 0.04,
              (ws["y0"] + ws["y1"]) / 2 - d["w"] / 2,
              (ws["y0"] + ws["y1"]) / 2 + d["w"] / 2, up["top_z"],
              up["top_z"] + d["h"]))
    pl = rf["planter"]
    ph = max(pl["size"] / 2.0, pl["canopy_r"])                  # canopy included
    B.append(("Planter_A", pl["cx"] - ph, pl["cx"] + ph, pl["cy"] - ph,
              pl["cy"] + ph, 0.0, pl["canopy_top"]))
    for k, bd in PARAMS["buildings"].items():
        bz = float(bd.get("base_z", 0.0))
        B.append((f"Bldg{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                  bz - 1.0, bz + bd["h"]))
        B.append((f"Bldg{k}_roof", bd["x0"] - 0.1, bd["x1"] + 0.1,
                  bd["y0"] - 0.1, bd["y1"] + 0.1, bz + bd["h"],
                  bz + bd["h"] + 0.5))
    _BOXES_CACHE[0] = B
    return B


def _solid_at(x, y, z):
    """Name of the solid containing the point (x,y,z) (None if there is none).
    The single source for the camera-eye-buried and sight-line-blocked (ray march) tests."""
    for nm, x0, x1, y0, y1, z0, z1 in _solid_boxes():
        if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
            return nm
    cx, cy = PARAMS["center"]["cx"], PARAMS["center"]["cy"]
    w, ac, pp = PARAMS["winder"], PARAMS["access"], PARAMS["parapet"]
    nw = PARAMS["newel"]
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    if r <= nw["r"] and nw["z_bot"] <= z <= nw["z_top"]:
        return "Newel"
    a = math.degrees(math.atan2(dy, dx)) % 360.0
    span = w["n"] * w["sector_deg"]
    if w["a0"] <= a <= w["a0"] + span:
        i = min(int((a - w["a0"]) / w["sector_deg"]), w["n"] - 1)
        top = _step_top(i)
        if w["r_in"] <= r <= w["r_out"] and w["base_z"] <= z <= top:
            return f"Step_{i}"
        # parapet arc ring + top handrail (+0.06) as one band
        if ac["parapet_first"] <= i <= ac["parapet_last"] \
                and pp["r_in"] <= r <= pp["r_out"] \
                and top - 0.1 <= z <= top + pp["h"] + 0.06:
            return f"Parapet_{i}"
    return None


def _ray_hit(eye, dirv, step=0.1, tmax=80.0):
    """March from eye along dirv (unit) in steps of step — (distance, solid name|None)."""
    for k in range(1, int(tmax / step) + 1):
        t = k * step
        s = _solid_at(eye[0] + dirv[0] * t, eye[1] + dirv[1] * t,
                      eye[2] + dirv[2] * t)
        if s is not None:
            return t, s
    return tmax, None


def _cam_basis(eye, tgt, hfov=60.0, aspect=16.0 / 9.0):
    """(eye, forward, right, up, tan(hfov/2), tan(vfov/2)) — 1920×1080 = 60°."""
    e = np.array(eye, dtype=float)
    f = np.array(tgt, dtype=float) - e
    f /= np.linalg.norm(f)
    rt = np.cross(f, np.array([0.0, 0.0, 1.0]))
    rt /= np.linalg.norm(rt)
    th = math.tan(math.radians(hfov / 2.0))
    return e, f, rt, np.cross(rt, f), th, th / aspect


def _screen_uv(eye, tgt, p):
    """Normalised screen coordinates of the world point p (sx, sy, whether it is in frame). |s|<=1 = in frame."""
    e, f, rt, uu, th, tv = _cam_basis(eye, tgt)
    v = np.array(p, dtype=float) - e
    d = float(v @ f)
    if d <= 1e-6:
        return None, None, False
    sx, sy = float(v @ rt) / d / th, float(v @ uu) / d / tv
    return sx, sy, (abs(sx) <= 1.0 and abs(sy) <= 1.0)


def _frame_scan(eye, tgt, nx=21, ny=12, step=0.12, tmax=80.0, face=False):
    """Scan the viewport (1920x1080 = 60 deg horizontal FOV) sparsely with nx x ny rays.
    Returns: {solid name: screen occupancy %} — no contact is '<SKY>'.
    With face=True the winder steps are split into `Step_i:tread` / `Step_i:riser` (if the hit point z
    equals that step's top face it is the tread, otherwise the riser face) — for reading ascending sight-line cuts.
    *The convention answering the v6 judgment 'occlusion-check failures recur': after re-aiming, always run
     ray casting through this function, including every parapet member.*"""
    e, f, rt, uu, th, tv = _cam_basis(eye, tgt)
    cnt = {}
    for iy in range(ny):
        sy = (1.0 - (iy + 0.5) * 2.0 / ny) * tv
        for ix in range(nx):
            sx = ((ix + 0.5) * 2.0 / nx - 1.0) * th
            d = f + sx * rt + sy * uu
            d /= np.linalg.norm(d)
            t, s = _ray_hit(e, d, step, tmax)
            k = s if s is not None else "<SKY>"
            if face and k.startswith("Step_"):
                zh = e[2] + d[2] * t
                k += ":tread" if abs(zh - _step_top(int(k.split("_")[1]))) \
                    <= step else ":riser"
            cnt[k] = cnt.get(k, 0) + 1
    tot = float(nx * ny)
    return {k: 100.0 * v / tot for k, v in cnt.items()}


def _pct(scan, *prefixes):
    return sum(v for k, v in scan.items() if k.startswith(prefixes))


def _geom_report():
    """Pre-boot geometry and camera self-verification (NEGOBS_SMOKE=1)."""
    views = build_views()
    up = PARAMS["upper"]
    bE = PARAMS["buildings"]["E"]
    e_roof = bE["base_z"] + bE["h"]
    print("=" * 70)
    print("scene19_fan_winder — SMOKE 기하 자기검증 (부팅 전)")
    print("=" * 70)
    print(f"  총낙차 {abs(_step_top(PARAMS['winder']['n'] - 1)):.2f} m "
          f"(카이트 {PARAMS['winder']['kite_n']}섹터 + 잔여 "
          f"{PARAMS['winder']['n'] - PARAMS['winder']['kite_n']}단) — 불변 검사")
    print(f"  E동 지붕 z {e_roof:+.2f} (캡 {e_roof + 0.5:+.2f}) vs 옥상 눈높이 "
          f"{up['top_z'] + 2.0:+.2f} → "
          f"{'OK (눈높이 이하)' if e_roof + 0.5 < up['top_z'] + 2.0 else 'FAIL'}")

    hits = [(n, _solid_at(*v["eye"])) for n, v in sorted(views.items())]
    hits = [(n, s) for n, s in hits if s is not None]
    for n, s in hits:
        print(f"    [FAIL] {n} eye 가 {s} 내부(매몰)")
    print(f"  [eye 매몰] {len(hits)}건 → {'OK' if not hits else 'FAIL'}")

    print("  [프레임 레이마칭] 21×12 광선 · 60° 수평화각")
    v = views["roof_skyline"]
    sc_sky = _frame_scan(v["eye"], v["tgt"])
    pe = _pct(sc_sky, "BldgE")
    print(f"    roof_skyline  eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
    for k in sorted(sc_sky, key=lambda k: -sc_sky[k])[:6]:
        print(f"      {k:16s} {sc_sky[k]:5.1f}%")
    print(f"      E동 점유 {pe:.1f}% (≥8 = 스케일 앵커 성립) → "
          f"{'OK' if pe >= 8.0 else 'FAIL'}")

    def _stair_cut(name, min_step, min_tier, max_white):
        v = views[name]
        sc_ = _frame_scan(v["eye"], v["tgt"], tmax=20.0, step=0.03, face=True)
        steps_ = _pct(sc_, "Step_")
        riser = sum(val for k, val in sc_.items() if k.endswith(":riser"))
        tiers = sorted({int(k.split("_")[1].split(":")[0])
                        for k, val in sc_.items()
                        if k.startswith("Step_") and val >= 0.4})
        white_ = _pct(sc_, "Parapet_", "RoofPP", "EdgeGuard", "Threshold")
        print(f"    {name:13s} eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
        print(f"      단 점유 {steps_:.1f}%(라이저 {riser:.1f} / 디딤 "
              f"{steps_ - riser:.1f}) · 시인 단 {len(tiers)}/"
              f"{PARAMS['winder']['n']} {tiers} · 뉴얼 "
              f"{sc_.get('Newel', 0.0):.1f}% · 백색 매스 {white_:.1f}%")
        ok = (steps_ >= min_step and len(tiers) >= min_tier
              and white_ <= max_white)
        print(f"      → {'OK' if ok else 'FAIL'} (기준 단≥{min_step:.0f}% · "
              f"시인≥{min_tier}단 · 백색≤{max_white:.0f}%)")

    # radial_nosing = descending down-view (mostly treads) / lower_lookup = ascending up-view (risers)
    _stair_cut("radial_nosing", 60.0, 8, 5.0)
    _stair_cut("lower_lookup", 60.0, 6, 5.0)

    v = views["roof_context"]
    rf = PARAMS["roof"]
    pl, hv = rf["planter"], rf["hvac"]
    probes = [("수관 정상", (pl["cx"], pl["cy"], pl["canopy_top"]))]
    for i, u in enumerate(hv):
        probes.append((f"실외기{i}", (u["cx"], u["cy"], 0.5 + 0.4 * i)))
    probes += [("환기구", (rf["vent"]["cx"], rf["vent"]["cy"], 0.8)),
               ("배관", (10.0, rf["pipe"]["y"], 0.14)),
               ("남 파라펫 상단", (10.0, PARAMS["upper"]["y0"] + 0.12,
                                   rf["pp_h"]))]
    print(f"    roof_context  eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
    bad = []
    for nm, p in probes:
        sx, sy, ok = _screen_uv(v["eye"], v["tgt"], p)
        print(f"      {nm:14s} sx {sx:+.2f} sy {sy:+.2f} → "
              f"{'프레임 안' if ok else '프레임 밖'}")
        if not ok:
            bad.append(nm)
    print(f"      → {'OK' if not bad else 'FAIL ' + str(bad)} "
          f"(수관 잘림 0 · 설비 클러스터 전원 프레임 안)")

    print("  [미장센 시선축 첫 접촉]")
    for n in ("upper_approach", "winder_mid", "lower_lookup", "entry_gate",
              "roof_context", "radial_nosing", "roof_skyline"):
        v = views[n]
        e = np.array(v["eye"], float)
        d = np.array(v["tgt"], float) - e
        L = float(np.linalg.norm(d))
        t, s = _ray_hit(e, d / L, 0.05, L * 3.0)
        print(f"    {n:16s} t={t:5.2f} ({L:5.2f} 까지 tgt) → "
              f"{s if s else '무접촉(지평/하늘)'}")
    print("=" * 70)


# ===========================================================================
# [D] camera presets — grid_views mirrored about x=6 (upper approach axis) + 4 mise-en-scene cuts
# ===========================================================================
def build_views():
    """Preset axis = the upper approach direction. grid_views (gazing +X) is mirrored about x=6 to
    convert it into the axis that looks down the winder descent toward −X from the upper sidewalk (+X, z=0)."""
    # [rooftop v3] xref 6.0→5.8: after mirroring, d5 eye x=17.0 fell inside the east rooftop parapet (16.75~17,
    #   h1.2), blacking out the whole h0.3/0.9_d5 frame → moved inward to 16.6.
    #   d10 (21.6) is kept as an off-roof hover cut = the "rooftop seen from outside" context cut.
    xref = 5.8
    # [v5 judgment] d10 (x21.6 after mirroring) is empty air off the roof — a viewpoint no pedestrian
    #   can occupy, which invalidated 1/3 of the grid. Replaced with physically possible on-roof distances (2, 3.5, 5).
    v = sc.grid_views(0.0, dists=(2, 3.5, 5))
    out = {}
    for k, val in v.items():
        e, t = list(val["eye"]), list(val["tgt"])
        e[0] = 2.0 * xref - e[0]                # mirror → camera on the +X side, gazing −X
        t[0] = 2.0 * xref - t[0]
        out[k] = dict(eye=e, tgt=t)
    out["upper_approach"] = dict(eye=[9.0, -1.0, 1.0], tgt=[1.0, 2.0, -1.2])
    # [v5 judgment] the winder_mid and lower_lookup compositions sat outside the parapet, so the fan
    #   steps were entirely hidden (0 step sightings across 15 cuts). Re-aimed to a viewpoint **inside** the stair corridor:
    #   walk line r~2.6, entry (angle 11 deg) → exit (angle 79 deg).
    #   winder_mid: looking down the fan descent from above the kite landing (the entry shoulder)
    out["winder_mid"]     = dict(eye=[3.4, 0.9, 1.3],  tgt=[1.1, 2.4, -1.3])
    # [rooftop v4 / v6 judgment extra observation] lower_lookup re-aimed. The old eye(0.9,4.4,−0.35) stood
    #   on the lower sidewalk looking at the parapet ring **head-on** — the sight-line axis was
    #   blocked by `Parapet_9` 0.60 m ahead and the white parapet filled 54.1 % of the frame
    #   (matching the v6 judgment "left half → 55 %"). The "corner slab" only has width near angle 45 deg
    #   in the first place, and that span is exactly the parapet-retained span (22.5~75 deg), so it was a
    #   structurally impossible spot. → replaced by stepping down **onto the last step of the descent (sector 10)**
    #   and looking back up the fan (the parapet ring falls behind the sight line).
    #   eye polar r 3.40 / angle 80.0 deg (sector 10, top face −1.617), eye height 1.60 m above it.
    #   [_frame_scan check] steps 88.8 % (**riser 41.8 / tread 47.0** — an ascending sight line, so the
    #   riser faces are exposed in alternation) · 8 steps sighted (sector 2~9) · white mass 0.0 % ·
    #   newel 11.2 % (the radial convergence datum) · dark L wall 0.1 %.
    out["lower_lookup"]   = dict(eye=[0.59, 3.35, -0.02], tgt=[1.55, 1.55, -0.9])
    # [rooftop v4 / v6 judgment (2)] the old eye(5.2,0.7,1.5) sat inside the L wall and edge guard, so no
    #   tgt could avoid the white mass (0 fan steps visible). Following the judgment's recommendation it
    #   moves to **near the successful winder_mid = above the kite landing** and tgt drops to the
    #   foot of the newel. eye is 1.60 m of eye height above the kite top face (−0.15), polar
    #   r 3.15 / angle 17.6 deg (sector 2 = the kite) → tgt r 1.73 / angle 56.8 deg (sector 7),
    #   depression 57 deg. [_frame_scan check] steps 84.9 % · all 12/12 steps sighted (per step
    #   1.8~13.4 %) · newel 5.7 % (the radial convergence datum point) · parapet/rail/guard/threshold/
    #   gate post 0.0 % · dark L wall 8.3 % (1/3 of winder_mid's 22.5 %).
    out["radial_nosing"]  = dict(eye=[3.0, 0.95, 1.45], tgt=[0.95, 1.45, -1.85])
    out["entry_gate"]     = dict(eye=[6.5, 0.5, 1.2], tgt=[1.8, 1.8, -1.2])  # accessibility v2 entry route
    # [rooftop v3] roof_context: plant cluster (HVAC · vent · pipe run) + parapet, a level cut
    # [rooftop v4 / v6 judgment extra observation (1)] canopy cropping resolved. The old tgt z 0.2 (depression 10.7 deg)
    #   combined with the old planter (11,−6) (viewing distance 5.9 m) put the canopy top at sy=1.95 = a point
    #   2x outside the top of frame. The planter is pushed to the west end (6.0,−6.8), stretching the viewing distance to 10.8 m
    #   and the depression eased to 4.4 deg (tgt z 0.2→1.15, eye z 1.8→1.9 = human eye height kept).
    #   [check sy (= normalised vertical screen coordinate, |sy|<=1 is inside the frame)]
    #   canopy top +0.86 · HVAC0 −0.67 · HVAC1 −0.67 · vent −0.14 ·
    #   pipe run −0.41 · south parapet top ±0.00 → **all inside the frame**
    #   (the canopy uses roof.planter.canopy_top 3.90 = the conservative upper bound on the measured 3.81).
    #   [_frame_scan] sky 30.1 / roof deck 20.9 / planter and tree 19.0 (was 44.2 →
    #   over-occupancy eased) / south and west parapets 13.9 / HVAC 11.0 / vent 0.5 %.
    out["roof_context"]   = dict(eye=[16.6, -4.2, 1.9], tgt=[9.0, -8.0, 1.15])
    # [rooftop v4 / v6 judgment (1)] roof_skyline re-aimed for the 3rd time. The north-west bearing of v5 and v6 was
    #   checked by eye only and failed both times — the real occluders were not the winder arc rings but
    #   (a) the U_N rooftop parapet right in front (top 1.1) and (b) the lower terrace parapets L_W/L_N
    #   (top −0.75); building E's cap (−1.0) sank below silhouette (b), leaving only 2 % of the roof
    #   exposed (the v6 frame was reproduced and confirmed with _frame_scan).
    #   Solution: keep the eye height at a human 2.0 m and **move building E due north** (see PARAMS
    #   buildings) — looking due north from the rooftop's north edge (y3.75), the lower terrace
    #   (x<=4) and its parapet do not enter the sight line at all.
    #   [check] eye(10.0,2.0,2.0): 1.76 m to the inner face of U_N → the sight line's depression limit is
    #   atan(0.9/1.76)=27.1 deg. Building E's near end (y16, cap −1.0) is 12.0 deg down · its far end (y42)
    #   4.3 deg → the 7.7 deg roof band (21 % of the 36 deg vertical FOV) is inside the limit (15.1 deg to spare).
    #   For L_N (y16.75..17, x<=4) the sight line is at x11.7 by y17 → no crossing.
    #   [_frame_scan] sky 44.6 % · building E 38.9 % (roof top face 12.3 %) · ground (the alley 6 m
    #   below) 7.7 % · U_N parapet foreground 6.7 % · dark wall 0 %.
    out["roof_skyline"]   = dict(eye=[10.0, 2.0, 2.0], tgt=[13.0, 29.0, -2.0])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. upper_approach — 상부 보도에서 방사형 단코, 직선 소실점 부재
 2. h0.3·d5~10     — 코너 winder 낙차(1.8m) 인지
 3. winder_mid     — 1/4회전 하강의 부채꼴 단 형태
 4. radial_nosing  — 방사선 단코가 세그(3) 각짐 없이 읽히는가(하강 부감=디딤면)
 4b. lower_lookup  — [옥상 v4] 마지막 단에서 팬을 거슬러 올려다본 **라이저 면**
                     (4번과 짝: 부감=디딤 84 % / 앙각=라이저 47 %)
 5. cue            — 상/하부 보도 재질경계 / 외측 파라펫·핸드레일
 6. entry_gate     — [접근성 v2] 문턱→카이트 랜딩 연속(입구 폭 1.53)·게이트
                     기둥·에지 가드, 하부는 출구 sector→코너 슬래브→하부 보도 연속
 7. roof_context   — [옥상 v3] 실외기·환기구·배관·옥상 파라펫 + 옥상 화단·수목
                     [옥상 v4] 수관 정상이 프레임 안에 온전히 들어오는가
                     (스케일 앵커 역할은 8번 roof_skyline 이 전담 — 이 컷의
                      시선은 U_W 파라펫(상단 1.2)에 막혀 원경 D동이 안 보인다)
 8. roof_skyline   — [옥상 v4] 북측 파라펫 너머 E동 지붕이 **눈높이 아래**로
                     열리는가(스케일 앵커) + 6 m 아래 지반이 함께 읽히는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    if smoke_mode:
        # [rooftop v4] coordinate check before booting — the convention that stops occlusion failures recurring (v6 judgment §lessons).
        _geom_report()

    sc.check_assets(
        ["plaza_light", "plaza_lower", "granite_dark",
         "brick_red", "grass", "hdri", "mdl"],
        hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene19")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    C = PARAMS["center"]
    cx, cy = C["cx"], C["cy"]

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["upper"] = sc.make_pbr(
            stage, "/World/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["lower"] = sc.make_pbr(
            stage, "/World/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["lower_warm_tint"])
        # step material = light plaza_light (contrasts with the granite_dark walls) [A-19(1)]
        M["step"] = sc.make_pbr(
            stage, "/World/Looks/Step", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # building corner L wall and newel = dark granite (granite_dark) — contrasts with the steps
        M["granite"] = sc.make_pbr(
            stage, "/World/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["granite_dark"])
        M["brick"] = sc.make_pbr(
            stage, "/World/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            scl["brick_red"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
        M["glass"] = sc.make_pbr(stage, "/World/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["parapet"] = sc.make_pbr(stage, "/World/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        M["hvac"] = sc.make_pbr(stage, "/World/Looks/Hvac",
                                diffuse_color=mp["hvac_color"], metallic=0.3,
                                roughness_const=mp["hvac_rough"])
        M["door"] = sc.make_pbr(stage, "/World/Looks/Door",
                                diffuse_color=mp["door_color"], metallic=0.4,
                                roughness_const=mp["door_rough"])
        # [W2-D · §5.6] urethane membrane waterproofing (green) — deck coat + parapet turn-up in the same colour.
        #   `[spec-doc]` Nara Marketplace R25BK00911379 "the surface colour is green".
        M["coating"] = sc.make_pbr(stage, "/World/Looks/Coating",
                                   diffuse_color=mp["coating_color"],
                                   roughness_const=mp["coating_rough"])
        M["gk_iron"] = sc.make_pbr(stage, "/World/Looks/GKitIron",
                                   diffuse_color=(0.09, 0.09, 0.095),
                                   metallic=0.55, roughness_const=0.55)
        M["gk_stain"] = sc.make_pbr(stage, "/World/Looks/GKitStain",
                                    diffuse_color=(0.17, 0.19, 0.16),
                                    roughness_const=0.88)
        return M

    # -------------------------------------------------------------------
    # ground floor (grass) — full-area slab (below the drop = the floor). Tiled as 4 boxes.
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        top, th = g["top_z"], 1.0
        cz = top - th / 2.0
        xm = (g["x0"] + g["x1"]) / 2.0
        ym = (g["y0"] + g["y1"]) / 2.0
        for tag, (x0, x1, y0, y1) in (
                ("SW", (g["x0"], xm, g["y0"], ym)),
                ("SE", (xm, g["x1"], g["y0"], ym)),
                ("NW", (g["x0"], xm, ym, g["y1"])),
                ("NE", (xm, g["x1"], ym, g["y1"]))):
            sc.add_box(stage, f"/World/Scene19/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])

    # -------------------------------------------------------------------
    # upper/lower sidewalks (material boundary) — solid slabs (down to ground −2.31). Outside the stairs (r>=4).
    # -------------------------------------------------------------------
    def build_walkways(M, hazard):
        base = PARAMS["ground"]["top_z"]
        for name, mtl in (("upper", M["upper"]), ("lower", M["lower"])):
            w = PARAMS[name]
            top = w["top_z"] if hazard else 0.0    # the flat control is z=0 throughout
            # [W2-0 · P-A] The upper roof deck is the ground_kit stage.
            sc.skin_exclude(f"/World/Scene19/Walk_{name}")
            sc.add_box(stage, f"/World/Scene19/Walk_{name}",
                       ((w["x0"] + w["x1"]) / 2.0, (w["y0"] + w["y1"]) / 2.0,
                        (top + base) / 2.0),
                       (w["x1"] - w["x0"], w["y1"] - w["y0"], top - base),
                       mtl, collider=True)
        # [accessibility v2] corner slab: between the winder outer arc (r4) and the straight sidewalk edges (x=4/y=4),
        #   the floor that fills the wedge (max width 1.66). hazard = lower plaza extension (−1.95),
        #   flat control = z0. The x/y<0 band that overlaps the wall interior is buried in the wall volume (not visible).
        co = PARAMS["access"]["corner"]
        top = PARAMS["lower"]["top_z"] if hazard else 0.0
        sc.add_box(stage, "/World/Scene19/CornerSlab",
                   ((co["x0"] + co["x1"]) / 2.0, (co["y0"] + co["y1"]) / 2.0,
                    (top + base) / 2.0),
                   (co["x1"] - co["x0"], co["y1"] - co["y0"], top - base),
                   M["lower"], collider=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P6 roof_membrane (spec §5.6 scene19 row)
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        up = PARAMS["upper"]
        ins = float(g["region_inset"])
        ox = float(g["grid_origin_x"])
        s_edge = ox - float(up["x0"])          # axis "-x": s = origin_x - x
        gp = gk.plan_ground(
            "roof_membrane",
            region=(up["x0"] + ins, up["y0"] + ins,
                    up["x1"] - ins, up["y1"] - ins),
            z=float(up["top_z"]), gy=0.0, origin=(ox, 0.0, 0.0), axis="-x",
            edges=[("roof_edge", s_edge)], dists=(2, 3.5, 5),
            scene="scene19", tactile=(),
            overrides=dict(infra=dict(gully=2),
                           surface=(("patch", 4),
                                    ("stain", ("water", "drip", "dirt")))),
            extras_args=dict(membrane=dict(seam_pitch=float(g["seam_pitch"]),
                                           wear_n=int(g["wear_n"]))),
            sites=dict(gully=[tuple(v) for v in g["drains"]],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=19)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(membrane=M["coating"], membrane_seam=M["gk_stain"],
                  membrane_wear=M["coating"], patch=M["coating"],
                  patch_cut=M["gk_stain"], gully=M["gk_iron"],
                  manhole=M["gk_iron"], trench=M["gk_iron"],
                  trench_frame=M["gk_iron"], joint=M["gk_stain"],
                  crack=M["gk_stain"], weed=M["grass"], wear=M["gk_stain"],
                  stain_water=M["gk_stain"], stain_drip=M["gk_stain"],
                  stain_dirt=M["gk_stain"])
        res = gk.apply_ground(kit, "/World/Scene19/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene19 P6 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # winder 12 steps + newel + building L wall + outer parapet
    # -------------------------------------------------------------------
    # [rooftop v4] _step_top uses the module-scope definition from section [C] as is
    #   (single-sourced so that assembly ↔ occlusion check read the same step top faces).

    def build_winder(M):
        w = PARAMS["winder"]
        for i in range(w["n"]):
            a0 = w["a0"] + i * w["sector_deg"]
            sc.build_arc_steps(stage, f"/World/Scene19/Step_{i}", cx, cy,
                               w["r_in"], w["r_out"], a0, a0 + w["sector_deg"],
                               w["seg"], _step_top(i), w["base_z"], M["step"])
        # inner corner newel
        nw = PARAMS["newel"]
        sc.add_cylinder(stage, "/World/Scene19/Newel",
                        (cx, cy, (nw["z_top"] + nw["z_bot"]) / 2.0),
                        nw["r"], nw["z_top"] - nw["z_bot"], M["granite"],
                        collider=True)
        # 2 faces of the building corner L wall
        wl = PARAMS["walls"]
        zc = (wl["z_top"] + wl["z_bot"]) / 2.0
        hz = wl["z_top"] - wl["z_bot"]
        for tag in ("south", "west"):
            b = wl[tag]
            sc.add_box(stage, f"/World/Scene19/Wall_{tag}",
                       ((b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0, zc),
                       (b["x1"] - b["x0"], b["y1"] - b["y0"], hz), M["granite"],
                       collider=True)
        # outer low parapet: the entry (sector 0..1) and exit (10..11) are open [accessibility v2],
        #   arc rings on the middle sectors only (each step top +h)
        pp = PARAMS["parapet"]
        ac = PARAMS["access"]
        for i in range(ac["parapet_first"], ac["parapet_last"] + 1):
            a0 = w["a0"] + i * w["sector_deg"]
            top = _step_top(i)
            sc.build_arc_steps(stage, f"/World/Scene19/Parapet_{i}", cx, cy,
                               pp["r_in"], pp["r_out"], a0, a0 + w["sector_deg"],
                               1, top + pp["h"], top - 0.1, M["parapet"],
                               collider=True)
        # gate posts at both ends of the parapet (marking where the opening starts, look_refs study) — metal.
        #   The post foot is buried −0.05 below the top face of the open-side (lower) step → prevents floating
        r_mid = (pp["r_in"] + pp["r_out"]) / 2.0
        for tag, top, ang in (
                ("entry", _step_top(ac["parapet_first"]),
                 w["a0"] + ac["parapet_first"] * w["sector_deg"]),
                ("exit", _step_top(ac["parapet_last"] + 1),
                 w["a0"] + (ac["parapet_last"] + 1) * w["sector_deg"])):
            a = math.radians(ang)
            sc.add_cylinder(stage, f"/World/Scene19/GatePost_{tag}",
                            (cx + r_mid * math.cos(a), cy + r_mid * math.sin(a),
                             top - 0.05 + ac["post_h"] / 2.0),
                            ac["post_r"], ac["post_h"], M["rail"])

    # -------------------------------------------------------------------
    # [accessibility v2] upper threshold + edge guard — walk continuity (look_refs study)
    # -------------------------------------------------------------------
    def build_access(M):
        ac = PARAMS["access"]
        up = PARAMS["upper"]
        low_z = PARAMS["lower"]["top_z"]
        # threshold sliver: fills the gap between the sidewalk (z0) and the entry sector outer arc with sidewalk paving.
        #   The band biting inward (r<4) is buried outside the entry steps (step0/1) → the effective tread
        #   boundary stays consistently at x=3.86
        th = ac["threshold"]
        sc.add_box(stage, "/World/Scene19/Threshold",
                   ((th["x0"] + up["x0"]) / 2.0, (th["y0"] + th["y1"]) / 2.0,
                    (up["top_z"] + low_z) / 2.0),
                   (up["x0"] - th["x0"], th["y1"] - th["y0"],
                    up["top_z"] - low_z), M["upper"], collider=True)
        # edge guard retaining wall: guards the sidewalk edge north of the threshold (a 1.95 drop to the corner slab).
        #   From the corner slab top face (−1.95) up to +1.0 above the sidewalk
        gd = ac["guard"]
        sc.add_box(stage, "/World/Scene19/EdgeGuard",
                   ((gd["x0"] + gd["x1"]) / 2.0, (gd["y0"] + gd["y1"]) / 2.0,
                    (low_z + gd["h_top"]) / 2.0),
                   (gd["x1"] - gd["x0"], gd["y1"] - gd["y0"],
                    gd["h_top"] - low_z), M["parapet"], collider=True)

    # -------------------------------------------------------------------
    # [rooftop v3] rooftop parapet (perimeter guard) + plant props + rooftop door
    #   — scene context cues (plant back-inference · scale anchor). Hazard geometry (winder) unchanged.
    # -------------------------------------------------------------------
    def build_rooftop(M):
        rf = PARAMS["roof"]
        up, lo = PARAMS["upper"], PARAMS["lower"]
        t, h, hi = rf["pp_t"], rf["pp_h"], rf["pp_h_inner"]

        cw = rf["coping_w"]
        tu = rf["turnup_h"]

        def pp(tag, x0, x1, y0, y1, base, hh, ref=None):
            sc.add_box(stage, f"/World/Scene19/RoofPP_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        base - 0.05 + (hh + 0.05) / 2.0),
                       (x1 - x0, y1 - y0, hh + 0.05), M["parapet"],
                       collider=True)
            ref = ref or up                    # deck this parapet belongs to
            # [W2-D · spec §5.6 19-2] **turn-up + coping**.
            #   ① turn-up: the waterproofing coat wraps the parapet's inner
            #      face for `turnup_h` (0.30 m) — it is the same green as the
            #      deck, not concrete. `[spec-doc]` "coated wrapping the whole of the inner wall and the top".
            #   ② coping: a cap `coping_w` (0.45~0.55) wide **centred** on the
            #      parapet, so it overhangs 0.125 m each side with a drip edge
            #      instead of cantilevering over the deck. Both are 12 mm
            #      plates — no GT change, no camera occlusion (the roof_context
            #      eye sits at z 1.9, above the 1.15~1.20 parapet crown).
            #   Orientation is derived from the box: the long axis is the run,
            #   the short axis is the thickness, and "inner" is the side that
            #   faces the centre of the deck this parapet belongs to (`ref`) —
            #   passing `ref` matters for the lower terrace ring, whose
            #   east parapet has the deck on its **-X** side, the opposite of
            #   the upper deck's.
            sx, sy = x1 - x0, y1 - y0
            cxm, cym = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            top = base - 0.05 + (hh + 0.05)
            if sx <= sy:                       # runs along Y, thickness in X
                inner = 1.0 if cxm < (ref["x0"] + ref["x1"]) / 2.0 else -1.0
                sc.add_box(stage, f"/World/Scene19/RoofTurn_{tag}",
                           (cxm + inner * (sx / 2.0 + 0.006), cym,
                            base + tu / 2.0), (0.012, sy, tu), M["coating"])
                sc.add_box(stage, f"/World/Scene19/RoofCope_{tag}",
                           (cxm, cym, top + 0.006),
                           (cw, sy, 0.012), M["parapet"])
            else:                              # runs along X, thickness in Y
                inner = 1.0 if cym < (ref["y0"] + ref["y1"]) / 2.0 else -1.0
                sc.add_box(stage, f"/World/Scene19/RoofTurn_{tag}",
                           (cxm, cym + inner * (sy / 2.0 + 0.006),
                            base + tu / 2.0), (sx, 0.012, tu), M["coating"])
                sc.add_box(stage, f"/World/Scene19/RoofCope_{tag}",
                           (cxm, cym, top + 0.006),
                           (sx, cw, 0.012), M["parapet"])

        # upper rooftop (z0) perimeter: east (x1) · south (y0) · west (x0, south end..L wall y0) · north (lower terrace boundary)
        pp("U_E", up["x1"] - t, up["x1"], up["y0"], up["y1"], up["top_z"], h)
        pp("U_S", up["x0"], up["x1"] - t, up["y0"], up["y0"] + t, up["top_z"], h)
        pp("U_W", up["x0"], up["x0"] + t, up["y0"] + t, -1.0, up["top_z"], h)
        pp("U_N", up["x0"], up["x1"], up["y1"] - t, up["y1"], up["top_z"], hi)
        # lower terrace (−1.95) perimeter: west (x0) · north (y1) · east (x1, outside the upper body, y>4)
        pp("L_W", lo["x0"], lo["x0"] + t, lo["y0"], lo["y1"], lo["top_z"], h, lo)
        pp("L_N", lo["x0"] + t, lo["x1"], lo["y1"] - t, lo["y1"], lo["top_z"], h, lo)
        pp("L_E", lo["x1"] - t, lo["x1"], lo["y0"], lo["y1"] - t, lo["top_z"], h, lo)

        # HVAC units (0.1 plinth + body) + gooseneck vent + pipe run — upper rooftop
        hs = rf["hvac_size"]
        for i, u in enumerate(rf["hvac"]):
            sc.add_box(stage, f"/World/Scene19/HvacBase_{i}",
                       (u["cx"], u["cy"], up["top_z"] + 0.05),
                       (hs[0] + 0.1, hs[1] + 0.1, 0.1), M["granite"])
            sc.add_box(stage, f"/World/Scene19/Hvac_{i}",
                       (u["cx"], u["cy"], up["top_z"] + 0.1 + hs[2] / 2.0),
                       hs, M["hvac"])
        v = rf["vent"]
        sc.add_cylinder(stage, "/World/Scene19/Vent",
                        (v["cx"], v["cy"], up["top_z"] + v["h"] / 2.0),
                        v["r"], v["h"], M["hvac"])
        sc.add_cylinder(stage, "/World/Scene19/VentCap",
                        (v["cx"] + v["r"] * 1.2, v["cy"],
                         up["top_z"] + v["h"] + v["r"] * 0.4),
                        v["r"] * 0.9, v["r"] * 2.6, M["hvac"], rotY=90.0)
        p = rf["pipe"]
        sc.add_cylinder(stage, "/World/Scene19/PipeRun",
                        ((p["x0"] + p["x1"]) / 2.0, p["y"],
                         up["top_z"] + p["r"] + 0.02),
                        p["r"], p["x1"] - p["x0"], M["hvac"], rotY=90.0)
        # rooftop steel door — at upper terrace level on the L wall south end face (x=4, width 1m).
        #   Right beside the entry threshold, so the route "out of the rooftop core and onto the corner stairs" reads.
        d = rf["door"]
        ws = PARAMS["walls"]["south"]
        sc.add_box(stage, "/World/Scene19/CoreDoor",
                   (ws["x1"] + 0.02, (ws["y0"] + ws["y1"]) / 2.0,
                    up["top_z"] + d["h"] / 2.0),
                   (0.04, d["w"], d["h"]), M["door"])

    # -------------------------------------------------------------------
    # dressing — planter + distant buildings + [rooftop v3] rooftop context elements
    # -------------------------------------------------------------------
    def build_dressing(M):
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        pl = PARAMS["roof"]["planter"]     # [rooftop v4] position comes from the single source PARAMS
        sc.build_planter(stage, "/World/Scene19/Planter_A",
                         pl["cx"], pl["cy"], 0.0,
                         M["granite"], M["grass"], tree_mtls=tree_mtls,
                         size=pl["size"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene19/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])
        build_rooftop(M)

    # -------------------------------------------------------------------
    # cue toggles (geometry unchanged)
    # -------------------------------------------------------------------
    def build_cues(M):
        w = PARAMS["winder"]
        pp = PARAMS["parapet"]
        # cue_railing: handrail on the parapet top (per-step arc cap) — only on the parapet-retained span
        if cfg.get("cue_railing"):
            ac = PARAMS["access"]
            for i in range(ac["parapet_first"], ac["parapet_last"] + 1):
                a0 = w["a0"] + i * w["sector_deg"]
                top = _step_top(i) + pp["h"]
                sc.build_arc_steps(stage, f"/World/Scene19/Rail_{i}", cx, cy,
                                   pp["r_out"] - 0.06, pp["r_out"], a0,
                                   a0 + w["sector_deg"], 1, top + 0.06,
                                   top - 0.06, M["rail"], collider=False)
        # cue_tactile: warning tactile strip on the upper approach (in front of the first step)
        if cfg.get("cue_tactile"):
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, "/World/Scene19/Tactile",
                             4.1, 4.5, -1.0, 1.0, tac, z=0.0)
        # cue_nosing: radial nosing anti-slip arc bands
        if cfg.get("cue_nosing"):
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i in range(w["n"]):
                a0 = w["a0"] + i * w["sector_deg"]
                top = _step_top(i)
                sc.build_arc_steps(stage, f"/World/Scene19/Nosing_{i}", cx, cy,
                                   w["r_out"] - 0.06, w["r_out"], a0,
                                   a0 + w["sector_deg"], 1, top + 0.004,
                                   top - 0.02, nos, collider=False)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_ground(M)
    build_walkways(M, hazard)
    if hazard:
        build_winder(M)
        build_access(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if hazard:
        build_cues(M)
    build_ground_kit(M)             # [W2-D] ground elements — after the dressing (scatter order convention)
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        nprim = sum(1 for pr in stage.Traverse() if pr.IsA(UsdGeom.Gprim))
        print(f"SMOKE_OK prims={nprim}")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

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

    VIEWS = build_views()
    _v0 = VIEWS["upper_approach"]
    look_from(_v0["eye"], _v0["tgt"])

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene19_{ts}.png")
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
