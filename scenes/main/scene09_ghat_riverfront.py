# -*- coding: utf-8 -*-
"""
scene09_ghat_riverfront.py — NegObs synthetic scene 9: lake park waterfront stairs
(Isaac Sim 4.5)

Spec : Docs/briefs/multi_scene_brief_v5.md §R4 (replaces the old v3 §D scene09)
Shared library : scene_common.py / skeleton convention : scene03_riverbank.py

[v5 adopted] Stage reinterpretation: an Indian 'ghat' → **lake park waterfront viewing stairs**.
  ** geometry entirely unchanged ** — 36 steps, riser table, 2 landings, embankment, water z all as before.
  Only the dressing is swapped, to strip out the religious colour:
    ghat pavilions (chhatri) 2 → waterfront pavilion 1 (samojeong: 4 posts + hip roof)
    mooring bollards 8  → deck piles 8 (r 0.13→0.09, h 1.1→0.50)
    rowing boats 2      → duck boat 1 (white box hull + approximated head)
    (new) timber boardwalk connection · reed stands · sign_info (lake park guide)
    (new) moss tint — the 2 steps just below the water (with the water-mark band, showing the water-level history)

[v6 judgment rework] "unclear intent unresolved" — the reinterpretation elements were **only in the
  code and appeared in no cut**. Leaving the stair and water geometry alone, all 4 readability axes are reworked:
  (1) pavilion : concrete box → **timber samojeong**. Stone plinth + timber floor (wood) + 4 posts (wood) +
            tie beam + 2-tier eave line + **4-sided sloping hip roof mesh (corner lift)** + finial.
            It also moves to x −5.4..−1.0 / y 6.2..10.6 (25 m from the water → 13~15 m).
  (2) duck boat: box hull → **an assembly of ellipsoids** (hull, breast, stern, wings) + curved head and
            beak, yellow tint (white 0.86 → 0.78/0.70/0.25). y 10.5 → 3.0, pulling it inside the FOV of
            across_river, from_river and park_vista.
  (3) materials: the stair and terrace stone goes from **sandstone (ghat pink-beige) → plaza_light granite**
            (+ 2 lawn bands on the upper terrace · 10 street trees) = a park impression.
  (4) camera: **park_vista added** — a mise-en-scene cut holding the pavilion, deck, lawn, stair head,
            waterline and duck boat in one frame (bearing/elevation checks in the view comments).
  Incidental: canopy and distant silhouette albedo raised (easing the black-band alternative).

Type (ultra-wide waterfront stairs): **ultra-wide stone stairs x a horizontal water boundary**.
  A 10m wide flight of 36 granite steps (uneven riser table) descends to the water, with 2 mid landings.
  The water submerges the bottom 6 steps → **the boundary where the water cuts horizontally across the
  middle of the stairs** is the only fixed drop anchor. A water-mark tint band emphasises the waterline.
  Distinguished from T5 (river): all stone, ultra-wide, landings.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene09_ghat_riverfront.py

[v7 judgment rework] judge_v7_rt_A §6 — 2 items owned here.
  (1) [top-priority bug] the pavilion hip-roof mesh is **near-white, the exact opposite of its albedo**
     (176,179,186) — 1.6x the finial (107,116,128), which is the same material.
     → the cause is **normals never authored** in `build_hip_roof` (the smoothed normals blur the
       21.8 deg slope faces and the vertical eave band into 'white tent' shading). Author faceVarying
       face normals + state orientation/doubleSided. Check `roof_normal_selfcheck()`:
       the geometric Lambert upper-bound ratio is only 1.10x → the measured 1.6x is confirmed as a normals problem.
  (2) the stone tone swap landed as a **large near-white area** (paving 223 · violates §4).
     → `stone_tint` 0.90 → 0.64 (recommended 0.62~0.68). The water-mark and moss tints drop by the
       same ratio, **preserving the contrast ratio** (the waterline = this scene's only drop anchor).
  (3) (shared) new §4 large-near-white-area self-check `albedo_selfcheck()`.
  Not addressed (out of scope): judgment (c) re-aiming `ghat_walk` · (d) raising the far-bank black silhouette.

[v8 judgment rework — Y1] judge_v8_rt §4 (1) "roof shading pixels unchanged (0 delta)".
  **The v7 normals hypothesis is rejected.** The v7↔v8 roof pixel diff of 0.0 % is the evidence:
  in reality **flat (face-normal) shading was already in effect before any normals were authored** —
  in the v8 render the ridges stand angular and the shaded face (-X) separates into its own tone step.
  ⇒ the rewritten faceVarying normals equal what the renderer was already using → 0 delta.

  **The real cause = only `M["pav_roof"]` leaves `specular_level` unset (OmniPBR default 0.5).**
  3 pieces of evidence (all measured from the existing v8_rt PNG · no render needed):
   (a) binding and normals are innocent. The v8 smoke log already prints both Roof and Finial as
     `/World/Looks/PavRoof` · normals 64 faceVarying.
   (b) **diffuse alone does not add up.** The roof faces visible in park_vista are only the
     +Y group (Lambert 0.840) and the −X group (0.508); fitting those two to `resp = S·lam + K`
     gives **K = −0.87** (a negative ambient) — physically impossible.
     ⇒ there must be a **view-dependent term** that Lambert cannot explain.
   (c) taking the out-of-lobe face (−X, N·H 0.39~0.48) and the horizontal paving as diffuse anchors,
     S 1.360 / K 0.749 → a predicted diffuse response of **1.892** on the +Y faces (matching the scene's
     `_ALBEDO_GAIN` 1.77) → predicted sRGB (147,152,160). The measurement is (180,183,190).
     **The excess is the same +0.164 linear in all 3 channels** = not an albedo error but an
     **additive reflection term**. Along the park_vista sight line the half vector gives N·H 0.78~0.79
     (38 deg) on the +Y faces — dead centre of the wide GGX lobe at roughness 0.72.
   (d) the finial being dark has the same explanation. A cylinder sweeps its normals continuously, so
     only **a single thin column** falls in the lobe — and indeed the measurement gives a bright column of
     157~163 against a body of 111. The judgment's "1.6x in the same material" compared the roof's
     **specular additive face** with the finial's **diffuse body** (column against column it is 1.20x = within the geometric bound).
  Fix (1): `specular_level=0.0` on `pav_roof` — unglazed Korean roof tile is matte, and every other
    matte material in this scene (reed/far/canopy_a/canopy_b) is already 0.0.
    Only `pav_roof` was missing it.
  Fix (2): `roof_tile_color` x0.70 → (0.109,0.116,0.130). The real reflectance band of dark grey
    unglazed tile is 0.10~0.15. Fix (1) alone leaves (147,152,160) = still a light grey.
  Prediction (the S/K model above): +Y roof faces (125,129,136) · −X roof faces (110,114,120) ·
    eave bands (103,106,111)/(81,83,88) → the ordering eave band < roof face also holds.
  ※ the judgment's fallback (rebuilding from 4 _oriented_box planes) was **not adopted** — the mesh is
    not the culprit (flat shading and binding are fine), so switching to boxes would keep the same
    specular addition at the same material and orientation, and would only lose the corner lift.

Auto capture : NEGOBS_CAPTURE=1 python scene09_ghat_riverfront.py
Assembly smoke: NEGOBS_SMOKE=1 python scene09_ghat_riverfront.py
Self-check   : NEGOBS_SELFCHECK=1 python scene09_ghat_riverfront.py  (no boot)

Coordinates: Z-up, m, travel axis +X (descending toward the river). Stair head = x=0 (z=0).

────────────────────────────────────────────────────────────────────────────
Geometry core (director's supplement applied):
  · riser table = [0.14,0.16,0.18,0.20,0.18,0.16] repeating (fixed list, 0.14~0.20),
    tread 0.34. 2 mid landings = the tread of steps 12 and 24 set to 1.2 (a deep tread = a landing).
  · the stair top-face z is accumulated directly → **water z = top face of the 6th step from the bottom +0.05**
    (so the bottom 6 steps end up under water). The brief's z~-4.2 is an approximate hint; the formula wins.
  · submerged part: steps in the 1.5-step band above the water are swapped for a **separate water-mark
    material (stone texture + stain_tint)** — geometry unchanged (only the per-step add_box material branches).
────────────────────────────────────────────────────────────────────────────
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
# [A] SCENE_CONFIG — standard 7 keys. Ghat stairs have no railing by custom (cue_railing default False).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → stairs and banks flattened to z=0
    "cue_railing":        False,   # waterfront viewing stairs, no railing (custom) — code path reserved only
    # [v5] non-conventional (waterfront deck) scene → cue_tactile stays False (brief v5 shared layer)
    "cue_tactile":        False,   # unused (code path only)
    "cue_material_break": True,    # upper terrace vs stair material contrast (both granite,
                                   #   terrace gets no tint). False→terrace also in stain tone
    "cue_sign":           True,    # [v5 shared layer] sign_info (lake park guide) x1
    "cue_scene_dressing": True,    # pavilion, deck piles, boardwalk, reeds, far-side woods together
    "cue_nosing":         False,   # unused (code path only)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
# uneven riser table (0.14~0.20 repeating) — fixed list guarantees reproducibility
_RISER_CYCLE = [0.14, 0.16, 0.18, 0.20, 0.18, 0.16]   # sum 1.02 / 6 steps
_RISER_MU = sum(_RISER_CYCLE) / len(_RISER_CYCLE)       # 0.17

PARAMS = dict(
    stairs=dict(x0=0.0, nsteps=36, tread=0.34, y0=-5.0, y1=5.0, z_top=0.0,
                base_pad=0.6,                  # base_z = bottom step top face - base_pad
                landing_steps=[11, 23],        # steps 12 and 24 (0-based) = mid landings
                landing_tread=1.2,             # landing depth
                submerge_from_bottom=6,         # bottom 6 steps submerged (water level datum)
                # [W2-D Sec.5.7 row 09] "stair water-mark band 1.5 -> 3 steps".
                #   The waterline is this scene's only fixed drop anchor, and a
                #   1.5-step band is thinner than one riser at grazing angle.
                stain_band_steps=3.0),          # water-mark tint over the 3-step band above the water
    water_extra=0.05,                          # water z = top face of the 6th step + 0.05
    # === [W2-D ground_kit] P2 `plaza_water` - spec Sec.5.7 row 09 ==========
    #  Natural scene (`natural=True`): manhole / gully / gutter / marking all
    #  raise. The whole near-window prescription is joints + slab loss + film.
    #    09-1 slab joints made geometric, 5-9 mm wide, 1-2 mm recess-as-tone
    #    09-2 slab loss ("flagstone loss") 4-6 per 100 m^2 -> patch field
    #    09-3 water film / algae decals
    #  step_x/step_y = 1.80 m override. The P2 table ships step_x = 19.80 m
    #  (`step_expansion_ghat`, the *expansion* joint period) and `_compose_ops`
    #  emits exactly one joint op, so over an 11.2 m approach corridor the
    #  profile default yields **zero** joint lines - the opposite of what
    #  Sec.5.7 asks for. 1.80 m = 3 x the 0.600 granite cell, so Sec.4.5 U2
    #  holds, and the 19.80 m expansion joint stays a multiple of it (11x).
    #  Dropped from the profile: `silt_band` and `edge_break`. Neither has a
    #  target here - the silt band belongs on the submerged steps (handled by
    #  the scene's own stain/moss banding, widened above) and the terrace has
    #  no material boundary inside the frame (the lawns start at |y| = 12,
    #  outside the 5.77 m half-width at X = 10 m) [calc].
    gkit=dict(
        region=(-12.0, -5.0, -0.80, 5.0),
        joint_step=1.80,                       # 3 x granite cell 0.600 [computed]
        #  One slab-loss patch per preset near-window; |y| small because the
        #  frame half-width in W1 is 0.43 m (d2) / 0.81 m (d5, d10) [computed].
        patches=((-1.30, 0.20), (-3.70, -0.30), (-8.70, 0.40)),
        patch_n=5,                             # 4-6 per 100 m^2 x 112 m^2
        seed=9,
    ),
    # Upper terrace (flat sandstone, z=0). [A-09-2] x0 −12 → −30: fixes the d10 grid view (eye x=−10)
    #   having nothing but void right behind it.
    terrace=dict(x0=-30.0, x1=0.0, y0=-40.0, y1=40.0, z_top=0.0, thick=0.5),
    # Left/right embankments : [A-09-1] build_slope (linear plane) → replaced by a **stepped
    #   form on the same riser table as the stairs**. The z gap between linear slope and discrete steps along y=±5
    #   made a sawtooth groove/lip of up to 0.315 m (landing run) (over the 0.2 judgment threshold).
    #   It uses the same (xa, xb, tz, base_z), so the seam error = 0.
    embankment=dict(y_edge=40.0),
    # Water : from the stair submergence line to the far side (river width ~30m)
    water=dict(x_far=44.0, y0=-40.0, y1=40.0),
    # Far-side bank (sandstone) + tree line
    #   [B-09-2] above_water 0.3 → 1.6 / hedge 2.0 → 3.6 / trees 3 → 8 + 2 buildings:
    #   fixes the horizon-closure failure where the top half of the frame was uniform teal (an 'infinity pool').
    #   [v5 judgment] thick 0.6 → 2.4: the bottom face was fb_z − thick = water_z + 1.6 − 0.6
    #   = −4.19, floating 1.0 m above the water (−5.19) → sky leaked under the slab and put a
    #   hard-edged white band (RGB 183–197) on the horizon of every water cut. At 2.4 the bottom face
    #   sits at water_z − 0.8, safely submerged, and the top face z (fb_z) is unchanged, so the B-09-2
    #   horizon-closure effect and the hedge/tree/building base_z all stay as they were.
    far_bank=dict(x0=44.0, x1=74.0, y0=-40.0, y1=40.0, above_water=1.6,
                  thick=2.4),
    far_hedge=dict(cx=52.0, sx=1.4, length=24.0, h=3.6),
    far_hedges=[dict(cy=-24.0), dict(cy=0.0), dict(cy=24.0)],
    far_trees=[dict(cx=56.0, cy=-28.0), dict(cx=57.5, cy=-20.0),
               dict(cx=55.5, cy=-11.0), dict(cx=57.0, cy=-3.0),
               dict(cx=55.5, cy=5.0), dict(cx=57.5, cy=13.0),
               dict(cx=56.0, cy=21.0), dict(cx=57.0, cy=29.0)],
    # Far-side building silhouettes 2 (dark constant colour) — a distant layer 3 tiers deep
    far_buildings=[dict(x0=66.0, x1=72.0, cy=14.0, sy=12.0, h=7.0),
                   dict(x0=66.0, x1=72.0, cy=-14.0, sy=12.0, h=7.0)],
    # [v5 adopted] mooring bollard → **waterfront boundary pile**: religious and ferry-landing colour removed,
    #   scaled down to a stair-head boundary pile for a waterfront park. r 0.13→0.09, h 1.1→0.50.
    #   [v6] the |y| 8.5 pair is deleted — it falls under the new pavilion eaves (x −7.25..−1.15, y 5.35..11.45)
    #   and overlaps them. The remaining 6 are spaced 3.8/9.7/5.5, i.e. unevenly
    #   (§3 bans even spacing), which is actually a better fit.
    mooring=[dict(cx=-1.2, cy=3.8), dict(cx=-1.2, cy=-3.8),
             dict(cx=-1.2, cy=13.5), dict(cx=-1.2, cy=-13.5),
             dict(cx=-1.2, cy=19.0), dict(cx=-1.2, cy=-19.0)],
    mooring_r=0.09, mooring_h=0.50,

    # --- context dressing (must read as "lake park waterfront stairs") ---
    # [v6 rework (1)] waterfront pavilion (samojeong) — clears the old "achromatic concrete box" judgment.
    #   Real-world proportions (customary dimensions of a Korean traditional timber samojeong):
    #     bay (post centre spacing) 4.4 m · post diameter 0.26 (1/17 of the bay)
    #     post height 2.30 (0.52 of the bay) · eave overhang 0.85 (0.37 of post height)
    #     roof pitch = rise 1.15 / eave half-width 3.05 → 20.7 deg (~ traditional 4-5 chi pitch)
    #     corner lift (eave-tip rise) 0.16 · finial r0.11 h0.42
    #   The old parameters (z_roof/roof_t/cap_shrink/cap_t) were flat-roof only and are retired.
    #   Relocation : the old (x −9.0..−5.8, y 6.4..9.6) was, from from_river/across_river,
    #     25~30 m away (6 % of frame width) and unreadable. Pull it toward the stair head and
    #     grow one side 3.2 → 4.4 m → 20 % of frame width at 29.4 m in from_river,
    #     17 % at 33.2 m in across_river, 39 % at 14.9 m in the new park_vista.
    #   Safety : y0 6.6 > stair width 5.0 (1.6 m clear) · x1 = −1.54 including the plinth overhang,
    #     and even the **eave tip** (the most projecting point) at x −1.15 / y 5.75 → from the stair-head corner (x=0)
    #     1.15 m · 0.75 m from the stair-width boundary, 0 objects on the ground → **hazard geometry unchanged**.
    #   Grid preset FOV check (eye x −2/−5/−10 @ y=0, +-30 deg): the nearest eave corner
    #     (−1.15, 5.75) bears 81.6 deg / 56.2 deg / **33.0 deg** = all outside the FOV →
    #     **the pavilion never enters a concealment preset** (no effect on grazing concealment).
    #     ghat_walk(−4,0) is out too, at 63.6 deg.
    pavilion=dict(x0=-6.4, x1=-2.0, y0=6.6, y1=11.0,
                  base_t=0.22, base_over=0.46,      # stone plinth
                  floor_t=0.23, floor_over=0.30,    # timber raised floor
                  post_r=0.13, post_h=2.30,         # 4 posts
                  beam_t=0.20, beam_w=0.15,         # changbang (head tie beam)
                  eave_over=0.85, eave_t=0.10,      # eave line tier 1 (rafter layer)
                  fascia_inset=0.18, fascia_t=0.09,  # eave line tier 2 (buyeon / tiled eave)
                  roof_rise=1.15, corner_lift=0.16,  # 4-sided slope + corner lift
                  finial_r=0.11, finial_h=0.42,
                  rail_h=0.44, rail_t=0.07, rail_post_r=0.035, rail_n=3),
    # 4 landing marker stone posts — outside the stair width (y±5). Reads the ultra-wide scale and landing positions
    land_posts=dict(r=0.24, h=2.1, ys=(-5.6, 5.6)),
    # [v6 rework (3)] 2 lawn bands on the upper terrace — puts the evidence for "park" into the frame.
    #   Outside the stair width (y±5) · inside the terrace (x −30..0, y ±40). Top face proud by 0.03 (walk continuity).
    #   How it reads: left/right lawn faces in park_vista; in from_river/across_river
    #   only the **street-tree canopies** rise above the terrace ridge line, forming a green skyline.
    lawns=[dict(x0=-24.0, x1=-0.8, y0=12.0, y1=30.0),
           dict(x0=-24.0, x1=-0.8, y0=-30.0, y1=-12.0)],
    lawn_proud=0.03,
    # 10 street trees — on the lawn bands, irregular layout (§3 bans grids and even spacing).
    #   From park_vista (eye −9.6, 22) the nearest is 6.1 m away and all sit outside the +-30 deg FOV →
    #   zero foreground intrusion. From from_river(23.92,0)/across_river(27.96,0) they
    #   bear −18.9 deg~+25.7 deg = inside the frame (canopy elevation 11.4 deg, within the half-vertical +-18 deg).
    park_trees=[(-13.4, 17.2), (-19.8, 15.0), (-16.4, 24.6),
                (-22.6, 21.8), (-12.2, 27.4),
                (-13.0, -17.8), (-19.2, -15.6), (-16.8, -25.0),
                (-22.2, -22.4), (-12.6, -27.0)],
    # 4 benches (river view) — [§3] beside anchors (pavilion · lawn band edge · deck) · yaw jitter
    #   0/1 : 1.14 m from the pavilion plinth N/S faces (|y| 11.46), on the lawn band start line (|y| 12)
    #   2/3 : 1.0 m from the deck's west side (x0 −10.0), on the lawn band
    benches=[(-4.6, 12.6, 86.5), (-4.6, -12.6, 274.0),
             (-11.0, 13.4, 93.5), (-11.0, -13.4, 265.5)],
    # [v6 rework (2)] 1 duck boat — box assembly → **ellipsoid (scaled sphere) assembly**.
    #   Judgment: "white untextured box + plank neck" → hull, breast, stern and wings go curved,
    #   and the canopy goes from a thick box (h 0.45) to a thin plate (0.05) + 4 posts.
    #   Position (18.5, 10.5) → **(15.4, 3.0)** : clears the judgment "bears 47.9 deg from across_river
    #     so it is outside the FOV / half cropped at the top-left of ghat_walk". Re-check (FOV +-30 deg,
    #     including both ends of the 3.07 m hull length):
    #       from_river(23.92,0)  −19.4 deg (9.03 m, −29.0..−9.8 deg)  all inside
    #       across_river(27.96,0) −13.4 deg (12.91 m, −20.2..−6.6 deg) all inside
    #       park_vista(−10.2,22)  +20.6 deg (31.9 m, +17.9..+23.3 deg) all inside
    #   Heading rotz 62 deg : 87 deg / 90 deg to the sight lines of the two water cuts (−25.4 deg / 152.3 deg) →
    #     **side silhouette from both** (the angle at which a duck reads most easily).
    #   Stair interference : after the rotz 62 deg rotation the rearmost hull x = 15.4 − (1.525·cos62 +
    #     0.69·sin62) = 14.08 → 0.12 m clear in plan of the bottom step (x1 13.96).
    #     Even if they overlapped in plan, the submerged step top (−6.12) vs the hull bottom (water_z − 0.24 = −5.43)
    #     gives **0.69 m of vertical clearance** → 0 contact. Stair and water geometry unchanged.
    boats=[dict(cx=15.4, cy=3.0, rotz=62.0)],
    boat=dict(hull=(1.30, 0.62, 0.36),      # hull radii (ellipsoid scale)
              breast=(0.62, 0.52, 0.42), stern=(0.42, 0.34, 0.26),
              wing=(0.62, 0.14, 0.24), wing_dy=0.55,
              neck_r=0.115, neck_h=0.60, neck_lean=12.0,
              head=(0.24, 0.20, 0.20), beak=(0.30, 0.13, 0.09),
              canopy=(1.15, 1.10, 0.05), canopy_post_r=0.03,
              hull_float=0.12),             # how far the hull centre floats above the water
    # [v5 adopted] timber boardwalk — waterfront promenade on the upper terrace.
    #   [v6] x −4.0..−1.6 → **−10.0..−7.6** : swaps places with the new pavilion (plinth x −6.86..−1.54).
    #   0.74 m clear of the pavilion plinth and 7.6 m clear of the stair head (x=0)
    #   → the hazard geometry margin actually grows.
    #   [v6] plank seam spacing 2.0 → 0.62 m : a 2 m plank width read as 'wooden floor'.
    #   0.62 m is the width of a 3~4 board bundle = the minimum density at which the grain still stands at distance.
    deck=dict(x0=-10.0, x1=-7.6, y0=-22.0, y1=22.0, top_z=0.06,
              seam_step=0.62, seam_w=0.035, seam_drop=0.010),
    # [v5 adopted] reed stands — the embankment near the waterline (**outside** the stair width y±5) and the far bank.
    #   (cx, cy, n, seed). x 12.2~13.6 = just below the waterline (water_x0≈11.92) →
    #   reeds appear to rise out of the water. No interference with the hazard geometry (stairs y±5).
    reeds=[(12.2, -8.5, 9, 11), (12.9, -13.0, 11, 12), (12.2, -18.0, 9, 13),
           (13.6, -24.0, 12, 14),
           (12.2, 8.5, 9, 21), (12.9, 13.0, 11, 22), (12.2, 18.0, 9, 23),
           (13.6, 24.0, 12, 24),
           (45.6, -14.0, 10, 41), (45.6, 14.0, 10, 42)],
    reed=dict(r=0.022, h_lo=1.1, h_hi=1.9, spread=0.85, tilt=9.0),
    # [v5 shared layer] Korean sign — (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   [v6] Info (−6.5, 5.5) → **(−7.0, −5.6)** : the +Y side is filled by the pavilion (plinth y 5.74~)
    #     and the deck (x −10.0..−7.6), leaving no room → moved to the symmetric position on the south side.
    #     0.6 m from the deck's east end, 0.6 m outside the stair width (y±5).
    #   Camera check (FOV +-30 deg): grid eye=(−2/−5/−10, 0) → behind / behind /
    #     −61.8 deg (out), ghat_walk(−4,0) −118.2 deg (out), waterline faces the +X water side → behind.
    #     from_river(23.92,0) +10.3 deg (31.4 m, distant) · park_vista −26.2 deg (27.8 m,
    #     bottom-left of frame) = the sign board enters the mise-en-scene cut with 0 sight-line occlusion.
    signs=[("Info", "sign_info", -7.0, -5.6, 0.0, 180.0, 1.0, 0.75)],

    material=dict(
        # [v6 rework (3)] stone role sandstone → **plaza_light** (light granite paving).
        #   The pink-beige sandstone of an Indian ghat was the main culprit keeping the "ghat" reading alive.
        #   No effect on hazard geometry or concealment behaviour (every step + terrace + embankment share
        #   one material, so homogeneity is unchanged). scale 1.5 → 1.1 (granite slab tile size).
        scale=dict(stone=1.1, grass=1.4, wood_dark=0.9, wood_fine=0.45),
        # [v7 judgment §6 (3)] the stone tone swap landed as a **large near-white area**.
        #   `ghat_walk` paving RGB (223,222,221) · 65 % of the frame,
        #   and in `from_river` the 36 steps fused into "one white retaining wall", losing all step articulation.
        #   Judgment recommendation (b), lowering 0.86 → 0.62~0.68, is adopted as is (the 0.64 family).
        #   plaza_light diff linear mean 0.469 × 0.64 = **albedo 0.300**
        #   (real grey granite sits in the 0.2~0.35 band) → expected render sRGB 0.75 ~ 191.
        #   ** geometry and concealment behaviour unchanged ** — every step, terrace and embankment still share one material.
        stone_tint=(0.64, 0.63, 0.60),         # was (0.90,0.89,0.86)
        # [v5 adopted] moss tint — the 2 steps just below the water (the 'wet band' of the water-level history).
        # [v7] **contrast ratio preserved** to match the stone_tint reduction (0.90→0.64).
        #   old moss/stone = 0.30/0.90 = 0.333 → new 0.64×0.333 = 0.213.
        #   (dropping the absolute value alone would kill the waterline cue with it — this scene's only drop anchor)
        moss_tint=(0.213, 0.284, 0.185),       # was (0.30,0.40,0.26)
        deck_tint=(0.95, 0.88, 0.78),          # timber boardwalk (grey weathered wood)
        seam_color=(0.030, 0.026, 0.022),      # deck plank seams (dark-colour rule)
        # [v6 (1)] pavilion timber members — posts, tie beams, railing (reddish-brown pine) / raised floor (light floorboard)
        pav_wood_tint=(0.68, 0.44, 0.28), pav_floor_tint=(0.78, 0.60, 0.42),
        # [v8 judgment §4 (1)] the near-white roof was really a **specular additive term** (module
        #   docstring [v8 Y1] (b)(c)). Killing that term with `specular_level=0.0` leaves diffuse
        #   only, at (147,152,160) — still a light grey, so the albedo also drops x0.70.
        #   0.109~0.130 = the measured 0.10~0.15 reflectance band of dark grey unglazed tile.
        #   The colour ratio (1 : 1.064 : 1.193) is preserved as is.
        roof_tile_color=(0.109, 0.116, 0.130), roof_tile_rough=0.72,  # Korean roof tile
        roof_tile_specular=0.0,                # [v8 Y1] the cause — see the comment below
        # [v6 (2)] duck boat — white (0.86) → yellow (at or below the §4 near-white cap of 0.8)
        duck_color=(0.78, 0.70, 0.25), duck_rough=0.45,
        duck_top_color=(0.52, 0.19, 0.17), duck_top_rough=0.55,  # canopy (red)
        beak_color=(0.74, 0.42, 0.07), beak_rough=0.5,
        # [v6 side fix] 0.055/0.065/0.030 → raised. The reeds fused into black needles.
        reed_color=(0.110, 0.125, 0.060), reed_rough=1.0,
        # [B-09-4] 0.55 → 0.42: the water-mark band was weaker than the sandstone texture variation,
        #   so the waterline was not identifiable. (The contrast amount is kept identical after the stone swap.)
        # [v7] contrast ratio preserved for the same reason: old 0.42/0.90 = 0.467 → 0.64×0.467 = 0.299
        stain_tint=(0.299, 0.299, 0.263),      # was (0.42,0.42,0.37)
        grass_tint=(0.55, 0.68, 0.42),
        # [B-09-3] rough 0.10 → 0.15 (eases the uniform bright teal clipping)
        water_color=(0.06, 0.11, 0.12), water_rough=0.15,
        # [B-09-1] 0.34 → 0.10: under noon direct 2450 the bollards went pure white (PVC pipe)
        post_color=(0.10, 0.085, 0.07), post_rough=0.8,
        # [v6 side fix] judgment: "the whole far bank is an untextured black silhouette (p5 5.2/8.8)".
        #   Raise the distant silhouette and canopy albedo into the measured vegetation reflectance band (6~12 %).
        far_color=(0.130, 0.125, 0.118),       # distant building silhouette
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.055, 0.085, 0.035), canopy_b=(0.075, 0.115, 0.045),
        canopy_rough=1.0,
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
    # Director r1 — the standard 171.5 (az205) puts the +X-facing risers in shadow, turning the
    # sandstone stairs seen head-on into a black silhouette. → offset 0.0 (az33.5) lights the +X risers frontally (the sandstone comes alive).
    SUN_AZ_OFFSET=0.0,

    # [v8 Y1] the park_vista camera = **single source**. build_views (the assembler) and
    #   roof_specular_selfcheck (the checker) are made to read the same coordinates
    #   (scene04 `verge_instances` convention). roof_z = roof-face centroid z
    #   = z_fa 3.05 + fascia 0.09 + rise/3 0.383 ≒ 3.52.
    views_park_vista=dict(eye=[-10.2, 22.0, 3.8], tgt=[4.0, 0.0, -1.8],
                          roof_z=3.52),

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
# [C] paths / asset roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene09")

# [v6 rework (3)] sandstone → plaza_light (light granite paving)
ASSET_ROLES = ["plaza_light", "grass", "wood_dark", "sign_info", "hdri", "mdl"]


# ===========================================================================
# stair geometry precompute — (xa, xb, top_z) list + water level and water-mark band
# ===========================================================================
def compute_steps():
    st = PARAMS["stairs"]
    n = st["nsteps"]
    risers = [_RISER_CYCLE[i % len(_RISER_CYCLE)] for i in range(n)]
    treads = [st["tread"]] * n
    for li in st["landing_steps"]:
        treads[li] = st["landing_tread"]
    steps = []
    xa = float(st["x0"])
    z = float(st["z_top"])
    for i in range(n):
        z -= risers[i]                         # top face (tread) z of step i
        xb = xa + treads[i]
        steps.append((xa, xb, z))
        xa = xb
    z_bot = steps[-1][2]
    base_z = z_bot - st["base_pad"]
    # water z = top face of the k-th step from the bottom + water_extra
    k = st["submerge_from_bottom"]
    idx6 = n - k                               # index of the 6th step from the bottom (0-based)
    water_z = steps[idx6][2] + PARAMS["water_extra"]
    band_hi = water_z + st["stain_band_steps"] * _RISER_MU
    return steps, base_z, z_bot, water_z, band_hi


# ===========================================================================
# [C2] [v7 judgment §6 (2)] hip roof custom mesh — topology + normals (module level)
# ---------------------------------------------------------------------------
# Symptom: the `park_vista` roof faces are RGB (176,179,186) while the finial cylinder,
#   which uses the **same material** (`M["pav_roof"]`, albedo 0.155/0.165/0.185 = the dark
#   grey of Korean roof tile), is (107,116,128). 1.6x under the same light and material → a white tent, not tile.
# Cause: **normals never authored** on the `UsdGeom.Mesh`. Without them Hydra estimates
#   averaged (smoothed) normals from adjacent faces, and on this roof the 8 slope faces at 21.8 deg
#   share the eave ring T[0..7] with the 8 **vertical** eave-band faces. The average normal of the two
#   groups lifts the whole eave region skyward, so the angular tiled roof shades as an
#   **inflated tent / parasol** (= exactly the judgment's wording). `sc.add_cylinder`/`add_box`
#   are built-in prims whose normals are fixed by schema, so they are immune → this is mesh-path only.
# Fix: author the face normals explicitly as **faceVarying** (forcing flat shading) +
#   state orientation/doubleSided. Winding and normal direction are checked numerically without
#   a render (`roof_normal_selfcheck`) — so that assembler and checker use the same coordinates,
#   topology generation is split out to module level (scene04 `verge_instances` convention).
#
# ---------------------------------------------------------------------------
# [v8 judgment §4 (1) — Y1] **the v7 diagnosis above was wrong.** Treat the following as authoritative.
#   · v7↔v8 roof pixel diff **0.0 %**. Authoring normals did not change the render by a single bit
#     = the renderer was **already using the same face normals before authoring** (RTX uses
#     face normals on subdivisionScheme="none" meshes). Indeed, in the v8 PNG the
#     ridges stand angular and the −X shaded face separates from the +Y face in its own tone step.
#   · So the normal authoring and check in this block are **harmless but ineffective**. They are kept
#     as defensive code that pins the behaviour instead of relying on renderer defaults.
#   · The real cause is the material's **specular additive term** — see the module docstring
#     [v8 judgment rework — Y1] (a)~(d). Below, in `roof_normal_selfcheck`,
#     item (4) is updated with the v8 measurements and records that separation numerically.
# ===========================================================================
def hip_roof_topology(cx, cy, sx, sy, z_bot, band, rise, lift):
    """(points, faceVertexCounts, faceVertexIndices, z_top, z_apex) of the hip
    roof mesh. See the build_hip_roof docstring for the coordinate definitions."""
    hx, hy = sx / 2.0, sy / 2.0
    ring = [(cx + hx, cy + hy, lift), (cx, cy + hy, 0.0),
            (cx - hx, cy + hy, lift), (cx - hx, cy, 0.0),
            (cx - hx, cy - hy, lift), (cx, cy - hy, 0.0),
            (cx + hx, cy - hy, lift), (cx + hx, cy, 0.0)]
    z_top = z_bot + band
    z_apex = z_top + rise
    pts = [(px, py, z_bot) for px, py, _ in ring]            # B 0..7
    pts += [(px, py, z_top + dz) for px, py, dz in ring]     # T 8..15
    pts.append((cx, cy, z_apex))                             # A 16
    counts, idx = [], []
    for i in range(8):                       # 8 roof triangles
        counts.append(3)
        idx += [8 + i, 8 + (i + 1) % 8, 16]
    for i in range(8):                       # 8 eave band quads
        counts.append(4)
        idx += [i, (i + 1) % 8, 8 + (i + 1) % 8, 8 + i]
    counts.append(8)                         # bottom face
    idx += [7, 6, 5, 4, 3, 2, 1, 0]
    return pts, counts, idx, z_top, z_apex


def _newell(poly):
    """Unit normal of a polygon (Newell's method) — stable for convex, concave and non-planar alike.
    Same sign convention as the USD default orientation=rightHanded."""
    nx = ny = nz = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0, z0 = poly[i]
        x1, y1, z1 = poly[(i + 1) % n]
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return (nx / L, ny / L, nz / L)


def hip_roof_face_normals(pts, counts, idx):
    """List of unit face normals, in face order."""
    out, o = [], 0
    for c in counts:
        out.append(_newell([pts[i] for i in idx[o:o + c]]))
        o += c
    return out


def _sun_dir():
    """DistantLight travel direction d (world) — back-computed from the op order of
    setup_lighting (default −Z → rotateX(90−elev) → rotateZ(rz)). The direct Lambert
    term a face receives is max(0, −d·n)."""
    lp = PARAMS["light"]
    rz = math.radians(lp["noon_dome_rot"] + PARAMS["SUN_AZ_OFFSET"]
                      + lp["hdri_sun_rotz_offset"])
    rx = math.radians(90.0 - lp["noon_sun_elev"])
    return (-math.sin(rx) * math.sin(rz),
            math.sin(rx) * math.cos(rz),
            -math.cos(rx))


def roof_normal_selfcheck(verbose=True):
    """[v7 §6 (2)] roof mesh normal check — verifies direction and Lambert numerically **without a render**.

    (1) roof faces 8: is the normal z>0 with its horizontal component pointing away from the axis (outward)?
    (2) eave bands 8: is the normal horizontal (|nz|<1e-6) and outward?
    (3) bottom face 1: is the normal (0,0,−1)?
    (4) vs the finial (cylinder): the quantitative basis for why one material looked different —
       the ratio of mean roof-face Lambert to max cylinder-side Lambert. A brightness
       difference beyond this ratio is a material/normal problem, not a geometry problem.
    Returns (ok, diag)."""
    p = PARAMS["pavilion"]
    cx = (p["x0"] + p["x1"]) / 2.0
    cy = (p["y0"] + p["y1"]) / 2.0
    sx, sy = p["x1"] - p["x0"], p["y1"] - p["y0"]
    z_ev = (p["base_t"] + p["floor_t"] + p["post_h"] + p["beam_t"]
            + p["eave_t"])
    fx = sx + 2 * p["eave_over"] - 2 * p["fascia_inset"]
    fy = sy + 2 * p["eave_over"] - 2 * p["fascia_inset"]
    pts, counts, idx, _z_top, z_apex = hip_roof_topology(
        cx, cy, fx, fy, z_ev, p["fascia_t"], p["roof_rise"], p["corner_lift"])
    nrm = hip_roof_face_normals(pts, counts, idx)
    d = _sun_dir()
    # per-face centroid → outward test
    cents, o = [], 0
    for c in counts:
        poly = [pts[i] for i in idx[o:o + c]]
        o += c
        cents.append((sum(q[0] for q in poly) / c,
                      sum(q[1] for q in poly) / c))
    bad = []
    for f, n in enumerate(nrm):
        gx, gy = cents[f][0] - cx, cents[f][1] - cy
        out = n[0] * gx + n[1] * gy
        if f < 8:                                   # roof face
            if not (n[2] > 0.0 and out > 0.0):
                bad.append(("roof", f, n))
        elif f < 16:                                # eave band
            if not (abs(n[2]) < 1e-6 and out > 0.0):
                bad.append(("band", f, n))
        else:                                       # bottom face
            if n[2] > -0.999999:
                bad.append(("bottom", f, n))
    lam_roof = [max(0.0, -(d[0] * n[0] + d[1] * n[1] + d[2] * n[2]))
                for n in nrm[:8]]
    lam_r = sum(lam_roof) / 8.0
    lam_cyl_side = math.hypot(d[0], d[1])           # max Lambert on a cylinder side
    slope = math.degrees(math.atan2(p["roof_rise"], fx / 2.0))
    ok = not bad
    if verbose:
        print("=" * 68)
        print("scene09 [v7] 모임지붕 메시 법선 검산 (렌더 없음)")
        print("=" * 68)
        print(f"  면 구성            지붕 8삼각 + 처마밴드 8쿼드 + 밑면 1 "
              f"= {len(counts)}면 / 정점 {len(pts)}")
        print(f"  지붕 경사          {slope:.1f}° (rise {p['roof_rise']:.2f} / "
              f"반폭 {fx/2.0:.2f}) · 용마루 z {z_apex:.2f}")
        print(f"  ① 지붕면 법선      nz>0 & 외향 → "
              f"{'OK' if not any(b[0]=='roof' for b in bad) else 'FAIL'}"
              f"   (예: {nrm[0][0]:+.3f},{nrm[0][1]:+.3f},{nrm[0][2]:+.3f})")
        print(f"  ② 처마밴드 법선    수평 & 외향 → "
              f"{'OK' if not any(b[0]=='band' for b in bad) else 'FAIL'}"
              f"   (예: {nrm[8][0]:+.3f},{nrm[8][1]:+.3f},{nrm[8][2]:+.3f})")
        print(f"  ③ 밑면 법선        (0,0,−1) → "
              f"{'OK' if not any(b[0]=='bottom' for b in bad) else 'FAIL'}"
              f"   ({nrm[16][0]:+.3f},{nrm[16][1]:+.3f},{nrm[16][2]:+.3f})")
        print(f"  ④ 램버트(직달)     지붕면 평균 {lam_r:.3f} · "
              f"절병통 측면 최대 {lam_cyl_side:.3f} → 기하상 상한비 "
              f"{lam_r / max(lam_cyl_side, 1e-6):.2f}배")
        print(f"     ※ [v8 정정] v7 은 여기서 '초과분 = 스무딩 법선'으로 "
              f"결론냈으나 **오진**이었다.")
        print(f"       v7↔v8 지붕 픽셀 diff 0.0 % = 법선은 저작 전부터 이미 "
              f"면법선이었다. 실체는 ⑤.")
        if bad:
            for kind, f, n in bad:
                print(f"     [FAIL] {kind} face{f} n={n}")
        roof_specular_selfcheck(nrm, cx, cy, verbose=True)
        print("=" * 68)
    return ok, dict(n_faces=len(counts), lam_roof=lam_r,
                    lam_cyl=lam_cyl_side, bad=bad)


# ---------------------------------------------------------------------------
# [C2-b] [v8 judgment §4 (1) — Y1] roof specular diagnosis (no render)
#   The v8_rt/rt_noon_park_vista.png measurements are hard-coded as constants and compared
#   against a "diffuse only" model to reproduce **without booting** whether an excess remains.
#   The point is that whoever opens this next round sees the same numbers (lesson: 2 rounds burnt on the same 1 line).
# ---------------------------------------------------------------------------
# park_vista measurements (v7 and v8 identical): +Y roof faces (180,183,190) · −X roof faces (130,134,144)
#                              paving (horizontal, albedo 0.300) 193.5
_V8_MEAS = dict(roof_pY=(180.2, 183.1, 189.9), roof_mX=(130.0, 134.0, 144.0),
                pav=193.5, pav_albedo=0.300)


def _lin(s):
    """sRGB(0..255) → linear."""
    u = max(0.0, min(1.0, s / 255.0))
    return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4


def roof_specular_selfcheck(nrm, cx, cy, verbose=True):
    """Separates numerically the fact that the near-white roof is **a specular additive term, not albedo**.

    (1) The roof faces visible in park_vista are only the +Y group (face0,1) and the −X group (face2,3).
    (2) Solving `resp = S·lam + K` from those two alone gives K<0 (a negative ambient) = impossible
       ⇒ a **view-dependent term** that Lambert cannot explain exists.
    (3) Re-solving with the out-of-lobe face (−X) and the horizontal paving as diffuse anchors gives
       positive S/K, and the predicted diffuse response on the +Y faces matches `_ALBEDO_GAIN`.
       measurement − prediction = the same **additive** value in all 3 channels → specular.
    (4) The GGX half vector N·H confirms that only the +Y group is inside the lobe.
    Returns (ok, diag). ok = "was a specular term detected and is specular_level 0.0".
    """
    v = PARAMS["views_park_vista"]
    d = _sun_dir()
    lam = [max(0.0, -(d[0] * n[0] + d[1] * n[1] + d[2] * n[2])) for n in nrm]
    lam_pY = (lam[0] + lam[1]) / 2.0
    lam_mX = (lam[2] + lam[3]) / 2.0
    lam_h = -d[2]
    alb = PARAMS["material"]["roof_tile_color"]
    m = _V8_MEAS
    # (2) fit on the 2 roof faces alone → K<0 means a view-dependent term exists
    r_pY = _lin(m["roof_pY"][0]) / 0.155      # albedo R at the time of v8 = 0.155
    r_mX = _lin(m["roof_mX"][0]) / 0.155
    S_bad = (r_pY - r_mX) / (lam_pY - lam_mX)
    K_bad = r_pY - S_bad * lam_pY
    # (3) out-of-lobe face + horizontal paving = diffuse anchors
    r_pav = _lin(m["pav"]) / m["pav_albedo"]
    S = (r_pav - r_mX) / (lam_h - lam_mX)
    K = r_pav - S * lam_h
    resp_pY = S * lam_pY + K
    excess = [_lin(c) - a * resp_pY for c, a in zip(m["roof_pY"],
                                                    (0.155, 0.165, 0.185))]
    # (4) half vector
    eye = v["eye"]
    px, py, pz = cx, cy, v["roof_z"]
    vv = [eye[0] - px, eye[1] - py, eye[2] - pz]
    lv = [-d[0], -d[1], -d[2]]
    nh = []
    for arr in (vv, lv):
        L = math.sqrt(sum(q * q for q in arr)) or 1.0
        arr[:] = [q / L for q in arr]
    h = [vv[i] + lv[i] for i in range(3)]
    L = math.sqrt(sum(q * q for q in h)) or 1.0
    h = [q / L for q in h]
    for f in range(4):
        nh.append(sum(nrm[f][i] * h[i] for i in range(3)))
    spec_off = PARAMS["material"].get("roof_tile_specular", 0.0) == 0.0
    ok = (K_bad < 0.0) and spec_off
    if verbose:
        print(f"  ⑤ [v8] 정반사 분리   park_vista 가시면 = +Y군(lam "
              f"{lam_pY:.3f}) · −X군(lam {lam_mX:.3f})")
        print(f"     ⓑ 확산만 적합      S {S_bad:+.3f} / K {K_bad:+.3f} → "
              f"K<0 = 음의 앰비언트 ⇒ **시선의존 항 존재** "
              f"{'OK' if K_bad < 0 else 'FAIL'}")
        print(f"     ⓒ 로브 밖 재적합   S {S:+.3f} / K {K:+.3f} → +Y면 확산 "
              f"응답 {resp_pY:.3f} (GAIN {_ALBEDO_GAIN})")
        print(f"        실측−확산예측   {excess[0]:+.4f} / {excess[1]:+.4f} / "
              f"{excess[2]:+.4f} (선형) = 3채널 동일 **가산 반사항**")
        print(f"     ⓓ 하프벡터 N·H     +Y {nh[0]:+.3f},{nh[1]:+.3f} vs "
              f"−X {nh[2]:+.3f},{nh[3]:+.3f} → +Y군만 GGX 로브 안"
              f"(rough {PARAMS['material']['roof_tile_rough']})")
        print(f"     ⑥ 조치 반영        specular_level 0.0 "
              f"{'OK' if spec_off else 'FAIL'} · roof_tile_color "
              f"{alb[0]:.3f}/{alb[1]:.3f}/{alb[2]:.3f}")
        for tag, lm in (("+Y 지붕면", lam_pY), ("−X 지붕면", lam_mX),
                        ("+Y 처마밴드", lam[8]), ("−X 처마밴드", lam[10])):
            pr = [_srgb(a * (S * lm + K)) * 255.0 for a in alb]
            print(f"        예측 sRGB {tag:11s} "
                  f"({pr[0]:5.1f},{pr[1]:5.1f},{pr[2]:5.1f})")
    return ok, dict(S_bad=S_bad, K_bad=K_bad, S=S, K=K,
                    resp_pY=resp_pY, excess=excess, nh=nh)


# ===========================================================================
# [C3] [v7 judgment §11-6] §4 "no large near-white (>0.8) areas" albedo cap self-check
# ---------------------------------------------------------------------------
# It happened this round on 09 paving, 18 plaza and 19 roof at once → the judge recommended
# "instead of pointing at them one by one, add a global albedo-cap check script to the smoke run".
# **Without a render**, both criteria are checked from the material definitions alone (shared convention of 05/09/12):
#   (A) albedo cap  : effective albedo max channel > CAP(0.80) → violates the letter of v5.1 §4.
#   (B) render prediction : for **large horizontal areas** only (paving, deck, roof top face, lawn),
#       expected render sRGB = sRGB(albedo x GAIN) > PRED_CAP(0.87 ~ 222).
#       GAIN 1.77 = back-computed from the v7_rt measurement: this scene's `ghat_walk` paving albedo
#       0.469×0.90 = 0.422 → render (223,222,221) = linear 0.738.
#       (a shared value for 05/09/12, which use the same rig: dome 1000 + sun 2450 · elev 49.79)
#       Vertical faces have different insolation and sky visibility, so (B) does not apply to them.
#   Effective albedo = the constant colour as is | diff texture linear mean x tint.
#   ※ (A) alone would miss this round's 09 paving (albedo 0.422) and (B) alone would miss vertical
#      near-white panels (the 19 parapet family) — both criteria have to be present.
# ===========================================================================
_ALBEDO_GAIN = 1.77          # noon direct front-lit horizontal face, back-computed from the v7_rt measurement
_ALBEDO_CAP = 0.80           # v5.1 §4 "no large near-white (>0.8) areas"
_ALBEDO_PRED_CAP = 0.87      # just under the measurement (223/220) the judge flagged as "large near-white area"
_TEXMEAN_CACHE = {}


def _tex_lin_mean(role):
    """Linear (sRGB-decoded) channel mean of the diff texture. None if PIL or the file is missing."""
    if role in _TEXMEAN_CACHE:
        return _TEXMEAN_CACHE[role]
    val = None
    try:
        from PIL import Image
        im = Image.open(sc.tex_path(role, "diff")).convert("RGB")
        im.thumbnail((192, 192))
        a = np.asarray(im, dtype=np.float64) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        val = tuple(float(v) for v in lin.mean(axis=(0, 1)))
    except Exception:
        val = None
    _TEXMEAN_CACHE[role] = val
    return val


def _srgb(u):
    u = max(0.0, min(1.0, u))
    return 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055


# (label, texture role|None, material key, large area, horizontal)
_ALBEDO_TABLE = [
    ("계단·테라스·제방 석재", "plaza_light", "stone_tint",      True,  True),
    ("물때(수위선) 밴드",     "plaza_light", "stain_tint",      True,  True),
    ("상부 잔디 밴드",        "grass",       "grass_tint",      True,  True),
    ("산책 데크(목)",         "wood_dark",   "deck_tint",       True,  True),
    ("정자 기와지붕",         None,          "roof_tile_color", True,  True),
    ("정자 누마루(목)",       "wood_dark",   "pav_floor_tint",  False, True),
    ("오리배 선체",           None,          "duck_color",      False, False),
    ("원경 건물 실루엣",      None,          "far_color",       True,  False),
]


def albedo_selfcheck(verbose=True):
    """[v7 §4/§11-6] large-near-white-area self-check. A violation is (A) albedo > 0.80 or
    (B) an expected render sRGB > 0.87 on a large horizontal area. Large area FAIL /
    small area WARN. Returns (ok, rows)."""
    mp = PARAMS["material"]
    rows, fails, warns = [], [], []
    for label, role, key, wide, horiz in _ALBEDO_TABLE:
        v = mp.get(key)
        if v is None:
            continue
        base = (1.0, 1.0, 1.0) if role is None else _tex_lin_mean(role)
        if base is None:
            rows.append((label, key, None, None, "SKIP(텍스처 없음)"))
            continue
        alb = max(b * t for b, t in zip(base, v))
        pred = _srgb(alb * _ALBEDO_GAIN) if horiz else None
        why = []
        if alb > _ALBEDO_CAP:
            why.append("A:알베도")
        if pred is not None and pred > _ALBEDO_PRED_CAP:
            why.append("B:렌더예측")
        if why:
            mark = "/".join(why)
            (fails if wide else warns).append(label)
            tag = (f"FAIL 대면적({mark})" if wide
                   else f"WARN 소면적({mark})")
        else:
            tag = "OK"
        rows.append((label, key, alb, pred, tag))
    ok = not fails
    if verbose:
        print("=" * 68)
        print("scene09 [v7 §4] 순백 대면적 알베도 상한 자가검사 "
              f"(CAP {_ALBEDO_CAP} · 수평 렌더예측 CAP {_ALBEDO_PRED_CAP} "
              f"· GAIN {_ALBEDO_GAIN})")
        print("=" * 68)
        for label, key, alb, pred, tag in rows:
            if alb is None:
                print(f"  {label:22s} {key:18s} {tag}")
                continue
            pr = f"{pred*255:5.1f}" if pred is not None else "  수직"
            print(f"  {label:22s} {key:18s} 알베도 {alb:.3f} · "
                  f"수평 예상 렌더 {pr}  {tag}")
        print(f"  ⇒ {'OK — 대면적 위반 0건' if ok else 'FAIL: ' + str(fails)}"
              f"{'  (WARN: ' + str(warns) + ')' if warns else ''}")
        print("=" * 68)
    return ok, rows


# ===========================================================================
# [C-2] ground_kit plan - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def ground_plan():
    """P2 `plaza_water` plan for the upper granite terrace (z = 0).

    Drop edge = terrace x1 = stairs x0, i.e. the head of the 36-step flight.
    """
    g = PARAMS["gkit"]
    tr, st = PARAMS["terrace"], PARAMS["stairs"]
    return gk.plan_ground(
        "plaza_water",
        region=tuple(float(v) for v in g["region"]),
        z=float(tr["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("stair_head", float(st["x0"]))],
        dists=(2, 5, 10), scene="scene09",
        tactile=(),                # Sec.12.4 OFF - p = 0.24 and natural scene
        sites=dict(patch=[tuple(v) for v in g["patches"]]),
        overrides=dict(
            pave=dict(step_x=float(g["joint_step"]),
                      step_y=float(g["joint_step"])),
            surface=(("patch", int(g["patch_n"])), ("crack", 4),
                     ("stain", ("water",))),
            extras=()),
        seed=int(g["seed"]))


# ===========================================================================
# [D] camera presets
# ===========================================================================
def build_views(run, z_bot, water_z, water_x0):
    views = sc.grid_views(0.0)
    # ghat_walk: from the upper terrace toward the river — checks the boundary where the water cuts the stairs in half
    views["ghat_walk"] = dict(eye=[-4.0, 0.0, 1.4], tgt=[8.0, 0.0, water_z + 0.8])
    # waterline: eye height close to the horizontal water boundary (the signature point)
    views["waterline"] = dict(eye=[water_x0 - 3.0, 4.0, water_z + 1.2],
                              tgt=[water_x0 + 2.0, 0.0, water_z])
    # from_river: looking up at the stairs head-on from close in on the river (ultra-wide, landings, waterline)
    views["from_river"] = dict(eye=[water_x0 + 12.0, 0.0, water_z + 1.6],
                               tgt=[2.0, 0.0, -1.0])
    # across_river: director r1 — re-aimed from mid-river above the water (h1.5) to frame the ghat head-on
    #   (it used to look only at far_bank, leaving the ghat out of frame). Includes the river-width reflection + the water boundary.
    river_mid = (water_x0 + PARAMS["water"]["x_far"]) / 2.0
    views["across_river"] = dict(eye=[river_mid, 0.0, water_z + 1.5],
                                 tgt=[2.0, 0.0, -1.0])
    # [v6 rework (4)] park_vista — the **reinterpretation mise-en-scene cut** the judgment asked for.
    #   "pavilion + deck + water + stair head in one frame" (judgment revision 1).
    #   The judgment's example eye(4,16,2)→tgt(−7,5,−0.5) back-computes to **water out of frame**
    #   (the waterline x 11.92 bears +80.8 deg), so it was not adopted; instead the axis was redesigned to look
    #   south-east and downward from the lawn band west of the boardwalk (x −10.2, y 22).
    #   FOV +-30 deg (horizontal) · +-18 deg (vertical), sight-line bearing −57.2 deg / pitch −12.1 deg
    #   → frame bearing [−87.2, −27.2] · elevation [−30.1, +5.9]
    #   Back-computation (element = bearing offset / distance / elevation):
    #     waterfront pavilion (−4.2, 8.8)  −8.4 deg  14.50 m  finial tip +3.6 deg (eaves +-11.9 deg)
    #     boardwalk (x −8.8 axis)  −24.9 deg~−28.8 deg  10~20 m     → left-hand leading line
    #     lawn bands N/S           green faces left and right of frame  → the evidence for "park"
    #     stair-head corner (0, 5) −1.9 deg  19.83 m  −10.9 deg      → centre of frame
    #     waterline (11.92, 0)     +12.3 deg 31.20 m  −16.1 deg      → water boundary
    #     duck boat (15.4, 3.0)    +20.6 deg 31.88 m  −13.1 deg      → right side
    #     sign_info (−7.0, −5.6)   −26.2 deg 27.78 m               → bottom left
    #     far-bank horizon                          −7.0 deg        → top of frame
    #   Zero near (<6 m) intrusion : the nearest street tree (−13.4, 17.2) is 5.77 m away but its bearing offset
    #   of −66.5 deg puts it outside the FOV. Bench 0 (−4.6, 12.6) is −2.1 deg / 10.94 m mid-ground (height
    #   0.45 → elevation −17.0 deg), so it does not hide the pavilion (finial +3.6 deg).
    #   [intent] the pavilion's bearing span (−22.6 deg~+8.9 deg) contains the stair-head corner (−1.9 deg).
    #   That is not occlusion but **a composition that looks at the stairs and water through the open pavilion** — sight-line check:
    #   the ray toward (0,5) passes z 1.53 at y 11.85 and z 0.17 at y 5.75, threading the **empty gap**
    #   between the railing top (floor+0.44 → z 0.89) and the underside of the tie beam (z 2.75),
    #   and clears the 4 posts (x −6.27/−2.13, y 6.73/10.87) by at least 2.1 m. The stair-head
    #   corner (elevation −10.9 deg) is **above** the pavilion floor edge (−11.4 deg), so it stays in frame.
    #   [v8 Y1] the coordinates come from the single source PARAMS["views_park_vista"] (shared with the checker).
    _pv = PARAMS["views_park_vista"]
    views["park_vista"] = dict(eye=list(_pv["eye"]), tgt=list(_pv["tgt"]))
    return views


# ===========================================================================
# [E] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. ghat_walk    — 수면이 계단 중간을 수평으로 자르는 경계가 낙차 앵커인가
                  (뷰 키는 판정 파일명 연속성 때문에 v4 이름 유지)
 2. waterline    — 물때 밴드(수면 위 1.5단) + 이끼(수면 아래 2단) 수위 이력
 3. from_river   — 초광폭 36단 + 중간 참 2개가 정면에서 읽히나
 4. h0.3·d5~10   — 상부 테라스가 평지로 보이고 낙차 증거가 수면뿐인가
 5. across_river — 대안 둔치(+1.6)+숲+건물 실루엣이 지평을 막는가
 6. cue_railing OFF/ON — 위험 기하(계단) 트랜스폼 동일한가
 7. 이음새       — y=±5 경계에 톱니 홈/턱이 없는가 (제방 계단식 정합)
 8. [v5] 맥락    — 정자·데크 말뚝·오리배·산책 데크·갈대·안내판이
                   '호수공원'으로 읽히나 (종교색 잔존 0)
 9. [v6] park_vista — 목조 사모정(4면 경사 지붕·귀솟음)·데크 널결·잔디 밴드·
                   황색 오리배가 **한 프레임**에서 동시에 판독되나
10. [v8] 지붕 셰이딩 — park_vista 에서 +Y 지붕면이 (125,129,136) 대역
                   (구 180,183,190 = 흰 천막)으로 내려오고 −X 그늘면
                   (110,114,120)·처마밴드(103/81)와 **밝기 순서**가 서는가.
                   원인은 법선이 아니라 `specular_level` 미지정이었다
11. [v7] 석재 톤   — ghat_walk 포장이 순백(223)에서 회색 화강암(≈192)으로
                   내려오고, from_river 36단의 **단 분절**이 되살아났는가.
                   물때(수위선)·이끼 밴드 대비는 그대로인가(대비비 보존)"""


def main():
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # [v7] pure-Python self-checks that run without booting (roof normals · §4 albedo cap).
    #   NEGOBS_SELFCHECK=1 python scene09_ghat_riverfront.py
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        ok1, _ = roof_normal_selfcheck()
        ok2, _ = albedo_selfcheck()
        sys.exit(0 if (ok1 and ok2) else 1)

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode or smoke)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view
    from pxr import UsdGeom

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene09")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene09"

    steps, base_z, z_bot, water_z, band_hi = compute_steps()
    run = steps[-1][1]
    # water submergence line x : the start xa of the 6th step from the bottom (roughly the waterline)
    water_x0 = steps[PARAMS["stairs"]["nsteps"]
                     - PARAMS["stairs"]["submerge_from_bottom"]][0]

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        # [v6 rework (3)] stone = plaza_light (light granite). The old sandstone is retired.
        M["stone"] = tex("plaza_light", "/World/Looks/Stone", sca["stone"],
                         tint=mp["stone_tint"])
        # water mark (waterline) — same texture with a darker tint (geometry unchanged, material only branches)
        M["stain"] = tex("plaza_light", "/World/Looks/StoneStain",
                         sca["stone"], tint=mp["stain_tint"])
        # [v5 adopted] moss — the 2 steps just below the water. Geometry unchanged, material only branches.
        M["moss"] = tex("plaza_light", "/World/Looks/StoneMoss",
                        sca["stone"], tint=mp["moss_tint"])
        M["deck"] = tex("wood_dark", "/World/Looks/Deck", sca["wood_dark"],
                        tint=mp["deck_tint"])
        M["seam"] = sc.make_pbr(stage, "/World/Looks/Seam",
                                diffuse_color=mp["seam_color"],
                                roughness_const=0.9)
        # [v6 (1)] 2 pavilion timber materials + 1 roof tile
        M["pav_wood"] = tex("wood_dark", "/World/Looks/PavWood",
                            sca["wood_fine"], tint=mp["pav_wood_tint"])
        M["pav_floor"] = tex("wood_dark", "/World/Looks/PavFloor",
                             sca["wood_fine"], tint=mp["pav_floor_tint"])
        # [v8 Y1] specular_level=0.0 — the **cause** of the near-white roof. Left unset,
        #   OmniPBR defaults to 0.5 (F0 0.04) and the wide GGX lobe at roughness 0.72
        #   caught the sun plus sky on the +Y roof faces (N·H 0.78) along the park_vista sight line,
        #   adding a linear +0.164 on top of the diffuse. Every other matte material in this scene
        #   (reed/far/canopy_a/canopy_b) is 0.0 — only pav_roof was missing it.
        M["pav_roof"] = sc.make_pbr(stage, "/World/Looks/PavRoof",
                                    diffuse_color=mp["roof_tile_color"],
                                    roughness_const=mp["roof_tile_rough"],
                                    specular_level=mp["roof_tile_specular"])
        M["duck"] = sc.make_pbr(stage, "/World/Looks/Duck",
                                diffuse_color=mp["duck_color"],
                                roughness_const=mp["duck_rough"])
        M["duck_top"] = sc.make_pbr(stage, "/World/Looks/DuckTop",
                                    diffuse_color=mp["duck_top_color"],
                                    roughness_const=mp["duck_top_rough"])
        M["beak"] = sc.make_pbr(stage, "/World/Looks/Beak",
                                diffuse_color=mp["beak_color"],
                                roughness_const=mp["beak_rough"])
        M["reed"] = sc.make_pbr(stage, "/World/Looks/Reed",
                                diffuse_color=mp["reed_color"],
                                roughness_const=mp["reed_rough"],
                                specular_level=0.0)
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["water"] = sc.make_pbr(stage, "/World/Looks/Water",
                                 diffuse_color=mp["water_color"],
                                 roughness_const=mp["water_rough"],
                                 metallic=0.0)
        M["post"] = sc.make_pbr(stage, "/World/Looks/Post",
                                diffuse_color=mp["post_color"],
                                roughness_const=mp["post_rough"])
        M["far"] = sc.make_pbr(stage, "/World/Looks/Far",
                               diffuse_color=mp["far_color"],
                               roughness_const=0.95, specular_level=0.0)
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
        return M

    # -------------------------------------------------------------------
    # ultra-wide stairs — add_box per step; the water-mark band only branches the material (geometry unchanged)
    # -------------------------------------------------------------------
    st_p = PARAMS["stairs"]
    # [v5 adopted] moss steps = the 2 steps just below the water (= the first submerged step and the next one).
    _MOSS_IDX = (st_p["nsteps"] - st_p["submerge_from_bottom"],
                 st_p["nsteps"] - st_p["submerge_from_bottom"] + 1)

    def _step_mtl(M, tz, default, idx=None):
        """Water-mark material in the 1.5-step band above the water (the waterline), moss
        material on the 2 steps below the water.
        **Geometry unchanged — only the material branches** (the mtl argument of the per-step add_box)."""
        if idx is not None and idx in _MOSS_IDX:
            return M["moss"]
        return M["stain"] if (water_z - 0.01) < tz <= band_hi else default

    def build_stairs(M):
        st = PARAMS["stairs"]
        cy = (st["y0"] + st["y1"]) / 2.0
        Ly = st["y1"] - st["y0"]
        default = M["stone"] if cfg["cue_material_break"] else M["stain"]
        n_stain = 0
        for i, (xa, xb, tz) in enumerate(steps):
            mtl = _step_mtl(M, tz, default, i)
            if mtl is M["stain"] and default is not M["stain"]:
                n_stain += 1
            cx = (xa + xb) / 2.0
            cz = (tz + base_z) / 2.0
            hz = tz - base_z
            sc.add_box(stage, f"{ROOT}/Step_{i}", (cx, cy, cz),
                       (xb - xa, Ly, hz), mtl, collider=True)
        print(f"[기하] 가트 {len(steps)}단 run={run:.3f} z_bot={z_bot:.3f} "
              f"water_z={water_z:.3f} 물때단={n_stain} 참={st['landing_steps']}")

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P2 plaza_water on the upper terrace.
    #   Materials are the scene's own granite tints: the joint / crack / film
    #   tone is exactly the darker `stain` variant already authored for the
    #   waterline band, so no new asset and no change to `_ALBEDO_TABLE`.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["stain"], crack=M["seam"], patch=M["stone"],
                  patch_cut=M["stain"], stain_water=M["moss"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                              skin_exclude=sc.skin_exclude)
        print(f"[ground_kit] scene09 P2 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_terrace(M):
        """Upper sandstone terrace (z=0)."""
        tr = PARAMS["terrace"]
        # [W2-0 P-A] The terrace is the slab ground_kit decorates. Its
        #   displacement skin tops out at +16.5 mm and would bury the 1.5 mm
        #   slab joints and 2 mm patches outright (spec Sec.1.1).
        sc.skin_exclude(f"{ROOT}/Terrace")
        sc.add_box(stage, f"{ROOT}/Terrace",
                   ((tr["x0"] + tr["x1"]) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
                    tr["z_top"] - tr["thick"] / 2.0),
                   (tr["x1"] - tr["x0"], tr["y1"] - tr["y0"], tr["thick"]),
                   M["stone"], collider=True)

    def build_embankment(M):
        """[A-09-1] Left/right embankments — a stepped extension on the **same step table** as the stairs.
        It reuses each step's (xa, xb, tz, base_z) as is, so the z difference at the y=±5 seam is
        structurally 0 (the old linear slope gave up to 0.315 m of sawtooth). The result is an 80 m wide
        ultra-wide ghat, which also reinforces the type identity (T12)."""
        st = PARAMS["stairs"]
        em = PARAMS["embankment"]
        default = M["stone"] if cfg["cue_material_break"] else M["stain"]
        for tag, y0, y1 in (("N", -em["y_edge"], st["y0"]),
                            ("P", st["y1"], em["y_edge"])):
            cyb = (y0 + y1) / 2.0
            Lyb = y1 - y0
            for i, (xa, xb, tz) in enumerate(steps):
                sc.add_box(stage, f"{ROOT}/Embank_{tag}_{i}",
                           ((xa + xb) / 2.0, cyb, (tz + base_z) / 2.0),
                           (xb - xa, Lyb, tz - base_z),
                           _step_mtl(M, tz, default, i), collider=True)

    def build_river(M):
        """Water (submerging the stairs) + far bank + distant tree line — horizon closure and water boundary."""
        wt = PARAMS["water"]
        sc.build_water(stage, f"{ROOT}/Water", water_x0, wt["y0"], wt["x_far"],
                       wt["y1"], water_z, mtl=M["water"])
        fb = PARAMS["far_bank"]
        fb_z = water_z + fb["above_water"]
        sc.add_box(stage, f"{ROOT}/FarBank",
                   ((fb["x0"] + fb["x1"]) / 2.0, (fb["y0"] + fb["y1"]) / 2.0,
                    fb_z - fb["thick"] / 2.0),
                   (fb["x1"] - fb["x0"], fb["y1"] - fb["y0"], fb["thick"]),
                   M["grass"], collider=True)
        fh = PARAMS["far_hedge"]
        for i, h in enumerate(PARAMS["far_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fh["cx"] - fh["sx"] / 2.0,
                           h["cy"] - fh["length"] / 2.0,
                           fh["cx"] + fh["sx"] / 2.0,
                           h["cy"] + fh["length"] / 2.0, fh["h"], base_z=fb_z)
        for i, t in enumerate(PARAMS["far_trees"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", t["cx"], t["cy"], fb_z,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        # Far-side building silhouettes 2 (distant layer) — completes the 3-tier depth of the horizon
        for i, b in enumerate(PARAMS["far_buildings"]):
            sc.add_box(stage, f"{ROOT}/FarBldg_{i}",
                       ((b["x0"] + b["x1"]) / 2.0, b["cy"],
                        fb_z + b["h"] / 2.0),
                       (b["x1"] - b["x0"], b["sy"], b["h"]), M["far"],
                       collider=True)

    def _step_top_at(x):
        """Stair (= embankment) top-face z at x. For grounding the reeds. Outside the range, the end value."""
        if x <= steps[0][0]:
            return PARAMS["stairs"]["z_top"]
        for xa, xb, tz in steps:
            if x < xb:
                return tz
        return steps[-1][2]

    def build_hip_roof(path, cx, cy, sx, sy, z_bot, band, rise, lift, mtl):
        """[v6 rework (1)] **Hip roof (samo roof) solid mesh** — 4-sided slope + corner lift.
        Returns : (mesh, z_apex).

        Why a mesh and not a box assembly:
          · stacking shrinking boxes → a 'wedding-cake tier' at a distance.
          · the **union** of 4 rotated `sc.build_slope` boxes takes the max of each face as its top,
            so the apex height survives along the ±X/±Y axes (a diagonal valley rather than
            a pyramid). In other words a 4-sided slope cannot be built from a union.
        → so an 8-sided eave ring + a pyramid with 1 apex is defined directly.

        3-ring construction (applying the scene14 wedge-slit lesson = "no joints without overlap"):
          B[0..7] bottom ring  a planar octagon at z_bot (underside of the buyeon layer)
          T[0..7] eave ring    corner = z_bot+band+lift · edge midpoint = z_bot+band
          A       apex         z_bot+band+rise
        Only the 4 corner points are raised by lift, making **the corner lift where the eave line rises at
        the corners** (approximating the hip-rafter curve), while the **8 vertical band quads** running
        down to the bottom ring fill the space beneath it solidly, so no triangular cavity opens under a
        lifted corner.

        Winding: the bottom ring is taken counter-clockwise seen from above, so
          · side triangles (T[i], T[i+1], A)      → normal outward and up
          · band quads     (B[i], B[i+1], T[i+1], T[i]) → normal outward
          · bottom octagon in reverse (7..0)      → normal downward
        subdivisionScheme='none' is fixed — with the default catmullClark the pyramid would be smeared
        into a round blob.

        [v7 judgment §6 (2) — top-priority bug] **fix for normals never authored.**
          Symptom: roof faces (176,179,186) vs the finial in the same material (107,116,128) = 1.6x.
          Cause: without normals, Hydra estimates averaged (smoothed) normals from adjacent faces.
            The 8 slope faces at 21.8 deg and the 8 **vertical** eave band faces share the eave ring
            T[0..7], so the averaged normal lifts the eave region skyward and the
            angular tiled roof shades as an **inflated white tent / parasol**.
          Fix: author the face normals explicitly as **faceVarying** (each face-vertex carrying that
            face's normal) → forcing flat shading. orientation and doubleSided are stated too, so
            winding interpretation does not depend on viewer/renderer defaults.
          Check: `roof_normal_selfcheck()` (module level, no render needed) — confirms from the
            coordinates that roof faces are nz>0 and outward, bands horizontal and outward, and the
            bottom face −Z. The topology comes from the single source
            `hip_roof_topology()`, shared by assembler and checker."""
        from pxr import UsdGeom, Gf, Vt
        hx, hy = sx / 2.0, sy / 2.0
        raw_pts, counts, idx, _z_top, z_apex = hip_roof_topology(
            cx, cy, sx, sy, z_bot, band, rise, lift)
        pts = [Gf.Vec3f(*p) for p in raw_pts]
        face_n = hip_roof_face_normals(raw_pts, counts, idx)
        # faceVarying = 1 normal per face-vertex. All the same value inside a face → flat shading.
        normals = []
        for f, c in enumerate(counts):
            normals += [Gf.Vec3f(*face_n[f])] * c
        mesh = UsdGeom.Mesh.Define(stage, path)
        mesh.CreatePointsAttr(pts)
        mesh.CreateFaceVertexCountsAttr(counts)
        mesh.CreateFaceVertexIndicesAttr(idx)
        mesh.CreateSubdivisionSchemeAttr("none")
        mesh.CreateNormalsAttr(Vt.Vec3fArray(normals))
        mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)
        mesh.CreateOrientationAttr(UsdGeom.Tokens.rightHanded)
        mesh.CreateDoubleSidedAttr(False)
        mesh.CreateExtentAttr([Gf.Vec3f(cx - hx, cy - hy, z_bot),
                               Gf.Vec3f(cx + hx, cy + hy, z_apex)])
        sc._bind_mtl(mesh.GetPrim(), mtl)
        return mesh, z_apex

    def build_pavilion(M):
        """[v6 rework (1)] Waterfront **timber samojeong** — a complete replacement of the old
        "flat-roofed achromatic concrete box" (v6 judgment). Layers (bottom→top):
          (1) stone plinth  base_t 0.22, overhang 0.46 — keeps ground damp out (customary)
          (2) timber floor  floor_t 0.23, overhang 0.30
          (3) 4 posts       r 0.13 · h 2.30, from the floor top face to the underside of the tie beam
          (4) tie beam      4 rectangular beams joining the post heads — the minimum signal of 'timber frame'
          (5) eave line 1   rafter layer (0.85 beyond the post line, 6.10 × 6.10)
          (6) eave line 2 + hip roof = one build_hip_roof mesh (5.74 × 5.74 band
             0.09 + 4-sided slope rise 1.15 + corner lift 0.16)
          (7) finial        apex cylinder
          (8) gyeja railing 3 sides N/E/S (west open for entry) — bottom rail + top rail + 3 balusters
        Height accumulation : 0.22 + 0.23 + 2.30 + 0.20 + 0.10 = 3.05 (underside of eave tier 2),
        ridge = 3.05 + 0.09 + 1.15 = 4.29, finial tip 4.71.
        It sits outside the stair width (y±5) at y 6.6..11.0, x1 = −1.54 including the plinth overhang,
        eave tip x −1.15 → **hazard geometry unchanged**."""
        p = PARAMS["pavilion"]
        cx = (p["x0"] + p["x1"]) / 2.0
        cy = (p["y0"] + p["y1"]) / 2.0
        sx, sy = p["x1"] - p["x0"], p["y1"] - p["y0"]
        P = f"{ROOT}/Pavilion"
        # (1) stone plinth
        bo = p["base_over"]
        sc.add_box(stage, f"{P}/Base", (cx, cy, p["base_t"] / 2.0),
                   (sx + 2 * bo, sy + 2 * bo, p["base_t"]), M["stone"],
                   collider=True)
        # (2) timber raised floor
        fo = p["floor_over"]
        z_fl = p["base_t"] + p["floor_t"]                 # floor top face 0.45
        sc.add_box(stage, f"{P}/Floor",
                   (cx, cy, p["base_t"] + p["floor_t"] / 2.0),
                   (sx + 2 * fo, sy + 2 * fo, p["floor_t"]), M["pav_floor"],
                   collider=True)
        # (3) 4 posts (inset from the corner by their radius = keeps the 4.4 bay)
        pr, ph = p["post_r"], p["post_h"]
        posts = ((p["x0"] + pr, p["y0"] + pr, "SW"),
                 (p["x0"] + pr, p["y1"] - pr, "NW"),
                 (p["x1"] - pr, p["y0"] + pr, "SE"),
                 (p["x1"] - pr, p["y1"] - pr, "NE"))
        for px, py, tag in posts:
            sc.add_cylinder(stage, f"{P}/Post_{tag}", (px, py, z_fl + ph / 2.0),
                            pr, ph, M["pav_wood"], collider=True)
        # (4) changbang — 4 rectangular head tie beams
        z_bm = z_fl + ph                                  # 2.75
        bt, bw = p["beam_t"], p["beam_w"]
        for tag, yy in (("N", p["y1"] - pr), ("S", p["y0"] + pr)):
            sc.add_box(stage, f"{P}/Beam_{tag}", (cx, yy, z_bm + bt / 2.0),
                       (sx, bw, bt), M["pav_wood"])
        for tag, xx in (("E", p["x1"] - pr), ("W", p["x0"] + pr)):
            sc.add_box(stage, f"{P}/Beam_{tag}", (xx, cy, z_bm + bt / 2.0),
                       (bw, sy, bt), M["pav_wood"])
        # (5) eave line, 2 tiers — rafter layer (timber) + buyeon/tiled eave layer (tile)
        z_ev = z_bm + bt                                  # 2.95
        eo = p["eave_over"]
        ex, ey = sx + 2 * eo, sy + 2 * eo                 # 6.10 × 6.10
        sc.add_box(stage, f"{P}/Eave", (cx, cy, z_ev + p["eave_t"] / 2.0),
                   (ex, ey, p["eave_t"]), M["pav_wood"])
        # (6) eave line tier 2 (buyeon band) + hip roof — a single mesh (the band fills under the corner lift)
        z_fa = z_ev + p["eave_t"]                         # 3.05
        fi = p["fascia_inset"]
        fx, fy = ex - 2 * fi, ey - 2 * fi                 # 5.74 × 5.74
        _, z_ap = build_hip_roof(f"{P}/Roof", cx, cy, fx, fy, z_fa,
                                 p["fascia_t"], p["roof_rise"],
                                 p["corner_lift"], M["pav_roof"])
        # (7) finial — ridge apex z_ap = 4.29
        sc.add_cylinder(stage, f"{P}/Finial",
                        (cx, cy, z_ap + p["finial_h"] / 2.0),
                        p["finial_r"], p["finial_h"], M["pav_roof"])
        # (8) gyeja railing — 3 sides N/E/S (west open for entry). Bottom rail + top rail + rail_n balusters
        rh, rt, rr = p["rail_h"], p["rail_t"], p["rail_post_r"]
        rails = (("N", cx, p["y1"] - pr, sx - 2 * pr, rt),
                 ("S", cx, p["y0"] + pr, sx - 2 * pr, rt),
                 ("E", p["x1"] - pr, cy, rt, sy - 2 * pr))
        for tag, rx, ry, lx, ly in rails:
            for lbl, zz, th in (("Low", z_fl + 0.06, 0.10),
                                ("Top", z_fl + rh, 0.08)):
                sc.add_box(stage, f"{P}/Rail{lbl}_{tag}", (rx, ry, zz),
                           (lx, ly, th), M["pav_wood"])
            span = max(lx, ly)
            for k in range(p["rail_n"]):
                t = (k + 1.0) / (p["rail_n"] + 1.0) - 0.5
                bx = rx + (span * t if lx > ly else 0.0)
                by = ry + (0.0 if lx > ly else span * t)
                sc.add_cylinder(stage, f"{P}/RailPost_{tag}{k}",
                                (bx, by, z_fl + rh / 2.0), rr, rh,
                                M["pav_wood"])

    def build_lawns(M):
        """[v6 rework (3)] 2 lawn bands on the upper terrace + 10 street trees.
        Answers the judgment "no lawn or tree band up top, so the evidence for 'park' is 0 in frame".
        All outside the stair width (y±5) (|y| >= 12) · proud of the terrace top face by lawn_proud (0.03)
        → **no effect on hazard geometry or grazing concealment** (outside the +-30 deg FOV of the grid
        presets: from eye x=−10 the nearest point of a band bears 86 deg or more)."""
        pr = PARAMS["lawn_proud"]
        for i, lw in enumerate(PARAMS["lawns"]):
            sc.add_box(stage, f"{ROOT}/Lawn_{i}",
                       ((lw["x0"] + lw["x1"]) / 2.0,
                        (lw["y0"] + lw["y1"]) / 2.0, pr / 2.0),
                       (lw["x1"] - lw["x0"], lw["y1"] - lw["y0"], pr),
                       M["grass"], collider=True)
        for i, (tx, ty) in enumerate(PARAMS["park_trees"]):
            sc.build_tree(stage, f"{ROOT}/ParkTree_{i}", tx, ty, pr,
                          M["wood"], M["canopy_a"], M["canopy_b"])

    def build_deck(M):
        """[v5 adopted] Timber boardwalk connection — the lake park waterfront promenade.
        [v6] x −9.2..−6.8 (6.8 m clear of the stair-head edge x=0 → no interference with the
        hazard geometry), top face 0.06 (6 cm above the terrace 0.0 — walk continuity). The plank seam
        spacing is tightened 2.0 → 0.62 m so it still reads as 'a deck with plank grain' at a distance."""
        d = PARAMS["deck"]
        cx = (d["x0"] + d["x1"]) / 2.0
        sc.add_box(stage, f"{ROOT}/Deck",
                   (cx, (d["y0"] + d["y1"]) / 2.0, d["top_z"] / 2.0),
                   (d["x1"] - d["x0"], d["y1"] - d["y0"], d["top_z"]),
                   M["deck"], collider=True)
        n = int(round((d["y1"] - d["y0"]) / d["seam_step"]))
        for k in range(1, n):
            y = d["y0"] + k * d["seam_step"]
            sc.add_box(stage, f"{ROOT}/DeckSeam_{k}",
                       (cx, y, d["top_z"] - d["seam_drop"] / 2.0),
                       (d["x1"] - d["x0"], d["seam_w"], d["seam_drop"]),
                       M["seam"])

    def build_reeds(M):
        """[v5 adopted] Reed stands — near the waterline (embankment, outside the stair width y±5) and on the far bank.
        Each stand is reproducible from a seeded RandomState. The stems (cylinders) get a small tilt angle."""
        rd = PARAMS["reed"]
        fb = PARAMS["far_bank"]
        fb_z = water_z + fb["above_water"]
        for ci, (cx, cy, n, seed) in enumerate(PARAMS["reeds"]):
            rs = np.random.RandomState(int(seed))
            gz = fb_z if cx >= fb["x0"] else _step_top_at(cx)
            for k in range(int(n)):
                dx = float(rs.uniform(-rd["spread"], rd["spread"]))
                dy = float(rs.uniform(-rd["spread"], rd["spread"]))
                hh = float(rs.uniform(rd["h_lo"], rd["h_hi"]))
                a = float(rs.uniform(0.0, 360.0))
                t = rd["tilt"]
                sc.add_cylinder(
                    stage, f"{ROOT}/Reed_{ci}_{k}",
                    (cx + dx, cy + dy, gz + hh / 2.0), rd["r"], hh, M["reed"],
                    rotY=t * math.cos(math.radians(a)),
                    rotX=t * math.sin(math.radians(a)))

    def build_signs():
        """[v5 shared layer] Korean sign (sc.build_sign). The coordinate checks are in the PARAMS comments."""
        back = sc.make_pbr(stage, "/World/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_dressing(M):
        """[v5 adopted / v6 rework] Lake park dressing — 8 waterfront boundary piles +
        **1 timber samojeong** + 4 landing stone posts + 4 benches + **1 duck boat (curved)** +
        boardwalk + **2 lawn bands + 10 street trees** + 10 reed stands.
        [v6 §6 emptying] the 2 planters are deleted — the street trees on the lawn bands take over that role.
        All outside the stair width (y±5) or on the terrace → hazard geometry unchanged."""
        r = PARAMS["mooring_r"]
        h = PARAMS["mooring_h"]
        # [v5] mooring bollard → boundary pile (scaled down): marks the stair-head waterfront boundary
        #   [v6] now that the deck has moved to x −10.0..−7.6, this pile row (x −1.2) means
        #   only "stair-head boundary" (the prim names are kept for continuity with the judgment files).
        for i, m in enumerate(PARAMS["mooring"]):
            sc.add_cylinder(stage, f"{ROOT}/DeckPile_{i}",
                            (m["cx"], m["cy"], h / 2.0), r, h, M["post"],
                            collider=True)
            sc.add_cylinder(stage, f"{ROOT}/DeckPileCap_{i}",
                            (m["cx"], m["cy"], h + 0.04 / 2.0), r * 1.2, 0.04,
                            M["post"])
        build_pavilion(M)
        build_lawns(M)                       # [v6 (3)] lawn bands + street trees
        build_deck(M)
        build_reeds(M)
        # 4 landing marker stone posts — at the landing x centre, outside the stair width (y±5.6)
        lp = PARAMS["land_posts"]
        for li, si in enumerate(PARAMS["stairs"]["landing_steps"]):
            xa, xb, _ = steps[si]
            for yi, yy in enumerate(lp["ys"]):
                sc.add_cylinder(stage, f"{ROOT}/LandPost_{li}_{yi}",
                                ((xa + xb) / 2.0, yy,
                                 steps[si][2] + lp["h"] / 2.0),
                                lp["r"], lp["h"], M["stone"], collider=True)
        # 4 benches — [§3] beside anchors (pavilion · lawn band edge · deck), yaw jitter +-3~8 deg
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0, M["post"],
                           yaw=yaw)
        # [v6 rework (2)] 1 duck boat — box assembly → **ellipsoid assembly**.
        #   Judgment: "at 400 % crop it is a white untextured box + a plank neck — it does not
        #   read as a 'boat'". The duck silhouette is now built from 6 curved parts (hull, breast, stern, 2 wings),
        #   and the canopy goes from a thick box (h 0.45) to a thin plate (0.05) + 4 posts so it
        #   no longer hides the hull curvature. Albedo white 0.86 → yellow 0.78/0.70/0.25.
        #   Draught : hull radius 0.36, centre 0.12 above the water → 0.24 below the water /
        #   0.48 above it (approximating the measured draught ratio of a real duck boat). Heading via rot_group.
        bt = PARAMS["boat"]
        hl, br, st_, wg = bt["hull"], bt["breast"], bt["stern"], bt["wing"]
        hd, bk, cp = bt["head"], bt["beak"], bt["canopy"]
        for i, b in enumerate(PARAMS["boats"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/DuckBoat_{i}",
                                     (b["cx"], b["cy"]), b["rotz"])
            bx, by = b["cx"], b["cy"]
            hz = water_z + bt["hull_float"]               # hull centre z
            SPH = sc.add_sphere
            SPH(stage, f"{grp}/Hull", (bx, by, hz), hl, M["duck"])
            SPH(stage, f"{grp}/Breast", (bx + hl[0] * 0.71, by, hz + 0.14),
                br, M["duck"])
            SPH(stage, f"{grp}/Stern", (bx - hl[0] * 0.85, by, hz + 0.18),
                st_, M["duck"])
            for tag, sgn in (("P", 1.0), ("S", -1.0)):
                SPH(stage, f"{grp}/Wing_{tag}",
                    (bx - 0.15, by + sgn * bt["wing_dy"], hz - 0.04), wg,
                    M["duck"])
            # Neck — a cylinder leaning forward from above the breast by neck_lean deg.
            #   add_cylinder does **rotY about the centre**, so the neck tip (where the head goes)
            #   moves (neck_h/2)·(sinθ, 0, cosθ) from the centre. The head centre is
            #   a further head_rz·0.55 out from there along the same axis.
            nx = bx + hl[0] * 0.81
            nz = hz + 0.38 + bt["neck_h"] / 2.0
            sc.add_cylinder(stage, f"{grp}/Neck", (nx, by, nz),
                            bt["neck_r"], bt["neck_h"], M["duck"],
                            rotY=bt["neck_lean"])
            lean = math.radians(bt["neck_lean"])
            d_nh = bt["neck_h"] / 2.0 + hd[2] * 0.55       # 0.41
            hxc = nx + d_nh * math.sin(lean)
            hzc = nz + d_nh * math.cos(lean)
            SPH(stage, f"{grp}/Head", (hxc, by, hzc), hd, M["duck"])
            sc.add_box(stage, f"{grp}/Beak",
                       (hxc + hd[0] + bk[0] / 2.0, by, hzc - 0.04), bk,
                       M["beak"])
            # Canopy — thin plate + 4 posts (was: a 0.45-high box = the main cause of the 'white box')
            #   Plate top face = 1.55 m above the water (the measured band for duck-boat canopies), slightly
            #   above the crown of the head (1.41 above the water) → it does not hide the head in silhouette.
            cz = hz + 1.40                      # canopy plate centre
            czb = hz + 0.10                     # post foot (embedded in the hull)
            sc.add_box(stage, f"{grp}/Canopy", (bx - 0.30, by, cz), cp,
                       M["duck_top"])
            ph_c = cz - cp[2] / 2.0 - czb
            for tag, sx_, sy_ in (("SW", -1.0, -1.0), ("SE", 1.0, -1.0),
                                  ("NW", -1.0, 1.0), ("NE", 1.0, 1.0)):
                sc.add_cylinder(
                    stage, f"{grp}/CanopyPost_{tag}",
                    (bx - 0.30 + sx_ * (cp[0] / 2.0 - 0.06),
                     by + sy_ * (cp[1] / 2.0 - 0.06), czb + ph_c / 2.0),
                    bt["canopy_post_r"], ph_c, M["duck_top"])

    def build_flat_fill(M):
        """hazard_stairs=False control : stairs and banks unified into z=0 flat ground (water kept)."""
        sc.add_box(stage, f"{ROOT}/FlatFill", (16.0, 0.0, -0.25),
                   (56.0, 80.0, 0.5), M["stone"], collider=True)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_terrace(M)
    if cfg["hazard_stairs"]:
        build_stairs(M)
        build_embankment(M)
        build_ground_kit(M)             # [W2-D] terrace ground elements
    else:
        build_flat_fill(M)
    build_river(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if cfg.get("cue_sign"):
        build_signs()                       # [v5 shared layer]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke:
        # [v7] roof mesh normals + §4 albedo cap self-check (no render)
        roof_normal_selfcheck()
        albedo_selfcheck()
        # binding check right after assembly — follow-up to judgment §6 (2) ("if it is still bright, check the binding")
        rp = stage.GetPrimAtPath(f"{ROOT}/Pavilion/Roof")
        fp = stage.GetPrimAtPath(f"{ROOT}/Pavilion/Finial")
        from pxr import UsdShade, UsdGeom as _UG
        rb = UsdShade.MaterialBindingAPI(rp).GetDirectBinding() if rp else None
        fb = UsdShade.MaterialBindingAPI(fp).GetDirectBinding() if fp else None
        rmat = rb.GetMaterialPath() if rb else "(없음)"
        fmat = fb.GetMaterialPath() if fb else "(없음)"
        ni = _UG.Mesh(rp).GetNormalsInterpolation() if rp else "(없음)"
        nn = len(_UG.Mesh(rp).GetNormalsAttr().Get() or []) if rp else 0
        print("=" * 68)
        print("scene09 [v7] 지붕/절병통 재질 바인딩 · 법선 저작 확인")
        print(f"  Roof   바인딩 {rmat} · normals {nn}개 · "
              f"interpolation {ni}")
        print(f"  Finial 바인딩 {fmat}")
        print(f"  ⇒ 두 프림 동일 재질 "
              f"{'OK' if str(rmat) == str(fmat) else 'FAIL'} · "
              f"법선 저작 {'OK' if nn > 0 else 'FAIL'}")
        # [v8 Y1] MDL parameters measured — judgment recommendation (b) ("if the binding is right, look at the specular family").
        #   Binding and normals already came out OK in the v7 round. To stop the next round
        #   digging in the same place, **the shader input values themselves** are logged.
        try:
            shp = stage.GetPrimAtPath("/World/Looks/PavRoof/Shader")
            sh = UsdShade.Shader(shp)
            got = {}
            for nm in ("diffuse_color_constant", "reflection_roughness_constant",
                       "specular_level", "metallic_constant"):
                i = sh.GetInput(nm)
                got[nm] = i.Get() if i else "(미지정=MDL 기본값)"
            print("  PavRoof MDL 입력 실측:")
            for nm, val in got.items():
                print(f"    {nm:32s} {val}")
            sl = got["specular_level"]
            print(f"  ⇒ specular_level {'OK(0.0 명시)' if sl == 0.0 else 'FAIL'}"
                  f" — 미지정이면 OmniPBR 기본 0.5(F0 0.04)가 살아 "
                  f"roughness {mp['roof_tile_rough']} 광로브로 천공/태양을 가산한다")
        except Exception as e:
            print(f"  [WARN] MDL 입력 조회 실패: {e}")
        print("=" * 68)
        print("[SMOKE] 부팅+조립+조명 완료 — 렌더 없이 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views(run, z_bot, water_z, water_x0)
    _v0 = views["ghat_walk"]
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

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, views, out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene09_{ts}.png")
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
