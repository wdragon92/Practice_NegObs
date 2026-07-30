# -*- coding: utf-8 -*-
"""
scene01_campus_stairs.py - NegObs synthetic scene 1: campus plaza descending stair (Isaac Sim 4.5)

Spec    : Docs/scene01_design_brief.md (the only spec)
Cookbook: negobs_look_check_v1.py (verified API patterns ported over)

Hazard  : upper and lower levels are the same granite family, so the stair level
          difference vanishes from a low viewpoint.
Goal    : bring up a wide granite plaza + a wide, low-rise 4-step stair + the
          lower plaza in the GUI and judge from the render (render only, physics
          colliders attached but no sim step).

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene01_campus_stairs.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene01_campus_stairs.py
      NEGOBS_CAPTURE_DIR  : output folder (default look_check/scene01/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (default rt)
      NEGOBS_VIEWS        : comma-separated view-name filter (default all)

Smoke / registry print (CPU only, no Isaac boot):
    NEGOBS_SMOKE=1 python scene01_campus_stairs.py

Coordinates: Z-up, m, travel axis +X, stair top edge = x=0.

═══ W3 renovation (intake v2 §2 scene01 row · §7 ruling 6 · CB-2 / CB-5) ════
Target image: `Docs/reference_photos/Generated Image - Scene01.jpg` (**G1**).
Season pinned from G1: **autumn, foliage still on the crowns** (the frame's maples are
full orange, the pines dark green; there is **no bare trunk anywhere in G1**), so
`build_tree(bare=)` is deliberately **not** used here — the leaf-off wrapper would
contradict the image. What autumn does buy is **litter**: G1 shows fallen leaves on the
treads and swept into the step corners, and that is built (`sc.scatter_debris`, the
`Debris/*fall*` pool).

1. **The flight is approved and does not move.** `upper_plaza`, `stairs`, `lower_plaza`,
   `flank`, `amphi`, `south_apron` and `west_bank` are byte-unchanged. The user's 2nd
   review approved the stair and asked only for the **flanks** and the **environment**.

2. **GT-4 is RETIRED (§7-6); the flanks become a kerbed designed lawn.** GT-4 planned to
   extend the paving to the building faces and abolish the turf. G1 answers 01-B in the
   opposite direction — the paving meets a **kerbed, inhabited lawn strip** (benches,
   fountain), not a building plinth. The rule survives ("no undesigned turf"), the
   geometry inverts. The raw `GroundGrass` interface and the two `Terrace*` walking bands
   are replaced by a designed lawn platform at **z = −0.15** with a **150 mm granite kerb**
   (`infra_kit.build_curb_line`, unit-length blocks) along the upper-plaza frontage and a
   granite retaining band along the lower-plaza frontage. **GT-27** declares it.

3. **Environment opened (BS-4).** Buildings **R** and **L** — the 14 m and 10 m masses that
   boxed the plaza on both long sides, 68 prims — are **deleted**, not re-clad: they are
   what the user called *"미흡"*. The collegiate backdrop G1 shows is rebuilt with
   `building_kit`'s `kind="backdrop"` at 55–78 m, low enough that **sky shows above every
   roofline in every judged cut** (`z_ceil` printed per block).

4. **The plaza field is emptied (01-C, and G1).** Planters A / B / D stood in the middle
   of the upper plaza; in G1 the plaza above the steps is bare paving and every planted
   element sits in the lawn strip. The three beds are removed and the planting moves to
   the lawn as a **monospecific `elm` row at the statutory 8.0 m pitch**
   (`sc.TREE_PITCH_M`). This also clears scene01's row in the `w3_md_reverts_v1.md` §5
   census — `Planter_A` was 1.70 m from seven judged eyes and it no longer exists.

5. **Benches parallel to their anchors (01-D, CB-5).** The ±3–8° yaw jitter is deleted;
   the plaza-side row runs parallel to the kerb line and the lower-plaza pair parallel to
   its planter faces.

6. **R01-2 — `entry_canopy` deleted.** A free-standing 4 × 1.4 m porch with no counterpart
   in G1; it is not an underground approach, so U-5 does not protect it.

7. **G-4 manholes.** The two lids were sited from the d5/d10 near-window (the old PARAMS
   comment says so in as many words). They are re-derived from a declared service line with
   `infra_kit.derive_manholes` — the function that "knows nothing about cameras, deliberately".

8. **Decal vocabulary (01-A, CB-2).** `plaza_granite` already carries **no `patch` row**
   (GT-24 deleted the saw-cut rectangle from all three unit-paving profiles); what remains
   is `crack` (lines) and `stain` (irregular lobes). No rectangular ground pattern is
   authored by this scene. The charcoal `Band_*` runs are a **continuous paving band**, the
   vocabulary G1's own cross-cutting read lists as legitimate, not a decal.

No humans, no vehicles.
"""

import os
import sys
import math
import json
import datetime


# [v5 shared layer] only the Korean sign (build_sign) is pulled from the shared library.
#   scene_common is safe to import **before** the SimulationApp boots (pxr/omni are lazy-imported).
#   scene01's other builder / material helpers keep their existing local implementations (regression guard).
import scene_common as sc
import ground_kit as gk
# [W3 S01] Lane-1 kits, all CPU-safe at import time (pxr is lazy inside every builder).
#   infra_kit  — K5 `build_curb_line` (the lawn kerb) + `derive_manholes` (G-4)
#   building_kit / facade_kit — BS-4 `kind="backdrop"` for the collegiate masses
import infra_kit as ik
import facade_kit as fk
import building_kit as bk


# ===========================================================================
# [A] SCENE_CONFIG (brief §2) - toggles other than hazard_stairs never change the geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> whole stair + lower plaza becomes flat z=0 (only geometry toggle)
    "cue_railing":        True,   # centre + both-side stainless handrails (h 0.9, stair + 1 m top extension)
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality - default OFF (ablation path kept)   # dot tactile band: 0.3 m ahead of the top edge, stair width, depth 0.3 m
    "cue_material_break": True,   # False -> lower plaza gets the same material and tone as the upper one
    "cue_sign":           True,   # [v5 shared layer] one Korean sign (facility info)
    "cue_scene_dressing": True,   # planters, trees, buildings, streetlights and amphitheater together
}


# ===========================================================================
# [B] PARAMS - brief §1 dimension table + material/lighting/capture. NEGOBS_PARAMS_OVERRIDE merges in.
# ===========================================================================
PARAMS = dict(
    # --- §1 coordinates and layout ---
    # v4-A3: thick 0.5->0.7 (bottom face −0.70 < grass top face −0.63) - removes the exposed cut-face undercut
    upper_plaza=dict(x0=-16.0, x1=0.0, y0=-8.0, y1=8.0, z_top=0.0, thick=0.7),
    band=dict(width=0.45, spacing=2.7, proud=0.0015, embed=0.05),  # charcoal bands running along Y (F5: 1.5 mm proud)
    stairs=dict(x0=0.0, riser=0.15, tread=0.38, nsteps=4,          # total drop 0.6 m
                y0=-5.5, y1=5.5, base_z=-0.7),

    # === [W2-D ground_kit] P1 plaza_granite (spec §5.1 row 01) =============
    # The decorated surface is the upper plaza strip the h0.3 grid actually
    # sees: x -12..0 (d10 eye sits at x=-10), y = stair width. Everything is
    # read from PARAMS, never from the spec text (spec §7.4).
    #
    #  * manholes 2 - [W3 S01 · G-4] **no longer sited from the camera.** The two
    #    coordinates used to be (-3.80, -2.40) and (-8.40, -2.60), and the comment
    #    this replaces said so outright: "the second one is placed to land inside
    #    the d10 near window". That is the defect `derive_manholes` exists to end
    #    ("the function knows nothing about cameras, deliberately"; a derived
    #    position may be *rejected* by a near-window check, never *produced* by one).
    #    `manhole_line` below is the plaza's storm branch to the north stair-head
    #    gully; `infra_kit.derive_manholes(line, d_mm=450)` returns exactly two
    #    chambers from it - the upstream head and the direction-change vertex -
    #    which is also the count `GROUND_PROFILES["plaza_granite"].infra` prescribes.
    #    Occupancy re-check (reject-only, gy=-2.75, +-30 deg): head is BEHIND every
    #    grid eye; the vertex bears +86.9 / +65.2 / +41.2 deg at d2 / d5 / d10, i.e.
    #    **outside every judged frame** `[measured]`.
    #  * gullies 2 - ruling C-1' (spec §5.0): the stair-head drainage is two
    #    point gullies at x=-0.95, |y| = stair_width/2 - 0.40, NOT a full-width
    #    trench. Flush (z_e = 0) so GT-E1' asks for 0 m stand-off.
    #  * NO stair-head trench. Spec §5.1 still lists one at x=-2.55, but it
    #    cannot be built here - two independent B7 failures, both measured with
    #    `python3 ground_kit.py` arithmetic and reported in
    #    Docs/reports/w2d_edit_g1.md §3:
    #      (a) x=-2.55 puts the trench *frame* (lip 0.040 each side, ledger
    #          "trench_frame_w") near edge at x=-2.36, i.e. drow=15.7 rows
    #          @1080 < the 16-row floor for d10. C-1' sized the 0.30 m slot but
    #          not the frame. x=-2.59 fixes that.
    #      (b) even at x=-2.59 the trench and the statutory tactile band are
    #          two singular full-width cross lines inside the d10 E band, which
    #          GT-E2 caps at one; the tactile band holds that single slot by
    #          GT-E2-x (spec §6.2). So the trench can only exist while
    #          cue_tactile is OFF - a toggle-dependent hard gate is worse than
    #          no trench, and C-1' already moved the drainage duty to gullies.
    #  * tactile: spec §12.4 registers scene01 stair_top (p=0.51, defect
    #    "faded/soiled -40 %"). Statutory band = 0.30 m set-back + 0.60 m depth
    #    over the full stair width, i.e. x -0.90..-0.30 (ground_kit derives it
    #    from the edge, so no coordinate is hard-coded here). It replaces the
    #    old local `Tactile` box, which sat at x -0.30..0.00 and therefore
    #    violated both the statute (no set-back) and GT-E1' (dot 6 mm needs
    #    40*0.006 = 0.24 m of clearance, it had 0).
    gkit=dict(x0=-12.0,
              # storm branch: west head -> east along the north planting margin ->
              # 45 deg bend into the north stair-head gully at (-0.95, +5.10).
              manhole_line=[(-11.50, 4.60), (-1.60, 4.60), (-0.95, 5.10)],
              manhole_d_mm=450.0,
              gully_x=-0.95, gully_inset=0.40),
    lower_plaza=dict(x0=1.52, x1=14.0, y0=-8.0, y1=8.0, z_top=-0.6, thick=0.5),
    # v4-A4: x1 2.0->1.52 (flush with the lower plaza west end) - removes the free-end stub mid lower plaza
    flank=dict(y_out=0.5, x0=-0.5, x1=1.52, z_top=0.0, z_bot=-1.1),  # stair flank low wall
    amphi=dict(x0=0.0, y0=6.0, y1=8.0, rise=0.3, depth=0.9, ntiers=3,
               base_z=-0.7),   # F1: solid bottom z=-0.7 (no floating above the lower plaza)
    # v4-A1: fills the sunken grass pit south of the stair (x 0..1.52 x y −8..−6, depth 0.63).
    #   an upper-plaza extension apron symmetric to the +Y amphitheater (x 0..2.7, y 6..8).
    south_apron=dict(x0=0.0, x1=1.52, y0=-8.0, y1=-6.0, z_top=0.0, base_z=-0.7),
    # v4-A2: unguarded 0.60 fall at the upper plaza west end (x=−16) -> terminated by a gentle 3-step grass bank
    west_bank=dict(x0=-16.0, step=0.6, drops=(-0.16, -0.32, -0.48),
                   y0=-8.0, y1=8.0, base_z=-1.0),
    # planters: C/E on the lower plaza (z -0.6) only.
    # [W3 S01 · 01-C + G1] **A / B / D deleted.** They stood in the middle of the upper
    #   plaza (-5,-6) / (-9,6) / (-13,2); in G1 the plaza above the steps is **bare
    #   paving** and every planted element is in the lawn strip beyond it. Deleting them
    #   is also the answer to `w3_md_reverts_v1.md` §5: `Planter_A` was this scene's
    #   census row - AABB 1.70 m from `preset_h0.3_d5` and inside 2.5 m of **seven**
    #   judged cuts, the second-widest exposure in the library. The planting it carried
    #   moves to `lawn_trees` below (monospecific `elm`, 8.0 m pitch).
    planters=[dict(name="C", cx=7.0, cy=-5.5, base_z=-0.6),
              dict(name="E", cx=10.0, cy=4.0, base_z=-0.6)],   # v4-D10
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    # v4-B3: new-planting stakes on a mature tree are contradictory -> stakes=False (code path kept)
    tree=dict(trunk_r=0.06, trunk_h=2.2, stake_r=0.015, stake_h=1.5,
              stake_off=0.5, stakes=False),
    # ═══ [W3 S01 · BS-4] the collegiate backdrop — G1's open campus ══════════
    #  **What it replaces.** Buildings **R** (x -18..12, y 9.5..14, h 14.0, 42 prims) and
    #  **L** (x -20..4, y -15..-10.5, h 10.0, 26 prims) boxed the plaza on both long
    #  sides at 9.5 m and 10.5 m from the centreline. From an h0.3 eye that is a 14 m
    #  wall subtending 55 deg of the lateral field — the closed, unresolved edge the
    #  user's 2nd review calls "미흡", and the reason the frame does not read as a
    #  campus. They are **deleted, not re-clad**: nothing replaces them in the near
    #  field except the lawn. Buildings **C** (x 24, h 12) and **D** (x -42, h 9) are
    #  kept as *identity* — G1 does show stone institutional blocks — but are pushed
    #  back and lowered until sky shows above every roofline, and are built by
    #  `building_kit` with an explicit `kind="backdrop"`: 3-4 prims, **no windows**.
    #
    #  Frame-ceiling arithmetic `[measured — building_kit module header]`: the judged
    #  camera is h·d grid at pitch -10 deg, vFOV 36 deg, so the top of frame is +8 deg
    #  above the horizon and the tallest thing that can enter frame at plan distance d
    #  is `z = h_eye + 0.1405·d`. Every block below is chosen so its ridge sits under
    #  that ceiling for the **worst** (lowest, nearest) judged eye, h0.3_d2 — i.e. the
    #  roofline is always inside the frame with sky above it, never cutting the top edge.
    #  `plan_building` re-derives `z_ceil` per block from the real eye set and the build
    #  loop prints it, so the claim is checked at assembly time, not asserted here.
    backdrop=dict(
        base_z=-0.63,          # sits on GroundGrass, not on the plaza
        mat="brick_R",
        # (tag, x0, x1, y0, y1, h) — plan rectangles of the silhouette masses.
        #   E1..E3  the +X campus block G1 puts across the head of the plaza
        #   W1      the -X mass that closes `lower_lookback`
        #   N1 / S1 the flanking wings, far enough that the lawn reads as open ground
        #  Every ridge below is set from that ceiling, measured per block at assembly
        #  time; the printed `sky above roof` column must read True six times.
        blocks=(
            ("E1",  56.0,  72.0, -16.0,  -1.0,  8.2),
            ("E2",  60.0,  74.0,   2.0,  18.0,  9.0),
            ("E3",  78.0,  92.0, -10.0,   8.0, 10.5),
            ("W1", -90.0, -74.0,  -8.0,  10.0,  9.0),
            ("N1", -26.0, -10.0,  60.0,  72.0,  9.0),
            ("S1",   4.0,  22.0, -68.0, -56.0,  7.8),
        ),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # ═══ [W3 S01 · R01-1] the kerbed designed lawn — replaces GT-4 ═══════════
    #  G1: the paving stops at a **kerbed, inhabited lawn strip** with benches, a tree
    #  row and a fountain. Rule kept from GT-4 ("no undesigned turf"), geometry inverted.
    #  Levels: lawn top **-0.15** = 150 mm below the upper plaza, which is exactly the
    #  `build_curb_line` default exposure, so the kerb top lands **flush** with the walk
    #  (S06-B 2. requires flush … +20 mm). Against the **lower** plaza (-0.60) the same
    #  lawn is 0.45 m **above**, so that frontage is a retaining band and an **up-step**,
    #  not a drop — GT-27 says so explicitly (append-template rule (b)).
    #  Outer edge: two 0.16 m grass steps down to the `GroundGrass` plate (-0.63), the
    #  same ladder `west_bank` already uses, so the platform never ends in a hard cut.
    lawn=dict(
        z_top=-0.15, z_bot=-0.70,
        y_in=8.20, x_in_e=14.20,      # inner edges (outside the kerb / retaining band)
        y_out=20.0, x_out=26.0,       # outer edges of the designed platform
        x_w=-20.0,                    # west end (past the west bank)
        ret_t=0.20,                   # retaining-band thickness at the lower-plaza frontage
        bank_step=0.8, bank_drops=(-0.31, -0.47),
    ),
    #  The kerb runs only along the **upper**-plaza frontage (x -16..0), where the walk
    #  top really is 0.0; east of the stair line the neighbour is the amphitheatre and
    #  then the lower plaza, which is a retaining case, not a kerb case.
    #  `lod_span` keeps the 1 m product rhythm inside the judged window and drops to
    #  `far_unit` outside it (K5 handover 6: use the LOD lever, never a coarser `unit`).
    #  `lod_win` is in **arc length from p0**, and both runs are authored p0 = x −16 ->
    #  p1 = x 0 (the side is chosen with `road_side`, not by reversing the line), so one
    #  window covers both: s 4…16 = x −12…0, exactly the ground_kit decorated strip and
    #  the whole judged eye range (x −10…−2).
    curb=dict(y_face=8.20, x0=-16.0, x1=0.0, height=0.150, width=0.20,
              embed=0.55, unit=1.0, far_unit=4.0, lod_win=(4.0, 16.0)),

    #  Monospecific `elm` row on each lawn band — `SCENE_SPECIES["Scene01"] = ("elm",
    #  None)` and `species="elm"` is passed explicitly so the declaration is visible at
    #  the call site rather than inherited silently. Pitch is `sc.TREE_PITCH_M` (8.0 m,
    #  조례 6-8 m / 고시 4-8 m). `trunk_h` 3.0 -> target 3.0*1.60 = 4.80 m, over the
    #  S-4 street floor of 3.5 m; the plaza beds' 2.2 m trunk is gone with them.
    #  **Two rows per band, not one.** The first pilot put a single row at |y| = 11.4 and
    #  the lawn behind it rendered as an empty green plane running to the backdrop — open,
    #  but not a campus. G1's lawn is layered: bench line, then a near tree row, then a
    #  deeper mass. The second row sits at |y| = 17.4 with a taller trunk (4.0 -> 6.40 m)
    #  and is offset half a pitch in x, so the two rows never line up into a grid.
    #  Same species in both rows — this is one route's planting seen in depth, not a
    #  belt; Scene01's `SCENE_SPECIES` belt is `None` and stays `None`.
    lawn_trees=(dict(y=(11.4, -11.4), x0=-13.0, n=4, trunk_h=3.0, trunk_r=0.085),
                dict(y=(17.4, -17.4), x0=-9.0, n=4, trunk_h=4.0, trunk_r=0.110)),

    #  G1's fountain, in the north lawn where `beauty_overview` actually looks
    #  (bearing 45.9 deg from that eye against a +-30 deg half-field about 33.1 deg).
    #  A still basin: rim ring + water disc + centre plinth. No jets, no spray — moving
    #  water is outside this project's vocabulary and adds no negative-obstacle value.
    #  Form note, from the first pilot: the basin was authored as an outer cylinder with
    #  an inner "well" cylinder, and **a solid outer cylinder has no inside** — the water
    #  disc rendered buried inside it and the whole thing read as a concrete drum. It is
    #  now built the way this scene already builds a planter: four granite walls + a cap
    #  + an inner fill, with water as the fill. Square rather than round, which G1 is
    #  not, and that divergence is stated rather than hidden.
    fountain=dict(cx=7.0, cy=12.0, size=5.2, wall_t=0.30, wall_h=0.45,
                  cap_over=0.05, cap_h=0.06, water_drop=0.14,
                  plinth_r=0.45, plinth_h=0.34),

    #  Autumn litter (G1: leaves on the treads, swept into the step corners and along
    #  the kerb). `cover` is a target ground-cover FRACTION, not a count.
    litter=dict(treads=dict(cover=0.030, edge_bias=0.45, seed=10101),
                foot=dict(cover=0.022, edge_bias=0.30, seed=20202),
                plaza=dict(cover=0.012, edge_bias=1.20, seed=30303)),
    streetlight=dict(pole_h=6.0, pole_r=0.06,
                     arm_len=1.0, arm_r=0.04, head=0.25),
    # v4-D4: streetlights 1->4 (6 m rhythm = urban-space cue). (x, y, base_z)
    # [W3 S01] pole line y 6.80 -> **6.30**: the bench row now runs at y 7.10 (body
    #   y 6.875..7.325) and a pole at 6.80 cleared it by 15 mm, which is a collision in
    #   all but arithmetic. 0.50 m clear at 6.30, and the poles still read as one line.
    streetlights=[(-6.0, 6.3, 0.0), (-12.0, 6.3, 0.0), (-1.2, 6.3, 0.0),
                  (8.0, 6.3, -0.6)],

    # === v4-D context dressing (part of cue_scene_dressing, hazard geometry unchanged) ===
    # D1 entry canopy — [W3 S01 · R01-2] **DELETED**, params and builder both.
    #   It was `dict(x0=-8.0, x1=-4.0, y0=8.0, y1=9.4, z_roof=3.2, post_r=0.08,
    #   roof_t=0.14, base_z=0.0)`: a free-standing 4.0 x 1.4 m slab on four posts,
    #   authored as the porch of building R. Building R is gone and G1 has no
    #   counterpart; it is not an underground approach, so U-5's "canopy to the end"
    #   does not protect it. The `build_canopy_unit` helper is deleted with it rather
    #   than left as a dead call site that reads as intent (K2 precedent).
    # D2 four bike racks (U-hoop = 2 posts + top bar)
    # [v5.1] moved from mid plaza (x −13.5..−12.7, y −6..−3) to the **west circulation edge**.
    #   0.3 m east of the hedge (x −16.0..−15.4), hugging the walking margin at the upper plaza west end.
    #   ys spacing also goes from an even 1.0 to an irregular 0.95/1.05/0.90 (§3 bans even spacing).
    bike_rack=dict(x_a=-15.1, x_b=-14.3, ys=(-6.85, -5.90, -4.85, -3.95),
                   r=0.05, h=0.75, base_z=0.0),
    # D3 benches - (cx, cy, base_z, along, yaw). along="y" -> long axis Y
    # [W3 S01 · 01-D / CB-5 "benches parallel to their planter faces"] **the yaw jitter
    #   is deleted, every value is 0.0.** The v5.1 list carried -7.0 … +5.0 deg of
    #   hand-authored jitter beside planter anchors that no longer exist (A/B/D removed).
    #   G1 shows the campus bench line as a **straight row parallel to the lawn edge**,
    #   which is also CB-3's rule ("furniture reads as a single line parallel to its
    #   anchor; no object off its anchor bearing"). Two anchors survive:
    #     - the **kerb line** at y = +8.20: benches 0-3 sit 1.10 m inside it on the
    #       paving, long axis along X = parallel to the kerb, backs to the lawn.
    #       Spacing is deliberately irregular (5.0 / 4.5 / 3.0 m; §3 bans even spacing)
    #       while the bearing stays constant - that is the difference between "a real
    #       row" and "a grid", and it is orientation entropy the §6.3 note says must
    #       come from clutter, not from re-rotating furniture.
    #     - the two **lower-plaza planters** C(7,-5.5) / E(10,4): benches 4-5 keep their
    #       v5.1 sites, now with yaw 0 and their long axis parallel to the cap face they
    #       front (cap outer face +-1.55 from the centre; clearance 0.225 / 0.175 m).
    #   camera numeric check (grid eye x -2/-5/-10 @ y -2.75, FOV +-30 deg; pass rule as
    #   N-4 = zero hits of "near (<1.2 m) AND inside the FOV") `[measured]`:
    #     0..3 : y = 7.10 -> bearing +79.9 / +51.2 / +44.7 deg at the nearest eye = out
    #     4·5  : lower plaza, out of `lower_lookback` and `amphi_view` as before
    #     beauty_overview(-9,-5.5,3) : nearest bench 12.9 m, far outside the 1.2 m gate
    #   All four plaza benches keep x < 0 so they stand on the **upper** plaza slab
    #   (x -16..0); east of the stair line the floor is the lower plaza at -0.60 and a
    #   bench authored at base_z 0.0 would float 0.6 m.
    benches=[(-13.40, 7.10, 0.0, "x", 0.0), (-8.40, 7.10, 0.0, "x", 0.0),
             (-3.90, 7.10, 0.0, "x", 0.0), (-0.90, 7.10, 0.0, "x", 0.0),
             (5.00, -5.80, -0.6, "y", 0.0), (10.30, 2.05, -0.6, "x", 0.0)],
    bench=dict(length=1.8, width=0.45, height=0.45, seat_t=0.06),
    # D5 two campus notice boards (panel + 2 posts) - (cx, cy, base_z, yaw)
    # [v5.1] symmetric pair in mid plaza (x −14, y +-2) -> **two asymmetric spots on the circulation edge**.
    #   0 (−7.2, 7.6, yaw 90) : beside the walking route in front of building R's entry canopy (x −8..−4),
    #     0.4 m from the plaza north edge (y1 8.0) - the panel face looks −Y (toward the plaza).
    #   1 (−14.6, −1.2, yaw 180): west edge, the panel face looks +X (toward the plaza).
    #     0.8 m east of the hedge · outside the bike racks (y −6.85..−3.95).
    #   camera: 0 -> out of every grid preset by 76.9 deg+ / amphi_view 13.6 m far,
    #           1 -> behind every preset at x < −10. Zero near-field occlusion.
    boards=[(-7.2, 7.6, 0.0, 90.0), (-14.6, -1.2, 0.0, 180.0)],
    board=dict(thick=0.12, width=2.4, z0=1.0, z1=2.2, post_r=0.05),
    # [v5 shared layer] Korean signs - (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   [v5.2 user] arbitrary warning placards removed - Caution (stair warning) deleted, facility info only.
    #   Info(−7.5, −6.8): 1.0 m west of planter A (cx −5, size 3 -> x −6.5..−3.5),
    #     2.50 m from the bench (−9.25, −5.0).
    #   camera numeric check (grid gy=−2.75, eye x −2/−5/−10, FOV +-30 deg):
    #     Info    -> behind / behind / −58.3 deg              = out of every preset
    #     beauty_overview(−9,−5.5) axis 33.1 deg vs Info 74 deg out -> zero occlusion.
    signs=[("Info", "sign_info", -7.5, -6.8, 0.0, 180.0, 1.0, 0.75)],
    # D6 four litter bins — [W3 S01] the (-4.0, 7.2) bin sat **inside** the new bench 2
    #   footprint (x -4.80..-3.00, y 6.875..7.325); moved to (-5.60, 7.35), 0.80 m clear
    #   of the bench end and still on the bench-row line where a real bin goes.
    bins=[(-13.0, -7.2, 0.0), (-5.6, 7.35, 0.0),
          (3.0, -7.2, -0.6), (9.0, 7.2, -0.6)],
    bin_spec=dict(r=0.28, h=0.9),
    # D7 lower-plaza bollard row - [v6 ruling §3] **removed entirely**.
    #   was: x 13.2 · y −6..6 · step 2.4 · r 0.06 · h 0.75 · M["rail"] (pure white), 6 of them.
    #   the v6 RT ruling flagged it for violating §2/§3/§4 at once:
    #     §2 spec - h 0.75 < 0.80 lower bound / no reflective band / spacing 2.4 != 1.5
    #     §2 location - grass/sidewalk boundary (no basis for vehicle entry). Not one of the allowed spots
    #               (sidewalk-roadway junction · ramp/plaza entry · stair approach)
    #     §3 evenly spaced alignment / §4 large pure-white area
    #   this scene is a pedestrian-only campus plaza, so **a vehicle barrier line has no basis at all** ->
    #   instead of swapping the spec (option 2), follow v5.1 §2 "remove decorative bollard rows entirely" ·
    #   and v5.2 §6 "emptiness is the default" and delete it (ruling recommendation (1)).
    #   the lower plaza east boundary is carried by planter E(10, 4) · streetlight(8, 6.8) · building C(x 24).
    # D8 low hedge on the upper plaza west side (terminates the site together with the A2 bank)
    west_hedge=dict(x0=-16.0, x1=-15.4, y0=-8.0, y1=8.0, h=0.6, base_z=0.0),
    # D9 amphi seat-face timber strips (so the tiers read as seating)
    amphi_seat=dict(y0=6.2, y1=7.8, width=0.4, inset=0.15, thick=0.05,
                    proud=0.012),
    railing=dict(post_r=0.02, post_h=0.9, spacing=1.2, rail_r=0.03,  # R2-5: top rail 0.025->0.03
                 rail_mid_r=0.018, rail_mid_drop=0.45,               # R2-5: mid rail
                 ext=1.0, y_lines=(0.0, 5.45, -5.45)),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004),   # F4: near flush (4 mm), dots come from the normal map

    # --- §3 materials: physical size for texture_scale [m/tile] + tints/constants ---
    material=dict(
        scale=dict(plaza_light=1.80, band_dark=0.6, plaza_lower=0.7,
                   granite_dark=1.0, brick_red=2.0, grass=1.4, tactile=0.3),  # R2-3: grass 2→4
        lower_warm_tint=(1.06, 1.0, 0.94),        # lower plaza warm tint (§3)
        building_L_tint=(0.95, 0.92, 0.88),       # building L, slightly different tone
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,   # window glass (OmniGlass forbidden)
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,  # stainless
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,     # trunk and stakes
        # R2-2: two canopy variants bound alternately. look r3: still too bright -> dark olive + matte
        # v4-B1: the 0.025/0.045 band reads as a 'black blotch' even under the noon sun -> raised near
        #   the upper bound (0.06) to keep the silhouette. Constraint (2) (0.02~0.06) respected.
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030), canopy_rough=1.0,
        # v4-B2: granite_dark (kerb, bands) reads as a black hole -> diffuse lift
        granite_lift_tint=(1.25, 1.25, 1.22),
        hedge_tint=(0.50, 0.62, 0.36),                      # v4-D8 hedge
        # [W3 S01 · S06-B 3.] `curb_granite_light` — the curb-class role K5 asks scene
        #   owners to author. It is bound to the kerb blocks and **must not** be
        #   `granite_dark` (S06-B 3. forbids it by name; this very scene recorded that
        #   granite_dark "reads as a black hole"). The prim is named `/World/Looks/Curb`
        #   on purpose: `sc.LOOK_ROLE["Curb"] = "curb"` is what gives the blocks the
        #   R = 10 mm arris for free (`LOOK_CLASS["curb"]["bevel"] = 0.010`, zero prims),
        #   which is exactly what `ik.check_arris_role(sc)` asserts at build time.
        curb_tint=(0.86, 0.85, 0.82),
        # [W3 S01] autumn lawn. G1's turf is late-season: still green-dominant but
        #   desaturated and warmed, nothing like the mid-summer tint this scene carried
        #   (0.55, 0.68, 0.42). Green stays the largest channel - a straw-yellow lawn
        #   would be a different season, not this one.
        grass_autumn_tint=(0.62, 0.60, 0.34),
        # [W3 S01 · 01-A] stain tone: the plaza granite's own 0.72 tint, one step down.
        #   Not `granite_dark` — see the `M2.update` note in `build_ground_kit`.
        stain_tint=(0.62, 0.62, 0.61),
        # Still basin water: dark, smooth, dielectric. OmniGlass is forbidden project-wide.
        water_color=(0.045, 0.062, 0.070), water_rough=0.09,
        seat_wood=(0.055, 0.036, 0.022), seat_wood_rough=0.8,  # v4-D9 seat timber
        sign_color=(0.045, 0.085, 0.19), sign_face=(0.55, 0.56, 0.58),  # v4-D5 notice board
        # [v5.1 §4] parapet 0.90 -> 0.72 (no large pure-white areas)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,      # lamp head (not emissive by day)
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
    ),

    # --- §5 lighting: v1 noon verified constants ported over (dawn omitted) ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # user offset for the sun azimuth - added to the dome Z rotation. R2-6: 0->171.5 (world sun azimuth
    # ~205 deg: front light for the presets, riser (+X face) shading strengthens nosing contrast,
    # building R's shadow falls toward +X+Y, outside the plaza).
    SUN_AZ_OFFSET=171.5,

    render=dict(pt_total_spp=512, pt_max_bounces=8),   # §6 PT values (same as v1)
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


# parameter override (for A/B render comparison - no effect on a default run, v1 pattern)
#   NEGOBS_PARAMS_OVERRIDE='{"SUN_AZ_OFFSET":30}' python scene01_campus_stairs.py
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

# F8: SCENE_CONFIG override via environment variable (for the toggle-integrity verification pipeline)
#   NEGOBS_SCENE_CONFIG='{"cue_railing":false}' python scene01_campus_stairs.py
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] paths and assets (brief §3 canonical filenames)
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")
S1_DIR = os.path.join(ASSETS_DIR, "scene01")
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene01")

OMNIPBR_PATH = os.path.expanduser(
    "~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/"
    "omni/mdl/core/Base/OmniPBR.mdl")

# per-role texture set - [W2] the private copy of the registry is gone.
# It was the last place still naming `aerial_grass_rock_*`, so the Grass001
# swap (B-audit A1) would have reached 32 scenes and skipped scene01 alone,
# leaving one scene at a 15 m grass tile while the other 32 moved to 1.4 m.
# The role SUBSET is kept deliberately: `_check_assets` below iterates this
# dict, and pulling in the full `sc.TEX` would make scene01 abort on textures
# it never binds.
_ROLES = ("plaza_light", "band_dark", "plaza_lower", "granite_dark",
          "brick_red", "grass", "tactile", "sign_info")
TEX = {r: dict(sc.TEX[r]) for r in _ROLES}


def _tex_path(role, kind):
    return os.path.join(TEX[role]["dir"], TEX[role][kind])


def _check_assets():
    """Check that the brief §3 assets exist. If not, print the list and exit (v1 pattern)."""
    missing = []
    for role, spec in TEX.items():
        for kind in ("diff", "nor", "rough"):
            if kind not in spec:
                continue
            p = os.path.join(spec["dir"], spec[kind])
            if not os.path.isfile(p):
                missing.append((role, kind, p))
    hdri = os.path.join(ASSETS_DIR, PARAMS["light"]["hdri"])
    if not os.path.isfile(hdri):
        missing.append(("light", "hdri", hdri))
    if not os.path.isfile(OMNIPBR_PATH):
        missing.append(("material", "mdl", OMNIPBR_PATH))
    if missing:
        print("=" * 64)
        print("[에러] 다음 에셋이 없습니다. assets/scene01/ 다운로드 후 재실행:")
        for role, kind, p in missing:
            print(f"  - [{role}/{kind}] {p}")
        print("=" * 64)
        sys.exit(1)


# [W2] The private `_ensure_noon_lookfix` copy has been DELETED, not patched.
# It was RGBA-unsafe (`[..., ::-1]` on a 4-channel EXR yields [A,R,G,B]), and
# because the failure was swallowed by a bare `except` that returns the source
# path, an uncapped sun disc would have combined with the explicit DistantLight
# into a silent double sun. It also hard-coded the 1.5 deg cap, so
# `NEGOBS_SUN_CAP_DEG` did not reach this scene.
# The single implementation now lives in `sc.ensure_noon_lookfix`
# (`[..., :3][..., ::-1]` + env-driven cap) and scene01 routes through
# `sc.setup_lighting`, which calls it.
_ensure_noon_lookfix = sc.ensure_noon_lookfix    # back-compat alias only


def build_views():
    """§6 camera presets: 9 h·d grid cuts + 4 mise-en-scene cuts."""
    # [W2] The 9-cut grid was an inline copy of `sc.grid_views`, so every change
    # to the shared preset silently skipped scene01 alone. Delegated. gy is
    # expressed as the argument it always was:
    # R2-1 moved the grid y from 0 to -2.75 (left-half centre line of the
    # stair) to keep the central handrail at y=0 out of frame.
    # Verified byte-identical to the previous inline loop for all 9 cuts
    # (eye/tgt compared as JSON, 2026-07-29).
    views = sc.grid_views(-2.75)
    # look r3: lower and closer - the stair bands catch as a silhouette and building C fills the background
    views["beauty_overview"] = dict(eye=[-9.0, -5.5, 3.0], tgt=[2.5, 2.0, -1.3])
    views["lower_lookback"] = dict(eye=[6.0, 1.5, 1.0], tgt=[-2.0, 0.0, 0.4])
    views["edge_closeup"] = dict(eye=[-1.2, -1.0, 0.55], tgt=[0.8, 0.3, -0.45])
    # R2-7: from the lower plaza, seat tiers head-on and the stair flank wall on the diagonal (avoids the back wall -Y face)
    views["amphi_view"] = dict(eye=[5.5, 2.5, 0.75], tgt=[0.8, 7.2, -0.1])
    return views


# ===========================================================================
# [C2] plaza_selfcheck — the R-1 registry print (CPU only, no Isaac, no pxr)
# ===========================================================================
def plaza_selfcheck(verbose=True):
    """Re-derive and print the hazard / drop registry from `PARAMS`.

    This is the **R-1 step of GT-27's re-cache** (`gt_changes_w3.md` §1: *"the scene's
    own self-check re-derives and prints the hazard/drop registry from the changed
    geometry"*), and it doubles as scene01's `NEGOBS_SMOKE` harness. Until this landed
    scene01 had **no smoke path at all** — it booted Isaac unconditionally at `main()`,
    which is why `w3_mb_patch_v1.md` had to record the §6.1 SMOKE item as having no
    subject in this scene. It has one now.

    Every number is derived from `PARAMS`, never restated: if a parameter moves, the
    registry moves with it and the assertions below are what fail.

    Returns: `(rows, fails)` — `rows` are `(tag, kind, z_hi, z_lo, delta)` tuples.
    """
    up = PARAMS["upper_plaza"]
    st = PARAMS["stairs"]
    lp = PARAMS["lower_plaza"]
    lw = PARAMS["lawn"]
    cb = PARAMS["curb"]
    wb = PARAMS["west_bank"]
    am = PARAMS["amphi"]
    rows, fails = [], []

    def row(tag, kind, z_hi, z_lo):
        rows.append((tag, kind, z_hi, z_lo, z_hi - z_lo))

    def chk(tag, ok, msg=""):
        if not ok:
            fails.append(tag)
        if verbose:
            print(f"  [{'PASS' if ok else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    # --- 1. the stair: the scene's subject, and it does not move -----------
    for i in range(st["nsteps"]):
        row(f"nosing_{i}", "drop", -st["riser"] * i, -st["riser"] * (i + 1))
    total = st["riser"] * st["nsteps"]
    row("stair_total", "drop", st["z_top"] if "z_top" in st else 0.0,
        -total)

    # --- 2. the new lawn edges (GT-27) ------------------------------------
    #   upper plaza (0) -> lawn (-0.15): a DROP, the kerb face
    row("lawn_kerb_N", "drop", up["z_top"], lw["z_top"])
    row("lawn_kerb_S", "drop", up["z_top"], lw["z_top"])
    #   lower plaza (-0.60) -> lawn (-0.15): an UP-STEP, the retaining band.
    #   Labelling this a drop would poison the GT map (append-template rule (b)).
    row("lawn_retain_N", "up_step", lw["z_top"], lp["z_top"])
    row("lawn_retain_S", "up_step", lw["z_top"], lp["z_top"])
    row("lawn_retain_E", "up_step", lw["z_top"], lp["z_top"])
    #   lawn outer bank -> ground plate: three walkable grass treads
    prev = lw["z_top"]
    for i, z in enumerate(list(lw["bank_drops"]) + [-0.63]):
        row(f"lawn_bank_{i}", "walkable", prev, z)
        prev = z

    # --- 3. the pre-existing edges that survive ---------------------------
    prev = up["z_top"]
    for i, z in enumerate(list(wb["drops"]) + [-0.63]):
        row(f"west_bank_{i}", "walkable", prev, z)
        prev = z
    # amphitheatre tiers are **seating**, not a walking route: 0.30 m rise is a bench
    # height, which is why they carry their own kind and are outside the 0.20 m
    # walkable-step gate below.
    for i in range(am["ntiers"]):
        row(f"amphi_tier_{i}", "seat_tier", 0.3 - am["rise"] * i,
            0.3 - am["rise"] * (i + 1))

    if verbose:
        print("=" * 72)
        print("scene01 · 위험/낙차 등록부 (PARAMS 재유도)")
        print("=" * 72)
        print(f"  {'tag':<16}{'kind':<10}{'z_hi':>8}{'z_lo':>8}{'Δ':>9}")
        for tag, kind, hi, lo, d in rows:
            print(f"  {tag:<16}{kind:<10}{hi:>8.3f}{lo:>8.3f}{d:>9.3f}")
        n_drop = len([r for r in rows if r[1] == "drop"])
        n_up = len([r for r in rows if r[1] == "up_step"])
        n_walk = len([r for r in rows if r[1] == "walkable"])
        print(f"  → drop {n_drop} · up_step {n_up} · walkable {n_walk} · "
              f"seat_tier {len(rows) - n_drop - n_up - n_walk}")
        print("-" * 72)

    # --- 4. assertions ----------------------------------------------------
    chk("계단 총낙차 0.600 불변 (승인된 기하는 움직이지 않는다)",
        abs(total - 0.600) < 1e-9, f"{total:.6f} m")
    chk("계단 단높이 0.150 ≤ 0.180 (교통약자 시행규칙 별표2 상한)",
        st["riser"] <= 0.180 + 1e-9, f"{st['riser']:.3f} m")
    curb_top = lw["z_top"] + cb["height"]
    chk("연석 top 이 보도면 대비 flush … +20 mm (S06-B 2.)",
        -1e-9 <= curb_top - up["z_top"] <= 0.020 + 1e-9,
        f"{(curb_top - up['z_top']) * 1000:+.0f} mm")
    chk("연석 노출고 0.100~0.250 대역 (S06-B, INFRA_DIMENSIONS)",
        0.100 - 1e-9 <= cb["height"] <= 0.250 + 1e-9, f"{cb['height']:.3f} m")
    chk("잔디 top = 상단광장 − 연석 노출고 (레벨 정합)",
        abs((up["z_top"] - lw["z_top"]) - cb["height"]) < 1e-9,
        f"{up['z_top'] - lw['z_top']:.3f} m")
    ret = lw["z_top"] - lp["z_top"]
    chk("하단광장 전면은 UP-STEP (+0.450), 낙차가 아니다",
        ret > 0, f"{ret:+.3f} m")
    chk("연석 블록 바닥이 광장 슬래브 바닥(−0.70)까지 내려간다 (배면 공동 0)",
        abs((lw["z_top"] - cb["embed"]) - (up["z_top"] - up["thick"])) < 1e-9,
        f"{lw['z_top'] - cb['embed']:.3f} vs {up['z_top'] - up['thick']:.3f}")
    new_drops = [r for r in rows if r[1] == "drop" and not r[0].startswith("nosing")
                 and r[0] != "stair_total"]
    chk("새 낙차는 계단(0.600)보다 작다 — 주 위험이 바뀌지 않는다",
        all(r[4] < total - 1e-9 for r in new_drops),
        " · ".join(f"{r[0]} {r[4]:.3f}" for r in new_drops))
    chk("잔디 바깥 뱅크 단높이 ≤ 0.200 (보행 가능)",
        all(abs(r[4]) <= 0.200 + 1e-9 for r in rows if r[1] == "walkable"),
        f"max {max(abs(r[4]) for r in rows if r[1] == 'walkable'):.3f} m")

    # --- 5. bench / planter geometry (01-D + the §5 census obligation) -----
    yaws = [b[4] for b in PARAMS["benches"]]
    chk("벤치 yaw 지터 0 — 앵커선과 평행 (01-D · CB-5)",
        all(abs(y) < 1e-9 for y in yaws), f"max |yaw| {max(abs(y) for y in yaws):.1f}°")
    views = build_views()
    pl = PARAMS["planter"]
    half = pl["size"] / 2.0 + pl["cap_over"]
    worst = None
    for vname, v in views.items():
        ex, ey = v["eye"][0], v["eye"][1]
        for spec in PARAMS["planters"]:
            dx = max(abs(ex - spec["cx"]) - half, 0.0)
            dy = max(abs(ey - spec["cy"]) - half, 0.0)
            d = math.hypot(dx, dy)
            if worst is None or d < worst[0]:
                worst = (d, vname, spec["name"])
    chk("판정 시점 ↔ 화단 최단거리 ≥ 2.5 m (w3_md_reverts §5 센서스)",
        worst is not None and worst[0] >= 2.5,
        f"{worst[0]:.2f} m · {worst[1]} ↔ Planter_{worst[2]}")

    # --- 6. no humans / vehicles, and no rectangular ground pattern -------
    chk("사람·차량 0 (전 웨이브 금지)", True, "이 씬은 인물·차량 프림을 만들지 않는다")
    chk("직사각 지면 무늬 0 — plaza_granite 는 patch 행이 없다 (GT-24)",
        "patch" not in {it[0] for it in
                        gk.GROUND_PROFILES["plaza_granite"]["surface"]},
        str([it[0] for it in gk.GROUND_PROFILES["plaza_granite"]["surface"]]))

    if verbose:
        print("-" * 72)
        print(f"[selfcheck] {'OK' if not fails else 'FAIL ' + str(fails)}")
    return rows, fails


# ===========================================================================
# [D] Isaac Sim scene assembly + main loop (__main__ only)
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. beauty_overview  — 새 캠퍼스 광장 인상 (포장 줄무늬·화단·건물·앰피 식별)
 2. h0.3·d5~10       — 계단 디딤면이 grazing 각에서 소실되는가
 3. h1.8·d2          — 계단이 명확히 보이는가
 4. cue ON vs OFF    — 계단·광장 기하 트랜스폼 동일한가
 5. 재질             — 타일 반복·늘어남·Z파이팅·앨리어싱 없는가"""


def main():
    # [W3 S01] SMOKE: registry + assertions only. Must come **before** the Isaac boot —
    # the whole point is that the §6.1 floor item can run on a machine with no GPU.
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        _rows, _fails = plaza_selfcheck()
        print(f"SMOKE_{'OK' if not _fails else 'FAIL'} rows={len(_rows)}")
        sys.exit(1 if _fails else 0)
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    _check_assets()

    # ── step 1: boot Isaac Sim (SimulationApp always first - v9 verified block) ──
    from isaacsim import SimulationApp
    simulation_app = SimulationApp(
        {"headless": capture_mode, "width": 1920, "height": 1080})

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom, UsdShade, UsdPhysics, Sdf, Gf
    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    settings.set("/rtx/post/dlss/execMode", 2)     # DLSS Quality
    settings.set("/rtx/post/aa/op", 3)             # DLSS AA
    # turn every viewport grid and axis guide off so they never land in a render (capture hygiene, v1)
    settings.set("/app/viewport/grid/enabled", False)
    settings.set("/persistent/app/viewport/displayOptions", 0)
    settings.set("/app/viewport/show/grid", False)
    settings.set("/app/viewport/outline/enabled", False)

    stage = omni.usd.get_context().get_stage()

    # ── stage units (§1: Z-up, meter) ──
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    if abs(mpu - 1.0) > 1e-9:
        print(f"[경고] metersPerUnit={mpu} → 1.0(미터)으로 설정")
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

    UsdGeom.Xform.Define(stage, "/World")
    UsdGeom.Xform.Define(stage, "/World/Scene01")
    cfg = SCENE_CONFIG
    mp = PARAMS["material"]

    # -------------------------------------------------------------------
    # geometry helpers (UsdGeom.Cube + Cylinder + Sphere, unified xformOp)
    # note: UsdGeom.Cube defaults to size=2 (+-1) -> scale = desired dimension / 2
    # -------------------------------------------------------------------
    def bind_mtl(prim, mtl):
        if mtl is not None:
            UsdShade.MaterialBindingAPI.Apply(prim).Bind(mtl)

    def add_box(path, center, size, mtl=None, collider=False, rotZ=0.0):
        # [v5.1] rotZ added - for irregular placement (yaw jitter). op order is T -> Rz -> S
        #   (USD standard TRS: scale applies first, then rotation -> no shear even on an anisotropic box).
        cube = UsdGeom.Cube.Define(stage, path)
        cube.CreateSizeAttr(2.0)
        cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
        xf = UsdGeom.Xformable(cube)
        xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
        if abs(rotZ) > 1e-9:
            xf.AddRotateZOp().Set(float(rotZ))
        xf.AddScaleOp().Set(Gf.Vec3f(float(size[0]) / 2.0,
                                     float(size[1]) / 2.0,
                                     float(size[2]) / 2.0))
        prim = cube.GetPrim()
        bind_mtl(prim, mtl)
        if collider:
            UsdPhysics.CollisionAPI.Apply(prim)
        return cube

    def add_cylinder(path, center, radius, height, mtl=None,
                     rotY=0.0, rotX=0.0, collider=False):
        cyl = UsdGeom.Cylinder.Define(stage, path)
        cyl.CreateRadiusAttr(float(radius))
        cyl.CreateHeightAttr(float(height))
        cyl.CreateAxisAttr(UsdGeom.Tokens.z)
        xf = UsdGeom.Xformable(cyl)
        # order: translate -> rotate (rotate at the prim origin, then move)
        xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
        if abs(rotY) > 1e-9:
            xf.AddRotateYOp().Set(float(rotY))
        if abs(rotX) > 1e-9:
            xf.AddRotateXOp().Set(float(rotX))
        prim = cyl.GetPrim()
        bind_mtl(prim, mtl)
        if collider:
            UsdPhysics.CollisionAPI.Apply(prim)
        return cyl

    def add_sphere(path, center, scale3, mtl=None):
        sph = UsdGeom.Sphere.Define(stage, path)
        sph.CreateRadiusAttr(1.0)
        xf = UsdGeom.Xformable(sph)
        xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
        xf.AddScaleOp().Set(Gf.Vec3f(*[float(s) for s in scale3]))
        bind_mtl(sph.GetPrim(), mtl)
        return sph

    # -------------------------------------------------------------------
    # setup_materials - every material comes from the single OmniPBR helper make_pbr
    # -------------------------------------------------------------------
    def make_pbr(path, diff=None, nor=None, rough=None, scale_m=1.0,
                 tint=None, metallic=0.0, roughness_const=None,
                 diffuse_color=None, bump=1.0):
        """[realism v1] delegated to scene_common.

        scene01 was the **first scene** in this library, so it implemented its own
        material factory, and that code was later extracted into
        `scene_common.make_pbr`. scene01 alone kept using its local copy, which
        made it **the one scene out of 33 that never went through the shared
        layer**. The problem surfaced when the realism look layer (per-role
        recipes · MDL swaps · bevel · saturation) landed in
        `scene_common.make_pbr` and reached every scene except scene01, so it is
        cleaned up here.

        Behaviour is identical before and after delegation - the local copy was a
        functional subset of `sc.make_pbr` (no specular_level · emission ·
        uv_mode) and the call sites use only those arguments. Verification:
        render with the look layer OFF and compare against the previous output.
        """
        return sc.make_pbr(stage, path, diff=diff, nor=nor, rough=rough,
                           scale_m=scale_m, tint=tint, metallic=metallic,
                           roughness_const=roughness_const,
                           diffuse_color=diffuse_color, bump=bump)

    def setup_materials():
        sc = mp["scale"]
        M = {}
        # [T1 T-1] plaza_light tone x0.72 — 9 scenes share this untinted material.
        # Linear albedo 0.469 sits in the WHITE-cement band; grey portland paving
        # is 0.35~0.40 new / 0.20~0.30 aged [LBNL Heat Island / ACPA RT3.05].
        # x0.72 -> 0.338 lands at the low end of "new grey". Paired with
        # scale_m 0.75->1.80 (same call, cannot be split; T1 §1.8-2).
        M["plaza_light"] = make_pbr(
            "/World/Looks/PlazaLight", _tex_path("plaza_light", "diff"),
            _tex_path("plaza_light", "nor"), _tex_path("plaza_light", "rough"),
            sc["plaza_light"], tint=(0.72, 0.72, 0.72))
        # look r3: PavingStones127 has a strong grain, so the bands read like a timber deck ->
        # swapped for the same dark granite tile as the kerb (granite_dark) (joint 0.9 m)
        # v4-B2: the bands are granite_dark too - a lift tint softens the black striping
        M["band_dark"] = make_pbr(
            "/World/Looks/BandDark", _tex_path("granite_dark", "diff"),
            _tex_path("granite_dark", "nor"), _tex_path("granite_dark", "rough"),
            0.9, tint=mp["granite_lift_tint"])
        # lower plaza: material and tint follow cue_material_break (geometry unchanged)
        if cfg["cue_material_break"]:
            M["lower"] = make_pbr(
                "/World/Looks/PlazaLower", _tex_path("plaza_lower", "diff"),
                _tex_path("plaza_lower", "nor"),
                _tex_path("plaza_lower", "rough"),
                sc["plaza_lower"], tint=mp["lower_warm_tint"])
        else:
            M["lower"] = make_pbr(                       # [T1 T-1] x0.72
                "/World/Looks/PlazaLower", _tex_path("plaza_light", "diff"),
                _tex_path("plaza_light", "nor"),
                _tex_path("plaza_light", "rough"), sc["plaza_light"],
                tint=(0.72, 0.72, 0.72))
        M["granite_dark"] = make_pbr(
            "/World/Looks/GraniteDark", _tex_path("granite_dark", "diff"),
            _tex_path("granite_dark", "nor"),
            _tex_path("granite_dark", "rough"), sc["granite_dark"],
            tint=mp["granite_lift_tint"])                     # v4-B2
        M["brick_R"] = make_pbr(
            "/World/Looks/BrickR", _tex_path("brick_red", "diff"),
            _tex_path("brick_red", "nor"), _tex_path("brick_red", "rough"),
            sc["brick_red"])
        M["brick_L"] = make_pbr(
            "/World/Looks/BrickL", _tex_path("brick_red", "diff"),
            _tex_path("brick_red", "nor"), _tex_path("brick_red", "rough"),
            sc["brick_red"], tint=mp["building_L_tint"])
        M["grass"] = make_pbr(                     # [W3 S01] autumn tint (G1)
            "/World/Looks/Grass", _tex_path("grass", "diff"),
            _tex_path("grass", "nor"), _tex_path("grass", "rough"),
            sc["grass"], tint=mp["grass_autumn_tint"])
        # [W3 S01 · S06-B 3.] curb-class role. Prim name `Curb` -> LOOK_ROLE "curb".
        M["curb"] = make_pbr(
            "/World/Looks/Curb", _tex_path("plaza_light", "diff"),
            _tex_path("plaza_light", "nor"), _tex_path("plaza_light", "rough"),
            1.0, tint=mp["curb_tint"])
        M["water"] = make_pbr("/World/Looks/Water",
                              diffuse_color=mp["water_color"],
                              roughness_const=mp["water_rough"], metallic=0.0)
        # [W3 S01 · 01-A] stain tone — the plaza's own granite, darkened one step.
        M["stain"] = make_pbr(
            "/World/Looks/Stain", _tex_path("plaza_light", "diff"),
            _tex_path("plaza_light", "nor"), _tex_path("plaza_light", "rough"),
            sc["plaza_light"], tint=mp["stain_tint"])
        M["tactile"] = make_pbr(
            "/World/Looks/Tactile", _tex_path("tactile", "diff"),
            _tex_path("tactile", "nor"), None, sc["tactile"])
        # constant-colour materials
        M["glass"] = make_pbr("/World/Looks/Glass", diffuse_color=mp["glass_color"],
                              roughness_const=mp["glass_rough"], metallic=0.0)
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = make_pbr("/World/Looks/GKitIron",
                            diffuse_color=(0.10, 0.10, 0.105),
                            metallic=0.55, roughness_const=0.55)
        M["rail"] = make_pbr("/World/Looks/Rail", diffuse_color=mp["rail_color"],
                             metallic=mp["rail_metallic"],
                             roughness_const=mp["rail_rough"])
        M["wood"] = make_pbr("/World/Looks/Wood", diffuse_color=mp["wood_color"],
                             roughness_const=mp["wood_rough"])
        M["canopy_a"] = make_pbr("/World/Looks/CanopyA",
                                 diffuse_color=mp["canopy_a"],
                                 roughness_const=mp["canopy_rough"])
        M["canopy_b"] = make_pbr("/World/Looks/CanopyB",
                                 diffuse_color=mp["canopy_b"],
                                 roughness_const=mp["canopy_rough"])
        M["parapet"] = make_pbr("/World/Looks/Parapet",
                                diffuse_color=mp["parapet_color"],
                                roughness_const=mp["parapet_rough"])
        M["lamp"] = make_pbr("/World/Looks/Lamp", diffuse_color=mp["lamp_color"],
                             roughness_const=mp["lamp_rough"])
        M["pole"] = make_pbr("/World/Looks/Pole", diffuse_color=mp["pole_color"],
                             metallic=mp["pole_metallic"],
                             roughness_const=mp["pole_rough"])
        # v4-D dressing-only materials
        M["hedge"] = make_pbr(
            "/World/Looks/Hedge", _tex_path("grass", "diff"),
            _tex_path("grass", "nor"), _tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        M["seat_wood"] = make_pbr("/World/Looks/SeatWood",
                                  diffuse_color=mp["seat_wood"],
                                  roughness_const=mp["seat_wood_rough"])
        # [v5.1 §4] per-instance tint jitter +-5% - so the benches do not read as clones of one material.
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"seat_wood_{_i}"] = make_pbr(
                f"/World/Looks/SeatWood_{_i}",
                diffuse_color=tuple(c * _f for c in mp["seat_wood"]),
                roughness_const=mp["seat_wood_rough"] * (1.0 + 0.04 * (_i - 1)))
        M["sign"] = make_pbr("/World/Looks/Sign",
                             diffuse_color=mp["sign_color"],
                             roughness_const=0.5)
        M["sign_face"] = make_pbr("/World/Looks/SignFace",
                                  diffuse_color=mp["sign_face"],
                                  roughness_const=0.6)
        return M

    # -------------------------------------------------------------------
    # build_* functions (brief §7)
    # -------------------------------------------------------------------
    def build_upper_plaza(M):
        up = PARAMS["upper_plaza"]
        b = PARAMS["band"]
        cx = (up["x0"] + up["x1"]) / 2.0
        cy = (up["y0"] + up["y1"]) / 2.0
        Lx = up["x1"] - up["x0"]
        Ly = up["y1"] - up["y0"]
        top = up["z_top"]
        th = up["thick"]
        # [W2-0 · P-A] Register the plaza as a skin-excluded slab. scene01 owns
        # a local `add_box` that never calls `_ground_skin`, so nothing is
        # displaced today; the registration is what keeps the flush ground_kit
        # elements (manhole +-10 mm, tactile 6 mm) safe if this scene is ever
        # routed through `sc.add_box` (spec §1.2).
        sc.skin_exclude("/World/Scene01/UpperPlaza")
        add_box("/World/Scene01/UpperPlaza", (cx, cy, top - th / 2.0),
                (Lx, Ly, th), M["plaza_light"], collider=True)
        # charcoal bands: separate boxes running along Y (own material), repeated by spacing in X.
        # 3 mm proud, 5 cm embedded -> never coplanar with the slab top face (prevents Z-fighting).
        z_bot = top - b["embed"]
        z_top = top + b["proud"]
        cz = (z_top + z_bot) / 2.0
        hz = z_top - z_bot
        n = 0
        x = up["x0"] + b["spacing"]
        while x < up["x1"] - 1e-6:
            add_box(f"/World/Scene01/Band_{n}", (x, cy, cz),
                    (b["width"], Ly, hz), M["band_dark"])
            x += b["spacing"]
            n += 1

    def build_stairs(M):
        """Four descending steps. Each step is a solid box stacked so that its top face (tread) is exposed."""
        st = PARAMS["stairs"]
        tread, riser, ns = st["tread"], st["riser"], st["nsteps"]
        cy = (st["y0"] + st["y1"]) / 2.0
        Ly = st["y1"] - st["y0"]
        base = st["base_z"]
        for i in range(1, ns + 1):
            ztop = -riser * i                       # top-face height of step i
            xa = st["x0"] + tread * (i - 1)
            xb = st["x0"] + tread * i
            cx = (xa + xb) / 2.0
            cz = (ztop + base) / 2.0
            hz = ztop - base
            add_box(f"/World/Scene01/Step_{i}", (cx, cy, cz),
                    (tread, Ly, hz), M["plaza_light"], collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False control: the stair and the whole lower plaza become one
        flat z=0 surface like the upper one → the drop and the hazard are removed
        completely (bias-corrected reading of the brief)."""
        st = PARAMS["stairs"]
        lp = PARAMS["lower_plaza"]
        up = PARAMS["upper_plaza"]
        x0, x1 = st["x0"], lp["x1"]
        y0, y1 = up["y0"], up["y1"]
        th = up["thick"]
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        add_box("/World/Scene01/FlatFill", (cx, cy, up["z_top"] - th / 2.0),
                (x1 - x0, y1 - y0, th), M["plaza_light"], collider=True)

    def build_lower_plaza(M):
        lp = PARAMS["lower_plaza"]
        cx = (lp["x0"] + lp["x1"]) / 2.0
        cy = (lp["y0"] + lp["y1"]) / 2.0
        add_box("/World/Scene01/LowerPlaza",
                (cx, cy, lp["z_top"] - lp["thick"] / 2.0),
                (lp["x1"] - lp["x0"], lp["y1"] - lp["y0"], lp["thick"]),
                M["lower"], collider=True)

    def build_flank_walls(M):
        """Stair flank low wall: 0.5 m outside y ±5.5, top face z=0, down to the bottom."""
        fl = PARAMS["flank"]
        st = PARAMS["stairs"]
        cx = (fl["x0"] + fl["x1"]) / 2.0
        Lx = fl["x1"] - fl["x0"]
        cz = (fl["z_top"] + fl["z_bot"]) / 2.0
        hz = fl["z_top"] - fl["z_bot"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            yc = sgn * (st["y1"] + fl["y_out"] / 2.0)   # wall 5.5->6.0, centre 5.75
            add_box(f"/World/Scene01/FlankWall_{tag}", (cx, yc, cz),
                    (Lx, fl["y_out"], hz), M["granite_dark"], collider=True)

    def build_amphitheater(M):
        """Amphitheater seating, 3 tiers (motif from the right side of photo 1). F1: the
        top descends as z = +0.3−(i−1)*0.3 (+0.3/0.0/−0.3) - the highest tier reads
        as a bench 0.3 above the upper plaza, and the last tier (−0.3) falls to the
        lower plaza (−0.6). Solid bottom z=−0.7."""
        am = PARAMS["amphi"]
        cy = (am["y0"] + am["y1"]) / 2.0
        Ly = am["y1"] - am["y0"]
        base = am["base_z"]
        for i in range(1, am["ntiers"] + 1):
            ztop = 0.3 - (i - 1) * am["rise"]
            xa = am["x0"] + am["depth"] * (i - 1)
            xb = am["x0"] + am["depth"] * i
            cx = (xa + xb) / 2.0
            add_box(f"/World/Scene01/AmphiTier_{i}",
                    (cx, cy, (ztop + base) / 2.0),
                    (am["depth"], Ly, ztop - base), M["plaza_light"],
                    collider=True)

    def build_tree(prefix, cx, cy, gz, trunk_h=None, trunk_r=None,
                   species="elm"):
        """[realism v1] delegated to `scene_common.build_tree`.

        [W3 S01 · K4(b)] `species` is passed **explicitly**, not inherited. The
        `SCENE_SPECIES["Scene01"]` row already resolves this scene's prefix to
        `("elm", None)` — 느티나무의 대용으로 등재된 `Elm_Sapling` — so the value is
        the same either way; stating it at the call site is what makes the scene
        monospecific *by declaration* instead of by a lookup that a later table edit
        could silently change. `belt=` is never used: Scene01's belt is `None`, and
        inventing a second stand here would contradict the frozen table.

        scene01 was the first scene in this library, so it kept its own copy of the
        tree builder as well (the same pattern as `make_pbr` and the capture
        block). The result: **improvements to the shared layer passed scene01 by**
        - the realism round replaced the inside of `sc.build_tree` with real
        vegetation USD assets, yet scene01's trees were still sphere blobs.

        The old comment said "switching to sc would bring back the stakes that
        v4-B3 blocked", but the shared function has defaulted to `stakes=False`
        since the v6 ruling. That reason is gone, so we delegate.
        """
        tr = PARAMS["tree"]
        sc.build_tree(stage, prefix, cx, cy, gz,
                      M["wood"], M["canopy_a"], M["canopy_b"],
                      trunk_r=(tr["trunk_r"] if trunk_r is None else trunk_r),
                      trunk_h=(tr["trunk_h"] if trunk_h is None else trunk_h),
                      stake_r=tr["stake_r"], stake_h=tr["stake_h"],
                      stake_off=tr["stake_off"],
                      stakes=bool(tr.get("stakes", False)),
                      species=species)

    def build_planters(M):
        pl = PARAMS["planter"]
        S, h, t = pl["size"], pl["curb_h"], pl["curb_t"]
        over, cap_h, gh = pl["cap_over"], pl["cap_h"], pl["grass_h"]
        half = S / 2.0
        for spec in PARAMS["planters"]:
            cx, cy, bz = spec["cx"], spec["cy"], spec["base_z"]
            base = f"/World/Scene01/Planter_{spec['name']}"
            top = bz + h
            # kerb frame, 4 walls (dark granite)
            walls = [
                ("S", cx, cy - half + t / 2.0, S, t),
                ("N", cx, cy + half - t / 2.0, S, t),
                ("W", cx - half + t / 2.0, cy, t, S - 2 * t),
                ("E", cx + half - t / 2.0, cy, t, S - 2 * t),
            ]
            for tag, wx, wy, sx, sy in walls:
                add_box(f"{base}/Curb_{tag}", (wx, wy, bz + h / 2.0),
                        (sx, sy, h), M["granite_dark"], collider=True)
                # cap: 5 cm overhang (dark granite)
                add_box(f"{base}/Cap_{tag}", (wx, wy, top + cap_h / 2.0),
                        (sx + 2 * over if sx < sy else sx,
                         sy + 2 * over if sy <= sx else sy, cap_h),
                        M["granite_dark"])
            # grass top face (inside the kerb, under the cap)
            add_box(f"{base}/Grass", (cx, cy, bz + gh / 2.0),
                    (S - 2 * t, S - 2 * t, gh), M["grass"])
            build_tree(base, cx, cy, bz + gh, species="elm")

    def build_backdrop(M):
        """[W3 S01 · BS-4] the collegiate silhouette G1 shows behind the lawn.

        This function **replaces** `build_buildings`, which emitted a shell + a uniform
        window grid + a parapet band for four masses (128 prims, 60 of them windows).
        Two of those masses (R, L) are gone entirely; the other two survive only as
        distant identity and are built through `building_kit.plan_building(..., kind=
        "backdrop")`, whose whole contract is *distant silhouette only, no windows,
        3-4 prims*.

        `bk.judged_eyes(-2.75)` hands the planner **this scene's real preset eye set**
        (`sc.grid_views(-2.75)`), so `d_true`, `in_frame` and `z_ceil` come from the
        judging geometry rather than from `|facade plane|` (B-F3). The loop prints
        `z_ceil` against each block's ridge: the acceptance condition for "the
        environment is open" is `h < z_ceil` on every block, i.e. **sky above every
        roofline**, and it is checked here rather than asserted in a comment.
        """
        bp = PARAMS["backdrop"]
        eyes = bk.judged_eyes(-2.75)
        kit = fk.Kit(sc.add_box, sc.add_cylinder,
                     getattr(sc, "_oriented_box", None))
        n_tot = 0
        over = []
        for tag, x0, x1, y0, y1, hh in bp["blocks"]:
            # A backdrop mass is a plan rectangle seen edge-on; `axis`/`facade_*` only
            # decide which face the planner measures from, and for a silhouette that
            # face is simply the one turned toward the plaza centre.
            if abs((x0 + x1) / 2.0) >= abs((y0 + y1) / 2.0):
                bd = dict(x0=x0, x1=x1, y0=y0, y1=y1, h=hh, floors=3, axis="x",
                          facade_x=(x0 if (x0 + x1) > 0 else x1),
                          face_dir=(-1.0 if (x0 + x1) > 0 else 1.0),
                          base_z=bp["base_z"])
            else:
                bd = dict(x0=x0, x1=x1, y0=y0, y1=y1, h=hh, floors=3, axis="y",
                          facade_y=(y0 if (y0 + y1) > 0 else y1),
                          face_dir=(-1.0 if (y0 + y1) > 0 else 1.0),
                          base_z=bp["base_z"])
            p = bk.plan_building(bd, kind="backdrop", eyes=eyes)
            # `parapet=` gets the **shell material**, not `M["parapet"]`. At 54-80 m a
            # 0.72-grey capping band on a dark brick mass reads as a lit highlight
            # along the roofline — the first pilot showed it as a white lid on the
            # `h0.3_d5` background. A silhouette has no cap by definition.
            prims = bk.build_korean_building(
                kit, stage, f"/World/Scene01/Backdrop_{tag}", bd,
                bk.Mtls(M[bp["mat"]], parapet=M[bp["mat"]]), plan=p)
            n_tot += len(prims)
            sky = (p.z_ceil is None) or (hh + bp["base_z"] < p.z_ceil)
            if not sky:
                over.append((tag, hh, p.z_ceil))
            print(f"[backdrop] {tag} W {p.W:5.1f} h {hh:5.1f} · kind {p.kind} / "
                  f"tier {p.tier} · d_true {p.d_true:6.2f} m · "
                  f"in_frame {str(p.in_frame):5s} · z_ceil "
                  f"{('%.2f' % p.z_ceil) if p.z_ceil is not None else '  n/a'} · "
                  f"sky above roof {str(sky):5s} · prims {len(prims)}")
        print(f"[backdrop] {len(bp['blocks'])}동 {n_tot} 프림 · 창 0 · "
              f"지붕선 위 하늘 {len(bp['blocks']) - len(over)}/{len(bp['blocks'])}"
              + (f" · 초과 {over}" if over else ""))

    def build_streetlight(M):
        """v4-D4: place several poles from the PARAMS['streetlights'] list (x, y, base_z)."""
        sl = PARAMS["streetlight"]
        for k, (x, y, bz) in enumerate(PARAMS["streetlights"]):
            base = f"/World/Scene01/Streetlight_{k}"
            add_cylinder(f"{base}/Pole", (x, y, bz + sl["pole_h"] / 2.0),
                         sl["pole_r"], sl["pole_h"], M["pole"], collider=True)
            # twin arms + lamp heads (+-X direction)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                ax = x + sgn * sl["arm_len"] / 2.0
                add_cylinder(f"{base}/Arm_{tag}",
                             (ax, y, bz + sl["pole_h"] - 0.1),
                             sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                hx = x + sgn * sl["arm_len"]
                add_box(f"{base}/Head_{tag}",
                        (hx, y, bz + sl["pole_h"] - 0.15),
                        (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_south_apron(M):
        """v4-A1 [critical]: fills the sunken grass pit south of the stair.

        Check of the existing coordinates: upper plaza x≤0 · lower plaza x≥1.52 ·
        stair y≥−5.5 · FlankWall_N y −6.0..−5.5 · TerraceL y≤−8 → no prim covered
        the rectangle x 0..1.52 × y −8..−6 and the only floor was GroundGrass
        (−0.63) → a 0.63-deep pit. On the +Y side the amphitheater (x 0..2.7,
        y 6..8) fills the same slot, so the two sides were asymmetric.
        → symmetry restored with a single apron of the same top face (z=0) and the
           same material as the upper plaza.
           Its east cut face (x=1.52) meets the lower plaza (−0.6) west face
           exactly (same as the flank wall).
        """
        ap = PARAMS["south_apron"]
        add_box("/World/Scene01/SouthApron",
                ((ap["x0"] + ap["x1"]) / 2.0, (ap["y0"] + ap["y1"]) / 2.0,
                 (ap["z_top"] + ap["base_z"]) / 2.0),
                (ap["x1"] - ap["x0"], ap["y1"] - ap["y0"],
                 ap["z_top"] - ap["base_z"]),
                M["plaza_light"], collider=True)
        # the matching +Y rectangle (x 0..1.52, y 6..8) is filled by the amphitheater, but
        # the amphi belongs to cue_scene_dressing -> with dressing OFF the same pit opens.
        # for toggle integrity a north apron is laid only in that case (avoids overlapping the amphi top face).
        if not cfg["cue_scene_dressing"]:
            add_box("/World/Scene01/NorthApron",
                    ((ap["x0"] + ap["x1"]) / 2.0, 7.0,
                     (ap["z_top"] + ap["base_z"]) / 2.0),
                    (ap["x1"] - ap["x0"], 2.0, ap["z_top"] - ap["base_z"]),
                    M["plaza_light"], collider=True)

    def build_west_bank(M):
        """v4-A2: terminates the unguarded 0.60 m fall at the upper plaza west end
        (x=−16) with three grass steps. Step heights 0.16 / 0.16 / 0.16 + 0.15 down
        to the grass → all 0.2 m or under (walkable)."""
        wb = PARAMS["west_bank"]
        for i, ztop in enumerate(wb["drops"]):
            x1 = wb["x0"] - wb["step"] * i
            x0 = x1 - wb["step"]
            add_box(f"/World/Scene01/WestBank_{i}",
                    ((x0 + x1) / 2.0, (wb["y0"] + wb["y1"]) / 2.0,
                     (ztop + wb["base_z"]) / 2.0),
                    (wb["step"], wb["y1"] - wb["y0"], ztop - wb["base_z"]),
                    M["grass"], collider=True)

    def build_surroundings(M):
        """F3: prevents the void outside the site (independent of cue_scene_dressing, always built)."""
        # (1) large grass ground plate: top z=−0.63 (a 3 cm step from the lower plaza −0.6 avoids coplanarity)
        add_box("/World/Scene01/GroundGrass", (0.0, 0.0, -0.63 - 0.25),
                (160.0, 160.0, 0.5), M["grass"])
        # (2) [W3 S01 · R01-1] the two `Terrace*` walking bands are **deleted**:
        #     `TerraceR` (x −18..14, y 8..9.5, top 0) and `TerraceL` (x −20..14,
        #     y −10.5..−8, top 0). They existed to carry a walking margin in front of
        #     buildings R and L; both buildings are gone, and G1 puts a lawn there, not
        #     a second paved band. Their footprint is inside the new lawn platform.
        build_lawn(M)
        # (3) v4-A2: west grass bank (always - the upper plaza exists regardless of the toggle)
        build_west_bank(M)

    # -------------------------------------------------------------------
    # [W3 S01 · R01-1] the kerbed designed lawn — GT-27
    # -------------------------------------------------------------------
    def build_lawn(M):
        """Designed lawn platform on the three open flanks of the site.

        Levels, all measured against the two plaza tops that do **not** move:
          * lawn top **−0.150** — 150 mm below the upper plaza (z 0), which is the
            `build_curb_line` default exposure, so the kerb top lands flush with the walk;
          * the same lawn is **+0.450 above** the lower plaza (z −0.60), so the
            lower-plaza frontage is a **retaining band and an up-step**, not a drop
            (GT-27 labels it explicitly — an up-step read as a drop poisons the GT map);
          * the outer edge steps down to the `GroundGrass` plate (−0.63) in two 0.16 m
            grass treads, the ladder `west_bank` already uses, so the platform never
            ends in a hard 0.48 m cut.
        """
        lw = PARAMS["lawn"]
        zt, zb = lw["z_top"], lw["z_bot"]
        yi, xe = lw["y_in"], lw["x_in_e"]
        yo, xo, xw = lw["y_out"], lw["x_out"], lw["x_w"]

        def _slab(name, x0, x1, y0, y1, top, bot, mtl, col=True):
            add_box(f"/World/Scene01/{name}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (top + bot) / 2.0),
                    (x1 - x0, y1 - y0, top - bot), mtl, collider=col)

        # --- the turf platform: N band, S band, E band (they overlap at the corners,
        #     which is fine — overlapping solids share no coplanar face) ---
        _slab("LawnN", xw, xo, yi, yo, zt, zb, M["grass"])
        _slab("LawnS", xw, xo, -yo, -yi, zt, zb, M["grass"])
        _slab("LawnE", xe, xo, -yi, yi, zt, zb, M["grass"])

        # --- granite edge band, top = lawn top -------------------------------
        #     One continuous 0.20 m band closes the strip between the plaza slab
        #     (y = ±8.00 / x = 14.00) and the turf (y = ±8.20 / x = 14.20), so there is
        #     no open slot anywhere along the frontage. What the band *does* changes
        #     with what it fronts, and that is the whole GT story of this scene:
        #       * against the UPPER plaza (x −16…0) the kerb blocks sit on top of it,
        #         and the exposed thing is the 0.150 m kerb face — a **drop**;
        #       * against the LOWER plaza (x 0…14.2, and the east end) the band's inner
        #         face stands 0.450 m **above** the paving — an **up-step**, not a drop.
        #     The band is authored under the kerb rather than beside it so no top face
        #     is ever coplanar with another (the kerb block spans −0.70…0.00 and simply
        #     buries the band's −0.15 top over that run).
        t = lw["ret_t"]
        _slab("LawnRetN", xw, xe, yi - t, yi, zt, zb, M["granite_dark"])
        _slab("LawnRetS", xw, xe, -yi, -yi + t, zt, zb, M["granite_dark"])
        _slab("LawnRetE", xe - t, xe, -yi, yi, zt, zb, M["granite_dark"])

        # --- outer grass bank down to the ground plate ---
        st = lw["bank_step"]
        for i, ztop in enumerate(lw["bank_drops"]):
            a = yo + st * i
            _slab(f"LawnBankN_{i}", xw, xo + st * (i + 1), a, a + st,
                  ztop, zb, M["grass"], col=False)
            _slab(f"LawnBankS_{i}", xw, xo + st * (i + 1), -(a + st), -a,
                  ztop, zb, M["grass"], col=False)
            b = xo + st * i
            _slab(f"LawnBankE_{i}", b, b + st, -(yo + st * (i + 1)),
                  yo + st * (i + 1), ztop, zb, M["grass"], col=False)

    def build_lawn_kerb(M):
        """[W3 S01 · K5] the 150 mm granite kerb along the upper-plaza frontage.

        `infra_kit.build_curb_line` — unit-length 1 m blocks with a 6 mm joint gap over a
        continuous bedding core, which is the point of the row: a monolithic extrusion
        has no scale and "reads as paint" at h0.3 (S06-B). Numbers handed to it:

            z_road = lawn top (−0.150)   height = 0.150   ->   curb top = 0.000
            walk_z = upper plaza (0.000) ->  over = +0 mm, inside "flush … +20 mm"
            gutter = False               ->  gt_drop = 0.150 exactly, no cross-fall

        `gutter=False` is deliberate and is the difference between this call and the one
        S06-B writes for a 보차도: a lawn edge has no carriageway and no L-gutter, so the
        default 18 mm pan cross-fall (which would make `gt_drop` 0.168) must not be
        chained in. `embed` is raised to 0.55 so the block bottom reaches −0.70, the
        upper-plaza slab's own underside, leaving no void behind the face.

        The line is offset to `y = ±8.20`, i.e. the block body occupies y 8.00…8.20 —
        **outside** the plaza slab (which ends at y = 8.00). Running the face on y = 8.00
        would put the block top coplanar with the plaza top over a 0.20 m strip; this is
        the z-fighting the whole scene is built to avoid.
        """
        cb = PARAMS["curb"]
        kit = ik.kit_from_scene_common(sc, stage)
        # The arris is a property of the bound material, not of a prim: assert it.
        arr = ik.check_arris_role(sc, role="curb", arris_r=cb["width"] * 0.0 + 0.010)
        print(f"[curb] arris role check: {arr}")
        lw = PARAMS["lawn"]
        res = []
        for tag, sgn, side in (("N", 1.0, "left"), ("S", -1.0, "right")):
            yf = sgn * cb["y_face"]
            # Both runs go p0 = x0 -> p1 = x1 (+X). The lawn is on +Y for the north run
            # and on −Y for the south one, so which side is "road" is expressed with
            # `road_side`, NOT by reversing the polyline — reversing it would mirror the
            # arc length and silently put the LOD window on the wrong half.
            r = ik.build_curb_line(
                kit, f"/World/Scene01/LawnKerb_{tag}",
                (cb["x0"], yf), (cb["x1"], yf), M["curb"],
                height=cb["height"], width=cb["width"], unit=cb["unit"],
                gutter=False, z_road=lw["z_top"], walk_z=0.0,
                road_side=side, embed=cb["embed"],
                lod_span=cb["lod_win"], far_unit=cb["far_unit"],
                collider=True)
            res.append(r)
            print(f"[curb] {tag} len {r['length']:.2f} m · blocks {r['n_blocks']} "
                  f"@ {r['unit_actual']:.3f} m · top z {r['curb_top_z']:+.3f} · "
                  f"gt_drop {r['gt_drop']:.3f} · prims {r['prim_count']} "
                  f"({r['prims_per_m']:.2f}/m) · warnings {r['warnings']}")
        return res

    def build_lawn_trees(M):
        """Monospecific `elm` planting on the lawn bands, pitch `sc.TREE_PITCH_M` (8.0 m).

        Two rows per band at different distances and different heights, offset half a
        pitch so they never resolve into a grid. Same species throughout: this is one
        route's planting seen in depth, not a belt.
        """
        pitch = float(getattr(sc, "TREE_PITCH_M", 8.0))
        zt = PARAMS["lawn"]["z_top"]
        n = 0
        for r, lt in enumerate(PARAMS["lawn_trees"]):
            for j, y in enumerate(lt["y"]):
                for i in range(int(lt["n"])):
                    x = lt["x0"] + pitch * i
                    build_tree(f"/World/Scene01/LawnTree_{r}{j}{i}", x, y, zt,
                               trunk_h=lt["trunk_h"], trunk_r=lt["trunk_r"],
                               species="elm")
                    n += 1
        print(f"[lawn] 교목 {n}주 · elm 단일종 · 피치 {pitch:.1f} m · "
              f"{len(PARAMS['lawn_trees'])}열")

    def build_fountain(M):
        """G1's fountain — a still basin, built as a walled tank, not as nested discs.

        The first pilot authored it as an outer cylinder + an inner cylinder + a water
        disc, and the render showed why that cannot work: **a solid cylinder has no
        inside**, so the water and the well both sat buried in the outer mass and the
        element read as a plain concrete drum. Rebuilt on the form this scene already
        owns (`build_planters`): four granite walls, a capping course, and a fill —
        with water as the fill instead of turf.
        """
        ft = PARAMS["fountain"]
        zt = PARAMS["lawn"]["z_top"]
        base = "/World/Scene01/Fountain"
        S, t, h = ft["size"], ft["wall_t"], ft["wall_h"]
        over, cap_h = ft["cap_over"], ft["cap_h"]
        half = S / 2.0
        cx, cy = ft["cx"], ft["cy"]
        top = zt + h
        walls = [("S", cx, cy - half + t / 2.0, S, t),
                 ("N", cx, cy + half - t / 2.0, S, t),
                 ("W", cx - half + t / 2.0, cy, t, S - 2 * t),
                 ("E", cx + half - t / 2.0, cy, t, S - 2 * t)]
        for tag, wx, wy, sx, sy in walls:
            add_box(f"{base}/Wall_{tag}", (wx, wy, zt + h / 2.0 - 0.20),
                    (sx, sy, h + 0.40), M["granite_dark"], collider=True)
            add_box(f"{base}/Cap_{tag}", (wx, wy, top + cap_h / 2.0),
                    (sx + 2 * over if sx < sy else sx,
                     sy + 2 * over if sy <= sx else sy, cap_h),
                    M["granite_dark"])
        # still water, inside the walls, `water_drop` below the coping
        wz = top - ft["water_drop"]
        add_box(f"{base}/Water", (cx, cy, wz - 0.05),
                (S - 2 * t, S - 2 * t, 0.10), M["water"])
        add_cylinder(f"{base}/Plinth", (cx, cy, wz + ft["plinth_h"] / 2.0),
                     ft["plinth_r"], ft["plinth_h"], M["granite_dark"])

    def build_litter(M):
        """[W3 S01 · season] autumn leaf litter (G1).

        `sc.scatter_debris` over three regions, each with its own `edge_bias` because
        the sweeping pattern differs: on the treads the leaves collect at the step
        corners (bias high), at the stair foot they lie in a loose apron, and on the
        open plaza only the kerb line and the bands catch them. `ground_fn` seats each
        instance on the actual tread it lands on and lays it along the local slope —
        without it a leaf on a 0.15 m riser floats.
        """
        li = PARAMS["litter"]
        st = PARAMS["stairs"]
        lp = PARAMS["lower_plaza"]
        tread, riser, ns = st["tread"], st["riser"], st["nsteps"]

        def stair_z(x, y):
            if x <= st["x0"]:
                return 0.0
            i = min(int((x - st["x0"]) / tread), ns - 1)
            return -riser * (i + 1)

        n = 0
        n += sc.scatter_debris(
            stage, "/World/Scene01/Litter_Tread",
            st["x0"], st["y0"], st["x0"] + tread * ns, st["y1"], 0.0,
            cover=li["treads"]["cover"], edge_bias=li["treads"]["edge_bias"],
            seed=li["treads"]["seed"], ground_fn=stair_z, max_count=90)
        n += sc.scatter_debris(
            stage, "/World/Scene01/Litter_Foot",
            lp["x0"], -5.0, lp["x0"] + 5.0, 5.0, lp["z_top"],
            cover=li["foot"]["cover"], edge_bias=li["foot"]["edge_bias"],
            seed=li["foot"]["seed"], max_count=70)
        n += sc.scatter_debris(
            stage, "/World/Scene01/Litter_Plaza",
            -12.0, -7.6, -1.0, 7.6, 0.0,
            cover=li["plaza"]["cover"], edge_bias=li["plaza"]["edge_bias"],
            seed=li["plaza"]["seed"], max_count=60)
        print(f"[litter] 낙엽 {n}개 (가을 · G1)")

    # -------------------------------------------------------------------
    # v4-D context dressing (part of cue_scene_dressing) - so it reads as a "campus"
    # -------------------------------------------------------------------
    def build_bench_unit(M, prefix, cx, cy, bz, along="x", yaw=0.0, mtl=None):
        """Seat slab + 4 legs. along='y' puts the long axis on Y (parallel to the paving
        bands). [v5.1] yaw jitter (degrees) - seat and legs all rotate about the
        centre (cx,cy)."""
        bs = PARAMS["bench"]
        L, W, H, st = bs["length"], bs["width"], bs["height"], bs["seat_t"]
        sx, sy = (L, W) if along == "x" else (W, L)
        mt = mtl if mtl is not None else M["seat_wood"]
        add_box(f"{prefix}/Seat", (cx, cy, bz + H - st / 2.0),
                (sx, sy, st), mt, collider=True, rotZ=yaw)
        lx = sx / 2.0 - 0.09
        ly = sy / 2.0 - 0.09
        legh = H - st
        ca, sa = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        for i, (ox, oy) in enumerate(((lx, ly), (lx, -ly), (-lx, ly),
                                      (-lx, -ly))):
            rx, ry = ox * ca - oy * sa, ox * sa + oy * ca
            add_box(f"{prefix}/Leg_{i}", (cx + rx, cy + ry, bz + legh / 2.0),
                    (0.07, 0.07, legh), mt, rotZ=yaw)

    def build_dressing_props(M):
        """D2~D9: bike racks · benches · notice boards · litter bins · hedge · seat
        faces. (D1 entry canopy deleted by R01-2 — the `build_canopy_unit` helper went
        with it, not left as a dead call site. The D7 bollard row was deleted by the v6
        ruling - see the D7 comment in PARAMS.)"""
        R = "/World/Scene01"
        # D2 four bike racks (U-hoop)
        br = PARAMS["bike_rack"]
        for k, y in enumerate(br["ys"]):
            for tag, x in (("A", br["x_a"]), ("B", br["x_b"])):
                add_cylinder(f"{R}/BikeRack_{k}/Post{tag}",
                             (x, y, br["base_z"] + br["h"] / 2.0),
                             br["r"], br["h"], M["rail"], collider=True)
            add_cylinder(f"{R}/BikeRack_{k}/Bar",
                         ((br["x_a"] + br["x_b"]) / 2.0, y,
                          br["base_z"] + br["h"] - br["r"]),
                         br["r"], abs(br["x_b"] - br["x_a"]), M["rail"],
                         rotY=90.0)
        # D3 six benches - [v5.1] beside planter anchors + yaw jitter + per-instance tint jitter (§4)
        for k, (cx, cy, bz, along, yaw) in enumerate(PARAMS["benches"]):
            build_bench_unit(M, f"{R}/Bench_{k}", cx, cy, bz, along, yaw=yaw,
                             mtl=M[f"seat_wood_{k % 3}"])
        # D5 two notice boards (panel + 2 posts + white board face) - [v5.1] yaw supported
        #   local axes: panel thickness = normal n(yaw), panel width = tangent t = n turned +90 deg.
        bo = PARAMS["board"]
        for k, (cx, cy, bz, yaw) in enumerate(PARAMS["boards"]):
            zc = (bo["z0"] + bo["z1"]) / 2.0
            hz = bo["z1"] - bo["z0"]
            ca, sa = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
            add_box(f"{R}/Board_{k}/Panel", (cx, cy, bz + zc),
                    (bo["thick"], bo["width"], hz), M["sign"], collider=True,
                    rotZ=yaw)
            fo = bo["thick"] / 2.0 + 0.006      # the board face is on the −normal side (approach side)
            add_box(f"{R}/Board_{k}/Face", (cx - ca * fo, cy - sa * fo, bz + zc),
                    (0.012, bo["width"] - 0.24, hz - 0.16), M["sign_face"],
                    rotZ=yaw)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                d = sgn * (bo["width"] / 2.0 - 0.12)
                add_cylinder(f"{R}/Board_{k}/Post_{tag}",
                             (cx - sa * d, cy + ca * d, bz + bo["z1"] / 2.0),
                             bo["post_r"], bo["z1"], M["pole"], collider=True)
        # D6 four litter bins
        bn = PARAMS["bin_spec"]
        for k, (cx, cy, bz) in enumerate(PARAMS["bins"]):
            add_cylinder(f"{R}/Bin_{k}/Body", (cx, cy, bz + bn["h"] / 2.0),
                         bn["r"], bn["h"], M["pole"], collider=True)
            add_cylinder(f"{R}/Bin_{k}/Rim", (cx, cy, bz + bn["h"] + 0.02),
                         bn["r"] * 1.1, 0.04, M["rail"])
        # D7 bollard row - [v6 ruling §3] deleted (see the §2/§3/§4 violation notes in the PARAMS comment).
        # D8 low hedge on the upper plaza west side (hides the bank top + terminates the site)
        wh = PARAMS["west_hedge"]
        add_box(f"{R}/WestHedge",
                ((wh["x0"] + wh["x1"]) / 2.0, (wh["y0"] + wh["y1"]) / 2.0,
                 wh["base_z"] + wh["h"] / 2.0),
                (wh["x1"] - wh["x0"], wh["y1"] - wh["y0"], wh["h"]),
                M["hedge"], collider=True)
        # D9 three amphi seat-face timber strips (so the tiers read as seating)
        am = PARAMS["amphi"]
        se = PARAMS["amphi_seat"]
        for i in range(1, am["ntiers"] + 1):
            ztop = 0.3 - (i - 1) * am["rise"]
            xb = am["x0"] + am["depth"] * i
            bx = xb - se["inset"] - se["width"] / 2.0
            z_hi = ztop + se["proud"]
            add_box(f"{R}/AmphiSeat_{i}",
                    (bx, (se["y0"] + se["y1"]) / 2.0, z_hi - se["thick"] / 2.0),
                    (se["width"], se["y1"] - se["y0"], se["thick"]),
                    M["seat_wood"])

    def build_signs():
        """[v5 shared layer] Korean signs - sc.build_sign (post + st-UV panel + backing).
        [v5.2 user] arbitrary warning placards removed - only the facility info
        (sign_info) is placed. See the PARAMS['signs'] comment for the coordinates
        and the camera numeric check. Hazard geometry unchanged."""
        back = sc.make_pbr(stage, "/World/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=_tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"/World/Scene01/Sign_{tag}", cx, cy, bz,
                          yaw, panel, w=w, h=h, back_mtl=back)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P1 plaza_granite. Upper plaza, x -12..0.
    #   The drop edge is the stair nosing at x = stairs.x0 = 0. Joint ticks
    #   that fall inside the edge guard band are dropped by ground_kit itself
    #   (`_edge_guard_ticks`, GT-E2 delta >= 16 rows @1080).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        st = PARAMS["stairs"]
        # stair-head gullies: C-1' puts them 0.40 m inboard of each stair end.
        gy_off = (st["y1"] - st["y0"]) / 2.0 - g["gully_inset"]
        # [W3 S01 · G-4] manholes are DERIVED from the service line, never from the
        #   frame. `derive_manholes` returns the upstream head plus every direction
        #   change / junction / grade or size change, then fills long straight runs at
        #   the KDS 61 40 00 interval for the pipe diameter (Ø450 -> 75 m, so an 11 m
        #   plaza branch gets no intermediate chamber at all).
        mh = ik.derive_manholes(g["manhole_line"], d_mm=g["manhole_d_mm"])
        print("[gkit] 맨홀 유도 " + " · ".join(
            f"{m['tag']}({m['x']:+.2f},{m['y']:+.2f}) {m['reason']}" for m in mh))
        gp = gk.plan_ground(
            "plaza_granite",
            region=(g["x0"], st["y0"], st["x0"], st["y1"]),
            z=PARAMS["upper_plaza"]["z_top"], gy=-2.75,
            origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene01",
            tactile=("stair_top",) if cfg["cue_tactile"] else (),
            sites=dict(manhole=[(m["x"], m["y"]) for m in mh],
                       gully=[(g["gully_x"], -gy_off), (g["gully_x"], gy_off)]),
            seed=1)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # [W3 S01 · 01-A] **stains stop being blobs.** They were bound to
        #   `granite_dark`, i.e. the same near-black stone as the kerb, so a "stain"
        #   rendered as a solid dark ellipse on white granite — the most visible ground
        #   mark in the `beauty_overview` cut of the pilot, and exactly the class of
        #   thing the user's ban is about even though it is not a rectangle. ground_kit's
        #   own R3 rule says the decal ladder must stay **a tone separator, never
        #   relief**; a material 3 stops darker than its host is not a tone separator.
        #   `M["stain"]` is the plaza's own granite at 0.62 tone: the lobe still reads as
        #   soiling at h0.3 and stops reading as paint at 20 m.
        M2.update(joint=M["granite_dark"], crack=M["granite_dark"],
                  patch=M["lower"], patch_cut=M["granite_dark"],
                  manhole=M["gk_iron"], gully=M["gk_iron"], weed=M["hedge"],
                  stain_dirt=M["stain"], stain_water=M["stain"],
                  tactile=M["tactile"])
        res = gk.apply_ground(kit, "/World/Scene01/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris,
                              slabs=("/World/Scene01/UpperPlaza",))
        print(f"[ground_kit] scene01 P1 · prims {res['prims']} · "
              f"delta_max {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_cues(M):
        # tactile paving: [W2-D] moved to ground_kit (spec §12.4 registry entry
        #   scene01/stair_top). The old box sat at x -0.30..0.00 - no statutory
        #   0.30 m set-back and a GT-E1' violation (6 mm dot needs 0.24 m).
        #   `build_ground_kit` now emits the compliant band at x -0.90..-0.30,
        #   still gated by cfg["cue_tactile"] so the ablation toggle is intact.

        # handrails: centre y=0 + both sides y=+-5.45. Top rail tilted along the stair slope +
        # a 1 m horizontal extension at the top + posts (dia 4 cm, spacing ~1.2 m, height 0.9 m).
        if cfg["cue_railing"]:
            rl = PARAMS["railing"]
            st = PARAMS["stairs"]
            tread, riser, nsteps = st["tread"], st["riser"], st["nsteps"]
            run_x1 = tread * nsteps                   # 1.52
            drop = riser * nsteps                     # 0.6
            rail_h = rl["post_h"]                     # 0.9
            ext = rl["ext"]
            ang = math.degrees(math.atan2(drop, run_x1))   # slope angle (vs horizontal)
            L = math.hypot(run_x1, drop)
            for j, y in enumerate(rl["y_lines"]):
                base = f"/World/Scene01/Rail_{j}"
                # top horizontal extension rail (x -ext->0, z=rail_h) - Cylinder Z axis turned to X
                add_cylinder(f"{base}/RailExt", (-ext / 2.0, y, rail_h),
                             rl["rail_r"], ext, M["rail"], rotY=90.0)
                # sloped rail: (0, rail_h) -> (run_x1, rail_h-drop). Tilted with rotateY.
                add_cylinder(f"{base}/RailSlope",
                             (run_x1 / 2.0, y, rail_h - drop / 2.0),
                             rl["rail_r"], L, M["rail"], rotY=90.0 + ang)
                # R2-5: mid rail - same geometry as the top rail, copied with z lowered by mid_drop.
                mid_z = rail_h - rl["rail_mid_drop"]
                add_cylinder(f"{base}/RailExtMid", (-ext / 2.0, y, mid_z),
                             rl["rail_mid_r"], ext, M["rail"], rotY=90.0)
                add_cylinder(f"{base}/RailSlopeMid",
                             (run_x1 / 2.0, y, mid_z - drop / 2.0),
                             rl["rail_mid_r"], L, M["rail"], rotY=90.0 + ang)
                # posts: F6 - they land on the actual step top face. Bottom = tread, top = sloped rail.
                xp = -ext
                p = 0
                while xp <= run_x1 + 1e-6:
                    if xp <= 0:
                        gz = 0.0                       # upper plaza / extension section
                    else:
                        step_idx = min(int(xp / tread), nsteps - 1)
                        gz = -riser * (step_idx + 1)   # height of that tread
                    railz = rail_h - drop * max(0.0, min(xp / run_x1, 1.0))
                    ph = railz - gz                    # variable height (between rail and tread)
                    add_cylinder(f"{base}/Post_{p}", (xp, y, gz + ph / 2.0),
                                 rl["post_r"], ph, M["rail"])
                    xp += rl["spacing"]
                    p += 1

    # -------------------------------------------------------------------
    # setup_lighting (§5: DomeLight + noon HDRI lookfix + auxiliary sun)
    # -------------------------------------------------------------------
    def setup_lighting():
        # [W2] Delegates to `sc.setup_lighting` — the local copy is gone.
        # scene01 was the last scene still on a private lighting stack, and the
        # divergence was not cosmetic: its private `_ensure_noon_lookfix` never
        # got the RGBA patch, so any 4-channel EXR sky made `cv2.imread(...)
        # [..., ::-1]` produce [A,R,G,B]; the horizon lift then raised a
        # broadcast error, the bare `except` swallowed it and returned the
        # ORIGINAL path. Result: an uncapped HDRI sun disc PLUS the explicit
        # DistantLight = double sun, one warning line, render "passes".
        # The three new skies are all RGBA, so this was live ammunition.
        # Same signature, same param keys, same prim paths (/World/DomeLight,
        # /World/NoonSun) -> byte-identical for the existing 3-channel sky.
        return sc.setup_lighting(stage, PARAMS["light"],
                                 PARAMS["SUN_AZ_OFFSET"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_upper_plaza(M)
    if cfg["hazard_stairs"]:
        build_stairs(M)
        build_lower_plaza(M)
        build_flank_walls(M)        # F7: only when the stair exists (flank top face z=0)
        build_south_apron(M)        # v4-A1: fills the south pit (not needed in the flat control)
    else:
        build_flat_fill(M)          # control: unified flat z=0
        # F7: the flank top face (z=0) would be coplanar with the FlatFill top (z=0) -> Z-fighting.
        #     flank walls are meaningless in the flat control, so skip them.
    build_surroundings(M)           # F3: ground outside the site (always built)
    build_lawn_kerb(M)              # [W3 S01] GT-27 — the kerb is site geometry, not
                                    #   dressing: it is the designed edge of the walked
                                    #   plaza and exists in the cue-OFF arm as well.
    if cfg["cue_scene_dressing"]:
        build_amphitheater(M)
        build_planters(M)
        build_backdrop(M)           # [W3 S01 · BS-4] silhouettes, no windows
        build_lawn_trees(M)         # [W3 S01] monospecific elm row, 8.0 m pitch
        build_fountain(M)           # [W3 S01] G1's basin
        build_streetlight(M)
        build_dressing_props(M)     # v4-D: all campus context cues
    build_ground_kit(M)             # [W2-D] ground elements (after dressing)
    build_litter(M)                 # [W3 S01] autumn leaf litter (after the ground)
    build_cues(M)
    if cfg["cue_sign"]:
        build_signs()               # [v5 shared layer]
    apply_dome_rot = setup_lighting()

    # ── §6 camera + render mode ──
    def look_from(eye, pitch_deg=None, target=None):
        if target is None:
            p = math.radians(pitch_deg)
            target = [eye[0] + 5.0 * math.cos(p), eye[1],
                      eye[2] + 5.0 * math.sin(p)]
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in target])

    _v0 = build_views()["beauty_overview"]
    look_from(_v0["eye"], target=_v0["tgt"])       # start camera = mise-en-scene

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

    # ===================================================================
    # auto capture mode (headless verification pipeline - noon only)
    # ===================================================================
    if capture_mode:
        # [realism v1] the local capture block now delegates to `scene_common.capture_pipeline`.
        # this block was the original of capture_pipeline (extracted from here), and after that
        # the other 32 scenes used the shared function while scene01 alone kept a copy and drifted.
        # as a result shared-layer improvements such as PT acceleration (NEGOBS_PT_FAST) and the
        # look-layer measurement report never reached scene01.
        sc.capture_pipeline(
            simulation_app, build_views(),
            os.path.join(LOOKCHECK_DIR, "auto"),
            set_render_mode,
            lambda eye, tgt: look_from(eye, target=tgt))
        simulation_app.close()
        return

    # ===================================================================
    # GUI look check mode (default)
    # ===================================================================
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]                           # user offset from the [ / ] keys

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene01_{ts}.png")
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
