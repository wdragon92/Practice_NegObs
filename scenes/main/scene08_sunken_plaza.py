# -*- coding: utf-8 -*-
"""
scene08_sunken_plaza.py — NegObs synthetic scene 8 (v7 CURVED): downtown sunken plaza (Isaac Sim 4.5)

Type    : circular sunken plaza (bowl) cut into a city-block plaza. **v7 is a full curved
          rebuild** authorised in `Docs/surveys/w3_intake_v2_images.md` §7-2 (*"scene08 curved
          rebuild — AUTHORIZED IN FULL (bowl, parapet, tiers, paving bands, ring decks per G8)"*)
          against target image **G8** `Docs/reference_photos/Generated Image - Scene08.jpg`.
          Everything that used to be rectangular — the 12 x 9 pit, the straight parapet, the two
          straight flights, the tactile ring, the plaza slab — is gone. Nothing in the scene is
          axis-aligned any more except the CBD backdrop blocks.
Shared  : scene_common.py (K4(d) annular-sector mesh via build_arc_steps(mesh=True) ·
          build_rot_group · build_planter · build_tree/place_shrubs species · build_sign ·
          build_building) · props_kit.py (K4(c) build_glass_balustrade G8 template ·
          build_bench_slat · build_bollard_v2; `build_tube_railing` is NOT called — see
          the R2 note below, GT-85) · infra_kit.py (K5
          build_curb_line — the real 보차도 경계석 the painted lane lines never had) ·
          building_kit.py (BS-4 kind="backdrop" CBD wall) · ground_kit.py (P3 sidewalk_block).

Season  : **late spring / early summer, full leaf** — pinned from G8 (§7-8 season policy). Every
          broadleaf in the frame carries its canopy; there is no `bare=` call anywhere in this
          file and there must not be one until the target image changes. `Rhododendron`'s
          full-bloom flower strip is inert library-wide (K4-F1) — that is the library's state,
          not a scene regression.

Hazard (unchanged in kind, rebuilt in geometry)
  A circular bowl of radius 14.0 m, depth 4.500, is cut into the plaza; its centre is
  C = (14.0, 0.0), so the **near rim sits exactly on the walk axis at x = 0** and the far rim at
  x = 28.0. At robot eye height (h0.3) the bowl is **hidden in principle, entirely**: the sight
  line grazing the near rim (x = 0, z = 0) reaches the bowl floor (−4.500) at
  x = 4.500 * d / 0.3 = 15 * d — 30.0 m at d = 2 m — which is **beyond the far rim at 28.0 m**.
  So at h0.3 the far plaza (r >= 14, z = 0) reads as a plane continuous with the near ground and
  the 4.5 m cavity between them vanishes from the frame (negative obstacle).

  What guards it, and what does not — **S08-B closed as option B-1** (`w3_intake_v2_images.md`
  §2 scene08 (g) R08-2): the pit edge carries a **continuous parapet upstand + structural glass
  balustrade** everywhere except **at the stair head**, and the stair head is the 60 deg cascade
  sector straddling the walk axis. That is the whole of the opening: a grand cascade has no guard
  across its head in any real plaza, because the head *is* the way in. The v6 temporary marking
  (2 banded safety posts + a sagging tape) is **DELETED** — ruling `w3_execution_spec_v1.md` §1.6,
  ledger row **GT-7**; it supersedes `tonglam_v2.md` §1 row 08's PASS and the supersede note
  travels with the commit.

  The **deliberate deviation of v5/v6 survives the rebuild and is the reason B-1 lands where it
  does**: the opening must sit on the grid axis (+X, y = 0), because sealing the approach edge
  with parapet would fill 6 of the 9 h0.3/h0.9 grid shots with parapet wall and make judgment
  impossible (the scene19 d5 blackout precedent). v6 bought that with a *demolished* 1.8 m gap;
  v7 buys it with a **legitimate stair head**, which is what G8 shows.

Goal
  (1) circular bowl — arena floor + curved forecourt, no plane covers the cavity
  (2) **granite cascade** on the walk axis (sector 150..210 deg): 15 + 14 arc-step courses of
      riser 0.150 / tread 0.300 with a 1.20 m mid landing, 30 risers = 4.500 m
  (3) **timber seating tiers** (sector 70..150 deg): 11 courses, riser 0.375 / tread 0.900
  (4) **retail arcade** under a curved ring deck (sector 210..290 deg): shopfront glass at
      r = 17.0, deck edge at r = 14.0, round columns, wood-slat soffit
  (5) **control retaining wall** (sector 290..70 deg) — the far, on-axis edge; the surface the
      h0.3 illusion is actually read against
  (6) curved paving bands (annular) on both levels + a circular granite inlay in the arena
  (7) continuous parapet + glass balustrade over the guarded 220 deg, open over the cascade
  (8) a real **carriageway** with a K5 1 m-unit kerb — the lane markings v6 painted on bare
      ground now have a road under them (S06-B)

Stair compliance (`Docs/reports/stair_compliance_v1.md` — scene08 was that report's **#1**
offender, 2 P0 findings)
  - **L1 계단참**: 4.500 m drop, one direct flight in v6 -> v7 has a 1.20 m mid landing at
    −2.250, so no flight exceeds 2.250 m < 3.0 m. **CLEARED.**
  - **R1 중간난간**: v6 was riser 0.173 on a 4.0 m flight -> **not** exempt. v7 is
    **riser 0.150 AND tread 0.300**, which is exactly 피난방화규칙 §15①3's 단서 -> the cascade is
    **EXEMPT at any width**, which is what lets it be a 14.6 m-wide civic cascade without a
    handrail row standing on the camera axis. The riser value is therefore a *judgment*
    requirement, not a style choice. **CLEARED.**
  - **R2 편측 난간**: both flanks of the cascade carry a raked 4-rail tube guard. **[GT-85]** It
    is built in-scene, not by `props_kit.build_tube_railing`: that kit samples the ground once
    per polyline segment and lays every rail with `rotY=90`, so on a 4.400 m descent it built
    4 LEVEL tubes at the mid-flight height while its posts followed the true stair — rails with
    no post under them at the top, posts finishing 2 m below their rails at the foot, and the
    south run driving through the timber tier bank. The kit's section is kept verbatim (4 rails
    in 1.100 m, 0.120 m bottom offset, clear span 0.279 m); the run is re-laid on the **nosing
    pitch line** (`flank_datum`), carried by posts snapped to tread centres, and terminated at
    both ends by a 0.300 m level handrail extension dying into an end newel that stands wholly
    on flat ground. Same client move as scene06's spiral guard, for the same kit limitation
    (finding S08-F1 / S06-F1).
  - The **timber tiers are seating, not circulation** (riser 0.375) — the scene05 ※ precedent.
    They are reached from the arena floor and from the cascade, and the self-check records them
    as seating so a later compliance sweep does not read them as an illegal stair.

Walk-continuity self-check table (enter -> descend -> arena -> arcade)
  ┌ # section              coordinates (x, y, z)        step / judgment
  │ 0 plaza approach       (−10.00, 0.00,  0.000)       flat (unit paving, ring deck)
  │ 1 cascade head         (  0.00, 0.00,  0.000)       ← **drop 4.500 begins, opening in guard**
  │ 2 course 1 top         (  0.30, 0.00, −0.150)       0.150
  │ 3 course 15 top        (  4.50, 0.00, −2.250)       0.150 x 14
  │ 4 mid landing          (  5.10, 0.00, −2.250)       flat (1.20 m)
  │ 5 course 16 top        (  6.00, 0.00, −2.400)       0.150
  │ 6 course 29 top        (  9.90, 0.00, −4.350)       0.150 x 13
  │ 7 arena floor          ( 10.40, 0.00, −4.500)       0.150 (30th riser)
  │ 8 arena centre         ( 14.00, 0.00, −4.500)       flat (circular granite inlay)
  │ 9 forecourt            ( 20.00,−8.00, −4.500)       flat (curved paving bands)
  └10 arcade walk          ( 24.00,−9.50, −4.500)       flat (under the ring deck)
  * radial distances are measured from C = (14.0, 0.0); the table walks the a = 180 deg ray and
    the smoke run re-derives it at 5 cm resolution rather than trusting it.

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene08_sunken_plaza.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene08_sunken_plaza.py
Smoke (pre-boot geometry·lighting·camera self-check·early exit):
    NEGOBS_SMOKE=1 python scene08_sunken_plaza.py

Coordinates: Z-up, m, travel axis +X, walk centreline y = 0. Bowl centre C = (14.0, 0.0),
  rim radius 14.0, plaza top z = 0, bowl floor z = −4.500. **Drop start edge x = 0 (unchanged
  from v6 — the near rim did not move, which is why the near-window arithmetic re-derives to the
  same three windows; see PARAMS["gkit"]).**
  Sun: SUN_AZ_OFFSET = 60 (raking) -> rays travel from above +Y toward −Y, so the bowl's south
  half (the arcade side) takes direct sun and the north half (the timber tiers) stays dark —
  re-verified numerically against the circular plan in the smoke run.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk
import infra_kit as ik
import props_kit as pk
import building_kit as bk
import facade_kit as fk


# ===========================================================================
# [A] SCENE_CONFIG - 7 keys. Only hazard_stairs toggles the hazard geometry (bowl <-> flat).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> bowl/cascade/tiers/arcade become z=0 flat ground
    "cue_railing":        True,    # parapet upstand + glass balustrade over the guarded arc,
                                   #   cascade flank tube railings. The cascade head is ALWAYS open
    "cue_tactile":        False,   # [v5.2 user] tactile paving is rare in reality - default OFF.
                                   #   v7 rebuilds it as a curved stair-head warning arc
                                   #   (R16-2 stair-cue-first); the v6 rectangular ring with 2
                                   #   deliberately missing tiles is deleted with its rectangle
    "cue_material_break": True,    # plaza unit paving vs cascade granite / tier timber contrast
    "cue_sign":           True,    # [v5.2 user] arbitrary warning signs removed - facility sign only
    "cue_scene_dressing": True,    # planting beds·street trees·benches·street lights·bollards·CBD wall
    "cue_nosing":         False,   # True -> anti-slip strip on the cascade nosing
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
# --- the numbers everything else is derived from ---------------------------
_CX, _CY = 14.0, 0.0               # bowl centre. CX = R_RIM puts the near rim on x = 0
_R_RIM = 14.0                      # bowl rim radius -> far rim at x = 28.0
_RISER = 0.150                     # cascade riser. 0.150 is NOT cosmetic: it is the exact
                                   #   피난방화규칙 §15①3 단서 threshold that exempts the cascade
                                   #   from an intermediate handrail row (see the module docstring)
_NRISER = 30                       # total riser count -> drop 30 x 0.150 = 4.500
_FLOOR_Z = -round(_RISER * _NRISER, 4)          # -4.500

_TREAD = 0.300                     # cascade tread (>= 0.300 = the other half of the 단서)
_LAND = 1.20                       # mid landing radial depth (>= 1.20 m, 피난방화규칙 §15①1)
_NBUILT = _NRISER - 1              # 29 built courses; the 30th riser is the arena floor itself
                                   #   (building it would put the last top coplanar with the floor)
_R_ARENA = round(_R_RIM - (_NBUILT * _TREAD + _LAND), 4)      # 4.10

_TIER_RISER = 0.375                # timber seating tiers - seating, not circulation
_TIER_TREAD = 0.900
_NTIER = 11                        # 11 built courses; the 12th riser is the arena floor
#   11 * 0.900 = 9.900 = R_RIM - R_ARENA  -> the tier bank and the cascade land on the same floor
#   12 * 0.375 = 4.500 = the bowl depth   -> and reach it over the same 9.900 m of radius

PARAMS = dict(
    # --- the bowl -----------------------------------------------------------
    bowl=dict(cx=_CX, cy=_CY, r_rim=_R_RIM, r_arena=_R_ARENA, floor_z=_FLOOR_Z,
              floor_thick=0.60, bank_base=-4.90),
    # --- angular sectors (deg, 0 = +X, CCW, about C) ------------------------
    #  Placement is NOT decorative. Every sector boundary is set by the h0.3 frame:
    #  the default viewport is 60 deg horizontal (18.147 mm focal / 20.955 mm aperture), so the
    #  half-FOV is 30 deg, and any bowl feature whose lateral bearing from the d=2 eye exceeds
    #  ~30 deg cannot appear in a judged near cut. The smoke run PRINTS the measured bearings
    #  (`[사분면 프레임 검산]`) and gates on them rather than trusting this comment.
    #    cascade  150..210  straddles the walk axis  -> the opening, and the descent
    #    tier      90..150  north  -> every stepped course is EITHER below the h0.3 graze cone
    #                                 OR outside the 30 deg half-frame; scanned, not asserted
    #    arcade   210..270  south  -> the mirror of `tier`, same joint criterion
    #    ctrl     270..450  the far, on-axis 180 deg -> a plain vertical wall, which is the only
    #                                 bank form that may be BOTH in frame and above the cone:
    #                                 a wall reads as continuous ground, a stepped bank does not.
    #  This is the single hardest constraint in the rebuild and it is what fixes the sector
    #  widths: at h0.3 the graze cone descends only 0.15 m per metre, so any *stepped* surface
    #  inside the bowl that is both in frame and above z = -0.15 x announces the depth.
    sector=dict(cascade=(150.0, 210.0), tier=(90.0, 150.0),
                arcade=(210.0, 270.0), ctrl=(270.0, 450.0)),
    # --- cascade (granite, on the walk axis) --------------------------------
    cascade=dict(riser=_RISER, tread=_TREAD, n_riser=_NRISER, n_built=_NBUILT,
                 land=_LAND, n_flight_a=15, arc_seg=20),
    # --- timber seating tiers ----------------------------------------------
    tiers=dict(riser=_TIER_RISER, tread=_TIER_TREAD, n=_NTIER, arc_seg=24,
               plank_t=0.06),
    # --- retail arcade under the ring deck ---------------------------------
    #     deck edge = the rim (r 14.0); shopfronts set back to r 17.0; the 3.0 m between them is
    #     the covered arcade walk. Clear height 3.70 m (deck soffit -0.80 to floor -4.50).
    arcade=dict(r_shop=17.0, shop_t=0.60, r_col=14.60, col_r=0.28, n_col=6,
                soffit_t=0.14, n_slat=12, bays=9,
                glass_z0=-4.30, glass_z1=-1.60, sill_h=0.20,
                emis=(0.86, 0.90, 0.82), emis_int=180.0),
    # --- control retaining wall (far, on-axis) ------------------------------
    ctrl=dict(wall_t=0.60, arc_seg=28),
    # --- upper plaza (ring deck) -------------------------------------------
    #     one annulus r 14.0..26.0 about C, 16 sectors, thickness 0.80. The plaza is circular by
    #     construction: a rectangle with a circular hole cannot be tiled by boxes and annular
    #     sectors without either a coplanar overlap (z-fighting) or an uncovered corner, and the
    #     v6 rectangle is precisely the shape the user asked to be taken out of this scene.
    #     Band materials are chosen on **measured albedo**, not on name. `plaza_light` is
    #     mean 0.710 `[measured — diff texture, 512 px]` and under a noon sun it renders past
    #     the v5.1 §4 pure-white line: the first pilot put **77.4 % of `h0.3_d2` above 0.8**
    #     with it on the near band. The near band is therefore `paving_interlock` (0.554) —
    #     literally v6's own plaza material, whose measured WHITE share was 0.3 % — and the
    #     rhythm is carried by `plaza_lower` (0.494), a 1.12:1 tone step, which is the kind of
    #     band G8 actually shows. A bullseye is as much a decorative ground pattern as a
    #     rectangle is.
    plaza=dict(r_out=26.0, thick=0.80, sectors=16, arc_seg=6,
               bands=((14.0, 17.2, "paving"), (17.2, 20.4, "plaza_b"),
                      (20.4, 23.6, "paving"), (23.6, 26.0, "plaza_b"))),
    # --- ground beyond the plaza + the carriageway --------------------------
    #     [S06-B] v6 painted two 90 m lane lines on bare ground with no road slab and no kerb.
    #     v7 builds the road: an 80 deg carriageway arc at street level (−0.150) with a real
    #     `infra_kit.build_curb_line` 1 m-unit kerb on its plaza side and dashed centre markings
    #     on the carriageway itself. Everything else outside the plaza stays flush at z = 0, so
    #     the scene carries exactly ONE new linear drop and it is the kerb, declared in the ledger.
    ground=dict(r_out=60.0, sectors=16, arc_seg=6, thick=1.0),
    road=dict(a0=20.0, a1=100.0, r_in=26.0, r_out=40.0, z_top=-0.150,
              chords=4, curb_h=0.150, curb_w=0.20, curb_unit=1.0,
              dash_r=(32.9, 33.1), dash_n=10, dash_deg=4.0),
    # --- parapet + glass balustrade (the B-1 guard) -------------------------
    #     guarded arc = arcade + ctrl = 210..450 deg. The cascade head (150..210) and the tier
    #     bank head (70..150) carry no guard: a 0.375 m tier riser is not a fall edge, and the
    #     cascade head IS the opening. Upstand + balustrade = 0.30 + 1.10 = 1.40 m, i.e. ABOVE
    #     the current statutory 1.1 rather than v6's sub-code 1.0 — the "sub-code reality" moved
    #     from the guard (G8 shows a modern glass system) to the fact that an opening exists.
    parapet=dict(a0=210.0, a1=450.0, t=0.30, h=0.30, arc_seg=28,
                 cope_h=0.06, cope_over=0.02, chords=22,
                 panel_h=1.10, panel_t=0.019, panel_len=1.35, joint=0.012,
                 cap_r=0.025, shoe_h=0.10),
    # --- cascade flank railings (R2) ---------------------------------------
    #  [GT-85] v7 called `props_kit.build_tube_railing` on a radial line that descends 4.400 m.
    #  That kit samples the ground ONCE per polyline segment (its midpoint) and lays every rail
    #  with `rotY=90`, i.e. **horizontal**. On a one-segment run the result was 4 level tubes
    #  frozen at the mid-flight height while the posts followed the true stair, so the run read
    #  as floating rails over orphan posts `[measured — rails z −2.130…−1.150 vs post tops
    #  −3.250…−0.100; 3 of 6 posts finished entirely below the lowest rail]`, and on the south
    #  flank the same level tubes drove straight through the timber tier bank. A raked stair
    #  guard is not expressible in that kit, so the run is built in-scene against the kit's own
    #  SECTION numbers — the scene06 precedent for a run the X-only template cannot state.
    #
    #  The guard is now dimensioned off the **nosing pitch line** (`flank_datum`), which is the
    #  line a stair guard is measured from: rail_h is the height over every nosing, so the guard
    #  stands 1.100 m over each nosing and 1.250 m over each tread back edge, and the lowest
    #  rail keeps a uniform 0.120 m toe gap `[computed]`. Section kept verbatim from the kit:
    #  4 rails inside 1.100 m with a 0.120 m bottom offset -> largest clear span
    #  (1.100 − 0.120)/3 − 2×0.024 = **0.279 m**, the deliberate non-baluster form.
    #    edge_off  the end newels stand this far clear of the rim / arena edge so the WHOLE post
    #              footprint bears on flat ground (post_r 0.030 << 0.100): no post straddles a
    #              riser, which is what left v7's posts hanging over a 0.150 m step
    #    ext       level handrail extension past each end of the flight, dying into an end newel
    #              (편의증진법 별표1 손잡이 수평연장 0.30 m) — no rail end is free anywhere
    #    azim_in   plan inset of the run from the cascade sector edge, in degrees (was hardcoded)
    flank_rail=dict(rails=4, rail_h=1.10, tube_r=0.024, post_r=0.030,
                    post_pitch=1.80, bottom=0.12, edge_off=0.10, ext=0.30,
                    azim_in=0.80),
    # --- tactile warning arc (cue_tactile; R16-2 stair-cue-first) ----------
    #     head band 0.30 m clear of the first riser, 0.60 m deep, on the cascade arc only.
    #     No stop-type device anywhere in this scene (R16-2), and no rectangle.
    tactile=dict(setback=0.30, depth=0.60, proud=0.006, arc_seg=16),

    # === [W2-D ground_kit] P3 `sidewalk_block` - spec Sec.5.2 row 08 ========
    #  RE-DERIVED for v7, not carried over. Two facts drive it and both are re-measured in the
    #  smoke run rather than trusted:
    #   (1) the near rim did **not** move: C = (14, 0) with r_rim = 14 puts the drop edge on
    #       x = 0 exactly where the v6 rectangle put it, so the three preset near-windows
    #       W1 = [eye_x + 0.564, eye_x + 2.000] are numerically unchanged:
    #         d2  W1 x −1.436..0     d5  W1 x −4.436..−3.000    d10 W1 x −9.436..−8.000
    #   (2) the scene-side `("patch", 3)` surface override is **DELETED** (GT-24 vocabulary,
    #       user ban on decorative ground rectangles). `sidewalk_block`'s own profile patch row
    #       was already deleted library-wide by GT-24 (`8b6baa7`), so v7 emits **0 patches**.
    #       `relaid` was considered and refused: a re-laid unit group needs a *cause*, and G8
    #       shows a plaza in its first decade with none.
    #  What is left in the near window is therefore ONE area element — the manhole — and its
    #  occupancy is re-derived, not patched: phi 0.648 at x = −2.40 is BEHIND the d2 eye
    #  (x = −2.0), and at d5 / d10 it sits 2.60 m / 7.60 m ahead where the frame half-width is
    #  1.501 m / 4.389 m, giving 21.6 % / 7.4 % of frame width. Both under the 25 % near-window
    #  monopoly ceiling the scene15 pilot set, and outside every W1.
    gkit=dict(
        region=(-11.0, -4.0, -0.95, 4.0),
        manhole=(-2.40, 1.60),
        gullies=((-1.90, -3.20), (-1.90, 3.20)),   # intercept before the rim
        arena_region=(11.5, -2.5, 16.5, 2.5),      # inscribed in the r 4.10 arena disc
        arena_gully=(14.0, 0.0),
        seed=8,
    ),

    # --- curved planting (G8's planted terrace + the tier-head bed) ---------
    #     Beds are annular, never square. `place_shrubs` walks the bed arc.
    beds=dict(
        tier_head=dict(r0=14.0, r1=15.4, a0=94.0, a1=146.0, kerb_h=0.45,
                       soil_h=0.40, n_shrub=9, n_tree=3),
        arcade_edge=dict(r0=14.6, r1=15.6, a0=214.0, a1=266.0, kerb_h=0.45,
                         soil_h=0.40, n_shrub=8, n_tree=0),
        # the one bed INSIDE the bowl (G8's planted lower terrace). It sits in the arcade
        # sector on purpose: a tree crown inside the bowl would otherwise stand above the
        # h0.3 graze cone and hand the depth away for free.
        #   a0/a1 are NOT round numbers: they are the arc over which the bed's 5.4 m tree
        #   crown clears the 30 deg half-frame at r0 = 8.6 (the binding radius). At a = 216 the
        #   crown measured 29.5 deg — inside the frame and 1.28 m above the graze cone.
        arena_south=dict(r0=8.6, r1=10.2, a0=222.0, a1=258.0, kerb_h=0.42,
                         soil_h=0.38, n_shrub=6, n_tree=1),
    ),
    # --- upper plaza street trees (4 square kerbed beds on the outer ring) --
    plaza_planters=[(148.0, 22.0), (212.0, 22.0), (56.0, 22.0), (304.0, 22.0)],
    plaza_planter=dict(size=3.0),
    # --- benches ------------------------------------------------------------
    arena_benches=dict(r=3.40, a0=96.0, a1=136.0, n=5),
    plaza_benches=[(168.0, 20.6, 0.0), (192.0, 20.6, 180.0),
                   (330.0, 20.6, 0.0), (30.0, 20.6, 180.0)],
    # --- street lights on the plaza ring ------------------------------------
    #  NOT on the walk axis: an a=180 pole at r=24 stands exactly on the h*_d10 eye.
    streetlights=[(60.0, 24.0), (120.0, 24.0), (240.0, 24.0), (300.0, 24.0)],
    streetlight=dict(pole_h=4.8, pole_r=0.075, arm_len=1.0, head=0.26),
    # --- bollards: re-sited from the v6 x = −18 row (a row of posts standing in the middle
    #     of a plaza separating nothing) to the kerb they actually belong to.
    #  PE-6/PE-7 `[law - 교통약자법 시행규칙 별표2 제7호]`: bollard pitch 1.5 m. The v6 row
    #  was 5 posts at 2.4 m standing in open plaza; v7 is ONE short run of 6 at exactly 1.5 m
    #  arc pitch across a crossing point on the kerb, which is what a bollard row is for.
    bollards=dict(a0=51.5, a1=68.5, r=25.3, n=6),
    # --- signs (cue_sign) --- [v5.2 user] arbitrary warning signs removed
    sign_exit=dict(a=236.0, r=13.2, z=_FLOOR_Z, yaw=326.0, w=0.62, h=0.62,
                   pole_h=2.2),
    # --- BS-4 CBD wall (kind="backdrop") ------------------------------------
    #     G8 legitimately closes the horizon with a downtown block. Placed on a ring at
    #     r 42..56 about C so it closes every judged bearing without ever entering the bowl.
    backdrop=dict(base_z=-0.35, blocks=(
        # (x0, x1, y0, y1, h, floors, axis, facade, face_dir, mtl)
        (44.0, 56.0, -16.0,  -2.0, 34.0, 11, "x",  44.0, -1.0, "city_stone"),
        (44.0, 56.0,  -2.0,  12.0, 46.0, 15, "x",  44.0, -1.0, "city_plaster"),
        (44.0, 56.0,  12.0,  26.0, 28.0,  9, "x",  44.0, -1.0, "city_wall"),
        (18.0, 32.0,  34.0,  46.0, 38.0, 12, "y",  34.0, -1.0, "city_plaster"),
        (-2.0, 14.0,  34.0,  46.0, 26.0,  8, "y",  34.0, -1.0, "city_stone"),
        (18.0, 32.0, -46.0, -34.0, 42.0, 13, "y", -34.0,  1.0, "city_wall"),
        (-2.0, 14.0, -46.0, -34.0, 30.0, 10, "y", -34.0,  1.0, "city_plaster"),
        #  the −X block sits back at 30 m: at a −18 m facade `building_kit` measures
        #  `d_true` 8.0 m from the h*_d10 eye, i.e. a 32 m tower standing 8 m behind the
        #  judged camera. Measured, then moved.
        (-46.0, -30.0, -14.0,  2.0, 32.0, 10, "x", -30.0, 1.0, "city_stone"),
    )),
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.2),

    material=dict(
        # texture_scale = physical tile size [m].
        scale=dict(paving_interlock=1.5, plaza_light=1.6, plaza_lower=1.6,
                   band_dark=1.2, concrete_wall=2.0, concrete_floor=1.0,
                   granite_dark=1.2, grass=1.4, tactile=0.3, wood_dark=1.1,
                   stone_flag=1.4, asphalt=2.0),
        grass_tint=(0.55, 0.68, 0.42),
        # sRGB gamma rule (§A-1): a "dark colour" lives in the 0.02~0.06 band.
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.88,
        paint_color=(0.72, 0.72, 0.68), paint_rough=0.6,
        parapet_tint=(0.80, 0.79, 0.76),      # concrete diff x tint -> ~0.58
        cope_tint=(0.70, 0.69, 0.67),
        grime_color=(0.24, 0.235, 0.225), grime_rough=0.82,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [K5 S06-B 3.] a curb-class role, NOT granite_dark (scene01: "reads as a black hole")
        curb_tint=(0.86, 0.85, 0.82),
        #  **Plaza albedo is measured, not styled.** The stock diffuse maps sit high —
        #  `paving_interlock` 0.554, `plaza_lower` 0.494, `stone_flag` 0.476 `[measured,
        #  512 px, Rec.709 luma]` — and pilot 2 rendered the sunlit near band at
        #  `near_ground_stats` **L_mu 0.728 · wht 29.6 %**, i.e. a plaza that is brighter than
        #  any 화강석 판석 or 보도블록 in the field (real 0.35–0.45). These tints pull all three
        #  onto ~0.40, which is both the realistic band and what clears the v5.1 §4 WHITE flag.
        pave_tint=(0.72, 0.72, 0.71),      # 0.554 -> 0.399
        plazab_tint=(0.80, 0.80, 0.79),    # 0.494 -> 0.395
        flag_tint=(0.85, 0.85, 0.84),      # 0.476 -> 0.405
        cwall_tint=(0.85, 0.85, 0.84),     # 0.523 -> 0.445
        wood_tint=(0.72, 0.62, 0.50),
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        glass_color=(0.055, 0.075, 0.090), glass_rough=0.10,
        # [G8] the balustrade is low-iron laminated glass seen against sky, not shopfront glass
        #  No transmission is available in this material stack, so a laminated balustrade
        #  seen against sky must be authored as what it *reads* as: a pale, slightly rough
        #  panel. At 0.115 it rendered as a black ribbon around the rim (pilot 1).
        gb_color=(0.30, 0.34, 0.36), gb_rough=0.12,
        mull_color=(0.055, 0.055, 0.060), mull_rough=0.45, mull_metallic=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        sign_back_color=(0.055, 0.060, 0.070), sign_back_rough=0.5,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        city_stone_tint=(0.62, 0.61, 0.58),
        city_plaster_tint=(0.70, 0.68, 0.64),
        city_wall_tint=(0.55, 0.55, 0.54),
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
    # raking light, inherited from the old scene08 and kept: a bowl 4.5 deep goes flat under
    #   standard noon light. At 60 deg the south half of the bowl (the arcade side) takes direct
    #   sun and the north half (the timber tiers) stays in shadow, which is what separates the
    #   two banks tonally. Re-verified numerically against the circular plan in the smoke run.
    SUN_AZ_OFFSET=60.0,

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
# [B2] PLACEMENT — the geometry-free datum block `scripts/placement_lint.py` reads
#      statically (spec §10.4). Declared, and where it is empty the emptiness is a
#      finding rather than an omission (the scene04 / scene07 precedent).
# ===========================================================================
PLACEMENT = dict(
    # **Empty on purpose.** LINT-5 reads `walk_edges` as a 보도 boundary and applies PE-8
    # (「도로의 구조·시설 기준에 관한 규칙」 제16조, 1.5 m effective width) to whatever stands
    # near it. This scene is a 광장: the strip that fronts the carriageway is 12.0 m of
    # continuous plaza ring (r 14.0 → 26.0), so the 1.5 m floor is vacuous by two orders of
    # magnitude, and declaring an arbitrary inner boundary would import a rule that does not
    # govern a plaza — and would then "fail" furniture placed correctly against a circle.
    walk_edges=[],
    # **The 보차도 경계 is real geometry, so it is declared.** These are the four chords the
    # K5 `build_curb_line` runs are actually built on (r = 26.0 about C = (14, 0), a = 20..100
    # deg), listed as literals because the linter reads this block statically and cannot call
    # `_pol`. LINT-6's PE-7 axis lock now has its datum instead of reporting `nodata`.
    kerb_lines=[
        ((38.432, 8.8925), (33.9172, 16.7125)),
        ((33.9172, 16.7125), (27.0, 22.5167)),
        ((27.0, 22.5167), (18.5149, 25.605)),
        ((18.5149, 25.605), (9.4851, 25.605)),
    ],
    # **No anchor is declared, and the reason is the plan, not taste.** LINT-7's inferred
    # expectation is the Cartesian set {0, 90, 180, 270}; on a radial plan every bench, sign
    # and light faces the bowl centre, so its correct yaw is its own azimuth and no single
    # `face_bearing_deg` describes the set. Fitting one anchor per prop to the geometry it is
    # meant to judge proves nothing (scene04's call), so the datum stays absent and LINT-7's
    # findings stay advisory `[inferred]` — which is what §10.4 says an inferred finding is for.
    anchors={},
    # 08's trees are **four isolated kerbed beds** on a plaza ring plus one bed inside the
    # bowl, not a street row. Declaring a `route` would import the 8.0 m 가로수 pitch rule
    # (TREE_PITCH_M) onto beds that are 90 deg apart on a circle by design.
    routes={},
)


# ===========================================================================
# [C] paths + texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene08")
ASSET_ROLES = ["paving_interlock", "plaza_light", "plaza_lower", "band_dark",
               "concrete_wall", "concrete_floor", "granite_dark", "grass",
               "tactile", "wood_dark", "stone_flag", "asphalt",
               "sign_exit", "hdri", "mdl"]


# ===========================================================================
# [C2] polar geometry helpers — the single source of coordinate definitions.
#      Everything in this scene is designed in (r, a) about C and converted here.
# ===========================================================================
def _pol(r, a_deg):
    """(r, a) about the bowl centre -> world (x, y)."""
    b = PARAMS["bowl"]
    t = math.radians(a_deg)
    return (b["cx"] + r * math.cos(t), b["cy"] + r * math.sin(t))


def _rad(x, y):
    b = PARAMS["bowl"]
    return math.hypot(x - b["cx"], y - b["cy"])


def _azi(x, y):
    b = PARAMS["bowl"]
    return math.degrees(math.atan2(y - b["cy"], x - b["cx"])) % 360.0


def _in_sector(a_deg, a0, a1):
    """Is azimuth a inside [a0, a1)? Handles wrap (a1 may exceed 360)."""
    return ((a_deg - a0) % 360.0) < (a1 - a0) - 1e-9


def _sector_of(a_deg):
    for name, (a0, a1) in PARAMS["sector"].items():
        if _in_sector(a_deg, a0, a1):
            return name
    return "ctrl"


def cascade_courses():
    """[(r_in, r_out, top_z, kind)] outermost first. kind: 'A' | 'L' | 'B'.

    The 30th riser is **the arena floor itself** — building a 30th course would put its top
    coplanar with the floor slab top and z-fight (the v5 lesson, kept)."""
    cs = PARAMS["cascade"]
    b = PARAMS["bowl"]
    out, r = [], b["r_rim"]
    for k in range(cs["n_flight_a"]):
        out.append((r - cs["tread"], r, -(k + 1) * cs["riser"], "A"))
        r -= cs["tread"]
    out.append((r - cs["land"], r, -cs["n_flight_a"] * cs["riser"], "L"))
    r -= cs["land"]
    for k in range(cs["n_flight_a"], cs["n_built"]):
        out.append((r - cs["tread"], r, -(k + 1) * cs["riser"], "B"))
        r -= cs["tread"]
    return out, round(r, 6)


def tier_courses():
    """[(r_in, r_out, top_z)] outermost first. The 12th riser is the arena floor."""
    tp = PARAMS["tiers"]
    b = PARAMS["bowl"]
    out, r = [], b["r_rim"]
    for k in range(tp["n"]):
        out.append((r - tp["tread"], r, -(k + 1) * tp["riser"]))
        r -= tp["tread"]
    return out, round(r, 6)


def _surface_z(x, y):
    """Top of the walked surface at (x, y)."""
    b = PARAMS["bowl"]
    rd = PARAMS["road"]
    r, a = _rad(x, y), _azi(x, y)
    if r >= b["r_rim"]:
        if rd["r_in"] <= r < rd["r_out"] and _in_sector(a, rd["a0"], rd["a1"]):
            return rd["z_top"]
        if r >= rd["r_out"] and _in_sector(a, rd["a0"], rd["a1"]):
            return rd["z_top"]
        return 0.0
    if r <= b["r_arena"]:
        return b["floor_z"]
    sec = _sector_of(a)
    if sec == "cascade":
        for r_in, r_out, tz, _k in cascade_courses()[0]:
            if r_in - 1e-9 <= r <= r_out + 1e-9:
                return tz
    elif sec == "tier":
        for r_in, r_out, tz in tier_courses()[0]:
            if r_in - 1e-9 <= r <= r_out + 1e-9:
                return tz
    return b["floor_z"]                 # arcade + ctrl forecourt


# --- [GT-85] cascade flank guard: the run is designed here, built in [F] -----
def flank_azimuths():
    """[(tag, a_deg)] the two flank rays, inset `azim_in` from the cascade sector edges.

    The rays are UNCHANGED from v7 (a0 + 0.80 / a1 − 0.80); only what is built on them moved.
    The binding clearance is at the foot, where the sector edge is the tier bank's radial face:
    at r = 4.100 the 0.80 deg inset is 0.057 m in plan, so the post face stands 0.027 m and the
    tube face 0.033 m clear of it `[measured]` — tight, but the run does not touch the bank.
    The v7 defect was the opposite failure: level tubes at one frozen z drove straight THROUGH
    the tier bank between r 11 and 12 on the south flank."""
    a0, a1 = PARAMS["sector"]["cascade"]
    ai = PARAMS["flank_rail"]["azim_in"]
    return [("S", a0 + ai), ("N", a1 - ai)]


def flank_nodes():
    """(r_head, r_a_foot, r_land_foot, r_foot) — the guard's kink radii, outermost first.

    Both outer nodes sit `edge_off` CLEAR of the edge they guard (rim / arena rather than on it)
    so every newel's footprint bears wholly on one flat surface; `post_r` 0.030 << `edge_off`
    0.100 `[computed]`. A post placed exactly on the rim or the arena edge is half over a
    0.150 m riser, which is the class of defect this rebuild exists to remove."""
    b, cs, fr = PARAMS["bowl"], PARAMS["cascade"], PARAMS["flank_rail"]
    r_a = b["r_rim"] - cs["n_flight_a"] * cs["tread"]        # 9.50 flight A foot
    return (b["r_rim"] + fr["edge_off"], r_a, r_a - cs["land"],
            b["r_arena"] - fr["edge_off"])


def flank_datum(r):
    """z of the guard datum on the cascade ray at radius r — the **nosing pitch line**.

    Straight over each flight at dz/dr = riser/tread = 0.500, level over the 1.20 m mid landing,
    level over both handrail extensions. Every rail is a fixed offset from this line, so the
    guard height is constant relative to the stair instead of constant in world z (the GT-85
    defect). At r = r_rim the line is exactly z = 0, i.e. it meets the plaza at the rim."""
    b, cs = PARAMS["bowl"], PARAMS["cascade"]
    r_head, r_a, r_l, r_foot = flank_nodes()
    s = cs["riser"] / cs["tread"]
    z_a = -cs["n_flight_a"] * cs["riser"]                    # −2.250 at the flight A foot
    if r >= r_head:
        return s * (r_head - b["r_rim"])
    if r >= r_a:
        return s * (r - b["r_rim"])
    if r >= r_l:
        return z_a
    if r >= r_foot:
        return z_a + s * (r - r_l)
    return z_a + s * (r_foot - r_l)


def _tread_centres(r_hi, r_lo, tread):
    """[r] centre radius of every whole tread in (r_lo, r_hi], outermost first."""
    out, r = [], r_hi
    while r - tread > r_lo - 1e-9:
        out.append(round(r - tread / 2.0, 6))
        r -= tread
    return out


def flank_posts():
    """[r] post radii on one flank, outermost first.

    Every rail kink carries a post except the landing foot, where a post would bridge the
    landing nosing and the course below it; that one kink is closed by an elbow instead.
    Interior posts SNAP to tread centres, which is what makes the run read as one guard: a post
    landing at a tread centre is always the same length `[computed 1.199 m]`, so the whole run
    finishes within 1.124…1.224 m. Bay count is ceil(L / post_pitch), so no bay exceeds the
    1.80 m spec pitch `[computed max 1.65 m]`."""
    b, cs, fr = PARAMS["bowl"], PARAMS["cascade"], PARAMS["flank_rail"]
    r_head, r_a, r_l, r_foot = flank_nodes()

    def interior(r_hi, r_lo, cen):
        n = max(1, int(math.ceil((r_hi - r_lo) / fr["post_pitch"] - 1e-9)))
        out = []
        for i in range(1, n):
            want = r_hi - (r_hi - r_lo) * i / n
            out.append(min(cen, key=lambda c: (abs(c - want), -c)))
        return out

    return ([round(r_head + fr["ext"], 6), round(r_head, 6)]
            + interior(r_head, r_a, _tread_centres(b["r_rim"], r_a, cs["tread"]))
            + [round(r_a, 6), round(r_l + fr["edge_off"], 6)]
            + interior(r_l, r_foot, _tread_centres(r_l, b["r_arena"], cs["tread"]))
            + [round(r_foot, 6), round(r_foot - fr["ext"], 6)])


def flank_rail_offsets():
    """[dz] rail-axis offsets above the datum line, lowest first — the kit's own ladder."""
    fr = PARAMS["flank_rail"]
    n = int(fr["rails"])
    return [fr["bottom"] + (fr["rail_h"] - fr["bottom"]) * k / max(1, n - 1)
            for k in range(n)]


def _sun_dir():
    """DistantLight travel direction d (world). Inverts setup_lighting's op order exactly."""
    lp = PARAMS["light"]
    rz = math.radians(lp["noon_dome_rot"] + PARAMS["SUN_AZ_OFFSET"]
                      + lp["hdri_sun_rotz_offset"])
    rx = math.radians(90.0 - lp["noon_sun_elev"])
    return (-math.sin(rx) * math.sin(rz),
            math.sin(rx) * math.cos(rz),
            -math.cos(rx))


# --- named bed / planter footprints, shared by the builders and the checks --
def bed_arcs():
    """[(name, r0, r1, a0, a1, kerb_h)] for every annular planting bed."""
    return [(n, d["r0"], d["r1"], d["a0"], d["a1"], d["kerb_h"])
            for n, d in PARAMS["beds"].items()]


def planter_boxes():
    """[(tag, x0, x1, y0, y1, z0, z1)] for the 4 square upper-plaza street-tree beds."""
    ps = PARAMS["plaza_planter"]["size"] / 2.0
    out = []
    for i, (a, r) in enumerate(PARAMS["plaza_planters"]):
        cx, cy = _pol(r, a)
        out.append((f"PlazaPlanter_{i}", cx - ps, cx + ps, cy - ps, cy + ps,
                    0.0, 3.40))
    return out


def bed_contains(name, x, y, margin=0.0):
    """Plan distance from (x, y) to a bed footprint. 0.0 when inside.

    Annular beds are tested in POLAR coordinates, not by AABB: a 52 deg arc's axis-aligned
    bounding box is ~20 x 15 m and would swallow half the plaza, which is exactly how a
    containment check turns into a false alarm (and, run the other way, into a missed one).
    """
    bd = PARAMS["beds"][name]
    r, a = _rad(x, y), _azi(x, y)
    dr = max(bd["r0"] - r, 0.0, r - bd["r1"])
    da = 0.0
    if not _in_sector(a, bd["a0"], bd["a1"]):
        d0 = min((a - bd["a0"]) % 360.0, (bd["a0"] - a) % 360.0)
        d1 = min((a - bd["a1"]) % 360.0, (bd["a1"] - a) % 360.0)
        da = math.radians(min(d0, d1)) * max(r, 1e-6)
    return math.hypot(dr, da) - margin


def planter_dist(x, y):
    """Plan distance from (x, y) to the nearest bed of ANY kind, with its name."""
    best, who = 1e9, ""
    for name in PARAMS["beds"]:
        d = bed_contains(name, x, y)
        if d < best:
            best, who = d, f"Bed_{name}"
    for tag, x0, x1, y0, y1, _z0, _z1 in planter_boxes():
        d = math.hypot(max(x0 - x, 0.0, x - x1), max(y0 - y, 0.0, y - y1))
        if d < best:
            best, who = d, tag
    return best, who


def h03_probes():
    """[(tag, x, y, z_top)] — every element that stands inside the bowl and could poke above
    the h0.3 graze cone. Walked surfaces are scanned separately (they are continuous); this
    list is the *standing* furniture the surface scan cannot see."""
    b = PARAMS["bowl"]
    fr = PARAMS["flank_rail"]
    out = []
    # cascade flank guard — [GT-85] probe the CROWN of the top rail (datum + rail_h + tube_r),
    #   which is the run's highest point, over the whole run INCLUDING both handrail extensions.
    #   The v7 probe used `_surface_z + rail_h`, which was neither where the rail was built nor
    #   the top of it, and it stopped 0.25 m short of each end.
    r_head, _r_a, _r_l, r_foot = flank_nodes()
    r0, r1 = r_foot - fr["ext"], r_head + fr["ext"]
    for tag, a in flank_azimuths():
        r = r0
        while r <= r1 + 1e-6:
            px, py = _pol(r, a)
            out.append((f"Flank{tag}_{r:.1f}", px, py,
                        flank_datum(r) + fr["rail_h"] + fr["tube_r"]))
            r += 0.25
    # in-bowl bed: kerb + shrub crown
    bd = PARAMS["beds"]["arena_south"]
    for i in range(13):
        aa = bd["a0"] + (bd["a1"] - bd["a0"]) * i / 12.0
        for rr in (bd["r0"], bd["r1"]):
            px, py = _pol(rr, aa)
            gz = _surface_z(px, py)
            out.append((f"BedShrub_{i}", px, py, gz + bd["soil_h"] + 0.90))
            out.append((f"BedTree_{i}", px, py, gz + bd["soil_h"] + 5.4))
    # arena benches
    ab = PARAMS["arena_benches"]
    for i in range(int(ab["n"])):
        aa = ab["a0"] + (ab["a1"] - ab["a0"]) * (i + 0.5) / ab["n"]
        px, py = _pol(ab["r"], aa)
        out.append((f"ArenaBench_{i}", px, py, b["floor_z"] + 0.85))
    # arcade columns + soffit + shopfront head
    ar = PARAMS["arcade"]
    a0, a1 = PARAMS["sector"]["arcade"]
    for i in range(int(ar["n_col"])):
        aa = a0 + (a1 - a0) * (i + 0.5) / ar["n_col"]
        px, py = _pol(ar["r_col"], aa)
        out.append((f"ArcadeCol_{i}", px, py, -0.80))
    for i in range(9):
        aa = a0 + (a1 - a0) * i / 8.0
        px, py = _pol(ar["r_shop"], aa)
        out.append((f"ShopHead_{i}", px, py, ar["glass_z1"] + 0.34))
    # the facility sign
    sg = PARAMS["sign_exit"]
    sx, sy = _pol(sg["r"], sg["a"])
    out.append(("SignExit", sx, sy, sg["z"] + sg["pole_h"]))
    return out


def h03_visible(x, y, z, d=2.0, half_fov=30.0):
    """Would (x, y, z) show in the h0.3_d{d} frame?

    Two conditions, and BOTH must hold: the point must sit above the graze cone from the eye
    (-d, 0, 0.3) over the near rim (0, 0, 0) — z > -0.15 (x) at d = 2 — and it must lie inside
    the 30 deg half-frame. The cone slope is 0.3/d, so d = 2 is the binding case and the only
    one scanned.
    """
    if x <= 0.0:
        return False
    if z <= -(0.3 / d) * x + 1e-6:
        return False
    return abs(math.degrees(math.atan2(y, x + d))) < half_fov


def _obstacle_boxes():
    """Obstacle AABB list for camera collision checks (name, x0,x1, y0,y1, z0,z1).
    [brief v5 instruction] Verify by coordinates that the grid/mise-en-scene cameras do not
    collide with a guard·planter (the scene19 d5 blackout precedent)."""
    b = PARAMS["bowl"]
    pr = PARAMS["parapet"]
    boxes = list(planter_boxes())
    # **Annular beds are deliberately NOT in this list.** The AABB of a 36-52 deg arc at
    # r ~ 15 is a ~20 x 12 m box that reports a false collision for any eye standing inside
    # the bowl; they are tested in polar by `bed_contains` in the collision loop instead.
    # the guarded rim arc, as 12 chord AABBs (one AABB would swallow the whole plaza)
    for i in range(12):
        aa = pr["a0"] + (pr["a1"] - pr["a0"]) * i / 12.0
        ab = pr["a0"] + (pr["a1"] - pr["a0"]) * (i + 1) / 12.0
        xs, ys = [], []
        for a in (aa, (aa + ab) / 2.0, ab):
            for rr in (b["r_rim"], b["r_rim"] + pr["t"]):
                px, py = _pol(rr, a)
                xs.append(px)
                ys.append(py)
        boxes.append((f"Guard_{i}", min(xs), max(xs), min(ys), max(ys),
                      0.0, pr["h"] + pr["panel_h"] + 0.10))
    sl = PARAMS["streetlight"]
    for i, (a, r) in enumerate(PARAMS["streetlights"]):
        cx, cy = _pol(r, a)
        boxes.append((f"Streetlight_{i}", cx - 0.30, cx + 0.30,
                      cy - 1.20, cy + 1.20, 0.0, sl["pole_h"]))
    sg = PARAMS["sign_exit"]
    sx, sy = _pol(sg["r"], sg["a"])
    hw = sg["w"] / 2.0 + 0.06
    boxes.append(("SignExit", sx - hw, sx + hw, sy - hw, sy + hw,
                  sg["z"], sg["z"] + sg["pole_h"]))
    return boxes


def _solid_at(x, y, z):
    """Name of the terrain/structure solid containing (x, y, z), else None.
    Single source for the camera-eye burial check + the sight-line ray march."""
    b = PARAMS["bowl"]
    pl = PARAMS["plaza"]
    gr = PARAMS["ground"]
    rd = PARAMS["road"]
    ar = PARAMS["arcade"]
    pr = PARAMS["parapet"]
    r, a = _rad(x, y), _azi(x, y)
    sec = _sector_of(a)

    # --- upper plaza ring / ring deck ------------------------------------
    if b["r_rim"] <= r <= pl["r_out"] and -pl["thick"] <= z < 0.0:
        return "PlazaRing"
    # --- ground beyond the plaza -----------------------------------------
    if pl["r_out"] < r <= gr["r_out"]:
        road = _in_sector(a, rd["a0"], rd["a1"])
        top = rd["z_top"] if road else 0.0
        if top - gr["thick"] <= z < top:
            return "Road" if road else "Ground"
    # --- bowl floor slab --------------------------------------------------
    r_floor = ar["r_shop"] if sec == "arcade" else b["r_rim"]
    if r <= r_floor and b["floor_z"] - b["floor_thick"] <= z < b["floor_z"]:
        return "BowlFloor"
    # --- banks -------------------------------------------------------------
    if b["r_arena"] < r < b["r_rim"]:
        if sec == "cascade":
            for i, (r_in, r_out, tz, _k) in enumerate(cascade_courses()[0]):
                if r_in <= r < r_out and b["bank_base"] <= z < tz:
                    return f"Cascade_{i}"
        elif sec == "tier":
            for i, (r_in, r_out, tz) in enumerate(tier_courses()[0]):
                if r_in <= r < r_out and b["bank_base"] <= z < tz:
                    return f"Tier_{i}"
        elif sec == "ctrl" and r >= b["r_rim"] - PARAMS["ctrl"]["wall_t"] \
                and b["bank_base"] <= z < 0.0:
            return "CtrlWall"
    if sec == "arcade" and ar["r_shop"] <= r < ar["r_shop"] + ar["shop_t"] \
            and b["bank_base"] <= z < 0.0:
        return "ShopWall"
    # --- the guard --------------------------------------------------------
    if _in_sector(a, pr["a0"], pr["a1"]) \
            and b["r_rim"] <= r <= b["r_rim"] + pr["t"] and 0.0 <= z <= pr["h"]:
        return "Parapet"
    return None


# ===========================================================================
# [C3] smoke - pre-boot self-check of geometry·lighting·camera (early exit)
# ===========================================================================
def _smoke_report():
    b = PARAMS["bowl"]
    cs = PARAMS["cascade"]
    tp = PARAMS["tiers"]
    pr = PARAMS["parapet"]
    gates = []

    def gate(name, cond, detail=""):
        gates.append((name, bool(cond)))
        print(f"    [{'OK ' if cond else 'FAIL'}] {name}"
              f"{('  ' + detail) if detail else ''}")

    print("=" * 76)
    print("scene08_sunken_plaza — SMOKE 기하 자기검증 v7 곡선 (부팅 없음)")
    print("=" * 76)

    # ── 1. bowl + cascade + tiers arithmetic ──────────────────────────────
    courses, r_end_c = cascade_courses()
    tiers, r_end_t = tier_courses()
    drop = cs["riser"] * cs["n_riser"]
    print("  [보울 · 캐스케이드 · 티어 산술]")
    print(f"    보울 중심 C=({b['cx']:.1f},{b['cy']:.1f}) · 림 반경 {b['r_rim']:.1f}"
          f" → 근측 연단 x={b['cx']-b['r_rim']:.2f} · 원측 연단 x={b['cx']+b['r_rim']:.2f}")
    gate("근측 연단이 보행축 x=0", abs(b["cx"] - b["r_rim"]) < 1e-9)
    gate("낙차 = riser × n_riser", abs(drop + b["floor_z"]) < 1e-9,
         f"{drop:.3f} = {abs(b['floor_z']):.3f}")
    gate("낙차 ≥ 0.30 m", drop >= 0.3, f"{drop:.3f}")
    print(f"    캐스케이드 : {cs['n_built']}단(솔리드) + 계단참 {cs['land']:.2f} m "
          f"+ 바닥 1라이저 = {cs['n_riser']} 라이저 · riser {cs['riser']:.3f} · "
          f"tread {cs['tread']:.3f}")
    gate("캐스케이드가 아레나 반경에서 끝난다",
         abs(r_end_c - b["r_arena"]) < 1e-6,
         f"r={r_end_c:.4f} vs {b['r_arena']:.4f}")
    gate("티어 뱅크도 같은 아레나 반경에서 끝난다",
         abs(r_end_t - b["r_arena"]) < 1e-6, f"r={r_end_t:.4f}")
    gate("티어 12라이저 = 보울 깊이",
         abs((tp["n"] + 1) * tp["riser"] + b["floor_z"]) < 1e-9,
         f"{(tp['n']+1)*tp['riser']:.3f}")
    dA = cs["n_flight_a"] * cs["riser"]
    dB = (cs["n_built"] - cs["n_flight_a"] + 1) * cs["riser"]
    print(f"    [법규 L1 계단참] A 구간 낙차 {dA:.3f} · B 구간 낙차 {dB:.3f} · "
          f"계단참 너비 {cs['land']:.2f} m")
    gate("L1 어느 구간도 3.0 m 직통 아님", max(dA, dB) <= 3.0 + 1e-9)
    gate("L1 계단참 너비 ≥ 1.20 m", cs["land"] >= 1.20 - 1e-9)
    exempt = (cs["riser"] <= 0.150 + 1e-9) and (cs["tread"] >= 0.300 - 1e-9)
    a0c, a1c = PARAMS["sector"]["cascade"]
    w_head = 2.0 * b["r_rim"] * math.sin(math.radians((a1c - a0c) / 2.0))
    w_foot = 2.0 * b["r_arena"] * math.sin(math.radians((a1c - a0c) / 2.0))
    print(f"    [법규 R1 중간난간] 캐스케이드 현폭 머리 {w_head:.2f} m → 발치 "
          f"{w_foot:.2f} m (반경 비례 · tread 는 전 구간 {cs['tread']:.3f} 균일 = 윈더 아님)")
    gate("R1 면제 성립 (riser≤0.150 AND tread≥0.300)", exempt,
         f"riser {cs['riser']:.3f} · tread {cs['tread']:.3f}")
    gate("D1 단높이 ≤ 0.20", cs["riser"] <= 0.20)
    print(f"    [좌석 티어] riser {tp['riser']:.3f} · tread {tp['tread']:.3f} — "
          f"관람석(순환동선 아님). scene05 ※ 선례로 계단 규정 대상 제외를 명시 기록")

    # [GT-85] R2 flank guard — the run must be CARRIED, not floating. Four properties, each of
    #   which the v7 kit call violated: bay ≤ spec pitch, one post length (so one rail height),
    #   the lowest rail clear of the walked surface, and no post foot straddling a riser.
    fr = PARAMS["flank_rail"]
    fp = flank_posts()
    a_f = flank_azimuths()[0][1]
    f_bay = max(fp[i] - fp[i + 1] for i in range(len(fp) - 1))
    f_len = [flank_datum(r) + fr["rail_h"] + fr["tube_r"]
             - _surface_z(*_pol(r, a_f)) for r in fp]
    f_toe, rr = 9e9, fp[-1]
    while rr <= fp[0] + 1e-9:
        f_toe = min(f_toe, flank_datum(rr) + fr["bottom"]
                    - _surface_z(*_pol(rr, a_f)))
        rr += 0.01
    print(f"    [법규 R2 편측난간] 플랭크당 지주 {len(fp)} · 간격 "
          f"{min(fp[i]-fp[i+1] for i in range(len(fp)-1)):.2f}~{f_bay:.2f} m · "
          f"지주 길이 {min(f_len):.3f}~{max(f_len):.3f} m · 최하단 레일 발끝 여유 "
          f"{f_toe:.3f} m · 수평연장 {fr['ext']:.2f} m × 2")
    gate("R2 지주 간격 ≤ post_pitch", f_bay <= fr["post_pitch"] + 1e-9,
         f"{f_bay:.2f} ≤ {fr['post_pitch']:.2f}")
    gate("R2 지주 길이 편차 ≤ 0.15 m (난간고 일정)",
         max(f_len) - min(f_len) <= 0.15 + 1e-9,
         f"Δ{max(f_len)-min(f_len):.3f} m")
    gate("R2 최하단 레일이 보행면 위 (파고듦 0)", f_toe >= 0.05,
         f"{f_toe:.3f} m")
    gate("R2 지주 발이 전부 평탄면 (라이저 걸침 0)",
         all(abs(_surface_z(*_pol(r - fr["post_r"], a_f))
                 - _surface_z(*_pol(r + fr["post_r"], a_f))) < 1e-6
             for r in fp))
    gate("R2 레일 마디 끝이 전부 지주/엘보에 물림",
         all(any(abs(r - p) < 1e-6 for p in fp)
             or abs(r - flank_nodes()[2]) < 1e-6
             for r in (flank_nodes()[0] + fr["ext"], flank_nodes()[0],
                       flank_nodes()[1], flank_nodes()[2],
                       flank_nodes()[3], flank_nodes()[3] - fr["ext"])))

    # ── 2. nothing covers the cavity ──────────────────────────────────────
    print("  [공동 은폐 검산] 개구 위를 덮는 z≥0 판이 있는가")
    covered = []
    for aa in range(0, 360, 5):
        for rr in (0.5, 2.0, 5.0, 9.0, 13.5):
            px, py = _pol(rr, float(aa))
            s = _solid_at(px, py, 0.05)
            if s is not None:
                covered.append((rr, aa, s))
    gate("보울 내부 z=+0.05 에 솔리드 없음", not covered,
         f"{covered[:3]}" if covered else "")
    gate("아레나 바닥이 −4.500",
         abs(_surface_z(b["cx"], b["cy"]) - b["floor_z"]) < 1e-9)

    # ── 3. walk continuity along the a=180 ray ────────────────────────────
    print("  [보행 연속성] a=180° 광선 위 단차 (모두 ≤ riser)")
    prev, worst, worst_at, x = 0.0, 0.0, 0.0, 0.0
    while x <= 10.6:
        z = _surface_z(x, 0.0)
        d = abs(z - prev)
        if d > worst:
            worst, worst_at = d, x
        prev = z
        x += 0.05
    gate("연속 단차 ≤ riser + 1 mm", worst <= cs["riser"] + 0.001,
         f"최대 {worst:.4f} m @ x={worst_at:.2f}")

    # ── 4. h0.3 concealment (research core) ───────────────────────────────
    print("  [h0.3 은닉 검산] 근측 연단(x=0,z=0) 스치는 시선이 바닥에 닿는 x")
    far_rim = b["cx"] + b["r_rim"]
    hid_all = True
    for d in (2.0, 5.0, 10.0):
        x_hit = abs(b["floor_z"]) * d / 0.3
        hid_all = hid_all and (x_hit > far_rim)
        print(f"    d={d:4.1f} m → x_hit {x_hit:6.1f} m vs 원측 연단 {far_rim:.1f} m "
              f"→ 여유 {x_hit-far_rim:+.1f} m")
    gate("전 프리셋 거리에서 보울 바닥 은닉", hid_all)
    print("    [돌출물 검산] '스침원뿔 위' ∧ '30° 반프레임 안' 인 보울 내부 요소")
    surf = []
    for aa in range(0, 360):
        rr = b["r_arena"]
        while rr <= b["r_rim"] + 1e-6:
            px, py = _pol(float(rr), float(aa))
            if h03_visible(px, py, _surface_z(px, py)):
                surf.append((round(px, 1), round(py, 1),
                             round(_surface_z(px, py), 2)))
            rr += 0.10
    gate("보울 내부 보행면 — 프레임 안 노출 0", not surf,
         f"{len(surf)} 점, 예: {surf[:2]}" if surf else "")
    stand = [(t, round(px, 1), round(py, 1), round(pz, 2))
             for t, px, py, pz in h03_probes() if h03_visible(px, py, pz)]
    gate("보울 내부 기립요소(난간·화단·벤치·기둥·사인) — 프레임 안 노출 0",
         not stand, f"{len(stand)} 개, 예: {stand[:2]}" if stand else "")
    gate("파라펫/유리난간이 캐스케이드 머리에 없음",
         not _in_sector(180.0, pr["a0"], pr["a1"]), "개구 = 계단 머리 (B-1)")

    # ── 5. lateral framing — which sectors can enter a judged frame ───────
    print("  [사분면 프레임 검산] d=2 눈(−2,0,0.3) 기준 방위각 (반각 30° = 프레임 밖)")

    def _bear(a):
        px, py = _pol(b["r_rim"], a)
        return abs(math.degrees(math.atan2(py, px + 2.0)))
    for nm, (a0, a1) in sorted(PARAMS["sector"].items()):
        wb = min(_bear(a0), _bear(a1))
        print(f"    {nm:8s} {a0:6.1f}..{a1:6.1f}° → 최소 방위 {wb:5.1f}° "
              f"({'프레임 안' if wb < 30.0 else '프레임 밖'})")
    for nm in ("tier", "arcade"):
        a0, a1 = PARAMS["sector"][nm]
        wb = min(_bear(a0), _bear(a1))
        gate(f"{nm} 뱅크가 h0.3 프레임 밖", wb >= 30.0, f"{wb:.1f}°")

    # ── 6. near-window occupancy, RE-DERIVED ──────────────────────────────
    print("  [근접창 점유 재유도] W1 = [eye+0.564, eye+2.000] · 화각 60°(반각 30°)")
    g = PARAMS["gkit"]
    mx, _my = g["manhole"]
    occ_ok = True
    for d in (2.0, 5.0, 10.0):
        ex = -d
        w1 = (ex + 0.564, ex + 2.000)
        ahead = mx - ex
        if ahead <= 0.05:
            print(f"    d={d:4.1f} W1 x [{w1[0]:+.3f},{w1[1]:+.3f}] · 맨홀 x{mx:+.2f}"
                  f" = 카메라 뒤 → 점유 0.0 %")
            continue
        half = ahead * math.tan(math.radians(30.0))
        frac = 0.648 / (2.0 * half) * 100.0
        inw1 = w1[0] <= mx <= w1[1]
        occ_ok = occ_ok and frac <= 25.0 and not inw1
        print(f"    d={d:4.1f} W1 x [{w1[0]:+.3f},{w1[1]:+.3f}] · 맨홀 {ahead:.2f} m "
              f"전방 · 프레임 반폭 {half:.3f} → 점유 {frac:5.1f} % · W1 내부 "
              f"{'예' if inw1 else '아니오'}")
    gate("근접창 점유 ≤ 25 % 이고 W1 밖", occ_ok)
    gate("장식 사각 패치 0 (GT-24 어휘)", "patch" not in json.dumps(g))

    # ── 7. raking-light penetration ───────────────────────────────────────
    d = _sun_dir()
    print("  [사광 침투 검산] SUN_AZ_OFFSET="
          f"{PARAMS['SUN_AZ_OFFSET']:.1f}, elev {PARAMS['light']['noon_sun_elev']:.2f}")
    print(f"    광선 진행 d = ({d[0]:+.3f}, {d[1]:+.3f}, {d[2]:+.3f}) → 태양은 "
          f"{'+Y(북)' if -d[1] > 0 else '−Y(남)'} 상공")
    sx = abs(b["floor_z"]) * d[0] / abs(d[2])
    sy = abs(b["floor_z"]) * d[1] / abs(d[2])
    lit = tot = 0
    for aa in range(0, 360, 3):
        rr = 0.5
        while rr < b["r_rim"]:
            px, py = _pol(float(rr), float(aa))
            if _surface_z(px, py) <= b["floor_z"] + 1e-6:
                tot += 1
                if _rad(px - sx, py - sy) <= b["r_rim"]:
                    lit += 1
            rr += 0.5
    frac = (100.0 * lit / tot) if tot else 0.0
    print(f"    림 통과 후 바닥까지 수평 이동 Δ=({sx:+.2f},{sy:+.2f}) → 바닥 직사 "
          f"{frac:.1f} % (샘플 {tot})")
    gate("보울 바닥이 암흑 아님 (직사 ≥ 15 %)", frac >= 15.0)
    print(f"    아레나 중심 천공 반각 "
          f"{math.degrees(math.atan2(b['r_rim'], abs(b['floor_z']))):.0f}° → 돔 간접광 충분")

    # ── 8. camera collision + bed containment (census MD-F7) ──────────────
    boxes = _obstacle_boxes()
    views = build_views()
    print(f"  [카메라 충돌 검산] 뷰 {len(views)}개 × 장애물 {len(boxes)}개 AABB")
    hits = []
    for name, v in sorted(views.items()):
        ex, ey, ez = v["eye"]
        for bn, x0, x1, y0, y1, z0, z1 in boxes:
            if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1:
                hits.append((name, bn))
        s = _solid_at(ex, ey, ez)
        if s is not None:
            hits.append((name, f"{s}(지형 매몰)"))
        for bn in PARAMS["beds"]:
            bd = PARAMS["beds"][bn]
            gz = _surface_z(*_pol((bd["r0"] + bd["r1"]) / 2.0,
                                  (bd["a0"] + bd["a1"]) / 2.0))
            if bed_contains(bn, ex, ey) <= 0.0 \
                    and gz <= ez <= gz + bd["kerb_h"] + 1.20:
                hits.append((name, f"Bed_{bn}(극좌표)"))
    for name, bn in hits:
        print(f"    [FAIL] {name} eye 가 {bn} 내부")
    gate("카메라 충돌 0", not hits)
    # [w3_md_reverts_v1.md §5 MD-F7] scene08 beauty_overview used to sit INSIDE PlazaPlanter_0's
    #   footprint with a live Fraxinus in it (kerb distance 0.00 m, the C02-P1 class). The fix is
    #   a plan fix, not a nudge: every judged eye must stand clear of every bed footprint with a
    #   stated margin, and the margin is asserted here so it cannot silently regress.
    print("  [화단 이격 검산] 판정 시점 ↔ 화단 발자국 평면거리 (census C02-P1 / MD-F7)")
    worst_d, worst_pair = 1e9, ("", "")
    for name, v in sorted(views.items()):
        dd, who = planter_dist(v["eye"][0], v["eye"][1])
        if dd < worst_d:
            worst_d, worst_pair = dd, (name, who)
    print(f"    최근접 쌍 {worst_pair[0]} ↔ {worst_pair[1]} = {worst_d:.3f} m")
    gate("모든 판정 시점이 화단 발자국 밖 (≥ 1.0 m)", worst_d >= 1.0)

    # ── 9. sight-line ray march for the mise-en-scene cuts ────────────────
    print("    [시선 차단] 미장센 컷 ray march (첫 차단 비율 ≥ 0.90 = OK)")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        e = np.array(v["eye"], dtype=float)
        tg = np.array(v["tgt"], dtype=float)
        Ln = float(np.linalg.norm(tg - e))
        frac, hit = 1.0, None
        for k in range(1, int(Ln / 0.1) + 1):
            f = k * 0.1 / Ln
            s = _solid_at(*(e + (tg - e) * f))
            if s is not None:
                frac, hit = f, s
                break
        print(f"      {name:18s} 첫 차단 {frac:5.2f} ({hit if hit else '없음'})")
        if frac < 0.90:
            blocked.append(name)
    gate("미장센 컷 차단 0", not blocked, f"{blocked}" if blocked else "")
    print("    [시선 회랑] x −12..0, |y| ≤ 1.5 에 서 있는 요소")
    intr = [bn for bn, x0, x1, y0, y1, _z0, z1 in boxes
            if not (x1 <= -12.0 or x0 >= 0.0 or y1 <= -1.5 or y0 >= 1.5)
            and z1 > 0.05]
    gate("회랑 침범 0", not intr, f"{intr}" if intr else "")
    for dd in (2.0, 5.0, 10.0):
        e = np.array([-dd, 0.0, 0.3])
        rim = np.array([0.0, 0.0, 0.002])
        dirv = (rim - e) / np.linalg.norm(rim - e)
        pre = None
        for k in range(1, int(30.0 / 0.05)):
            pnt = e + dirv * (k * 0.05)
            s = _solid_at(*pnt)
            if s is not None and pnt[0] < -1e-6:
                pre = s
                break
        print(f"      grid h0.3_d{dd:.0f} 연단 스침 시선 → 연단 전 차단 "
              f"{'없음(OK)' if pre is None else pre + '(FAIL)'}")
        gates.append((f"graze_d{dd:.0f}", pre is None))

    # ── 10. deletions this rebuild owes ───────────────────────────────────
    print("  [삭제 확인] v6 요소가 실제로 사라졌는가")
    src = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    pdump = json.dumps({k: v for k, v in PARAMS.items()
                        if k not in ("material", "light")}, default=str)
    gate("GT-7 임시표지(tempbar) 삭제",
         ("def build_" + "tempbar") not in src and ("temp" + "bar") not in pdump)
    gate("road_lines(도로 없는 차선) 삭제", "road_lines" not in pdump)
    gate("사각 tactile ring + 결손 타일 삭제", ("gap_" + "tiles") not in src)
    gate("x=−18 볼라드 열 → 연석변 재배치",
         isinstance(PARAMS["bollards"], dict) and "r" in PARAMS["bollards"])
    gate("계절: leaf-off 호출 없음 (G8 = 늦봄·만엽)", ("bare=" + "True") not in src)
    gate("사각 개구(v6 pit) 파라미터 소멸", "'pit'" not in pdump and '"pit"' not in pdump)

    # ── verdict ────────────────────────────────────────────────────────────
    nf = sum(1 for _n, c in gates if not c)
    print("-" * 76)
    for n, c in gates:
        if not c:
            print(f"  [FAILED GATE] {n}")
    print(f"[SELFCHECK] scene08 v7 곡선 — 게이트 {len(gates)}개 · 실패 {nf}개 → "
          f"{'PASS' if nf == 0 else 'FAIL'}")
    print("=" * 76)
    return nf


# ===========================================================================
# [C-2] ground_kit plans - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def ground_plan():
    """P3 `sidewalk_block` plan for the upper plaza ring (approach corridor).

    **`("patch", n)` is gone.** GT-24 deleted `sidewalk_block`'s own profile patch row
    library-wide; this scene's local `("patch", 3)` override goes with it rather than being
    converted to `relaid`, because a re-laid unit group needs a cause and G8 shows none.
    """
    g = PARAMS["gkit"]
    b = PARAMS["bowl"]
    return gk.plan_ground(
        "sidewalk_block",
        region=tuple(float(v) for v in g["region"]),
        z=0.0, gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("bowl_near_rim", 0.0)],
        voids=[(b["cx"] - b["r_rim"], b["cy"] - b["r_rim"],
                b["cx"] + b["r_rim"], b["cy"] + b["r_rim"])],
        dists=(2, 5, 10), scene="scene08",
        tactile=(),                  # Sec.12.4 - kept on the scene's own curved arc
        sites=dict(manhole=[tuple(g["manhole"])],
                   gully=[tuple(v) for v in g["gullies"]]),
        overrides=dict(
            pave=dict(step_y=3.0),
            surface=(("crack", 4), ("stain", ("dirt", "gum")), ("weed", 8))),
        seed=int(g["seed"]))


def ground_plan_arena():
    """Arena-floor plan - the single mandatory low-point gully, nothing else."""
    g = PARAMS["gkit"]
    return gk.plan_ground(
        "sidewalk_block",
        region=tuple(float(v) for v in g["arena_region"]),
        z=float(PARAMS["bowl"]["floor_z"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=(), dists=(2, 5, 10), scene="scene08", tactile=(),
        sites=dict(gully=[tuple(g["arena_gully"])]),
        overrides=dict(pave=dict(joint=None),
                       infra=dict(manhole=0, gully=1, gutter_L=0),
                       surface=(), extras=()),
        seed=int(g["seed"]) + 80)


# ===========================================================================
# [D] camera presets: grid_views(gy=0) + 6 mise-en-scene shots
#     **Cut names are preserved from the v6 baseline** so the regression pairing survives the
#     rebuild: a renamed cut reports [MISSING] + [NEW] and drops out of every later comparison.
# ===========================================================================
def build_views():
    """Preset axis = the plaza walk axis +X (approach -> bowl). The cascade head straddles that
    axis, so the h0.3 grid is itself the 'hazard concealment' judgment shot."""
    views = sc.grid_views(0.0)
    # pit_edge: pedestrian standing at the cascade head (h1.55) - the bowl interior is exposed
    views["pit_edge"] = dict(eye=[-1.60, -0.60, 1.55], tgt=[7.00, 1.20, -2.60])
    # open_gap: oblique ALONG the guard to the point where it stops and the cascade head
    #   begins (the B-1 replacement for v6's demolished run). Pilot 2's framing
    #   (eye (−3.20, −6.40, 1.60)) put the tier bank across the middle and the guard end out
    #   of frame — it answered no question, so it was re-sited rather than kept for pairing.
    #   The eye must stand INSIDE the cascade sector (a < 210 deg): at a = 218 it is behind
    #   the guard it is meant to look along, and the smoke run's ray march says so (first
    #   block 0.27 on `Parapet`).
    _ox, _oy = _pol(18.5, 196.0)
    _px, _py = _pol(7.0, 205.0)
    #   tgt z is set 0.30 m ABOVE the cascade top face at that radius (−3.00): aiming at
    #   −3.20 puts the sight line inside the flight and the ray march says so (0.82).
    views["open_gap"] = dict(eye=[_ox, _oy, 2.00], tgt=[_px, _py, -2.70])
    # underground_look: from the arena floor looking back up the cascade at the rim
    views["underground_look"] = dict(eye=[15.20, 1.60, -3.10],
                                     tgt=[3.00, -0.80, 0.60])
    # stair_south: the cascade's south flank descent line (the direct-sun run). The eye
    #   stands on the plaza INSIDE the cascade sector (a = 205 deg), i.e. on the open side of
    #   the guard, so nothing in the B-1 balustrade stands between it and the flight.
    _sx, _sy = _pol(16.5, 205.0)
    _tx, _ty = _pol(8.0, 190.0)
    views["stair_south"] = dict(eye=[_sx, _sy, 2.20], tgt=[_tx, _ty, -2.60])
    # facade_court: oblique ALONG the arcade from the forecourt — columns receding, wood
    #   soffit overhead, shopfronts (weakly emissive) on the right. Pilot 2 aimed this cut
    #   radially at r 11.4 -> 17.0 and got two columns filling the frame with a flat grey
    #   sheet between them; the arcade is a *linear* space and has to be read along.
    ax, ay = _pol(12.0, 232.0)
    tx, ty = _pol(16.2, 262.0)
    views["facade_court"] = dict(eye=[ax, ay, -3.00], tgt=[tx, ty, -3.00])
    # beauty_overview: the G8 composition - high oblique from the near south-west, so the
    #   cascade runs away from the eye, the timber tiers fill the far left and the arcade the
    #   near right. [MD-F7] the eye now stands well clear of every bed footprint in plan.
    views["beauty_overview"] = dict(eye=[-14.0, -16.0, 11.0], tgt=[15.0, 1.0, -2.0])
    return views


# ===========================================================================
# [E] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드        — 개구 너머 보울이 '연속 평면'으로 은닉되는가
 2. pit_edge/open_gap  — 파라펫+유리난간이 끊기는 지점 = 계단 머리(B-1)로 읽히는가
 3. underground_look   — 아레나에서 캐스케이드·티어·림이 곡선으로 읽히는가 (PT)
 4. stair_south        — 캐스케이드 명암 경계(사광 60°)와 측면 튜브 난간
 5. facade_court       — 아케이드 상점 파사드 약발광 (PT 8바운스 전제)
 6. 재질/접지          — 환형 섹터 이음·Z파이팅·부유 없는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        sys.exit(1 if _smoke_report() else 0)

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
    UsdGeom.Xform.Define(stage, "/World/Scene08")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    b = PARAMS["bowl"]
    ROOT = "/World/Scene08"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False,
            rotZ=0.0):
        # rotZ defaults to 0.0, so every pre-GT-85 call site is byte-identical; the flank guard
        # needs it to swing a raked tube (rotY) onto its plan bearing.
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col, rotZ=rotZ)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def SECT(path, r_in, r_out, a0, a1, z_bot, z_top, mtl=None, col=False,
             arc_seg=12):
        """One annular-sector prism — the K4(d) true-sector mesh. This is the scene's plate
        primitive: apart from the CBD backdrop, no axis-aligned ground box survives v7."""
        return sc._annular_sector_mesh(stage, path, b["cx"], b["cy"],
                                       r_in, r_out, a0, a1, z_bot, z_top,
                                       mtl, collider=col, arc_seg=int(arc_seg))

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}

        def tex(role, key, scale, **kw):
            return PBR(f"{ROOT}/Looks/{key}", sc.tex_path(role, "diff"),
                       sc.tex_path(role, "nor"), sc.tex_path(role, "rough"),
                       scale, **kw)

        M["paving"] = tex("paving_interlock", "Paving", sca["paving_interlock"],
                          tint=mp["pave_tint"])
        M["plaza_a"] = tex("plaza_light", "PlazaA", sca["plaza_light"])
        M["plaza_b"] = tex("plaza_lower", "PlazaB", sca["plaza_lower"],
                           tint=mp["plazab_tint"])
        M["band"] = tex("band_dark", "Band", sca["band_dark"])
        M["cwall"] = tex("concrete_wall", "ConcreteWall", sca["concrete_wall"],
                         tint=mp["cwall_tint"])
        M["cfloor"] = tex("concrete_floor", "ConcreteFloor",
                          sca["concrete_floor"])
        M["granite"] = tex("granite_dark", "Granite", sca["granite_dark"])
        M["flag"] = tex("stone_flag", "StoneFlag", sca["stone_flag"],
                        tint=mp["flag_tint"])
        M["asphalt_t"] = tex("asphalt", "AsphaltTex", sca["asphalt"])
        M["wood"] = tex("wood_dark", "Wood", sca["wood_dark"],
                        tint=mp["wood_tint"])
        M["grass"] = tex("grass", "Grass", sca["grass"], tint=mp["grass_tint"])
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # [K5 S06-B 3.] curb-class role — light granite, never `granite_dark`
        M["curb"] = tex("plaza_light", "Curb", 1.0, tint=mp["curb_tint"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        M["parapet"] = tex("concrete_wall", "Parapet", 1.2,
                           tint=mp["parapet_tint"])
        M["cope"] = tex("granite_dark", "Cope", 0.9, tint=mp["cope_tint"])
        M["grime"] = PBR(f"{ROOT}/Looks/Grime",
                         diffuse_color=mp["grime_color"],
                         roughness_const=mp["grime_rough"])
        M["gk_iron"] = PBR(f"{ROOT}/Looks/GKitIron",
                           diffuse_color=(0.10, 0.10, 0.105),
                           metallic=0.55, roughness_const=0.55)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        ar = PARAMS["arcade"]
        M["glass_emis"] = PBR(f"{ROOT}/Looks/GlassEmis",
                              diffuse_color=mp["glass_color"],
                              roughness_const=mp["glass_rough"], metallic=0.0,
                              emission_color=ar["emis"],
                              emission_intensity=ar["emis_int"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["gb_glass"] = PBR(f"{ROOT}/Looks/GlassBal",
                            diffuse_color=mp["gb_color"],
                            roughness_const=mp["gb_rough"], metallic=0.0)
        M["mullion"] = PBR(f"{ROOT}/Looks/Mullion",
                           diffuse_color=mp["mull_color"],
                           metallic=mp["mull_metallic"],
                           roughness_const=mp["mull_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["sign_back"] = PBR(f"{ROOT}/Looks/SignBack",
                             diffuse_color=mp["sign_back_color"],
                             roughness_const=mp["sign_back_rough"])
        for key in ("exit",):
            M[f"sign_{key}"] = PBR(
                f"{ROOT}/Looks/Sign_{key}",
                diff=sc.tex_path(f"sign_{key}", "diff"), uv_mode=True,
                roughness_const=0.45)
        for key, tint in (("city_stone", mp["city_stone_tint"]),
                          ("city_plaster", mp["city_plaster_tint"]),
                          ("city_wall", mp["city_wall_tint"])):
            M[key] = tex("concrete_wall", f"City_{key}", 2.4, tint=tint)
        return M

    # -------------------------------------------------------------------
    # ground beyond the plaza + the carriageway (S06-B)
    # -------------------------------------------------------------------
    def build_ground(M):
        gr = PARAMS["ground"]
        pl = PARAMS["plaza"]
        rd = PARAMS["road"]
        n = int(gr["sectors"])
        step = 360.0 / n
        made = 0
        for i in range(n):
            a0 = i * step
            if _in_sector(a0 + step / 2.0, rd["a0"], rd["a1"]):
                SECT(f"{ROOT}/Road_{i}", pl["r_out"], gr["r_out"], a0,
                     a0 + step, rd["z_top"] - gr["thick"], rd["z_top"],
                     M["asphalt_t"], col=True, arc_seg=int(gr["arc_seg"]))
            else:
                SECT(f"{ROOT}/Ground_{i}", pl["r_out"], gr["r_out"], a0,
                     a0 + step, -gr["thick"], 0.0, M["paving"], col=True,
                     arc_seg=int(gr["arc_seg"]))
            made += 1
        # the two radial returns where the carriageway ends against flush ground
        for tag, a in (("S", rd["a0"]), ("N", rd["a1"])):
            x0, y0 = _pol(pl["r_out"], a)
            x1, y1 = _pol(gr["r_out"], a)
            sc._oriented_box(stage, f"{ROOT}/RoadReturn_{tag}",
                             ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                              rd["z_top"] / 2.0),
                             (0.30, math.hypot(x1 - x0, y1 - y0),
                              abs(rd["z_top"])), M["curb"], rotz=a + 90.0)
            made += 1
        # dashed centre markings, ON the carriageway (they now have a road under them)
        da = (rd["a1"] - rd["a0"] - 8.0) / rd["dash_n"]
        for k in range(int(rd["dash_n"])):
            a0 = rd["a0"] + 4.0 + k * da
            SECT(f"{ROOT}/RoadDash_{k}", rd["dash_r"][0], rd["dash_r"][1],
                 a0, a0 + rd["dash_deg"], rd["z_top"] + 0.002,
                 rd["z_top"] + 0.006, M["paint"], arc_seg=3)
            made += 1
        print(f"[지반] 환형 섹터 {made} 프림 · 차도 호 {rd['a0']:.0f}..{rd['a1']:.0f}° "
              f"(z {rd['z_top']:+.3f})")

    def build_curb(M):
        """[K5 · S06-B] the real 보차도 경계석 the v6 lane lines never had.

        `infra_kit.build_curb_line` is a straight-run builder, so the kerb arc is cut into
        `road.chords` chords and each chord is built inside its own `sc.build_rot_group`, i.e.
        the kit's own 1 m unit rhythm and 10 mm top arris are used verbatim rather than
        re-implemented. `gt_drop` is read back from the builder and printed — this is the scene's
        second declared drop edge and the ledger row quotes THIS number, not an assumed one.
        """
        rd = PARAMS["road"]
        pl = PARAMS["plaza"]
        kit = ik.kit_from_scene_common(sc, stage)
        n = int(rd["chords"])
        gt, blocks, unit = None, 0, None
        for j in range(n):
            a0 = rd["a0"] + (rd["a1"] - rd["a0"]) * j / n
            a1 = rd["a0"] + (rd["a1"] - rd["a0"]) * (j + 1) / n
            p0, p1 = _pol(pl["r_out"], a0), _pol(pl["r_out"], a1)
            mxx, myy = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
            L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            bear = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            grp = sc.build_rot_group(stage, f"{ROOT}/CurbGrp_{j}",
                                     (mxx, myy), bear)
            try:
                res = ik.build_curb_line(
                    kit, f"{grp}/Curb", (mxx - L / 2.0, myy),
                    (mxx + L / 2.0, myy), M["curb"], height=rd["curb_h"],
                    width=rd["curb_w"], unit=rd["curb_unit"],
                    z_road=rd["z_top"], walk_z=0.0, gutter=False,
                    arris="look", joint_mtl=M["grime"], strict=False)
            except Exception as e:
                print(f"[K5][경고] 연석 현 {j} 실패: {e}")
                continue
            if isinstance(res, dict):
                gt = res.get("gt_drop", gt)
                blocks += int(res.get("n_blocks", 0) or 0)
                unit = res.get("unit_actual", unit)
        print(f"[K5] 연석 {n} 현 · 유닛블록 {blocks} (실측 유닛 "
              f"{unit if unit is None else round(float(unit), 3)} m) · "
              f"gt_drop {gt if gt is None else round(float(gt), 4)} "
              f"(= 연석 노출 {rd['curb_h']:.3f} + 거터 낙차; 이 값이 원장 행의 근거다)")
        return gt

    # -------------------------------------------------------------------
    # upper plaza ring deck — curved paving bands (no rectangle anywhere)
    # -------------------------------------------------------------------
    def build_plaza(M):
        pl = PARAMS["plaza"]
        n = int(pl["sectors"])
        step = 360.0 / n
        for i in range(n):
            path = f"{ROOT}/PlazaRing_{i}"
            # [W2-0 P-A] the sectors ground_kit decorates keep no displacement skin
            sc.skin_exclude(path)
            SECT(path, b["r_rim"], pl["r_out"], i * step, (i + 1) * step,
                 -pl["thick"], 0.0, M["paving"], col=True,
                 arc_seg=int(pl["arc_seg"]))
        for j, (r0, r1, mkey) in enumerate(pl["bands"]):
            SECT(f"{ROOT}/PlazaBand_{j}", r0, r1, 0.0, 360.0,
                 -0.004, 0.006, M[mkey], arc_seg=64)
        print(f"[상부광장] 링 섹터 {n} + 곡선 포장 밴드 {len(pl['bands'])} "
              f"(r {b['r_rim']:.0f}..{pl['r_out']:.0f})")

    def build_flat_fill(M):
        """hazard_stairs=False control: fill the bowl so the whole plaza is z=0 flat ground."""
        SECT(f"{ROOT}/FlatBowl", 0.001, b["r_rim"], 0.0, 360.0,
             -PARAMS["plaza"]["thick"], 0.0, M["paving"], col=True, arc_seg=64)

    # -------------------------------------------------------------------
    # the bowl — floor, cascade, tiers, arcade, control wall
    # -------------------------------------------------------------------
    def build_bowl_floor(M):
        ar = PARAMS["arcade"]
        sec = PARAMS["sector"]
        SECT(f"{ROOT}/Arena", 0.001, b["r_arena"], 0.0, 360.0,
             b["floor_z"] - b["floor_thick"], b["floor_z"], M["flag"],
             col=True, arc_seg=48)
        for tag, (a0, a1), r_out in (("Ctrl", sec["ctrl"], b["r_rim"]),
                                     ("Arc", sec["arcade"], ar["r_shop"])):
            SECT(f"{ROOT}/Forecourt_{tag}", b["r_arena"], r_out, a0, a1,
                 b["floor_z"] - b["floor_thick"], b["floor_z"], M["flag"],
                 col=True, arc_seg=36)
        # circular granite inlay at the bowl centre (G8's dark disc). A CIRCLE, deliberately:
        #   the user's ban is on decorative rectangles, and a disc repeats the plaza's own plan.
        SECT(f"{ROOT}/ArenaInlay", 0.001, 2.20, 0.0, 360.0,
             b["floor_z"] - 0.004, b["floor_z"] + 0.006, M["granite"],
             arc_seg=48)
        rr, j = b["r_arena"], 0
        while rr < ar["r_shop"] - 0.6:
            r1 = min(rr + 2.20, ar["r_shop"])
            # 0.494 vs 0.306 `[measured]` — a 1.6:1 step, the grey/화강석 pair G8 shows.
            # The first pilot alternated 0.710 against 0.318 at 1.30 m and read as a bullseye.
            mkey = "plaza_b" if j % 2 == 0 else "granite"
            for tag, (a0, a1), lim in (("Ctrl", sec["ctrl"], b["r_rim"]),
                                       ("Arc", sec["arcade"], ar["r_shop"])):
                if rr >= lim:
                    continue
                SECT(f"{ROOT}/FloorBand_{tag}_{j}", rr, min(r1, lim), a0, a1,
                     b["floor_z"] - 0.004, b["floor_z"] + 0.006, M[mkey],
                     arc_seg=36)
            rr, j = r1, j + 1
        print(f"[보울 바닥] 아레나 r{b['r_arena']:.2f} + 전정 2 + 원형 인레이 + "
              f"곡선 밴드 {j}")

    def build_cascade(M):
        """The granite cascade on the walk axis — 29 annular-sector courses + a mid landing.

        `sc.build_arc_steps(..., seg=1, mesh=True, arc_seg=N)` is the K4(d) true-sector path: one
        mesh per course spanning the whole 60 deg sector, faceted `arc_seg` times, with the
        neighbouring courses sharing their rays exactly. The box convention's 1.03 chord cover
        (and the wedge gaps it exists to hide) is not merely reduced here — it is unnecessary.
        """
        cs = PARAMS["cascade"]
        a0, a1 = PARAMS["sector"]["cascade"]
        mtl = M["granite"] if cfg["cue_material_break"] else M["paving"]
        courses, _r = cascade_courses()
        for i, (r_in, r_out, tz, kind) in enumerate(courses):
            sc.build_arc_steps(stage, f"{ROOT}/Cascade_{i}", b["cx"], b["cy"],
                               r_in, r_out, a0, a1, 1, tz, b["bank_base"],
                               M["flag"] if kind == "L" else mtl,
                               collider=True, mesh=True,
                               arc_seg=int(cs["arc_seg"]))
        if cfg["cue_nosing"]:
            for i, (r_in, _r_out, tz, kind) in enumerate(courses):
                if kind == "L":
                    continue
                SECT(f"{ROOT}/CascadeNosing_{i}", r_in, r_in + 0.05, a0, a1,
                     tz - 0.001, tz + 0.001, M["paint"],
                     arc_seg=int(cs["arc_seg"]))
        print(f"[캐스케이드] {len(courses)} 코스 (A {cs['n_flight_a']} · 계단참 1 · "
              f"B {cs['n_built']-cs['n_flight_a']}) · 섹터 {a0:.0f}..{a1:.0f}° · "
              f"riser {cs['riser']:.3f} / tread {cs['tread']:.3f} → R1 면제")

    def build_tiers(M):
        """Timber seating tiers — G8's amphitheatre bank. Seating, not circulation."""
        tp = PARAMS["tiers"]
        a0, a1 = PARAMS["sector"]["tier"]
        courses, _r = tier_courses()
        for i, (r_in, r_out, tz) in enumerate(courses):
            sc.build_arc_steps(stage, f"{ROOT}/TierCore_{i}", b["cx"], b["cy"],
                               r_in, r_out, a0, a1, 1, tz - tp["plank_t"],
                               b["bank_base"], M["cfloor"], collider=True,
                               mesh=True, arc_seg=int(tp["arc_seg"]))
            SECT(f"{ROOT}/TierDeck_{i}", r_in, r_out - 0.03, a0, a1,
                 tz - tp["plank_t"], tz, M["wood"], arc_seg=int(tp["arc_seg"]))
        print(f"[티어 뱅크] {len(courses)} 코스 · riser {tp['riser']:.3f} / tread "
              f"{tp['tread']:.3f} (관람석) · 섹터 {a0:.0f}..{a1:.0f}°")

    def build_ctrl_wall(M):
        """The far, on-axis retaining wall — the surface the h0.3 illusion is read against."""
        c = PARAMS["ctrl"]
        a0, a1 = PARAMS["sector"]["ctrl"]
        SECT(f"{ROOT}/CtrlWall", b["r_rim"] - c["wall_t"], b["r_rim"], a0, a1,
             b["bank_base"], 0.0, M["cwall"], col=True,
             arc_seg=int(c["arc_seg"]))
        # base grime band — the one piece of ageing that still reads at 28 m
        SECT(f"{ROOT}/CtrlGrime", b["r_rim"] - c["wall_t"] - 0.006,
             b["r_rim"] - c["wall_t"] + 0.001, a0, a1,
             b["floor_z"], b["floor_z"] + 0.32, M["grime"],
             arc_seg=int(c["arc_seg"]))

    def build_arcade(M):
        """Retail arcade under a curved ring deck (G8's right-hand side).

        Section, outward: shopfront wall r 17.0 -> covered walk 3.0 m -> column line r 14.60 ->
        deck edge r 14.00. Clear height 3.70 m (deck soffit −0.80 to floor −4.50).
        """
        ar = PARAMS["arcade"]
        a0, a1 = PARAMS["sector"]["arcade"]
        SECT(f"{ROOT}/ShopWall", ar["r_shop"], ar["r_shop"] + ar["shop_t"],
             a0, a1, b["bank_base"], 0.0, M["cwall"], col=True, arc_seg=24)
        n = int(ar["bays"])
        span = (a1 - a0) / n
        for i in range(n):
            aa = a0 + i * span
            SECT(f"{ROOT}/Shop/Glass_{i}", ar["r_shop"] - 0.05,
                 ar["r_shop"] + 0.01, aa + 0.6, aa + span - 0.6,
                 ar["glass_z0"], ar["glass_z1"], M["glass_emis"], arc_seg=4)
        for i in range(n + 1):
            aa = a0 + i * span
            SECT(f"{ROOT}/Shop/Mull_{i}", ar["r_shop"] - 0.10,
                 ar["r_shop"] - 0.02, aa - 0.3, aa + 0.3,
                 ar["glass_z0"] - 0.05, ar["glass_z1"] + 0.05, M["mullion"],
                 arc_seg=2)
        SECT(f"{ROOT}/Shop/Sill", ar["r_shop"] - 0.16, ar["r_shop"] + 0.02,
             a0, a1, ar["glass_z0"] - ar["sill_h"], ar["glass_z0"],
             M["cwall"], arc_seg=24)
        SECT(f"{ROOT}/Shop/Lintel", ar["r_shop"] - 0.16, ar["r_shop"] + 0.02,
             a0, a1, ar["glass_z1"], ar["glass_z1"] + 0.34, M["cwall"],
             arc_seg=24)
        # one continuous transom — without it the shopfront renders as a single flat sheet
        # of grey, which is the "facade billboard" defect in miniature
        SECT(f"{ROOT}/Shop/Transom", ar["r_shop"] - 0.11, ar["r_shop"] - 0.01,
             a0, a1, ar["glass_z0"] + 2.10, ar["glass_z0"] + 2.19, M["mullion"],
             arc_seg=24)
        for i in range(int(ar["n_col"])):
            aa = a0 + (a1 - a0) * (i + 0.5) / ar["n_col"]
            cx, cy = _pol(ar["r_col"], aa)
            CYL(f"{ROOT}/ArcadeCol_{i}", (cx, cy, (b["floor_z"] - 0.80) / 2.0),
                ar["col_r"], abs(b["floor_z"]) - 0.80, M["cwall"], col=True)
        r0, r1, k = b["r_rim"], ar["r_shop"], int(ar["n_slat"])
        for i in range(k):
            ra = r0 + (r1 - r0) * i / k
            rb = r0 + (r1 - r0) * (i + 1) / k
            SECT(f"{ROOT}/ArcadeSoffit_{i}", ra + 0.03, rb - 0.03, a0, a1,
                 -0.80 - ar["soffit_t"], -0.80, M["wood"], arc_seg=24)
        SECT(f"{ROOT}/ArcadeFascia", b["r_rim"] - 0.02, b["r_rim"] + 0.30,
             a0, a1, -0.86, 0.0, M["cwall"], arc_seg=24)
        print(f"[아케이드] 상점 {n} 베이 · 기둥 {ar['n_col']} · 소핏 슬랫 {k} · "
              f"유효고 {abs(b['floor_z']) - 0.80:.2f} m")

    # -------------------------------------------------------------------
    # cues — the B-1 guard, flank railings, tactile arc
    # -------------------------------------------------------------------
    def build_guard(M):
        """Continuous parapet upstand + `props_kit.build_glass_balustrade` over 210..450 deg.

        The G8 template is used **verbatim**: the kit builds one axis-aligned bay
        (`sc.add_box(seg_len, panel_t, panel_h)` + a `rotY=90` cap), so every chord is mounted in
        its own `sc.build_rot_group` at the chord bearing and the kit runs in that local frame.
        Finding **S08-F1** (reported, not fixed here — kits are frozen this window): the kit
        cannot be called directly on a non-X-aligned polyline, because the panel box and the cap
        cylinder are both authored on world axes. The rot-group mount is the correct client-side
        workaround; the kit should grow a `bearing`/`rotz` kwarg.
        """
        pr = PARAMS["parapet"]
        SECT(f"{ROOT}/Parapet", b["r_rim"], b["r_rim"] + pr["t"],
             pr["a0"], pr["a1"], 0.0, pr["h"] - pr["cope_h"], M["parapet"],
             col=True, arc_seg=int(pr["arc_seg"]))
        SECT(f"{ROOT}/ParapetCope", b["r_rim"] - pr["cope_over"],
             b["r_rim"] + pr["t"] + pr["cope_over"], pr["a0"], pr["a1"],
             pr["h"] - pr["cope_h"], pr["h"], M["cope"],
             arc_seg=int(pr["arc_seg"]))
        n = int(pr["chords"])
        made = dict(panel=0, shoe=0, cap=0)
        r_gb = b["r_rim"] + pr["t"] / 2.0
        for j in range(n):
            a0 = pr["a0"] + (pr["a1"] - pr["a0"]) * j / n
            a1 = pr["a0"] + (pr["a1"] - pr["a0"]) * (j + 1) / n
            p0, p1 = _pol(r_gb, a0), _pol(r_gb, a1)
            mxx, myy = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
            L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            bear = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            grp = sc.build_rot_group(stage, f"{ROOT}/GBGrp_{j}",
                                     (mxx, myy), bear)
            r = pk.build_glass_balustrade(
                stage, f"{grp}/GB",
                [(mxx - L / 2.0, myy), (mxx + L / 2.0, myy)],
                lambda _x, _y: pr["h"], M["gb_glass"], M["rail"],
                shoe_mtl=M["rail"], panel_h=pr["panel_h"],
                panel_t=pr["panel_t"], panel_len=pr["panel_len"],
                joint=pr["joint"], cap_r=pr["cap_r"], shoe_h=pr["shoe_h"])
            for key in made:
                made[key] += int(r.get(key, 0))
        print(f"[가드 B-1] 파라펫 호 {pr['a0']:.0f}..{pr['a1']:.0f}° (개구 = 캐스케이드 "
              f"머리 {PARAMS['sector']['cascade'][0]:.0f}.."
              f"{PARAMS['sector']['cascade'][1]:.0f}°) · 유리 패널 {made['panel']} · "
              f"캡 {made['cap']} · 슈 {made['shoe']}")

    def build_flank_rails(M):
        """R2 — a **raked** tube guard on each cascade flank, built in-scene [GT-85].

        `props_kit.build_tube_railing` samples the ground once per polyline segment and lays
        every rail with `rotY=90`, so on this 4.400 m descent it produced level tubes hanging
        over posts that tracked the stair. The kit's SECTION is kept verbatim (4 rails, 0.120 m
        bottom offset, tube 0.024 / post 0.030 -> clear span 0.279 m); only the geometry is
        rebuilt, the same client move scene06 makes for its spiral guard.

        Closure rules, and every one of them is asserted in the smoke run:
          - rails are offsets from `flank_datum`, so the guard is one height over the stair;
          - each post runs from the surface under it up to the top rail's CROWN, so the tube is
            fully engaged in the post (post_r 0.030 > tube_r 0.024) and no post finishes short;
          - every rail run ends on a post axis, so no cut face is exposed and every mitre is
            hidden inside a newel — except the landing foot, which takes an elbow because a post
            there would straddle a riser;
          - both ends are level handrail extensions dying into an end newel on flat ground.
        """
        fr = PARAMS["flank_rail"]
        r_head, r_a, r_l, r_foot = flank_nodes()
        nodes = [r_head + fr["ext"], r_head, r_a, r_l, r_foot,
                 r_foot - fr["ext"]]
        posts = flank_posts()
        offs = flank_rail_offsets()
        # rake angle of each rail run, one per node interval. Constant over a flank, so it is
        # derived once rather than per rail.
        elevs = [math.degrees(math.atan2(flank_datum(nodes[j + 1])
                                         - flank_datum(nodes[j]),
                                         nodes[j] - nodes[j + 1]))
                 for j in range(len(nodes) - 1)]
        # Landing-foot elbow radius. Two tubes deflected by `dfl` leave a V whose outermost
        # point sits tube_r / cos(dfl/2) from the node, so a tube_r sphere would leave the
        # outside of the bend open by 0.7 mm; this closes it exactly
        # `[computed 0.02466 m at dfl 26.565 deg]` and bulges 2.7 % of a tube radius, which is
        # what a welded elbow does anyway.
        elb_r = fr["tube_r"] / math.cos(math.radians(
            abs(elevs[3] - elevs[2]) / 2.0))
        n_p = n_r = n_e = 0
        for tag, a in flank_azimuths():
            grp = f"{ROOT}/FlankGrp_{tag}"
            UsdGeom.Xform.Define(stage, grp)
            bear = a + 180.0            # the run descends INWARD along the flank ray
            for i, rr in enumerate(posts):
                px, py = _pol(rr, a)
                z0 = _surface_z(px, py)
                z1 = flank_datum(rr) + fr["rail_h"] + fr["tube_r"]
                CYL(f"{grp}/Post_{i}", (px, py, (z0 + z1) / 2.0),
                    fr["post_r"], z1 - z0, M["rail"], col=True)
                n_p += 1
            for j in range(len(nodes) - 1):
                ra, rb = nodes[j], nodes[j + 1]
                pa, pb = _pol(ra, a), _pol(rb, a)
                run = ra - rb                       # plan length, outward -> inward
                rise = flank_datum(rb) - flank_datum(ra)
                # rotY lays the cylinder's local Z along +X and tilts it to the rake; rotZ then
                # swings that raked tube onto the ray bearing (sc.add_cylinder op order).
                elev = elevs[j]
                for k, off in enumerate(offs):
                    za = flank_datum(ra) + off
                    zb = flank_datum(rb) + off
                    CYL(f"{grp}/Rail_{k}_{j}",
                        ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0,
                         (za + zb) / 2.0),
                        fr["tube_r"], math.hypot(run, rise), M["rail"],
                        rotY=90.0 - elev, rotZ=bear)
                    n_r += 1
            ex, ey = _pol(r_l, a)
            for k, off in enumerate(offs):
                sc.add_sphere(stage, f"{grp}/Elbow_{k}",
                              (ex, ey, flank_datum(r_l) + off),
                              (elb_r,) * 3, M["rail"])
                n_e += 1
        bay = max(posts[i] - posts[i + 1] for i in range(len(posts) - 1))
        clear = ((fr["rail_h"] - fr["bottom"]) / max(1, int(fr["rails"]) - 1)
                 - 2.0 * fr["tube_r"])
        print(f"[측면 난간 R2] 양 플랭크 · 지주 {n_p} · 레일 {n_r} · 엘보 {n_e} · "
              f"최대 지주 간격 {bay:.2f} m (≤ {fr['post_pitch']:.2f}) · 레일 안목 "
              f"{clear:.3f} m · 디딤코선 기준 난간고 {fr['rail_h']:.2f} m · "
              f"양단 수평연장 {fr['ext']:.2f} m")

    def build_tactile_arc(M):
        """cue_tactile — a curved warning band at the cascade head only.

        R16-2 (stair-cue-first): this scene carries **no stop-type device**. The band is the true
        stair cue at the statutory 0.30 m setback from the first riser, 0.60 m deep, and it is an
        **arc**: v6's rectangular ring with two deliberately missing tiles is deleted with the
        rectangle it was drawn on.
        """
        tc = PARAMS["tactile"]
        a0, a1 = PARAMS["sector"]["cascade"]
        r1 = b["r_rim"] + tc["setback"]
        SECT(f"{ROOT}/TactileHead", r1, r1 + tc["depth"], a0 + 1.0, a1 - 1.0,
             -0.004, tc["proud"], M["tactile"], arc_seg=int(tc["arc_seg"]))

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P3 sidewalk_block (plaza ring) + arena gully
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["granite"], crack=M["granite"], patch=M["paving"],
                  patch_cut=M["granite"], manhole=M["gk_iron"],
                  gully=M["gk_iron"], gutter=M["cwall"], stain_dirt=M["grime"],
                  stain_gum=M["grime"], weed=M["grass"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                              skin_exclude=sc.skin_exclude)
        arena = gk.apply_ground(kit, f"{ROOT}/GKitArena", ground_plan_arena(),
                                M2, skin_exclude=sc.skin_exclude)
        print(f"[ground_kit] scene08 P3 · 프림 {res['prims']} + 아레나 "
              f"{arena['prims']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']} · patch 0 (GT-24)")
        return res

    def build_signs(M):
        """[v5.2 user] Arbitrary warning signs removed — 1 facility sign only."""
        sg = PARAMS["sign_exit"]
        cx, cy = _pol(sg["r"], sg["a"])
        sc.build_sign(stage, f"{ROOT}/Sign_exit", cx, cy, sg["z"], sg["yaw"],
                      panel_mtl=M["sign_exit"], w=sg["w"], h=sg["h"],
                      pole_h=sg["pole_h"], pole_mtl=M["bollard"],
                      back_mtl=M["sign_back"])

    # -------------------------------------------------------------------
    # dressing — curved planting beds, benches, lights, bollards
    # -------------------------------------------------------------------
    def build_bed(M, name, bd):
        """An annular planting bed: kerb ring + soil + shrubs (+ trees) on the bed arc.

        Beds inside the bowl are **arcs, never squares** — a square bed on a circular plaza is
        exactly the v6 shape the user asked to be removed, and `sc.build_planter` can only build
        squares. The four street-tree beds on the outer ring stay square: a kerbed street bed on
        a straight footway edge is rectangular in reality, and the ban is on decorative ground
        patterns, not on kerbs.
        """
        r0, r1, a0, a1 = bd["r0"], bd["r1"], bd["a0"], bd["a1"]
        gz = _surface_z(*_pol((r0 + r1) / 2.0, (a0 + a1) / 2.0))
        t = 0.22
        for tag, ra, rb in (("In", r0, r0 + t), ("Out", r1 - t, r1)):
            SECT(f"{ROOT}/Bed_{name}/Kerb{tag}", ra, rb, a0, a1,
                 gz - 0.30, gz + bd["kerb_h"], M["flag"], col=True, arc_seg=20)
        SECT(f"{ROOT}/Bed_{name}/EndA", r0, r1, a0, a0 + 1.4,
             gz - 0.30, gz + bd["kerb_h"], M["flag"], col=True, arc_seg=3)
        SECT(f"{ROOT}/Bed_{name}/EndB", r0, r1, a1 - 1.4, a1,
             gz - 0.30, gz + bd["kerb_h"], M["flag"], col=True, arc_seg=3)
        SECT(f"{ROOT}/Bed_{name}/Soil", r0 + t, r1 - t, a0 + 1.4, a1 - 1.4,
             gz - 0.10, gz + bd["soil_h"], M["grass"], arc_seg=20)
        top = gz + bd["soil_h"]
        rm = (r0 + r1) / 2.0
        pts = []
        for i in range(int(bd["n_shrub"])):
            aa = a0 + 2.5 + (a1 - a0 - 5.0) * i / max(1, bd["n_shrub"] - 1)
            px, py = _pol(rm + (0.22 if i % 2 else -0.22), aa)
            pts.append((px, py, top))
        sc.place_shrubs(stage, f"{ROOT}/Bed_{name}/Shrub", pts, target_h=0.80,
                        pool=sc.SHRUB_ORNAMENT,
                        seed=abs(hash(name)) % 99991, species="ornament_bed")
        for i in range(int(bd["n_tree"])):
            aa = a0 + 6.0 + (a1 - a0 - 12.0) * i / max(1, bd["n_tree"] - 1)
            px, py = _pol(rm, aa)
            # [K4(b)] species is a declaration, not a draw: scene08 = `ash` (Fraxinus), the
            #   civic-plaza row it shares with scene05. Season is late spring (G8) -> no `bare=`.
            sc.build_tree(stage, f"{ROOT}/Bed_{name}/Tree_{i}", px, py, top,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          species="ash")

    def build_dressing(M):
        for name, bd in PARAMS["beds"].items():
            build_bed(M, name, bd)
        pp = PARAMS["plaza_planter"]
        for i, (a, r) in enumerate(PARAMS["plaza_planters"]):
            cx, cy = _pol(r, a)
            sc.build_planter(stage, f"{ROOT}/PlazaPlanter_{i}", cx, cy, 0.0,
                             M["cwall"], M["grass"], size=pp["size"],
                             tree_mtls=(M["wood"], M["canopy_a"],
                                        M["canopy_b"]))
        ab = PARAMS["arena_benches"]
        for i in range(int(ab["n"])):
            aa = ab["a0"] + (ab["a1"] - ab["a0"]) * (i + 0.5) / ab["n"]
            cx, cy = _pol(ab["r"], aa)
            pk.build_bench_slat(stage, f"{ROOT}/ArenaBench_{i}", cx, cy,
                                b["floor_z"], M["wood"], frame_mtl=M["rail"],
                                yaw=aa + 90.0)
        for i, (a, r, yaw) in enumerate(PARAMS["plaza_benches"]):
            cx, cy = _pol(r, a)
            pk.build_bench_slat(stage, f"{ROOT}/PlazaBench_{i}", cx, cy, 0.0,
                                M["wood"], frame_mtl=M["rail"], yaw=a + yaw)
        sl = PARAMS["streetlight"]
        for i, (a, r) in enumerate(PARAMS["streetlights"]):
            lx, ly = _pol(r, a)
            ax, ay = _pol(r - sl["arm_len"], a)          # arm points at the bowl
            CYL(f"{ROOT}/Streetlight_{i}/Pole", (lx, ly, sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["bollard"], col=True)
            BOX(f"{ROOT}/Streetlight_{i}/Head",
                (ax, ay, sl["pole_h"] - 0.18),
                (sl["head"], sl["head"], 0.13), M["lamp"])
        bl = PARAMS["bollards"]
        for i in range(int(bl["n"])):
            aa = bl["a0"] + (bl["a1"] - bl["a0"]) * i / max(1, bl["n"] - 1)
            cx, cy = _pol(bl["r"], aa)
            pk.build_bollard_v2(stage, f"{ROOT}/Bollard_{i}", cx, cy, 0.0,
                                M["bollard"], band_mtl=M["lamp"])

    def build_backdrop(M):
        """BS-4 — the CBD wall G8 closes the horizon with, `kind="backdrop"` (3-4 prims each)."""
        bp = PARAMS["backdrop"]
        try:
            eyes = bk.judged_eyes(0.0)
            # the injection container lives in `facade_kit`, not `building_kit` — the
            # scene16 BS-4 precedent, verified live rather than assumed.
            kit = fk.Kit(sc.add_box, sc.add_cylinder,
                         getattr(sc, "_oriented_box", None))
        except Exception as e:
            eyes, kit = None, None
            print(f"[backdrop][경고] building_kit 진입 실패 → 폴백: {e}")
        n_tot = 0
        for i, row in enumerate(bp["blocks"]):
            x0, x1, y0, y1, h, floors, axis, facade, face_dir, mkey = row
            bd = dict(x0=x0, x1=x1, y0=y0, y1=y1, h=h, floors=floors,
                      axis=axis, base_z=bp["base_z"], face_dir=face_dir)
            bd["facade_x" if axis == "x" else "facade_y"] = facade
            done = False
            if kit is not None:
                try:
                    # BS-4 forces `kind="backdrop"` only for blocks the judged eyes cannot
                    # frame; these stand 30-46 m from the beauty eye and DO frame, so the
                    # tier is left to `plan_building`/`should_backdrop` rather than pinned.
                    p = bk.plan_building(bd, eyes=eyes)
                    prims = bk.build_korean_building(
                        kit, stage, f"{ROOT}/CityBlock_{i}", bd,
                        bk.Mtls(M[mkey], parapet=M["parapet"]), plan=p)
                    n_tot += len(prims)
                    print(f"[backdrop] {i} kind {p.kind} / tier {p.tier} · d_true "
                          f"{p.d_true:5.1f} m · in_frame {p.in_frame} · 프림 {len(prims)}")
                    done = True
                except Exception as e:
                    print(f"[backdrop][경고] {i} → build_building 폴백: {e}")
            if not done:
                sc.build_building(stage, f"{ROOT}/CityBlock_{i}", bd,
                                  M[mkey], M["glass"], M["parapet"],
                                  window=PARAMS["window"])
                n_tot += 1
        print(f"[backdrop] CBD 벽 {len(bp['blocks'])} 동 · 프림 {n_tot}")

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    build_plaza(M)
    if cfg["hazard_stairs"]:
        build_bowl_floor(M)
        build_cascade(M)
        build_tiers(M)
        build_ctrl_wall(M)
        build_arcade(M)
        build_ground_kit(M)
        if cfg["cue_railing"]:
            build_guard(M)
            build_flank_rails(M)
        if cfg["cue_tactile"]:
            build_tactile_arc(M)
        if cfg["cue_sign"]:
            build_signs(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_curb(M)
        build_dressing(M)
        build_backdrop(M)

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene08_{ts}.png")
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
