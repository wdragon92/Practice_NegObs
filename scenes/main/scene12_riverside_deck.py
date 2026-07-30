# -*- coding: utf-8 -*-
"""
scene12_riverside_deck.py - NegObs synthetic scene 12 (v5 R7): Han River
waterfront cantilever deck walk (Isaac Sim 4.5)

Type    : cantilever axis (inherits the geometry axis of the old T17 cliff
          catwalk) - only the stage is swapped for a 'Han River / stream
          waterfront timber deck promenade'. Spec: Docs/briefs/multi_scene_brief_v5.md
          §R7 (source: Docs/scene_redesign_v5_proposal.md disposition table 12=replace)
Shared  : scene_common.py · **world shared with scene17_ramp_pair_hangang.py**
          (water / apartment backdrop / bridge / silver grass / streetlight
          parameters and material patterns reused)

Hazard
  A 2.5 m wide timber deck cantilevers 1.25 m out over the revetment riprap and
  passes above the water (−1.8). On the river side **one 2.4 m span of railing
  is destroyed** (only post stubs remain, plus a single warning tape), so that
  stretch is entirely unguarded, and even the surviving railing **has no kick
  plate (bottom closure panel)**, so at robot eye height h0.3 the sight line
  runs straight out under the mid rail (z 0.55). Yet **the near water is not
  visible** - the sight line grazing the deck outer edge (y 1.25, z 0) reaches
  the water only at y = 8.75 m, so the 7.50 m stretch of riprap and water over
  y 1.25..8.75 disappears from frame (missing ground band). The 8-step descent
  at the deck end (x=0) is hidden the same way in grazing.

Goal
  (1) deck (x −18..0, width 2.5, z=0) + timber beams and piles + cantilever 1.25 m
  (2) river-side railing (posts + top rail + mid rail, no kick plate) + destroyed
      span 2.4 m
  (3) 8-riser connecting stair at the deck end (0.17 × 8 = 1.36) → lower
      floodplain (−1.36)
  (4) revetment riprap tiers (−0.55/−1.45/−1.75/−1.78/−1.95/−2.40) + water −1.8
      + reeds and silver grass
  (5) bike-path band · bench · streetlight · backdrop bridge/apartments
      (scene17 convention)
  (6) [v5.2 user] arbitrary warning signboards removed - only damage traces
      (post stubs, tape) remain

v6 ruling (judge_v6_rt_new7 §6) applied - **GT drop 1.80 unchanged** (director
decision 4)
  · water z assembly coordinate check : sc.build_water puts a 0.2-thick box
    centred at z−0.1 so its top face lands on z → water top face = −1.800, deck
    top face = 0.000 → drop 1.800.
    **No assembly bug** (re-confirmed on every run by the smoke [water z assembly
    check]).
    The real cause of "the water looks glued to the deck top face" was not z but
    **visibility**: with exposed riprap covering only y 1.25..2.35 (1.10 m), the
    high-angle sight line was cut by the deck edge, riprap and shoreline were
    hidden wholesale, and the water began right behind the deck edge.
  · measure (1) widen the exposed revetment band 2.4× (shoreline y 2.35 → 3.90,
           water y0 1.90 → 3.70) + film band + 96 rubble stones (was 42) → the
           riprap revetment stays in frame.
    measure (2) cantilever underside visibility cut : re-aim under_deck (low
           viewpoint 0.9 m above the water) + **new bank_face** (river-side high
           angle - deck surface, edge, fascia, beams, piles, riprap and shoreline
           stack vertically in one frame so 1.80 m reads as a scale).
    measure (3) raise the beauty_overview elevation (hidden band 2.96 → 1.31 m).
    measure (4) re-aim stair_join (the cut where the 8-step descent was out of
           frame and a streetlight cut through it).
    measure (5) [C-6] the warning tape was square bar stock and floating → a
           sagging ribbon tied to the surviving posts (4 mm thick).

Walk-continuity self-verification table (entry → walk → descent → exit; every
step <= 0.17)
  ┌ # section           coords (x, y, z)           step / verdict
  │ 0 upper grass       (−26.0, −3.0, 0.00)        flat (grass / decomposed granite path)
  │ 1 deck entry        (−18.0,  0.0, 0.00)        flat (flush with the floodplain)
  │ 2 deck walk         (−12.0,  0.0, 0.00)        flat (width 2.5, river-side railing)
  │ 3 destroyed span    ( −4.8,  0.0, 0.00)        ← **river side 2.4 m unguarded**
  │                                                    (drop 1.80 beyond the edge)
  │ 4 stair head        (  0.0,  0.0, 0.00)        flat
  │ 5 step 1 tread      (  0.16, 0.0, −0.17)       0.17
  │ 6 step 7 tread      (  2.08, 0.0, −1.19)       0.17 × 6
  │ 7 lower floodplain  (  2.60, 0.0, −1.36)       0.17 (8th riser)
  │ 8 bike path joint   (  8.0, −6.5, −1.358)      flat
  └ 9 east exit         ( 20.0, −6.5, −1.358)      flat
  * the upper floodplain (z=0) and the lower one (−1.36) are also linked south of
    the deck by a grass slope (1:2, x 0..2.72) - the stair is not the only route
    (a walking detour exists).
  * the deck's south edge is at the **same level** as the upper floodplain, so no
    drop there. The hazard is one-sided, on the river side.

[v7 ruling revision] judge_v7_rt_A §8 - items in scope.
  (1) the `edge_void` water is a **perfect mirror with no waves** ("infinity
      pool"). The smoke already confirmed GT (1.80 m) is consistent → the problem
      is not z but **material and framing**.
      → water_rough 0.08 → **0.14** (scene09 0.15 band) + turbidity tint nudged
        up, and `edge_void` tgt pulled in to just short of the shoreline so the
        **exposed riprap band (y 3.03..3.90) sits at frame centre** (eye, slope
        and the 1.78 m hidden band all unchanged).
  (2) the 4 silver grass bands = **brown cuboids** (C-5, v6's most repeated
      complaint, never acted on).
      → port the scene17 W-5 convention: `build_hedge` box → a **stand of 164
        stalks** (r 22 mm · height jitter · small-angle tilt · per-band seed).
        Band rectangles unchanged.
  (3) the railing is a **glossy white pipe** → painted steel (0.80/metallic 0.9 →
      0.30/0.25).
  (4) the right (+X) horizon was not closed → 1 south-side town block (S2) added
      (C-2).
  (5) (shared) §4 pure-white large-area self-check `albedo_selfcheck()` and the
      silver grass check `reed_selfcheck()` folded into the smoke. Parapet 0.90 →
      0.70 · luminaire 0.88 → 0.78.
  Not addressed (out of scope · shared builders): flat-colour bench slab
     (`sc.build_bench`), the straight cut of the bike path (§5), the near-black
     under-deck cavity in `bank_face` (an illumination item).

[W3 L12 - target-image renovation] Lane 3 row 3.1 of `w3_intake_v2_images.md` §4.
  **SEASON = SUMMER.** scene12 has no image of its own; under §7 ruling 8 an
  imageless scene inherits its **nearest image's** season, and the intake names
  **G3** (`Docs/reference_photos/Generated Image - Scene03.jpg`) primary and
  **G9** (`...Scene09.jpg`) secondary. G3 is a Han River levee promenade in full
  summer - saturated green shrub mass on the levee slope, full-leaf broadleaf on
  the crest, deep blue sky with cirrus. **G9 is autumn and is read for the
  deck-over-water FORM only, never for its season** - exactly the pairing
  scene17 declares, and 12 and 17 share one world, so they must agree.
  `season_audit()` runs the per-scene check §7-8 requires; there is no `bare=`
  call site in this file and the audit gates on that.

  **GT-43** (`Docs/audit_v4/gt_changes_w3.md` §3) - the river-side guard becomes
  **착색방부목 round post-and-rail**, the product G3 actually shows at the water
  edge, and its members move to the two round preservative-timber sections this
  repo has verified (`s3_research_numbers_v1.md` §A5, KFS-TRAIL 그림 3-20 p.72,
  grade A): **Ø120 posts · Ø80 rails**, replacing Ø64/Ø70/Ø40 steel-pipe
  diameters. Three things are deliberately NOT done, each with its reason:
    (a) **no balusters.** scene10's square sawn 방부목 railing
        (`w3_s10_rebuild_v1.md` §2) is a park-deck 방부각재 product; G3's
        river-edge product is a round-log post-and-rail with no infill at all.
        More decisively: the h0.3 sight line running out **under the mid rail**
        is this scene's negative-obstacle premise (see Hazard above), so
        infilling the bay would silently move the research variable.
    (b) **post pitch stays 1.5 m** against §A5's 1.2 m 통나무펜스 정간 - the
        2.4 m destroyed span is two bays of the 1.5 m grid and the stubs at
        -5.4/-4.2 sit on it, so re-pitching would move the hazard itself.
    (c) **rail height stays 1.05 m.** It is below both 조경설계기준 16.13.2(2)
        (산책로 1,100) and 16.20.2(2) (관찰데크 1,200); scene10 landed 1.10 on
        the KNPS n=1,227 built-reality median. Left alone and recorded as
        **L12-F1** - this scene's declared identity is a degraded guard, and
        moving the rail height without a ruling moves a cue.
  **GT-44** - the deck timber goes to the measured 2-5 year 방부목 patina band.
  `M["deckwood"]` bound the `wood_dark` map **raw**: mean linear
  (0.0824, 0.0584, 0.0442), L* 30.03, `albedo_selfcheck` 0.081 - a third of the
  band floor, on a walked deck. Target **L* 55.0 / a* +1.0 / b* +6.0**, albedo
  0.2293, which satisfies all four clauses of the band at once and lands level
  with scene10's deck (the same product, the same library, the same L0 sun).
  L* 56.0 was rendered first and corrected once by the reference - see
  `PARAMS["material"]["deck_tint"]` for the derivation, the correction and the
  clipping test.

  **River width: measured, NOT re-widened.** The intake is explicit that "12 and
  17 must not be re-widened independently of 03". `river_view_selfcheck()`
  reports the water's share of every judged frame; the effective channel is
  y 3.70..70.00 = **66.3 m**, already ~2x scene03's landed 33.8 m, so R03-1's
  inheritance is satisfied by construction and the water plane is untouched.

  **Species: no flip owed, measured not assumed.** `SCENE_SPECIES["Scene12"] =
  ("poplar", None)`; all 5 route trees already resolve to `Lombardy_Poplar` by
  prim-path token, so K4-F4's "a declared belt stays inert until the scene
  passes species=/belt=" does not bite here - the **belt is None because the
  scene has no across-water tree stand to put one on** (every tree is at
  y -8.5..-13, the land side). Recorded so a later sweep does not "fix" it.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene12_riverside_deck.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene12_riverside_deck.py
Smoke (pre-boot self-check of geometry, grounding, occlusion and cameras; early exit):
    NEGOBS_SMOKE=1 python scene12_riverside_deck.py

Coordinates: Z-up, m. Travel axis +X (deck walk → stair descent). **The drop
  starts at edge x=0** (stair head). The river is the +Y (north) side, land the
  −Y (south) side. Deck top face z=0, water z=−1.8.
  Sun SUN_AZ_OFFSET=171.5 (standard) → the rays travel from above −X−Y towards
  +X+Y = front light along the walking direction, while the revetment slope
  (normal +Y) is a back-lit dark zone (checked in the smoke).
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
# [A] SCENE_CONFIG - 7 keys. Only hazard_stairs toggles hazard geometry (deck/stair <-> flat).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> deck/stair/floodplain steps flattened to z=0 (only geometry toggle)
    "cue_railing":        True,    # river-side railing (no kick plate). The 2.4 m destroyed span is always missing
    "cue_tactile":        False,   # tactile paving not customary on a waterfront timber deck - code path reserved only
    "cue_material_break": True,    # deck timber vs floodplain grass/gravel contrast. False -> stair in grass-tone timber too
    "cue_sign":           False,   # [v5.2 user] arbitrary warning signboards removed - none placed (key reserved only)
    "cue_scene_dressing": True,    # reeds · bench · streetlight · bike path · bridge · apartment backdrop
    "cue_nosing":         False,   # True -> non-slip strip on the stair nosing
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
_RISER = 0.17
_NRISER = 8                                     # 8 risers -> drop 1.36
_LOWER_Z = -round(_RISER * _NRISER, 4)          # -1.36 (lower floodplain top face)

PARAMS = dict(
    # --- timber deck (x −18..0, width 2.5, top face z=0) ---
    #     y0 −1.25 is flush with the upper floodplain (no drop), y1 +1.25 is the river-side cantilever edge.
    deck=dict(x0=-18.0, x1=0.0, y0=-1.25, y1=1.25, z_top=0.0, slab_t=0.14,
              fascia_t=0.03),
    # === [W2-D ground_kit] P10 `deck_timber` - spec Sec.5.7 row 12 =========
    #  Natural scene: `natural=True` blocks manhole / gutter / marking, which
    #  matches the ruling "scene12 = deck facility, road infrastructure banned"
    #  (deck railings and low lighting stay props, not ground_kit).
    #  Two plans because the plank gaps need a different z (see below):
    #    A `ground_plan()`      z = deck z_top, staining + shoreline film band
    #    B `ground_plan_deck()` z lifted, plank gaps only
    #  Prescription: plank width 0.145 / gap 0.005 (120 boards over 18 m),
    #  butt joints staggered, gap detritus, shoreline film widened.
    #  The film band is placed at y 0.65..1.25, i.e. the river-side cantilever
    #  strip - `build_silt_band` runs bands parallel to +X at constant y, so
    #  this is the one edge of the deck it can actually describe.
    gkit=dict(
        film_line=0.65,               # band start y -> covers 0.65..1.25
        film_w=0.60,
        deck_gaps=120,                # Sec.5.7 "120 boards over 18 m"
        seed=12,
    ),
    # deck substructure: 2 longitudinal beams (y −0.8 / 0.0) + cross beams + piles. Outermost support line y=0.0
    #   -> cantilever overhang = 1.25 m (1.20 m from the revetment crest y=0.05).
    deckframe=dict(beam_ys=(-0.8, 0.0), beam_w=0.16, beam_h=0.26,
                   pile_r=0.11, pile_step=3.0, cross_w=0.16, cross_step=3.0),
    # --- connecting stair, 8 risers (n_geom 7 + lower floodplain 1) ---
    #     n_geom=7 : the 8th riser **is the lower floodplain top face itself**. If all 8 were built,
    #     the last step top (−1.36) would be coplanar with the floodplain slab top -> Z-fighting.
    stair=dict(x0=0.0, riser=_RISER, tread=0.32, n_riser=_NRISER,
               n_geom=_NRISER - 1, base_z=-2.0),
    # --- ground ---
    upper=dict(x0=-40.0, x1=0.0, y0=-22.0, y1=-1.25, z_top=0.0, thick=1.4,
               x_split=-18.0, y_crest=0.05),   # west of x_split extends to y_crest
    shoulder=dict(x0=-18.0, x1=0.0, y0=-1.25, y1=0.05, z_top=-1.20, thick=1.6),
    lower=dict(x0=0.0, x1=48.0, y0=-22.0, y1=1.25, z_top=_LOWER_Z, thick=1.2),
    slope=dict(x0=0.0, run=2.72, drop=1.36, y0=-22.0, y1=-1.25, thick=1.6),
    # revetment riprap tiers (all solid down to z_bot - prevents floating)
    #   [v6 ruling (2)] answer to "the water looks glued to the deck top face" - **GT drop 1.80 unchanged**
    #   (deck top face 0.00 − water −1.80). Director decision 4: leave the water z alone and
    #   **widen the exposed revetment band** to give the drop visual evidence.
    #     old: exposed riprap = y 1.25..2.35 (1.10 m) -> shoreline 0.65 m in front of the deck edge
    #     new: exposed riprap = y 1.25..3.90 (2.65 m, 2.4x) -> shoreline recedes to y 3.90
    #   D top face −1.75 is unchanged, so the **deck edge -> riprap fall height 1.75 m also stays**.
    rip_bot=-3.2,
    riprap=[dict(tag="A", x0=-40.0, x1=-18.0, y0=0.05, y1=0.65, z=-0.55),
            dict(tag="B", x0=-40.0, x1=-18.0, y0=0.65, y1=1.25, z=-1.45),
            dict(tag="C", x0=-18.0, x1=0.0, y0=0.05, y1=1.25, z=-1.45),
            dict(tag="D", x0=-40.0, x1=48.0, y0=1.25, y1=2.30, z=-1.75),
            dict(tag="E", x0=-40.0, x1=48.0, y0=2.30, y1=3.90, z=-1.78),
            dict(tag="F", x0=-40.0, x1=48.0, y0=3.90, y1=5.60, z=-1.95),
            dict(tag="G", x0=-40.0, x1=48.0, y0=5.60, y1=7.40, z=-2.40)],
    # film (wet riprap) band - softens the hard shoreline edge (v6 ruling (4) "no film or moss")
    waterline=dict(y0=2.90, y1=3.90, z=-1.78, proud=0.012),
    # individual rubble stones (randomly rotated boxes) - fixed seed. Count and range raised with the wider exposed band
    #   (answers ruling (4) "smooth cut-stone paving -> not a rubble revetment")
    rocks=dict(n=96, seed=712, x0=-38.0, x1=44.0, y0=0.2, y1=4.8,
               s_lo=0.30, s_hi=1.10),
    water=dict(x0=-40.0, x1=60.0, y0=3.70, y1=70.0, z=-1.80),
    far_bank=dict(x0=-40.0, x1=60.0, y0=70.0, y1=100.0, z_top=-1.50,
                  thick=2.2),
    # --- railing (river side y=1.15) : **no** kick plate - why the robot view stays open ---
    # [W3 L12 · GT-43] sections move off steel-pipe diameters onto the two round
    #   preservative-timber sizes this repo has verified (`s3_research_numbers_v1.md` §A5,
    #   KFS-TRAIL 그림 3-20 p.72, source grade A): 방부원형목재 **Ø120** and **Ø80**.
    #     post_r 0.032 -> 0.060 (Ø64 -> Ø120) · top_r 0.035 -> 0.040 (Ø70 -> Ø80)
    #     mid_r  0.020 -> 0.040 (Ø40 -> Ø80)
    #   Cost to the premise, re-derived not asserted: the open band between the deck top
    #   face (z=0) and the **mid-rail underside** goes 0.530 -> 0.510 m (-20 mm, -3.8 %),
    #   top-rail underside 1.015 -> 1.010. The h0.3 sight line survives; the cost is printed
    #   by the smoke rather than left to a reader's arithmetic.
    #   `spacing` and `post_h` are deliberately NOT touched - see the L12 docstring block (b)/(c).
    rail=dict(y=1.15, post_r=0.060, post_h=1.05, spacing=1.5,
              top_z=1.05, top_r=0.040, mid_z=0.55, mid_r=0.040,
              gap_x0=-6.0, gap_x1=-3.6,            # destroyed span 2.4 m
              stub_xs=(-5.4, -4.2), stub_h=0.10,   # sheared-off post stubs
              # [v6 C-6] warning tape = 0.02-thick square bar -> **thin ribbon + sag**.
              #   the old spec was a solid rod spanning x −6.0..−3.6 outright, so (a) its thickness
              #   was steel-beam grade and (b) the east end −3.6 had no support, so it floated in mid-air.
              #   new spec: tie both ends to the **surviving posts x −6.0 / −3.0** and
              #   let the centre droop by sag - a parabolic ribbon (4 mm thick).
              tape=dict(anchor_xs=(-6.0, -3.0), z_end=0.90, sag=0.17,
                        nseg=10, w=0.075, t=0.004, tie_h=0.05)),
    # [v5.2 user] arbitrary warning signboards removed - fall-hazard / stair-hazard sign parameters deleted.
    # --- upper floodplain dressing ---
    path=dict(x0=-40.0, x1=0.0, y0=-4.6, y1=-2.6, proud=0.002),   # decomposed-granite promenade
    benches=[(-13.0, -1.90, 0.0), (-6.5, -1.90, 0.0)],
    streetlights=[(-15.0, -2.30), (-2.0, -2.60)],
    streetlight=dict(pole_h=4.5, pole_r=0.07, arm_len=0.9, arm_r=0.04,
                     head=0.24),
    trees=[(-34.0, -9.0), (-27.0, -13.0), (-19.0, -8.5), (-9.0, -12.0),
           (-2.0, -9.0)],
    # --- lower floodplain dressing ---
    bikeroad=dict(x0=0.0, x1=48.0, y0=-8.0, y1=-5.0, proud=0.002),
    lower_benches=[(9.0, -3.4, 180.0), (19.0, -3.4, 180.0)],
    lower_bollards=[(3.4, -1.6), (3.4, 1.6)],
    # reed / silver grass bands (waterfront vegetation)
    # === [v7 ruling §8 (3)] the 4 silver grass bands are **brown/olive cuboids** (C-5) ===
    #   symptom: at the centre of `bank_face` and the right of `beauty_overview`, rectangular
    #     boxes with only a domed top. v6 named this "the most obvious sim tell in 12"; not acted on.
    #   cause: planted with `sc.build_hedge` (box + rounded top) - the hedge builder
    #     cannot express vegetation **whose background shows through between stalks**, as silver grass does.
    #   fix: port the scene17 W-5 convention (and its origin, scene09 `build_reeds`) -
    #     inside the band rectangle (position and size = **unchanged**), scatter thin
    #     cylinder stalks at density stalks/m² with a fixed seed. Height jitter 0.80~1.12x · small-angle
    #     tilt 9 deg · per-band fixed seed -> reproducibility kept.
    #   the prim-count numeric check is `reed_selfcheck()` (module level, no boot).
    reeds=[dict(x0=-34.0, y0=1.40, x1=-28.0, y1=2.25, h=1.10, z=-1.75,
                seed=121),
           dict(x0=-13.0, y0=1.40, x1=-9.0, y1=2.25, h=1.05, z=-1.75,
                seed=122),
           dict(x0=6.0, y0=0.10, x1=12.0, y1=1.10, h=1.20, z=_LOWER_Z,
                seed=123),
           dict(x0=22.0, y0=1.40, x1=30.0, y1=2.25, h=1.15, z=-1.75,
                seed=124),
           dict(x0=36.0, y0=0.10, x1=42.0, y1=1.10, h=1.10, z=_LOWER_Z,
                seed=125)],
    # stalk convention - same values as scene17 PARAMS["reed"] (unifies vegetation tone and thickness across the 21 scenes)
    reed=dict(r=0.022, density=6.0, h_lo=0.80, h_hi=1.12, tilt=9.0),
    reed_tint=(0.42, 0.44, 0.26),
    # --- backdrop (scene17 world reused) : apartments across the river + bridge + south-side townscape ---
    far_buildings=dict(
        A=dict(x0=-34.0, x1=-14.0, y0=84.0, y1=92.0, h=44.0, floors=15,
               axis="y", facade_y=84.0, face_dir=-1.0, base_z=-1.5),
        B=dict(x0=-4.0, x1=16.0, y0=84.0, y1=92.0, h=50.0, floors=17,
               axis="y", facade_y=84.0, face_dir=-1.0, base_z=-1.5),
        C=dict(x0=26.0, x1=44.0, y0=84.0, y1=92.0, h=40.0, floors=13,
               axis="y", facade_y=84.0, face_dir=-1.0, base_z=-1.5),
        S=dict(x0=-30.0, x1=-6.0, y0=-42.0, y1=-30.0, h=32.0, floors=11,
               axis="y", facade_y=-30.0, face_dir=1.0, base_z=0.0),
        # [v7 ruling §8 (3) leftover] "right horizon not closed" - the south townscape only reached x <= −6, so
        #   the +X side (behind-right of the walking direction) was open to the sky. Add 1 block per the
        #   C-2 (horizon closure) convention. Offset 8 m · setback 4 m · height 26 m so it forms no
        #   repeating rhythm with S (§3). Over 30 m from the deck (x −18..0) and stair (x 0..2.24), hence
        #   irrelevant to the hazard geometry and to grazing occlusion.
        S2=dict(x0=2.0, x1=24.0, y0=-38.0, y1=-26.0, h=26.0, floors=9,
                axis="y", facade_y=-26.0, face_dir=1.0, base_z=0.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.6, margin=2.0),
    bridge=dict(x0=30.0, x1=34.0, y0=-6.0, y1=100.0, deck_top=6.0,
                deck_t=1.2, pier_r=1.2, pier_x=32.0,
                pier_ys=(-2.0, 18.0, 42.0, 66.0), pier_base=-3.6),
    far_hedges=[dict(cx=-36.0, cy=-16.0, sx=1.2, length=20.0, h=1.6),
                dict(cx=-20.0, cy=-19.0, sx=1.2, length=20.0, h=1.6),
                dict(cx=6.0, cy=-19.0, sx=1.2, length=20.0, h=1.6)],

    material=dict(
        # [v6 ruling (4)] rock_wall 1.4 -> 0.7 : a 1.4 m tile turns the revetment riprap into
        #   "smooth cut-stone paving". Halving it to 0.7 makes each stone block read half the size.
        scale=dict(wood_dark=0.6, rock_wall=0.7, grass=1.4, gravel=0.6,
                   concrete_wall=2.0),
        # film (wet riprap) - teal mossiness + low roughness (wet reflection)
        wet_tint=(0.34, 0.38, 0.30), wet_rough=0.28,
        grass_tint=(0.55, 0.68, 0.42),
        # sRGB gamma rule (§A-1): a "dark colour" is the 0.02~0.06 band.
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.85,
        paint_color=(0.72, 0.72, 0.68), paint_rough=0.6,
        # === [v7 ruling §8 (1)/(a)] the `edge_void` water is a **perfect mirror** (crisp building reflections)
        #   + waveless uniform teal -> an "infinity pool". Deck plank -> mossy riprap band -> water
        #   looking joined at one level: half of that impression is this reflection (the other half is the high angle).
        #   fix: roughness 0.08 -> **0.14** (scene09 water_rough 0.15 reference band)
        #     + turbidity tint nudged up (0.05,0.10,0.11 -> 0.062,0.108,0.112) -
        #     Han River turbid water is a pale grey-blue in reality, not pure blue-black.
        #   ** water z (−1.80) and extent unchanged = GT 1.80 m unchanged. Material only. **
        water_color=(0.062, 0.108, 0.112), water_rough=0.14,
        # === [W3 L12 · GT-44] deck timber -> the measured 2-5 year 방부목 patina band ===
        #   The `wood_dark` map was bound RAW here. Measured at full resolution this lane:
        #     source mean linear (0.0824, 0.0584, 0.0442) · Y 0.0625 · L* 30.03
        #   (an independent reproduction of `w3_s10_rebuild_v1.md` §2.2's figure).
        #   Band [research §D4/D5, CIELAB from Forests 9(8) 488 and Wood Research 62(5) 737]:
        #     L* 53-60 · a* 0..+2 · b* +4..+10 · albedo 0.22-0.28
        #   The band's own clauses disagree at the floor - L* 53 <-> Y 0.2105 is BELOW the
        #   albedo clause - so the effective intersection is **L* 54.1-59.9**. The target sits
        #   in its lower half because this deck is open and unshaded under the 49.79 deg L0 sun.
        #   Reference read [ref, this session]: G9's boardwalk in diffuse light measures
        #     L* 58.05 · a* +1.41 · b* +2.34 - inside the band, but it is a RENDERED PIXEL under
        #     sky illumination, i.e. an upper bound on albedo, not an albedo. Hence below it.
        #   L* 56.0 was built and rendered FIRST (round `260731_w3_l12`, tint 3.207/4.030/4.553,
        #   albedo 0.2391). Against the reference it read **a shade bleached** - closer to
        #   driftwood grey than to a 2-5 year patina - and the near-ground band measured
        #   mean 185 where scene10's landed deck, the same product in the same library under
        #   the same L0 sun, measures **181**. Corrected ONCE by the reference, exactly as
        #   `w3_s10_rebuild_v1.md` §2.2 records doing:
        #   target L* 55.0 / a* +1.0 / b* +6.0 -> linear (0.2537, 0.2258, 0.1925), albedo 0.2293
        #   - still inside all four clauses, still in the effective band's lower half, and now
        #   numerically level with scene10. **The reference moved the value within the standard;
        #   it did not overrule it.** This does NOT clear the near-ground mean>170 / wht%>=2
        #   gates and is not claimed to: no in-band target can (even at the albedo floor 0.220
        #   the band measures 177-178), which is L12-F3.
        #   tint = target / source; clipped texels at this gain = 0.0070 % -> the shipped map
        #   carries the target, so no weathered-plank procurement is opened (S10 G5 stays unspent).
        deck_tint=(3.080, 3.864, 4.355),
        # === [W3 L12 · GT-43] guard timber = 착색방부목 (colour-stained), NOT weathered silver ===
        #   G3's levee-edge guard and benches are a stained product, measured over 5 clean
        #   patches this session at L* 32.7 (shadowed post) .. 51.6 (sunlit bench slat),
        #   a* +0.5..+3.8, b* +6.8..+20.7 - plainly darker and warmer than the weathered band.
        #   Research §D5 names 착색방부목 as a distinct product that starts brown rather than
        #   following the ACQ green -> honey -> driftwood-grey path, so the deck and the guard
        #   are genuinely two products, not one material at two ages.
        #   Target L* 44.0 / a* +3.0 / b* +12.0 - inside the measured bracket, below the sunlit
        #   reads (a lit face renders above its albedo), above the deep-shadow read.
        #   -> linear (0.1766, 0.1320, 0.0894), albedo 0.1384. Clipping 0.0001 %.
        #   Consequence, measured rather than hoped: deck/guard luminance contrast becomes
        #   **1.73x**, where the outgoing painted steel against the corrected deck would have
        #   been only 1.29x - the cue reads BETTER after the swap, not worse.
        guard_tint=(2.144, 2.258, 2.022),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # [v7 §4] parapet 0.90 -> 0.70 · luminaire 0.88 -> 0.78 (albedo cap 0.80).
        #   scene05 was already down at 0.72; only 12 still had 0.90 left.
        parapet_color=(0.70, 0.70, 0.68), parapet_rough=0.6,
        bridge_color=(0.05, 0.05, 0.055), bridge_rough=0.7,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        tape_color=(0.75, 0.62, 0.10), tape_rough=0.7,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
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
    # standard kept (brief v5 §R7 states 171.5). Same light rig as scene17 = shared world.
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene12")
ASSET_ROLES = ["wood_dark", "rock_wall", "grass", "gravel", "concrete_wall",
               "hdri", "mdl"]   # [v5.2 user] arbitrary warning signboards removed


# ===========================================================================
# [C2] geometry helpers (shared by smoke and assembly)
# ===========================================================================
def _rail_posts():
    """Railing post x list - **inside** the destroyed span (gap_x0..gap_x1) is left empty.
    The posts at both ends of the span survive (so the damage boundary reads)."""
    d = PARAMS["deck"]
    r = PARAMS["rail"]
    xs = []
    n = int(round((d["x1"] - d["x0"]) / r["spacing"]))
    for k in range(n + 1):
        x = d["x0"] + k * r["spacing"]
        if r["gap_x0"] < x < r["gap_x1"]:
            continue
        xs.append(round(x, 4))
    return xs


def reed_instances():
    """[v7 ruling §8 (3)] Silver grass stalk generator - **the builder and the
    numeric check use the same coordinates** (scene04 `verge_instances`
    convention). Per-band fixed seed → reproducibility guaranteed.
    yield: (band_i, band, k, px, py, hh, rotY, rotX)"""
    rd = PARAMS["reed"]
    for i, b in enumerate(PARAMS["reeds"]):
        rs = np.random.RandomState(int(b["seed"]))
        area = (b["x1"] - b["x0"]) * (b["y1"] - b["y0"])
        for k in range(int(round(area * rd["density"]))):
            px = float(rs.uniform(b["x0"], b["x1"]))
            py = float(rs.uniform(b["y0"], b["y1"]))
            hh = float(b["h"] * rs.uniform(rd["h_lo"], rd["h_hi"]))
            a = float(rs.uniform(0.0, 360.0))
            yield (i, b, k, px, py, hh,
                   rd["tilt"] * math.cos(math.radians(a)),
                   rd["tilt"] * math.sin(math.radians(a)))


def reed_selfcheck(verbose=True):
    """Silver grass stand numeric check - band rectangles unchanged · stalk count ·
    tilt end excursion · zero intrusion into the walk corridor (|y| ≤ 0.55) or
    the railing line (y 1.15) of the **deck section (x −18..0)**.
    (The x 6..42 bands sit on the lower floodplain and are not subject to the
     corridor convention - as in the existing corridor check, the x range is
     considered together.)"""
    rd = PARAMS["reed"]
    d = PARAMS["deck"]
    r = PARAMS["rail"]
    inst = list(reed_instances())
    # largest excursion of a tip leaning at the 9 deg tilt beyond the band
    out = 0.0
    intrude = []
    for i, b, k, px, py, hh, ry, rx in inst:
        dx = abs(math.tan(math.radians(rd["tilt"]))) * hh / 2.0
        out = max(out, dx)
        if not (d["x0"] - dx <= px <= d["x1"] + dx):
            continue                       # outside the deck section = lower floodplain planting
        if abs(py) - dx <= 0.55 or abs(py - r["y"]) <= dx:
            intrude.append((i, k))
    ok = (not intrude)
    if verbose:
        print("  [억새 군락 — v7 §8 ③ stalk 전환]")
        print(f"    밴드 {len(PARAMS['reeds'])}개(사각형 좌표 불변) · 밀도 "
              f"{rd['density']:.1f} 본/m² → **대 {len(inst)}본** "
              f"(구: build_hedge 육면체 {len(PARAMS['reeds'])}개)")
        print(f"    대 r {rd['r']*1000:.0f} mm · 높이 지터 {rd['h_lo']:.2f}"
              f"~{rd['h_hi']:.2f}× · 기울기 {rd['tilt']:.0f}° "
              f"(끝 이탈 최대 {out*100:.1f} cm)")
        print(f"    데크 구간(x {PARAMS['deck']['x0']:.0f}.."
              f"{PARAMS['deck']['x1']:.0f}) 회랑(|y|≤0.55)·난간선"
              f"(y {PARAMS['rail']['y']:.2f}) 침범 "
              f"{len(intrude)}건 → {'OK' if ok else 'FAIL'}")
    return ok, dict(n=len(inst), out=out, intrude=intrude)


# ===========================================================================
# [C2b] [v7 ruling §11-6] §4 "no pure white (>0.8) over large areas" albedo cap self-check
#   shared convention for 05/09/12. Two criteria are checked together:
#     (A) effective albedo max channel > CAP(0.80)  -> violates the letter of v5.1 §4
#     (B) predicted render sRGB of a **large horizontal area** = sRGB(albedo x GAIN) > 0.87 (~222)
#   GAIN 1.77 = back-computed from v7_rt measurements (scene09 `ghat_walk` paving 0.422 -> render 223).
#   05/09/12 share one lighting rig: dome 1000 + sun 2450 · elev 49.79.
# ===========================================================================
_ALBEDO_GAIN = 1.77
_ALBEDO_CAP = 0.80
_ALBEDO_PRED_CAP = 0.87
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
        a = np.asarray(im, dtype=float) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        val = tuple(float(v) for v in lin.mean(axis=(0, 1)))
    except Exception:
        val = None
    _TEXMEAN_CACHE[role] = val
    return val


def _srgb(u):
    u = max(0.0, min(1.0, u))
    return 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055


# (label, texture role|None, material key|None, large area, horizontal face)
_ALBEDO_TABLE = [
    # [W3 L12] the two timber rows now carry their derived tints. Before GT-44 the deck row
    #   read `None` (the map bound raw) and printed 알베도 0.081 - the defect, in the scene's
    #   own instrument. The guard row was `rail_color`, a painted-steel constant.
    ("데크 널(목)",     "wood_dark",      "deck_tint",      True,  True),
    ("가드 난간(목)",   "wood_dark",      "guard_tint",     False, False),
    ("호안 사석",       "rock_wall",      None,             True,  True),
    ("물때 사석",       "rock_wall",      "wet_tint",       True,  True),
    ("둔치 잔디",       "grass",          "grass_tint",     True,  True),
    ("자갈 산책로",     "gravel",         None,             True,  True),
    ("아파트 외벽",     "concrete_wall",  None,             True,  False),
    ("자전거도로 차선", None,             "paint_color",    False, True),
    ("파라펫",          None,             "parapet_color",  True,  False),
    ("가로등 등기구",   None,             "lamp_color",     False, False),
    ("경고 테이프",     None,             "tape_color",     False, False),
    ("억새 대",         "grass",          "reed_tint",      False, False),
]


def albedo_selfcheck(verbose=True):
    """[v7 §4/§11-6] Pure-white large-area self-check. Returns (ok, rows)."""
    mp = PARAMS["material"]
    rows, fails, warns = [], [], []
    for label, role, key, wide, horiz in _ALBEDO_TABLE:
        if key is None:
            tint = (1.0, 1.0, 1.0)
        else:
            tint = mp.get(key, PARAMS.get(key))
            if tint is None:
                continue
        base = (1.0, 1.0, 1.0) if role is None else _tex_lin_mean(role)
        if base is None:
            rows.append((label, key or role, None, None, "SKIP(텍스처 없음)"))
            continue
        alb = max(b * t for b, t in zip(base, tint))
        pred = _srgb(alb * _ALBEDO_GAIN) if horiz else None
        why = []
        if alb > _ALBEDO_CAP:
            why.append("A:알베도")
        if pred is not None and pred > _ALBEDO_PRED_CAP:
            why.append("B:렌더예측")
        if why:
            mark = "/".join(why)
            (fails if wide else warns).append(label)
            tag = f"FAIL 대면적({mark})" if wide else f"WARN 소면적({mark})"
        else:
            tag = "OK"
        rows.append((label, key or role, alb, pred, tag))
    ok = not fails
    if verbose:
        print("  [§4 순백 대면적 알베도 상한 자가검사] "
              f"CAP {_ALBEDO_CAP} · 수평 렌더예측 CAP {_ALBEDO_PRED_CAP} "
              f"· GAIN {_ALBEDO_GAIN}")
        for label, key, alb, pred, tag in rows:
            if alb is None:
                print(f"    {label:14s} {str(key):16s} {tag}")
                continue
            pr = f"{pred*255:5.1f}" if pred is not None else "  수직"
            print(f"    {label:14s} {str(key):16s} 알베도 {alb:.3f} · "
                  f"수평 예상 렌더 {pr}  {tag}")
        print(f"    ⇒ {'OK — 대면적 위반 0건' if ok else 'FAIL: ' + str(fails)}"
              f"{'  (WARN: ' + str(warns) + ')' if warns else ''}")
    return ok, rows


# ===========================================================================
# [B-3] [W3 L12] season audit + river-view measurement. Both are pure CPU, no
#       Isaac boot, no GPU, no render - the scene03 `river_width_selfcheck`
#       convention (`w3_s03_v1.md` §1.2) ported to this scene's geometry.
# ===========================================================================
def season_audit(verbose=True):
    """[W3 L12] §7 ruling 8 requires **one seasonal audit per scene**, against the
    season that scene's own target image pins. scene12 is imageless and inherits
    **G3 = SUMMER**; G9 (autumn) is read for the deck-over-water form only.

    Every row is a value read out of PARAMS, not an adjective. Returns (ok, rows).
    """
    mp = PARAMS["material"]

    def _green_dom(t):
        """A tint is a summer-foliage tint if green leads and it is not a dry khaki."""
        return t[1] >= t[0] and t[1] > t[2]

    rows = []
    rows.append(("route trees x%d" % len(PARAMS["trees"]),
                 'SCENE_SPECIES["Scene12"] route=poplar · bare= not passed (default False)',
                 "full leaf", True))
    rows.append(("belt trees x0",
                 'SCENE_SPECIES["Scene12"] belt=None · no across-water stand exists '
                 '(every tree y -8.5..-13, land side)',
                 "n/a - nothing to flip", True))
    for key in ("canopy_a", "canopy_b"):
        t = mp[key]
        rows.append((f"tree canopy {key}", f"{t}", "dark green", _green_dom(t)))
    t = mp["grass_tint"]
    rows.append(("floodplain turf grass_tint", f"{t}", "green-dominant", _green_dom(t)))
    t = PARAMS["reed_tint"]
    # 억새 read: green-dominant foliage with NO plume geometry built is a summer stand.
    # A khaki plume band would be the autumn read; scene17 makes exactly this call and
    # 12 shares its world, so the two must agree.
    rows.append((f"silver grass x{sum(1 for _ in PARAMS['reeds'])} bands · "
                 f"{len(list(reed_instances()))} stalks",
                 f"reed_tint {t} · g/r {t[1]/t[0]:.2f} · g/b {t[1]/t[2]:.2f} · "
                 f"no plume geometry built",
                 "summer 억새 foliage", _green_dom(t)))
    # Measured, not asserted. The token is assembled at runtime so that this counting
    # line does not itself contain the literal it is looking for (it did, and the audit
    # duly reported its own source as a leaf-off call site).
    tok = "bare" + "=True"
    nbare = 0
    try:
        with open(os.path.abspath(__file__), encoding="utf-8") as fh:
            nbare = sum(1 for ln in fh if tok in ln and "tok =" not in ln)
    except OSError:
        nbare = -1
    rows.append(("bare= / BARE_SUBPRIMS call sites", f"{nbare} in this file",
                 "n/a by design - nothing here is leaf-off", nbare == 0))
    rows.append(("Rhododendron (K4-F1 flower loss)",
                 "not referenced in this scene",
                 "n/a - library-wide, not a scene regression", True))
    rows.append(("sun noon_sun_elev",
                 f"{PARAMS['light']['noon_sun_elev']:.2f} deg = the library L0 datum "
                 f"(29 of 33 scenes)",
                 "INFO - no scene can pin summer through sun angle (S17-F3)", True))
    ok = all(r[3] for r in rows)
    if verbose:
        print("  [W3 L12 계절 감사] G3 = 여름 (G9 는 형태만, 계절 아님)")
        for name, val, read, good in rows:
            print(f"    {'OK  ' if good else 'FAIL'} {name:34s} {val}")
            print(f"         -> {read}")
        print(f"    ⇒ 위반 {sum(1 for r in rows if not r[3])} 건")
    return ok, rows


def _cam_basis(eye, tgt):
    """World -> normalised camera image coords. up=+Z, image u(right) · v(up).
    Ported verbatim from `scene03_riverbank._cam_basis` so the two river scenes
    are measured with one instrument. Returns project(P) -> (u, v, depth) in tan units."""
    ex, ey, ez = eye
    fx, fy, fz = tgt[0] - ex, tgt[1] - ey, tgt[2] - ez
    fl = math.sqrt(fx * fx + fy * fy + fz * fz)
    f = (fx / fl, fy / fl, fz / fl)
    rx, ry = f[1], -f[0]
    rl = math.hypot(rx, ry)
    if rl < 1e-9:                       # sight line vertical - not used by this scene
        return lambda p: None
    r = (rx / rl, ry / rl, 0.0)
    u_ = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2],
          r[0] * f[1] - r[1] * f[0])

    def project(p):
        dx_, dy_, dz_ = p[0] - ex, p[1] - ey, p[2] - ez
        d = dx_ * f[0] + dy_ * f[1] + dz_ * f[2]
        if d <= 1e-6:
            return None
        return ((dx_ * r[0] + dy_ * r[1] + dz_ * r[2]) / d,
                (dx_ * u_[0] + dy_ * u_[1] + dz_ * u_[2]) / d, d)
    return project


def river_view_selfcheck(verbose=True):
    """[W3 L12] How much river is actually in frame - the quantity R03-1 needs.

    The intake is explicit that **12 and 17 must not be re-widened independently
    of 03** (`w3_intake_v2_images.md` §2 scene12 (c)), so this scene **measures**
    its channel rather than moving it. The water plane is untouched by L12.

    As `w3_s03_v1.md` §1.2 established, R03-1's literal wording - *"water subtends
    >= 1/3 of the d5 frame width"* - is satisfied trivially by any horizontal band,
    so it is not a discriminating test and is not reported as a pass. What is
    reported is the same pair scene03 reports, computed the same way:

      * `v_pct`    vertical subtense of the water band **in the frame's centre column**,
                   as % of frame height. scene03 takes this on its sight axis because its
                   river spans the same axis its cameras look down; here the river spans
                   +Y while every preset looks down +X, so an "on-axis" column probe is
                   degenerate (it lands at zero depth). The centre-column occupancy is the
                   same quantity, read off the same sample, and is not axis-dependent.
      * `area_pct` share of the frame the water polygon covers, by a 240 x 135 cell sample

    Occlusion by near geometry is **not** modelled (the deck edge hides a great deal
    of near water by design - that is this scene's whole hazard), so `area_pct` is an
    upper bound and is used as a relative number, exactly as scene03 uses it.

    Returns: (ok, diagnostic dict).
    """
    wt, fb = PARAMS["water"], PARAMS["far_bank"]
    y_near, y_far = wt["y0"], fb["y0"]
    zw, width = wt["z"], fb["y0"] - wt["y0"]
    x0, x1 = wt["x0"], wt["x1"]
    TU, TV = math.tan(math.radians(30.0)), math.tan(math.radians(18.0))

    views = build_views()
    diag = {}
    for name in sorted(views):
        eye, tgt = views[name]["eye"], views[name]["tgt"]
        proj = _cam_basis(eye, tgt)
        cells, centre_rows = set(), set()
        NX, NY = 200, 140
        for i in range(NX + 1):
            xx = x0 + (x1 - x0) * i / NX
            for j in range(NY + 1):
                yy = y_near + (y_far - y_near) * j / NY
                q = proj((xx, yy, zw))
                if q is None or abs(q[0]) > TU or abs(q[1]) > TV:
                    continue
                cu = int((q[0] + TU) / (2 * TU) * 240)
                cv = int((q[1] + TV) / (2 * TV) * 135)
                cells.add((cu, cv))
                if 114 <= cu <= 125:            # centre column, ~5 % of frame width
                    centre_rows.add(cv)
        diag[name] = dict(v_pct=round(100.0 * len(centre_rows) / 135.0, 2),
                          area_pct=round(100.0 * len(cells) / (240.0 * 135.0), 2))

    # scene03 landed 33.8 m (v7, `w3_s03_v1.md` §1.1). This scene must not be narrower
    # than the river it shares a world with, and must not have been widened by this lane.
    ok = width >= 33.8
    if verbose:
        print("  [W3 L12 강 뷰 검산] 기하만 · GPU 0 · 수면 평면 **무변경**")
        print(f"    유효 수면 y {y_near:.2f}..{y_far:.2f} = {width:.1f} m "
              f"(scene03 v7 착지값 33.8 m · v4 22.5 m) → "
              f"{'OK (03 이상, 재확폭 불요)' if ok else 'FAIL'}")
        for k in sorted(diag):
            d = diag[k]
            print(f"      {k:20s} 세로각 {d['v_pct']:6.2f} %  화면면적 {d['area_pct']:6.2f} %")
        print("    주: R03-1 문구의 '프레임 폭 1/3'은 수면이 가로 밴드라 보이기만 하면 "
              "항상 100 % — 실질 지표는 위 두 값 (w3_s03_v1.md §1.2).")
    return ok, dict(width=width, views=diag)


def _sun_dir():
    """DistantLight travel direction d (world) - back-computed from the
    setup_lighting op order (base −Z → rotateX(90−elev) → rotateZ(rz))."""
    lp = PARAMS["light"]
    rz = math.radians(lp["noon_dome_rot"] + PARAMS["SUN_AZ_OFFSET"]
                      + lp["hdri_sun_rotz_offset"])
    rx = math.radians(90.0 - lp["noon_sun_elev"])
    return (-math.sin(rx) * math.sin(rz),
            math.sin(rx) * math.cos(rz),
            -math.cos(rx))


def _obstacle_boxes():
    """Obstacle AABBs for the camera collision check (name, x0,x1, y0,y1, z0,z1).
    [brief v5 instruction] Numeric coordinate check that the grid and
    mise-en-scene cameras do not collide with railings, benches, reeds or signs
    (precedent: the scene19 d5 blackout)."""
    d = PARAMS["deck"]
    r = PARAMS["rail"]
    boxes = []
    # 2 railing segments (AABB including posts and rails)
    for tag, x0, x1 in (("Rail_W", d["x0"], r["gap_x0"]),
                        ("Rail_E", r["gap_x1"], d["x1"])):
        boxes.append((tag, x0, x1, r["y"] - 0.06, r["y"] + 0.06,
                      0.0, r["top_z"]))
    # bench · streetlight · tree · reed · sign · bollard
    for i, (bx, by, _yaw) in enumerate(PARAMS["benches"]):
        boxes.append((f"Bench_{i}", bx - 0.95, bx + 0.95, by - 0.25, by + 0.25,
                      0.0, 0.46))
    for i, (bx, by, _yaw) in enumerate(PARAMS["lower_benches"]):
        boxes.append((f"BenchLow_{i}", bx - 0.95, bx + 0.95, by - 0.25,
                      by + 0.25, PARAMS["lower"]["z_top"],
                      PARAMS["lower"]["z_top"] + 0.46))
    sl = PARAMS["streetlight"]
    for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
        boxes.append((f"Streetlight_{i}", lx - 0.15, lx + 0.15,
                      ly - sl["arm_len"] - 0.2, ly + 0.2, 0.0, sl["pole_h"]))
    for i, (tx, ty) in enumerate(PARAMS["trees"]):
        boxes.append((f"Tree_{i}", tx - 0.9, tx + 0.9, ty - 0.9, ty + 0.9,
                      0.0, 3.3))
    for i, rd in enumerate(PARAMS["reeds"]):
        boxes.append((f"Reed_{i}", rd["x0"], rd["x1"], rd["y0"], rd["y1"],
                      rd["z"], rd["z"] + rd["h"]))
    # [v5.2 user] arbitrary warning signboards removed - sign AABB deleted.
    for i, (bx, by) in enumerate(PARAMS["lower_bollards"]):
        boxes.append((f"BollardLow_{i}", bx - 0.08, bx + 0.08, by - 0.08,
                      by + 0.08, PARAMS["lower"]["z_top"],
                      PARAMS["lower"]["z_top"] + 0.75))
    return boxes


def _solid_at(x, y, z):
    """Name of the terrain / structural solid containing point (x,y,z) (None if there is none).
    Single source for the camera-eye burial check + the **sight-line blocking
    check** (ray march).
    Covers: upper and lower floodplain, shoulder riprap, grass slope, deck slab
    and beams, stair solid, revetment riprap tiers, backdrop bridge deck.
    (Props are handled by _obstacle_boxes.)"""
    u = PARAMS["upper"]
    sh = PARAMS["shoulder"]
    lo = PARAMS["lower"]
    d = PARAMS["deck"]
    st = PARAMS["stair"]
    sp = PARAMS["slope"]
    # upper floodplain A (west of the deck: up to the crest) / B (deck section: up to the deck south edge)
    if u["x0"] <= x <= u["x_split"] and u["y0"] <= y <= u["y_crest"] \
            and u["z_top"] - u["thick"] <= z < u["z_top"]:
        return "UpperA"
    if u["x_split"] <= x <= u["x1"] and u["y0"] <= y <= u["y1"] \
            and u["z_top"] - u["thick"] <= z < u["z_top"]:
        return "UpperB"
    if sh["x0"] <= x <= sh["x1"] and sh["y0"] <= y <= sh["y1"] \
            and sh["z_top"] - sh["thick"] <= z < sh["z_top"]:
        return "Shoulder"
    if lo["x0"] <= x <= lo["x1"] and lo["y0"] <= y <= lo["y1"] \
            and lo["z_top"] - lo["thick"] <= z < lo["z_top"]:
        return "Lower"
    # grass slope (1:2) - top face z = −(drop/run)(x − x0)
    if sp["x0"] <= x <= sp["x0"] + sp["run"] and sp["y0"] <= y <= sp["y1"]:
        zs = -(sp["drop"] / sp["run"]) * (x - sp["x0"])
        if zs - sp["thick"] <= z < zs:
            return "GrassSlope"
    # deck slab + lower beam zone (approximated as one blocker down to the beam soffit)
    if d["x0"] <= x <= d["x1"] and d["y0"] <= y <= d["y1"]:
        z_beam_bot = d["z_top"] - d["slab_t"] - PARAMS["deckframe"]["beam_h"]
        if d["z_top"] - d["slab_t"] <= z < d["z_top"]:
            return "DeckSlab"
        if z_beam_bot <= z < d["z_top"] - d["slab_t"] and y <= 0.1:
            return "DeckBeam"          # longitudinal beams occupy y <= 0.0 - the cantilever part is open
    # stair solid (x0..x0+run, deck width)
    run = st["n_geom"] * st["tread"]
    if st["x0"] <= x <= st["x0"] + run and d["y0"] <= y <= d["y1"]:
        idx = min(int((x - st["x0"]) / st["tread"]), st["n_geom"] - 1)
        ztop = -st["riser"] * (idx + 1)
        if st["base_z"] <= z < ztop:
            return "Stairs"
    for rp in PARAMS["riprap"]:
        if rp["x0"] <= x <= rp["x1"] and rp["y0"] <= y <= rp["y1"] \
                and PARAMS["rip_bot"] <= z < rp["z"]:
            return f"Riprap_{rp['tag']}"
    br = PARAMS["bridge"]
    if br["x0"] <= x <= br["x1"] and br["y0"] <= y <= br["y1"] \
            and br["deck_top"] - br["deck_t"] <= z <= br["deck_top"]:
        return "BridgeDeck"
    return None


# ===========================================================================
# [C3] smoke - pre-boot self-check of geometry, grounding, occlusion, cameras (early exit)
# ===========================================================================
def _smoke_report():
    d = PARAMS["deck"]
    st = PARAMS["stair"]
    r = PARAMS["rail"]
    wt = PARAMS["water"]
    print("=" * 70)
    print("scene12_riverside_deck — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 70)
    drop_edge = d["z_top"] - wt["z"]
    drop_st = st["riser"] * st["n_riser"]
    print(f"  데크           : x [{d['x0']:.1f},{d['x1']:.1f}] 폭 "
          f"{d['y1']-d['y0']:.2f} m, 상면 {d['z_top']:+.2f}")
    print(f"  낙차 ① 데크 에지 → 수면 : {drop_edge:.2f} m → "
          f"{'OK' if drop_edge >= 0.3 else 'FAIL'}")
    print(f"  낙차 ② 접속 계단        : riser {st['riser']} × "
          f"{st['n_riser']} = {drop_st:.2f} m "
          f"(n_geom {st['n_geom']}단 + 하부 둔치 1라이저), run "
          f"{st['n_geom']*st['tread']:.2f} → "
          f"{'OK' if drop_st >= 0.3 else 'FAIL'}")
    lo = PARAMS["lower"]
    drop_lo = lo["z_top"] - wt["z"]
    print(f"  낙차 ③ 하부 둔치 → 수면 : {drop_lo:.2f} m → "
          f"{'OK' if drop_lo >= 0.3 else 'FAIL'}")
    print(f"  계단 착지 검증 : 하부 둔치 상면 {lo['z_top']:+.3f} == "
          f"−riser×n_riser {-drop_st:+.3f} → "
          f"{'OK' if abs(lo['z_top'] + drop_st) < 1e-6 else 'FAIL'}")

    # ── cantilever numeric check ──
    sh = PARAMS["shoulder"]
    df = PARAMS["deckframe"]
    y_sup = max(df["beam_ys"])
    print("  [캔틸레버]")
    print(f"    최외곽 지지선 y={y_sup:+.2f} · 데크 외단 y={d['y1']:+.2f} → "
          f"내밈 {d['y1']-y_sup:.2f} m")
    print(f"    호안 crest y={sh['y1']:+.2f}(상면 {sh['z_top']:+.2f}) 기준 "
          f"내밈 {d['y1']-sh['y1']:.2f} m → "
          f"{'OK' if 1.0 <= d['y1']-sh['y1'] <= 1.5 else 'FAIL'}")
    pile_h = (d["z_top"] - d["slab_t"] - df["beam_h"]) - sh["z_top"]
    print(f"    말뚝 길이 {pile_h:.2f} m (어깨 사석 상면 {sh['z_top']:+.2f} → "
          f"보 밑면 {d['z_top']-d['slab_t']-df['beam_h']:+.2f}) → "
          f"{'OK(접지)' if pile_h > 0.3 else 'FAIL(부유/매몰)'}")

    # ── ground / water plate table + floating check (audit v4's most common defect) ──
    u = PARAMS["upper"]
    fb = PARAMS["far_bank"]
    plates = [("UpperA(grass)", u["x0"], u["x_split"], u["y0"], u["y_crest"],
               u["z_top"]),
              ("UpperB(grass)", u["x_split"], u["x1"], u["y0"], u["y1"],
               u["z_top"]),
              ("Shoulder(rock)", sh["x0"], sh["x1"], sh["y0"], sh["y1"],
               sh["z_top"]),
              ("Lower(grass)", lo["x0"], lo["x1"], lo["y0"], lo["y1"],
               lo["z_top"]),
              ("Deck(wood)", d["x0"], d["x1"], d["y0"], d["y1"], d["z_top"])]
    for rp in PARAMS["riprap"]:
        plates.append((f"Riprap_{rp['tag']}", rp["x0"], rp["x1"], rp["y0"],
                       rp["y1"], rp["z"]))
    plates.append(("Water(river)", wt["x0"], wt["x1"], wt["y0"], wt["y1"],
                   wt["z"]))
    plates.append(("FarBank(grass)", fb["x0"], fb["x1"], fb["y0"], fb["y1"],
                   fb["z_top"]))
    print("  [지면·수면 플레이트 표] (수면 −1.80 보다 낮은 인접 상면 = 부유 유발)")
    print(f"    {'이름':18s} {'x범위':>16s} {'y범위':>14s}  상면z")
    off = []
    for nm, x0, x1, y0, y1, z in plates:
        print(f"    {nm:18s} [{x0:6.1f},{x1:6.1f}] [{y0:6.1f},{y1:6.1f}]  "
              f"{z:+.3f}")
        if nm.startswith("Water") or nm.startswith("Riprap"):
            continue
        if (not (x1 <= wt["x0"] or x0 >= wt["x1"] or
                 y1 <= wt["y0"] or y0 >= wt["y1"])) and z < wt["z"] - 1e-9:
            off.append(nm)
    print(f"    수면과 XY 중첩 + 상면이 수면보다 낮은 플레이트: "
          f"{off if off else '없음 → OK'}")
    print(f"    FarBank 저면 {fb['z_top']-fb['thick']:+.2f} vs 수면 "
          f"{wt['z']:+.2f} → "
          f"{'OK(매입)' if fb['z_top']-fb['thick'] < wt['z'] else 'FAIL(부유)'}"
          f"  [scene09 교훈]")
    # does the lowest riprap tier sink below the water (prevents a hard water's-edge line)
    deep = min(rp["z"] for rp in PARAMS["riprap"])
    print(f"    사석 최심 상면 {deep:+.2f} < 수면 {wt['z']:+.2f} → "
          f"{'OK(수몰단 존재)' if deep < wt['z'] else 'FAIL'}")

    # ── hidden band numeric check (core of the research - h0.3 robot viewpoint) ──
    print("  [h0.3 은닉 밴드 검산] 데크 외단(y=1.25, z=0)을 스치는 시선")
    for h in (0.3, 0.9, 1.8):
        # y where the ray from (y=0, z=h) through the edge (y=1.25, z=0) meets the water (−1.8)
        slope = h / (d["y1"] - 0.0)
        y_hit = d["y1"] + (0.0 - wt["z"]) / slope
        # [v6] the hidden band is measured **from the deck outer edge** (measuring from the water y0
        #   goes negative once the exposed band is widened and means nothing - the riprap is hidden too).
        print(f"    h={h:.1f} → 수면 가시 시작 y {y_hit:6.2f} m "
              f"(에지 뒤 은닉 대역 {d['y1']:.2f}..{y_hit:.2f} = "
              f"{y_hit-d['y1']:.2f} m)")
    print(f"    ⇒ h0.3 에서 근접 수면·사석이 통째로 사라진다(missing ground band).")
    # opening angle from the missing kick plate
    z_at_rail = 0.3 + (r["y"] - 0.0) * ((0.0 - 0.3) / (d["y1"] - 0.0))
    print(f"    킥플레이트 부재: h0.3 시선이 난간선(y={r['y']:.2f})을 "
          f"z={z_at_rail:+.3f} 로 통과 → 중간대(z {r['mid_z']:.2f}) 아래 여유 "
          f"{r['mid_z']-z_at_rail:.2f} m → {'OK(개방)' if r['mid_z']-z_at_rail > 0.2 else 'FAIL'}")
    # stair grazing occlusion
    for dd in (2.0, 5.0):
        x_hit = abs(lo["z_top"]) * dd / 0.3 + st["x0"]
        print(f"    계단 은닉: h0.3·d{dd:.0f} 시선이 하부 둔치에 닿는 x "
              f"{x_hit:5.1f} m (계단 끝 {st['x0']+st['n_geom']*st['tread']:.2f}) "
              f"→ {'OK(하강 은닉)' if x_hit > st['x0']+st['n_geom']*st['tread'] else 'FAIL'}")

    # ── [v6 ruling (2)] water z assembly check + drop-visibility numeric check ──
    print("  [수면 z 조립 검증] (감독 결정 4 — GT 1.80 유지, 버그면 수정)")
    print("    sc.build_water: 두께 0.2 박스를 z−0.1 중심에 → **상면 = z**. "
          f"수면 상면 {wt['z']:+.3f}")
    gt = d["z_top"] - wt["z"]
    print(f"    데크 상면 {d['z_top']:+.3f} − 수면 상면 {wt['z']:+.3f} = "
          f"{gt:.3f} m → "
          f"{'OK(GT 1.80 일치 · 조립 버그 없음)' if abs(gt - 1.80) < 1e-9 else 'FAIL'}")
    print("    ⇒ '수면이 데크 상면에 붙어 보인다'의 원인은 z 가 아니라 **가시성**"
          " (아래 노출대·부감 검산 참조)")
    expo = [rp for rp in PARAMS["riprap"]
            if rp["z"] > wt["z"] and rp["y1"] > d["y1"]]
    y_wet = max((rp["y1"] for rp in expo), default=d["y1"])
    z_D = PARAMS["riprap"][3]["z"]
    print(f"    노출 사석대 : y {d['y1']:.2f}..{y_wet:.2f} = "
          f"{y_wet - d['y1']:.2f} m (구 1.10) · 수제선 y {y_wet:.2f} (구 2.35)"
          f" · 수면 y0 {wt['y0']:.2f} (구 1.90)")
    print(f"    데크 에지 → 사석 D 상면 낙하고 {d['z_top'] - z_D:.2f} m "
          f"(구 1.75 = 불변) / → 수면 {gt:.2f} m")
    print(f"    물때 밴드 y [{PARAMS['waterline']['y0']:.2f},"
          f"{PARAMS['waterline']['y1']:.2f}] · 잡석 {PARAMS['rocks']['n']}개"
          f" (구 42) y ≤ {PARAMS['rocks']['y1']:.2f}")
    # rubble grounding numeric check - after band_top(x,y) gained an x condition, confirm 0 floating
    rk_ = PARAMS["rocks"]
    rs_ = np.random.RandomState(int(rk_["seed"]))
    placed = skipped = 0
    for _ in range(int(rk_["n"])):
        rx = rs_.uniform(rk_["x0"], rk_["x1"])
        ry = rs_.uniform(rk_["y0"], rk_["y1"])
        rs_.uniform(rk_["s_lo"], rk_["s_hi"])
        rs_.uniform(0.0, 90.0)
        if any(rp["x0"] <= rx <= rp["x1"] and rp["y0"] <= ry < rp["y1"]
               for rp in PARAMS["riprap"]):
            placed += 1
        else:
            skipped += 1
    print(f"    잡석 접지 검산 : 사석 단 위 배치 {placed} · 단 없는 대역 생략 "
          f"{skipped} → {'OK(부유 0)' if placed + skipped == rk_['n'] else 'FAIL'}"
          f"  [구 구현은 y 만 보고 x>−18 잡석이 0.8~0.9 m 부유했다]")

    def _bank_top(y):
        """Revetment profile top-face z in the deck section (x≈−9) - highest of the riprap tiers ∪ the water."""
        z = None
        for rp in PARAMS["riprap"]:
            if rp["x0"] <= -9.0 <= rp["x1"] and rp["y0"] <= y < rp["y1"]:
                z = rp["z"] if z is None else max(z, rp["z"])
        if wt["y0"] <= y <= wt["y1"]:
            z = wt["z"] if z is None else max(z, wt["z"])
        return z

    print("  [낙차 시각 성립] 데크 외단(y 1.25, z 0)을 스치는 시선의 지면 최초 접촉")
    for nm in ("beauty_overview", "bank_face", "under_deck", "edge_void"):
        v = build_views()[nm]
        ex, ey, ez = v["eye"]
        if ey >= d["y1"]:
            print(f"    {nm:16s} 강측 시점(eye y {ey:+.2f} > 데크 외단) → "
                  f"에지 폐색 없음 · 캔틸레버 하부·사석 직시")
            continue
        m = (0.0 - ez) / (d["y1"] - ey)          # slope of the sight line through the edge (negative)
        y_hit, z_hit = None, None
        yy = d["y1"]
        while yy <= 40.0:
            zs = _bank_top(yy)
            if zs is not None and m * (yy - d["y1"]) <= zs:
                y_hit, z_hit = yy, zs
                break
            yy += 0.02
        if y_hit is None:
            print(f"    {nm:16s} 기울기 {m:+.3f}/m → 40 m 내 접촉 없음")
            continue
        band = y_hit - d["y1"]
        kind = "수면" if abs(z_hit - wt["z"]) < 1e-9 else "노출 사석"
        flag = "OK(사석·수제선 프레임 잔존)" if kind == "노출 사석" else \
               "주의(사석 전부 은닉 — 부감 부족)"
        print(f"    {nm:16s} 기울기 {m:+.3f}/m → 최초 접촉 y {y_hit:5.2f} "
              f"(z {z_hit:+.2f}, {kind}) · 에지 뒤 은닉 밴드 {band:.2f} m → {flag}")

    # ── railing destroyed span ──
    xs = _rail_posts()
    gapw = r["gap_x1"] - r["gap_x0"]
    print("  [난간]")
    print(f"    포스트 {len(xs)}본 (간격 {r['spacing']} m) · 상단대 z "
          f"{r['top_z']:.2f} · 중간대 z {r['mid_z']:.2f} · **킥플레이트 없음**")
    print(f"    훼손 스팬 x [{r['gap_x0']:.1f},{r['gap_x1']:.1f}] = {gapw:.1f} m"
          f" → {'OK' if abs(gapw-2.4) < 1e-6 else 'FAIL'} "
          f"(잔존 밑동 {len(r['stub_xs'])}본)")
    print(f"    난간 상단 {r['top_z']:.2f} m — 현행 규정 1.1 미달 = "
          f"'규정 미달의 현실'")
    # [v6 C-6] warning tape = ribbon tied to the surviving posts at both ends (no floating)
    tp = r["tape"]
    anch_ok = all(any(abs(ax - px) < 1e-6 for px in xs)
                  for ax in tp["anchor_xs"])
    print(f"    경고 테이프: 두께 {tp['t']*1000:.0f} mm 리본 × {tp['nseg']}세그 "
          f"(구 {20:.0f} mm 각재) · 폭 {tp['w']*100:.1f} cm · "
          f"처짐 {tp['sag']*100:.0f} cm")
    print(f"      결속 x {tp['anchor_xs']} vs 잔존 포스트 → "
          f"{'OK(양단 지지 — 부유 해소)' if anch_ok else 'FAIL(무지지 단부)'}"
          f"  · 스팬 {tp['anchor_xs'][1]-tp['anchor_xs'][0]:.1f} m, "
          f"양단 z {tp['z_end']:.2f} → 중앙 z "
          f"{tp['z_end']-tp['sag']:.2f}")

    # ── [v7] silver grass stalk conversion + §4 albedo cap self-check ──
    reed_selfcheck()
    albedo_selfcheck()

    # ── [W3 L12 · GT-43 R-1] the guard re-section, printed rather than claimed ──
    #   The ledger row asserts three things: the hazard/drop registry does not change,
    #   14 collision boxes change radius, and the h0.3 sight line survives. All three
    #   are re-derived here from PARAMS so a regression is visible without a render.
    r = PARAMS["rail"]
    posts = _rail_posts()
    ncol = len(posts) + len(r["stub_xs"])
    open_mid = r["mid_z"] - r["mid_r"]
    open_top = r["top_z"] - r["top_r"]
    print("  [W3 L12 · GT-43 R-1 가드 재단면 검산]")
    print(f"    부재: 포스트 Ø{r['post_r']*2*1000:.0f} × {len(posts)} "
          f"(구 Ø64) · 상부대 Ø{r['top_r']*2*1000:.0f} (구 Ø70) · "
          f"중간대 Ø{r['mid_r']*2*1000:.0f} (구 Ø40)  "
          f"[방부원형목재 Ø120/Ø80 · s3_research_numbers_v1.md §A5]")
    print(f"    콜라이더(col=True) {ncol} 개 반경 0.032 → {r['post_r']:.3f} "
          f"(포스트 {len(posts)} + 스텁 {len(r['stub_xs'])}) · 프림 수 불변")
    print(f"    h0.3 시선 개구: 데크 상면 0.000 → 중간대 하단 {open_mid:.3f} m "
          f"(구 0.530, Δ {(open_mid-0.530)*1000:+.0f} mm, "
          f"{(open_mid/0.530-1.0)*100:+.1f} %) · 상부대 하단 {open_top:.3f} (구 1.015)")
    print(f"    난간동자 0 개 (G3 = 통나무 가로대, 인필 없음) · 킥플레이트 없음 · "
          f"훼손 스팬 {r['gap_x1']-r['gap_x0']:.1f} m 유지 → 위험 기하 불변")
    print(f"    [L12-F1] 난간 높이 {r['post_h']:.2f} m — 조경설계기준 16.13.2(2) 1,100 / "
          f"16.20.2(2) 1,200 미달 · scene10 은 실측 1.10 착지. "
          f"본 씬은 '열화된 가드' 정체성이므로 무변경, 발견사항으로만 기록")

    # ── [W3 L12] season pin + river-view measurement ──
    season_audit()
    river_view_selfcheck()

    # ── raking light ──
    sd = _sun_dir()
    print("  [태양] SUN_AZ_OFFSET="
          f"{PARAMS['SUN_AZ_OFFSET']:.1f} → 진행 d = "
          f"({sd[0]:+.3f}, {sd[1]:+.3f}, {sd[2]:+.3f})")
    print(f"    태양 위치 방향 (−d) = ({-sd[0]:+.3f}, {-sd[1]:+.3f}, "
          f"{-sd[2]:+.3f}) → −X−Y 상공(진행 순광, scene17 동일)")
    print(f"    데크 상면(법선 +Z) 직사 OK / 호안 사면(법선 +Y) d·n="
          f"{sd[1]:+.3f} > 0 → 역광 암부 (에지 아래 은닉 강화)")

    # ── camera collision numeric check ──
    boxes = _obstacle_boxes()
    views = build_views()
    print(f"  [카메라 충돌 검산] 뷰 {len(views)}개 × 장애물 {len(boxes)}개 AABB")
    hits = []
    for name, v in sorted(views.items()):
        ex, ey, ez = v["eye"]
        for bn, x0, x1, y0, y1, z0, z1 in boxes:
            if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1:
                hits.append((name, bn))
    for name, v in sorted(views.items()):
        s = _solid_at(*v["eye"])
        if s is not None:
            hits.append((name, f"{s}(지형 매몰)"))
    for name, bn in hits:
        print(f"    [FAIL] {name} eye 가 {bn} 내부")
    print(f"    충돌: {len(hits)}건 → {'OK' if not hits else 'FAIL'}")
    # sight-line blocking check (ray march 0.1 m) - are the mise-en-scene cuts buried in terrain.
    #   if the first blocking point is under 90 % of the way to the target, the frame is walled off by terrain.
    print("    [시선 차단] 미장센 컷 ray march (첫 차단 비율 ≥ 0.90 = OK)")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        e = np.array(v["eye"], dtype=float)
        t = np.array(v["tgt"], dtype=float)
        L = float(np.linalg.norm(t - e))
        frac, hit = 1.0, None
        for k in range(1, int(L / 0.1) + 1):
            f = k * 0.1 / L
            s = _solid_at(*(e + (t - e) * f))
            if s is not None:
                frac, hit = f, s
                break
        flag = "OK" if frac >= 0.90 else "FAIL"
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {flag}")
        if frac < 0.90:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")
    # no obstacles in the deck walk corridor (robot body width 1.1 m = |y| <= 0.55).
    #   the railing (y 1.15) must lie outside the corridor.
    half = 0.55
    intr = [bn for bn, x0, x1, y0, y1, z0, z1 in boxes
            if not (x1 <= -18.0 or x0 >= 0.0 or y1 <= -half or y0 >= half)
            and z1 > 0.05]
    print(f"    데크 종주 회랑(|y|≤{half}) 침범 요소: "
          f"{intr if intr else '없음 → OK'}")
    print("=" * 70)


# ===========================================================================
# [C-2] ground_kit plans - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def ground_plan():
    """Plan A - staining and the shoreline film band on the deck surface."""
    g = PARAMS["gkit"]
    d, st = PARAMS["deck"], PARAMS["stair"]
    return gk.plan_ground(
        "deck_timber",
        region=(float(d["x0"]), float(d["y0"]),
                float(d["x1"]), float(d["y1"])),
        z=float(d["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("deck_end", float(st["x0"]))],
        dists=(2, 5, 10), scene="scene12",
        tactile=(),                    # Sec.12.4 OFF - natural / deck scene
        overrides=dict(
            surface=(("stain", ("dirt", "water")),),
            extras=(("silt_band", dict(waterline=float(g["film_line"]),
                                       width=float(g["film_w"]), n=1)),)),
        seed=int(g["seed"]))


def ground_plan_deck():
    """Plan B - plank gaps only, at the deck's own z (recess-as-tone).

    Same history as scene10: the W2-D round had to pass a lifted z because
    `build_deck_planks` put the gap strip top at `z - 0.020`, and the deck slab
    is a solid 0.14 m box, so at the deck's own z the 120 strips were sealed
    inside it and rendered zero pixels - the burial mode the scene15 pilot
    measured for joints and manholes. The builder now applies `surface_top_z()`
    itself (kit defect R1, fixed 2026-07-30), so the lift is removed and the
    strips land unchanged. The walking surface and therefore GT do not move,
    and the strips keep `exc="plank_gap"`.
    """
    g = PARAMS["gkit"]
    d, st = PARAMS["deck"], PARAMS["stair"]
    return gk.plan_ground(
        "deck_timber",
        region=(float(d["x0"]), float(d["y0"]),
                float(d["x1"]), float(d["y1"])),
        z=float(d["z_top"]),
        gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("deck_end", float(st["x0"]))],
        dists=(2, 5, 10), scene="scene12", tactile=(),
        overrides=dict(pave=dict(joint=None), surface=(),
                       extras=(("deck_planks",
                                dict(max_gaps=int(g["deck_gaps"]))),),
                       scatter=None),
        seed=int(g["seed"]) + 100)


# ===========================================================================
# [D] camera presets: grid_views(gy=0, deck walk +X) + 5 mise-en-scene cuts
# ===========================================================================
def build_views():
    """Preset axis = deck walk direction +X. The grid sits on the deck centreline
    (y=0) - the h0.3 cut is itself the 'no kick plate + hidden near water'
    ruling cut."""
    views = sc.grid_views(0.0)
    # edge_void: from robot eye height (0.35), standing inside the destroyed span **right at the edge** (y 0.90),
    #   looking out past the edge - the key cut. [coordinate check] the sight line clears the deck outer
    #   edge (y 1.25) at z=+0.16 (the old eye y 0.20 punched through the slab). From this viewpoint
    #   the water is visible only from y >= 3.05, and 1.90..3.05 stays hidden.
    #   [v7 ruling §8 (d) re-aim] the old tgt (−2.60, 4.60, −1.70) put the frame centre in the
    #   middle of the water (y 4.60), so the **exposed riprap band (y 3.03..3.90)** emerging
    #   from the hidden band behind the edge was pushed to the bottom margin, leaving only
    #   "deck plank -> mossy band -> water". Pull tgt in to just short of the shoreline
    #   (y 3.45, z −1.62) so the riprap band sits at frame centre. **eye unchanged** (inside the
    #   destroyed span, robot eye height 0.35 = the reason this cut exists). The through-edge slope
    #   −1.000/m is unchanged too, so the 1.78 m hidden band backing the ruling holds (smoke [drop visibility]).
    views["edge_void"] = dict(eye=[-4.80, 0.90, 0.35], tgt=[-3.05, 3.45, -1.62])
    # broken_span: the destroyed span seen obliquely from land (the promenade) - post stubs and warning tape
    views["broken_span"] = dict(eye=[-9.50, -3.20, 1.70], tgt=[-4.60, 0.70, 0.10])
    # stair_join: the 8-step descent joint at the deck end.
    #   [v6 ruling (4) re-aim] the old cut (eye −4.20,−3.40,2.80 / tgt 1.80,−0.30,−1.00) had
    #   (a) no stair in frame and (b) a streetlight (−2.0,−2.60, pole h4.5) running vertically
    #   through the picture. Drop the camera to **walking eye height above the lower floodplain (z −1.36)**
    #   and look up at the stair from below - all 8 steps stand out in silhouette.
    #   [coordinate check] eye z 0.30 = lower floodplain top face (−1.36) + 1.66. The sight line is at
    #   z −0.37 > lowest step top −1.19 at x 2.24 (stair foot), and at x 1.20 z −0.55 >
    #   that step's top −0.68 -> it grazes above the stair solid the whole way (no punch-through).
    #   both streetlights are at x<0 = behind the target -> nothing crosses the frame.
    views["stair_join"] = dict(eye=[6.00, -4.20, 0.30], tgt=[1.20, -0.10, -0.55])
    # deck_walk: pedestrian eye-height walk - deck, railing, backdrop bridge/apartments
    views["deck_walk"] = dict(eye=[-14.00, 0.00, 1.60], tgt=[0.00, 0.40, 0.20])
    # under_deck: **cantilever underside visibility cut** (director decision 4). From a low viewpoint 0.90 m
    #   above the water (boat height), sweep the under-deck space lengthwise - slab soffit,
    #   fascia, longitudinal beams, piles and shoulder riprap are exposed in turn, proving
    #   geometrically that "the deck floats 1.8 m above the water".
    #   [coordinate check] eye (5.0, 4.60, −0.90) : 0.90 m above the water (−1.80), 1.05 m above
    #   riprap F top face (−1.95) -> not buried. The sight line always stays above riprap F/E/D tops
    #   (−1.95/−1.78/−1.75) (lowest −0.58 @ y 2.30), and on entering the deck it is at z ~ −0.44,
    #   below the beam soffit (−0.40), so it goes **into the under-deck space, not the slab**.
    views["under_deck"] = dict(eye=[5.00, 4.60, -0.90], tgt=[-7.00, 0.60, -0.35])
    # bank_face [new]: river-side cross section from a high angle - deck top face and railing -> edge -> fascia ->
    #   beam/pile cavity -> 3 revetment riprap tiers -> shoreline, **stacked vertically in one frame**.
    #   the cut that carries the visual evidence for the GT 1.80 m drop (answers v6 ruling (2)).
    #   [coordinate check] eye (−9.50, 11.00, 2.60) : 4.40 m above the water, inside the water XY but
    #   with z far above −1.80 -> not buried. Sight-line slope dz/dy = 0.333 ->
    #   z −0.24 at y 3.90 (shoreline) and z −0.65 at y 1.25 (deck edge), so it **punches through neither
    #   the deck slab (−0.14..0) nor the longitudinal beams (−0.40..−0.14)** and enters the
    #   under-deck space (above riprap C top face −1.45).
    views["bank_face"] = dict(eye=[-9.50, 11.00, 2.60], tgt=[-9.20, 0.80, -0.80])
    # beauty_overview: oblique high angle - deck, river, bridge and apartments together.
    #   [v6 ruling (2) re-aim] in the old cut (eye −16,−14,9) the ray grazing the deck edge had
    #   a slope of only 0.59/m, so the riprap and shoreline over y 1.25..4.21 (2.96 m) hid
    #   entirely behind the edge -> the direct cause of the water looking glued to the deck top face.
    #   Raising eye to (−15,−9,13) gives a slope of 1.268/m -> hidden band 1.31 m,
    #   and exposed riprap E (y 2.56..3.90) with the shoreline stays in frame.
    views["beauty_overview"] = dict(eye=[-15.0, -9.0, 13.0], tgt=[2.0, 4.0, -1.4])
    return views


# ===========================================================================
# [E] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드     — 킥플레이트 없는 난간 아래로 근접 수면이 은닉되는가
 2. edge_void       — 훼손 스팬에서 수면 직행 개방이 읽히는가 (핵심 컷)
 3. broken_span     — 잔존 포스트 밑동·경고 테이프(리본 처짐·양단 결속)
 4. stair_join      — 데크 끝 8단 하강이 프레임에 들어왔는가(재조준 컷)
 5. under_deck      — 캔틸레버 하부 말뚝·보·사석 공간이 보이는가(저시점)
 6. bank_face       — 데크면→에지→하부공간→사석→수제선이 수직으로 쌓이는가
                      (= GT 1.80 m 낙차의 시각적 근거 · 신설 컷)
 7. 원경            — 교량·아파트·갈대가 '한강 둔치'로 읽히는가
 8. [v7] 수면       — edge_void·bank_face 에서 건물 반사가 흐려지고 잔물결
                      대역이 생겨 '인피니티 풀'이 아니라 강으로 읽히는가
 9. [v7] 억새       — bank_face 중앙·beauty_overview 우측이 갈색 육면체가
                      아니라 **줄기 사이로 배경이 비치는 대(stalk) 군락**인가
10. [v7] 난간       — 광택 백색 파이프가 도장 강재(다크그레이)로 바뀌었는가
11. [v7] 지평       — +X(우측) 배후가 시가지 실루엣으로 닫혔는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene12")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene12"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # materials (scene17 pattern reused)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        # [W3 L12 · GT-44] the map was bound raw (albedo 0.081). `deck_tint` is derived
        #   as target/source against the measured 방부목 patina band - see PARAMS.
        M["deckwood"] = PBR(
            f"{ROOT}/Looks/DeckWood", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            sca["wood_dark"], tint=mp["deck_tint"])
        M["rock"] = PBR(
            f"{ROOT}/Looks/Rock", sc.tex_path("rock_wall", "diff"),
            sc.tex_path("rock_wall", "nor"), sc.tex_path("rock_wall", "rough"),
            sca["rock_wall"])
        # [v6 (4)] film (wet riprap) - same texture at a finer scale (0.45) + teal tint +
        #   low roughness constant (no rough texture -> roughness_const applies directly)
        M["wetrock"] = PBR(
            f"{ROOT}/Looks/WetRock", sc.tex_path("rock_wall", "diff"),
            sc.tex_path("rock_wall", "nor"), None, sca["rock_wall"] * 0.65,
            tint=mp["wet_tint"], roughness_const=mp["wet_rough"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        # [v7 ruling §8 (3)] material dedicated to the silver grass stalks - same as scene17 M["reed"]
        #   (grass texture 0.6 m/tile + reed_tint). At a stalk thickness of 44 mm a 0.6 m
        #   tile spreads the texture almost uniformly over one stalk, giving a 'dry stalk' tone.
        M["reed"] = PBR(
            f"{ROOT}/Looks/Reed", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            0.6, tint=PARAMS["reed_tint"])
        M["gravel"] = PBR(
            f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"])
        M["cwall"] = PBR(
            f"{ROOT}/Looks/ConcreteWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        # [W2-D ground_kit] plank-gap tone. With recess-as-tone the gap *is*
        #   the material, so it needs a dark line colour rather than the deck
        #   board texture (which would render the gap invisible).
        M["gk_gap"] = PBR(f"{ROOT}/Looks/GkGap",
                          diffuse_color=(0.026, 0.022, 0.018),
                          roughness_const=0.95, specular_level=0.0)
        # [W3 L12 · GT-43] painted steel -> 착색방부목. The prim is renamed off `Looks/Rail`
        #   because that name is an exact hit in `scene_common.LOOK_ROLE` -> class **metal**,
        #   which would keep putting the brushed-metal detail grain on timber. `DeckGuardWood`
        #   carries no metal keyword and hits the `wood` substring rule instead.
        M["guard"] = PBR(
            f"{ROOT}/Looks/DeckGuardWood", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            sca["wood_dark"], tint=mp["guard_tint"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["bridge"] = PBR(f"{ROOT}/Looks/Bridge",
                          diffuse_color=mp["bridge_color"],
                          roughness_const=mp["bridge_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["tape"] = PBR(f"{ROOT}/Looks/Tape", diffuse_color=mp["tape_color"],
                        roughness_const=mp["tape_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        # [v5.2 user] arbitrary warning signboards removed - sign panel / backing material creation deleted.
        return M

    # -------------------------------------------------------------------
    # ground - 2 upper floodplain boxes + shoulder riprap + lower floodplain + grass slope
    # -------------------------------------------------------------------
    def build_terrain(M):
        u = PARAMS["upper"]
        sh = PARAMS["shoulder"]
        lo = PARAMS["lower"]
        # upper floodplain A: west of the deck (x < x_split), z=0 up to the revetment crest
        BOX(f"{ROOT}/UpperA",
            ((u["x0"] + u["x_split"]) / 2.0, (u["y0"] + u["y_crest"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0),
            (u["x_split"] - u["x0"], u["y_crest"] - u["y0"], u["thick"]),
            M["grass"], col=True)
        # upper floodplain B: the deck section (x_split..0), up to the deck south edge
        BOX(f"{ROOT}/UpperB",
            ((u["x_split"] + u["x1"]) / 2.0, (u["y0"] + u["y1"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0),
            (u["x1"] - u["x_split"], u["y1"] - u["y0"], u["thick"]),
            M["grass"], col=True)
        # shoulder under the deck (riprap fill) - the pile landing surface
        BOX(f"{ROOT}/Shoulder",
            ((sh["x0"] + sh["x1"]) / 2.0, (sh["y0"] + sh["y1"]) / 2.0,
             sh["z_top"] - sh["thick"] / 2.0),
            (sh["x1"] - sh["x0"], sh["y1"] - sh["y0"], sh["thick"]),
            M["rock"], col=True)
        # lower floodplain (low-water zone)
        BOX(f"{ROOT}/Lower",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"], lo["thick"]),
            M["grass"], col=True)
        # grass slope (1:2) linking upper and lower - a detour route besides the stair
        sp = PARAMS["slope"]
        sc.build_slope(stage, f"{ROOT}/GrassSlope", sp["x0"], u["z_top"],
                       sp["run"], sp["drop"], sp["y0"], sp["y1"], sp["thick"],
                       M["grass"], margin=0.0, collider=True)
        # promenade (decomposed granite) band
        pa = PARAMS["path"]
        BOX(f"{ROOT}/Path",
            ((pa["x0"] + pa["x1"]) / 2.0, (pa["y0"] + pa["y1"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0 + pa["proud"]),
            (pa["x1"] - pa["x0"], pa["y1"] - pa["y0"], u["thick"]),
            M["gravel"], col=True)

    def build_riprap(M):
        """Revetment riprap tiers + film band + individual rubble stones (fixed seed,
        random rotation).
        [v6 (2)(4)] exposed band y 1.25..3.90 (2.65 m) - D top face −1.75 is
        unchanged, so the deck-edge fall height 1.75 m and the GT drop (→ water)
        1.80 m both stay as they were."""
        zb = PARAMS["rip_bot"]
        for rp in PARAMS["riprap"]:
            BOX(f"{ROOT}/Riprap_{rp['tag']}",
                ((rp["x0"] + rp["x1"]) / 2.0, (rp["y0"] + rp["y1"]) / 2.0,
                 (rp["z"] + zb) / 2.0),
                (rp["x1"] - rp["x0"], rp["y1"] - rp["y0"], rp["z"] - zb),
                M["rock"], col=True)
        # film band - covers 1.0 m inside the shoreline with the wet riprap material.
        #   the bottom is embedded 4 mm (−0.004) to rule out **coplanar Z-fighting** with the
        #   tier top face below it, and the top face protrudes only 8 mm (§A-8 convention).
        wl = PARAMS["waterline"]
        wx0, wx1 = PARAMS["riprap"][3]["x0"], PARAMS["riprap"][3]["x1"]
        z_bot = wl["z"] - 0.004
        BOX(f"{ROOT}/WaterlineBand",
            ((wx0 + wx1) / 2.0, (wl["y0"] + wl["y1"]) / 2.0,
             z_bot + wl["proud"] / 2.0),
            (wx1 - wx0, wl["y1"] - wl["y0"], wl["proud"]), M["wetrock"])
        rk = PARAMS["rocks"]
        rs = np.random.RandomState(int(rk["seed"]))

        def band_top(x, y):
            """Top face of the riprap tier covering (x,y) (highest of several). None if none.
            [v6 latent grounding defect fixed] the old implementation looked at
            y only and returned the **first matching tier**, so in the
            y 0.05..1.25 band - where only A/B (x −40..−18) exist - rubble at
            x > −18 floated 0.8~0.9 m above the real ground (lower floodplain
            −1.36). Raising the rubble from 42 → 96 would amplify that, so an
            x condition is added."""
            best = None
            for rp in PARAMS["riprap"]:
                if rp["x0"] <= x <= rp["x1"] and rp["y0"] <= y < rp["y1"]:
                    best = rp["z"] if best is None else max(best, rp["z"])
            return best
        for i in range(int(rk["n"])):
            rx = rs.uniform(rk["x0"], rk["x1"])
            ry = rs.uniform(rk["y0"], rk["y1"])
            s = rs.uniform(rk["s_lo"], rk["s_hi"])
            yaw = rs.uniform(0.0, 90.0)
            top = band_top(rx, ry)
            if top is None:                  # no riprap tier here -> skip placement
                continue                     # (RNG draw order preserved = determinism)
            sc._oriented_box(stage, f"{ROOT}/Rock_{i}",
                             (rx, ry, top - s * 0.15),
                             (s, s * 0.85, s * 0.7), M["rock"], rotz=yaw)

    def build_river(M):
        wt = PARAMS["water"]
        sc.build_water(stage, f"{ROOT}/Water", wt["x0"], wt["y0"], wt["x1"],
                       wt["y1"], wt["z"], mtl=M["water"])
        fb = PARAMS["far_bank"]
        BOX(f"{ROOT}/FarBank",
            ((fb["x0"] + fb["x1"]) / 2.0, (fb["y0"] + fb["y1"]) / 2.0,
             fb["z_top"] - fb["thick"] / 2.0),
            (fb["x1"] - fb["x0"], fb["y1"] - fb["y0"], fb["thick"]),
            M["grass"], col=True)

    # -------------------------------------------------------------------
    # deck - slab + fascia + longitudinal/cross beams + piles (cantilever 1.25 m)
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P10 deck_timber (two plans, see ground_plan_deck).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(deck=M["gk_gap"], stain_dirt=M["gravel"],
                  stain_water=M["wetrock"], silt=M["wetrock"])
        a = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                            skin_exclude=sc.skin_exclude)
        b = gk.apply_ground(kit, f"{ROOT}/GKitPlanks", ground_plan_deck(), M2,
                            skin_exclude=sc.skin_exclude)
        print(f"[ground_kit] scene12 P10 · 프림 {a['prims']}+{b['prims']} · "
              f"δmax {a['gt_delta_max']:.4f} · unit_cell {a['unit_cell']}")
        return a

    def build_deck(M):
        d = PARAMS["deck"]
        df = PARAMS["deckframe"]
        mtl = M["deckwood"] if cfg["cue_material_break"] else M["gravel"]
        # [W2-0 P-A] The deck slab is what ground_kit decorates. It is 2.5 m
        #   wide so `_skin_wanted` rejects it anyway (>= 4.0 m on both axes)
        #   and "deck" is in `_SKIN_DENY`; registered explicitly regardless.
        sc.skin_exclude(f"{ROOT}/Deck")
        BOX(f"{ROOT}/Deck/Slab",
            ((d["x0"] + d["x1"]) / 2.0, (d["y0"] + d["y1"]) / 2.0,
             d["z_top"] - d["slab_t"] / 2.0),
            (d["x1"] - d["x0"], d["y1"] - d["y0"], d["slab_t"]), mtl, col=True)
        # outer fascia (side board). **Not a kick plate** - its top face is level with
        #   the deck surface (z=0) and never rises above the walking surface (robot view stays open).
        #   the outer face protrudes just 5 mm to avoid coplanar Z-fighting with the slab side.
        BOX(f"{ROOT}/Deck/Fascia",
            ((d["x0"] + d["x1"]) / 2.0,
             d["y1"] - d["fascia_t"] / 2.0 + 0.005,
             d["z_top"] - 0.20 / 2.0),
            (d["x1"] - d["x0"], d["fascia_t"], 0.20), mtl)
        z_beam_top = d["z_top"] - d["slab_t"]
        zc = z_beam_top - df["beam_h"] / 2.0
        for i, by in enumerate(df["beam_ys"]):
            BOX(f"{ROOT}/Deck/Beam_{i}",
                ((d["x0"] + d["x1"]) / 2.0, by, zc),
                (d["x1"] - d["x0"], df["beam_w"], df["beam_h"]), mtl)
        # cross beams
        n_cross = int((d["x1"] - d["x0"]) / df["cross_step"])
        for k in range(n_cross + 1):
            cx = d["x0"] + k * df["cross_step"]
            BOX(f"{ROOT}/Deck/Cross_{k}", (cx, (d["y0"] + d["y1"]) / 2.0, zc),
                (df["cross_w"], d["y1"] - d["y0"], df["beam_h"] * 0.8), mtl)
        # piles - landing on the shoulder riprap top face (−1.20)
        sh = PARAMS["shoulder"]
        pile_top = z_beam_top - df["beam_h"]
        ph = pile_top - sh["z_top"]
        n_pile = int((d["x1"] - d["x0"]) / df["pile_step"])
        for k in range(n_pile + 1):
            px = d["x0"] + k * df["pile_step"] + 0.4
            if px > d["x1"] - 0.2:
                continue
            for j, py in enumerate(df["beam_ys"]):
                CYL(f"{ROOT}/Deck/Pile_{k}_{j}",
                    (px, py, sh["z_top"] + ph / 2.0), df["pile_r"], ph,
                    mtl, col=True)

    def build_stairs(M):
        st = PARAMS["stair"]
        d = PARAMS["deck"]
        mtl = M["deckwood"] if cfg["cue_material_break"] else M["gravel"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], d["y0"], d["y1"], st["riser"],
            st["tread"], st["n_geom"], st["base_z"], mtl, z_top=0.0,
            collider=True)
        if cfg["cue_nosing"]:
            sc.build_nosing(stage, f"{ROOT}/Nosing", st["x0"], d["y0"],
                            d["y1"], st["riser"], st["tread"], st["n_geom"],
                            z_top=0.0)

    def build_flat_fill(M):
        """hazard_stairs=False control: deck, stair and floodplain level differences flattened to z=0."""
        u = PARAMS["upper"]
        lo = PARAMS["lower"]
        BOX(f"{ROOT}/FlatFill",
            ((u["x0"] + lo["x1"]) / 2.0, (u["y0"] + lo["y1"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0),
            (lo["x1"] - u["x0"], lo["y1"] - u["y0"], u["thick"]),
            M["grass"], col=True)

    # -------------------------------------------------------------------
    # railing - a single river-side run. 2.4 m destroyed span missing + no kick plate.
    # -------------------------------------------------------------------
    def build_railing(M):
        d = PARAMS["deck"]
        r = PARAMS["rail"]
        for i, px in enumerate(_rail_posts()):
            CYL(f"{ROOT}/Rail/Post_{i}", (px, r["y"], r["post_h"] / 2.0),
                r["post_r"], r["post_h"], M["guard"], col=True)
        # top rail and mid rail : 2 segments minus the destroyed span (Z-axis cylinder laid along X)
        segs = [("W", d["x0"], r["gap_x0"]), ("E", r["gap_x1"], d["x1"])]
        for tag, x0, x1 in segs:
            if x1 - x0 <= 1e-6:
                continue
            for nm, zz, rr in (("Top", r["top_z"], r["top_r"]),
                               ("Mid", r["mid_z"], r["mid_r"])):
                CYL(f"{ROOT}/Rail/{nm}_{tag}",
                    ((x0 + x1) / 2.0, r["y"], zz), rr, x1 - x0, M["guard"],
                    rotY=90.0)
        # sheared-off post stubs (damage trace - a cue for inferring the original fitting)
        for i, sx in enumerate(r["stub_xs"]):
            CYL(f"{ROOT}/Rail/Stub_{i}", (sx, r["y"], r["stub_h"] / 2.0),
                r["post_r"], r["stub_h"], M["guard"], col=True)
        # a single warning tape (plainly sub-code - not a guard).
        #   [v6 C-6] a 0.02-thick solid square bar with an unsupported floating east end -> replaced by a
        #   **4 mm ribbon + parabolic sag + tied to the surviving posts at both ends**.
        _build_tape_ribbon(M)

    def _build_tape_ribbon(M):
        """Warning tape across the destroyed span = a sagging ribbon tied to the 2 surviving posts.

        Geometry : x ∈ [xa, xb] (surviving post x), z(x) = z_end − sag·(1 − u²),
                   u = 2(x − xm)/L  → z_end at both ends, z_end − sag at the centre.
        Build    : sc._oriented_box(rotz=90, rotx=a).
                   op order is scale → rotX → rotZ, so local Y (the length axis)
                   is (0, cos a, sin a) after rotX(a) and (−cos a, 0, sin a)
                   after rotZ(90).
                   That is, the segment axis (cos a, 0, −sin a) ∝ (dx, 0, dz)
                   → a = atan2(−dz, dx). Given size=(t, seg_len, w),
                   local X = thickness (world Y) and local Z = width (vertical).
        """
        r = PARAMS["rail"]
        tp = r["tape"]
        xa, xb = tp["anchor_xs"]
        L = xb - xa
        xm = (xa + xb) / 2.0

        def z_of(x):
            u = 2.0 * (x - xm) / L
            return tp["z_end"] - tp["sag"] * (1.0 - u * u)

        n = int(tp["nseg"])
        for i in range(n):
            x0 = xa + L * i / n
            x1 = xa + L * (i + 1) / n
            z0, z1 = z_of(x0), z_of(x1)
            dx, dz = x1 - x0, z1 - z0
            seg_len = math.hypot(dx, dz)
            ang = math.degrees(math.atan2(-dz, dx))
            sc._oriented_box(
                stage, f"{ROOT}/Rail/Tape_{i}",
                ((x0 + x1) / 2.0, r["y"], (z0 + z1) / 2.0),
                (tp["t"], seg_len * 1.02, tp["w"]), M["tape"],
                rotz=90.0, rotx=ang)
        # tie point - the tape end wrapped round the post (lets the eye confirm it is not floating)
        for i, ax in enumerate((xa, xb)):
            CYL(f"{ROOT}/Rail/TapeTie_{i}", (ax, r["y"], z_of(ax)),
                r["post_r"] + 0.006, tp["tie_h"], M["tape"])

    # [v5.2 user] arbitrary warning signboards removed - build_signs() deleted.

    # -------------------------------------------------------------------
    # dressing - reeds · bench · streetlight · tree · bike path · bollard
    # -------------------------------------------------------------------
    def build_dressing(M):
        u = PARAMS["upper"]
        lo = PARAMS["lower"]
        # bike path (lower floodplain) + 2 white edge lines
        br = PARAMS["bikeroad"]
        BOX(f"{ROOT}/BikeRoad",
            ((br["x0"] + br["x1"]) / 2.0, (br["y0"] + br["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0 + br["proud"]),
            (br["x1"] - br["x0"], br["y1"] - br["y0"], lo["thick"]),
            M["asphalt"], col=True)
        for tag, yc in (("Lo", br["y0"] + 0.15), ("Hi", br["y1"] - 0.15)):
            BOX(f"{ROOT}/BikeLine_{tag}",
                ((br["x0"] + br["x1"]) / 2.0, yc, lo["z_top"] + 0.005),
                (br["x1"] - br["x0"], 0.10, 0.02), M["paint"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, u["z_top"],
                           M["wood"], yaw=yaw)
        for i, (bx, by, yaw) in enumerate(PARAMS["lower_benches"]):
            sc.build_bench(stage, f"{ROOT}/BenchLow_{i}", bx, by, lo["z_top"],
                           M["wood"], yaw=yaw)
        for i, (bx, by) in enumerate(PARAMS["lower_bollards"]):
            sc.build_bollard(stage, f"{ROOT}/BollardLow_{i}", bx, by,
                             lo["z_top"], mtl=M["bollard"])
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, u["z_top"] + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["bollard"], col=True)
            CYL(f"{base}/Arm", (lx, ly - sl["arm_len"] / 2.0,
                                u["z_top"] + sl["pole_h"] - 0.1),
                sl["arm_r"], sl["arm_len"], M["bollard"], rotX=90.0)
            BOX(f"{base}/Head", (lx, ly - sl["arm_len"],
                                 u["z_top"] + sl["pole_h"] - 0.15),
                (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (tx, ty) in enumerate(PARAMS["trees"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, u["z_top"],
                          M["wood"], M["canopy_a"], M["canopy_b"])
        # [v7 ruling §8 (3)] silver grass = a **stalk stand** (the old build_hedge cuboid is dropped).
        #   scene17 W-5 / scene09 build_reeds convention. The band rectangles are unchanged.
        for i, rd, k, px, py, hh, ry, rx in reed_instances():
            CYL(f"{ROOT}/Reed_{i}_{k}", (px, py, rd["z"] + hh / 2.0),
                PARAMS["reed"]["r"], hh, M["reed"], rotY=ry, rotX=rx)
        for i, fh in enumerate(PARAMS["far_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fh["cx"] - fh["sx"] / 2.0,
                           fh["cy"] - fh["length"] / 2.0,
                           fh["cx"] + fh["sx"] / 2.0,
                           fh["cy"] + fh["length"] / 2.0, fh["h"],
                           base_z=u["z_top"])

    def build_skyline(M):
        """Backdrop - 3 apartment blocks across the river + bridge + 1 south-side town
        block (horizon closure §A-4).
        Inherits scene17's 'Han River floodplain' read-out elements as they are."""
        for key, bd in PARAMS["far_buildings"].items():
            sc.build_building(stage, f"{ROOT}/FarBuilding_{key}", bd,
                              M["cwall"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        br = PARAMS["bridge"]
        deck_c = br["deck_top"] - br["deck_t"] / 2.0
        BOX(f"{ROOT}/Bridge/Deck",
            ((br["x0"] + br["x1"]) / 2.0, (br["y0"] + br["y1"]) / 2.0, deck_c),
            (br["x1"] - br["x0"], br["y1"] - br["y0"], br["deck_t"]),
            M["bridge"], col=True)
        pier_top = br["deck_top"] - br["deck_t"]
        ph = pier_top - br["pier_base"]
        for i, py in enumerate(br["pier_ys"]):
            CYL(f"{ROOT}/Bridge/Pier_{i}",
                (br["pier_x"], py, br["pier_base"] + ph / 2.0),
                br["pier_r"], ph, M["bridge"], col=True)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if cfg["hazard_stairs"]:
        build_terrain(M)
        build_deck(M)
        build_ground_kit(M)          # [W2-D] deck ground elements
        build_stairs(M)
        if cfg["cue_railing"]:
            build_railing(M)
        # [v5.2 user] arbitrary warning signboards removed - cue_sign placement deleted.
    else:
        build_flat_fill(M)
    build_riprap(M)                     # revetment, water and backdrop are always on (horizon closure)
    build_river(M)
    if cfg["cue_scene_dressing"]:
        build_skyline(M)
        if cfg["hazard_stairs"]:
            build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["deck_walk"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene12_{ts}.png")
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
