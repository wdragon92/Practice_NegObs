# -*- coding: utf-8 -*-
"""
scene04_parktrail.py — NegObs synthetic scene 4: park sleeper stair (T4, Isaac Sim 4.5)

Spec : Docs/multi_scene_brief_v2.md §C `scene04_parktrail` (sole spec)
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
    path=dict(width=1.8, thick=0.06, proud=0.001, overlap=0.7, width_jit=0.10,
              tint=(1.10, 1.05, 0.95),
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

    # 6 shrub (hedge) clusters: (cx, cy, gz notation).
    # v4-B1: gz="slope" shrubs are axis-aligned boxes, so grade 0.261 x half-width 0.6 ->
    #   0.157 buried upslope / 0.157 floating downslope (26 % of the 0.6 height) -> switched to build_slope.
    # v4-B2: a single box with sharp corners read as a 'crate on the lawn' -> 3 overlapping slabs per cluster.
    # [v5 verdict applied / re-fix] The v4-B1+B2 combination backfired. build_slope
    #   makes a thin plate whose top face alone follows the grade, and 3 such plates at
    #   different angles rendered as a 'heap of angular boards poking out of the lawn'
    #   (step_detail right / canopy_anchor lower right / trail_approach both sides).
    #   -> The shape is replaced by **3 overlapping flattened ellipsoids (add_sphere) = a canopy blob**.
    #     · The slope correction is applied to the 'placement height' only, not to the shape (_resolve_gz).
    #       Being an axis-aligned solid of revolution, no angular cut face appears from any angle.
    #     · Grounding: the sphere centre sits at ground z + rz*(1−embed), burying the bottom by
    #       rz*embed (=25 %) -> floating and hard-edged shadows disappear.
    #     · blobs = (dx, dy, rx, ry, rz) [radius, m]. Max height ~ 1.75*rz.
    hedges=[dict(cx=-10.0, cy=3.0, gz=0.0), dict(cx=-4.0, cy=5.5, gz=0.0),
            dict(cx=1.5, cy=4.5, gz="slope"),
            dict(cx=7.0, cy=-4.5, gz="lower"), dict(cx=13.0, cy=-2.0, gz="lower"),
            dict(cx=16.0, cy=3.0, gz="lower")],
    hedge=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.72, 0.60, 0.34),
                      (0.52, 0.40, 0.50, 0.42, 0.25),
                      (-0.44, -0.36, 0.55, 0.38, 0.29))),  # (dx,dy,rx,ry,rz)

    # === [v5.1] Sleeper stair among grass - grass mound band + shrubs on both sides ===
    # The old v4-D8 `slope_understory` (4 build_slope tilted plates) is the same family as the
    #   'angular boards' shape the v5 verdict flagged on the shrubs, so it is dropped and
    #   fully replaced by a **row of flattened ellipsoids** wrapping both sides of the stair.
    #   · rowA (grass mound band) : covers the dirt shoulder (|y| 1.15~1.7) and the trim seam.
    #   · rowB/rowC (shrubs)      : close the slope into scrub beyond it.
    #
    # [v6 verdict - re-fix] rowA rendered as a **"mossy boulder field / Japanese rock garden"**.
    #   Cause = (a bulky 1.4x1.24x0.84 m smooth ellipsoid) x (grass texture uv 1.6 m/tile).
    #   A 1.6 m period normal map laid over a 1.4 m lump gives **rock-mass relief**, not leaves,
    #   and once it also exceeds knee height it reads as a boulder. As the verdict recommended:
    #   **drop the texture (constant green) + shrink + increase the count + randomise placement**.
    #     (a) Material : grass texture -> 3 constant tuft colours (bright green·dry green variants,
    #                    2.2x brighter than shrub -> separates the 'grass' and 'shrub' layers).
    #     (b) Size     : rx 0.70 -> 0.30/0.42/0.46, rz 0.42 -> 0.17/0.24/0.26
    #                    (max height 0.74 -> 0.54 m = below the knee -> reads as grassland).
    #                    Complies with the verdict's rx 0.35~0.45 (the front row is smaller still).
    #     (c) Count    : 1 row (step 0.85, 9 per side) -> **3 rows** (step 0.26/0.40/0.50).
    #                    Total 38 -> 121. Being smaller they are laid denser, so concealment improves.
    #     (d) Irregular: to kill the evenly spaced bead-string look the row spacing itself is jittered +-35 %
    #                    (jit_step) and 12 % are skipped, creating clumps and gaps.
    #                    To stop the axis-aligned ellipsoids all lying the same way,
    #                    half of them swap rx/ry.
    #   · Corridor intrusion check - tuft rows use an rx/ry swap, so the y radius must be taken as
    #     max(rx,ry) to stay on the safe side (worst case = maximum jitter combination):
    #       rowA0 inner edge = 1.42 − 0.22·0.7 − 0.30·1.18 = 0.912 > half width 0.90 ✓
    #       rowA1 inner edge = 1.92 − 0.154 − 0.42·1.18   = 1.270 ✓
    #       rowA2 inner edge = 2.45 − 0.154 − 0.46·1.18   = 1.753 ✓
    #     (the seed is deterministic, so the **measured minimum is 0.942** - verge_selfcheck (1))
    #   · Concealment: coverage of the dirt-band outline (|y|=1.30) along x is **91.7 %** (the old rowA
    #     was bulky enough to cover past the seam, but was itself a boulder field). The remaining 8 %
    #     of gaps is intentional - a little soil showing between grass clumps is normal for grassland.
    #   · Grounding condition rz·embed >= rx·grade (0.261) - invariant under scale jitter (both sides scale with s).
    #     For tuft rows a swap shrinks the x radius, so un-swapped (original rx) is the worst case:
    #       rowA0 0.17×0.5=0.085 ≥ 0.30×0.261=0.078 ✓
    #       rowA1 0.24×0.5=0.120 ≥ 0.42×0.261=0.110 ✓
    #       rowA2 0.26×0.5=0.130 ≥ 0.46×0.261=0.120 ✓
    #       rowB  0.32×0.5=0.160 ≥ 0.60×0.261=0.157 ✓ (shrub - no swap)
    #       rowC  0.30×0.5=0.150 ≥ 0.55×0.261=0.144 ✓
    #   rows: (cy, rx, ry, rz, step, x0, x1, mtl)  — mtl "tuft"|"shrub"
    verge=dict(embed=0.50, jit_pos=0.22, jit_scale=0.18, jit_step=0.35,
               skip=0.12, swap=0.5,
               rows=((1.42, 0.30, 0.30, 0.17, 0.26, -0.80, 6.40, "tuft"),
                     (1.92, 0.42, 0.36, 0.24, 0.40, -0.75, 6.35, "tuft"),
                     (2.45, 0.46, 0.40, 0.26, 0.50, -0.60, 6.25, "tuft"),
                     (3.05, 0.60, 0.66, 0.32, 1.10, -0.50, 6.20, "shrub"),
                     (3.85, 0.55, 0.62, 0.30, 1.75, -0.20, 6.00, "shrub"))),

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
    leaf_piles=[(-9.0, -2.50, 0.0), (-2.0, -0.75, 0.0), (8.0, -0.95, "lower"),
                (15.0, 0.60, "lower")],
    leaf=dict(sx=1.6, sy=1.2, h=0.05, proud=0.002),

    # Log handrail line (y=+1.0) when cue_railing is True.
    log_rail=dict(y=1.0, rail_r=0.05, post_r=0.05, rail_h=0.9, spacing=1.2),

    # --- Materials: physical size for texture_scale [m/tile] ---
    material=dict(
        # S4-4: dirt_park scale 2.0->3.0 (smaller leaf grain), desaturated tint.
        scale=dict(dirt_park=3.0, gravel=0.5, grass=1.4, wood_dark=1.0),
        dirt_tint=(0.92, 0.88, 0.80),           # eases over-saturated leaves (base soil ground)
        grass_tint=(0.55, 0.68, 0.42),          # eases tile repetition + green tint
        hedge_tint=(0.46, 0.58, 0.32),          # v4-B2 hedge band (background·understory)
        # [v5 verdict applied] Constant material for shrub blobs only. Meets verdict (c) "separate the
        #   tint further from the grass" while keeping the existing canopy albedo convention (0.025~0.06 family ·
        #   rough 1.0 · specular 0). One notch darker and less saturated than canopy_a/b so that
        #   'tree canopy' and 'ground shrub' stay distinguishable.
        shrub=(0.030, 0.047, 0.021), shrub_rough=1.0,
        # [v6 verdict] 3 constant colours for the verge grass band only - removes the direct cause of the
        #   grass texture (uv 1.6) turning into 'mossy rock' on an ellipsoid.
        #   2.2x brighter than shrub(0.030,0.047,0.021) and less saturated, giving a **grass layer > shrub
        #   layer** brightness order (it must stay darker than the grass texture's effective albedo ~ 0.11/0.14/0.08
        #   to read as a clump). The 3 = deep green·light green·dry grass.
        tuft=((0.070, 0.105, 0.042), (0.082, 0.112, 0.050),
              (0.078, 0.096, 0.038)), tuft_rough=1.0,
        # [v5.1 global convention 4] Instance tint jitter +-5 % - to add as few new materials as possible
        #   the base colour is left alone and only the variant count grows to 3 (shrub)·2 (canopy).
        tint_jitter=0.05,
        # S4-3: tree colours unified with the scene01 final values
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,   # tree trunk·stakes
        # v4-B (shared): canopy albedo raised (eases the problem of only a spherical blob silhouette showing)
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
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
# [D] Paths
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene04")

# Only the texture roles this scene uses are checked.
ASSET_ROLES = ["dirt_park", "gravel", "grass", "wood_dark", "hdri", "mdl"]


def slope_z(x):
    """Slope top-face z interpolation (x 0..run -> 0..−drop, clamped outside)."""
    sl = PARAMS["slope"]
    t = max(0.0, min(x / sl["run"], 1.0))
    return sl["z0"] - sl["drop"] * t


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
# [D2] [v6] verge instance generator - split out **so the assembler and the checker share coordinates**.
#   (Structurally this was the loop inside build_verge. The seed is deterministic, so the measured
#    minimum |y| / grounding clearance can be computed without Isaac -> verge_selfcheck)
#   yield: (px, py, cz, ax, ay, az, kind, k, row)  - cz/a* are final world values
# ===========================================================================
def verge_instances():
    vg = PARAMS["verge"]
    emb, jp, js = vg["embed"], vg["jit_pos"], vg["jit_scale"]
    jstep, skip, swap = vg["jit_step"], vg["skip"], vg["swap"]
    for r, (cy0, rx, ry, rz, step, x0, x1, kind) in enumerate(vg["rows"]):
        for sgn in (1.0, -1.0):
            k, x = 0, x0
            while x <= x1 + 1e-6:
                rnd = random.Random(int((r * 97 + k * 7919
                                         + (0 if sgn > 0 else 3571))))
                x_next = x + step * (1.0 + rnd.uniform(-jstep, jstep))
                k += 1
                # [v6] 12 % dropout - gives clumps and gaps instead of an evenly spaced bead string.
                if rnd.random() < skip:
                    x = x_next
                    continue
                px = x + rnd.uniform(-jp, jp)
                py = sgn * (cy0 + rnd.uniform(-jp, jp) * 0.7)
                s = 1.0 + rnd.uniform(-js, js)
                # [v6] So that the axis-aligned ellipsoids do not all lie the same way, half of them
                #   swap rx/ry (add_sphere has no rotation argument). **tuft rows only** -
                #   shrub rows have ry>rx, so a swap enlarges the x radius and breaks the grounding
                #   inequality (rz·embed >= rx·grade) (rowB 0.160 < 0.172).
                ax, ay = ((ry, rx) if (kind == "tuft" and rnd.random() < swap)
                          else (rx, ry))
                yield (px, py, slope_z(px) + rz * s * (1.0 - emb),
                       ax * s, ay * s, rz * s, kind, k, r)
                x = x_next


def verge_selfcheck(verbose=True):
    """[v6] Coordinate check for the reworked verge - 0 stair intrusion · 0 floating · concealment continuity.

    (1) Intrusion: is each instance's inner y edge |py| − ay greater than the stair half width 0.90 (measured minimum).
    (2) Floating: does the ellipsoid bottom on the slope grade bite below the ground.
        Highest point of the bottom (upslope tangent) z = cz − az, ground at that x = slope_z(px);
        the grade correction lifts the upslope side by rx·|dz/dx|, so clearance = az·embed − ax·0.261.
    (3) Concealment: over what % of x is the exposed dirt band (|y| 0.90~1.70) covered
        (sweeping x −0.75..6.35 on a 0.1 m grid to see whether it falls inside some instance's XY ellipse).
    Returns: (ok, diag)
    """
    sl = PARAMS["slope"]
    grade = sl["drop"] / sl["run"]
    inst = list(verge_instances())
    half = PARAMS["stairs"]["y1"]                       # 0.90
    min_gap = min(abs(p[1]) - p[4] for p in inst)
    min_ground = min(p[5] * PARAMS["verge"]["embed"] - p[3] * grade
                     for p in inst)
    # (3) dirt-band coverage (one side, y=1.30 reference line)
    xs = [(-0.75 + 0.1 * i) for i in range(72)]
    cov = 0
    for xq in xs:
        hit = False
        for px, py, _cz, ax, ay, _az, _k, _i, _r in inst:
            if py <= 0.0:
                continue
            if ((xq - px) / ax) ** 2 + ((1.30 - py) / ay) ** 2 <= 1.0:
                hit = True
                break
        cov += 1 if hit else 0
    ok = (min_gap > half) and (min_ground >= 0.0) and (cov / len(xs) > 0.90)
    if verbose:
        n_t = sum(1 for p in inst if p[6] == "tuft")
        print("=" * 64)
        print("scene04 [v6] verge(초지 밴드) 재작업 검산")
        print("=" * 64)
        print(f"  개체 수            {len(inst)} (tuft {n_t} / shrub "
              f"{len(inst) - n_t})   구 38개")
        print(f"  ① 계단 침범 여유   min(|y|−ry) = {min_gap:.3f} m "
              f"> 반폭 {half:.2f} → {'OK' if min_gap > half else 'FAIL'}")
        print(f"  ② 접지 여유        min(rz·emb − rx·구배) = {min_ground:+.4f} "
              f"→ {'OK' if min_ground >= 0 else 'FAIL'}")
        print(f"  ③ 흙띠(y=1.30) 피복 {100.0 * cov / len(xs):.1f} % "
              f"→ {'OK' if cov / len(xs) > 0.90 else 'FAIL'}")
        print(f"  최대 높이          "
              f"{max(p[2] - slope_z(p[0]) + p[5] for p in inst):.2f} m "
              f"(구 0.74 m)")
        print("=" * 64)
    return ok, dict(n=len(inst), min_gap=min_gap, min_ground=min_ground,
                    cover=cov / len(xs))


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
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── [v6] Run the coordinate check only, then exit (no Isaac boot needed) ──
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        verge_selfcheck()
        return

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
            0.30, tint=(0.82, 0.81, 0.79))
        M["gravel"] = sc.make_pbr(
            stage, "/World/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            S["gravel"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            S["grass"], tint=mp["grass_tint"])
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
        M["hedge"] = sc.make_pbr(
            stage, "/World/Looks/Hedge", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        # [v5 verdict applied] shrub blobs only (canopy convention: rough 1.0 · specular 0)
        # [v5.1] 3 variants at +-5 % jitter (per-individual variation inside a cluster)
        M["shrub_v"] = [sc.make_pbr(stage, f"/World/Looks/Shrub{i}",
                                    diffuse_color=tint_jitter(mp["shrub"],
                                                              40 + i),
                                    roughness_const=mp["shrub_rough"],
                                    specular_level=0.0) for i in range(3)]
        M["shrub"] = M["shrub_v"][0]
        # [v6 verdict] verge grass band - the old "grass texture (uv 1.6) + hedge tint" rendered as
        #   rock because of the magnified normal map -> replaced by **3 constant colours** (same as the
        #   canopy convention: rough 1.0 · specular 0). The per-instance +-5 % tint jitter is kept.
        M["verge"] = [sc.make_pbr(
            stage, f"/World/Looks/Verge{i}",
            diffuse_color=tint_jitter(c, 60 + i),
            roughness_const=mp["tuft_rough"], specular_level=0.0)
            for i, c in enumerate(mp["tuft"])]
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
        """Upper flat (always). Base ground = grass (S4-1)."""
        # [W2-0 · P-A] Slabs ground_kit decorates — keep the displacement skin
        # off them so the +0.6..2 mm decals are not buried (spec §1.2).
        sc.skin_exclude(f"{ROOT}/UpperFlat", f"{ROOT}/ConnectU")
        _flat(f"{ROOT}/UpperFlat", PARAMS["upper"], M["grass"])

    def build_slope_zone(M):
        """Lower flat + slope (hazard on). Slope = grass base + corridor-side dirt band
        + trim strip. The stair corridor itself (y +-corridor_y) is left empty (the stair fills it)."""
        _flat(f"{ROOT}/LowerFlat", PARAMS["lower"], M["grass"])
        sl = PARAMS["slope"]
        run, drop, thk = sl["run"], sl["drop"], sl["thick"]
        cy, to, dy, fy = (sl["corridor_y"], sl["trim_out"], sl["dirt_y"],
                          sl["flank_y"])
        tov = sl["trim_over"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            gy0, gy1 = sorted((sgn * dy, sgn * fy))     # grass flank (outer)
            sc.build_slope(stage, f"{ROOT}/SlopeGrass_{tag}", sl["x0"], sl["z0"],
                           run, drop, gy0, gy1, thk, M["grass"], collider=False)
            dy0, dy1 = sorted((sgn * to, sgn * dy))     # dirt band (corridor side)
            sc.build_slope(stage, f"{ROOT}/SlopeDirt_{tag}", sl["x0"], sl["z0"],
                           run, drop, dy0, dy1, thk, M["dirt"], collider=True)
            ty0, ty1 = sorted((sgn * cy, sgn * to))     # S4-5 trim sealing strip
            sc.build_slope(stage, f"{ROOT}/SlopeTrim_{tag}", sl["x0"],
                           sl["z0"] + tov, run, drop, ty0, ty1, thk, M["dirt"],
                           collider=False)

    def build_flat_fill(M):
        """hazard_stairs=False control: slope·stair·lower unified into a z=0 flat (grass).
        The upper flat (x <=0) is already laid by build_ground -> only x 0..lower.x1 is filled."""
        lo = PARAMS["lower"]
        x0, x1 = PARAMS["slope"]["x0"], lo["x1"]
        y0, y1 = lo["y0"], lo["y1"]
        th = PARAMS["upper"]["thick"]
        sc.add_box(stage, f"{ROOT}/FlatFill",
                   ((x0 + x1) / 2.0, (y0 + y1) / 2.0, 0.0 - th / 2.0),
                   (x1 - x0, y1 - y0, th), M["grass"], collider=True)

    def tree_no_stake(M, prefix, cx, cy, gz, trunk_h, slot=0):
        """v4-B3: 3 nursery-planting stakes are the most incongruous element on a natural
        trail -> neutralised by driving the stake dimensions close to 0. (Proposal: add a
        stakes=False argument to scene_common.build_tree - see the fix log)
        [v5.1] Each tree gets a different canopy material pair to break the colour repetition
        (shape·size variation is already done by scene_common.build_tree v2 from the coordinate seed)."""
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
            tree_no_stake(M, f"{ROOT}/BgTree_{bi}", b["cx"], b["cy"], gz,
                          b["trunk_h"], slot=bi)

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
        """[v5.1] Sleeper stair among grass - grass mound band + 2 shrub rows on both sides.

        Each instance is a flattened ellipsoid (add_sphere). The slope grade is reflected in
        the **placement height** only (slope_z), not in the shape - so as not to repeat the
        'tilted slab boards' the v5 verdict rejected. For grounding the centre sits at
        gz + rz(1−embed), burying the bottom by rz·embed (see the anti-floating inequality in
        the PARAMS.verge comment). Position·size jitter is deterministic from the coordinate
        seed - identical on re-run.
        [v6] Coordinate generation is split out into verge_instances() (guaranteeing the same
        coordinates as the checker)."""
        n = 0
        for px, py, cz, ax, ay, az, kind, k, r in verge_instances():
            mtl = (M["verge"][(k + r) % len(M["verge"])] if kind == "tuft"
                   else M["shrub_v"][(k + r) % len(M["shrub_v"])])
            sc.add_sphere(stage, f"{ROOT}/Verge_{n}", (px, py, cz),
                          (ax, ay, az), mtl)
            n += 1
        return n

    def build_nature(M):
        for ti, spec in enumerate(PARAMS["trees"]):
            gz = _resolve_gz(spec["gz"], spec["cx"])
            tree_no_stake(M, f"{ROOT}/Tree_{spec['name']}", spec["cx"],
                          spec["cy"], gz, spec["trunk_h"], slot=ti + 1)
        for n, spec in enumerate(PARAMS["trees_extra"]):        # v4-D9
            gz = _resolve_gz(spec["gz"], spec["cx"])
            tree_no_stake(M, f"{ROOT}/TreeX_{n}", spec["cx"], spec["cy"], gz,
                          spec["trunk_h"], slot=n + 2)
        # [v5 verdict applied / re-fix] Shrub cluster = 3 overlapping flattened ellipsoids (canopy blob).
        #   v4's 'tilted slab + 3 stacked boxes' rendered as angular boards and was dropped.
        #   An axis-aligned solid of revolution is used regardless of the slope, and the grade is
        #   reflected only by sampling ground z at each blob's centre x (_resolve_gz).
        #   -> The slope/flat branch itself disappears, so shear artefacts are eliminated at source.
        hb = PARAMS["hedge"]
        emb = hb["embed"]
        for n, spec in enumerate(PARAMS["hedges"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(hb["blobs"]):
                cx, cy = spec["cx"] + dx, spec["cy"] + dy
                gz = _resolve_gz(spec["gz"], cx)       # grade applied to the placement height only
                sc.add_sphere(stage, f"{ROOT}/Hedge_{n}_{j}",
                              (cx, cy, gz + rz * (1.0 - emb)),
                              (rx, ry, rz),
                              M["shrub_v"][(n + j) % len(M["shrub_v"])])
        # [v5.1] The v4-D8 slope understory band (4 build_slope tilted plates) is dropped ->
        #   shrub rows 2·3 of build_verge replace the same area with ellipsoids.
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
        # D11 4 leaf piles
        lf = PARAMS["leaf"]
        for n, (lx, ly, gz_spec) in enumerate(PARAMS["leaf_piles"]):
            lz = _resolve_gz(gz_spec, lx) + lf["proud"]
            sc.add_box(stage, f"{ROOT}/LeafPile_{n}",
                       (lx, ly, lz - lf["h"] / 2.0),
                       (lf["sx"], lf["sy"], lf["h"]), M["dirt"])

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
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
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
    build_ground(M)                 # upper flat (grass, always)
    if cfg["hazard_stairs"]:
        build_slope_zone(M)         # lower flat + slope (grass+dirt band+trim)
        build_sleeper_stairs(M)
    else:
        build_flat_fill(M)          # control: unified z=0 flat (grass)
    build_paths(M)                  # trail band + dirt connectors before/after the stair
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    build_background(M)             # far-field closure (background fence·trees, always)
    if cfg["cue_scene_dressing"]:
        build_nature(M)
        build_park_props(M)         # v4-D: park context cues as a set
        if cfg["hazard_stairs"]:
            # [v5.1] Grass on both sides of the stair - only when the slope exists (meaningless in the flat control)
            print(f"[씬] verge 초지·관목 {build_verge(M)}개")
    build_cues(M)
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
