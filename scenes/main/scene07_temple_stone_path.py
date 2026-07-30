# -*- coding: utf-8 -*-
"""
scene07_temple_stone_path.py — NegObs synthetic scene 7 (v5 R2): sparse natural stone stair at a mountain temple

Type    : R2 (v5 redesign) — **discrete natural stepping stones** (large slabs set sparsely)
Spec    : Docs/briefs/multi_scene_brief_v5.md §R2 + Docs/scene_redesign_v5_proposal.md
Shared  : scene_common.py (unmodified) / skeleton convention : scenes/main/scene04_parktrail.py
Inherit : scenes/archive_v3/scene07_wornstone_temple.py (worn_stone·mountain-temple dressing vocabulary)

────────────────────────────────────────────────────────────────────────────
[Hazard]
  The approach path to a Korean mountain temple. Not a standard stair: **large natural stones
  set sparsely** do the job of one. The hazard is not 'exotic terrain' but three layers of
  **reality falling short of code**.

  (1) Broken stepping rhythm — the gaps between stones (0.05~0.30 m) and the rises
     (0.04~0.31 m) are uneven, so the stair prior "the nth nosing = n×riser" does not hold.
     From the robot viewpoint (h0.3) the next tread height cannot be extrapolated.
  (2) A 1.8 m lateral slope drop, **unguarded** — beyond the south shoulder of the corridor
     (y ±1.7) a stone retaining wall falls 1.8 m straight down. There is no railing, kerb or
     tactile paving of any kind (not the practice at mountain temples). Under grazing the leaf
     surface of the lower terrace reads as **one continuous sheet of ground** with the corridor
     face and the border vanishes — the core of this scene's positive GT.
  (3) Partial leaf occlusion — the leaf_ground band bites over the stone edges and erases the
     nosing cut lines (series (2), partial occlusion).

  GT rule: outside the stone path (corridor), the south slope drop = positive. The rises of the
  stones themselves come close to 0.3 m (max 0.31), so the scene doubles as a borderline case of a 'small drop'.

[Walk continuity self-check table]  — entry → descent → exit (coordinates on the y=0 walk line)
  ┌ Section ─────────────┬ Coords (x, z) ───────────┬ Step / basis ───────────┐
  │ Precinct yard (entry)│ x −24..0,  z 0.000       │ flat (granite soil)     │
  │ through the gate     │ x −5.6,    z 0.000       │ posts y ±1.35 (gap 2.7) │
  │ yard edge → stone 1  │ x 0 → 0.24, 0.000→−0.02x │ step = see table [1]    │
  │ descend 24 stones    │ x 0.06..12.05            │ rise min/max = table [2]│
  │ last stone → approach│ x 12.05→12.2, →−4.200    │ step = see table [3]    │
  │ lower approach (exit)│ x 12.2..90, z −4.200     │ flat (leafy dirt path)  │
  └──────────────────────┴──────────────────────────┴─────────────────────────┘
  · Every stone must cover the walk line |y| ≤ 0.22, so the cy jitter is tied to the width
    (|cy| ≤ w/2 − 0.22) → zero "stretches with no stone to step on" (SMOKE checks them all).
  · The actual figures and verdicts are printed by `NEGOBS_SMOKE=1` in tables [1][2][3].

[Geometry core]
  · The stones do not use scene_common.build_worn_stone_stairs (that builder splits each step
    into transverse blocks, a 'continuous stone stair', which cannot give a sparse setting).
    **Individual boxes per stone** are generated scene-locally with a seed-fixed random:
      width w U(0.50,1.10) · depth U(0.28,0.40) · gap U(0.05,0.30) ·
      thickness = proud + U(0.10,0.18) (0.12~0.26) · top-face proud U(0.02,0.08) ·
      yaw rz U(−4,4)° · top-face unevenness rx U(−2.5,2.5)°  → sc._oriented_box
    The ground between the stones is filled by a leaf_ground slope (the corridor slab).
  · Stone top z = P(cx) + proud,  P(x) = −(4.2/12.2)·x  (slope 19.0°)
    → embedded depth = thickness − proud ∈ [0.10, 0.18] m (zero floating, minimum embedment 0.10).
  · Total drop 4.2 m / total run 12.2 m / 24 stones.

[v6 ruling re-fix — judge_v6_rt_new7.md §2 + supervisor decision item 2]
  (1) **Sun re-selection** (supervisor approved). The old `SUN_AZ_OFFSET=0.0` (world az 33.5 = sun
     in the +X·+Y sky) was **fully backlit** on the main camera axis (+X viewing), so the distant
     ridge (−X-facing faces)·south stone wall (−Y-facing faces) had lambert 0 → the upper 40~60 %
     of the frame was pure black.
     → `SUN_AZ_OFFSET=191.5` (world az = 33.5+191.5 = **225**, shadow az 45).
       Per-face direct lambert = dot(N, L) (sun elevation 49.79° → horizontal part 0.6456):
         −X facing (distant ridge·gate front·stone risers) 0.707×0.6456 = **0.456**
         −Y facing (south unguarded stone wall·lower terrace cut face)  = **0.456**
         top face (yard·corridor·stone tops)      sin49.79              = **0.763**
       i.e. the grid (+X)·`side_slope`·`grazing_edge` cuts are all front-lit. Shadows fall to +X·+Y
       (into the frame·north) and do not cover the foreground.
     · (v6 comment error — corrected in v7) "the eave shadow lands at x ≈ 0.69 and only grazes
       1~2 stones" came from projecting **the single eave end line only**. A roof is a surface, so
       the shadow is a **band** over x −3.17…+0.57, and that band covered the near yard.
       → see the [v7] section below. SMOKE now recomputes caster footprints from every AABB corner.
     · Only `gate_frame` (looking back) leaves the gate's +X face on the shaded side — structurally
       unavoidable in the az 180~270 range (clearing the pure-black background outranks it). Instead
       the plinths·2-tier eaves·podium brightness reinforce the silhouette reading.
  (2) **The natural stones rendered as 'brick slabs'** → the cause was twofold.
     (a) the material `stone_worn` = **a masonry joint texture** (regular bricks + mortar joints),
     (b) `make_pbr` uses **world-space projection**, so every stone shared one joint grid
         → joints ran on across the stone borders = a concrete pavement slab.
     → The material was replaced with `rock_face` (jointless natural rock diff/nor) and a
       **per-stone material pool** (8 variants of scale·tint·texture_rotate·texture_translate
       jitter) was built so that the grain·colour·relief of adjacent stones disagree. bump 1.5 strengthens the relief.
     → Silhouette: each stone carries one **canted knob** (a subsidiary lump 1~3 cm lower than the
       main stone with different rz·rx) to break the rectangular outline. Protrusion in x is held
       down by a numeric check.
  (3) **Background horizon closure** — the ridge albedo sat at the sRGB dark floor (0.030), so even
     front-lit it became a black wall. Distant aerial perspective was baked into the albedo, raising
     it to near 0.052 / mid 0.088 / far 0.142 (more blue with distance), the near ridge was split
     into **3 staggered pieces** (y offset·height jitter), and a forest band (build_hedge round
     crowns) was laid on each crest, clearing the straight ridgeline and the black wall at once.
  (4) The leaf band was **an axis-aligned horizontal slab**, so over the 19° corridor its upper end
     was buried and its lower end floated 0.17 m → the identity of the "two black square holes" in
     `gate_frame`. Slope-following (`build_slope`) + 3 rotated overlaps per patch clear the floating
     and the rectangular decal together.

[v7 ruling re-fix — judge_v7_rt_A.md §5 "the shadow moved into the near yard"]
  Diagnosis: v6 chose the bearing looking only at **per-face lambert**. Every face did become
    front-lit, but **the cast shadow** had not vanished; it had simply moved from up there
    (background) to down here (foreground). At az 225 the z=0 projection of the only large caster,
    the Iljumun gate (flying rafter width 5.14 m · eave z 2.81), covers x −3.17…+0.57 · y ≥ −0.89
    → it swallowed the grid's **lower-half ground band** (h0.3_d2 = x −1.44…−0.30, half-width ±0.33)
    whole (lower-half mean 27.5). Rotating the sun cannot shorten the shadow (2.38 m), so three axes are used together.
  (1) **Sun az 225 → 240** (offset 191.5 → 206.5) : the shadow az tips 45 → 60, pushing the shadow
     further toward +Y. A side effect is that **−Y-facing faces (the south unguarded stone wall =
     the grazing judging face) rise in lambert, 0.456 → 0.559**. The cost is −X facing (distant ridge) 0.456 → 0.323.
  (2) **Gate cx −3.0 → −5.6** (stone lanterns·notice board move −2.6 with it) : the shadow's x band
     retreats to −6.26…−2.25, emptying the h0.3_d2 lower-half ground band completely.
  (3) **Gable overhang roof_y 2.35 → 1.90** (flying rafter 2.57 → 2.12) : the shadow's south edge
     moves north from y −0.89 to **−0.06** → the south half of the walk line and the south (right)
     side of the frame are in direct sun. (The flying rafter is wider than the shadow shift, so az alone cannot avoid it entirely.)
  (4) **Distant ridge albedo ×1.42** : offsets the cost of (1) and **preserves render luminance
     (albedo × lambert) at the v7 level** — without this correction the "background pure-black fix"
     reverts. + the mid and far ridges were split into 2 staggered pieces (heights 15.0/18.4 ·
     25.0/29.2), breaking the **horizontal straight crest ("stage backdrop")** of a single box.
  Checks: SMOKE `[v6 sun]` (per-face lambert + albedo×lambert product comparison) ·
        `[v7 shadow]` (z=0 projected footprint per caster) ·
        `[v7 lower-half ground band]` (9 presets × the ground span in the lower half of the frame).
────────────────────────────────────────────────────────────────────────────

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene07_temple_stone_path.py

Auto capture : NEGOBS_CAPTURE=1 python scene07_temple_stone_path.py
Smoke        : NEGOBS_SMOKE=1 python3 scene07_temple_stone_path.py  (no boot)

Coordinates: Z-up, m, travel axis +X descending (convention). Drop start edge = x=0 (yard shoulder).
        The grid axis (y=0) runs precinct → gate → stone descent → lower approach road.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs toggles hazard geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> flatten stepping stones·slope·south drop to z=0
    "cue_railing":        False,   # railings are not the practice on temple stone paths (unguarded) - code path only
    "cue_tactile":        False,   # not the practice (v5 brief §shared) - code path only
    "cue_material_break": True,    # yard decomposed granite vs worn stone contrast
    "cue_sign":           True,    # [v5 shared layer] sign_info (temple notice) at the entrance
    "cue_scene_dressing": True,    # Iljumun gate·stone lanterns·stone wall·pines·Dharma hall silhouette
    "cue_nosing":         False,   # non-slip strips are not the practice on natural-stone nosings - code path only
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
STAIR_RUN = 12.2                   # horizontal length of the stepping-stone run
STAIR_DROP = 4.2                   # total drop over the stepping-stone run (slope 19.0 deg)
SIDE_DROP = 1.8                    # unguarded lateral drop on the south (−Y) side

PARAMS = dict(
    # --- stepping stones (discrete natural stone) generation params : seed-fixed random ---
    stones=dict(n=24, seed=707, x_start=0.06, x_end=12.05,
                w=(0.50, 1.10), depth=(0.28, 0.40), gap=(0.05, 0.30),
                proud=(0.02, 0.08), embed=(0.10, 0.18),
                rz=4.0, rx=2.5, foot_half=0.22),
    # --- [v6] per-stone material pool : breaks the 'continuous joints' of a shared world projection ---
    #     Based on rock_face (jointless natural rock) · scale/tint/rotate/translate jitter.
    stone_mtl=dict(n=8, seed=7071, scale=(0.55, 1.35), bump=1.5,
                   tint_dry=(0.88, 0.86, 0.82), tint_moss=(0.74, 0.84, 0.70),
                   moss_every=3, jitter=0.06),
    # --- [v6] canted knob : breaks the rectangular silhouette (below the main stone top, so GT is unchanged) ---
    #     SMOKE checks x half-width = (dx·cosθ + dy·sinθ)/2 <= stone depth/2 + 0.02.
    #     The 0.050 drop floor keeps a margin over the corner rise (0.043) from the max rx tilt
    #     -> the knob peak never exceeds the main stone top (walk surface GT unchanged).
    knob=dict(seed=7072, fx=0.62, fy=0.50, rz=(10.0, 20.0), rx=(3.0, 9.0),
              drop=(0.050, 0.080), off_y=0.33, thick=0.16),
    # --- corridor (ground between the stones) : leaf_ground slope ---
    corridor=dict(y0=-1.7, y1=1.7, thick=0.60),

    # === [W2-D ground_kit] P12 `courtyard_dg` - spec Sec.5.7 row 07 =========
    #  Natural scene: `natural=True` makes plan_ground raise on any urban infra
    #  (manhole / gully / gutter / marking), so the whole prescription is
    #  tone + scatter. Three bands, exactly as Sec.5.7 asks for:
    #    07-1  3.0 m decomposed-granite walking band  = region y +-1.50, and
    #          `edge_break` on both band lines (the "3-band split" of the
    #          24 x 45.7 m single plate).
    #    07-2  trodden wear axis, width 1.20, albedo x0.85  -> `wear_lane`
    #    07-3  exposed gravel 8/m^2  -> scatter 270 over 33.6 m^2 = 8.04/m^2
    #    07-4  plinth moss band + soil staining -> stain(dirt, water)
    #  region x1 = -0.80 (= EDGE_STANDOFF), NOT the plate edge x=0. Reason:
    #  `apply_ground` runs the profile scatter over the **untrimmed** region,
    #  so only the region itself can keep 6 cm gravel off the shoulder edge.
    #  Surface elements are trimmed to the same -0.80 by `_trim_region`.
    #  Dropped from the profile: `edge_litter`. `_compose_ops` forces its
    #  width to the region span (3.0 m here, 12x the 0.25 m the ledger gives
    #  it) and the two bands then cover y -3.0..3.0, which overlaps the wear
    #  lane at an identical top z -> coplanar decals. Carried as a kit defect.
    gkit=dict(
        region=(-12.0, -1.50, -0.80, 1.50),
        wear_w=1.20,                       # Sec.5.7 "trodden wear axis 1.2"
        band_lines=(-1.50, 1.50),          # the 3.0 m granite-sand band edges
        gravel_n=180,                      # [W2 F2] 270 -> 180; the walked forecourt is
                                           #   gravel, not a rubble yard (8/m^2 was the
                                           #   boulder-era figure)
        seed=7,
    ),
    # --- axis-aligned ground plate table (name, x0, x1, y0, y1, z_top, thick, mtl) ---
    #     v5 regression checklist (3) : no plane covers a cavity - at the south drop y=−1.7
    #     the plates are **split** at that border (no continuous slab bridges it).
    plates=[
        ("Courtyard",     -24.0,   0.0,  -1.7,  44.0,   0.0, 0.50, "gravel"),
        ("CourtyardBody", -24.0,   0.0,  -1.7,  44.0,  -0.5, 2.20, "rock"),
        ("BackField",     -46.0, -24.0,  -1.7,  44.0,   0.0, 2.40, "grass"),
        ("SouthTerraceA", -46.0,   0.0, -34.0,  -1.7,  -1.8, 1.20, "leaf"),
        ("SouthTerraceC",  12.2,  90.0, -34.0,  -1.7,  -6.0, 1.20, "leaf"),
        ("Approach",       12.2,  90.0,  -1.7,   2.15, -4.2, 1.00, "leaf"),
        ("NorthWallFlat",  12.2,  90.0,   2.15,  2.6,  -1.25, 3.20, "rock"),
        ("NorthBankFlat",  12.2,  90.0,   2.6,  44.0,  -2.0, 1.20, "grass"),
        ("ScarpFlatBot",   12.2,  90.0,  -1.80, -1.66, -4.2, 2.00, "rock"),
    ],
    # --- slope plates (build_slope) : (name, z0, drop, y0, y1, thick, mtl) ---
    #     All x0=0, run=STAIR_RUN. margin=0.0 (plate borders match exactly).
    slopes=[
        ("PathCorridor",  0.00, STAIR_DROP, -1.70,  1.70, 0.60, "leaf"),
        ("SouthTerraceB", -1.80, STAIR_DROP, -34.0, -1.70, 1.20, "leaf"),
        ("SouthScarp",    0.00, STAIR_DROP, -1.80, -1.66, 2.00, "rock"),
        ("NorthWall",     0.75, 2.00,        1.70,  2.15, 3.20, "rock"),
        ("NorthBank",     0.00, 2.00,        2.15, 44.00, 1.20, "grass"),
    ],
    # --- leaf-litter band (partial occlusion of stone edges) : thin slabs over the corridor (cx, cy, sx, sy) ---
    #     [v6] axis-aligned horizontal slabs -> **slope-following slabs** (19 deg) + 3 rotated overlaps per patch.
    #     The old way buried the upper end and floated the lower one by 0.17 m (= gate_frame's black square holes).
    leaf_drifts=[(1.30, 0.55, 1.30, 0.95), (3.05, -0.60, 1.10, 1.00),
                 (5.40, 0.35, 1.40, 1.10), (7.20, -0.75, 1.00, 0.85),
                 (9.10, 0.50, 1.25, 1.00), (10.90, -0.40, 1.15, 0.90)],
    # [W2 F3] proud 0.012 -> 0.004. A 12 mm rim all the way round each drift is
    #   the "edge shadow" that made the leaf drifts read as carpets laid on the DG.
    # [W3 F3 / DEC-2] `thick` and the three `sub_*` rectangle-stacking knobs are retired:
    #   the mask is a single zero-thickness N-gon, so there is no rim left to shade and no
    #   stack of rectangles to hide behind. `subs` stays at 1 for the self-check line.
    #   `feather` = the leaf-card band straddling the boundary (inner 0.30 / outer 0.50 m,
    #   spec §10.5 DEC-2); `feather_cap` bounds the instance cost per mask.
    leaf_band=dict(proud=0.004, seed=7073, subs=1,
                   feather=(0.30, 0.50), feather_cap=22),
    # [v6] 3 leaf drifts on the yard (decomposed granite) - eases the 'large high-reflectance beige plane' (ruling (5)).
    #      A yard is flat by practice, so material variation, not curvature, breaks the monotony.
    #      All at y >= −1.55 (never past the south border −1.7 = zero floating).
    yard_drifts=[(-2.6, 2.2, 2.4, 1.8), (-7.6, -0.72, 2.1, 1.6),
                 (-13.2, 1.7, 2.6, 2.0)],
    yard_leaf=dict(seed=7074, subs=2, scale=(0.6, 0.9), off=0.38, rz=30.0),

    # --- Iljumun gate (2 pillars + gable roof) : behind the yard shoulder, 2.7 m opening on the grid axis ---
    #   [v7 ruling §5 (2)] This gate is the **only large caster** of the near-view yard shadow.
    #     Old cx −3.0 · roof_y 2.35 (flying rafter 2.57) · az 225 -> shadow x −3.17…+0.57 ·
    #     y >= −0.89, covering the whole lower-half ground band of h0.3_d2 (x −1.44…−0.30, y +-0.98)
    #     (measured lower-half mean 27.5). Rotating the sun alone cannot shorten the x-direction
    #     shadow length (flying rafter 2.81 m x cot49.79 = 2.38 m), so **the gate retreats 2.6 m
    #     west** and the gable overhang shrinks 1.00 -> 0.55 m, moving the shadow's south edge north to y~0
    #     (the SMOKE [v7 shadow] table compares it against each preset's lower-half ground band).
    gate=dict(cx=-5.6, half_y=1.35, post_r=0.24, post_h=3.05,
              beam_t=0.30, beam_over=0.45,
              roof_half_run=1.55, roof_drop=0.62, roof_t=0.22,
              roof_y=1.90, ridge_z=4.00),
    # --- 2 stone lanterns (in front of the gate) ---
    #   [v6] The old shape (prism + square cap + cylinder) read as a **brick chimney**.
    #   Causes: (1) a masonry texture (stone_worn), (2) no standard granite-lantern members.
    #   -> base stone·lower pedestal·round shaft·upper pedestal·light chamber (4 posts + dark
    #      light windows)·2-tier roof stone·jewel finial instead, in a jointless granite tone.
    #   [v7] Moved −2.6 m with the gate (keeps its 1.3 m relative position in front of it).
    lanterns=[dict(cx=-6.9, cy=2.45), dict(cx=-6.9, cy=-1.15)],
    lantern=dict(plinth_w=0.86, plinth_h=0.14, lower_r=0.30, lower_h=0.20,
                 shaft_r=0.13, shaft_h=0.62, upper_r=0.26, upper_h=0.16,
                 fire_w=0.46, fire_h=0.42, pillar=0.075,
                 cap_w=0.94, cap_h=0.11, cap2_w=0.66, cap2_h=0.09,
                 jewel_r=0.085),
    # --- Dharma hall silhouette (upper) : podium + pillar row + gable roof ---
    #   pillar top (0.9+2.4=3.30) < roof soffit (3.72) over the outermost pillar (+-4.1) - zero interpenetration
    hall=dict(cx=-18.0, cy=3.5, sx=9.0, sy=5.6, base_h=0.9,
              post_r=0.20, post_h=2.4, n_posts=5,
              roof_half_run=5.6, roof_drop=1.6, roof_t=0.30, roof_y=4.2,
              ridge_z=5.20),
    # --- pines (build_tree) : slope·yard·terrace (name, cx, cy, zone, trunk_h) ---
    pines=[("N0", 2.5, 4.6, "north", 3.0), ("N1", 7.4, 6.2, "north", 3.4),
           ("N2", 11.6, 4.2, "north", 2.8), ("N3", -6.0, 6.5, "flat", 3.2),
           ("S0", 4.2, -4.4, "south", 2.6), ("S1", 9.0, -6.0, "south", 3.0),
           ("S2", -8.0, -5.2, "south", 2.8), ("S3", 15.0, -4.0, "south", 3.1)],
    tree=dict(trunk_r=0.11),
    # --- shrub clumps (overlapping flattened ellipsoids - scene04 v5 convention) ---
    # [v6] North shrubs y 3.0~3.6 -> 4.4~5.0 : right behind the stone wall (y 1.70~2.15, 0.75 m
    #      lower at the back), they read from the corridor as 'floating on top of the wall'.
    shrubs=[(1.8, 4.5, "north"), (6.0, 4.9, "north"), (10.4, 4.6, "north"),
            (2.0, -2.9, "south"), (7.6, -3.4, "south"), (12.0, -3.0, "south"),
            (-9.0, 3.0, "flat"), (-14.0, -3.4, "south")],
    shrub=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.78, 0.62, 0.36),
                      (0.55, 0.42, 0.52, 0.44, 0.26),
                      (-0.46, -0.38, 0.58, 0.40, 0.30))),
    # --- temple notice board (sign_info) : at the entrance (before the gate), facing the approach (yaw 180) ---
    #   [v7] Moved −2.6 m with the gate (keeps its 0.65 m relative position behind it).
    sign=dict(cx=-4.95, cy=-1.15, yaw=180.0, w=0.78, h=0.62, pole_h=1.95),

    # --- distant ridgelines (horizon closure, straight ahead on the main camera axis +X) ---
    #   [v6] The old near ridge was a single sy 130 box -> **a straight ridgeline + a black wall**.
    #   The near ridge is split into 3 staggered pieces (x 41.0~46.5 · heights 7.6/10.4/8.6) and each crest
    #   carries a forest band (ridge_crest) to roughen the ridgeline. The y union −74..+79 covers
    #   the grid FOV (+-30 m @ 50 m) with room to spare.
    ridge=[dict(cx=42.5, cy=-46.0, sx=7.0, sy=56.0, h=7.6, z0=-6.0,
                tone="near"),
           dict(cx=46.5, cy=6.0, sx=8.0, sy=52.0, h=10.4, z0=-6.0,
                tone="near"),
           dict(cx=41.0, cy=52.0, sx=6.5, sy=54.0, h=8.6, z0=-6.0,
                tone="near"),
           # [v7 ruling §5 (2)] The mid and far ridges were **single boxes** of sy 170/210, so their crests
           #   were perfectly horizontal = "a stage backdrop with a horizontal seam". Treated the same
           #   way as the near ridge: split into 2 staggered pieces (3~4 m height difference) to break the skyline.
           #   The y union still covers the grid FOV (+-48 m @ 84 m).
           dict(cx=62.0, cy=-52.0, sx=11.0, sy=104.0, h=15.0, z0=-6.0,
                tone="mid"),
           dict(cx=66.0, cy=48.0, sx=10.0, sy=112.0, h=18.4, z0=-6.0,
                tone="mid"),
           dict(cx=84.0, cy=-58.0, sx=14.0, sy=132.0, h=25.0, z0=-6.0,
                tone="far"),
           dict(cx=88.0, cy=56.0, sx=13.0, sy=140.0, h=29.2, z0=-6.0,
                tone="far")],
    # ridge-crest forest bands : (ridge index, height) - build_hedge round crowns treat
    # distant trees as a **silhouette band** rather than individuals (avoids the C-4 lollipop).
    ridge_crest=[(0, 3.4, "near"), (1, 4.2, "near"), (2, 3.8, "near"),
                 (3, 5.0, "far"), (4, 4.2, "far")],
    # individual trees only on the near ridge crest, a few (for edge silhouette variation)
    ridge_trees=[dict(ri=0, cy=-30.0), dict(ri=1, cy=-6.0),
                 dict(ri=1, cy=14.0), dict(ri=2, cy=38.0)],
    # rear (−X) forest line : 3 background hedges + 3 trees. base is the ground in that y band.
    back_hedge=dict(cx=-34.0, sx=1.4, length=20.0, h=2.0),
    back_hedges=[dict(cy=8.5, base=0.0), dict(cy=29.0, base=0.0),
                 dict(cy=-16.0, base=-1.8)],
    back_trees=[dict(cx=-38.0, cy=-12.0, gz=-1.8, trunk_h=3.4),
                dict(cx=-38.0, cy=6.0, gz=0.0, trunk_h=3.8),
                dict(cx=-38.0, cy=24.0, gz=0.0, trunk_h=3.2)],
    # distant forest bands (name, x0, x1, y0, y1, h, base_z) - south terrace / north slope
    far_hedges=[("S0", -40.0, 0.0, -30.0, -27.0, 2.4, -1.80),
                ("S1", 12.2, 80.0, -30.0, -27.0, 2.4, -6.00),
                ("N0", -40.0, 0.0, 40.0, 43.0, 2.6, 0.00),
                ("N1", 12.2, 80.0, 40.0, 43.0, 2.6, -2.00)],

    # --- materials ---
    material=dict(
        # [v6] rock_face = jointless natural rock for the stones / granite = lanterns·plinths
        scale=dict(rock_wall=3.5, rock_face=0.95,
                   granite=3.2, leaf_ground=2.0, gravel=0.35, grass=1.4),
        stone_moss_tint=(0.86, 0.95, 0.82),   # (old stepping-stone moss tone - unused in v6)
        leaf_tint=(0.95, 0.90, 0.82),
        gravel_tint=(0.84, 0.81, 0.76),       # [v6] eases the yard's high-reflectance beige
        granite_tint=(1.0, 1.0, 1.0),
        grass_tint=(0.55, 0.68, 0.42),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        roof_color=(0.045, 0.030, 0.018),     # dark timber and roof tile (sRGB dark-colour rule)
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        shrub=(0.030, 0.047, 0.021), shrub_rough=1.0,
        # [v6] Aerial perspective baked into the distant albedos (old 0.030~0.052 = a black wall even lit).
        #   Brightness and blue rise with distance - the 3 ridge tiers read as separate layers.
        # [v7] With the sun az 225 -> 240, the −X-facing lambert drops 0.456 -> 0.323 (x0.708).
        #   To **preserve render luminance (= albedo x lambert) at the v7 level**, the ridge and
        #   crest albedos are all scaled x1.42 (=0.456/0.323), staying under the pure-white
        #   ceiling of 0.72. Without this correction the "background pure-black fix" reverts
        #   - the SMOKE [v6 sun] block compares the albedo x lambert product against the v6 values.
        ridge_near=(0.074, 0.088, 0.064),
        ridge_mid=(0.125, 0.139, 0.131),
        ridge_far=(0.202, 0.222, 0.250),
        crest_near=(0.060, 0.078, 0.051),     # ridge-crest forest band (near)
        crest_far=(0.102, 0.122, 0.111),
        sign_back=(0.055, 0.050, 0.045),
        rail_color=(0.20, 0.18, 0.16), rail_metallic=0.25, rail_rough=0.75,
    ),

    # --- lighting: scene01's verified noon constants ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # Per-scene sun. World sun az ~ 33.5+offset (the bearing the sun is at); shadows fall at az−180.
    # [v6 ruling §2 (6) + supervisor decision item 2 - re-selection approved]
    #   Old 0.0 (az 33.5) = sun in the +X·+Y sky -> fully backlit on the +X viewing axis.
    #     Distant ridge (−X facing) lambert −0.538 -> 0, south stone wall (−Y facing) −0.553 -> 0 = pure black.
    #   Old 191.5 (az 225) = sun in the −X·−Y sky. Face lambert was saved, but **the gate's
    #     shadow fell straight onto the near yard (the grid's lower-half ground band)** (v7 §5 (2)).
    #   New 206.5 (az 240, shadow az 60) = lays the shadow further toward +Y, clearing the south
    #     half of the walk line. −X facing 0.323 / −Y facing 0.559 / top face 0.763.
    #     · −Y facing (south unguarded stone wall = the grazing judging face) **rises** 0.456 -> 0.559.
    #     · −X facing (distant ridge) falls 0.456 -> 0.323 -> ridge albedo corrected x1.35.
    #     Detailed checks in the SMOKE [v7 shadow]·[v7 sun] tables.
    SUN_AZ_OFFSET=206.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene07")

ASSET_ROLES = ["rock_wall", "rock_face", "granite_dark",
               "leaf_ground", "gravel", "grass", "sign_info", "hdri", "mdl"]


# ===========================================================================
# [D] terrain maths (no boot needed - reused as is by SMOKE)
# ===========================================================================
def path_z(x):
    """Corridor (stone slope) top z. x 0..run → 0..−drop, clamped outside."""
    t = max(0.0, min(x / STAIR_RUN, 1.0))
    return -STAIR_DROP * t


def bank_z(x):
    """North (+Y) cut slope top z (gentle 9.3° — a hillside cut face)."""
    t = max(0.0, min(x / STAIR_RUN, 1.0))
    return -2.0 * t


def ground_z(x, y):
    """Ground z for landing the dressing. Corridor/yard/approach · north slope · south terrace."""
    if y >= 2.15:
        return bank_z(x)
    if y <= -1.7:
        return path_z(x) - SIDE_DROP
    return path_z(x)


def _zone_z(x, y, zone):
    """Pick the landing surface by zone tag: north/south/flat (yard z=0)."""
    if zone == "north":
        return bank_z(x)
    if zone == "south":
        return path_z(x) - SIDE_DROP
    if zone == "flat":
        return 0.0
    return ground_z(x, y)


# ===========================================================================
# [E] discrete natural stepping-stone layout - seed-fixed random (reproducible)
# ===========================================================================
def stone_layout():
    """Return the list of per-stone box specs (computable without booting).

    Each element: dict(i, xa, xb, cx, w, cy, thick, proud, top, rz, rx, gap_next)
      xa/xb = the stone's −X/+X ends, cx = centre, w = Y width, cy = Y centre offset,
      top   = top face z (= path_z(cx) + proud), thick = thickness (embedment included).
    Gaps and depths are geometrically scaled so the raw samples fit x_end−x_start exactly
    (the total run is fixed so the junction coordinates of the lower approach road do not drift).
    """
    sp = PARAMS["stones"]
    rng = random.Random(int(sp["seed"]))
    n = int(sp["n"])
    raw = []
    for _ in range(n):
        raw.append((rng.uniform(*sp["depth"]), rng.uniform(*sp["gap"]),
                    rng.uniform(*sp["w"]), rng.uniform(*sp["proud"]),
                    rng.uniform(*sp["embed"]),
                    rng.uniform(-sp["rz"], sp["rz"]),
                    rng.uniform(-sp["rx"], sp["rx"]),
                    rng.random()))
    span = float(sp["x_end"]) - float(sp["x_start"])
    total = sum(d + g for d, g, *_ in raw)
    k = span / total                    # geometric scaling (gaps and depths together)
    out = []
    x = float(sp["x_start"])
    fh = float(sp["foot_half"])
    for i, (d, g, w, pr, em, rz, rx, u) in enumerate(raw):
        dep = d * k
        gap = g * k
        xa, xb = x, x + dep
        cx = (xa + xb) / 2.0
        cy_max = max(0.0, w / 2.0 - fh)   # must cover the walk line |y|<=fh
        cy = (u * 2.0 - 1.0) * min(cy_max, 0.35)
        out.append(dict(i=i, xa=xa, xb=xb, cx=cx, w=w, cy=cy,
                        proud=pr, thick=pr + em, top=path_z(cx) + pr,
                        rz=rz, rx=rx, gap_next=gap))
        x = xb + gap
    return out


STONES = stone_layout()


def knob_layout():
    """[v6] Per-stone canted knob spec (computed without booting — SMOKE checks containment).

    Each element: dict(i, cx, cy, dx, dy, thick, top, rz, rx, half_x, over_x)
      · top   = main stone top − drop  → **the walk surface (GT) is the main stone top, unchanged**.
      · half_x= X half-width after rotation = (dx·|cos| + dy·|sin|)/2.
      · over_x= half_x − stone depth/2 (positive means X protrusion beyond the stone — held to 0.02 m or less).
      · cy is pushed to one side by off_y·w so the Y silhouette leaves the main stone outline.
    """
    kp = PARAMS["knob"]
    rng = random.Random(int(kp["seed"]))
    out = []
    for s in STONES:
        dep = s["xb"] - s["xa"]
        dx = dep * float(kp["fx"])
        dy = s["w"] * float(kp["fy"])
        rz = rng.uniform(*kp["rz"]) * (1.0 if rng.random() < 0.5 else -1.0)
        rx = rng.uniform(*kp["rx"]) * (1.0 if rng.random() < 0.5 else -1.0)
        drop = rng.uniform(*kp["drop"])
        sgn = 1.0 if rng.random() < 0.5 else -1.0
        a = math.radians(abs(rz))
        half_x = (dx * math.cos(a) + dy * math.sin(a)) / 2.0
        out.append(dict(i=s["i"], cx=s["cx"], cy=s["cy"] + sgn * kp["off_y"]
                        * s["w"], dx=dx, dy=dy, thick=float(kp["thick"]),
                        top=s["top"] - drop, rz=rz, rx=rx,
                        half_x=half_x, over_x=half_x - dep / 2.0))
    return out


KNOBS = knob_layout()


def leaf_patches():
    """Leaf carpets → **DEC-2 masks**. `(name, cx, cy, rx, ry)`, one entry per drift.

    [W3 F3 / DEC-2 `[ruled 07-30]` spec §10.5 · CB-2 pilot criterion §7.2]
      The v6 construction laid `subs=3` overlapping **rectangles** per drift and relied on
      the union of their borders to look irregular. It does not: at h0.3 the union of three
      axis-aligned rectangles reads as three axis-aligned rectangles, which is the whole of
      `tonglam_v2.md` §2.13-2's "photographic carpets laid on the DG" and is the named
      pass condition for this pilot (*"07's leaf carpets ... stop being rectangles"*).
      One `ground_kit.build_carpet_mask` lobe now replaces each 3-rectangle stack:
      **18 prims -> 6**, no straight edge anywhere on the boundary, and the mask follows
      the 19 deg corridor exactly because `build_blot` takes a per-vertex `z_fn`
      (= `path_z`) instead of a slope-slab approximation.
      `sub_scale` / `sub_off` / `sub_rz` are retired with the rectangles; `subs` stays in
      PARAMS at 1 so the self-check line keeps reporting the same quantity.
    """
    out = []
    for n, (cx, cy, sx, sy) in enumerate(PARAMS["leaf_drifts"]):
        rx, ry = sx / 2.0, sy / 2.0
        cxc = min(max(float(cx), 0.04 + rx), STAIR_RUN - 0.05 - rx)
        cyc = min(max(float(cy), -1.66 + ry), 1.66 - ry)
        out.append((f"{n}", cxc, cyc, rx, ry))
    return out


LEAF_PATCHES = leaf_patches()


def stone_metrics():
    """Stepping-stone verification metrics — (rise list, gap list, entry/exit steps)."""
    tops = [s["top"] for s in STONES]
    rises = [tops[i] - tops[i + 1] for i in range(len(tops) - 1)]
    gaps = [s["gap_next"] for s in STONES[:-1]]
    enter = 0.0 - tops[0]                        # yard (z=0) -> top of stone 1
    exit_ = tops[-1] - (-STAIR_DROP)             # last stone -> approach road (−4.2)
    return rises, gaps, enter, exit_


# ===========================================================================
# [E-2] ground_kit plan - pure CPU, no USD. Coordinates come from PARAMS
#       (spec Sec.7.4: the scene, not the spec table, is the source of truth).
# ===========================================================================
def _plate(name):
    """Axis-aligned ground plate row by name: (name,x0,x1,y0,y1,z_top,t,mtl)."""
    for row in PARAMS["plates"]:
        if row[0] == name:
            return row
    raise KeyError(f"scene07: plate '{name}' not in PARAMS['plates']")


def ground_plan():
    """P12 `courtyard_dg` plan for the temple forecourt (x -24..0, z=0).

    The drop edge is the courtyard shoulder = the Courtyard plate's x1, which
    is also where the discrete stepping stones start. Everything the profile
    would emit as urban infrastructure is blocked by `natural=True`.
    """
    g = PARAMS["gkit"]
    cy = _plate("Courtyard")
    return gk.plan_ground(
        "courtyard_dg",
        region=tuple(float(v) for v in g["region"]),
        z=float(cy[5]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("courtyard_shoulder", float(cy[2]))],
        dists=(2, 5, 10), scene="scene07",
        tactile=(),                    # Sec.12.4: natural scene -> not listed
        overrides=dict(
            # water = the plinth moss / damp band of Sec.5.7; dirt = tracked soil
            surface=(("stain", ("dirt", "water")),),
            extras=(("wear_lane", dict(width=float(g["wear_w"]))),
                    ("edge_break", dict(density=10.0,
                                        lines=list(g["band_lines"])))),
            scatter=dict(kind="gravel", cover=0.09,
                         count=int(g["gravel_n"]),
                         scale_jitter=(0.38, 0.62), burial=0.38)),   # [W2 F2]
        seed=int(g["seed"]))


# ===========================================================================
# [F] camera presets: grid_views(gy=0.0) + 5 mise-en-scene cuts
#     Every coordinate comes from path_z() - no hardcoding (guarantees slope alignment).
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)          # h{0.3,0.9,1.8} × d{2,5,10}, +X

    # temple_walk : eye height on the yard, looking ahead - the stones melt into slope and leaves, drop vanishes
    #   [v7] The gate retreated to −5.6 -> the eye pulls back to 3.0 m in front of it, so the gate
    #   frames the path inside the shot (the old −6.0 would sit right under the gate).
    views["temple_walk"] = dict(eye=[-8.6, 0.0, 1.30],
                                tgt=[4.0, 0.0, path_z(4.0) + 0.30])
    # stone_rhythm : close-up of the stones - uneven gaps and rises (broken stepping rhythm)
    views["stone_rhythm"] = dict(eye=[1.0, -1.05, path_z(1.0) + 0.60],
                                 tgt=[5.4, 0.10, path_z(5.4) + 0.05])
    # gate_frame : looking back from mid-descent - frames the gate·lanterns·Dharma hall silhouette
    #   [v7] tgt realigned to the moved gate (cx −5.6). The gate's +X face being shaded is a
    #   structural consequence of sun az 180~270 - awaiting a supervisor decision (mirror the cut).
    views["gate_frame"] = dict(eye=[7.0, 0.0, path_z(7.0) + 1.50],
                               tgt=[PARAMS["gate"]["cx"], 0.0, 1.60])
    # side_slope : section of the unguarded 1.8 m drop, from the lower south terrace
    views["side_slope"] = dict(
        eye=[6.0, -5.2, path_z(6.0) - SIDE_DROP + 1.20],
        tgt=[6.6, -1.5, path_z(6.6) - 0.35])
    # grazing_edge : robot view at the corridor's south shoulder - the lower terrace looks continuous with the corridor
    #   sight pitch (−17.4 deg) < slope angle (19.0 deg) -> the lower terrace compresses toward the horizon
    views["grazing_edge"] = dict(eye=[2.0, 1.10, path_z(2.0) + 0.30],
                                 tgt=[12.0, -1.50, path_z(12.0) + 0.60])
    return views


# ===========================================================================
# [G] SMOKE - geometry self-verification without booting
# ===========================================================================
def lantern_height():
    """Total lantern height (base stone underside → top of the jewel finial)."""
    ln = PARAMS["lantern"]
    return (ln["plinth_h"] + ln["lower_h"] + ln["shaft_h"] + ln["upper_h"]
            + ln["fire_h"] + ln["cap_h"] + ln["cap2_h"] + 2 * ln["jewel_r"])


def _grid_obstacles():
    """AABB list for the grid camera (−d, 0, h) collision check [(name,x0,x1,y0,y1,z0,z1)]."""
    g = PARAMS["gate"]
    hl = PARAMS["hall"]
    sg = PARAMS["sign"]
    ln = PARAMS["lantern"]
    obs = []
    for tag, sgn in (("P", 1.0), ("N", -1.0)):
        cy = sgn * g["half_y"]
        pr = g["post_r"] * 1.55            # [v6] includes the plinth radius
        obs.append((f"GatePost_{tag}", g["cx"] - pr, g["cx"] + pr,
                    cy - pr, cy + pr, 0.0, g["post_h"]))
    # [v6] Includes the flying rafter (2nd-tier eave) - the lowest eave z is ridge−0.45−drop'−0.11
    obs.append(("GateRoof", g["cx"] - g["roof_half_run"] - 0.35,
                g["cx"] + g["roof_half_run"] + 0.35,
                -(g["roof_y"] + 0.22), g["roof_y"] + 0.22,
                g["ridge_z"] - 0.45 - g["roof_drop"] * 1.20 - 0.11,
                g["ridge_z"]))
    obs.append(("Hall", hl["cx"] - hl["sx"] / 2.0, hl["cx"] + hl["sx"] / 2.0,
                hl["cy"] - hl["roof_y"], hl["cy"] + hl["roof_y"],
                0.0, hl["ridge_z"]))
    obs.append(("SignPost", sg["cx"] - 0.06, sg["cx"] + 0.06,
                sg["cy"] - sg["w"] / 2.0, sg["cy"] + sg["w"] / 2.0,
                0.0, sg["pole_h"]))
    for i, p in enumerate(PARAMS["lanterns"]):
        r = ln["cap_w"] / 2.0
        obs.append((f"Lantern_{i}", p["cx"] - r, p["cx"] + r,
                    p["cy"] - r, p["cy"] + r, 0.0, lantern_height()))
    for name, cx, cy, zone, th in PARAMS["pines"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Pine_{name}", cx - 0.9, cx + 0.9, cy - 0.9, cy + 0.9,
                    gz, gz + th + 1.4))
    return obs


def _smoke_report():
    P = PARAMS
    print("=" * 72)
    print("scene07_temple_stone_path (v5 R2) — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 72)
    slope_deg = math.degrees(math.atan2(STAIR_DROP, STAIR_RUN))
    print(f"  사면: run {STAIR_RUN:.2f} m / drop {STAIR_DROP:.2f} m "
          f"= {slope_deg:.1f}°  · 배석 {len(STONES)}석 (seed "
          f"{P['stones']['seed']})")
    print(f"  낙차 검증: 주낙차 {STAIR_DROP:.2f} ≥ 0.3 → "
          f"{'OK' if STAIR_DROP >= 0.3 else 'FAIL'} · "
          f"측방 {SIDE_DROP:.2f} ≥ 0.3 → "
          f"{'OK' if SIDE_DROP >= 0.3 else 'FAIL'}")

    # ── tables [1][2][3] stepping stones ──
    rises, gaps, enter, exit_ = stone_metrics()
    print("\n  [표] 자연석 이산 배석 (i, xa..xb, 폭 w, cy, 두께, 상면 z, "
          "답차→다음, 간격)")
    print(f"    {'i':>2} {'xa':>6} {'xb':>6} {'w':>5} {'cy':>6} {'thk':>5} "
          f"{'top z':>7} {'답차':>6} {'간격':>6} {'매입':>5} 워크라인")
    ok_walk = True
    for s in STONES:
        i = s["i"]
        rise = rises[i] if i < len(rises) else float("nan")
        y0, y1 = s["cy"] - s["w"] / 2.0, s["cy"] + s["w"] / 2.0
        fh = P["stones"]["foot_half"]
        covers = (y0 <= -fh + 1e-9) and (y1 >= fh - 1e-9)
        ok_walk = ok_walk and covers
        print(f"    {i:2d} {s['xa']:6.2f} {s['xb']:6.2f} {s['w']:5.2f} "
              f"{s['cy']:+6.2f} {s['thick']:5.2f} {s['top']:7.3f} "
              f"{rise:6.3f} {s['gap_next']:6.3f} "
              f"{s['thick'] - s['proud']:5.2f} {'OK' if covers else 'MISS'}")
    print(f"    [1] 진입 단차(마당 z0 → 1석 상면) = {enter:+.3f} m")
    print(f"    [2] 답차 min {min(rises):.3f} / max {max(rises):.3f} / "
          f"평균 {sum(rises)/len(rises):.3f} m  "
          f"(리듬 파괴 폭 {max(rises)-min(rises):.3f})")
    print(f"        간격 min {min(gaps):.3f} / max {max(gaps):.3f} m "
          f"(목표대 0.05~0.35 → "
          f"{'OK' if min(gaps) >= 0.045 and max(gaps) <= 0.355 else 'CHECK'})")
    print(f"    [3] 탈출 단차(마지막 석 → 진입로 z{-STAIR_DROP:.1f}) "
          f"= {exit_:+.3f} m")
    print(f"    보행 연속성: 전 배석이 워크라인 |y| ≤ "
          f"{P['stones']['foot_half']} 를 덮는가 → "
          f"{'OK' if ok_walk else 'FAIL'}")
    max_step = max(abs(enter), abs(exit_), max(abs(r) for r in rises))
    print(f"    최대 단일 답차 {max_step:.3f} m "
          f"({'보행 가능(<0.35)' if max_step < 0.35 else '과대 — 재조정 필요'})")
    emin = min(s["thick"] - s["proud"] for s in STONES)
    print(f"    최소 매입 깊이 {emin:.3f} m (>0 = 부유 없음 → "
          f"{'OK' if emin > 0.0 else 'FAIL'})")

    # ── [v6] canted knob : checks GT invariance + X protrusion limit ──
    over = max(k["over_x"] for k in KNOBS)
    # knob peak = top + (dy/2)·sin|rx| (rotX lifts the Y edge)
    ktop = [k["top"] + (k["dy"] / 2.0) * math.sin(math.radians(abs(k["rx"])))
            for k in KNOBS]
    marg = min(s["top"] - t for s, t in zip(STONES, ktop))
    kemb = max(k["top"] - k["thick"] - path_z(k["cx"]) for k in KNOBS)
    print(f"\n  [v6 노브] {len(KNOBS)}개 · 노브 최고점이 주석 상면보다 낮은 "
          f"여유 min {marg:+.4f} m (>0 = 보행면 GT 불변 → "
          f"{'OK' if marg > 0.0 else 'FAIL'})")
    print(f"    X 최대 돌출 {over:+.4f} m (≤0.02 → "
          f"{'OK' if over <= 0.02 else 'CHECK'}) · 노브 하면−회랑면 최대 "
          f"{kemb:+.3f} m (<0 = 전량 매입 → "
          f"{'OK' if kemb < 0.0 else 'CHECK'})")

    # ── [W3 F3] leaf carpets : DEC-2 masks — slope alignment + corridor containment ──
    #    The mask is a `build_blot` N-gon normalised to max radius 1, so the lobe
    #    **inscribes** (cx±rx, cy±ry) and the containment test is exact on the bbox.
    lb = P["leaf_band"]
    ferr, dk = 0.0, gk.dry_kit()
    for nm, cx, cy, rx, ry in LEAF_PATCHES:
        b = gk.build_blot(dk, f"/dry/LeafMask_{nm}", cx, cy, rx, ry, None,
                          n=24, rough=0.18, seed=int(lb["seed"]) + int(nm),
                          z=0.0, proud=lb["proud"], z_fn=lambda x, y: path_z(x))
        for (px, _py), pz in zip(b["points"], b["zs"]):
            ferr = max(ferr, abs(pz - (path_z(px) + lb["proud"])))
    yout = max(abs(cy) + ry for _n, _cx, cy, _rx, ry in LEAF_PATCHES)
    xout = max(cx + rx for _n, cx, _cy, rx, _ry in LEAF_PATCHES)
    xin = min(cx - rx for _n, cx, _cy, rx, _ry in LEAF_PATCHES)
    print(f"\n  [W3 낙엽] 마스크 {len(LEAF_PATCHES)}매(드리프트 "
          f"{len(P['leaf_drifts'])}×{lb['subs']}, 직사각 0매) · "
          f"정점 z = path_z(x)+{lb['proud']:.3f} 사면 정합 오차 "
          f"{ferr:.4f} m ({'OK' if ferr < 1e-6 else 'FAIL'})")
    print(f"    최대 |y| {yout:.3f} (<1.70 = 남측 공동 위 부유 없음 → "
          f"{'OK' if yout < 1.70 else 'FAIL'}) · x 범위 {xin:.2f}..{xout:.2f} "
          f"(≤{STAIR_RUN:.2f} → "
          f"{'OK' if xout <= STAIR_RUN + 1e-9 and xin >= 0.0 else 'CHECK'})")

    # ── [v6] sun bearing -> per-face direct-light lambert check ──
    az = 33.5 + float(P["SUN_AZ_OFFSET"])
    el = math.radians(float(P["light"]["noon_sun_elev"]))
    lx = math.cos(math.radians(az)) * math.cos(el)
    ly = math.sin(math.radians(az)) * math.cos(el)
    lz = math.sin(el)
    print(f"\n  [v6 태양] offset {P['SUN_AZ_OFFSET']:.1f} → 월드 az {az:.1f}° "
          f"(그림자 az {az - 180:.1f}°) · 고도 {math.degrees(el):.2f}°")
    for nm, N in (("−X향(원경 능선·문 정면)", (-1, 0, 0)),
                  ("−Y향(남측 무방호 석축)", (0, -1, 0)),
                  ("상면(마당·회랑·배석)", (0, 0, 1)),
                  ("+X향(gate_frame 문 배면)", (1, 0, 0))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<24} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    lam_x = -lx                                   # −X-facing lambert (distant ridge)
    for nm, key, old_a, old_l in (("근경 능선", "ridge_near", 0.052, 0.456),
                                  ("중경 능선", "ridge_mid", 0.088, 0.456),
                                  ("원경 능선", "ridge_far", 0.142, 0.456),
                                  ("마루 숲(근)", "crest_near", 0.042, 0.456)):
        a_new = P["material"][key][0]
        print(f"    {nm:<12} 알베도 {old_a:.3f}→{a_new:.3f} · 휘도곱 "
              f"{old_a*old_l:.4f} → {a_new*lam_x:.4f} "
              f"({'보존 OK' if a_new*lam_x >= old_a*old_l else 'CHECK(어두워짐)'}"
              f") · 순백 상한 0.72 "
              f"{'OK' if a_new <= 0.72 else 'FAIL'}")

    # ── [v7] cast shadow footprint x grid lower-half ground band ──
    #   Lesson (end of judge_v7): "shadows do not vanish, they move". A per-face lambert table
    #   does not tell you **where the cast shadow goes** - the cell W2 missed was the
    #   'grid near-view ground'. Here the two tables are compared on one screen.
    #   · shadow projection : P -> P − L·(P.z/L.z),  horizontal shift = −(cos az, sin az)·z·cot(el)
    #   · lower-half ground band : vertical half-FOV 18.0 deg (focal 18.147 / vertical aperture 11.787),
    #     pitch −10 deg -> the x span where the frame-bottom −28 deg · centre −10 deg rays meet the yard (z=0)
    cot = math.cos(el) / math.sin(el)
    sdx = -math.cos(math.radians(az)) * cot
    sdy = -math.sin(math.radians(az)) * cot
    g = P["gate"]
    ln_h = lantern_height()
    casters = [
        ("일주문 주지붕", g["cx"] - g["roof_half_run"],
         g["cx"] + g["roof_half_run"], -g["roof_y"], g["roof_y"],
         g["ridge_z"] - g["roof_drop"], g["ridge_z"]),
        ("일주문 부연", g["cx"] - g["roof_half_run"] - 0.30,
         g["cx"] + g["roof_half_run"] + 0.30, -(g["roof_y"] + 0.22),
         g["roof_y"] + 0.22,
         g["ridge_z"] - 0.45 - g["roof_drop"] * (g["roof_half_run"] + 0.30)
         / g["roof_half_run"], g["ridge_z"] - 0.45),
        ("일주문 기둥", g["cx"] - 0.24, g["cx"] + 0.24, -g["half_y"] - 0.24,
         g["half_y"] + 0.24, 0.0, g["post_h"]),
        ("석등(남)", P["lanterns"][1]["cx"] - 0.47,
         P["lanterns"][1]["cx"] + 0.47, P["lanterns"][1]["cy"] - 0.47,
         P["lanterns"][1]["cy"] + 0.47, 0.0, ln_h),
        ("안내판", P["sign"]["cx"] - 0.06, P["sign"]["cx"] + 0.06,
         P["sign"]["cy"] - P["sign"]["w"] / 2.0,
         P["sign"]["cy"] + P["sign"]["w"] / 2.0, 0.0, P["sign"]["pole_h"]),
        ("법당", P["hall"]["cx"] - P["hall"]["sx"] / 2.0,
         P["hall"]["cx"] + P["hall"]["sx"] / 2.0,
         P["hall"]["cy"] - P["hall"]["roof_y"],
         P["hall"]["cy"] + P["hall"]["roof_y"], 0.0, P["hall"]["ridge_z"]),
    ]
    print("\n  [v7 그림자] 캐스터 → 마당(z=0) 투영 발자국 · 워크라인 |y|≤0.22")
    shade = []                       # (name, x0, x1, y_south) - shadow on the yard
    for nm, x0, x1, y0, y1, zlo, zhi in casters:
        xs = [x + sdx * z for x in (x0, x1) for z in (zlo, zhi)]
        ys = [y + sdy * z for y in (y0, y1) for z in (zlo, zhi)]
        sx0, sx1, sy0, sy1 = min(xs), max(xs), min(ys), max(ys)
        cross = (sy0 <= 0.22 and sy1 >= -0.22)
        shade.append((nm, sx0, sx1, sy0))
        print(f"    {nm:<12} x[{sx0:+6.2f},{sx1:+6.2f}] y[{sy0:+6.2f},"
              f"{sy1:+6.2f}]  워크라인 {'가로지름' if cross else '비껴감'}")
    big = [s for s in shade if (s[2] - s[1]) * 1.0 >= 2.0]     # large casters only
    print("  [v7 하반 지면대] 프리셋별 프레임 아래절반이 찍는 마당 구간 "
          "(x_하단…x_중앙) vs 대형 그림자")
    for h in (0.3, 0.9, 1.8):
        for d in (2, 5, 10):
            xe = -float(d)
            xn = xe + h / math.tan(math.radians(28.0))
            xm = xe + h / math.tan(math.radians(10.0))
            half_w = (xn - xe) * math.tan(math.radians(30.0))   # near-end half-width
            ov = []
            for nm, sx0, sx1, sy0 in big:
                if sx1 > xn and sx0 < xm and sy0 < half_w:
                    ov.append(nm if sy0 <= -half_w else f"{nm}(북측만)")
            state = "직사광" if not ov else ("부분(" + ",".join(ov) + ")")
            print(f"    h{h}_d{d:<3} 지면대 x[{xn:+6.2f},{xm:+6.2f}] "
                  f"반폭 ±{half_w:.2f} → {state}")
    print("    ※ x_중앙 > 0 인 프리셋은 하반이 배석·회랑(사면)이라 마당 투영이"
          " 아니라 SMOKE 사면 표로 판정한다.")

    # ── ground plate table + south drop verification ──
    print("\n  [표] 축정렬 지면 플레이트 (상면 z / 두께)")
    print(f"    {'이름':16s} {'x범위':>16s} {'y범위':>16s} {'상면z':>7s} 두께")
    for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]:
        print(f"    {nm:16s} [{x0:7.1f},{x1:7.1f}] [{y0:7.2f},{y1:7.2f}] "
              f"{zt:7.2f} {th:5.2f}")
    print("  [표] 사면 플레이트 (x0=0, run=%.2f)" % STAIR_RUN)
    for nm, z0, drop, y0, y1, th, _m in P["slopes"]:
        print(f"    {nm:16s} z0 {z0:+6.2f} → {z0 - drop:+6.2f}  "
              f"y[{y0:7.2f},{y1:7.2f}] 두께 {th:.2f}")
    for x in (0.0, 3.0, 6.0, 9.0, 12.2):
        print(f"    x={x:5.1f}: 회랑 {path_z(x):+6.3f} / 남측테라스 "
              f"{path_z(x) - SIDE_DROP:+6.3f} (낙차 {SIDE_DROP:.2f}) / "
              f"북측사면 {bank_z(x):+6.3f} / 담 상단 {bank_z(x) + 0.75:+6.3f}")
    print("    남측 낙차는 y=−1.7 에서 플레이트가 갈라짐 → 공동 위 연속 평면 "
          "없음 (체크리스트 ③ OK)")

    # ── grid camera vs geometry collision check ──
    print("\n  [검산] 그리드 카메라(−d, 0, h) vs 기하 AABB")
    obs = _grid_obstacles()
    hit_any = False
    for d in (2, 5, 10):
        for h in (0.3, 0.9, 1.8):
            ex, ey, ez = -float(d), 0.0, float(h)
            hits = [nm for nm, x0, x1, y0, y1, z0, z1 in obs
                    if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1]
            if hits:
                hit_any = True
                print(f"    d{d} h{h}: ⚠ {hits}")
    print(f"    충돌 = {hit_any} (False 여야 함)  · 카메라 접지면 z=0 "
          "(Courtyard x −24..0, y −1.7..44) 내부 OK")

    # ── mise-en-scene camera coordinates ──
    print("\n  [카메라] 미장센")
    v = build_views()
    for vn in ("temple_walk", "stone_rhythm", "gate_frame", "side_slope",
               "grazing_edge"):
        vv = v[vn]
        print(f"    {vn:<14} eye={['%.2f' % e for e in vv['eye']]} "
              f"tgt={['%.2f' % t for t in vv['tgt']]}")
    print("=" * 72)


# ===========================================================================
# [H] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 배석 너머 사면이 평지로 접히고 남측 낙차가 소실되나
 2. stone_rhythm     — 돌 간 간격·답차 불균일(디딤 리듬 파괴)이 읽히나
 3. grazing_edge     — 회랑면과 하부 테라스가 한 장 지면으로 이어져 보이나
 4. side_slope       — 무방호 1.8 m 석축 낙차 단면이 명확한가
 5. gate_frame       — 일주문·석등·석축담·법당이 '산사'로 판독되나
 6. 낙엽 밴드        — 돌 에지를 물고 덮어 단코 절단선을 지우나
 7. 접지             — 배석 매입(≥0.10)·석등·기둥에 부유·틈이 없나
 8. 지평 폐쇄        — 근경 능선 3분절 + 마루 숲 밴드가 검은 벽 없이 닫히나
10. [v6] 배석 재질   — 인접 돌의 결·색이 어긋나 '연속 줄눈 판석'이 사라졌나
11. [v6] 낙엽 밴드   — 사면에 밀착(하류단 부유·검은 사각 구멍 소멸)했나
12. [v6] 석등        — 굴뚝이 아니라 화사석·옥개석 갖춘 석등으로 읽히나
 9. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가"""


def main():
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if smoke:
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

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
    UsdGeom.Xform.Define(stage, "/World/Scene07")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene07"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl, rotY=rotY,
                               collider=col)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        def tex_xform(mtl, translate=None, rotate=None):
            """[v6] World-projection UV offset·rotation. Under the `scene_common` no-edit rule,
            inputs are added scene-locally to the OmniPBR shader that make_pbr created
            (texture_translate/texture_rotate of OmniPBR.mdl — effective when project_uvw=True).
            The grain of adjacent stones disagrees and the 'continuous joints' disappear."""
            from pxr import UsdShade, Sdf, Gf
            sh = UsdShade.Shader(
                stage.GetPrimAtPath(mtl.GetPath().AppendChild("Shader")))
            if translate is not None:
                sh.CreateInput("texture_translate",
                               Sdf.ValueTypeNames.Float2).Set(
                    Gf.Vec2f(float(translate[0]), float(translate[1])))
            if rotate is not None:
                sh.CreateInput("texture_rotate",
                               Sdf.ValueTypeNames.Float).Set(float(rotate))
            return mtl

        M = {}
        # [v6] The old M["stone"] (stone_worn = masonry joints) is **dropped** - the stones now
        #      draw from the rock_face pool below (the cause behind ruling §2 (5) 'brick-jointed slabs').
        # [v6] lanterns·plinths = jointless granite tone (old stone_cap = masonry texture -> chimney)
        M["stone_cap"] = tex("granite_dark", "/World/Looks/StoneCap",
                             sca["granite"], tint=mp["granite_tint"])
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"])
        M["leaf"] = tex("leaf_ground", "/World/Looks/Leaf",
                        sca["leaf_ground"], tint=mp["leaf_tint"])
        M["gravel"] = tex("gravel", "/World/Looks/Gravel", sca["gravel"],
                          tint=mp["gravel_tint"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["roof"] = sc.make_pbr(stage, "/World/Looks/Roof",
                                diffuse_color=mp["roof_color"],
                                roughness_const=0.9, specular_level=0.0)
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["shrub"] = sc.make_pbr(stage, "/World/Looks/Shrub",
                                 diffuse_color=mp["shrub"],
                                 roughness_const=mp["shrub_rough"],
                                 specular_level=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        # [W2-D ground_kit] tone-only materials for the kit's ground elements.
        #   Sec.4.4 hands colour to T1, but a wear lane and a moss band *are*
        #   tone by definition - bound to the plain courtyard gravel they would
        #   render a zero-contrast null (the scene15 pilot measured exactly
        #   that for patches). Both are tints of the gravel texture already in
        #   use, so no new asset and no new texture role is introduced.
        M["gk_wear"] = tex("gravel", "/World/Looks/GkWear", sca["gravel"],
                           tint=tuple(c * 0.85 for c in mp["gravel_tint"]))
        # [W2 fix batch F2] Scatter pool override. Bound over each scattered rock
        #   with `strongerThanDescendants`, so the procured asset's own basecolor
        #   (linear 0.23) is replaced by a real gravel texture dulled to 0.19 -
        #   the middle of the "grey debris 0.18~0.30" convention.
        M["gk_rock"] = tex("gravel", "/World/Looks/GkRock", 0.30,
                           tint=(0.82, 0.81, 0.79))
        M["gk_moss"] = tex("gravel", "/World/Looks/GkMoss", sca["gravel"],
                           tint=PARAMS["stone_mtl"]["tint_moss"])
        for tone in ("near", "mid", "far"):
            M[f"ridge_{tone}"] = sc.make_pbr(
                stage, f"/World/Looks/Ridge_{tone}",
                diffuse_color=mp[f"ridge_{tone}"], roughness_const=0.95,
                specular_level=0.0)
        for tone in ("near", "far"):
            M[f"crest_{tone}"] = sc.make_pbr(
                stage, f"/World/Looks/Crest_{tone}",
                diffuse_color=mp[f"crest_{tone}"], roughness_const=1.0,
                specular_level=0.0)
        # [v6] stepping-stone material pool - rock_face (jointless) x scale/tint/rotate/translate jitter
        smp = PARAMS["stone_mtl"]
        rng = random.Random(int(smp["seed"]))
        jt = float(smp["jitter"])
        M["stone_pool"] = []
        for k in range(int(smp["n"])):
            base = (smp["tint_moss"] if (k % int(smp["moss_every"]) == 0)
                    else smp["tint_dry"])
            tint = tuple(max(0.0, c * (1.0 + rng.uniform(-jt, jt)))
                         for c in base)
            m = tex("rock_face", f"/World/Looks/StoneNat_{k}",
                    rng.uniform(*smp["scale"]), tint=tint,
                    bump=float(smp["bump"]))
            tex_xform(m, translate=(rng.uniform(-4.0, 4.0),
                                    rng.uniform(-4.0, 4.0)),
                      rotate=rng.uniform(0.0, 360.0))
            M["stone_pool"].append(m)
        # [v5 shared layer] Korean sign panel - uv_mode=True (mesh st matched 1:1)
        M["sign_info"] = sc.make_pbr(
            stage, "/World/Looks/SignInfo",
            sc.tex_path("sign_info", "diff"), None, None, 1.0,
            roughness_const=0.55, uv_mode=True)
        M["sign_back"] = sc.make_pbr(stage, "/World/Looks/SignBack",
                                     diffuse_color=mp["sign_back"],
                                     roughness_const=0.7)
        # yard material toggle (cue_material_break=False -> the stones take the decomposed-granite tone too)
        #   [v6] The stones draw from the material pool. With the toggle OFF they all share one decomposed-granite material.
        if not cfg["cue_material_break"]:
            M["stone_pool"] = [M["gravel"]]
        return M

    # -------------------------------------------------------------------
    # terrain : axis-aligned plate table + slope plate table
    # -------------------------------------------------------------------
    def build_terrain(M):
        # [W2-0 P-A] The courtyard plate is what ground_kit decorates, so its
        #   displacement skin must be off *before* the box is created - the
        #   skin top sits at +6.5..16.5 mm and would bury every 0.6 mm decal
        #   (spec Sec.1.1). Registration is prefix-matched.
        sc.skin_exclude(f"{ROOT}/Plate_Courtyard")
        for nm, x0, x1, y0, y1, zt, th, mk in PARAMS["plates"]:
            BOX(f"{ROOT}/Plate_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M[mk], col=True)
        for nm, z0, drop, y0, y1, th, mk in PARAMS["slopes"]:
            sc.build_slope(stage, f"{ROOT}/Slope_{nm}", 0.0, z0, STAIR_RUN,
                           drop, y0, y1, th, M[mk], margin=0.0, collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False control : stones·slope·south drop flattened to z=0."""
        BOX(f"{ROOT}/FlatFill", (22.0, 5.0, -0.5), (136.0, 78.0, 1.0),
            M["gravel"], col=True)

    # -------------------------------------------------------------------
    # discrete natural stepping stones (scene-local - build_worn_stone_stairs unused)
    # -------------------------------------------------------------------
    def build_stones(M):
        pool = M["stone_pool"]
        for s in STONES:
            cz = s["top"] - s["thick"] / 2.0
            # per-stone material (a pool whose world-projected UVs are offset) - breaks joint continuity between neighbours
            sc._oriented_box(stage, f"{ROOT}/Stone_{s['i']}",
                             (s["cx"], s["cy"], cz),
                             (s["xb"] - s["xa"], s["w"], s["thick"]),
                             pool[s["i"] % len(pool)], collider=True,
                             rotz=s["rz"], rotx=s["rx"])
        # canted knob : a subsidiary lump lower than the main stone (breaks the rectangular silhouette, GT unchanged)
        for k in KNOBS:
            sc._oriented_box(stage, f"{ROOT}/StoneKnob_{k['i']}",
                             (k["cx"], k["cy"], k["top"] - k["thick"] / 2.0),
                             (k["dx"], k["dy"], k["thick"]),
                             pool[(k["i"] + 3) % len(pool)], collider=False,
                             rotz=k["rz"], rotx=k["rx"])
        # [W3 F3 / DEC-2] leaf carpets - one irregular mask per drift, no rectangles.
        #   The corridor masks take `z_fn=path_z`, so every vertex sits on the 19 deg
        #   corridor plane and the "floating / buried end" the v6 slope slabs were built to
        #   cure cannot come back. The yard masks are flat (the yard is flat by practice -
        #   material variation, not curvature, breaks its monotony).
        lb = PARAMS["leaf_band"]
        yl = PARAMS["yard_leaf"]
        kit = gk.kit_from_scene_common(sc, stage)
        # Feather-ring clip boxes. A leaf card that lands off its host plate sits at the
        #   mask's own z over different ground and floats: the corridor cards must stay
        #   inside the PathCorridor slope (|y| <= 1.70, x 0..STAIR_RUN) and the yard cards
        #   inside the Courtyard plate (x −24..0, y >= −1.70).
        clip_cor = (0.0, -1.66, STAIR_RUN, 1.66)
        clip_yard = (-23.9, -1.66, -0.10, 12.0)
        masks = []
        for nm, cx, cy, rx, ry in LEAF_PATCHES:
            masks.append((f"LeafDrift_{nm}",
                          gk.build_carpet_mask(
                              kit, f"{ROOT}/LeafDrift_{nm}", cx, cy, rx, ry,
                              M["leaf"], z=0.0, proud=lb["proud"],
                              n=24, rough=0.18,
                              seed=int(lb["seed"]) + int(nm),
                              feather=lb["feather"],
                              feather_cap=int(lb["feather_cap"]),
                              feather_clip=clip_cor,
                              z_fn=lambda x, y: path_z(x)),
                          (lambda x, y: path_z(x)), 0.0))
        for n, (cx, cy, sx, sy) in enumerate(PARAMS["yard_drifts"]):
            masks.append((f"YardLeaf_{n}",
                          gk.build_carpet_mask(
                              kit, f"{ROOT}/YardLeaf_{n}", cx, cy,
                              sx / 2.0, sy / 2.0, M["leaf"],
                              z=0.0, proud=lb["proud"], n=24, rough=0.20,
                              seed=int(yl["seed"]) + n,
                              feather=lb["feather"],
                              feather_cap=int(lb["feather_cap"]),
                              feather_clip=clip_yard),
                          (lambda x, y: 0.0), 0.0))
        # DEC-2 feather ring: individual leaf cards straddling the mask boundary, density
        #   falling to zero outward. Delegated to `scatter_debris` exactly the way
        #   `ground_kit.apply_ground` consumes `build_edge_break`'s `scatter_req`, so the
        #   asset pool stays in one place. `sct_debris_leaves_dry_*` / VEG_DEBRIS are
        #   season-scoped to the leaf scenes (C2 · 07 · 10 · D3) - PROC §6.1 - and 07 is one.
        #   **Every ring gets a two-argument `ground_fn`.** `scatter_debris` calls it as
        #   `ground_fn(px, py)` and wraps the call in `except Exception: pass`
        #   (`scene_common.py:2368-2381`), so handing it the scene's own one-argument
        #   `path_z` does not raise - it silently falls back to the flat `z` argument and
        #   lays every card at z = 0 over a corridor that descends 4.2 m. That is a real
        #   defect this pilot caught in its first render: a band of leaves hanging in mid-air
        #   across the frame. The lambda is the fix and the reason it must stay a lambda.
        nfeather = 0
        for nm, res, gfn, z0 in masks:
            for i, req in enumerate(res["scatter_req"]):
                rx0, ry0, rx1, ry1 = req["region"]
                nfeather += int(sc.scatter_debris(
                    stage, f"{ROOT}/{nm}_Feather_{i}",
                    rx0, ry0, rx1, ry1, z0,
                    cover=0.06, seed=gk.det_seed("s07.feather", nm, i),
                    edge_bias=float(req["edge_bias"]),
                    max_count=int(req["count"]), ground_fn=gfn,
                    scale_jitter=(0.7, 1.15)) or 0)
        print(f"[W3 F3] scene07 낙엽 마스크 {len(masks)}매(직사각 0) · "
              f"페더 링 인스턴스 {nfeather}")

    # -------------------------------------------------------------------
    # gable roof : 2 build_slope slabs (each falling +-X from the ridge)
    # -------------------------------------------------------------------
    def gable_roof(prefix, x_ridge, z_ridge, half_run, drop, y0, y1, thick,
                   mtl):
        """From the ridge (x_ridge, z_ridge), **fall** by drop on each side along ±X.
        build_slope only descends toward +X, so the −X half is given a start point at the eave
        (x_ridge−half_run, z_ridge−drop) with drop=−drop (a rise)."""
        sc.build_slope(stage, f"{prefix}/RoofP", x_ridge, z_ridge, half_run,
                       drop, y0, y1, thick, mtl, margin=0.10, collider=False)
        sc.build_slope(stage, f"{prefix}/RoofN", x_ridge - half_run,
                       z_ridge - drop, half_run, -drop, y0, y1, thick, mtl,
                       margin=0.10, collider=False)

    # -------------------------------------------------------------------
    # dressing : Iljumun gate · 2 stone lanterns · Dharma hall silhouette · pines · shrubs
    # -------------------------------------------------------------------
    def build_gate(M):
        g = PARAMS["gate"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            CYL(f"{ROOT}/Gate/Post_{tag}",
                (g["cx"], sgn * g["half_y"], g["post_h"] / 2.0),
                g["post_r"], g["post_h"], M["wood"], col=True)
            # [v6] plinth stones - eases the 'beige box' look of timber posts stuck straight into the ground
            CYL(f"{ROOT}/Gate/Plinth_{tag}",
                (g["cx"], sgn * g["half_y"], 0.15),
                g["post_r"] * 1.55, 0.30, M["stone_cap"], col=True)
        # architrave (horizontal lintel)
        BOX(f"{ROOT}/Gate/Beam",
            (g["cx"], 0.0, g["post_h"] + g["beam_t"] / 2.0),
            (g["post_r"] * 2.2, 2 * (g["half_y"] + g["beam_over"]),
             g["beam_t"]), M["wood"])
        gable_roof(f"{ROOT}/Gate", g["cx"], g["ridge_z"], g["roof_half_run"],
                   g["roof_drop"], -g["roof_y"], g["roof_y"], g["roof_t"],
                   M["roof"])
        # [v6] flying rafter (2nd-tier eave) - 0.34 m below the main roof and 0.30 m further out, making
        #      a two-tier eave shadow (a cue for the double eaves of a Korean temple gate). No interpenetration:
        #      the lower eave top (ridge−0.34) sits below the main roof soffit (ridge−roof_t).
        gable_roof(f"{ROOT}/GateEave", g["cx"], g["ridge_z"] - 0.45,
                   g["roof_half_run"] + 0.30,
                   g["roof_drop"] * (g["roof_half_run"] + 0.30)
                   / g["roof_half_run"],
                   -(g["roof_y"] + 0.22), g["roof_y"] + 0.22, 0.11,
                   M["wood"])

    def build_lanterns(M):
        """2 stone lanterns — base stone·lower pedestal·shaft·upper pedestal·light chamber·2-tier roof stone·jewel finial.
        [v6] The old shape (square body + square cap) combined with the masonry texture to read as a
        'brick chimney'. The member layout was changed to a standard lantern profile and the light
        chamber given dark light windows so it reads from the silhouette alone. Total height = lantern_height()."""
        ln = PARAMS["lantern"]
        pw, ph = ln["plinth_w"], ln["plinth_h"]
        for i, p in enumerate(PARAMS["lanterns"]):
            gz = ground_z(p["cx"], p["cy"])
            pre = f"{ROOT}/Lantern_{i}"
            BOX(f"{pre}/Plinth", (p["cx"], p["cy"], gz + ph / 2.0),
                (pw, pw, ph), M["stone_cap"], col=True)           # base stone
            z = gz + ph
            CYL(f"{pre}/Lower", (p["cx"], p["cy"], z + ln["lower_h"] / 2.0),
                ln["lower_r"], ln["lower_h"], M["stone_cap"])      # lower pedestal
            z += ln["lower_h"]
            CYL(f"{pre}/Shaft", (p["cx"], p["cy"], z + ln["shaft_h"] / 2.0),
                ln["shaft_r"], ln["shaft_h"], M["stone_cap"])      # shaft
            z += ln["shaft_h"]
            CYL(f"{pre}/Upper", (p["cx"], p["cy"], z + ln["upper_h"] / 2.0),
                ln["upper_r"], ln["upper_h"], M["stone_cap"])      # upper pedestal
            z += ln["upper_h"]
            # light chamber : 4 corner posts + dark interior (light window) - no interpenetration (posts are outboard)
            fo = (ln["fire_w"] - ln["pillar"]) / 2.0
            for j, (sx, sy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
                BOX(f"{pre}/Fire_{j}",
                    (p["cx"] + sx * fo, p["cy"] + sy * fo,
                     z + ln["fire_h"] / 2.0),
                    (ln["pillar"], ln["pillar"], ln["fire_h"]), M["stone_cap"])
            BOX(f"{pre}/FireCore",
                (p["cx"], p["cy"], z + ln["fire_h"] / 2.0),
                (ln["fire_w"] - 2 * ln["pillar"] - 0.02,
                 ln["fire_w"] - 2 * ln["pillar"] - 0.02,
                 ln["fire_h"] * 0.92), M["roof"])
            z += ln["fire_h"]
            BOX(f"{pre}/Cap", (p["cx"], p["cy"], z + ln["cap_h"] / 2.0),
                (ln["cap_w"], ln["cap_w"], ln["cap_h"]), M["stone_cap"])
            z += ln["cap_h"]
            BOX(f"{pre}/Cap2", (p["cx"], p["cy"], z + ln["cap2_h"] / 2.0),
                (ln["cap2_w"], ln["cap2_w"], ln["cap2_h"]), M["stone_cap"])
            z += ln["cap2_h"]
            sc.add_sphere(stage, f"{pre}/Jewel",
                          (p["cx"], p["cy"], z + ln["jewel_r"]),
                          (ln["jewel_r"],) * 3, M["stone_cap"])    # jewel finial

    def build_hall(M):
        """Upper Dharma hall silhouette : podium (stone wall) + pillar row + gable roof."""
        hl = PARAMS["hall"]
        BOX(f"{ROOT}/Hall/Base", (hl["cx"], hl["cy"], hl["base_h"] / 2.0),
            (hl["sx"] + 1.2, hl["sy"] + 1.2, hl["base_h"]), M["rock"],
            col=True)
        n = int(hl["n_posts"])
        for j in range(n):
            t = (j / float(n - 1)) - 0.5
            px = hl["cx"] + t * (hl["sx"] - 0.8)
            for tag, sgn in (("P", 1.0), ("N", -1.0)):
                CYL(f"{ROOT}/Hall/Post_{j}_{tag}",
                    (px, hl["cy"] + sgn * (hl["sy"] / 2.0 - 0.4),
                     hl["base_h"] + hl["post_h"] / 2.0),
                    hl["post_r"], hl["post_h"], M["wood"])
        # body (wall) - a dark panel inside the pillar row
        BOX(f"{ROOT}/Hall/Body",
            (hl["cx"], hl["cy"], hl["base_h"] + hl["post_h"] / 2.0),
            (hl["sx"] - 1.0, hl["sy"] - 1.2, hl["post_h"]), M["wood"])
        gable_roof(f"{ROOT}/Hall", hl["cx"], hl["ridge_z"],
                   hl["roof_half_run"], hl["roof_drop"],
                   hl["cy"] - hl["roof_y"], hl["cy"] + hl["roof_y"],
                   hl["roof_t"], M["roof"])

    def build_nature(M):
        tr = PARAMS["tree"]
        for name, cx, cy, zone, th in PARAMS["pines"]:
            gz = _zone_z(cx, cy, zone)
            sc.build_tree(stage, f"{ROOT}/Pine_{name}", cx, cy, gz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=tr["trunk_r"], trunk_h=th,
                          stake_r=0.004, stake_h=0.02, stake_off=0.2)
        # shrub = 3 overlapping flattened ellipsoids (scene04 v5 convention - no angular slabs)
        #   [v6] On a slope (zones north/south fall along X), grounding by the blob centre z leaves
        #   **the downhill side floating by rx·tan19 deg** -> the ground at the downhill end (x+rx)
        #   is used as the datum instead, removing the float structurally.
        sh = PARAMS["shrub"]
        emb = sh["embed"]
        for n, (cx, cy, zone) in enumerate(PARAMS["shrubs"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(sh["blobs"]):
                bx, by = cx + dx, cy + dy
                gz = min(_zone_z(bx - rx, by, zone), _zone_z(bx, by, zone),
                         _zone_z(bx + rx, by, zone))
                sc.add_sphere(stage, f"{ROOT}/Shrub_{n}_{j}",
                              (bx, by, gz + rz * (1.0 - emb)),
                              (rx, ry, rz), M["shrub"])

    def build_horizon(M):
        """Horizon closure : front ridges (near, in 3 pieces + mid·far) + crest forest bands + rear forest line.
        [v6] The near ridge is broken into 3 staggered slabs and each crest carries a round-crown
        forest band, clearing the 'straight ridgeline + black wall' (albedo: see material)."""
        rg = PARAMS["ridge"]
        for i, r in enumerate(rg):
            BOX(f"{ROOT}/Ridge_{i}", (r["cx"], r["cy"], r["z0"] + r["h"] / 2.0),
                (r["sx"], r["sy"], r["h"]), M[f"ridge_{r['tone']}"], col=True)
        for n, (ri, hh, tone) in enumerate(PARAMS["ridge_crest"]):
            r = rg[ri]
            top = r["z0"] + r["h"]
            sc.build_hedge(stage, f"{ROOT}/RidgeCrest_{n}",
                           r["cx"] - r["sx"] * 0.62, r["cy"] - r["sy"] / 2.0,
                           r["cx"] + r["sx"] * 0.62, r["cy"] + r["sy"] / 2.0,
                           hh, mtl=M[f"crest_{tone}"], base_z=top - 0.4)
        for i, t in enumerate(PARAMS["ridge_trees"]):
            r = rg[t["ri"]]
            sc.build_tree(stage, f"{ROOT}/RidgeTree_{i}", r["cx"], t["cy"],
                          r["z0"] + r["h"] - 0.4,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.16, trunk_h=4.2, stake_r=0.004,
                          stake_h=0.02, stake_off=0.2)
        bh = PARAMS["back_hedge"]
        for i, h in enumerate(PARAMS["back_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           bh["cx"] - bh["sx"] / 2.0,
                           h["cy"] - bh["length"] / 2.0,
                           bh["cx"] + bh["sx"] / 2.0,
                           h["cy"] + bh["length"] / 2.0, bh["h"],
                           base_z=h["base"])
        for i, t in enumerate(PARAMS["back_trees"]):
            sc.build_tree(stage, f"{ROOT}/BackTree_{i}", t["cx"], t["cy"],
                          t["gz"], M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_h=t["trunk_h"], stake_r=0.004, stake_h=0.02,
                          stake_off=0.2)
        for nm, x0, x1, y0, y1, hh, bz in PARAMS["far_hedges"]:
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{nm}", x0, y0, x1, y1, hh,
                           base_z=bz)

    def build_sign(M):
        """[v5 shared layer] Temple notice board — at the entrance (before the gate), facing the approach."""
        sg = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/SignInfo", sg["cx"], sg["cy"], 0.0,
                      sg["yaw"], M["sign_info"], w=sg["w"], h=sg["h"],
                      pole_h=sg["pole_h"], pole_mtl=M["wood"],
                      back_mtl=M["sign_back"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P12 courtyard_dg. Runs after the dressing so the
    #   scatter callback is invoked last (spec Sec.8.4 call-order rule).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        gp = ground_plan()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(stain_dirt=M["leaf"], stain_water=M["gk_moss"],
                  wear=M["gk_wear"], edge_break=M["leaf"], litter=M["leaf"],
                  debris=M["gk_rock"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene07 P12 · 프림 {res['prims']} · "
              f"산포 {res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_cues(M):
        """Cues that are not the practice here (code path only — all False by default)."""
        if cfg["cue_railing"]:
            def gfn(x):
                return path_z(x)
            sc.build_railing_line(stage, f"{ROOT}/Rail", -1.55, 0.0, 0.0,
                                  STAIR_RUN, STAIR_DROP, gfn, M["rail"],
                                  rail_h=0.9, post_r=0.035, spacing=1.4,
                                  rail_r=0.035)
        if cfg["cue_tactile"]:
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, f"{ROOT}/Tactile", -0.62, -0.02,
                             -1.6, 1.6, tac, z=0.0)
        if cfg["cue_nosing"]:
            for s in STONES:
                BOX(f"{ROOT}/Nose_{s['i']}",
                    (s["xb"] - 0.03, s["cy"], s["top"] + 0.002),
                    (0.06, s["w"] * 0.9, 0.012), M["stone_cap"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if cfg["hazard_stairs"]:
        build_terrain(M)
        build_stones(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    build_horizon(M)
    if cfg["cue_scene_dressing"] and cfg["hazard_stairs"]:
        build_gate(M)
        build_lanterns(M)
        build_hall(M)
        build_nature(M)
    if cfg["cue_sign"] and cfg["hazard_stairs"]:
        build_sign(M)
    if cfg["hazard_stairs"]:
        build_ground_kit(M)          # [W2-D] ground elements, dressing last

    rises, gaps, enter, exit_ = stone_metrics()
    print(f"[기하] 배석 {len(STONES)}석 run={STAIR_RUN:.2f} drop="
          f"{STAIR_DROP:.2f} · 답차 {min(rises):.3f}~{max(rises):.3f} · "
          f"간격 {min(gaps):.3f}~{max(gaps):.3f} · 측방 낙차 {SIDE_DROP:.2f}")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── camera + render mode ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["temple_walk"]
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

    # ── GUI look check ──
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene07_{ts}.png")
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
