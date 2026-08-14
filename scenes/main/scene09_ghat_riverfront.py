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

[W3 P09 · GT-41] The two items the S09 lane **filed and did not take**, taken here after
  `w3_intake_v2_images.md` §7.2 ruled on both. Nothing else in the scene moves.
    (1) **판석 디딤돌 — the stepping stones, un-declined.** §7.2: *"S09 — stepping stones ALLOWED
        as physical 판석 slabs with 3D relief (the user's ban targets decorative rectangle DECALS,
        not real objects; prefer irregular outlines)."* Ten slabs, **irregular 6/7-gon prisms**
        authored as `UsdGeom.Mesh` in-scene, 0.120 m thick, in the −Y lawn band on a 0.57 m stride
        from the lawn edge to the **landward end of boardwalk leg L1** — which until now began in
        the middle of a lawn with no approach at all. Top face **12 mm** above the mown turf,
        **below `ground_kit.GT_DELTA` (0.020)**, `collider=False`: element AABBs add (GT-8 class),
        the hazard/collision box list does not. `stepstone_selfcheck()` asserts all five conditions
        — sub-threshold · irregular · inside the lawn · clear of the deck · clear of the trees —
        from the shipped coordinates, and fails the build otherwise.
    (2) **the stone tone correction.** `w3_s09_v1.md` §7 **P1** measured it and declined to take
        it after its own pilot; §7.2 authorised it — `stone_tint` **0.64 → 0.524** (linear factor
        **0.818**). `stain` · `moss` · `drystone` · `drystone_cap` take the **same** factor, so
        every ratio the file authors survives and the **waterline contrast — this scene's only
        drop anchor — is preserved by construction**, exactly as v7 preserved it at 0.90 → 0.64.
        Material only: **0 prims, 0 geometry**, GT-17's *"render-gate item, not a GT item"* class.
  Still **not** done, and still for the reasons `w3_s09_v1.md` §7 gives: the last two metres of
  boardwalk onto the embankment stone (**P7** — §7.2 *"boardwalk 0.60 m termination ACCEPTED"*) ·
  flowering ground cover (**P2**, no stock asset) · reflective water (**P4**) · a real `PLACEMENT`
  block (**P5**) · the ridge-crown device (**P3**).

[GT-115 ⑨] 260806_w3_allview5 audit batch — seven rows, all measured off the shipped cuts
  (`look_check/scene09/260806_w3_allview5/`). **The hazard rows are untouched**: waterline edge and
  coping, water material (P4), the 36-step flight, the far-shore black-silhouette question and every
  camera stay exactly as they were.
  **The single mechanism behind three of the seven** is the look layer's constant-colour texture
  **promotion** (`scene_common._promote_const_to_texture`) landing on objects the class prescription
  was never sized for. It preserves the texture's *mean*, and it does that by multiplying the bound
  texture per channel by `intended / texture_mean` — so on an object far smaller than the tile the
  multiplier lands on **one unrepresentative texel patch**, not on the mean [measured, this session]:
    · `Looks/Reed` → veg → `grass_lawn` @ 1.4 m tile with base_color **(3.99, 1.85, 5.46)**. A 44 mm
      culm samples 1.5 % of one tile, and the ×5.46 on the grass map's near-empty blue channel is
      exactly the "grey-lilac granite-speckled" amplification `scene_common:591-596` documents for
      scene11's `leaf_far_*`. Measured on `pt_noon_across_river.png`: stems **(183,163,172)** —
      blue **above** green on a material declared (0.232, 0.196, 0.118) warm brown. The plume's
      down-facing cap, lit by sky only and multiplied ×5.46 in blue, is the **navy gap** under
      every seed head. It also squeaked through the class spread cap by 1.7 % (2.95 vs 3.00).
    · `Looks/PavRoof` → the keyword rule reads **"pav"** before it ever reaches "roof", so the
      tiled hip roof classifies **paving** and promotes to `paving_interlock` = the grey
      running-bond blocks in every cut.
    · `Looks/PavFloor` → **paving** for the same reason, so the 누마루 rides the *ground* MDL with a
      concrete detail normal, and its declared tint 0.78/0.60/0.42 on `wood_dark`
      (linear mean 0.081/0.058/0.044) lands at an effective albedo of **0.038 luminance** — under
      the roof's shade that is the measured RGB (4,4,6) black floor.
  The fix for all three is the same and it is the promotion's own intent done honestly: **bind the
  texture explicitly, in a role whose hue is already the declared hue**, so the multiplier is flat
  (spread ≤ 1.27) and no channel can be amplified into a false colour. A literal constant is not
  reachable from a scene file for a `_CONST_MDL_CLASSES` role without abusing `uv_mode`, and a
  constant is the corpus' largest source of dead flat % anyway.
    (1) **reeds** — `wood_dark` @ 0.28 m (a culm is lignified fibre, and the map is *already* brown:
        tint (2.861, 3.403, 2.700), spread **1.26**, product = the declared brown to 4 dp) ·
        seed head rebuilt as a **2-segment spindle** (r 1.9 → 0.85 × culm) seated 45 mm **into** the
        culm, so the flat top and the navy joint gap are both gone by construction.
    (2) **far ridge tone** — `hill_a/b/c` were 0.196–0.245 albedo = the measured band mean **47 %**
        of the pastel blob belt, against the **6–12 %** vegetation reflectance band this file's
        own `wood_color`/canopy note declares and applies to `canopy_a/b`. Levelled
        ×0.55 / ×0.55 / ×0.49 → max channel 0.108 / 0.116 / 0.120.
        `hill_d` (0.078) was already in band and does not move; the aerial-perspective ordering
        GT-86 fixed (d < a < b < c in luminance) is preserved exactly [computed].
    (3) **누마루** — class corrected to `wood` by naming (`PavFloorPlank`, the `Deck`/`Joist`
        precedent in this same file) and the tint re-solved on the texture it actually rides:
        (2.58, 2.83, 2.77) → effective albedo **0.170 luminance**, inside the 0.15–0.25 timber band.
        Side effect, declared: the slab loses its `_ground_skin` (a mineral micro-relief mesh the
        `paving` class was giving a timber floor) — 1 prim, LOOK_GEO arm only.
    (4) **계선주** — bound to `rock_face`, which a survey of the registry this session shows is the
        **only** stone role without a course pattern (plaza_light 6×6 slabs · granite_dark 5×5
        stack bond · stone_worn running bond · sandstone ashlar · marble_light slabs · rock_wall
        riprap) — the posts are monoliths and were wearing the promenade's slab grid — and cut
        from Ø0.48 × H2.1 — a column — to **Ø0.30 × H0.90**, the real Korean quay-post band. No
        self-check reads their size (`fov_selfcheck` does not list them); their collider AABBs
        shrink with them.
    (5) **기와지붕** — `granite_dark` with tint (1.434, 1.512, 1.680), which reproduces the declared
        `roof_tile_color` **exactly**, so `roof_specular_selfcheck`'s predictions and the v8 Y1
        finding stand unchanged; the map's own 5×5 module is *used*, not fought — tile 1.50 m puts
        one cell on **0.30 m** = the 기와 course, which is the thing a staggered pavement bond can
        never be · the ridge box becomes a **절병통** of 5 stacked discs (`add_disc`, 32-gon — the
        analytic `Cylinder` Hydra tessellates coarsely is why it read as a chimney).
    (6) **조경석** — the boulders were bedded a flat 0.10 m regardless of size; they are now sunk a
        declared **fraction of their own height** (rocks 1/3, the stump keeps its shallow 0.08 —
        G9's root feature sits *on* its moss bed).
    (7) **오리배** — a dark seat well (`DuckCockpit`) breaks the smooth yellow mass. Hull, breast,
        stern, wings, neck, head, beak and canopy dimensions are all unchanged.
  **Not done, and why**: the fluorescent magenta shrub band. Its colour is not in this file and
  cannot be reached from it — the carriers are `Shrub/Burning_Bush.usd` (bed B1) and the `sp=2`
  runs of `far_hedges`, and their leaf basecolor has a **measured mean linear albedo of
  (0.490, 0.293, 0.270)** — a 49 % red leaf — bound inside `BurningBush_leaf_Mat.mdl`, which
  `place_shrubs` references as an **instanceable prototype**; a scene-side bind cannot reach into a
  prototype (`w3_t4b_v1.md` §1.2, the same fact that forced the T4b wrapper for the bed boulders).
  Species re-mix / run-splitting **would** cut the band, but that is a planting-design change to a
  backdrop the user has already ruled on twice (GT-63, GT-86), so it is filed, not taken.

[GT-126] 260815_w4_r4batch judgment-cut tone tails (R-2 materials only, 0 prims, 0 geometry).
  Measured on `pt_noon_preset_h0.3_d5` with the `shortcut_audit` metric (display luminance
  > 0.75 / < 0.10): clipHi **56.8 %** / clipLo **14.8 %**. Region split [measured]:
    clipHi — promenade pavers y 0.31-1.0 own **51.6 pp** of the 56.8 (sky 2.2 · far-tree
      leaf sparkle 3.0). clipLo — far-shore tree band y 0.05-0.25 owns **8.8 pp**, the
      shoreline hedge line y 0.25-0.31 **5.0 pp**, far pavers 1.0.
  The bright tail is **not** a binding failure — `from_river` shows the water-mark band at
  its authored hue (R/B 1.20 vs authored 1.196) and at the declared stain/stone ratio
  (0.52 vs 0.476), so the tint family lands. The excess is **exposure**: the judged PT
  noon gain on open horizontal ground measures **2.40-2.46** (paver lin 0.578-0.592 over
  effective 0.241), where the v7 §4 machinery predicts with the RT-era GAIN 1.77. At the
  measured gain the metric's clip line (disp 0.75) sits at effective albedo **0.211 —
  inside the 0.20-0.35 weathered-granite band**, so no in-band stone clears the metric at
  this exposure; what can move is the mean. Landing rule = GT-121 2차 (scene15): reproduce
  its landing display (mean disp 0.725) under this scene's own gain → eff 0.197-0.202,
  taken just inside the band: `stone_tint` **× 0.850** → effective 0.209 (bottom third,
  floor respected), and the same factor to every ratio-authored tint (stain · moss ·
  drystone · drystone_cap · stepstone) so the **waterline contrast — this scene's only
  drop anchor — is preserved by construction** (the v7 / GT-41(2) idiom, third pass).
  Projected on the shipped cut [computed]: paver clipHi 76.5 → 28.5 %, frame ≈ 24 %;
  the residual is exposure-owned (GT-125's PHYS_V1 grazing arm is the next lever, not a
  darker stone). The dark tail is **left**: 13.8 of its 14.8 pp are instanced-foliage
  interiors (FarTree oak / FarHedge shrub prototypes — a scene-side bind cannot reach
  into a prototype, `w3_t4b_v1.md` §1.2, the same fact as the magenta shrub row) plus
  hedge-shadowed far-bank faces whose grass already rides an in-band 0.073 albedo —
  that is shade, not a material tone error, and raising an in-band albedo to fight shade
  is the banned direction (GT-108). The far-side black band therefore stays a shading /
  asset question, not a tint this file owns; the waterline coping is untouched.

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
    #   [GT-86] y0/y1 -+40 -> -+150. **The channel width (x 11.92..44) and water_z are
    #   untouched** — the drop anchor is the waterline on the stairs and it does not move.
    #   What moves is the lake's *lateral* extent, and it has to: the backdrop masses ran to
    #   y -+108 over a water plate that stopped at -+40, so from `park_vista` and `g9_oblique`
    #   every mass beyond |y| 40 hung over **nothing** and the sky showed under it (the
    #   260731 verdict, "a cloud across the lake"). Grounding the belt means the ground and
    #   the water under it have to reach as far as the belt does. -+150 = the far-shore
    #   plate's `lake_y`, so water and shore share one edge with no gap [computed].
    water=dict(x_far=44.0, y0=-150.0, y1=150.0),
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
    # === [GT-86] far-shore TERRAIN — the ground every backdrop mass now stands on =========
    #   The 260731 verdict on this scene: *"What is that cloud-like thing across the lake?"*
    #   Measured cause, from `look_check/scene09/260731_w3_full/pt_noon_g9_oblique.png` and
    #   `pt_noon_park_vista.png`: `far_hills` ran x 68..141 and y -120..+132 while the only
    #   terrain out there — `far_bank` — is x 44..74, y -+40. **Every ridge outside that
    #   30 x 80 m rectangle had no ground under it at all**, so each ridge body box showed its
    #   flat bottom face and its raw end walls against the sky, and the belt terminated in
    #   mid-air over the water. That is the "flat-bottomed slab" and it is a grounding
    #   failure, not a tone failure.
    #
    #   Fix = five terrain plates that tile the whole backdrop footprint with **no plan
    #   overlap** (so no two coplanar top faces can z-fight) and **no free edge inside any
    #   camera frame** (`backdrop_selfcheck` proves the second claim):
    #     SideS/SideN  x_west..x1  |y| 150..182  — the lake's own S/N shore
    #     BankS/BankN  44..rear_x0 |y| 40..150   — the far bank continued past its y edges
    #     Rear         rear_x0..x1 |y| <= 150    — the wooded terrace behind the shore
    #   **`rear_x0` = `far_bank["x1"]` and `rise` = 0.0 — a butt joint, deliberately.** The
    #   first cut of this row raised the Rear plate 0.35 m so that it would *bury* the far
    #   bank's +X cliff face; that works, but it substitutes a dead-straight 0.35 m lip
    #   running 300 m along x = 72 (0.29 deg, ~9 px at 70 m [computed]) for the cliff, and a
    #   300 m machined line in a natural shoreline is the same class of defect this round
    #   exists to remove. Butting the plates at x = 74 instead leaves the two solids sharing
    #   one plane: the bank's +X face and Rear's -X face are coincident and face **opposite
    #   ways**, so neither is ever the front-most surface, and above z -5.99 there is nothing
    #   to see there at all. Every plate therefore ships at one elevation, `fb_z`, and the
    #   far shore has no seam, no lip and no tone break anywhere in it.
    #   Plate bottoms: side/bank thick 2.4 -> z -5.99 (below water -5.19, exactly the
    #   `far_bank` convention), rear thick 4.6 -> z -8.19. `collider=False` on all five:
    #   nothing walks 100 m across open water, and the hazard/collision box list must not
    #   change for a backdrop row.
    far_shore=dict(x_west=-40.0, x1=158.0, rear_x0=74.0, lake_y=150.0,
                   edge_y=184.0, rise=0.0, thick_side=2.4, thick_rear=4.6),
    # === [GT-86] shoreline scrub — was a 3-run clipped hedge (`build_hedge`, 3.6 m) ========
    #   In both review cuts that row read as **a line of identical dark-green balls** with a
    #   machined scallop on top, 45 m out on a wild lake shore. GT-63 keeps the box+crown
    #   idiom for distant masses, and this row is inside the exception the user opened on
    #   this scene: at 45 m a 2.4-3.2 m shrub subtends 3.0-4.1 deg (~100-130 px at
    #   1920 px / 60 deg), well inside the range where real foliage geometry pays for itself.
    #   -> `sc.place_hedge_row` per segment (real shrub USD, instanced, **legacy build_hedge
    #   fallback when the assets are absent** — the degradation contract is unchanged), with
    #   the runs BROKEN and the heights uneven so the fringe has a profile instead of a scallop.
    #   9 shoreline segments over y -86..+94 (the shoreline is now continuous to |y| 150) plus
    #   4 thicket clumps at x 65..69 that carry the eye from the open shore into the woods
    #   (all four end at x <= 68.8, clear of the Rear plate's x 74 joint).
    #   `sp` indexes `far_hedge["pools"]`; one species per continuous run (K4(b) S-2).
    far_hedge=dict(w=2.4, seed=9021, overlap=0.10, end_margin=0.40,
                   pools=(("Shrub/Holly.usd",), ("Shrub/Privet.usd",),
                          ("Shrub/Burning_Bush.usd",))),
    far_hedges=[dict(cx=51.0, cy=-86.0, L=18.0, h=2.4, sp=0),
                dict(cx=52.4, cy=-64.0, L=14.0, h=3.0, sp=1),
                dict(cx=50.6, cy=-44.0, L=20.0, h=2.6, sp=2),
                dict(cx=52.0, cy=-20.0, L=16.0, h=3.2, sp=0),
                dict(cx=50.8, cy=2.0, L=22.0, h=2.4, sp=1),
                dict(cx=52.6, cy=26.0, L=14.0, h=3.0, sp=2),
                dict(cx=51.2, cy=48.0, L=18.0, h=2.8, sp=0),
                dict(cx=52.2, cy=72.0, L=16.0, h=2.4, sp=1),
                dict(cx=50.6, cy=94.0, L=20.0, h=3.0, sp=2),
                dict(cx=66.2, cy=-52.0, L=15.0, h=3.6, sp=2),
                dict(cx=67.6, cy=-14.0, L=13.0, h=3.2, sp=0),
                dict(cx=66.0, cy=22.0, L=15.0, h=3.8, sp=1),
                dict(cx=67.4, cy=60.0, L=13.0, h=3.4, sp=2)],
    # === [GT-86] far-shore tree stand ====================================================
    #   Was 8 trees on `sc.build_tree`'s **default trunk_h 2.2**, i.e. a target height of
    #   2.2 x 1.60 = 3.52 m [computed]. At 45 m a 3.5 m tree is 4.5 deg tall and stands
    #   *behind a 3.6 m hedge*: in both review cuts the stand is invisible and the shore
    #   reads as bare ground with a ball hedge on it. `th` is now declared per tree and the
    #   stand is a real 8.6-11.5 m shoreline wood (belt species `oak_black`, native 19.74 m,
    #   scaled ~0.5x, instanced by `build_tree`). It also gives the backdrop its middle
    #   depth layer: real foliage at 45-60 m in front of the procedural ridges at 85-200 m,
    #   which is the sane LOD ladder — no 15.6 M-triangle asset is spent at 140 m.
    #   Spacing 6-11 m, irregular, 3 loose ranks; band d_min 7.50 m is satisfied 6x over.
    far_trees=[dict(cx=56.4, cy=-84.0, th=5.6), dict(cx=61.8, cy=-76.0, th=6.4),
               dict(cx=55.0, cy=-68.0, th=6.0), dict(cx=64.5, cy=-60.0, th=5.8),
               dict(cx=57.8, cy=-54.0, th=6.8), dict(cx=54.2, cy=-45.0, th=6.2),
               dict(cx=62.6, cy=-38.0, th=7.0), dict(cx=56.0, cy=-30.0, th=5.8),
               dict(cx=66.0, cy=-24.0, th=6.6), dict(cx=58.6, cy=-17.0, th=6.0),
               dict(cx=54.6, cy=-8.0, th=6.4), dict(cx=63.4, cy=-2.0, th=7.2),
               dict(cx=57.2, cy=6.0, th=5.4), dict(cx=60.8, cy=14.0, th=6.6),
               dict(cx=54.8, cy=21.0, th=6.0), dict(cx=65.2, cy=28.0, th=6.8),
               dict(cx=58.0, cy=35.0, th=5.8), dict(cx=62.0, cy=44.0, th=6.4),
               dict(cx=55.4, cy=52.0, th=6.2), dict(cx=66.4, cy=62.0, th=7.0),
               dict(cx=59.2, cy=70.0, th=5.6), dict(cx=63.8, cy=80.0, th=6.6),
               dict(cx=56.8, cy=90.0, th=6.0)],
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
    # Autumn hillside belt.
    #   [GT-86 — the user overrides the GT-63 "cheap distant mass is intended" ruling for
    #    THIS scene, recorded in the ledger row.] Two measured defects were rebuilt out:
    #
    #   (a) **balloons.** The old crown was `blob_r 0.58 x h` in z on a plan radius of
    #       `sx x 0.92 / 2` — 12.4-23.9 m across. From the h1.8 grid eye that subtends
    #       **8.0-10.0 deg**, ~290 px at 1920 px / 60 deg [computed]. A real broadleaf crown
    #       is 4-8 m across. The belt was drawing objects 2.5x too big to be trees, which is
    #       why it read as cumulus. The crown radius is now declared per ridge (`cr`) and set
    #       so that **every belt subtends the same 3.2-3.6 deg** whatever its distance — a
    #       real distance LOD, not a constant: cr 2.8 @ 88 m, 3.6 @ 113 m, 4.6 @ 134 m,
    #       5.6 @ 180 m (the flanking ridges).
    #   (b) **the body box.** `body_frac 0.30 x h` was an axis-aligned cuboid under the
    #       crowns; at 11-19 m tall it was never covered and it is the flat-topped slab and
    #       the raw end walls visible in `pt_noon_g9_oblique.png`. It is **deleted**. The
    #       landform is now `lobes` flattened ellipsoids whose centres sit BELOW the terrain
    #       top (`sink` 0.55 of their own z radius), so only a cap emerges — a buried cap has
    #       no bottom face and no end wall by construction, at any camera angle.
    #
    #   Silhouette: crowns are scattered on a jittered grid over the ridge footprint, each
    #   drawn at 0.72-1.30 x cr with an independent z radius, and `spire_p` of them are
    #   redrawn as narrow conifer spires (0.46 x radius, 2.30 x height) that break the crest
    #   line — the sawtooth-with-spikes profile of a Korean wooded ridge. Every crown is sunk
    #   `bury` of its z radius into the surface it stands on, so no crown floats and none
    #   shows a cut edge.
    #   Tone: `hill_mix[tone]` are per-crown weights over (hill_a, hill_b, hill_c, hill_d),
    #   so a ridge is a mixed stand, not one flat colour.
    #
    #   **`h` is the ridge's CREST height above its terrain plate, and it is honest.** The
    #   first cut of this row kept the old meaning ("landform = h x land_frac, crowns on
    #   top"), which made the realized crest of a 20.5 m ridge come out at **9.9 m** —
    #   `horizon_selfcheck` and `backdrop_selfcheck` would both have been asserting against
    #   a height the scene does not build. The assembler now solves the landform from the
    #   crest instead: `land_h = h - (1 - bury) * cr * crown_ref`, so the mean crest crown
    #   tops out at `base + h` and the two gates measure the mass that is actually there.
    #   Heights are set from the two things that bind them [computed]:
    #     - `horizon_selfcheck`: the nearest ridge face (x 74.2, 50.3 m from `from_river`)
    #       must subtend >= 9.44 deg -> crest >= 8.36 m. Belt A ships 11.0-12.5 m.
    #     - belt separation at the LOW eyes (the grid presets at z 0.3-1.8, where a farther
    #       ridge is only visible if it is taller): z_B > 1.8 + 1.235 (z_A - 1.8) and
    #       z_C > 1.8 + 1.231 (z_B - 1.8). Against the DERATED crest (0.85 h, the ratio the
    #       gates use) that needs h_B > 12.1 and h_C > 13.4; the shipped 11.0 / 13.5 / 16.0
    #       clears both.
    #   `sx` widened with it (18-30 -> 26-34) so the landform slope stays in the 40-45 deg
    #   band a Korean wooded ridge actually stands at, instead of becoming a thumb.
    #
    #   Layout (cx, cy, sx, sy, h, tone, cr) — 3 belts + 2 flanking shore ridges:
    #     belt A  cx 90-92   h 11.0-12.5  the wooded slope right behind the shore; its toe is
    #             at x 74.2, i.e. hard against the Rear plate's front edge [computed]
    #     belt B  cx 112-114 h 13.5-14.5
    #     belt C  cx 133-135 h 16.0-17.0  stands on the Rear plate's back edge, so the plate's
    #             own far edge (x 158) is always behind a crest and never meets the sky
    #     flank   cy -+167   h 13.5       on the SideS/SideN plates: these close the lake's own
    #             S/N horizon, which is where `park_vista` and `g9_oblique` looked straight
    #             past the old belt into empty dome.
    #   Every footprint is inside a single terrain plate and every crown centre is clamped to
    #   that plate inset by its own radius — `backdrop_selfcheck()` asserts both.
    far_hills=[dict(cx=90.0, cy=-124.0, sx=26.0, sy=46.0, h=11.5, tone=0, cr=2.8),
               dict(cx=91.0, cy=-86.0, sx=26.0, sy=42.0, h=12.5, tone=1, cr=2.8),
               dict(cx=90.0, cy=-50.0, sx=26.0, sy=40.0, h=11.0, tone=0, cr=2.8),
               dict(cx=92.0, cy=-14.0, sx=26.0, sy=40.0, h=12.5, tone=1, cr=2.8),
               dict(cx=90.0, cy=22.0, sx=26.0, sy=40.0, h=11.5, tone=0, cr=2.8),
               dict(cx=91.5, cy=58.0, sx=26.0, sy=40.0, h=12.0, tone=1, cr=2.8),
               dict(cx=90.0, cy=96.0, sx=26.0, sy=46.0, h=11.0, tone=0, cr=2.8),
               dict(cx=113.0, cy=-118.0, sx=30.0, sy=52.0, h=13.5, tone=1, cr=3.6),
               dict(cx=112.0, cy=-70.0, sx=30.0, sy=52.0, h=14.5, tone=2, cr=3.6),
               dict(cx=114.0, cy=-20.0, sx=30.0, sy=52.0, h=13.5, tone=1, cr=3.6),
               dict(cx=112.0, cy=30.0, sx=30.0, sy=52.0, h=14.5, tone=2, cr=3.6),
               dict(cx=114.0, cy=78.0, sx=30.0, sy=52.0, h=14.0, tone=1, cr=3.6),
               dict(cx=113.0, cy=120.0, sx=30.0, sy=48.0, h=13.5, tone=2, cr=3.6),
               dict(cx=135.0, cy=-112.0, sx=34.0, sy=60.0, h=16.0, tone=2, cr=4.6),
               dict(cx=133.0, cy=-56.0, sx=34.0, sy=62.0, h=17.0, tone=2, cr=4.6),
               dict(cx=135.0, cy=0.0, sx=34.0, sy=62.0, h=16.5, tone=2, cr=4.6),
               dict(cx=133.0, cy=56.0, sx=34.0, sy=62.0, h=17.0, tone=2, cr=4.6),
               dict(cx=135.0, cy=112.0, sx=34.0, sy=60.0, h=16.0, tone=2, cr=4.6),
               dict(cx=60.0, cy=-167.0, sx=180.0, sy=20.0, h=13.5, tone=2, cr=5.6),
               dict(cx=60.0, cy=167.0, sx=180.0, sy=20.0, h=13.5, tone=2, cr=5.6)],
    #   `lobe_span` / `lobe_r` / `lobe_w` are the landform's fit to its own footprint, and
    #   they are solved, not tuned: an ellipsoid sunk by `sink` of its z radius emerges with
    #   `sqrt(1 - sink^2)` = 0.835 of its plan radius, so the outermost cap reaches
    #   `lobe_span/2 + lobe_r` = 0.28 + 0.22 = **0.50** of the ridge length — exactly the
    #   declared footprint, never past it — while adjacent caps still overlap
    #   (centre pitch 0.28 L against radii 0.22 L each) so the ridge has no notch between
    #   lobes. Across the ridge, `lobe_w + lobe_jit` = 0.43 + 0.07 = **0.50** likewise
    #   [computed]. That is what lets `backdrop_selfcheck` test the footprint and be testing
    #   the geometry.
    hill=dict(lobes=3, sink=0.55, bury=0.45, pitch=1.55, crown_ref=1.20,
              jit=0.30, spire_p=0.18, spire_r=0.46, spire_h=2.30, seed=91,
              lobe_span=0.56, lobe_r=0.22, lobe_w=0.43, lobe_jit=0.07,
              # per-crown tone weights over (hill_a maple, hill_b ginkgo,
              #   hill_c haze, hill_d evergreen). Warm near, hazy far — the aerial
              #   perspective is now carried by the MIX, not by one flat colour.
              mix=((0.42, 0.26, 0.04, 0.28),
                   (0.24, 0.44, 0.06, 0.26),
                   (0.12, 0.16, 0.54, 0.18))),
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
                  # [GT-115 ⑨ (5)] **절병통, not a chimney.** The apex member was a single
                  #   `add_cylinder` — an analytic `UsdGeom.Cylinder`, which Hydra tessellates at
                  #   its own low default (the octagon defect `scene_common.DISC_SEGMENTS`
                  #   documents), so a 0.22 m-wide 0.42 m-tall drum on a ridge renders as a
                  #   flat-sided box = the chimney in `pt_noon_across_river.png`. A Korean 절병통
                  #   is a *stack*: 노반 base plate, 복발 bowl, a turned neck, 보주 bead, tip. Five
                  #   `add_disc` members (32-gon, silhouette under our control) give that profile
                  #   for 4 extra prims on one pavilion, and the total height stays **0.42** so the
                  #   finial tip is still 4.71 and no other number in this file moves.
                  #   (label, height fraction of finial_h, radius × finial_r)
                  finial_stack=(("", 0.143, 1.41),        # 노반 — base plate, widest
                                ("Bowl", 0.310, 1.14),    # 복발 — the bowl
                                ("Neck", 0.214, 0.68),    # 목 — turned waist
                                ("Bead", 0.238, 1.05),    # 보주 — the bead
                                ("Tip", 0.095, 0.50)),    # 촉 — soft tip
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
    #   [GT-115 ⑨ (4)] **Ø0.48 × H2.1 → Ø0.30 × H0.90.** Measured off
    #   `260806_w3_allview5/pt_noon_across_river.png`: at 2.1 m tall and 0.48 across these read as
    #   four *columns* standing on the promenade, not as quay posts — a Korean 계선주 / 말뚝 on a
    #   park waterfront is 0.6–0.9 m of stone above the paving with a 0.25–0.35 shaft. r 0.15 /
    #   h 0.90 is the top of that band (it still has to be seen from the water).
    #   Nothing measures them: `fov_selfcheck()` does not list `land_posts`, and the two clearances
    #   the block above derives improve rather than shrink — the footprint edge moves x −1.04 →
    #   **−0.95** (pavilion eave tip −1.15, clearance 0.11 → **0.20 m**) and the gap to the pile row
    #   at x −1.2 grows from 0.07 to **0.16 m** [computed]. They keep `collider=True`, so the four
    #   element AABBs shrink with them (GT-8 class: element boxes move, the hazard list does not).
    land_posts=dict(r=0.15, h=0.90, x=-0.80, z=0.0,
                    ys=(-12.0, -5.6, 5.6, 12.0)),
    # [v6 rework (3)] 2 lawn bands on the upper terrace — puts the evidence for "park" into the frame.
    #   Outside the stair width (y±5) · inside the terrace (x −30..0, y ±40). Top face proud by 0.03 (walk continuity).
    #   How it reads: left/right lawn faces in park_vista; in from_river/across_river
    #   only the **street-tree canopies** rise above the terrace ridge line, forming a green skyline.
    lawns=[dict(x0=-24.0, x1=-0.8, y0=12.0, y1=30.0),
           dict(x0=-24.0, x1=-0.8, y0=-30.0, y1=-12.0)],
    lawn_proud=0.03,
    # [W3 P09 · GT-41 (1)] **판석 디딤돌 — G9's stepping stones, as physical slabs.**
    #   `w3_s09_v1.md` §2 row 15 declined them (**P6**) because the user's 바닥 사각형 무늬 ban
    #   was live and a scene lane cannot adjudicate a ban. `w3_intake_v2_images.md` §7.2 did
    #   adjudicate it: *"S09 — stepping stones ALLOWED as physical 판석 slabs with 3D relief
    #   (the user's ban targets decorative rectangle DECALS, not real objects; prefer irregular
    #   outlines)"*. So the three conditions of the permission are built in, and each one is a
    #   machine check in `stepstone_selfcheck()` rather than a sentence here:
    #     · **physical, with relief** — a 0.120 m thick slab (the 화강석 판석 100~150 mm band),
    #       bedded into the turf, authored as a **UsdGeom.Mesh prism** (the `build_hip_roof`
    #       precedent) and not as a ground decal;
    #     · **irregular outline** — 6 or 7 vertices, per-vertex radius drawn from
    #       [`r_lo`, `r_hi`] and per-vertex angle jittered by up to `ang_var`, so no slab is a
    #       rectangle and no two slabs are alike. The gate asserts `nv >= 5` and a minimum
    #       radius spread on every slab;
    #     · **sub-threshold** — top face `lawn_proud + proud` = 0.030 + 0.012 = **0.042**, i.e.
    #       12 mm above the mown turf, **below `ground_kit.GT_DELTA` (0.020)**. The gate asserts
    #       it against the imported constant, so a later edit cannot drift it silently.
    #   **12 mm is also the correct Korean detail here, not just the convenient one.** A 디딤돌
    #   in a **planting bed** stands 30~60 mm proud (it must shed water and out-top the ground
    #   cover); a 디딤돌 in a **mown lawn** is set flush-to-slightly-proud, because anything
    #   taller is a mower strike. G9's slabs sit in mown turf with the grass growing to their
    #   edges — flush-set, and that is what is built.
    #   **Where, and why there.** One route, in the −Y lawn band, from the lawn's inner edge to
    #   the **landward end of boardwalk leg L1** (`y −18.0`, `x −16.0…−9.2`). Before this the
    #   boardwalk began in the middle of a lawn with **no land approach at all** — a 디딤돌 line
    #   exists exactly where a desire line crosses turf between two hard surfaces, and this is
    #   that line. `x = −14.6` is chosen, not centred: the park tree at (−13.0, −17.8) stands on
    #   the obvious `x = −13` line, and 1.60 m of clearance from its trunk is worth more than a
    #   round number. Stagger ±0.10 m alternating — a stepping-stone line follows a **stride**,
    #   and a stride alternates feet.
    #   **No +Y mirror**, deliberately: the +Y lawn has no boardwalk and therefore no
    #   destination, and a decorative copy of a functional route is the thing the ban is about.
    #   **Placement law** [computed]: the footprint is `x −15.015…−14.185`, `y −17.865…−12.105`,
    #   i.e. entirely **behind** all three h0.3 preset eyes (`x = −2/−5/−10`, looking +X), so
    #   `fov_selfcheck` returns `OUT(전 프리셋 후방)` and the judged near window cannot see it.
    #   It reads in `g9_oblique`, the cut the target image is judged against.
    stepstones=dict(x=-14.6, y0=-12.42, pitch=0.57, n=10, stagger=0.10,
                    r_lo=0.235, r_hi=0.315, nv=(6, 7), ang_var=12.0,
                    thick=0.120, proud=0.012, seed=709),
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
              hull_float=0.12,              # how far the hull centre floats above the water
              # [GT-115 ⑨ (7)] **the seat well.** The v6 rework gave the boat a curved hull and
              #   stopped there, so at 400 % it is still one smooth yellow mass with a canopy
              #   floating over it — there is no opening, and a pedal boat is mostly opening.
              #   One dark box does the whole job: 1.10 × 0.86 in plan (inside the 2.60 × 1.24
              #   hull), top face **0.025 below the hull crown**, which is where the ellipsoid has
              #   already fallen away at |y| > 0.227 [computed: 0.36·√(1−(y/0.62)²) = 0.335], so the
              #   well **emerges through the flanks** and reads as a cut-away cockpit from the two
              #   water cuts while staying a rectangle seen from `park_vista` above. Dimensions of
              #   every existing part are untouched — this row adds one box and one material.
              cockpit=(1.10, 0.86, 0.30), cockpit_dx=-0.12, cockpit_drop=0.025),
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
    #   [GT-115 ⑨ (6)] **`sink` is now declared per row, as a fraction of the feature's own
    #   height.** Every row used to be bedded by the same flat 0.10 m, which on a 0.55 m boulder
    #   is 18 % and on a 0.78 m one is 13 % — measured in `pt_noon_park_vista.png` the rocks read
    #   as if *laid on* the mown surface, which is the one thing a 조경석 never is: Korean practice
    #   sets a landscape stone with roughly **a third of its height buried** (지반 매입 1/3), and
    #   the exposed part is the part that was above ground in the quarry. 0.33 for the three
    #   boulders. The stump keeps a shallow **0.08** — G9's root feature sits *on* its moss bed and
    #   burying a root plate to a third would delete the feature.
    #   (asset, bed tag, u, v, target_h, yaw, sink) — u/v are fractions of the bed footprint,
    #   `sink` is a fraction of `target_h`.
    bed_features=[("tree_stump_01", "B2", 0.42, 0.52, 1.25, 24.0, 0.08),
                  ("rock_moss_set_01", "B1", 0.68, 0.40, 0.62, 137.0, 0.33),
                  ("rock_moss_set_01", "B3", 0.30, 0.58, 0.78, 291.0, 0.33),
                  ("rock_moss_set_01", "B4", 0.55, 0.46, 0.55, 63.0, 0.33)],
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
              plume_h=0.22, plume_r_mul=1.9,
              # [GT-115 ⑨ (1)] The seed head was **one cylinder**: a flat top and a full-radius
              #   down-facing cap sitting proud of a culm less than half its width. Both are
              #   visible at 400 % in `260806_w3_allview5/pt_noon_across_river.png` — the flat
              #   top reads as a cotton bud and the cap, lit by sky alone, is the dark ring at
              #   the joint. A 갈대 panicle is a **spindle**: it carries its mass low and dies
              #   away to a soft tip. Two stacked cylinders of decreasing radius are the cheapest
              #   honest form of that (1 extra prim per plume, 102 in the scene) —
              #     lower `plume_lo_frac` of the height at `plume_r_mul` × r  (the mass)
              #     upper remainder at `plume_tip_mul` × r                     (the tip, 19 mm)
              #   and the whole head is seated `plume_seat` **into** the culm so no gap can open
              #   at the joint whatever the tilt.
              plume_lo_frac=0.62, plume_tip_mul=0.85, plume_seat=0.045),
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
        # [GT-115 ⑨] three world tile sizes join the table. All three exist because the object
        #   they dress is far smaller than the promenade module the old entries were sized for,
        #   and a world-projected map on an object smaller than its own tile is what the audit
        #   batch is about (module docstring, the promotion mechanism):
        #     `quay_stone` 0.38 — the 계선주 is Ø0.30 × 0.90, so at 0.38 m one post covers about
        #       one tile of `rock_face`: the map's mean is what the post shows, and the mottle
        #       runs at the grain size of a quarried block rather than as a pattern.
        #     `roof_tile` 1.50 — **solved, not chosen.** `granite_dark` is a 5 × 5 module inside
        #       its own tile [measured], so the world size of one cell is `scale / 5`; a Korean
        #       기와 course is 0.30–0.35 m, and 1.50 / 5 = **0.30 m** puts the map's module
        #       exactly on the real course module instead of somewhere between two of them.
        #     `reed` 0.28 — a culm is 44 mm across and 1.1–1.9 m tall, so the tile has to be
        #       *shorter than the stem* for the grain to run along it (4–7 repeats per culm) and
        #       for neighbouring stems to sample different phases = free per-stem tone variation.
        scale=dict(stone=1.1, grass=1.4, wood_dark=0.9, wood_fine=0.45,
                   quay_stone=0.38, roof_tile=1.50, reed=0.28),
        # [v7 judgment §6 (3)] the stone tone swap landed as a **large near-white area**.
        #   `ghat_walk` paving RGB (223,222,221) · 65 % of the frame,
        #   and in `from_river` the 36 steps fused into "one white retaining wall", losing all step articulation.
        #   Judgment recommendation (b), lowering 0.86 → 0.62~0.68, is adopted as is (the 0.64 family).
        #   plaza_light diff linear mean 0.469 × 0.64 = **albedo 0.300**
        #   (real grey granite sits in the 0.2~0.35 band) → expected render sRGB 0.75 ~ 191.
        #   ** geometry and concealment behaviour unchanged ** — every step, terrace and embankment still share one material.
        # [W3 P09 · GT-41 (2)] **0.64 → 0.524.** The v7 step above fixed the *sandstone swap*'s
        #   near-white; it did not fix the paving, and the W3 S09 round measured exactly how much
        #   was left: `near_ground_stats` on the three judged h0.3 cuts read **wht% 64.6 / 66.0 /
        #   65.2** against the v5.1 §1 convention of < 2, mean **203 / 206 / 204** against ≤ 170,
        #   and `regression_check` raised a **WHITE FAIL** on `h0.3_d10` (2.1 → 45.4 %,
        #   `look_check/scene09/260731_w3_s09/regr_vs_260731_w3_cb1.json`). `w3_s09_v1.md` §7 **P1**
        #   filed the correction and declined to take it at the end of a long lane, *"after the
        #   pilot"*; `w3_intake_v2_images.md` §7.2 then authorised it — *"stone_tint 0.64→0.524
        #   measured correction authorized (material micro)"*.
        #   Linear factor **0.818** (0.64 × 0.818 = 0.5235). albedo 0.469 × 0.524 = **0.2458**,
        #   which is the middle of the real grey-granite 0.20~0.35 band and no longer its top;
        #   expected render sRGB `_srgb(0.2458 × 1.77)` = **0.691 ≈ 176** (was 0.756 ≈ 193).
        #   **The same 0.818 is applied to every tint that was authored as a ratio of this one**
        #   (`stain` · `moss` · `drystone` · `drystone_cap`), so the ratios below survive to four
        #   decimal places and the **waterline contrast — this scene's only drop anchor — is
        #   preserved by construction**, exactly as v7 preserved it through 0.90 → 0.64.
        #   Not scaled, deliberately: `gk_crack` (a flat 0.055 near-black) — darkening the paving
        #   only *widens* the crack contrast, and a crack is not a ratio of the stone it is in.
        # [GT-126] **× 0.850** — third exposure correction, same shape as the two above.
        #   260815_w4_r4batch judgment cut clipHi 56.8 % (audit metric, disp > 0.75); the
        #   pavers own 51.6 pp of it. Not a binding failure [measured — `from_river` renders
        #   the stain band at its authored hue R/B 1.20 and the declared stain/stone ratio]:
        #   the judged PT noon gain on open horizontal ground is **2.40-2.46** (paver lin
        #   0.578-0.592 over effective 0.2411), so the v7 "expected render 176" above is an
        #   RT-era prediction and stale under PT. At the measured gain the metric's clip line
        #   sits at effective **0.211 — inside the 0.20-0.35 band** — so no legal stone albedo
        #   clears the metric; the mean is brought under the line instead. Landing rule =
        #   GT-121 2차 (s15 0.30 → 0.24): reproduce its landing display (mean disp 0.725)
        #   under this scene's own gain → eff 0.197-0.202; taken just inside the band:
        #   0.469 × 0.445 = **0.209** (measured-map luminance 0.205; bottom third, floor
        #   respected), expected paver mean ≈ disp 0.73 ≈ 187 sRGB. Projected on the shipped
        #   cut [computed]: paver clipHi 76.5 → 28.5 %, frame ≈ 24 %; the residual is texture
        #   spread over an exposure whose clip line is in-band — exposure-owned (GT-125's
        #   PHYS_V1 grazing arm is the next lever, not a darker stone).
        #   **The same 0.850 goes to every tint authored as a ratio of this one** (`stain` ·
        #   `moss` · `drystone` · `drystone_cap` · `stepstone`), so the ratios below survive
        #   and the **waterline contrast — this scene's only drop anchor — is preserved by
        #   construction**, exactly as 0.90 → 0.64 → 0.524 preserved it twice before.
        #   `gk_crack` again not scaled (same reason as above). `quay_stone_tint` takes a
        #   **partial** factor — see its own note (two-anchor conflict).
        #   구값 `[repro — W3 P09 · GT-41 (2)]`: (0.524, 0.515, 0.491)
        stone_tint=(0.445, 0.438, 0.417),      # was (0.524,0.515,0.491) ← (0.64,0.63,0.60) ← (0.90,0.89,0.86)
        # [v5 adopted] moss tint — the 2 steps just below the water (the 'wet band' of the water-level history).
        # [v7] **contrast ratio preserved** to match the stone_tint reduction (0.90→0.64).
        #   old moss/stone = 0.30/0.90 = 0.333 → new 0.64×0.333 = 0.213.
        #   (dropping the absolute value alone would kill the waterline cue with it — this scene's only drop anchor)
        # [W3 P09] × 0.818 again. moss/stone 0.3328 → **0.3321** [computed].
        # [GT-126] × 0.850 with the paving. moss/stone 0.3321 → **0.3326** [computed].
        moss_tint=(0.148, 0.197, 0.128),       # was (0.174,0.232,0.151) ← (0.213,0.284,0.185)
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
        # [W3 P09 · GT-41 (2)] × 0.818 with the paving, and **this is the reason it had to move**:
        #   the comment above authors this tint as *0.86× the paving*. Left at 0.55 while the
        #   paving dropped to 0.524 the wall would have come out **lighter than the machined slab
        #   beside it** (ratio 1.050) — the exact inverse of the physical claim it is built on.
        #   drystone/stone 0.8594 → **0.8588**, cap/stone 0.9375 → **0.9370** [computed].
        #   These two faces are outside the ±30° cone of all three h0.3 presets (`fov_selfcheck`),
        #   so they cannot enter the wht% verification in either direction — the two halves of
        #   this tone row are cleanly separable, and they are separated in the report.
        # [GT-126] × 0.850 with the paving, for the same reason it had to move with GT-41 (2):
        #   left alone, the field-stone wall comes out lighter than the machined slab — the
        #   inverse of the physical claim it is built on. drystone/stone 0.8588 → **0.8607**,
        #   cap/stone 0.9370 → **0.9371** [computed].
        drystone_tint=(0.383, 0.361, 0.320),   # was (0.450,0.425,0.376) ← (0.55,0.52,0.46)
        drystone_cap_tint=(0.417, 0.396, 0.348),  # was (0.491,0.466,0.409) — coping, a shade lighter
        # [W3 S09 row (6)] autumn hillside. The three tones are the two that dominate G9
        #   (ginkgo yellow, maple orange) plus the dark conifer band a Korean hillside always
        #   carries; `hill_c` is the far ridge and is deliberately **lighter and greyer**, not
        #   darker — aerial perspective washes a distant ridge toward the sky, and the old
        #   `far_color` boxes got that backwards (a 0.13 near-black silhouette at 70 m).
        # [GT-86] **levelled down x0.73.** The measured failure of the 260731 cut is that
        #   the belt read as *cloud*, and the tone was half the cause: at 0.288 albedo the
        #   render prediction is sRGB 0.74 (189/255) — brighter than the granite promenade
        #   in the same frame, on a mass 90-140 m away. Measured autumn hillside reflectance
        #   at that range sits in the 0.14-0.22 band, so the pair is re-levelled and the
        #   hue ratio (1 : 0.731 : 0.291 / 1 : 0.875 : 0.299) is preserved exactly.
        # [GT-115 ⑨ (2)] **levelled again, ×0.55 — into this file's own declared band.** GT-86
        #   levelled these to 0.196–0.245 against a "measured autumn hillside 0.14–0.22" figure,
        #   but that figure is a *hillside-with-haze* reflectance and it was applied to the crown
        #   masses themselves, so the belt still renders as pastel blobs: measured band mean on
        #   `260806_w3_allview5/pt_noon_park_vista.png` is **47 % linear** (bright crown faces
        #   150–200 sRGB), against the **6–12 %** vegetation reflectance band this same PARAMS
        #   block declares 60 lines below (`far_color`/canopy note) and applies to `canopy_a/b`.
        #   The ×0.73 GT-86 used and the ×0.55 here compose to 0.40 of the pre-GT-86 tone; the
        #   hue ratios (1 : 0.731 : 0.291 and 1 : 0.875 : 0.299) are preserved exactly, so the
        #   ginkgo/maple separation the belt is built on survives the level change.
        hill_a=(0.108, 0.079, 0.031),          # 단풍 maple orange-red   (was 0.196/0.143/0.057)
        hill_b=(0.116, 0.101, 0.035),          # 은행 ginkgo yellow      (was 0.210/0.184/0.063)
        # [GT-86] the dark evergreen a Korean hillside always carries, added as a **fourth**
        #   tone. The three-tone belt gave every ridge one flat colour, which is the other
        #   half of the cloud read; `hill_mix` now draws per crown from four tones, and this
        #   is the one that supplies the tonal breaks between the warm masses.
        hill_d=(0.058, 0.078, 0.048),          # 상록침엽 dark evergreen
        # [revised after the first pilot] the first value (0.176, 0.176, 0.148) was **darker**
        #   than the near ridges (0.268) — the exact opposite of what the comment above it claims,
        #   and it rendered as a near-black rock wall standing over the autumn ridge instead of
        #   receding behind it. Aerial perspective adds the sky's own light along the path, so a
        #   distant ridge is **lighter and bluer** than a near one, never darker. Corrected to sit
        #   above `hill_a`/`hill_b` in value with a blue bias, which is also what G9 shows.
        # [GT-86] levelled with the pair above (x0.85 here, not x0.73: the haze tone must stay
        #   **above** hill_a/hill_b in value or aerial perspective inverts again).
        # [GT-115 ⑨ (2)] ×0.49 here, not ×0.55, for the same reason GT-86 used a different factor
        #   on this row: the ceiling of the 6–12 % band is 0.12 on the max channel, and this tone
        #   is the blue-biased one, so the flat ×0.55 would have put it at 0.135 = outside the band
        #   the row is being levelled into. The ordering that carries aerial perspective survives
        #   and is asserted by construction — Rec.709 luminance d **0.0716** < a **0.0817** <
        #   b **0.0994** < c **0.1021** [computed], the same order as before this row.
        hill_c=(0.096, 0.102, 0.120),          # far ridge, washed toward the sky (was 0.196/0.209/0.245)
        hill_rough=1.0,
        # [GT-86] the bare hillside under the canopy (the emerged landform caps). Deliberately
        #   duller and greyer than `grass_tint` (x0.72 / x0.66 / x0.79): it is only ever seen
        #   in the slivers between crowns at 85-200 m, where a promenade-bright green would
        #   read as a painted flat. The far-shore ground plates themselves keep `grass_tint`,
        #   identical to `FarBank`, so the shoreline carries **no tone seam** at all.
        shore_tint=(0.396, 0.449, 0.332),
        # [GT-86] procedural fallback tone for the shoreline scrub (`place_hedge_row` ->
        #   `build_hedge` when the shrub assets are absent). Darker than the shore it stands
        #   on, or the fringe disappears into the ground in the degraded arm.
        scrub_tint=(0.232, 0.298, 0.196),
        # [v6 (1)] pavilion timber members — posts, tie beams, railing (reddish-brown pine) / raised floor (light floorboard)
        # [GT-115 ⑨ (3)] **`pav_floor_tint` 0.78/0.60/0.42 → 2.58/2.83/2.77.** The old triple was
        #   authored as if it were an sRGB colour, but a tint is a *multiplier on the bound map*,
        #   and the map is `wood_dark` — linear mean (0.081, 0.058, 0.044), luminance 0.062, the
        #   darkest wood in the library (`scene_common:574` says so in as many words and raises the
        #   class gain cap to 7.0 because of it). 0.78/0.60/0.42 on that is an effective albedo of
        #   **0.038 luminance**, i.e. 3.8 % — a dark-stained plywood, in permanent shade under a
        #   hip roof. Measured floor RGB in `pt_noon_park_vista.png`: **(4,4,6)**.
        #   Re-solved rather than nudged: target 0.170 luminance (middle of the 0.15–0.25 timber
        #   band a 누마루 마루널 actually sits in) at a floorboard ratio 1 : 0.78 : 0.58, i.e. an
        #   effective albedo of (0.209, 0.163, 0.121); divide by the map's own mean and the tint
        #   falls out as (2.58, 2.83, 2.77) [computed]. **It is near-neutral on purpose** — the
        #   map is already the right hue, and the old triple double-counted its warmth, which is
        #   the other half of why the floor went black rather than merely dark.
        #   ×3 on a map whose mean is 0.062 is well inside the wood class's own 7.0 gain cap.
        pav_wood_tint=(0.68, 0.44, 0.28), pav_floor_tint=(2.58, 2.83, 2.77),
        # [v8 judgment §4 (1)] the near-white roof was really a **specular additive term** (module
        #   docstring [v8 Y1] (b)(c)). Killing that term with `specular_level=0.0` leaves diffuse
        #   only, at (147,152,160) — still a light grey, so the albedo also drops x0.70.
        #   0.109~0.130 = the measured 0.10~0.15 reflectance band of dark grey unglazed tile.
        #   The colour ratio (1 : 1.064 : 1.193) is preserved as is.
        roof_tile_color=(0.109, 0.116, 0.130), roof_tile_rough=0.72,  # Korean roof tile
        roof_tile_specular=0.0,                # [v8 Y1] the cause — see the comment below
        # [GT-115 ⑨ (5)] **the roof was a grey running-bond block wall.** Cause, measured:
        #   `Looks/PavRoof` never reaches the "roof" keyword — `_LOOK_RULES` tests **paving**
        #   (rule 16) before **concrete** (rule 17, which owns "roof"), and paving's token list
        #   contains **"pav"**. So the material classified `paving`, and a constant colour in a
        #   `_CONST_MDL_CLASSES` role is promoted to its class texture: `paving_interlock`, i.e.
        #   interlocking pavement blocks, laid over a 4-sided hip roof at a 1.2 m tile.
        #   `roof_tile_color` stays the **declared albedo** (it is what `roof_specular_selfcheck`
        #   predicts from, and the v8 Y1 finding is built on it); what changes is that the map is
        #   now chosen and bound here instead of being guessed by the promoter:
        #     `granite_dark` — linear mean (0.076, 0.077, 0.077), the only **neutral** map in the
        #     registry, hence a tint of (1.434, 1.512, 1.680) whose channel spread is **1.17**:
        #     nothing can be amplified into a false hue. Its own module is a 5 × 5 stack bond, and
        #     that is why it is the right map here rather than in spite of it — a roof **is**
        #     modular, and `scale["roof_tile"]` 1.50 lands one cell on **0.30 m**, the Korean
        #     기와 course. `paving_interlock` could never do that: it is a *running* bond
        #     (staggered), which is the one thing a course of roof tiles never is.
        #   tint × map mean = (0.109, 0.116, 0.130) = `roof_tile_color`, to 4 dp [computed], so the
        #   scene's own §4 albedo check and the v8 sRGB predictions are unchanged in value.
        roof_tile_tint=(1.434, 1.512, 1.680),
        # [v6 (2)] duck boat — white (0.86) → yellow (at or below the §4 near-white cap of 0.8)
        duck_color=(0.78, 0.70, 0.25), duck_rough=0.45,
        duck_top_color=(0.52, 0.19, 0.17), duck_top_rough=0.55,  # canopy (red)
        beak_color=(0.74, 0.42, 0.07), beak_rough=0.5,
        # [GT-115 ⑨ (7)] the seat well. Dark enough to read as an opening at 12–30 m (the two
        #   water cuts) without going to black — a moulded GRP cockpit liner is a dark grey with a
        #   little of the hull's warmth in it, and 0.06 is the same near-black floor the kit's own
        #   crack decal uses (`gk_crack` 0.055), i.e. inside a value this scene already ships.
        duck_seat_color=(0.062, 0.058, 0.054), duck_seat_rough=0.70,
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
        # [GT-115 ⑨ (1)] **the two colours above stay exactly as declared — they are now
        #   reproduced through a map instead of being handed to the promoter.** Mechanism, from
        #   `scene_common`: `Looks/Reed` classifies `veg` (exact-match table), veg is in
        #   `_CONST_MDL_CLASSES`, so the constant was promoted to the class map `grass_lawn` with
        #   `base_color = declared / map mean` = **(3.99, 1.85, 5.46)**. Promotion preserves the
        #   map's *mean*; it cannot preserve the mean of a **sample**, and a 44 mm culm covers
        #   1.5 % of a 1.4 m tile — so each stem takes one arbitrary texel patch and multiplies it
        #   ×5.46 in the channel the grass map barely has (`scene_common:591-596` names this exact
        #   failure on scene11's `leaf_far_*`). Measured on the shipped cut: stems
        #   **(183,163,172) sRGB — blue above green**, on a material declared warm brown, wrapped
        #   in the grass map's blade/soil structure stretched to a 1.4 m period = the "masonry
        #   joint" reading. The plume's down-facing cap, sky-lit only, ×5.46 in blue, is the navy
        #   gap at the joint.
        #   Fix = bind a map whose **hue is already the declared hue**, so the multiplier is flat:
        #   `wood_dark` (linear mean 0.081/0.058/0.044) is the library's dry-fibre map, and a
        #   갈대 culm is lignified fibre with a visible longitudinal grain. Spread falls
        #   **2.95 → 1.26** (stem) / **1.27** (plume): no channel can be pushed into a false hue
        #   whatever patch a stem lands on. tint × map mean reproduces `reed_color` /
        #   `reed_plume_color` to 4 dp [computed], so the §4 albedo rows below are unchanged in
        #   value and only change which map they are measured against.
        #   The two colour rows stay above as the **declaration of record**: they are what these
        #   tints reproduce, and what any future re-map has to reproduce again. Nothing binds them
        #   directly any more — the tint is the thing that reaches the frame.
        reed_tint=(2.861, 3.403, 2.700),
        reed_plume_tint=(4.340, 5.521, 5.446),
        lily_color=(0.086, 0.132, 0.062), lily_rough=0.62,
        # [B-09-4] 0.55 → 0.42: the water-mark band was weaker than the sandstone texture variation,
        #   so the waterline was not identifiable. (The contrast amount is kept identical after the stone swap.)
        # [v7] contrast ratio preserved for the same reason: old 0.42/0.90 = 0.467 → 0.64×0.467 = 0.299
        # [W3 P09 · GT-41 (2)] × 0.818 again. stain/stone 0.4672 → **0.4676** [computed].
        #   This is the tint the **waterline band** and the kit's **joint** lines both bind to
        #   (`build_ground_kit` M2: `joint=M["stain"]`), so holding the ratio holds the joint
        #   grid's legibility at the same time as the drop anchor's.
        # [GT-126] × 0.850 with the paving. stain/stone 0.4676 → **0.4674** [computed] — the
        #   band `from_river` measured at exactly its authored hue (R/B 1.20) keeps both its
        #   hue and its contrast against the darkened stone.
        stain_tint=(0.208, 0.208, 0.183),      # was (0.245,0.245,0.215) ← (0.299,0.299,0.263)
        # [W3 P09 · GT-41 (1)] 판석 디딤돌. A lawn-set stepping stone is a **different stone lot**
        #   from the sawn promenade slab beside it — soil splash and mower wear take it a shade
        #   down and a shade greyer. 0.92× the paving tint keeps it in the same albedo family
        #   (so `albedo_selfcheck` governs it) while separating it from the paving at 20 m.
        # [GT-126] × 0.850 with the paving — the 0.92× family relation holds
        #   (0.9199 → **0.9213** [computed]).
        stepstone_tint=(0.410, 0.403, 0.384),  # was (0.482,0.474,0.452)
        # [GT-115 ⑨ (4)] 계선주. The four terrace posts were bound to `M["stone"]`, i.e. the
        #   promenade's `plaza_light` map — a **running-bond slab grid**, measured in
        #   `pt_noon_across_river.png` as joint lines wrapping each shaft. A quay post is one
        #   quarried block: it has grain and it has no joints anywhere.
        #   **Map chosen by inspection of the registry, not by name** [measured, this session]:
        #   `plaza_light` 6 × 6 slabs · `granite_dark` 5 × 5 stack bond · `stone_worn` running
        #   bond · `sandstone` ashlar · `marble_light` slabs · `rock_wall` riprap — every stone
        #   role in the library carries a course pattern **except `rock_face`**, a continuous
        #   bedrock scan. That is the one that can dress a monolith.
        #   It is a warm brown (linear mean 0.159/0.118/0.083, ratio 1 : 0.743 : 0.523), so this
        #   tint carries a hue correction as well as a level — spread **1.70**, and the post is
        #   ~1 tile across at `quay_stone` 0.38, i.e. it samples the map's mean rather than one
        #   arbitrary patch, which is the condition the reed row shows must hold before a
        #   per-channel multiplier is safe. Effective albedo (0.221, 0.214, 0.197), luminance
        #   **0.214** = 0.90 × the promenade's 0.246 at the promenade's own hue ratio: a set post
        #   weathers a shade below the slab beside it, and it stays inside the 0.20–0.35 화강석
        #   band the `stone` class states [computed].
        # [GT-126] **× 0.9346, a partial factor — the two anchors above now conflict.** The
        #   promenade dropped to 0.209, so holding 0.90× exactly would land 0.188, *outside*
        #   the 0.20-0.35 band this row's own note claims; left alone at 0.214 the post comes
        #   out *lighter* than the slab beside it (1.02×) — the same inversion the drystone
        #   note forbids. The band wins (it is the class's own statement): effective luminance
        #   0.214 → **0.200**, the band floor, post/slab 0.957 — "a shade below" survives
        #   directionally. Level only; the ⑨(4) map choice and hue correction are untouched.
        #   구값 `[repro — GT-115 ⑨ (4)]`: (1.392, 1.813, 2.371)
        quay_stone_tint=(1.301, 1.694, 2.216),
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
# [GT-115 ⑨] `granite_dark` (기와지붕) and `rock_face` (계선주) join the gate — a role that is
#   bound but not listed here fails at render time instead of at the asset gate, which is the
#   whole point of `check_assets`.
ASSET_ROLES = ["plaza_light", "granite_dark", "rock_face", "grass", "wood_dark",
               "sign_info", "hdri", "mdl"]


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
    # [GT-115 ⑨] the roof is no longer a constant — it is `granite_dark` × `roof_tile_tint`,
    #   which reproduces `roof_tile_color` exactly. The row follows the material so the check
    #   keeps governing **what reaches the frame** rather than a number nothing binds any more.
    ("정자 기와지붕",         "granite_dark", "roof_tile_tint", True,  True),
    ("정자 누마루(목)",       "wood_dark",   "pav_floor_tint",  False, True),
    ("오리배 선체",           None,          "duck_color",      False, False),
    # [W3 S09] the rows the renovation adds. The dry-stone wall is a **large vertical** face
    #   (5 walls, up to 6.4 m x 1.5 m) so criterion (A) governs it and (B) does not apply;
    #   the autumn hills are large but vertical-ish masses at 70-130 m, same treatment.
    #   `far_color` leaves the table with its two boxes (row (6)).
    ("자연석 옹벽",           "plaza_light", "drystone_tint",   True,  False),
    ("자연석 옹벽 갓돌",      "plaza_light", "drystone_cap_tint", False, True),
    # [W3 P09] the 판석 디딤돌 — 10 slabs of ~0.24 m² each ≈ 2.4 m², a **small horizontal**
    #   area, so criterion (B) applies and a violation would be a WARN, not a FAIL. Listed so
    #   the new tint is governed by the same cap as everything else rather than escaping it.
    ("판석 디딤돌",           "plaza_light", "stepstone_tint",  False, True),
    ("데크 장선",             "wood_dark",   "joist_tint",      False, False),
    ("데크 기둥",             "wood_dark",   "post_tint",       False, False),
    ("가을 산능선 a(단풍)",   None,          "hill_a",          True,  False),
    ("가을 산능선 b(은행)",   None,          "hill_b",          True,  False),
    ("가을 산능선 c(원경)",   None,          "hill_c",          True,  False),
    # [GT-86] the fourth ridge tone and the bare-hillside tone. Both are large but
    #   vertical-ish masses at 85-200 m, so criterion (A) governs them and (B) does not —
    #   the same treatment the three ridge tones above already carry. The far-shore ground
    #   plates are NOT a new row: they bind `grass_tint`, which is already in this table.
    ("가을 산능선 d(상록)",   None,          "hill_d",          True,  False),
    ("원경 산체(지형 캡)",    "grass",       "shore_tint",      True,  False),
    ("물가 관목 폴백",        "grass",       "scrub_tint",      False, False),
    # [GT-115 ⑨] the reed pair and the quay posts. The plume row moves off the constant onto the
    #   map it now rides (same value, different instrument); the culm and the 계선주 are **new
    #   rows** — both are tints on a dark map, i.e. exactly the shape of parameter this check
    #   exists to keep honest, and neither was governed before.
    ("갈대 줄기",             "wood_dark",   "reed_tint",       False, False),
    ("갈대 이삭",             "wood_dark",   "reed_plume_tint", False, False),
    ("계선주(화강석)",        "rock_face",   "quay_stone_tint", False, False),
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
    # [GT-86] Privet registered — the shoreline scrub draws it, and `Holly`/`Privet` share
    #   one leaf atlas (`hollyprivet_basecolor.png`), so the verdict is literally the same
    #   measurement. Without the row the audit would have reported "계절 판정 미등록".
    "Shrub/Privet.usd":       "hollyprivet_basecolor.png",
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
    # [GT-86] the shoreline scrub joins the audit. It is massed planting on the same rule as
    #   a bed (one species per continuous run), and leaving it out would let a new row put a
    #   spring blossom on an autumn shore without the gate saying a word. One entry per
    #   distinct pool, not per segment — 13 segments draw from 3 pools.
    _plant = [(b["tag"], b["species"]) for b in PARAMS["beds"]]
    for _p in dict.fromkeys(PARAMS["far_hedge"]["pools"]):
        _plant.append(("물가관목", _p[0]))
    for b_tag, a in _plant:
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
            fails.append(f"{b_tag}:{a}({'/'.join(prob)})")
        used.append((b_tag, a, atlas or "-", ver or "-", "OK" if not prob
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


# ===========================================================================
# [C5] [W3 P09 · GT-41 (1)] 판석 디딤돌 — **one source** for the assembler and both gates.
#   `build_stepstones` extrudes this, `fov_selfcheck` excludes it from the judged cones and
#   `stepstone_selfcheck` asserts the §7.2 permission's conditions on it. A gate that
#   re-derives geometry from a *copy* of the coordinates proves nothing — the
#   `hip_roof_topology` / `views_park_vista` single-source convention, applied again.
# ===========================================================================
def stepstone_outlines():
    """Returns `[(tag, cx, cy, poly, z_top, z_bot)]`, `poly` = CCW [(x, y), ...] in world plan.

    Determinism: `np.random.RandomState(seed)`, **never `hash()`** — CPython randomises
    `hash(str)` per process, which is the S09-F3 defect that would have made the prim hash
    differ run to run. Per-vertex angle jitter is capped at `ang_var` = 12°, i.e. well under
    half the 51.4°/60° vertex spacing, so the vertex order stays monotonic and the polygon
    cannot self-intersect.
    """
    ss = PARAMS["stepstones"]
    rs = np.random.RandomState(int(ss["seed"]) & 0x7FFFFFFF)
    z_top = float(PARAMS["lawn_proud"]) + float(ss["proud"])
    z_bot = z_top - float(ss["thick"])
    out = []
    for k in range(int(ss["n"])):
        cx = float(ss["x"]) + (ss["stagger"] if k % 2 == 0 else -ss["stagger"])
        cy = float(ss["y0"]) - k * float(ss["pitch"])
        nv = int(ss["nv"][k % len(ss["nv"])])
        a0 = float(rs.uniform(0.0, 360.0))
        poly = []
        for j in range(nv):
            a = (a0 + 360.0 * j / nv
                 + float(rs.uniform(-ss["ang_var"], ss["ang_var"])))
            r = float(rs.uniform(ss["r_lo"], ss["r_hi"]))
            poly.append((cx + r * math.cos(math.radians(a)),
                         cy + r * math.sin(math.radians(a))))
        out.append((f"S{k}", cx, cy, poly, z_top, z_bot))
    return out


def _poly_aabb(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def stepstone_selfcheck(verbose=True):
    """[W3 P09 · GT-41 (1)] The stepping-stone permission, asserted from the shipped
    coordinates instead of from a paragraph. No render, no boot. Five conditions:

      (a) **sub-threshold** — proud above the mown lawn < `ground_kit.GT_DELTA` (0.020).
          Read from the imported constant, so a later `GT_DELTA` edit re-decides this
          scene automatically instead of leaving a stale number in a comment.
      (b) **irregular outline** — `nv >= 5` (a rectangle is impossible) **and** a radius
          spread >= 0.04 m about the slab centre (a *regular* n-gon is impossible too:
          `sc.add_disc` would have produced one, and a machined disc is not a 판석).
      (c) **in the lawn** — every slab's plan AABB lies wholly inside one lawn band, so no
          slab overhangs onto the granite promenade where it would be a trip lip on a
          walked surface instead of a stone in turf.
      (d) **clear of the boardwalk** — >= 0.10 m in plan from every leg footprint. The
          route's whole purpose is to arrive at leg L1; arriving *inside* it would be an
          interpenetration, not an arrival.
      (e) **clear of the park trees** — >= 1.00 m from every trunk station. This is the
          gate that keeps `x = -14.6` honest: the obvious `x = -13` line runs straight
          through the tree at (-13.0, -17.8).
    """
    ss = PARAMS["stepstones"]
    stones = stepstone_outlines()
    proud = float(ss["proud"])
    rows, bad = [], []
    gt_delta = float(gk.GT_DELTA)
    ok_a = proud < gt_delta
    if not ok_a:
        bad.append("(a) 문턱")
    lawns = [(lw["x0"], lw["y0"], lw["x1"], lw["y1"]) for lw in PARAMS["lawns"]]
    legs = [(x0, y0, x1, y1)
            for _t, x0, y0, x1, y1, _ax in PARAMS["boardwalk"]["legs"]]
    trees = list(PARAMS["park_trees"])
    for tag, cx, cy, poly, z_top, _z_bot in stones:
        x0, y0, x1, y1 = _poly_aabb(poly)
        radii = [math.hypot(px - cx, py - cy) for px, py in poly]
        spread = max(radii) - min(radii)
        ok_b = len(poly) >= 5 and spread >= 0.04
        ok_c = any(lx0 <= x0 and x1 <= lx1 and ly0 <= y0 and y1 <= ly1
                   for lx0, ly0, lx1, ly1 in lawns)
        d_leg = min(_rect_gap(x0, y0, x1, y1, *lg) for lg in legs)
        ok_d = d_leg >= 0.10
        d_tree = min(_rect_gap(x0, y0, x1, y1, tx, ty, tx, ty)
                     for tx, ty in trees)
        ok_e = d_tree >= 1.00
        if not (ok_b and ok_c and ok_d and ok_e):
            bad.append(tag)
        rows.append((tag, len(poly), spread, ok_b, ok_c, d_leg, ok_d,
                     d_tree, ok_e))
    ok = ok_a and not bad
    if verbose:
        print("=" * 68)
        print("scene09 [W3 P09] 판석 디딤돌 허가 조건 검산 (렌더 없음)")
        print("=" * 68)
        print(f"  (a) 문턱 이하   잔디면 위 노출 {proud * 1000:.0f} mm "
              f"< GT_DELTA {gt_delta * 1000:.0f} mm  "
              f"{'OK' if ok_a else 'FAIL'}   "
              f"[상면 z {stones[0][4]:.3f} · 두께 {ss['thick'] * 1000:.0f} mm]")
        for tag, nv, sp, ok_b, ok_c, dl, ok_d, dt, ok_e in rows:
            print(f"  {tag:4s} 꼭짓점 {nv} · 반지름 편차 {sp * 1000:5.1f} mm "
                  f"{'OK' if ok_b else 'FAIL'} · 잔디밭 내부 "
                  f"{'OK' if ok_c else 'FAIL'} · 데크 이격 {dl:5.3f} m "
                  f"{'OK' if ok_d else 'FAIL'} · 수목 이격 {dt:5.2f} m "
                  f"{'OK' if ok_e else 'FAIL'}")
        print(f"  ⇒ {'OK — 허가 조건 위반 0건' if ok else 'FAIL: ' + str(bad)}")
        print("=" * 68)
    return ok, rows


def _rect_gap(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1):
    """Plan gap between two axis-aligned rects (0.0 if they overlap or touch)."""
    dx = max(bx0 - ax1, ax0 - bx1, 0.0)
    dy = max(by0 - ay1, ay0 - by1, 0.0)
    return math.hypot(dx, dy)


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
    # [W3 P09] the 판석 디딤돌 route, as **one** footprint: the slabs are a single element
    #   for this test (they are collinear on 0.57 m centres, so the union's nearest corner
    #   is the binding one and per-slab rows would be ten copies of the same answer).
    _sx0, _sy0, _sx1, _sy1 = 1e9, 1e9, -1e9, -1e9
    for _t, _cx, _cy, _poly, _zt, _zb in stepstone_outlines():
        _a0, _b0, _a1, _b1 = _poly_aabb(_poly)
        _sx0, _sy0 = min(_sx0, _a0), min(_sy0, _b0)
        _sx1, _sy1 = max(_sx1, _a1), max(_sy1, _b1)
    items.append(("판석 디딤돌 10", _sx0, _sy0, _sx1, _sy1))
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


# [GT-86] Both horizon gates derate the declared crest to **0.85 h** before measuring.
#   `h` is the crest a ridge's TALLEST crowns reach; the continuous skyline a viewer sees is
#   the p90 of the crown draw, measured at 0.85 h over the 977 crowns this table ships
#   [measured, replaying the assembler's own RandomState]. Asserting against the maximum
#   would be asserting against a silhouette made of a handful of spires.
_CREST_KEEP = 0.85


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
        # [GT-86] `dx > 0` guard. GT-86 adds two flanking shore ridges whose near face is at
        #   x = -35, i.e. **behind** both water eyes; `atan2(+dz, -dx)` returns ~+166 deg for
        #   them and the max would have been a meaningless number that always passes. Only
        #   masses in front of the eye can close the horizon in front of the eye.
        e_new = max((math.degrees(math.atan2(
            fb_z + h["h"] * _CREST_KEEP - ez, (h["cx"] - h["sx"] / 2.0) - ex))
            for h in PARAMS["far_hills"]
            if (h["cx"] - h["sx"] / 2.0) - ex > 0.0), default=-90.0)
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
# [C6] [GT-86] far-shore terrain — **one source** for the assembler and the gate.
#   `build_far_shore` extrudes this table, `build_far_hills` seats every ridge and clamps
#   every crown against it, and `backdrop_selfcheck` proves the two claims the user's
#   verdict turns on. A gate that re-derives the ground from a copy proves nothing — the
#   `hip_roof_topology` / `stepstone_outlines` single-source convention, applied again.
# ===========================================================================
def shore_plates():
    """`[(tag, x0, y0, x1, y1, top_z, thick)]` — the far-shore terrain, tiled with **no plan
    overlap**. Two plates that overlap in plan at the same top z would z-fight along the
    shared face; two plates that merely touch cannot. Ordered near-to-far for readability;
    `shore_top_at` returns the first hit, and the tiling makes 'first' unambiguous."""
    _s, _b, _z, water_z, _h = compute_steps()
    fb, fs = PARAMS["far_bank"], PARAMS["far_shore"]
    fz = water_z + fb["above_water"]           # far-bank top face  [computed -3.590]
    rz = fz + fs["rise"]                       # rear plate top; rise 0.0 -> the same -3.590
    ts, tr = fs["thick_side"], fs["thick_rear"]
    return [("BankS", fb["x0"], -fs["lake_y"], fs["rear_x0"], fb["y0"], fz, ts),
            ("BankN", fb["x0"], fb["y1"], fs["rear_x0"], fs["lake_y"], fz, ts),
            ("Rear", fs["rear_x0"], -fs["lake_y"], fs["x1"], fs["lake_y"], rz, tr),
            ("SideS", fs["x_west"], -fs["edge_y"], fs["x1"], -fs["lake_y"], fz, ts),
            ("SideN", fs["x_west"], fs["lake_y"], fs["x1"], fs["edge_y"], fz, ts)]


def shore_plate_at(x, y):
    """The plate a point stands on, or None. Boundaries are inclusive on both plates; a
    ridge is only ever declared inside one of them (asserted by `backdrop_selfcheck`)."""
    for row in shore_plates():
        if row[1] <= x <= row[3] and row[2] <= y <= row[4]:
            return row
    return None


def shore_top_at(x, y, default=None):
    """Terrain top z at (x, y) on the far shore. `default` covers the far bank itself, whose
    plate is `far_bank` and whose top face is the datum every other plate is measured from.
    Callers pass `fb_z` — a planting station inside the bank rectangle then keeps the
    bank's own top face and nothing moves."""
    row = shore_plate_at(x, y)
    return float(row[5]) if row is not None else default


def _ray_box_near(ex, ey, ux, uy, x0, x1, y0, y1):
    """Nearest positive distance at which the ray is inside the plan box (slab test).
    None when it never enters."""
    tmin, tmax = 0.0, 1e18
    for a, u, lo, hi in ((ex, ux, x0, x1), (ey, uy, y0, y1)):
        if abs(u) < 1e-12:
            if a < lo or a > hi:
                return None
        else:
            t1, t2 = (lo - a) / u, (hi - a) / u
            if t1 > t2:
                t1, t2 = t2, t1
            tmin, tmax = max(tmin, t1), min(tmax, t2)
    return tmin if tmax >= tmin else None


def _ground_exit(ex, ey, ux, uy, step=1.0, far=440.0):
    """Distance at which the ray last stands over covered ground (shore plate, far bank or
    water plate). Marched rather than solved: the covered region is a union of five plates
    plus the bank and the lake, and a march is the honest way to say 'the last one'."""
    fb, wt = PARAMS["far_bank"], PARAMS["water"]
    _s, _b, _z, water_z, _h = compute_steps()
    wx0 = _s[PARAMS["stairs"]["nsteps"]
             - PARAMS["stairs"]["submerge_from_bottom"]][0]
    fz = water_z + fb["above_water"]
    last, t = None, step
    while t < far:
        x, y = ex + ux * t, ey + uy * t
        p = shore_plate_at(x, y)
        if p is not None:
            last = (t, p[5])
        elif fb["x0"] <= x <= fb["x1"] and fb["y0"] <= y <= fb["y1"]:
            last = (t, fz)
        elif wx0 <= x <= wt["x_far"] and wt["y0"] <= y <= wt["y1"]:
            last = (t, water_z)
        t += step
    return last


# The cuts that look INTO the backdrop. `across_river` / `from_river` / `stair_flank_*` are
#   excluded because they face the ghat (-X): the backdrop is behind them, and closing it
#   there is `horizon_selfcheck`'s job, not this gate's.
_BACKDROP_CAM_NAMES = ("g9_oblique", "park_vista", "preset_h1.8_d10",
                       "preset_h0.3_d2", "waterline")
_BACKDROP_HALF_FOV = 30.0


def _backdrop_cams():
    """`[(name, eye, tgt)]` read out of **`build_views()` itself**, not re-typed here. A gate
    that keeps its own copy of the eye coordinates silently stops tracking the camera the
    day someone re-aims it; this one cannot."""
    steps, _bz, z_bot, water_z, _bh = compute_steps()
    wx0 = steps[PARAMS["stairs"]["nsteps"]
                - PARAMS["stairs"]["submerge_from_bottom"]][0]
    v = build_views(steps[-1][1], z_bot, water_z, wx0)
    return [(n, tuple(v[n]["eye"]), tuple(v[n]["tgt"]))
            for n in _BACKDROP_CAM_NAMES if n in v]
# The outer 8 % of frame width on each side is not sampled. At those bearings every cut in
#   this scene already looks past the lake into the dome (the void ring x < 11.92 / |y| > 40
#   beside the ghat is pre-existing and is not this row's to close), so asserting there
#   would be asserting against the baseline rather than against this change. [measured]
_BACKDROP_EDGE_SKIP = 0.08


def backdrop_selfcheck(verbose=True):
    """[GT-86] The two claims the user's verdict turns on, asserted from the shipped
    coordinates with no render. Returns (ok, rows).

      (A) **GROUNDED** — every ridge footprint, grown by its own crown radius, lies wholly
          inside ONE terrain plate, and its base sits on that plate's top face. This is the
          direct statement of "no mass hangs over water or sky": a mass that cannot leave
          its plate cannot have a bottom face against the sky. (The assembler additionally
          clamps each crown centre to the same rect inset by its own radius, so the
          guarantee holds per crown, not just per footprint.)
      (B) **CLOSED** — for every backdrop camera and every sampled bearing across its frame,
          some ridge in front subtends a HIGHER elevation than the terrain's own far edge
          along that bearing. That is exactly "the sky meets a treeline, never a bare ground
          edge", and it is what `far_hills` exists for. Reported as a margin in degrees; the
          worst margin is the number to watch between rounds.
    """
    plates = shore_plates()
    rows_a, bad = [], []
    for i, h in enumerate(PARAMS["far_hills"]):
        r = float(h["cr"])
        x0, x1 = h["cx"] - h["sx"] / 2.0 - r, h["cx"] + h["sx"] / 2.0 + r
        y0, y1 = h["cy"] - h["sy"] / 2.0 - r, h["cy"] + h["sy"] / 2.0 + r
        hit = next((p for p in plates
                    if p[1] <= x0 and x1 <= p[3] and p[2] <= y0 and y1 <= p[4]),
                   None)
        m = 0.0 if hit is None else min(x0 - hit[1], hit[3] - x1,
                                        y0 - hit[2], hit[4] - y1)
        if hit is None:
            bad.append(f"Hill_{i}(지면 밖)")
        rows_a.append((i, hit[0] if hit else "-", m, hit is not None))
    rows_b = []
    for name, eye, tgt in _backdrop_cams():
        ex, ey, ez = eye
        az0 = math.degrees(math.atan2(tgt[1] - ey, tgt[0] - ex))
        worst, worst_az, n = 1e9, None, 41
        for k in range(n):
            f = k / (n - 1.0)
            if f < _BACKDROP_EDGE_SKIP or f > 1.0 - _BACKDROP_EDGE_SKIP:
                continue
            az = az0 - _BACKDROP_HALF_FOV + 2.0 * _BACKDROP_HALF_FOV * f
            ux = math.cos(math.radians(az))
            uy = math.sin(math.radians(az))
            ge = _ground_exit(ex, ey, ux, uy)
            if ge is None:
                continue
            te, zg = ge
            e_edge = math.degrees(math.atan2(zg - ez, te))
            e_mass = -90.0
            for h in PARAMS["far_hills"]:
                tn = _ray_box_near(ex, ey, ux, uy,
                                   h["cx"] - h["sx"] / 2.0, h["cx"] + h["sx"] / 2.0,
                                   h["cy"] - h["sy"] / 2.0, h["cy"] + h["sy"] / 2.0)
                if tn is None or tn <= 0.5 or tn >= te:
                    continue
                p = shore_plate_at(h["cx"], h["cy"])
                top = (p[5] if p else 0.0) + h["h"] * _CREST_KEEP
                e_mass = max(e_mass,
                             math.degrees(math.atan2(top - ez, tn)))
            if e_mass - e_edge < worst:
                worst, worst_az = e_mass - e_edge, az
        okc = worst > 0.0
        if not okc:
            bad.append(f"{name}(지평 열림)")
        rows_b.append((name, worst, worst_az, okc))
    ok = not bad
    if verbose:
        print("=" * 68)
        print("scene09 [GT-86] 원경 배경 접지·지평 검산 (렌더 없음)")
        print("=" * 68)
        print("  (A) 접지 — 능선 발자국+수관반경이 지형판 안에 있는가")
        for i, tag, m, okr in rows_a:
            print(f"    Hill_{i:<2d} 지형판 {tag:6s} 가장자리 여유 {m:6.2f} m  "
                  f"{'OK' if okr else 'FAIL(허공)'}")
        print("  (B) 폐합 — 프레임 방위별 [능선 고도 − 지형 끝단 고도]")
        for name, w, az, okr in rows_b:
            print(f"    {name:16s} 최악 여유 {w:+6.2f}° @방위 "
                  f"{(f'{az:+7.2f}' if az is not None else '   n/a')}  "
                  f"{'OK' if okr else 'FAIL(하늘이 맨땅 끝단과 만난다)'}")
        print(f"  ⇒ {'OK — 허공 부양 0건 · 지평 열림 0건' if ok else 'FAIL: ' + str(bad)}")
        print("=" * 68)
    return ok, rows_a + rows_b


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
    #   **Handedness, corrected against the first render rather than against the arithmetic.**
    #   The bearing table above was first written for an eye on the **+Y** side, on the reading
    #   that a positive bearing offset puts an element on the right of frame (the `park_vista`
    #   comment says so in as many words: *"duck boat +20.6 deg → right side"*). The first
    #   `g9_oblique` render at eye (−20, **+36**, 13) came back **mirrored** — water filling the
    #   LEFT, terrace on the right — so that reading is wrong for a camera looking south, and the
    #   note it came from is only true for park_vista's own sense. Measured, not re-derived: the
    #   eye moves to the **−Y** side and the target's y flips with it, which puts the −Y terraced
    #   beds and the boardwalk in the left foreground and the water, far bank and autumn ridge on
    #   the right — G9's layout. The magnitudes in the table above are unchanged (the geometry is
    #   symmetric about y = 0 in everything this cut frames); only the sign of y is.
    views["g9_oblique"] = dict(eye=[-20.0, -36.0, 13.0], tgt=[9.0, 1.0, 0.0])
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
        (신설 요소 전부 ±30° 밖 — `fov_selfcheck`)
15. [W3 P09 · GT-41] 톤 + 디딤돌
    (1) 석재 톤 — h0.3 세 컷의 포장이 순백(wht% 65 · mean 205)에서 내려왔는가.
        물때(수위선) 밴드와 줄눈 대비는 **비가 보존됐으므로** 그대로여야 한다.
        자연석 옹벽이 포장보다 **어둡게** 남아 있는가 (0.86배 관계 유지)
    (2) 판석 디딤돌 — `g9_oblique` 좌하단 잔디밭에서, **모서리가 직각이 아닌**
        부정형 판석 10장이 잔디에 박혀 보드워크 L1 끝단으로 이어지는가.
        데칼이 아니라 **두께 120 mm 의 돌**로 보이는가 (측면 그림자)"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
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
        # [W3 P09] the 판석 디딤돌 permission gate (GT-41 (1)).
        ok6, _ = stepstone_selfcheck()
        # [GT-86] the backdrop grounding + skyline-closure gate.
        ok7, _ = backdrop_selfcheck()
        sys.exit(0 if (ok1 and ok2 and ok3 and ok4 and ok5 and ok6 and ok7)
                 else 1)

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
        # [W3 P09 · GT-41 (1)] 판석 디딤돌 — the same granite texture at its own tone
        #   (`stepstone_tint`). Texture scale 0.75× the promenade's: a slab is ~0.55 m across
        #   and the promenade's 1.1 m granite cell would put **less than half a cell** on a
        #   whole stone, i.e. no visible stone character at all.
        M["stepstone"] = tex("plaza_light", "/World/Looks/StepStone",
                             sca["stone"] * 0.75, tint=mp["stepstone_tint"])
        # [GT-115 ⑨ (4)] 계선주 — a monolith, so a **joint-free** map (`rock_face`; the survey of
        #   every stone role is in the `quay_stone_tint` note). `QuayStone` classifies `stone`
        #   through the keyword rule, so the post keeps the stone class's weathering, bevel and
        #   0.34 albedo ceiling; only the slab grid is gone.
        M["quay_stone"] = tex("rock_face", "/World/Looks/QuayStone",
                              sca["quay_stone"], tint=mp["quay_stone_tint"])
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
        # [GT-115 ⑨ (3)] path renamed `PavFloor` → **`PavFloorPlank`**. Not cosmetic: the keyword
        #   classifier tests **wood** (rule 8) before **paving** (rule 16), and `PavFloor` carries
        #   no wood token, so the 누마루 was landing in `paving` on the strength of "pav" — a
        #   *ground* MDL route with a concrete detail normal and a mineral bevel on a timber
        #   floor, and (with `sx`,`sy` ≥ 4 m and `sz` 0.23) a `_ground_skin` micro-relief mesh on
        #   top of it. "plank" puts it in `wood`, which is where this file already puts the
        #   boardwalk (`Looks/Deck`, `Looks/Joist`) — one class for one material family.
        #   Declared consequence: **−1 prim** in the LOOK_GEO arm (the skin), and `bump` is passed
        #   explicitly because the omni route takes it from the call, not from the class.
        M["pav_floor"] = tex("wood_dark", "/World/Looks/PavFloorPlank",
                             sca["wood_fine"], tint=mp["pav_floor_tint"],
                             bump=1.3)
        # [v8 Y1] specular_level=0.0 — the **cause** of the near-white roof. Left unset,
        #   OmniPBR defaults to 0.5 (F0 0.04) and the wide GGX lobe at roughness 0.72
        #   caught the sun plus sky on the +Y roof faces (N·H 0.78) along the park_vista sight line,
        #   adding a linear +0.164 on top of the diffuse. Every other matte material in this scene
        #   (reed/far/canopy_a/canopy_b) is 0.0 — only pav_roof was missing it.
        # [GT-115 ⑨ (5)] the constant is replaced by `granite_dark` × `roof_tile_tint`, which
        #   reproduces the same declared albedo (see the PARAMS note) while taking the material
        #   **out of the promoter's hands** — as a constant in the `paving` class it was being
        #   given `paving_interlock`, i.e. pavement blocks on a hip roof. `specular_level` 0.0 is
        #   unchanged and still the v8 Y1 fix; `roughness_const` now actually lands (the promotion
        #   path dropped it — `scene_common:1576` passes `roughness_const=None`), so the matte
        #   0.72 the v8 row declared is authored for the first time.
        M["pav_roof"] = sc.make_pbr(stage, "/World/Looks/PavRoof",
                                    sc.tex_path("granite_dark", "diff"),
                                    sc.tex_path("granite_dark", "nor"),
                                    None, sca["roof_tile"],
                                    tint=mp["roof_tile_tint"],
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
        # [GT-115 ⑨ (7)] the seat well. `Looks/Duck*` classifies `metal` (the keyword list owns
        #   "duck"), which is **outside** `_CONST_MDL_CLASSES` — so this one legitimately stays a
        #   constant colour, like the hull and the canopy it sits between.
        #   Named `DuckCockpit` and **not** `DuckSeat`: "sea" is a `water`-rule token and it is a
        #   substring of "seat", so a seat material would have been metered as water (rule 6 is
        #   tested before rule 7). Verified against `_look_spec` before it was written.
        M["duck_seat"] = sc.make_pbr(stage, "/World/Looks/DuckCockpit",
                                     diffuse_color=mp["duck_seat_color"],
                                     roughness_const=mp["duck_seat_rough"],
                                     specular_level=0.0)
        # [GT-115 ⑨ (1)] the culm and its seed head. Both were constants in the `veg` class and
        #   both were therefore promoted to `grass_lawn` at a 1.4 m tile with a ×5.46 blue
        #   multiplier — the pink-lilac rods and the navy joint gap in the shipped cut (see the
        #   `reed_tint` note for the measurement). Binding `wood_dark` here keeps the declared
        #   browns, flattens the multiplier to a 1.26 spread and puts the grain **along** the
        #   culm at a tile shorter than the stem. `specular_level` 0.0 is unchanged (v8 Y1: every
        #   matte material in this scene states it).
        #   The roughness **map is deliberately not bound**: `tex()` would also author
        #   `reflection_roughness_texture_influence = 1.0`, which overrides the constant, and
        #   `reed_rough` 1.0 (fully matte) is a declared value of this scene, not an accident.
        M["reed"] = sc.make_pbr(stage, "/World/Looks/Reed",
                                sc.tex_path("wood_dark", "diff"),
                                sc.tex_path("wood_dark", "nor"),
                                None, sca["reed"], tint=mp["reed_tint"],
                                roughness_const=mp["reed_rough"],
                                specular_level=0.0, bump=1.1)
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        # [GT-86] the emerged landform caps (bare hillside under the canopy) and the
        #   procedural fallback tone for the shoreline scrub. Both ride the grass texture at
        #   a 2.4x coarser world scale: at 80-150 m the promenade-scale tiling turns into
        #   uniform noise, and the coarser cell keeps a legible grain instead [computed].
        M["shore"] = tex("grass", "/World/Looks/Shore", sca["grass"] * 2.4,
                         tint=mp["shore_tint"])
        M["scrub"] = tex("grass", "/World/Looks/Scrub", sca["grass"],
                         tint=mp["scrub_tint"])
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
                                      sc.tex_path("wood_dark", "diff"),
                                      sc.tex_path("wood_dark", "nor"),
                                      None, sca["reed"],
                                      tint=mp["reed_plume_tint"],
                                      roughness_const=mp["reed_plume_rough"],
                                      specular_level=0.0, bump=1.1)
        M["lily"] = sc.make_pbr(stage, "/World/Looks/Lily",
                                diffuse_color=mp["lily_color"],
                                roughness_const=mp["lily_rough"],
                                specular_level=0.0)
        for _k in ("hill_a", "hill_b", "hill_c", "hill_d"):   # [GT-86] +hill_d
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
        build_far_shore(M)
        # [GT-86] shoreline scrub — one `place_hedge_row` per segment (real shrub USD,
        #   instanced; legacy `build_hedge` under the same prim root when the assets are
        #   absent, so the degradation contract is unchanged). The runs are broken and the
        #   heights uneven: the old 3-run clipped band read as a line of identical balls.
        fh = PARAMS["far_hedge"]
        pools = fh["pools"]
        n_sh = 0
        for i, h in enumerate(PARAMS["far_hedges"]):
            base = shore_top_at(h["cx"], h["cy"], fb_z)
            n_sh += sc.place_hedge_row(
                stage, f"{ROOT}/FarHedge_{i}",
                h["cx"] - fh["w"] / 2.0, h["cy"] - h["L"] / 2.0,
                h["cx"] + fh["w"] / 2.0, h["cy"] + h["L"] / 2.0,
                float(h["h"]), int(fh["seed"]) + 17 * i,
                pool=list(pools[int(h["sp"]) % len(pools)]), base_z=base,
                overlap=float(fh["overlap"]), end_margin=float(fh["end_margin"]),
                fallback_mtl=M["scrub"])
        print(f"[원경] 물가 관목 {len(PARAMS['far_hedges'])}구간 · 실관목 {n_sh}주 "
              f"(0 = 절차적 폴백)")
        # [W3 S09 · row (7)] **belt species declared.** `SCENE_SPECIES["Scene09"]` is
        #   `("birch", "oak_black")` and the belt half has been inert since K4(b) landed —
        #   `resolve_species` only reaches it when a call passes `belt=True`, and no scene09
        #   call did (**K4-F4**: the belts registered for 03 / 09 / 17 "stay inert until you
        #   pass species="). The far-bank stand is exactly what a belt is for: a *different*
        #   species at a distance where its crown cannot roof the walked corridor
        #   (`sc.TREE_BANDS["belt"]`, d_min 7.50 — this row is 44 m away across water).
        #   The route trees on the terrace keep the scene default (`birch`), so the two bands
        #   are now genuinely two species instead of one repeated.
        #   [GT-86] `trunk_h=t["th"]` — the call used to take the 2.2 m DEFAULT, so the whole
        #   stand was 3.52 m tall behind a 3.6 m hedge and never appeared in a cut. Ground
        #   z is read from the terrain table, not assumed to be `fb_z`, because the stand now
        #   runs out to |y| 90 where the shoreline is a `BankS/BankN` plate.
        for i, t in enumerate(PARAMS["far_trees"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", t["cx"], t["cy"],
                          shore_top_at(t["cx"], t["cy"], fb_z),
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_h=float(t["th"]), belt=True)
        print(f"[원경] 물가 수림 {len(PARAMS['far_trees'])}주 "
              f"(수고 {min(t['th'] for t in PARAMS['far_trees']) * 1.60:.1f}~"
              f"{max(t['th'] for t in PARAMS['far_trees']) * 1.60:.1f} m · belt 종)")
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
        # [GT-115 ⑨ (5)] **절병통 stack, not a drum.** One cylinder of constant radius reads as a
        #   chimney on the ridge (measured in `260806_w3_allview5/pt_noon_across_river.png`), and
        #   the analytic `UsdGeom.Cylinder` tessellates at Hydra's low default, which is what puts
        #   the flat sides on it. `add_disc` is the library's answer to exactly that (32-gon,
        #   `scene_common.DISC_SEGMENTS`), and stacking five of them at the declared radii gives
        #   the turned profile a 절병통 actually has. Heights are fractions of `finial_h`, so the
        #   total is still 0.42 and the tip still lands at 4.71 — no other number moves.
        #   The **first member keeps the path `{P}/Finial`**, so the smoke run's material-binding
        #   probe (which reads that exact path) is untouched.
        _fz = z_ap
        for _tag, _hf, _rm in p["finial_stack"]:
            _fh = p["finial_h"] * float(_hf)
            sc.add_disc(stage, f"{P}/Finial{'_' + _tag if _tag else ''}",
                        (cx, cy, _fz + _fh / 2.0),
                        p["finial_r"] * float(_rm), _fh, M["pav_roof"])
            _fz += _fh
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

    def build_stepstones(M):
        """[W3 P09 · GT-41 (1)] 판석 디딤돌 — one irregular prism mesh per slab.

        **Why it is not `sc.add_box`**: a box is a rectangle, and §7.2's permission is
        explicitly conditional on *"irregular outlines preferred"*. **Why it is not
        `sc.add_disc`**: that is a *regular* n-gon — a machined disc, which is what a
        원형 디딤돌 is and not what a 판석 is. So the slab is authored here from
        `stepstone_outlines()`, exactly the way `build_hip_roof` authors the pavilion roof:
        side quads + two n-gon caps, `subdivisionScheme="none"` so the faceted outline
        survives (catmullClark would round every slab into a pebble), winding taken from
        the CCW plan ring so the side normals point outward — the `sc.add_disc` topology,
        with the ring made irregular.

        `collider=False`, and the reason is GT-41's z-profile cell: the lawn box underneath
        is already `collider=True` with its top face 12 mm lower, so the walkable surface
        exists and does not move by more than `GT_DELTA`. Adding 10 collision boxes to buy
        12 mm of relief would change the hazard/collision box list, which is a different
        declaration from the element-AABB one this row makes.
        """
        from pxr import UsdGeom, Gf
        P = f"{ROOT}/StepStones"
        n = 0
        for tag, _cx, _cy, poly, z_top, z_bot in stepstone_outlines():
            nv = len(poly)
            pts = ([Gf.Vec3f(float(x), float(y), float(z_bot))
                    for x, y in poly]
                   + [Gf.Vec3f(float(x), float(y), float(z_top))
                      for x, y in poly])
            counts, idx = [], []
            for k in range(nv):                       # side quads, outward
                counts.append(4)
                idx += [k, (k + 1) % nv, (k + 1) % nv + nv, k + nv]
            counts.append(nv)                         # top cap (+Z)
            idx += list(range(nv, 2 * nv))
            counts.append(nv)                         # bottom cap (−Z)
            idx += list(range(nv - 1, -1, -1))
            x0, y0, x1, y1 = _poly_aabb(poly)
            m = UsdGeom.Mesh.Define(stage, f"{P}/Slab_{tag}")
            m.CreatePointsAttr(pts)
            m.CreateFaceVertexCountsAttr(counts)
            m.CreateFaceVertexIndicesAttr(idx)
            m.CreateSubdivisionSchemeAttr("none")
            m.CreateExtentAttr([Gf.Vec3f(float(x0), float(y0), float(z_bot)),
                                Gf.Vec3f(float(x1), float(y1), float(z_top))])
            sc._bind_mtl(m.GetPrim(), M["stepstone"])
            n += 1
        return n

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
        for i, (aid, tag, u, v, th, yaw, sink) in enumerate(
                PARAMS["bed_features"]):
            b = _bed_at(tag)
            if b is None:
                continue
            px = b["x0"] + (b["x1"] - b["x0"]) * float(u)
            py = b["y0"] + (b["y1"] - b["y0"]) * float(v)
            pz = float(b["top"]) - soil_drop
            try:
                # `z_mode="base"` + a declared bed depth. Measured live on this run, the default
                #   `grade` mode buries these rows: `tree_stump_01` carries **38.9 %** of its
                #   triangles below its own origin (zmin −0.193 m) and `rock_moss_set_01`
                #   **52.4 %** (zmin −0.661 m) — urban_kit prints both warnings and tells the
                #   caller exactly this. `z_mode="base"` puts the lowest geometry on the z given,
                #   so the bed depth is simply subtracted here.
                # [GT-115 ⑨ (6)] the depth is **`sink` × the feature's own height**, not a flat
                #   0.10 m. At 0.10 the three boulders were bedded 13–18 % and read as laid on
                #   the mown surface (`pt_noon_park_vista.png`); a Korean 조경석 is set with about
                #   a third of its height in the ground, which is also what stops it reading as
                #   a prop. The stump keeps its shallow value — G9's root feature sits **on** its
                #   moss bed and a third of 1.25 m would delete it.
                uk.add_urban_asset(stage, f"{ROOT}/Bed_{tag}/Feat_{i}", aid,
                                   pos_m=(px, py, pz - float(th) * float(sink)),
                                   yaw_deg=float(yaw),
                                   target_h=float(th), scene="09", z_mode="base",
                                   instanceable=True, treatment="mtlxoff")
                n += 1
            except Exception as e:
                print(f"[urban][경고] {aid} 배치 실패({tag}): {e}")
        print(f"[화단 특징물] 그루터기/이끼바위 {n}점 (T4b mtlxoff 래퍼 · instanceable)")
        return n

    def build_far_shore(M):
        """[GT-86] The far-shore terrain — five plates from `shore_plates()`.

        Why it exists: `far_hills` ran to x 141 / y -120..+132 while the only ground out
        there was `far_bank` (x 44..74, y +-40), so every ridge outside that rectangle stood
        on nothing and showed its cut bottom against the sky. This is that ground.
        `collider=False` throughout — no body reaches 100 m of open water, and a backdrop row
        may not change the hazard/collision box list."""
        n = 0
        for tag, x0, y0, x1, y1, tz, th in shore_plates():
            # All five carry `grass`, the same material as `FarBank`: the plates butt at one
            #   elevation, so a second tone here would put a straight seam across an
            #   otherwise continuous shoreline. Aerial perspective is carried by the ridge
            #   tone mix instead, where it belongs.
            sc.add_box(stage, f"{ROOT}/FarShore_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, tz - th / 2.0),
                       (x1 - x0, y1 - y0, th), M["grass"], collider=False)
            n += 1
        print(f"[원경] 원안 지형판 {n}장 (x {PARAMS['far_shore']['x_west']:.0f}~"
              f"{PARAMS['far_shore']['x1']:.0f} · |y| ≤ "
              f"{PARAMS['far_shore']['edge_y']:.0f} · 맞댐이음 단차 "
              f"{PARAMS['far_shore']['rise'] * 1000:.0f} mm · 비충돌)")

    def _lobe_surface(lobes, x, y, base):
        """Landform surface z at (x, y): the highest emerged ellipsoid cap, or the terrain
        top where no cap reaches. Analytic, so a crown can be seated on the slope it stands
        on instead of on a nominal ridge height."""
        z = base
        for lx, ly, lz, rx, ry, rz in lobes:
            u = ((x - lx) / rx) ** 2 + ((y - ly) / ry) ** 2
            if u < 1.0:
                z = max(z, lz + rz * math.sqrt(1.0 - u))
        return z

    def build_far_hills(M):
        """[GT-86] The autumn hillside backdrop, rebuilt **grounded and de-ballooned**.

        Two structural changes against the row it replaces (W3 S09 row (6)):

        (1) **No body box.** The old ridge was `add_box(h*0.30)` under a row of blobs, and at
            11-19 m tall the box was never covered: its flat bottom face and its raw end
            walls are the "slab floating over the waterline" in `pt_noon_g9_oblique.png`.
            The landform is now `lobes` flattened ellipsoids whose centre sits `sink` of
            their own z radius BELOW the terrain top, so only a cap emerges. A buried cap
            has no bottom face and no end wall — the defect is removed by construction, not
            by hiding it.
              cap height = rz * (1 - sink)             -> rz = land_h / (1 - sink)
              cap radius = r * sqrt(1 - sink^2)        -> r  = wanted / sqrt(1 - sink^2)
            Both identities are applied below rather than tuned by eye, and `lobe_span` /
            `lobe_r` / `lobe_w` are sized off them so the emerged landform reaches its own
            footprint edge and stops there [computed].

        (2) **Crowns at tree scale.** The old crown was 12.4-23.9 m across, which subtends
            8.0-10.0 deg from the h1.8 grid eye — cumulus, not a canopy.
            `cr` is declared per ridge so every belt subtends 3.2-3.6 deg regardless of
            range, and each crown is drawn at 0.72-1.30 x cr with an independent z radius.
            `spire_p` of them are redrawn as narrow conifer spires that break the crest.
            Each crown is sunk `bury` of its z radius into the surface returned by
            `_lobe_surface`, so nothing floats and nothing shows a cut, and each centre is
            clamped to its own terrain plate inset by its own radius, so nothing can
            overhang the terrain either. `backdrop_selfcheck()` asserts both.

        Tone is drawn per crown from `hill["mix"][tone]` over the four hill tones, so a
        ridge is a mixed stand instead of one flat colour (the other half of the cloud read).
        Deterministic: one `RandomState` per ridge off `hill["seed"]`, never `hash()`.
        """
        hp = PARAMS["hill"]
        tone_mtl = (M["hill_a"], M["hill_b"], M["hill_c"], M["hill_d"])
        mix = hp["mix"]
        k_em = math.sqrt(max(1e-6, 1.0 - float(hp["sink"]) ** 2))
        n_lobe = n_crown = 0
        for i, h in enumerate(PARAMS["far_hills"]):
            plate = shore_plate_at(h["cx"], h["cy"])
            if plate is None:                       # gated by backdrop_selfcheck
                print(f"[원경][경고] Hill_{i} 이 지형판 밖이다 — 건너뛴다")
                continue
            _t, px0, py0, px1, py1, base, _th = plate
            rs = np.random.RandomState(int(hp["seed"]) + 13 * i)
            along_y = h["sy"] >= h["sx"]
            L, W = max(h["sx"], h["sy"]), min(h["sx"], h["sy"])
            # --- landform: overlapping buried caps along the ridge axis -----------
            # `h` is the CREST height, so the landform is what is left of it once the crown
            #   that stands on the crest is subtracted — see the PARAMS note.
            crest = max(0.5, h["h"] - (1.0 - float(hp["bury"]))
                        * float(h["cr"]) * float(hp["crown_ref"]))
            lobes = []
            nl = max(1, int(hp["lobes"]))
            for k in range(nl):
                t = 0.5 if nl == 1 else k / (nl - 1.0)
                prof = 0.62 + 0.38 * math.sin(math.pi * t)   # tapers to both ends
                land_h = crest * prof * float(rs.uniform(0.88, 1.12))
                rz = land_h / (1.0 - float(hp["sink"]))
                lz = base - float(hp["sink"]) * rz
                rl = L * float(hp["lobe_r"]) / k_em
                rw = W * float(hp["lobe_w"]) / k_em
                u = (t - 0.5) * L * float(hp["lobe_span"])
                v = float(rs.uniform(-1.0, 1.0)) * hp["lobe_jit"] * W
                lx, ly = ((h["cx"] + v, h["cy"] + u) if along_y
                          else (h["cx"] + u, h["cy"] + v))
                rx, ry = ((rw, rl) if along_y else (rl, rw))
                lobes.append((lx, ly, lz, rx, ry, rz))
                sc.add_sphere(stage, f"{ROOT}/Hill_{i}/Land_{k}",
                              (lx, ly, lz), (rx, ry, rz), M["shore"])
                n_lobe += 1
            # --- canopy: jittered grid of crowns over the ridge footprint ---------
            cr = float(h["cr"])
            pitch = cr * float(hp["pitch"])
            nu = max(1, int(round(L / pitch)))
            nv = max(1, int(round(W / pitch)))
            w = mix[int(h["tone"]) % len(mix)]
            cw = [sum(w[:j + 1]) for j in range(len(w))]
            for a in range(nu):
                for b in range(nv):
                    du = -L / 2.0 + (a + 0.5) * (L / nu) + float(
                        rs.uniform(-1.0, 1.0)) * hp["jit"] * pitch
                    dv = -W / 2.0 + (b + 0.5) * (W / nv) + float(
                        rs.uniform(-1.0, 1.0)) * hp["jit"] * pitch
                    cx, cy = ((h["cx"] + dv, h["cy"] + du) if along_y
                              else (h["cx"] + du, h["cy"] + dv))
                    s = float(rs.uniform(0.72, 1.30))
                    spire = float(rs.uniform(0.0, 1.0)) < float(hp["spire_p"])
                    rx = cr * s * (float(hp["spire_r"]) if spire else 1.0)
                    ry = rx * float(rs.uniform(0.86, 1.16))
                    rz = cr * s * (float(hp["spire_h"]) if spire
                                   else float(rs.uniform(0.95, 1.45)))
                    # never overhang the plate this ridge stands on
                    cx = min(max(cx, px0 + rx), px1 - rx)
                    cy = min(max(cy, py0 + ry), py1 - ry)
                    surf = _lobe_surface(lobes, cx, cy, base)
                    pk = float(rs.uniform(0.0, 1.0))
                    ti = next((j for j, c in enumerate(cw) if pk <= c),
                              len(cw) - 1)
                    sc.add_sphere(stage, f"{ROOT}/Hill_{i}/Crown_{a}_{b}",
                                  (cx, cy, surf - float(hp["bury"]) * rz),
                                  (rx, ry, rz), tone_mtl[ti % len(tone_mtl)])
                    n_crown += 1
        print(f"[원경] 가을 능선 {len(PARAMS['far_hills'])}열 · 지형 캡 {n_lobe}개 "
              f"· 수관 {n_crown}개 (수관 반경 2.8~5.6 m = 어느 열에서나 3.2~3.6°)")

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
                # [GT-115 ⑨ (1)] **spindle, seated into the culm.** Two members of decreasing
                #   radius replace the single drum: the flat top and the sky-lit down-facing
                #   cap were both visible at 400 % (the cap is the dark ring at the joint).
                #   The stack starts `plume_seat` **below** the culm top, so the culm and the
                #   plume overlap by 45 mm and no gap can open at any tilt; the axis unit
                #   vector is now the exact composition `Ry(ry)·Rx(rx)·(0,0,1)` that
                #   `add_cylinder` applies (op list [translate, rotZ, rotY, rotX] = points go
                #   through rotX → rotY), instead of the small-angle form used before.
                ph = rd["plume_h"]
                srx, sry = math.radians(rx), math.radians(ry)
                ux = math.cos(srx) * math.sin(sry)
                uy = -math.sin(srx)
                uz = math.cos(srx) * math.cos(sry)
                h_lo = ph * rd["plume_lo_frac"]
                h_hi = ph - h_lo
                # distance from the culm centre to each member's own centre, along that axis
                d_lo = hh / 2.0 - rd["plume_seat"] + h_lo / 2.0
                d_hi = hh / 2.0 - rd["plume_seat"] + h_lo + h_hi / 2.0
                for lbl, d_up, seg_h, seg_r in (
                        ("", d_lo, h_lo, rd["r"] * rd["plume_r_mul"]),
                        ("Tip", d_hi, h_hi, rd["r"] * rd["plume_tip_mul"])):
                    sc.add_cylinder(
                        stage,
                        f"{ROOT}/ReedPlume{lbl}_{ci}_{k}",
                        (cx + dx + d_up * ux, cy + dy + d_up * uy,
                         gz + hh / 2.0 + d_up * uz),
                        seg_r, seg_h, M["reed_plume"], rotY=ry, rotX=rx)

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
        n_ss = build_stepstones(M)           # [W3 P09 (1)] 판석 디딤돌 — G9's stepping stones
        _sst = PARAMS["stepstones"]
        print(f"[디딤돌] 판석 {n_ss}장 · 부정형 {_sst['nv'][0]}~{_sst['nv'][-1]}각 "
              f"· 두께 {_sst['thick'] * 1000:.0f} mm · 잔디면 위 노출 "
              f"{_sst['proud'] * 1000:.0f} mm (< GT_DELTA {gk.GT_DELTA * 1000:.0f} mm) "
              f"· 콜라이더 없음")
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
        #   [GT-115 ⑨ (4)] material `M["stone"]` → **`M["quay_stone"]`** and Ø0.48 × H2.1 →
        #   Ø0.30 × H0.90 (both derived in the `land_posts` PARAMS block). A 계선주 is one
        #   quarried block: the promenade's `plaza_light` slab map was wrapping each shaft in
        #   running-bond course lines, which is the one pattern a monolith cannot have.
        lp = PARAMS["land_posts"]
        for pi, yy in enumerate(lp["ys"]):
            sc.add_cylinder(stage, f"{ROOT}/LandPost_{pi}",
                            (lp["x"], yy, lp["z"] + lp["h"] / 2.0),
                            lp["r"], lp["h"], M["quay_stone"], collider=True)
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
            # [GT-115 ⑨ (7)] the seat well — the one thing that separates a pedal boat from a
            #   bath toy at 400 %. A single dark box, sunk `cockpit_drop` under the hull crown so
            #   the ellipsoid's own fall-off exposes it through the flanks (derivation in the
            #   `boat` PARAMS block). No existing part changes size or position.
            ck = bt["cockpit"]
            sc.add_box(stage, f"{grp}/Cockpit",
                       (bx + bt["cockpit_dx"], by,
                        hz + hl[2] - bt["cockpit_drop"] - ck[2] / 2.0),
                       ck, M["duck_seat"])
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
        _d_ok, _ = stepstone_selfcheck()     # [W3 P09] GT-41 (1)
        _b_ok, _ = backdrop_selfcheck()      # [GT-86] 접지 · 지평 폐합
        print(f"[W3 S09] 계절 {'OK' if _s_ok else 'FAIL'} · "
              f"FOV 배제 {'OK' if _f_ok else 'FAIL'} · "
              f"지평 폐합 {'OK' if _h_ok else 'FAIL'} · "
              f"[W3 P09] 디딤돌 {'OK' if _d_ok else 'FAIL'} · "
              f"[GT-86] 원경 접지 {'OK' if _b_ok else 'FAIL'}")
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
            # [GT-115 ⑨ (5)] `roughness_a` is not an input `_make_ground_pbr` ever authors —
            #   a constant roughness lands on **`rough_floor_a`** (`scene_common:2061`, with
            #   `rough_mult_a` 0). So this row has been reporting "(미지정)" in every round on
            #   the MDL side regardless of what the scene declared; corrected to the spelling
            #   the factory actually writes. (The row this batch cares about: the promotion
            #   path dropped `roughness_const` altogether, and now that the roof binds its map
            #   here, the declared 0.72 reaches the material for the first time.)
            _PAIRS = (("diffuse_color_constant", "base_color_a"),
                      ("reflection_roughness_constant", "rough_floor_a"),
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
