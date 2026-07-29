# -*- coding: utf-8 -*-
"""
scene10_park_deck_switchback.py — NegObs synthetic scene 10 (v5 R5): park slope deck switchback

Type   : R5 (v5 redesign) — timber deck zigzag stair (inherits the open-riser see-through cue)
Spec   : Docs/briefs/multi_scene_brief_v5.md §R5 + Docs/scene_redesign_v5_proposal.md
Shared : scene_common.py (unmodified) / skeleton convention : scenes/main/scene04_parktrail.py
Legacy : scenes/archive_v3/scene10_switchback_cliff.py
         (rot_group 180° reversal + the **parallel switchback Y band** convention · open_riser builder)

────────────────────────────────────────────────────────────────────────────
[Hazard]
  A timber deck switchback stair on the slope of a neighbourhood park trail. The
  hazard is **the reality of falling short of code**.

  (1) One landing railing is broken — on the first landing (z −1.65, outer edge x 4.4)
      two rails have come away and only the posts remain. The ground below is z −6.62
      → a **4.97 m open drop**. A railing reduced to posts is easily mis-detected as
      'railing present' from the robot's viewpoint (a trap case for the
      equipment-inference cue).
  (2) Open risers — the flight below and the ground show through between the timber
      treads. With no tread/riser light-dark pair, the nosing cut line never forms.
  (3) Leaf litter — a leaf_ground band bites over and covers the edges of the top two
      steps (treads 1·2), erasing the first nosing. Reading that as 'a flat deck entry'
      from the approaching robot's viewpoint (h0.3) is the GT-positive core of this scene.
  (4) The 30° grass slope south of the trail (−Y) is unguarded — beyond the trail
      shoulder (y −1.6) it falls at 30°, dropping 2.3 m within 4 m. No railing or kerb
      (not the practice on a park dirt trail).

[Walking continuity self-check table]  — entry → descent → exit (SMOKE recomputes all of it)
  ┌ Segment ────────────────┬ Coords (x, y band, z) ─────────┬ Step ─────────┐
  │ Upper trail (entry)     │ x −40..−1.5, y −1.6..1.45, 0.0 │ level         │
  │ Entry deck (wall head)  │ x −1.5..0,  y ±1.40,   −0.005  │ 0.005         │
  │ Flight0 (+X, −Y band)   │ x 0→3.0,  z 0→−1.65 (10 steps) │ riser 0.165   │
  │ Landing0 (reversal)     │ x 3.0..4.4, y ±1.40,   −1.65   │ 0 (flush)     │
  │ Flight1 (−X, +Y band)   │ x 3.0→0.0, z −1.65→−3.30       │ riser 0.165   │
  │ Landing1                │ x −1.4..0,  y ±1.40,   −3.30   │ 0             │
  │ Flight2 (+X, −Y band)   │ x 0→3.0,   z −3.30→−4.95       │ riser 0.165   │
  │ Landing2                │ x 3.0..4.4, y ±1.40,   −4.95   │ 0             │
  │ Flight3 (−X, +Y band)   │ x 3.0→0.0, z −4.95→−6.60       │ riser 0.165   │
  │ Landing3                │ x −1.4..0,  y ±1.40,   −6.60   │ 0             │
  │ Lower path (exit)       │ ground z −6.62 (2 cm below L3) │ 0.02          │
  └─────────────────────────┴────────────────────────────────┴───────────────┘
  · turn path on a landing: (x_bot, y −0.70) → (landing centre, y 0) → (x_bot, y +0.70)
    — both width bands fall inside the landing (y ±1.40), so there is no break.
  · vertical clearance between flights = 2×1.65 − 0.29 (stringer+tread) = 3.01 m.
  · even band y[−1.39,−0.01] / odd band y[+0.01,+1.39] — overlap 0 (gap 0.02).

[Geometry core]
  · 4 flights × 10 steps, riser 0.165 / tread 0.30 / width 1.38, total drop 6.60.
  · A pure switchback makes no horizontal progress (plan x −1.4..4.4). The ground along
    the stair must therefore be effectively vertical, and that is realised as a **park
    cut stone retaining wall** (head wall at x=−1.5 + side wall at y=1.45). The brief's
    "30° slope" is met by the **surrounding slopes** (the north +Y 30° grass slope /
    the south −Y 30° grass slope).
  · No ground plane covers the cavity (the stair passage) — the upper trail plate stops
    at x=−1.5, and in front of it (x −1.5..4.4) only the lower path (z −6.62) exists.

[v6 verdict revision — judge_v6_rt_new7.md §4 + supervisor decision, 3 items]
  (1) **sun reselected** (supervisor approved — front lit on the open side). The old
     `SUN_AZ_OFFSET=171.5` (world az 205 = sun in the −X·−Y sky) put the whole
     switchback passage into the shadow of the **head wall (x=−1.5, top z 0)**: the
     shadow boundary of a point at depth d is x < −1.5 + 0.766·d, so out to d 6.6 m
     everything up to x 3.56 is dark = the entire passage. That directly killed the
     `from_below` and `through_treads` shots.
     → `SUN_AZ_OFFSET=216.5` (world az = 33.5+216.5 = **250**, shadow az 70).
       The only open directions in this scene are **−Y (the south lower park)** and +X,
       so the sun is swung far toward −Y to put direct light into the passage.
       Back-tracing the sun ray as a check:
         (x 1.7, y −0.7, z −4.24) → it reaches z=0 at (0.47, −4.07) : it does not cross
         the x=−1.5 plane → no occlusion by the head wall or the south slope =
         **direct sun arrives**.
       lambert per face (elevation 49.79 → horizontal component 0.6456):
         −Y faces (stringers·landing noses·north wall = the 4 shots)  0.607
         −X faces (grid axis front·distant ridge)                     0.221
         top faces (trail·landings·treads·grass)                      0.763
       The −X faces of the grid (viewing +X) drop to 0.221, but the grid image is mostly
       **top faces** (0.763), so no reading is lost. Conversely the −Y faces go
       0.273→0.607, a factor of 2.2.
     · The lowest point (landing3, x −1.4..0, z −6.60) is directly under the head wall and
       stays shaded under any western sun — it is left as a physical fact of a 6.6 m cut
       floor (all 4 key-cue shots are in direct sun).
  (2) **dispelling the "fortress wall" impression** (verdict (5) 'material and scale
     replacement is the key to reading this as a park')
     (a) `rock_wall` UV 3.0 m → **0.9 m** : 0.6 m-class blocks of fortress masonry →
         0.18 m-class **quarried rubble** (the practice on park cut faces).
     (b) **separate the built wall from the natural cut face by material** : only the
         head wall and the north wall are masonry (`rock_wall`); the body of the south
         slope (the cut face dropping from x=−1.5 into the lower park) is `rock_face`
         (jointless natural rock) — previously that face was masonry too, so the left
         half of `from_below` was one solid rampart.
     (c) **two-tier east wall** (x 5.2..44) : a single 6.62 m wall → lower 3.32 m +
         **berm 1.0 m (planted)** + upper 3.30 m. This is the standard section for an
         urban park cut wall, and the deck run (x −1.5..5.2) keeps the single wall, so
         the **hazard geometry is unchanged**.
     (d) **coping band on top of the wall** — a concrete strip projecting 0.08 m past
         the wall face.
  (3) **the railing read as a temporary ladder frame / gallows** (verdict (5)) →
     **vertical bars** (0.30 m pitch) were added to a railing that had only top and mid
     rails. This is the standard for a park deck railing, and with the bars in place the
     raking rails of the adjacent flight are no longer misread as bracing.
  (4) **leaf and dirt-trail square decals** (C-7) · **confetti saturation** (verdict (5))
     → dirt UV 3.0→1.1, leaf 1.8→1.05, tints neutralised, ground leaf patches broken up
     by overlaying 3 rotated copies.
  (5) shrubs floating above the slope → the blob grounding z was lowered to the
     **downhill ground**.
  (6) distant lollipops (C-4) → jitter on distant tree trunk radius and height + a forest
     silhouette band on the distant ridge crest (build_hedge round crowns).

[v7 verdict revision — judge_v7_rt_A.md §7 "the 4 mise-en-scene shots do not read as a park"]
  Conclusion of the verdict: **"what is left is not the code but the camera"** — the
  material fixes (smaller rubble, separated natural rock, two-tier wall, vertical bars)
  are sufficient, but all 4 shots were deck close-ups, so no park signal (grass, shrubs,
  trees, visitor furniture) entered a single frame. The grid shots, by contrast, do read
  as a park = the problem is framing, not geometry.
  (1) **mirror `from_below` to the open side (−Y)** (direct instruction (b)) : the old
     sight line 129.6° had half its subject facing +X (head wall and cut face =
     lambert −0.342), giving mean 36.4·dark 66.3 %. eye (8.0,−7.5)→**(5.2,−10.8)**,
     sight 105.4° (normal 285.4° = **lambert +0.527**), pitch +6.6°. The bottom of the
     frame lands on the **lower park dirt trail**, and 3 shrubs, 3 north grass slopes,
     the waymarker and the bench = **8 park anchors** are inside the FOV.
  (2) **`reversal` pulled back and raised** ((a)) : eye (3.7,−3.2,−0.30)→**(6.6,−6.6,1.20)**,
     pitch −24° → **−16°**. The top of the frame (+2.0° elevation) now carries the
     **north 30° grass slope** beyond the wall coping, so about a quarter of the image is
     greenery (landing0 and flights 0/1 are kept).
  (3) **`broken_rail` rotated south** : sight 135° (lambert +0.273, damaged and intact
     railing in the same dark band) → 112° (**+0.480**). The bottom ray passes through the
     vertical space under landing0 and lands at z −4.46 → the depth of the drop stays in
     the frame.
  (4) **waymarker shrunk again** ((c)) : blades 0.72×0.11 → **0.58×0.09**, heights
     1.72/1.98 → **1.80/2.06**, post r 0.065 → 0.080 · total height 2.26 → post 79 % exposed.
  (5) one shrub clump added in the lower park (0.5,−5.5) — for the left framing of
     `from_below` (passes §6 "the minimum needed to read": the park reading of this shot
     is the very reason for the revision).
  Check: SMOKE `[v7 mise-en-scene]` — per shot the sight line / normal / **lambert**, the
        ground point the bottom ray lands on, and the park anchors inside the FOV
        (horizontal ±30° · vertical ±18°).
  Not addressed: `through_treads` (a see-through close-up, "improvement confirmed" in v7)
        has 0 anchors by nature — only its illumination is confirmed at lambert +0.620
        and the composition is kept.
────────────────────────────────────────────────────────────────────────────

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene10_park_deck_switchback.py

Auto capture : NEGOBS_CAPTURE=1 python scene10_park_deck_switchback.py
Smoke        : NEGOBS_SMOKE=1 python3 scene10_park_deck_switchback.py  (no boot)

Coordinates: Z-up, m. Flights descend along local +X (convention). Odd flights use
        rot_group 180° (pivot = top of the flight) → −X in world. Grid axis = upper approach (+X).
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
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs toggles the hazard geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> flights become a flat z=0 deck (drop removed)
    "cue_railing":        True,    # park deck = railing is the practice. **but one break at the landing0 outer edge**
    "cue_tactile":        False,   # not the practice on a park dirt trail (v5 brief §shared) - code path only
    "cue_material_break": True,    # timber deck vs grass / leaf ground contrast
    "cue_sign":           False,   # [v5.2 user] arbitrary warning sign removed - nothing placed (key reserved only)
    "cue_scene_dressing": True,    # trees·shrubs·waymarker·bench·shelter pavilion
    "cue_nosing":         False,   # a nosing band on a timber deck is not the practice - code path only
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- switchback flights (inherits the parallel Y-band convention of archive_v3/scene10) ---
    #   half_w 0.69 -> width 1.38 ~ the brief's 1.4. y_off 0.70 -> 0.02 gap between the two bands.
    flights=dict(n=4, steps=10, riser=0.165, tread=0.30, half_w=0.69,
                 y_off=0.70, tread_t=0.05, gap=0.02, z_top=0.0),
    # landing 1.4 (X) x 2.8 (Y) - covers both width bands
    landing=dict(size=1.4, thick=0.12, y0=-1.40, y1=1.40),
    # entry deck : from the retaining wall head (x −1.5) to the first step (x 0) - joins the upper trail
    entry=dict(x0=-1.5, x1=0.0, top=-0.005, thick=0.10),
    # deck posts : the four landing corners (0.15 inside the landing x ends) x y +-half_y.
    #   the actual (x, z range) is derived from the landing stack by post_segments().
    post=dict(r=0.075, half_y=1.25, inset=0.15),
    # railing : top rail h1.05 / mid rail h0.55, post spacing 1.05
    #   [v6] baluster = vertical bar (the standard for park deck railings). Rails alone read
    #   as a 'temporary ladder frame' (verdict §4 (5)). At the break (landing0 outer) the bars are gone too.
    rail=dict(h=1.05, mid=0.55, post_r=0.05, post_h=1.10, bar_t=0.06,
              spacing=1.05, broken_landing=0,   # landing0 outer = the break
              bal_r=0.022, bal_step=0.30, bal_top=1.02),

    # === [W2-D ground_kit] P18 `deck_trail_hybrid` - spec Sec.5.8 / Sec.13.4 =
    #  Sec.13 measured this scene's three h0.3 cuts and killed the provisional
    #  P10 assignment: **d2 is entry deck, d5/d10 are park dirt trail + grass**.
    #  Hence two plans, at two different z:
    #    A `ground_plan()`      trail  z = TrailPath z_top (0.002)
    #    B `ground_plan_deck()` entry deck z = entry top (-0.005)
    #  Prescription (Sec.13.4):
    #    10-1 edge_break on the dirt<->grass line y = +-0.85 (dE76 15.2, the
    #         same "0 px transition" defect as scene04)
    #    10-2 leaf-decal outline break - scatter ring around the two trail
    #         decals (dE76 27.3, 1.8x stronger than 10-1)
    #    10-3 entry-deck plank gaps, d2 only
    #    10-4 trodden wear axis, width 0.90
    #    10-5 exposed gravel scatter, expose <= 0.06
    #  Dropped from the profile: `edge_litter` - `_compose_ops` forces its
    #  width to the region span (1.70 m, ~7x the 0.25 m ledger value) and the
    #  two bands then straddle the wear lane at an identical top z.
    #  Sec.7.3 invariant for scene10 ("the upper trail is cut at x = -1.5") is
    #  respected by construction: plan A stops at TrailPath x1 = -1.6, and
    #  every element of plan B is flagged `deck`.
    gkit=dict(
        wear_w=0.90,
        gravel_n=85,                  # [W2 F2] 120 -> 85 (cover 0.12 -> 0.08 is the
                                  #   binding lever here; the cap is not reached)
        leaf_ring_n=15,               # 10-2: 12-20 per decal, Sec.13.4
        leaf_ring_pad=0.28,           # ring width around the decal outline
        deck_gaps=9,                  # 10-3: 9 gaps over the 1.5 m entry deck
        seed=10,
    ),
    # --- axis-aligned ground plates (name, x0, x1, y0, y1, z_top, thick, mtl) ---
    #   v5 regression checklist (3) : the upper trail **stops** at x=−1.5
    #   (it does not cover the stair cavity). Beyond it there is only the lower path (−6.60).
    #   [Z-fighting avoidance] the lower path ground top is −6.62, 2 cm below the deck's
    #   lowest point (−6.60) -> landing3 and the last tread of flight3 never become coplanar
    #   with the ground (lesson 8). The 0.02 m walking step is verified in the continuity table.
    #   [v6 (2)(c)] BankCut (north retaining wall) stays a single 6.62 m wall only over the deck
    #   run x −40..5.2; east of it (x 5.2..44) it splits into **lower wall + berm (1.0 m) + upper wall**.
    #   berm top z −3.30; the upper wall steps back to y 2.45..2.60, which creates a shadow line.
    plates=[
        ("UpperTrail",   -40.0,  -1.5,  -1.60,  1.45,  0.00, 0.45, "grass"),
        ("UpperBody",    -40.0,  -1.5,  -1.60,  1.45, -0.45, 6.95, "rock"),
        ("TrailPath",    -40.0,  -1.6,  -0.85,  0.85,  0.002, 0.06, "dirt"),
        ("BankCut",      -40.0,   5.20,  1.45,  2.60,  0.00, 7.40, "rock"),
        ("EastTierLow",    5.20, 44.0,   1.45,  2.45, -3.30, 4.30, "rock"),
        ("EastTierUp",     5.20, 44.0,   2.45,  2.60,  0.00, 3.50, "rock"),
        ("LowerParkMain", -1.5,  44.0, -13.00,  1.45, -6.62, 1.50, "grass"),
        ("LowerParkFar", -40.0,  44.0, -60.00, -13.00, -6.62, 1.50, "grass"),
        ("LowerPath",     -1.5,  44.0,  -4.40, -2.60, -6.618, 0.06, "dirt"),
        ("FarHill",      -40.0,  44.0,  15.00, 40.00,  7.16, 9.00, "grass"),
        # distant ridge across the valley (+X horizon closure)
        ("FarRidge",      44.0,  78.0, -60.00, 40.00,  3.50, 12.00, "grass"),
    ],
    # --- Y-direction slopes (_ybank, rotX slab) : (name, x0,x1, y_hi,z_hi, y_lo,z_lo,
    #     thick, mtl). +Y is high and it falls toward −Y.
    ybanks=[
        # north park slope (30.0 deg) - retaining wall top (y2.60,z0) -> ridge (y15,z7.16)
        ("NorthBank", -40.0, 44.0, 15.00, 7.16, 2.60, 0.00, 9.00, "grass"),
        # south unguarded slope (30.1 deg) - trail shoulder (y−1.6,z0) -> lower ground (y−13)
        ("SouthBankCap", -40.0, -1.5, -1.60, 0.00, -13.00, -6.62, 0.50,
         "grass"),
        # [v6 (2)(b)] body material rock (masonry) -> rockface (jointless natural rock).
        #   the +X end face of this slab (x=−1.5, y −1.6..−13) is the **natural cut face**
        #   dropping to the lower park, and it fills the left half of `from_below`. As masonry it is a rampart.
        ("SouthBankBody", -40.0, -1.5, -1.60, -0.50, -13.00, -7.12, 7.50,
         "rockface"),
    ],
    # --- [v6] retaining wall coping band : (name, x0, x1, y0, y1, z_top, thick) ---
    #     projects 0.08 m past the wall face to cast a shadow line at the top (reads as civil works).
    #   (the head wall top is covered by the entry deck, so no coping - avoids interpenetration)
    copings=[("BankW", -40.0, 5.20, 1.41, 2.60, 0.02, 0.18),
             ("BankE", 5.20, 44.0, 2.37, 2.60, 0.02, 0.18),
             ("Tier", 5.20, 44.0, 1.37, 2.45, -3.28, 0.16)],
    # --- [v6] berm planting band : (x0, x1) - shrub strip on the berm top (z −3.30) ---
    berm_hedges=[(5.6, 15.5), (19.0, 29.0), (33.0, 43.4)],
    berm=dict(y0=1.62, y1=2.34, h=0.85, base_z=-3.30),

    # --- leaf bands : hiding the top two step edges (flight0 treads 1·2) + ground litter ---
    # [W2 F3] proud 0.012 -> 0.005 — the rim shadow that drew an outline round the
    #   trail leaf patches.
    leaf=dict(thick=0.02, proud=0.005, over=0.045),
    # [v6 C-7] ground leaf patch : one square decal -> 3 overlaid with rotation / size jitter
    leaf_patch=dict(seed=1007, subs=3, scale=(0.55, 0.90), off=0.42, rz=32.0),
    leaf_ground_patches=[(-3.2, -0.9, 1.6, 1.1, "trail"),
                         (-5.6, 0.7, 1.4, 1.0, "trail"),
                         (1.4, -3.4, 2.2, 1.6, "lower"),
                         (5.0, -1.9, 2.0, 1.5, "lower")],

    # --- dressing ---
    # 10 trees (cx, cy, zone, trunk_h) - zone: north/south/lower/trail
    trees=[(-6.0, 5.5, "north", 3.6), (0.5, 8.0, "north", 4.0),
           (7.0, 6.0, "north", 3.4), (13.0, 9.5, "north", 3.8),
           (-14.0, 4.5, "north", 3.2), (-20.0, 7.5, "north", 3.6),
           (-9.0, -7.5, "south", 3.0), (-17.0, -10.0, "south", 3.4),
           (9.0, -9.0, "lower", 3.2), (16.0, -5.0, "lower", 3.6),
           (2.0, -11.5, "lower", 3.0), (21.0, -12.0, "lower", 3.4)],
    tree=dict(trunk_r=0.10),
    # shrub clumps (overlaid flattened ellipsoids - scene04 v5 convention)
    #   [v6] clump 4 is added at the top corner of the south cut face (x=−1.5) to hide the
    #        straight cut line (softens the 'rampart' impression in the left half of from_below).
    shrubs=[(-4.0, 3.3, "north"), (3.5, 4.0, "north"), (10.0, 3.6, "north"),
            (-12.0, 3.4, "north"), (-6.5, -4.2, "south"),
            (-14.0, -6.0, "south"), (6.0, -4.6, "lower"),
            (12.0, -2.6, "lower"),
            (-2.3, -2.7, "south"), (-2.6, -5.4, "south"),
            (-2.2, -8.2, "south"), (-2.9, -10.8, "south"),
            # [v7 verdict §7 (a)] one more park shrub is set at the left of the from_below frame
            #   (yaw −26 deg) so the deck is wrapped in planting. The sight corridor (camera->deck)
            #   runs in the x 3.5 band, so there is no intrusion - checked by SMOKE [v7 mise-en-scene].
            (0.5, -5.5, "lower")],
    shrub=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.75, 0.60, 0.35),
                      (0.54, 0.41, 0.51, 0.43, 0.26),
                      (-0.45, -0.37, 0.56, 0.39, 0.29))),
    # timber waymarker (post + 2 direction blades + post cap)
    #   [v6] the old spec (two 0.90x0.16 blades @1.55/1.80) read as a **picnic table** at a
    #   distance -> blades made thinner and shorter (0.72x0.11), heights spread (1.72/1.98)
    #   and a cap added on top to give a 'post-type waymarker' silhouette.
    #   [v7 verdict §7 (3)] the two 0.72x0.11 blades still read as a "low picnic table with a
    #   wide top" -> blades shrunk further to **0.58x0.09** and lifted to 2.06/1.80, so the
    #   **exposed post grows to 1.80 m (79 % of the total height)**. The post thickens
    #   0.065 -> 0.080 so the 'post-type' silhouette reads first at a distance.
    signpost=dict(cx=-3.6, cy=1.00, post_r=0.080, post_h=2.26,
                  arm=(0.58, 0.05, 0.09), arm_off=0.34,
                  arms=((2.06, 15.0), (1.80, 195.0)),
                  cap=(0.20, 0.20, 0.07)),
    # bench 1 (upper trail)
    bench=dict(cx=-6.5, cy=0.90, yaw=180.0),
    # shelter pavilion (lower path). [v7] even after from_below is mirrored from
    #   (5.2,−10.8) to (2.4,−0.6), the pavilion (centre 11.5,−6.0) sits at yaw 68 deg, outside the FOV - still no sight interference.
    pergola=dict(x0=10.0, x1=13.0, y0=-7.5, y1=-4.5, z_roof=-4.20, post_r=0.10,
                 roof_t=0.16),
    # [v5.2 user] arbitrary warning sign removed - the stair-caution sign (PARAMS['sign']) is deleted.
    # distant closure : forest band beyond the lower park + trees on the upper ridge
    far_hedges=[dict(x0=-40.0, x1=6.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=6.0, x1=44.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=40.0, x1=43.0, y0=-33.0, y1=1.40, h=4.0)],
    # [v6 C-4] forest silhouette band on the distant ridge crest (FarRidge top z 3.50) -
    #   the horizon is closed with a round-crown strip instead of individual lollipops.
    #   + the **straight horizon** of the north hill (FarHill top 7.16), verdict (1)'s 'stage
    #     backdrop', is broken up by a crest band as well.
    ridge_crest=[dict(x0=46.0, x1=54.0, y0=-58.0, y1=-8.0, h=5.0, base=3.10),
                 dict(x0=49.0, x1=57.0, y0=-10.0, y1=38.0, h=6.0, base=3.10),
                 dict(x0=-40.0, x1=6.0, y0=13.6, y1=17.4, h=5.2, base=6.76),
                 dict(x0=6.0, x1=44.0, y0=13.6, y1=17.4, h=4.6, base=6.76)],
    # (cx, cy, zone) - north = north slope, far = distant ridge (z 3.5), low = lower ground
    hill_trees=[dict(cx=-22.0, cy=20.0, zone="north"),
                dict(cx=-8.0, cy=24.0, zone="north"),
                dict(cx=6.0, cy=19.0, zone="north"),
                dict(cx=20.0, cy=25.0, zone="north"),
                dict(cx=32.0, cy=20.0, zone="north"),
                dict(cx=50.0, cy=-14.0, zone="far"),
                dict(cx=58.0, cy=2.0, zone="far"),
                dict(cx=52.0, cy=16.0, zone="far"),
                dict(cx=62.0, cy=-28.0, zone="far"),
                dict(cx=-14.0, cy=-38.5, zone="low"),
                dict(cx=10.0, cy=-38.5, zone="low"),
                dict(cx=28.0, cy=-38.5, zone="low")],

    # --- materials ---
    material=dict(
        # [v6] rock_wall 3.0->0.9 (fortress masonry -> quarried rubble) · dirt 3.0->1.1
        #      (confetti saturation) · leaf 1.8->1.05 · rock_face (natural cut face) added
        #      grass 4.0->2.6 (softens the 'quilt pattern' repetition on the slope)
        scale=dict(wood_dark=1.0, rock_wall=0.9, rock_face=2.2, grass=1.4,
                   leaf_ground=1.05, dirt_park=1.1, concrete_wall=2.4),
        deck_tint=(1.00, 0.96, 0.90),          # deck planks (slightly weathered tone)
        stringer_tint=(0.72, 0.70, 0.66),      # stringers·posts (darker)
        grass_tint=(0.55, 0.68, 0.42),
        leaf_tint=(0.88, 0.85, 0.80),
        dirt_tint=(0.78, 0.76, 0.72),          # [v6] saturation and value lowered (avoids confetti)
        rock_tint=(0.82, 0.82, 0.80),          # [v6] rubble greyed (removes the European rampart tone)
        rockface_tint=(0.80, 0.80, 0.78),
        coping_tint=(0.78, 0.77, 0.74),
        shrub=(0.030, 0.047, 0.021), shrub_rough=1.0,
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
    ),   # [v5.2 user] arbitrary warning sign removed - sign_back colour constant deleted

    # --- lighting: scene01 noon verified constants + the sun specified in v5 §R5 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # [v6 verdict §4 (4) + supervisor decision item 3 - reselection approved (front lit on the open side)]
    #   old 171.5 (az 205) -> the head retaining wall put the whole switchback passage in shadow.
    #   new 216.5 = world az 250 (sun in the −X·−Y sky, shadow az 70).
    #   direct sun enters the passage from the open side (−Y lower park). Check in docstring (1).
    SUN_AZ_OFFSET=216.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene10")

ASSET_ROLES = ["wood_dark", "rock_wall", "rock_face", "concrete_wall",
               "grass", "leaf_ground", "dirt_park",
               "hdri", "mdl"]     # [v5.2 user] arbitrary warning sign removed

DECK_BOT = -6.60                   # deck bottom (landing3 top = end of flight3)
GROUND_Z = -6.62                   # lower path ground top (2 cm below the deck)
TRAIL_Z = 0.0                      # upper trail
HEAD_X = -1.5                      # retaining wall head = end of the upper plate
FAR_RIDGE_Z = 3.50                 # distant ridge top
NORTH_TAN = math.tan(math.radians(30.0))
SOUTH_SLOPE = 6.62 / 11.40         # south slope gradient (= tan 30.14 deg)


# ===========================================================================
# [D] flight layout precomputation (no boot needed)
# ===========================================================================
def compute_flights():
    fl = PARAMS["flights"]
    run = fl["steps"] * fl["tread"]             # 3.00
    fdrop = fl["steps"] * fl["riser"]           # 1.65
    land = PARAMS["landing"]["size"]            # 1.40
    seq = []
    x_top, z_top = 0.0, float(fl["z_top"])
    for k in range(fl["n"]):
        even = (k % 2 == 0)
        rot = 180.0 * (k % 2)
        z_bot = z_top - fdrop
        if even:
            x_bot = x_top + run
            lx0, lx1 = x_bot, x_bot + land      # the landing juts forward along the travel direction
        else:
            x_bot = x_top - run
            lx0, lx1 = x_bot - land, x_bot
        seq.append(dict(k=k, x_top=x_top, z_top=z_top, x_bot=x_bot,
                        z_bot=z_bot, rot=rot, even=even, lx0=lx0, lx1=lx1))
        # next flight top = **exactly where the flight ended**, not the landing's far corner
        # (archive_v3/scene10 audit A-10-2 - prevents burial under the landing)
        x_top, z_top = x_bot, z_bot
    return seq, run, fdrop


SEQ, FLIGHT_RUN, FLIGHT_DROP = compute_flights()
TOTAL_DROP = -SEQ[-1]["z_bot"]                  # 6.60


def band(even):
    """Width band of a flight (world y). Even = −Y band, odd = +Y band."""
    fl = PARAMS["flights"]
    lo, hi = -fl["y_off"] - fl["half_w"], -fl["y_off"] + fl["half_w"]
    return (lo, hi) if even else (-hi, -lo)


# ===========================================================================
# [E] terrain maths
# ===========================================================================
def north_z(y):
    """Top z of the north (+Y) 30° grass slope (retaining wall top y2.60 = 0)."""
    if y <= 2.60:
        return 0.0
    return min(7.16, (y - 2.60) * NORTH_TAN)


def south_z(y):
    """Top z of the south (−Y) 30° unguarded slope (trail shoulder y−1.60 = 0)."""
    if y >= -1.60:
        return 0.0
    return max(GROUND_Z, (y + 1.60) * SOUTH_SLOPE)


def ground_z(x, y):
    """Ground z used to seat dressing."""
    if y >= 2.60:
        return north_z(y)
    if y >= 1.45:
        return 0.0                     # side retaining wall top
    if y >= -1.60:
        return TRAIL_Z if x <= HEAD_X else GROUND_Z
    if x <= HEAD_X:
        return south_z(y)
    return GROUND_Z


def _zone_z(x, y, zone):
    if zone == "north":
        return north_z(y)
    if zone == "south":
        return south_z(y)
    if zone in ("lower", "low"):
        return GROUND_Z
    if zone == "trail":
        return TRAIL_Z
    if zone == "far":
        return FAR_RIDGE_Z
    return ground_z(x, y)


# ===========================================================================
# [F] deck post layout (post bottoms must always meet the ground or the landing below)
# ===========================================================================
def post_segments():
    """List of (name, cx, cy, z_lo, z_hi) — z_hi is the underside of the slab being supported."""
    ld = PARAMS["landing"]
    ent = PARAMS["entry"]
    hy = PARAMS["post"]["half_y"]
    ins = PARAMS["post"]["inset"]
    t = ld["thick"]
    segs = []
    # support per landing : up to the landing slab underside (z_bot − thick); the bottom is the ground or the landing top below
    for f in SEQ:
        cols = [f["lx0"] + ins, f["lx1"] - ins]
        for ci, cx in enumerate(cols):
            for tag, sgn in (("P", 1.0), ("N", -1.0)):
                z_hi = f["z_bot"] - t
                # if another landing shares the same x band below, start from its top face
                below = [g["z_bot"] for g in SEQ
                         if g["k"] > f["k"] and abs(g["lx0"] - f["lx0"]) < 1e-6]
                z_lo = max(below) if below else GROUND_Z
                if z_hi - z_lo > 0.05:
                    segs.append((f"L{f['k']}_C{ci}_{tag}", cx, sgn * hy,
                                 z_lo, z_hi))
    # post at the +X end of the entry deck (rises from landing1 top −3.30 below)
    z_hi = ent["top"] - ent["thick"]
    z_lo = SEQ[1]["z_bot"]
    for tag, sgn in (("P", 1.0), ("N", -1.0)):
        segs.append((f"Entry_{tag}", ent["x1"] - ins, sgn * hy, z_lo, z_hi))
    return segs


# ===========================================================================
# [F-2] ground_kit plans - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def _plate(name):
    """Axis-aligned ground plate row: (name,x0,x1,y0,y1,z_top,thick,mtl)."""
    for row in PARAMS["plates"]:
        if row[0] == name:
            return row
    raise KeyError(f"scene10: plate '{name}' not in PARAMS['plates']")


def ground_plan():
    """Plan A - the park dirt trail (d5 / d10 near windows)."""
    g = PARAMS["gkit"]
    tp = _plate("TrailPath")
    ent = PARAMS["entry"]
    return gk.plan_ground(
        "deck_trail_hybrid",
        region=(-12.0, float(tp[3]), float(tp[2]), float(tp[4])),
        z=float(tp[5]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("deck_far_edge", float(ent["x1"]))],
        dists=(2, 5, 10), scene="scene10",
        tactile=(),                    # Sec.12.4 OFF - park, p = 0.24
        overrides=dict(
            surface=(("stain", ("dirt",)),),
            extras=(("edge_break", dict(density=12.0,
                                        lines=[float(tp[3]), float(tp[4])])),
                    ("wear_lane", dict(width=float(g["wear_w"])))),
            scatter=dict(kind="gravel", cover=0.08,
                         count=int(g["gravel_n"]),
                         scale_jitter=(0.38, 0.62), burial=0.38)),   # [W2 F2]
        seed=int(g["seed"]))


def ground_plan_deck():
    """Plan B - entry-deck plank gaps only (d2 near window).

    z is the deck top, plainly. The W2-D round had to pass
    `surface_top_z(z_deck) + 0.020` here because `build_deck_planks` put the gap
    strip's top at `z - 0.020`, i.e. **below** the deck surface, and the deck
    slab is a solid box - the burial defect the scene15 pilot measured for
    joints and manholes (rendered pixels = 0). The builder now applies
    `surface_top_z()` itself (kit defect R1, fixed 2026-07-30), so the scene-side
    lift is removed; the strips land in exactly the same place as before
    (both routes put the strip centre at deck top - 0.0094 `[calc]`).
    GT is unaffected: the strips carry `exc="plank_gap"` and the walking
    surface z does not move.
    """
    g = PARAMS["gkit"]
    ent, ld = PARAMS["entry"], PARAMS["landing"]
    z_deck = float(ent["top"])
    return gk.plan_ground(
        "deck_trail_hybrid",
        region=(float(ent["x0"]), float(ld["y0"]),
                float(ent["x1"]), float(ld["y1"])),
        z=z_deck,
        gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("deck_far_edge", float(ent["x1"]))],
        dists=(2, 5, 10), scene="scene10", tactile=(),
        overrides=dict(pave=dict(joint=None), surface=(),
                       extras=(("deck_planks",
                                dict(max_gaps=int(g["deck_gaps"]))),),
                       scatter=None),
        seed=int(g["seed"]) + 100)


# ===========================================================================
# [G] camera presets: grid_views (gy=0.0) + 5 mise-en-scene shots
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)          # h{0.3,0.9,1.8} × d{2,5,10}, +X

    l0 = SEQ[0]                          # landing0 (z −1.65, x 3.0..4.4)
    lc = ((l0["lx0"] + l0["lx1"]) / 2.0, 0.0, l0["z_bot"])
    # reversal : landing0 from the south (open side) - the flight above (+X down) and below (−X reversed) at once.
    #   [v7 verdict §7 (1)·(a)] the old shot (eye 3.70,−3.20,−0.30 / pitch −24 deg) filled the
    #   frame with masonry wall + brown timber only, so "neighbourhood park" did not read.
    #   -> **pull back 3.6 m, rise 1.5 m and lift the pitch to −16 deg**: the frame top
    #   (+2.0 deg elevation) catches the **north 30 deg grass slope and shrub clumps** past the coping,
    #   while the bottom (−34 deg) keeps landing0 and flights 0/1 (SMOKE [v7 mise-en-scene] check).
    views["reversal"] = dict(eye=[6.60, -6.60, 1.20],
                             tgt=[2.90, -0.35, -0.88])
    # through_treads : open-riser see-through - the flight below and the ground between the treads
    views["through_treads"] = dict(eye=[1.5, -2.8, -1.10],
                                   tgt=[1.7, 0.30, -4.20])
    # broken_rail : close-up of the missing-rail run at the landing0 outer edge (x 4.4) + the 4.95 m drop
    #   [v7 verdict §7 (2)] the old sight line 135 deg gave lit-face normal 315 deg -> lambert +0.273,
    #   putting the broken and the intact railing in the same dark band. Rotating 0.7 m toward
    #   the south (open side) gives sight 111.9 deg (normal 291.9 deg) -> **+0.480**. The frame
    #   bottom (−38.5 deg) passes through the vertical space under landing0 and lands on the wall
    #   face at z −4.46 -> **the depth of the 4.95 m drop itself stays in frame** (SMOKE bottom-ray landing).
    views["broken_rail"] = dict(eye=[5.60, -3.40, -0.30],
                                tgt=[4.35, -0.30, -1.55])
    # leaf_edge : leaves hiding the top two steps - close to the approaching robot's viewpoint
    views["leaf_edge"] = dict(eye=[-1.05, -1.55, 0.55],
                              tgt=[0.80, -0.70, -0.38])
    # from_below : the whole switchback from the lower park (landings·posts·drop anchors)
    #   [v7 verdict §7 (2)·(b)] the old shot (eye 8.0,−7.5 -> tgt 1.8,0) had sight azimuth 129.6 deg,
    #   so **half the subject was the +X-facing cut face and head wall** (lambert −0.342 = shaded side)
    #   -> mean 36.4 · dark 66.3 %. At sun az 250 the front-lit faces are the −Y ones (0.607),
    #   so the shot is **mirrored to the open side (−Y)** and looks up at the deck from due south.
    #   sight 105.4 deg · lit-face normal 285.4 deg -> lambert +0.526.
    #   pitch +6.6 deg is the value that puts "the lower park grass, dirt trail and shrubs in the
    #   bottom half, the deck stack in the top half" (the former at 7.5~10.6 m, the latter at +18.7 deg elevation).
    views["from_below"] = dict(eye=[5.20, -10.80, GROUND_Z + 1.55],
                               tgt=[2.40, -0.60, -3.85])
    return views


# ===========================================================================
# [H] SMOKE - geometry self-check without booting
# ===========================================================================
def _grid_obstacles():
    """AABBs for checking grid camera (−d, 0, h) collisions [(name,x0,x1,y0,y1,z0,z1)]."""
    sp = PARAMS["signpost"]
    bn = PARAMS["bench"]
    # [v5.2 user] arbitrary warning sign removed - Sign AABB deleted (waymarker and bench only)
    obs = [("SignPost", sp["cx"] - sp["arm"][0], sp["cx"] + sp["arm"][0],
            sp["cy"] - 0.4, sp["cy"] + 0.4, 0.0, sp["post_h"]),
           ("Bench", bn["cx"] - 0.95, bn["cx"] + 0.95, bn["cy"] - 0.25,
            bn["cy"] + 0.25, 0.0, 0.50)]
    for cx, cy, zone, th in PARAMS["trees"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Tree_{len(obs)}", cx - 0.9, cx + 0.9, cy - 0.9, cy + 0.9,
                    gz, gz + th + 1.4))
    for cx, cy, zone in PARAMS["shrubs"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Shrub_{len(obs)}", cx - 1.3, cx + 1.3, cy - 1.1,
                    cy + 1.1, gz, gz + 0.65))
    return obs


def _smoke_report():
    P = PARAMS
    fl = P["flights"]
    ld = P["landing"]
    ent = P["entry"]
    print("=" * 74)
    print("scene10_park_deck_switchback (v5 R5) — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 74)
    print(f"  플라이트 {fl['n']} × {fl['steps']}단 · riser {fl['riser']} / "
          f"tread {fl['tread']} · 폭 {2*fl['half_w']:.2f} m")
    print(f"  총 낙차 {TOTAL_DROP:.2f} m (≥0.3 → "
          f"{'OK' if TOTAL_DROP >= 0.3 else 'FAIL'}) · "
          f"플라이트 경사 {math.degrees(math.atan2(fl['riser'], fl['tread'])):.1f}°"
          f" · 평면 x [{SEQ[1]['lx0']:.2f}, {SEQ[0]['lx1']:.2f}]")

    # ── flight and landing table ──
    print("\n  [표] 플라이트/참 (월드 좌표)")
    print(f"    {'k':>2} {'rot':>4} {'대역 y':>16} {'x_top→x_bot':>14} "
          f"{'z_top→z_bot':>16} {'참 x범위':>14} 참 z")
    for f in SEQ:
        lo, hi = band(f["even"])
        print(f"    {f['k']:2d} {int(f['rot']):4d} [{lo:+6.2f},{hi:+6.2f}] "
              f"{f['x_top']:6.2f}→{f['x_bot']:6.2f} "
              f"{f['z_top']:+7.3f}→{f['z_bot']:+7.3f} "
              f"[{f['lx0']:6.2f},{f['lx1']:6.2f}] {f['z_bot']:+7.3f}")
    lo_e, hi_e = band(True)
    lo_o, hi_o = band(False)
    print(f"    대역 간극 = {lo_o - hi_e:.3f} m (>0 = 두 방향 간섭 0 → "
          f"{'OK' if lo_o > hi_e else 'FAIL'})")
    print(f"    참 y범위 [{ld['y0']:+.2f},{ld['y1']:+.2f}] 이 두 대역을 모두 "
          f"덮는가 → {'OK' if ld['y0'] <= lo_e and ld['y1'] >= hi_o else 'FAIL'}")
    head = 2 * FLIGHT_DROP - 0.29
    print(f"    상·하 플라이트 연직 여유 = 2×{FLIGHT_DROP:.2f} − 0.29 = "
          f"{head:.2f} m ({'OK' if head > 2.0 else 'CHECK'})")

    # ── exhaustive walking continuity check ──
    print("\n  [표] 보행 연속성 (구간 → 다음 구간, n단 분할 단차)")
    links = [("상부 트레일", TRAIL_Z, "진입 데크", ent["top"], 1)]
    prev_n, prev_z = "진입 데크", ent["top"]
    for f in SEQ:
        z1 = f["z_top"] - fl["riser"]
        links.append((prev_n, prev_z, f"플라이트{f['k']} 1단", z1, 1))
        links.append((f"플라이트{f['k']} 1단", z1,
                      f"플라이트{f['k']} {fl['steps']}단", f["z_bot"],
                      fl["steps"] - 1))
        links.append((f"플라이트{f['k']} {fl['steps']}단", f["z_bot"],
                      f"참{f['k']}", f["z_bot"], 1))
        prev_n, prev_z = f"참{f['k']}", f["z_bot"]
    links.append((prev_n, prev_z, "하부 산책로", GROUND_Z, 1))
    worst = 0.0
    for n0, z0, n1, z1, ns in links:
        d = (z0 - z1) / float(ns)
        worst = max(worst, abs(d))
        flag = "OK" if abs(d) <= fl["riser"] + 1e-6 else "CHECK"
        print(f"    {n0:<15} {z0:+7.3f} → {n1:<15} {z1:+7.3f} "
              f"×{ns:2d}단  단차 {d:+6.3f}  {flag}")
    print(f"    최대 단일 단차 {worst:.3f} m (riser {fl['riser']} 이하 = "
          f"{'OK' if worst <= fl['riser'] + 1e-6 else 'CHECK'})")
    gap = SEQ[-1]["z_bot"] - GROUND_Z
    print(f"    참3 상면 {SEQ[-1]['z_bot']:+.3f} vs 하부 지면 {GROUND_Z:+.3f} "
          f"→ 프라우드 {gap:+.3f} m "
          f"({'OK (동일평면 아님·보행 무해)' if 0.0 < gap <= 0.05 else 'CHECK'})")

    # ── ground plate / slope table ──
    print("\n  [표] 축정렬 지면 플레이트")
    print(f"    {'이름':15s} {'x범위':>16s} {'y범위':>16s} {'상면z':>7s} 두께")
    for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]:
        print(f"    {nm:15s} [{x0:7.1f},{x1:7.1f}] [{y0:7.2f},{y1:7.2f}] "
              f"{zt:7.3f} {th:5.2f}")
    print("  [표] Y 방향 사면(_ybank, rotX)")
    for nm, x0, x1, yh, zh, yl, zl, th, _m in P["ybanks"]:
        ang = math.degrees(math.atan2(zh - zl, yh - yl))
        print(f"    {nm:15s} y {yh:+6.2f}(z{zh:+6.2f}) → {yl:+6.2f}"
              f"(z{zl:+6.2f})  {ang:5.1f}° 두께 {th:.2f}")
    print("    상부 트레일 플레이트는 x=%.1f 에서 끊김 → 계단 공동(x %.1f..%.1f) "
          "위 연속 평면 없음 (체크리스트 ③ OK)"
          % (HEAD_X, SEQ[1]["lx0"], SEQ[0]["lx1"]))
    for y in (4.0, 2.0, 0.0, -3.0, -8.0, -14.0):
        print(f"    ground_z(x=−5, y={y:+6.1f}) = {ground_z(-5.0, y):+6.3f} · "
              f"(x=+2, y={y:+6.1f}) = {ground_z(2.0, y):+6.3f}")
    print(f"    남측 무방호: 트레일 어깨(y−1.60) 기준 y−5.6 에서 "
          f"{-south_z(-5.6):.2f} m 하강 (브리프 2~3 m 대역)")

    # ── deck post grounding table ──
    print("\n  [표] 데크 기둥 접지 (하단 z / 상단 z / 길이)")
    for nm, cx, cy, z_lo, z_hi in post_segments():
        base = "지면" if abs(z_lo - GROUND_Z) < 1e-6 else "하부 참"
        print(f"    {nm:<12} ({cx:6.2f},{cy:+5.2f}) {z_lo:+7.3f} → "
              f"{z_hi:+7.3f}  L={z_hi - z_lo:5.3f}  하단={base}")

    # ── broken railing ──
    br = P["rail"]["broken_landing"]
    f = SEQ[br]
    print(f"\n  [파손 난간] 참{br} 외측 에지 x={f['lx1'] if f['even'] else f['lx0']:.2f}"
          f" z={f['z_bot']:+.2f} — 가로대 2본 탈락 · 포스트 잔존")
    print(f"    개방 낙차 = {f['z_bot'] - GROUND_Z:.2f} m "
          f"(≥0.3 → {'OK' if f['z_bot'] - GROUND_Z >= 0.3 else 'FAIL'})")

    # ── [v6] sun reselection check : lambert per face + direct sun reaching the passage ──
    az = 33.5 + float(P["SUN_AZ_OFFSET"])
    el = math.radians(float(P["light"]["noon_sun_elev"]))
    ux, uy = math.cos(math.radians(az)), math.sin(math.radians(az))
    lx, ly, lz = ux * math.cos(el), uy * math.cos(el), math.sin(el)
    hv = math.cos(el) / math.sin(el)          # horizontal travel per 1 m of rise
    print(f"\n  [v6 태양] offset {P['SUN_AZ_OFFSET']:.1f} → 월드 az {az:.1f}° "
          f"(그림자 az {az - 180:.1f}°) · 고도 {math.degrees(el):.2f}°")
    for nm, N in (("−Y향(데크 측면·북측 옹벽면)", (0, -1, 0)),
                  ("−X향(그리드 정면·원경 능선)", (-1, 0, 0)),
                  ("상면(트레일·참·디딤판)", (0, 0, 1)),
                  ("+X향(머리 옹벽 노출면)", (1, 0, 0))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<26} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    print("    [광선 역추적] 통로 대표점 → 태양 방향으로 z=0 까지 상승했을 때의 "
          "평면 위치 (x<−1.5 이면 머리 옹벽/남측 사면에 차폐)")
    for nm, px, py, pz in (("플라이트0 중단", 1.5, -0.7, -0.83),
                           ("참0 상면", 3.70, -0.70, -1.65),
                           ("플라이트2 중단", 1.7, -0.7, -4.24),
                           ("참2 상면", 3.70, -0.70, -4.95),
                           ("참3 상면(최하부)", -0.70, 0.70, -6.60)):
        rise = -pz
        ex, ey = px + ux * hv * rise, py + uy * hv * rise   # trace back toward the sun
        ok = ex >= HEAD_X            # conservative test (crossing the x=−1.5 plane means possible occlusion)
        print(f"    {nm:<16} ({px:+.2f},{py:+.2f},{pz:+.2f}) → "
              f"({ex:+.2f},{ey:+.2f}, 0.00)  "
              f"{'직사광 도달' if ok else '옹벽 그늘(설계상 허용)'}")

    # ── [v6] two-tier retaining wall consistency check ──
    tiers = {nm: (x0, x1, y0, y1, zt, th)
             for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]
             if nm in ("BankCut", "EastTierLow", "EastTierUp")}
    bc, tl, tu = tiers["BankCut"], tiers["EastTierLow"], tiers["EastTierUp"]
    print(f"\n  [v6 옹벽] 단일벽 x ≤ {bc[1]:.2f}(데크 구간 — 위험 기하 불변) / "
          f"동측 2단 x ≥ {tl[0]:.2f}")
    print(f"    하단벽 상면(소단) z {tl[4]:+.2f} · 노출고 "
          f"{tl[4] - GROUND_Z:.2f} m · 상단벽 노출고 {0.0 - tl[4]:.2f} m "
          f"(구 단일 {0.0 - GROUND_Z:.2f} m → "
          f"{'OK' if max(tl[4] - GROUND_Z, -tl[4]) < 4.0 else 'CHECK'})")
    print(f"    소단 폭 {tu[2] - tl[2]:.2f} m · 접합 연속(하단벽 상면 y "
          f"{tl[2]:.2f}~{tl[3]:.2f}, 상단벽 저면 z {tu[4] - tu[5]:+.2f} ≤ "
          f"{tl[4]:+.2f} → "
          f"{'OK' if tu[4] - tu[5] <= tl[4] + 1e-9 else 'FAIL'})")
    bm = P["berm"]
    print(f"    소단 식재 {len(P['berm_hedges'])}띠 y[{bm['y0']:.2f},"
          f"{bm['y1']:.2f}] ⊂ 소단 y[{tl[2]:.2f},{tl[3]:.2f}] → "
          f"{'OK' if bm['y0'] >= tl[2] and bm['y1'] <= tl[3] else 'FAIL'}")

    # ── grid camera collision check ──
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
    print(f"    충돌 = {hit_any} (False 여야 함) · 카메라 접지면 z=0 "
          f"(UpperTrail x −40..{HEAD_X}, y −1.60..1.45) 내부 OK")

    print("\n  [카메라] 미장센")
    v = build_views()
    for vn in ("reversal", "through_treads", "broken_rail", "leaf_edge",
               "from_below"):
        vv = v[vn]
        print(f"    {vn:<15} eye={['%.2f' % e for e in vv['eye']]} "
              f"tgt={['%.2f' % t for t in vv['tgt']]}")

    # ── [v7] mise-en-scene framing : are the park anchors in frame + front lighting per shot ──
    #   verdict §7 (1) "none of the 4 mise-en-scene shots carries a park signal (grass·shrubs·
    #   trees·visitor furniture) - the problem is framing, not geometry". To **verify the
    #   re-aim by coordinates**, the park anchors inside the FOV (horizontal half 30 deg ·
    #   vertical half 18 deg) are enumerated, with the lit-face lambert per shot attached
    #   (judge v7 lesson: "a re-aim is checked by frame coverage, illumination is not").
    anchors = []
    for cx, cy, zone in P["shrubs"]:
        if zone in ("lower", "south"):
            anchors.append((f"관목({cx:+.1f},{cy:+.1f})", cx, cy,
                            _zone_z(cx, cy, zone) + 0.55))
    for cx, cy, zone, th in P["trees"]:
        anchors.append((f"수목({cx:+.1f},{cy:+.1f})", cx, cy,
                        _zone_z(cx, cy, zone) + th + 0.7))
    pg = P["pergola"]
    anchors.append(("쉼터 정자", (pg["x0"] + pg["x1"]) / 2.0,
                    (pg["y0"] + pg["y1"]) / 2.0, pg["z_roof"]))
    for yy in (4.0, 7.0, 11.0):
        anchors.append((f"북측 잔디사면 y{yy:.0f}", 3.0, yy, north_z(yy)))
    bm = P["berm"]
    for x0b, x1b in P["berm_hedges"][:1]:
        anchors.append(("소단 식재띠", (x0b + x1b) / 2.0,
                        (bm["y0"] + bm["y1"]) / 2.0,
                        bm["base_z"] + bm["h"] / 2.0))
    sp, bn = P["signpost"], P["bench"]
    anchors.append(("이정표", sp["cx"], sp["cy"], sp["post_h"] / 2.0))
    anchors.append(("벤치", bn["cx"], bn["cy"], 0.25))

    azd = 33.5 + float(P["SUN_AZ_OFFSET"])
    el2 = math.radians(float(P["light"]["noon_sun_elev"]))
    print("\n  [v7 미장센] 컷별 피사면 lambert + 프레임 내 공원 앵커")
    for vn in ("reversal", "through_treads", "broken_rail", "leaf_edge",
               "from_below"):
        ex, ey, ez = v[vn]["eye"]
        tx, ty, tz = v[vn]["tgt"]
        fx, fy = tx - ex, ty - ey
        dh = math.hypot(fx, fy)
        ux, uy = fx / dh, fy / dh
        rx, ry = uy, -ux
        gaze = math.degrees(math.atan2(fy, fx)) % 360.0
        nrm = (gaze + 180.0) % 360.0
        lam = math.cos(math.radians(nrm - azd)) * math.cos(el2)
        pit = math.degrees(math.atan2(tz - ez, dh))
        seen = []
        for nm, ax, ay, az_ in anchors:
            vx, vy, vz = ax - ex, ay - ey, az_ - ez
            dep = vx * ux + vy * uy
            if dep <= 0.5:
                continue
            yaw = math.degrees(math.atan2(vx * rx + vy * ry, dep))
            elv = math.degrees(math.atan2(vz, math.hypot(vx, vy)))
            if abs(yaw) <= 30.0 and abs(elv - pit) <= 18.0:
                seen.append(f"{nm}[yaw{yaw:+.0f}°]")
        # the ground hit by the bottom-centre ray (is the lower half grass / dirt trail)
        pr = math.radians(pit - 18.0)
        hit = None
        for i in range(1, 401):
            s = i * 0.25
            px, py = ex + ux * s * math.cos(pr), ey + uy * s * math.cos(pr)
            pz = ez + s * math.sin(pr)
            if pz <= ground_z(px, py):
                zone = ("하부공원 흙길" if (px > HEAD_X and -4.4 <= py <= -2.6)
                        else ("하부공원 잔디" if (px > HEAD_X and py < 1.45)
                              else "상부/사면"))
                hit = f"({px:+.1f},{py:+.1f}) {zone}"
                break
        print(f"    {vn:<15} 시선 {gaze:5.1f}° · 법선 {nrm:5.1f}° · lambert "
              f"{lam:+.3f} {'순광' if lam > 0.15 else '역광/터미네이터'} · "
              f"피치 {pit:+5.1f}°")
        print(f"      하단 시선 착지 : {hit if hit else '지면 미교차(하늘)'}")
        # verdict §7 (1) said "**every** mise-en-scene shot lacks a park signal".
        #   the re-aimed shots (from_below·reversal) must catch an anchor, while the
        #   close-ups (through_treads·broken_rail) are exempt - instead their illumination
        #   and drop are checked by lambert and the bottom-ray landing point.
        need = vn in ("from_below", "reversal")
        verdict = ("OK" if seen else "FAIL ← 판정 §7 ① 재발") if need \
            else ("OK" if seen else "면제(클로즈업 — lambert·하단 착지로 판정)")
        print(f"      공원 앵커 {len(seen)}개 [{verdict}] : "
              f"{', '.join(seen) if seen else '-'}")
    print("=" * 74)


# ===========================================================================
# [I] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 낙엽 덮인 상단 2단이 '평탄한 데크 진입'으로 읽히나
 2. through_treads   — 라이저 부재로 디딤판 사이 아래 플라이트·지면이 투시되나
 3. reversal         — 참0에서 두 방향 플라이트(±X, 병렬 Y 대역)가 한 프레임에
 4. broken_rail      — 가로대 탈락·포스트 잔존 + 4.97 m 개방 낙차가 명확한가
 5. leaf_edge        — 낙엽 밴드가 단코를 물고 덮어 절단선을 지우나
 6. from_below       — 데크 기둥 접지·참 스택이 낙차 앵커로 읽히나
 7. 남측 사면        — 트레일 어깨 밖 30° 무방호 하강이 grazing 시 소실되나
 8. 지평 폐쇄        — 북측 언덕·원경 능선 마루 숲 밴드가 직선 지평을 깨는가
 9. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가
10. [v6] 태양        — from_below·through_treads 에 직사광이 들어왔나(암부 사망 해소)
11. [v6] 옹벽        — 사석 스케일 + 동측 2단(소단 식재)로 '공원 절토면'이 되나
12. [v6] 난간        — 세로살이 들어가 '가설 사다리틀'이 아니라 데크 난간인가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene10")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene10"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl, rotY=rotY,
                               collider=col)

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        M["deck"] = tex("wood_dark", "/World/Looks/Deck", sca["wood_dark"],
                        tint=mp["deck_tint"])
        M["stringer"] = tex("wood_dark", "/World/Looks/Stringer",
                            sca["wood_dark"] * 1.6, tint=mp["stringer_tint"])
        # [v6] built retaining wall (masonry, rubble scale) / natural cut face (jointless) / coping (concrete)
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"],
                        tint=mp["rock_tint"])
        M["rockface"] = tex("rock_face", "/World/Looks/RockFace",
                            sca["rock_face"], tint=mp["rockface_tint"])
        M["coping"] = tex("concrete_wall", "/World/Looks/Coping",
                          sca["concrete_wall"], tint=mp["coping_tint"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["leaf"] = tex("leaf_ground", "/World/Looks/Leaf",
                        sca["leaf_ground"], tint=mp["leaf_tint"])
        M["dirt"] = tex("dirt_park", "/World/Looks/Dirt", sca["dirt_park"],
                        tint=mp["dirt_tint"])
        # [W2-D ground_kit] tone materials for kit ground elements.
        #   gk_wear: the trodden axis is defined as albedo x0.85 of the trail,
        #   so it must not be bound to the plain dirt material or it renders a
        #   zero-contrast null. gk_gap: a plank gap reads as a dark line, and
        #   with recess-as-tone the line *is* the material.
        M["gk_wear"] = tex("dirt_park", "/World/Looks/GkWear", sca["dirt_park"],
                           tint=tuple(c * 0.85 for c in mp["dirt_tint"]))
        # [W2 fix batch F2] Scatter pool override. Bound over each scattered rock
        #   with `strongerThanDescendants`, so the procured asset's own basecolor
        #   (linear 0.23) is replaced by a real gravel texture dulled to 0.19 -
        #   the middle of the "grey debris 0.18~0.30" convention.
        M["gk_rock"] = tex("gravel", "/World/Looks/GkRock", 0.30,
                           tint=(0.82, 0.81, 0.79))
        M["gk_gap"] = sc.make_pbr(stage, "/World/Looks/GkGap",
                                  diffuse_color=(0.028, 0.024, 0.020),
                                  roughness_const=0.95, specular_level=0.0)
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["shrub"] = sc.make_pbr(stage, "/World/Looks/Shrub",
                                 diffuse_color=mp["shrub"],
                                 roughness_const=mp["shrub_rough"],
                                 specular_level=0.0)
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        # [v5.2 user] arbitrary warning sign removed - sign panel and backing material creation deleted.
        M["tread"] = M["deck"] if cfg["cue_material_break"] else M["stringer"]
        return M

    # -------------------------------------------------------------------
    # terrain : axis-aligned plates + Y-direction slopes (rotX slabs)
    # -------------------------------------------------------------------
    def ybank(path, x0, x1, y_hi, z_hi, y_lo, z_lo, thick, mtl):
        """Slope slab tilting from +Y (high) → −Y (low). The Y counterpart of build_slope.
        rotX(θ): local +Y → (0, cosθ, sinθ), so θ>0 descends toward −Y.
        Local −Z (the thickness direction) → world (0, sinθ, −cosθ)."""
        dy, dz = (y_hi - y_lo), (z_hi - z_lo)
        ang = math.atan2(dz, dy)
        L = math.hypot(dy, dz)
        cy = (y_hi + y_lo) / 2.0 + (thick / 2.0) * math.sin(ang)
        cz = (z_hi + z_lo) / 2.0 - (thick / 2.0) * math.cos(ang)
        return sc._oriented_box(stage, path, ((x0 + x1) / 2.0, cy, cz),
                                (x1 - x0, L, thick), mtl, collider=True,
                                rotx=math.degrees(ang))

    def build_terrain(M):
        # [W2-0 P-A] TrailPath is what plan A decorates. It is 1.70 m wide so
        #   `_skin_wanted` already rejects it (needs >= 4.0 m on both axes),
        #   but the registration is explicit so the guarantee does not depend
        #   on a width that a later edit could change. Same for the entry deck
        #   (also covered by the "deck" token in `_SKIN_DENY`).
        sc.skin_exclude(f"{ROOT}/Plate_TrailPath", f"{ROOT}/EntryDeck")
        for nm, x0, x1, y0, y1, zt, th, mk in PARAMS["plates"]:
            BOX(f"{ROOT}/Plate_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M[mk], col=True)
        for nm, x0, x1, yh, zh, yl, zl, th, mk in PARAMS["ybanks"]:
            ybank(f"{ROOT}/Bank_{nm}", x0, x1, yh, zh, yl, zl, th, M[mk])
        # [v6] retaining wall coping - projects past the wall face to make a shadow line at the top
        for nm, x0, x1, y0, y1, zt, th in PARAMS["copings"]:
            BOX(f"{ROOT}/Coping_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M["coping"], col=True)
        # [v6] planting band on the east two-tier wall berm (z −3.30) - dispels the 'fortress' impression
        bm = PARAMS["berm"]
        for i, (x0, x1) in enumerate(PARAMS["berm_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BermHedge_{i}", x0, bm["y0"],
                           x1, bm["y1"], bm["h"], base_z=bm["base_z"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P18 deck_trail_hybrid (two plans, two z levels).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(stain_dirt=M["leaf"], wear=M["gk_wear"],
                  edge_break=M["leaf"], litter=M["leaf"], deck=M["gk_gap"],
                  debris=M["gk_rock"])
        a = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                            skin_exclude=sc.skin_exclude,
                            scatter=sc.scatter_debris)
        b = gk.apply_ground(kit, f"{ROOT}/GKitDeck", ground_plan_deck(), M2,
                            skin_exclude=sc.skin_exclude)
        # 10-2 - break the straight outline the 3 stacked leaf decals still
        #   leave behind (dE76 27.3, the strongest boundary Sec.13.3 found).
        #   `scatter_debris(edge_bias=...)` skips 65 % of the interior, so the
        #   debris lands on the outline instead of filling the rectangle.
        g = PARAMS["gkit"]
        tp = _plate("TrailPath")
        pad = float(g["leaf_ring_pad"])
        ring = 0
        for i, (cx, cy, sx, sy, zone) in enumerate(
                PARAMS["leaf_ground_patches"]):
            if zone != "trail":
                continue
            ring += int(sc.scatter_debris(
                stage, f"{ROOT}/GKit/LeafRing_{i}",
                cx - sx / 2.0 - pad, cy - sy / 2.0 - pad,
                cx + sx / 2.0 + pad, cy + sy / 2.0 + pad, float(tp[5]),
                cover=0.10, seed=gk.det_seed("scene10.leafring", i),
                edge_bias=pad,
                max_count=int(g["leaf_ring_n"])) or 0)
        print(f"[ground_kit] scene10 P18 · 프림 {a['prims']}+{b['prims']} · "
              f"산포 {a['instances']}+{ring} · δmax {a['gt_delta_max']:.4f} · "
              f"unit_cell {a['unit_cell']}")
        return a

    def build_flat_fill(M):
        """hazard_stairs=False control : the stair run becomes a flat z=0 deck."""
        ld = PARAMS["landing"]
        x0, x1 = SEQ[1]["lx0"], SEQ[0]["lx1"]
        BOX(f"{ROOT}/FlatDeck",
            ((x0 + x1) / 2.0, (ld["y0"] + ld["y1"]) / 2.0, -0.06),
            (x1 - x0, ld["y1"] - ld["y0"], 0.12), M["deck"], col=True)

    # -------------------------------------------------------------------
    # switchback deck stair
    # -------------------------------------------------------------------
    def deck_rail(prefix, x0, x1, y0, y1, z_top, broken=False):
        """One axis-aligned railing run (posts + top/mid rails + **vertical bars**).
        broken=True → rails and bars gone, only the posts remain (the landing0 break).
        The hazard geometry is unchanged."""
        r = PARAMS["rail"]
        horiz = abs(x1 - x0) >= abs(y1 - y0)
        L = math.hypot(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        if not broken:
            for tag, hh, rr in (("Top", r["h"], r["bar_t"]),
                                ("Mid", r["mid"], r["bar_t"] * 0.7)):
                size = ((L, rr, rr) if horiz else (rr, L, rr))
                BOX(f"{prefix}/Bar{tag}", (cx, cy, z_top + hh), size,
                    M["rail"])
            # [v6] vertical bars : standard for park deck railings. Up to the underside of the top rail.
            nb = max(1, int(round(L / r["bal_step"])) - 1)
            for i in range(nb):
                t = (i + 1) / float(nb + 1)
                bx = x0 + (x1 - x0) * t
                by = y0 + (y1 - y0) * t
                CYL(f"{prefix}/Bal_{i}", (bx, by, z_top + r["bal_top"] / 2.0),
                    r["bal_r"], r["bal_top"], M["rail"])
        n = max(2, int(round(L / r["spacing"])) + 1)
        for i in range(n):
            t = i / float(n - 1)
            px = x0 + (x1 - x0) * t
            py = y0 + (y1 - y0) * t
            CYL(f"{prefix}/Post_{i}", (px, py, z_top + r["post_h"] / 2.0),
                r["post_r"], r["post_h"], M["rail"])

    def build_deck(M):
        fl = PARAMS["flights"]
        ld = PARAMS["landing"]
        ent = PARAMS["entry"]
        r = PARAMS["rail"]
        lcy = (ld["y0"] + ld["y1"]) / 2.0
        lsy = ld["y1"] - ld["y0"]

        def _flight_rails(grp, f, gy0, gy1):
            """Railings on both sides of a flight — **inside** the rot_group (local +X descent convention).
            They stand 0.04 in from the band edge: at the centre (the even/odd band
            boundary) the inner posts of the two flights (r 0.05) merely meet at
            y=−0.05 / +0.05 and do not interpenetrate."""
            def gfn(x, _xt=f["x_top"], _zt=f["z_top"]):
                if x <= _xt:
                    return _zt
                i = min(int((x - _xt) / fl["tread"]) + 1, fl["steps"])
                return _zt - i * fl["riser"]

            for tag, y in (("N", gy0 + 0.04), ("P", gy1 - 0.04)):
                sc.build_railing_line(
                    stage, f"{grp}/Rail_{tag}", y, f["x_top"], f["x_top"],
                    FLIGHT_RUN, FLIGHT_DROP, gfn, M["rail"], rail_h=r["h"],
                    post_r=r["post_r"], spacing=r["spacing"],
                    rail_r=r["bar_t"] / 2.0,
                    # this scene has **its own vertical-bar loop below**. Turning on the shared
                    # balusters would duplicate the cylinders and interpenetrate (red team found 48 pairs).
                    baluster_r=0.0)
                # [v6] vertical bars on the raking railing : tread face -> top rail. Without them
                #      the two raking rails overlap behind the neighbouring frame and are misread
                #      as 'diagonal bracing' (verdict §4 (5), temporary ladder frame).
                top0 = f["z_top"] + r["h"]
                nb = max(1, int(round(FLIGHT_RUN / r["bal_step"])) - 1)
                for i in range(nb):
                    bx = f["x_top"] + FLIGHT_RUN * (i + 1) / float(nb + 1)
                    zr = top0 - FLIGHT_DROP * (bx - f["x_top"]) / FLIGHT_RUN
                    zg = gfn(bx)
                    hh = zr - zg - r["bar_t"] / 2.0
                    if hh > 0.05:
                        CYL(f"{grp}/Bal_{tag}_{i}", (bx, y, zg + hh / 2.0),
                            r["bal_r"], hh, M["rail"])

        # entry deck (retaining wall head -> first step)
        BOX(f"{ROOT}/EntryDeck",
            ((ent["x0"] + ent["x1"]) / 2.0, lcy, ent["top"] - ent["thick"] / 2.0),
            (ent["x1"] - ent["x0"], lsy, ent["thick"]), M["deck"], col=True)

        for f in SEQ:
            k = f["k"]
            lo, hi = band(True)              # local band (even convention) - rot180 mirrors it
            grp = sc.build_rot_group(stage, f"{ROOT}/FlightGrp_{k}",
                                     (f["x_top"], 0.0), f["rot"])
            sc.build_open_riser_stairs(
                stage, f"{grp}/Flight", f["x_top"], lo, hi, fl["riser"],
                fl["tread"], fl["steps"], f["z_top"], M["tread"],
                M["stringer"], tread_t=fl["tread_t"], gap=fl["gap"])
            if cfg["cue_railing"]:
                _flight_rails(grp, f, lo, hi)
            # landing (world coordinates) - slab covering both bands
            BOX(f"{ROOT}/Landing_{k}",
                ((f["lx0"] + f["lx1"]) / 2.0, lcy,
                 f["z_bot"] - ld["thick"] / 2.0),
                (f["lx1"] - f["lx0"], lsy, ld["thick"]), M["deck"], col=True)

        # deck posts (all grounded on the ground or on the landing below)
        pp = PARAMS["post"]
        for nm, cx, cy, z_lo, z_hi in post_segments():
            h = z_hi - z_lo
            CYL(f"{ROOT}/Post_{nm}", (cx, cy, z_lo + h / 2.0), pp["r"], h,
                M["stringer"], col=True)

        # landing railing : outer edge + both sides. Only the landing0 outer run is **broken** (rails gone).
        if cfg["cue_railing"]:
            for f in SEQ:
                k = f["k"]
                z = f["z_bot"]
                x_out = f["lx1"] if f["even"] else f["lx0"]
                broken = (k == int(r["broken_landing"]))
                deck_rail(f"{ROOT}/LandRail_{k}_Out", x_out, x_out, ld["y0"],
                          ld["y1"], z, broken=broken)
                for tag, yy in (("N", ld["y0"]), ("P", ld["y1"])):
                    deck_rail(f"{ROOT}/LandRail_{k}_{tag}", f["lx0"], f["lx1"],
                              yy, yy, z)
            # 2 side railings on the entry deck
            for tag, yy in (("N", ld["y0"]), ("P", ld["y1"])):
                deck_rail(f"{ROOT}/EntryRail_{tag}", ent["x0"], ent["x1"],
                          yy, yy, ent["top"])

        # leaf band : hides the top two step edges of flight0
        lf = PARAMS["leaf"]
        f0 = SEQ[0]
        blo, bhi = band(True)
        for i in (1, 2):
            xa = f0["x_top"] + (i - 1) * fl["tread"]
            xb = f0["x_top"] + i * fl["tread"]
            zt = f0["z_top"] - i * fl["riser"] + lf["proud"]
            cx = (xa + 0.06 + xb + lf["over"]) / 2.0
            sx = (xb + lf["over"]) - (xa + 0.06)
            BOX(f"{ROOT}/LeafTread_{i}", (cx, (blo + bhi) / 2.0,
                                          zt - lf["thick"] / 2.0),
                (sx, bhi - blo, lf["thick"]), M["leaf"])
        # 4 ground leaf drifts - [v6 C-7] square decal -> 3 rotated overlays break the boundary
        lp = PARAMS["leaf_patch"]
        rng = random.Random(int(lp["seed"]))
        for n, (cx, cy, sx, sy, zone) in enumerate(
                PARAMS["leaf_ground_patches"]):
            zt = _zone_z(cx, cy, zone) + lf["proud"]
            for j in range(int(lp["subs"])):
                f = 1.0 if j == 0 else rng.uniform(*lp["scale"])
                ox = 0.0 if j == 0 else rng.uniform(-1.0, 1.0) * lp["off"] * sx
                oy = 0.0 if j == 0 else rng.uniform(-1.0, 1.0) * lp["off"] * sy
                sc._oriented_box(
                    stage, f"{ROOT}/LeafGround_{n}_{j}",
                    (cx + ox, cy + oy, zt - lf["thick"] / 2.0 - j * 0.002),
                    (sx * f, sy * f * rng.uniform(0.85, 1.15), lf["thick"]),
                    M["leaf"], collider=False,
                    rotz=rng.uniform(-lp["rz"], lp["rz"]))

    # -------------------------------------------------------------------
    # dressing
    # -------------------------------------------------------------------
    def build_nature(M):
        tr = PARAMS["tree"]
        for n, (cx, cy, zone, th) in enumerate(PARAMS["trees"]):
            gz = _zone_z(cx, cy, zone)
            sc.build_tree(stage, f"{ROOT}/Tree_{n}", cx, cy, gz, M["wood"],
                          M["canopy_a"], M["canopy_b"], trunk_r=tr["trunk_r"],
                          trunk_h=th, stake_r=0.004, stake_h=0.02,
                          stake_off=0.2)
        # [v6] a blob grounded by its centre z on a 30 deg slope floats ry·tan30 (~0.35 m) downhill
        #      -> ground it on the **lowest ground** in the blob footprint (structurally removes floating).
        sh = PARAMS["shrub"]
        emb = sh["embed"]
        for n, (cx, cy, zone) in enumerate(PARAMS["shrubs"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(sh["blobs"]):
                bx, by = cx + dx, cy + dy
                gz = min(_zone_z(bx, by - ry, zone), _zone_z(bx, by, zone),
                         _zone_z(bx, by + ry, zone))
                sc.add_sphere(stage, f"{ROOT}/Shrub_{n}_{j}",
                              (bx, by, gz + rz * (1.0 - emb)),
                              (rx, ry, rz), M["shrub"])

    def build_props(M):
        # timber waymarker (post + 2 direction blades + cap)
        sp = PARAMS["signpost"]
        CYL(f"{ROOT}/SignPost/Post",
            (sp["cx"], sp["cy"], sp["post_h"] / 2.0), sp["post_r"],
            sp["post_h"], M["wood"], col=True)
        BOX(f"{ROOT}/SignPost/Cap",
            (sp["cx"], sp["cy"], sp["post_h"] + sp["cap"][2] / 2.0),
            sp["cap"], M["wood"])
        for k, (az, yaw) in enumerate(sp["arms"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/SignPost/Arm_{k}",
                                     (sp["cx"], sp["cy"]), yaw)
            BOX(f"{grp}/Box", (sp["cx"] + sp["arm_off"], sp["cy"], az),
                sp["arm"], M["wood"])
        # bench 1
        bn = PARAMS["bench"]
        sc.build_bench(stage, f"{ROOT}/Bench", bn["cx"], bn["cy"], 0.0,
                       M["deck"], yaw=bn["yaw"])
        # shelter pavilion (lower path)
        pg = PARAMS["pergola"]
        sc.build_canopy(stage, f"{ROOT}/Pergola", pg["x0"], pg["x1"], pg["y0"],
                        pg["y1"], pg["z_roof"], pg["post_r"], M["deck"],
                        M["stringer"], roof_t=pg["roof_t"], base_z=GROUND_Z)

    def build_horizon(M):
        for i, h in enumerate(PARAMS["far_hedges"]):
            base = ground_z((h["x0"] + h["x1"]) / 2.0,
                            (h["y0"] + h["y1"]) / 2.0)
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}", h["x0"], h["y0"],
                           h["x1"], h["y1"], h["h"], base_z=base)
        # [v6 C-4] forest band on the distant ridge crest - closed with a silhouette strip, not lollipops
        for i, h in enumerate(PARAMS["ridge_crest"]):
            sc.build_hedge(stage, f"{ROOT}/RidgeCrest_{i}", h["x0"], h["y0"],
                           h["x1"], h["y1"], h["h"], base_z=h["base"])
        # [v6 C-4] distant individuals get thicker trunks and more height to avoid 'thin stick + sphere'
        for i, t in enumerate(PARAMS["hill_trees"]):
            gz = _zone_z(t["cx"], t["cy"], t["zone"])
            sc.build_tree(stage, f"{ROOT}/HillTree_{i}", t["cx"], t["cy"], gz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.17, trunk_h=4.6 + 0.35 * (i % 4),
                          stake_r=0.004, stake_h=0.02, stake_off=0.2)

    # [v5.2 user] arbitrary warning sign removed - build_sign() deleted.

    def build_cues(M):
        """Non-standard equipment cue (code path only)."""
        if cfg["cue_tactile"]:
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, f"{ROOT}/Tactile", -2.10, -1.50,
                             PARAMS["landing"]["y0"], PARAMS["landing"]["y1"],
                             tac, z=0.0)
        if cfg["cue_nosing"]:
            fl = PARAMS["flights"]
            for f in SEQ:
                grp = sc.build_rot_group(stage, f"{ROOT}/NoseGrp_{f['k']}",
                                         (f["x_top"], 0.0), f["rot"])
                lo, hi = band(True)
                sc.build_nosing(stage, f"{grp}/Nose", f["x_top"], lo, hi,
                                fl["riser"], fl["tread"], fl["steps"],
                                base_z=f["z_bot"], z_top=f["z_top"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    M["rail"] = M["stringer"]          # timber railing (same timber as the deck)
    build_terrain(M)
    if cfg["hazard_stairs"]:
        build_deck(M)
        build_cues(M)
        build_ground_kit(M)          # [W2-D] trail + entry-deck ground elements
    else:
        build_flat_fill(M)
    build_horizon(M)
    if cfg["cue_scene_dressing"]:
        build_nature(M)
        build_props(M)
    # [v5.2 user] arbitrary warning sign removed - cue_sign placement deleted.

    print(f"[기하] 갈지자 {PARAMS['flights']['n']}플라이트 × "
          f"{PARAMS['flights']['steps']}단 총낙차 {TOTAL_DROP:.2f} "
          f"(z {SEQ[0]['z_top']:+.2f} → {SEQ[-1]['z_bot']:+.2f}) · "
          f"참0 외측 난간 파손 개방낙차 "
          f"{SEQ[0]['z_bot'] - GROUND_Z:.2f} m")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── camera + render mode ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["reversal"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene10_{ts}.png")
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
