# -*- coding: utf-8 -*-
"""
scene20_diagonal_oblique.py - NegObs synthetic scene 20: diagonal oblique stair (Isaac Sim 4.5)

Type    : T8 diagonal oblique (alignment assumption breaks down)
Spec    : Docs/multi_scene_brief_v3.md §D scene20_diagonal_oblique
Shared  : scene_common.py (verified API helpers) · scene01/scene02 (urban skeleton)

Hazard  : a straight stair rotated 30 deg relative to the plaza walk axis (+X). In the
          frontal presets (axis = walk axis +X, fixed) the drop boundary cuts across the
          frame diagonally - the assumption that a stair is aligned with the direction of
          travel breaks down. The horizon-closing buildings stay axis-aligned, which
          sharpens the contrast.
Goal    : assemble an upper plaza (plaza_light + bands, a scaled-down scene01 motif), a
          30 deg rot_group stair of 14 steps (width 5), the diagonal extension wedge
          (flush plaza-to-stair joint), a lower plaza (warm plaza_lower), grass fill (no
          cavity), an axis-aligned FAR backdrop silhouette and axis-aligned props (bollard
          rows, planters, benches, street lamps), and judge it from renders (render only).

Target image (W3, Lane 3 row 3.3): **G1** primary
          (`Docs/reference_photos/Generated Image - Scene01.jpg`) + **G8** secondary.
          G1 is the archetype of this scene - a granite plaza, a wide low-riser flight,
          benches, planters, streetlights, and **open sky above the roofline**; only the
          30 deg rotation differs. Season is pinned from G1 -> **autumn, in leaf**
          (`w3_intake_v2_images.md` §7 ruling 8: an imageless scene inherits its nearest
          image's season). G8 supplies the paving-band vocabulary.

═══ [GT-87] 08-06 gallery answer — the flight gets a side wall ══════════════════
User ruling: *"계단 양옆에 난간이나 뭔가 있어야 하지 않나..? 벽이라도.. 너무 위험해 보여"*.
The tube guard this scene shipped (`stair_rail`, `StairRail_N/_S`) is replaced by a **masonry
cheek wall on each side of the flight** (`build_stair_walls`, prim roots `StairWall_N/_S`,
still gated by `cue_railing`). Two defects go with it, both visible in
`look_check/scene20/260805_w3_hedgeswap`: a Ø60 tube 0.10 m inboard of the flight edge is the
whole guard against a 2.10 m drop and reads as a floating fragment over the mesa lip; and the
flight's own **side faces were raw** — 14 stepped end faces of `build_straight_stairs` meeting
the valley grass with nothing capping them. The wall is built the way `scene14.build_parapets`
builds one (body box + oblique top haunch + head newel + toe end cap), and — GT-78 having
just removed the handrail from scene14's wall top — **nothing rides on this wall either**.
**Stair geometry, drop, walked-surface z, the 30° drop-edge line and the GT registries are
unchanged**; the wall is new solid beside the flight. OCCL: it is a new opaque occluder along
the flight's two flanks (declared and measured in `plaza_selfcheck` gate (5)).

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene20_diagonal_oblique.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene20_diagonal_oblique.py
Smoke early exit:         NEGOBS_SMOKE=1  python scene20_diagonal_oblique.py

Coordinates: Z-up, m, walk axis +X (fixed by the presets), drop start edge = x=0 before rotation.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk
# [W3 L20] Lane-1 kits. All four are CPU-safe at import time (`pxr` is imported
#   lazily inside every builder), so `NEGOBS_SMOKE` and the fake-USD harness see
#   the same module graph the GPU run does.
#     infra_kit    - K5 `derive_manholes` (G-4: manholes come from a declared
#                    service line, never from the camera)
#     building_kit - BS-4 `kind="backdrop"` (the "open it up" move G1 asks for)
#     facade_kit   - the `Kit` primitive-injection shim building_kit builds through
#     props_kit    - K4(c) C6 regulation bollard template
import infra_kit as ik
import facade_kit as fk
import building_kit as bk
import props_kit as pk


# [W3 L20 · season] Pinned from the nearest target image G1 (§7 ruling 8).
#   G1 is **autumn in leaf**: the frame-right maple carries a full orange crown,
#   the mid-ground broadleaf row is turning and the conifer domes are dark green -
#   there is no bare trunk anywhere in the frame. So `build_tree(bare=)` is
#   deliberately NOT used here (the same audit result scene01 published for the
#   same image); what autumn buys this scene is leaf litter and a warmed turf
#   tone, both built below. Stated rather than skipped: "the leaf-off mechanism
#   exists" is not a reason to fire it.
#   [GT-126] The litter is cut to trace density — the canopy tuples this scene
#   actually carries are summer green, and an autumn carpet under a green crown
#   is a one-frame season contradiction (see the `litter=` PARAMS note).
SEASON = "autumn"


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs is a geometry toggle (False -> unified flat ground).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> remove stairs/lower plaza, whole scene flat at z=0
    "cue_railing":        True,   # [GT-87] Cheek WALLS on both sides of the stair (inside rot_group - follows the diagonal). False -> bare flight, the ablation arm is unchanged in kind
    "cue_tactile":        False,  # [v5.2 user] Tactile paving is rare in reality - OFF by default (ablation path kept)   # Top warning strip (inside rot_group - follows the diagonal)
    "cue_material_break": True,   # False -> unify stair/lower with the upper material (plaza_light)
    "cue_nosing":         False,  # (key reserved)
    "cue_sign":           False,  # [v5.2 user] Arbitrary warning placards removed - nothing placed (key reserved only)
    "cue_scene_dressing": True,   # Bands, axis-aligned buildings and grass in one go
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # Upper plaza (mesa): plaza_light, x -14..-4.5, y -8..8. Top face z=0, solid down to the valley.
    #   [audit v4 A2] x1 0.0 -> -4.5. If the axis-aligned plaza edge runs east past the stair
    #   top line (local x=0 = world x=-0.5774*y diagonal), the north (y>0) top steps get
    #   buried in the plaza solid and the first step height grows to as much as 0.75 m. x1=-4.5
    #   satisfies both limits at once:
    #     (1) the value at which the plaza edge stays west of the diagonal over all |y|<=8
    #        (diagonal x = -0.5774*8 = -4.619 <= -4.5 exceeds by only 0.12 m at y=8 - and that
    #         point is outside the stair width (local |y|<=2.5), pure cliff, irrelevant to walking),
    #     (2) the value at which the wedge below (local |y|<=9) still covers the remaining area
    #        with no gap (mesa points have lx<=0 => y <= -1.732x => ly = -0.5x+0.866y <= -2x <= 9).
    upper=dict(x0=-14.0, x1=-4.5, y0=-8.0, y1=8.0, z_top=0.0, base_z=-2.2),
    # Diagonal extension wedge of the upper plaza (inside rot_group - east face = stair top line)
    wedge=dict(x0=-8.0, x1=0.0, y_half=9.0, z_top=0.0, base_z=-2.2),
    # [W2-D, spec §5.1 scene20 row] Band x range -13...-5 -> **extended to -13...-0.5**.
    #   Measurement basis: the current 5 bands (-13/-11/-9/-7/-5) **hit the d10 cut only** - the
    #   near window of d5 is x -4.44...-3.0 and d2 is -1.44...0, so not one band falls inside.
    #   Restoring the -3 and -1 bands gives all three cuts a longitudinal structure line.
    #   * The old comment ("bands only over the axis-aligned plaza") pulled x1 back to -5.0 for a
    #     real reason: the mesa is the union of the axis-aligned plaza (x <= -4.5) and the 30 deg
    #     wedge, and the wedge's east boundary is the world line **x = -0.5774*y**. Leaving a
    #     full-width y+-8 band at x=-3 would leave the y > 5.196 stretch floating in mid-air.
    #     -> extend x1 as the spec says, but **clamp each band's +y end to the mesa boundary**
    #       (`y_hi = min(y_half, 1.7321*|x|)`). The -y side stays at y_half since it is inside the
    #       wedge local |ly| <= 9 [computed]. The clipped bands end in a staircase along the
    #       diagonal, which if anything strengthens this scene's theme of "axis-aligned props vs 30 deg diagonal".
    band=dict(width=0.45, spacing=2.0, proud=0.0015, x0=-13.0, x1=-0.5,
              y_half=8.0, mesa_slope=1.7320508),   # cot(30°) = 1/tan(30°)
    # Stair 14 steps x riser 0.15, tread 0.34 -> drop 2.1 m, run 4.76 m. Width 5 (y +-2.5).
    stairs=dict(x0=0.0, riser=0.15, tread=0.34, nsteps=14,
                y0=-2.5, y1=2.5, z_top=0.0, base_z=-2.6),
    # rot_group: pivot (0,0), 30 deg - rotates stair and lower plaza together (boundary stays aligned)
    # ★ [W3 R20-1, restated in code] `deg=30.0` is a **scene-wide skew, not per-instance
    #   jitter** (`w3_intake_06_10.md` §1.2 · intake v2 §2 scene20 (g)). It is the whole
    #   identity of the T8 case - the drop boundary is deliberately off the walk axis - and
    #   it is FROZEN. A later jitter-abolition linter pass must **not** zero it, and neither
    #   must scene18's -2.57 deg, which is the same class of quantity. Anything that reads
    #   this key as noise is reading the wrong table.
    rot=dict(pivot=(0.0, 0.0), deg=30.0),
    # Lower plaza (warm) - inside rot_group, continues from the stair foot (local x=4.76, z=-2.1)
    lower=dict(x0=4.76, x1=18.0, y0=-2.5, y1=2.5, z_top=-2.1, thick=0.15),
    # Lower grass base - fills the valley (no cavity). Fully solid under the rotated stair/plaza.
    valley=dict(size=100.0, z_top=-2.15, thick=1.0),

    # === [GT-87] 난간벽 — the side guard the 08-06 gallery answer asks for ==============
    #  What was here: `stair_rail` — a tube guard (rail Ø60 · mid Ø36 · posts Ø40) standing
    #  at local |y| 2.40, i.e. 0.10 m INBOARD of the flight's own side face. Retired with its
    #  call site, for the two reasons the round's cuts show:
    #    (1) it was the only thing between the walker and a 2.10 m drop, and against light
    #        granite a white tube line reads as a fragment floating over the mesa lip;
    #    (2) it left the flight's **side faces raw** — `build_straight_stairs` emits boxes
    #        y −2.5…2.5 down to base −2.6, so 14 stepped end faces met the valley grass.
    #  A cheek wall answers both, and it is the construction the library already carries for
    #  a civic flight (`scene14.build_parapets`): body + oblique haunch + newel + end cap.
    #    `wall_h`   0.95 — wall top over the nosing line. The 08-05 wall band is 0.85~0.95 and
    #                      scene14's parapet sits at the same 0.950, so the two grand-stair
    #                      scenes guard at one height. With the coping the guard line is
    #                      0.95 + 0.06 = **1.010 m** [computed]; the fall here is 2.10 m, i.e.
    #                      past the 1.20 m at which 건축법 시행령 §40 makes a guard mandatory.
    #    `lap`      0.06 — how far the wall's inner face laps ONTO the flight: |y| 2.44 against
    #                      the flight's 2.50. A flush 2.50 face would be coplanar with the
    #                      stair's own side face in a **different material** — the z-fighting
    #                      this round's verdict names. With the lap the stepped side faces end
    #                      up inside the wall solid. Clear walking width 5.00 → **4.88 m**
    #                      [computed]; no stair prim moves and no drop edge moves.
    #    `width`    0.36 — wall thickness, |y| 2.44…2.80. 350 mm masonry class.
    #    `haunch_t` 2.10 — PERPENDICULAR thickness of the oblique top slab (`sc.build_slope`
    #                      measures it that way). Vertical equivalent 2.10/cos 23.815° =
    #                      **2.295 m**, which must exceed the flight's 2.10 m drop or the body
    #                      box shows through the wall face — scene14's "bite" condition,
    #                      re-derived here rather than copied. Bite at the head **0.095 m**
    #                      [computed]. The slab's deepest vertex lands at z **−3.071**, inside
    #                      the valley slab (bottom −3.150), so no solid pokes out of the
    #                      ground plane at the toe.
    #    `body_drop` 0.10 — body top = wall top at the toe (−1.150) − 0.10 = **−1.250**, so the
    #                      body is buried under the haunch over the whole run.
    #    `base_z`  −2.30 — foot of every wall solid, 0.15 m under the valley top (−2.15).
    #                      Nothing terminates in air.
    #    `cap_t`    0.06 · `cap_proud` 0.03 · `cap_bite` 0.04 — the coping: a band oversailing
    #                      the wall 30 mm on each face and sunk 40 mm into it, so it reads as a
    #                      capping with its own shadow line and is not a coplanar skin. Bound
    #                      to `band_dark`, the plaza's own dark granite, which is what makes
    #                      the guard a LINE at 20 m — the property the tube did not have.
    #    `nose`     0.02 — coping projection past the newel end and the toe end face. A coping
    #                      stopping flush with the end face reads as a saw cut.
    stair_wall=dict(width=0.36, lap=0.06, wall_h=0.95, haunch_t=2.10,
                    body_drop=0.10, base_z=-2.30,
                    cap_t=0.06, cap_proud=0.03, cap_bite=0.04, nose=0.02),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004),

    # === [W2-D ground_kit] P1 plaza_granite - spec §5.1 scene20 row ========================
    #  The row's own prescription is the band extension (see `band` above);
    #  the P1 common set (6 m expansion + 1.8 m contraction joints, 1~2
    #  manholes with one in W1, repair patches, soiling decals, edge weeds)
    #  supplies the rest.
    #  ★ Tactile **OFF** (§12.4 identity conflict — hidden illusion). Gate B12
    #    `_inv_hidden_illusion` refuses a tactile element or any bright
    #    (albedo > 0.28) full-width transverse line for scene20.
    #  ★ Region x1 = **-2.0**, not -0.5. The drop edge of this scene is the
    #    30 deg diagonal x = -0.5774*y, not the line x = 0 that the kit's frame
    #    model assumes. A rectangle is only entirely on the mesa if
    #    x1 <= -0.5774*|y|max; with y = +-3.0 that is x1 <= -1.73, and -2.0
    #    keeps 0.27 m of margin at the worst corner [computed].
    #    Consequence: the d2 near window (x -1.44..0) cannot be filled by the
    #    kit at all in this scene. That is geometry, not an omission — the d2
    #    window lies beyond the diagonal for most of the frame width.
    #  ★ [W3 L20 · F1 ghost patches — the spec names scene20] the `patch=` site list
    #    is **deleted**, not re-sited. Two things were true at once and only one of them
    #    was visible: (1) GT-24 already removed `("patch", 1)` from the `plaza_granite`
    #    profile library-wide (a saw-cut milled rectangle is an *asphalt* repair; on 판석
    #    600 unit paving the real repair lifts and relays whole flags), so this list has
    #    emitted **0 prims** since that row landed — measured on the composed stage, GKit
    #    carries crack/joint/gully/manhole/stain and no `Patch_*` at all; and (2) the
    #    scene-side binding underneath it was `patch=M["upper"]`, i.e. the patch was bound
    #    to the plaza's **own** material — the "lighter-than-base ghost patch" F1 names.
    #    A dead call site that names a banned vocabulary reads as intent, so it goes
    #    (the K2 doctrine: flip the default, then remove the now-inert call sites in the
    #    same work package). G1 shows no repair mark of any kind on the granite field.
    #  ★ [W3 L20 · G-4] manholes are no longer literal coordinates. `utility.line` declares
    #    where the storm branch actually runs — along the north planting margin, on the
    #    service side, into the north stair-head gully — and `infra_kit.derive_manholes`
    #    returns the chambers the KDS 61 40 00 trigger table asks for. The two deleted
    #    magic values `(-5.00, +1.40)` / `(-10.00, -1.40)` sat at |y| <= 1.4 with x < 0,
    #    i.e. inside the d2/d5 near-window band the G-4 census indicts (19/26 sites).
    gkit=dict(
        region=(-13.0, -3.0, -2.0, 3.0),
        #    Ø450 storm branch under the north planting margin, running east to the
        #    outfall; the north stair-head gully lateral joins it at x = -8.00. A 9.8 m
        #    branch is two orders shorter than the Ø<=600 mm KDS straight-run interval
        #    (75 m), so the run gets **no** intermediate chamber and the derivation
        #    returns exactly the upstream head plus the gully junction = 2, which is also
        #    the count `GROUND_PROFILES["plaza_granite"].infra` prescribes.
        utility=dict(line=[(-12.60, 2.60), (-2.80, 2.60)],
                     junctions=[(-8.00, 2.60)], d_mm=450.0),
        gullies=[(-3.00, -2.60), (-8.00, 2.60)],
    ),

    # === [W3 L20 · BS-4] the axis-aligned masses stay, the closed horizon goes =========
    #  What was here: three `sc.build_building` masses at **26 / 16 / 32 m** from the
    #  plaza centre carrying h 13.0 / 11.0 / 16.0 and a full window grid. From the h0.3
    #  judging eye at x=-2 the nearest of them (facade x=26, d 28.0 m) has a frame ceiling
    #  of z = 0.3 + 0.1405*28.0 = **4.23 m** and a ridge at **13.75 m** — the mass runs off
    #  the top edge of frame and there is no sky in the cut at all. G1's own reading is the
    #  opposite: *"open sky above the roofline — no far skyline wall"*, and the intake row
    #  names it as this scene's gap ("three axis-aligned buildings close the horizon — same
    #  'open it up' move as 01 and 14").
    #  What replaces it: the same **axis-aligned** identity — which is this scene's whole
    #  theme, axis-aligned world against a 30 deg stair — rebuilt as a FAR silhouette
    #  through `building_kit.plan_building(..., kind="backdrop")`, whose contract is
    #  *distant silhouette only, no windows, 3-4 prims*. `bk.judged_eyes(0.0)` hands the
    #  planner this scene's real preset eye set (gy = 0.0, spec §D fixes the axis), so
    #  `d_true` / `in_frame` / `z_ceil` come from the judging geometry and not from
    #  `|facade plane|` (B-F3). The acceptance condition is a number checked at assembly
    #  time and printed per block: **ridge < z_ceil**, i.e. sky above every roofline,
    #  where `ridge = base_z + h + bk.roof_allow(p)` — the parapet band and penthouse
    #  `build_korean_building` emits **above** the shell-top invariant (S01-F1). It is
    #  computed from the plan here rather than copied as a constant, because a copied 2.90
    #  is exactly how scene01 shipped a wall off the top of frame twice.
    #  base_z = -2.15 is the top face of the valley grass (audit v4 B3: left unset the
    #  shells floated 1.15 m).
    backdrop=dict(
        base_z=-2.15,
        mat="brick",
        # (tag, x0, x1, y0, y1, h) - plan rectangles of the silhouette masses, all
        #   axis-aligned. E1/E2 close the head of the diagonal, W1 backs the mesa entry
        #   ramp, N1/S1 are the flanking wings that keep the valley from reading as a
        #   tabletop. Every h is solved from that block's own ceiling minus its own
        #   `roof_allow`, and the printed "지붕선 위 하늘" column must read 5/5.
        #  ★ Every block must also sit **inside the valley ground plane**. The first
        #    solve put E1/E2/W1 at 56-76 m and N1/S1 partly past `Valley` (a 100 m box
        #    centred at x=+6, i.e. x -44…+56 · y -50…+50), and the pilot render showed
        #    exactly that: masses standing at the edge of the world with the plane's own
        #    horizon seam running behind them. The sky arithmetic was right and the
        #    containment was never checked — so `plaza_selfcheck` now gates BOTH, and the
        #    blocks are re-solved inside the plane with >= 2 m of margin. W1 is **deleted**
        #    rather than re-sited: the preset axis is +X (spec §D) and all four
        #    mise-en-scene cuts look east, so a -X mass is behind every judged eye and was
        #    paying 3 prims for nothing.
        blocks=(
            ("E1",  44.0,  52.0, -26.0,  -4.0, 5.5),
            ("E2",  46.0,  54.0,   3.0,  26.0, 5.7),
            ("N1", -18.0,  30.0,  40.0,  48.0, 4.8),
            ("S1", -20.0,  28.0, -48.0, -40.0, 4.8),
        )),

    # === [W3 L20 · K4(b) · U-7 "open environment"] the mid-ground belt =================
    #  Opening the horizon is only half the move. scene01's pilot found the other half the
    #  hard way (its defect 4): with the near masses gone, the ground between the plaza and
    #  the backdrop is *an empty green plane* — open, but not a place. G1 shows what fills
    #  it: mature broadleaves between the plaza and the buildings, in autumn colour.
    #  Two east rows on the valley grass plus one row on each flank, every tree the scene's
    #  **route** species `elm` passed explicitly (`SCENE_SPECIES["Scene20"] = ("elm", None)`
    #  — the belt slot is None and inventing a second stand here would contradict the frozen
    #  table, which is the same call scene01 published for the same image).
    #  Row separation **8.6 m** and pitch **8.0 m** (`sc.TREE_PITCH_M`): at 6.0 m separation
    #  every tree's nearest neighbour is in the *other* row and `placement_lint` LINT-2
    #  reads one zig-zag run instead of two rows (scene01's measurement, reused rather than
    #  re-derived). Crown top lands at about -2.15 + 4.80 = **2.65 m**, under the h0.3
    #  frame ceiling at every row distance, so the belt fills the mid-ground without
    #  re-closing the sky the backdrop just opened.
    belt=dict(z=-2.15, trunk_h=3.0, pitch=8.0,
              rows=(("E1", 24.0, -16.0, 16.0, "y"),
                    ("E2", 32.6, -16.0, 16.0, "y"),
                    ("N1", 18.0, -18.0, 14.0, "x"),
                    ("S1", -18.0, -18.0, 14.0, "x"))),

    # --- Context dressing (cue_scene_dressing): "civic / university-front urban plaza" ---
    #     The contrast between axis-aligned props (bands, buildings, planter rows) and the 30 deg diagonal edge is this scene's theme.
    #     All upper props sit on the mesa (axis-aligned plaza union wedge) - see fixlog_I5 for the coordinate check.
    # [v5.1 §2] Bollards regularised - old: 5 bollards at 2.0 m spacing along x -1.2 over y -7..1
    #   plus 3 scattered = 8 total. That is a **decorative row lined up right in front of the
    #   diagonal drop edge (local x=0)**, which has no basis in §2 (vehicle entry points only) and
    #   also violates the equal-spacing convention (§3). Dropped exactly as instructed: "do not line them up along the diagonal edge itself".
    #   New: **one row** at each of the 2 actual vehicle approach points (1.5 m spacing, 1.5 m centre gap),
    #   with a 0.3 m dot-tactile strip in front of each row on the pedestrian side.
    #     (1) Top of the mesa entry ramp (x -13.6; ramp x -18..-14, width y +-2)
    #        -> **behind** (x < -10) every grid eye (x -2/-5/-10) and every mise-en-scene preset
    #     (2) Entrance to the lower plaza's diagonal corridor (rot local lx 17.0, plaza x1 18.0)
    #        -> world (14.72, 8.50). From the grid eyes that is bearing 19-27 deg, distance 18.7-26 m,
    #          i.e. background, with no interference with the judged region (diagonal drop boundary x -4.6..0).
    bollards=dict(x=-13.6, ys=(-2.25, -0.75, 0.75, 2.25),
                  block=dict(x0=-13.6, x1=-13.3, y0=-2.55, y1=2.55)),
    # === [W3 L20 · C5 / census / CB-5] the mesa furniture is re-sited, measured ========
    #  Three defects, all found by arithmetic over the footprint rectangles before
    #  anything was rendered (`scratchpad` layout probe, reproduced by `plaza_selfcheck`
    #  below) — the pre-edit layout carried **four hard interpenetrations**:
    #    Planter_2 x Bench_0        1.450 x 0.400 m  (a bench sitting inside a flower bed)
    #    Planter_2 x Streetlight_0  0.140 x 0.140 m  (a 5.5 m pole rising out of the bed,
    #                               0.78 m from the bed's own tree)
    #    Planter_1 x Streetlight_1  0.140 x 0.140 m  (the same defect, south flank)
    #    Bench_0   x Streetlight_0  0.140 x 0.070 m
    #  and the census row `w3_md_reverts_v1.md` §5 — `oblique_overview` at **0.450 m**
    #  from `Planter_1`'s bed AABB with a live `Elm_Sapling` in it, named there as *"the
    #  closest geometric analogue"* to the C02-P1 defect that batch had just fixed.
    #  The fix is a re-site, not a mitigation: the beds move onto the flank margins where
    #  G1 puts every planted element (in G1 the plaza field above the steps is bare
    #  paving), the bench row becomes ONE row parallel to the kerb line at y = +3.60 with
    #  a constant bearing and irregular 3.25 / 4.25 m spacing (CB-5's pilot condition —
    #  that is the difference between a row and a grid), and the poles move off the beds.
    #  Post-edit: **0 overlaps**, every footprint corner on the mesa, worst judged-eye ->
    #  bed distance **2.750 m** (`Planter_1` x `oblique_overview`) against the >= 2.50 m
    #  gate `plaza_selfcheck` now asserts over all 13 cuts x all beds.
    planters=[(-12.3, 5.6), (-12.3, -5.6), (-7.0, 5.6)],
    planter=dict(size=3.0),
    #  [K4(b) S-2] one species per bed, declared, not drawn: `planter_accent` = Yew, the
    #  formal-planter role of the species table. Before this the beds inherited
    #  `SHRUB_ORNAMENT` through a per-bed `randrange`, and the composed stage measured
    #  **4 Rhododendron + 2 Juniper across 3 beds** — two species in one civic planter run,
    #  which is precisely what S-2 exists to stop. (Rhododendron's flower loss is a
    #  library-wide `_deactivate_seasonal` treatment, K4-F1 — not a regression, and not the
    #  reason for this change.)
    planter_species="planter_accent",
    benches=[(-12.9, 3.6, 0.0), (-9.65, 3.6, 0.0), (-5.4, 3.6, 0.0)],
    streetlights=[(-12.6, 2.0), (-7.0, 3.0), (-9.5, -6.9)],
    streetlight=dict(pole_h=5.5, pole_r=0.07, arm_len=1.0, arm_r=0.04,
                     head=0.25),
    hedges=[(-14.0, 7.4, -9.0, 8.0), (-14.0, -8.0, -9.0, -7.4)],
    # Mesa entry ramp (west side) - "how does one get up onto this plaza" (audit v4 A5)
    access_ramp=dict(x0=-18.0, x1=-14.0, y0=-2.0, y1=2.0, thick=2.6),
    # [v5.2 user] Arbitrary warning placards removed - stair-warning sign (PARAMS['signs']) deleted.
    # Lower plaza props (rot_group local coordinates, base_z=-2.1)
    # [v5.1 §2] Old: 2 pairs at the stair foot (lx 5.6/9.0) = decorative placement lining the
    #   diagonal corridor. -> Moved to a single row at the corridor **entrance** (lx 17.0) plus a 0.3 m dot-tactile strip in front.
    lower_bollards=dict(x=17.0, ys=(-2.25, -0.75, 0.75, 2.25),
                        block=dict(x0=16.7, x1=17.0, y0=-2.55, y1=2.55)),
    lower_benches=[(12.0, -1.85, 0.0), (12.0, 1.85, 0.0)],

    # === [W3 L20 · season] leaf litter — [GT-126] reduced to trace ====================
    #  Three regions, each with its own `edge_bias` because the sweeping pattern differs.
    #  The treads region lives **inside the 30 deg rot_group** and is authored in group
    #  local coordinates, so the litter follows the diagonal exactly as the stair does —
    #  scattering it in world space would lay a rectangular leaf field across a rotated
    #  flight. `ground_fn` seats each instance on the tread it actually lands on; without
    #  it a leaf on a 0.15 m riser floats.
    #  [GT-126] cover 0.030/0.022/0.012 -> 0.006/0.004/0.002 (with the max_count caps in
    #  `build_litter` cut to match). The audit caught the frame contradicting itself:
    #  `canopy_a/b` below are the FULL summer-green tuples (identical to scene16's), yet
    #  the ground carried an autumn carpet — and carried it on the paving only, with the
    #  adjacent turf clean, which no wind does. The canopy is not touched (recolouring a
    #  crown is a new-asset move, and the belt is shared vocabulary); the carpet is cut to
    #  the handful of dry stray leaves that survives ANY season, which reads with a green
    #  crown and needs no matching turf field. SEASON stays "autumn" — what autumn still
    #  buys this scene is the warmed `grass_tint`, which contradicts nothing.
    litter=dict(treads=dict(cover=0.006, edge_bias=0.45, seed=10120),
                foot=dict(cover=0.004, edge_bias=0.30, seed=20220),
                plaza=dict(cover=0.002, edge_bias=1.20, seed=30320)),

    material=dict(
        # [GT-126] band_dark 0.6 -> 1.80 · plaza_lower 0.7 -> 2.4. Both are unit-size
        #   arithmetic, not taste: `band_dark_diff` carries ~5x8 stone units per tile, so
        #   at 0.6 m/tile a unit is 0.12 x 0.075 m — below what the judged distances
        #   resolve, and its directional grain mip-averages into the one-axis smear the
        #   audit crops show on the bands and the wall coping. At 1.80 (the same scale_m
        #   as the plaza_light field, i.e. the audit's "판석과 같은 실척") a unit is
        #   0.36 x 0.225 m and survives as a unit. `plaza_lower_diff` carries ~12x6 setts
        #   in a 2:1 image, so 0.7 gave 0.06 x 0.12 m micro-weave one frame away from the
        #   0.6 m upper flags; 2.4 puts the sett on the real 0.2~0.3 m block module.
        scale=dict(plaza_light=1.80, band_dark=1.80, plaza_lower=2.4,
                   grass=1.4, brick_red=2.0, tactile=0.3),
        lower_warm_tint=(1.06, 1.0, 0.94),
        # [W3 L20 · season] 0.55/0.68/0.42 -> 0.60/0.63/0.38: desaturated and warmed for
        #   autumn, green still the largest channel. A straw-yellow lawn would be a
        #   different season, not this one. (Same value scene01 measured against the same
        #   image, so the two G1 scenes do not drift apart in tone.)
        grass_tint=(0.60, 0.63, 0.38),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] Parapet 0.90 -> 0.72 (no large pure-white areas)
        # [GT-126] 0.72 -> 0.32. The [GT-87] cheek walls bind this, and the audit
        #   measured their faces at 0.87 screen luminance — a flawless white plane over
        #   the very band 0.72 was meant to avoid, because 0.72 clips at the top of the
        #   tone mapping (the LOOK_CLASS "snow" note documents 0.72-0.78 doing exactly
        #   that). 0.32 sits inside the real concrete band (the look layer's own
        #   `alb_max` 0.34 ceiling), so the promoted concrete grain has headroom to
        #   read instead of blowing out. `Looks/Parapet` already classifies concrete
        #   (LOOK_ROLE exact match), so texture promotion needs no rename here.
        #   **Material only** — the walls are this scene's drop-edge guard (2.10 m fall),
        #   so their geometry is frozen; no coping/thickness prim is added or moved.
        parapet_color=(0.32, 0.32, 0.30), parapet_rough=0.6,
        # For dressing (dark constant-colour albedo convention)
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
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
    SUN_AZ_OFFSET=171.5,   # Standard. Keeps the preset frontal light (inherited from scene01). Shadows fall on the
                           # diagonal drop boundary and emphasise the obliqueness (can be fine-tuned at render time).

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


_CUEOFF_SCENE = "scene20"


# ===========================================================================
# [B'] keep_dressing / placebo_remove — v3 C팔 옵트인 키 (D82 ②)
# ===========================================================================
#   `experiments/weekend_0823/cue_audit/scenes_cueoff/scene20_*.py` 의 감사
#   통과본을 **정본으로 승격**한 것이다(D82 ② additive 옵트인 키 채택, 기본값
#   무변경 해시게이트 증명 조건).  두 플래그가 모두 False 이면 아래의 모든 가드
#   표현식은 이식 이전의 코드 경로로 **정확히 붕괴**한다.
#
#   keep_dressing   D25/D30 패턴 (원본 `scenes/batch1/sceneC2_leaf_stairs.py`
#                   :496-520).  C 팔 = 낙차 기하 제거, 단서·드레싱 유지.
#   placebo_remove  D35/R2 §5.3-2 요구.  본 씬의 군은 백드롭 블록 E1·E2 이며,
#                   **AMBER(탐색 전용, PREREG_CUEOFF §3.3)** 로 등급이 낮다 —
#                   실측 질량은 `PLACEBO_PIXEL_MASS_crest.csv`.
#
#   주의 — scene20 의 `cue_railing`(치크월)은 **구조물 실측**(12,656셀 · 3.160 m)
#   이라 계획 §1.2 에서 **영구 금지 레버**다.  C 팔은 레버를 쓰지 않으므로
#   해당 없음.
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
PLACEBO_REMOVE = bool(SCENE_CONFIG.get("placebo_remove", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            f"[FATAL {_CUEOFF_SCENE}] keep_dressing=True requires "
            "hazard_stairs=False — with the hazard ON there is nothing to keep "
            "and the arm would be an unlabelled duplicate of arm A. "
            "Fix the render config.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            f"[FATAL {_CUEOFF_SCENE}] keep_dressing=True contradicts "
            "cue_scene_dressing=False — the dressing IS what this arm exists to "
            "preserve.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            f"[FATAL {_CUEOFF_SCENE}] placebo_remove=True requires "
            "hazard_stairs=True — the placebo arm is a HAZARD-ON appearance "
            "control (D35). With the hazard off it measures nothing.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            f"[FATAL {_CUEOFF_SCENE}] placebo_remove=True with "
            "cue_scene_dressing=False removes the placebo group twice over and "
            "confounds arm P with arm B1. Fix the render config.")
    if KEEP_DRESSING:
        raise SystemExit(
            f"[FATAL {_CUEOFF_SCENE}] placebo_remove and keep_dressing are "
            "different arms (P and C) and must never be set together.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "A/B_hz%d_rail%d_mat%d_dress%d" % (
            int(SCENE_CONFIG.get("hazard_stairs", True)),
            int(SCENE_CONFIG.get("cue_railing", False)),
            int(SCENE_CONFIG.get("cue_material_break", True)),
            int(SCENE_CONFIG.get("cue_scene_dressing", True))))
print(f"[CUE-OFF] {_CUEOFF_SCENE} arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] Path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene20")

ASSET_ROLES = ["plaza_light", "band_dark", "plaza_lower", "grass",
               "brick_red", "tactile",
               "hdri", "mdl"]      # [v5.2 user] Arbitrary warning placards removed


def build_views():
    """Camera presets: grid_views(gy=0, walk axis +X [fixed]) + 4 mise-en-scene cuts."""
    views = sc.grid_views(0.0)               # Preset axis = walk axis +X (spec §D, fixed)
    # oblique_overview: the diagonal drop boundary cuts across the frame
    views["oblique_overview"] = dict(eye=[-8.0, -4.0, 3.2], tgt=[3.0, 1.0, -1.0])
    # walk_axis_front: head-on along the walk axis - the boundary slices the frame diagonally
    views["walk_axis_front"] = dict(eye=[-6.0, 0.0, 1.6], tgt=[4.0, 0.0, -0.8])
    # along_diagonal: looking down along the stair's diagonal axis (confirms the alignment breakdown)
    views["along_diagonal"] = dict(eye=[-3.0, -3.0, 1.5], tgt=[5.0, 1.6, -1.6])
    # low_grazing: low viewpoint - the drop is hidden above the diagonal boundary
    views["low_grazing"] = dict(eye=[-6.0, 0.0, 0.35], tgt=[4.0, 0.5, -0.3])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. oblique_overview / walk_axis_front — 30° 사교 계단·사선 낙차 경계 식별
 2. h0.3·d5~10                         — 사선 경계 위로 낙차 2.1m가 은닉되는가
 3. 정렬 대비                          — 건물은 축정렬, 계단만 30° 틀어진 대비
 4. cue ON vs OFF                      — 측벽/tactile(사선 따라) 토글 시 계단 기하 불변
 5. 재질/공동                          — 하부 잔디 채움·경계 정합·Z파이팅 없는가
 6. [v4] 사선 쐐기 접합(첫 단차 전 폭 0.15)·축정렬 볼라드 열·건물 접지
 7. [v5] 공통 레이어 — 사선 점자띠 판독"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene20")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene20"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["upper"] = PBR(
            f"{ROOT}/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # [GT-126] `Looks/Band` -> `Looks/BandDark`. The bare name "Band" is pinned to
        #   the **paint** class by LOOK_ROLE exact match (GT-113 W6 pinned the painted
        #   bands there when the "band" keyword was retired) — but this material is
        #   *textured dark granite*, so paint-class routing kept it on plain cubic
        #   OmniPBR with no detail normal, no dither and no albedo band: half of the
        #   band/coping smear the audit crops show. "BandDark" is the very name W6's
        #   note names as the fixed case — it falls through to the concrete family via
        #   its "dark" token and gets the ground treatment (triplanar + detail + band).
        #   The dict key `M["band"]` and every bind site are unchanged.
        M["band"] = PBR(
            f"{ROOT}/Looks/BandDark", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["lower"] = PBR(
            f"{ROOT}/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["lower_warm_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        # [GT-87] `Looks/Rail` is gone with the tube guard it was the only binding for.
        #   `rail_color` / `rail_metallic` / `rail_rough` stay in PARAMS because the three
        #   bollard bodies below are derived from them — the wall takes `Looks/Parapet`
        #   (concrete) and `Looks/BandDark` (dark granite coping), both already in this
        #   scene.
        # [v5.1 §2/§4] Materials for the regulation bollards - 3 body variants (tint jitter +-5%) + reflective band.
        #   The band is small in area, so high luminance is allowed (unrelated to the no-large-pure-white-area rule).
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"bollard_{_i}"] = PBR(
                f"{ROOT}/Looks/Bollard_{_i}",
                diffuse_color=tuple(min(c * _f, 1.0) for c in mp["rail_color"]),
                metallic=mp["rail_metallic"],
                roughness_const=mp["rail_rough"] * (1.0 + 0.05 * (_i - 1)))
        # [GT-126] band (0.86,0.86,0.84) -> safety yellow. Against a body derived from
        #   `rail_color` (0.80 grey) the old value was the same white — the band, whose
        #   whole function is night-time contrast, vanished in every cut. The C6
        #   regulation band is high-contrast against a light body (황색). `BollardBand`
        #   classifies paint (constant colour kept by the look layer), so the cue
        #   colour survives LOOK_V1 untouched.
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=(0.80, 0.52, 0.05),
                                roughness_const=0.35)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        # [W2 fix batch F1] Ground-class decal materials for the kit.
        #   Binding kit crack / stain / wear elements to the scene's joint-sealant
        #   (`paint` class), steel (`metal`) or kerb constants is what rendered them
        #   as flat texture-less ribbons and mats: those classes are excluded from
        #   `_CONST_MDL_CLASSES` **by design** (a constant colour is physically right
        #   for paint and metal), so a *ground* prim bound to one gets no texture at
        #   all. `GKitCrack` / `GKitStain` classify as concrete, so they are promoted
        #   to a real ground texture with the intended albedo preserved.
        # [W3 L20 · 01-A, on the first pilot render] the stain lobes stopped being plates.
        #   `GKitStain` was a **constant near-black** (0.20, 0.20, 0.195) laid on white
        #   granite. `Stain_water/water_2` measures 0.613 x 0.496 m and its near edge sits
        #   0.05 m in front of the `preset_h0.3_d5` eye `[measured — composed inventory]`,
        #   so at h0.3 it fills a third of the near band and reads as a **painted plate**,
        #   not as soiling. ground_kit's own R3 rule is that the decal ladder must be *a
        #   tone separator, never relief*, and a material three stops darker than its host
        #   is not a tone separator — the same defect scene01's pilot found and fixed on
        #   the same profile. `M["stain"]` is now the plaza's own granite at **0.62 of the
        #   scene's own T-1 tone** (0.72 x 0.62 = 0.4464): still clearly soiling at h0.3,
        #   no longer paint at 20 m. Material only — 0 prims, no GT quantity moves.
        M["stain"] = PBR(
            f"{ROOT}/Looks/GKitStain", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.4464, 0.4464, 0.4464))
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # Ground - valley grass (fully solid, no cavity) + upper mesa
    # -------------------------------------------------------------------
    def build_ground(M):
        v = PARAMS["valley"]
        H = v["size"] / 2.0
        BOX(f"{ROOT}/Valley", (6.0, 0.0, v["z_top"] - v["thick"] / 2.0),
            (v["size"], v["size"], v["thick"]), M["grass"], col=True)

    def build_upper(M):
        u = PARAMS["upper"]
        cx = (u["x0"] + u["x1"]) / 2.0
        cy = (u["y0"] + u["y1"]) / 2.0
        top, bot = u["z_top"], u["base_z"]
        # [W2-0 · P-A] The mesa top is the ground_kit stage.
        sc.skin_exclude(f"{ROOT}/UpperPlaza")
        BOX(f"{ROOT}/UpperPlaza", (cx, cy, (top + bot) / 2.0),
            (u["x1"] - u["x0"], u["y1"] - u["y0"], top - bot),
            M["upper"], col=True)
        # Bands (charcoal stripes running along Y, a scaled-down scene01 motif)
        if cfg["cue_scene_dressing"]:
            build_bands(M, top)

    def build_bands(M, top):
        """[C팔 이식] 메사의 목탄색 줄무늬를 `build_upper` 에서 **밖으로** 뽑아냈다.

        이 리팩터가 존재하는 이유 — 정리가 아니라 **데이텀 수리**다.  띠 상면은
        `top + proud − 0.003 + 0.01` = **+0.0085 m** 이고 `build_upper` 는 낙차
        분기 안에 있으므로, 정본의 낙차-OFF 팔은 띠를 잃고 그와 함께 카메라 지면
        데이텀 8.5 mm 를 잃는다.  그 이동은 출하된 코퍼스에서 측정된다:
        `260820_boost_e2_on` 컷 0000/0001 은 `cam.ground_z` 0.0085 를 갖는데
        짝인 off 팔은 0.0 을 갖는다.
        C 팔(`keep_dressing`)은 "낙차 제거, **드레싱 유지**" 로 정의되고 띠는
        **드레싱**이다 — 그러므로 평평해진 광장 위에 띠를 다시 짓는 것이
        의미상 옳은 팔이면서 동시에 C 팔의 카메라 데이텀을 A 팔과 동일하게
        만드는 조치다.  y 클램프가 x 만의 함수라서 다시 지은 띠는 A 팔의 것과
        좌표까지 동일하다.  (B1 팔은 정당하게 띠를 잃는다 — 그것이 개입이고,
        PREREG §5.1 이 그 결과인 `pose_tol` 층을 숨기지 않고 선언한다.)
        """
        bd = PARAMS["band"]
        x = bd["x0"]
        i = 0
        while x <= bd["x1"] + 1e-6:
            # [W2-D] Clamp the +y end to the mesa boundary (axis-aligned plaza union 30 deg wedge).
            y_hi = min(bd["y_half"], bd["mesa_slope"] * abs(x))
            y_lo = -bd["y_half"]
            if y_hi - y_lo > 0.30:      # Skip the band if no length remains
                BOX(f"{ROOT}/Band_{i}",
                    (x, (y_lo + y_hi) / 2.0, top + bd["proud"] - 0.003),
                    (bd["width"], y_hi - y_lo, 0.02), M["band"])
            x += bd["spacing"]
            i += 1

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P1 plaza_granite (spec §5.1 scene20 row)
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        st = PARAMS["stairs"]
        # [W3 L20 · G-4] the chambers are DERIVED from the declared branch, never from
        #   the frame. `derive_manholes` knows nothing about cameras by construction;
        #   the near-window check keeps a job, but only a **reject-only** one (G-4 build
        #   spec 1: it may reject a position, never produce one), and it is run below in
        #   `plaza_selfcheck` against this scene's own preset eyes.
        u = g["utility"]
        mh = ik.derive_manholes(u["line"], d_mm=u["d_mm"],
                                junctions=[tuple(j) for j in u["junctions"]])
        print("[gkit] 맨홀 유도 " + " · ".join(
            f"{m['tag']}({m['x']:+.2f},{m['y']:+.2f}) {m['reason']}" for m in mh))
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]),
            z=float(PARAMS["upper"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene20", tactile=(),
            sites=dict(manhole=[(m["x"], m["y"]) for m in mh],
                       gully=[tuple(v) for v in g["gullies"]]),
            seed=20)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # [W3 L20 · F1] `patch=M["upper"]` / `patch_cut=M["band"]` are **deleted** with
        #   the site list above. `M["upper"]` is the plaza's own material, so the binding
        #   authored a repair patch in the same stone as the field it repairs — the
        #   "lighter-than-base ghost rectangle" F1 indicts. The role emits nothing under
        #   GT-24 either way; keeping a dead binding to a banned vocabulary is how the
        #   next lane re-opts into it by accident.
        M2.update(joint=M["band"], crack=M["band"],
                  manhole=M["band"], gully=M["band"],
                  gutter=M["band"], gutter_cover=M["band"],
                  trench=M["band"], trench_frame=M["band"],
                  marking=M["band"], weed=M["grass"], wear=M["stain"],
                  stain_dirt=M["stain"], stain_water=M["stain"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene20 P1 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_flat_fill(M):
        """hazard_stairs=False control: unify upper+stair+lower into flat ground at z=0."""
        sc.skin_exclude(f"{ROOT}/FlatPlaza")     # [W2-0, P-A] The twin gets the same conditions
        u = PARAMS["upper"]
        v = PARAMS["valley"]
        x0, x1 = u["x0"], 20.0
        y0, y1 = -8.0, 8.0
        BOX(f"{ROOT}/FlatPlaza", ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
            (0.0 + v["z_top"]) / 2.0), (x1 - x0, y1 - y0, 0.0 - v["z_top"]),
            M["upper"], col=True)

    # -------------------------------------------------------------------
    # Stair + lower plaza (rot_group 30 deg - boundary stays aligned) + diagonal cue
    # -------------------------------------------------------------------
    def build_stair_walls(M, grp):
        """[GT-87] The masonry cheek wall on each side of the 30° flight.

        Authored in **rot_group local coordinates**, so the two walls follow the diagonal
        exactly as the flight does — a world-space wall beside a rotated flight is the
        defect this scene exists to avoid.

        Four solids per side, which is `scene14.build_parapets`' construction and its
        reasons, re-derived for this flight's numbers:
          `Body`   an axis-aligned box over the whole run, top **−1.250** (the wall top at
                   the toe, less 0.10). Its top face never shows: the haunch underside is
                   at −1.345 at the head and sinks from there, so the box is bitten into
                   the slab by ≥ **0.095 m** everywhere [computed].
          `Haunch` ONE oblique slab (`sc.build_slope`, `margin=0`) whose TOP face is the
                   nosing line + 0.950 from the drop edge to the last nosing. This is the
                   line the eye reads, and it is straight — a per-step wall would be the
                   stepped parapet the 08-05 answer already rejected in scene14.
          `Newel`  a level head block on the mesa, plan length `lap` = haunch_t·sin(ang) +
                   0.15 = **0.998 m**. `lap` is not a taste number: the perpendicular end
                   face of an oblique slab retreats uphill by haunch_t·sin(ang) = 0.848 m,
                   and without a block that long the wall would open a triangular cavity
                   under its own head — scene14's v6 "wedge slit" defect, in its exact form.
          `EndCap` the same block at the toe, giving the run a **vertical** end face at the
                   last nosing instead of the knife edge the slab's tilted end would leave.
        Plus a three-piece `band_dark` coping that oversails 30 mm per face, sinks 40 mm in
        (no coplanar skin) and projects `nose` = 20 mm past both end faces.

        Foundations: every solid runs down to −2.30, which is 0.15 m under the valley top
        (−2.15) — no member ends in air — and the slab's deepest vertex is −3.071 against
        the valley's own bottom at −3.150, so nothing pokes through the ground plane.

        Not touched: the flight, the wedge, the lower plaza, the 30° drop-edge line and
        every walked-surface z. The wall laps 0.06 m onto the flight so the two materials
        never share a plane; that lap is the only thing it takes from the walked width
        (5.00 → 4.88 m clear), and it takes it by standing there, not by moving a stair.
        """
        st = PARAMS["stairs"]
        sw = PARAMS["stair_wall"]
        run = st["tread"] * st["nsteps"]                 # 4.760
        drop = st["riser"] * st["nsteps"]                # 2.100
        ang = math.atan2(st["riser"], st["tread"])       # 23.815°
        x_h, x_t = st["x0"], st["x0"] + run              # 0.000 · 4.760
        z_h = st["z_top"] + sw["wall_h"]                 # +0.950 wall top at the drop edge
        z_t = st["z_top"] - drop + sw["wall_h"]          # −1.150 wall top at the last nosing
        base = sw["base_z"]                              # −2.300
        body_top = z_t - sw["body_drop"]                 # −1.250
        y_in = st["y1"] - sw["lap"]                      # 2.440 inner face (laps the flight)
        y_out = y_in + sw["width"]                       # 2.800 outer face
        yc, w = (y_in + y_out) / 2.0, sw["width"]
        c_in, c_out = y_in - sw["cap_proud"], y_out + sw["cap_proud"]
        cc, cw = (c_in + c_out) / 2.0, c_out - c_in      # 2.620 · 0.420
        lap = sw["haunch_t"] * math.sin(ang) + 0.15      # 0.998 — buries the slab end face
        cap_v = sw["cap_t"] + sw["cap_bite"]             # 0.100 vertical depth of the coping
        cap_perp = cap_v * math.cos(ang)                 # 0.091 perpendicular (build_slope)
        cap_lap = cap_perp * math.sin(ang) + 0.03        # 0.067 — same seal, coping scale
        n = 0
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            p = f"{grp}/StairWall_{tag}"
            BOX(f"{p}/Body", ((x_h + x_t) / 2.0, sgn * yc,
                              (body_top + base) / 2.0),
                (run, w, body_top - base), M["parapet"], col=True)
            sc.build_slope(stage, f"{p}/Haunch", x_h, z_h, run, drop,
                           sgn * y_in, sgn * y_out, sw["haunch_t"],
                           M["parapet"], margin=0.0, collider=True)
            BOX(f"{p}/Newel", (x_h - lap / 2.0, sgn * yc, (z_h + base) / 2.0),
                (lap, w, z_h - base), M["parapet"], col=True)
            BOX(f"{p}/EndCap", (x_t - lap / 2.0, sgn * yc, (z_t + base) / 2.0),
                (lap, w, z_t - base), M["parapet"], col=True)
            # Coping — dressing on top of a wall that already collides (col default False).
            BOX(f"{p}/Cap_Head",
                (x_h - (lap + sw["nose"]) / 2.0, sgn * cc,
                 z_h + sw["cap_t"] - cap_v / 2.0),
                (lap + sw["nose"], cw, cap_v), M["band"])
            sc.build_slope(stage, f"{p}/Cap_Rake", x_h, z_h + sw["cap_t"],
                           run, drop, sgn * c_in, sgn * c_out, cap_perp,
                           M["band"], margin=0.0, collider=False)
            BOX(f"{p}/Cap_Toe",
                (x_t + (sw["nose"] - cap_lap) / 2.0, sgn * cc,
                 z_t + sw["cap_t"] - cap_v / 2.0),
                (cap_lap + sw["nose"], cw, cap_v), M["band"])
            n += 7
        print(f"[GT-87] 계단 측벽 2면 · 프림 {n} · 벽마루 = 노징선 위 "
              f"{sw['wall_h']:.3f} + 갓돌 {sw['cap_t']:.3f} → 가드선 "
              f"{sw['wall_h'] + sw['cap_t']:.3f} m · 내면 |y| {y_in:.3f} "
              f"(계단 겹침 {sw['lap']:.3f} · 유효폭 {2 * y_in:.2f} m) · 외면 "
              f"{y_out:.3f} · 발치 z {base:.2f} (잔디 "
              f"{PARAMS['valley']['z_top']:.2f} 아래 "
              f"{PARAMS['valley']['z_top'] - base:.2f}) · 상·하단 마감 "
              f"{lap:.3f} m · 난간 튜브 0")
        return n

    def build_diagonal(M):
        # Stair tone unified with the upper plaza_light family (the contrast with the warm lower level is lower's job).
        stair_mtl = M["upper"]
        r = PARAMS["rot"]
        grp = sc.build_rot_group(stage, f"{ROOT}/Diag", r["pivot"], r["deg"])
        # [audit v4 S1] Diagonal extension wedge of the upper plaza - being inside the rotation group,
        # its east face becomes a 30 deg diagonal edge exactly coincident with the stair top edge (local x=0).
        # It overlaps the axis-aligned plaza (x <= -4.5) to form one continuous top face (z=0), so
        #   * A1, the south wedge trench (horizontal gap up to 1.25 m, drop 2.15 m), disappears,
        #   * A2, the north top-step burial (first step up to 0.75 m), disappears -> first step 0.15 m across the full width,
        #   * B1 the tactile strip (local x -0.3..0) and B2 the south railing start (local x -0.4) sit on the ground,
        #   * the drop boundary becomes the whole 30 deg line instead of a single point at the origin, so the scene's character is reinforced.
        # In the overlap both boxes have top 0 / bottom -2.2 with identical material and world-projected
        # texture, so any Z-fighting makes no visible difference on screen.
        wg = PARAMS["wedge"]
        BOX(f"{grp}/UpperWedge",
            ((wg["x0"] + wg["x1"]) / 2.0, 0.0,
             (wg["z_top"] + wg["base_z"]) / 2.0),
            (wg["x1"] - wg["x0"], 2.0 * wg["y_half"],
             wg["z_top"] - wg["base_z"]), M["upper"], col=True)
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{grp}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        # Lower plaza (warm) - a thin slab proud of the grass. Same 30 deg group -> boundary stays aligned.
        lo = PARAMS["lower"]
        lower_mtl = M["lower"] if cfg["cue_material_break"] else M["upper"]
        BOX(f"{grp}/LowerPlaza",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"], lo["thick"]),
            lower_mtl, col=True)

        # Diagonal cue (inside rot_group - rotates along the drop diagonal)
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{grp}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
        if cfg["cue_railing"]:
            build_stair_walls(M, grp)

        # Lower plaza props (rotation-group local - aligned along the diagonal corridor)
        if cfg["cue_scene_dressing"]:
            lz = lo["z_top"]
            # [v5.1 §2] One row of regulation bollards + dot tactile at the corridor entrance (rot local coordinates)
            lb = PARAMS["lower_bollards"]
            for i, ly in enumerate(lb["ys"]):
                build_bollard_std(M, f"{grp}/LowBollard_{i}", lb["x"], ly, lz,
                                  k=i)
            if cfg["cue_tactile"]:
                bk = lb["block"]
                sc.build_tactile(stage, f"{grp}/Tactile_LowBollard",
                                 bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                                 M["tactile"], z=lz,
                                 proud=PARAMS["tactile"]["proud"])
            for i, (lx, ly, yaw) in enumerate(PARAMS["lower_benches"]):
                sc.build_bench(stage, f"{grp}/LowBench_{i}", lx, ly, lz,
                               M["wood"], yaw=yaw)

    # -------------------------------------------------------------------
    # Dressing - 3 axis-aligned buildings + axis-aligned props (bollard rows, planters, benches,
    #          street lamps, hedges) + mesa entry ramp
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[W3 L20 · K4(c) C6] one regulation bollard, now from the props_kit template.

        What this replaced: a bare `sc.build_bollard` cylinder (r 0.075 · h 0.90) plus a
        hand-authored band ring — two prims, a flat top and no base detail, i.e. a pipe
        offcut standing on a slab. `props_kit.build_bollard_v2` is the C6 template the
        intake row names, and it carries the four features that make the read
        `[practice - §C6]`: **dome cap** (a flat-topped bollard is an offcut), **base
        plate + anchor cover ring** (a bollard is bolted down, it does not grow out of
        the paving), the **reflective band at knee height**, and a body that is not a
        mirror. Statutory envelope is unchanged and still satisfied — 도로교통 약자
        편의증진법 시행규칙 별표2: h 0.80-1.00 (template default **0.85**, the old value
        was 0.90), Ø 0.10-0.20 (**0.11**, was 0.15), pitch ~1.5 m (this scene's rows are
        at 1.5 m with a 1.5 m centre gap, unchanged).

        **GT consequence, declared before it landed**: the body is a collider, so the
        collision box moves — r 0.075 -> 0.055 and h 0.90 -> 0.85 on 8 instances (4 on the
        mesa entry ramp, 4 in the lower-plaza corridor). No walked surface and no drop edge
        is touched. That is GT class A and it is why this scene's row exists.

        `compliant=True` on every instance: this is a civic plaza built to spec, not the
        measured field population (the template's `compliant=False` arm reproduces the
        three real failure modes and is deliberately not used here — a deterministic
        choice about the site, stated rather than drawn).
        """
        pk.build_bollard_v2(stage, prefix, cx, cy, bz,
                            M[f"bollard_{k % 3}"], band_mtl=M["bollard_band"],
                            radius=0.055, height=0.85, band_z=0.62,
                            band_h=0.06, compliant=True, seed=k)

    def build_backdrop(M):
        """[W3 L20 · BS-4] the axis-aligned horizon, opened.

        Returns `(n_prims, over)` where `over` lists any block whose ridge breaks the
        frame ceiling — empty is the acceptance condition, and `plaza_selfcheck` asserts
        it rather than trusting this print.
        """
        bp = PARAMS["backdrop"]
        eyes = bk.judged_eyes(0.0)          # spec §D: the preset axis is +X at gy = 0
        kit = fk.Kit(sc.add_box, sc.add_cylinder,
                     getattr(sc, "_oriented_box", None))
        n_tot = 0
        over = []
        # ---- PLACEBO GROUP (AMBER -- exploratory only, PREREG §3.3) ---------
        #   The E blocks are the ONLY removable in-frame mass in scene20's 6
        #   strict-H frames: every piece of mesa furniture measures 0 px in 6/6
        #   (PLACEBO_PIXEL_MASS_crest.csv), being either behind the camera
        #   (bollards, x -13.6) or outside the 62 deg forward FOV.  The E blocks
        #   are 240 k px = 11.6 % of frame -- but they stand on the VALLEY floor
        #   with their feet cut by the mesa lip, which is the same FORM the
        #   matrix reads as geometry_silhouette.  The only defence is that the
        #   canonical matrix §2.4 s20 judged the `cue_railing=False` arm's h0.3
        #   frames "effectively drop-evidence-free" WITH the backdrop present.
        #   That is thin, so this arm is rendered and tabled but EXCLUDED from
        #   the placebo-corrected primary rule.
        _blocks = [b for b in bp["blocks"]
                   if not (PLACEBO_REMOVE and b[0].startswith("E"))]
        for tag, x0, x1, y0, y1, hh in _blocks:
            # A silhouette is a plan rectangle seen edge-on; `axis`/`facade_*` only pick
            # which face the planner measures from, and that face is the one turned
            # toward the plaza centre.
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
            # `parapet=` gets the SHELL material, not `M["parapet"]` (0.72 grey). At
            # 44-62 m a light capping band on a dark mass reads as a lit highlight along
            # the roofline — a silhouette has no cap by definition (S01's pilot defect 3).
            prims = bk.build_korean_building(
                kit, stage, f"{ROOT}/Backdrop_{tag}", bd,
                bk.Mtls(M[bp["mat"]], parapet=M[bp["mat"]]), plan=p)
            n_tot += len(prims)
            # `hh` is the SHELL top. `roof_allow` is the parapet band + penthouse that
            # `build_korean_building` emits ABOVE the shell-top invariant, and backdrop
            # policy (2) does not gate it (S01-F1). Compute it from the plan — never copy
            # a constant — and compare the RIDGE.
            allow = bk.roof_allow(p)
            ridge = bp["base_z"] + hh + allow
            sky = (p.z_ceil is None) or (ridge < p.z_ceil)
            if not sky:
                over.append((tag, round(ridge, 2), round(p.z_ceil, 2)))
            print(f"[backdrop] {tag} W {p.W:5.1f} · shell h {hh:5.2f} · allow "
                  f"{allow:4.2f} · ridge {ridge:5.2f} · {p.kind}/{p.tier} · d_true "
                  f"{p.d_true:6.2f} m · in_frame {str(p.in_frame):5s} · z_ceil "
                  f"{('%.2f' % p.z_ceil) if p.z_ceil is not None else '  n/a'} · "
                  f"하늘 {str(sky):5s} · 프림 {len(prims)}")
        n_b = len(_blocks)
        print(f"[backdrop] {n_b}동 {n_tot} 프림 · 창 0 · 지붕선 위 하늘 "
              f"{n_b - len(over)}/{n_b}" + (f" · 초과 {over}" if over else ""))
        return n_tot, over

    def build_belt(M):
        """[W3 L20 · K4(b)] the mid-ground elm belt on the valley grass."""
        b = PARAMS["belt"]
        mts = (M["wood"], M["canopy_a"], M["canopy_b"])
        n = 0
        for tag, fixed, a0, a1, axis in b["rows"]:
            k = 0
            v = a0
            while v <= a1 + 1e-6:
                cx, cy = (fixed, v) if axis == "y" else (v, fixed)
                sc.build_tree(stage, f"{ROOT}/Belt_{tag}_{k}", cx, cy, b["z"],
                              *mts, trunk_h=b["trunk_h"], species="elm")
                n += 1
                k += 1
                v += b["pitch"]
        print(f"[belt] 중경 수목 {n}주 · elm · 피치 {b['pitch']:.1f} m · "
              f"열간 8.6 m · z {b['z']:.2f}")
        return n

    def build_litter(M):
        """[W3 L20 · season] leaf litter — [GT-126] trace density (see PARAMS note).

        The carpet-level cover contradicted the summer-green canopy tuples in the same
        frame; what remains is the few stray dry leaves that read in any season. The
        caps below are cut with the cover values so a future cover bump cannot silently
        restore the carpet through the cap alone.

        The tread scatter is authored **inside the 30 deg rot_group**, in group-local
        coordinates, so it rotates with the flight; `stair_z` is the local ground
        callback so each leaf sits on the tread it lands on instead of floating over a
        0.15 m riser. The plaza scatter is world-space and is clipped to the
        axis-aligned part of the mesa (x <= -4.5), because the wedge east of that line is
        where the drop boundary runs and a leaf field there would sit over the cliff.
        """
        li = PARAMS["litter"]
        st = PARAMS["stairs"]
        lo = PARAMS["lower"]
        # The rot_group Xform is authored by `build_diagonal`; re-calling
        # `sc.build_rot_group` here would append a second set of xformOps to the same
        # prim, so the path is referenced, not rebuilt. `build_litter` is therefore
        # ordered strictly after `build_diagonal` in the assembly block below.
        grp = f"{ROOT}/Diag"
        tread, riser, ns = st["tread"], st["riser"], st["nsteps"]

        def stair_z(x, y):
            if x <= st["x0"]:
                return 0.0
            i = min(int((x - st["x0"]) / tread), ns - 1)
            return -riser * (i + 1)

        # [GT-87] The two rot_group scatters are inset from the flight edge by the width
        #   the side wall now occupies. The wall laps `lap` onto the flight and its coping
        #   oversails a further `cap_proud`, so a leaf authored on the old ±2.500 edge
        #   would be seated INSIDE the wall solid — a leaf half-buried in masonry is the
        #   interpenetration this round is about. Inset = lap + cap_proud + 0.05 clearance
        #   = 0.140 m [computed]; with `cue_railing` off the full width is used, so the
        #   ablation arm keeps its own scatter.
        inset = (PARAMS["stair_wall"]["lap"] + PARAMS["stair_wall"]["cap_proud"]
                 + 0.05) if cfg["cue_railing"] else 0.0
        n = 0
        n += sc.scatter_debris(
            stage, f"{grp}/Litter_Tread",
            st["x0"], st["y0"] + inset, st["x0"] + tread * ns, st["y1"] - inset,
            0.0,
            cover=li["treads"]["cover"], edge_bias=li["treads"]["edge_bias"],
            seed=li["treads"]["seed"], ground_fn=stair_z, max_count=14)
        n += sc.scatter_debris(
            stage, f"{grp}/Litter_Foot",
            lo["x0"], lo["y0"] + inset, lo["x0"] + 5.0, lo["y1"] - inset,
            lo["z_top"],
            cover=li["foot"]["cover"], edge_bias=li["foot"]["edge_bias"],
            seed=li["foot"]["seed"], max_count=10)
        n += sc.scatter_debris(
            stage, f"{ROOT}/Litter_Plaza",
            PARAMS["upper"]["x0"] + 0.5, -7.6, PARAMS["upper"]["x1"], 7.6, 0.0,
            cover=li["plaza"]["cover"], edge_bias=li["plaza"]["edge_bias"],
            seed=li["plaza"]["seed"], max_count=8)
        print(f"[litter] 낙엽 {n}개 (미량 산잎 · GT-126)")
        return n

    def build_dressing(M):
        _n_bd, _over = build_backdrop(M)
        build_belt(M)
        # [v5.1 §2] One row of regulation bollards + dot tactile at the top of the mesa entry ramp
        bl = PARAMS["bollards"]
        for i, by in enumerate(bl["ys"]):
            build_bollard_std(M, f"{ROOT}/Bollard_{i}", bl["x"], by, 0.0, k=i)
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=0.0,
                             proud=PARAMS["tactile"]["proud"])
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (px, py) in enumerate(PARAMS["planters"]):
            sc.build_planter(stage, f"{ROOT}/Planter_{i}", px, py, 0.0,
                             M["curb"], M["grass"], tree_mtls=tree_mtls,
                             size=PARAMS["planter"]["size"],
                             species=PARAMS["planter_species"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["pole"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly, sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        # [GT-63] clipped hedge bands: box+crown blobs -> fused rows of real
        #   shrub USDs (place_hedge_row; rects/heights/prim roots unchanged;
        #   legacy build_hedge fallback inside).
        n_hedge = 0
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            n_hedge += sc.place_hedge_row(
                stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                0.9, gk.det_seed("scene20.hedge", i), base_z=0.0)
        print(f"[GT-63] 생울타리 실관목 {n_hedge}주 "
              f"(place_hedge_row · 폴백 {'무' if n_hedge else 'build_hedge'})")
        # Mesa entry ramp (west side, grass -2.15 -> plaza 0). Negative drop = rising towards +X.
        # margin=0, so the top edge is exactly flush with the plaza west face (x=-14, z=0).
        ar = PARAMS["access_ramp"]
        vz = PARAMS["valley"]["z_top"]
        sc.build_slope(stage, f"{ROOT}/AccessRamp", ar["x0"], vz,
                       ar["x1"] - ar["x0"], vz - PARAMS["upper"]["z_top"],
                       ar["y0"], ar["y1"], ar["thick"], M["upper"],
                       margin=0.0, collider=True)
        return _over

    # [v5.2 user] Arbitrary warning placards removed - build_signs() deleted.

    # -------------------------------------------------------------------
    # [W3 L20] plaza_selfcheck - the R-1 registry print + this lane's four gates
    # -------------------------------------------------------------------
    def plaza_selfcheck(backdrop_over):
        """Boot-free, GPU-free assertions over the PARAMS this scene was built from.

        The four things this lane changed are the four things it gates, because
        "the geometry looks right in the file" is not evidence:
          (1) **hazard / collision registry (R-1)** — the drop edge, the walked surfaces
              and every collision box this scene declares, printed so a re-cache can be
              read against it. The GT row for this lane is class **A**: the ONLY entries
              that move are the 8 bollard bodies (C6 template) and the 3 planter kerb
              runs (re-site); no walked surface and no drop edge is touched, and the
              print is what proves it.
          (2) **judged eye -> planter bed >= 2.50 m** over all 13 cuts x all beds
              (`w3_md_reverts_v1.md` §5's census gate).
          (3) **prop footprint overlaps = 0** over the mesa furniture.
          (4) **G-4 reject-only occupancy** — every derived chamber is behind the eye or
              outside the +-30 deg judged frame. This may only *reject*; it never
              produces a position.
          (5) **[GT-87] the stair side walls** — the four numbers a cheek wall can get
              wrong (the body biting into the haunch, the end faces sealed, the foot under
              grade, the deepest vertex inside the ground plane) plus the guard height
              band, and the **OCCL declaration**: what the new opaque guard hides, from
              which judged eye, in world coordinates.
        Plus the season audit and the backdrop sky result, both fail-loud.
        """
        import math as _m
        ok = True
        views = build_views()
        eyes = [(k, float(v["eye"][0]), float(v["eye"][1]))
                for k, v in views.items()]

        # (1) hazard / collision registry ---------------------------------
        st, up, lo = PARAMS["stairs"], PARAMS["upper"], PARAMS["lower"]
        drop = st["riser"] * st["nsteps"]
        print("[registry] 낙차 경계 = 30° 사선 x = -0.5774·y (rot local x=0) · "
              f"낙차 {drop:.2f} m · 단 {st['nsteps']}개 "
              f"(riser {st['riser']:.3f} · tread {st['tread']:.3f})")
        print(f"[registry] 보행면: UpperPlaza z={up['z_top']:.2f} · UpperWedge "
              f"z={up['z_top']:.2f} · Stairs z_top={st['z_top']:.2f} · LowerPlaza "
              f"z={lo['z_top']:.2f} · Valley z={PARAMS['valley']['z_top']:.2f} "
              "— 이번 레인에서 전부 불변")
        n_boll = len(PARAMS["bollards"]["ys"]) + len(PARAMS["lower_bollards"]["ys"])
        n_wall = 8 if cfg["cue_railing"] else 0
        print(f"[registry] 충돌상자 변경: 볼라드 몸통 {n_boll}개 "
              "(r 0.075→0.055 · h 0.90→0.85, C6) · 화단 연석 "
              f"{len(PARAMS['planters']) * 4}개 (재배치) · [GT-87] 측벽 신규 "
              f"{n_wall}개 (계단 밖 |y| 2.44~2.80, 난간 튜브 제거) · 그 외 0")

        # (5) [GT-87] stair side walls — construction gates + OCCL ---------
        sw = PARAMS["stair_wall"]
        ang = _m.atan2(st["riser"], st["tread"])
        run_s = st["tread"] * st["nsteps"]
        z_h = st["z_top"] + sw["wall_h"]                     # +0.950
        z_t = st["z_top"] - drop + sw["wall_h"]              # −1.150
        vert = sw["haunch_t"] / _m.cos(ang)                  # haunch vertical depth
        retreat = sw["haunch_t"] * _m.sin(ang)               # end-face uphill retreat
        lap_w = retreat + 0.15                               # newel / end-cap plan length
        bite = (z_t - sw["body_drop"]) - (z_h - vert)        # body top over haunch soffit
        deep = z_t - sw["haunch_t"] * _m.cos(ang)            # lowest vertex of the haunch
        v_top = PARAMS["valley"]["z_top"]
        v_bot = v_top - PARAMS["valley"]["thick"]
        guard = sw["wall_h"] + sw["cap_t"]
        y_in_w = st["y1"] - sw["lap"]
        wall_ok = (bite > 0.0                       # the body never shows through the face
                   and lap_w > retreat              # both end faces buried, no wedge slit
                   and sw["base_z"] <= v_top - 0.05  # every solid founded under grade
                   and deep >= v_bot                # nothing pokes out of the ground plane
                   and sw["lap"] > 0.0              # no plane shared with the flight
                   and 0.85 - 1e-9 <= sw["wall_h"] <= 0.95 + 1e-9
                   and guard <= 1.10 + 1e-9)
        if cfg["cue_railing"] and not wall_ok:
            ok = False
        print(f"[selfcheck · GT-87] 측벽 bite {bite:+.3f} m · 마감 {lap_w:.3f} > "
              f"후퇴 {retreat:.3f} · 발치 {sw['base_z']:.2f} ≤ {v_top - 0.05:.2f} · "
              f"최저점 {deep:.3f} ≥ 지반 바닥 {v_bot:.2f} · 계단 겹침 "
              f"{sw['lap']:.3f} (유효폭 {2 * y_in_w:.2f} m) · 가드선 {guard:.3f} m "
              f"≤ 1.100 · {'OK' if wall_ok else '위반'}")
        # OCCL. The guard is opaque, so it is declared, not assumed harmless. The wall band
        #   is rot_group local x −0.998…4.760 · |y| 2.410…2.830; the eye is taken INTO that
        #   local frame (inverse 30° rotation) so the clearance is exact rather than a
        #   corner approximation. The drop-edge line itself (world x = −0.5774·y) does not
        #   move and stays unguarded outside the flight width — that is what keeps the T8
        #   identity intact while the flight itself becomes walkable.
        th = _m.radians(PARAMS["rot"]["deg"])
        cs, sn = _m.cos(th), _m.sin(th)
        wx0, wx1 = st["x0"] - lap_w, st["x0"] + run_s
        cor = [(lx * cs - ly * sn, lx * sn + ly * cs)
               for lx in (wx0, wx1)
               for ly in (-2.83, -2.41, 2.41, 2.83)]
        near = None
        for k, ex, ey in eyes:
            lx = ex * cs + ey * sn
            ly = -ex * sn + ey * cs
            dx = max(wx0 - lx, 0.0, lx - wx1)
            dy = max(2.41 - abs(ly), abs(ly) - 2.83, 0.0)
            d = _m.hypot(dx, dy)
            if near is None or d < near[0]:
                near = (d, k)
        print(f"[OCCL · GT-87] 신규 차폐체 = 계단 양측 측벽 2면 · 월드 AABB "
              f"x[{min(c[0] for c in cor):+.2f} {max(c[0] for c in cor):+.2f}] "
              f"y[{min(c[1] for c in cor):+.2f} {max(c[1] for c in cor):+.2f}] · "
              f"마루 z {z_h + sw['cap_t']:+.3f}→{z_t + sw['cap_t']:+.3f} · "
              f"최근접 판정시점 {near[1]} {near[0]:.2f} m · 낙차 경계선·보행면 불변")

        # (2) + (3) footprint arithmetic ----------------------------------
        def _rect(cx, cy, sx, sy, yaw=0.0):
            if abs(abs(yaw) - 90.0) < 1e-6:
                sx, sy = sy, sx
            return (cx - sx / 2.0, cy - sy / 2.0, cx + sx / 2.0, cy + sy / 2.0)

        S = PARAMS["planter"]["size"] + 2 * 0.05      # kerb + cap overhang
        items = [(f"Planter_{i}", _rect(px, py, S, S))
                 for i, (px, py) in enumerate(PARAMS["planters"])]
        items += [(f"Bench_{i}", _rect(bx, by, 1.8, 0.4, yaw))
                  for i, (bx, by, yaw) in enumerate(PARAMS["benches"])]
        items += [(f"Streetlight_{i}",
                   _rect(lx, ly, 2 * PARAMS["streetlight"]["pole_r"],
                         2 * PARAMS["streetlight"]["pole_r"]))
                  for i, (lx, ly) in enumerate(PARAMS["streetlights"])]
        items += [(f"Hedge_{i}", (min(a, c), min(b, d), max(a, c), max(b, d)))
                  for i, (a, b, c, d) in enumerate(PARAMS["hedges"])]
        bl = PARAMS["bollards"]
        items += [(f"Bollard_{i}", _rect(bl["x"], by, 0.16, 0.16))
                  for i, by in enumerate(bl["ys"])]
        ar = PARAMS["access_ramp"]
        items.append(("AccessRamp", (ar["x0"], ar["y0"], ar["x1"], ar["y1"])))

        coll = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i][1], items[j][1]
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 0 and oy > 0:
                    coll.append((items[i][0], items[j][0], ox, oy))
        if coll:
            ok = False
            for n1, n2, ox, oy in coll:
                print(f"[selfcheck] ✘ 간섭 {n1} x {n2} {ox:.3f} x {oy:.3f} m")
        print(f"[selfcheck] 지물 간섭 {len(coll)}건 (기준 0)")

        worst = None
        for nm, r in items:
            if not nm.startswith("Planter"):
                continue
            for k, ex, ey in eyes:
                d = _m.hypot(max(r[0] - ex, 0.0, ex - r[2]),
                             max(r[1] - ey, 0.0, ey - r[3]))
                if worst is None or d < worst[0]:
                    worst = (d, nm, k)
        if worst[0] < 2.50:
            ok = False
        print(f"[selfcheck] 판정시점↔화단 최단 {worst[0]:.3f} m "
              f"({worst[1]} x {worst[2]}) · 기준 ≥ 2.50 · "
              f"{'OK' if worst[0] >= 2.50 else '위반'}")

        # (4) G-4 reject-only occupancy -----------------------------------
        u = PARAMS["gkit"]["utility"]
        mh = ik.derive_manholes(u["line"], d_mm=u["d_mm"],
                                junctions=[tuple(j) for j in u["junctions"]])
        grid = [(k, ex, ey) for k, ex, ey in eyes if k.startswith("preset_")]
        for m in mh:
            worst_b = 0.0
            behind = True
            for k, ex, ey in grid:
                dx = m["x"] - ex
                if dx <= 0.0:
                    continue                      # behind this eye (+X walk axis)
                behind = False
                worst_b = max(worst_b, abs(_m.degrees(_m.atan2(m["y"] - ey, dx))))
            inside = (not behind) and worst_b <= 30.0
            if inside:
                ok = False
            print(f"[selfcheck] 맨홀 {m['tag']}({m['x']:+.2f},{m['y']:+.2f}) "
                  + ("모든 그리드 시점 후방" if behind
                     else f"최대 방위 {worst_b:.1f}° (프레임 ±30°)")
                  + f" · {'위반' if inside else 'OK'}")

        # season audit + backdrop -----------------------------------------
        row = sc.SCENE_SPECIES.get("Scene20", (None, None))
        print(f"[season] {SEASON} · G1 in-leaf → bare=False · 수종 route "
              f"{row[0]} · belt {row[1]} · 화단 {PARAMS['planter_species']} "
              "· 봄개화 자산 0")
        if backdrop_over:
            ok = False
            print(f"[selfcheck] ✘ 지붕선이 프레임 천장을 넘음: {backdrop_over}")

        # ground-plane containment — the defect the first pilot render exposed --------
        #   The sky arithmetic can be perfect while the mass stands off the edge of the
        #   world. `Valley` is the only ground this scene has; every backdrop block and
        #   every belt tree must be inside it, with margin, or the plane's own horizon
        #   seam runs behind them. Nothing in the kit checks this — it is a scene-side
        #   fact about a scene-side ground box, so it is gated here.
        v = PARAMS["valley"]
        H = v["size"] / 2.0
        gx0, gx1, gy0, gy1 = 6.0 - H, 6.0 + H, -H, H
        MRG = 2.0
        off = []
        for tag, x0, x1, y0, y1, _h in PARAMS["backdrop"]["blocks"]:
            if (x0 < gx0 + MRG or x1 > gx1 - MRG
                    or y0 < gy0 + MRG or y1 > gy1 - MRG):
                off.append(tag)
        b = PARAMS["belt"]
        n_belt = 0
        for tag, fixed, a0, a1, axis in b["rows"]:
            t = a0
            while t <= a1 + 1e-6:
                cx, cy = (fixed, t) if axis == "y" else (t, fixed)
                n_belt += 1
                if not (gx0 + MRG <= cx <= gx1 - MRG
                        and gy0 + MRG <= cy <= gy1 - MRG):
                    off.append(f"Belt_{tag}@{cx:.1f},{cy:.1f}")
                t += b["pitch"]
        if off:
            ok = False
        print(f"[selfcheck] 지면 포함 — Valley x[{gx0:+.1f} {gx1:+.1f}] "
              f"y[{gy0:+.1f} {gy1:+.1f}] · 배경 {len(PARAMS['backdrop']['blocks'])}동 "
              f"+ 벨트 {n_belt}주 · 이탈 {len(off)}건"
              + (f" {off}" if off else " · OK"))
        print(f"[selfcheck] scene20 {'통과' if ok else '실패'}")
        return ok

    # -- Scene assembly --
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_upper(M)
        build_diagonal(M)
    elif KEEP_DRESSING:
        # [C팔] 낙차만 제거.  `build_flat_fill` 은 여기서 안전하다 — scene12 와
        #   달리 이 씬의 `FlatPlaza` 는 이미 `skin_exclude` 돼 있고 상면이
        #   딱딱한 0.000 이다 — 그러나 메사에 타고 있던 **드레싱**이 함께
        #   돌아와야 한다.  아니면 C 팔은 A 팔 대비 카메라 데이텀 8.5 mm 를
        #   조용히 잃는다.  `build_bands` 주석 참조.
        build_flat_fill(M)
        if cfg["cue_scene_dressing"]:
            build_bands(M, PARAMS["upper"]["z_top"])
    else:
        build_flat_fill(M)
    _bd_over = []
    if cfg["cue_scene_dressing"]:
        _bd_over = build_dressing(M)
    build_ground_kit(M)             # [W2-D] Ground elements - after dressing (scatter-order convention)
    if cfg["hazard_stairs"] and cfg["cue_scene_dressing"]:
        build_litter(M)             # season dressing - strictly after build_diagonal (rot_group)
    if PLACEBO_REMOVE:
        print("[placebo_remove] scene20 — removed backdrop blocks E1·E2 "
              "(AMBER: exploratory only, PREREG §3.3). KEPT: cheek walls, "
              "bands, belt, bollards, planters, benches, streetlights, hedges.")
    if not plaza_selfcheck(_bd_over):
        raise SystemExit("scene20 self-check 실패")
    # [v5.2 user] Arbitrary warning placards removed - cue_sign placement deleted.

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene20 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["oblique_overview"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene20_{ts}.png")
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
