# -*- coding: utf-8 -*-
"""
sceneC4_wet_stairs.py — NegObs synthetic scene 28: wet stone stairs right after rain (Isaac Sim 4.5)

Type    : C4 condition variant — wide granite stair geometry + a wetness (material) layer
Spec    : Docs/nanobanana_batch1_geometry_map.md §B sceneC4_wet_stairs
Look ref: look_refs/c4_wet_stairs.jpg
Shared  : scene_common.py · scene16_canopy_shadow.py (standard template) ·
          scene01_campus_stairs.py (straight-stair reference)

Hazard  : The geometry is a plain wide straight 14-step flight (riser 0.15 ·
          tread 0.35 · width 6.0), but the rain-soaked tread tops **mirror the
          overcast sky**. The bright sky reflection washes the riser shading off
          the adjacent step so the step edges **merge**, and treads holding a
          water film add a second specular layer on top of that.
          GT follows the geometry — **drop positive (2.10m)** — and with C1 (snow)
          this forms the "material variation axis".
Goal    : Keep walking continuity upper plaza -> wide stairs -> lower plaza while
          building the wetness as a **material layer (a low-roughness thin plate
          on the treads only)**, laying water films (build_water thin plates) on
          top and judging it by render (render only).
          [R-2 water row · 08-06] The films are **transparent** (OmniPBR
          cutout_opacity). Standing water is clear, so it must not occlude the
          tread it sits on; the cue that carries the scene is the wet **darkening
          + gloss of the tread patch**, read through the film, not the film's own
          mirror. See PARAMS["material"] water_* for the constants and the reason.

Feature precondition [IMPORTANT]:
  An **overcast sky dome** is what makes this scene work. The specular faces need
  a bright, uniform sky to reflect for "step edge merging" to happen. Under clear
  noon light the sun prints a point highlight and hard shadows revive the edges,
  and the feature collapses.
  -> light profile = sc.OVERCAST_HDRI + lookfix=False + no sun (shared with sceneC1).
  Specular reflection is also underestimated by single-bounce RT, so **judge with PT**.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneC4_wet_stairs.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneC4_wet_stairs.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneC4_wet_stairs.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — standard 7 keys + 1 feature toggle (wet_surface).
#     Only hazard_stairs is a geometry toggle (False -> whole site flat at z=0).
#     wet_surface is a material toggle (geometry unchanged); the water-film
#     plates are removed with it so we never get "water on a dry surface".
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> stairs · bank · lower plaza flat at z=0 (sole geometry toggle)
    "cue_railing":        True,   # 2 stainless rails on top of both cheek bands
    "cue_tactile":        True,   # top warning tactile paving (only high-contrast cue that survives the wet)
    "cue_material_break": True,   # False -> stairs get the plaza paving too
    "cue_nosing":         False,  # off by default — nosing paint defeats the 'edge merge' feature.
                                  #            Set True for the ablation run.
    "cue_sign":           False,  # [optional] not implemented — config key reserved only
    "cue_scene_dressing": True,   # grass bank · bollards · distant buildings together
    "wet_surface":        True,   # [feature] False -> dry materials + water films removed = twin
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # Wide straight 14 steps x riser 0.15 · tread 0.35 -> drop 2.10m, run 4.90m, width 6.0
    stairs=dict(x0=0.0, riser=0.15, tread=0.35, nsteps=14,
                y0=-3.0, y1=3.0, z_top=0.0, base_z=-3.00),

    # Upper plaza (stone paving). Thickness 2.6 -> solid down past the lower plaza floor.
    upper=dict(x0=-60.0, x1=0.0, y0=-60.0, y1=60.0, z_top=0.0, thick=2.60),

    # ═══ [W2 ground_kit] P3 sidewalk_block — spec §5.2 row C4 ═══════════════
    #  Prescription: (1) **extend the wet patches into the near window** (they are
    #  crowded on the stair faces now, h0.3 window empty) (2) tide/moss joints (3) edge weeds.
    #  * Condition overlay: this scene's ground elements go **under the wetness** —
    #    patches take wet-stone / dry-stone material per the `wet_surface` toggle,
    #    joints and grime bind to the tide (`tide`) / half-dry (`stone_damp`) materials.
    #    Geometry is identical either way (twin geometry-invariance rule).
    #  * Tactile paving: §12.4 "stays ON" + **non-compliance reproduced = wrong position**
    #    (0.6~1.0 m in front, not the statutory 0.3 m). A 2023 blind-persons'
    #    federation survey gives 4.0 % compliant / 77.3 % not, so "by-the-book
    #    placement is unreal" `[statistic — spec §12.4 non-compliance rule]`. setback 1.00 m.
    gkit=dict(
        region=(-10.0, -2.90, 0.0, 2.90),
        manhole=(-2.40, 0.60),          # W2 window (d5 X=2.6 m · 21.6 % of frame width)
        gullies=[(-3.60, 2.50), (-7.00, -2.50)],
        #  2 wet patches — one in the d2 near window (x −1.436…0) and one in
        #  the spec band (x −4.4…0). |y| <= 0.4 keeps them inside the d2 half-width.
        wet_patches=[(-1.20, 0.10), (-4.40, -1.20)],
        tactile_setback=1.00,           # ← non-compliant (misplaced). Statutory is 0.30
        tactile_depth=0.60,
    ),
    # Lower plaza. x0 starts 0.05 behind the stair end (run) and its top is 2mm
    # lower, avoiding coplanarity (Z-fighting) with the last tread — 5cm overlap.
    lower=dict(x_back=0.05, x1=60.0, y0=-60.0, y1=60.0, z_gap=0.002,
               thick=0.70),

    # Stone cheek band on the stair flank (exposed stringer). Top = nosing line + proud.
    cheek=dict(y_in=2.94, y_out=3.60, proud=0.06, x_head=0.05, x_tail=0.10,
               thick=0.70),
    # Grass bank outside the cheek — an embankment tying the upper plaza edge to the lower.
    #   Top plane z = −(riser/tread)·x -> no extra drop edge (no GT contamination),
    #   walking continuity kept (lesson 9). Unlike the scene17 ramp pair, not a drive path.
    bank=dict(y_in=3.55, y_out=60.0, x_head=0.05, x_tail=0.20, thick=2.40),

    # ─── Wetness layer [feature parameters] ─────────────────────────────────────
    #  film_*      thin plate on the tread tops only (the wet film). Only this plate
    #              takes the low-roughness material: "specular tread vs half-dry riser·flank".
    #              proud is inside the 0.001~0.004 convention (0.003). It overhangs
    #              3~5mm in x/y to avoid coplanarity with the step solid faces.
    #  wet_rough   specular roughness. Lower = sharper sky reflection -> stronger merge.
    #              spec 0.06~0.12. Start 0.08. Sweep 0.06 (mirror)~0.12 (matte wet).
    #  damp_rough  half-dry roughness for risers and flanks (spec 0.4).
    #  wet_tint / damp_tint : physical approximation of albedo darkening when wet.
    #  water_films : step index and partial width per film (no randomness — fixed table).
    # ────────────────────────────────────────────────────────────────────
    wet=dict(film_t=0.012, film_proud=0.003, film_over_x=0.003,
             film_over_y=0.005,
             wet_rough=0.14, wet_spec=0.9,   # r1: 0.08 was a full mirror -> specular eased
             plaza_rough=0.12, plaza_spec=0.8,
             damp_rough=0.40,
             wet_tint=(0.55, 0.56, 0.60), plaza_tint=(0.56, 0.57, 0.61),
             damp_tint=(0.74, 0.75, 0.79),
             water_t=0.005, water_lift=0.006,
             # ─── [just-after-rain package v2 · 07-27] ────────────────────────────
             #  User note: "the rain does not read / it is just glare on bright stone".
             #  (1) Patchwork: tread wetness goes from one material to **partial-width
             #     plates within the tread** across 3 tiers (kills the per-tread boundary).
             #  (2) Darkening: strong wet 0.36 vs the dry reference (damp_tint 0.74) = 51% down
             #     (the brief asked for 30~40%+), mid 0.47, half-dry patch 0.62.
             #     B channel is raised relatively (approximates wet stone's saturation rise).
             #  (3) Roughness per tier 0.10 / 0.20 / 0.35 — strong wet stays specular so
             #     the "edge merge" feature (sky reflection) does not collapse.
             #  (4) Geometry unchanged: the plate envelope (tread-top proud 0.003 ·
             #     thickness 0.012) stays. Only a y split is added; adjacent patches
             #     overlap by patch_overlap and stagger proud by patch_step (no coplanarity).
             patch_tiers=[dict(name="Strong", rough=0.10, spec=0.95,
                               tint=(0.352, 0.362, 0.398)),
                          dict(name="Mid", rough=0.20, spec=0.85,
                               tint=(0.455, 0.468, 0.500)),
                          dict(name="Damp", rough=0.35, spec=0.60,
                               tint=(0.605, 0.615, 0.645))],
             patch_seed=2804, patch_min=3, patch_max=5, patch_bias=0.62,
             patch_overlap=0.006, patch_step=0.0004,
             # Puddle darkening ring (the damp halo) — proud lower than the water film.
             ring_proud=0.0045, ring_grow_x=0.022, ring_grow_y=0.075,
             # tide mark (water line) · cheek runoff · riser run-down streaks
             #  Note: the cheek band's outer face shows only 6cm above the grass bank
             #    (y_in 3.55), so a tall tide band would be buried -> only the exposed
             #    0.10 is banded; the **cheek-top runoff stripe** carries the "it rained" look.
             tide_h=0.34, tide_h_cheek=0.10, tide_drop=0.005, tide_proud=0.012,
             runoff_w=0.24, runoff_in=0.02, runoff_proud=0.003, runoff_t=0.05,
             streak_seed=2811, streak_n=14, streak_w=0.11, streak_proud=0.003),
    # Water films: (step index 1~n, y0, y1) — pooled on part of the tread width only.
    #   v2: 1 rectangle -> **3~4 overlapping irregular lobes + darkening ring** (fixed seed).
    water_films=[dict(step=3, y0=-2.40, y1=0.30),
                 dict(step=6, y0=0.10, y1=2.55),
                 dict(step=9, y0=-2.60, y1=-0.20),
                 dict(step=12, y0=-1.20, y1=2.40)],
    # 2 plaza sheets (lower = big sheet at the stair foot · upper = shallow approach sheet)
    #   v2: 3 overlapping rotated lobes kill the rectangular outline + darkening ring.
    water_sheets=[dict(name="Lower", x0=0.15, x1=5.60, y0=-2.20, y1=2.60,
                       where="lower"),
                  dict(name="Upper", x0=-4.80, x1=-1.40, y0=-1.60, y1=1.90,
                       where="upper")],

    # Railings on both sides (on the cheek bands). Same slope as the stairs.
    rail=dict(y=3.27, x_start=-1.20, rail_h=0.90, post_r=0.022, rail_r=0.03,
              rail_mid_r=0.018, rail_mid_drop=0.45, spacing=1.50),

    tactile=dict(ahead=0.30, proud=0.004),
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.05, proud=0.001,
                y_inset=0.02),

    # ── Bollards [v5.1 §2 · ctx2] one row at the upper plaza entrance ───────────────────────
    #   Old: a 2x2 decorative array at (−2.6/−5.6, +-4.6) · φ0.16·h0.80 · no band /
    #   no dot tactile paving -> breaks the ban on decorative bollard rows (v5.1 §2).
    #   New: **one transverse row at the plaza entrance (x=−6.0)** · φ0.12·h0.90 ·
    #   spacing 1.5 m · white band on top · 0.3 m dot tactile in front (−X approach).
    #   The centre |y| < 2.8 (5.6 m wide ~ stair width 6.4 m) is left open as a
    #   **pedestrian/fire access gap** — the main line to the grand stair is never blocked.
    #   * Numeric check that the feature (wet stairs) is preserved:
    #     · From d10 (eye −10) the innermost bollard silhouette bears 34.4 deg and the
    #       innermost tactile corner 33.4 deg — both beyond the 30 deg half-frame -> no occlusion.
    #     · approach(eye −7)·grazing_mirror(eye −2.4)·film_closeup(eye −0.8)
    #       are each 70 deg off azimuth or behind the camera -> no interference.
    #     · From lower_lookback (eye +8.5) they are **farther** than the stairs, so cannot occlude.
    #   * No wet tint on the dot tactile (supervisor's call): the small slabs at
    #     x −6.06..−6.36 lie outside the upper water sheet (x −4.80..−1.40), so it is physical too.
    #   * [GT-115 ④] The dot tactile is **no longer built** (`tactile=False` at the call
    #     site) — from lower_lookback it printed as isolated yellow fragments at the post
    #     feet, unrelated to the stair-head warning band. The wet-tint note above is kept
    #     for the record; it is moot while the pad is off. Row geometry unchanged.
    bollard_rows=[dict(name="N", x=-6.0, y0=2.8, y1=5.8),
                  dict(name="S", x=-6.0, y0=-2.8, y1=-5.8)],
    bollard=dict(radius=0.06, height=0.90, spacing=1.5, front=(-1.0, 0.0)),
    buildings=dict(
        # +X distant vista blocker (plinth at lower plaza level). Facade on the -X plane.
        C=dict(x0=28.0, x1=34.0, y0=-16.0, y1=16.0, h=14.0, floors=4,
               axis="x", facade_x=28.0, face_dir=-1.0, level="lower"),
        # -X distant block (for lower_lookback). Facade +X plane, plinth at upper plaza level.
        D=dict(x0=-48.0, x1=-42.0, y0=-16.0, y1=16.0, h=10.0, floors=3,
               axis="x", facade_x=-42.0, face_dir=1.0, level="upper"),
        # [context v2] Wider facade front — two low wings flanking C give a civic block
        #   feel. Their y ranges are disjoint from C (y +-16), no overlap. All distant, x>=30.
        E=dict(x0=30.0, x1=36.0, y0=17.0, y1=40.0, h=11.0, floors=3,
               axis="x", facade_x=30.0, face_dir=-1.0, level="lower"),
        F=dict(x0=30.0, x1=36.0, y0=-40.0, y1=-17.0, h=12.0, floors=3,
               axis="x", facade_x=30.0, face_dir=-1.0, level="lower"),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # ═══ [context dressing v2 · 07-27] sense of place: a grand stair before a civic hall ═══
    #  Answers audit v4 master plan §emptiness. Stair geometry and wetness params unchanged.
    #  New prims stand only on the flat tops of the upper plaza (x<0, z=0) and
    #  the lower plaza (x>RUN, z=LOWER_TOP), never on the grass bank (x -0.05..5.10, |y|>3.55).
    #
    #  [camera check — build_views() 8+4 shots, FOV assumed +-30 deg H / +-18 deg V]
    #   grid eye(-2/-5/-10, 0, h) +X · approach eye(-7,0,1.65) az 0 ·
    #   grazing_mirror eye(-2.4,0,0.32) az 0 (vertical -27.1..+8.9 deg) ·
    #   film_closeup eye(-0.8,-1.2,0.75) az 23.6 (frame -6.4..53.6) ·
    #   lower_lookback eye(8.5,1.0,1.5) az 186.0 (frame 156..216)
    #   Rules (1) no new solid within 1.5 m of a camera eye
    #         (2) **every lower-plaza prop is at x>5.5, farther than the stairs
    #            (x 0..4.9), so none can hide the specular-merge feature** (no-occlusion proof)
    #         (3) vertical elements (lamps · flagpoles · capitals) sit inside the
    #            grazing_mirror/approach frame (az |·|<30 deg) to catch the wet reflection
    # ───────────────────────────────────────────────────────────────────────
    # 2 large planter pairs — upper at the stair shoulder (lookback az 159.6 deg),
    #   lower flanking the stair foot (grazing az +-25.5 · approach +-14.7), framing the stairs.
    #   Upper planters (x -2.1..-0.3) clear the existing bollards (x -2.68..-2.52) by 0.42 m.
    planters=[dict(cx=-1.2, cy=4.6, size=1.8, base="upper"),
              dict(cx=-1.2, cy=-4.6, size=1.8, base="upper"),
              dict(cx=6.6, cy=4.3, size=2.0, base="lower"),
              dict(cx=6.6, cy=-4.3, size=2.0, base="lower")],
    planter=dict(curb_h=0.52, curb_t=0.22, cap_over=0.05, cap_h=0.06,
                 soil_h=0.44, shrub_r=0.42),
    # 4 plaza lamps — 2 pairs on the lower plaza, casting vertical reflections on wet paving.
    #   (9.2,+-4.8) / (15.0,+-4.8): clear of planters (x 5.6..7.6) and sculpture (x 10.8..13.2).
    #   From lower_lookback they sit at az 79.6 deg (out of frame) -> no near occlusion.
    plazalamps=[dict(cx=9.2, cy=4.8, base="lower"),
                dict(cx=9.2, cy=-4.8, base="lower"),
                dict(cx=15.0, cy=4.8, base="lower"),
                dict(cx=15.0, cy=-4.8, base="lower"),
                dict(cx=-3.5, cy=5.6, base="upper"),
                dict(cx=-3.5, cy=-5.6, base="upper")],
    plazalamp=dict(pole_r=0.075, pole_h=4.60, base_r=0.16, base_h=0.45,
                   head_r=0.24, head_h=0.30),
    # 3 flagpoles + granite plinth — upper plaza +Y. For lower_lookback only
    #   (frame +Y limit: y<=8.35 at x=-8 -> 5.8/7.0 inside, 8.2 on the edge).
    #   All out of frame from the frontal views (approach/grazing/grid) = feature untouched.
    flag=dict(cx=-8.0, cys=(5.8, 7.0, 8.2), pole_r=0.055, pole_h=8.0,
              finial_r=0.09, plinth_pad=0.75, plinth_h=0.35),
    # Sculpture plinth + monolith — lower plaza +Y. grazing_mirror az 20.9 deg,
    #   approach az 16.1 deg, so **fully in frame** (silhouette against the distant facade).
    sculpture=dict(cx=12.0, cy=5.5, plinth=2.4, plinth_h=0.55,
                   mono_w=0.85, mono_h=3.20, base="lower"),
    # Distant colonnade — 0.2 m clear of the building C facade (x=28).
    #   The "colonnade hint" from the civic facade-widening brief. All distant, x>=25.4.
    colonnade=dict(x_c=26.6, y0=-9.6, y1=9.6, step=2.4, col_r=0.42,
                   col_h=6.60, sty_x0=25.4, sty_x1=27.8, sty_pad=1.9,
                   sty_h=0.50, beam_t=0.90, beam_pad=0.6, base="lower"),

    material=dict(
        scale=dict(granite_dark=1.2, stone_flag=0.9, grass=1.4,
                   brick_red=2.0, tactile=0.3),
        grass_tint=(0.42, 0.52, 0.34),      # rain-soaked grass — darker than the standard tone
        # ─── Water films [R-2 material row · 08-06] ──────────────────────────
        #  Verdict on round 260806_w3_allview4: the films render as opaque
        #  horizontal mirror plates and hide the tread/paving under them
        #  ("the water looks strange · water is clear, so it must not occlude
        #  the pad"). Cause: the film material carried no opacity input at all,
        #  so diffuse 0.03 + roughness 0.02 + specular 1.0 = a black mirror.
        #  [constraint] OmniGlass is forbidden project-wide (scene01 §3 material
        #  note), so transparency is OmniPBR `enable_opacity` +
        #  `opacity_threshold = 0` = **fractional** cutout_opacity, not a cutout
        #  mask [measured — kit/mdl/core/Base/OmniPBRBase.mdl:469].
        #  [computed] cutout_opacity weights the whole BSDF, so the film's own
        #  sky reflection scales with `opacity`. That is intended: the wet
        #  darkening + gloss of the **tread patch under** the film stays the
        #  primary wetness cue and the film only adds the grazing sheen on top.
        water_color=(0.026, 0.038, 0.044),  # near-black body: what shows is reflection, not haze
        water_rough=0.035,                  # 0.02 read as a plastic mirror — a touch of ripple blur
        water_spec=1.0,
        #  Opacity: single-lobe value. The lobes overlap, and stacked film is
        #  physically deeper water, so the compound opacity rises on its own —
        #  [computed] tread seam 2 layers 1−0.78² = 0.39 · plaza pool centre
        #  3 layers 1−0.82³ = 0.45, both still reading the pad through them.
        water_opacity=0.22,                 # tread films (a few-mm sheet)
        water_opacity_pool=0.18,            # plaza pools (3 lobes stack -> 0.45 at the centre)
        #  Ripple: a large-tile world-projected normal at a very low bump factor.
        #  Without it a constant-normal plate under a uniform overcast dome is a
        #  dead-flat mirror, which is exactly what "looks strange" reads as.
        water_ripple_scale=2.60,            # [m/tile] normal projection period
        water_ripple_bump=0.055,            # tread film — nearly flat
        water_ripple_bump_pool=0.110,       # plaza pool — open to the wind
        #  Meniscus: OmniPBR round edges on the slab rim, so the film terminates
        #  as surface tension instead of a raw 5/10 mm cut face (edge rule).
        water_meniscus=0.0030, water_meniscus_pool=0.0055,
        #  Puddle halo (the damp ring) — **wet stone, not paint**. The ring kept
        #  its geometry but was bound to the near-black `tide` constant (0.062),
        #  which printed a ~5 m matte-black lobe on the lower plaza that reads as
        #  a pit, not as a damp ring. It now takes the same texture role and world
        #  projection as the surface it sits on, so the stone grain runs straight
        #  through the ring boundary and only the tone/gloss change.
        #  [computed] halo 0.278 vs plaza 0.56 = 50 % down, and 21 % below the
        #  strongest tread tier (0.352) -> still the darkest ground tone in frame.
        halo_tint=(0.278, 0.288, 0.318), halo_rough=0.085, halo_spec=1.0,
        dry_rough_hint=0.55,                # dry twin (uses the roughness texture)
        rail_color=(0.78, 0.80, 0.83), rail_metallic=0.9, rail_rough=0.30,
        # Bollard v5.1 top reflective band (white, small area). Body shares the rail material.
        bollard_band_color=(0.88, 0.88, 0.86),
        wall_tint=(0.86, 0.86, 0.88),
        glass_color=(0.05, 0.07, 0.10), glass_rough=0.12,
        parapet_color=(0.84, 0.85, 0.86), parapet_rough=0.7,
        # ─ rain package v2 / context v2 constants (sRGB dark-tone rule 0.02~0.09) ─
        tide_color=(0.062, 0.066, 0.078), tide_rough=0.22, tide_spec=0.9,
        shrub_color=(0.032, 0.050, 0.030),
    ),

    # ─── overcast lighting profile (same as sceneC1) ────────────────────────
    #  · hdri=sc.OVERCAST_HDRI : the uniform overcast sky the mirrors reflect.
    #  · lookfix=False         : lookfix is for "sun cap + horizon lift". Meaningless
    #                            on a sunless HDRI, so the original is used.
    #  · noon_sun_enable=False : auxiliary DistantLight invisible -> no hard shadows.
    #                            (setup_lighting always reads the intensity/color
    #                             keys, so the keys themselves stay.)
    #  · dome_intensity        : raised to make up for losing 2450 of direct light.
    #                            Sweep 1500~2500 against the old noon 1000. Start 2000
    #                            (same start as sceneC1 — granite is darker than snow,
    #                             so push toward 2400 if it renders dark).
    #  · hdri_sun_rotz_offset  : meaningless without a sun -> 0.0.
    # ────────────────────────────────────────────────────────────────────
    light=dict(
        hdri=sc.OVERCAST_HDRI,
        # r1: 2000->1500 to ease overexposure / [rain package v2] 1500->1150 for the
        #   gloom after a shower. lookfix=False · sunless profile kept (feature precondition).
        dome_intensity=1150.0,
        noon_dome_rot=-110.0,
        lookfix=False,
        noon_sun_enable=False, noon_sun_elev=49.79,
        noon_sun_intensity=600.0, noon_sun_color=(1.0, 0.985, 0.97),
        hdri_sun_rotz_offset=0.0,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET: sunless profile, so shadow azimuth means nothing. Dome Z rotation
    #     only changes the overcast sky's gentle luminance gradient (= the brightness
    #     mirrored by the specular faces). Kept at brief v3 §A-7 default 171.5; sweep with [ ]. ─
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
# [B'] keep_dressing — the v3 arm C control, resolved ONCE at module scope
# ===========================================================================
#   Ported verbatim from `sceneC2_leaf_stairs.py:496-520` (the canonical
#   implementation) per RENDER_PLAN_V3 §1.3. Every use below reads this one
#   constant, so `grep KEEP_DRESSING` is the whole audit surface. False (the
#   default, and the value in both existing arms) makes every guarded
#   expression collapse to exactly what it was before the patch.
#   Arm C = `{"hazard_stairs": false, "keep_dressing": true}` with every `cue_*`
#   at its A-arm default: the descent is removed, the cue objects stay.
#   The two contradictions below are FATAL rather than silently resolved: an arm
#   whose config does not say what it means must not render 24 cuts and be
#   discovered later in a metrics table.
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneC4] keep_dressing=True requires hazard_stairs=False — "
            "with the hazard ON there is nothing to keep and the arm would be "
            "an unlabelled duplicate of arm A. Fix the render config.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneC4] keep_dressing=True contradicts "
            "cue_scene_dressing=False — the dressing IS what this arm exists to "
            "preserve.")
    print("[keep_dressing] sceneC4 ON — hazard geometry only (stair·cheek "
          "band·grass bank·lower plaza -> flat z=0); the stair railing keeps "
          "its ON transform (descending line), tactile paving · bollards · "
          "civic dressing · buildings are already hazard-free and unchanged. "
          "Tread water films · rain marks are dropped with the treads they "
          "are plated onto (`wet_surface` is a material feature, not a cue). "
          "Camera datum untouched: FlatFill's top is `upper.z_top` = the very "
          "z the ON arm's UpperPlaza carries over the whole x<0 strip.")


# ===========================================================================
# [C] Path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneC4")

ASSET_ROLES = ["granite_dark", "stone_flag", "grass", "brick_red", "tactile",
               "hdri", "mdl"]


# --- Derived dimensions (shared by builders) -------------------------------------------
def _dims():
    st = PARAMS["stairs"]
    run = st["tread"] * st["nsteps"]
    drop = st["riser"] * st["nsteps"]
    slope_k = st["riser"] / st["tread"]          # nosing-line slope (descending +X)
    return run, drop, slope_k


def bollard_points():
    """[v5.1 §2] Plaza-entrance bollard centres [(name, x, y), ...] (spacing 1.5 m)."""
    out = []
    sp = PARAMS["bollard"]["spacing"]
    for row in PARAMS["bollard_rows"]:
        for i, (bx, by) in enumerate(bc.bollard_line(
                row["x"], row["y0"], row["x"], row["y1"], spacing=sp)):
            out.append((f"{row['name']}{i}", bx, by))
    return out


def civic_placements():
    """Planters and plaza lamps at their nominal centres.

    [W3 CB-3 · J-4 abolished, spec §1.2 / §10.1] Was +-0.15 m / +-0.18 m
    position jitter, justified as "breaks exact L/R symmetry". A symmetric
    civic plaza IS symmetric; the cure for a cloned row is a real cause for the
    interval (a tree pit, a manhole, a doorway), not a coordinate hash.
    """
    pls = [(i, pd["cx"], pd["cy"], pd) for i, pd in enumerate(PARAMS["planters"])]
    lms = [(i, ld["cx"], ld["cy"], ld) for i, ld in enumerate(PARAMS["plazalamps"])]
    return pls, lms


def ground_plans():
    """[W2 ground_kit] Ground plan — scene assembly and the CPU check share this function."""
    g = PARAMS["gkit"]
    st = PARAMS["stairs"]
    x_edge = float(st["x0"])
    band = (x_edge - g["tactile_setback"] - g["tactile_depth"],
            float(st["y0"]), x_edge - g["tactile_setback"], float(st["y1"]))
    gp = gk.plan_ground(
        "sidewalk_block", region=tuple(g["region"]),
        z=float(PARAMS["upper"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("stair_top", x_edge)],
        dists=(2, 5, 10), scene="sceneC4",
        tactile=("stair_top",) if SCENE_CONFIG["cue_tactile"] else (),
        sites=dict(manhole=[tuple(g["manhole"])],
                   gully=[tuple(p) for p in g["gullies"]],
                   patch=[tuple(p) for p in g["wet_patches"]],
                   tactile=dict(stair_top=band)),
        #  L-shaped gutters belong at a carriageway edge — not on a civic grand-stair plaza.
        #  [GT-115 ④] `surface` row taken over from the profile **minus `("weed", 8)`**.
        #    P3 seeds its 8 tufts along `_weed_seed_lines`, which for this profile is the
        #    step_x=3.0 joint grid — full-width transverse lines at x −9/−6/−3 — so 6 of
        #    the 8 land in the open middle of the plaza (measured centres: −9.05/−0.29,
        #    −8.96/+0.61, −5.96/+0.55, −2.96/+2.12, −2.12/+0.90, −3.90/+2.61) and 6 fall
        #    inside the pt_noon_lower_lookback crop (1000,440–1600,560) [computed].
        #    Two defects at once: (1) a maintained civic plaza does not grow tufts in the
        #    field — the same call scene01's `plaza_granite` already carries (ground_kit
        #    §13 A1, "weed 6 -> 0"); (2) the builder references `Shrub/Grass_Short_C.usd`
        #    and never binds the scene's `weed` material, so the tufts keep the asset's
        #    dry bright green while every other surface in frame is rain-darkened.
        #    Placement is library-internal (`_weed_sites`), so the scene cannot restrict
        #    it to real joints/edges from here — the row is dropped instead. `crack` and
        #    `stain` are kept verbatim so NEGOBS_DECAL_FULL=1 still restores exactly what
        #    the profile prescribes. Hard gates B6~B12 re-checked PASS, prims 18 -> 10.
        overrides=dict(infra=dict(manhole=1, gully=2, gutter_L=0),
                       surface=(("crack", 4), ("stain", ("dirt", "gum")))),
        seed=28)
    return [("upper", gp)]


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene shots. No centre railing."""
    views = sc.grid_views(0.0)
    # approach: pedestrian view on the upper plaza — the wide stairs in full
    views["approach"] = dict(eye=[-7.0, 0.0, 1.65], tgt=[2.5, 0.0, -1.00])
    # grazing_mirror: low eye — do sky reflections merge the step edges (feature check 1)
    views["grazing_mirror"] = dict(eye=[-2.4, 0.0, 0.32], tgt=[4.6, 0.0, -0.80])
    # film_closeup: close on a water-film tread — [R-2 water row] the check is now
    #   "is the tread patch readable **through** the film", not "is it a mirror"
    views["film_closeup"] = dict(eye=[-0.8, -1.2, 0.75], tgt=[2.4, 0.20, -1.10])
    # lower_lookback: looking back from below — check the wet riser contrast
    views["lower_lookback"] = dict(eye=[8.5, 1.0, 1.50], tgt=[-1.0, 0.0, 0.20])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 하늘 방위
[체크리스트]
 1. approach / grid    — 광폭 14단·상하 광장·측면 치크밴드 식별
 2. grazing_mirror·PT  — 트레드 경면이 하늘을 반사해 단 에지가 병합되는가(특색)
 3. film_closeup·PT    — 수막 4곳이 투명한가(아래 패치·줄눈이 비치는가)·
                        가장자리가 메니스커스로 끝나는가 (RT는 과소평가)
 4. wet ON vs OFF      — 건조 대응쌍에서 단 에지가 되살아나는가·기하 불변인가
 5. 조명               — 무태양 저대비인가(경질 그림자 0), 경면 하이라이트 점 없는가
 6. 재질·Z파이팅       — 젖음 박판 가장자리·수막·광장 이음에 깜빡임 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene28")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    wt = PARAMS["wet"]
    ROOT = "/World/Scene28"

    RUN, DROP, SLOPE_K = _dims()
    LOWER_TOP = PARAMS["stairs"]["z_top"] - DROP - PARAMS["lower"]["z_gap"]

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def PBR_WATER(path, opacity, ripple_bump, meniscus):
        """Local OmniPBR factory for the water films — **transparent** water.

        `sc.make_pbr` exposes no opacity input and `scene_common` is out of scope
        for this row, so the film material is authored here. Everything except
        the opacity/ripple/meniscus block mirrors `sc.make_pbr`: same OmniPBR
        source asset, same world-space projection, same 3 mdl outputs, so the
        film behaves like every other material in the scene.

        `opacity_threshold = 0` -> fractional opacity used as is (alpha), not a
        cutout mask [measured — OmniPBRBase.mdl:469]. RT under-reports specular
        and transparency alike, so the verdict stays PT (header note).
        `/rtx/{raytracing,pathtracing}/fractionalCutoutOpacity` both default to
        True, so nothing has to be set on the renderer side
        [survey — H_rtx_capability_verification.md §5.2].

        GT side effect, and it is the one we want: Replicator scores segmentation
        as true only at opacity 1.0, so an alpha < 1 film **drops out of the
        semantic mask** and the mask keeps reading the tread underneath (same
        survey §5.2b). This scene's GT is geometric (the 2.10 m drop) and no
        water prim is GT-bearing, so nothing in the registry moves — the film
        simply stops being able to contaminate the tread label.

        LOOK class for `Looks/Water` is `water` = bevel 0 / detail off / no MDL
        swap, so routing through `make_pbr` would add nothing here anyway.

        Graceful degradation: the ripple normal is wired **only** when the
        granite_dark normal map resolves on disk; without it the film is a
        constant-normal transparent sheet and nothing else changes.
        """
        from pxr import UsdShade, Sdf, Gf
        mtl = UsdShade.Material.Define(stage, path)
        sh = UsdShade.Shader.Define(stage, path + "/Shader")
        sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
        sh.SetSourceAsset(Sdf.AssetPath(sc.OMNIPBR_PATH), "mdl")
        sh.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
        F = Sdf.ValueTypeNames.Float
        C3 = Sdf.ValueTypeNames.Color3f
        B = Sdf.ValueTypeNames.Bool
        F2 = Sdf.ValueTypeNames.Float2
        sh.CreateInput("diffuse_color_constant",
                       C3).Set(Gf.Vec3f(*mp["water_color"]))
        sh.CreateInput("metallic_constant", F).Set(0.0)
        sh.CreateInput("reflection_roughness_constant",
                       F).Set(float(mp["water_rough"]))
        sh.CreateInput("specular_level", F).Set(float(mp["water_spec"]))
        # (1) transparency — the pad under the film has to stay readable
        sh.CreateInput("enable_opacity", B).Set(True)
        sh.CreateInput("enable_opacity_texture", B).Set(False)
        sh.CreateInput("opacity_constant", F).Set(float(opacity))
        sh.CreateInput("opacity_threshold", F).Set(0.0)
        # (2) meniscus — the slab rim must not terminate as a raw cut face.
        #     Kit 106.1+ round edges, verified in both RT and PT (scene_common §4).
        if meniscus > 0.0:
            sh.CreateInput("round_edges_radius", F).Set(float(meniscus))
            sh.CreateInput("round_edges_roundness", F).Set(1.0)
            sh.CreateInput("round_edges_across_materials", B).Set(False)
        # (3) ripple — world projection, so the perturbation is continuous
        #     across the overlapping lobes instead of restarting per prim.
        nor = None
        if ripple_bump > 0.0:
            try:
                p = sc.tex_path("granite_dark", "nor")
                nor = p if p and os.path.isfile(p) else None
            except Exception:
                nor = None
        if nor is not None:
            a = sh.CreateInput("normalmap_texture", Sdf.ValueTypeNames.Asset)
            a.Set(nor)
            try:                                   # a normal map must be raw
                a.GetAttr().SetColorSpace("raw")
            except Exception:
                pass
            sh.CreateInput("project_uvw", B).Set(True)
            sh.CreateInput("world_or_object", B).Set(True)
            s = 1.0 / float(mp["water_ripple_scale"])
            sh.CreateInput("texture_scale", F2).Set(Gf.Vec2f(s, s))
            sh.CreateInput("bump_factor", F).Set(float(ripple_bump))
        for out in ("surface", "displacement", "volume"):
            mtl.CreateOutput(f"mdl:{out}",
                             Sdf.ValueTypeNames.Token).ConnectToSource(
                sh.ConnectableAPI(), "out")
        return mtl

    # -------------------------------------------------------------------
    # Materials
    #   Wet materials get **no** roughness texture: with OmniPBR,
    #   reflection_roughness_texture_influence=1.0 ignores the constant, so to force
    #   a mirror (0.08) we use diff+nor only and set a constant roughness.
    #   (the dry twin keeps the roughness texture = the original stone look)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        wet = cfg["wet_surface"]
        M = {}
        gd = ("granite_dark", sca["granite_dark"])
        sf = ("stone_flag", sca["stone_flag"])

        def stone(name, role_scale, rough, spec, tint):
            role, s = role_scale
            if wet:
                return PBR(f"{ROOT}/Looks/{name}", sc.tex_path(role, "diff"),
                           sc.tex_path(role, "nor"), None, s,
                           tint=tint, roughness_const=rough,
                           specular_level=spec, metallic=0.0)
            return PBR(f"{ROOT}/Looks/{name}", sc.tex_path(role, "diff"),
                       sc.tex_path(role, "nor"), sc.tex_path(role, "rough"),
                       s, metallic=0.0)

        # tread wet plate (specular) / step solid and riser (half-dry) / plaza paving
        M["tread_wet"] = stone("TreadWet", gd, wt["wet_rough"],
                               wt["wet_spec"], wt["wet_tint"])
        # [rain package v2] 3 wetness tiers — in the dry twin stone() falls back to the
        #   texture-roughness path and all three become the same dry stone (twin
        #   consistency held in both geometry and look).
        for ti, td in enumerate(wt["patch_tiers"]):
            M[f"tread_p{ti}"] = stone(f"TreadP{td['name']}", gd, td["rough"],
                                      td["spec"], td["tint"])
        M["stone_damp"] = stone("StoneDamp", gd, wt["damp_rough"], None,
                                wt["damp_tint"])
        # [R-2 water row] Puddle halo — the damp ring around/under standing water.
        #   Same texture role and scale as the surface it lies on (granite on the
        #   treads, flagstone on the plaza) and `make_pbr` projects in **world**
        #   space, so the grain runs continuously through the ring boundary: only
        #   tone and gloss change, no "pasted plate" silhouette.
        #   Names avoid the LOOK role tokens tread/step/wet/tide on purpose so the
        #   pair classifies as `stone` exactly like StoneDamp (scene_common §1b).
        #   In the dry twin `stone()` falls back to the dry texture path, same as
        #   every other wet material here.
        M["halo_step"] = stone("PuddleStoneA", gd, mp["halo_rough"],
                               mp["halo_spec"], mp["halo_tint"])
        M["halo_plaza"] = stone("PuddleStoneB", sf, mp["halo_rough"],
                                mp["halo_spec"], mp["halo_tint"])
        M["plaza"] = stone("Plaza", sf, wt["plaza_rough"], wt["plaza_spec"],
                           wt["plaza_tint"])
        M["cheek"] = stone("Cheek", gd, wt["damp_rough"], None,
                           wt["damp_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"], tint=mp["wall_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # [R-2 water row] Two transparent water materials — the tread film is a
        #   thin sheet, the plaza pool is standing water (deeper -> less clear,
        #   more wind ripple, wider meniscus). Prim root `Looks/Water` is kept.
        M["water"] = PBR_WATER(f"{ROOT}/Looks/Water", mp["water_opacity"],
                               mp["water_ripple_bump"], mp["water_meniscus"])
        M["water_pool"] = PBR_WATER(f"{ROOT}/Looks/WaterPool",
                                    mp["water_opacity_pool"],
                                    mp["water_ripple_bump_pool"],
                                    mp["water_meniscus_pool"])
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
        # Bollard v5.1 white top band — 0.08 m² each, a small area (complies with v5.1 §4)
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # [rain package v2] shared by tide mark · puddle darkening ring · riser run-down
        #   dark wet material (sRGB dark-tone rule 0.02~0.09, specularity kept)
        # [W2 fix batch F1] Ground-class decal materials for the kit — see the
        #   `scripts/const_color_audit.py` rule: a *ground* prim may not carry a
        #   texture-less constant. paint / metal / water / misc are excluded from
        #   `_CONST_MDL_CLASSES` by design, so binding a kit crack or stain to one
        #   left it as a dead flat ribbon.
        M["gk_stain"] = PBR(f"{ROOT}/Looks/GKitStain",
                            diffuse_color=(0.20, 0.20, 0.195),
                            roughness_const=0.86)
        M["tide"] = PBR(f"{ROOT}/Looks/Tide", diffuse_color=mp["tide_color"],
                        roughness_const=mp["tide_rough"], metallic=0.0,
                        specular_level=mp["tide_spec"])
        # [context v2] planter shrubs — wet leaves (dark + weak specular)
        M["shrub"] = PBR(f"{ROOT}/Looks/Shrub", diffuse_color=mp["shrub_color"],
                         roughness_const=0.65, specular_level=0.5)
        return M

    # -------------------------------------------------------------------
    # Terrain — upper plaza / lower plaza / cheek band / grass bank
    #   Embankment type with no opening (pit), so no 4-box split is needed. The four
    #   solids tile with overlap -> no plane covering a cavity and no floating edge.
    # -------------------------------------------------------------------
    def build_upper(M):
        up = PARAMS["upper"]
        # [W2-0 · P-A] The upper plaza top is what ground_kit dresses -> displacement
        #   skin OFF (registered **before the BOX call**). Keeps the wet patches (+2 mm)
        #   and tactile paving (6 mm studs) from vanishing under the skin (+6.5~16.5 mm).
        sc.skin_exclude(f"{ROOT}/UpperPlaza")
        BOX(f"{ROOT}/UpperPlaza",
            ((up["x0"] + up["x1"]) / 2.0, (up["y0"] + up["y1"]) / 2.0,
             up["z_top"] - up["thick"] / 2.0),
            (up["x1"] - up["x0"], up["y1"] - up["y0"], up["thick"]),
            M["plaza"], col=True)

    def build_lower(M):
        lo = PARAMS["lower"]
        x0 = RUN - lo["x_back"]
        BOX(f"{ROOT}/LowerPlaza",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             LOWER_TOP - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["plaza"], col=True)

    def build_cheeks(M):
        """Stone cheek band on the stair flank — top = nosing line + proud."""
        ck = PARAMS["cheek"]
        x0 = -ck["x_head"]
        z0 = SLOPE_K * ck["x_head"] + ck["proud"]
        run = RUN + ck["x_head"] + ck["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a, b = sgn * ck["y_in"], sgn * ck["y_out"]
            sc.build_slope(stage, f"{ROOT}/Cheek_{tag}", x0, z0, run,
                           run * SLOPE_K, min(a, b), max(a, b), ck["thick"],
                           M["cheek"], margin=0.0, collider=True)

    def build_banks(M):
        """Grass bank outside the cheek — top = nosing line (no extra drop edge)."""
        bk = PARAMS["bank"]
        x0 = -bk["x_head"]
        z0 = SLOPE_K * bk["x_head"]
        run = RUN + bk["x_head"] + bk["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a, b = sgn * bk["y_in"], sgn * bk["y_out"]
            sc.build_slope(stage, f"{ROOT}/Bank_{tag}", x0, z0, run,
                           run * SLOPE_K, min(a, b), max(a, b), bk["thick"],
                           M["grass"], margin=0.0, collider=True)

    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False control: the whole site flat at z=0."""
        up = PARAMS["upper"]
        # [W2-0 · P-A] Ground elements are laid in the control too -> skin OFF.
        sc.skin_exclude(f"{ROOT}/FlatFill")
        lo = PARAMS["lower"]
        x0, x1 = up["x0"], lo["x1"]
        BOX(f"{ROOT}/FlatFill",
            ((x0 + x1) / 2.0, (up["y0"] + up["y1"]) / 2.0,
             up["z_top"] - up["thick"] / 2.0),
            (x1 - x0, up["y1"] - up["y0"], up["thick"]),
            M["plaza"], col=True)

    # -------------------------------------------------------------------
    # Wetness layer [feature] — tread-only thin plates + water films
    #   The plates bury into the step solid (overhanging 3~5mm in x/y) and only the
    #   top shows, proud 3mm -> no coplanarity. Only the material is specular (roughness 0.08).
    # -------------------------------------------------------------------
    def build_tread_films(M):
        """[rain package v2] Break the tread wet plate into **3~5 partial-width patches
        inside each tread**. The geometric envelope (top proud 0.003 · thickness 0.012 ·
        x +-3mm overhang) is unchanged; only the y cut lines are scattered from a fixed
        seed, erasing the "wetness per tread" impression.
        Adjacent patches overlap by patch_overlap (6mm) and their proud is staggered by
        patch_step (0.4mm) on a j%3 ladder, so no coplanarity (Z-fighting) appears in
        the overlap zones.
        In the dry twin (wet_surface=False) all 3 tier materials collapse to the same
        dry stone, so **twin consistency holds in both geometry and look**."""
        st = PARAMS["stairs"]
        ox, oy = wt["film_over_x"], wt["film_over_y"]
        y_lo, y_hi = st["y0"] - oy, st["y1"] + oy
        span = y_hi - y_lo
        rng = random.Random(int(wt["patch_seed"]))
        bias = float(wt["patch_bias"])
        n_patch = 0
        for i in range(1, st["nsteps"] + 1):
            xa = st["x0"] + st["tread"] * (i - 1) - ox
            xb = xa + st["tread"] + 2.0 * ox
            ztop = st["z_top"] - st["riser"] * i
            k = rng.randint(int(wt["patch_min"]), int(wt["patch_max"]))
            cuts = sorted(y_lo + span * (j / k)
                          + rng.uniform(-0.34, 0.34) * span / k
                          for j in range(1, k))
            edges = [y_lo] + cuts + [y_hi]
            for j in range(k):
                r = rng.random()
                ti = 0 if r < bias * 0.55 else (1 if r < bias else 2)
                ya = edges[j] - (wt["patch_overlap"] if j > 0 else 0.0)
                yb = edges[j + 1] + (wt["patch_overlap"] if j < k - 1 else 0.0)
                z_hi = ztop + wt["film_proud"] + (j % 3) * wt["patch_step"]
                z_lo = ztop - wt["film_t"]
                BOX(f"{ROOT}/WetFilm/T{i}_P{j}",
                    ((xa + xb) / 2.0, (ya + yb) / 2.0, (z_hi + z_lo) / 2.0),
                    (xb - xa, yb - ya, z_hi - z_lo), M[f"tread_p{ti}"])
                n_patch += 1
        print(f"[젖음] 트레드 패치 {n_patch}매 · tier "
              f"{len(wt['patch_tiers'])}단 (seed={wt['patch_seed']})")

    def build_water(M):
        """Water films — [rain package v2] one rectangle -> **overlapping irregular lobes
        + a darkening ring**. Fixed seed (patch_seed+1). z ladder rule:
          tread film top 0.0030~0.0038 < darkening ring 0.0045~0.0051
          < water surface 0.0060~0.0068  -> none of the 3 layers is coplanar.
        Tread puddle lobes are made ragged by x inset and y splits alone, without
        rotation (rotating them would poke past the nosing). The plaza sheets have no
        such constraint, so 3 of them are overlapped at an angle with _oriented_box
        rotZ to erase the rectangular outline.

        [R-2 water row · 08-06] The lobe table and all extents are unchanged; only
        the bindings change. Films take the transparent `water`/`water_pool`
        materials (the tread patch and the paving read **through** them) and the
        rings take the wet-stone halo instead of the near-black `tide` constant.
        The lobe bottom face is not a floating edge either way: the tread lobe
        bottom sits at ztop +0.0010~0.0018, i.e. **inside** the tread patch
        (top +0.0030~0.0038), and the plaza lobes sink 4 mm into the plaza slab
        [computed]. What transparency now exposes is the patch under the film,
        which is the point of the row."""
        st = PARAMS["stairs"]
        ox = wt["film_over_x"]
        rng = random.Random(int(wt["patch_seed"]) + 1)
        k = 0
        for f in PARAMS["water_films"]:
            i = int(f["step"])
            x_lo = st["x0"] + st["tread"] * (i - 1) - ox     # film leading edge
            x_hi = x_lo + st["tread"] + 2.0 * ox             # film trailing edge
            xa = st["x0"] + st["tread"] * (i - 1) + 0.010
            xb = xa + st["tread"] - 0.030
            ztop = st["z_top"] - st["riser"] * i
            y0, y1 = f["y0"], f["y1"]
            ly = y1 - y0
            cuts = sorted(y0 + ly * (j / 3.0) + rng.uniform(-0.16, 0.16) * ly / 3.0
                          for j in (1, 2))
            edges = [y0] + cuts + [y1]
            for j in range(3):
                lx0 = xa + rng.uniform(0.0, 0.055)
                lx1 = xb - rng.uniform(0.0, 0.045)
                ly0 = edges[j] - (0.05 if j > 0 else 0.0)
                ly1 = edges[j + 1] + (0.05 if j < 2 else 0.0)
                # (1) darkening ring (the damp halo) — clamped inside the tread film width
                rx0 = max(x_lo + 0.002, lx0 - wt["ring_grow_x"])
                rx1 = min(x_hi - 0.002, lx1 + wt["ring_grow_x"])
                rz = ztop + wt["ring_proud"] + j * 0.0003
                BOX(f"{ROOT}/Water/Ring_{k}",
                    ((rx0 + rx1) / 2.0, (ly0 + ly1) / 2.0, rz - 0.005),
                    (rx1 - rx0, (ly1 - ly0) + 2.0 * wt["ring_grow_y"], 0.010),
                    M["halo_step"])
                # (2) water-surface lobe
                sc.build_water(stage, f"{ROOT}/Water/Tread_{k}", lx0, ly0,
                               lx1, ly1,
                               ztop + wt["water_lift"] + j * 0.0004,
                               thick=wt["water_t"], mtl=M["water"])
                k += 1
        # Plaza sheets — 3 rotated lobes (+ ring). To stay out of the stair corridor
        #   (x>=0) the upper sheet's lobes stop at x = −0.97 (checked value).
        lobes = ((0.82, 0.70, -0.06, 0.10, 9.0),
                 (0.66, 0.92, 0.14, -0.08, -13.0),
                 (0.90, 0.52, 0.02, 0.16, 4.0))
        for sh in PARAMS["water_sheets"]:
            base = LOWER_TOP if sh["where"] == "lower" else 0.0
            xs = RUN if sh["where"] == "lower" else 0.0
            x0, x1 = sh["x0"] + xs, sh["x1"] + xs
            cx0 = (x0 + x1) / 2.0
            cy0 = (sh["y0"] + sh["y1"]) / 2.0
            Lx, Ly = x1 - x0, sh["y1"] - sh["y0"]
            for j, (fx, fy, dx, dy, rz_deg) in enumerate(lobes):
                cx = cx0 + dx * Lx
                cy = cy0 + dy * Ly
                # Ring top 0.0026/0.0029/0.0032 above the slab. The old ladder
                # started at exactly 0.0020, which is **coplanar** with the
                # ground_kit relaid patch (`patch_proud` = 0.002, ground_kit.py:261)
                # — and the upper sheet covers the patch at (−4.40, −1.20)
                # [computed]. +0.6 mm clears it while staying far under the water
                # top (0.0060~0.0068), so the 3-layer ladder still holds:
                #   gkit patch 0.0020 < halo ring 0.0026~0.0032 < water 0.0060~0.0068.
                sc._oriented_box(
                    stage, f"{ROOT}/Water/RingSheet_{sh['name']}_{j}",
                    (cx, cy, base + 0.0026 + j * 0.0003 - 0.005),
                    (Lx * fx + 0.22, Ly * fy + 0.22, 0.010), M["halo_plaza"],
                    rotz=rz_deg)
                sc._oriented_box(
                    stage, f"{ROOT}/Water/Sheet_{sh['name']}_{j}",
                    (cx, cy, base + 0.006 + j * 0.0004 - 0.005),
                    (Lx * fx, Ly * fy, 0.010), M["water_pool"], rotz=rz_deg)

    # -------------------------------------------------------------------
    # [rain package v2] tide mark (water line) + riser run-down streaks
    #   They are the "evidence" of wetness, so they follow the wet_surface toggle
    #   and are not built for the dry twin (stair body and films carry twin geometry).
    # -------------------------------------------------------------------
    def build_rain_marks(M):
        st = PARAMS["stairs"]
        ck = PARAMS["cheek"]
        th = wt["tide_h"]
        x0 = -ck["x_head"]
        run = RUN + ck["x_head"] + ck["x_tail"]
        z_ck = SLOPE_K * ck["x_head"] + ck["proud"]      # cheek top at x=x0
        # (1) cheek band **top runoff stripe** — a dark wet band along the inner edge
        #    on the stair side where water ran down. proud 3mm (within rule), width 0.24.
        #    The cheek top sits at nosing line +0.06, the only broad slope exposed above
        #    the grass bank -> in frame at approach az 23.2 deg · grazing az 22.3 deg.
#    y 3.02..3.26 : outside the stair flank (+-3.00) · inside the cheek (2.94..3.60)
#    -> even at the nosing the plate bites into the cheek solid, so no floating slit.
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a = sgn * (ck["y_in"] + wt["runoff_in"])
            b = sgn * (ck["y_in"] + wt["runoff_in"] + wt["runoff_w"])
            sc.build_slope(stage, f"{ROOT}/Tide/Runoff_{tag}", x0,
                           z_ck + wt["runoff_proud"], run, run * SLOPE_K,
                           min(a, b), max(a, b), wt["runoff_t"], M["tide"],
                           margin=0.0, collider=False)
        # (2) cheek outer-face tide — only the 0.10 exposed above the bank is banded.
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a = sgn * (ck["y_out"] - 0.002)
            b = sgn * (ck["y_out"] + wt["tide_proud"])
            sc.build_slope(stage, f"{ROOT}/Tide/Cheek_{tag}", x0,
                           z_ck - wt["tide_drop"], run, run * SLOPE_K,
                           min(a, b), max(a, b), wt["tide_h_cheek"],
                           M["tide"], margin=0.0, collider=False)
        # (3) distant facade base tide — band at the foot of building C's facade (x=28)
        bC = PARAMS["buildings"]["C"]
        BOX(f"{ROOT}/Tide/FacadeC",
            (bC["facade_x"] - 0.012, (bC["y0"] + bC["y1"]) / 2.0,
             LOWER_TOP + th / 2.0),
            (0.030, bC["y1"] - bC["y0"], th), M["tide"])
        # (4) riser run-down streaks — vertical bands standing 3mm proud of the riser face.
        #    proud is staggered by k%3 so overlaps on the same step are never coplanar.
        # [GT-115 ④] The centre offset carried the **wrong sign**. `xa + (0.020 - pr)/2`
        #    with a 0.020+pr box spans x = xa−pr … xa+0.020, i.e. the 20 mm that is meant
        #    to be the burial depth sat on the **air** side and only pr (3.0~4.0 mm) was
        #    inside the solid. Because `_stair_steps` descends towards +X, the riser face
        #    at x=xa is exposed towards **+X** (step i−1's solid is at x<xa), so each band
        #    cantilevered 20 mm out over the tread below, showing its own top and side
        #    faces. Bound to the near-black `tide` constant that read as free-standing
        #    ~0.10 x 0.12 m black boxes standing on the treads — 5 of the 14 fall inside
        #    the pt_noon_lower_lookback crop (300,620–900,960) [computed], which is the
        #    audit's "unexplainable as any construction · CG artefact".
        #    Negating the offset gives x = xa−0.020 … xa+pr: 20 mm buried in the riser,
        #    pr proud, exactly what the line above has always described. Seed, count,
        #    y positions, widths and the z ladder are untouched, so the streaks stay the
        #    same dark run-down bands — they simply lie on the riser instead of standing
        #    on the tread.
        rng = random.Random(int(wt["streak_seed"]))
        for k in range(int(wt["streak_n"])):
            i = rng.randint(2, st["nsteps"] - 1)
            y = rng.uniform(st["y0"] + 0.25, st["y1"] - 0.25)
            xa = st["x0"] + st["tread"] * (i - 1)
            zt = st["z_top"] - st["riser"] * i
            z_lo = zt + 0.005                    # clear of the tread film
            z_hi = zt + st["riser"] - 0.025      # clear of the film above
            pr = wt["streak_proud"] + (k % 3) * 0.0005
            w = wt["streak_w"] * rng.uniform(0.55, 1.45)
            BOX(f"{ROOT}/Tide/Streak_{k}",
                (xa - (0.020 - pr) / 2.0, y, (z_lo + z_hi) / 2.0),
                (0.020 + pr, w, z_hi - z_lo), M["tide"])
        print(f"[비] 치크 러노프 2 · 치크 tide 2 · 파사드 tide 1 · "
              f"라이저 스트릭 {int(wt['streak_n'])}줄 "
              f"(seed={wt['streak_seed']})")

    # -------------------------------------------------------------------
    # Cue — nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"],
                st["y0"] + ns["y_inset"], st["y1"] - ns["y_inset"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])
        # [W2 §12.4] Tactile paving is **executed by ground_kit** (`build_ground_kit`).
        #   (1) today's `sc.build_tactile` is a flat constant-colour plate with no studs,
        #      so the statutory 36 studs cast zero shading on screen (§12.5 (3)).
        #   (2) the position changes too — **1.0 m in front**, not the statutory 0.3 m
        #      (non-compliance reproduced). Laying it twice would double it, so not here.
        #   The toggle (`cue_tactile`) is read as-is by `ground_plans()`.
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]
            ck = PARAMS["cheek"]

            def cheek_ground(x):
                """Post landing surface: upper plaza top for x<=0, cheek band top for x>0.
                (The cheek band exists only along the stair run, so the posts on the
                 level extension land on the plaza — the rail top therefore sits proud
                 lower than the cheek band at 0.84m, which is the statutory 0.9m when
                 measured from the plaza.)"""
                if x <= 0.0:
                    return 0.0
                return ck["proud"] - SLOPE_K * min(x, RUN)

            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                sc.build_railing_line(
                    stage, f"{ROOT}/StairRail_{tag}", sgn * rl["y"],
                    rl["x_start"], st["x0"], RUN, DROP, cheek_ground,
                    M["rail"], rail_h=rl["rail_h"], post_r=rl["post_r"],
                    spacing=rl["spacing"], rail_r=rl["rail_r"],
                    rail_mid_r=rl["rail_mid_r"],
                    rail_mid_drop=rl["rail_mid_drop"])

    # -------------------------------------------------------------------
    # [W2] ground_kit — P3 sidewalk_block. Honouring the condition overlay (wetness),
    #   patches take the `wet_surface` toggle's material while joints and grime take
    #   the tide / half-dry materials. **Geometry is identical either way** (twin rule).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        patch_mtl = M["tread_wet"] if cfg["wet_surface"] else M["plaza"]
        M2 = dict(M)
        M2.update(joint=M["stone_damp"], crack=M["stone_damp"],
                  patch=patch_mtl, patch_cut=M["cheek"], manhole=M["gk_iron"],
                  gully=M["gk_iron"], gutter=M["cheek"], weed=M["shrub"],
                  tactile=M["tactile"], stain_dirt=M["gk_stain"],
                  stain_gum=M["gk_stain"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneC4 P3 · 프림 {res['prims']} · 산포 "
              f"{res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"wet={cfg['wet_surface']} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Dressing — 4 bollards + 2 distant buildings (horizon closure §A-4)
    # -------------------------------------------------------------------
    def build_dressing(M):
        # Bollards [v5.1 §2] — one row at the plaza entrance (5.6 m gap at centre), post +
        #   white band. The front dot tactile is off since [GT-115 ④] (see below).
        bo = PARAMS["bollard"]
        # [GT-115 ④] Per-bollard dot tactile **off** (`tactile=False`). The pad is a
        #   0.30 x 0.40 m slab flush against each post (x −6.36…−6.06, y cy+-0.20), and
        #   from lower_lookback the two +Y posts print it as isolated yellow fragments at
        #   px 1316..1367 / 1491..1547 — inside the audit crop (1000,440–1600,560), and
        #   0.6~1.6 m of bare granite away from the actual warning band at x −1.60…−1.00
        #   [computed], so it reads as debris rather than as guidance. The statutory
        #   점형블록 marks a crossing or a stair head, not the foot of every post on an
        #   open plaza; this row has no carriageway to guard (5.6 m pedestrian gap at
        #   centre) and the stair head already carries its own band. Same call the other
        #   five batch1 bollard scenes make (D1/N1/N2/N3/N4). Post, white band, spacing,
        #   row geometry and `bollard.front` are untouched.
        for name, bx, by in bollard_points():
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{name}", bx, by, 0.0,
                                 None, M["rail"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["radius"], height=bo["height"],
                                 tactile=False)
        # [v3 arm C · datum] This IS the sceneC2 `Z_LOW` switch and it is
        #   already correct for `keep_dressing`: the module guard makes
        #   `hazard_stairs` False whenever KEEP_DRESSING is True, so the
        #   lower-anchored building plinths already read 0.0 = the FlatFill
        #   top and ride the fill. Writing `or KEEP_DRESSING` here would be a
        #   no-op. Left untouched on purpose.
        low_base = LOWER_TOP if cfg["hazard_stairs"] else 0.0
        for key, bd in PARAMS["buildings"].items():
            b = dict(bd)
            # level="lower" (plinth at lower plaza) / "upper" (plinth at upper plaza)
            b["base_z"] = low_base if bd.get("level", "upper") == "lower" \
                else 0.0
            sc.build_building(stage, f"{ROOT}/Building_{key}", b,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_civic(M)

    # -------------------------------------------------------------------
    # Context dressing v2 — sense of place: a grand stair before a civic hall
    #   planter pairs · plaza lamps · flagpoles · sculpture · distant colonnade.
    #   Everything stands on flat ground (upper plaza z=0 / lower plaza z=LOWER_TOP),
    #   and every lower prop sits at x>5.5, farther than the stairs (x 0..4.9) = no occlusion.
    #   Vertical elements (lamps · flagpoles · capitals) were placed inside the
    #   grazing_mirror/approach frames so they catch the wet-paving reflection.
    # -------------------------------------------------------------------
    def build_civic(M):
        wet = cfg["wet_surface"]
        # [v3 arm C · datum] Same `Z_LOW` switch as `build_dressing`, same
        #   verdict: KEEP_DRESSING implies hazard_stairs=False, so the
        #   sculpture · colonnade · lower planters already sit on 0.0 = the
        #   FlatFill top. No KEEP_DRESSING term is needed or added.
        low = LOWER_TOP if cfg["hazard_stairs"] else 0.0

        def base_of(kind):
            return low if kind == "lower" else 0.0

        def tide_band(path, cx, cy, sx, sy, z_base):
            """[rain package] Wet band at the base of vertical structures (proud 12mm)."""
            if not wet:
                return
            h = wt["tide_h"] * 0.8
            BOX(path, (cx, cy, z_base + h / 2.0),
                (sx + 2.0 * wt["tide_proud"], sy + 2.0 * wt["tide_proud"], h),
                M["tide"])

        # (1) large planter pairs (kerb + cap + soil + 3 shrubs)
        pl = PARAMS["planter"]
        _pls, _lms = civic_placements()                # v5.1 §3 placement jitter
        for i, pcx, pcy, pd in _pls:
            bz = base_of(pd["base"])
            pfx = f"{ROOT}/Planter_{i}"
            sc.build_planter(stage, pfx, pcx, pcy, bz,
                             M["cheek"], M["shrub"], tree_mtls=None,
                             size=pd["size"], curb_h=pl["curb_h"],
                             curb_t=pl["curb_t"], cap_over=pl["cap_over"],
                             cap_h=pl["cap_h"], grass_h=pl["soil_h"])
            r = pl["shrub_r"] * (pd["size"] / 2.0)
            for j, (dx, dy, s) in enumerate(((0.0, 0.0, 1.0),
                                             (0.26, -0.20, 0.78),
                                             (-0.24, 0.22, 0.72))):
                sc.add_sphere(stage, f"{pfx}/Shrub_{j}",
                              (pcx + dx * pd["size"] * 0.5,
                               pcy + dy * pd["size"] * 0.5,
                               bz + pl["soil_h"] + r * s * 0.45),
                              (r * s, r * s, r * s * 0.72), M["shrub"])
            tide_band(f"{pfx}/Tide", pcx, pcy, pd["size"],
                      pd["size"], bz)

        # (2) plaza lamps — the key element making vertical reflections on wet paving
        lm = PARAMS["plazalamp"]
        for i, lcx, lcy, ld in _lms:
            bz = base_of(ld["base"])
            pfx = f"{ROOT}/PlazaLamp_{i}"
            CYL(f"{pfx}/Base", (lcx, lcy, bz + lm["base_h"] / 2.0),
                lm["base_r"], lm["base_h"], M["cheek"], col=True)
            CYL(f"{pfx}/Pole",
                (lcx, lcy, bz + lm["pole_h"] / 2.0 + 0.20),
                lm["pole_r"], lm["pole_h"], M["rail"], col=True)
            CYL(f"{pfx}/Head",
                (lcx, lcy,
                 bz + lm["pole_h"] + 0.20 + lm["head_h"] / 2.0 - 0.04),
                lm["head_r"], lm["head_h"], M["parapet"])
            tide_band(f"{pfx}/Tide", lcx, lcy, lm["base_r"] * 2.0,
                      lm["base_r"] * 2.0, bz)

        # (3) 3 flagpoles + granite plinth (upper plaza +Y · lookback only)
        fl = PARAMS["flag"]
        cy_mid = sum(fl["cys"]) / len(fl["cys"])
        py = (max(fl["cys"]) - min(fl["cys"])) + 2.0 * fl["plinth_pad"]
        BOX(f"{ROOT}/Flag/Plinth",
            (fl["cx"], cy_mid, fl["plinth_h"] / 2.0),
            (2.0 * fl["plinth_pad"], py, fl["plinth_h"]), M["cheek"], col=True)
        for i, fy in enumerate(fl["cys"]):
            CYL(f"{ROOT}/Flag/Pole_{i}",
                (fl["cx"], fy, fl["plinth_h"] + fl["pole_h"] / 2.0 - 0.10),
                fl["pole_r"], fl["pole_h"], M["rail"], col=True)
            sc.add_sphere(stage, f"{ROOT}/Flag/Finial_{i}",
                          (fl["cx"], fy,
                           fl["plinth_h"] + fl["pole_h"] - 0.10
                           + fl["finial_r"]),
                          (fl["finial_r"],) * 3, M["parapet"])
        tide_band(f"{ROOT}/Flag/Tide", fl["cx"], cy_mid,
                  2.0 * fl["plinth_pad"], py, 0.0)

        # (4) sculpture plinth + monolith (lower plaza +Y · in the grazing/approach frames)
        sp = PARAMS["sculpture"]
        bz = base_of(sp["base"])
        BOX(f"{ROOT}/Sculpture/Plinth",
            (sp["cx"], sp["cy"], bz + sp["plinth_h"] / 2.0),
            (sp["plinth"], sp["plinth"], sp["plinth_h"]), M["cheek"], col=True)
        BOX(f"{ROOT}/Sculpture/Mono",
            (sp["cx"], sp["cy"],
             bz + sp["plinth_h"] + sp["mono_h"] / 2.0 - 0.05),
            (sp["mono_w"], sp["mono_w"], sp["mono_h"]), M["plaza"], col=True)
        tide_band(f"{ROOT}/Sculpture/Tide", sp["cx"], sp["cy"], sp["plinth"],
                  sp["plinth"], bz)

        # (5) distant colonnade — stylobate + column row + entablature
        co = PARAMS["colonnade"]
        bz = base_of(co["base"])
        sty_cx = (co["sty_x0"] + co["sty_x1"]) / 2.0
        sty_y0 = co["y0"] - co["sty_pad"]
        sty_y1 = co["y1"] + co["sty_pad"]
        BOX(f"{ROOT}/Colonnade/Stylobate",
            (sty_cx, (sty_y0 + sty_y1) / 2.0, bz + co["sty_h"] / 2.0),
            (co["sty_x1"] - co["sty_x0"], sty_y1 - sty_y0, co["sty_h"]),
            M["plaza"], col=True)
        n_col = int(round((co["y1"] - co["y0"]) / co["step"])) + 1
        z_col = bz + co["sty_h"]
        for i in range(n_col):
            cyc = co["y0"] + co["step"] * i
            CYL(f"{ROOT}/Colonnade/Col_{i}",
                (co["x_c"], cyc, z_col + co["col_h"] / 2.0 - 0.05),
                co["col_r"], co["col_h"], M["plaza"], col=True)
        BOX(f"{ROOT}/Colonnade/Beam",
            (co["x_c"], (co["y0"] + co["y1"]) / 2.0,
             z_col + co["col_h"] + co["beam_t"] / 2.0 - 0.10),
            (co["col_r"] * 3.4, (co["y1"] - co["y0"]) + 2.0 * co["beam_pad"],
             co["beam_t"]), M["parapet"])
        if wet:
            BOX(f"{ROOT}/Colonnade/Tide",
                (sty_cx, (sty_y0 + sty_y1) / 2.0, bz + co["sty_h"] * 0.55),
                (co["sty_x1"] - co["sty_x0"] + 2.0 * wt["tide_proud"],
                 sty_y1 - sty_y0 + 2.0 * wt["tide_proud"], co["sty_h"] * 0.9),
                M["tide"])
        print(f"[드레싱] 화분 {len(PARAMS['planters'])} · 가로등 "
              f"{len(PARAMS['plazalamps'])} · 게양대 {len(fl['cys'])} · "
              f"조형물 1 · 열주 {n_col}주 · 파사드 "
              f"{len(PARAMS['buildings'])}동")

    # ── Scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["stone_damp"] if cfg["cue_material_break"] else M["plaza"]

    if cfg["hazard_stairs"]:
        build_upper(M)
        build_lower(M)
        build_banks(M)
        build_cheeks(M)
        build_stairs(stair_mtl)
        build_tread_films(M)          # geometry always identical — only the material is wet/dry
        build_cues(M)
        if cfg["wet_surface"]:
            build_water(M)
            build_rain_marks(M)
    elif KEEP_DRESSING:
        # [v3 arm C] hazard-only removal. The flat control's ground is reused
        #   verbatim — unlike scene12's, this scene's `FlatFill` IS the ON
        #   arm's UpperPlaza slab extended east (same y span, same top
        #   `upper.z_top`, same `upper.thick`, same `skin_exclude`), so over the
        #   whole camera strip (x<0) it is the identical surface at the
        #   identical z and the camera datum cannot move. What the plain OFF
        #   arm additionally loses, and this arm gets back, is `build_cues` —
        #   the stair railing (`cue_railing`, ON by default), which is the cue
        #   this arm exists to ask about. Not rebuilt, and deliberately: the
        #   tread water films / rain streaks are plated onto the step and cheek
        #   faces, and `wet_surface` is a material feature, not a `cue_*` key
        #   (CUE_COVERAGE §2.3 `Sp`). Tactile paving is NOT here either — it is
        #   laid by `build_ground_kit`, which runs in every arm already.
        build_flat_fill(M)
        build_cues(M)               # the descending railing line, ON transform
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements — after dressing (scatter rule)

    print(f"[기하] run={RUN:.2f}m drop={DROP:.2f}m slope_k={SLOPE_K:.4f} "
          f"lower_top={LOWER_TOP:.3f} wet={cfg['wet_surface']} "
          f"rough={wt['wet_rough'] if cfg['wet_surface'] else 'tex'}")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneC4 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["approach"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneC4_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[하늘 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[하늘 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
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
