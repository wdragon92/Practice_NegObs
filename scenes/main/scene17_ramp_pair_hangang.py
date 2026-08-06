# -*- coding: utf-8 -*-
"""
scene17_ramp_pair_hangang.py — NegObs synthetic scene 17 (v5.1 rebuild):
Han river levee section — levee path -> grass bank -> terrace -> river (Isaac Sim 4.5)

Type    : T21 ramp-stair contrast pair (same 3.2 m drop — stairs vs drivable grade)
Spec    : Docs/audit_v4/user_feedback_v5_1.md §per-scene instructions, row 17
Shared  : scene_common.py (build_slope/build_straight_stairs/build_rot_group/
          build_water/build_building/build_tree/add_sphere) · follows scene16 structure
          (v6: silver grass moved from build_hedge boxes to stalk clumps and blobs,
          so that call is retired)

[v5.1] Why it was rebuilt (user: "unidentifiable · forced terrain")
  In the old version, stairs and a **zigzag 2-flight ramp (paired lanes + a separate
  parapet)** burst out of an opening in a retaining wall — an unidentifiable structure.
  No real Han river levee looks like that. The real section is simple:
      levee crest (sidewalk + bike road, width 6) -> **grass bank (1:2 grade, height 3.2)**
      -> terrace (promenade + grass + benches) -> riprap revetment -> broad water
      -> apartments and bridge on the far bank
  Down that bank go (a) **concrete stairs cutting straight through** (width 3, unrailed
  by custom) and (b) **a single diagonal ramp crossing the bank obliquely** (width 2.5,
  grade 12.5% [W3 S17]), taking the same 3.2 m drop at different grades — the contrast-pair
  intent is unchanged, only the terrain was replaced with a real Han river section.
  Dropped: the zigzag 2 flights · paired lanes (lane A/B) · separate parapet ·
  the 3 retaining-wall opening segments.

[W3 S17] Season, reference images, and the one authorised lever
  * **Season = SUMMER**, pinned from **G3** (`Docs/reference_photos/Generated Image -
    Scene03.jpg`), the nearest image to this scene under the 07-31 season ruling
    (`w3_intake_v2_images.md` §7-8: an imageless scene inherits its nearest image's
    season). G3 is the same Hangang levee section — crest path, planted slope, a **wide
    unrailed flight cutting straight down the bank**, promenade, fence, benches, broad
    water, bridge, far apartments — in **full leaf under a blue summer sky**. **G9**
    (`…Scene09.jpg`, autumn) is secondary and is read **for the water-edge terrace form
    only, never for its season.** Consequence: `build_tree(bare=)` stays **False**
    everywhere in this file; there is no leaf-off element to wrap.
  * **R17-1 = (ii)** (`w3_intake_v2_images.md` §7 ruling 7): the stair identity is
    restored by **shortening the ramp**, NOT by widening the flight (the flight's
    `y0/y1/riser/tread/nsteps/x0` are frozen) and NOT by re-aiming any camera
    (`build_views` is byte-frozen — *"legibility comes from geometry, never from camera
    edits"*).

Hazard
  Looking +X from the levee path (z=0) at robot eye height h0.3, the sight line grazing
  the crest shoulder (x=0) is far gentler than the bank (50% average), so **the bank,
  the stairs and the terrace all disappear from view** and only the far side of the
  terrace (x >= 21) is left on the horizon -> it reads as one continuous plane with the
  near grass. There is no guard (Han river levee stairs are unrailed by custom). The
  river-side edge of the diagonal ramp is only a kerb (h0.15) on a 1.5 m stone
  revetment — a below-code reality.

Two declared below-code realities (stated, never smoothed)
  1. The ramp's river-side edge is a 0.15 m kerb, not a guard (above).
  2. **The ramp grade is 12.5% = 1/8** [W3 S17]. 편의증진법 접근로/경사로's ceiling is
     **1/12**, and the 1/8 relaxation needs **all three** of 기존시설 · 높이 ≤1 m ·
     상시보조서비스 (`Docs/surveys/cue_arrangement_survey.md:148` `[확인]`), none of which
     holds here. So 1/8 is used as what it is: **the steepest gradient the Korean
     accessibility code ever names** — a named number rather than an invented one — and
     the deviation is declared, exactly as (1) is. What the 40 m ramp used to be was not
     code-clean either: at 8.0% it was a **40 m continuous run with no rest landing**,
     against 조경설계기준 LDS-2016 5.9 경사로 (4) — *1,500 × 1,500 landing every 30 m*
     (`Docs/surveys/s3_research_numbers_v1.md` §217, grade **A**) — and landings are
     **CANCELLED for 02 · 03 · 17** by `w3_execution_spec_v1.md` §6.1-1/2/5/8/9/10. At
     25.6 m the run is under that 30 m threshold, so **no landing is owed**: the
     shortening closes that defect instead of inheriting it.

S06-B kerbless-by-design — VERIFIED, EV-C closed [W3 S17]
  `w3_intake_06_10.md` §3 leaves 03/12/17 kerbless *"only if a photo check confirms it"*.
  **G3 is that photo**: its levee crown paving meets the planted slope with a flush edge
  and no raised 연석 anywhere along the promenade. The section here has no 차도 at all —
  「도로의 구조·시설 기준」 제16조's 연석 separates a **carriageway** from a footway, and
  what this crest carries is a 자전거도로 (asphalt, x −7…−3 [GT-81]) and a 보도
  (interlock, x −10.5…−7.5) **separated by a 0.5 m planting strip**, both at the same
  +0.006 top, with a 3.0 m turf verge between the bike road and the crest. A
  보차도 경계석 would be a fabrication. `infra_kit.build_curb_line` is therefore **not**
  called here; the only kerb-like prims are the crest cope (a 마루 끝 cope, `PARAMS["cope"]`)
  and the ramp's river-side kerb, and neither is a 보차도 연석.

[GT-81] The crown moved back and both routes were joined up (08-06 user verdict)
  * *"The main road is right next to the slope — widen the distance and trim it
    neatly."* It was literally true: the bike road's riverward edge and the 3.2 m
    drop edge were the same line, x=0. The whole crown (walk · planting strip ·
    bike road) is translated **−3.0 m** as a rigid body — widths, `proud`, `embed`
    and the z ladder untouched — and `x −3.0 … 0.0` becomes a **turf verge** that
    ends on the crest cope. The drop edge stays at x=0, so no GT row moves.
  * The 08-06 audit added: *"ramp slab isolated in grass, not connected to top
    levee road or bottom riverside road."* Four `spurs` close the four turf gaps
    (5.10 m at the stair foot, 2.10 m at the ramp foot, 3.00 m at the stair head
    once the road moved, 0.58 m at the ramp head), each ending edge-to-edge on a
    built face, never in turf.
  * The ramp embankment was truncated flat at s=0 — up to 1.37 m of vertical face
    plus nine batter-strip ends. `ramp["head"]` gives every band a return nose at
    the batter's own grade; all ten bands dive under the bank inside their own run
    and clear the flight by 0.39 m [computed, smoke gate].
  * The river-side kerb now ends with a 0.50 m dropped-kerb piece instead of a
    0.146 m stub, the trench drain butts a catch basin at each end instead of
    stopping 0.70 m short, and the footway wear lane runs the walk's full length
    in the walk's own material instead of being a 12 m concrete island.

Goal
  (1) levee crest (sidewalk 3 + bike road 4 + 0.5 planting strip + 3.0 verge)
      + crest cope
  (2) grass bank as a 7-segment polyline (shoulder rounding 25.7% -> 60% at the
      bottom, 50% average = 1:2), built as 2 Y bands that leave only the stair width
      (y +-1.5) open — segments overlap by margin so no gap can open
  (3) 20 stair steps (riser 0.16 · tread 0.32 · width 3) cutting straight through
      — **frozen by R17-1 (ii): no widening, no move, so GT keeps its drop edge at x=0**
  (4) diagonal ramp: a single build_slope inside rot_group (yaw **75.5225 deg**) — length
      **25.6 m**, grade **12.5%**, width 2.5, uphill cut face (max 0.30 m) · river-side
      stone revetment (max 1.50 m)
  (5) terrace (promenade width 3 + grass + benches + silver grass) · riprap revetment ·
      broad water · 4 apartment blocks across · bridge (existing PARAMS reused)

Walking-continuity self-check table (both routes: levee path z=0 -> terrace z=−3.2)
  ┌ #  section               coord (x, y, z)            step / verdict
  │ A0 bike road centre      (−5.00,  −6.00, +0.006)    flat  [GT-81 −2.00 -> −5.00]
  │ A1 stair entry link      (−1.50,   0.00, +0.006)    flat  (LinkStairCrest 3.0 x 3.0,
  │                                                      butts the road at x −3.0)
  │ A2 crest shoulder (edge) ( 0.00,   0.00, +0.006)    ← **drop 3.20, no railing**
  │ A3 stair step 1          ( 0.32,   0.00, −0.160)    0.166 (unchanged: the link
  │                                                      restores the crown's +0.006 top)
  │ A4 stair step 20         ( 6.40,   0.00, −3.200)    0.160 x 19
  │ A5 stair foot link       ( 9.00,   0.00, −3.196)    0.004 up, flat  [GT-81 NEW —
  │                                                      was 5.10 m of turf]
  │ A6 promenade             (11.50,   0.00, −3.196)    flat, edge to edge with A5
  ├ B0 bike road centre      (−5.00,   3.85, +0.006)    flat
  │ B1 ramp entry link       (−1.00,   3.85, +0.006)    flat  (LinkRampCrest, butts the
  │                                                      road at x −3.0)  [GT-81 NEW]
  │ B2 ramp uphill start     ( 0.58,   3.85,  0.000)    0.006 threshold vs the link
  │                                                     ([v7] old apron prim removed —
  │                                                      see PARAMS["ramp"]["apron"];
  │                                                      the 0.149 turf notch it left is
  │                                                      what B1 now paves)
  │ B3 ramp s=6.4            ( 3.39,   9.73, −0.800)    grade 12.5%
  │ B4 ramp s=16             ( 5.79,  19.03, −2.000)    grade 12.5%
  │ B5 ramp end s=25.6       ( 8.19,  28.32, −3.200)    grade 12.5% -> flush with terrace
  │ B6 ramp foot link        (10.00,  29.00, −3.196)    flat  [GT-81 NEW — was 2.10 m
  │                                                      of turf]
  └ B7 promenade             (11.50,  29.00, −3.196)    flat, edge to edge with B6
  * Both routes drop the same 3.20 — the basis of the contrast pair. Stairs 50% vs ramp
    12.5% (was 8%): the contrast is 4.0x instead of 6.25x, and it now fits one frame.
  * [W3 S17] Route B is a **walked surface**, so shortening it is a **GT FULL** change
    (`w3_intake_v2_images.md` §2 GT key: FULL = walked surface moves -> R-1+R-2+R-3).
    The intake's (f) guessed **A**; the measurement says FULL and the ledger row says
    FULL. Route A (the flight) and the drop edge at x=0 are untouched.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene17_ramp_pair_hangang.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene17_ramp_pair_hangang.py
Smoke (no boot):          NEGOBS_SMOKE=1  python scene17_ramp_pair_hangang.py

Coordinates: Z-up, m, travel axis +X (levee path -> bank -> water). **Drop start edge x=0.**
  levee path z=0 · terrace z=−3.2 · water z=−3.42 · far-bank terrace z=−3.1.
"""

import os
import sys
import math
import json
import datetime
import random as _random          # [v6] fixed-seed jitter for silver-grass clumps and far-bank blobs

import scene_common as sc
import ground_kit as gk
import infra_kit as ik          # [W3 S17 · F5] derive_manholes — G-4, KDS 61 40 00


# ===========================================================================
# [A] SCENE_CONFIG — standard 7 keys. Only hazard_stairs toggles hazard geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> bank · stairs · ramp become flat z=0 (sole geometry toggle)
    "cue_railing":        False,   # Han river levee stairs are **customarily unrailed**. True -> 1 pipe rail on the stair's right
    "cue_tactile":        False,   # not customary for river works — code path reserved only
    "cue_material_break": True,    # levee grass/asphalt vs stair and ramp concrete contrast
    "cue_sign":           False,   # [optional] not implemented — config key reserved only
    "cue_scene_dressing": True,    # promenade · benches · silver grass · lamps · apartments · bridge
    "cue_nosing":         False,   # True -> nosing band on every step
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
_SLOPE_RUN = 6.4          # bank run (grade 1:2 · height 3.2)
_SLOPE_H = 3.2            # bank height = GT drop (shared by stairs and ramp)
_TERRACE_Z = -_SLOPE_H    # terrace top -3.2

PARAMS = dict(
    # --- Levee crest (levee path) : sidewalk 3 + planting strip 0.5 + bike road 4 on grass fill ---
    #  [W2-D · spec §5.9 17 (2)] Cross section re-cut. The old crown was
    #  walk 3.0 (x -6..-3) + bike 3.0 (x -3..0) with the two hard surfaces
    #  butted together. §5.9 prescribes **bike 3.0 -> 4.0, walk relocated,
    #  0.5 m planting strip between them**; the Han-river levee bikeway is the
    #  one place the supervisor left the bike road valid (§5.7 ruling, 07-29:
    #  "scene03 stays natural, the bike road is valid only on the scene17 levee").
    #    bike  x -4.0 .. 0.0   (4.0, asphalt)   <- crest side
    #    green x -4.5 .. -4.0  (0.5, grass)     <- separation strip
    #    walk  x -7.5 .. -4.5  (3.0, interlock) <- landward
    #  ★ `crown_bike.proud` 0.004 -> **0.006** so the two hard bands share one
    #    top plane z=+0.006. ground_kit lays its elements on that plane
    #    (`plan_ground(z=...)`); with two different tops half of them would be
    #    2 mm below the surface they belong to and read as buried.
    #  ★ `crown_line.x` -1.5 -> **-2.0** = centre of the widened bike road.
    #
    #  ═══ [GT-81] the whole crown moves 3.0 m LANDWARD — a real verge ═════════
    #  User verdict 08-06: *"the main road is right next to the slope — widen the
    #  distance and trim it neatly."* Measured, the complaint is exact: the bike
    #  road's riverward edge was `x = 0.000`, i.e. **the carriageway edge and the
    #  3.2 m drop edge were the same line** — zero verge, and the only thing
    #  between asphalt and a 1:2 bank was the 0.25 m cope [measured].
    #  Every crown band therefore translates by **dx = -3.0** and the freed strip
    #  `x -3.0 .. 0.0` becomes `verge` — levee crest turf, no new prim (a band
    #  prim at z=0 would be coplanar with `Levee`'s top and z-fight).
    #    bike  x -7.0 .. -3.0  (4.0, asphalt)   <- 3.0 m back from the crest
    #    green x -7.5 .. -7.0  (0.5, grass)
    #    walk  x -10.5 .. -7.5 (3.0, interlock)
    #    verge x -3.0 ..  0.0  (3.0, turf)      <- NEW, ends on the cope line
    #  Widths, `proud`, `embed` and the z ladder are untouched: this is a rigid
    #  translation, so the crown's own construction is unchanged and only its
    #  offset from the hazard moves. The drop edge stays `x = 0` (GT frozen); what
    #  changes is that the surface AT the edge is now turf, not asphalt, except at
    #  the two entry spurs (see `spurs`) that carry the road to the stair and ramp
    #  heads. Crest-edge z was already the cope's +0.050 wherever the cope runs,
    #  so `hazard_registry` is unaffected [computed].
    levee=dict(x0=-24.0, x1=0.0, y0=-30.0, y1=48.0, z_top=0.0, thick=3.6),
    crown_walk=dict(x0=-10.5, x1=-7.5, proud=0.006, embed=0.06),  # sidewalk (interlocking)
    crown_green=dict(x0=-7.5, x1=-7.0, top=0.000, embed=0.10),    # 0.5 planting separation strip
    crown_bike=dict(x0=-7.0, x1=-3.0, proud=0.006, embed=0.06),   # bike road (asphalt)
    crown_line=dict(x=-5.0, w=0.10, seg=2.4, gap=2.0, z=0.008),   # bike road centre dashed line
    # [GT-81] The verge is a datum, not a prim — the `Levee` crest turf already
    #   occupies x -24..0 at z=0. Recorded here so the spur builders and the smoke
    #   gate read one number instead of re-deriving `crown_bike["x1"]`.
    verge=dict(x0=-3.0, x1=0.0),

    # ═══ [W2-D ground_kit] P13 levee_paved — spec §5.9 scene17 row ═══════════
    #  (3) construction joints 3 m + patches · (4) interlock joints incised 2 mm (profile default) ·
    #  (6) drainage + gullies · (7) 1 manhole (W1) · (10) tread-wear lane.
    #  * Deviation from (6) "L-shaped gutter": `build_gutter_L` is a **carriageway edge**
    #    detail and `_compose_ops` always lays it at y = const spanning x0..x1,
    #    i.e. **across** the crown. Here the road runs along **Y** (the levee),
    #    so a y=const gutter would be perpendicular to the road it drains.
    #    The same drainage function is carried by a **linear trench drain at
    #    x = -7.15** (the bike road's landward edge, against the planting
    #    strip) which the kit can orient correctly. `gutter_L` is set to 0.
    #    GT-E2 check, re-run after the [GT-81] crown translation: the trench sits
    #    7.15 m in front of the crest, so at d2 it is at X=-5.15 and at d5 at
    #    X=-2.15 (both **behind** the eye) and at d10 at X=2.85 against the E band
    #    [7.0, 22.0] — **outside at every station**, i.e. it is never judged as a
    #    near-edge transverse line. The translation moves it further from the edge
    #    than the -4.15 it was cleared at, so the margin only grows [computed].
    #  ═══ [GT-81] the linear run now **terminates into a chamber at each end** ══
    #    The trench used to run y -4.80..+4.80 with the two gullies parked at
    #    y = ±5.50, i.e. a 9.6 m grating that **stopped in mid-pavement 0.70 m
    #    short of the thing it drains into** — the review cut's "fragment". The
    #    gully AABBs are y ∓5.70..∓5.30 [measured, `plan_ground` dry run], so the
    #    run is extended to y -5.30..+5.30 and now **butts the catch basin at both
    #    ends**: gully - trench - gully reads as one drainage set instead of three
    #    unrelated slabs. Length 9.60 -> 10.60 m; prim count unchanged (2).
    #  * (5) "block settlement +-3 mm (2x2 units)" is **not** placed here: it is a per-unit
    #    perturbation of the paving cell, which §4.4 assigns to T1 (MDL unit
    #    jitter). The kit's job is the ledger — unit_cell 0.200 / origin (0,0)
    #    is handed over by `plan_ground`.
    #  ═══ [W3 S17 · F5] the manhole is DERIVED, not sited ═══════════════════
    #  `tonglam_v2.md` FIX-5 calls the manhole *"the worst single prop"* in 17's d5 cut,
    #  and G-4 diagnosed why: its coordinate (−2.00, 1.20) was solved from the camera,
    #  not from a drainage network. `infra_kit.derive_manholes` now exists, so the
    #  coordinate list is **deleted** and replaced by the service line it should always
    #  have come from. `utility` below is that line; `build_ground_kit` runs the
    #  derivation live and the smoke prints it, so the count is a **result**, not a claim.
    #  Measured: Ø450 storm main under the trench drain at x = −7.15 ([GT-81]: it follows
    #  the trench, which followed the crown), the whole modelled levee y −30…48 (78.0 m).
    #  KDS 61 40 00 max straight-run interval for Ø ≤ 600 is **75 m**, so the run yields
    #  **2** chambers — `head` at (−7.15, −30.00) and one `interval` at (−7.15, +9.00) —
    #  and **both are outside the ground plan region** (x −10.5…−3.0, y −6…6). Manholes
    #  inside the plan: **0**, unchanged by the translation (the derivation never saw a
    #  camera and does not see the crown offset either). That is the whole of FIX-5.
    #  The gullies at (−7.15, ±5.50) are **not** declared as `junctions`: a 우수받이
    #  reaches the main through a 연결관, and treating each as a chamber trigger would
    #  put two manholes back into the near window by the back door.
    #
    #  `patches` is **deleted too**, and it is a measured null, not a hope: GT-24's
    #  `levee_paved` extension (`f39abe0`) already removed the profile's `("patch", 4)`
    #  row, so the site list has been inert since. CPU A/B of `plan_ground` with the list
    #  present vs absent: `patch` **0 in both arms**, element count and prim count equal.
    #  Kept as a comment rather than a live list because the user's ban on decorative
    #  ground rectangles makes a dormant list of four rectangles read as intent.
    #    was: patches=[(-1.15,-0.55), (-5.60,2.20), (-3.10,-3.40), (-6.40,-1.10)]
    #  ═══ [GT-81] the wear lane runs the WHOLE walk, not a 12 m island ════════
    #    `build_wear_lane` is a decal strip along a centreline and it is **not**
    #    clipped to `region` (checked: `plan_ground` accepts the full-length
    #    centreline and still passes B6-B12 [measured, dry run]). It used to be
    #    given y -6..+6, so a 0.90 x 12.0 m band began and ended in the middle of
    #    a 78 m footway — which is what reads as a slab dropped on the paving.
    #    It now spans the walk's own extent (levee y -30..48), so it terminates
    #    where the walk terminates and nowhere else. 1 prim either way.
    gkit=dict(
        region=(-10.5, -6.0, -3.0, 6.0),      # crown hard surface only (translated -3.0)
        gullies=[(-7.15, -5.50), (-7.15, 5.50)],
        trench=(-7.15, -5.30, 5.30),          # bike/green boundary drain, gully to gully
        wear_lane=((-9.00, -30.0), (-9.00, 48.0)),   # sidewalk wear axis (runs in Y, full walk)
    ),
    #  The declared storm main (G-4's `PARAMS["utility"]` shape). Laid where a real one
    #  runs: under the footway/bikeway boundary, parallel to the levee, toward the low end.
    utility=dict(line=[(-7.15, -30.0), (-7.15, 48.0)], d_mm=450.0, kind="storm"),
    # Crest-end cope — open exactly where an entry spur crosses it, nowhere else.
    #   [GT-81] the ramp gap moves 2.60..4.40 -> **3.15..4.55** so it is the ramp
    #   spur's own y-extent: the cope now ends flush against the spur edge on both
    #   sides instead of leaving a 0.55 m stub of turf between kerb and paving.
    #   The stair gap (±1.5) already equalled the stair width and is unchanged.
    cope=dict(x0=-0.20, x1=0.05, h=0.05,
              y_segs=((-30.0, -1.5), (1.5, 3.15), (4.55, 48.0))),
    # --- Grass bank: 7-segment polyline (rounded shoulder -> straight below, 50% average) ---
    #     Check rule: each segment end must sit **above** the stair chord (z = −0.5x)
    #     or the stairs get buried in the bank (auto-checked in the smoke run).
    slope=dict(segs=((0.7, 0.18), (0.8, 0.34), (0.9, 0.50), (1.0, 0.58),
                     (1.0, 0.60), (1.0, 0.50), (1.0, 0.50)),
               thick=3.0, margin=0.25, y0=-30.0, y1=48.0),
    # --- 20 stair steps : straight through the bank (width 3, concrete, no railing) ---
    stairs=dict(x0=0.0, riser=0.16, tread=0.32, nsteps=20,
                y0=-1.5, y1=1.5, z_top=0.0, base_z=-4.6),
    # --- Single diagonal ramp : crosses the bank obliquely ---
    #     length 25.6 m · grade 12.5% · width 2.5. Heading yaw = acos(6.4/25.6) = 75.5225 deg
    #     (only 6.4 m of X progress over 25.6 m of run -> the 50% bank grade stretched to 12.5%)
    #     offset e : how far the deck's uphill edge is pushed riverward from the
    #     bank-chord tangent. e_up=0.6 gives an uphill cut face of 0.07~0.30 m (0 buried).
    #     [W3 S17] Re-measured at length 25.6: cut 0.065~0.291 (positive everywhere, so the
    #       deck is never buried) and the worst river-side face 1.530 -> **1.500 m**, still
    #       far under the 2.35 m solid fill depth. The smoke prints both live — the v6
    #       figures below (1.53 / 1.18) are the judgment's record, not current values.
    #     [v6 judgment (a)] Exposed fill face: the river-side cut (max 1.53 m) read as a
    #       "concrete block laid on the bank" (judge_v6_rt_mod6 §6 — worst forced element).
    #       Causes: (a) material break (rock_wall vs surrounding grass) + (b) flat top +
    #       a vertical cut. Ramp deck · grade · width · endpoints (= hazard GT) stay **unchanged**;
    #       only the finish changes: Fill takes the same grass material as the bank, and a
    #       3-step grass batter is added river-side to break up the vertical face.
    #       batter: n steps x width w x drop dz (grade 1:1.19 ~ 40 deg — customary for a
    #       grass fill shoulder). 3 steps = width 1.50 · drop 1.26, covering the whole
    #       maximum exposure under the deck (1.53 − deck_t 0.35 = 1.18 m).
    #     [v7 judgment (11)-1 — why the fix did not show] W-5 did change `Fill` to grass,
    #       yet the judgment said "the brown mass is the same as v6". Back-projecting the
    #       prims through the levee_walk camera showed the mass was **`Ramp/Apron`, neither
    #       `Fill` nor `Deck`**. The cause is **local/world axis confusion** inside rot_group:
    #         · the apron assumed "local −X = behind the ramp = inland of the crest" and
    #           was placed at local x ∈ [−1.4, 0], y ∈ [0.9, 5.2], thickness 2.8 m.
    #         · but with rot_group yaw = 80.793 deg, local −X is not world −X but almost
    #           world −Y. The real world footprint has four corners
    #           (3.06,3.50) (2.84,2.12) (−1.41,2.81) (−1.18,4.19) —
    #           and **world x juts out over the bank as far as +3.06.**
    #         · the bank top there is z −1.40 while the apron top is −0.015 ->
    #           a **2.8 m thick concrete block standing 1.39 m above the bank**,
    #           whose vertical cut dominated the frame (= the brown mass in the judgment).
    #       -> the apron is rewritten outside rot_group as a **world-aligned crest landing**
    #         (build_ramp_apron below). The parameters here are that world rectangle.
    #         Thickness also drops 2.8 -> 0.35 (deck thickness) to remove the blockiness.
    #     [v7 judgment (11)-1 (a)] The batter read as "3 artificial steps" because a step
    #       height of 0.42 m is distinct at 17 m. **Keeping total width and drop (1.50 x 1.26)**,
    #       it splits into 9 steps at 0.14 m each (advised <=0.15) = a continuous slope.
    #     [W3 S17 · R17-1 (ii)] **length 40.0 -> 25.6, grade 8.0% -> 12.5%, yaw
    #       80.7931 -> 75.5225 deg.** `p0`, `width`, `e_up`, the deck thickness, the kerb
    #       and the batter are all **unchanged** — the single edited number is `length`,
    #       and every other ramp quantity is derived from it by `ramp_geom()`.
    #       *Why shorten and not re-site.* The ruling offers both. Measured in image space
    #       (scratchpad `s17_frame_metric.py`, default Isaac camera hFOV 60 / vFOV 36 at
    #       1920x1080, the frozen `build_views` eyes), against the ramp/stair projected-area
    #       ratio in `pair_compare`:
    #         · shorten, +Y sense (this)     40.0 -> 25.6 m : ratio 4.84 -> 3.59
    #         · re-site to descend in −Y     40.0 m         : ratio 4.84 -> **7.53** (worse:
    #           the ramp swings into the near field and takes 3.5 % of the frame)
    #         · re-site head-far, foot beside the stair foot : ratio -> **5.04**, and the two
    #           heads stop sharing the crest, which is the pair's premise (an agent standing
    #           at the drop edge must see both ways down)
    #       so **shorten** is the measured winner and the other two are recorded as tried.
    #       Ramp plan-Y extent **39.88 -> 25.41 m (−36 %)**; the deck's far end comes from
    #       65.5 m to 53.2 m off the `pair_compare` eye; the visible fraction of the deck in
    #       `preset_h1.8_d10` goes 15.7 % -> 26.5 %.
    #       *Why 25.6 and not 30.* 25.6 m is 3.2 / (1/8) — the run at the steepest gradient
    #       Korean accessibility law names (see the docstring's below-code declaration 2).
    #       30.0 m would be 10.67 % — a gradient no Korean standard names at all, i.e. an
    #       invented number, which this repo does not ship (RF-5's "not an invented yellow").
    #       Both are under the 30 m rest-landing threshold, so neither owes a landing.
    #     ═══ [GT-81] the head was a RAW CUT — `head` closes it ═══════════════
    #       Reading `pt_noon_levee_walk` and `pt_noon_ramp_run` (260731_w3_full):
    #       the embankment is truncated flat at s=0, so the whole transverse
    #       profile — deck 0.35, `Fill` down to −2.35, and the nine `Batter`
    #       steps — presents a vertical face standing over the bank. Measured at
    #       s=0 with `slope_z`: 0.15 m of exposure at the uphill corner (e 0.6)
    #       rising to **1.369 m** at the deck's river corner (e 3.1), and each
    #       batter step showing 0.66…1.07 m of its own end. That is the grey slab
    #       with a vertical left face, and the nine strips beside it that read as
    #       a picket comb.
    #       A fill embankment is never cut off; it **returns into the slope**. So
    #       every longitudinal band gets a mirror-image nose that starts at that
    #       band's own top and falls upstream at the batter's own grade
    #       (dz/w = 0.140/0.1667 = 1:1.19), until it dives under the bank surface.
    #       `run0` is the fill band's nose length and each batter band k gets
    #       `run0 - run_step*(k+1)` — the outer bands sit lower and need less, so
    #       the nose fans in plan instead of ending on one straight line.
    #       Closure, worst point of each band [computed, `slope_z` vs nose top]:
    #         fill (e 3.20) buried at t 1.15 < run 1.35 · batter k0 (e 3.37) at
    #         t 1.10 < 1.29 · k4 (e 4.03) at t 1.00 < 1.05 · k8 (e 4.70) at
    #         t 0.75 < 0.81 — every band closes inside its own run.
    #       Stair clearance is the binding constraint, not the closure: the nose
    #       runs upstream, i.e. toward the flight. Its most −Y corner is
    #       y = 1.89 (fill band) against the stair's y1 = 1.50, a **0.39 m**
    #       clear gap [computed]; that is why the runs are sized down to the
    #       minimum that still buries, and why they are not simply set equal.
    #     [GT-81] `curb_end` — the river-side kerb used to stop dead 0.146 m proud
    #       of the terrace at s=L. The last 0.50 m is now a dropped-kerb ramp to
    #       the foot apron's top, so the run ends at zero height like a real kerb
    #       does. The hazardous stretch (worst face 1.500 at s≈8…13.6) is nowhere
    #       near it, so the below-code declaration (1) is untouched [computed].
    ramp=dict(p0=(0.0, 4.0), length=25.6, width=2.5, e_up=0.60,
              deck_t=0.35, fill_t=2.0, fill_out=0.10,
              curb_w=0.15, curb_h=0.15, curb_end=0.50,
              batter=dict(n=9, w=0.1667, dz=0.14, margin=0.30),
              head=dict(run0=1.35, run_step=0.06, margin=0.10),
              apron=dict(build=False, x0=-1.60, x1=0.05, y0=0.60, y1=5.40,
                         t=0.35, drop=0.015)),
    # --- Terrace (riverside flat) : grass + promenade (width 3, parallel to the river) ---
    terrace=dict(x0=6.4, x1=27.5, y0=-30.0, y1=48.0, z_top=_TERRACE_Z,
                 thick=1.0),
    promenade=dict(x0=11.5, x1=14.5, proud=0.004, line_w=0.10, line_in=0.18),
    # ═══ [GT-81] `spurs` — the four links that stop both routes ending in turf ══
    #   The 08-06 audit: *"ramp slab isolated in grass, not connected to top levee
    #   road or bottom riverside road."* Measured before the fix, both routes were
    #   islands at **both** ends:
    #     · stair head  — the bike road reached x=0, so the head was fed only
    #       because the carriageway itself ran to the drop edge. Moving the crown
    #       3.0 m back (see `crown_*`) would have left a 3.0 m turf gap, so the
    #       spur is not decoration, it is what makes the widened verge legal.
    #     · ramp head   — the deck's uphill corner is (0.581, 3.850) and the crest
    #       ends at x=0: a 0.58 m turf notch, 0.152 m deep [computed].
    #     · stair foot  — flight ends x=6.40 z=−3.200; promenade starts x=11.50.
    #       **5.10 m of turf** between the last tread and the riverside path.
    #     · ramp foot   — deck foot edge (6.981, 28.636)…(9.402, 28.011) z=−3.200;
    #       same promenade edge. **2.10 m** of turf at the near corner.
    #   Each link is one slab, `proud` above the plate it lies on so nothing is
    #   coplanar (crest links +0.006 = the crown's own top plane; terrace links
    #   +0.004 = the promenade's), and each **ends on a built edge**, never in
    #   turf: crest links butt the bike road at x=-3.0, terrace links butt the
    #   promenade at x=11.5 exactly (edge to edge, no overlap, no z-fight).
    #   The ramp links are deliberately allowed to run a few cm past the deck's
    #   diagonal edge — the deck's plan boundary is at 75.52°, a box cannot follow
    #   it, and the residual is a 6 mm lip at worst (crest, where the deck top is
    #   z=0) or a clean intersection line (foot, where the 12.5 % deck simply
    #   emerges through the level apron). Both beat leaving a wedge of turf.
    #   None of these is a hazard surface: every one is flat, at the level of the
    #   plate it joins, and outside the GT drop registry [computed].
    spurs=dict(
        stair_crest=dict(x0=-3.00, x1=0.00, y0=-1.50, y1=1.50,
                         proud=0.006, embed=0.30),
        ramp_crest=dict(x0=-3.00, x1=0.70, y0=3.15, y1=4.55,
                        proud=0.006, embed=0.55),
        stair_foot=dict(x0=6.35, x1=11.50, y0=-1.50, y1=1.50,
                        proud=0.004, embed=0.26),
        ramp_foot=dict(x0=6.90, x1=11.50, y0=27.90, y1=30.40,
                       proud=0.004, embed=0.26),
    ),
    # --- Riprap revetment + water + far bank ---
    bank=dict(x0=27.5, run=2.0, drop=0.45, thick=1.2, margin=0.2),
    water=dict(x0=28.6, x1=72.0, y0=-42.0, y1=60.0, z=-3.42),
    far_bank=dict(x0=72.0, x1=100.0, y0=-42.0, y1=60.0, z_top=-3.1, thick=0.5),
    # [v6 judgment (b)] Far-bank silver-grass band — build_hedge boxes -> flat ellipsoid blobs.
    #   Planted at spacing with seeded size/position jitter (§3 bans even spacing).
    #   [v7 judgment (11)-2] the old layout was **1 row · evenly spaced (spacing 1.55,
    #     y jitter +-0.3 only)**, reading at 76 m as a "necklace of equal khaki beads" (§3).
    #     -> (1) 3 staggered rows across the band (dx sets fore/aft, y phase differs per row)
    #        (2) spacing becomes a **random walk** of spacing x U(0.55, 1.60) (even spacing gone)
    #        (3) size 0.60~1.45x · height 0.70~1.25x jitter (band advised by the judgment)
    #        (4) back row bigger and taller, front row smaller and lower -> the band gains depth.
    far_hedge=dict(cx=76.0, sx=1.2, length=26.0, h=1.7, spacing=1.55,
                   rad=0.80,
                   rows=((-1.15, 1.18, 0.00), (0.00, 1.00, 0.37),
                         (1.25, 0.82, 0.68))),
    far_hedges=[dict(cy=-26.0), dict(cy=3.0), dict(cy=32.0)],
    far_trees=[dict(cx=80.4, cy=-19.0), dict(cx=79.1, cy=7.0),
               dict(cx=80.9, cy=34.0)],
    # [v6 judgment (c)] Far-bank apartments — fixes "4 identical blocks on an even grid".
    #   Old: x0 fixed at 88.0 (only H 89.5) · width 20/20/18/16 · gaps 8/6/6 · height 42/48/38/44
    #       -> facades lined up on one plane and the silhouette read as a repeating grid (§3).
    #   New: (1) setback (x0) 85.5~90.5, a 3.0 m spread -> facade plane broken up (depth)
    #       (2) width 17/23/15/17, gaps 8/5/11 -> no repeat period
    #       (3) height 36/49/41/30.5 · floors 12/16/14/10 (floor height 2.93~3.06 m, real band)
    #       (4) 4 tints cycled (shell / shell_c / shell_b / shell_d) — neighbours differ
    #   All far backdrop; no bearing on hazard geometry or continuity. Within far_bank x 72..100.
    far_buildings=dict(
        E=dict(x0=86.5, x1=94.5, y0=-38.0, y1=-21.0, h=36.0, floors=12,
               axis="x", facade_x=86.5, face_dir=-1.0, base_z=-3.1),
        F=dict(x0=89.0, x1=97.0, y0=-13.0, y1=10.0, h=49.0, floors=16,
               axis="x", facade_x=89.0, face_dir=-1.0, base_z=-3.1),
        G=dict(x0=85.5, x1=93.5, y0=15.0, y1=30.0, h=41.0, floors=14,
               axis="x", facade_x=85.5, face_dir=-1.0, base_z=-3.1),
        H=dict(x0=90.5, x1=98.5, y0=41.0, y1=58.0, h=30.5, floors=10,
               axis="x", facade_x=90.5, face_dir=-1.0, base_z=-3.1),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.6, margin=2.0),
    bridge=dict(x0=42.0, x1=46.0, y0=-42.0, y1=60.0, deck_top=6.0,
                deck_t=1.2, pier_r=1.2, pier_x=44.0,
                pier_ys=(-30.0, -10.0, 12.0, 34.0, 54.0), pier_base=-3.7),

    # --- Dressing (irregular placement: no even spacing, beside anchors, yaw jitter) ---
    #     Placed clear of the ramp footprint (the diagonal strip) and the stair width.
    # [v6 judgment (b)] Silver-grass band — build_hedge boxes (khaki boxes reading as
    #   straw bales / containers) replaced by **stalk clumps**, porting the scene09
    #   build_reeds rule (thin cylinders r0.022 · height jitter · slight tilt · fixed seed).
    #   The band rectangle stays; stalks are scattered inside it at density [stalks/m²].
    reeds=[dict(x0=24.6, y0=-18.0, x1=26.4, y1=-6.5, h=1.35, seed=171),
           dict(x0=24.9, y0=5.0, x1=26.6, y1=15.8, h=1.25, seed=172),
           dict(x0=25.2, y0=26.0, x1=26.8, y1=33.4, h=1.40, seed=173),
           dict(x0=7.4, y0=-27.0, x1=8.9, y1=-20.2, h=1.10, seed=174)],
    reed=dict(r=0.022, density=6.0, h_lo=0.80, h_hi=1.12, tilt=9.0),
    reed_tint=(0.42, 0.44, 0.26),
    terrace_trees=[(17.6, -14.2), (19.8, 8.6), (16.9, 30.1), (21.4, 39.7),
                   (18.2, -23.5)],
    terrace_benches=[(16.2, -13.0, 96.0), (16.4, 9.8, -84.0),
                     (15.9, 29.2, 93.0), (10.6, -21.4, -86.0)],
    terrace_lights=[(15.1, -19.0), (15.1, 1.5), (15.1, 22.0), (15.1, 41.0)],
    # [W2-D §5.9 ②] x -6.4 -> -7.9. The re-cut crown moved the walk to
    #   x -7.5..-4.5, so -6.4 would put a lighting pole in the middle of
    #   the footway. -7.9 is 0.4 m landward of the walk edge.
    # [GT-81] -7.9 -> -10.9: the crown translated -3.0, so the same
    #   "0.4 m landward of the walk edge (now -10.5)" rule gives -10.9.
    #   The arm still reaches +1.0 m riverward, i.e. to x -9.9, inside the
    #   walk's landward half — lighting geometry unchanged.
    crown_lights=[(-10.9, -12.0), (-10.9, 9.5), (-10.9, 31.0)],
    streetlight=dict(pole_h=4.6, pole_r=0.075, arm_len=1.0, arm_r=0.045,
                     head=0.25),
    # [GT-81] all four translated -3.0 with the crown. Without it the -9.8 tree
    #   would stand in the middle of the relocated footway (x -10.5..-7.5).
    #   Landward-most is now -20.1, still 3.9 m inside the levee body (x0 -24.0).
    crown_trees=[(-14.2, -8.4), (-17.6, 12.7), (-12.8, 33.2), (-20.1, -19.6)],
    km_sign=dict(x=14.9, y=-4.6, pole_r=0.05, pole_h=2.2,
                 panel=(0.06, 0.7, 0.42), panel_z=1.95),

    material=dict(
        scale=dict(concrete_floor=0.9, paving_interlock=1.2, grass=1.4,
                   rock_wall=1.6, asphalt=3.0),          # [W2-D §5.9 ①]
        grass_tint=(0.54, 0.66, 0.41),
        grass_tint_b=(0.49, 0.62, 0.38),          # bank grass (tint jitter −5%)
        # [W2 fix batch F4] Two more grass looks. At `h1.8_d10` about 70 % of the frame
        #   is turf, and every turf prim carried one of two materials whose tints differ
        #   by 5 % **along the same channel ratio** - a brightness step, not a hue step -
        #   at one fixed `scale_m` 1.4. World-projected at a single tile size the 4096 px
        #   source repeats on an exact grid, which is what reads as a printed leaf carpet.
        #   These break the ratio (yellower / bluer-greyer) *and* the tile size, and are
        #   dealt out per **large** prim - never between adjacent ramp steps, which is the
        #   striping the v6 note at `build_ramp` warns about.
        grass_tint_c=(0.57, 0.65, 0.36),          # sun-bleached, yellower
        grass_tint_d=(0.46, 0.60, 0.42),          # shaded, bluer-greyer
        grass_scale_c=1.05,
        grass_scale_d=1.85,
        # [v7 judgment (11)-1] The `concrete_floor` diff average is sRGB (115.7,102.2,77.0) =
        #   a warm brown earth. The old tint (0.80,0.79,0.76) kept the channel ratio, so the
        #   render came out sRGB (98,87,69) — **brown**. Ramp deck · kerb · crest kerb ·
        #   stairs all use this material, so half of the "brown mass" impression was colour.
        #   -> linear channel equalisation (same as the scene06/11 W-1 rule): R and G are
        #   pulled down to the lowest channel (B), giving sRGB (80,79,78) ~ neutral grey concrete.
        conc_tint=(0.53, 0.66, 1.00),
        paving_tint=(0.84, 0.83, 0.81),
        # [GT-81] Trodden interlock. `ground_kit.build_wear_lane` declares
        #   albedo 0.22 and the scene bound it to `conc`, so a 0.90 m band of a
        #   **different material** was laid on the footway — the "slab" of the
        #   review cut. A wear lane is the same paving, walked dull: same
        #   texture, same scale, tint pulled to 0.74x of `paving_tint`, which is
        #   the ratio between the kit's declared 0.22 and the interlock's
        #   nominal 0.30 [derived].
        paving_worn_tint=(0.62, 0.61, 0.60),
        rock_tint=(0.72, 0.71, 0.68),
        asphalt_color=(0.145, 0.145, 0.155), asphalt_rough=0.86,
        # [W2-D §5.9 ①] tint for the textured asphalt — keeps the old
        #   constant-colour value as the target mean (albedo well under 0.30).
        asphalt_tint=(0.42, 0.42, 0.45),
        paint_color=(0.70, 0.70, 0.66), paint_rough=0.62,   # no pure white (<0.8)
        water_color=(0.05, 0.10, 0.11), water_rough=0.06,
        rail_color=(0.66, 0.68, 0.70), rail_metallic=0.7, rail_rough=0.4,
        wood_color=(0.28, 0.19, 0.12), wood_rough=0.85,
        post_color=(0.33, 0.33, 0.36), post_metallic=0.35, post_rough=0.5,
        glass_color=(0.055, 0.075, 0.10), glass_rough=0.08,
        parapet_color=(0.60, 0.60, 0.58), parapet_rough=0.62,
        shell_tint=(0.84, 0.82, 0.79), shell_tint_b=(0.78, 0.77, 0.76),
        # [v6 judgment (c)] 2 extra tints so the apartment blocks can cycle 4
        shell_tint_c=(0.80, 0.77, 0.71), shell_tint_d=(0.73, 0.74, 0.73),
        bridge_color=(0.045, 0.045, 0.050), bridge_rough=0.7,
        lamp_color=(0.78, 0.78, 0.74), lamp_rough=0.4,
        sign_color=(0.05, 0.09, 0.16), sign_rough=0.5,
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
# [C] Paths + texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene17")
ASSET_ROLES = ["concrete_floor", "paving_interlock", "grass", "rock_wall",
               "hdri", "mdl"]


# ===========================================================================
# [C2] Bank and ramp geometry — the single source of truth for all functions
# ===========================================================================
def slope_nodes():
    """Bank polyline vertices [(x, z), ...] (starting at x=0, z=0)."""
    x, z = 0.0, 0.0
    nodes = [(0.0, 0.0)]
    for run, drop in PARAMS["slope"]["segs"]:
        x += run
        z -= drop
        nodes.append((round(x, 6), round(z, 6)))
    return nodes


def slope_z(xq):
    """Bank surface z(x). Crest (0) for x<0, terrace beyond the bank end."""
    if xq <= 0.0:
        return 0.0
    x, z = 0.0, 0.0
    for run, drop in PARAMS["slope"]["segs"]:
        if xq <= x + run + 1e-12:
            return z - drop * (xq - x) / run
        x += run
        z -= drop
    return z


def ramp_geom():
    """Heading and unit vectors of the diagonal ramp. Returned dict:
      yaw   : rot_group rotation (deg). Local +X -> travel direction d, local +Y -> −n (uphill)
      d     : travel unit vector (in plan), n : river-side (downhill) normal unit vector
      length/drop/grade, e_up/e_dn : uphill / downhill edge offsets (riverward +)
    Derivation: for the deck to stretch the bank chord (50% grade) out to 8%, every 1 m
      of travel must advance dx = grade/0.5 = 0.16 m in X -> cos(yaw) = 0.16."""
    rp = PARAMS["ramp"]
    L = float(rp["length"])
    drop = float(_SLOPE_H)
    cos_p = float(_SLOPE_RUN) / L                  # 0.16
    sin_p = math.sqrt(max(0.0, 1.0 - cos_p * cos_p))
    return dict(yaw=math.degrees(math.acos(cos_p)),
                d=(cos_p, sin_p), n=(sin_p, -cos_p),
                length=L, drop=drop, grade=drop / L,
                e_up=float(rp["e_up"]),
                e_dn=float(rp["e_up"]) + float(rp["width"]))


def derived_manholes():
    """[W3 S17 · F5] Chambers the declared storm main needs — `infra_kit.derive_manholes`.

    G-4's rule, applied rather than quoted: a manhole exists where the **line** does
    something (방향 / 경사 / 관경 변화 or 합류) and otherwise at the KDS 61 40 00
    straight-run interval for its diameter. This function knows nothing about cameras,
    which is the entire point of FIX-5 — the old coordinate (−2.00, 1.20) was solved
    from the d5 near window."""
    u = PARAMS["utility"]
    return ik.derive_manholes([tuple(p) for p in u["line"]],
                              d_mm=float(u["d_mm"]), kind=u["kind"])


def ramp_point(s, e):
    """Ramp path parameters (s: distance travelled, e: riverward lateral offset) -> world (x, y, z)."""
    g = ramp_geom()
    px, py = PARAMS["ramp"]["p0"]
    x = px + g["d"][0] * s + g["n"][0] * e
    y = py + g["d"][1] * s + g["n"][1] * e
    return (x, y, -g["grade"] * s)


# ===========================================================================
# [C3] Smoke — pre-boot geometry self-check (early exit)
# ===========================================================================
def hazard_registry():
    """**R-1 for GT-27** — re-derive the hazard / drop registry from `PARAMS`, boot-free.

    `gt_changes_w3.md` §1 R-1: *"the scene's own self-check re-derives and prints the
    hazard/drop registry from the changed geometry"*. Rows are derived, never typed:
    every z comes out of `slope_z` / `ramp_geom` / the stair ladder.

    Returns `[dict(tag, kind, x, y, z_top, fall, note), …]`; `kind` is `drop`
    (a negative obstacle), `up_step` (never to be labelled a drop — GT-1's rule) or
    `grade` (a walked surface that descends without an edge)."""
    st = PARAMS["stairs"]
    rp = PARAMS["ramp"]
    sl = PARAMS["slope"]
    cp = PARAMS["cope"]
    g = ramp_geom()
    rows = []
    # (1) the scene's negative obstacle: the crest shoulder, everywhere the stair gap is not
    rows.append(dict(tag="levee_crest", kind="drop", x=float(st["x0"]),
                     y=(float(sl["y0"]), float(sl["y1"])),
                     z_top=0.0, fall=float(_SLOPE_H),
                     note="bank shoulder x=0 -> terrace; no guard (unrailed by custom)"))
    # (2) the flight — 20 nosings, frozen by R17-1 (ii)
    for k in range(int(st["nsteps"])):
        rows.append(dict(tag=f"stair_nosing_{k + 1:02d}", kind="drop",
                         x=float(st["x0"]) + st["tread"] * k,
                         y=(float(st["y0"]), float(st["y1"])),
                         z_top=-st["riser"] * k, fall=float(st["riser"]),
                         note="frozen"))
    # (3) route B — a graded walked surface, NOT a drop
    rows.append(dict(tag="ramp_deck", kind="grade", x=float(rp["p0"][0]),
                     y=float(rp["p0"][1]), z_top=0.0, fall=float(g["drop"]),
                     note=f"length {g['length']:.2f} m, grade {g['grade'] * 100:.2f}%, "
                          f"yaw {g['yaw']:.4f} deg — descends without an edge"))
    # (4) the ramp's river-side edge: kerb only, over the fill face -> a real lateral fall
    worst_face, worst_s = 0.0, 0.0
    for i in range(0, 129):
        s = g["length"] * i / 128.0
        xd = g["d"][0] * s + g["n"][0] * g["e_dn"]
        gz = slope_z(xd) if xd <= _SLOPE_RUN else _TERRACE_Z
        face = (-g["grade"] * s) - gz
        if face > worst_face:
            worst_face, worst_s = face, s
    px, py = rp["p0"]
    rows.append(dict(tag="ramp_river_edge", kind="drop",
                     x=px + g["d"][0] * worst_s + g["n"][0] * g["e_dn"],
                     y=py + g["d"][1] * worst_s + g["n"][1] * g["e_dn"],
                     z_top=-g["grade"] * worst_s, fall=worst_face,
                     note=f"worst section at s={worst_s:.2f}; kerb h{rp['curb_h']:.2f} "
                          f"only — declared below-code reality (1)"))
    # (5) the crest cope — an UP-stand, never a drop (GT-1's labelling rule)
    rows.append(dict(tag="crest_cope", kind="up_step", x=float(cp["x0"]),
                     y=tuple(cp["y_segs"][0]), z_top=float(cp["h"]),
                     fall=float(cp["h"]),
                     note="cope proud of the crest; open at the stair gap and the ramp entry"))
    return rows


def _frame_metric():
    """[W3 S17] The acceptance test for **R17-1 (ii)** — projected ramp/stair area.

    The ruling asks that *"the stair-ramp pair reads in one frame"* with the judge
    presets untouched, so the instrument has to be image space, not plan space. Default
    Isaac viewport camera: focalLength 18.147 / horizontalAperture 20.955 -> **hFOV 60.0
    deg**, 16:9 -> **vFOV 36.0 deg** at 1920x1080. Cameras come from `build_views()`,
    which this work package does not edit."""
    W, H = 1920.0, 1080.0
    fx = (W / 2.0) / math.tan(math.radians(60.0) / 2.0)
    fy = (H / 2.0) / math.tan(math.radians(36.0) / 2.0)
    st = PARAMS["stairs"]
    rp = PARAMS["ramp"]
    g = ramp_geom()
    px, py = rp["p0"]
    stair = [(st["x0"], st["y0"], 0.0), (st["x0"], st["y1"], 0.0),
             (st["x0"] + st["nsteps"] * st["tread"], st["y1"], -_SLOPE_H),
             (st["x0"] + st["nsteps"] * st["tread"], st["y0"], -_SLOPE_H)]
    ramp = [(px + g["d"][0] * s + g["n"][0] * e,
             py + g["d"][1] * s + g["n"][1] * e, -g["grade"] * s)
            for s, e in ((0.0, g["e_up"]), (0.0, g["e_dn"]),
                         (g["length"], g["e_dn"]), (g["length"], g["e_up"]))]

    def basis(eye, tgt):
        f = [tgt[i] - eye[i] for i in range(3)]
        n = math.sqrt(sum(c * c for c in f))
        f = [c / n for c in f]
        r = [f[1], -f[0], 0.0]
        n = math.sqrt(r[0] * r[0] + r[1] * r[1]) or 1.0
        r = [r[0] / n, r[1] / n, 0.0]
        u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2],
             r[0] * f[1] - r[1] * f[0]]
        return f, r, u

    def proj(p, eye, bs):
        f, r, u = bs
        v = [p[i] - eye[i] for i in range(3)]
        z = sum(v[i] * f[i] for i in range(3))
        if z <= 1e-6:
            return None
        return (W / 2.0 + fx * sum(v[i] * r[i] for i in range(3)) / z,
                H / 2.0 - fy * sum(v[i] * u[i] for i in range(3)) / z)

    def clip(poly):
        out = list(poly)
        for e in range(4):
            if not out:
                return []
            inp, out = out, []
            for i in range(len(inp)):
                a, b = inp[i - 1], inp[i]

                def ins(p, e=e):
                    return (p[0] >= 0.0, p[0] <= W, p[1] >= 0.0, p[1] <= H)[e]

                def cut(a, b, e=e):
                    if e < 2:
                        xe = 0.0 if e == 0 else W
                        t = (xe - a[0]) / (b[0] - a[0])
                        return (xe, a[1] + t * (b[1] - a[1]))
                    ye = 0.0 if e == 2 else H
                    t = (ye - a[1]) / (b[1] - a[1])
                    return (a[0] + t * (b[0] - a[0]), ye)

                if ins(b):
                    if not ins(a):
                        out.append(cut(a, b))
                    out.append(b)
                elif ins(a):
                    out.append(cut(a, b))
        return out

    def area(poly):
        if len(poly) < 3:
            return 0.0
        return abs(sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1]
                       for i in range(len(poly)))) / 2.0

    out = []
    views = build_views()
    for vn in ("pair_compare", "across_river", "toe_lookup",
               "preset_h0.9_d10", "preset_h1.8_d10"):
        v = views[vn]
        bs = basis(v["eye"], v["tgt"])
        vals = {}
        for nm, poly in (("stair", stair), ("ramp", ramp)):
            pp = [proj(p, v["eye"], bs) for p in poly]
            vals[nm] = (0.0, 0.0) if any(q is None for q in pp) else \
                (area(clip(pp)), area(pp))
        out.append((vn, vals["stair"][0] / (W * H), vals["ramp"][0] / (W * H),
                    (vals["ramp"][0] / vals["stair"][0]) if vals["stair"][0] > 1e-6 else float("inf"),
                    (vals["ramp"][0] / vals["ramp"][1] * 100.0) if vals["ramp"][1] > 1e-6 else 0.0))
    return out


def _smoke_report():
    st = PARAMS["stairs"]
    rp = PARAMS["ramp"]
    sl = PARAMS["slope"]
    te = PARAMS["terrace"]
    wt = PARAMS["water"]
    g = ramp_geom()

    print("=" * 74)
    print("scene17_ramp_pair_hangang — SMOKE 기하 자기검증 (부팅 없음, v5.1)")
    print("=" * 74)

    # ── Bank polyline (grade 1:2) ──
    nodes = slope_nodes()
    print(f"  [잔디 사면 폴리라인]  {len(sl['segs'])}세그 · 두께 "
          f"{sl['thick']:.1f} · 세그 margin {sl['margin']:.2f}(겹침)")
    ok_chord = True
    for i, (run, drop) in enumerate(sl["segs"]):
        x0, z0 = nodes[i]
        x1, z1 = nodes[i + 1]
        above = z1 >= -0.5 * x1 - 1e-9
        ok_chord &= above
        print(f"    seg{i + 1}: x {x0:5.2f} → {x1:5.2f}  z {z0:+.3f} → "
              f"{z1:+.3f}  구배 {drop / run * 100:5.1f}%  "
              f"현(−0.5x) 대비 {'위 OK' if above else '아래 FAIL'}")
    tot_run = nodes[-1][0]
    tot_drop = -nodes[-1][1]
    print(f"    총 {tot_run:.2f} × {tot_drop:.2f} → 평균 구배 "
          f"{tot_drop / tot_run * 100:.1f}% (1:2 = 50%) → "
          f"{'OK' if abs(tot_drop / tot_run - 0.5) < 1e-6 else 'FAIL'}")
    print(f"    계단 매몰 방지(전 절점이 현 위): "
          f"{'OK' if ok_chord else 'FAIL'}")

    # ── Contrast pair ──
    sdrop = st["nsteps"] * st["riser"]
    srun = st["nsteps"] * st["tread"]
    print("  [대비쌍: 같은 낙차 · 다른 경사]")
    print(f"    계단 {st['nsteps']}단 × riser {st['riser']} = 낙차 "
          f"{sdrop:.2f} · run {srun:.2f} → 경사 {sdrop / srun * 100:.0f}% "
          f"(폭 {st['y1'] - st['y0']:.1f}, 무난간 관행)")
    print(f"    램프 길이 {g['length']:.1f} · 낙차 {g['drop']:.2f} → 경사 "
          f"{g['grade'] * 100:.1f}% (폭 {rp['width']:.1f}, 사선 단일로)")
    print(f"    낙차 일치 {sdrop:.2f} ≈ {g['drop']:.2f} → "
          f"{'OK' if abs(sdrop - g['drop']) < 1e-6 else 'FAIL'} · "
          f"계단 run {srun:.2f} = 사면 수평 {tot_run:.2f} → "
          f"{'OK' if abs(srun - tot_run) < 1e-6 else 'FAIL'}")
    print(f"    낙차 검증: {sdrop:.2f} ≥ 0.3 m → "
          f"{'OK' if sdrop >= 0.3 else 'FAIL'}")

    # ── Ramp diagonal placement · cut/fill check ──
    p_end = ramp_point(g["length"], (g["e_up"] + g["e_dn"]) / 2.0)
    print("  [사선 램프 배치]")
    print(f"    yaw {g['yaw']:.4f}° (cos = {_SLOPE_RUN}/{g['length']:.1f} = "
          f"{g['d'][0]:.3f}) · 시점 {rp['p0']} · 종점 중심 "
          f"({p_end[0]:.2f}, {p_end[1]:.2f}, {p_end[2]:+.2f})")
    print(f"    상류 절토(+) / 매몰(−) · 강측 석축 높이:")
    # [W3 S17] The station list is **derived from the live length**. It used to be the
    #   literal `(0, 6, 12, 20, 28, 34, 40)`, which silently sampled 14.4 m of thin air
    #   the moment `length` moved off 40 and reported a bogus FAIL for both this gate and
    #   the batter gate below. Six equal stations + the end, whatever the length is.
    _S = tuple(g["length"] * k / 6.0 for k in range(7))
    worst_cut, worst_face = 9.9, 0.0
    for s in _S:
        deck = -g["grade"] * s
        xu = g["d"][0] * s + g["n"][0] * g["e_up"]
        xd = g["d"][0] * s + g["n"][0] * g["e_dn"]
        tu = slope_z(xu) if xu <= tot_run else te["z_top"]
        td = slope_z(xd) if xd <= tot_run else te["z_top"]
        cut = deck - tu
        face = deck - td
        worst_cut = min(worst_cut, cut)
        worst_face = max(worst_face, face)
        print(f"      s{s:5.1f}  노면 {deck:+.3f} · 상류edge x{xu:5.2f} "
              f"지반 {tu:+.3f} → 절토 {cut:+.3f} · 강측edge x{xd:5.2f} "
              f"지반 {td:+.3f} → 석축 {face:.3f}")
    print(f"    최소 절토 {worst_cut:+.3f} ≥ 0 (음수면 노면이 잔디에 매몰) → "
          f"{'OK' if worst_cut >= -1e-9 else 'FAIL'}")
    fill_bot = rp["deck_t"] + rp["fill_t"]
    print(f"    최대 석축 {worst_face:.3f} < 성토 두께 {fill_bot:.2f} "
          f"(노면 밑 {fill_bot:.2f} m 까지 솔리드) → "
          f"{'OK (부유 없음)' if worst_face < fill_bot else 'FAIL'}")

    # ── [v6 judgment (a)] river-side grass batter check ──
    bt = rp["batter"]
    n_bt, w_bt, dz_bt = int(bt["n"]), float(bt["w"]), float(bt["dz"])
    e_toe = g["e_dn"] + rp["fill_out"] + w_bt * n_bt
    print(f"  [강측 잔디 배터] {n_bt}단 × 폭 {w_bt:.2f} × 낙차 {dz_bt:.2f} "
          f"= 폭 {w_bt * n_bt:.2f} · 낙차 {dz_bt * n_bt:.2f} "
          f"(구배 {dz_bt / w_bt * 100:.0f}% ≈ 1:{w_bt / dz_bt:.2f})")
    print(f"    덮어야 할 노면 밑 최대 노출 = 최대석축 {worst_face:.3f} − "
          f"노면두께 {rp['deck_t']:.2f} = {worst_face - rp['deck_t']:.3f} m → "
          f"{'OK (배터 낙차가 더 큼)' if dz_bt * n_bt >= worst_face - rp['deck_t'] else 'FAIL'}")
    worst_res, x_toe_max, y_toe_min = 0.0, -99.0, 99.0
    for s in _S:                                   # [W3 S17] length-derived, see above
        deck = -g["grade"] * s
        z_toe = deck - rp["deck_t"] - dz_bt * n_bt
        x_toe = g["d"][0] * s + g["n"][0] * e_toe
        y_toe = rp["p0"][1] + g["d"][1] * s + g["n"][1] * e_toe
        gz = slope_z(x_toe) if x_toe <= tot_run else te["z_top"]
        res = max(0.0, z_toe - gz)
        worst_res = max(worst_res, res)
        x_toe_max, y_toe_min = max(x_toe_max, x_toe), min(y_toe_min, y_toe)
        print(f"      s{s:5.1f}  배터 끝 (x{x_toe:5.2f}, y{y_toe:6.2f}) "
              f"상면 {z_toe:+.3f} · 지반 {gz:+.3f} → 잔여 잔디면 {res:.3f}")
    print(f"    잔여 최대 {worst_res:.3f} m (구 수직 절단면 {worst_face:.3f} m "
          f"대비 −{(1 - worst_res / worst_face) * 100:.0f}%) · 전 구간 잔디 재질")
    print(f"    배터 풋프린트: x ≤ {x_toe_max:.2f} < 산책로 x0 "
          f"{PARAMS['promenade']['x0']:.1f} → "
          f"{'OK' if x_toe_max < PARAMS['promenade']['x0'] else 'FAIL'} · "
          f"y ≥ {y_toe_min:.2f} > 계단 y1 {st['y1']:.1f} → "
          f"{'OK (계단 무간섭)' if y_toe_min > st['y1'] else 'FAIL'}")

    # ── [GT-81] head return (nose) closure + stair clearance ──
    hd = rp["head"]
    bt2 = rp["batter"]
    k_ret = float(bt2["dz"]) / float(bt2["w"])
    e_fill_hi = g["e_dn"] + rp["fill_out"]
    noses = [("fill  ", float(hd["run0"]), -rp["deck_t"], e_fill_hi)]
    for k in range(int(bt2["n"])):
        noses.append((f"batt{k}", float(hd["run0"]) - float(hd["run_step"]) * (k + 1),
                      -rp["deck_t"] - bt2["dz"] * (k + 1),
                      e_fill_hi + bt2["w"] * (k + 1)))
    print(f"  [GT-81 램프 두부 리턴] {len(noses)}밴드 × 구배 1:{1.0 / k_ret:.2f} "
          f"(배터와 동일) · 기준 런 {hd['run0']:.2f} − {hd['run_step']:.2f}/밴드")
    ok_nose, y_min_nose = True, 99.0
    for tag, run_j, z0_j, e_hi in noses:
        t_close = None
        for i in range(1, 201):
            t = run_j * i / 200.0
            xw = g["n"][0] * e_hi - g["d"][0] * t
            gz = slope_z(xw) if xw <= tot_run else te["z_top"]
            if z0_j - k_ret * t <= gz + 1e-9:
                t_close = t
                break
        y_corner = rp["p0"][1] + g["n"][1] * e_hi - g["d"][1] * run_j
        y_min_nose = min(y_min_nose, y_corner)
        ok = t_close is not None
        ok_nose &= ok
        face0 = z0_j - (slope_z(g["n"][0] * e_hi) if g["n"][0] * e_hi <= tot_run
                        else te["z_top"])
        print(f"    {tag} e{e_hi:5.2f} 절단면 {max(0.0, face0):5.3f} m → 런 "
              f"{run_j:.2f} · 매몰 t "
              f"{('%.2f' % t_close) if ok else ' 미매몰'} · 끝단 y {y_corner:6.2f}")
    print(f"    전 밴드 자기 런 안에서 지반에 매몰 → "
          f"{'OK (수직 절단면 소멸)' if ok_nose else 'FAIL'}")
    print(f"    두부 최소 y {y_min_nose:.2f} > 계단 y1 {st['y1']:.2f} → "
          f"{'OK (계단 무간섭, 여유 %.2f m)' % (y_min_nose - st['y1']) if y_min_nose > st['y1'] else 'FAIL'}")

    # ── [GT-81] crown offset — the road is no longer on the drop edge ──
    vg = PARAMS["verge"]
    cb, cw, cg = PARAMS["crown_bike"], PARAMS["crown_walk"], PARAMS["crown_green"]
    print("  [GT-81 마루 단면 후퇴] 도로↔사면 이격")
    print(f"    보도 [{cw['x0']:6.2f},{cw['x1']:6.2f}] · 식수대 "
          f"[{cg['x0']:6.2f},{cg['x1']:6.2f}] · 자전거도로 "
          f"[{cb['x0']:6.2f},{cb['x1']:6.2f}] · 녹지 verge "
          f"[{vg['x0']:6.2f},{vg['x1']:6.2f}]")
    print(f"    자전거도로 강측 끝 {cb['x1']:+.2f} → 낙차 시단 {st['x0']:+.2f} "
          f"이격 {st['x0'] - cb['x1']:.2f} m (구 0.00) → "
          f"{'OK' if st['x0'] - cb['x1'] >= 2.5 else 'FAIL'}")
    print(f"    폭 보존: 자전거 {cb['x1'] - cb['x0']:.2f} · 보도 "
          f"{cw['x1'] - cw['x0']:.2f} · 분리대 {cg['x1'] - cg['x0']:.2f} → "
          f"{'OK (강체 평행이동)' if abs((cb['x1'] - cb['x0']) - 4.0) < 1e-9 and abs((cw['x1'] - cw['x0']) - 3.0) < 1e-9 else 'FAIL'}")
    print(f"    낙차 시단 불변 x {st['x0']:.2f} · 사면 시단 불변 → "
          f"{'OK' if abs(st['x0']) < 1e-9 else 'FAIL'}")

    # ── [GT-81] links — no run may end in turf, no slab may float ──
    sp = PARAMS["spurs"]
    pm = PARAMS["promenade"]
    print("  [GT-81 접속 슬래브] 양 끝이 축조면에 닿는가 · 부유 없는가")
    _lk = (("stair_crest", 0.0, cb["x1"], st["x0"], "자전거도로", "계단 시단"),
           ("ramp_crest", 0.0, cb["x1"], None, "자전거도로", "램프 상류변"),
           ("stair_foot", te["z_top"], None, pm["x0"], "계단 하단", "산책로"),
           ("ramp_foot", te["z_top"], None, pm["x0"], "램프 노면", "산책로"))
    ok_link = True
    for key, base, x_in, x_out, nm_in, nm_out in _lk:
        b = sp[key]
        z_hi, z_lo = base + b["proud"], base - b["embed"]
        d_in = None if x_in is None else b["x0"] - x_in
        d_out = None if x_out is None else b["x1"] - x_out
        # underside vs ground at the riverward end (crest links overhang the shoulder)
        gz_end = (slope_z(b["x1"]) if base == 0.0 and b["x1"] > 0.0
                  else (te["z_top"] if base != 0.0 else 0.0))
        floats = z_lo > gz_end + 1e-9
        ok_link &= (d_in is None or abs(d_in) < 1e-9) and \
                   (d_out is None or abs(d_out) < 1e-9) and not floats
        print(f"    {key:12s} x [{b['x0']:6.2f},{b['x1']:6.2f}] y "
              f"[{b['y0']:6.2f},{b['y1']:6.2f}] 상면 {z_hi:+.3f} 하면 {z_lo:+.3f}")
        print(f"      {nm_in} 접합 "
              f"{'—' if d_in is None else '%+.3f m' % d_in} · {nm_out} 접합 "
              f"{'—' if d_out is None else '%+.3f m' % d_out} · 강측 끝 지반 "
              f"{gz_end:+.3f} → {'부유 FAIL' if floats else '착지 OK'}")
    # the two turf gaps the links close, restated as the numbers they were
    print(f"    구 잔디 공백: 계단 하단 {pm['x0'] - (st['x0'] + srun):.2f} m · "
          f"램프 하단 {pm['x0'] - (g['d'][0] * g['length'] + g['n'][0] * g['e_dn']):.2f} m · "
          f"램프 상단 {g['n'][0] * g['e_up']:.2f} m → 전부 0")
    print(f"    램프 상류변 x (y {sp['ramp_crest']['y0']:.2f}→"
          f"{sp['ramp_crest']['y1']:.2f}) = "
          f"{g['n'][0] * g['e_up']:.3f}→"
          f"{g['n'][0] * g['e_up'] + g['d'][0] * (sp['ramp_crest']['y1'] - (rp['p0'][1] + g['n'][1] * g['e_up'])) / g['d'][1]:.3f}"
          f" vs 슬래브 끝 {sp['ramp_crest']['x1']:.2f} → 사선 잔차 ≤ 0.07 m")
    print(f"    접속 슬래브 종합 → {'OK' if ok_link else 'FAIL'}")

    # ── [GT-81] river-side kerb end ──
    _ce = float(rp["curb_end"])
    _z_ce = rp["curb_h"] - g["grade"] * (g["length"] - _ce)
    _z_ap = te["z_top"] + sp["ramp_foot"]["proud"]
    print(f"  [GT-81 연석 종단] 본체 {g['length'] - _ce:.2f} m + 낮춤 {_ce:.2f} m "
          f"({_z_ce:+.3f} → {_z_ap:+.3f}, 낙차 {_z_ce - _z_ap:.3f}) → "
          f"{'OK (0 높이로 종단)' if abs((_z_ce - _z_ap) - (g['grade'] * _ce + rp['curb_h'] - sp['ramp_foot']['proud'])) < 1e-6 else 'FAIL'}")

    # ── [v7 judgment (11)-1] entry apron footprint check (guards against the brown mass) ──
    #   The old apron sat inside rot_group(yaw), so local coordinates were mistaken for
    #   world and it reached world x +3.06 over the bank. The calculation is kept here.
    # [W3 S17] Pinned to the **historical** yaw 80.7931 deg (length 40). This block is a
    #   record of a past defect, so it must keep reporting the footprint the defective
    #   prim actually had; recomputing it under the current yaw would rewrite history.
    _YAW_HIST = 80.7931
    cy_, sy_ = (math.cos(math.radians(_YAW_HIST)),
                math.sin(math.radians(_YAW_HIST)))
    px0, py0 = rp["p0"]

    def _rot_world(lx, ly):
        vx, vy = lx - px0, ly - py0
        return (px0 + vx * cy_ - vy * sy_, py0 + vx * sy_ + vy * cy_)

    old_pts = [_rot_world(lx, ly) for lx in (-1.4, 0.0)
               for ly in (rp["p0"][1] - g["e_dn"], rp["p0"][1] + 1.2)]
    old_xmax = max(p[0] for p in old_pts)
    ap = rp["apron"]
    print("  [진입 apron 풋프린트 — v7 판정 ⑪-1 갈색 매스]")
    print(f"    구(rot_group 내부, 두께 2.80 · 사적 yaw 80.7931): 월드 꼭짓점 "
          f"{[(round(a, 2), round(b, 2)) for a, b in old_pts]}")
    print(f"      → 월드 x 최대 {old_xmax:+.2f} (사면 상면 "
          f"{slope_z(old_xmax):+.2f}) = 사면 위 "
          f"{-ap['drop'] - slope_z(old_xmax):+.2f} m 돌출 → 갈색 블록의 정체")
    thresh = -g["grade"] * 0.0 - slope_z(g["n"][0] * g["e_up"])
    print(f"    신: 빌드 생략(build={ap['build']}) — 대체 필요 없음. 마루 끝"
          f"(x 0) ~ 램프 상류 시단(x {g['n'][0]*g['e_up']:.2f}) 사이 문턱 "
          f"{thresh:.3f} m < 계단 riser {st['riser']:.2f} → "
          f"{'OK (별도 프림 불요)' if thresh < st['riser'] else 'FAIL'}")
    print(f"      프레임 갈색 매스 잔존 가능 프림: "
          f"{'없음 → OK' if not ap['build'] else 'Apron 재빌드됨 → 확인 요'}")

    # ── [v6 judgment (c)] far-bank apartment variation check ──
    fb2 = PARAMS["far_buildings"]
    print("  [건너편 아파트 4동 — 격자/동일 인상 해소]")
    prev_y1 = None
    for key, bd in fb2.items():
        gap = "" if prev_y1 is None else f"이격 {bd['y0'] - prev_y1:5.1f}"
        print(f"    {key}: x0 {bd['x0']:5.1f} · 폭 {bd['y1'] - bd['y0']:5.1f} · "
              f"h {bd['h']:5.1f} ({bd['floors']:2d}층, 층고 "
              f"{bd['h'] / bd['floors']:.2f}) {gap}")
        prev_y1 = bd["y1"]
    xs = sorted(set(round(b["x0"], 2) for b in fb2.values()))
    gaps = [round(list(fb2.values())[i + 1]["y0"] - list(fb2.values())[i]["y1"], 1)
            for i in range(len(fb2) - 1)]
    fbk = PARAMS["far_bank"]
    inside = all(fbk["x0"] <= b["x0"] and b["x1"] <= fbk["x1"]
                 for b in fb2.values())
    print(f"    후퇴(x0) {len(xs)}종 {xs} · 이격 {gaps} (동일값 반복 없음: "
          f"{len(set(gaps)) == len(gaps)}) · far_bank "
          f"[{fbk['x0']:.0f},{fbk['x1']:.0f}] 내 {inside}")

    # ── [v6 judgment (b)] silver-grass clump check ──
    rd = PARAMS["reed"]
    tot_stalk = sum(int(round((r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
                              * rd["density"])) for r in PARAMS["reeds"])
    fh = PARAMS["far_hedge"]
    import random as _rnd_chk
    n_far, gaps_far = 0, []
    for i in range(len(PARAMS["far_hedges"])):
        for ri, (dx, sk, phase) in enumerate(fh["rows"]):
            r_ = _rnd_chk.Random((i + 1) * 26417 ^ (ri + 1) * 6151)
            yy, prev = fh["spacing"] * phase, None
            while yy <= fh["length"]:
                r_.uniform(0.70, 1.25), r_.uniform(0.60, 1.45)
                r_.uniform(-0.30, 0.30), r_.uniform(0.8, 1.4)
                if prev is not None:
                    gaps_far.append(round(yy - prev, 2))
                prev = yy
                yy += fh["spacing"] * r_.uniform(0.55, 1.60)
                n_far += 1
    print(f"  [억새 군락] 근경 {len(PARAMS['reeds'])}밴드 · 밀도 "
          f"{rd['density']:.1f} 본/m² → 대 {tot_stalk}본 "
          f"(r {rd['r']:.3f} · h {rd['h_lo']:.2f}~{rd['h_hi']:.2f}× · "
          f"기울기 {rd['tilt']:.0f}°)")
    print(f"    [v7 판정 ⑪-2] 건너편 억새: {len(PARAMS['far_hedges'])}띠 × "
          f"{len(fh['rows'])}열(dx {[r[0] for r in fh['rows']]}) → 블롭 {n_far}개 · "
          f"간격 {min(gaps_far):.2f}~{max(gaps_far):.2f} m "
          f"(구: 1열 등간격 {fh['spacing']:.2f} 고정) → "
          f"{'OK (등간격 소멸)' if len(set(gaps_far)) > len(gaps_far) * 0.5 else 'FAIL'}")

    # ── z ladder plate table ──
    lv = PARAMS["levee"]
    fb = PARAMS["far_bank"]
    plates = [
        ("Levee(grass)", lv["x0"], lv["x1"], lv["y0"], lv["y1"], lv["z_top"]),
        ("CrownWalk(paving)", PARAMS["crown_walk"]["x0"],
         PARAMS["crown_walk"]["x1"], lv["y0"], lv["y1"],
         lv["z_top"] + PARAMS["crown_walk"]["proud"]),
        ("CrownBike(asphalt)", PARAMS["crown_bike"]["x0"],
         PARAMS["crown_bike"]["x1"], lv["y0"], lv["y1"],
         lv["z_top"] + PARAMS["crown_bike"]["proud"]),
        ("Slope(grass)", 0.0, tot_run, sl["y0"], sl["y1"], -1.6),
        ("Terrace(grass)", te["x0"], te["x1"], te["y0"], te["y1"],
         te["z_top"]),
        ("Promenade(asphalt)", PARAMS["promenade"]["x0"],
         PARAMS["promenade"]["x1"], te["y0"], te["y1"],
         te["z_top"] + PARAMS["promenade"]["proud"]),
        ("Bank(rock)", PARAMS["bank"]["x0"],
         PARAMS["bank"]["x0"] + PARAMS["bank"]["run"], te["y0"], te["y1"],
         te["z_top"] - PARAMS["bank"]["drop"]),
        ("Water(river)", wt["x0"], wt["x1"], wt["y0"], wt["y1"], wt["z"]),
        ("FarBank(grass)", fb["x0"], fb["x1"], fb["y0"], fb["y1"],
         fb["z_top"]),
    ]
    print("  [지면·수면 플레이트 표] (물가 위계: 둔치 −3.20 > 수면 −3.42)")
    print(f"    {'이름':22s} {'x범위':>16s} {'y범위':>16s}  상면z")
    for nm, x0, x1, y0, y1, z in plates:
        print(f"    {nm:22s} [{x0:6.1f},{x1:6.1f}] [{y0:6.1f},{y1:6.1f}]  "
              f"{z:+.3f}")
    offenders = [nm for nm, x0, x1, y0, y1, z in plates
                 if nm not in ("Water(river)", "Bank(rock)")
                 and not (x1 <= wt["x0"] or x0 >= wt["x1"]) and z < wt["z"]]
    print(f"    수면({wt['z']:+.2f}) 와 x겹침 중 더 낮은 지면: "
          f"{offenders if offenders else '없음 → OK'}")
    print(f"    호안: 둔치 {te['z_top']:+.2f} → 사석 사면 "
          f"{te['z_top'] - PARAMS['bank']['drop']:+.2f} (수면 {wt['z']:+.2f} "
          f"아래로 잠김) → "
          f"{'OK' if te['z_top'] - PARAMS['bank']['drop'] < wt['z'] else 'FAIL'}")

    # ── grazing concealment check ──
    print("  [h0.3/h0.9 grazing 은닉 검산] 마루 어깨(x=0,z=0) 스치는 시선")
    for h in (0.3, 0.9):
        for d in (2.0, 5.0, 10.0):
            k = h / d                                   # sight-line descent slope
            x_hit = te["z_top"] / -k                    # x where it meets the terrace (-3.2)
            hid = x_hit > tot_run
            print(f"    h{h:.1f} d{d:4.1f} → 시선이 −3.20 에 닿는 x = "
                  f"{x_hit:6.1f} vs 사면 끝 {tot_run:.1f} → "
                  f"{'사면·계단 전부 은닉 OK' if hid else '사면 일부 노출'}")
    print("    ⇒ 은닉 컷에서는 둔치 원측만 지평으로 남아 근측 잔디와 "
          "연속 평면으로 읽힌다(negative obstacle 성립).")

    # ── [W3 S17] R-1 — hazard / drop registry, re-derived from PARAMS ──
    reg = hazard_registry()
    drops = [r for r in reg if r["kind"] == "drop"]
    ups = [r for r in reg if r["kind"] == "up_step"]
    grades = [r for r in reg if r["kind"] == "grade"]
    print(f"  [R-1 위험/낙차 레지스트리] drop {len(drops)} · up_step {len(ups)} · "
          f"grade {len(grades)}  (GT-27 full re-cache 의 R-1)")
    for r in reg:
        if r["tag"].startswith("stair_nosing_") and r["tag"] != "stair_nosing_01":
            continue
        y = r["y"]
        ys = (f"[{y[0]:6.2f},{y[1]:6.2f}]" if isinstance(y, tuple)
              else f"{y:13.2f}")
        print(f"    {r['tag']:18s} {r['kind']:8s} x{r['x']:6.2f} y{ys} "
              f"z_top{r['z_top']:+7.3f} 낙차 {r['fall']:5.3f}  {r['note']}")
    print(f"    · stair_nosing_02..20 은 동일 규칙(riser {PARAMS['stairs']['riser']:.3f}) "
          f"으로 생략 · 총 낙차 "
          f"{PARAMS['stairs']['nsteps'] * PARAMS['stairs']['riser']:.2f}")
    print(f"    · up_step 은 drop 이 아니다(GT-1 규칙): cope {ups[0]['fall']:.3f} m 는 "
          f"마루 끝 돋움이지 낙차가 아니다 → "
          f"{'OK' if all(u['kind'] == 'up_step' for u in ups) else 'FAIL'}")
    print(f"    · 램프는 grade 행이다 — 가장자리 없이 내려간다 → "
          f"{'OK' if grades and grades[0]['kind'] == 'grade' else 'FAIL'}")
    print(f"    · 계단 낙차 시단 x {PARAMS['stairs']['x0']:.2f} · GT drop edge 불변 → "
          f"{'OK' if abs(PARAMS['stairs']['x0']) < 1e-9 else 'FAIL'}")

    # ── [W3 S17 · F5] manhole derivation (G-4 / KDS 61 40 00) ──
    mh = derived_manholes()
    gr = PARAMS["gkit"]["region"]
    mh_in = [m for m in mh
             if gr[0] <= m["x"] <= gr[2] and gr[1] <= m["y"] <= gr[3]]
    u = PARAMS["utility"]
    llen = sum(math.dist(u["line"][i], u["line"][i + 1])
               for i in range(len(u["line"]) - 1))
    print(f"  [F5 맨홀 유도] 관로 Ø{u['d_mm']:.0f} · {u['kind']} · 연장 {llen:.1f} m "
          f"→ KDS 최대 간격 {ik.MANHOLE_INTERVAL_KDS[0][1]:.0f} m")
    for m in mh:
        print(f"    ({m['x']:6.2f}, {m['y']:6.2f}) s={m['s']:5.1f} {m['reason']}")
    print(f"    지반 플랜 영역 {tuple(gr)} 내 맨홀 {len(mh_in)}개 → "
          f"{'OK (tonglam FIX-5: 카메라 해 (−2.00,1.20) 폐기)' if not mh_in else '확인 요'}")

    # ── [W3 S17] R17-1 (ii) acceptance — projected ramp/stair area ──
    print("  [R17-1(ii) 수용 검사] 투영 면적비 (hFOV 60 · vFOV 36 · 1920×1080, "
          "카메라 무편집)")
    for vn, sfrac, rfrac, ratio, vis in _frame_metric():
        print(f"    {vn:17s} 계단 {sfrac * 100:6.3f}% · 램프 {rfrac * 100:6.3f}% · "
              f"램프/계단 {ratio:6.2f} · 램프 프레임내 {vis:5.1f}%")
    print("    (기준선 L=40: pair_compare 계단 0.468% · 램프 2.265% · 비 4.84 · "
          "램프 plan-Y 39.88 m)")
    print("=" * 74)


# ===========================================================================
# [D] Camera presets
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)
    # pair_compare: stairs (y 0) and diagonal ramp (y 4 -> 43) in one frame — the pair's core.
    #   [v5.1 re-aim] dropping the zigzag lets the ramp run 40 m in +Y -> re-aimed as a
    #   high south-west overhead. Check (eye −20,−13,15): stair centre off-axis 14.6 deg,
    #   ramp s=20 13.8 deg, ramp end 21.1 deg (all within hFOV 30 deg); depression is
    #   32.0 deg at the stairs · 16.3 deg at the end, inside camera pitch 24.6 +-17.5 deg.
    views["pair_compare"] = dict(eye=[-20.0, -13.0, 15.0], tgt=[7.0, 13.0, -2.2])
    # levee_walk: along the levee path (+Y) — grazing view where bank, stairs, terrace vanish
    views["levee_walk"] = dict(eye=[-1.5, -14.0, 1.50], tgt=[-1.3, 6.0, 0.90])
    # ramp_run: along the diagonal ramp (eye height above the deck)
    views["ramp_run"] = dict(eye=[2.15, 5.68, 1.39], tgt=[5.35, 25.40, -1.50])
    # across_river: from the levee path over stairs, terrace, river and far skyline
    views["across_river"] = dict(eye=[-4.0, 0.5, 1.60], tgt=[22.0, 2.0, -2.60])
    # toe_lookup: looking up the bank and stairs from the terrace (proves the stairs exist)
    views["toe_lookup"] = dict(eye=[14.0, -6.0, -1.60], tgt=[3.5, -0.3, -1.20])
    return views


# ===========================================================================
# [E] Main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. pair_compare  — 같은 낙차의 계단(50%) vs 사선 램프(8%)가 한 화면에 대비되는가
 2. levee_walk·h0.3 — 둑길 grazing 에서 사면·계단·둔치가 소실되는가(특색)
 3. ramp_run      — 사선 단일로가 사면을 비스듬히 가로지르는가(지그재그 폐기)
 4. toe_lookup    — 사면 잔디 곡률(어깨 라운딩)·계단 절개면이 자연스러운가
 5. across_river  — 산책로·억새·호안·수면·건너편 아파트/교량 지평
 6. 접합          — 마루/사면/둔치/호안/수면 경계에 부유·틈·Z파이팅 없는가
 7. [v6] 융화     — 램프 성토가 잔디 배터로 사면에 녹아드는가(갈색 블록 소멸),
                    억새가 박스가 아니라 대(stalk) 군락으로 보이는가,
                    건너편 아파트가 격자 반복이 아닌가
 8. [v7] 갈색 매스 — levee_walk 우중앙에 **평평한 상면 + 수직면 갈색 블록**이
                    완전히 사라졌는가(정체 = 구 Ramp/Apron, 빌드 제거).
                    남는 램프 노면·연석·계단이 갈색이 아니라 **중성 회색
                    콘크리트**인가(conc_tint 채널 등화).
 9. [v7] 배터·억새 — 강측 배터가 '계단 3단'이 아니라 연속 사면으로 읽히는가
                    (9단 × 0.14 m), 건너편 억새가 등간격 구슬열이 아니라
                    3열 엇갈림 군락으로 읽히는가
10. [GT-81] 이격 — levee_walk 에서 **도로 / 3.0 m 잔디 verge / 마루 코프 / 사면**
                    이 네 켜로 읽히는가(도로가 낙차선에 붙어 있지 않은가)
11. [GT-81] 접속 — pair_compare·ramp_run 에서 램프·계단이 **잔디에서 끝나지 않는가**:
                    상단은 자전거도로까지, 하단은 산책로 x11.5 까지 포장이 이어지는가
12. [GT-81] 두부 — levee_walk 우측 램프 시단의 **평평한 상면 + 수직 절단면 + 빗살
                    무늬 배터 끝**이 사라지고 잔디 코가 사면으로 잠기는가
13. [GT-81] 마감 — 강측 연석이 산책로 앞에서 0 높이로 낮아지는가, 트렌치가 양 끝
                    우수받이에 물리는가(흰 금속 띠가 아니라 어두운 주철인가),
                    보도 마모대가 보도 재질로 전 구간 연속인가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene17")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene17"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # Materials (including tint-jitter variants)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["conc"] = PBR(
            f"{ROOT}/Looks/Concrete", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["conc_tint"])
        M["paving"] = PBR(
            f"{ROOT}/Looks/Paving", sc.tex_path("paving_interlock", "diff"),
            sc.tex_path("paving_interlock", "nor"),
            sc.tex_path("paving_interlock", "rough"),
            sca["paving_interlock"], tint=mp["paving_tint"])
        # [GT-81] same texture and tile size as `paving`, tint only — so the wear
        #   lane reads as trodden footway, not as a slab of another material.
        M["paving_worn"] = PBR(
            f"{ROOT}/Looks/PavingWorn", sc.tex_path("paving_interlock", "diff"),
            sc.tex_path("paving_interlock", "nor"),
            sc.tex_path("paving_interlock", "rough"),
            sca["paving_interlock"], tint=mp["paving_worn_tint"])
        # [W2 fix batch F4, iteration 1] The turf materials are renamed into the
        #   **soil** look class. `LOOK_CLASS["veg"]` is `mdl="omni"`, so every grass
        #   plane took the plain OmniPBR branch and none of the MDL de-tiling ran:
        #   no `unit_cell` albedo jitter, no `patch_mix` rotation, no `macro_amp`, no
        #   `tri_dither`. A 4096 px source world-projected at one tile size onto a
        #   24x78 m plane therefore repeats on an exact grid - which is the "billiard
        #   leaf-print carpet" read, and it is a *repetition* defect that tint jitter
        #   alone cannot touch. `TurfSoil*` classifies as soil (mdl="ground",
        #   patch=1.0), so the same grass texture now goes through NegObsGround with
        #   patch rotation and macro modulation. Only this scene is renamed.
        M["grass"] = PBR(
            f"{ROOT}/Looks/TurfSoil", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["grass_b"] = PBR(
            f"{ROOT}/Looks/TurfSoilB", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint_b"])
        M["grass_c"] = PBR(
            f"{ROOT}/Looks/TurfSoilC", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            float(mp["grass_scale_c"]), tint=mp["grass_tint_c"])
        M["grass_d"] = PBR(
            f"{ROOT}/Looks/TurfSoilD", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            float(mp["grass_scale_d"]), tint=mp["grass_tint_d"])
        M["rock"] = PBR(
            f"{ROOT}/Looks/Rock", sc.tex_path("rock_wall", "diff"),
            sc.tex_path("rock_wall", "nor"), sc.tex_path("rock_wall", "rough"),
            sca["rock_wall"], tint=mp["rock_tint"])
        # [W2-D · spec §5.9 17 (1)] Constant colour -> **real PBR**. The asphalt
        #   texture set has been in `assets/scene01` all along and this scene
        #   simply never bound it, which is why the worst frame of the whole
        #   batch (d2 flat 99.78 %) was flat: a constant-colour road has no
        #   spatial frequency at all at grazing angle. `scale=3.0` = 3 m of
        #   texture per tile (§5.9 "3.0 m PBR").
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           sc.tex_path("asphalt", "diff"),
                           sc.tex_path("asphalt", "nor"),
                           sc.tex_path("asphalt", "rough"),
                           sca["asphalt"], tint=mp["asphalt_tint"])
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"])
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"])
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = PBR(f"{ROOT}/Looks/GKitIron",
                            diffuse_color=(0.10, 0.10, 0.105),
                            metallic=0.55, roughness_const=0.55)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["shell"] = PBR(f"{ROOT}/Looks/Shell",
                         sc.tex_path("concrete_floor", "diff"),
                         sc.tex_path("concrete_floor", "nor"),
                         sc.tex_path("concrete_floor", "rough"),
                         sca["concrete_floor"], tint=mp["shell_tint"])
        M["shell_b"] = PBR(f"{ROOT}/Looks/ShellB",
                           sc.tex_path("concrete_floor", "diff"),
                           sc.tex_path("concrete_floor", "nor"),
                           sc.tex_path("concrete_floor", "rough"),
                           sca["concrete_floor"], tint=mp["shell_tint_b"])
        for tag in ("c", "d"):
            M[f"shell_{tag}"] = PBR(
                f"{ROOT}/Looks/Shell{tag.upper()}",
                sc.tex_path("concrete_floor", "diff"),
                sc.tex_path("concrete_floor", "nor"),
                sc.tex_path("concrete_floor", "rough"),
                sca["concrete_floor"], tint=mp[f"shell_tint_{tag}"])
        M["reed"] = PBR(f"{ROOT}/Looks/Reed", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"),
                        sc.tex_path("grass", "rough"),
                        0.6, tint=PARAMS["reed_tint"])
        M["bridge"] = PBR(f"{ROOT}/Looks/Bridge",
                          diffuse_color=mp["bridge_color"],
                          roughness_const=mp["bridge_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        return M

    # -------------------------------------------------------------------
    # Levee crest (levee path) — fill body + sidewalk/bike-road bands + crest kerb
    # -------------------------------------------------------------------
    def build_levee(M):
        lv = PARAMS["levee"]
        cy = (lv["y0"] + lv["y1"]) / 2.0
        Ly = lv["y1"] - lv["y0"]
        BOX(f"{ROOT}/Levee",
            ((lv["x0"] + lv["x1"]) / 2.0, cy, lv["z_top"] - lv["thick"] / 2.0),
            (lv["x1"] - lv["x0"], Ly, lv["thick"]), M["grass"], col=True)
        for key, mtl in (("crown_walk", M["paving"]),
                         ("crown_bike", M["asphalt"])):
            b = PARAMS[key]
            z_hi = lv["z_top"] + b["proud"]
            z_lo = lv["z_top"] - b["embed"]
            # [W2-0 · P-A] The two hard crown bands are the ground_kit stage.
            sc.skin_exclude(f"{ROOT}/{key.split('_')[1].capitalize()}Band")
            BOX(f"{ROOT}/{key.split('_')[1].capitalize()}Band",
                ((b["x0"] + b["x1"]) / 2.0, cy, (z_hi + z_lo) / 2.0),
                (b["x1"] - b["x0"], Ly, z_hi - z_lo), mtl, col=True)
        # [W2-D §5.9 (2)] 0.5 m planting strip — between sidewalk and bike road. Its top
        #   sits at z=0, 6 mm below the two paved tops (+0.006), so it reads as a planting bed.
        gb = PARAMS["crown_green"]
        BOX(f"{ROOT}/GreenStrip",
            ((gb["x0"] + gb["x1"]) / 2.0, cy,
             (gb["top"] + lv["z_top"] - gb["embed"]) / 2.0),
            (gb["x1"] - gb["x0"], Ly, gb["top"] - lv["z_top"] + gb["embed"]),
            M["grass_b"], col=True)
        # bike road centre dashed line
        cl = PARAMS["crown_line"]
        step = cl["seg"] + cl["gap"]
        n = int(Ly / step)
        for i in range(n):
            yy = lv["y0"] + 1.0 + i * step + cl["seg"] / 2.0
            if yy > lv["y1"] - 1.0:
                break
            BOX(f"{ROOT}/CrownLine_{i}", (cl["x"], yy, cl["z"] - 0.01),
                (cl["w"], cl["seg"], 0.02), M["paint"])
        # Crest-end kerb — left open at the stair gap and the ramp apron
        cp = PARAMS["cope"]
        for i, (y0, y1) in enumerate(cp["y_segs"]):
            BOX(f"{ROOT}/Cope_{i}",
                ((cp["x0"] + cp["x1"]) / 2.0, (y0 + y1) / 2.0,
                 cp["h"] / 2.0 - 0.10),
                (cp["x1"] - cp["x0"], y1 - y0, cp["h"] + 0.20), M["conc"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P13 levee_paved (spec §5.9 scene17 row)
    #   Drop edge = levee crest x=0 (PARAMS["stairs"]["x0"], §7.4).
    #   The crown hard surface sits at z = levee.z_top + crown_bike.proud, so
    #   the plan is laid on that plane, not on z=0.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        lv = PARAMS["levee"]
        z_crown = float(lv["z_top"]) + float(PARAMS["crown_bike"]["proud"])
        # [W3 S17 · F5] Derive, do not site. Returns the chambers the declared Ø450
        #   storm main actually needs (KDS 61 40 00); keep only those inside the ground
        #   plan region. The build count is whatever this returns — measured 0.
        mh = derived_manholes()
        gr = tuple(g["region"])
        mh_in = [(m["x"], m["y"]) for m in mh
                 if gr[0] <= m["x"] <= gr[2] and gr[1] <= m["y"] <= gr[3]]
        print(f"[S17·F5] 관로 유도 맨홀 {len(mh)}개 "
              f"{[(round(m['x'], 2), round(m['y'], 2), m['reason']) for m in mh]} "
              f"→ 지반 플랜 영역 내 {len(mh_in)}개 (구: 카메라 해 (−2.00, 1.20) 1개)")
        gp = gk.plan_ground(
            "levee_paved", region=gr, z=z_crown, gy=0.0,
            origin=(0.0, 0.0, 0.0),
            edges=[("levee_crest", float(PARAMS["stairs"]["x0"]))],
            dists=(2, 5, 10), scene="scene17", tactile=(),
            # §12.4 — 17 is OFF: p = 0.24 (park/riverside), below the 0.50 bar.
            overrides=dict(infra=dict(manhole=len(mh_in), gully=2, gutter_L=0,
                                      trench=1)),
            extras_args=dict(wear_lane=dict(centerline=tuple(g["wear_lane"]),
                                            width=0.90)),
            sites=dict(manhole=mh_in,
                       gully=[tuple(v) for v in g["gullies"]],
                       trench=[tuple(g["trench"])]),
            seed=17)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["conc"], crack=M["conc"], patch=M["asphalt"],
                  patch_cut=M["conc"], manhole=M["gk_iron"], gully=M["gk_iron"],
                  gutter=M["conc"], gutter_cover=M["conc"],
                  # [GT-81] the trench was the brightest prim on the crown. Its
                  #   elements declare albedo 0.10 (frame) / 0.09 (cover), but the
                  #   scene bound them to `rail` — a 0.66 stainless constant — so a
                  #   grating that should read as dark cast iron rendered as a white
                  #   strip lying on the asphalt. Same defect and same fix as the
                  #   W2-F5 manhole/gully covers, which already use `gk_iron` (0.10).
                  trench=M["gk_iron"], trench_frame=M["gk_iron"],
                  marking=M["paint"], weed=M["grass_b"], wear=M["paving_worn"],
                  stain_dirt=M["conc"], stain_water=M["conc"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene17 P13 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Grass bank — 7 segments x 2 Y bands (stair width left open). Segments overlap by margin.
    # -------------------------------------------------------------------
    def build_slope_faces(M):
        sl = PARAMS["slope"]
        st = PARAMS["stairs"]
        nodes = slope_nodes()
        bands = (("S", sl["y0"], st["y0"]), ("N", st["y1"], sl["y1"]))
        for i, (run, drop) in enumerate(sl["segs"]):
            x0, z0 = nodes[i]
            mg = 0.0 if i == 0 else sl["margin"]
            for tag, y0, y1 in bands:
                sc.build_slope(
                    stage, f"{ROOT}/Slope_{i}_{tag}", x0, z0, run, drop,
                    y0, y1, sl["thick"],
                    (M["grass"], M["grass_c"], M["grass_b"])[i % 3],
                    margin=mg, collider=True)

    # -------------------------------------------------------------------
    # 20 stair steps — straight through the bank (no railing)
    # -------------------------------------------------------------------
    def build_stairs(M, stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    # -------------------------------------------------------------------
    # Diagonal ramp — one build_slope inside rot_group(yaw) + fill (revetment) + kerb
    #   Local convention: +X = travel (descending), +Y = uphill side (= −n). Local y = p0y − e.
    # -------------------------------------------------------------------
    def build_ramp(M, ramp_mtl):
        rp = PARAMS["ramp"]
        g = ramp_geom()
        px, py = rp["p0"]
        grp = sc.build_rot_group(stage, f"{ROOT}/Ramp", (px, py), g["yaw"])
        L, drop = g["length"], g["drop"]
        y_up = py - g["e_up"]                       # uphill edge (larger local y)
        y_dn = py - g["e_dn"]                       # river-side edge
        # (1) fill — from the deck underside downward, projecting fill_out riverward.
        #   [v6 judgment (a)] material M["rock"] (revetment) -> M["grass_b"] (as the bank grass).
        #   Removes the cause of the brown revetment reading as a foreign concrete block.
        sc.build_slope(stage, f"{grp}/Fill", px, -rp["deck_t"], L, drop,
                       y_dn - rp["fill_out"], y_up, rp["fill_t"], M["grass_b"],
                       margin=0.0, collider=True)
        # (1)-b [v6 judgment (a)] river-side grass batter — breaks the vertical cut into
        #   stepped grass-fill shoulders. Step k retreats w riverward and drops dz.
        #   9 steps (total drop 1.26) cover the 1.18 m maximum exposure under the deck.
        #   [v7 judgment (11)-1 (a)] the old 3 steps (0.42 each) read as **artificial stairs**
        #   at 17 m -> total width and drop (1.50 x 1.26) are kept but split into 9 steps,
        #   lowering step height to 0.14 (advised <=0.15). The old build also alternated
        #   grass/grass_b, making **the step boundaries stripe**, so it now uses the same
        #   **single grass_b material as the fill body (`Fill`)** and reads as a terrain fold.
        #   margin stretches top and bottom slightly to close the joint with the fill.
        bt = rp["batter"]
        for k in range(int(bt["n"])):
            y_hi = y_dn - rp["fill_out"] - bt["w"] * k
            sc.build_slope(stage, f"{grp}/Batter_{k}", px,
                           -rp["deck_t"] - bt["dz"] * (k + 1), L, drop,
                           y_hi - bt["w"], y_hi, rp["fill_t"],
                           M["grass_b"],
                           margin=bt["margin"], collider=True)
        # (1)-c [GT-81] head return — the mirror of the batter, run upstream.
        #   Local +X of `grp_h` is −d (upstream) and local +Y is +n (riverward),
        #   so one `build_slope` per longitudinal band gives that band a nose that
        #   starts at its own top and falls at the batter's grade until the bank
        #   surface swallows it. Without this the embankment is truncated flat at
        #   s=0 and shows 0.15…1.37 m of vertical face plus nine strip ends.
        hd = rp["head"]
        k_ret = float(bt["dz"]) / float(bt["w"])       # 1:1.19, the batter's own grade
        grp_h = sc.build_rot_group(stage, f"{ROOT}/RampHead", (px, py),
                                   g["yaw"] + 180.0)
        e_fill_hi = g["e_dn"] + rp["fill_out"]
        _noses = [(float(hd["run0"]), -rp["deck_t"],
                   py + g["e_up"], py + e_fill_hi)]
        for k in range(int(bt["n"])):
            _noses.append((float(hd["run0"]) - float(hd["run_step"]) * (k + 1),
                           -rp["deck_t"] - bt["dz"] * (k + 1),
                           py + e_fill_hi + bt["w"] * k,
                           py + e_fill_hi + bt["w"] * (k + 1)))
        for j, (run_j, z0_j, ya, yb) in enumerate(_noses):
            sc.build_slope(stage, f"{grp_h}/Nose_{j}", px, z0_j, run_j,
                           k_ret * run_j, ya, yb, rp["fill_t"], M["grass_b"],
                           margin=float(hd["margin"]), collider=True)
        # (2) deck (concrete paving)
        sc.build_slope(stage, f"{grp}/Deck", px, 0.0, L, drop, y_dn, y_up,
                       rp["deck_t"], ramp_mtl, margin=0.0, collider=True)
        # (3) river-side kerb (h0.15) — no railing (a below-code reality)
        #   [GT-81] the run stops `curb_end` short and a dropped-kerb piece takes
        #   the last stretch down to the foot apron's top, so the kerb ends at
        #   zero height on paving instead of as a 0.146 m stub.
        _ce = float(rp["curb_end"])
        _z_ce = rp["curb_h"] - g["grade"] * (L - _ce)          # kerb top where the drop starts
        _z_apron = _TERRACE_Z + PARAMS["spurs"]["ramp_foot"]["proud"]
        sc.build_slope(stage, f"{grp}/Curb", px, rp["curb_h"], L - _ce,
                       drop * (L - _ce) / L,
                       y_dn, y_dn + rp["curb_w"], rp["curb_h"] + 0.35,
                       M["conc"], margin=0.0, collider=True)
        sc.build_slope(stage, f"{grp}/CurbEnd", px + (L - _ce), _z_ce, _ce,
                       _z_ce - _z_apron, y_dn, y_dn + rp["curb_w"],
                       rp["curb_h"] + 0.35, M["conc"], margin=0.05,
                       collider=True)
        # (4) entry apron — [v7 judgment (11)-1] **build skipped** (reason in the note below).
        if PARAMS["ramp"]["apron"]["build"]:
            ap = PARAMS["ramp"]["apron"]
            BOX(f"{ROOT}/RampApron",
                ((ap["x0"] + ap["x1"]) / 2.0, (ap["y0"] + ap["y1"]) / 2.0,
                 -ap["drop"] - ap["t"] / 2.0),
                (ap["x1"] - ap["x0"], ap["y1"] - ap["y0"], ap["t"]),
                ramp_mtl, col=True)
        # ── [v7 judgment (11)-1] why it was removed ────────────────────────────────────
        #  The old apron was a box **inside** rot_group (yaw 80.793 deg) that assumed
        #  "local −X = inland of the crest". Local −X is not world −X but almost world −Y,
        #  so it actually swung over the bank to world x +3.06, where the bank top is
        #  −1.40 — a **2.8 m thick concrete block** standing 1.39 m above it.
        #  This prim is exactly the "brown ramp-fill mass" the v6 and v7 judgments named
        #  (the `Fill` that W-5 fixed was already grass and renders as grass in frame).
        #  It is functionally unnecessary too: the "crest <-> ramp start" step that an
        #  entry landing would fill is already covered by the crest slab (levee x −24…0,
        #  top 0.000, thickness 3.6) and the bike road (x −3…0, top +0.004) out to the crest
        #  end; what remains is a **0.152 m threshold at most** between the crest end (x 0)
        #  and the ramp's uphill start (x 0.59) (smoke [ramp diagonal placement] s0.0 cut
        #  +0.152) — a construction joint below the 0.16 stair riser, so no prim is needed.
        #  PARAMS **remains for history** per the v5.2 rule (scene05 speaker precedent).

    # -------------------------------------------------------------------
    # Terrace + promenade + riprap revetment
    # -------------------------------------------------------------------
    def build_terrace(M):
        te = PARAMS["terrace"]
        pm = PARAMS["promenade"]
        cy = (te["y0"] + te["y1"]) / 2.0
        Ly = te["y1"] - te["y0"]
        BOX(f"{ROOT}/Terrace",
            ((te["x0"] + te["x1"]) / 2.0, cy, te["z_top"] - te["thick"] / 2.0),
            (te["x1"] - te["x0"], Ly, te["thick"]), M["grass_c"], col=True)
        # promenade (parallel to the river = a Y-direction band)
        z_hi = te["z_top"] + pm["proud"]
        BOX(f"{ROOT}/Promenade",
            ((pm["x0"] + pm["x1"]) / 2.0, cy, z_hi - 0.06),
            (pm["x1"] - pm["x0"], Ly, 0.12), M["asphalt"], col=True)
        for tag, xc in (("W", pm["x0"] + pm["line_in"]),
                        ("E", pm["x1"] - pm["line_in"])):
            BOX(f"{ROOT}/PromLine_{tag}", (xc, cy, z_hi + 0.004),
                (pm["line_w"], Ly, 0.02), M["paint"])
        # riprap revetment slope (terrace -> below the waterline)
        bk = PARAMS["bank"]
        sc.build_slope(stage, f"{ROOT}/Bank", bk["x0"], te["z_top"], bk["run"],
                       bk["drop"], te["y0"], te["y1"], bk["thick"], M["rock"],
                       margin=bk["margin"], collider=True)

    # -------------------------------------------------------------------
    # [GT-81] Links — crest road -> both heads, both feet -> riverside promenade
    #   Four slabs, no cleverness: each is a box whose top sits on the z ladder of
    #   the plate it joins (crest +0.006 = the crown plane, terrace +0.004 = the
    #   promenade plane) so nothing is coplanar with the turf underneath it, and
    #   each terminates on a built edge — x=-3.0 is the bike road's riverward
    #   face, x=11.5 is the promenade's landward face, both met edge to edge.
    #   `embed` is sized so the underside stays below the falling ground at the
    #   riverward end (crest links overhang the bank shoulder by up to 0.70 m,
    #   where the bank has already dropped 0.18 m), i.e. no slab floats.
    # -------------------------------------------------------------------
    def build_links(M, hard_mtl):
        sp = PARAMS["spurs"]
        for key, base in (("stair_crest", 0.0), ("ramp_crest", 0.0),
                          ("stair_foot", _TERRACE_Z), ("ramp_foot", _TERRACE_Z)):
            b = sp[key]
            z_hi = base + b["proud"]
            z_lo = base - b["embed"]
            name = "".join(p.capitalize() for p in key.split("_"))
            BOX(f"{ROOT}/Link{name}",
                ((b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0,
                 (z_hi + z_lo) / 2.0),
                (b["x1"] - b["x0"], b["y1"] - b["y0"], z_hi - z_lo),
                hard_mtl, col=True)

    # -------------------------------------------------------------------
    # River + far bank (broad water kept — no meander)
    # -------------------------------------------------------------------
    def build_river(M):
        wt = PARAMS["water"]
        sc.build_water(stage, f"{ROOT}/Water", wt["x0"], wt["y0"], wt["x1"],
                       wt["y1"], wt["z"], mtl=M["water"])
        fb = PARAMS["far_bank"]
        BOX(f"{ROOT}/FarBank",
            ((fb["x0"] + fb["x1"]) / 2.0, (fb["y0"] + fb["y1"]) / 2.0,
             fb["z_top"] - fb["thick"] / 2.0),
            (fb["x1"] - fb["x0"], fb["y1"] - fb["y0"], fb["thick"]),
            M["grass_d"], col=True)
        # [v6 judgment (b) · v7 (11)-2] far-bank silver-grass band — flat ellipsoid clumps.
        #   At 76 m individual stalks are lost, so blobs only break up the silhouette.
        #   The old build was **1 row · evenly divided y + +-0.3 jitter**, so even spacing
        #   survived and it read as a "necklace of equal beads" (§3 violation). Now:
        #     · rows = (dx, size_k, phase), 3 rows — dx sets fore/aft, phase the row offset
        #     · y advances by a **random walk** (spacing x U(0.55,1.60)) -> even spacing gone
        #     · size 0.60~1.45x · height 0.70~1.25x jitter
        #   Grounding: centre z = z_top + hh*0.42, rz = hh*0.60 -> base 0.18hh below grade.
        fh = PARAMS["far_hedge"]
        for i, h in enumerate(PARAMS["far_hedges"]):
            y_lo = h["cy"] - fh["length"] / 2.0
            y_hi = h["cy"] + fh["length"] / 2.0
            for ri, (dx, sk, phase) in enumerate(fh["rows"]):
                rnd = _random.Random((i + 1) * 26417 ^ (ri + 1) * 6151)
                yy = y_lo + fh["spacing"] * phase
                k = 0
                while yy <= y_hi:
                    hh = fh["h"] * sk * rnd.uniform(0.70, 1.25)
                    rr = fh["rad"] * sk * rnd.uniform(0.60, 1.45)
                    sc.add_sphere(stage, f"{ROOT}/FarReed_{i}_{ri}_{k}",
                                  (fh["cx"] + dx + rnd.uniform(-0.30, 0.30),
                                   yy, fb["z_top"] + hh * 0.42),
                                  (fh["sx"] / 2.0 * sk * rnd.uniform(0.8, 1.4),
                                   rr, hh * 0.60),
                                  M["reed"])
                    yy += fh["spacing"] * rnd.uniform(0.55, 1.60)
                    k += 1
        # [W3 S17 · K4(b)/K4-F4] **belt flip.** `SCENE_SPECIES["Scene17"] = ("poplar",
        #   "oak_black")` — 양버들 on the walked levee, 굴참나무-class broadleaf on the far
        #   bank. K4-F4 records that a declared belt is **inert until the scene passes
        #   `species=`/`belt=`**, so until this line every tree in the scene, including
        #   these three at x ~80 m across the water, was drawn as the route poplar. These
        #   are the only three prims in the file that are physically a separate stand.
        #   `bare=` stays default-OFF: G3 pins summer (see the header).
        for i, t in enumerate(PARAMS["far_trees"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", t["cx"], t["cy"],
                          fb["z_top"], M["wood"], M["canopy_a"], M["canopy_b"],
                          belt=True)

    def build_flat_fill(M):
        """hazard_stairs=False control: crest to terrace unified as flat grass at z=0."""
        lv = PARAMS["levee"]
        te = PARAMS["terrace"]
        BOX(f"{ROOT}/FlatFill",
            ((lv["x0"] + te["x1"]) / 2.0, (lv["y0"] + lv["y1"]) / 2.0,
             lv["z_top"] - lv["thick"] / 2.0),
            (te["x1"] - lv["x0"], lv["y1"] - lv["y0"], lv["thick"]),
            M["grass_c"], col=True)

    # -------------------------------------------------------------------
    # Distant dressing — far-bank apartment skyline + bridge (80% of reading it as the Han)
    # -------------------------------------------------------------------
    def build_skyline(M):
        # [v6 judgment (c)] 2 alternating tints -> 4 cycled, so neighbours never repeat a tone.
        tones = (M["shell"], M["shell_c"], M["shell_b"], M["shell_d"])
        for i, (key, bd) in enumerate(PARAMS["far_buildings"].items()):
            sc.build_building(stage, f"{ROOT}/FarBuilding_{key}", bd,
                              tones[i % len(tones)],
                              M["glass"], M["parapet"],
                              window=PARAMS["window"])
        br = PARAMS["bridge"]
        BOX(f"{ROOT}/Bridge/Deck",
            ((br["x0"] + br["x1"]) / 2.0, (br["y0"] + br["y1"]) / 2.0,
             br["deck_top"] - br["deck_t"] / 2.0),
            (br["x1"] - br["x0"], br["y1"] - br["y0"], br["deck_t"]),
            M["bridge"], col=True)
        pier_top = br["deck_top"] - br["deck_t"]
        ph = pier_top - br["pier_base"]
        for i, py in enumerate(br["pier_ys"]):
            CYL(f"{ROOT}/Bridge/Pier_{i}",
                (br["pier_x"], py, br["pier_base"] + ph / 2.0),
                br["pier_r"], ph, M["bridge"], col=True)

    # -------------------------------------------------------------------
    # Near dressing — silver grass · benches · trees · lamps · signposts (irregular)
    # -------------------------------------------------------------------
    def build_dressing(M):
        tz = PARAMS["terrace"]["z_top"]
        # [v6 judgment (b)] silver grass = stalk clumps, scattered inside the band rectangle
        #   at density stalks/m² with a fixed seed (scene09 build_reeds rule). Height/tilt jitter.
        rd = PARAMS["reed"]
        for i, r in enumerate(PARAMS["reeds"]):
            rnd = _random.Random(int(r["seed"]))
            area = (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
            for k in range(int(round(area * rd["density"]))):
                hh = r["h"] * rnd.uniform(rd["h_lo"], rd["h_hi"])
                a = rnd.uniform(0.0, 360.0)
                CYL(f"{ROOT}/Reed_{i}_{k}",
                    (rnd.uniform(r["x0"], r["x1"]),
                     rnd.uniform(r["y0"], r["y1"]), tz + hh / 2.0),
                    rd["r"], hh, M["reed"],
                    rotY=rd["tilt"] * math.cos(math.radians(a)),
                    rotX=rd["tilt"] * math.sin(math.radians(a)))
        for i, (tx, ty) in enumerate(PARAMS["terrace_trees"]):
            sc.build_tree(stage, f"{ROOT}/TerraceTree_{i}", tx, ty, tz,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (tx, ty) in enumerate(PARAMS["crown_trees"]):
            sc.build_tree(stage, f"{ROOT}/CrownTree_{i}", tx, ty, 0.0,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (bx, by, yaw) in enumerate(PARAMS["terrace_benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, tz,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for tag, lights, base in (("T", PARAMS["terrace_lights"], tz),
                                  ("C", PARAMS["crown_lights"], 0.0)):
            for i, (lx, ly) in enumerate(lights):
                pre = f"{ROOT}/Light{tag}_{i}"
                CYL(f"{pre}/Pole", (lx, ly, base + sl["pole_h"] / 2.0),
                    sl["pole_r"], sl["pole_h"], M["post"], col=True)
                CYL(f"{pre}/Arm",
                    (lx + sl["arm_len"] / 2.0, ly,
                     base + sl["pole_h"] - 0.12),
                    sl["arm_r"], sl["arm_len"], M["post"], rotY=90.0)
                BOX(f"{pre}/Head",
                    (lx + sl["arm_len"], ly, base + sl["pole_h"] - 0.17),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        ks = PARAMS["km_sign"]
        CYL(f"{ROOT}/KmSign/Pole", (ks["x"], ks["y"], tz + ks["pole_h"] / 2.0),
            ks["pole_r"], ks["pole_h"], M["post"], col=True)
        BOX(f"{ROOT}/KmSign/Panel", (ks["x"], ks["y"], tz + ks["panel_z"]),
            ks["panel"], M["sign"])

    # -------------------------------------------------------------------
    # Cue — railing / nosing (OFF by default: unrailed is the custom)
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
            sc.build_railing_line(
                stage, f"{ROOT}/Rail", st["y1"] - 0.15, -0.5, st["x0"],
                run, drop, stair_ground, M["rail"], rail_h=0.9)
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"], z_top=st["z_top"])

    # ── Scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hard_mtl = M["conc"] if cfg["cue_material_break"] else M["paving"]

    build_levee(M)
    if cfg["hazard_stairs"]:
        build_slope_faces(M)
        build_stairs(M, hard_mtl)
        build_ramp(M, hard_mtl)
        build_terrace(M)
        build_links(M, hard_mtl)    # [GT-81] after the terrace: the foot links lie on it
        build_cues(M)
    else:
        build_flat_fill(M)
    build_river(M)                  # river and far bank always on (horizon closure)
    if cfg["cue_scene_dressing"]:
        build_skyline(M)            # apartments and bridge stay even in the flat control
        if cfg["hazard_stairs"]:
            build_dressing(M)
    build_ground_kit(M)             # [W2-D] ground elements — after dressing (scatter order rule)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["pair_compare"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene17_{ts}.png")
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
