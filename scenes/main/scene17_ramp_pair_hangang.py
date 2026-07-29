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
  grade 8%), taking the same 3.2 m drop at different grades — the contrast-pair intent
  is unchanged, only the terrain was replaced with a real Han river section.
  Dropped: the zigzag 2 flights · paired lanes (lane A/B) · separate parapet ·
  the 3 retaining-wall opening segments.

Hazard
  Looking +X from the levee path (z=0) at robot eye height h0.3, the sight line grazing
  the crest shoulder (x=0) is far gentler than the bank (50% average), so **the bank,
  the stairs and the terrace all disappear from view** and only the far side of the
  terrace (x >= 21) is left on the horizon -> it reads as one continuous plane with the
  near grass. There is no guard (Han river levee stairs are unrailed by custom). The
  river-side edge of the diagonal ramp is only a kerb (h0.15) on a 1.5 m stone
  revetment — a below-code reality.

Goal
  (1) levee crest (sidewalk 3 + bike road 3) + crest kerb
  (2) grass bank as a 7-segment polyline (shoulder rounding 25.7% -> 60% at the
      bottom, 50% average = 1:2), built as 2 Y bands that leave only the stair width
      (y +-1.5) open — segments overlap by margin so no gap can open
  (3) 20 stair steps (riser 0.16 · tread 0.32 · width 3) cutting straight through
  (4) diagonal ramp: a single build_slope inside rot_group (yaw 80.7931 deg) — length
      40 m, grade 8%, width 2.5, uphill cut face (max 0.30 m) · river-side stone
      revetment (max 1.53 m)
  (5) terrace (promenade width 3 + grass + benches + silver grass) · riprap revetment ·
      broad water · 4 apartment blocks across · bridge (existing PARAMS reused)

Walking-continuity self-check table (both routes: levee path z=0 -> terrace z=−3.2)
  ┌ #  section               coord (x, y, z)            step / verdict
  │ A0 levee bike road       (−1.50,  −6.00,  0.000)    flat
  │ A1 crest shoulder (edge) ( 0.00,   0.00,  0.000)    ← **drop 3.20, no railing**
  │ A2 stair step 1          ( 0.32,   0.00, −0.160)    0.160
  │ A3 stair step 20         ( 6.40,   0.00, −3.200)    0.160 x 19
  │ A4 terrace grass         ( 7.20,   0.00, −3.200)    flat (flush with stair foot)
  │ A5 promenade             (13.00,   0.00, −3.200)    flat
  ├ B0 levee crest           (−0.60,   4.10,  0.000)    flat
  │ B1 ramp uphill start     ( 0.59,   3.90,  0.000)    0.152 threshold vs crest end
  │                                                     ([v7] old apron prim removed —
  │                                                      see PARAMS["ramp"]["apron"])
  │ B2 ramp s=10             ( 3.43,  13.58, −0.800)    grade 8%
  │ B3 ramp s=25             ( 5.83,  28.38, −2.000)    grade 8%
  │ B4 ramp end s=40         ( 8.23,  43.19, −3.200)    grade 8% -> flush with terrace
  └ B5 promenade merge       (13.00,  43.00, −3.200)    flat
  * Both routes drop the same 3.20 — the basis of the contrast pair. Stairs 50% vs ramp 8%.

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
    levee=dict(x0=-24.0, x1=0.0, y0=-30.0, y1=48.0, z_top=0.0, thick=3.6),
    crown_walk=dict(x0=-7.5, x1=-4.5, proud=0.006, embed=0.06),   # sidewalk (interlocking)
    crown_green=dict(x0=-4.5, x1=-4.0, top=0.000, embed=0.10),    # 0.5 planting separation strip
    crown_bike=dict(x0=-4.0, x1=0.0, proud=0.006, embed=0.06),    # bike road (asphalt)
    crown_line=dict(x=-2.0, w=0.10, seg=2.4, gap=2.0, z=0.008),   # bike road centre dashed line

    # ═══ [W2-D ground_kit] P13 levee_paved — spec §5.9 scene17 row ═══════════
    #  (3) construction joints 3 m + patches · (4) interlock joints incised 2 mm (profile default) ·
    #  (6) drainage + gullies · (7) 1 manhole (W1) · (10) tread-wear lane.
    #  * Deviation from (6) "L-shaped gutter": `build_gutter_L` is a **carriageway edge**
    #    detail and `_compose_ops` always lays it at y = const spanning x0..x1,
    #    i.e. **across** the crown. Here the road runs along **Y** (the levee),
    #    so a y=const gutter would be perpendicular to the road it drains.
    #    The same drainage function is carried by a **linear trench drain at
    #    x = -4.15** (the bike road's landward edge, against the planting
    #    strip) which the kit can orient correctly. `gutter_L` is set to 0.
    #    GT-E2 check: the trench sits 4.15 m in front of the crest, so at d5 it
    #    is at X=0.85 and at d10 at X=5.85 — both **outside** the E band
    #    [0.7d, 2.2d], i.e. it is never judged as a near-edge transverse line
    #    [computed].
    #  * (5) "block settlement +-3 mm (2x2 units)" is **not** placed here: it is a per-unit
    #    perturbation of the paving cell, which §4.4 assigns to T1 (MDL unit
    #    jitter). The kit's job is the ledger — unit_cell 0.200 / origin (0,0)
    #    is handed over by `plan_ground`.
    gkit=dict(
        region=(-7.5, -6.0, 0.0, 6.0),        # crown hard surface only
        manholes=[(-2.00, 1.20)],             # 1 unit, d5 near window
        gullies=[(-4.15, -5.50), (-4.15, 5.50)],
        trench=(-4.15, -4.80, 4.80),          # bike/green boundary drain
        patches=[(-1.15, -0.55), (-5.60, 2.20), (-3.10, -3.40), (-6.40, -1.10)],
        wear_lane=((-6.00, -6.0), (-6.00, 6.0)),   # sidewalk wear axis (runs in Y)
    ),
    # Crest-end kerb — open at the stair gap (y +-1.5) and the ramp entry apron (y 2.6..4.4)
    cope=dict(x0=-0.20, x1=0.05, h=0.05,
              y_segs=((-30.0, -1.5), (1.5, 2.6), (4.4, 48.0))),
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
    #     length 40 m · grade 8% · width 2.5. Heading yaw = acos(6.4/40) = 80.7931 deg
    #     (only 6.4 m of X progress over 40 m of run -> the 50% bank grade stretched to 8%)
    #     offset e : how far the deck's uphill edge is pushed riverward from the
    #     bank-chord tangent. e_up=0.6 gives an uphill cut face of 0.07~0.30 m (0 buried).
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
    ramp=dict(p0=(0.0, 4.0), length=40.0, width=2.5, e_up=0.60,
              deck_t=0.35, fill_t=2.0, fill_out=0.10,
              curb_w=0.15, curb_h=0.15,
              batter=dict(n=9, w=0.1667, dz=0.14, margin=0.30),
              apron=dict(build=False, x0=-1.60, x1=0.05, y0=0.60, y1=5.40,
                         t=0.35, drop=0.015)),
    # --- Terrace (riverside flat) : grass + promenade (width 3, parallel to the river) ---
    terrace=dict(x0=6.4, x1=27.5, y0=-30.0, y1=48.0, z_top=_TERRACE_Z,
                 thick=1.0),
    promenade=dict(x0=11.5, x1=14.5, proud=0.004, line_w=0.10, line_in=0.18),
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
    crown_lights=[(-7.9, -12.0), (-7.9, 9.5), (-7.9, 31.0)],
    streetlight=dict(pole_h=4.6, pole_r=0.075, arm_len=1.0, arm_r=0.045,
                     head=0.25),
    crown_trees=[(-11.2, -8.4), (-14.6, 12.7), (-9.8, 33.2), (-17.1, -19.6)],
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
    print(f"    yaw {g['yaw']:.4f}° (cos = {_SLOPE_RUN}/{g['length']:.0f} = "
          f"{g['d'][0]:.3f}) · 시점 {rp['p0']} · 종점 중심 "
          f"({p_end[0]:.2f}, {p_end[1]:.2f}, {p_end[2]:+.2f})")
    print(f"    상류 절토(+) / 매몰(−) · 강측 석축 높이:")
    worst_cut, worst_face = 9.9, 0.0
    for s in (0.0, 6.0, 12.0, 20.0, 28.0, 34.0, 40.0):
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
    for s in (0.0, 6.0, 12.0, 20.0, 28.0, 34.0, 40.0):
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

    # ── [v7 judgment (11)-1] entry apron footprint check (guards against the brown mass) ──
    #   The old apron sat inside rot_group(yaw), so local coordinates were mistaken for
    #   world and it reached world x +3.06 over the bank. The calculation is kept here.
    cy_, sy_ = (math.cos(math.radians(g["yaw"])),
                math.sin(math.radians(g["yaw"])))
    px0, py0 = rp["p0"]

    def _rot_world(lx, ly):
        vx, vy = lx - px0, ly - py0
        return (px0 + vx * cy_ - vy * sy_, py0 + vx * sy_ + vy * cy_)

    old_pts = [_rot_world(lx, ly) for lx in (-1.4, 0.0)
               for ly in (rp["p0"][1] - g["e_dn"], rp["p0"][1] + 1.2)]
    old_xmax = max(p[0] for p in old_pts)
    ap = rp["apron"]
    print("  [진입 apron 풋프린트 — v7 판정 ⑪-1 갈색 매스]")
    print(f"    구(rot_group 내부, 두께 2.80): 월드 꼭짓점 "
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
                    3열 엇갈림 군락으로 읽히는가"""


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
        gp = gk.plan_ground(
            "levee_paved", region=tuple(g["region"]), z=z_crown, gy=0.0,
            origin=(0.0, 0.0, 0.0),
            edges=[("levee_crest", float(PARAMS["stairs"]["x0"]))],
            dists=(2, 5, 10), scene="scene17", tactile=(),
            # §12.4 — 17 is OFF: p = 0.24 (park/riverside), below the 0.50 bar.
            overrides=dict(infra=dict(manhole=1, gully=2, gutter_L=0,
                                      trench=1)),
            extras_args=dict(wear_lane=dict(centerline=tuple(g["wear_lane"]),
                                            width=0.90)),
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[tuple(v) for v in g["gullies"]],
                       trench=[tuple(g["trench"])],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=17)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["conc"], crack=M["conc"], patch=M["asphalt"],
                  patch_cut=M["conc"], manhole=M["gk_iron"], gully=M["gk_iron"],
                  gutter=M["conc"], gutter_cover=M["conc"],
                  trench=M["rail"], trench_frame=M["rail"],
                  marking=M["paint"], weed=M["grass_b"], wear=M["conc"],
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
        # (2) deck (concrete paving)
        sc.build_slope(stage, f"{grp}/Deck", px, 0.0, L, drop, y_dn, y_up,
                       rp["deck_t"], ramp_mtl, margin=0.0, collider=True)
        # (3) river-side kerb (h0.15) — no railing (a below-code reality)
        sc.build_slope(stage, f"{grp}/Curb", px, rp["curb_h"], L, drop,
                       y_dn, y_dn + rp["curb_w"], rp["curb_h"] + 0.35,
                       M["conc"], margin=0.0, collider=True)
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
        for i, t in enumerate(PARAMS["far_trees"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", t["cx"], t["cy"],
                          fb["z_top"], M["wood"], M["canopy_a"], M["canopy_b"])

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
