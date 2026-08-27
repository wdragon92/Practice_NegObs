# -*- coding: utf-8 -*-
"""
scene04_parktrail.py — NegObs synthetic scene 4: park sleeper stair (T4, Isaac Sim 4.5)

Spec : Docs/briefs/multi_scene_brief_v2.md §C `scene04_parktrail` (sole spec)
Shared library : scene_common.py (verified API - ported·generalised from scene01)

Hazard (T4): an **irregular-riser sleeper stair** descending a gently sloped park bank.
  The sleeper (timber) risers + decomposed-granite (gravel) treads blend into the
  surrounding soil·leaf litter, blurring the nosing cut line. The anchor cue is the
  lower tree canopy sitting at upper eye level.

[v5.1 realism] User feedback: "trail curvature + the slope beside the stair look unnatural".
  (1) Stronger trail meander - the centreline polyline grows to 12~13 nodes, per-segment
      yaw amplitude +-20~32 deg (was +-8~12 deg) and a +-10 % width wobble remove the
      'ruled band' impression.
  (2) **Sleeper stair among grass** - the exposed dirt slope on both sides of the stair
      (old dirt band |y| 1.15~3.0) is narrowed to 1.7 and covered by a grass mound band
      (row of flattened ellipsoids) + 2 shrub rows, concealing the cut slope. The
      stair·sleeper·stake (hazard geometry) transforms are unchanged.

[v6 verdict - re-fix] The grass band of (2) rendered as a **"mossy boulder field"** (bulky
  ellipsoid x grass texture uv 1.6). -> Reworked to 3 constant tuft colours · half the size ·
  3x the count · irregular placement (spacing jitter/dropout/axis swap). Check:
  `NEGOBS_SELFCHECK=1 python scene04_parktrail.py` (stair intrusion · grounding · dirt-band
  coverage). Hazard geometry unchanged.

[W3 S04-1 · verge renovation] Target image **G4**
  (`Docs/reference_photos/Generated Image - Scene04.jpg`), law =
  `Docs/surveys/w3_intake_v2_images.md` scene04 row §2 + §7 rulings 8 / R04-1 / R04-2.
  The user's directive was *"침목길 수풀 좀 더 추가하면 나을지도?"*, and G4 redefines what
  "수풀" means here: the flanks are **a deep continuous leaf-litter floor with bare trunks and
  low tufts**, plus the **rope-on-timber-post handline** that is the actual Korean trail
  signature. They are **not** shrub domes. What changed:
   (1) The five constant-`cy` ellipsoid verge rows (121 `add_sphere` instances) and the six
       3-blob shrub clusters (18 instances) are **deleted** - `tonglam_v2` scored the scene
       FAIL on *"giant moss-green ellipsoid blobs"* and both families are that shape.
   (2) A **ground layer** replaces them: leaf-litter base material on every off-path ground
       plate, ~40 CB-2 (`ground_kit.build_blot`, DEC-1) drift lobes that follow the **walk
       centreline** instead of a constant `cy`, several hundred real 3-D leaf cards
       (`VEG_DEBRIS`), low turf tufts from the procured-unused `Grass_Short_A/B`, and
       leaf-off trunks via the `build_tree(bare=)` mechanism landed at `1346b70`.
   (3) A **rope-on-timber-post handline** along the walk (scene-local, lift-ready for
       `props_kit`). Ruling **R04-1** is binding: it is **DRESSING, NOT A GUARD** and does not
       flip this scene's negative-obstacle label. The mechanism that makes that true is not a
       promise but construction: **it is built in both hazard arms** (like the ground_kit twin
       parity), so its presence carries zero information about the label.
   (4) Season pinned **late autumn / leaf-off** (§7 ruling 8 -> R04-2), with a per-element
       seasonal audit printed by the self-check.
   (5) `04-B`: the ground_kit gravel scatter is **masked off the lawn onto the trail polygon**.
       The `G-6` deposition scatter stays **gated** and is not implemented here.
  Self-check (no boot, no GPU):
  `NEGOBS_SELFCHECK=1 python3 scene04_parktrail.py` (= `NEGOBS_SMOKE=1`).

[GT-126 · repair] (1) x=0 seam: `build_slope`'s ±0.15 margin stands every slope slab
  +0.038 (+0.058 trim) proud of the z=0 flat with an overhung end face — the "floating
  plate / open slot" band. Buried by a 2-slab crest berm per flank (non-walking side,
  colliders untouched) + a head sleeper under the landing lip (top −0.03, edge x=0/z=0
  and the walking surfaces bit-identical). (2) Lombardy_Poplar retired from the tree
  pools: its twig broom does not survive to the render at 04's scales (bare pole read).

Consistency correction (against the director's brief §C):
  riser table sum = 1.45, tread table sum = 5.55.
  -> slope drop = 1.45 (not the brief text's 0.9/−1.5 approximation), lower flat z = −1.45 throughout.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene04_parktrail.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene04_parktrail.py
      NEGOBS_CAPTURE_DIR  : output folder (default look_check/scene04/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (default rt)
      NEGOBS_VIEWS        : comma-separated view name filter (default all)

Coordinates: Z-up, m, travel axis +X, stair top edge = x=0.
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
# [A] SCENE_CONFIG - same 6 keys as scene01 + new cue_nosing.
#     Toggles other than hazard_stairs never change the hazard geometry (invariant).
#     Per the T4 identity the fitting cues (railing·tactile·anti-slip) default to False (the code paths exist).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> slope+stairs+lower flattened to z=0 (sole geometry toggle)
    "cue_railing":        False,   # True -> one log handrail line (y=+1.0, wood_dark cylinder r0.05 + wooden posts)
    "cue_tactile":        False,   # True -> tactile paving strip at the top edge (unusual in a park - code path only)
    "cue_material_break": True,    # True -> gravel tread (decomposed granite), False -> dirt_park (blends with the surrounding soil, more ambiguous)
    "cue_sign":           False,   # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,    # trees·shrubs (hedge)·benches as a set (trail·grass terrain is always on)
    "cue_nosing":         False,   # new key. True -> anti-slip strip on every step (unusual on a park sleeper stair)
}


# ===========================================================================
# [B] Irregular step table (brief §C) - the sums are the slope run/drop.
# ===========================================================================
RISERS = [0.16, 0.14, 0.18, 0.15, 0.19, 0.14, 0.17, 0.15, 0.17]   # sum = 1.45
TREADS = [0.55, 0.70, 0.50, 0.80, 0.60, 0.55, 0.75, 0.50, 0.60]   # sum = 5.55
STAIR_RUN = sum(TREADS)     # 5.55
STAIR_DROP = sum(RISERS)    # 1.45


# ===========================================================================
# [C] PARAMS - dimensions·materials·lighting·capture. light dict = scene01 port + SUN_AZ_OFFSET.
# ===========================================================================
PARAMS = dict(
    # --- Terrain (Z-up, descending +X). Base ground = grass, site widened to y+-25 ---
    upper=dict(x0=-35.0, x1=0.0, y0=-25.0, y1=25.0, z_top=0.0, thick=0.5),
    lower=dict(x0=STAIR_RUN, x1=35.0, y0=-25.0, y1=25.0, z_top=-STAIR_DROP,
               thick=0.5),
    # Slope (x 0..run): grass base + a dirt slope only within y+-dirt_y around the stair corridor.
    #   The corridor-side trim strip (y +-corridor_y..+-trim_out) seals the nosing line at +trim_over.
    # [v5.1] dirt_y 3.0 -> 1.7 : the exposed dirt slope on both sides of the stair is cut to a 0.55 m shoulder.
    #   The rest (1.7~25) is grass, covered by the verge (grass mound band + shrubs).
    slope=dict(x0=0.0, z0=0.0, run=STAIR_RUN, drop=STAIR_DROP, thick=0.35,
               corridor_y=0.9, trim_out=1.15, trim_over=0.02,
               dirt_y=1.7, flank_y=25.0),
    # 3m dirt connector before/after the stair (soil trail landing on the grass ground)
    connect=dict(length=3.0, half_y=3.0),

    # === [W2-D ground_kit] P11 trail_soil (spec §5.7 row 04) ===============
    # Natural profile: ground_kit raises on any urban infra by itself.
    # Element split follows the two constraints that actually bind here:
    #  * scatter (exposed gravel, exposure <= 0.06 m) obeys the GT-E5 ramp,
    #    |x_e| >= 40 * 0.06 = 2.40 m. The scatter field is driven by the plan
    #    **region**, so the region stops at x=-2.40; the d5/d10 near windows
    #    (x -4.44..-3.00 and -9.44..-8.00) sit fully inside it, and the d2
    #    window is filled by the strip elements below instead.
    #  * wear lane + edge litter are decals (+0.6 mm -> GT-E1' needs 0.024 m),
    #    so they may run right up to the stair head. They are given an explicit
    #    centreline on the ConnectU landing, which is the one straight piece of
    #    trail in frame; the PathU polyline meanders out of the h0.3 frame
    #    (at x=-9 its centre is y=-2.46 while the frame half width is 1.16).
    #  * `build_edge_break` targets the real culprit named by spec §5.7 /
    #    appendix A6: the 3.0 x 6.0 m ConnectU dirt box against the grass slab,
    #    transition width 0 px, dE76 18.9. Its three seams are x=-3.0 (across
    #    the frame) and y=+-3.0 (along it); the composer can only emit
    #    constant-y lines, so the seams are built by direct calls.
    #  * region y -3.0..+1.0 is not symmetric on purpose: it is the trail
    #    corridor. The PathU centre line runs y -2.46 (x=-9.3) to -1.36
    #    (x=-3.5), and the h0.3 frame half width is 1.16 m at X=2.0, so this
    #    band covers both the trail and the frame centre without spending
    #    scatter budget on lawn the camera never sees.
    gkit=dict(x0=-12.0, y0=-3.0, y1=1.0, scatter_x1=-2.40,
              wear=((-3.0, 0.0), (-0.6, 0.0)), wear_w=0.90),
    # Sleeper stair: width y −0.9..0.9, base_z=−1.8. Tread = gravel (decomposed granite).
    stairs=dict(x0=0.0, y0=-0.9, y1=0.9, base_z=-1.8, z_top=0.0,
                sleeper_thick=0.15, sleeper_over=0.02,
                stake_r=0.025, stake_h=0.35, stake_y=0.8),

    # Trail: width 1.8, dirt_park with a light tint, 1mm proud.
    # v4-A1: 3 axis-aligned segments + a cy 0.8 jog made a right-angle (Tetris) outline,
    #   not a curve -> replaced by a centreline polyline + rotZ-rotated segments
    #   (build_rot_group), 6 gently meandering segments. v4-A2: both ends now run
    #   into the background fence openings, curing the 'from nowhere, to nowhere' approach/exit cut.
    # [v5.1 realism] The old polyline drifted monotonically in y (upper −4.6->0, lower 0->1.9),
    #   so segment yaw varied only 8~12 deg - a 'gently bent straight line'. Regenerated
    #   with a sine meander (wavelength 21~23 m, amplitude 1.5 m) + node jitter (+-0.18):
    #   segment yaw +-20~32 deg, max adjacent yaw change 21 deg (upper)/27 deg (lower). Nodes 7->13 (upper)·7->11 (lower).
    #   The end nodes are kept: the upper start sits inside the background fence opening (y −6.5..−2.5),
    #   the lower end inside its opening (y −1.5..3.5), and the stair junctions (0,0)/(5.55,0) are fixed.
    #   width_jit: per-segment width +-10 % (removes the artificial band of a constant compacted width).
    # [W3 S04-1] tint 1.10/1.05/0.95 -> 1.00/0.96/0.88: against a lawn the trail had to be
    #   lifted to read as compacted soil; against a litter floor the same lift made the 6 m
    #   ConnectU landing the brightest object in the near frame (pilot round 1).
    path=dict(width=1.8, thick=0.06, proud=0.001, overlap=0.7, width_jit=0.10,
              tint=(0.94, 0.90, 0.82),
              upper=[(-33.0, -4.90), (-29.6, -5.51), (-26.7, -5.19),
                     (-23.8, -4.23), (-20.9, -2.39), (-18.0, -1.17),
                     (-15.1, -1.01), (-12.2, -1.49), (-9.3, -2.46),
                     (-6.4, -2.43), (-3.5, -1.36), (-1.2, -0.18), (0.0, 0.0)],
              lower=[(5.55, 0.0), (8.4, -1.07), (11.3, -0.72), (14.2, 0.16),
                     (17.1, 1.50), (20.0, 2.41), (22.9, 2.27), (25.8, 1.58),
                     (28.7, 0.57), (31.6, 0.02), (33.5, -0.15)]),

    # Far-field closure: background hedge band + tree line (blocks the void of the widened site).
    #   gz: 'lower'->lower flat, 'slope'->slope interpolation, number->absolute. (x0,y0,x1,y1).
    # v4-A4: the fences are pushed close to the site edge (x +-35 / y +-25) at +-34 / +-24.2 to minimise
    #   the grass that used to show above them + h 1.2->1.5.
    # v4-A3: the 5.55 m hole left open across the slope span (x 0..5.55) is sealed with a slope-interpolated band.
    # v4-A2: the openings the trail passes through are kept (upper y −6.5..−2.5 / lower y −1.5..3.5).
    bg_hedge=dict(h=1.5),
    bg_hedges=[
        dict(x0=-34.0, y0=-24.2, x1=-32.8, y1=-6.5, gz=0.0),    # upper rear (south)
        dict(x0=-34.0, y0=-2.5, x1=-32.8, y1=24.2, gz=0.0),     # upper rear (north)
        dict(x0=32.8, y0=-24.2, x1=34.0, y1=-1.5, gz="lower"),  # lower end (south)
        dict(x0=32.8, y0=3.5, x1=34.0, y1=24.2, gz="lower"),    # lower end (north)
        dict(x0=-34.0, y0=23.0, x1=0.0, y1=24.2, gz=0.0),       # upper +Y
        dict(x0=-34.0, y0=-24.2, x1=0.0, y1=-23.0, gz=0.0),     # upper -Y
        dict(x0=5.55, y0=23.0, x1=34.0, y1=24.2, gz="lower"),   # lower +Y
        dict(x0=5.55, y0=-24.2, x1=34.0, y1=-23.0, gz="lower"), # lower -Y
    ],
    # v4-A3: slope-span sealing band (grade-corrected - build_slope method)
    bg_slope_hedges=[dict(y0=23.0, y1=24.2), dict(y0=-24.2, y1=-23.0)],
    bg_trees=[dict(cx=-31.0, cy=-10.0, gz=0.0, trunk_h=2.4),
              dict(cx=-31.0, cy=9.0, gz=0.0, trunk_h=2.2),
              dict(cx=31.0, cy=-8.0, gz="lower", trunk_h=2.4),
              dict(cx=31.0, cy=6.0, gz="lower", trunk_h=2.2),
              dict(cx=31.0, cy=15.0, gz="lower", trunk_h=2.3)],

    # Nature: 5 trees (1 upper·1 beside the slope·3 lower). Lower trees get a reduced trunk_h so the
    #   canopy top lands at z ~ 0.5~1.2. gz='slope' interpolates the slope, 'lower' is the lower flat.
    trees=[dict(name="U0", cx=-6.0, cy=-4.0, gz=0.0, trunk_h=2.2),
           dict(name="S0", cx=2.5, cy=3.5, gz="slope", trunk_h=2.0),
           dict(name="L0", cx=9.0, cy=-3.0, gz="lower", trunk_h=1.3),
           dict(name="L1", cx=12.0, cy=4.0, gz="lower", trunk_h=1.4),
           dict(name="L2", cx=15.0, cy=-5.0, gz="lower", trunk_h=1.2)],
    tree=dict(trunk_r=0.06, stake_r=0.015, stake_h=1.2, stake_off=0.5),
    # v4-D9: trees 10 -> 18 (3 upper + 5 lower added)
    trees_extra=[dict(cx=-12.0, cy=-8.0, gz=0.0, trunk_h=2.3),
                 dict(cx=-18.0, cy=6.0, gz=0.0, trunk_h=2.5),
                 dict(cx=-24.0, cy=-3.0, gz=0.0, trunk_h=2.2),
                 dict(cx=20.0, cy=-6.0, gz="lower", trunk_h=1.5),
                 dict(cx=24.0, cy=5.0, gz="lower", trunk_h=1.7),
                 dict(cx=28.0, cy=-12.0, gz="lower", trunk_h=2.0),
                 dict(cx=18.0, cy=9.0, gz="lower", trunk_h=1.6),
                 dict(cx=22.0, cy=0.0, gz="lower", trunk_h=1.4)],

    # === [W3 S04-1] verge = G4 ground layer ================================
    # **Deleted here**: `hedges` / `hedge` (6 clusters x 3 flattened ellipsoids = 18 prims) and
    #   `verge.rows` (5 constant-`cy` rows of `add_sphere`, 121 prims). Both are the shape
    #   `tonglam_v2` failed the scene on - *"giant moss-green ellipsoid blobs"* - and G4 shows
    #   **no shrub dome anywhere**: the flanks are a litter floor, bare trunks and low tufts.
    #   The v6 rework (3 constant tuft colours, smaller, denser) treated the symptom
    #   (the texture) and kept the disease (the ellipsoid row). The row itself is now gone.
    #
    # Everything below is laid **against the walk centreline**, not against a constant `cy` -
    # that is what removes the "bead string beside a ruled band" read at source. `off` is the
    # perpendicular offset from the walk (trail polyline -> stair spine -> trail polyline).
    #
    # (a) Drift lobes - CB-2 `ground_kit.build_blot` (DEC-1), one Mesh each, single face,
    #     zero thickness, **never a rectangle**. Bands of lobes with jittered offset, radii and
    #     along-line spacing. `proud` 0.006 m: above the 4 mm scene07 uses (04's lobes sit on
    #     bare ground, not on stone) and far below the GT decal tolerance 0.020.
    litter=dict(
        proud=0.006, seed=40401, n=22, rough=0.20,
        reach=(-8.5, 12.5),                 # along-walk x window for the whole ground layer
        # bands: (offset, step, rx, ry, jit_off, jit_r)
        #   The apron band (first row) hugs the walk: small `ry` is what lets it pass the
        #   0.95 m corridor clearance at a 1.42 m offset, so litter reaches the stair
        #   shoulder the way G4's does instead of stopping a metre short.
        bands=((1.42, 1.05, 0.85, 0.34, 0.14, 0.18),
               (2.05, 1.35, 1.35, 0.80, 0.30, 0.20),
               (3.55, 1.85, 1.55, 0.95, 0.38, 0.20),
               (5.45, 2.35, 1.80, 1.10, 0.45, 0.22)),
        skip=0.10,
        # (b) 3-D leaf cards - the relief that stops a litter floor reading as lino
        #     (`scene_common.VEG_DEBRIS`, the S3 Debris leaf set). Season-legal here **because
        #     04 is now pinned late autumn** (R04-2); C2/07/10/D3 were the earlier scope.
        #   Scale band 0.55-0.95 (was 0.75-1.35): `fallcluster1` is natively 0.42 x 0.40 m
        #   `[measured - usd-core bbox, this WP]`, so the old upper bound put 0.57 m leaf
        #   clusters in the near frame - single leaves the size of a boot. More, smaller.
        cards=dict(n=320, seed=40417, off=(1.12, 5.20), scale=(0.55, 0.95),
                   rim=0.34),
        # (c) low tufts - the procured-but-unused turf patches. `veg_manifest_w2.json` records
        #     `Grass_Short_A` with role `verge_turf` and the note "잔디 패치(대) — scene04
        #     버지 블롭 대체", i.e. it was bought for exactly this deletion and never wired.
        #     Hue orange 0.177 / green 0.537 -> inside the turf gate, legal in the autumn cell.
        #   n 30 -> 14 after pilot round 1: 30 turf patches read as a lawn breaking through
        #   the litter, and G4 shows **two or three** green clumps in the whole frame.
        tufts=dict(n=14, seed=40423, off=(1.30, 4.60), h=(0.12, 0.17),
                   clump=(2, 3), clump_r=0.75),
    ),
    # (d) bare trunks - the G4 signature. Authored, not scattered: they frame the stair.
    #     (x, perpendicular offset from the walk, target height [m], species slot)
    #     Species slots: 0 = birch · 1 = elm (leaf-off capable, see TREES04).
    #     [GT-126] Slot 2 (poplar) retired — see the TREES04 note. The nine former slot-2
    #     rows keep their positions and heights and alternate 0/1, so the tall rank stays.
    trunks=[(-7.6, -4.35, 8.6, 0), (-6.1, 3.05, 4.1, 0), (-4.2, -3.15, 3.4, 1),
            (-2.4, 2.60, 9.4, 1), (-0.9, -2.45, 3.8, 0), (0.7, 2.20, 4.6, 0),
            (1.9, -2.10, 3.3, 1), (3.3, 2.45, 10.2, 0), (4.6, -2.35, 4.4, 0),
            (5.9, 2.75, 3.6, 1), (7.4, -2.80, 9.0, 1), (8.8, 3.10, 4.8, 0),
            (10.6, -3.40, 3.9, 1), (12.1, 3.60, 8.2, 0),
            # second rank - G4's flanks are a *stand*, not a row. These sit 6-11 m off the
            # walk and close the frame behind the first rank.
            (-8.8, 7.40, 11.5, 1), (-5.0, -6.90, 4.6, 0), (-1.6, -7.80, 10.8, 0),
            (2.2, 6.60, 4.2, 1), (6.2, -6.40, 11.0, 1), (9.6, 7.10, 4.9, 0),
            (13.4, -7.60, 10.4, 0), (15.8, 6.20, 4.3, 1)],

    # === [W3 S04-1] rope-on-timber-post handline (K4(c) new prop template) ==
    # **R04-1: DRESSING, NOT A GUARD.** Built in **both** hazard arms so its presence carries
    #   zero information about the negative-obstacle label (the same twin-parity discipline
    #   `build_ground_kit` already follows for GT-E4). Asserted in `verge_selfcheck`.
    # Built form:
    #   · post   Ø0.12 m round timber `[assumed]`, above the ≥0.07 m 끝마구리 floor that
    #     「조경공사 표준시방서」(2003/2016) sets for a 통나무 post line `[law, adjacent form -
    #     the clause governs a 철조망 post line, the nearest codified 통나무 post rule]`.
    #   · pitch  ≤1.75 m, inside the same clause's ≤1.8 m post spacing. G4 reads ~2 m `[assumed]`.
    #   · height 0.95 m exposed. KNPS-RAIL n=243 rows whose name contains 로프 give a median
    #     **1.00 m** (`Docs/surveys/s3_research_numbers_v1.md` §A3, grade **B** - the column is
    #     `폭높이` and may mix width entries) `[data]`. 0.95 is that median minus the grade-B
    #     margin and matches G4's post-to-step proportion.
    #   · rope   Ø0.018 m `[assumed]` (16-20 mm is the trail band), tied 0.10 m below the post
    #     top, catenary sag 0.075 x span, drawn as 6 straight segments per span.
    #   · offset 1.35 m from the walk centreline - outboard of the stair half width 0.90, of the
    #     trim strip 1.15 and of the trail half width 0.99 (worst case with `width_jit`).
    #   · reach  x -0.55 .. 6.60 along the walk. Two reasons, both stated: a 로프난간 is
    #     installed at the steep/stepped reach, not along a flat park path; and extending it up
    #     the meandering trail would stand posts 0.85-1.08 m in front of the d5/d10 preset eyes
    #     (which run along y=0 while the trail wanders off it) - the "new geometry swallows a
    #     preset camera" regression this project has already had four times.
    rope=dict(x0=-0.55, x1=6.60, offset=1.35, pitch_max=1.75,
              post_r=0.060, post_h=0.95, post_embed=0.10, post_jit=0.035,
              rope_r=0.009, tie_drop=0.10, sag=0.075, seg=6, eye_keepout=1.20),

    # 5 benches (v4-D4: 1 -> 5). (cx, cy, gz, yaw)
    # [v5.1 global convention 3] No grid or aligned placement -> all moved beside an anchor (tree shade·shrub
    #   cluster·trail edge) with yaw jittered +-3~8 deg to a non-integer angle.
    #   · (11.7, 2.55) under the canopy of tree L1(12,4) - the seat axis runs along y (yaw 96), so
    #     the seat end (11.7, 3.45) clears the trunk (12,4) by 0.62 m (no interpenetration).
    #   · (−8.7, 3.3) 1.44 m beside the shrub cluster (−10,3) · (10.1,−3.05) 1.10 m beside
    #     tree L0(9,−3) · (17.2, 3.1) 1.20 m beside the shrub (16,3) · (−13.0,−2.55) at the trail edge
    #     (1.18 from the centreline -> 0.19 m from the road edge).
    #   All are outside the trail half width 0.99 - zero benches standing on the path.
    benches=[(11.7, 2.55, "lower", 96.0), (-8.7, 3.3, 0.0, 94.0),
             (-13.0, -2.55, 0.0, 4.5), (10.1, -3.05, "lower", 93.0),
             (17.2, 3.1, "lower", 87.0)],
    # v4-D1 [top priority] wooden signpost - fixes 'park trail' in a single frame
    # [v5.1] (−3.5, 2.2) was open ground 3.5 m from the re-meandered trail (centre y ~ −1.36 at that x)
    #   -> moved 0.15 m to the side of the outer trail curve (edge −1.80).
    signpost=dict(cx=-2.3, cy=-1.95, post_r=0.07, post_h=2.0,
                  arm=(0.9, 0.06, 0.16), arm_off=0.45,
                  arms=((1.75, 22.0), (1.5, 203.0))),   # (z, yaw)
    # v4-D2 information map board
    # [v5.1] The old (−6.0,−2.6) was **inside** the re-meandered trail band (centre −2.43, edge −3.33),
    #   standing mid-road -> moved 0.35 m outside the trail (2.5 m from tree U0(−6,−4)).
    board=dict(cx=-8.5, cy=-4.15, thick=0.10, width=1.4, z0=1.0, z1=1.9,
               post_r=0.05),
    # v4-D5 3 bins - [v5.1] repositioned to the re-meandered trail edge (0.2~0.5 m)
    bins=[(-3.2, -2.85, 0.0), (7.4, -1.9, "lower"), (14.3, 1.5, "lower")],
    bin_spec=dict(r=0.26, h=0.85),
    # v4-D6 pergola/shelter
    pergola=dict(x0=10.0, x1=13.0, y0=4.5, y1=7.5, z_roof=2.5, post_r=0.09,
                 roof_t=0.14),
    # v4-D11 4 leaf piles (season cue·ground variety)
    # [v5.1] Repositioned onto/beside the re-meandered trail (<=0.3 m from the centreline) - leaves
    #   must pile on a compacted surface to read as 'a path people walk'.
    # [W3 S04-1] The four piles were **1.6 x 1.2 m axis-aligned boxes** - i.e. rectangles, the
    #   one shape CB-2 exists to abolish. Same four sites, now DEC-1 lobes (`build_blot`) with
    #   the drift material; `sy` becomes the lobe's y radius, `sx/2` its x radius.
    #   [W3 S04-1] Extended from 4 to 10 sites. These are the **only** litter lobes allowed to
    #   lie on a walked approach surface (the 3 x 6 m ConnectU landing and the trail band), and
    #   they are authored rather than generated for exactly that reason. The class is
    #   unchanged: at `proud` 0.006 m they are decals, an order below the 0.024 m GT-E1'
    #   tolerance, and `ground_kit`'s own `edge_litter` / `wear_lane` decals already sit on
    #   this same slab at +0.6-2 mm. **None of them touches a stair tread** - the nosing cut
    #   line is this scene's hazard cue and it stays clean (see `verge_selfcheck` (2)).
    leaf_piles=[(-9.0, -2.50, 0.0), (-2.0, -0.75, 0.0), (8.0, -0.95, "lower"),
                (15.0, 0.60, "lower"),
                (-2.55, 1.35, 0.0), (-1.30, -1.55, 0.0), (-0.75, 1.05, 0.0),
                (-2.20, -2.25, 0.0), (6.80, 1.20, "lower"), (7.60, -1.85, "lower")],
    leaf=dict(rx=1.05, ry=0.72, proud=0.006, n=20, rough=0.22, seed=40431),

    # Log handrail line (y=+1.0) when cue_railing is True.
    log_rail=dict(y=1.0, rail_r=0.05, post_r=0.05, rail_h=0.9, spacing=1.2),

    # --- Materials: physical size for texture_scale [m/tile] ---
    material=dict(
        # S4-4: dirt_park scale 2.0->3.0 (smaller leaf grain), desaturated tint.
        # [W3 S04-1] `grass` is **retired from this scene** (see the seasonal audit): a lawn
        #   texture measured 98.25 % green is a summer pixel set, and G4's off-path ground is
        #   litter end to end. `leaf_ground` (TEX role, the C2 fallen-leaf ground) takes over.
        # `leaf_ground` at 2.0 m/tile made 4-6 cm leaves subtend ~2 px at the h0.3 eye and
        #   the floor read as *sand with confetti* in the first pilot cut. 1.20 m/tile puts
        #   the leaf grain at G4's apparent size. `[measured - pilot round 1, this WP]`
        scale=dict(dirt_park=3.0, gravel=0.5, leaf_ground=1.20, wood_dark=1.0),
        dirt_tint=(0.92, 0.88, 0.80),           # eases over-saturated leaves (base soil ground)
        # [W3 S04-1] two litter tones so the drift lobes read against the floor they lie on:
        #   the floor is the flatter/greyer one, the drift a touch warmer and darker (a drift is
        #   deeper, so it is less lit). Both are the same texture - only the tint differs, which
        #   is the cheapest legal way to get tonal variation without a second 4K map.
        # Pilot round 1 measured the floor far too bright against G4 (whose litter sits at
        #   sRGB ~150/110/80). The map's own mean is 0.270/0.211/0.124, so the tint carries it
        #   rather than fights it: the floor is left near-neutral-warm and the drift goes
        #   deeper, because a drift is thicker litter in shade, not a different leaf.
        litter_tint=(0.88, 0.82, 0.72),
        #   Round-2 note: at 0.70/0.60/0.48 the drift lobes read as **dark islands with a hard
        #   rim** on the paler floor at grazing angles - the "carpet laid on the ground"
        #   artefact `tonglam_v2` §2.13-2 flagged on 07's leaf band. Two cures applied
        #   together: the tint gap is halved, and a third of the leaf cards are seeded on the
        #   lobe rims (the DEC-2 feather-ring idea, re-implemented with a walk mask).
        drift_tint=(0.79, 0.71, 0.59),
        # far-field understory mass (`bg_hedge` band). Same texture, darkest tint - at 34 m it
        #   is a brown twig/litter mass, which is what a late-autumn hillside actually shows.
        hedge_tint=(0.62, 0.56, 0.48),
        # [v5.1 global convention 4] Instance tint jitter +-5 % - to add as few new materials as possible
        #   the base colour is left alone and only the variant count grows.
        tint_jitter=0.05,
        # S4-3: tree colours unified with the scene01 final values
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,   # tree trunk·stakes
        # [W3 S04-1] rope + post. The rope in G4 is a pale weathered twisted rope; timber posts
        #   are grey-brown weathered 방부 log. Constant colours (a Ø18 mm rope and a Ø120 mm
        #   post are below the resolution where a tiled map buys anything).
        rope_color=(0.60, 0.56, 0.47), rope_rough=0.92,
        post_color=(0.24, 0.19, 0.14), post_rough=0.88,
        # v4-B (shared): canopy albedo. **Blob-fallback only** (assets absent / LOOK_GEO=0) -
        #   with the assets present every tree is a real leaf-off USD. Pinned to a late-autumn
        #   dry-twig brown so the fallback does not smuggle summer green into an autumn scene.
        canopy_a=(0.052, 0.041, 0.026), canopy_b=(0.061, 0.047, 0.029),
        canopy_rough=1.0,
        tactile_color=(0.85, 0.72, 0.10),       # cue_tactile constant yellow
        sign_face=(0.55, 0.56, 0.58),           # v4-D2 board map face
    ),

    # --- Lighting: scene01 light dict as-is + SUN_AZ_OFFSET=171.5 ---
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


# Parameter override (for A/B render comparison - no effect on a default run, scene01 pattern)
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

# SCENE_CONFIG environment override (for the toggle-integrity verification pipeline)
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C-2] PLACEMENT — the geometry-free declaration `scripts/placement_lint.py` reads
#       (spec §10.4). Additive and static: it authors no prim and moves no coordinate, and it
#       is parsed as a module-level literal, so every value here must stay a literal.
#       Added by W3 S04-1 because the linter reported `PLACEMENT=NO` for this scene, i.e.
#       every rule needing a datum was degrading to `nodata`.
# ===========================================================================
PLACEMENT = dict(
    # **Empty on purpose, and that is a finding rather than an omission** - the same call
    # scene07 made. LINT-5 reads `walk_edges` as a 보도 footway boundary and applies PE-8,
    # 「도로의 구조·시설 기준에 관한 규칙」 제16조's 1.5 m effective-width floor, to anything
    # standing near it. This is a park 산책로 with a sleeper stair, not a 도로 보도: 제16조
    # does not govern it, and declaring the trail edge as a footway boundary would import a
    # rule that would then "fail" the rope handline - a device that is standard practice on
    # exactly this archetype. The datum is declared **absent**, not mis-declared.
    walk_edges=[],
    # There is no kerb line on a park trail. The dirt shoulder is a cut edge, not a 연석,
    # so LINT-1's tree-to-kerb rule is vacuous here rather than unmeasured.
    kerb_lines=[],
    # **No anchor is declared, and the reason is measured, not stylistic.** Declaring one was
    # tried in this WP: LINT-7 then becomes enforceable and turns 8 advisory `[inferred]` WARNs
    # into **12 ERRORs** against props whose bearing is correct built form - a trail signpost
    # carries two arms pointing *both ways along the path* (yaw 22° / 203°), so no single
    # `face_bearing_deg` describes it, and the benches sit against tree shade and the trail
    # edge with the v5.1 ±3-8° jitter, i.e. against natural anchors that have no build axis.
    # Fitting a bearing datum to the geometry it is supposed to judge proves nothing, so the
    # datum is left absent and LINT-7 stays advisory - which is what §10.4 says an inferred
    # finding is for.
    anchors={},
    # 04's trees are a **hillside stand**, not a street route. Declaring a `route` would import
    # a 6-8 m street-tree pitch rule that no forest has ever obeyed (X4's scene13 call).
    routes={},
)


# ===========================================================================
# [D] Paths
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene04")

# Only the texture roles this scene uses are checked.
# [W3 S04-1] `grass` -> `leaf_ground`: the scene is pinned late autumn (R04-2) and no prim
#   is bound to the lawn texture any more, so listing it would assert a dependency we do not have.
ASSET_ROLES = ["dirt_park", "gravel", "leaf_ground", "wood_dark", "hdri", "mdl"]

# [W3 S04-1] Scene-local tree species table - the season pin needs a species selector and
#   `build_tree` has none (it draws from `scene_common.VEG_TREES` by coordinate hash; the
#   planned K4(b) `species=` kwarg does not exist yet, and K4 is not this lane's file).
#   `(usd rel, native zmax [m], weight, bare)` - `native` is the **measured `zmax`**, the
#   quantity `add_vegetation` scales against `[measured - assets/veg_manifest_w2.json]`.
#   Who is here and who is not, by the pixel rule, not by species name:
#     · Gray_Birch / Elm_Sapling / Lombardy_Poplar - the **only three** assets in the whole
#       library that split trunk and leaves into sibling meshes under `/Root`, so
#       `BARE_SUBPRIMS` can strip `/Root/leaves` and leave a real bare tree
#       (`scene_common.py` BARE_SUBPRIMS, landed `1346b70`). They carry the branch armature in
#       the trunk mesh, so leaf-off costs 24-46 % of the triangles and keeps 98-99 % of height.
#     · `Shumard_Oak` - **excluded**. Its leaves ride inside MASH `PointInstancer`s that also
#       carry the branches, so it **cannot be stripped** (verified in the K4 micro-commit), and
#       green oak foliage in a leaf-off frame is exactly the cherry-blossom mistake again.
#       It is not "pushed to the backdrop" either: a green broadleaf at 34 m is still green.
#     · one evergreen conifer, **far field only** - a conifer is legitimately green in late
#       autumn and a Korean hillside in November is bare broadleaf with conifer mixed in.
#       It is `Douglas_Fir` (zmax 6.0263, 24,336 tri, manifest verdict **PASS**), not a pine:
#       `Yellow_Pine` and `White_Pine` are **retired species** under spec §10.2 and
#       `placement_lint` LINT-4b errors on them by the bound asset name - measured on this
#       very file, 3 ERROR, before the swap. Douglas fir is a `[substitute]` for the Korean
#       conifer the same way `Shumard_Oak` substitutes for pin oak in `VEG_TREES`.
#     · `Chinese_Juniper` - excluded: evergreen, so season-legal, but it is a landscaping
#       shrub-tree, not a hillside forest species.
#
# **The bare rows reference a wrapper layer, not the source asset, and that is a defect
#   report as much as a design choice.** `build_tree(bare=)`'s mechanism - deactivate
#   `/Root/leaves` on the referencing prim, *then* `SetInstanceable(True)` - does not survive
#   instancing: USD ignores prim opinions on **descendants of an instance**, so the shared
#   prototype is composed from the reference alone and keeps its leaves. Measured twice this
#   session: `usd-core 26.8` reports the prototype's children as `['Looks', 'trunk', 'leaves']`
#   after a successful `SetActive(False)`, and pilot round 1 rendered **37/37 trees in full
#   green leaf** while the scene log reported 37 deactivations and 0 failures. The K4 commit
#   could not have seen this - its acceptance test was a 33/33 prim-hash identity with the
#   feature **off**, and no scene had opted in. The fix belongs in `scene_common` (Lane K4's
#   file, not this lane's); scene04 carries it as three additive wrapper layers under
#   `assets/veg_bare/` (deliberately **outside** the gitignored `assets/vegetation/` tree - the
#   wrapper holds no asset content, so it is trackable while the geometry stays procured), which put
#   the `over` **above** the instance boundary and
#   keep one shared prototype per species. Reported in `Docs/reports/w3_s04_v1.md` §7.
#   `native` for a bare row is the **bare** zmax `[measured - usd-core, this session]`, so the
#   0.8-1.8 % height shortfall the K4 note warns about does not apply here either.
# [GT-126] `Lombardy_Poplar_bare` is retired from every 04 pool. The wrapper composes with
#   the full twig broom in `/Root/trunk` (max radial extent 2.32 m at z 5.4-6.7 `[measured -
#   usd-core 26.8, this WP]`), yet in every render round on file (260806 allview5 · 260814
#   r0probe · 260815 datapilot) no placed instance shows any of it at the scales this scene
#   draws (0.17-0.90 of a 13.42 m native) — each renders as a smooth branchless column, the
#   audit's "민둥 기둥" finding. Birch/elm render their armature in the same frames at every
#   scale, so the near/mid pool is those two; the far pool keeps the conifer unchanged.
TREES04 = [
    ("../veg_bare/Gray_Birch_bare.usda",  3.2960, 4, True),
    ("../veg_bare/Elm_Sapling_bare.usda", 3.0424, 3, True),
]
TREES04_FAR = TREES04 + [("Trees/Douglas_Fir.usd", 6.0263, 2, False)]
# Low turf patches. `(usd rel, native zmax [m], |zmin| [m], native half width [m], weight)`
#   `[measured - assets/veg_manifest_w2.json]`. A/B carry `role: verge_turf` and the note
#   *"잔디 패치(대) — scene04 버지 블롭 대체"*: they were procured for exactly this deletion
#   and have never been wired. C is the repo's standing `edge_weed` asset (1,598 tri).
#   Weights favour the **small** patches: at native scale A is 1.29 m across, and a 2 m turf
#   mat is a lawn, not the handful of clumps G4 shows in the litter.
# Placement tally — filled at build time, printed with the assembly line. A season pin that
#   nobody counts is a claim; this makes "every near tree is leaf-off" a **number in the log**.
VEG_TALLY = {}

TUFTS04 = [("Shrub/Grass_Short_A.usd", 0.1390, 0.0228, 0.6446, 1),
           ("Shrub/Grass_Short_B.usd", 0.1464, 0.0172, 0.3308, 2),
           ("Shrub/Grass_Short_C.usd", 0.1229, 0.0021, 0.1395, 6)]


def slope_z(x):
    """Slope top-face z interpolation (x 0..run -> 0..−drop, clamped outside)."""
    sl = PARAMS["slope"]
    t = max(0.0, min(x / sl["run"], 1.0))
    return sl["z0"] - sl["drop"] * t


def ground_z(x):
    """[W3 S04-1] Ground top z of **the arm actually being built**.

    The hazard arm is the slope profile; the `hazard_stairs=False` control is one flat plane
    at z=0 (`build_flat_fill`). Every element of the new ground layer - litter lobes, leaf
    cards, tufts, trunks, rope posts - is seated with this, which is what lets the whole layer
    (the handline above all) be built **identically in both arms**. That is not a convenience:
    a dressing element that appears only in the hazard arm is a label leak, and R04-1 forbids
    the handline from carrying label information.
    """
    return slope_z(x) if SCENE_CONFIG["hazard_stairs"] else 0.0


def slope_grade(x):
    """dz/dx of the ground at x (0 outside the slope run, 0 in the flat control)."""
    sl = PARAMS["slope"]
    if not SCENE_CONFIG["hazard_stairs"]:
        return 0.0
    return -(sl["drop"] / sl["run"]) if 0.0 <= x <= sl["run"] else 0.0


def _resolve_gz(spec_gz, cx):
    """Resolve a gz spec: 'slope'->slope interpolation, 'lower'->lower flat, number->as-is."""
    if spec_gz == "slope":
        return slope_z(cx)
    if spec_gz == "lower":
        return PARAMS["lower"]["z_top"]
    return float(spec_gz)


def tint_jitter(color, seed, amp=None):
    """[v5.1 global convention 4] Per-instance +-amp colour jitter (deterministic).

    When dozens of instances share one constant colour it reads as 'copy-paste
    placement'. The base colour is left alone; the seed only wobbles it by +-5 %."""
    if amp is None:
        amp = PARAMS["material"]["tint_jitter"]
    rnd = random.Random(1000003 * (int(seed) + 11))
    return tuple(round(max(0.005, c * (1.0 + rnd.uniform(-amp, amp))), 5)
                 for c in color)


# ===========================================================================
# [D2] [W3 S04-1] Walk-relative ground-layer generators.
#
#   Every generator below is **deterministic and boot-free**, and the assembler and the
#   checker consume the same one - the v6 lesson (`verge_instances`) that a checker with its
#   own copy of the coordinates checks nothing. `verge_selfcheck` therefore measures the
#   prims that are actually built.
#
#   The organising idea of the rebuild: the old verge was five rows at **constant `cy`**
#   beside a meandering trail, which is why it read as a bead string beside a ruled band.
#   Everything here is placed at a **perpendicular offset from the walk centreline**, so the
#   litter, the tufts and the handline all bend with the path the way G4's do.
# ===========================================================================
def _walk_polyline():
    """Walk centreline: upper trail -> stair spine -> lower trail. x is monotone."""
    pa = PARAMS["path"]
    pts = list(pa["upper"])                       # ... -> (0.0, 0.0)
    pts.append((STAIR_RUN, 0.0))                  # stair spine (corridor centre)
    pts.extend(pa["lower"][1:])                   # lower starts at (STAIR_RUN, 0)
    return pts


WALK = _walk_polyline()
# Worst-case trail half width: `path.width` x (1 + `width_jit`) / 2 = 1.8 x 1.1 / 2.
TRAIL_HALF = PARAMS["path"]["width"] * (1.0 + PARAMS["path"]["width_jit"]) / 2.0
STAIR_HALF = PARAMS["stairs"]["y1"]               # 0.90


def _seg_dist(x, y, a, b):
    """Distance from (x,y) to segment a-b, and the parameter t of the closest point."""
    (xa, ya), (xb, yb) = a, b
    dx, dy = xb - xa, yb - ya
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 <= 1e-12 else max(0.0, min(1.0, ((x - xa) * dx
                                                   + (y - ya) * dy) / L2))
    return math.hypot(x - (xa + t * dx), y - (ya + t * dy)), t


def trail_dist(x, y):
    """Perpendicular distance to the nearest **trail** centreline segment (not the stair)."""
    pa = PARAMS["path"]
    best = 1e9
    for pts in (pa["upper"], pa["lower"]):
        for n in range(len(pts) - 1):
            best = min(best, _seg_dist(x, y, pts[n], pts[n + 1])[0])
    return best


def walk_clear(x, y):
    """Clearance [m] from (x,y) to the nearest **walked surface** edge.

    Two walked surfaces exist: the trail band (half width `TRAIL_HALF`, worst case) and the
    stair corridor (`|y| <= STAIR_HALF` over `x -0.10 .. STAIR_RUN + 0.10`, the connector
    landings included). Negative means the point is *on* a walked surface. This is the single
    predicate every new element is filtered by, so "nothing new stands where a person walks"
    is true by construction and measurable without a render.
    """
    c = trail_dist(x, y) - TRAIL_HALF
    if -0.10 <= x <= STAIR_RUN + 0.10:
        c = min(c, abs(y) - STAIR_HALF)
    return c


def _ellipse_support(rx, ry, nx, ny):
    """Support radius of an axis-aligned ellipse along the unit direction (nx, ny)."""
    return math.hypot(rx * nx, ry * ny)


def _walk_support_clear(x, y, rx, ry):
    """`walk_clear` for an ellipse: clearance measured with the ellipse's own support radius
    along each walked edge's normal, not with its bounding circle. A drift lobe is long
    **along** the path and short across it, so a bounding-circle test would push the whole
    litter band 0.5 m further out than the geometry needs."""
    pa = PARAMS["path"]
    best = 1e9
    for pts in (pa["upper"], pa["lower"]):
        for n in range(len(pts) - 1):
            d, _t = _seg_dist(x, y, pts[n], pts[n + 1])
            (xa, ya), (xb, yb) = pts[n], pts[n + 1]
            L = math.hypot(xb - xa, yb - ya) or 1.0
            nx, ny = -(yb - ya) / L, (xb - xa) / L
            best = min(best, d - TRAIL_HALF - _ellipse_support(rx, ry, nx, ny))
    if -0.10 <= x <= STAIR_RUN + 0.10:
        best = min(best, abs(y) - STAIR_HALF - ry)
    return best


def _walk_at(s):
    """Point and unit direction at arc length `s` along `WALK`."""
    acc = 0.0
    for n in range(len(WALK) - 1):
        (xa, ya), (xb, yb) = WALK[n], WALK[n + 1]
        L = math.hypot(xb - xa, yb - ya)
        if acc + L >= s or n == len(WALK) - 2:
            t = 0.0 if L <= 1e-9 else max(0.0, min(1.0, (s - acc) / L))
            return ((xa + t * (xb - xa), ya + t * (yb - ya)),
                    ((xb - xa) / (L or 1.0), (yb - ya) / (L or 1.0)))
        acc += L
    return WALK[-1], (1.0, 0.0)


def _walk_s_of_x(x):
    """Arc length of the first point on `WALK` at abscissa x (x is monotone along WALK)."""
    acc = 0.0
    for n in range(len(WALK) - 1):
        (xa, ya), (xb, yb) = WALK[n], WALK[n + 1]
        L = math.hypot(xb - xa, yb - ya)
        if xa <= x <= xb and abs(xb - xa) > 1e-9:
            return acc + L * (x - xa) / (xb - xa)
        acc += L
    return acc


def _grade_tilt(x):
    """(tiltX, tiltY) [deg] that lays a flat asset along the local grade.
    Same convention as `scene_common.scatter_debris`: tilt = (atan(dz/dy), -atan(dz/dx))."""
    return (0.0, -math.degrees(math.atan(slope_grade(x))))


def litter_lobes():
    """CB-2 drift lobes (DEC-1). yield: (i, cx, cy, rx, ry, seed)."""
    lt = PARAMS["litter"]
    s0, s1 = (_walk_s_of_x(lt["reach"][0]), _walk_s_of_x(lt["reach"][1]))
    i = 0
    for b, (off, step, rx0, ry0, joff, jr) in enumerate(lt["bands"]):
        for side in (1.0, -1.0):
            k, s = 0, s0
            while s <= s1 + 1e-6:
                rnd = random.Random(int(lt["seed"] + b * 977 + k * 7919
                                        + (0 if side > 0 else 3571)))
                s_next = s + step * (1.0 + rnd.uniform(-0.30, 0.30))
                k += 1
                if rnd.random() < lt["skip"]:
                    s = s_next
                    continue
                (cx, cy), (dx, dy) = _walk_at(s)
                nx, ny = -dy, dx
                d = off + rnd.uniform(-joff, joff)
                px, py = cx + side * d * nx, cy + side * d * ny
                rx = rx0 * (1.0 + rnd.uniform(-jr, jr))
                ry = ry0 * (1.0 + rnd.uniform(-jr, jr))
                # A lobe never laps a walked surface: GT stays class **A** by construction
                # (the alternative - litter over the treads - is on-archetype for G4 but moves
                #  the walked-surface reading, so it is a supervisor call, not this lane's).
                if _walk_support_clear(px, py, rx, ry) >= 0.05:
                    yield (i, px, py, rx, ry, int(lt["seed"] + 13 * i))
                    i += 1
                s = s_next


def leaf_cards():
    """3-D leaf cards over the flanks. yield: (i, px, py, rel, scale, yaw, tilt)."""
    lt = PARAMS["litter"]["cards"]
    reach = PARAMS["litter"]["reach"]
    s0, s1 = _walk_s_of_x(reach[0]), _walk_s_of_x(reach[1])
    pool = [p for p in sc.VEG_DEBRIS
            if os.path.isfile(os.path.join(sc.VEG_DIR, p[0]))]
    if not pool:
        return
    rnd = random.Random(int(lt["seed"]))
    lobes = list(litter_lobes())
    i, tries = 0, 0
    while i < int(lt["n"]) and tries < int(lt["n"]) * 12:
        tries += 1
        if lobes and rnd.random() < float(lt.get("rim", 0.0)):
            # **Rim card** - DEC-2's feather ring, re-implemented. `build_carpet_mask` would
            # give it for free, but its ring is an unmasked AABB scatter and 04's walk runs
            # *through* the litter band, so its cards would land on the stair and the trail.
            # Here the ring is drawn on the lobe's own ellipse and then passed through the
            # same walk mask as every other card.
            _i, lx, ly, lrx, lry, _sd = lobes[rnd.randrange(len(lobes))]
            a = rnd.uniform(0.0, 2 * math.pi)
            r = rnd.uniform(0.88, 1.16)
            px, py = lx + lrx * r * math.cos(a), ly + lry * r * math.sin(a)
        else:
            s = rnd.uniform(s0, s1)
            (cx, cy), (dx, dy) = _walk_at(s)
            nx, ny = -dy, dx
            side = 1.0 if rnd.random() < 0.5 else -1.0
            # sqrt-biased draw across the band: a real litter floor is deepest against the
            # cut shoulder and thins outward, and a flat uniform draw reads as wallpaper.
            u = rnd.random()
            d = lt["off"][0] + (lt["off"][1] - lt["off"][0]) * (u ** 0.7)
            px, py = cx + side * d * nx, cy + side * d * ny
        if walk_clear(px, py) < 0.06:
            continue
        rel = pool[rnd.randrange(len(pool))][0]
        yield (i, px, py, rel, rnd.uniform(*lt["scale"]),
               rnd.uniform(0.0, 360.0), _grade_tilt(px))
        i += 1


def tuft_instances():
    """Low turf patches in clumps. yield: (i, px, py, rel, native, zmin, target_h, yaw)."""
    tf = PARAMS["litter"]["tufts"]
    reach = PARAMS["litter"]["reach"]
    s0, s1 = _walk_s_of_x(reach[0]), _walk_s_of_x(reach[1])
    pool = [t for t in TUFTS04
            if os.path.isfile(os.path.join(sc.VEG_DIR, t[0]))]
    if not pool:
        return
    wpool = [t for t in pool for _ in range(t[4])]
    rnd = random.Random(int(tf["seed"]))
    i, tries = 0, 0
    while i < int(tf["n"]) and tries < int(tf["n"]) * 12:
        tries += 1
        # G4's tufts are not a band - they are a handful of clumps in the litter, so the
        # generator draws a clump anchor and then 2-4 members around it.
        s = rnd.uniform(s0, s1)
        (cx, cy), (dx, dy) = _walk_at(s)
        nx, ny = -dy, dx
        side = 1.0 if rnd.random() < 0.5 else -1.0
        d = rnd.uniform(*tf["off"])
        ax, ay = cx + side * d * nx, cy + side * d * ny
        for _m in range(rnd.randint(*tf["clump"])):
            if i >= int(tf["n"]):
                break
            r = tf["clump_r"] * math.sqrt(rnd.random())
            a = rnd.uniform(0.0, 2 * math.pi)
            px, py = ax + r * math.cos(a), ay + r * math.sin(a)
            rel, native, zmin, hw, _w = wpool[rnd.randrange(len(wpool))]
            h = rnd.uniform(*tf["h"])
            # A turf patch is 0.28-1.29 m across, so it is filtered on its **own scaled
            # footprint**, not on the point clearance the leaf cards use.
            if walk_clear(px, py) < hw * (h / native) + 0.05:
                continue
            yield (i, px, py, rel, native, zmin, h, rnd.uniform(0.0, 360.0))
            i += 1


def trunk_instances():
    """Authored bare trunks along the flanks. yield: (i, px, py, rel, native, h, bare)."""
    rnd = random.Random(40441)
    for i, (x, off, h, slot) in enumerate(PARAMS["trunks"]):
        s = _walk_s_of_x(x)
        (cx, cy), (dx, dy) = _walk_at(s)
        nx, ny = -dy, dx
        px, py = cx + off * nx, cy + off * ny
        rel, native, _w, bare = TREES04[int(slot) % len(TREES04)]
        yield (i, px, py, rel, native, h * rnd.uniform(0.94, 1.06), bare)


# --- the rope-on-timber-post handline (R04-1: dressing, not a guard) --------
def rope_posts():
    """Post positions on both sides. yield: (side, k, px, py, gz).

    Lift-ready: the only scene coupling is `WALK` / `ground_z`, both passed as values here,
    so `props_kit` can take this verbatim as `build_rope_handline(line, ground_fn, spec)`.
    """
    rp = PARAMS["rope"]
    s0, s1 = _walk_s_of_x(rp["x0"]), _walk_s_of_x(rp["x1"])
    L = s1 - s0
    n_span = max(1, int(math.ceil(L / rp["pitch_max"])))
    for k in range(n_span + 1):
        (cx, cy), (dx, dy) = _walk_at(s0 + L * k / n_span)
        nx, ny = -dy, dx
        for side in (1.0, -1.0):
            px, py = cx + side * rp["offset"] * nx, cy + side * rp["offset"] * ny
            yield (side, k, px, py, ground_z(px))


def rope_pitch():
    """Realised post pitch [m] (arc length / span count)."""
    rp = PARAMS["rope"]
    L = _walk_s_of_x(rp["x1"]) - _walk_s_of_x(rp["x0"])
    return L / max(1, int(math.ceil(L / rp["pitch_max"])))


def rope_span_points(p0, p1):
    """Catenary-ish rope polyline between two tie points (parabolic sag, `seg` segments)."""
    rp = PARAMS["rope"]
    n = int(rp["seg"])
    span = math.dist(p0, p1)
    sag = rp["sag"] * span
    out = []
    for i in range(n + 1):
        t = i / n
        out.append((p0[0] + t * (p1[0] - p0[0]),
                    p0[1] + t * (p1[1] - p0[1]),
                    p0[2] + t * (p1[2] - p0[2]) - 4.0 * sag * t * (1.0 - t)))
    return out


def _eye_points():
    """Every camera eye this scene ships (presets + mise-en-scene), for the keep-out test."""
    return [tuple(v["eye"]) for v in build_views().values()]


# --- 04-B : gravel masked off the lawn onto the trail polygon --------------
def trail_tiles(x0, y0, x1, y1):
    """Axis-aligned tiles **inscribed in the trail band** and clipped to the region.

    `scatter_debris` scatters uniformly in an AABB and has no mask hook, so the ground_kit
    field request (`region` x -12..-2.40, y -3..1, 38.4 m2) put ~150 gravel stones on the
    **lawn** as well as on the trail - defect `04-B`. An AABB of half-side `a` fits inside a
    strip of half width `h` at bearing `th` iff `a * (|sin th| + |cos th|) <= h`, so the tiles
    below are inside the trail polygon **by construction** and the mask is provable on the
    CPU (`verge_selfcheck` (5)) rather than judged by eye on a render.
    """
    pa = PARAMS["path"]
    hw = pa["width"] * (1.0 - pa["width_jit"]) / 2.0     # conservative half width
    out = []
    for pts in (pa["upper"], pa["lower"]):
        for n in range(len(pts) - 1):
            (xa, ya), (xb, yb) = pts[n], pts[n + 1]
            L = math.hypot(xb - xa, yb - ya)
            if L <= 1e-6:
                continue
            ux, uy = (xb - xa) / L, (yb - ya) / L
            a = hw / (abs(ux) + abs(uy))                 # inscribed half side
            k, t = 0, a
            while t <= L - a + 1e-6:
                cx, cy = xa + t * ux, ya + t * uy
                tx0, ty0, tx1, ty1 = cx - a, cy - a, cx + a, cy + a
                cx0, cy0 = max(tx0, min(x0, x1)), max(ty0, min(y0, y1))
                cx1, cy1 = min(tx1, max(x0, x1)), min(ty1, max(y0, y1))
                if cx1 - cx0 > 0.12 and cy1 - cy0 > 0.12:
                    out.append((cx0, cy0, cx1, cy1))
                t += 2.0 * a
                k += 1
    return out


# ===========================================================================
# [D3] [W3 S04-1] verge_selfcheck - the R-1 registry print.
#   Spec §6.2 names `verge_selfcheck` as 04's own gate, so the name survives the rebuild and
#   the content is re-derived from the new geometry. Runs with no Isaac, no GPU.
# ===========================================================================
def _hazard_registry():
    """Re-derive the hazard/drop registry from the geometry that is actually built."""
    st = PARAMS["stairs"]
    steps = sc._stair_steps(st["x0"], 0.0, 0.0, 0, st["z_top"], RISERS, TREADS)
    return dict(kind="T4 irregular-riser sleeper stair",
                n_risers=len(RISERS), run=STAIR_RUN, drop=STAIR_DROP,
                top_edge_x=st["x0"], top_edge_z=st["z_top"],
                corridor_half=st["y1"], steps=steps,
                riser_min=min(RISERS), riser_max=max(RISERS),
                lower_z=PARAMS["lower"]["z_top"])


def verge_selfcheck(verbose=True):
    """[W3 S04-1] R-1 registry print + the new ground layer's own gates.

    (1) hazard/drop registry re-derived from RISERS/TREADS (unchanged by this WP - printed so
        the claim is a measurement, not an assertion).
    (2) walk intrusion: min clearance to a walked surface over **every** new prim family.
    (3) rope handline: R04-1 evidence - offsets, pitch, twin-arm parity, camera keep-out.
    (4) grounding: nothing floats on the 0.261 grade.
    (5) 04-B gravel mask: every scatter tile inside the trail polygon.
    (6) R04-2 seasonal audit, element by element.
    Returns: (ok, diag)
    """
    reg = _hazard_registry()
    lobes = list(litter_lobes())
    cards = list(leaf_cards())
    tufts = list(tuft_instances())
    trunks = list(trunk_instances())
    posts = list(rope_posts())
    rp = PARAMS["rope"]
    eyes = _eye_points()

    # (2) walk intrusion
    c_lobe = min([_walk_support_clear(px, py, rx, ry)
                  for _i, px, py, rx, ry, _s in lobes] or [9.9])
    c_card = min([walk_clear(px, py) for _i, px, py, *_r in cards] or [9.9])
    _hw = {t[0]: t[3] for t in TUFTS04}
    c_tuft = min([walk_clear(px, py) - _hw[rel] * (h / nat)
                  for _i, px, py, rel, nat, _z, h, _y in tufts] or [9.9])
    c_trunk = min([walk_clear(px, py) - 0.16
                   for _i, px, py, _r, _n, _h, _b in trunks] or [9.9])
    c_post = min([walk_clear(px, py) - rp["post_r"]
                  for _s, _k, px, py, _g in posts] or [9.9])

    # (3) rope
    pitch = rope_pitch()
    d_eye = min(math.hypot(px - e[0], py - e[1])
                for _s, _k, px, py, _g in posts for e in eyes)
    n_span = len(posts) // 2 - 1
    # (5) gravel mask
    g = PARAMS["gkit"]
    tiles = trail_tiles(g["x0"], g["y0"], g["scatter_x1"], g["y1"])
    pa = PARAMS["path"]
    hw_out = pa["width"] * (1.0 + pa["width_jit"]) / 2.0
    tile_off = 0.0
    for (a0, b0, a1, b1) in tiles:
        for cx, cy in ((a0, b0), (a1, b0), (a0, b1), (a1, b1)):
            tile_off = max(tile_off, trail_dist(cx, cy) - hw_out)

    ok = (c_lobe >= 0.0 and c_card >= 0.0 and c_tuft >= 0.0 and c_trunk >= 0.0
          and c_post >= 0.0 and d_eye >= rp["eye_keepout"]
          and pitch <= 1.80 and tile_off <= 0.0 and len(tiles) > 0)

    if verbose:
        print("=" * 72)
        print("scene04 [W3 S04-1] R-1 레지스트리 + 지면층 자기검산 (부팅 0 · GPU 0)")
        print("=" * 72)
        print("[1] 위험/낙차 레지스트리 — 이번 WP 에서 이동 0 (재유도값)")
        print(f"    유형          {reg['kind']}")
        print(f"    단수/런/낙차  {reg['n_risers']}단 · run {reg['run']:.3f} · "
              f"drop {reg['drop']:.3f} (라이저 {reg['riser_min']:.2f}~"
              f"{reg['riser_max']:.2f})")
        print(f"    낙차 시작선   x={reg['top_edge_x']:.3f} · z={reg['top_edge_z']:.3f}"
              f" → 하부 z={reg['lower_z']:.3f}")
        print(f"    보행 회랑     |y| ≤ {reg['corridor_half']:.2f} · "
              f"답면 상단 z {', '.join(f'{s[2]:.3f}' for s in reg['steps'])}")
        print("[2] 신설 프림의 보행면 침범 (음수면 FAIL)")
        print(f"    낙엽 로브     {len(lobes):4d}매  min clear {c_lobe:+.3f} m")
        print(f"    낙엽 카드     {len(cards):4d}개  min clear {c_card:+.3f} m")
        print(f"    초지 포기     {len(tufts):4d}주  min clear {c_tuft:+.3f} m")
        print(f"    나목 줄기     {len(trunks):4d}주  min clear {c_trunk:+.3f} m")
        print(f"    로프 기둥     {len(posts):4d}본  min clear {c_post:+.3f} m")
        print("[3] 로프 난간 — R04-1: 난간(가드) 아님 · 드레싱")
        print(f"    측당 {len(posts) // 2}본 · 경간 {n_span}개 · 실현 피치 "
              f"{pitch:.3f} m ≤ 1.80 [법·인접형식] · 지름 "
              f"{2 * rp['post_r']:.3f} m ≥ 0.07 [법·인접형식]")
        print(f"    노출고 {rp['post_h']:.2f} m (KNPS-RAIL 로프 n=243 중앙값 1.00 "
              f"[데이터·등급B]) · 로프 Ø{2 * rp['rope_r']:.3f} [추정] · "
              f"새그 {rp['sag']:.3f}×경간")
        print(f"    보행 중심선 이격 {rp['offset']:.2f} m > 회랑 반폭 "
              f"{STAIR_HALF:.2f} · 트림 1.15 · 답로 반폭 {TRAIL_HALF:.2f}")
        print(f"    카메라 최근접 {d_eye:.3f} m ≥ 킵아웃 {rp['eye_keepout']:.2f} "
              f"(프리셋+연출 {len(eyes)}대)")
        print("    · 강성 레일 0 · 인필 0 · 발끝막이 0 — 단일 현수 로프뿐")
        print(f"    · 낙차선(x {reg['top_edge_x']:.2f}~{reg['run']:.2f}, "
              f"|y| ≤ {reg['corridor_half']:.2f})을 가로지르는 부재 0")
        print("    · **양팔 동시 시공**: hazard_stairs=True/False 모두에 동일 건설 "
              "→ 난간 유무가 라벨 정보를 0 비트 운반")
        print("    ⇒ 네거티브 장애물 라벨 불변: T4 침목 계단 낙차 "
              f"{reg['drop']:.2f} m")
        print("[4] 접지 — 기둥 매입 "
              f"{rp['post_embed']:.3f} m > 구배 {abs(slope_grade(1.0)):.3f}"
              f"×지름 {2 * rp['post_r']:.3f} = "
              f"{abs(slope_grade(1.0)) * 2 * rp['post_r']:.4f} m")
        print(f"[5] 04-B 자갈 마스킹 — 타일 {len(tiles)}개 · 답로 밖 최대 "
              f"{tile_off:+.3f} m (≤0 이면 잔디 유출 0)")
        print("[6] R04-2 계절 감사 — 씬 고정 = 늦가을/낙엽")
        for row in seasonal_audit():
            print(f"    {row}")
        print(f"판정: {'OK' if ok else 'FAIL'}")
        print("=" * 72)
    return ok, dict(lobes=len(lobes), cards=len(cards), tufts=len(tufts),
                    trunks=len(trunks), posts=len(posts), pitch=pitch,
                    d_eye=d_eye, tiles=len(tiles), tile_off=tile_off,
                    clear=min(c_lobe, c_card, c_tuft, c_trunk, c_post))


def seasonal_audit():
    """[R04-2] Per-element seasonal verdict. Judged on **texture pixels**, never on a name -
    the convention `Japanese_Cherry` was deleted under (`scene_common.VEG_TREES`)."""
    return [
        "지면 베이스   leaf_ground(낙엽 지면) — 구 grass(녹색 98.25 %) 결합 해제 ✓",
        "낙엽 로브     leaf_ground + 웜 틴트 — 계절 일치 ✓",
        "낙엽 카드     VEG_DEBRIS 5종(마른 낙엽) — 늦가을 고정으로 적법화 ✓",
        "초지 포기     Grass_Short_A/B (green 0.537 · orange 0.177, 잔디 게이트) ✓",
        "교목 근·중경  Gray_Birch·Elm_Sapling **잎-off** "
        "(래퍼 레이어 — 인스턴싱 프로토타입에서 leaves 제거 검증; "
        "GT-126 Lombardy_Poplar 은퇴 — 렌더에서 가지 소실 → 민둥 기둥) ✓",
        "교목 원경     Douglas_Fir(상록 침엽 — 11월 산지 혼효림, PASS종) ✓ / "
        "Shumard_Oak 배제(MASH 인스턴서 → 잎 제거 불가) ✓",
        "배경 헤지대   leaf_ground + 어두운 틴트(34 m 원경 갈색 임상) ✓",
        "관목 블롭     삭제(18프림) — 상록 녹색 돔은 늦가을 오류 ✓",
        "버지 타래     삭제(121프림) — 상동 ✓",
        "침목·목재 프롭 계절 중립(목재) — 변경 없음 ✓",
        "자갈 답면     계절 중립(마사토) — 변경 없음 ✓",
        "HDRI·태양     qwantani_noon(무운 청천) — 계절 표지 없음, 미변경 (선언) △",
    ]


# ===========================================================================
# [E] Camera presets: grid_views(gy=0.0) + 4 mise-en-scene shots.
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)
    # trail_approach: from h0.9 on the upper trail toward the stair (+X)
    views["trail_approach"] = dict(eye=[-6.0, 0.0, 0.9], tgt=[0.8, 0.0, -0.35])
    # step_detail: frames the stair better (S4-6, slightly oblique + lowered)
    views["step_detail"] = dict(eye=[-2.0, 0.6, 0.75], tgt=[1.8, 0.0, -0.55])
    # below_lookup: looking back up the stair from below (−X)
    views["below_lookup"] = dict(eye=[8.5, 0.0, 0.95], tgt=[2.0, 0.0, -0.55])
    # canopy_anchor: from h1.6 up top, the lower tree canopy sits at eye level
    views["canopy_anchor"] = dict(eye=[-2.0, -1.0, 1.6], tgt=[12.0, -1.0, 0.85])
    return views


# ===========================================================================
# [F] Scene assembly + main (__main__ only)
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. trail_approach   — 상부 길에서 계단이 사면에 접혀 단차가 모호해지는가
 2. step_detail      — 침목(목재) 라이저 vs 마사토 디딤면 대비, 단코 절단선
 3. below_lookup     — 하부에서 불규칙 단높이 9단이 읽히는가
 4. canopy_anchor    — 하부 나무 수관이 상부 눈높이에 걸리는 앵커 구도
 5. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── [v6] Run the coordinate check only, then exit (no Isaac boot needed) ──
    # [W3 S04-1] `NEGOBS_SMOKE` is accepted as an alias. The §6.1 floor runs
    #   `NEGOBS_SMOKE=1 python <scene>` on every scene a WP touched; without this alias 04
    #   would **boot Isaac and take the GPU** on what is meant to be a CPU gate.
    if (os.environ.get("NEGOBS_SELFCHECK", "0") == "1"
            or os.environ.get("NEGOBS_SMOKE", "0") == "1"):
        ok, _diag = verge_selfcheck()
        sys.exit(0 if ok else 1)

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    # ── Isaac Sim boot (SimulationApp unconditionally first - scene_common.boot) ──
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene04")
    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene04"

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def make_mtls():
        S = mp["scale"]
        M = {}
        M["dirt"] = sc.make_pbr(
            stage, "/World/Looks/Dirt", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            S["dirt_park"], tint=mp["dirt_tint"])
        M["dirt_path"] = sc.make_pbr(
            stage, "/World/Looks/DirtPath", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            S["dirt_park"], tint=PARAMS["path"]["tint"])
        # [W2 fix batch F2] Scatter pool override. Bound over each scattered rock
        #   with `strongerThanDescendants`, so the procured asset's own basecolor
        #   (linear 0.23) is replaced by a real gravel texture dulled to 0.19 -
        #   the middle of the "grey debris 0.18~0.30" convention.
        M["gk_rock"] = sc.make_pbr(
            stage, "/World/Looks/GkRock", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            # [W3 S04-1] 0.82 -> 0.62: against a lawn the scattered stones sat inside the
            #   "grey debris 0.18-0.30" convention; against a litter floor they read as white
            #   pebbles dropped on brown leaves (pilot round 1).
            0.30, tint=(0.62, 0.60, 0.57))
        M["gravel"] = sc.make_pbr(
            stage, "/World/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            S["gravel"])
        # [W3 S04-1 · R04-2] The off-path ground of a late-autumn Korean hillside is litter,
        #   not lawn. `Litter` is the floor, `LeafDrift` the deeper drift lobes; both are
        #   `leaf_ground` and differ only by tint. **Naming matters**: `_look_spec` classes a
        #   material by the last path token, and "Leaf"/"Litter" land in the `veg` class -
        #   which is *not* in `_SKIN_CLASSES`, so the ground slabs keep taking no displacement
        #   skin (they took none before either, under `Grass`) and the 6 mm lobes cannot be
        #   buried by one. That parity is deliberate, not luck.
        M["litter"] = sc.make_pbr(
            stage, "/World/Looks/LeafLitter", sc.tex_path("leaf_ground", "diff"),
            sc.tex_path("leaf_ground", "nor"),
            sc.tex_path("leaf_ground", "rough"),
            S["leaf_ground"], tint=mp["litter_tint"])
        M["drift"] = sc.make_pbr(
            stage, "/World/Looks/LeafDrift", sc.tex_path("leaf_ground", "diff"),
            sc.tex_path("leaf_ground", "nor"),
            sc.tex_path("leaf_ground", "rough"),
            S["leaf_ground"] * 0.80, tint=mp["drift_tint"])
        M["wood_dark"] = sc.make_pbr(
            stage, "/World/Looks/WoodDark", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            S["wood_dark"])
        # Constant-colour materials (tree trunk·canopy·tactile)
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        # [v5.1] 4 canopy variants (2 base colours x 2 jitters of +-5 %) - each tree gets a different pair
        #   so the same two colours do not repeat across every tree.
        M["canopy"] = []
        for i, base in enumerate((mp["canopy_a"], mp["canopy_b"])):
            for j in range(2):
                M["canopy"].append(sc.make_pbr(
                    stage, f"/World/Looks/Canopy{i}{j}",
                    diffuse_color=tint_jitter(base, 10 * i + j),
                    roughness_const=mp["canopy_rough"], specular_level=0.0))
        M["canopy_a"], M["canopy_b"] = M["canopy"][0], M["canopy"][2]
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
        M["tactile"] = sc.tactile_pbr(stage, "/World/Looks/Tactile")
        # [W3 S04-1] far-field understory band. Was the lawn texture with a green tint - a
        #   34 m-distant green wall in a leaf-off frame. Same builder, litter texture, dark tint.
        M["hedge"] = sc.make_pbr(
            stage, "/World/Looks/HedgeLeaf", sc.tex_path("leaf_ground", "diff"),
            sc.tex_path("leaf_ground", "nor"),
            sc.tex_path("leaf_ground", "rough"),
            1.2, tint=mp["hedge_tint"])
        # [W3 S04-1] `Shrub*` / `Verge*` constant-colour materials **deleted** with the 139
        #   ellipsoids they were made for (121 verge + 18 shrub-cluster blobs). Deleting the
        #   material as well as the geometry is the point: a constant-colour green left in the
        #   Looks scope is exactly how a summer tint survives a season pin.
        M["rope"] = sc.make_pbr(stage, "/World/Looks/Rope",
                                diffuse_color=mp["rope_color"],
                                roughness_const=mp["rope_rough"])
        # **Name it `...Wood`, never `...Post`.** `_look_spec` classes a material by the
        #   last path token and its keyword table puts "post" in the **metal** family
        #   (alongside rail/pole/bollard). Pilot round 1 shipped `/World/Looks/PostTimber`
        #   and rendered 12 pale plastic-looking pipes in place of weathered log posts.
        #   "wood" is the token that lands in the wood family.
        M["post"] = sc.make_pbr(stage, "/World/Looks/HandlineWood",
                                diffuse_color=mp["post_color"],
                                roughness_const=mp["post_rough"])
        M["sign_face"] = sc.make_pbr(stage, "/World/Looks/SignFace",
                                     diffuse_color=mp["sign_face"],
                                     roughness_const=0.6)
        # Tread: cue_material_break - True=gravel (decomposed granite), False=blends with the surrounding soil
        M["tread"] = M["gravel"] if cfg["cue_material_break"] else M["dirt"]
        return M

    # -------------------------------------------------------------------
    # Terrain
    # -------------------------------------------------------------------
    def _flat(prefix, d, mtl):
        sc.add_box(stage, prefix,
                   ((d["x0"] + d["x1"]) / 2.0, (d["y0"] + d["y1"]) / 2.0,
                    d["z_top"] - d["thick"] / 2.0),
                   (d["x1"] - d["x0"], d["y1"] - d["y0"], d["thick"]),
                   mtl, collider=True)

    def build_ground(M):
        """Upper flat (always). Base ground = **leaf litter** (S4-1 + W3 S04-1)."""
        # [W2-0 · P-A] Slabs ground_kit decorates — keep the displacement skin
        # off them so the +0.6..2 mm decals are not buried (spec §1.2).
        sc.skin_exclude(f"{ROOT}/UpperFlat", f"{ROOT}/ConnectU")
        _flat(f"{ROOT}/UpperFlat", PARAMS["upper"], M["litter"])

    def build_slope_zone(M):
        """Lower flat + slope (hazard on). Slope = litter base + corridor-side dirt band
        + trim strip. The stair corridor itself (y +-corridor_y) is left empty (the stair fills it)."""
        _flat(f"{ROOT}/LowerFlat", PARAMS["lower"], M["litter"])
        sl = PARAMS["slope"]
        run, drop, thk = sl["run"], sl["drop"], sl["thick"]
        cy, to, dy, fy = (sl["corridor_y"], sl["trim_out"], sl["dirt_y"],
                          sl["flank_y"])
        tov = sl["trim_over"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            gy0, gy1 = sorted((sgn * dy, sgn * fy))     # litter flank (outer)
            sc.build_slope(stage, f"{ROOT}/SlopeFlank_{tag}", sl["x0"], sl["z0"],
                           run, drop, gy0, gy1, thk, M["litter"], collider=False)
            dy0, dy1 = sorted((sgn * to, sgn * dy))     # dirt band (corridor side)
            sc.build_slope(stage, f"{ROOT}/SlopeDirt_{tag}", sl["x0"], sl["z0"],
                           run, drop, dy0, dy1, thk, M["dirt"], collider=True)
            ty0, ty1 = sorted((sgn * cy, sgn * to))     # S4-5 trim sealing strip
            sc.build_slope(stage, f"{ROOT}/SlopeTrim_{tag}", sl["x0"],
                           sl["z0"] + tov, run, drop, ty0, ty1, thk, M["dirt"],
                           collider=False)
            # [GT-126] x=0 seam crest berm. `build_slope`'s default margin runs each slab
            #   0.145 m past the top hinge, so its up-slope end stands +0.038 (+0.058 trim)
            #   proud of the z=0 flat with a 14.6° overhung end face — the "floating plate +
            #   open slot" band (step_detail / below_lookup, GT-126 audit). The three slabs
            #   above stay bit-identical (SlopeDirt is a collider); the seam is buried from
            #   the flank side instead, GT-119 s10 wedge precedent. The two crest slabs share
            #   the ridge line (x −0.12, z +0.070 > lip max +0.058) so their bodies overlap
            #   below it — no knife edge; ends dive below grade (up-slope top −0.005 at
            #   x −0.70; down-slope feathers under the flank plane from x 0.123 and meets the
            #   trim plane flush at x≈0, end x 0.66 top −0.258 < flank −0.172). |y| ≥ 0.9 —
            #   the walking corridor and every registry value untouched.
            cy0, cy1 = sorted((sgn * cy, sgn * fy))     # full flank: corridor edge → site
            sc.build_slope(stage, f"{ROOT}/SeamCrestUp_{tag}", -0.70, -0.005,
                           0.58, -0.075, cy0, cy1, 0.22, M["litter"],
                           margin=0.0, collider=False)
            sc.build_slope(stage, f"{ROOT}/SeamCrestDn_{tag}", -0.12, 0.070,
                           0.78, 0.328, cy0, cy1, 0.22, M["litter"],
                           margin=0.0, collider=False)

    def build_flat_fill(M):
        """hazard_stairs=False control: slope·stair·lower unified into a z=0 flat (litter).
        The upper flat (x <=0) is already laid by build_ground -> only x 0..lower.x1 is filled."""
        lo = PARAMS["lower"]
        x0, x1 = PARAMS["slope"]["x0"], lo["x1"]
        y0, y1 = lo["y0"], lo["y1"]
        th = PARAMS["upper"]["thick"]
        sc.add_box(stage, f"{ROOT}/FlatFill",
                   ((x0 + x1) / 2.0, (y0 + y1) / 2.0, 0.0 - th / 2.0),
                   (x1 - x0, y1 - y0, th), M["litter"], collider=True)

    def _veg_bare(prefix, rel, native, cx, cy, gz, target_h, yaw, bare):
        """Reference one vegetation USD, strip its leaves if the species allows, then instance.

        **Order is the whole trick** and it is the trap `build_tree` and `place_shrubs` both
        document: once `SetInstanceable(True)` is set the descendants live in a shared
        prototype and a per-instance `SetActive(False)` is silently ignored - the source would
        look right and the render would still be in leaf. Deactivate first, instance after.

        The registry read is `scene_common.BARE_SUBPRIMS` (public), not the private
        `_deactivate_seasonal`, so this function borrows the K4 micro-commit's **data** without
        depending on another lane's private API.
        Returns True when a real asset landed (False -> the caller falls back to blobs).
        """
        xf = sc.add_vegetation(stage, prefix, rel, (cx, cy, gz),
                               yaw_deg=yaw, target_h=target_h, native_h=native)
        if xf is None:
            return False
        VEG_TALLY[rel] = VEG_TALLY.get(rel, 0) + 1
        if bare:
            if rel not in sc.BARE_SUBPRIMS:
                VEG_TALLY["bare_wrap"] = VEG_TALLY.get("bare_wrap", 0) + 1
            # The wrapper layer has already removed the leaves above the instance boundary;
            # this loop is a **no-op for the wrapper rows** (their `rel` is not a
            # `BARE_SUBPRIMS` key) and stays only so that a future row pointing straight at a
            # source asset still gets the K4 treatment - with its known instancing limit.
            for nm in sc.BARE_SUBPRIMS.get(rel, ()):
                try:
                    p = stage.GetPrimAtPath(f"{prefix}/Asset/{nm}")
                    if p and p.IsValid() and p.SetActive(False):
                        VEG_TALLY["bare_off"] = VEG_TALLY.get("bare_off", 0) + 1
                    else:
                        VEG_TALLY["bare_miss"] = \
                            VEG_TALLY.get("bare_miss", 0) + 1
                except Exception as e:                  # never kill the scene over dressing
                    print(f"[씬][경고] 잎-off 실패 {prefix}/{nm}: {e}")
        try:
            stage.GetPrimAtPath(f"{prefix}/Asset").SetInstanceable(True)
        except Exception:
            pass
        return True

    def tree_no_stake(M, prefix, cx, cy, gz, trunk_h, slot=0, far=False):
        """[W3 S04-1] Season-pinned tree placement (R04-2 · §7 ruling 8).

        `build_tree(bare=True)` alone is not enough and the K4 commit says so in its own
        docstring: it draws the species from `VEG_TREES` by coordinate hash and only
        `Elm_Sapling` of the three bare-capable assets is in that pool, so `bare=True` yields a
        **mixed** frame - some trees leaf-off, the oaks still in full green leaf. A uniformly
        leaf-off canopy needs a species selector, and the planned K4(b) `species=` kwarg does
        not exist yet. So 04 draws from its own `TREES04` table and calls `add_vegetation`
        itself, exactly as that docstring prescribes ("...or must call `add_vegetation` itself").

        v4-B3 is preserved: no nursery stakes on a natural trail (the asset path has none, and
        the blob fallback is called with the stake dimensions driven to ~0).
        """
        pool = TREES04_FAR if far else TREES04
        rnd = random.Random((int(round(cx * 100)) * 73856093)
                            ^ (int(round(cy * 100)) * 19349663))
        wp = [t for t in pool for _ in range(t[2])
              if os.path.isfile(os.path.join(sc.VEG_DIR, t[0]))]
        if sc.LOOK_GEO and wp:
            rel, native, _w, bare = wp[rnd.randrange(len(wp))]
            # Same height convention as `build_tree`: total height = 1.60 x trunk_h with
            # +-8 % per-instance variation, so the scene's canopy-top cue is untouched.
            target = float(trunk_h) * 1.60 * rnd.uniform(0.92, 1.08)
            if _veg_bare(f"{prefix}/Veg", rel, native, cx, cy, gz, target,
                         rnd.uniform(0.0, 360.0), bare):
                return
        ca, cb = ((0, 2), (1, 3), (2, 1), (3, 0))[int(slot) % 4]
        sc.build_tree(stage, prefix, cx, cy, gz, M["wood"], M["canopy"][ca],
                      M["canopy"][cb], trunk_r=PARAMS["tree"]["trunk_r"],
                      trunk_h=trunk_h, stake_r=0.004, stake_h=0.02,
                      stake_off=0.2)

    def build_background(M):
        """Far-field closure (S4-2, always): background hedge band + tree line."""
        hh = PARAMS["bg_hedge"]["h"]
        for n, b in enumerate(PARAMS["bg_hedges"]):
            gz = _resolve_gz(b["gz"], (b["x0"] + b["x1"]) / 2.0)
            sc.build_hedge(stage, f"{ROOT}/BgHedge_{n}", b["x0"], b["y0"],
                           b["x1"], b["y1"], hh, mtl=M["hedge"], base_z=gz)
        # v4-A3: sealing the slope span (x 0..5.55) - a band tilted along the grade
        sl = PARAMS["slope"]
        for n, b in enumerate(PARAMS["bg_slope_hedges"]):
            sc.build_slope(stage, f"{ROOT}/BgSlopeHedge_{n}", sl["x0"],
                           sl["z0"] + hh, sl["run"], sl["drop"],
                           b["y0"], b["y1"], hh, M["hedge"], margin=0.0,
                           collider=True)
        # No coordinates in prim names - a negative '-' is not a legal USD identifier (director hotfix)
        for bi, b in enumerate(PARAMS["bg_trees"]):
            gz = _resolve_gz(b["gz"], b["cx"])
            # far=True lets an evergreen conifer into the backdrop mix - legitimately green in
            # late autumn, and a Korean November hillside is bare broadleaf with pine in it.
            tree_no_stake(M, f"{ROOT}/BgTree_{bi}", b["cx"], b["cy"], gz,
                          b["trunk_h"], slot=bi, far=True)

    # -------------------------------------------------------------------
    # Sleeper stair (irregular steps) + sleeper risers + anchor stakes
    # -------------------------------------------------------------------
    def build_sleeper_stairs(M):
        st = PARAMS["stairs"]
        # Solid stair (tread = decomposed granite/soil). Descends along +X from z_top=0, irregular steps.
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            riser=0.0, tread=0.0, n=0, base_z=st["base_z"], mtl=M["tread"],
            riser_list=RISERS, tread_list=TREADS, z_top=st["z_top"],
            collider=True)
        # Sleeper + anchor stakes at each step's leading edge (xb). _stair_steps reuses the step coordinates.
        steps = sc._stair_steps(st["x0"], 0.0, 0.0, 0, st["z_top"],
                                RISERS, TREADS)
        cy = (st["y0"] + st["y1"]) / 2.0
        Ly = st["y1"] - st["y0"]
        thk = st["sleeper_thick"]
        over = st["sleeper_over"]
        # [GT-126] Head sleeper. Every leading edge below carries a retaining timber, but
        #   the top riser (x=0) had none, so below_lookup reads a lit landing lip over an
        #   unlit slot — a floating board at the drop line (hazard-adjacent). Same 0.15
        #   section, sunk so its top sits 0.03 under the landing: the drop edge stays the
        #   x=0 / z=0 soil corner and no walking surface moves. Exposed face x ≤ 0.025 —
        #   the tread's heel gap, never walked. No collider — the collision set is unchanged.
        sc.add_box(stage, f"{ROOT}/Sleeper_Head",
                   (st["x0"] - thk / 2.0 + 0.025, cy, st["z_top"] - 0.165),
                   (thk, Ly, 0.27), M["wood_dark"])
        for i, (xa, xb, ztop) in enumerate(steps):
            riser_i = RISERS[i] if i < len(RISERS) else RISERS[-1]
            h = riser_i + over                       # sleeper height
            z_hi = ztop + over                       # top face = step top + 0.02
            cz = z_hi - h / 2.0
            bx = xb - thk / 2.0                      # 0.15 thick, inside the leading edge
            sc.add_box(stage, f"{ROOT}/Sleeper_{i}", (bx, cy, cz),
                       (thk, Ly, h), M["wood_dark"], collider=True)
            # 2 anchor stakes per step (both ends of the sleeper front, y +-0.8)
            scz = z_hi - st["stake_h"] / 2.0
            for sgn, ptag in ((1.0, "P"), (-1.0, "N")):
                sc.add_cylinder(
                    stage, f"{ROOT}/Stake_{i}_{ptag}",
                    (xb, sgn * st["stake_y"], scz),
                    st["stake_r"], st["stake_h"], M["wood_dark"])

    # -------------------------------------------------------------------
    # Trail (dirt band) - bends gently through 3 segment boxes, 1mm proud
    # -------------------------------------------------------------------
    def build_paths(M):
        """v4-A1: each span of the centreline polyline is laid as a rotZ-rotated box.
        Segment centre = midpoint of the two nodes, length = node distance + overlap (joint
        overlap), yaw = atan2(dy, dx). A box put into build_rot_group (pivot = segment centre)
        rotates about that pivot -> a continuous meander with no staircase misalignment."""
        pa = PARAMS["path"]
        w, th, proud, ov = pa["width"], pa["thick"], pa["proud"], pa["overlap"]
        wj = pa["width_jit"]

        def _seg(prefix, pts, surf_z, seed):
            z_hi = surf_z + proud
            cz = z_hi - th / 2.0
            rnd = random.Random(seed)
            for n in range(len(pts) - 1):
                (xa, ya), (xb, yb) = pts[n], pts[n + 1]
                cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
                L = math.hypot(xb - xa, yb - ya) + ov
                yaw = math.degrees(math.atan2(yb - ya, xb - xa))
                # [v5.1] Segment width +-10 % - removes the artificial band of a uniform compacted width.
                #   Even when adjacent segments differ in width at a bend node, overlap 0.7 covers the
                #   joint, so no opening appears (width difference <=0.36 m << overlap length).
                ws = w * (1.0 + rnd.uniform(-wj, wj))
                grp = sc.build_rot_group(stage, f"{prefix}_{n}", (cx, cy), yaw)
                sc.add_box(stage, f"{grp}/Box", (cx, cy, cz), (L, ws, th),
                           M["dirt_path"], collider=True)

        _seg(f"{ROOT}/PathU", pa["upper"], PARAMS["upper"]["z_top"], 20260727)
        _seg(f"{ROOT}/PathL", pa["lower"], PARAMS["lower"]["z_top"], 51)

        # 3m dirt connector before/after the stair (soil trail landing on the grass ground)
        cn = PARAMS["connect"]
        L, hy = cn["length"], cn["half_y"]
        x_bot = PARAMS["stairs"]["x0"] + STAIR_RUN         # 5.55
        for tag, cx, surf_z in (
                ("U", PARAMS["stairs"]["x0"] - L / 2.0, PARAMS["upper"]["z_top"]),
                ("L", x_bot + L / 2.0, PARAMS["lower"]["z_top"])):
            cz = (surf_z + proud) - th / 2.0
            sc.add_box(stage, f"{ROOT}/Connect{tag}", (cx, 0.0, cz),
                       (L, 2 * hy, th), M["dirt_path"], collider=True)

    # -------------------------------------------------------------------
    # Nature (trees·shrubs·benches)
    # -------------------------------------------------------------------
    def build_verge(M):
        """[W3 S04-1] The G4 ground layer, in place of the deleted ellipsoid rows.

        Four families, all laid against the **walk centreline** (see [D2]):
          (a) drift lobes  - CB-2 DEC-1 `build_blot`, one Mesh each, never a rectangle,
                             `z_fn` seats every vertex on the local grade so no lobe end
                             floats or buries on the 14.6 deg slope;
          (b) leaf cards   - real 3-D leaf assets, the relief that stops the floor reading
                             as lino (the exact defect `VEG_DEBRIS`'s own comment records);
          (c) turf tufts   - `Grass_Short_A/B`, procured for this deletion, never wired;
          (d) bare trunks  - the G4 signature, leaf-off by species table.
        Returns a count dict for the assembly print.
        """
        lt = PARAMS["litter"]
        kit = gk.kit_from_scene_common(sc, stage)
        gfn = (lambda x, y: ground_z(x))
        n_lobe = 0
        for i, cx, cy, rx, ry, seed in litter_lobes():
            gk.build_blot(kit, f"{ROOT}/Drift_{i}", cx, cy, rx, ry, M["drift"],
                          n=int(lt["n"]), rough=float(lt["rough"]), seed=seed,
                          z=0.0, proud=float(lt["proud"]), z_fn=gfn)
            n_lobe += 1
        # v4-D11's four leaf piles: same sites, rectangles -> lobes.
        lf = PARAMS["leaf"]
        for i, (lx, ly, _gzs) in enumerate(PARAMS["leaf_piles"]):
            gk.build_blot(kit, f"{ROOT}/LeafPile_{i}", lx, ly, lf["rx"],
                          lf["ry"], M["drift"], n=int(lf["n"]),
                          rough=float(lf["rough"]), seed=int(lf["seed"]) + i,
                          z=0.0, proud=float(lf["proud"]), z_fn=gfn)
        n_card = 0
        for i, px, py, rel, s, yaw, tilt in leaf_cards():
            if sc.add_vegetation(stage, f"{ROOT}/LeafCard_{i}", rel,
                                 (px, py, ground_z(px)), yaw_deg=yaw,
                                 tilt_deg=tilt, scale_mul=s) is not None:
                try:
                    stage.GetPrimAtPath(
                        f"{ROOT}/LeafCard_{i}/Asset").SetInstanceable(True)
                except Exception:
                    pass
                n_card += 1
        n_tuft = 0
        for i, px, py, rel, native, zmin, h, yaw in tuft_instances():
            s = h / native
            # `zmin` is the asset's depth below its own origin; lifting by it puts the patch
            # bottom exactly on the ground (the defect `place_shrubs` documents at 41 cm on
            # Rhododendron). The litter lobes' 6 mm then hide the seam.
            if sc.add_vegetation(stage, f"{ROOT}/Tuft_{i}", rel,
                                 (px, py, ground_z(px) + zmin * s),
                                 yaw_deg=yaw, scale_mul=s) is not None:
                try:
                    stage.GetPrimAtPath(
                        f"{ROOT}/Tuft_{i}/Asset").SetInstanceable(True)
                except Exception:
                    pass
                n_tuft += 1
        n_trunk = 0
        for i, px, py, rel, native, h, bare in trunk_instances():
            if _veg_bare(f"{ROOT}/Trunk_{i}", rel, native, px, py,
                         ground_z(px), h, (i * 47.0) % 360.0, bare):
                n_trunk += 1
            else:                                   # blob fallback (assets absent)
                tree_no_stake(M, f"{ROOT}/Trunk_{i}", px, py, ground_z(px),
                              h / 1.6, slot=i)
                n_trunk += 1
        return dict(lobe=n_lobe, card=n_card, tuft=n_tuft, trunk=n_trunk)

    def build_handline(M):
        """[W3 S04-1 · K4(c) · R04-1] Rope-on-timber-post handline — **dressing, not a guard**.

        Written **lift-ready** for `props_kit`: the only scene coupling is the centreline and
        the ground function, both already values (`rope_posts` / `ground_z`), so lifting it is
        a signature change (`line, ground_fn, spec`) and no logic change. Lane 1 may take it.

        Why it is not a guard, in construction rather than in prose:
          · no rigid rail, no infill, no toe board - one Ø18 mm catenary rope per span;
          · it stands 1.35 m off the walk centreline, outboard of the corridor half width
            0.90, of the trim strip 1.15 and of the trail half width 0.99, so it neither
            narrows the walking band nor stands between the walker and the drop;
          · nothing crosses the drop edge (x 0..5.55, |y| <= 0.90);
          · **it is built in both hazard arms**, so its presence carries zero bits about the
            negative-obstacle label. That is the property R04-1 actually needs; the rest is
            description.
        """
        rp = PARAMS["rope"]
        ties = {}
        n_post = 0
        for side, k, px, py, gz in rope_posts():
            tag = "P" if side > 0 else "N"
            rnd = random.Random(40451 + k * 31 + (0 if side > 0 else 7))
            h = rp["post_h"] * (1.0 + rnd.uniform(-rp["post_jit"],
                                                  rp["post_jit"]))
            total = h + rp["post_embed"]
            sc.add_cylinder(stage, f"{ROOT}/RopePost_{tag}_{k}",
                            (px, py, gz + h - total / 2.0),
                            rp["post_r"], total, M["post"], collider=True)
            ties[(tag, k)] = (px, py, gz + h - rp["tie_drop"])
            n_post += 1
        n_seg = 0
        n_k = max(k for _t, k in ties)
        for tag in ("P", "N"):
            for k in range(n_k):
                pts = rope_span_points(ties[(tag, k)], ties[(tag, k + 1)])
                for j in range(len(pts) - 1):
                    a, b = pts[j], pts[j + 1]
                    d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
                    L = math.sqrt(sum(v * v for v in d)) or 1e-6
                    ux, uy, uz = d[0] / L, d[1] / L, d[2] / L
                    # `add_cylinder` authors [translate, rotateY, rotateX]; under the USD
                    # row-vector convention points apply in reverse (rotX -> rotY -> translate),
                    # so a local +Z axis maps to (cos a sin b, -sin a, cos a cos b). Inverting
                    # that gives the two angles below - one prim per segment, no pivot group.
                    ax = math.degrees(math.asin(max(-1.0, min(1.0, -uy))))
                    by = math.degrees(math.atan2(ux, uz))
                    sc.add_cylinder(
                        stage, f"{ROOT}/RopeSpan_{tag}_{k}_{j}",
                        ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0,
                         (a[2] + b[2]) / 2.0),
                        rp["rope_r"], L, M["rope"], rotY=by, rotX=ax)
                    n_seg += 1
        return dict(post=n_post, span=n_seg)

    def build_nature(M):
        for ti, spec in enumerate(PARAMS["trees"]):
            gz = _resolve_gz(spec["gz"], spec["cx"])
            tree_no_stake(M, f"{ROOT}/Tree_{spec['name']}", spec["cx"],
                          spec["cy"], gz, spec["trunk_h"], slot=ti + 1)
        for n, spec in enumerate(PARAMS["trees_extra"]):        # v4-D9
            gz = _resolve_gz(spec["gz"], spec["cx"])
            tree_no_stake(M, f"{ROOT}/TreeX_{n}", spec["cx"], spec["cy"], gz,
                          spec["trunk_h"], slot=n + 2, far=(abs(spec["cx"]) > 16.0))
        # [W3 S04-1] The 6 shrub clusters (18 flattened ellipsoids) are **deleted**. They are
        #   the same "moss-green blob" family as the verge rows `tonglam_v2` failed the scene
        #   on, and G4 has no shrub dome anywhere - a late-autumn hillside understory is litter,
        #   bare twigs and the occasional turf patch. The area they occupied is now covered by
        #   the drift-lobe bands and tuft clumps of `build_verge`.
        # v4-D4: 5 benches
        for n, (bx, by, gz_spec, yaw) in enumerate(PARAMS["benches"]):
            gz = _resolve_gz(gz_spec, bx)
            sc.build_bench(stage, f"{ROOT}/Bench_{n}", bx, by, gz,
                           M["wood_dark"], yaw=yaw)

    def build_park_props(M):
        """v4-D1/D2/D5/D6/D11 - man-made props that make it read as a 'park trail'."""
        # D1 wooden signpost (post + 2 direction arms on different bearings)
        sp = PARAMS["signpost"]
        gz = _resolve_gz(0.0, sp["cx"])
        sc.add_cylinder(stage, f"{ROOT}/SignPost/Post",
                        (sp["cx"], sp["cy"], gz + sp["post_h"] / 2.0),
                        sp["post_r"], sp["post_h"], M["wood_dark"],
                        collider=True)
        for k, (az, yaw) in enumerate(sp["arms"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/SignPost/Arm_{k}",
                                     (sp["cx"], sp["cy"]), yaw)
            sc.add_box(stage, f"{grp}/Box",
                       (sp["cx"] + sp["arm_off"], sp["cy"], gz + az),
                       sp["arm"], M["wood_dark"])
        # D2 information map board
        bo = PARAMS["board"]
        bz = _resolve_gz(0.0, bo["cx"])
        zc = (bo["z0"] + bo["z1"]) / 2.0
        sc.add_box(stage, f"{ROOT}/Board/Panel", (bo["cx"], bo["cy"], bz + zc),
                   (bo["thick"], bo["width"], bo["z1"] - bo["z0"]),
                   M["wood_dark"])
        sc.add_box(stage, f"{ROOT}/Board/Face",
                   (bo["cx"] - bo["thick"] / 2.0 - 0.006, bo["cy"], bz + zc),
                   (0.012, bo["width"] - 0.18, (bo["z1"] - bo["z0"]) - 0.14),
                   M["sign_face"])
        for tag, sgn in (("A", -1.0), ("B", 1.0)):
            sc.add_cylinder(stage, f"{ROOT}/Board/Post_{tag}",
                            (bo["cx"], bo["cy"] + sgn * (bo["width"] / 2.0
                                                         - 0.12),
                             bz + bo["z1"] / 2.0),
                            bo["post_r"], bo["z1"], M["wood_dark"],
                            collider=True)
        # D5 3 bins
        bn = PARAMS["bin_spec"]
        for n, (bx, by, gz_spec) in enumerate(PARAMS["bins"]):
            bzz = _resolve_gz(gz_spec, bx)
            sc.add_cylinder(stage, f"{ROOT}/Bin_{n}/Body",
                            (bx, by, bzz + bn["h"] / 2.0), bn["r"], bn["h"],
                            M["wood_dark"], collider=True)
            sc.add_cylinder(stage, f"{ROOT}/Bin_{n}/Rim",
                            (bx, by, bzz + bn["h"] + 0.02), bn["r"] * 1.1,
                            0.04, M["wood_dark"])
        # D6 pergola/shelter
        pg = PARAMS["pergola"]
        sc.build_canopy(stage, f"{ROOT}/Pergola", pg["x0"], pg["x1"],
                        pg["y0"], pg["y1"], pg["z_roof"], pg["post_r"],
                        M["wood_dark"], M["wood_dark"], roof_t=pg["roof_t"],
                        base_z=PARAMS["lower"]["z_top"])
        # D11 4 leaf piles — moved into `build_verge` as DEC-1 lobes (they were rectangles).

    # -------------------------------------------------------------------
    # cue - log handrail (railing) · tactile paving (tactile) · anti-slip (nosing)
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P11 trail_soil (spec §5.7 row 04).
    #   Runs in both hazard arms (GT-E4 twin parity).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        st = PARAMS["stairs"]
        z = PARAMS["upper"]["z_top"] + PARAMS["path"]["proud"]
        gp = gk.plan_ground(
            "trail_soil",
            region=(g["x0"], g["y0"], g["scatter_x1"], g["y1"]),
            z=z, gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene04",
            tactile=(),                 # §12.4 - natural scene, not installed
            extras_args=dict(
                wear_lane=dict(centerline=tuple(g["wear"]),
                               width=g["wear_w"]),
                edge_litter=dict(centerline=tuple(g["wear"])),
                # seams are built below (they are not constant-y lines)
                edge_break=dict(lines=[])),
            seed=4)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(wear=M["dirt"], litter=M["dirt_path"], edge_break=M["dirt"],
                  stain_dirt=M["dirt"], debris=M["gk_rock"])

        def scatter_on_trail(st_, prefix, x0, y0, x1, y1, z_, cover=0.15,
                             seed=0, max_count=0, edge_bias=0.0, pool=None,
                             mtl=None, sink=0.0, scale_jitter=(0.75, 1.25),
                             **kw):
            """[04-B] The injected scatter callback, masked onto the trail polygon.

            `plan_ground`'s field request is one AABB and `scatter_debris` has no mask hook,
            so the P11 gravel field (region 38.4 m2) was landing ~150 stones on the **lawn**
            as much as on the trail. This wrapper replaces that single call with one call per
            tile of `trail_tiles`, i.e. per axis-aligned box **inscribed in the trail band**,
            with `max_count` shared out by area. Per-area density is preserved and the lawn
            gets nothing, provably (`verge_selfcheck` (5)) rather than by eye.

            The signature is explicit rather than `**kw` on purpose: `ground_kit` decides
            whether to pass `mtl` / `sink` / `scale_jitter` by **inspecting the callback's
            parameters**, and a bare `**kw` would silently drop the `gk_rock` material
            override and the F2 burial fraction.
            """
            tiles = trail_tiles(x0, y0, x1, y1)
            if not tiles:
                return 0
            areas = [(a1 - a0) * (b1 - b0) for a0, b0, a1, b1 in tiles]
            tot = sum(areas) or 1.0
            n = 0
            for i, ((a0, b0, a1, b1), ar) in enumerate(zip(tiles, areas)):
                share = max(1, int(round(float(max_count) * ar / tot)))
                n += int(sc.scatter_debris(
                    st_, f"{prefix}_T{i}", a0, b0, a1, b1, z_, cover=cover,
                    seed=int(seed) + 7919 * i, max_count=share,
                    edge_bias=edge_bias, pool=pool, mtl=mtl, sink=sink,
                    scale_jitter=scale_jitter, **kw) or 0)
            return n

        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=scatter_on_trail)
        # ConnectU seam breaking — the dE76 18.9 boundary of the 3.0 x 6.0 m
        #   dirt landing against the grass slab (spec §5.7 / appendix A6).
        cn = PARAMS["connect"]
        x_w, hy = st["x0"] - cn["length"], cn["half_y"]
        seams = (("W", ((x_w, -hy), (x_w, hy))),
                 ("S", ((x_w, -hy), (st["x0"] - 0.05, -hy))),
                 ("N", ((x_w, hy), (st["x0"] - 0.05, hy))))
        nb = 0
        for tag, line in seams:
            nb += gk.build_edge_break(kit, f"{ROOT}/GKit/EdgeBreak_{tag}",
                                      line, z, M["dirt"])["prim_count"]
        print(f"[ground_kit] scene04 P11 · prims {res['prims']} "
              f"+ edge_break {nb} · scatter {res['instances']} · "
              f"delta_max {res['gt_delta_max']:.4f}")
        return res

    def build_cues(M):
        st = PARAMS["stairs"]
        # Log handrail line (y=+1.0): cylinder tilted along the slope profile + wooden posts
        if cfg["cue_railing"]:
            lr = PARAMS["log_rail"]
            y = lr["y"]
            x0, x1 = st["x0"], st["x0"] + STAIR_RUN
            z0 = slope_z(x0) + lr["rail_h"]          # top rail z
            z1 = slope_z(x1) + lr["rail_h"]          # bottom rail z
            L = math.hypot(x1 - x0, z0 - z1)
            ang = math.degrees(math.atan2(z0 - z1, x1 - x0))
            sc.add_cylinder(stage, f"{ROOT}/LogRail/Rail",
                            ((x0 + x1) / 2.0, y, (z0 + z1) / 2.0),
                            lr["rail_r"], L, M["wood_dark"], rotY=90.0 + ang)
            xp = x0 + lr["spacing"] / 2.0
            p = 0
            while xp <= x1 + 1e-6:
                gz = slope_z(xp)
                ph = lr["rail_h"]
                sc.add_cylinder(stage, f"{ROOT}/LogRail/Post_{p}",
                                (xp, y, gz + ph / 2.0),
                                lr["post_r"], ph, M["wood_dark"])
                xp += lr["spacing"]
                p += 1

        # Tactile paving strip: 0.3m before the top edge (unusual in a park - code path only)
        if cfg["cue_tactile"]:
            sc.build_tactile(stage, f"{ROOT}/Tactile", st["x0"] - 0.3, st["x0"],
                             st["y0"], st["y1"], M["tactile"],
                             z=PARAMS["upper"]["z_top"])

        # Anti-slip nosing strip: leading edge of every step (new cue_nosing)
        if cfg["cue_nosing"]:
            sc.build_nosing(stage, f"{ROOT}/Nosing", st["x0"], st["y0"],
                            st["y1"], 0.0, 0.0, 0, base_z=st["base_z"],
                            riser_list=RISERS, tread_list=TREADS,
                            z_top=st["z_top"])

    # ── Scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = make_mtls()
    build_ground(M)                 # upper flat (litter floor, always)
    if cfg["hazard_stairs"]:
        build_slope_zone(M)         # lower flat + slope (litter+dirt band+trim)
        build_sleeper_stairs(M)
    else:
        build_flat_fill(M)          # control: unified z=0 flat (litter)
    build_paths(M)                  # trail band + dirt connectors before/after the stair
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    build_background(M)             # far-field closure (background fence·trees, always)
    if cfg["cue_scene_dressing"]:
        build_nature(M)
        build_park_props(M)         # v4-D: park context cues as a set
        # [W3 S04-1] **Both arms.** The old code built the verge only when the slope existed;
        #   the ground layer is seated on `ground_z`, which resolves per arm, so the flat
        #   control gets the same litter floor, tufts, trunks and handline. For the handline
        #   that is not tidiness but ruling R04-1: dressing that appears only in the hazard
        #   arm *is* a label cue, whatever the report says about it.
        nv = build_verge(M)
        nh = build_handline(M)
        print(f"[씬] 지면층 — 낙엽 로브 {nv['lobe']}매 · 낙엽 카드 "
              f"{nv['card']}개 · 초지 포기 {nv['tuft']}주 · 나목 "
              f"{nv['trunk']}주")
        _sp = ", ".join(f"{os.path.splitext(k.split('/')[-1])[0]} {v}"
                        for k, v in sorted(VEG_TALLY.items())
                        if k.endswith((".usd", ".usda")))
        print(f"[씬] 수종(R04-2) — {_sp} · 잎-off(래퍼 레이어) "
              f"{VEG_TALLY.get('bare_wrap', 0)} · 잎-off(런타임) "
              f"{VEG_TALLY.get('bare_off', 0)} · 실패 "
              f"{VEG_TALLY.get('bare_miss', 0)}")
        print(f"[씬] 로프 난간(드레싱·R04-1) — 기둥 {nh['post']}본 · 로프 "
              f"세그먼트 {nh['span']}개 · 피치 {rope_pitch():.2f} m · "
              f"양팔 동시 시공")
    build_cues(M)
    # R-1: the registry print rides every run, so the claim "the hazard geometry did not move"
    #   is re-derived from the assembled scene rather than remembered from the report.
    verge_selfcheck()
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── Camera + render mode ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["trail_approach"]
    look_from(_v0["eye"], _v0["tgt"])               # start camera = mise-en-scene

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

    # ===================================================================
    # Auto capture mode (headless verification pipeline - scene_common.capture_pipeline)
    # ===================================================================
    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ===================================================================
    # GUI look check mode (default)
    # ===================================================================
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]                            # [ / ] key user offset

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene04_{ts}.png")
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
