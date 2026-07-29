# -*- coding: utf-8 -*-
"""
scene18_wavy_artstair.py - NegObs synthetic scene 18: neighbourhood mural (painted) stair
(Isaac Sim 4.5)

Spec            : Docs/briefs/multi_scene_brief_v5.md §reinterpretation (scene18) - replaces v3 §D
Shared library  : scene_common.py (§A) - boot·make_pbr·add_box·lighting·capture
Motif reference : scene05_amphitheater.py (main skeleton·cue toggles·dressing)

[v5 adopted] stage reinterpreted: 'artistic wavy stair' -> **culture-village painted stair**.
  The geometry is pulled back toward a standard stair (phase 0.4->0.25, amp 0.35->0.245 = 30 %
  reduction) and only the colour variation (camouflage) is kept. 5 colours retained. Drop 2.56 m (16x0.16) unchanged.
  Derived geometry (cheek wall, upper walkway wave edge segs) reads amp/phase through functions, so it
  **follows automatically** - `_wave_selfcheck()` verifies it by coordinates (NEGOBS_SMOKE=1).

Type identity: high-contrast colour actually disrupts drop perception (camouflage contrast group).
  16 steps, each step approximated by 24 y-seg boxes so that the nosings form a gentle sine
  (amplitude 0.245, wavelength 4 m). Riser faces alternate through 5 saturated colours (constant colour). Treads are bright concrete.
  cue_nosing False by default - the colour blurs where the nosings are and impedes hazard perception.

[v6 verdict - re-revised] "the sea horizon is unseen in all 13 cuts / the mural is colour blocks (Lego) /
  sliver breakup on the slope / sawtooth parapet on the cheek wall". Actions:
    (a) coast rebuilt - ground east end x1 50->34 (= shoreline), water top −4.40->−3.35,
       the town moved off the stair view axis (|y|<13) into north and south clusters. -> horizon exposed in every +X cut
       (check `_sea_selfcheck`, frame openness 54~100 %). oblique_down re-aimed +
       new sea_beauty cut.
    (b) mural - 5 primary colours -> 7 low-saturation colours x 3 wear variants, colour boundaries as **diagonal continuous bands**.
    (c) slivers - upper seg minimum width 0.052->0.203 m, nseg 24->40 (side notch 0.128->0.077).
    (d) cheek wall - stepped sawtooth scrapped -> oblique haunch parallel to the nosing line (scene14 method).
  The wavy stair surface and the 2.56 m drop (hazard geometry GT) are all unchanged.

Run / capture / smoke : same env convention as scene05·scene06.
    NEGOBS_CAPTURE=1 / NEGOBS_SMOKE=1 / NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG
    NEGOBS_SELFCHECK=1 : coordinate check only, without booting Isaac (wave + horizon)

Coordinates: Z-up, m, travel axis +X. Top (behind step 1) corner x~0, treads descend toward +X.
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
# [A] SCENE_CONFIG - 7 keys. hazard_stairs = wavy stair geometry toggle (<-> flat plaza).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # wavy stair (False -> flat z=0 mini plaza)
    "cue_railing":        False,   # art-stair identity: open - no railing at all
    "cue_tactile":        False,   # True -> warning tactile strip at the top
    "cue_material_break": True,    # upper (plaza_light) vs lower (plaza_lower) walkway
    "cue_nosing":         False,   # identity: colour camouflage - no nosing anti-slip by default
    "cue_sign":           False,   # [reserved]
    "cue_scene_dressing": True,    # bench, streetlight, planter, building
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # wavy stair: 16 steps, riser 0.16, tread 0.34, y segs 8 (-4..4). Front-edge x offset
    #   = amp*sin(2pi*y_j/wavelength + i*phase) (phase shifts per step -> the wave flows down)
    #   nseg 24 - softens sine faceting and vertical seams (hotfix)(offset continuous across adjacent segs) [A-18(2)]
    # [v5 adopted] wave relaxed -> **neighbourhood mural (painted) stair**. Geometry pulled back
    #   toward a standard stair, only the colour variation (camouflage) is kept. 5 colours retained.
    #     phase 0.4 -> 0.25 · amp 0.35 -> 0.245 (30 % reduction)
    #   min exposed tread of step 1 = tread - 2·amp·|sin(phase/2)|
    #     old: 0.34 - 2(0.35)sin(0.20) = 0.34 - 0.1391 = **0.201**
    #     new: 0.34 - 2(0.245)sin(0.125) = 0.34 - 0.0611 = **0.279** (max 0.401)
    #   riser 0.16 x 16 steps = drop 2.56 m **unchanged** (hazard geometry GT preserved).
    # [v6 verdict (c)] nseg 24 -> 40. The front-edge x difference between seg j and j+1 (= seg-to-seg
    #   stepping of the wave) is at most amp·k·Wb = 0.245·(2pi/4)·(8/nseg), and over that width the
    #   **side face (y normal)** of the neighbouring seg is exposed, becoming a self-shadow
    #   triangular notch under noon light (= the "dozens of paper slivers" in oblique_down). 24 -> 40 gives 0.128 -> 0.077 m.
    #   The wave surface _front_x(i,y) itself is unchanged, so **hazard geometry GT is unchanged** (refinement only).
    stair=dict(n=16, riser=0.16, tread=0.34, nseg=40, y0=-4.0, y1=4.0,
               amp=0.245, wavelength=4.0, phase=0.25, base_z=-3.0),
    # Riser colour = 0.05-thick solid box, front face embedded 5 mm (overlaps the stair solid ->
    #   seals the top opening, prevents the 'trough' look), height riser+0.005 (1 mm below the tread above) [A-18(1)]
    riser_panel=dict(thick=0.05, proud=0.005, embed=0.045, top_gap=0.001,
                     over=0.005),
    # Upper/lower walkway (material break) - solid slab (down to ground -3.01)
    #   x0=-15.0 : terrace extended to the facades of the two west shops (D/E), removing a 3 m cliff [D-18(1)]
    #   follow_wave=True : the east edge is split into nseg segments following the stair-head back
    #     corner _front_x(-1,y). The old straight edge (x=0.5) buried 1-2 steps at the wave troughs,
    #     making the first level difference swing 0.16/0.32/0.48 m (audit A-18 A1, critical).
    #   x0=-15.2 : bitten 0.2 m into the building facade (x=-15.0) to avoid coplanar Z-fighting
    #   [v6 verdict (c)] seg_min_w : **lower bound on the x width** of a wave-following seg. The old code
    #     used x_cut = -amp-0.05, so a trough seg became a **paper-thin slab** of 0.052 m x 3.01 m
    #     height (the real cause of the breakup on the right of oblique_down). Raised 0.05 -> 0.20
    #     to secure a 0.202 m floor (verdict recommended >= 0.15). The east edge (stair joint face) is
    #     unchanged, so the uniform 0.16 first level difference stays as is.
    upper=dict(x0=-15.2, x1=0.5, y0=-9.0, y1=9.0, top_z=0.0, follow_wave=True,
               seg_min_w=0.20),
    # x0=5.05 : 0.04 inside the last step's minimum front edge 5.09 (= 5.44-0.35) -> removes the 0.11 m slot
    # top_z=-2.57 : 1 cm clear of the last step's top face (-2.56) (avoids coplanar Z-fighting + shrinks the lip)
    lower=dict(x0=5.05, x1=16.0, y0=-9.0, y1=9.0, top_z=-2.57),
    # Ditch-sealing skirt outside the stair width (|y| 4..9) - between the upper walkway edge (x=0.5) and the lower walkway [A5]
    skirt=dict(x0=0.5, y_in=4.0, y_out=9.0),

    # ═══ [W2-D ground_kit] P1 plaza_granite - spec §5.1 scene18 row ═══════════
    #  Row prescription: "slab joints made geometric · sand drift band · salt
    #  efflorescence (albedo cap 0.30 strictly) · patches 3 per 20 m";
    #  drift band = "seaward edge of the paving".
    #  ★ Tactile **OFF** (§12.4): "18 = wave-form, irregular — laying a 300 mm
    #    grid on it is not practice". `TACTILE_OFF_REASON["scene18"]` records it.
    #  ★ Edge s = **-amp (-0.245)**, not 0. The drop edge of this scene is the
    #    wavy stair head `_front_x(-1, y) = amp*sin(...)`, i.e. a band between
    #    -0.245 and +0.245, and GT-E1'/GT-E2 must be measured from its
    #    **nearest** point or the standoff is optimistic by one amplitude.
    #  ★ Drift band orientation: `build_silt_band` emits X-long strips at
    #    y = const, so it cannot draw a band along the seaward (x = const)
    #    edge — and that edge is the hazard edge anyway, inside the 0.80 m
    #    exclusion. The two bands are therefore placed on the walkway's
    #    **lee lateral margin** (y ~ -4.4/-3.9), which is where wind-driven
    #    sand actually piles up against a kerb. Recorded as a deviation.
    #  ★ "alley pole" (§5.4 15-10 analogue) is **allowed** in this scene but not
    #    placed: the pole body is props-team scope and there is no pole in
    #    PARAMS, and §7.4 forbids hard-coding a document coordinate. If props
    #    add one, its base grime/weed band is a `stain`/`weed` site here.
    gkit=dict(
        region=(-12.0, -5.0, -0.5, 5.0),
        edge_s=-0.245,                        # = -stair.amp (nearest wave trough)
        manholes=[(-4.0, 1.0), (-9.0, -1.0)],
        gullies=[(-2.5, -4.6), (-8.0, 4.6)],
        patches=[(-1.30, 0.20), (-3.80, -0.55), (-8.70, 0.40)],
        silt=dict(waterline=-4.60, width=0.45, n=2),
    ),
    # [v6 verdict (a)] the east end of the ground is the **shoreline**. The old x1=50 + water top -4.40
    #   combination meant a 1.39 m ground cut face had to be hidden by the town, and that town blocked
    #   the horizon entirely (horizon 0 in all 13 cuts). -> Cut the ground at x1=34 and lay the water
    #   from just under it (31) so the cut face becomes **0.34 m = a low quay**. With nothing left to hide,
    #   the town can be moved off the sight line.
    #   y half-width +-50 -> +-90 (so the ground edge never enters frame in lateral views).
    ground=dict(x0=-60.0, x1=34.0, y0=-90.0, y1=90.0, top_z=-3.01),
    # Seafront promenade (quay top finish) - removes the impression of grass meeting the sea directly
    quay=dict(x0=29.5, x1=34.0, y0=-90.0, y1=90.0, top_z=-3.005),
    # Dressing
    benches=[(-4.0, -6.0, 0.0, 0.0), (-4.0, 6.0, 0.0, 0.0),
             (8.0, -5.0, -2.57, 90.0), (8.0, 5.0, -2.57, 90.0),
             (12.0, -5.0, -2.57, 90.0), (12.0, 5.0, -2.57, 90.0)],
    # 4 streetlight rows (lines flanking the stair) + the existing single upper pole [D-18(2)]
    streetlights=[dict(x=-6.0, y=-7.5, base_z=0.0, pole_h=6.0),
                  dict(x=-1.0, y=-5.0, base_z=0.0, pole_h=5.0),
                  dict(x=-1.0, y=5.0, base_z=0.0, pole_h=5.0),
                  dict(x=6.5, y=-5.0, base_z=-2.57, pole_h=5.0),
                  dict(x=6.5, y=5.0, base_z=-2.57, pole_h=5.0)],
    streetlight=dict(pole_r=0.06, arm_len=1.0, arm_r=0.04, head=0.25),
    planters=[("A", -7.0, 7.0, 0.0), ("B", 10.0, 7.0, -2.57),
              ("C", 10.0, -7.0, -2.57)],
    # Bollards - [v5.1 §2] **removed entirely**.
    #   Feedback: "bollards do not fit". Under §2 a bollard is a functional fixture placed only where
    #   vehicle intrusion is a concern (sidewalk-roadway junction / plaza or ramp entry / directly in
    #   front of a stair approach), and this scene is a hillside alley mural stair with no roadway, so there is no basis.
    #   The old 8 posts (upper x -1.2 · lower x 6.4) were a purely decorative row, so they are deleted.
    # Stair side finish (cheek wall) [v5 verdict applied] - the end faces of the 24 wave segments
    #   were exposed bare at |y|=4.0, so the 2.57 m side above the skirt (-2.57) read like a grille or
    #   cavity (= right side of oblique_down), and at the same time the 2.57 m lateral drop from stair
    #   to skirt was unguarded. A stepped kerb reusing each step's own front/back x is raised at
    #   |y| 4.0..4.3. **The stair (hazard geometry) transform is unchanged** - it is a finish added only
    #   outside the stair width, so grazing concealment (stair exposure 0) is unaffected as well (its height is
    #   +0.14 above the adjacent tread, so it makes no drop silhouette from an h0.3 sight line).
    # [v6 verdict (d)] the old cheek wall had a top face at z_top+0.14 per step - a **stepped sawtooth parapet**
    #   - the same family of shape the user had scrapped in scene14, still surviving in 18.
    #   -> the per-step boxes now sit **flush with the tread (curb=0)** to kill the sawtooth,
    #     and an **oblique haunch** parallel to the nosing line (build_slope, 1 per side) is laid over them.
    #     Haunch top face z(x) = rise - (riser/tread)·x  (= nosing line + rise).
    #     Thickness 0.45 -> the haunch underside is 0.497 below the top face (= 0.45/cos 25.2 deg), so it
    #     always bites at least 0.08 m below the per-step box top (-0.16(i+1)) -> zero floating
    #     or gapping. The stair (hazard geometry) is |y|<4.0, the haunch is 4.0..4.3 - no intrusion.
    cheek=dict(w=0.30, curb=0.0, base_z=-2.72,
               rise=0.14, haunch_x0=-0.10, haunch_over=0.15, thick=0.45),
    # Edge parapet on the upper walkway |y| 4.2..9 (guards the drop to the skirt) [D-18(4)]
    parapet=dict(x0=0.2, x1=0.5, y_in=4.2, y_out=9.0, h=1.05),
    # 2 floor bands on the lower plaza (plaza scale cue) [D-18(6)]
    # [v6 verdict / v5.2 §6] the two dark grey albedo-0.045 bands were judged "unidentifiable straight
    #   bands" (oblique_down). They are scale decoration with no functional basis, so **deleted**
    #   (the builder path stays - refilling the list restores them).
    bands=[],
    buildings=dict(
        # Two low-rise shops beyond the stair (west) - fixes the upper half of the color_front and
        #   lower_lookback frames being 100 % sky. Grounded to the terrain (-3.01) via base_z [B1/D-18(1)]
        # [v6 verdict (e)] h 12/15 · 4-5 storeys read as **dark-red brick apartments**, in head-on conflict
        #   with the "low houses on a hill" narrative -> lowered to 2-storey shops (h 5.0/6.2).
        #   What was lowered is compensated by the hill fill terraces behind (tops 1.4/4.6/8.2) and the
        #   house silhouettes on them, so the upper half of the frame stays filled (no return of 100 % sky):
        #   elevation angles from lower_lookback - shops 8.2 deg < hill1 11.3 deg < hill2 13.9 deg
        #   < hill3 15.3 deg, tiering upward.
        D=dict(x0=-24.0, x1=-15.0, y0=-14.0, y1=-1.0, h=5.0, floors=2,
               axis="x", facade_x=-15.0, face_dir=1.0, base_z=-3.01),
        E=dict(x0=-24.0, x1=-15.0, y0=1.0, y1=14.0, h=6.2, floors=2,
               axis="x", facade_x=-15.0, face_dir=1.0, base_z=-3.01),
        # [v5.1] the old C (x 44..54, h 15) was a high-rise wall blocking the entire +X horizon.
        #   With the seaside-hill identity fixed it is **deleted** - the horizon below the stair (+X) is
        #   closed by the low-roof skyline of seaside["town"] below plus the sea horizon.
    ),

    # === [v5.1 realism] identity fixed: **seaside hill mural stair** ===
    #   Feedback: "feels like a seaside mural stair - the positioning needs to be settled."
    #   The stair descends from the hill (-X, high) toward the sea (+X, low). Therefore
    #     · **below the stair (+X)** = shoreline -> sea horizon (the view axis)
    #     · **flanking the stair (+-Y)**   = low-rise town (seated off the view axis)
    #     · **above the stair (-X)**   = hillside house silhouettes (on stepped fill)
    # [v6 verdict (a) - structural rework] the old layout was "lay the water under the ground (-4.40)
    #   and hide the 1.39 m cut face with the town", but that town **hid the horizon along with it**
    #   (horizon 0 in all 13 cuts = identity not met). The cause: at low eye heights (h0.35-1.8) the
    #   horizon sits at -0.4 to -5 deg while the town roofs sit at +2 to +7 deg, so it cannot win structurally.
    #   -> **remove the cut face that needs hiding**: cut the ground at x1=34 (shoreline) and lay the water
    #   right below it at -3.35, shrinking the cut face to 0.34 m so it reads as a quay.
    #   The town retreats off the stair view axis (|y| < 13) into north and south clusters.
    #   _sea_selfcheck() runs the numeric check per cut (raycasts the +-30 deg frame at 5 deg steps).
    seaside=dict(
        # Water: haze tone (low saturation, mid value) + low roughness - a distant-horizon impression
        # [v6 verdict (a)] top_z -4.40 -> **-3.35** (0.34 m just below the ground top -3.01).
        #   x0 46 -> 31 (3 m inside the ground east end 34 = bitten into the 1.0 ground thickness so the
        #   joint has zero opening). Now even from a low eye (h0.35) the water band shows not above the
        #   roofs but **beyond and below the ground** - the very reason for the town to hide it disappears.
        water=dict(x0=31.0, x1=530.0, y0=-560.0, y1=560.0,
                   top_z=-3.35, thick=1.2),
        water_color=(0.175, 0.205, 0.225), water_rough=0.22,
        # Low-roof skyline (x0, x1, y0, y1, h, floors) - roof caps come from roof below
        #   No even spacing or grid (§3): x, y, height and width are all scattered irregularly.
        # [v6 verdict (a)] the old layout was a **two-row wall** squarely blocking the stair descent axis
        #   (|y| <~ 13) (x 21..42.5 x y -34..38). In a real seaside stair town the stair axis *is* the
        #   view axis and the houses sit **to either side** -> the central corridor |y| < 13 is cleared
        #   and the town regrouped into north and south clusters (x 17..32.5, inside the ground).
        #   Heights are lowered to 3.0-5.6 (1-2 storeys) as well.
        town=[(18.0, 23.5, -40.0, -32.5, 3.4, 1), (21.0, 26.5, -31.0, -24.0, 5.0, 2),
              (17.5, 22.5, -22.5, -15.5, 3.0, 1),
              (26.5, 32.0, -37.0, -29.5, 4.6, 2), (28.0, 32.5, -28.0, -20.0, 3.2, 1),
              (25.5, 31.0, -18.5, -13.5, 5.4, 2),
              (18.5, 24.0, 13.0, 20.0, 3.6, 1), (21.5, 27.0, 21.5, 29.0, 5.2, 2),
              (17.0, 22.0, 30.5, 37.0, 3.0, 1), (20.0, 25.5, 38.5, 45.0, 4.4, 1),
              (26.0, 31.5, 14.5, 22.0, 4.8, 2), (28.5, 32.5, 23.5, 31.0, 3.2, 1),
              (25.0, 30.5, 32.5, 40.0, 5.6, 2)],
        roof=dict(over=0.35, t=0.28),      # roof cap (0.35 eaves overhang) - town silhouette
        roof_color=(0.115, 0.085, 0.070), roof_rough=0.75,
        # 3 hill fill terraces (x0, x1, top_z) - full y width. The uphill side (-X) of the stair rises.
        terraces=[(-33.0, -26.0, 1.4), (-40.0, -33.0, 4.6), (-50.0, -40.0, 8.2)],
        terrace_y=(-46.0, 46.0),
        # Hillside houses (x0, x1, y0, y1, base_z, h) - grounded on the terrace tops, irregular layout
        houses=[(-31.5, -27.0, -41.0, -35.5, 1.4, 3.8),
                (-32.0, -27.5, -33.0, -27.0, 1.4, 4.4),
                (-31.0, -26.5, -24.5, -18.5, 1.4, 3.5),
                (-32.5, -27.0, 17.5, 23.5, 1.4, 4.1),
                (-31.5, -26.5, 25.5, 32.0, 1.4, 3.6),
                (-32.0, -27.5, 34.0, 40.5, 1.4, 4.6),
                (-38.5, -34.0, -38.0, -31.5, 4.6, 4.0),
                (-39.0, -33.5, -29.0, -22.0, 4.6, 3.4),
                (-38.0, -33.5, -13.0, -6.0, 4.6, 4.5),
                (-39.0, -34.5, 6.5, 13.0, 4.6, 3.9),
                (-38.5, -34.0, 21.0, 27.5, 4.6, 4.3),
                (-39.5, -34.0, 30.0, 37.0, 4.6, 3.6),
                (-47.0, -41.5, -34.0, -27.0, 8.2, 3.7),
                (-46.5, -41.0, -18.0, -11.0, 8.2, 4.2),
                (-47.5, -42.0, 2.0, 9.0, 8.2, 3.5),
                (-46.0, -41.0, 15.0, 22.0, 8.2, 4.4),
                (-47.0, -41.5, 28.0, 35.0, 8.2, 3.8)],
        house_color=(0.30, 0.29, 0.27), house_rough=0.75,
        # [v6] verdict (5) "clones of untextured white boxes". Wall and roof variants raised 3 -> 5, and
        #   not only value but **hue** (warm/cool) is shaken - painted walls of a harbour town.
        house_var=((0.90, 0.89, 0.87), (1.00, 0.98, 0.94), (1.10, 1.04, 0.96),
                   (0.94, 0.99, 1.06), (1.16, 1.10, 1.00)),
        roof_var=((0.85, 0.88, 0.95), (1.00, 0.96, 0.92), (1.12, 1.00, 0.90),
                  (0.92, 0.90, 1.00), (1.05, 1.08, 1.10)),
    ),

    material=dict(
        scale=dict(concrete_floor=1.2, plaza_light=1.80, plaza_lower=0.8,
                   brick_red=2.0, grass=1.4),
        tread_tint=(1.15, 1.15, 1.12),            # bright concrete tread
        lower_warm_tint=(1.06, 1.0, 0.94),
        # Riser colours - [v6 verdict (b)] the old 5 colours were primary solids (max/min channel ratio 7-9),
        #   so each step changed colour wholesale and read as a **stack of Lego blocks**. The verdict's
        #   recommendation, "continuous lateral bands + low saturation (a mural impression)", is implemented thus:
        #     (i) the palette grows to 7 colours with the channel ratio held below 2.2 - **mural mid-tones**
        #        (terracotta · mustard · sage · teal · blue · mauve-grey · cream). Max channel 0.52
        #        -> comfortably within §4 "no large areas of pure white (>0.8)".
        #     (ii) the colour index is keyed not to step i but to **i + (normalised y)·mural_skew**, so the
        #        colour boundaries become **continuous bands cutting diagonally across** the stair.
        #        (= colour boundaries and nosing boundaries no longer coincide -> the scene's identity,
        #          'colour camouflage', is in fact reinforced. skew 2.5 = a 2.5-step shift over the 8 m width)
        #     (iii) 3 per-seg wear tints (+-10 %) shake the value even within one band, softening both the
        #        solid-panel impression and the vertical seams.
        riser_colors=[(0.42, 0.24, 0.19), (0.50, 0.40, 0.20),
                      (0.30, 0.38, 0.27), (0.20, 0.34, 0.36),
                      (0.22, 0.30, 0.42), (0.36, 0.28, 0.34),
                      (0.52, 0.49, 0.42)],
        mural_skew=2.5,
        mural_wear=(0.88, 1.0, 1.09),
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [v5.1 §4] parapet 0.90 -> 0.72 (no large areas of pure white)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene18")


# ===========================================================================
# [C] wave front-edge offset (pure maths - no pxr needed)
# ===========================================================================
def _seg_centers():
    s = PARAMS["stair"]
    Wb = (s["y1"] - s["y0"]) / s["nseg"]
    return [s["y0"] + (j + 0.5) * Wb for j in range(s["nseg"])], Wb


def _front_x(i, y):
    """Front-edge x of step i. i=−1 is the top back corner. Phase i*phase makes the wave flow down."""
    s = PARAMS["stair"]
    k = 2.0 * math.pi / s["wavelength"]
    return (i + 1) * s["tread"] + s["amp"] * math.sin(k * y + i * s["phase"])


# ===========================================================================
# [C2] [v5 adopted] wave-relaxation self-check - confirms **by coordinates** that the cheek wall
#      and upper-edge segs follow automatically (no Isaac boot needed, pure maths).
# ===========================================================================
def _wave_selfcheck(verbose=True):
    """Coordinate check that an amp/phase change is reflected automatically in the derived geometry.

    (1) Cheek wall (|y| 4.0..4.3): the x interval of step i is taken as _front_x(i−1/i, y1).
       Wave phase identity - since k = 2π/wavelength = 2π/4,
         y=+4 : sin(k·4  + iφ) = sin( 2π + iφ) = sin(iφ)
         y=−4 : sin(k·(−4)+ iφ) = sin(−2π + iφ) = sin(iφ)
       **both sides always have the same phase** -> this holds regardless of the phase/amp values (because
       the 4 m wavelength divides the 8 m stair width into exactly 2 periods). Re-confirmed numerically below.
    (2) Upper walkway segs (follow_wave): x_cut = −amp − 0.05, seg east edge
       x1_j = _front_x(−1, yc_j) = amp·sin(k·yc_j − φ) ∈ [−amp, amp]
       -> x1_j − x_cut >= 0.05 for every seg (no negative-width slab).
    (3) Upper walkway straight edge at |y|>4: x=0.5 > max back corner (amp).
    (4) Lower walkway x0=5.05 < the last step's minimum front edge (= 16·tread − amp).
    Returns: (ok, diagnostics dict)
    """
    s = PARAMS["stair"]
    up, lo = PARAMS["upper"], PARAMS["lower"]
    ck = PARAMS["cheek"]
    yc, Wb = _seg_centers()
    # (1) cheek wall left/right phase identity
    dmax = max(abs(_front_x(i, s["y1"]) - _front_x(i, s["y0"]))
               for i in range(-1, s["n"]))
    # (2) seg width
    x_cut = -s["amp"] - up.get("seg_min_w", 0.05)
    wmin = min(_front_x(-1, y) + 0.002 - x_cut for y in yc)
    # (3) straight edge margin
    back_max = max(_front_x(-1, y) for y in yc)
    m3 = up["x1"] - back_max
    # (4) lower walkway overlap
    front_min = min(_front_x(s["n"] - 1, y) for y in yc)
    m4 = front_min - lo["x0"]
    # (5) exposed tread width (min/max) - hazard-perception difficulty metric
    tr = [_front_x(i, y) - _front_x(i - 1, y)
          for i in range(s["n"]) for y in yc]
    # (6) [v6] seg side notch - front-edge x difference between neighbouring segs (= exposed side width).
    #    The dimension actually responsible for the self-shadow triangular notches ("paper slivers").
    notch = max(abs(_front_x(i, yc[j + 1]) - _front_x(i, yc[j]))
                for i in range(s["n"]) for j in range(s["nseg"] - 1))
    # (7) [v6] cheek haunch - is the top face above the adjacent tread and the underside below the body top?
    kk = s["riser"] / s["tread"]
    def hz(x):                                    # haunch top face z(x)
        return ck["rise"] - kk * x

    hb = ck["thick"] / math.cos(math.atan(kk))    # top face -> underside vertical distance
    h_over, h_under = 1e9, 1e9
    for i in range(s["n"]):
        xa, xb = _front_x(i - 1, s["y1"]), _front_x(i, s["y1"])
        top_i = -s["riser"] * (i + 1) + ck["curb"]
        for x in (xa, xb):
            h_over = min(h_over, hz(x) - top_i)        # haunch top - body top
            h_under = min(h_under, top_i - (hz(x) - hb))  # body top - haunch underside
    ok = (dmax < 1e-9) and (wmin > 0.0) and (m3 > 0.0) and (m4 > 0.0) \
        and (min(tr) > 0.0) and (notch < 0.09) and (h_over > 0.0) \
        and (h_under > 0.0)
    diag = dict(cheek_lr_dx=dmax, seg_w_min=wmin, upper_edge_margin=m3,
                lower_overlap=m4, tread_min=min(tr), tread_max=max(tr),
                notch=notch, haunch_over=h_over, haunch_under=h_under,
                drop=s["n"] * s["riser"])
    if verbose:
        print("=" * 64)
        print("scene18 [v5] 물결 완화 자기검증 (amp=%.3f phase=%.3f)"
              % (s["amp"], s["phase"]))
        print("=" * 64)
        print(f"  ① 치크월 좌우 위상차  max|x(+4)−x(−4)| = {dmax:.3e}  "
              f"→ {'동일(자동 추종 OK)' if dmax < 1e-9 else 'FAIL'}")
        print(f"     치크월 x 구간(단 0) = "
              f"[{_front_x(-1, s['y1']):+.4f}, {_front_x(0, s['y1']):+.4f}] "
              f"@ |y| {s['y1']:.1f}..{s['y1'] + ck['w']:.1f}")
        print(f"  ② 상부 세그 최소 폭   {wmin:.4f} m (x_cut={x_cut:+.3f})  "
              f"→ {'OK' if wmin > 0 else 'FAIL'}")
        print(f"  ③ 직선 에지 여유      {m3:.4f} m (x1={up['x1']}, "
              f"back_max={back_max:+.4f}) → {'OK' if m3 > 0 else 'FAIL'}")
        print(f"  ④ 하부 보도 겹침      {m4:.4f} m (x0={lo['x0']}, "
              f"front_min={front_min:.4f}) → {'OK' if m4 > 0 else 'FAIL'}")
        print(f"  ⑤ 노출 디딤 폭        {min(tr):.4f} ~ {max(tr):.4f} m "
              f"(구 0.201~0.479)")
        print(f"  ⑥ 세그 측면 노치 최대 {notch:.4f} m (nseg={s['nseg']}, "
              f"구 nseg24 = 0.1276) → {'OK' if notch < 0.09 else 'FAIL'}")
        print(f"  ⑦ 치크 헌치           상면−몸통 {h_over:+.4f} · "
              f"몸통−밑면 {h_under:+.4f} → "
              f"{'OK(틈·부유 0)' if h_over > 0 and h_under > 0 else 'FAIL'}")
        print(f"  낙차(GT) {s['n'] * s['riser']:.2f} m — 불변")
        print("=" * 64)
    return ok, diag


# ===========================================================================
# [C3] [v6 verdict (a)] **sea horizon visibility check** - pure maths (no Isaac boot needed).
#   v6 verdict: "the sea horizon is visible in none of the 13 cuts. The occlusion check in the VC
#   fix log only looked at the ground cut face - **there was no horizon visibility check**."
#   -> that check is now pinned in code. Per cut, on the plane normal to the sight line:
#     · water band elevation range [a_near, a_far]
#         a_far  = elevation of the water far edge (x1) ~ the horizon
#         a_near = where a sight line grazing the ground east end (shoreline) meets the water
#     · occlusion elevation blk = max top-face elevation of obstacles (town, hill, shops, planters) on the sight plane
#     · frame = is it within the 18 deg vertical half-FOV (vFOV 36 deg, 16:9 at the default focal length)
#   Verdict: blk < a_far (horizon exposed) · a_far <= pitch+18 deg · a_near >= pitch-18 deg
# ===========================================================================
def _sea_selfcheck(verbose=True, cuts=("wave_raking", "oblique_down",
                                       "sea_beauty", "preset_h0.3_d5",
                                       "preset_h1.8_d10")):
    sea = PARAMS["seaside"]
    w, g = sea["water"], PARAMS["ground"]
    rf_h = 0.5                                   # build_building parapet height
    # (x0, x1, y0, y1, top_z) obstacles - only those that can block the +X sight line
    obs = [(x0, x1, y0, y1, g["top_z"] + h + rf_h)
           for (x0, x1, y0, y1, h, _f) in sea["town"]]
    for name, bd in PARAMS["buildings"].items():
        obs.append((bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["base_z"] + bd["h"] + rf_h))
    for px, py, bz in [(p[1], p[2], p[3]) for p in PARAMS["planters"]]:
        obs.append((px - 1.5, px + 1.5, py - 1.5, py + 1.5, bz + 3.2))
    views = build_views()
    diag, ok = {}, True
    for name in cuts:
        v = views[name]
        ex, ey, ez = v["eye"]
        tx, ty, tz = v["tgt"]
        dxh, dyh = tx - ex, ty - ey
        dh = math.hypot(dxh, dyh)
        ux, uy = dxh / dh, dyh / dh              # horizontal unit vector of the sight axis
        pitch = math.degrees(math.atan2(tz - ez, dh))
        if ux <= 1e-6:                           # cuts facing away from the sea (+X) are out of scope
            diag[name] = dict(skip=True)
            continue
        d_edge = (g["x1"] - ex) / ux             # horizontal distance to the shoreline
        slope = (g["top_z"] - ez) / d_edge
        d_near = (w["top_z"] - ez) / slope       # distance at which the sight line meets the water
        d_far = (w["x1"] - ex) / ux
        a_near = math.degrees(math.atan2(w["top_z"] - ez, d_near))
        a_far = math.degrees(math.atan2(w["top_z"] - ez, d_far))
        # Occlusion is swept not along a single sight axis but across the **full horizontal FOV (+-30 deg)**
        #   at 5 deg steps (looking only along the axis would pass even when the town blocks half the frame).
        base_az = math.degrees(math.atan2(uy, ux))
        blk, who, n_vis, n_ray = -90.0, "", 0, 0
        for m_ in range(-6, 7):
            aa = math.radians(base_az + 5.0 * m_)
            vx, vy = math.cos(aa), math.sin(aa)
            if vx <= 1e-6:
                continue
            n_ray += 1
            de = (g["x1"] - ex) / vx
            af = math.degrees(math.atan2(w["top_z"] - ez,
                                         (w["x1"] - ex) / vx))
            b_, w_ = -90.0, ""
            for x0, x1, y0, y1, top in obs:
                t0, t1 = 0.0, 1e9
                for a, u, lo, hi in ((ex, vx, x0, x1), (ey, vy, y0, y1)):
                    if abs(u) < 1e-9:
                        if a < lo or a > hi:
                            t0, t1 = 1.0, 0.0
                            break
                        continue
                    ta, tb = (lo - a) / u, (hi - a) / u
                    t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
                if t0 > t1 or t1 <= 0.0 or t0 > de:
                    continue
                ang = math.degrees(math.atan2(top - ez, max(t0, 0.5)))
                if ang > b_:
                    b_, w_ = ang, f"{x0:.0f}~{x1:.0f}"
            if b_ < af:
                n_vis += 1
            if b_ > blk:
                blk, who = b_, w_
        vis = n_vis >= max(1, int(0.5 * n_ray))     # exposed over at least half the FOV
        in_frame = (a_far <= pitch + 18.0) and (a_near >= pitch - 18.0)
        diag[name] = dict(pitch=round(pitch, 1), a_near=round(a_near, 2),
                          a_far=round(a_far, 2), blk=round(blk, 2),
                          blk_who=who, vis=vis, in_frame=in_frame,
                          open_pct=round(100.0 * n_vis / max(n_ray, 1)),
                          band=round(min(a_far, pitch + 18.0)
                                     - max(a_near, pitch - 18.0), 2))
        if not (vis and in_frame and diag[name]["band"] > 0.5):
            ok = False
    if verbose:
        print("=" * 64)
        print("scene18 [v6] 바다 수평선 시인성 검산 (세로 반화각 18° 가정)")
        print("=" * 64)
        for k, d in diag.items():
            if d.get("skip"):
                print(f"  {k:16s} — 바다 반대편 시선(대상 외)")
                continue
            print(f"  {k:16s} pitch{d['pitch']:+6.1f}°  수면 앙각 "
                  f"{d['a_near']:+6.2f}..{d['a_far']:+6.2f}°  "
                  f"최대차폐 {d['blk']:+6.2f}°  화폭 개방 {d['open_pct']:3d}%  "
                  f"수면띠 {d['band']:5.2f}°  "
                  f"{'OK' if d['vis'] and d['in_frame'] else 'FAIL'}")
        print(f"  → {'OK (요구 3컷 이상에서 수평선 시인)' if ok else 'FAIL'}")
        print("=" * 64)
    return ok, diag


# ===========================================================================
# [D] camera presets - grid_views(gy=0) + 4 mise-en-scene cuts
# ===========================================================================
def build_views():
    """9 grid views (referenced to the top back corner x~0) + 4 mise-en-scene cuts (brief §D features)."""
    v = sc.grid_views(0.0)
    out = {k: dict(eye=list(val["eye"]), tgt=list(val["tgt"]))
           for k, val in v.items()}
    out["wave_raking"]    = dict(eye=[-3.0, 0.0, 0.35], tgt=[5.0, 0.0, -1.3])
    # color_front: the stair head-on from the lower plaza (h1.2 above the lower walkway -2.58, d~6) [A-18(3)]
    out["color_front"]    = dict(eye=[11.7, 0.0, -1.38], tgt=[2.7, 0.0, -1.1])
    # [v6 verdict (a)] oblique_down re-aimed - the old (eye -4,4.5,2.6 -> tgt 3.5,0,-1.5) had a
    #   25.7 deg depression, so the horizon band fell completely above the frame (centre +20 to +25 deg).
    #   The depression is lowered to 14.6 deg and the eye raised 0.4 m so that the **wavy stair (lower left)
    #   and the sea horizon (upper part)** fit in one frame (checked by _sea_selfcheck).
    out["oblique_down"]   = dict(eye=[-4.5, 5.0, 3.0],  tgt=[7.5, 0.0, -0.4])
    out["lower_lookback"] = dict(eye=[8.5, 0.0, -1.9],  tgt=[2.0, 0.0, -1.4])
    # [v6 verdict (a), new] sea_beauty - a 3/4 high-angle view from the hill side (beauty cut).
    #   Beyond the stair descent axis the shoreline and horizon sit from mid-frame to the top.
    out["sea_beauty"]     = dict(eye=[-12.0, -9.0, 5.5], tgt=[26.0, 4.0, -1.5])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. wave_raking    — h0.3 그레이징에서 색 교대가 낙차를 위장하는가
 2. color_front    — 라이저 5색 교대(고채색)가 단코를 흐리는가
 3. oblique_down   — 완만해진 단코가 세그(24) 각짐 없이 흐르는가
                     + 치크월(|y|4.0..4.3)이 물결을 그대로 따라가는가 [v5]
 4. cue_nosing OFF — 색채 위장 정체성(기본 논슬립 없음)
 5. material_break — 상부(밝음)/하부(웜) 보도 재질 경계
 6. [v5] 노출 디딤 0.279~0.401 m — '표준 계단에 색만 칠한' 인상인가
 7. [v6] sea_beauty / oblique_down / wave_raking — **바다 수평선**이 보이는가
        (검산: NEGOBS_SELFCHECK=1 python scene18_wavy_artstair.py)
 8. [v6] 벽화 사선 띠가 '레고 적층'이 아니라 칠한 그림으로 읽히는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    if smoke_mode:
        _wave_selfcheck()          # [v5] pre-boot coordinate check (prim count is verified after it)
        _sea_selfcheck()           # [v6] horizon visibility check

    # Run the coordinate check only and exit (no Isaac boot needed)
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        a, _ = _wave_selfcheck()
        b, _ = _sea_selfcheck()
        print(f"SELFCHECK {'OK' if (a and b) else 'FAIL'}")
        return

    sc.check_assets(
        ["concrete_floor", "plaza_light", "plaza_lower", "grass", "brick_red",
         "hdri", "mdl"],
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
    UsdGeom.Xform.Define(stage, "/World/Scene18")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["tread"] = sc.make_pbr(
            stage, "/World/Looks/Tread", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), scl["concrete_floor"],
            tint=mp["tread_tint"])
        M["upper"] = sc.make_pbr(
            stage, "/World/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["lower"] = sc.make_pbr(
            stage, "/World/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["lower_warm_tint"])
        # [v6] mural palette 7 colours x 3 wear variants = 21 materials (M["riser"][colour][wear])
        M["riser"] = [[sc.make_pbr(
            stage, f"/World/Looks/Riser_{c}_{w}",
            diffuse_color=tuple(min(v * f, 1.0) for v in col),
            roughness_const=0.55, metallic=0.0)
            for w, f in enumerate(mp["mural_wear"])]
            for c, col in enumerate(mp["riser_colors"])]
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
        M["lamp"] = sc.make_pbr(stage, "/World/Looks/Lamp",
                                diffuse_color=mp["lamp_color"],
                                roughness_const=mp["lamp_rough"])
        M["pole"] = sc.make_pbr(stage, "/World/Looks/Pole",
                                diffuse_color=mp["pole_color"],
                                metallic=mp["pole_metallic"],
                                roughness_const=mp["pole_rough"])
        # [W2-D ground_kit] Dedicated dark bindings. Defect D5 (w2_pilot §7):
        #   gate B9 judges a *declared* albedo while the scene binds whatever
        #   material it likes, so a manhole can pass B9 and still render near
        #   white. These three keep the declared and the bound value together.
        #   Salt efflorescence is the one that must stay under the 0.30 cap
        #   even though it is a *bright* stain (§5.1 18 row, explicit).
        M["gk_joint"] = sc.make_pbr(stage, "/World/Looks/GKitJoint",
                                    diffuse_color=(0.12, 0.12, 0.12),
                                    roughness_const=0.75)
        M["gk_iron"] = sc.make_pbr(stage, "/World/Looks/GKitIron",
                                   diffuse_color=(0.09, 0.09, 0.095),
                                   metallic=0.55, roughness_const=0.55)
        M["gk_stain"] = sc.make_pbr(stage, "/World/Looks/GKitStain",
                                    diffuse_color=(0.20, 0.20, 0.19),
                                    roughness_const=0.85)
        M["gk_salt"] = sc.make_pbr(stage, "/World/Looks/GKitSalt",
                                   diffuse_color=(0.29, 0.29, 0.28),
                                   roughness_const=0.90)
        # [v5.1] seaside hill identity - water, roofs, house walls. Instance tint jitter (§4) is given
        #   in 3 variants each for roofs and walls (so the town does not look like one cloned colour).
        sea = PARAMS["seaside"]
        M["sea"] = sc.make_pbr(stage, "/World/Looks/Sea",
                               diffuse_color=sea["water_color"],
                               roughness_const=sea["water_rough"],
                               metallic=0.0)
        M["nvar"] = len(sea["house_var"])
        for i in range(M["nvar"]):
            M[f"roof_{i}"] = sc.make_pbr(
                stage, f"/World/Looks/Roof_{i}",
                diffuse_color=tuple(min(c * f, 1.0) for c, f
                                    in zip(sea["roof_color"],
                                           sea["roof_var"][i])),
                roughness_const=sea["roof_rough"])
            M[f"house_{i}"] = sc.make_pbr(
                stage, f"/World/Looks/House_{i}",
                diffuse_color=tuple(min(c * f, 1.0) for c, f
                                    in zip(sea["house_color"],
                                           sea["house_var"][i])),
                roughness_const=sea["house_rough"])
        return M

    # -------------------------------------------------------------------
    # Ground floor (grass) - full slab (below the drop = the floor). Tiled as 4 boxes.
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
            sc.add_box(stage, f"/World/Scene18/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])

    # -------------------------------------------------------------------
    # Upper/lower walkway (material break) - solid slab.
    # -------------------------------------------------------------------
    def _slab(path, x0, x1, y0, y1, top, mtl):
        """One solid slab, top face at top and underside filled down to the ground (−3.01)."""
        base = PARAMS["ground"]["top_z"]
        # [W2-0 · P-A] The upper walkway slabs are the ground_kit stage; the
        #   registration must precede `add_box`, which evaluates the skin test
        #   inline. Prefix matching in `skin_exclude` covers every wave segment.
        if path.startswith("/World/Scene18/Walk_upper"):
            sc.skin_exclude(path)
        sc.add_box(stage, path,
                   ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (top + base) / 2.0),
                   (x1 - x0, y1 - y0, top - base), mtl, collider=True)

    def build_walkways(M, hazard):
        """Upper and lower walkways. With hazard=True the upper walkway's **east edge is
        segmented to follow the wave** (audit A-18 A1, critical).

        Old structure: the upper slab filled x <= 0.5 solid from z 0..−3.01, so 1-2 steps were
        buried wholesale wherever the front edge lay below x=0.5 (the wave troughs) -> the first level
        difference swung across the width as 0.16 / 0.32 / 0.48 m (2.70 m of the 8 m width had a 0.48 m drop = a jump).
        New structure: inside the stair width (|y|<4) the east edge of seg j is set to
            x1_j = _front_x(-1, yc[j]) = 0.35·sin(k·yc[j] − 0.4)  ∈ [−0.35, +0.35]
        -> it meshes exactly with the stair's topmost back corner, giving **a uniform 0.16 m first level
        difference across the whole width**. The stair (hazard geometry) transform is unchanged; only the walkway is touched.
        Lower: x0 5.2->5.05 (0.04 inside the last step's minimum front edge 5.09) -> removes the A3 slot.
        Skirt: fills the grass ditch at x 0.5..5.05, |y| 4..9 up to the lower level (A5)."""
        s = PARAMS["stair"]
        up, lo = PARAMS["upper"], PARAMS["lower"]
        top_u = up["top_z"] if hazard else 0.0
        top_l = lo["top_z"] if hazard else 0.0
        if hazard and up.get("follow_wave", False):
            yc, Wb = _seg_centers()
            # [v6 verdict (c)] seg minimum-width floor = upper["seg_min_w"] (0.052 -> 0.202)
            x_cut = -s["amp"] - up.get("seg_min_w", 0.05)
            # (1) main body (full width) x0..x_cut
            _slab("/World/Scene18/Walk_upper_W", up["x0"], x_cut,
                  up["y0"], up["y1"], top_u, M["upper"])
            # (2) outside the stair width (|y| 4..9) - keeps the old straight edge x1 (=0.5)
            for tag, y0, y1 in (("S", up["y0"], s["y0"]),
                                ("N", s["y1"], up["y1"])):
                _slab(f"/World/Scene18/Walk_upper_{tag}", x_cut, up["x1"],
                      y0, y1, top_u, M["upper"])
            # (3) inside the stair width - per-seg wave edge (2 mm overlap prevents hairlines)
            for j in range(s["nseg"]):
                x1j = _front_x(-1, yc[j]) + 0.002
                sy0 = s["y0"] + j * Wb - 0.001
                sy1 = s["y0"] + (j + 1) * Wb + 0.001
                _slab(f"/World/Scene18/Walk_upper_Seg_{j}", x_cut, x1j,
                      sy0, sy1, top_u, M["upper"])
        else:
            _slab("/World/Scene18/Walk_upper", up["x0"], up["x1"],
                  up["y0"], up["y1"], top_u, M["upper"])
        # --- lower walkway ---
        _slab("/World/Scene18/Walk_lower", lo["x0"], lo["x1"],
              lo["y0"], lo["y1"], top_l, M["lower"])
        if hazard:
            # 2 ditch-sealing skirts outside the stair width (hazard geometry unchanged)
            sk = PARAMS["skirt"]
            for tag, y0, y1 in (("S", -sk["y_out"], -sk["y_in"]),
                                ("N", sk["y_in"], sk["y_out"])):
                _slab(f"/World/Scene18/Walk_skirt_{tag}", sk["x0"], lo["x0"],
                      y0, y1, top_l, M["lower"])
        else:
            # Control (flat): fills the stair footprint with z=0
            _slab("/World/Scene18/Walk_flat", up["x1"], lo["x0"],
                  lo["y0"], lo["y1"], 0.0, M["lower"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P1 plaza_granite (spec §5.1 scene18 row)
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        up = PARAMS["upper"]
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]),
            z=float(up["top_z"]), gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(g["edge_s"]))],
            dists=(2, 5, 10), scene="scene18", tactile=(),
            overrides=dict(
                infra=dict(manhole=2, gully=2),
                # salt efflorescence replaces the generic "water" stain here.
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
        M2.update(joint=M["gk_joint"], crack=M["gk_joint"], patch=M["upper"],
                  patch_cut=M["gk_joint"], manhole=M["gk_iron"],
                  gully=M["gk_iron"], gutter=M["gk_iron"],
                  gutter_cover=M["gk_iron"], trench=M["gk_iron"],
                  trench_frame=M["gk_iron"], marking=M["gk_stain"],
                  weed=M["grass"], wear=M["gk_stain"], silt=M["gk_stain"],
                  stain_dirt=M["gk_stain"], stain_efflorescence=M["gk_salt"])
        res = gk.apply_ground(kit, "/World/Scene18/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene18 P1 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Wavy stair - step i x seg j boxes + riser colour panels
    # -------------------------------------------------------------------
    def build_stair(M):
        s = PARAMS["stair"]
        rp = PARAMS["riser_panel"]
        base_z = s["base_z"]
        yc, Wb = _seg_centers()
        ncol = len(M["riser"])
        skew = mp["mural_skew"]
        span_y = s["y1"] - s["y0"]
        for i in range(s["n"]):
            z_top = -s["riser"] * (i + 1)
            for j in range(s["nseg"]):
                y = yc[j]
                # [v6] diagonal continuous bands: colour boundaries run across the stair, out of step with the nosings.
                col_mtl = M["riser"][int(math.floor(
                    i + (y - s["y0"]) / span_y * skew)) % ncol][
                        (i * 7 + j * 13) % len(mp["mural_wear"])]
                x_back = _front_x(i - 1, y)
                x_front = _front_x(i, y)
                cxs = (x_back + x_front) / 2.0
                sy0 = s["y0"] + j * Wb - 0.001    # 1 mm overlap
                sy1 = s["y0"] + (j + 1) * Wb + 0.001
                # tread (solid box, top face = tread surface)
                sc.add_box(stage, f"/World/Scene18/Step_{i}_{j}",
                           (cxs, (sy0 + sy1) / 2.0, (z_top + base_z) / 2.0),
                           (x_front - x_back, sy1 - sy0, z_top - base_z),
                           M["tread"], collider=True)
                # Riser colour solid (front face embedded 5 mm - overlaps the stair solid to seal the top).
                #   Front face = x_front+over (proud), back face = x_front-embed (overlap inside the stair).
                #   Height = riser+over, top = z_top-top_gap (1 mm below the tread above).
                r_cx = x_front - rp["thick"] / 2.0 + rp["over"]
                r_h = s["riser"] + rp["over"]
                r_top = z_top - rp["top_gap"]
                sc.add_box(stage, f"/World/Scene18/Riser_{i}_{j}",
                           (r_cx, (sy0 + sy1) / 2.0, r_top - r_h / 2.0),
                           (rp["thick"], sy1 - sy0, r_h), col_mtl)
            # [v5 verdict applied] side cheek wall - 2 kerb bodies (|y| 4.0..4.3) reusing step i's own
            #   front/back x. At y=+-4 the wave phase is
            #   sin(k·(+-4)+i·phi) = sin(+-2pi+i·phi) = sin(i·phi), i.e. **identical on both sides**, so
            #   one pair of x intervals builds left and right alike.
            # [v6 verdict (d)] the body top face is made flush with the tread (curb=0) to remove the stepped
            #   sawtooth. The visible top face is the oblique haunch from build_cheek_haunch below.
            ck = PARAMS["cheek"]
            xb_e = _front_x(i - 1, s["y1"])
            xf_e = _front_x(i, s["y1"])
            c_top = z_top + ck["curb"]
            for tag, cy0, cy1 in (("S", s["y0"] - ck["w"], s["y0"]),
                                  ("N", s["y1"], s["y1"] + ck["w"])):
                sc.add_box(stage, f"/World/Scene18/Cheek_{tag}_{i}",
                           ((xb_e + xf_e) / 2.0, (cy0 + cy1) / 2.0,
                            (c_top + ck["base_z"]) / 2.0),
                           (xf_e - xb_e, cy1 - cy0, c_top - ck["base_z"]),
                           M["upper"], collider=True)

    def build_cheek_haunch(M):
        """[v6 verdict (d)] cheek wall oblique haunch - one top face per side, parallel to the nosing line (scene14 method).

        Top face z(x) = rise − (riser/tread)·x. Always 0.025~0.415 m above the per-step box top
        (−riser·(i+1)), and at least 0.08 m above the haunch underside (top face−thick/cos) ->
        **zero gapping or floating**. The stair width (|y|<4.0) is left untouched."""
        s, ck = PARAMS["stair"], PARAMS["cheek"]
        k = s["riser"] / s["tread"]
        x0h = ck["haunch_x0"]
        z0h = ck["rise"] - k * x0h
        runh = s["n"] * s["tread"] - x0h + ck["haunch_over"]
        for tag, y0, y1 in (("S", s["y0"] - ck["w"], s["y0"]),
                            ("N", s["y1"], s["y1"] + ck["w"])):
            sc.build_slope(stage, f"/World/Scene18/CheekHaunch_{tag}",
                           x0h, z0h, runh, k * runh, y0, y1, ck["thick"],
                           M["upper"], margin=0.0, collider=True)

    # -------------------------------------------------------------------
    # Dressing - benches, streetlights, planters, buildings
    # -------------------------------------------------------------------
    def build_streetlight(M, idx, sl_i):
        sl = PARAMS["streetlight"]
        x, y, bz, ph = sl_i["x"], sl_i["y"], sl_i["base_z"], sl_i["pole_h"]
        base = f"/World/Scene18/Streetlight_{idx}"
        sc.add_cylinder(stage, f"{base}/Pole", (x, y, bz + ph / 2.0),
                        sl["pole_r"], ph, M["pole"], collider=True)
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            ax = x + sgn * sl["arm_len"] / 2.0
            sc.add_cylinder(stage, f"{base}/Arm_{tag}",
                            (ax, y, bz + ph - 0.1),
                            sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
            hx = x + sgn * sl["arm_len"]
            sc.add_box(stage, f"{base}/Head_{tag}", (hx, y, bz + ph - 0.15),
                       (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_seaside(M):
        """[v5.1 realism] the layer that fixes the **seaside hill mural stair** identity.

        Composition (coordinate rationale in the PARAMS["seaside"] comments):
          (1) Sea - a water plate running 500 m from x 31, below the shoreline (ground east end x=34),
             top face −3.35 (0.34 m below the ground top) + a haze-tone, low-saturation material.
             [v6] even from a low eye the horizon now floats **beyond the ground**, not above the roofs.
          (2) Quay promenade - x 29.5..34, width 4.5 m (so the grass never meets the sea directly).
          (3) 13 low-rise town buildings - the stair view axis (|y| < 13) is **cleared** and they move
             into north and south clusters (x 17..32.5, h 3.0~5.6). They fill the sides of the frame and close the distance.
          (4) Hill - 3 fill terraces **above the stair (−X)** (tops 1.4 / 4.6 / 8.2) +
             17 houses on them. They look out over shops D/E (x −24..−15, h 5.0/6.2).
        No element's coordinates overlap the hazard geometry (wavy stair, cheek wall, walkways)
        (nearest town x0 = 17.0 -> 1.0 m from the lower walkway east end x1 = 16.0,
         and y lies outside ±13, so the in-plane clearance is 13 m or more).
        """
        sea = PARAMS["seaside"]
        w = sea["water"]
        sc.add_box(stage, "/World/Scene18/Sea",
                   ((w["x0"] + w["x1"]) / 2.0, (w["y0"] + w["y1"]) / 2.0,
                    w["top_z"] - w["thick"] / 2.0),
                   (w["x1"] - w["x0"], w["y1"] - w["y0"], w["thick"]),
                   M["sea"])
        gz = PARAMS["ground"]["top_z"]
        # [v6] quay promenade - removes the impression of grass meeting the sea directly (width 4.5 m).
        #   Its top face is only 5 mm above the ground (avoids coplanar Z-fighting).
        q = PARAMS["quay"]
        sc.add_box(stage, "/World/Scene18/Quay",
                   ((q["x0"] + q["x1"]) / 2.0, (q["y0"] + q["y1"]) / 2.0,
                    (q["top_z"] + gz - 0.4) / 2.0),
                   (q["x1"] - q["x0"], q["y1"] - q["y0"],
                    q["top_z"] - (gz - 0.4)), M["lower"])
        rf = sea["roof"]
        for i, (x0, x1, y0, y1, h, fl) in enumerate(sea["town"]):
            sc.build_building(
                stage, f"/World/Scene18/Town_{i}",
                dict(x0=x0, x1=x1, y0=y0, y1=y1, h=h, floors=fl,
                     axis="x", facade_x=x0, face_dir=-1.0, base_z=gz),
                M[f"house_{i % M['nvar']}"], M["glass"],
                M[f"roof_{(i * 3) % M['nvar']}"])
            sc.add_box(stage, f"/World/Scene18/TownRoof_{i}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        gz + h + rf["t"] / 2.0),
                       (x1 - x0 + 2 * rf["over"], y1 - y0 + 2 * rf["over"],
                        rf["t"]), M[f"roof_{(i * 3) % M['nvar']}"])
        ty0, ty1 = sea["terrace_y"]
        for i, (x0, x1, top) in enumerate(sea["terraces"]):
            sc.add_box(stage, f"/World/Scene18/HillTerrace_{i}",
                       ((x0 + x1) / 2.0, (ty0 + ty1) / 2.0,
                        (top + gz - 1.0) / 2.0),
                       (x1 - x0, ty1 - ty0, top - (gz - 1.0)), M["grass"])
        for i, (x0, x1, y0, y1, bz, h) in enumerate(sea["houses"]):
            sc.add_box(stage, f"/World/Scene18/Hill_{i}/Body",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, bz + h / 2.0),
                       (x1 - x0, y1 - y0, h),
                       M[f"house_{(i * 2 + 1) % M['nvar']}"])
            sc.add_box(stage, f"/World/Scene18/Hill_{i}/Roof",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        bz + h + rf["t"] / 2.0),
                       (x1 - x0 + 2 * rf["over"], y1 - y0 + 2 * rf["over"],
                        rf["t"]), M[f"roof_{(i + 2) % M['nvar']}"])

    def build_dressing(M):
        """Context dressing - read-out phrase: "a harbour town with a seaside hill mural stair".
        A combination of the existing builders (build_bench/planter/building) + build_seaside."""
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for j, (cx, cy, bz, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"/World/Scene18/Bench_{j}", cx, cy, bz,
                           M["wood"], yaw=yaw)
        for i, sl_i in enumerate(PARAMS["streetlights"]):
            build_streetlight(M, i, sl_i)
        for name, px, py, bz in PARAMS["planters"]:
            sc.build_planter(stage, f"/World/Scene18/Planter_{name}", px, py, bz,
                             M["parapet"], M["grass"], tree_mtls=tree_mtls)
        # [v5.1] the 8 bollards are deleted (no §2 basis - the PARAMS["bollards"] entry is removed)
        build_seaside(M)
        # Edge parapet on the upper walkway |y| 4.2..9 - guards the 2.57 m drop to the skirt (-2.57)
        pa = PARAMS["parapet"]
        for tag, y0, y1 in (("S", -pa["y_out"], -pa["y_in"]),
                            ("N", pa["y_in"], pa["y_out"])):
            sc.add_box(stage, f"/World/Scene18/Parapet_{tag}",
                       ((pa["x0"] + pa["x1"]) / 2.0, (y0 + y1) / 2.0,
                        pa["h"] / 2.0),
                       (pa["x1"] - pa["x0"], y1 - y0, pa["h"]),
                       M["parapet"], collider=True)
        # 2 floor bands on the lower plaza (plaza scale cue - dark constant colour 0.045)
        band = sc.make_pbr(stage, "/World/Looks/Band",
                           diffuse_color=(0.045, 0.045, 0.05),
                           roughness_const=0.8)
        lo = PARAMS["lower"]
        for k, bx in enumerate(PARAMS["bands"]):
            sc.add_box(stage, f"/World/Scene18/Band_{k}",
                       (bx, (lo["y0"] + lo["y1"]) / 2.0, lo["top_z"] - 0.01),
                       (0.45, lo["y1"] - lo["y0"], 0.04), band)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene18/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])

    # -------------------------------------------------------------------
    # Cue toggles (geometry unchanged)
    # -------------------------------------------------------------------
    def build_cues(M):
        s = PARAMS["stair"]
        yc, Wb = _seg_centers()
        # cue_tactile: warning tactile strip on the top approach
        if cfg.get("cue_tactile"):
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, "/World/Scene18/Tactile",
                             -0.6, -0.2, s["y0"], s["y1"], tac, z=0.0)
        # cue_nosing: wavy nosing anti-slip (a constant-colour strip on each seg front edge) - False by default
        if cfg.get("cue_nosing"):
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i in range(s["n"]):
                z_top = -s["riser"] * (i + 1)
                for j in range(s["nseg"]):
                    y = yc[j]
                    xf = _front_x(i, y)
                    sy0 = s["y0"] + j * Wb - 0.001
                    sy1 = s["y0"] + (j + 1) * Wb + 0.001
                    sc.add_box(stage, f"/World/Scene18/Nosing_{i}_{j}",
                               (xf - 0.03, (sy0 + sy1) / 2.0, z_top + 0.004),
                               (0.06, sy1 - sy0, 0.01), nos)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_ground(M)
    build_walkways(M, hazard)
    if hazard:
        build_stair(M)
        build_cheek_haunch(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if hazard:
        build_cues(M)
    build_ground_kit(M)             # [W2-D] ground elements - after the dressing (scatter ordering convention)
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
    _v0 = VIEWS["wave_raking"]
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
