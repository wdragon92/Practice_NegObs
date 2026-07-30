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

[W3 CB-1] w3_execution_spec_v1.md Sec.4.3 WP-S5 · Sec.5.2 CB-1. Two rows, one commit.
  (A) **S09-A — three diagnostic side cuts** (Sec.10.5). The user could not judge this stair
     because **not one of the five existing mise-en-scene cuts crosses the flight axis**:
     ghat_walk / waterline / from_river / across_river all look along or head-on to ±X and
     park_vista is framed on the pavilion, so 140-200 mm risers on a 10 m-wide flight
     foreshorten into a flat masonry wall. Added to `build_views` **after** park_vista:
     `stair_flank_raking` (primary, raking profile from over the water at +X/-Y) ·
     `stair_flank_grazing` (down the flight from step 4 — the concealment case) ·
     `landing_return` (cross-flight close-up on landing 1). Mise-en-scene registry only —
     **no `sc.grid_views` call change and no preset touched**, so the 9 preset cuts stay
     byte-identical and the judgement baseline is unaffected.
  (B) **S09-C — stone posts off the stair face** (Sec.8 GT-10). The four `land_posts` stood
     on the revetment at the two landing top faces (z -2.040 / -4.080), reading as posts
     embedded partway up the stair face at different heights. They move to the terrace
     promenade edge, all four at one height (x -0.80, z 0.0, four y stations). Props only —
     hazard geometry (steps · landings · embankment · terrace) is untouched, and at
     |y| ≥ 5.6 they sit outside the ±30 deg FOV of every grid preset [computed].
  These two rows are coupled: `landing_return` runs at constant x = 4.34, which is exactly
  the landing-1 x centre the old posts stood on, so the old post at (4.34, -5.6) would have
  blocked the new cut outright.

[W3 S09 · G9 renovation] `Docs/surveys/w3_intake_v2_images.md` §2 scene09 (b)/(c)/(e) + §7 ruling 8
  (**R09-1: scene09 = autumn**) + §3(ii) (rectangular-ground sweep) + `w3_mb_patch_v1.md` MB-F1/MB-F2.
  The target image is `Docs/reference_photos/Generated Image - Scene09.jpg` (**G9**) — an aerial
  oblique of a Korean lake park: terraced planting beds retained by **dry-stone 자연석 walls**,
  massed ground cover one species per bed, a **zigzag timber boardwalk** stepping to wide stone
  step courses, reeds and lily pads at the water, and a **full autumn hillside** across the lake.
  Seven rows land here; every one of them stays **outside the ±30° FOV of all nine grid presets**
  (`fov_selfcheck()` asserts it from the coordinates, no render), so the judged near-ground cuts
  and the drop-cue behaviour of the 36-step flight are untouched.
    (1) **terraced beds + dry-stone retaining walls** — 5 beds (3 on −Y, 2 on +Y) at bed-top
        z 0.50 / 1.00 / 1.50, each faced in coursed 자연석 blocks with a 1:6 batter. New collision
        boxes beside the terrace (the **GT-15 precedent**), no walked-surface z change.
    (2) **massed ground cover, one species per bed** — `sc.place_shrubs(pool=[<one asset>])`, so a
        bed is monospecific **by construction** rather than by the per-bed draw. The species were
        chosen from a **measured** seasonal audit (`season_audit()`), not from names.
    (3) **zigzag timber boardwalk** — the straight 2.4 × 44 m slab is replaced by a 3-leg /
        2-turn boardwalk in **stocked 방부목 sections** (scene10 precedent: 산림청고시 2014-2
        thickness series 21/24/27/30 mm, width 90–300 mm in 10 mm steps → 25 × 140 데크판재;
        120각 column, 90각 newel). Top face stays **0.06** — the walked surface does not move.
    (4) **`plaza_water` patch row deleted scene-side** (MB-F1: the GT-24 profile deletion could not
        reach this scene because the scene authors its own `surface` row). A waterfront terrace has
        no repair cause — §3(ii)'s own ruling for this profile, applied where it can actually land.
    (5) **`SCENE_PLANS["scene09"]` fixture synced** to the wired call (MB-F2 / ledger §7 **W9**).
    (6) **far-bank building silhouettes deleted → autumn hillside belt.** G9 has no buildings: the
        horizon is rolling wooded hills in ginkgo yellow / maple orange. The 2 dark boxes were the
        v5 horizon-closure device; the hills close the horizon **and** carry the season.
    (7) **belt species declared** — `build_tree(belt=True)` on the far-bank row, which activates
        `SCENE_SPECIES["Scene09"][1] = "oak_black"` (K4-F4: a belt stays inert until a scene passes
        it). Route trees keep the scene default `birch`.
  Deliberately **not** done, with reasons, in `Docs/reports/w3_s09_v1.md` §3: timber steps laid on
  the embankment stone (moves a walked surface for no research value) · G9's stepping-stone slabs
  (the user's rectangular-ground ban is live and cannot be adjudicated here) · the light rig
  (the dataset's controlled variable — season is carried by content, never by the sun).

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
    #    09-2 slab loss ("flagstone loss") 4-6 per 100 m^2 -> patch field   **DELETED, W3 S09**
    #    09-3 water film / algae decals
    #
    #  [W3 S09 · row (4)] **The patch row is deleted.** `w3_intake_v2_images.md` §3(ii)'s
    #  enumeration ruled `plaza_water` (**09**, the profile's only carrier) *"a waterfront
    #  terrace with two repairs and no cause → 0"*. GT-24 executed that at the profile level
    #  (`ground_kit.py:1755`, `8b6baa7`) and it **could not reach this scene**: scene09 authors
    #  its own `surface` row here, so the profile deletion moved 0 prims and 0 pixels in 09 —
    #  measured, and that null is the direct evidence for `w3_mb_patch_v1.md` **MB-F1**. The row
    #  the sweep was aimed at is *this* tuple, and §3 GT-24's amended scope cell says in as many
    #  words that 09 keeps its scene-side row and it is **the scene owner's to delete**. Done here.
    #  The `sites patch=[...]` list goes with it rather than being left inert (the `scene05` /
    #  `sceneN1` dead-list precedent, declared in GT-24's change cell as the implementing lane's
    #  choice — this lane cleans).
    #  What survives is correct and stays: `("crack", 4)` (irregular, DEC-1 class) and
    #  `("stain", ("water",))` (a DEC-1 lobe). The **joint grid stays too** — §3(ii) item 4:
    #  *"orthogonal, axis-aligned, correct and staying. A 600 mm granite module IS a grid of
    #  rectangles"* — and G9 shows exactly that grey stone-block paving at bottom-left.
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
    # [W3 S09 · row (6)] **The 2 far-side building silhouettes are DELETED.**
    #   They were the v5/B-09-2 horizon-closure device ("the top half of the frame was uniform
    #   teal, an infinity pool"). G9 answers the same question differently and the image is the
    #   law here: there is **not one building** in the target — the far shore is a wooded
    #   shoreline backed by **rolling autumn hills**, and that is what closes the horizon.
    #   Deleting them is also the honest reading of the scene's own identity: a "lake park
    #   waterfront" whose far bank carries two 7 m dark boxes is reading as a city river.
    #   Replacement = `far_hills`, which closes the horizon **higher** (12–19 m vs 7 m) and
    #   over a **wider** span, so B-09-2's failure mode cannot return; `horizon_selfcheck()`
    #   asserts the elevation subtended at the two water cameras against the old boxes.
    #
    # Autumn hillside belt — 3 ridges at increasing distance, each a row of overlapping
    #   ellipsoid masses on a low ridge body. Colours are the two autumn tones G9 shows
    #   (ginkgo yellow, maple orange) plus the dark conifer that a Korean hillside always
    #   carries; the far ridge is desaturated toward the sky (aerial perspective), which is
    #   why `hill_c` is both lighter and greyer than `hill_a`, not darker.
    #   (cx, cy, sx, sy, h, tone) — tone indexes (hill_a, hill_b, hill_c).
    far_hills=[dict(cx=78.0, cy=-26.0, sx=16.0, sy=30.0, h=12.0, tone=0),
               dict(cx=76.0, cy=2.0, sx=15.0, sy=34.0, h=13.5, tone=1),
               dict(cx=79.0, cy=30.0, sx=16.0, sy=30.0, h=12.5, tone=0),
               dict(cx=98.0, cy=-14.0, sx=20.0, sy=44.0, h=17.0, tone=2),
               dict(cx=100.0, cy=26.0, sx=20.0, sy=40.0, h=16.0, tone=2),
               dict(cx=126.0, cy=6.0, sx=26.0, sy=64.0, h=19.0, tone=2)],
    hill=dict(blobs=9, blob_r=0.62, spread=0.78, seed=91),
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
    # 4 stone posts. [W3 CB-1 · S09-C] **moved off the stair face onto the terrace.**
    #   Defect (w3_intake_06_10 S09-C, visible in look_check/scene09/260730_w2d_fix/
    #   pt_noon_across_river.png and pt_noon_from_river.png): the four posts stood at
    #   the two landing x centres (4.34 / 9.28) on the embankment at y ±5.6, i.e. on
    #   the **revetment face**, with their bases at the landing top faces z -2.040 and
    #   z -4.080. They read as posts embedded partway up the stair face at three or
    #   four different heights. A Korean 계선주 / quay post stands on the **quay top**,
    #   at the level a boat is tied — never on a stair slope.
    #   Fix, per w3_execution_spec_v1 Sec.8 GT-10 ("to the terrace edge or the lowest
    #   landing"): **terrace edge**, all four at one height, z base 0.0.
    #     · `x = -0.80` — the terrace's own declared promenade edge line: it is
    #       `lawns[*].x1` (-0.8) verbatim. It is also the deepest setback available
    #       here: with r 0.24 the footprint reaches x -1.04, clearing the pavilion
    #       **eave tip x -1.15** (build_pavilion docstring) by 0.11 m [computed], and
    #       standing 0.56 m back from the stair head lip at x = 0.
    #     · `ys` — 4 stations on that one line, both taken from existing PARAMS, none
    #       invented: ±5.6 is the row's own current y (0.6 m outside the flight edge
    #       y ±5), ±12.0 is `lawns[*].y0 / y1`, the lawn bands' inner edge.
    #       The `mooring` pile stations (±3.8 / ±13.5 / ±19.0) are deliberately NOT
    #       reused: a pile sits at x -1.2, only 0.40 m away, and r 0.09 + r 0.24 = 0.33
    #       would leave a 70 mm gap between two very differently sized posts.
    #   Checks [computed]: |y| ≥ 5.6 at x -0.80 bears ≥ 31.3 deg from the furthest grid
    #   preset eye (-10, 0) → **all four stay outside the ±30 deg preset FOV**, so they
    #   cannot occlude the stair-head drop edge in any judged cut. Hazard geometry
    #   (steps · landings · embankment · terrace) is untouched — these are props.
    #   The ±12.0 pair straddles the lawn bands' river-side corner; `lawn_proud` is
    #   0.03 m, so there is no step of consequence under the base.
    land_posts=dict(r=0.24, h=2.1, x=-0.80, z=0.0,
                    ys=(-12.0, -5.6, 5.6, 12.0)),
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
    # 4 benches (river view) — [§3] beside anchors (pavilion · bed wall · boardwalk) · yaw jitter
    #   [W3 S09] re-sited off the two anchors that moved. 0 and 2 used to sit **inside** the new
    #   +Y bed footprints (B4 y0 13.2 · B5 x −14.4..−8.0) and 1 sat 0.2 m off boardwalk leg L3;
    #   each moves to 0.8–1.0 m clear of its new anchor, which is the same relationship the old
    #   comment describes. Bench 3 (−11.0, −13.4) is **unmoved** — L3's south edge is y −12.4, so
    #   it is already the declared 1.0 m clear [computed].
    #   0 : 0.8 m south of bed B4's wall face (y 13.2), 1.74 m north of the pavilion plinth
    #   1 : 1.0 m south of boardwalk leg L3 (y −12.4)
    #   2 : 1.0 m south of bed B5's wall face (y 13.2)
    #   3 : 1.0 m south of boardwalk leg L3 — unchanged
    benches=[(-4.6, 12.4, 86.5), (-4.6, -13.4, 274.0),
             (-11.0, 12.2, 93.5), (-11.0, -13.4, 265.5)],
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
    # [W3 S09 · row (3)] **straight slab → zigzag boardwalk in stocked 방부목 sections.**
    #   G9's boardwalk is the scene's leading line: it comes off the park, turns twice, and runs
    #   out to the head of the stone step courses. The old element was a 2.4 × 44.0 m plank-seamed
    #   plate at one x — a *floor*, not a route: it makes no turn, it goes nowhere, and at y ±22 it
    #   is 22 m long in a frame that never sees its ends.
    #   **3 legs, 2 right-angle turns, net progress toward the water** (legs overlap at the turns
    #   by their own width, so the corners are solid and no seam opens):
    #     L1  y −20.4…−18.0, x −16.0…−9.2   (east, off the park)
    #     L2  x −11.6…−9.2,  y −20.4…−12.4  (north, along the shore)
    #     L3  y −12.4…−10.0, x −11.6…−0.6   (east, out to the step courses)
    #   Width **2.400 m** on every leg — unchanged from the old deck, and 조경설계기준 5.9(4)'s
    #   1.5 m minimum with margin for a two-way lakeside promenade.
    #   **The walked surface does not move**: `top_z` stays **0.060**, the value the old deck
    #   shipped, so this is a planform change and a member change, not a z change [computed].
    #   **Sections are stocked, per the scene10 precedent** (`scene10:262-265`, 산림청고시 2014-2
    #   제8조 fixes the 데크판재 thickness series at 21/24/27/30 mm and the width series at
    #   90–300 mm in 10 mm steps): plank **25 × 140** laid across the leg with a 6 mm gap ·
    #   joist **38 × 140** at 0.45 m pitch · beam **90 × 90** · post **120 × 120** (scene10's
    #   stocked 기둥재) · edge/rim board **25 × 140** on the free sides.
    #   The old `seam_step 0.62` "3–4 board bundle" abstraction is retired: a 0.146 m plank pitch
    #   is the real thing, and at 0.06 m above grade the members below are what read at a raking
    #   angle, which is exactly what G9 shows.
    #   **Termination.** L3 ends at x = **−0.60**, i.e. 0.60 m short of the stair head (x = 0), at
    #   |y| 10.0…12.4 — **1.04 m outside the ±30° cone of the furthest grid preset eye** [computed,
    #   `fov_selfcheck`]. The boardwalk therefore *delivers you onto the stone step courses* the way
    #   G9 shows, without a single timber member landing on the embankment: a tread laid on the
    #   stone would raise a walked surface by the 25 mm plank (above `GT_DELTA` 0.020) and buy the
    #   research nothing. Declined on purpose — `Docs/reports/w3_s09_v1.md` §3.
    boardwalk=dict(
        top_z=0.06, width=2.40,
        legs=[("L1", -16.0, -20.4, -9.2, -18.0, "x"),
              ("L2", -11.6, -20.4, -9.2, -12.4, "y"),
              ("L3", -11.6, -12.4, -0.6, -10.0, "x")],
        plank=(0.140, 0.025), plank_gap=0.006,   # 25 x 140 데크판재
        joist=(0.038, 0.140), joist_pitch=0.45,  # 38 x 140 장선
        beam=0.090, post=0.120, post_pitch=2.70,  # 90각 멍에 · 120각 기둥
        rim=(0.025, 0.140)),                     # 25 x 140 마구리/코너 보드
    # [W3 S09 · rows (1)(2)] **terraced planting beds retained by dry-stone 자연석 walls.**
    #   G9's whole left half. Each bed is a raised planting mass whose **water-facing (+X) face and
    #   its exposed flank** are laid up in coursed 자연석 blocks; the beds step **up away from the
    #   water** (0.50 → 1.00 → 1.50), which is what the image shows and what a real 계단식 화단 on a
    #   flat lakeside terrace has to do.
    #   **Placement law**: every bed corner nearest the travel axis is asserted outside the ±30°
    #   FOV of all nine grid presets by `fov_selfcheck()` — the closest is B1's (−2.60, −5.80),
    #   which bears **38.1°** from the furthest preset eye (−10, 0) [computed]. So the beds cannot
    #   occlude the stair-head drop edge in any judged cut, and the flight (|y| ≤ 5) and terrace
    #   top face are untouched. They read in `park_vista`, `from_river`, `across_river` and the new
    #   `g9_oblique`.
    #   `species` is the **single asset** the bed is massed with — monospecific *by construction*
    #   (a one-member `pool=`), which is stronger than K4(b)'s per-bed draw and makes the record
    #   exact. Every choice is justified by `season_audit()`'s measured hue fractions, not by name.
    #   (tag, x0, y0, x1, y1, top_z, species asset, target_h, n, seed)
    beds=[dict(tag="B1", x0=-8.0, y0=-9.4, x1=-2.6, y1=-5.8, top=0.50,
               species="Shrub/Burning_Bush.usd", h=0.85, n=15, seed=911,
               faces=("+x", "-y")),
          dict(tag="B2", x0=-14.4, y0=-9.4, x1=-8.0, y1=-5.8, top=1.00,
               species="Shrub/Juniper.usd", h=0.60, n=16, seed=912,
               faces=("+x", "-y")),
          dict(tag="B3", x0=-20.8, y0=-9.4, x1=-14.4, y1=-5.8, top=1.50,
               species="Shrub/Holly.usd", h=1.05, n=14, seed=913,
               faces=("+x", "-y")),
          dict(tag="B4", x0=-8.0, y0=13.2, x1=-2.6, y1=18.4, top=0.50,
               species="Shrub/Yew.usd", h=0.70, n=16, seed=914,
               faces=("+x", "+y")),
          dict(tag="B5", x0=-14.4, y0=13.2, x1=-8.0, y1=18.4, top=1.00,
               species="Shrub/Boxwood.usd", h=0.65, n=17, seed=915,
               faces=("+x", "+y"))],
    #   Dry-stone (자연석 건식쌓기) facing. Course height 0.22 m and block length 0.36–0.62 m are
    #   the ordinary Korean 자연석 쌓기 band; `batter` 1:6 is the dry-laid lean that keeps a
    #   mortarless wall standing, and it is what makes the courses read as *stacked* rather than
    #   as a printed texture. `jitter` moves each block's face in and out by up to ±18 mm so no two
    #   courses line up — a dry-stone wall has **no continuous vertical joint**, which is the single
    #   cue that separates it from a block wall.
    #   **LINT-10 adjudication, made in the parameter name.** The linter asks the owning WP to
    #   classify any `jitter=` kwarg: §1.2 X2 keeps **size / interval variation** and abolishes
    #   **placement jitter**. This one is size variation and the code says so — each block's
    #   *bedding face is pinned to the wall plane* and only its **depth** is drawn, so the front
    #   face moves as a consequence of the block being a different stone, not because the stone
    #   was nudged. Renamed `jitter` -> `depth_var` so the classification is visible at the call
    #   site instead of living in a report.
    drystone=dict(course_h=0.22, block_lo=0.36, block_hi=0.62, batter=1.0 / 6.0,
                  depth=0.26, depth_var=0.018, gap=0.012, cap_h=0.10, seed=97),
    # [W3 S09] G9's **root/stump feature on a moss bed** and the boulders sitting in the beds.
    #   Both go through the **T4b wrapper** (`w3_t4b_v1.md` §1.1): `treatment="mtlxoff"` blocks the
    #   MaterialX terminal whose `ND_normalmap_float` is missing from this runtime's Sdr registry
    #   (**MD-F3**, the red error fallback) and falls back to the UsdPreviewSurface terminal the
    #   same material already carries — so instancing and the asset's own normal survive together.
    #   `rock_moss_set_01__mtlxoff.usda` / `tree_stump_01__mtlxoff.usda` are pre-authored and
    #   committed; nothing here writes into `assets/urban_wrap/`.
    #   (asset, bed tag, u, v, target_h, yaw) — u/v are fractions of the bed footprint.
    bed_features=[("tree_stump_01", "B2", 0.42, 0.52, 1.25, 24.0),
                  ("rock_moss_set_01", "B1", 0.68, 0.40, 0.62, 137.0),
                  ("rock_moss_set_01", "B3", 0.30, 0.58, 0.78, 291.0),
                  ("rock_moss_set_01", "B4", 0.55, 0.46, 0.55, 63.0)],
    # [W3 S09] lily pads and floating leaf rafts — G9's right half. Thin discs on the water.
    #   **Sited beside the reed beds at |y| ≥ 19.6, not out in the open water**, for two reasons
    #   that agree: (a) `fov_selfcheck()` caught the first siting (|y| 9.8–15.5) **inside** the
    #   ±30° cone of the `d10` presets — at 25–31 m the h0.3 sight line lands on the water at
    #   x ≈ 21, which is exactly where those pads were, so they would have moved judged pixels;
    #   (b) it is where lily pads actually grow. 수련 needs sheltered, shallow, still water —
    #   the lee of a reed stand — not the middle of a 30 m open lake in front of a public
    #   waterfront stair. The gate and the botany point the same way; the gate found it first.
    #   Margins after the move (nearest corner, furthest preset eye (−10, 0)) [computed]:
    #   +5.1° · +7.1° · +3.2° · +5.1°.
    #   (cx, cy, n, r_lo, r_hi, seed)
    lilies=[(16.0, -21.5, 14, 0.20, 0.42, 51), (20.0, -26.0, 12, 0.22, 0.46, 52),
            (16.5, 20.5, 13, 0.20, 0.40, 53), (21.0, 25.0, 11, 0.24, 0.48, 54)],
    lily=dict(t=0.012, spread=1.9),
    # [v5 adopted] reed stands — the embankment near the waterline (**outside** the stair width y±5) and the far bank.
    #   (cx, cy, n, seed). x 12.2~13.6 = just below the waterline (water_x0≈11.92) →
    #   reeds appear to rise out of the water. No interference with the hazard geometry (stairs y±5).
    reeds=[(12.2, -8.5, 9, 11), (12.9, -13.0, 11, 12), (12.2, -18.0, 9, 13),
           (13.6, -24.0, 12, 14),
           (12.2, 8.5, 9, 21), (12.9, 13.0, 11, 22), (12.2, 18.0, 9, 23),
           (13.6, 24.0, 12, 24),
           (45.6, -14.0, 10, 41), (45.6, 14.0, 10, 42)],
    reed=dict(r=0.022, h_lo=1.1, h_hi=1.9, spread=0.85, tilt=9.0,
              # [W3 S09] plume = the buff seed head, 0.22 m of the culm top at 1.9x the radius.
              #   Autumn 갈대 is read by its plume, not by its stem.
              plume_h=0.22, plume_r_mul=1.9),
    # [v5 shared layer] Korean sign — (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   [v6] Info (−6.5, 5.5) → **(−7.0, −5.6)** : the +Y side is filled by the pavilion (plinth y 5.74~)
    #     and the deck (x −10.0..−7.6), leaving no room → moved to the symmetric position on the south side.
    #     0.6 m from the deck's east end, 0.6 m outside the stair width (y±5).
    #   Camera check (FOV +-30 deg): grid eye=(−2/−5/−10, 0) → behind / behind /
    #     −61.8 deg (out), ghat_walk(−4,0) −118.2 deg (out), waterline faces the +X water side → behind.
    #     from_river(23.92,0) +10.3 deg (31.4 m, distant) · park_vista −26.2 deg (27.8 m,
    #     bottom-left of frame) = the sign board enters the mise-en-scene cut with 0 sight-line occlusion.
    #   [W3 S09] **The flat post-and-panel sign becomes a lectern (안내 거치대).** G9 carries
    #     exactly one grey information lectern and it stands **beside the deck at the water end**,
    #     not out on the lawn: a raked panel on a low plinth, chest height, read from above.
    #     Re-sited (−7.0, −5.6) → **(−1.9, −9.4)**: 0.70 m east of bed B1's face (x −2.6) and
    #     0.60 m north of boardwalk leg L3 (y −10.0), i.e. it is *at* the point the boardwalk
    #     hands you to the stone step courses — the position that makes an information lectern
    #     mean something. Its old site is now 0.20 m from bed B1's y1 face and could not be kept.
    #     Camera re-check [computed, `fov_selfcheck`]: grid eyes (−2/−5/−10, 0) → −86.2 / −71.7 /
    #     −49.3 deg, **all outside ±30 deg**; park_vista −18.9 deg at 31.4 m = bottom-left of frame.
    #     `panel_tilt` 22 deg is the ordinary Korean 안내판 rake (readable standing at 1.5 m).
    signs=[("Info", "sign_info", -1.9, -9.4, 0.0, 180.0, 0.92, 0.62)],
    lectern=dict(plinth=(0.46, 0.30, 0.86), panel_tilt=22.0, panel_t=0.05,
                 leg_r=0.045),

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
        deck_tint=(0.95, 0.88, 0.78),          # timber boardwalk planks (grey weathered wood)
        # [W3 S09 row (3)] the members under the plank deck are **not** the same tone as the
        #   walking face: a deck plank silvers in the weather, a joist in permanent shade does
        #   not. 0.72x the plank keeps the same hue and drops the value one step, which is what
        #   separates the members at a raking angle. (scene10 ships the same relationship:
        #   deck L* 55.0 / stringer L* 53.0.)
        joist_tint=(0.68, 0.63, 0.56),
        post_tint=(0.58, 0.53, 0.47),          # 120각 기둥 — one step darker again
        seam_color=(0.030, 0.026, 0.022),      # (kept: dark-colour rule, used by the rim shadow)
        # [W3 S09 row (1)] dry-stone 자연석. A dry-laid Korean retaining wall is a **warmer and
        #   darker** stone than the machined granite paving beside it — it is a field stone, not a
        #   sawn slab, and it carries lichen. 0.86x the paving tint with a warm bias keeps it
        #   inside the same albedo family (so `albedo_selfcheck` still governs it) while reading
        #   as a different material at 20 m.
        drystone_tint=(0.55, 0.52, 0.46),
        drystone_cap_tint=(0.60, 0.57, 0.50),  # the coping course, weathered a shade lighter
        # [W3 S09 row (6)] autumn hillside. The three tones are the two that dominate G9
        #   (ginkgo yellow, maple orange) plus the dark conifer band a Korean hillside always
        #   carries; `hill_c` is the far ridge and is deliberately **lighter and greyer**, not
        #   darker — aerial perspective washes a distant ridge toward the sky, and the old
        #   `far_color` boxes got that backwards (a 0.13 near-black silhouette at 70 m).
        hill_a=(0.268, 0.196, 0.078),          # 단풍 maple orange-red
        hill_b=(0.288, 0.252, 0.086),          # 은행 ginkgo yellow
        hill_c=(0.176, 0.176, 0.148),          # far ridge, desaturated toward the sky
        hill_rough=1.0,
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
        # [W3 S09 · R09-1] **autumn.** A 갈대 stand in a Korean October is straw, not olive:
        #   the culm has gone over and the plume is buff. The measured reference is the library's
        #   own `lawngrass_a_basecolor.png` — orange 55.5 % / yellow 23.2 %, mean RGB
        #   (0.628, 0.595, 0.420) `[measured, season_audit]` — scaled into this scene's albedo
        #   band. Green 0.0 % is the point: the old (0.110, 0.125, 0.060) is a **summer** olive
        #   and it was the loudest wrong-season pixel block in the frame after the far bank.
        reed_color=(0.232, 0.196, 0.118), reed_rough=1.0,
        # plumes — the buff seed head that makes a reed bed read as a reed bed at 20 m
        reed_plume_color=(0.352, 0.318, 0.238), reed_plume_rough=1.0,
        lily_color=(0.086, 0.132, 0.062), lily_rough=0.62,
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
        # [W3 S09 row (6)] `far_color` (the distant **building** silhouette) is **deleted with its
        #   two boxes**; the horizon is closed by `hill_a/b/c` instead. Nothing else read it.
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        # [W3 S09 · R09-1] the **procedural blob canopy** (the fallback path of `sc.build_tree`,
        #   and the only tree colour this scene can actually set — see `season_audit()` item 3:
        #   the library has **zero** autumn foliage assets, all 10 measured tree/shrub rows read
        #   green 74–100 % with orange 0.000 and red 0.000). Pinned to the autumn pair G9 shows so
        #   the fallback cannot smuggle summer green into an autumn scene. Same reflectance band
        #   (6–12 %) the v6 side fix established, re-hued rather than re-levelled.
        canopy_a=(0.118, 0.086, 0.032),        # 단풍 orange-red
        canopy_b=(0.132, 0.116, 0.040),        # 은행 yellow
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
    # [W3 S09] the rows the renovation adds. The dry-stone wall is a **large vertical** face
    #   (5 walls, up to 6.4 m x 1.5 m) so criterion (A) governs it and (B) does not apply;
    #   the autumn hills are large but vertical-ish masses at 70-130 m, same treatment.
    #   `far_color` leaves the table with its two boxes (row (6)).
    ("자연석 옹벽",           "plaza_light", "drystone_tint",   True,  False),
    ("자연석 옹벽 갓돌",      "plaza_light", "drystone_cap_tint", False, True),
    ("데크 장선",             "wood_dark",   "joist_tint",      False, False),
    ("데크 기둥",             "wood_dark",   "post_tint",       False, False),
    ("가을 산능선 a(단풍)",   None,          "hill_a",          True,  False),
    ("가을 산능선 b(은행)",   None,          "hill_b",          True,  False),
    ("가을 산능선 c(원경)",   None,          "hill_c",          True,  False),
    ("갈대 이삭",             None,          "reed_plume_color", False, False),
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
# [C4] [W3 S09 · R09-1] **the scene's own seasonal audit** — §7 ruling 8 requires one per scene
#   ("each scene runs an internal seasonal audit (the cherry-blossom precedent)"), and the
#   instrument is the project's own: **pixels, never names** (`w3_execution_spec_v1.md` C-21,
#   *"Name heuristics are dead — the pixel rule is the only instrument"*).
#
# What it measures: for every shrub basecolor atlas in the library, the hue histogram of the
#   opaque, saturated texels. What it decides: which assets this scene may mass a bed with, now
#   that its season is pinned **autumn**. Measured this session (256 px thumbnails, alpha > 0.5,
#   value > 0.06, saturation > 0.15; hue bands in degrees):
#
#     atlas                        red   orange  yellow   yg    green   magenta  mean RGB
#     burningbush_leaf            0.399   0.005   0.002  0.262  0.000    0.000   (.654 .462 .430)
#     forsythiaflower             0.000   0.064   0.936  0.000  0.000    0.000   (.795 .706 .213)
#     green1 (Boxwood/Yew/Cedar)  0.000   0.000   0.000  1.000  0.000    0.000   (.410 .483 .229)
#     hollyprivet                 0.000   0.000   0.000  0.310  0.690    0.000   (.222 .344 .100)
#     lawngrass_a                 0.000   0.555   0.232  0.177  0.019    0.000   (.628 .595 .420)
#     rhododendron                0.046   0.003   0.222  0.000  0.000    0.729   (.657 .423 .623)
#     switchgrass                 0.000   0.000   0.000  0.000  1.000    0.000   (.321 .547 .267)
#
# Three findings this scene acts on:
#   1. **`Burning_Bush` is re-admitted, and it is the only warm mass in the library.** Its ban
#      (`scene_common.py` `SHRUB_ORNAMENT` block) reads *"red 30.2 % (autumn colour). Fine for C2,
#      but banned in summer and all-season scenes, so it is dropped from the global pool"* — the
#      ban's stated premise is the **global summer lock**, and §7 ruling 8 retired that lock. On a
#      scene pinned autumn the asset is not merely admissible, it is the correct one. It is taken
#      through `pool=`, not by re-adding it to `SHRUB_ORNAMENT` (that is K4's file and it is frozen).
#   2. **`Forsythia` stays banned even in autumn.** Yellow 93.6 % on a *blossom-only* atlas is
#      March–April, not October — an autumn pin does not license a spring flower. Named here so the
#      next reader does not "fix" the omission.
#   3. **The library has no flowering ground cover at all, and no autumn tree.** `Rhododendron`'s
#      magenta 72.9 % is the `/Root/Flowers` strip, which K4(0)'s season wrapper removes library-wide
#      (**K4-F1** — this is not a regression, it is the fix), and every tree row measures green
#      74–100 % / orange 0.000 / red 0.000. So G9's massed pink/white cosmos **cannot be built from
#      stock**: this scene delivers massed *autumn foliage* colour instead, and the flowering
#      ground-cover procurement is a routed follow-up (`w3_s09_v1.md` §7).
# ===========================================================================
# `scenes/main/` -> repo root -> assets/. Taken from `_HERE` rather than from `sc.VEG_DIR` so the
# audit still runs when the vegetation tree is unprocured (it then reports SKIP, never a pass).
_SHRUB_TEX_DIR = os.path.abspath(os.path.join(
    _HERE, "..", "..", "assets", "vegetation", "Shrub", "materials", "textures"))

# (atlas, verdict for an AUTUMN scene, why) — the verdicts are the decision, the numbers above
# are the evidence, and `season_audit()` re-measures the numbers rather than trusting this table.
_SEASON_RULE = [
    ("burningbush_leaf_basecolor.png", "USE",  "red 0.399 — 단풍 mass, autumn-correct"),
    ("hollyprivet_basecolor.png",      "USE",  "상록 — season-neutral"),
    ("green1_basecolor.png",           "USE",  "상록 — season-neutral"),
    ("switchgrass_basecolor.png",      "N/A",  "green 1.000, and unreachable: no VEG_SHRUBS row"),
    ("lawngrass_a_basecolor.png",      "N/A",  "straw, but unreachable: no VEG_SHRUBS row"),
    ("rhododendron_basecolor.png",     "USE",  "magenta 0.729 is the Flowers strip — K4(0) wrapper removes it"),
    ("forsythiaflower_basecolor.png",  "BAN",  "yellow 0.936 blossom-only = 3~4월, not autumn"),
]
# The assets this scene actually masses its beds with. Every one must be a `VEG_SHRUBS` row
# **and** carry a `USE` verdict above; `season_audit()` FAILs if either is untrue.
_BED_ASSET_ATLAS = {
    "Shrub/Burning_Bush.usd": "burningbush_leaf_basecolor.png",
    "Shrub/Juniper.usd":      "green1_basecolor.png",
    "Shrub/Holly.usd":        "hollyprivet_basecolor.png",
    "Shrub/Yew.usd":          "green1_basecolor.png",
    "Shrub/Boxwood.usd":      "green1_basecolor.png",
}


def _hue_fracs(path):
    """Hue-band fractions of the opaque, saturated texels of a basecolor atlas.
    Returns None when PIL or the file is missing (the audit then reports SKIP, never a pass)."""
    try:
        from PIL import Image
        im = Image.open(path).convert("RGBA")
        im.thumbnail((256, 256))
        a = np.asarray(im, dtype=np.float64) / 255.0
    except Exception:
        return None
    rgb, al = a[..., :3], a[..., 3]
    m = (al > 0.5) & (rgb.max(axis=-1) > 0.06)
    if not m.any():
        return None
    px = rgb[m]
    mx, mn = px.max(axis=-1), px.min(axis=-1)
    dl = mx - mn
    r, g, b = px[:, 0], px[:, 1], px[:, 2]
    hh = np.zeros(len(px))
    nz = dl > 1e-6
    i = (mx == r) & nz
    hh[i] = ((g[i] - b[i]) / dl[i]) % 6
    i = (mx == g) & nz
    hh[i] = ((b[i] - r[i]) / dl[i]) + 2
    i = (mx == b) & nz
    hh[i] = ((r[i] - g[i]) / dl[i]) + 4
    hue = hh * 60.0
    strong = np.where(mx > 0, dl / np.maximum(mx, 1e-9), 0.0) > 0.15
    n = float(len(px))

    def f(lo, hi):
        return float(((hue >= lo) & (hue < hi) & strong).sum()) / n
    return dict(red=float((((hue < 20) | (hue >= 330)) & strong).sum()) / n,
                orange=f(20, 45), yellow=f(45, 70), yg=f(70, 90),
                green=f(90, 160), magenta=f(280, 330),
                mean=tuple(float(v) for v in px.mean(axis=0)))


def season_audit(verbose=True):
    """[W3 S09 · §7 ruling 8] Per-scene seasonal audit. Returns (ok, rows).

    FAILs if (a) a bed is massed with an asset carrying a `BAN` verdict, (b) a bed asset is not a
    `VEG_SHRUBS` row (it would silently fall back to the default pool — see S09-F1), or (c) a
    `BAN` atlas measures as season-neutral after all (i.e. the ban is stale and should be revisited).
    """
    rows, fails = [], []
    veg_rows = {s[0] for s in getattr(sc, "VEG_SHRUBS", ())}
    for atlas, verdict, why in _SEASON_RULE:
        fr = _hue_fracs(os.path.join(_SHRUB_TEX_DIR, atlas))
        if fr is None:
            rows.append((atlas, verdict, None, "SKIP(텍스처/PIL 없음)", why))
            continue
        warm = fr["red"] + fr["orange"]
        tag = "OK"
        if verdict == "BAN" and fr["yellow"] < 0.10 and warm < 0.10:
            tag = "REVISIT(금지 근거 약함)"
        rows.append((atlas, verdict, fr, tag, why))
    used = []
    for b in PARAMS["beds"]:
        a = b["species"]
        atlas = _BED_ASSET_ATLAS.get(a)
        ver = dict((x[0], x[1]) for x in _SEASON_RULE).get(atlas)
        prob = []
        if a not in veg_rows:
            prob.append("VEG_SHRUBS 행 없음(S09-F1)")
        if ver == "BAN":
            prob.append("금지 종")
        if ver is None:
            prob.append("계절 판정 미등록")
        if prob:
            fails.append(f"{b['tag']}:{a}({'/'.join(prob)})")
        used.append((b["tag"], a, atlas or "-", ver or "-", "OK" if not prob
                     else "FAIL " + "/".join(prob)))
    ok = not fails
    if verbose:
        print("=" * 68)
        print("scene09 [W3 S09 · R09-1] 계절 감사 — 씬 고정 = **가을**  (픽셀 계측, 이름 금지)")
        print("=" * 68)
        for atlas, verdict, fr, tag, why in rows:
            if fr is None:
                print(f"  {atlas:32s} {verdict:5s} {tag}")
                continue
            print(f"  {atlas:32s} {verdict:5s} red {fr['red']:.3f} "
                  f"or {fr['orange']:.3f} yel {fr['yellow']:.3f} "
                  f"yg {fr['yg']:.3f} grn {fr['green']:.3f} "
                  f"mag {fr['magenta']:.3f}  {tag}")
            print(f"     └ {why}")
        print("  ── 화단별 단일 종 (pool=1개 = 구조적 단일종) ──")
        for tag, a, atlas, ver, st in used:
            print(f"  {tag}  {a:26s} {atlas:32s} {ver:5s} {st}")
        print(f"  ⇒ {'OK — 계절 위반 0건' if ok else 'FAIL: ' + str(fails)}")
        print("  ※ 한계(정직하게): 이 라이브러리에는 **개화 지피 자산이 0종**이고 "
              "**단풍 수목 자산도 0종**이다.")
        print("     G9 의 분홍/흰 코스모스 군식은 재고로 만들 수 없다 — 이 씬은 "
              "가을 **단풍 잎색** 군식으로 대체하고,")
        print("     개화 지피 조달은 후속 행으로 넘긴다 (w3_s09_v1.md §7).")
        print("=" * 68)
    return ok, rows


# ===========================================================================
# [C5] [W3 S09] **FOV self-check** — the placement law of this renovation, asserted from the
#   coordinates with no render. Every element the G9 rows add must lie outside the +-30 deg
#   horizontal FOV of **all nine** `sc.grid_views` presets, so it cannot occlude the stair-head
#   drop edge in any judged cut. This is the S09-C / land_posts argument (`:291`) generalised
#   into a gate: that row proved its four posts one at a time in a comment, and a comment does
#   not fail a build.
#   An element is OUT when, for every preset eye, either it is behind the eye (dx <= 0) or its
#   nearest corner bears more than `FOV_HALF` from the +X axis. The **nearest corner** is the
#   one that minimises |bearing| over the footprint, computed exactly (not sampled): x is taken
#   at its maximum and |y| at its minimum, which is the extremum of atan(|y|/dx) on a box.
# ===========================================================================
_FOV_HALF = 30.0
_PRESET_EYES = tuple((-d, 0.0) for d in (2, 5, 10))


def _box_min_bearing(x0, y0, x1, y1, eye):
    """Smallest |bearing| (deg) any point of the axis-aligned box subtends at `eye`, looking +X.
    Returns None when the whole box is behind the eye."""
    ex, ey = eye
    dx = max(x0, x1) - ex
    if dx <= 0.0:
        return None
    lo, hi = min(y0, y1) - ey, max(y0, y1) - ey
    dy = 0.0 if lo <= 0.0 <= hi else (lo if lo > 0.0 else hi)
    return abs(math.degrees(math.atan2(dy, dx)))


def fov_selfcheck(verbose=True):
    """[W3 S09] Returns (ok, rows). ok = every added element is outside every preset FOV."""
    items = []
    for b in PARAMS["beds"]:
        items.append((f"화단 {b['tag']}", b["x0"], b["y0"], b["x1"], b["y1"]))
    bw = PARAMS["boardwalk"]
    for tag, x0, y0, x1, y1, _ax in bw["legs"]:
        items.append((f"보드워크 {tag}", x0, y0, x1, y1))
    lx, ly = PARAMS["signs"][0][2], PARAMS["signs"][0][3]
    items.append(("안내 거치대", lx - 0.35, ly - 0.35, lx + 0.35, ly + 0.35))
    for cx, cy, _n, _rl, _rh, _s in PARAMS["lilies"]:
        sp = PARAMS["lily"]["spread"]
        items.append((f"수련 ({cx:.1f},{cy:.1f})", cx - sp, cy - sp, cx + sp,
                      cy + sp))
    rows, bad = [], []
    for name, x0, y0, x1, y1 in items:
        worst, worst_eye = 1e9, None
        for eye in _PRESET_EYES:
            b = _box_min_bearing(x0, y0, x1, y1, eye)
            if b is not None and b < worst:
                worst, worst_eye = b, eye
        if worst_eye is None:
            rows.append((name, None, None, "OUT(전 프리셋 후방)"))
            continue
        ok_i = worst > _FOV_HALF
        if not ok_i:
            bad.append(name)
        rows.append((name, worst, worst_eye,
                     f"OUT (여유 {worst - _FOV_HALF:+.1f}°)" if ok_i
                     else "**IN — 판정컷 침범**"))
    ok = not bad
    if verbose:
        print("=" * 68)
        print(f"scene09 [W3 S09] 신설 요소 프리셋 FOV 배제 검산 "
              f"(±{_FOV_HALF:.0f}° · 눈 x=-2/-5/-10, y=0 · 렌더 없음)")
        print("=" * 68)
        for name, b, eye, tag in rows:
            if b is None:
                print(f"  {name:22s} {tag}")
            else:
                print(f"  {name:22s} 최소 방위 {b:6.1f}° @eye{eye}  {tag}")
        print(f"  ⇒ {'OK — 판정 프리셋 침범 0건' if ok else 'FAIL: ' + str(bad)}")
        print("=" * 68)
    return ok, rows


def horizon_selfcheck(verbose=True):
    """[W3 S09 row (6)] The deleted far-side building boxes closed the horizon; the autumn hills
    must close it **at least as high** from the two water cameras, or B-09-2's 'infinity pool'
    failure comes back. Compares the elevation each mass subtends at `from_river` / `across_river`
    against the retired boxes (x0 66, h 7.0 on a far bank whose top face is `water_z + 1.6`).
    No render — pure trigonometry on the shipped coordinates."""
    _steps, _bz, _zb, water_z, _bh = compute_steps()
    fb = PARAMS["far_bank"]
    fb_z = water_z + fb["above_water"]
    water_x0 = _steps[PARAMS["stairs"]["nsteps"]
                      - PARAMS["stairs"]["submerge_from_bottom"]][0]
    cams = (("from_river", water_x0 + 12.0, water_z + 1.6),
            ("across_river", (water_x0 + PARAMS["water"]["x_far"]) / 2.0,
             water_z + 1.5))
    old = 7.0                      # retired far_buildings h, at x0 66.0
    rows, bad = [], []
    for tag, ex, ez in cams:
        e_old = math.degrees(math.atan2(fb_z + old - ez, 66.0 - ex))
        e_new = max(math.degrees(math.atan2(
            fb_z + h["h"] - ez, (h["cx"] - h["sx"] / 2.0) - ex))
            for h in PARAMS["far_hills"])
        okr = e_new >= e_old
        if not okr:
            bad.append(tag)
        rows.append((tag, e_old, e_new, okr))
    ok = not bad
    if verbose:
        print("=" * 68)
        print("scene09 [W3 S09] 지평 폐합 검산 — 폐기된 건물 실루엣 vs 가을 산능선")
        print("=" * 68)
        for tag, a, b, okr in rows:
            print(f"  {tag:14s} 구 건물 {a:+.2f}° → 신 능선 {b:+.2f}°  "
                  f"{'OK' if okr else 'FAIL(지평이 낮아졌다)'}")
        print(f"  ⇒ {'OK — 지평 폐합 유지 또는 개선' if ok else 'FAIL: ' + str(bad)}")
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
        sites={},                  # [W3 S09 row (4)] the `patch` site list went with the row
        overrides=dict(
            pave=dict(step_x=float(g["joint_step"]),
                      step_y=float(g["joint_step"])),
            # [W3 S09 row (4)] `("patch", 5)` DELETED — see the PARAMS["gkit"] block.
            surface=(("crack", 4), ("stain", ("water",))),
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

    # === [W3 CB-1 · S09-A] three diagnostic side cuts =======================
    #   w3_execution_spec_v1.md Sec.10.5 "S09-A three diagnostic cuts".
    #   Why they exist: **not one of the five existing mise-en-scene cuts crosses the
    #   flight axis** — ghat_walk / waterline / from_river / across_river all look
    #   along or head-on to +-X, and park_vista is framed on the pavilion. At those
    #   ranges the 140-200 mm risers on a 10 m-wide flight foreshorten into a flat
    #   masonry wall (pt_noon_across_river.png reads as a plain revetment with faint
    #   horizontal courses), which is the whole reason the stair cannot be judged.
    #
    #   These are **mise-en-scene registry entries only**. They are appended AFTER
    #   park_vista, so the first 14 entries of `views` keep their identity and their
    #   order: the 9 `sc.grid_views` presets stay byte-identical and the judgement
    #   baseline is untouched. No preset height/distance/pitch is read or written here.
    #
    #   Lighting constraint (derived, not assumed): SUN_AZ_OFFSET = 0.0 with
    #   hdri_sun_rotz_offset = 233.5; measured in pt_noon_across_river.png the mooring
    #   /pile shadows fall toward +Y, so **the sun is on the -Y side**. A flank camera
    #   must therefore sit at **+X and -Y** to keep both the risers and the flank
    #   front-lit — which is what stair_flank_raking and landing_return do.
    #
    #   Geometry the bearings are derived from (recomputed from compute_steps(), all
    #   [computed]): 36 risers, tread 0.34, landings at step 12 (x 3.74..4.94,
    #   top z -2.040) and step 24 (x 8.68..9.88, top z -4.080); bottom step top
    #   z -6.120 at x 13.96; water surface **z = -5.190** (= 6th-from-bottom step top
    #   -5.240 + water_extra 0.05) starting at x = 11.92.
    #   NOTE: w3_execution_spec_v1 Sec.10.5 and w3_intake_06_10 S09-B both quote the
    #   waterline as "-5.240" — that is the *step top face*, not the water surface;
    #   the surface this scene actually builds is **-5.190** (the water covers that
    #   tread by 50 mm). Confirmed independently by WP-T3 on a real usd-core stage
    #   (`Docs/reports/w3_geom_reverify_v1.md`, commit e0fdee4). It changes none of
    #   the three cuts, which are literal coordinates — only the derived note below.

    # (1) PRIMARY. Bearing 130.8 deg, pitch -5.5 deg, range 14.60 m [computed].
    #   Eye is over the water (water starts at x 11.92) at z -2.20 = **2.99 m above
    #   the surface (-5.190)** — a boat / mast height, not a drone shot.
    #   Delivers the whole 36-riser stack in raking profile against the water, both
    #   landings visible as breaks in the riser rhythm, and the waterline cutting the
    #   flight. Front-lit: eye is at +X / -Y, the sun side.
    views["stair_flank_raking"] = dict(eye=[15.00, -11.00, -2.20],
                                       tgt=[5.50, 0.00, -3.60])
    # (2) The concealment case, without touching a preset. Eye stands on **step 4**
    #   (0-based index 3, x 1.02..1.36, top z -0.680) at z 0.55 = **1.23 m above that
    #   tread** [computed], 0.4 m in from the north flight edge (y 4.60 vs y1 5.0),
    #   looking straight down the flight (+X, target y identical so the axis is pure).
    #   By construction the risers face **away** from the camera — this is the same
    #   read the h0.3 grid presets test, and the question it answers is whether the
    #   nosing line collapses into a single plane.
    views["stair_flank_grazing"] = dict(eye=[1.20, 4.60, 0.55],
                                        tgt=[11.00, 4.60, -4.60])
    # (3) Cross-flight close-up on **landing 1** (x 3.74..4.94, top z -2.040).
    #   Bearing 90 deg (+Y), pitch -14.7 deg, range 9.10 m [computed]. Shows the
    #   1.20 m landing tread against the 0.34 m steps, the flank / cheek condition and
    #   the terrace junction. Front-lit from the south (-Y).
    #   Occlusion check against the embankment (PARAMS["embankment"], scene09:184-188):
    #   the embankment is a **stepped extension on the same step table**, so at
    #   x = 4.34 the surface at y = -8.20 is the same z = -2.040 as the landing, i.e.
    #   there is no side *slope* to occlude. The ray from z +0.20 to z -2.10 passes
    #   z = -0.636 at the y = -5.0 flight seam, **1.40 m clear** of that surface [computed].
    #   The eye at z +0.20 is 2.24 m above it.
    #   [W3 CB-1 · S09-C dependency] the ray is at constant x = 4.34, which is exactly
    #   the landing-1 x centre the old `land_posts` stood on: the post at (4.34, -5.6)
    #   used to span z -2.040..+0.060 directly on this sight line and would have
    #   blocked the cut outright. S09-C moves those posts to the terrace, which is why
    #   the two rows ship in the same commit.
    views["landing_return"] = dict(eye=[4.34, -8.20, 0.20],
                                   tgt=[4.34, 0.60, -2.10])

    # === [W3 S09] `g9_oblique` — the cut the target image is judged against ==
    #   G9 is an **aerial oblique**: terraced beds and the boardwalk on the left, the stone step
    #   courses and the pavilion through the centre, water and the autumn far shore filling the
    #   right. `park_vista` already looks down that axis (its own note has the boardwalk at −25°
    #   left, the stair head at −2° centre, the waterline at +12° right) but it stands at z 3.8
    #   and frames the pavilion, so the beds and the boardwalk's turns fall outside it.
    #   This cut keeps the axis (bearing **−51.9°**, against park_vista's −57.2°) and lifts the
    #   eye to 13.0 m — the height at which G9 was drawn — so the renovation can be compared with
    #   the image element for element instead of by assertion.
    #   Back-computation, FOV ±30° horizontal / ±18° vertical, sight-line pitch −15.5°
    #   → frame bearing offsets [−30, +30], frame elevation [−33.5°, +2.5°] (all [computed]):
    #     bed B5 (−11.2, 15.8)   −14.6°  22.0 m   elev −28.6°   → left foreground, terraced
    #     bed B4 (−5.3, 15.8)     −2.1°  25.0 m                 → left of centre
    #     bed B1 (−5.3, −7.6)    −19.5°  46.0 m                 → left, the +X wall face
    #     bed B2 (−11.2, −7.6)   −26.7°                          → left edge
    #     boardwalk L3 axis      −21.6°  49.2 m                 → the leading line, with its turn
    #     pavilion (−4.2, 8.8)    −8.0°  31.5 m                 → centre-left
    #     stair head (0, 0)       −9.0°  41.2 m   elev −17.5°   → centre, the 36 courses in plan
    #     waterline (11.92, 0)    +3.5°  48.1 m   elev −20.8°   → centre-right
    #     duck boat (15.4, 3.0)   +8.9°                          → right
    #     far bank near edge      +22.5° 73.4 m                 → right
    #     autumn ridge 0          +19.6° 115.9 m  elev −2.3°    → top right, closing the horizon
    #   **Mise-en-scene registry only** — appended after the S09-A cuts, so the 9 `sc.grid_views`
    #   presets keep their identity and their order and the judgement baseline is untouched
    #   (the S09-A precedent, `w3_execution_spec_v1.md` Sec.10.5, applied again).
    views["g9_oblique"] = dict(eye=[-20.0, 36.0, 13.0], tgt=[9.0, -1.0, 0.0])
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
                   물때(수위선)·이끼 밴드 대비는 그대로인가(대비비 보존)
12. [W3 S09-A] 진단 3컷 — 기존 5개 연출컷 중 **비행 축을 가로지르는 컷이 하나도 없었다**.
    stair_flank_raking  — 36단 스택이 레이킹 프로파일로 서는가.
                          중간 참 2개가 리듬의 끊김으로 보이고, 수면이 계단을 자르는가
    stair_flank_grazing — 계단 4번째 단 위(트레드 +1.23 m)에서 내려다볼 때
                          디딤코 선이 한 평면으로 뭉개지는가(은폐 케이스)
    landing_return      — 1.20 m 참 트레드가 0.34 m 단들과 대비되어 읽히는가.
                          측벽(cheek)·테라스 접합부가 보이는가
    ※ 프리셋 13컷은 손대지 않았다 — 판정 베이스라인 불변
13. [W3 S09-C] 석주 위치 — 계단면(리벳먼트) 중턱에 박혀 있던 석주 4본이
                   테라스 산책로 가장자리(x −0.80, z 0.0)의 **한 높이**로 올라왔는가.
                   계선주는 배를 매는 안벽 상단에 서지, 계단 경사면에 서지 않는다
14. [W3 S09 · G9] 목표 이미지 대조 — `g9_oblique` 한 컷에서 아래가 동시에 읽히나
    (1) 자연석 계단식 화단 5단 — 켜(course)가 층지고 **세로 줄눈이 이어지지 않는가**
    (2) 화단마다 **한 종**의 지피가 덩어리로 차 있는가 (혼식 0)
    (3) 지그재그 데크 — 두 번 꺾이고, 널이 **진행 방향과 직교**하며,
        장선·멍에·기둥이 레이킹 각에서 분리되어 보이는가
    (4) 가을 — 갈대가 짚빛 + 이삭, 원경 능선이 단풍/은행 색으로 지평을 닫는가
        (건물 실루엣 2동은 삭제됐다 — G9 에 건물은 한 채도 없다)
    (5) 판정 프리셋 13컷의 근경은 **아무것도 바뀌지 않았는가**
        (신설 요소 전부 ±30° 밖 — `fov_selfcheck`)"""


def main():
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # [v7] pure-Python self-checks that run without booting (roof normals · §4 albedo cap).
    #   NEGOBS_SELFCHECK=1 python scene09_ghat_riverfront.py
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        ok1, _ = roof_normal_selfcheck()
        ok2, _ = albedo_selfcheck()
        # [W3 S09] the three gates this renovation adds — season (R09-1), preset-FOV exclusion
        #   (the placement law of every added element) and horizon closure (row (6)'s premise).
        ok3, _ = season_audit()
        ok4, _ = fov_selfcheck()
        ok5, _ = horizon_selfcheck()
        sys.exit(0 if (ok1 and ok2 and ok3 and ok4 and ok5) else 1)

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
        # [W3 S09 row (3)] the members under the walking face are a shade darker — see the
        #   `joist_tint` / `post_tint` comments. Same texture, so this is a tone step, not a
        #   second material family.
        M["joist"] = tex("wood_dark", "/World/Looks/Joist", sca["wood_dark"],
                         tint=mp["joist_tint"])
        M["deck_post"] = tex("wood_dark", "/World/Looks/DeckPost",
                             sca["wood_dark"], tint=mp["post_tint"])
        # [W3 S09 row (1)] dry-stone 자연석 — the granite texture at a warmer, darker tint.
        M["drystone"] = tex("plaza_light", "/World/Looks/DryStone",
                            sca["stone"] * 0.55, tint=mp["drystone_tint"])
        M["drystone_cap"] = tex("plaza_light", "/World/Looks/DryStoneCap",
                                sca["stone"] * 0.55,
                                tint=mp["drystone_cap_tint"])
        # [W2 fix batch F1] Ground-class decal materials for the kit — see the
        #   `scripts/const_color_audit.py` rule: a *ground* prim may not carry a
        #   texture-less constant. paint / metal / water / misc are excluded from
        #   `_CONST_MDL_CLASSES` by design, so binding a kit crack or stain to one
        #   left it as a dead flat ribbon.
        M["gk_crack"] = sc.make_pbr(stage, "/World/Looks/GKitCrack",
                                    diffuse_color=(0.055, 0.055, 0.056),
                                    roughness_const=0.92)
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
        # [W3 S09] reed plume (buff seed head) + lily pad + the three autumn ridge tones.
        #   `far` (the retired building silhouette material) is deleted with row (6).
        M["reed_plume"] = sc.make_pbr(stage, "/World/Looks/ReedPlume",
                                      diffuse_color=mp["reed_plume_color"],
                                      roughness_const=mp["reed_plume_rough"],
                                      specular_level=0.0)
        M["lily"] = sc.make_pbr(stage, "/World/Looks/Lily",
                                diffuse_color=mp["lily_color"],
                                roughness_const=mp["lily_rough"],
                                specular_level=0.0)
        for _k in ("hill_a", "hill_b", "hill_c"):
            M[_k] = sc.make_pbr(stage, f"/World/Looks/Hill{_k[-1].upper()}",
                                diffuse_color=mp[_k],
                                roughness_const=mp["hill_rough"],
                                specular_level=0.0)
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
        M2.update(joint=M["stain"], crack=M["gk_crack"], patch=M["stone"],
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
        # [W3 S09 · row (7)] **belt species declared.** `SCENE_SPECIES["Scene09"]` is
        #   `("birch", "oak_black")` and the belt half has been inert since K4(b) landed —
        #   `resolve_species` only reaches it when a call passes `belt=True`, and no scene09
        #   call did (**K4-F4**: the belts registered for 03 / 09 / 17 "stay inert until you
        #   pass species="). The far-bank stand is exactly what a belt is for: a *different*
        #   species at a distance where its crown cannot roof the walked corridor
        #   (`sc.TREE_BANDS["belt"]`, d_min 7.50 — this row is 44 m away across water).
        #   The route trees on the terrace keep the scene default (`birch`), so the two bands
        #   are now genuinely two species instead of one repeated.
        for i, t in enumerate(PARAMS["far_trees"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", t["cx"], t["cy"], fb_z,
                          M["wood"], M["canopy_a"], M["canopy_b"], belt=True)
        # [W3 S09 · row (6)] the 2 building silhouettes are gone; the autumn ridges close the
        #   horizon in their place. `horizon_selfcheck()` proves the closure did not get lower.
        build_far_hills(M)

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
            # [W3 S09] a route tree standing **inside** a terraced bed is planted in that bed,
            #   not floating over it: its ground z is the bed's soil surface. Without this the
            #   tree at (−13.4, 17.2) — inside B5 — would be buried to 0.88 m of its trunk.
            #   Species stays the scene default (`birch`); only the far-bank belt is declared.
            sc.build_tree(stage, f"{ROOT}/ParkTree_{i}", tx, ty,
                          _bed_top_at(tx, ty, pr),
                          M["wood"], M["canopy_a"], M["canopy_b"])

    def build_deck(M):
        """[W3 S09 · row (3)] **Zigzag timber boardwalk** — replaces the v5/v6 straight slab.

        Three legs, two right-angle turns, net progress toward the water (see the
        `PARAMS["boardwalk"]` block for the coordinates and the reason each one is where it is).
        The walked surface is **unchanged**: `top_z` is still 0.060.

        Members, all **stocked 방부목 sections** on the scene10 precedent (산림청고시 2014-2 제8조
        fixes the 데크판재 thickness series 21/24/27/30 mm and the width series 90–300 mm in 10 mm
        steps; a 0.145 m plank is a KCS specification width, not a retail size):
          plank  25 x 140 laid **across** the leg, 6 mm gap  — the walking face
          joist  38 x 140 on edge at 0.45 m pitch            — under the planks, spanning the width
          beam   90 x 90 continuous under the joists          — the 멍에
          post   120 x 120 at 2.70 m                          — the 기둥, down to grade
          rim    25 x 140 on the two free edges               — the 마구리 board
        A plank runs across the leg because that is how a boardwalk is built (planks span joists,
        joists span beams); the old element ran its seams **along** its own long axis, which is
        the one direction a plank never runs.
        Turn corners are solid: consecutive legs overlap by a full leg width, so the plank runs
        simply butt into each other and no seam opens at a corner.
        """
        bw = PARAMS["boardwalk"]
        tz = float(bw["top_z"])
        pw, pt = bw["plank"]
        pg = float(bw["plank_gap"])
        jw, jd = bw["joist"]
        bm, po = float(bw["beam"]), float(bw["post"])
        rw, rd = bw["rim"]
        z_plank = tz - pt / 2.0                       # plank body
        z_joist = tz - pt - jd / 2.0                  # joists hang under the planks
        z_beam = tz - pt - jd - bm / 2.0
        pitch = pw + pg                               # 0.146 m plank period
        n_plank = n_joist = n_post = 0
        for tag, x0, y0, x1, y1, axis in bw["legs"]:
            P = f"{ROOT}/Boardwalk/{tag}"
            lo, hi = (x0, x1) if axis == "x" else (y0, y1)
            run = hi - lo
            # --- planks, across the leg -------------------------------------
            n = max(1, int(math.floor(run / pitch)))
            off = (run - (n * pitch - pg)) / 2.0      # centre the run in the leg
            for k in range(n):
                c = lo + off + pw / 2.0 + k * pitch
                if axis == "x":
                    ctr, size = (c, (y0 + y1) / 2.0, z_plank), (pw, y1 - y0, pt)
                else:
                    ctr, size = ((x0 + x1) / 2.0, c, z_plank), (x1 - x0, pw, pt)
                sc.add_box(stage, f"{P}/Plank_{k}", ctr, size, M["deck"],
                           collider=(k % 6 == 0))
                n_plank += 1
            # --- joists, along the leg ---------------------------------------
            cross_lo, cross_hi = (y0, y1) if axis == "x" else (x0, x1)
            nj = max(2, int(round((cross_hi - cross_lo) / bw["joist_pitch"])))
            for k in range(nj + 1):
                c = cross_lo + (cross_hi - cross_lo) * k / float(nj)
                if axis == "x":
                    ctr, size = ((x0 + x1) / 2.0, c, z_joist), (run, jw, jd)
                else:
                    ctr, size = (c, (y0 + y1) / 2.0, z_joist), (jw, run, jd)
                sc.add_box(stage, f"{P}/Joist_{k}", ctr, size, M["joist"])
                n_joist += 1
            # --- beams + posts ------------------------------------------------
            npst = max(2, int(round(run / bw["post_pitch"])))
            for s, cc in ((0, cross_lo + bm), (1, cross_hi - bm)):
                if axis == "x":
                    sc.add_box(stage, f"{P}/Beam_{s}",
                               ((x0 + x1) / 2.0, cc, z_beam), (run, bm, bm),
                               M["deck_post"])
                else:
                    sc.add_box(stage, f"{P}/Beam_{s}",
                               (cc, (y0 + y1) / 2.0, z_beam), (bm, run, bm),
                               M["deck_post"])
                for k in range(npst + 1):
                    c = lo + run * k / float(npst)
                    px, py = (c, cc) if axis == "x" else (cc, c)
                    hpost = z_beam - bm / 2.0 + 0.30      # 0.30 m into grade
                    sc.add_box(stage, f"{P}/Post_{s}_{k}",
                               (px, py, (z_beam - bm / 2.0) - hpost / 2.0),
                               (po, po, hpost), M["deck_post"], collider=True)
                    n_post += 1
            # --- rim board on the two free edges -------------------------------
            for s, cc in ((0, cross_lo + rw / 2.0), (1, cross_hi - rw / 2.0)):
                if axis == "x":
                    ctr, size = ((x0 + x1) / 2.0, cc, tz - rd / 2.0), (run, rw, rd)
                else:
                    ctr, size = (cc, (y0 + y1) / 2.0, tz - rd / 2.0), (rw, run, rd)
                sc.add_box(stage, f"{P}/Rim_{s}", ctr, size, M["joist"])
        print(f"[보드워크] 지그재그 3구간 2회 꺾임 · 널 {n_plank} · 장선 {n_joist} "
              f"· 기둥 {n_post} · 상면 z {tz:.3f}(불변)")

    # -------------------------------------------------------------------
    # [W3 S09 · rows (1)(2)] terraced beds + dry-stone 자연석 retaining walls
    # -------------------------------------------------------------------
    def _drystone_face(M, path, ax, const, lo, hi, z0, z1, seed):
        """One coursed dry-stone face. `ax` is the face normal ('+x','-x','+y','-y'); the face
        plane sits at `const` and the wall runs from `lo` to `hi` along the other horizontal axis.

        Courses are laid bottom-up. Within a course the block lengths are drawn from
        [block_lo, block_hi] so **no vertical joint continues** into the course above — that
        discontinuity is the single cue that separates 자연석 건식쌓기 from a block wall. Each
        block's **depth** is drawn from `depth +- depth_var` with its bedding face pinned to the
        wall plane (size variation, not placement jitter — see the LINT-10 adjudication in
        `PARAMS["drystone"]`), and the whole face leans back with the dry-laid `batter` (1:6), so
        the courses catch light one at a time instead of reading as one flat plane.
        Blocks are dressing (`collider=False`) — the bed core behind them carries the collision.
        """
        ds = PARAMS["drystone"]
        rs = np.random.RandomState(int(seed) & 0x7FFFFFFF)
        sgn = 1.0 if ax in ("+x", "+y") else -1.0
        along_x = ax in ("+y", "-y")
        ch = ds["course_h"]
        nc = max(1, int(round((z1 - z0) / ch)))
        ch = (z1 - z0) / nc
        n = 0
        for c in range(nc):
            zc = z0 + (c + 0.5) * ch
            # batter: each course above the base steps back from the face plane
            back = ds["batter"] * (zc - z0)
            u = lo
            k = 0
            while u < hi - 0.05:
                L = float(rs.uniform(ds["block_lo"], ds["block_hi"]))
                L = min(L, hi - u)
                d = ds["depth"] + float(rs.uniform(-ds["depth_var"],
                                                    ds["depth_var"]))
                cu = u + L / 2.0
                cf = const - sgn * (back + d / 2.0)
                if along_x:
                    ctr = (cu, cf, zc)
                    size = (max(L - ds["gap"], 0.08), d, ch - ds["gap"])
                else:
                    ctr = (cf, cu, zc)
                    size = (d, max(L - ds["gap"], 0.08), ch - ds["gap"])
                sc.add_box(stage, f"{path}/C{c}_{k}", ctr, size, M["drystone"])
                u += L
                k += 1
                n += 1
        # coping course (갓돌) — one continuous flatter band that reads as the wall head
        back = ds["batter"] * (z1 - z0)
        d = 0.30
        cf = const - sgn * (back + d / 2.0)
        if along_x:
            ctr = ((lo + hi) / 2.0, cf, z1 + ds["cap_h"] / 2.0)
            size = (hi - lo, d, ds["cap_h"])
        else:
            ctr = (cf, (lo + hi) / 2.0, z1 + ds["cap_h"] / 2.0)
            size = (d, hi - lo, ds["cap_h"])
        sc.add_box(stage, f"{path}/Cap", ctr, size, M["drystone_cap"])
        return n + 1

    def _tag_seed(tag):
        """Stable per-bed seed offset. **Not `hash()`** — CPython randomises `hash(str)` per
        process (PEP 456 / `PYTHONHASHSEED`), so seeding a wall off it would make the scene
        emit a different stone layout on every run and break the prim-hash reproducibility
        `geom_invariance_check` and every regression baseline depend on. Caught here before it
        shipped; the sum of code points is deterministic for all time."""
        return sum(ord(c) for c in str(tag)) % 89

    def _bed_at(tag):
        for b in PARAMS["beds"]:
            if b["tag"] == tag:
                return b
        return None

    def _bed_top_at(x, y, default=0.0):
        """Soil-surface z at (x, y) if it falls inside a terraced bed, else `default`.
        The beds do not overlap, so the first hit is the answer."""
        for b in PARAMS["beds"]:
            if b["x0"] <= x <= b["x1"] and b["y0"] <= y <= b["y1"]:
                return float(b["top"]) - 0.12          # soil_drop
        return float(default)

    def build_beds(M):
        """[W3 S09 · rows (1)(2)] The terraced planting beds — G9's left half.

        Each bed is one solid core (the planting mass, collider — this is what a body collides
        with) plus a coursed dry-stone facing on its **exposed** faces only. Which faces are
        exposed is declared per bed rather than derived, because the derivation would be wrong:
        B2 stands behind B1, so B2's +X face is exposed **only above B1's top** — the facing is
        cut to that band and no block is built where nothing can see it.
        The soil surface sits `soil_drop` below the wall head so the bed reads as a container
        holding a mass, not as a slab with plants glued on top.
        """
        ds = PARAMS["drystone"]
        soil_drop = 0.12
        tops = {b["tag"]: b["top"] for b in PARAMS["beds"]}
        n_block = 0
        for b in PARAMS["beds"]:
            B = f"{ROOT}/Bed_{b['tag']}"
            top = float(b["top"])
            # core: the retained planting mass. Top face `soil_drop` below the wall head.
            sc.add_box(stage, f"{B}/Core",
                       ((b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0,
                        (top - soil_drop) / 2.0),
                       (b["x1"] - b["x0"], b["y1"] - b["y0"], top - soil_drop),
                       M["grass"], collider=True)
            for fi, face in enumerate(b["faces"]):
                # the exposed band: from the top of whatever stands in front, to this wall head
                z0 = 0.0
                if face == "+x":
                    front = [t for tg, t in tops.items()
                             if tg != b["tag"] and t < top]
                    # a bed directly in front (larger x0, same y band) hides the lower part
                    for ob in PARAMS["beds"]:
                        if (ob["tag"] != b["tag"] and ob["x0"] >= b["x1"] - 1e-6
                                and not (ob["y1"] <= b["y0"] or ob["y0"] >= b["y1"])):
                            z0 = max(z0, ob["top"])
                    _ = front
                    n_block += _drystone_face(
                        M, f"{B}/Wall{fi}", "+x", b["x1"], b["y0"], b["y1"],
                        z0, top, ds["seed"] + 7 * fi + _tag_seed(b["tag"]))
                else:
                    const = b["y0"] if face == "-y" else b["y1"]
                    n_block += _drystone_face(
                        M, f"{B}/Wall{fi}", face, const, b["x0"], b["x1"],
                        0.0, top, ds["seed"] + 11 * fi + _tag_seed(b["tag"]))
        print(f"[화단] 계단식 {len(PARAMS['beds'])}단 · 자연석 블록 {n_block}")
        return n_block

    def build_bed_planting():
        """[W3 S09 · row (2)] Massed ground cover, **one species per bed**.

        `pool=[<one asset>]` makes the bed monospecific *by construction*: `place_shrubs` filters
        `VEG_SHRUBS` by the pool and then draws one row for the whole bed (K4(b) · S-2), so a
        one-member pool removes the draw entirely and the record is exact. The species come from
        `season_audit()`'s measured verdicts.
        Points are an irregular lattice — a jittered grid at ~0.9 m, then culled to `n` — because
        a planting bed is planted on a spacing, not scattered, but never on a visible grid.
        """
        placed = 0
        soil_drop = 0.12
        for b in PARAMS["beds"]:
            rs = np.random.RandomState(int(b["seed"]))
            x0, y0 = b["x0"] + 0.55, b["y0"] + 0.55
            x1, y1 = b["x1"] - 0.55, b["y1"] - 0.55
            nx = max(1, int(round((x1 - x0) / 0.95)) + 1)
            ny = max(1, int(round((y1 - y0) / 0.95)) + 1)
            pts = []
            for i in range(nx):
                for j in range(ny):
                    px = x0 + (x1 - x0) * i / max(nx - 1, 1)
                    py = y0 + (y1 - y0) * j / max(ny - 1, 1)
                    pts.append((px + float(rs.uniform(-0.26, 0.26)),
                                py + float(rs.uniform(-0.26, 0.26)),
                                float(b["top"]) - soil_drop))
            rs.shuffle(pts)
            pts = pts[:int(b["n"])]
            placed += sc.place_shrubs(
                stage, f"{ROOT}/Bed_{b['tag']}/Mass", pts, float(b["h"]),
                pool=[b["species"]], seed=int(b["seed"]), tag="Sh")
        print(f"[화단 군식] 관목 {placed}본 · 화단당 1종(pool 1개 = 구조적 단일종)")
        return placed

    def build_bed_features():
        """[W3 S09] G9's root/stump feature and the boulders in the beds, through the **T4b
        wrapper** — `treatment="mtlxoff"` + `instanceable=True`. This is the only route that
        combines instancing with a working material on `rock_moss_set_01`: the asset binds a
        MaterialX material whose `ND_normalmap_float` is missing from this runtime's Sdr registry
        (**MD-F3**), and a scene-side bind cannot reach inside a prototype (`w3_t4b_v1.md` §1.2).
        Failure is non-fatal: an unprocured urban tree must not cost the scene its beds."""
        try:
            import urban_kit as uk
        except Exception as e:
            print(f"[urban][경고] urban_kit 로드 실패 — 화단 특징물 생략: {e}")
            return 0
        soil_drop = 0.12
        n = 0
        for i, (aid, tag, u, v, th, yaw) in enumerate(PARAMS["bed_features"]):
            b = _bed_at(tag)
            if b is None:
                continue
            px = b["x0"] + (b["x1"] - b["x0"]) * float(u)
            py = b["y0"] + (b["y1"] - b["y0"]) * float(v)
            pz = float(b["top"]) - soil_drop
            try:
                # `z_mode="base"` + a 0.10 m bed. Measured live on this run, the default
                #   `grade` mode buries these rows: `tree_stump_01` carries **38.9 %** of its
                #   triangles below its own origin (zmin −0.193 m) and `rock_moss_set_01`
                #   **52.4 %** (zmin −0.661 m) — urban_kit prints both warnings and tells the
                #   caller exactly this. A boulder set in a planting bed is bedded a hand's
                #   depth, not sunk to its waist, and G9's root feature sits **on** its moss bed.
                uk.add_urban_asset(stage, f"{ROOT}/Bed_{tag}/Feat_{i}", aid,
                                   pos_m=(px, py, pz - 0.10), yaw_deg=float(yaw),
                                   target_h=float(th), scene="09", z_mode="base",
                                   instanceable=True, treatment="mtlxoff")
                n += 1
            except Exception as e:
                print(f"[urban][경고] {aid} 배치 실패({tag}): {e}")
        print(f"[화단 특징물] 그루터기/이끼바위 {n}점 (T4b mtlxoff 래퍼 · instanceable)")
        return n

    def build_far_hills(M):
        """[W3 S09 · row (6)] The autumn hillside belt that replaces the 2 building silhouettes.

        Each ridge is a low body box plus a row of overlapping flattened ellipsoids — the same
        device `sc.build_hedge`'s crown uses, at landscape scale. Deterministic per ridge.
        `horizon_selfcheck()` asserts these close the horizon at least as high as the boxes did.
        """
        hp = PARAMS["hill"]
        _steps, _bz, _zb, water_z, _bh = compute_steps()
        fb = PARAMS["far_bank"]
        base = water_z + fb["above_water"]
        tone_mtl = (M["hill_a"], M["hill_b"], M["hill_c"])
        for i, h in enumerate(PARAMS["far_hills"]):
            mtl = tone_mtl[int(h["tone"]) % 3]
            body_h = h["h"] * 0.55
            sc.add_box(stage, f"{ROOT}/Hill_{i}/Body",
                       (h["cx"], h["cy"], base + body_h / 2.0),
                       (h["sx"], h["sy"], body_h), mtl)
            rs = np.random.RandomState(int(hp["seed"]) + 13 * i)
            nb = int(hp["blobs"])
            for k in range(nb):
                t = (k + 0.5) / nb
                by = h["cy"] - h["sy"] / 2.0 + h["sy"] * t
                bx = h["cx"] + float(rs.uniform(-1.0, 1.0)) * h["sx"] * 0.18
                # ridge profile: full height at the centre, tapering to the ends
                prof = 0.55 + 0.45 * math.sin(math.pi * t)
                rz = h["h"] * hp["blob_r"] * prof * float(rs.uniform(0.86, 1.14))
                rx = h["sx"] * hp["spread"] * 0.5 * float(rs.uniform(0.82, 1.18))
                ry = h["sy"] / nb * 0.95 * float(rs.uniform(0.88, 1.22))
                sc.add_sphere(stage, f"{ROOT}/Hill_{i}/Crown_{k}",
                              (bx, by, base + body_h * 0.82 + rz * 0.34),
                              (rx, ry, rz), mtl)

    def build_lilies(M):
        """[W3 S09] Lily pads / floating leaf rafts on the still water — G9's right half.
        Thin n-gon discs at the water surface, |y| >= 7.4 so they are nowhere near the flight."""
        lp = PARAMS["lily"]
        n = 0
        for ci, (cx, cy, cnt, rlo, rhi, seed) in enumerate(PARAMS["lilies"]):
            rs = np.random.RandomState(int(seed))
            for k in range(int(cnt)):
                dx = float(rs.uniform(-lp["spread"], lp["spread"]))
                dy = float(rs.uniform(-lp["spread"], lp["spread"]))
                r = float(rs.uniform(rlo, rhi))
                sc.add_disc(stage, f"{ROOT}/Lily_{ci}_{k}",
                            (cx + dx, cy + dy, water_z + lp["t"] / 2.0), r,
                            lp["t"], M["lily"], seg=9)
                n += 1
        print(f"[수생] 수련 잎 {n}장 (수면 z {water_z:.3f})")

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
                ry = t * math.cos(math.radians(a))
                rx = t * math.sin(math.radians(a))
                sc.add_cylinder(
                    stage, f"{ROOT}/Reed_{ci}_{k}",
                    (cx + dx, cy + dy, gz + hh / 2.0), rd["r"], hh, M["reed"],
                    rotY=ry, rotX=rx)
                # [W3 S09 · R09-1] the buff seed head. An autumn 갈대 bed is read by its
                #   plumes, not by its culms; without them a straw-tinted stem row just
                #   looks like dead grass. Seated at the culm top and following its tilt —
                #   `add_cylinder` rotates about the prim centre, so the top of a stem tilted
                #   by (rx, ry) has moved, and the plume centre is placed on that same axis.
                ph = rd["plume_h"]
                d_up = hh / 2.0 + ph / 2.0
                sr, sy_ = math.radians(ry), math.radians(rx)
                sc.add_cylinder(
                    stage, f"{ROOT}/ReedPlume_{ci}_{k}",
                    (cx + dx + d_up * math.sin(sr),
                     cy + dy - d_up * math.sin(sy_),
                     gz + hh / 2.0 + d_up * math.cos(sr) * math.cos(sy_)),
                    rd["r"] * rd["plume_r_mul"], ph, M["reed_plume"],
                    rotY=ry, rotX=rx)

    def build_signs():
        """[v5 shared layer / W3 S09] Korean information **lectern** (안내 거치대).

        G9 carries exactly one, and it is a lectern, not a post-and-panel sign: a raked panel on
        a low plinth, read from above by someone standing at it. `sc.build_sign` builds the
        post-and-panel form, so the lectern is assembled here from the same panel material —
        plinth (a stone body on two legs) + a `rotX`-raked panel at `panel_tilt` — and the panel
        texture role is unchanged, so nothing downstream of `sign_info` moves.
        """
        lc = PARAMS["lectern"]
        body = sc.make_pbr(stage, "/World/Looks/LecternBody",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            P = f"{ROOT}/Sign_{tag}"
            px, py, pz = lc["plinth"]
            grp = sc.build_rot_group(stage, P, (cx, cy), yaw)
            # two legs + the plinth head
            for s, dy in (("L", -py * 0.62), ("R", py * 0.62)):
                sc.add_cylinder(stage, f"{grp}/Leg_{s}",
                                (cx, cy + dy, bz + (pz - 0.10) / 2.0),
                                lc["leg_r"], pz - 0.10, body, collider=True)
            sc.add_box(stage, f"{grp}/Head",
                       (cx, cy, bz + pz - 0.05), (px, w + 0.10, 0.10), body)
            # The raked panel. `_oriented_box` applies scale -> rotX -> rotZ -> translate, so the
            #   box is authored **standing** (X = width, Y = thickness, Z = height) and rotX
            #   `panel_tilt` leans its top back by that angle from vertical. Its centre is lifted
            #   by half the *projected* height so the panel foot sits on the plinth head.
            tilt = float(lc["panel_tilt"])
            hh = float(h)
            sc._oriented_box(
                stage, f"{grp}/Panel",
                (cx, cy, bz + pz + hh * math.cos(math.radians(tilt)) / 2.0),
                (float(w), lc["panel_t"], hh), panel, rotx=tilt)

    def build_dressing(M):
        """[v5 adopted / v6 rework / W3 S09] Lake park dressing — 6 waterfront boundary piles +
        **1 timber samojeong** + 4 terrace stone posts + 4 benches + **1 duck boat (curved)** +
        **5 terraced beds in dry-stone 자연석** + **a zigzag timber boardwalk** + 2 lawn bands +
        10 street trees + 10 reed stands with plumes + 4 lily rafts.
        [v6 §6 emptying] the 2 planters are deleted — the street trees on the lawn bands take over that role.
        All outside the stair width (y±5) or on the terrace → hazard geometry unchanged, and
        every element **W3 S09** adds is additionally asserted outside the ±30° FOV of all nine
        grid presets by `fov_selfcheck()`."""
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
        build_beds(M)                        # [W3 S09 (1)] 자연석 계단식 화단 — G9's left half
        build_lawns(M)                       # [v6 (3)] lawn bands + street trees
        build_deck(M)                        # [W3 S09 (3)] zigzag boardwalk
        build_bed_planting()                 # [W3 S09 (2)] one species per bed
        build_bed_features()                 # [W3 S09] stump / moss boulders via T4b wrapper
        build_reeds(M)
        build_lilies(M)                      # [W3 S09] lily pads on the still water
        # 4 stone posts on the terrace promenade edge.
        #   [W3 CB-1 · S09-C] was: two per landing at the landing x centre, standing on
        #   the revetment at the landing top z. Now: one line at x = -0.80, z base 0.0,
        #   four y stations — see the PARAMS["land_posts"] block for the derivation.
        #   The prim names are kept as LandPost_* for continuity with the judgement files.
        lp = PARAMS["land_posts"]
        for pi, yy in enumerate(lp["ys"]):
            sc.add_cylinder(stage, f"{ROOT}/LandPost_{pi}",
                            (lp["x"], yy, lp["z"] + lp["h"] / 2.0),
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
        # [W3 S09] season / FOV / horizon gates, in the smoke run too — the S1–S8 obligation
        #   (spec §6.2) is that the scene's own self-check passes **after** the edit.
        _s_ok, _ = season_audit()
        _f_ok, _ = fov_selfcheck()
        _h_ok, _ = horizon_selfcheck()
        print(f"[W3 S09] 계절 {'OK' if _s_ok else 'FAIL'} · "
              f"FOV 배제 {'OK' if _f_ok else 'FAIL'} · "
              f"지평 폐합 {'OK' if _h_ok else 'FAIL'}")
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
            # [W3 S09 · S09-F2] **the v8 probe was reading the wrong input names.** With
            #   `NEGOBS_LOOK_V1=1` (i.e. `LOOK_MTL` on — the channel every judged round uses),
            #   `sc.make_pbr` routes a constant-colour material in a `_CONST_MDL_CLASSES` role
            #   through `_make_ground_pbr` (`scene_common.py:1295-1319`), and that factory names
            #   its inputs **`..._a`** (`:1551` `specular_level_a`, `:1520` `base_color_a`). The
            #   v8 probe asked for `specular_level` / `diffuse_color_constant` only, so under the
            #   judged channel it reported **all four inputs "(미지정)" and printed a false FAIL**
            #   on a material that is correctly set — including `diffuse_color_constant`, which is
            #   demonstrably authored. Measured this session, not inferred. The probe now asks for
            #   both spellings and reports which factory actually built the material.
            _PAIRS = (("diffuse_color_constant", "base_color_a"),
                      ("reflection_roughness_constant", "roughness_a"),
                      ("specular_level", "specular_level_a"),
                      ("metallic_constant", "metallic_a"))
            route = "make_pbr(OmniPBR 직결)"
            for a, b in _PAIRS:
                ia, ib = sh.GetInput(a), sh.GetInput(b)
                if ia is not None and ia.Get() is not None:
                    got[a] = ia.Get()
                elif ib is not None and ib.Get() is not None:
                    got[b] = ib.Get()
                    route = "_make_ground_pbr(const-MDL 경유)"
                else:
                    got[a] = "(미지정=MDL 기본값)"
            print(f"  PavRoof MDL 입력 실측  ·  경로 {route}:")
            for nm, val in got.items():
                print(f"    {nm:32s} {val}")
            sl = got.get("specular_level", got.get("specular_level_a"))
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
