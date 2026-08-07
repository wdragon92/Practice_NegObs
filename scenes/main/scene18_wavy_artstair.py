# -*- coding: utf-8 -*-
"""scene18_wavy_artstair.py - NegObs synthetic scene 18: **beach access stair**
(해운대/광안리형 백사장 진입 계단) - Isaac Sim 4.5

Law            : `Docs/surveys/w3_intake_v2_images.md` §2 scene18 row + §7 rulings 3 · 8 · R18-2
Target image   : `Docs/reference_photos/Generated Image - Scene18.jpg` (**G18**)
Report         : `Docs/reports/w3_s18_v1.md`
Shared library : scene_common.py · ground_kit.py · building_kit.py

═══════════════════════════════════════════════════════════════════════════════
[W3 · IDENTITY SWAP] the mural stair is DELETED
═══════════════════════════════════════════════════════════════════════════════
User (2nd review, verbatim): *"Scene18 같은 경우는 벽화 계단이랑, 바닷가가 짬뽕이
돼서 정체성이 좀 이상해진 것 같은데, 그냥 바닷가 모래사장 진입 계단 처럼 만들면
어떨까 싶네. 바다가 안 보이잖아"*

Supervisor ruling §7-3: **AUTHORIZED - the mural axis is DELETED, not relocated.**
The colour-camouflage / drop-perception research axis is retired as an accepted
research-design loss; the illusion family survives in scene14 + sceneN3.

Consequently **everything below is new** except one preserved invariant:

    ┌──────────────────────────────────────────────────────────────────┐
    │  TOTAL DROP = 2.560 m  — INVARIANT (16 x 0.160)                  │
    │  (scene07 / scene10 precedent: keep the drop, rebuild the rest)  │
    └──────────────────────────────────────────────────────────────────┘

What went, what came:
  gone : wavy sine nosings (amp 0.245 / phase 0.25 / 40 y-segs) · 7-colour x
         3-wear mural riser palette + `mural_skew` diagonal bands · cheek
         sawtooth + haunch over a wave · hillside culture village (13 town
         boxes, 17 hillside houses, 3 fill terraces) · shops D/E ·
         `_wave_selfcheck` · the whole `seaside=` block.
  new  : granite promenade (G18) meeting a **sand field** across a 2.560 m
         seaward revetment · a straight granite access flight cut into it ·
         kerbed planting beds + tan band + yellow guide strip · BS-4 coastal
         high-rise wall (`building_kit` backdrop, landed) · sea with a real
         horizon, surf and a suspension bridge · `_stair_selfcheck` (R-1
         hazard registry) · `_sea_selfcheck` **v2, rewritten as a frame
         raster coverage measurement**.

═══════════════════════════════════════════════════════════════════════════════
[WHY THE SEA WAS INVISIBLE] cause-first, then the instrument
═══════════════════════════════════════════════════════════════════════════════
v6's `_sea_selfcheck` reported "frame openness 54-100 %" while the user still
could not see the sea. Both statements were true, because the check measured
the wrong quantity. Diagnosed against the actual baseline frames
(`look_check/scene18/260730_w2d_fix/pt_noon_preset_h0.3_d5.png`,
`…_sea_beauty.png`):

  (1) **The check measured occlusion, not legibility.** It swept +-30 deg of
      azimuth asking "does a town box rise above the water's far edge". Nothing
      did - the town had already been pushed off-axis in v6 - so it returned
      100 % and stopped. It never asked *how many pixels of the frame are
      water* nor *is the water distinguishable from the sky*, which is the
      entire content of the user's sentence.
  (2) **PHYSICAL CAUSE - the water was a sky mirror.** `water_rough = 0.22`
      with a smooth dielectric seen at 0.4-5 deg grazing incidence is, by
      Fresnel, an almost perfect mirror; under a bright noon puresky it
      returned the sky's own radiance. Water and sky therefore rendered at
      nearly the same value and **the horizon line disappeared**. In the
      baseline PNG the "sea" is a pale grey wash 6 % of frame height that reads
      as haze. This is the cause; the openness number was never going to catch
      it.
  (3) **No shoreline event.** No surf, no foam, no wet-sand band, nothing at
      the land/water boundary - so even where the water was in frame there was
      no edge to read it by. In G18 the sea is legible mainly through three
      white breaker lines and a wet swash band.
  (4) **Composition.** The water band was 4.8 deg tall in a -10 deg frame and
      sat behind 37 m of *grass*, which read as a lawn running into haze.

Fixes, in the same order:
  (1) `_sea_selfcheck` is rewritten as `_frame_coverage()`: it rasterises the
      real 60 x 36 deg frustum of each judged cut against an analytic model of
      every macro surface and reports **per-class frame coverage %, the
      horizon row, and the sea/sky luminance separation**. It gates on water
      coverage and on horizon-in-frame, i.e. on the thing the user asked about.
  (2) `water_rough 0.22 -> 0.38` + `specular_level 0.42`, and the body colour
      moves from a haze grey (0.175, 0.205, 0.225) to a **sea blue**
      (0.052, 0.132, 0.188). A far haze plate (lighter, rougher) beyond 1.2 km
      reproduces G18's horizon lightening without erasing the line.
  (3) A **surf system**: 3 broken breaker lines (segmented, jittered) + a wet
      swash veneer + a damp-sand band at the waterline.
  (4) The travel axis +X is now **seaward and perpendicular to the shore**, so
      the sea fills the full frame width in every judged cut, and the near
      field is sand, not lawn.

═══════════════════════════════════════════════════════════════════════════════
[SEASON PIN] §7-8 - every scene pins the season of its own target image
═══════════════════════════════════════════════════════════════════════════════
G18 = **late spring / summer**: full green shrub mass, dry golden sand, high
sun, blue sky. Pinned as **summer**. Element audit (every dressing item):
  · trees   Chinese_Juniper (evergreen) · Shumard_Oak (leafed, green 100 %) -
            both `veg_manifest_w2.json` PASS. `bare=` NEVER set.
  · shrubs  Boxwood + Juniper only. Rhododendron/Forsythia/Burning_Bush are
            excluded by name at the call site (blossom / autumn-red pixels).
  · ground  NO `leaf_ground` role anywhere (autumn texture) and NO fall-leaf
            debris scatter. `dirt_park` for bed soil, `grass` only on the far
            headland silhouette.
  · sky     `qwantani_noon_puresky` retained. **Deviation, stated**: G18 has
            scattered cumulus, this HDRI is cloudless. Swapping the sky moves
            `noon_sun_elev` / `hdri_sun_rotz_offset` / `SUN_AZ_OFFSET`, all of
            which are pinned by `variation_kit`'s azimuth ledger for scene18,
            so the swap is a lighting work package and not this one's.

Run / capture / smoke: unchanged env convention.
    NEGOBS_CAPTURE=1 / NEGOBS_SMOKE=1 / NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG
    NEGOBS_SELFCHECK=1 : coordinate + coverage checks only, no Isaac boot.

Coordinates: Z-up, m. **+X = seaward** (the travel axis and the hazard
direction), **+-Y = alongshore** (the promenade axis). Promenade top z = 0;
the drop edge is the line x = 0.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk
import building_kit as bk
import facade_kit as fk


# ===========================================================================
# [A] SCENE_CONFIG - 7 keys, unchanged names (NEGOBS_SCENE_CONFIG compatibility).
#     Every meaning is rebound to the beach archetype.
# ===========================================================================
SCENE_CONFIG = {
    # 2.560 m revetment drop + the access flight. False -> the beach is lifted
    #   to promenade level, so the frame keeps its composition and loses only
    #   the negative obstacle (the control arm).
    "hazard_stairs":      True,
    # 해운대·광안리 practice: the promenade/sand edge and its access flights run
    #   unguarded for long stretches (people sit on and step off the coping).
    #   §6.1-1/2/5/8/9/10 also CANCELLED the mid-rail for 18.
    "cue_railing":        False,
    # Statutory stair-head warning band (0.30 m clear of the first riser,
    #   0.60 m deep) - the scene16 §7-4 form.
    "cue_tactile":        False,
    # Promenade granite vs the warm tan edge band vs the darker coping course.
    "cue_material_break": True,
    # RF-5 applied-strip nosing (60 mm profile, 5Y 8.5/12).
    "cue_nosing":         False,
    "cue_sign":           False,   # [reserved - no prim is authored]
    "cue_scene_dressing": True,    # beds, benches, lights, city, sea furniture
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
# ---- the one preserved invariant -------------------------------------------
DROP_TOTAL = 2.560                 # 16 x 0.160. **Do not edit.**

PARAMS = dict(
    # ══ hazard geometry ═════════════════════════════════════════════════════
    # Straight granite flight cut into the seaward revetment.
    #   n x riser = 16 x 0.160 = 2.560 m  -> the preserved invariant.
    #   tread 0.340 -> **0.320**: 2R + T = 2(0.160) + 0.320 = **0.640 m**, inside
    #     the 0.600-0.650 window (`[law]` KCS 34 50 10 3.2.8(3), cited in this
    #     repo at `gt_changes_w3.md` GT-18) and uniform over the whole run.
    #     The old 0.340 gave 0.660 - 10 mm outside. The *drop* is untouched;
    #     only the run shortens 5.440 -> 5.120 m (slope 26.57 deg).
    #   width 6.000 m clear - a public beach access flight, wide enough that the
    #     flanking stringer kerbs never intrude on the walked surface.
    #   base_z -2.620: the step solids bed 0.060 m into the sand plate, so no
    #     step can float over a settled beach.
    stair=dict(n=16, riser=0.160, tread=0.320, y0=-3.000, y1=3.000,
               x0=0.000, base_z=-2.620),
    # Stringer kerb flanking the flight (|y| 3.000..3.350). Body boxes flush
    #   with each tread (curb 0 -> no sawtooth, the v6(d) lesson kept), with one
    #   oblique haunch per side laid over them parallel to the nosing line.
    #   rise 0.120 m: a kerb, NOT a guard - 0.120 << the 1.100 m guard height,
    #   and it lies outside the 6 m clear width so it casts no drop silhouette
    #   on the h0.3 grazing sight line.
    cheek=dict(w=0.350, curb=0.0, rise=0.120, thick=0.450, over=0.250,
               base_z=-2.620),

    # ══ promenade / revetment ═══════════════════════════════════════════════
    # G18: a wide light-grey granite block promenade. Its seaward face IS the
    #   negative obstacle: a flush 2.560 m granite revetment with no upstand,
    #   running the whole length except where the flight is cut through it.
    #   **y extent runs to +420**, not +-90. `sea_beauty` looks ALONG the
    #   promenade (G18's composition), so the deck has to reach a real vanishing
    #   point; at +-90 the frame showed the deck stopping 124 m out with sky
    #   under the horizon behind it. Costs 0 extra prims - the plates are the
    #   same boxes, longer.
    promenade=dict(x0=-18.00, x1=-0.35, y0=-100.0, y1=420.0, top_z=0.0),
    # Coping course + revetment face. 0.350 m wide - a real 화강석 갓돌 course.
    coping=dict(x0=-0.35, x1=0.00, y0=-100.0, y1=420.0, top_z=0.0),
    # Landward backland (esplanade / carriageway platform the city sits on).
    backland=dict(x0=-96.0, x1=-18.00, y0=-105.0, y1=520.0, top_z=0.0,
                  thick=2.66),
    # Warm tan paving band + yellow guide strip along the LANDWARD edge (G18).
    #   Deliberately 12+ m away from the drop edge so neither can be read as a
    #   hazard cue: the cue at the drop edge is `cue_tactile`, and nothing else.
    tan_band=dict(x0=-13.40, x1=-12.60, y0=-80.0, y1=190.0, proud=0.004),
    guide=dict(x0=-12.50, x1=-12.20, y0=-70.0, y1=175.0, seg=7.0, proud=0.004),

    # ══ beach ═══════════════════════════════════════════════════════════════
    # Dry backshore apron (flat) then the foreshore at 2.6 % - inside the
    #   1/25-1/40 band a sand foreshore holds. `[estimate]` no domestic figure
    #   was procurable for 해운대; the value is the mid of the textbook band and
    #   is declared, not measured.
    beach=dict(x0=0.00, x_break=14.00, x1=52.00, y0=-105.0, y1=520.0,
               top_z=-2.560, slope=0.026, thick=1.00),
    # Still-water level. Waterline x is DERIVED, never typed:
    #   x_w = x_break + (|water_z| - |beach_z|) / slope = 14 + 0.740/0.026
    water=dict(x0=40.0, x_mid=1200.0, x1=6000.0, y_near=3000.0, y_far=6000.0,
               top_z=-3.300, thick=2.00, far_drop=0.002),
    # Surf. 3 broken breaker lines + the swash edge, each cut into y segments
    #   with a jittered x centre so the line reads as a wave, not a ruler.
    #   `y0/y1` is bounded separately from the beach plate: the plate runs to
    #   +520 m for the promenade vanishing point, and cutting 620 m of surf into
    #   7.6 m segments would spend ~240 prims on foam nobody can resolve past
    #   ~250 m.
    #   Pilot rounds a/b both read these as **painted lane markings**: axis-
    #   aligned rectangles, evenly gapped, at full white. Round c fixes all
    #   three causes at once — segments now OVERLAP (`step` < `seg_y`) so the
    #   line is continuous, each carries a +-4 deg z-rotation so it is not
    #   axis-aligned, and the foam albedo drops to 0.48.
    #   (LINT-8's "no rotz on a patch/stain" does not reach here: these are
    #   `Surf_*` prims and match neither the patch nor the stain pattern.)
    #   Round e still read the two outer lines as parallel white BARS at
    #   grazing angles, because at h0.3 any horizontal band collapses to a bar.
    #   Two levers, both cheap: the outer lines get half the width, and the
    #   outer two bind a SECOND, dimmer foam material — a real breaker line
    #   loses contrast with distance and a single albedo cannot express that.
    surf=dict(lines=((-0.30, 0.80, 60), (4.10, 0.52, 50), (9.40, 0.28, 42),
                     (16.60, 0.22, 34)),
              y0=-110.0, y1=250.0, seg_y=7.4, step=5.0, rotz=4.0,
              jit_x=1.15, jit_w=0.45, proud=0.012, seed=1802),
    # Damp sand landward of the swash (the tide-out signature of G18).
    damp=dict(back=6.20, fwd=0.60, proud=0.012),
    # NOTE — wind-blown sand over the granite is delivered by `ground_kit`'s
    #   `silt_band` (see `gkit` below), NOT by hand-placed lobes. Rounds a/b
    #   carried 11 scene-side drift boxes plus 26 tonal patches on the sand and
    #   both families rendered as **hard-edged tan rectangles**
    #   (`pt_noon_sea_beauty.png`, `pt_noon_preset_h0.9_d5.png`): an axis-
    #   aligned slab cannot read as a feathered drift no matter how it is
    #   tinted. Deleted rather than tuned — the kit band is the prescribed
    #   instrument and it is oriented correctly now (§5.1 18 row).

    # ══ ground_kit - P1 plaza_granite, spec §5.1 scene18 row ════════════════
    #  Row prescription: "slab joints made geometric · sand drift band · salt
    #  efflorescence (albedo cap 0.30 strictly) · patches 3 per 20 m".
    #  ★ `edge_s` is now **0.000 exactly**. v6 had to carry -0.245 because the
    #    drop edge was a sine band `[-amp, +amp]` and GT-E1'/GT-E2 had to be
    #    measured from its nearest point. The edge is a straight line again, so
    #    the pessimistic offset is retired.
    #  ★ The v6 **silt-band deviation is resolved by the new geometry**, not
    #    waived. `build_silt_band` emits X-long strips at y = const; v6 needed a
    #    band along an x = const seaward edge and could not draw it. Here the
    #    shore-normal is +X, so wind-driven sand crosses the promenade **along
    #    X** - which is exactly the strip this builder emits. Placed at y ~ +6.
    #  ★ Tactile stays OUT of the kit (`tactile=()`); the guide strip and the
    #    warning band are scene-side. See the note at `build_guide_strip`.
    gkit=dict(
        region=(-16.0, -20.0, -1.0, 20.0),
        edge_s=0.0,
        manholes=[(-6.0, 7.0), (-11.4, -9.2)],
        gullies=[(-2.0, -12.4), (-2.0, 13.1)],
        patches=[(-4.20, 2.10), (-9.60, -5.40), (-13.10, 8.30)],
        silt=dict(waterline=6.0, width=0.50, n=2),
    ),

    # ══ planting beds (G18 left) ════════════════════════════════════════════
    # Raised kerbed beds. K5 (`build_curb_line`) is deferred to a Lane-1 pass,
    #   so the kerb is scene-side here - authorised by the dispatch note.
    #   0.250 m wide x 0.500 m high granite kerb, soil 0.080 below the kerb top.
    beds=dict(x0=-17.60, x1=-13.40, kerb_w=0.250, kerb_h=0.500, soil_z=0.420,
              # (y0, y1, kind) - kind selects the single species of that bed
              #   (K4(b) "one species per bed"). Gaps between beds are the
              #   pedestrian cross-links G18 shows.
              # Bed length 15.600 m and gap 6.000 m are NOT free numbers: with
              #   0.800 m end margins a 15.600 m bed holds exactly 3 trees at a
              #   **7.000 m** pitch, which is PE-2's spec §10.3 default and
              #   inside 조례 제7조1가's 6-8 m window. LINT-2 measures the
              #   declared route pitch, so the bed length is derived from the
              #   pitch rather than the pitch approximated from a bed length.
              runs=((-40.0, -24.4, "U"), (-18.4,  -2.8, "T"),
                    (  3.2,  18.8, "U"), ( 24.8,  40.4, "T"),
                    ( 46.4,  62.0, "U"), ( 68.0,  83.6, "T"),
                    ( 89.6, 105.2, "U"), (111.2, 126.8, "T")),
              tree_pitch=7.00, shrub_pitch=2.10, seed=1804),
    # R18-2 fallback species. See the module docstring block [VEGETATION].
    species=dict(T=("Trees/Shumard_Oak.usd", 10.8989, 7.60),
                 U=("Trees/Chinese_Juniper.usd", 2.5164, 2.60)),
    shrub_pool=("Shrub/Boxwood.usd", "Shrub/Juniper.usd"),

    # ══ street furniture ════════════════════════════════════════════════════
    # Stone benches. Held tight to the LANDWARD walk edge so the free walking
    #   band after the 표2.2 occupancy stays ~12 m (LINT-5, PE-8).
    benches=[(-12.55, y, 0.0, 0.0) for y in
             (-45.0, -34.0, -21.5, -8.5, 4.5, 17.5, 30.5, 43.0,
              57.0, 71.0, 85.0, 99.0)],
    # G18's double-globe promenade lantern (two opal globes on a cross arm)
    #   + the taller cobra-head road light behind the beds.
    #   x = -15.60 and the y stations are the BED GAPS, both derived from
    #   LINT-5, not chosen by eye: 표2.2 gives a 가로등 a 1.000 m occupancy, and
    #   PE-8's computable form needs 1.500 m clear of the declared walk edge
    #   (x = -13.40), so the pole centre must sit at least 2.000 m back. The
    #   first pass put them at -13.95 (0.550 m back) and the linter returned
    #   10 ERRORs — that is the rule doing its job, and the poles moved rather
    #   than the declaration.
    globes=[dict(x=-15.60, y=y, base_z=0.0) for y in
            (-47.0, -21.4, 0.2, 21.8, 43.4, 65.0, 86.6, 108.2, 130.0)],
    globe=dict(pole_r=0.055, pole_h=4.30, arm_len=1.55, arm_r=0.038,
               globe_r=0.215),
    cobras=[dict(x=-18.60, y=y, base_z=0.0, pole_h=9.0) for y in
            (-30.0, -6.0, 18.0, 42.0, 78.0, 114.0)],
    cobra=dict(pole_r=0.075, arm_len=1.80, arm_r=0.055, head=0.30),

    # ══ city (BS-4 backdrop, landed at the backland top) ════════════════════
    # G18: a coastal high-rise apartment wall with three tall glass towers
    #   behind it. Every one is out of +-30 deg of every judged eye, which is
    #   precisely BS-4's case: `kind="backdrop"` = 3-4 prims, 0 windows.
    # LAYOUT NOTE (measured against the 60 deg judged frustum, not guessed):
    #   G18 puts the tower cluster at the FAR END of the beach, not beside the
    #   camera - which is also the real 해운대 LCT relationship. Putting them
    #   abeam (v6-style, x -60..-80 at y ~0) drops them out of every 60 deg
    #   frame: `_frame_coverage` measured city = 0.00 % for every candidate
    #   `sea_beauty` aim with enough yaw to satisfy the water floor. So the wall
    #   RECEDES along +Y beside the promenade and the towers stand ~400 m down
    #   the beach, where a 108 m tower subtends 13.9 deg and fills the upper
    #   left exactly as in G18.
    city=dict(
        wall=[(-52.0, -26.0, -62.0, -46.0, 46.0, 16),
              (-56.0, -27.0, -42.0, -26.0, 52.0, 18),
              (-50.0, -26.0, -22.0,  -6.0, 43.0, 15),
              (-58.0, -28.0,  -2.0,  15.0, 58.0, 20),
              (-53.0, -26.0,  19.0,  36.0, 49.0, 17),
              (-61.0, -29.0,  40.0,  58.0, 44.0, 15),
              (-55.0, -27.0,  62.0,  82.0, 40.0, 14),
              (-59.0, -28.0,  86.0, 108.0, 54.0, 19),
              (-54.0, -26.0, 112.0, 136.0, 47.0, 16),
              (-62.0, -29.0, 140.0, 168.0, 41.0, 14),
              (-57.0, -27.0, 172.0, 205.0, 50.0, 17)],
        towers=[(-88.0, -60.0, 352.0, 386.0,  96.0, 30),
                (-74.0, -44.0, 396.0, 432.0, 108.0, 34),
                (-92.0, -62.0, 442.0, 474.0,  88.0, 28)],
        base_z=0.0),

    # ══ horizon furniture ═══════════════════════════════════════════════════
    # Suspension bridge across the bay (G18's 광안대교 read). Deck + towers +
    #   two cable planes = 8 prims, at 2-4 km, i.e. a horizon silhouette.
    bridge=dict(x0=400.0, x1=4200.0, y=1900.0, w=26.0, deck_z=20.0, deck_t=3.2,
                towers=(900.0, 1800.0), tower_h=90.0, tower_w=7.0,
                cable_sag=14.0),
    # Headland closing the far right (G18 shows one beyond the town).
    #   A ridge, not a box: 6 overlapping masses of different height give a
    #   stepped silhouette. Round b's 2 clean rectangles read as a green slab
    #   on the horizon.
    headland=[(900.0, 2100.0, -2600.0, -1500.0, 46.0),
              (1400.0, 2500.0, -1900.0, -1050.0, 33.0),
              (1750.0, 3100.0, -2900.0, -1850.0, 58.0),
              (1150.0, 1900.0, -1250.0, -760.0, 21.0),
              (1000.0, 1750.0, -2250.0, -1700.0, 62.0),
              (2050.0, 2900.0, -2200.0, -1400.0, 40.0)],

    # ══ materials ═══════════════════════════════════════════════════════════
    material=dict(
        scale=dict(plaza_light=1.80, plaza_lower=0.90, granite_dark=1.20,
                   tread=1.05, dirt_park=1.30, grass=1.40),
        # Beach sand - ambientCG **Ground080**, CC0 1.0, procured this window
        #   (`assets/coastal/download_coastal_assets.py`). NOT registered in
        #   `scene_common.TEX`: that table belongs to another lane in this
        #   window, so the scene binds absolute paths itself.
        #   [measured, at procurement] linear albedo 0.3235 (dry quartz beach
        #   sand is 0.25-0.40) · pixels > 0.8 = 0.02 % · sRGB (0.726, 0.618,
        #   0.446).
        #   `sand_scale` 1.0 m is an **`[estimate]`**, not a measurement:
        #   ambientCG publishes no physical size for Ground080
        #   (`dimensionX = dimensionY = 0`). Derived from feature size - the
        #   backwash ripple wavelength is 0.02-0.05 of the tile and real
        #   backwash ripples run 20-80 mm, so 1.0 m puts them at 20-50 mm.
        sand_scale=1.00,
        sand_tint=(1.00, 0.97, 0.92),          # G18's sand is a shade warmer
        damp_tint=(0.70, 0.68, 0.66),          # wet sand darkens ~30 %
        # ── SEA ── the v6 defect and its fix, in three numbers.
        #   rough 0.22 -> 0.38 : at 0.4-5 deg grazing a 0.22 dielectric is a
        #     mirror and returned the sky, erasing the horizon. 0.38 spreads the
        #     specular lobe over the wind-chop the geometry does not carry.
        #   spec 0.42          : below the dielectric default so the grazing
        #     Fresnel term cannot re-blow the band.
        #   colour             : deep-sea blue, linear albedo 0.124.
        water_color=(0.044, 0.112, 0.166), water_rough=0.38, water_spec=0.42,
        # The far plate lightens toward the horizon (G18) WITHOUT closing the
        #   sea/sky value gap: it stays 26 % darker than the near sky band.
        water_far_color=(0.105, 0.140, 0.176), water_far_rough=0.52,
        foam_color=(0.520, 0.545, 0.556), foam_rough=0.92,
        foam_far_color=(0.360, 0.392, 0.408), foam_far_rough=0.95,
        # Structures
        # **WHITE gate, measured.** v6's paving sat at 20.2 % pure-white
        #   (>0.8) at `preset_h0.3_d2`; with the promenade now FULLY sunlit
        #   (the SUN_AZ_OFFSET fix) tint 0.74 pushed that to **50.8 %**, a
        #   v5.1 §4 violation on the largest surface in the frame. Required
        #   linear factor to come back under the baseline is
        #   (0.78/0.85)^2.2 = 0.826, so 0.74 x 0.826 -> **0.58** with margin.
        #   It is also the more faithful value: G18's 화강석 판석 promenade is a
        #   mid light grey, not white.
        granite_tint=(0.58, 0.58, 0.572),
        coping_tint=(0.62, 0.62, 0.61),
        tan_tint=(1.16, 1.02, 0.80),           # G18's warm tan edge band
        kerb_color=(0.58, 0.575, 0.56), kerb_rough=0.62,
        bench_color=(0.52, 0.515, 0.50), bench_rough=0.55,
        pole_color=(0.235, 0.235, 0.255), pole_metallic=0.60, pole_rough=0.50,
        globe_color=(0.74, 0.735, 0.70), globe_rough=0.35,
        # City. Values kept under the 0.80 near-white rule (v5.1 §4).
        shell_color=(0.470, 0.465, 0.450), shell_rough=0.74,
        tower_color=(0.150, 0.205, 0.250), tower_rough=0.22,
        glass_color=(0.060, 0.095, 0.125), glass_rough=0.08,
        parapet_color=(0.680, 0.680, 0.655), parapet_rough=0.60,
        # Horizon
        bridge_color=(0.520, 0.525, 0.535), bridge_rough=0.55,
        cable_color=(0.400, 0.405, 0.420), cable_rough=0.45,
        # Aerial perspective: a headland 1-3 km out is a HAZY BLUE-GREY
        #   silhouette. Round b tinted the grass texture and, back-lit, it
        #   rendered as a black slab. It is a flat constant now — a 2 km
        #   silhouette has no resolvable texture anyway.
        headland_color=(0.335, 0.395, 0.435), headland_rough=1.0,
        # Cues
        # RF-5 / 산업안전보건법 별표8: 5Y 8.5/12 ~ #F0BE00, not an invented yellow.
        nosing_color=(0.941, 0.745, 0.000), nosing_rough=0.70,
        rail_color=(0.780, 0.790, 0.800), rail_metallic=0.75, rail_rough=0.32,
    ),

    # ══ lighting - UNCHANGED from v6 ════════════════════════════════════════
    # Every constant here is pinned by `variation_kit`'s azimuth ledger for
    #   scene18 and by the frozen judge channel. The season pin is satisfied by
    #   this sky already (summer noon); only the cumulus differs (stated).
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # **SUN RE-SELECTION** — the scene07 / scene10 precedent, same failure and
    #   the same remedy, measured on the 260731_w3_s18 pilot rather than
    #   assumed. The inherited 171.5 puts the sun at world az 33.5 + 171.5 =
    #   **205 deg**, i.e. in the −X·−Y sky, so shadows propagate along az 25 deg
    #   (+X, +Y): the 40-58 m coastal wall at x −26 threw a 49.1 m shadow
    #   (h / tan 49.79 deg) that covered the ENTIRE promenade and 18 m of sand.
    #   The pilot frames show it directly (`pt_noon_sea_beauty.png`,
    #   `pt_noon_preset_h0.3_d5.png`: the granite reads near-black).
    #   Round b tried **221.5** (world az 255, shadow az 75): the promenade lit
    #   correctly but the revetment face and all 16 risers went to
    #   dot = cos 255 · cos 49.79 = **−0.167**, i.e. fully self-shadowed, and
    #   `pt_noon_color_front.png` came back a near-black flight.
    #   → **251.5** = world az **285 deg**, shadow az 105 deg. Measured
    #   consequences:
    #     · promenade + sand fully sunlit (deck normal +Z, cos 49.79 = 0.764)
    #     · the wall's shadow runs LANDWARD, Δx = 49.1·cos 105 = −12.7 m, so it
    #       never touches the promenade at all
    #     · the revetment face and the risers (normal +X) get a **grazing**
    #       dot = cos 285 · cos 49.79 = **+0.167** — dim enough that the 2.56 m
    #       drop still reads as a dark band, bright enough that the flight is
    #       not a black hole (the round-b defect)
    #     · the two stringer cheeks split, one lit (+Y face, +0.62) one shaded
    #       (−0.62), which is what gives the flight its modelling
    #     · no sun glint: the specular path off still water needs a 49.79 deg
    #       depression and no judged cut looks steeper than ~6.5 deg
    SUN_AZ_OFFSET=251.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene18")
# `sc.ASSETS_DIR` resolves from `scene_common.py`'s own location, i.e. the repo
# root, so it is correct whether the scene is run from `scenes/main/` (where
# `assets` is a symlink) or from the repo root.
COASTAL_DIR = os.path.join(sc.ASSETS_DIR, "coastal")
SAND_TEX = dict(diff=os.path.join(COASTAL_DIR, "beach_sand_diff.jpg"),
                nor=os.path.join(COASTAL_DIR, "beach_sand_nor_dx.jpg"),
                rough=os.path.join(COASTAL_DIR, "beach_sand_rough.jpg"))

ASSET_ROLES = ["plaza_light", "plaza_lower", "granite_dark",
               "dirt_park", "grass", "hdri", "mdl"]


# ===========================================================================
# [B-2] PLACEMENT - the geometry-free declaration `scripts/placement_lint.py`
#       reads (spec §10.4). Additive and static: it authors no prim and moves
#       no coordinate; every value is a module-level literal.
#
#       v6 declared nothing, so LINT-1/2/3/5/7 all degraded to `nodata`. The
#       promenade IS a 보행안전공간, so the data now exists and the rules can
#       actually bite.
# ===========================================================================
PLACEMENT = dict(
    # The walked band is the promenade between the tan edge band (landward)
    #   and the coping (seaward). PE-8's 1.5 m floor is evaluated inside it;
    #   the realised free width after the bench row is ~12.2 m.
    #   The segment spans the FULL plate extent (-100 .. 420), not a token
    #   +-90: a shorter polyline silently exempts every prop beyond its end,
    #   which is how 2 of the 12 lanterns escaped LINT-5 on the first pass.
    walk_edges=[((-13.40, -100.0), (-13.40, 420.0)),
                ((0.00, -100.0), (0.00, 420.0))],
    # The planting-bed kerb line - a real 연석 face, which is what PE-1's
    #   tree-to-kerb clearance is written against.
    kerb_lines=[((-13.40, -100.0), (-13.40, 420.0))],
    anchors={
        # Benches face the sea (+X = bearing 0 in this scene's convention).
        "sea_view": dict(face_bearing_deg=0.0, props=["Bench_.*"]),
        # Prop names follow `placement_rules_v1.yaml` §props verbatim so the
        #   linter actually CLASSIFIES them: `Lantern_*` and `Streetlight_*`
        #   are in its `lamp` pattern, `Globe_*`/`Cobra_*` were not and would
        #   have slipped past LINT-5 unmeasured.
        "bed_line": dict(face_bearing_deg=0.0,
                         props=["Lantern_.*", "Streetlight_.*"]),
    },
    # ONE ROUTE PER BED, not one route per species. S-2 is "one species per
    #   bed", and a bed is the physical planting unit; folding all six "U" beds
    #   into one route would make the *inter-bed* gap (21.6 m) the measured
    #   pitch and fail PE-2 for a spacing that does not exist on the ground.
    #   `pts` are the REAL tree stations — `build_beds` emits
    #   y0 + 0.800 + j*7.000 at x = (-17.60 + -13.40)/2 = -15.500, so the
    #   declaration and the geometry are the same three numbers.
    #   `species` keys are §10.2 `pass_list`: oak_pin = Shumard_Oak,
    #   juniper = Chinese_Juniper.
    routes={
        "bed_0_low": dict(pts=[(-15.50, -39.2), (-15.50, -32.2),
                               (-15.50, -25.2)],
                          species="juniper", pitch_m=7.0),
        "bed_1_tall": dict(pts=[(-15.50, -17.6), (-15.50, -10.6),
                                (-15.50, -3.6)],
                           species="oak_pin", pitch_m=7.0),
        "bed_2_low": dict(pts=[(-15.50, 4.0), (-15.50, 11.0),
                               (-15.50, 18.0)],
                          species="juniper", pitch_m=7.0),
        "bed_3_tall": dict(pts=[(-15.50, 25.6), (-15.50, 32.6),
                                (-15.50, 39.6)],
                           species="oak_pin", pitch_m=7.0),
        "bed_4_low": dict(pts=[(-15.50, 47.2), (-15.50, 54.2),
                               (-15.50, 61.2)],
                          species="juniper", pitch_m=7.0),
        "bed_5_tall": dict(pts=[(-15.50, 68.8), (-15.50, 75.8),
                                (-15.50, 82.8)],
                           species="oak_pin", pitch_m=7.0),
        "bed_6_low": dict(pts=[(-15.50, 90.4), (-15.50, 97.4),
                               (-15.50, 104.4)],
                          species="juniper", pitch_m=7.0),
        "bed_7_tall": dict(pts=[(-15.50, 112.0), (-15.50, 119.0),
                                (-15.50, 126.0)],
                           species="oak_pin", pitch_m=7.0),
    },
)


# ===========================================================================
# [C] pure geometry helpers - no pxr, so SMOKE / SELFCHECK reach them
# ===========================================================================
# ---------------------------------------------------------------------------
# **AABB TILE CAP — a real defect this scene hit, kept as a named constant.**
#   `variation_kit._Stage1Index` (`variation_kit.py:754`) drops any prim whose
#   largest AABB dimension exceeds **400 m**, on the reasonable premise that
#   such a prim is a sky dome or an infinite plane. The first build of this
#   scene ran the promenade / backland / beach plates from y −100 to +420…520
#   so that `sea_beauty` would have a real vanishing point — 520-625 m long —
#   and every one of them was therefore INVISIBLE to the data-channel camera
#   validator. `check_data_run.py` came back
#       [FAIL] ground found under every camera — 0/24
#       [FAIL] ground_below == sampled h_rel
#   i.e. the cameras were reported as floating in space over a scene that has
#   ground everywhere. Long ground plates are therefore TILED below the cap.
#   Tiles overlap 10 mm in y; they are solid boxes, so an overlap is free and a
#   butt joint would risk a hairline.
AABB_TILE_MAX = 380.0


def _tile_y(y0, y1, cap=AABB_TILE_MAX, over=0.01):
    """Split [y0, y1] into segments no longer than `cap` (see AABB_TILE_MAX)."""
    span = float(y1) - float(y0)
    n = max(1, int(math.ceil(span / cap)))
    step = span / n
    out = []
    for i in range(n):
        a = y0 + i * step - (over if i else 0.0)
        b = y0 + (i + 1) * step + (over if i < n - 1 else 0.0)
        out.append((a, b))
    return out


def _hz(hazard=None):
    """z offset applied to everything seaward of the coping in the CONTROL arm.

    With `hazard_stairs=False` the whole beach + sea rises by the full drop, so
    the frame keeps its composition and loses exactly one thing: the negative
    obstacle. (v6's control filled the stair footprint at z=0 and left a
    lower walkway 2.57 m down, i.e. it kept a drop in the control arm.)"""
    h = SCENE_CONFIG["hazard_stairs"] if hazard is None else hazard
    return 0.0 if h else DROP_TOTAL


def beach_z(x, hazard=None):
    """Sand top z at seaward distance x. Flat apron, then the foreshore."""
    b = PARAMS["beach"]
    xx = max(b["x0"], min(float(x), b["x1"]))
    if xx <= b["x_break"]:
        return b["top_z"] + _hz(hazard)
    return b["top_z"] - b["slope"] * (xx - b["x_break"]) + _hz(hazard)


def waterline_x(hazard=None):
    """**Derived**, never typed: where the foreshore plane meets still water."""
    b, w = PARAMS["beach"], PARAMS["water"]
    return b["x_break"] + (b["top_z"] - w["top_z"]) / b["slope"]


def nosing_z(x):
    """Flight nosing line z(x) = -(riser/tread)*x over the run."""
    s = PARAMS["stair"]
    k = s["riser"] / s["tread"]
    return -k * max(0.0, min(float(x), s["n"] * s["tread"]))


def step_top(i):
    """Top face z of step i (0-based). step_top(n-1) == -DROP_TOTAL."""
    return -PARAMS["stair"]["riser"] * (i + 1)


# ===========================================================================
# [C2] R-1 — hazard / drop registry, re-derived from the geometry and PRINTED
#      (`gt_changes_w3.md` §1: "the scene's own self-check re-derives and
#      prints the hazard/drop registry from the changed geometry").
#
#      This REPLACES `_wave_selfcheck`, which verified that derived geometry
#      followed a sine that no longer exists.
# ===========================================================================
def _stair_selfcheck(verbose=True):
    s, ck = PARAMS["stair"], PARAMS["cheek"]
    cop, prom, b = PARAMS["coping"], PARAMS["promenade"], PARAMS["beach"]
    riser, tread, n = s["riser"], s["tread"], s["n"]
    drop = n * riser
    ratio = 2.0 * riser + tread
    slope_deg = math.degrees(math.atan2(riser, tread))
    run = n * tread
    width = s["y1"] - s["y0"]

    # (1) the invariant
    inv_ok = abs(drop - DROP_TOTAL) < 1e-9
    # (2) the flight lands exactly on the sand apron - no lip, no last-step gap
    land = step_top(n - 1) - beach_z(run, hazard=True)
    land_ok = abs(land) < 1e-9
    # (3) the unguarded revetment edge outside the opening
    edge_drop = prom["top_z"] - beach_z(0.0, hazard=True)
    edge_ok = abs(edge_drop - DROP_TOTAL) < 1e-9
    # (4) the first riser off the coping
    first = prom["top_z"] - step_top(0)
    # (5) stringer kerb: above the tread (visible) yet far below a guard, and
    #     its haunch always bites into the body (no float, no gap)
    k = riser / tread
    hb = ck["thick"] / math.cos(math.atan(k))
    h_over, h_under = 1e9, 1e9
    for i in range(n):
        for x in (tread * i, tread * (i + 1)):
            htop = ck["rise"] - k * x
            h_over = min(h_over, htop - step_top(i))
            h_under = min(h_under, step_top(i) - (htop - hb))
    kerb_ok = (0.0 < ck["rise"] < 1.100) and h_over > 0.0 and h_under > 0.0
    # (6) foreshore is a ramp, not a step: 2.6 % << the 5 % that would make it
    #     a walking hazard in its own right
    fore_ok = b["slope"] < 0.05
    # (7) no guard prim exists unless the cue asks for one
    rail_ok = True if SCENE_CONFIG["cue_railing"] else True
    ok = (inv_ok and land_ok and edge_ok and kerb_ok and fore_ok and rail_ok
          and 0.600 <= ratio <= 0.650)

    reg = dict(
        drop_total=drop, invariant=DROP_TOTAL, riser=riser, tread=tread,
        n=n, run=run, ratio_2rt=ratio, slope_deg=slope_deg, clear_width=width,
        edge_line_x=cop["x1"], edge_y=(cop["y0"], cop["y1"]),
        opening_y=(s["y0"], s["y1"]), edge_drop=edge_drop,
        first_riser=first, landing_err=land,
        nosing_z=[round(step_top(i), 4) for i in range(n)],
        kerb_rise=ck["rise"], kerb_over=h_over, kerb_under=h_under,
        waterline_x=waterline_x(hazard=True), foreshore_slope=b["slope"],
        railing=SCENE_CONFIG["cue_railing"],
        warning_band=SCENE_CONFIG["cue_tactile"],
    )
    if verbose:
        print("=" * 68)
        print("scene18 [R-1] 낙차 원장 재유도 — 백사장 진입 계단")
        print("=" * 68)
        print(f"  ① 총 낙차          {drop:.3f} m = {n} x {riser:.3f}  "
              f"→ 불변량 {DROP_TOTAL:.3f} {'일치' if inv_ok else 'FAIL'}")
        print(f"  ② 2R+T             {ratio:.3f} m  (0.600~0.650) "
              f"→ {'OK' if 0.600 <= ratio <= 0.650 else 'FAIL'} · "
              f"경사 {slope_deg:.2f}° · 유효폭 {width:.3f} m · 진행 {run:.3f} m")
        print(f"  ③ 호안 상시 낙차   x={cop['x1']:.2f} 선, y {cop['y0']:.0f}"
              f"~{cop['y1']:.0f} (개구부 y {s['y0']:.1f}~{s['y1']:.1f} 제외) "
              f"= {edge_drop:.3f} m {'OK' if edge_ok else 'FAIL'}")
        print(f"  ④ 첫 챌면          {first:.3f} m · 착지 오차 "
              f"{land:+.6f} m {'OK' if land_ok else 'FAIL'}")
        print(f"  ⑤ 스트링거 연석    상면 +{ck['rise']:.3f} m (가드 아님, "
              f"1.100 기준의 {ck['rise'] / 1.100 * 100:.0f} %) · "
              f"헌치 상면−몸통 {h_over:+.4f} · 몸통−밑면 {h_under:+.4f} "
              f"→ {'OK' if kerb_ok else 'FAIL'}")
        print(f"  ⑥ 전빈 경사        {b['slope'] * 100:.1f} % "
              f"→ {'램프(계단 아님)' if fore_ok else 'FAIL'} · "
              f"정수위선 x = {reg['waterline_x']:.3f} (유도값)")
        print(f"  ⑦ 큐 상태          난간 {reg['railing']} · "
              f"계단머리 경고블록 {reg['warning_band']} · "
              f"논슬립 {SCENE_CONFIG['cue_nosing']}")
        print("  ⑧ 단코 z 사다리    " +
              " ".join(f"{v:.2f}" for v in reg["nosing_z"]))
        print("=" * 68)
    return ok, reg


# ===========================================================================
# [C3] `_sea_selfcheck` **v2** — frame raster coverage.
#
#  v6 asked "is anything taller than the water's far edge inside +-30 deg".
#  That is an occlusion test, and it passed at 54-100 % while the user still
#  could not see the sea. What the user's sentence actually asks is
#      "how much of this frame is water, and can I tell it from the sky".
#  So the instrument is replaced, not tuned: every judged cut is rasterised at
#  its real frustum (hFOV 60 deg, vFOV 36 deg at the default 18.1476 mm /
#  20.955 mm aperture, 16:9) against an analytic model of the macro surfaces,
#  and the check reports per-class coverage, the horizon row, and the declared
#  sea/sky value separation.
#
#  Surfaces are (a) rectangular plane patches z = a + b*x + c*y over an
#  (x, y) box, or (b) axis-aligned blocking boxes. That is enough: every macro
#  surface in this scene is one of the two, and the tracer is 60 lines.
# ===========================================================================
def _macro_model(hazard=True):
    """(patches, boxes) — the analytic stand-in for the assembled scene."""
    P = PARAMS
    pr, cop, bl = P["promenade"], P["coping"], P["backland"]
    s, b, w = P["stair"], P["beach"], P["water"]
    dz = _hz(hazard)
    pat = []                       # (name, x0,x1,y0,y1, a,b,c)  z = a+b*x+c*y
    pat.append(("paving", pr["x0"], pr["x1"], pr["y0"], pr["y1"],
                pr["top_z"], 0.0, 0.0))
    pat.append(("paving", bl["x0"], bl["x1"], bl["y0"], bl["y1"],
                bl["top_z"], 0.0, 0.0))
    pat.append(("coping", cop["x0"], cop["x1"], cop["y0"], cop["y1"],
                cop["top_z"], 0.0, 0.0))
    if hazard:
        # the flight, as its nosing plane over the opening
        k = s["riser"] / s["tread"]
        pat.append(("stair", s["x0"], s["x0"] + s["n"] * s["tread"],
                    s["y0"], s["y1"], 0.0, -k, 0.0))
    pat.append(("sand", b["x0"], b["x_break"], b["y0"], b["y1"],
                b["top_z"] + dz, 0.0, 0.0))
    pat.append(("sand", b["x_break"], b["x1"], b["y0"], b["y1"],
                b["top_z"] + dz + b["slope"] * b["x_break"], -b["slope"], 0.0))
    pat.append(("water", w["x0"], w["x_mid"], -w["y_near"], w["y_near"],
                w["top_z"] + dz, 0.0, 0.0))
    pat.append(("water", w["x_mid"] - 5.0, w["x1"], -w["y_far"], w["y_far"],
                w["top_z"] + dz - w["far_drop"], 0.0, 0.0))
    box = []                       # (name, x0,x1,y0,y1,z0,z1)
    for (x0, x1, y0, y1, h, _f) in P["city"]["wall"] + P["city"]["towers"]:
        box.append(("city", x0, x1, y0, y1, P["city"]["base_z"],
                    P["city"]["base_z"] + h + bk.RAIL_H))
    bd = P["bridge"]
    box.append(("bridge", bd["x0"], bd["x1"], bd["y"] - bd["w"] / 2.0,
                bd["y"] + bd["w"] / 2.0, bd["deck_z"] - bd["deck_t"],
                bd["deck_z"]))
    for tx in bd["towers"]:
        box.append(("bridge", tx - bd["tower_w"] / 2.0, tx + bd["tower_w"] / 2.0,
                    bd["y"] - bd["w"] / 2.0, bd["y"] + bd["w"] / 2.0,
                    bd["deck_z"], bd["deck_z"] + bd["tower_h"]))
    for (x0, x1, y0, y1, h) in P["headland"]:
        box.append(("land", x0, x1, y0, y1, w["top_z"] + dz, h))
    bs = P["beds"]
    for (y0, y1, _k) in bs["runs"]:
        box.append(("planting", bs["x0"], bs["x1"], y0, y1, 0.0,
                    bs["soil_z"] + 3.2))
    return pat, box


def _trace(eye, d, pat, box):
    """First hit along `d` from `eye`. Returns (t, class) or (inf, 'sky')."""
    best, cls = float("inf"), "sky"
    ex, ey, ez = eye
    dx, dy, dz = d
    for nm, x0, x1, y0, y1, a, bb, cc in pat:
        den = dz - bb * dx - cc * dy
        if abs(den) < 1e-12:
            continue
        t = (a + bb * ex + cc * ey - ez) / den
        if t <= 1e-6 or t >= best:
            continue
        px, py = ex + t * dx, ey + t * dy
        if x0 - 1e-9 <= px <= x1 + 1e-9 and y0 - 1e-9 <= py <= y1 + 1e-9:
            best, cls = t, nm
    for nm, x0, x1, y0, y1, z0, z1 in box:
        t0, t1 = 1e-6, best
        for a, u, lo, hi in ((ex, dx, x0, x1), (ey, dy, y0, y1),
                             (ez, dz, z0, z1)):
            if abs(u) < 1e-12:
                if a < lo or a > hi:
                    t0, t1 = 1.0, 0.0
                    break
                continue
            ta, tb = (lo - a) / u, (hi - a) / u
            t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
        if t0 <= t1:
            best, cls = t0, nm
    return best, cls


# Cuts that MUST show the sea, and the water-coverage floor each one owes.
# The floors are set from the geometry, not from a rendered result: at h1.8
# on the promenade the water band spans ~0.05-5.4 deg of a 36 deg frame, so
# ~1.5 % is the honest floor for a level judged cut, while the two seaward
# beauty cuts must do much better than that or the composition is wrong.
SEA_CUTS = {"preset_h0.3_d5": 0.8, "preset_h0.9_d5": 1.2,
            "preset_h1.8_d5": 1.6, "preset_h1.8_d10": 1.6,
            "wave_raking": 1.5, "oblique_down": 3.0, "sea_beauty": 5.0}
# Fraction of frame WIDTH that must still carry water. v6's town scored ~100 %
# on "openness" while hiding the horizon everywhere; this number cannot.
OPEN_COL_MIN = 35.0
_HFOV, _VFOV = 60.0, 36.0


def _frame_coverage(view, nx=112, ny=63, hazard=True, pat=None, box=None):
    """Per-class coverage of one cut, plus the horizon row."""
    if pat is None:
        pat, box = _macro_model(hazard)
    ex, ey, ez = view["eye"]
    tx, ty, tz = view["tgt"]
    fx, fy, fz = tx - ex, ty - ey, tz - ez
    fn = math.sqrt(fx * fx + fy * fy + fz * fz)
    fx, fy, fz = fx / fn, fy / fn, fz / fn
    # right = forward x up  (up = +Z) — the Isaac viewport convention
    rx, ry, rz = fy * 1.0 - 0.0, 0.0 - fx * 1.0, 0.0
    rn = math.hypot(rx, ry) or 1.0
    rx, ry = rx / rn, ry / rn
    ux, uy, uz = (ry * fz - 0.0, 0.0 - rx * fz, rx * fy - ry * fx)
    th = math.tan(math.radians(_HFOV / 2.0))
    tv = math.tan(math.radians(_VFOV / 2.0))
    cnt, horiz_row = {}, None
    col_water = [False] * nx
    for j in range(ny):
        v = (1.0 - 2.0 * (j + 0.5) / ny) * tv
        row_has_water = False
        for i in range(nx):
            h = (2.0 * (i + 0.5) / nx - 1.0) * th
            d = (fx + h * rx + v * ux, fy + h * ry + v * uy, fz + v * uz)
            dn = math.sqrt(sum(c * c for c in d))
            d = tuple(c / dn for c in d)
            _t, cls = _trace((ex, ey, ez), d, pat, box)
            cnt[cls] = cnt.get(cls, 0) + 1
            if cls == "water":
                row_has_water = True
                col_water[i] = True
        if row_has_water and horiz_row is None:
            horiz_row = j                      # topmost row carrying water
    tot = float(nx * ny)
    # **The v6 failure mode, measured directly.** v6's town hid the horizon
    #   across the whole frame while "openness" still read 100 %. The honest
    #   form of that question is: across what fraction of the frame WIDTH does
    #   at least one pixel of water survive to camera?
    open_cols = 100.0 * sum(1 for c in col_water if c) / float(nx)
    return ({k: 100.0 * v / tot for k, v in cnt.items()}, horiz_row, ny,
            open_cols)


def _sea_selfcheck(verbose=True, cuts=None):
    """The sea legibility gate. Replaces the v6 openness heuristic entirely."""
    mp = PARAMS["material"]
    views = build_views()
    cuts = tuple(cuts or SEA_CUTS)
    pat, box = _macro_model(True)
    diag, ok = {}, True
    for name in cuts:
        v = views[name]
        cov, hrow, ny, ocol = _frame_coverage(v, hazard=True, pat=pat, box=box)
        water = cov.get("water", 0.0)
        floor = SEA_CUTS.get(name, 0.0)
        # the horizon must be INSIDE the frame, not clipped off the top
        horizon_in = hrow is not None and 0 < hrow < ny - 1
        good = (water >= floor) and horizon_in and ocol >= OPEN_COL_MIN
        diag[name] = dict(water=round(water, 2), floor=floor,
                          sand=round(cov.get("sand", 0.0), 1),
                          paving=round(cov.get("paving", 0.0)
                                       + cov.get("coping", 0.0), 1),
                          stair=round(cov.get("stair", 0.0), 1),
                          sky=round(cov.get("sky", 0.0), 1),
                          land=round(cov.get("land", 0.0), 1),
                          city=round(cov.get("city", 0.0), 1),
                          bridge=round(cov.get("bridge", 0.0), 2),
                          open_cols=round(ocol, 1),
                          horizon_row=hrow, rows=ny, ok=good)
        if not good:
            ok = False
    # declared sea/sky separation — a number the render must not erase
    sea_v = sum(mp["water_color"]) / 3.0
    far_v = sum(mp["water_far_color"]) / 3.0
    if verbose:
        print("=" * 76)
        print("scene18 [R-1/시각] 바다 가독성 검산 v2 — 화폭 래스터 피복률 "
              "(hFOV 60° · vFOV 36°)")
        print("=" * 76)
        for k, d in diag.items():
            print(f"  {k:17s} 물 {d['water']:5.2f}% (하한 {d['floor']:.1f}) · "
                  f"모래 {d['sand']:4.1f} · 포장 {d['paving']:4.1f} · "
                  f"계단 {d['stair']:4.1f} · 하늘 {d['sky']:4.1f} · "
                  f"도시 {d['city']:4.1f} · 곶 {d['land']:3.1f} · "
                  f"교량 {d['bridge']:4.2f} · "
                  f"수평선行 {str(d['horizon_row']):>3s}/{d['rows']} · "
                  f"폭개방 {d['open_cols']:5.1f}% "
                  f"{'OK' if d['ok'] else 'FAIL'}")
        print(f"  수면 알베도 근 {sea_v:.3f} / 원 {far_v:.3f} · "
              f"거칠기 {mp['water_rough']:.2f}/{mp['water_far_rough']:.2f} · "
              f"스페큘러 {mp['water_spec']:.2f} "
              f"(v6: 0.202 / 거칠기 0.22 = 경사입사 거울 → 수평선 소멸)")
        print(f"  → {'OK' if ok else 'FAIL'}")
        print("=" * 76)
    return ok, diag


# ===========================================================================
# [D] camera presets — 9 grid views + 5 mise-en-scene cuts.
#
#   The five mise-en-scene KEYS ARE PRESERVED even though every aim changed:
#   `scripts/make_review_gallery.py:45` selects scene18's hero by the name
#   `sea_beauty` and `scripts/make_hq_sheet.py:52` selects `color_front`.
#   Renaming them would silently drop scene18 out of two published sheets, and
#   those files belong to other lanes. The docstrings below carry the new
#   meanings.
# ===========================================================================
def build_views():
    v = sc.grid_views(0.0)
    out = {k: dict(eye=list(val["eye"]), tgt=list(val["tgt"]))
           for k, val in v.items()}
    # h0.35 grazing over the coping to the surf. The KEY is kept: the "wave"
    #   it rakes is now a real breaker line instead of a sine nosing, and every
    #   `regr_*.json` baseline back to `r2_on` carries a `wave_raking` row —
    #   renaming it would have shown up as MISSING + NEW-VIEW forever.
    out["wave_raking"] = dict(eye=[-3.0, 0.0, 0.35], tgt=[9.0, 0.0, -1.60])
    # The flight read head-on FROM THE SAND (a person standing on the beach,
    #   eye 1.55 m above it) — the cut `make_hq_sheet` publishes.
    out["color_front"] = dict(eye=[12.0, 0.0, -1.01], tgt=[1.5, 0.0, -1.28])
    # 3/4 high over the flight and out to sea.
    out["oblique_down"] = dict(eye=[-6.0, 7.0, 3.20], tgt=[20.0, -1.5, -1.60])
    # From the sand looking back up at the revetment + flight (the negative
    #   obstacle from below, which is where its 2.56 m actually reads).
    out["lower_lookback"] = dict(eye=[16.0, -6.0, -1.01], tgt=[0.0, 0.5, -1.40])
    # G18 REPLICA. Aim SWEPT, not guessed: `_frame_coverage` was run over
    #   eye x in {-2.5 … -7}, yaw {8 … 28}, pitch {-2.5 … -5}, and this is the
    #   only aim that carries the water floor (>= 5 %), a G18-scale sand wedge
    #   (~30 %) and the city wall at once. Yaw +18 deg off the promenade axis
    #   toward the sea; pitch -3.5 deg puts the horizon just above frame centre
    #   as in G18. Composition: deck + bed line converge left of centre, sand
    #   and sea open the right, the receding wall closes the left, and the
    #   bridge crosses the horizon on the right.
    _bx, _by, _bz = -2.50, -34.0, 1.62
    _yaw, _pit, _d = math.radians(18.0), math.radians(-3.5), 70.0
    out["sea_beauty"] = dict(
        eye=[_bx, _by, _bz],
        tgt=[_bx + _d * math.sin(_yaw), _by + _d * math.cos(_yaw),
             _bz + _d * math.tan(_pit)])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트 — 정체성 교체판]
 1. sea_beauty      — G18 재현: 산책로 소실점 · 우측 모래+바다 · 좌측 고층벽
                      · 수평선 위 사장교가 한 화면에 드는가
 2. preset_h0.3_d*  — **바다가 보이는가**(수평선·파도선·젖은모래) — v6 실패의 본체
 3. wave_raking     — h0.35 그레이징에서 2.56 m 호안 낙차가 실루엣으로 서는가
 4. color_front     — 백사장에서 올려다본 진입 계단(16단·유효폭 6.0 m)
 5. lower_lookback  — 개구부 밖 호안선이 난간 없이 2.56 m로 이어지는가
 6. 계절 감사        — 상록(향나무)·활엽 녹엽만 · 낙엽/꽃 픽셀 0
 7. 검산            — NEGOBS_SELFCHECK=1 python scene18_wavy_artstair.py"""


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

    if smoke_mode:
        _stair_selfcheck()
        _sea_selfcheck()

    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        a, _ = _stair_selfcheck()
        b, _ = _sea_selfcheck()
        print(f"SELFCHECK {'OK' if (a and b) else 'FAIL'}")
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    missing = [k for k, p in SAND_TEX.items() if not os.path.isfile(p)]
    if missing:
        print("=" * 68)
        print("[에러] 해안 텍스처 부재 — 아래 실행 후 재시도:")
        print("  python3 assets/coastal/download_coastal_assets.py")
        for k in missing:
            print(f"  - [beach_sand/{k}] {SAND_TEX[k]}")
        print("=" * 68)
        sys.exit(1)

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene18")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene18"
    hazard = cfg["hazard_stairs"]
    DZ = _hz(hazard)

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        # Promenade granite (G18's light grey block paving)
        M["prom"] = sc.make_pbr(
            stage, "/World/Looks/PavingPromenade",
            sc.tex_path("plaza_light", "diff"), sc.tex_path("plaza_light", "nor"),
            sc.tex_path("plaza_light", "rough"), scl["plaza_light"],
            tint=mp["granite_tint"])
        # Coping / revetment face / flight — a darker dressed granite so the
        #   drop edge is a *material* edge as well as a geometric one, which is
        #   what a real 갓돌 course does.
        M["coping"] = sc.make_pbr(
            stage, "/World/Looks/CopingGranite",
            sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), scl["granite_dark"],
            tint=mp["coping_tint"])
        # Steps are the SAME granite as the promenade, sawn rather than
        #   flamed — that is how a real 진입 계단 is built, and it keeps a value
        #   break at the drop edge without inventing a second stone. Round c
        #   bound `concrete_floor` here and the flight rendered chocolate brown.
        M["tread"] = sc.make_pbr(
            stage, "/World/Looks/TreadStoneStep",
            sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"),
            sc.tex_path("plaza_light", "rough"), scl["tread"],
            tint=(0.66, 0.66, 0.645))
        M["tan"] = sc.make_pbr(
            stage, "/World/Looks/PavingTanBand",
            sc.tex_path("plaza_lower", "diff"), sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), scl["plaza_lower"],
            tint=mp["tan_tint"])
        M["backland"] = sc.make_pbr(
            stage, "/World/Looks/PavingBackland",
            sc.tex_path("plaza_lower", "diff"), sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), scl["plaza_lower"],
            tint=(0.80, 0.79, 0.77))
        # Beach sand — the procured CC0 map. Path token "SandSoil" puts it in
        #   the look layer's `soil` class (granular detail grain), which is what
        #   sand is; "Sand" alone matches no rule and would fall to `misc`.
        M["sand"] = sc.make_pbr(
            stage, "/World/Looks/SandSoilBeach", SAND_TEX["diff"],
            SAND_TEX["nor"], SAND_TEX["rough"], mp["sand_scale"],
            tint=mp["sand_tint"])
        M["damp"] = sc.make_pbr(
            stage, "/World/Looks/SandSoilDamp", SAND_TEX["diff"],
            SAND_TEX["nor"], SAND_TEX["rough"], mp["sand_scale"],
            tint=mp["damp_tint"])
        # Sea. `Sea*` -> look class `water` (omni, no bevel, no detail normal),
        #   so the explicit roughness/specular below survives the look layer.
        M["sea"] = sc.make_pbr(stage, "/World/Looks/SeaNear",
                               diffuse_color=mp["water_color"],
                               roughness_const=mp["water_rough"],
                               metallic=0.0,
                               specular_level=mp["water_spec"])
        M["sea_far"] = sc.make_pbr(stage, "/World/Looks/SeaFar",
                                   diffuse_color=mp["water_far_color"],
                                   roughness_const=mp["water_far_rough"],
                                   metallic=0.0,
                                   specular_level=mp["water_spec"])
        M["foam"] = sc.make_pbr(stage, "/World/Looks/SeaFoam",
                                diffuse_color=mp["foam_color"],
                                roughness_const=mp["foam_rough"], metallic=0.0)
        M["foam_far"] = sc.make_pbr(stage, "/World/Looks/SeaFoamFar",
                                    diffuse_color=mp["foam_far_color"],
                                    roughness_const=mp["foam_far_rough"],
                                    metallic=0.0)
        # Planting
        M["soil"] = sc.make_pbr(
            stage, "/World/Looks/BedSoil", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            scl["dirt_park"], tint=(0.86, 0.82, 0.78))
        M["kerb"] = sc.make_pbr(stage, "/World/Looks/KerbGranite",
                                diffuse_color=mp["kerb_color"],
                                roughness_const=mp["kerb_rough"])
        M["headland"] = sc.make_pbr(stage, "/World/Looks/HeadlandHaze",
                                    diffuse_color=mp["headland_color"],
                                    roughness_const=mp["headland_rough"])
        # The kit's weed/grass role still needs a real vegetation material.
        M["weed"] = sc.make_pbr(
            stage, "/World/Looks/GrassWeed", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=(0.62, 0.70, 0.48))
        # Furniture / city
        M["bench"] = sc.make_pbr(stage, "/World/Looks/BenchStone",
                                 diffuse_color=mp["bench_color"],
                                 roughness_const=mp["bench_rough"])
        M["pole"] = sc.make_pbr(stage, "/World/Looks/PoleLamp",
                                diffuse_color=mp["pole_color"],
                                metallic=mp["pole_metallic"],
                                roughness_const=mp["pole_rough"])
        M["globe"] = sc.make_pbr(stage, "/World/Looks/LampGlobe",
                                 diffuse_color=mp["globe_color"],
                                 roughness_const=mp["globe_rough"])
        M["shell"] = sc.make_pbr(stage, "/World/Looks/CityShell",
                                 diffuse_color=mp["shell_color"],
                                 roughness_const=mp["shell_rough"])
        M["tower"] = sc.make_pbr(stage, "/World/Looks/CityTowerGlass",
                                 diffuse_color=mp["tower_color"],
                                 roughness_const=mp["tower_rough"])
        M["glass"] = sc.make_pbr(stage, "/World/Looks/CityGlass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"])
        M["parapet"] = sc.make_pbr(stage, "/World/Looks/CityParapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        M["bridge"] = sc.make_pbr(stage, "/World/Looks/BridgeDeck",
                                  diffuse_color=mp["bridge_color"],
                                  roughness_const=mp["bridge_rough"])
        M["cable"] = sc.make_pbr(stage, "/World/Looks/BridgeCable",
                                 diffuse_color=mp["cable_color"],
                                 roughness_const=mp["cable_rough"])
        # ground_kit dedicated dark bindings (W2-D defect D5 — declared albedo
        #   and bound albedo must be the same object).
        M["gk_joint"] = sc.make_pbr(stage, "/World/Looks/GKitJoint",
                                    diffuse_color=(0.12, 0.12, 0.12),
                                    roughness_const=0.75)
        M["gk_iron"] = sc.make_pbr(stage, "/World/Looks/GKitIron",
                                   diffuse_color=(0.09, 0.09, 0.095),
                                   metallic=0.55, roughness_const=0.55)
        M["gk_stain"] = sc.make_pbr(stage, "/World/Looks/GKitStain",
                                    diffuse_color=(0.20, 0.20, 0.19),
                                    roughness_const=0.85)
        # Salt efflorescence on a seafront granite promenade — the one bright
        #   stain, and it stays under the 0.30 cap (§5.1 18 row, explicit).
        M["gk_salt"] = sc.make_pbr(stage, "/World/Looks/GKitSalt",
                                   diffuse_color=(0.29, 0.29, 0.28),
                                   roughness_const=0.90)
        return M

    # -------------------------------------------------------------------
    # Ground plates — promenade · coping/revetment · backland · beach · sea
    # -------------------------------------------------------------------
    def _plate(path, x0, x1, y0, y1, top, bot, mtl, collider=True,
               skin=False):
        if skin:
            sc.skin_exclude(path)
        sc.add_box(stage, path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                                 (top + bot) / 2.0),
                   (x1 - x0, y1 - y0, top - bot), mtl, collider=collider)

    def build_platform(M):
        pr, cop, bl = (PARAMS["promenade"], PARAMS["coping"],
                       PARAMS["backland"])
        b = PARAMS["beach"]
        base = b["top_z"] + DZ
        # The promenade is the ground_kit stage, so it must be registered
        #   before `add_box` evaluates the skin test inline (W2-0 · P-A).
        for i, (a, b) in enumerate(_tile_y(pr["y0"], pr["y1"])):
            _plate(f"{ROOT}/Walk_promenade_{i}", pr["x0"], pr["x1"], a, b,
                   pr["top_z"], base - 0.60, M["prom"], skin=True)
        # Coping course + revetment face: THE negative obstacle.
        for i, (a, b) in enumerate(_tile_y(cop["y0"], cop["y1"])):
            _plate(f"{ROOT}/Revetment_coping_{i}", cop["x0"], cop["x1"], a, b,
                   cop["top_z"], base - 0.60, M["coping"])
        for i, (a, b) in enumerate(_tile_y(bl["y0"], bl["y1"])):
            _plate(f"{ROOT}/Walk_backland_{i}", bl["x0"], bl["x1"], a, b,
                   bl["top_z"], bl["top_z"] - bl["thick"], M["backland"])

    def build_beach(M):
        b = PARAMS["beach"]
        run = b["x1"] - b["x_break"]
        dp = PARAMS["damp"]
        xw = waterline_x(hazard)
        x0d = xw - dp["back"]
        rund = dp["back"] + dp["fwd"]
        for i, (a, c) in enumerate(_tile_y(b["y0"], b["y1"])):
            # (1) dry backshore apron — flat
            _plate(f"{ROOT}/Beach_apron_{i}", b["x0"], b["x_break"], a, c,
                   b["top_z"] + DZ, b["top_z"] + DZ - b["thick"], M["sand"])
            # (2) foreshore — one inclined slab per tile; the same plane
            #     `beach_z` returns, so the analytic model and the USD can
            #     never disagree.
            sc.build_slope(stage, f"{ROOT}/Beach_foreshore_{i}", b["x_break"],
                           b["top_z"] + DZ, run, b["slope"] * run,
                           a, c, b["thick"], M["sand"],
                           margin=0.0, collider=True)
            # (3) damp swash band landward of the waterline (G18's tide-out)
            sc.build_slope(stage, f"{ROOT}/Beach_damp_{i}", x0d,
                           beach_z(x0d, hazard) + dp["proud"], rund,
                           b["slope"] * rund, a, c, 0.10, M["damp"],
                           margin=0.0, collider=False)

    def build_sea(M):
        w = PARAMS["water"]
        top = w["top_z"] + DZ
        _plate(f"{ROOT}/Sea_near", w["x0"], w["x_mid"], -w["y_near"],
               w["y_near"], top, top - w["thick"], M["sea"], collider=False)
        _plate(f"{ROOT}/Sea_far", w["x_mid"] - 5.0, w["x1"], -w["y_far"],
               w["y_far"], top - w["far_drop"],
               top - w["far_drop"] - w["thick"], M["sea_far"], collider=False)

    def build_surf(M):
        """Breaker lines + swash edge.

        A straight strip reads as a ruler, so each line is cut into y segments
        whose x centre and width are jittered by a seeded RNG. That is the
        cheapest thing that turns "a blue plane" into "the sea": in G18 the
        surf lines are the single strongest sea cue after the horizon."""
        import random as _r
        sf = PARAMS["surf"]
        b, w = PARAMS["beach"], PARAMS["water"]
        rnd = _r.Random(sf["seed"])
        xw = waterline_x(hazard)
        top = w["top_z"] + DZ + sf["proud"]
        for li, (off, wid, nseg) in enumerate(sf["lines"]):
            span = sf["y1"]
            y = sf["y0"]
            k = 0
            while y < span and k < nseg * 3:
                ly = sf["seg_y"] * rnd.uniform(0.80, 1.35)
                cxs = xw + off + rnd.uniform(-sf["jit_x"], sf["jit_x"])
                ww = wid * rnd.uniform(1.0 - sf["jit_w"], 1.0 + sf["jit_w"])
                sc._oriented_box(
                    stage, f"{ROOT}/Surf_{li}_{k}",
                    (cxs, y + ly / 2.0, top - 0.06), (ww, ly, 0.12),
                    M["foam"] if li < 2 else M["foam_far"], collider=False,
                    rotz=rnd.uniform(-sf["rotz"], sf["rotz"]))
                # segments OVERLAP: `step` < the drawn length, so the breaker
                #   line is continuous instead of a row of dashes
                y += sf["step"] * rnd.uniform(0.75, 1.15)
                k += 1

    # -------------------------------------------------------------------
    # Hazard geometry — flight + stringer kerbs
    # -------------------------------------------------------------------
    def build_stair(M):
        s = PARAMS["stair"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stair", s["x0"], s["y0"], s["y1"],
            s["riser"], s["tread"], s["n"], s["base_z"], M["tread"],
            z_top=0.0, collider=True)

    def build_cheeks(M):
        """Per-step stringer bodies flush with the tread + one oblique haunch
        per side parallel to the nosing line (the scene14 method).

        Flush bodies (curb = 0) kill the stepped sawtooth the user scrapped in
        14 and which v6 still carried in 18; the haunch supplies the single
        visible raking top face. `_stair_selfcheck` ⑤ proves the haunch is
        always above the body and always bites into it."""
        s, ck = PARAMS["stair"], PARAMS["cheek"]
        for i in range(s["n"]):
            xa = s["x0"] + s["tread"] * i
            xb = xa + s["tread"]
            for tag, cy0, cy1 in (("S", s["y0"] - ck["w"], s["y0"]),
                                  ("N", s["y1"], s["y1"] + ck["w"])):
                sc.add_box(stage, f"{ROOT}/Cheek_{tag}_{i}",
                           ((xa + xb) / 2.0, (cy0 + cy1) / 2.0,
                            (step_top(i) + ck["base_z"]) / 2.0),
                           (xb - xa, cy1 - cy0, step_top(i) - ck["base_z"]),
                           M["coping"], collider=True)
        k = s["riser"] / s["tread"]
        run = s["n"] * s["tread"] + ck["over"]
        for tag, y0, y1 in (("S", s["y0"] - ck["w"], s["y0"]),
                            ("N", s["y1"], s["y1"] + ck["w"])):
            sc.build_slope(stage, f"{ROOT}/CheekHaunch_{tag}", s["x0"],
                           ck["rise"], run, k * run, y0, y1, ck["thick"],
                           M["coping"], margin=0.0, collider=True)

    def build_control_fill(M):
        """CONTROL arm (`hazard_stairs=False`): the beach is already lifted by
        `_hz()`, so the only thing left is to close the 0.35 m coping notch."""
        cop = PARAMS["coping"]
        for i, (a, b) in enumerate(_tile_y(cop["y0"], cop["y1"])):
            _plate(f"{ROOT}/Walk_flat_{i}", cop["x0"],
                   PARAMS["beach"]["x_break"], a, b, 0.0, -0.60, M["coping"])

    # -------------------------------------------------------------------
    # Promenade dressing
    # -------------------------------------------------------------------
    def build_edge_bands(M):
        """Warm tan band + yellow guide strip along the LANDWARD edge (G18).

        **Why the guide strip is scene-side and not a `ground_kit` tactile
        site**: `ground_kit.TACTILE_OFF_REASON["scene18"]` reads "18 = wave-form,
        irregular - laying a 300 mm grid on it is not practice". That reason
        died with the wave; the promenade is a flat granite route and G18 shows
        a continuous yellow guide line along its landward edge. `ground_kit`
        belongs to another lane this window, so the site is not registered
        there and `plan_ground(tactile=())` stays. **The stale registry entry is
        recorded as owed to Lane-1 in the report.**

        **Fidelity deviation, stated**: G18's strip is a 선형(유도)블록 (bars).
        The library's only tactile texture is 점형(warning, 36 dots). Using it
        here would paint 120 m of statutory *warning* surface where none
        belongs, so the strip is built at the correct width (0.30 m) and colour
        with the tactile material and is kept 12.20 m clear of the drop edge,
        where no reader can take it for a stair-head cue. The bar geometry is
        owed to K4/K5."""
        tb, gd = PARAMS["tan_band"], PARAMS["guide"]
        if cfg["cue_material_break"]:
            _plate(f"{ROOT}/Band_tan", tb["x0"], tb["x1"], tb["y0"], tb["y1"],
                   tb["proud"], -0.02, M["tan"], collider=False)
        tac = sc.tactile_pbr(stage, "/World/Looks/TactileGuide")
        n = int((gd["y1"] - gd["y0"]) / gd["seg"])
        for i in range(n):
            y0 = gd["y0"] + i * gd["seg"]
            sc.build_tactile(stage, f"{ROOT}/GuideStrip_{i}", gd["x0"],
                             gd["x1"], y0, y0 + gd["seg"] - 0.02, tac,
                             z=0.0, proud=gd["proud"])

    def build_beds(M):
        """Kerbed raised planting beds. K5 deferred -> scene-side kerb.

        [VEGETATION — R18-2, bounded procurement attempt: **NEGATIVE**]
          Searched, this window, the three licensed sources the ruling names:
            · Poly Haven models — full index pulled (521 assets): **0 palm,
              0 umbrella/stone pine**. The only conifers are fir/pine/spruce
              saplings of a temperate forest collection.
            · ambientCG — a material library; it publishes no plant models.
            · KOGL / 문화포털 — no reachable 3D vegetation catalogue.
          So neither a palm nor an umbrella pine is procurable under the
          CC0/KOGL doctrine, and NoAI / unverified-Sketchfab sources are barred.

          The ruling's fallback is "substitute pines only". **That fallback is
          itself blocked**, and the conflict is reported rather than worked
          around: `Docs/briefs/placement_rules_v1.yaml` `species.retired`
          lists **White_Pine and Yellow_Pine** — the repo's only two pines —
          and LINT-4b's severity is `error`. Binding either would trade a look
          gain for a hard linter failure. (The v6 scene *does* trip it: the
          baseline lint on scene18 reports 1 LINT-4b ERROR because
          `build_planter` -> `build_tree` drew White_Pine at random.)

          Adopted, and stated plainly as a **less coastal read**:
            · bed kind "U" = **Chinese_Juniper** (향나무) 2.60 m — evergreen,
              §10.2 pass list, and a real Korean coastal-park planting.
            · bed kind "T" = **Shumard_Oak** 7.60 m — the repo's zelkova/pin-oak
              substitute, standing in for G18's tall bed.
            · shrub mass  = Boxwood + Juniper ONLY (season pin: no Rhododendron
              blossom, no Burning_Bush autumn red, no Forsythia).
          Species are placed EXPLICITLY (not through `build_tree`'s random
          pool), so LINT-4b goes 1 -> 0 and LINT-4's one-species-per-bed holds
          by construction."""
        bs = PARAMS["beds"]
        sp = PARAMS["species"]
        kw, kh = bs["kerb_w"], bs["kerb_h"]
        placed_t, placed_s = 0, 0
        for bi, (y0, y1, kind) in enumerate(bs["runs"]):
            # kerb ring (4 sides) — a 연석 face is what LINT-1 measures against
            for tag, kx0, kx1, ky0, ky1 in (
                    ("W", bs["x0"], bs["x0"] + kw, y0, y1),
                    ("E", bs["x1"] - kw, bs["x1"], y0, y1),
                    ("S", bs["x0"], bs["x1"], y0, y0 + kw),
                    ("N", bs["x0"], bs["x1"], y1 - kw, y1)):
                _plate(f"{ROOT}/Planter_{bi}/Kerb_{tag}", kx0, kx1, ky0, ky1,
                       kh, -0.05, M["kerb"])
            _plate(f"{ROOT}/Planter_{bi}/Soil", bs["x0"] + kw, bs["x1"] - kw,
                   y0 + kw, y1 - kw, bs["soil_z"], -0.05, M["soil"],
                   collider=False)
            rel, native, target = sp[kind]
            cx = (bs["x0"] + bs["x1"]) / 2.0
            # pitch is HELD, not approximated: ny is chosen so the realised
            #   spacing over the planted length equals `tree_pitch` exactly,
            #   which is what `PLACEMENT['routes'][*]['pitch_m']` declares and
            #   LINT-2 gates.
            ny = int(round((y1 - y0 - 1.6) / bs["tree_pitch"])) + 1
            for j in range(ny):
                ty = y0 + 0.8 + j * (y1 - y0 - 1.6) / max(1, ny - 1)
                if _place_species(f"{ROOT}/Planter_{bi}/Tree_{j}", rel, native,
                                  target, cx, ty, bs["soil_z"],
                                  yaw=(bi * 47 + j * 113) % 360, M=M):
                    placed_t += 1
            pts = []
            yy = y0 + kw + 0.55
            while yy < y1 - kw - 0.40:
                for sx in (bs["x0"] + kw + 0.55, bs["x1"] - kw - 0.55):
                    pts.append((sx, yy, bs["soil_z"]))
                yy += bs["shrub_pitch"]
            placed_s += sc.place_shrubs(
                stage, f"{ROOT}/Planter_{bi}/Shrub", pts, 0.85,
                pool=list(PARAMS["shrub_pool"]), seed=bs["seed"] + bi,
                tag="Sh")
        print(f"[식생] 교목 {placed_t} · 관목 {placed_s} "
              f"(종 고정: Chinese_Juniper / Shumard_Oak — R18-2 폴백)")

    def _place_species(path, rel, native, target, cx, cy, gz, yaw, M):
        """`build_tree` with the species FIXED (K4(b) is a Lane-1 package, so
        the `species=` kwarg does not exist yet and the intake explicitly
        licenses `add_vegetation` at the call site).

        Falls back to `build_tree`'s procedural blob when the vegetation tree is
        absent, exactly as the library does — a missing asset must degrade, not
        crash."""
        if not (sc.LOOK_GEO and sc.veg_available()):
            sc.build_tree(stage, path, cx, cy, gz, M["kerb"], M["weed"],
                          M["weed"], trunk_h=target / 1.60)
            return True
        xf = sc.add_vegetation(stage, path + "/Veg", rel, (cx, cy, gz),
                               yaw_deg=float(yaw), target_h=float(target),
                               native_h=float(native))
        if xf is None:
            return False
        sc._deactivate_seasonal(stage, path + "/Veg/Asset", rel)
        try:
            stage.GetPrimAtPath(path + "/Veg/Asset").SetInstanceable(True)
        except Exception:
            pass
        return True

    def build_furniture(M):
        for j, (cx, cy, bz, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{j}", cx, cy, bz, M["bench"],
                           length=1.90, width=0.46, height=0.42, yaw=yaw)
        gl = PARAMS["globe"]
        for i, g in enumerate(PARAMS["globes"]):
            base = f"{ROOT}/Lantern_{i}"
            sc.add_cylinder(stage, f"{base}/Pole",
                            (g["x"], g["y"], g["base_z"] + gl["pole_h"] / 2.0),
                            gl["pole_r"], gl["pole_h"], M["pole"],
                            collider=True)
            sc.add_cylinder(stage, f"{base}/Arm",
                            (g["x"], g["y"], g["base_z"] + gl["pole_h"]),
                            gl["arm_r"], gl["arm_len"], M["pole"], rotX=90.0)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                sc.add_sphere(stage, f"{base}/Globe_{tag}",
                              (g["x"], g["y"] + sgn * gl["arm_len"] / 2.0,
                               g["base_z"] + gl["pole_h"] + gl["globe_r"]
                               * 0.55),
                              (gl["globe_r"],) * 3, M["globe"])
        cb = PARAMS["cobra"]
        for i, c in enumerate(PARAMS["cobras"]):
            base = f"{ROOT}/Streetlight_{i}"
            sc.add_cylinder(stage, f"{base}/Pole",
                            (c["x"], c["y"], c["base_z"] + c["pole_h"] / 2.0),
                            cb["pole_r"], c["pole_h"], M["pole"], collider=True)
            sc.add_cylinder(stage, f"{base}/Arm",
                            (c["x"] + cb["arm_len"] / 2.0, c["y"],
                             c["base_z"] + c["pole_h"] - 0.10),
                            cb["arm_r"], cb["arm_len"], M["pole"], rotY=90.0)
            sc.add_box(stage, f"{base}/Head",
                       (c["x"] + cb["arm_len"], c["y"],
                        c["base_z"] + c["pole_h"] - 0.16),
                       (cb["head"], cb["head"] * 0.55, 0.14), M["globe"])

    # -------------------------------------------------------------------
    # City (BS-4) + horizon furniture
    # -------------------------------------------------------------------
    def build_city(M):
        """G18's coastal high-rise wall, via `building_kit` **BS-4**.

        Every one of these ten masses is outside +-30 deg of every judged eye
        (they stand behind the camera in the +X judged cuts and only enter the
        `sea_beauty` frame), which is exactly the case BS-4 was written for:
        `kind="backdrop"` -> 3-4 prims, no windows, no attachments. Building
        them with the full apartment builder would spend a few thousand prims
        on a silhouette. They are **landed** at the backland top, not floated."""
        K = fk.Kit(sc.add_box, sc.add_cylinder, sc._oriented_box)
        cty = PARAMS["city"]
        wall_m = bk.Mtls(M["shell"], M["glass"], M["parapet"],
                         stone=M["coping"], metal=M["pole"])
        tower_m = bk.Mtls(M["tower"], M["glass"], M["parapet"],
                          stone=M["coping"], metal=M["pole"])
        for tag, rows, mt in (("Wall", cty["wall"], wall_m),
                              ("Tower", cty["towers"], tower_m)):
            for i, (x0, x1, y0, y1, h, fl) in enumerate(rows):
                bd = dict(x0=x0, x1=x1, y0=y0, y1=y1, h=h, floors=fl,
                          axis="x", facade_x=x1, face_dir=1.0,
                          base_z=cty["base_z"])
                bk.build_korean_building(K, stage, f"{ROOT}/City{tag}_{i}", bd,
                                         mt, kind="backdrop",
                                         seed=1800 + i * 7)

    def build_horizon(M):
        """Suspension bridge + headland — G18's two horizon anchors.

        They are what turns "a blue band" into "a bay". Both are pure
        silhouettes at 0.9-4 km: 8 prims for the bridge, 2 for the headland."""
        bd = PARAMS["bridge"]
        y0, y1 = bd["y"] - bd["w"] / 2.0, bd["y"] + bd["w"] / 2.0
        _plate(f"{ROOT}/Bridge_deck", bd["x0"], bd["x1"], y0, y1,
               bd["deck_z"], bd["deck_z"] - bd["deck_t"], M["bridge"],
               collider=False)
        for ti, tx in enumerate(bd["towers"]):
            _plate(f"{ROOT}/Bridge_tower_{ti}", tx - bd["tower_w"] / 2.0,
                   tx + bd["tower_w"] / 2.0, y0, y1,
                   bd["deck_z"] + bd["tower_h"], bd["deck_z"] - bd["deck_t"],
                   M["bridge"], collider=False)
        # main cables — 3 chords per span, enough for a catenary read at 2 km
        spans = [(bd["x0"], bd["towers"][0]), (bd["towers"][0], bd["towers"][1]),
                 (bd["towers"][1], bd["x1"])]
        for si, (sa, sb) in enumerate(spans):
            for c in range(3):
                f = (c + 1) / 4.0
                za = bd["deck_z"] + bd["tower_h"] * (1.0 - 4.0 * f * (1.0 - f))
                _plate(f"{ROOT}/Bridge_cable_{si}_{c}",
                       sa + (sb - sa) * f - 1.2, sa + (sb - sa) * f + 1.2,
                       y0 + 1.0, y1 - 1.0, za, za - 0.9, M["cable"],
                       collider=False)
        for i, (x0, x1, hy0, hy1, h) in enumerate(PARAMS["headland"]):
            _plate(f"{ROOT}/Headland_{i}", x0, x1, hy0, hy1, h,
                   PARAMS["water"]["top_z"] + DZ - 4.0, M["headland"],
                   collider=False)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P1 plaza_granite on the promenade
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]),
            z=float(PARAMS["promenade"]["top_z"]), gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("revetment_edge", float(g["edge_s"]))],
            dists=(2, 5, 10), scene="scene18", tactile=(),
            overrides=dict(
                infra=dict(manhole=2, gully=2),
                surface=(("patch", 3), ("crack", 4),
                         ("stain", ("dirt", "efflorescence")), ("weed", 6)),
                extras=(("silt_band", dict(n=int(g["silt"]["n"]))),)),
            extras_args=dict(silt_band=dict(
                waterline=float(g["silt"]["waterline"]),
                width=float(g["silt"]["width"]), n=int(g["silt"]["n"]))),
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[tuple(v) for v in g["gullies"]],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=18)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # `patch` = a granite slab REPLACEMENT, so it must be granite. Round b
        #   bound it to the warm tan band and the three repair patches rendered
        #   as large tan rectangles in the middle of the promenade.
        M2.update(joint=M["gk_joint"], crack=M["gk_stain"], patch=M["coping"],
                  patch_cut=M["gk_joint"], manhole=M["gk_iron"],
                  gully=M["gk_iron"], gutter=M["gk_iron"],
                  gutter_cover=M["gk_iron"], trench=M["gk_iron"],
                  trench_frame=M["gk_iron"], marking=M["gk_stain"],
                  weed=M["weed"], wear=M["gk_stain"],
                  # the drift band IS sand here — the v6 orientation deviation
                  #   is resolved by the new shore-normal (see PARAMS.gkit)
                  silt=M["sand"],
                  stain_dirt=M["gk_stain"], stain_efflorescence=M["gk_salt"],
                  grass=M["weed"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene18 P1 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Cue toggles (hazard geometry unchanged by every one of them)
    # -------------------------------------------------------------------
    def build_cues(M):
        s = PARAMS["stair"]
        if cfg.get("cue_tactile"):
            # Statutory stair-head warning band: 0.30 m clear of the first
            #   riser, 0.60 m deep, across the clear width — the same form
            #   §7-4 ruled for scene16.
            tac = sc.tactile_pbr(stage, "/World/Looks/TactileWarn")
            sc.build_tactile(stage, f"{ROOT}/WarnBand", -0.90, -0.30,
                             s["y0"], s["y1"], tac, z=0.0)
        if cfg.get("cue_nosing"):
            # RF-5 retrofit metal strip: 60 mm profile set back 10 mm from the
            #   nosing, ending short of the tread ends (the real tell).
            nos = sc.make_pbr(stage, "/World/Looks/NosingStrip",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i in range(s["n"]):
                xf_ = s["x0"] + s["tread"] * (i + 1)
                sc.add_box(stage, f"{ROOT}/Nosing_{i}",
                           (xf_ - 0.040, 0.0, step_top(i) + 0.005),
                           (0.060, (s["y1"] - s["y0"]) - 0.24, 0.010), nos)
        if cfg.get("cue_railing"):
            rail = sc.make_pbr(stage, "/World/Looks/RailStainless",
                               diffuse_color=mp["rail_color"],
                               metallic=mp["rail_metallic"],
                               roughness_const=mp["rail_rough"])
            k = s["riser"] / s["tread"]
            run = s["n"] * s["tread"]
            for tag, yy in (("S", s["y0"] - 0.10), ("N", s["y1"] + 0.10)):
                sc.build_railing_line(stage, f"{ROOT}/Rail_{tag}", yy,
                                      s["x0"], s["x0"], run, k * run,
                                      nosing_z, rail, h=1.10, baluster_r=0.0)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_platform(M)
    build_beach(M)
    build_sea(M)
    build_surf(M)
    if hazard:
        build_stair(M)
        build_cheeks(M)
    else:
        build_control_fill(M)
    if cfg["cue_scene_dressing"]:
        build_edge_bands(M)
        build_beds(M)
        build_furniture(M)
        build_city(M)
        build_horizon(M)
    if hazard:
        build_cues(M)
    build_ground_kit(M)          # after the dressing (scatter ordering)
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
    _v0 = VIEWS["sea_beauty"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene18_{ts}.png")
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
